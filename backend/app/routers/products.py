from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.product import Category, UnitOfMeasure, Product
from app.schemas.product import (
    CategoryCreate, CategoryOut,
    UoMCreate, UoMOut,
    ProductCreate, ProductUpdate, ProductOut,
)

router = APIRouter(tags=["products"])

# ── Categories ───────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@router.post("/categories", response_model=CategoryOut, status_code=201)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    existing = await db.execute(select(Category).where(func.lower(Category.name) == data.name.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Category already exists")
    cat = Category(**data.model_dump())
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


@router.delete("/categories/{cat_id}", status_code=204)
async def delete_category(cat_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(Category).where(Category.id == cat_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "Category not found")
    await db.delete(cat)
    await db.commit()


# ── Units of Measure ─────────────────────────────────────────────────────────

@router.get("/uom", response_model=list[UoMOut])
async def list_uom(db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(UnitOfMeasure).order_by(UnitOfMeasure.name))
    return result.scalars().all()


@router.post("/uom", response_model=UoMOut, status_code=201)
async def create_uom(data: UoMCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    existing = await db.execute(select(UnitOfMeasure).where(func.lower(UnitOfMeasure.name) == data.name.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Unit of measure already exists")
    uom = UnitOfMeasure(**data.model_dump())
    db.add(uom)
    await db.commit()
    await db.refresh(uom)
    return uom


@router.delete("/uom/{uom_id}", status_code=204)
async def delete_uom(uom_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(select(UnitOfMeasure).where(UnitOfMeasure.id == uom_id))
    uom = result.scalar_one_or_none()
    if not uom:
        raise HTTPException(404, "UoM not found")
    await db.delete(uom)
    await db.commit()


# ── Products ─────────────────────────────────────────────────────────────────

@router.get("/products", response_model=list[ProductOut])
async def list_products(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    q = select(Product).options(selectinload(Product.category), selectinload(Product.unit_of_measure))
    if category_id:
        q = q.where(Product.category_id == category_id)
    if search:
        q = q.where(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
    if is_active is not None:
        q = q.where(Product.is_active == is_active)
    result = await db.execute(q.order_by(Product.name))
    return result.scalars().all()


@router.post("/products", response_model=ProductOut, status_code=201)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    existing = await db.execute(select(Product).where(Product.sku == data.sku))
    if existing.scalar_one_or_none():
        raise HTTPException(409, f"SKU '{data.sku}' already exists")
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.category), selectinload(Product.unit_of_measure))
        .where(Product.id == product.id)
    )
    return result.scalar_one()


@router.get("/products/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)):
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.category), selectinload(Product.unit_of_measure))
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Product not found")
    return product


@router.patch("/products/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int, data: ProductUpdate,
    db: AsyncSession = Depends(get_db), _: User = Depends(get_current_user)
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Product not found")
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(product, field, val)
    await db.commit()
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.category), selectinload(Product.unit_of_measure))
        .where(Product.id == product_id)
    )
    return result.scalar_one()
