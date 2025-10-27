# Implementation Approach

**Project:** Spec-Driven Development Enforcement  
**Date:** 2025-10-07

---

## 1. Implementation Philosophy

**Core Approach:** Documentation-driven behavior change

Rather than building complex enforcement systems, we leverage:
1. Clear standards in MCP-queryable format
2. Behavioral triggers in `.cursorrules`
3. AI's ability to query and follow standards
4. Human review as ultimate enforcement

---

## 2. File Creation Strategy

### 2.1 Universal Standard

**File:** `universal/standards/ai-safety/spec-driven-development.md`

**Implementation Pattern:**
```markdown
# Standard Structure
1. Core Principle (one sentence)
2. Process Flow (step by step)
3. When Spec Required (clear decision tree)
4. Spec Structure (5-file standard)
5. Content Depth Guidelines
6. Behavioral Triggers (what to query)
7. Examples (small and large specs)
```

**Content Strategy:**
- Start with "why" (core principle)
- Be prescriptive (must/should/may)
- Include decision trees
- Provide concrete examples
- Reference related standards

**Tone:**
- Direct and authoritative
- AI-readable (clear sections, bullets)
- Human-reviewable (concise, organized)

---

### 2.2 Project-Specific Baseline Quality

**File:** `.praxis-os/standards/baseline-quality.md`

**Implementation Pattern:**
```markdown
# Baseline Quality for {PROJECT_NAME}

## Testing Requirements
- [Specific to project: test framework, coverage, etc.]

## Documentation Requirements
- [Specific to project: docstring style, README updates, etc.]

## Code Quality Requirements
- [Specific to project: linters, formatters, style guides]

## Bug Fix Process
- [Specific to project: reproduce, test, document]
```

**Content Strategy:**
- Make it project-specific (not generic)
- Be measurable (coverage %, no linter errors)
- Reference existing tools (tox, pytest, mypy)
- Include examples from this project

**For prAxIs OS Specifically:**
- Testing: pytest, tox, >85% coverage
- Docs: Google-style docstrings, update READMEs
- Quality: mypy, no linter errors, Path objects
- Process: regression tests, root cause documentation

---

### 2.3 .cursorrules Update

**Current Trigger (Line ~14):**
```markdown
4. About to write ANY code? → Query MCP: `"production code universal checklist"` (ALL code is production code)
```

**Updated Trigger:**
```markdown
3. About to write ANY code? → Query MCP: `"spec-driven development"` (Is spec approved?)
4. Implementing approved spec? → Query MCP: `"production code universal checklist"`
```

**Implementation:**
- Add new trigger as #3
- Renumber existing #3 to #4
- Keep existing triggers intact (additive change)
- Update comment to clarify two-phase check

---

## 3. Content Templates

### 3.1 Universal Standard Template

