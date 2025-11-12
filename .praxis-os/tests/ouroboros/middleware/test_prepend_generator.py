"""
Unit tests for ouroboros.middleware.prepend_generator.

Tests prepend generation including:
    - Progress line formatting
    - Angle indicators
    - Suggestion generation
    - Completion messages
    - Topic extraction
"""

import pytest
from ouroboros.middleware.prepend_generator import PrependGenerator
from ouroboros.middleware.query_tracker import QueryTracker


class TestPrependGenerator:
    """Test PrependGenerator class."""

    def test_generator_initialization(self):
        """PrependGenerator should initialize with tracker."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        assert generator is not None
        assert generator.tracker is tracker

    def test_generate_first_query(self):
        """First query should show 1/5 progress."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        tracker.record_query("s1", "What is X?")
        prepend = generator.generate("s1", "What is X?")

        assert "Queries: 1/5" in prepend
        assert "Unique: 1" in prepend
        assert "📖✓" in prepend  # Conceptual covered
        assert "💡 Try:" in prepend  # Should have suggestion

    def test_generate_multiple_queries(self):
        """Multiple queries should update progress."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        tracker.record_query("s1", "What is X?")
        tracker.record_query("s1", "Where is Y?")
        tracker.record_query("s1", "How to use Z?")

        prepend = generator.generate("s1", "How to use Z?")

        assert "Queries: 3/5" in prepend
        assert "Unique: 3" in prepend

    def test_angle_indicators_one_angle(self):
        """Angle indicators should show one covered angle."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        tracker.record_query("s1", "What is X?")  # conceptual
        prepend = generator.generate("s1", "What is X?")

        assert "📖✓" in prepend  # Conceptual covered
        assert "📍⬜" in prepend  # Location not covered
        assert "🔧⬜" in prepend  # Implementation not covered
        assert "⭐⬜" in prepend  # Critical not covered
        assert "⚠️⬜" in prepend  # Troubleshooting not covered

    def test_angle_indicators_multiple_angles(self):
        """Angle indicators should show multiple covered angles."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        tracker.record_query("s1", "What is X?")  # conceptual
        tracker.record_query("s1", "Where is Y?")  # location
        tracker.record_query("s1", "How to use Z?")  # implementation

        prepend = generator.generate("s1", "How to use Z?")

        assert "📖✓" in prepend
        assert "📍✓" in prepend
        assert "🔧✓" in prepend
        assert "⭐⬜" in prepend
        assert "⚠️⬜" in prepend

    def test_completion_message(self):
        """Completion message should appear for ≥5 queries + ≥4 angles."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        # Cover 4 angles with 5 queries
        tracker.record_query("s1", "What is X?")
        tracker.record_query("s1", "Where is Y?")
        tracker.record_query("s1", "How to use Z?")
        tracker.record_query("s1", "Best practice for A")
        tracker.record_query("s1", "Another query")

        prepend = generator.generate("s1", "Another query")

        assert "🎉 Keep exploring!" in prepend
        assert "Query liberally" in prepend

    def test_suggestion_before_completion(self):
        """Suggestions should appear before completion."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        tracker.record_query("s1", "What is X?")
        prepend = generator.generate("s1", "What is X?")

        assert "💡 Try:" in prepend
        assert "🎉" not in prepend  # No completion message yet

    def test_extract_topic_simple(self):
        """_extract_topic() should extract simple topics."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        topic = generator._extract_topic("What is checkpoint validation?")
        assert "checkpoint validation" in topic

    def test_extract_topic_removes_common_words(self):
        """_extract_topic() should remove common words."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        topic = generator._extract_topic("How to use the workflow?")
        # Should remove: how, to, use, the
        assert "workflow" in topic.lower()

    def test_extract_topic_empty_query(self):
        """_extract_topic() should handle empty queries."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        topic = generator._extract_topic("")
        assert topic == "[concept]"

    def test_extract_topic_sanitizes_html(self):
        """_extract_topic() should remove HTML tags (XSS prevention)."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        topic = generator._extract_topic("What is <script>alert('xss')</script>?")
        assert "<script>" not in topic
        assert "alert" in topic  # Content remains after tag removal

    def test_generate_suggestion_uncovered_angle(self):
        """_generate_suggestion() should suggest uncovered angle."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        # Cover only conceptual
        tracker.record_query("s1", "What is X?")

        uncovered = tracker.get_uncovered_angles("s1")
        # _generate_angle_suggestion now requires recent_suggestions parameter
        suggestion = generator._generate_angle_suggestion(uncovered, "workflow", recent_suggestions=[])

        # Should suggest one of the uncovered angles
        assert "'" in suggestion  # Suggestions are quoted
        assert len(suggestion) > 0

    def test_generate_suggestion_all_covered(self):
        """_generate_suggestion() should handle all angles covered."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        # _generate_angle_suggestion (renamed from _generate_suggestion)
        suggestion = generator._generate_angle_suggestion(set(), "workflow", recent_suggestions=[])

        assert "Explore more" in suggestion

    def test_prepend_format(self):
        """Prepend should have consistent format."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        tracker.record_query("s1", "What is X?")
        prepend = generator.generate("s1", "What is X?")

        # Should have:
        # - Progress line
        # - Feedback line
        # - Empty line
        # - Separator
        # - Empty line
        lines = prepend.split("\n")
        assert len(lines) >= 4
        assert "---" in prepend  # Separator present

    def test_prepend_token_budget(self):
        """Prepend should stay within token budget (~120 tokens max)."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        tracker.record_query("s1", "What is X?")
        prepend = generator.generate("s1", "What is X?")

        # Rough token estimate: ~1 token per 4 characters
        estimated_tokens = len(prepend) / 4
        assert estimated_tokens < 150  # Conservative upper bound

    def test_duplicate_queries_unique_count(self):
        """Prepend should reflect correct unique count."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        tracker.record_query("s1", "What is X?")
        tracker.record_query("s1", "what is x?")  # Duplicate
        tracker.record_query("s1", "What is X?")  # Duplicate

        prepend = generator.generate("s1", "What is X?")

        assert "Queries: 3/5" in prepend  # Total
        assert "Unique: 1" in prepend  # Only 1 unique

    def test_session_isolation_in_prepends(self):
        """Different sessions should have isolated prepends."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        tracker.record_query("s1", "Query 1")
        tracker.record_query("s2", "Query A")
        tracker.record_query("s1", "Query 2")

        prepend1 = generator.generate("s1", "Query 2")
        prepend2 = generator.generate("s2", "Query A")

        assert "Queries: 2/5" in prepend1
        assert "Queries: 1/5" in prepend2


class TestIntegration:
    """Integration tests for complete workflow."""

    def test_full_session_progression(self):
        """Test full session from start to completion."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        # Query 1: Conceptual
        tracker.record_query("s1", "What is validation?")
        prepend1 = generator.generate("s1", "What is validation?")
        assert "Queries: 1/5" in prepend1
        assert "📖✓" in prepend1

        # Query 2: Location
        tracker.record_query("s1", "Where is validator?")
        prepend2 = generator.generate("s1", "Where is validator?")
        assert "Queries: 2/5" in prepend2
        assert "📖✓" in prepend2
        assert "📍✓" in prepend2

        # Query 3-5: More angles
        tracker.record_query("s1", "How to use validator?")
        tracker.record_query("s1", "Best practice for validation")
        tracker.record_query("s1", "Another query")

        prepend_final = generator.generate("s1", "Another query")
        assert "🎉 Keep exploring!" in prepend_final

    def test_diversity_encouragement(self):
        """Test that suggestions encourage diversity."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)

        # Keep querying same angle
        for i in range(3):
            tracker.record_query("s1", f"What is X{i}?")

        prepend = generator.generate("s1", "What is X2?")

        # Should still suggest trying other angles
        assert "💡 Try:" in prepend
        # Should not have completion message (only 1 angle covered)
        assert "🎉" not in prepend
