"""Tests for transcriber."""

from pipeline.speech.commentary_parser import CommentaryParser


def test_commentary_parser_goal():
    parser = CommentaryParser()
    event = parser.parse("Oh what a goal! He scores!", 1000, "seg_001")
    assert event.detected_event_type == "goal"
    assert event.commentary_confidence > 0.3


def test_commentary_parser_no_match():
    parser = CommentaryParser()
    event = parser.parse("The weather is nice today.", 1000, "seg_001")
    assert event.detected_event_type is None
