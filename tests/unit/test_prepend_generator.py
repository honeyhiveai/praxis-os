"""
Unit tests for Prepend Generator module.

Tests prepend generation, format compliance, token budgets,
topic extraction, and performance requirements.

Traceability: implementation.md Section 4.2 (Unit Testing Strategy)
"""

import re
import time

import tiktoken

from mcp_server.core.prepend_generator import (
    _extract_topic,
    _generate_angle_indicators,
    _generate_suggestion,
    generate_query_prepend,
)
from mcp_server.core.query_tracker import QueryTracker


class TestGenerateQueryPrepend:
    """Test main prepend generation function."""

    def test_prepend_includes_header_line(self) -> None:
        """Test prepend includes header with emojis and tagline."""
        tracker = QueryTracker()
        tracker.record_query("session1", "What is X?")

        prepend = generate_query_prepend(tracker, "session1", "What is X?")

        assert "🔍🔍🔍🔍🔍" in prepend
        assert "QUERIES = KNOWLEDGE = ACCURACY = QUALITY" in prepend
        assert "⭐⭐⭐⭐⭐" in prepend

    def test_prepend_includes_progress_line(self) -> None:
        """Test prepend includes progress line with query counts and angles."""
        tracker = QueryTracker()
        tracker.record_query("session1", "What is X?")

        prepend = generate_query_prepend(tracker, "session1", "What is X?")

        assert "Queries: 1/5" in prepend
        assert "Unique: 1" in prepend
        assert "Angles:" in prepend

    def test_prepend_includes_suggestion_when_incomplete(self) -> None:
        """Test prepend includes suggestion when <5 queries."""
        tracker = QueryTracker()
        tracker.record_query("session1", "What is X?")

        prepend = generate_query_prepend(tracker, "session1", "What is X?")

        assert "💡 Try:" in prepend
        assert "'" in prepend  # Suggestion wrapped in quotes

    def test_prepend_includes_completion_message_when_complete(self) -> None:
        """Test prepend includes completion message when ≥5 queries and ≥4 angles."""
        tracker = QueryTracker()

        # Record 5 queries with 4 different angles
        tracker.record_query("session1", "What is X?")  # definition
        tracker.record_query("session1", "Where is Y?")  # location
        tracker.record_query("session1", "How to Z?")  # practical
        tracker.record_query("session1", "Best practices?")  # best_practice
        tracker.record_query("session1", "What is A?")  # definition again

        prepend = generate_query_prepend(tracker, "session1", "What is A?")

        assert "🎉" in prepend
        assert "Great exploration" in prepend
        assert "💡 Try:" not in prepend  # No suggestion when complete

    def test_prepend_includes_separator(self) -> None:
        """Test prepend includes visual separator."""
        tracker = QueryTracker()
        tracker.record_query("session1", "What is X?")

        prepend = generate_query_prepend(tracker, "session1", "What is X?")

        assert "---" in prepend

    def test_prepend_format_is_three_lines_plus_separator(self) -> None:
        """Test prepend maintains ≤3 line content format (plus separator)."""
        tracker = QueryTracker()
        tracker.record_query("session1", "What is X?")

        prepend = generate_query_prepend(tracker, "session1", "What is X?")

        # Split into lines, filter empty lines
        lines = [line for line in prepend.split("\n") if line.strip()]

        # Should have: header, progress, suggestion/completion, separator
        assert len(lines) == 4

    def test_prepend_token_count_within_budget(self) -> None:
        """Test prepend token count ≤120 tokens maximum."""
        tracker = QueryTracker()
        enc = tiktoken.get_encoding("cl100k_base")

        # Test various scenarios
        scenarios = [
            ("1 query", 1),
            ("3 queries", 3),
            ("5 queries", 5),
            ("10 queries", 10),
        ]

        for scenario_name, num_queries in scenarios:
            tracker_test = QueryTracker()

            # Record queries with different angles
            queries = [
                "What is workflow?",
                "Where is StateManager?",
                "How to create checkpoint?",
                "Best practices for testing?",
                "Avoid mistakes in validation?",
                "What is phase gating?",
                "Where is parser?",
                "How to use RAG?",
                "Standard patterns?",
                "Common errors?",
            ]

            for i in range(min(num_queries, len(queries))):
                tracker_test.record_query(f"test_{scenario_name}", queries[i])

            prepend = generate_query_prepend(
                tracker_test, f"test_{scenario_name}", queries[num_queries - 1]
            )

            token_count = len(enc.encode(prepend))
            assert (
                token_count <= 120
            ), f"Scenario '{scenario_name}' token count {token_count} exceeds 120 token budget"

    def test_prepend_average_token_count(self) -> None:
        """Test prepend average token count ~85 tokens across 100 samples."""
        enc = tiktoken.get_encoding("cl100k_base")
        token_counts = []

        queries = [
            "What is workflow validation?",
            "Where is checkpoint system?",
            "How to implement testing?",
            "Best practices for code quality?",
            "Avoid mistakes in async?",
        ]

        for i in range(100):
            tracker = QueryTracker()
            session_id = f"sample_{i}"

            # Vary number of queries (1-5)
            num_queries = (i % 5) + 1
            for j in range(num_queries):
                tracker.record_query(session_id, queries[j])

            prepend = generate_query_prepend(
                tracker, session_id, queries[num_queries - 1]
            )
            token_count = len(enc.encode(prepend))
            token_counts.append(token_count)

        avg_tokens = sum(token_counts) / len(token_counts)
        assert (
            75 <= avg_tokens <= 95
        ), f"Average token count {avg_tokens:.1f} not within 75-95 range"

    def test_prepend_performance(self) -> None:
        """Test generate_query_prepend meets ≤10ms performance target."""
        tracker = QueryTracker()

        # Record some queries
        for i in range(5):
            tracker.record_query("perf_test", f"Query {i}")

        # Warm up
        for _ in range(10):
            generate_query_prepend(tracker, "perf_test", "Query")

        # Measure 100 runs
        timings = []
        for i in range(100):
            start = time.perf_counter()
            generate_query_prepend(tracker, "perf_test", f"Performance query {i}")
            end = time.perf_counter()
            timings.append((end - start) * 1000)  # Convert to ms

        avg_time_ms = sum(timings) / len(timings)
        assert (
            avg_time_ms <= 10.0
        ), f"Average prepend generation time {avg_time_ms:.2f}ms exceeds 10ms target"


