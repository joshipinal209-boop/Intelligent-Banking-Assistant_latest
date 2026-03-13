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

class LoanEligibility(BaseModel):
    eligible: bool = False
    max_amount: float = 0.0
    reason: str = ""

class CurrentLoan(BaseModel):
    loan_id: str = ""
    type: str = ""
    amount: float = 0.0
    interest_rate: float = 0.0
    tenure_months: int = 0
    emi: float = 0.0
    status: str = ""
    risk_flag: bool = False

class Provenance(BaseModel):
    type: str = Field(description="mcp or kg")
    name: str = Field(description="endpoint or query name")
    args: Dict[str, Any]

class LoanAgentResponse(BaseModel):
    eligibility: LoanEligibility
    current_loans: List[CurrentLoan] = []
    required_documents: List[str] = []
    provenance: List[Provenance] = []

from common.decorators import time_node

# --- Loan Agent Node ---

LOAN_AGENT_PROMPT = """
You are the Loan Agent for FinCore. Your job is to assess loan eligibility and summarize current loan exposure.
Use the provided context from MCP tools and Knowledge Graph traversals.

User Query: {query}
Customer ID: {customer_id}

Context:
{context}

Response Requirements:
1. Assess eligibility if a specific loan amount or type is mentioned.
2. Summarize all existing loans found in the context.
3. If uncertainty remains or credit score is missing, return "eligible: false" and list required documents (e.g., Salary Slips, PAN, ITR).
4. Return a VALID response matching the requested schema.
5. Provide full "provenance" for all data sources used.
"""

@time_node("loan_agent")
async def loan_agent_node(state: GraphState) -> Dict[str, Any]:
    """
    Handles loan eligibility and current loan details.
    Uses Credit MCP and KG Engine.
    """
    customer_id = state.get("customer_id", "unknown")
    session_id = state.get("session_id", "default")
    if customer_id == "unknown":
        return {"agent_outputs": {"loan_agent": {"error": "Missing customer ID"}}}

    kg = get_kg_engine()
    llm = get_llm()
    structured_llm = llm.with_structured_output(LoanAgentResponse)
    
    from graph.toolkit import toolkit
    from graph.main_graph import audit_store
    
    context_data = []
    provenance = []
    
    # 1. Fetch current loans from KG via toolkit
    kg_res = toolkit.kg_query(session_id, audit_store, "get_customer_loans", customer_id)
    kg_loans = kg_res.get("results", [])
    if "provenance" in kg_res: provenance.append(kg_res["provenance"])
    
    # 2. Extract requested loan amount from query if present
    amount_match = re.search(r"(?:₹|\$|INR)\s?(\d+(?:\.\d+)?)\s?(?:L|Lakh|Cr)?", state["query"])
    requested_amount = 500000.0 # Default fallback
    if amount_match:
        try:
            val = float(amount_match.group(1))
            if "L" in state["query"] or "Lakh" in state["query"]: val *= 100000
            elif "Cr" in state["query"]: val *= 10000000
            requested_amount = val
        except: pass
    
    # 3. Fetch from Credit MCP via toolkit
    mcp_base_url = "http://localhost:8102"
    
    # Extract loan type from query
    loan_type = "Personal"
    if "home" in state["query"].lower(): loan_type = "Home"
    elif "msme" in state["query"].lower() or "business" in state["query"].lower(): loan_type = "MSME"
    elif "car" in state["query"].lower() or "vehicle" in state["query"].lower(): loan_type = "Car"
    
    eligibility_data = {}
    mcp_loans = []
    credit_data = {}
    emi_data = {}
    
    # A. Check Eligibility
    elig_res = await toolkit.mcp_call(session_id, audit_store, mcp_base_url, "check_loan_eligibility", {
        "customer_id": customer_id,
        "loan_type": loan_type,
        "amount": requested_amount
    })
    eligibility_data = elig_res.get("data", {})
    if "provenance" in elig_res: provenance.append(elig_res["provenance"])

    # B. Get Credit Score (for provenance and details)
    score_res = await toolkit.mcp_call(session_id, audit_store, mcp_base_url, "get_credit_score", {"customer_id": customer_id})
    credit_data = score_res.get("data", {})
    if "provenance" in score_res: provenance.append(score_res["provenance"])

    # C. Get EMI Obligations
    emi_res = await toolkit.mcp_call(session_id, audit_store, mcp_base_url, "get_emi_obligations", {"customer_id": customer_id})
    emi_data = emi_res.get("data", {})
    if "provenance" in emi_res: provenance.append(emi_res["provenance"])
    
    # D. Fetch full loan details for those found in KG
    for kl in kg_loans:
        loan_id = kl["id"]
        loan_res = await toolkit.mcp_call(session_id, audit_store, mcp_base_url, "get_loan_details", {"loan_id": loan_id})
        if "data" in loan_res: mcp_loans.append(loan_res["data"])
        if "provenance" in loan_res: provenance.append(loan_res["provenance"])

    # 4. Synthesize with LLM
    prompt = ChatPromptTemplate.from_template(LOAN_AGENT_PROMPT)
    chain = prompt | structured_llm
    
    full_context = {
        "mcp_eligibility": eligibility_data,
        "mcp_credit_score": credit_data,
        "mcp_emi_obligations": emi_data,
        "kg_loans": kg_loans,
        "mcp_loan_details": mcp_loans,
        "internal_logs": provenance,
        "errors": context_data
    }
    
    try:
        response: LoanAgentResponse = await chain.ainvoke({
            "query": state["query"],
            "customer_id": customer_id,
            "context": json.dumps(full_context)
        })
        
        # Log to state
        all_provenance = provenance + [p.dict() for p in response.provenance if p.name not in [x.get("name") for x in provenance]]
        
        new_mcp_logs = [p for p in all_provenance if p.get("type") == "mcp"]
        new_kg_logs = [p.get("name") for p in all_provenance if p.get("type") == "kg" and p.get("name")]
        
        final_output = response.dict()
        final_output["provenance"] = all_provenance
        
        return {
            "agent_outputs": {"loan_agent": final_output},
            "mcp_calls_log": new_mcp_logs,
            "kg_queries_log": new_kg_logs
        }
    except Exception as e:
        return {"agent_outputs": {"loan_agent": {"error": str(e)}}}
