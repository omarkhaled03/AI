"""Pydantic request/response schemas for the Passenger resource."""
from __future__ import annotations

import datetime
import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class GovernmentIdType(str, Enum):
    passport = "passport"
    national_id = "national_id"


class PassengerCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    date_of_birth: datetime.date
    email: EmailStr
    phone: str | None = None
    government_id_type: GovernmentIdType
    government_id_number: str = Field(min_length=1, max_length=50)

    @field_validator("full_name", mode="before")
    @classmethod
    def _strip_full_name(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("email")
    @classmethod
    def _lowercase_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("government_id_number", mode="before")
    @classmethod
    def _normalize_government_id_number(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("date_of_birth")
    @classmethod
    def _date_of_birth_in_past(cls, value: datetime.date) -> datetime.date:
        if value >= datetime.datetime.now(tz=datetime.timezone.utc).date():
            raise ValueError("date_of_birth must be strictly before today")
        return value


class PassengerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    date_of_birth: datetime.date
    email: str
    phone: str | None
    government_id_type: GovernmentIdType
    government_id_number: str
    created_at: datetime.datetime


class PassengerListQuery(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    name: str | None = None
    government_id_number: str | None = None
    government_id_type: GovernmentIdType | None = None

    @field_validator("government_id_number", mode="before")
    @classmethod
    def _normalize_government_id_number(cls, value: str | None) -> str | None:
        if isinstance(value, str):
            return value.strip().upper()
        return value


class PassengerListResponse(BaseModel):
    items: list[PassengerRead]
    total: int
    limit: int
    offset: int
