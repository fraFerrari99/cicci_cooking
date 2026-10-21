from fastapi import APIRouter

from app.routers import health

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(health.router)
