"""Synthetic events for testing."""

SAMPLE_EVENTS = [
    {"timestamp_ms": 8000, "type": "foul"},
    {"timestamp_ms": 23000, "type": "corner"},
    {"timestamp_ms": 41000, "type": "goal"},
    {"timestamp_ms": 55000, "type": "yellow_card"},
]

NOISE_EVENTS = [
    {"timestamp_ms": 15000, "type": "none"},
    {"timestamp_ms": 32000, "type": "none"},
]
