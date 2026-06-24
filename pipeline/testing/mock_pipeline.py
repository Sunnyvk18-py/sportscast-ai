"""Full mock pipeline — zero API keys, no network, no files."""

import asyncio
import logging
import random
from collections.abc import AsyncGenerator

from pipeline.agent.commentary_agent import CommentaryAgent
from pipeline.audio.classifier import CrowdNoiseClassifier
from pipeline.fusion.signal_fuser import SignalFuser
from pipeline.kafka.schemas import FusedEvent
from pipeline.speech.mock_transcriber import MockWhisperTranscriber
from pipeline.vision.mock_detector import MockVisionDetector

logger = logging.getLogger(__name__)


class MockPipeline:
    def __init__(
        self,
        duration_seconds: int = 60,
        events_to_simulate: list[dict] | None = None,
        commentary_enabled: bool = True,
    ):
        self.duration_seconds = duration_seconds
        self.events_to_simulate = events_to_simulate or []
        self.commentary_enabled = commentary_enabled
        self.vision = MockVisionDetector()
        self.speech = MockWhisperTranscriber()
        self.audio = CrowdNoiseClassifier()
        self.fuser = SignalFuser()
        self.commentary_agent = CommentaryAgent()
        self._match_history: list[str] = []

    async def run(self) -> AsyncGenerator[FusedEvent, None]:
        start_time = asyncio.get_event_loop().time()
        scheduled = sorted(self.events_to_simulate, key=lambda e: e["timestamp_ms"])

        # Add noise events for review queue demonstration
        noise_events = [
            {"timestamp_ms": 17000, "type": "none"},
            {"timestamp_ms": 48000, "type": "none"},
        ]

        all_events = scheduled + noise_events
        all_events.sort(key=lambda e: e["timestamp_ms"])

        for spec in all_events:
            target_ms = spec["timestamp_ms"]
            event_type = spec.get("type", "none")

            elapsed_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            wait_ms = target_ms - elapsed_ms
            if wait_ms > 0:
                await asyncio.sleep(wait_ms / 1000.0)

            segment_id = f"seg_{target_ms // 10000:03d}"

            try:
                vision_event = await self.vision.detect_event(
                    "",
                    segment_id,
                    target_ms,
                    event_type=event_type if event_type != "none" else None,
                )
                speech_event = await self.speech.transcribe_segment(
                    "",
                    segment_id,
                    target_ms,
                    event_type=event_type if event_type != "none" else None,
                )
                audio_event = self.audio.create_mock_event(
                    segment_id, target_ms, event_type if event_type != "none" else None
                )

                # Boost confidences for real events to ensure fusion works
                if event_type and event_type != "none":
                    if event_type == "yellow_card":
                        vision_event.detected_event_type = "yellow_card"
                        vision_event.confidence = 0.58 + random.uniform(-0.05, 0.05)
                        speech_event = await self.speech.transcribe_segment(
                            "", segment_id, target_ms, event_type="yellow_card"
                        )
                    elif event_type == "goal":
                        vision_event.confidence = max(vision_event.confidence, 0.88)
                    elif event_type == "foul":
                        vision_event.confidence = max(vision_event.confidence, 0.80)
                    elif event_type == "corner":
                        vision_event.confidence = max(vision_event.confidence, 0.72)

                fused = await self.fuser.fuse_all(vision_event, speech_event, audio_event)

                if fused and fused.composite_confidence >= 0.45:
                    if self.commentary_enabled:
                        commentary = await self.commentary_agent.generate(
                            fused, self._match_history
                        )
                        fused.commentary = commentary
                        self._match_history.append(f"{fused.event_type} at {fused.timestamp_ms}ms")
                    yield fused

            except Exception as exc:
                logger.warning("Mock pipeline step failed: %s", exc)

        logger.info("Mock pipeline completed %ds simulation", self.duration_seconds)
