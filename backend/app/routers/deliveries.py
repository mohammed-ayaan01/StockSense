from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.delivery import Delivery, DeliveryLine, DeliveryStatus
from app.schemas.delivery import DeliveryCreate, DeliveryOut
from app.services import delivery_service
import random, string

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


def _gen_ref() -> str:
    suffix = "".join(random.choices(string.digits, k=5))
    return f"DEL/{suffix}"


@router.get("", response_model=list[DeliveryOut])
async def list_deliveries(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
    status: Optional[DeliveryStatus] = Query(None),
    location_id: Optional[int] = Query(None),
):
    q = select(Delivery).options(selectinload(Delivery.lines))
    if status:
        q = q.where(Delivery.status == status)
    if location_id:
        q = q.where(Delivery.location_id == location_id)
    result = await db.execute(q.order_by(Delivery.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=DeliveryOut, status_code=201)
async def create_delivery(
    data: DeliveryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not data.lines:
        raise HTTPException(400, "Delivery must have at least one line")
    delivery = Delivery(
        reference=_gen_ref(),
        customer=data.customer,
        location_id=data.location_id,
        notes=data.notes,
        scheduled_date=data.scheduled_date,
        created_by=current_user.id,
    )
    db.add(delivery)
    await db.flush()
    for line in data.lines:
        if line.requested_qty <= 0:
            raise HTTPException(400, "Requested quantity must be > 0")
        db.add(DeliveryLine(delivery_id=delivery.id, product_id=line.product_id, requested_qty=line.requested_qty))
    await db.commit()
    result = await db.execute(
        select(Delivery).options(selectinload(Delivery.lines)).where(Delivery.id == delivery.id)
    )
    return result.scalar_one()


@router.get("/{delivery_id}", response_model=DeliveryOut)
async def get_delivery(delivery_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(
        select(Delivery).options(selectinload(Delivery.lines)).where(Delivery.id == delivery_id)
    )
    delivery = result.scalar_one_or_none()
    if not delivery:
        raise HTTPException(404, "Delivery not found")
    return delivery


@router.post("/{delivery_id}/advance", response_model=DeliveryOut)
async def advance_delivery(delivery_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Advance: DRAFT→WAITING→READY→PICKING→PACKING→DONE. Final step validates and deducts stock."""
    return await delivery_service.advance_delivery(db, delivery_id, current_user.id)


@router.post("/{delivery_id}/cancel", response_model=DeliveryOut)
async def cancel_delivery(delivery_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    return await delivery_service.cancel_delivery(db, delivery_id)
