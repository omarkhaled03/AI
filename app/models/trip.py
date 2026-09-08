"""Pydantic request/response schemas for the Trip resource."""
from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TripCreate(BaseModel):
    destination: str = Field(min_length=1, max_length=200)
    departure_date: datetime.date
    return_date: datetime.date | None = None

    @field_validator("destination", mode="before")
    @classmethod
    def _strip_destination(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @model_validator(mode="after")
    def _return_date_not_before_departure_date(self) -> TripCreate:
        if self.return_date is not None and self.return_date < self.departure_date:
            raise ValueError("return_date must not be before departure_date")
        return self


class TripRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    destination: str
    departure_date: datetime.date
    return_date: datetime.date | None
    created_at: datetime.datetime


class TripListQuery(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    destination: str | None = None


class TripListResponse(BaseModel):
    items: list[TripRead]
    total: int
    limit: int
    offset: int