class TestGenerateAngleIndicators:
    """Test angle coverage indicator generation."""

    def test_all_angles_covered(self) -> None:
        """Test indicator generation when all angles covered."""
        angles_covered = {
            "definition",
            "location",
            "practical",
            "best_practice",
            "error_prevention",
        }

        indicators = _generate_angle_indicators(angles_covered)

        # Should have 5 checkmarks
        assert indicators.count("✓") == 5
        assert indicators.count("⬜") == 0

    def test_no_angles_covered(self) -> None:
        """Test indicator generation when no angles covered."""
        angles_covered = set()

        indicators = _generate_angle_indicators(angles_covered)

        # Should have 5 empty boxes
        assert indicators.count("✓") == 0
        assert indicators.count("⬜") == 5

    def test_partial_angles_covered(self) -> None:
        """Test indicator generation with partial coverage."""
        angles_covered = {"definition", "location"}

        indicators = _generate_angle_indicators(angles_covered)

        # Should have 2 checkmarks, 3 empty boxes
        assert indicators.count("✓") == 2
        assert indicators.count("⬜") == 3
        assert "📖✓" in indicators
        assert "📍✓" in indicators

    def test_indicator_order_is_deterministic(self) -> None:
        """Test indicators always appear in same order."""
        angles_covered = {"practical", "definition", "error_prevention"}

        indicators = _generate_angle_indicators(angles_covered)

        # Verify order: definition, location, practical, best_practice, error_prevention
        assert re.search(r"📖.*📍.*🔧.*⭐.*⚠️", indicators)


class TestExtractTopic:
    """Test topic extraction from queries."""

    def test_extract_topic_removes_common_words(self) -> None:
        """Test topic extraction removes common query words."""
        test_cases = [
            ("What is checkpoint validation?", "checkpoint validation"),
            ("How to use workflows?", "use workflows"),
            ("Where is the parser?", "parser"),
            ("What are the best practices?", "best practices"),
        ]

        for query, expected_topic in test_cases:
            topic = _extract_topic(query)
            assert topic == expected_topic

    def test_extract_topic_handles_empty_query(self) -> None:
        """Test topic extraction falls back to [concept] for empty query."""
        assert _extract_topic("") == "[concept]"
        assert _extract_topic(None) == "[concept]"  # type: ignore[arg-type]

    def test_extract_topic_handles_only_common_words(self) -> None:
        """Test topic extraction falls back when only common words."""
        assert _extract_topic("what is the") == "[concept]"
        assert _extract_topic("how to do") == "[concept]"

    def test_extract_topic_limits_to_three_words(self) -> None:
        """Test topic extraction limits to 3 words."""
        topic = _extract_topic("What is the checkpoint validation system architecture?")
        # Should get first 3 non-common words
        words = topic.split()
        assert len(words) <= 3


class TestGenerateSuggestion:
    """Test suggestion generation for uncovered angles."""

    def test_suggestion_for_uncovered_angle(self) -> None:
        """Test suggestion generation selects uncovered angle."""
        uncovered = {"location", "practical"}
        topic = "workflow"

        suggestion = _generate_suggestion(uncovered, topic)

        # Should suggest location (first in priority order)
        assert "Where is workflow" in suggestion or "location" in suggestion.lower()

    def test_suggestion_when_all_covered(self) -> None:
        """Test suggestion when all angles covered."""
        uncovered = set()
        topic = "workflow"

        suggestion = _generate_suggestion(uncovered, topic)

        assert "Explore more" in suggestion or "advanced" in suggestion.lower()

    def test_suggestion_wrapped_in_quotes(self) -> None:
        """Test suggestions are wrapped in single quotes."""
        uncovered = {"definition"}
        topic = "test"

        suggestion = _generate_suggestion(uncovered, topic)

        assert suggestion.startswith("'")
        assert suggestion.endswith("'")


# Integration test
def test_full_prepend_workflow() -> None:
    """Test complete prepend generation workflow."""
    tracker = QueryTracker()

    # Record first query
    tracker.record_query("integration", "What is checkpoint?")
    prepend = generate_query_prepend(tracker, "integration", "What is checkpoint?")

    # Verify structure
    assert "🔍🔍🔍🔍🔍" in prepend
    assert "Queries: 1/5" in prepend
    assert "Unique: 1" in prepend
    assert "📖✓" in prepend  # definition covered
    assert "💡 Try:" in prepend
    assert "---" in prepend

    # Record more queries
    tracker.record_query("integration", "Where is parser?")
    tracker.record_query("integration", "How to use RAG?")
    tracker.record_query("integration", "Best practices?")
    tracker.record_query("integration", "Avoid errors?")

    prepend = generate_query_prepend(tracker, "integration", "Avoid errors?")

    # Should have completion message now
    assert "🎉" in prepend
    assert "Queries: 5/5" in prepend


def test_module_exports() -> None:
    """Test module exports expected symbols."""
    from mcp_server.core import prepend_generator

    assert hasattr(prepend_generator, "generate_query_prepend")
