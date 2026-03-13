import json
import httpx
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from config.llm import get_llm
from kg.engine import get_kg_engine
from vector_store.loader import get_retriever
from graph.state import GraphState

# --- Pydantic Models for Structured Output ---

class RuleReference(BaseModel):
    rule_id: str = ""
    source: str = Field("RBI", description="RBI or DPDP")
    description: str = ""

class DTICompliance(BaseModel):
    name: str = "DTI_limit"
    within_limit: bool = True
    max_dti: float = 0.5

class ComplianceAgentResponse(BaseModel):
    documents_checklist: List[str] = []
    rules: List[RuleReference] = []
    compliance_checks: List[DTICompliance] = []
    provenance: List[Dict[str, Any]] = []

from common.decorators import time_node

# --- Compliance Agent Node ---

COMPLIANCE_AGENT_PROMPT = """
You are the Compliance Agent for FinCore. Your job is to provide required documents and rules applicable to a product or scenario.
Answer based ONLY on the provided context from MCP tools, Knowledge Graph traversals, and Vector Store documents.

User Query: {query}
Customer ID: {customer_id}

Context:
{context}

Response Requirements:
1. Provide a comprehensive checklist of required documents for the mentioned product.
2. Cite specific rule IDs and sources (RBI/DPDP) from the provided rules.
3. Include compliance check results (e.g., DTI limit).
4. Return a VALID response matching the requested schema.
5. Provide full "provenance" for all data sources used.
"""

@time_node("compliance_agent")
async def compliance_agent_node(state: GraphState) -> Dict[str, Any]:
    """
    Handles regulatory compliance, document requirements, and rule retrieval.
    Uses Compliance MCP, KG Engine, and Vector Store.
    """
    customer_id = state.get("customer_id", "unknown")
    session_id = state.get("session_id", "default")
    kg = get_kg_engine()
    llm = get_llm()
    structured_llm = llm.with_structured_output(ComplianceAgentResponse)
    
    from graph.toolkit import toolkit
    from graph.main_graph import audit_store
    
    context_data = []
    provenance = []
    
    # 1. Extraction: Look for Product Name or Topic in query
    product_match = re.search(r"'(.*?)'|\"(.*?)\"|(Home Loan|Car Loan|Personal Loan|MSME Loan|Account)", state["query"], re.IGNORECASE)
    product_id = product_match.group(0) if product_match else "General"
    
    topic = "rbi_general"
    if any(k in state["query"].lower() for k in ["privacy", "data", "dpdp"]):
        topic = "dpdp_privacy"
    elif any(k in state["query"].lower() for k in ["loan", "emi", "mortgage", "msme"]):
        topic = "loan_docs"

    # 2. Tools via toolkit
    mcp_base_url = "http://localhost:8104" # Compliance MCP
    
    # A. Get Document Requirements
    doc_res = await toolkit.mcp_call(session_id, audit_store, mcp_base_url, "get_required_documents", {"product_id": product_id})
    doc_reqs = doc_res.get("data", {}).get("required_documents", [])
    if "provenance" in doc_res: provenance.append(doc_res["provenance"])

    # B. Get Regulatory Rules by Topic
    rules_res = await toolkit.mcp_call(session_id, audit_store, mcp_base_url, "get_rules_by_topic", {"topic": topic})
    mcp_rules = rules_res.get("data", {}).get("rules", [])
    if "provenance" in rules_res: provenance.append(rules_res["provenance"])

    # C. Check DTI Limit
    dti_res = await toolkit.mcp_call(session_id, audit_store, mcp_base_url, "check_dti_limit", {"customer_id": customer_id})
    dti_status = dti_res.get("data", {})
    if "provenance" in dti_res: provenance.append(dti_res["provenance"])

    # D. KG Rules
    kg_res = toolkit.kg_query(session_id, audit_store, "rules_for_product", product_id)
    kg_rules = kg_res.get("results", [])
    if "provenance" in kg_res: provenance.append(kg_res["provenance"])

    # E. Vector Store Retrieval
    search_query = f"{product_id} {topic} compliance rules"
    ret_res = toolkit.retrieve(session_id, audit_store, search_query)
    vector_docs = ret_res.get("results", [])
    if "provenance" in ret_res: provenance.append(ret_res["provenance"])

    # 3. Synthesize
    prompt = ChatPromptTemplate.from_template(COMPLIANCE_AGENT_PROMPT)
    chain = prompt | structured_llm
    
    full_context = {
        "mcp_documents": doc_reqs,
        "mcp_rules": mcp_rules,
        "mcp_dti": dti_status,
        "kg_rules": kg_rules,
        "vector_docs": vector_docs,
        "internal_logs": provenance,
        "errors": context_data
    }
    
    try:
        response: ComplianceAgentResponse = await chain.ainvoke({
            "query": state["query"],
            "customer_id": customer_id,
            "context": json.dumps(full_context)
        })
        
        # Log to state
        all_provenance = provenance + [p for p in response.provenance if p.get("name") not in [x.get("name") for x in provenance]]
        
        final_output = response.dict()
        final_output["provenance"] = all_provenance
        
        return {
            "agent_outputs": {"compliance_agent": final_output},
            "mcp_calls_log": [p for p in all_provenance if p.get("type") == "mcp"],
            "kg_queries_log": [p.get("name") for p in all_provenance if p.get("type") == "kg" and p.get("name")]
        }
    except Exception as e:
        return {"agent_outputs": {"compliance_agent": {"error": str(e)}}}
