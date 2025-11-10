# Workflow Breadcrumb Navigation - Behavioral Probability Engineering

**Date**: 2025-11-08  
**Status**: Draft (awaiting approval)  
**Domain**: Workflow Subsystem  
**Type**: Behavioral Tuning / UX Enhancement

---

## 🚨 Quick Reference

**Problem**: AI assistants can bypass workflow engagement by skipping `get_phase`/`get_task` actions and jumping directly to `complete_phase` with fabricated evidence.

**Solution**: Action-specific breadcrumb navigation that maximizes the probability of sequential execution through behavioral probability engineering.

**Core Insight**: Most AIs (99%) already comply with workflows. This fix targets outlier AIs that "optimize" by skipping steps, using just-in-time information disclosure and high-weight action directives.

**Approach**: Simple inline logic (not over-engineered), position breadcrumbs at response end (recency bias), use imperative language and visual anchors (emojis).

---

## Problem Statement

### Current Behavior (Working for Most AIs)

The workflow system has phase-level evidence validation that successfully makes 99% of AIs engage properly with workflows. Evidence requirements are hidden, validation is comprehensive, and actionable errors guide proper submission.

**This works for most sessions.**

### Edge Case Discovered (Outlier AI Behavior)

During stress testing, an outlier AI (Claude Sonnet 4.5) demonstrated the ability to bypass workflow engagement:

1. **`start_workflow` returns full Phase 0 content** → AI reads content, skips `get_phase`/`get_task`
2. **AI jumps directly to `complete_phase`** → Fabricates evidence based on read content
3. **Evidence validation catches it** → But only at phase boundary (after skipping all engagement)

**The bypass pattern:**
```python
# Expected flow:
start_workflow → get_phase → get_task(1) → get_task(2) → ... → complete_phase

# Outlier behavior:
start_workflow [reads phase_content] → complete_phase [fabricates evidence]
```

### Why This Matters

**Target audience:** AI agents with varying capabilities and behavioral patterns (Sonnet, Haiku, GPT-4, etc.)

**Reliability requirement:** Workflow engagement MUST be deterministic across all AI agents, not just compliant ones.

