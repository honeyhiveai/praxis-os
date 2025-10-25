"""
Query Classifier for Query Gamification System.

Classifies query strings into one of five standard angles using keyword
pattern matching for deterministic, fast angle identification.

Traceability: specs.md Section 2.1 (QueryClassifier Component)
"""

from typing import Literal

# Type alias for query angles
QueryAngle = Literal[
    "definition",
    "location",
    "practical",
    "best_practice",
    "error_prevention",
]

# Keyword patterns for each angle (case-insensitive matching)
# Ordered by specificity - more specific patterns checked first
_ANGLE_KEYWORDS = {
    "best_practice": [
        "best practice",
        "recommended",
        "should i",
        "pattern",
        "standard",
        "convention",
        "idiomatic",
        "optimal",
        "preferred",
        "guidelines",
    ],
    "error_prevention": [
        "avoid",
        "prevent",
        "mistake",
        "pitfall",
        "gotcha",
        "common error",
        "warning",
        "caution",
        "anti-pattern",
        "don't",
    ],
    "location": [
        "where",
        "which file",
        "which directory",
        "locate",
        "find",
        "path to",
        "location of",
        "search for",
        "look for",
        "in what file",
    ],
    "practical": [
        "how to",
        "how do i",
        "how can i",
        "tutorial",
        "example",
        "guide",
        "steps",
        "implement",
        "usage",
        "use",
    ],
    "definition": [
        "what is",
        "what are",
        "define",
        "explain",
        "meaning",
        "understand",
        "concept",
        "purpose",
        "overview",
        "introduction",
    ],
}

# Emoji mapping for angles
_ANGLE_EMOJIS = {
    "definition": "📖",
    "location": "📍",
    "practical": "🔧",
    "best_practice": "⭐",
    "error_prevention": "⚠️",
}

# Suggestion templates for each angle
_ANGLE_SUGGESTIONS = {
    "definition": "What is {topic}?",
    "location": "Where is {topic} implemented?",
    "practical": "How to use {topic}?",
    "best_practice": "{topic} best practices",
    "error_prevention": "Common {topic} mistakes to avoid",
}


def classify_query_angle(query: str) -> QueryAngle:
    """
    Classify query into one of 5 standard angles using keyword patterns.

    Uses deterministic keyword matching for fast, consistent classification.
    Case-insensitive, prioritizes first match in precedence order.

    Args:
        query: The query string to classify

    Returns:
        QueryAngle enum value ('definition', 'location', 'practical',
        'best_practice', or 'error_prevention')

    Performance:
        - Latency: ≤5ms for typical queries
        - Accuracy: ≥90% on balanced test sets

    Examples:
        >>> classify_query_angle("What is checkpoint validation?")
        'definition'
        >>> classify_query_angle("Where is validation implemented?")
        'location'
        >>> classify_query_angle("How to implement testing?")
        'practical'
        >>> classify_query_angle("What are workflow best practices?")
        'best_practice'
        >>> classify_query_angle("Common mistakes in mocking?")
        'error_prevention'

    Notes:
        - Empty/None queries fall back to 'definition'
        - Ambiguous queries return first matching angle
        - Non-English queries may misclassify (known limitation)

    Traceability:
        - FR-002: Query angle classification
        - FR-005: Support for 5 standard angles
        - NFR-P2: ≤5ms performance target
    """
    # Handle empty/invalid input
    if not query or not isinstance(query, str):
        return "definition"

    # Normalize query for case-insensitive matching
    query_lower = query.lower()

    # Check each angle in precedence order
    for angle, keywords in _ANGLE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in query_lower:
                return angle  # type: ignore[return-value]

    # Default to 'definition' if no keywords match
    return "definition"


def get_angle_emoji(angle: QueryAngle) -> str:
    """
    Get emoji representation for query angle.

    Args:
        angle: The query angle

    Returns:
        Emoji string ('📖' for definition, '📍' for location, '🔧' for
        practical, '⭐' for best_practice, '⚠️' for error_prevention)

    Raises:
        KeyError: If angle is not a valid QueryAngle value

    Examples:
        >>> get_angle_emoji('definition')
        '📖'
        >>> get_angle_emoji('location')
        '📍'
        >>> get_angle_emoji('practical')
        '🔧'

    Traceability:
        - FR-005: Angle emoji representations
    """
    if angle not in _ANGLE_EMOJIS:
        raise KeyError(f"Invalid angle: {angle}. Must be one of {list(_ANGLE_EMOJIS.keys())}")

    return _ANGLE_EMOJIS[angle]


def get_angle_suggestion(angle: QueryAngle, topic: str = "[concept]") -> str:
    """
    Generate example query suggestion for given angle.

    Creates angle-specific suggestion strings with customizable topic
    to guide users toward diverse query patterns.

    Args:
        angle: The angle to suggest
        topic: Optional topic to customize suggestion (default: "[concept]")

    Returns:
        Formatted suggestion string (e.g., "What is workflow?")

    Raises:
        KeyError: If angle is not a valid QueryAngle value

    Examples:
        >>> get_angle_suggestion('definition', 'workflow')
        'What is workflow?'
        >>> get_angle_suggestion('location', 'validator')
        'Where is validator implemented?'
        >>> get_angle_suggestion('practical')
        'How to use [concept]?'

    Traceability:
        - FR-008: Angle-specific suggestion generation
    """
    if angle not in _ANGLE_SUGGESTIONS:
        raise KeyError(f"Invalid angle: {angle}. Must be one of {list(_ANGLE_SUGGESTIONS.keys())}")

    template = _ANGLE_SUGGESTIONS[angle]
    return template.format(topic=topic)


__all__ = [
    "QueryAngle",
    "classify_query_angle",
    "get_angle_emoji",
    "get_angle_suggestion",
]

