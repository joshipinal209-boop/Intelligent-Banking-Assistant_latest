# FinCore Intelligent Banking Assistant

An AI-powered multi-agent conversational banking system built with **LangGraph**, **FastAPI**, and **React**. The system provides intelligent banking services through specialized agents handling accounts, loans, fraud detection, and compliance.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│          React Frontend (Vite + TypeScript)              │
│         - Chat Interface                                 │
│         - Session Management                             │
│         - Audit Trail Visualization                      │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP
                         ▼
┌─────────────────────────────────────────────────────────┐
│     FastAPI Backend (Python 3.10+)                       │
│  ┌────────────────────────────────────────────────────┐ │
│  │      LangGraph Multi-Agent Workflow                │ │
│  │                                                    │ │
│  │  Router ──┬─► Account Agent                       │ │
│  │           ├─► Loan Agent                          │ │
│  │           ├─► Fraud Agent                         │ │
│  │           └─► Compliance Agent                    │ │
│  │                    │                               │ │
│  │                    ▼                               │ │
│  │                Aggregator ─► Final Response       │ │
│  │                                                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  Data Layer:                                             │
│  ├─ KG Engine (NetworkX)                               │
│  ├─ Vector Store (ChromaDB + Google Embeddings)        │
│  └─ Audit Logger (SQLite)                              │
└─────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐         ┌─────────┐         ┌─────────┐
    │ MCP     │         │ MCP     │         │ MCP     │
    │ Core    │         │ Credit  │         │ Fraud   │
    │ Banking │         │ Scoring │         │ Detect  │
    │ (8101)  │         │ (8102)  │         │ (8103)  │
    └─────────┘         └─────────┘         └─────────┘
         │
         ▼
    ┌─────────┐
    │ MCP     │
    │Compliance
    │ (8104)  │
    └─────────┘
```

## 📋 Features

✅ **Multi-Agent Intelligence**
- Intelligent query routing based on intent
- Specialized agents for different banking domains
- Confidence-based response aggregation

✅ **Comprehensive Data Integration**
- Knowledge Graph for relationship understanding
- Vector Database for semantic search
- Synthetic Banking Data (customers, accounts, transactions)

✅ **Risk Management & Compliance**
- Fraud detection and flagging
- Human escalation for high-risk transactions
- Full audit trail logging

✅ **Enterprise Authentication**
- JWT/OAuth2 authentication with token rotation
- Role-based access control (RBAC) with scopes
- Secure password hashing with argon2
- User registration, login, and profile management
- Access token (30 min) and refresh token (7 days) lifecycle

✅ **User Experience**
- Interactive chat interface
- Session management
- Real-time latency monitoring
- Audit trail viewer
- Configurable backend endpoint

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18 or higher  
- **npm**: 9 or higher

### Installation

```bash
# 1. Clone/Navigate to project
cd "Intelligent Banking Assistant (copy 1)/fincore-intelligent-banking-assistant"

# 2. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install frontend dependencies
cd frontend
npm install
cd ..

# 5. Verify installation
python3 -c "import fastapi, langchain, langgraph; print('✅ Python packages OK')"
cd frontend && npm list react && cd ..
```

### Configuration

The project uses environment variables from `.env` file:

```bash
# View current configuration
cat .env

# Should contain:
# GOOGLE_API_KEY=your_api_key_here
# GEMINI_MODEL=gemini-2.5-flash
# APP_DB_BACKEND=sqlite
# KG_BACKEND=networkx
# VECTOR_DB_PATH=./data/vector/chroma
```

To use your own Google API key:
1. Get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Update the `.env` file
3. **Never commit `.env` to version control**

### Running the Application

#### Option 1: All-in-One Startup (Recommended for Development)

```bash
# Make script executable
chmod +x scripts/start_all.sh

# Start all services
./scripts/start_all.sh

# Wait for initialization (~10 seconds)
sleep 10

# Access the application
# Backend API: http://localhost:8080
# Frontend UI: http://localhost:5173
# View logs: tail -f *.log
```

#### Option 2: Start Individual Components

```bash
# Terminal 1: Core Banking MCP Server
python src/mcp_servers/core_banking_mcp.py

