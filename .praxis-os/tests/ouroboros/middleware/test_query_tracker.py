"""
Test QueryTracker middleware for behavioral engineering.

Tests:
- Query logging and aggregation
- Session isolation (queries tracked per session)
- Thread safety (concurrent access)
- Statistics calculation (unique queries, angle coverage)

Traceability:
    Phase 8, Task 8.1: Query tracking tests
    FR-024: Query Tracking Middleware
"""

import pytest
from ouroboros.middleware.query_tracker import QueryTracker


class TestQueryTracker:
    """Test QueryTracker middleware."""
    
    def test_initialization(self):
        """Test QueryTracker initializes with empty state."""
        tracker = QueryTracker()
        
        stats = tracker.get_stats("session_1")
        
        assert stats.total_queries == 0
        assert stats.unique_queries == 0
        assert len(stats.query_history) == 0
    
    def test_record_query_increments_count(self):
        """Test recording query increments counters."""
        tracker = QueryTracker()
        
        result = tracker.record_query("session_1", "test query")
        stats = tracker.get_stats("session_1")
        
        assert stats.total_queries == 1
        assert stats.unique_queries == 1
        assert len(stats.query_history) == 1
        assert result.primary in ["conceptual", "location", "implementation", "critical", "troubleshooting"]
    
    def test_duplicate_queries_tracked_correctly(self):
        """Test duplicate queries increase total but not unique count."""
        tracker = QueryTracker()
        
        tracker.record_query("session_1", "same query")
        tracker.record_query("session_1", "same query")
        tracker.record_query("session_1", "different query")
        
        stats = tracker.get_stats("session_1")
        
        assert stats.total_queries == 3
        assert stats.unique_queries == 2
    
    def test_session_isolation(self):
        """Test queries are isolated per session."""
        tracker = QueryTracker()
        
        tracker.record_query("session_1", "query A")
        tracker.record_query("session_2", "query B")
        
        stats_1 = tracker.get_stats("session_1")
        stats_2 = tracker.get_stats("session_2")
        
        assert stats_1.total_queries == 1
        assert stats_2.total_queries == 1
        assert stats_1.query_history[0] == "query A"
        assert stats_2.query_history[0] == "query B"
    
    def test_angle_coverage_tracking(self):
        """Test angle coverage is tracked correctly."""
        tracker = QueryTracker()
        
        # Use queries that trigger different angles
        tracker.record_query("session_1", "what is workflow")  # conceptual
        tracker.record_query("session_1", "where is validation")  # location
        tracker.record_query("session_1", "how to implement testing")  # implementation
        
        stats = tracker.get_stats("session_1")
        
        # Should have at least 3 unique angles
        assert "conceptual" in stats.angles_covered
        assert "location" in stats.angles_covered
        assert "implementation" in stats.angles_covered
    
    def test_query_history_preserves_order(self):
        """Test query history maintains insertion order."""
        tracker = QueryTracker()
        
        queries = ["first", "second", "third"]
        for q in queries:
            tracker.record_query("session_1", q)
        
        stats = tracker.get_stats("session_1")
        history = stats.query_history
        
        assert len(history) == 3
        assert history[0] == "first"
        assert history[1] == "second"
        assert history[2] == "third"
    
    def test_thread_safety(self):
        """Test concurrent query logging is thread-safe."""
        import threading
        
        tracker = QueryTracker()
        
        def record_queries(session_id, count):
            for i in range(count):
                tracker.record_query(session_id, f"query_{i}")
        
        # Launch multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=record_queries, args=(f"session_{i}", 10))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Verify each session has 10 queries
        for i in range(5):
            stats = tracker.get_stats(f"session_{i}")
            assert stats.total_queries == 10
            assert stats.unique_queries == 10
    
    def test_reset_session(self):
        """Test resetting a session clears its data."""
        tracker = QueryTracker()
        
        tracker.record_query("session_1", "query 1")
        tracker.record_query("session_1", "query 2")
        
        # Reset session
        tracker.reset_session("session_1")
        stats = tracker.get_stats("session_1")
        assert stats.total_queries == 0

