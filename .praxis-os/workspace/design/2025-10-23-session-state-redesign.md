# Session State Redesign

**Status:** DRAFT - Design Discussion  
**Date:** 2025-10-23  
**Context:** Discovered during aos_workflow implementation that session completion logic is broken  
**Related Session:** 062f24e7-6fdc-40b3-a2d8-7ffaea6351b6 (aos_workflow spec execution)

---

## Problem Statement

### Current Issues

1. **Broken Completion Detection**
   - `is_complete()` uses buggy logic: `current_phase > total_phases`
   - For 0-indexed workflows (phases 0-5), after completing phase 5, `current_phase = 6`
   - Check: `6 > 6` = False ❌ (should be True)

2. **Data Duplication**
   - `total_phases` is in workflow metadata.json but not in session state
   - Forces recalculation or hardcoded assumptions
   - After MCP restart, requires loading metadata to determine completion

3. **Invalid State Values**
   - `current_phase = 6` when phases are 0-5 (phase 6 doesn't exist!)
   - Using out-of-range values as sentinel for "complete"
   - Semantically incorrect

4. **Missing Resumption Context**
   - No phase timing information
   - Can't compute progress estimates
   - No explicit lifecycle flags (paused, completed, failed)
   - Poor AI resumption after MCP restart or new session

### Discovery Context

Found while completing Phase 5 of aos_workflow implementation:
- Session showed `current_phase: 6` with `completed_phases: [0,1,2,3,4,5]`
- But `is_complete()` returned `false` ❌
- Root cause: `6 > 6` comparison fails
- Deeper issue: Missing `total_phases` in session metadata

---

## Design Goals

### Primary Use Cases

**Use Case 1: Same AI Session After MCP Restart**
```
Working on Phase 3, Task 2
Modified 3 files, wrote tests
MCP crashes/restarts
[Cache cleared, memory gone]
Load session file...
Need: "Where was I? What was I doing? What files did I touch?"
```

**Use Case 2: New AI Session (Days Later)**
```
User returns 3 days later with different AI
Phase 2 completed, sitting at Phase 3
[No context from previous conversation]
Load session file...
Need: "What's the workflow about? What was done? What's next?
       Why was I paused? Any issues or blockers?"
```

### Design Principles

1. **Session File = Event Log + State Flags**
   - Immutable: phase_timing, phase_artifacts, checkpoints (history)
   - Mutable: current_phase, lifecycle flags, updated_at (current state)

2. **Explicit State, No Calculations**
   - Set `lifecycle.completed = true` when last phase finishes
   - Don't compute completion from current_phase comparisons

3. **Workflow Structure Snapshot**
   - Capture `total_phases`, `starting_phase`, `indexing_scheme` at session creation
   - Session completes based on contract it started with (not future changes)

4. **Valid Semantic Values**
   - `current_phase` always refers to a valid phase (0-5 for 6 phases)
   - Never exceeds valid range

5. **Rich Resumption Context**
   - Phase timing for progress estimates
   - Explicit lifecycle state (active/paused/completed/failed)
   - Clear "what's next" logic

---

## Proposed Design

### Session File Structure

```json
{
  // ========================================
  // SECTION 1: Session Identity
  // ========================================
  "session_id": "abc-123",
  "workflow_type": "spec_execution_v1",
  "target_file": ".praxis-os/specs/my-spec",
  
  // ========================================
  // SECTION 2: Workflow Structure Snapshot
  // Captured at session creation time
  // ========================================
  "workflow_structure": {
    "total_phases": 6,
    "starting_phase": 0,
    "indexing_scheme": "zero_based",  // or "one_based"
    "workflow_version": "v1"
  },
  
  // ========================================
  // SECTION 3: Progress Tracking
  // ========================================
  "current_phase": 5,              // Stays at last valid phase when complete
  "completed_phases": [0, 1, 2, 3, 4, 5],
  
  // ========================================
  // SECTION 4: Phase Timing
  // Track when each phase started/completed
  // ========================================
  "phase_timing": {
    "0": {
      "started_at": "2025-10-23T07:00:00Z",
      "completed_at": "2025-10-23T07:30:00Z"
    },
    "1": {
      "started_at": "2025-10-23T07:30:00Z",
      "completed_at": "2025-10-23T08:15:00Z"
    },
    "2": {
      "started_at": "2025-10-23T08:15:00Z",
      "completed_at": "2025-10-23T09:27:00Z"
    },
    "3": {
      "started_at": "2025-10-23T09:27:00Z"
      // No completed_at = in progress
    }
  },
  
  // ========================================
  // SECTION 5: Lifecycle State
  // Explicit flags (set once, never recalculated)
  // ========================================
  "lifecycle": {
    "completed": false,
    "completed_at": null,
    
    "paused": false,
    "paused_at": null,
    "paused_reason": null,         // "user_request" | "checkpoint_failed" | "system_error"
    "paused_context": null,        // What was being worked on when paused
    
    "resumed_at": null,
    "resume_count": 0,
    
    "last_error": null,
    "last_error_at": null
  },
  
  // ========================================
  // SECTION 6: Phase Artifacts (existing)
  // ========================================
  "phase_artifacts": {
    "0": {
      "phase_number": 0,
      "evidence": {...},
      "outputs": {...},
      "commands_executed": [],
      "timestamp": "2025-10-23T07:30:00Z"
    }
  },
  
  // ========================================
  // SECTION 7: Checkpoint Results (existing)
  // ========================================
  "checkpoints": {
    "0": "passed",
    "1": "passed",
    "2": "failed",  // Can retry or rollback
    "3": "pending"
  },
  
  // ========================================
  // SECTION 8: Timestamps (existing)
  // ========================================
  "created_at": "2025-10-23T07:00:00Z",
  "updated_at": "2025-10-23T09:27:15Z",
  
  // ========================================
  // SECTION 9: Additional Metadata (existing)
  // ========================================
  "metadata": {
    "spec_path": "...",
    "user_options": {},
    "agent_version": "1.0.0"
  }
}
```

### Key Behavior Changes

#### 1. At Session Creation (`StateManager.create_session()`)

```python
# Load workflow metadata to get structure
workflow_metadata = workflow_engine.load_workflow_metadata(workflow_type)

# Detect starting phase
starting_phase = self._detect_starting_phase(workflow_type)

state = WorkflowState(
    # ... existing fields ...
    workflow_structure={
        "total_phases": workflow_metadata.total_phases,
        "starting_phase": starting_phase,
        "indexing_scheme": "zero_based" if starting_phase == 0 else "one_based",
        "workflow_version": workflow_metadata.version,
    },
    lifecycle={
        "completed": False,
        "paused": False,
        "resume_count": 0,
    },
    phase_timing={
        starting_phase: {
            "started_at": now.isoformat(),
        }
    },
)
```

#### 2. At Phase Completion (`WorkflowState.complete_phase()`)

```python
def complete_phase(self, phase: int, artifact: PhaseArtifact, checkpoint_passed: bool = True) -> None:
    if phase != self.current_phase:
        raise ValueError(f"Cannot complete phase {phase}, current phase is {self.current_phase}")
    
    now = datetime.now()
    
    # Store artifacts and checkpoint status
    self.phase_artifacts[phase] = artifact
    self.checkpoints[phase] = CheckpointStatus.PASSED if checkpoint_passed else CheckpointStatus.FAILED
    
    # Record phase completion timing
    if phase in self.phase_timing:
        started_at = datetime.fromisoformat(self.phase_timing[phase]["started_at"])
        duration = (now - started_at).total_seconds()
        self.phase_timing[phase]["completed_at"] = now.isoformat()
        self.phase_timing[phase]["duration_seconds"] = duration
    
    if checkpoint_passed:
        self.completed_phases.append(phase)
        
        # Check if this is the last phase
        total_phases = self.workflow_structure.get("total_phases")
        starting_phase = self.workflow_structure.get("starting_phase", 0)
        
        if total_phases:
            # Calculate last phase number
            if starting_phase == 0:
                last_phase = total_phases - 1  # 0-indexed: 0..5 for 6 phases
            else:
                last_phase = total_phases      # 1-indexed: 1..6 for 6 phases
            
            if phase == last_phase:
                # ✅ Workflow complete! Don't advance current_phase
                self.lifecycle["completed"] = True
                self.lifecycle["completed_at"] = now.isoformat()
                total_duration = (now - self.created_at).total_seconds()
                self.lifecycle["total_duration_seconds"] = total_duration
                # current_phase stays at last valid phase (5)
            else:
                # Not done yet, advance to next phase
                next_phase = phase + 1
                self.current_phase = next_phase
                
                # Start timing for next phase
                self.phase_timing[next_phase] = {
                    "started_at": now.isoformat()
                }
        else:
            # Legacy fallback (no workflow_structure)
            self.current_phase = phase + 1
    
    self.updated_at = now
```

#### 3. Completion Check (`WorkflowState.is_complete()`)

```python
def is_complete(self) -> bool:
    """Check if workflow is complete."""
    # Primary: check completed flag
    if self.lifecycle.get("completed"):
        return True
    
    # Fallback for legacy sessions: check if all phases done
    total_phases = self.workflow_structure.get("total_phases")
    if total_phases and len(self.completed_phases) > 0:
        # Check if completed_phases contains all phases
        starting_phase = self.workflow_structure.get("starting_phase", 0)
        if starting_phase == 0:
            # 0-indexed: should have phases 0..N-1
            expected_phases = set(range(total_phases))
        else:
            # 1-indexed: should have phases 1..N
            expected_phases = set(range(1, total_phases + 1))
        
        return set(self.completed_phases) == expected_phases
    
    # Last resort: very old sessions without workflow_structure
    return False
```

---

## AI Resumption Context

When loading a session after restart or in new AI session, compute and display:

```python
# Progress metrics
percent_complete = len(completed_phases) / total_phases * 100
phases_remaining = total_phases - len(completed_phases)

# Timing analysis
completed_durations = [
    (parse(phase_timing[p]["completed_at"]) - parse(phase_timing[p]["started_at"])).total_seconds()
    for p in completed_phases if p in phase_timing and "completed_at" in phase_timing[p]
]
avg_phase_duration = mean(completed_durations) if completed_durations else None
estimated_remaining = avg_phase_duration * phases_remaining if avg_phase_duration else None

# Current phase analysis
if current_phase in phase_timing and "completed_at" not in phase_timing[current_phase]:
    phase_started = parse(phase_timing[current_phase]["started_at"])
    time_in_phase = (now - phase_started).total_seconds()
    is_stalled = time_in_phase > (2 * avg_phase_duration) if avg_phase_duration else False

# Status determination
if lifecycle["completed"]:
    status = "completed"
elif lifecycle["paused"]:
    status = "paused"
elif checkpoints.get(current_phase) == "failed":
    status = "checkpoint_failed"
elif is_stalled:
    status = "possibly_stalled"
else:
    status = "active"
```

Display format:
```
📋 Session abc-123: spec_execution_v1
   Target: .praxis-os/specs/my-spec
   
🎯 Progress: Phase 3 of 6 (50% complete)
   Current: Phase 3 (started 2 hours ago)
   Average phase time: 49 minutes
   ⚠️  Current phase taking longer than average
   
✅ Completed Phases:
   Phase 0: Planning (30 min) ✅ Checkpoint PASSED
   Phase 1: Setup (45 min) ✅ Checkpoint PASSED
   Phase 2: Implementation (1.2 hr) ❌ Checkpoint FAILED
      Evidence: tests_passing=42/45, coverage=65%
      Issue: Coverage requirement is 80%
      
🔄 Current Status: checkpoint_failed
   Next step: Add more tests to reach 80% coverage, then retry Phase 2

⏰ Timing:
   Started: 3.5 hours ago
   Last updated: 5 minutes ago
   Estimated remaining: ~2.5 hours
```

---

## Implementation Changes

### New Fields in `WorkflowState` Dataclass

```python
@dataclass
class WorkflowState:
    # Existing fields
    session_id: str
    workflow_type: str
    target_file: str
    current_phase: int
    completed_phases: List[int]
    phase_artifacts: Dict[int, PhaseArtifact]
    checkpoints: Dict[int, CheckpointStatus]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # NEW FIELDS
    workflow_structure: Dict[str, Any] = field(default_factory=dict)
    lifecycle: Dict[str, Any] = field(default_factory=dict)
    phase_timing: Dict[int, Dict[str, Any]] = field(default_factory=dict)
```

### Files to Modify

1. **`mcp_server/models/workflow.py`**
   - Add new fields to `WorkflowState`
   - Update `to_dict()` and `from_dict()` serialization
   - Update `complete_phase()` logic
   - Simplify `is_complete()` logic

2. **`mcp_server/state_manager.py`**
   - Update `create_session()` to populate `workflow_structure`
   - Needs access to `WorkflowEngine.load_workflow_metadata()` (dependency injection or passed as param)

3. **`mcp_server/workflow_engine.py`**
   - Update `start_workflow()` to pass metadata to `create_session()`
   - No changes to `is_complete()` callers (signature stays the same)

4. **`mcp_server/core/session.py`**
   - Add helper method to compute resumption context
   - Display rich context when loading session

### Migration for Existing Sessions

Legacy sessions without new fields will fall back to:
- `is_complete()`: Check if all phases in `completed_phases` (requires `total_phases` from metadata)
- Display warning when loading: "Legacy session format, limited resumption context"
- Can add upgrade script to migrate old sessions (optional)

---

## Benefits

### For AI Agent (Primary Consumer)

1. **Clear Progress Context**
   - "You are on Phase 3 of 6 (50% complete)"
   - "This phase started 45 minutes ago"
   - "Average phase time: 1.2 hours, estimated remaining: ~2.5 hours"

2. **Explicit State, No Calculations**
   - `if lifecycle["completed"]` vs calculating from phase numbers
   - No confusion about 0-indexed vs 1-indexed

3. **Error Recovery Context**
   - After MCP restart: "Last working on Phase 3 (started 2025-10-23T10:00:00)"
   - "Previous phases took: 30m, 45m, 1.2h"
   - "No pauses or interruptions"

4. **Simple "What's Next?" Logic**
   - Clear decision tree based on explicit flags
   - No edge case bugs with phase numbering

### For System

1. **Semantic Correctness**
   - `current_phase` always valid (never exceeds range)
   - No sentinel values

2. **Single Source of Truth**
   - `workflow_structure` captured at session creation
   - Session completes based on contract it started with

3. **Backward Compatible**
   - Existing sessions continue to work (with fallbacks)
   - Can migrate incrementally

4. **Extensible**
   - Easy to add pause/resume tracking
   - Can add phase retry tracking
   - Can track multiple error occurrences

---

## Open Questions

1. **StateManager dependency on WorkflowEngine**
   - `StateManager.create_session()` needs `workflow_metadata.total_phases`
   - Options:
     - A) Pass metadata as parameter to `create_session()`
     - B) Inject WorkflowEngine into StateManager
     - C) StateManager loads metadata itself (duplicate code)
   - **Recommendation:** Option A (pass as parameter)

2. **Phase timing for resumed sessions**
   - If session paused mid-phase, how track "active time" vs "paused time"?
   - Should we track `phase_timing[N]["paused_duration_seconds"]`?

3. **Migration strategy**
   - Upgrade existing sessions on load (modify file)?
   - Or just handle gracefully with warnings?
   - **Recommendation:** Graceful fallback, no automatic migration

4. **Display integration**
   - Where should rich resumption context be displayed?
   - In `get_phase()` response?
   - New `get_session_context()` action?
   - **Recommendation:** Add to `get_state()` response

---

## Next Steps

1. **User Review** - Validate design approach
2. **Create Formal Spec** - Use `spec_creation_v1` workflow
3. **Implementation** - Use `spec_execution_v1` workflow
4. **Testing** - Verify resumption scenarios
5. **Migration** - Handle existing sessions gracefully

---

## Related Context

- **Triggering Issue:** aos_workflow Phase 5 completion showed `is_complete() = false`
- **Root Cause:** `current_phase = 6` with `6 > 6` check
- **Session:** 062f24e7-6fdc-40b3-a2d8-7ffaea6351b6
- **Workflow:** spec_execution_v1 for aos_workflow tool

