# Implementation Approach

**Project:** Spec Creation Workflow (spec_creation_v1)  
**Date:** 2025-10-07

---

## 1. Implementation Philosophy

**Core Principles:**
1. **User-Guided:** Workflow guides, doesn't generate
2. **Quality-Gated:** Validate before advancing
3. **Context-Preserving:** Integrate existing work (Phase 0)
4. **Standards-Driven:** Auto-query MCP for guidance
5. **Incremental:** Build phase-by-phase, test thoroughly

---

## 2. Implementation Order

### Phase 1: Workflow Structure
**Rationale:** Foundation before content

1. Create directory structure
2. Create metadata.json
3. Define validation rules
4. Test workflow registration

### Phase 2: Phase Content (0-5)
**Rationale:** Content before logic

1. Write Phase 0 content (supporting docs)
2. Write Phase 1 content (requirements)
3. Write Phase 2 content (design)
4. Write Phase 3 content (tasks)
5. Write Phase 4 content (implementation)
6. Write Phase 5 content (finalization)

### Phase 3: Integration
**Rationale:** Connect to workflow engine

1. Test Phase 0 skip logic
2. Test MCP query integration
3. Test validation gates
4. Test file creation

### Phase 4: Testing and Dogfooding
**Rationale:** Validate end-to-end

1. Unit tests
2. Integration tests
3. Dogfood: Create real spec using workflow
4. Documentation

---

## 3. File Creation Strategy

### 3.1 Directory Structure

```bash
mkdir -p universal/workflows/spec_creation_v1/{phases/{0,1,2,3,4,5},core}
```

### 3.2 metadata.json

**Start with minimal, expand:**

```json
{
  "workflow_type": "spec_creation_v1",
  "version": "1.0.0",
  "name": "Specification Creation Workflow",
  "description": "Systematically create comprehensive specifications",
  "total_phases": 6,
  "phases": [
    {
      "phase_number": 0,
      "phase_name": "Supporting Documents Integration",
      "phase_file": "phases/0/phase.md",
      "skippable": true
    }
    // ... phases 1-5
  ]
}
```

**Key:** Use `skippable: true` for Phase 0

---

## 4. Phase Content Implementation

**CRITICAL:** Follow **Workflow Construction Standards** from `universal/standards/workflows/workflow-construction-standards.md`

### Key Principles
1. **Phase files:** ~80 lines (overview + task links)
2. **Task files:** 100-170 lines (detailed execution)
3. **Pattern:** Based on `spec_execution_v1` (validated working workflow)
4. **Each task = separate file** (horizontal decomposition)

---

### 4.1 Phase 0: Supporting Documents

**Files to Create:**
- `phases/0/phase.md` (~80 lines)
- `phases/0/task-1-copy-documents.md` (100-170 lines)
- `phases/0/task-2-create-index.md` (100-170 lines)
- `phases/0/task-3-extract-insights.md` (100-170 lines)

**Phase File Structure:** `phases/0/phase.md`

```markdown
# Phase 0: Supporting Documents Integration

**Phase Number:** 0  
**Purpose:** Incorporate pre-existing documents into spec structure  
**Estimated Time:** 10-20 minutes  
**Total Tasks:** 3

**Note:** This phase is OPTIONAL and only runs if supporting_docs provided.

---

## 🎯 Phase Objective

Process existing analysis, research, or design documents to extract insights that will inform requirements, design, and implementation phases.

---

## Tasks in This Phase

### Task 1: Copy or Reference Documents
**File:** [task-1-copy-documents.md](task-1-copy-documents.md)  
**Purpose:** Make documents accessible in spec directory  
**Time:** 5 minutes

### Task 2: Create Document Index
**File:** [task-2-create-index.md](task-2-create-index.md)  
**Purpose:** Catalog all documents with structured metadata  
**Time:** 5 minutes

### Task 3: Extract Key Insights
**File:** [task-3-extract-insights.md](task-3-extract-insights.md)  
**Purpose:** Extract and categorize insights for later phases  
**Time:** 10 minutes

---

## Execution Approach

🛑 EXECUTE-NOW: Complete tasks sequentially

Tasks must be completed in order: 1 → 2 → 3

---

## Phase Deliverables

Upon completion, you will have:
- ✅ All supporting docs accessible (copied or referenced)
- ✅ INDEX.md with document catalog
- ✅ Extracted insights (requirements/design/implementation)

---

## Validation Gate

🛑 VALIDATE-GATE: Phase 0 Checkpoint

Before advancing to Phase 1:
- [ ] All documents accessible ✅/❌
- [ ] INDEX.md complete ✅/❌
- [ ] Insights extracted and categorized ✅/❌

---

## Start Phase 0

🎯 NEXT-MANDATORY: [task-1-copy-documents.md](task-1-copy-documents.md)

Begin with Task 1 to copy or reference supporting documents.
```

