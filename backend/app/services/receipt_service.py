"""
Service: Receipt business logic.
Handles Draft -> Ready -> Done -> Cancelled transitions.
All stock mutations are transactional with row-level locking.
"""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.receipt import Receipt, ReceiptLine, ReceiptStatus
from app.models.inventory import InventoryStock
from app.models.movement import StockMovement, MovementType


async def _get_or_create_stock(db: AsyncSession, product_id: int, location_id: int) -> InventoryStock:
    """Get existing stock row or create it with quantity=0. Uses FOR UPDATE for safety."""
    result = await db.execute(
        select(InventoryStock)
        .where(InventoryStock.product_id == product_id, InventoryStock.location_id == location_id)
        .with_for_update()
    )
    stock = result.scalar_one_or_none()
    if stock is None:
        stock = InventoryStock(product_id=product_id, location_id=location_id, quantity=0.0, reserved=0.0)
        db.add(stock)
        await db.flush()
    return stock


async def complete_receipt(db: AsyncSession, receipt_id: int, user_id: int | None) -> Receipt:
    """
    Atomically:
    1. Lock receipt row (prevent double-complete)
    2. Validate state
    3. For each line: increase stock, write movement
    4. Mark receipt DONE
    """
    result = await db.execute(
        select(Receipt)
        .where(Receipt.id == receipt_id)
        .options(selectinload(Receipt.lines))
        .with_for_update()
    )
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise HTTPException(404, "Receipt not found")
    if receipt.status == ReceiptStatus.DONE:
        raise HTTPException(409, "Receipt already completed")
    if receipt.status == ReceiptStatus.CANCELLED:
        raise HTTPException(409, "Cannot complete a cancelled receipt")
    if receipt.status not in (ReceiptStatus.DRAFT, ReceiptStatus.READY):
        raise HTTPException(409, f"Cannot complete receipt in status {receipt.status}")
    if not receipt.lines:
        raise HTTPException(400, "Receipt has no lines")

    now = datetime.now(timezone.utc)

    for line in receipt.lines:
        qty = line.expected_qty  # receive full expected quantity
        stock = await _get_or_create_stock(db, line.product_id, receipt.location_id)
        stock.quantity += qty
        stock.updated_at = now
        line.received_qty = qty

        movement = StockMovement(
            movement_type=MovementType.RECEIPT,
            product_id=line.product_id,
            location_id=receipt.location_id,
            quantity=qty,
            reference=receipt.reference,
            reference_id=receipt.id,
            notes=f"Receipt completed: {receipt.reference}",
            created_by=user_id,
            created_at=now,
        )
        db.add(movement)

    receipt.status = ReceiptStatus.DONE
    receipt.done_at = now
    await db.commit()
    await db.refresh(receipt)
    return receipt


async def cancel_receipt(db: AsyncSession, receipt_id: int) -> Receipt:
    result = await db.execute(
        select(Receipt).where(Receipt.id == receipt_id).with_for_update()
    )
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise HTTPException(404, "Receipt not found")
    if receipt.status == ReceiptStatus.DONE:
        raise HTTPException(409, "Cannot cancel a completed receipt")
    if receipt.status == ReceiptStatus.CANCELLED:
        raise HTTPException(409, "Already cancelled")
    receipt.status = ReceiptStatus.CANCELLED
    await db.commit()
    await db.refresh(receipt)
    return receipt
