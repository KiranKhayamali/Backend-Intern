import uuid
import time
import structlog
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = structlog.get_logger(__name__)


class LoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        started_at = time.perf_counter()
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            client_host=request.client.host if request.client else None,
            path=request.url.path,
            method=request.method,
        )
        response = await call_next(request)
        structlog.contextvars.bind_contextvars(status_code=response.status_code)
        logger.info(
            "http_request_completed",
            status_code=response.status_code,
            duration_ms=round((time.perf_counter() - started_at) * 1000, 2),
        )
        response.headers["X-Request-ID"] = request_id
        return response
