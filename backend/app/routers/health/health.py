from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.routers.health.schemas import HealthResponse

router = APIRouter(tags=["System"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="State of the service",
    description="Responds with 200 if the API is alive. Used by Docker healthcheck and monitoring.",
)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        env=settings.ENV,
        timestamp=datetime.now(UTC),
    )
