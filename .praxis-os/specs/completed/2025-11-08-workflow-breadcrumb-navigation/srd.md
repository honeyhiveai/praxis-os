# Software Requirements Document

**Project:** Workflow Breadcrumb Navigation System  
**Date:** 2025-11-08  
**Priority:** High  
**Category:** Enhancement

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for implementing a "breadcrumb trail" navigation pattern in the workflow subsystem to guide AI behavior through phase-gated workflows by making sequential execution the highest-probability decision.

### 1.2 Scope
This feature will modify the workflow engine to provide action-specific navigation breadcrumbs that reveal only the next action (not the full workflow chain), preventing information leakage and maximizing the probability that AI agents execute workflows sequentially rather than skipping steps.

---

## 2. Business Goals

### Goal 1: Maximize Deterministic AI Behavior Across All AI Models

**Objective:** Increase workflow engagement compliance from 99% (current baseline for compliant AIs) to 99.9% (catching outlier AIs that bypass workflow steps).

**Success Metrics:**
- **Engagement Rate**: 99% (current) → 99.9% (target)
  - Measured as: % of workflow sessions where AI calls `get_task` for all tasks (vs skipping to `complete_phase`)
- **Breadcrumb Following Rate**: Not measured currently → >95% (target)
  - Measured as: % of sessions where AI's next action matches the `⚡_NEXT_ACTION` breadcrumb

**Business Impact:**
- **Target Audience**: AI agents with varying capabilities (Claude Sonnet, Haiku, GPT-4, etc.) can reliably use praxis-os workflows
- **Reliability**: Workflow engagement becomes deterministic across all AI models, not just compliant ones
- **Observability**: Can track which AI models follow breadcrumbs vs. which ones skip, enabling behavioral analysis and future tuning

### Goal 2: Preserve Existing Working Behavior for Compliant AIs

**Objective:** Ensure the 99% of AI sessions that already engage properly with workflows continue to work without disruption or degraded UX.

**Success Metrics:**
- **Evidence Validation Failure Rate**: <5% (current) → <5% (target, no increase)
  - Measured as: % of `complete_phase` calls that fail validation
- **Backward Compatibility**: 100% of existing workflow sessions continue to work
  - Measured as: No breaking changes in workflow engine API

**Business Impact:**
- **User Trust**: Compliant AIs don't experience degraded UX or unexpected changes
- **Adoption**: Non-breaking change enables immediate deployment without migration
- **Development Velocity**: One extra call (`get_phase` after `start_workflow`) is negligible for performance-conscious AIs

### Goal 3: Enable Behavioral Observation and Data Capture

**Objective:** Build a dataset of AI behavioral patterns (do they follow breadcrumbs? do they skip tasks?) to inform future workflow UX tuning and AI capability research.

**Success Metrics:**
- **Behavioral Logging**: 0% of actions currently track breadcrumb following → 100% of workflow actions emit breadcrumb following metrics
- **Data Granularity**: Can answer "Which AI models skip steps?" and "Does emoji choice affect compliance?"

**Business Impact:**
- **Product Intelligence**: Evidence-based decisions for future workflow UX improvements
- **Research Value**: Dataset of AI behavioral patterns under structured constraints (unique research contribution)
- **Continuous Improvement**: Can A/B test breadcrumb formats and iterate based on real behavioral data

---

## 2.1 Supporting Documentation

The business goals above are informed by:
- **2025-11-08-workflow-breadcrumb-navigation.md**: Edge case discovery during stress testing, 99% compliance baseline, outlier AI bypass pattern analysis

See `supporting-docs/INDEX.md` and `supporting-docs/INSIGHTS.md` for complete analysis.

---

## 3. User Stories

User stories describe the feature from the user's perspective.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: AI Agent Guided Through Workflow

**As an** AI agent executing a workflow  
**I want to** receive explicit next-action instructions after each workflow action  
**So that** I don't have to infer or guess what to do next, reducing the probability I'll skip steps or optimize incorrectly

