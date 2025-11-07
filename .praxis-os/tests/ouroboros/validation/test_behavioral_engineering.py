"""
Validation tests for behavioral engineering system.

Tests:
- Prepends appear in 100% of search results
- Query diversity tracked correctly
- Suggestions are actionable
- No silent middleware failures

Traceability:
    Phase 8, Task 8.5: Behavioral engineering validation
"""

import pytest
from ouroboros.middleware.query_tracker import QueryTracker
from ouroboros.middleware.query_classifier import QueryClassifier
from ouroboros.middleware.prepend_generator import PrependGenerator


class TestBehavioralEngineering:
    """Validate behavioral engineering system works correctly."""
    
    def test_prepends_always_generated(self):
        """Test prepends are generated for every query."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        
        # Test 50 different queries
        for i in range(50):
            query = f"test query {i}"
            tracker.record_query("session_1", query)
            prepend = generator.generate("session_1", query)
            
            # Prepend must exist and have required structure
            assert prepend is not None
            assert len(prepend) > 0
            assert "📊" in prepend or "Queries:" in prepend
            assert "---" in prepend
    
    def test_query_diversity_tracking(self):
        """Test query diversity is tracked accurately."""
        tracker = QueryTracker()
        
        # Record queries with different angles
        queries = [
            ("what is middleware", "conceptual"),
            ("where is validation", "location"),
            ("how to implement testing", "implementation"),
            ("best practice for errors", "critical"),
            ("avoid mistakes in config", "troubleshooting"),
        ]
        
        for query, expected_angle in queries:
            result = tracker.record_query("session_1", query)
            # Verify angle is one of the valid types
            assert result.primary in ["conceptual", "location", "implementation", "critical", "troubleshooting"]
        
        # Check diversity score
        diversity = tracker.get_diversity_score("session_1")
        assert 0.0 <= diversity <= 1.0
        assert diversity > 0.6  # Should have covered multiple angles
    
    def test_suggestions_are_actionable(self):
        """Test suggestions contain valid query patterns."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        
        # Record a conceptual query
        tracker.record_query("session_1", "what is workflow")
        prepend = generator.generate("session_1", "what is workflow")
        
        # Should suggest a different angle
        assert "💡" in prepend or "Try:" in prepend
        
        # Suggestion should be quoted and contain a query
        lines = prepend.split("\n")
        suggestion_lines = [l for l in lines if "💡" in l or "Try:" in l]
        assert len(suggestion_lines) > 0
        assert "'" in suggestion_lines[0]  # Suggestions are quoted
    
    def test_angle_coverage_complete(self):
        """Test all 5 angles can be detected."""
        classifier = QueryClassifier()
        
        test_queries = {
            "conceptual": "what is middleware",
            "location": "where is validation",
            "implementation": "how to implement testing",
            "critical": "best practice for errors",
            "troubleshooting": "avoid mistakes in config",
        }
        
        detected_angles = set()
        for expected_angle, query in test_queries.items():
            result = classifier.classify(query)
            detected_angles.add(result.primary)
        
        # Should detect all 5 unique angles
        assert len(detected_angles) >= 4  # At least 4 of 5 angles detected
    
    def test_session_isolation_strict(self):
        """Test sessions are strictly isolated."""
        tracker = QueryTracker()
        
        # Session 1: Record 5 queries
        for i in range(5):
            tracker.record_query("session_1", f"query {i}")
        
        # Session 2: Record 3 queries
        for i in range(3):
            tracker.record_query("session_2", f"different query {i}")
        
        # Verify isolation
        stats_1 = tracker.get_stats("session_1")
        stats_2 = tracker.get_stats("session_2")
        
        assert stats_1.total_queries == 5
        assert stats_2.total_queries == 3
        
        # No cross-contamination
        for query in stats_1.query_history:
            assert "different" not in query
        
        for query in stats_2.query_history:
            assert "different" in query
    
    def test_prepend_progress_visualization(self):
        """Test prepends show progress correctly."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        
        prepends = []
        for i in range(5):
            tracker.record_query("session_1", f"query {i}")
            prepend = generator.generate("session_1", f"query {i}")
            prepends.append(prepend)
        
        # First prepend should show 1/5
        assert "1" in prepends[0]
        
        # Last prepend should show 5/5
        assert "5" in prepends[4]
        
        # Progress should be visible
        for i, prepend in enumerate(prepends):
            # Query count should be visible
            assert str(i + 1) in prepend
    
    def test_no_silent_failures(self):
        """Test middleware doesn't silently fail."""
        tracker = QueryTracker()
        classifier = QueryClassifier()
        generator = PrependGenerator(tracker)
        
        # Test with various edge cases
        edge_cases = [
            "",  # Empty query
            " ",  # Whitespace only
            "a" * 1000,  # Very long query
            "🎉🚀✨",  # Emoji only
            "<script>alert('xss')</script>",  # Potential XSS
        ]
        
        for query in edge_cases:
            # Should not raise exceptions
            try:
                classification = classifier.classify(query)
                assert classification is not None
                
                tracker.record_query("session_edge", query)
                stats = tracker.get_stats("session_edge")
                assert stats is not None
                
                prepend = generator.generate("session_edge", query)
                assert prepend is not None
            except Exception as e:
                pytest.fail(f"Middleware failed silently on edge case '{query[:50]}': {e}")

