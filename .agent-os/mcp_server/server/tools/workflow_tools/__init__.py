"""
Consolidated workflow management tools.

Single unified interface for all workflow operations following aos_browser pattern.
Organized into submodules for maintainability:
- constants: Action names and validation constants
- validators: Input validation functions
- handlers/: Action handlers grouped by category (discovery, execution, management, recovery)
- dispatcher: Main aos_workflow tool with action routing
"""

from .constants import MAX_EVIDENCE_SIZE, SESSION_ID_PATTERN, VALID_ACTIONS
from .dispatcher import ACTION_HANDLERS, register_workflow_tools
from .handlers import (
    handle_complete_phase,
    handle_delete_session,
    handle_get_phase,
    handle_get_session,
    handle_get_state,
    handle_get_task,
    handle_list_sessions,
    handle_list_workflows,
    handle_start,
)

# Import discovery module for cache access in tests
from .handlers import discovery as _discovery_module

from .validators import (
    validate_evidence_size,
    validate_session_id,
    validate_target_file,
)

# Aliases for backward compatibility with tests
_handle_list_workflows = handle_list_workflows
_handle_start = handle_start
_handle_get_phase = handle_get_phase
_handle_get_task = handle_get_task
_handle_complete_phase = handle_complete_phase
_handle_get_state = handle_get_state
_handle_list_sessions = handle_list_sessions
_handle_get_session = handle_get_session
_handle_delete_session = handle_delete_session


# Property-based access to cache for testing
def _get_cache():
    return _discovery_module._workflow_metadata_cache


def _set_cache(value):
    _discovery_module._workflow_metadata_cache = value


# For backward compatibility: tests can read/write _workflow_metadata_cache
__all__ = [
    # Main registration
    "register_workflow_tools",
    # Constants
    "VALID_ACTIONS",
    "MAX_EVIDENCE_SIZE",
    "SESSION_ID_PATTERN",
    # Validators
    "validate_session_id",
    "validate_target_file",
    "validate_evidence_size",
    # Action handlers (for testing)
    "ACTION_HANDLERS",
    # Handlers (new names)
    "handle_list_workflows",
    "handle_start",
    "handle_get_phase",
    "handle_get_task",
    "handle_complete_phase",
    "handle_get_state",
    "handle_list_sessions",
    "handle_get_session",
    "handle_delete_session",
    # Handlers (old names with underscore - for backward compatibility)
    "_handle_list_workflows",
    "_handle_start",
    "_handle_get_phase",
    "_handle_get_task",
    "_handle_complete_phase",
    "_handle_get_state",
    "_handle_list_sessions",
    "_handle_get_session",
    "_handle_delete_session",
    # Discovery module (for cache access in tests)
    "_discovery_module",
]
