# Requirements List for Testing

**Extracted from:** srd.md  
**Date:** 2025-11-06

---

## Functional Requirements

| FR ID | Description | Acceptance Criteria | Priority |
|-------|-------------|---------------------|----------|
| FR-001 | Query Prepend Generation | Prepends generated for all search results with gamification content | High |
| FR-002 | Query Tracking and Persistence | All queries logged to SQLite with session context | High |
| FR-003 | Query Diversity Classification | Queries classified into 5 angles (conceptual, location, implementation, critical, troubleshooting) | High |
| FR-004 | Behavioral Drift Detection | Diversity drops detected, prepends strengthened automatically | Medium |
| FR-005 | pos_search_project - Unified Search Tool | Single tool routes to 6 search actions (search_standards, search_code, search_ast, find_callers, find_dependencies, find_call_paths) | High |
| FR-006 | pos_workflow - Workflow Execution Tool | Action-based dispatch for 14 workflow operations | High |
| FR-007 | pos_browser - Browser Automation Tool | Action-based dispatch for browser operations with isolated Playwright sessions | High |
| FR-008 | pos_filesystem - File Operations Tool | Safe file operations with path validation and gitignore respect | High |
| FR-009 | get_server_info - Server Status Tool | Returns server metadata, health status, behavioral metrics, version info | Medium |
| FR-010 | Tool Auto-Discovery and Registration | ToolRegistry discovers tools from tools/ directory and registers automatically | High |
| FR-011 | Standards Search (Hybrid: Vector + FTS + RRF + Rerank) | Hybrid search with vector search + FTS + RRF fusion + optional reranking | High |
| FR-012 | Code Semantic Search (LanceDB) | CodeBERT embeddings for semantic code search | Medium |
| FR-013 | Code Graph Traversal (DuckDB) | Recursive CTEs for call graph queries | Medium |
| FR-014 | AST Structural Search (Tree-sitter) | Structural code search with Tree-sitter parsers | Medium |
| FR-015 | File Watcher (Incremental Index Updates) | Monitors paths, triggers incremental updates within 5s | High |
| FR-016 | Index Health Checks and Auto-Repair | Detects corrupted indexes on startup, auto-rebuilds | High |
| FR-017 | Phase-Gated Execution | Sequential phase execution with validation gates | High |
| FR-018 | Evidence Validation (Multi-Layer) | 5-layer validation (field, type, custom, cross-field, artifact) | High |
| FR-019 | Hidden Evidence Schemas | Schemas hidden from agents to force real work | High |
| FR-020 | Workflow State Persistence | Persistent state across sessions, resumable | High |
| FR-021 | Isolated Playwright Sessions | Per-conversation browser sessions via SessionMapper | Medium |
| FR-022 | Browser Actions | Comprehensive browser automation actions (navigate, click, type, etc.) | Medium |
| FR-023 | Pydantic v2 Schema Validation | Config validation with fail-fast error messages | High |
| FR-024 | Config-Driven Language Support | Add languages via YAML config only | Medium |
| FR-025 | Fail-Fast Validation | All validation errors at startup, not runtime | High |

---

## Non-Functional Requirements

### Performance (NFR-P)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-P1 | Server Cold Start Time | <30s p95 (from process start to "Server ready") | High |
| NFR-P2 | Config Load Time | <100ms p95 (YAML read to MCPConfig instantiated) | Medium |
| NFR-P3 | Search Latency (Hybrid Search) | <200ms p95 for <10K documents | High |
| NFR-P4 | Search Latency (Code Graph Traversal) | <100ms p95 for <50K symbols | Medium |
| NFR-P5 | Incremental Index Update Latency | <5s p95 (file save to searchable) | High |
| NFR-P6 | Prepend Generation Overhead | <5ms p95 | Low |
| NFR-P7 | Memory Usage | <2GB RSS during normal operation | Medium |

