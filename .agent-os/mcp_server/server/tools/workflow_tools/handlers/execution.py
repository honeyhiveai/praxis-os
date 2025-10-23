"""
Execution action handlers for workflow tools.

Handles workflow execution operations:
- start: Start new workflow session
- get_phase: Get current phase content
- get_task: Get specific task details
- complete_phase: Complete phase with evidence validation
- get_state: Get complete workflow state
"""

import logging
from typing import Any, Dict, Optional

from ..validators import validate_evidence_size, validate_session_id, validate_target_file

logger = logging.getLogger(__name__)


async def handle_start(
    workflow_type: Optional[str] = None,
    target_file: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    workflow_engine: Optional[Any] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Handle start action.

    Starts a new workflow session with the specified workflow type and target file.
    Validates inputs and delegates to WorkflowEngine.

    Args:
        workflow_type: Workflow identifier (e.g., "test_generation_v3")
        target_file: Target file path (validated for security)
        options: Optional workflow configuration
        workflow_engine: WorkflowEngine instance (injected by dispatcher)
        **kwargs: Additional parameters (ignored)

    Returns:
        Dictionary with session info and Phase 1 content

    Raises:
        ValueError: If required parameters missing or invalid

    Examples:
        >>> result = await handle_start(
        ...     workflow_type="test_generation_v3",
        ...     target_file="src/module.py",
        ...     workflow_engine=engine
        ... )
        >>> result["status"]
        'success'
        >>> "session_id" in result
        True
    """
    # 1. Validate required parameters
    if not workflow_type:
        raise ValueError("start action requires workflow_type parameter")
    if not target_file:
        raise ValueError("start action requires target_file parameter")
    if not workflow_engine:
        raise ValueError("workflow_engine not available (internal error)")

    # 2. Validate inputs for security
    validate_target_file(target_file)

    # 3. Call WorkflowEngine to start session
    result = workflow_engine.start_workflow(
        workflow_type=workflow_type,
        target_file=target_file
    )
    # Note: options parameter not currently supported by WorkflowEngine

    # 4. Return formatted response (ensure target_file is included)
    return {
        "status": "success",
        "action": "start",
        "target_file": target_file,
        **result,
    }


async def handle_get_phase(
    session_id: Optional[str] = None,
    workflow_engine: Optional[Any] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Handle get_phase action.

    Retrieves current phase content and requirements for an active workflow session.
    Includes all task summaries and checkpoint criteria.

    Args:
        session_id: Session identifier (required, validated)
        workflow_engine: WorkflowEngine instance (injected by dispatcher)
        **kwargs: Additional parameters (ignored)

    Returns:
        Dictionary with current phase content, tasks, and checkpoint

    Raises:
        ValueError: If session_id missing, invalid, or session not found

    Examples:
        >>> result = await handle_get_phase(
        ...     session_id="550e8400-e29b-41d4-a716-446655440000",
        ...     workflow_engine=engine
        ... )
        >>> result["status"]
        'success'
        >>> "phase_content" in result
        True
    """
    # 1. Validate required parameters
    if not session_id:
        raise ValueError("get_phase action requires session_id parameter")
    if not workflow_engine:
        raise ValueError("workflow_engine not available (internal error)")

    # 2. Validate session ID format for security
    validate_session_id(session_id)

    # 3. Call WorkflowEngine to get current phase
    result = workflow_engine.get_current_phase(session_id=session_id)

    # 4. Return formatted response
    return {
        "status": "success",
        "action": "get_phase",
        **result,
    }


async def handle_get_task(
    session_id: Optional[str] = None,
    phase: Optional[int] = None,
    task_number: Optional[int] = None,
    workflow_engine: Optional[Any] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Handle get_task action.

    Retrieves detailed content for a specific task within a phase.
    Includes execution steps, commands, and acceptance criteria.

    Args:
        session_id: Session identifier (required, validated)
        phase: Phase number (required, must be positive integer)
        task_number: Task number within phase (required, must be positive integer)
        workflow_engine: WorkflowEngine instance (injected by dispatcher)
        **kwargs: Additional parameters (ignored)

    Returns:
        Dictionary with complete task content and execution steps

    Raises:
        ValueError: If required parameters missing, invalid, or task not found

    Examples:
        >>> result = await handle_get_task(
        ...     session_id="550e8400-e29b-41d4-a716-446655440000",
        ...     phase=1,
        ...     task_number=2,
        ...     workflow_engine=engine
        ... )
        >>> result["status"]
        'success'
        >>> "task_content" in result
        True
    """
    # 1. Validate required parameters
    if not session_id:
        raise ValueError("get_task action requires session_id parameter")
    if phase is None:
        raise ValueError("get_task action requires phase parameter")
    if task_number is None:
        raise ValueError("get_task action requires task_number parameter")
    if not workflow_engine:
        raise ValueError("workflow_engine not available (internal error)")

    # 2. Validate session ID format for security
    validate_session_id(session_id)

    # 3. Validate phase and task_number are positive integers
    if not isinstance(phase, int) or phase < 0:
        raise ValueError(f"phase must be a non-negative integer, got: {phase}")
    if not isinstance(task_number, int) or task_number < 1:
        raise ValueError(f"task_number must be a positive integer, got: {task_number}")

    # 4. Call WorkflowEngine to get specific task
    result = workflow_engine.get_task(
        session_id=session_id, phase=phase, task_number=task_number
    )

    # 5. Return formatted response
    return {
        "status": "success",
        "action": "get_task",
        **result,
    }


async def handle_complete_phase(
    session_id: Optional[str] = None,
    phase: Optional[int] = None,
    evidence: Optional[Dict[str, Any]] = None,
    workflow_engine: Optional[Any] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Handle complete_phase action.

    Validates evidence against checkpoint criteria and advances to next phase
    if all requirements are met. This is a critical gating function that enforces
    workflow quality standards.

    Args:
        session_id: Session identifier (required, validated)
        phase: Phase number being completed (required, must be non-negative)
        evidence: Evidence dictionary with checkpoint criteria (required, size-limited)
        workflow_engine: WorkflowEngine instance (injected by dispatcher)
        **kwargs: Additional parameters (ignored)

    Returns:
        Dictionary with checkpoint result and next phase content if passed

    Raises:
        ValueError: If required parameters missing, invalid, or checkpoint fails

    Examples:
        >>> result = await handle_complete_phase(
        ...     session_id="550e8400-e29b-41d4-a716-446655440000",
        ...     phase=1,
        ...     evidence={"tests_passing": 42, "coverage": 85.5},
        ...     workflow_engine=engine
        ... )
        >>> result["status"]
        'success'
        >>> result["checkpoint_passed"]
        True
    """
    # 1. Validate required parameters
    if not session_id:
        raise ValueError("complete_phase action requires session_id parameter")
    if phase is None:
        raise ValueError("complete_phase action requires phase parameter")
    if evidence is None:
        raise ValueError("complete_phase action requires evidence parameter")
    if not workflow_engine:
        raise ValueError("workflow_engine not available (internal error)")

    # 2. Validate session ID format for security
    validate_session_id(session_id)

    # 3. Validate phase is non-negative integer
    if not isinstance(phase, int) or phase < 0:
        raise ValueError(f"phase must be a non-negative integer, got: {phase}")

    # 4. Validate evidence is a dictionary and check size
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be a dictionary")
    validate_evidence_size(evidence)

    # 5. Call WorkflowEngine to complete phase with checkpoint validation
    result = workflow_engine.complete_phase(
        session_id=session_id, phase=phase, evidence=evidence
    )

    # 6. Return formatted response
    return {
        "status": "success",
        "action": "complete_phase",
        **result,
    }


async def handle_get_state(
    session_id: Optional[str] = None,
    workflow_engine: Optional[Any] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Handle get_state action.

    Retrieves complete workflow state for a session including progress,
    completed phases, current phase, and all artifacts.

    Args:
        session_id: Session identifier (required, validated)
        workflow_engine: WorkflowEngine instance (injected by dispatcher)
        **kwargs: Additional parameters (ignored)

    Returns:
        Dictionary with complete workflow state

    Raises:
        ValueError: If session_id missing, invalid, or session not found

    Examples:
        >>> result = await handle_get_state(
        ...     session_id="550e8400-e29b-41d4-a716-446655440000",
        ...     workflow_engine=engine
        ... )
        >>> result["status"]
        'success'
        >>> "workflow_state" in result
        True
    """
    # 1. Validate required parameters
    if not session_id:
        raise ValueError("get_state action requires session_id parameter")
    if not workflow_engine:
        raise ValueError("workflow_engine not available (internal error)")

    # 2. Validate session ID format for security
    validate_session_id(session_id)

    # 3. Call WorkflowEngine to get workflow state
    state_data = workflow_engine.get_workflow_state(session_id=session_id)

    # 4. Return formatted response (wrap state_data under workflow_state key for consistency)
    return {
        "status": "success",
        "action": "get_state",
        "workflow_state": state_data,
    }

