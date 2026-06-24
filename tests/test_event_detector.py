"""Tests for event detector."""

from pipeline.vision.event_detector import VisionEventDetector


def test_parse_json_response():
    detector = VisionEventDetector(api_key="")
    parsed = detector._parse_response(
        '{"event_type": "goal", "confidence": 0.92, "reasoning": "celebration"}'
    )
    assert parsed["event_type"] == "goal"
    assert parsed["confidence"] == 0.92


def test_parse_embedded_json():
    detector = VisionEventDetector(api_key="")
    parsed = detector._parse_response(
        'Result: {"event_type": "foul", "confidence": 0.8, "reasoning": "x"}'
    )
    assert parsed["event_type"] == "foul"
