import json
from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from config.llm import get_llm
from graph.state import GraphState

# --- Pydantic Model for Validation ---

class RouterOutput(BaseModel):
    """Output schema for the Router node."""
    intents: List[str] = Field(description="List of detected intents")
    customer_id: str = Field(description="Extracted customer ID or 'unknown'")
    risk_hint: Literal["low", "medium", "high"] = Field(description="Risk level hint")

from common.decorators import time_node

# --- Router Node ---

ROUTER_SYSTEM_PROMPT = """
You are the Router for FinCore’s Intelligent Banking Assistant.
Classify the user's query into one or more intents from:
[ "account_summary", "loan_eligibility", "fraud_report", "compliance_info", "product_upgrade", "transaction_issue", "loan_general", "account_inventory" ].
Use "compliance_info" specifically for document checklists, required paperwork, rules, or regulatory requirements. If the user asks for a checklist or what documents are needed, use compliance_info.
Also extract the customer_id if explicitly provided (else return "unknown").

{format_instructions}

User query: {query}
"""

@time_node("router")
async def router_node(state: GraphState) -> Dict[str, Any]:
    """
    Classifies the user query and extracts customer ID with Pydantic validation.
    """
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=RouterOutput)
    
    prompt = ChatPromptTemplate.from_template(ROUTER_SYSTEM_PROMPT)
    
    chain = prompt | llm | parser
    
    try:
        # Run the chain
        result: RouterOutput = await chain.ainvoke({
            "query": state["query"],
            "format_instructions": parser.get_format_instructions()
        })
        
        extracted_id = result.customer_id
        if extracted_id == "unknown" and state.get("customer_id") and state["customer_id"] != "unknown":
            extracted_id = state["customer_id"]

        return {
            "intent": result.intents,
            "customer_id": extracted_id,
            "risk_level": result.risk_hint
        }
    except Exception as e:
        print(f"Error in router_node: {e}")
        # Fallback to defaults
        return {
            "intent": ["account_summary"],
            "customer_id": "unknown",
            "risk_level": "low"
        }

# --- Conditional Routing Logic ---

def route_query(state: GraphState) -> List[str]:
    """
    Determines the next nodes in the graph based on the detected intents.
    Returns a list of agent names for parallel execution.
    """
    intents = state.get("intent", [])
    agents = set()
    
    if not intents:
        return ["account_agent"]
    
    if any(i in ["fraud_report"] for i in intents):
        agents.add("fraud_agent")
    
    if any(i in ["transaction_issue"] for i in intents):
        agents.add("fraud_agent")
        agents.add("account_agent") # Check balance/status for issues
    
    if any(i in ["loan_eligibility", "loan_general"] for i in intents):
        agents.add("loan_agent")
        agents.add("account_agent") # Check current holdings/balance
        if "loan_eligibility" in intents:
            agents.add("compliance_agent") # RBI rules/DTI
    
    if any(i == "product_upgrade" for i in intents):
        agents.add("account_agent")
        agents.add("compliance_agent")
    
    if any(i == "compliance_info" for i in intents):
        agents.add("compliance_agent")
        # If it mentions loans, add loan agent
        if any(w in state["query"].lower() for w in ["loan", "emi", "mortgage"]):
            agents.add("loan_agent")
    
    if any(i in ["account_summary", "account_inventory"] for i in intents):
        agents.add("account_agent")
        
    if not agents:
        return ["account_agent"]
        
    return list(agents)
