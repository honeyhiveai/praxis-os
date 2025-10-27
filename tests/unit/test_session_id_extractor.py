"""
Unit tests for Session ID Extractor module.

Tests session extraction, dynamic countdown timer, hashing,
and performance requirements.

Traceability: implementation.md Section 4.2 (Unit Testing Strategy)
"""

import time
from typing import Set

import pytest

from mcp_server.core.session_id_extractor import (
    SessionState,
    cleanup_stale_sessions,
    extract_session_id_from_context,
    get_session_stats,
    hash_session_id,
)


class TestSessionState:
    """Test SessionState dataclass."""

    def test_get_session_key_format(self) -> None:
        """Test session key format is correct."""
        state = SessionState("client_123", 0, time.time(), 1)
        assert state.get_session_key() == "client_123_s0"

        state = SessionState("client_abc", 5, time.time(), 1)
        assert state.get_session_key() == "client_abc_s5"

    def test_get_timeout_seconds_starts_at_20(self) -> None:
        """Test initial timeout is 20 seconds."""
        state = SessionState("c", 0, time.time(), 1)  # First query
        assert state.get_timeout_seconds() == 20.0

    def test_get_timeout_seconds_decreases(self) -> None:
        """Test timeout decreases by 1s per query."""
        state = SessionState("c", 0, time.time(), 1)  # Query 1
        assert state.get_timeout_seconds() == 20.0

        state.queries_in_session = 2  # Query 2
        assert state.get_timeout_seconds() == 19.0

        state.queries_in_session = 5  # Query 5
        assert state.get_timeout_seconds() == 16.0

    def test_get_timeout_seconds_floor_at_5(self) -> None:
        """Test timeout has 5s floor."""
        state = SessionState("c", 0, time.time(), 20)  # Many queries
        assert state.get_timeout_seconds() == 5.0

        state.queries_in_session = 100  # Very many queries
        assert state.get_timeout_seconds() == 5.0

    def test_is_expired_returns_false_within_timeout(self) -> None:
        """Test session not expired within timeout window."""
        last_query_time = 100.0
        state = SessionState("c", 0, last_query_time, 1)  # 20s timeout

        # 10s elapsed (within 20s timeout)
        assert state.is_expired(110.0) is False

        # 19s elapsed (within 20s timeout)
        assert state.is_expired(119.0) is False

    def test_is_expired_returns_true_after_timeout(self) -> None:
        """Test session expired after timeout window."""
        last_query_time = 100.0
        state = SessionState("c", 0, last_query_time, 1)  # 20s timeout

        # 21s elapsed (exceeds 20s timeout)
        assert state.is_expired(121.0) is True

        # 30s elapsed (exceeds 20s timeout)
        assert state.is_expired(130.0) is True


