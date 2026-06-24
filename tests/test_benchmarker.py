"""Tests for benchmarker."""

import pytest

from pipeline.evaluation.benchmarker import OfflineBenchmarker
from pipeline.evaluation.labeled_clips import SAMPLE_LABELED_DATASET


@pytest.mark.asyncio
async def test_run_benchmark():
    benchmarker = OfflineBenchmarker(SAMPLE_LABELED_DATASET[:2])
    result = await benchmarker.run_benchmark()
    assert result.total_clips == 2
    assert result.precision >= 0
