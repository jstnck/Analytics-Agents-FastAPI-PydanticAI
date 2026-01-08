from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    """Individual chat message."""

    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Message content")
    timestamp: datetime | None = Field(default=None, description="Message timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "user",
                "content": "What were the total sales last month?",
                "timestamp": "2024-01-08T12:00:00Z",
            }
        }
    )


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., min_length=1, description="User's message to the agent")
    conversation_id: str | None = Field(
        default=None, description="Optional conversation ID for context"
    )
    history: list[ChatMessage] | None = Field(
        default=None, description="Optional conversation history"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "What were the total sales last month?",
                "conversation_id": "conv-123",
                "history": [],
            }
        }
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    message: str = Field(..., description="Agent's response message")
    conversation_id: str = Field(..., description="Conversation identifier")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Response timestamp"
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Optional metadata (SQL queries, charts, etc.)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Total sales last month were $125,430.",
                "conversation_id": "conv-123",
                "timestamp": "2024-01-08T12:00:01Z",
                "metadata": {
                    "sql_query": "SELECT SUM(amount) FROM sales WHERE month = 'December'",
                    "chart_type": "bar",
                },
            }
        }
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(default=None, description="Detailed error information")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Error timestamp"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Query execution failed",
                "detail": "Table 'sales' does not exist",
                "timestamp": "2024-01-08T12:00:01Z",
            }
        }
    )
