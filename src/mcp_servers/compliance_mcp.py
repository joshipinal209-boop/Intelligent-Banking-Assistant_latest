import os
import json
import glob
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Constants
COMPLIANCE_DATA_PATH = "data/seed/mcp/compliance.json"
RULES_DIR = "data/seed/vector_docs"

app = FastAPI(
    title="Compliance MCP Server",
    description="MCP-like interface for synthetic compliance and regulatory data",
    version="1.0.0"
)

# --- Pydantic Models ---

class ComplianceReportRequest(BaseModel):
    customer_id: str = Field(..., description="The unique ID of the customer")

class ComplianceReport(BaseModel):
    report_id: str
    customer_id: str
    status: str
    category: str

class ComplianceReportResponse(BaseModel):
    customer_id: str
    reports: List[ComplianceReport]

class RulesRequest(BaseModel):
    topic: str = Field(..., description="Topic key: 'loan_docs', 'rbi_general', 'dpdp_privacy'")

class RuleSummary(BaseModel):
    rule_id: str
    title: str
    summary: str
    source_file: str

class RulesResponse(BaseModel):
    topic: str
    rules: List[RuleSummary]

class DocumentRequirementsRequest(BaseModel):
    product_id: str

class DocumentRequirementsResponse(BaseModel):
    product_id: str
    required_documents: List[str]

class DTILimitRequest(BaseModel):
    customer_id: str
    amount: float = 0.0

class DTILimitResponse(BaseModel):
    customer_id: str
    within_limit: bool
    current_dti: float
    max_allowed_dti: float = 0.5

# --- Helper Functions ---

def parse_rule_markdown(file_path: str) -> RuleSummary:
    """Parses a rule markdown file to extract title and a brief summary."""
    with open(file_path, "r") as f:
        content = f.read()
    
    lines = content.split("\n")
    title = lines[0].lstrip("# ").strip() if lines else "Untitled"
    
    # Simple summary extraction: find the paragraph after "## Regulation Overview"
    summary = "No summary available"
    try:
        overview_idx = content.find("## Regulation Overview")
        if overview_idx != -1:
            rest = content[overview_idx + len("## Regulation Overview"):].strip()
            summary = rest.split("\n\n")[0].strip()
    except Exception:
        pass
        
    rule_id = os.path.basename(file_path).replace("rule_", "").replace(".md", "")
    
    return RuleSummary(
        rule_id=rule_id,
        title=title,
        summary=summary,
        source_file=os.path.basename(file_path)
    )

# --- Tool Endpoints ---

@app.post("/tools/get_compliance_report", response_model=ComplianceReportResponse, tags=["Tools"])
async def get_compliance_report(request: ComplianceReportRequest):
    if not os.path.exists(COMPLIANCE_DATA_PATH):
        raise RuntimeError("Compliance data file not found.")
        
    with open(COMPLIANCE_DATA_PATH, "r") as f:
        data = json.load(f)
        
    reports = [r for r in data["compliance_reports"] if r["customer_id"] == request.customer_id]
    
    return {
        "customer_id": request.customer_id,
        "reports": reports
    }

@app.post("/tools/get_rules_by_topic", response_model=RulesResponse, tags=["Tools"])
async def get_rules_by_topic(request: RulesRequest):
    # Mapping topics to keywords found in rule titles or contents
    topic_map = {
        "loan_docs": ["Digital Lending"],
        "rbi_general": ["KYC", "AML", "Regulation"],
        "dpdp_privacy": ["Data Privacy"]
    }
    
    if request.topic not in topic_map:
        raise HTTPException(status_code=400, detail=f"Invalid topic: {request.topic}. Supported: {list(topic_map.keys())}")
        
    keywords = topic_map[request.topic]
    rule_files = glob.glob(os.path.join(RULES_DIR, "rule_*.md"))
    
    matched_rules = []
    for f in rule_files:
        rule = parse_rule_markdown(f)
        # Check if any keyword matches title or summary
        if any(kw.lower() in rule.title.lower() or kw.lower() in rule.summary.lower() for kw in keywords):
            matched_rules.append(rule)
            
    return {
        "topic": request.topic,
        "rules": matched_rules
    }

@app.post("/tools/get_required_documents", response_model=DocumentRequirementsResponse, tags=["Tools"])
async def get_required_documents(request: DocumentRequirementsRequest):
    # Mock document list based on product keywords
    docs = ["PAN Card", "Aadhaar Card", "Address Proof"]
    if "loan" in request.product_id.lower():
        docs.extend(["Salary Slips (3 months)", "Bank Statements (6 months)", "ITR Acknowledgement"])
    if "home" in request.product_id.lower():
        docs.extend(["Property Documents", "NOC from Builder"])
    
    return {
        "product_id": request.product_id,
        "required_documents": docs
    }

@app.post("/tools/check_dti_limit", response_model=DTILimitResponse, tags=["Tools"])
async def check_dti_limit(request: DTILimitRequest):
    # This tool would ideally call Credit MCP
    # For simplicity, we'll mock the check
    # Let's assume most customers are within limit unless they have a specific simulated ID
    dti = 0.35
    if request.customer_id == "high_risk_dti":
        dti = 0.65
        
    return {
        "customer_id": request.customer_id,
        "within_limit": dti <= 0.5,
        "current_dti": dti,
        "max_allowed_dti": 0.5
    }

# --- Health Check ---

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8104)