```markdown
# Spec-Driven Development

**Standard Type:** AI Safety / Process  
**Scope:** Universal  
**Enforcement:** Behavioral (MCP query)

---

## 🎯 Core Principle

**All feature work requires an approved specification (spec) before implementation.**

The spec is the approved design artifact. The planning phase produces it, the implementation phase executes it.

---

## 📋 Process Flow

### Step 1: Planning Phase
- Human requests feature/change
- AI and human discuss design
- AI creates spec (5-file structure)

### Step 2: Spec Review
- Human reviews spec
- Discusses design decisions
- Requests changes if needed

### Step 3: Approval
- Human explicitly approves spec
- Spec status updated to "Approved"
- Approval recorded in spec README

### Step 4: Implementation Phase
- AI implements approved spec
- Uses `spec_execution_v1` workflow (recommended)
- Follows baseline quality requirements
- Updates tasks.md as work progresses

---

## 🚦 When Spec Required

### ❌ No Spec Needed (Trivial Changes)
- Typo fixes
- Formatting changes
- Obvious non-controversial changes
- No design decisions required

### ✅ Spec Required (Standard Changes)
- New features
- Bug fixes with design decisions
- Refactoring
- Process changes
- Standard additions/modifications

### ✅ Full Detailed Spec (System Changes)
- Architectural changes
- Major redesigns
- New workflows
- Framework modifications

**Rule of Thumb:** If uncertain, create a spec. Human can say "no spec needed."

---

## 📁 Spec Structure (Standard 5-File Interface)

**ALL specs MUST include these files:**

1. **README.md** - Executive summary
   - Status, priority, effort estimate
   - Problem statement and solution overview
   - Approval section

2. **srd.md** - Software Requirements Document
   - Stakeholder requirements
   - Functional requirements
   - Non-functional requirements
   - Acceptance criteria

3. **specs.md** - Technical Specifications
   - Architecture overview
   - Component design
   - Data models
   - Integration points

4. **implementation.md** - Implementation Approach
   - Implementation philosophy
   - File creation strategy
   - Code patterns
   - Testing approach

5. **tasks.md** - Task Breakdown
   - Phases and tasks
   - Acceptance criteria
   - Time estimates
   - Dependencies

---

## 📏 Content Depth vs Structure

**Key Insight:** Structure is standardized, content depth varies by scope.

### Small Change Example (Bug Fix)
```
README.md: 1 page (brief summary)
srd.md: 2 pages (key requirements)
specs.md: 2 pages (approach and design)
implementation.md: 1 page (implementation pattern)
tasks.md: 5-10 tasks
```

### Large Change Example (Architecture)
```
README.md: 2-3 pages (comprehensive summary)
srd.md: 5-10 pages (detailed requirements)
specs.md: 10-20 pages (full architecture)
implementation.md: 5-10 pages (detailed patterns)
tasks.md: 30-50 tasks
```

**The interface is consistent, the content scales with complexity.**

---

## 🤖 Behavioral Triggers for AI

### Before Writing Any Code
```
Query: "spec-driven development"
Check: Is there an approved spec?
  - YES → Proceed with implementation
  - NO → Create spec and seek approval
```

### When Uncertain About Process
```
Query: "spec-driven development"
Read: Process flow and decision tree
Action: Follow the process
```

### Before Completing Work
```
Query: "baseline quality"
Check: Does implementation meet requirements?
  - Tests written?
  - Docs updated?
  - Linter clean?
  - Bug fix process followed?
```

---

## 📚 Examples

### Example 1: Small Spec (Bug Fix)
See: `.praxis-os/specs/example-bug-fix/` (if created)
- Brief 1-page README
- Key requirements only
- Simple design
- 3-5 tasks

### Example 2: Large Spec (System Design)
See: `.praxis-os/specs/2025-10-07-dynamic-workflow-session-refactor/`
- Comprehensive README
- Detailed requirements
- Full architecture
- 15+ tasks across 4 phases

---

## 🔗 Related Standards

- [Operating Model](universal/usage/operating-model.md) - Human orchestrates, AI implements
- [Production Code Checklist](universal/standards/ai-safety/production-code-checklist.md) - Quality requirements
- [Baseline Quality](.praxis-os/standards/baseline-quality.md) - Project-specific requirements

---

## ⚠️ Anti-Patterns

### ❌ DON'T: Skip spec because "it's small"
If it has design decisions, it needs a spec (even a brief one).

### ❌ DON'T: Start implementing during planning phase
Planning produces the spec. Implementation comes after approval.

### ❌ DON'T: Update code without updating spec
The spec is the source of truth. Keep it in sync.

### ❌ DON'T: Assume approval without explicit confirmation
Human must explicitly approve. "Looks good" ≠ "Approved."

---

## ✅ Best Practices

### ✅ DO: Query standard when uncertain
Better to ask than assume.

### ✅ DO: Create brief specs for small changes
Structure stays consistent, content scales down.

### ✅ DO: Keep spec updated during implementation
If design changes, update the spec.

### ✅ DO: Check baseline quality before declaring done
Tests, docs, linting - all must pass.

---

**This standard is indexed in MCP RAG and queryable by AI agents.**
```

---

### 3.2 Baseline Quality Template

