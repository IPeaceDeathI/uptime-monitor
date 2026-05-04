"""Тест воркера проверки: запись результата и публикация при смене статуса."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import httpx
import pytest
from sqlalchemy import select

_ROOT = Path(__file__).resolve().parents[1]
_CHK = _ROOT / "services" / "checker-worker"
# В тестовом прогоне уже может быть загружен другой пакет `app`
# (например, из api-gateway). Сбрасываем его, чтобы импортировать
# правильный `app` из checker-worker.
for _mod in list(sys.modules):
    if _mod == "app" or _mod.startswith("app."):
        del sys.modules[_mod]
sys.path.insert(0, str(_CHK))
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

from app.db import SessionLocal, init_db  # noqa: E402
from app.models import CheckResult, Site  # noqa: E402
from app.worker import check_one_site  # noqa: E402


@pytest.fixture(autouse=True)
async def _setup() -> None:
    await init_db()
    yield


@pytest.mark.asyncio
async def test_checker_writes_result_and_publishes_on_flip() -> None:
    async with SessionLocal() as session:
        site = Site(url="https://mock.test/", name="m", interval_sec=5)
        session.add(site)
        await session.commit()
        await session.refresh(site)
        prev = CheckResult(
            site_id=site.id,
            status_code=500,
            latency_ms=10,
            is_up=False,
        )
        session.add(prev)
        await session.commit()

    transport = httpx.MockTransport(lambda request: httpx.Response(200))
    rcli = AsyncMock()
    rcli.publish = AsyncMock(return_value=1)

    async with SessionLocal() as session:
        site2 = await session.get(Site, site.id)
        assert site2 is not None
        async with httpx.AsyncClient(transport=transport) as client:
            await check_one_site(session, rcli, client, site2)

    async with SessionLocal() as session:
        res = await session.execute(select(CheckResult).where(CheckResult.site_id == site.id))
        rows = list(res.scalars().all())
        assert len(rows) == 2
        assert rows[-1].is_up is True

    rcli.publish.assert_awaited()
