import os
import json
import random
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Constants
DATA_PATH = "data/seed/mcp/credit.json"

app = FastAPI(
    title="Credit MCP Server",
    description="MCP-like interface for synthetic credit and loan data",
    version="1.0.0"
)

# --- Pydantic Models ---

class CreditScoreRequest(BaseModel):
    customer_id: str = Field(..., description="The unique ID of the customer")

class CreditScoreResponse(BaseModel):
    customer_id: str
    score: int
    provider: str = "FinCore Bureau"

class LoanDetailsRequest(BaseModel):
    loan_id: str = Field(..., description="The unique ID of the loan")

class LoanResponse(BaseModel):
    loan_id: str
    customer_id: str
    type: str
    amount: float
    interest_rate: float
    tenure_months: int
    emi: float
    status: str
    risk_flag: bool

class CustomerLoansRequest(BaseModel):
    customer_id: str = Field(..., description="The unique ID of the customer")

class CustomerLoansResponse(BaseModel):
    customer_id: str
    loans: List[LoanResponse]

class EMIObligationsResponse(BaseModel):
    customer_id: str
    total_emi: float
    active_loans_count: int

class EligibilityRequest(BaseModel):
    customer_id: str
    loan_type: str
    amount: float
    monthly_income: float = Field(50000.0, description="Monthly income for DTI calculation")

class EligibilityResponse(BaseModel):
    eligible: bool
    max_amount: float
    reason: str
    dti_ratio: float

# --- Data Loading ---

def load_data():
    if not os.path.exists(DATA_PATH):
        raise RuntimeError(f"Data file not found at {DATA_PATH}")
    with open(DATA_PATH, "r") as f:
        return json.load(f)

# --- Tool Endpoints ---

@app.post("/tools/get_credit_score", response_model=CreditScoreResponse, tags=["Tools"])
async def get_credit_score(request: CreditScoreRequest):
    # Simulated Bureau Error for a specific test ID
    if request.customer_id == "bureau_error_id":
        raise HTTPException(status_code=503, detail="bureau_error: Credit Bureau is currently unreachable")
        
    data = load_data()
    score_entry = next((s for s in data["credit_scores"] if s["customer_id"] == request.customer_id), None)
    
    if not score_entry:
        raise HTTPException(status_code=404, detail=f"insufficient_data: No credit history found for {request.customer_id}")
        
    return {
        "customer_id": request.customer_id,
        "score": score_entry["score"],
        "provider": "FinCore Bureau"
    }

@app.post("/tools/get_loan_details", response_model=LoanResponse, tags=["Tools"])
async def get_loan_details(request: LoanDetailsRequest):
    data = load_data()
    loan = next((l for l in data["loans"] if l["loan_id"] == request.loan_id), None)
    
    if not loan:
        raise HTTPException(status_code=404, detail=f"loan_not_found: {request.loan_id}")
        
    return loan

@app.post("/tools/get_customer_loans", response_model=CustomerLoansResponse, tags=["Tools"])
async def get_customer_loans(request: CustomerLoansRequest):
    data = load_data()
    loans = [l for l in data["loans"] if l["customer_id"] == request.customer_id]
    
    # We return an empty list if no loans found, but we could also 404 if the customer doesn't exist
    return {
        "customer_id": request.customer_id,
        "loans": loans
    }

@app.post("/tools/get_emi_obligations", response_model=EMIObligationsResponse, tags=["Tools"])
async def get_emi_obligations(request: CustomerLoansRequest):
    data = load_data()
    active_loans = [l for l in data["loans"] if l["customer_id"] == request.customer_id and l["status"] == "Active"]
    total_emi = sum(l["emi"] for l in active_loans)
    
    return {
        "customer_id": request.customer_id,
        "total_emi": total_emi,
        "active_loans_count": len(active_loans)
    }

@app.post("/tools/check_loan_eligibility", response_model=EligibilityResponse, tags=["Tools"])
async def check_loan_eligibility(request: EligibilityRequest):
    data = load_data()
    # 1. Get Credit Score
    score_entry = next((s for s in data["credit_scores"] if s["customer_id"] == request.customer_id), None)
    if not score_entry:
        return {
            "eligible": False,
            "max_amount": 0.0,
            "reason": "insufficient_data: No credit score found",
            "dti_ratio": 0.0
        }
    
    score = score_entry["score"]
    
    # 2. Get EMI Obligations
    active_loans = [l for l in data["loans"] if l["customer_id"] == request.customer_id and l["status"] == "Active"]
    current_emi = sum(l["emi"] for l in active_loans)
    
    # 3. Calculate DTI
    # Standard rule: Total EMI (current + new) should be < 50% of monthly income
    # Simulated New EMI: assume 1% of loan amount per month for simplicity
    estimated_new_emi = request.amount * 0.01 
    total_future_emi = current_emi + estimated_new_emi
    dti = total_future_emi / request.monthly_income
    
    # Eligibility rules
    if score < 650:
        return {
            "eligible": False,
            "max_amount": 0.0,
            "reason": f"Credit score {score} is below 650 threshold.",
            "dti_ratio": dti
        }
    
    if dti > 0.5:
        max_allowed_emi = request.monthly_income * 0.5 - current_emi
        max_loan = max(0.0, max_allowed_emi / 0.01)
        return {
            "eligible": False,
            "max_amount": max_loan,
            "reason": f"DTI ratio {dti:.2f} exceeds 0.5 limit with requested amount.",
            "dti_ratio": dti
        }
        
    return {
        "eligible": True,
        "max_amount": request.amount * 1.5, # Slightly more for buffer
        "reason": "Credit score and DTI within healthy limits.",
        "dti_ratio": dti
    }

# --- Health Check ---

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8102)
