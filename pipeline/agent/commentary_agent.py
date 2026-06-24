"""LangGraph play-by-play commentary agent."""

import logging
from typing import TypedDict

from pipeline.kafka.schemas import FusedEvent

logger = logging.getLogger(__name__)

COMMENTARY_TEMPLATES = {
    "goal": "GOAL! The striker finds the back of the net!",
    "foul": "Referee blows the whistle — that's a clear foul in midfield.",
    "corner": "Corner kick awarded, the winger races to place the ball.",
    "yellow_card": "Yellow card shown — the referee has made his decision.",
    "red_card": "Red card! The player is sent off!",
    "substitution": "Substitution made — fresh legs coming on.",
}


class CommentaryState(TypedDict):
    fused_event: FusedEvent
    match_context: list[str]
    raw_commentary: str
    formatted_commentary: str


class CommentaryAgent:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self._graph = None

    def _build_graph(self):
        try:
            from langgraph.graph import END, StateGraph

            graph = StateGraph(CommentaryState)

            async def event_analyzer(state: CommentaryState) -> CommentaryState:
                return state

            async def context_retriever(state: CommentaryState) -> CommentaryState:
                return state

            async def commentary_writer(state: CommentaryState) -> CommentaryState:
                event = state["fused_event"]
                context = "; ".join(state["match_context"][-5:])
                prompt = (
                    f"You are a professional sports commentator. Given this match event: "
                    f"{event.event_type} detected at {event.timestamp_ms}ms with "
                    f"{event.composite_confidence:.0%} confidence. "
                    f"Recent context: {context}. "
                    f"Generate ONE sentence of broadcast-quality play-by-play commentary. "
                    f"Be specific, energetic, and accurate. Maximum 30 words."
                )
                try:
                    if self.api_key:
                        from openai import AsyncOpenAI

                        client = AsyncOpenAI(api_key=self.api_key)
                        resp = await client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=80,
                        )
                        raw = resp.choices[0].message.content or ""
                    else:
                        raise ValueError("No API key")
                except Exception as exc:
                    logger.debug("LLM commentary fallback: %s", exc)
                    fallback = (
                        f"{event.event_type.title()} detected at "
                        f"{self._format_time(event.timestamp_ms)}!"
                    )
                    raw = COMMENTARY_TEMPLATES.get(event.event_type, fallback)
                state["raw_commentary"] = raw
                return state

            async def formatter(state: CommentaryState) -> CommentaryState:
                state["formatted_commentary"] = state["raw_commentary"].strip()
                return state

            graph.add_node("event_analyzer", event_analyzer)
            graph.add_node("context_retriever", context_retriever)
            graph.add_node("commentary_writer", commentary_writer)
            graph.add_node("formatter", formatter)
            graph.set_entry_point("event_analyzer")
            graph.add_edge("event_analyzer", "context_retriever")
            graph.add_edge("context_retriever", "commentary_writer")
            graph.add_edge("commentary_writer", "formatter")
            graph.add_edge("formatter", END)
            return graph.compile()
        except Exception as exc:
            logger.warning("LangGraph unavailable: %s", exc)
            return None

    async def generate(self, event: FusedEvent, match_history: list[str] | None = None) -> str:
        match_history = match_history or []
        if self._graph is None:
            self._graph = self._build_graph()

        if self._graph is not None:
            try:
                result = await self._graph.ainvoke(
                    {
                        "fused_event": event,
                        "match_context": match_history,
                        "raw_commentary": "",
                        "formatted_commentary": "",
                    }
                )
                return result["formatted_commentary"]
            except Exception as exc:
                logger.warning("Commentary graph failed: %s", exc)

        return self._template_fallback(event)

    def _template_fallback(self, event: FusedEvent) -> str:
        template = COMMENTARY_TEMPLATES.get(event.event_type)
        if template:
            return template
        return f"{event.event_type.title()} detected at {self._format_time(event.timestamp_ms)}!"

    @staticmethod
    def _format_time(timestamp_ms: int) -> str:
        minutes = timestamp_ms // 60000
        seconds = (timestamp_ms % 60000) // 1000
        return f"{minutes:02d}:{seconds:02d}"
