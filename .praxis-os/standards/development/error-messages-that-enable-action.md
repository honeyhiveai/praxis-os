# Error Messages That Enable Action

**Keywords for search**: error messages, actionable errors, error design, remediation guidance, auto-fix suggestions, field path errors, clear error messages, error formatting, user-friendly errors, debugging guidance, error message patterns, helpful errors, error context, error recovery, fail-fast errors, validation errors

---

## 🚨 TL;DR - Error Message Design Quick Reference

**Core Principle:** Error messages should tell AI agents (and humans) EXACTLY what to do to fix the problem, not just what went wrong.

**The Pattern:**
```
❌ Error: {specific problem}

**Field Path:** {config.section.field}

**What's Wrong:**
{clear explanation of the problem}

**How to Fix:**
{concrete steps or commands}

**Why This Matters:**
{rationale for the requirement}

**Example:**
{example of correct usage}
```

**Critical Requirements:**
- ✅ Field paths included (indexes → standards → vector → chunk_size)
- ✅ Concrete remediation (actual commands to run)
- ✅ Examples of correct usage
- ✅ Context about why it matters
- ✅ No vague errors ("something failed")

**Common Anti-Patterns:**
- ❌ Vague errors ("validation failed")
- ❌ No field paths ("value must be positive")
- ❌ No remediation ("fix and try again")
- ❌ Technical jargon without context
- ❌ Error without impact explanation

---

## ❓ Questions This Answers

1. "How do I write actionable error messages?"
2. "What should an error message include?"
3. "How do I format field paths in errors?"
4. "How do I provide remediation guidance?"
5. "How do I write examples in error messages?"
6. "How do I make errors user-friendly for AI agents?"
7. "What is the error message structure?"
8. "How do I include context in errors?"
9. "How do I test error messages?"
10. "How do I format multi-field errors?"
11. "How do I write errors for validation failures?"
12. "How do I make errors discoverable?"
13. "How do I provide error recovery paths?"
14. "How do I explain why requirements exist?"
15. "How do I avoid vague error messages?"

---

## 🎯 Purpose

Define patterns for writing error messages that enable immediate action by providing clear explanations, concrete remediation steps, and examples of correct usage.

**Key Distinction:** Actionable Errors vs Status Messages
- **Actionable Errors:** Tell user HOW to fix (this standard)
- **Status Messages:** Tell user WHAT failed (insufficient)

**Why This Matters:** AI agents and humans need to know how to fix errors, not just that something failed. Vague errors ("validation failed") require multiple back-and-forth cycles. Clear errors with remediation enable immediate fixes.

---

## ❌ The Problem

**Without actionable errors:**

1. **Vague Errors**
   ```
   Error: Validation failed
   ```
   - What validation?
   - Which field?
   - What was wrong?
   - How to fix?

2. **No Field Paths**
   ```
   Error: chunk_size must be >= 100
   ```
   - Which chunk_size? (might be multiple)
   - Where in config?
   - What file?

3. **No Remediation**
   ```
   Error: Test output file not found
   ```
   - What file was expected?
   - Where should it be?
   - How to create it?

4. **No Context**
   ```
   Error: Value must be positive
   ```
   - Why must it be positive?
   - What breaks if negative?
   - What's the valid range?

---

## ✅ The Standard

### Pattern 1: Complete Error Structure

**Full Format:**
```python
class ActionableError(Exception):
    def __init__(
        self,
        error: str,
        field_path: Optional[str] = None,
        current_value: Optional[Any] = None,
        remediation: str = "",
        why_matters: str = "",
        example: Optional[str] = None,
        impact: Optional[str] = None
    ):
        self.error = error
        self.field_path = field_path
        self.current_value = current_value
        self.remediation = remediation
        self.why_matters = why_matters
        self.example = example
        self.impact = impact
    
    def format(self) -> str:
        msg = f"❌ Error: {self.error}\n\n"
        
        if self.field_path:
            msg += f"**Field Path:** {self.field_path}\n"
        
        if self.current_value is not None:
            msg += f"**Current Value:** {self.current_value!r}\n\n"
        
        if self.remediation:
            msg += f"**How to Fix:**\n{self.remediation}\n\n"
        
        if self.why_matters:
            msg += f"**Why This Matters:**\n{self.why_matters}\n\n"
        
        if self.example:
            msg += f"**Example:**\n{self.example}\n\n"
        
        if self.impact:
            msg += f"**Impact if Not Fixed:**\n{self.impact}\n"
        
        return msg
```

