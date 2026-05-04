from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.config import settings
from app.db import init_db
from app.metrics import PrometheusMiddleware
from app.routers import sites, subscribers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(PrometheusMiddleware)
app.include_router(sites.router)
app.include_router(subscribers.router)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    data = generate_latest()
    return Response(data, media_type=CONTENT_TYPE_LATEST)
