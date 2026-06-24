"""Rule-based event extraction from commentary transcripts."""

import time
from uuid import uuid4

from pipeline.kafka.schemas import SpeechEvent

KEYWORD_MAP: dict[str, list[str]] = {
    "goal": [
        "goal",
        "scores",
        "scored",
        "what a goal",
        "1-0",
        "2-1",
        "3-2",
        "back of the net",
        "finds the net",
    ],
    "foul": ["foul", "free kick", "penalty", "referee", "whistle"],
    "corner": ["corner", "corner kick", "from the corner"],
    "yellow_card": ["yellow card", "booked", "caution"],
    "red_card": ["red card", "sent off", "dismissed"],
    "substitution": ["substitution", "coming off", "coming on", "replaced"],
}


class CommentaryParser:
    def parse(self, transcript: str, timestamp_ms: int, segment_id: str) -> SpeechEvent:
        start = time.perf_counter()
        scores: dict[str, float] = {}
        lower = transcript.lower()

        for event_type, keywords in KEYWORD_MAP.items():
            matches = sum(1 for kw in keywords if kw in lower)
            scores[event_type] = min(1.0, matches / 3.0)

        best_type: str | None = None
        best_score = 0.0
        for event_type, score in scores.items():
            if score > best_score:
                best_score = score
                best_type = event_type

        detected = best_type if best_score > 0.3 else None
        processing_ms = int((time.perf_counter() - start) * 1000)

        return SpeechEvent(
            event_id=str(uuid4()),
            timestamp_ms=timestamp_ms,
            segment_id=segment_id,
            transcript=transcript,
            detected_event_type=detected,
            commentary_confidence=best_score,
            language="en",
            processing_ms=processing_ms,
        )
