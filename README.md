# StockSense

**Inventory & Warehouse Management System** — Odoo x GCET Hackathon 2026

**Team:** Mohammed Abdul Raheem (Lead) · Piyush Jha · Mohd Ibrahim · Mohammed Ayaan

---

## Quick Start

```bash
# 1. Clone and configure
git clone https://github.com/akhi-mohammmed-o7/StockSense-IARE.git
cd StockSense-IARE
cp .env.example .env  # edit if needed

# 2. Start everything
docker compose up --build

# App:      http://localhost:5173
# API:      http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Default login:** `admin@stocksense.com` / `admin123`

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

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS |
| Backend | FastAPI (Python 3.12) |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy (async) + Alembic |
| Auth | JWT + bcrypt + OTP |
| Container | Docker + Docker Compose |

---

## Architecture

```
StockSense-IARE/
├── backend/          # FastAPI app
│   ├── app/
│   │   ├── core/     # config, database, security, deps
│   │   ├── models/   # SQLAlchemy ORM models
│   │   ├── schemas/  # Pydantic request/response schemas
│   │   ├── routers/  # API route handlers
│   │   └── services/ # Business logic (transactional operations)
│   └── migrations/   # Alembic migrations
├── frontend/         # React + TypeScript + Vite
│   └── src/
│       ├── api/      # Axios API client
│       ├── components/ # Reusable UI components
│       ├── pages/    # Page-level components
│       └── store/    # Zustand state management
└── docker-compose.yml
```

---

## API Documentation

Full OpenAPI docs available at `http://localhost:8000/docs`

### Key Endpoints

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
pip install -r requirements.txt
pytest tests/ -v
```

---

## Environment Variables

See `.env.example` for all required variables. Never commit `.env`.

---

## Evaluator Access

Evaluator GitHub: `mebh-odoo` — should be added as a repo collaborator with Read access.
