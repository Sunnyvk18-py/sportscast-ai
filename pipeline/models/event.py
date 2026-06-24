"""SQLAlchemy ORM models for SportsCast AI."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MatchSession(Base):
    __tablename__ = "match_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    source_video_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    events: Mapped[list["DetectedEvent"]] = relationship(back_populates="session")


class DetectedEvent(Base):
    __tablename__ = "detected_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("match_sessions.id"))
    event_type: Mapped[str] = mapped_column(String(64))
    timestamp_ms: Mapped[int] = mapped_column(Integer)
    composite_confidence: Mapped[float] = mapped_column(Float)
    signals_agreed: Mapped[int] = mapped_column(Integer, default=0)
    auto_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_review: Mapped[bool] = mapped_column(Boolean, default=False)
    commentary: Mapped[str | None] = mapped_column(Text, nullable=True)
    highlight_clip_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    vision_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    speech_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    audio_energy: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    session: Mapped["MatchSession"] = relationship(back_populates="events")
    review_decisions: Mapped[list["ReviewDecision"]] = relationship(back_populates="event")


class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("detected_events.id"))
    decision: Mapped[str] = mapped_column(String(32))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    event: Mapped["DetectedEvent"] = relationship(back_populates="review_decisions")
