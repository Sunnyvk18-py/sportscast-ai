"""Recorded match example — yt-dlp + real models."""

import argparse
import asyncio
import logging
import os

from pipeline.config import settings
from pipeline.ingestor.video_ingestor import VideoIngestor
from pipeline.testing.mock_pipeline import MockPipeline

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="SportsCast AI — Recorded Match")
    parser.add_argument("--url", required=True, help="YouTube or video URL")
    parser.add_argument("--mock", action="store_true", help="Use mock pipeline")
    args = parser.parse_args()

    os.makedirs(settings.SEGMENTS_DIR, exist_ok=True)

    if args.mock or settings.USE_MOCK_PIPELINE:
        logger.info("Running mock pipeline (no API keys)")
        pipeline = MockPipeline(
            duration_seconds=60,
            events_to_simulate=[
                {"timestamp_ms": 8000, "type": "foul"},
                {"timestamp_ms": 41000, "type": "goal"},
            ],
        )
        async for event in pipeline.run():
            print(f"{event.event_type}: {event.composite_confidence:.0%}")
        return

    ingestor = VideoIngestor(args.url, settings.SEGMENTS_DIR, settings.SEGMENT_DURATION)
    video_path = ingestor.download_video()
    logger.info("Downloaded: %s", video_path)

    async for segment in ingestor.segment_to_hls(video_path):
        logger.info("Segment ready: %s", segment)


if __name__ == "__main__":
    asyncio.run(main())
