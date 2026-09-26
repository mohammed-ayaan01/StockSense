"""
Service: Stock Adjustment business logic.
Takes a physically counted quantity, computes delta vs recorded,
requires a reason, and rejects if result would be negative.
"""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.adjustment import StockAdjustment, AdjustmentStatus
from app.models.inventory import InventoryStock
from app.models.movement import StockMovement, MovementType


async def complete_adjustment(db: AsyncSession, adjustment_id: int, user_id: int | None) -> StockAdjustment:
    """
    Atomically:
    1. Lock adjustment row
    2. Snapshot current recorded qty
    3. Compute delta = counted - recorded
    4. Reject if result is negative
    5. Apply delta to stock, write movement
    6. Mark adjustment DONE
    """
    result = await db.execute(
        select(StockAdjustment)
        .where(StockAdjustment.id == adjustment_id)
        .with_for_update()
    )
    adj = result.scalar_one_or_none()
    if not adj:
        raise HTTPException(404, "Adjustment not found")
    if adj.status == AdjustmentStatus.DONE:
        raise HTTPException(409, "Adjustment already completed")
    if adj.status == AdjustmentStatus.CANCELLED:
        raise HTTPException(409, "Cannot complete a cancelled adjustment")

    now = datetime.now(timezone.utc)

    # Lock and get stock row
    stock_result = await db.execute(
        select(InventoryStock)
        .where(
            InventoryStock.product_id == adj.product_id,
            InventoryStock.location_id == adj.location_id,
        )
        .with_for_update()
    )
    stock = stock_result.scalar_one_or_none()
    recorded = stock.quantity if stock else 0.0
    delta = adj.counted_qty - recorded

    # Guard: result cannot be negative
    new_qty = recorded + delta
    if new_qty < 0:
        raise HTTPException(
            400,
            f"Adjustment would result in negative stock ({new_qty:.2f}). Rejected.",
        )

    # Update snapshot fields on adjustment
    adj.recorded_qty = recorded
    adj.delta = delta

    # Apply to stock
    if stock is None:
        stock = InventoryStock(
            product_id=adj.product_id, location_id=adj.location_id,
            quantity=adj.counted_qty, reserved=0.0, updated_at=now
        )
        db.add(stock)
    else:
        stock.quantity = adj.counted_qty
        stock.updated_at = now

    # Write movement
    db.add(StockMovement(
        movement_type=MovementType.ADJUSTMENT,
        product_id=adj.product_id,
        location_id=adj.location_id,
        quantity=delta,
        reference=adj.reference,
        reference_id=adj.id,
        notes=f"Adjustment: {adj.reason}",
        created_by=user_id,
        created_at=now,
    ))

    adj.status = AdjustmentStatus.DONE
    adj.done_at = now
    await db.commit()
    await db.refresh(adj)
    return adj


async def cancel_adjustment(db: AsyncSession, adjustment_id: int) -> StockAdjustment:
    result = await db.execute(
        select(StockAdjustment).where(StockAdjustment.id == adjustment_id).with_for_update()
    )
    adj = result.scalar_one_or_none()
    if not adj:
        raise HTTPException(404, "Adjustment not found")
    if adj.status == AdjustmentStatus.DONE:
        raise HTTPException(409, "Cannot cancel a completed adjustment")
    if adj.status == AdjustmentStatus.CANCELLED:
        raise HTTPException(409, "Already cancelled")
    adj.status = AdjustmentStatus.CANCELLED
    await db.commit()
    await db.refresh(adj)
    return adj
