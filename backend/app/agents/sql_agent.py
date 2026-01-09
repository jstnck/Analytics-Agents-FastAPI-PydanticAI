"""SQL Agent for generating and executing SQL queries against NBA data."""

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from app.agents.tools import QueryError, QueryResult, execute_sql_query, get_database_schema
from app.config import settings
from app.database.duckdb_client import DuckDBClient
from app.utils.prompts import SQL_AGENT_SYSTEM_PROMPT


class SQLAgentResponse(BaseModel):
    """Structured response from SQL agent."""

    message: str = Field(..., description="Concise answer to the user's question")
    sql_query: str | None = Field(
        None, description="SQL query used to generate the answer (if applicable)"
    )
    data_summary: dict[str, Any] | None = Field(
        None, description="Optional summary of key data points"
    )
    results: list[dict[str, Any]] | None = Field(
        None, description="Query results data (for passing to visualization agent)"
    )


@dataclass
class SQLAgentDeps:
    """Dependencies for the SQL agent.

    Following PydanticAI best practices, dependencies contain runtime context
    like database connections, not the user's prompt (which is passed separately).
    """

    db_client: DuckDBClient
    user_id: str | None = None  # For future user tracking/analytics


# Create SQL agent with configured model and structured response
sql_agent = Agent(
    settings.default_llm_model,
    output_type=SQLAgentResponse,
    deps_type=SQLAgentDeps,
    system_prompt=SQL_AGENT_SYSTEM_PROMPT,
    retries=2,  # Allow retries for self-correction
)


@sql_agent.tool
async def get_schema(ctx: RunContext[SQLAgentDeps]) -> dict[str, list[dict[str, str]]]:
    """
    Get the complete database schema.

    Returns table and column information for all available tables.
    Use this when you need to understand table structure.
    """
    return await get_database_schema(ctx.deps.db_client)


@sql_agent.tool
async def execute_query(ctx: RunContext[SQLAgentDeps], sql: str) -> dict[str, Any]:
    """
    Execute a SQL query against the database.

    Only SELECT queries are allowed. Returns results or error details.
    If you receive an error, analyze it and generate a corrected query.

    Args:
        sql: SQL SELECT query to execute

    Returns:
        Dictionary with query results or error information
    """
    result = await execute_sql_query(sql, ctx.deps.db_client)

    if isinstance(result, QueryResult):
        return {
            "status": "success",
            "sql_query": result.sql_query,
            "rows_returned": result.rows_returned,
            "results": result.results,
            "columns": result.columns,
        }
    elif isinstance(result, QueryError):
        return {
            "status": "error",
            "sql_query": result.sql_query,
            "error_message": result.error_message,
            "error_type": result.error_type,
        }
    else:
        return {"status": "error", "error_message": "Unknown error occurred"}


async def run_sql_agent(user_question: str, db_client: DuckDBClient) -> SQLAgentResponse:
    """
    Run the SQL agent to answer a user's question.

    Args:
        user_question: The user's question about NBA data
        db_client: Database client instance for executing queries

    Returns:
        SQLAgentResponse with message, sql_query, and optional data_summary
    """
    deps = SQLAgentDeps(db_client=db_client)
    result = await sql_agent.run(user_question, deps=deps)
    return result.output
