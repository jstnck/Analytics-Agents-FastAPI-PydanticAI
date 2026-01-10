"""Rate limiting configuration for AI agents.

Implements Strategy 1: Conservative Per-Agent Budget
- Per-agent limits prevent individual agents from monopolizing resources
- Per-conversation limits control total cost and prevent runaway loops
- Token-based limits are primary constraints (more important than request counts)
"""

from pydantic_ai import UsageLimits


# Per-agent limits (per invocation)
# These apply each time an agent is called
ORCHESTRATOR_LIMITS = UsageLimits(
    request_limit=6,  # SQL call + viz call + retries + response formatting
    total_tokens_limit=50_000,  # ~$0.15 per orchestrator call (Claude Sonnet 4)
)

SQL_AGENT_LIMITS = UsageLimits(
    request_limit=6,  # Schema + query generation + retries + result formatting
    total_tokens_limit=20_000,  # SQL queries are relatively small (~$0.06)
)

VIZ_AGENT_LIMITS = UsageLimits(
    request_limit=4,  # Chart decision + tool call + retry + formatting
    total_tokens_limit=30_000,  # Chart specs can be verbose (~$0.09)
)


# Per-conversation limits (cumulative across all agents)
# These track total usage across an entire conversation
class ConversationLimits:
    """Global limits for an entire conversation."""

    MAX_REQUESTS = 10  # Max total LLM requests per conversation
    MAX_TOKENS = 150_000  # Max total tokens per conversation (~$0.45)
    MAX_TOOL_CALLS = 15  # Max tool calls (SQL queries, chart generations)


class RateLimitError(Exception):
    """Raised when rate limits are exceeded."""

    pass


class ConversationTracker:
    """Tracks usage across a conversation to enforce global limits.

    Usage:
        tracker = ConversationTracker()
        tracker.add_usage(agent_result)
        tracker.check_limits()  # Raises RateLimitError if exceeded
    """

    def __init__(self):
        """Initialize tracker with zero usage."""
        self.total_requests = 0
        self.total_tokens = 0
        self.total_tool_calls = 0

    def add_usage(self, usage_info: dict) -> None:
        """Add usage from an agent run.

        Args:
            usage_info: Dictionary with 'requests', 'tokens', 'tool_calls' keys
        """
        self.total_requests += usage_info.get("requests", 0)
        self.total_tokens += usage_info.get("tokens", 0)
        self.total_tool_calls += usage_info.get("tool_calls", 0)

    def check_limits(self) -> None:
        """Check if conversation has exceeded limits.

        Raises:
            RateLimitError: If any limit is exceeded
        """
        if self.total_requests >= ConversationLimits.MAX_REQUESTS:
            raise RateLimitError(
                f"Conversation request limit exceeded: {self.total_requests}/{ConversationLimits.MAX_REQUESTS}. "
                "Please start a new conversation."
            )

        if self.total_tokens >= ConversationLimits.MAX_TOKENS:
            raise RateLimitError(
                f"Conversation token limit exceeded: {self.total_tokens}/{ConversationLimits.MAX_TOKENS}. "
                "Please start a new conversation."
            )

        if self.total_tool_calls >= ConversationLimits.MAX_TOOL_CALLS:
            raise RateLimitError(
                f"Conversation tool call limit exceeded: {self.total_tool_calls}/{ConversationLimits.MAX_TOOL_CALLS}. "
                "Please start a new conversation."
            )

    def get_usage_summary(self) -> dict:
        """Get current usage summary.

        Returns:
            Dictionary with usage stats and remaining capacity
        """
        return {
            "requests": {
                "used": self.total_requests,
                "limit": ConversationLimits.MAX_REQUESTS,
                "remaining": ConversationLimits.MAX_REQUESTS - self.total_requests,
            },
            "tokens": {
                "used": self.total_tokens,
                "limit": ConversationLimits.MAX_TOKENS,
                "remaining": ConversationLimits.MAX_TOKENS - self.total_tokens,
            },
            "tool_calls": {
                "used": self.total_tool_calls,
                "limit": ConversationLimits.MAX_TOOL_CALLS,
                "remaining": ConversationLimits.MAX_TOOL_CALLS - self.total_tool_calls,
            },
        }
