"""FastAPI router for the Trip resource."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.models.trip import (
    TripCreate,
    TripListQuery,
    TripListResponse,
    TripRead,
)
from app.services.trip_service import create_trip, list_trips

router = APIRouter(prefix="/trips")


@router.post("", response_model=TripRead, status_code=201)
def create_trip_endpoint(
    data: TripCreate, session: Session = Depends(get_session)
) -> TripRead:
    trip = create_trip(session, data)
    session.commit()
    return TripRead.model_validate(trip)


@router.get("", response_model=TripListResponse)
def list_trips_endpoint(
    query: TripListQuery = Depends(), session: Session = Depends(get_session)
) -> TripListResponse:
    result = list_trips(session, query)
    return TripListResponse(
        items=[TripRead.model_validate(item) for item in result.items],
        total=result.total,
        limit=query.limit,
        offset=query.offset,
    )
