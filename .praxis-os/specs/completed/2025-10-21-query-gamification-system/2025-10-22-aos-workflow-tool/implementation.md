# Implementation Guide: aos_workflow Tool

**Spec Location:** `.praxis-os/specs/review/2025-10-22-aos-workflow-tool/`  
**Implementation Strategy:** Clean cutover with comprehensive testing  
**Target Completion:** 2 weeks

---

## Quick Start

This document provides detailed, step-by-step implementation guidance for the `aos_workflow` consolidated tool. Follow the phases sequentially, validate at each gate, and reference the specifications for detailed requirements.

**Before You Begin:**
1. Read `srd.md` for business requirements
2. Read `specs.md` for technical design
3. Read `tasks.md` for task breakdown
4. Set up development environment
5. Create feature branch: `git checkout -b feat/aos-workflow-tool`

---

## Development Environment Setup

### Prerequisites
```bash
# Python 3.11+
python --version  # Should be >= 3.11

# Install dependencies
pip install -r mcp_server/requirements.txt
pip install -r requirements-dev.txt  # pytest, pylint, etc.

# Verify MCP server runs
python -m mcp_server
# Expected: Server starts without errors
```

### Create Module Files
```bash
# Create module and test files
touch mcp_server/server/tools/workflow_tools.py
touch tests/server/tools/test_workflow_tools.py
touch tests/server/tools/test_workflow_tools_security.py
touch tests/server/tools/test_workflow_tools_performance.py
touch tests/integration/test_aos_workflow_e2e.py

# Verify structure
ls -la mcp_server/server/tools/
# Expected: workflow_tools.py present
```

---

## Phase 1: Foundation Implementation

### Step 1.1: Module Structure

**File:** `mcp_server/server/tools/workflow_tools.py`

```python
"""
Consolidated workflow management tool.

Provides single unified interface for all workflow operations:
- Discovery (1 action): list_workflows
- Execution (5 actions): start, get_phase, get_task, complete_phase, get_state
- Management (5 actions): list_sessions, get_session, delete_session, pause, resume
- Recovery (3 actions): retry_phase, rollback, get_errors

Follows aos_browser pattern for consistency and LLM performance.
"""

import os
import re
import json
import glob
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Agent OS imports
from mcp_server.core.workflow_engine import WorkflowEngine
from mcp_server.core.state_manager import StateManager

# MCP imports
try:
    from mcp import tool as mcp_tool
except ImportError:
    from mcp_server.lib.mcp import tool as mcp_tool

logger = logging.getLogger(__name__)

# Constants
VALID_ACTIONS = {
    "list_workflows", "start", "get_phase", "get_task", "complete_phase",
    "get_state", "list_sessions", "get_session", "delete_session",
    "pause", "resume", "retry_phase", "rollback", "get_errors"
}

MAX_EVIDENCE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_ACTIVE_SESSIONS = 100
SESSION_ID_PATTERN = r"^[a-z0-9_]+$"
STATE_DIR = ".praxis-os/state/workflows/"
```

**Test:** `tests/server/tools/test_workflow_tools.py`

```python
"""Tests for consolidated workflow tool."""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock

from mcp_server.server.tools.workflow_tools import (
    VALID_ACTIONS,
    validate_session_id,
    validate_target_file,
    validate_evidence_size,
)


class TestModule:
    """Test module structure and imports."""
    
    def test_module_imports(self):
        """Verify all required imports work."""
        from mcp_server.server.tools import workflow_tools
        assert workflow_tools is not None
    
    def test_constants_defined(self):
        """Verify constants are defined."""
        assert len(VALID_ACTIONS) == 14
        assert "list_workflows" in VALID_ACTIONS
        assert "start" in VALID_ACTIONS
```

### Step 1.2: Tool Registration Function

**Add to** `workflow_tools.py`:

