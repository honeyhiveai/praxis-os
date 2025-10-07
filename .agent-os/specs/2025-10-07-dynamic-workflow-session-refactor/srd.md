# Software Requirements Document (SRD)
## Dynamic Workflow Engine & Session-Scoped Refactor

**Date:** 2025-10-06  
**Version:** 1.0  
**Status:** Approved

---

## 1. Introduction

### 1.1 Purpose

This document specifies the requirements for extending the Agent OS workflow engine to support dynamically-generated workflow content and refactoring to a session-scoped architecture.

### 1.2 Scope

The system shall:
- Support workflows with dynamic phase/task content sourced from external files
- Enforce command language and validation gates across all phases
- Refactor workflow engine to session-scoped object pattern
- Maintain 100% backward compatibility with existing workflows
- Provide extensible architecture for future workflow types

### 1.3 Stakeholders

- **AI Agents:** Primary users of workflows, need reliable enforcement
- **Workflow Authors:** Create reusable workflow frameworks
- **Agent OS Developers:** Maintain and extend workflow engine
- **End Users:** Benefit from consistent, high-quality AI output

---

## 2. Goals & Objectives

### 2.1 Primary Goals

1. **Enforce Workflow Patterns:** AI agents must follow workflow guidance through all phases, not just Phase 0
2. **Enable Dynamic Workflows:** Support workflows where phase/task content comes from external sources
3. **Improve Architecture:** Clean, testable, extensible session-scoped design
4. **Maintain Compatibility:** Zero breaking changes for existing workflows

### 2.2 Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Workflow Enforcement Rate | 50% (Phase 0 only) | 85%+ (all phases) | Command language compliance audit |
| Checkpoint Completion Rate | 60% | 95%+ | Evidence submission tracking |
| Code Test Coverage | ~60% | 80%+ | pytest coverage report |
| Session Memory Usage | N/A | < 5 MB/session | Runtime profiling |
| Template Render Latency | N/A | < 100ms (first), < 5ms (cached) | Performance benchmarks |

---

## 3. Functional Requirements

### FR-1: Dynamic Content Registry

**Priority:** Critical  
**Description:** System shall maintain session-scoped registry of dynamically-generated workflow content.

**Requirements:**
- FR-1.1: Registry shall be keyed by session_id
- FR-1.2: Registry shall support multiple concurrent sessions
- FR-1.3: Registry shall cache parsed source data per session
- FR-1.4: Registry shall cache rendered templates per session
- FR-1.5: Registry shall clean up on session completion
- FR-1.6: Registry shall detect workflows with `dynamic_phases: true` in metadata

### FR-2: Template System

**Priority:** Critical  
**Description:** System shall render phase/task templates with command language enforcement.

**Requirements:**
- FR-2.1: System shall load templates from workflow directory
- FR-2.2: Templates shall contain command language symbols (🛑, 🎯, ⚠️, 📊, 🚨)
- FR-2.3: System shall support placeholder substitution in templates
- FR-2.4: System shall render templates on-demand (lazy)
- FR-2.5: System shall cache rendered content for performance
- FR-2.6: System shall validate template structure on load

### FR-3: Source Parsing

**Priority:** Critical  
**Description:** System shall parse external sources into structured phase/task data.

**Requirements:**
- FR-3.1: System shall parse Agent OS spec `tasks.md` format
- FR-3.2: Parser shall extract phase headers, names, descriptions
- FR-3.3: Parser shall extract task lists with acceptance criteria
- FR-3.4: Parser shall extract validation gates per phase
- FR-3.5: Parser shall extract dependencies between tasks
- FR-3.6: Parser shall validate source structure and report errors
- FR-3.7: System shall support extensible parser registry for future source types

### FR-4: Session-Scoped Architecture

**Priority:** High  
**Description:** System shall use session-scoped objects instead of stateless service pattern.

