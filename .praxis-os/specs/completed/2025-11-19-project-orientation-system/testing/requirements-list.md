# Requirements List for Testing

**Project:** Project Orientation System  
**Date:** 2025-11-19  
**Source:** srd.md

---

## Functional Requirements

| FR ID | Description | Acceptance Criteria | Priority |
|-------|-------------|---------------------|----------|
| FR-001 | Inline Metadata Discovery for Orientation | - Detects **Metadata**: orientation=true in standards files<br>- Extracts orientation-specific metadata fields (priority, category, queries)<br>- Uses regex-based parsing consistent with standards index<br>- Defaults to path-based metadata when missing | Critical |
| FR-002 | mcp.yaml Project Orientation Extension | - mcp.yaml schema extended with optional `project.orientation` section<br>- Orientation section supports list of query objects with metadata<br>- Configuration validated via Pydantic schemas<br>- Multiple configuration sources supported (inline OR mcp.yaml OR both) | Critical |
| FR-003 | Automatic Project Orientation Execution | - Base orientation query 10 triggers project orientation discovery<br>- Project queries executed in priority order (critical → high → medium)<br>- Each project query executed via pos_search_project<br>- Execution completes within 1 minute for typical projects (5-10 queries) | Critical |
| FR-004 | Error-Resistant Metadata Parsing | - Missing metadata → use path-based defaults or skip<br>- Malformed key=value pairs → skip bad pairs, parse valid pairs<br>- Typo in **Metadata**: marker → return defaults, log warning<br>- Bad type coercion → skip field, log warning, use remaining fields<br>- NO indexing failures or crashes due to metadata errors | Critical |
| FR-005 | Query Execution Order and Dependencies | - Queries executed in priority order (critical=1, high=2, medium=3)<br>- Within same priority, queries executed in definition order<br>- Optional `depends_on` field for explicit dependencies<br>- Dependency validation prevents circular dependencies | High |
| FR-006 | Standards Metadata Pattern Compatibility | - Orientation metadata uses **Metadata**: key=value format<br>- Type coercion follows standards parsing (bool, int, string)<br>- Error handling follows standards parsing (skip malformed, log warnings)<br>- Code reuse: shared _extract_inline_metadata() method or equivalent | High |
| FR-007 | Base Orientation Integration | - Base orientation query 10 explicitly mentions project orientation discovery<br>- AI agents query for "project orientation" or "project-specific queries"<br>- Discovery returns project orientation metadata and query list<br>- AI agents execute project queries after base orientation complete | Critical |
| FR-008 | Orientation Metadata Schema | - Required fields: orientation=true, query (string)<br>- Optional fields: priority (1-3), category, description, depends_on<br>- Schema documented in standards for project maintainers<br>- Validation provides actionable error messages | High |
| FR-009 | No Consumer Tooling Requirements | - Orientation works with markdown files only (no build step)<br>- mcp.yaml extension optional, not required<br>- No pre-commit hooks needed for validation<br>- Malformed metadata degrades gracefully (no user intervention) | Critical |

---

## Non-Functional Requirements