```python
def register_workflow_tools(mcp_server) -> int:
    """
    Register consolidated workflow tool with MCP server.
    
    Args:
        mcp_server: MCP server instance
        
    Returns:
        Number of tools registered (always 1)
    """
    
    @mcp_server.tool()
    async def aos_workflow(
        action: str,
        
        # Session context
        session_id: Optional[str] = None,
        
        # Start workflow parameters
        workflow_type: Optional[str] = None,
        target_file: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        
        # Task retrieval parameters
        phase: Optional[int] = None,
        task_number: Optional[int] = None,
        
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
        to_phase: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Consolidated workflow management tool following aos_browser pattern.
        
        Handles all workflow operations through action-based dispatch:
        - Discovery (1 action): list_workflows
        - Execution (5 actions): start, get_phase, get_task, complete_phase, get_state
        - Management (5 actions): list_sessions, get_session, delete_session, pause, resume
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
            status: Session status filter (for list_sessions)
            reason: Reason for operation (for delete_session)
            checkpoint_note: Note for pause checkpoint (for pause)
            reset_evidence: Reset evidence flag (for retry_phase)
            to_phase: Target phase (for rollback)
        
        Returns:
            Dictionary with operation-specific results, always including:
            - status: "success" or "error"
            - action: Echo of requested action
            - Additional fields per action
        
        Examples:
            # Discovery
            result = aos_workflow(action="list_workflows")
            result = aos_workflow(action="list_workflows", category="code_generation")
            
            # Execution
            session = aos_workflow(action="start", workflow_type="test_generation_v3", target_file="test.py")
            phase = aos_workflow(action="get_phase", session_id=session["session_id"])
            
            # Management
            sessions = aos_workflow(action="list_sessions", status="active")
            aos_workflow(action="pause", session_id=session_id, checkpoint_note="Break for review")
            
            # Recovery
            aos_workflow(action="retry_phase", session_id=session_id, phase=2)
        """
        try:
            # Validate action
            if action not in VALID_ACTIONS:
                return {
                    "status": "error",
                    "action": action,
                    "error": f"Unknown action: {action}",
                    "error_type": "ValueError",
                    "valid_actions": sorted(list(VALID_ACTIONS))
                }
            
            # Get handler
            handler = ACTION_HANDLERS.get(action)
            if not handler:
                return {
                    "status": "error",
                    "action": action,
                    "error": f"Handler not implemented for action: {action}",
                    "error_type": "NotImplementedError"
                }
            
            # Call handler
            result = await handler(
                session_id=session_id,
                workflow_type=workflow_type,
                target_file=target_file,
                options=options,
                phase=phase,
                task_number=task_number,
                evidence=evidence,
                category=category,
                status=status,
                reason=reason,
                checkpoint_note=checkpoint_note,
                reset_evidence=reset_evidence,
                to_phase=to_phase
            )
            
            # Ensure action is echoed
            if "action" not in result:
                result["action"] = action
            
            return result
            
        except ValueError as e:
            return {
                "status": "error",
                "action": action,
                "error": str(e),
                "error_type": "ValueError"
            }
        except Exception as e:
            logger.error(f"Unexpected error in aos_workflow: {e}", exc_info=True)
            return {
                "status": "error",
                "action": action,
                "error": "Internal server error",
                "error_type": "RuntimeError"
            }
    
    # Return tool count
    return 1


# Action handler mapping (to be populated in later steps)
ACTION_HANDLERS = {}
```

**Test Addition:**

```python
class TestRegistration:
    """Test tool registration."""
    
    @pytest.mark.asyncio
    async def test_register_returns_one(self):
        """Verify registration returns tool count of 1."""
        mock_server = Mock()
        tool_decorator = Mock(side_effect=lambda f: f)
        mock_server.tool = Mock(return_value=tool_decorator)
        
        count = register_workflow_tools(mock_server)
        assert count == 1
        assert mock_server.tool.called
```

### Step 1.3: Action Dispatcher & Validation

**Add validation functions to** `workflow_tools.py`:

