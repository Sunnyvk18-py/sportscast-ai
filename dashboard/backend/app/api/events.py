"""Detected events CRUD API."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.backend.app.database import get_db
from pipeline.models.event import DetectedEvent, MatchSession

router = APIRouter(prefix="/api/events", tags=["events"])


class EventResponse(BaseModel):
    id: str
    session_id: str
    event_type: str
    timestamp_ms: int
    composite_confidence: float
    signals_agreed: int
    auto_confirmed: bool
    requires_review: bool
    commentary: str | None
    highlight_clip_path: str | None
    vision_confidence: float | None
    speech_confidence: float | None
    audio_energy: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[EventResponse])
async def list_events(
    session_id: str | None = None,
    event_type: str | None = None,
    min_confidence: float | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(DetectedEvent).order_by(DetectedEvent.timestamp_ms.desc())
    if session_id:
        query = query.where(DetectedEvent.session_id == session_id)
    if event_type:
        query = query.where(DetectedEvent.event_type == event_type)
    if min_confidence is not None:
        query = query.where(DetectedEvent.composite_confidence >= min_confidence)
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DetectedEvent).where(DetectedEvent.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/session/{session_id}", response_model=list[EventResponse])
async def get_session_events(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DetectedEvent)
        .where(DetectedEvent.session_id == session_id)
        .order_by(DetectedEvent.timestamp_ms)
    )
    return result.scalars().all()


@router.delete("/{event_id}")
async def delete_event(event_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DetectedEvent).where(DetectedEvent.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    await db.delete(event)
    await db.commit()
    return {"status": "deleted"}
