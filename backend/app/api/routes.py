import logging
from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_ai_sdk import ai_endpoint

from app.agents.orchestrator import run_orchestrator
from app.agents.rate_limits import ConversationTracker, RateLimitError
from app.api.streaming import stream_orchestrator_response
from app.auth import (
    DEMO_LIMITS,
    DemoLimitError,
    User,
    get_current_user,
    get_usage_info_for_ip,
    record_ip_query,
)
from app.database.duckdb_client import DuckDBClient, get_db_client
from app.schemas.chat import ChatRequest, ChatResponse, ErrorResponse, VercelChatRequest

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for conversation trackers (keyed by conversation_id)
# For production, replace with Redis or similar persistent store
_conversation_trackers: dict[str, ConversationTracker] = {}

@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now(UTC)}


@router.get("/usage")
async def get_usage(request: Request, user: Annotated[User, Depends(get_current_user)]) -> dict[str, Any]:
    """Get usage information for current user.

    Demo users see IP-based query limits.
    Admin users see unlimited status.
    """
    logger.debug(f"Usage request from user: {user.ip_address}, admin: {user.is_admin}")
    if user.is_admin:
        return {
            "tier": "admin",
            "limits": "unlimited",
            "message": "Admin access - no rate limits",
        }

    # Demo mode: Return IP-based usage
    return get_usage_info_for_ip(user.ip_address)


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def chat(
    request: ChatRequest,
    db_client: Annotated[DuckDBClient, Depends(get_db_client)],
    user: Annotated[User, Depends(get_current_user)],
) -> ChatResponse:
    """
    Chat endpoint for agent interactions.

    Supports two modes:
    - Demo mode: Anonymous users with 3 queries/hour, 20K tokens per query
    - Admin mode: Full access with API key (no limits)

    Rate Limits:
    - Demo users: IP-based rate limiting (3 queries/hour)
    - Admin users: No limits
    - Per-agent token limits still apply to both
    """
    logger.info(f"Chat request from {'admin' if user.is_admin else f'IP {user.ip_address}'}: {request.message[:100]}...")

    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv-{uuid4().hex[:12]}"
        logger.debug(f"Conversation ID: {conversation_id}")

        # Get or create conversation tracker (only for demo users)
        tracker = None
        if not user.is_admin:
            if conversation_id not in _conversation_trackers:
                _conversation_trackers[conversation_id] = ConversationTracker()
                logger.debug(f"Created new conversation tracker for {conversation_id}")
            tracker = _conversation_trackers[conversation_id]

        # Convert history to simple dict format for orchestrator
        history = None
        if request.history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]
            logger.debug(f"Including {len(history)} messages from conversation history")

        # Call orchestrator agent with injected db_client and tracker
        # Admin users skip conversation limits by passing None
        result = await run_orchestrator(
            request.message, db_client, history, conversation_tracker=tracker
        )

        # Record query for demo users (after successful response)
        if not user.is_admin and user.ip_address:
            record_ip_query(user.ip_address)
            logger.debug(f"Recorded query for IP: {user.ip_address}")

        logger.info(f"Chat request completed successfully for conversation {conversation_id}")
        return ChatResponse(
            message=result.message,
            conversation_id=conversation_id,
            timestamp=datetime.now(UTC),
            metadata=result.metadata,
        )

    except DemoLimitError as e:
        logger.warning(f"Demo limit exceeded for IP {user.ip_address}: {str(e)}")
        # Return 429 for demo limit errors
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        ) from e

    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded for conversation {conversation_id}: {str(e)}")
        # Return 429 Too Many Requests for conversation limit errors
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        ) from e

    except Exception as e:
        logger.exception(f"Unexpected error in chat endpoint for conversation {conversation_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.post("/chat/stream")
@ai_endpoint()
async def chat_stream(
    request: VercelChatRequest,
    db_client: Annotated[DuckDBClient, Depends(get_db_client)],
    user: Annotated[User, Depends(get_current_user)],
):
    """
    Streaming chat endpoint using Vercel AI SDK protocol.

    Returns SSE stream compatible with useChat hook.
    Same functionality as /chat but with real-time streaming.
    """
    if not request.messages:
        # Should be handled by pydantic validation but just in case
        raise HTTPException(status_code=400, detail="No messages provided")

    # Extract conversation ID from request if present (Vercel SDK sends it as 'id')
    conversation_id = request.id or f"conv-{uuid4().hex[:12]}"
    
    # Extract latest message content
    last_msg = request.messages[-1]
    message_content = last_msg.content
    if not message_content and last_msg.parts:
        text_parts = [p.text for p in last_msg.parts if p.type == 'text' and p.text]
        message_content = "".join(text_parts)
    
    if not message_content:
        # Fallback or error if really empty
        message_content = ""

    logger.info(f"Streaming chat request from {'admin' if user.is_admin else f'IP {user.ip_address}'}: {message_content[:100]}...")

    try:
        # Get or create conversation tracker (demo users only)
        tracker = None
        if not user.is_admin:
            if conversation_id not in _conversation_trackers:
                _conversation_trackers[conversation_id] = ConversationTracker()
            tracker = _conversation_trackers[conversation_id]

        # Convert history
        history = []
        for msg in request.messages[:-1]:
            content = msg.content
            if not content and msg.parts:
                text_parts = [p.text for p in msg.parts if p.type == 'text' and p.text]
                content = "".join(text_parts)
            
            if content:
                history.append({"role": msg.role, "content": content})

        # Call orchestrator (same as non-streaming endpoint)
        result = await run_orchestrator(
            message_content, db_client, history, conversation_tracker=tracker
        )

        # Record query for demo users
        if not user.is_admin and user.ip_address:
            record_ip_query(user.ip_address)

        # Build and return stream response
        builder = await stream_orchestrator_response(result, message_id=conversation_id)
        logger.info(f"Streaming chat completed for conversation {conversation_id}")
        return builder

    except DemoLimitError as e:
        logger.warning(f"Demo limit exceeded for IP {user.ip_address}: {str(e)}")
        # Return error in stream format
        from fastapi_ai_sdk import AIStreamBuilder
        builder = AIStreamBuilder()
        builder.start()
        builder.text(f"Error: {str(e)}")
        builder.finish()
        return builder

    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded for conversation {conversation_id}: {str(e)}")
        from fastapi_ai_sdk import AIStreamBuilder
        builder = AIStreamBuilder()
        builder.start()
        builder.text(f"Rate limit exceeded: {str(e)}")
        builder.finish()
        return builder

    except Exception as e:
        logger.exception(f"Unexpected error in streaming chat")
        from fastapi_ai_sdk import AIStreamBuilder
        builder = AIStreamBuilder()
        builder.start()
        builder.text(f"An error occurred: {str(e)}")
        builder.finish()
        return builder
