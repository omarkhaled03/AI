"""Business logic for the Passenger resource."""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Passenger
from app.models.passenger import PassengerCreate, PassengerListQuery
from app.repositories.passenger_repository import PassengerRepository


class PassengerAlreadyExistsError(Exception):
    def __init__(self, existing_passenger_id: uuid.UUID) -> None:
        self.existing_passenger_id = existing_passenger_id
        super().__init__(
            f"Passenger with this government id already exists: {existing_passenger_id}"
        )


@dataclass
class PassengerListResult:
    items: list[Passenger]
    total: int


def create_passenger(session: Session, data: PassengerCreate) -> Passenger:
    repo = PassengerRepository(session)
    passenger = Passenger(
        full_name=data.full_name,
        date_of_birth=data.date_of_birth,
        email=data.email,
        phone=data.phone,
        government_id_type=data.government_id_type.value,
        government_id_number=data.government_id_number,
    )
    try:
        with session.begin_nested():
            repo.add(passenger)
            session.flush()
    except IntegrityError as exc:
        existing = repo.get_by_government_id(
            data.government_id_type.value, data.government_id_number
        )
        if existing is None:
            raise
        raise PassengerAlreadyExistsError(existing_passenger_id=existing.id) from exc

    return passenger


def list_passengers(
    session: Session, query: PassengerListQuery
) -> PassengerListResult:
    repo = PassengerRepository(session)
    items, total = repo.search(
        name=query.name,
        government_id_number=query.government_id_number,
        government_id_type=(
            query.government_id_type.value if query.government_id_type else None
        ),
        limit=query.limit,
        offset=query.offset,
    )
    return PassengerListResult(items=items, total=total)
