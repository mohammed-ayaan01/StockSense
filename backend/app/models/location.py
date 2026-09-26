from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Location(Base):
    __tablename__ = "locations"
    __table_args__ = (UniqueConstraint("warehouse_id", "code", name="uq_location_warehouse_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    warehouse: Mapped["Warehouse"] = relationship(back_populates="locations")  # type: ignore[name-defined]
    inventory_stocks: Mapped[list["InventoryStock"]] = relationship(back_populates="location")  # type: ignore[name-defined]
