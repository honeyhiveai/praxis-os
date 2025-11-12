# Requirements Traceability Matrix

**Project:** AST-Aware Code Chunking with Import Penalty  
**Date:** 2025-11-11  
**Purpose:** Complete list of all requirements (FR, NFR) for test coverage mapping

---

## Functional Requirements (FR)

### FR-001: AST-Aware Code Chunking
- **Priority:** Critical
- **User Stories:** Story 1, Story 2
- **Description:** Parse source code with Tree-sitter and chunk at AST boundaries (function/class definitions)
- **Test Coverage:** `functional-tests.md` Test Case FT-001

### FR-002: Import Penalty Mechanism
- **Priority:** Critical
- **User Stories:** Story 1
- **Description:** Calculate import ratio and apply ranking penalty to import-heavy chunks
- **Test Coverage:** `functional-tests.md` Test Case FT-002

### FR-003: Token-Based Chunk Sizing
- **Priority:** Critical
- **User Stories:** Story 2, Story 4
- **Description:** Create chunks targeting ~500 tokens (±20%), respecting CodeBERT 514 token limit
- **Test Coverage:** `functional-tests.md` Test Case FT-003

### FR-004: Configuration-Driven Language Support
- **Priority:** High
- **User Stories:** Story 3
- **Description:** Support multiple languages via mcp.yaml config (no code changes per language)
- **Test Coverage:** `functional-tests.md` Test Case FT-004

### FR-005: Graceful Fallback to Line-Based Chunking
- **Priority:** High
- **User Stories:** Story 3, Story 4
- **Description:** Fall back to line-based chunking for unsupported languages or parse failures
- **Test Coverage:** `functional-tests.md` Test Case FT-005

### FR-006: Index Rebuild Capability
- **Priority:** High
- **User Stories:** Story 4
- **Description:** Support rebuilding code index with AST-aware chunking (<10 minutes for 100K LOC)
- **Test Coverage:** `functional-tests.md` Test Case FT-006

### FR-007: Configuration-Based Rollback
- **Priority:** High
- **User Stories:** Story 5
- **Description:** Quick rollback to line-based via config change (<5 minutes)
- **Test Coverage:** `functional-tests.md` Test Case FT-007

### FR-008: Health Check Integration
- **Priority:** High
- **User Stories:** Story 5
- **Description:** Integrate with Cascading Health Check Architecture, report component health
- **Test Coverage:** `functional-tests.md` Test Case FT-008

### FR-009: Import Chunk Grouping
- **Priority:** Medium
- **User Stories:** Story 1, Story 2
- **Description:** Group consecutive import statements into single chunk
- **Test Coverage:** `functional-tests.md` Test Case FT-009

### FR-010: Multi-Language Consistency
- **Priority:** Medium
- **User Stories:** Story 3
- **Description:** Apply AST chunking consistently across all configured languages
- **Test Coverage:** `functional-tests.md` Test Case FT-010

---

## Non-Functional Requirements (NFR)

### Performance

#### NFR-P1: Search Query Latency
- **Requirement:** p95 search latency <200ms with AST chunking
- **Measurement:** Prometheus metrics (p50 <100ms, p95 <200ms, p99 <300ms)
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-P1

#### NFR-P2: Index Build Time
- **Requirement:** Full rebuild <10 minutes for 100K LOC
- **Measurement:** Index build timing logs, progress logging
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-P2

#### NFR-P3: Import Penalty Application Overhead
- **Requirement:** Import penalty adds <1ms to query latency
- **Measurement:** Profiling search ranking stage
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-P3

### Reliability

#### NFR-R1: Graceful Degradation
- **Requirement:** Continue operating when AST parsing fails
- **Measurement:** Fallback count, health check status
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-R1

#### NFR-R2: Quick Recovery from Degradation
- **Requirement:** Rollback to line-based in <5 minutes
- **Measurement:** Rollback timing logs
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-R2

#### NFR-R3: Component Health Monitoring
- **Requirement:** Health monitoring via Cascading Health Check Architecture
- **Measurement:** Health check API output, metrics
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-R3

### Maintainability

#### NFR-M1: Configuration-Driven Language Support
- **Requirement:** Add languages via config only (no code changes)
- **Measurement:** Code review, language addition process
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-M1

#### NFR-M2: Test Coverage
- **Requirement:** Comprehensive test coverage (unit, integration, comparison, relevance)
- **Measurement:** Test suite execution, coverage reports
- **Test Coverage:** `test-strategy.md` Test Coverage Section

