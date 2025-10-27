# Implementation Guide

**Project:** Workflow Task Management Guidance  
**Date:** 2025-10-08  
**For:** Developers implementing this feature

---

## 1. Code Patterns

### 1.1 Guidance Wrapper Function Pattern

**File:** `mcp_server/workflow_engine.py`

**Pattern: Pure Function Decorator**

```python
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Define guidance fields as module-level constant
WORKFLOW_GUIDANCE_FIELDS = {
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": (
        "This workflow manages ALL tasks. DO NOT use todo_write or "
        "external task lists. The workflow IS your task tracker."
    ),
    "execution_model": "Complete task → Submit evidence → Advance phase"
}


def add_workflow_guidance(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inject task management guidance into workflow tool response.
    
    This decorator adds explicit guidance fields to inform AI assistants
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
            f"Skipping guidance injection for non-dict response: "
            f"{type(response).__name__}"
        )
        return response
    
    try:
        # Prepend guidance fields (dict unpacking ensures guidance appears first)
        return {**WORKFLOW_GUIDANCE_FIELDS, **response}
    except Exception as e:
        # Fail-safe: return original response if injection fails
        logger.warning(
            f"Failed to inject workflow guidance: {e}. "
            f"Returning original response."
        )
        return response
```

**Why This Pattern:**
- ✅ Stateless: No side effects, thread-safe, scales horizontally
- ✅ Fail-safe: Never breaks workflow operations if guidance fails
- ✅ Pure function: Same input always produces same output
- ✅ Type-safe: Type hints enable static analysis
- ✅ Testable: Easy to unit test in isolation

---

### 1.2 Integration Pattern: Method Wrapping

**File:** `mcp_server/workflow_engine.py` (WorkflowEngine class)

**Pattern: Apply decorator before return**

```python
class WorkflowEngine:
    """Manages workflow sessions and phase progression."""
    
    def __init__(self, rag_engine, state_manager):
        self.rag_engine = rag_engine
        self.state_manager = state_manager
    
    def start_workflow(
        self, 
        workflow_type: str, 
        target_file: str, 
        options: Dict = None
    ) -> Dict:
        """Start a new workflow session."""
        # Existing logic (unchanged)
        session = self._create_session(workflow_type, target_file, options)
        response = self._build_start_response(session)
        
        # ⭐ NEW: Apply guidance wrapper before return
        return add_workflow_guidance(response)
    
    def get_current_phase(self, session_id: str) -> Dict:
        """Get current phase content."""
        # Existing logic (unchanged)
        phase_data = self._load_phase_content(session_id)
        response = self._build_phase_response(phase_data)
        
        # ⭐ NEW: Apply guidance wrapper
        return add_workflow_guidance(response)
    
    def get_task(
        self, 
        session_id: str, 
        phase: int, 
        task_number: int
    ) -> Dict:
        """Get specific task content."""
        # Existing logic (unchanged)
        task_data = self._load_task_content(session_id, phase, task_number)
        response = self._build_task_response(task_data)
        
        # ⭐ NEW: Apply guidance wrapper
        return add_workflow_guidance(response)
    
    def complete_phase(
        self, 
        session_id: str, 
        phase: int, 
        evidence: Dict
    ) -> Dict:
        """Validate checkpoint and advance phase."""
        # Existing logic (unchanged)
        validation_result = self._validate_and_advance(
            session_id, phase, evidence
        )
        response = self._build_checkpoint_response(validation_result)
        
        # ⭐ NEW: Apply guidance wrapper
        return add_workflow_guidance(response)
    
    def get_workflow_state(self, session_id: str) -> Dict:
        """Get complete workflow state."""
        # Existing logic (unchanged)
        state = self.state_manager.load_state(session_id)
        response = self._build_state_response(state)
        
        # ⭐ NEW: Apply guidance wrapper
        return add_workflow_guidance(response)
```

**Integration Checklist:**
- [ ] Import `add_workflow_guidance` at top of file
- [ ] Add wrapper call before each return statement
- [ ] NO changes to method signatures
- [ ] NO changes to core logic
- [ ] Total changes: ~5 lines (one per method)

---

### 1.3 Anti-Patterns (What NOT to Do)

