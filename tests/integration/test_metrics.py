import pytest
import httpx
import asyncio
import uuid
import numpy as np

BASE_URL = "http://localhost:8080"
CUSTOMER_ID = "cc3bfa78"

@pytest.mark.asyncio
async def test_metrics_collection():
    """
    Verifies that metrics are collected and aggregated correctly.
    """
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        # 1. Run a few queries to generate profile data
        queries = [
            "What is my balance?",
            "Am I eligible for a loan?",
            "Any fraud alerts?"
        ]
        
        for q in queries:
            session_id = str(uuid.uuid4())
            res = await client.post("/query", json={
                "session_id": session_id,
                "query": q,
                "customer_id": CUSTOMER_ID
            })
            assert res.status_code == 200
            
        # 2. Call /metrics
        metrics_res = await client.get("/metrics")
        assert metrics_res.status_code == 200
        metrics = metrics_res.json()
        
        print("\n--- Captured Metrics ---")
        import json
        print(json.dumps(metrics, indent=2))
        
        # 3. Assertions
        assert "overall" in metrics
        assert "by_component" in metrics
        assert metrics["overall"]["count"] > 0
        
        # Check for specific component timings
        components = metrics["by_component"].keys()
        
        # We expect at least these event types: NODE_END, MCP_CALL (for some)
        has_nodes = any(c.startswith("NODE_END:") for c in components)
        has_tools = any(c.startswith("MCP_CALL:") or c.startswith("KG_QUERY:") for c in components)
        
        assert has_nodes, "No node metrics found"
        # Since we ran balance and loan, we definitely expect tool calls
        assert has_tools, "No tool/KG metrics found"
        
        # Verify p90 >= p50
        for comp, stats in metrics["by_component"].items():
            assert stats["p90"] >= stats["p50"], f"P90 < P50 for {comp}"

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_metrics_collection())
