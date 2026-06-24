"""Sample labeled dataset for testing."""

from dataclasses import dataclass, field


@dataclass
class LabeledClip:
    clip_path: str
    ground_truth_events: list[dict] = field(default_factory=list)


SAMPLE_LABELED_DATASET: list[LabeledClip] = [
    LabeledClip(
        clip_path="mock_clip_001",
        ground_truth_events=[
            {"timestamp_ms": 8000, "event_type": "foul"},
            {"timestamp_ms": 23000, "event_type": "corner"},
        ],
    ),
    LabeledClip(
        clip_path="mock_clip_002",
        ground_truth_events=[
            {"timestamp_ms": 41000, "event_type": "goal"},
        ],
    ),
    LabeledClip(
        clip_path="mock_clip_003",
        ground_truth_events=[
            {"timestamp_ms": 12000, "event_type": "foul"},
            {"timestamp_ms": 35000, "event_type": "goal"},
        ],
    ),
    LabeledClip(
        clip_path="mock_clip_004",
        ground_truth_events=[
            {"timestamp_ms": 55000, "event_type": "yellow_card"},
        ],
    ),
    LabeledClip(
        clip_path="mock_clip_005",
        ground_truth_events=[
            {"timestamp_ms": 15000, "event_type": "corner"},
            {"timestamp_ms": 42000, "event_type": "goal"},
            {"timestamp_ms": 58000, "event_type": "substitution"},
        ],
    ),
]
