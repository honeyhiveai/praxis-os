# Tasks.md Template

Template for creating tasks.md during Phase 3 (Task Breakdown).

---

## Complete tasks.md Structure

```markdown
# Implementation Tasks

**Project:** {FEATURE_NAME}  
**Date:** {CURRENT_DATE}  
**Status:** Draft - Pending Approval

---

## Time Estimates

### Human Implementation (Traditional)
- **Phase 1:** {hours} ({description})
- **Phase 2:** {hours} ({description})
- **Total:** {hours} ({days})

### AI Agent + Human Orchestration (Agent OS Enhanced)
- **Phase 1:** {AI hours} AI work, {human minutes} human orchestration ({leverage}x)
- **Phase 2:** {AI hours} AI work, {human minutes} human orchestration ({leverage}x)
- **Total:** {AI hours} AI work, {human hours} human effort ({leverage}x leverage)

---

## Phase 1: {Phase Name}

**Objective:** {What this phase accomplishes}

**Estimated Duration:** {hours}

### Phase 1 Tasks

- [ ] **Task 1.1**: {Task name}
  - **Human Estimate:** {hours} ({S/M/L})
  - **AI Agent Estimate:** {AI hours} AI work, {human min} orchestration ({leverage}x)
  
  - {Action item}
  - {Action item}
  - Verify {verification}
  
  **Acceptance Criteria:**
  - [ ] {Criterion 1}
  - [ ] {Criterion 2}

- [ ] **Task 1.2**: {Task name}
  - **Human Estimate:** {hours} ({S/M/L})
  - **AI Agent Estimate:** {AI hours} AI work, {human min} orchestration ({leverage}x)
  
  - {Action item}
  
  **Acceptance Criteria:**
  - [ ] {Criterion}

---

## Phase 2: {Phase Name}

[Repeat structure]

---

## Dependencies

### Phase 1 → Phase 2
{Describe dependency}

---

## Risk Mitigation

### Risk: {Risk description}
**Mitigation:** {How to mitigate}

---

## Testing Strategy

### Unit Tests
- {What to test}

### Integration Tests
- {What to test}

---

## Acceptance Criteria Summary

### Phase 1
- [ ] {High-level criterion}

### Phase 2
- [ ] {High-level criterion}
```

---

## Task Format Guidelines

### Good Task Format

```markdown
- [ ] **Task 1.1**: Create database schema
  - **Human Estimate:** 4 hours (M)
  - **AI Agent Estimate:** 4 hours AI work, 12 min human orchestration (20x leverage)
  
  - Define tables for users, resources, tags
  - Add indexes for foreign keys and frequently queried columns
  - Create migration file with up/down migrations
  - Verify schema matches data models from specs.md
  
  **Acceptance Criteria:**
  - [ ] All tables created with correct columns and types
  - [ ] Foreign key constraints defined
  - [ ] Indexes created for performance
  - [ ] Migration runs successfully (up and down)
  - [ ] Schema documentation updated
```

**Why Good:**
- Dual time estimates (human vs AI agent)
- Shows leverage multiplier (20x)
- Specific action items
- Clear verification step
- Measurable acceptance criteria
- Traceable to specs.md

### Poor Task Format

```markdown
- [ ] **Task 1.1**: Setup database
  - Create database
  
  **Acceptance Criteria:**
  - [ ] Database works
```

**Why Bad:**
- Vague action items
- No verification
- Unmeasurable criteria
- Not actionable

---

## Acceptance Criteria Guidelines

### INVEST Criteria

**I**ndependent: Can be completed independently  
**N**egotiable: Details can be refined  
**V**aluable: Delivers clear value  
**E**stimable: Can be sized and estimated  
**S**mall: Fits in reasonable timeframe  
**T**estable: Has clear success criteria

### Good Acceptance Criteria

```markdown
**Acceptance Criteria:**
- [ ] All unit tests passing (>80% coverage)
- [ ] API endpoint responds within 200ms (p95)
- [ ] Error handling covers 5 identified edge cases
- [ ] Documentation includes 3 code examples
- [ ] Linter reports zero errors
```

**Why Good:** Specific, measurable, testable

### Poor Acceptance Criteria

```markdown
**Acceptance Criteria:**
- [ ] Code is done
- [ ] Tests exist
- [ ] Works well
```

**Why Bad:** Vague, not measurable

---

## Dependency Mapping

### Linear Dependencies

```
Phase 1 → Phase 2 → Phase 3
  ↓         ↓         ↓
Task 1.1  Task 2.1  Task 3.1
Task 1.2  Task 2.2  Task 3.2
```

### Parallel with Sync Points

