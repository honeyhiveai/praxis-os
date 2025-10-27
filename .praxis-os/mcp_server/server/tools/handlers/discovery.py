"""
Discovery action handlers for workflow tools.

Handles workflow discovery operations:
- list_workflows: List available workflows with optional filtering
"""

# pylint: disable=global-statement
# Justification: Module-level cache for workflow metadata provides significant
# performance benefit (avoids filesystem scan on every list_workflows call).
# Global is appropriate here as cache is module-scoped and thread-safe via GIL.
# Tests that need to clear cache can import this module directly.

import glob
import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Workflow metadata cache
_workflow_metadata_cache: Optional[list] = None


def _load_workflow_metadata() -> list:
    """
    Load all workflow metadata from filesystem.

    Scans ONLY installed workflows in .praxis-os/workflows/. The MCP server
    runs from .praxis-os/ installation and should never read from skeleton
    source code (universal/workflows/).

    Returns:
        List of workflow metadata dictionaries

    Raises:
        None - Errors are logged and skipped to return partial results

        Examples:
        >>> workflows = _load_workflow_metadata()
        >>> len(workflows) > 0
        True
    """
    workflows: list = []

    # ONLY read from installed workflows in .praxis-os/
    # The skeleton (universal/workflows/) is source code, not runtime
    workflow_base = ".praxis-os/workflows/"

    if not os.path.exists(workflow_base):
        logger.warning("Workflow directory not found: %s", workflow_base)
        return workflows

    # Find all metadata.json files
    pattern = os.path.join(workflow_base, "*/metadata.json")
    for metadata_file in glob.glob(pattern):
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                workflows.append(metadata)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Failed to load %s: %s", metadata_file, e)
            continue

    return workflows


async def handle_list_workflows(category: Optional[str] = None) -> Dict[str, Any]:
    """
    Handle list_workflows action.

    Lists all available workflows with optional category filtering.
    Caches metadata for performance.

    Args:
        category: Optional category filter (e.g., "code_generation", "testing")

    Returns:
        Dictionary with workflows list and count

    Examples:
        >>> result = await handle_list_workflows()
        >>> result["status"]
        'success'
        >>> result = await handle_list_workflows(category="testing")
        >>> all(w["category"] == "testing" for w in result["workflows"])
        True
    """
    global _workflow_metadata_cache

    # Load metadata (cached)
    if _workflow_metadata_cache is None:
        _workflow_metadata_cache = _load_workflow_metadata()

    workflows = _workflow_metadata_cache

    # Apply category filter if provided
    if category:
        workflows = [w for w in workflows if w.get("category") == category]

    return {
        "status": "success",
        "action": "list_workflows",
        "workflows": workflows,
        "count": len(workflows),
    }