**Task File Example:** `phases/0/task-1-copy-documents.md`

```markdown
# Task 1: Copy or Reference Documents

**Phase:** 0 (Supporting Documents Integration)  
**Purpose:** Make supporting documents accessible in spec directory  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Copy provided documents to `supporting-docs/` directory or create reference links, depending on embed mode.

---

## Prerequisites

🛑 EXECUTE-NOW: Verify supporting docs provided

You provided these documents: {LIST_OF_DOCS}
Embedding mode: {EMBED_MODE}

---

## Steps

### Step 1: Create Directory

```bash
mkdir -p .agent-os/specs/{spec_dir}/supporting-docs/
```

### Step 2: Copy or Reference

{IF embed_supporting_docs == true}

**Copy documents:**
```bash
cp {doc1} .agent-os/specs/{spec_dir}/supporting-docs/
cp {doc2} .agent-os/specs/{spec_dir}/supporting-docs/
```

{ELSE}

**Create reference file:**
Create `supporting-docs/REFERENCES.md`:
```markdown
# Document References

- [{doc1}]({original_path1})
- [{doc2}]({original_path2})
```

{ENDIF}

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

- [ ] supporting-docs/ directory created ✅/❌
- [ ] All documents accessible ✅/❌
- [ ] Files readable and valid ✅/❌

---

## Next Task

🎯 NEXT-MANDATORY: [task-2-create-index.md](task-2-create-index.md)

Continue to Task 2 to create document index.
```

**Implementation Note:**
- Phase file is ~80 lines (overview only)
- Each task file is 100-170 lines (detailed execution)
- Placeholders (`{LIST_OF_DOCS}`) replaced by workflow engine

---

### 4.2 Phase 1: Requirements Gathering

**Files to Create:**
- `phases/1/phase.md` (~80 lines)
- `phases/1/task-1-business-goals.md` (100-170 lines)
- `phases/1/task-2-user-stories.md` (100-170 lines)
- `phases/1/task-3-functional-requirements.md` (100-170 lines)
- `phases/1/task-4-nonfunctional-requirements.md` (100-170 lines)
- `phases/1/task-5-out-of-scope.md` (100-170 lines)

**Structure:** Phase file provides overview (~80 lines), each task file contains detailed steps, templates, and MCP queries (100-170 lines).

**Pattern:** Same as Phase 0 - phase.md links to task files, task files have detailed execution steps.

---

### 4.3 Phase 2: Technical Design

**Files to Create:**
- `phases/2/phase.md` (~80 lines)
- `phases/2/task-1-architecture.md` (100-170 lines) - includes ASCII diagram templates
- `phases/2/task-2-components.md` (100-170 lines)
- `phases/2/task-3-apis.md` (100-170 lines)
- `phases/2/task-4-data-models.md` (100-170 lines)
- `phases/2/task-5-security.md` (100-170 lines)
- `phases/2/task-6-performance.md` (100-170 lines)

**Key Content:** Architecture task file includes ASCII diagram templates like:
```
┌─────────────────┐
│   Component 1   │
└────────┬────────┘
         ▼
┌─────────────────┐
│   Component 2   │
└─────────────────┘
```

---

### 4.4 Phase 3: Task Breakdown

**Files to Create:**
- `phases/3/phase.md` (~80 lines)
- `phases/3/task-1-identify-phases.md` (100-170 lines)
- `phases/3/task-2-break-down-tasks.md` (100-170 lines) - includes task template
- `phases/3/task-3-acceptance-criteria.md` (100-170 lines)
- `phases/3/task-4-map-dependencies.md` (100-170 lines)
- `phases/3/task-5-validation-gates.md` (100-170 lines)

