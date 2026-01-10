"""Tests for MotherDuck background sync functionality."""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app, sync_motherduck_background


@pytest.mark.asyncio
async def test_sync_motherduck_background_no_credentials():
    """Test that sync gracefully skips when credentials are missing."""
    with patch.dict(os.environ, {}, clear=True):
        # Should not raise an exception
        await sync_motherduck_background()


@pytest.mark.asyncio
async def test_sync_motherduck_background_with_credentials():
    """Test that sync runs when credentials are provided."""
    with patch.dict(
        os.environ,
        {
            "MOTHERDUCK_DB": "test_db",
            "MOTHERDUCK_TOKEN": "test_token",
            "MOTHERDUCK_SCHEMA": "test_schema",
        },
    ):
        with patch("app.database.sync_motherduck.sync_from_motherduck") as mock_sync:
            with patch("app.main.settings") as mock_settings:
                mock_settings.duckdb_path = "/tmp/test.duckdb"

                await sync_motherduck_background()

                # Verify sync was called with correct parameters
                mock_sync.assert_called_once_with(
                    motherduck_db="test_db",
                    motherduck_token="test_token",
                    local_db_path="/tmp/test.duckdb",
                    source_schema="test_schema",
                )


@pytest.mark.asyncio
async def test_sync_motherduck_background_handles_errors():
    """Test that sync handles errors gracefully."""
    with patch.dict(
        os.environ,
        {"MOTHERDUCK_DB": "test_db", "MOTHERDUCK_TOKEN": "test_token"},
    ):
        with patch("app.database.sync_motherduck.sync_from_motherduck") as mock_sync:
            with patch("app.main.settings") as mock_settings:
                mock_settings.duckdb_path = "/tmp/test.duckdb"
                mock_sync.side_effect = Exception("Sync failed")

                # Should not raise, just log the error
                await sync_motherduck_background()


def test_lifespan_starts_background_sync():
    """Test that the lifespan context starts the background sync task."""
    with TestClient(app) as client:
        # Just starting the client should trigger the lifespan
        # The background sync should start (though it may not complete)
        response = client.get("/")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_sync_uses_default_schema():
    """Test that sync uses default schema when not specified."""
    with patch.dict(
        os.environ,
        {"MOTHERDUCK_DB": "test_db", "MOTHERDUCK_TOKEN": "test_token"},
        clear=True,
    ):
        with patch("app.database.sync_motherduck.sync_from_motherduck") as mock_sync:
            with patch("app.main.settings") as mock_settings:
                mock_settings.duckdb_path = "/tmp/test.duckdb"

                await sync_motherduck_background()

                # Verify default schema "dmt" is used
                call_args = mock_sync.call_args
                assert call_args[1]["source_schema"] == "dmt"