❌ **BAD: Modifying response in-place**
```python
def add_workflow_guidance(response):
    response["⚠️_WORKFLOW_EXECUTION_MODE"] = "ACTIVE"  # Mutates input!
    return response
```
**Why bad:** Mutates input, side effects, breaks immutability principle

✅ **GOOD: Creating new dict**
```python
def add_workflow_guidance(response):
    return {**WORKFLOW_GUIDANCE_FIELDS, **response}  # New dict
```

---

❌ **BAD: Raising exceptions**
```python
def add_workflow_guidance(response):
    if not isinstance(response, dict):
        raise TypeError("Response must be dict")  # Breaks workflow!
```
**Why bad:** Breaks workflow operations if guidance fails

✅ **GOOD: Graceful degradation**
```python
def add_workflow_guidance(response):
    if not isinstance(response, dict):
        return response  # Return unchanged
```

---

❌ **BAD: Workflow-specific logic**
```python
def add_workflow_guidance(response):
    if response.get("workflow_type") == "spec_creation_v1":
        message = "Custom message for spec creation"
    ...
```
**Why bad:** Adds complexity, violates FR-4 (universal coverage)

✅ **GOOD: Universal guidance**
```python
WORKFLOW_GUIDANCE_FIELDS = {  # Same for all workflows
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    ...
}
```

---

## 2. Testing Strategy

### 2.1 Unit Tests

**File:** `tests/unit/test_workflow_guidance.py`

**Pattern: Test pure function in isolation**

```python
import pytest
from mcp_server.workflow_engine import (
    add_workflow_guidance,
    WORKFLOW_GUIDANCE_FIELDS
)


class TestWorkflowGuidance:
    """Unit tests for workflow guidance wrapper function."""
    
    def test_add_guidance_to_valid_dict(self):
        """Test normal case: guidance added to valid dict response."""
        base_response = {
            "session_id": "test-123",
            "workflow_type": "spec_creation_v1",
            "phase": 1
        }
        
        result = add_workflow_guidance(base_response)
        
        # Guidance fields added
        assert "⚠️_WORKFLOW_EXECUTION_MODE" in result
        assert result["⚠️_WORKFLOW_EXECUTION_MODE"] == "ACTIVE"
        assert "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS" in result
        assert "execution_model" in result
        
        # Original fields preserved
        assert result["session_id"] == "test-123"
        assert result["workflow_type"] == "spec_creation_v1"
        assert result["phase"] == 1
    
    def test_add_guidance_preserves_original_fields(self):
        """Test non-invasive: original fields unchanged."""
        base_response = {"key1": "value1", "key2": "value2"}
        
        result = add_workflow_guidance(base_response)
        
        assert result["key1"] == "value1"
        assert result["key2"] == "value2"
        assert len(result) == len(base_response) + 3  # +3 guidance fields
    
    def test_add_guidance_with_non_dict_input(self):
        """Test graceful degradation: non-dict returned unchanged."""
        # String input
        result = add_workflow_guidance("not a dict")
        assert result == "not a dict"
        
        # None input
        result = add_workflow_guidance(None)
        assert result is None
        
        # List input
        result = add_workflow_guidance([1, 2, 3])
        assert result == [1, 2, 3]
    
    def test_guidance_fields_appear_first(self):
        """Test field ordering: guidance fields first in dict."""
        base_response = {"session_id": "123", "phase": 1}
        
        result = add_workflow_guidance(base_response)
        keys = list(result.keys())
        
        # First 3 keys are guidance fields
        assert keys[0] == "⚠️_WORKFLOW_EXECUTION_MODE"
        assert keys[1] == "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS"
        assert keys[2] == "execution_model"
    
    def test_guidance_field_values(self):
        """Test field values match expected constants."""
        result = add_workflow_guidance({})
        
        assert result["⚠️_WORKFLOW_EXECUTION_MODE"] == "ACTIVE"
        assert "DO NOT use todo_write" in result["🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS"]
        assert "Complete task" in result["execution_model"]
        assert "Submit evidence" in result["execution_model"]
        assert "Advance phase" in result["execution_model"]
    
    def test_all_required_fields_present(self):
        """Test completeness: all 3 guidance fields present."""
        result = add_workflow_guidance({"test": "data"})
        
        required_fields = [
            "⚠️_WORKFLOW_EXECUTION_MODE",
            "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS",
            "execution_model"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
```

