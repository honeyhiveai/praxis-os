"""
Management action handlers for workflow tools.

Handles session management operations:
- list_sessions: List all sessions with optional status filtering
- get_session: Get detailed session information
- delete_session: Delete a session and cleanup state
"""

# pylint: disable=too-many-branches
# Justification: handle_list_sessions has 13 branches (1 over limit) for status
# validation, WorkflowState vs dict handling (test compatibility), status computation
# (complete/paused/active/error), and status filtering. Refactoring would fragment
# cohesive session listing logic across multiple functions for minimal gain.

import logging
from typing import Any, Dict, Optional

from ..validators import validate_session_id

logger = logging.getLogger(__name__)


async def handle_list_sessions(
    status: Optional[str] = None, workflow_engine: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Handle list_sessions action.

    Lists all workflow sessions with optional status filtering.
    Uses StateManager for session discovery and management.

    Args:
        status: Optional status filter ("active", "paused", "completed", "error")
        workflow_engine: WorkflowEngine instance (injected, has state_manager)

    Returns:
        Dictionary with sessions list and count

    Raises:
        ValueError: If status filter is invalid

    Examples:
        >>> result = await handle_list_sessions(workflow_engine=engine)
        >>> result["status"]
        'success'
        >>> "sessions" in result
        True
        >>> result = await handle_list_sessions(status="active", workflow_engine=engine)
        >>> all(s["status"] == "active" for s in result["sessions"])
        True
    """
    # 1. Validate workflow_engine available
    if not workflow_engine:
        raise ValueError("workflow_engine not available (internal error)")

    # 2. Validate status filter if provided
    valid_statuses = {"active", "paused", "completed", "error"}
    if status and status not in valid_statuses:
        raise ValueError(
            f"Invalid status filter: {status}. "
            f"Must be one of: {', '.join(sorted(valid_statuses))}"
        )

    # 3. Get StateManager from WorkflowEngine and list sessions
    state_manager = workflow_engine.state_manager

    # Map status filter to StateManager parameters
    active_only = (status == "active") if status else False

    # Get all sessions (StateManager returns List[WorkflowState] objects)
    session_objects = state_manager.list_sessions(active_only=active_only)

    # Convert WorkflowState objects (or dicts from tests) to dictionaries
    sessions = []
    for session_obj in session_objects:
        # Handle both WorkflowState objects and dictionaries (for testing)
        if isinstance(session_obj, dict):
            # Already a dictionary (from test mocks)
            session_dict = session_obj.copy()
            # Ensure session_status exists (tests may use 'status')
            if "status" in session_dict and "session_status" not in session_dict:
                session_dict["session_status"] = session_dict.pop("status")
        else:
            # WorkflowState object - compute status
            if session_obj.is_complete():
                computed_status = "completed"
            elif session_obj.metadata.get("paused", False):
                computed_status = "paused"
            elif any(
                checkpoint_status.value == "failed"
                for checkpoint_status in session_obj.checkpoints.values()
            ):
                computed_status = "error"
            else:
                computed_status = "active"

            session_dict = {
                "session_id": session_obj.session_id,
                "workflow_type": session_obj.workflow_type,
                "session_status": computed_status,
                "current_phase": session_obj.current_phase,
                "created_at": (
                    session_obj.created_at.isoformat()
                    if hasattr(session_obj.created_at, "isoformat")
                    else str(session_obj.created_at)
                ),
                "updated_at": (
                    session_obj.updated_at.isoformat()
                    if hasattr(session_obj.updated_at, "isoformat")
                    else str(session_obj.updated_at)
                ),
            }

        # Apply status filter if provided
        if status:
            if session_dict.get("session_status") == status:
                sessions.append(session_dict)
        else:
            sessions.append(session_dict)

    # 4. Return formatted response
    return {
        "status": "success",
        "action": "list_sessions",
        "sessions": sessions,
        "count": len(sessions),
    }


async def handle_get_session(
    session_id: Optional[str] = None, workflow_engine: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Handle get_session action.

    Retrieves detailed information about a specific workflow session
    including metadata, progress, and configuration.

    Args:
        session_id: Session identifier (required, validated)
        workflow_engine: WorkflowEngine instance (injected, has state_manager)

    Returns:
        Dictionary with session details

    Raises:
        ValueError: If session_id missing, invalid, or session not found

    Examples:
        >>> result = await handle_get_session(
        ...     session_id="550e8400-e29b-41d4-a716-446655440000",
        ...     workflow_engine=engine
        ... )
        >>> result["status"]
        'success'
        >>> "session_info" in result
        True
    """
    # 1. Validate required parameters
    if not session_id:
        raise ValueError("get_session action requires session_id parameter")
    if not workflow_engine:
        raise ValueError("workflow_engine not available (internal error)")

    # 2. Validate session ID format for security
    validate_session_id(session_id)

    # 3. Get StateManager from WorkflowEngine and load session state
    state_manager = workflow_engine.state_manager
    workflow_state = state_manager.load_state(session_id=session_id)

    if not workflow_state:
        raise ValueError(f"Session not found: {session_id}")

    # 4. Convert WorkflowState object (or dict from tests) to dictionary
    if isinstance(workflow_state, dict):
        # Already a dictionary (from test mocks)
        session_info = workflow_state.copy()
        # Ensure session_status exists
        if "status" in session_info and "session_status" not in session_info:
            session_info["session_status"] = session_info.pop("status")
    else:
        # WorkflowState object - compute status and convert
        if workflow_state.is_complete():
            computed_status = "completed"
        elif workflow_state.metadata.get("paused", False):
            computed_status = "paused"
        elif any(
            checkpoint_status.value == "failed"
            for checkpoint_status in workflow_state.checkpoints.values()
        ):
            computed_status = "error"
        else:
            computed_status = "active"

        session_info = {
            "session_id": workflow_state.session_id,
            "workflow_type": workflow_state.workflow_type,
            "session_status": computed_status,
            "current_phase": workflow_state.current_phase,
            "target_file": workflow_state.target_file,
            "created_at": (
                workflow_state.created_at.isoformat()
                if hasattr(workflow_state.created_at, "isoformat")
                else str(workflow_state.created_at)
            ),
            "updated_at": (
                workflow_state.updated_at.isoformat()
                if hasattr(workflow_state.updated_at, "isoformat")
                else str(workflow_state.updated_at)
            ),
            "checkpoints": {
                phase: checkpoint_status.value
                for phase, checkpoint_status in workflow_state.checkpoints.items()
            },
            "artifacts": {
                phase: artifact.to_dict()
                for phase, artifact in workflow_state.phase_artifacts.items()
            },
        }

    # 5. Return formatted response
    return {
        "status": "success",
        "action": "get_session",
        **session_info,
    }


async def handle_delete_session(
    session_id: Optional[str] = None, workflow_engine: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Handle delete_session action.

    Deletes a workflow session and cleans up associated state files.
    This operation is irreversible and should be used with caution.

    Args:
        session_id: Session identifier (required, validated)
        workflow_engine: WorkflowEngine instance (injected, has state_manager)

    Returns:
        Dictionary confirming deletion

    Raises:
        ValueError: If session_id missing, invalid, or session not found

    Examples:
        >>> result = await handle_delete_session(
        ...     session_id="550e8400-e29b-41d4-a716-446655440000",
        ...     workflow_engine=engine
        ... )
        >>> result["status"]
        'success'
        >>> result["deleted"]
        True
    """
    # 1. Validate required parameters
    if not session_id:
        raise ValueError("delete_session action requires session_id parameter")
    if not workflow_engine:
        raise ValueError("workflow_engine not available (internal error)")

    # 2. Validate session ID format for security
    validate_session_id(session_id)

    # 3. Get StateManager from WorkflowEngine and delete session
    state_manager = workflow_engine.state_manager
    state_manager.delete_session(session_id=session_id)

    # 4. Return formatted response
    return {
        "status": "success",
        "action": "delete_session",
        "session_id": session_id,
        "deleted": True,
    }
