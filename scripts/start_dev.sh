#!/bin/bash

# ================================================
# ProSensia Smart-Serve — Start Development Servers
# ================================================
# Starts backend, frontend, and required services.
# Usage: ./scripts/start_dev.sh
# ================================================

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   ProSensia Smart-Serve — Starting Dev      ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs) 2>/dev/null
fi

# ========================================
# Check if Docker services are needed
# ========================================
echo "── Checking Required Services ──"

# Check PostgreSQL
if ! pg_isready -q 2>/dev/null; then
    echo "Starting PostgreSQL via Docker..."
    docker run -d \
        --name prosensia-db \
        -e POSTGRES_DB=prosensia \
        -e POSTGRES_USER=prosensia_user \
        -e POSTGRES_PASSWORD=prosensia_pass \
        -p 5432:5432 \
        postgres:15 2>/dev/null || echo "PostgreSQL container may already exist"
    sleep 3
    echo "[✓] PostgreSQL started on port 5432"
else
    echo "[✓] PostgreSQL already running"
fi

# Check Redis
if ! redis-cli ping &>/dev/null; then
    echo "Starting Redis via Docker..."
    docker run -d \
        --name prosensia-redis \
        -p 6379:6379 \
        redis:7-alpine 2>/dev/null || echo "Redis container may already exist"
    sleep 2
    echo "[✓] Redis started on port 6379"
else
    echo "[✓] Redis already running"
fi

echo ""

# ========================================
# Start Backend
# ========================================
echo "── Starting Backend Server ──"

cd "$PROJECT_ROOT/backend"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt --quiet
fi

# Set Python path
export PYTHONPATH="${PYTHONPATH}:${PROJECT_ROOT}"

# Run migrations
echo "Running database migrations..."
alembic upgrade head 2>/dev/null || echo "Migrations may need manual attention"

# Start backend in background
echo "Starting FastAPI server..."
uvicorn main:socket_app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "[✓] Backend started on http://localhost:8000 (PID: $BACKEND_PID)"

cd "$PROJECT_ROOT"
echo ""

# ========================================
# Start Frontend
# ========================================
echo "── Starting Frontend Server ──"

cd "$PROJECT_ROOT/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install --silent
fi

# Start frontend in background
echo "Starting React dev server..."
npm run dev &
FRONTEND_PID=$!
echo "[✓] Frontend started on http://localhost:3000 (PID: $FRONTEND_PID)"

cd "$PROJECT_ROOT"
echo ""

# ========================================
# Save PIDs for stop script
# ========================================
echo "$BACKEND_PID" > /tmp/prosensia_backend.pid
echo "$FRONTEND_PID" > /tmp/prosensia_frontend.pid

# ========================================
# Summary
# ========================================
echo "╔══════════════════════════════════════════════╗"
echo "║           ALL SERVICES STARTED! 🚀          ║"
echo "╠══════════════════════════════════════════════╣"
echo "║                                              ║"
echo "║  Frontend:  http://localhost:3000             ║"
echo "║  Backend:   http://localhost:8000             ║"
echo "║  API Docs:  http://localhost:8000/docs        ║"
echo "║  Health:    http://localhost:8000/health       ║"
echo "║                                              ║"
echo "║  To stop:   ./scripts/stop_dev.sh             ║"
echo "║  Logs:      Check terminal output             ║"
echo "║                                              ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for any process to exit
wait