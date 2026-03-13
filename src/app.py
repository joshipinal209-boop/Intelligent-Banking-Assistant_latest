import os
import uuid
import json
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from graph.main_graph import app as graph_app
from graph.audit import audit_store
from auth import router as auth_router, get_current_user
from auth.models import User

# Initialize FastAPI app
app = FastAPI(
    title="FinCore Intelligent Banking Assistant API",
    description="AI-powered multi-agent banking system with JWT authentication",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)

# --- Pydantic Models ---

class QueryRequest(BaseModel):
    session_id: str = Field(..., description="Unique thread ID for the LangGraph session")
    query: str = Field(..., description="User query for the assistant")
    customer_id: Optional[str] = Field(None, description="Explicit customer ID if known")

class QueryResponse(BaseModel):
    status: str = "SUCCESS"
    final_response: str
    agent_outputs: Dict[str, Any]
    risk_level: str = "low"
    requires_human: bool = False
    audit_id: str
    customer_id: str
    latency_ms: Optional[float] = None

@app.get("/customers")
async def get_customers(current_user: User = Depends(get_current_user)):
    """
    Returns a list of all synthetic customers for the dropdown.
    Requires: Authentication (read scope)
    """
    path = "data/seed/mcp/core_banking.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            return data.get("customers", [])
    return []

# --- API Endpoints ---

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, current_user: User = Depends(get_current_user)):
    """
    Exposes the LangGraph banking assistant workflow.
    Handles session persistence and human-in-the-loop escalation.
    Requires: Authentication (write scope)
    """
    config = {"configurable": {"thread_id": request.session_id}}
    
    # Initialize state
    initial_state = {
        "query": request.query,
        "customer_id": request.customer_id or "unknown",
        "intent": [],
        "agent_outputs": {},
        "mcp_calls_log": [],
        "kg_queries_log": [],
        "final_response": "",
        "risk_level": "low",
        "requires_human": False,
        "session_id": request.session_id
    }
    
    try:
        # Invoke the graph
        final_state = await graph_app.ainvoke(initial_state, config)
        
        status = "SUCCESS"
        if final_state.get("requires_human", False):
            status = "ESCALATED"
            
        return QueryResponse(
            status=status,
            final_response=final_state.get("final_response", "No response generated."),
            agent_outputs=final_state.get("agent_outputs", {}),
            risk_level=final_state.get("risk_level", "low"),
            requires_human=final_state.get("requires_human", False),
            audit_id=request.session_id,
            customer_id=final_state.get("customer_id", "unknown"),
            latency_ms=final_state.get("latency_ms")
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: process_query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@app.get("/audit/{session_id}")
async def get_audit_trail(session_id: str, current_user: User = Depends(get_current_user)):
    """
    Retrieves the full audit trail for a given session/thread.
    Requires: Authentication (read or audit scope)
    """
    try:
        trail = audit_store.get_audit_trail(session_id)
        if not trail:
            raise HTTPException(status_code=404, detail="Audit trail not found for this session.")
        return {"session_id": session_id, "trail": trail}
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: get_audit_trail failed for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit trail: {str(e)}")

@app.get("/metrics")
async def get_metrics(current_user: User = Depends(get_current_user)):
    """
    Returns aggregated P50 and P90 latency metrics per node and overall.
    Requires: Authentication (admin scope)
    """
    import numpy as np
    
    try:
        data = audit_store.get_all_durations()
        if not data:
            return {"status": "no_data", "metrics": {}}
        
        # Group by type and name
        groups = {}
        all_durations = []
        
        for entry in data:
            key = f"{entry['event_type']}:{entry['node_name']}"
            if key not in groups:
                groups[key] = []
            groups[key].append(entry['duration_ms'])
            all_durations.append(entry['duration_ms'])
            
        metrics = {
            "overall": {
                "p50": float(np.percentile(all_durations, 50)),
                "p90": float(np.percentile(all_durations, 90)),
                "count": len(all_durations)
            },
            "by_component": {}
        }
        
        for key, durations in groups.items():
            metrics["by_component"][key] = {
                "p50": float(np.percentile(durations, 50)),
                "p90": float(np.percentile(durations, 90)),
                "count": len(durations)
            }
            
        return metrics
    except Exception as e:
        print(f"ERROR: get_metrics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate metrics: {str(e)}")

@app.get("/audit/export")
async def export_audit(current_user: User = Depends(get_current_user)):
    """
    Streams the entire audit trail in JSONL format.
    Requires: Authentication (admin scope)
    """
    from fastapi.responses import StreamingResponse
    
    try:
        return StreamingResponse(
            audit_store.stream_all_jsonl(),
            media_type="application/x-jsonlines",
            headers={"Content-Disposition": "attachment; filename=audit_export.jsonl"}
        )
    except Exception as e:
        print(f"ERROR: export_audit failed: {e}")
        raise HTTPException(status_code=500, detail=f"Audit export failed: {str(e)}")

# --- Startup ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
