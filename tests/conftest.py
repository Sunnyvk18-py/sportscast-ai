"""Pytest configuration."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def sample_events():
    return [
        {"timestamp_ms": 8000, "type": "foul"},
        {"timestamp_ms": 41000, "type": "goal"},
    ]
