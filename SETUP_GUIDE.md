# Setup & Deployment Guide - FinCore Intelligent Banking Assistant

Complete step-by-step guide for setting up, configuring, and deploying the FinCore Banking Assistant system.

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Environment Setup](#environment-setup)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Production Deployment](#production-deployment)

---

## System Requirements

### Minimum Specifications

| Component | Requirement |
|-----------|------------|
| **OS** | Linux, macOS, or Windows (with WSL2) |
| **Python** | 3.10 or higher |
| **Node.js** | 18 or higher |
| **npm** | 9 or higher |
| **RAM** | 4 GB minimum (8 GB recommended) |
| **Disk** | 2 GB free space |
| **Internet** | Required for Google Gemini API |

### Recommended Specifications

```
OS:        Ubuntu 22.04 LTS
Python:    3.11.4
Node.js:   20.9.0
npm:       10.1.0
RAM:       8 GB
CPU:       4 cores
Storage:   20 GB SSD
```

### Supported Platforms

- ✅ Ubuntu 20.04+
- ✅ macOS 12+
- ✅ Windows 10/11 (with WSL2)
- ✅ Docker (any OS)

---

## Environment Setup

### 1.1 Install Python 3.10+

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip
python3.10 --version
```

#### macOS

```bash
brew install python@3.10
python3.10 --version
```

#### Windows (with WSL2)

```bash
wsl --install
# Then in WSL2 terminal:
sudo apt update
sudo apt install -y python3.10 python3.10-venv
```

### 1.2 Install Node.js & npm

#### Ubuntu/Debian

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node --version && npm --version
```

#### macOS

```bash
brew install node
node --version && npm --version
```

#### Windows

Download from https://nodejs.org/en/download/

### 1.3 Install Git

#### Ubuntu/Debian

```bash
sudo apt install -y git
```

#### macOS

```bash
brew install git
```

#### Windows

Download from https://git-scm.com/download/win

---

## Installation

### Step 1: Clone/Navigate to Project

```bash
# Navigate to the project directory
cd "/home/labuser/Intelligent Banking Assistant (copy 1)/fincore-intelligent-banking-assistant"

# Or if setting up from scratch:
cd ~/projects
git clone <repository-url>
cd fincore-intelligent-banking-assistant
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify activation (should show "venv" prefix)
python --version
pip --version
```

### Step 3: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install project dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, langchain, langgraph; print('✅ Python packages OK')"
```

### Step 4: Install Frontend Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install npm packages
npm install

# Verify installation
npm list react

# Return to project root
cd ..
```

### Step 5: Verify Complete Installation

```bash
# Run comprehensive verification
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

print("=" * 60)
print("INSTALLATION VERIFICATION")
print("=" * 60)

# Check Python version
import platform
print(f"✅ Python {platform.python_version()}")

# Check critical packages
packages = [
    ('fastapi', 'FastAPI'),
    ('fastapi.applications', 'FastAPI Application'),
    ('langchain', 'LangChain'),
    ('langgraph', 'LangGraph'),
    ('pydantic', 'Pydantic'),
    ('dotenv', 'python-dotenv'),
]

for package, name in packages:
    try:
        __import__(package)
        print(f"✅ {name}")
    except ImportError as e:
        print(f"❌ {name}: {e}")

# Check backend modules
modules = [
    ('app', 'FastAPI Application'),
    ('config.llm', 'LLM Configuration'),
    ('graph.main_graph', 'LangGraph Workflow'),
    ('kg.engine', 'Knowledge Graph Engine'),
    ('vector_store.loader', 'Vector Store Loader'),
]

print("\nBackend Modules:")
for module, description in modules:
    try:
        __import__(module)
        print(f"✅ {description}")
    except Exception as e:
        print(f"❌ {description}: {e}")

print("=" * 60)
print("Installation verification complete!")
print("=" * 60)
EOF
```

---

## Configuration

### Step 1: Environment Variables

The project uses a `.env` file for configuration:

```bash
# View current configuration
cat .env

# Edit if needed
nano .env  # or vim, code, etc.
```

### Step 2: .env File Contents

```ini
# Google AI API Configuration
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Database Configuration
APP_DB_BACKEND=sqlite
KG_BACKEND=networkx

# Storage Configuration
VECTOR_DB_PATH=./data/vector/chroma
SQLITE_PATH=./audit.db

# Optional: LLM Parameters (defaults below)
# LLM_TEMPERATURE=0.2
# LLM_MAX_TOKENS=2048
```

### Step 3: Get Google API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key
5. Update the `GOOGLE_API_KEY` in your `.env` file

⚠️ **IMPORTANT**: Never commit `.env` to version control!

### Step 4: Verify Configuration

```bash
# Check if .env is properly loaded
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
if api_key and api_key != 'your_api_key_here':
    print('✅ GOOGLE_API_KEY is configured')
else:
    print('❌ GOOGLE_API_KEY is not properly configured')
"

# Test LLM initialization
python3 -c "
import sys
sys.path.insert(0, 'src')
from config.llm import get_llm
try:
    llm = get_llm()
    print('✅ LLM initialized successfully')
    print(f'Model: {llm.model_name}')
except Exception as e:
    print(f'❌ LLM initialization failed: {e}')
"
```

---

## Running the Application

### Option 1: All-in-One Startup (Recommended for Development)

```bash
# Make startup script executable
chmod +x scripts/start_all.sh

# Start all services
./scripts/start_all.sh

# Output should show:
# Stopping existing services...
# Loaded environment from .env file
# Starting MCP Servers...
# Starting Backend...
# Starting Frontend...
# All services started!

# Wait for services to initialize (10-15 seconds)
sleep 15

# Verify services are running
echo "Checking service status..."
ps aux | grep -E "python.*mcp|uvicorn|npm run dev" | grep -v grep

# Check backend is responding
curl -s http://localhost:8080/customers | head -20

# Open in browser
echo "Frontend: http://localhost:5173"
echo "Backend: http://localhost:8080"
```

### Option 2: Manual Component Startup

Recommended for debugging or when you need to restart individual services.

#### Terminal 1: Core Banking MCP

```bash
cd "/home/labuser/Intelligent Banking Assistant (copy 1)/fincore-intelligent-banking-assistant"
export PYTHONPATH=$(pwd)/src
python src/mcp_servers/core_banking_mcp.py
# Should show: INFO:     Uvicorn running on http://0.0.0.0:8101
```

#### Terminal 2: Credit MCP

```bash
cd "/home/labuser/Intelligent Banking Assistant (copy 1)/fincore-intelligent-banking-assistant"
export PYTHONPATH=$(pwd)/src
python src/mcp_servers/credit_mcp.py
# Should show: INFO:     Uvicorn running on http://0.0.0.0:8102
```

#### Terminal 3: Fraud MCP

```bash
cd "/home/labuser/Intelligent Banking Assistant (copy 1)/fincore-intelligent-banking-assistant"
export PYTHONPATH=$(pwd)/src
python src/mcp_servers/fraud_mcp.py
# Should show: INFO:     Uvicorn running on http://0.0.0.0:8103
```

#### Terminal 4: Compliance MCP

```bash
cd "/home/labuser/Intelligent Banking Assistant (copy 1)/fincore-intelligent-banking-assistant"
export PYTHONPATH=$(pwd)/src
python src/mcp_servers/compliance_mcp.py
# Should show: INFO:     Uvicorn running on http://0.0.0.0:8104
```

#### Terminal 5: Backend

```bash
cd "/home/labuser/Intelligent Banking Assistant (copy 1)/fincore-intelligent-banking-assistant"
export PYTHONPATH=$(pwd)/src
uvicorn src.app:app --host 0.0.0.0 --port 8080 --reload
# Should show: INFO:     Uvicorn running on http://0.0.0.0:8080
```

#### Terminal 6: Frontend

```bash
cd "/home/labuser/Intelligent Banking Assistant (copy 1)/fincore-intelligent-banking-assistant/frontend"
npm run dev -- --host 0.0.0.0 --port 5173
# Should show: VITE v8.0.0  ready in XXX ms
```

### Option 3: Production Mode

```bash
# Build frontend
cd frontend
npm run build
cd ..

# Start backend (no hot reload, multiple workers)
export PYTHONPATH=$(pwd)/src
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.app:app --bind 0.0.0.0:8080

# Or use uvicorn directly:
uvicorn src.app:app --host 0.0.0.0 --port 8080 --workers 4

# Serve frontend (example with Python)
cd frontend/dist
python -m http.server 5173
```

### Option 4: Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Testing

### 1. Test Backend API

```bash
# 1. Get customers list
curl -X GET http://localhost:8080/customers \
  -H "Accept: application/json"

# 2. Test MCP server (Core Banking)
curl -X POST http://localhost:8101/tools/get_balance \
  -H "Content-Type: application/json" \
  -d '{"account_id": "ACC435073"}'

# 3. Test query endpoint
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-001",
    "query": "What is my account balance?",
    "customer_id": "fa800b9e"
  }'

# 4. Check audit trail
curl -X GET http://localhost:8080/audit/test-001 \
  -H "Accept: application/json"
```

### 2. Test Frontend

```bash
# Open browser and navigate to
http://localhost:5173

# Test workflow:
# 1. Select customer from dropdown
# 2. Type a query: "Show me my accounts"
# 3. Review the response
# 4. Check "Audit Trail" for execution details
# 5. Try different queries:
#    - "What loans can I get?"
#    - "Check for fraud"
#    - "Show my KYC status"
```

### 3. Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_core_banking_mcp.py -v

# Run specific test function
pytest tests/test_core_banking_mcp.py::test_get_customer -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Run integration tests
pytest tests/integration/ -v
```

### 4. Manual Component Testing

```bash
# Test KG Engine
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from kg.engine import get_kg_engine

kg = get_kg_engine()
accounts = kg.get_customer_accounts("fa800b9e")
print(f"Found {len(accounts)} accounts for customer fa800b9e")
for acc in accounts:
    print(f"  - {acc}")
EOF

# Test Vector Store
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from vector_store.loader import get_vectorstore

vs = get_vectorstore()
results = vs.similarity_search("loan eligibility", k=2)
print(f"Found {len(results)} documents")
for doc in results:
    print(f"  - {doc.page_content[:100]}...")
EOF
```

---

## Troubleshooting

### Issue: Port Already in Use

```bash
# Find process using port 8080
lsof -i :8080
# or
netstat -tulpn | grep 8080

# Kill the process
kill -9 <PID>
# or
pkill -f "uvicorn.*8080"
```

### Issue: Python Module Not Found

```bash
# Make sure PYTHONPATH is set
export PYTHONPATH=$(pwd)/src

# Test import
python -c "from app import app; print('OK')"
```

### Issue: API Key Not Working

```bash
# Check if .env file exists
ls -la .env

# Verify API key is set
echo $GOOGLE_API_KEY

# If not set, source the .env file
set -a
source .env
set +a

# Test LLM
python3 -c "
import sys
sys.path.insert(0, 'src')
from config.llm import get_llm
llm = get_llm()
print('✅ LLM initialized')
"
```

### Issue: Frontend Not Connecting to Backend

```bash
# 1. Check backend is running
curl http://localhost:8080/customers

# 2. Check frontend settings
# In browser console, type:
localStorage.getItem('apiBaseUrl')
# Should return: http://localhost:8080

# 3. Use Settings modal to configure
# Click Settings (gear icon) in frontend
# Update Backend URL to: http://localhost:8080

# 4. Check browser console for CORS errors
# Right-click → Inspect → Console tab
```

### Issue: Database Errors

```bash
# Check database files exist
ls -la data/

# Verify vector store
ls -la data/vector/chroma/

# Reset database (removes audit trail)
rm -f audit.db
rm -rf data/vector/chroma/

# Re-initialize
python3 -c "
import sys
sys.path.insert(0, 'src')
from graph.state import SqliteAuditStore
store = SqliteAuditStore()
print('✅ Database initialized')
"
```

### Issue: MCP Server Not Starting

```bash
# Check specific MCP server
python src/mcp_servers/core_banking_mcp.py

# Should show:
# INFO:     Uvicorn running on http://0.0.0.0:8101

# If error, check:
# 1. Port is available: lsof -i :8101
# 2. Data files exist: ls data/seed/mcp/
# 3. All imports work: python -c "from mcp_servers.core_banking_mcp import app"
```

### Issue: Frontend Build Fails

```bash
# Clean and rebuild
cd frontend
rm -rf node_modules dist
npm install
npm run build

# If still failing:
npm run build -- --debug

# Check Node/npm versions
node --version
npm --version
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Update `.env` with production API key
- [ ] Set `GEMINI_MODEL` to production model
- [ ] Disable debug mode
- [ ] Enable HTTPS/SSL
- [ ] Configure database (PostgreSQL instead of SQLite)
- [ ] Set up monitoring/logging
- [ ] Configure backups
- [ ] Test all endpoints
- [ ] Review security settings
- [ ] Set up CI/CD pipeline

### 1. Docker Deployment

```bash
# Build Docker images
docker build -f Dockerfile.backend -t fincore-backend:latest .
cd frontend && docker build -f Dockerfile -t fincore-frontend:latest .

# Tag for registry
docker tag fincore-backend:latest myregistry.azurecr.io/fincore-backend:latest
docker push myregistry.azurecr.io/fincore-backend:latest
```

### 2. Kubernetes Deployment

```bash
# Create ConfigMap for environment
kubectl create configmap fincore-config --from-env-file=.env

# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml

# Expose services
kubectl apply -f k8s/services.yaml

# Check status
kubectl get pods
kubectl get svc
```

### 3. Cloud Platform Deployment

#### AWS

```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Deploy to ECS
aws ecs create-service --cluster fincore --service-name backend ...
```

#### Google Cloud

```bash
# Deploy to Cloud Run
gcloud run deploy fincore-backend \
  --image gcr.io/PROJECT_ID/fincore-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=xxx
```

#### Azure

```bash
# Deploy to Container Instances
az container create \
  --resource-group fincore \
  --name backend \
  --image myregistry.azurecr.io/fincore-backend:latest
```

### 4. SSL/TLS Certificate

```bash
# Using Let's Encrypt with Certbot
sudo certbot certonly --standalone -d yourdomain.com

# Configure nginx to use certificate
# Update nginx config to use:
# ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

### 5. Monitoring & Logging

```bash
# Install monitoring tools
pip install prometheus-client
pip install python-json-logger

# Set up log aggregation
# Example: ELK Stack, Datadog, or CloudWatch
```

### 6. Backup Strategy

```bash
# Backup database
pg_dump fincore > backup.sql

# Backup vector store
tar -czf chroma-backup.tar.gz data/vector/chroma/

# Schedule automated backups
# Example cron job:
# 0 2 * * * /backup/backup.sh
```

---

## Performance Tuning

### Backend Optimization

```bash
# Enable uvicorn workers
uvicorn src.app:app --workers 4 --loop uvloop

# Enable caching
# See config for caching strategies

# Database optimization
# Add indexes, query optimization
```

### Frontend Optimization

```bash
# Build with optimization
npm run build -- --optimize

# Enable compression
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

### System Optimization

```bash
# Increase file descriptors
ulimit -n 65536

# Tune network buffers
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.wmem_max=134217728
```

---

## Security Hardening

### 1. API Authentication

```python
# Add JWT authentication
from fastapi.security import HTTPBearer, HTTPAuthCredential
security = HTTPBearer()

@app.post("/query")
async def query(request: QueryRequest, credentials: HTTPAuthCredential = Depends(security)):
    # Verify token
    pass
```

### 2. Rate Limiting

```python
# Add slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/query")
@limiter.limit("10/minute")
async def query(request: QueryRequest):
    pass
```

### 3. Input Validation

```python
# Validate and sanitize inputs
from pydantic import BaseModel, validator

class QueryRequest(BaseModel):
    query: str
    
    @validator('query')
    def validate_query(cls, v):
        if len(v) > 1000:
            raise ValueError('Query too long')
        return v.strip()
```

### 4. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

**Last Updated**: March 13, 2026  
**Version**: 1.0.0

