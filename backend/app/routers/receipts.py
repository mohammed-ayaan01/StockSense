from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.receipt import Receipt, ReceiptLine, ReceiptStatus
from app.schemas.receipt import ReceiptCreate, ReceiptOut
from app.services import receipt_service
import random, string

router = APIRouter(prefix="/receipts", tags=["receipts"])


def _gen_ref() -> str:
    suffix = "".join(random.choices(string.digits, k=5))
    return f"REC/{suffix}"


@router.get("", response_model=list[ReceiptOut])
async def list_receipts(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
    status: Optional[ReceiptStatus] = Query(None),
    location_id: Optional[int] = Query(None),
):
    q = select(Receipt).options(selectinload(Receipt.lines))
    if status:
        q = q.where(Receipt.status == status)
    if location_id:
        q = q.where(Receipt.location_id == location_id)
    result = await db.execute(q.order_by(Receipt.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=ReceiptOut, status_code=201)
async def create_receipt(
    data: ReceiptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not data.lines:
        raise HTTPException(400, "Receipt must have at least one line")
    receipt = Receipt(
        reference=_gen_ref(),
        supplier=data.supplier,
        location_id=data.location_id,
        notes=data.notes,
        scheduled_date=data.scheduled_date,
        created_by=current_user.id,
    )
    db.add(receipt)
    await db.flush()
    for line in data.lines:
        if line.expected_qty <= 0:
            raise HTTPException(400, "Expected quantity must be > 0")
        db.add(ReceiptLine(receipt_id=receipt.id, product_id=line.product_id, expected_qty=line.expected_qty))
    await db.commit()
    result = await db.execute(
        select(Receipt).options(selectinload(Receipt.lines)).where(Receipt.id == receipt.id)
    )
    return result.scalar_one()


@router.get("/{receipt_id}", response_model=ReceiptOut)
async def get_receipt(receipt_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(
        select(Receipt).options(selectinload(Receipt.lines)).where(Receipt.id == receipt_id)
    )
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise HTTPException(404, "Receipt not found")
    return receipt


@router.post("/{receipt_id}/confirm", response_model=ReceiptOut)
async def confirm_receipt(receipt_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Move DRAFT -> READY."""
    result = await db.execute(select(Receipt).where(Receipt.id == receipt_id))
    receipt = result.scalar_one_or_none()
    if not receipt:
        raise HTTPException(404, "Receipt not found")
    if receipt.status != ReceiptStatus.DRAFT:
        raise HTTPException(409, f"Cannot confirm receipt in status {receipt.status.value}")
    receipt.status = ReceiptStatus.READY
    await db.commit()
    result = await db.execute(select(Receipt).options(selectinload(Receipt.lines)).where(Receipt.id == receipt_id))
    return result.scalar_one()


@router.post("/{receipt_id}/validate", response_model=ReceiptOut)
async def validate_receipt(receipt_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Complete receipt — increases stock transactionally."""
    return await receipt_service.complete_receipt(db, receipt_id, current_user.id)


@router.post("/{receipt_id}/cancel", response_model=ReceiptOut)
async def cancel_receipt(receipt_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    return await receipt_service.cancel_receipt(db, receipt_id)
