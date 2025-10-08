---
sidebar_position: 4
---

# Workflows

Agent OS Enhanced includes **phase-gated workflows** that guide AI through complex, multi-step development processes with built-in quality gates and evidence-based progression.

## What Are Workflows?

Workflows are structured, multi-phase processes that:
- Break complex tasks into manageable phases
- Enforce sequential progression (can't skip phases)
- Require evidence at checkpoints before advancing
- Persist state across sessions
- Provide targeted guidance at each step

### Example: Spec Creation Workflow

```
Phase 0: Context Gathering → Phase 1: Requirements → Phase 2: Design → 
Phase 3: Implementation Planning → Phase 4: Review & Finalization
```

Each phase has:
- Clear objectives
- Specific deliverables
- Checkpoint evidence requirements
- Targeted execution guidance (≤100 lines per task)

## Phase Gating

### The Problem

Without enforcement, AI agents:
- Skip ahead to implementation before design is complete
- Miss critical analysis steps
- Deliver incomplete specifications
- Require extensive rework

### The Solution: Architectural Gating

Phases are **architecturally enforced** in code, not just suggested in documentation:

```python
class WorkflowState:
    current_phase: int = 0
    completed_phases: List[int] = []
    
    def can_access_phase(self, phase: int) -> bool:
        """
        AI can ONLY access:
        1. Current phase
        2. Previously completed phases
        
        Cannot skip ahead to future phases.
        """
        if phase == self.current_phase:
            return True
        if phase in self.completed_phases:
            return True
        return False  # Structurally impossible
```

**Result:** Phase skipping is impossible, not just discouraged.

## Checkpoint System

### Evidence-Based Progression

To advance from Phase N to Phase N+1, AI must provide **evidence**:

```python
# Phase 1 checkpoint (Requirements)
evidence = {
    "srd_created": True,
    "business_requirements": ["req1", "req2", "req3"],
    "success_criteria": ["criterion1", "criterion2"],
    "stakeholders_identified": True
}

# Attempt to complete phase
result = complete_phase(
    session_id="session_abc",
    phase=1,
    evidence=evidence
)

if result.passed:
    # Phase 1 marked complete
    # Phase 2 now accessible
    current_phase = 2
else:
    # Missing evidence
    # AI stays on Phase 1
    missing = result.missing_evidence
    # ["stakeholder_approval"]
```

### Dynamic Checkpoint Loading

Checkpoints are loaded **dynamically** from workflow metadata, not hardcoded:

```python
# Load checkpoint requirements from docs
requirements = load_checkpoint(
    workflow="spec_creation_v1",
    phase=1
)

# Validate evidence against requirements
validate_evidence(provided=evidence, required=requirements)
```

**Benefit:** Update checkpoints in documentation, no code changes needed.

## Workflow Structure

### Three-Tier Architecture

Based on LLM attention characteristics:

#### Tier 1: Execution Files (≤100 lines)
```
workflows/spec_creation_v1/phases/
├── phase-0-task-1.md        # 45 lines
├── phase-0-task-2.md        # 78 lines
├── phase-1-task-1.md        # 92 lines
└── phase-1-task-2.md        # 65 lines
```

**Purpose:** Immediate execution guidance
**Size:** ≤100 lines (optimal LLM attention)
**Content:** Commands, steps, examples

#### Tier 2: Methodology Files (200-500 lines)
```
workflows/spec_creation_v1/core/
├── phase-0-overview.md      # 320 lines
├── phase-1-overview.md      # 280 lines
└── framework-core.md        # 450 lines
```

**Purpose:** Comprehensive guidance
**Size:** 200-500 lines (active reading)
**Content:** Methodology, principles, patterns

#### Tier 3: Output Files (Unlimited)
```
.agent-os/specs/2025-10-08-user-auth/
├── README.md                # Generated output
├── srd.md                   # Generated output
├── specs.md                 # Generated output
└── tasks.md                 # Generated output
```

**Purpose:** AI-generated artifacts
**Size:** No limit
**Content:** Specifications, designs, plans

### Why This Structure?

Based on LLM research:
- **≤100 lines**: 95%+ attention, high execution accuracy
- **200-500 lines**: 70-85% attention, good for methodology
- **>500 lines**: &lt;70% attention, information gets lost

## Available Workflows

### Spec Creation v1

**Purpose:** Create comprehensive design specifications

**Phases:**
0. Context Gathering - Understand existing codebase
1. Requirements - Define business requirements (SRD)
2. Design - Technical architecture and design
3. Implementation Planning - Task breakdown and sequencing
4. Review & Finalization - Validation and approval

**Use when:** Starting a new feature or major refactoring

### Spec Execution v1

**Purpose:** Implement specifications systematically

**Phases:**
0. Spec Review - Understand requirements
1. Setup - Create structure, dependencies
2. Implementation - Build features
3. Testing - Comprehensive test coverage
4. Documentation - User and API docs
5. Review - Quality validation

**Use when:** Have approved spec, ready to build

## Using Workflows

### Start a Workflow

```python
# Via MCP tool
result = start_workflow(
    workflow_type="spec_creation_v1",
    target_file="user_authentication"
)

# Returns:
{
    "session_id": "abc123",
    "current_phase": 0,
    "workflow_overview": {
        "total_phases": 5,
        "phases": [
            {"phase": 0, "name": "Context Gathering", ...},
            {"phase": 1, "name": "Requirements", ...},
            ...
        ]
    }
}
```

### Get Current Phase

```python
# AI queries current phase
phase_content = get_current_phase(session_id="abc123")

# Returns Phase 0 content:
# - Objectives
# - Tasks to execute
# - Deliverables expected
# - Checkpoint requirements
```

### Complete Phase

```python
# Submit evidence
result = complete_phase(
    session_id="abc123",
    phase=0,
    evidence={
        "codebase_analyzed": True,
        "tech_stack_documented": ["Python", "FastAPI"],
        "patterns_identified": ["async", "REST API"]
    }
)

if result.passed:
    # Advance to Phase 1
    next_phase = get_current_phase(session_id="abc123")
```

### Resume Workflow

Workflows persist state - resume anytime:

```python
# Get workflow state
state = get_workflow_state(session_id="abc123")

# Shows:
# - Current phase: 2
# - Completed phases: [0, 1]
# - Evidence submitted for each phase
# - Artifacts created
```

## Creating Custom Workflows

Use the **meta-framework** to create your own workflows:

```python
# Generate new workflow
create_workflow(
    name="api_documentation_v1",
    workflow_type="documentation",
    phases=["Analysis", "Generation", "Review"],
    target_language="python"
)
```

**Result:** Complete workflow structure with:
- Phase files (≤100 lines each)
- Metadata (phases, checkpoints)
- Command language
- Validation gates

See the **Meta-Framework Guide** in the repository for details.

## Workflow Best Practices

### 1. Trust the Process

Don't skip phases, even if they seem unnecessary. Each phase builds critical context.

### 2. Provide Complete Evidence

Checkpoint evidence should be **specific and verifiable**:
- ✅ `"requirements": ["User can login", "Supports OAuth"]`
- ❌ `"requirements_done": True`

### 3. Use Task-by-Task Execution

Complete one task at a time:
```
"Execute Phase 0, Task 1" ✅
Not: "Do all of Phase 0" ❌
```

### 4. Review Artifacts

After each phase, review generated artifacts before advancing.

### 5. Resume Don't Restart

If interrupted, resume the workflow - don't start over.

## Next Steps

- **[Architecture](./architecture)** - How workflows are enforced
- **[Installation](./installation)** - Get workflows in your project
- **Meta-Framework** - Create custom workflows (see repository)