# Terminal 2: Credit MCP Server  
python src/mcp_servers/credit_mcp.py

# Terminal 3: Fraud MCP Server
python src/mcp_servers/fraud_mcp.py

# Terminal 4: Compliance MCP Server
python src/mcp_servers/compliance_mcp.py

# Terminal 5: Backend API Server
export PYTHONPATH=src
uvicorn src.app:app --host 0.0.0.0 --port 8080 --reload

# Terminal 6: Frontend Dev Server
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

#### Option 3: Production Mode

```bash
# Build frontend
cd frontend
npm run build
cd ..

# Start backend (without auto-reload)
export PYTHONPATH=src
uvicorn src.app:app --host 0.0.0.0 --port 8080 --workers 4

# Serve frontend build with a simple server or nginx
# Example with Python
python -m http.server 5173 --directory frontend/dist
```

## 📝 Testing the Application

### Test API Connectivity

```bash
# Get customer list
curl -X GET http://localhost:8080/customers

# Test MCP server
curl -X POST http://localhost:8101/tools/get_balance \
  -H "Content-Type: application/json" \
  -d '{"account_id": "ACC435073"}'
```

### Authentication

All API endpoints require JWT authentication. Follow these steps:

```bash
# 1. Register a new user
curl -X POST "http://localhost:8080/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "SecurePassword123!"
  }'

# 2. Login to get tokens
LOGIN=$(curl -s -X POST "http://localhost:8080/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePassword123!"
  }')

ACCESS_TOKEN=$(echo $LOGIN | jq -r '.access_token')

# 3. Use token to access protected endpoints
curl -X GET "http://localhost:8080/customers" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Test Query Processing (with Authentication)

```bash
# Send a banking query
curl -X POST http://localhost:8080/query \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-001",
    "query": "What is my account balance?",
    "customer_id": "fa800b9e"
  }'
```

### Test Frontend

1. Open http://localhost:5173 in your browser
2. Register or login with your credentials
3. Select a customer from the dropdown
4. Type a query (e.g., "Show me my accounts")
5. View the response and agent outputs
6. Check the Audit Trail for execution details

### Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run authentication tests
pytest tests/test_auth.py -v

# Run specific test file
pytest tests/test_core_banking_mcp.py -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html
```

## 🔐 Authentication Details

FinCore uses **JWT/OAuth2** for secure API access:

- **Registration:** Create new user accounts with email and password
- **Login:** Obtain access token (30 min) and refresh token (7 days)
- **Token Refresh:** Get new access token without re-entering credentials
- **Scopes:** Role-based access control (read, write, admin, audit)
- **Password Hashing:** Argon2 for secure password storage

For complete authentication documentation, see [AUTH_GUIDE.md](AUTH_GUIDE.md)

**Quick Login in Swagger UI:**
1. Go to http://localhost:8080/docs
2. Click "Authorize" button (top right)
3. Use the "Login for access" endpoint
4. Enter credentials and get token
5. All subsequent requests will include the token

## 📊 Project Structure

