"""
Action handlers for consolidated workflow tool.
"""

from .discovery import handle_list_workflows
from .execution import (
    handle_complete_phase,
    handle_get_phase,
    handle_get_state,
    handle_get_task,
    handle_start,
)
from .management import (
    handle_delete_session,
    handle_get_session,
    handle_list_sessions,
)

__all__ = [
    # Discovery
    "handle_list_workflows",
    # Execution
    "handle_start",
    "handle_get_phase",
    "handle_get_task",
    "handle_complete_phase",
    "handle_get_state",
    # Management
    "handle_list_sessions",
    "handle_get_session",
    "handle_delete_session",
]

