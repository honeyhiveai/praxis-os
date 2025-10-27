# Problem Analysis: Workflow Task Management Guidance

**Date:** 2025-10-08  
**Context:** prAxIs OS MCP Workflow System  
**Issue:** AI creates separate TODO lists while executing MCP workflows

---

## Problem Statement

When executing prAxIs OS workflows via MCP, the AI assistant creates separate TODO lists using Cursor's `todo_write` tool instead of using the workflow system as the sole task management interface. This violates the single-source-of-truth principle and creates confusion about task state.

### Example Incident

**Scenario:** User requests spec creation using `spec_creation_v1` workflow

**What happened:**
1. AI correctly started workflow: `start_workflow("spec_creation_v1")`
2. AI correctly queried phase content: `get_current_phase()`
3. AI correctly read task details: `get_task(phase=0, task_number=1)`
4. ❌ AI then created parallel TODOs using `todo_write`:
   - "Phase 0 Task 1: Copy design document"
   - "Phase 0 Task 2: Create document index"
   - "Phase 0 Task 3: Extract insights"
   - "Phase 1-5: Complete remaining phases"

**Why this is wrong:**
- The workflow system already tracks phases, tasks, and evidence
- Creates two competing task management systems
- Violates single-source-of-truth
- Not the intended workflow execution pattern

---

## Root Cause Analysis

### Architectural Context

**Two Tool Providers:**
1. **Cursor Tools** (built-in to Cursor IDE)
   - `todo_write` - Task management
   - `read_file`, `write`, etc.
   - ❌ Cannot be modified by prAxIs OS team

2. **prAxIs OS MCP Tools** (custom MCP server)
   - `start_workflow`, `complete_phase`, etc.
   - ✅ Fully under prAxIs OS control
   - Can modify tool responses

### Why AI Made the Wrong Choice

**AI's reasoning chain:**
1. Saw: "6 phases with multiple tasks = complex work"
2. `todo_write` tool says: *"Use for complex multi-step tasks (3+ distinct steps)"*
3. Thought: "This qualifies as complex, let me track it"
4. Created TODOs in parallel with workflow execution

**What was missing:**
- No explicit signal that workflow system IS the task tracker
- No indication that `todo_write` should NOT be used during workflow execution
- Nothing in workflow responses saying "I'm managing your tasks now"

### Context Gaps Identified

**Gap 1: todo_write tool description (Cursor-side - can't fix)**
- Says: Use for "complex multi-step tasks"
- Doesn't say: "NEVER use inside MCP workflows"
- This is a Cursor tool we can't modify

**Gap 2: Workflow tool responses (prAxIs OS-side - CAN fix)**
- `start_workflow()` response doesn't indicate task management mode
- `get_current_phase()` doesn't warn against external task tools
- `get_task()` doesn't reinforce workflow-managed execution
- Nothing makes it explicit that workflow supersedes other task systems

**Gap 3: Workflow phase content (prAxIs OS-side - CAN fix)**
- Phase markdown files don't include workflow execution guidance
- No header saying "WORKFLOW-MANAGED SESSION"
- Could inject guidance at runtime

---

## Architectural Constraint

**Critical limitation:** We cannot modify Cursor's tool descriptions.

**Implication:** All guidance must come from prAxIs OS MCP tool responses and workflow content.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | All workflow tool responses must indicate task management mode | MUST |
| FR-2 | Guidance must explicitly prohibit external task tools | MUST |
| FR-3 | Pattern must work for all workflows (existing + future) | MUST |
| FR-4 | Implementation must not require updating workflow .md files | SHOULD |
| FR-5 | Guidance must be visible on every workflow tool call | SHOULD |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Response size increase | < 200 bytes |
| NFR-2 | Implementation time | < 1 hour |
| NFR-3 | Backward compatibility | 100% (existing workflows) |

---

## Proposed Solutions

### Option 1: Prepend Guidance to All Workflow Tool Responses ⭐ RECOMMENDED

**Implementation:** Modify `workflow_engine.py` to inject guidance into every response.

**Example response modification:**
```python
{
  "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
  "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "This workflow manages ALL tasks. DO NOT use todo_write or external task lists. The workflow IS your task tracker.",
  "execution_model": "Complete task → Submit evidence → Advance phase",
  
  # ... rest of normal response
}
```

**Pros:**
- ✅ Visible on every workflow call
- ✅ Can't be missed by AI
- ✅ No .md file changes needed
- ✅ Works for all workflows immediately
- ✅ Easy to implement

**Cons:**
- Adds ~150 bytes to every response

### Option 2: Inject Preamble into phase_content

**Implementation:** When returning `phase_content`, prepend guidance.

```python
phase_content = [
    {
        "content": "🔄 WORKFLOW-MANAGED SESSION\n\nDO NOT create TODOs...",
        "is_workflow_guidance": True,
        "critical": True
    },
    # ... actual phase content
]
```

**Pros:**
- ✅ Contextual to phase content
- ✅ Can be styled as critical

**Cons:**
- Only visible when reading phase content
- Requires more complex injection logic

### Option 3: Add to workflow_overview Only

**Implementation:** Modify only the `workflow_overview` in `start_workflow()`.

**Pros:**
- ✅ Minimal code changes
- ✅ Introduces concept early

**Cons:**
- ❌ Only shown once at workflow start
- ❌ AI may forget by Phase 2+
- ❌ Not reinforced throughout execution

---

## Recommendation

**Implement Option 1** (Prepend to all responses) because:
1. Most reliable - guidance present on every call
2. Easiest to implement - single injection point
3. Most comprehensive - covers all workflows
4. Fail-safe - can't be missed

---

## Success Criteria

1. ✅ AI never creates TODOs when inside workflow
2. ✅ Works for all workflow types (spec_creation, spec_execution, etc.)
3. ✅ Existing workflows continue working unchanged
4. ✅ No negative impact on response parsing
5. ✅ Validated through testing with multiple workflow scenarios

---

## Implementation Scope

**Files to modify:**
- `mcp_server/workflow_engine.py` - Add response wrapper
- `mcp_server/server/tools/workflow_tools.py` - Apply wrapper to tool responses
- Tests: Unit tests for response injection
- Tests: Integration test for workflow execution without TODOs

**Files NOT modified:**
- No workflow .md files
- No workflow metadata
- No phase/task files

---

## References

- Conversation: 2025-10-08 with user identifying TODO creation issue
- Related: Meta-framework principles (single-source-of-truth)
- Related: Workflow construction standards

