"""Kafka producer with graceful degradation."""

import asyncio
import json
import logging
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SportsCastProducer:
    def __init__(self, bootstrap_servers: str):
        self.available = False
        self._producer = None
        self._memory_queue: list[tuple[str, dict[str, Any]]] = []

        try:
            from confluent_kafka import Producer

            self._producer = Producer({"bootstrap.servers": bootstrap_servers})
            self.available = True
        except Exception as exc:
            logger.warning("Kafka producer unavailable, using in-memory queue: %s", exc)

    async def produce(self, topic: str, event: BaseModel) -> bool:
        try:
            payload = event.model_dump(mode="json")
            key = getattr(event, "event_id", None) or payload.get("review_id", "")

            if not self.available or self._producer is None:
                self._memory_queue.append((topic, payload))
                return True

            loop = asyncio.get_event_loop()

            def _delivery(err, msg):
                if err:
                    logger.warning("Kafka delivery failed: %s", err)

            await loop.run_in_executor(
                None,
                lambda: self._producer.produce(
                    topic,
                    key=str(key),
                    value=json.dumps(payload),
                    callback=_delivery,
                ),
            )
            self._producer.poll(0)
            return True
        except Exception as exc:
            logger.warning("Kafka produce error: %s", exc)
            self._memory_queue.append((topic, event.model_dump(mode="json")))
            return False

    def drain_memory_queue(self) -> list[tuple[str, dict]]:
        items = list(self._memory_queue)
        self._memory_queue.clear()
        return items
