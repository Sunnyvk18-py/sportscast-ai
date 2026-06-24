"""CLI entry point for stream/video processing."""

import argparse
import logging

from pipeline.cli_output import print_event
from pipeline.config import settings
from pipeline.runner import SportsCastPipeline

logger = logging.getLogger(__name__)


async def run_cli(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="SportsCast AI — process a live stream or video URL"
    )
    parser.add_argument("--url", required=True, help="YouTube, stream, or video file URL/path")
    parser.add_argument(
        "--no-dashboard", action="store_true", help="Do not POST events to dashboard API"
    )
    parser.add_argument("--no-clips", action="store_true", help="Skip highlight clip generation")
    parser.add_argument("--name", default="Live Match", help="Match name for dashboard")
    args = parser.parse_args(argv)

    logging.basicConfig(level=settings.LOG_LEVEL)

    logger.info("Analyzing %s", args.url)
    pipeline = SportsCastPipeline(
        source_url=args.url,
        match_name=args.name,
        post_to_dashboard=not args.no_dashboard,
        generate_clips=not args.no_clips,
    )

    async for event in pipeline.run():
        print_event(event)

    print("Pipeline complete. Open http://localhost:3000 for the dashboard.")
