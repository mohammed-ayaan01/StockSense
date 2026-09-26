"""
Service: Internal Transfer business logic.
Moves stock atomically from src_location to dst_location.
Total stock across both locations is unchanged after transfer.
"""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.transfer import Transfer, TransferLine, TransferStatus
from app.models.inventory import InventoryStock
from app.models.movement import StockMovement, MovementType


async def _get_or_create_stock(db: AsyncSession, product_id: int, location_id: int) -> InventoryStock:
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


async def complete_transfer(db: AsyncSession, transfer_id: int, user_id: int | None) -> Transfer:
    """
    Atomically:
    1. Lock transfer row
    2. Validate src != dst
    3. For each line: check src has enough stock
    4. Deduct from src, add to dst, write two movements per line
    5. Mark transfer DONE
    """
    result = await db.execute(
        select(Transfer)
        .where(Transfer.id == transfer_id)
        .options(selectinload(Transfer.lines))
        .with_for_update()
    )
    transfer = result.scalar_one_or_none()
    if not transfer:
        raise HTTPException(404, "Transfer not found")
    if transfer.status == TransferStatus.DONE:
        raise HTTPException(409, "Transfer already completed")
    if transfer.status == TransferStatus.CANCELLED:
        raise HTTPException(409, "Cannot complete a cancelled transfer")
    if transfer.src_location_id == transfer.dst_location_id:
        raise HTTPException(400, "Source and destination locations must be different")
    if not transfer.lines:
        raise HTTPException(400, "Transfer has no lines")

    now = datetime.now(timezone.utc)

    # First pass: validate sufficient stock at source
    for line in transfer.lines:
        src_stock_result = await db.execute(
            select(InventoryStock)
            .where(
                InventoryStock.product_id == line.product_id,
                InventoryStock.location_id == transfer.src_location_id,
            )
            .with_for_update()
        )
        src_stock = src_stock_result.scalar_one_or_none()
        available = (src_stock.quantity - src_stock.reserved) if src_stock else 0.0
        if available < line.quantity:
            raise HTTPException(
                400,
                f"Insufficient stock at source for product {line.product_id}: "
                f"need {line.quantity}, available {available:.2f}",
            )

    # Second pass: mutate atomically
    for line in transfer.lines:
        src_stock = await _get_or_create_stock(db, line.product_id, transfer.src_location_id)
        dst_stock = await _get_or_create_stock(db, line.product_id, transfer.dst_location_id)

        src_stock.quantity -= line.quantity
        src_stock.updated_at = now
        dst_stock.quantity += line.quantity
        dst_stock.updated_at = now

        # Two movements: one out, one in
        db.add(StockMovement(
            movement_type=MovementType.TRANSFER_OUT,
            product_id=line.product_id,
            location_id=transfer.src_location_id,
            quantity=-line.quantity,
            reference=transfer.reference,
            reference_id=transfer.id,
            notes=f"Transfer out: {transfer.reference}",
            created_by=user_id,
            created_at=now,
        ))
        db.add(StockMovement(
            movement_type=MovementType.TRANSFER_IN,
            product_id=line.product_id,
            location_id=transfer.dst_location_id,
            quantity=line.quantity,
            reference=transfer.reference,
            reference_id=transfer.id,
            notes=f"Transfer in: {transfer.reference}",
            created_by=user_id,
            created_at=now,
        ))

    transfer.status = TransferStatus.DONE
    transfer.done_at = now
    await db.commit()
    await db.refresh(transfer)
    return transfer


async def cancel_transfer(db: AsyncSession, transfer_id: int) -> Transfer:
    result = await db.execute(
        select(Transfer).where(Transfer.id == transfer_id).with_for_update()
    )
    transfer = result.scalar_one_or_none()
    if not transfer:
        raise HTTPException(404, "Transfer not found")
    if transfer.status == TransferStatus.DONE:
        raise HTTPException(409, "Cannot cancel a completed transfer")
    if transfer.status == TransferStatus.CANCELLED:
        raise HTTPException(409, "Already cancelled")
    transfer.status = TransferStatus.CANCELLED
    await db.commit()
    await db.refresh(transfer)
    return transfer
