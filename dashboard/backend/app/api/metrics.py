"""Real-time pipeline metrics API."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.backend.app.database import get_db
from pipeline.evaluation.benchmarker import OfflineBenchmarker
from pipeline.evaluation.labeled_clips import SAMPLE_LABELED_DATASET
from pipeline.evaluation.metrics import BenchmarkResult
from pipeline.models.event import DetectedEvent

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

_metrics_history: list[dict] = []


@router.get("/live")
async def live_metrics(db: AsyncSession = Depends(get_db)):
    count_result = await db.execute(select(func.count()).select_from(DetectedEvent))
    total = count_result.scalar() or 0

    avg_conf = await db.execute(select(func.avg(DetectedEvent.composite_confidence)))
    avg_confidence = float(avg_conf.scalar() or 0)

    agreement = await db.execute(select(func.avg(DetectedEvent.signals_agreed)))
    signal_agreement_rate = float(agreement.scalar() or 0) / 3.0

    review_depth = await db.execute(
        select(func.count())
        .select_from(DetectedEvent)
        .where(DetectedEvent.requires_review == True)  # noqa: E712
    )

    metrics = {
        "events_per_minute": total / max(1, 1),
        "avg_confidence": avg_confidence,
        "signal_agreement_rate": signal_agreement_rate,
        "review_queue_depth": review_depth.scalar() or 0,
        "false_positive_rate_estimate": 0.05,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _metrics_history.append(metrics)
    if len(_metrics_history) > 100:
        _metrics_history.pop(0)
    return metrics


@router.get("/history")
async def metrics_history():
    return _metrics_history


@router.post("/benchmark", response_model=BenchmarkResult)
async def run_benchmark():
    benchmarker = OfflineBenchmarker(SAMPLE_LABELED_DATASET)
    return await benchmarker.run_benchmark()
