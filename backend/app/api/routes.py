from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.orchestrator import run_orchestrator
from app.database.duckdb_client import DuckDBClient
from app.schemas.chat import ChatRequest, ChatResponse, ErrorResponse

router = APIRouter()


def get_db_client() -> DuckDBClient:
    """
    Dependency for getting a database client instance.

    Following PydanticAI best practices, we inject the db_client
    as a dependency rather than using a global singleton.
    """
    return DuckDBClient()


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now(UTC)}


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def chat(
    request: ChatRequest, db_client: DuckDBClient = Depends(get_db_client)
) -> ChatResponse:
    """
    Chat endpoint for agent interactions.

    Sends a message to the orchestrator agent which routes to appropriate specialist agents.
    Uses dependency injection to provide the database client.
    """
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv-{uuid4().hex[:12]}"

        # Convert history to simple dict format for orchestrator
        history = None
        if request.history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]

        # Call orchestrator agent with injected db_client
        result = await run_orchestrator(request.message, db_client, history)

        return ChatResponse(
            message=result.message,
            conversation_id=conversation_id,
            timestamp=datetime.now(UTC),
            metadata=result.metadata,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
