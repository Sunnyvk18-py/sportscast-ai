"""Highlight clips endpoints."""

import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dashboard.backend.app.config import settings
from dashboard.backend.app.database import get_db
from pipeline.models.event import DetectedEvent

router = APIRouter(prefix="/api/highlights", tags=["highlights"])


class HighlightResponse(BaseModel):
    id: str
    event_type: str
    timestamp_ms: int
    composite_confidence: float
    commentary: str | None
    highlight_clip_path: str | None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[HighlightResponse])
async def list_highlights(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DetectedEvent)
        .where(DetectedEvent.highlight_clip_path.isnot(None))
        .order_by(DetectedEvent.timestamp_ms.desc())
    )
    return result.scalars().all()


@router.get("/{event_id}/download")
async def download_highlight(event_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DetectedEvent).where(DetectedEvent.id == event_id))
    event = result.scalar_one_or_none()
    if not event or not event.highlight_clip_path:
        raise HTTPException(status_code=404, detail="Highlight not found")

    clip_path = event.highlight_clip_path
    if not os.path.isabs(clip_path):
        clip_path = os.path.join(settings.CLIPS_DIR, os.path.basename(clip_path))

    if not os.path.isfile(clip_path):
        raise HTTPException(status_code=404, detail="Clip file not found")

    return FileResponse(clip_path, media_type="video/mp4", filename=os.path.basename(clip_path))
