"""
Consolidated workflow management tools.

Single unified interface for all workflow operations following aos_browser pattern.
Organized into submodules for maintainability:
- constants: Action names and validation constants
- validators: Input validation functions
- handlers/: Action handlers grouped by category
  (discovery, execution, management, recovery)
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
from .validators import (
    validate_evidence_size,
    validate_session_id,
    validate_target_file,
)

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
    # Action handlers
    "ACTION_HANDLERS",
    "handle_list_workflows",
    "handle_start",
    "handle_get_phase",
    "handle_get_task",
    "handle_complete_phase",
    "handle_get_state",
    "handle_list_sessions",
    "handle_get_session",
    "handle_delete_session",
]
