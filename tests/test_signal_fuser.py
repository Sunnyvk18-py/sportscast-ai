"""Tests for signal fuser."""

import pytest

from pipeline.audio.classifier import CrowdNoiseClassifier
from pipeline.fusion.signal_fuser import SignalFuser
from pipeline.speech.mock_transcriber import MockWhisperTranscriber
from pipeline.vision.mock_detector import MockVisionDetector


@pytest.mark.asyncio
async def test_fuse_all_goal():
    vision = await MockVisionDetector().detect_event("", "seg", 41000, event_type="goal")
    speech = await MockWhisperTranscriber().transcribe_segment("", "seg", 41000, event_type="goal")
    audio = CrowdNoiseClassifier().create_mock_event("seg", 41000, "goal")

    fuser = SignalFuser()
    fused = await fuser.fuse_all(vision, speech, audio)
    assert fused is not None
    assert fused.event_type == "goal"
    assert fused.composite_confidence >= 0.45
