from fastapi import FastAPI
from httpx import AsyncClient


async def test_request_id_generated(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    request_id = response.headers.get("x-request-id")
    assert request_id
    assert len(request_id) == 32  # uuid4().hex


async def test_request_id_propagated_from_client(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health", headers={"X-Request-ID": "abc-123"})
    assert response.headers["x-request-id"] == "abc-123"


async def test_404_has_error_shape(client: AsyncClient) -> None:
    response = await client.get("/api/v1/nope", headers={"X-Request-ID": "req-404"})

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert body["error"]["message"]
    assert body["error"]["request_id"] == "req-404"


async def test_422_has_error_shape(app: FastAPI, client: AsyncClient) -> None:
    @app.get("/api/v1/_echo")
    async def _echo(n: int) -> dict[str, int]:
        return {"n": n}

    response = await client.get("/api/v1/_echo", params={"n": "not-a-number"})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["details"]
    assert body["error"]["request_id"]


async def test_500_is_generic(app: FastAPI, client: AsyncClient) -> None:
    @app.get("/api/v1/_boom")
    async def _boom() -> None:
        raise RuntimeError("segreto interno")

    response = await client.get("/api/v1/_boom")

    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "internal_error"
    assert "segreto" not in response.text
    assert response.headers.get("x-request-id")
