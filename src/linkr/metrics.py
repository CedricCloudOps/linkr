import time

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

HTTP_REQUESTS = Counter(
    "linkr_http_requests_total",
    "HTTP requests processed",
    ["method", "path", "status"],
)
HTTP_LATENCY = Histogram(
    "linkr_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)
REDIRECTS = Counter("linkr_redirects_total", "Successful short-link redirects")
CACHE_HITS = Counter("linkr_cache_hits_total", "Redirect cache hits")
CACHE_MISSES = Counter("linkr_cache_misses_total", "Redirect cache misses")


def _route_template(request: Request) -> str:
    """Use the route template (not the raw path) to keep label cardinality bounded."""
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        path = _route_template(request)
        HTTP_LATENCY.labels(request.method, path).observe(time.perf_counter() - start)
        HTTP_REQUESTS.labels(request.method, path, response.status_code).inc()
        return response


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
