from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.inventory import InventoryStock
from app.models.receipt import Receipt, ReceiptStatus
from app.models.delivery import Delivery, DeliveryStatus
from app.models.transfer import Transfer, TransferStatus
from app.models.product import Product
from app.models.movement import StockMovement
from app.schemas.dashboard import DashboardKPIs

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis", response_model=DashboardKPIs)
async def get_kpis(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    # KPI 1: Total Products in Stock (distinct products with quantity > 0)
    total_in_stock = await db.execute(
        select(func.count(func.distinct(InventoryStock.product_id)))
        .where(InventoryStock.quantity > 0)
    )
    total_products_in_stock = total_in_stock.scalar() or 0

    # KPI 2: Low Stock / Out of Stock Items
    # Out of stock: quantity = 0
    # Low stock: quantity > 0 but quantity <= reorder_threshold
    low_or_out = await db.execute(
        select(func.count(func.distinct(InventoryStock.product_id)))
        .join(Product, Product.id == InventoryStock.product_id)
        .where(
            (InventoryStock.quantity == 0) |
            (
                (Product.reorder_threshold != None) &  # noqa: E711
                (InventoryStock.quantity > 0) &
                (InventoryStock.quantity <= Product.reorder_threshold)
            )
        )
    )
    low_stock_or_out = low_or_out.scalar() or 0

    # KPI 3: Pending Receipts (DRAFT + READY)
    pending_receipts_q = await db.execute(
        select(func.count(Receipt.id))
        .where(Receipt.status.in_([ReceiptStatus.DRAFT, ReceiptStatus.READY]))
    )
    pending_receipts = pending_receipts_q.scalar() or 0

    # KPI 4: Pending Deliveries (not DONE, not CANCELLED)
    pending_deliveries_q = await db.execute(
        select(func.count(Delivery.id))
        .where(Delivery.status.notin_([DeliveryStatus.DONE, DeliveryStatus.CANCELLED]))
    )
    pending_deliveries = pending_deliveries_q.scalar() or 0

    # KPI 5: Internal Transfers Scheduled (DRAFT + READY)
    scheduled_transfers_q = await db.execute(
        select(func.count(Transfer.id))
        .where(Transfer.status.in_([TransferStatus.DRAFT, TransferStatus.READY]))
    )
    internal_transfers_scheduled = scheduled_transfers_q.scalar() or 0

    return DashboardKPIs(
        total_products_in_stock=total_products_in_stock,
        low_stock_or_out_of_stock=low_stock_or_out,
        pending_receipts=pending_receipts,
        pending_deliveries=pending_deliveries,
        internal_transfers_scheduled=internal_transfers_scheduled,
    )


@router.get("/recent-movements")
async def get_recent_movements(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(
        select(StockMovement).order_by(StockMovement.created_at.desc()).limit(10)
    )
    movements = result.scalars().all()
    return [
        {
            "id": m.id,
            "type": m.movement_type.value,
            "reference": m.reference,
            "quantity": m.quantity,
            "created_at": m.created_at,
        }
        for m in movements
    ]