```python
def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.
    
    Args:
        session_id: Session identifier to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If session ID is invalid
    """
    if not session_id:
        raise ValueError("session_id is required")
    
    if not re.match(SESSION_ID_PATTERN, session_id):
        raise ValueError(f"Invalid session_id format: must match {SESSION_ID_PATTERN}")
    
    return True


def validate_target_file(target_file: str) -> bool:
    """
    Validate target file path to prevent directory traversal.
    
    Args:
        target_file: File path to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If path is invalid or attempts traversal
    """
    if not target_file:
        raise ValueError("target_file is required")
    
    # Normalize path
    norm_path = os.path.normpath(target_file)
    
    # Check for directory traversal
    if ".." in norm_path or norm_path.startswith("/"):
        raise ValueError("Invalid target_file: directory traversal detected")
    
    # Ensure path is within workspace
    workspace = os.getcwd()
    full_path = os.path.join(workspace, norm_path)
    
    if not full_path.startswith(workspace):
        raise ValueError("Invalid target_file: outside workspace")
    
    return True


def validate_evidence_size(evidence: Dict) -> bool:
    """
    Validate evidence size to prevent memory exhaustion.
    
    Args:
        evidence: Evidence dictionary
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If evidence is too large
    """
    if not evidence:
        return True
    
    evidence_json = json.dumps(evidence)
    size = len(evidence_json)
    
    if size > MAX_EVIDENCE_SIZE:
        raise ValueError(
            f"Evidence too large: {size} bytes (max: {MAX_EVIDENCE_SIZE})"
        )
    
    return True


def sanitize_error(error: Exception) -> Dict[str, Any]:
    """
    Sanitize error message for safe exposure to users.
    
    Args:
        error: Exception to sanitize
        
    Returns:
        Sanitized error dictionary
    """
    # Map internal exceptions to safe types
    safe_types = {
        ValueError: "ValidationError",
        KeyError: "NotFoundError",
        FileNotFoundError: "NotFoundError",
        PermissionError: "PermissionError"
    }
    
    error_type = type(error)
    safe_type = safe_types.get(error_type, "RuntimeError")
    
    # Get first line of error message only
    safe_message = str(error).split("\n")[0]
    
    # Redact file paths
    safe_message = re.sub(r"/[^\s]+/", "***/", safe_message)
    
    return {
        "error_type": safe_type,
        "error": safe_message
    }
```

**Tests for validation:**

```python
class TestValidation:
    """Test validation functions."""
    
    def test_validate_session_id_valid(self):
        """Test valid session ID."""
        assert validate_session_id("test_gen_v3_myfile_py_20251023_143022")
    
    def test_validate_session_id_invalid(self):
        """Test invalid session ID."""
        with pytest.raises(ValueError, match="Invalid session_id format"):
            validate_session_id("../../../etc/passwd")
    
    def test_validate_target_file_valid(self):
        """Test valid target file."""
        assert validate_target_file("src/myfile.py")
    
    def test_validate_target_file_traversal(self):
        """Test directory traversal protection."""
        with pytest.raises(ValueError, match="directory traversal"):
            validate_target_file("../../../etc/passwd")
        
        with pytest.raises(ValueError, match="directory traversal"):
            validate_target_file("/etc/passwd")
    
    def test_validate_evidence_size_valid(self):
        """Test valid evidence size."""
        evidence = {"test": "data"}
        assert validate_evidence_size(evidence)
    
    def test_validate_evidence_size_too_large(self):
        """Test evidence size limit."""
        large_evidence = {"data": "x" * (11 * 1024 * 1024)}  # 11 MB
        with pytest.raises(ValueError, match="too large"):
            validate_evidence_size(large_evidence)
```

**Phase 1 Checkpoint:**
```bash
# Run Phase 1 tests
pytest tests/server/tools/test_workflow_tools.py::TestModule -v
pytest tests/server/tools/test_workflow_tools.py::TestRegistration -v
pytest tests/server/tools/test_workflow_tools.py::TestValidation -v

# Expected: All tests passing
```

---

## Phase 2: Discovery & Execution Implementation

### Step 2.1: Implement list_workflows Handler

**Add to** `workflow_tools.py`:

```python
# Workflow metadata cache
_workflow_metadata_cache = None


def _load_workflow_metadata() -> List[Dict]:
    """
    Load all workflow metadata from filesystem.
    
    Returns:
        List of workflow metadata dictionaries
    """
    workflows = []
    
    # Detect workflow base paths
    workflow_dirs = []
    if os.path.exists(".praxis-os/workflows/"):
        workflow_dirs.append(".praxis-os/workflows/")
    if os.path.exists("universal/workflows/"):
        workflow_dirs.append("universal/workflows/")
    
    for base_dir in workflow_dirs:
        # Find all metadata.json files
        pattern = os.path.join(base_dir, "*/metadata.json")
        for metadata_file in glob.glob(pattern):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    workflows.append(metadata)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load {metadata_file}: {e}")
                continue
    
    return workflows


async def _handle_list_workflows(
    category: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Handle list_workflows action.
    
    Args:
        category: Optional category filter
        
    Returns:
        Dictionary with workflows list
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
        "count": len(workflows)
    }


# Register handler
ACTION_HANDLERS["list_workflows"] = _handle_list_workflows
```

