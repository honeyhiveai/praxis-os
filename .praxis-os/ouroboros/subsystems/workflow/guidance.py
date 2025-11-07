"""
Workflow task management guidance injection.

Adds explicit guidance fields to workflow responses to prevent AI assistants
from using external task management tools (like todo_write) when a workflow
is active, which would create duplicate/conflicting task tracking.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Guidance fields injected into all workflow tool responses
WORKFLOW_GUIDANCE_FIELDS = {
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": (
        "This workflow manages ALL tasks. DO NOT use todo_write or "
        "external task lists. The workflow IS your task tracker."
    ),
    "execution_model": "Complete task → Submit evidence → Advance phase",
}


def add_workflow_guidance(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inject task management guidance into workflow tool response.

    This function adds explicit guidance fields to inform AI assistants
    that the workflow system manages task state and external task tools
    (like todo_write) should not be used.

    Args:
        response: Base response dict from workflow engine

    Returns:
        Response dict with injected guidance fields (guidance fields first)

    Example:
        >>> base = {"session_id": "123", "phase": 1}
        >>> wrapped = add_workflow_guidance(base)
        >>> "⚠️_WORKFLOW_EXECUTION_MODE" in wrapped
        True
        >>> wrapped["⚠️_WORKFLOW_EXECUTION_MODE"]
        'ACTIVE'

    Note:
        - Gracefully handles non-dict inputs (returns unchanged)
        - Never raises exceptions (fail-safe design)
        - Original response fields preserved (non-invasive)
    """
    # Input validation: only process dict responses
    if not isinstance(response, dict):
        logger.debug(
            "Skipping guidance injection for non-dict response: %s",
            type(response).__name__,
        )
        return response

    try:
        # Prepend guidance fields (dict unpacking ensures guidance appears first)
        return {**WORKFLOW_GUIDANCE_FIELDS, **response}
    except Exception as e:
        # Fail-safe: return original response if injection fails
        logger.warning(
            "Failed to inject workflow guidance: %s. Returning original response.", e
        )
        return response


__all__ = [
    "WORKFLOW_GUIDANCE_FIELDS",
    "add_workflow_guidance",
]

