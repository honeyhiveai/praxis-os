# Technical Specifications

**Project:** Spec Creation Workflow (spec_creation_v1)  
**Date:** 2025-10-07

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              User Initiates Spec Creation                    │
│  start_workflow(workflow_type="spec_creation_v1")           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   Workflow Engine             │
         │   Creates Session             │
         │   Determines Starting Phase   │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │ Phase 0: Supporting Docs?     │
         │ (optional - skip if no docs)  │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │ Phase 1: Requirements         │
         │ - Query MCP standards         │
         │ - Guide user through srd.md   │
         │ - Validate completeness       │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │ Phase 2: Technical Design     │
         │ - Query architecture patterns │
         │ - Guide user through specs.md │
         │ - Validate completeness       │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │ Phase 3: Task Breakdown       │
         │ - Guide user through tasks.md │
         │ - Validate task structure     │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │ Phase 4: Implementation Guide │
         │ - Guide through impl.md       │
         │ - Validate patterns           │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │ Phase 5: Finalization         │
         │ - Create README.md            │
         │ - Validate consistency        │
         │ - Mark spec complete          │
         └───────────────────────────────┘
```

---

## 2. Workflow Metadata Structure

**File:** `universal/workflows/spec_creation_v1/metadata.json`

```json
{
  "workflow_type": "spec_creation_v1",
  "version": "1.0.0",
  "name": "Specification Creation Workflow",
  "description": "Systematically create comprehensive specifications with phase-gated validation",
  "author": "Agent OS Team",
  "total_phases": 6,
  "estimated_duration": "1-2 hours (+ supporting docs review time)",
  "dynamic_phases": false,
  "start_phase": 0,
  "phases": [
    {
      "phase_number": 0,
      "phase_name": "Supporting Documents Integration",
      "phase_file": "phases/0/phase.md",
      "skippable": true,
      "skip_condition": "No supporting_docs in options",
      "checkpoint": {
        "required_evidence": [
          "supporting_docs_accessible",
          "document_index_created",
          "insights_extracted"
        ]
      }
    },
    {
      "phase_number": 1,
      "phase_name": "Requirements Gathering",
      "phase_file": "phases/1/phase.md",
      "checkpoint": {
        "required_evidence": [
          "srd_created",
          "business_goals_defined",
          "user_stories_documented",
          "functional_requirements_listed",
          "nfr_defined",
          "out_of_scope_clarified"
        ]
      }
    },
    {
      "phase_number": 2,
      "phase_name": "Technical Design",
      "phase_file": "phases/2/phase.md",
      "checkpoint": {
        "required_evidence": [
          "specs_created",
          "architecture_documented",
          "components_defined",
          "security_addressed",
          "performance_addressed"
        ]
      }
    },
    {
      "phase_number": 3,
      "phase_name": "Task Breakdown",
      "phase_file": "phases/3/phase.md",
      "checkpoint": {
        "required_evidence": [
          "tasks_created",
          "phases_defined",
          "all_tasks_have_acceptance_criteria",
          "dependencies_mapped",
          "validation_gates_specified"
        ]
      }
    },
    {
      "phase_number": 4,
      "phase_name": "Implementation Guidance",
      "phase_file": "phases/4/phase.md",
      "checkpoint": {
        "required_evidence": [
          "implementation_created",
          "code_patterns_documented",
          "testing_strategy_defined",
          "deployment_guidance_specified"
        ]
      }
    },
    {
      "phase_number": 5,
      "phase_name": "Finalization",
      "phase_file": "phases/5/phase.md",
      "checkpoint": {
        "required_evidence": [
          "readme_created",
          "all_files_consistent",
          "spec_validated",
          "ready_for_implementation"
        ]
      }
    }
  ]
}
```

---

## 3. Phase Content Structure

### Meta-Framework Compliance

Following **three-tier architecture** and **horizontal decomposition** standards:

**Phase Files:** `phase.md` (~80 lines)
- Phase metadata and objective
- Task list with links (brief)
- Execution approach
- Phase deliverables
- Phase-level validation gate
- Navigation to first task

**Task Files:** `task-N-name.md` (100-170 lines)
- Single-responsibility execution instructions
- Detailed steps with command language
- Task-specific validation
- Evidence collection
- Link to next task

**Rationale:** Based on actual working workflows (`spec_execution_v1`). Phase files are concise overviews; task files contain detailed execution.

---

### Phase File Template

`phases/N/phase.md` (~80 lines):

```markdown
# Phase N: [Phase Name]

