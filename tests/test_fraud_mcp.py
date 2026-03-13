import pytest
import json
from httpx import AsyncClient, ASGITransport
from mcp_servers.fraud_mcp import app

@pytest.mark.asyncio
async def test_check_payee_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/check_payee", json={"payee_name": "Acme Corp"})
    assert response.status_code == 200
    assert response.json()["payee_name"] == "Acme Corp"
    assert "risk_score" in response.json()

@pytest.mark.asyncio
async def test_check_payee_deterministic():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp1 = await ac.post("/tools/check_payee", json={"payee_name": "Test Payee"})
        resp2 = await ac.post("/tools/check_payee", json={"payee_name": "Test Payee"})
    assert resp1.json()["risk_score"] == resp2.json()["risk_score"]

@pytest.mark.asyncio
async def test_check_payee_unknown():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/check_payee", json={"payee_name": "Payee UNKNOWN"})
    assert response.status_code == 404
    assert "payee_unknown" in response.json()["detail"]

@pytest.mark.asyncio
async def test_check_payee_model_error():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/check_payee", json={"payee_name": "MODEL_ERROR_TRIGGER"})
    assert response.status_code == 500
    assert "model_error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_fraud_alerts_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_fraud_alerts")
    assert response.status_code == 200
    assert "alerts" in response.json()
    assert len(response.json()["alerts"]) > 0