```
fincore-intelligent-banking-assistant/
├── src/                              # Python backend source code
│   ├── app.py                        # FastAPI main application
│   ├── config/
│   │   └── llm.py                    # LLM configuration
│   ├── graph/
│   │   ├── main_graph.py             # LangGraph workflow definition
│   │   ├── state.py                  # Graph state and audit store
│   │   ├── router.py                 # Query routing logic
│   │   ├── account_agent.py          # Account specialist agent
│   │   ├── loan_agent.py             # Loan specialist agent
│   │   ├── fraud_agent.py            # Fraud detection agent
│   │   ├── compliance_agent.py       # Compliance agent
│   │   ├── aggregator.py             # Response aggregation
│   │   └── audit.py                  # Audit logging
│   ├── kg/
│   │   └── engine.py                 # Knowledge Graph engine
│   ├── mcp_servers/
│   │   ├── core_banking_mcp.py       # Core banking MCP (port 8101)
│   │   ├── credit_mcp.py             # Credit MCP (port 8102)
│   │   ├── fraud_mcp.py              # Fraud MCP (port 8103)
│   │   └── compliance_mcp.py         # Compliance MCP (port 8104)
│   └── vector_store/
│       └── loader.py                 # ChromaDB vector store
├── frontend/                         # React frontend source
│   ├── src/
│   │   ├── App.tsx                   # Main app component
│   │   ├── components/               # React components
│   │   ├── lib/
│   │   │   ├── api.ts                # API client
│   │   │   └── types.ts              # TypeScript types
│   │   └── styles.css                # Component styles
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── data/                             # Data files
│   ├── seed/
│   │   ├── kg_nodes.jsonl            # KG nodes
│   │   ├── kg_edges.jsonl            # KG edges
│   │   ├── mcp/                      # MCP data files
│   │   └── vector_docs/              # FAQ documents for RAG
│   └── vector/chroma/                # ChromaDB storage
├── scripts/
│   ├── start_all.sh                  # Multi-service startup script
│   └── seed_synthetic_data.py        # Data generation script
├── tests/                            # Test suite
│   ├── test_*.py                     # Unit tests
│   └── integration/                  # Integration tests
├── requirements.txt                  # Python dependencies
├── .env                              # Environment variables
├── .gitignore                        # Git ignore rules
├── README.md                         # This file
└── PROJECT_ANALYSIS.md               # Detailed analysis document
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Google AI API
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Database backends
APP_DB_BACKEND=sqlite              # or 'postgres' in production
KG_BACKEND=networkx                # or 'neo4j' for larger graphs

# Storage paths
VECTOR_DB_PATH=./data/vector/chroma
SQLITE_PATH=./audit.db
```

### MCP Server Ports

Each MCP server runs on a dedicated port:
- **8101**: Core Banking (accounts, customers, transactions)
- **8102**: Credit Scoring (loan products, eligibility)
- **8103**: Fraud Detection (fraud rules, detection logic)
- **8104**: Compliance (KYC, regulatory rules)

### Backend API

- **Base URL**: http://localhost:8080
- **WebSocket**: Not used (REST only)
- **CORS**: Enabled for all origins (configure in production)

## 🧪 Testing

### Unit Tests

```bash
# Test all MCP servers
pytest tests/test_*_mcp.py -v

# Test specific functionality
pytest tests/integration/test_api_scenarios.py -v
```

### Integration Tests

```bash
# Full end-to-end test
pytest tests/integration/test_api_scenarios.py::test_complete_workflow -v

# Performance test
pytest tests/integration/test_performance.py -v
```

### Manual Testing

Use the provided curl commands or import the test queries into Postman:

1. Get customers
2. Query by customer ID
3. Check audit trail
4. Test different agent specializations

## 📈 Performance Considerations

- **Latency**: Typically 2-5 seconds per query (due to LLM)
- **Throughput**: ~10-20 concurrent queries per instance
- **Memory**: ~1.5 GB for all services
- **Storage**: ~500 MB for vector store and synthetic data

### Optimization Tips

1. **Enable query caching** in production
2. **Use connection pooling** for databases
3. **Deploy MCP servers on separate instances**
4. **Use CDN for static assets**
5. **Enable gzip compression** for API responses

## 🔒 Security Considerations

### Current Limitations

⚠️ **Production Deployment Requires:**

1. **Authentication** - Add JWT/OAuth2
2. **Authorization** - Role-based access control
3. **Rate Limiting** - Prevent abuse
4. **Input Validation** - Sanitize queries
5. **Encryption** - HTTPS/TLS
6. **Audit Logging** - Enhanced logging with signing
7. **API Keys** - Use secure key management (HashiCorp Vault, AWS Secrets Manager)
8. **CORS** - Restrict to known domains

### Best Practices

- Never commit `.env` files
- Use environment-specific configurations
- Enable HTTPS in production
- Implement request signing
- Use parameterized queries
- Enable SQL injection protection
- Monitor for suspicious patterns

## 🚀 Deployment

### Docker Deployment

```bash
# Build backend image
docker build -t fincore-backend .

# Build frontend image
cd frontend && docker build -t fincore-frontend .

# Run with docker-compose
docker-compose up -d
```