class TestExtractSessionIdFromContext:
    """Test session ID extraction with dynamic countdown timer."""

    def test_first_query_creates_session_0(self) -> None:
        """Test first query from client creates session_0."""
        # Clear any existing state
        from mcp_server.core.session_id_extractor import _session_states

        _session_states.clear()

        session_id = extract_session_id_from_context(None)

        # Should be session_0 for new client
        assert session_id.endswith("_s0")

    def test_rapid_queries_same_session(self) -> None:
        """Test queries within timeout stay in same session."""
        from mcp_server.core.session_id_extractor import _session_states

        _session_states.clear()

        # First query
        session_id_1 = extract_session_id_from_context(None)

        # Immediate second query (within timeout)
        session_id_2 = extract_session_id_from_context(None)

        # Should be same session
        assert session_id_1 == session_id_2
        assert session_id_1.endswith("_s0")

    def test_timeout_creates_new_session(self) -> None:
        """Test query after timeout creates new session."""
        from mcp_server.core.session_id_extractor import _session_states

        _session_states.clear()

        # First query
        session_id_1 = extract_session_id_from_context(None)
        assert session_id_1.endswith("_s0")

        # Manually expire session by manipulating last_query_time
        # Set it to 25 seconds ago (exceeds 20s initial timeout)
        client_id = list(_session_states.keys())[0]
        state = _session_states[client_id]
        state.last_query_time = time.time() - 25.0

        # Next query should create new session
        session_id_2 = extract_session_id_from_context(None)
        assert session_id_2.endswith("_s1")

    def test_countdown_timer_descends(self) -> None:
        """Test countdown timer decreases with each query."""
        from mcp_server.core.session_id_extractor import _session_states

        _session_states.clear()

        # Record 5 queries
        for _ in range(5):
            extract_session_id_from_context(None)

        # Check timeout has decreased
        client_id = list(_session_states.keys())[0]
        state = _session_states[client_id]

        # After 5 queries, timeout should be 16s (20 - 4)
        assert state.get_timeout_seconds() == 16.0

    def test_session_isolation_with_countdown(self) -> None:
        """Test multiple clients have independent countdown timers."""
        from mcp_server.core.session_id_extractor import _session_states

        _session_states.clear()

        # Simulate two different clients by manipulating state directly
        client_1_state = SessionState("client_1", 0, time.time(), 1)
        client_2_state = SessionState("client_2", 0, time.time(), 1)

        _session_states["client_1"] = client_1_state
        _session_states["client_2"] = client_2_state

        # Advance client_1 to many queries
        client_1_state.queries_in_session = 10

        # Client_2 should still have high timeout
        assert client_2_state.get_timeout_seconds() == 20.0

        # Client_1 should have lower timeout
        assert client_1_state.get_timeout_seconds() == 11.0

    def test_always_returns_valid_session_id(self) -> None:
        """Test extraction never returns None or empty string."""
        from mcp_server.core.session_id_extractor import _session_states

        _session_states.clear()

        for _ in range(10):
            session_id = extract_session_id_from_context(None)
            assert session_id is not None
            assert isinstance(session_id, str)
            assert len(session_id) > 0
            assert "_s" in session_id

    def test_extraction_performance(self) -> None:
        """Test extraction meets ≤0.1ms (100μs) performance target."""
        from mcp_server.core.session_id_extractor import _session_states

        _session_states.clear()

        # Warm up
        for _ in range(10):
            extract_session_id_from_context(None)

        # Measure 100 runs
        timings = []
        for _ in range(100):
            start = time.perf_counter()
            extract_session_id_from_context(None)
            end = time.perf_counter()
            timings.append((end - start) * 1000)  # Convert to ms

        avg_time_ms = sum(timings) / len(timings)
        assert (
            avg_time_ms <= 0.1
        ), f"Average extraction time {avg_time_ms:.4f}ms exceeds 0.1ms target"


class TestHashSessionId:
    """Test session ID hashing."""

    def test_hash_is_deterministic(self) -> None:
        """Test hashing produces same output for same input."""
        session_id = "client_123_s0"

        hash_1 = hash_session_id(session_id)
        hash_2 = hash_session_id(session_id)

        assert hash_1 == hash_2

    def test_hash_length_is_16_characters(self) -> None:
        """Test hashed IDs are exactly 16 characters."""
        test_ids = [
            "client_123_s0",
            "client_abc_s5",
            "pid_12345_s10",
            "default_s0",
        ]

        for session_id in test_ids:
            hashed = hash_session_id(session_id)
            assert len(hashed) == 16

    def test_hash_is_hex_string(self) -> None:
        """Test hash uses only hex characters."""
        session_id = "client_123_s0"
        hashed = hash_session_id(session_id)

        # Should only contain hex digits (0-9, a-f)
        assert all(c in "0123456789abcdef" for c in hashed)

    def test_hash_collision_resistance(self) -> None:
        """Test 1,000 different inputs produce 1,000 unique hashes."""
        hashes: Set[str] = set()

        for i in range(1000):
            session_id = f"client_{i}_s{i % 10}"
            hashed = hash_session_id(session_id)
            hashes.add(hashed)

        # All hashes should be unique
        assert len(hashes) == 1000

    def test_hash_performance(self) -> None:
        """Test hashing meets ≤1ms performance target."""
        session_id = "client_123_s0"

        # Warm up
        for _ in range(10):
            hash_session_id(session_id)

        # Measure 100 runs
        timings = []
        for i in range(100):
            start = time.perf_counter()
            hash_session_id(f"client_{i}_s0")
            end = time.perf_counter()
            timings.append((end - start) * 1000)  # Convert to ms

        avg_time_ms = sum(timings) / len(timings)
        assert (
            avg_time_ms <= 1.0
        ), f"Average hash time {avg_time_ms:.4f}ms exceeds 1ms target"