**Run tests:**
```bash
pytest tests/unit/test_workflow_guidance.py -v
```

**Expected output:**
```
test_workflow_guidance.py::TestWorkflowGuidance::test_add_guidance_to_valid_dict PASSED
test_workflow_guidance.py::TestWorkflowGuidance::test_add_guidance_preserves_original_fields PASSED
test_workflow_guidance.py::TestWorkflowGuidance::test_add_guidance_with_non_dict_input PASSED
test_workflow_guidance.py::TestWorkflowGuidance::test_guidance_fields_appear_first PASSED
test_workflow_guidance.py::TestWorkflowGuidance::test_guidance_field_values PASSED
test_workflow_guidance.py::TestWorkflowGuidance::test_all_required_fields_present PASSED

====== 6 passed in 0.02s ======
```

---

### 2.2 Integration Tests

**File:** `tests/integration/test_workflow_guidance_integration.py`

**Pattern: Test end-to-end workflow execution**

```python
import pytest
from mcp_server.workflow_engine import WorkflowEngine
from mcp_server.rag_engine import RAGEngine
from mcp_server.state_manager import StateManager


@pytest.fixture
def workflow_engine():
    """Create workflow engine for testing."""
    rag = RAGEngine()
    state_mgr = StateManager()
    return WorkflowEngine(rag, state_mgr)


class TestWorkflowGuidanceIntegration:
    """Integration tests for workflow guidance in real workflow execution."""
    
    def test_workflow_responses_include_guidance(self, workflow_engine):
        """Test all workflow tool responses include guidance fields."""
        # Start workflow
        start_response = workflow_engine.start_workflow(
            workflow_type="spec_creation_v1",
            target_file="test-feature"
        )
        
        # Verify guidance in start response
        assert "⚠️_WORKFLOW_EXECUTION_MODE" in start_response
        assert "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS" in start_response
        assert "execution_model" in start_response
        
        session_id = start_response["session_id"]
        
        # Get current phase
        phase_response = workflow_engine.get_current_phase(session_id)
        assert "⚠️_WORKFLOW_EXECUTION_MODE" in phase_response
        
        # Get task
        task_response = workflow_engine.get_task(session_id, phase=0, task_number=1)
        assert "⚠️_WORKFLOW_EXECUTION_MODE" in task_response
        
        # Complete phase
        evidence = {"supporting_docs_accessible": True, "document_index_created": True}
        complete_response = workflow_engine.complete_phase(
            session_id, phase=0, evidence=evidence
        )
        assert "⚠️_WORKFLOW_EXECUTION_MODE" in complete_response
    
    def test_guidance_fields_in_all_workflow_types(self, workflow_engine):
        """Test guidance present across different workflow types."""
        workflow_types = ["spec_creation_v1", "spec_execution_v1"]
        
        for wf_type in workflow_types:
            response = workflow_engine.start_workflow(
                workflow_type=wf_type,
                target_file=f"test-{wf_type}"
            )
            
            assert "⚠️_WORKFLOW_EXECUTION_MODE" in response
            assert "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS" in response
            assert response["⚠️_WORKFLOW_EXECUTION_MODE"] == "ACTIVE"
    
    def test_backward_compatibility(self, workflow_engine):
        """Test existing workflows continue working with guidance."""
        # Start workflow
        response = workflow_engine.start_workflow(
            workflow_type="spec_creation_v1",
            target_file="test-feature"
        )
        
        # Original fields still present and valid
        assert "session_id" in response
        assert "workflow_type" in response
        assert response["workflow_type"] == "spec_creation_v1"
        
        # Workflow can complete successfully
        session_id = response["session_id"]
        phase_response = workflow_engine.get_current_phase(session_id)
        
        assert "phase_content" in phase_response or "current_phase" in phase_response
```

**Run integration tests:**
```bash
pytest tests/integration/test_workflow_guidance_integration.py -v
```

---

### 2.3 Test Coverage Requirements

**Target:** 100% coverage of `add_workflow_guidance()` function

