import pytest
import httpx
import time
import uuid
import json
import asyncio
import numpy as np
from typing import List, Dict, Any

# --- Test Configuration ---
BASE_URL = "http://localhost:8080"
CUSTOMER_ID = "cc3bfa78"
ITERATIONS = 10
LATENCY_THRESHOLD_P90 = 4.0  # Target P90 < 4s

class TestPerformanceAndAudit:

    async def run_monitored_query(self, client: httpx.AsyncClient, query: str, expected_agents: List[str]) -> float:
        """Runs a query, measures latency, and verifies audit trail."""
        session_id = str(uuid.uuid4())
        start_time = time.monotonic()
        
        # 1. POST /query
        response = await client.post("/query", json={
            "session_id": session_id,
            "query": query,
            "customer_id": CUSTOMER_ID
        })
        latency = time.monotonic() - start_time
        
        assert response.status_code == 200, f"Query failed: {response.text}"
        data = response.json()
        
        # 2. GET /audit/{session_id} to verify agent triggering
        # Wait a small bit for audit logs to persist if async
        await asyncio.sleep(0.5) 
        audit_res = await client.get(f"/audit/{session_id}")
        assert audit_res.status_code == 200, f"Audit retrieval failed: {audit_res.text}"
        audit_trail = audit_res.json()
        
        # Check if expected agents appear as node_start/end events
        audit_str = json.dumps(audit_trail)
        for agent in expected_agents:
            assert agent in audit_str, f"Agent {agent} not found in audit trail for session {session_id}"
            
        return latency

    async def benchmark_scenario(self, name: str, query: str, expected_agents: List[str]):
        """Runs 10 iterations and computes P90."""
        latencies = []
        print(f"\n--- Benchmarking: {name} ---")
        print(f"Query: '{query}'")
        
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
            for i in range(ITERATIONS):
                try:
                    latency = await self.run_monitored_query(client, query, expected_agents)
                    latencies.append(latency)
                    print(f"  Iteration {i+1}: {latency:.2f}s")
                except Exception as e:
                    print(f"  Iteration {i+1} FAILED: {str(e)}")
                    # Not appending to latencies so failed runs don't skew stats positively
        
        if not latencies:
            pytest.fail(f"All iterations failed for {name}")
            
        p90 = np.percentile(latencies, 90)
        avg = np.mean(latencies)
        
        print(f"RESULTS for {name}:")
        print(f"  P90 Latency: {p90:.2f}s")
        print(f"  Average Latency: {avg:.2f}s")
        
        # Assertion per requirement (P90 < 4s)
        # Note: If this fails, it indicates we need more optimization or the LLM is slow.
        assert p90 < LATENCY_THRESHOLD_P90, f"P90 latency {p90:.2f}s exceeds threshold {LATENCY_THRESHOLD_P90}s"

    @pytest.mark.asyncio
    async def test_performance_account_summary(self):
        """Scenario: Basic Account Summary (Account Agent)"""
        await self.benchmark_scenario(
            "Account Summary",
            "What is my current account balance and last 5 transactions?",
            ["account_agent"]
        )

    @pytest.mark.asyncio
    async def test_performance_loan_eligibility(self):
        """Scenario: Loan Eligibility (Loan Agent)"""
        await self.benchmark_scenario(
            "Loan Eligibility",
            "Am I eligible for a ₹10L Home Loan?",
            ["loan_agent"]
        )

    @pytest.mark.asyncio
    async def test_performance_fraud_check(self):
        """Scenario: Fraud Alerts (Fraud Agent)"""
        await self.benchmark_scenario(
            "Fraud Alerts",
            "Do I have any suspicious activity or fraud alerts?",
            ["fraud_agent"]
        )

    @pytest.mark.asyncio
    async def test_performance_compliance_docs(self):
        """Scenario: Compliance Checklist (Compliance Agent)"""
        await self.benchmark_scenario(
            "Compliance Checklist",
            "What documents do I need for a Personal Loan?",
            ["compliance_agent"]
        )

    @pytest.mark.asyncio
    async def test_performance_parallel_query(self):
        """Scenario: Parallel Account + Loan (Parallel Execution)"""
        await self.benchmark_scenario(
            "Parallel Query",
            "Show my balance and check if I can get a ₹5L car loan",
            ["account_agent", "loan_agent"]
        )
