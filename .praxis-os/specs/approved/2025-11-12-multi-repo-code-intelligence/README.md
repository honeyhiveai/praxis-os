# Multi-Repo Code Intelligence for Instrumentor Analysis

**Status:** Ready for Implementation  
**Date:** 2025-11-12  
**Estimated Effort:** 25-30 hours (7 phases)  
**Business Value:** 3 hours → 15 minutes per instrumentor (12x speedup)

---

## Executive Summary

This specification defines a **multi-repository code intelligence system** for analyzing OpenTelemetry instrumentors to extract semantic conventions automatically. The system enables HoneyHive to support **270 instrumentors** across 4 providers (OpenLit, Traceloop, Arize, OpenTelemetry) for the BYOI (Bring Your Own Instrumentor) feature.

**Key Capabilities:**
- **Partition-based indexing** (primary code vs. instrumentors)
- **Incremental updates** (only changed files, not full repos)
- **Cross-repo queries** with filtering by partition/repo/provider
- **Automated extraction** of span attributes and naming patterns
- **Performance targets:** Primary p95 < 50ms, Instrumentors p95 < 200ms, Extraction < 15 min

**Scale:** 437K total chunks (primary 113K + instrumentors 324K), 270 repositories, < 3GB disk

---

## Problem Statement

**Current State:**
- **Manual instrumentor analysis** takes 3 hours per instrumentor
- Error-prone (attributes missed, incorrect mappings)
- Doesn't scale to 270 instrumentors (810 hours manual work)
- Maintenance burden when instrumentors update

**Desired State:**
- **Automated extraction** completes in 15 minutes per instrumentor
- 100% accuracy (all attributes captured)
- Scales to 270 instrumentors (~68 hours initial indexing, then incremental)
- Incremental updates when instrumentors change (< 5 seconds for typical changes)

**Business Impact:**
- **12x faster** analysis (3 hours → 15 minutes)
- **Enables BYOI** feature with comprehensive framework support
- **Reduces manual effort** by ~800 hours for initial 270 instrumentors
- **Ongoing maintenance** from hours to minutes with incremental updates

---

## Solution Overview

### Architecture

**Partition-Based Modular Monolith:**
- **CodeIndex** (container) → **CodePartition** (primary, instrumentors) → **3 Sub-Indexes** (Semantic, AST, Graph)
- Dynamic partition discovery from config (zero hardcoded partition names)
- 4-level fractal health checks (CodeIndex → Partition → Index → Sub-components)

**Key Innovations:**
1. **Parse-Once-Index-Thrice:** Single Tree-sitter parse populates all 3 indexes (2.25x speedup)
2. **Partition Routing:** Queries route to specific partition to minimize chunks searched (3.9x speedup)
3. **Incremental Indexing:** Git diff detects changes, only reprocesses changed files (200x speedup)
4. **Sparse Checkout:** Clone only relevant subdirectories (20x smaller disk, 5x faster clone)

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Semantic Index | LanceDB (vector + FTS + RRF) | Code similarity search |
| AST Index | DuckDB (SQL) | Structural pattern matching |
| Graph Index | DuckDB (recursive CTE) | Call graph traversal |
| Chunking | Tree-sitter (AST-aware) | Semantic code boundaries |
| Embedding | CodeBERT (512-dim) | Semantic vectors |
| Git Sync | GitPython | Repository management |
| Config | Pydantic + YAML | Schema validation |

---

## Document Guide

This specification package contains 5 main documents plus supporting testing documentation:

### Core Specification Documents

#### 1. **srd.md** (Software Requirements Document)
**Purpose:** What to build (requirements)  
**Sections:**
- User stories and business goals
- 10 functional requirements (FR-001 to FR-010)
- 29 non-functional requirements (NFR-P1 to NFR-PB2)
- Success criteria and out-of-scope items

**Read this if:** You need to understand business needs and acceptance criteria

---

#### 2. **specs.md** (Technical Specification)
**Purpose:** How to build it (design)  
**Sections:**
- Architecture overview (partition-based)
- 6 core components (CodeIndex, CodePartition, RepositoryTracker, etc.)
- API specifications (enhanced `pos_search_project` with filters)
- Data models (Pydantic config, database schemas)
- Security considerations
- Performance optimizations

**Read this if:** You need to understand the technical design and architecture

---

#### 3. **tasks.md** (Implementation Tasks)
**Purpose:** Implementation plan (what to do, in what order)  
**Sections:**
- 7 implementation phases (0-6)
- 26 detailed tasks with acceptance criteria
- Time estimates (25-30 hours total)
- Dependencies and critical path
- Risk mitigation strategies

**Read this if:** You're implementing the system and need a step-by-step plan

---

#### 4. **implementation.md** (Implementation Guidance)
**Purpose:** How to implement (code patterns, deployment, troubleshooting)  
**Sections:**
- 8 concrete code patterns with examples
- Deployment guidance (3-phase rollout)
- Rollback procedures (< 2 minutes)
- Troubleshooting guide (7 common issues)
- Success criteria checklist

