# Workflow Breadcrumb Navigation System

**Status:** Review  
**Date:** 2025-11-08  
**Priority:** High  
**Category:** Enhancement

---

## Executive Summary

This specification defines a "breadcrumb trail" navigation pattern for praxis-os workflows that guides AI agents through sequential execution by making the correct path the easiest path. The system removes early information disclosure and provides explicit next-action instructions, increasing workflow compliance from 99% to 99.9%.

**Problem:** Outlier AI agents bypass workflow steps by reading full phase content from `start_workflow` responses, skipping `get_phase` and `get_task` actions, and submitting fabricated evidence to `complete_phase`.

**Solution:** Remove `phase_content` from `start_workflow` responses (just-in-time disclosure) and add action-specific breadcrumbs (`⚡_NEXT_ACTION`) positioned at the end of responses (recency bias), guiding AIs step-by-step through workflows.

**Business Impact:**
- **Reliability**: 99.9% engagement rate (from 99%)
- **Observability**: Track breadcrumb following rates across AI models
- **Backward Compatibility**: 100% non-breaking for existing workflows

---

## Document Index

### 1. [srd.md](srd.md) - Software Requirements Document
**Purpose:** Business goals, user stories, and functional requirements

**Key Sections:**
- Business Goals: Maximize deterministic AI behavior, preserve compliant AI experience, enable behavioral observation
- User Stories: 4 stories (Critical: AI Agent Guided, Outlier AI Prevented; High: Compliant AI Not Disrupted; Medium: Human Developer Observing)
- Functional Requirements: 10 requirements (FR-001 through FR-010) covering just-in-time disclosure, action-specific breadcrumbs, task count retrieval, backward compatibility
- Non-Functional Requirements: Performance (<5ms task count, <1ms breadcrumb), Maintainability (KISS principle), Backward Compatibility (100%), Usability (literal syntax), Reliability (graceful degradation), Observability (behavioral metrics)
- Out of Scope: Task-level evidence validation, preventing direct file reading, A/B testing, configurable emojis

**Stats:**
- 571 lines
- 10 functional requirements
- 6 non-functional requirement categories
- 4 user stories

---

### 2. [specs.md](specs.md) - Technical Specifications
**Purpose:** Architecture, components, APIs, data models, security, and performance

**Key Sections:**
- Architecture Overview: Behavioral Probability Engineering pattern, architectural decisions, technology stack, requirements traceability
- Component Design: 3 components (Workflow Guidance Module, Task Count Retrieval, Breadcrumb Generation Logic)
- API Design: Internal interfaces (`add_workflow_guidance`, `get_task_count`, `_get_task_count_for_phase`), DTOs, error handling, contract guarantees
- Data Models: Ephemeral breadcrumb structure, workflow state/metadata, computed task count, response structure evolution
- Security Design: Input validation, authorization, data protection, code security
- Performance Design: Task count retrieval (<5ms static, <1ms dynamic), breadcrumb generation (<1ms), end-to-end impact (<1% increase), memory footprint (~200 bytes/breadcrumb)

**Stats:**
- 3034 lines
- 3 components modified
- 3 new internal methods
- 4 action handlers modified
- Performance targets: <5ms, <1ms, <1%

---

### 3. [tasks.md](tasks.md) - Implementation Task Breakdown
**Purpose:** Phased implementation plan with tasks, dependencies, and validation gates

**Key Sections:**
- Time Estimates: 9-13 hours total (~1.5-2 days)
- Phase 1: Foundation Changes (1-2h) - Modify `add_workflow_guidance` for optional breadcrumb parameter
- Phase 2: Task Count Infrastructure (2-3h) - Add task count retrieval for static and dynamic workflows
- Phase 3: Breadcrumb Generation (3-4h) - Modify 4 action handlers to generate action-specific breadcrumbs
- Phase 4: Testing & Validation (3-4h) - Unit, integration, performance, and behavioral tests
- Dependencies: Phase dependencies (linear), task dependencies (linear, parallel, cross-phase), critical path (5.5 hours)
- Phase Validation Gates: 4 phase gates with specific criteria, project completion criteria

