"""SportsCast AI Dashboard — FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dashboard.backend.app.api import events, highlights, matches, metrics, review, ws
from dashboard.backend.app.config import settings
from dashboard.backend.app.database import init_db

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Database initialized")
    yield


app = FastAPI(title="SportsCast AI Dashboard", version="0.1.0", lifespan=lifespan)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(matches.router)
app.include_router(review.router)
app.include_router(highlights.router)
app.include_router(metrics.router)
app.include_router(ws.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sportscast-ai-dashboard"}
