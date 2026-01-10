"""Authentication and authorization for the API.

Supports two modes:
1. Admin mode: Full access with API key (no limits)
2. Demo mode: Anonymous users with IP-based rate limiting
"""

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Header, HTTPException, Request, status

from app.config import settings

# Demo mode limits (anonymous users)
DEMO_LIMITS = {
    "queries_per_hour": 6,
    "tokens_per_query": 20_000,
}

# In-memory storage for IP-based rate limiting
# For production, replace with Redis
_ip_usage: dict[str, dict] = {}


class DemoLimitError(Exception):
    """Raised when demo user exceeds rate limits."""

    pass


class User:
    """User information extracted from request."""

    def __init__(self, is_admin: bool, ip_address: str | None = None):
        self.is_admin = is_admin
        self.ip_address = ip_address
        self.tier = "admin" if is_admin else "demo"

    def __repr__(self):
        return f"User(tier={self.tier}, ip={self.ip_address})"


def check_ip_rate_limit(ip_address: str) -> dict:
    """Check if IP address is within rate limits.

    Args:
        ip_address: Client IP address

    Returns:
        Dictionary with usage info

    Raises:
        DemoLimitError: If rate limit exceeded
    """
    now = datetime.now()
    hour_ago = now - timedelta(hours=1)

    # Get or initialize IP usage
    if ip_address not in _ip_usage:
        _ip_usage[ip_address] = {"queries": [], "first_seen": now}

    ip_data = _ip_usage[ip_address]

    # Clean up queries older than 1 hour
    ip_data["queries"] = [q for q in ip_data["queries"] if q > hour_ago]

    # Check limit
    queries_this_hour = len(ip_data["queries"])
    if queries_this_hour >= DEMO_LIMITS["queries_per_hour"]:
        raise DemoLimitError(
            f"Demo limit reached: {queries_this_hour}/{DEMO_LIMITS['queries_per_hour']} queries per hour. "
            "Please wait an hour or sign in for more access."
        )

    return {
        "queries_used": queries_this_hour,
        "queries_remaining": DEMO_LIMITS["queries_per_hour"] - queries_this_hour,
        "tokens_per_query_limit": DEMO_LIMITS["tokens_per_query"],
    }


def record_ip_query(ip_address: str) -> None:
    """Record that an IP made a query.

    Args:
        ip_address: Client IP address
    """
    now = datetime.now()

    if ip_address not in _ip_usage:
        _ip_usage[ip_address] = {"queries": [], "first_seen": now}

    _ip_usage[ip_address]["queries"].append(now)


async def get_current_user(
    request: Request, authorization: Annotated[str | None, Header()] = None
) -> User:
    """Get current user from request.

    Checks for admin API key first, falls back to demo mode with IP-based limits.

    Args:
        request: FastAPI request object
        authorization: Optional Authorization header

    Returns:
        User object with tier and limits

    Raises:
        DemoLimitError: If demo user exceeds limits
    """
    # Check for admin API key
    if authorization:
        if authorization == f"Bearer {settings.admin_api_key}":
            return User(is_admin=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
            )

    # Demo mode: Use IP-based rate limiting
    client_ip = request.client.host if request.client else "unknown"

    # Check rate limit (raises DemoLimitError if exceeded)
    check_ip_rate_limit(client_ip)

    return User(is_admin=False, ip_address=client_ip)


def get_usage_info_for_ip(ip_address: str) -> dict:
    """Get usage information for an IP address.

    Args:
        ip_address: Client IP address

    Returns:
        Dictionary with usage stats
    """
    try:
        usage = check_ip_rate_limit(ip_address)
        return {
            "tier": "demo",
            "queries_used": usage["queries_used"],
            "queries_remaining": usage["queries_remaining"],
            "queries_limit": DEMO_LIMITS["queries_per_hour"],
            "tokens_per_query_limit": DEMO_LIMITS["tokens_per_query"],
            "reset_in_minutes": 60,  # Sliding window, so approximate
        }
    except DemoLimitError:
        return {
            "tier": "demo",
            "queries_used": DEMO_LIMITS["queries_per_hour"],
            "queries_remaining": 0,
            "queries_limit": DEMO_LIMITS["queries_per_hour"],
            "tokens_per_query_limit": DEMO_LIMITS["tokens_per_query"],
            "reset_in_minutes": 60,
        }
