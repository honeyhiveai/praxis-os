# Task 1: Create Workflow Directory

**Phase**: 2 - Workflow Scaffolding  
**Purpose**: Create universal/workflows/{name}/  
**Depends On**: Phase 0 (target_workflow_name, workflow_root_path)  
**Feeds Into**: Task 2 (Create Phase Directories)

---

## Objective

Create the root directory for the target workflow in the correct location within the prAxIs OS structure.

---

## Context

📊 **CONTEXT**: All workflows are stored in `universal/workflows/` following the prAxIs OS directory structure. The workflow name comes from Phase 0 Task 5 preparation.

---

## Instructions

### Step 1: Construct Directory Path

Use the `target_workflow_name` from Phase 0 to construct the full path:

```
universal/workflows/{target_workflow_name}/
```

Example: If `target_workflow_name` is `payment-processing-v1`, the path would be:
```
universal/workflows/payment-processing-v1/
```

⚠️ **CONSTRAINT**: The directory name MUST exactly match the `name` field from the workflow definition.

### Step 2: Check if Directory Already Exists

Before creating, verify the directory does not already exist.

📖 **DISCOVER-TOOL**: List directory contents to check existence

If the directory already exists:
- 🚨 **CRITICAL**: Determine if this is an overwrite scenario
- If not explicitly approved to overwrite, STOP and request guidance
- If approved, document that we're overwriting an existing workflow

### Step 3: Create Directory

Create the directory using the appropriate command.

📖 **DISCOVER-TOOL**: Create a directory at a specified path

Verify the command succeeded.

### Step 4: Verify Creation

Confirm the directory was created successfully.

📖 **DISCOVER-TOOL**: List directory contents to verify creation

Expected result: Directory exists and is empty (or only contains hidden files like .DS_Store).

---

## Expected Output

**Variables to Capture**:
- `workflow_directory_path`: String (absolute path to created directory)
- `directory_created`: Boolean (true if creation successful)
- `is_overwrite`: Boolean (true if overwriting existing)

---

## Quality Checks

✅ Directory path correctly constructed  
✅ Checked for existing directory  
✅ Directory created successfully  
✅ Creation verified  
✅ Path stored for subsequent tasks

---

## Navigation

🎯 **NEXT-MANDATORY**: task-2-create-phase-directories.md

↩️ **RETURN-TO**: phase.md (after task complete)

