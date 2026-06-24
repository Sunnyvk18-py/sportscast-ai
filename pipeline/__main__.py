"""SportsCast AI CLI — pass a stream or video URL to run the real pipeline."""

import asyncio

from pipeline.cli import run_cli

if __name__ == "__main__":
    asyncio.run(run_cli())
