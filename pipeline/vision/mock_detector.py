"""Mock vision detector for zero-API testing."""

import asyncio
import random
from uuid import uuid4

from pipeline.kafka.schemas import VisionEvent

EVENT_SEQUENCE = [
    None,
    None,
    None,
    "foul",
    None,
    None,
    "goal",
    None,
    "corner",
    None,
]

BASE_CONFIDENCES = {
    None: 0.1,
    "foul": 0.82,
    "goal": 0.91,
    "corner": 0.78,
    "yellow_card": 0.58,
    "red_card": 0.85,
    "substitution": 0.72,
}


class MockVisionDetector:
    def __init__(self):
        self._index = 0

    async def detect_event(
        self, frame_path: str, segment_id: str, timestamp_ms: int, event_type: str | None = None
    ) -> VisionEvent:
        await asyncio.sleep(random.uniform(0.01, 0.05))

        if event_type is not None:
            detected = event_type if event_type != "none" else None
        else:
            detected = EVENT_SEQUENCE[self._index % len(EVENT_SEQUENCE)]
            self._index += 1

        base = BASE_CONFIDENCES.get(detected, 0.5)
        confidence = max(0.0, min(1.0, base + random.uniform(-0.1, 0.1)))
        processing_ms = random.randint(200, 800)

        return VisionEvent(
            event_id=str(uuid4()),
            timestamp_ms=timestamp_ms,
            segment_id=segment_id,
            frame_path=frame_path or "",
            detected_event_type=detected,
            confidence=confidence,
            raw_response=f"mock:{detected}",
            model_used="mock-vision",
            processing_ms=processing_ms,
        )
