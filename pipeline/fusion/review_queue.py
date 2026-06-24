"""Low-confidence human review queue."""

import asyncio
import logging
from datetime import datetime, timezone

from pipeline.kafka.schemas import ReviewItem

logger = logging.getLogger(__name__)


class ReviewQueue:
    def __init__(self):
        self._queue: asyncio.Queue[ReviewItem] = asyncio.Queue()
        self._items: dict[str, ReviewItem] = {}

    async def put(self, item: ReviewItem) -> None:
        self._items[item.review_id] = item
        await self._queue.put(item)

    async def get(self) -> ReviewItem:
        item = await self._queue.get()
        return item

    async def approve(self, review_id: str, notes: str = "") -> ReviewItem | None:
        item = self._items.get(review_id)
        if not item:
            logger.warning("Review item not found: %s", review_id)
            return None
        item.reviewer_decision = "approved"
        item.reviewer_notes = notes
        item.reviewed_at = datetime.now(timezone.utc)
        return item

    async def reject(self, review_id: str, notes: str = "") -> ReviewItem | None:
        item = self._items.get(review_id)
        if not item:
            logger.warning("Review item not found: %s", review_id)
            return None
        item.reviewer_decision = "rejected"
        item.reviewer_notes = notes
        item.reviewed_at = datetime.now(timezone.utc)
        return item

    def pending(self) -> list[ReviewItem]:
        return [item for item in self._items.values() if item.reviewer_decision is None]
