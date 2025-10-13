---
sidebar_position: 3
doc_type: how-to
---

# Debug Workflow Failures

This guide shows you how to troubleshoot and resolve common workflow execution failures including checkpoint validation errors, tool invocation issues, and state corruption.

## Goal

By following this guide, you will:
- Identify which phase or task failed in a workflow
- Understand checkpoint validation failures
- Resolve common workflow errors
- Resume interrupted workflows successfully
- Know when to restart vs. resume a workflow

## Prerequisites

- Understanding of Agent OS Enhanced workflows ([Understanding Agent OS Enhanced Workflows](../tutorials/understanding-agent-os-workflows))
- Active or failed workflow to debug
- Access to Cursor chat with MCP tools

## When to Use This

Use this guide when you encounter:

❌ **Checkpoint validation failures** - Workflow blocked at phase gate  
❌ **Tool invocation errors** - MCP tool calls failing  
❌ **State corruption** - Workflow state inconsistent or lost  
❌ **Interrupted workflows** - Workflow stopped mid-execution  
❌ **Unexpected behavior** - Workflow not progressing as expected  

---

## Step 1: Check Workflow State

Always start by checking the complete workflow state.

### 1.1 Query Workflow State

In Cursor chat, ask:

```
What's the current workflow state? Use get_workflow_state tool.
```

**Expected Output:**

```json
{
  "session_id": "workflow_session_123",
  "workflow_type": "spec_creation_v1",
  "status": "in_progress",
  "current_phase": 2,
  "total_phases": 6,
  "phase_progress": {
    "0": "completed",
    "1": "completed",
    "2": "in_progress",
    "3": "pending",
    "4": "pending",
    "5": "pending"
  },
  "completed_phases": [
    {
      "phase_number": 0,
      "phase_name": "Supporting Documents Integration",
      "completed_at": "2025-10-12T10:30:15Z",
      "evidence": {
        "supporting_docs_accessible": true,
        "document_index_created": true,
        "insights_extracted": true
      }
    },
    {
      "phase_number": 1,
      "phase_name": "Requirements Gathering",
      "completed_at": "2025-10-12T10:45:22Z",
      "evidence": {
        "srd_created": true,
        "business_goals_defined": true,
        "user_stories_documented": true,
        "functional_requirements_listed": true,
        "nfr_defined": true,
        "out_of_scope_clarified": true
      }
    }
  ],
  "current_task": {
    "phase": 2,
    "task_number": 1,
    "task_name": "Define Architecture"
  }
}
```

### 1.2 Identify the Problem

From the state output, determine:

1. **Is the workflow stuck?**
   - `status`: "blocked", "failed", or "in_progress" for extended time

2. **Which phase failed?**
   - Look at `current_phase` number
   - Check `phase_progress` for failed phases

3. **What evidence is missing?**
   - Look at `completed_phases` evidence objects
   - Compare against required evidence (see Step 2)

---

## Step 2: Read Checkpoint Requirements

Each phase has specific evidence requirements. Understanding what's needed is key to resolving failures.

### 2.1 Check Phase Metadata

Ask the agent:

```
What are the checkpoint requirements for Phase 2 of spec_creation_v1?
```

**Expected Response:**

```
Phase 2: Technical Design

Required Evidence:
- specs_created: specs.md file must exist
- architecture_documented: Architecture section must be present
- components_defined: Component definitions must be listed
- security_addressed: Security considerations documented
- performance_addressed: Performance requirements specified
```

### 2.2 Compare with Current Evidence

Cross-reference the requirements with what the workflow has collected:

```
Show me what evidence has been collected for Phase 2
```

This reveals **which evidence is missing**.

---

## Step 3: Resolve Common Failure Patterns

### Pattern 1: Missing Evidence Keys

**Symptom:**

```
❌ Checkpoint validation failed
Missing evidence: specs_created
```

**Cause:** Required file or artifact not created

**Solution:**

1. Create the missing artifact:
   ```
   Create the specs.md file as required by Phase 2
   ```

2. Verify the file exists:
   ```bash
   ls .agent-os/specs/[date]-[name]/specs.md
   ```

3. Retry checkpoint validation:
   ```
   I've created specs.md. Please validate Phase 2 checkpoint.
   ```

### Pattern 2: Incorrect Evidence Values

**Symptom:**

```
❌ Checkpoint validation failed
Evidence 'architecture_documented' is false, expected true
```

**Cause:** File exists but doesn't contain required sections

**Solution:**

1. Check what's missing:
   ```
   What sections are required in specs.md for architecture_documented?
   ```

2. Add the missing content:
   ```
   Add the Architecture section to specs.md with:
   - System overview
   - Component diagram
   - Technology stack
   ```

3. Retry validation:
   ```
   I've added the Architecture section. Validate checkpoint.
   ```

### Pattern 3: Tool Invocation Errors

**Symptom:**

```
Error: Tool 'get_current_phase' failed
Error message: Session not found
```

**Cause:** Workflow session lost or expired

**Solution:**

1. Check if session exists:
   ```
   List all active workflow sessions
   ```

2. If session lost, restart workflow:
   ```
   Start a new spec_creation_v1 workflow for [feature-name]
   ```

   **Note:** Cannot resume from lost session. Must start fresh.

### Pattern 4: State File Corruption

**Symptom:**

```
Error: Failed to load workflow state
Error: JSON parse error in state file
```

**Cause:** Workflow state file corrupted (rare)