#### NFR-M3: Logging and Diagnostics
- **Requirement:** Comprehensive logging for debugging
- **Measurement:** Log output, issue resolution time
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-M3

### Scalability

#### NFR-SC1: Multi-Repository Support
- **Requirement:** AST chunking applies consistently across all partitions
- **Measurement:** Index health checks, partition metrics
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-SC1

#### NFR-SC2: Language Extensibility
- **Requirement:** Support 3+ languages at launch (Python, TypeScript, Go)
- **Measurement:** Supported language count, addition process (<1 hour)
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-SC2

### Usability

#### NFR-U1: Search Result Relevance
- **Requirement:** Prioritize implementation over imports (Relevance@5 >90%, FPR <15%)
- **Measurement:** Position tracking, human evaluation
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-U1

#### NFR-U2: Developer Experience
- **Requirement:** Transparent and predictable behavior
- **Measurement:** User feedback, documentation quality
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-U2

### Compatibility

#### NFR-C1: Backward Compatibility with Line-Based Chunking
- **Requirement:** Maintain line-based as fallback
- **Measurement:** Fallback testing, functionality tests
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-C1

#### NFR-C2: Integration with Existing RAG Infrastructure
- **Requirement:** Seamless integration with CodeIndex, SemanticIndex, health checks
- **Measurement:** Integration tests, architecture review
- **Test Coverage:** `nonfunctional-tests.md` Test Case NFT-C2

---

## Requirements Summary

**Total Requirements:** 27
- **Functional Requirements:** 10 (Critical: 3, High: 5, Medium: 2)
- **Non-Functional Requirements:** 17
  - Performance: 3
  - Reliability: 3
  - Maintainability: 3
  - Scalability: 2
  - Usability: 2
  - Compatibility: 2

---

## Traceability to User Stories

| User Story | Functional Requirements | NFRs |
|------------|------------------------|------|
| Story 1: Find Implementation Code | FR-001, FR-002, FR-009 | NFR-U1 |
| Story 2: Discover Relevant Code | FR-001, FR-003, FR-009 | NFR-U1 |
| Story 3: Work Across Languages | FR-004, FR-005, FR-010 | NFR-SC1, NFR-SC2, NFR-C1 |
| Story 4: Search Without Degradation | FR-003, FR-005, FR-006 | NFR-P1, NFR-P2, NFR-P3 |
| Story 5: Recover from Degradation | FR-007, FR-008 | NFR-R1, NFR-R2, NFR-R3 |

---

## Test Coverage Matrix

| Requirement ID | Functional Test | Non-Functional Test | Unit Test | Integration Test |
|----------------|-----------------|---------------------|-----------|------------------|
| FR-001 | FT-001 | - | Phase 2, Task 2.8 | Phase 3, Task 3.5 |
| FR-002 | FT-002 | NFT-U1 | Phase 2, Task 2.8 | Phase 3, Task 3.5 |
| FR-003 | FT-003 | NFT-P1 | Phase 2, Task 2.8 | Phase 3, Task 3.5 |
| FR-004 | FT-004 | NFT-M1, NFT-SC2 | Phase 1, Task 1.4 | Phase 3, Task 3.5 |
| FR-005 | FT-005 | NFT-R1, NFT-C1 | Phase 1, Task 1.4 | Phase 3, Task 3.5 |
| FR-006 | FT-006 | NFT-P2 | - | Phase 4, Task 4.1 |
| FR-007 | FT-007 | NFT-R2 | - | Phase 4, Task 4.1 |
| FR-008 | FT-008 | NFT-R3 | - | Phase 4, Task 4.1 |
| FR-009 | FT-009 | - | Phase 2, Task 2.8 | Phase 3, Task 3.5 |
| FR-010 | FT-010 | NFT-SC1 | Phase 2, Task 2.8 | Phase 4, Task 4.2 |

---

## Critical Success Criteria

**PRIMARY:** python-sdk query validation (FR-002, NFR-U1)
- Implementation ranks #1-2
- Imports rank #5+
- **Test:** Phase 4, Task 4.3 (PRIMARY VALIDATION)

**PERFORMANCE:** Search latency targets (NFR-P1, NFR-P2, NFR-P3)
- p95 query latency <200ms
- Index rebuild <10 minutes for 100K LOC
- **Test:** Phase 4, Task 4.4

**QUALITY:** Relevance metrics (NFR-U1)
- Relevance@5 >90%
- False Positive Rate <15%
- **Test:** Phase 4, Task 4.5

---


