# Defensive Task Parser with Phase Shift Logic

**Status:** DRAFT - Pre-Implementation Design  
**Date:** 2025-11-05  
**Context:** Parser failing on real-world tasks.md with format variations  
**Related Session:** Current - spec_execution_v1 workflow first test

---

## Problem Statement

### Current Failure Mode

The `SpecTasksParser` in `.praxis-os/ouroboros/subsystems/workflow/task_parser.py` is failing to correctly parse tasks.md files due to **rigid pattern matching** that cannot handle format variations produced by probabilistic AI systems.

**Observed Bug:**
- Testing on `2025-11-04-rag-index-submodule-refactor/tasks.md`:
  - ❌ Phase 0 NOT recognized
  - ❌ All 27 tasks incorrectly assigned to Phase 4
  - ❌ "Detailed Task Breakdown" section treated as a phase
  
**Root Cause:** Parser expects exact patterns:
- Phase headers must have "phase" keyword + separator
- Tasks must immediately follow phase headers
- No tolerance for structural variations (overview sections vs. detailed sections)

### Why This Happens

**Probabilistic AI Drift:**
- `spec_creation_v1` workflow (which generates tasks.md) is itself an AI
- Despite strong guidance, format variations are inevitable
- Examples observed:
  - `## Phase 0: Foundation` vs. `### Phase 0 Tasks (Detailed)`
  - High-level overview sections with placeholders
  - Separate "Detailed Task Breakdown" sections with actual tasks
  - Varying header levels (##, ###)
  - Different separator styles (`:`, `-`, `—`)

**GIGO Prevention Required:**
- System must prevent "garbage in, garbage out"
- Parser should be **defensive**, not **brittle**
- Must handle variations gracefully while still validating quality

---

## Additional Architectural Requirement: Phase Shift Logic

### Workflow Harness Architecture

`spec_execution_v1` uses a **hybrid static/dynamic** architecture:

**Phase 0 (STATIC):** "Spec Analysis & Planning"
- Hardcoded in `metadata.json`
- 3 tasks: locate spec, parse tasks.md, build execution plan
- Initializes the parser and dynamic registry

**Phases 1-N (DYNAMIC):** Implementation phases from tasks.md
- Parsed from spec's tasks.md file
- Structure/count determined at runtime
- Delivered one task at a time via `get_task(phase, task_number)`

### The Phase Shift Problem

**Scenario:** Spec authors naturally start at Phase 0 for foundation work.

**tasks.md contains:**
```markdown
## Phase 0: Foundation & Utilities
## Phase 1: Standards Index
## Phase 2: Code Index
```

**Workflow harness needs:**
- Phase 0 = Static "Spec Analysis" (not from tasks.md)
- Phase 1 = "Foundation & Utilities" (tasks.md Phase 0)
- Phase 2 = "Standards Index" (tasks.md Phase 1)
- Phase 3 = "Code Index" (tasks.md Phase 2)

**Parser must:**
1. Detect if tasks.md contains Phase 0
2. Apply +1 shift to ALL phase numbers
3. Maintain task dependency relationships through the shift

---

## Design Goals

### 1. Defensive Parsing (Format Variation Tolerance)

**Dynamic Logic, Not Static Patterns:**
- Semantic scoring: Evaluate multiple confidence signals
- Proximity-based association: Link tasks to nearest preceding phase
- Inference from task numbers: Task "0.2" likely belongs to Phase 0
- Graceful degradation: Best-effort parsing even with unusual formatting

### 2. Phase Shift Detection & Normalization

**Automatic Detection:**
- Scan all phase headers, extract phase numbers
- If `min(phase_numbers) == 0`: Apply +1 shift to all phases
- If `min(phase_numbers) == 1`: No shift needed
- If `min(phase_numbers) > 1`: ERROR (missing phases)

**Validation:**
- After shift, phases must be sequential: [1, 2, 3, 4, ...]
- Any gaps → ERROR with actionable message
- Ensures spec quality (prevent GIGO)

### 3. Task/Dependency Normalization

**Task Numbering:**
- `task_id` field: Just the task number within phase (`"1"`, `"2"`, `"3"`)
- Used by `get_task(phase, task_number)` for lookup
- 1-indexed, sequential within each phase

**Dependency Format:**
- `dependencies` field: Phase.task format (`["1.1", "1.2", "2.3"]`)
- Required for cross-phase dependency tracking
- Dependency phase numbers shifted along with task phases

---

## Proposed Algorithm

### Phase 1: Collection & Scoring

```
For each header in AST:
    Extract: text, level, line_number
    
    Calculate phase_score:
        + 40 if "phase" keyword present
        + 25 if single number (0-20)
        + 15 if level == 2 (##)
        + 10 if has separator (: or —)
        + 5  if descriptive keywords present
        - 90% if "detailed" + "breakdown"
        - 30% if "tasks" (plural)
    
    Calculate task_score:
        + 40 if "task" keyword present
        + 30 if dotted number pattern (N.M)
        + 20 if level == 3 (###)
        + 10 if starts with number
        + 5  if action verbs present
```

### Phase 2: Classification

```
PHASE_THRESHOLD = 30.0
TASK_THRESHOLD = 30.0

Classify headers:
    If phase_score >= PHASE_THRESHOLD and phase_score > task_score:
        → Phase header
        Extract: phase_number, phase_name
    
    Elif task_score >= TASK_THRESHOLD and task_score >= phase_score:
        → Task header
        Extract: task_number (N.M), task_name
```

### Phase 3: Phase Shift Detection

```
phase_numbers = [ph.number for ph in phase_headers]
phase_numbers.sort()

min_phase = min(phase_numbers)

If min_phase == 0:
    shift_amount = 1
    reason = "Phase 0 detected, applying +1 shift for workflow harness"
Elif min_phase == 1:
    shift_amount = 0
    reason = "No Phase 0, no shift needed"
Else:
    RAISE ERROR: f"First phase is {min_phase}, expected 0 or 1. Missing phases."
```

### Phase 4: Validation (Gap Detection)

```
After shift:
    shifted_phases = [p + shift_amount for p in phase_numbers]
    expected = list(range(1, len(shifted_phases) + 1))
    
    If shifted_phases != expected:
        missing = set(expected) - set(shifted_phases)
        RAISE ERROR: f"Phase gaps detected. Missing phases: {missing}. Spec quality issue."
```

### Phase 5: Task Association

```
For each task_header:
    # Strategy 1: Proximity (nearest preceding phase)
    nearest_phase = max(ph for ph in phase_headers if ph.line < task_header.line)
    
    # Strategy 2: Inference from task number
    If task_number like "N.M":
        inferred_phase = N
    
    # Use inference if proximity unclear, proximity if confident
    final_phase = nearest_phase  # (with fallback to inference)
    
    # Apply shift
    final_phase += shift_amount
    
    # Associate task with phase
    phases[final_phase].tasks.append(task)
```

### Phase 6: Dependency Normalization

```
For each task with dependencies:
    For each dep in task.dependencies:
        If dep matches "N.M" pattern:
            phase_num = N
            task_num = M
            
            # Apply shift to dependency phase
            shifted_phase = phase_num + shift_amount
            
            # Normalize to "phase.task" format
            normalized_dep = f"{shifted_phase}.{task_num}"
        
        Else:
            # Handle other formats (e.g., "None", "Previous task")
            normalized_dep = dep
```

### Phase 7: Task ID Normalization

```
For each phase:
    For task_index, task in enumerate(phase.tasks):
        # Normalize task_id to just the task number (1-indexed)
        task.task_id = str(task_index + 1)
```

---

## Examples

### Example 1: With Phase 0 (Shift Required)

**Input (tasks.md):**
```markdown
## Phase 0: Foundation & Utilities
- Task 0.1: Implement BaseIndex (2-3h)
- Task 0.2: Implement LockManager (2-3h)
  Dependencies: Task 0.1

## Phase 1: Standards Index Refactor
- Task 1.1: Create submodule structure (30min)
- Task 1.2: Migrate SemanticIndex (2h)
  Dependencies: Task 0.1, Task 0.2
```

**Output (Parser Result):**
```python
# Shift detected: +1 (Phase 0 found)

DynamicPhase(
    phase_number=1,  # Shifted from 0
    phase_name="Foundation & Utilities",
    tasks=[
        DynamicTask(
            task_id="1",  # Normalized
            task_name="Implement BaseIndex",
            dependencies=[]
        ),
        DynamicTask(
            task_id="2",  # Normalized
            task_name="Implement LockManager",
            dependencies=["1.1"]  # Shifted from "0.1"
        )
    ]
)

DynamicPhase(
    phase_number=2,  # Shifted from 1
    phase_name="Standards Index Refactor",
    tasks=[
        DynamicTask(
            task_id="1",
            task_name="Create submodule structure",
            dependencies=[]
        ),
        DynamicTask(
            task_id="2",
            task_name="Migrate SemanticIndex",
            dependencies=["1.1", "1.2"]  # Shifted from "0.1", "0.2"
        )
    ]
)
```

**Usage:**
```python
# AI calls get_task
get_task(session_id, phase=1, task_number=1)
# Returns: "Implement BaseIndex" (was tasks.md Phase 0, Task 0.1)

get_task(session_id, phase=2, task_number=2)
# Returns: "Migrate SemanticIndex" (was tasks.md Phase 1, Task 1.2)
```

### Example 2: Without Phase 0 (No Shift)

**Input (tasks.md):**
```markdown
## Phase 1: Data Layer
- Task 1.1: Create models (3h)

## Phase 2: API Layer
- Task 2.1: Implement endpoints (4h)
  Dependencies: Task 1.1
```

**Output:**
```python
# No shift: Phase 1 is minimum

DynamicPhase(
    phase_number=1,
    phase_name="Data Layer",
    tasks=[DynamicTask(task_id="1", ...)]
)

DynamicPhase(
    phase_number=2,
    phase_name="API Layer",
    tasks=[DynamicTask(task_id="1", dependencies=["1.1"], ...)]
)
```

### Example 3: Error Cases

**Gap Detected:**
```markdown
## Phase 0: Foundation
## Phase 2: Integration  ← Missing Phase 1!
## Phase 4: Testing      ← Missing Phase 3!
```

**Error:**
```
❌ PARSE ERROR: Phase gaps detected after shift
  Expected: [1, 2, 3]
  Found: [1, 3, 5]
  Missing: [2, 4]
  
  Reason: Spec quality issue - phases must be sequential
  
  Fix: Review tasks.md and add missing phases OR renumber phases sequentially
```

**Invalid Start:**
```markdown
## Phase 3: Implementation  ← Starts at 3, not 0 or 1!
```

**Error:**
```
❌ PARSE ERROR: First phase is 3, expected 0 or 1
  
  Reason: Phases must start at 0 or 1
  
  Fix: Renumber phases starting from Phase 0 or Phase 1
```

---

## Data Structures

### Confidence Scoring

```python
@dataclass
class ScoredHeader:
    text: str
    level: int  # 1=H1, 2=H2, 3=H3
    line: int
    phase_score: float
    task_score: float
    numbers: List[int]  # All numbers found in text
    node: Any  # AST node reference
```

### Phase Shift Metadata

```python
@dataclass
class PhaseShiftInfo:
    shift_amount: int  # 0 or 1
    reason: str
    original_phases: List[int]
    shifted_phases: List[int]
    validation_passed: bool
    errors: List[str]
```

---

## Error Handling

### Error Categories

1. **Format Errors (Graceful)**
   - No phase headers found → Empty result (not fatal)
   - Ambiguous headers (equal scores) → Use proximity + heuristics

2. **Quality Errors (Fatal)**
   - Phase gaps detected → ERROR with missing phase numbers
   - Invalid phase start (not 0 or 1) → ERROR with guidance
   - Circular dependencies → ERROR with cycle path

3. **Parsing Errors (Fatal)**
   - File not found → ParseError with file path
   - Invalid markdown → ParseError with line number
   - Empty file → ParseError

### Error Message Format

```python
raise ParseError(
    what_failed="Phase validation",
    why_failed="Phase gaps detected. Expected [1,2,3], found [1,3,5]. Missing: [2,4]",
    how_to_fix="Review tasks.md and either add missing phases OR renumber phases sequentially"
)
```

---

## Testing Strategy

### Unit Tests

**Test 1: Phase Shift Detection**
- Input: Phase 0, 1, 2
- Expected: shift_amount=1, phases=[1,2,3]

**Test 2: No Shift**
- Input: Phase 1, 2, 3
- Expected: shift_amount=0, phases=[1,2,3]

**Test 3: Gap Detection**
- Input: Phase 0, 2, 4
- Expected: ParseError (missing [1, 3])

**Test 4: Invalid Start**
- Input: Phase 3, 4, 5
- Expected: ParseError (starts at 3)

**Test 5: Dependency Shift**
- Input: Task 1.1 depends on Task 0.2
- With shift: deps=["1.2"]
- Without shift: deps=["0.2"]

**Test 6: Task Normalization**
- Input: Phase with tasks 0.1, 0.2, 0.3
- Expected: task_ids=["1", "2", "3"]

### Integration Tests

**Test 7: Real tasks.md Files**
- Parse all completed specs in `.praxis-os/specs/completed/`
- Validate no regressions
- Document any failures for format patterns

**Test 8: Format Variations**
- Different header levels (##, ###)
- Different separators (:, -, —)
- With/without Phase 0
- Overview sections vs. detailed sections

### Edge Cases

**Test 9: Single Phase**
- Input: Only Phase 0
- Expected: phase_number=1 (shifted)

**Test 10: Many Phases**
- Input: Phase 0-20
- Expected: phases=[1-21] (all shifted)

**Test 11: No Tasks**
- Input: Phase headers but no tasks
- Expected: Phases with empty task lists

---

## Implementation Notes

### Files to Modify

**Primary:**
- `.praxis-os/ouroboros/subsystems/workflow/task_parser.py`
  - Replace `_extract_phase_info()` with semantic scoring
  - Add `_detect_phase_shift()`
  - Add `_validate_phase_sequence()`
  - Add `_normalize_dependencies()`
  - Update `parse()` to orchestrate new logic

**Testing:**
- `tests/unit/test_task_parser.py` (new file)
- `tests/integration/test_dynamic_workflows.py` (update)

### Backward Compatibility

**Concern:** Existing specs that work with old parser

**Mitigation:**
- Semantic scoring should match current patterns
- Old format: `## Phase 0: Name` with tasks immediately following
- New approach will handle this as high-confidence phase
- Run full regression test on completed specs

---

## Success Criteria

1. ✅ Parse `2025-11-04-rag-index-submodule-refactor/tasks.md` correctly
   - Phase 0 recognized → Workflow Phase 1
   - All 27 tasks correctly distributed across 5 phases
   - Dependencies preserved and shifted

2. ✅ Handle format variations gracefully
   - Different header levels
   - Different separators
   - Overview vs. detailed sections

3. ✅ Validate spec quality
   - Error on phase gaps
   - Error on invalid phase start
   - Actionable error messages

4. ✅ Zero regressions on existing specs
   - All completed specs still parse correctly
   - May improve parsing for edge cases

5. ✅ Cross-phase dependencies work
   - Task in Phase 2 can depend on Phase 1 task
   - Dependencies shifted correctly
   - Validation prevents forward references

---

## Open Questions

1. **Should we support Phase renumbering in-place?**
   - If spec has phases [2, 3, 4], auto-renumber to [1, 2, 3]?
   - OR error and require human fix?
   - **Recommendation:** Error for now (quality gate), can add auto-renumber later

2. **What about non-numeric phase identifiers?**
   - "Phase Alpha", "Phase Beta"
   - **Recommendation:** Not supported, error with guidance

3. **Should parser validate dependency task existence?**
   - Task 2.1 depends on Task 1.5 (but no Task 1.5 exists)
   - **Recommendation:** Yes, add validation (separate PR)

---

## References

- Current parser: `.praxis-os/ouroboros/subsystems/workflow/task_parser.py`
- Old implementation: `mcp_server/core/parsers.py` (ported yesterday)
- Workflow metadata: `.praxis-os/workflows/spec_execution_v1/metadata.json`
- Dependency resolver doc: `.praxis-os/workflows/spec_execution_v1/core/dependency-resolver.md`
- Test spec: `.praxis-os/specs/review/2025-11-04-rag-index-submodule-refactor/tasks.md`

---

**Next Step:** Review this design doc, then proceed to implementation if approved.

