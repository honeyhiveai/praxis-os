"""
Unit tests for Query Tracker module.

Tests session tracking, uniqueness detection, angle coverage,
query history management, and performance requirements.

Traceability: implementation.md Section 4.2 (Unit Testing Strategy)
"""

import sys
import time
from datetime import datetime

import pytest

from mcp_server.core.query_classifier import QueryAngle
from mcp_server.core.query_tracker import (
    QueryStats,
    QueryTracker,
    get_tracker,
)


class TestQueryStats:
    """Test QueryStats dataclass."""

    def test_default_values(self) -> None:
        """Test QueryStats initializes with correct defaults."""
        stats = QueryStats()
        assert stats.total_queries == 0
        assert stats.unique_queries == 0
        assert stats.angles_covered == set()
        assert stats.query_history == []
        assert stats.last_query_time is None

    def test_all_five_fields_present(self) -> None:
        """Test QueryStats has all 5 required fields."""
        stats = QueryStats()
        assert hasattr(stats, "total_queries")
        assert hasattr(stats, "unique_queries")
        assert hasattr(stats, "angles_covered")
        assert hasattr(stats, "query_history")
        assert hasattr(stats, "last_query_time")


class TestQueryTracker:
    """Test QueryTracker class."""

    def test_initialization(self) -> None:
        """Test QueryTracker initializes with empty sessions."""
        tracker = QueryTracker()
        assert tracker._sessions == {}

    def test_record_query_increments_total(self) -> None:
        """Test record_query increments total_queries."""
        tracker = QueryTracker()

        tracker.record_query("session1", "What is X?")
        stats = tracker.get_stats("session1")
        assert stats.total_queries == 1

        tracker.record_query("session1", "Where is Y?")
        stats = tracker.get_stats("session1")
        assert stats.total_queries == 2

    def test_record_query_returns_angle(self) -> None:
        """Test record_query returns classified angle."""
        tracker = QueryTracker()

        angle = tracker.record_query("session1", "What is checkpoint?")
        assert angle == "definition"

        angle = tracker.record_query("session1", "Where is validation?")
        assert angle == "location"

    def test_uniqueness_detection_case_insensitive(self) -> None:
        """Test uniqueness detection is case-insensitive."""
        tracker = QueryTracker()

        tracker.record_query("session1", "What is X?")
        tracker.record_query("session1", "what is x?")  # Same query, different case
        tracker.record_query("session1", "WHAT IS X?")  # Same query, all caps

        stats = tracker.get_stats("session1")
        assert stats.total_queries == 3
        assert stats.unique_queries == 1  # Only counted once

    def test_uniqueness_detection_ignores_whitespace(self) -> None:
        """Test uniqueness detection strips whitespace."""
        tracker = QueryTracker()

        tracker.record_query("session1", "What is X?")
        tracker.record_query("session1", "  What is X?  ")  # Extra whitespace

        stats = tracker.get_stats("session1")
        assert stats.total_queries == 2
        assert stats.unique_queries == 1

    def test_query_history_limited_to_10(self) -> None:
        """Test query history maintains max 10 entries (FIFO)."""
        tracker = QueryTracker()

        # Record 15 queries
        for i in range(15):
            tracker.record_query("session1", f"Query {i}")

        stats = tracker.get_stats("session1")
        assert len(stats.query_history) == 10  # Limited to 10

        # Verify FIFO: first 5 should be evicted, last 10 should remain
        assert "Query 0" not in stats.query_history
        assert "Query 4" not in stats.query_history
        assert "Query 5" in stats.query_history
        assert "Query 14" in stats.query_history

    def test_angles_covered_tracking(self) -> None:
        """Test angles_covered set is updated correctly."""
        tracker = QueryTracker()

        tracker.record_query("session1", "What is X?")  # definition
        stats = tracker.get_stats("session1")
        assert "definition" in stats.angles_covered
        assert len(stats.angles_covered) == 1

        tracker.record_query("session1", "Where is Y?")  # location
        stats = tracker.get_stats("session1")
        assert "definition" in stats.angles_covered
        assert "location" in stats.angles_covered
        assert len(stats.angles_covered) == 2

    def test_last_query_time_updated(self) -> None:
        """Test last_query_time is updated on each query."""
        tracker = QueryTracker()

        before = datetime.now()
        tracker.record_query("session1", "What is X?")
        after = datetime.now()

        stats = tracker.get_stats("session1")
        assert stats.last_query_time is not None
        assert before <= stats.last_query_time <= after

    def test_get_stats_creates_empty_for_new_session(self) -> None:
        """Test get_stats returns empty QueryStats for new session."""
        tracker = QueryTracker()

        stats = tracker.get_stats("nonexistent_session")
        assert stats.total_queries == 0
        assert stats.unique_queries == 0
        assert stats.angles_covered == set()

    def test_get_uncovered_angles_returns_all_for_new_session(self) -> None:
        """Test get_uncovered_angles returns all 5 angles for new session."""
        tracker = QueryTracker()

        uncovered = tracker.get_uncovered_angles("new_session")
        assert len(uncovered) == 5
        assert uncovered == {
            "definition",
            "location",
            "practical",
            "best_practice",
            "error_prevention",
        }

    def test_get_uncovered_angles_excludes_covered(self) -> None:
        """Test get_uncovered_angles excludes angles already covered."""
        tracker = QueryTracker()

        tracker.record_query("session1", "What is X?")  # definition
        tracker.record_query("session1", "Where is Y?")  # location

        uncovered = tracker.get_uncovered_angles("session1")
        assert len(uncovered) == 3
        assert "definition" not in uncovered
        assert "location" not in uncovered
        assert "practical" in uncovered
        assert "best_practice" in uncovered
        assert "error_prevention" in uncovered

    def test_session_isolation(self) -> None:
        """Test sessions are isolated (no cross-contamination)."""
        tracker = QueryTracker()

        tracker.record_query("session1", "What is X?")
        tracker.record_query("session2", "Where is Y?")

        stats1 = tracker.get_stats("session1")
        stats2 = tracker.get_stats("session2")

        assert stats1.total_queries == 1
        assert stats2.total_queries == 1
        assert stats1.angles_covered != stats2.angles_covered

    def test_reset_session(self) -> None:
        """Test reset_session clears session data."""
        tracker = QueryTracker()

        tracker.record_query("session1", "What is X?")
        tracker.record_query("session1", "Where is Y?")

        tracker.reset_session("session1")

        stats = tracker.get_stats("session1")
        assert stats.total_queries == 0
        assert stats.angles_covered == set()

    def test_memory_per_session(self) -> None:
        """Test memory per session is ≤1.5KB."""
        tracker = QueryTracker()

        # Record 10 queries (max history)
        for i in range(10):
            tracker.record_query("session1", f"What is query number {i}?")

        stats = tracker.get_stats("session1")
        memory_bytes = sys.getsizeof(stats)

        # Convert to KB
        memory_kb = memory_bytes / 1024

        assert memory_kb <= 1.5, f"Memory {memory_kb:.2f}KB exceeds 1.5KB target"

    def test_record_query_performance(self) -> None:
        """Test record_query meets ≤2ms performance target."""
        tracker = QueryTracker()

        # Warm up
        for i in range(10):
            tracker.record_query("session1", f"Warmup {i}")

        # Measure 100 runs
        timings = []
        for i in range(100):
            query = f"Performance test query {i}"
            start = time.perf_counter()
            tracker.record_query("session1", query)
            end = time.perf_counter()
            timings.append((end - start) * 1000)  # Convert to ms

        avg_time_ms = sum(timings) / len(timings)
        assert (
            avg_time_ms <= 2.0
        ), f"Average record_query time {avg_time_ms:.2f}ms exceeds 2ms target"


