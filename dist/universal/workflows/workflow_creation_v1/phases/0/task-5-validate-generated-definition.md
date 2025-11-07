# Task 5: Validate Generated Definition

**Phase**: 0 - Input Conversion & Preprocessing  
**Purpose**: Verify YAML definition is well-formed and ready for Phase 1  
**Depends On**: Task 4 (standard_definition_path)  
**Feeds Into**: Phase 1 (Definition Import & Validation)

---

## Objective

Verify the YAML definition (whether generated from design doc or provided directly) has valid syntax and can be parsed successfully before passing to Phase 1.

---

## Context

📊 **CONTEXT**: This is a quick validation to ensure Phase 1 will receive a valid YAML file. Full structural validation happens in Phase 1. This task only checks YAML syntax and basic readability.

---

## Instructions

### Step 1: Read Definition File

Read the YAML file at `standard_definition_path`:

📖 **DISCOVER-TOOL**: Read file contents

This works for both:
- Generated YAML (from Task 4)
- Direct YAML input (from user)

### Step 2: Parse YAML Syntax

Attempt to parse the file as YAML:

```python
try:
    yaml_content = parse_yaml(definition_content)
    yaml_syntax_valid = True
except YAMLParseError as e:
    yaml_syntax_valid = False
    error_message = str(e)
```

⚠️ **CONSTRAINT**: If YAML parsing fails, this is a fatal error:

```
Error: Invalid YAML syntax

File: {standard_definition_path}
Error: {error_message}

{if yaml_generated}
This was generated from a design document. The extraction or
generation logic may need adjustment. Please review the generated
YAML file and correct any syntax errors.
{else}
The provided YAML definition has syntax errors. Please fix the
YAML syntax and try again.
{end}
```

🚨 **CRITICAL**: STOP if YAML invalid. Cannot proceed to Phase 1.

### Step 3: Check Top-Level Keys

Verify basic top-level keys exist (Phase 1 will do deeper validation):

Required keys:
- `name`
- `version`
- `workflow_type`
- `problem`
- `phases`

If any missing:
```
Warning: Definition may be incomplete

Missing required keys: {missing_keys}

Phase 1 will perform full validation and may fail if required
fields are missing. Consider reviewing the definition.
```

This is a warning, not an error. Let Phase 1 handle complete validation.

### Step 4: Record Validation Success

Store validation results:
- `yaml_syntax_valid`: True
- `definition_ready_for_phase1`: True

### Step 5: Verify Phase 0 Complete

Confirm all Phase 0 tasks are complete:
- ✅ Input validated and document read
- ✅ Design document converted to YAML (if applicable)
- ✅ Standard definition generated at correct path
- ✅ YAML syntax validated and parseable

Phase 0 is ready for checkpoint submission.

---

## Expected Output

**Variables to Capture**:
- `yaml_syntax_valid`: Boolean (True)
- `definition_ready_for_phase1`: Boolean (True)
- `top_level_keys_found`: Array (list of keys present)

---

## Quality Checks

✅ YAML syntax valid  
✅ File parseable  
✅ Basic structure present  
✅ Ready for Phase 1

---

## Checkpoint Submission

After this task completes, Phase 0 is ready for validation. This phase is complete when:
- ✅ Input type identified and document read
- ✅ Design document converted to standard YAML definition (if applicable)
- ✅ Definition file generated at correct path
- ✅ YAML syntax validated and parseable
- ✅ Ready for Phase 1 comprehensive validation

Submit checkpoint evidence to advance to Phase 1.

---

## Navigation

🎯 **NEXT-MANDATORY**: ../1/phase.md (begin Phase 1 after checkpoint passes)

↩️ **RETURN-TO**: phase.md (after task complete, for checkpoint submission)

