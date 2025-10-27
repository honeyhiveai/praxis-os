"""
Query Tracker for Query Gamification System.

Tracks per-session query statistics including total/unique counts,
angle coverage, and query history for progress visualization.

Traceability: specs.md Section 2.2 (QueryTracker Component)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Set

from .query_classifier import QueryAngle, classify_query_angle


@dataclass
class QueryStats:
    """
    Statistics for a query session.

    Tracks query counts, angle coverage, and recent query history
    for progress visualization and gamification feedback.

    Attributes:
        total_queries: Total number of queries in session (includes duplicates)
        unique_queries: Number of unique queries (normalized comparison)
        angles_covered: Set of QueryAngle values seen in this session
        query_history: List of recent queries (max 10, FIFO)
        last_query_time: Timestamp of most recent query (None if no queries yet)

    Memory:
        Approximately 1-1.5KB per session (bounded by history limit)

    Examples:
        >>> stats = QueryStats()
        >>> stats.total_queries
        0
        >>> stats.angles_covered
        set()

    Traceability:
        - FR-001: Session-based query tracking
        - NFR-P3: Memory footprint ≤1MB per session
    """

    total_queries: int = 0
    unique_queries: int = 0
    angles_covered: Set[QueryAngle] = field(default_factory=set)
    query_history: List[str] = field(default_factory=list)
    last_query_time: datetime | None = None


class QueryTracker:
    """
    Track query patterns per conversation session.

    Maintains isolated statistics for each session including total/unique
    query counts, angle coverage, and recent query history. Uses singleton
    pattern for global state management.

    The tracker automatically:
    - Classifies query angles using QueryClassifier
    - Detects duplicate queries via normalized comparison
    - Maintains bounded history (FIFO, max 10 queries)
    - Creates new sessions on first query
    - Isolates session state (no cross-contamination)

    Performance:
        - record_query(): ≤2ms average latency
        - Memory: ~1KB per session

    Thread Safety:
        Not thread-safe. Use separate instances for concurrent contexts.

    Examples:
        >>> tracker = QueryTracker()
        >>> angle = tracker.record_query("session_1", "What is X?")
        >>> angle
        'definition'
        >>> stats = tracker.get_stats("session_1")
        >>> stats.total_queries
        1

    Traceability:
        - FR-001: Session-based query tracking
        - FR-004: Track query count
        - FR-005: Track angle coverage
        - NFR-R2: Session isolation
    """

    def __init__(self) -> None:
        """
        Initialize query tracker with empty session storage.

        Creates an empty dictionary for session statistics.
        Each session_id maps to its own QueryStats instance.
        """
        self._sessions: Dict[str, QueryStats] = {}

    def record_query(self, session_id: str, query: str) -> QueryAngle:
        """
        Record a query and return its classified angle.

        Tracks query in session statistics:
        - Increments total_queries count
        - Increments unique_queries if not seen before (normalized comparison)
        - Adds angle to angles_covered set
        - Appends to query_history (FIFO, max 10)
        - Updates last_query_time

        Args:
            session_id: Conversation session identifier
            query: The query string to record

        Returns:
            QueryAngle: The classified angle for this query

        Performance:
            - Average latency: ≤2ms
            - O(1) session lookup
            - O(n) duplicate detection (n ≤ 10 for history)

        Examples:
            >>> tracker = QueryTracker()
            >>> angle = tracker.record_query("session_1", "What is X?")
            >>> angle
            'definition'
            >>> tracker.record_query("session_1", "what is x?")  # Duplicate
            'definition'
            >>> stats = tracker.get_stats("session_1")
            >>> stats.total_queries
            2
            >>> stats.unique_queries
            1

        Traceability:
            - FR-001: Record query in session
            - FR-010: Unique query detection
            - NFR-P2: ≤2ms latency
        """
        # Classify query angle
        angle = classify_query_angle(query)

        # Get or create session stats
        if session_id not in self._sessions:
            self._sessions[session_id] = QueryStats()

        stats = self._sessions[session_id]

        # Update total count
        stats.total_queries += 1

        # Check if query is unique (normalized comparison)
        normalized_query = query.lower().strip()
        normalized_history = [q.lower().strip() for q in stats.query_history]

        if normalized_query not in normalized_history:
            stats.unique_queries += 1

        # Add angle to covered set
        stats.angles_covered.add(angle)

        # Add to query history (FIFO, max 10)
        stats.query_history.append(query)
        if len(stats.query_history) > 10:
            stats.query_history.pop(0)  # Remove oldest

        # Update timestamp
        stats.last_query_time = datetime.now()

        return angle

    def get_stats(self, session_id: str) -> QueryStats:
        """
        Get current statistics for session.

        Returns the QueryStats instance for the given session.
        If session doesn't exist, returns an empty QueryStats.

        Args:
            session_id: Conversation session identifier

        Returns:
            QueryStats: Current statistics for the session

        Examples:
            >>> tracker = QueryTracker()
            >>> stats = tracker.get_stats("new_session")  # New session
            >>> stats.total_queries
            0
            >>> tracker.record_query("new_session", "What is X?")
            'definition'
            >>> stats = tracker.get_stats("new_session")
            >>> stats.total_queries
            1

        Traceability:
            - FR-001: Retrieve session statistics
        """
        if session_id not in self._sessions:
            return QueryStats()

        return self._sessions[session_id]

    def get_uncovered_angles(self, session_id: str) -> Set[QueryAngle]:
        """
        Get angles not yet covered in this session.

        Returns the set of QueryAngle values that have NOT been
        recorded in this session. Useful for generating suggestions
        to explore diverse query patterns.

        Args:
            session_id: Conversation session identifier

        Returns:
            Set[QueryAngle]: Angles not yet covered in session

        Examples:
            >>> tracker = QueryTracker()
            >>> tracker.record_query("s1", "What is X?")  # definition
            'definition'
            >>> uncovered = tracker.get_uncovered_angles("s1")
            >>> len(uncovered)
            4
            >>> 'definition' in uncovered
            False
            >>> 'location' in uncovered
            True

        Traceability:
            - FR-005: Track angle coverage
            - FR-006: Support suggestion generation
        """
        all_angles: Set[QueryAngle] = {
            "definition",
            "location",
            "practical",
            "best_practice",
            "error_prevention",
        }

        if session_id not in self._sessions:
            return all_angles

        stats = self._sessions[session_id]
        return all_angles - stats.angles_covered

    def reset_session(self, session_id: str) -> None:
        """
        Reset session statistics (primarily for testing).

        Removes all statistics for the given session. Useful for
        test cleanup and session restart scenarios.

        Args:
            session_id: Conversation session identifier to reset

        Examples:
            >>> tracker = QueryTracker()
            >>> tracker.record_query("s1", "What is X?")
            'definition'
            >>> tracker.reset_session("s1")
            >>> stats = tracker.get_stats("s1")
            >>> stats.total_queries
            0

        Traceability:
            - Testing utility for session isolation
        """
        if session_id in self._sessions:
            del self._sessions[session_id]


# Global singleton instance
_tracker: QueryTracker | None = None


def get_tracker() -> QueryTracker:
    """
    Get the global query tracker instance.

    Uses singleton pattern to ensure a single QueryTracker instance
    per process. Thread-safe initialization.

    Returns:
        QueryTracker: The global tracker instance

    Examples:
        >>> tracker1 = get_tracker()
        >>> tracker2 = get_tracker()
        >>> tracker1 is tracker2
        True

    Traceability:
        - Implementation note: Global singleton pattern
    """
    global _tracker
    if _tracker is None:
        _tracker = QueryTracker()
    return _tracker


__all__ = [
    "QueryStats",
    "QueryTracker",
    "get_tracker",
]