class TestCleanupStaleSessions:
    """Test stale session cleanup."""

    def test_cleanup_removes_old_sessions(self) -> None:
        """Test cleanup removes sessions older than max_age."""
        from mcp_server.core.session_id_extractor import _session_states

        _session_states.clear()

        # Create session with old timestamp
        old_time = time.time() - 400  # 400 seconds ago
        _session_states["old_client"] = SessionState("old_client", 0, old_time, 1)

        # Create session with recent timestamp
        recent_time = time.time()
        _session_states["recent_client"] = SessionState(
            "recent_client", 0, recent_time, 1
        )

        # Clean up sessions older than 300 seconds
        removed_count = cleanup_stale_sessions(300)

        assert removed_count == 1
        assert "old_client" not in _session_states
        assert "recent_client" in _session_states

    def test_cleanup_returns_correct_count(self) -> None:
        """Test cleanup returns number of sessions removed."""
        from mcp_server.core.session_id_extractor import _session_states

        _session_states.clear()

        # Create 3 old sessions
        old_time = time.time() - 400
        for i in range(3):
            _session_states[f"old_client_{i}"] = SessionState(
                f"old_client_{i}", 0, old_time, 1
            )

        removed_count = cleanup_stale_sessions(300)
        assert removed_count == 3


class TestGetSessionStats:
    """Test session statistics retrieval."""

    def test_get_session_stats_returns_dict(self) -> None:
        """Test get_session_stats returns dictionary."""
        from mcp_server.core.session_id_extractor import _session_states

        _session_states.clear()

        extract_session_id_from_context(None)

        stats = get_session_stats()
        assert isinstance(stats, dict)

    def test_stats_include_required_fields(self) -> None:
        """Test stats include session_number, queries, timeout, age."""
        from mcp_server.core.session_id_extractor import _session_states

        _session_states.clear()

        extract_session_id_from_context(None)

        stats = get_session_stats()
        client_id = list(stats.keys())[0]
        client_stats = stats[client_id]

        assert "session_number" in client_stats
        assert "queries_in_session" in client_stats
        assert "timeout_seconds" in client_stats
        assert "age_seconds" in client_stats


# Integration test
def test_full_session_workflow() -> None:
    """Test complete session workflow with dynamic countdown."""
    from mcp_server.core.session_id_extractor import _session_states

    _session_states.clear()

    # First query - should create session_0
    session_1 = extract_session_id_from_context(None)
    assert session_1.endswith("_s0")

    # Get stats
    stats = get_session_stats()
    assert len(stats) == 1

    # Hash the session ID
    hashed = hash_session_id(session_1)
    assert len(hashed) == 16

    # Immediate second query - should stay in session_0
    session_2 = extract_session_id_from_context(None)
    assert session_1 == session_2

    # Manually expire session
    client_id = list(_session_states.keys())[0]
    _session_states[client_id].last_query_time = time.time() - 25.0

    # Next query - should create session_1
    session_3 = extract_session_id_from_context(None)
    assert session_3.endswith("_s1")
    assert session_3 != session_1


def test_module_exports() -> None:
    """Test module exports expected symbols."""
    from mcp_server.core import session_id_extractor

    assert hasattr(session_id_extractor, "SessionState")
    assert hasattr(session_id_extractor, "extract_session_id_from_context")
    assert hasattr(session_id_extractor, "hash_session_id")
    assert hasattr(session_id_extractor, "cleanup_stale_sessions")
    assert hasattr(session_id_extractor, "get_session_stats")
