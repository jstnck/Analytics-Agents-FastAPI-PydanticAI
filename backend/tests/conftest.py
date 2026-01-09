import pytest
from dotenv import load_dotenv

# Load environment variables BEFORE any app imports
load_dotenv()

from fastapi.testclient import TestClient  # noqa: E402

from app.database.duckdb_client import DuckDBClient  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def db_client():
    """DuckDB client fixture for unit tests."""
    return DuckDBClient()
