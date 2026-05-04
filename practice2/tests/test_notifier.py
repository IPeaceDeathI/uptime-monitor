"""Тест отправки уведомления в Telegram (AsyncClient.post замокан)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest

_ROOT = Path(__file__).resolve().parents[1]
_NTF = _ROOT / "services" / "notifier"
# В тестовом прогоне уже может быть загружен другой пакет `app`.
# Сбрасываем его, чтобы импортировать `app` именно из notifier.
for _mod in list(sys.modules):
    if _mod == "app" or _mod.startswith("app."):
        del sys.modules[_mod]
sys.path.insert(0, str(_NTF))
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["TELEGRAM_BOT_TOKEN"] = "TESTTOKEN_12345"


from app.listener import _send_telegram  # noqa: E402


@pytest.mark.asyncio
async def test_send_telegram_called() -> None:
    mock_post = AsyncMock(return_value=httpx.Response(200, json={"ok": True}))
    with patch.object(httpx.AsyncClient, "post", mock_post):
        async with httpx.AsyncClient() as client:
            ok = await _send_telegram(client, "12345", "hello")

    assert ok is True
    mock_post.assert_awaited()
