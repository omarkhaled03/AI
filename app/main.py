"""FastAPI application entrypoint."""
from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import passengers, trips

app = FastAPI(title="abcd")

_allowed_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(passengers.router)
app.include_router(trips.router)
