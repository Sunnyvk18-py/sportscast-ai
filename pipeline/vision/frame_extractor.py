"""FFmpeg frame extraction per segment."""

import base64
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

FFMPEG_TIMEOUT = 60


class FrameExtractor:
    """Extracts sample frames from video segments using FFmpeg."""

    def extract_frames(self, segment_path: str, sample_rate: int) -> list[str]:
        temp_dir = tempfile.mkdtemp(prefix="sportscast_frames_")
        output_pattern = os.path.join(temp_dir, "frame_%04d.jpg")
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            segment_path,
            "-vf",
            f"fps=1/{sample_rate}",
            output_pattern,
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=FFMPEG_TIMEOUT, check=False
            )
            if result.returncode != 0:
                logger.error(
                    "FFmpeg frame extraction failed: %s. "
                    "Install FFmpeg: https://ffmpeg.org/download.html",
                    result.stderr,
                )
                return []
            frames = sorted(str(p) for p in Path(temp_dir).glob("frame_*.jpg") if p.is_file())
            return frames
        except FileNotFoundError:
            logger.error("FFmpeg not found. Install FFmpeg: https://ffmpeg.org/download.html")
            return []
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg frame extraction timed out after %ss", FFMPEG_TIMEOUT)
            return []
        finally:
            # Caller should use frames before cleanup; store temp dir on instance
            self._last_temp_dir = temp_dir

    def cleanup_frames(self, frame_paths: list[str]) -> None:
        if not frame_paths:
            return
        temp_dir = os.path.dirname(frame_paths[0])
        if temp_dir and "sportscast_frames_" in temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def frame_to_base64(self, frame_path: str) -> str:
        with open(frame_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
