#!/bin/bash

# ================================================
# ProSensia Smart-Serve — Stop Development Servers
# ================================================
# Stops all running development services.
# Usage: ./scripts/stop_dev.sh
# ================================================

echo "╔══════════════════════════════════════════════╗"
echo "║   ProSensia Smart-Serve — Stopping Dev      ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Kill backend
if [ -f /tmp/prosensia_backend.pid ]; then
    BACKEND_PID=$(cat /tmp/prosensia_backend.pid)
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID"
        echo "[✓] Backend stopped (PID: $BACKEND_PID)"
    fi
    rm -f /tmp/prosensia_backend.pid
fi

# Kill frontend
if [ -f /tmp/prosensia_frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/prosensia_frontend.pid)
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID"
        echo "[✓] Frontend stopped (PID: $FRONTEND_PID)"
    fi
    rm -f /tmp/prosensia_frontend.pid
fi

# Kill any remaining uvicorn processes
pkill -f "uvicorn main:socket_app" 2>/dev/null && \
    echo "[✓] Killed remaining uvicorn processes" || true

# Kill any remaining vite/node processes on port 3000
lsof -ti:3000 | xargs kill 2>/dev/null && \
    echo "[✓] Freed port 3000" || true

# Kill any remaining processes on port 8000
lsof -ti:8000 | xargs kill 2>/dev/null && \
    echo "[✓] Freed port 8000" || true

echo ""

# Optionally stop Docker containers
read -p "Stop Docker containers (PostgreSQL, Redis)? [y/N]: " stop_docker
if [[ "$stop_docker" =~ ^[Yy]$ ]]; then
    docker stop prosensia-db prosensia-redis 2>/dev/null && \
        echo "[✓] Docker containers stopped" || true
    docker rm prosensia-db prosensia-redis 2>/dev/null || true
fi

echo ""
echo "[✓] All services stopped."