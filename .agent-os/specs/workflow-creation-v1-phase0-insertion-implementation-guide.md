# workflow_creation_v1: Phase 0 Insertion Implementation Guide

**Date:** 2025-10-13  
**Purpose:** Insert new Phase 0 for design document conversion  
**Status:** Implementation Ready  
**Estimated Time:** 90 minutes (AI agent execution)

---

## Context & Rationale

### Problem Statement

The `workflow_creation_v1` workflow currently expects a YAML definition file as input. However, in the Agent OS Enhanced operating model, the natural output of Phase 2 (Spec Creation) is a **markdown design document** (e.g., `design-spec.md`).

**Current Flow (Broken):**
```
Phase 2: Spec Creation
    ↓ OUTPUT: design-spec.md (markdown)
    ↓
    ❌ GAP: No conversion mechanism
    ↓
Phase 3: Build (workflow_creation_v1)
    ↓ EXPECTS: workflow-definition.yaml (YAML)
```

**Usage Reality:**
- 90%+ of the time, input will be design documents (markdown)
- 10% of the time, input will be pre-built YAML definitions (expert mode, programmatic use)

### Why Insert New Phase 0 (Not Extend Existing)?

**Key Context:** There are **zero users yet** - workflow built ~12 hours ago.

**Advantages of Inserting:**
1. **Separation of Concerns** - Conversion vs validation are different responsibilities
2. **Future-Proof** - Can add PDF, Notion, Confluence support to Phase 0 later
3. **Clear Error Boundaries** - Phase 0 = input problem, Phase 1 = validation problem
4. **Models Best Practices** - Shows horizontal decomposition to other workflows
5. **No Tech Debt** - Get architecture right on Day 1

**No Downsides:**
- ❌ No existing users to break
- ❌ No backward compatibility concerns
- ❌ No mental models to preserve

**Decision:** Insert new Phase 0 for input conversion and preprocessing.

---

## Architecture Overview

### New Phase Structure

```
Phase 0: Input Conversion & Preprocessing (NEW)
  Purpose: Accept multiple input formats, normalize to YAML definition
  Tasks: 5 tasks
  Gate: Ensure valid YAML definition exists

Phase 1: Definition Import & Validation (CURRENT Phase 0 - RENUMBERED)
  Purpose: Validate YAML structure and completeness
  Tasks: 5 tasks
  Gate: Definition validated and parsed

Phase 2: Workflow Scaffolding (CURRENT Phase 1 - RENUMBERED)
  Purpose: Create directory structure and metadata
  Tasks: 8 tasks
  Gate: Scaffolding verified

Phase 3: Core Files & Documentation (CURRENT Phase 2 - RENUMBERED)
  Purpose: Create supporting files and documentation
  Tasks: 4 tasks
  Gate: Core files created

Dynamic Phases: 4 to N+3 (CURRENT 3 to N+2 - MATH SHIFTED)
  Purpose: Generate target workflow phases
  Tasks: Variable (per target phase)
  Gate: Each target phase complete

Phase N+4: Meta-Workflow Compliance (CURRENT Phase N+3 - RENUMBERED)
  Purpose: Audit compliance with meta-workflow principles
  Tasks: 10 tasks
  Gate: 100% compliance achieved

Phase N+5: Testing & Delivery (CURRENT Phase N+4 - RENUMBERED)
  Purpose: Test, refine, obtain human approval
  Tasks: 8 tasks
  Gate: Human approval obtained
```

### Phase Number Changes Summary

| Component | Before | After | Change |
|-----------|--------|-------|--------|
| Total Static Phases | 5 | 6 | +1 |
| Definition Validation | Phase 0 | Phase 1 | +1 |
| Scaffolding | Phase 1 | Phase 2 | +1 |
| Core Files | Phase 2 | Phase 3 | +1 |
| Dynamic Phases Start | 3 | 4 | +1 |
| Dynamic Phases End | N+2 | N+3 | +1 |
| Compliance | N+3 | N+4 | +1 |
| Delivery | N+4 | N+5 | +1 |

---

## Phase 0 Design Specification

### Purpose

