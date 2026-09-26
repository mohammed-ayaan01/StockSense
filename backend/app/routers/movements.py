from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.movement import StockMovement, MovementType
from app.schemas.movement import MovementOut

router = APIRouter(prefix="/movements", tags=["movements"])


@router.get("", response_model=list[MovementOut])
async def list_movements(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
    product_id: Optional[int] = Query(None),
    location_id: Optional[int] = Query(None),
    movement_type: Optional[MovementType] = Query(None),
    reference: Optional[str] = Query(None),
    limit: int = Query(200, le=500),
    offset: int = Query(0, ge=0),
):
    q = select(StockMovement)
    if product_id:
        q = q.where(StockMovement.product_id == product_id)
    if location_id:
        q = q.where(StockMovement.location_id == location_id)
    if movement_type:
        q = q.where(StockMovement.movement_type == movement_type)
    if reference:
        q = q.where(StockMovement.reference.ilike(f"%{reference}%"))
    result = await db.execute(q.order_by(StockMovement.created_at.desc()).offset(offset).limit(limit))
    return result.scalars().all()
