#!/bin/bash

# FinCore Intelligent Banking Assistant - Verification Script
# This script verifies all components are properly configured and working

set -e

echo "======================================================================"
echo "FinCore Intelligent Banking Assistant - System Verification"
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Function to check command
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅${NC} $1 is installed"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌${NC} $1 is NOT installed"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Function to check file
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $1 exists"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌${NC} $1 NOT found"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Function to check Python package
check_python_package() {
    if python3 -c "import $1" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} Python package '$1' is installed"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌${NC} Python package '$1' is NOT installed"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "1. SYSTEM REQUIREMENTS"
echo "────────────────────────────────────────────────────────────────────"
check_command python3
check_command node
check_command npm
echo ""

echo "2. PROJECT FILES"
echo "────────────────────────────────────────────────────────────────────"
check_file ".env"
check_file "requirements.txt"
check_file "README.md"
check_file ".gitignore"
check_file "scripts/start_all.sh"
echo ""

echo "3. SOURCE CODE STRUCTURE"
echo "────────────────────────────────────────────────────────────────────"
check_file "src/app.py"
check_file "src/config/llm.py"
check_file "src/graph/main_graph.py"
check_file "src/kg/engine.py"
check_file "src/vector_store/loader.py"
check_file "frontend/package.json"
echo ""

echo "4. DATA FILES"
echo "────────────────────────────────────────────────────────────────────"
check_file "data/seed/kg_nodes.jsonl"
check_file "data/seed/kg_edges.jsonl"
check_file "data/seed/mcp/core_banking.json"
check_file "data/seed/mcp/credit.json"
check_file "data/seed/mcp/fraud.json"
check_file "data/seed/mcp/compliance.json"
echo ""

echo "5. PYTHON DEPENDENCIES"
echo "────────────────────────────────────────────────────────────────────"
check_python_package "fastapi"
check_python_package "uvicorn"
check_python_package "pydantic"
check_python_package "langchain"
check_python_package "langgraph"
check_python_package "chromadb"
check_python_package "networkx"
echo ""

echo "6. FRONTEND DEPENDENCIES"
echo "────────────────────────────────────────────────────────────────────"
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✅${NC} Node modules installed"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️${NC} Node modules not installed (run: cd frontend && npm install)"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "7. PYTHON IMPORTS TEST"
echo "────────────────────────────────────────────────────────────────────"
if python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from app import app
    from graph.main_graph import app as graph_app
    from kg.engine import get_kg_engine
    from vector_store.loader import get_vectorstore
    from config.llm import get_llm
    print('✅ All critical imports successful')
    exit(0)
except Exception as e:
    print(f'❌ Import failed: {e}')
    exit(1)
" 2>/dev/null; then
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌${NC} Python imports failed"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "8. CONFIGURATION"
echo "────────────────────────────────────────────────────────────────────"
if grep -q "GOOGLE_API_KEY=" .env; then
    echo -e "${GREEN}✅${NC} GOOGLE_API_KEY is configured"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️${NC} GOOGLE_API_KEY not found in .env"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "9. FRONTEND BUILD TEST"
echo "────────────────────────────────────────────────────────────────────"
if [ -d "frontend/dist" ]; then
    echo -e "${GREEN}✅${NC} Frontend build exists (dist/)"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠️${NC} Frontend build not found (run: cd frontend && npm run build)"
fi
echo ""

echo "======================================================================"
echo "SUMMARY"
echo "======================================================================"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All verification checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Install frontend dependencies (if not done):"
    echo "   cd frontend && npm install && cd .."
    echo ""
    echo "2. Build frontend (if not done):"
    echo "   cd frontend && npm run build && cd .."
    echo ""
    echo "3. Start all services:"
    echo "   chmod +x scripts/start_all.sh"
    echo "   ./scripts/start_all.sh"
    echo ""
    echo "4. Access the application:"
    echo "   Frontend: http://localhost:5173"
    echo "   Backend: http://localhost:8080"
    exit 0
else
    echo -e "${RED}❌ Some verification checks failed!${NC}"
    echo ""
    echo "Please resolve the above issues before running the application."
    exit 1
fi
