import pytest
from httpx import AsyncClient, ASGITransport
from mcp_servers.core_banking_mcp import app

@pytest.mark.asyncio
async def test_get_customer_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_customer", json={"customer_id": "cc3bfa78"})
    assert response.status_code == 200
    assert response.json()["customer_id"] == "cc3bfa78"
    assert "name" in response.json()

@pytest.mark.asyncio
async def test_get_customer_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_customer", json={"customer_id": "missing_id"})
    assert response.status_code == 404
    assert "customer_not_found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_balance_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_balance", json={"account_id": "ACC102559"})
    assert response.status_code == 200
    assert response.json()["account_id"] == "ACC102559"
    assert "balance" in response.json()

@pytest.mark.asyncio
async def test_get_balance_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_balance", json={"account_id": "MISSING_ACC"})
    assert response.status_code == 404
    assert "account_not_found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_list_transactions_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/list_transactions", json={"account_id": "ACC102559", "limit": 5})
    assert response.status_code == 200
    assert response.json()["account_id"] == "ACC102559"
    assert len(response.json()["transactions"]) <= 5

@pytest.mark.asyncio
async def test_list_transactions_limit_exceeded():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/list_transactions", json={"account_id": "ACC102559", "limit": 105})
    assert response.status_code == 400
    assert "limit_exceeded" in response.json()["detail"]
