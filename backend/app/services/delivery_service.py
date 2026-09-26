"""
Service: Delivery business logic.
Pick -> Pack -> Validate (Done) with stock guard.
All stock mutations are transactional with row-level locking.
"""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.delivery import Delivery, DeliveryLine, DeliveryStatus
from app.models.inventory import InventoryStock
from app.models.movement import StockMovement, MovementType

# State machine allowed transitions
ALLOWED_TRANSITIONS = {
    DeliveryStatus.DRAFT: [DeliveryStatus.WAITING, DeliveryStatus.CANCELLED],
    DeliveryStatus.WAITING: [DeliveryStatus.READY, DeliveryStatus.CANCELLED],
    DeliveryStatus.READY: [DeliveryStatus.PICKING, DeliveryStatus.CANCELLED],
    DeliveryStatus.PICKING: [DeliveryStatus.PACKING, DeliveryStatus.CANCELLED],
    DeliveryStatus.PACKING: [DeliveryStatus.DONE, DeliveryStatus.CANCELLED],
    DeliveryStatus.DONE: [],
    DeliveryStatus.CANCELLED: [],
}


async def advance_delivery(db: AsyncSession, delivery_id: int, user_id: int | None) -> Delivery:
    """Advance delivery to next state in the Pick→Pack→Done pipeline."""
    result = await db.execute(
        select(Delivery)
        .where(Delivery.id == delivery_id)
        .options(selectinload(Delivery.lines))
        .with_for_update()
    )
    delivery = result.scalar_one_or_none()
    if not delivery:
        raise HTTPException(404, "Delivery not found")

    current = delivery.status
    transitions = ALLOWED_TRANSITIONS.get(current, [])
    # Find next non-cancel state
    next_states = [s for s in transitions if s != DeliveryStatus.CANCELLED]
    if not next_states:
        raise HTTPException(409, f"No forward transition from {current.value}")

    next_status = next_states[0]

    if next_status == DeliveryStatus.DONE:
        await _validate_and_deliver(db, delivery, user_id)
    else:
        delivery.status = next_status
        await db.commit()
        await db.refresh(delivery)

    return delivery


async def _validate_and_deliver(db: AsyncSession, delivery: Delivery, user_id: int | None) -> None:
    """
    Final validation step — check stock, deduct, write movements.
    All in one atomic transaction (already within with_for_update lock on delivery).
    """
    if not delivery.lines:
        raise HTTPException(400, "Delivery has no lines")

    now = datetime.now(timezone.utc)

    # First pass: validate all lines have sufficient stock (fail-fast before any mutation)
    for line in delivery.lines:
        stock_result = await db.execute(
            select(InventoryStock)
            .where(
                InventoryStock.product_id == line.product_id,
                InventoryStock.location_id == delivery.location_id,
            )
            .with_for_update()
        )
        stock = stock_result.scalar_one_or_none()
        available = (stock.quantity - stock.reserved) if stock else 0.0
        if available < line.requested_qty:
            raise HTTPException(
                400,
                f"Insufficient available stock for product {line.product_id}: "
                f"requested {line.requested_qty}, available {available:.2f}. "
                f"Delivery rejected — stock unchanged.",
            )

    # Second pass: mutate stock and write movements
    for line in delivery.lines:
        stock_result = await db.execute(
            select(InventoryStock)
            .where(
                InventoryStock.product_id == line.product_id,
                InventoryStock.location_id == delivery.location_id,
            )
            .with_for_update()
        )
        stock = stock_result.scalar_one_or_none()
        stock.quantity -= line.requested_qty
        stock.updated_at = now
        line.delivered_qty = line.requested_qty

        movement = StockMovement(
            movement_type=MovementType.DELIVERY,
            product_id=line.product_id,
            location_id=delivery.location_id,
            quantity=-line.requested_qty,
            reference=delivery.reference,
            reference_id=delivery.id,
            notes=f"Delivery validated: {delivery.reference}",
            created_by=user_id,
            created_at=now,
        )
        db.add(movement)

    delivery.status = DeliveryStatus.DONE
    delivery.done_at = now
    await db.commit()
    await db.refresh(delivery)


async def cancel_delivery(db: AsyncSession, delivery_id: int) -> Delivery:
    result = await db.execute(
        select(Delivery).where(Delivery.id == delivery_id).with_for_update()
    )
    delivery = result.scalar_one_or_none()
    if not delivery:
        raise HTTPException(404, "Delivery not found")
    if delivery.status == DeliveryStatus.DONE:
        raise HTTPException(409, "Cannot cancel a completed delivery")
    if delivery.status == DeliveryStatus.CANCELLED:
        raise HTTPException(409, "Already cancelled")
    delivery.status = DeliveryStatus.CANCELLED
    await db.commit()
    await db.refresh(delivery)
    return delivery
