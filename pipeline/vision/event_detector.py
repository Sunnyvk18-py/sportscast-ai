"""GPT-4o Vision / LLaVA event detection."""

import json
import logging
import re
import time
from uuid import uuid4

from pipeline.kafka.schemas import VisionEvent

logger = logging.getLogger(__name__)

VISION_PROMPT = (
    "You are analyzing a sports broadcast frame. Identify if any of "
    "these events are occurring: goal, foul, corner kick, yellow card, "
    "red card, substitution, or none. Respond in JSON only: "
    '{"event_type": string, "confidence": float 0-1, "reasoning": string}'
)

EVENT_TYPE_MAP = {
    "goal": "goal",
    "foul": "foul",
    "corner kick": "corner",
    "corner": "corner",
    "yellow card": "yellow_card",
    "red card": "red_card",
    "substitution": "substitution",
    "none": None,
}


class VisionEventDetector:
    def __init__(self, model: str = "gpt-4o", api_key: str = ""):
        self.model = model
        self.api_key = api_key

    async def detect_event(
        self, frame_path: str, segment_id: str, timestamp_ms: int
    ) -> VisionEvent:
        start = time.perf_counter()
        try:
            from pipeline.vision.frame_extractor import FrameExtractor

            extractor = FrameExtractor()
            b64 = extractor.frame_to_base64(frame_path)

            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": VISION_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )
            raw = response.choices[0].message.content or ""
            parsed = self._parse_response(raw)
            event_type = EVENT_TYPE_MAP.get(parsed.get("event_type", "none").lower())
            if event_type is None and parsed.get("event_type", "").lower() != "none":
                event_type = parsed.get("event_type")
            processing_ms = int((time.perf_counter() - start) * 1000)
            return VisionEvent(
                event_id=str(uuid4()),
                timestamp_ms=timestamp_ms,
                segment_id=segment_id,
                frame_path=frame_path,
                detected_event_type=event_type,
                confidence=float(parsed.get("confidence", 0.0)),
                raw_response=raw,
                model_used=self.model,
                processing_ms=processing_ms,
            )
        except Exception as exc:
            logger.warning("Vision detection failed: %s", exc)
            return VisionEvent(
                timestamp_ms=timestamp_ms,
                segment_id=segment_id,
                frame_path=frame_path,
                detected_event_type=None,
                confidence=0.0,
                raw_response=str(exc),
                model_used=self.model,
                processing_ms=int((time.perf_counter() - start) * 1000),
            )

    def _parse_response(self, raw: str) -> dict:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{[^}]+\}", raw)
            if match:
                return json.loads(match.group())
            return {"event_type": "none", "confidence": 0.0, "reasoning": raw}


class LLaVAEventDetector:
    """HuggingFace LLaVA fallback — same interface as VisionEventDetector."""

    def __init__(self):
        self.model = "llava-hf/llava-1.5-7b-hf"
        self._pipe = None
        try:
            from transformers import pipeline

            self._pipe = pipeline("image-to-text", model=self.model)
        except Exception as exc:
            logger.warning("LLaVA model load failed, will use mock: %s", exc)

    async def detect_event(
        self, frame_path: str, segment_id: str, timestamp_ms: int
    ) -> VisionEvent:
        if self._pipe is None:
            from pipeline.vision.mock_detector import MockVisionDetector

            return await MockVisionDetector().detect_event(frame_path, segment_id, timestamp_ms)

        start = time.perf_counter()
        try:
            result = self._pipe(frame_path)
            text = result[0]["generated_text"] if result else ""
            parsed = VisionEventDetector("", "")._parse_response(text)
            event_type = EVENT_TYPE_MAP.get(parsed.get("event_type", "none").lower())
            return VisionEvent(
                timestamp_ms=timestamp_ms,
                segment_id=segment_id,
                frame_path=frame_path,
                detected_event_type=event_type,
                confidence=float(parsed.get("confidence", 0.5)),
                raw_response=text,
                model_used=self.model,
                processing_ms=int((time.perf_counter() - start) * 1000),
            )
        except Exception as exc:
            logger.warning("LLaVA detection failed: %s", exc)
            return VisionEvent(
                timestamp_ms=timestamp_ms,
                segment_id=segment_id,
                frame_path=frame_path,
                detected_event_type=None,
                confidence=0.0,
                model_used=self.model,
                processing_ms=int((time.perf_counter() - start) * 1000),
            )
