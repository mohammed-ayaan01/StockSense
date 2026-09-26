from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.transfer import Transfer, TransferLine, TransferStatus
from app.schemas.transfer import TransferCreate, TransferOut
from app.services import transfer_service
import random, string

router = APIRouter(prefix="/transfers", tags=["transfers"])


def _gen_ref() -> str:
    suffix = "".join(random.choices(string.digits, k=5))
    return f"INT/{suffix}"


@router.get("", response_model=list[TransferOut])
async def list_transfers(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
    status: Optional[TransferStatus] = Query(None),
):
    q = select(Transfer).options(selectinload(Transfer.lines))
    if status:
        q = q.where(Transfer.status == status)
    result = await db.execute(q.order_by(Transfer.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=TransferOut, status_code=201)
async def create_transfer(
    data: TransferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.src_location_id == data.dst_location_id:
        raise HTTPException(400, "Source and destination locations must be different")
    if not data.lines:
        raise HTTPException(400, "Transfer must have at least one line")
    transfer = Transfer(
        reference=_gen_ref(),
        src_location_id=data.src_location_id,
        dst_location_id=data.dst_location_id,
        notes=data.notes,
        scheduled_date=data.scheduled_date,
        created_by=current_user.id,
    )
    db.add(transfer)
    await db.flush()
    for line in data.lines:
        if line.quantity <= 0:
            raise HTTPException(400, "Transfer quantity must be > 0")
        db.add(TransferLine(transfer_id=transfer.id, product_id=line.product_id, quantity=line.quantity))
    await db.commit()
    result = await db.execute(
        select(Transfer).options(selectinload(Transfer.lines)).where(Transfer.id == transfer.id)
    )
    return result.scalar_one()


@router.get("/{transfer_id}", response_model=TransferOut)
async def get_transfer(transfer_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(
        select(Transfer).options(selectinload(Transfer.lines)).where(Transfer.id == transfer_id)
    )
    transfer = result.scalar_one_or_none()
    if not transfer:
        raise HTTPException(404, "Transfer not found")
    return transfer


@router.post("/{transfer_id}/validate", response_model=TransferOut)
async def validate_transfer(transfer_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Atomically deduct from source, add to destination, write two movements."""
    return await transfer_service.complete_transfer(db, transfer_id, current_user.id)


@router.post("/{transfer_id}/cancel", response_model=TransferOut)
async def cancel_transfer(transfer_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    return await transfer_service.cancel_transfer(db, transfer_id)
