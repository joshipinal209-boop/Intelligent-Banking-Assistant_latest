import os
import sqlite3
import time
from typing import Dict, Any, List, Union
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import GraphState, SqliteAuditStore
from graph.router import router_node, route_query
from graph.account_agent import account_agent_node
from graph.loan_agent import loan_agent_node
from graph.fraud_agent import fraud_agent_node
from graph.compliance_agent import compliance_agent_node
from graph.aggregator import aggregator_node
from common.decorators import time_node

# --- Audit Store Initialization ---
from graph.audit import audit_store

@time_node("human_interrupt")
async def human_interrupt_node(state: GraphState):
    """
    Halts execution and returns escalation instructions.
    """
    
    instructions = (
        "CRITICAL: High risk detected. This session has been flagged and halted for manual compliance review. "
        "A bank representative will contact you shortly. Reference ID: " + state.get("customer_id", "Unknown")
    )
    
    result = {
        "final_response": instructions,
        "requires_human": True
    }
    return result

# --- Conditional Edges ---

def fraud_check_edge(state: GraphState) -> str:
    """
    Routes to human_interrupt if fraud risk is high.
    """
    if state.get("requires_human", False):
        return "human_interrupt"
    return "aggregator"

# --- Graph Creation ---

def create_graph():
    # Define the graph
    workflow = StateGraph(GraphState)

    # Add Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("account_agent", account_agent_node)
    workflow.add_node("loan_agent", loan_agent_node)
    workflow.add_node("fraud_agent", fraud_agent_node)
    workflow.add_node("compliance_agent", compliance_agent_node)
    workflow.add_node("aggregator", aggregator_node)
    workflow.add_node("human_interrupt", human_interrupt_node)

    # Define Entry Point
    workflow.set_entry_point("router")

    # Routing from Router
    workflow.add_conditional_edges(
        "router",
        route_query,
        {
            "account_agent": "account_agent",
            "loan_agent": "loan_agent",
            "fraud_agent": "fraud_agent",
            "compliance_agent": "compliance_agent"
        }
    )

    # Routing from Specialized Agents
    # All specialist agents (except fraud) go to aggregator
    workflow.add_edge("account_agent", "aggregator")
    workflow.add_edge("loan_agent", "aggregator")
    workflow.add_edge("compliance_agent", "aggregator")
    
    # Fraud Agent has a safety check
    workflow.add_conditional_edges(
        "fraud_agent",
        fraud_check_edge,
        {
            "human_interrupt": "human_interrupt",
            "aggregator": "aggregator"
        }
    )

    # Aggregator and Human Interrupt are Terminal nodes in this simplified flow
    # (Human interrupt stops the graph)
    workflow.add_edge("aggregator", END)
    workflow.add_edge("human_interrupt", END)

    # Checkpointing
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)

# --- Singleton Graph Instance ---
app = create_graph()
