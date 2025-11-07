# Requirements List for Testing

**Extracted from:** srd.md  
**Date:** 2025-11-05

---

## Functional Requirements

| FR ID | Description | Acceptance Criteria | Priority |
|-------|-------------|---------------------|----------|
| FR-001 | Uniform Container Entry Point | Each index has container.py with all public methods | High |
| FR-002 | Registry-Based Index Discovery | IndexManager discovers indexes via registry pattern | High |
| FR-003 | File-Based Lock for Corruption Prevention | Advisory file locks prevent concurrent write access | Critical |
| FR-004 | Database Consolidation (LanceDB + DuckDB) | Eliminate SQLite, use only LanceDB + DuckDB | High |
| FR-005 | Corruption Detection and Auto-Repair | Detect corruption patterns, auto-rebuild index | Critical |
| FR-006 | Shared Utility Modules (DRY) | Database connections, embedding models in shared modules | High |
| FR-007 | Independent Submodule Internals | Index internals isolated, no cross-index dependencies | High |
| FR-008 | Incremental Update via FileWatcher | File changes trigger incremental index updates | High |
| FR-009 | BaseIndex Abstract Interface | All indexes implement BaseIndex interface | High |
| FR-010 | Health Check Three-Tier Validation | Existence + integrity + operational validation | High |

---

## Non-Functional Requirements

### Performance (NFR-P)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-P1 | Health Check Response Time | <5s per index, <15s total at startup | High |
| NFR-P2 | Index Build Time | Standards <2min, Code <3min, Incremental <10s | High |
| NFR-P3 | Query Response Time | Semantic p95 <200ms, AST p95 <100ms, Graph p95 <500ms | High |

### Reliability (NFR-R)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-R1 | Corruption Prevention | 0 corruption incidents/month (baseline: 2-3/week) | Critical |
| NFR-R2 | Auto-Repair Success Rate | 100% startup, 95%+ runtime, <60s standards, <120s code | Critical |
| NFR-R3 | Index Build Success Rate | 100% first-time, 100% rebuild | High |
| NFR-R4 | Data Integrity | Row count ±5%, no data loss, updates <1min | High |

### Maintainability (NFR-M)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-M1 | Code Reuse via Shared Utilities | <50 lines duplication (baseline: ~200 lines) | High |
| NFR-M2 | Test Coverage | ≥80% unit, 100% integration critical paths | High |
| NFR-M3 | Code Complexity | 0 IndexManager branches, container <300 lines, complexity <10/method | High |
| NFR-M4 | Documentation and Discoverability | All submodules documented, onboarding <15min | Medium |

### Scalability (NFR-SC)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-SC1 | Index Addition Scalability | <30min (baseline: ~4 hours), 3 steps, 0 IndexManager changes | High |
| NFR-SC2 | Concurrent Query Support | Unlimited readers, no query interference | High |

### Portability (NFR-PT)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-PT1 | Platform Support | POSIX full support, Windows graceful degradation, Python 3.10+ | High |
| NFR-PT2 | Database Portability | LanceDB ≥0.13.0, DuckDB ≥0.9.0, no vendor-specific SQL | High |

### Usability (NFR-U)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-U1 | Error Messages (Actionable) | All errors include what/why/how_to_fix | High |
| NFR-U2 | Logging and Observability | Structured logging, visual indicators (✅/⚠️/❌) | Medium |

### Testability (NFR-T)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-T1 | Unit Test Isolation | Independent tests, mock dependencies, <30s suite | High |
| NFR-T2 | Integration Test Coverage | Corruption recovery, lock behavior, registry discovery | High |
| NFR-T3 | Corruption Scenario Testing | Mock LanceDB errors, verify detection/repair | High |

### Security (NFR-SEC)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-SEC1 | File System Security | Restricted permissions (600 lock, 644 data), advisory locks | Medium |
| NFR-SEC2 | Dependency Security | Pinned versions, no eval/exec | Medium |

---

## Summary

- **Total Functional Requirements:** 10
- **Total Non-Functional Requirements:** 22
- **Total Requirements to Test:** 32

**Categories:**
- Performance: 3 NFRs
- Reliability: 4 NFRs (2 CRITICAL: R1 Corruption Prevention, R2 Auto-Repair)
- Maintainability: 4 NFRs
- Scalability: 2 NFRs
- Portability: 2 NFRs
- Usability: 2 NFRs
- Testability: 3 NFRs
- Security: 2 NFRs

**Critical Requirements:**
- **FR-003**: File-Based Lock - Prevents corruption from concurrent access (2-3/week → 0/month)
- **FR-005**: Corruption Detection and Auto-Repair - Transparent recovery
- **NFR-R1**: Corruption Prevention - 0 incidents per month
- **NFR-R2**: Auto-Repair Success - 100% startup, 95%+ runtime

**High-Impact Business Goals:**
- Index Addition Time: 4 hours → 30 minutes (FR-002, NFR-SC1)
- Corruption Incidents: 2-3/week → 0/month (FR-003, NFR-R1)
- Database Technologies: 3 → 2 (FR-004)
- Discovery Time: 15 min → 2 min (FR-001, NFR-M4)

