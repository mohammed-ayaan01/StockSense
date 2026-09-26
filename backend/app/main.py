from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.routers import auth, products, warehouses, inventory, receipts, deliveries, transfers, adjustments, movements, dashboard

settings = get_settings()

app = FastAPI(
    title="StockSense API",
    description="Inventory & Warehouse Management System — Odoo x GCET Hackathon 2026",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(warehouses.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(receipts.router, prefix="/api")
app.include_router(deliveries.router, prefix="/api")
app.include_router(transfers.router, prefix="/api")
app.include_router(adjustments.router, prefix="/api")
app.include_router(movements.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "stocksense-api"}
