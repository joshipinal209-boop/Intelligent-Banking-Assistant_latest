# 🚀 QUICK START - Get FinCore Banking Assistant Running

## Prerequisites Checklist
- ✅ Python 3.10+ installed
- ✅ Node.js 18+ installed  
- ✅ Google Gemini API key configured (AIzaSyD7raY4ST1voy1ENfU6rp2jV6JiCwqlqOY)
- ✅ .env file created with API key

---

## Option 1: Start All Services (Recommended)

### Step 1: Navigate to Project
```bash
cd "fincore-intelligent-banking-assistant"
```

### Step 2: Run Start Script
```bash
./scripts/start_all.sh
```

This will automatically:
- ✅ Start MCP servers (ports 8101-8104)
- ✅ Start FastAPI backend (port 8000)
- ✅ Start React frontend (port 5173)
- ✅ Load knowledge graph data
- ✅ Initialize vector store

**Expected Output:**
```
Starting FinCore Banking Assistant...
✅ MCP Core Banking Server on port 8101
✅ MCP Credit Server on port 8102
✅ MCP Fraud Server on port 8103
✅ MCP Compliance Server on port 8104
✅ FastAPI Server on port 8000
✅ React Frontend on port 5173
```

### Step 3: Access the System
- **API Documentation**: http://localhost:8000/docs
- **Frontend Application**: http://localhost:5173

---

## Option 2: Start Services Individually

### Start Backend API
```bash
# Terminal 1 - Backend Server
cd fincore-intelligent-banking-assistant
python src/app.py
# or
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
# Terminal 2 - Frontend
cd frontend
npm install  # Only needed first time
npm run dev
```

### Start MCP Servers (Optional)
```bash
# Terminal 3 - MCP Servers
cd fincore-intelligent-banking-assistant
python src/mcp_servers/core_banking_mcp.py &
python src/mcp_servers/credit_mcp.py &
python src/mcp_servers/fraud_mcp.py &
python src/mcp_servers/compliance_mcp.py &
```

---

## First Login Experience

### Step 1: Register New User

**Using API Documentation (Easiest)**:
1. Go to http://localhost:8000/docs
2. Click "Authorize" (top right)
3. Find POST `/auth/register` endpoint
4. Click "Try it out"
5. Fill in:
   ```json
   {
     "email": "user@example.com",
     "username": "testuser",
     "full_name": "Test User",
     "password": "Password123!"
   }
   ```
6. Click "Execute"

**Using cURL**:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "Password123!"
  }'
```

### Step 2: Login

**Using API Documentation**:
1. Find POST `/auth/login` endpoint
2. Click "Try it out"
3. Fill in:
   ```json
   {
     "username": "testuser",
     "password": "Password123!"
   }
   ```
4. Click "Execute"
5. Copy the `access_token` from response

**Using cURL**:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Password123!"
  }' | jq '.access_token'
```

### Step 3: Get User Info

**Using cURL**:
```bash
# Save token in variable
TOKEN="<paste_your_access_token_here>"

curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "testuser",
  "email": "user@example.com",
  "full_name": "Test User",
  "is_active": true,
  "is_admin": false
}
```

---

## Common Commands

### Check if Services are Running
```bash
# Check API
curl http://localhost:8000/health

# Check Frontend
curl http://localhost:5173

# Check MCP Servers
netstat -tuln | grep -E '810[1-4]'
```

### View Logs
```bash
# Backend logs
tail -f logs/fincore.log

# Frontend logs (in terminal 2)
# Visible in the terminal where you ran npm run dev
```

### Test API Endpoint

```bash
# Get customers (requires token)
curl -X GET "http://localhost:8000/customers" \
  -H "Authorization: Bearer $TOKEN"

# Process query (requires token)
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-1",
    "customer_id": "fa800b9e",
    "query": "What is my account balance?"
  }'
```

---

## Troubleshooting

### Issue: Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python src/app.py --port 8001
```

### Issue: API Key Not Working
```bash
# Verify API key in .env
cat .env | grep GOOGLE_API_KEY

# Check if google-generativeai is installed
python -c "import google.generativeai; print('✅ Package installed')"
```

### Issue: Frontend Won't Load
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

### Issue: Authentication Errors
```bash
# Check if JWT_SECRET_KEY is set
python -c "import os; print(os.getenv('JWT_SECRET_KEY', 'NOT SET'))"

# Check database
sqlite3 data/app_state.sqlite ".tables"
```

---

## Testing All Features

### Test Registration & Login Flow
```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# 1. Register
echo "📝 Registering user..."
REGISTER=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@fincore.com",
    "username": "testuser",
    "password": "TestPassword123!"
  }')

echo "✅ User registered"

# 2. Login
echo "🔑 Logging in..."
LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPassword123!"
  }')

TOKEN=$(echo $LOGIN | jq -r '.access_token')
echo "✅ Login successful, token: ${TOKEN:0:20}..."

# 3. Get user info
echo "👤 Fetching user info..."
curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo "✅ All tests passed!"
```

Save as `test_auth.sh` and run:
```bash
chmod +x test_auth.sh
./test_auth.sh
```

---

## Next Steps After Starting

1. **Test the API**: Visit http://localhost:8000/docs
2. **Create a user**: Register and login
3. **Test queries**: Submit banking queries
4. **View audit logs**: Check audit trail
5. **Check metrics**: View system metrics
6. **Explore frontend**: Open http://localhost:5173

---

## Production Deployment

For production deployment, see:
- `DEPLOYMENT.md` - Full deployment guide
- `DEPLOYMENT_VERIFICATION.md` - Pre-deployment checklist
- `README.md` - Complete documentation

---

## Support

- **API Documentation**: http://localhost:8000/docs (when running)
- **Guide**: See `REGISTRATION_LOGIN_GUIDE.md`
- **Setup**: See `AUTHENTICATION_SETUP.md`
- **Architecture**: See `docs/architecture_report.md`

---

**Ready? Start with**: `./scripts/start_all.sh` 🚀

