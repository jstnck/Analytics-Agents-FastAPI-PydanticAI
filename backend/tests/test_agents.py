"""Tests for agent tools and SQL agent."""

import pytest

from app.agents.tools import QueryError, QueryResult, execute_sql_query, get_database_schema
from app.database.duckdb_client import DuckDBClient


@pytest.mark.asyncio
class TestDatabaseTools:
    """Test database interaction tools."""

    async def test_get_database_schema_returns_schema_info(self, db_client: DuckDBClient) -> None:
        """Test that get_database_schema returns valid schema information."""
        schema = await get_database_schema(db_client)

        assert isinstance(schema, dict)
        assert len(schema) > 0

        # Check that we have the expected NBA tables
        table_names = list(schema.keys())
        assert any("dmt_team_per_game_stats" in name for name in table_names)
        assert any("dmt_schedule" in name for name in table_names)

        # Check structure of schema info
        for _table_name, columns in schema.items():
            assert isinstance(columns, list)
            if columns:  # If table has columns
                assert "name" in columns[0]
                assert "type" in columns[0]

    async def test_execute_sql_query_success(self, db_client: DuckDBClient) -> None:
        """Test successful SQL query execution."""
        sql = "SELECT 1 as test_column"
        result = await execute_sql_query(sql, db_client)

        assert isinstance(result, QueryResult)
        assert result.sql_query == sql
        assert result.rows_returned == 1
        assert len(result.results) == 1
        assert result.results[0]["test_column"] == 1
        assert "test_column" in result.columns

    async def test_execute_sql_query_with_table_data(self, db_client: DuckDBClient) -> None:
        """Test query against actual NBA data."""
        sql = "SELECT team_name FROM dmt.dmt_team_per_game_stats LIMIT 5"
        result = await execute_sql_query(sql, db_client)

        assert isinstance(result, QueryResult)
        assert result.rows_returned <= 5
        assert "team_name" in result.columns
        if result.results:
            assert "team_name" in result.results[0]

    async def test_execute_sql_query_rejects_non_select(self, db_client: DuckDBClient) -> None:
        """Test that non-SELECT queries are rejected."""
        sql = "DELETE FROM dmt.dmt_schedule"
        result = await execute_sql_query(sql, db_client)

        assert isinstance(result, QueryError)
        assert result.error_type == "validation"
        assert "Only SELECT queries" in result.error_message

    async def test_execute_sql_query_rejects_drop(self, db_client: DuckDBClient) -> None:
        """Test that DROP statements are rejected."""
        sql = "DROP TABLE dmt.dmt_schedule"
        result = await execute_sql_query(sql, db_client)

        assert isinstance(result, QueryError)
        assert result.error_type == "validation"
        assert "SELECT" in result.error_message

    async def test_execute_sql_query_rejects_insert(self, db_client: DuckDBClient) -> None:
        """Test that INSERT statements are rejected."""
        sql = "INSERT INTO dmt.dmt_schedule VALUES (1, 2, 3)"
        result = await execute_sql_query(sql, db_client)

        assert isinstance(result, QueryError)
        assert result.error_type == "validation"

    async def test_execute_sql_query_handles_syntax_error(self, db_client: DuckDBClient) -> None:
        """Test handling of SQL syntax errors."""
        sql = "SELECT * FROM nonexistent_table_xyz123"
        result = await execute_sql_query(sql, db_client)

        assert isinstance(result, QueryError)
        assert result.error_type == "execution"
        assert len(result.error_message) > 0

    async def test_execute_sql_query_handles_empty_result(self, db_client: DuckDBClient) -> None:
        """Test query that returns no rows."""
        sql = "SELECT * FROM dmt.dmt_schedule WHERE 1=0"
        result = await execute_sql_query(sql, db_client)

        assert isinstance(result, QueryResult)
        assert result.rows_returned == 0
        assert result.results == []