**Phase Number:** N  
**Purpose:** [What this phase accomplishes]  
**Estimated Time:** [Duration]  
**Total Tasks:** [N]

---

## 🎯 Phase Objective

[1-2 paragraph description of what user will accomplish in this phase]

---

## Tasks in This Phase

### Task 1: [Task Name]
**File:** [task-1-name.md](task-1-name.md)  
**Purpose:** [Brief description]  
**Time:** [Duration]

### Task 2: [Task Name]
**File:** [task-2-name.md](task-2-name.md)  
**Purpose:** [Brief description]  
**Time:** [Duration]

[Repeat for all tasks]

---

## Execution Approach

🛑 EXECUTE-NOW: Complete tasks sequentially

Tasks must be completed in order: 1 → 2 → 3 → ...

Each task builds on the previous one's output.

---

## Phase Deliverables

Upon completion, you will have:
- ✅ [Deliverable 1]
- ✅ [Deliverable 2]
- ✅ [Deliverable 3]

---

## Validation Gate

🛑 VALIDATE-GATE: Phase N Checkpoint

Before advancing to Phase N+1:
- [ ] [Phase-level criterion 1] ✅/❌
- [ ] [Phase-level criterion 2] ✅/❌
- [ ] [Phase-level criterion 3] ✅/❌

---

## Start Phase N

🎯 NEXT-MANDATORY: [task-1-name.md](task-1-name.md)

Begin with Task 1 to [brief description].
```

---

### Task File Template

`phases/N/task-X-name.md` (100-170 lines):

```markdown
# Task X: [Task Name]

**Phase:** N ([Phase Name])  
**Purpose:** [What this task accomplishes]  
**Estimated Time:** [Duration]

---

## 🎯 Objective

[Clear 1-2 paragraph statement of what user creates/accomplishes in this task]

---

## Prerequisites

🛑 EXECUTE-NOW: Verify dependencies

[Prerequisites statement if any]

⚠️ MUST-READ: [Relevant documentation]

---

## Steps

### Step 1: [Action Name]

[Detailed instructions for this step]

```bash
# Example command if applicable
command here
```

📊 COUNT-AND-DOCUMENT: [What to measure]
- Metric 1: [value]
- Metric 2: [value]

### Step 2: [Action Name]

🛑 VALIDATE-GATE: [Checkpoint Name]

[Instructions with validation criteria]

- [ ] Criterion 1 ✅/❌
- [ ] Criterion 2 ✅/❌

### Step 3: [Action Name]

[Instructions]

**MCP Query:**
```python
MCP: search_standards("[specific query]")
```

[Continue with more steps as needed]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] [Acceptance criterion 1] ✅/❌
- [ ] [Acceptance criterion 2] ✅/❌
- [ ] [Acceptance criterion 3] ✅/❌

🚨 FRAMEWORK-VIOLATION: [What not to do]

[Warning about common mistakes or skipped steps]

---

## Evidence Collection

📊 COUNT-AND-DOCUMENT: Task Results

**[Category 1]:**
- Item: [value]
- Item: [value]

**[Category 2]:**
- Item: [value]

**Validation:** [PASS/FAIL]

---

## Next Task

🎯 NEXT-MANDATORY: [task-X+1-name.md](task-X+1-name.md)