**Read this if:** You're writing code and need concrete patterns to follow

---

#### 5. **testing/** (Testing Documentation)
**Purpose:** How to validate (test cases and strategy)  
**Files:**
- `requirements-list.md`: All 39 requirements with traceability
- `functional-tests.md`: 27 test cases for functional requirements
- `nonfunctional-tests.md`: 29 test cases for non-functional requirements
- `test-strategy.md`: Testing methodology (unit/integration/E2E, 70/20/10 pyramid)

**Read this if:** You're writing tests or verifying requirements are met

---

### Supporting Documents

#### 6. **supporting-docs/** (Design Documents)
- `INDEX.md`: Extracted insights from design document (47 insights)
- Original design document reference

**Read this if:** You need to trace requirements back to original design decisions

---

## Quick Start

### For Product Managers
1. Read **srd.md** for requirements and acceptance criteria
2. Review **tasks.md** for timeline and effort estimates
3. Check **testing/requirements-list.md** for requirement coverage

### For Architects
1. Read **specs.md** for technical architecture
2. Review **implementation.md** Section 1 for code patterns
3. Check **supporting-docs/INDEX.md** for design insights

### For Developers
1. Start with **tasks.md** Phase 0 (Config & Schema)
2. Follow **implementation.md** code patterns for each phase
3. Write tests using **testing/functional-tests.md** and **testing/nonfunctional-tests.md**
4. Reference **specs.md** for detailed API/schema definitions

### For QA Engineers
1. Read **testing/test-strategy.md** for overall approach
2. Implement tests from **testing/functional-tests.md** (27 tests)
3. Implement tests from **testing/nonfunctional-tests.md** (29 tests)
4. Use **testing/requirements-list.md** for traceability matrix

---

## Implementation Phases

| Phase | Name | Duration | Key Deliverables |
|-------|------|----------|------------------|
| 0 | Config & Schema | 3-4 hours | Config models, schema migrations |
| 1 | Repository Tracking | 3-4 hours | RepositoryTracker, RepositorySyncer |
| 2 | CodePartition Container | 4-5 hours | Dynamic partition discovery, health checks |
| 3 | Incremental Indexing | 5-6 hours | Parse-once-index-thrice, changed file detection |
| 4 | Partition Lifecycle | 4-5 hours | CRUD operations, soft delete, orphaned data detection |
| 5 | Cross-Repo Queries | 3-4 hours | Partition routing, cross-repo graph traversal |
| 6 | Query Workflows | 3-4 hours | Extraction workflows, YAML/JSON export |

**Total:** 25-30 hours  
**Critical Path:** 0 → 1 → 2 → 3 → 5 → 6 (22-27 hours)

---

## Key Requirements Summary

### Functional Requirements (10)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | Multi-Repository Indexing | P0 |
| FR-002 | Partition Management | P0 |
| FR-003 | Repository State Tracking | P0 |
| FR-004 | Incremental Indexing | P0 |
| FR-005 | Cross-Repository Query Filtering | P0 |
| FR-006 | Cross-Repo Call Graph Traversal | P1 |
| FR-007 | Git Repository Synchronization | P0 |
| FR-008 | Semantic Convention Extraction | P0 |
| FR-009 | Machine-Readable Output | P0 |
| FR-010 | Partition Lifecycle Management | P1 |

### Non-Functional Requirements (29)

**Performance (5):**
- NFR-P1: Primary partition p95 < 50ms
- NFR-P2: Instrumentors partition p95 < 200ms
- NFR-P3: Extraction < 15 minutes
- NFR-P4: Incremental update < 5 seconds
- NFR-P5: Cold start < 10 minutes

**Storage (2):**
- NFR-ST1: Total disk < 3GB
- NFR-ST2: Incremental storage (no duplication)

**Reliability (4):**
- NFR-R1: Graceful parse error handling
- NFR-R2: Per-repo health checks
- NFR-R3: Rollback < 2 minutes
- NFR-R4: Sync failure isolation

**Scalability (4):**
- NFR-S1: Scale to 270 instrumentors
- NFR-S2: Single-table architecture
- NFR-S3: Support 437K chunks
- NFR-S4: Parse error rate < 5%

**Operability (4):**
- NFR-O1: Soft delete with archival
- NFR-O2: Orphaned data detection
- NFR-O3: Partition migration
- NFR-O4: Config validation

**Security (3):**
- NFR-SEC1: No embedded credentials
- NFR-SEC2: Path traversal prevention
- NFR-SEC3: Error message safety

**Integration (3):**
- NFR-I1: Cascading health check integration
- NFR-I2: AST-aware chunking integration
- NFR-I3: Backward compatibility

**Performance Benchmarks (2):**
- NFR-PB1: Sync success rate > 95%
- NFR-PB2: Parse-once >= 2x faster

---

