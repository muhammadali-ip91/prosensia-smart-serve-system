# ProSensia Smart-Serve — Project Master Guide

This document is a single-place technical summary of the full project.
It consolidates architecture, modules, runtime behavior, data model, roles, workflows, AI, automation, testing, CI/CD, and deployment notes.

---

## 1) What This Project Is

ProSensia Smart-Serve is an internal food ordering and delivery system for industrial/factory environments.

Core goals:
- Let engineers place orders from workstations (station/bay context).
- Provide ETA prediction (AI-first, fallback-enabled).
- Coordinate kitchen and runner workflows.
- Offer role-based dashboards and operations.
- Support real-time updates and notifications.
- Provide testing, simulation, and CI/CD pipelines.

---

## 2) High-Level Architecture

Main modules:
- `backend/` — FastAPI application (API + auth + business logic + DB models + middleware + websockets).
- `frontend/` — React + Vite web app for all roles.
- `ai_module/` — ETA model training, loading, prediction, fallback logic.
- `automation/` — seed generation, load testing, behavior simulation.
- `tests/` — unit, integration, and end-to-end suites.
- `.github/workflows/` — CI/CD and retraining workflows.
- `docs/` — setup, API, DB schema, deployment, testing, AI notes.

Runtime components:
- API service (FastAPI / Uvicorn)
- Database (PostgreSQL in container mode, SQLite in local fallback mode)
- Redis (cache / real-time support)
- Frontend SPA (React)
- Optional model artifacts (`ai_module/models/*`)

---

## 3) Tech Stack Used

Backend:
- Python 3.11+
- FastAPI, Starlette middleware
- SQLAlchemy + Alembic
- PostgreSQL (`psycopg2-binary`), optional SQLite fallback
- Redis (`redis`, `aioredis`)
- JWT auth (`python-jose`)
- Password hashing (`passlib[bcrypt]`)
- Rate limiting (`slowapi`)
- Logging (`loguru`)

Frontend:
- React 18, React Router
- Vite
- Axios
- Tailwind CSS + PostCSS
- Jest + Testing Library
- Cypress

AI:
- scikit-learn
- pandas
- numpy
- joblib

Automation / Performance:
- Locust
- custom simulation scripts

DevOps / Repo Ops:
- Docker, Docker Compose
- GitHub Actions
- Dependabot, CODEOWNERS, templates

---

## 4) Backend Architecture (Detailed)

Entry point:
- `backend/main.py`

What it does:
- Loads settings from `backend/config.py`.
- Initializes DB tables on startup (`create_tables`).
- Attempts AI model load (with warning/fallback path).
- Registers CORS, logging middleware, error handlers, limiter.
- Mounts routers:
  - `auth_router`
  - `order_router`
  - `menu_router`
  - `kitchen_router`
  - `runner_router`
  - `admin_router`
  - `notification_router`
  - `trivia_router`
  - `health_router`

Core backend layers:
- `routers/` → API endpoints and role-guarded access.
- `services/` → business logic (orders, ETA, runners, kitchen, analytics, admin).
- `models/` → SQLAlchemy entities.
- `schemas/` → request/response validation.
- `database/` → engine/session/seed.
- `auth/` → JWT, dependency resolution, RBAC.
- `middleware/` → error handling, logging, rate limiting, CORS config helpers.
- `websocket/` → socket manager/event room support.
- `utils/` → constants, validators, helpers, ID generation.

---

## 5) Authentication & Authorization

Authentication:
- Login issues JWT access + refresh tokens.
- `auth/dependencies.py` resolves current user from bearer token.
- Inactive/deleted users are blocked.

Authorization (RBAC):
- Implemented in `auth/rbac.py`.
- Role checkers:
  - `require_admin`
  - `require_kitchen`
  - `require_runner`
  - `require_engineer`
  - `require_any_authenticated`

Permission model (project logic):
- Engineer: place/cancel own orders, view own orders, submit feedback.
- Kitchen: view kitchen queue, update kitchen statuses, menu availability.
- Runner: view assigned deliveries, update delivery statuses, update own status.
- Admin: aggregate access + management + reporting functions.

---

## 6) Database Design and Storage

### Schema coverage
The project defines 13 main entities (users, stations, menu, orders, order items, runners, status history, feedback, notifications, trivia questions/scores, AI training data, system logs).

### Actual storage location behavior
Two modes are used in this codebase:

1) Docker/Postgres mode:
- DB URL from compose/env points to PostgreSQL.
- Data persisted in Docker volume `pgdata`.

2) Local fallback mode:
- DB URL can be switched to SQLite.
- Example local file: `prosensia_test.db` at project root.

### DB bootstrap
- Engine/session in `backend/database/connection.py`.
- Table creation via `create_tables()`.
- Seed via `backend/database/seed_data.py`.

---

## 7) Seeded Users and Operational Identities

Seed script creates:
- Admin: `ADM-001` (`admin@prosensia.com`)
- Kitchen: `KIT-001`, `KIT-002`
- Runners: `RUN-001`..`RUN-005`
- Engineers: `ENG-001`..`ENG-010` (`engineer1@prosensia.com` ..)

