# Standards Creation Process

**Standard for creating, structuring, and maintaining standards in Agent OS Enhanced.**

---

## 🎯 Purpose

Define how to create new standards, when to create them, and how to structure them for maximum effectiveness. Standards are the "how to work" guidelines that shape agent behavior and code quality.

**Key Distinction**: Standards vs Specs
- **Standards**: Guidelines for HOW to work (this is a standard)
- **Specs**: Design docs for WHAT to build (features/implementations)

---

## 🚨 When to Create a Standard

Create a standard when you need to define:
- ✅ **Process/methodology** - How to do something consistently
- ✅ **Quality criteria** - What "good" looks like
- ✅ **Best practices** - Patterns that work well
- ✅ **Constraints/rules** - Things that must/must not be done
- ✅ **Behavioral patterns** - How agents should act

**Examples of standards:**
- Production code checklist
- Testing standards  
- RAG content authoring
- Git safety rules
- Documentation patterns

Do NOT create a standard for:
- ❌ Feature designs (use specs)
- ❌ One-time tasks (just do them)
- ❌ Project-specific details (document in project README)

---

## 📋 Standard Structure Template

```markdown
# [Standard Name]

**[One sentence describing what this standard defines]**

---

## 🎯 Purpose

[2-3 sentences explaining why this standard exists and what problem it solves]

**Core Principle**: [The key insight this standard embodies]

---

## 🚨 The Problem

[Describe what happens WITHOUT this standard]

**Example of the problem:**
[Concrete scenario showing the pain point]

---

## ✅ The Standard

### [Principle/Rule 1]

**What to do:**
[Clear, actionable guidance]

**Why:**
[Rationale for this principle]

**Example:**
```
[Code/text showing correct application]
```

**Anti-pattern:**
```
[Code/text showing what NOT to do]
```

### [Principle/Rule 2]

[Repeat structure]

---

## 📋 Checklist

When [doing the thing this standard covers]:

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

---

## 📚 Examples

### Example 1: [Scenario]

**Context**: [Situation]

**Bad** (violates standard):
```
[Example of violation]
```

**Good** (follows standard):
```
[Example of compliance]
```

**Why it matters**: [Impact of following vs not following]

---

## 🚫 Anti-Patterns

### Anti-Pattern 1: [Common mistake]

**Wrong:**
```
[What people do wrong]
```

**Right:**
```
[Correct approach]
```

---

## 📞 Questions?

**[Common question 1]?**
→ [Answer]

**[Common question 2]?**
→ [Answer]

---

**Related Standards:**
- [Related standard 1]
- [Related standard 2]

**Query anytime:**
```python
search_standards("[natural language query]")
```

---

**Remember**: [Key takeaway for this standard]
```

---

## 🔄 Standards Creation Workflow

### Step 1: Identify the Gap

**Trigger**: You experience a problem or inconsistency that needs a standard.

**Questions to ask:**
- Is this a repeating pattern that needs consistency?
- Would a guideline prevent quality/safety issues?
- Is this knowledge that agents need to query?

**Example**: 
- "Agents keep breaking out of Agent OS patterns"
- "Content isn't discoverable through RAG"
- "Code quality is inconsistent"

### Step 2: Research Existing Standards

**Before creating**, query to see if standard already exists:

```python
search_standards("[topic] standards")
search_standards("how to [do the thing]")
search_standards("[related concept] guidelines")
```

**If exists**: Update existing standard, don't create duplicate.

### Step 3: Draft the Standard

**Use the template above.**

**Key requirements:**
- Clear, actionable principles
- Examples showing good vs bad
- Checklist for compliance
- Anti-patterns documented
- RAG-optimized for discoverability (follow rag-content-authoring.md)

### Step 4: Test Discoverability

```python
# Test if agents can find your standard
search_standards("how to [do what standard covers]")
search_standards("[natural question about topic]")

# Should return your new standard in top 3-5 results
```

If not discoverable, add query hooks and keywords.

### Step 5: Place in Correct Directory

**Standards location**: `universal/standards/[category]/[standard-name].md`

**Categories:**
- `ai-assistant/` - How AI agents should work
- `ai-safety/` - Safety constraints and rules
- `architecture/` - Architectural patterns
- `concurrency/` - Concurrency standards
- `database/` - Database patterns
- `documentation/` - Documentation standards
- `failure-modes/` - Error handling patterns
- `installation/` - Installation/upgrade procedures
- `meta-framework/` - Framework creation/maintenance
- `performance/` - Performance optimization
- `security/` - Security patterns
- `testing/` - Testing standards
- `workflows/` - Workflow system standards

**Create new category** if none fit (but query first to see if it should merge with existing).

### Step 6: Test with Real Usage

**Dogfooding**: Use the standard yourself immediately.

**Check:**
- Can you follow the standard easily?
- Does it solve the problem it intended to solve?
- Are the examples clear?
- Is it discoverable through natural queries?

**Iterate** based on actual usage.

### Step 7: Ship to `universal/`

Commit to `universal/standards/[category]/[name].md`.

File watcher will detect and reindex within 30 seconds.

