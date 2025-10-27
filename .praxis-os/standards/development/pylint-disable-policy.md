# Pylint Disable Policy

**Define when and how to use pylint disable pragmas, with strong preference for fixing code over suppressing warnings.**

---

## 🚨 TL;DR - Pylint Disable Policy Quick Reference

**Keywords for search**: pylint disable, pylint pragma, suppress warnings, code quality, pylint exceptions, global disable, per-file disable, inline disable, pyproject.toml disable, pylint policy, when to disable pylint, how to suppress pylint warnings

**Core Principle:** Fix the code, don't suppress the warning. Pylint warnings exist to catch real quality issues.

**Current Global Disables (pyproject.toml):**
```toml
disable = [
    "too-few-public-methods",  # Dataclasses and data models
    "import-error",            # Mypy and tests catch these
]
```

**Approval Required For:**
- ✅ New global disables in `pyproject.toml` (almost never acceptable)
- ✅ Per-file disables with detailed justification
- ❌ Inline `# pylint: disable` comments (strongly discouraged)

**Decision Tree:**
1. Can you refactor the code? → Do it
2. Is it a false positive? → Still try to refactor first
3. Is it intentional design? → Document with per-file disable + justification
4. Unsure? → Ask for review before suppressing

**Quality Target:** 10.0/10 for all new code

---

## ❓ Questions This Answers

1. "When can I use pylint disable?"
2. "How do I suppress a pylint warning?"
3. "What pylint disables are allowed globally?"
4. "Can I use inline pylint disable comments?"
5. "How do I get approval for a pylint disable?"
6. "What's the difference between global and per-file disables?"
7. "Why not just disable all warnings?"
8. "How to fix code instead of suppressing warnings?"
9. "What justification is needed for pylint disable?"
10. "Are there alternatives to disabling pylint warnings?"

---

## 🎯 Purpose

Maintain code quality by minimizing pylint warning suppressions. Establish clear policy for when warnings can be suppressed and require explicit justification for all exceptions.

---

## 🚨 The Problem - What Happens Without This Policy

**Without policy:**
```python
# Developer hits warning, takes easy route
def complex_function(a, b, c, d, e, f, g):  # pylint: disable=too-many-arguments
    var1 = ...  # pylint: disable=invalid-name
    var2 = ...  # pylint: disable=invalid-name
    # ... suppression proliferates
```

**Result:** Code quality degrades, warnings lose meaning, technical debt accumulates

**With policy:**
```python
# Developer refactors to fix root cause
def complex_function(config: FunctionConfig):
    prepared_data = _prepare_data(config)
    return _process_data(prepared_data)
```

**Result:** Better code, maintainable quality, meaningful warnings

---

## 📋 The Standard - Pylint Disable Rules

### Rule 1: Default Stance

**Fix the code, don't suppress the warning.**

Pylint warnings indicate real quality issues. Suppression should be rare and always justified.

### Rule 2: Global Disables (pyproject.toml)

**Only 2 global disables currently approved:**

```toml
[tool.pylint.messages_control]
disable = [
    "too-few-public-methods",  # Many dataclasses and simple classes
    "import-error",            # Handled by mypy and testing
]
```

**Adding new global disables requires:**
1. Team discussion
2. Documented decision in this file
3. Update to `pyproject.toml` with inline justification

**Rationale for current disables:**
- `too-few-public-methods`: Python dataclasses intentionally minimal
- `import-error`: False positives during development; mypy catches real issues

### Rule 3: Per-File Disables

**Allowed only with explicit, detailed justification at top of file.**

**Required format:**
```python
# pylint: disable=specific-warning-name
# Justification: Clear, specific reason why suppression is necessary
# and why the code cannot be refactored to avoid the warning.
# Must explain the trade-off and why this is the best solution.
```

**Examples of acceptable per-file disables:**

```python
# pylint: disable=too-many-lines
# Justification: WorkflowEngine is the core orchestration component with
# phase gating, checkpoints, validation, content rendering, and session 
# management (1270 lines). Splitting would fragment cohesive workflow logic.
# Alternative considered: Multiple files would break atomic workflow state.
```

```python
# pylint: disable=too-many-instance-attributes
# Justification: Data models (dataclasses) require many attributes to represent
# complete workflow state, metadata, and checkpoint information. This is by 
# design for comprehensive type-safe data structures per domain-driven design.
```

```python
# pylint: disable=broad-exception-caught
# Justification: Workflow engine must be robust - catches broad exceptions
# to provide graceful degradation and detailed error messages for AI agents.
# Specific exceptions re-raised after logging. Alternative (narrow catching)
# would miss edge cases and break workflow execution.
```

### Rule 4: Inline Disables

**STRONGLY DISCOURAGED. Almost never acceptable.**

Inline `# pylint: disable=...` comments are code smell indicators:
- Code has a quality issue
- We're hiding it instead of fixing it
- Technical debt accumulates silently

**The ONE exception - Protected access within same logical module:**

```python
# Accessing internal cache within the same module
if hasattr(wf_tools, "_workflow_metadata_cache"):
    wf_tools._workflow_metadata_cache.clear()  # pylint: disable=protected-access
```

**But even then:** Prefer refactoring to a public API.

### Rule 5: Approval Process

**Before using any per-file disable:**

1. **Try to fix the code first**
   - Refactor function into smaller pieces
   - Use better data structures
   - Simplify logic

2. **If truly unfixable**, document why
   - What refactoring was attempted?
   - Why didn't it work?
   - What's the trade-off?

3. **Get explicit approval**
   - Team discussion or PR review
   - Explain why this is best solution
   - Document decision

