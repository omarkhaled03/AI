"""SQLAlchemy ORM models."""
from __future__ import annotations

import datetime
import uuid

from sqlalchemy import Date, DateTime, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Passenger(Base):
    __tablename__ = "passengers"
    __table_args__ = (
        UniqueConstraint(
            "government_id_type",
            "government_id_number",
            name="uq_passenger_government_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(String(200))
    date_of_birth: Mapped[datetime.date] = mapped_column(Date)
    email: Mapped[str] = mapped_column(String)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    government_id_type: Mapped[str] = mapped_column(String)
    government_id_number: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("clock_timestamp()")
    )


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    destination: Mapped[str] = mapped_column(String(200))
    departure_date: Mapped[datetime.date] = mapped_column(Date)
    return_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("clock_timestamp()")
    )
