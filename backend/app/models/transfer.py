import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class TransferStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    reference: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    src_location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    dst_location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    status: Mapped[TransferStatus] = mapped_column(Enum(TransferStatus), default=TransferStatus.DRAFT, nullable=False)
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

    src_location: Mapped["Location"] = relationship(foreign_keys=[src_location_id])  # type: ignore[name-defined]
    dst_location: Mapped["Location"] = relationship(foreign_keys=[dst_location_id])  # type: ignore[name-defined]
    lines: Mapped[list["TransferLine"]] = relationship(back_populates="transfer", cascade="all, delete-orphan")
    creator: Mapped["User"] = relationship()  # type: ignore[name-defined]


class TransferLine(Base):
    __tablename__ = "transfer_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transfer_id: Mapped[int] = mapped_column(Integer, ForeignKey("transfers.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)

    transfer: Mapped["Transfer"] = relationship(back_populates="lines")
    product: Mapped["Product"] = relationship()  # type: ignore[name-defined]
