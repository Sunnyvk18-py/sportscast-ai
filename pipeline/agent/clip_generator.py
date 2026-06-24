"""FFmpeg auto-clip trimmer."""

import logging
import os
import subprocess

from pipeline.kafka.schemas import FusedEvent

logger = logging.getLogger(__name__)

FFMPEG_TIMEOUT = 60


class ClipGenerator:
    def __init__(self, source_video_path: str, clips_dir: str):
        self.source_video_path = source_video_path
        self.clips_dir = clips_dir
        os.makedirs(clips_dir, exist_ok=True)

    async def generate_clip(self, event: FusedEvent, padding_seconds: int = 5) -> str | None:
        if not os.path.isfile(self.source_video_path):
            logger.warning(
                "Source video not available for clip generation: %s",
                self.source_video_path,
            )
            return None

        start = max(0, (event.timestamp_ms / 1000) - padding_seconds)
        end = (event.timestamp_ms / 1000) + padding_seconds
        filename = f"{event.event_id}_{event.event_type}.mp4"
        output_path = os.path.join(self.clips_dir, filename)

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            self.source_video_path,
            "-ss",
            str(start),
            "-to",
            str(end),
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-preset",
            "fast",
            output_path,
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=FFMPEG_TIMEOUT, check=False
            )
            if result.returncode != 0:
                logger.error("Clip generation failed: %s", result.stderr)
                return None
            return os.path.relpath(output_path)
        except FileNotFoundError:
            logger.error("FFmpeg not found. Install FFmpeg: https://ffmpeg.org/download.html")
            return None
        except subprocess.TimeoutExpired:
            logger.error("Clip generation timed out")
            return None
