import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import create_app


@pytest.fixture(scope="session")
def setup_test_database():
    # Use the same Postgres DB as configured; ensure tables exist.
    Base.metadata.create_all(bind=engine)
    yield
    # Do not drop tables after session to preserve seed data.


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
