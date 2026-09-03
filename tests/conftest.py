"""Shared pytest fixtures for the test suite.

Uses a real PostgreSQL schema (not mocks) for anything touching
repositories/DB constraints, per docs/conventions.md.

The test DB connection string is read from TEST_DATABASE_URL. Developers
running these tests locally are expected to point this at a disposable
PostgreSQL database/schema; nothing here mocks the database.
"""
from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# These imports are expected to fail until the developer implements app/.
from app.db.models import Base
from app.db.session import get_session
from app.main import app

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg:///fedac_test"
)


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(engine) -> Session:
    connection = engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    session = session_factory()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    from fastapi.testclient import TestClient

    def _override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