**Test:**

```python
class TestListWorkflows:
    """Test list_workflows action."""
    
    @pytest.mark.asyncio
    async def test_list_workflows_success(self, mock_workflow_metadata):
        """Test listing workflows."""
        result = await _handle_list_workflows()
        
        assert result["status"] == "success"
        assert "workflows" in result
        assert result["count"] >= 0
    
    @pytest.mark.asyncio
    async def test_list_workflows_with_category(self, mock_workflow_metadata):
        """Test listing workflows with category filter."""
        result = await _handle_list_workflows(category="code_generation")
        
        assert result["status"] == "success"
        assert all(w["category"] == "code_generation" for w in result["workflows"])
```

### Step 2.2-2.6: Implement Execution Handlers

**Pattern for all execution handlers:**

```python
async def _handle_start(
    workflow_type: Optional[str] = None,
    target_file: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Handle start action."""
    # 1. Validate required parameters
    if not workflow_type:
        raise ValueError("start requires workflow_type parameter")
    if not target_file:
        raise ValueError("start requires target_file parameter")
    
    # 2. Validate inputs
    validate_target_file(target_file)
    
    # 3. Call WorkflowEngine
    workflow_engine = WorkflowEngine()
    result = workflow_engine.start_workflow(
        workflow_type=workflow_type,
        target_file=target_file,
        options=options or {}
    )
    
    # 4. Return formatted response
    return {
        "status": "success",
        "action": "start",
        **result
    }


ACTION_HANDLERS["start"] = _handle_start

# Repeat pattern for:
# - _handle_get_phase
# - _handle_get_task
# - _handle_complete_phase
# - _handle_get_state
```

**Key Implementation Notes:**

1. **Always validate required parameters first**
2. **Call appropriate WorkflowEngine or StateManager method**
3. **Handle errors and return sanitized messages**
4. **Include "status" and "action" in all responses**
5. **Add comprehensive tests for each handler**

**Phase 2 Checkpoint:**
```bash
pytest tests/server/tools/test_workflow_tools.py::TestDiscovery -v
pytest tests/server/tools/test_workflow_tools.py::TestExecution -v
# Expected: All Phase 1 + Phase 2 tests passing
```

---

## Phase 3: Management & Recovery Implementation

Follow same pattern as Phase 2, implementing handlers for:

**Management Actions:**
- `_handle_list_sessions()` → StateManager.list_sessions()
- `_handle_get_session()` → StateManager.get_session()
- `_handle_delete_session()` → StateManager.delete_session()
- `_handle_pause()` → Update state to "paused"
- `_handle_resume()` → Update state to "active"

**Recovery Actions:**
- `_handle_retry_phase()` → WorkflowEngine.retry_phase()
- `_handle_rollback()` → WorkflowEngine.rollback()
- `_handle_get_errors()` → Return errors from state

**Phase 3 Checkpoint:**
```bash
pytest tests/server/tools/test_workflow_tools.py -v
# Expected: >= 55 tests, all passing
```

---

## Phase 4: Testing & Documentation

### Security Testing Implementation

**File:** `tests/server/tools/test_workflow_tools_security.py`

```python
"""Security tests for aos_workflow tool."""

import pytest
from mcp_server.server.tools.workflow_tools import aos_workflow


class TestPathTraversal:
    """Test path traversal protection."""
    
    @pytest.mark.asyncio
    async def test_rejects_parent_directory_traversal(self):
        """Test that ../ is rejected."""
        result = await aos_workflow(
            action="start",
            workflow_type="test_gen_v3",
            target_file="../../../etc/passwd"
        )
        
        assert result["status"] == "error"
        assert "directory traversal" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_rejects_absolute_paths(self):
        """Test that absolute paths are rejected."""
        result = await aos_workflow(
            action="start",
            workflow_type="test_gen_v3",
            target_file="/etc/passwd"
        )
        
        assert result["status"] == "error"
        assert "directory traversal" in result["error"].lower()


class TestResourceLimits:
    """Test resource limit enforcement."""
    
    @pytest.mark.asyncio
    async def test_evidence_size_limit(self, mock_session):
        """Test that oversized evidence is rejected."""
        large_evidence = {"data": "x" * (11 * 1024 * 1024)}  # 11 MB
        
        result = await aos_workflow(
            action="complete_phase",
            session_id=mock_session["session_id"],
            phase=1,
            evidence=large_evidence
        )
        
        assert result["status"] == "error"
        assert "too large" in result["error"].lower()
```