| NFR ID | Category | Description | Measurement Criteria | Priority |
|--------|----------|-------------|----------------------|----------|
| NFR-P1 | Performance | Orientation Execution Time | - Project orientation discovery and execution: < 1 minute for 5-10 queries<br>- Inline metadata parsing overhead: < 100ms per markdown file<br>- mcp.yaml parsing overhead: < 50ms per configuration load | High |
| NFR-P2 | Performance | Indexing Performance | - Metadata extraction shall not degrade standards index build time by more than 5%<br>- Parsing errors shall not cause retry loops or significant slowdowns | High |
| NFR-R1 | Reliability | Graceful Degradation | - 100% graceful degradation on malformed metadata (skip, log warning, continue)<br>- Zero indexing failures due to metadata syntax errors<br>- Zero orientation execution failures due to bad metadata | Critical |
| NFR-R2 | Reliability | Error Resilience | - Missing metadata → use defaults or skip project orientation<br>- Malformed key=value pairs → parse valid pairs, skip bad pairs<br>- Typo in marker → log warning, return defaults<br>- Bad type coercion → skip field, use remaining fields | Critical |
| NFR-U1 | Usability | Zero Tooling Requirements | - No additional tooling required in consumer projects<br>- No pre-commit hooks required for metadata validation<br>- No build step required for orientation to function<br>- Orientation works with markdown files and mcp.yaml only | Critical |
| NFR-U2 | Usability | Error Messages | - Actionable error/warning messages for malformed metadata<br>- Log warnings with file path, line number, and specific issue<br>- Error messages guide users to fix metadata without deep framework knowledge | High |
| NFR-U3 | Usability | Documentation Clarity | - Orientation metadata schema documented with examples<br>- Project maintainers can implement orientation without framework expertise<br>- Examples cover common patterns (inline markdown, mcp.yaml extension) | High |
| NFR-M1 | Maintainability | Code Reuse | - Reuse existing _extract_inline_metadata() parsing logic<br>- Share error handling patterns between standards and orientation metadata<br>- Leverage existing Pydantic schema infrastructure for mcp.yaml extensions | High |
| NFR-M2 | Maintainability | Test Coverage | - Minimum 90% code coverage for metadata parsing and orientation execution<br>- Comprehensive test scenarios: valid, missing, malformed, typos, bad types<br>- Integration tests for base + project orientation workflow | High |
| NFR-M3 | Maintainability | Code Quality | - Comprehensive Sphinx-style docstrings for all functions<br>- Full type hints (parameters and return types)<br>- Zero linting errors (flake8, mypy) | High |
| NFR-C1 | Compatibility | Configuration Schema Compatibility | - mcp.yaml extensions follow Pydantic v2 schema patterns<br>- Backward compatible: projects without orientation metadata continue working<br>- Forward compatible: new metadata fields added without breaking existing configs | Critical |
| NFR-C2 | Compatibility | Standards Index Compatibility | - Orientation metadata parsing compatible with existing standards index architecture<br>- No breaking changes to current standards markdown format<br>- Inline metadata pattern matches standards parsing design | High |
| NFR-S1 | Security | No Code Execution | - Regex-based parsing only (no eval(), exec(), or dynamic code execution)<br>- Metadata values treated as data, not code<br>- No command injection risk from malicious metadata | Critical |
| NFR-S2 | Security | Input Validation | - All metadata fields validated against expected types<br>- Query strings sanitized before execution<br>- Dependency graph validated to prevent infinite loops | Critical |

---

## Requirements Summary

### Functional Requirements
- **Total Functional Requirements:** 9
- **Critical Priority:** 6 (FR-001, FR-002, FR-003, FR-004, FR-007, FR-009)
- **High Priority:** 3 (FR-005, FR-006, FR-008)
- **FRs with Acceptance Criteria:** 9/9 (100%)

### Non-Functional Requirements
- **Total Non-Functional Requirements:** 14
- **Critical Priority:** 6 (NFR-R1, NFR-R2, NFR-U1, NFR-C1, NFR-S1, NFR-S2)
- **High Priority:** 8 (NFR-P1, NFR-P2, NFR-U2, NFR-U3, NFR-M1, NFR-M2, NFR-M3, NFR-C2)
- **NFRs with Measurement Criteria:** 14/14 (100%)

### Overall Summary
- **Total Requirements to Test:** 23
- **Critical Requirements:** 12 (52%)
- **High Priority Requirements:** 11 (48%)
- **Requirements with Criteria:** 23/23 (100%)

---

## Requirements by Category

### Metadata Discovery & Parsing
- FR-001, FR-004, FR-006, FR-008
- NFR-R1, NFR-R2, NFR-S1

### Configuration & Extensibility
- FR-002, FR-009
- NFR-C1, NFR-C2, NFR-U1

### Orientation Execution
- FR-003, FR-005, FR-007
- NFR-P1, NFR-P2

### Quality Attributes
- NFR-M1, NFR-M2, NFR-M3, NFR-U2, NFR-U3, NFR-S2

---

## Traceability to User Stories

| Requirement | Related User Stories |
|-------------|---------------------|
| FR-001 | Story 1 (AI Agent Self-Orientation), Story 2 (Project Maintainer Defines Orientation) |
| FR-002 | Story 2 (Project Maintainer Defines Orientation) |
| FR-003 | Story 1 (AI Agent Self-Orientation), Story 3 (Developer Benefits) |
| FR-004 | Story 2 (Project Maintainer Defines Orientation) |
| FR-005 | Story 2 (Project Maintainer Defines Orientation) |
| FR-006 | Story 4 (Framework Author Demonstrates Extensibility) |
| FR-007 | Story 1 (AI Agent Self-Orientation), Story 3 (Developer Benefits) |
| FR-008 | Story 2 (Project Maintainer Defines Orientation) |
| FR-009 | All Stories (cross-cutting requirement) |

---


