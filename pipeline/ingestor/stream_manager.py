"""Manages HLS segment queue."""

import asyncio
import logging
from collections import deque

logger = logging.getLogger(__name__)


class StreamManager:
    def __init__(self, max_queue_size: int = 50):
        self._queue: deque[str] = deque(maxlen=max_queue_size)
        self._lock = asyncio.Lock()
        self._event = asyncio.Event()

    async def push(self, segment_path: str) -> None:
        async with self._lock:
            self._queue.append(segment_path)
            self._event.set()

    async def pop(self) -> str | None:
        async with self._lock:
            if self._queue:
                return self._queue.popleft()
            self._event.clear()
            return None

    async def wait_for_segment(self, timeout: float = 30.0) -> str | None:
        try:
            await asyncio.wait_for(self._event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
        return await self.pop()

    def size(self) -> int:
        return len(self._queue)