Verify it's indexed:
```python
search_standards("[your standard topic]")
```

---

## ✅ Quality Standards for Standards

A good standard must:

- [ ] **Solve a real problem** - Based on actual experience, not theoretical
- [ ] **Be actionable** - Clear what to do, not vague philosophy
- [ ] **Include examples** - Show good vs bad concretely
- [ ] **Be discoverable** - Returns for natural queries (RAG-optimized)
- [ ] **Have checklist** - Concrete compliance criteria
- [ ] **Document anti-patterns** - Show common mistakes
- [ ] **Link to related standards** - Part of coherent system
- [ ] **Be maintainable** - Single source of truth, no duplication
- [ ] **Be testable** - Can verify compliance programmatically

---

## 🚫 Anti-Patterns in Standards Creation

### Anti-Pattern 1: Vague Philosophy

**Wrong:**
```markdown
# Excellence Standard

Always strive for excellence in your code.
Be thoughtful and careful.
```

**Right:**
```markdown
# Production Code Checklist

Code must:
- [ ] Have Sphinx-style docstrings
- [ ] Include type hints for all parameters
- [ ] Handle errors with specific exception types
[...concrete, checkable criteria]
```

---

### Anti-Pattern 2: Creating Specs When You Need Standards

**Wrong thinking**: "I need to design a new testing approach" → Create spec

**Right thinking**: "I need to define how we test" → Create standard

**Test**: Does this define HOW to work (standard) or WHAT to build (spec)?

---

### Anti-Pattern 3: Duplicating Existing Standards

**Wrong**: Creating `python-testing-best-practices.md` when `testing/test-pyramid.md` already exists

**Right**: Update existing standard or link to it

**Always query first**:
```python
search_standards("[topic you're covering]")
```

---

### Anti-Pattern 4: Not RAG-Optimizing

**Wrong**: Writing for human readers who will read top-to-bottom

**Right**: Writing for AI agents who will query with natural language

**Follow**: `standards/documentation/rag-content-authoring.md`

---

## 📚 Examples of Good Standards

Study these as templates:

- `standards/ai-safety/production-code-checklist.md` - Comprehensive checklist format
- `standards/testing/test-pyramid.md` - Clear principles with examples
- `standards/workflows/workflow-construction-standards.md` - Structural guidelines
- `standards/documentation/rag-content-authoring.md` - RAG optimization

---

## 🔄 Maintaining Standards

### When to Update Standards

Update when:
- Technology/tools change (e.g., new testing framework)
- Pattern proves insufficient through usage
- Better approach discovered through dogfooding
- Discoverability issues found (agents can't find it)

### How to Update Standards

1. **Test current discoverability**:
   ```python
   search_standards("[topic]")
   ```

2. **Make updates**:
   - Preserve core principles
   - Update examples/tools/syntax
   - Add new anti-patterns discovered
   - Improve query hooks if needed

3. **Test new discoverability**:
   Same queries should still return the standard

4. **Commit to `universal/`**:
   File watcher reindexes automatically

### Deprecating Standards

If standard is obsolete:
- **Don't delete immediately** - May break existing queries
- **Add deprecation notice** at top:
  ```markdown
  ## ⚠️ DEPRECATED
  
  This standard is superseded by [new-standard.md].
  
  Use search_standards("[new topic]") for current guidance.
  ```
- **Keep for 3+ months** to allow transition
- **Then archive** to `deprecated/` directory

---

## 📊 Standards Metrics

Track effectiveness:

- **Discoverability**: Do natural queries return this standard?
- **Usage**: Do agents follow this standard in practice?
- **Quality impact**: Does code/work improve measurably?
- **Maintenance**: How often does it need updates?

**Good standard indicators:**
- Returns in top 3-5 for relevant queries
- Agents naturally follow it without prompting
- Quality metrics improve (test coverage, linter scores, etc.)
- Rarely needs updates (principles are stable)

---

## 📞 Questions?

**How do I know if something should be a standard vs a spec?**
→ Ask: "Is this HOW to work (standard) or WHAT to build (spec)?"

**Can I create a standard without formal approval?**
→ Yes! Agent OS is dogfooded. Experience a need → Create standard → Test it → Ship it.

**What if my standard conflicts with an existing standard?**
→ Query to find existing: `search_standards("[topic]")`. Update existing or document why new one is needed.

**How do I test if my standard is being followed?**
→ Review code/work for compliance. Add linter rules or automated checks if possible.

**What if my standard becomes obsolete?**
→ Add deprecation notice, point to replacement, keep for 3 months, then archive.

---

**Related Standards:**
- `standards/documentation/rag-content-authoring.md` - How to make standards discoverable
- `standards/meta-framework/command-language.md` - Command language for frameworks
- `standards/meta-framework/three-tier-architecture.md` - Framework architecture

**Query anytime:**
```python
search_standards("how to create a standard")
search_standards("standards creation process")
search_standards("when to write a standard vs spec")
```

---

**Remember**: Standards emerge from real experience. If you hit a problem that needs consistency, create the standard. Don't wait for permission. Dogfood it. Ship it.

