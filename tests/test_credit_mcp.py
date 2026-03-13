import pytest
import json
from httpx import AsyncClient, ASGITransport
from mcp_servers.credit_mcp import app

@pytest.mark.asyncio
async def test_get_credit_score_success():
    with open("data/seed/mcp/credit.json", "r") as f:
        data = json.load(f)
    customer_id = data["credit_scores"][0]["customer_id"]
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_credit_score", json={"customer_id": customer_id})
    assert response.status_code == 200
    assert response.json()["customer_id"] == customer_id
    assert "score" in response.json()

@pytest.mark.asyncio
async def test_get_credit_score_insufficient_data():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_credit_score", json={"customer_id": "non_existent_id"})
    assert response.status_code == 404
    assert "insufficient_data" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_credit_score_bureau_error():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_credit_score", json={"customer_id": "bureau_error_id"})
    assert response.status_code == 503
    assert "bureau_error" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_loan_details_success():
    with open("data/seed/mcp/credit.json", "r") as f:
        data = json.load(f)
    loan_id = data["loans"][0]["loan_id"]
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_loan_details", json={"loan_id": loan_id})
    assert response.status_code == 200
    assert response.json()["loan_id"] == loan_id

@pytest.mark.asyncio
async def test_get_loan_details_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_loan_details", json={"loan_id": "MISSING_LOAN"})
    assert response.status_code == 404
    assert "loan_not_found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_customer_loans_success():
    with open("data/seed/mcp/credit.json", "r") as f:
        data = json.load(f)
    customer_id = data["loans"][0]["customer_id"]
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tools/get_customer_loans", json={"customer_id": customer_id})
    assert response.status_code == 200
    assert len(response.json()["loans"]) > 0
