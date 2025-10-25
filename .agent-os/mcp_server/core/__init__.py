"""
Core components for dynamic workflow engine and query gamification.

Provides parsers, registries, session management for dynamic workflows,
and query tracking/gamification for RAG search enhancement.
"""

from .dynamic_registry import DynamicContentRegistry, DynamicRegistryError
from .parsers import ParseError, SourceParser, SpecTasksParser
from .prepend_generator import generate_query_prepend
from .query_classifier import QueryAngle, classify_query_angle, get_angle_emoji
from .query_tracker import QueryStats, QueryTracker, get_tracker
from .session import WorkflowSession, WorkflowSessionError
from .session_id_extractor import (
    SessionState,
    extract_session_id_from_context,
    hash_session_id,
)

__all__ = [
    # Dynamic workflow components
    "ParseError",
    "SourceParser",
    "SpecTasksParser",
    "DynamicRegistryError",
    "DynamicContentRegistry",
    "WorkflowSessionError",
    "WorkflowSession",
    # Query gamification components
    "QueryAngle",
    "classify_query_angle",
    "get_angle_emoji",
    "QueryStats",
    "QueryTracker",
    "get_tracker",
    "generate_query_prepend",
    "SessionState",
    "extract_session_id_from_context",
    "hash_session_id",
]
