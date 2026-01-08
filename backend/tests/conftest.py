import pytest
from dotenv import load_dotenv

# Load environment variables BEFORE any app imports
load_dotenv()

from fastapi.testclient import TestClient

from app.database.duckdb_client import DuckDBClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def db_client():
    """DuckDB client fixture for unit tests."""
    return DuckDBClient()
