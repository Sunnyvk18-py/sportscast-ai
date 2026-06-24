"""Tests for event detector."""

import pytest

from pipeline.vision.mock_detector import MockVisionDetector


@pytest.mark.asyncio
async def test_mock_detector_returns_event():
    detector = MockVisionDetector()
    event = await detector.detect_event("", "seg_001", 8000, event_type="goal")
    assert event.detected_event_type == "goal"
    assert 0 <= event.confidence <= 1