Accept design documents (markdown) or YAML definitions, convert design docs to standard YAML format, output validated definition path for Phase 1.

### Input Options

**Primary Path (90% usage):**
```python
start_workflow("workflow_creation_v1", target_name, {
    "design_document_path": ".agent-os/specs/design-spec.md"
})
```

**Expert Path (10% usage):**
```python
start_workflow("workflow_creation_v1", target_name, {
    "definition_path": "workflow-definition.yaml"
})
```

### Task Breakdown

**Task 1: Determine Input Type**
- Check workflow options for `design_document_path` or `definition_path`
- Error if neither provided
- Set `input_type` variable
- Expected: 2-3 minutes

**Task 2: Read Input Document**
- Read file from determined path
- Store raw content
- Verify file exists and readable
- Expected: 1-2 minutes

**Task 3: Extract from Design Document (Conditional)**
- Only executes if `input_type == "design_document"`
- Parse markdown structure
- Extract key sections (see extraction logic below)
- Expected: 5-10 minutes

**Task 4: Generate YAML Definition**
- Only executes if design doc provided
- Build YAML following workflow-definition-template.yaml structure
- Write to temporary file
- Expected: 5-10 minutes

**Task 5: Validate Generated Definition**
- Check YAML syntax valid
- Verify required fields present
- Confirm file readable by Phase 1
- Expected: 2-3 minutes

### Validation Gate Evidence

```yaml
evidence_required:
  input_type:
    type: string
    validator: non_empty
    description: "Type of input provided (design_document or yaml_definition)"
  
  input_document_read:
    type: boolean
    validator: is_true
    description: "Input document successfully read"
  
  design_document_converted:
    type: boolean
    validator: is_true
    description: "Design document converted to YAML (if applicable)"
  
  standard_definition_path:
    type: string
    validator: file_exists
    description: "Path to YAML definition file for Phase 1"
  
  yaml_syntax_valid:
    type: boolean
    validator: is_true
    description: "YAML syntax validated successfully"

human_approval_required: false
```

---

## Extraction Logic (Design Doc → YAML)

### Source Document Structure

**Expected Sections in design-spec.md:**

1. **Problem Statement** (lines ~40-73)
   - Contains: Current state, desired state, problems, benefits
   - Extract: problem.statement, problem.why_workflow

2. **Success Criteria** (lines ~19-23)
   - Contains: Measurable outcomes
   - Extract: problem.success_criteria (array)

3. **Requirements** (lines ~76-149)
   - FR1-FR6: Functional requirements
   - NFR1-NFR4: Non-functional requirements
   - Extract: Used to inform phase/task descriptions

4. **Phase Breakdown** (lines ~213-445)
   - Phase 0-5 with tasks and validation gates
   - Extract: phases array with all fields

5. **Validation Framework** (lines ~447-725)
   - Checkpoint validation structures
   - Extract: validation_gate evidence fields per phase

### Extraction Mapping

**Problem Section:**
```python
# Extract from "Problem Statement" section
problem = {
    "statement": extract_subsections([
        "Current State",
        "Desired State", 
        "Problems"
    ]),
    "why_workflow": extract_subsection("Why a Workflow?"),
    "success_criteria": extract_list("Success Criteria")
}
```

**Phases Section:**
```python
# Extract from "Phase Breakdown" section
for phase_section in ["Phase 0:", "Phase 1:", ...]:
    phase = {
        "number": extract_phase_number(phase_section),
        "name": extract_phase_name(phase_section),
        "purpose": extract_field("Goal:" or "Purpose:"),
        "deliverable": extract_field("Deliverable:" or "Expected Duration:"),
        "tasks": extract_tasks(phase_section),
        "validation_gate": extract_validation_gate(phase_section)
    }
```

**Task Extraction:**
```python
# From "Tasks:" subsection in each phase
task = {
    "number": task_number,
    "name": kebab_case(task_title),
    "purpose": task_description,
    "domain_focus": extract_if_present("domain:"),
    "commands_needed": infer_from_description(),
    "estimated_lines": 100  # default
}
```

