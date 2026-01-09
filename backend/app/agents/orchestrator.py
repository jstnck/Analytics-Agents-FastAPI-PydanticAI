"""Orchestrator agent that coordinates specialist agents."""

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from app.agents.sql_agent import run_sql_agent
from app.agents.viz_agent import run_viz_agent
from app.config import settings
from app.database.duckdb_client import DuckDBClient
from app.utils.prompts import ORCHESTRATOR_SYSTEM_PROMPT


class OrchestratorResponse(BaseModel):
    """Structured response from orchestrator agent."""

    message: str = Field(..., description="Response message to the user")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata from specialist agents (SQL queries, etc.)",
    )


@dataclass
class OrchestratorDeps:
    """Dependencies for the orchestrator agent.

    Following PydanticAI best practices, dependencies contain runtime context
    like database connections, not the user's prompt or conversation history
    (which are passed via agent.run() parameters).
    """

    db_client: DuckDBClient
    user_id: str | None = None  # For future user tracking/analytics


# Create orchestrator agent
orchestrator_agent = Agent(
    settings.default_llm_model,
    output_type=OrchestratorResponse,
    deps_type=OrchestratorDeps,
    system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
    retries=1,
)


@orchestrator_agent.tool
async def call_sql_agent(ctx: RunContext[OrchestratorDeps], question: str) -> dict[str, Any]:
    """
    Call the SQL agent to query and analyze NBA data.

    Use this tool when the user asks about statistics, game data,
    team performance, schedules, or any basketball metrics.

    Args:
        question: The data question to send to the SQL agent

    Returns:
        Dictionary with message, sql_query, data_summary, and results data
    """
    try:
        result = await run_sql_agent(question, ctx.deps.db_client)
        return {
            "status": "success",
            "message": result.message,
            "sql_query": result.sql_query,
            "data_summary": result.data_summary,
            "results": result.results,  # Include results for viz agent
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"SQL agent error: {str(e)}",
            "sql_query": None,
            "data_summary": None,
            "results": None,
        }


@orchestrator_agent.tool
async def call_viz_agent(
    ctx: RunContext[OrchestratorDeps],
    user_question: str,
    sql_query: str,
    query_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Call the visualization agent to create charts from data.

    Use this tool when the user wants to visualize data as a chart or graph.
    You should call the SQL agent FIRST to get data, then pass all context to this tool.

    The viz agent uses three pieces of context to make smart chart decisions:
    1. User's original question (intent: ranking, comparison, trend, etc.)
    2. SQL query executed (data structure: columns, ORDER BY, aggregations)
    3. Query results (data shape: row count, values)

    Args:
        user_question: The original question the user asked
        sql_query: The SQL query that was executed by the SQL agent
        query_results: The results returned from the SQL query

    Returns:
        Dictionary with message, chart_spec (Plotly JSON), and chart_type
    """
    try:
        result = await run_viz_agent(
            user_question=user_question,
            sql_query=sql_query,
            query_results=query_results,
            db_client=ctx.deps.db_client,
        )
        return {
            "status": "success",
            "message": result.message,
            "chart_spec": result.chart_spec,
            "chart_type": result.chart_type,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Visualization agent error: {str(e)}",
            "chart_spec": None,
            "chart_type": None,
        }


async def run_orchestrator(
    user_question: str,
    db_client: DuckDBClient,
    conversation_history: list[dict[str, str]] | None = None,
) -> OrchestratorResponse:
    """
    Run the orchestrator agent to handle a user question.

    The orchestrator routes questions to appropriate specialist agents
    and returns a unified response.

    Args:
        user_question: The user's question
        db_client: Database client instance to pass to specialist agents
        conversation_history: Optional conversation history for multi-turn conversations

    Returns:
        OrchestratorResponse with message and metadata
    """
    deps = OrchestratorDeps(db_client=db_client)

    # Run agent with conversation history if provided
    if conversation_history:
        result = await orchestrator_agent.run(
            user_question,
            deps=deps,
            message_history=conversation_history
        )
    else:
        result = await orchestrator_agent.run(user_question, deps=deps)

    return result.output
