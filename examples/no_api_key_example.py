"""
SportsCast AI — No API Key Example
Runs the full mock pipeline end to end.
No FFmpeg needed, no Kafka needed, no API keys needed.

Run: python examples/no_api_key_example.py
"""

import asyncio

from pipeline.testing.mock_pipeline import MockPipeline


def format_ms(ms: int) -> str:
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    return f"{minutes:02d}:{seconds:02d}"


async def main():
    print("SportsCast AI — Mock Pipeline Demo")
    print("====================================")
    print("Simulating 60 seconds of match footage...\n")

    pipeline = MockPipeline(
        duration_seconds=60,
        events_to_simulate=[
            {"timestamp_ms": 8000, "type": "foul"},
            {"timestamp_ms": 23000, "type": "corner"},
            {"timestamp_ms": 41000, "type": "goal"},
            {"timestamp_ms": 55000, "type": "yellow_card"},
        ],
    )

    async for event in pipeline.run():
        status = (
            "✅ AUTO-CONFIRMED"
            if event.auto_confirmed
            else "⚠️  NEEDS REVIEW" if event.requires_review else "❌ DISCARDED"
        )

        print(
            f"[{format_ms(event.timestamp_ms)}] "
            f"{event.event_type.upper():12} | "
            f"Confidence: {event.composite_confidence:.0%} | "
            f"Signals: {event.signals_agreed}/3 | "
            f"{status}"
        )
        if event.commentary:
            print(f"  💬 {event.commentary}")
        print()

    print("\n✅ Mock pipeline complete. No API keys required.")
    print("Add OPENAI_API_KEY to .env to use real models.")


if __name__ == "__main__":
    asyncio.run(main())
