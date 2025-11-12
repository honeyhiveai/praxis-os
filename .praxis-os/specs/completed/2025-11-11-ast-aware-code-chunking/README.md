# AST-Aware Code Chunking with Import Penalty

**Specification Package**  
**Created:** 2025-11-11  
**Status:** Final - Ready for Implementation  
**Estimated Effort:** 38 hours (~5 days)

---

## Executive Summary

**Problem:** Code semantic search returns import files (e.g., `__init__.py`) ranked higher than actual implementations, burying relevant results at position #4+. This is the first negative feedback on prAxIs OS code intelligence quality.

**Solution:** Use Tree-sitter AST parsing to chunk code at function/class boundaries (instead of arbitrary line counts), and apply a ranking penalty to import-heavy chunks. Configuration-driven design enables easy language support without code changes.

**Primary Success Metric:** python-sdk query ranks implementation #1-2, imports #5+ (currently: imports #1, implementation #4)

**Impact:**
- 🎯 **Relevance**: Implementation code ranks above imports
- ⚡ **Precision**: Function-level chunks vs arbitrary line splits
- 📊 **Quality**: Relevance@5 target >90% (from 60% baseline)
- 🔍 **Scalability**: Config-driven multi-language support

---

## Quick Start

### For Implementers

1. **Read Requirements**: Start with `srd.md` (Software Requirements Document)
2. **Review Design**: Read `specs.md` (Technical Specifications)
3. **Follow Tasks**: Execute `tasks.md` phases sequentially (Phase 0 → Phase 5)
4. **Use Patterns**: Reference `implementation.md` for code patterns and deployment
5. **Test Coverage**: Follow `testing/` documentation for comprehensive validation

### For Reviewers

1. **Business Case**: See `srd.md` sections 1-2 (Goals and User Stories)
2. **Technical Approach**: See `specs.md` sections 1-2 (Architecture and Components)
3. **Success Metrics**: See `testing/requirements-list.md` (Critical Success Criteria)
4. **Risk Assessment**: See `srd.md` section 6 (Out of Scope) and `implementation.md` section 6 (Troubleshooting)

---

## Document Structure

### Core Specifications (Required Reading)

#### 1. `srd.md` - Software Requirements Document
**Purpose:** Define WHAT to build and WHY

**Key Sections:**
- **Business Goals**: Improve relevance, reduce false positives, maintain performance, enable multi-repo
- **User Stories**: 5 stories (AI agent, developer, polyglot codebase, performance, rollback)
- **Functional Requirements**: 10 FRs (AST chunking, import penalty, token sizing, config-driven, fallback, rebuild, rollback, health check, import grouping, multi-language)
- **Non-Functional Requirements**: 17 NFRs (performance, reliability, maintainability, scalability, usability, compatibility)
- **Out of Scope**: Real-time re-indexing, per-file strategies, custom ranking, cross-language AST

**Read Time:** 20 minutes

---

#### 2. `specs.md` - Technical Specifications
**Purpose:** Define HOW to build it

**Key Sections:**
- **Architecture Overview**: Config-driven, AST-aware, graceful fallback
- **Component Design**: UniversalASTChunker, ASTExtractor (refactored), SemanticIndex (modified), mcp.yaml config
- **API Design**: pos_search_project tool, UniversalASTChunker API, mcp.yaml config schema
- **Data Models**: CodeChunk (9 fields), LanguageConfig, LanceDB schema
- **Security Design**: File path validation, config validation, Tree-sitter sandboxing
- **Performance Design**: Caching, parallel processing, HNSW tuning

**Read Time:** 30 minutes

---

#### 3. `tasks.md` - Implementation Tasks
**Purpose:** Define execution plan

**Key Sections:**
- **Implementation Phases**: 6 phases (Config Extraction → Refactor → Chunker → Integration → Validation → Docs)
- **Task Breakdown**: 42 tasks total with specific action items
- **Acceptance Criteria**: 4.7 criteria per task average (measurable, binary)
- **Dependencies**: Phase and task-level dependencies mapped
- **Validation Gates**: 6 phase gates with exit criteria
- **Critical Path**: 38 hours (~5 days) sequential execution

**Read Time:** 45 minutes

---

#### 4. `implementation.md` - Implementation Guidance
**Purpose:** Provide concrete implementation patterns

**Key Sections:**
- **Code Patterns**: 8 patterns (config-driven, AST chunking, import penalty, tree traversal, fallback, config schema, data model, import ratio)
- **Testing Strategy**: Unit, integration, E2E, performance, relevance (see `testing/` for details)
- **Deployment Guidance**: Gradual rollout (4 weeks), index rebuild, rollback procedure
- **Troubleshooting**: 5 common issues with diagnosis and solutions

