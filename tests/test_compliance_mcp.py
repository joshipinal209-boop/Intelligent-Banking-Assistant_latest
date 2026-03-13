import pytest
import json
from httpx import AsyncClient, ASGITransport
from mcp_servers.compliance_mcp import app

@pytest.mark.asyncio
async def test_get_compliance_report_success():
    # Using a customer ID known to have reports in compliance.json
    customer_id = "dc43a761"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_compliance_report", json={"customer_id": customer_id})
    assert response.status_code == 200
    assert response.json()["customer_id"] == customer_id
    assert len(response.json()["reports"]) > 0

@pytest.mark.asyncio
async def test_get_rules_by_topic_rbi():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_rules_by_topic", json={"topic": "rbi_general"})
    assert response.status_code == 200
    assert response.json()["topic"] == "rbi_general"
    assert len(response.json()["rules"]) > 0
    assert any("KYC" in r["title"] or "AML" in r["title"] or "Regulation" in r["title"] for r in response.json()["rules"])

@pytest.mark.asyncio
async def test_get_rules_by_topic_invalid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_rules_by_topic", json={"topic": "invalid_topic"})
    assert response.status_code == 400
    assert "Invalid topic" in response.json()["detail"]
