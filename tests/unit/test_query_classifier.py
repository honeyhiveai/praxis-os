"""
Unit tests for Query Classifier module.

Tests keyword pattern matching, emoji mapping, suggestion generation,
performance requirements, and accuracy targets.

Traceability: implementation.md Section 4.2 (Unit Testing Strategy)
"""

import time
from typing import Set

import pytest

from mcp_server.core.query_classifier import (
    QueryAngle,
    classify_query_angle,
    get_angle_emoji,
    get_angle_suggestion,
)


class TestClassifyQueryAngle:
    """Test query angle classification."""

    def test_definition_angle(self) -> None:
        """Test definition angle classification."""
        queries = [
            "What is checkpoint validation?",
            "What are workflows?",
            "Define phase gating",
            "Explain the concept",
            "What's the meaning of RAG?",
        ]
        for query in queries:
            assert classify_query_angle(query) == "definition"

    def test_location_angle(self) -> None:
        """Test location angle classification."""
        queries = [
            "Where is validation implemented?",
            "Which file contains the parser?",
            "Locate the workflow engine",
            "Find the StateManager class",
            "Where can I find the config?",
        ]
        for query in queries:
            assert classify_query_angle(query) == "location"

    def test_practical_angle(self) -> None:
        """Test practical angle classification."""
        queries = [
            "How to implement testing?",
            "How do I use workflows?",
            "Tutorial for checkpoint validation",
            "Example of phase gating",
            "Steps to create a workflow",
        ]
        for query in queries:
            assert classify_query_angle(query) == "practical"

    def test_best_practice_angle(self) -> None:
        """Test best_practice angle classification."""
        queries = [
            "What are workflow best practices?",
            "Recommended approach for testing",
            "Should I use mocking?",
            "Standard pattern for validation",
            "Preferred convention for naming",
        ]
        for query in queries:
            assert classify_query_angle(query) == "best_practice"

    def test_error_prevention_angle(self) -> None:
        """Test error_prevention angle classification."""
        queries = [
            "Common mistakes in mocking?",
            "How to avoid race conditions?",
            "Pitfalls of async code",
            "Gotchas in type hints",
            "Don't do this with workflows",
        ]
        for query in queries:
            assert classify_query_angle(query) == "error_prevention"

    def test_empty_query_returns_default(self) -> None:
        """Test empty query falls back to definition."""
        assert classify_query_angle("") == "definition"
        assert classify_query_angle(None) == "definition"  # type: ignore[arg-type]

    def test_case_insensitive(self) -> None:
        """Test classification is case-insensitive."""
        assert classify_query_angle("What is X?") == "definition"
        assert classify_query_angle("WHAT IS X?") == "definition"
        assert classify_query_angle("what is x?") == "definition"

    def test_ambiguous_query_returns_first_match(self) -> None:
        """Test ambiguous queries return first matching angle."""
        # "what" matches definition keywords first
        query = "What are the best practices?"  # Could be definition OR best_practice
        result = classify_query_angle(query)
        assert result in ["definition", "best_practice"]

    def test_no_keyword_match_returns_default(self) -> None:
        """Test queries with no keyword matches default to definition."""
        assert classify_query_angle("Random text with no keywords") == "definition"
        assert classify_query_angle("xyz123") == "definition"

    def test_all_five_angles_covered(self) -> None:
        """Test that all 5 angles can be classified."""
        angles_seen: Set[QueryAngle] = set()

        test_queries = [
            ("What is this?", "definition"),
            ("Where is this?", "location"),
            ("How to do this?", "practical"),
            ("Best practices for this?", "best_practice"),
            ("Avoid mistakes in this?", "error_prevention"),
        ]

        for query, expected_angle in test_queries:
            result = classify_query_angle(query)
            angles_seen.add(result)
            assert result == expected_angle

        # Verify all 5 angles were classified
        assert len(angles_seen) == 5

    def test_classification_performance(self) -> None:
        """Test classification meets ≤5ms performance target."""
        query = "What are the best practices for implementing workflows?"

        # Warm up
        for _ in range(10):
            classify_query_angle(query)

        # Measure 100 runs
        timings = []
        for _ in range(100):
            start = time.perf_counter()
            classify_query_angle(query)
            end = time.perf_counter()
            timings.append((end - start) * 1000)  # Convert to ms

        avg_time_ms = sum(timings) / len(timings)
        assert (
            avg_time_ms <= 5.0
        ), f"Average classification time {avg_time_ms:.2f}ms exceeds 5ms target"