**Example Output:**
```
❌ Error: chunk_size must be >= 100

**Field Path:** indexes → standards → vector → chunk_size
**Current Value:** 50

**How to Fix:**
Update config/mcp.yaml:

indexes:
  standards:
    vector:
      chunk_size: 200  # Must be >= 100

**Why This Matters:**
Chunks < 100 tokens are too small for effective semantic search.
Quality degrades below this threshold.

**Example:**
indexes:
  standards:
    vector:
      chunk_size: 200  # Recommended: 100-500 for standards
      model: "all-MiniLM-L6-v2"
      dimension: 384
```

---

### Pattern 2: Field Path Format

**Format:** `parent → child → grandchild → field`

**Implementation:**
```python
def format_field_path(loc: tuple) -> str:
    """Format Pydantic error location as field path.
    
    Args:
        loc: Pydantic error location tuple
        
    Returns:
        Formatted path like "indexes → standards → chunk_size"
    """
    return " → ".join(str(part) for part in loc)

# Example
loc = ("indexes", "standards", "vector", "chunk_size")
path = format_field_path(loc)  # "indexes → standards → vector → chunk_size"
```

**Why Arrows:**
- Clear visual hierarchy
- Not confused with file paths (no `/`)
- Not confused with dict access (no `.`)
- Consistent across all errors

---

### Pattern 3: Remediation Guidance

**Always Include:**

1. **Exact Location**
   ```
   Update config/mcp.yaml line 15:
   ```

2. **Concrete Steps**
   ```
   1. Open config/mcp.yaml
   2. Find the 'indexes' section
   3. Change chunk_size from 50 to 200
   4. Save and restart
   ```

3. **Commands to Run**
   ```bash
   # Fix the config
   sed -i 's/chunk_size: 50/chunk_size: 200/' config/mcp.yaml
   
   # Verify
   python -m mcp_server validate-config
   ```

4. **What Success Looks Like**
   ```
   After fix, you should see:
   ✅ Config validation passed
   ```

**Implementation:**
```python
def generate_remediation(error_type: str, context: Dict) -> str:
    """Generate concrete remediation steps."""
    if error_type == "config_value_too_small":
        return f"""
Update {context['file']} line {context['line']}:

{context['field']}: {context['min_value']}  # Must be >= {context['min_value']}

Then restart the service:
mcp_server restart
"""
    
    elif error_type == "file_not_found":
        return f"""
Create the missing file:

mkdir -p {context['directory']}
touch {context['file_path']}

Or run the setup script:
python scripts/setup_{context['component']}.py
"""
```

---

### Pattern 4: Examples in Errors

**Show Valid Configuration:**
```python
example = """
# Valid configuration example
indexes:
  standards:
    vector:
      chunk_size: 200
      model: "all-MiniLM-L6-v2"
      dimension: 384
    fts:
      enabled: true
      language: "english"
"""
```

**Show Valid Evidence:**
```python
example = """
# Valid evidence structure
{
  "test_output_path": ".test-results/junit.xml",
  "tests_run": 42,
  "tests_passed": 40,
  "tests_failed": 2,
  "coverage_percent": 85.5
}
"""
```

**Show Valid Usage:**
```python
example = """
# Correct usage
result = pos_search_project(
    content_type="standards",
    query="how to implement X",
    session_id="abc123"
)
"""
```

---

### Pattern 5: Context and Impact

**Explain Why:**
```python
why_matters = """
Chunk size < 100 tokens degrades search quality because:
- Semantic embeddings lose context
- Related concepts get separated
- Search relevance drops below 70%

Recommended range: 100-500 tokens for standards content.
"""
```

**Explain Impact:**
```python
impact = """
Without this fix:
- Search results will be less relevant
- AI agents won't find critical standards
- Behavioral reinforcement will fail
- System effectiveness drops by ~40%
"""
```

---

### Pattern 6: Multiple Errors Format

**Show All Errors:**
```python
def format_multiple_errors(errors: List[ActionableError]) -> str:
    """Format multiple errors with numbering."""
    msg = f"❌ {len(errors)} Validation Errors Found\n\n"
    
    for i, error in enumerate(errors, 1):
        msg += f"## Error {i}/{len(errors)}\n\n"
        msg += error.format()
        msg += "\n" + "─" * 60 + "\n\n"
    
    msg += "**Fix all errors above before continuing.**\n"
    return msg
```