**Validation Gate Extraction:**
```python
# From "Checkpoint Validation:" code blocks
validation_gate = {
    "evidence_required": {
        field_name: {
            "type": field_type,
            "description": field_desc,
            "validator": infer_validator(field_type)
        }
    },
    "human_approval_required": check_if_mentioned()
}
```

### YAML Template Structure

**Follow:** `universal/templates/workflow-definition-template.yaml`

**Required Fields:**
```yaml
name: "extracted-from-title"
version: "1.0.0"
workflow_type: "infer-from-content"
problem:
  statement: |
    [Extracted problem statement]
  why_workflow: "[Extracted justification]"
  success_criteria:
    - "[Criterion 1]"
    - "[Criterion 2]"
phases:
  - number: 0
    name: "[Phase Name]"
    purpose: "[Phase Purpose]"
    deliverable: "[Phase Deliverable]"
    tasks:
      - number: 1
        name: "[kebab-case-name]"
        purpose: "[Task purpose]"
    validation_gate:
      evidence_required:
        field_name:
          type: "string"
          description: "[Description]"
          validator: "non_empty"
      human_approval_required: false
```

### Inference Rules

**Workflow Type:**
- Contains "standard" or "documentation" → "documentation"
- Contains "test" or "testing" → "testing"
- Contains "implement" or "build" → "implementation"
- Contains "validate" or "check" → "validation"
- Default → "implementation"

**Validators:**
- boolean type → "is_true"
- integer type + "count" → "greater_than_0"
- integer type + "percent" → "percent_gte_80" (or 95/100 based on context)
- string type + "path" → "file_exists" or "directory_exists"
- string type → "non_empty"

**Domain Focus:**
- Look for "RAG", "semantic search" → domain_focus: "RAG Optimization"
- Look for "validation", "gate", "checkpoint" → domain_focus: "Validation Gates"
- Look for "command", "symbol" → domain_focus: "Command Language"

---

## Implementation Checklist

### ✅ Phase 1: Create New Phase 0 (30 minutes)

**Directory Setup:**
- [ ] Create `universal/workflows/workflow_creation_v1/phases/0-new/`

**Files to Create:**

- [ ] **phase.md** (~80 lines)
  - Purpose: Input Conversion & Preprocessing
  - Overview: Accept multiple formats, normalize to YAML
  - Task table (5 tasks)
  - Validation gate (see evidence above)
  - Navigation: Start → task-1, After complete → ../1/phase.md

- [ ] **task-1-determine-input-type.md** (~100 lines)
  - Check options.design_document_path
  - Check options.definition_path
  - Error if neither
  - Set input_type variable
  - Navigation: NEXT → task-2

- [ ] **task-2-read-input-document.md** (~100 lines)
  - Read file from path (design doc or YAML)
  - Store raw content
  - Verify readable
  - DISCOVER-TOOL: read_file
  - Navigation: NEXT → task-3

- [ ] **task-3-extract-from-design.md** (~100 lines)
  - Conditional: Only if input_type == "design_document"
  - MUST-SEARCH: "workflow definition structure phases tasks"
  - Parse markdown sections
  - Extract problem, phases, tasks, gates
  - Store structured data
  - Navigation: NEXT → task-4

- [ ] **task-4-generate-yaml-definition.md** (~100 lines)
  - Conditional: Only if design doc path
  - Read workflow-definition-template.yaml for structure
  - Build YAML from extracted data
  - Write to temp file (.agent-os/specs/generated-definition.yaml)
  - DISCOVER-TOOL: write file
  - Navigation: NEXT → task-5

- [ ] **task-5-validate-generated-definition.md** (~100 lines)
  - Check YAML syntax valid
  - Verify required fields present
  - Store definition_path for Phase 1
  - CONSTRAINT: Must pass validation
  - Navigation: NEXT → ../1/phase.md (Phase 1)

**Quality Checks:**
- [ ] All task files ≤100 lines
- [ ] Command language applied (≥80% coverage)
- [ ] Navigation links correct
- [ ] Validation gate complete
- [ ] MUST-SEARCH added where appropriate

---

### ✅ Phase 2: Renumber Existing Phases (5 minutes)

