import asyncio
from pathlib import Path
from typing import Any

import duckdb

from app.config import settings


class DuckDBClient:
    """Local DuckDB client for querying analytics data.

    Following PydanticAI best practices, all I/O operations are async
    to prevent blocking the FastAPI event loop.
    """

    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path or settings.duckdb_path
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Ensure the database file and parent directories exist."""
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

    def _execute_sync(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Synchronous execute helper for running in thread pool."""
        with duckdb.connect(self.db_path, read_only=False) as conn:
            result = conn.execute(query, params or {})
            columns = [desc[0] for desc in result.description] if result.description else []
            rows = result.fetchall()
            return [dict(zip(columns, row, strict=True)) for row in rows]

    async def execute(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a query and return results as a list of dictionaries.

        Runs in a thread pool to avoid blocking the event loop.
        """
        return await asyncio.to_thread(self._execute_sync, query, params)

    def _get_schema_info_sync(self) -> dict[str, list[dict[str, str]]]:
        """Synchronous get_schema_info helper for running in thread pool."""
        with duckdb.connect(self.db_path, read_only=True) as conn:
            # Get all tables
            tables = conn.execute(
                "SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema != 'information_schema'"
            ).fetchall()

            schema_info = {}
            for schema, table in tables:
                # Get columns for each table
                columns = conn.execute(
                    """
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = ? AND table_name = ?
                    ORDER BY ordinal_position
                    """,
                    [schema, table],
                ).fetchall()

                full_table_name = f"{schema}.{table}"
                schema_info[full_table_name] = [{"name": col[0], "type": col[1]} for col in columns]

            return schema_info

    async def get_schema_info(self) -> dict[str, list[dict[str, str]]]:
        """Get information about available tables and their schemas.

        Runs in a thread pool to avoid blocking the event loop.
        """
        return await asyncio.to_thread(self._get_schema_info_sync)


# NOTE: Global singleton removed in favor of dependency injection.
# Create instances via FastAPI Depends() or pass explicitly to agents.
