"""Human review queue endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.backend.app.database import get_db
from pipeline.models.event import DetectedEvent, ReviewDecision

router = APIRouter(prefix="/api/review", tags=["review"])


class ReviewAction(BaseModel):
    notes: str = ""


class ReviewEventResponse(BaseModel):
    id: str
    event_type: str
    timestamp_ms: int
    composite_confidence: float
    signals_agreed: int
    commentary: str | None
    requires_review: bool

    model_config = {"from_attributes": True}


@router.get("", response_model=list[ReviewEventResponse])
async def list_pending_review(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DetectedEvent)
        .where(DetectedEvent.requires_review == True)  # noqa: E712
        .order_by(DetectedEvent.created_at.desc())
    )
    events = result.scalars().all()
    pending = []
    for event in events:
        decision = await db.execute(
            select(ReviewDecision).where(ReviewDecision.event_id == event.id)
        )
        if decision.scalar_one_or_none() is None:
            pending.append(event)
    return pending


@router.post("/{event_id}/approve")
async def approve_event(
    event_id: str, body: ReviewAction, db: AsyncSession = Depends(get_db)
):
    event = await _get_event(event_id, db)
    decision = ReviewDecision(
        event_id=event_id,
        decision="approved",
        notes=body.notes,
        decided_at=datetime.now(timezone.utc),
    )
    event.requires_review = False
    event.auto_confirmed = True
    db.add(decision)
    await db.commit()
    return {"status": "approved", "event_id": event_id}


@router.post("/{event_id}/reject")
async def reject_event(
    event_id: str, body: ReviewAction, db: AsyncSession = Depends(get_db)
):
    event = await _get_event(event_id, db)
    decision = ReviewDecision(
        event_id=event_id,
        decision="rejected",
        notes=body.notes,
        decided_at=datetime.now(timezone.utc),
    )
    event.requires_review = False
    db.add(decision)
    await db.commit()
    return {"status": "rejected", "event_id": event_id}


@router.get("/stats")
async def review_stats(db: AsyncSession = Depends(get_db)):
    total_review = await db.execute(
        select(func.count()).select_from(DetectedEvent).where(
            DetectedEvent.requires_review == True  # noqa: E712
        )
    )
    approved = await db.execute(
        select(func.count()).select_from(ReviewDecision).where(
            ReviewDecision.decision == "approved"
        )
    )
    rejected = await db.execute(
        select(func.count()).select_from(ReviewDecision).where(
            ReviewDecision.decision == "rejected"
        )
    )
    pending_result = await db.execute(
        select(DetectedEvent).where(DetectedEvent.requires_review == True)  # noqa: E712
    )
    pending_events = pending_result.scalars().all()
    pending_count = 0
    for event in pending_events:
        d = await db.execute(
            select(ReviewDecision).where(ReviewDecision.event_id == event.id)
        )
        if d.scalar_one_or_none() is None:
            pending_count += 1

    return {
        "total": total_review.scalar() or 0,
        "approved": approved.scalar() or 0,
        "rejected": rejected.scalar() or 0,
        "pending": pending_count,
    }


async def _get_event(event_id: str, db: AsyncSession) -> DetectedEvent:
    result = await db.execute(select(DetectedEvent).where(DetectedEvent.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
