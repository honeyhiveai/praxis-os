# RAG Index Submodule Refactor - Specification Package

**Project:** RAG Index Submodule Refactor  
**Date:** 2025-11-04  
**Status:** Ready for Implementation  
**Workflow:** spec_creation_v1 (Complete)

---

## Executive Summary

This specification package documents a comprehensive refactoring of the RAG (Retrieval-Augmented Generation) index system to use a submodule-per-index pattern. The refactor addresses current architectural limitations (inconsistent abstractions, tight coupling, 3-database complexity) and enables scalable, maintainable index management.

**Key Benefits:**
- **Uniform Interface:** All indexes implement BaseIndex (no special cases)
- **Independent Evolution:** Add/modify indexes without touching IndexManager
- **Database Consolidation:** 3 databases → 2 (LanceDB + DuckDB, eliminate SQLite)
- **Corruption Prevention:** File-based locking prevents concurrent access issues
- **Reduced Onboarding:** 1 hour → 15 minutes to understand system

**Deliverables:** 5 production-ready specification documents (186KB total)

---

## Document Index

### Core Specification Documents

| Document | Purpose | Size | Sections |
|----------|---------|------|----------|
| **[srd.md](srd.md)** | Software Requirements | 15KB | Goals, Stories, FR/NFR, Scope |
| **[specs.md](specs.md)** | Technical Design | 76KB | Architecture, Components, APIs, Data Models, Security, Performance |
| **[tasks.md](tasks.md)** | Implementation Plan | 39KB | 5 Phases, 27 Tasks, Dependencies, Gates, Estimates |
| **[implementation.md](implementation.md)** | Developer Guidance | 56KB | Patterns, Testing, Deployment, Troubleshooting |
| **[README.md](README.md)** | Package Overview | This file | Document index, metrics, quick start |

### Supporting Documents

- **[supporting-docs/rag-index-submodule-pattern.md](supporting-docs/rag-index-submodule-pattern.md)** - Original design document (2,800 lines) with detailed code examples
- **[supporting-docs/INDEX.md](supporting-docs/INDEX.md)** - Supporting document catalog

---

## Quick Start by Role

### For Project Managers

**Read First:** [srd.md](srd.md) - Business goals and requirements

**Key Metrics:**
- **Timeline:** 44-57 hours (5-7 days)
- **Phases:** 5 (Foundation → Standards → Code → Integration → Testing)
- **Requirements:** 10 functional, 5 non-functional
- **Risk:** Medium (local development, no production users, straightforward rollback)

**Critical Success Factors:**
- Phase gates enforced (no skipping)
- Standards index validates pattern before code index
- Old files retained until Phase 4 complete (safety net)

---

### For Architects

**Read First:** [specs.md](specs.md) - Technical architecture and design decisions

**Key Architectural Patterns:**
- **Modular Monolith + Submodule-Per-Index** - Clear boundaries, single deployment
- **Dependency Inversion** - IndexManager depends on BaseIndex abstraction
- **Registry Pattern** - Add indexes without code changes
- **Container Pattern** - Uniform entry point (container.py) for all indexes

**Technology Stack:**
- **Languages:** Python 3.10+
- **Databases:** LanceDB 0.13.0+ (vector search), DuckDB 0.9.0+ (structural search)
- **Key Libraries:** sentence-transformers, pydantic, fcntl (locking)

**Architecture Decisions:** 6 major decisions documented with rationale, alternatives, trade-offs

---

### For Developers

**Read First:** [implementation.md](implementation.md) - Code patterns and examples

**Quick Implementation Guide:**
1. **Phase 0** (3-4h): Implement BaseIndex, Lock Manager, Utilities
2. **Phase 1** (2-3h): Refactor standards index to submodule pattern
3. **Phase 2** (4-5h): Refactor code index (LanceDB + DuckDB)
4. **Phase 3** (3-4h): Update IndexManager with registry pattern
5. **Phase 4** (3-4h): Test, validate, cleanup old files

**Code Patterns:**
- Simple Submodule (LanceDB only): `standards/` - 6 documented patterns
- Complex Submodule (LanceDB + DuckDB): `code/` - Full example code
- Utility Helpers (DRY): `utils/` - Reusable connection/model loaders

