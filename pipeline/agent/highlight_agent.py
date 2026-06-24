"""LangGraph highlight summary agent."""

import logging

from pipeline.kafka.schemas import FusedEvent

logger = logging.getLogger(__name__)


class HighlightAgent:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def generate_summary(self, events: list[FusedEvent]) -> str:
        if not events:
            return "No highlights to summarize."

        types = [e.event_type for e in events]
        summary = f"Match highlights: {len(events)} key moments including "
        summary += ", ".join(sorted(set(types)))
        summary += "."

        if self.api_key:
            try:
                from openai import AsyncOpenAI

                client = AsyncOpenAI(api_key=self.api_key)
                prompt = f"Summarize these match events in 2 sentences: {types}"
                resp = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                )
                return resp.choices[0].message.content or summary
            except Exception as exc:
                logger.warning("Highlight summary LLM failed: %s", exc)

        return summary
