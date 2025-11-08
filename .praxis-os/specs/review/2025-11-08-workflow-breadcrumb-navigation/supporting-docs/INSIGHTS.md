# Extracted Insights from Supporting Documents

**Spec:** Workflow Breadcrumb Navigation System  
**Extraction Date:** 2025-11-08  
**Source Documents:** 1 (design document)

---

## Requirements Insights

### Core User Needs

1. **Deterministic AI Behavior Across All Models**
   - Target audience includes AI agents with varying capabilities (Sonnet, Haiku, GPT-4, etc.)
   - Workflow engagement MUST be deterministic across ALL AI agents, not just compliant ones
   - Current system works for 99% of AIs, need to catch the outlier 1%

2. **Prevent Task Skipping**
   - Edge case discovered: Outlier AI (Claude Sonnet 4.5) can bypass workflow engagement
   - Pattern: `start_workflow` → reads `phase_content` → jumps to `complete_phase` → fabricates evidence
   - Evidence validation catches it at phase boundary, but only after skipping all engagement

3. **Maintain Observability**
   - Need to track task progress (can't observe if AI skips tasks)
   - Need behavioral data capture (what actions did AI call?)
   - Need quality gates enforced (evidence submitted after actual work)

### Business Goals

1. **Maximize Probability of Sequential Execution**
   - Make breadcrumb following the highest-weight AI decision
   - Cannot force behavior (probabilistic models), can only influence decision weights

2. **Preserve Existing Working Behavior**
   - Don't break workflows for the 99% of compliant AIs
   - Must be non-breaking change (backward compatible)

3. **Enable Behavioral Observation**
   - Track which actions AIs call (did they follow breadcrumbs?)
   - Build dataset for future behavioral tuning

### Functional Requirements

1. **Just-In-Time Information Disclosure**
   - Remove `phase_content` from `start_workflow` response (information leakage)
   - Force sequential calls: `start_workflow` → `get_phase` → `get_task` → `complete_phase`
   - No lookahead: can't know what's next without calling it

2. **Action-Specific Breadcrumb Navigation**
   - Each response includes exactly ONE next action (no choice)
   - Breadcrumb positioned at end (recency bias for AI decision weights)
   - Literal call syntax (copy-paste-execute, no interpretation needed)

3. **Support Both Workflow Types**
   - Static workflows (filesystem-based): need `get_task_count()` method
   - Dynamic workflows (cached): already have task count from `DynamicContentRegistry`

### Non-Functional Requirements

1. **Simplicity**
   - No over-engineering (inline logic, not strategy pattern)
   - Readable (all logic in one place)
   - Maintainable (simple = easy to change)

2. **Performance**
   - Task count retrieval must be fast (`glob()` for task files)
   - Only called once per `get_task` action

3. **Backward Compatibility**
   - `breadcrumb` parameter optional (non-breaking change)
   - Existing guidance preserved
   - Only adds fields, doesn't remove

### Out of Scope

1. **NOT forcing `complete_task` per task** (too granular, evidence validation works at phase level)
2. **NOT preventing file reading** (can't control, just make tools more attractive)
3. **NOT adding task-level evidence validation** (complexity not justified)
4. **NOT implementing strategy pattern** (KISS principle applies here)

---

## Design Insights

### Architectural Patterns

1. **Behavioral Probability Engineering**
   - Core principle: Maximize probability of desired action through decision weight factors
   - Decision weights: Recency bias (last content = highest weight), visual emphasis (emojis), imperative language (commands > suggestions), singularity (one action > multiple options)

2. **Breadcrumb Trail Pattern**
   - Each response reveals only the NEXT action (not the full chain)
   - Positioned at response end (recency bias)
   - Uses visual anchors: ⚡ (action directive), 🎯 (position marker), ✅ (completion)

3. **Inline Logic Over Abstraction**
   - Simple conditionals in each action handler (not separate strategy class)
   - Helper method for task count (`_get_task_count_for_phase`)
   - Rationale: String formatting with 3-4 cases doesn't need abstraction

### Component Design

1. **Modified `add_workflow_guidance()` Function**
   - Accepts optional `breadcrumb` parameter
   - Positions breadcrumb at end of response (dict ordering preserved in Python 3.7+)
   - Non-breaking: breadcrumb optional

2. **New `WorkflowRenderer.get_task_count()` Method**
   - For static workflows only
   - Counts `task-*-*.md` files in phase directory
   - Graceful error handling (raises `RendererError` if phase not found)

3. **New `WorkflowEngine._get_task_count_for_phase()` Helper**
   - Dynamic routing for static vs. dynamic workflows
   - Encapsulates task count logic in one place
   - Dynamic: from `DynamicContentRegistry`
   - Static: from `WorkflowRenderer`

### Data Flow

1. **Breadcrumb Chain**
   - `start_workflow` → "call `get_phase(0)`"
   - `get_phase(0)` → "call `get_task(0, 1)`"
   - `get_task(0, 1)` → "call `get_task(0, 2)`"
   - `get_task(0, N)` (final) → "call `complete_phase(0, evidence={...})`"
   - `complete_phase(0, ...)` → "call `get_phase(1)`"

2. **Task Position Detection**
   - If `task_number < task_count` → point to next task
   - If `task_number == task_count` → point to `complete_phase`
   - Special case: phase with no tasks → point directly to `complete_phase`

### UI/UX Considerations

1. **Visual Emphasis with Emojis**
   - ⚡ = Action directive (bright, attention-grabbing)
   - 🎯 = Position marker ("you are here")
   - ✅ = Phase complete (positive reinforcement)
   - 🎉 = Workflow complete (celebration)
   - 📊 = Phase info (context)

2. **Field Naming Convention**
   - `⚡_NEXT_ACTION`: Literal call syntax for next action
   - `🎯_CURRENT_POSITION`: Task N/M indicator
   - `✅_PHASE_COMPLETE`: Success message
   - `📊_PHASE_INFO`: Task count context

### Trade-Offs Made

1. **Simplicity vs. Extensibility**
   - **Chose:** Simplicity (inline logic)
   - **Rejected:** Extensibility (strategy pattern)
   - **Rationale:** String formatting doesn't need abstraction

2. **Information Disclosure vs. UX**
   - **Chose:** Remove `phase_content` from `start_workflow`
   - **Trade-off:** One extra call for compliant AIs
   - **Rationale:** Just-in-time disclosure prevents lookahead

3. **Emoji Usage vs. Clarity**
   - **Chose:** Use emojis for attention anchors
   - **Risk:** Some environments may not render emojis
   - **Mitigation:** Descriptive field names work without emojis

---

## Implementation Insights

### Code Changes Required

1. **`.praxis-os/ouroboros/subsystems/workflow/guidance.py`**
   - Modify `add_workflow_guidance(response, breadcrumb=None)` signature
   - Accept optional breadcrumb parameter
   - Position breadcrumb at end: `guided.update(breadcrumb)` after merging response

2. **`.praxis-os/ouroboros/subsystems/workflow/workflow_renderer.py`**
   - Add `get_task_count(workflow_type, phase)` method
   - Implementation: `task_files = list(phase_dir.glob("task-*-*.md")); return len(task_files)`
   - Error handling: Raise `RendererError` if phase directory not found

3. **`.praxis-os/ouroboros/subsystems/workflow/engine.py`**
   - Add `_get_task_count_for_phase(state, phase)` helper
   - Modify `start_workflow()`: Remove `phase_content`, add breadcrumb `"⚡_NEXT_ACTION": "get_phase(phase=0)"`
   - Modify `get_phase()`: Add breadcrumb to first task or `complete_phase` (if no tasks)
   - Modify `get_task()`: Add dynamic breadcrumb based on task position
   - Modify `complete_phase()`: Add breadcrumb to next phase or completion message

### Testing Strategy

1. **Unit Tests**
   - `test_get_task_count_static_workflow()`: Verify glob counting
   - `test_get_task_count_dynamic_workflow()`: Verify registry lookup
   - `test_breadcrumb_generation_first_task()`: Verify points to task 2
   - `test_breadcrumb_generation_middle_task()`: Verify points to next task
   - `test_breadcrumb_generation_final_task()`: Verify points to `complete_phase`
   - `test_breadcrumb_generation_no_tasks()`: Verify edge case handling

2. **Integration Tests**
   - `test_full_workflow_breadcrumbs_static()`: Validate breadcrumbs throughout static workflow
   - `test_full_workflow_breadcrumbs_dynamic()`: Validate breadcrumbs throughout dynamic workflow
   - `test_start_workflow_no_phase_content()`: Verify information leakage fix

3. **Behavioral Tests (Manual)**
   - Run workflows with different AI models (Sonnet, Haiku, GPT-4)
   - Observe if AIs follow breadcrumbs
   - Track action sequences (log analysis)

### Code Patterns & Examples

1. **Helper Method for Task Count**
   ```python
   def _get_task_count_for_phase(self, state: WorkflowState, phase: int) -> int:
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

2. **Breadcrumb Logic in `get_task()`**
   ```python
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
   
   return add_workflow_guidance(response, breadcrumb=breadcrumb)
   ```

3. **Breadcrumb in `start_workflow()`**
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
   
   breadcrumb = {
       "⚡_NEXT_ACTION": "get_phase(phase=0)",
   }
   
   return add_workflow_guidance(response, breadcrumb=breadcrumb)
   ```

### Deployment Considerations

1. **Backward Compatibility**
   - `breadcrumb` parameter optional (defaults to `None`)
   - Existing workflows continue to work
   - Compliant AIs not disrupted

2. **Performance Impact**
   - Task count retrieval via `glob()` is fast for small directories
   - Called once per `get_task` (not on every operation)
   - Can cache task count per phase if needed later

3. **Monitoring & Observability**
   - Track breadcrumb following rate: % of sessions where AI's next action matches `⚡_NEXT_ACTION`
   - Track engagement rate: % of workflow sessions that call `get_task` for all tasks
   - Track evidence validation failure rate: % of `complete_phase` calls that fail validation

### Risks & Edge Cases

1. **Edge Case: Phase with No Tasks**
   - `get_phase()` should return breadcrumb pointing directly to `complete_phase`
   - Handled: `if task_count > 0: ... else: ... ` logic

2. **Risk: Breadcrumbs Might Not Change AI Behavior**
   - Mitigation: Evidence validation still catches bypasses at phase gate
   - Mitigation: Track behavioral metrics to iterate on format/positioning

3. **Risk: Task Count Retrieval Performance**
   - Likelihood: Low
   - Mitigation: `glob()` is fast, can cache if needed

### Success Metrics

1. **Engagement Rate**
   - Baseline: 99% (current, for compliant AIs)
   - Target: 99.9% (catch outlier AIs)

2. **Breadcrumb Following Rate**
   - Target: >95% of sessions follow `⚡_NEXT_ACTION`

3. **Evidence Validation Failure Rate**
   - Baseline: <5% (current)
   - Target: <5% (no increase)

---

## Cross-Cutting Concerns

### Related Standards

- **Adversarial Design for AI Systems**: Evidence validation, hidden requirements
- **Workflow Discovery Patterns**: Dynamic workflow content loading
- **MCP Tool Design**: Response structure, field naming conventions

### Open Questions for Discussion

1. **Should we A/B test breadcrumb formats?**
   - Different emoji choices (⚡ vs 🔹 vs ⚠️)
   - Field name variations (`_NEXT_ACTION` vs `_EXECUTE_NEXT`)
   - Positioning experiments (last vs first)

2. **Should we log breadcrumb following behavior?**
   - Track when AI's next action matches breadcrumb
   - Build behavioral dataset for future tuning

3. **Should we add config for emoji enable/disable?**
   - Some environments may not render emojis well
   - Power users may prefer minimal output

### Dependencies

- **Workflow subsystem** (engine, renderer, guidance)
- **Dynamic workflow registry** (for task count retrieval)
- **Session state management** (persists workflow state)

---

## Insights Summary

**Key Takeaway:** This is a behavioral probability engineering solution, not a hard enforcement. The goal is to make the "correct path" (sequential execution) the "easiest path" (highest decision weight) for AI agents through just-in-time information disclosure, visual emphasis, and action-specific navigation.

**Implementation Philosophy:** Keep it simple. This is inline string formatting logic (3-4 cases), not a complex architecture. Simplicity = maintainability = success.

**Success Criteria:** Catch outlier AIs that bypass workflows (99% → 99.9% engagement), while maintaining UX for compliant AIs and enabling behavioral observability for future tuning.

