"""Vercel AI SDK streaming adapter for orchestrator responses."""

import logging

from fastapi_ai_sdk import AIStreamBuilder

from app.agents.orchestrator import OrchestratorResponse

logger = logging.getLogger(__name__)


async def stream_orchestrator_response(
    orchestrator_result: OrchestratorResponse,
    message_id: str | None = None,
) -> AIStreamBuilder:
    """
    Convert orchestrator response to AI SDK stream.

    Streams:
    - Text response (chunked for streaming effect)
    - SQL query (as data part)
    - Chart spec (as data part)
    - Chart type (as data part)
    """
    builder = AIStreamBuilder(message_id=message_id)

    try:
        builder.start()

        # Stream main text response in chunks
        builder.text(orchestrator_result.message, chunk_size=50)

        # Stream metadata as data parts
        if orchestrator_result.metadata:
            # SQL query
            if sql_query := orchestrator_result.metadata.get("sql_query"):
                # Wrap scalar values in dict to satisfy Pydantic validation
                builder.data("sql_query", {"query": sql_query})
                logger.debug(f"Streamed SQL query: {sql_query[:100]}...")

            # Chart spec (usually already a dict)
            if chart_spec := orchestrator_result.metadata.get("chart_spec"):
                if isinstance(chart_spec, dict):
                    builder.data("chart_spec", chart_spec)
                else:
                    builder.data("chart_spec", {"spec": chart_spec})
                logger.debug("Streamed chart spec")

            # Chart type
            if chart_type := orchestrator_result.metadata.get("chart_type"):
                builder.data("chart_type", {"type": chart_type})

            # Data summary
            if data_summary := orchestrator_result.metadata.get("data_summary"):
                if isinstance(data_summary, dict):
                    builder.data("data_summary", data_summary)
                else:
                    builder.data("data_summary", {"summary": data_summary})

        builder.finish()

    except Exception as e:
        logger.exception("Error streaming orchestrator response")
        builder.text(f"Error: {str(e)}")
        builder.finish()

    return builder
