# Technical Specifications

**Project:** Spec-Driven Development Enforcement  
**Date:** 2025-10-07

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      User Request                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │    .cursorrules Trigger       │
         │  "About to write code?"       │
         │  → Query MCP for standard     │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │   MCP RAG: Query Standard     │
         │  "spec-driven-development"    │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │   Standard Returns Process    │
         │  Planning → Spec → Approval   │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │      AI Creates Spec          │
         │    (5-file structure)         │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │    Human Reviews & Approves   │
         └───────────┬───────────────────┘
                     │
                     ▼
         ┌───────────────────────────────┐
         │  Implementation Phase Begins  │
         │  (using spec_execution_v1)    │
         └───────────────────────────────┘
```

---

## 2. Component Design

### 2.1 Standard Document Structure

**File:** `universal/standards/ai-safety/spec-driven-development.md`

**Purpose:** Universal standard defining spec-driven process

**Content Structure:**
```markdown
# Spec-Driven Development

## Core Principle
All feature work requires approved design (spec) before implementation.

## Process Flow
1. Planning Phase: Design discussion
2. Spec Creation: 5-file standard structure
3. Approval: Human review and explicit approval
4. Implementation: Execute via workflow

## When Spec Required
- ❌ Trivial: typos, formatting, obvious fixes
- ✅ Standard: features, bug fixes, refactors
- ✅ System: architecture, redesigns, processes

## Spec Structure (Standard 5-File Interface)
1. README.md - Executive summary
2. srd.md - Requirements
3. specs.md - Technical design
4. implementation.md - Implementation approach
5. tasks.md - Task breakdown

## Content Depth vs Structure
- Small change: Brief spec (each file may be 1-2 sections)
- Large change: Detailed spec (comprehensive content)
- Structure: ALWAYS the same 5 files

## Baseline Quality
See project-specific `.praxis-os/standards/baseline-quality.md`

## Behavioral Triggers
- "About to write code?" → Query this standard
- "User requests feature?" → Create spec first
- "Uncertain about scope?" → Create spec
```

---

### 2.2 Baseline Quality Document

**File:** `.praxis-os/standards/baseline-quality.md` (project-specific)

**Purpose:** Define mandatory quality requirements for THIS project

**Content Structure:**
```markdown
# Baseline Quality Requirements
## Project: Agent OS Enhanced

### Testing Requirements
- Unit tests for all new functions/classes
- Integration tests for cross-component features
- Test coverage >85% for new code
- All tests pass before PR

### Documentation Requirements
- Docstrings for all public APIs
- Update relevant README files
- Add examples for new features
- Inline comments for complex logic

### Code Quality Requirements
- No linter errors (checked via read_lints)
- Type hints for Python code
- Follow existing code style
- No hardcoded paths (use Path objects)

### Bug Fix Process
- Reproduce bug with test (if possible)
- Create spec if fix requires design decisions
- Document root cause in commit message
- Add regression test
```

---

### 2.3 .cursorrules Integration

**Current `.cursorrules` Trigger:**
```markdown
## 🚨 FIRST ACTIONS (Before Responding)
4. About to write ANY code? → Query MCP: `"production code universal checklist"`
```

**Enhanced Trigger:**
```markdown
## 🚨 FIRST ACTIONS (Before Responding)
1. Question about standards/patterns? → Query MCP first, respond second
2. Uncertain about your role? → Query MCP: `"operating model"`
3. About to write ANY code? → Query MCP: `"spec-driven development"` (Is spec approved?)
4. Implementing approved spec? → Query MCP: `"production code universal checklist"`
```

---

## 3. Data Models

### 3.1 Spec Structure

```
.praxis-os/specs/{YYYY-MM-DD-spec-name}/
├── README.md           # Executive summary, status, approval
├── srd.md             # Requirements document
├── specs.md           # Technical design
├── implementation.md  # Implementation approach
└── tasks.md           # Task breakdown
```

**Metadata Fields (in README.md):**
- `Date`: YYYY-MM-DD format
- `Status`: Draft | Approved | In Progress | Complete | Cancelled
- `Priority`: Low | Medium | High | Critical
- `Estimated Effort`: Time estimate
- `Approval`: Who approved and when

---

### 3.2 Change Categories

```python
class ChangeCategory(Enum):
    TRIVIAL = "trivial"      # No spec needed
    STANDARD = "standard"    # Spec required
    SYSTEM = "system"        # Full detailed spec
```

**Decision Matrix:**

| Change Type | Design Decisions? | Spec Required? | Category |
|-------------|-------------------|----------------|----------|
| Typo fix | No | No | Trivial |
| Formatting | No | No | Trivial |
| New feature | Yes | Yes | Standard |
| Bug fix (simple) | No | No | Trivial |
| Bug fix (complex) | Yes | Yes | Standard |
| Refactor | Yes | Yes | Standard |
| Architecture change | Yes | Yes | System |
| New workflow | Yes | Yes | System |
| Process change | Yes | Yes | System |

---

## 4. Integration Points

### 4.1 MCP RAG Query

**AI Query Flow:**
```python
# AI is about to write code, checks standard
response = mcp_search_standards("spec-driven development")