**Read Time:** 25 minutes

---

### Testing Documentation

#### 5. `testing/requirements-list.md` - Requirements Traceability Matrix
**Purpose:** Map all requirements to test coverage

**Contents:**
- 10 Functional Requirements (Critical: 3, High: 5, Medium: 2)
- 17 Non-Functional Requirements (Performance: 3, Reliability: 3, Maintainability: 3, Scalability: 2, Usability: 2, Compatibility: 2)
- Traceability to user stories
- Test coverage matrix
- Critical success criteria (PRIMARY: python-sdk query)

---

#### 6. `testing/functional-tests.md` - Functional Test Plan
**Purpose:** Detailed test cases for all FRs

**Contents:**
- 10 test cases (FT-001 through FT-010)
- Each test case: objective, preconditions, test steps, expected results, failure criteria
- Estimated execution time: 4-6 hours

---

#### 7. `testing/nonfunctional-tests.md` - Non-Functional Test Plan
**Purpose:** Test cases for NFRs (performance, reliability, etc.)

**Contents:**
- 15 test cases (NFT-P1 through NFT-C2)
- Performance tests: query latency, index build time, import penalty overhead
- Reliability tests: graceful degradation, quick recovery, health monitoring
- Maintainability, scalability, usability, compatibility tests
- Estimated execution time: 6-8 hours

---

#### 8. `testing/test-strategy.md` - Testing Strategy
**Purpose:** Comprehensive testing approach

**Contents:**
- Test levels: Unit → Integration → E2E → Performance → Relevance
- Test data: Fixtures for Python, TypeScript, Go + real-world python-sdk case
- Test execution: CI pipeline, phase alignment
- Acceptance criteria: Phase gates, release criteria
- Test tooling: pytest, pytest-cov, profiling tools

---

### Supporting Documentation

#### 9. `supporting-docs/INDEX.md` - Supporting Documents Index
**Purpose:** Catalog and analyze design documents

**Contents:**
- Design document metadata
- Extracted insights (87 total: 25 requirements, 42 design, 20 implementation)
- Cross-document analysis
- Design maturity assessment

#### 10. `supporting-docs/2025-11-10-ast-aware-code-chunking-import-penalty.md` - Design Document
**Purpose:** Comprehensive technical design

**Contents:**
- Problem statement (real python-sdk failure case)
- Current state analysis
- Root cause analysis (line-based chunking issues)
- Proposed solution (AST-aware + import penalty)
- Design details (AST traversal, chunking algorithm, penalty mechanism)
- Implementation plan (4 phases)
- Performance analysis
- Migration strategy
- Success metrics
- Risks and mitigations

---

## Implementation Phases

### Phase 0: Config Extraction (8 hours)
**Objective:** Extract node type mappings from ast.py to mcp.yaml

**Deliverables:**
- mcp.yaml with language_configs (Python, TypeScript, Go)
- Pydantic config models
- Migration guide

**Validation Gate:** Config schema validated, backward compatible

---

### Phase 1: Refactor AST Extractor (4 hours)
**Objective:** Make ast.py config-driven

**Deliverables:**
- Refactored ast.py (~45 lines net reduction)
- Config reading logic
- Fallback for unconfigured languages
- Unit tests

**Validation Gate:** All existing AST tests passing, zero linter errors

---

### Phase 2: Build Universal Chunker (12 hours)
**Objective:** Create language-agnostic AST chunker

**Deliverables:**
- ast_chunker.py with UniversalASTChunker class
- CodeChunk dataclass
- Import grouping, definition chunking, penalty calculation
- 30+ unit tests (>85% coverage)

**Validation Gate:** Functions chunked at boundaries, imports grouped, penalty calculated correctly

---

### Phase 3: Integrate with SemanticIndex (6 hours)
**Objective:** Connect AST chunker to search

**Deliverables:**
- Modified semantic.py (uses UniversalASTChunker)
- LanceDB schema updated (chunk_type, import_ratio, import_penalty, symbols)
- Import penalty applied in search ranking
- Graceful fallback
- 5+ integration tests

**Validation Gate:** Test fixture query ranks implementation above imports

---

### Phase 4: Migration & Validation (6 hours)
**Objective:** Validate python-sdk query fix

**Deliverables:**
- Index rebuilt with AST chunking
- Comparison test suite (20 queries, AST vs line-based)
- python-sdk query validation (PRIMARY TEST)
- Performance profiling (p95 <200ms)
- Relevance metrics (Relevance@5 >90%)

**Validation Gate:** python-sdk query PASSED, performance targets met, relevance metrics achieved

---