### Performance Testing Implementation

**File:** `tests/server/tools/test_workflow_tools_performance.py`

```python
"""Performance tests for aos_workflow tool."""

import pytest
import time
from mcp_server.server.tools.workflow_tools import aos_workflow


class TestResponseTimes:
    """Test response time targets."""
    
    @pytest.mark.asyncio
    async def test_list_workflows_under_100ms(self):
        """Test that list_workflows responds in < 100ms."""
        start = time.time()
        result = await aos_workflow(action="list_workflows")
        elapsed = time.time() - start
        
        assert elapsed < 0.1, f"list_workflows took {elapsed*1000:.1f}ms (target: < 100ms)"
        assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_start_under_500ms(self):
        """Test that start responds in < 500ms."""
        start = time.time()
        result = await aos_workflow(
            action="start",
            workflow_type="test_generation_v3",
            target_file="test.py"
        )
        elapsed = time.time() - start
        
        assert elapsed < 0.5, f"start took {elapsed*1000:.1f}ms (target: < 500ms)"
```

**Phase 4 Checkpoint:**
```bash
pytest tests/ -v --cov=mcp_server.server.tools.workflow_tools
# Expected: >= 85 tests, >= 90% coverage
```

---

## Phase 5: Deployment

### Step 5.1: Integration with MCP Server

**Update** `mcp_server/server/__init__.py`:

```python
from mcp_server.server.tools.workflow_tools import register_workflow_tools

def setup_server(mcp_server):
    """Register all MCP tools."""
    tool_count = 0
    
    # Register workflow tools
    tool_count += register_workflow_tools(mcp_server)
    
    # Register other tools...
    
    logger.info(f"Registered {tool_count} MCP tools")
    return tool_count
```

### Step 5.2: Clean Cutover Script

**Create** `scripts/cutover_to_aos_workflow.py`:

```python
"""
Clean cutover script: Remove old workflow tools, deploy aos_workflow.

This script performs a clean cutover by:
1. Backing up current tool registry
2. Removing old fragmented workflow tools
3. Verifying aos_workflow is registered
4. Validating tool count reduction
"""

import sys
import logging
from mcp_server.server.tools import workflow_tools

# Tools to remove
OLD_WORKFLOW_TOOLS = [
    "start_workflow",
    "get_current_phase",
    "get_task",
    "complete_phase",
    "get_workflow_state",
    # ... any other fragmented workflow tools
]

def execute_cutover():
    """Execute clean cutover."""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting clean cutover to aos_workflow")
    
    # 1. Verify aos_workflow is available
    try:
        from mcp_server.server.tools.workflow_tools import register_workflow_tools
        logger.info("✓ aos_workflow module available")
    except ImportError as e:
        logger.error(f"✗ Failed to import aos_workflow: {e}")
        return False
    
    # 2. Remove old tool registrations
    logger.info(f"Removing {len(OLD_WORKFLOW_TOOLS)} old workflow tools")
    for tool_name in OLD_WORKFLOW_TOOLS:
        logger.info(f"  - Removing {tool_name}")
        # Tool removal logic here
    
    # 3. Verify new tool registered
    logger.info("Verifying aos_workflow registration")
    # Verification logic here
    
    logger.info("✓ Clean cutover complete")
    return True

if __name__ == "__main__":
    success = execute_cutover()
    sys.exit(0 if success else 1)
```

### Step 5.3: Post-Deployment Validation

**Create** `scripts/validate_aos_workflow.py`:

