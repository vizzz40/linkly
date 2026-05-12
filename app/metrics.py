import time

from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)
REDIRECTS = Counter("redirects_total", "Total short-link redirects served")


def _normalize_path(raw_path: str) -> str:
    if raw_path.startswith("/api/stats/"):
        return "/api/stats/{code}"
    if raw_path in ("/", "/healthz", "/readyz", "/metrics") or raw_path.startswith("/api/"):
        return raw_path
    return "/{code}"


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start

        path = _normalize_path(request.url.path)
        REQUEST_COUNT.labels(request.method, path, response.status_code).inc()
        REQUEST_LATENCY.labels(request.method, path).observe(elapsed)
        return response
