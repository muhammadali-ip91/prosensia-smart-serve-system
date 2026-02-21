#!/bin/bash

# ================================================
# ProSensia Smart-Serve — Initial Setup Script
# ================================================
# This script sets up the entire project from scratch.
# Usage: chmod +x scripts/setup.sh && ./scripts/setup.sh
# ================================================

set -e  # Exit on any error

echo "╔══════════════════════════════════════════════╗"
echo "║   ProSensia Smart-Serve — Project Setup     ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# ========================================
# Step 1: Check Prerequisites
# ========================================
echo "── Step 1: Checking Prerequisites ──"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    print_status "Python found: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    print_status "Node.js found: $NODE_VERSION"
else
    print_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version 2>&1)
    print_status "Docker found: $DOCKER_VERSION"
else
    print_warning "Docker not found. Docker deployment won't work."
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    print_status "Docker Compose found"
else
    print_warning "Docker Compose not found."
fi

echo ""

# ========================================
# Step 2: Create Environment File
# ========================================
echo "── Step 2: Environment Setup ──"

if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        print_status "Created .env from .env.example"
    else
        # Create default .env
        cat > .env << 'EOF'
# ProSensia Smart-Serve Environment Variables

# Database
DATABASE_URL=postgresql://prosensia_user:prosensia_pass@localhost:5432/prosensia
POSTGRES_DB=prosensia
POSTGRES_USER=prosensia_user
POSTGRES_PASSWORD=prosensia_pass

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=prosensia-super-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API
API_BASE_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000

# App
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# AI Model
AI_MODEL_PATH=ai_module/models/eta_model.pkl

# Admin
ADMIN_EMAIL=admin@prosensia.com
ADMIN_PASSWORD=admin123
DEFAULT_PASSWORD=test123

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SOCKET_URL=ws://localhost:8000
EOF
        print_status "Created default .env file"
    fi
else
    print_status ".env file already exists"
fi

echo ""

# ========================================
# Step 3: Backend Setup
# ========================================
echo "── Step 3: Backend Setup ──"

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Created Python virtual environment"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_status "Activated virtual environment"

# Install backend dependencies
pip install -r requirements.txt --quiet 2>/dev/null
print_status "Installed backend dependencies"

# Install AI module dependencies
if [ -f "../ai_module/requirements.txt" ]; then
    pip install -r ../ai_module/requirements.txt --quiet 2>/dev/null
    print_status "Installed AI module dependencies"
fi

# Install automation dependencies
if [ -f "../automation/requirements.txt" ]; then
    pip install -r ../automation/requirements.txt --quiet 2>/dev/null
    print_status "Installed automation dependencies"
fi

# Create log directories
mkdir -p logs
print_status "Created logs directory"

cd ..
echo ""

# ========================================
# Step 4: Frontend Setup
# ========================================
echo "── Step 4: Frontend Setup ──"

cd frontend

# Install Node dependencies
npm install --silent 2>/dev/null
print_status "Installed frontend dependencies"

cd ..
echo ""

# ========================================
# Step 5: Create Required Directories
# ========================================
echo "── Step 5: Creating Directories ──"

mkdir -p ai_module/data
mkdir -p ai_module/models
mkdir -p ai_module/notebooks
mkdir -p automation/reports
mkdir -p backend/logs
print_status "Created all required directories"

echo ""

# ========================================
# Step 6: Generate AI Training Data
# ========================================
echo "── Step 6: AI Module Setup ──"

cd backend
source venv/bin/activate

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(cd .. && pwd)"

# Generate training data
python3 -m ai_module.scripts.generate_data 2>/dev/null && \
    print_status "Generated AI training data (5000 records)" || \
    print_warning "Could not generate AI data (run manually later)"

# Train model
python3 -m ai_module.scripts.train_model 2>/dev/null && \
    print_status "Trained AI model" || \
    print_warning "Could not train AI model (run manually later)"

cd ..
echo ""

# ========================================
# Step 7: Make Scripts Executable
# ========================================
echo "── Step 7: Setting Permissions ──"

chmod +x scripts/*.sh 2>/dev/null
print_status "Made all scripts executable"

echo ""

# ========================================
# Summary
# ========================================
echo "╔══════════════════════════════════════════════╗"
echo "║           SETUP COMPLETE! 🎉                ║"
echo "╠══════════════════════════════════════════════╣"
echo "║                                              ║"
echo "║  To start the project:                       ║"
echo "║                                              ║"
echo "║  Option 1 (Docker):                          ║"
echo "║    docker-compose up --build                  ║"
echo "║                                              ║"
echo "║  Option 2 (Manual):                          ║"
echo "║    ./scripts/start_dev.sh                     ║"
echo "║                                              ║"
echo "║  Default Logins:                             ║"
echo "║    Admin:    ADM-001 / admin123               ║"
echo "║    Engineer: ENG-001 / test123                ║"
echo "║    Kitchen:  KIT-001 / test123                ║"
echo "║    Runner:   RUN-001 / test123                ║"
echo "║                                              ║"
echo "║  URLs:                                       ║"
echo "║    Frontend: http://localhost:3000             ║"
echo "║    Backend:  http://localhost:8000             ║"
echo "║    API Docs: http://localhost:8000/docs        ║"
echo "║                                              ║"
echo "╚══════════════════════════════════════════════╝"