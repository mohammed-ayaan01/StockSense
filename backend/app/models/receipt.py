import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ReceiptStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reference: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    supplier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    status: Mapped[ReceiptStatus] = mapped_column(Enum(ReceiptStatus), default=ReceiptStatus.DRAFT, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    location: Mapped["Location"] = relationship()  # type: ignore[name-defined]
    lines: Mapped[list["ReceiptLine"]] = relationship(back_populates="receipt", cascade="all, delete-orphan")
    creator: Mapped["User"] = relationship()  # type: ignore[name-defined]


class ReceiptLine(Base):
    __tablename__ = "receipt_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    receipt_id: Mapped[int] = mapped_column(Integer, ForeignKey("receipts.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    expected_qty: Mapped[float] = mapped_column(Float, nullable=False)
    received_qty: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    receipt: Mapped["Receipt"] = relationship(back_populates="lines")
    product: Mapped["Product"] = relationship()  # type: ignore[name-defined]