## Success Metrics

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Primary partition query latency | p95 < 50ms | 100 queries, p95 calculation |
| Instrumentors partition query latency | p95 < 200ms | 100 queries, p95 calculation |
| Extraction workflow duration | < 15 minutes | Single instrumentor, full workflow |
| Incremental index update | < 5 seconds | 10 changed files |
| Cold start time | < 10 minutes | 270 instrumentors (concurrent) |
| Total disk usage | < 3GB | `du -sh .indexes/code/` |

### Business Metrics

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Instrumentor analysis time | 3 hours | 15 minutes | 12x faster |
| Supported instrumentors | 10 | 270 | 27x scale |
| Manual effort (270 instrumentors) | 810 hours | 68 hours | 92% reduction |
| Accuracy | 80% (manual errors) | 100% (automated) | Eliminates human error |

---

## Risks and Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Performance targets not met | High | Medium | Profile early, optimize incrementally, implement concurrent indexing |
| Parse error rate > 5% | Medium | Low | Graceful handling, skip problematic files, log warnings |
| Disk usage exceeds 3GB | Medium | Medium | Use sparse checkout, monitor incrementally, archive old partitions |
| Git sync failures | Medium | Low | Isolate failures per-repo, retry with backoff, mark failed state |
| Complex refactoring required | High | Low | Incremental migration, feature flags, rollback capability |

---

## Dependencies

**Prerequisites (Must be complete before starting):**
- AST-Aware Code Chunking implementation (completed)
- Cascading Health Check Architecture (completed)
- Tree-sitter language support (Python, TypeScript, Go)

**External Dependencies:**
- Git repositories accessible (SSH keys configured)
- OpenTelemetry instrumentor repositories available
- Disk space available (~3GB)

---

## Testing Summary

**Total Test Cases:** 56 (27 functional + 29 non-functional)  
**Coverage Target:** >= 85% code coverage  
**Test Types:**
- Unit Tests (70%): Fast, isolated, mocked dependencies
- Integration Tests (20%): Multi-component workflows
- E2E Tests (10%): Full extraction workflows

**Test Execution:**
- Local: `pytest` (< 5 minutes for unit + integration)
- CI/CD: GitHub Actions on every commit
- Performance: Nightly benchmarks

---

## Approval and Sign-Off

### Specification Review

**Technical Review:**
- [ ] Architecture approved by: _______________ Date: _______
- [ ] API design approved by: _______________ Date: _______
- [ ] Performance targets approved by: _______________ Date: _______

**Business Review:**
- [ ] Requirements approved by: _______________ Date: _______
- [ ] Timeline approved by: _______________ Date: _______
- [ ] Success criteria approved by: _______________ Date: _______

### Implementation Authorization

- [ ] Ready for implementation: YES / NO
- [ ] Approved by: _______________ Date: _______

---

## Change History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-11-12 | 1.0 | AI Agent | Initial specification created |

---

## Contact and Support

**Specification Questions:**
- Review design document in `supporting-docs/`
- Check `specs.md` for technical details
- Reference `srd.md` for requirements

**Implementation Questions:**
- Follow `tasks.md` for step-by-step plan
- Use `implementation.md` for code patterns
- Reference `testing/` for test cases

**Issue Reporting:**
- Open GitHub issue with:
  - Specification section reference (e.g., "specs.md Section 2.3")
  - Description of issue or ambiguity
  - Proposed resolution (if any)

---

## Appendix

### Glossary

| Term | Definition |
|------|------------|
| **Partition** | Logical grouping of repositories with independent indexes (e.g., primary, instrumentors) |
| **Semantic Convention** | OpenTelemetry standard for span attributes and naming (e.g., `http.method`, `http.url`) |
| **Instrumentor** | Library that automatically adds OpenTelemetry instrumentation to frameworks (e.g., FastAPI, LangChain) |
| **Sparse Checkout** | Git feature to clone only specific subdirectories (saves disk space) |
| **Parse-Once-Index-Thrice** | Optimization: single Tree-sitter parse populates all 3 indexes |
| **RRF** | Reciprocal Rank Fusion (combines vector search + full-text search results) |
| **AST** | Abstract Syntax Tree (structured representation of source code) |
| **p95 Latency** | 95th percentile latency (95% of queries complete faster than this) |

### Acronyms

- **FR:** Functional Requirement
- **NFR:** Non-Functional Requirement
- **AST:** Abstract Syntax Tree
- **FTS:** Full-Text Search
- **RRF:** Reciprocal Rank Fusion
- **CRUD:** Create, Read, Update, Delete
- **E2E:** End-to-End
- **CI/CD:** Continuous Integration/Continuous Deployment
- **p95:** 95th percentile
- **BYOI:** Bring Your Own Instrumentor

### References

- **Design Document:** `.praxis-os/design/2025-11-12-multi-repo-code-intelligence.md`
- **AST-Aware Chunking Spec:** `.praxis-os/specs/completed/2025-11-XX-ast-aware-code-chunking/`
- **Cascading Health Check Spec:** `.praxis-os/specs/completed/2025-11-XX-cascading-health-check-architecture/`
- **prAxIs OS Standards:** `.praxis-os/standards/`

---

**End of Specification Package**

---

