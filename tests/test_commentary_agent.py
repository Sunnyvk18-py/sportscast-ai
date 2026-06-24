"""Tests for commentary agent."""

import pytest

from pipeline.agent.commentary_agent import CommentaryAgent
from pipeline.kafka.schemas import FusedEvent


@pytest.mark.asyncio
async def test_commentary_fallback():
    agent = CommentaryAgent()
    event = FusedEvent(
        timestamp_ms=41000,
        segment_id="seg",
        event_type="goal",
        composite_confidence=0.9,
        signals_agreed=3,
    )
    text = await agent.generate(event, [])
    assert text
    assert len(text) > 0
