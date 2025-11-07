# Ouroboros MCP Server (Clean Architecture Rewrite)

**Status:** Draft - Awaiting Review  
**Priority:** Critical  
**Category:** Ground-Up Rewrite  
**Date:** 2025-11-04

---

## Executive Summary

Ouroboros is a ground-up rewrite of the prAxIs OS MCP server with a mission-driven clean architecture centered on enabling praxis (knowledge compounding + behavioral reinforcement). The current `mcp_server` has deep architectural issues (30K LOC with coupling, external scripts, inconsistent behavioral engineering) that cannot be fixed via refactoring. Ouroboros builds the server correctly from day one with behavioral engineering as the PRIMARY mission, not a secondary feature.

**Key Benefits:**
- **Behavioral Engineering First:** Query prepends in 100% of searches (self-reinforcing loop functional)
- **Clean Architecture:** Mission-Driven Layered Architecture (Tools → Middleware → Subsystems → Foundation)
- **Zero Cross-Talk:** Subsystems fully isolated, no coupling
- **Config-Driven:** Add languages/features via YAML, not code changes
- **Fail-Fast Validation:** Invalid state crashes immediately with actionable remediation

---

## Quick Links

- **Requirements:** [srd.md](srd.md) (1,701 lines - 5 business goals, 10 user stories, 25 FRs, 44 NFRs)
- **Technical Design:** [specs.md](specs.md) (4,623 lines - architecture, 22 components, APIs, data models, security, performance)
- **Implementation Tasks:** [tasks.md](tasks.md) (1,028 lines - 8 phases, 31 tasks, dependencies, critical path)
- **Implementation Guide:** [implementation.md](implementation.md) (1,320 lines - 7 code patterns, testing strategy, deployment, troubleshooting)

---

## Overview

### What This Feature Does

Ouroboros replaces the existing `mcp_server` with a clean, behavioral-engineering-first architecture that makes AI agents systematically better at software development through continuous querying, knowledge compounding, and adversarial design. It provides semantic search (standards, code), structural search (AST), graph traversal (call graphs), phase-gated workflows, and browser automation—all wrapped in middleware that reinforces query-first behavior.

### Who It's For

- **Primary Users:** AI agents (Claude, GPT, etc.) working on praxis-os-enabled projects
- **Secondary Users:** Human developers (observability, debugging, extending the system)

### Success Metrics

- **Knowledge Compounding:** Standards growth >5 docs/month, specs referenced in 80%+ of decisions
- **Behavioral Reinforcement:** Query diversity >60% (3+ angles), query-to-implementation correlation >0.70, correction frequency decreases session-to-session
- **Adversarial Design:** Evidence validation enforced 100% (no hardcoded bypasses), zero `--no-verify` commits
- **Technical Quality:** <30s cold start, <200ms search latency (p95), ≥90% test coverage, 99.9% uptime

---

## Requirements Summary

### Business Goals

1. **Enable Praxis (Knowledge Compounding + Behavioral Reinforcement):** AI agents systematically improve across sessions via standards accumulation and query-first behavioral patterns
2. **Deliver Production-Grade RAG Architecture:** Multi-index search (standards, code semantic, code graph, AST) with hybrid methods (vector + FTS + RRF + reranking)
3. **Enforce Quality Through Adversarial Design:** Phase-gated workflows with hidden evidence validation prevent AI shortcuts
4. **Provide Transparent, Debuggable System:** Comprehensive observability (query logs, diversity metrics, latency tracking) for both AI and humans
5. **Establish Extensible Foundation:** Config-driven extensibility enables new languages, tools, and features without code changes

### Key User Stories

- **Story 1 (Knowledge Discovery):** As an AI agent, I want to search project standards semantically so I can discover relevant patterns before implementing
- **Story 2 (Cross-Session Learning):** As an AI agent, I want my query patterns tracked across sessions so my behavior improves over time
- **Story 3 (Graph Traversal):** As an AI agent, I want to find code context via graph traversal (who calls this?) so I understand impact before changes
- **Story 4 (Multi-Angle Discovery):** As an AI agent, I want query diversity metrics to guide my search behavior so I explore multiple perspectives
- **Story 5 (Adversarial Validation):** As a workflow user, I want evidence validation to catch shortcuts so I cannot game the system

### Functional Requirements (Summary)

**Middleware Layer (Behavioral Engineering):**
- FR-001: Query Gamification (prepends with progress bars, diversity metrics)
- FR-002: Query Tracking (logs every search with metadata)
- FR-003: Query Classification (5 angles: conceptual, location, implementation, critical, troubleshooting)

