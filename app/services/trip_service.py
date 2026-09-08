"""Business logic for the Trip resource."""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models import Trip
from app.models.trip import TripCreate, TripListQuery
from app.repositories.trip_repository import TripRepository


@dataclass
class TripListResult:
    items: list[Trip]
    total: int


def create_trip(session: Session, data: TripCreate) -> Trip:
    repo = TripRepository(session)
    trip = Trip(
        destination=data.destination,
        departure_date=data.departure_date,
        return_date=data.return_date,
    )
    repo.add(trip)
    session.flush()
    return trip


def list_trips(session: Session, query: TripListQuery) -> TripListResult:
    repo = TripRepository(session)
    items, total = repo.search(
        destination=query.destination,
        limit=query.limit,
        offset=query.offset,
    )
    return TripListResult(items=items, total=total)
