"""
Простой нагрузочный тест API (100–200 запросов) для демонстрации метрик в Grafana.

Запуск (после port-forward или через Ingress):
  python loadtest.py http://localhost:8000
"""

from __future__ import annotations

import asyncio
import sys

import httpx


async def main(base_url: str, n: int = 200, concurrency: int = 10) -> None:
    sem = asyncio.Semaphore(concurrency)

    async def one(client: httpx.AsyncClient, i: int) -> None:
        async with sem:
            await client.get(f"{base_url.rstrip('/')}/healthz")
            await client.get(f"{base_url.rstrip('/')}/sites")

    async with httpx.AsyncClient(timeout=30.0) as client:
        await asyncio.gather(*[one(client, i) for i in range(n)])
    print(f"Done {n} iterations (healthz + /sites each)")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    asyncio.run(main(url))
