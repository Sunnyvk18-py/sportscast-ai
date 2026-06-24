"""Kafka consumer with graceful degradation."""

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)


class SportsCastConsumer:
    def __init__(self, bootstrap_servers: str, topics: list[str], group_id: str):
        self.topics = topics
        self.group_id = group_id
        self.available = False
        self._consumer = None
        self._producer_memory: list[tuple[str, dict]] = []

        try:
            from confluent_kafka import Consumer

            self._consumer = Consumer(
                {
                    "bootstrap.servers": bootstrap_servers,
                    "group.id": group_id,
                    "auto.offset.reset": "earliest",
                }
            )
            self._consumer.subscribe(topics)
            self.available = True
        except Exception as exc:
            logger.warning("Kafka consumer unavailable, using mock events: %s", exc)

    async def consume(
        self,
        callback: Callable[[str, dict], Awaitable[None]],
        stop_event: asyncio.Event,
    ) -> None:
        if not self.available or self._consumer is None:
            await self._mock_consume(callback, stop_event)
            return

        loop = asyncio.get_event_loop()
        while not stop_event.is_set():
            try:
                msg = await loop.run_in_executor(None, self._consumer.poll, 1.0)
                if msg is None:
                    await asyncio.sleep(0.1)
                    continue
                if msg.error():
                    logger.warning("Kafka consumer error: %s", msg.error())
                    continue
                topic = msg.topic()
                data = json.loads(msg.value().decode("utf-8"))
                await callback(topic, data)
            except Exception as exc:
                logger.warning("Kafka consume error: %s", exc)
                await asyncio.sleep(1)

        try:
            self._consumer.close()
        except Exception:
            pass

    async def _mock_consume(
        self,
        callback: Callable[[str, dict], Awaitable[None]],
        stop_event: asyncio.Event,
    ) -> None:
        logger.info("Running mock Kafka consumer (demo mode)")
        demo_count = 0
        while not stop_event.is_set():
            await asyncio.sleep(2)
            if stop_event.is_set():
                break
            demo_count += 1
            if demo_count > 5:
                continue
            await callback(
                "sportscast.fused",
                {
                    "type": "heartbeat",
                    "message": "mock consumer alive",
                },
            )
