import json
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from config.llm import get_llm
from kg.engine import get_kg_engine
from graph.state import GraphState

# --- Pydantic Models for Structured Output ---

class Transaction(BaseModel):
    txn_id: str = ""
    amount: float = 0.0
    timestamp: str = ""
    merchant: str = ""
    type: str = ""
    direction: str = ""
    status: str = ""

class AccountInfo(BaseModel):
    account_id: str
    account_type: str = "Savings"
    balance: float = 0.0
    status: str = "Active"
    last_5_transactions: List[Transaction] = []

class Provenance(BaseModel):
    type: str = Field(description="mcp or kg")
    name: str = Field(description="endpoint or query name")
    args: Dict[str, Any]

class AccountAgentResponse(BaseModel):
    accounts: List[AccountInfo]
    inactive_accounts: List[str] = []
    upgrade_eligibility: Dict[str, Any] = {}
    summary: str = Field("", description="A brief summary of findings")
    provenance: List[Provenance] = []

from common.decorators import time_node

# --- Account Agent Node ---

ACCOUNT_AGENT_PROMPT = """
You are the Account Agent for FinCore. Answer the user query based ONLY on the provided context.
If information is missing, state what is missing instead of guessing.

User Query: {query}
Customer ID: {customer_id}

Context:
{context}

Response Requirements:
1. Return a VALID JSON object matching the requested schema.
2. Include ALL fields: "accounts", "inactive_accounts", "upgrade_eligibility", "summary", and "provenance".
3. Use the "summary" field to explain the status, balances, and any eligibility for upgrades or alerts about inactivity.
4. If "inactive_accounts" or "accounts" are empty, return an empty list [], not null.
5. "provenance" must contain all MCP and KG calls provided in the internal logs.

{format_instructions}
"""

@time_node("account_agent")
async def account_agent_node(state: GraphState) -> Dict[str, Any]:
    """
    Handles account summary and inventory queries.
    Uses Core Banking MCP and KG Engine.
    """
    customer_id = state.get("customer_id", "unknown")
    session_id = state.get("session_id", "default")
    if customer_id == "unknown":
        return {"agent_outputs": {"account_agent": {"error": "Missing customer ID"}}}

    kg = get_kg_engine()
    llm = get_llm()
    # Pydantic validation is now handled natively by the LLM client
    structured_llm = llm.with_structured_output(AccountAgentResponse)
    
    from graph.toolkit import toolkit
    from graph.main_graph import audit_store
    
    context_data = []
    provenance = []
    
    # 1. Fetch data from toolkit
    mcp_base_url = "http://localhost:8101"
    
    # A. KG: Get accounts
    kg_res = toolkit.kg_query(session_id, audit_store, "get_customer_accounts", customer_id)
    kg_accounts = kg_res.get("results", [])
    if "provenance" in kg_res: provenance.append(kg_res["provenance"])
    
    accounts_data = []
    for acc in kg_accounts:
        acc_id = acc["id"]
        # B. MCP: Get Balance
        bal_res = await toolkit.mcp_call(session_id, audit_store, mcp_base_url, "get_balance", {"account_id": acc_id})
        if "provenance" in bal_res: provenance.append(bal_res["provenance"])
        
        # C. MCP: List Transactions
        txn_res = await toolkit.mcp_call(session_id, audit_store, mcp_base_url, "list_transactions", {"account_id": acc_id, "limit": 5})
        if "provenance" in txn_res: provenance.append(txn_res["provenance"])
        
        acc_info = {
            "account_id": acc_id,
            "account_type": acc.get("account_type", "Unknown"),
            "balance": bal_res.get("data", {}).get("balance", 0.0) if "data" in bal_res else 0.0,
            "status": bal_res.get("data", {}).get("status", "Active") if "data" in bal_res else "Unknown",
            "last_5_transactions": txn_res.get("data", {}).get("transactions", []) if "data" in txn_res else []
        }
        accounts_data.append(acc_info)

    # 2. Check for inactive accounts via KG
    inactive_ids = []
    if any(k in state["query"].lower() for k in ["inactive", "dormant", "summary"]):
        inact_res = toolkit.kg_query(session_id, audit_store, "find_inactive_accounts", customer_id, 6)
        inactive_ids = inact_res.get("results", [])
        if "provenance" in inact_res: provenance.append(inact_res["provenance"])

    # 3. Check for Product Upgrade Eligibility
    upgrade_info = {}
    if any(k in state["query"].lower() for k in ["upgrade", "premium", "benefits"]):
        target_product = "Premium Savings"
        if "premium" in state["query"].lower(): target_product = "Premium Savings"
        elif "current" in state["query"].lower(): target_product = "Current Account"
        
        upg_res = toolkit.kg_query(session_id, audit_store, "get_upgrade_eligibility", customer_id, target_product)
        upgrade_info = upg_res.get("results", {})
        if "provenance" in upg_res: provenance.append(upg_res["provenance"])

    # 4. Synthesize with LLM
    prompt = ChatPromptTemplate.from_template(ACCOUNT_AGENT_PROMPT)
    chain = prompt | structured_llm
    
    full_context = {
        "mcp_accounts": accounts_data,
        "kg_inactive": inactive_ids,
        "kg_upgrade_eligibility": upgrade_info,
        "internal_logs": provenance,
        "errors": context_data
    }
    
    try:
        response: AccountAgentResponse = await chain.ainvoke({
            "query": state["query"],
            "customer_id": customer_id,
            "context": json.dumps(full_context),
            "format_instructions": "" # Handled by with_structured_output
        })
        
        # Log to state
        # Merge LLM-detected provenance with internal toolkit logs for 100% accuracy
        all_provenance = provenance + [p.dict() for p in response.provenance if p.name not in [x.get("name") for x in provenance]]
        
        new_mcp_logs = [p for p in all_provenance if p.get("type") == "mcp"]
        new_kg_logs = [p.get("name") for p in all_provenance if p.get("type") == "kg" and p.get("name")]
        
        final_output = response.dict()
        final_output["provenance"] = all_provenance
        
        return {
            "agent_outputs": {"account_agent": final_output},
            "mcp_calls_log": new_mcp_logs,
            "kg_queries_log": new_kg_logs
        }
    except Exception as e:
        return {"agent_outputs": {"account_agent": {"error": str(e)}}}
