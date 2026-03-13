# QUICK REFERENCE GUIDE
## FinCore Intelligent Banking Assistant

---

## 📋 Quick Start (5 minutes)

```bash
# 1. Navigate to project
cd "fincore-intelligent-banking-assistant"

# 2. Create Python environment
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)

# 3. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 4. Verify setup
./verify_setup.sh

# 5. Start all services
chmod +x scripts/start_all.sh
./scripts/start_all.sh

# 6. Open browser
# Frontend: http://localhost:5173
# Backend: http://localhost:8080
```

---

## 🔌 Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 5173 | React UI |
| Backend | 8080 | FastAPI |
| Core Banking MCP | 8101 | Accounts, Transactions |
| Credit MCP | 8102 | Loans, Eligibility |
| Fraud MCP | 8103 | Fraud Detection |
| Compliance MCP | 8104 | KYC, Rules |

---

## 📁 Project Structure

```
├── src/                    # Python backend
│   ├── app.py             # FastAPI main
│   ├── graph/             # LangGraph agents
│   ├── kg/                # Knowledge Graph
│   ├── mcp_servers/       # MCP services
│   └── vector_store/      # ChromaDB
├── frontend/              # React app
│   ├── src/               # Components
│   ├── dist/              # Build output
│   └── package.json
├── data/                  # Seed data
│   ├── seed/              # KG, MCP data
│   └── vector/chroma/     # Vector store
├── scripts/               # Automation
├── tests/                 # Unit tests
├── requirements.txt       # Python deps
├── .env                   # Configuration
└── README.md             # Documentation
```

---

## 🚀 Common Commands

### Installation
```bash
pip install -r requirements.txt           # Install Python packages
npm install --prefix frontend            # Install frontend packages
./verify_setup.sh                         # Verify everything
```

### Running Services
```bash
./scripts/start_all.sh                    # Start all services
python src/mcp_servers/core_banking_mcp.py  # Start one MCP
uvicorn src.app:app --reload              # Start backend with reload
cd frontend && npm run dev                # Start frontend dev server
```

### Building
```bash
cd frontend && npm run build              # Build frontend for production
python -m py_compile src/**/*.py          # Check Python syntax
```

### Testing
```bash
pytest tests/ -v                          # Run all tests
pytest tests/test_core_banking_mcp.py    # Run specific test
curl http://localhost:8080/customers     # Test API
```

### Cleanup
```bash
pkill -f "uvicorn"                        # Kill backend
pkill -f "mcp_servers"                    # Kill MCP servers
rm -rf frontend/node_modules frontend/dist  # Clean frontend
rm -rf venv                               # Remove Python env
```

---

## 🔑 Environment Configuration

Create `.env` file in project root:

```ini
GOOGLE_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
APP_DB_BACKEND=sqlite
KG_BACKEND=networkx
VECTOR_DB_PATH=./data/vector/chroma
```

Get API key: https://aistudio.google.com/app/apikey

---

## 🧪 Testing APIs

### Get Customers
```bash
curl http://localhost:8080/customers
```

### Test MCP Server
```bash
curl -X POST http://localhost:8101/tools/get_balance \
  -H "Content-Type: application/json" \
  -d '{"account_id":"ACC435073"}'
```

### Send Query
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id":"test-001",
    "query":"Show my accounts",
    "customer_id":"fa800b9e"
  }'