**Stats:**
- 332 lines
- 4 implementation phases
- 14 implementation tasks
- 4 validation gates
- 9-13 hour estimate

---

### 4. [implementation.md](implementation.md) - Implementation Guidance
**Purpose:** Code patterns, testing strategy, deployment, and troubleshooting

**Key Sections:**
- Implementation Philosophy: 5 core principles (Simplicity, Backward Compatibility, Behavioral Probability Engineering, Graceful Degradation, Test-Driven Validation)
- Implementation Order: Phased approach (Foundation → Task Count → Breadcrumbs → Testing)
- Code Patterns: 7 patterns with examples (Optional Parameter, Graceful Error Handling, Dynamic Routing, Just-In-Time Disclosure, Position-Aware Breadcrumbs, Emoji Field Names, Graceful Degradation)
- Common Pitfalls: 3 anti-patterns (Training Data vs. Project Standards, Premature Optimization, Breaking Backward Compatibility)
- File Modification Checklist: 3 files modified (`guidance.py`, `workflow_renderer.py`, `engine.py`)
- Testing Strategy: 18 tests (14 unit, 2 integration, 2 performance, 1 behavioral validation), 100% FR coverage
- Deployment Guidance: Pre-deployment checklist, deployment steps, monitoring (5 key metrics), troubleshooting (3 common issues), rollback strategy

**Stats:**
- 1129 lines
- 7 code patterns
- 7 anti-patterns
- 18 tests planned
- 5 monitoring metrics

---

## Quick Start by Role

### For Product Managers
**Start here:** [srd.md](srd.md)

Read:
1. Section 2: Business Goals (understand success metrics)
2. Section 3: User Stories (understand user needs)
3. Section 4: Functional Requirements (understand scope)

**Key Takeaway:** This feature increases workflow compliance from 99% to 99.9% by guiding AI agents step-by-step, preventing task skipping.

---

### For Architects
**Start here:** [specs.md](specs.md)

Read:
1. Section 1: Architecture Overview (understand pattern and decisions)
2. Section 2: Component Design (understand 3 modified components)
3. Section 3: API Design (understand internal interfaces)
4. Section 6: Performance Design (understand targets: <5ms, <1ms)

**Key Takeaway:** Behavioral Probability Engineering pattern - make correct path easiest path through response structure (just-in-time disclosure + recency bias positioning).

---

### For Developers
**Start here:** [implementation.md](implementation.md)

Read:
1. Section 3: Code Patterns (7 patterns with examples)
2. Section 4: Common Pitfalls (avoid anti-patterns)
3. Section 5: File Modification Checklist (know what to change)
4. Section 7: Testing Strategy (18 tests to implement)

Then refer to:
- [tasks.md](tasks.md) for step-by-step implementation order
- [specs.md](specs.md) for detailed API specifications

**Key Takeaway:** 3 files modified, 7 patterns to follow, 18 tests to write. Estimated 9-13 hours (~1.5-2 days).

---

### For QA Engineers
**Start here:** [implementation.md](implementation.md) Section 7

Read:
1. Section 7.2: Unit Test Plan (14 tests across 4 test files)
2. Section 7.3: Integration Test Plan (2 comprehensive workflow tests)
3. Section 7.4: Performance Test Plan (2 benchmark tests)
4. Section 7.5: Manual Behavioral Validation (breadcrumb following rate >95%)

Then refer to:
- [srd.md](srd.md) Section 4 for testable requirements
- [tasks.md](tasks.md) for acceptance criteria per task

**Key Takeaway:** 100% FR coverage (all 10 functional requirements tested), performance benchmarks (<5ms, <1ms), behavioral validation (>95% following rate).

---

### For DevOps/SRE
**Start here:** [implementation.md](implementation.md) Section 8

Read:
1. Section 8.2: Pre-Deployment Checklist
2. Section 8.3: Deployment Steps (staging → production)
3. Section 8.6: Monitoring (5 key metrics)
4. Section 8.7: Troubleshooting (3 common issues)
5. Section 8.5: Rollback Strategy

