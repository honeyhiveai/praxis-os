# Task 6: Generate Metadata JSON

**Phase**: 1 - Workflow Scaffolding  
**Purpose**: Generate metadata.json from definition  
**Depends On**: All previous tasks, Phase 0 (definition data)  
**Feeds Into**: Task 7 (Verify Scaffolding)

---

## Objective

Generate the `metadata.json` file that describes the complete workflow structure, referencing all phases and tasks.

---

## Context

📊 **CONTEXT**: The `metadata.json` file is the master index for the workflow. It must include complete information about all phases, tasks, and configuration. The workflow engine uses this file to navigate and validate the workflow.

🔍 **MUST-SEARCH**: "metadata.json structure workflow engine requirements"

---

## Instructions

### Step 1: Construct Basic Metadata

From the workflow definition and Phase 0 preparation, build the top-level structure:

```json
{
  "name": "{target_workflow_name}",
  "version": "{target_workflow_version}",
  "description": "{from problem.statement}",
  "workflow_type": "{target_workflow_type}",
  "target_language": ["{language}"] or ["any"],
  "total_phases": {count},
  "dynamic_phases": true/false,
  "created": "YYYY-MM-DD",
  "updated": "YYYY-MM-DD"
}
```

⚠️ **CONSTRAINT**: Use today's date for both `created` and `updated` fields.

### Step 2: Add Dynamic Configuration (if applicable)

If `is_dynamic == true`, add the dynamic_config section:

```json
{
  ...
  "dynamic_config": {
    "source_path_key": "{from definition}",
    "source_type": "{from definition}",
    "templates": {
      "phase": "phases/dynamic/phase-template.md",
      "task": "phases/dynamic/task-template.md"
    },
    "parser": "{from definition or inferred}",
    "iteration_variable": "{from definition}"
  }
}
```

### Step 3: Build Phases Array

For each phase in `phases_to_create`, create a phase object:

```json
{
  "phase_number": 0,
  "phase_name": "Phase Name",
  "tasks": [
    {
      "task_number": 1,
      "name": "task-name-kebab-case",
      "file": "task-1-task-name-kebab-case.md"
    },
    ...
  ]
}
```

⚠️ **CONSTRAINT**: Task file names MUST follow the pattern: `task-{number}-{name}.md`

### Step 4: Add Quality Gates

Include quality standards from the definition:

```json
{
  ...
  "quality_gates": {
    "file_size_compliance": "95%+ ≤100 lines",
    "command_coverage": "80%+",
    "validation_gates": "100%",
    "meta_workflow_compliance": "100%"
  }
}
```

Use defaults if not specified in definition:
- `task_file_max_lines`: 100
- `command_coverage_min`: 80
- `validation_gate_required`: true

### Step 5: Write metadata.json File

Write the complete JSON structure to:

```
{workflow_directory_path}/metadata.json
```

📖 **DISCOVER-TOOL**: Write content to a file

Ensure proper JSON formatting:
- 2-space indentation
- Proper escaping of strings
- Valid JSON syntax

### Step 6: Validate JSON Structure

Read the file back and confirm it's valid JSON.

📖 **DISCOVER-TOOL**: Read file contents

Verify:
- File is valid JSON (parseable)
- All required fields present
- Phase count matches expected
- Task references are consistent

---

## Expected Output

**Variables to Capture**:
- `metadata_json_created`: Boolean (true if successful)
- `metadata_json_path`: String (path to file)
- `metadata_valid`: Boolean (true if JSON is valid)

---

## Quality Checks

✅ All metadata fields included  
✅ Dynamic config added if applicable  
✅ All phases referenced  
✅ All tasks referenced  
✅ Quality gates included  
✅ File written successfully  
✅ JSON structure validated  
✅ Proper formatting applied

---

## Navigation

🎯 **NEXT-MANDATORY**: task-7-verify-scaffolding.md

↩️ **RETURN-TO**: phase.md (after task complete)