class TestGetAngleEmoji:
    """Test emoji representation for angles."""

    def test_all_angles_have_emojis(self) -> None:
        """Test all 5 angles return correct emojis."""
        expected_emojis = {
            "definition": "📖",
            "location": "📍",
            "practical": "🔧",
            "best_practice": "⭐",
            "error_prevention": "⚠️",
        }

        for angle, expected_emoji in expected_emojis.items():
            result = get_angle_emoji(angle)  # type: ignore[arg-type]
            assert result == expected_emoji

    def test_invalid_angle_raises_error(self) -> None:
        """Test invalid angle raises KeyError."""
        with pytest.raises(KeyError, match="Invalid angle"):
            get_angle_emoji("invalid_angle")  # type: ignore[arg-type]


class TestGetAngleSuggestion:
    """Test suggestion generation for angles."""

    def test_all_angles_have_suggestions(self) -> None:
        """Test all 5 angles generate valid suggestions."""
        topic = "workflow"

        expected_suggestions = {
            "definition": "What is workflow?",
            "location": "Where is workflow implemented?",
            "practical": "How to use workflow?",
            "best_practice": "workflow best practices",
            "error_prevention": "Common workflow mistakes to avoid",
        }

        for angle, expected_suggestion in expected_suggestions.items():
            result = get_angle_suggestion(angle, topic)  # type: ignore[arg-type]
            assert result == expected_suggestion

    def test_default_topic_placeholder(self) -> None:
        """Test default topic uses [concept] placeholder."""
        result = get_angle_suggestion("definition")  # type: ignore[arg-type]
        assert "[concept]" in result
        assert result == "What is [concept]?"

    def test_invalid_angle_raises_error(self) -> None:
        """Test invalid angle raises KeyError."""
        with pytest.raises(KeyError, match="Invalid angle"):
            get_angle_suggestion("invalid_angle")  # type: ignore[arg-type]


class TestAccuracyRequirement:
    """Test classification accuracy ≥90% on balanced sample set."""

    def test_accuracy_on_50_query_sample(self) -> None:
        """Test ≥90% accuracy on 50 queries (10 per angle)."""
        # 10 queries per angle (50 total)
        test_set = [
            # Definition (10)
            ("What is phase gating?", "definition"),
            ("Define checkpoint", "definition"),
            ("Explain workflow", "definition"),
            ("What are standards?", "definition"),
            ("Meaning of RAG", "definition"),
            ("What's the purpose?", "definition"),
            ("Understand the concept", "definition"),
            ("Overview of system", "definition"),
            ("Introduction to prAxIs OS", "definition"),
            ("What is this?", "definition"),
            # Location (10)
            ("Where is the parser?", "location"),
            ("Which file has validation?", "location"),
            ("Locate StateManager", "location"),
            ("Find the config", "location"),
            ("Where can I see examples?", "location"),
            ("In what file is this?", "location"),
            ("Path to workflows", "location"),
            ("Which directory has tests?", "location"),
            ("Search for the module", "location"),
            ("Look for implementation", "location"),
            # Practical (10)
            ("How to create a workflow?", "practical"),
            ("How do I use phases?", "practical"),
            ("Tutorial for testing", "practical"),
            ("Example of validation", "practical"),
            ("Steps to implement", "practical"),
            ("Guide for setup", "practical"),
            ("How can I use this?", "practical"),
            ("Usage instructions", "practical"),
            ("Implement checkpoint", "practical"),
            ("Use the framework", "practical"),
            # Best Practice (10)
            ("Best practices for workflows?", "best_practice"),
            ("Recommended approach", "best_practice"),
            ("Should I mock this?", "best_practice"),
            ("Standard pattern", "best_practice"),
            ("Convention for naming", "best_practice"),
            ("Idiomatic Python", "best_practice"),
            ("Optimal solution", "best_practice"),
            ("Preferred method", "best_practice"),
            ("Guidelines for code", "best_practice"),
            ("What's recommended?", "best_practice"),
            # Error Prevention (10)
            ("Common mistakes?", "error_prevention"),
            ("Avoid race conditions", "error_prevention"),
            ("Pitfalls of async", "error_prevention"),
            ("Gotchas in testing", "error_prevention"),
            ("Don't do this", "error_prevention"),
            ("Prevent errors", "error_prevention"),
            ("Warning about X", "error_prevention"),
            ("Caution with Y", "error_prevention"),
            ("Anti-pattern example", "error_prevention"),
            ("Mistakes to avoid", "error_prevention"),
        ]

        correct = 0
        total = len(test_set)

        for query, expected_angle in test_set:
            result = classify_query_angle(query)
            if result == expected_angle:
                correct += 1

        accuracy = (correct / total) * 100
        assert (
            accuracy >= 90.0
        ), f"Accuracy {accuracy:.1f}% below 90% target (correct: {correct}/{total})"


# Integration test placeholder
def test_module_exports() -> None:
    """Test module exports expected symbols."""
    from mcp_server.core import query_classifier

    assert hasattr(query_classifier, "QueryAngle")
    assert hasattr(query_classifier, "classify_query_angle")
    assert hasattr(query_classifier, "get_angle_emoji")
    assert hasattr(query_classifier, "get_angle_suggestion")