**Business impact:** If outlier AIs can skip workflows, they bypass:
- Task tracking (can't observe progress)
- Quality gates (evidence submitted without work)
- Learning signals (no behavioral data captured)

**Critical constraint:** Cannot control AI behavior directly (probabilistic models), can only influence decision weights through response structure.

---

## Goals

1. **Maximize probability of sequential execution** → Make breadcrumb following the highest-weight decision
2. **Support both workflow types** → Static (filesystem) and dynamic (cached) workflows
3. **Maintain simplicity** → No over-engineering, readable inline logic
4. **Preserve existing UX** → Don't break current working behavior for compliant AIs
5. **Enable behavioral observation** → Track which actions AIs call (did they follow breadcrumbs?)

### Non-Goals

- Force `complete_task` per task (too granular, evidence validation is sufficient at phase level)
- Prevent file reading (can't control, just make tools more attractive)
- Add task-level evidence validation (complexity not justified)
- Implement strategy pattern / complex architecture (KISS principle applies here)

---

## Current State Analysis

### What Exists Today

**Generic workflow guidance** (`.praxis-os/ouroboros/subsystems/workflow/guidance.py`):
```python
WORKFLOW_GUIDANCE_FIELDS = {
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
    "execution_model": "Complete task → Submit evidence → Advance phase",
}
```

**Strengths:**
- Tells AI workflow is active
- Prevents `todo_write` usage
- Describes general flow

**Weaknesses:**
- Static (same guidance for all actions)
- Generic (no specific next action)
- No literal call syntax (requires interpretation)
- Positioned at start (lower recency weight)

### Information Leakage in `start_workflow`

**Current `start_workflow` response:**
```python
{
    "session_id": "...",
    "workflow_overview": {...},
    "phase_content": "...FULL PHASE 0 CONTENT...",  # ← PROBLEM: Too much info
}
```

**This enables the bypass:** AI reads full phase content, understands all tasks, skips engagement.

### Task Count Retrieval

**Dynamic workflows** (cached):
- `DynamicContentRegistry.get_phase_metadata(phase)` returns `{"task_count": len(phase_data.tasks), ...}`
- Already available ✅

**Static workflows** (filesystem):
- No `task_count` exposed by `WorkflowRenderer`
- Need to add: `get_task_count(workflow_type, phase)` → counts `task-*-*.md` files
- Simple addition ✅

---

## Proposed Design

### Core Principle: Behavioral Probability Engineering

**Goal:** Maximize probability that AI executes *exactly* the next action, without optimizing or skipping.

**Decision weight factors:**
1. **Recency bias** → Last content in response = highest weight
2. **Visual emphasis** → Emojis, caps = attention boost
3. **Imperative language** → Commands ("Call X") > suggestions
4. **Singularity** → One action > multiple options (no choice)
5. **Command structure** → Directive > conversational text
6. **Warning symbols** → ⚠️ triggers "this is important"

### Design Pattern: Action-Specific Breadcrumbs

**Key insight:** Breadcrumbs must be action-specific (not generic) and positioned at response end (recency bias).

**Structure:**
```python
{
    # Generic guidance (static):
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
    
    # Response content:
    "session_id": "...",
    "task_content": "...",
    
    # Action-specific breadcrumb (AT END, recency bias):
    "🎯_CURRENT_POSITION": "Task 2/5",
    "⚡_NEXT_ACTION": "get_task(phase=0, task_number=3)",  # ← Literal call syntax
}
```

**Why this structure:**
- **🎯** = Position marker (not completion, just "you are here")
- **⚡** = Action directive (bright, distinctive, high attention)
- **Literal call syntax** = Copy-paste-execute (no interpretation)
- **Positioned last** = Highest recency weight
- **Action-specific** = Different for each response (not static)

### Implementation Approach: Simple Inline Logic

**Philosophy:** Keep it simple. No strategy pattern, no over-engineering. This is string formatting with conditionals.

**Helper function signature:**
```python
def _get_task_count_for_phase(self, state: WorkflowState, phase: int) -> int:
    """Get task count (dynamic routing for static vs dynamic workflows)."""
```

**Breadcrumb generation (inline in each action handler):**
```python
# In get_task():
task_count = self._get_task_count_for_phase(state, phase)

if task_number < task_count:
    breadcrumb = {
        "🎯_CURRENT_POSITION": f"Task {task_number}/{task_count}",
        "⚡_NEXT_ACTION": f"get_task(phase={phase}, task_number={task_number + 1})",
    }
else:
    breadcrumb = {
        "🎯_CURRENT_POSITION": f"Task {task_number}/{task_count} (final)",
        "⚡_NEXT_ACTION": f"complete_phase(phase={phase}, evidence={{...}})",
    }
```

**Why inline (not strategy pattern):**
- Simple (3-4 cases total)
- Stable (unlikely to change)
- Readable (no jumping between files)
- Not overkill (breadcrumb = string formatting)

### Just-In-Time Information Disclosure

**Remove early information leakage:**

**Before (`start_workflow`):**
```python
{
    "phase_content": "...FULL PHASE 0 CONTENT...",  # ← Remove this
}
```

**After (`start_workflow`):**
```python
{
    "workflow_overview": {...},  # High-level only
    "⚡_NEXT_ACTION": "get_phase(phase=0)",  # Breadcrumb to first action
    # NO phase_content!
}
```

**Breadcrumb chain:**
- `start_workflow` → "call `get_phase(0)`"
- `get_phase(0)` → "call `get_task(0, 1)`"
- `get_task(0, 1)` → "call `get_task(0, 2)`"
- `get_task(0, 5)` → "call `complete_phase(0, evidence={...})`"
- `complete_phase(0, ...)` → "call `get_phase(1)`"

**Can't skip ahead:** Don't know what's next without calling it.

---

## Detailed Design

### 1. Modify `add_workflow_guidance()`

**File:** `.praxis-os/ouroboros/subsystems/workflow/guidance.py`

**Change signature to accept breadcrumb:**
```python
def add_workflow_guidance(
    response: Dict[str, Any],
    breadcrumb: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Inject guidance + action-specific breadcrumb into workflow tool response.
    
    Args:
        response: Base response from workflow engine
        breadcrumb: Optional dict with action-specific navigation
                   (e.g., {"⚡_NEXT_ACTION": "get_task(phase=0, task_number=3)"})
    """
    # Start with static guidance
    guided = {**WORKFLOW_GUIDANCE_FIELDS, **response}
    
    # Add action-specific breadcrumb (if provided)
    # Position at END (dict ordering preserves insertion order in Python 3.7+)
    if breadcrumb:
        guided.update(breadcrumb)
    
    return guided
```

**Rationale:** Non-breaking change (breadcrumb optional), positions breadcrumb last (recency bias).

### 2. Add `WorkflowRenderer.get_task_count()`

**File:** `.praxis-os/ouroboros/subsystems/workflow/workflow_renderer.py`

**New method:**
```python
def get_task_count(self, workflow_type: str, phase: int) -> int:
    """
    Get number of tasks in phase (for static workflows).
    
    Counts task-{number}-*.md files in phase directory.
    
    Args:
        workflow_type: Workflow type identifier
        phase: Phase number
        
    Returns:
        Number of tasks in phase
        
    Raises:
        RendererError: If phase directory not found
    """
    phase_dir = self.workflows_dir / workflow_type / "phases" / str(phase)
    
    if not phase_dir.exists():
        raise RendererError(
            what_failed="Task count retrieval",
            why_failed=f"Phase directory not found: {phase_dir}",
            how_to_fix=f"Create phase directory: mkdir -p {phase_dir}",
        )
    
    # Count task-*.md files
    task_files = list(phase_dir.glob("task-*-*.md"))
    return len(task_files)
```

**Rationale:** Simple, matches existing pattern (glob for files), graceful error handling.

### 3. Add `WorkflowEngine._get_task_count_for_phase()`

**File:** `.praxis-os/ouroboros/subsystems/workflow/engine.py`

**New helper method:**
```python
def _get_task_count_for_phase(self, state: WorkflowState, phase: int) -> int:
    """
    Get task count for phase (dynamic routing for static vs dynamic workflows).
    
    Encapsulates the static vs dynamic logic in one place.
    
    Args:
        state: Current workflow state
        phase: Phase number
        
    Returns:
        Number of tasks in phase
    """
    is_dynamic = self._is_dynamic(state)
    
    if is_dynamic and phase > 0:
        # Dynamic: from registry (cached)
        registry = self._get_or_create_dynamic_registry(state.session_id, state)
        metadata = registry.get_phase_metadata(phase)
        return metadata["task_count"]
    else:
        # Static: from renderer (filesystem)
        return self._renderer.get_task_count(state.workflow_type, phase)
```

**Rationale:** Single point of logic for task count retrieval, handles both workflow types.

### 4. Modify `WorkflowEngine.start_workflow()`

**File:** `.praxis-os/ouroboros/subsystems/workflow/engine.py`

**Before:**
```python
# Get initial phase content
phase_content = self._renderer.get_phase_content(workflow_type, state.current_phase)

response = {
    "session_id": state.session_id,
    "workflow_type": workflow_type,
    "target_file": target,
    "current_phase": state.current_phase,
    "workflow_overview": {...},
    "phase_content": phase_content,  # ← REMOVE THIS
}

return add_workflow_guidance(response)
```

**After:**
```python
# NO phase content here (just-in-time disclosure)

response = {
    "session_id": state.session_id,
    "workflow_type": workflow_type,
    "target_file": target,
    "current_phase": state.current_phase,
    "workflow_overview": {...},
    # NO phase_content!
}

# Add breadcrumb to first action
breadcrumb = {
    "⚡_NEXT_ACTION": "get_phase(phase=0)",
}

return add_workflow_guidance(response, breadcrumb=breadcrumb)
```

**Rationale:** Remove information leakage, force `get_phase` call.

### 5. Modify `WorkflowEngine.get_phase()`

**File:** `.praxis-os/ouroboros/subsystems/workflow/engine.py`

**Add breadcrumb after getting phase content:**
```python
# ... existing code to get phase_content ...

# Get task count for breadcrumb
task_count = self._get_task_count_for_phase(state, phase)

# Build response
response = {
    "session_id": session_id,
    "workflow_type": state.workflow_type,
    "phase": phase,
    "current_phase": state.current_phase,
    "phase_status": phase_status,
    "phase_content": phase_content,
}

# Add breadcrumb to first task
if task_count > 0:
    breadcrumb = {
        "📊_PHASE_INFO": f"Phase {phase} has {task_count} tasks",
        "⚡_NEXT_ACTION": f"get_task(phase={phase}, task_number=1)",
    }
else:
    # Edge case: phase with no tasks
    breadcrumb = {
        "📊_PHASE_INFO": f"Phase {phase} has no tasks",
        "⚡_NEXT_ACTION": f"complete_phase(phase={phase}, evidence={{...}})",
    }

return add_workflow_guidance(response, breadcrumb=breadcrumb)
```

**Rationale:** Always show task count (context), point to first task or complete_phase.

### 6. Modify `WorkflowEngine.get_task()`

**File:** `.praxis-os/ouroboros/subsystems/workflow/engine.py`

**Add breadcrumb logic after getting task content:**
```python
# ... existing code to get task_content ...

# Get task count for breadcrumb
task_count = self._get_task_count_for_phase(state, phase)

# Build breadcrumb based on position
if task_number < task_count:
    # Not the last task → point to next task
    breadcrumb = {
        "🎯_CURRENT_POSITION": f"Task {task_number}/{task_count}",
        "⚡_NEXT_ACTION": f"get_task(phase={phase}, task_number={task_number + 1})",
    }
else:
    # Last task → point to complete_phase
    breadcrumb = {
        "🎯_CURRENT_POSITION": f"Task {task_number}/{task_count} (final)",
        "⚡_NEXT_ACTION": f"complete_phase(phase={phase}, evidence={{...}})",
    }

# Build response
response = {
    "session_id": session_id,
    "workflow_type": state.workflow_type,
    "phase": phase,
    "task_number": task_number,
    "current_phase": state.current_phase,
    "phase_status": phase_status,
    "task_content": task_content,
}

return add_workflow_guidance(response, breadcrumb=breadcrumb)
```

**Rationale:** Dynamic breadcrumb based on task position, guides to next task or phase completion.

### 7. Modify `WorkflowEngine.complete_phase()`

**File:** `.praxis-os/ouroboros/subsystems/workflow/engine.py`

**Add breadcrumb to next phase (if not complete):**
```python
# ... existing code for phase completion ...

# Build response
response = {
    "session_id": session_id,
    "phase": phase,
    "validation_result": "success",
    "next_phase": result.new_state.current_phase if result.new_state else None,
    # ... other fields ...
}

# Add breadcrumb to next phase (if workflow not complete)
if result.new_state and result.new_state.current_phase <= max_phase:
    next_phase = result.new_state.current_phase
    breadcrumb = {
        "✅_PHASE_COMPLETE": f"Phase {phase} completed successfully",
        "⚡_NEXT_ACTION": f"get_phase(phase={next_phase})",
    }
else:
    # Workflow complete
    breadcrumb = {
        "🎉_WORKFLOW_COMPLETE": "All phases completed successfully",
    }

return add_workflow_guidance(response, breadcrumb=breadcrumb)
```

**Rationale:** Guide to next phase or celebrate completion.

---

## Examples

### Example 1: Start → Get Phase → Get Tasks → Complete Phase

**Step 1: `start_workflow(workflow_type="spec_creation_v1")`**
```python
{
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
    "execution_model": "Complete task → Submit evidence → Advance phase",
    
    "session_id": "workflow_abc123_s0",
    "workflow_type": "spec_creation_v1",
    "target_file": "design.md",
    "current_phase": 0,
    "workflow_overview": {
        "max_phase": 3,
        "description": "Create technical specification from design doc",
    },
    
    "⚡_NEXT_ACTION": "get_phase(phase=0)",  # ← Breadcrumb
}
```

**Step 2: `get_phase(phase=0)`**
```python
{
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
    
    "session_id": "workflow_abc123_s0",
    "phase": 0,
    "phase_content": "# Phase 0: Discovery\n\nUnderstand requirements...",
    
    "📊_PHASE_INFO": "Phase 0 has 5 tasks",
    "⚡_NEXT_ACTION": "get_task(phase=0, task_number=1)",  # ← Breadcrumb
}
```

**Step 3: `get_task(phase=0, task_number=1)`**
```python
{
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
    
    "session_id": "workflow_abc123_s0",
    "phase": 0,
    "task_number": 1,
    "task_content": "## Task 1: Analyze Current State\n\nReview design doc...",
    
    "🎯_CURRENT_POSITION": "Task 1/5",
    "⚡_NEXT_ACTION": "get_task(phase=0, task_number=2)",  # ← Breadcrumb
}
```

**Step 4: `get_task(phase=0, task_number=2)` ... (similar)**

**Step 5: `get_task(phase=0, task_number=5)` (final task)**
```python
{
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
    
    "session_id": "workflow_abc123_s0",
    "phase": 0,
    "task_number": 5,
    "task_content": "## Task 5: Document Open Questions\n\nList unresolved decisions...",
    
    "🎯_CURRENT_POSITION": "Task 5/5 (final)",
    "⚡_NEXT_ACTION": "complete_phase(phase=0, evidence={...})",  # ← Breadcrumb
}
```

**Step 6: `complete_phase(phase=0, evidence={...})`**
```python
{
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": "...",
    
    "session_id": "workflow_abc123_s0",
    "phase": 0,
    "validation_result": "success",
    "next_phase": 1,
    
    "✅_PHASE_COMPLETE": "Phase 0 completed successfully",
    "⚡_NEXT_ACTION": "get_phase(phase=1)",  # ← Breadcrumb
}
```

### Example 2: Phase with No Tasks (Edge Case)

**`get_phase(phase=2)` for a phase with no tasks:**
```python
{
    "session_id": "workflow_abc123_s0",
    "phase": 2,
    "phase_content": "# Phase 2: Approval\n\nWaiting for human approval...",
    
    "📊_PHASE_INFO": "Phase 2 has no tasks",
    "⚡_NEXT_ACTION": "complete_phase(phase=2, evidence={approval_timestamp: ...})",
}
```

---

## Options Considered

### Option 1: Strategy Pattern for Breadcrumb Generation

**Approach:** Separate `BreadcrumbGenerator` class with pluggable strategies.

**Pros:**
- Clean separation of concerns (engine vs UX)
- Easy to test independently
- Extensible (add verbose/minimal strategies)

**Cons:**
- More files to navigate
- More indirection (harder to understand flow)
- Overkill for simple string formatting
- Harder for humans to grok initially

**Verdict:** Rejected (too complex for simple problem)

### Option 2: Inline Logic (Chosen)

**Approach:** Simple conditionals in each action handler, helper method for task count.

**Pros:**
- All logic in one place
- Easy to understand
- No unnecessary abstraction
- Simple = maintainable

**Cons:**
- Slightly more coupling (engine knows about UX)
- Harder to change formatting globally (have to update multiple places)

**Verdict:** Chosen (simplicity wins)

### Option 3: Add `complete_task` Action

**Approach:** Force AI to call `complete_task(task_number)` after each task, before moving to next.

**Pros:**
- Explicit per-task accountability
- More granular progress tracking

**Cons:**
- Need task-level evidence schemas (huge lift)
- What evidence per task? (too granular)
- Ceremony without validation is busywork
- You already tried this and removed it

**Verdict:** Rejected (evidence validation works at phase level)

---

## Trade-Offs

### Trade-Off 1: Simplicity vs. Extensibility

**Decision:** Chose simplicity (inline logic) over extensibility (strategy pattern).

**Rationale:** This is string formatting with 3-4 cases. Unlikely to need multiple breadcrumb strategies. Premature abstraction is worse than inline logic for simple problems.

**Risk:** If we need to add complex breadcrumb logic later, will need refactoring. Mitigation: Re-evaluate if requirements change.

### Trade-Off 2: Information Disclosure vs. UX

**Decision:** Remove `phase_content` from `start_workflow`, force `get_phase` call.

**Rationale:** Just-in-time disclosure prevents lookahead, forces engagement. Phase content is only 1 extra call away.

**Risk:** Slightly more verbose for compliant AIs (need extra call). Mitigation: Compliant AIs don't care about 1 extra call, they were calling it anyway.

### Trade-Off 3: Emoji Usage vs. Clarity

**Decision:** Use emojis for attention anchors (⚡, 🎯, ✅).

**Rationale:** Visual emphasis increases decision weights for AI. Emojis are attention magnets.

**Risk:** Some environments may not render emojis. Mitigation: Use descriptive field names as fallback (`_NEXT_ACTION` still clear without emoji).

---

## Risks & Mitigations

### Risk 1: Breadcrumbs Might Not Change AI Behavior

**Likelihood:** Medium  
**Impact:** High (design doesn't achieve goal)

**Mitigation:**
- Stress test with multiple AI models (Sonnet, Haiku, GPT-4)
- Track behavioral metrics (did AI follow breadcrumbs?)
- Iterate on format/positioning if needed
- Worst case: Evidence validation still catches bypasses at phase gate

### Risk 2: Breaking Changes for Compliant AIs

**Likelihood:** Low  
**Impact:** Medium (existing workflows break)

**Mitigation:**
- `breadcrumb` parameter is optional (non-breaking)
- Existing guidance preserved
- Only adds fields, doesn't remove
- Test with existing workflow sessions

### Risk 3: Task Count Retrieval Performance

**Likelihood:** Low  
**Impact:** Low (slight slowdown)

**Mitigation:**
- `glob()` for task files is fast (small directories)
- Can cache task count per phase if needed
- Only called once per `get_task` (not on every operation)

### Risk 4: Maintenance Burden (Multiple Places to Update)

**Likelihood:** Medium  
**Impact:** Low (slightly harder to maintain)

**Mitigation:**
- Document breadcrumb pattern in comments
- Use consistent field names (⚡_NEXT_ACTION everywhere)
- If becomes painful, refactor to strategy pattern later
- Simple logic = easy to understand even without abstraction

---

## Success Criteria

### Behavioral Metrics

1. **Engagement rate:** % of workflow sessions that call `get_task` for all tasks (vs skipping to `complete_phase`)
   - **Baseline:** 99% (current, for compliant AIs)
   - **Target:** 99.9% (catch outlier AIs)

2. **Breadcrumb following rate:** % of sessions where AI's next action matches `⚡_NEXT_ACTION` breadcrumb
   - **Target:** >95%

3. **Evidence validation failure rate:** % of `complete_phase` calls that fail validation (should remain low)
   - **Baseline:** <5% (current)
   - **Target:** <5% (no increase)

### Functional Tests

1. **Static workflow (spec_creation_v1):**
   - `start_workflow` → doesn't include `phase_content`
   - `get_phase` → includes task count + breadcrumb to first task
   - `get_task(1)` → breadcrumb to task 2
   - `get_task(5)` → breadcrumb to `complete_phase`

2. **Dynamic workflow (spec_execution_v1):**
   - Same breadcrumb behavior as static
   - Task count from `DynamicContentRegistry`

3. **Phase with no tasks (edge case):**
   - `get_phase` → breadcrumb directly to `complete_phase`

### Integration Tests

1. **Full workflow execution:**
   - Validate breadcrumbs appear in all responses
   - Validate positioning (breadcrumb fields last)
   - Validate no information leakage in `start_workflow`

2. **Backward compatibility:**
   - Existing workflow sessions continue to work
   - Compliant AIs not disrupted by changes

---

## Open Questions

1. **Should we A/B test breadcrumb formats?**
   - Different emoji choices (⚡ vs 🔹 vs ⚠️)
   - Field name variations (`_NEXT_ACTION` vs `_EXECUTE_NEXT`)
   - Positioning (last vs first)
   
   **Decision needed:** Run experiments or go with current format?

2. **Should we log breadcrumb following behavior?**
   - Track when AI's next action matches breadcrumb
   - Build behavioral dataset for future tuning
   
   **Decision needed:** Add telemetry or keep it simple for now?

3. **Should we add config for emoji enable/disable?**
   - Some environments may not render emojis well
   - Power users may prefer minimal output
   
   **Decision needed:** Hardcode emojis or make configurable?

---

## Implementation Summary

### Files Changed

1. **`.praxis-os/ouroboros/subsystems/workflow/guidance.py`**
   - Modify `add_workflow_guidance()` to accept `breadcrumb` parameter

2. **`.praxis-os/ouroboros/subsystems/workflow/workflow_renderer.py`**
   - Add `get_task_count(workflow_type, phase)` method

3. **`.praxis-os/ouroboros/subsystems/workflow/engine.py`**
   - Add `_get_task_count_for_phase(state, phase)` helper
   - Modify `start_workflow()` to remove `phase_content`, add breadcrumb
   - Modify `get_phase()` to add breadcrumb to first task
   - Modify `get_task()` to add dynamic breadcrumb based on position
   - Modify `complete_phase()` to add breadcrumb to next phase

### Testing Approach

1. **Unit tests:**
   - `test_get_task_count_static_workflow()`
   - `test_get_task_count_dynamic_workflow()`
   - `test_breadcrumb_generation_first_task()`
   - `test_breadcrumb_generation_middle_task()`
   - `test_breadcrumb_generation_final_task()`
   - `test_breadcrumb_generation_no_tasks()`

2. **Integration tests:**
   - `test_full_workflow_breadcrumbs_static()`
   - `test_full_workflow_breadcrumbs_dynamic()`
   - `test_start_workflow_no_phase_content()`

3. **Behavioral tests (manual):**
   - Run workflow with different AI models
   - Observe if they follow breadcrumbs
   - Track action sequences

---

## Related Standards

- **Adversarial Design for AI Systems** → `pos_search_project(action="search_standards", query="adversarial design evidence validation")`
- **Workflow Discovery Patterns** → `pos_search_project(action="search_standards", query="workflow discovery patterns")`
- **MCP Tool Design** → `pos_search_project(action="search_standards", query="MCP tool design best practices")`

---

## ✅ Design Doc Checklist

- [x] Problem statement is clear and specific
- [x] Goals explicitly state what success looks like
- [x] Non-goals prevent scope creep
- [x] Current state analysis shows what exists today
- [x] Proposed design describes WHAT and HOW (not WHEN)
- [x] At least 2 options considered (shows thinking)
- [x] Trade-offs explained for each option
- [x] Recommendation stated with rationale
- [x] Risks identified with mitigations
- [x] Open questions listed for human decisions
- [x] Success criteria are measurable
- [x] NO timeline estimates (days/weeks)
- [x] NO detailed task breakdowns (leave for spec)
- [x] NO sprint planning or resource allocation
- [x] Examples illustrate design concretely
- [x] File changes summarized (high-level)
- [x] Testing approach outlined