**Requirements:**
- FR-4.1: System shall provide `WorkflowSession` class encapsulating session logic
- FR-4.2: WorkflowEngine shall act as session factory
- FR-4.3: WorkflowSession shall own session_id, workflow_type, and state
- FR-4.4: WorkflowSession shall have methods: get_current_phase(), get_task(), complete_phase()
- FR-4.5: WorkflowSession shall manage dynamic content registry if applicable
- FR-4.6: WorkflowSession shall clean up resources on completion

### FR-5: Workflow Engine Integration

**Priority:** Critical  
**Description:** System shall integrate dynamic content with existing workflow engine.

**Requirements:**
- FR-5.1: Engine shall detect dynamic workflows via metadata.json
- FR-5.2: Engine shall initialize dynamic registry on workflow start
- FR-5.3: Engine shall return template-wrapped content for dynamic phases
- FR-5.4: Engine shall return RAG content for static workflows (unchanged)
- FR-5.5: Engine shall use dynamic content for get_phase and get_task when applicable
- FR-5.6: Engine shall clean up dynamic registry on workflow completion

### FR-6: Command Language Enforcement

**Priority:** Critical  
**Description:** Dynamically-generated content shall include command language enforcement.

**Requirements:**
- FR-6.1: Phase content shall include 🛑 EXECUTE-NOW for mandatory actions
- FR-6.2: Phase content shall include 🎯 NEXT-MANDATORY for routing
- FR-6.3: Phase content shall include 🛑 VALIDATE-GATE for checkpoints
- FR-6.4: Phase content shall include 🚨 FRAMEWORK-VIOLATION warnings
- FR-6.5: Task content shall enforce production code checklist
- FR-6.6: Task content shall enforce horizontal scaling (one task at a time)

### FR-7: Error Handling

**Priority:** High  
**Description:** System shall handle errors gracefully with clear feedback.

**Requirements:**
- FR-7.1: System shall return structured errors for parse failures
- FR-7.2: System shall return helpful hints for common errors
- FR-7.3: System shall validate source files exist before parsing
- FR-7.4: System shall validate template files exist before rendering
- FR-7.5: System shall handle missing phases/tasks gracefully
- FR-7.6: System shall log errors with context for debugging

---

## 4. Non-Functional Requirements

### NFR-1: Performance

- NFR-1.1: Template rendering shall complete in < 100ms (first access)
- NFR-1.2: Cached content retrieval shall complete in < 5ms
- NFR-1.3: Source parsing shall complete in < 500ms for typical spec
- NFR-1.4: Session memory overhead shall be < 5 MB per active session
- NFR-1.5: System shall support 10+ concurrent sessions

### NFR-2: Reliability

- NFR-2.1: System shall have 0 memory leaks (sessions cleaned up)
- NFR-2.2: System shall have 0 regressions in existing workflows
- NFR-2.3: System shall validate all templates on load
- NFR-2.4: System shall fail fast with clear errors

### NFR-3: Maintainability

- NFR-3.1: Code shall have ≥ 80% test coverage
- NFR-3.2: All public APIs shall have Sphinx-style docstrings
- NFR-3.3: Code shall follow production code checklist
- NFR-3.4: Architecture shall be documented with diagrams
- NFR-3.5: Error messages shall be actionable

### NFR-4: Extensibility

- NFR-4.1: Parser system shall support new source types via registry
- NFR-4.2: Template system shall support custom template syntax
- NFR-4.3: Dynamic registry shall support custom rendering logic
- NFR-4.4: Session architecture shall support session-specific extensions

### NFR-5: Backward Compatibility

- NFR-5.1: Existing workflows (test_generation_v3, production_code_v2) shall work unchanged
- NFR-5.2: MCP tool signatures shall remain unchanged
- NFR-5.3: StateManager interface shall remain unchanged
- NFR-5.4: Workflow state format shall remain compatible

---

## 5. User Stories

### US-1: Dynamic Workflow Execution (AI Agent)

