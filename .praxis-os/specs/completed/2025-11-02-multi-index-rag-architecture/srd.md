# Software Requirements Document

**Project:** Multi-Index RAG Architecture  
**Date:** 2025-11-02  
**Priority:** Critical  
**Category:** Enhancement

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for enhancing prAxIs OS's RAG (Retrieval-Augmented Generation) system with multi-index architecture, hybrid search, metadata filtering, and code search capabilities to preserve behavioral reinforcement at scale.

### 1.2 Scope
This feature will extend the current single-index RAG system to support multiple content types (standards, code), hybrid search strategies (vector + FTS), metadata-based filtering, and config-driven extensibility while maintaining zero-cost operation and completing in a single day.

---

## 2. Business Goals

### Goal 1: Preserve Behavioral Reinforcement at Scale

**Objective:** Prevent RAG discovery degradation as standards corpus grows from 60 to 500+ documents, preserving the behavioral modification system that makes prAxIs OS effective.

**Success Metrics:**
- Single-query accuracy: Maintain 40%+ (prevent degradation to projected 5%)
- Multi-query success rate: Maintain 90%+ within 3 queries (current baseline)
- Hybrid search accuracy: Improve from 33% → 50-60% baseline
- Metadata filtering accuracy: Improve from 50% → 70%+ when filters applied
- Scale target: Support 500+ standards without behavioral system collapse

