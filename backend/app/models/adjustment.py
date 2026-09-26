import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class AdjustmentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class StockAdjustment(Base):
    __tablename__ = "stock_adjustments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reference: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    counted_qty: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_qty: Mapped[float] = mapped_column(Float, nullable=False)  # snapshot at time of adjustment
    delta: Mapped[float] = mapped_column(Float, nullable=False)         # counted - recorded
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[AdjustmentStatus] = mapped_column(Enum(AdjustmentStatus), default=AdjustmentStatus.DRAFT, nullable=False)
    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    product: Mapped["Product"] = relationship()  # type: ignore[name-defined]
    location: Mapped["Location"] = relationship()  # type: ignore[name-defined]
    creator: Mapped["User"] = relationship()  # type: ignore[name-defined]
