"""Database access for the Passenger aggregate."""
from __future__ import annotations

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from app.db.models import Passenger


class PassengerRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, passenger: Passenger) -> Passenger:
        self._session.add(passenger)
        return passenger

    def get_by_government_id(
        self, id_type: str, id_number: str
    ) -> Passenger | None:
        stmt = select(Passenger).where(
            Passenger.government_id_type == id_type,
            Passenger.government_id_number == id_number,
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def search(
        self,
        *,
        name: str | None = None,
        government_id_number: str | None = None,
        government_id_type: str | None = None,
        limit: int,
        offset: int,
    ) -> tuple[list[Passenger], int]:
        filters: list[ColumnElement[bool]] = []
        if name is not None:
            filters.append(Passenger.full_name.ilike(f"%{name}%"))
        if government_id_number is not None:
            filters.append(Passenger.government_id_number == government_id_number)
        if government_id_type is not None:
            filters.append(Passenger.government_id_type == government_id_type)

        count_stmt = select(func.count()).select_from(Passenger).where(*filters)
        total = self._session.execute(count_stmt).scalar_one()

        stmt = (
            select(Passenger)
            .where(*filters)
            .order_by(Passenger.created_at.desc(), Passenger.id.desc())
            .limit(limit)
            .offset(offset)
        )
        items = list(self._session.execute(stmt).scalars().all())
        return items, total