**Testing Strategy:**
- Unit tests: 80% coverage minimum, 90% for foundation
- Integration tests: Every phase before advancing
- Performance benchmarks: Standards build <60s, code build <120s

**Troubleshooting:** 6 common issues documented with solutions (lock failures, corruption, migrations, etc.)

---

### For QA Engineers

**Read First:** [tasks.md](tasks.md) - Acceptance criteria and test strategy

**Phase Validation Gates:**
- **Phase 0:** Foundation tests passing, 90% coverage
- **Phase 1:** Standards index working, zero regressions
- **Phase 2:** Code index functional (semantic + graph), migration verified
- **Phase 3:** IndexManager routing correctly, tools integrated
- **Phase 4:** Full suite passing (529+ tests), performance targets met

**Test Organization:**
```
tests/ouroboros/subsystems/rag/
├── test_base.py              # BaseIndex, SearchResult, HealthStatus
├── test_lock_manager.py      # File locking (concurrent access)
├── test_utils.py             # Connection/model utilities
├── standards/                # Standards index tests
├── code/                     # Code index tests (semantic + graph)
└── test_index_manager.py     # Integration tests
```

**Performance Targets:**
- Standards build: < 60s (450 chunks)
- Code build: < 120s (semantic + AST)
- Search p95: < 300ms (5 results)
- Graph traversal p95: < 300ms (depth=10)

---

### For Technical Writers

**Read First:** [README.md](README.md) (this file), then [srd.md](srd.md)

**Documentation Requirements:**
- All public APIs have docstrings (Args, Returns, Raises)
- README updated if submodule pattern is public-facing
- Migration guide for SQLite → DuckDB included in implementation.md

**Key Terminology:**
- **Submodule:** Self-contained Python package (standards/, code/)
- **Container:** Entry point implementing BaseIndex (container.py)
- **Semantic Search:** Vector + FTS search (LanceDB)
- **Structural Search:** AST symbol search (DuckDB)
- **Graph Traversal:** Call graph via recursive CTEs (DuckDB)

---

## Project Metrics

### Requirements Coverage

| Category | Count | Status |
|----------|-------|--------|
| Business Goals | 4 | Defined with success metrics |
| User Stories | 5 | With value propositions |
| Functional Requirements | 10 | FR-001 through FR-010 |
| Non-Functional Requirements | 5 | Reliability, Performance (3), Maintainability |

**Requirements Traceability:** All 10 FRs mapped to architecture → tasks → implementation

---

### Implementation Scope

| Metric | Value |
|--------|-------|
| **Total Phases** | 5 (Phase 0-4) |
| **Total Tasks** | 27 |
| **Total Estimated Time** | 44-57 hours (5-7 days) |
| **Critical Path** | 40-51 hours (20-21 tasks) |
| **Components** | 7 (BaseIndex, 2 index submodules, lock manager, 3 utilities, IndexManager) |
| **Validation Gates** | 5 (1 per phase) |
| **Test Coverage Target** | 80% minimum, 90% foundation |

---

### Design Complexity

| Metric | Value |
|--------|-------|
| **Architecture Decisions** | 6 (with rationale, alternatives, trade-offs) |
| **Code Patterns** | 6 (with concrete examples) |
| **Anti-Patterns** | 4 (what NOT to do) |
| **Database Schemas** | 4 (2 LanceDB tables, 2 DuckDB tables) |
| **API Interfaces** | 3 core (BaseIndex, IndexManager, IndexLockManager) |

---

### Documentation Metrics

| Document | Lines | KB | Sections | Status |
|----------|-------|-----|---------|--------|
| srd.md | ~400 | 15 | 7 | Complete |
| specs.md | ~1,500 | 76 | 7 major (20+ subsections) | Complete |
| tasks.md | ~800 | 39 | 9 major | Complete |
| implementation.md | ~1,100 | 56 | 9 major | Complete |
| **Total** | **~3,800** | **186** | **32+** | **Ready** |

---

## Key Features of This Refactor

### 1. Uniform Submodule Pattern

**Every index follows same 3-file structure:**
```
<index_name>/
├── __init__.py        # Pure exports (no logic)
├── container.py       # Implements BaseIndex (interface)
└── semantic.py        # Implementation (hidden from IndexManager)
```

