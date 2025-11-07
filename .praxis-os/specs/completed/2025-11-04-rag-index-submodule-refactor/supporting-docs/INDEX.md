# Supporting Documents Index

**Spec:** RAG Index Submodule Refactor  
**Created:** 2025-11-04  
**Total Documents:** 1

## Document Catalog

### 1. RAG Index Submodule Pattern

**File:** `rag-index-submodule-pattern.md`  
**Type:** Architecture Design Document  
**Purpose:** Defines comprehensive refactoring strategy to reorganize RAG indexes using submodule-per-index pattern, addressing inconsistent abstractions and preparing for future index additions

**Relevance:** Requirements [H], Design [H], Implementation [H]

**Key Topics:**
- Submodule-per-index architectural pattern
- Uniform interface via BaseIndex contract
- Database consolidation (LanceDB + DuckDB, eliminating SQLite)
- IndexManager orchestration and registry-based initialization
- File locking for index integrity
- Corruption detection and auto-repair mechanisms
- Shared utilities (DRY principles)
- Incremental update flows
- Migration path from current structure

---

## Cross-Document Analysis

**Common Themes:**
- SOLID principles application (especially Dependency Inversion)
- Clean architecture with clear abstraction boundaries
- Production reliability (auto-repair, file locking, health checks)
- Scalability and extensibility (easy to add new indexes)
- Uniform discovery patterns (container.py entry point)

**Potential Conflicts:**
- None (single authoritative document)

**Coverage Gaps:**
- No performance benchmarks or migration timeline estimates
- Testing strategy outlined but not detailed test plans
- No rollback strategy if migration fails
- Windows compatibility for file locking is stubbed (no-op)
- Missing details on handling existing user data during migration

---

## Next Steps

This index will be used in Task 3 to systematically extract insights from the document. The extracted insights will be organized by:
- **Requirements Insights:** User needs, business goals, functional requirements (corruption prevention, maintainability)
- **Design Insights:** Architecture patterns, technical approaches, component designs (submodule structure, interfaces, database choices)
- **Implementation Insights:** Code patterns, testing strategies, deployment guidance (migration path, utilities, registry pattern)


---

## Extracted Insights

### Requirements Insights (Phase 1)

#### From RAG Index Submodule Pattern:
- **User Need:** Consistent, predictable interface for discovering and using RAG indexes (AI/human developers)
- **User Need:** Prevent index corruption from concurrent manual rebuilds during MCP server operation
- **Business Goal:** Enable easy addition of new indexes (project_docs, dependency_docs) without modifying core orchestrator
- **Functional Req:** Uniform entry point via `container.py` for all indexes regardless of complexity
- **Functional Req:** Automatic corruption detection and repair without user intervention ("just works" reliability)
- **Functional Req:** File-based locking (fcntl) to coordinate access between MCP server and manual rebuild scripts
- **Functional Req:** Health checks with three-tier validation (metadata, functional, data integrity)
- **Constraint:** Database architecture limited to LanceDB + DuckDB only (no SQLite)
- **Constraint:** Windows file locking not yet implemented (stub/no-op for now)
- **Out of Scope:** Performance benchmarking during initial migration

### Design Insights (Phase 2)

#### From RAG Index Submodule Pattern:
- **Architecture:** Submodule-per-index with uniform `BaseIndex` interface, following Dependency Inversion Principle
- **Architecture:** Three-file pattern: `__init__.py` (exports), `container.py` (interface), implementation files (semantic.py, graph.py)
- **Architecture:** Registry-based initialization for dynamic index discovery and config-driven setup
- **Component:** `IndexManager` orchestrates all indexes, treats them identically via `BaseIndex` contract
- **Component:** Simple indexes (standards) delegate to single semantic.py, complex indexes (code) orchestrate semantic.py + graph.py
- **Component:** Shared utilities (LanceDBConnection, EmbeddingModelLoader, DuckDBConnection, FileChangeTracker, IndexLockManager)
- **Data Model:** LanceDB tables for semantic search (vector + FTS + scalar indexes on metadata)
- **Data Model:** DuckDB tables for structural search (symbols table, relationships table, recursive CTEs for graph traversal)
- **API:** BaseIndex interface: build(), search(), update(), health_check(), get_stats()
- **API:** CodeIndex extends with: search_ast(), find_callers(), find_dependencies() for structural/graph queries
- **Security:** Advisory file locking (shared lock for queries, exclusive lock for rebuilds)
- **Security:** Thread-safe rebuild with `threading.Lock()` and `_is_rebuilding` flag to prevent concurrent rebuilds within process

### Implementation Insights (Phase 4)

#### From RAG Index Submodule Pattern:
- **Code Pattern:** Lazy initialization for database connections, tables, and embedding models
- **Code Pattern:** Context manager (`with lock_manager.exclusive_lock():`) for safe rebuild operations
- **Code Pattern:** Corruption detection via pattern matching on exception strings ("lance error", "invalid manifest", etc.)
- **Code Pattern:** Auto-repair on search errors: detect corruption → acquire lock → rebuild → retry search (once)
- **Code Pattern:** Health check returns `HealthStatus` Pydantic model with healthy/message/details/last_updated
- **Testing:** Unit tests for lock behavior (shared allows multiple, exclusive blocks all)
- **Testing:** Integration tests for startup corruption recovery (corrupt index → auto-rebuild → healthy)
- **Testing:** Mock-based tests for corruption detection and auto-repair flows
- **Deployment:** Two-phase migration: (1) Refactor existing standards+code, (2) Add new project_docs+dependency_docs
- **Deployment:** Migration script pattern: create submodule dirs → move files → update imports → remove special cases
- **Monitoring:** Structured logging with emojis (✅/⚠️/❌/🔧/🔍) for visual health status
- **Monitoring:** Health check logs on startup: check all → categorize unhealthy → rebuild → re-check → report summary

### Cross-References

**Validated by Multiple Sources:** N/A (single document)

**Conflicts:** None

**High-Priority:**
- File locking implementation (prevents primary corruption source)
- Corruption detection + auto-repair (reliability cornerstone)
- BaseIndex interface uniformity (enables independent evolution)
- Shared utilities (eliminates duplication across indexes)
- Migration path clarity (Phase 1: refactor existing, Phase 2: add new)

## Insight Summary

**Total:** 39 insights  
**By Category:** Requirements [10], Design [13], Implementation [16]  
**Multi-source validated:** 0 (single document)  
**Conflicts to resolve:** 0  
**High-priority items:** 5

**Phase 0 Complete:** ✅ 2025-11-04
