import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class MovementType(str, enum.Enum):
    RECEIPT = "RECEIPT"
    DELIVERY = "DELIVERY"
    TRANSFER_OUT = "TRANSFER_OUT"
    TRANSFER_IN = "TRANSFER_IN"
    ADJUSTMENT = "ADJUSTMENT"


class StockMovement(Base):
    """Immutable audit log — never updated or deleted once written."""
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    movement_type: Mapped[MovementType] = mapped_column(Enum(MovementType), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)          # positive = in, negative = out
    reference: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g. "REC/001", "DEL/001"
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True)        # FK to source doc id
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    product: Mapped["Product"] = relationship()  # type: ignore[name-defined]
    location: Mapped["Location"] = relationship()  # type: ignore[name-defined]
    creator: Mapped["User"] = relationship()  # type: ignore[name-defined]