**Complex indexes add more files but keep same structure:**
```
code/
├── __init__.py        # Pure exports
├── container.py       # Orchestrates semantic + graph
├── semantic.py        # LanceDB (vector search)
└── graph.py           # DuckDB (AST + call graph)
```

---

### 2. Database Consolidation

**Before:** 3 databases (complex)
- LanceDB: Vector + FTS
- SQLite: AST symbols
- DuckDB: Call graph

**After:** 2 databases (simpler)
- **LanceDB:** Vector + FTS + Scalar (standards, code semantic)
- **DuckDB:** AST + Call graph + Recursive CTEs (code structural)

**Benefits:**
- Simpler architecture (fewer moving parts)
- Faster builds (single-pass DuckDB vs SQLite→DuckDB export/import)
- Clearer separation (semantic vs structural)

---

### 3. Corruption Prevention

**Problem:** 2-3 corruption incidents per week from concurrent access

**Solution:** File-based advisory locks (fcntl)
```python
with lock_manager.exclusive_lock():
    index.build(source_paths, force=True)  # Protected
```

**Lock Types:**
- **Shared (LOCK_SH):** Multiple readers (queries)
- **Exclusive (LOCK_EX):** Single writer (rebuild)

**Target:** 0 corruption incidents per month

---

### 4. Registry-Based Discovery

**Before:** Hardcoded index initialization
```python
self._indexes["standards"] = StandardsIndex(...)
self._indexes["code"] = CodeIndex(...)
# Must modify code for every new index
```

**After:** Registry-driven initialization
```python
INDEX_REGISTRY = {
    "standards": ("ouroboros.subsystems.rag.standards", "StandardsIndex"),
    "code": ("ouroboros.subsystems.rag.code", "CodeIndex"),
    # Add new index here (zero code changes elsewhere)
}
```

**Benefit:** Add new index in 30 minutes vs 4 hours

---

## Implementation Phases

### Phase 0: Foundation & Utilities (3-4 hours)

**Deliverables:**
- BaseIndex abstract interface
- IndexLockManager (file-based locking)
- Shared utility modules (LanceDB, DuckDB, model loaders)

**Validation Gate:**
- All foundation tests passing
- 90% code coverage
- Lock acquisition/release functional

---

### Phase 1: Standards Index Refactor (2-3 hours)

**Deliverables:**
- `standards/` submodule (container + semantic)
- StandardsIndex implements BaseIndex
- Backward compatibility with old standards_index.py

**Validation Gate:**
- Standards index functional
- Integration test passing (build → search → update)
- Zero regressions

---

### Phase 2: Code Index Refactor (4-5 hours)

**Deliverables:**
- `code/` submodule (container + semantic + graph)
- CodeIndex orchestrates LanceDB + DuckDB
- SQLite → DuckDB migration

**Validation Gate:**
- Code index functional (semantic + graph)
- Recursive CTEs working (find_callers, find_dependencies)
- Migration verified (row counts match)
- Performance targets met

---

### Phase 3: IndexManager Refactor & Integration (3-4 hours)

**Deliverables:**
- IndexManager with registry pattern
- Query routing updated (all actions)
- Tools layer integrated (pos_search_project)

**Validation Gate:**
- IndexManager initializes only 2 indexes (not 4)
- All routing actions functional
- End-to-end tests passing

---

### Phase 4: Testing & Validation (3-4 hours)

**Deliverables:**
- Full test suite passing (529+ tests)
- Performance benchmarks validated
- Old files deleted
- Documentation updated

**Validation Gate:**
- Zero test failures
- Performance targets met or exceeded
- System operational in production

---

## Risk Assessment

### Overall Risk Level: **Medium**

**Risk Factors:**
- **Complexity:** Medium (multiple components, 2 databases)
- **Impact:** Medium (breaks AI workflow if failed, but local-only)
- **Rollback:** Low risk (straightforward, old files available)

**Mitigation Strategies:**

1. **Phase Gates Enforced**
   - Cannot skip phases
   - Must pass all acceptance criteria before proceeding
   - Prevents cascading failures

2. **Pattern Validation**
   - Phase 1 (simple index) validates pattern
   - Phase 2 (complex index) builds on validated pattern
   - Reduces risk for most complex component

3. **Backward Compatibility**
   - Old files retained until Phase 4
   - Can rollback at any phase
   - Time to rollback: < 5 minutes