# Response includes:
{
  "standard": "All feature work requires approved spec",
  "process": "Planning → Spec → Approval → Implementation",
  "spec_structure": "5 files: README, srd, specs, implementation, tasks",
  "when_required": "Features, bug fixes, refactors, architecture"
}

# AI decision:
if has_design_decisions():
    create_spec()
    await_approval()
else:
    proceed_with_trivial_change()
```

### 4.2 Workflow Integration

**spec_execution_v1 Workflow:**
- Assumes spec is already approved
- Phase 0 confirms scope and context
- Phases 1+ implement tasks from `tasks.md`

**Relationship:**
```
Spec Creation (manual) → Approval (manual) → spec_execution_v1 (workflow)
         ↑                      ↑                        ↑
    Planning Phase         Design Review         Implementation Phase
```

---

## 5. Behavioral Logic

### 5.1 AI Decision Tree

```
User Request
    │
    ├─ Is it trivial? (typo, format)
    │   └─ YES → Proceed directly
    │
    └─ NO → Does design exist?
        │
        ├─ YES → Is it approved?
        │   │
        │   ├─ YES → Implement
        │   └─ NO → Seek approval
        │
        └─ NO → Create spec
            └─ Present for approval
            └─ Implement after approval
```

### 5.2 Approval Tracking

**Current (Simple):**
- Spec has "Status: Approved" in README.md
- Human explicitly says "approved" in chat

**Future (Enhanced):**
- MCP tool: `approve_spec(spec_name, approver)`
- Auditable approval log
- Timestamp and signature

---

## 6. Error Handling

### 6.1 AI Violations

**Scenario:** AI starts writing code without spec

**Detection:**
- Human notices and stops AI
- Post-hoc review finds unapproved changes

**Response:**
- Revert changes
- Create spec
- Get approval
- Re-implement

### 6.2 Unclear Scope

**Scenario:** Unclear if change needs spec

**Resolution:**
- AI queries `spec-driven development` standard
- AI **errs on side of creating spec**
- Human can say "no spec needed, proceed"

---

## 7. Performance Considerations

### 7.1 Query Latency
- MCP RAG query: <100ms (already optimized)
- Spec creation: Human interaction (not automated)
- No performance impact on actual implementation

### 7.2 Storage
- Each spec: ~20-50 KB
- Git tracks history
- Negligible storage impact

---

## 8. Testing Strategy

### 8.1 Standard Validation
- **Test:** Query MCP RAG for "spec-driven development"
- **Expected:** Standard returned with correct content
- **Method:** Manual query verification

### 8.2 Behavioral Validation
- **Test:** Request feature without providing spec
- **Expected:** AI creates spec and seeks approval before implementing
- **Method:** Manual interaction test

### 8.3 Baseline Quality Validation
- **Test:** Check if `.praxis-os/standards/baseline-quality.md` exists
- **Expected:** AI queries it before completing work
- **Method:** Manual interaction test

---

## 9. Migration Strategy

### 9.1 Rollout Plan

**Phase 1: Standards Creation** (This Spec)
1. Create `spec-driven-development.md` universal standard
2. Create `baseline-quality.md` project-specific standard
3. Update `.cursorrules` with new trigger
4. Validate MCP RAG indexing

**Phase 2: Validation**
1. Test AI behavior with feature request
2. Confirm spec creation before implementation
3. Confirm baseline quality adherence

**Phase 3: Documentation**
1. Add examples to docs
2. Update contributing guide
3. Publicize to team/users

### 9.2 Backward Compatibility

- Existing specs remain valid
- No changes to workflow engine
- `.cursorrules` is additive (no breaking changes)

---

## 10. Future Enhancements

### 10.1 Spec Creation Workflow
Create `create_spec_v1` workflow to guide spec creation:
- Templates for 5 files
- Prompts for each section
- Validation of completeness

### 10.2 Approval Tracking MCP Tool
```python
@mcp.tool()
def approve_spec(spec_name: str, approver: str) -> dict:
    """Record spec approval programmatically."""
    # Update spec README with approval
    # Log to approval database
    # Return approval record
```

### 10.3 Spec Linting
Validate spec structure:
- All 5 files present
- Required metadata in README
- Tasks have acceptance criteria

---

## 11. Security Considerations

### 11.1 Approval Authenticity
- Currently: Trust-based (human says "approved")
- Future: Could integrate with Git commit signatures

### 11.2 Spec Tampering
- Git history tracks all changes
- Approval recorded in commit message

---

## 12. Open Questions

1. **Should trivial changes be logged?**
   - Currently: No formal tracking
   - Could add: Log all work in `.praxis-os/work-log.md`

2. **Should approval be recorded programmatically?**
   - Currently: Manual (status field in README)
   - Could add: MCP tool for approval tracking

3. **Should specs expire?**
   - Currently: No expiration
   - Could add: Stale spec detection (>30 days draft)

---

## 13. Success Metrics

### 13.1 Process Compliance
- % of implementations with approved specs
- Target: 100% for non-trivial changes

### 13.2 Quality Adherence
- % of PRs meeting baseline quality
- Target: 100%

### 13.3 Efficiency
- Average time from request to approval
- Target: <2 hours for simple specs, <1 day for complex

---

**Approval Status:** Draft - Pending Technical Review
