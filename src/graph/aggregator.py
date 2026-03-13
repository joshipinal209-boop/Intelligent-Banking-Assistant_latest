import json
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from config.llm import get_llm
from graph.state import GraphState

from common.decorators import time_node

AGGREGATOR_PROMPT = """
You are the Aggregator. Consolidate agent outputs into a single, coherent, and explainable response.

Rules:
- Preserve facts only from agent outputs. No new facts.
- Include a brief “Why this decision?” section referencing provenance.
- If requires_human=true, clearly state escalation and next steps.

Your final output MUST follow this STRICT format:
1. A user-friendly answer (<= 150 words)
2. A bullet list of data sources used (provenance: MCP endpoints, KG queries, retrieved docs)
3. Risk level and whether a human is involved

Input JSON:
{agent_outputs}
"""

@time_node("aggregator")
async def aggregator_node(state: GraphState) -> Dict[str, Any]:
    """
    Merges specialized agent outputs into a final cohesive response following strict user templates.
    """
    llm = get_llm()
    agent_outputs = state.get("agent_outputs", {})
    requires_human = state.get("requires_human", False)
    risk_level = state.get("risk_level", "low")
    
    # Format the outputs for the LLM
    formatted_input = json.dumps({
        "agent_outputs": agent_outputs,
        "requires_human": requires_human,
        "risk_level": risk_level
    }, indent=2)
    
    prompt = ChatPromptTemplate.from_template(AGGREGATOR_PROMPT)
    chain = prompt | llm
    
    try:
        response = await chain.ainvoke({
            "agent_outputs": formatted_input
        })
        
        return {
            "final_response": response.content
        }
    except Exception as e:
        return {
            "final_response": f"Error aggregating agent responses: {str(e)}"
        }
