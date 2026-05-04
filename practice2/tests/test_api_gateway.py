"""Интеграционные тесты API Gateway (SQLite in-memory)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

_ROOT = Path(__file__).resolve().parents[1]
_API = _ROOT / "services" / "api-gateway"
sys.path.insert(0, str(_API))
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.db import init_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
async def _init_db() -> None:
    await init_db()
    yield


@pytest.mark.asyncio
async def test_api_create_and_get_site() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post(
            "/sites",
            json={"url": "https://example.com", "name": "Example", "interval_sec": 30},
        )
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["url"] == "https://example.com"
        rid = body["id"]

        r2 = await ac.get("/sites")
        assert r2.status_code == 200
        sites = r2.json()
        assert any(s["id"] == rid for s in sites)

        r3 = await ac.get(f"/sites/{rid}/checks")
        assert r3.status_code == 200
        assert r3.json() == []