**Tools Layer (AI Agent Interface):**
- FR-005: pos_search_project (6 actions: search_standards, search_code, search_ast, find_callers, find_dependencies, find_paths)
- FR-006: pos_workflow (14 actions: lifecycle management)
- FR-007: pos_browser (23 actions: Playwright automation)
- FR-008: pos_filesystem (12 actions: file operations)
- FR-009: get_server_info (observability)

**RAG Subsystem:**
- FR-011: StandardsIndex (hybrid search: vector + FTS + RRF + rerank)
- FR-012: CodeIndex (semantic search: LanceDB + CodeBERT)
- FR-013: GraphIndex (call graph traversal: DuckDB + recursive CTEs)
- FR-014: ASTIndex (structural search: Tree-sitter)
- FR-015: FileWatcher (incremental updates <5s)

**Total:** 25 functional requirements

### Non-Functional Requirements (Summary)

- **Performance:** Cold start <30s, search latency <200ms (p95), incremental update <5s, config load <100ms
- **Reliability:** 99.9% uptime, graceful degradation, auto-recovery from failures, zero silent errors
- **Security:** Input validation, path traversal prevention, command injection protection, secrets management
- **Testability:** ≥90% test coverage (core), unit + integration + performance + validation tests
- **Extensibility:** Tool auto-discovery, config-driven language support, plugin architecture

**Total:** 44 non-functional requirements across 11 categories

---

## Technical Design Summary

### Architecture

**Pattern:** Mission-Driven Layered Architecture

**Key Components:**
- **Tools Layer (5 tools):** pos_search_project, pos_workflow, pos_browser, pos_filesystem, get_server_info
- **Middleware Layer (3 components):** PrependGenerator, QueryTracker, QueryClassifier
- **RAG Subsystem (6 components):** IndexManager, StandardsIndex, CodeIndex, GraphIndex, ASTIndex, FileWatcher
- **Workflow Subsystem (3 components):** WorkflowEngine, StateManager, TaskParser
- **Browser Subsystem (2 components):** BrowserManager, PlaywrightImpl
- **Foundation Layer (4 components):** Config (Pydantic v2), Utils, Errors, Logging

### Technology Stack

- **Framework:** FastMCP (official Python MCP framework)
- **Language:** Python 3.10+
- **Config:** Pydantic v2 (type-safe validation)
- **Search:** LanceDB (vector + FTS), sentence-transformers (embeddings), CodeBERT (code embeddings)
- **Graph:** DuckDB (recursive CTEs for call graph traversal)
- **AST:** Tree-sitter (structural code parsing)
- **Workflow:** JSON state persistence, YAML evidence schemas
- **Browser:** Playwright (isolated sessions)
- **Logging:** Structured JSON

### Data Models

**Config (Pydantic v2):**
- MCPConfig (root)
- IndexesConfig (standards, code, AST)
- WorkflowConfig, BrowserConfig

**Storage Schemas:**
- LanceDB: standards (vector + FTS + metadata), code (vector + FTS)
- DuckDB: symbols table, relationships table (call graph)
- JSON: workflow state
- JSON Lines: query logs

### APIs

**MCP Tools (External Interface):**
- `pos_search_project(action, query, method, max_results, ...)` - 6 actions
- `pos_workflow(action, session_id, workflow_type, ...)` - 14 actions
- `pos_browser(action, session_id, url, ...)` - 23 actions
- `pos_filesystem(action, path, content, ...)` - 12 actions
- `get_server_info()` - Server/project metadata

**Internal Python Interfaces:**
- `BaseIndex.search(query, method, max_results)` - Search interface
- `MiddlewareHook.process(request, response)` - Middleware hook
- `WorkflowEngine.execute_phase(session_id, phase)` - Workflow execution

---

## Implementation Plan

### Timeline

**Total Estimated Time:** 64-84 hours (8-10.5 days)  
**Critical Path:** 52-68 hours (6.5-8.5 days)

