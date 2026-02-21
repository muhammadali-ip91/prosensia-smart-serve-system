#!/bin/bash

# ================================================
# ProSensia Smart-Serve — Generate Seed Data
# ================================================
# Generates all seed data for the system.
# Usage: ./scripts/generate_seed_data.sh [--api]
# ================================================

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   ProSensia — Generate Seed Data             ║"
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

# Check mode
MODE="generate"
if [ "$1" == "--api" ]; then
    MODE="api"
    echo "Mode: Seeding via API (server must be running)"
    
    # Check if server is running
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "❌ Backend server not running!"
        echo "   Start with: ./scripts/start_dev.sh"
        exit 1
    fi
else
    echo "Mode: Generate only (no API calls)"
    echo "  Use --api flag to seed via API"
fi

echo ""

# Run seed all
python3 -m automation.data_generation.seed_all --mode "$MODE"

echo ""
echo "[✓] Seed data generation complete!"