**Key Takeaway:** Low-risk deployment (code-only, backward compatible, no migrations). Monitor 5 metrics (engagement rate, breadcrumb following, action duration, task count performance, error rate).

---

## Key Metrics

### Requirements Coverage
- **Functional Requirements**: 10 (FR-001 through FR-010)
- **Non-Functional Requirements**: 6 categories (Performance, Maintainability, Backward Compatibility, Usability, Reliability, Observability)
- **Out of Scope**: 6 items explicitly excluded
- **User Stories**: 4 stories (2 Critical, 1 High, 1 Medium)

### Implementation Scope
- **Files Modified**: 3 (`guidance.py`, `workflow_renderer.py`, `engine.py`)
- **New Methods**: 3 (`get_task_count`, `_get_task_count_for_phase`, modified `add_workflow_guidance`)
- **Action Handlers Modified**: 4 (`start_workflow`, `get_phase`, `get_task`, `complete_phase`)
- **Implementation Phases**: 4 phases (Foundation, Task Count, Breadcrumbs, Testing)
- **Total Tasks**: 14 implementation tasks
- **Estimated Time**: 9-13 hours (~1.5-2 days)

### Testing Coverage
- **Unit Tests**: 14 tests across 4 test files
- **Integration Tests**: 2 comprehensive workflow tests
- **Performance Tests**: 2 benchmark tests
- **Behavioral Validation**: 1 manual test
- **Requirements Coverage**: 100% (all 10 FRs have ≥1 test)
- **Test Coverage Target**: ≥90% for modified code

### Performance Targets
- **Task Count Retrieval (Static)**: <5ms for <50 files
- **Task Count Retrieval (Dynamic)**: <1ms (cached lookup)
- **Breadcrumb Generation**: <1ms per action
- **End-to-End Impact**: <1% increase in workflow execution time
- **Memory Footprint**: ~200 bytes per breadcrumb (~800 bytes per workflow)

### Success Metrics
- **Engagement Rate**: 99% → 99.9% (target)
- **Breadcrumb Following Rate**: 0% → >95% (target)
- **Evidence Validation Failure Rate**: <5% (no increase)
- **Backward Compatibility**: 100% (no breaking changes)
- **Error Rate**: No increase (≤2x baseline alert threshold)

---

## Design Principles

### 1. Behavioral Probability Engineering
**Philosophy:** Design systems to heavily weight the probability of desired AI behaviors.

**Application:** Make the correct execution path (sequential: `start_workflow` → `get_phase` → `get_task` → `complete_phase`) the highest-probability decision by:
- Removing early information (just-in-time disclosure)
- Positioning guidance last (recency bias)
- Providing literal call syntax (copy-paste executable)

**Analogy:** Like managing ADHD - create structured constraints that make the right path the easiest path.

---

### 2. Just-In-Time Information Disclosure
**Philosophy:** Reveal only the next step, never the full path.

**Application:** Remove `phase_content` from `start_workflow` responses, forcing AI agents to call `get_phase` to retrieve phase information. Prevents information leakage that enables bypassing.

**Trade-off:** One extra MCP call per workflow (negligible for performance-conscious AIs).

---

### 3. Recency Bias Positioning
**Philosophy:** Last information seen has highest attention weight.

**Application:** Position breadcrumbs (`⚡_NEXT_ACTION`) at the end of response dictionaries using Python 3.7+ dict ordering. Ensures AI agents see explicit next action after reading all context.

**Implementation:** `response.update(breadcrumb)` after merging static guidance and response content.

---

### 4. Graceful Degradation
**Philosophy:** Breadcrumb failures never break workflows.

**Application:** All breadcrumb generation wrapped in try/except, logging errors but continuing execution. If task count fails, breadcrumb is `None` and workflow proceeds without guidance (backward compatible).

**Risk Mitigation:** Breadcrumb absence doesn't affect workflow completion (phase gates remain the ultimate enforcement).

---

