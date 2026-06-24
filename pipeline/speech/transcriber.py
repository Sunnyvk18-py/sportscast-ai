"""Whisper real-time transcription."""

import logging
import time

from pipeline.kafka.schemas import SpeechEvent
from pipeline.speech.commentary_parser import CommentaryParser

logger = logging.getLogger(__name__)


class WhisperTranscriber:
    def __init__(self, model_size: str = "base", api_key: str = ""):
        self.model_size = model_size
        self.api_key = api_key
        self._local_model = None
        self.parser = CommentaryParser()

    def _load_local_model(self):
        if self._local_model is None:
            import whisper

            self._local_model = whisper.load_model(self.model_size)
        return self._local_model

    async def transcribe_segment(
        self, audio_path: str, segment_id: str, timestamp_ms: int
    ) -> SpeechEvent:
        start = time.perf_counter()
        transcript = ""
        try:
            if self.api_key:
                from openai import AsyncOpenAI

                client = AsyncOpenAI(api_key=self.api_key)
                with open(audio_path, "rb") as f:
                    response = await client.audio.transcriptions.create(model="whisper-1", file=f)
                transcript = response.text
            else:
                model = self._load_local_model()
                result = model.transcribe(audio_path)
                transcript = result.get("text", "")
        except Exception as exc:
            logger.warning("Whisper transcription failed: %s", exc)
            transcript = ""

        processing_ms = int((time.perf_counter() - start) * 1000)
        event = self.parser.parse(transcript, timestamp_ms, segment_id)
        event.processing_ms = processing_ms
        return event
