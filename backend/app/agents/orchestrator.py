"""Orchestrator agent that coordinates specialist agents."""

import json
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelSettings, RunContext

from app.agents.rate_limits import ORCHESTRATOR_LIMITS, ConversationTracker, RateLimitError
from app.agents.sql_agent import run_sql_agent
from app.agents.viz_agent import run_viz_agent
from app.config import settings
from app.database.duckdb_client import DuckDBClient
from app.utils.prompts import ORCHESTRATOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


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
    instrument=True,
    model_settings=ModelSettings(temperature=0),
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
    logger.info(f"Orchestrator calling SQL agent with question: {question[:100]}...")
    try:
        result = await run_sql_agent(question, ctx.deps.db_client)
        logger.info(f"SQL agent succeeded. Query: {result.sql_query}")
        return {
            "status": "success",
            "message": result.message,
            "sql_query": result.sql_query,
            "data_summary": result.data_summary,
            "results": result.results,  # Include results for viz agent
        }
    except Exception as e:
        logger.exception(f"SQL agent failed for question: {question}")
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
    logger.info(f"Orchestrator calling viz agent. Results count: {len(query_results)}")
    try:
        result = await run_viz_agent(
            user_question=user_question,
            sql_query=sql_query,
            query_results=query_results,
            db_client=ctx.deps.db_client,
        )
        logger.info(f"Viz agent succeeded. Chart type: {result.chart_type}")
        return {
            "status": "success",
            "message": result.message,
            "chart_spec": result.chart_spec,
            "chart_type": result.chart_type,
        }
    except Exception as e:
        logger.exception(f"Viz agent failed for question: {user_question}")
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
    conversation_tracker: ConversationTracker | None = None,
) -> OrchestratorResponse:
    """
    Run the orchestrator agent to handle a user question.

    The orchestrator routes questions to appropriate specialist agents
    and returns a unified response.

    Args:
        user_question: The user's question
        db_client: Database client instance to pass to specialist agents
        conversation_history: Optional conversation history for multi-turn conversations
        conversation_tracker: Optional tracker for enforcing per-conversation limits

    Returns:
        OrchestratorResponse with message and metadata

    Raises:
        RateLimitError: If conversation limits are exceeded
    """
    logger.info(f"Orchestrator received question: {user_question[:100]}...")
    deps = OrchestratorDeps(db_client=db_client)

    # Check conversation limits before running
    if conversation_tracker:
        logger.debug(f"Checking conversation limits: {conversation_tracker.get_usage_summary()}")
        conversation_tracker.check_limits()

    # Run agent with conversation history if provided
    try:
        if conversation_history:
            logger.debug(f"Running with conversation history ({len(conversation_history)} messages)")
            result = await orchestrator_agent.run(
                user_question,
                deps=deps,
                message_history=conversation_history,
                usage_limits=ORCHESTRATOR_LIMITS,
            )
        else:
            logger.debug("Running without conversation history")
            result = await orchestrator_agent.run(
                user_question, deps=deps, usage_limits=ORCHESTRATOR_LIMITS
            )

        # Track usage if tracker provided
        if conversation_tracker and result.usage():
            usage = result.usage()
            conversation_tracker.add_usage(
                {
                    "requests": usage.requests,
                    "tokens": usage.total_tokens,
                    "tool_calls": len(result.all_messages()),  # Count tool calls from messages
                }
            )
            logger.info(
                f"Orchestrator usage - Requests: {usage.requests}, "
                f"Tokens: {usage.total_tokens}, Tool calls: {len(result.all_messages())}"
            )

        logger.info("Orchestrator completed successfully")
        return result.output

    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded: {str(e)}")
        raise
    except Exception as e:
        logger.exception(f"Orchestrator failed for question: {user_question}")
        raise


# Map tool names to user-friendly step messages
STEP_MESSAGES = {
    "call_sql_agent": "Querying database...",
    "call_viz_agent": "Generating chart...",
}


async def run_orchestrator_stream(
    user_question: str,
    db_client: DuckDBClient,
    conversation_history: list[dict[str, str]] | None = None,
    conversation_tracker: ConversationTracker | None = None,
) -> AsyncGenerator[str, None]:
    """
    Run the orchestrator agent with streaming support.

    Yields Server-Sent Events (SSE) with high-level progress steps:
    - step events: User-friendly progress messages
    - final event: Complete response with metadata

    Args:
        user_question: The user's question
        db_client: Database client instance
        conversation_history: Optional conversation history
        conversation_tracker: Optional tracker for enforcing limits

    Yields:
        SSE-formatted strings (data: {json}\n\n)

    Raises:
        RateLimitError: If conversation limits are exceeded
    """
    logger.info(f"Orchestrator streaming for question: {user_question[:100]}...")
    deps = OrchestratorDeps(db_client=db_client)

    # Check conversation limits before running
    if conversation_tracker:
        logger.debug(f"Checking conversation limits: {conversation_tracker.get_usage_summary()}")
        conversation_tracker.check_limits()

    # Emit initial thinking step
    yield f"data: {json.dumps({'type': 'step', 'message': 'Analyzing your question...'})}\n\n"

    try:
        # Run agent with streaming (use async context manager)
        if conversation_history:
            logger.debug(f"Running with conversation history ({len(conversation_history)} messages)")
            stream_ctx = orchestrator_agent.run_stream(
                user_question,
                deps=deps,
                message_history=conversation_history,
                usage_limits=ORCHESTRATOR_LIMITS,
            )
        else:
            logger.debug("Running without conversation history")
            stream_ctx = orchestrator_agent.run_stream(
                user_question, deps=deps, usage_limits=ORCHESTRATOR_LIMITS
            )

        # Track which steps we've already emitted
        emitted_steps: set[str] = set()

        async with stream_ctx as result:
            # Stream the result and emit step events for tool calls
            async for _message in result.stream(debounce_by=0):
                # Check all messages for tool calls
                all_messages = result.all_messages()
                for msg in all_messages:
                    # Look for tool use in message parts
                    if hasattr(msg, "parts"):
                        for part in msg.parts:
                            if hasattr(part, "tool_name"):
                                tool_name = part.tool_name
                                if tool_name in STEP_MESSAGES and tool_name not in emitted_steps:
                                    step_msg = STEP_MESSAGES[tool_name]
                                    logger.debug(f"Emitting step: {step_msg}")
                                    yield f"data: {json.dumps({'type': 'step', 'message': step_msg})}\n\n"
                                    emitted_steps.add(tool_name)

            # Get the final validated output from streamed result
            output = await result.get_output()

            # Track usage if tracker provided
            if conversation_tracker and result.usage():
                usage = result.usage()
                conversation_tracker.add_usage(
                    {
                        "requests": usage.requests,
                        "tokens": usage.total_tokens,
                        "tool_calls": len(result.all_messages()),
                    }
                )
                logger.info(
                    f"Orchestrator streaming usage - Requests: {usage.requests}, "
                    f"Tokens: {usage.total_tokens}, Tool calls: {len(result.all_messages())}"
                )

            # Emit final response
            logger.info("Orchestrator streaming completed successfully")
            yield f"data: {json.dumps({'type': 'final', 'message': output.message, 'metadata': output.metadata})}\n\n"

    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        raise
    except Exception as e:
        logger.exception(f"Orchestrator streaming failed for question: {user_question}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        raise
