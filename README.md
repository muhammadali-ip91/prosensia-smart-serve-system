# ProSensia Smart-Serve

Smart internal food-ordering and delivery platform for industrial environments with AI ETA prediction, live status tracking, role-based dashboards, and operational analytics.

## What This Project Includes

- **Engineer flow**: place orders, track delivery, feedback, trivia while waiting.
- **Kitchen flow**: incoming/preparing/ready queues + kitchen open/close controls.
- **Runner flow**: assigned deliveries and status transitions.
- **Admin flow**: system KPIs, live orders, user/menu/trivia management.
- **AI module**: ETA prediction using a trained sklearn model (`eta_model.pkl`).

## Architecture (High-Level)

- **Frontend**: React + Vite + Tailwind (`frontend/`)
- **Backend**: FastAPI + SQLAlchemy + Socket.IO (`backend/`)
- **AI**: Pandas / NumPy / Scikit-learn (`ai_module/`)
- **Automation/Testing**: pytest, Cypress, Locust (`tests/`, `automation/`)

## Project Structure

```text
prosensia-smart-serve-system/
├── backend/            # FastAPI APIs, auth, services, DB models
├── frontend/           # React UI
├── ai_module/          # Model training/loading/evaluation
├── automation/         # Load testing and simulation scripts
├── tests/              # Integration and E2E tests
├── docs/               # Technical documentation
├── scripts/            # Utility scripts (run, test, validate, seed)
├── docker-compose.yml
└── README.md
```

## Local Run (Windows, Recommended)

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### 1) Install dependencies

```powershell
# from repo root
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
pip install -r ai_module/requirements.txt
pip install -r automation/requirements.txt

cd frontend
npm install
cd ..
```

### 2) Start app

```powershell
.\scripts\run-local.ps1
```

This opens two terminals:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

### 3) Health check

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Default Demo Credentials

- Admin: `admin@prosensia.com` / `admin123`
- Engineer: `engineer1@prosensia.com` / `engineer123`
- Kitchen: `kitchen1@prosensia.com` / `kitchen123`
- Runner: `runner1@prosensia.com` / `runner123`

## AI Model Notes

- Active model path: `ai_module/models/eta_model.pkl`
- Health endpoint shows model load status and MAE.
- If model is missing/corrupt, system falls back to rule-based ETA logic.

Train/retrain model:

```powershell
.\.venv\Scripts\Activate.ps1
python -m ai_module.scripts.train_model
```

## Validation and Testing

Run full validation (backend + frontend + integration + Cypress):

```powershell
.\scripts\run_validation.ps1
```

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
