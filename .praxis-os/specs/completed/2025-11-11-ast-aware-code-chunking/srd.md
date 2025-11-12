# Software Requirements Document

**Project:** AST-Aware Code Chunking with Import Penalty  
**Date:** 2025-11-11  
**Priority:** High  
**Category:** Enhancement

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for implementing AST-aware code chunking with import ranking penalties to improve semantic code search relevance in prAxIs OS.

### 1.2 Scope
This feature will replace simple line-based code chunking with Tree-sitter AST-aware chunking at function/class boundaries, apply ranking penalties to import-heavy chunks, and leverage a unified configuration-driven approach for language support.

---

## 2. Business Goals

### Goal 1: Improve Code Discovery Relevance

**Objective:** Dramatically improve the relevance of code semantic search results so developers find implementation code (not import declarations) in the top results.

**Success Metrics:**
- **Relevance@5**: 60% (baseline) → 90% (target)
  - Measure: Human evaluation of top-5 results for 100 representative queries
  - Target: 9 out of 10 queries return relevant implementation code in top-5
- **Implementation Ranking**: #4 average (baseline) → #1-2 average (target)
  - Measure: Position tracking for actual implementation code
  - Target: Implementation code appears in positions #1 or #2
- **Import Ranking**: #1-3 (baseline) → #5+ (target)
  - Measure: Position tracking for import-only files (`__init__.py`, etc.)
  - Target: Import files pushed below top-5 results

**Business Impact:**
- **Developer Productivity**: Reduce time spent filtering irrelevant results (40KB noise → targeted results)
- **Code Intelligence Quality**: First negative feedback on search quality addressed before hive-kube monorepo deployment
- **AI Agent Effectiveness**: Improved code discovery directly impacts AI agent's ability to understand and modify codebases
- **Competitive Advantage**: Superior code intelligence compared to traditional text-based search tools

### Goal 2: Reduce False Positive Rate

**Objective:** Minimize irrelevant results appearing in top-5 search results.

**Success Metrics:**
- **False Positive Rate**: 40% (baseline) → <15% (target)
  - Measure: Percentage of top-5 results that are irrelevant to the query
  - Target: Less than 1 in 5 top results is irrelevant
- **User Satisfaction**: Qualitative feedback from python-sdk and hive-kube usage
  - Target: No reported issues with "too much noise" or "right code buried"

**Business Impact:**
- **Reduced Cognitive Load**: Developers spend less time evaluating irrelevant results
- **Faster Onboarding**: New developers discover correct code patterns faster
- **Lower Support Burden**: Fewer "where is X implemented?" questions
- **Improved User Experience**: First-time users see value immediately

### Goal 3: Maintain Search Performance

**Objective:** Ensure AST-aware chunking does not degrade search query latency.

**Success Metrics:**
- **Search Latency (p95)**: <200ms (baseline) → <200ms (target)
  - Measure: Prometheus metrics for query response time
  - Target: No regression in search latency
- **Index Build Time**: Acceptable one-time overhead (2-3x slower parsing acceptable)
  - Measure: Time to rebuild code index for 100K LOC
  - Target: <10 minutes for full rebuild

**Business Impact:**
- **No User-Facing Degradation**: Search remains fast and responsive
- **Acceptable Infrastructure Cost**: Parsing overhead paid once at index time, not query time
- **Operational Viability**: Feature can be enabled in production without performance concerns

### Goal 4: Enable Multi-Repo Code Intelligence

**Objective:** Establish architecture foundation for indexing and searching across multiple repositories (hive-kube monorepo readiness).

**Success Metrics:**
- **Language Support**: Configuration-driven support for Python, TypeScript, Go (with easy extension to other languages)
  - Measure: Number of languages supported via config (no code changes)
  - Target: 3+ languages at launch, easy to add more
- **Scalability**: AST chunking applies consistently across all partitions (primary code, instrumentors)
  - Measure: Index health checks show consistent chunking quality across partitions
  - Target: 100% of configured languages use AST chunking (with graceful fallback)

**Business Impact:**
- **Hive-Kube Readiness**: prAxIs OS ready to support large monorepo deployment
- **Instrumentor Analysis**: Foundation for multi-repo instrumentor semantic analysis (openlit, traceloop, arize)
- **Future Growth**: Easy to extend to new languages and repositories as needed

---