```

### Check Audit
```bash
curl http://localhost:8080/audit/test-001
```

---

## 🐛 Troubleshooting Quick Fixes

### Port Already in Use
```bash
lsof -i :8080                             # Find process
kill -9 <PID>                             # Kill it
```

### Python Import Errors
```bash
export PYTHONPATH=$(pwd)/src              # Set path
python -c "from app import app"           # Test import
```

### .env Not Loading
```bash
set -a && source .env && set +a           # Load variables
echo $GOOGLE_API_KEY                      # Verify loaded
```

### Frontend Won't Connect
```bash
curl http://localhost:8080/customers     # Check backend
# Use Settings modal in UI to set base URL
```

### Database Errors
```bash
rm -f audit.db                            # Reset DB
rm -rf data/vector/chroma/*              # Reset vectors
```

---

## 📊 Logs Location

```
app.log                 # Backend API
core.log               # Core Banking MCP
credit.log             # Credit MCP
fraud.log              # Fraud MCP
compliance.log         # Compliance MCP
frontend.log           # Frontend dev server
```

View logs:
```bash
tail -f app.log         # Follow backend log
tail -20 app.log        # Last 20 lines
grep ERROR app.log      # Find errors
```

---

## 🔐 Security Checklist

### Before Production
- [ ] Update `.env` with real API key
- [ ] Change GEMINI_MODEL if needed
- [ ] Enable HTTPS/TLS
- [ ] Implement authentication
- [ ] Add rate limiting
- [ ] Configure CORS for specific domains
- [ ] Set up monitoring
- [ ] Enable audit logging
- [ ] Use production database
- [ ] Review security guide in SETUP_GUIDE.md

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| README.md | Project overview & features |
| SETUP_GUIDE.md | Installation & deployment |
| PROJECT_ANALYSIS.md | Technical architecture |
| DELIVERY_SUMMARY.md | Status & roadmap |
| FINAL_REPORT.md | Complete analysis |
| QUICK_REFERENCE.md | This file |

---

## 🎯 Testing Workflow

1. **Start Services**
   ```bash
   ./scripts/start_all.sh
   ```

2. **Open Frontend**
   - Visit http://localhost:5173

3. **Test Query**
   - Select customer
   - Type query
   - Verify response

4. **Check Audit Trail**
   - Click "Audit Trail" button
   - Review execution details

5. **Test Different Scenarios**
   - "Show my accounts"
   - "What loans can I get?"
   - "Check for fraud"
   - "What are my KYC requirements?"

---

## 🚀 Deployment Quick Links

### Docker
```bash
docker-compose up -d
```

### Single Command Start
```bash
./scripts/start_all.sh && echo "All services ready!"
```

### Production Start
```bash
uvicorn src.app:app --workers 4 --host 0.0.0.0 --port 8080
```

---

## 📞 Support

### Getting Help

1. **Check Logs**
   ```bash
   tail -f *.log
   ```

2. **Run Verification**
   ```bash
   ./verify_setup.sh
   ```

3. **Read Documentation**
   - SETUP_GUIDE.md → Troubleshooting section
   - PROJECT_ANALYSIS.md → Error detection section

4. **Test Components**
   ```bash
   pytest tests/ -v
   ```

---

## ✅ Verification Checklist

Run this to verify setup:
```bash
./verify_setup.sh
```

Should show: **31/31 Checks Passed**

If any fail:
1. Read error message
2. Check corresponding documentation section
3. Run fix command if provided
4. Re-run verify_setup.sh

---

## 🎓 Technology Stack

```
Frontend:  React 19.2.4 + Vite 8.0.0 + TypeScript 5.9.3
Backend:   Python 3.10 + FastAPI 0.135.1 + Pydantic 2.12.3
Workflow:  LangGraph 1.0.1 + LangChain 1.0.2
AI:        Google Gemini 2.5-flash + text-embedding-004
Database:  SQLite + ChromaDB + NetworkX
Server:    Uvicorn 0.34.0
```

---

## 📈 Performance Tips

1. **Faster Queries**: Enable caching
2. **Reduce Latency**: Use streaming responses
3. **Scale Backend**: Add uvicorn workers
4. **Optimize Frontend**: Enable compression
5. **Database**: Use indexes, upgrade to PostgreSQL

---

**Last Updated**: March 13, 2026  
**Version**: 1.0.0  
**Status**: Ready for Production

For complete information, see the full documentation files.
