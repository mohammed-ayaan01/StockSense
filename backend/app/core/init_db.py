import logging
from sqlalchemy import select
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import hash_password
import app.models  # noqa: F401
from app.models.user import User, UserRole
from app.models.product import Category, UnitOfMeasure
from app.models.warehouse import Warehouse
from app.models.location import Location

logger = logging.getLogger("stocksense.init_db")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check admin user
        res = await session.execute(select(User).where(User.email == "admin@stocksense.com"))
        admin = res.scalar_one_or_none()
        if not admin:
            admin = User(
                email="admin@stocksense.com",
                full_name="Admin User",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(admin)

        # Check categories
        res = await session.execute(select(Category))
        categories = res.scalars().all()
        if not categories:
            sample_categories = [
                Category(name="Electronics", description="Electronic components and devices"),
                Category(name="Furniture", description="Office and warehouse furniture"),
                Category(name="Raw Materials", description="Basic materials for production"),
                Category(name="Consumables", description="Day-to-day consumable items"),
            ]
            session.add_all(sample_categories)

        # Check units of measure
        res = await session.execute(select(UnitOfMeasure))
        uoms = res.scalars().all()
        if not uoms:
            sample_uoms = [
                UnitOfMeasure(name="Unit", abbreviation="pcs"),
                UnitOfMeasure(name="Kilogram", abbreviation="kg"),
                UnitOfMeasure(name="Liter", abbreviation="L"),
                UnitOfMeasure(name="Meter", abbreviation="m"),
                UnitOfMeasure(name="Box", abbreviation="box"),
            ]
            session.add_all(sample_uoms)

        # Check warehouses
        res = await session.execute(select(Warehouse))
        warehouses = res.scalars().all()
        if not warehouses:
            wh1 = Warehouse(name="Main Warehouse", code="WH01", address="123 Industrial Area, Hyderabad", is_active=True)
            wh2 = Warehouse(name="Secondary Warehouse", code="WH02", address="456 Storage Zone, Hyderabad", is_active=True)
            session.add_all([wh1, wh2])
            await session.flush()

            loc1 = Location(warehouse_id=wh1.id, name="Zone A", code="A01", description="Primary storage zone", is_active=True)
            loc2 = Location(warehouse_id=wh1.id, name="Zone B", code="B01", description="Secondary storage zone", is_active=True)
            loc3 = Location(warehouse_id=wh2.id, name="Zone A", code="A01", description="Primary storage zone", is_active=True)
            session.add_all([loc1, loc2, loc3])

        await session.commit()