**Rename Commands:**
```bash
cd universal/workflows/workflow_creation_v1/phases/

# Rename in reverse order to avoid conflicts
mv 4/ 5/
mv 3/ 4/
mv 2/ 3/
mv 1/ 2/
mv 0/ 1/
mv 0-new/ 0/
```

**Verification:**
- [ ] phases/0/ exists (new phase)
- [ ] phases/1/ exists (was 0)
- [ ] phases/2/ exists (was 1)
- [ ] phases/3/ exists (was 2)
- [ ] phases/4/ exists (was 3, compliance)
- [ ] phases/5/ exists (was 4, delivery)
- [ ] phases/dynamic/ unchanged

---

### ✅ Phase 3: Update Metadata (5 minutes)

**File:** `universal/workflows/workflow_creation_v1/metadata.json`

**Changes:**
```json
{
  "total_phases": 6,  // WAS: 5
  "phases": [
    {
      "phase_number": 0,
      "phase_name": "Input Conversion & Preprocessing",  // NEW
      "tasks": [
        {"task_number": 1, "name": "determine-input-type", "file": "task-1-determine-input-type.md"},
        {"task_number": 2, "name": "read-input-document", "file": "task-2-read-input-document.md"},
        {"task_number": 3, "name": "extract-from-design", "file": "task-3-extract-from-design.md"},
        {"task_number": 4, "name": "generate-yaml-definition", "file": "task-4-generate-yaml-definition.md"},
        {"task_number": 5, "name": "validate-generated-definition", "file": "task-5-validate-generated-definition.md"}
      ]
    },
    {
      "phase_number": 1,  // WAS: 0
      "phase_name": "Definition Import & Validation",
      // ... existing tasks
    },
    {
      "phase_number": 2,  // WAS: 1
      "phase_name": "Workflow Scaffolding",
      // ... existing tasks
    },
    {
      "phase_number": 3,  // WAS: 2
      "phase_name": "Core Files & Documentation",
      // ... existing tasks
    },
    {
      "phase_number": 4,  // WAS: 3
      "phase_name": "Meta-Workflow Compliance",
      // ... existing tasks
    },
    {
      "phase_number": 5,  // WAS: 4
      "phase_name": "Testing & Delivery",
      // ... existing tasks
    }
  ]
}
```

**Checklist:**
- [ ] total_phases updated to 6
- [ ] New Phase 0 entry added
- [ ] All existing phases renumbered (+1)
- [ ] Phase 4 = Meta-Workflow Compliance (was 3)
- [ ] Phase 5 = Testing & Delivery (was 4)
- [ ] JSON syntax valid

---

### ✅ Phase 4: Update Dynamic Phase Logic (10 minutes)

**File:** `universal/workflows/workflow_creation_v1/phases/dynamic/phase-template.md`

**Find and Replace:**
```markdown
# OLD:
🎯 NEXT-MANDATORY: ../3/phase.md (proceed to Meta-Workflow Compliance)

# NEW:
🎯 NEXT-MANDATORY: ../4/phase.md (proceed to Meta-Workflow Compliance)
```

**Changes:**
- [ ] Line ~243: Update `../3/phase.md` → `../4/phase.md`
- [ ] Any "Phase N+3" text → "Phase N+4"
- [ ] Any "Phase N+2" text → "Phase N+3" (dynamic range end)

**File:** `universal/workflows/workflow_creation_v1/phases/dynamic/task-template.md`

**Changes:**
- [ ] Check for any phase number references
- [ ] Update if phase math used in templates

---

### ✅ Phase 5: Update Phase Internal Headers (15 minutes)

Each phase.md and task file has phase number in headers and metadata.

**Phase 1 (was Phase 0):**

Files to update:
- [ ] `phases/1/phase.md`
  - Header: "# Phase 1: Definition Import & Validation" (was Phase 0)
  - Purpose line: Update if mentions "Phase 0"
  - Navigation: "After Phase 1 Complete" → `../2/phase.md` (was ../1/)

- [ ] `phases/1/task-1-locate-definition.md`
  - Header: "**Phase**: 1 - Definition Import & Validation" (was 0)
  - Navigation: NEXT → task-2

