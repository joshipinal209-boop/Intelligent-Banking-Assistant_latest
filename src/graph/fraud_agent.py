import json
import httpx
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from config.llm import get_llm
from kg.engine import get_kg_engine
from graph.state import GraphState

# --- Pydantic Models for Structured Output ---

class RiskAssessment(BaseModel):
    risk_score: float = Field(0.0, description="Normalized risk score between 0.0 and 1.0")
    flags: List[str] = Field(default_factory=list, description="List of risk triggers")
    escalate: bool = Field(False, description="True if score > 0.7")

class RelatedEntities(BaseModel):
    payee_overlap_customers: List[str] = Field(default_factory=list, description="Other customer IDs who paid the same merchant")

class Action(BaseModel):
    type: str = Field("none", description="Action type: flag, block, or alert")
    transaction_id: str = ""
    reason: str = ""

class Provenance(BaseModel):
    type: str = Field(description="mcp or kg")
    name: str = Field(description="endpoint or query name")
    args: Dict[str, Any]

class FraudAgentResponse(BaseModel):
    risk_assessment: RiskAssessment = Field(default_factory=RiskAssessment)
    related_entities: RelatedEntities = Field(default_factory=RelatedEntities)
    actions: List[Action] = []
    provenance: List[Provenance] = []

from common.decorators import time_node

# --- Fraud Agent Node ---

FRAUD_AGENT_PROMPT = """
You are the Fraud Agent for FinCore. Your job is to evaluate transaction risks and identify suspicious networks.
Use the provided context from MCP tools and Knowledge Graph traversals.

User Query: {query}
Customer ID: {customer_id}

Context:
{context}

Response Requirements:
1. Provide a risk score (0-1.0) and list all identified flags.
2. If risk_score > 0.7, set escalate: true and specify a "flag" action.
3. List related entities (payee overlap) found via KG to identify potential suspicious networks.
4. If no specific transaction ID is provided in the query, analyze recent alerts for the customer if available.
5. Return a VALID response matching the requested schema.
6. Provide full "provenance" for all data sources used.
"""

@time_node("fraud_agent")
async def fraud_agent_node(state: GraphState) -> Dict[str, Any]:
    """
    Handles fraud detection, risk scoring, and payee network analysis.
    Uses Fraud MCP and KG Engine via toolkit.
    """
    customer_id = state.get("customer_id", "unknown")
    session_id = state.get("session_id", "default")
    llm = get_llm()
    structured_llm = llm.with_structured_output(FraudAgentResponse)
    
    from graph.toolkit import toolkit
    from graph.main_graph import audit_store
    
    context_data = []
    provenance = []
    
    # 1. Extraction: Look for transaction amount and payee in query
    amount_match = re.search(r"(?:₹|\$|INR)\s?(\d+(?:\.\d+)?)\s?(?:L|Lakh|Cr)?", state["query"])
    tx_amount = 0.0
    if amount_match:
        try:
            val = float(amount_match.group(1))
            if "L" in state["query"] or "Lakh" in state["query"]: val *= 100000
            elif "Cr" in state["query"]: val *= 10000000
            tx_amount = val
        except: tx_amount = 500.0
    
    payee_match = re.search(r"'(.*?)'|\"(.*?)\"", state["query"])
    payee_id = payee_match.group(0).strip("'\"") if payee_match else "Unknown"

    # 2. Tools via toolkit
    mcp_base_url = "http://localhost:8103" # Fraud MCP
    
    # A. Score Risk
    risk_res = await toolkit.mcp_call(session_id, audit_store, mcp_base_url, "score_transaction_risk", {
        "amount": tx_amount, "payee_id": payee_id
    })
    risk_data = risk_res.get("data", {})
    if "provenance" in risk_res: provenance.append(risk_res["provenance"])

    # B. Get Alerts
    alerts_res = await toolkit.mcp_call(session_id, audit_store, mcp_base_url, "get_fraud_alerts", {"customer_id": customer_id})
    fraud_alerts = alerts_res.get("data", {}).get("alerts", [])
    if "provenance" in alerts_res: provenance.append(alerts_res["provenance"])

    # C. KG: Payee Overlap
    kg_res = toolkit.kg_query(session_id, audit_store, "fraud_payee_overlap", payee_id)
    payee_network = kg_res.get("results", [])
    if "provenance" in kg_res: provenance.append(kg_res["provenance"])

    # 3. Synthesize
    prompt = ChatPromptTemplate.from_template(FRAUD_AGENT_PROMPT)
    chain = prompt | structured_llm
    
    full_context = {
        "mcp_risk": risk_data,
        "mcp_alerts": fraud_alerts,
        "kg_overlaps": payee_network,
        "internal_logs": provenance,
        "errors": context_data
    }
    
    try:
        response: FraudAgentResponse = await chain.ainvoke({
            "query": state["query"],
            "customer_id": customer_id,
            "context": json.dumps(full_context)
        })
        
        # Log to state
        new_mcp_logs = [p.dict() for p in response.provenance if p.type == "mcp"]
        new_kg_logs = [p.name for p in response.provenance if p.type == "kg"]
        
        return {
            "agent_outputs": {"fraud_agent": response.dict()},
            "mcp_calls_log": new_mcp_logs,
            "kg_queries_log": new_kg_logs,
            "risk_level": "high" if response.risk_assessment.escalate else "low",
            "requires_human": response.risk_assessment.escalate
        }
    except Exception as e:
        return {"agent_outputs": {"fraud_agent": {"error": str(e)}}}
