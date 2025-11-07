# Multi-Index RAG Architecture - Specification

**Status:** Review  
**Created:** 2025-11-02  
**Priority:** Critical  
**Category:** Enhancement  
**Estimated Time:** 14-18 hours (single day focused or 2 days comfortable)

---

## 🎯 Executive Summary

This specification defines a multi-index RAG architecture to preserve prAxIs OS's behavioral reinforcement system at scale (500+ standards). The current single-index approach degrades from 33% → 5% accuracy as the corpus grows, breaking the system that makes prAxIs OS work.

**Key Features:**
1. **Hybrid Search:** Vector + FTS (BM25) with Reciprocal Rank Fusion (33% → 50-60% accuracy)
2. **Metadata Filtering:** Scalar indexes (BTREE/BITMAP) reduce search space (50% → 70%+ accuracy)
3. **Code Search - Semantic:** BGE embeddings on code text for concept-based discovery
4. **Code Search - Structural:** Tree-sitter AST queries for precise symbol location (all 50+ languages, day 1)
5. **Config-Driven:** Dynamic language support, zero code changes for extensibility
6. **Zero-Cost:** Local models only, unlimited queries
7. **Index Safety:** File locking prevents corruption with teaching messages

**Constraint:** Complete TODAY (14-18 hours), zero breaking changes, zero external API costs.

**Impact:** Enables AI agents to maintain accurate discovery at scale + verify docs against code reality.

---

## 📚 Quick Links

| Document | Purpose | Audience |
|----------|---------|----------|
| [srd.md](srd.md) | Business goals, requirements, scope | Product, stakeholders |
| [specs.md](specs.md) | Technical architecture, APIs, data models | Architects, implementers |
| [tasks.md](tasks.md) | Phase-by-phase implementation tasks | Implementers |
| [implementation.md](implementation.md) | Code patterns, config, troubleshooting | Implementers |
| [supporting-docs/](supporting-docs/) | Original design document | All (reference) |

---

## 📋 Requirements Summary

### Business Goals (4)
1. **Preserve Behavioral Reinforcement at Scale:** Maintain 50-60%+ discovery accuracy at 500+ standards
2. **Enable Code Discovery:** AI agents verify docs against code reality ("trust but verify")
3. **Zero-Cost Enhancement:** Unlimited queries without API costs
4. **Safe Manual Operations:** File locking prevents index corruption, teaches correct usage

### User Stories (8)
- Accurate standard discovery at scale
- Code discovery by concept ("how does StateManager work")
- Precise symbol location ("where is StateManager class defined")
- Doc verification against code
- Zero-config language support (auto-detection)
- Zero-cost enhancement (local models)
- Self-teaching config (YAML comments)
- Safe manual index rebuild (file locking with teaching messages)

### Functional Requirements (12)
- **FR-001:** Hybrid search (vector + FTS with RRF)
- **FR-002:** Metadata filtering (scalar indexes: BTREE/BITMAP)
- **FR-003:** Semantic code search (BGE embeddings)
- **FR-004:** Structural code search (Tree-sitter AST)
- **FR-005:** Dynamic language support (50+ languages, config-driven)
- **FR-006:** File watcher (incremental updates, per-content-type debouncing)
- **FR-007:** Unified search tool (`pos_search` MCP tool)
- **FR-008:** LLM-driven installation (language detection, config generation)
- **FR-009:** Index rebuild safety (file locking with `fcntl`)
- **FR-010:** Self-teaching config (`index_config.yaml` with 180+ lines of comments)
- **FR-011:** Zero API cost (local models only)
- **FR-012:** Config-driven extensibility (add languages without code changes)

### Non-Functional Requirements (20 across 8 categories)
- **Performance:** <200ms query latency (p95), <1.5GB storage
- **Reliability:** File locking prevents corruption, graceful degradation
- **Maintainability:** Config-driven, systematic testing (80%+ unit coverage)
- **Usability:** Self-teaching config, teaching messages on misuse
- **Cost:** Zero API cost, local models only
- **Scalability:** Handles 500+ standards, 100K lines of code
- **Portability:** Unix/Linux/macOS (Windows deferred)
- **Development Velocity:** Complete in 14-18 hours

