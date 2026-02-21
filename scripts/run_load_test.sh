#!/bin/bash

# ================================================
# ProSensia Smart-Serve — Run Load Test
# ================================================
# Runs load testing against the running server.
# Usage: ./scripts/run_load_test.sh [--quick]
# ================================================

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   ProSensia — Load Testing                   ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Set Python path
export PYTHONPATH="${PYTHONPATH}:${PROJECT_ROOT}"

# Activate virtual environment
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
fi

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend server not running!"
    echo "   Start with: ./scripts/start_dev.sh"
    exit 1
fi

echo "[✓] Backend server is running"
echo ""

# Run load test
if [ "$1" == "--quick" ]; then
    echo "Running QUICK load test (10 engineers, 30 orders)..."
    python3 -m automation.load_testing.load_simulator --quick
else
    echo "Running FULL load test (100 engineers, 1000 orders)..."
    echo "This may take several minutes..."
    python3 -m automation.load_testing.load_simulator
fi

echo ""
echo "[✓] Load test complete! Check automation/reports/ for results."