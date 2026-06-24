"""Pydantic v2 event schemas per Kafka topic."""

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class VisionEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp_ms: int
    segment_id: str
    frame_path: str = ""
    detected_event_type: str | None = None
    confidence: float = 0.0
    raw_response: str = ""
    model_used: str = "mock"
    processing_ms: int = 0


class SpeechEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp_ms: int
    segment_id: str
    transcript: str = ""
    detected_event_type: str | None = None
    commentary_confidence: float = 0.0
    language: str = "en"
    processing_ms: int = 0


class AudioEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp_ms: int
    segment_id: str
    energy_level: float = 0.0
    crowd_state: str = "ambient"
    classifier_confidence: float = 0.0
    mfcc_features: list[float] = Field(default_factory=list)
    processing_ms: int = 0


class FusedEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp_ms: int
    segment_id: str
    event_type: str
    composite_confidence: float
    vision_signal: VisionEvent | None = None
    speech_signal: SpeechEvent | None = None
    audio_signal: AudioEvent | None = None
    signals_agreed: int = 0
    requires_review: bool = False
    auto_confirmed: bool = False
    commentary: str | None = None
    highlight_clip_path: str | None = None
    created_at: datetime = Field(default_factory=_utcnow)


class ReviewItem(BaseModel):
    review_id: str = Field(default_factory=lambda: str(uuid4()))
    fused_event: FusedEvent
    reviewer_decision: str | None = None
    reviewer_notes: str | None = None
    reviewed_at: datetime | None = None
    created_at: datetime = Field(default_factory=_utcnow)
