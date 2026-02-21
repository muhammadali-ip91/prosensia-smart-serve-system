# 🚢 ProSensia Smart-Serve — Deployment Guide

---

## Deployment Options

### Option 1: Docker Compose (Recommended for Demo)

```bash
# Clone repository
git clone https://github.com/your-username/prosensia-smart-serve.git
cd prosensia-smart-serve

# Create environment file
cp .env.example .env
# Edit .env with production values

# Build and start
docker-compose -f docker-compose.yml up -d --build

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed initial data
docker-compose exec backend python -m automation.data_generation.seed_all --mode api

# Train AI model
docker-compose exec backend python -m ai_module.scripts.generate_data
docker-compose exec backend python -m ai_module.scripts.train_model

# Check status
docker-compose ps
docker-compose logs --tail=50
Stopping
Bash

docker-compose down          # Stop containers
docker-compose down -v       # Stop + remove volumes (deletes data)
Option 2: Manual Deployment
Bash

# Backend
cd backend
source venv/bin/activate
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000

# Frontend
cd frontend
npm run build
npx serve -s build -l 3000
Environment Variables
env

# Database
DATABASE_URL=postgresql://user:pass@db:5432/prosensia

# Redis
REDIS_URL=redis://redis:6379

# JWT
JWT_SECRET=your-super-secret-key-change-this
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Model
AI_MODEL_PATH=/app/ai_module/models/eta_model.pkl

# CORS
CORS_ORIGINS=http://localhost:3000

# App
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
Health Checks
Bash

# API health
curl http://localhost:8000/health

# Database check
docker-compose exec db pg_isready

# Redis check
docker-compose exec redis redis-cli ping
Backup
Bash

# Database backup
docker-compose exec db pg_dump -U user prosensia > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20240115.sql | docker-compose exec -T db psql -U user prosensia
Monitoring
Bash

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Container stats
docker stats
text