### Reliability (NFR-R)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-R1 | Uptime / Crash Rate | 24+ hours without crashes | High |
| NFR-R2 | Health Check Coverage | 95%+ of corruption issues detected | High |
| NFR-R3 | Auto-Repair Success Rate | 90%+ of detected issues repaired | Medium |
| NFR-R4 | Graceful Degradation | Falls back to vector-only if FTS fails | Medium |
| NFR-R5 | Data Integrity | Incremental updates produce identical results to full rebuild | High |

### Security (NFR-S)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-S1 | Adversarial Design Enforcement | 99%+ of gaming attempts rejected | High |
| NFR-S2 | Query Sanitization | No PII in logs | Medium |
| NFR-S3 | Path Traversal Prevention | All path traversal attempts blocked | High |
| NFR-S4 | Secrets Management | No secrets in git, logs, or error messages | High |

### Scalability (NFR-SC)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-SC1 | Document Scaling | Supports up to 50K documents without degradation | Medium |
| NFR-SC2 | Symbol Scaling | Supports up to 100K code symbols | Medium |
| NFR-SC3 | Concurrent Query Handling | 10 concurrent queries without degradation | Low |

### Maintainability (NFR-M)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-M1 | Code Quality | 0 circular dependencies | High |
| NFR-M2 | Clean Architecture | 0 cross-subsystem imports | High |
| NFR-M3 | Test Coverage | ≥60% integration test coverage | Medium |
| NFR-M4 | Error Message Quality | All ActionableError messages include how_to_fix | High |
| NFR-M5 | Documentation Coverage | All public APIs documented | Medium |

### Usability (NFR-U)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-U1 | Error Discoverability | All errors actionable within 1 search | High |
| NFR-U2 | Fail-Fast Validation | All config errors at startup, not runtime | High |
| NFR-U3 | Behavioral Feedback | Query diversity metrics visible | Medium |
| NFR-U4 | Tool Discoverability | RAG indexes workflow metadata | Medium |

### Extensibility (NFR-E)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-E1 | Config-Driven Languages | Add language with 1 YAML change | High |
| NFR-E2 | Pluggable Tools | Drop tool in tools/ directory | High |
| NFR-E3 | Custom Workflows | Create workflow without core code changes | Medium |

### Portability (NFR-PO)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-PO1 | MacOS Support | Runs on macOS 12+ | High |
| NFR-PO2 | Linux Support | Runs on Ubuntu 20.04+ | High |
| NFR-PO3 | WSL2 Support | Runs on Windows WSL2 | Medium |

### Compatibility (NFR-C)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-C1 | MCP Protocol Compatibility | Works with all MCP clients | High |
| NFR-C2 | Index Format Backwards Compatibility | Reads old LanceDB/DuckDB indexes | High |
| NFR-C3 | Python Version Support | Supports Python 3.10+ | High |

### Observability (NFR-O)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-O1 | Structured Logging | JSON logs with context | Medium |
| NFR-O2 | Query Metrics Tracking | All queries logged with metadata | High |
| NFR-O3 | Performance Metrics | Latency metrics (p50/p95/p99) logged | Medium |
| NFR-O4 | Behavioral Metrics | Query diversity trends tracked | High |

### Testability (NFR-T)

| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|
| NFR-T1 | Unit Test Isolation | Unit tests run without external resources | High |
| NFR-T2 | Integration Test Coverage | ≥70% integration test coverage | Medium |
| NFR-T3 | Performance Test Repeatability | <5% variance across runs | Medium |

---

## Summary

- **Total Functional Requirements:** 25
- **Total Non-Functional Requirements:** 44
- **Total Requirements to Test:** 69

**Categories:**
- Performance: 7 NFRs
- Reliability: 5 NFRs
- Security: 4 NFRs
- Scalability: 3 NFRs
- Maintainability: 5 NFRs
- Usability: 4 NFRs
- Extensibility: 3 NFRs
- Portability: 3 NFRs
- Compatibility: 3 NFRs
- Observability: 4 NFRs
- Testability: 3 NFRs