4. **Reproducible Indexes**
   - All indexes rebuild from source files
   - If migration fails, just rebuild
   - No permanent data loss risk

---

## Success Criteria

### Definition of Done

**All 10 Functional Requirements Satisfied:**
- ✅ FR-001: Every index has container.py
- ✅ FR-002: Registry enables zero-code index addition
- ✅ FR-003: Lock manager prevents corruption
- ✅ FR-004: Only 2 databases (LanceDB + DuckDB)
- ✅ FR-005: Auto-repair triggers on health check failure
- ✅ FR-006: Shared utilities eliminate duplication
- ✅ FR-007: Submodule internals hidden from IndexManager
- ✅ FR-008: Incremental updates route through IndexManager
- ✅ FR-009: BaseIndex interface enforced
- ✅ FR-010: 3-tier health checks

**All 5 Non-Functional Requirements Met:**
- ✅ NFR-R1: 0 corruption incidents per month
- ✅ NFR-P1: Build times < 60s (standards), < 120s (code)
- ✅ NFR-P2: Search p95 < 300ms
- ✅ NFR-P3: Incremental updates < 5s (10 files)
- ✅ NFR-M1: Add new index in 30 minutes (vs 4 hours)

**Quality Gates:**
- ✅ 529+ tests passing
- ✅ Zero linter/mypy errors
- ✅ Code coverage >= 80%
- ✅ All documentation updated

---

## Next Steps

### Immediate Actions

1. **Review Specifications** (Stakeholders)
   - Read srd.md for business context
   - Review specs.md for technical approach
   - Approve or request changes

2. **Plan Sprint** (Dev Team Lead)
   - Use tasks.md as backlog
   - Allocate 5-7 days (1-2 sprints)
   - Assign Phase 0 (foundation) first

3. **Setup Environment** (Developers)
   - Verify Python 3.10+
   - Install dependencies (lancedb, duckdb, sentence-transformers)
   - Review implementation.md code patterns

4. **Kick Off Phase 0** (Team)
   - Implement BaseIndex, Lock Manager, Utilities
   - Run foundation tests
   - Pass Phase 0 validation gate

---

### Follow-On Tasks (After Completion)

1. **Add Project Docs Index** (Future)
   - Follow same submodule pattern
   - Add to registry
   - ~ 2-3 hours

2. **Add Dependency Docs Index** (Future)
   - Complex index (versioning support)
   - Follow code index pattern
   - ~ 4-6 hours

3. **Performance Optimization** (Future)
   - Parallel chunking (4x speedup)
   - GPU acceleration (2x speedup)
   - Query result caching

---

## Specification Package Status

**Package Completeness:** ✅ All 5 required documents present

| Document | Created | Reviewed | Status |
|----------|---------|----------|--------|
| srd.md | ✅ | ✅ | Ready |
| specs.md | ✅ | ✅ | Ready |
| tasks.md | ✅ | ✅ | Ready |
| implementation.md | ✅ | ✅ | Ready |
| README.md | ✅ | ✅ | **You Are Here** |

**Cross-Document Consistency:** ✅ Verified (component names, terminology, cross-references)

**Requirements Traceability:** ✅ All 10 FRs traced through architecture → tasks → implementation

**Ready for Implementation:** ✅ Yes

---

## Contact & Resources

**Specification Authors:** praxis-os AI Agent (via spec_creation_v1 workflow)  
**Specification Date:** 2025-11-04  
**Workflow Duration:** ~6-7 hours (Phase 0-5, systematic approach)

**Key Resources:**
- **Standards:** `.praxis-os/standards/` (query with pos_search_project)
- **Supporting Doc:** `supporting-docs/rag-index-submodule-pattern.md` (2,800 lines, 55 code blocks)
- **Test Examples:** `tests/ouroboros/subsystems/rag/` (working code patterns)

**Questions?** Reference the appropriate spec document:
- Business/requirements questions → srd.md
- Architecture/design questions → specs.md
- Implementation/task questions → tasks.md
- Code pattern questions → implementation.md

---

**END OF SPECIFICATION PACKAGE README**

**Status:** Ready for Implementation ✅  
**Approval Status:** Pending Stakeholder Review  
**Next Action:** Review and approve specifications, then begin Phase 0

