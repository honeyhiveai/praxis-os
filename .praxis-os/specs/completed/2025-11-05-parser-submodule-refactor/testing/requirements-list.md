# Requirements List for Testing

**Extracted from:** srd.md  
**Date:** 2025-11-05

---

## Functional Requirements

| FR ID | Description | Acceptance Criteria | Priority |
|-------|-------------|---------------------|----------|
| FR-001 | Extensible Parser Architecture | Create parsers/ submodule, plugin-like pattern, base classes | High |
| FR-002 | Module Size Constraints | All modules ≤500 lines, target 50-400 lines per file | High |
| FR-003 | Backward Compatibility | Old imports work with deprecation warnings | High |
| FR-004 | Plugin-Like Parser Pattern | New parsers added without modifying existing code | High |
| FR-005 | Incremental Migration with Rollback | 8-phase migration, each phase independently verifiable | High |
| FR-006 | Defensive Format Parsing | Semantic scoring with multi-signal evaluation | High |
| FR-007 | Phase Shift Detection | Detect phase header shifts (Phase 0→1, Phase 3→1) | High |
| FR-008 | Sequential Phase Validation | Reject non-sequential phases (1→3 skipping 2) | High |
| FR-009 | Cross-Phase Dependencies | Validate dependencies don't reference future phases | Medium |
| FR-010 | Task ID Normalization | Normalize task IDs (3.1, 3-1, 3_1 → 3.1) | Medium |
| FR-011 | Dependency Format Preservation | Preserve original dependency strings in metadata | Low |

---

## Non-Functional Requirements

### Performance (NFR-P)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-P1 | Parsing Speed | ≤100ms for files up to 50KB, ±5% variance acceptable | High |
| NFR-P2 | Memory Efficiency | Peak memory ≤50MB for typical specs, no memory leaks | Medium |

### Reliability (NFR-R)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-R1 | Zero Regressions | 100% of existing specs parse identically, all 529+ tests pass | Critical |
| NFR-R2 | Error Handling | All parse errors throw ParseError with actionable messages | High |

### Maintainability (NFR-M)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-M1 | Module Size Limits | Max 500 lines per module, enforced by hooks | High |
| NFR-M2 | Code Organization | Clear separation of concerns, no circular imports | High |
| NFR-M3 | Documentation | Every public function/class has docstring | Medium |

### Testability (NFR-T)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-T1 | Test Coverage | ≥85% code coverage, 100% for critical paths | High |
| NFR-T2 | Test Isolation | Unit tests run independently, no interdependencies | High |
| NFR-T3 | Test Speed | Full suite <30s, individual modules <2s | Medium |

### Compatibility (NFR-C)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-C1 | Backward Compatibility | Old imports work with deprecation warnings until v2.0 | High |
| NFR-C2 | Python Version | Support Python 3.9+ | High |
| NFR-C3 | Dependency Stability | No new dependencies beyond mistletoe, pyyaml, pydantic | Medium |

### Extensibility (NFR-E)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-E1 | Parser Addition Effort | New parser ≤4 hours, zero existing file modifications | High |
| NFR-E2 | Shared Utility Reuse | ≥60% code reuse for new parsers | Medium |

### Deployment (NFR-D)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-D1 | Migration Safety | 8-phase incremental migration, each independently verifiable | High |
| NFR-D2 | Zero Downtime | Refactor deployable without service interruption | Medium |

### Quality Assurance (NFR-Q)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-Q1 | Linting Compliance | Zero linting errors (pylint, flake8, mypy), type hints on all public functions | High |
| NFR-Q2 | Code Review | All changes reviewed by senior developer/architect | Medium |

### Configuration (NFR-SC)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-SC1 | Scoring Thresholds | PHASE_THRESHOLD=30.0, TASK_THRESHOLD=30.0, configurable via constructor | High |
| NFR-SC2 | Scoring Signals | Multi-signal evaluation, signals tunable without code changes | High |

---

## Summary

- **Total Functional Requirements:** 11
- **Total Non-Functional Requirements:** 16
- **Total Requirements to Test:** 27

**Categories:**
- Performance: 2 NFRs
- Reliability: 2 NFRs (including CRITICAL NFR-R1: Zero Regressions)
- Maintainability: 3 NFRs
- Testability: 3 NFRs
- Compatibility: 3 NFRs
- Extensibility: 2 NFRs
- Deployment: 2 NFRs
- Quality Assurance: 2 NFRs
- Configuration: 2 NFRs

**Critical Requirements:**
- **NFR-R1**: Zero Regressions - 100% of 529+ existing tests must pass
- **FR-007**: Phase Shift Detection - Prevents misassigned tasks (current production bug)
- **FR-008**: Sequential Phase Validation - Validates phase ordering