[Brief description of what's next, or indicate phase completion]
```

---

## 4. Directory Structure

```
universal/workflows/spec_creation_v1/
├── metadata.json                           # Workflow definition
├── phases/
│   ├── 0/                                  # Phase 0 (Optional)
│   │   ├── phase.md                       # 200-300 lines: Overview + task links
│   │   ├── task-1-setup-directory.md      # 60-100 lines
│   │   ├── task-2-process-documents.md    # 60-100 lines
│   │   ├── task-3-create-index.md         # 60-100 lines
│   │   └── task-4-extract-insights.md     # 60-100 lines
│   ├── 1/                                  # Phase 1: Requirements
│   │   ├── phase.md                       # 200-300 lines
│   │   ├── task-1-business-goals.md       # 60-100 lines
│   │   ├── task-2-user-stories.md         # 60-100 lines
│   │   ├── task-3-functional-reqs.md      # 60-100 lines
│   │   ├── task-4-nonfunctional-reqs.md   # 60-100 lines
│   │   └── task-5-out-of-scope.md         # 60-100 lines
│   ├── 2/                                  # Phase 2: Technical Design
│   │   ├── phase.md                       # 200-300 lines
│   │   ├── task-1-architecture.md         # 60-100 lines
│   │   ├── task-2-components.md           # 60-100 lines
│   │   ├── task-3-apis.md                 # 60-100 lines
│   │   ├── task-4-data-models.md          # 60-100 lines
│   │   ├── task-5-security.md             # 60-100 lines
│   │   └── task-6-performance.md          # 60-100 lines
│   ├── 3/                                  # Phase 3: Task Breakdown
│   │   ├── phase.md                       # 200-300 lines
│   │   ├── task-1-identify-phases.md      # 60-100 lines
│   │   ├── task-2-break-down-tasks.md     # 60-100 lines
│   │   ├── task-3-acceptance-criteria.md  # 60-100 lines
│   │   ├── task-4-map-dependencies.md     # 60-100 lines
│   │   └── task-5-validation-gates.md     # 60-100 lines
│   ├── 4/                                  # Phase 4: Implementation Guidance
│   │   ├── phase.md                       # 200-300 lines
│   │   ├── task-1-code-patterns.md        # 60-100 lines
│   │   ├── task-2-testing-strategy.md     # 60-100 lines
│   │   ├── task-3-deployment.md           # 60-100 lines
│   │   └── task-4-troubleshooting.md      # 60-100 lines
│   └── 5/                                  # Phase 5: Finalization
│       ├── phase.md                       # 200-300 lines
│       ├── task-1-create-readme.md        # 60-100 lines
│       ├── task-2-check-consistency.md    # 60-100 lines
│       └── task-3-final-review.md         # 60-100 lines
└── core/
    ├── srd-template.md                    # Template for requirements document
    ├── specs-template.md                  # Template for technical design
    └── validation-helpers.md              # Validation guidance
```

**Meta-Framework Compliance:**
- Phase files: 6 × ~80 lines (`phase.md` - overview + task links)
- Task files: ~25 × 100-170 lines (`task-N-name.md` - detailed execution)
- Pattern based on: `spec_execution_v1` (validated working workflow)
- Horizontal decomposition: Single-responsibility task files
- Optimal AI attention: Concise phase overviews, detailed task execution

---

## 5. Workflow Session State

```python
@dataclass
class SpecCreationState(WorkflowState):
    """Extended state for spec creation workflow."""
    
    # Standard workflow fields
    session_id: str
    workflow_type: str  # "spec_creation_v1"
    target_file: str    # Feature name for directory
    current_phase: int
    completed_phases: List[int]
    
    # Spec-specific fields
    spec_directory: Path           # .agent-os/specs/YYYY-MM-DD-{target_file}
    feature_description: str
    priority: str                  # Critical|High|Medium|Low
    category: str                  # Feature|Enhancement|Fix
    
    # Supporting documents (Phase 0)
    supporting_docs: List[str]     # File paths
    embed_supporting_docs: bool    # Copy vs reference
    supporting_docs_processed: bool
    
    # Created files tracking
    created_files: Dict[str, bool] = field(default_factory=lambda: {
        "supporting-docs/INDEX.md": False,
        "srd.md": False,
        "specs.md": False,
        "tasks.md": False,
        "implementation.md": False,
        "README.md": False
    })
    
    # Validation evidence
    validation_evidence: Dict[int, Dict[str, Any]] = field(default_factory=dict)
```

---

## 6. Phase 0: Supporting Documents Integration

### 6.1 Conditional Execution

Phase 0 only runs if `supporting_docs` provided in options:

```python
def should_run_phase_0(options: Dict[str, Any]) -> bool:
    """Determine if Phase 0 should run."""
    return "supporting_docs" in options and len(options["supporting_docs"]) > 0

# In workflow engine
if current_phase == 0 and not should_run_phase_0(state.metadata):
    # Skip to Phase 1
    state.current_phase = 1
    state_manager.save_state(state)
```

### 6.2 Document Processing

```python
def process_supporting_docs(
    docs: List[str],
    embed: bool,
    spec_dir: Path
) -> Dict[str, Any]:
    """
    Process supporting documents for Phase 0.
    
    Args:
        docs: List of document paths
        embed: Whether to copy docs or just reference
        spec_dir: Spec directory path
        
    Returns:
        Processing results with insights
    """
    supporting_dir = spec_dir / "supporting-docs"
    supporting_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "docs_processed": [],
        "insights": {
            "requirements": [],
            "design": [],
            "implementation": []
        }
    }
    
    for doc_path in docs:
        if embed:
            # Copy document
            shutil.copy2(doc_path, supporting_dir)
        else:
            # Create reference
            # (stored in INDEX.md)
            pass
        
        # Extract insights (manual user task, guided by phase content)
        results["docs_processed"].append(doc_path)
    
    return results
