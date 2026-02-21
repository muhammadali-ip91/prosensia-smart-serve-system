#!/bin/bash

# ================================================
# ProSensia Smart-Serve — Train AI Model
# ================================================
# Generates training data and trains the ETA model.
# Usage: ./scripts/train_ai_model.sh
# ================================================

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   ProSensia — AI Model Training Pipeline     ║"
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

# Step 1: Generate training data
echo "── Step 1: Generating Training Data ──"
python3 -m ai_module.scripts.generate_data
echo ""

# Step 2: Train model
echo "── Step 2: Training Model ──"
python3 -m ai_module.scripts.train_model
echo ""

# Step 3: Evaluate model
echo "── Step 3: Evaluating Model ──"
python3 -m ai_module.scripts.evaluate_model
echo ""

echo "╔══════════════════════════════════════════════╗"
echo "║   AI Model Training Pipeline Complete! 🤖    ║"
echo "╚══════════════════════════════════════════════╝"