# Практика №4 — Мониторинг (Prometheus + Grafana)

## Выбор системы

Использован стек **Prometheus + Grafana** через Helm-чарт **kube-prometheus-stack**: де-факто стандарт CNCF, встроенные дашборды по кластеру, простое подключение `ServiceMonitor` для приложений.

## Установка (Minikube)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f practice4/monitoring/values.yaml
kubectl apply -f practice4/monitoring/servicemonitor.yaml
```

Доступ к Grafana (пример):

```bash
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
```

Логин по умолчанию часто `admin` / пароль из секрета:

```bash
kubectl -n monitoring get secret monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d
```

Импортируйте дашборд JSON: [monitoring/grafana-dashboard.json](monitoring/grafana-dashboard.json) (UI Grafana → Dashboards → Import).

> Если UID источника данных не `prometheus`, поменяйте поле `datasource.uid` в JSON на фактический UID вашего Prometheus в Grafana.

## Экспортируемые метрики приложения

| Метрика | Тип | Где собирается | Назначение |
|---------|-----|----------------|------------|
| `http_requests_total{method,endpoint,status}` | Counter | api-gateway, notifier | RPS и коды ответа по маршрутам |
| `http_request_duration_seconds_bucket` (+ `_sum/_count`) | Histogram | api-gateway, notifier | Латентность HTTP |
| `sites_registered_total` | Counter | api-gateway | Бизнес-счётчик регистрации целей мониторинга |
| `sites_checked_total{result}` | Counter | checker-worker | Количество успешных/ошибочных проверок |
| `site_up{site_id,url}` | Gauge | checker-worker | Текущее состояние доступности по каждому URL |
| `notifications_sent_total{channel,result}` | Counter | notifier | Попытки отправки в Telegram |

## Сбор метрик

Используется ресурс **ServiceMonitor** ([servicemonitor.yaml](monitoring/servicemonitor.yaml)):

- выбирает сервисы в `uptime-monitor` с лейблом `release: monitoring`;
- скрейпит порт с именем `http` по пути `/metrics` каждые 15 с.

Сервисы приложения уже содержат:

```yaml
metadata:
  labels:
    release: monitoring
spec:
  ports:
    - name: http
```

## Нагрузочный тест

```bash
pip install httpx
python practice4/monitoring/loadtest.py http://uptime.local
```

Ожидаемо растут `rate(http_requests_total[...])` и квантили `http_request_duration_seconds`.

## Скриншоты

См. каталог [screenshots/](screenshots/) — добавьте PNG с подписями панелей (минимум 3 файла).

## Выводы

Метрики HTTP и бизнес-счётчики позволяют отделить проблемы инфраструктуры (рост 5xx, рост latency) от логики мониторинга (частота `sites_checked_total` с меткой `error`, всплеск `notifications_sent_total`).