```

### 6.3 INDEX.md Template

```markdown
# Supporting Documents Index

This spec incorporates the following pre-existing documents:

## 1. [{DOCUMENT_NAME}]({FILENAME})

**Created:** {DATE}  
**Purpose:** {PURPOSE}

**Key Insights:**

### Requirements
- {INSIGHT_1}
- {INSIGHT_2}

### Design
- {INSIGHT_1}
- {INSIGHT_2}

### Implementation
- {INSIGHT_1}
- {INSIGHT_2}

---

## 2. [Next Document...]
```

---

## 7. Validation System

### 7.1 Validation Rules

```python
class SpecValidationRules:
    """Validation rules for spec creation."""
    
    PHASE_0_RULES = {
        "supporting_docs_accessible": lambda state: all(
            (state.spec_directory / "supporting-docs" / Path(doc).name).exists()
            for doc in state.supporting_docs
        ) if state.embed_supporting_docs else True,
        
        "document_index_created": lambda state: 
            (state.spec_directory / "supporting-docs" / "INDEX.md").exists(),
        
        "insights_extracted": lambda evidence: 
            len(evidence.get("insights", {}).get("requirements", [])) > 0
    }
    
    PHASE_1_RULES = {
        "srd_created": lambda state: 
            (state.spec_directory / "srd.md").exists(),
        
        "business_goals_defined": lambda evidence: 
            len(evidence.get("business_goals", [])) >= 1,
        
        "user_stories_documented": lambda evidence: 
            evidence.get("user_stories", 0) >= 1,
        
        "functional_requirements_listed": lambda evidence: 
            evidence.get("functional_requirements", 0) >= 3,
        
        "nfr_defined": lambda evidence: 
            evidence.get("nfr_defined", False),
        
        "out_of_scope_clarified": lambda evidence: 
            evidence.get("out_of_scope_clarified", False)
    }
    
    # Similar for phases 2-5...
