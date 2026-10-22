"""Middleware request id + access log.

Per ogni richiesta HTTP:
1. legge l'header `X-Request-ID` se il client lo manda, altrimenti ne genera uno;
2. lo mette nel contesto di structlog, così ogni log scritto durante la richiesta lo include;
3. lo restituisce nell'header della risposta;
4. scrive una riga di log con metodo, path, status e durata.

È un middleware ASGI "puro" (non `BaseHTTPMiddleware`): più leggero e senza
problemi con risposte in streaming.
"""

import time
import uuid

import structlog
from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = "x-request-id"
_STATE_KEY = "request_id"

log = structlog.get_logger("app.access")


def get_request_id(request: Request) -> str | None:
    value = request.scope.get("state", {}).get(_STATE_KEY)
    return value if isinstance(value, str) else None


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = MutableHeaders(scope=scope)
        request_id = headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        scope.setdefault("state", {})[_STATE_KEY] = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.perf_counter()
        status_code = 500

        async def send_with_header(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = MutableHeaders(scope=message)
                if REQUEST_ID_HEADER not in response_headers:
                    response_headers.append(REQUEST_ID_HEADER, request_id)
            await send(message)

        try:
            await self.app(scope, receive, send_with_header)
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            log.info(
                "request",
                method=scope["method"],
                path=scope["path"],
                status=status_code,
                duration_ms=duration_ms,
            )
            structlog.contextvars.clear_contextvars()
