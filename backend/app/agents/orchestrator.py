"""Orchestrator agent that coordinates specialist agents."""

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from app.agents.sql_agent import run_sql_agent
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
        Dictionary with message, sql_query, and optional data_summary
    """
    try:
        result = await run_sql_agent(question, ctx.deps.db_client)
        return {
            "status": "success",
            "message": result.message,
            "sql_query": result.sql_query,
            "data_summary": result.data_summary,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"SQL agent error: {str(e)}",
            "sql_query": None,
            "data_summary": None,
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
        conversation_history: Optional conversation history (note: not yet used with message_history)

    Returns:
        OrchestratorResponse with message and metadata
    """
    deps = OrchestratorDeps(db_client=db_client)
    result = await orchestrator_agent.run(user_question, deps=deps)
    return result.data