**Phases:**
1. **Phase 1 (6-8h):** Foundation (Config + Utils) - Pydantic schemas, logging, errors
2. **Phase 2 (8-10h):** Core Infrastructure (Registry + Middleware) - Tool discovery, prepend generation, query tracking
3. **Phase 3 (16-20h):** RAG Subsystem (Search + Indexes) - Standards, code, graph, AST indexes + file watcher
4. **Phase 4 (8-10h):** Workflow Subsystem - Phase-gated execution, evidence validation, state persistence
5. **Phase 5 (4-6h):** Browser Subsystem - Playwright integration, session isolation
6. **Phase 6 (6-8h):** Tools Layer - Implement all 5 MCP tools with domain abstraction pattern
7. **Phase 7 (4-6h):** Entry Points + Integration - Server startup, end-to-end flows
8. **Phase 8 (12-16h):** Testing + Validation - Unit, integration, performance, behavioral tests

### Key Milestones

- **Milestone 1:** Config + Utils complete (Phase 1 done) - 6-8 hours
- **Milestone 2:** Middleware functional (prepends in 100% of searches) - 16-20 hours
- **Milestone 3:** RAG subsystem operational (all 4 indexes searchable) - 36-48 hours
- **Milestone 4:** All tools implemented (MCP interface complete) - 52-68 hours
- **Milestone 5:** All tests passing (validation complete) - 64-84 hours

### Dependencies

- **Critical Path:** Phase 1 → Phase 2 → Phase 3 → Phase 6 → Phase 7 → Phase 8
- **Parallel Tracks:** Phase 4 (Workflow) and Phase 5 (Browser) can proceed in parallel with Phase 3 (RAG)
- **External Dependencies:** None (all libraries in requirements.txt, Tree-sitter parsers auto-installed)

---

## Risks and Mitigations

### Risk 1: Performance Regression

**Impact:** High (search latency >200ms breaks UX)  
**Probability:** Medium  
**Mitigation:**
- Phase 8.4 performance tests must pass before approval
- Caching strategies (embedding models, LanceDB index, optional query results)
- Lazy loading (load indexes on first use)
- Fallback: Optimize hot paths if tests fail

### Risk 2: Config Incompatibility

**Impact:** Medium (migration friction for existing users)  
**Probability:** Low  
**Mitigation:**
- Phase 8.5 validation tests existing YAML configs
- Provide migration script if needed
- Document config changes in README

### Risk 3: Feature Parity Gaps

**Impact:** High (missing features block adoption)  
**Probability:** Low  
**Mitigation:**
- Phase 8.5 checklist ensures all mcp_server tools replicated
- Document any differences with migration path
- Parallel deployment (keep mcp_server as rollback option)

### Risk 4: Query Gamification Overhead

**Impact:** Low (prepend generation adds latency)  
**Probability:** Medium  
**Mitigation:**
- Phase 8.4 tests search latency with middleware enabled
- Cache prepends for identical query patterns
- Optimize diversity calculation
- Fallback: Simplify prepend format if >50ms overhead

### Risk 5: LanceDB FTS Corruption

**Impact:** High (panics crash searches)  
**Probability:** Low (fixed in current implementation)  
**Mitigation:**
- Standards

Index.incremental_update() rebuilds FTS + scalar indexes after every update
- Auto-repair health check detects corruption and rebuilds
- Fallback: Force rebuild with `force_rebuild=True`

---

## Out of Scope

**Not included in this release:**

- **Multi-repo indexing:** Single-repo only (one project at a time)
  - *Rationale:* Praxis OS is repo-specific by design (deep expertise on one project)
  - *Future Consideration:* Potential Phase 3 if multi-project workflows emerge

- **Human UI/Dashboard:** AI agent is primary user
  - *Rationale:* Focus on AI-first architecture
  - *Future Consideration:* Potential Phase 2 for observability dashboard

- **Cloud/SaaS deployment:** Local-only
  - *Rationale:* Privacy, security, offline-first design
  - *Future Consideration:* Potential Phase 3 if demand justifies