**Key Content:** Task 2 includes template for task format with acceptance criteria.

---

### 4.5 Phase 4: Implementation Guidance

**Files to Create:**
- `phases/4/phase.md` (~80 lines)
- `phases/4/task-1-code-patterns.md` (100-170 lines) - includes code examples
- `phases/4/task-2-testing-strategy.md` (100-170 lines)
- `phases/4/task-3-deployment.md` (100-170 lines)
- `phases/4/task-4-troubleshooting.md` (100-170 lines)

**Key Content:** Task 1 includes code pattern templates with examples, best practices, and anti-patterns.

---

### 4.6 Phase 5: Finalization

**Files to Create:**
- `phases/5/phase.md` (~80 lines)
- `phases/5/task-1-create-readme.md` (100-170 lines) - includes README template
- `phases/5/task-2-check-consistency.md` (100-170 lines) - includes consistency checklist
- `phases/5/task-3-final-review.md` (100-170 lines)

**Key Content:** Task 1 provides README template with executive summary structure.

---

**Implementation Note for All Phases:**
- **Phase files:** ~80 lines (overview + task list + validation gate)
- **Task files:** 100-170 lines (detailed steps + templates + validation)
- **Pattern:** Matches `spec_execution_v1` (validated working workflow)
- **Reference:** See `universal/standards/workflows/workflow-construction-standards.md`

---

## 5. Validation Logic Implementation

### 5.1 Phase 0 Validation

```python
def validate_phase_0(state: SpecCreationState, evidence: Dict) -> ValidationResult:
    """Validate Phase 0 completion."""
    missing = []
    
    # Check documents accessible
    if state.embed_supporting_docs:
        supporting_dir = state.spec_directory / "supporting-docs"
        for doc in state.supporting_docs:
            doc_name = Path(doc).name
            if not (supporting_dir / doc_name).exists():
                missing.append(f"Document not found: {doc_name}")
    
    # Check INDEX.md exists
    index_path = state.spec_directory / "supporting-docs" / "INDEX.md"
    if not index_path.exists():
        missing.append("INDEX.md not created")
    
    # Check insights extracted
    insights = evidence.get("insights_extracted", {})
    if not insights.get("requirements") or len(insights["requirements"]) == 0:
        missing.append("No requirements insights extracted")
    
    return ValidationResult(
        passed=len(missing) == 0,
        missing_evidence=missing
    )
```

### 5.2 Phase 1 Validation

```python
def validate_phase_1(state: SpecCreationState, evidence: Dict) -> ValidationResult:
    """Validate Phase 1 completion."""
    missing = []
    
    # Check srd.md exists
    if not (state.spec_directory / "srd.md").exists():
        missing.append("srd.md not created")
    
    # Check business goals (minimum 1)
    if len(evidence.get("business_goals", [])) < 1:
        missing.append("At least 1 business goal required")
    
    # Check user stories (minimum 1)
    if evidence.get("user_stories", 0) < 1:
        missing.append("At least 1 user story required")
    
    # Check functional requirements (minimum 3)
    if evidence.get("functional_requirements", 0) < 3:
        missing.append("At least 3 functional requirements required")
    
    # Check NFR defined
    if not evidence.get("nfr_defined"):
        missing.append("Non-functional requirements not defined")
    
    # Check out of scope clarified
    if not evidence.get("out_of_scope_clarified"):
        missing.append("Out of scope not clarified")
    
    return ValidationResult(
        passed=len(missing) == 0,
        missing_evidence=missing
    )
```

**Similar validation for phases 2-5**

---

## 6. MCP Integration Implementation

### 6.1 Auto-Query in Phase Content

```python
def get_phase_content_with_mcp(session_id: str, phase: int) -> Dict:
    """Get phase content with automatic MCP queries."""
    
    # Load phase content
    phase_content = load_phase_markdown(phase)
    
    # Get MCP queries for this phase
    queries = PHASE_MCP_QUERIES.get(phase, [])
    
    # Execute queries
    mcp_results = {}
    for query in queries:
        try:
            results = search_standards(query, n_results=3)
            mcp_results[query] = results
        except Exception as e:
            logger.warning(f"MCP query failed: {query} - {e}")
            mcp_results[query] = {"error": str(e)}
    
    # Inject MCP results into phase content
    # (displayed as collapsible section in response)
    return {
        "phase_number": phase,
        "phase_content": phase_content,
        "mcp_guidance": mcp_results,
        "instructions": "Review MCP guidance, then complete phase tasks"
    }
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

```python
# tests/unit/test_spec_creation_validation.py

