# Supporting Documents Index

**Spec:** Multi-Index RAG Architecture  
**Created:** 2025-11-02  
**Total Documents:** 1

## Document Catalog

### 1. Multi-Index RAG Architecture Design Document

**File:** `multi-index-rag-architecture.md`  
**Type:** Design Document  
**Purpose:** Comprehensive design for enhancing prAxIs OS RAG system with hybrid search (FTS + vector), metadata filtering, and code search (semantic + structural). Addresses RAG accuracy degradation at scale (33% → 5% for 500+ standards) and enables AI-generated codebase navigation.

**Relevance:** Requirements [H], Design [H], Implementation [H]

**Key Topics:**
- Hybrid search (LanceDB native FTS + vector embeddings with RRF)
- Metadata filtering (scalar indexes: BTREE/BITMAP)
- Semantic code search (BGE embeddings on code text)
- Structural code search (Tree-sitter AST, all 50+ languages day 1)
- Config-driven file watcher (per-content-type debouncing)
- LLM-driven installation (language detection, config generation)
- Index rebuild safety (file locking with teaching messages)
- Systematic testing strategy (80%+ unit coverage, blocking gates)
- Zero-cost constraint (local models only)

---

## Cross-Document Analysis

**Common Themes:**
- Config-driven architecture (extensibility without code changes)
- Dynamic logic over static patterns (Tree-sitter language support via convention-based imports)
- Adversarial design (prevent + teach: file locking prevents corruption, returns teaching messages)
- Zero-cost operation (local embeddings, no API calls for search)
- Behavioral reinforcement (accurate RAG → correct AI behavior)

**Potential Conflicts:**
- None (single document)

**Coverage Gaps:**
- Performance benchmarks for hybrid search vs. pure vector (design mentions sub-100ms but no baseline comparison)
- Concrete examples of AST queries for different languages (patterns described but not shown)
- Migration strategy from current single-index system (assumes greenfield)

---

## Next Steps

This index will be used in Task 3 to systematically extract insights from each document. The extracted insights will be organized by:
- **Requirements Insights:** User needs, business goals, functional requirements
- **Design Insights:** Architecture patterns, technical approaches, component designs
- **Implementation Insights:** Code patterns, testing strategies, deployment guidance

---

## Extracted Insights

### Requirements Insights (Phase 1)

#### From multi-index-rag-architecture.md:
- **User Need:** AI agents need fast, accurate discovery of project standards and code patterns to maintain correct behavior at scale (500+ standards)
- **Business Goal:** Preserve behavioral reinforcement system as prAxIs OS scales from 60 to 500+ standards per project
- **Functional Req:** Improve RAG discovery accuracy from projected 5% (at 500 standards) to 70%+ through hybrid search and metadata filtering
- **Functional Req:** Enable code discovery by concept (semantic) and structure (AST queries) for AI-generated codebases
- **Functional Req:** Support all 50+ Tree-sitter languages day 1 through config-driven, dynamic architecture
- **Functional Req:** Zero-cost operation (local models only, no API calls for search)
- **Functional Req:** LLM-driven installation that detects project languages and auto-generates config
- **Functional Req:** Safe manual index rebuilds with file locking (prevent corruption + teach correct usage)
- **Constraint:** Complete implementation in single day (14-18 hours)
- **Constraint:** Zero breaking changes to existing `search_standards` API
- **Out-of-Scope:** Agentic query rewriting, relevance learning, distributed deployment, cloud sync

### Design Insights (Phase 2)