- **LSP integration:** Search-based code nav only
  - *Rationale:* LSP optimized for interactive IDE use, not AI agent batch operations (see Sourcebot analysis)
  - *Future Consideration:* None (LSP doesn't align with AI workflow)

- **Windows support:** macOS/Linux only
  - *Rationale:* Development resources focused on primary platforms
  - *Future Consideration:* Potential Phase 3 if Windows demand exists

**Future Enhancements (Potential Roadmap):**

- **Phase 2 (After MVP Proven):**
  - Multi-language AST support (expand beyond Python/TypeScript/Rust/Go)
  - Performance optimizations (query result caching, embedding caching)
  - Human observability dashboard (metrics, query logs, diversity charts)

- **Phase 3 (Long-Term):**
  - Multi-repo indexing (if cross-project patterns emerge)
  - Advanced graph queries (data flow analysis, dependency cycles)
  - Distributed indexing (if single-repo scale becomes an issue)

---

## Getting Started

### For Implementers

1. **Read [srd.md](srd.md)** - Understand business goals, user stories, and all requirements (5 business goals, 10 user stories, 69 requirements)
2. **Review [specs.md](specs.md)** - Study architecture, 22 component designs, API specifications, data models, security, performance
3. **Follow [tasks.md](tasks.md)** - Implement in sequence: 8 phases, 31 tasks, follow critical path
4. **Reference [implementation.md](implementation.md)** - Use 7 code patterns (Pydantic, FastMCP, LanceDB, DuckDB, Tree-sitter, Error handling), testing strategy, deployment guidance

**Implementation Order (Critical Path):**
```
Phase 1 (Config) → Phase 2 (Middleware) → Phase 3 (RAG) → Phase 6 (Tools) → Phase 7 (Entry Points) → Phase 8 (Testing)
```

**Parallel Work:**
- Phase 4 (Workflow) and Phase 5 (Browser) can start after Phase 1, run in parallel with Phase 3

### For Reviewers

1. **Review [srd.md](srd.md)** - Validate requirements completeness (business goals, user stories, FRs, NFRs)
2. **Check [specs.md](specs.md)** - Evaluate architecture (layered design), component boundaries (zero cross-talk), API design (domain abstraction)
3. **Validate [tasks.md](tasks.md)** - Verify task completeness (31 tasks with acceptance criteria), dependencies (critical path identified), time estimates (64-84h)
4. **Assess [implementation.md](implementation.md)** - Check code patterns (7 patterns with examples), testing strategy (4 levels), deployment guidance (troubleshooting included)

**Key Review Focus:**
- **Behavioral Engineering:** Are prepends in 100% of searches? Is query tracking comprehensive?
- **Clean Architecture:** Are subsystems isolated? Is middleware wrapping all tool calls?
- **Config-Driven:** Can new languages be added via YAML only?
- **Fail-Fast:** Do invalid configs crash with actionable errors?

### For Stakeholders

- **Summary:** See "Executive Summary" above
- **Timeline:** 64-84 hours (8-10.5 days), critical path 52-68 hours (6.5-8.5 days)
- **Progress:** Track against 8 phases and 5 milestones in [tasks.md](tasks.md)
- **Benefits:** Behavioral engineering functional, knowledge compounding enabled, adversarial design enforced
- **Risks:** 5 identified risks with mitigations (performance, config compatibility, feature parity, query overhead, FTS corruption)

---

## Success Criteria

**This feature will be considered successful when:**

- [ ] **All functional requirements implemented and tested** (25 FRs: middleware, tools, RAG, workflow, browser, config)
- [ ] **Non-functional requirements met** (performance <30s cold start, <200ms search; reliability 99.9% uptime; security validated; ≥90% test coverage)
- [ ] **Behavioral engineering validated** (prepends in 100% of searches, query diversity tracked, middleware never fails silently)
- [ ] **Feature parity confirmed** (all mcp_server tools replicated, existing YAML configs work)
- [ ] **Production deployment completed** (switched from mcp_server to ouroboros, rollback plan validated)
- [ ] **Success metrics achieved** (query diversity >60%, standards growth >5/month, correction frequency decreasing)

---

## Questions or Feedback

**For implementation questions:** See [implementation.md](implementation.md) - 7 code patterns, testing strategy, troubleshooting  
**For requirements clarification:** See [srd.md](srd.md) - 5 business goals, 10 user stories, 69 requirements  
**For design questions:** See [specs.md](specs.md) - Architecture, 22 components, APIs, data models, security, performance  
**For task dependencies:** See [tasks.md](tasks.md) - 8 phases, 31 tasks, dependencies matrix, critical path

---

## Document History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-11-04 | 1.0 | AI Agent (spec_creation_v1 workflow) | Initial spec creation (Phase 0-5 complete) |

---

## Approval

**Spec Status:** Draft - Awaiting Human Review

**Next Steps:**
1. Human reviews all spec files (README.md, srd.md, specs.md, tasks.md, implementation.md)
2. Human approves with "Approved" or "Implement the spec"
3. Spec moves: `git mv specs/review/2025-11-03-ouroboros-mcp-server specs/approved/`
4. Implementation begins using `spec_execution_v1` workflow

**Approvers:**
- [ ] Product Owner: Josh (praxis-os maintainer)
- [ ] Tech Lead: TBD
- [ ] Engineering Manager: TBD

**Approved Date:** _____________