class TestGetTracker:
    """Test global singleton get_tracker()."""

    def test_returns_singleton_instance(self) -> None:
        """Test get_tracker returns same instance (singleton pattern)."""
        tracker1 = get_tracker()
        tracker2 = get_tracker()

        assert tracker1 is tracker2

    def test_singleton_maintains_state(self) -> None:
        """Test singleton instance maintains state across calls."""
        tracker1 = get_tracker()
        tracker1.record_query("test_session", "What is X?")

        tracker2 = get_tracker()
        stats = tracker2.get_stats("test_session")

        assert stats.total_queries == 1

    def test_returns_query_tracker_instance(self) -> None:
        """Test get_tracker returns QueryTracker instance."""
        tracker = get_tracker()
        assert isinstance(tracker, QueryTracker)


# Integration test
def test_full_workflow_integration() -> None:
    """Test complete workflow: record queries, check stats, get uncovered angles."""
    tracker = QueryTracker()

    # Record queries of different angles
    angle1 = tracker.record_query("integration_test", "What is workflow?")
    assert angle1 == "definition"

    angle2 = tracker.record_query("integration_test", "Where is StateManager?")
    assert angle2 == "location"

    angle3 = tracker.record_query("integration_test", "How to create a workflow?")
    assert angle3 == "practical"

    # Check stats
    stats = tracker.get_stats("integration_test")
    assert stats.total_queries == 3
    assert stats.unique_queries == 3
    assert len(stats.angles_covered) == 3
    assert len(stats.query_history) == 3

    # Check uncovered angles
    uncovered = tracker.get_uncovered_angles("integration_test")
    assert len(uncovered) == 2
    assert "best_practice" in uncovered
    assert "error_prevention" in uncovered


def test_module_exports() -> None:
    """Test module exports expected symbols."""
    from mcp_server.core import query_tracker

    assert hasattr(query_tracker, "QueryStats")
    assert hasattr(query_tracker, "QueryTracker")
    assert hasattr(query_tracker, "get_tracker")