**Acceptance Criteria:**
- Given I have called `start_workflow`, When I receive the response, Then it includes `⚡_NEXT_ACTION: "get_phase(phase=0)"` without full phase content
- Given I have called `get_phase(0)`, When I receive the response, Then it includes `⚡_NEXT_ACTION: "get_task(phase=0, task_number=1)"` and task count
- Given I have called `get_task(0, 2)` (task 2 of 5), When I receive the response, Then it includes `⚡_NEXT_ACTION: "get_task(phase=0, task_number=3)"`
- Given I have called the final task, When I receive the response, Then it includes `⚡_NEXT_ACTION: "complete_phase(phase=0, evidence={...})"`

**Priority:** Critical

### Story 2: Outlier AI Agent Prevented from Skipping Steps

**As an** AI agent with high capability (e.g., Claude Sonnet 4.5)  
**I want to** not be able to see future workflow content in initial responses  
**So that** I'm incentivized to engage with the workflow sequentially rather than bypassing it

**Acceptance Criteria:**
- Given I call `start_workflow`, When I inspect the response, Then `phase_content` is NOT present (no information leakage)
- Given I want to read Phase 0 content, When I check my options, Then I must call `get_phase(0)` (just-in-time disclosure enforced)
- Given I call `get_phase`, When I inspect the response, Then I receive phase overview but task details require calling `get_task` for each

**Priority:** Critical

### Story 3: Compliant AI Agent Not Disrupted

**As an** AI agent that already follows workflow discipline  
**I want to** continue using workflows exactly as before  
**So that** my existing behavior patterns and scripts don't break

