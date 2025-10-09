# Dynamic Workflow Engine & Session-Scoped Refactor

**Date:** 2025-10-06  
**Status:** Approved for Implementation  
**Priority:** High  
**Estimated Effort:** 2-3 days

---

## Executive Summary

This specification addresses a critical architectural gap in the Agent OS workflow engine: the inability to enforce workflow patterns for dynamically-generated phases. The current implementation successfully guides AI agents through Phase 0 of workflows, but loses enforcement at phase boundaries when content is dynamically sourced (e.g., from spec `tasks.md` files).

Additionally, this spec refactors the workflow engine from a stateless service pattern to a session-scoped object pattern, improving code quality, testability, and enabling natural implementation of dynamic workflow features.

---

## Problem Statement

**Issue 1: Workflow Enforcement Gap**

The `spec_execution_v1` workflow breaks down after Phase 0:
- ✅ Phase 0: Command language enforced, agents follow workflow
- ❌ Phase 1+: No command language, agents break out and implement directly
- Result: Workflow state shows "Phase 1" but implementation is 100% complete

**Root Cause:** Dynamic phases (1-N) are parsed from external source (`tasks.md`) without command language wrapper. RAG returns raw spec content instead of template-wrapped enforcement.

**Issue 2: Architectural Debt**

The workflow engine uses a stateless service pattern where `session_id` is passed to every method:
- `workflow_engine.get_current_phase(session_id)`
- `workflow_engine.get_task(session_id, phase, task_number)`
- `workflow_engine.complete_phase(session_id, phase, evidence)`

This creates:
- Parameter pollution (session_id everywhere)
- Difficult to add session-scoped features (like dynamic content)
- Poor encapsulation (session state external to session logic)
- Harder to test (must mock multiple layers)

---

## Solution Overview

### Dynamic Workflow Support

Add template-based rendering system for workflows marked `dynamic_phases: true` in `metadata.json`:

1. **Template Loading:** Load phase/task templates from workflow directory
2. **Source Parsing:** Parse external source (e.g., spec's `tasks.md`) into structured data
3. **Template Rendering:** Merge parsed data with templates containing command language
4. **Session Registry:** Cache rendered content per session for performance

**Result:** All phase/task content includes command language enforcement, preventing workflow breakout.

### Session-Scoped Architecture

Refactor to session-scoped pattern:

```python
# Before (stateless service)
workflow_engine.get_current_phase(session_id)

# After (session-scoped)
session = workflow_engine.get_session(session_id)
session.get_current_phase()  # Clean!
```

**Benefits:**
- Natural place for dynamic content registry
- Better encapsulation and testability
- Cleaner API (no session_id pollution)
- Easier to extend with session-specific features

---

## Business Impact

### Without This Fix

- **Workflow Enforcement:** Only 50% effective (Phase 0 only)
- **Evidence Collection:** Incomplete (agents skip checkpoints)
- **Quality Assurance:** Inconsistent (some agents follow, some don't)
- **Audit Trail:** Inaccurate (workflow state doesn't reflect reality)
- **Trust:** Low (workflows provide guidance, not enforcement)

### With This Fix

- **Workflow Enforcement:** 85%+ effective (all phases)
- **Evidence Collection:** Complete (all checkpoints enforced)
- **Quality Assurance:** Consistent (all agents follow workflow)
- **Audit Trail:** Accurate (state matches implementation)
- **Trust:** High (workflows reliably guide execution)
- **Architecture:** Clean, testable, extensible

---

## Scope

### In Scope

1. **Dynamic Content Registry** - Session-scoped cache for rendered templates
2. **Template Rendering System** - Merge source data with command language templates
3. **Source Parsers** - Parse `tasks.md` (extensible for other sources)
4. **Session-Scoped Refactor** - `WorkflowSession` class with lifecycle management
5. **Workflow Engine Integration** - Detect dynamic workflows, use appropriate path
6. **Testing** - Unit and integration tests for new components
7. **Documentation** - Architecture guide, usage examples

### Out of Scope

1. **New Workflows** - Only infrastructure, not new workflow types
2. **MCP API Changes** - No breaking changes to tool signatures
3. **StateManager Refactor** - Keep existing persistence layer
4. **UI/Visualization** - Command-line only
5. **Performance Optimization** - Functional first, optimize later if needed

---

## Success Criteria

- [ ] Phase 0 → Phase 1 transition includes command language enforcement
- [ ] `get_task()` returns template-wrapped content with enforcement symbols
- [ ] AI agents CANNOT break out of workflow after Phase 0
- [ ] All phase checkpoints enforced through completion
- [ ] Backward compatibility maintained (existing workflows unchanged)
- [ ] Unit test coverage ≥ 80% for new components
- [ ] Integration test validates end-to-end enforcement
- [ ] Session memory usage < 5 MB per active session
- [ ] Template rendering latency < 100ms first access, < 5ms cached
- [ ] All existing workflows (test_generation_v3, production_code_v2) still work

---

## Deliverables

1. **Code Components**
   - `core/dynamic_registry.py` - Dynamic content management
   - `core/parsers.py` - Source parsers (tasks.md, extensible)
   - `core/session.py` - `WorkflowSession` class
   - Updated `workflow_engine.py` - Session factory and integration
   - Updated `workflow_tools.py` - Use session-scoped API

2. **Tests**
   - Unit tests for registry, parsers, session
   - Integration test for dynamic workflow enforcement
   - Backward compatibility test suite

3. **Documentation**
   - Architecture guide (this spec)
   - Dynamic workflow creation guide
   - API migration guide for session-scoped pattern

4. **Supporting Documents**
   - Bug report with evidence
   - Detailed architecture design
   - Implementation patterns

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing workflows | High | Maintain backward compatibility via detection |
| Performance degradation | Medium | Lazy rendering, caching, profiling |
| Complexity increase | Medium | Clear separation of concerns, good docs |
| Memory leaks (session cleanup) | Medium | Explicit cleanup on workflow completion |
| Template parsing errors | Low | Robust error handling, validation |

---

## Dependencies

- Existing workflow engine infrastructure
- MCP server models (WorkflowState, PhaseArtifact, etc.)
- RAG engine for static workflow content
- StateManager for session persistence

---

## Timeline

**Total Effort:** 2-3 days (16-24 hours)

| Phase | Effort | Deliverables |
|-------|--------|--------------|
| Phase 1: Core Infrastructure | 6-8 hours | Dynamic registry, parsers, models |
| Phase 2: Session Refactor | 4-6 hours | WorkflowSession class, factory |
| Phase 3: Integration | 3-4 hours | Workflow engine integration |
| Phase 4: Testing & Validation | 3-6 hours | Tests, validation, bug fixes |

---

## Related Documents

- [Bug Report](WORKFLOW_ENFORCEMENT_BUG_REPORT.md) - Detailed evidence of enforcement gap
- [Architecture Design](DYNAMIC_WORKFLOW_ARCHITECTURE.md) - Comprehensive technical design
- [spec_execution_v1 Workflow](../../workflows/spec_execution_v1/) - The workflow this fixes

---

## Approval

This spec was created through dogfooding: attempting to use `spec_execution_v1` to implement the MCP server modular redesign revealed the workflow enforcement gap. This is a critical fix to make workflows production-ready.

**Approved by:** Josh (via architectural review)  
**Implementation Method:** Use `spec_execution_v1` workflow (dogfooding!)

---

**Next Step:** Review this spec, then start implementation via `start_workflow("spec_execution_v1", ".agent-os/specs/2025-10-06-dynamic-workflow-session-refactor")`
