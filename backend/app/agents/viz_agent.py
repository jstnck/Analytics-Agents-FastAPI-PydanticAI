"""Visualization Agent for generating Plotly charts from data."""

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelSettings, RunContext

from app.agents.rate_limits import VIZ_AGENT_LIMITS
from app.config import settings
from app.database.duckdb_client import DuckDBClient
from app.utils.prompts import VIZ_AGENT_SYSTEM_PROMPT


class VizAgentResponse(BaseModel):
    """Structured response from visualization agent."""

    message: str = Field(..., description="Brief description of the visualization")
    chart_spec: dict[str, Any] | None = Field(
        None, description="Plotly chart specification (data + layout)"
    )
    chart_type: str | None = Field(None, description="Type of chart (bar, line, scatter, etc.)")


@dataclass
class VizAgentDeps:
    """Dependencies for the visualization agent.

    Following PydanticAI best practices, dependencies contain runtime context
    like database connections, not the user's prompt (which is passed separately).
    """

    db_client: DuckDBClient
    user_id: str | None = None  # For future user tracking/analytics


# Create visualization agent with configured model and structured response
viz_agent = Agent(
    settings.default_llm_model,
    output_type=VizAgentResponse,
    deps_type=VizAgentDeps,
    system_prompt=VIZ_AGENT_SYSTEM_PROMPT,
    retries=1,
    instrument=True,
    model_settings=ModelSettings(temperature=0),
)


@viz_agent.tool
async def create_chart(
    ctx: RunContext[VizAgentDeps],
    chart_type: str,
    data: list[dict[str, Any]],
    x_column: str,
    y_column: str,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
) -> dict[str, Any]:
    """
    Create a Plotly chart specification from data.

    Generates a chart configuration that can be rendered by Plotly.js in the frontend.

    Args:
        chart_type: Type of chart (bar, line, scatter, pie, etc.)
        data: List of data dictionaries with column values
        x_column: Column name for x-axis
        y_column: Column name for y-axis
        title: Optional chart title
        x_label: Optional x-axis label
        y_label: Optional y-axis label

    Returns:
        Dictionary with Plotly chart specification (data + layout)
    """
    try:
        # Extract x and y values from data
        x_values = [row.get(x_column) for row in data]
        y_values = [row.get(y_column) for row in data]

        # Build Plotly chart specification
        chart_spec = {
            "data": [
                {
                    "type": chart_type,
                    "x": x_values,
                    "y": y_values,
                    "name": y_label or y_column,
                }
            ],
            "layout": {
                "title": {"text": title or f"{y_column} by {x_column}"},
                "xaxis": {"title": x_label or x_column},
                "yaxis": {"title": y_label or y_column},
                "template": "plotly_white",
            },
        }

        return {
            "status": "success",
            "chart_spec": chart_spec,
            "chart_type": chart_type,
            "data_points": len(data),
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Chart generation failed: {str(e)}",
        }


@viz_agent.tool
async def create_multi_series_chart(
    ctx: RunContext[VizAgentDeps],
    chart_type: str,
    data: list[dict[str, Any]],
    x_column: str,
    y_columns: list[str],
    title: str | None = None,
    x_label: str | None = None,
) -> dict[str, Any]:
    """
    Create a multi-series Plotly chart (multiple y-values).

    Useful for comparing multiple metrics on the same chart.

    Args:
        chart_type: Type of chart (bar, line, scatter)
        data: List of data dictionaries
        x_column: Column name for x-axis
        y_columns: List of column names for multiple y-series
        title: Optional chart title
        x_label: Optional x-axis label

    Returns:
        Dictionary with Plotly chart specification
    """
    try:
        x_values = [row.get(x_column) for row in data]

        # Create a trace for each y column
        traces = []
        for y_col in y_columns:
            y_values = [row.get(y_col) for row in data]
            traces.append({"type": chart_type, "x": x_values, "y": y_values, "name": y_col})

        chart_spec = {
            "data": traces,
            "layout": {
                "title": {"text": title or f"Comparison by {x_column}"},
                "xaxis": {"title": x_label or x_column},
                "yaxis": {"title": "Values"},
                "template": "plotly_white",
                "barmode": "group" if chart_type == "bar" else None,
            },
        }

        return {
            "status": "success",
            "chart_spec": chart_spec,
            "chart_type": chart_type,
            "series_count": len(y_columns),
            "data_points": len(data),
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Multi-series chart generation failed: {str(e)}",
        }


async def run_viz_agent(
    user_question: str,
    sql_query: str,
    query_results: list[dict[str, Any]],
    db_client: DuckDBClient,
) -> VizAgentResponse:
    """
    Run the visualization agent to create a chart.

    The agent uses three pieces of context to make smart chart decisions:
    1. User's original question - understand intent (compare, trend, ranking, etc.)
    2. SQL query executed - understand data structure (columns, aggregations, ordering)
    3. Query results - understand data shape (row count, column types, values)

    Args:
        user_question: The user's original question
        sql_query: The SQL query that was executed
        query_results: The results from the SQL query
        db_client: Database client instance

    Returns:
        VizAgentResponse with message, chart_spec, and chart_type
    """
    deps = VizAgentDeps(db_client=db_client)

    # Build comprehensive context for the viz agent
    prompt = f"""User Question: {user_question}

SQL Query Executed:
{sql_query}

Query Results ({len(query_results)} rows):
{query_results}

Based on the user's question, the SQL query structure, and the result data, create an appropriate visualization."""

    result = await viz_agent.run(prompt, deps=deps, usage_limits=VIZ_AGENT_LIMITS)
    return result.output
