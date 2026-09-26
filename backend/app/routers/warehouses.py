from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.location import Location
from app.schemas.warehouse import (
    WarehouseCreate, WarehouseUpdate, WarehouseOut,
    LocationCreate, LocationUpdate, LocationOut,
)

router = APIRouter(tags=["warehouses"])


# ── Warehouses ────────────────────────────────────────────────────────────────

@router.get("/warehouses", response_model=list[WarehouseOut])
async def list_warehouses(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(Warehouse).order_by(Warehouse.name))
    return result.scalars().all()


@router.post("/warehouses", response_model=WarehouseOut, status_code=201)
async def create_warehouse(data: WarehouseCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    existing = await db.execute(select(Warehouse).where(Warehouse.code == data.code.upper()))
    if existing.scalar_one_or_none():
        raise HTTPException(409, f"Warehouse code '{data.code}' already exists")
    wh = Warehouse(name=data.name, code=data.code.upper(), address=data.address)
    db.add(wh)
    await db.commit()
    await db.refresh(wh)
    return wh


@router.get("/warehouses/{wh_id}", response_model=WarehouseOut)
async def get_warehouse(wh_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(Warehouse).where(Warehouse.id == wh_id))
    wh = result.scalar_one_or_none()
    if not wh:
        raise HTTPException(404, "Warehouse not found")
    return wh


@router.patch("/warehouses/{wh_id}", response_model=WarehouseOut)
async def update_warehouse(wh_id: int, data: WarehouseUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(Warehouse).where(Warehouse.id == wh_id))
    wh = result.scalar_one_or_none()
    if not wh:
        raise HTTPException(404, "Warehouse not found")
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(wh, field, val)
    await db.commit()
    await db.refresh(wh)
    return wh


# ── Locations ─────────────────────────────────────────────────────────────────

@router.get("/locations", response_model=list[LocationOut])
async def list_locations(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
    warehouse_id: Optional[int] = Query(None),
):
    q = select(Location).options(selectinload(Location.warehouse))
    if warehouse_id:
        q = q.where(Location.warehouse_id == warehouse_id)
    result = await db.execute(q.order_by(Location.name))
    return result.scalars().all()


@router.post("/locations", response_model=LocationOut, status_code=201)
async def create_location(data: LocationCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    existing = await db.execute(
        select(Location).where(
            Location.warehouse_id == data.warehouse_id,
            Location.code == data.code,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, f"Location code '{data.code}' already exists in this warehouse")
    loc = Location(**data.model_dump())
    db.add(loc)
    await db.commit()
    result = await db.execute(
        select(Location).options(selectinload(Location.warehouse)).where(Location.id == loc.id)
    )
    return result.scalar_one()


@router.get("/locations/{loc_id}", response_model=LocationOut)
async def get_location(loc_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(
        select(Location).options(selectinload(Location.warehouse)).where(Location.id == loc_id)
    )
    loc = result.scalar_one_or_none()
    if not loc:
        raise HTTPException(404, "Location not found")
    return loc


@router.patch("/locations/{loc_id}", response_model=LocationOut)
async def update_location(loc_id: int, data: LocationUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(Location).where(Location.id == loc_id))
    loc = result.scalar_one_or_none()
    if not loc:
        raise HTTPException(404, "Location not found")
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(loc, field, val)
    await db.commit()
    result = await db.execute(
        select(Location).options(selectinload(Location.warehouse)).where(Location.id == loc_id)
    )
    return result.scalar_one()