**As an** AI agent  
**I want to** execute a spec-driven workflow with enforcement  
**So that** I follow the spec design systematically with quality gates

**Acceptance Criteria:**
- Agent starts spec_execution_v1 workflow
- Agent completes Phase 0 (spec analysis)
- Agent receives Phase 1 content with command language
- Agent is directed to call get_task() for each task
- Agent cannot skip validation gates
- Agent submits evidence to advance phases
- Workflow state accurately reflects progress

### US-2: Static Workflow Execution (AI Agent)

**As an** AI agent  
**I want to** execute existing workflows without disruption  
**So that** my current workflows continue to work

**Acceptance Criteria:**
- Agent starts test_generation_v3 workflow
- Agent receives content from RAG (existing behavior)
- All phases work as before
- No performance degradation
- No new errors or warnings

### US-3: Workflow Creation (Workflow Author)

**As a** workflow author  
**I want to** create dynamic workflows with templates  
**So that** content comes from external sources but includes enforcement

**Acceptance Criteria:**
- Author creates workflow directory
- Author adds metadata.json with dynamic_phases: true
- Author creates phase-template.md and task-template.md
- Author specifies source type and parser
- Workflow engine automatically uses templates
- AI agents receive enforced content

### US-4: Debugging Workflow Execution (Developer)

**As a** developer  
**I want to** debug workflow execution issues  
**So that** I can fix problems quickly

**Acceptance Criteria:**
- Clear error messages for parse failures
- Helpful hints for common issues
- Logs show source, template, and rendered content
- Can inspect session state
- Can trace template rendering

### US-5: Session Management (Developer)

**As a** developer  
**I want to** work with session-scoped objects  
**So that** code is cleaner and easier to test

**Acceptance Criteria:**
- Can create WorkflowSession instances
- Session methods don't require session_id parameter
- Can mock sessions for testing
- Sessions clean up resources automatically
- Clear lifecycle management

---

## 6. Constraints

### Technical Constraints

- Must maintain Python 3.9+ compatibility
- Must use existing MCP protocol (no breaking changes)
- Must integrate with existing StateManager
- Must work with current RAGEngine
- Must preserve workflow state format

### Resource Constraints

- Implementation: 2-3 days
- Memory: < 5 MB per session
- Performance: No noticeable degradation

### Organizational Constraints

- No breaking changes to existing workflows
- Must be testable without external dependencies
- Must follow Agent OS coding standards
- Must include comprehensive documentation

---

## 7. Assumptions & Dependencies

### Assumptions

- Spec `tasks.md` files follow standard format
- Templates use simple placeholder syntax
- Sessions are short-lived (< 1 week)
- Concurrent sessions < 50

### Dependencies

- **Internal:**
  - workflow_engine.py
  - state_manager.py
  - rag_engine.py
  - models/workflow.py

- **External:**
  - Python 3.9+
  - pathlib, dataclasses (stdlib)
  - typing (stdlib)

---

## 8. Validation & Acceptance

### Validation Criteria

1. **Unit Tests:** All new components have ≥ 80% coverage
2. **Integration Test:** End-to-end dynamic workflow execution
3. **Backward Compat Test:** All existing workflows pass
4. **Performance Test:** Rendering latency within targets
5. **Memory Test:** No leaks, usage within targets

### Acceptance Process

1. Developer implements per spec
2. All tests pass
3. Code review confirms quality standards
4. Performance benchmarks meet targets
5. Documentation complete
6. Demo with spec_execution_v1 workflow

---

## 9. Future Enhancements (Out of Scope)

- Visual workflow editor
- Workflow analytics dashboard
- Multi-user collaboration
- Cloud-based workflow execution
- AI-powered workflow optimization
- Custom template language (beyond simple placeholders)

---

**Document prepared by:** AI Agent (via dogfooding)  
**Reviewed by:** Josh  
**Approved:** 2025-10-06
