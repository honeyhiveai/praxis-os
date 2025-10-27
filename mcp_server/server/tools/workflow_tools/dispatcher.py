"""
Action dispatcher for consolidated workflow tool.

Provides the main pos_workflow tool that routes actions to specific handlers.
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
# Justification: pos_workflow is the main MCP tool function with 14 parameters
# (required by FastMCP signature pattern for action dispatch), 17 local variables
# for parameter validation and routing. This is intentional design following
# pos_browser pattern where a single consolidated tool provides all workflow
# operations. Alternative would be 14 separate MCP tools which degrades LLM
# performance (research shows 85% drop with >20 tools).

# pylint: disable=broad-exception-caught
# Justification: Top-level MCP tool must catch all exceptions to return
# structured error responses to LLM. Specific exceptions re-raised after logging.
# Alternative (narrow catching) would crash tool and break AI workflows.

import inspect
import logging
from typing import Any, Dict, Optional, Union

from .constants import VALID_ACTIONS
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

logger = logging.getLogger(__name__)

# Action handler mapping
ACTION_HANDLERS: Dict[str, Any] = {
    # Discovery
    "list_workflows": handle_list_workflows,
    # Execution
    "start": handle_start,
    "get_phase": handle_get_phase,
    "get_task": handle_get_task,
    "complete_phase": handle_complete_phase,
    "get_state": handle_get_state,
    # Management
    "list_sessions": handle_list_sessions,
    "get_session": handle_get_session,
    "delete_session": handle_delete_session,
    # Recovery (Phase 3 - to be implemented)
    # "pause": handle_pause,
    # "resume": handle_resume,
    # "retry_phase": handle_retry_phase,
    # "rollback": handle_rollback,
    # "get_errors": handle_get_errors,
}


def register_workflow_tools(
    mcp: Any,
    workflow_engine: Any,
    framework_generator: Any,
    workflow_validator: Any,
) -> int:
    """
    Register consolidated workflow tool with MCP server.

    Registers a single pos_workflow tool that provides all workflow operations
    through action-based dispatch, following the pos_browser pattern for
    optimal LLM performance.

    :param mcp: FastMCP server instance
    :param workflow_engine: WorkflowEngine instance for workflow operations
    :param framework_generator: FrameworkGenerator instance (for future use)
    :param workflow_validator: WorkflowValidator class (for future use)
    :return: Number of tools registered (always 1)

    Traceability:
        FR-001 (Single consolidated tool)
        NFR-P1 (LLM performance - action dispatch pattern)
    """

    @mcp.tool()
    async def pos_workflow(
        action: str,
        # Session context
        session_id: Optional[str] = None,
        # Start workflow parameters
        workflow_type: Optional[str] = None,
        target_file: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        # Task retrieval parameters (Union to handle JSON number serialization)
        phase: Union[int, float, None] = None,
        task_number: Union[int, float, None] = None,
        # Phase completion parameters
        evidence: Optional[Dict[str, Any]] = None,
        # Discovery parameters
        category: Optional[str] = None,
        # Session management parameters
        status: Optional[str] = None,
        reason: Optional[str] = None,
        checkpoint_note: Optional[str] = None,
        # Recovery parameters
        reset_evidence: Optional[bool] = False,
        to_phase: Union[int, float, None] = None,
    ) -> Dict[str, Any]:
        """
        Consolidated workflow management tool following pos_browser pattern.

        Handles all workflow operations through action-based dispatch:
        - Discovery (1 action): list_workflows
        - Execution (5 actions): start, get_phase, get_task, complete_phase,
          get_state
        - Management (5 actions): list_sessions, get_session, delete_session,
          pause, resume
        - Recovery (3 actions): retry_phase, rollback, get_errors

        Args:
            action: Operation to perform (required)
            session_id: Session identifier (required for most operations)
            workflow_type: Workflow type identifier (required for start)
            target_file: Target file path (required for start)
            options: Optional workflow configuration (for start)
            phase: Phase number (for complete_phase, retry_phase)
            task_number: Task number (for get_task)
            evidence: Evidence dictionary (for complete_phase)
            category: Workflow category filter (for list_workflows)
            status: Session status (for list_sessions filter)
            reason: Pause/resume reason (for pause, resume)
            checkpoint_note: Note for pause checkpoint (for pause)
            reset_evidence: Reset evidence on retry (for retry_phase)
            to_phase: Target phase for rollback (for rollback)

        Returns:
            Dictionary with operation results and status

        Raises:
            ValueError: If action is invalid or required parameters missing
        """
        try:
            # Validate action
            if action not in VALID_ACTIONS:
                return {
                    "status": "error",
                    "action": action,
                    "error": f"Unknown action: {action}",
                    "error_type": "ValueError",
                    "valid_actions": sorted(list(VALID_ACTIONS)),
                    "remediation": (
                        f"Action must be one of: {', '.join(sorted(VALID_ACTIONS))}. "
                        "See tool documentation for action descriptions."
                    ),
                }

            # Get handler
            handler = ACTION_HANDLERS.get(action)
            if not handler:
                return {
                    "status": "error",
                    "action": action,
                    "error": f"Handler not implemented for action: {action}",
                    "error_type": "NotImplementedError",
                    "remediation": "Action handlers will be implemented in Phase 3",
                }

            # Type coercion for numeric parameters
            # (MCP sends JSON numbers, we need Python ints)
            if phase is not None:
                phase = int(phase)
            if task_number is not None:
                task_number = int(task_number)
            if to_phase is not None:
                to_phase = int(to_phase)

            # Build parameter dict with all possible parameters
            all_params = {
                "session_id": session_id,
                "workflow_type": workflow_type,
                "target_file": target_file,
                "options": options,
                "phase": phase,
                "task_number": task_number,
                "evidence": evidence,
                "category": category,
                "status": status,
                "reason": reason,
                "checkpoint_note": checkpoint_note,
                "reset_evidence": reset_evidence,
                "to_phase": to_phase,
                # Injected dependencies from outer scope
                "workflow_engine": workflow_engine,
                "framework_generator": framework_generator,
                "workflow_validator": workflow_validator,
            }

            # Introspect handler signature and only pass parameters it accepts
            sig = inspect.signature(handler)
            handler_params = {
                name: all_params[name]
                for name in sig.parameters.keys()
                if name in all_params
            }

            # Call handler with only the parameters it accepts
            result = await handler(**handler_params)

            # Ensure action is echoed in result
            if "action" not in result:
                result["action"] = action

            return result  # type: ignore[no-any-return]

        except ValueError as e:
            logger.warning("ValueError in pos_workflow: %s", e)
            return {
                "status": "error",
                "action": action,
                "error": str(e),
                "error_type": "ValueError",
            }
        except Exception as e:
            logger.error("Unexpected error in pos_workflow: %s", e, exc_info=True)
            return {
                "status": "error",
                "action": action,
                "error": "Internal server error",
                "error_type": "RuntimeError",
                "remediation": "Check server logs for detailed error information",
            }

    logger.info("✅ Registered consolidated pos_workflow tool (14 actions)")
    return 1  # One tool registered
