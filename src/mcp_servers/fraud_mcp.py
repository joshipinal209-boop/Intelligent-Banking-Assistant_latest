import os
import json
import hashlib
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Constants
DATA_PATH = "data/seed/mcp/fraud.json"

app = FastAPI(
    title="Fraud MCP Server",
    description="MCP-like interface for synthetic fraud monitoring data",
    version="1.0.0"
)

# --- Pydantic Models ---

class PayeeCheckRequest(BaseModel):
    payee_name: str = Field(..., description="The name of the payee to check")
    account_id: Optional[str] = Field(None, description="The account ID initiating the payment")

class PayeeCheckResponse(BaseModel):
    payee_name: str
    risk_score: int = Field(..., description="Risk score from 0-100 (higher is riskier)")
    risk_level: str
    recommendation: str

class Alert(BaseModel):
    alert_id: str
    txn_id: str
    reason: str
    status: str

class FraudAlertsResponse(BaseModel):
    alerts: List[Alert]

class RiskScoreRequest(BaseModel):
    txn_id: str
    amount: float
    payee_name: str

class RiskScoreResponse(BaseModel):
    txn_id: str
    risk_score: float
    flags: List[str]
    is_suspicious: bool

class FlagTransactionRequest(BaseModel):
    txn_id: str
    reason: str

class FlagTransactionResponse(BaseModel):
    txn_id: str
    status: str
    message: str

# --- Helper Functions ---

def get_deterministic_score(name: str) -> int:
    """Generates a deterministic score between 0 and 100 based on the payee name."""
    hash_object = hashlib.md5(name.lower().encode())
    return int(hash_object.hexdigest(), 16) % 101

def get_risk_level(score: int) -> str:
    if score < 30:
        return "Low"
    elif score < 70:
        return "Medium"
    else:
        return "High"

def get_recommendation(level: str) -> str:
    if level == "Low":
        return "Approved"
    elif level == "Medium":
        return "Secondary verification recommended"
    else:
        return "Manual review required / Blocked"

# --- Data Loading ---

def load_data():
    if not os.path.exists(DATA_PATH):
        raise RuntimeError(f"Data file not found at {DATA_PATH}")
    with open(DATA_PATH, "r") as f:
        return json.load(f)

# --- Tool Endpoints ---

@app.post("/tools/check_payee", response_model=PayeeCheckResponse, tags=["Tools"])
async def check_payee(request: PayeeCheckRequest):
    # Simulated Error Cases
    if "UNKNOWN" in request.payee_name.upper():
        raise HTTPException(status_code=404, detail="payee_unknown: The specified payee is not in our verified registry.")
        
    if request.payee_name == "MODEL_ERROR_TRIGGER":
        raise HTTPException(status_code=500, detail="model_error: The underlying fraud detection model failed to return a response.")
        
    score = get_deterministic_score(request.payee_name)
    level = get_risk_level(score)
    recommendation = get_recommendation(level)
    
    return {
        "payee_name": request.payee_name,
        "risk_score": score,
        "risk_level": level,
        "recommendation": recommendation
    }

@app.post("/tools/get_fraud_alerts", response_model=FraudAlertsResponse, tags=["Tools"])
async def get_fraud_alerts():
    data = load_data()
    return {"alerts": data["fraud_alerts"]}

@app.post("/tools/score_transaction_risk", response_model=RiskScoreResponse, tags=["Tools"])
async def score_transaction_risk(request: RiskScoreRequest):
    # Simulated risk logic
    score = get_deterministic_score(request.payee_name) / 100.0
    flags = []
    
    if request.amount > 50000:
        score = min(1.0, score + 0.3)
        flags.append("High value transaction")
        
    if "UNKNOWN" in request.payee_name.upper():
        score = min(1.0, score + 0.5)
        flags.append("Unverified payee")
        
    return {
        "txn_id": request.txn_id,
        "risk_score": score,
        "flags": flags,
        "is_suspicious": score > 0.7
    }

@app.post("/tools/flag_transaction", response_model=FlagTransactionResponse, tags=["Tools"])
async def flag_transaction(request: FlagTransactionRequest):
    # Mocking the flagging action
    return {
        "txn_id": request.txn_id,
        "status": "Flagged",
        "message": f"Transaction {request.txn_id} successfully flagged: {request.reason}"
    }

# --- Health Check ---

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8103)