### 5. Backward Compatibility
**Philosophy:** Preserve existing behavior for 99% of compliant AIs.

**Application:** Optional `breadcrumb=None` parameter in `add_workflow_guidance()`, preserving existing callers. No changes to workflow state format, evidence validation, or API contracts.

**Success Criteria:** 100% of existing workflow sessions continue to work without modification.

---

## Next Steps

### 1. Review & Approval
- [ ] Product Manager reviews [srd.md](srd.md) for business goals alignment
- [ ] Architect reviews [specs.md](specs.md) for technical soundness
- [ ] Tech Lead reviews [tasks.md](tasks.md) for implementation feasibility
- [ ] Dev Team reviews [implementation.md](implementation.md) for code patterns clarity

### 2. Implementation
- [ ] Assign to developer (estimated 9-13 hours, ~1.5-2 days)
- [ ] Follow phased approach in [tasks.md](tasks.md):
  - Phase 1: Foundation Changes (1-2h)
  - Phase 2: Task Count Infrastructure (2-3h)
  - Phase 3: Breadcrumb Generation (3-4h)
  - Phase 4: Testing & Validation (3-4h)
- [ ] Verify all validation gates passed before advancing phases

### 3. Testing
- [ ] QA implements 18 tests from [implementation.md](implementation.md) Section 7
- [ ] Run test suite: `pytest ouroboros/subsystems/workflow/tests/`
- [ ] Verify test coverage ≥90%
- [ ] Run performance benchmarks (<5ms task count, <1ms breadcrumb)
- [ ] Manual behavioral validation (>95% breadcrumb following rate)

### 4. Deployment
- [ ] Deploy to staging (follow [implementation.md](implementation.md) Section 8.3)
- [ ] Smoke test on staging (run workflow end-to-end)
- [ ] Monitor 5 key metrics (Section 8.6)
- [ ] Deploy to production
- [ ] Monitor for 24 hours post-deployment

### 5. Observability
- [ ] Add workflow breadcrumb metrics to dashboard
- [ ] Track engagement rate (target: 99.9%)
- [ ] Track breadcrumb following rate (target: >95%)
- [ ] Track performance (task count <5ms, breadcrumb <1ms)
- [ ] Analyze behavioral patterns across AI models

---

## Questions & Support

### Common Questions

**Q: Why not just block file reading entirely?**  
A: We can't prevent AI agents from reading workflow files on disk (they have filesystem access). Instead, we make the MCP interface more attractive through better UX (explicit guidance) and easier execution (copy-paste syntax).

**Q: What if breadcrumb generation fails?**  
A: Graceful degradation - workflows continue without breadcrumbs (backward compatible). Error logged for debugging.

**Q: Will this affect performance?**  
A: Negligible impact (<1% increase). Task count retrieval <5ms, breadcrumb generation <1ms. One extra `get_phase` call adds ~20ms total.

**Q: Can AIs still skip steps?**  
A: Technically yes (they can read files directly), but breadcrumbs make sequential execution the highest-probability decision. Phase gates remain the ultimate enforcement.

**Q: Is this backward compatible?**  
A: Yes - 100%. Existing workflows work unchanged. Breadcrumb parameter is optional. No breaking changes to APIs or state format.

---

### Support Resources

- **Design Document**: See `supporting-docs/2025-11-08-workflow-breadcrumb-navigation.md` for detailed design rationale
- **Code Intelligence**: Use `pos_search_project(action="search_code", query="workflow engine breadcrumb")` for implementation details
- **Standards**: Query `pos_search_project(action="search_standards", query="workflow execution patterns")` for project conventions
- **MCP Server Logs**: `~/Library/Application Support/Cursor/logs/.../MCP*.log`

---

## Document History

**Version 1.0** (2025-11-08)
- Initial specification created via `spec_creation_v1` workflow
- 5 documents: README.md, srd.md, specs.md, tasks.md, implementation.md
- Total: 5637 lines across all documents
- Status: Review (pending approval)

---

**Specification Complete** ✅  
Ready for review and implementation.

