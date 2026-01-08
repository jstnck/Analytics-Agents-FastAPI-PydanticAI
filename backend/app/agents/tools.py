"""Tools for PydanticAI agents to interact with the database."""

from typing import Any

from pydantic import BaseModel, Field

from app.database.duckdb_client import DuckDBClient


class QueryResult(BaseModel):
    """Result from executing a SQL query."""

    sql_query: str = Field(..., description="The SQL query that was executed")
    rows_returned: int = Field(..., description="Number of rows returned")
    results: list[dict[str, Any]] = Field(..., description="Query results as list of dicts")
    columns: list[str] = Field(..., description="Column names in the result set")


class QueryError(BaseModel):
    """Error from executing a SQL query."""

    sql_query: str = Field(..., description="The SQL query that failed")
    error_message: str = Field(..., description="Error message from the database")
    error_type: str = Field(..., description="Type of error (syntax, execution, validation)")


async def get_database_schema(db_client: DuckDBClient) -> dict[str, list[dict[str, str]]]:
    """
    Get the complete database schema information.

    Args:
        db_client: Database client instance

    Returns a dictionary mapping table names to their column definitions.
    Each column definition includes 'name' and 'type'.

    Example:
        {
            "dmt.dmt_team_per_game_stats": [
                {"name": "team_name", "type": "VARCHAR"},
                {"name": "games_played", "type": "BIGINT"},
                ...
            ]
        }
    """
    return await db_client.get_schema_info()


async def execute_sql_query(sql: str, db_client: DuckDBClient) -> QueryResult | QueryError:
    """
    Execute a SQL query against the database with validation.

    Only SELECT queries are allowed for safety. The query is executed
    and results are returned as a structured response.

    Args:
        sql: SQL query string to execute (must be SELECT only)
        db_client: Database client instance

    Returns:
        QueryResult on success, QueryError on failure

    Validation rules:
        - Query must start with SELECT (case-insensitive)
        - Query must not contain destructive operations
        - Query must be valid DuckDB SQL syntax
    """
    # Normalize whitespace and check if it's a SELECT query
    normalized_sql = sql.strip().upper()

    # Validation: Only SELECT queries allowed
    if not normalized_sql.startswith("SELECT"):
        return QueryError(
            sql_query=sql,
            error_message="Only SELECT queries are allowed. Query must start with SELECT.",
            error_type="validation",
        )

    # Check for destructive operations (defense in depth)
    destructive_keywords = ["DROP", "DELETE", "TRUNCATE", "INSERT", "UPDATE", "ALTER", "CREATE"]
    if any(keyword in normalized_sql for keyword in destructive_keywords):
        return QueryError(
            sql_query=sql,
            error_message=f"Query contains disallowed operations: {destructive_keywords}",
            error_type="validation",
        )

    # Execute the query
    try:
        results = await db_client.execute(sql)
        columns = list(results[0].keys()) if results else []

        return QueryResult(
            sql_query=sql,
            rows_returned=len(results),
            results=results,
            columns=columns,
        )

    except Exception as e:
        # Return error details for self-correction
        return QueryError(
            sql_query=sql,
            error_message=str(e),
            error_type="execution",
        )