```python
"""
Post-deployment validation script.

Tests all 14 actions in production environment.
"""

import asyncio
import sys
from mcp_server.server.tools.workflow_tools import aos_workflow


async def validate_discovery():
    """Validate discovery actions."""
    print("Testing discovery actions...")
    
    # Test list_workflows
    result = await aos_workflow(action="list_workflows")
    assert result["status"] == "success", "list_workflows failed"
    assert result["count"] >= 2, "Expected at least 2 workflows"
    print("  ✓ list_workflows")


async def validate_execution():
    """Validate execution actions."""
    print("Testing execution actions...")
    
    # Test start
    result = await aos_workflow(
        action="start",
        workflow_type="test_generation_v3",
        target_file="validation_test.py"
    )
    assert result["status"] == "success", "start failed"
    session_id = result["session_id"]
    print("  ✓ start")
    
    # Test get_phase
    result = await aos_workflow(action="get_phase", session_id=session_id)
    assert result["status"] == "success", "get_phase failed"
    print("  ✓ get_phase")
    
    # ... test remaining actions
    
    return session_id


async def main():
    """Run all validations."""
    print("=" * 60)
    print("aos_workflow Production Validation")
    print("=" * 60)
    
    try:
        await validate_discovery()
        session_id = await validate_execution()
        # await validate_management()
        # await validate_recovery()
        
        print("\n✓ All validations passed!")
        return True
    except Exception as e:
        print(f"\n✗ Validation failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
```

**Run validation:**
```bash
python scripts/validate_aos_workflow.py
# Expected: All checks pass
```

---

## Troubleshooting Guide

### Issue: "Unknown action" error

**Symptom:**
```json
{"status": "error", "error": "Unknown action: my_action"}
```

**Solution:**
1. Verify action is in `VALID_ACTIONS` set
2. Verify action is in `ACTION_HANDLERS` dict
3. Check spelling and case (actions are lowercase with underscores)

### Issue: "Handler not implemented" error

**Symptom:**
```json
{"status": "error", "error": "Handler not implemented for action: start"}
```

**Solution:**
1. Verify handler function exists (`_handle_start`)
2. Verify handler is registered in `ACTION_HANDLERS`
3. Check handler function signature

### Issue: Performance targets not met

**Symptom:** Tests failing with "took XXXms (target: < 100ms)"

**Solution:**
1. Check if metadata cache is working (`_workflow_metadata_cache`)
2. Profile slow operations with `cProfile`
3. Add more aggressive caching if needed
4. Check for N+1 query patterns in state loading

### Issue: Concurrency errors in production

**Symptom:** State corruption or "Session modified by another operation" errors

**Solution:**
1. Verify file locking is implemented (`with_session_lock`)
2. Check for race conditions in state updates
3. Enable optimistic locking if file locking insufficient
4. Add session-level mutex if needed

---

## Best Practices

### Code Organization
- Keep handlers focused and single-purpose
- Extract common validation logic into helper functions
- Use type hints consistently
- Add docstrings to all public functions

### Error Handling
- Always sanitize errors before returning to users
- Log full error details internally
- Provide remediation guidance in error messages
- Use specific error types (ValueError, NotFoundError, etc.)

### Testing
- Test happy path and error cases for every action
- Use pytest fixtures for common setup
- Mock external dependencies (WorkflowEngine, StateManager)
- Aim for >= 90% test coverage

### Performance
- Cache workflow metadata aggressively
- Use lazy loading for heavy operations
- Profile performance-critical paths
- Monitor performance metrics in production

### Security
- Validate all user inputs
- Never trust file paths from users
- Enforce resource limits (evidence size, session count)
- Log security-relevant events

---

## Rollback Plan

If issues are discovered post-deployment:

1. **Immediate Rollback:**
   ```bash
   git revert <commit-hash>
   git push
   # Redeploy previous version
   ```

2. **Restore Old Tools:**
   - Restore old tool registration functions
   - Verify old tools working
   - Remove aos_workflow registration

3. **Root Cause Analysis:**
   - Review logs for error patterns
   - Identify failed actions
   - Reproduce issue in development
   - Fix and re-test before re-deployment

---

## Success Metrics

Monitor these metrics post-deployment:

**Performance Metrics:**
- `list_workflows` latency: target < 100ms, alert if > 200ms
- `start` latency: target < 500ms, alert if > 1s
- Memory usage: target < 50MB, alert if > 100MB

**Reliability Metrics:**
- Error rate: target < 1%, alert if > 5%
- Success rate: target > 99%
- Uptime: target 99.9%

**Usage Metrics:**
- Total workflow executions per day
- Most common actions (track top 5)
- Average session duration

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-23  
**Status:** Ready for Implementation

