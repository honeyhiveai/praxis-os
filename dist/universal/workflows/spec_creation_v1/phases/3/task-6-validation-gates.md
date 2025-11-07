# Task 5: Define Validation Gates

**Phase:** 3 (Task Breakdown)  
**Purpose:** Add phase-level validation checkpoints  
**Estimated Time:** 8 minutes

---

## 🎯 Objective

Define validation gates for each phase. Gates ensure quality and completeness before proceeding, preventing issues from cascading to later phases.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1-4 must be completed

- All phases, tasks, and dependencies must be defined

⚠️ MUST-READ: Reference template

See `core/tasks-template.md` for validation gate patterns.

---

## Steps

### Step 1: Add Phase Validation Gates

For each phase in tasks.md, add a validation section:

```markdown
## Phase {N} Validation Gate

Before advancing to Phase {N+1}:
- [ ] All tasks in Phase {N} completed ✅/❌
- [ ] All acceptance criteria met ✅/❌
- [ ] All tests passing ✅/❌
- [ ] No linting errors ✅/❌
- [ ] Code reviewed ✅/❌
- [ ] Documentation updated ✅/❌
```

### Step 2: Add Phase-Specific Criteria

Tailor gates to phase purpose. Examples from `core/tasks-template.md`:

**Setup Phase:**
```markdown
- [ ] Directory structure created
- [ ] Configuration files valid
- [ ] Database accessible
- [ ] Dependencies installed
```

**Implementation Phase:**
```markdown
- [ ] All components implemented
- [ ] Unit tests >80% coverage
- [ ] Integration tests passing
- [ ] APIs documented
```

**Testing Phase:**
```markdown
- [ ] All test suites passing
- [ ] Coverage targets met
- [ ] Performance benchmarks met
- [ ] Security scan clean
```

**Deployment Phase:**
```markdown
- [ ] Deployment scripts tested
- [ ] Monitoring configured
- [ ] Documentation complete
- [ ] Stakeholders notified
```

### Step 3: Define Exit Criteria

For each phase: tasks complete, no blockers, quality gates passed, ready for next phase.

### Step 4: Add Overall Summary

```markdown
## Acceptance Criteria Summary
[List high-level criteria for each phase]

## Project Completion
- [ ] All phases + validation gates passed
- [ ] Production deployment successful
- [ ] Documentation complete
```

### Step 5: Validate Gate Quality

Check each gate: objective, comprehensive, achievable, blocking.

📊 COUNT-AND-DOCUMENT: Phase gates [number], criteria per gate [avg], total [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] All phases have validation gates ✅/❌
- [ ] Gates are specific and measurable ✅/❌
- [ ] Exit criteria defined for each phase ✅/❌
- [ ] Overall acceptance criteria summary added ✅/❌
- [ ] Project completion criteria defined ✅/❌

---

## Phase 3 Completion

🎯 PHASE-COMPLETE: Task breakdown complete

This phase is complete when tasks.md contains:
- ✅ Implementation phases clearly defined with purpose
- ✅ All tasks broken down with specific action items
- ✅ Acceptance criteria for each task (measurable outcomes)
- ✅ Dependencies mapped between tasks (what blocks what)
- ✅ Validation gates specified for each phase
- ✅ Time estimates provided for effort planning

Submit checkpoint evidence to advance to Phase 4 (Implementation Guidance) where you'll document code patterns and testing strategies.
