# Практика №2 — MVP Uptime Monitor

## Ссылка на репозиторий

URL публичного репозитория GitHub: `https://github.com/IPeaceDeathI/uptime-monitor`

## Использованные ИИ-инструменты

- **Cursor Agent** — генерация каркаса FastAPI, SQLAlchemy-моделей, Dockerfile, docker-compose, Kubernetes-манифестов и тестов.
- (Опционально) **GigaChat / YandexGPT** — уточнение формулировок Problem Statement и промптов для C4.

## Примеры промптов, давших наиболее полезный результат

1. «Создай FastAPI-сервис с async SQLAlchemy 2.0: модели Site, CheckResult, Subscriber, эндпоинты POST/GET /sites, GET /sites/{id}/checks, middleware для Prometheus http_requests_total и histogram latency.»
2. «Напиши asyncio-воркер: каждые 10 с читает сайты из PostgreSQL, httpx GET, пишет CheckResult, при смене is_up публикует JSON в Redis Pub/Sub.»
3. «Сгенерируй pytest-asyncio тесты: ASGITransport для API, MockTransport httpx для checker, unittest.mock для Telegram sendMessage.»

## Оценка доли кода ИИ / вручную

- **~65–75%** сгенерировано ИИ (структура сервисов, boilerplate, YAML, тестовые шаблоны).
- **~25–35%** доработано вручную (согласование схемы БД между сервисами, порядок `last_run` в воркере, обработка `IntegrityError`, метки Prometheus, тексты отчётов).

## Ошибки и «галлюцинации» ИИ

| Проблема | Как исправлено |
|----------|----------------|
| ИИ предложил `on_event("startup")` (устаревший паттерн FastAPI) | Заменено на `lifespan` |
| Неверная строка подключения `postgres://` для asyncpg | Исправлено на `postgresql+asyncpg://` |
| Лишняя связь «API → Telegram напрямую» на диаграмме | Убрана на этапе C4 (практика 1) |
| Предложено хранить очередь задач в Redis List вместо Pub/Sub | Выбран Pub/Sub под события смены статуса |

## Скриншоты (вставьте в отчёт при сдаче)

1. Успешный прогон тестов: `cd practice2 && pip install -r services/api-gateway/requirements.txt -r tests/requirements.txt && pytest -v`
   <img width="1099" height="353" alt="image" src="https://github.com/user-attachments/assets/a6539e39-0b48-4101-896c-f7632b61ad56" />

3. Логи `docker compose up --build` с здоровыми сервисами `api-gateway`, `checker-worker`, `notifier`.
  <img width="1280" height="1001" alt="image" src="https://github.com/user-attachments/assets/23f0e424-adcc-49d0-9816-3d62a20b5a33" />


## Схема взаимодействия микросервисов

```mermaid
flowchart LR
  Client[Client] --> API[api-gateway]
  API --> PG[(PostgreSQL)]
  CHK[checker-worker] --> PG
  CHK --> RD[(Redis Pub/Sub)]
  NTF[notifier] --> RD
  NTF --> TG[Telegram API]
```

## Запуск локально

```bash
cd practice2
docker compose up --build
```

- API: http://localhost:8000/docs  
- Checker metrics: http://localhost:8001/metrics  
- Notifier metrics: http://localhost:8002/metrics
  <img width="1280" height="678" alt="image" src="https://github.com/user-attachments/assets/18f899eb-cbb2-4676-9076-77054113fbe7" />
  <img width="703" height="812" alt="image" src="https://github.com/user-attachments/assets/5869f7c9-88bf-46a5-87f1-8748bc0e4807" />