```markdown
# Baseline Quality Requirements

**Project:** prAxIs OS  
**Last Updated:** 2025-10-07

---

## Overview

These are **mandatory** requirements for ALL implementations in this project, regardless of scope or change type.

**Principle:** Every change must meet baseline quality before being considered complete.

---

## 1. Testing Requirements

### Unit Tests
- [ ] All new functions and classes have unit tests
- [ ] All new code paths covered
- [ ] Edge cases and error conditions tested
- [ ] Tests use meaningful assertions (not just "doesn't crash")

### Integration Tests
- [ ] Cross-component features have integration tests
- [ ] End-to-end workflows validated
- [ ] Real MCP tool calls tested (not just mocks)

### Test Coverage
- [ ] New code has >85% coverage
- [ ] No decrease in overall project coverage
- [ ] Run: `tox -e py311` to verify

### Test Quality
- [ ] Tests are deterministic (no flaky tests)
- [ ] Tests clean up after themselves (temp files, state)
- [ ] Test names clearly describe what's being tested

---

## 2. Documentation Requirements

### Code Documentation
- [ ] All public APIs have Google-style docstrings
- [ ] All classes have docstrings describing purpose
- [ ] Complex logic has inline comments explaining "why"
- [ ] Type hints on all function signatures

### Project Documentation
- [ ] README updated if user-facing changes
- [ ] CHANGELOG updated with changes
- [ ] Examples provided for new features
- [ ] Architecture docs updated if structure changes

### Spec Documentation
- [ ] Implementation matches approved spec
- [ ] tasks.md updated as work progresses
- [ ] Final completion summary added to tasks.md

---

## 3. Code Quality Requirements

### Linting
- [ ] No linter errors: `read_lints` must be clean
- [ ] No type errors: `mypy` must pass
- [ ] Consistent code style with existing codebase

### Best Practices
- [ ] No hardcoded paths (use `Path` objects)
- [ ] No credential leaks (use `.env`, never commit secrets)
- [ ] Proper error handling (specific exceptions, not bare `except`)
- [ ] Resource cleanup (file handles, connections)

### Code Structure
- [ ] Functions are focused (single responsibility)
- [ ] No duplicate code (DRY principle)
- [ ] Proper separation of concerns
- [ ] Dependency injection where appropriate

---

## 4. Bug Fix Process

### Reproduction
- [ ] Bug reproduced with test (if possible)
- [ ] Root cause identified and documented
- [ ] Edge cases considered

### Fix Implementation
- [ ] Regression test added (prevents recurrence)
- [ ] Fix addresses root cause (not symptom)
- [ ] No introduction of new bugs

### Documentation
- [ ] Root cause documented in commit message
- [ ] Fix approach explained in spec (if complex)
- [ ] Related bugs checked (similar issues elsewhere?)

---

## 5. Git Hygiene

### Commits
- [ ] Meaningful commit messages
- [ ] Logical commit grouping (not "WIP" or "fixes")
- [ ] No `--no-verify` or `--force` without explicit approval

### Branches
- [ ] Branch named descriptively: `feature/`, `bugfix/`, `refactor/`
- [ ] Branch focused on single change
- [ ] Branch synced with main before PR

---

## 6. Review Checklist

Before declaring work complete, verify:

- [ ] All tests pass: `tox`
- [ ] Linter clean: `read_lints`
- [ ] Docs updated: README, docstrings, etc.
- [ ] Spec synced: tasks.md marked complete
- [ ] No hardcoded paths
- [ ] No credential leaks
- [ ] No new linter errors introduced
- [ ] Implementation matches approved design

---

## 7. Tool-Specific Standards

### Python
- Use `pathlib.Path` for all paths
- Use `typing` for type hints
- Use `dataclasses` for data structures
- Use `pytest` for testing

### MCP
- All tools have docstrings
- All tools handle errors gracefully
- All tools return structured data (dicts)
- All tools logged via `logger`

### Workflows
- Command language preserved
- Templates use clean placeholders
- Metadata includes all required fields
- Backward compatibility maintained

---

## 8. Exemptions

**These requirements can be waived only with explicit approval:**

- Test coverage below 85% (if code is not testable)
- Linter errors (if external library issue)
- Documentation for internal utilities (if truly internal)

**Request exemption:** Explain in spec or implementation.md why exemption needed.

---

## 9. Consequences of Non-Compliance

**Work is not complete until baseline quality is met.**

If baseline quality is missing:
1. AI must fix before declaring done
2. PR will be rejected
3. Work must be reworked

---

## 10. Continuous Improvement

This document should evolve with the project.

**Add new requirements when:**
- Pattern of issues emerges
- New tools/frameworks adopted
- Team identifies quality gaps

**Remove requirements when:**
- No longer relevant (tool deprecated)
- Proven to not add value

---

**Last Review:** 2025-10-07  
**Next Review:** 2025-11-07 (monthly)
```

