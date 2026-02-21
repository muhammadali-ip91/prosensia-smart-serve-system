# ================================================
# ProSensia Smart-Serve — Makefile
# ================================================
# Quick commands for common tasks
# Usage: make <command>
# ================================================

.PHONY: help setup start stop test seed train load-test backup clean

# Default target
help:
	@echo "╔══════════════════════════════════════════════╗"
	@echo "║   ProSensia Smart-Serve — Commands           ║"
	@echo "╠══════════════════════════════════════════════╣"
	@echo "║                                              ║"
	@echo "║  make setup      — Initial project setup     ║"
	@echo "║  make start      — Start all services        ║"
	@echo "║  make stop       — Stop all services         ║"
	@echo "║  make test       — Run all tests             ║"
	@echo "║  make seed       — Generate seed data        ║"
	@echo "║  make seed-api   — Seed data via API         ║"
	@echo "║  make train      — Train AI model            ║"
	@echo "║  make load-test  — Run load test             ║"
	@echo "║  make quick-test — Quick load test           ║"
	@echo "║  make backup     — Backup database           ║"
	@echo "║  make docker     — Start with Docker         ║"
	@echo "║  make docker-down— Stop Docker               ║"
	@echo "║  make clean      — Clean generated files     ║"
	@echo "║                                              ║"
	@echo "╚══════════════════════════════════════════════╝"

# Initial setup
setup:
	@chmod +x scripts/*.sh
	@./scripts/setup.sh

# Start development servers
start:
	@./scripts/start_dev.sh

# Stop development servers
stop:
	@./scripts/stop_dev.sh

# Run all tests
test:
	@./scripts/run_tests.sh

# Generate seed data (no API)
seed:
	@./scripts/generate_seed_data.sh

# Seed data via API
seed-api:
	@./scripts/generate_seed_data.sh --api

# Train AI model
train:
	@./scripts/train_ai_model.sh

# Full load test
load-test:
	@./scripts/run_load_test.sh

# Quick load test
quick-test:
	@./scripts/run_load_test.sh --quick

# Backup database
backup:
	@./scripts/backup_db.sh

# Docker start
docker:
	@docker-compose up --build -d
	@echo "Services started. Frontend: http://localhost:3000"

# Docker stop
docker-down:
	@docker-compose down
	@echo "All containers stopped."

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -rf ai_module/data/*.csv
	@rm -rf ai_module/models/*.pkl
	@rm -rf ai_module/models/*.json
	@rm -rf automation/reports/*
	@rm -rf backend/logs/*.log
	@rm -rf backups/
	@rm -rf frontend/build/
	@rm -rf frontend/dist/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@echo "[✓] Cleanup complete!"