@pytest.mark.asyncio
class TestVizAgentTools:
    """Test visualization agent tools."""

    async def test_create_chart_basic(self) -> None:
        """Test basic chart creation from viz_agent tools."""
        from app.agents.viz_agent import create_chart, VizAgentDeps
        from app.database.duckdb_client import DuckDBClient
        from pydantic_ai import RunContext

        db_client = DuckDBClient()
        deps = VizAgentDeps(db_client=db_client)

        # Create a mock RunContext
        class MockCtx:
            def __init__(self, deps):
                self.deps = deps

        ctx = MockCtx(deps)

        # Sample data
        data = [
            {"team": "Lakers", "points": 110},
            {"team": "Celtics", "points": 105},
            {"team": "Warriors", "points": 115},
        ]

        result = await create_chart(
            ctx,
            chart_type="bar",
            data=data,
            x_column="team",
            y_column="points",
            title="Team Points"
        )

        assert result["status"] == "success"
        assert result["chart_type"] == "bar"
        assert result["data_points"] == 3
        assert "chart_spec" in result
        assert "data" in result["chart_spec"]
        assert "layout" in result["chart_spec"]

    async def test_create_multi_series_chart(self) -> None:
        """Test multi-series chart creation."""
        from app.agents.viz_agent import create_multi_series_chart, VizAgentDeps
        from app.database.duckdb_client import DuckDBClient

        db_client = DuckDBClient()
        deps = VizAgentDeps(db_client=db_client)

        class MockCtx:
            def __init__(self, deps):
                self.deps = deps

        ctx = MockCtx(deps)

        data = [
            {"team": "Lakers", "points": 110, "assists": 25},
            {"team": "Celtics", "points": 105, "assists": 22},
        ]

        result = await create_multi_series_chart(
            ctx,
            chart_type="bar",
            data=data,
            x_column="team",
            y_columns=["points", "assists"],
            title="Team Stats"
        )

        assert result["status"] == "success"
        assert result["chart_type"] == "bar"
        assert result["series_count"] == 2
        assert len(result["chart_spec"]["data"]) == 2

    async def test_viz_agent_response_structure(self) -> None:
        """Test VizAgentResponse model structure."""
        from app.agents.viz_agent import VizAgentResponse

        response = VizAgentResponse(
            message="Chart created",
            chart_spec={"data": [], "layout": {}},
            chart_type="bar"
        )

        assert response.message == "Chart created"
        assert response.chart_type == "bar"
        assert response.chart_spec is not None


# Note: Integration tests for agents require API keys and will be added
# when we test the full orchestrator -> SQL agent flow


class TestOrchestratorStructure:
    """Tests for orchestrator structure (non-integration)."""

    def test_orchestrator_response_model_structure(self) -> None:
        """Test that OrchestratorResponse has the expected structure."""
        from app.agents.orchestrator import OrchestratorResponse

        response = OrchestratorResponse(
            message="Test response", metadata={"sql_query": "SELECT 1", "agent": "sql"}
        )

        assert response.message == "Test response"
        assert response.metadata["sql_query"] == "SELECT 1"
        assert response.metadata["agent"] == "sql"

    def test_orchestrator_response_empty_metadata(self) -> None:
        """Test that OrchestratorResponse works with empty metadata."""
        from app.agents.orchestrator import OrchestratorResponse

        response = OrchestratorResponse(message="Simple response")

        assert response.message == "Simple response"
        assert response.metadata == {}

    def test_orchestrator_accepts_conversation_history(self) -> None:
        """Test that run_orchestrator accepts conversation history parameter."""
        from app.agents.orchestrator import run_orchestrator
        from app.database.duckdb_client import DuckDBClient

        # This test verifies the function signature accepts history
        # Full integration test would require API keys
        db_client = DuckDBClient()
        conversation_history = [
            {"role": "user", "content": "What teams are in the database?"},
            {"role": "assistant", "content": "There are 30 NBA teams in the database."},
        ]

        # Verify the function accepts the parameters (won't execute without API keys)
        import inspect
        sig = inspect.signature(run_orchestrator)
        params = sig.parameters

        assert "user_question" in params
        assert "db_client" in params
        assert "conversation_history" in params
        assert params["conversation_history"].default is None
