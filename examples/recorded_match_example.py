"""Recorded match — full pipeline from YouTube or file URL."""

import argparse
import asyncio
import logging

from pipeline.cli_output import print_event
from pipeline.config import settings
from pipeline.runner import SportsCastPipeline

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="SportsCast AI — Recorded Match")
    parser.add_argument("--url", required=True, help="YouTube or video URL / local path")
    parser.add_argument("--no-dashboard", action="store_true", help="Skip dashboard POST")
    parser.add_argument("--no-clips", action="store_true", help="Skip clip generation")
    parser.add_argument("--name", default="Recorded Match", help="Match name")
    args = parser.parse_args()

    pipeline = SportsCastPipeline(
        source_url=args.url,
        match_name=args.name,
        post_to_dashboard=not args.no_dashboard,
        generate_clips=not args.no_clips,
    )
    async for event in pipeline.run():
        print_event(event)


if __name__ == "__main__":
    asyncio.run(main())