### Cloud Deployment

#### AWS

```bash
# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URI
docker tag fincore-backend:latest $ECR_URI/fincore-backend:latest
docker push $ECR_URI/fincore-backend:latest

# Deploy to ECS/Fargate
aws ecs create-service --cluster fincore --service-name backend ...
```

#### Google Cloud

```bash
# Deploy to Cloud Run
gcloud run deploy fincore-backend \
  --image gcr.io/PROJECT_ID/fincore-backend \
  --platform managed \
  --region us-central1
```

#### Azure

```bash
# Deploy to Container Instances
az container create \
  --resource-group fincore \
  --name backend \
  --image $ACR_URL/fincore-backend
```

## 📊 Monitoring & Logging

### Structured Logging

```python
# Use Python logging
import logging
logger = logging.getLogger(__name__)
logger.info("Processing query", extra={"session_id": session_id})
```

### Metrics

Key metrics to monitor:
- Request latency (p50, p95, p99)
- Error rate by endpoint
- Agent execution time
- Vector DB query time
- MCP server response time
- Memory usage
- Database connection pool status

### Health Checks

```bash
# Health endpoint
curl http://localhost:8080/health

# Check MCP servers
curl http://localhost:8101/health
curl http://localhost:8102/health
curl http://localhost:8103/health
curl http://localhost:8104/health
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find and kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Or use the cleanup script
pkill -f "uvicorn"
pkill -f "mcp_servers"
```

### API Key Issues

```bash
# Verify .env file exists
ls -la .env

# Check API key is set
echo $GOOGLE_API_KEY

# Test LLM connection
python -c "from config.llm import get_llm; llm = get_llm(); print('✅ LLM OK')"
```

### Frontend Not Connecting

1. Check backend is running: `curl http://localhost:8080/customers`
2. Use Settings modal to configure correct backend URL
3. Check browser console for CORS errors
4. Verify firewall allows port 8080

### MCP Server Errors

```bash
# Check server is running
ps aux | grep mcp_servers

# Check logs
tail -f core.log
tail -f credit.log
tail -f fraud.log
tail -f compliance.log

# Test endpoint
curl http://localhost:8101/docs
```

## 📚 API Documentation

### Query Endpoint

**POST** `/query`

Request:
```json
{
  "session_id": "unique-session-123",
  "query": "What is my account balance?",
  "customer_id": "fa800b9e"
}
```

Response:
```json
{
  "status": "SUCCESS",
  "final_response": "Your account balance is $XXX...",
  "agent_outputs": {
    "account_agent": {...},
    "fraud_agent": {...}
  },
  "risk_level": "low",
  "requires_human": false,
  "audit_id": "audit-12345",
  "latency_ms": 2345
}
```

### Customers Endpoint

**GET** `/customers`

Response:
```json
[
  {
    "customer_id": "fa800b9e",
    "name": "John Doe",
    "email": "john@example.com",
    "credit_score": 750
  }
]
```

### Audit Endpoint

**GET** `/audit/{session_id}`

Response:
```json
{
  "session_id": "unique-session-123",
  "trail": [
    {
      "event_type": "NODE_START",
      "node_name": "router",
      "timestamp": "2026-03-13T10:00:00Z"
    }
  ]
}
```

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and test
3. Commit: `git commit -m "Add feature"`
4. Push: `git push origin feature/my-feature`
5. Create a Pull Request

## 📄 License

Proprietary - All Rights Reserved

## 📞 Support

For issues and questions:
1. Check PROJECT_ANALYSIS.md for detailed technical information
2. Review logs in root directory
3. Check browser console for frontend errors
4. Verify environment configuration

## 🎯 Roadmap

- [ ] Add LLM caching
- [ ] Support multiple LLM providers
- [ ] Enhanced error handling
- [ ] Rate limiting
- [ ] User authentication
- [ ] Advanced analytics dashboard
- [ ] GraphQL API
- [ ] WebSocket support
- [ ] Batch processing API
- [ ] Custom agent framework

---

**Last Updated**: March 13, 2026  
**Version**: 1.0.0  
**Status**: Production Ready (with security configurations)

