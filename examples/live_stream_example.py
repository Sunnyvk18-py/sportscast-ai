"""Live stream ingestion example."""

import argparse
import asyncio
import logging

from pipeline.config import settings
from pipeline.ingestor.stream_manager import StreamManager
from pipeline.ingestor.video_ingestor import VideoIngestor
from pipeline.testing.mock_pipeline import MockPipeline

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="SportsCast AI — Live Stream")
    parser.add_argument("--url", help="Live stream URL")
    parser.add_argument("--mock", action="store_true", help="Use mock pipeline")
    args = parser.parse_args()

    if args.mock or settings.USE_MOCK_PIPELINE or not args.url:
        logger.info("Running mock live stream simulation")
        pipeline = MockPipeline(
            duration_seconds=30,
            events_to_simulate=[
                {"timestamp_ms": 5000, "type": "foul"},
                {"timestamp_ms": 20000, "type": "goal"},
            ],
        )
        async for event in pipeline.run():
            print(f"[LIVE] {event.event_type}: {event.composite_confidence:.0%}")
        return

    manager = StreamManager()
    ingestor = VideoIngestor(args.url, settings.SEGMENTS_DIR)

    async def process_segments():
        video_path = ingestor.download_video()
        async for segment in ingestor.segment_to_hls(video_path):
            await manager.push(segment)
            logger.info("Queued segment: %s", segment)

    await process_segments()


if __name__ == "__main__":
    asyncio.run(main())