### Phase 5: Documentation (2 hours)
**Objective:** Update docs and inline comments

**Deliverables:**
- Architecture docs updated
- Language config guide
- Migration notes
- Inline docstrings (100% public API coverage)

**Validation Gate:** Documentation complete, zero linter errors

---

## Success Metrics

### Primary Success Criterion
**python-sdk Query Validation:**
- Query: "EventsAPI list_events multiple filters array implementation"
- ✅ Implementation (`api/events.py`) ranks #1-2
- ✅ Imports (`api/__init__.py`) rank #5+

**Current State:** Imports #1, Implementation #4 (FAILURE)  
**Target State:** Implementation #1-2, Imports #5+ (SUCCESS)

### Performance Metrics
- ✅ p95 query latency <200ms
- ✅ Index rebuild <10 minutes for 100K LOC
- ✅ Import penalty overhead <1ms

### Quality Metrics
- ✅ Relevance@5 >90% (from 60% baseline)
- ✅ False Positive Rate <15% (from 40% baseline)
- ✅ Implementation rank #1-2 average (from #4)

---

## Dependencies

**External:**
- Tree-sitter (already installed: `tree-sitter-language-pack`)
- CodeBERT embeddings (already installed: `microsoft/codebert-base`)
- LanceDB (already installed)
- DuckDB (already installed)

**Internal:**
- Existing ASTExtractor (will be refactored)
- Existing SemanticIndex (will be modified)
- Cascading Health Check Architecture (will be extended)

**No new dependencies required!**

---

## Risks and Mitigations

### Risk 1: Tree-sitter Parse Failures
**Impact:** Index build fails or chunks incorrectly

**Mitigation:**
- Graceful fallback to line-based chunking
- Comprehensive error logging
- Health check reports degraded status
- Per-language rollback capability

---

### Risk 2: Import Penalty Too Aggressive/Ineffective
**Impact:** Imports still rank high OR implementations demoted incorrectly

**Mitigation:**
- Human evaluation (100 queries, Relevance@5)
- Comparison tests (AST vs line-based)
- Tunable penalty via config (default: 0.3)
- Per-language penalty adjustment

---

### Risk 3: Performance Regression
**Impact:** Query latency exceeds 200ms target

**Mitigation:**
- Performance profiling (cProfile)
- Import penalty overhead <1ms
- Parallel processing for index build
- Rollback if latency persists

---

## Rollback Plan

**If AST chunking degrades quality:**

1. **Detect:** Relevance@5 <70%, latency >300ms, user reports
2. **Action:** Set `chunking_strategy: "line"` in mcp.yaml
3. **Rebuild:** < 5 minutes (old index backed up)
4. **Recovery:** Search operational with line-based chunks

**Per-language rollback available** (disable AST for specific language only)

---

## Questions and Clarifications

### For Business Stakeholders
**Q: Why is this a priority?**  
A: First negative feedback on code intelligence quality. Critical for hive-kube monorepo deployment.

**Q: What's the ROI?**  
A: Reduced developer cognitive load, faster code discovery, improved AI agent effectiveness.

### For Technical Reviewers
**Q: Why AST parsing instead of ML-based ranking?**  
A: AST parsing is deterministic, explainable, and doesn't require training data. Import penalty is simple and effective.

**Q: What if Tree-sitter parse fails?**  
A: Graceful fallback to line-based chunking. Index build never crashes. Health check reports degraded status.

**Q: Impact on existing code?**  
A: Minimal. ASTExtractor refactored (~45 lines net reduction). SemanticIndex modified (add import penalty). No breaking changes.

### For Implementation Teams
**Q: Can we add a new language?**  
A: Yes! Add config to mcp.yaml (no code changes). Takes <1 hour.

**Q: How do we test this?**  
A: Follow `testing/test-strategy.md`. PRIMARY TEST: python-sdk query validation.

**Q: What if we need to rollback?**  
A: Set `chunking_strategy: "line"` in mcp.yaml. Rebuild takes <5 minutes.

---

## Next Steps

1. **Review Meeting**: Schedule stakeholder review (30 min)
2. **Approval**: Get sign-off from technical lead and product owner
3. **Resource Allocation**: Assign implementation team (1 developer, 5 days)
4. **Kickoff**: Implementation Phase 0 (Config Extraction)
5. **Tracking**: Monitor progress via phase gates in `tasks.md`

---

## Contact

**Specification Author:** AI Assistant (prAxIs OS)  
**Technical Lead:** [To be assigned]  
**Product Owner:** [To be assigned]  
**Implementation Team:** [To be assigned]

**Questions:** See `implementation.md` section 6.3 (Getting Help)

---

**🚀 Ready for Implementation**