- [ ] `phases/1/task-2-parse-definition.md`
  - Header: "**Phase**: 1" (was 0)

- [ ] `phases/1/task-3-validate-structure.md`
  - Header: "**Phase**: 1" (was 0)

- [ ] `phases/1/task-4-validate-completeness.md`
  - Header: "**Phase**: 1" (was 0)

- [ ] `phases/1/task-5-prepare-workspace.md`
  - Header: "**Phase**: 1" (was 0)
  - Navigation: NEXT → `../2/phase.md` (was ../1/)

**Phase 2 (was Phase 1):**

Files to update:
- [ ] `phases/2/phase.md`
  - Header: "# Phase 2: Workflow Scaffolding" (was Phase 1)
  - Navigation: After complete → `../3/phase.md` (was ../2/)

- [ ] All 8 task files in `phases/2/`
  - Header: "**Phase**: 2" (was 1)
  - Last task navigation: NEXT → `../3/phase.md`

**Phase 3 (was Phase 2):**

Files to update:
- [ ] `phases/3/phase.md`
  - Header: "# Phase 3: Core Files & Documentation" (was Phase 2)
  - Navigation: After complete → `../4/phase.md` (was ../3/)

- [ ] All 4 task files in `phases/3/`
  - Header: "**Phase**: 3" (was 2)
  - Last task navigation: NEXT → `../4/phase.md`

**Phase 4 (was Phase 3 - Compliance):**

Files to update:
- [ ] `phases/4/phase.md`
  - Header: "# Phase 4: Meta-Workflow Compliance" (was Phase 3)
  - Note: "Phase N+4" (was N+3)
  - Navigation: After complete → `../5/phase.md` (was ../4/)

- [ ] All 10 task files in `phases/4/`
  - Header: "**Phase**: 4" (was 3)
  - Last task navigation: NEXT → `../5/phase.md`

**Phase 5 (was Phase 4 - Delivery):**

Files to update:
- [ ] `phases/5/phase.md`
  - Header: "# Phase 5: Testing & Delivery" (was Phase 4)
  - Note: "Phase N+5" (was N+4)

- [ ] All 8 task files in `phases/5/`
  - Header: "**Phase**: 5" (was 4)

---

### ✅ Phase 6: Update Documentation (15 minutes)

**File:** `universal/workflows/workflow_creation_v1/supporting-docs/design-summary.md`

**Changes:**
```markdown
# OLD:
### Static Phases (5 Total)

**Phase 0: Definition Import & Validation** (5 tasks)
**Phase 1: Workflow Scaffolding** (7 tasks)
**Phase 2: Core Files & Documentation** (4 tasks)
**Phase N+3: Meta-Workflow Compliance** (10 tasks)
**Phase N+4: Testing & Delivery** (8 tasks)

### Dynamic Phases (3 to N+2)

# NEW:
### Static Phases (6 Total)

**Phase 0: Input Conversion & Preprocessing** (5 tasks)
**Phase 1: Definition Import & Validation** (5 tasks)
**Phase 2: Workflow Scaffolding** (8 tasks)
**Phase 3: Core Files & Documentation** (4 tasks)
**Phase N+4: Meta-Workflow Compliance** (10 tasks)
**Phase N+5: Testing & Delivery** (8 tasks)

### Dynamic Phases (4 to N+3)
```

**Checklist:**
- [ ] Update phase count: 5 → 6
- [ ] Add Phase 0 description
- [ ] Renumber all phases (+1)
- [ ] Update dynamic phase range: 3 to N+2 → 4 to N+3
- [ ] Update compliance: N+3 → N+4
- [ ] Update delivery: N+4 → N+5
- [ ] Update usage pattern example

**File:** `universal/workflows/workflow_creation_v1/core/compliance-audit-methodology.md`

**Changes:**
- [ ] Check for any "Phase 3" references (should be Phase 4)
- [ ] Check for any "Phase 4" references (should be Phase 5)
- [ ] Update if compliance phase number mentioned

**File:** `workflow-creation-v1-definition.yaml` (if exists in repo)

**Changes:**
- [ ] Update phase numbers
- [ ] Update total_phases
- [ ] Add Phase 0 definition