### Out of Scope (24 items)
- Windows support (fcntl unavailable)
- Remote/cloud indexes
- API-based embeddings
- Real-time streaming search
- Multi-user concurrency
- (See [srd.md](srd.md) for full list)

---

## 🏗️ Technical Design Summary

### Architecture Pattern
**Multi-Index Modular Architecture** with config-driven extensibility

```
User Query → pos_search(content_type, query, filters)
    ↓
IndexManager (Orchestration)
    ↓
├─ StandardsIndex: Hybrid (vector + FTS) + metadata filtering
├─ CodeIndex: Semantic search (BGE embeddings)
└─ ASTIndex: Structural search (Tree-sitter)
```

### Key Components
1. **BaseIndex:** Abstract class for all indexes
2. **IndexManager:** Config-driven orchestration, routes queries
3. **StandardsIndex:** Hybrid search (LanceDB vector + FTS + scalar indexes)
4. **CodeIndex:** Semantic code search (BGE embeddings on code text)
5. **ASTIndex:** Structural search (Tree-sitter AST, dynamic parser loading)
6. **AgentOSFileWatcher:** Incremental updates, config-driven patterns
7. **pos_search Tool:** Unified MCP tool for all content types

### Technology Stack
- **LanceDB:** All indexes (vector, FTS, scalar) - single database!
- **BGE-small-en-v1.5:** Embedding model (134MB, MIT license)
- **Tree-sitter:** AST parsing (50+ languages, dynamic imports)
- **Watchdog:** File system monitoring
- **fcntl:** File locking (Unix/Linux/macOS)

### Data Models
- **Table 1:** `praxis_os_standards` - standards corpus with vector + FTS + scalar indexes
- **Table 2:** `praxis_os_code_semantic` - code chunks with BGE embeddings
- **Table 3:** `praxis_os_code_ast` - parsed symbols (functions, classes, methods)

### Key Algorithms
- **Hybrid Search:** Reciprocal Rank Fusion (RRF, k=60) combines vector + FTS results
- **Re-Ranking:** Cross-encoder reorders top 10 results for final output
- **Metadata Filtering:** SQL WHERE clauses with scalar indexes (pre-filtering)

---

## 🛠️ Implementation Plan

### 8 Phases (14-18 hours total)

| Phase | Goal | Time | Key Deliverable |
|-------|------|------|-----------------|
| 1 | Foundation (Extensible Architecture) | 2-3h | IndexManager + BaseIndex + Zero breaking changes |
| 2 | Hybrid Search (FTS + Vector) | 1.5-2h | 33% → 50-60% accuracy |
| 3 | Metadata Filtering (Scalar Indexes) | 2-2.5h | Domain/phase/role filters, 50% → 70%+ accuracy |
| 4 | Code Search - Semantic | 1-1.5h | Concept-based code discovery (BGE) |
| 5 | Code Search - Structure | 3-3.5h | Tree-sitter AST, precise symbol location |
| 6 | File Watcher for Code | 1-1.5h | Incremental updates, hot reload |
| 7 | Installation Integration | 1-1.5h | LLM-driven config, auto-detect languages |
| 8 | Integration & Testing | 1-2h | pos_search tool, systematic testing (80%+ coverage) |

**Critical Path:** Phase 1 → 2 → 3 → 8 (7.5-10 hours)  
**Parallel Tracks:** Phases 4-7 can run in parallel with 2-3

---

## 🧪 Testing Strategy

**Systematic Approach** (from `test-generation-js-ts` workflow):
1. **Code Inventory:** Classes, methods, parameters, complexity
2. **Dependency Analysis:** External (LanceDB, Tree-sitter), Internal (RAGEngine)
3. **Test Plan:** Unit (≥80% coverage, BLOCKING) + Integration (≥60%)
4. **Test Generation:** Mock external dependencies, test success and error cases
5. **Quality Validation:** Pylint 10.0/10, MyPy 0 errors (BLOCKING)

**Coverage Targets:**
- Unit tests: ≥80% (BLOCKING quality gate)
- Integration tests: ≥60%
- All existing tests still passing (zero breaking changes)

---

