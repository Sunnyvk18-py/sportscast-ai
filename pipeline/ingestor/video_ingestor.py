"""yt-dlp + FFmpeg HLS segmenter."""

import asyncio
import logging
import os
import subprocess
import tempfile
from collections.abc import AsyncGenerator
from pathlib import Path

logger = logging.getLogger(__name__)

FFMPEG_TIMEOUT = 60


class VideoIngestor:
    def __init__(self, source_url: str, output_dir: str, segment_duration: int = 10):
        self.source_url = source_url
        self.output_dir = output_dir
        self.segment_duration = segment_duration
        os.makedirs(output_dir, exist_ok=True)

    def download_video(self, url: str | None = None) -> str:
        source = url or self.source_url
        if os.path.isfile(source):
            logger.info("Using local video file: %s", source)
            return source

        output_template = os.path.join(self.output_dir, "source.%(ext)s")
        cmd = [
            "yt-dlp",
            "-o",
            output_template,
            "--no-playlist",
            source,
        ]
        try:
            logger.info("Downloading video from %s", source)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=False)
            if result.returncode != 0:
                logger.error("yt-dlp download failed: %s", result.stderr)
                raise RuntimeError(f"yt-dlp failed: {result.stderr}")

            for ext in ("mp4", "mkv", "webm", "avi"):
                path = os.path.join(self.output_dir, f"source.{ext}")
                if os.path.isfile(path):
                    logger.info("Downloaded video: %s", path)
                    return path

            files = list(Path(self.output_dir).glob("source.*"))
            if files:
                return str(files[0])
            raise RuntimeError("Download completed but no video file found")
        except FileNotFoundError:
            logger.error("yt-dlp not found. Install with: pip install yt-dlp")
            raise

    async def segment_to_hls(self, video_path: str) -> AsyncGenerator[str, None]:
        segment_pattern = os.path.join(self.output_dir, "seg_%03d.ts")
        playlist = os.path.join(self.output_dir, "playlist.m3u8")
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-hls_time",
            str(self.segment_duration),
            "-hls_list_size",
            "0",
            "-hls_segment_filename",
            segment_pattern,
            playlist,
        ]

        seen: set[str] = set()
        process = None
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            while True:
                if process.returncode is not None:
                    break
                for seg in sorted(Path(self.output_dir).glob("seg_*.ts")):
                    path = str(seg)
                    if path not in seen:
                        seen.add(path)
                        yield path
                if process.returncode is None:
                    try:
                        await asyncio.wait_for(process.wait(), timeout=0.5)
                    except asyncio.TimeoutError:
                        await asyncio.sleep(0.5)
                        continue
                break

            for seg in sorted(Path(self.output_dir).glob("seg_*.ts")):
                path = str(seg)
                if path not in seen:
                    seen.add(path)
                    yield path
        except FileNotFoundError:
            logger.error("FFmpeg not found. Install FFmpeg: https://ffmpeg.org/download.html")
        except asyncio.CancelledError:
            if process and process.returncode is None:
                process.terminate()
                await process.wait()
            raise
        finally:
            if process and process.returncode is None:
                try:
                    process.terminate()
                except ProcessLookupError:
                    pass

    def extract_audio_track(self, video_path: str, output_path: str) -> str:
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            output_path,
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=FFMPEG_TIMEOUT, check=False
            )
            if result.returncode != 0:
                logger.error("Audio extraction failed: %s", result.stderr)
                raise RuntimeError(result.stderr)
            return output_path
        except FileNotFoundError:
            logger.error("FFmpeg not found. Install FFmpeg: https://ffmpeg.org/download.html")
            raise

    def get_segment_audio(self, segment_path: str) -> str:
        fd, output_path = tempfile.mkstemp(suffix=".wav", prefix="seg_audio_")
        os.close(fd)
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            segment_path,
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            output_path,
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=FFMPEG_TIMEOUT, check=False
            )
            if result.returncode != 0:
                logger.error("Segment audio extraction failed: %s", result.stderr)
                raise RuntimeError(result.stderr)
            return output_path
        except FileNotFoundError:
            logger.error("FFmpeg not found. Install FFmpeg: https://ffmpeg.org/download.html")
            raise
