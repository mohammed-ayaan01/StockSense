from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.adjustment import StockAdjustment, AdjustmentStatus
from app.models.inventory import InventoryStock
from app.schemas.adjustment import AdjustmentCreate, AdjustmentOut
from app.services import adjustment_service
import random, string

router = APIRouter(prefix="/adjustments", tags=["adjustments"])


def _gen_ref() -> str:
    suffix = "".join(random.choices(string.digits, k=5))
    return f"ADJ/{suffix}"


@router.get("", response_model=list[AdjustmentOut])
async def list_adjustments(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
    status: Optional[AdjustmentStatus] = Query(None),
    product_id: Optional[int] = Query(None),
):
    q = select(StockAdjustment)
    if status:
        q = q.where(StockAdjustment.status == status)
    if product_id:
        q = q.where(StockAdjustment.product_id == product_id)
    result = await db.execute(q.order_by(StockAdjustment.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=AdjustmentOut, status_code=201)
async def create_adjustment(
    data: AdjustmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not data.reason or not data.reason.strip():
        raise HTTPException(400, "Reason is required for stock adjustments")
    if data.counted_qty < 0:
        raise HTTPException(400, "Counted quantity cannot be negative")

    # Snapshot current recorded qty
    stock_result = await db.execute(
        select(InventoryStock).where(
            InventoryStock.product_id == data.product_id,
            InventoryStock.location_id == data.location_id,
        )
    )
    stock = stock_result.scalar_one_or_none()
    recorded = stock.quantity if stock else 0.0
    delta = data.counted_qty - recorded

    adj = StockAdjustment(
        reference=_gen_ref(),
        product_id=data.product_id,
        location_id=data.location_id,
        counted_qty=data.counted_qty,
        recorded_qty=recorded,
        delta=delta,
        reason=data.reason.strip(),
        created_by=current_user.id,
    )
    db.add(adj)
    await db.commit()
    await db.refresh(adj)
    return adj


@router.get("/{adj_id}", response_model=AdjustmentOut)
async def get_adjustment(adj_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(StockAdjustment).where(StockAdjustment.id == adj_id))
    adj = result.scalar_one_or_none()
    if not adj:
        raise HTTPException(404, "Adjustment not found")
    return adj


@router.post("/{adj_id}/validate", response_model=AdjustmentOut)
async def validate_adjustment(adj_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Applies the counted quantity to stock, writes movement, marks DONE."""
    return await adjustment_service.complete_adjustment(db, adj_id, current_user.id)


@router.post("/{adj_id}/cancel", response_model=AdjustmentOut)
async def cancel_adjustment(adj_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    return await adjustment_service.cancel_adjustment(db, adj_id)
