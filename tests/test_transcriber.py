"""Tests for transcriber."""

import pytest

from pipeline.speech.commentary_parser import CommentaryParser
from pipeline.speech.mock_transcriber import MockWhisperTranscriber


def test_commentary_parser_goal():
    parser = CommentaryParser()
    event = parser.parse("Oh what a goal! He scores!", 1000, "seg_001")
    assert event.detected_event_type == "goal"
    assert event.commentary_confidence > 0.3


@pytest.mark.asyncio
async def test_mock_transcriber():
    transcriber = MockWhisperTranscriber()
    event = await transcriber.transcribe_segment("", "seg_001", 8000, event_type="goal")
    assert event.detected_event_type == "goal"