**Business Impact:**
- AI agents continue to discover correct standards through querying (don't revert to training data guessing)
- Adversarial design system remains effective (phase gating, evidence validation work because discovery works)
- Per-project installations scale from small (70 standards) to large enterprise (500+ standards) without degradation
- prAxIs OS adoption not limited by corpus size

### Goal 2: Enable Code Discovery for AI-Generated Codebases

**Objective:** Provide semantic and structural code search to enable AI agents to verify documentation against implementation and discover existing patterns in large, AI-generated codebases.

**Success Metrics:**
- Code search latency: <200ms p95 for semantic queries
- Code search latency: <100ms p95 for AST structural queries
- Language coverage: All 50+ Tree-sitter languages supported day 1 (config-driven)
- Discovery capability: "Trust but verify" - agents can validate docs against actual code
- Codebase scale: Support 32K+ lines (current prAxIs OS size) with fast discovery

**Business Impact:**
- AI agents can navigate AI-generated codebases (prAxIs OS: 32K lines in 2.5 months)
- "Trust but verify" behavioral pattern enables quality checking (docs vs implementation)
- Code pattern discovery reduces reinvention, improves consistency
- Supports multi-language projects without per-language code changes

### Goal 3: Zero-Cost Enhancement of RAG Capabilities

**Objective:** Deliver hybrid search, metadata filtering, and code search using only local, open-source models with no API costs beyond LLM calls.

**Success Metrics:**
- API cost: $0 for all search operations (vector, FTS, code, metadata filtering)
- Storage cost: <1.5GB total for all indexes
- Memory cost: <1GB active memory during queries
- Model licensing: MIT/Apache 2.0 only (BGE-small-en-v1.5: 134MB, MIT licensed)
- Infrastructure: No external services required (LanceDB local, Tree-sitter local)

**Business Impact:**
- Unlimited search queries without cost scaling concerns
- Economic alignment: Better AI behavior doesn't increase costs
- Per-project installations remain viable at scale (no per-query fees)
- Enterprise adoption: No vendor lock-in or usage-based pricing

### Goal 4: Safe Manual Index Operations

**Objective:** Enable safe manual index rebuilds and maintenance through file locking and teaching messages, preventing data corruption while reinforcing correct usage patterns.

**Success Metrics:**
- Corruption prevention: 0% index corruption from concurrent access
- Teaching effectiveness: 100% of lock failures return actionable guidance (not silent errors)
- Platform coverage: Unix/Linux/macOS (Windows deferred)
- Recovery time: <1 second to detect lock conflict and return teaching message

**Business Impact:**
- Adversarial design extended to index management (prevent + teach)
- AI agents learn correct index rebuild protocol through teaching messages
- Manual index operations safe during active MCP server usage
- Operational confidence: Users can rebuild indexes without risk

---

## 2.1 Supporting Documentation

The business goals above are informed by:
- **multi-index-rag-architecture.md**: Complete design document with problem statement, solution architecture, success metrics, and implementation phases

See `supporting-docs/INDEX.md` for complete analysis of requirements, design, and implementation insights.

---

## 3. User Stories

User stories describe the feature from the user's perspective.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: Accurate Discovery at Scale

**As an** AI agent  
**I want to** discover relevant project standards accurately even when the corpus grows to 500+ documents  
**So that** I maintain correct behavior through querying instead of reverting to training data guessing

**Acceptance Criteria:**
- Given a standards corpus of 200+ documents
- When I query for a specific development pattern
- Then I receive relevant results with 40%+ single-query accuracy
- And multi-query success remains 90%+ within 3 queries

**Priority:** Critical

---

### Story 2: Code Discovery by Concept

**As an** AI agent  
**I want to** find code implementations by describing their purpose semantically  
**So that** I can discover existing patterns without knowing exact function names

**Acceptance Criteria:**
- Given a codebase with 32K+ lines
- When I query "how to handle authentication tokens"
- Then I receive relevant code chunks from auth modules
- And results include both class definitions and usage examples
- And latency is <200ms p95

**Priority:** Critical

---

### Story 3: Precise Symbol Location

**As an** AI agent  
**I want to** locate specific functions, classes, or methods by name or signature  
**So that** I can navigate to exact implementation points quickly

**Acceptance Criteria:**
- Given a multi-language codebase (Python, TypeScript, Go, etc.)
- When I query for "StateManager class definition"
- Then I receive the exact file and line range
- And latency is <100ms p95
- And it works for all 50+ Tree-sitter supported languages

**Priority:** High

---

### Story 4: Verify Docs Against Code

**As an** AI agent  
**I want to** verify that documentation matches actual implementation  
**So that** I can "trust but verify" and catch documentation drift

**Acceptance Criteria:**
- Given a standard that describes how MCP server starts
- When I search code for actual startup logic
- Then I can compare standard description vs implementation
- And identify discrepancies (outdated docs, missing steps)

**Priority:** High

---

### Story 5: Zero-Config Language Support

**As a** user installing prAxIs OS  
**I want** the system to automatically detect my project's languages and configure code search  
**So that** I don't need to manually specify which languages to support

**Acceptance Criteria:**
- Given a project with Python and TypeScript code
- When prAxIs OS installation runs
- Then both languages are auto-detected
- And `index_config.yaml` includes both languages
- And Tree-sitter parsers are auto-installed
- And code search works immediately after install

**Priority:** High

---

### Story 6: Zero-Cost Enhancement

**As a** user with budget constraints  
**I want** enhanced RAG capabilities without increasing API costs  
**So that** I can query unlimited times without cost concerns

**Acceptance Criteria:**
- Given hybrid search, metadata filtering, and code search features
- When I perform any search operation (standards, code, AST)
- Then no API calls are made (all local: embeddings, FTS, Tree-sitter)
- And storage cost is <1.5GB
- And memory usage is <1GB active

**Priority:** Critical

---

### Story 7: Self-Teaching Config

**As a** user unfamiliar with AI/RAG systems  
**I want** the config file to explain itself with inline documentation  
**So that** I can understand and modify settings without AI expertise

**Acceptance Criteria:**
- Given `index_config.yaml`
- When I open the file
- Then every section has clear comments explaining purpose
- And examples show how to add new languages
- And trade-offs are documented (chunk size, model selection)

**Priority:** Medium

---

### Story 8: Safe Manual Index Rebuild

**As a** system administrator  
**I want** to manually rebuild indexes without risking corruption  
**So that** I can recover from issues or force a full re-index safely

**Acceptance Criteria:**
- Given MCP server is running with indexes locked
- When I attempt manual index rebuild via script
- Then file lock prevents concurrent access
- And I receive a teaching message: "MCP server holds lock, stop server first or use MCP tool"
- And no index corruption occurs

**Priority:** High

---

## 3.1 Story Priority Summary

**Critical (Must-Have):**
- Story 1: Accurate Discovery at Scale
- Story 2: Code Discovery by Concept
- Story 6: Zero-Cost Enhancement

**High Priority:**
- Story 3: Precise Symbol Location
- Story 4: Verify Docs Against Code
- Story 5: Zero-Config Language Support
- Story 8: Safe Manual Index Rebuild

**Medium Priority:**
- Story 7: Self-Teaching Config

---

## 3.2 Supporting Documentation

User needs from supporting documents:
- **multi-index-rag-architecture.md**: Problem statement (RAG degradation), user impact (AI behavioral system), success metrics

See `supporting-docs/INDEX.md` for details.

---

## 4. Functional Requirements

Functional requirements specify capabilities the system must provide.

---

### FR-001: Hybrid Search (Vector + FTS)

**Description:** The system shall combine vector search (semantic) and full-text search (BM25-based) using Reciprocal Rank Fusion (RRF) to improve discovery accuracy from 33% to 50-60%.

**Priority:** Critical

**Related User Stories:** Story 1 (Accurate Discovery at Scale)

**Acceptance Criteria:**
- LanceDB native FTS index created for standards content
- Vector search and FTS execute in parallel
- RRF with k=60 merges results
- Single-query accuracy improves to 50-60% (measured against test corpus)
- Query latency remains <200ms p95

---

### FR-002: Metadata Filtering

**Description:** The system shall support metadata-based pre-filtering using LanceDB scalar indexes (BTREE/BITMAP) with SQL WHERE clauses to reduce search space and improve accuracy from 50% to 70%+.

**Priority:** Critical

**Related User Stories:** Story 1 (Accurate Discovery at Scale)

**Acceptance Criteria:**
- Scalar indexes created on metadata fields: domain, phase, role
- Filters expressed as SQL WHERE clauses (e.g., `WHERE metadata.domain = 'backend'`)
- Filtered search accuracy reaches 70%+ when domain-specific filters applied
- Filter execution adds <10ms to query latency

---

### FR-003: Semantic Code Search

**Description:** The system shall index project source code using BGE embeddings to enable discovery by conceptual meaning (e.g., "authentication token handling").

**Priority:** Critical

**Related User Stories:** Story 2 (Code Discovery by Concept)

**Acceptance Criteria:**
- Code files indexed with same BGE-small-en-v1.5 model as standards
- Chunking strategy: 500 tokens per chunk, 50 token overlap
- Semantic search returns relevant code chunks for conceptual queries
- Query latency <200ms p95 for code search
- Supports multi-language codebases (Python, JavaScript, TypeScript, Go, Rust, etc.)

---

### FR-004: Structural Code Search (AST)

**Description:** The system shall parse source code into Abstract Syntax Trees (AST) using Tree-sitter to enable precise symbol queries (e.g., "StateManager class definition").

**Priority:** High

**Related User Stories:** Story 3 (Precise Symbol Location)

**Acceptance Criteria:**
- Tree-sitter parsers dynamically loaded via `importlib.import_module(f"tree_sitter_{language}")`
- AST index stores: symbol name, type (class/function/method), file path, line range
- Structural queries return exact file and line range
- Query latency <100ms p95 for AST lookups
- Graceful degradation when parser unavailable (log warning, fallback to semantic search)

---

### FR-005: Dynamic Language Support

**Description:** The system shall support all 50+ Tree-sitter languages day 1 through config-driven, convention-based dynamic imports without code changes.

**Priority:** High

**Related User Stories:** Story 3 (Precise Symbol Location), Story 5 (Zero-Config Language Support)

**Acceptance Criteria:**
- No hardcoded language lists in code
- Convention: package name `tree-sitter-{language}` maps to `tree_sitter_{language}` module
- Config file lists enabled languages (e.g., `languages: [python, typescript, go]`)
- Adding new language requires only: edit config + install Tree-sitter package
- Warning logged when parser unavailable, with installation instructions

---

### FR-006: Config-Driven File Watcher

**Description:** The system shall monitor file system changes and incrementally update indexes based on configurable patterns with per-content-type debouncing.

**Priority:** High

**Related User Stories:** Story 2 (Code Discovery by Concept)

**Acceptance Criteria:**
- Watches file patterns from `index_config.yaml` (e.g., `standards/**/*.md`, `**/*.py`)
- Debouncing configurable per content type (standards: 2s, code: 5s)
- Explicit exclude patterns (e.g., `**/__pycache__/**`, `**/node_modules/**`)
- Incremental updates (changed files only, not full rebuild)
- File events processed in order (no race conditions)

---

### FR-007: Unified Search Tool

**Description:** The system shall provide a single `pos_search` MCP tool with explicit `content_type` parameter to search standards, code, or AST indexes.

**Priority:** Critical

**Related User Stories:** Story 1, 2, 3 (All search stories)

**Acceptance Criteria:**
- Tool parameters: `query`, `content_type` (standards/code/ast), `filters` (optional)
- Returns unified `SearchResult[]` format across all content types
- Backward compatible: existing `search_standards` calls delegate to `pos_search(content_type="standards")`
- Zero breaking changes to existing agent queries

---

### FR-008: LLM-Driven Installation

**Description:** The system shall automatically detect project languages during installation, generate `index_config.yaml`, and install Tree-sitter dependencies via AI agent.

**Priority:** High

**Related User Stories:** Story 5 (Zero-Config Language Support)

**Acceptance Criteria:**
- AI agent counts files by extension (`.py`, `.js`, `.ts`, `.go`, `.rs`)
- Determines primary and secondary languages
- Generates `index_config.yaml` with detected languages enabled
- Appends Tree-sitter packages to `.praxis-os/mcp_server/requirements.txt`
- Runs `pip install` in isolated venv
- Code search works immediately after install completes

---

### FR-009: Index Rebuild Safety

**Description:** The system shall use file locking (`fcntl` on Unix) to prevent concurrent index access during manual rebuilds, returning teaching messages on lock conflicts.

**Priority:** High

**Related User Stories:** Story 8 (Safe Manual Index Rebuild)

**Acceptance Criteria:**
- MCP server acquires file lock when opening indexes
- Manual rebuild script attempts lock acquisition with timeout
- Lock conflict returns teaching message: "MCP server holds lock, stop server first or use MCP tool"
- Zero index corruption from concurrent access
- Lock automatically released on MCP server shutdown

---

### FR-010: Self-Teaching Config

**Description:** The system shall provide `index_config.yaml` with comprehensive inline documentation explaining every setting, example values, and trade-offs.

**Priority:** Medium

**Related User Stories:** Story 7 (Self-Teaching Config)

**Acceptance Criteria:**
- Every config section has comment block explaining purpose
- Examples provided for common modifications (add language, change chunk size)
- Trade-offs documented (model accuracy vs size, chunk size vs granularity)
- Config file is understandable without AI/RAG expertise

---

### FR-011: Zero API Cost

**Description:** The system shall execute all search operations (vector, FTS, code, AST) using only local models and libraries with no external API calls.

**Priority:** Critical

**Related User Stories:** Story 6 (Zero-Cost Enhancement)

**Acceptance Criteria:**
- BGE-small-en-v1.5 embedding model runs locally (MIT license, 134MB)
- LanceDB native FTS (no rank-bm25 library API calls)
- Tree-sitter parsers run locally (MIT license)
- Zero API calls for any search operation
- Storage <1.5GB total, memory <1GB active

---

### FR-012: Config-Driven Extensibility

**Description:** The system shall support adding new content types, languages, or features by editing `index_config.yaml` without code changes.

**Priority:** High

**Related User Stories:** Story 5 (Zero-Config Language Support)

**Acceptance Criteria:**
- Adding language: edit config `languages: [python, go, rust]` + install Tree-sitter package
- File watcher patterns configurable per content type
- Chunking strategy configurable per content type
- No code changes required for new languages or patterns

---

## 4.1 Requirements by Category

### Search Capabilities
- FR-001 (Hybrid Search)
- FR-002 (Metadata Filtering)
- FR-003 (Semantic Code Search)
- FR-004 (Structural Code Search)
- FR-007 (Unified Search Tool)

### Extensibility & Configuration
- FR-005 (Dynamic Language Support)
- FR-006 (Config-Driven File Watcher)
- FR-010 (Self-Teaching Config)
- FR-012 (Config-Driven Extensibility)

### Installation & Operations
- FR-008 (LLM-Driven Installation)
- FR-009 (Index Rebuild Safety)

### Cost & Performance
- FR-011 (Zero API Cost)

---

## 4.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority |
|-------------|--------------|----------------|----------|
| FR-001 | Story 1 | Goal 1 | Critical |
| FR-002 | Story 1 | Goal 1 | Critical |
| FR-003 | Story 2 | Goal 2 | Critical |
| FR-004 | Story 3 | Goal 2 | High |
| FR-005 | Story 3, 5 | Goal 2 | High |
| FR-006 | Story 2 | Goal 2 | High |
| FR-007 | Story 1, 2, 3 | Goal 1, 2 | Critical |
| FR-008 | Story 5 | Goal 2 | High |
| FR-009 | Story 8 | Goal 4 | High |
| FR-010 | Story 7 | Goal 2 | Medium |
| FR-011 | Story 6 | Goal 3 | Critical |
| FR-012 | Story 5 | Goal 2 | High |

---

## 4.3 Supporting Documentation

Requirements informed by:
- **multi-index-rag-architecture.md**: Technical architecture, LanceDB capabilities, Tree-sitter integration, file locking design, installation flow

See `supporting-docs/INDEX.md` for complete design insights.

---

## 5. Non-Functional Requirements

Non-functional requirements define system qualities and constraints.

### NFR-001: Query Performance

**Category:** Performance  
**Requirement:** All search operations shall complete within specified latency thresholds.

**Metrics:**
- Standards hybrid search: <200ms p95
- Code semantic search: <200ms p95
- AST structural search: <100ms p95
- Metadata filtering overhead: <10ms

**Priority:** Critical

---

### NFR-002: Storage Efficiency

**Category:** Resource Utilization  
**Requirement:** Index storage shall not exceed specified limits to enable local deployment.

**Metrics:**
- Total index storage: <1.5GB
- Standards index: <500MB
- Code semantic index: <800MB
- AST index: <200MB

**Priority:** High

---

### NFR-003: Memory Efficiency

**Category:** Resource Utilization  
**Requirement:** Active memory usage during queries shall remain within constraints for consumer hardware.

**Metrics:**
- Active query memory: <1GB
- Idle memory footprint: <200MB
- Embedding model memory: 134MB (BGE-small-en-v1.5)

**Priority:** High

---

### NFR-004: Accuracy at Scale

**Category:** Quality  
**Requirement:** Search accuracy shall not degrade below specified thresholds as corpus grows.

**Metrics:**
- Single-query accuracy at 200+ standards: ≥40%
- Hybrid search baseline: 50-60%
- With metadata filtering: 70%+
- Multi-query success: 90%+ within 3 queries

**Priority:** Critical

---

### NFR-005: Zero External Dependencies

**Category:** Cost & Portability  
**Requirement:** All search operations shall execute without external API calls or paid services.

**Metrics:**
- API cost per query: $0
- External service dependencies: 0
- All models/libraries: MIT or Apache 2.0 licensed
- Works fully offline after initial model download

**Priority:** Critical

---

### NFR-006: Platform Compatibility

**Category:** Portability  
**Requirement:** System shall operate on Unix-like platforms with specified Python version.

**Metrics:**
- Python version: 3.10+
- Supported platforms: macOS, Linux
- Windows support: Deferred (fcntl unavailable)
- Dependencies: pip-installable only

**Priority:** High

---

### NFR-007: Config-Driven Extensibility

**Category:** Maintainability  
**Requirement:** Adding support for new languages or features shall require only config changes and dependency installation.

**Metrics:**
- Code changes for new language: 0
- Steps to add language: 2 (edit config, install Tree-sitter package)
- Config file self-documenting: Yes (inline comments)

**Priority:** High

---

### NFR-008: Index Integrity

**Category:** Reliability  
**Requirement:** Concurrent access shall not corrupt indexes under any circumstances.

**Metrics:**
- Corruption incidents from concurrent access: 0
- Lock acquisition failures: Return teaching message 100% of time
- Lock release on crash: Automatic via OS

**Priority:** Critical

---

### NFR-009: Incremental Update Efficiency

**Category:** Performance  
**Requirement:** File watcher shall update only changed files, not full corpus rebuild.

**Metrics:**
- Single file change update time: <5s
- Debouncing configurable: Yes (per content type)
- Full rebuild avoidance: 100% of file changes

**Priority:** Medium

---

### NFR-010: Installation Automation

**Category:** Usability  
**Requirement:** Installation shall auto-detect languages and configure code search without manual intervention.

**Metrics:**
- User manual config steps: 0
- Language detection accuracy: 95%+
- Post-install code search: Works immediately

**Priority:** High

---

### NFR-011: Backward Compatibility

**Category:** Maintainability  
**Requirement:** Existing `search_standards` API shall continue to work without modification.

**Metrics:**
- Breaking changes to existing queries: 0
- Migration required: None (automatic delegation)
- Deprecation timeline: Never (permanent compatibility)

**Priority:** Critical

---

### NFR-012: Implementation Timeline

**Category:** Development Velocity  
**Requirement:** Complete implementation shall fit within single-day timeline.

**Metrics:**
- Total implementation time: 12-16 hours
- Phases: 8 (sequential)
- Blockers: None identified

**Priority:** High

---

## 6. Out of Scope

The following items are explicitly excluded from this implementation:

### 6.1 Deferred to Future Phases

1. **Dependencies Index** - Curated library documentation (Pandas, FastAPI, React, etc.)
   - Rationale: Requires external data curation, violates zero-cost constraint if API-based
   - Future: Phase 6 with local-only library docs

2. **Cross-Index Search** - Query multiple content types simultaneously (standards + code in one query)
   - Rationale: Adds complexity, current explicit `content_type` selection is clearer
   - Future: If user feedback indicates need

3. **Query Expansion** - Automatic synonym expansion or query rewriting
   - Rationale: LLM-based violates zero-cost, classical NLP deferred for complexity
   - Future: Revisit if accuracy insufficient

4. **Relevance Learning** - Machine learning on click-through data to improve rankings
   - Rationale: Requires data collection, training infrastructure
   - Future: If scale justifies complexity

5. **Distributed Deployment** - Multi-node index serving
   - Rationale: Per-project installations are single-tenant, local
   - Future: Enterprise scale-out if needed

### 6.2 Platform Limitations

6. **Windows Support** - File locking on Windows requires different approach
   - Rationale: fcntl not available on Windows, requires platform-specific code
   - Future: Add Windows file locking when Windows users identified

### 6.3 UI/Visualization

7. **Web UI for Index Management** - Browser-based index management interface
   - Rationale: MCP tool sufficient, UI adds maintenance burden
   - Future: Part of Browser-IDE module if multi-agent validated

8. **Query Analytics Dashboard** - Visualize query patterns, accuracy trends
   - Rationale: Not critical for functionality, adds complexity
   - Future: If observability gap identified

### 6.4 Advanced Features

9. **Multi-Modal Search** - Images, diagrams, video transcripts
   - Rationale: Corpus is text-only currently
   - Future: If multi-modal content adopted

10. **Real-Time Collaboration** - Shared indexes across team members
    - Rationale: Per-project installations are single-user
    - Future: Enterprise team features

11. **Version Control Integration** - Index diffs across git branches
    - Rationale: Complexity high, value unclear
    - Future: If workflow pain identified

12. **Cloud Sync** - Synchronize indexes across machines
    - Rationale: Violates local-first principle, adds external dependency
    - Future: Only if strong user demand

### 6.5 Out of Scope Rationale Summary

**Core Principles:**
- Zero-cost operation (no API calls, external services)
- Single-day implementation (12-16 hours)
- Zero breaking changes (backward compatibility)
- Per-project, single-user focus (not multi-tenant)
- Local-first (no cloud dependencies)

Any feature violating these principles is explicitly out of scope unless requirements change.