---

### ✅ Phase 7: Update Navigation Links (10 minutes)

**Search Patterns:**

```bash
# Find all navigation links to update
cd universal/workflows/workflow_creation_v1/

# Pattern 1: Direct phase references
grep -r "\.\.\/0\/phase\.md" phases/
grep -r "\.\.\/1\/phase\.md" phases/
grep -r "\.\.\/2\/phase\.md" phases/
grep -r "\.\.\/3\/phase\.md" phases/
grep -r "\.\.\/4\/phase\.md" phases/

# Pattern 2: Phase N references
grep -r "Phase N+3" phases/ supporting-docs/ core/
grep -r "Phase N+4" phases/ supporting-docs/ core/
```

**Replacements:**

| Old Pattern | New Pattern | Where |
|-------------|-------------|-------|
| `../0/phase.md` | `../1/phase.md` | Phase 2, 3, 4, 5 task files |
| `../1/phase.md` | `../2/phase.md` | Phase 3, 4, 5 task files |
| `../2/phase.md` | `../3/phase.md` | Phase 4, 5 task files |
| `../3/phase.md` | `../4/phase.md` | Phase 5 task files, dynamic template |
| `../4/phase.md` | `../5/phase.md` | Dynamic template (if completed) |
| `Phase N+3` | `Phase N+4` | All documentation (compliance) |
| `Phase N+4` | `Phase N+5` | All documentation (delivery) |
| `3 to N+2` | `4 to N+3` | design-summary.md (dynamic range) |

**Verification:**
- [ ] No broken navigation links
- [ ] Phase 0 → Phase 1 navigation works
- [ ] Phase 1 → Phase 2 navigation works
- [ ] Phase 2 → Phase 3 navigation works
- [ ] Phase 3 → Phase 4 navigation works
- [ ] Phase 4 → Phase 5 navigation works
- [ ] Dynamic phases → Phase 4 navigation works

---

### ✅ Phase 8: Verification (15 minutes)

**Structural Verification:**
- [ ] Directory `phases/0/` exists with 5 task files
- [ ] Directory `phases/1/` exists (was 0)
- [ ] Directory `phases/2/` exists (was 1)
- [ ] Directory `phases/3/` exists (was 2)
- [ ] Directory `phases/4/` exists (was 3)
- [ ] Directory `phases/5/` exists (was 4)
- [ ] Directory `phases/dynamic/` unchanged
- [ ] No leftover `phases/0-new/` directory

**Metadata Verification:**
- [ ] metadata.json: `total_phases` = 6
- [ ] metadata.json: Phase 0 entry exists
- [ ] metadata.json: Phase 4 name = "Meta-Workflow Compliance"
- [ ] metadata.json: Phase 5 name = "Testing & Delivery"

**Content Verification:**
- [ ] Read `phases/0/phase.md` - should be "Input Conversion"
- [ ] Read `phases/1/phase.md` - should be "Definition Import"
- [ ] Read `phases/4/phase.md` - should be "Meta-Workflow Compliance"
- [ ] Read `phases/5/phase.md` - should be "Testing & Delivery"

**Navigation Verification:**
- [ ] `phases/0/task-5-*.md` → `../1/phase.md` (Phase 1)
- [ ] `phases/1/task-5-*.md` → `../2/phase.md` (Phase 2)
- [ ] `phases/2/task-8-*.md` → `../3/phase.md` (Phase 3)
- [ ] `phases/3/task-4-*.md` → `../4/phase.md` (Phase 4)
- [ ] `phases/dynamic/phase-template.md` → `../4/phase.md` (Compliance)

**Phase Number Verification:**
- [ ] No references to "Phase 0: Definition Import" (should be Phase 1)
- [ ] No references to "Phase N+3: Meta-Workflow Compliance" (should be N+4)
- [ ] No references to "Phase N+4: Testing" (should be N+5)
- [ ] No broken "../3/phase.md" links (should be ../4/)

**Documentation Verification:**
- [ ] `design-summary.md` shows 6 static phases
- [ ] `design-summary.md` shows "4 to N+3" for dynamic range
- [ ] `design-summary.md` shows Phase N+4 = Compliance
- [ ] `design-summary.md` shows Phase N+5 = Delivery

