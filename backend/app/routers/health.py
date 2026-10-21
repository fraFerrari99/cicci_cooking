from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import Env, Settings, get_settings

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str
    env: Env
    timestamp: datetime


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Stato del servizio",
    description="Risponde 200 se l'API è viva. Usato da Docker healthcheck e monitoraggio.",
)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        env=settings.ENV,
        timestamp=datetime.now(UTC),
    )
