"""Tests for confidence scorer."""

from pipeline.fusion.confidence_scorer import ConfidenceScorer
from pipeline.kafka.schemas import AudioEvent, SpeechEvent, VisionEvent


def test_score_all_signals_agree():
    scorer = ConfidenceScorer()
    vision = VisionEvent(
        timestamp_ms=1000, segment_id="s", detected_event_type="goal", confidence=0.9
    )
    speech = SpeechEvent(
        timestamp_ms=1000,
        segment_id="s",
        detected_event_type="goal",
        commentary_confidence=0.85,
    )
    audio = AudioEvent(timestamp_ms=1000, segment_id="s", energy_level=0.85)

    composite, agreed = scorer.score(vision, speech, audio, "goal")
    assert composite >= 0.75
    assert agreed >= 2