---

## 4. Implementation Order

### Phase 1: Standards Creation
1. Create `spec-driven-development.md` (universal)
2. Create `baseline-quality.md` (project-specific)
3. Review both with user for approval

### Phase 2: Integration
1. Update `.cursorrules` with new trigger
2. Verify MCP RAG can find standards
3. Test AI queries return correct content

### Phase 3: Validation
1. Test: Request feature without spec
2. Verify: AI creates spec first
3. Verify: AI checks baseline quality before completing

### Phase 4: Documentation
1. Add spec examples to docs
2. Update CONTRIBUTING.md
3. Create announcement/guidance doc

---

## 5. Code Patterns

### 5.1 No Code Changes Required

**Key Insight:** This is a behavioral change, not a code change.

No modifications to:
- `workflow_engine.py`
- `praxis_os_rag.py`
- MCP tools
- Any Python code

Only changes:
- Markdown standards (new files)
- `.cursorrules` (one line addition)

---

### 5.2 Standard Writing Pattern

**Structure:**
```markdown
# [Standard Name]

## Core Principle (Why)
One sentence summary.

## Process (How)
Step-by-step flow.

## Decisions (When)
Clear decision tree.

## Details (What)
Specific requirements.

## Examples (Show)
Concrete examples.

## Related (Links)
References to other standards.
```

**Style Guide:**
- Use emoji for section headers (🎯, 📋, 🚦, etc.) - makes scanning easier
- Use checkboxes for checklists
- Use tables for decision matrices
- Use code blocks for templates
- Use bold for **MUST**, italics for *SHOULD*, regular for MAY

---

## 6. Testing Approach

### 6.1 Manual Validation Tests

**Test 1: Standard Queryable**
```
Action: Query MCP RAG for "spec-driven development"
Expected: Standard returned with correct content
Validation: Manual review of response
```

**Test 2: AI Creates Spec Before Implementing**
```
Action: Request new feature
Expected: AI creates spec and seeks approval
Validation: Observe AI behavior
```

**Test 3: AI Checks Baseline Quality**
```
Action: Complete implementation
Expected: AI queries baseline quality and verifies compliance
Validation: Observe checklist verification
```

### 6.2 Integration with Existing Tests

No changes to existing test suite required.

Existing tests continue to validate:
- Workflow engine functionality
- MCP tool behavior
- RAG query performance

---

## 7. Rollback Strategy

**If standard doesn't work as expected:**

1. **Immediate:** Remove `.cursorrules` trigger
2. **Short-term:** Update standard based on issues
3. **Long-term:** Consider programmatic enforcement

**Rollback is simple:** Just remove the trigger line. Standards remain as documentation even if not enforced behaviorally.

---

## 8. Success Validation

### Quantitative Metrics
- [ ] Standard queryable via MCP (response time <100ms)
- [ ] AI queries standard 100% of time before writing code
- [ ] 100% of non-trivial changes have approved specs

### Qualitative Metrics
- [ ] Human feels in control of design decisions
- [ ] AI does not jump to implementation without approval
- [ ] Development process feels systematic, not ad-hoc

---

## 9. Documentation Strategy

### User-Facing Documentation
- Add "How to Request Features" guide
- Reference spec-driven process
- Link to example specs

### Developer Documentation
- Update CONTRIBUTING.md
- Reference standard in development workflow
- Add "Creating Specs" guide

### AI-Facing Documentation
- Standards are self-documenting (AI queries them)
- `.cursorrules` provides behavioral triggers
- No separate AI documentation needed

---

## 10. Future Extensions

### Near-Term (Next Month)
- Add example specs (small and large)
- Create spec template generator script
- Document lessons learned

### Medium-Term (Next Quarter)
- Consider `create_spec_v1` workflow
- Add spec approval MCP tool
- Implement spec linting

### Long-Term (Next Year)
- Integrate with CI/CD for validation
- Add spec metrics dashboard
- Expand to product layer

---

**Implementation Status:** Ready for Approval  
**Approval Required From:** Josh