**Check coverage:**
```bash
pytest --cov=mcp_server.workflow_engine \
       --cov-report=term \
       --cov-report=html \
       tests/unit/test_workflow_guidance.py

# Expected output:
# mcp_server/workflow_engine.py    100%    (lines 45-75 fully covered)
```

**Coverage breakdown:**
- ✅ Normal case (dict input)
- ✅ Edge case (non-dict input)
- ✅ Error handling (exception during merge)
- ✅ Field ordering verification
- ✅ Field value verification

---

## 3. Deployment Guidance

### 3.1 Pre-Deployment Checklist

**Before merging to main:**
- [ ] All unit tests passing (`pytest tests/unit/test_workflow_guidance.py`)
- [ ] All integration tests passing (`pytest tests/integration/test_workflow_guidance_integration.py`)
- [ ] Code review completed
- [ ] Linter clean (`ruff check mcp_server/workflow_engine.py`)
- [ ] Type checking passed (`mypy mcp_server/workflow_engine.py` if applicable)
- [ ] Documentation updated (CHANGELOG.md)
- [ ] Manual validation completed (see Section 3.3)

---

### 3.2 Deployment Steps

**Step 1: Merge to main**
```bash
git checkout main
git pull origin main
git merge feature/workflow-task-management-guidance
git push origin main
```

**Step 2: Deploy to environment**
```bash
# If using containerized deployment
docker-compose restart mcp-server

# If using systemd
sudo systemctl restart agent-os-mcp-server

# If running directly
pkill -f "python -m mcp_server"
python -m mcp_server &
```

**Step 3: Verify deployment**
```bash
# Check MCP server is running
curl http://localhost:PORT/health  # (if health endpoint exists)

# Check logs for startup
tail -f logs/mcp_server.log
```

**Step 4: Smoke test**
- Start a workflow via MCP: `start_workflow("spec_creation_v1", "test")`
- Verify response includes guidance fields
- Verify no errors in logs

---

### 3.3 Manual Validation Procedure

**Validation Script:**
```python
# File: scripts/validate_workflow_guidance.py

from mcp_server.workflow_engine import WorkflowEngine, add_workflow_guidance

def validate_guidance():
    """Manual validation of workflow guidance feature."""
    print("🔍 Validating Workflow Guidance Feature...")
    
    # Test 1: Wrapper function
    print("\n✅ Test 1: Guidance wrapper function")
    test_response = {"session_id": "test"}
    wrapped = add_workflow_guidance(test_response)
    assert "⚠️_WORKFLOW_EXECUTION_MODE" in wrapped
    print("   ✓ Guidance fields added")
    
    # Test 2: Integration with workflow engine
    print("\n✅ Test 2: Workflow engine integration")
    engine = WorkflowEngine(rag_engine, state_manager)
    response = engine.start_workflow("spec_creation_v1", "test")
    assert "⚠️_WORKFLOW_EXECUTION_MODE" in response
    print("   ✓ start_workflow includes guidance")
    
    print("\n🎉 All validation checks passed!")

if __name__ == "__main__":
    validate_guidance()
```

**Run validation:**
```bash
python scripts/validate_workflow_guidance.py
```

---

### 3.4 Rollback Procedure

**If issues detected after deployment:**

**Step 1: Identify commit to revert**
```bash
git log --oneline -10  # Find the guidance feature commit
```

**Step 2: Revert commit**
```bash
git revert <commit-hash>
git push origin main
```

**Step 3: Redeploy**
```bash
# Restart MCP server (same commands as deployment)
docker-compose restart mcp-server
```

**Step 4: Verify rollback**
- Start workflow, verify guidance fields absent
- Check logs for any errors

**Rollback time:** < 5 minutes

---

## 4. Troubleshooting Guide

### 4.1 Common Issues

#### Issue 1: Guidance Fields Not Appearing

**Symptoms:**
- Workflow responses don't have guidance fields
- No errors in logs

**Diagnosis:**
```python
# Check if wrapper function is being called
import logging
logging.basicConfig(level=logging.DEBUG)

# Check workflow engine method
response = engine.start_workflow("spec_creation_v1", "test")
print(list(response.keys()))  # Should show guidance fields first
```

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Wrapper not imported | Add `from mcp_server.workflow_engine import add_workflow_guidance` |
| Wrapper not called | Add `return add_workflow_guidance(response)` to each method |
| Response cached | Clear cache, restart server |

