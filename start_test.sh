#!/bin/bash
export PYTHONPATH=src
python src/mcp_servers/core_banking_mcp.py &
PID1=$!
python src/mcp_servers/credit_mcp.py &
PID2=$!
python src/mcp_servers/fraud_mcp.py &
PID3=$!
python src/mcp_servers/compliance_mcp.py &
PID4=$!
python src/app.py &
PID5=$!

sleep 5

curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{"session_id": "test-session-123", "query": "What is my account balance?", "customer_id": "CUST12345"}'
echo -e "\n\n"
curl "http://localhost:8000/metrics"
echo -e "\n\n"

kill $PID1 $PID2 $PID3 $PID4 $PID5
