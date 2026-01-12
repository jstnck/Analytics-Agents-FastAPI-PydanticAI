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

        # Debug: Log what metadata we have
        logger.info(f"Orchestrator metadata keys: {list(orchestrator_result.metadata.keys()) if orchestrator_result.metadata else 'None'}")

        # Stream main text response in chunks
        builder.text(orchestrator_result.message, chunk_size=50)

        # Stream metadata as data parts
        # Each data part becomes a field in the merged metadata object on the frontend
        if orchestrator_result.metadata:
            # SQL query - send with correct field name
            if sql_query := orchestrator_result.metadata.get("sql_query"):
                builder.data("sql_query_data", {"sql_query": sql_query})
                logger.debug(f"Streamed SQL query: {sql_query[:100]}...")

            # Chart spec - send with correct field name
            if chart_spec := orchestrator_result.metadata.get("chart_spec"):
                builder.data("chart_spec_data", {"chart_spec": chart_spec})
                logger.debug("Streamed chart spec")

            # Chart type - send with correct field name
            if chart_type := orchestrator_result.metadata.get("chart_type"):
                builder.data("chart_type_data", {"chart_type": chart_type})

            # Data summary - send with correct field name
            if data_summary := orchestrator_result.metadata.get("data_summary"):
                builder.data("data_summary_data", {"data_summary": data_summary})

        builder.finish()

    except Exception as e:
        logger.exception("Error streaming orchestrator response")
        builder.text(f"Error: {str(e)}")
        builder.finish()

    return builder
