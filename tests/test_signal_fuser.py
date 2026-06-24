"""Tests for signal fuser."""

import pytest

from pipeline.fusion.signal_fuser import SignalFuser
from pipeline.kafka.schemas import AudioEvent, SpeechEvent, VisionEvent


@pytest.mark.asyncio
async def test_fuse_all_goal():
    vision = VisionEvent(
        timestamp_ms=41000,
        segment_id="seg",
        detected_event_type="goal",
        confidence=0.91,
    )
    speech = SpeechEvent(
        timestamp_ms=41000,
        segment_id="seg",
        transcript="Oh what a goal!",
        detected_event_type="goal",
        commentary_confidence=0.85,
    )
    audio = AudioEvent(
        timestamp_ms=41000,
        segment_id="seg",
        energy_level=0.85,
        crowd_state="roar",
        classifier_confidence=0.88,
        mfcc_features=[0.1 * i for i in range(13)],
    )

    fuser = SignalFuser()
    fused = await fuser.fuse_all(vision, speech, audio)
    assert fused is not None
    assert fused.event_type == "goal"
    assert fused.composite_confidence >= 0.45
