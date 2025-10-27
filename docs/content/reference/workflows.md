---
sidebar_position: 4
doc_type: reference
---

# Workflows Reference

Complete reference for prAxIs OS phase-gated workflows.

## Overview

Workflows are structured, multi-phase processes with architectural enforcement of sequential progression and evidence-based checkpoints.

**Key Characteristics:**
- Phase gating (cannot skip phases)
- Evidence-based progression
- Persistent state (resumable)
- Targeted guidance (under 100 lines per task)

---

## Available Workflows

### Production Workflows

| Workflow | Purpose | Phases | Duration | Status |
|----------|---------|--------|----------|--------|
| [spec_creation_v1](#spec_creation_v1) | Create comprehensive design specifications | 6 phases | 2-4 hours | Production |
| [spec_execution_v1](#spec_execution_v1) | Implement specifications systematically | Dynamic (spec-driven) | Varies by spec | Production |
| [agent_os_upgrade_v1](#agent_os_upgrade_v1) | Upgrade prAxIs OS safely with rollback | 6 phases | 15-30 min | Production |

---

## Workflow Details

### spec_creation_v1

Create comprehensive design specifications with requirements, architecture, and implementation plans.

**Purpose:** Systematic specification creation for new features or major refactorings.

**When to Use:** Starting any non-trivial feature development.

**Phases:**

| Phase | Name | Objective | Duration |
|-------|------|-----------|----------|
| 0 | Supporting Documents Integration | Copy existing docs, create index, extract insights | 15-30 min |
| 1 | Requirements Gathering | Business goals, user stories, functional/non-functional requirements | 30-60 min |
| 2 | Technical Design | Architecture, components, APIs, data models, security, performance | 45-90 min |
| 3 | Implementation Planning | Identify phases, break down tasks, acceptance criteria, dependencies, validation gates | 30-60 min |
| 4 | Implementation Guidance | Code patterns, testing strategy, deployment, troubleshooting | 30-45 min |
| 5 | Review & Finalization | Completeness review, consistency check, final packaging | 15-30 min |

**Output Artifacts:**
- `README.md` - Executive summary
- `srd.md` - Software Requirements Document
- `specs.md` - Technical specification
- `tasks.md` - Implementation task breakdown
- `implementation.md` - Detailed implementation guidance

**Checkpoint Example (Phase 1):**
```python
evidence = {
    "srd_created": True,
    "business_goals_defined": True,
    "user_stories_documented": True,
    "functional_requirements_listed": True,
    "nfr_defined": True,
    "out_of_scope_clarified": True
}
```

**Usage:**
```python
start_workflow(
    workflow_type="spec_creation_v1",
    target_file="user_authentication"
)
```

---

### spec_execution_v1

Implement approved specifications with systematic phase-by-phase execution.

**Purpose:** Transform specifications into production code with tests and documentation.

**When to Use:** Have approved spec, ready to implement.

**Phases:**

| Phase | Name | Objective | Duration |
|-------|------|-----------|----------|
| 0 | Spec Review | Locate spec, parse tasks, build execution plan | 15-30 min |
| Dynamic | Implementation Phases | Execute tasks from `tasks.md` | Varies by spec |

**Dynamic Phase Structure:**
- Phases loaded from `tasks.md` in spec directory
- Each phase contains tasks with acceptance criteria
- Validation gates enforced between phases
- Horizontal scaling (one task at a time)

**Output Artifacts:**
- Implementation code
- Comprehensive tests
- API documentation
- User documentation

**Checkpoint Example (Dynamic Phase):**
```python
evidence = {
    "task_1_complete": True,
    "task_2_complete": True,
    "all_tests_passing": True,
    "code_reviewed": True
}
```

**Usage:**
```python
start_workflow(
    workflow_type="spec_execution_v1",
    target_file="2025-10-12-user-auth"
)
```

---

### agent_os_upgrade_v1

Upgrade prAxIs OS safely with automatic rollback on failure.

**Purpose:** Update prAxIs OS standards, workflows, and MCP server with minimal risk.

**When to Use:** Upgrading to new prAxIs OS version.

**Phases:**

| Phase | Name | Objective | Duration |
|-------|------|-----------|----------|
| 0 | Validation | Validate source/target, check disk space, verify no concurrent workflows | 2-5 min |
| 1 | Backup | Create full backup, verify integrity, acquire upgrade lock | 3-5 min |
| 2 | Content Upgrade | Dry-run, actual upgrade, update .gitignore, verify checksums | 5-10 min |
| 3 | MCP Server Update | Copy server files, install dependencies, restart server | 3-5 min |
| 4 | Validation | Validate tools, run smoke tests, generate report | 2-5 min |
| 5 | Cleanup | Release lock, archive backups, generate summary | 1-2 min |

**Rollback:** Automatic rollback on failure in phases 2-4.

**Output Artifacts:**
- Upgrade report
- Backup archive
- Validation results

**Usage:**
```python
start_workflow(
    workflow_type="agent_os_upgrade_v1",
    target_file="upgrade"
)
```

---

## Workflow Architecture

### Phase Gating

Phases are **architecturally enforced** - skipping is impossible, not just discouraged.

```python
class WorkflowState:
    current_phase: int = 0
    completed_phases: List[int] = []
    
    def can_access_phase(self, phase: int) -> bool:
        # Only current or completed phases accessible
        return phase == self.current_phase or phase in self.completed_phases
```

### Checkpoint System

Evidence-based progression requires verifiable proof before advancing.

**Checkpoint Validation:**
```python
result = complete_phase(
    session_id="abc123",
    phase=1,
    evidence={...}
)

if result.passed:
    current_phase = 2  # Advance
else:
    missing = result.missing_evidence  # Stay on Phase 1
```

### Evidence Validation System

Each phase has a `gate-definition.yaml` file that defines validation requirements.

**Gate Definition Structure:**
```yaml
# Gate Definition - Phase 1: Requirements Gathering
checkpoint:
  strict: false          # Allow override if needed
  allow_override: true   # Permit manual advancement

evidence_schema:
  srd_created:
    type: boolean
    required: true
    description: "Software Requirements Document created"
  
  business_goals_defined:
    type: boolean
    required: true
    description: "Business goals documented in srd.md"

validators: {}  # Optional custom validators
```

**Validation Behavior:**

| Mode | Description | Use Case |
|------|-------------|----------|
| **YAML Validation** | Strict validation against gate-definition.yaml | Workflows with gates (spec_creation_v1, etc.) |
| **RAG Fallback** | Query standards for validation rules | Legacy workflows being migrated |
| **Permissive Mode** | Allow progression with warning | Development/prototyping |

**Field Types:**
- `boolean` - True/False values
- `integer` - Numeric values (e.g., test count)
- `string` - Text values (e.g., file paths)
- `object` - Complex nested structures
- `array` - Lists of values

**Example Validation:**
```python
# Valid evidence
evidence = {
    "srd_created": True,
    "business_goals_defined": True,
    "user_stories_documented": True
}

result = complete_phase(session_id="abc", phase=1, evidence=evidence)
# Returns: {"checkpoint_passed": True, "next_phase": 2}

# Invalid evidence (missing field)
evidence = {
    "srd_created": True
    # Missing required fields!
}

result = complete_phase(session_id="abc", phase=1, evidence=evidence)
# Returns: {
#   "checkpoint_passed": False, 
#   "errors": ["Missing required field: business_goals_defined"],
#   "remediation": "Ensure all required evidence is provided"
# }
```

**Gate Coverage:**

All production workflows have complete gate coverage:
- spec_creation_v1: 6/6 phases
- spec_execution_v1: 1/1 phase
- agent_os_upgrade_v1: 6/6 phases
- workflow_creation_v1: 6/6 phases

### File Size Standards

Based on LLM attention quality research:

| File Type | Size | Attention Quality | Use Case |
|-----------|------|-------------------|----------|
| Task files | 100-170 lines | 95%+ | Single-task execution |
| Phase files | ~80 lines | 95%+ | Phase overview + navigation |
| Methodology | 200-500 lines | 70-85% | Comprehensive guidance |
| Output | Unlimited | N/A | Generated artifacts |

---

## MCP Tool Reference

### Start Workflow

```python
start_workflow(
    workflow_type: str,    # "spec_creation_v1", "spec_execution_v1", etc.
    target_file: str,      # Feature name or spec directory
    options: dict = {}     # Optional workflow-specific config
) -> dict
```

**Returns:**
```python
{
    "session_id": "abc123",
    "current_phase": 0,
    "workflow_type": "spec_creation_v1",
    "phase_content": {...}
}
```

### Get Current Phase

```python
get_current_phase(
    session_id: str
) -> dict
```

**Returns:**
```python
{
    "current_phase": 1,
    "phase_content": {
        "title": "Requirements Gathering",
        "objectives": [...],
        "tasks": [...],
        "deliverables": [...]
    },
    "artifacts": {
        "phase_0": {...}  # Previous phase artifacts
    }
}
```

### Get Task

```python
get_task(
    session_id: str,
    phase: int,
    task_number: int
) -> dict
```

**Returns:**
```python
{
    "task_content": {
        "title": "Define Business Goals",
        "description": "...",
        "steps": [...],
        "acceptance_criteria": [...]
    }
}
```

### Complete Phase

```python
complete_phase(
    session_id: str,
    phase: int,
    evidence: dict
) -> dict
```

**Returns (Success):**
```python
{
    "status": "passed",
    "phase_completed": 1,
    "next_phase": 2,
    "next_phase_content": {...}
}
```

**Returns (Failure):**
```python
{
    "status": "failed",
    "missing_evidence": ["srd_created", "requirements_documented"],
    "current_phase_content": {...}
}
```

### Get Workflow State

```python
get_workflow_state(
    session_id: str
) -> dict
```

**Returns:**
```python
{
    "session_id": "abc123",
    "workflow_type": "spec_creation_v1",
    "current_phase": 2,
    "completed_phases": [0, 1],
    "artifacts": {...},
    "can_resume": True
}
```

---

## Creating Custom Workflows

Use the meta-workflow to create your own workflows:

```python
create_workflow(
    name="api_documentation_v1",
    workflow_type="documentation",
    phases=["Analysis", "Generation", "Review"],
    target_language="python"
)
```

**Generated Structure:**
```
.praxis-os/workflows/api_documentation_v1/
├── metadata.json
├── phases/
│   ├── 0/
│   │   ├── phase.md
│   │   └── task-1-analyze.md
│   ├── 1/
│   │   ├── phase.md
│   │   └── task-1-generate.md
│   └── 2/
│       ├── phase.md
│       └── task-1-review.md
└── README.md
```

**Validation:**
```python
validate_workflow(
    workflow_path=".praxis-os/workflows/api_documentation_v1"
)
```

**See Also:**
- [How-To: Create Custom Workflows](../how-to-guides/create-custom-workflows)
- [Workflow Construction Standards](https://github.com/honeyhiveai/agent-os-enhanced/blob/main/universal/standards/workflows/workflow-construction-standards.md)
- [Workflow Metadata Standards](https://github.com/honeyhiveai/agent-os-enhanced/blob/main/universal/standards/workflows/workflow-metadata-standards.md)

---

## Best Practices

### Execution

- ✅ Execute one task at a time
- ✅ Provide complete, verifiable evidence at checkpoints
- ✅ Review artifacts after each phase
- ✅ Resume workflows rather than restarting
- ❌ Don't attempt to skip phases
- ❌ Don't provide incomplete checkpoint evidence

### Workflow Selection

| Scenario | Workflow |
|----------|----------|
| New feature or major change | `spec_creation_v1` → `spec_execution_v1` |
| Bug fix (non-trivial) | `spec_creation_v1` → `spec_execution_v1` |
| Simple bug fix | Ad-hoc (no workflow needed) |
| Upgrade prAxIs OS | `agent_os_upgrade_v1` |
| Custom process | Create custom workflow |

---

## Related Documentation

- [MCP Tools Reference](./mcp-tools) - Complete workflow tool API
- [How It Works](../explanation/how-it-works) - RAG-driven workflow execution
- [Architecture](../explanation/architecture) - Workflow engine implementation
- [Standards](./standards) - Standards integrated with workflows
