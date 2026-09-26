from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.inventory import InventoryStock
from app.models.product import Product
from app.models.location import Location

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("")
async def get_inventory(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
    product_id: Optional[int] = Query(None),
    location_id: Optional[int] = Query(None),
    warehouse_id: Optional[int] = Query(None),
):
    q = (
        select(InventoryStock)
        .options(
            selectinload(InventoryStock.product).selectinload(Product.category),
            selectinload(InventoryStock.product).selectinload(Product.unit_of_measure),
            selectinload(InventoryStock.location).selectinload(Location.warehouse),
        )
    )
    if product_id:
        q = q.where(InventoryStock.product_id == product_id)
    if location_id:
        q = q.where(InventoryStock.location_id == location_id)
    if warehouse_id:
        q = q.join(Location).where(Location.warehouse_id == warehouse_id)

    result = await db.execute(q)
    stocks = result.scalars().all()

    return [
        {
            "id": s.id,
            "product_id": s.product_id,
            "product_name": s.product.name if s.product else None,
            "product_sku": s.product.sku if s.product else None,
            "category": s.product.category.name if s.product and s.product.category else None,
            "uom": s.product.unit_of_measure.abbreviation if s.product and s.product.unit_of_measure else None,
            "location_id": s.location_id,
            "location_name": s.location.name if s.location else None,
            "location_code": s.location.code if s.location else None,
            "warehouse_id": s.location.warehouse_id if s.location else None,
            "warehouse_name": s.location.warehouse.name if s.location and s.location.warehouse else None,
            "quantity": s.quantity,
            "reserved": s.reserved,
            "free_to_use": s.quantity - s.reserved,
            "reorder_threshold": s.product.reorder_threshold if s.product else None,
            "updated_at": s.updated_at,
        }
        for s in stocks
    ]
