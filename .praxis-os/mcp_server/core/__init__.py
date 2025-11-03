"""
Core components for dynamic workflow engine and query gamification.

Provides parsers, registries, session management for dynamic workflows,
and query tracking/gamification for RAG search enhancement.

NOTE: Lazy import package to prevent circular import issues.
Components should be imported directly from submodules, not from this package:
    from mcp_server.core.parsers import SpecTasksParser  # ✅ Correct
    from mcp_server.core import SpecTasksParser  # ❌ Don't use (causes circular imports)
"""

# Lazy imports to prevent circular import chains
# Users should import directly from submodules (e.g., from mcp_server.core.parsers import ...)
__all__ = [
    # Dynamic workflow components (import from submodules)
    "ParseError",
    "SourceParser",
    "SpecTasksParser",
    "DynamicRegistryError",
    "DynamicContentRegistry",
    "WorkflowSessionError",
    "WorkflowSession",
    # Query gamification components (import from submodules)
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


def __getattr__(name):
    """Lazy import to avoid circular dependencies."""
    if name in __all__:
        # Dynamic imports only when requested
        if name in ["ParseError", "SourceParser", "SpecTasksParser"]:
            from .parsers import ParseError, SourceParser, SpecTasksParser
            return locals()[name]
        elif name in ["DynamicRegistryError", "DynamicContentRegistry"]:
            from .dynamic_registry import DynamicContentRegistry, DynamicRegistryError
            return locals()[name]
        elif name in ["WorkflowSessionError", "WorkflowSession"]:
            from .session import WorkflowSession, WorkflowSessionError
            return locals()[name]
        elif name in ["QueryAngle", "classify_query_angle", "get_angle_emoji"]:
            from .query_classifier import QueryAngle, classify_query_angle, get_angle_emoji
            return locals()[name]
        elif name in ["QueryStats", "QueryTracker", "get_tracker"]:
            from .query_tracker import QueryStats, QueryTracker, get_tracker
            return locals()[name]
        elif name == "generate_query_prepend":
            from .prepend_generator import generate_query_prepend
            return generate_query_prepend
        elif name in ["SessionState", "extract_session_id_from_context", "hash_session_id"]:
            from .session_id_extractor import (
                SessionState,
                extract_session_id_from_context,
                hash_session_id,
            )
            return locals()[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