#### From multi-index-rag-architecture.md:
- **Architecture:** Single database (LanceDB) with native FTS, vector search, and scalar indexes - no external dependencies
- **Architecture:** Multi-index system with per-content-type indexes (standards, code-semantic, code-ast)
- **Architecture:** Config-driven design (`index_config.yaml`) - add languages/features without code changes
- **Component:** BaseIndex abstract class with shared indexing logic, specialized by StandardsIndex, CodeIndex, ASTIndex
- **Component:** IndexManager orchestrates all indexes, provides unified search interface
- **Component:** AgentOSFileWatcher monitors file changes, triggers incremental updates with per-content-type debouncing
- **Data Model:** LanceDB tables with schemas: `praxis_os_standards`, `praxis_os_code_semantic`, `praxis_os_code_ast`
- **Data Model:** Metadata fields for filtering: domain (backend/frontend/qa), phase (0-8), role (user/orchestrator/specialist)
- **API:** Unified `pos_search` MCP tool with explicit content_type parameter (standards/code/ast)
- **API:** Hybrid search via Reciprocal Rank Fusion (RRF) combining vector + FTS results
- **API:** Re-ranking with cross-encoder for final result ordering
- **Security:** File locking via `fcntl` (Unix) to prevent concurrent index corruption
- **Security:** Teaching messages when lock acquisition fails (adversarial design: prevent + teach)
- **Performance:** Sub-100ms query latency at billions of records (LanceDB native capabilities)
- **Performance:** Chunking strategy: 1000 tokens per chunk, 200 token overlap for standards
- **Performance:** Smaller chunks for code (500 tokens, 50 overlap) due to focused search needs
- **Technology:** BGE-small-en-v1.5 embedding model (134MB, MIT license, local)
- **Technology:** Tree-sitter for AST parsing with dynamic parser imports (convention: `tree-sitter-{language}`)
- **Technology:** LanceDB native FTS (BM25-based), no rank-bm25 library needed

### Implementation Insights (Phase 4)

#### From multi-index-rag-architecture.md:
- **Code Pattern:** Dynamic Tree-sitter parser loading via `importlib.import_module(f"tree_sitter_{language}")`
- **Code Pattern:** Graceful degradation when parser unavailable (log warning, fall back to text search)
- **Code Pattern:** Convention over configuration for Tree-sitter packages (`tree-sitter-python`, `tree-sitter-go`)
- **Code Pattern:** Config-driven file watcher patterns with per-content-type debouncing
- **Code Pattern:** LanceDB scalar index creation: `table.create_scalar_index("metadata.domain", index_type="BTREE")`
- **Code Pattern:** LanceDB FTS index: `table.create_fts_index("content", use_tantivy=False)` (BM25-based)
- **Code Pattern:** SQL WHERE clauses for metadata filtering: `WHERE metadata.domain = 'backend'`
- **Code Pattern:** RRF formula: `score = sum(1 / (k + rank_i))` where k=60
- **Testing:** Systematic approach: code inventory → dependency analysis → test plan → generation → validation
- **Testing:** 80%+ unit test coverage required on day 1 (blocking gate)
- **Testing:** Integration tests for hybrid search accuracy, metadata filtering, code search
- **Testing:** Performance tests validating sub-100ms query latency
- **Deployment:** Install to `.praxis-os/mcp_server/` (isolated venv, no project dependency conflicts)
- **Deployment:** Tree-sitter packages appended to `.praxis-os/mcp_server/requirements.txt` during install
- **Deployment:** RAGEngine delegates to new pos_search tool while maintaining backward compatibility
- **Troubleshooting:** File lock acquisition failures return teaching messages (not silent errors)
- **Troubleshooting:** Missing Tree-sitter parser logs warning with installation instructions

### Cross-References

**Validated by Multiple Sources:** 
- Config-driven architecture (mentioned in multiple phases)
- Zero-cost constraint (throughout design)
- Adversarial design philosophy (file locking, teaching messages)
- Dynamic logic over static patterns (Tree-sitter, file watcher)

**Conflicts:** 
- None (single document)

**High-Priority:**
- Hybrid search (vector + FTS) is critical for accuracy improvement (33% → 70%+)
- Metadata filtering reduces search space, enables domain-specific queries
- Config-driven architecture enables all 50+ Tree-sitter languages day 1
- Zero-cost operation is non-negotiable (local models only)
- File locking prevents index corruption (safety-critical)
- 80%+ unit test coverage required (quality gate)

## Insight Summary

**Total:** 49 insights  
**By Category:** Requirements [11], Design [17], Implementation [14], Cross-cutting [7]  
**Multi-source validated:** 4  
**Conflicts to resolve:** 0  
**High-priority items:** 6

**Phase 0 Complete:** ✅ 2025-11-02

