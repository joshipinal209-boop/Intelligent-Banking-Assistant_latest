import os
import json
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field

# Constants
DATA_PATH = "data/seed/mcp/core_banking.json"

app = FastAPI(
    title="Core Banking MCP Server",
    description="MCP-like interface for synthetic core banking data",
    version="1.0.0"
)

# --- Pydantic Models ---

class CustomerRequest(BaseModel):
    customer_id: str = Field(..., description="The unique ID of the customer")

class CustomerResponse(BaseModel):
    customer_id: str
    name: str
    email: str
    phone: str
    address: str
    pan: str
    credit_score: int
    risk_profile: str
    kyc_status: str
    created_at: str

class BalanceRequest(BaseModel):
    account_id: str = Field(..., description="The unique ID of the account")

class BalanceResponse(BaseModel):
    account_id: str
    customer_id: str
    account_type: str
    balance: float
    currency: str
    status: str

class TransactionRequest(BaseModel):
    account_id: str = Field(..., description="The unique ID of the account")
    limit: int = Field(10, description="Number of transactions to return (max 100)")

class Transaction(BaseModel):
    txn_id: str
    account_id: str
    type: str
    amount: float
    direction: str
    timestamp: str
    merchant: str
    status: str

class TransactionListResponse(BaseModel):
    account_id: str
    transactions: List[Transaction]

# --- Data Loading ---

def load_data():
    if not os.path.exists(DATA_PATH):
        raise RuntimeError(f"Data file not found at {DATA_PATH}")
    with open(DATA_PATH, "r") as f:
        return json.load(f)

# --- Tool Endpoints ---

@app.post("/tools/get_customer", response_model=CustomerResponse, tags=["Tools"])
async def get_customer(request: CustomerRequest):
    data = load_data()
    customer = next((c for c in data["customers"] if c["customer_id"] == request.customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail=f"customer_not_found: {request.customer_id}")
    return customer

@app.post("/tools/get_balance", response_model=BalanceResponse, tags=["Tools"])
async def get_balance(request: BalanceRequest):
    data = load_data()
    account = next((a for a in data["accounts"] if a["account_id"] == request.account_id), None)
    if not account:
        raise HTTPException(status_code=404, detail=f"account_not_found: {request.account_id}")
    return account

@app.post("/tools/list_transactions", response_model=TransactionListResponse, tags=["Tools"])
async def list_transactions(request: TransactionRequest):
    if request.limit > 100:
        raise HTTPException(status_code=400, detail="limit_exceeded: Maximum limit is 100")
        
    data = load_data()
    # Ensure account exists first
    account_exists = any(a for a in data["accounts"] if a["account_id"] == request.account_id)
    if not account_exists:
        raise HTTPException(status_code=404, detail=f"account_not_found: {request.account_id}")
        
    transactions = [t for t in data["transactions"] if t["account_id"] == request.account_id]
    # Sort by timestamp descending
    transactions.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "account_id": request.account_id,
        "transactions": transactions[:request.limit]
    }

# --- Health Check ---

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8101)
