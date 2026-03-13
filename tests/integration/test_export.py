import pytest
import httpx
import json
import uuid

BASE_URL = "http://localhost:8080"
CUSTOMER_ID = "cc3bfa78"

@pytest.mark.asyncio
async def test_audit_export_jsonl():
    """
    Verifies that the /audit/export endpoint returns valid JSONL.
    """
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        # 1. Run a query to ensure there is data
        session_id = str(uuid.uuid4())
        await client.post("/query", json={
            "session_id": session_id,
            "query": "Show my account summary",
            "customer_id": CUSTOMER_ID
        })
        
        # 2. Call /audit/export
        response = await client.get("/audit/export")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/x-jsonlines"
        
        # 3. Validate content
        lines = response.text.strip().split("\n")
        assert len(lines) > 0, "Export should not be empty"
        
        for line in lines:
            try:
                data = json.loads(line)
                assert "session_id" in data
                assert "event_type" in data
                assert "timestamp" in data
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON line: {line}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_audit_export_jsonl())
