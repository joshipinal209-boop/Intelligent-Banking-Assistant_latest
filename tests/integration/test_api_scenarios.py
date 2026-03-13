import pytest
import httpx
import time
import uuid
import json
import asyncio
from typing import Dict, Any

# --- Test Configuration ---
BASE_URL = "http://localhost:8080"
CUSTOMER_ID = "cc3bfa78" # Consistent with seed data

# --- Multi-scenario test class to share logic ---

class TestBankingAssistant:
    
    @pytest.mark.asyncio
    async def run_scenario(self, query: str, customer_id: str = CUSTOMER_ID):
        session_id = str(uuid.uuid4())
        start_time = time.monotonic()
        
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
            response = await client.post("/query", json={
                "session_id": session_id,
                "query": query,
                "customer_id": customer_id
            })
        
        latency = time.monotonic() - start_time
        data = response.json() if response.status_code == 200 else {}
        if response.status_code != 200:
            print(f"FAILED: {response.text}")
        else:
            print(f"\nScenario Query: '{query}'")
            print(f"Latency: {latency:.2f}s | Status: {data['status']}")
            
        assert response.status_code == 200, f"Query failed for '{query}': {response.text}"
        return data, latency

    @pytest.mark.asyncio
    async def test_scenario_1_balance_and_last5(self):
        """Scenario 1: Balance and Last 5 Transactions"""
        data, latency = await self.run_scenario("What is my current account balance and last 5 transactions?")
        
        assert "account_agent" in data["agent_outputs"]
        output = data["agent_outputs"]["account_agent"]
        prov = output.get("provenance", [])
        assert any(p["name"] == "get_balance" for p in prov)
        assert any(p["name"] == "list_transactions" for p in prov)
        assert len(output["accounts"]) > 0
        assert "balance" in str(data["final_response"]).lower()

    @pytest.mark.asyncio
    async def test_scenario_2_loan_eligibility(self):
        """Scenario 2: Loan Eligibility"""
        data, latency = await self.run_scenario("Am I eligible for a ₹10L Home Loan?")
        
        assert "loan_agent" in data["agent_outputs"]
        output = data["agent_outputs"]["loan_agent"]
        prov = output.get("provenance", [])
        assert any(p["name"] == "check_loan_eligibility" for p in prov)
        assert "Home Loan" in data["final_response"] or "eligible" in data["final_response"].lower()

    @pytest.mark.asyncio
    async def test_scenario_3_fraud_alerts(self):
        """Scenario 3: Fraud Alerts"""
        data, latency = await self.run_scenario("Do I have any suspicious activity or fraud alerts?")
        
        assert "fraud_agent" in data["agent_outputs"]
        output = data["agent_outputs"]["fraud_agent"]
        assert any(p["name"] == "get_fraud_alerts" for p in output.get("provenance", []))

    @pytest.mark.asyncio
    async def test_scenario_4_compliance_checklist(self):
        """Scenario 4: Compliance Checklist"""
        data, latency = await self.run_scenario("What documents do I need for a Personal Loan?")
        
        assert "compliance_agent" in data["agent_outputs"]
        output = data["agent_outputs"]["compliance_agent"]
        assert any(p["name"] == "get_required_documents" for p in output.get("provenance", []))
        assert len(output["documents_checklist"]) > 0

    @pytest.mark.asyncio
    async def test_scenario_5_parallel_account_loan(self):
        """Scenario 5: Parallel Account + Loan Query"""
        data, latency = await self.run_scenario("Show my balance and check if I can get a ₹5L car loan")
        
        assert "account_agent" in data["agent_outputs"]
        assert "loan_agent" in data["agent_outputs"]
        assert "balance" in data["final_response"].lower()

    @pytest.mark.asyncio
    async def test_scenario_6_fraud_escalation(self):
        """Scenario 6: High Risk Fraud Escalation"""
        data, latency = await self.run_scenario("Report a suspicious transaction of ₹10,00,000 to Unknown Payee 'SCAMMER'")
        
        assert data["status"] == "ESCALATED"
        assert "halted" in data["final_response"].lower() or "critical" in data["final_response"].lower() or "escalated" in data["final_response"].lower()

    @pytest.mark.asyncio
    async def test_scenario_7_privacy_compliance(self):
        """Scenario 7: Privacy Compliance"""
        data, latency = await self.run_scenario("Show me the privacy rules for my personal data according to RBI and DPDP")
        
        assert "compliance_agent" in data["agent_outputs"], f"compliance_agent not in outputs: {data}"
        output = data["agent_outputs"]["compliance_agent"]
        if "error" in output:
             pytest.fail(f"Compliance Agent Error: {output['error']}")
        rules_text = json.dumps(output["rules"])
        assert any(k in rules_text.lower() for k in ["dpdp", "privacy", "data"])

    @pytest.mark.asyncio
    async def test_scenario_8_account_inventory(self):
        """Scenario 8: Account Inventory"""
        data, latency = await self.run_scenario("List all my active and inactive accounts")
        
        assert "account_agent" in data["agent_outputs"], f"account_agent not in outputs: {data}"
        output = data["agent_outputs"]["account_agent"]
        prov = [p["name"] for p in output.get("provenance", [])]
        print(f"Found provenance: {prov}")
        assert "find_inactive_accounts" in prov, f"find_inactive_accounts not in provenance: {prov}"
        assert "inactive_accounts" in output
