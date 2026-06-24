"""Mock transcriber synchronized with mock vision events."""

import random
from uuid import uuid4

from pipeline.kafka.schemas import SpeechEvent

MOCK_TRANSCRIPTS: dict[str, list[str]] = {
    "foul": [
        "That's a clear foul! The referee blows the whistle.",
        "Free kick awarded after a heavy challenge in midfield.",
    ],
    "goal": [
        "Oh what a goal! The striker puts it in the back of the net!",
        "GOAL! What a finish from the edge of the box!",
    ],
    "corner": [
        "Corner kick awarded, the winger races to place the ball.",
        "They win a corner on the far side.",
    ],
    "yellow_card": [
        "Yellow card shown — the referee has made his decision.",
        "He's booked for that challenge.",
    ],
    "red_card": [
        "Red card! He's sent off!",
        "Dismissed! A straight red from the referee.",
    ],
    "substitution": [
        "Substitution made — fresh legs coming on.",
        "He's coming off, replaced by the substitute.",
    ],
    None: [
        "Good possession in the midfield here.",
        "The ball is played back to the defense.",
        "Building from the back under pressure.",
    ],
}


class MockWhisperTranscriber:
    async def transcribe_segment(
        self,
        audio_path: str,
        segment_id: str,
        timestamp_ms: int,
        event_type: str | None = None,
    ) -> SpeechEvent:
        key = event_type if event_type and event_type != "none" else None
        options = MOCK_TRANSCRIPTS.get(key, MOCK_TRANSCRIPTS[None])
        transcript = random.choice(options)
        confidence = 0.85 if key else 0.15

        if key:
            from pipeline.speech.commentary_parser import CommentaryParser

            return CommentaryParser().parse(transcript, timestamp_ms, segment_id)

        return SpeechEvent(
            event_id=str(uuid4()),
            timestamp_ms=timestamp_ms,
            segment_id=segment_id,
            transcript=transcript,
            detected_event_type=None,
            commentary_confidence=confidence,
            language="en",
            processing_ms=random.randint(150, 400),
        )
