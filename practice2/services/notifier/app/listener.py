from __future__ import annotations

import asyncio
import json
import logging

import httpx
import redis.asyncio as redis
from sqlalchemy import or_, select

from app.config import settings
from app.db import SessionLocal
from app.metrics import NOTIFICATIONS_SENT_TOTAL
from app.models import Subscriber

log = logging.getLogger("notifier")


async def _fetch_chat_ids(site_id: int) -> list[str]:
    async with SessionLocal() as session:
        q = select(Subscriber.telegram_chat_id).where(
            or_(Subscriber.site_id == site_id, Subscriber.site_id.is_(None))
        )
        res = await session.execute(q)
        rows = [r[0] for r in res.all()]
    # уникальные chat_id
    return list(dict.fromkeys(rows))


async def _send_telegram(client: httpx.AsyncClient, chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        resp = await client.post(
            url,
            json={"chat_id": chat_id, "text": text},
            timeout=15.0,
        )
        ok = resp.status_code == 200
        NOTIFICATIONS_SENT_TOTAL.labels("telegram", "ok" if ok else "fail").inc()
        return ok
    except Exception as exc:  # noqa: BLE001
        log.warning("telegram send failed: %s", exc)
        NOTIFICATIONS_SENT_TOTAL.labels("telegram", "fail").inc()
        return False


async def redis_listener(stop: asyncio.Event) -> None:
    r = redis.from_url(settings.redis_url, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe(settings.redis_channel)
    async with httpx.AsyncClient() as client:
        while not stop.is_set():
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if msg is None:
                continue
            if msg.get("type") != "message":
                continue
            try:
                data = json.loads(msg["data"])
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
            site_id = int(data["site_id"])
            url = str(data.get("url", ""))
            was_up = bool(data.get("was_up"))
            is_up = bool(data.get("is_up"))
            latency = data.get("latency_ms")
            text = (
                f"Uptime alert\nURL: {url}\nStatus: {'UP' if was_up else 'DOWN'} → "
                f"{'UP' if is_up else 'DOWN'}\nLatency ms: {latency}"
            )
            for chat_id in await _fetch_chat_ids(site_id):
                await _send_telegram(client, chat_id, text)
