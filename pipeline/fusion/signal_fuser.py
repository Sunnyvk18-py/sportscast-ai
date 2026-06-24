"""Timestamp alignment and multi-signal voting."""

import logging
from collections import deque
from datetime import datetime, timezone
from uuid import uuid4

from pipeline.config import settings
from pipeline.fusion.confidence_scorer import ConfidenceScorer
from pipeline.kafka.schemas import AudioEvent, FusedEvent, SpeechEvent, VisionEvent

logger = logging.getLogger(__name__)


class SignalFuser:
    def __init__(self, window_ms: int | None = None):
        self.window_ms = window_ms or settings.FUSION_WINDOW_MS
        self.scorer = ConfidenceScorer()
        self.vision_buffer: deque[VisionEvent] = deque(maxlen=100)
        self.speech_buffer: deque[SpeechEvent] = deque(maxlen=100)
        self.audio_buffer: deque[AudioEvent] = deque(maxlen=100)
        self._processed_ids: set[str] = set()

    async def ingest_vision(self, event: VisionEvent) -> FusedEvent | None:
        self.vision_buffer.append(event)
        return await self.try_fuse()

    async def ingest_speech(self, event: SpeechEvent) -> FusedEvent | None:
        self.speech_buffer.append(event)
        return await self.try_fuse()

    async def ingest_audio(self, event: AudioEvent) -> FusedEvent | None:
        self.audio_buffer.append(event)
        return await self.try_fuse()

    async def fuse_all(
        self,
        vision: VisionEvent,
        speech: SpeechEvent,
        audio: AudioEvent,
    ) -> FusedEvent | None:
        """Direct fusion of aligned signals (used by mock pipeline)."""
        event_type = self._dominant_event_type(vision, speech, audio)
        if not event_type or event_type == "none":
            return None

        composite, agreed = self.scorer.score(vision, speech, audio, event_type)
        return self._build_fused_event(vision, speech, audio, event_type, composite, agreed)

    async def try_fuse(self) -> FusedEvent | None:
        for vision in list(self.vision_buffer):
            if vision.event_id in self._processed_ids:
                continue
            if not vision.detected_event_type:
                continue

            speech = self._find_in_window(self.speech_buffer, vision.timestamp_ms)
            audio = self._find_in_window(self.audio_buffer, vision.timestamp_ms)

            if speech is None and audio is None:
                continue

            event_type = self._dominant_event_type(vision, speech, audio)
            if not event_type:
                continue

            composite, agreed = self.scorer.score(vision, speech, audio, event_type)

            if composite < settings.REVIEW_THRESHOLD:
                self._mark_processed(vision, speech, audio)
                continue

            fused = self._build_fused_event(vision, speech, audio, event_type, composite, agreed)
            self._mark_processed(vision, speech, audio)
            return fused

        return None

    def _find_in_window(
        self, buffer: deque, timestamp_ms: int
    ) -> VisionEvent | SpeechEvent | AudioEvent | None:
        best = None
        best_delta = self.window_ms + 1
        for item in buffer:
            delta = abs(item.timestamp_ms - timestamp_ms)
            if delta <= self.window_ms and delta < best_delta:
                best = item
                best_delta = delta
        return best

    def _dominant_event_type(
        self,
        vision: VisionEvent | None,
        speech: SpeechEvent | None,
        audio: AudioEvent | None,
    ) -> str | None:
        votes: dict[str, float] = {}

        if vision and vision.detected_event_type:
            votes[vision.detected_event_type] = votes.get(vision.detected_event_type, 0) + (
                0.45 * vision.confidence
            )
        if speech and speech.detected_event_type:
            votes[speech.detected_event_type] = votes.get(speech.detected_event_type, 0) + (
                0.35 * speech.commentary_confidence
            )
        if vision and vision.detected_event_type and not votes:
            return vision.detected_event_type

        if not votes:
            if vision and vision.detected_event_type:
                return vision.detected_event_type
            if speech and speech.detected_event_type:
                return speech.detected_event_type
            return None

        best_type = max(votes, key=lambda k: votes[k])
        if votes[best_type] < 0.1:
            candidates = [
                (vision, vision.confidence if vision else 0),
                (speech, speech.commentary_confidence if speech else 0),
            ]
            candidates = [
                (s, c) for s, c in candidates if s and getattr(s, "detected_event_type", None)
            ]
            if candidates:
                best_signal = max(candidates, key=lambda x: x[1])[0]
                return best_signal.detected_event_type
            return None

        return best_type

    def _build_fused_event(
        self,
        vision: VisionEvent | None,
        speech: SpeechEvent | None,
        audio: AudioEvent | None,
        event_type: str,
        composite: float,
        agreed: int,
    ) -> FusedEvent:
        requires_review = settings.REVIEW_THRESHOLD <= composite < settings.CONFIDENCE_THRESHOLD
        auto_confirmed = composite >= settings.CONFIDENCE_THRESHOLD

        segment_id = (
            (vision and vision.segment_id)
            or (speech and speech.segment_id)
            or (audio and audio.segment_id)
            or "unknown"
        )
        timestamp_ms = (
            (vision and vision.timestamp_ms)
            or (speech and speech.timestamp_ms)
            or (audio and audio.timestamp_ms)
            or 0
        )

        return FusedEvent(
            event_id=str(uuid4()),
            timestamp_ms=timestamp_ms,
            segment_id=segment_id,
            event_type=event_type,
            composite_confidence=composite,
            vision_signal=vision,
            speech_signal=speech,
            audio_signal=audio,
            signals_agreed=agreed,
            requires_review=requires_review,
            auto_confirmed=auto_confirmed,
            created_at=datetime.now(timezone.utc),
        )

    def _mark_processed(self, *events) -> None:
        for event in events:
            if event is not None:
                self._processed_ids.add(event.event_id)
                if isinstance(event, VisionEvent):
                    self._safe_remove(self.vision_buffer, event)
                elif isinstance(event, SpeechEvent):
                    self._safe_remove(self.speech_buffer, event)
                elif isinstance(event, AudioEvent):
                    self._safe_remove(self.audio_buffer, event)

    def _safe_remove(self, buffer: deque, item) -> None:
        try:
            buffer.remove(item)
        except ValueError:
            pass
