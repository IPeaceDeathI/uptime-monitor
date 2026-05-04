import time
from typing import Callable

from prometheus_client import Counter, Histogram, CollectorRegistry
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

registry = CollectorRegistry()

REQUESTS = Counter(
    "http_requests_total",
    "HTTP requests",
    ["method", "endpoint", "status"],
    registry=registry,
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
    registry=registry,
)


def _endpoint_label(request: Request) -> str:
    route = request.scope.get("route")
    if route and getattr(route, "path", None):
        return route.path
    return request.url.path


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path == "/metrics":
            return await call_next(request)
        ep = _endpoint_label(request)
        start = time.perf_counter()
        response = await call_next(request)
        REQUESTS.labels(request.method, ep, str(response.status_code)).inc()
        REQUEST_DURATION.labels(ep).observe(time.perf_counter() - start)
        return response
