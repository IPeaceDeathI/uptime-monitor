import asyncio
import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.config import settings
from app.db import init_db
from app.listener import redis_listener
from app.metrics import PrometheusMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    stop = asyncio.Event()
    task = asyncio.create_task(redis_listener(stop))
    yield
    stop.set()
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task


app = FastAPI(title="uptime-notifier", lifespan=lifespan)
app.add_middleware(PrometheusMiddleware)


@app.get("/healthz")
async def healthz() -> dict[str, str | bool]:
    return {"status": "ok", "telegram_configured": bool(settings.telegram_bot_token)}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