## 2.1 Supporting Documentation

The business goals above are informed by:
- **AST-Aware Code Chunking Design Document (2025-11-10)**: Real failure case from python-sdk, success metrics, performance analysis, and alignment with Cascading Health Check Architecture

See `supporting-docs/INDEX.md` for complete analysis and extracted insights (87 total insights: 25 requirements, 42 design, 20 implementation).

---

## 3. User Stories

User stories describe the feature from the user's perspective, focusing on who needs it, what they want to accomplish, and why it matters.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: Find Implementation Code, Not Imports

**As a** AI agent analyzing a codebase  
**I want to** find actual function implementations when I search for specific functionality  
**So that** I can understand and modify the correct code, not waste time on import declarations

**Acceptance Criteria:**
- **Given** I search for "EventsAPI list_events multiple filters array implementation"
- **When** semantic search returns top-5 results
- **Then** actual implementation code (`api/events.py` lines 181-380) ranks in positions #1-2
- **And** import files (`api/__init__.py`) rank below position #5
- **And** top-5 results have <15% false positive rate

**Priority:** Critical (Must-Have)

**Real Failure Case (python-sdk):**
- **Current Result**: Imports #1, implementation #4 (40KB noise, "right code buried")
- **Target Result**: Implementation #1-2, imports #5+ (targeted, relevant)

---

### Story 2: Discover Relevant Code Quickly

**As a** developer searching for how a feature is implemented  
**I want to** see function-level code chunks in search results  
**So that** I can quickly understand the implementation without reading entire files

**Acceptance Criteria:**
- **Given** I search for a specific function or class
- **When** search results are returned
- **Then** each result is a semantically meaningful chunk (function/class, not arbitrary lines)
- **And** chunk boundaries align with AST nodes (no mid-function splits)
- **And** each chunk is ~500 tokens (fits in CodeBERT context)

**Priority:** High

---

### Story 3: Work Across Multiple Languages

**As a** developer working in a polyglot codebase (Python, TypeScript, Go)  
**I want to** consistent code search quality across all languages  
**So that** I can discover implementations regardless of language

**Acceptance Criteria:**
- **Given** the codebase contains Python, TypeScript, and Go files
- **When** I search for functionality in any language
- **Then** AST-aware chunking is applied consistently across all configured languages
- **And** search relevance metrics (Relevance@5 >90%) apply to all languages
- **And** adding a new language requires only config changes (no code modifications)

**Priority:** High

---

### Story 4: Search Without Performance Degradation

**As a** developer using code semantic search  
**I want to** maintain fast query response times (<200ms)  
**So that** my workflow is not interrupted by slow searches

**Acceptance Criteria:**
- **Given** the code index uses AST-aware chunking
- **When** I execute a semantic search query
- **Then** p95 latency remains <200ms
- **And** there is no perceptible slowdown compared to line-based chunking
- **And** index rebuild time is acceptable (<10 minutes for 100K LOC)

**Priority:** High

---

### Story 5: Recover from Search Quality Degradation

**As a** system administrator  
**I want to** quickly rollback AST chunking if it degrades search quality  
**So that** users are not impacted by broken search

**Acceptance Criteria:**
- **Given** AST chunking is enabled
- **When** search quality degrades (Relevance@5 <70%)
- **Then** I can set `chunking_strategy: "line"` in config
- **And** system rebuilds index with line-based chunking
- **And** recovery completes in <5 minutes

**Priority:** High

---

## 3.1 Story Priority Summary

**Critical (Must-Have):**
- Story 1: Find Implementation Code, Not Imports (addresses primary user pain point)

**High Priority:**
- Story 2: Discover Relevant Code Quickly (improves code discovery UX)
- Story 3: Work Across Multiple Languages (enables multi-repo support)
- Story 4: Search Without Performance Degradation (maintains operational viability)
- Story 5: Recover from Search Quality Degradation (provides operational safety)

---

## 3.2 Supporting Documentation

User needs from supporting documents:
- **AST-Aware Code Chunking Design Document**: Real failure case from python-sdk ("Too much noise, 40KB of results, right code buried at #4"), multi-repo instrumentor analysis requirements, performance constraints (CodeBERT 514 token limit), rollback procedures for operational safety

See `supporting-docs/INDEX.md` for details.

---

## 4. Functional Requirements

Functional requirements specify the specific capabilities the system must provide to meet the business goals and user stories.