```

### 7.2 Validation Execution

```python
def validate_phase(phase: int, state: SpecCreationState, evidence: Dict) -> ValidationResult:
    """
    Validate phase completion.
    
    Args:
        phase: Phase number
        state: Current workflow state
        evidence: Evidence provided by user
        
    Returns:
        ValidationResult with pass/fail and missing items
    """
    rules = getattr(SpecValidationRules, f"PHASE_{phase}_RULES")
    
    missing = []
    for rule_name, rule_func in rules.items():
        try:
            if not rule_func(state if "state" in signature(rule_func) else evidence):
                missing.append(rule_name)
        except Exception as e:
            missing.append(f"{rule_name} (error: {e})")
    
    return ValidationResult(
        passed=len(missing) == 0,
        missing_evidence=missing
    )
```

---

## 8. MCP Integration

### 8.1 Automatic Standards Queries

Each phase automatically queries relevant standards:

```python
PHASE_MCP_QUERIES = {
    0: [
        "incorporating existing documentation",
        "spec creation from analysis"
    ],
    1: [
        "creating specifications requirements",
        "user story best practices",
        "functional requirements standards"
    ],
    2: [
        "architecture patterns",
        "API design principles",
        "data modeling best practices",
        "security considerations",
        "performance optimization"
    ],
    3: [
        "task breakdown best practices",
        "phased implementation",
        "dependency management"
    ],
    4: [
        "production code checklist",
        "{language} code patterns",
        "testing strategies",
        "deployment best practices"
    ],
    5: [
        "spec validation",
        "documentation completeness"
    ]
}

def get_phase_content(session_id: str, phase: int) -> Dict:
    """Get phase content with MCP query results."""
    queries = PHASE_MCP_QUERIES.get(phase, [])
    
    mcp_results = {}
    for query in queries:
        mcp_results[query] = search_standards(query, n_results=3)
    
    return {
        "phase_content": load_phase_file(phase),
        "mcp_guidance": mcp_results
    }
```

---

## 9. File Creation Templates

### 9.1 Directory Creation

```python
def create_spec_directory(target_file: str) -> Path:
    """
    Create spec directory with standard structure.
    
    Args:
        target_file: Feature name
        
    Returns:
        Path to created directory
    """
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    spec_dir = Path(f".agent-os/specs/{date_prefix}-{target_file}")
    
    spec_dir.mkdir(parents=True, exist_ok=True)
    
    return spec_dir
```

### 9.2 File Templates

Each phase creates files with standard headers:

```python
def create_srd_template(spec_dir: Path, feature_desc: str) -> Path:
    """Create srd.md template."""
    srd_path = spec_dir / "srd.md"
    
    template = f"""# Software Requirements Document

**Project:** {feature_desc}  
**Date:** {datetime.now().strftime("%Y-%m-%d")}

---

## 1. Introduction

### 1.1 Purpose

[Define the purpose of this feature]

### 1.2 Scope

[Define what's included and what's not]

---

## 2. Business Goals

[Define business objectives]

---

## 3. User Stories

[Document user stories]

---

## 4. Functional Requirements

[List functional requirements]

---

## 5. Non-Functional Requirements

[List non-functional requirements]

---

## 6. Out of Scope

[Explicitly state what's not included]
"""
    
    srd_path.write_text(template)
    return srd_path
```

---

## 10. Testing Strategy

### 10.1 Unit Tests

```python
# tests/unit/test_spec_creation_workflow.py

def test_phase_0_skipped_without_supporting_docs():
    """Test Phase 0 skipped when no supporting docs."""
    state = create_test_state(supporting_docs=[])
    assert not should_run_phase_0(state.metadata)

def test_phase_0_runs_with_supporting_docs():
    """Test Phase 0 runs when supporting docs provided."""
    state = create_test_state(supporting_docs=["doc1.md"])
    assert should_run_phase_0(state.metadata)

def test_validation_phase_1_requires_minimum():
    """Test Phase 1 validation enforces minimums."""
    evidence = {
        "business_goals": ["goal1"],
        "user_stories": 1,
        "functional_requirements": 2  # Less than minimum 3
    }
    result = validate_phase(1, None, evidence)
    assert not result.passed
    assert "functional_requirements_listed" in result.missing_evidence
