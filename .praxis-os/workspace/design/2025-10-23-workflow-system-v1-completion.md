# Workflow System v1 Completion Design
**Date**: 2025-10-23  
**Author**: Agent OS Team  
**Status**: Design Phase  
**Target**: Workflow System v1.0 Production Ready

---

## Problem Statement

The Agent OS Enhanced workflow system is **architecturally complete** but has **critical implementation gaps** that prevent it from being production-ready:

### What's Broken
1. **Validation system bypassed** - Implemented Oct 20 but never enabled (session.py:504: `checkpoint_passed = True`)
   - AI can pass any evidence, defeating checkpoint purpose
   - 36 gate-definition.yaml files exist but unused
   - Multi-layer validation (4 layers) sitting idle

2. **Session state incomplete** - Missing critical information
   - No lifecycle flags (must calculate `is_complete()`)
   - No phase timing (can't estimate progress)
   - No AI resumption context (high cognitive load)
   - `current_phase` can go out of range (6 for 0-5 phases)

3. **Core workflow set incomplete** - Missing 5th workflow
   - `standards_creation_v1` exists in hive-kube (since Oct 13)
   - Not rolled out to agent-os-enhanced
   - Should be part of universal core set

### Impact If Not Solved
- **Validation bypass**: AI can game checkpoints, no quality enforcement
- **Poor session state**: AI must recalculate status on every load, MCP restart loses context
- **Incomplete core set**: Users can't create standards systematically
- **Bootstrap problem**: Validation system validated itself while validation off

### Why This Matters
Agent OS Enhanced is 16 days old with impressive velocity (35 commits, 4 core workflows). But the validation system is a **fortress with open gates** - beautifully designed but not protecting anything. Session state requires **AI to do math** instead of reading status. This blocks v1.0 production readiness.

---

## Goals & Non-Goals

### Goals (v1.0 Must Have)

**Goal 1: Validation System Operational**
- Evidence validation enabled in production
- Monitored and tuned based on real usage
- Trust metrics established
- Gradual rollout to strict mode

**Goal 2: Robust Session State**
- Explicit lifecycle flags (`completed`, `paused`, `failed_phase`)
- Complete phase timing (`started_at`, `completed_at`, `duration_seconds`)
- AI resumption context computed on load
- No out-of-range phase numbers
- Session integrity validation

**Goal 3: Complete Core Workflow Set**
- All 5 core workflows available
- `standards_creation_v1` rolled out to universal/
- All phases have gate-definition.yaml
- Dogfooding validation complete

**Goal 4: Self-Validating System**
- Validation system validates itself
- Evidence validation spec re-executed with validation on
- Trust metrics collected
- Bootstrap problem acknowledged and addressed

### Non-Goals (Post-v1)

Valuable but deferred to v1.1+:
- ❌ Pause/resume support (manual checkpoints work)
- ❌ Rollback support (state persistence sufficient)
- ❌ Command execution tracking (evidence captures outcomes)
- ❌ Performance monitoring/Prometheus (basic logging sufficient)
- ❌ Workflow marketplace (extensibility works)
- ❌ Multi-user collaboration (single-agent model)

---

## Current State Analysis

### Architecture Overview

```
MCP Tools (workflow_tools/)
  ↓
WorkflowEngine (session cache, metadata loader, validation orchestrator)
  ↓
WorkflowSession (session-scoped execution, dynamic registry)
  ↓
DynamicContentRegistry (template rendering, AST parsing) [for dynamic workflows]
  ↓
StateManager (JSON persistence, file locking, lifecycle)
```

### What Works Well

**✅ Core Architecture (Production Quality)**
- Thread-safe session management (double-checked locking, RLock)
- Dynamic workflow system (SpecTasksParser, WorkflowDefinitionParser)
- Modular design (clean separation of concerns)
- Comprehensive MCP tool (`aos_workflow` with 14 actions)
- 151 tests (150 passing), 99.3% coverage

**✅ Evidence Validation System (Complete, Disabled)**
- CheckpointLoader: Three-tier fallback (YAML → RAG → permissive)
- ValidatorExecutor: Safe lambda execution (restricted globals, security tested)
- FieldSchema: Type checking (boolean, integer, string, object, list)
- CrossFieldRule: Multi-field validation (lambda expressions)
- 36 gate-definition.yaml files (all 4 core workflows × phases)
- **Intentionally disabled** for staged rollout (Oct 20, 2025)

**✅ 4 Core Workflows Shipping**
- `spec_creation_v1`: Create comprehensive specs (6 phases)
- `spec_execution_v1`: Execute specs dynamically (Phase 0 + dynamic 1-N)
- `workflow_creation_v1`: Create new workflows (meta-framework, 6 phases)
- `agent_os_upgrade_v1`: Safe upgrade system (6 phases)

### What's Broken

**❌ Validation Bypassed (Critical)**

**Location:** `.praxis-os/mcp_server/core/session.py:504`
```python
# TODO: Implement _validate_checkpoint in workflow_engine (Tasks 1.2-1.7)
# For now, returning True to maintain backwards compatibility
checkpoint_passed = True  # ← BYPASSED!
```

**What exists:**
- `WorkflowEngine._validate_checkpoint()` fully implemented (lines 907-1066)
- Multi-layer validation: fields → types → validators → cross-field
- Structured output: errors, warnings, diagnostics, remediation, next_steps
- Security tested (45 tests), performance tested (26 tests)

**Why bypassed:**
- Oct 20 commit message: "Prepared for validation (TODO marker for integration)"
- Plan: "Progressive rollout: warnings → errors over time"
- Backwards compatibility concern

**Impact:**
- AI can submit `evidence: {"fake": true}` and pass
- Validation gates are decorative
- No enforcement of proof requirements

**❌ Session State Incomplete**

**Current Structure (models/workflow.py):**
```python
@dataclass
class WorkflowState:
    session_id: str
    workflow_type: str
    target_file: str
    current_phase: int                    # ⚠️ Can be out of range
    completed_phases: List[int]           # [0,1,2,3,4,5]
    phase_artifacts: Dict[int, PhaseArtifact]
    checkpoints: Dict[int, CheckpointStatus]
    created_at: datetime                  # ✅ Session start
    updated_at: datetime                  # ⚠️ Last ANY update (not phase-specific)
    metadata: Dict[str, Any]              # {total_phases: 6, spec_path: "..."}
```

**Missing:**
1. **No lifecycle flags** - Must calculate `is_complete()` every time
2. **No phase timing** - Only `timestamp` in PhaseArtifact (completion time)
3. **No resumption context** - AI must recalculate progress, next actions, suggestions
4. **current_phase sentinel issue** - For 0-5 phases, becomes 6 when complete (invalid!)
5. **commands_executed never populated** - Always empty list
6. **Generic metadata** - No schema, inconsistent across sessions

**Example from production:**
```json
{
  "session_id": "062f24e7-6fdc-40b3-a2d8-7ffaea6351b6",
  "current_phase": 6,  // ← Phase 6 doesn't exist! (0-5 workflow)
  "completed_phases": [0, 1, 2, 3, 4, 5],
  "metadata": {"spec_path": "...", "total_phases": 6}
}
```

**AI Experience on Session Load:**
```python
# What AI receives:
state = load_state(session_id)

# What AI must calculate:
is_complete = (state.current_phase >= state.metadata["total_phases"])  # recalculate
progress_percent = len(state.completed_phases) / total_phases * 100     # recalculate
time_elapsed = datetime.now() - state.created_at                        # calculate
average_phase_time = time_elapsed / len(state.completed_phases)         # calculate
estimated_remaining = average_phase_time * phases_remaining             # calculate
```

High cognitive load, error-prone, inefficient.

**❌ Missing Core Workflow**

`standards_creation_v1` exists in `../hive-kube/.praxis-os/workflows/` (created Oct 13):
- 6 phases: Discovery → Content → RAG Optimization → Discoverability Testing → Validation → Integration
- Well-tested in hive-kube
- Not rolled out to agent-os-enhanced `universal/workflows/`

Should be part of core set (5 workflows, not 4).

### What Exists But Needs Work

**⚠️ Completion Detection**

**Current Code (workflow.py:243-283):**
```python
def is_complete(self) -> bool:
    total_phases = self.metadata.get("total_phases")
    if total_phases is None:
        # Fallback for legacy sessions
        total_phases = 8 if "test" in self.workflow_type else 6
    
    # Detect 0-indexed vs 1-indexed
    if len(self.completed_phases) > 0:
        min_phase = min(self.completed_phases)
        zero_indexed = (min_phase == 0)
    else:
        zero_indexed = (self.current_phase == 0)
    
    if zero_indexed:
        return self.current_phase >= total_phases
    else:
        return self.current_phase > total_phases
```

**Issues:**
- Must recalculate every call
- Fragile zero-detection logic
- Fallback hardcoded (string matching)
- No validation that `total_phases` matches workflow

**Better:** Explicit `lifecycle.completed` flag, set once, read many times.

---

## Proposed Design

### Design Overview

**Approach:** Enable validation in lenient mode, redesign session state with explicit lifecycle, rollout standards_creation_v1, validate the validator.

**Core Principles:**
1. **Enable, don't rebuild** - Validation is done, just uncomment it
2. **Explicit over calculated** - Store lifecycle flags, don't recalculate
3. **AI-optimized state** - Provide resumption context, reduce cognitive load
4. **Self-validation** - Use system to validate itself
5. **Gradual rollout** - Lenient → strict, monitor before enforcing

### Component 1: Validation Enablement

**What Changes:**
- File: `.praxis-os/mcp_server/core/session.py`
- Line 504: Call `WorkflowEngine._validate_checkpoint()` instead of `checkpoint_passed = True`
- Mode: Start in `strict: false` (errors → warnings)

**Validation Flow:**
```
complete_phase(phase, evidence)
  ↓
WorkflowEngine._validate_checkpoint(workflow_type, phase, evidence)
  ↓
CheckpointLoader.load_checkpoint_requirements(workflow_type, phase)
  ↓ (three-tier fallback)
  ├─→ YAML: gate-definition.yaml (if exists)
  ├─→ RAG: Parse from phase.md (if YAML missing)
  └─→ Permissive: Accept all (if RAG fails)
  ↓
ValidatorExecutor (4 layers)
  ├─→ Layer 1: Required fields present?
  ├─→ Layer 2: Field types correct?
  ├─→ Layer 3: Custom validators pass?
  └─→ Layer 4: Cross-field rules pass?
  ↓
Result: {checkpoint_passed, errors, warnings, diagnostics, remediation}
```

**Strict vs. Lenient Mode:**
```yaml
# gate-definition.yaml
checkpoint:
  strict: false  # ← Lenient mode (errors → warnings)
  allow_override: true
```

- **Lenient mode**: All errors become warnings, checkpoint passes but logs issues
- **Strict mode**: Errors block phase completion, must fix before advancing
- **Rollout strategy**: Start lenient, tune rules, gradually enable strict

**Monitoring:**
- Log all validation results to `.praxis-os/.cache/validation-logs/{session_id}.json`
- Daily review: False positive rate, false negative rate
- Tune validation rules based on data
- After 1 week + tuning: Enable strict mode for new workflows

### Component 2: Session State Redesign

**New Structure:**

```python
@dataclass
class LifecycleState:
    """Explicit lifecycle flags (no calculation needed)."""
    completed: bool = False
    paused: bool = False
    failed_phase: Optional[int] = None
    error_message: Optional[str] = None

@dataclass
class PhaseTiming:
    """Complete timing data for one phase."""
    phase: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
@dataclass
class ResumptionContext:
    """Computed context for AI on session load."""
    progress_percent: float
    phases_completed: int
    phases_remaining: int
    current_phase_name: str
    total_duration_seconds: float
    average_phase_duration_seconds: float
    estimated_remaining_seconds: float
    next_actions: List[str]
    discovery_suggestions: List[str]

@dataclass
class WorkflowState:
    # Identity (unchanged)
    session_id: str
    workflow_type: str
    target_file: str
    
    # Structure snapshot (explicit, not calculated)
    current_phase: int                    # ← Never out of range
    completed_phases: List[int]
    total_phases: int                     # ← Always present
    starting_phase: int                   # ← 0 or 1
    workflow_version: str                 # ← From metadata.json
    indexing_scheme: str                  # ← "0-indexed" or "1-indexed"
    
    # Progress tracking (unchanged)
    phase_artifacts: Dict[int, PhaseArtifact]
    checkpoints: Dict[int, CheckpointStatus]
    
    # Lifecycle (NEW - explicit flags)
    lifecycle: LifecycleState
    
    # Timing (NEW - complete phase timing)
    phase_timings: Dict[int, PhaseTiming]
    
    # Timestamps (system-managed, never AI-submitted)
    created_at: datetime
    updated_at: datetime
    
    # Additional metadata (unchanged)
    metadata: Dict[str, Any]
    
    # Resumption context (computed on load, cached)
    _resumption_context: Optional[ResumptionContext] = None
```

**Key Behaviors:**

**1. Lifecycle Management**
```python
# On phase completion:
if self.current_phase == self.total_phases - 1:  # Last phase (0-indexed)
    self.lifecycle.completed = True
    # current_phase stays at last valid phase (5 for 0-5)
else:
    self.current_phase += 1

# is_complete() becomes trivial:
def is_complete(self) -> bool:
    return self.lifecycle.completed
```

**2. Phase Timing**
```python
# On get_current_phase():
if self.current_phase not in self.phase_timings:
    self.phase_timings[self.current_phase] = PhaseTiming(
        phase=self.current_phase,
        started_at=datetime.now()
    )

# On complete_phase():
timing = self.phase_timings[phase]
timing.completed_at = datetime.now()
timing.duration_seconds = (timing.completed_at - timing.started_at).total_seconds()
```

**3. Resumption Context**
```python
# Computed on load_state(), cached:
def get_resumption_context(self) -> ResumptionContext:
    if self._resumption_context is not None:
        return self._resumption_context
    
    # Calculate once:
    total_duration = (datetime.now() - self.created_at).total_seconds()
    completed_count = len(self.completed_phases)
    remaining_count = self.total_phases - completed_count
    
    avg_duration = total_duration / completed_count if completed_count > 0 else 0
    estimated_remaining = avg_duration * remaining_count
    
    # Compute next actions based on state:
    next_actions = []
    if self.lifecycle.completed:
        next_actions = ["Workflow complete - no further actions"]
    elif self.lifecycle.paused:
        next_actions = [f"Resume workflow: aos_workflow(action='resume', session_id='{self.session_id}')"]
    else:
        next_actions = [
            f"Get current phase: aos_workflow(action='get_phase', session_id='{self.session_id}')",
            f"Or get specific task: aos_workflow(action='get_task', session_id='{self.session_id}', phase={self.current_phase}, task_number=1)"
        ]
    
    # Compute discovery suggestions:
    suggestions = [
        f"Review {self.workflow_type} methodology: search_standards('{self.workflow_type} best practices')",
        f"Understand phase {self.current_phase}: search_standards('{self.workflow_type} phase {self.current_phase}')"
    ]
    
    self._resumption_context = ResumptionContext(
        progress_percent=(completed_count / self.total_phases * 100),
        phases_completed=completed_count,
        phases_remaining=remaining_count,
        current_phase_name=f"Phase {self.current_phase}",
        total_duration_seconds=total_duration,
        average_phase_duration_seconds=avg_duration,
        estimated_remaining_seconds=estimated_remaining,
        next_actions=next_actions,
        discovery_suggestions=suggestions
    )
    
    return self._resumption_context
```

**AI Experience After Redesign:**
```python
# AI receives:
state = load_state(session_id)
context = state.get_resumption_context()

# All information readily available:
is_complete = state.lifecycle.completed              # No calculation!
progress = context.progress_percent                  # Pre-computed
next_actions = context.next_actions                  # Ready to use
time_remaining = context.estimated_remaining_seconds # Estimated
```

**Migration Strategy:**

Legacy sessions need migration. Two approaches:

**Option A: Automatic Migration (On Load)**
```python
def load_state(session_id: str) -> WorkflowState:
    data = json.load(file)
    
    # Detect legacy session (missing lifecycle)
    if "lifecycle" not in data:
        logger.info("Migrating legacy session %s", session_id)
        data = _migrate_legacy_session(data)
    
    return WorkflowState.from_dict(data)
```

**Option B: Manual Migration Script**
```bash
python scripts/migrate-session-state-v2.py --dry-run  # Preview
python scripts/migrate-session-state-v2.py            # Execute
```

**Recommendation:** Option A (automatic) for convenience, but log migrations and offer Option B for batch processing.

### Component 3: standards_creation_v1 Rollout

**What to Copy:**
- Source: `../hive-kube/.praxis-os/workflows/standards_creation_v1/`
- Destination: `universal/workflows/standards_creation_v1/`
- Files: metadata.json, phases (0-5), core utilities, README.md

**What to Adapt:**
- Remove hive-kube specific references
- Update paths to `.praxis-os/` conventions
- Ensure RAG queries work universally
- Add gate-definition.yaml for all phases (if missing)

**Validation:**
- Test dogfooding: Create a new standard using the workflow
- Verify all 6 phases work
- Ensure discoverability testing phase functions
- Compare output to manually-created standards

### Component 4: Self-Validation

**The Bootstrap Problem:**

Evidence validation system was implemented via `spec_execution_v1` workflow while validation was disabled. **Can we trust validation that validated itself while validation was off?**

**Solution: External Validation + Self-Test**

**External Validation (Primary Trust):**
- 151 unit tests (150 passing)
- 45 security tests (all passing)
- 26 performance tests (all passing)
- 13 integration tests (all passing)
- Human code review (Oct 20 commit)

**Self-Test (Confidence Building):**
1. Re-execute evidence validation spec with validation ON
2. Compare results to original Oct 20 execution (validation OFF)
3. Question: Would validation have caught issues?
4. Measure: What changed?

**Trust Metrics Dashboard:**
```markdown
# Validation Trust Metrics

## Data Collection Period
Start: 2025-10-23
Duration: 1 week (minimum)

## Metrics
- Total validations run: X
- Pass rate: Y%
- Warning rate: Z%
- False positive count: N (manually reviewed)
- False negative count: M (issues found post-validation)

## Confidence Level
- Week 1: Low (monitoring, lenient mode)
- Week 2: Medium (tuned rules, still lenient)
- Week 3+: High (strict mode for new workflows)
```

**Audit Trail:**
```json
{
  "session_id": "...",
  "timestamp": "2025-10-23T12:34:56Z",
  "workflow_type": "spec_execution_v1",
  "phase": 2,
  "evidence": {...},
  "validation_result": {
    "checkpoint_passed": true,
    "errors": [],
    "warnings": ["field 'test_coverage' below threshold (78% < 80%)"],
    "gate_source": "yaml",
    "diagnostics": {...}
  }
}
```

---

## Options Considered

### Option 1: Enable Validation First, Then Session State

**Approach:** Uncomment line 504, monitor for 1 week, tune, then redesign session state.

**Pros:**
- Quick win (1 line change)
- Completes Oct 20 work immediately
- Can validate session state work with real validation
- De-risks validation before big state refactor

**Cons:**
- Old session state during validation testing (less ideal)
- Two separate deployment cycles
- Validation tuning may surface session state issues

### Option 2: Session State First, Then Validation

**Approach:** Redesign session state, deploy, then enable validation.

**Pros:**
- Better foundation for validation
- Single comprehensive update
- Clean slate for testing

**Cons:**
- Delays completing Oct 20 work
- Large change without validation safety net
- Session state changes might need validation feedback

### Option 3: Both in Parallel (Recommended)

**Approach:** Enable validation (strict: false), redesign session state in parallel, deploy together.

**Pros:**
- ✅ Enables validation immediately (completes Oct 20 work)
- ✅ Validation doesn't block session work (different files)
- ✅ Can validate session state with real validator
- ✅ Monitor validation while building new state
- ✅ Single deployment at end (less churn)

**Cons:**
- More complex coordination
- Must ensure compatibility

**Recommendation:** **Option 3** - Parallel work maximizes velocity, minimal conflicts (different files).

### Option 4: Skip Self-Validation

**Approach:** Trust external tests, skip re-running validation spec.

**Pros:**
- Saves time
- External tests are stronger anyway

**Cons:**
- ❌ Doesn't address bootstrap problem perception
- ❌ Misses learning opportunity
- ❌ No confidence building for users

**Recommendation:** **Do self-validation** - It's quick (few hours) and builds trust.

---

## Risks & Mitigations

### Risk 1: Validation Breaks Existing Workflows
- **Probability:** Medium
- **Impact:** High (workflows fail mid-execution)
- **Mitigation:**
  - Start in strict: false (warnings only, never blocks)
  - Monitor for 1 week before any strict mode
  - Tune false positives aggressively
  - Keep rollback ready (revert line 504)
- **Contingency:** Disable validation, investigate issues, fix gates, re-enable

### Risk 2: Session State Migration Corrupts Data
- **Probability:** Low
- **Impact:** Critical (data loss)
- **Mitigation:**
  - Automatic migration with extensive logging
  - Detect migration failures early (validate on load)
  - Backward compatibility (can read both formats)
  - No forced migration (gradual, new sessions first)
- **Contingency:** Load from backup, fix migration logic, retry

### Risk 3: Bootstrap Problem Undermines Trust
- **Probability:** Low
- **Impact:** Medium (perception issue)
- **Mitigation:**
  - Acknowledge openly in documentation
  - Emphasize external validation (tests)
  - Re-validate with validation enabled (self-test)
  - Build trust gradually with data
- **Contingency:** Document limitations, plan v2 external validation

### Risk 4: False Positive Rate Too High
- **Probability:** Medium
- **Impact:** Medium (user frustration)
- **Mitigation:**
  - Lenient mode first (warnings, no blocking)
  - Tune rules based on real data
  - Clear remediation messages
  - Allow overrides (allow_override: true)
- **Contingency:** Adjust validators, loosen constraints, extend monitoring

### Risk 5: Performance Degradation
- **Probability:** Low
- **Impact:** Low (slight slowdown)
- **Mitigation:**
  - Validation already cached (CheckpointLoader)
  - Benchmark before/after
  - Profile if issues found
- **Contingency:** Optimize hot paths, add caching

### Risk 6: standards_creation_v1 Rollout Issues
- **Probability:** Very Low
- **Impact:** Low (one workflow)
- **Mitigation:**
  - Already tested in hive-kube
  - Adapt carefully for universal context
  - Test dogfooding before declaring done
- **Contingency:** Fix issues found, iterate

---

## Open Questions

### Q1: Session Migration - Automatic or Manual?
**Context:** Legacy sessions need new fields (lifecycle, phase_timings, etc.)

**Option A:** Automatic on load (transparent to users)
- Pro: Seamless experience
- Con: Potential for silent failures

**Option B:** Manual script (user runs explicitly)
- Pro: Controlled, visible
- Con: Requires user action

**Recommendation:** Automatic with logging (best UX), but provide manual script for batch operations.

**Decision Needed:** Approve automatic migration approach?

### Q2: When to Enable Strict Validation Mode?
**Context:** Need to balance safety (lenient) vs. enforcement (strict)

**Options:**
- After 1 week monitoring (aggressive)
- After 2 weeks monitoring (moderate)
- After 4 weeks monitoring (conservative)
- Per-workflow basis (complex)

**Recommendation:** 1 week lenient + tune + 1 week lenient with tuned rules + enable strict for NEW workflows only (legacy stays lenient).

**Decision Needed:** Approve timeline?

### Q3: How to Handle Validation in Active Sessions?
**Context:** Some sessions may be mid-execution when validation enabled

**Option A:** Grandfather in (no validation for existing sessions)
- Pro: No disruption
- Con: Inconsistent experience

**Option B:** Apply validation to all (retroactive)
- Pro: Consistent
- Con: Might break active work

**Recommendation:** Option A - New validation starts with new sessions, active sessions complete with old behavior.

**Decision Needed:** Confirm approach?

### Q4: Should We Add Pause/Resume to v1?
**Context:** Mentioned in non-goals, but might be easy to add

**Effort:** Low (state already persists, just need workflow actions)
**Value:** Medium (nice to have, not critical)

**Recommendation:** Defer to v1.1 unless we discover it's trivial during session state work.

**Decision Needed:** Confirm as non-goal?

---

## Success Criteria

### Validation System
- ✅ Validation enabled in production (strict: false initially)
- ✅ At least 5 workflows executed with validation
- ✅ Validation monitoring data collected (1 week minimum)
- ✅ False positive rate measured and < 10%
- ✅ False negative rate measured and < 5%
- ✅ Validation tuning complete
- ✅ Trust metrics dashboard exists

### Session State
- ✅ New WorkflowState structure implemented
- ✅ Lifecycle flags working (completed, paused, failed_phase)
- ✅ Phase timing captured (started_at, completed_at, duration)
- ✅ Resumption context computed in < 1ms
- ✅ Zero out-of-range current_phase errors
- ✅ Legacy sessions can be loaded (backward compatible)
- ✅ Migration successful (all sessions migrated or migratable)

### Core Workflows
- ✅ standards_creation_v1 rolled out to universal/
- ✅ All 5 core workflows documented
- ✅ All phases have gate-definition.yaml
- ✅ Dogfooding: Created at least 1 standard using the workflow

### Self-Validation
- ✅ Evidence validation spec re-executed with validation on
- ✅ Comparison report vs. Oct 20 execution (validation off)
- ✅ Trust metrics collected
- ✅ Bootstrap problem documented

### Quality
- ✅ All tests passing (150+ tests)
- ✅ Test coverage >= 95%
- ✅ Pylint score: 10.0/10
- ✅ Zero critical bugs
- ✅ Zero P0 bugs

---

## File Changes

### Files to Modify

**Validation:**
- `.praxis-os/mcp_server/core/session.py` (1 line: call _validate_checkpoint)

**Session State:**
- `.praxis-os/mcp_server/models/workflow.py` (major: add LifecycleState, PhaseTiming, ResumptionContext)
- `.praxis-os/mcp_server/state_manager.py` (updates: populate lifecycle, validate on load)
- `.praxis-os/mcp_server/core/session.py` (updates: track timing, set lifecycle flags)
- `.praxis-os/mcp_server/workflow_engine.py` (updates: ensure metadata complete)

**Standards Rollout:**
- `universal/workflows/standards_creation_v1/` (new directory, copy from hive-kube)

### Files to Create

**Monitoring:**
- `.praxis-os/workspace/monitoring/validation-dashboard.md`
- `.praxis-os/workspace/monitoring/validation-trust-metrics.md`

**Analysis:**
- `.praxis-os/workspace/analysis/validation-bootstrap-analysis.md`

**Scripts:**
- `scripts/migrate-session-state-v2.py` (if manual migration needed)

**Logs (per session):**
- `.praxis-os/.cache/validation-logs/{session_id}.json`

---

## Testing Approach

### Unit Tests
- WorkflowState: lifecycle flags, phase timing, resumption context, is_complete()
- StateManager: session validation, migration, integrity checks
- WorkflowSession: phase timing tracking, lifecycle management
- WorkflowEngine: validation integration, metadata population
- Migration script: all scenarios (new fields, missing data, corruption)

### Integration Tests
- End-to-end: All 5 core workflows with validation enabled
- Session state: Create → save → load → validate → resume
- Validation system: YAML → RAG → permissive fallback
- Legacy compatibility: Load old sessions, migrate, save

### Dogfooding Tests
- Create spec with validation enabled
- Execute spec with validation enabled
- Create workflow with new session state
- Upgrade agent-os with new system
- Create standard using standards_creation_v1
- Resume interrupted workflow (test resumption context)

### Validation Monitoring
- Run 10+ workflows over 1 week
- Collect all validation results
- Manually review warnings/errors
- Categorize: true positive, false positive, edge case
- Tune rules based on data

---

## Related Documents

**Analysis:**
- Deep Dive: `.praxis-os/workspace/analysis/workflow-system-current-state-2025-10-23.md`
- Session State Design: `.praxis-os/workspace/design/2025-10-23-session-state-redesign.md`

**Specs:**
- Evidence Validation: `.praxis-os/specs/completed/2025-10-20-evidence-validation-system/`

**Standards:**
- Design Doc Structure: `search_standards("design document structure")`
- RAG Content Authoring: `search_standards("rag content authoring")`
- Knowledge Compounding: `search_standards("knowledge compounding")`

---

## Next Steps

1. **Human reviews this design doc** (approve, request changes, or reject)
2. **If approved:** Create full spec using `spec_creation_v1` workflow
3. **Execute spec:** Use `spec_execution_v1` to implement systematically
4. **Dogfooding:** Use the workflow system to improve the workflow system

---

**Version**: 2.0.0  
**Created**: 2025-10-23  
**Revised**: 2025-10-23 (following design-document-structure.md standard)  
**Status**: Ready for Review