**File Count Verification:**
```bash
# Should show:
# phases/0: 1 phase.md + 5 tasks = 6 files
# phases/1: 1 phase.md + 5 tasks = 6 files
# phases/2: 1 phase.md + 8 tasks = 9 files
# phases/3: 1 phase.md + 4 tasks = 5 files
# phases/4: 1 phase.md + 10 tasks = 11 files
# phases/5: 1 phase.md + 8 tasks = 9 files

find phases/ -name "*.md" | wc -l  # Should be 46 (was 40)
```

---

## Key Patterns Reference

### Find/Replace Patterns

**Phase Header Updates:**
```bash
# Phase 0 → Phase 1
find phases/1/ -name "*.md" -exec sed -i '' 's/\*\*Phase\*\*: 0/\*\*Phase\*\*: 1/g' {} \;
find phases/1/ -name "*.md" -exec sed -i '' 's/# Phase 0:/# Phase 1:/g' {} \;

# Phase 1 → Phase 2
find phases/2/ -name "*.md" -exec sed -i '' 's/\*\*Phase\*\*: 1/\*\*Phase\*\*: 2/g' {} \;
find phases/2/ -name "*.md" -exec sed -i '' 's/# Phase 1:/# Phase 2:/g' {} \;

# Phase 2 → Phase 3
find phases/3/ -name "*.md" -exec sed -i '' 's/\*\*Phase\*\*: 2/\*\*Phase\*\*: 3/g' {} \;
find phases/3/ -name "*.md" -exec sed -i '' 's/# Phase 2:/# Phase 3:/g' {} \;

# Phase 3 → Phase 4
find phases/4/ -name "*.md" -exec sed -i '' 's/\*\*Phase\*\*: 3/\*\*Phase\*\*: 4/g' {} \;
find phases/4/ -name "*.md" -exec sed -i '' 's/# Phase 3:/# Phase 4:/g' {} \;

# Phase 4 → Phase 5
find phases/5/ -name "*.md" -exec sed -i '' 's/\*\*Phase\*\*: 4/\*\*Phase\*\*: 5/g' {} \;
find phases/5/ -name "*.md" -exec sed -i '' 's/# Phase 4:/# Phase 5:/g' {} \;
```

**Navigation Link Updates:**
```bash
# Update navigation links
find phases/ -name "*.md" -exec sed -i '' 's|../0/phase\.md|../1/phase.md|g' {} \;
find phases/ -name "*.md" -exec sed -i '' 's|../1/phase\.md|../2/phase.md|g' {} \;
find phases/ -name "*.md" -exec sed -i '' 's|../2/phase\.md|../3/phase.md|g' {} \;
find phases/ -name "*.md" -exec sed -i '' 's|../3/phase\.md|../4/phase.md|g' {} \;
find phases/ -name "*.md" -exec sed -i '' 's|../4/phase\.md|../5/phase.md|g' {} \;
```

**Note:** These sed commands are for reference. Recommend using `search_replace` tool for precision.

---

## Success Criteria

Upon completion, the workflow must:

✅ **Accept Design Documents as Primary Input**
- Can process `.agent-os/specs/design-spec.md` (markdown)
- Extracts problem, phases, tasks, validation gates
- Generates valid YAML definition

✅ **Maintain Backward Compatibility**
- Can still accept YAML definition files (expert mode)
- Phase 1-5 function identically to before (just renumbered)

✅ **Preserve All Functionality**
- Dynamic phase system works (4 to N+3)
- Compliance audit works (Phase N+4)
- Human approval works (Phase N+5)
- All validation gates function

✅ **Maintain Quality Standards**
- All task files ≤100 lines
- Command coverage ≥80%
- Navigation links correct
- Validation gates parseable

✅ **Complete Documentation**
- design-summary.md updated
- metadata.json accurate
- All phase numbers consistent

---

## Testing Plan

### Test Case 1: Design Document Input (Primary Path)

