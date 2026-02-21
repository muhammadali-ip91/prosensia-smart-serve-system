<p align="center">
  <img src="docs/architecture_diagram.png" alt="ProSensia Smart-Serve" width="280" />
</p>

<h1 align="center">ProSensia Smart-Serve</h1>

<p align="center">
  <strong>AI-Powered Smart Food Ordering &amp; Delivery System for Industrial Environments</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-blue" alt="Version" />
  <img src="https://img.shields.io/badge/python-3.11-green" alt="Python" />
  <img src="https://img.shields.io/badge/node-18+-green" alt="Node" />
  <img src="https://img.shields.io/badge/FastAPI-0.104-009688" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-18-61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License" />
</p>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running Locally (Windows)](#running-locally-windows)
  - [Running with Docker](#running-with-docker)
- [Demo Credentials](#demo-credentials)
- [API Reference](#api-reference)
- [WebSocket Events](#websocket-events)
- [AI / ML Module](#ai--ml-module)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Deployment](#deployment)
- [Make Commands](#make-commands)
- [Documentation](#documentation)
- [License](#license)

---

## Overview

**ProSensia Smart-Serve** is a full-stack, real-time food ordering and delivery management platform purpose-built for industrial campuses, corporate parks, and large facility messes. It replaces manual paper/token systems with a digital workflow that covers the entire order lifecycle — from menu browsing to kitchen preparation to runner delivery — backed by an AI model that predicts delivery ETAs in real time.

The system serves **four distinct user roles**, each with a dedicated dashboard and real-time Socket.IO connectivity:

| Role | Capabilities |
|------|-------------|
| **Engineer** | Browse menu, place orders, track live status, view AI-predicted ETA, provide feedback, play trivia while waiting |
| **Kitchen** | View incoming/preparing/ready queues, update order status, toggle menu availability, control kitchen open/close hours |
| **Runner** | See assigned deliveries, update delivery status (picked up → delivered), toggle personal availability |
| **Admin** | Full system management — analytics dashboard, menu CRUD with image upload, user management, trivia management |

---

## Key Features

### Core Workflow
- **Digital Ordering** — Engineers browse a categorized menu, add items to cart, set priority (Regular / Urgent), and place orders with special instructions.
- **Kitchen Queue Management** — Kitchen staff see orders in Incoming → Preparing → Ready pipeline with one-click status transitions.
- **Runner Assignment** — Automatic runner assignment based on availability; runners see active deliveries and update status in real time.
- **Live Order Tracking** — Engineers track their order through every status change with a visual timeline and progress bar.

### AI-Powered ETA Prediction
- **Machine Learning Model** — A trained `RandomForestRegressor` (scikit-learn) predicts delivery ETA using 11 features: time of day, item complexity, kitchen queue length, runner availability, station distance, and more.
- **Automatic Fallback** — If the ML model is unavailable, the system seamlessly falls back to a rule-based estimation engine. The engineer always sees an ETA.
- **Continuous Learning** — Delivered orders are logged to a training data table and can be used to retrain and improve the model over time.
- **Model Metrics** — Current model: MAE = 2.52 min, RMSE = 3.15 min, R² = 0.92 (trained on 3,000 records).

### Real-Time Communication
- **Socket.IO Integration** — Every status change, new order, delivery assignment, and ETA update is broadcast in real time to the relevant role dashboards.
- **Room-Based Targeting** — Events are scoped to `engineer_{id}`, `runner_{id}`, and `kitchen` rooms so clients only receive relevant updates.
- **Optional Redis Pub/Sub** — Horizontal scaling support via Redis message manager for multi-instance deployments.

### Engagement & Extras
- **Trivia Game** — Engineers can play a trivia game while waiting for their order, with a weekly leaderboard.
- **Feedback System** — Star rating and text feedback after delivery, aggregated in admin analytics.
- **Notification System** — In-app notifications with unread counts and sound alerts for new orders and status changes.
- **Offline Detection** — Frontend detects network loss and shows an offline banner with auto-reconnect.

### Admin & Ops
- **Dashboard Analytics** — Total orders, revenue, average delivery time, popular items, peak hours chart, runner performance table.
- **Menu Management** — Full CRUD with image upload (max 5 MB), price, category, prep time, complexity score.
- **User Management** — Create, activate/deactivate, update users across all roles.
- **Rate Limiting** — Configurable per-minute and login-specific rate limits via SlowAPI.
- **Structured Logging** — Loguru-based request/response logging with file rotation.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│          React 18 + Vite + Tailwind CSS + Socket.IO Client      │
│                    Port 5173 (dev) / 3000 (Docker)              │
└───────────────┬─────────────────────────────┬───────────────────┘
                │ REST (Axios)                │ WebSocket (Socket.IO)
                ▼                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                          BACKEND                                │
│     FastAPI + SQLAlchemy + python-socketio (ASGI via Uvicorn)   │
│                         Port 8000                               │
│                                                                 │
│   ┌─────────┐ ┌──────────┐ ┌────────────┐ ┌─────────────────┐  │
│   │  Auth   │ │  Orders  │ │  Kitchen   │ │  Runner         │  │
│   │  JWT    │ │  CRUD    │ │  Queue Mgmt│ │  Delivery Mgmt  │  │
│   └─────────┘ └──────────┘ └────────────┘ └─────────────────┘  │
│   ┌─────────┐ ┌──────────┐ ┌────────────┐ ┌─────────────────┐  │
│   │  Admin  │ │  Menu    │ │  Notifs    │ │  Trivia         │  │
│   │  Panel  │ │  Service │ │  Service   │ │  Game           │  │
│   └─────────┘ └──────────┘ └────────────┘ └─────────────────┘  │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              ETA Service (AI Integration)               │   │
│   │   ML Model (.pkl) ←→ Feature Engineering ←→ Fallback   │   │
│   └─────────────────────────────────────────────────────────┘   │
└───────────┬─────────────────────────────┬───────────────────────┘
            │                             │
            ▼                             ▼
┌───────────────────┐         ┌───────────────────────┐
│   SQLite (local)  │         │   Redis (optional)    │
│   PostgreSQL      │         │   Socket.IO scaling   │
│   (production)    │         │   + caching           │
└───────────────────┘         └───────────────────────┘
```

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, Vite 5, Tailwind CSS 3, React Router 6, Axios, Socket.IO Client, React Hot Toast, Lucide Icons, date-fns |
| **Backend** | Python 3.11, FastAPI 0.104, Uvicorn, SQLAlchemy 2.0, Pydantic 2, python-socketio 5, Loguru |
| **Database** | SQLite (development), PostgreSQL 15 (production/Docker) |
| **Cache / PubSub** | Redis 7 (optional, for Socket.IO horizontal scaling) |
| **AI / ML** | scikit-learn 1.3, pandas, NumPy, joblib |
| **Auth** | JWT (python-jose), bcrypt (passlib) |
| **Testing** | pytest, pytest-asyncio, httpx, Jest, React Testing Library, Cypress 13 |
| **Load Testing** | Locust |
| **DevOps** | Docker, Docker Compose, GitHub Actions CI/CD, Alembic (migrations) |

---

## Project Structure

```
prosensia-smart-serve-system/
│
├── backend/                    # FastAPI application
│   ├── main.py                 # App entry point, lifespan, router registration
│   ├── config.py               # Pydantic settings (env-based configuration)
│   ├── Dockerfile              # Backend container definition
│   ├── auth/                   # JWT handler, password hashing, RBAC
│   ├── database/               # Engine, sessions, seed data, connection normalization
│   ├── middleware/              # CORS, error handling, logging, rate limiting
│   ├── migrations/             # Alembic migration scripts (13 tables)
│   ├── models/                 # SQLAlchemy ORM models (User, Order, MenuItem, etc.)
│   ├── routers/                # API route handlers (auth, order, menu, kitchen, runner, admin, trivia, health, notification)
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/               # Business logic (order lifecycle, ETA, notifications, analytics)
│   ├── uploads/                # Uploaded menu item images
│   ├── utils/                  # ID generator, time utils, validators, constants
│   └── websocket/              # Socket.IO manager, events, rooms
│
├── frontend/                   # React SPA
│   ├── index.html              # Vite entry
│   ├── Dockerfile              # Frontend container definition
│   ├── package.json            # Dependencies and scripts
│   ├── tailwind.config.js      # Tailwind theme configuration
│   ├── vite.config.js          # Vite build configuration
│   └── src/
│       ├── App.jsx             # Root component with role-based routing
│       ├── api/                # Axios instance + API modules (auth, order, menu, kitchen, runner, admin, trivia, notification)
│       ├── assets/             # Fonts, images, SVGs, sound effects
│       ├── components/         # Reusable UI components organized by domain
│       │   ├── admin/          # Dashboard charts, forms, tables
│       │   ├── auth/           # Login form, session expired modal
│       │   ├── cart/           # Cart items, summary, ETA preview, priority toggle
│       │   ├── common/         # Navbar, Footer, Button, Modal, Badge, Spinner, Toast, etc.
│       │   ├── feedback/       # Star rating, feedback form
│       │   ├── kitchen/        # Order cards, timers, status buttons, menu toggle
│       │   ├── menu/           # Item cards, category filter, quantity selector
│       │   ├── notification/   # Bell icon, dropdown, sound alerts
│       │   ├── order/          # Order card, timeline, progress bar, ETA display
│       │   ├── runner/         # Delivery cards, actions, status toggle
│       │   └── trivia/         # Question display, timer, leaderboard, score
│       ├── context/            # React contexts (Auth, Cart, Order, Socket, Notification)
│       ├── hooks/              # Custom hooks (useAuth, useCart, useOrder, useSocket, useTrivia, useNotification)
│       ├── pages/              # Page components by role (engineer, kitchen, runner, admin, trivia, auth, common)
│       ├── routes/             # Route definitions by role
│       ├── services/           # Cache, push notification, socket, storage services
│       └── utils/              # Constants, formatters, helpers, validators, sound manager
│
├── ai_module/                  # Machine Learning module
│   ├── core/                   # Predictor, Feature Engineering, Model Loader, Fallback
│   ├── data/                   # Training/test CSV data
│   ├── models/                 # Trained model (.pkl) + metadata (.json)
│   ├── notebooks/              # Jupyter notebooks (exploration, feature importance, model comparison)
│   └── scripts/                # train_model, retrain, evaluate, generate data, export training data
│
├── automation/                 # Automation scripts
│   ├── data_generation/        # Seed scripts (menu, engineers, runners, stations, trivia)
│   ├── load_testing/           # Locust config, simulator, report generator, cleanup
│   ├── reports/                # Generated load test reports and CSVs
│   └── simulation/             # Kitchen, order flow, runner, traffic pattern simulators
│
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests (AI, backend services, frontend components)
│   ├── integration/            # Integration tests (auth flow, order lifecycle, websocket, concurrency)
│   └── e2e/                    # Cypress end-to-end tests (login, place order, kitchen, runner, feedback, trivia, offline)
│
├── docs/                       # Project documentation
│   ├── api_documentation.md    # Full API reference
│   ├── database_schema.md      # Database schema details
│   ├── websocket_events.md     # Socket.IO event reference
│   ├── ai_model_guide.md       # AI model training and integration guide
│   ├── feature_matrix.md       # Endpoint-to-UI mapping (34 endpoints)
│   ├── deployment_guide.md     # Production deployment guide
│   ├── scaling_guide.md        # Horizontal scaling guide
│   ├── setup_guide.md          # Developer setup guide
│   ├── testing_guide.md        # Testing strategy and execution
│   ├── error_codes.md          # Error code reference
│   └── project_master_guide.md # Comprehensive project overview
│
├── scripts/                    # Developer utility scripts
│   ├── run-local.ps1           # Start backend + frontend locally (Windows)
│   ├── run_validation.ps1      # Full validation suite (Windows)
│   ├── scaffold.ps1            # Project scaffolding
│   ├── setup.sh                # Initial setup (Linux/Mac)
│   ├── start_dev.sh            # Start dev servers (Linux/Mac)
│   ├── stop_dev.sh             # Stop dev servers
│   ├── run_tests.sh            # Run test suite
│   ├── backup_db.sh            # Database backup
│   ├── generate_seed_data.sh   # Generate seed data
│   ├── run_load_test.sh        # Run load tests
│   └── train_ai_model.sh       # Train AI model
│
├── .github/                    # GitHub configuration
│   ├── workflows/              # CI/CD pipelines (ci.yml, cd.yml, ai_retrain.yml)
│   ├── ISSUE_TEMPLATE/         # Bug report and feature request templates
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS
│   └── dependabot.yml          # Dependency update automation
│
├── docker-compose.yml          # Full-stack Docker setup (backend + frontend + PostgreSQL + Redis)
├── Makefile                    # Developer convenience commands
├── .env.example                # Environment variable template
├── .gitignore                  # Git ignore rules
└── LICENSE                     # MIT License
```

---

## Getting Started

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.11+ | Backend and AI module |
| **Node.js** | 18+ | Frontend build and dev server |
| **npm** | 9+ | Frontend package management |
| **Git** | 2.x | Version control |
| **Docker** *(optional)* | 24+ | Containerized deployment |

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/muhammadali-ip91/prosensia-smart-serve-system.git
   cd prosensia-smart-serve-system
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your values (for local dev, defaults work fine)
   ```

3. **Create Python virtual environment and install dependencies**
   ```bash
   python -m venv .venv

   # Windows
   .\.venv\Scripts\Activate.ps1

   # Linux / Mac
   source .venv/bin/activate

   pip install -r backend/requirements.txt
   pip install -r ai_module/requirements.txt
   pip install -r automation/requirements.txt
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running Locally (Windows)

The recommended way to run both servers locally on Windows:

```powershell
.\scripts\run-local.ps1
```

This script:
- Activates the virtual environment
- Kills any processes on ports 8000 and 5173
- Starts the FastAPI backend at `http://localhost:8000`
- Starts the Vite dev server at `http://localhost:5173`

**Manual start (any OS):**

```bash
# Terminal 1 — Backend
cd backend
uvicorn main:socket_app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — Frontend
cd frontend
npm run dev
```

**Verify the system is running:**

```bash
# Health endpoint
curl http://localhost:8000/health

# API docs (interactive)
# Open http://localhost:8000/docs in your browser
```

### Running with Docker

```bash
docker-compose up --build
```

This starts four containers:

| Service | Port | Image |
|---------|------|-------|
| Backend (FastAPI) | 8000 | python:3.11-slim |
| Frontend (Vite) | 3000 | node:18-alpine |
| PostgreSQL 15 | 5432 | postgres:15-alpine |
| Redis 7 | 6379 | redis:7-alpine |

Stop all services:
```bash
docker-compose down
```

---

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@prosensia.com` | `admin123` |
| Engineer | `engineer1@prosensia.com` | `engineer123` |
| Kitchen | `kitchen1@prosensia.com` | `kitchen123` |
| Runner | `runner1@prosensia.com` | `runner123` |

> These are seeded automatically on first run. Change them in production via the Admin panel or database.

---

## API Reference

Base URL: `http://localhost:8000`

Interactive documentation available at [`/docs`](http://localhost:8000/docs) (Swagger UI) and [`/redoc`](http://localhost:8000/redoc) (ReDoc).

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/login` | Login with email/employee_id → JWT tokens |
| `POST` | `/auth/refresh` | Refresh access token |
| `GET` | `/auth/me` | Get current user profile |
| `POST` | `/auth/logout` | Client-side logout |

### Orders

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| `POST` | `/orders` | Place a new order | Engineer |
| `GET` | `/orders` | Get order history (paginated) | Engineer |
| `GET` | `/orders/{order_id}` | Get order details | Owner/Admin |
| `DELETE` | `/orders/{order_id}` | Cancel order | Owner/Admin |
| `POST` | `/orders/{order_id}/feedback` | Submit feedback | Engineer |

### Menu

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| `GET` | `/menu` | Available menu items | Authenticated |
| `GET` | `/menu/all` | All items (incl. unavailable) | Authenticated |

### Kitchen

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| `GET` | `/kitchen/orders` | Active kitchen orders | Kitchen |
| `PATCH` | `/kitchen/orders/{id}/status` | Update preparation status | Kitchen |
| `PATCH` | `/kitchen/menu/{id}/availability` | Toggle item availability | Kitchen |
| `GET` | `/kitchen/settings` | Kitchen open/close status | Kitchen |
| `PATCH` | `/kitchen/settings/hours` | Update operating hours | Kitchen |
| `PATCH` | `/kitchen/settings/toggle` | Open/close kitchen | Kitchen |

### Runner

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| `GET` | `/runner/deliveries` | Assigned deliveries | Runner |
| `PATCH` | `/runner/deliveries/{id}/status` | Update delivery status | Runner |
| `PATCH` | `/runner/status` | Toggle runner availability | Runner |

### Admin

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| `GET` | `/admin/dashboard` | Analytics overview | Admin |
| `GET` | `/admin/popular-items` | Most popular items | Admin |
| `POST` | `/admin/menu` | Add menu item | Admin |
| `POST` | `/admin/menu/upload-image` | Upload item image (≤5 MB) | Admin |
| `PUT` | `/admin/menu/{id}` | Update menu item | Admin |
| `DELETE` | `/admin/menu/{id}` | Delete menu item | Admin |
| `GET` | `/admin/users` | List users (optional role filter) | Admin |
| `POST` | `/admin/users` | Create user | Admin |
| `PUT` | `/admin/users/{id}` | Update user | Admin |
| `PUT` | `/admin/users/{id}/toggle` | Activate/deactivate user | Admin |

### Trivia

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| `GET` | `/trivia/question` | Random trivia question | Engineer |
| `POST` | `/trivia/answer` | Submit answer | Engineer |
| `GET` | `/trivia/leaderboard` | Weekly leaderboard | Engineer |

### Notifications

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| `GET` | `/notifications` | Get notifications (+ unread count) | Authenticated |
| `PATCH` | `/notifications/read` | Mark as read | Authenticated |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health (DB, Redis, AI model, uptime) |
| `GET` | `/` | API info |

---

## WebSocket Events

The system uses **Socket.IO** for real-time communication. Clients join role-based rooms on connection.

### Server → Client

| Event | Target | Description |
|-------|--------|-------------|
| `order_status_update` | Engineer, Kitchen, Runner | Order status changed |
| `new_order` | Kitchen | New order placed |
| `new_delivery` | Runner | Delivery assignment |
| `eta_update` | Engineer | Updated ETA prediction |
| `notification` | All roles | Generic notification |
| `order_cancelled` | Kitchen, Runner | Order cancellation |
| `delivery_reassigned` | Runner | Delivery resource change |

### Client → Server

| Event | Description |
|-------|-------------|
| `join_room` | Join a role-based room (`engineer_{id}`, `runner_{id}`, `kitchen`) |
| `leave_room` | Leave a room |

---

## AI / ML Module

The AI module predicts **delivery ETA** for each order using a trained machine learning model.

### How It Works

1. **Feature Extraction** — When an order is placed, the system extracts 11 features:

   | # | Feature | Description |
   |---|---------|-------------|
   | 1 | `hour_of_day` | Hour when order was placed (0–23) |
   | 2 | `day_of_week` | Day of week (0=Mon, 6=Sun) |
   | 3 | `active_orders_count` | Currently active orders |
   | 4 | `item_complexity` | Weighted complexity score |
   | 5 | `total_items` | Number of items ordered |
   | 6 | `available_runners` | Runners currently available |
   | 7 | `kitchen_queue_length` | Orders ahead in queue |
   | 8 | `avg_prep_time` | Average prep time of items (minutes) |
   | 9 | `station_distance` | Distance to delivery station (meters) |
   | 10 | `is_peak_hour` | Lunch (12–14) or Dinner (18–20) |
   | 11 | `priority_encoded` | 0 = Regular, 1 = Urgent |

2. **Prediction** — The `RandomForestRegressor` model predicts ETA (clamped to 3–60 minutes).
3. **Confidence Score** — A confidence value (0–1) is returned with every prediction.
4. **Fallback** — If the model fails to load or predict, a rule-based engine provides the ETA. The user **never** sees a blank ETA.

### Model Performance

| Metric | Value |
|--------|-------|
| Algorithm | Random Forest (100 trees, max_depth=12) |
| MAE | 2.52 minutes |
| RMSE | 3.15 minutes |
| R² Score | 0.92 |
| Training Data | 3,000 records |
| Threshold | MAE < 3.0 min |

### Training / Retraining

```bash
# Activate environment
.\.venv\Scripts\Activate.ps1    # Windows
source .venv/bin/activate        # Linux/Mac

# Train model
python -m ai_module.scripts.train_model

# Evaluate model
python -m ai_module.scripts.evaluate_model

# Export training data from database
python -m ai_module.scripts.export_training_data

# Generate synthetic training data
python -m ai_module.scripts.generate_data
```

Output: `ai_module/models/eta_model.pkl` + `ai_module/models/model_metadata.json`

---

## Database Schema

The system uses **13 tables**:

| Table | Description |
|-------|-------------|
| `users` | All system users (engineer, kitchen, runner, admin) |
| `stations` | Delivery stations with distance from kitchen |
| `menu_items` | Food items with price, prep time, complexity, availability |
| `orders` | Order records with status, priority, AI ETA, actual time |
| `order_items` | Individual items within an order |
| `runners` | Runner availability and status tracking |
| `order_status_history` | Complete audit trail of order status changes |
| `feedback` | Star rating and text feedback per order |
| `notifications` | In-app notification records |
| `trivia_questions` | Trivia question bank |
| `trivia_scores` | Player scores and streaks |
| `ai_training_data` | Logged order data for model retraining |
| `system_logs` | System event logs |

Database migrations are managed via **Alembic** (see `backend/migrations/`).

> In local development, SQLite is used by default. For production, configure `DATABASE_URL` in `.env` to point to PostgreSQL.

---

## Testing

### Unit Tests

```bash
pytest tests/unit/ -v
```

Covers: AI prediction, feature engineering, fallback logic, auth, order service, kitchen service, menu service, runner assignment, notification service, trivia, validators, time utils, ID generator.

### Integration Tests

```bash
pytest tests/integration/ -v
```

Covers: Auth flow, order lifecycle, kitchen workflow, runner workflow, WebSocket events, database consistency, concurrent orders, AI integration.

### End-to-End Tests (Cypress)

```bash
cd frontend
npx cypress open    # Interactive mode
npx cypress run     # Headless mode
```

Covers: Login, place order, track order, cancel order, kitchen dashboard, runner delivery, feedback, trivia game, admin panel, offline mode, error handling.

### Frontend Unit Tests (Jest)

```bash
cd frontend
npm test
```

### Full Validation (Windows)

```powershell
.\scripts\run_validation.ps1
```

Runs: backend startup check, API health verification, unit tests, integration tests, Cypress E2E, and generates a validation report.

### Load Testing (Locust)

```bash
python -m automation.load_testing.load_simulator
# or
locust -f automation/load_testing/locustfile.py
```

---

## Deployment

### Frontend (Vercel / Netlify)

1. Connect repository to Vercel or Netlify.
2. Set build command: `cd frontend && npm run build`
3. Set output directory: `frontend/dist`
4. Set environment variables:
   - `VITE_API_URL=https://your-backend-url.com`
   - `VITE_SOCKET_URL=wss://your-backend-url.com`

### Backend (Render / Railway / VPS)

1. Deploy using Docker or raw Python.
2. Set environment variables from `.env.example`.
3. Key variables:
   - `DATABASE_URL` — PostgreSQL connection string
   - `JWT_SECRET_KEY` — Change to a strong random secret
   - `CORS_ORIGINS` — Your frontend domain
   - `FRONTEND_URL` — Your frontend URL
   - `AI_MODEL_PATH` — Path to model file

### Database (Supabase / Neon / RDS)

- Use any PostgreSQL 15+ provider.
- Set the `DATABASE_URL` environment variable.
- Tables are auto-created on first backend startup.

### Quick Docker Deploy

```bash
docker-compose -f docker-compose.yml up -d --build
```

---

## Make Commands

| Command | Description |
|---------|-------------|
| `make setup` | Initial project setup |
| `make start` | Start all development servers |
| `make stop` | Stop all development servers |
| `make test` | Run full test suite |
| `make seed` | Generate seed data (direct DB) |
| `make seed-api` | Seed data via API endpoints |
| `make train` | Train the AI model |
| `make load-test` | Run full load test |
| `make quick-test` | Quick load test |
| `make backup` | Backup database |
| `make docker` | Start with Docker Compose |
| `make docker-down` | Stop Docker Compose |
| `make clean` | Clean generated files |

---

## Documentation

Detailed documentation is available in the [`docs/`](docs/) directory:

| Document | Description |
|----------|-------------|
| [API Documentation](docs/api_documentation.md) | Complete API reference with examples |
| [Database Schema](docs/database_schema.md) | Table definitions and relationships |
| [WebSocket Events](docs/websocket_events.md) | Real-time event reference |
| [AI Model Guide](docs/ai_model_guide.md) | Model training, evaluation, and integration |
| [Feature Matrix](docs/feature_matrix.md) | Endpoint-to-UI screen mapping |
| [Setup Guide](docs/setup_guide.md) | Developer environment setup |
| [Deployment Guide](docs/deployment_guide.md) | Production deployment instructions |
| [Scaling Guide](docs/scaling_guide.md) | Horizontal scaling strategies |
| [Testing Guide](docs/testing_guide.md) | Testing strategy and execution |
| [Error Codes](docs/error_codes.md) | Error code reference |
| [Project Master Guide](docs/project_master_guide.md) | Comprehensive project overview |

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ by the ProSensia Team
</p>

Run integration tests only:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest tests/integration -q
```

Run frontend E2E only:

```powershell
cd frontend
npm run cypress:run -- --project ../tests/e2e
```

## Deployment Pattern (Recommended)

- Frontend: **Vercel** (or Netlify)
- Backend: **Render / Railway** (Docker)
- DB: **PostgreSQL** (Supabase / Neon / Render Postgres)
- Redis (optional for scaling): Upstash / Redis Cloud

Important: frontend should call backend API URL via env vars:
- `VITE_API_URL=https://<backend-domain>`
- `VITE_SOCKET_URL=https://<backend-domain>`

## Common Issues

- **Network error in UI**: backend not reachable on `localhost:8000`.
- **Orders appear/disappear**: DB path mismatch; use backend-local DB path consistently.
- **Model not loading**: invalid `.pkl` file (empty/corrupt files raise `EOFError`/pickle errors).

## Useful Scripts

- `scripts/run-local.ps1` – start local backend + frontend
- `scripts/run_validation.ps1` – full validation matrix
- `scripts/run_tests.sh` – test suite helper
- `scripts/train_ai_model.sh` – model training helper
- `scripts/run_load_test.sh` – load testing helper

## License

MIT (see `LICENSE`)
