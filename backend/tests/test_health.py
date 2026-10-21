from httpx import AsyncClient


async def test_health_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["env"] == "test"
    assert body["version"]
    assert "timestamp" in body


async def test_docs_available_outside_prod(client: AsyncClient) -> None:
    response = await client.get("/api/docs")
    assert response.status_code == 200
