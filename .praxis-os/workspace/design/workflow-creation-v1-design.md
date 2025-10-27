# Workflow Creation v1 - Complete Design Document

**Date**: 2025-10-13  
**Status**: Design Complete - Ready for Implementation  
**Type**: Core Workflow (universal/workflows/)

---

## Table of Contents

1. [Overview](#overview)
2. [Problem Statement](#problem-statement)
3. [Architecture](#architecture)
4. [Workflow Definition Format](#workflow-definition-format)
5. [Phase Structure](#phase-structure)
6. [Task Breakdown](#task-breakdown)
7. [Nested Workflow Support](#nested-workflow-support)
8. [Quality Standards](#quality-standards)
9. [Bootstrap Strategy](#bootstrap-strategy)
10. [Implementation Notes](#implementation-notes)
11. [Terminology](#terminology)

---

## Overview

`workflow_creation_v1` is a **meta-workflow** - a systematic process for creating other workflows. It consumes a structured workflow definition document (YAML) and generates a complete, meta-workflow-compliant workflow ready for use.

### Key Characteristics

- **Core Workflow**: Ships with Agent OS Enhanced to all consumers
- **Dynamic**: Uses template-based iteration for target workflow phases
- **Spec-Driven**: Requires workflow definition YAML as input
- **Bootstrap**: Hand-created once, then used for all future workflows
- **Self-Improving**: Can be used to refine itself (v1.1, v1.2, etc.)

### Success Criteria

- All target workflow phases fully populated (phase.md + all task files)
- 95%+ task files ≤100 lines (horizontal decomposition)
- 80%+ command language coverage (binding contract)
- 100% phases have validation gates
- 100% meta-workflow compliance
- Human approval obtained for final workflow

---

## Problem Statement

### The Problem

Creating high-quality workflows manually is:
- **Time-consuming**: 50-100+ task files to write
- **Inconsistent**: Easy to miss meta-workflow principles
- **Error-prone**: Validation gates might not be parseable by CheckpointLoader
- **Tedious**: Repetitive application of command language
- **Incomplete**: Domain expertise not systematically integrated

### Why a Workflow (vs Tool or Standard)

**Not a Tool**: Too complex, requires multiple phases with validation gates  
**Not a Standard**: Needs systematic execution, not just guidance  
**Needs Workflow**: Multi-phase process with quality checkpoints, domain expertise integration, and human review points

### What This Solves

- **Systematic Creation**: Step-by-step process ensures completeness
- **Quality Enforcement**: Validation gates ensure meta-workflow compliance
- **Consistency**: All workflows follow same patterns
- **Efficiency**: Automates repetitive work (command application, file creation)
- **Knowledge Integration**: Systematically searches standards for domain expertise
- **Scalability**: Enables rapid workflow development

---

## Architecture

### Three-Layer AI Guidance System

```
Layer 1: Standards (Teaching)
    ↓ search_standards() provides context
    ↓ Influences thinking, provides examples
    
Layer 2: Workflows (API for AI)
    ↓ Command language binds behavior
    ↓ Structured process with gates
    
Layer 3: Engine (Programmatic Gating)
    ↓ Phase boundaries enforced
    ↓ Evidence validation required
    ↓ Cannot skip or shortcut
```

### Component Interaction

```
Design Conversation
    ↓
working-docs/workflow-creation-v1-design.md (this document)
    ↓
workflow-creation-v1-definition.yaml (structured spec)
    ↓
start_workflow(
    workflow_type="workflow_creation_v1",
    options={"definition_path": "./definition.yaml"}
)
    ↓
universal/workflows/[target-workflow-name]/
    ├── metadata.json
    ├── core/
    │   ├── command-language-glossary.md
    │   └── progress-tracking.md
    ├── supporting-docs/
    │   ├── workflow-definition.yaml
    │   └── design-summary.md
    └── phases/
        ├── 0/phase.md + task files
        ├── 1/phase.md + task files
        └── ...
```

---

## Workflow Definition Format

### Discovery Pattern

1. Design conversation produces requirements
2. AI searches: `🔍 search_standards("workflow definition format template")`
3. Standard instructs: "List contents of universal/templates/ directory"
4. AI discovers: `workflow-definition-template.yaml`
5. AI reads complete template
6. AI fills based on conversation context
7. AI writes: `{workflow-name}-definition.yaml`
8. Definition consumed by `workflow_creation_v1`

### YAML Schema

**Required Foundation:**
```yaml
name: "workflow-name-v1"          # snake_case-v1 format
version: "1.0.0"                  # Semantic versioning
workflow_type: "implementation"   # Category

problem:
  statement: |
    [Multi-paragraph problem description]
  why_workflow: "[Why not tool/standard]"
  success_criteria:
    - "[Measurable criterion 1]"
    - "[Measurable criterion 2]"

phases:                           # Array of phase objects
  - number: 0
    name: "[Phase Name]"
    purpose: "[What this accomplishes]"
    deliverable: "[Concrete output]"
    tasks: [...]                  # Array of task objects
    validation_gate: {...}        # Evidence requirements
```

**Optional Extensions:**
```yaml
dynamic: true                     # Dynamic workflow flag
dynamic_config: {...}             # If dynamic: true
target_language: "python"         # Language-specific
tags: ["backend", "api"]          # Categorization
quality_standards: {...}          # Override defaults
```

**Task Object with Nested Workflow Support:**
```yaml
tasks:
  - number: 1
    name: "task-name"
    purpose: "[Purpose]"
    
    # Standard fields
    domain_focus: "[Domain]"
    commands_needed: ["write", "grep"]
    
    # NEW: Child workflow invocation
    invokes_workflow: "standards_creation_v1"
    invokes_workflow_options:
      target_file: "{{domain}}-patterns.md"
    invokes_workflow_required_evidence:
      - "session_id"
      - "completed"
      - "output_path"
```

### Template Location

**File**: `universal/templates/workflow-definition-template.yaml`  
**Size**: ~530 lines with extensive inline documentation  
**Discovery**: Via `list_dir("universal/templates/")`

---

## Phase Structure

### Overview

**Structure**: 4 static setup phases + N dynamic content phases + 2 static validation phases  
**Total Phases**: 6 + N (where N = number of target workflow phases)  
**Dynamic Behavior**: Template repeats once per target workflow phase

### Phase Flow Diagram

```
Phase 0: Definition Import (Static)
    ↓
Phase 1: Workflow Scaffolding (Static)
    ↓
Phase 2: Entry Point & Workflow Files (Static)
    ↓
Phase 3: Create Target Phase 0 (Dynamic - Iteration 1)
    ↓
Phase 4: Create Target Phase 1 (Dynamic - Iteration 2)
    ↓
    ... (Repeat for each target phase)
    ↓
Phase N+2: Create Target Phase N-1 (Dynamic - Iteration N)
    ↓
Phase N+3: Meta-Workflow Compliance (Static)
    ↓
Phase N+4: Testing & Delivery (Static - Human Approval)
```

---

## Task Breakdown

### Phase 0: Definition Import & Validation (STATIC)

**Purpose**: Load workflow definition, validate structure, prepare for creation  
**Deliverable**: Validated definition, parsed metadata, readiness confirmed  
**Tasks**: 5

1. **locate-definition** - Find workflow definition file via options.definition_path
2. **parse-definition** - Read YAML and parse structure
3. **validate-structure** - Check all required sections present
4. **validate-completeness** - Verify all phases have tasks and gates
5. **prepare-workspace** - Extract metadata, set up iteration variables

**Validation Gate:**
```yaml
evidence_required:
  definition_path:
    type: "string"
    description: "Path to workflow definition file"
    validator: "file_exists"
  definition_valid:
    type: "boolean"
    description: "All validation checks passed"
    validator: "is_true"
  total_target_phases:
    type: "integer"
    description: "Number of phases in target workflow"
    validator: "greater_than_0"
  total_target_tasks:
    type: "integer"
    description: "Total tasks across all target phases"
    validator: "greater_than_0"
human_approval_required: false
```

---

### Phase 1: Workflow Scaffolding (STATIC)

**Purpose**: Create directory structure and metadata.json  
**Deliverable**: Complete workflow directory with all phase folders  
**Tasks**: 7

1. **create-workflow-directory** - Create `universal/workflows/{name}/`
2. **create-phase-directories** - Create `phases/0/`, `phases/1/`, etc.
3. **create-core-directory** - Create `core/` for supporting files
4. **create-supporting-docs** - Create `supporting-docs/` for definition archive
5. **create-dynamic-directories** - If dynamic, create `phases/dynamic/`
6. **generate-metadata-json** - Generate metadata.json from definition
7. **verify-scaffolding** - Confirm all directories created correctly

**Validation Gate:**
```yaml
evidence_required:
  workflow_directory_path:
    type: "string"
    description: "Path to created workflow directory"
    validator: "directory_exists"
  phase_directories_count:
    type: "integer"
    description: "Number of phase directories created"
    validator: "greater_than_0"
  metadata_json_created:
    type: "boolean"
    description: "metadata.json file created and valid"
    validator: "is_true"
  scaffolding_verified:
    type: "boolean"
    description: "All directory structure verified"
    validator: "is_true"
human_approval_required: false
```

---

### Phase 2: Core Files & Documentation (STATIC)

**Purpose**: Create core supporting files, documentation, and archive definition  
**Deliverable**: Core files, supporting docs, and workflow documentation  
**Tasks**: 4

1. **create-command-glossary** - Document all command symbols in core/command-language-glossary.md
2. **create-progress-tracking** - Create progress table template in core/progress-tracking.md
3. **archive-definition** - Copy definition YAML to supporting-docs/workflow-definition.yaml
4. **generate-design-summary** - Create human-readable supporting-docs/design-summary.md

**Validation Gate:**
```yaml
evidence_required:
  command_glossary_created:
    type: "boolean"
    description: "Command glossary file created in core/"
    validator: "is_true"
  progress_tracking_created:
    type: "boolean"
    description: "Progress tracking file created in core/"
    validator: "is_true"
  definition_archived:
    type: "boolean"
    description: "Definition YAML archived in supporting-docs/"
    validator: "is_true"
  design_summary_created:
    type: "boolean"
    description: "Design summary markdown generated"
    validator: "is_true"
human_approval_required: false
```

**Task 3-4 Details: Archive Definition and Generate Summary**

**Task 3: archive-definition**
```markdown
🛑 EXECUTE-NOW: Archive workflow definition for reference

Copy the original definition YAML to workflow supporting-docs:
- Source: {definition_path} (from workflow options)
- Destination: {workflow_dir}/supporting-docs/workflow-definition.yaml

This preserves the source of truth for this workflow.

📊 Evidence:
- definition_path: supporting-docs/workflow-definition.yaml
- definition_archived: true
```

**Task 4: generate-design-summary**
```markdown
🛑 EXECUTE-NOW: Generate human-readable design summary

Create supporting-docs/design-summary.md with:

```markdown
# Workflow Design Summary: {name}

**Version**: {version}  
**Type**: {workflow_type}  
**Created**: {created}  
**Generated by**: workflow_creation_v1

## Problem Statement

{problem.statement}

## Why a Workflow?

{problem.why_workflow}

## Success Criteria

{for each criterion in problem.success_criteria}
- {criterion}

## Phases

| Phase | Name | Purpose | Deliverable | Tasks |
|-------|------|---------|-------------|-------|
{for each phase in phases}
| {phase.number} | {phase.name} | {phase.purpose} | {phase.deliverable} | {phase.tasks.length} |

## Quality Standards

{if quality_standards specified}
- Task file max lines: {quality_standards.task_file_max_lines}
- Command coverage: {quality_standards.command_coverage_min}%
- Validation gates: {quality_standards.validation_gate_required}
{else}
- Using default meta-workflow quality standards

## Notes

This workflow was created from a structured workflow definition.
See workflow-definition.yaml for complete machine-readable specification.
```

📊 Evidence:
- design_summary_path: supporting-docs/design-summary.md
- design_summary_created: true
```

---

### Phase 3 to N+2: Target Phase Content Creation (DYNAMIC - N ITERATIONS)

**Purpose**: Completely populate ONE target workflow phase  
**Deliverable**: One complete target phase (phase.md + all task files)  
**Tasks**: 12 per iteration

**THIS TEMPLATE EXECUTES N TIMES** (once per target workflow phase)

**Context Variables Available:**
- `target_phase_number` - Current phase being created (0 to N-1)
- `target_phase_name` - Name from definition
- `target_phase_purpose` - Purpose from definition
- `target_phase_deliverable` - Deliverable from definition
- `target_phase_tasks` - Array of task objects from definition
- `iteration_number` - Which iteration (1 to N)
- `total_iterations` - Total N phases

**Tasks:**

1. **load-target-phase-spec** - Extract this target phase from definition
2. **write-phase-file** - Create `phases/{N}/phase.md` (~80 lines)
3. **write-task-files** - Create ALL `task-{N}-{name}.md` files for this phase
4. **add-domain-expertise** - Search standards and integrate domain knowledge
5. **apply-command-language** - Convert to 80%+ command coverage
6. **add-validation-gates** - Add parseable gates to phase and tasks
7. **add-examples** - Include concrete examples throughout
8. **add-violation-warnings** - Add 🚨 WORKFLOW-VIOLATION warnings
9. **add-task-routing** - Add 🎯 NEXT-MANDATORY navigation between tasks
10. **validate-file-sizes** - Check phase.md ~80 lines, tasks ≤100 lines
11. **validate-command-coverage** - Count commands vs natural language
12. **collect-evidence** - Document completion metrics

**Special Handling for Child Workflows:**

If `task.invokes_workflow` is set, task file generation includes:
```markdown
🔍 MUST-SEARCH: "{task.invokes_workflow} workflow usage"

🛑 EXECUTE-NOW: Start child workflow

start_workflow(
    workflow_type="{task.invokes_workflow}",
    target_file="{task.invokes_workflow_options.target_file}",
    options={task.invokes_workflow_options}
)

Complete all phases of the child workflow before proceeding.

📊 Evidence required for THIS task:
{for each field in task.invokes_workflow_required_evidence}
- {field}: [value from child workflow]
```

**Validation Gate:**
```yaml
evidence_required:
  target_phase_number:
    type: "integer"
    description: "Phase number that was completed"
    validator: "greater_than_0"
  phase_file_created:
    type: "boolean"
    description: "phase.md file created"
    validator: "is_true"
  phase_file_line_count:
    type: "integer"
    description: "Lines in phase.md"
    validator: "between_60_100"
  task_files_count:
    type: "integer"
    description: "Number of task files created"
    validator: "greater_than_0"
  task_files_under_100_lines:
    type: "integer"
    description: "Count of task files ≤100 lines"
    validator: "greater_than_0"
  command_coverage_percent:
    type: "integer"
    description: "Percentage of instructions using commands"
    validator: "percent_gte_80"
  domain_expertise_integrated:
    type: "boolean"
    description: "Domain expertise added via search_standards"
    validator: "is_true"
human_approval_required: false
```

**After completing one target phase, template repeats for next phase until all N phases done.**

---

### Phase N+3: Meta-Workflow Compliance (STATIC)

**Purpose**: Validate entire workflow against all 5 meta-workflow principles  
**Deliverable**: Compliance report, all violations fixed  
**Tasks**: 10

1. **audit-file-sizes** - Check all task files across all phases
2. **audit-command-coverage** - Count command vs natural language usage
3. **verify-three-tier** - Validate tier separation (task ≤100, entry 200-500, outputs unrestricted)
4. **verify-validation-gates** - Check every phase has gate with parseable evidence
5. **verify-binding-contract** - Confirm contract in entry point with acknowledgment
6. **verify-horizontal-decomposition** - Check single responsibility per task
7. **generate-compliance-report** - Document all metrics and findings
8. **fix-violations** - Address any compliance failures (split files, add commands, etc.)
9. **re-validate** - Re-run all checks after fixes
10. **final-compliance-check** - Confirm 100% compliance achieved

**Validation Gate:**
```yaml
evidence_required:
  file_size_compliance_percent:
    type: "integer"
    description: "Percentage of task files ≤100 lines"
    validator: "percent_gte_95"
  command_coverage_percent:
    type: "integer"
    description: "Average command coverage across workflow"
    validator: "percent_gte_80"
  three_tier_validated:
    type: "boolean"
    description: "Three-tier architecture verified"
    validator: "is_true"
  gate_coverage_percent:
    type: "integer"
    description: "Percentage of phases with validation gates"
    validator: "percent_gte_100"
  binding_contract_present:
    type: "boolean"
    description: "Binding contract verified in entry point"
    validator: "is_true"
  violations_fixed:
    type: "boolean"
    description: "All violations resolved"
    validator: "is_true"
human_approval_required: false
```

---

### Phase N+4: Testing & Delivery (STATIC - HUMAN APPROVAL)

**Purpose**: Test workflow end-to-end, refine, obtain human approval  
**Deliverable**: Tested, refined, production-ready workflow  
**Tasks**: 8

1. **dry-run-navigation** - Test workflow navigation works (🎯 NEXT-MANDATORY links)
2. **validate-commands** - Ensure all commands are clear and properly formatted
3. **validate-gates-parseable** - Confirm gates use indicator keywords CheckpointLoader can parse
4. **identify-usability-issues** - Document friction points, unclear instructions
5. **implement-refinements** - Fix all identified issues
6. **create-usage-guide** - Write documentation on when/how to use workflow
7. **final-validation** - Re-run Phase N+3 compliance checks
8. **human-review** - Present to human for final approval

**Validation Gate:**
```yaml
evidence_required:
  dry_run_successful:
    type: "boolean"
    description: "Dry run completed without errors"
    validator: "is_true"
  usability_issues_count:
    type: "integer"
    description: "Number of usability issues found"
    validator: "greater_than_0"
  refinements_applied:
    type: "boolean"
    description: "All identified issues addressed"
    validator: "is_true"
  usage_guide_created:
    type: "boolean"
    description: "Usage guide written"
    validator: "is_true"
  final_compliance_passed:
    type: "boolean"
    description: "Final compliance check passed"
    validator: "is_true"
  human_approved:
    type: "boolean"
    description: "Human reviewed and approved for production"
    validator: "is_true"
human_approval_required: true
```

---

## Nested Workflow Support

### Problem

Target workflows might need to invoke child workflows (e.g., documenting patterns via `standards_creation_v1`).

### Solution

Use flexible evidence gating (already supported by engine) - no new engine features needed.

### How It Works

1. **Definition includes child workflow fields** in task object
2. **Task file generation** includes child workflow invocation instructions
3. **Evidence requirements** include proof of child completion
4. **Validation gate** enforces child workflow completion

### Definition Schema

```yaml
tasks:
  - number: 1
    name: "create-standards"
    purpose: "Document patterns"
    
    invokes_workflow: "standards_creation_v1"
    invokes_workflow_options:
      target_file: "{{domain}}-patterns.md"
    invokes_workflow_required_evidence:
      - "session_id"
      - "completed"
      - "output_path"
```

### Generated Task Content

```markdown
🔍 MUST-SEARCH: "standards_creation_v1 workflow usage"

🛑 EXECUTE-NOW: Start child workflow

start_workflow(
    workflow_type="standards_creation_v1",
    target_file="payment-processing-patterns.md",
    options={...}
)

📊 RECORD: standards_session_id = [returned session_id]

Complete ALL phases of standards creation workflow.

🚨 WORKFLOW-VIOLATION: Cannot proceed until child workflow complete

📊 Evidence required for THIS task:
- standards_session_id: [session ID from start_workflow]
- standards_completed: true
- standards_doc_path: [path to created standard]
```

### Evidence Validation

Task/phase validation gate includes child workflow evidence:
```yaml
validation_gate:
  evidence_required:
    standards_session_id:
      type: "string"
      description: "Session ID of completed standards workflow"
      validator: "non_empty"
    standards_completed:
      type: "boolean"
      description: "Standards workflow completed successfully"
      validator: "is_true"
    standards_doc_path:
      type: "string"
      description: "Path to created standards document"
      validator: "file_exists"
```

### Why This Works

✅ **No engine changes** - Uses existing evidence validation  
✅ **Flexible** - Any workflow can invoke any workflow  
✅ **Enforced** - Cannot pass gate without child completion  
✅ **Traceable** - Session IDs link parent to child  
✅ **Composable** - Unlimited nesting depth

---

## Quality Standards

### File Size Compliance

- **Task files**: 95%+ ≤100 lines (hard limit: 170 lines)
- **Phase files**: ~80 lines target
- **Entry point**: 200-500 lines
- **Enforcement**: Phase N+3 audits and requires fixes

### Command Language Coverage

- **Target**: 80%+ instructions use command symbols
- **Commands**: 🛑 EXECUTE-NOW, 🔍 MUST-SEARCH, 🎯 NEXT-MANDATORY, 📊 COUNT-AND-DOCUMENT, 🔄 UPDATE-TABLE, ⚠️ WARNING, 🚨 WORKFLOW-VIOLATION
- **Enforcement**: Phase N+3 counts and validates coverage

### Validation Gates

- **Coverage**: 100% of phases must have validation gates
- **Parseability**: Gates must use indicator keywords (must provide, required:, evidence:, checkpoint:, verify that, proof of)
- **Evidence fields**: All must have type, description, validator
- **Enforcement**: Phase N+3 verifies gate structure

### Three-Tier Architecture

- **Tier 1 (Execution)**: Task files ≤100 lines
- **Tier 2 (Methodology)**: Entry/phase files 200-500 lines
- **Tier 3 (Outputs)**: Unlimited, never re-read by workflow
- **Enforcement**: Phase N+3 validates tier separation

### Horizontal Decomposition

- **Single responsibility**: Each task file has one clear purpose
- **No duplication**: Domain expertise via 🔍 MUST-SEARCH, not copy-paste
- **Focused scope**: If task grows >100 lines, split into multiple tasks
- **Enforcement**: Phase N+3 reviews task purposes

---

## Bootstrap Strategy

### The Paradox

How do we create `workflow_creation_v1` when we need `workflow_creation_v1` to create workflows?

### Solution: Manual Bootstrap

**Step 1**: Hand-create `workflow_creation_v1` (one time only)
- Manually write all phase files
- Manually write all task files
- Manually create metadata.json
- Manually create entry point
- Location: `universal/workflows/workflow_creation_v1/`

**Step 2**: Test by creating another workflow
- Use it to create `standards_creation_v1` or similar
- Validate it works end-to-end
- Refine based on learnings

**Step 3**: Mark as core workflow
- Already in `universal/workflows/`
- Ships with Agent OS Enhanced
- Available to all consumers

**Step 4**: Self-improvement (optional)
- Use `workflow_creation_v1` to improve itself
- Create definition for v1.1 with improvements
- Run workflow to generate v1.1
- Replace v1.0 with v1.1

### Post-Bootstrap

After `workflow_creation_v1` exists:
- **Deprecate** `create_workflow` tool (no longer needed)
- **Use exclusively** for all new workflows
- **Iterate** on improvements via self-execution

---

## Implementation Notes

### File Locations

**Temporary (Design Phase):**
- `working-docs/workflow-creation-v1-design.md` - This document
- `./workflow-creation-v1-definition.yaml` - Structured spec (created from this design)

**Permanent (Core Workflow):**
- `universal/workflows/workflow_creation_v1/` - The actual workflow
- `universal/templates/workflow-definition-template.yaml` - Template for definitions
- `universal/standards/workflow-construction/workflow-definition-format.md` - Teaching standard

### Tool Usage

**Tools Used by This Workflow:**
- `search_standards` - Discover template, get domain expertise
- `list_dir` - Find template file
- `read_file` - Read definition, read template
- `write` - Create all workflow files
- `grep` - Validate content, count commands
- `run_terminal_cmd` - File operations (mkdir, wc -l, etc.)

**No New Tools Required** - All operations use existing tools

### Dynamic Template Variables

Variables available in `phases/dynamic/phase-template.md` and `phases/dynamic/task-template.md`:

```jinja2
{{ target_phase_number }}        # 0, 1, 2, ...
{{ target_phase_name }}          # From definition.phases[i].name
{{ target_phase_purpose }}       # From definition.phases[i].purpose
{{ target_phase_deliverable }}   # From definition.phases[i].deliverable
{{ target_phase_tasks }}         # Array of task objects
{{ iteration_number }}           # 1 to N
{{ total_iterations }}           # N
```

### Parser Requirements

Need to build `WorkflowDefinitionParser` class:
- Read YAML definition file
- Validate structure
- Extract metadata for templates
- Provide iteration context
- Similar to existing `SpecTasksParser` in `mcp_server/core/parsers.py`

### Metadata.json Configuration

```json
{
  "name": "workflow-creation-v1",
  "version": "1.0.0",
  "description": "Systematic workflow creation using meta-workflow principles",
  "workflow_type": "workflow_creation",
  "target_language": ["any"],
  "total_phases": "6 + N (dynamic)",
  "dynamic_phases": true,
  "dynamic_config": {
    "source_path_key": "definition_path",
    "source_type": "workflow_definition",
    "templates": {
      "phase": "phases/dynamic/phase-template.md",
      "task": "phases/dynamic/task-template.md"
    },
    "parser": "workflow_definition_parser",
    "iteration_variable": "target_phase"
  },
  "quality_gates": {
    "file_size_compliance": "95%+ ≤100 lines",
    "command_coverage": "80%+",
    "validation_gates": "100%",
    "meta_workflow_compliance": "100%"
  }
}
```

---

## Summary

### What This Workflow Does

1. Reads structured workflow definition (YAML)
2. Validates definition completeness
3. Creates directory structure and metadata
4. Generates core files and supporting documentation
5. Iterates through target phases, creating complete content
6. Integrates domain expertise via search
7. Applies command language systematically
8. Validates meta-workflow compliance
9. Tests and refines
10. Obtains human approval

### What Consumers Get

- **One workflow to rule them all**: Create any custom workflow
- **Quality enforced**: Meta-workflow compliance automatic
- **Knowledge integrated**: Domain expertise systematically added
- **Time saved**: Hours/days of manual work → automated systematic process
- **Consistency**: All workflows follow same high-quality patterns

### Total Scope

**Static Tasks**: 34 tasks (Phases 0, 1, 2, N+3, N+4)
  - Phase 0: 5 tasks
  - Phase 1: 7 tasks  
  - Phase 2: 4 tasks
  - Phase N+3: 10 tasks
  - Phase N+4: 8 tasks
  
**Dynamic Tasks**: 12 tasks × N iterations  
**Total**: 34 + (12 × N) tasks

**Example (N=5 target phases)**: 34 + 60 = 94 total tasks

---

## Next Steps

1. ✅ Design complete (this document)
2. ⏳ Write workflow definition YAML from this design
3. ⏳ Hand-create all workflow files (bootstrap)
4. ⏳ Test by creating another workflow
5. ⏳ Refine based on testing
6. ⏳ Mark as production-ready
7. ⏳ Deprecate `create_workflow` tool

---

---

## Terminology

### Terminology Note

**Important**: We use "workflow" consistently throughout Agent OS Enhanced.

**Workflow** (Instance):
- A specific structured process (e.g., `workflow_creation_v1`, `test-generation-js-ts-v1`)
- Lives in `universal/workflows/` (core) or `.praxis-os/workflows/` (custom)
- Created using `workflow_creation_v1`
- Example: "The payment-processing workflow has 5 phases"

**Meta-Workflow** (Universal Principles):
- The overarching system of principles for building workflows
- 5 core principles: LLM Constraint Awareness, Horizontal Decomposition, Command Language, Validation Gates, Evidence-Based Progress
- Documented in standards
- Example: "This workflow follows meta-workflow principles"

**Legacy "Framework" Usage**:
- Old documentation in `workflow-authoring/` uses "framework" terminology
- When updating documentation: "framework" → "workflow", "meta-framework" → "meta-workflow"
- All new content should use "workflow" terminology exclusively

### Key Terms

- **Target Workflow**: The workflow being created by `workflow_creation_v1`
- **Static Phase**: Fixed phase that executes once (e.g., Phase 0, 1, 2)
- **Dynamic Phase**: Template-based phase that iterates N times
- **Evidence**: Required proof for passing validation gates
- **Child Workflow**: A workflow invoked by a task within another workflow
- **Binding Contract**: MANDATORY acknowledgment that enforces compliance
- **Command Language**: Symbols (🛑 🔍 🎯 📊) that bind AI behavior
- **Horizontal Decomposition**: Breaking complex work into ≤100 line focused files
- **Three-Tier Architecture**: Organizing content by AI consumption pattern (≤100, 200-500, unlimited)

---

**Design Status**: COMPLETE AND READY FOR IMPLEMENTATION

**Design Date**: 2025-10-13  
**Design Version**: 1.0  
**Approved By**: [Pending]

