# Gate Definition YAML - Checkpoint Validation Reference

**Standard for creating gate-definition.yaml files that define checkpoint requirements for phase validation.**

---

## 🎯 TL;DR - Gate Definition YAML Quick Reference

**Keywords for search**: gate-definition.yaml, checkpoint validation YAML structure, evidence schema definition, validator lambda functions, three-tier fallback strategy, YAML validation gates, phase checkpoint requirements, strict mode lenient mode gates, evidence field types, checkpoint gate structure, validator patterns safe execution, gate YAML examples, workflow phase gates, validation gate syntax, checkpoint evidence requirements

**Core Principle:** gate-definition.yaml files define explicit, machine-readable validation requirements that enable systematic checkpoint enforcement through the three-tier fallback strategy (YAML → RAG → Permissive).

**Three-Tier Fallback Strategy:**
1. **YAML gates** (gate-definition.yaml) - Explicit, precise requirements (this document, highest priority)
2. **RAG parsing** - Dynamic extraction from phase.md markdown (automatic fallback)
3. **Permissive gate** - Always-pass backwards compatibility (final safety net)

**File Location Pattern:**
```
.agent-os/workflows/{workflow_type}/phases/{phase_number}/gate-definition.yaml
```

**Complete Gate Structure:**
```yaml
# Checkpoint behavior control
checkpoint:
  strict: false              # false=warnings, true=errors block
  allow_override: true       # Manual override allowed?
  
# Evidence field definitions
evidence_schema:
  field_name:
    type: boolean            # boolean|integer|string|list|dict
    required: true           # Must be present in evidence?
    description: "What this validates"
    validator: validator_ref # Optional: validator function name
    
# Reusable validator functions
validators:
  validator_name: "lambda x: x > 0"  # Safe lambda expressions
```

**Common Validator Patterns:**
```yaml
validators:
  positive: "lambda x: x > 0"
  non_empty: "lambda x: len(x) > 0"  
  valid_path: "lambda x: '/' in x and not x.startswith('..')"
  percentage: "lambda x: 0 <= x <= 100"
  in_range: "lambda x, min_val, max_val: min_val <= x <= max_val"
```

**When to Use Strict vs Lenient:**
- ✅ **Strict** (true): Phases 2+, critical workflows, production deployments
- ✅ **Lenient** (false): Phases 0-1, learning/onboarding, experimental workflows

**Quick Validation Checklist:**
- [ ] checkpoint section present with strict and allow_override
- [ ] evidence_schema with >= 1 field defined
- [ ] All fields have type, required, description
- [ ] Validators defined if any field references them
- [ ] Valid YAML syntax (no tabs, proper indentation)
- [ ] Field names use snake_case convention
- [ ] Descriptions are clear and specific