## 🚨 Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tree-sitter parser incompatibility | Medium | Low | Graceful degradation, log warning |
| Accuracy targets not met | Low | High | Iterative tuning (RRF k-value, re-ranker) |
| Performance degradation | Low | Medium | Measure at each phase, optimize if needed |
| Breaking changes | Low | Critical | Comprehensive backward compatibility tests |
| Time overrun | Medium | Medium | Phase-gated approach allows partial delivery |

**Minimum Viable:** Phase 1-2 (Foundation + Hybrid Search) = 50% value in 4 hours

---

## 📦 Out of Scope (24 items)

**Deferred:**
- Windows support (fcntl unavailable, use msvcrt in future)
- Blue-green index deployment (file locking simpler, sufficient for single-user)
- Distributed/sharded indexes (not needed for per-project scale)
- Real-time streaming search
- Multi-user concurrency (per-project single-user model)

**Explicitly Not Included:**
- API-based embeddings (violates zero-cost constraint)
- Cloud-hosted indexes (local-first architecture)
- GUI for index management (CLI/MCP tools sufficient)
- Multi-tenancy
- Cross-project search

*See [srd.md](srd.md) Section 6 for complete list with rationale and future considerations.*

---

## 🚀 Getting Started

### For Reviewers
1. **Read this README** for overview
2. **Review [srd.md](srd.md)** for requirements and scope
3. **Review [specs.md](specs.md)** for technical design
4. **Review [tasks.md](tasks.md)** for implementation plan
5. **Approve or request changes**

### For Implementers
1. **Read [specs.md](specs.md)** for architecture and APIs
2. **Read [implementation.md](implementation.md)** for code patterns and config
3. **Follow [tasks.md](tasks.md)** phase by phase (DO NOT skip phases)
4. **Use `spec_execution_v1` workflow** for systematic implementation
5. **Query [supporting-docs/](supporting-docs/)** for additional context

### For Stakeholders
1. **Read this README** for executive summary
2. **Review [srd.md](srd.md)** Section 2 (Business Goals) and Section 3 (User Stories)
3. **Review risk mitigation** above
4. **Approve or request changes**

---

## 📊 Success Metrics

**Functional:**
- ✅ All 12 functional requirements implemented
- ✅ Hybrid search accuracy: 50-60% (baseline 33%)
- ✅ Filtered search accuracy: 70%+ (baseline 50%)
- ✅ Code search functional for detected languages
- ✅ Tree-sitter support for 50+ languages (config-driven)

**Performance:**
- ✅ Standards hybrid search latency: <200ms p95
- ✅ Code semantic search latency: <200ms p95
- ✅ AST structural search latency: <100ms p95
- ✅ Storage: <1.5GB total
- ✅ Memory: <1GB active

**Quality (BLOCKING):**
- ✅ Unit test coverage: ≥80%
- ✅ Integration test coverage: ≥60%
- ✅ Pylint score: 10.0/10
- ✅ MyPy: 0 errors (strict mode)
- ✅ Zero breaking changes (all existing tests pass)

**Deployment:**
- ✅ Installation auto-detects languages (95%+ accuracy)
- ✅ Zero manual config steps required
- ✅ File locking prevents corruption (zero corrupt index events)
- ✅ Graceful degradation tested (system continues with warnings)

---

## 🔗 Related Standards

- **Config-Driven Dynamic Logic:** `.praxis-os/standards/development/config-driven-dynamic-logic.md`
- **Adversarial Design:** Philosophy of preventing AI shortcuts and teaching correct behavior
- **Dogfooding Model:** Local-first development and copy-up workflow
- **Workflow Construction:** Standards for creating phase-gated workflows

---

## 📞 Support

**Questions about this spec?**
- Review [supporting-docs/](supporting-docs/) for additional context
- Use `search_standards` MCP tool to query prAxIs OS standards
- Ask the human reviewer for clarification

**Ready to implement?**
- Use `start_workflow("spec_execution_v1", target_file="srd.md")` to begin
- Follow [tasks.md](tasks.md) phase by phase
- Use [implementation.md](implementation.md) for concrete code patterns

---

**Specification Version:** 1.0.0  
**Created:** 2025-11-02  
**Status:** Awaiting Review  
**Next Step:** Human review and approval

