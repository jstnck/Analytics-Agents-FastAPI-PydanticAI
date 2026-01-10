"""Tests for rate limiting functionality."""

import pytest

from app.agents.rate_limits import ConversationLimits, ConversationTracker, RateLimitError


def test_conversation_tracker_initialization():
    """Test that tracker initializes with zero usage."""
    tracker = ConversationTracker()
    assert tracker.total_requests == 0
    assert tracker.total_tokens == 0
    assert tracker.total_tool_calls == 0


def test_conversation_tracker_add_usage():
    """Test adding usage to tracker."""
    tracker = ConversationTracker()

    tracker.add_usage({"requests": 2, "tokens": 10000, "tool_calls": 3})

    assert tracker.total_requests == 2
    assert tracker.total_tokens == 10000
    assert tracker.total_tool_calls == 3


def test_conversation_tracker_cumulative():
    """Test that usage accumulates across multiple adds."""
    tracker = ConversationTracker()

    tracker.add_usage({"requests": 1, "tokens": 5000, "tool_calls": 2})
    tracker.add_usage({"requests": 2, "tokens": 15000, "tool_calls": 1})
    tracker.add_usage({"requests": 1, "tokens": 8000, "tool_calls": 3})

    assert tracker.total_requests == 4
    assert tracker.total_tokens == 28000
    assert tracker.total_tool_calls == 6


def test_conversation_tracker_check_limits_pass():
    """Test that check_limits passes when under limits."""
    tracker = ConversationTracker()

    tracker.add_usage({"requests": 5, "tokens": 50000, "tool_calls": 7})

    # Should not raise
    tracker.check_limits()


def test_conversation_tracker_request_limit_exceeded():
    """Test that exceeding request limit raises error."""
    tracker = ConversationTracker()

    tracker.add_usage({"requests": ConversationLimits.MAX_REQUESTS, "tokens": 1000})

    with pytest.raises(RateLimitError) as exc_info:
        tracker.check_limits()

    assert "request limit exceeded" in str(exc_info.value).lower()


def test_conversation_tracker_token_limit_exceeded():
    """Test that exceeding token limit raises error."""
    tracker = ConversationTracker()

    tracker.add_usage({"tokens": ConversationLimits.MAX_TOKENS, "requests": 1})

    with pytest.raises(RateLimitError) as exc_info:
        tracker.check_limits()

    assert "token limit exceeded" in str(exc_info.value).lower()


def test_conversation_tracker_tool_call_limit_exceeded():
    """Test that exceeding tool call limit raises error."""
    tracker = ConversationTracker()

    tracker.add_usage({"tool_calls": ConversationLimits.MAX_TOOL_CALLS, "requests": 1})

    with pytest.raises(RateLimitError) as exc_info:
        tracker.check_limits()

    assert "tool call limit exceeded" in str(exc_info.value).lower()


def test_conversation_tracker_usage_summary():
    """Test getting usage summary."""
    tracker = ConversationTracker()

    tracker.add_usage({"requests": 3, "tokens": 45000, "tool_calls": 5})

    summary = tracker.get_usage_summary()

    assert summary["requests"]["used"] == 3
    assert summary["requests"]["limit"] == ConversationLimits.MAX_REQUESTS
    assert summary["requests"]["remaining"] == ConversationLimits.MAX_REQUESTS - 3

    assert summary["tokens"]["used"] == 45000
    assert summary["tokens"]["limit"] == ConversationLimits.MAX_TOKENS
    assert summary["tokens"]["remaining"] == ConversationLimits.MAX_TOKENS - 45000

    assert summary["tool_calls"]["used"] == 5
    assert summary["tool_calls"]["limit"] == ConversationLimits.MAX_TOOL_CALLS
    assert summary["tool_calls"]["remaining"] == ConversationLimits.MAX_TOOL_CALLS - 5


def test_conversation_tracker_handles_missing_keys():
    """Test that tracker handles missing keys in usage_info."""
    tracker = ConversationTracker()

    # Only provide requests, not tokens or tool_calls
    tracker.add_usage({"requests": 2})

    assert tracker.total_requests == 2
    assert tracker.total_tokens == 0
    assert tracker.total_tool_calls == 0
