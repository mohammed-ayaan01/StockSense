from datetime import datetime, timezone
from sqlalchemy import Integer, Float, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class InventoryStock(Base):
    __tablename__ = "inventory_stock"
    __table_args__ = (
        UniqueConstraint("product_id", "location_id", name="uq_stock_product_location"),
        CheckConstraint("quantity >= 0", name="ck_stock_quantity_nonneg"),
        CheckConstraint("reserved >= 0", name="ck_stock_reserved_nonneg"),
        CheckConstraint("reserved <= quantity", name="ck_stock_reserved_lte_quantity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reserved: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    product: Mapped["Product"] = relationship(back_populates="inventory_stocks")  # type: ignore[name-defined]
    location: Mapped["Location"] = relationship(back_populates="inventory_stocks")  # type: ignore[name-defined]
