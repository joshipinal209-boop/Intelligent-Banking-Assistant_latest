#!/bin/bash

# Kill all existing processes on potential ports
echo "Stopping existing services..."
fuser -k 8080/tcp 2>/dev/null
fuser -k 8101/tcp 2>/dev/null
fuser -k 8102/tcp 2>/dev/null
fuser -k 8103/tcp 2>/dev/null
fuser -k 8104/tcp 2>/dev/null
fuser -k 5173/tcp 2>/dev/null
fuser -k 5174/tcp 2>/dev/null

# Load environment variables from .env file
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "Loaded environment from .env file"
else
    echo "WARNING: .env file not found in $(pwd)"
    echo "Make sure GOOGLE_API_KEY is set in your environment"
fi

export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Start MCP Servers
echo "Starting MCP Servers..."
nohup python src/mcp_servers/core_banking_mcp.py > core.log 2>&1 &
nohup python src/mcp_servers/credit_mcp.py > credit.log 2>&1 &
nohup python src/mcp_servers/fraud_mcp.py > fraud.log 2>&1 &
nohup python src/mcp_servers/compliance_mcp.py > compliance.log 2>&1 &

# Wait for MCPs
sleep 3

# Start Backend
echo "Starting Backend..."
nohup uvicorn src.app:app --host 0.0.0.0 --port 8080 > app.log 2>&1 &

# Wait for Backend
sleep 5

# Start Frontend
echo "Starting Frontend..."
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 5173 > ../frontend.log 2>&1 &

echo "All services started!"
echo "Backend: http://localhost:8080"
echo "Frontend: http://localhost:5173"
echo "Check logs for details."