```python
# Start workflow with design document
start_workflow("workflow_creation_v1", 
               "standards-creation-v1",
               {
                   "design_document_path": ".agent-os/specs/design-spec.md"
               })

# Expected:
# - Phase 0 executes
# - design-spec.md read
# - YAML generated
# - Phase 1 receives valid YAML
# - Workflow continues normally
```

**Verification:**
- [ ] Phase 0 completes successfully
- [ ] Generated YAML exists
- [ ] Generated YAML valid structure
- [ ] Phase 1 can parse it
- [ ] Workflow proceeds to scaffolding

### Test Case 2: YAML Definition Input (Expert Path)

```python
# Start workflow with pre-built YAML
start_workflow("workflow_creation_v1",
               "test-workflow-v1", 
               {
                   "definition_path": "test-definition.yaml"
               })

# Expected:
# - Phase 0 recognizes YAML path
# - Skips conversion
# - Passes to Phase 1
# - Workflow continues normally
```

**Verification:**
- [ ] Phase 0 detects YAML input
- [ ] No conversion attempted
- [ ] Phase 1 receives path
- [ ] Workflow proceeds normally

### Test Case 3: Error Handling

```python
# Start workflow with neither input
start_workflow("workflow_creation_v1",
               "test-workflow-v1",
               {})

# Expected:
# - Phase 0 Task 1 detects missing input
# - Error thrown with clear message
# - Workflow stops
```

**Verification:**
- [ ] Error thrown
- [ ] Clear error message
- [ ] Suggests providing either path

---

## Rollback Plan

If implementation fails or issues discovered:

### Option 1: Quick Revert
```bash
cd universal/workflows/workflow_creation_v1/phases/

# Revert directory changes
rm -rf 0/
mv 1/ 0/
mv 2/ 1/
mv 3/ 2/
mv 4/ 3/
mv 5/ 4/

# Revert metadata.json from git
git checkout metadata.json

# Revert documentation
git checkout supporting-docs/design-summary.md
```

### Option 2: Git Reset
```bash
# If committed, reset to before changes
git log --oneline  # Find commit before changes
git reset --hard <commit-hash>
```

---

## Post-Implementation

### Update Analysis Document

After successful implementation, update:
- `.agent-os/specs/workflow-creation-v1-analysis-2025-10-13.md`
- Mark Gap #1 as RESOLVED
- Add note about Phase 0 insertion

### Update This Document

Mark this implementation guide as:
- Status: COMPLETE
- Implementation Date: [date]
- Verification: PASSED

### Create Usage Example

Document first successful use:
```markdown
# First Use: standards_creation_v1

Input: .agent-os/specs/design-spec.md (1622 lines)
Command: start_workflow("workflow_creation_v1", 
                        "standards-creation-v1",
                        {"design_document_path": "..."})

Result:
- Phase 0: Converted design doc → YAML (12 min)
- Phase 1-5: Standard workflow execution
- Output: universal/workflows/standards_creation_v1/
- Total Time: 85 minutes
- Quality: 100% compliant
```

---

## Notes & Context

### Design Document Format Assumptions

This implementation assumes design documents follow the format of:
- `.agent-os/specs/design-spec.md` (Standards Creation Workflow spec)
- Output from `spec_creation_v1` workflow

**Key sections expected:**
- Problem Statement
- Success Criteria
- Requirements (FR/NFR)
- Phase Breakdown
- Validation Framework

If future design docs have different structures, Phase 0 extraction logic may need adjustment.

### Extensibility

Phase 0 is designed to be extensible for future input formats:

**Current Support:**
- Markdown design documents
- YAML definitions

**Future Additions (to Phase 0 only):**
- PDF design documents
- Notion pages
- Confluence documentation
- Google Docs
- Multiple markdown files

Add new tasks to Phase 0 without affecting Phases 1-5.

---

## Completion Checklist

- [ ] All 8 implementation phases complete
- [ ] All verification checks passed
- [ ] Test Case 1 (design doc) successful
- [ ] Test Case 2 (YAML) successful  
- [ ] Test Case 3 (error) successful
- [ ] Documentation updated
- [ ] Analysis document updated
- [ ] Implementation guide marked complete

---

**END OF IMPLEMENTATION GUIDE**

