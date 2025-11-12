"""
Unit tests for ouroboros.middleware.query_tracker.

Tests query tracking including:
    - Recording queries with statistics
    - Unique query detection
    - Angle coverage tracking
    - Session isolation
    - Thread safety
"""

import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from ouroboros.middleware.query_tracker import QueryStats, QueryTracker


class TestQueryStats:
    """Test QueryStats dataclass."""

    def test_querystats_creation(self):
        """QueryStats should initialize with zero values."""
        stats = QueryStats()

        assert stats.total_queries == 0
        assert stats.unique_queries == 0
        assert len(stats.angles_covered) == 0
        assert len(stats.query_history) == 0
        assert stats.last_query_time is None

    def test_querystats_with_values(self):
        """QueryStats should accept custom values."""
        stats = QueryStats(
            total_queries=5,
            unique_queries=3,
            angles_covered={"conceptual", "location"},
        )

        assert stats.total_queries == 5
        assert stats.unique_queries == 3
        assert len(stats.angles_covered) == 2


class TestQueryTracker:
    """Test QueryTracker class."""

    def test_tracker_initialization(self):
        """QueryTracker should initialize with empty sessions."""
        tracker = QueryTracker()
        assert tracker is not None

    def test_record_query_first_time(self):
        """First query should create new session."""
        tracker = QueryTracker()

        result = tracker.record_query("session1", "What is X?")

        assert result.primary == "conceptual"
        stats = tracker.get_stats("session1")
        assert stats.total_queries == 1
        assert stats.unique_queries == 1

    def test_record_query_increments_total(self):
        """Each query should increment total count."""
        tracker = QueryTracker()

        tracker.record_query("s1", "What is X?")
        tracker.record_query("s1", "Where is Y?")
        tracker.record_query("s1", "How to use Z?")

        stats = tracker.get_stats("s1")
        assert stats.total_queries == 3

    def test_detect_duplicate_query(self):
        """Duplicate queries should not increment unique count."""
        tracker = QueryTracker()

        tracker.record_query("s1", "What is X?")
        tracker.record_query("s1", "what is x?")  # Same, different case
        tracker.record_query("s1", "  What is X?  ")  # Same, extra whitespace

        stats = tracker.get_stats("s1")
        assert stats.total_queries == 3
        assert stats.unique_queries == 1

    def test_unique_queries_detected(self):
        """Different queries should increment unique count."""
        tracker = QueryTracker()

        tracker.record_query("s1", "What is X?")
        tracker.record_query("s1", "Where is Y?")
        tracker.record_query("s1", "How to use Z?")

        stats = tracker.get_stats("s1")
        assert stats.total_queries == 3
        assert stats.unique_queries == 3

    def test_angle_coverage_tracking(self):
        """Tracker should track covered angles."""
        tracker = QueryTracker()

        tracker.record_query("s1", "What is X?")  # conceptual
        tracker.record_query("s1", "Where is Y?")  # location

        stats = tracker.get_stats("s1")
        assert "conceptual" in stats.angles_covered
        assert "location" in stats.angles_covered
        assert len(stats.angles_covered) == 2

    def test_query_history_bounded(self):
        """Query history should be limited to 10 items."""
        tracker = QueryTracker()

        # Record 15 queries
        for i in range(15):
            tracker.record_query("s1", f"Query {i}")

        stats = tracker.get_stats("s1")
        assert len(stats.query_history) == 10
        # Should keep most recent (5-14)
        assert "Query 14" in stats.query_history
        assert "Query 5" in stats.query_history
        assert "Query 0" not in stats.query_history

    def test_last_query_time_updated(self):
        """Last query time should update on each query."""
        tracker = QueryTracker()

        tracker.record_query("s1", "First query")
        stats1 = tracker.get_stats("s1")
        time1 = stats1.last_query_time

        time.sleep(0.01)  # Small delay

        tracker.record_query("s1", "Second query")
        stats2 = tracker.get_stats("s1")
        time2 = stats2.last_query_time

        assert time1 is not None
        assert time2 is not None
        assert time2 > time1

    def test_session_isolation(self):
        """Different sessions should have isolated stats."""
        tracker = QueryTracker()

        tracker.record_query("s1", "Query 1")
        tracker.record_query("s2", "Query 2")
        tracker.record_query("s1", "Query 3")

        stats1 = tracker.get_stats("s1")
        stats2 = tracker.get_stats("s2")

        assert stats1.total_queries == 2
        assert stats2.total_queries == 1

    def test_get_stats_nonexistent_session(self):
        """get_stats() should return empty stats for new session."""
        tracker = QueryTracker()

        stats = tracker.get_stats("nonexistent")

        assert stats.total_queries == 0
        assert stats.unique_queries == 0

    def test_get_uncovered_angles(self):
        """get_uncovered_angles() should return uncovered angles."""
        tracker = QueryTracker()

        tracker.record_query("s1", "What is X?")  # conceptual

        uncovered = tracker.get_uncovered_angles("s1")

        assert "conceptual" not in uncovered
        assert "location" in uncovered
        assert "implementation" in uncovered
        assert len(uncovered) == 4

    def test_get_uncovered_angles_all_covered(self):
        """get_uncovered_angles() should return empty for all covered."""
        tracker = QueryTracker()

        # Cover all angles
        tracker.record_query("s1", "What is X?")  # conceptual
        tracker.record_query("s1", "Where is Y?")  # location
        tracker.record_query("s1", "How to use Z?")  # implementation
        tracker.record_query("s1", "Best practice for A")  # critical
        tracker.record_query("s1", "Fix error in B")  # troubleshooting

        uncovered = tracker.get_uncovered_angles("s1")
        assert len(uncovered) == 0

    def test_get_diversity_score_zero(self):
        """Diversity score should be 0.0 for no queries."""
        tracker = QueryTracker()

        score = tracker.get_diversity_score("s1")
        assert score == 0.0

    def test_get_diversity_score_partial(self):
        """Diversity score should increase with angle coverage."""
        tracker = QueryTracker()

        tracker.record_query("s1", "What is X?")  # 1/5
        assert tracker.get_diversity_score("s1") == 0.2

        tracker.record_query("s1", "Where is Y?")  # 2/5
        assert tracker.get_diversity_score("s1") == 0.4

    def test_get_diversity_score_complete(self):
        """Diversity score should be 1.0 for all angles."""
        tracker = QueryTracker()

        # Cover all 5 angles
        tracker.record_query("s1", "What is X?")
        tracker.record_query("s1", "Where is Y?")
        tracker.record_query("s1", "How to use Z?")
        tracker.record_query("s1", "Best practice for A")
        tracker.record_query("s1", "Fix error in B")

        assert tracker.get_diversity_score("s1") == 1.0

    def test_reset_session(self):
        """reset_session() should clear all stats."""
        tracker = QueryTracker()

        tracker.record_query("s1", "Query 1")
        tracker.record_query("s1", "Query 2")

        tracker.reset_session("s1")

        stats = tracker.get_stats("s1")
        assert stats.total_queries == 0

    def test_singleton_pattern(self):
        """get_singleton() should return same instance."""
        tracker1 = QueryTracker.get_singleton()
        tracker2 = QueryTracker.get_singleton()

        assert tracker1 is tracker2

    def test_secondary_angles_tracked(self):
        """Secondary angles should be tracked in coverage."""
        tracker = QueryTracker()

        # Query with multiple angles
        result = tracker.record_query("s1", "Where is X and how to use it?")

        stats = tracker.get_stats("s1")
        # Both primary and secondary should be tracked
        assert result.primary in stats.angles_covered
        for angle in result.secondary:
            assert angle in stats.angles_covered


class TestThreadSafety:
    """Test thread safety for concurrent access."""

    def test_concurrent_queries_same_session(self):
        """Concurrent queries to same session should not corrupt data."""
        tracker = QueryTracker()

        def record_queries():
            for i in range(10):
                tracker.record_query("s1", f"Query {i}")

        # Run 5 threads concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(record_queries) for _ in range(5)]
            for future in futures:
                future.result()

        stats = tracker.get_stats("s1")
        # Should have all 50 queries (5 threads × 10 queries)
        assert stats.total_queries == 50

    def test_concurrent_sessions(self):
        """Concurrent access to different sessions should work."""
        tracker = QueryTracker()

        def record_to_session(session_id: str):
            for i in range(10):
                tracker.record_query(session_id, f"Query {i}")

        # Run 5 threads with different sessions
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(record_to_session, f"s{i}") for i in range(5)]
            for future in futures:
                future.result()

        # Each session should have 10 queries
        for i in range(5):
            stats = tracker.get_stats(f"s{i}")
            assert stats.total_queries == 10
