"""
Prepend Generator for Query Gamification System.

Generates dynamic feedback messages based on query statistics
to encourage diverse exploration and provide progress visualization.

Traceability: specs.md Section 2.3 (PrependGenerator Component)
"""

import re
from typing import Set

from .query_classifier import QueryAngle, get_angle_emoji, get_angle_suggestion
from .query_tracker import QueryTracker


def generate_query_prepend(
    tracker: QueryTracker,
    session_id: str,
    current_query: str,
) -> str:
    """
    Generate dynamic prepend message based on query history.

    Creates a 3-line feedback message with:
    - Header with emoji tagline
    - Progress line (query counts and angle coverage visualization)
    - Suggestion (if <5 queries) or completion message (if ≥5 queries + ≥4 angles)
    - Visual separator

    Args:
        tracker: The query tracker instance with session statistics
        session_id: Current conversation session identifier
        current_query: The query that just executed (for topic extraction)

    Returns:
        str: Formatted prepend string with progress and suggestions

    Performance:
        - Latency: ≤10ms average
        - Token count: ≤120 tokens maximum, ~85 average

    Examples:
        >>> tracker = QueryTracker()
        >>> tracker.record_query("s1", "What is X?")
        'definition'
        >>> prepend = generate_query_prepend(tracker, "s1", "What is X?")
        >>> "Queries: 1/5" in prepend
        True
        >>> "📖✓" in prepend
        True

        After 5 queries with 4+ angles:
        >>> # ... record 4 more queries ...
        >>> prepend = generate_query_prepend(tracker, "s1", "query")
        >>> "Keep exploring" in prepend
        True

    Token Budget:
        - Scenario 1 (1 query): ~60 tokens
        - Scenario 2 (3 queries): ~65 tokens
        - Scenario 3 (5+ queries, complete): ~70 tokens
        - Maximum: 90 tokens (reduced by removing old header)

    Traceability:
        - FR-003: Dynamic prepend generation
        - FR-004: Progress counter
        - FR-005: Angle coverage visualization
        - FR-006: Concrete suggestions
        - FR-007: Completion message
        - NFR-P1: Token budget ≤500/task (~85 avg)
        - NFR-U1: Non-intrusive (≤3 lines)
    """
    # Get current session statistics
    stats = tracker.get_stats(session_id)

    # Generate progress line with angle coverage
    angle_indicators = _generate_angle_indicators(stats.angles_covered)
    progress_line = (
        f"📊 Queries: {stats.total_queries}/5 | "
        f"Unique: {stats.unique_queries} | "
        f"Angles: {angle_indicators}"
    )

    # Generate suggestion or completion message
    if stats.total_queries >= 5 and len(stats.angles_covered) >= 4:
        # Completion message
        feedback_line = "🎉 Keep exploring! Query liberally to deepen your knowledge."
    else:
        # Generate suggestion for uncovered angle
        uncovered_angles = tracker.get_uncovered_angles(session_id)
        topic = _extract_topic(current_query)
        suggestion = _generate_suggestion(uncovered_angles, topic)
        feedback_line = f"💡 Try: {suggestion}"

    # Separator
    separator = "---"

    # Combine all lines (no old header!)
    prepend = f"{progress_line}\n{feedback_line}\n\n{separator}\n\n"

    return prepend


def _generate_angle_indicators(angles_covered: Set[QueryAngle]) -> str:
    """
    Generate angle coverage indicators with emojis.

    Creates a visual representation of angle coverage using
    emojis with checkmarks (✓) for covered angles and
    empty boxes (⬜) for uncovered angles.

    Args:
        angles_covered: Set of QueryAngle values covered in session

    Returns:
        str: Formatted indicator string (e.g., "📖✓ 📍⬜ 🔧✓ ⭐⬜ ⚠️⬜")

    Examples:
        >>> indicators = _generate_angle_indicators({'definition', 'location'})
        >>> indicators
        '📖✓ 📍✓ 🔧⬜ ⭐⬜ ⚠️⬜'

    Traceability:
        - FR-005: Angle coverage visualization
    """
    # Deterministic angle order
    angle_order: tuple[QueryAngle, ...] = (
        "definition",
        "location",
        "practical",
        "best_practice",
        "error_prevention",
    )

    indicators = []
    for angle in angle_order:
        emoji = get_angle_emoji(angle)
        status = "✓" if angle in angles_covered else "⬜"
        indicators.append(f"{emoji}{status}")

    return " ".join(indicators)


def _extract_topic(query: str) -> str:
    """
    Extract topic from query by removing common words.

    Strips common query words (what, how, where, is, are, the, a, an)
    to extract the core topic for suggestion generation.

    **Security**: Sanitizes HTML tags to prevent XSS injection in suggestions.

    Args:
        query: The query string

    Returns:
        str: Extracted topic or "[concept]" if extraction fails

    Examples:
        >>> _extract_topic("What is checkpoint validation?")
        'checkpoint validation'
        >>> _extract_topic("How to use workflows?")
        'use workflows'
        >>> _extract_topic("Where is the parser?")
        'parser'

    Traceability:
        - Implementation detail for suggestion generation
        - Security: NFR-S1 (XSS prevention)
    """
    if not query or not isinstance(query, str):
        return "[concept]"

    # SECURITY: Remove HTML tags to prevent XSS (NFR-S1)
    # Simple regex to strip all <tag> and </tag> patterns
    sanitized_query = re.sub(r"<[^>]+>", "", query)

    # Common words to remove
    common_words = {
        "what",
        "is",
        "are",
        "how",
        "to",
        "where",
        "which",
        "the",
        "a",
        "an",
        "do",
        "does",
        "can",
        "i",
    }

    # Split, filter, and rejoin
    words = sanitized_query.lower().split()
    filtered_words = [w.strip("?.,;:!") for w in words if w not in common_words]

    if not filtered_words:
        return "[concept]"

    # Take first 2-3 words as topic
    topic = " ".join(filtered_words[:3])
    return topic if topic else "[concept]"


def _generate_suggestion(uncovered_angles: Set[QueryAngle], topic: str) -> str:
    """
    Generate concrete query suggestion for uncovered angle.

    Selects the first uncovered angle in deterministic order
    and generates a topic-specific suggestion string.

    Args:
        uncovered_angles: Set of angles not yet covered
        topic: Extracted topic from current query

    Returns:
        str: Concrete suggestion string (e.g., "'checkpoint validation best practices'")

    Examples:
        >>> suggestion = _generate_suggestion({'best_practice', 'location'}, 'workflow')
        >>> suggestion
        "'Where is workflow implemented?'"

    Traceability:
        - FR-006: Concrete query suggestions
    """
    if not uncovered_angles:
        # All angles covered, suggest general exploration
        return "'Explore more advanced topics'"

    # Deterministic angle order for consistent suggestions
    angle_priority: tuple[QueryAngle, ...] = (
        "definition",
        "location",
        "practical",
        "best_practice",
        "error_prevention",
    )

    # Select first uncovered angle in priority order
    selected_angle = None
    for angle in angle_priority:
        if angle in uncovered_angles:
            selected_angle = angle
            break

    if selected_angle is None:
        return "'Explore more advanced topics'"

    # Generate suggestion using angle-specific template
    suggestion_text = get_angle_suggestion(selected_angle, topic)
    return f"'{suggestion_text}'"


__all__ = [
    "generate_query_prepend",
]