---

#### Issue 2: TypeError - Response Not a Dict

**Symptoms:**
- Error: `TypeError: 'X' object does not support item assignment`
- Workflow operations fail

**Diagnosis:**
```python
# Check what type is being returned
response = engine.start_workflow(...)
print(type(response))  # Should be <class 'dict'>
```

**Cause:** Wrapper function modifying non-dict response

**Solution:**
- Ensure wrapper has `if not isinstance(response, dict): return response` check
- Verify all workflow engine methods return dicts

---

#### Issue 3: AI Still Creating TODOs

**Symptoms:**
- Despite guidance, AI creates `todo_write` calls during workflow execution

**Diagnosis:**
- Manually execute workflow
- Check for `todo_write` tool calls in session
- Verify guidance fields present in responses

**Possible Causes:**

| Cause | Solution |
|-------|----------|
| Guidance message unclear | Update `WORKFLOW_GUIDANCE_FIELDS` text to be more explicit |
| Guidance fields not prominent | Ensure fields appear first in response (dict unpacking order) |
| AI ignoring fields | May need stronger signal (🛑 emoji, ALL CAPS) |

**Iterative Fix:**
```python
# Try stronger messaging
WORKFLOW_GUIDANCE_FIELDS = {
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": (
        "⚠️ CRITICAL: This workflow manages ALL tasks. "
        "DO NOT create separate TODOs using todo_write. "
        "The workflow system IS your task manager. "
        "Use complete_phase() to track progress."
    ),
    ...
}
```

---

#### Issue 4: Performance Degradation

**Symptoms:**
- Workflow responses slower after deployment
- Response times > 1ms overhead

**Diagnosis:**
```python
import time

# Benchmark wrapper function
response = {"session_id": "test", "phase": 1}
start = time.perf_counter()
for _ in range(10000):
    add_workflow_guidance(response)
end = time.perf_counter()

print(f"Average time: {(end - start) / 10000 * 1000:.4f}ms")
# Should be < 0.001ms
```

**Cause:** Inefficient dict merging

**Solution:** Ensure using dict unpacking (`{**A, **B}`) not `dict.update()`

---

### 4.2 Debugging Tips

**Enable debug logging:**
```python
# In mcp_server/workflow_engine.py
logger.setLevel(logging.DEBUG)

# Add debug statements
def add_workflow_guidance(response):
    logger.debug(f"Injecting guidance into response type: {type(response)}")
    ...
```

**Inspect responses:**
```python
# In Python REPL or test
from mcp_server.workflow_engine import WorkflowEngine

engine = WorkflowEngine(...)
response = engine.start_workflow("spec_creation_v1", "test")

# Check guidance
import json
print(json.dumps(response, indent=2))
# Guidance fields should be at top
```

**Test in isolation:**
```python
# Test wrapper function without workflow engine
from mcp_server.workflow_engine import add_workflow_guidance

test_response = {"test": "data"}
result = add_workflow_guidance(test_response)
print(result)
# Should have guidance fields
```

---

### 4.3 Logging and Monitoring

**Key log messages to monitor:**

```
INFO: Workflow session started: session_id=abc-123
DEBUG: Injecting guidance into response type: <class 'dict'>
WARNING: Failed to inject workflow guidance: [exception]  # Should be rare/never
```

**Monitoring queries:**
```bash
# Count guidance injection warnings (should be 0)
grep "Failed to inject workflow guidance" logs/mcp_server.log | wc -l

# Check workflow start rate
grep "Workflow session started" logs/mcp_server.log | wc -l
```

**Alert conditions:**
- Warning: Any "Failed to inject" messages → Investigate immediately
- Critical: Workflow operations failing → Check for breaking changes

---

### 4.4 Getting Help

**Resources:**
- Spec: `.praxis-os/specs/2025-10-08-workflow-task-management-guidance/`
- Tests: `tests/unit/test_workflow_guidance.py`
- Integration tests: `tests/integration/test_workflow_guidance_integration.py`

**Contact:**
- GitHub Issues: Report bugs with reproducible test case
- Internal: Slack #agent-os channel

---

**End of Implementation Guide**