---

### FR-001: AST-Aware Code Chunking

**Description:** The system shall parse source code files using Tree-sitter and chunk code at Abstract Syntax Tree (AST) boundaries (function definitions, class definitions) rather than arbitrary line counts.

**Priority:** Critical

**Related User Stories:** Story 1 (Find Implementation Code), Story 2 (Discover Relevant Code Quickly)

**Acceptance Criteria:**
- System parses code files with Tree-sitter parser for each configured language
- Chunks are created at function and class definition boundaries (no mid-function splits)
- Function/class bodies are kept intact within a single chunk (unless exceeding size limits)
- Chunk boundaries align with AST nodes defined in language configuration
- Each chunk includes metadata: `chunk_type` (function/class/import/module), `symbols` (function/class names), `start_line`, `end_line`

---

### FR-002: Import Penalty Mechanism

**Description:** The system shall calculate an import ratio for each code chunk and apply a ranking penalty to import-heavy chunks to de-prioritize them in search results.

**Priority:** Critical

**Related User Stories:** Story 1 (Find Implementation Code)

**Acceptance Criteria:**
- System calculates `import_ratio = import_lines / total_lines` for each chunk
- Chunks with `import_ratio > 0.5` receive an import penalty multiplier
- Import penalty multiplier is configurable per language (default: 0.3)
- Penalty is applied during search ranking: `final_score = base_score * import_penalty`
- Import chunks rank below position #5 in search results (target: #5+)
- Implementation chunks rank in top-2 positions (target: #1-2)

---

### FR-003: Token-Based Chunk Sizing

**Description:** The system shall create code chunks targeting ~500 tokens per chunk (within CodeBERT's 514 token limit), with 50-token overlap between adjacent chunks.

**Priority:** Critical

**Related User Stories:** Story 2 (Discover Relevant Code Quickly), Story 4 (Search Without Performance Degradation)

**Acceptance Criteria:**
- Target chunk size: 500 tokens (±20% tolerance: 400-600 tokens)
- Chunk overlap: 50 tokens between adjacent chunks
- Token estimation uses approximate count (4 characters ≈ 1 token for code)
- Chunks exceeding 600 tokens are split at `split_boundary_nodes` (if/try/for statements)
- No chunk exceeds 514 tokens (CodeBERT hard limit)
- Chunk size metadata stored for monitoring and debugging

---

### FR-004: Configuration-Driven Language Support

**Description:** The system shall support multiple programming languages via declarative configuration in `mcp.yaml`, without requiring code changes for each new language.

**Priority:** High

**Related User Stories:** Story 3 (Work Across Multiple Languages)

**Acceptance Criteria:**
- Language-specific AST node types defined in `mcp.yaml` (not hardcoded in Python)
- Configuration includes: `import_nodes`, `definition_nodes`, `split_boundary_nodes`, `import_penalty`
- Adding a new language requires only adding a config entry (no code modifications)
- System validates config on startup (checks for missing/invalid node types)
- Supported languages at launch: Python, TypeScript, Go
- Configuration schema documented with examples for adding new languages

---

### FR-005: Graceful Fallback to Line-Based Chunking

**Description:** The system shall fall back to line-based chunking for files in unsupported languages or when AST parsing fails, ensuring search functionality remains operational.

**Priority:** High

**Related User Stories:** Story 3 (Work Across Multiple Languages), Story 4 (Search Without Performance Degradation)

**Acceptance Criteria:**
- AST parsing failure detected and logged (with file path and error details)
- System falls back to line-based chunking for failed files
- Fallback uses existing implementation (200-line chunks, 20-line overlap)
- Health check reports AST component status (operational/degraded/fallback)
- Fallback does not block index building or search operations
- Fallback count tracked in metrics for monitoring

---

### FR-006: Index Rebuild Capability

**Description:** The system shall support rebuilding the code index with AST-aware chunking, replacing existing line-based chunks.

**Priority:** High

**Related User Stories:** Story 4 (Search Without Performance Degradation)

**Acceptance Criteria:**
- Index rebuild triggered by deleting `.praxis-os/.cache/indexes/code` and restarting server
- Rebuild processes all source files with AST-aware chunking
- Rebuild time for 100K LOC: <10 minutes
- Rebuild preserves source file paths and metadata
- Rebuild validates chunk quality (token counts, import ratios, AST boundaries)
- Rebuild completion logged with timing and chunk statistics

---

### FR-007: Configuration-Based Rollback

**Description:** The system shall support quick rollback to line-based chunking via configuration change, without code deployment.

**Priority:** High

**Related User Stories:** Story 5 (Recover from Search Quality Degradation)

**Acceptance Criteria:**
- Rollback triggered by setting `chunking_strategy: "line"` in `mcp.yaml`
- System detects config change and rebuilds index with line-based chunking
- Rollback preserves old index as backup (`.cache/indexes/code.ast-backup`)
- Rollback completion time: <5 minutes
- Per-language rollback supported (enable AST for some languages, line-based for others)
- Rollback logged with timestamp and reason

---

### FR-008: Health Check Integration

**Description:** The system shall integrate AST chunking with the Cascading Health Check Architecture, reporting component health and enabling targeted diagnostics.

**Priority:** High

**Related User Stories:** Story 5 (Recover from Search Quality Degradation)

**Acceptance Criteria:**
- AST chunker registered as a component in CodeIndex health check
- Health check reports: operational/degraded/fallback status
- Health check includes metrics: chunk count, average token size, import penalty applications, fallback count
- Degraded status triggered by: high fallback rate (>25%), parse errors, invalid chunks
- Health check output includes actionable recommendations (e.g., "Check language config for TypeScript")
- Health check executed on demand via `pos_search_project` tool

---

### FR-009: Import Chunk Grouping

**Description:** The system shall group consecutive import statements into a single chunk, rather than creating individual chunks per import.

**Priority:** Medium

**Related User Stories:** Story 1 (Find Implementation Code), Story 2 (Discover Relevant Code Quickly)

**Acceptance Criteria:**
- Consecutive import/import_from statements grouped into one chunk
- Import chunk marked with `chunk_type = "import"`
- Import chunk receives import penalty (if `import_ratio > 0.5`)
- Import chunk includes list of imported symbols for metadata
- Import chunks separated from function/class definitions

---

### FR-010: Multi-Language Consistency

**Description:** The system shall apply AST-aware chunking consistently across all configured languages (Python, TypeScript, Go), ensuring uniform search quality.

**Priority:** Medium

**Related User Stories:** Story 3 (Work Across Multiple Languages)

**Acceptance Criteria:**
- Same chunking algorithm applied to all languages (language-agnostic logic)
- Language-specific behavior controlled via config (node types, penalties)
- Search relevance metrics (Relevance@5 >90%) consistent across languages
- Test suite validates chunking quality for all configured languages
- Documentation includes language-specific examples and config patterns

---

## 4.1 Requirements by Category

### Code Parsing & Chunking
- FR-001: AST-Aware Code Chunking
- FR-003: Token-Based Chunk Sizing
- FR-009: Import Chunk Grouping
- FR-010: Multi-Language Consistency

### Search Ranking
- FR-002: Import Penalty Mechanism

### Configuration & Extensibility
- FR-004: Configuration-Driven Language Support
- FR-007: Configuration-Based Rollback

### Operational Resilience
- FR-005: Graceful Fallback to Line-Based Chunking
- FR-006: Index Rebuild Capability
- FR-008: Health Check Integration

---

## 4.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority |
|-------------|--------------|----------------|----------|
| FR-001 | Story 1, 2 | Goal 1, 2 | Critical |
| FR-002 | Story 1 | Goal 1, 2 | Critical |
| FR-003 | Story 2, 4 | Goal 1, 3 | Critical |
| FR-004 | Story 3 | Goal 4 | High |
| FR-005 | Story 3, 4 | Goal 3, 4 | High |
| FR-006 | Story 4 | Goal 3 | High |
| FR-007 | Story 5 | Goal 3 | High |
| FR-008 | Story 5 | Goal 3 | High |
| FR-009 | Story 1, 2 | Goal 1 | Medium |
| FR-010 | Story 3 | Goal 4 | Medium |

---

## 4.3 Supporting Documentation

Requirements informed by:
- **AST-Aware Code Chunking Design Document (2025-11-10)**: Detailed technical requirements for AST parsing (Tree-sitter), import penalty calculation (0.3 multiplier), configuration-driven architecture (mcp.yaml), token sizing (500 target, 514 limit), graceful fallback patterns, health check integration, and rollback procedures

See `supporting-docs/INDEX.md` for complete requirements extraction (25 requirements insights).

---

## 5. Non-Functional Requirements

Non-functional requirements define quality attributes and system constraints that determine HOW WELL the system performs.

---

### 5.1 Performance

**NFR-P1: Search Query Latency**
- **Requirement:** Search query response time p95 shall remain <200ms with AST-aware chunking
- **Measurement:** Prometheus metrics tracking query latency distribution
- **Acceptance Criteria:**
  - p50 latency: <100ms
  - p95 latency: <200ms
  - p99 latency: <300ms
  - No regression compared to line-based chunking baseline

**NFR-P2: Index Build Time**
- **Requirement:** Full code index rebuild shall complete in <10 minutes for 100K LOC
- **Measurement:** Index build timing logs
- **Acceptance Criteria:**
  - 100K LOC rebuild: <10 minutes
  - AST parsing overhead: 2-3x slower than line-based (acceptable one-time cost)
  - Parallel processing utilized (multi-core)
  - Progress logging every 10% completion

**NFR-P3: Import Penalty Application Overhead**
- **Requirement:** Import penalty calculation shall add <1ms to search query latency
- **Measurement:** Profiling search ranking stage
- **Acceptance Criteria:**
  - Import ratio calculation: <0.5ms
  - Penalty application: <0.5ms
  - No perceptible impact on user experience

---

### 5.2 Reliability

**NFR-R1: Graceful Degradation**
- **Requirement:** System shall continue operating when AST parsing fails for individual files
- **Measurement:** Fallback activation count and health check status
- **Acceptance Criteria:**
  - Parse failures logged with file path and error details
  - Fallback to line-based chunking for failed files only
  - Health check reports degraded status (not failure)
  - Search functionality remains operational for all files

**NFR-R2: Quick Recovery from Degradation**
- **Requirement:** System shall support rollback to line-based chunking in <5 minutes
- **Measurement:** Rollback timing logs
- **Acceptance Criteria:**
  - Config change detected immediately
  - Old index preserved as backup
  - Index rebuild completes in <5 minutes
  - No user-facing downtime during rollback

**NFR-R3: Component Health Monitoring**
- **Requirement:** AST chunking health shall be monitored and reported via Cascading Health Check Architecture
- **Measurement:** Health check API output
- **Acceptance Criteria:**
  - Health check reports operational/degraded/fallback status
  - Metrics include: chunk count, token size distribution, fallback rate
  - Actionable recommendations provided for degraded state
  - Health checks executable on-demand via `pos_search_project` tool

---

### 5.3 Maintainability

**NFR-M1: Configuration-Driven Language Support**
- **Requirement:** New languages shall be added via configuration only, without code changes
- **Measurement:** Code review and language addition process
- **Acceptance Criteria:**
  - Language config includes: node types, import penalty, chunking parameters
  - No Python code changes required to add new language
  - Config validation on startup (catches invalid node types)
  - Documentation with examples for adding languages

**NFR-M2: Test Coverage**
- **Requirement:** AST chunking and import penalty features shall have comprehensive test coverage
- **Measurement:** Test suite execution and coverage reports
- **Acceptance Criteria:**
  - Unit tests: Parse files, verify boundaries, calculate penalties
  - Integration tests: Build index, run queries, validate ranking
  - Comparison tests: AST vs line-based side-by-side
  - Relevance tests: Human evaluation of top-5 results (100 queries)

**NFR-M3: Logging and Diagnostics**
- **Requirement:** System shall provide comprehensive logging for debugging AST chunking issues
- **Measurement:** Log output and issue resolution time
- **Acceptance Criteria:**
  - Parse failures logged with file path, language, and error
  - Chunk statistics logged: count, average token size, import ratio distribution
  - Fallback activations logged with reason
  - Health check output includes actionable diagnostics

---

### 5.4 Scalability

**NFR-SC1: Multi-Repository Support**
- **Requirement:** AST chunking shall apply consistently across all code partitions (primary, instrumentors)
- **Measurement:** Index health checks and partition metrics
- **Acceptance Criteria:**
  - AST chunking enabled for all configured partitions
  - Search quality metrics consistent across partitions
  - Partition-specific health monitoring
  - No cross-partition interference

**NFR-SC2: Language Extensibility**
- **Requirement:** System shall support 3+ languages at launch (Python, TypeScript, Go) with easy extension
- **Measurement:** Supported language count and addition process
- **Acceptance Criteria:**
  - Launch languages: Python, TypeScript, Go
  - Adding language: <1 hour (config only)
  - Config schema documented with examples
  - Test suite validates new language support

---

### 5.5 Usability

**NFR-U1: Search Result Relevance**
- **Requirement:** Search results shall prioritize implementation code over import declarations
- **Measurement:** Position tracking and Relevance@5 metric
- **Acceptance Criteria:**
  - Implementation code ranks #1-2 average (target)
  - Import files rank #5+ (below top-5)
  - Relevance@5 >90% (human evaluation)
  - False positive rate <15%

**NFR-U2: Developer Experience**
- **Requirement:** AST chunking behavior shall be transparent and predictable
- **Measurement:** User feedback and documentation quality
- **Acceptance Criteria:**
  - Chunk boundaries explained in documentation
  - Import penalty mechanism documented
  - Health check output human-readable
  - Rollback procedure clearly documented

---

### 5.6 Compatibility

**NFR-C1: Backward Compatibility with Line-Based Chunking**
- **Requirement:** System shall maintain line-based chunking as fallback for unsupported languages
- **Measurement:** Fallback activation and functionality testing
- **Acceptance Criteria:**
  - Line-based implementation unchanged
  - Fallback behavior equivalent to baseline
  - No impact on existing indexes for unsupported languages
  - Gradual migration path (enable AST per language)

**NFR-C2: Integration with Existing RAG Infrastructure**
- **Requirement:** AST chunking shall integrate seamlessly with existing CodeIndex, SemanticIndex, and health check systems
- **Measurement:** Integration tests and system architecture review
- **Acceptance Criteria:**
  - No breaking changes to SemanticIndex API
  - Health check architecture extended (not replaced)
  - Existing search queries continue to work
  - No impact on FTS or vector search components

---

## 5.7 Supporting Documentation

NFRs informed by:
- **AST-Aware Code Chunking Design Document (2025-11-10)**: Performance analysis (300-500 files/second AST parsing, <200ms p95 search latency target, <10 minutes rebuild for 100K LOC), reliability requirements (graceful fallback, <5 minute rollback), health check integration patterns, configuration-driven architecture principles, and rollback procedures

See `supporting-docs/INDEX.md` for complete NFR extraction (42 design insights).

---

## 6. Out of Scope

Explicitly defines what is NOT included in this release. Items may be considered for future phases.

### Explicitly Excluded

---

#### Features

**Not Included in This Release:**

1. **Real-Time Incremental Re-Indexing**
   - **Reason:** Index rebuild is manual/scheduled only. File watcher-based incremental re-indexing adds significant complexity for uncertain benefit.
   - **Future Consideration:** Phase 2 - If rebuild time becomes a bottleneck (e.g., >1 hour for very large codebases), consider incremental updates.

2. **Per-File Chunking Strategies**
   - **Reason:** Chunking strategy is global (per language), not per-file. Supporting file-specific overrides adds configuration complexity without clear use case.
   - **Future Consideration:** Not planned. If needed, users should configure per-language settings.

3. **Custom Ranking Algorithms Beyond Import Penalty**
   - **Reason:** This release implements a single, proven ranking adjustment (import penalty). Additional ranking strategies (e.g., complexity-based, recency-based) are out of scope.
   - **Future Consideration:** Phase 3 - After validating import penalty effectiveness, consider additional ranking signals.

4. **Cross-Language AST Comparisons**
   - **Reason:** AST chunking is language-specific. Comparing AST structures across languages (e.g., Python function vs TypeScript arrow function) is not required for search.
   - **Future Consideration:** Not planned. Different use case (code translation, cross-language refactoring).

5. **Dynamic Per-Query Chunking Strategies**
   - **Reason:** Chunking happens at index time, not query time. Dynamic chunking per query would require expensive re-chunking on every search.
   - **Future Consideration:** Not planned. Index-time chunking is the correct architecture for performance.

6. **Machine Learning-Based Ranking**
   - **Reason:** Rule-based import penalty is sufficient for the identified problem. ML-based ranking adds infrastructure complexity (training data, model deployment) without clear ROI.
   - **Future Consideration:** Phase 4 - If search quality plateaus, consider learning-to-rank approaches.

7. **Custom CodeBERT Fine-Tuning**
   - **Reason:** Using pre-trained CodeBERT embeddings without fine-tuning. Fine-tuning requires labeled training data and GPU infrastructure.
   - **Future Consideration:** Not planned. Pre-trained embeddings sufficient for code search use case.

8. **AST-Based Code Refactoring Tools**
   - **Reason:** AST parsing is used for chunking only, not code transformation. Refactoring tools (e.g., rename symbol, extract function) are out of scope.
   - **Future Consideration:** Different product domain. If needed, separate tool using same AST infrastructure.

---

#### User Types

**Not Supported:**

- **Non-Developer Users**: This feature is designed for developers and AI agents analyzing code. Non-technical users searching for documentation (not code) are out of scope for AST-aware chunking.
- **Code Review Automation**: While improved code discovery helps code review, automated review workflows (e.g., auto-suggesting reviewers based on AST analysis) are not included.

---

#### Languages

**Not Supported at Launch:**

- **Rust, Ruby, Java, C++, C#**: While the architecture is designed to support any language with a Tree-sitter grammar, only Python, TypeScript, and Go are configured at launch.
- **Domain-Specific Languages (DSLs)**: Configuration languages (YAML, JSON), markup languages (HTML, XML), and DSLs (SQL, GraphQL) are not included. These typically don't benefit from AST-aware chunking for code search.

---

#### Integrations

**Not Included:**

- **IDE Plugins**: No VSCode/IntelliJ plugins for visualizing chunks or penalties. Users interact via `pos_search_project` tool only.
- **CI/CD Integration**: No automated index rebuilding in CI/CD pipelines. Index rebuild is manual/scheduled.
- **External Search Engines**: No integration with external search tools (e.g., Elasticsearch, Algolia). prAxIs OS uses local LanceDB index only.

---

#### Quality Levels Beyond NFRs

**Not Included:**

- **100% Parse Success Rate**: AST parsing failures are acceptable if graceful fallback works. Target is >75% success rate, not 100%.
- **Sub-100ms Query Latency**: p95 <200ms is the target. Further optimization (e.g., caching, GPU acceleration) for sub-100ms is not included.
- **Zero Downtime Rollback**: Rollback in <5 minutes is acceptable. Zero-downtime blue/green deployment is out of scope.

---

## 6.1 Future Enhancements

**Potential Phase 2 (After Launch):**
- **Additional Languages**: Rust, Java, Ruby (add via config)
- **AST Metadata Enrichment**: Store function signatures, docstrings, complexity metrics in ASTIndex for enhanced `search_ast` queries
- **Multi-Repo Instrumentor Analysis**: Automated extraction of semantic conventions from instrumentor codebases (openlit, traceloop, arize)

**Potential Phase 3 (6-12 Months):**
- **Incremental Re-Indexing**: File watcher-based incremental updates for large codebases
- **Additional Ranking Signals**: Complexity-based, recency-based, or file-importance-based ranking adjustments
- **AST-Based Refactoring Tools**: Rename symbol, extract function, move class (separate tool using AST infrastructure)

**Explicitly Not Planned:**
- **ML-Based Ranking**: Pre-trained embeddings + rule-based penalties sufficient
- **Custom CodeBERT Fine-Tuning**: Infrastructure complexity not justified
- **Cross-Language AST Comparisons**: Different use case (code translation)
- **Real-Time Query-Time Chunking**: Architecture incompatible (index-time chunking required for performance)

---

## 6.2 Supporting Documentation

Out-of-scope items from:
- **AST-Aware Code Chunking Design Document (2025-11-10)**: Explicit scope boundaries defined in "Out of Scope" section, including real-time re-indexing, per-file strategies, custom ranking algorithms, and cross-language AST comparisons

See `supporting-docs/INDEX.md` for complete scope analysis.

---

## 7. Approval & Sign-Off

**Prepared By:** AI Assistant (prAxIs OS)  
**Date:** 2025-11-11  
**Status:** Draft - Awaiting Review

**Reviewers:**
- [ ] Josh Paul (Project Lead) - Business goals and scope approval
- [ ] Technical Review - Requirements completeness and feasibility

**Revision History:**
- v1.0 (2025-11-11): Initial draft created via `spec_creation_v1` workflow

---

**End of Software Requirements Document**

