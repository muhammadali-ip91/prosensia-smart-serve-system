# 🚀 ProSensia Smart-Serve — Setup Guide

## Complete guide to set up and run the project locally.

---

## Prerequisites

Before starting, make sure you have the following installed:

| Tool           | Version  | Download Link                          |
|----------------|----------|----------------------------------------|
| Python         | 3.11+    | https://python.org/downloads           |
| Node.js        | 18+      | https://nodejs.org                     |
| PostgreSQL     | 15+      | https://postgresql.org/download        |
| Redis          | 7+       | https://redis.io/download              |
| Docker         | 24+      | https://docker.com/get-started         |
| Docker Compose | 2.20+    | Included with Docker Desktop           |
| Git            | 2.40+    | https://git-scm.com                    |

---

## Option 1: Docker Setup (Recommended)

This is the easiest way to run the entire system.

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/prosensia-smart-serve.git
cd prosensia-smart-serve
Step 2: Create Environment File
Bash

cp .env.example .env
Edit .env and set your values (or use defaults for development).

Step 3: Build and Start All Services
Bash

docker-compose up --build
This starts:

Backend API → http://localhost:8000
Frontend App → http://localhost:3000
PostgreSQL → localhost:5432
Redis → localhost:6379
Step 4: Run Database Migrations
Bash

docker-compose exec backend alembic upgrade head
Step 5: Seed Initial Data
Bash

docker-compose exec backend python -m automation.data_generation.seed_all --mode api
Step 6: Train AI Model
Bash

docker-compose exec backend python -m ai_module.scripts.generate_data
docker-compose exec backend python -m ai_module.scripts.train_model
Step 7: Verify Everything Works
Bash

# Check API health
curl http://localhost:8000/health

# Open frontend
open http://localhost:3000

# Check API docs
open http://localhost:8000/docs
Option 2: Manual Setup (Without Docker)
Step 1: Clone Repository
Bash

git clone https://github.com/your-username/prosensia-smart-serve.git
cd prosensia-smart-serve
Step 2: Backend Setup
Bash

# Create virtual environment
cd backend
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install AI module dependencies
pip install -r ../ai_module/requirements.txt

# Install automation dependencies
pip install -r ../automation/requirements.txt
Step 3: Database Setup
Bash

# Start PostgreSQL (if not running)
# On Linux:
sudo systemctl start postgresql
# On Mac:
brew services start postgresql

# Create database
psql -U postgres
CREATE DATABASE prosensia;
CREATE USER prosensia_user WITH PASSWORD 'prosensia_pass';
GRANT ALL PRIVILEGES ON DATABASE prosensia TO prosensia_user;
\q

# Run migrations
cd backend
alembic upgrade head
Step 4: Redis Setup
Bash

# Start Redis (if not running)
# On Linux:
sudo systemctl start redis
# On Mac:
brew services start redis

# Verify Redis is running
redis-cli ping
# Should return: PONG
Step 5: Environment Variables
Bash

# Copy example env file
cp .env.example .env

# Edit with your settings
nano .env
Step 6: Start Backend Server
Bash

cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
Step 7: Frontend Setup
Bash

# Open new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
Step 8: Seed Data & Train AI
Bash

# Open new terminal
cd prosensia-smart-serve

# Seed data
python -m automation.data_generation.seed_all --mode api

# Generate AI training data
python -m ai_module.scripts.generate_data

# Train AI model
python -m ai_module.scripts.train_model
Default Login Credentials
Role	Employee ID	Password
Admin	ADM-001	admin123
Engineer	ENG-001	test123
Kitchen	KIT-001	test123
Runner	RUN-001	test123
Useful URLs After Setup
Service	URL
Frontend App	http://localhost:3000
Backend API	http://localhost:8000
API Docs	http://localhost:8000/docs
Health Check	http://localhost:8000/health
Locust Testing	http://localhost:8089
Troubleshooting
Port Already in Use
Bash

# Find what's using the port
lsof -i :8000
# Kill it
kill -9 <PID>
Database Connection Error
Bash

# Check if PostgreSQL is running
pg_isready
# Restart if needed
sudo systemctl restart postgresql
Redis Connection Error
Bash

# Check if Redis is running
redis-cli ping
# Restart if needed
sudo systemctl restart redis
Module Not Found Error
Bash

# Make sure you're in project root
cd prosensia-smart-serve
# Add to Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)
Docker Issues
Bash

# Remove all containers and rebuild
docker-compose down -v
docker-compose up --build

# Check logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
Stopping the Project
Docker
Bash

docker-compose down
Manual
Bash

# Stop backend: Ctrl+C in backend terminal
# Stop frontend: Ctrl+C in frontend terminal
# Stop PostgreSQL:
sudo systemctl stop postgresql
# Stop Redis:
sudo systemctl stop redis
text
