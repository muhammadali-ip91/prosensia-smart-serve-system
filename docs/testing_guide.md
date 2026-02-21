# 🧪 ProSensia Smart-Serve — Testing Guide

---

## Testing Pyramid
text

     /\
    / E2E \           10% — Cypress
   /────────\
  / Integration \     30% — Pytest
 /────────────────\
/    Unit Tests     \ 50% — Pytest + Jest
/────────────────────
/ AI + Load Testing \ 10% — Custom scripts
/────────────────────────\

text


---

## Running All Tests

```bash
# Run everything
./scripts/run_tests.sh

# Or individually:
Backend Unit Tests (Pytest)
Bash

cd backend
pytest tests/unit/backend/ -v --cov=. --cov-report=term-missing
Frontend Unit Tests (Jest)
Bash

cd frontend
npm test
npm test -- --coverage
Integration Tests
Bash

cd backend
pytest tests/integration/ -v
End-to-End Tests (Cypress)
Bash

cd frontend
npx cypress open          # Interactive mode
npx cypress run           # Headless mode
AI Model Tests
Bash

pytest tests/unit/ai/ -v
Load Testing
Bash

# Quick test (10 engineers, 30 orders)
python -m automation.load_testing.load_simulator --quick

# Full test (100 engineers, 1000 orders)
python -m automation.load_testing.load_simulator

# Locust (professional)
locust -f automation/load_testing/locustfile.py
# Open http://localhost:8089
Test Coverage Targets
Module	Target
Backend	> 80%
Frontend	> 70%
AI Module	> 75%
Overall	> 80%
text