def test_phase_0_validation_requires_index():
    """Test Phase 0 validation requires INDEX.md."""
    state = create_test_state()
    evidence = {"insights_extracted": {"requirements": 1}}
    
    result = validate_phase_0(state, evidence)
    assert not result.passed
    assert "INDEX.md not created" in result.missing_evidence

def test_phase_1_validation_requires_minimums():
    """Test Phase 1 enforces minimum requirements."""
    state = create_test_state()
    evidence = {
        "business_goals": ["goal1"],
        "user_stories": 1,
        "functional_requirements": 2  # Less than 3
    }
    
    result = validate_phase_1(state, evidence)
    assert not result.passed
    assert any("3 functional requirements" in m for m in result.missing_evidence)
```

### 7.2 Integration Tests

```python
def test_complete_workflow_without_supporting_docs():
    """Test full workflow from start to finish."""
    # Start workflow
    response = start_workflow(
        workflow_type="spec_creation_v1",
        target_file="test-feature",
        options={
            "feature_description": "Test feature",
            "priority": "High",
            "category": "Feature"
        }
    )
    
    session_id = response["session_id"]
    
    # Should skip Phase 0, start at Phase 1
    state = get_workflow_state(session_id)
    assert state["current_phase"] == 1
    
    # Complete all phases...
    
    # Verify all files created
    spec_dir = Path(f".agent-os/specs/2025-10-07-test-feature")
    assert (spec_dir / "srd.md").exists()
    assert (spec_dir / "specs.md").exists()
    assert (spec_dir / "tasks.md").exists()
    assert (spec_dir / "implementation.md").exists()
    assert (spec_dir / "README.md").exists()
```

### 7.3 Dogfooding Test

**Create a real spec using this workflow:**

```python
# Use spec_creation_v1 to create spec for a simple feature
response = start_workflow(
    workflow_type="spec_creation_v1",
    target_file="example-feature",
    options={
        "feature_description": "Example feature for testing",
        "priority": "Low",
        "category": "Feature"
    }
)

# Work through all phases manually
# Document any issues or improvements needed
# Verify quality of generated spec
```

---

## 8. Documentation Strategy

### 8.1 Update Usage Guide

**File:** `universal/usage/creating-specs.md`

Add new section:
```markdown
## Using spec_creation_v1 Workflow

### Start Workflow

```python
response = start_workflow(
    workflow_type="spec_creation_v1",
    target_file="feature-name",
    options={
        "feature_description": "Brief description",
        "priority": "High",
        "category": "Feature",
        "supporting_docs": ["doc1.md"],  # Optional
        "embed_supporting_docs": true     # Optional
    }
)
```

### Work Through Phases

[Phase-by-phase guide]

### Tips

- Take your time in Phase 1 (requirements are foundational)
- Use supporting docs (Phase 0) if you have existing analysis
- Validate thoroughly before advancing phases
```

---

## 9. Rollout Strategy

### 9.1 Development Phase

1. Create workflow structure
2. Write all phase content
3. Unit tests passing
4. Integration tests passing

### 9.2 Dogfooding Phase

1. Use workflow to create a real spec
2. Document experience
3. Fix any issues discovered
4. Refine phase content based on experience

### 9.3 Release Phase

1. Merge to main
2. Update documentation
3. Announce in README
4. Add example usage

---

## 10. Success Metrics

### 10.1 Development Metrics

- [ ] All 6 phases created
- [ ] Unit tests: >90% coverage
- [ ] Integration test: Full workflow pass
- [ ] Dogfooding: Successfully created real spec
- [ ] Documentation: Complete

### 10.2 User Metrics

- [ ] Spec creation time: <2 hours
- [ ] Spec quality: All sections complete
- [ ] Validation gates: Catch missing sections
- [ ] Resume capability: Works correctly

---

**Implementation guide complete. Ready for task breakdown.**
