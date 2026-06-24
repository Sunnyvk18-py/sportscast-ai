"""Match session management API."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.backend.app.api.ws import broadcast_event
from dashboard.backend.app.database import get_db
from pipeline.kafka.schemas import FusedEvent
from pipeline.models.event import DetectedEvent, MatchSession

router = APIRouter(prefix="/api/matches", tags=["matches"])


class MatchCreate(BaseModel):
    name: str
    source_url: str


class MatchResponse(BaseModel):
    id: str
    name: str
    source_url: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    total_events: int
    source_video_path: str | None

    model_config = {"from_attributes": True}


@router.post("", response_model=MatchResponse)
async def create_match(body: MatchCreate, db: AsyncSession = Depends(get_db)):
    match = MatchSession(
        id=str(uuid.uuid4()),
        name=body.name,
        source_url=body.source_url,
        status="pending",
        started_at=datetime.now(timezone.utc),
    )
    db.add(match)
    await db.commit()
    await db.refresh(match)
    return match


@router.get("", response_model=list[MatchResponse])
async def list_matches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MatchSession).order_by(MatchSession.started_at.desc()))
    return result.scalars().all()


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MatchSession).where(MatchSession.id == match_id))
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@router.put("/{match_id}/start", response_model=MatchResponse)
async def start_match(match_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MatchSession).where(MatchSession.id == match_id))
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.status = "running"
    await db.commit()
    await db.refresh(match)
    return match


@router.put("/{match_id}/complete", response_model=MatchResponse)
async def complete_match(match_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MatchSession).where(MatchSession.id == match_id))
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.status = "completed"
    match.completed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(match)
    return match


@router.post("/{match_id}/ingest")
async def ingest_event(match_id: str, event: FusedEvent, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MatchSession).where(MatchSession.id == match_id))
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    detected = DetectedEvent(
        id=event.event_id,
        session_id=match_id,
        event_type=event.event_type,
        timestamp_ms=event.timestamp_ms,
        composite_confidence=event.composite_confidence,
        signals_agreed=event.signals_agreed,
        auto_confirmed=event.auto_confirmed,
        requires_review=event.requires_review,
        commentary=event.commentary,
        highlight_clip_path=event.highlight_clip_path,
        vision_confidence=event.vision_signal.confidence if event.vision_signal else None,
        speech_confidence=event.speech_signal.commentary_confidence
        if event.speech_signal
        else None,
        audio_energy=event.audio_signal.energy_level if event.audio_signal else None,
        created_at=event.created_at,
    )
    db.add(detected)
    match.total_events += 1
    await db.commit()

    await broadcast_event(event)
    return {"status": "ingested", "event_id": event.event_id}
