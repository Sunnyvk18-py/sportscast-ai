"""WebSocket live event stream."""

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from pipeline.kafka.schemas import FusedEvent

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])

_connections: set[WebSocket] = set()


async def broadcast_event(event: FusedEvent) -> None:
    message = {"type": "new_event", "data": event.model_dump(mode="json")}
    dead: list[WebSocket] = []
    for ws in _connections:
        try:
            await ws.send_json(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connections.discard(ws)


@router.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    await websocket.accept()
    _connections.add(websocket)
    try:
        heartbeat_task = asyncio.create_task(_heartbeat(websocket))
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "pong":
                    continue
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        pass
    finally:
        _connections.discard(websocket)
        if "heartbeat_task" in dir():
            heartbeat_task.cancel()


async def _heartbeat(websocket: WebSocket) -> None:
    while websocket in _connections:
        try:
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})
        except Exception:
            break
