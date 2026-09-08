"""Database access for the Trip aggregate."""
from __future__ import annotations

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from app.db.models import Trip


class TripRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, trip: Trip) -> Trip:
        self._session.add(trip)
        return trip

    def search(
        self,
        *,
        destination: str | None = None,
        limit: int,
        offset: int,
    ) -> tuple[list[Trip], int]:
        filters: list[ColumnElement[bool]] = []
        if destination is not None:
            filters.append(Trip.destination.ilike(f"%{destination}%"))

        count_stmt = select(func.count()).select_from(Trip).where(*filters)
        total = self._session.execute(count_stmt).scalar_one()

        stmt = (
            select(Trip)
            .where(*filters)
            .order_by(Trip.created_at.desc(), Trip.id.desc())
            .limit(limit)
            .offset(offset)
        )
        items = list(self._session.execute(stmt).scalars().all())
        return items, total