**Solution:**

1. Attempt to recover state:
   ```
   Try to recover workflow state from backup
   ```

2. If recovery fails, restart:
   ```
   The workflow state is corrupted. Let's start a new workflow:
   
   Start spec_creation_v1 for [feature-name]
   ```

   **Important:** Save any completed artifacts before restarting:
   ```bash
   cp -r .agent-os/specs/[date]-[name] .agent-os/specs/[date]-[name]-backup
   ```

### Pattern 5: Phase Skipping Blocked

**Symptom:**

```
Cannot advance to Phase 3
Phase 2 checkpoint not passed
```

**Cause:** Workflow engine enforcing phase gating (working as intended)

**Solution:**

This is **not** a bug - it's the workflow enforcing quality gates.

1. Complete Phase 2 requirements:
   ```
   What do I need to complete for Phase 2 checkpoint?
   ```

2. Provide all required evidence

3. Only then can you advance

**Why this happens:** The workflow **cannot** be bypassed. Phase gates are hard-coded.

---

## Step 4: Resume Interrupted Workflows

Workflows maintain persistent state and can be resumed after interruptions.

### 4.1 When Can You Resume?

You can resume if:

✅ Session ID is known  
✅ State was saved successfully  
✅ MCP server restarted cleanly  
✅ State files exist on disk  

You **cannot** resume if:

❌ Session expired (typically 24 hours)  
❌ State files deleted  
❌ State file corrupted  
❌ Different project/workspace  

### 4.2 Resume After Interruption

If Cursor crashed or was closed mid-workflow:

```
I was running a spec_creation_v1 workflow. Can we resume?
```

The agent will:
1. Check for active sessions
2. Load the most recent workflow state
3. Show current progress
4. Continue from last checkpoint

**Example Response:**

```
Found workflow session: wf-spec-creation-2025-10-12-10-30
Status: In Progress
Current Phase: 2 (Technical Design)
Completed: Phases 0, 1

Resuming Phase 2...
```

### 4.3 Check Resumption Success

Verify the workflow resumed correctly:

```
Show me the workflow state to confirm we resumed correctly
```

Expected output should match the state before interruption.

---

## Step 5: Decide: Restart vs. Resume

### When to Resume

Resume the existing workflow if:

✅ Minor interruption (crash, close)  
✅ State is intact  
✅ Want to preserve completed work  
✅ No fundamental issues with workflow  

### When to Restart

Start a new workflow if:

❌ State corrupted  
❌ Requirements changed significantly  
❌ Phase 0/1 completed incorrectly  
❌ Want to change approach  

**Restart Command:**

```
Cancel the current workflow and start a new spec_creation_v1 for [feature-name]
```

This will:
1. Mark old session as cancelled
2. Start fresh session
3. Begin from Phase 0

---

## Troubleshooting Checklist

Work through this checklist when debugging:

- [ ] **Check workflow state** - Use `get_workflow_state` to see current status
- [ ] **Identify failing phase** - Which phase is blocked or failed?
- [ ] **Read checkpoint requirements** - What evidence is required?
- [ ] **Compare with current evidence** - What's missing?
- [ ] **Verify files exist** - Do required artifacts exist on disk?
- [ ] **Check file contents** - Do files have required sections?
- [ ] **Review error messages** - What's the specific error?
- [ ] **Check MCP server** - Is server running and responsive?
- [ ] **Try resuming** - Can the workflow be resumed?
- [ ] **Consider restarting** - Is a fresh start needed?

---

## Common Error Messages

### Error: "Checkpoint validation failed"

**Meaning:** Required evidence not provided

**Fix:** Complete missing evidence items (see Pattern 1 & 2 above)

### Error: "Session not found"

**Meaning:** Workflow session expired or lost

**Fix:** Start new workflow (cannot resume)

### Error: "Tool invocation failed"

**Meaning:** MCP tool call error

**Fix:** 
1. Check MCP server is running
2. Restart Cursor if needed
3. Retry the operation

### Error: "Phase N is not accessible"

**Meaning:** Trying to skip phases

**Fix:** Complete previous phases first (phase gating enforced)

### Error: "Evidence validation failed for [key]"

**Meaning:** Evidence provided but doesn't meet criteria

**Fix:** Review requirements and update the artifact

---

## Validation Checklist

After resolving a failure, verify:

- [ ] Workflow state shows correct phase
- [ ] All evidence collected for completed phases
- [ ] Required files exist and are valid
- [ ] Checkpoint validation passes
- [ ] Workflow can advance to next phase
- [ ] No error messages in chat

---

## Related Documentation

- **[Understanding Agent OS Enhanced Workflows](../tutorials/understanding-agent-os-workflows)** - Learn workflow concepts
- **[Create Custom Workflows](./create-custom-workflows)** - Build workflows with proper checkpoints
- **[Reference: Workflows](../reference/workflows)** - Workflow system reference

---

## Summary

You've learned to debug workflow failures by:

1. ✅ Checking workflow state with `get_workflow_state`
2. ✅ Identifying which phase/task failed
3. ✅ Reading checkpoint evidence requirements
4. ✅ Resolving common failure patterns (missing evidence, tool errors, corruption)
5. ✅ Resuming interrupted workflows
6. ✅ Deciding when to restart vs. resume

Most workflow failures are checkpoint validation issues - the workflow is correctly enforcing quality gates. The solution is to complete the required evidence, not bypass the gate.