**Example Output:**
```
❌ 3 Validation Errors Found

## Error 1/3

❌ Error: chunk_size must be >= 100
Field Path: indexes → standards → vector → chunk_size
[... full error ...]

────────────────────────────────────────────────────────────

## Error 2/3

❌ Error: timeout must be positive
Field Path: indexes → standards → timeout_seconds
[... full error ...]

────────────────────────────────────────────────────────────

## Error 3/3

❌ Error: unknown field detected
Field Path: indexes → standards → unknow_field
[... full error ...]

────────────────────────────────────────────────────────────

**Fix all errors above before continuing.**
```

---

### Pattern 7: Error Classes Hierarchy

**Create Specific Error Types:**
```python
class prAxIsOSError(Exception):
    """Base error for all prAxIs OS errors."""
    pass

class ConfigError(prAxIsOSError):
    """Configuration validation error."""
    pass

class BehavioralEngineeringError(prAxIsOSError):
    """Behavioral engineering system failure."""
    pass

class WorkflowValidationError(prAxIsOSError):
    """Workflow evidence validation failure."""
    pass

class IndexError(prAxIsOSError):
    """Index operation failure."""
    pass
```

**Use Specific Types:**
```python
# Specific error type makes handling easier
try:
    config = load_config()
except ConfigError as e:
    print(e.format())
    sys.exit(1)
except BehavioralEngineeringError as e:
    logger.critical("Behavioral system failed", exc_info=e)
    raise  # Don't degrade, fail-fast
```

---

## 📋 Checklist

**Error Content Checklist:**
- [ ] Error message is specific (not vague)
- [ ] Field path included (if applicable)
- [ ] Current value shown (helps debugging)
- [ ] Remediation steps concrete
- [ ] Examples provided
- [ ] Context explains why
- [ ] Impact explained if not obvious

**Format Checklist:**
- [ ] Starts with ❌ emoji
- [ ] Uses bold headers (**How to Fix:**)
- [ ] Code blocks for config/commands
- [ ] Field paths use arrows (→)
- [ ] Multiple errors numbered

**Quality Checklist:**
- [ ] AI agent can copy-paste fix
- [ ] No jargon without explanation
- [ ] File paths are absolute or clearly relative
- [ ] Commands are complete (not partial)
- [ ] Success criteria defined

---

## 💡 Examples

See Pattern sections above for comprehensive examples.

---

## ⚠️ Anti-Patterns

### Anti-Pattern 1: Vague Error

❌ **Wrong:**
```python
raise ValueError("Validation failed")
```

✅ **Correct:**
```python
raise ConfigError(
    error="chunk_size must be >= 100",
    field_path="indexes → standards → vector → chunk_size",
    current_value=50,
    remediation="Update config/mcp.yaml: chunk_size: 200"
)
```

---

### Anti-Pattern 2: No Remediation

❌ **Wrong:**
```python
raise FileNotFoundError("Test output not found")
```

✅ **Correct:**
```python
raise WorkflowValidationError(
    error="Test output file not found",
    field_path="test_output_path",
    remediation="""
Run tests to generate output:
pytest tests/ --junit-xml=.test-results/junit.xml

Then submit evidence with correct path.
"""
)
```

---

### Anti-Pattern 3: Technical Jargon

❌ **Wrong:**
```python
raise ValueError("FTS index corruption detected at offset 0x4A2F")
```

✅ **Correct:**
```python
raise IndexError(
    error="Search index is corrupted",
    remediation="""
Rebuild the index:
python -m mcp_server rebuild-index --type=standards

This will take ~60 seconds.
""",
    why_matters="Corrupted index causes search failures and behavioral drift"
)
```

---

## 📚 Related Standards

- `pos_search_project(content_type="standards", query="Pydantic validation error formatting")`
- `pos_search_project(content_type="standards", query="fail-fast error handling patterns")`
- `pos_search_project(content_type="standards", query="adversarial design validation errors")`

---

## 📊 When to Query This Standard

| Scenario | Query | Why |
|----------|-------|-----|
| Writing errors | `error message design patterns` | Need error structure |
| Validation errors | `actionable validation error messages` | Need field path format |
| Error formatting | `how to format error messages for AI` | Need formatting patterns |
| Remediation | `auto-fix suggestion patterns` | Need remediation guidance |
| Testing | `testing error messages` | Need test patterns |

---

**Version:** 1.0.0  
**Created:** 2025-11-04  
**Last Updated:** 2025-11-04  
**Next Review:** After Ouroboros error handling implementation

