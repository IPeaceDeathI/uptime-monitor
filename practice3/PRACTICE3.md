# Практика №3 — Деплой в Kubernetes (Minikube)

## Список микросервисов и образов

| Сервис | Docker-образ (тег) | Порт |
|--------|-------------------|------|
| api-gateway | `api-gateway:0.1` | 8000 |
| checker-worker | `checker-worker:0.1` | 8001 |
| notifier | `notifier:0.1` | 8002 |
| PostgreSQL | `postgres:16-alpine` | 5432 |
| Redis | `redis:7-alpine` | 6379 |

## Подготовка образов (Minikube Docker)

```powershell
minikube start --driver=docker --memory 4096
minikube addons enable ingress
minikube -p minikube docker-env | Invoke-Expression

docker build -t api-gateway:0.1 practice2/services/api-gateway
docker build -t checker-worker:0.1 practice2/services/checker-worker
docker build -t notifier:0.1 practice2/services/notifier
```

> На Linux/macOS используйте `eval $(minikube docker-env)` вместо `Invoke-Expression`.

## Применение манифестов

1. Экспортируйте токен в переменную окружения `TELEGRAM_BOT_TOKEN`.
2. Примените секрет с подстановкой переменной:

```powershell
$env:TELEGRAM_BOT_TOKEN="<ваш_токен>"
kubectl create secret generic uptime-secrets `
  --namespace uptime-monitor `
  --from-literal=postgres-password=uptime `
  --from-literal=telegram-bot-token=$env:TELEGRAM_BOT_TOKEN `
  --from-literal=database-url="postgresql+asyncpg://uptime:uptime@postgres:5432/uptime" `
  --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f practice3/k8s/
```

Для Linux/macOS:

```bash
export TELEGRAM_BOT_TOKEN="<ваш_токен>"
envsubst < practice3/k8s/secret.yaml | kubectl apply -f -
kubectl apply -f practice3/k8s/
```

3. В отдельном терминале (для Ingress на Docker-драйвере):

```bash
minikube tunnel
```

4. Добавьте в `C:\Windows\System32\drivers\etc\hosts` (от администратора):

```
127.0.0.1 uptime.local
```

(либо IP из `minikube ip`, если tunnel не используется — см. документацию Minikube для вашего драйвера).

## Проверка

```bash
kubectl get pods,svc,ingress -n uptime-monitor
curl http://uptime.local/healthz
curl http://uptime.local/sites
```

## Скриншоты для отчёта (вставьте вручную)

- `kubectl get pods,svc,ingress -n uptime-monitor`
- Успешный `curl` через Ingress
- `kubectl logs deploy/checker-worker -n uptime-monitor`

## Дополнительно реализовано

- **PostgreSQL в StatefulSet + PVC** — персистентное хранилище для данных мониторинга.
- Секреты (`database-url`, `postgres-password`, `telegram-bot-token`) вынесены в `Secret`, остальное — в `ConfigMap`.
