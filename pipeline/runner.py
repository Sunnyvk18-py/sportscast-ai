"""Real-time multimodal pipeline orchestrator."""

import asyncio
import logging
import os
from collections.abc import AsyncGenerator
from pathlib import Path

import httpx

from pipeline.agent.clip_generator import ClipGenerator
from pipeline.agent.commentary_agent import CommentaryAgent
from pipeline.audio.classifier import CrowdNoiseClassifier
from pipeline.config import settings
from pipeline.fusion.review_queue import ReviewQueue
from pipeline.fusion.signal_fuser import SignalFuser
from pipeline.ingestor.video_ingestor import VideoIngestor
from pipeline.kafka.producer import SportsCastProducer
from pipeline.kafka.schemas import FusedEvent, ReviewItem, VisionEvent
from pipeline.speech.transcriber import WhisperTranscriber
from pipeline.vision.event_detector import LLaVAEventDetector, VisionEventDetector
from pipeline.vision.frame_extractor import FrameExtractor

logger = logging.getLogger(__name__)


class SportsCastPipeline:
    """End-to-end pipeline: ingest → vision/speech/audio → fuse → commentary → clips → dashboard."""

    def __init__(
        self,
        source_url: str,
        match_name: str = "Live Match",
        post_to_dashboard: bool = True,
        generate_clips: bool = True,
        generate_commentary: bool = True,
    ):
        self.source_url = source_url
        self.match_name = match_name
        self.post_to_dashboard = post_to_dashboard
        self.generate_clips = generate_clips
        self.generate_commentary = generate_commentary

        self.ingestor = VideoIngestor(source_url, settings.SEGMENTS_DIR, settings.SEGMENT_DURATION)
        self.frame_extractor = FrameExtractor()
        self.fuser = SignalFuser()
        self.review_queue = ReviewQueue()
        self.producer = SportsCastProducer(settings.KAFKA_BOOTSTRAP_SERVERS)
        self.commentary_agent = CommentaryAgent(api_key=settings.OPENAI_API_KEY)
        self.audio_classifier = CrowdNoiseClassifier()
        self.speech = WhisperTranscriber(api_key=settings.OPENAI_API_KEY)

        if settings.USE_LLAVA:
            self.vision = LLaVAEventDetector()
        elif settings.OPENAI_API_KEY:
            self.vision = VisionEventDetector(api_key=settings.OPENAI_API_KEY)
        else:
            logger.warning(
                "No OPENAI_API_KEY and USE_LLAVA=false — vision detections will be empty. "
                "Set OPENAI_API_KEY in .env for GPT-4o Vision."
            )
            self.vision = VisionEventDetector(api_key="")

        self._session_id: str | None = None
        self._source_video_path: str | None = None
        self._clip_generator: ClipGenerator | None = None
        self._match_history: list[str] = []

    async def run(self) -> AsyncGenerator[FusedEvent, None]:
        os.makedirs(settings.SEGMENTS_DIR, exist_ok=True)
        os.makedirs(settings.CLIPS_DIR, exist_ok=True)

        if self.post_to_dashboard:
            await self._init_dashboard_session()

        logger.info("Downloading stream/video from %s", self.source_url)
        self._source_video_path = self.ingestor.download_video()
        if self.generate_clips and self._source_video_path:
            self._clip_generator = ClipGenerator(self._source_video_path, settings.CLIPS_DIR)

        segment_index = 0
        async for segment_path in self.ingestor.segment_to_hls(self._source_video_path):
            timestamp_ms = segment_index * settings.SEGMENT_DURATION * 1000
            segment_id = Path(segment_path).stem
            logger.info("Processing segment %s @ %dms", segment_id, timestamp_ms)

            fused = await self._process_segment(segment_path, segment_id, timestamp_ms)
            segment_index += 1

            if fused is None:
                continue

            if self.generate_commentary:
                try:
                    fused.commentary = await self.commentary_agent.generate(
                        fused, self._match_history
                    )
                    self._match_history.append(f"{fused.event_type} at {fused.timestamp_ms}ms")
                except Exception as exc:
                    logger.warning("Commentary generation failed: %s", exc)

            if (
                self.generate_clips
                and self._clip_generator
                and (fused.auto_confirmed or fused.requires_review)
            ):
                try:
                    clip_path = await self._clip_generator.generate_clip(fused)
                    if clip_path:
                        fused.highlight_clip_path = clip_path
                except Exception as exc:
                    logger.warning("Clip generation failed: %s", exc)

            await self._publish(fused)
            yield fused

        if self._session_id and self.post_to_dashboard:
            await self._complete_session()

        logger.info("Pipeline finished — processed %d segments", segment_index)

    async def _process_segment(
        self, segment_path: str, segment_id: str, timestamp_ms: int
    ) -> FusedEvent | None:
        audio_path: str | None = None
        try:
            vision_task = asyncio.create_task(
                self._run_vision(segment_path, segment_id, timestamp_ms)
            )
            audio_path = await asyncio.to_thread(self.ingestor.get_segment_audio, segment_path)
            speech_task = asyncio.create_task(
                self._run_speech(audio_path, segment_id, timestamp_ms)
            )
            audio_task = asyncio.create_task(self._run_audio(audio_path, segment_id, timestamp_ms))

            vision_event, speech_event, audio_event = await asyncio.gather(
                vision_task, speech_task, audio_task, return_exceptions=True
            )

            if isinstance(vision_event, BaseException):
                logger.warning("Vision branch failed: %s", vision_event)
                vision_event = VisionEvent(
                    timestamp_ms=timestamp_ms, segment_id=segment_id, frame_path=""
                )
            if isinstance(speech_event, BaseException):
                logger.warning("Speech branch failed: %s", speech_event)
                from pipeline.kafka.schemas import SpeechEvent

                speech_event = SpeechEvent(timestamp_ms=timestamp_ms, segment_id=segment_id)
            if isinstance(audio_event, BaseException):
                logger.warning("Audio branch failed: %s", audio_event)
                from pipeline.kafka.schemas import AudioEvent

                audio_event = AudioEvent(timestamp_ms=timestamp_ms, segment_id=segment_id)

            await self.producer.produce(settings.TOPIC_VISION_EVENTS, vision_event)
            await self.producer.produce(settings.TOPIC_SPEECH_EVENTS, speech_event)
            await self.producer.produce(settings.TOPIC_AUDIO_EVENTS, audio_event)

            fused = await self.fuser.fuse_all(vision_event, speech_event, audio_event)
            if fused is None or fused.composite_confidence < settings.REVIEW_THRESHOLD:
                return None

            return fused
        except Exception as exc:
            logger.warning("Segment processing failed: %s", exc)
            return None
        finally:
            if audio_path and os.path.isfile(audio_path):
                try:
                    os.remove(audio_path)
                except OSError:
                    pass

    async def _run_vision(
        self, segment_path: str, segment_id: str, timestamp_ms: int
    ) -> VisionEvent:
        frames = await asyncio.to_thread(
            self.frame_extractor.extract_frames,
            segment_path,
            settings.FRAME_SAMPLE_RATE,
        )
        if not frames:
            return VisionEvent(timestamp_ms=timestamp_ms, segment_id=segment_id, frame_path="")
        try:
            best: VisionEvent | None = None
            for frame_path in frames:
                event = await self.vision.detect_event(frame_path, segment_id, timestamp_ms)
                if best is None or event.confidence > best.confidence:
                    best = event
            return best or VisionEvent(timestamp_ms=timestamp_ms, segment_id=segment_id)
        finally:
            self.frame_extractor.cleanup_frames(frames)

    async def _run_speech(self, audio_path: str, segment_id: str, timestamp_ms: int):
        return await self.speech.transcribe_segment(audio_path, segment_id, timestamp_ms)

    async def _run_audio(self, audio_path: str, segment_id: str, timestamp_ms: int):
        return await self.audio_classifier.classify(audio_path, segment_id, timestamp_ms)

    async def _publish(self, event: FusedEvent) -> None:
        await self.producer.produce(settings.TOPIC_FUSED_EVENTS, event)

        if event.requires_review:
            review_item = ReviewItem(fused_event=event)
            await self.review_queue.put(review_item)
            await self.producer.produce(settings.TOPIC_REVIEW_QUEUE, review_item)

        if self.post_to_dashboard and self._session_id:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(
                        f"{settings.DASHBOARD_URL}/api/matches/{self._session_id}/ingest",
                        json=event.model_dump(mode="json"),
                    )
                    resp.raise_for_status()
            except Exception as exc:
                logger.warning("Dashboard ingest failed: %s", exc)

    async def _init_dashboard_session(self) -> None:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{settings.DASHBOARD_URL}/api/matches",
                    json={"name": self.match_name, "source_url": self.source_url},
                )
                resp.raise_for_status()
                self._session_id = resp.json()["id"]
                await client.put(f"{settings.DASHBOARD_URL}/api/matches/{self._session_id}/start")
                logger.info("Dashboard session started: %s", self._session_id)
        except Exception as exc:
            logger.warning("Dashboard unavailable (%s) — events will print locally only", exc)
            self.post_to_dashboard = False

    async def _complete_session(self) -> None:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                await client.put(
                    f"{settings.DASHBOARD_URL}/api/matches/{self._session_id}/complete"
                )
        except Exception as exc:
            logger.warning("Could not mark session complete: %s", exc)
