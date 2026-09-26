# StockSense

**Inventory & Warehouse Management System** — Odoo x GCET Hackathon 2026

**Team:** Mohammed Abdul Raheem (Lead) · Piyush Jha · Mohd Ibrahim · Mohammed Ayaan

---

## Running Locally (No Docker)

This is how we are currently running the project — backend with a local Python virtualenv + SQLite, frontend with Node.

### Prerequisites

| Tool | Version |
|---|---|
| Python | 3.12+ |
| Node.js | 18+ |
| npm | 9+ |

---

### 1. Clone the repo

```bash
git clone https://github.com/akhi-mohammmed-o7/StockSense-IARE.git
cd StockSense-IARE
```

---

### 2. Backend (FastAPI + SQLite)

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# The backend/.env is already configured for SQLite (no Postgres needed):
# DATABASE_URL=sqlite+aiosqlite:///stocksense.db

# Run the dev server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> The app auto-creates the SQLite database (`backend/stocksense.db`) and seeds
> default data (admin user, categories, units, warehouses) on first startup.

Backend runs at → **http://localhost:8000**  
API docs (Swagger UI) → **http://localhost:8000/docs**

---

### 3. Frontend (React + Vite)

Open a **second terminal**:

```bash
cd frontend

# Install dependencies (already done if node_modules exists)
npm install

# Start the dev server
npm run dev
```

Frontend runs at → **http://localhost:5173**  
*(If 5173 is occupied, Vite will automatically pick the next free port, e.g. 5174)*

---

### 4. Default Login

```
Email:    admin@stocksense.com
Password: admin123
```

---

## Environment Variables

### `backend/.env` (SQLite — local dev)

```env
DATABASE_URL=sqlite+aiosqlite:///stocksense.db
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
OTP_EXPIRE_MINUTES=10
APP_ENV=development
DEBUG=true
FRONTEND_URL=http://localhost:5173
```

> **Note:** `aiosqlite` is used as the async SQLite driver. No Postgres or Docker required for local dev.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + TypeScript + Vite 5 + Tailwind CSS 4 |
| State | Zustand + TanStack Query |
| Backend | FastAPI (Python 3.12) + Uvicorn |
| Database | SQLite (local dev) / PostgreSQL (production/Docker) |
| ORM | SQLAlchemy 2 (async) + Alembic |
| Auth | JWT + bcrypt + OTP |

---

## Architecture

```
StockSense/
├── backend/
│   ├── .venv/              # Python virtual environment
│   ├── app/
│   │   ├── core/           # config, database, security, deps
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── routers/        # API route handlers
│   │   └── services/       # Business logic (transactional)
│   ├── migrations/         # Alembic migrations
│   ├── .env                # Local env (SQLite)
│   ├── requirements.txt
│   └── stocksense.db       # SQLite database file (auto-created)
├── frontend/
│   ├── node_modules/
│   ├── src/
│   │   ├── api/            # Axios API client
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page-level components
│   │   └── store/          # Zustand state management
│   ├── package.json
│   └── vite.config.ts
├── .env                    # Root env (for Docker Compose / Postgres)
├── .env.example
└── docker-compose.yml      # Production / team setup (Postgres)
```

---

## Features

- ✅ JWT Auth + OTP-based password reset
- ✅ Products (Category + Unit of Measure)
- ✅ Warehouses & Locations
- ✅ Receipts (Draft → Ready → Done → Cancelled) — increases stock
- ✅ Deliveries (Pick → Pack → Validate) — decreases stock, rejects insufficient
- ✅ Internal Transfers (atomic cross-location, total stock preserved)
- ✅ Stock Adjustments (counted qty → delta → reason required)
- ✅ Move History (filterable audit log of all stock movements)
- ✅ Dashboard with 5 live KPIs from real database
- ✅ Role-based access (ADMIN / MANAGER / STAFF)
- ✅ Fully transactional — no double-completion, no negative stock ever

---

## API Reference

Full Swagger UI at `http://localhost:8000/docs`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Login, returns JWT |
| POST | `/api/auth/forgot-password` | Request OTP |
| POST | `/api/auth/reset-password` | Reset with OTP |
| GET | `/api/dashboard/kpis` | 5 live KPIs |
| GET | `/api/products` | List products (search/filter) |
| POST | `/api/receipts/{id}/validate` | Complete receipt, increase stock |
| POST | `/api/deliveries/{id}/advance` | Advance delivery state |
| POST | `/api/transfers/{id}/validate` | Atomic cross-location transfer |
| POST | `/api/adjustments/{id}/validate` | Apply stock adjustment |
| GET | `/api/movements` | Move history (filterable) |

---

## Stock Safety Rules

1. **Receipts** — stock increases only on final `DONE` state, transactionally
2. **Deliveries** — stock decreases only on `DONE`; all lines checked for availability **before** any mutation; rejects with clear error if insufficient
3. **Transfers** — both source decrease and destination increase happen in one transaction; total stock across locations is unchanged
4. **Adjustments** — takes physically *counted* quantity; delta computed from recorded; cannot result in negative stock; reason mandatory
5. **All** — row-level `SELECT ... FOR UPDATE` prevents double-completion and race conditions

---

## Running Tests

```bash
cd backend
.venv\Scripts\activate
pytest tests/ -v
```

---

## Docker (Production / Postgres)

If you want to run with Postgres instead of SQLite:

```bash
# From the project root
cp .env.example .env   # edit credentials if needed
docker compose up --build

# App:      http://localhost:5173
# API:      http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Evaluator Access

Evaluator GitHub: `mebh-odoo` — should be added as a repo collaborator with Read access.