```

### 10.2 Integration Tests

```python
def test_complete_spec_creation_without_supporting_docs():
    """Test end-to-end spec creation."""
    # Start workflow
    response = start_workflow(
        workflow_type="spec_creation_v1",
        target_file="test-feature",
        options={"feature_description": "Test feature"}
    )
    session_id = response["session_id"]
    
    # Should start at Phase 1 (skip Phase 0)
    state = get_workflow_state(session_id)
    assert state["current_phase"] == 1
    
    # Complete Phase 1
    complete_phase(session_id, 1, evidence={...})
    
    # Continue through all phases...
    
    # Verify all files created
    spec_dir = Path(f".agent-os/specs/{date}-test-feature")
    assert (spec_dir / "srd.md").exists()
    assert (spec_dir / "specs.md").exists()
    assert (spec_dir / "tasks.md").exists()
    assert (spec_dir / "implementation.md").exists()
    assert (spec_dir / "README.md").exists()

def test_complete_spec_creation_with_supporting_docs():
    """Test end-to-end with Phase 0."""
    response = start_workflow(
        workflow_type="spec_creation_v1",
        target_file="test-feature",
        options={
            "supporting_docs": ["analysis.md"],
            "embed_supporting_docs": True
        }
    )
    session_id = response["session_id"]
    
    # Should start at Phase 0
    state = get_workflow_state(session_id)
    assert state["current_phase"] == 0
    
    # Complete Phase 0
    complete_phase(session_id, 0, evidence={...})
    
    # Verify supporting-docs/ created
    spec_dir = Path(f".agent-os/specs/{date}-test-feature")
    assert (spec_dir / "supporting-docs" / "INDEX.md").exists()
    assert (spec_dir / "supporting-docs" / "analysis.md").exists()
```

---

## 11. Performance Considerations

### 11.1 File Operations

- Use pathlib for cross-platform compatibility
- Create directories lazily (only when needed)
- Minimize file I/O (batch operations)

### 11.2 MCP Queries

- Query standards at phase start (not repeatedly)
- Cache results in phase content response
- Limit to 3 results per query for responsiveness

### 11.3 State Persistence

- Save state after each phase completion
- Use JSON for fast serialization
- Keep state object small (< 10KB)

---

## 12. Error Handling

### 12.1 Common Errors

| Error | Cause | Handling |
|-------|-------|----------|
| Directory exists | Spec already created | Prompt: Continue or rename? |
| Supporting doc not found | Invalid path | Clear error, list valid paths |
| Validation fails | Missing evidence | Show specific missing items |
| MCP query fails | Network/server issue | Show cached guidance, continue |

### 12.2 Recovery

```python
def handle_spec_creation_error(error: Exception, state: SpecCreationState):
    """Handle errors during spec creation."""
    if isinstance(error, FileNotFoundError):
        # Supporting doc not found
        return {
            "error": f"Supporting document not found: {error.filename}",
            "resolution": "Check file path and try again",
            "can_continue": False
        }
    
    elif isinstance(error, ValidationError):
        # Phase validation failed
        return {
            "error": "Phase validation failed",
            "missing": error.missing_evidence,
            "resolution": "Complete missing requirements and try again",
            "can_continue": True
        }
    
    else:
        # Unexpected error
        logger.error(f"Unexpected error in spec creation: {error}")
        return {
            "error": "Unexpected error occurred",
            "resolution": "Check logs, workflow state saved and can resume",
            "can_continue": True
        }
```

---

## 13. Security Considerations

### 13.1 File System Access

- Validate all file paths (prevent directory traversal)
- Only create files within `.agent-os/specs/`
- Check file permissions before writing

### 13.2 User Input

- Sanitize `target_file` (no special characters)
- Validate file paths in `supporting_docs`
- Limit file sizes for embedding

---

**Technical specifications complete. Ready for implementation.**
