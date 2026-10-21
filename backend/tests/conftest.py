from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, get_settings
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    get_settings.cache_clear()
    return Settings(ENV="test", CORS_ORIGINS=["http://testserver"], _env_file=None)


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    application = create_app(settings)
    # L'endpoint health risolve Settings via Depends(get_settings): allineiamolo.
    application.dependency_overrides[get_settings] = lambda: settings
    return application


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    # raise_app_exceptions=False: vogliamo vedere la risposta 500 prodotta dal nostro
    # handler, non l'eccezione ri-sollevata dal test client.
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
