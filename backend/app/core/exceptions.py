"""Handler globali degli errori.

Obiettivo: qualunque errore esca dall'API ha sempre la stessa forma
(`ErrorResponse`) e porta il `request_id`, così il frontend lo mostra e noi
lo ritroviamo nei log. Il 500 non espone mai dettagli interni al client.
"""

from http import HTTPStatus

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.middleware.request_id import REQUEST_ID_HEADER, get_request_id
from app.schemas.common import ErrorBody, ErrorResponse

log = structlog.get_logger(__name__)


def _error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: object = None,
) -> JSONResponse:
    request_id = get_request_id(request)
    body = ErrorResponse(
        error=ErrorBody(code=code, message=message, details=details, request_id=request_id)
    )
    # L'header lo mettiamo anche qui: il 500 passa dal ServerErrorMiddleware di Starlette,
    # che sta fuori dal nostro RequestIdMiddleware e quindi non lo attraversa in uscita.
    headers = {REQUEST_ID_HEADER: request_id} if request_id else None
    return JSONResponse(
        status_code=status_code, content=body.model_dump(exclude_none=True), headers=headers
    )


def _code_from_status(status_code: int) -> str:
    """404 -> "not_found", 401 -> "unauthorized", ecc."""
    try:
        return HTTPStatus(status_code).phrase.lower().replace(" ", "_")
    except ValueError:
        return "error"


async def _http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    message = exc.detail if isinstance(exc.detail, str) else HTTPStatus(exc.status_code).phrase
    details = None if isinstance(exc.detail, str) else exc.detail
    return _error_response(
        request, exc.status_code, _code_from_status(exc.status_code), message, details
    )


async def _validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    return _error_response(
        request,
        HTTPStatus.UNPROCESSABLE_ENTITY,
        "validation_error",
        "Richiesta non valida",
        details=exc.errors(),
    )


async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log.exception("unhandled_exception", path=request.url.path)
    return _error_response(
        request,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        "internal_error",
        "Errore interno. Riprova più tardi.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(RequestValidationError, _validation_exception_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)
