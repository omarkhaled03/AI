"""FastAPI router for the Passenger resource."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.passenger import (
    PassengerCreate,
    PassengerListQuery,
    PassengerListResponse,
    PassengerRead,
)
from app.services.passenger_service import (
    PassengerAlreadyExistsError,
    create_passenger,
    list_passengers,
)

router = APIRouter(prefix="/passengers")


@router.post("", response_model=PassengerRead, status_code=201)
def create_passenger_endpoint(
    data: PassengerCreate, session: Session = Depends(get_session)
) -> PassengerRead | JSONResponse:
    try:
        passenger = create_passenger(session, data)
    except PassengerAlreadyExistsError as exc:
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Passenger with this government id already exists",
                "existing_passenger_id": str(exc.existing_passenger_id),
            },
        )
    session.commit()
    return PassengerRead.model_validate(passenger)


@router.get("", response_model=PassengerListResponse)
def list_passengers_endpoint(
    query: PassengerListQuery = Depends(), session: Session = Depends(get_session)
) -> PassengerListResponse:
    result = list_passengers(session, query)
    return PassengerListResponse(
        items=[PassengerRead.model_validate(item) for item in result.items],
        total=result.total,
        limit=query.limit,
        offset=query.offset,
    )