Important note:
- Some docs mention older credentials (`test123` / `employee_id` payload), while the active backend/tests use email+password patterns (`engineer123`, etc.).
- Current working integration aligns with email login payload.

---

## 8) Frontend Architecture (Detailed)

Entry files:
- `frontend/src/main.jsx`
- `frontend/src/App.jsx`

Layering:
- `api/` → Axios instance + domain APIs.
- `context/` → auth/cart/order/socket/notification state.
- `hooks/` → reusable logic wrappers.
- `pages/` → role-specific and common screens.
- `components/` → UI blocks grouped by domain.
- `routes/` → route grouping and guard patterns.
- `services/` → client-side service utilities (cache, etc.).
- `utils/` → helpers/constants.

Role UI sections:
- engineer pages
- kitchen pages
- runner pages
- admin pages
- trivia pages
- auth/common pages

Frontend API behavior:
- Axios base URL from `VITE_API_URL` or fallback default.
- Auth token injection via interceptor.
- Error handling for 401/403/429.

---

## 9) QR / Station Flow (Current Implementation)

What exists now:
- Station records include `qr_token` and `qr_token_expires_at` in DB model + seeds.
- Frontend `MenuPage` reads `?station=Bay-XX` from URL query and sets cart station context.
- Cart allows manual station input (`Bay-12` format style).

What is currently partial:
- Full secure QR token verification pipeline is not fully enforced end-to-end in the main order flow.
- In practical terms, station context is primarily query-param/manual driven in frontend.

---

## 10) Order Lifecycle Engine

Order system includes:
- Place order
- Validate menu availability and priority
- Duplicate order protection window
- ETA prediction (AI/fallback)
- Runner assignment
- Status transitions with role constraints
- History tracking
- Feedback capture

Status logic is centralized in constants + services and is validated before transitions.

---

## 11) AI Module (Detailed)

Core files:
- `ai_module/core/feature_engineering.py`
- `ai_module/core/model_loader.py`
- `ai_module/core/predictor.py`
- `ai_module/core/fallback.py`

Scripts:
- `generate_data.py`
- `train_model.py`
- `evaluate_model.py`
- `retrain.py`
- `export_training_data.py`

Operational behavior:
- Attempts model-based ETA first.
- Falls back to deterministic rule-based ETA if model unavailable/error.
- Supports retraining workflow and metadata artifacts.

---

## 12) Automation and Simulation

`automation/` includes:
- data generation scripts for users/stations/menu/runners/trivia
- load test config + simulator + report generator
- locust test file
- simulation scripts for traffic/order flow/kitchen/runner behavior

Use cases:
- realistic synthetic data
- system stress tests
- performance reporting

---

## 13) Testing Strategy and Coverage Layout

Test directories:
- `tests/unit/ai`
- `tests/unit/backend`
- `tests/unit/frontend`
- `tests/integration`
- `tests/e2e`

Execution stack:
- Pytest (unit + integration)
- Jest (frontend unit)
- Cypress (E2E)
- Locust/custom scripts (load)

E2E specs cover login, order placement, tracking, error handling, and role flows (with some placeholder/no-test spec files present).

---

## 14) CI/CD and GitHub Automation

Workflows present:
- `ci.yml` → lint/test/build pipeline coverage for backend, AI, frontend.
- `cd.yml` → deployment pipeline logic.
- `ai_retrain.yml` → scheduled/manual AI retraining flow.

Repo operations helpers:
- `CODEOWNERS`
- `dependabot.yml`
- PR/Issue templates

---

## 15) Deployment Modes

1) Docker Compose:
- backend + frontend + postgres + redis
- healthchecks and networking configured

2) Manual local:
- separate backend/frontend processes
- external PostgreSQL + Redis expected
- optional SQLite fallback for local validation

---

## 16) Current Known Practical Notes

- Documentation and runtime credentials are not fully uniform across all docs/files.
- Some docs still mention older auth payload fields (`employee_id`) while current tested flows use `email`.
- CORS and host origin (`localhost` vs `127.0.0.1`) can impact browser login/network behavior if not aligned.
- In recent local validation runs, fallback SQLite pathing and CORS were adjusted for stable execution.

---

## 17) How to Read This Project Quickly (Suggested Path)

1. Read `README.md` for conceptual overview.
2. Open `backend/main.py` and `backend/config.py` for runtime wiring.
3. Read routers in `backend/routers/` for API boundaries.
4. Read services in `backend/services/` for business rules.
5. Read DB model + seed in `backend/models/` and `backend/database/seed_data.py`.
6. Read frontend route/page entry points in `frontend/src/pages` and `frontend/src/routes`.
7. Read AI core + scripts in `ai_module/core` and `ai_module/scripts`.
8. Read `tests/` and `.github/workflows/` for quality gates.

---

## 18) One-Line Summary

ProSensia Smart-Serve is a role-driven, AI-assisted, full-stack internal food delivery platform that combines FastAPI + React + SQL data modeling + real-time events + automation/testing pipelines for factory-scale operations.
