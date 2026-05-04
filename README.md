# Uptime Monitor — практический цикл 9–12 (вариант 9)

Микросервисная система **проверки доступности сайтов**: REST API для регистрации URL, фоновый воркер HTTP-проверок с записью в PostgreSQL, асинхронные уведомления в **Telegram** через **Redis Pub/Sub**, деплой в **Kubernetes (Minikube)** и мониторинг **Prometheus + Grafana**.

## Структура репозитория

| Практика | Содержимое |
|----------|------------|
| [practice1/](practice1/) | C4: Problem Statement, `*.puml`, PNG, отчёт |
| [practice2/](practice2/) | Код 3 микросервисов, `docker-compose.yml`, тесты, `PRACTICE2.md` |
| [practice3/](practice3/) | Kubernetes YAML, `PRACTICE3.md` |
| [practice4/](practice4/) | ServiceMonitor, values Helm, дашборд Grafana, `PRACTICE4.md` |

## Быстрый старт (локально)

```bash
cd practice2
docker compose up --build
```

- Swagger: http://localhost:8000/docs  
- Метрики API: http://localhost:8000/metrics  
- Метрики checker: http://localhost:8001/metrics  
- Метрики notifier: http://localhost:8002/metrics  

## Тесты

```bash
cd practice2
pip install -r services/api-gateway/requirements.txt -r tests/requirements.txt
pytest -v
```

## Ссылка на репозиторий

URL публичного репозитория GitHub: `https://github.com/IPeaceDeathI/uptime-monitor`

## Реализованные усложнения (+баллы)

- **3 микросервиса** (api-gateway, checker-worker, notifier) вместо минимальных двух.
- **Асинхронное взаимодействие** checker → notifier через **Redis Pub/Sub**.
- **Внешняя интеграция** с **Telegram Bot API**.
- **PostgreSQL в Kubernetes** как **StatefulSet + PVC**.
- **Мониторинг**: kube-prometheus-stack, **ServiceMonitor**, кастомные метрики `/metrics`, дашборд Grafana (JSON).

## Рефлексия: роль ИИ в разработке

ИИ сильно ускоряет создание «скелета» (FastAPI, SQLAlchemy, Docker/K8s YAML, тестовые заготовки) и снижает порог входа в Prometheus/Grafana. Наиболее полезен там, где много шаблонного кода и известные best practices; **менее надёжен** там, где нужны точные границы системы, корректные связи в архитектуре и нюансы конкретных библиотек (версии SQLAlchemy, asyncpg DSN, семантика Redis). Итоговое качество достигается **итерациями и ручной проверкой** (тесты, `docker compose`, `kubectl`).

Рынок ИТ, вероятно, сместится к большей продуктивности инженеров и к спросу на **постановку задач, ревью и эксплуатацию** сложных систем, а рутинный бойлерплейт будет автоматизироваться ассистентами.

## Отчёты по практикам

1. [practice1/README.md](practice1/README.md)  
2. [practice2/PRACTICE2.md](practice2/PRACTICE2.md)  
3. [practice3/PRACTICE3.md](practice3/PRACTICE3.md)  
4. [practice4/PRACTICE4.md](practice4/PRACTICE4.md)  