**Common Anti-Patterns:**
- ❌ Missing descriptions (agents don't know what to provide)
- ❌ Strict mode in Phase 0-1 (blocks learning)
- ❌ No validators for complex types (integers, lists need validation)
- ❌ Generic field names like "data" or "result" (use specific names)
- ❌ Validators with dangerous operations (os, sys, exec, eval)

**When to Query This Standard:**
- Creating new workflow with validation → `search_standards("how to create gate-definition.yaml")`
- Understanding checkpoint validation → `search_standards("checkpoint validation YAML structure")`
- Writing validator functions → `search_standards("validator lambda patterns safe")`
- Debugging validation failures → `search_standards("gate-definition.yaml troubleshooting")`
- Migration to gates → `search_standards("add validation gates existing workflow")`

---

## ❓ Questions This Answers

1. "What is gate-definition.yaml?"
2. "How do I create a gate-definition.yaml file?"
3. "What fields are required in gate-definition.yaml?"
4. "What evidence field types are supported?"
5. "How do I write validator lambda functions?"
6. "When should I use strict mode vs lenient mode?"
7. "What is the three-tier fallback validation strategy?"
8. "How do validator functions execute safely?"
9. "What validator patterns are commonly used?"
10. "How do I validate integer fields with ranges?"
11. "When should allow_override be true vs false?"
12. "What are gate-definition.yaml anti-patterns?"
13. "How do I test gate-definition.yaml files?"
14. "Where do gate-definition.yaml files go in workflow directory?"
15. "How does CheckpointLoader parse YAML gates?"
16. "What happens when gate-definition.yaml is missing?"
17. "Can evidence fields be optional (required: false)?"
18. "How do parameterized validators work?"
19. "What's the difference between strict and lenient modes?"
20. "How do I migrate existing workflows to use validation gates?"
21. "What security restrictions apply to validator functions?"
22. "Can validators access external modules like os or sys?"
23. "How are validator errors handled during execution?"
24. "What type mapping exists between YAML and Python types?"

---

## 🎯 Purpose

Define the YAML structure, semantics, and best practices for gate-definition.yaml files that enable systematic, automated checkpoint validation in Agent OS workflows. These files are the first tier in the three-tier fallback validation strategy, providing explicit, machine-readable requirements that prevent phase advancement without proper evidence.

**Core Principle**: gate-definition.yaml files provide precise validation specifications that eliminate ambiguity, prevent gaming, and enforce quality systematically.

---

## Why Gate Definition Files Matter - The Problem

**Without gate-definition.yaml:**
- ❌ **Ambiguous requirements** - Agents guess what evidence to provide
- ❌ **Hardcoded validation** - All checkpoints pass (checkpoint_passed = True)
- ❌ **No enforcement** - Quality standards not systematically enforced
- ❌ **Gaming possible** - Agents provide fake evidence without verification
- ❌ **Maintenance burden** - Requirements scattered across documentation
- ❌ **No audit trail** - Can't prove compliance or track quality

**Example of the problem:**
```markdown
# phase.md validation gate
- [ ] All tasks complete
- [ ] Tests passing
- [ ] Code reviewed

# Agent submits:
{"done": true}  

# Result: Passes! But did they actually complete tasks? Run tests? Get review?
```

**Impact without gates:**
- Poor quality code advances through phases
- Missing critical artifacts (tests, documentation, reviews)
- Impossible to audit or measure compliance
- Technical debt accumulates unnoticed
- No systematic quality improvement

---

## What Is gate-definition.yaml Structure?

### What Are the Three Main Sections?

Every gate-definition.yaml has three sections:

**1. checkpoint** - Validation behavior metadata
**2. evidence_schema** - Field definitions with types and validators  
**3. validators** - Reusable lambda validation functions

**Minimal valid gate:**
```yaml
checkpoint:
  strict: false
  allow_override: true
  
evidence_schema:
  task_complete:
    type: boolean
    required: true
    description: "Task completion confirmation"
    
validators: {}
```

### What Is the checkpoint Section?

Controls how validation behaves when evidence fails checks.

**Required fields:**

**strict** (boolean):
- `false`: Validation errors become warnings (lenient mode)
  - Logs errors but allows phase advancement
  - Use for learning phases (0-1)
  - Use for subjective criteria
- `true`: Validation errors block advancement (strict mode)
  - Prevents phase progression until fixed
  - Use for phases 2+ with clear criteria
  - Use for critical workflows

**allow_override** (boolean):
- `true`: Human can manually override validation failures
  - Emergency escape hatch
  - Use for most workflows
- `false`: No override possible, must fix issues
  - Use for critical security/compliance workflows
  - Use sparingly

**Example strict configuration:**
```yaml
checkpoint:
  strict: true               # Errors block advancement
  allow_override: false      # No manual override
```

**Example lenient configuration:**
```yaml
checkpoint:
  strict: false              # Warnings only
  allow_override: true       # Allow override if needed
```

### What Is the evidence_schema Section?

Defines required evidence fields with validation rules.

**Field structure:**
```yaml
field_name:
  type: TYPE                 # boolean, integer, string, list, dict
  required: BOOLEAN          # true=must provide, false=optional
  description: "TEXT"        # What this field validates (clear, specific)
  validator: NAME            # Optional: validator function reference
```

**Type mapping (YAML string → Python type):**
- `boolean` → `bool` (True/False validation flags)
- `integer` → `int` (counts, scores, numeric metrics)
- `string` → `str` (paths, commit hashes, text)
- `list` → `list` (arrays of files, test names, etc.)
- `dict` → `dict` (structured objects, nested data)

**Complete example:**
```yaml
evidence_schema:
  tests_passing:
    type: integer
    required: true
    description: "Number of passing tests (must be > 0)"
    validator: positive
    
  commit_hash:
    type: string
    required: true
    description: "Git commit hash for this phase"
    validator: valid_git_hash
    
  files_created:
    type: list
    required: true
    description: "List of files created (must not be empty)"
    validator: non_empty
    
  validation_complete:
    type: boolean
    required: true
    description: "Manual validation completed flag"
    
  metadata:
    type: dict
    required: false
    description: "Optional metadata (not validated)"
```

### What Is the validators Section?

Defines reusable lambda functions for field validation.

**Structure:**
```yaml
validators:
  validator_name: "lambda expression"
```

**Rules for validator lambdas:**
- Must be valid Python lambda syntax
- Must return boolean (True=pass, False=fail)
- Can accept parameters beyond field value
- **MUST NOT** use dangerous operations (security restricted)

**Security restrictions (enforced by ValidatorExecutor):**
- ❌ NO os, sys, subprocess access
- ❌ NO open(), exec(), eval(), compile()
- ❌ NO __import__, __builtins__ access
- ❌ NO globals(), locals() introspection
- ✅ YES len(), str(), int(), isinstance()
- ✅ YES any(), all(), range()
- ✅ YES standard comparisons (>, <, ==, etc.)

**Common validator patterns:**
```yaml
validators:
  # Numeric validators
  positive: "lambda x: x > 0"
  non_negative: "lambda x: x >= 0"
  percentage: "lambda x: 0 <= x <= 100"
  in_range: "lambda x, min_val, max_val: min_val <= x <= max_val"
  
  # String validators
  non_empty: "lambda x: len(x) > 0"
  valid_path: "lambda x: '/' in x and not x.startswith('..')"
  alphanumeric: "lambda x: x.isalnum()"
  valid_git_hash: "lambda x: len(x) == 40 and all(c in '0123456789abcdef' for c in x)"
  
  # List validators
  non_empty_list: "lambda x: len(x) > 0"
  min_items: "lambda x, min_count: len(x) >= min_count"
  all_strings: "lambda x: all(isinstance(i, str) for i in x)"
  
  # Boolean validators
  is_true: "lambda x: x is True"
  is_false: "lambda x: x is False"
```

**Parameterized validators:**
```yaml
validators:
  in_range: "lambda x, min_val, max_val: min_val <= x <= max_val"
  
evidence_schema:
  test_coverage:
    type: integer
    required: true
    description: "Test coverage percentage (80-100)"
    validator: in_range
    validator_params:
      min_val: 80
      max_val: 100
```

---

## How Does the Three-Tier Fallback Work?

### What Is the Fallback Strategy?

CheckpointLoader tries three strategies in order:

**Tier 1: YAML Gate (Highest Priority)**
- Loads `phases/{N}/gate-definition.yaml`
- Explicit, precise requirements
- Fastest (cached after first load)
- **Recommended for all workflows**

**Tier 2: RAG Parsing (Automatic Fallback)**
- Queries RAG for phase.md validation section
- Extracts requirements from markdown
- Dynamic, no manual file needed
- **Automatic backwards compatibility**

**Tier 3: Permissive Gate (Final Safety)**
- Always returns empty requirements
- All evidence passes validation
- Prevents breaking existing workflows
- **Never blocks progress**

**Example flow:**
```python
# Agent completes Phase 2
checkpoint_loader.load_requirements("my_workflow", 2)

# Try Tier 1: YAML
if exists(".agent-os/workflows/my_workflow/phases/2/gate-definition.yaml"):
    return parse_yaml_gate()  # ✅ Found! Use explicit requirements
    
# Try Tier 2: RAG
rag_results = rag_engine.search("my_workflow phase 2 validation")
if rag_results.has_checkpoints():
    return parse_rag_requirements()  # ✅ Found in docs
    
# Tier 3: Permissive
return {}  # ✅ Allow advancement (backwards compatible)
```

---

## When Should I Use Strict Mode vs Lenient Mode?

### What Is Strict Mode?

**strict: true**
- Validation errors **block** phase advancement
- Agent must fix issues before proceeding
- Enforces quality gates systematically

**When to use strict mode:**
- ✅ Phases 2+ (after initial onboarding)
- ✅ Clear, objective criteria (test counts, file existence)
- ✅ Critical workflows (security, production)
- ✅ Well-defined requirements (no ambiguity)

**Example strict gate:**
```yaml
checkpoint:
  strict: true
  allow_override: false  # Must fix, no override
  
evidence_schema:
  tests_passing:
    type: integer
    required: true
    description: "All tests must pass"
    validator: "lambda x: x > 0"
    
  files_created:
    type: list
    required: true
    description: "Required files must exist"
    validator: "lambda x: len(x) >= 3"
```

### What Is Lenient Mode?

**strict: false**
- Validation errors become **warnings**
- Agent can proceed despite issues
- Logs errors for visibility

**When to use lenient mode:**
- ✅ Phases 0-1 (learning, onboarding)
- ✅ Subjective criteria (code quality assessments)
- ✅ Experimental workflows (trying new approaches)
- ✅ Gradual adoption (introducing gates slowly)

**Example lenient gate:**
```yaml
checkpoint:
  strict: false
  allow_override: true  # Warnings only, override allowed
  
evidence_schema:
  code_reviewed:
    type: boolean
    required: true
    description: "Code review recommended (warning if false)"
```

---

## What Are Complete Gate Examples?

### Example 1: Phase 0 - Discovery (Lenient)

```yaml
checkpoint:
  strict: false              # Learning phase, warnings only
  allow_override: true
  
evidence_schema:
  requirements_understood:
    type: boolean
    required: true
    description: "Requirements and context understood"
    
  key_concepts_identified:
    type: list
    required: true
    description: "List of key concepts identified"
    validator: non_empty
    
  related_docs_reviewed:
    type: integer
    required: false
    description: "Number of related docs reviewed (optional)"
    
validators:
  non_empty: "lambda x: len(x) > 0"
```

### Example 2: Phase 2 - Implementation (Strict)

```yaml
checkpoint:
  strict: true               # Enforce quality
  allow_override: true       # Emergency override allowed
  
evidence_schema:
  files_created:
    type: list
    required: true
    description: "List of implementation files created"
    validator: non_empty_list
    
  tests_passing:
    type: integer
    required: true
    description: "Number of passing tests (must be > 0)"
    validator: positive
    
  test_coverage:
    type: integer
    required: true
    description: "Test coverage percentage (>= 80%)"
    validator: min_coverage
    
  commit_hash:
    type: string
    required: true
    description: "Git commit hash (40 char hex)"
    validator: valid_git_hash
    
  linting_passed:
    type: boolean
    required: true
    description: "Linting checks passed"
    
validators:
  non_empty_list: "lambda x: len(x) > 0"
  positive: "lambda x: x > 0"
  min_coverage: "lambda x: x >= 80"
  valid_git_hash: "lambda x: len(x) == 40 and all(c in '0123456789abcdef' for c in x)"
```

### Example 3: Phase 5 - Deployment (Critical, No Override)

```yaml
checkpoint:
  strict: true               # Critical phase
  allow_override: false      # NO override, must pass
  
evidence_schema:
  all_tests_passing:
    type: boolean
    required: true
    description: "All tests passing (no failures allowed)"
    validator: is_true
    
  security_scan_passed:
    type: boolean
    required: true
    description: "Security vulnerability scan passed"
    validator: is_true
    
  deployment_tested:
    type: boolean
    required: true
    description: "Deployment tested in staging environment"
    validator: is_true
    
  rollback_plan_exists:
    type: boolean
    required: true
    description: "Rollback plan documented and tested"
    validator: is_true
    
validators:
  is_true: "lambda x: x is True"
```

---

## What Are Gate Definition Anti-Patterns?

### Anti-Pattern 1: Missing Descriptions

**Wrong:**
```yaml
evidence_schema:
  data:
    type: dict
    required: true
    description: ""  # Empty! Agent doesn't know what to provide
```

**Right:**
```yaml
evidence_schema:
  test_results:
    type: dict
    required: true
    description: "Test execution results with pass/fail counts and durations"
```

**Why it matters:** Agents need clear guidance on what evidence to collect.

### Anti-Pattern 2: Strict Mode Too Early

**Wrong:**
```yaml
# Phase 0
checkpoint:
  strict: true  # Blocks learning! Agent can't explore
```

**Right:**
```yaml
# Phase 0  
checkpoint:
  strict: false  # Allow exploration and learning
  
# Phase 2+
checkpoint:
  strict: true  # Enforce quality after learning
```

**Why it matters:** Strict mode in early phases prevents agents from exploring and understanding requirements.

### Anti-Pattern 3: No Validators for Complex Types

**Wrong:**
```yaml
evidence_schema:
  test_count:
    type: integer
    required: true
    description: "Number of tests"
    # No validator! Could be 0 or negative!
```

**Right:**
```yaml
evidence_schema:
  test_count:
    type: integer
    required: true
    description: "Number of passing tests (must be > 0)"
    validator: positive
    
validators:
  positive: "lambda x: x > 0"
```

**Why it matters:** Without validators, invalid values pass validation.

### Anti-Pattern 4: Generic Field Names

**Wrong:**
```yaml
evidence_schema:
  data:      # What data?
    type: dict
  result:    # What result?
    type: boolean
  count:     # Count of what?
    type: integer
```

**Right:**
```yaml
evidence_schema:
  test_execution_results:
    type: dict
  all_tests_passed:
    type: boolean
  passing_test_count:
    type: integer
```

**Why it matters:** Specific names make requirements self-documenting.

### Anti-Pattern 5: Dangerous Validators

**Wrong:**
```yaml
validators:
  check_file: "lambda x: os.path.exists(x)"  # ❌ os module access!
  run_test: "lambda x: exec(x)"              # ❌ exec() forbidden!
```

**Right:**
```yaml
validators:
  non_empty_path: "lambda x: len(x) > 0 and '/' in x"
  valid_test_name: "lambda x: x.startswith('test_') and x.endswith('.py')"
```

**Why it matters:** Dangerous operations create security vulnerabilities.

---

## How Do I Test gate-definition.yaml Files?

### What Is the Testing Process?

**Step 1: Validate YAML Syntax**
```bash
python -c "import yaml; yaml.safe_load(open('gate-definition.yaml'))"
```

**Step 2: Test Validator Functions**
```python
# Test positive validator
validator = lambda x: x > 0
assert validator(5) == True
assert validator(0) == False
assert validator(-1) == False
```

**Step 3: Test with CheckpointLoader**
```python
from mcp_server.workflow_engine import CheckpointLoader

loader = CheckpointLoader(rag_engine)
requirements = loader.load_checkpoint_requirements("test_workflow", 2)

# Verify loaded correctly
assert "required_evidence" in requirements
assert "tests_passing" in requirements["required_evidence"]
```

**Step 4: Test Validation with Evidence**
```python
from mcp_server.workflow_engine import WorkflowEngine

engine = WorkflowEngine(state_manager, rag_engine)

# Test passing evidence
passed, missing = engine._validate_checkpoint(
    "test_workflow",
    2,
    {"tests_passing": 10, "files_created": ["a.py", "b.py"]}
)
assert passed == True

# Test failing evidence
passed, missing = engine._validate_checkpoint(
    "test_workflow", 
    2,
    {"tests_passing": 0}  # Missing files_created, tests_passing=0
)
assert passed == False
assert len(missing) > 0
```

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Creating gates** | `search_standards("how to create gate-definition.yaml")` |
| **Understanding structure** | `search_standards("gate-definition.yaml structure fields")` |
| **Validator patterns** | `search_standards("validator lambda patterns examples")` |
| **Strict vs lenient** | `search_standards("when to use strict mode gates")` |
| **Troubleshooting** | `search_standards("gate validation failing debug")` |
| **Migration** | `search_standards("add validation gates existing workflow")` |
| **Security** | `search_standards("validator security restrictions safe")` |
| **Three-tier fallback** | `search_standards("three-tier fallback validation strategy")` |

---

## 🔗 Related Standards

**Query workflow for validation mastery:**

1. **Start with gate structure** → `search_standards("gate-definition.yaml structure")` (this document)
2. **Learn validation system** → `search_standards("evidence validation system overview")` → `standards/validation/evidence-validation-overview.md`
3. **Understand CheckpointLoader** → `search_standards("CheckpointLoader three-tier fallback")` → `standards/validation/checkpoint-loader.md`
4. **Learn ValidatorExecutor** → `search_standards("safe validator execution security")` → `standards/validation/validator-executor.md`

**By Category:**

**Validation:**
- `standards/validation/evidence-validation-overview.md` - System overview → `search_standards("evidence validation system")`
- `standards/validation/checkpoint-loader.md` - Three-tier fallback → `search_standards("CheckpointLoader fallback")`
- `standards/validation/validator-executor.md` - Safe execution → `search_standards("validator execution security")`

**Workflows:**
- `standards/workflows/workflow-construction-standards.md` - Workflow structure → `search_standards("workflow construction standards")`
- `standards/workflows/workflow-metadata-standards.md` - Metadata format → `search_standards("workflow metadata")`

---

**Remember**: gate-definition.yaml files are the first line of defense in quality enforcement. They prevent poor quality code from advancing while maintaining backwards compatibility through the three-tier fallback strategy.