**Acceptance Criteria:**
- Given I call workflow actions in sequence, When breadcrumbs are present, Then I can ignore them (they're guidance, not enforcement)
- Given I was calling `get_phase` before, When I continue calling it, Then the response includes both phase content and breadcrumb (backward compatible)
- Given I complete phases with proper evidence, When I submit evidence, Then validation passes exactly as before (no new requirements)

**Priority:** High

### Story 4: Human Developer Observing AI Behavior

**As a** human developer observing AI workflow execution  
**I want to** see whether the AI followed breadcrumb navigation or deviated  
**So that** I can understand which AI models comply and which need additional behavioral tuning

**Acceptance Criteria:**
- Given an AI executes a workflow, When I review execution logs, Then I can see which actions were called and in what order
- Given breadcrumbs were provided, When I analyze compliance, Then I can calculate breadcrumb following rate (% of next actions that matched breadcrumb)
- Given multiple AI models execute the same workflow, When I compare behavioral data, Then I can identify which models skip steps

**Priority:** Medium

---

## 3.1 Story Priority Summary

**Critical (Must-Have):**
- Story 1: AI Agent Guided Through Workflow
- Story 2: Outlier AI Agent Prevented from Skipping Steps

**High Priority:**
- Story 3: Compliant AI Agent Not Disrupted

**Medium Priority:**
- Story 4: Human Developer Observing AI Behavior

---

## 3.2 Supporting Documentation

User needs from supporting documents:
- **2025-11-08-workflow-breadcrumb-navigation.md**: Edge case of outlier AI bypassing workflows, need for sequential execution guidance, preserving UX for 99% of compliant AIs

See `supporting-docs/INSIGHTS.md` for detailed user need analysis.

---

## 4. Functional Requirements

Functional requirements specify capabilities the system must provide.

---

### FR-001: Just-In-Time Information Disclosure in start_workflow

**Description:** The system shall NOT include `phase_content` in the `start_workflow` response, forcing AI agents to call `get_phase` to retrieve phase information.

**Priority:** Critical

**Related User Stories:** Story 1 (AI Agent Guided), Story 2 (Outlier AI Prevented)

**Acceptance Criteria:**
- `start_workflow` response does NOT contain `phase_content` field
- `start_workflow` response includes only `workflow_overview` with high-level metadata (max_phase, description)
- AI agents must call `get_phase(0)` to receive Phase 0 content
- No lookahead: cannot see future phase content without calling `get_phase` for that phase

---

### FR-002: Action-Specific Breadcrumb in start_workflow

**Description:** The system shall include an action-specific breadcrumb in `start_workflow` response that directs AI agents to call `get_phase(phase=0)` as the next action.

**Priority:** Critical

**Related User Stories:** Story 1 (AI Agent Guided)

**Acceptance Criteria:**
- `start_workflow` response includes `⚡_NEXT_ACTION: "get_phase(phase=0)"` field
- Breadcrumb positioned at end of response dictionary (Python 3.7+ dict ordering)
- Literal call syntax (exact function signature with parameters)
- Uses emoji anchor (⚡) for visual emphasis

---

### FR-003: Action-Specific Breadcrumb in get_phase

**Description:** The system shall include an action-specific breadcrumb in `get_phase` response that directs AI agents to call either `get_task(phase=N, task_number=1)` if tasks exist, or `complete_phase(phase=N, evidence={...})` if no tasks exist.

**Priority:** Critical

**Related User Stories:** Story 1 (AI Agent Guided)

**Acceptance Criteria:**
- `get_phase` response includes `📊_PHASE_INFO: "Phase N has M tasks"` field
- If `task_count > 0`: response includes `⚡_NEXT_ACTION: "get_task(phase=N, task_number=1)"`
- If `task_count == 0`: response includes `⚡_NEXT_ACTION: "complete_phase(phase=N, evidence={...})"`
- Breadcrumb positioned at end of response dictionary

---

### FR-004: Dynamic Breadcrumb in get_task Based on Task Position

**Description:** The system shall include a position-aware breadcrumb in `get_task` response that directs AI agents to either the next task or `complete_phase` depending on whether the current task is the final task in the phase.

**Priority:** Critical

**Related User Stories:** Story 1 (AI Agent Guided)

**Acceptance Criteria:**
- `get_task` response includes `🎯_CURRENT_POSITION: "Task N/M"` field indicating current task number and total
- If `task_number < task_count`: response includes `⚡_NEXT_ACTION: "get_task(phase=P, task_number=N+1)"`
- If `task_number == task_count`: response includes `⚡_NEXT_ACTION: "complete_phase(phase=P, evidence={...})"` and `🎯_CURRENT_POSITION: "Task N/M (final)"`
- Breadcrumb positioned at end of response dictionary

---

### FR-005: Breadcrumb in complete_phase to Next Phase

**Description:** The system shall include a breadcrumb in `complete_phase` response that directs AI agents to either the next phase or indicates workflow completion.

**Priority:** High

**Related User Stories:** Story 1 (AI Agent Guided)

**Acceptance Criteria:**
- If more phases exist: response includes `✅_PHASE_COMPLETE: "Phase N completed successfully"` and `⚡_NEXT_ACTION: "get_phase(phase=N+1)"`
- If workflow complete: response includes `🎉_WORKFLOW_COMPLETE: "All phases completed successfully"` with no next action
- Breadcrumb positioned at end of response dictionary

---

### FR-006: Task Count Retrieval for Static Workflows

**Description:** The system shall provide a method to retrieve task count for static (filesystem-based) workflows by counting `task-*-*.md` files in the phase directory.

**Priority:** Critical

**Related User Stories:** Story 1 (AI Agent Guided)

**Acceptance Criteria:**
- `WorkflowRenderer.get_task_count(workflow_type, phase)` method exists
- Method returns count of files matching glob pattern `task-*-*.md` in `phases/{phase}/` directory
- Method raises `RendererError` if phase directory does not exist
- Method is performant (uses `glob()`, not recursive directory walk)

---

### FR-007: Task Count Retrieval for Dynamic Workflows

**Description:** The system shall retrieve task count for dynamic (cached) workflows from the `DynamicContentRegistry.get_phase_metadata()` method.

**Priority:** Critical

**Related User Stories:** Story 1 (AI Agent Guided)

**Acceptance Criteria:**
- `DynamicContentRegistry.get_phase_metadata(phase)` returns dictionary with `task_count` field
- Task count reflects number of tasks parsed from spec's `tasks.md` file
- Task count is cached (not re-parsed on every call)

---

### FR-008: Unified Task Count Helper Method

**Description:** The system shall provide a unified helper method in `WorkflowEngine` that routes task count retrieval to the appropriate source (static renderer vs. dynamic registry) based on workflow type.

**Priority:** Critical

**Related User Stories:** Story 1 (AI Agent Guided)

**Acceptance Criteria:**
- `WorkflowEngine._get_task_count_for_phase(state, phase)` method exists
- If dynamic workflow and `phase > 0`: retrieves from `DynamicContentRegistry`
- Otherwise: retrieves from `WorkflowRenderer.get_task_count()`
- Single point of logic for task count retrieval (no duplication)

---

### FR-009: Backward Compatible Breadcrumb Parameter

**Description:** The system shall accept an optional `breadcrumb` parameter in the `add_workflow_guidance()` function to ensure non-breaking change for existing code.

**Priority:** High

**Related User Stories:** Story 3 (Compliant AI Not Disrupted)

**Acceptance Criteria:**
- `add_workflow_guidance(response, breadcrumb=None)` signature
- If `breadcrumb=None`: response includes only static guidance fields (existing behavior)
- If `breadcrumb` provided: response includes static guidance + breadcrumb fields
- Breadcrumb fields positioned at end of response dictionary
- No changes required to existing callers (optional parameter)

---

### FR-010: Static Guidance Fields Preserved

**Description:** The system shall continue to include static workflow guidance fields (`⚠️_WORKFLOW_EXECUTION_MODE`, `🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS`, `execution_model`) in all workflow responses.

**Priority:** High

**Related User Stories:** Story 3 (Compliant AI Not Disrupted)

**Acceptance Criteria:**
- `WORKFLOW_GUIDANCE_FIELDS` dictionary unchanged
- Static fields prepended to all responses (before breadcrumb)
- Existing behavior for compliant AIs preserved

---

## 4.1 Requirements by Category

### Breadcrumb Generation (Core Functionality)
- FR-002: start_workflow breadcrumb
- FR-003: get_phase breadcrumb
- FR-004: get_task dynamic breadcrumb
- FR-005: complete_phase breadcrumb

### Information Disclosure Control
- FR-001: Just-in-time disclosure (remove phase_content from start_workflow)

### Task Count Infrastructure
- FR-006: Static workflow task count
- FR-007: Dynamic workflow task count
- FR-008: Unified task count helper

### Backward Compatibility
- FR-009: Optional breadcrumb parameter
- FR-010: Static guidance preserved

---

## 4.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority |
|-------------|--------------|----------------|----------|
| FR-001 | Story 1, 2 | Goal 1 | Critical |
| FR-002 | Story 1 | Goal 1 | Critical |
| FR-003 | Story 1 | Goal 1 | Critical |
| FR-004 | Story 1 | Goal 1 | Critical |
| FR-005 | Story 1 | Goal 1 | High |
| FR-006 | Story 1 | Goal 1 | Critical |
| FR-007 | Story 1 | Goal 1 | Critical |
| FR-008 | Story 1 | Goal 1 | Critical |
| FR-009 | Story 3 | Goal 2 | High |
| FR-010 | Story 3 | Goal 2 | High |

---

## 4.3 Supporting Documentation

Requirements informed by:
- **2025-11-08-workflow-breadcrumb-navigation.md**: Detailed design for breadcrumb pattern, task count retrieval, just-in-time disclosure, backward compatibility strategy

See `supporting-docs/INSIGHTS.md` for implementation insights from design document.

---

## 5. Non-Functional Requirements

NFRs define quality attributes and system constraints.

---

### 5.1 Performance

**NFR-P1: Task Count Retrieval Performance**
- Task count retrieval via `glob()` for static workflows: <5ms for directories with <50 task files
- Task count retrieval from `DynamicContentRegistry`: <1ms (cached lookup)
- No performance degradation for existing workflow operations (evidence validation, state persistence)

**NFR-P2: Breadcrumb Generation Overhead**
- Breadcrumb generation (string formatting + conditionals): <1ms per action
- No measurable impact on end-to-end workflow execution time (<1% increase acceptable)

---

### 5.2 Maintainability

**NFR-M1: Code Simplicity (KISS Principle)**
- Breadcrumb logic implemented as inline conditionals (not strategy pattern or separate class)
- All breadcrumb generation logic in one file (`engine.py`) for readability
- No more than 3-4 conditional branches per action handler
- Comments explain decision weight factors (recency bias, visual emphasis, etc.)

**NFR-M2: Code Quality**
- Test coverage: minimum 80% for new code (breadcrumb generation, task count retrieval)
- Pylint: 10/10 score (no linting errors)
- Type hints: 100% of function signatures

**NFR-M3: Documentation Quality**
- Inline docstrings for all new methods (Sphinx format)
- Design rationale documented in comments (why inline logic, why emojis, etc.)
- Examples in docstrings for breadcrumb generation logic

---

### 5.3 Backward Compatibility

**NFR-C1: Non-Breaking API Changes**
- `add_workflow_guidance(breadcrumb=None)`: optional parameter ensures no breaking changes
- Existing workflow callers require zero code changes
- Existing workflow sessions continue to work after deployment

**NFR-C2: Graceful Degradation**
- If breadcrumb generation fails (exception): workflow continues with static guidance only (no crash)
- If task count retrieval fails: workflow logs error and continues (no workflow termination)

---

### 5.4 Usability

**NFR-U1: Breadcrumb Clarity**
- Breadcrumb uses literal call syntax (exact function signature with parameters)
- No interpretation required: AI can copy-paste breadcrumb content directly into tool call
- Visual anchors (emojis) increase attention weight without reducing clarity

**NFR-U2: Error Messages**
- If task count retrieval fails for static workflow: error message includes `mkdir` command to fix
- If breadcrumb generation fails: log includes phase/task context for debugging

---

### 5.5 Reliability

**NFR-R1: Evidence Validation Preserved**
- Evidence validation failure rate: <5% (current baseline, no increase)
- Phase gate enforcement unchanged (breadcrumbs are guidance, evidence validation is enforcement)

**NFR-R2: No Workflow Interruption**
- Breadcrumb failures do not block workflow execution
- Workflow state persistence unaffected by breadcrumb logic

---

### 5.6 Observability

**NFR-O1: Behavioral Metrics Collection**
- All workflow actions emit metrics indicating whether breadcrumb was provided
- Metrics include: `breadcrumb_provided`, `breadcrumb_action`, `actual_next_action`
- Can calculate breadcrumb following rate post-deployment (target: >95%)

**NFR-O2: Debugging Support**
- Breadcrumbs visible in workflow response JSON (human-readable)
- Breadcrumb generation logic traceable via logs (DEBUG level)

---

### 5.7 Supporting Documentation

NFRs informed by:
- **2025-11-08-workflow-breadcrumb-navigation.md**: Performance constraints (glob is fast), simplicity requirements (inline logic, not strategy pattern), backward compatibility needs, visual emphasis rationale (emojis)

See `supporting-docs/INSIGHTS.md` for detailed trade-off analysis.

---

## 6. Out of Scope

Explicitly defines what is NOT included. Items may be considered for future phases.

### Explicitly Excluded

---

#### Features

**Not Included in This Release:**

1. **Task-Level Evidence Validation (`complete_task` action)**
   - **Reason:** Evidence validation at phase level is sufficient. Task-level validation adds ceremony without meaningful quality improvement. Requires defining evidence schemas for every task (high complexity, low ROI).
   - **Future Consideration:** Not planned. Phase-level evidence validation works for 99% of cases. If needed, can be added to specific workflows without changing engine architecture.

2. **Preventing Direct File Reading**
   - **Reason:** Cannot control AI behavior (probabilistic models). If AI decides to read workflow files directly (bypassing MCP tools), we cannot prevent it. Our goal is to make MCP tools *more attractive* (better UX, explicit guidance), not enforce exclusive use.
   - **Future Consideration:** Not technically feasible. Focus remains on making breadcrumb navigation the "easy path."

3. **A/B Testing Breadcrumb Formats**
   - **Reason:** Initial deployment should validate core concept first. Format variations (emoji choices, field names, positioning) can be tested post-deployment once behavioral metrics are collected.
   - **Future Consideration:** Potential Phase 2 if behavioral data shows room for optimization.

4. **Configurable Emoji Enable/Disable**
   - **Reason:** Adds complexity without clear demand. Field names (`_NEXT_ACTION`) are descriptive even without emojis. Can be added if users request it.
   - **Future Consideration:** Potential Phase 2 if accessibility concerns or user feedback warrants it.

5. **Strategy Pattern for Breadcrumb Generation**
   - **Reason:** Inline logic is simpler and sufficient for 3-4 action types. Strategy pattern is premature abstraction for string formatting. KISS principle applies.
   - **Future Consideration:** If breadcrumb logic becomes complex (>10 action types, multiple format strategies), refactor to strategy pattern. Not expected for foreseeable future.

6. **Task Count Caching for Static Workflows**
   - **Reason:** `glob()` is already fast (<5ms). Caching adds complexity (cache invalidation, memory overhead) without measurable performance benefit.
   - **Future Consideration:** If profiling shows task count retrieval as bottleneck (unlikely), add caching in Phase 2.

---

#### Behavioral Enforcement

**Not Included:**

- **Hard Blocking of Task Skipping**: Breadcrumbs are behavioral guidance (probability engineering), not hard enforcement. Evidence validation at phase gate remains the ultimate enforcement mechanism. Attempting to block skipping would be brittle and could break legitimate edge cases.

- **Per-Action Compliance Validation**: No real-time validation that AI followed breadcrumb (e.g., "Did you call the action we suggested?"). This is tracked via behavioral metrics post-deployment but not enforced during execution.

---

#### Metrics & Observability

**Not Included in Initial Release:**

- **Real-Time Dashboards for Breadcrumb Following Rate**: Behavioral metrics will be logged, but no UI/dashboard for visualizing compliance. This can be added in Phase 2 after data collection infrastructure is validated.

- **AI Model Fingerprinting**: No automatic detection of which AI model is executing (Claude, GPT-4, etc.). Metrics will show behavioral patterns but not model identity unless provided via telemetry.

---

#### Platforms & Integrations

**Fully Supported:**
- All workflows (static and dynamic) in praxis-os
- All MCP-capable AI clients

**Not Applicable:**
- This feature is internal to the workflow subsystem. No external platform or integration concerns.

---

## 6.1 Future Enhancements

**Potential Phase 2 (Post-Deployment Observations):**
- A/B testing of breadcrumb formats (emoji variations, field naming, positioning experiments)
- Real-time dashboard for breadcrumb following rate by AI model
- Configurable emoji enable/disable (if accessibility concerns arise)
- Additional behavioral metrics (time between actions, retry patterns, evidence quality correlation)

**Potential Phase 3 (If Complexity Grows):**
- Strategy pattern refactor (if breadcrumb logic becomes complex)
- Task count caching (if performance profiling shows bottleneck)

**Explicitly Not Planned:**
- Task-level evidence validation
- Hard enforcement of breadcrumb following (against design philosophy)
- Preventing file reading (not technically feasible)

---

## 6.2 Supporting Documentation

Out-of-scope items from:
- **2025-11-08-workflow-breadcrumb-navigation.md**: Non-goals section, options considered and rejected, trade-off analysis

See `supporting-docs/INSIGHTS.md` for detailed rationale on excluded features.

