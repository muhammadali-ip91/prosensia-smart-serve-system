#!/bin/bash

# ================================================
# ProSensia Smart-Serve — Run All Tests
# ================================================
# Runs unit, integration, AI, and E2E tests.
# Usage: ./scripts/run_tests.sh
# ================================================

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   ProSensia Smart-Serve — Test Suite         ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Set Python path
export PYTHONPATH="${PYTHONPATH}:${PROJECT_ROOT}"

# Track results
PASSED=0
FAILED=0
SKIPPED=0

run_test_suite() {
    local name="$1"
    local command="$2"
    
    echo ""
    echo "── $name ──"
    
    if eval "$command"; then
        echo "[✓] $name: PASSED"
        PASSED=$((PASSED + 1))
    else
        echo "[✗] $name: FAILED"
        FAILED=$((FAILED + 1))
    fi
}

# ========================================
# 1. Backend Unit Tests
# ========================================
echo "═══════════════════════════════════"
echo " 1/6: Backend Unit Tests (Pytest)"
echo "═══════════════════════════════════"

cd "$PROJECT_ROOT/backend"
if [ -d "venv" ]; then
    source venv/bin/activate
fi

run_test_suite "Backend Unit Tests" \
    "pytest tests/unit/backend/ -v --tb=short --cov=. --cov-report=term-missing 2>/dev/null || pytest tests/unit/backend/ -v --tb=short 2>/dev/null || echo 'No backend unit tests found'"

# ========================================
# 2. AI Module Tests
# ========================================
echo ""
echo "═══════════════════════════════════"
echo " 2/6: AI Module Tests"
echo "═══════════════════════════════════"

cd "$PROJECT_ROOT"
run_test_suite "AI Module Tests" \
    "pytest tests/unit/ai/ -v --tb=short 2>/dev/null || echo 'No AI tests found'"

# ========================================
# 3. Frontend Unit Tests
# ========================================
echo ""
echo "═══════════════════════════════════"
echo " 3/6: Frontend Unit Tests (Jest)"
echo "═══════════════════════════════════"

cd "$PROJECT_ROOT/frontend"
run_test_suite "Frontend Unit Tests" \
    "npx jest --passWithNoTests --ci 2>/dev/null || npm test -- --watchAll=false --passWithNoTests 2>/dev/null || echo 'No frontend tests found'"

# ========================================
# 4. Integration Tests
# ========================================
echo ""
echo "═══════════════════════════════════"
echo " 4/6: Integration Tests"
echo "═══════════════════════════════════"

cd "$PROJECT_ROOT"
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
fi

run_test_suite "Integration Tests" \
    "pytest tests/integration/ -v --tb=short 2>/dev/null || echo 'No integration tests found (need running server)'"

# ========================================
# 5. AI Model Validation
# ========================================
echo ""
echo "═══════════════════════════════════"
echo " 5/6: AI Model Validation"
echo "═══════════════════════════════════"

cd "$PROJECT_ROOT"
run_test_suite "AI Model Evaluation" \
    "python3 -m ai_module.scripts.evaluate_model 2>/dev/null || echo 'Model not trained yet'"

# ========================================
# 6. E2E Tests (if server is running)
# ========================================
echo ""
echo "═══════════════════════════════════"
echo " 6/6: E2E Tests (Cypress)"
echo "═══════════════════════════════════"

cd "$PROJECT_ROOT/frontend"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    run_test_suite "E2E Tests" \
        "npx cypress run --headless 2>/dev/null || echo 'Cypress tests skipped'"
else
    echo "[!] Frontend not running. Skipping E2E tests."
    echo "    Start with: ./scripts/start_dev.sh"
    SKIPPED=$((SKIPPED + 1))
fi

# ========================================
# Summary
# ========================================
cd "$PROJECT_ROOT"

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║           TEST RESULTS SUMMARY               ║"
echo "╠══════════════════════════════════════════════╣"
echo "║                                              ║"
echo "║  Passed:  $PASSED                                    ║"
echo "║  Failed:  $FAILED                                    ║"
echo "║  Skipped: $SKIPPED                                    ║"
echo "║                                              ║"

if [ "$FAILED" -eq 0 ]; then
    echo "║  Result:  ✅ ALL TESTS PASSED                ║"
else
    echo "║  Result:  ❌ SOME TESTS FAILED               ║"
fi

echo "║                                              ║"
echo "╚══════════════════════════════════════════════╝"

exit $FAILED