4. **Add detailed justification**
   - Multi-line comment explaining trade-off
   - Reference alternatives considered
   - Link to design decision if relevant

---

## ✅ Checklist - Before Disabling Any Warning

- [ ] Have I tried to refactor the code to fix the warning?
- [ ] Have I considered all alternatives (data structures, patterns)?
- [ ] Is this truly an intentional design decision (not laziness)?
- [ ] Have I written a detailed justification (not just "needed for X")?
- [ ] Have I explained WHY code can't be refactored?
- [ ] Have I documented alternatives considered?
- [ ] Have I gotten approval from team/reviewer?
- [ ] Is this the minimum scope disable (file vs global)?
- [ ] Will this make sense to someone reading it in 6 months?

---

## 🎓 Examples - How to Fix Instead of Suppress

### Example 1: Too Many Arguments

❌ **WRONG: Suppress the warning**
```python
def process_data(a, b, c, d, e, f, g, h):  # pylint: disable=too-many-arguments
    pass
```

✅ **CORRECT: Group related parameters**
```python
@dataclass
class ProcessConfig:
    input_data: str
    output_path: Path
    validation_rules: List[Rule]
    timeout_seconds: int

def process_data(config: ProcessConfig):
    pass
```

### Example 2: Too Many Local Variables

❌ **WRONG: Suppress the warning**
```python
def complex_function():  # pylint: disable=too-many-locals
    var1 = ...
    var2 = ...
    # ... 30 more variables
```

✅ **CORRECT: Extract helper functions**
```python
def complex_function():
    prepared_data = _prepare_data()
    validated_data = _validate_data(prepared_data)
    return _process_data(validated_data)

def _prepare_data():
    # Variables scoped to preparation
    pass

def _validate_data(data):
    # Variables scoped to validation
    pass
```

### Example 3: Unused Variable

❌ **WRONG: Suppress the warning**
```python
result = expensive_function()  # pylint: disable=unused-variable
# ... result never used
```

✅ **CORRECT: Remove unused code**
```python
# Don't capture if you don't need it
expensive_function()

# Or actually use it
result = expensive_function()
return result
```

### Example 4: Too Many Branches

❌ **WRONG: Suppress the warning**
```python
def handle_request(request_type):  # pylint: disable=too-many-branches
    if request_type == "A":
        ...
    elif request_type == "B":
        ...
    # ... 15 more branches
```

✅ **CORRECT: Use dispatch pattern**
```python
REQUEST_HANDLERS = {
    "A": handle_type_a,
    "B": handle_type_b,
    # ... handlers as functions
}

def handle_request(request_type):
    handler = REQUEST_HANDLERS.get(request_type, handle_unknown)
    return handler()
```

---

## ❌ Anti-Patterns - Common Mistakes

### Anti-Pattern 1: Suppressing Instead of Understanding

```python
# ❌ BAD: Suppress warning without understanding
result = func()  # pylint: disable=unused-variable

# ✅ GOOD: Understand why warning exists, fix root cause
# If result truly not needed:
func()  # Just call without capturing
```

### Anti-Pattern 2: Vague Justification

```python
# ❌ BAD: No real justification
# pylint: disable=too-many-arguments
# Justification: Needed for functionality

# ✅ GOOD: Detailed trade-off explanation
# pylint: disable=too-many-arguments  
# Justification: MCP tool registration requires 8 parameters to wire all
# tool groups (RAG, workflow, browser, generators, validators) with optional
# dependencies. Grouping into config object considered but rejected because:
# 1. Parameters have different lifecycles (some created early, some late)
# 2. Would require passing entire config through 5 layers (coupling)
# 3. MCP server interface expects flat parameters per FastMCP spec
```

### Anti-Pattern 3: Inline Disables Everywhere

```python
# ❌ BAD: Suppress at every occurrence
var1 = data  # pylint: disable=invalid-name
var2 = more  # pylint: disable=invalid-name
var3 = stuff  # pylint: disable=invalid-name

# ✅ GOOD: Fix the naming
input_data = data
processed_data = more
output_data = stuff
```

### Anti-Pattern 4: Global Disable for Convenience

```toml
# ❌ BAD: Disable globally because "it's annoying"
disable = [
    "too-many-arguments",
    "too-many-locals", 
    "too-many-branches"
]

# ✅ GOOD: Keep strict standards, refactor when needed
disable = [
    "too-few-public-methods",  # Dataclasses intentionally minimal
    "import-error",            # Mypy catches these
]
```

---

## 🔍 How to Search for This Standard

**If you're wondering:**
- "Can I disable this pylint warning?" → Search: "pylint disable policy"
- "How to suppress pylint?" → Search: "how to suppress pylint warnings"
- "What disables are allowed?" → Search: "pylint global disable approved"
- "Do I need approval?" → Search: "pylint disable approval process"

---

## 📊 Current Status

**Project Score:** 9.96/10 (as of 2025-10-23)

**Remaining 0.04 points are documented design decisions:**
- `too-many-*` in `workflow_engine.py` (core orchestration, splitting would fragment)
- `protected-access` for cache management (internal module access)
- `broad-exception-caught` for robustness (graceful degradation)
- `global-statement` for cache (performance optimization)

**All documented with per-file justifications.**

**Target:** 10.0/10 for all new code

---

## 🔗 Related Standards

- [Production Code Checklist](ai-safety/production-code-checklist.md)
- [Code Quality Standards](code-quality.md)
- [Python Standards](../coding/python-standards.md)
- [RAG Content Authoring](../ai-assistant/rag-content-authoring.md) (how this doc was written)
