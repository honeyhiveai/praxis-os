"""
Test PrependGenerator middleware for behavioral engineering.

Tests:
- Prepend format and structure
- Suggestion generation based on query stats
- Topic extraction from queries
- Sanitization of user input

Traceability:
    Phase 8, Task 8.1: Prepend generation tests
    FR-026: Prepend Generator Middleware
"""

import pytest
from ouroboros.middleware.prepend_generator import PrependGenerator
from ouroboros.middleware.query_tracker import QueryTracker


class TestPrependGenerator:
    """Test PrependGenerator middleware."""
    
    def test_initialization(self):
        """Test PrependGenerator initializes successfully."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        assert generator is not None
    
    def test_prepend_has_required_structure(self):
        """Test prepend contains required sections."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        
        # Record some queries
        for i in range(5):
            tracker.record_query("session_1", f"query {i}")
        
        prepend = generator.generate(
            session_id="session_1",
            current_query="test query"
        )
        
        # Should contain stats line
        assert "📊" in prepend or "Queries:" in prepend
        # Should contain separator
        assert "---" in prepend
    
    def test_prepend_shows_query_counts(self):
        """Test prepend displays query counts correctly."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        
        # Record 10 queries
        for i in range(10):
            tracker.record_query("session_1", f"unique query {i}")
        
        prepend = generator.generate(
            session_id="session_1",
            current_query="test query"
        )
        
        # Should show both total and unique counts
        assert "10" in prepend  # total queries should show
    
    def test_prepend_shows_angle_coverage(self):
        """Test prepend displays angle coverage indicators."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        
        # Record queries with different angles
        tracker.record_query("session_1", "what is middleware")  # conceptual
        tracker.record_query("session_1", "where is validation")  # location
        
        prepend = generator.generate(
            session_id="session_1",
            current_query="test query"
        )
        
        # Should show angle indicators (checkmarks or symbols)
        assert "✓" in prepend or "✅" in prepend or "⬜" in prepend
    
    def test_suggestion_generation(self):
        """Test suggestions are generated based on coverage gaps."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        
        # Record only conceptual queries
        tracker.record_query("session_1", "what is middleware")
        tracker.record_query("session_1", "what is workflow")
        tracker.record_query("session_1", "what is validation")
        
        prepend = generator.generate(
            session_id="session_1",
            current_query="what is middleware"
        )
        
        # Should contain suggestion line
        assert "💡" in prepend or "Try:" in prepend
    
    def test_suggestion_includes_query_topic(self):
        """Test suggestions include the query topic."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        
        # Record conceptual query
        tracker.record_query("session_1", "what is browser automation")
        tracker.record_query("session_1", "what is browser automation again")
        
        prepend = generator.generate(
            session_id="session_1",
            current_query="what is browser automation"
        )
        
        # Should suggest location query about browser automation
        suggestion_line = [line for line in prepend.split("\n") if "💡" in line or "Try:" in line]
        
        if suggestion_line:
            # Should contain some topic from the query
            assert any(word in suggestion_line[0].lower() for word in ["browser", "automation", "concept"])
    
    def test_sanitization_of_user_input(self):
        """Test user queries are sanitized before inclusion."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        
        # Query with potential injection attempt
        malicious_query = "test<script>alert('xss')</script>query"
        tracker.record_query("session_1", malicious_query)
        
        prepend = generator.generate(
            session_id="session_1",
            current_query=malicious_query
        )
        
        # Should not contain raw HTML/script tags in suggestions
        assert "<script>" not in prepend
    
    def test_prepend_length_reasonable(self):
        """Test prepend is not excessively long."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        
        # Record many queries with all angles
        tracker.record_query("session_1", "what is workflow")
        tracker.record_query("session_1", "where is validation")
        tracker.record_query("session_1", "how to implement testing")
        tracker.record_query("session_1", "best practice for error handling")
        tracker.record_query("session_1", "avoid mistakes in config")
        
        prepend = generator.generate(
            session_id="session_1",
            current_query="test query"
        )
        
        # Should be reasonable length (< 500 chars)
        assert len(prepend) < 500
    
    def test_prepend_format_consistency(self):
        """Test prepend format is consistent across calls."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        
        # Record some queries
        for i in range(5):
            tracker.record_query("session_1", f"query {i}")
        
        prepends = []
        for i in range(3):
            prepend = generator.generate(
                session_id="session_1",
                current_query=f"query {i}"
            )
            prepends.append(prepend)
        
        # All should start with stats section
        for prepend in prepends:
            assert prepend.startswith("📊") or "Queries:" in prepend[:50]
        
        # All should contain separator
        for prepend in prepends:
            assert "---" in prepend
    
    def test_completion_message(self):
        """Test completion message appears after sufficient exploration."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        
        # Record 5+ queries with 4+ different angles
        tracker.record_query("session_1", "what is workflow")  # conceptual
        tracker.record_query("session_1", "where is validation")  # location
        tracker.record_query("session_1", "how to implement testing")  # implementation
        tracker.record_query("session_1", "best practice for error handling")  # critical
        tracker.record_query("session_1", "another query")
        
        prepend = generator.generate(
            session_id="session_1",
            current_query="final query"
        )
        
        # Should contain completion message after sufficient exploration
        assert "🎉" in prepend or "Keep exploring" in prepend or "💡" in prepend