```
Phase 1
├── Task 1.1 (parallel)
├── Task 1.2 (parallel)
└── Task 1.3 (depends on 1.1 + 1.2)
```

### Task-Level Dependencies

```markdown
- [ ] **Task 2.3**: Implement API endpoints
  - **Depends on:** Task 2.1 (data models), Task 2.2 (business logic)
```

---

## Time Estimation Guidelines

### Dual Estimation: Human vs AI Agent

Agent OS Enhanced requires **two time estimates** to show the leverage multiplier:

1. **Human Estimate** - Traditional human implementation time
2. **AI Agent Estimate** - Breakdown of AI execution and human orchestration

**Why both?** To demonstrate the 20-40x velocity multiplier that Agent OS provides.

---

### T-Shirt Sizing (Human Implementation Time)

- **Small (S):** 1-2 hours
- **Medium (M):** 2-4 hours
- **Large (L):** 4-8 hours
- **Extra Large (XL):** 8-16 hours (consider breaking down)

---

### Human Estimation Formula

```
Human Time = Base Time × Complexity Factor × Risk Factor

Base Time: How long if everything goes smoothly
Complexity: 1.0 (simple) to 2.0 (complex)
Risk: 1.0 (low) to 1.5 (high uncertainty)
```

**Example:**
```
Base: 2 hours (write code)
Complexity: 1.5 (moderate complexity)
Risk: 1.2 (some unknowns)
Human Time: 2 × 1.5 × 1.2 = 3.6 hours (round to 4 hours)
```

---

### AI Agent Estimation Formula

```
AI Implementation Time = Human Time × 0.8 to 1.2
  (AI typically similar speed, sometimes faster for parallel tasks,
   sometimes slower for complex reasoning/debugging)

Human Orchestration Time = AI Implementation Time × 0.03 to 0.10
  (Typically 3-10% of AI time for direction and review)

Total Human Effort = Human Orchestration Time
Leverage Multiplier = Human Time ÷ Human Orchestration Time
```

**Example:**
```
Human Time: 4 hours (from above)

AI Implementation Time: 4 × 1.0 = 4 hours
  (AI works continuously, no context switching)

Human Orchestration Time: 4 × 0.05 = 0.2 hours (12 minutes)
  (Initial direction: 5 min, review: 7 min)

Leverage: 4 hours ÷ 0.2 hours = 20x
  (Human saves 3.8 hours per task)
```

---

### Task Format with Dual Estimates

```markdown
- [ ] **Task 1.1**: Create database schema
  - **Human Estimate:** 4 hours (M)
  - **AI Agent Estimate:** 4 hours AI work, 12 min human orchestration (20x leverage)
  
  - Define tables for users, resources, tags
  - Add indexes for foreign keys and frequently queried columns
  - Create migration file with up/down migrations
  - Verify schema matches data models from specs.md
  
  **Acceptance Criteria:**
  - [ ] All tables created with correct columns and types
  - [ ] Foreign key constraints defined
  - [ ] Indexes created for performance
  - [ ] Migration runs successfully (up and down)
  - [ ] Schema documentation updated
```

---

### Estimation Guidelines by Task Type

| Task Type | Human Time | AI Multiplier | Orchestration % | Leverage |
|-----------|-----------|---------------|-----------------|----------|
| Boilerplate/Setup | 2-4h | 0.8x (faster) | 3% | 30-40x |
| Straightforward Logic | 2-6h | 1.0x (same) | 5% | 20x |
| Complex Algorithm | 4-8h | 1.2x (slower) | 8% | 10-15x |
| Debugging/Research | 4-12h | 1.5x (slower) | 10% | 7-10x |
| Documentation | 1-3h | 0.6x (faster) | 3% | 30-50x |

**Notes:**
- AI is **faster** for repetitive/boilerplate work (0.6-0.8x)
- AI is **similar speed** for standard implementation (1.0x)
- AI is **slower** for novel/complex problems requiring deep reasoning (1.2-1.5x)
- Human orchestration is **always small** (3-10% of AI time)
- **Leverage remains high** even when AI is slower (7-50x)

---

## Validation Gate Checklist

For each phase, include:

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

---

## Common Patterns

### Setup Phase (Usually Phase 1)

- Directory structure
- Configuration files
- Database setup
- Dependency installation

### Implementation Phase (Middle phases)

- Core functionality
- Business logic
- Data access
- API endpoints

### Testing Phase (Late phase)

- Unit tests
- Integration tests
- Performance tests
- Documentation

### Deployment Phase (Final phase)

- Deployment scripts
- Monitoring setup
- Documentation finalization
- Announcement/handoff
