from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone

import httpx
import redis.asyncio as redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import SessionLocal
from app.metrics import SITE_UP, SITES_CHECKED_TOTAL
from app.models import CheckResult, Site


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def _last_result(session: AsyncSession, site_id: int) -> CheckResult | None:
    q = (
        select(CheckResult)
        .where(CheckResult.site_id == site_id)
        .order_by(CheckResult.checked_at.desc())
        .limit(1)
    )
    res = await session.execute(q)
    return res.scalar_one_or_none()


async def check_one_site(
    session: AsyncSession,
    rcli: redis.Redis,
    client: httpx.AsyncClient,
    site: Site,
) -> None:
    is_up = False
    status_code: int | None = None
    latency_ms: int | None = None
    try:
        t0 = time.perf_counter()
        resp = await client.get(site.url, follow_redirects=True)
        latency_ms = int((time.perf_counter() - t0) * 1000)
        status_code = resp.status_code
        is_up = 200 <= resp.status_code < 400
        SITES_CHECKED_TOTAL.labels("up" if is_up else "down").inc()
    except Exception:  # noqa: BLE001
        SITES_CHECKED_TOTAL.labels("error").inc()
        is_up = False

    prev = await _last_result(session, site.id)
    row = CheckResult(
        site_id=site.id,
        status_code=status_code,
        latency_ms=latency_ms,
        is_up=is_up,
        checked_at=utcnow(),
    )
    session.add(row)
    await session.commit()

    SITE_UP.labels(str(site.id), site.url[:200]).set(1 if is_up else 0)

    if prev is not None and prev.is_up != is_up:
        payload = {
            "site_id": site.id,
            "url": site.url,
            "was_up": prev.is_up,
            "is_up": is_up,
            "latency_ms": latency_ms,
        }
        await rcli.publish(settings.redis_channel, json.dumps(payload))


async def worker_loop(stop: asyncio.Event) -> None:
    rcli = redis.from_url(settings.redis_url, decode_responses=True)
    last_run: dict[int, float] = {}
    async with httpx.AsyncClient(timeout=settings.http_timeout_sec) as client:
        while not stop.is_set():
            async with SessionLocal() as session:
                res = await session.execute(select(Site).order_by(Site.id))
                sites = list(res.scalars().all())
                now = time.time()
                for site in sites:
                    if now - last_run.get(site.id, 0) < site.interval_sec:
                        continue
                    await check_one_site(session, rcli, client, site)
                    last_run[site.id] = time.time()
            try:
                await asyncio.wait_for(stop.wait(), timeout=settings.poll_interval_sec)
            except TimeoutError:
                continue


async def run_worker(stop: asyncio.Event) -> None:
    await worker_loop(stop)
