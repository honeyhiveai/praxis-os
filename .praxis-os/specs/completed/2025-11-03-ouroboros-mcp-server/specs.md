# Technical Specifications

**Project:** Ouroboros MCP Server  
**Date:** 2025-11-03  
**Based on:** srd.md (requirements)  
**Status:** Review

---

## 1. Architecture Overview

### 1.1 Architectural Pattern

**Primary Pattern:** Mission-Driven Layered Architecture

**Rationale:**
- **Requirements Addressed:** FR-001 through FR-004 (behavioral engineering), NFR-M3, NFR-M4 (clean boundaries)
- **Mission Alignment:** Architecture organized around enabling praxis (knowledge compounding + behavioral reinforcement), not just technical concerns
- **Benefits:**
  - Clear separation of concerns (Tools, Middleware, Subsystems, Foundation)
  - One-way dependencies (Tools → Middleware → Subsystems → Foundation)
  - Middleware layer ensures behavioral engineering at every interaction
  - Subsystem isolation prevents cross-contamination
  - Layered testing strategy (unit → integration → e2e)

**Alternative Patterns Considered:**

1. **Microservices Architecture**
   - **Why Not:** Complexity not justified; single-server per-project model simpler
   - **Trade-off:** Would enable independent scaling, but adds network latency, service discovery, distributed tracing overhead

2. **Hexagonal Architecture (Ports & Adapters)**
   - **Why Not:** Over-engineered for local single-server deployment
   - **Trade-off:** Domain-centric design appealing, but abstraction layers add complexity without clear benefit

3. **Event-Driven Architecture**
   - **Why Not:** Asynchronous complexity unnecessary; request-response model sufficient
   - **Trade-off:** Would enable decoupling, but adds message queue, eventual consistency, debugging complexity

**Trade-offs of Chosen Pattern:**
- **Pros:**
  - Clear boundaries enable reliable enforcement (behavioral, security, quality)
  - Layer-based testing strategy (mock lower layers)
  - Easy to understand and maintain
  - One-way dependencies prevent circular coupling
  - Middleware layer guarantees behavioral coverage
- **Cons:**
  - Layers can become "pass-through" if not carefully designed (mitigated by rich domain logic in each layer)
  - May seem over-engineered for "simple" tasks (intentional - complexity forces standards usage)

---

### 1.2 Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           TOOLS LAYER                                     │
│                  (AI Agent Interface - Intentionally Complex)             │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌────────────────┐│
│  │ pos_search_project  │  │ pos_workflow │  │ pos_browser │  │ pos_filesystem ││
│  └─────────────┘  └──────────────┘  └─────────────┘  └────────────────┘│
│           ┌───────────────┐                                              │
│           │ get_server_   │                                              │
│           │ info          │                                              │
│           └───────────────┘                                              │
│                                                                           │
│  Design: Domain abstraction with `action` parameter                      │
│  Purpose: Complexity → Forces standards usage → Querying                 │
│  Discovery: Auto-discover from tools/ directory                          │
│                                                                           │
└────────────────────────────┬──────────────────────────────────────────────┘
                             │ ALL tool calls flow through middleware
                             │ (NO EXCEPTIONS - 100% coverage required)
                             ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                      MIDDLEWARE LAYER (THE MISSION)                       │
│                (Behavioral Engineering - Self-Reinforcing Loop)           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ prepend_generator                                             │       │
│  │ - Query gamification (progress bars, diversity metrics)      │       │
│  │ - Appears in 100% of search results                          │       │
│  │ - Format: 📊 Queries: X/Y | Angles: [emojis] | 💡 Try: ...   │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ query_tracker                                                 │       │
│  │ - Logs every search (timestamp, query, session_id, angle)    │       │
│  │ - Detects behavioral drift (frequency drops, diversity low)  │       │
│  │ - Enables session-to-session analysis                        │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ query_classifier                                              │       │
│  │ - Multi-angle detection (📖 conceptual, 📍 location,          │       │
│  │   🔧 implementation, ⭐ critical, ⚠️ troubleshooting)          │       │
│  │ - Pattern matching on query keywords                         │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                           │
│  CRITICAL: If middleware fails, the request FAILS                        │
│            (No silent degradation - behavioral system is mandatory)      │
│                                                                           │
└────────────────────────────┬──────────────────────────────────────────────┘
                             │ Middleware wraps all subsystem calls
                             ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                         SUBSYSTEMS LAYER                                  │
│                   (Hidden Implementation - Isolated)                      │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ RAG SUBSYSTEM (Knowledge Compounding)                           │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │ IndexManager: Routes action to correct index                    │    │
│  │   ├─ StandardsIndex: Vector+FTS+RRF+Rerank (LanceDB)           │    │
│  │   ├─ CodeIndex: Semantic (LanceDB) + Graph (DuckDB)            │    │
│  │   └─ ASTIndex: Tree-sitter structural search                    │    │
│  │                                                                  │    │
│  │ FileWatcher: Incremental re-indexing (<5s latency)              │    │
│  │   - Monitors configured paths (e.g., .praxis-os/standards/)     │    │
│  │   - Routes to IndexManager → Correct index container            │    │
│  │   - Updates ALL sub-indexes (vector, FTS, scalar, graph)        │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ WORKFLOW SUBSYSTEM (Adversarial Design)                         │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │ PhaseGates: Structural enforcement (no phase skipping)          │    │
│  │ EvidenceValidator: Multi-layer validation                       │    │
│  │   - Field presence → Type → Custom → Cross-field → Artifact     │    │
│  │ HiddenSchemas: Information asymmetry (fields not exposed)       │    │
│  │ StateManager: Session persistence (.praxis-os/workflow_states/) │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ BROWSER SUBSYSTEM                                               │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │ Playwright: Isolated sessions per AI agent (keyed by           │    │
│  │             session_id)                                          │    │
│  │   - Headless mode by default                                    │    │
│  │   - Session cleanup: 30 min idle timeout                        │    │
│  │   - Browser types: chromium, firefox, webkit                    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  Design: Zero cross-talk between subsystems (no RAG → Workflow imports)  │
│  Purpose: Clean boundaries enable reliable enforcement                   │
│                                                                           │
└────────────────────────────┬──────────────────────────────────────────────┘
                             │ All subsystems use config
                             ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                         FOUNDATION LAYER                                  │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ Config (Pydantic v2)                                          │       │
│  │ - Type-safe, fail-fast validation at startup                 │       │
│  │ - Loaded from config/mcp.yaml                                │       │
│  │ - Models: MCPConfig, IndexesConfig, WorkflowConfig, etc.     │       │
│  │ - No dict["key"] access (type-safe everywhere)               │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ Logging                                                       │       │
│  │ - Structured JSON format (queryable via jq)                  │       │
│  │ - Behavioral metrics (query frequency, diversity, drift)     │       │
│  │ - Subsystem logs (index_manager.log, query_tracker.log)      │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │ Errors                                                        │       │
│  │ - Auto-fix suggestions (command to run, config to change)    │       │
│  │ - Clear field paths (e.g., "indexes → vector → chunk_size")  │       │
│  │ - Why it failed + how to fix                                 │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

### 1.3 Architectural Principles (In Priority Order)

#### Principle 1: Behavioral Engineering First

**Statement:** The middleware layer is NON-OPTIONAL. All tool calls MUST flow through behavioral reinforcement.

**Rationale:**
- **Requirements:** FR-001 (prepend generation), FR-002 (query tracking), FR-004 (drift detection)
- **Mission Alignment:** The system exists to enable praxis; behavioral engineering is the mechanism
- **Enforcement:** If prepend generation fails → Fail the request (no silent degradation)

**Implementation:**
- Middleware decorators wrap all tool entry points
- `prepend_generator` called synchronously before returning results
- If middleware unavailable → Server refuses to start (fail-fast)

---

#### Principle 2: One-Way Dependencies (Enforced)

**Statement:** Tools → Middleware → Subsystems → Foundation. NEVER reverse.

**Rationale:**
- **Requirements:** NFR-M3 (zero circular dependencies), NFR-M4 (subsystem isolation)
- **Benefits:** Testability (mock lower layers), maintainability (clear boundaries), reliability (no hidden coupling)
- **Anti-patterns:** NEVER allow Subsystems → Tools, RAG → Workflow, etc.

**Enforcement:**
- CI/CD import analysis (`importlab --tree ouroboros/`)
- Linting rules: `ruff check` configured to detect reverse imports
- Code review: Reject PRs with boundary violations

---

#### Principle 3: Config-Driven Extensibility

**Statement:** Supported behaviors (new languages, behavioral thresholds) require ONLY config changes, zero code.

**Rationale:**
- **Requirements:** FR-024 (config-driven language support), NFR-E1 (extensibility)
- **User Story:** Story 7 (Developer Adds New Language Support)
- **Benefit:** Maintainability (fewer code changes = fewer bugs)

**Implementation:**
- Pydantic v2 schemas for ALL config sections
- Subsystems read config at startup, dynamically adapt behavior
- Example: ASTIndex auto-installs Tree-sitter parsers based on `config.indexes.ast.languages`

---

#### Principle 4: Adversarial Design Throughout

**Statement:** Assume AI agents will attempt shortcuts. Make compliance easier than gaming.

**Rationale:**
- **Requirements:** FR-017 through FR-019 (phase gates, evidence validation, hidden schemas)
- **User Story:** Story 10 (AI Agent Bypasses Validation - Caught)
- **Philosophy:** Information asymmetry, multi-layer validation, fail-fast on gaming

**Implementation:**
- Hidden evidence schemas (YAML-defined, not exposed via tool schema)
- Multi-layer validation: field → type → custom → cross-field → artifact
- Clear error messages with auto-fix suggestions (make doing work easier than faking)

---

#### Principle 5: Observability Built-In

**Statement:** Query tracking, behavioral metrics, structured logging are non-negotiable features.

**Rationale:**
- **Requirements:** FR-002 (query tracking), NFR-O1 through NFR-O4 (observability)
- **User Story:** Story 6 (Human Developer Observes AI Improvement)
- **Philosophy:** Can't improve what you can't measure

**Implementation:**
- `query_tracker.log`: Every search logged (100% coverage)
- Behavioral metrics: Query frequency, diversity, session-to-session comparison
- JSON-formatted logs (queryable via `jq`)
- `get_server_info(action="behavioral_metrics")` exposes trends

---

### 1.4 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| **FR-001: Query Prepend Generation** | Middleware Layer: `prepend_generator` | Wraps all search results, generates gamification prepends (progress, diversity, suggestions) |
| **FR-002: Query Tracking** | Middleware Layer: `query_tracker` | Logs every search to `.praxis-os/logs/query_tracker.log` with full metadata |
| **FR-003: Query Diversity Classification** | Middleware Layer: `query_classifier` | Pattern-matches queries to 5 angles (📖📍🔧⭐⚠️) |
| **FR-004: Behavioral Drift Detection** | Middleware Layer: `query_tracker` + `prepend_generator` | Detects frequency/diversity drops, strengthens prepend messaging |
| **FR-005: pos_search_project Tool** | Tools Layer: `pos_search_project.py` | Unified project search with action parameter (search_standards, search_code, search_ast, find_callers, find_dependencies, find_paths) |
| **FR-006: pos_workflow Tool** | Tools Layer: `pos_workflow.py` | Workflow lifecycle with phase gates |
| **FR-007: pos_browser Tool** | Tools Layer: `pos_browser.py` | Browser automation with isolated sessions |
| **FR-008: pos_filesystem Tool** | Tools Layer: `pos_filesystem.py` | File operations with action parameter |
| **FR-009: get_server_info Tool** | Tools Layer: `get_server_info.py` | Server status, health, metrics, version |
| **FR-010: Tool Auto-Discovery** | Tools Layer: `ToolRegistry` | Scans `tools/` directory, registers with FastMCP |
| **FR-011: Standards Search** | RAG Subsystem: `StandardsIndex` | LanceDB hybrid search (vector + FTS + RRF + rerank) |
| **FR-012: Code Semantic Search** | RAG Subsystem: `CodeIndex` (LanceDB) | CodeBERT embeddings, code-optimized FTS |
| **FR-013: Code Graph Traversal** | RAG Subsystem: `CodeIndex` (DuckDB) | Recursive CTEs for call graphs (find_callers, find_dependencies, find_paths) |
| **FR-014: AST Structural Search** | RAG Subsystem: `ASTIndex` | Tree-sitter with auto-install parsers |
| **FR-015: File Watcher** | RAG Subsystem: `FileWatcher` | Monitors paths, triggers incremental updates via IndexManager |
| **FR-016: Index Health Checks** | RAG Subsystem: `IndexManager` | Startup health checks, auto-repair corrupted indexes |
| **FR-017: Phase-Gated Execution** | Workflow Subsystem: `PhaseGates` | Enforces sequential phase completion |
| **FR-018: Evidence Validation** | Workflow Subsystem: `EvidenceValidator` | Multi-layer validation (5 layers) |
| **FR-019: Hidden Evidence Schemas** | Workflow Subsystem: `HiddenSchemas` | YAML-defined schemas, not exposed to AI |
| **FR-020: Workflow State Persistence** | Workflow Subsystem: `StateManager` | Persists to `.praxis-os/workflow_states/{session_id}.json` |
| **FR-021: Isolated Playwright Sessions** | Browser Subsystem: `BrowserManager` | Session keyed by `session_id`, isolated contexts |
| **FR-022: Browser Actions** | Browser Subsystem: `BrowserManager` | Playwright actions (navigate, screenshot, click, type, etc.) |
| **FR-023: Pydantic v2 Validation** | Foundation Layer: Config | Type-safe, fail-fast config validation at startup |
| **FR-024: Config-Driven Language Support** | Foundation Layer: Config + RAG Subsystem | YAML-defined languages, zero code changes |
| **FR-025: Fail-Fast Validation** | Foundation Layer: Config + Subsystem Health Checks | Startup validation before accepting requests |
| **NFR-P1: Cold Start <30s** | All Layers: Lazy loading, optimized startup sequence | Config load → Subsystem init → Health checks → Tool discovery |
| **NFR-R2: Health Check Coverage** | RAG Subsystem: Health checks in each index | FTS/vector/scalar index validation |
| **NFR-M3: Zero Circular Dependencies** | Architectural Principle: One-Way Dependencies | Tools → Middleware → Subsystems → Foundation (enforced by CI/CD) |
| **NFR-M4: Subsystem Isolation** | Subsystems Layer: Clean boundaries | No RAG → Workflow imports, no cross-contamination |
| **NFR-O1: Structured Logging** | Foundation Layer: Logging | JSON format, queryable via `jq` |
| **NFR-O2: Behavioral Metrics** | Middleware Layer: `query_tracker` | 100% search coverage, trend analysis |

---

### 1.5 Technology Stack

#### Core Technologies

**Language:** Python 3.10+ (3.10, 3.11, 3.12 supported)
- **Rationale:** Mature ML/AI ecosystem (sentence-transformers, LanceDB, DuckDB bindings)
- **Requirements:** NFR-PO2 (Python version support)

**MCP Framework:** FastMCP
- **Rationale:** Official MCP Python framework, type hint integration, `@mcp.tool()` decorator
- **Requirements:** FR-010 (tool auto-discovery), NFR-C1 (MCP protocol compliance)

**Configuration:** Pydantic v2
- **Rationale:** Type-safe validation, fail-fast, JSON schema generation, nested models
- **Requirements:** FR-023 (Pydantic validation), NFR-U2 (fail-fast)
- **Alternative Considered:** Standard dataclasses (rejected: no validation, no auto-coercion)

#### Data Layer

**Vector Database:** LanceDB
- **Rationale:** Embedded, hybrid search (vector + FTS + metadata), persistent, production-grade
- **Requirements:** FR-011 (standards search), FR-012 (code semantic search)
- **Format:** Lance columnar format (Arrow-based)
- **Indexes:** HNSW (vector), FTS (BM25), BTREE/BITMAP (scalar metadata)

**Analytical Database:** DuckDB
- **Rationale:** Embedded, recursive CTEs for graph traversal, fast OLAP, reads Lance files directly
- **Requirements:** FR-013 (code graph traversal)
- **Schema:** `symbols` table (id, name, type, file_path), `relationships` table (caller_id, callee_id)

**Code Parsing:** Tree-sitter
- **Rationale:** Language-agnostic AST parsing, incremental parsing, bindings for Python/Go/Rust/TS
- **Requirements:** FR-014 (AST structural search), FR-024 (config-driven language support)
- **Installation:** Auto-install via pip in isolated venv (`.praxis-os/venv/`)

#### Embedding Models

**Standards/Docs:** `sentence-transformers/all-MiniLM-L6-v2` (default, configurable)
- **Rationale:** Balance of quality vs. speed, 384 dimensions, <50MB model size
- **Requirements:** FR-011 (standards search)

**Code:** `microsoft/codebert-base` or `microsoft/graphcodebert-base` (configurable)
- **Rationale:** Code-specific embeddings, trained on code corpus
- **Requirements:** FR-012 (code semantic search)

**Re-ranking (Optional):** `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **Rationale:** Improves top-K precision, <50ms latency for 10 candidates
- **Requirements:** FR-011 (standards search with re-ranking)

#### Browser Automation

**Browser:** Playwright
- **Rationale:** Multi-browser support (chromium, firefox, webkit), async API, session isolation
- **Requirements:** FR-021 (isolated sessions), FR-022 (browser actions)

#### Observability

**Logging:** Python `logging` module + JSON formatter
- **Rationale:** Built-in, structured output, queryable via `jq`
- **Requirements:** NFR-O1 (structured logging)

**Metrics:** Custom implementation (query_tracker.py)
- **Rationale:** Behavioral metrics (query frequency, diversity) not covered by standard metrics systems
- **Requirements:** NFR-O2 (behavioral metrics collection)

---

### 1.6 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       USER MACHINE                              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PROJECT DIRECTORY                                        │  │
│  │ (e.g., ~/projects/my-app/)                              │  │
│  │                                                          │  │
│  │  project_code/                                          │  │
│  │  .git/                                                   │  │
│  │  .praxis-os/                                             │  │
│  │    ├─ config/mcp.yaml        ← User-editable config     │  │
│  │    ├─ standards/              ← Project-specific        │  │
│  │    ├─ specs/                  ← Generated specs          │  │
│  │    ├─ venv/                   ← Isolated Python env     │  │
│  │    ├─ logs/                   ← Query tracker, etc.     │  │
│  │    ├─ .cache/                                            │  │
│  │    │   ├─ vector_index/       ← LanceDB files          │  │
│  │    │   └─ code.duckdb         ← DuckDB graph           │  │
│  │    └─ ouroboros/              ← Server code             │  │
│  │         ├─ tools/              ← MCP tools              │  │
│  │         ├─ middleware/         ← Behavioral eng.        │  │
│  │         ├─ subsystems/         ← RAG, Workflow, etc.   │  │
│  │         └─ __main__.py         ← Entry point           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ CURSOR / CLAUDE DESKTOP                                  │  │
│  │ (MCP Client)                                            │  │
│  │                                                          │  │
│  │  AI Agent ←──[stdio/JSON-RPC]──▶ Ouroboros MCP Server   │  │
│  │                                   (python -m ouroboros)  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Deployment Model: Per-Project Local Installation
- Each project has its own .praxis-os/ directory
- Server runs as subprocess of IDE/MCP client
- Indexes are project-specific (no shared state)
- Isolated venv prevents dependency conflicts

Communication: stdio (Standard Input/Output)
- MCP protocol over stdin/stdout
- JSON-RPC 2.0 message format
- Server started by IDE on-demand

Storage: Embedded Databases
- LanceDB: Arrow-based columnar files (.lance)
- DuckDB: Single-file database (code.duckdb)
- No external database servers required
```

---

### 1.7 Data Flow Diagrams

#### Data Flow 1: Search Flow (with Behavioral Engineering)

```
┌──────────────┐
│  AI Agent    │
│  (Cursor)    │
└──────┬───────┘
       │ 1. pos_search_project(action="search_standards", query="how to X")
       ▼
┌──────────────────────────────────────────┐
│  TOOLS LAYER: pos_search_project.py              │
│  - Validate parameters                   │
│  - Extract action, query, method         │
└──────┬───────────────────────────────────┘
       │ 2. Forward to middleware
       ▼
┌──────────────────────────────────────────┐
│  MIDDLEWARE: query_tracker               │
│  - Log query (timestamp, session_id,     │
│    action, query text)                   │
│  - Detect angle (📖📍🔧⭐⚠️)              │
└──────┬───────────────────────────────────┘
       │ 3. Route to subsystem
       ▼
┌──────────────────────────────────────────┐
│  RAG SUBSYSTEM: IndexManager             │
│  - Route action to correct index         │
│    (search_standards → StandardsIndex)   │
└──────┬───────────────────────────────────┘
       │ 4. Execute search
       ▼
┌──────────────────────────────────────────┐
│  RAG SUBSYSTEM: StandardsIndex           │
│  - Vector search (semantic similarity)   │
│  - FTS search (exact term matching)      │
│  - RRF fusion (combine results)          │
│  - Re-ranking (optional cross-encoder)   │
│  - Return: [chunk1, chunk2, ..., chunk5] │
└──────┬───────────────────────────────────┘
       │ 5. Return to middleware
       ▼
┌──────────────────────────────────────────┐
│  MIDDLEWARE: prepend_generator           │
│  - Generate prepend:                     │
│    "📊 Queries: 3/5 | Angles: 📖✓ 🔧✓    │
│     💡 Try: 'Where is X?' (📍 location)" │
│  - Prepend results                       │
└──────┬───────────────────────────────────┘
       │ 6. Return to AI agent
       ▼
┌──────────────┐
│  AI Agent    │
│  Sees:       │
│  - Prepend   │  ← Behavioral reinforcement
│  - Results   │  ← Actual search results
└──────────────┘
```

#### Data Flow 2: File Watcher → Incremental Index Update

```
┌──────────────┐
│  Developer   │
│  Saves file  │
└──────┬───────┘
       │ 1. File system event (modify, create, delete)
       ▼
┌──────────────────────────────────────────────────────────────────┐
│  RAG SUBSYSTEM: FileWatcher                                      │
│  - Monitors:                                                     │
│    • .praxis-os/standards/ → standards.md files                 │
│    • src/, lib/, app/ → code files (.py, .go, .rs, .ts, etc.)  │
│  - Debounce: 500ms (batch rapid changes)                        │
│  - Detects: file_path, event_type                               │
└──────┬───────────────────────────────────────────────────────────┘
       │ 2. Route to IndexManager (determines index from path)
       ▼
┌──────────────────────────────────────────────────────────────────┐
│  RAG SUBSYSTEM: IndexManager                                     │
│  - Path mapping:                                                 │
│    • .praxis-os/standards/ → StandardsIndex                     │
│    • src/, lib/, app/ → CodeIndex + ASTIndex (parallel)         │
└──────┬───────────────────────────────────────────────────────────┘
       │
       ├─────────────────────────┬──────────────────────────────────┐
       │ 3a. Standards path      │ 3b. Code path (both)             │
       ▼                         ▼                                  │
┌──────────────────────┐  ┌──────────────────────┐                 │
│  StandardsIndex      │  │  CodeIndex           │                 │
│  - Parse markdown    │  │  - Parse code        │                 │
│  - Generate embs     │  │  - Generate embs     │                 │
│  - Update LanceDB:   │  │  - Update LanceDB:   │                 │
│    • Vector index    │  │    • Vector (768d)   │                 │
│    • FTS (BM25)      │  │    • FTS (code-opt)  │                 │
│    • Scalar (meta)   │  │    • Scalar (lang)   │                 │
│  - <5s latency       │  │  - Extract symbols   │                 │
└──────────────────────┘  │  - Extract calls     │                 │
                          │  - Update DuckDB:    │                 │
                          │    • symbols table   │                 │
                          │    • relationships   │                 │
                          │  - <10s latency      │                 │
                          └──────────────────────┘                 │
                                                                    │
                          ┌──────────────────────┐                 │
                          │  ASTIndex            │◄────────────────┘
                          │  - Parse via Tree-s  │
                          │  - Extract AST nodes │
                          │  - Index symbols     │
                          │  - Index locations   │
                          │  - <5s latency       │
                          └──────────────────────┘
       │                         │                                  │
       └─────────────────────────┴──────────────────────────────────┘
       │ 4. All indexes updated, file now searchable
       ▼
┌──────────────────────────────────────────────────────────────────┐
│  AI Agent                                                        │
│  Can now discover new content via:                              │
│  - pos_search_project(action="search_standards", query="...")   │
│  - pos_search_project(action="search_code", query="...")        │
│  - pos_search_project(action="search_ast", query="...")         │
│  - pos_search_project(action="find_callers", query="X")         │
│  - pos_search_project(action="find_dependencies", query="X")    │
│  - pos_search_project(action="find_paths", from_symbol="X", to_symbol="Y")│
└──────────────────────────────────────────────────────────────────┘
```

---

### 1.8 Architectural Decisions

#### Decision 1: Middleware Layer as Non-Optional

**Decision:** ALL tool calls MUST flow through middleware. If middleware fails, requests fail (no silent degradation).

**Rationale:**
- **Requirement:** FR-001, FR-002, FR-003, FR-004 (behavioral engineering)
- **User Story:** Story 4 (AI Agent Applies Multi-Angle Discovery)
- **Benefit:** Guarantees behavioral reinforcement at every interaction
- **Mission Alignment:** Praxis requires 100% behavioral coverage; partial coverage = partial mission

**Alternatives Considered:**
- **Middleware as optional:** Rejected. Would enable silent degradation, breaking behavioral mission.
- **Middleware per-subsystem:** Rejected. Would allow inconsistent prepend generation across subsystems.

**Trade-offs:**
- **Pros:** Reliable behavioral enforcement, consistent prepends, query tracking never misses
- **Cons:** Middleware adds 5-10ms latency (acceptable per NFR-P6), middleware failure halts system (intentional)

**Implementation:** Middleware wraps tool entry points via decorators or FastMCP hooks.

---

#### Decision 2: Domain Abstraction Pattern for Tools

**Decision:** Tools are domains (`pos_search_project`, `pos_workflow`) with `action` parameter, not one tool per function.

**Rationale:**
- **Requirement:** FR-005 through FR-009 (unified tools)
- **User Story:** Implicit (AI agent discovers tool capabilities via schema)
- **Benefit:** Smaller tool footprint (5 tools vs. 50+), reasoning-friendly, forces standards usage (complexity by design)

**Alternatives Considered:**
- **One tool per function:** Rejected. Would create tool proliferation (50+ tools), AI never queries standards (tools too simple).
- **Monolithic tool:** Rejected. Would create parameter explosion (100+ params in single tool).

**Trade-offs:**
- **Pros:** Forces standards usage (parameter complexity), smaller tool count, clear domain boundaries
- **Cons:** Parameter complexity (intentional - mitigated by standards documentation)

**Implementation:** `action` parameter uses `Literal` type hints (exposed as enum in FastMCP schema for discoverability).

---

#### Decision 3: LanceDB + DuckDB Hybrid for Code Search

**Decision:** LanceDB for semantic search (vector + FTS), DuckDB for graph traversal (call graphs via recursive CTEs).

**Rationale:**
- **Requirement:** FR-012 (code semantic search), FR-013 (code graph traversal)
- **User Story:** Story 3 (AI Agent Finds Code Context via Graph Traversal)
- **Benefit:** "Best of both worlds" - LanceDB excels at hybrid search, DuckDB excels at graph queries

**Alternatives Considered:**
- **LanceDB only:** Rejected. No native graph traversal (would require manual BFS/DFS in Python, slow).
- **DuckDB only:** Rejected. VSS extension experimental, vector search not production-ready.
- **Neo4j:** Rejected. Not embedded, adds operational complexity (separate database server).

**Trade-offs:**
- **Pros:** Leverages each DB's strengths, both embedded (no servers), DuckDB reads Lance files directly
- **Cons:** Two databases to maintain, schema coordination required

**Implementation:** `CodeIndex` manages both LanceDB (semantic) and DuckDB (graph), exposes unified interface.

---

#### Decision 4: Greenfield Rewrite (Ouroboros) vs. Refactor (mcp_server/)

**Decision:** Ground-up rewrite in `.praxis-os/ouroboros/`, selective code extraction from `mcp_server/`.

**Rationale:**
- **Analysis:** 30,000 LOC of coupled code in `mcp_server/`, refactor estimated 4-6 weeks vs. 3-4 weeks for rewrite
- **Benefit:** Clean architecture from Day 1, no backward compat constraints, old server as safety net
- **Risk Mitigation:** Parallel development (old server keeps working)

**Alternatives Considered:**
- **Refactor in-place:** Rejected. Would touch 80%+ of codebase, high risk of breaking functionality.
- **Hybrid approach:** Rejected. Unclear boundaries (when to refactor vs. rewrite), worst of both worlds.

**Trade-offs:**
- **Pros:** Faster timeline, lower risk (safety net), clean slate
- **Cons:** Must recreate all functionality, git history reset (acceptable)

**Implementation:** Selective extraction (e.g., workflow engine if well-isolated), otherwise rewrite.

---

#### Decision 5: Hidden Evidence Schemas (Adversarial Design)

**Decision:** Evidence requirements NOT exposed to AI agents until submission (information asymmetry).

**Rationale:**
- **Requirement:** FR-019 (hidden evidence schemas)
- **User Story:** Story 10 (AI Agent Bypasses Validation - Caught)
- **Philosophy:** Prevents Goodhart's Law (optimizing for validation over completion)

**Alternatives Considered:**
- **Expose schema upfront:** Rejected. Would enable AI to optimize for validation fields without doing work.
- **Partial exposure:** Rejected. Still enables gaming (AI learns which fields to fake).

**Trade-offs:**
- **Pros:** Prevents gaming, forces genuine work
- **Cons:** AI must iterate on evidence submission (intentional - learning through consequences)

**Implementation:** Workflow YAML defines schemas, validation errors reveal missing fields AFTER submission.

---

## 2. Component Design

This section defines all components from the 4-layer architecture, specifying responsibilities, interfaces, dependencies, and error handling for each.

---

### 2.1 TOOLS LAYER

#### Component: ToolRegistry

**Purpose:** Auto-discovers and registers MCP tools from `tools/` directory with FastMCP.

**Responsibilities:**
- Scan `tools/` directory for Python modules on server startup
- Import modules and extract functions decorated with `@mcp.tool()`
- Extract tool signatures from type hints (for FastMCP schema generation)
- Register tools with FastMCP server
- Provide clear error messages for tool loading failures

**Requirements Satisfied:**
- FR-010: Tool Auto-Discovery and Registration
- NFR-E2: Tool Auto-Discovery (extensibility)

**Public Interface:**
```python
class ToolRegistry:
    def __init__(self, tools_dir: Path, mcp_server: FastMCP):
        """Initialize with tools directory and FastMCP server instance."""
        
    def discover_tools(self) -> List[ToolDefinition]:
        """Scan tools/ directory, return discovered tool definitions."""
        
    def register_tool(self, tool: ToolDefinition) -> None:
        """Register single tool with FastMCP."""
        
    def register_all(self) -> Dict[str, Any]:
        """Discover and register all tools. Returns registration results."""
```

**Dependencies:**
- Requires: FastMCP server instance, tools/ directory exists
- Provides: Registered tools available to AI agents via `tools/list`

**Error Handling:**
- Module import fails → Log error with module name, skip module, continue discovery
- Invalid `@mcp.tool()` decorator → Log error with function name, skip function
- Type hint extraction fails → Log error, use generic signature
- Zero tools discovered → Fail server startup (no tools = no functionality)

---

#### Component: pos_search_project

**Purpose:** Unified search tool with action-based interface for all project knowledge (standards, code semantic, AST structural, call graph traversal).

**Responsibilities:**
- Validate parameters (`action`, `query`, `method`, graph-specific params)
- Route to IndexManager based on `action` (search_standards → StandardsIndex, find_callers → CodeIndex.graph)
- Execute action (6 types: search_standards, search_code, search_ast, find_callers, find_dependencies, find_paths)
- Return results to middleware for prepend generation

**Requirements Satisfied:**
- FR-005: pos_search_project - Unified Search Tool
- User Story 1: AI Agent Discovers Project Patterns
- User Story 3: AI Agent Finds Code Context via Graph Traversal

**Public Interface:**
```python
@mcp.tool()
async def pos_search_project(
    action: Literal[
        "search_standards",  # Hybrid search standards docs
        "search_code",       # Semantic code search (LanceDB)
        "search_ast",        # Structural AST search (Tree-sitter)
        "find_callers",      # Graph: who calls this symbol?
        "find_dependencies", # Graph: what does this symbol call?
        "find_paths"         # Graph: show call chain A→B
    ],
    query: str,
    method: Literal["hybrid", "vector", "fts"] = "hybrid",  # For search_* actions
    n_results: int = 5,
    max_depth: int = 10,  # For graph traversal
    to_symbol: Optional[str] = None,  # For find_paths
    **kwargs
) -> Dict[str, Any]:
    """Unified search across content types with action-based operations."""
```

**Dependencies:**
- Requires: IndexManager (RAG subsystem), middleware (prepend_generator, query_tracker)
- Provides: Search results with prepends to AI agents

**Error Handling:**
- Invalid `action` → Pydantic validation error with enum of valid actions (search_standards, search_code, search_ast, find_callers, find_dependencies, find_paths)
- IndexManager unavailable → Return error "RAG subsystem not initialized"
- Search failure → Return error with specific cause (corrupted index, missing parser, DuckDB query timeout)
- Graph action on standards → Return error "Graph traversal not supported for standards, use action='search_standards'"
- Missing `to_symbol` for find_paths → Validation error "find_paths requires 'to_symbol' parameter"

---

#### Component: pos_workflow

**Purpose:** Unified workflow execution tool supporting lifecycle management (start, get_phase, get_task, complete_phase, pause, resume).

**Responsibilities:**
- Validate parameters (`action`, `workflow_type`, `session_id`)
- Route to WorkflowEngine based on action
- Return workflow overview on start (phases, tasks, estimated duration)
- Validate evidence on complete_phase (multi-layer validation)
- Return phase/task content to AI agent

**Requirements Satisfied:**
- FR-006: pos_workflow - Workflow Execution Tool
- User Story 10: AI Agent Bypasses Validation (Caught by Adversarial Design)

**Public Interface:**
```python
@mcp.tool()
async def pos_workflow(
    action: Literal["start", "get_phase", "get_task", "complete_phase", "list_sessions", "get_session", "pause", "resume", "delete_session"],
    session_id: Optional[str] = None,
    workflow_type: Optional[str] = None,
    target_file: Optional[str] = None,
    phase: Optional[int] = None,
    task_number: Optional[int] = None,
    evidence: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Unified workflow lifecycle management."""
```

**Dependencies:**
- Requires: WorkflowEngine (Workflow subsystem), StateManager
- Provides: Phase-gated execution with evidence validation

**Error Handling:**
- Invalid `action` → Validation error with valid actions
- Missing required parameters → Validation error with parameter name
- Evidence validation fails → Return detailed errors (field path, expected vs. actual, auto-fix suggestion)
- Workflow not found → Return error "No workflow found for session_id"

---

#### Component: pos_browser

**Purpose:** Browser automation tool with Playwright, supporting isolated sessions per AI agent.

**Responsibilities:**
- Validate parameters (`action`, `session_id`, `url`, `selector`, etc.)
- Route to BrowserManager based on action
- Maintain isolated sessions (keyed by `session_id`)
- Execute browser actions (navigate, screenshot, click, type, fill, etc.)
- Clean up sessions on close or timeout

**Requirements Satisfied:**
- FR-007: pos_browser - Browser Automation Tool
- FR-021: Isolated Playwright Sessions
- FR-022: Browser Actions

**Public Interface:**
```python
@mcp.tool()
async def pos_browser(
    action: Literal["navigate", "screenshot", "click", "type", "fill", "select", "wait", "evaluate", "close"],
    session_id: Optional[str] = None,
    url: Optional[str] = None,
    selector: Optional[str] = None,
    text: Optional[str] = None,
    value: Optional[str] = None,
    screenshot_path: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Unified browser automation with isolated sessions."""
```

**Dependencies:**
- Requires: BrowserManager (Browser subsystem), Playwright
- Provides: Browser automation for AI agent testing/verification

**Error Handling:**
- Invalid `action` → Validation error with valid actions
- Session not found → Create new session if `action="navigate"`, else error
- Navigation timeout → Return error with URL, timeout value
- Selector not found → Return error with selector, page URL, available elements
- Session timeout (30 min idle) → Auto-close session, log cleanup

---

#### Component: pos_filesystem

**Purpose:** File operations tool supporting all filesystem actions (read, write, delete, list, move, copy) with parameter grouping.

**Responsibilities:**
- Validate parameters (`action`, `path`, `content`, flags)
- Execute filesystem operations
- Respect gitignore (don't modify ignored files unless override flag)
- Safe defaults (no recursive delete without explicit flag)
- Standards document parameter groupings

**Requirements Satisfied:**
- FR-008: pos_filesystem - File Operations Tool

**Public Interface:**
```python
@mcp.tool()
async def pos_filesystem(
    action: Literal["read", "write", "delete", "list", "move", "copy", "exists", "mkdir", "rmdir"],
    path: str,
    content: Optional[str] = None,
    destination: Optional[str] = None,
    recursive: bool = False,
    follow_symlinks: bool = False,
    encoding: str = "utf-8",
    create_parents: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """Unified file operations with safe defaults."""
```

**Dependencies:**
- Requires: Python `pathlib`, `.gitignore` parser
- Provides: File operations for AI agent

**Error Handling:**
- Invalid `action` → Validation error with valid actions
- Path not found → Return error with path
- Permission denied → Return error with path, required permissions
- Recursive delete without flag → Reject with error "Use recursive=True to delete directory"
- Gitignored file → Reject with error "File is gitignored, use override_gitignore=True"

---

#### Component: get_server_info

**Purpose:** Server status, health, behavioral metrics, and version information.

**Responsibilities:**
- Validate `action` parameter
- Return server status (uptime, config loaded, subsystems initialized)
- Return health status (index status, parsers installed, config valid)
- Return behavioral metrics (query frequency, diversity, trends)
- Return version information (server, Python, dependencies)

**Requirements Satisfied:**
- FR-009: get_server_info - Server Status Tool
- User Story 6: Human Developer Observes AI Improvement

**Public Interface:**
```python
@mcp.tool()
async def get_server_info(
    action: Literal["status", "health", "behavioral_metrics", "version"] = "status"
) -> Dict[str, Any]:
    """Server status, health, metrics, version."""
```

**Dependencies:**
- Requires: All subsystems (RAG, Workflow, Browser), query_tracker logs
- Provides: Observability data for AI agents and humans

**Error Handling:**
- Invalid `action` → Validation error with valid actions
- Health check fails → Return errors with remediation suggestions
- Behavioral metrics unavailable → Return warning "No query data yet"

---

### 2.2 MIDDLEWARE LAYER

#### Component: prepend_generator

**Purpose:** Generate query gamification prepends for 100% of search results.

**Responsibilities:**
- Generate progress bar (`Queries: X/Y`)
- Calculate diversity metrics (`Angles: 📖✓ 📍⬜ 🔧✓ ⭐⬜ ⚠️⬜`)
- Generate actionable suggestions (`💡 Try: '[query]' ([angle] angle)`)
- Format prepend consistently
- Ensure generation time <5ms (p95)

**Requirements Satisfied:**
- FR-001: Query Prepend Generation
- User Story 4: AI Agent Applies Multi-Angle Discovery

**Public Interface:**
```python
class PrependGenerator:
    def __init__(self, query_tracker: QueryTracker):
        """Initialize with query tracker for session history."""
        
    def generate(self, query_record: QueryRecord) -> str:
        """Generate gamification prepend for query. Returns formatted string."""
        
    def _calculate_diversity(self, session_id: str) -> float:
        """Calculate diversity score (0.0-1.0) from session history."""
        
    def _suggest_next_angle(self, angles_used: Set[str]) -> str:
        """Suggest next angle to query based on what's missing."""
```

**Dependencies:**
- Requires: query_tracker (for session history, angle analysis)
- Provides: Prepends for all search results

**Error Handling:**
- Query tracker unavailable → Log error, generate minimal prepend (no fail)
- Calculation error → Log error, return default prepend
- Timeout (>5ms) → Log warning, return cached prepend
- If generation fails critically → FAIL the request (per architectural principle)

---

#### Component: query_tracker

**Purpose:** Log every search query with metadata, detect behavioral drift.

**Responsibilities:**
- Log query to `.praxis-os/logs/query_tracker.log` (structured JSON)
- Record: timestamp, action, method, query, session_id, angle_detected
- Calculate diversity score per session
- Detect drift (frequency drops, diversity low)
- Provide session-to-session comparison data

**Requirements Satisfied:**
- FR-002: Query Tracking and Persistence
- FR-004: Behavioral Drift Detection
- User Story 2: AI Agent Learns Cross-Session Patterns

**Public Interface:**
```python
class QueryTracker:
    def __init__(self, log_path: Path, query_classifier: QueryClassifier):
        """Initialize with log path and classifier."""
        
    def log_query(self, query_record: QueryRecord) -> None:
        """Log query to tracker log (JSON format)."""
        
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics (query count, diversity, angles used)."""
        
    def detect_drift(self, session_id: str) -> Optional[DriftAlert]:
        """Detect behavioral drift. Returns alert if drift detected."""
        
    def session_comparison(self, session_ids: List[str]) -> Dict[str, Any]:
        """Compare metrics across sessions. Returns trends."""
```

**Dependencies:**
- Requires: query_classifier (for angle detection), structured logging
- Provides: Query logs, behavioral metrics for prepend_generator and get_server_info

**Error Handling:**
- Log write fails → Log to stderr, continue (don't fail request)
- Log file full (>1GB) → Rotate log, archive old logs
- Drift detection fails → Log error, skip drift alert
- Session data corrupted → Log error, return empty stats

---

#### Component: query_classifier

**Purpose:** Automatically classify queries into 5 angles using pattern matching.

**Responsibilities:**
- Classify query into angles: 📖 conceptual, 📍 location, 🔧 implementation, ⭐ critical, ⚠️ troubleshooting
- Support multiple angles per query
- Default to implementation if unclassified
- Maintain >80% classification accuracy
- Ensure classification time <1ms (p95)

**Requirements Satisfied:**
- FR-003: Query Diversity Classification

**Public Interface:**
```python
class QueryClassifier:
    def __init__(self, patterns_config: Dict[str, List[str]]):
        """Initialize with pattern definitions from config."""
        
    def classify(self, query: str) -> Set[str]:
        """Classify query. Returns set of angle names."""
        
    def _match_patterns(self, query: str, patterns: List[str]) -> bool:
        """Check if query matches any pattern in list."""
```

**Dependencies:**
- Requires: Pattern definitions (loaded from config or hardcoded)
- Provides: Angle classification for query_tracker and prepend_generator

**Error Handling:**
- Pattern matching fails → Log error, default to "implementation"
- Empty query → Return set(["implementation"])
- Classification timeout → Log warning, default to "implementation"

---

### 2.3 RAG SUBSYSTEM

#### Component: IndexManager

**Purpose:** Central orchestrator routing search actions to correct index containers.

**Responsibilities:**
- Route `action` to correct index (search_standards → StandardsIndex, search_code → CodeIndex, find_callers → CodeIndex.graph)
- Initialize all indexes on server startup
- Coordinate health checks across all indexes
- Trigger index rebuilds when needed
- Provide unified search interface

**Requirements Satisfied:**
- Central routing for FR-011, FR-012, FR-013, FR-014
- FR-016: Index Health Checks and Auto-Repair

**Public Interface:**
```python
class IndexManager:
    def __init__(self, config: IndexesConfig):
        """Initialize with index configuration."""
        
    def route_action(self, action: str, query: str, **kwargs) -> Dict[str, Any]:
        """Route action to correct index. Main entry point for pos_search_project."""
        
    def get_index(self, index_name: str) -> BaseIndex:
        """Get index instance by name (standards, code, ast)."""
        
    def health_check_all(self) -> Dict[str, HealthStatus]:
        """Run health checks on all indexes. Returns status per index."""
        
    def rebuild_index(self, index_name: str) -> None:
        """Rebuild specified index from source."""
```

**Dependencies:**
- Requires: StandardsIndex, CodeIndex, ASTIndex, config (Pydantic)
- Provides: Unified search interface for pos_search_project tool

**Error Handling:**
- Unknown action → Return error "Invalid action: {action}. Valid: search_standards, search_code, search_ast, find_callers, find_dependencies, find_paths"
- Index initialization fails → Log error, mark index unavailable
- Health check fails → Attempt auto-repair, log results
- Search on unavailable index → Return error "Index unavailable: {index_name}"

---

#### Component: StandardsIndex

**Purpose:** Hybrid search (vector + FTS + RRF + rerank) over standards content using LanceDB.

**Responsibilities:**
- Load embedding model (sentence-transformers) from config
- Chunk markdown documents (800 tokens, 100 overlap)
- Build LanceDB indexes: vector (HNSW), FTS (BM25), scalar (BTREE/BITMAP)
- Execute hybrid search: vector search → FTS search → RRF fusion → optional reranking
- Support metadata filtering (framework_type, phase, is_critical)
- Incremental updates (add/update/delete chunks)

**Requirements Satisfied:**
- FR-011: Standards Search (Hybrid: Vector + FTS + RRF + Rerank)
- User Story 1: AI Agent Discovers Project Patterns

**Public Interface:**
```python
class StandardsIndex(BaseIndex):
    def __init__(self, config: StandardsConfig, index_path: Path):
        """Initialize with config and index storage path."""
        
    def build(self, source_paths: List[Path], use_incremental: bool = False) -> None:
        """Build or update index from source paths."""
        
    def search(
        self, 
        query: str, 
        method: Literal["hybrid", "vector", "fts"] = "hybrid",
        n_results: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Execute search. Returns ranked results."""
        
    def health_check(self) -> HealthStatus:
        """Check index health (FTS exists, vector dimension correct, etc.)."""
        
    def _rebuild_fts_index(self) -> None:
        """Rebuild FTS index with replace=True."""
        
    def _rebuild_scalar_indexes(self) -> None:
        """Rebuild scalar indexes (BTREE/BITMAP) after incremental updates."""
```

**Dependencies:**
- Requires: LanceDB, sentence-transformers, markdown parser
- Provides: Standards search results for pos_search_project

**Error Handling:**
- Embedding model load fails → Log error, fall back to default model
- FTS index corrupted → Rebuild with `replace=True`, log repair
- Scalar indexes stale → Rebuild via `table.optimize()`, log repair
- Search query fails → Log error, return empty results with error message

---

#### Component: CodeIndex

**Purpose:** Hybrid code search (LanceDB semantic + DuckDB graph traversal).

**Responsibilities:**
- **LanceDB (Semantic):**
  - Load CodeBERT/GraphCodeBERT embedding model from config
  - Chunk code (200 tokens, function/class granularity)
  - Build LanceDB indexes: vector, FTS (code-optimized), scalar (language, symbol_type)
  - Execute hybrid search (vector + FTS + RRF)
- **DuckDB (Graph):**
  - Extract call graph from Tree-sitter ASTs (who calls what?)
  - Build DuckDB tables: `symbols` (id, name, type, file), `relationships` (caller_id, callee_id)
  - Execute graph queries: find_callers, find_dependencies, find_call_paths (recursive CTEs)

**Requirements Satisfied:**
- FR-012: Code Semantic Search (LanceDB)
- FR-013: Code Graph Traversal (DuckDB)
- User Story 3: AI Agent Finds Code Context via Graph Traversal

**Public Interface:**
```python
class CodeIndex(BaseIndex):
    def __init__(self, config: CodeConfig, lance_path: Path, duckdb_path: Path):
        """Initialize with config, LanceDB path, DuckDB path."""
        
    def build(self, source_paths: List[Path], languages: List[str]) -> None:
        """Build semantic index (LanceDB) and graph index (DuckDB)."""
        
    def search(
        self, 
        query: str, 
        method: Literal["hybrid", "vector", "fts"] = "hybrid",
        n_results: int = 5
    ) -> List[Dict]:
        """Semantic search via LanceDB."""
        
    def find_callers(self, symbol_name: str, max_depth: int = 10) -> List[Dict]:
        """Graph query: Who calls this symbol? (DuckDB recursive CTE)."""
        
    def find_dependencies(self, symbol_name: str, max_depth: int = 10) -> List[Dict]:
        """Graph query: What does this symbol call? (DuckDB recursive CTE)."""
        
    def find_call_paths(
        self, 
        from_symbol: str, 
        to_symbol: str, 
        max_depth: int = 10
    ) -> List[List[str]]:
        """Graph query: Call chain from X to Y (DuckDB recursive CTE)."""
```

**Dependencies:**
- Requires: LanceDB, DuckDB, CodeBERT/GraphCodeBERT, Tree-sitter (for AST extraction)
- Provides: Code search (semantic + graph) for pos_search_project

**Error Handling:**
- CodeBERT load fails → Fall back to default sentence-transformers model
- DuckDB table creation fails → Log error, disable graph features
- Recursive CTE exceeds max_depth → Return partial results with warning
- Symbol not found → Return empty results with "Symbol not found in index"

---

#### Component: ASTIndex

**Purpose:** Structural code search using Tree-sitter ASTs with auto-install parsers.

**Responsibilities:**
- Auto-install Tree-sitter parsers (based on config) in isolated venv
- Parse source files to ASTs
- Index: symbol definitions, function/class locations, call sites
- Query: symbol lookup, definition search, usage search
- Support config-driven languages (Python, Go, Rust, TypeScript, etc.)

**Requirements Satisfied:**
- FR-014: AST Structural Search (Tree-sitter)
- FR-024: Config-Driven Language Support

**Public Interface:**
```python
class ASTIndex(BaseIndex):
    def __init__(self, config: ASTConfig, index_path: Path, venv_path: Path):
        """Initialize with config, index path, isolated venv path."""
        
    def ensure_parser(self, language: str) -> None:
        """Ensure Tree-sitter parser installed for language. Auto-install if missing."""
        
    def build(self, source_paths: List[Path]) -> None:
        """Build AST index from source files."""
        
    def search_symbol(self, symbol_name: str, language: Optional[str] = None) -> List[Dict]:
        """Search for symbol definition."""
        
    def search_usage(self, symbol_name: str, language: Optional[str] = None) -> List[Dict]:
        """Search for symbol usage sites."""
```

**Dependencies:**
- Requires: Tree-sitter (Python bindings), isolated venv, pip (for parser install)
- Provides: AST structural search for pos_search_project

**Error Handling:**
- Parser install fails → Log error with language, package name, network error
- Parse error (malformed code) → Log error with file, line, skip file
- Language not configured → Return error "Language not configured: {language}"
- Parser timeout (>30s install) → Return error "Parser install timeout"

---

#### Component: FileWatcher

**Purpose:** Monitor configured paths, trigger incremental index updates within 5 seconds.

**Responsibilities:**
- Monitor paths from config (e.g., `.praxis-os/standards/`)
- Detect file events: create, modify, delete
- Debounce rapid changes (500ms window)
- Route to IndexManager → Correct index container
- Ensure index container updates ALL sub-indexes (vector, FTS, scalar, graph)

**Requirements Satisfied:**
- FR-015: File Watcher (Incremental Index Updates)
- User Story 1: AI Agent Discovers Project Patterns (fresh content)

**Public Interface:**
```python
class FileWatcher:
    def __init__(self, config: FileWatcherConfig, index_manager: IndexManager):
        """Initialize with config and index manager."""
        
    def start(self) -> None:
        """Start monitoring configured paths."""
        
    def stop(self) -> None:
        """Stop monitoring."""
        
    def _on_file_event(self, event: FileSystemEvent) -> None:
        """Handle file event (create, modify, delete)."""
        
    def _debounce(self, file_path: Path, event_type: str) -> None:
        """Debounce rapid changes (500ms window)."""
```

**Dependencies:**
- Requires: IndexManager, `watchdog` library (filesystem monitoring)
- Provides: Incremental index updates for all indexes

**Error Handling:**
- Monitoring fails (permission denied) → Log error, fall back to manual rebuild
- IndexManager unavailable → Queue updates, retry when available
- Update fails → Log error, continue monitoring (don't crash watcher)
- Debounce overflow (>100 pending) → Trigger full rebuild

---

### 2.4 WORKFLOW SUBSYSTEM

#### Component: PhaseGates

**Purpose:** Enforce sequential phase completion (no phase skipping).

**Responsibilities:**
- Validate phase progression (must complete phase N before N+1)
- Check evidence submission before advancing
- Return phase content (tasks, guidance) to AI agent
- Persist phase completion state

**Requirements Satisfied:**
- FR-017: Phase-Gated Execution
- User Story 10: AI Agent Bypasses Validation

**Public Interface:**
```python
class PhaseGates:
    def __init__(self, workflow_def: WorkflowDefinition, state_manager: StateManager):
        """Initialize with workflow definition and state manager."""
        
    def can_advance(self, session_id: str, to_phase: int) -> Tuple[bool, str]:
        """Check if can advance to phase. Returns (allowed, reason)."""
        
    def get_phase_content(self, session_id: str, phase: int) -> Dict:
        """Get phase content (tasks, guidance). Validates current phase."""
        
    def complete_phase(self, session_id: str, phase: int, evidence: Dict) -> Dict:
        """Complete phase with evidence. Validates and advances."""
```

**Dependencies:**
- Requires: WorkflowDefinition (loaded from YAML), StateManager
- Provides: Phase-gated execution for pos_workflow

**Error Handling:**
- Phase skip attempt → Return error "Phase {N} incomplete. Complete phase {N} before advancing."
- Evidence missing → Delegate to EvidenceValidator
- State corrupted → Return error, suggest session restart

---

#### Component: EvidenceValidator

**Purpose:** Multi-layer validation (field presence → type → custom → cross-field → artifact).

**Responsibilities:**
- Validate field presence (required fields exist)
- Validate types (e.g., tests_passing is boolean)
- Validate custom constraints (e.g., chunk_size >= 100)
- Validate cross-field (e.g., if tests_passing=True, then test_artifact_path required)
- Validate artifacts (e.g., test_artifact_path points to valid JUnit XML)
- Generate clear errors with auto-fix suggestions

**Requirements Satisfied:**
- FR-018: Evidence Validation (Multi-Layer)
- User Story 10: AI Agent Bypasses Validation

**Public Interface:**
```python
class EvidenceValidator:
    def __init__(self, schema: Dict, validators: Dict[str, Callable]):
        """Initialize with evidence schema and custom validators."""
        
    def validate(self, evidence: Dict) -> ValidationResult:
        """Validate evidence. Returns result with errors/warnings."""
        
    def _validate_field_presence(self, evidence: Dict, required_fields: List[str]) -> List[str]:
        """Layer 1: Check required fields exist."""
        
    def _validate_types(self, evidence: Dict, type_map: Dict) -> List[str]:
        """Layer 2: Check field types."""
        
    def _validate_artifacts(self, evidence: Dict, artifact_fields: List[str]) -> List[str]:
        """Layer 5: Check artifact files exist and valid."""
```

**Dependencies:**
- Requires: Evidence schema (loaded from workflow YAML), filesystem access (for artifact validation)
- Provides: Multi-layer validation for PhaseGates

**Error Handling:**
- Schema load fails → Return error "Evidence schema invalid"
- Artifact not found → Return error with field path, expected location
- Artifact invalid (e.g., malformed XML) → Return error with parse error
- Validation timeout → Return error "Validation timeout"

---

#### Component: HiddenSchemas

**Purpose:** Information asymmetry - evidence schemas not exposed until submission.

**Responsibilities:**
- Load evidence schemas from workflow YAML (not exposed via tool schema)
- Provide schemas to EvidenceValidator (internal only)
- Generate validation errors AFTER submission (not before)
- Rationale documented: Prevents Goodhart's Law (optimizing for validation over work)

**Requirements Satisfied:**
- FR-019: Hidden Evidence Schemas
- User Story 10: AI Agent Bypasses Validation (philosophy)

**Public Interface:**
```python
class HiddenSchemas:
    def __init__(self, workflow_dir: Path):
        """Initialize with workflow directory (loads all workflow schemas)."""
        
    def get_schema(self, workflow_type: str, phase: int) -> Dict:
        """Get evidence schema for workflow/phase. Internal use only."""
        
    def is_schema_exposed(self) -> bool:
        """Always returns False. Schemas are NEVER exposed to AI."""
```

**Dependencies:**
- Requires: Workflow YAML files (with evidence schemas defined)
- Provides: Schemas for EvidenceValidator (internal only)

**Error Handling:**
- Schema not found → Return error "No schema defined for workflow {type} phase {N}"
- Schema malformed → Log error, use empty schema (accept all evidence)

---

#### Component: StateManager

**Purpose:** Persist workflow state to disk, enable resume after restart.

**Responsibilities:**
- Persist state to `.praxis-os/workflow_states/{session_id}.json`
- Load state on server restart
- Resume workflow from last completed phase
- Cleanup completed workflows (archive or delete after 30 days)

**Requirements Satisfied:**
- FR-020: Workflow State Persistence

**Public Interface:**
```python
class StateManager:
    def __init__(self, state_dir: Path):
        """Initialize with state directory."""
        
    def save_state(self, session_id: str, state: WorkflowState) -> None:
        """Persist state to disk."""
        
    def load_state(self, session_id: str) -> Optional[WorkflowState]:
        """Load state from disk. Returns None if not found."""
        
    def list_sessions(self, status: Optional[str] = None) -> List[Dict]:
        """List all workflow sessions, optionally filter by status."""
        
    def cleanup_completed(self, older_than_days: int = 30) -> int:
        """Cleanup completed sessions. Returns count deleted."""
```

**Dependencies:**
- Requires: Filesystem access
- Provides: State persistence for PhaseGates, pos_workflow

**Error Handling:**
- State write fails → Log error, return error to AI agent
- State read fails (corrupted JSON) → Log error, suggest session restart
- State dir full (>1GB) → Run cleanup, log warning

---

### 2.5 BROWSER SUBSYSTEM

#### Component: BrowserManager

**Purpose:** Isolated Playwright sessions per AI agent, browser automation.

**Responsibilities:**
- Maintain isolated Playwright sessions (keyed by `session_id`)
- Create browser context on first action
- Execute browser actions (navigate, screenshot, click, type, fill, select, wait, evaluate)
- Cleanup sessions (explicit close or 30 min idle timeout)
- Support multiple browser types (chromium, firefox, webkit)

**Requirements Satisfied:**
- FR-021: Isolated Playwright Sessions
- FR-022: Browser Actions

**Public Interface:**
```python
class BrowserManager:
    def __init__(self, config: BrowserConfig, max_sessions: int = 10):
        """Initialize with config and max concurrent sessions."""
        
    async def get_session(self, session_id: str) -> PlaywrightSession:
        """Get or create browser session."""
        
    async def navigate(self, session_id: str, url: str, wait_until: str = "load") -> Dict:
        """Navigate to URL."""
        
    async def screenshot(
        self, 
        session_id: str, 
        path: str, 
        full_page: bool = False
    ) -> Dict:
        """Capture screenshot."""
        
    async def click(self, session_id: str, selector: str, **kwargs) -> Dict:
        """Click element."""
        
    async def close_session(self, session_id: str) -> None:
        """Close session and cleanup."""
```

**Dependencies:**
- Requires: Playwright (async API), `.praxis-os/workspace/scratch/` (for screenshots)
- Provides: Browser automation for pos_browser

**Error Handling:**
- Session limit exceeded → Return error "Max sessions reached: {max}"
- Navigation timeout → Return error with URL, timeout value
- Selector not found → Return error with selector, page URL, suggestions
- Session timeout (30 min idle) → Auto-close, log cleanup
- Browser crash → Close session, log error, suggest restart

---

### 2.6 FOUNDATION LAYER

#### Component: Config (Pydantic v2)

**Purpose:** Type-safe configuration with fail-fast validation at startup.

**Responsibilities:**
- Load config from `config/mcp.yaml`
- Parse into Pydantic models (MCPConfig, IndexesConfig, WorkflowConfig, BrowserConfig)
- Validate on load (fail-fast at startup)
- Provide type-safe access (no `dict["key"]` in codebase)
- Generate clear validation errors with auto-fix suggestions

**Requirements Satisfied:**
- FR-023: Pydantic v2 Schema Validation
- FR-024: Config-Driven Language Support
- FR-025: Fail-Fast Validation

**Public Interface:**
```python
class MCPConfig(BaseConfig):
    version: str = Field(pattern=r"^\d+\.\d+$")
    indexes: IndexesConfig
    workflow: WorkflowConfig
    browser: BrowserConfig
    logging: LoggingConfig
    
    @classmethod
    def from_yaml(cls, path: Path) -> "MCPConfig":
        """Load and validate config from YAML. Raises ValidationError on failure."""
        
    def validate_paths(self) -> List[str]:
        """Validate all paths exist. Returns list of errors."""

class IndexesConfig(BaseConfig):
    standards: StandardsConfig
    code: CodeConfig
    ast: ASTConfig

class StandardsConfig(BaseConfig):
    source_paths: List[str]
    vector: VectorConfig
    fts: FTSConfig
    reranking: Optional[RerankingConfig] = None
```

**Dependencies:**
- Requires: Pydantic v2, PyYAML
- Provides: Type-safe config for all subsystems

**Error Handling:**
- YAML parse fails → Return error "Invalid YAML: {parse_error}"
- Validation fails → Return error with field path (e.g., "indexes → standards → vector → chunk_size: must be >= 100")
- Path validation fails → Return error with missing path, auto-fix suggestion
- Config file not found → Return error "Config file not found: {path}"

---

#### Component: Logging

**Purpose:** Structured JSON logging, behavioral metrics, queryable logs.

**Responsibilities:**
- Configure Python logging with JSON formatter
- Create subsystem-specific logs (index_manager.log, query_tracker.log, workflow.log)
- Include behavioral metrics in logs
- Ensure logs queryable via `jq`
- Log rotation (when >1GB)

**Requirements Satisfied:**
- NFR-O1: Structured Logging
- NFR-O2: Behavioral Metrics Collection

**Public Interface:**
```python
class StructuredLogger:
    def __init__(self, name: str, log_dir: Path):
        """Initialize logger with name and log directory."""
        
    def info(self, message: str, **extra) -> None:
        """Log info message with structured data."""
        
    def error(self, message: str, exc_info: bool = False, **extra) -> None:
        """Log error message with structured data."""
        
    def behavioral(self, event: str, metrics: Dict) -> None:
        """Log behavioral event (query, drift, etc.)."""
```

**Dependencies:**
- Requires: Python `logging`, JSON formatter
- Provides: Structured logs for all components

**Error Handling:**
- Log write fails → Write to stderr, continue
- Log dir full → Rotate logs, archive old logs
- Formatter fails → Fall back to plaintext logging

---

#### Component: Errors

**Purpose:** Clear error messages with auto-fix suggestions.

**Responsibilities:**
- Provide error classes with structured fields (what, why, how_to_fix)
- Generate auto-fix suggestions (command to run, config to change)
- Include field paths (e.g., "indexes → vector → chunk_size")
- Make errors actionable for AI agents

**Requirements Satisfied:**
- NFR-U1: Error Message Clarity

**Public Interface:**
```python
class ActionableError(Exception):
    def __init__(
        self, 
        what_failed: str, 
        why_failed: str, 
        how_to_fix: str,
        field_path: Optional[str] = None
    ):
        """Create actionable error with structured fields."""
        
    def to_dict(self) -> Dict[str, str]:
        """Serialize to dict for JSON return."""
        
    def __str__(self) -> str:
        """Format as human-readable message."""

class ConfigValidationError(ActionableError):
    """Config validation errors with auto-fix suggestions."""

class EvidenceValidationError(ActionableError):
    """Evidence validation errors with remediation."""
```

**Dependencies:**
- Requires: Python base Exception
- Provides: Actionable errors for all components

**Error Handling:**
- Error formatting fails → Return generic error message
- Auto-fix generation fails → Return error without suggestion

---

### 2.7 Component Interactions

**High-Level Interaction Flow:**

```
AI Agent
   ↓ (calls tool)
Tools Layer (pos_search_project, pos_workflow, etc.)
   ↓ (flows through)
Middleware Layer (query_tracker, prepend_generator, query_classifier)
   ↓ (routes to)
Subsystems Layer (RAG, Workflow, Browser)
   ↓ (uses)
Foundation Layer (Config, Logging, Errors)
```

**Detailed Interaction: Search Flow**

| From | To | Method | Purpose |
|------|-----|--------|---------|
| AI Agent | pos_search_project | `pos_search_project(action="search_standards", query="...")` | Initiate search |
| pos_search_project | query_tracker | `log_query(query_record)` | Log query for behavioral analysis |
| pos_search_project | IndexManager | `route_action(action, query, **kwargs)` | Route to correct index |
| IndexManager | StandardsIndex | `search(query, method="hybrid", n_results=5)` | Execute hybrid search |
| StandardsIndex | LanceDB | `table.search(query).limit(n_results).to_list()` | Vector + FTS search |
| StandardsIndex | IndexManager | `return results` | Return ranked results |
| IndexManager | pos_search_project | `return results` | Return to tool |
| pos_search_project | prepend_generator | `generate(query_record)` | Generate gamification prepend |
| prepend_generator | query_tracker | `get_session_stats(session_id)` | Get diversity metrics |
| prepend_generator | pos_search_project | `return prepend` | Return formatted prepend |
| pos_search_project | AI Agent | `return {prepend, results}` | Return prepend + results |

**Detailed Interaction: Incremental Index Update**

| From | To | Method | Purpose |
|------|-----|--------|---------|
| File System | FileWatcher | `on_modified(event)` | File changed notification |
| FileWatcher | IndexManager | `update_index(index_name, file_path, event_type)` | Route update request |
| IndexManager | StandardsIndex | `update(file_path, event_type)` | Incremental update |
| StandardsIndex | LanceDB | `table.add([new_chunk])` | Add new chunk |
| StandardsIndex | LanceDB | `table.create_fts_index("content", replace=True)` | Rebuild FTS index |
| StandardsIndex | LanceDB | `table.optimize()` | Rebuild scalar indexes |
| StandardsIndex | IndexManager | `return update_status` | Confirm update complete |
| IndexManager | FileWatcher | `return update_status` | Confirm to watcher |

---

### 2.8 Module Organization

**Directory Structure:**

```
.praxis-os/ouroboros/
├── __main__.py              # Entry point (server startup)
├── server.py                # FastMCP server initialization
├── config/                  # Foundation Layer
│   ├── __init__.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py          # BaseConfig, enums
│   │   ├── indexes.py       # IndexesConfig
│   │   ├── workflow.py      # WorkflowConfig
│   │   ├── browser.py       # BrowserConfig
│   │   └── mcp.py           # MCPConfig (root)
│   └── loader.py            # Config loading logic
├── tools/                   # Tools Layer (auto-discovered)
│   ├── __init__.py
│   ├── pos_search_project.py
│   ├── pos_workflow.py
│   ├── pos_browser.py
│   ├── pos_filesystem.py
│   └── get_server_info.py
├── registry/                # Tools Layer
│   ├── __init__.py
│   └── loader.py            # ToolRegistry
├── middleware/              # Middleware Layer
│   ├── __init__.py
│   ├── prepend_generator.py
│   ├── query_tracker.py
│   └── query_classifier.py
├── subsystems/              # Subsystems Layer
│   ├── __init__.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── index_manager.py
│   │   ├── standards_index.py
│   │   ├── code_index.py
│   │   ├── ast_index.py
│   │   └── watcher.py       # FileWatcher
│   ├── workflow/
│   │   ├── __init__.py
│   │   ├── engine.py        # PhaseGates
│   │   ├── validator.py     # EvidenceValidator
│   │   ├── schemas.py       # HiddenSchemas
│   │   └── state_manager.py
│   └── browser/
│       ├── __init__.py
│       └── manager.py       # BrowserManager
└── utils/                   # Foundation Layer
    ├── __init__.py
    ├── logging.py           # StructuredLogger
    ├── errors.py            # ActionableError
    └── metrics.py           # Performance metrics
```

**Dependency Rules:**

1. **One-Way Dependencies (Enforced):**
   - Tools → Middleware → Subsystems → Foundation
   - NEVER: Subsystems → Tools, RAG → Workflow

2. **No Circular Imports:**
   - Validated by `importlab --tree ouroboros/`
   - CI/CD gate: Fails build if circular dependencies detected

3. **Dependency Injection:**
   - Subsystems receive Pydantic config objects (not dicts)
   - Tools receive subsystem instances via registry
   - Middleware receives subsystem instances at initialization

4. **Import Conventions:**
   - Absolute imports from `ouroboros.` root
   - No relative imports across layers
   - Example: `from ouroboros.subsystems.rag import IndexManager`

---

**Component Count Summary:**
- Tools Layer: 6 components (5 tools + ToolRegistry)
- Middleware Layer: 3 components (prepend_generator, query_tracker, query_classifier)
- RAG Subsystem: 5 components (IndexManager, StandardsIndex, CodeIndex, ASTIndex, FileWatcher)
- Workflow Subsystem: 4 components (PhaseGates, EvidenceValidator, HiddenSchemas, StateManager)
- Browser Subsystem: 1 component (BrowserManager)
- Foundation Layer: 3 components (Config, Logging, Errors)

**Total: 22 components** across 4 layers

---

## 3. API Specifications

This section defines the interfaces and contracts exposed by Ouroboros components. Since this is an MCP server, there are no HTTP REST APIs. Instead, this section focuses on:
1. **MCP Tool Schemas** (exposed to AI agents via FastMCP)
2. **Internal Python Interfaces** (between components)
3. **Data Transfer Objects** (DTOs and Pydantic models)
4. **Error Response Format** (standardized error handling)

---

### 3.1 MCP Tool Schemas

These are the tools exposed to AI agents via the Model Context Protocol (MCP). FastMCP automatically generates JSON schemas from Python type hints and `Literal` enums.

#### Tool: pos_search_project

**Purpose:** Unified search across content types with multi-action support

**MCP Schema:**
```json
{
  "name": "pos_search_project",
  "description": "Unified project search with action-based interface: search standards/code/AST, traverse call graphs.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": [
          "search_standards",
          "search_code",
          "search_ast",
          "find_callers",
          "find_dependencies",
          "find_paths"
        ],
        "description": "Operation to perform:\n- search_standards: Hybrid search standards docs\n- search_code: Semantic code search (LanceDB)\n- search_ast: Structural AST search (Tree-sitter)\n- find_callers: Graph traversal - who calls this symbol?\n- find_dependencies: Graph traversal - what does this symbol call?\n- find_paths: Graph traversal - show call chain from A to B"
      },
      "query": {
        "type": "string",
        "description": "Search query (natural language, symbol name, or pattern)"
      },
      "method": {
        "type": "string",
        "enum": ["hybrid", "vector", "fts"],
        "default": "hybrid",
        "description": "Search method (for search_* actions only)"
      },
      "n_results": {
        "type": "integer",
        "default": 5,
        "minimum": 1,
        "maximum": 50,
        "description": "Number of results to return"
      },
      "max_depth": {
        "type": "integer",
        "default": 10,
        "minimum": 1,
        "maximum": 100,
        "description": "Max depth for graph traversal (for find_* actions)"
      },
      "to_symbol": {
        "type": "string",
        "description": "Target symbol for find_paths action (required for find_paths)"
      }
    },
    "required": ["action", "query"]
  }
}
```

**Response Format:**
```json
{
  "prepend": "💡 Queries: 3/5 | Angles: 📖✓ 🔧⬜ | Try: 'where is X used?'",
  "results": [
    {
      "content": "...",
      "metadata": {
        "file_path": "...",
        "score": 0.95,
        "method": "hybrid"
      }
    }
  ],
  "metadata": {
    "query": "...",
    "action": "search_standards",
    "method": "hybrid",
    "total_results": 5
  }
}
```

---

#### Tool: pos_workflow

**Purpose:** Workflow lifecycle management with phase-gated execution

**MCP Schema:**
```json
{
  "name": "pos_workflow",
  "description": "Unified workflow execution tool with phase-gated validation and hidden evidence schemas (adversarial design).",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["start", "get_phase", "get_task", "complete_phase", "list_sessions", "get_session", "pause", "resume", "delete_session"],
        "description": "Workflow operation to perform"
      },
      "session_id": {
        "type": "string",
        "format": "uuid",
        "description": "Workflow session identifier (required for most actions)"
      },
      "workflow_type": {
        "type": "string",
        "description": "Workflow type identifier (required for 'start')"
      },
      "target_file": {
        "type": "string",
        "description": "Target file path (optional for 'start')"
      },
      "phase": {
        "type": "integer",
        "minimum": 0,
        "description": "Phase number (for get_phase, complete_phase)"
      },
      "task_number": {
        "type": "integer",
        "minimum": 1,
        "description": "Task number (for get_task)"
      },
      "evidence": {
        "type": "object",
        "description": "Evidence dictionary for phase completion (schema hidden until submission)"
      }
    },
    "required": ["action"]
  }
}
```

**Response Format (start):**
```json
{
  "session_id": "uuid",
  "workflow_type": "spec_creation_v1",
  "status": "active",
  "overview": {
    "phases": 5,
    "total_tasks": 23,
    "estimated_duration": "2-3 hours"
  },
  "next_phase": {
    "phase": 0,
    "name": "Supporting Documents Integration",
    "tasks": 5
  }
}
```

**Response Format (complete_phase - validation error):**
```json
{
  "status": "error",
  "action": "complete_phase",
  "validation_result": {
    "valid": false,
    "errors": [
      {
        "field": "spec_directory_created",
        "error": "Missing required field",
        "type": "boolean",
        "suggestion": "Provide boolean value indicating if spec directory exists"
      }
    ]
  }
}
```

---

#### Tool: pos_browser

**Purpose:** Browser automation with isolated Playwright sessions

**MCP Schema:**
```json
{
  "name": "pos_browser",
  "description": "Browser automation tool with Playwright, supporting isolated sessions per AI agent.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["navigate", "screenshot", "click", "type", "fill", "select", "wait", "evaluate", "close"],
        "description": "Browser operation to perform"
      },
      "session_id": {
        "type": "string",
        "description": "Browser session identifier (auto-created if not provided)"
      },
      "url": {
        "type": "string",
        "format": "uri",
        "description": "Target URL (for 'navigate' action)"
      },
      "selector": {
        "type": "string",
        "description": "CSS selector (for actions targeting elements)"
      },
      "text": {
        "type": "string",
        "description": "Text to type (for 'type' action)"
      },
      "value": {
        "type": "string",
        "description": "Value to fill or select (for 'fill' or 'select' actions)"
      },
      "screenshot_path": {
        "type": "string",
        "description": "File path to save screenshot (for 'screenshot' action)"
      }
    },
    "required": ["action"]
  }
}
```

**Response Format:**
```json
{
  "status": "success",
  "action": "navigate",
  "session_id": "test-session-1",
  "result": {
    "url": "http://localhost:3000",
    "title": "App Title",
    "load_time_ms": 123
  }
}
```

---

#### Tool: pos_filesystem

**Purpose:** File operations with safe defaults and gitignore respect

**MCP Schema:**
```json
{
  "name": "pos_filesystem",
  "description": "Unified file operations tool supporting read, write, delete, list, move, copy with safe defaults.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["read", "write", "delete", "list", "move", "copy", "exists", "mkdir", "rmdir"],
        "description": "File operation to perform"
      },
      "path": {
        "type": "string",
        "description": "File or directory path"
      },
      "content": {
        "type": "string",
        "description": "File content (for 'write' action)"
      },
      "destination": {
        "type": "string",
        "description": "Destination path (for 'move' or 'copy' actions)"
      },
      "recursive": {
        "type": "boolean",
        "default": false,
        "description": "Enable recursive operations (for 'delete', 'list', 'copy')"
      },
      "follow_symlinks": {
        "type": "boolean",
        "default": false,
        "description": "Follow symbolic links"
      },
      "encoding": {
        "type": "string",
        "default": "utf-8",
        "description": "File encoding"
      },
      "create_parents": {
        "type": "boolean",
        "default": false,
        "description": "Create parent directories (for 'write', 'mkdir')"
      }
    },
    "required": ["action", "path"]
  }
}
```

**Response Format:**
```json
{
  "status": "success",
  "action": "read",
  "path": "/path/to/file.py",
  "result": {
    "content": "...",
    "size_bytes": 1234,
    "encoding": "utf-8"
  }
}
```

---

#### Tool: get_server_info

**Purpose:** Server status, health, behavioral metrics, version information

**MCP Schema:**
```json
{
  "name": "get_server_info",
  "description": "Retrieve server status, health checks, behavioral metrics, and version information.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["status", "health", "behavioral_metrics", "version"],
        "default": "status",
        "description": "Type of information to retrieve"
      }
    }
  }
}
```

**Response Format (status):**
```json
{
  "status": "running",
  "uptime_seconds": 3600,
  "config_loaded": true,
  "subsystems": {
    "rag": "initialized",
    "workflow": "initialized",
    "browser": "initialized"
  }
}
```

**Response Format (health):**
```json
{
  "overall_health": "healthy",
  "checks": {
    "standards_index": {
      "status": "healthy",
      "fts_index_exists": true,
      "vector_dimension": 384,
      "document_count": 1234
    },
    "code_index": {
      "status": "healthy",
      "lance_documents": 5678,
      "duckdb_symbols": 9012,
      "duckdb_relationships": 3456
    }
  }
}
```

**Response Format (behavioral_metrics):**
```json
{
  "session_id": "current-session",
  "query_count": 12,
  "query_diversity": 0.75,
  "angles_used": {
    "conceptual": 3,
    "location": 2,
    "implementation": 5,
    "critical": 1,
    "troubleshooting": 1
  },
  "session_comparison": {
    "previous_session_query_count": 8,
    "trend": "improving"
  }
}
```

---

### 3.2 Internal Python Interfaces

These interfaces define contracts between internal components. All interfaces use abstract base classes (ABCs) for enforcement.

#### Interface: BaseIndex

**Purpose:** Contract for all index implementations (StandardsIndex, CodeIndex, ASTIndex)

**Python Definition:**
```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class HealthStatus:
    """Health check result for an index."""
    healthy: bool
    component: str
    checks: Dict[str, bool]
    errors: List[str]
    warnings: List[str]

class BaseIndex(ABC):
    """Base interface for all index implementations."""
    
    @abstractmethod
    def build(self, source_paths: List[Path], **kwargs) -> None:
        """Build index from source paths.
        
        Args:
            source_paths: List of directories or files to index
            **kwargs: Index-specific options (e.g., use_incremental, languages)
        
        Raises:
            IndexBuildError: If build fails
        """
        pass
    
    @abstractmethod
    def search(
        self, 
        query: str, 
        method: str = "hybrid",
        n_results: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Execute search query.
        
        Args:
            query: Search query string
            method: Search method ("hybrid", "vector", "fts")
            n_results: Number of results to return
            **kwargs: Search-specific options
        
        Returns:
            List of search results with content, metadata, scores
        
        Raises:
            SearchError: If search fails
        """
        pass
    
    @abstractmethod
    def health_check(self) -> HealthStatus:
        """Check index health.
        
        Returns:
            HealthStatus object with detailed check results
        """
        pass
    
    @abstractmethod
    def update(self, file_path: Path, event_type: str) -> None:
        """Incremental update for single file.
        
        Args:
            file_path: Path to changed file
            event_type: "created", "modified", or "deleted"
        
        Raises:
            IndexUpdateError: If update fails
        """
        pass
```

---

#### Interface: Middleware Hook

**Purpose:** Contract for middleware components (prepend_generator, query_tracker, query_classifier)

**Python Definition:**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class QueryRecord:
    """Record of a single query for middleware processing."""
    session_id: str
    query: str
    action: str  # e.g., "search_standards", "find_callers"
    method: str
    timestamp: str
    angle: Optional[str] = None

class MiddlewareHook(ABC):
    """Base interface for middleware components."""
    
    @abstractmethod
    def process_request(self, query_record: QueryRecord) -> Dict[str, Any]:
        """Process request before executing.
        
        Args:
            query_record: Query metadata
        
        Returns:
            Enriched query record or modifications
        """
        pass
    
    @abstractmethod
    def process_response(
        self, 
        query_record: QueryRecord, 
        results: List[Dict]
    ) -> Dict[str, Any]:
        """Process response before returning to AI agent.
        
        Args:
            query_record: Query metadata
            results: Search results
        
        Returns:
            Enriched results with prepends, metadata
        """
        pass
```

---

#### Interface: WorkflowEngine

**Purpose:** Contract for workflow execution subsystem

**Python Definition:**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class WorkflowState:
    """Current state of a workflow session."""
    session_id: str
    workflow_type: str
    current_phase: int
    completed_phases: List[int]
    evidence_history: Dict[int, Dict[str, Any]]
    status: str  # "active", "completed", "error", "paused"
    created_at: float
    updated_at: float

@dataclass
class ValidationResult:
    """Result of evidence validation."""
    valid: bool
    errors: List[Dict[str, str]]
    warnings: List[Dict[str, str]]

class WorkflowEngine(ABC):
    """Base interface for workflow execution."""
    
    @abstractmethod
    def start_workflow(
        self, 
        workflow_type: str, 
        target_file: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Start new workflow session.
        
        Returns:
            Session info with session_id, overview
        """
        pass
    
    @abstractmethod
    def get_phase(self, session_id: str, phase: int) -> Dict[str, Any]:
        """Get phase content and guidance.
        
        Returns:
            Phase metadata, tasks, guidance
        """
        pass
    
    @abstractmethod
    def complete_phase(
        self, 
        session_id: str, 
        phase: int, 
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Complete phase with evidence submission.
        
        Returns:
            Validation result and next phase info
        
        Raises:
            ValidationError: If evidence invalid
        """
        pass
    
    @abstractmethod
    def validate_evidence(
        self, 
        workflow_type: str, 
        phase: int, 
        evidence: Dict[str, Any]
    ) -> ValidationResult:
        """Validate evidence against hidden schema.
        
        Returns:
            ValidationResult with detailed errors
        """
        pass
```

---

### 3.3 Data Transfer Objects (DTOs)

DTOs are implemented as Pydantic v2 models for automatic validation, type coercion, and JSON schema generation.

#### DTO: QueryRecord

**Purpose:** Metadata for a single search query

**Pydantic Definition:**
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class QueryRecord(BaseModel):
    """Record of a single search query."""
    session_id: str = Field(..., description="AI agent session identifier")
    query: str = Field(..., min_length=1, description="Search query text")
    action: str = Field(..., pattern="^(search_standards|search_code|search_ast|find_callers|find_dependencies|find_paths)$")
    method: str = Field(default="hybrid", pattern="^(hybrid|vector|fts)$")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    angle: Optional[str] = Field(None, description="Detected query angle")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "query": "how to implement X",
                "action": "search_standards",
                "method": "hybrid",
                "angle": "implementation"
            }
        }
```

---

#### DTO: SearchResult

**Purpose:** Single search result with content and metadata

**Pydantic Definition:**
```python
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class SearchResult(BaseModel):
    """Single search result from index."""
    content: str = Field(..., description="Result content (chunk text)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Result metadata (file_path, score, etc.)"
    )
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    method: str = Field(..., description="Search method used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "## How to Implement X\n\n...",
                "metadata": {
                    "file_path": "standards/dev/x-implementation.md",
                    "framework_type": "development",
                    "phase": 1
                },
                "score": 0.95,
                "method": "hybrid"
            }
        }
```

---

#### DTO: ToolResponse

**Purpose:** Standardized response format for all MCP tools

**Pydantic Definition:**
```python
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, List

class ToolResponse(BaseModel):
    """Standardized response for all MCP tools."""
    status: str = Field(..., pattern="^(success|error)$")
    action: str = Field(..., description="Action that was executed")
    result: Optional[Dict[str, Any]] = Field(None, description="Action result")
    prepend: Optional[str] = Field(None, description="Query gamification prepend")
    error: Optional[str] = Field(None, description="Error message if status=error")
    error_type: Optional[str] = Field(None, description="Error class name")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "action": "search",
                "result": {
                    "results": [...],
                    "total": 5
                },
                "prepend": "💡 Queries: 3/5 | Try: 'where is X?'",
                "metadata": {
                    "query": "how to X",
                    "action": "search_standards",
                    "execution_time_ms": 45
                }
            }
        }
```

---

### 3.4 Error Response Format

All errors follow a standardized format for consistent handling by AI agents.

#### Error Response Structure

**JSON Schema:**
```json
{
  "status": "error",
  "action": "string (action that failed)",
  "error": "string (human-readable error message)",
  "error_type": "string (Python exception class name)",
  "what_failed": "string (what operation failed)",
  "why_failed": "string (root cause)",
  "how_to_fix": "string (actionable remediation steps)",
  "field_path": "string (optional - config field path like 'indexes → vector → chunk_size')",
  "metadata": {
    "timestamp": "ISO 8601",
    "session_id": "string (if applicable)"
  }
}
```

**Example: Config Validation Error**
```json
{
  "status": "error",
  "action": "server_startup",
  "error": "Config validation failed",
  "error_type": "ConfigValidationError",
  "what_failed": "Loading config from config/mcp.yaml",
  "why_failed": "indexes → standards → vector → chunk_size: must be >= 100 (got 50)",
  "how_to_fix": "Update config/mcp.yaml:\n\nindexes:\n  standards:\n    vector:\n      chunk_size: 800  # Must be >= 100",
  "field_path": "indexes → standards → vector → chunk_size",
  "metadata": {
    "timestamp": "2025-11-04T10:30:00Z",
    "config_path": "config/mcp.yaml"
  }
}
```

**Example: Evidence Validation Error**
```json
{
  "status": "error",
  "action": "complete_phase",
  "error": "Evidence validation failed",
  "error_type": "EvidenceValidationError",
  "what_failed": "Phase 1 completion",
  "why_failed": "Required field 'spec_directory_created' missing",
  "how_to_fix": "Provide evidence with boolean field:\n\nevidence = {\n  'spec_directory_created': True,\n  'supporting_docs_directory_exists': True,\n  ...\n}",
  "field_path": "spec_directory_created",
  "metadata": {
    "timestamp": "2025-11-04T10:35:00Z",
    "session_id": "uuid",
    "phase": 1,
    "validation_errors": [
      {
        "field": "spec_directory_created",
        "error": "Missing required field",
        "type": "boolean"
      }
    ]
  }
}
```

**Example: Search Error**
```json
{
  "status": "error",
  "action": "search",
  "error": "Index unavailable",
  "error_type": "IndexUnavailableError",
  "what_failed": "Searching standards index",
  "why_failed": "FTS index corrupted (empty posting list panic)",
  "how_to_fix": "Index auto-repair attempted but failed. Manual rebuild required:\n\nRestart MCP server to trigger full index rebuild, or check logs at .praxis-os/logs/index_manager.log",
  "field_path": null,
  "metadata": {
    "timestamp": "2025-11-04T10:40:00Z",
    "session_id": "abc123",
    "action": "search_standards",
    "query": "how to X",
    "auto_repair_attempted": true,
    "auto_repair_result": "failed"
  }
}
```

---

### 3.5 API Integration Points

This section documents how external systems integrate with Ouroboros.

#### MCP Client Integration

**Connection:** Cursor IDE connects to Ouroboros via stdio transport (MCP protocol)

**Discovery:** Client calls `tools/list` to discover available tools and their schemas

**Invocation:** Client calls tools via JSON-RPC messages:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "pos_search_project",
    "arguments": {
      "action": "search_standards",
      "query": "how to implement X",
      "method": "hybrid"
    }
  }
}
```

**Response:** Server returns tool result:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"status\": \"success\", \"prepend\": \"...\", \"results\": [...]}"
      }
    ]
  }
}
```

---

#### File System Integration

**Config Loading:** Server reads `config/mcp.yaml` on startup

**Index Storage:** 
- LanceDB: `.praxis-os/.cache/vector_index/{standards|code|ast}/`
- DuckDB: `.praxis-os/code.duckdb`

**Logs:** `.praxis-os/logs/{index_manager|query_tracker|workflow|browser}.log`

**Workflow State:** `.praxis-os/workflow_states/{session_id}.json`

**Standards Content:** `.praxis-os/standards/` (source for StandardsIndex)

---

### 3.6 API Versioning Strategy

**MCP Tool Versioning:** Not supported (MCP protocol limitation)

**Mitigation:** Use config versioning and fail-fast validation:

```yaml
# config/mcp.yaml
version: "1.0"  # Config schema version
```

**Breaking Changes:** 
- Increment major version (1.0 → 2.0)
- Fail-fast on load if config version < required version
- Provide clear migration error with steps

**Non-Breaking Changes:**
- Add new optional parameters (with defaults)
- Add new tool actions (existing actions unchanged)
- Extend error metadata (existing fields unchanged)

---

**API Summary:**
- MCP Tools: 5 tools (pos_search_project, pos_workflow, pos_browser, pos_filesystem, get_server_info)
- Internal Interfaces: 4 interfaces (BaseIndex, MiddlewareHook, WorkflowEngine, and implicit interfaces via ABCs)
- DTOs: 3 primary DTOs (QueryRecord, SearchResult, ToolResponse)
- Error Format: Standardized ActionableError with auto-fix suggestions
- Integration Points: MCP Client (JSON-RPC), File System (config, indexes, logs, state)

---

## 4. Data Models

This section defines all data structures used in Ouroboros, including configuration models (Pydantic v2), storage schemas (LanceDB, DuckDB, JSON), and validation rules.

---

### 4.1 Configuration Models (Pydantic v2)

These are the type-safe configuration models loaded from `config/mcp.yaml` at server startup.

#### Model: MCPConfig (Root)

**Purpose:** Root configuration model, entry point for all config loading

**Pydantic Definition:**
```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from pathlib import Path

class MCPConfig(BaseModel):
    """Root MCP server configuration."""
    version: str = Field(
        ..., 
        pattern=r"^\d+\.\d+$",
        description="Config schema version (e.g., '1.0')"
    )
    indexes: IndexesConfig = Field(..., description="RAG index configuration")
    workflow: WorkflowConfig = Field(..., description="Workflow subsystem config")
    browser: BrowserConfig = Field(..., description="Browser subsystem config")
    logging: LoggingConfig = Field(..., description="Logging configuration")
    base_path: Path = Field(
        default=Path(".praxis-os"),
        description="Base path for all praxis-os files"
    )
    
    @classmethod
    def from_yaml(cls, path: Path) -> "MCPConfig":
        """Load and validate config from YAML file.
        
        Raises:
            ConfigValidationError: If validation fails
            FileNotFoundError: If config file not found
        """
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    @field_validator("version")
    def validate_version_format(cls, v: str) -> str:
        """Ensure version follows semantic versioning."""
        major, minor = v.split(".")
        if not (major.isdigit() and minor.isdigit()):
            raise ValueError("Version must be 'major.minor' format")
        return v
    
    def validate_paths(self) -> list[str]:
        """Validate all configured paths exist.
        
        Returns:
            List of error messages (empty if all valid)
        """
        errors = []
        if not self.base_path.exists():
            errors.append(f"Base path does not exist: {self.base_path}")
        # Additional path validation...
        return errors

class Config:
    validate_assignment = True  # Validate on field assignment
    extra = "forbid"  # Reject unknown fields
```

**Validation Rules:**
- `version`: Must match `^\d+\.\d+$` pattern
- `base_path`: Directory must exist
- All nested configs must pass their own validation
- Unknown fields are rejected (fail-fast)

---

#### Model: IndexesConfig

**Purpose:** Configuration for all RAG indexes

**Pydantic Definition:**
```python
from pydantic import BaseModel, Field
from typing import Dict, Any

class IndexesConfig(BaseModel):
    """Configuration for RAG indexes."""
    standards: StandardsIndexConfig = Field(..., description="Standards index config")
    code: CodeIndexConfig = Field(..., description="Code index config")
    ast: ASTIndexConfig = Field(..., description="AST index config")
    cache_path: Path = Field(
        default=Path(".praxis-os/.cache/vector_index"),
        description="Base cache path for all indexes"
    )
    file_watcher: FileWatcherConfig = Field(..., description="File watcher config")

class StandardsIndexConfig(BaseModel):
    """Configuration for standards index."""
    source_paths: list[str] = Field(
        ..., 
        min_length=1,
        description="Directories to index (relative to base_path)"
    )
    vector: VectorConfig = Field(..., description="Vector search config")
    fts: FTSConfig = Field(..., description="Full-text search config")
    reranking: Optional[RerankingConfig] = Field(None, description="Reranking config")
    
    @field_validator("source_paths")
    def validate_source_paths(cls, v: list[str]) -> list[str]:
        """Ensure at least one source path is provided."""
        if not v:
            raise ValueError("At least one source path required")
        return v

class VectorConfig(BaseModel):
    """Vector search configuration."""
    model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model identifier"
    )
    chunk_size: int = Field(
        default=800, 
        ge=100, 
        le=2000,
        description="Chunk size in tokens"
    )
    chunk_overlap: int = Field(
        default=100, 
        ge=0, 
        le=500,
        description="Overlap between chunks"
    )
    dimension: int = Field(
        default=384, 
        ge=128, 
        le=4096,
        description="Embedding dimension"
    )
    index_type: str = Field(
        default="HNSW",
        pattern="^(HNSW|IVF_PQ|FLAT)$",
        description="Vector index type"
    )
    
    @field_validator("chunk_overlap")
    def validate_overlap_lt_chunk_size(cls, v: int, info) -> int:
        """Ensure overlap is less than chunk size."""
        chunk_size = info.data.get("chunk_size", 800)
        if v >= chunk_size:
            raise ValueError(f"chunk_overlap ({v}) must be < chunk_size ({chunk_size})")
        return v

class FTSConfig(BaseModel):
    """Full-text search configuration."""
    enabled: bool = Field(default=True, description="Enable FTS index")
    use_tantivy: bool = Field(default=False, description="Use Tantivy backend")
    tokenizer: str = Field(
        default="default",
        pattern="^(default|standard|whitespace|simple)$",
        description="FTS tokenizer"
    )

class RerankingConfig(BaseModel):
    """Cross-encoder reranking configuration."""
    enabled: bool = Field(default=False, description="Enable reranking")
    model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="Cross-encoder model"
    )
    top_k: int = Field(
        default=20, 
        ge=5, 
        le=100,
        description="Rerank top K results"
    )

class CodeIndexConfig(BaseModel):
    """Configuration for code index (LanceDB + DuckDB)."""
    source_paths: list[str] = Field(..., description="Code directories to index")
    languages: list[str] = Field(..., description="Languages to index")
    vector: VectorConfig = Field(..., description="Vector config (CodeBERT)")
    fts: FTSConfig = Field(..., description="FTS config")
    duckdb_path: Path = Field(
        default=Path(".praxis-os/code.duckdb"),
        description="DuckDB database path"
    )
    graph: GraphConfig = Field(..., description="Graph traversal config")

class GraphConfig(BaseModel):
    """Graph traversal configuration."""
    max_depth: int = Field(
        default=10, 
        ge=1, 
        le=100,
        description="Max recursion depth for CTEs"
    )
    relationship_types: list[str] = Field(
        default=["calls", "imports", "inherits"],
        description="Relationship types to track"
    )

class ASTIndexConfig(BaseModel):
    """Configuration for AST index."""
    source_paths: list[str] = Field(..., description="Code directories to parse")
    languages: list[str] = Field(..., description="Languages to support")
    auto_install_parsers: bool = Field(
        default=True,
        description="Auto-install missing Tree-sitter parsers"
    )
    venv_path: Path = Field(
        default=Path(".praxis-os/venv"),
        description="Isolated venv for parser installation"
    )

class FileWatcherConfig(BaseModel):
    """File watcher configuration."""
    enabled: bool = Field(default=True, description="Enable file watching")
    debounce_ms: int = Field(
        default=500, 
        ge=100, 
        le=5000,
        description="Debounce delay in milliseconds"
    )
    watch_patterns: list[str] = Field(
        default=["*.md", "*.py", "*.go", "*.rs", "*.ts", "*.tsx"],
        description="File patterns to watch"
    )
```

**Validation Rules:**
- `chunk_size`: 100-2000 tokens
- `chunk_overlap`: 0-500 tokens, must be < chunk_size
- `dimension`: 128-4096 (depends on embedding model)
- `source_paths`: At least one path required
- `languages`: At least one language required
- `max_depth`: 1-100 for graph traversal

---

#### Model: WorkflowConfig

**Purpose:** Configuration for workflow subsystem

**Pydantic Definition:**
```python
class WorkflowConfig(BaseModel):
    """Configuration for workflow subsystem."""
    workflows_dir: Path = Field(
        default=Path(".praxis-os/workflows"),
        description="Directory containing workflow definitions"
    )
    state_dir: Path = Field(
        default=Path(".praxis-os/workflow_states"),
        description="Directory for persisting workflow state"
    )
    session_timeout_minutes: int = Field(
        default=1440,  # 24 hours
        ge=60,
        le=10080,  # 7 days
        description="Session timeout in minutes"
    )
    cleanup_completed_after_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Archive completed workflows after N days"
    )
    evidence_schemas_exposed: bool = Field(
        default=False,
        description="Expose evidence schemas (MUST be False for adversarial design)"
    )
    
    @field_validator("evidence_schemas_exposed")
    def prevent_schema_exposure(cls, v: bool) -> bool:
        """Ensure evidence schemas remain hidden (adversarial design)."""
        if v is True:
            raise ValueError(
                "evidence_schemas_exposed MUST be False. "
                "Exposing schemas violates adversarial design principle. "
                "See standards/development/adversarial-design-for-ai-systems.md"
            )
        return v
```

**Validation Rules:**
- `session_timeout_minutes`: 60 minutes to 7 days
- `cleanup_completed_after_days`: 1-365 days
- `evidence_schemas_exposed`: **MUST be False** (enforced at validation level)

---

#### Model: BrowserConfig

**Purpose:** Configuration for browser subsystem

**Pydantic Definition:**
```python
class BrowserConfig(BaseModel):
    """Configuration for browser subsystem."""
    browser_type: str = Field(
        default="chromium",
        pattern="^(chromium|firefox|webkit)$",
        description="Browser type for Playwright"
    )
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode"
    )
    max_sessions: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Max concurrent browser sessions"
    )
    session_timeout_minutes: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Idle session timeout"
    )
    screenshot_dir: Path = Field(
        default=Path(".praxis-os/workspace/scratch"),
        description="Directory for screenshots"
    )
```

**Validation Rules:**
- `browser_type`: chromium, firefox, or webkit
- `max_sessions`: 1-50 concurrent sessions
- `session_timeout_minutes`: 5-120 minutes

---

#### Model: LoggingConfig

**Purpose:** Configuration for structured logging

**Pydantic Definition:**
```python
class LoggingConfig(BaseModel):
    """Configuration for structured logging."""
    log_dir: Path = Field(
        default=Path(".praxis-os/logs"),
        description="Directory for log files"
    )
    level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Log level"
    )
    format: str = Field(
        default="json",
        pattern="^(json|text)$",
        description="Log format"
    )
    rotation_size_mb: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Rotate logs when size exceeds N MB"
    )
    max_files: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Keep N most recent log files"
    )
    behavioral_metrics_enabled: bool = Field(
        default=True,
        description="Log behavioral metrics (query diversity, trends)"
    )
```

**Validation Rules:**
- `level`: DEBUG, INFO, WARNING, ERROR, or CRITICAL
- `format`: json or text
- `rotation_size_mb`: 10-1000 MB
- `max_files`: 1-100 files

---

### 4.2 Storage Schemas

These schemas define how data is persisted to LanceDB, DuckDB, and JSON files.

#### Schema: LanceDB Standards Index

**Purpose:** Store standards content with vector embeddings, FTS, and metadata

**Table Name:** `standards` (in `.praxis-os/.cache/vector_index/standards/`)

**Schema Definition:**
```python
# LanceDB uses PyArrow schema
import pyarrow as pa

standards_schema = pa.schema([
    pa.field("id", pa.string()),  # Unique chunk ID (UUID)
    pa.field("content", pa.string()),  # Chunk text content
    pa.field("vector", pa.list_(pa.float32(), 384)),  # Embedding (dimension from config)
    pa.field("file_path", pa.string()),  # Source file path
    pa.field("framework_type", pa.string()),  # Framework type (e.g., "development")
    pa.field("phase", pa.int32()),  # Phase number (nullable)
    pa.field("is_critical", pa.bool_()),  # Critical flag
    pa.field("section_header", pa.string()),  # Section header
    pa.field("parent_headers", pa.list_(pa.string())),  # Parent headers hierarchy
    pa.field("tags", pa.list_(pa.string())),  # Tags
    pa.field("chunk_index", pa.int32()),  # Chunk position in document
    pa.field("created_at", pa.timestamp("ms")),  # Index creation timestamp
])
```

**Indexes:**
- **Vector Index:** HNSW on `vector` field (for semantic search)
- **FTS Index:** BM25 on `content` field (for keyword search)
- **Scalar Indexes:**
  - BTREE on `framework_type` (for filtering)
  - BITMAP on `phase` (for filtering)
  - BITMAP on `is_critical` (for filtering)

**Business Rules:**
- `id`: Must be unique (UUID format)
- `vector`: Dimension must match config (`dimension` field)
- `file_path`: Must be relative to `base_path/standards/`
- `framework_type`: One of: universal, development, testing, deployment
- `phase`: Nullable integer (0-N)
- `is_critical`: Boolean flag for critical content

---

#### Schema: LanceDB Code Index

**Purpose:** Store code chunks with embeddings and metadata

**Table Name:** `code` (in `.praxis-os/.cache/vector_index/code/`)

**Schema Definition:**
```python
code_schema = pa.schema([
    pa.field("id", pa.string()),  # Unique chunk ID (UUID)
    pa.field("content", pa.string()),  # Code chunk text
    pa.field("vector", pa.list_(pa.float32(), 768)),  # CodeBERT embedding (768-dim)
    pa.field("file_path", pa.string()),  # Source file path
    pa.field("language", pa.string()),  # Programming language
    pa.field("symbol_type", pa.string()),  # function, class, method, etc.
    pa.field("symbol_name", pa.string()),  # Symbol name (if applicable)
    pa.field("start_line", pa.int32()),  # Start line number
    pa.field("end_line", pa.int32()),  # End line number
    pa.field("chunk_index", pa.int32()),  # Chunk position
    pa.field("created_at", pa.timestamp("ms")),
])
```

**Indexes:**
- **Vector Index:** HNSW on `vector` field (768-dim CodeBERT)
- **FTS Index:** BM25 on `content` field (code-optimized tokenizer)
- **Scalar Indexes:**
  - BTREE on `language`
  - BTREE on `symbol_type`
  - BTREE on `symbol_name`

**Business Rules:**
- `language`: Must be in configured `languages` list
- `symbol_type`: One of: function, class, method, variable, constant, interface, enum
- `vector`: 768-dimensional (CodeBERT/GraphCodeBERT)
- `start_line` < `end_line`

---

#### Schema: DuckDB Code Graph

**Purpose:** Store call graph relationships for graph traversal

**Database:** `.praxis-os/code.duckdb`

**Table: symbols**
```sql
CREATE TABLE symbols (
    id TEXT PRIMARY KEY,          -- Symbol ID (UUID)
    name TEXT NOT NULL,            -- Symbol name (e.g., "calculate_total")
    qualified_name TEXT NOT NULL,  -- Fully qualified name (e.g., "utils.math.calculate_total")
    symbol_type TEXT NOT NULL,     -- function, class, method, etc.
    file_path TEXT NOT NULL,       -- Source file path
    start_line INTEGER NOT NULL,   -- Start line
    end_line INTEGER NOT NULL,     -- End line
    language TEXT NOT NULL,        -- Programming language
    signature TEXT,                -- Function/method signature
    docstring TEXT,                -- Documentation string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_symbols_name ON symbols(name);
CREATE INDEX idx_symbols_qualified_name ON symbols(qualified_name);
CREATE INDEX idx_symbols_type ON symbols(symbol_type);
CREATE INDEX idx_symbols_file ON symbols(file_path);
```

**Table: relationships**
```sql
CREATE TABLE relationships (
    id TEXT PRIMARY KEY,          -- Relationship ID (UUID)
    caller_id TEXT NOT NULL,      -- Symbol ID of caller
    callee_id TEXT NOT NULL,      -- Symbol ID of callee
    relationship_type TEXT NOT NULL,  -- calls, imports, inherits
    call_site_line INTEGER,       -- Line where call occurs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (caller_id) REFERENCES symbols(id) ON DELETE CASCADE,
    FOREIGN KEY (callee_id) REFERENCES symbols(id) ON DELETE CASCADE
);

CREATE INDEX idx_relationships_caller ON relationships(caller_id);
CREATE INDEX idx_relationships_callee ON relationships(callee_id);
CREATE INDEX idx_relationships_type ON relationships(relationship_type);
```

**Business Rules:**
- `qualified_name`: Must be unique per file
- `relationship_type`: One of: calls, imports, inherits
- `caller_id` and `callee_id`: Must reference valid symbols
- Cascade delete: When symbol deleted, relationships also deleted

**Graph Traversal Queries:**

1. **Find Callers (Who calls this symbol?):**
```sql
WITH RECURSIVE callers AS (
    -- Base case: Direct callers
    SELECT r.caller_id, s.name, s.file_path, 1 AS depth
    FROM relationships r
    JOIN symbols s ON r.caller_id = s.id
    WHERE r.callee_id = (SELECT id FROM symbols WHERE name = ?)
      AND r.relationship_type = 'calls'
    
    UNION ALL
    
    -- Recursive case: Transitive callers
    SELECT r.caller_id, s.name, s.file_path, c.depth + 1
    FROM relationships r
    JOIN symbols s ON r.caller_id = s.id
    JOIN callers c ON r.callee_id = c.caller_id
    WHERE c.depth < ? AND r.relationship_type = 'calls'
)
SELECT DISTINCT * FROM callers ORDER BY depth;
```

2. **Find Dependencies (What does this symbol call?):**
```sql
WITH RECURSIVE dependencies AS (
    -- Base case: Direct dependencies
    SELECT r.callee_id, s.name, s.file_path, 1 AS depth
    FROM relationships r
    JOIN symbols s ON r.callee_id = s.id
    WHERE r.caller_id = (SELECT id FROM symbols WHERE name = ?)
      AND r.relationship_type = 'calls'
    
    UNION ALL
    
    -- Recursive case: Transitive dependencies
    SELECT r.callee_id, s.name, s.file_path, d.depth + 1
    FROM relationships r
    JOIN symbols s ON r.callee_id = s.id
    JOIN dependencies d ON r.caller_id = d.callee_id
    WHERE d.depth < ? AND r.relationship_type = 'calls'
)
SELECT DISTINCT * FROM dependencies ORDER BY depth;
```

3. **Find Call Paths (Path from A to B):**
```sql
WITH RECURSIVE call_paths AS (
    -- Base case: Start from symbol A
    SELECT 
        r.caller_id AS start_id,
        r.callee_id AS current_id,
        ARRAY[s1.name, s2.name] AS path,
        1 AS depth
    FROM relationships r
    JOIN symbols s1 ON r.caller_id = s1.id
    JOIN symbols s2 ON r.callee_id = s2.id
    WHERE s1.name = ?  -- Start symbol
      AND r.relationship_type = 'calls'
    
    UNION ALL
    
    -- Recursive case: Extend path
    SELECT 
        cp.start_id,
        r.callee_id AS current_id,
        array_append(cp.path, s.name),
        cp.depth + 1
    FROM call_paths cp
    JOIN relationships r ON r.caller_id = cp.current_id
    JOIN symbols s ON r.callee_id = s.id
    WHERE cp.depth < ?  -- Max depth
      AND r.relationship_type = 'calls'
      AND NOT s.name = ANY(cp.path)  -- Prevent cycles
)
SELECT path FROM call_paths 
WHERE current_id = (SELECT id FROM symbols WHERE name = ?)  -- End symbol
LIMIT 10;
```

---

#### Schema: Workflow State (JSON)

**Purpose:** Persist workflow session state to disk for resume after restart

**File Location:** `.praxis-os/workflow_states/{session_id}.json`

**JSON Schema:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["session_id", "workflow_type", "current_phase", "status", "created_at", "updated_at"],
  "properties": {
    "session_id": {
      "type": "string",
      "format": "uuid",
      "description": "Workflow session identifier"
    },
    "workflow_type": {
      "type": "string",
      "description": "Workflow type (e.g., 'spec_creation_v1')"
    },
    "current_phase": {
      "type": "integer",
      "minimum": 0,
      "description": "Current phase number"
    },
    "completed_phases": {
      "type": "array",
      "items": {"type": "integer"},
      "description": "List of completed phase numbers"
    },
    "evidence_history": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "description": "Evidence submitted for each phase"
      },
      "description": "Map of phase -> evidence dictionary"
    },
    "status": {
      "type": "string",
      "enum": ["active", "completed", "error", "paused"],
      "description": "Workflow session status"
    },
    "target_file": {
      "type": "string",
      "description": "Target file for workflow (optional)"
    },
    "metadata": {
      "type": "object",
      "description": "Additional workflow metadata"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Session creation timestamp (ISO 8601)"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Last update timestamp (ISO 8601)"
    },
    "paused_at": {
      "type": "string",
      "format": "date-time",
      "description": "Pause timestamp (if paused)"
    },
    "pause_reason": {
      "type": "string",
      "description": "Reason for pause (if paused)"
    }
  }
}
```

**Example:**
```json
{
  "session_id": "64eb61c0-dc28-41f1-b5f0-ff328e5b8303",
  "workflow_type": "spec_creation_v1",
  "current_phase": 2,
  "completed_phases": [0, 1],
  "evidence_history": {
    "0": {
      "spec_directory_created": true,
      "supporting_docs_directory_exists": true,
      "documents_processed": true,
      "index_created": true,
      "insights_extracted": true
    },
    "1": {
      "srd_created": true,
      "business_goals_defined": true,
      "user_stories_documented": true,
      "functional_requirements_listed": true
    }
  },
  "status": "active",
  "target_file": null,
  "metadata": {
    "spec_dir": ".praxis-os/specs/review/2025-11-03-ouroboros-mcp-server"
  },
  "created_at": "2025-11-03T17:06:07.401986Z",
  "updated_at": "2025-11-03T17:19:44.853283Z"
}
```

**Business Rules:**
- `session_id`: Must be valid UUID
- `current_phase`: Must be >= 0
- `completed_phases`: Must be sorted, no duplicates
- `status`: Transitions: active → completed/error/paused → active (if resume)
- `updated_at`: Updated on every state change
- File is deleted after `cleanup_completed_after_days` (from config)

---

#### Schema: Query Tracker Log (JSON Lines)

**Purpose:** Log every search query for behavioral analysis

**File Location:** `.praxis-os/logs/query_tracker.log`

**Format:** JSON Lines (one JSON object per line)

**Record Schema:**
```json
{
  "timestamp": "2025-11-04T10:30:00.123Z",
  "session_id": "abc123",
  "query": "how to implement X",
  "action": "search_standards",
  "method": "hybrid",
  "n_results": 5,
  "angle": "implementation",
  "execution_time_ms": 45,
  "result_count": 5,
  "diversity_score": 0.75
}
```

**Business Rules:**
- One record per query
- `timestamp`: ISO 8601 format
- `angle`: One of: conceptual, location, implementation, critical, troubleshooting
- `diversity_score`: 0.0-1.0 (calculated from session history)
- File rotates when > 1GB (from config)

---

### 4.3 Data Model Relationships

**Relationship Diagram:**

```
MCPConfig (Pydantic)
  ├─ IndexesConfig
  │   ├─ StandardsIndexConfig → LanceDB standards table
  │   ├─ CodeIndexConfig → LanceDB code table + DuckDB symbols/relationships
  │   ├─ ASTIndexConfig → (In-memory Tree-sitter ASTs)
  │   └─ FileWatcherConfig → (Monitors file system)
  │
  ├─ WorkflowConfig → JSON state files (.praxis-os/workflow_states/)
  │
  ├─ BrowserConfig → (Playwright sessions in memory)
  │
  └─ LoggingConfig → JSON Lines logs (.praxis-os/logs/)

QueryRecord (Runtime) → query_tracker.log (Persistent)

WorkflowState (Runtime) → {session_id}.json (Persistent)

symbols (DuckDB) ←─ relationships (DuckDB)  [1:N, cascade delete]
```

**Key Relationships:**
1. **Config → Storage:**
   - `IndexesConfig.standards` → LanceDB `standards` table
   - `IndexesConfig.code` → LanceDB `code` table + DuckDB `symbols`/`relationships`
   - `WorkflowConfig` → JSON state files

2. **DuckDB Foreign Keys:**
   - `relationships.caller_id` → `symbols.id` (1:N)
   - `relationships.callee_id` → `symbols.id` (1:N)
   - Cascade delete enabled (symbol deleted → relationships deleted)

3. **Runtime → Persistent:**
   - `QueryRecord` (runtime) → `query_tracker.log` (persistent, append-only)
   - `WorkflowState` (runtime) → `{session_id}.json` (persistent, overwrite)

---

### 4.4 Validation Rules Summary

**Configuration Validation (Pydantic):**
- Fail-fast at startup (invalid config → server won't start)
- Type coercion (strings → Path, timestamps, etc.)
- Range validation (min/max for integers)
- Pattern validation (regex for enums)
- Custom validators (cross-field validation)

**Storage Validation:**
- LanceDB: Schema enforcement via PyArrow
- DuckDB: Foreign key constraints, CHECK constraints
- JSON State: Schema validation on load/save

**Business Rule Validation:**
- `chunk_overlap < chunk_size` (enforced by Pydantic validator)
- `evidence_schemas_exposed = False` (enforced by Pydantic validator with rationale)
- `completed_phases` sorted and unique (enforced by StateManager)
- `start_line < end_line` (enforced by CodeIndex)
- No circular paths in call graph (enforced by recursive CTE with cycle detection)

---

**Data Model Summary:**
- Configuration Models: 9 Pydantic models (MCPConfig, IndexesConfig, StandardsIndexConfig, VectorConfig, FTSConfig, RerankingConfig, CodeIndexConfig, GraphConfig, ASTIndexConfig, WorkflowConfig, BrowserConfig, LoggingConfig)
- Storage Schemas: 5 schemas (LanceDB standards, LanceDB code, DuckDB symbols, DuckDB relationships, JSON state files, JSON Lines logs)
- Relationships: 3 primary relationships (config→storage, DuckDB FK constraints, runtime→persistent)
- Validation Rules: 20+ validation rules enforced at config, storage, and business logic levels

---

## 5. Security Design

This section defines security controls for Ouroboros. Since this is a local MCP server (not a web service), traditional authentication/authorization is not applicable. Instead, this focuses on input validation, path traversal prevention, resource limits, and secure handling of user data.

---

### 5.1 Threat Model

**Deployment Context:**
- Ouroboros runs locally on the user's machine
- Communication via stdio (MCP protocol) with Cursor IDE
- No network exposure (no HTTP/HTTPS endpoints)
- Single-user environment (no multi-tenancy)

**Trust Boundary:**
- **Trusted:** User, Cursor IDE, local filesystem
- **Untrusted:** Tool arguments from AI agent, workflow evidence submissions, browser navigation targets, file paths

**Threat Actors:**
- **Primary:** Malicious or buggy AI agent attempting to:
  - Access files outside allowed directories (path traversal)
  - Execute arbitrary code (code injection)
  - Consume excessive resources (DoS)
  - Extract secrets from config/logs

---

### 5.2 Input Validation

**Principle:** Never trust tool arguments from AI agents. All inputs are validated before execution.

#### 5.2.1 Path Validation

**Threat:** Path traversal attacks (`.../../../etc/passwd`, absolute paths to sensitive files)

**Controls:**
1. **Whitelist Base Paths:**
   ```python
   ALLOWED_BASE_PATHS = [
       Path(".praxis-os/"),
       Path("src/"),
       Path("tests/"),
       Path("docs/"),
   ]
   
   def validate_path(path: str) -> Path:
       """Validate path is within allowed directories.
       
       Raises:
           SecurityError: If path escapes allowed directories
       """
       resolved = Path(path).resolve()
       
       if not any(resolved.is_relative_to(base) for base in ALLOWED_BASE_PATHS):
           raise SecurityError(
               what_failed="Path validation",
               why_failed=f"Path outside allowed directories: {path}",
               how_to_fix="Use paths within: .praxis-os/, src/, tests/, docs/"
           )
       
       return resolved
   ```

2. **Reject Directory Traversal Patterns:**
   - Reject paths containing `..`
   - Reject absolute paths (unless explicitly allowed)
   - Resolve symlinks and validate resolved path

3. **Gitignore Enforcement:**
   - Reject operations on gitignored files (unless override flag set)
   - Prevents accidental exposure of `.env`, secrets files

**Implementation:**
- Applied in: `pos_filesystem`, `pos_workflow`, File Watcher
- Validated before: File reads, writes, deletes, watches

---

#### 5.2.2 Command Injection Prevention

**Threat:** AI agent provides malicious arguments for shell commands or browser JavaScript

**Controls:**
1. **No Shell Execution:**
   - Use Python APIs directly (no `subprocess.run(shell=True)`)
   - Example: Use `pathlib` for file ops, not `os.system("rm -rf")`

2. **Parameterized Queries (DuckDB):**
   ```python
   # SECURE: Parameterized query
   cursor.execute(
       "SELECT * FROM symbols WHERE name = ?",
       [symbol_name]
   )
   
   # INSECURE: String formatting
   cursor.execute(f"SELECT * FROM symbols WHERE name = '{symbol_name}'")
   ```

3. **Safe Browser JS Execution:**
   ```python
   # Playwright's evaluate() safely sandboxes JS
   page.evaluate("() => document.title")  # Safe
   
   # But validate if user-provided JS contains dangerous patterns
   def validate_js_safe(script: str) -> None:
       """Reject scripts with dangerous patterns."""
       dangerous = ["eval(", "Function(", "require(", "import("]
       if any(pattern in script for pattern in dangerous):
           raise SecurityError("Script contains dangerous pattern")
   ```

**Implementation:**
- Applied in: `pos_browser` (evaluate action), `pos_filesystem`, DuckDB queries
- Validated before: Any dynamic code execution

---

#### 5.2.3 Workflow Evidence Validation

**Threat:** AI agent submits malicious evidence payloads (e.g., code injection in artifact paths)

**Controls:**
1. **Pydantic Validation:**
   ```python
   class EvidenceSchema(BaseModel):
       test_artifact_path: Path = Field(..., description="Path to test artifact")
       
       @field_validator("test_artifact_path")
       def validate_artifact_path(cls, v: Path) -> Path:
           """Ensure artifact path is safe."""
           if ".." in str(v):
               raise ValueError("Path traversal detected")
           if not v.suffix in [".xml", ".json", ".txt"]:
               raise ValueError("Invalid artifact type")
           return v
   ```

2. **Artifact Content Validation:**
   - Parse XML/JSON artifacts (don't execute)
   - Reject artifacts with dangerous content (e.g., embedded scripts)

**Implementation:**
- Applied in: `EvidenceValidator` (workflow subsystem)
- Validated before: Phase completion, artifact loading

---

#### 5.2.4 Resource Limits

**Threat:** AI agent causes DoS by requesting excessive resources

**Controls:**
1. **Query Limits:**
   ```python
   MAX_SEARCH_RESULTS = 50  # Cap at 50 results per query
   MAX_GRAPH_DEPTH = 100    # Cap recursion depth for CTEs
   ```

2. **File Size Limits:**
   ```python
   MAX_FILE_SIZE_MB = 10  # Reject files > 10MB for indexing
   MAX_SCREENSHOT_SIZE_MB = 5  # Cap screenshot file size
   ```

3. **Session Limits:**
   ```python
   MAX_BROWSER_SESSIONS = 50  # Cap concurrent browser sessions
   SESSION_TIMEOUT_MINUTES = 30  # Auto-close idle sessions
   ```

4. **Rate Limiting (Optional):**
   - Not implemented initially (single-user, local)
   - Can add if AI agent misbehaves (e.g., query loop)

**Implementation:**
- Applied in: All tools (n_results caps), BrowserManager (session limits), FileWatcher (file size checks)
- Enforced at: Pydantic validation, component initialization

---

### 5.3 Data Protection

#### 5.3.1 Secrets Management

**Threat:** Secrets (API keys for embedding models) exposed in logs or config

**Controls:**
1. **Environment Variables:**
   ```yaml
   # config/mcp.yaml
   indexes:
     standards:
       vector:
         model: "sentence-transformers/all-MiniLM-L6-v2"
         api_key: "${OPENAI_API_KEY}"  # Read from env var
   ```

2. **Log Masking:**
   ```python
   def mask_sensitive_fields(record: dict) -> dict:
       """Mask sensitive fields in log records."""
       sensitive_keys = ["api_key", "password", "token", "secret"]
       for key in sensitive_keys:
           if key in record:
               record[key] = "***REDACTED***"
       return record
   ```

3. **Config File Permissions:**
   - Ensure `config/mcp.yaml` has restrictive permissions (600)
   - Warn if config file is world-readable

**Implementation:**
- Applied in: Config loader, structured logging
- Enforced at: Server startup (config load), log write

---

#### 5.3.2 File System Isolation

**Threat:** AI agent accesses sensitive files outside project

**Controls:**
1. **Chroot-like Isolation:**
   - All file operations relative to project root
   - Absolute paths rejected (unless whitelisted)

2. **Gitignore Enforcement:**
   - Respect `.gitignore` for file operations
   - Prevents leaking `.env`, `.venv`, `.git`

3. **Read-Only Paths:**
   ```python
   READ_ONLY_PATHS = [
       Path(".git/"),  # Git internals read-only
       Path("node_modules/"),  # Dependencies read-only
   ]
   ```

**Implementation:**
- Applied in: `pos_filesystem`, File Watcher
- Enforced at: Path validation layer

---

#### 5.3.3 Query Logs Privacy

**Threat:** Query logs contain sensitive information from user's project

**Controls:**
1. **Local Storage Only:**
   - Logs stored locally (`.praxis-os/logs/`)
   - Never transmitted over network

2. **Log Rotation:**
   - Old logs archived and deleted (max 10 files)
   - Prevents unbounded log growth

3. **PII Scrubbing (Future):**
   - Detect and redact PII in query logs
   - Not implemented in v1.0 (low priority for local-only system)

**Implementation:**
- Applied in: Query tracker, structured logging
- Enforced at: Log write, log rotation

---

### 5.4 Browser Subsystem Security

**Threat:** AI agent uses browser to access malicious sites or exfiltrate data

**Controls:**
1. **Session Isolation:**
   - Each AI agent session gets isolated Playwright context
   - No shared cookies/storage between sessions

2. **Network Restrictions (Optional):**
   - Can configure Playwright to block external domains
   - Not enforced in v1.0 (user trusts their AI agent)

3. **Screenshot Storage:**
   - Screenshots saved to isolated directory (`.praxis-os/workspace/scratch/`)
   - Auto-cleanup after session close

4. **JavaScript Sandboxing:**
   - Playwright's `evaluate()` runs JS in sandboxed context
   - No access to Node.js APIs from browser JS

**Implementation:**
- Applied in: BrowserManager
- Enforced at: Session creation, JS evaluation

---

### 5.5 Workflow Subsystem Security

**Threat:** AI agent bypasses workflow validation or tampers with state

**Controls:**
1. **Hidden Evidence Schemas (Adversarial Design):**
   - Schemas not exposed to AI agent
   - Prevents optimization for validation vs. genuine work
   - Enforced by Pydantic validator:
     ```python
     @field_validator("evidence_schemas_exposed")
     def prevent_schema_exposure(cls, v: bool) -> bool:
         if v is True:
             raise ValueError("Exposing schemas violates adversarial design")
         return v
     ```

2. **State File Integrity:**
   - State files (`.praxis-os/workflow_states/*.json`) have restrictive permissions
   - JSON schema validation on load (reject tampered files)

3. **Phase Gate Enforcement:**
   - Cannot skip phases (enforced by PhaseGates component)
   - Cannot complete phase without valid evidence

**Implementation:**
- Applied in: WorkflowEngine, PhaseGates, EvidenceValidator
- Enforced at: Config load (prevent schema exposure), state load (validate integrity), phase transitions (enforce gates)

---

### 5.6 Index Subsystem Security

**Threat:** Malicious files indexed, corrupting search results

**Controls:**
1. **File Type Whitelist:**
   ```python
   ALLOWED_EXTENSIONS = [".md", ".py", ".go", ".rs", ".ts", ".tsx", ".js", ".jsx"]
   
   def is_indexable(file_path: Path) -> bool:
       """Check if file type is allowed for indexing."""
       return file_path.suffix in ALLOWED_EXTENSIONS
   ```

2. **Content Size Limits:**
   - Skip files > 10MB (prevents indexing binary files accidentally)
   - Log warning for skipped files

3. **Malicious Code Detection (Future):**
   - Scan indexed code for known malicious patterns
   - Not implemented in v1.0 (assumes user's project is trusted)

**Implementation:**
- Applied in: StandardsIndex, CodeIndex, ASTIndex
- Enforced at: File crawling, chunking

---

### 5.7 Dependency Security

**Threat:** Vulnerable dependencies in praxis-os or installed parsers

**Controls:**
1. **Dependency Pinning:**
   ```txt
   # requirements.txt
   lancedb==0.16.0  # Pin exact versions
   duckdb==1.1.3
   sentence-transformers==3.3.1
   ```

2. **Vulnerability Scanning:**
   - Run `pip-audit` in CI/CD
   - Fail build if vulnerabilities found

3. **Isolated Venv for Parsers:**
   - Tree-sitter parsers installed in isolated venv (`.praxis-os/venv/`)
   - Prevents polluting user's project venv

**Implementation:**
- Applied in: Dependency management, ASTIndex (parser installation)
- Enforced at: CI/CD pipeline, runtime (venv isolation)

---

### 5.8 Audit Logging

**Threat:** Unable to trace security incidents or AI agent misbehavior

**Controls:**
1. **Security Event Logging:**
   ```python
   def log_security_event(event_type: str, details: dict) -> None:
       """Log security-relevant events."""
       logger.warning(
           "SECURITY_EVENT",
           extra={
               "event_type": event_type,
               "timestamp": datetime.utcnow().isoformat(),
               "details": details
           }
       )
   ```

2. **Logged Events:**
   - Path validation failures
   - Command injection attempts
   - Resource limit exceeded
   - Invalid evidence submissions
   - Browser navigation to suspicious domains (if implemented)

3. **Log Retention:**
   - Security logs retained for 30 days (config: `cleanup_completed_after_days`)
   - Archived to `.praxis-os/logs/security_archive/`

**Implementation:**
- Applied in: All validation layers, error handlers
- Enforced at: Security exception handlers

---

### 5.9 Security Testing

**Test Coverage:**
1. **Path Traversal Tests:**
   ```python
   def test_path_traversal_blocked():
       with pytest.raises(SecurityError):
           validate_path("../../etc/passwd")
   ```

2. **Command Injection Tests:**
   ```python
   def test_sql_injection_blocked():
       result = index.search(query="'; DROP TABLE symbols; --")
       # Should safely parameterize, not execute DROP
       assert result["status"] == "success"
   ```

3. **Resource Limit Tests:**
   ```python
   def test_excessive_results_capped():
       result = pos_search_project(action="search_standards", query="test", n_results=1000)
       assert len(result["results"]) <= 50  # Capped at MAX_SEARCH_RESULTS
   ```

4. **Evidence Tampering Tests:**
   ```python
   def test_malicious_evidence_rejected():
       evidence = {"test_artifact_path": "../../etc/passwd"}
       result = complete_phase(session_id, phase=1, evidence=evidence)
       assert result["status"] == "error"
       assert "path traversal" in result["error"].lower()
   ```

**Test Execution:**
- Run as part of CI/CD pipeline
- Minimum 80% coverage for security-critical code

---

### 5.10 Security Checklist

**Pre-Release Security Review:**
- [ ] All user inputs validated (paths, queries, evidence)
- [ ] No shell execution with `subprocess.run(shell=True)`
- [ ] Parameterized queries for DuckDB
- [ ] Secrets masked in logs
- [ ] Resource limits enforced (query results, file sizes, sessions)
- [ ] Path traversal tests passing
- [ ] Command injection tests passing
- [ ] Dependency vulnerabilities scanned (`pip-audit`)
- [ ] Config file permissions validated (warn if world-readable)
- [ ] Security event logging implemented

---

**Security Summary:**
- **Threat Model:** Local MCP server, single-user, untrusted AI agent inputs
- **Key Controls:** 10 control categories (input validation, path validation, command injection prevention, resource limits, secrets management, file system isolation, browser isolation, workflow integrity, index security, audit logging)
- **Testing:** 4 test categories (path traversal, command injection, resource limits, evidence tampering)
- **Audit:** Security event logging with 30-day retention
- **Dependencies:** Pinned versions, vulnerability scanning in CI/CD

---

## 6. Performance Design

This section defines performance requirements, optimization strategies, and monitoring for Ouroboros. Performance targets are based on NFRs from Phase 1.

---

### 6.1 Performance Targets

**Server Startup:**
- Cold start: < 30 seconds (load config, initialize indexes, embedding models)
- Warm start (resume existing indexes): < 5 seconds

**Search Latency (p95):**
- Standards search (hybrid): < 200ms
- Code search (hybrid): < 300ms (larger embeddings)
- AST search (structural): < 100ms (no vector search)
- Graph traversal (find_callers): < 500ms for depth=10
- Graph traversal (find_paths): < 1000ms for depth=10

**Index Building:**
- Standards (full rebuild): < 2 minutes for 1000 docs
- Standards (incremental update): < 5 seconds per file
- Code (full rebuild): < 5 minutes for 10k functions
- Code (incremental update): < 10 seconds per file
- AST (full rebuild): < 3 minutes for 10k files

**Memory Usage:**
- Server process (idle): < 500MB RAM
- Embedding model (loaded): < 1GB RAM (sentence-transformers)
- Index cache (LanceDB): < 2GB RAM for 10k documents
- Peak memory: < 4GB RAM (during indexing)

**Throughput:**
- Search queries: 50-100 queries/second (single-threaded)
- File watcher: Process file changes within 5 seconds

---

### 6.2 Caching Strategy

#### 6.2.1 Embedding Model Cache

**Purpose:** Avoid reloading embedding models on every search

**Implementation:**
```python
class EmbeddingCache:
    """Cache embedding models in memory."""
    _cache: Dict[str, SentenceTransformer] = {}
    
    @classmethod
    def get_model(cls, model_name: str) -> SentenceTransformer:
        """Get cached model or load and cache."""
        if model_name not in cls._cache:
            logger.info(f"Loading embedding model: {model_name}")
            cls._cache[model_name] = SentenceTransformer(model_name)
        return cls._cache[model_name]
```

**Benefits:**
- Avoid 2-5 second model load on each search
- Trade-off: 500MB-1GB RAM per model

---

#### 6.2.2 Index Cache (LanceDB)

**Purpose:** Keep indexes in memory for fast access

**Implementation:**
- LanceDB automatically caches index data in memory
- Use memory-mapped files for large indexes (reduce RAM usage)
- Configure LanceDB cache size:
  ```python
  # LanceDB connection config
  db = lancedb.connect(".praxis-os/.cache/vector_index")
  # LanceDB handles caching internally
  ```

**Benefits:**
- Subsequent searches hit memory cache (10-50x faster than disk)
- Trade-off: 1-2GB RAM for cached index data

---

#### 6.2.3 Query Result Cache (Optional)

**Purpose:** Cache frequent query results for AI agents

**Implementation:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def search_cached(action: str, query: str, method: str) -> str:
    """Cache last 100 query results."""
    results = index_manager.route_action(action, query, method=method)
    return json.dumps(results)
```

**Benefits:**
- Instant response for repeated queries (< 1ms)
- Trade-off: 10-50MB RAM for cached results

**Decision:** Not implemented in v1.0 (AI agents rarely repeat exact queries)

---

### 6.3 Search Optimization

#### 6.3.1 Hybrid Search Performance

**Bottlenecks:**
1. **Vector Search:** Embedding generation + HNSW search
2. **FTS Search:** BM25 scoring
3. **RRF Fusion:** Merging results from vector and FTS
4. **Reranking:** Cross-encoder scoring (optional, slow)

**Optimization Strategies:**

1. **Lazy Reranking:**
   ```python
   # Only rerank if enabled in config AND query is complex
   if config.reranking.enabled and len(query.split()) > 3:
       results = reranker.rerank(results)
   ```

2. **Batch Embedding:**
   ```python
   # Generate embeddings in batch (faster than one-by-one)
   embeddings = model.encode([query], batch_size=32)
   ```

3. **Early Termination (HNSW):**
   ```python
   # LanceDB HNSW supports early termination (stop when n_results found)
   table.search(query_vector).limit(n_results)  # Stops early
   ```

4. **Parallel Search (Future):**
   ```python
   # Run vector and FTS search in parallel (not in v1.0)
   with ThreadPoolExecutor() as executor:
       vector_future = executor.submit(vector_search, query)
       fts_future = executor.submit(fts_search, query)
       vector_results = vector_future.result()
       fts_results = fts_future.result()
   ```

**Expected Performance:**
- Vector search: 50-100ms
- FTS search: 30-50ms
- RRF fusion: 5-10ms
- Reranking (if enabled): 200-500ms
- **Total (hybrid without reranking): 100-200ms**
- **Total (hybrid with reranking): 300-700ms**

---

#### 6.3.2 Graph Traversal Optimization

**Bottlenecks:**
1. **Recursive CTE Execution:** Can be slow for deep graphs
2. **Result Sorting:** Sorting large result sets

**Optimization Strategies:**

1. **Limit Max Depth:**
   ```python
   MAX_GRAPH_DEPTH = 10  # Cap at 10 levels
   # Prevents runaway queries
   ```

2. **Index Optimization:**
   ```sql
   -- Ensure indexes on relationship tables
   CREATE INDEX idx_relationships_caller ON relationships(caller_id);
   CREATE INDEX idx_relationships_callee ON relationships(callee_id);
   ```

3. **Result Limiting:**
   ```sql
   -- Limit results at each recursion level
   WITH RECURSIVE callers AS (
       SELECT * FROM relationships WHERE depth < 10
   )
   SELECT * FROM callers LIMIT 100;
   ```

**Expected Performance:**
- Depth 1 (direct callers): 10-20ms
- Depth 5: 50-100ms
- Depth 10: 200-500ms
- Depth 10 with large graph (1000+ nodes): 500-1000ms

---

### 6.4 Indexing Performance

#### 6.4.1 Full Index Rebuild

**Bottlenecks:**
1. **File I/O:** Reading source files
2. **Chunking:** Splitting documents into chunks
3. **Embedding Generation:** Encoding chunks (slowest step)
4. **Index Writing:** Writing to LanceDB/DuckDB

**Optimization Strategies:**

1. **Batch Embedding Generation:**
   ```python
   # Generate embeddings in large batches (32-64 at a time)
   embeddings = model.encode(chunks, batch_size=64, show_progress_bar=True)
   ```

2. **Parallel File Processing:**
   ```python
   # Process files in parallel (use CPU cores)
   from multiprocessing import Pool
   with Pool(processes=cpu_count()) as pool:
       chunks = pool.map(process_file, file_paths)
   ```

3. **Streaming Index Writes:**
   ```python
   # Write to LanceDB in batches (not all at once)
   for batch in chunked(records, 1000):
       table.add(batch)
   ```

**Expected Performance:**
- Standards (1000 docs, 10k chunks): 1-2 minutes
- Code (10k functions, 50k chunks): 3-5 minutes
- AST (10k files): 2-3 minutes (no embeddings)

---

#### 6.4.2 Incremental Index Updates

**Bottlenecks:**
1. **Index Rebuild:** After adding rows, FTS and scalar indexes must be rebuilt
2. **Small Updates:** Overhead of rebuild dominates for single-file updates

**Optimization Strategies:**

1. **Debounce File Watcher:**
   ```python
   # Wait 500ms for multiple changes, then update once
   debouncer.schedule(file_path, delay_ms=500)
   ```

2. **Batch Updates:**
   ```python
   # If multiple files changed, update in batch
   if len(changed_files) > 1:
       table.add(all_new_chunks)
       table.create_fts_index("content", replace=True)  # Rebuild once
   ```

3. **Skip Unnecessary Rebuilds:**
   ```python
   # Only rebuild FTS if content changed (not metadata)
   if change_type == "content":
       rebuild_fts()
   ```

**Expected Performance:**
- Single file update (standards): 3-5 seconds
- Single file update (code): 5-10 seconds
- Batch update (10 files): 15-30 seconds

---

### 6.5 Memory Optimization

#### 6.5.1 Lazy Loading

**Strategy:** Load components only when needed

**Implementation:**
```python
class IndexManager:
    def __init__(self, config: IndexesConfig):
        self.config = config
        self._standards_index = None  # Lazy load
        self._code_index = None
        self._ast_index = None
    
    def get_standards_index(self) -> StandardsIndex:
        """Lazy load standards index."""
        if self._standards_index is None:
            self._standards_index = StandardsIndex(self.config.standards)
        return self._standards_index
```

**Benefits:**
- Reduce startup time (don't load unused indexes)
- Reduce memory (only load what's needed)

---

#### 6.5.2 Streaming Processing

**Strategy:** Process large files in chunks, not all at once

**Implementation:**
```python
def process_large_file(file_path: Path):
    """Process file in streaming fashion."""
    with open(file_path) as f:
        for chunk in read_in_chunks(f, chunk_size=1024*1024):  # 1MB chunks
            process_chunk(chunk)
            # Memory freed after each chunk
```

**Benefits:**
- Avoid loading 100MB+ files into memory all at once
- Enables indexing very large codebases

---

#### 6.5.3 Index Pruning (Future)

**Strategy:** Remove old/unused chunks from indexes

**Implementation (Future):**
```python
# Delete chunks from deleted files
deleted_files = detect_deleted_files()
table.delete(f"file_path IN ({deleted_files})")
```

**Benefits:**
- Reduce index size (faster search, less RAM)

**Decision:** Not implemented in v1.0 (low priority)

---

### 6.6 Concurrency

**Deployment Model:**
- Single-threaded MCP server (stdio transport)
- One AI agent session = one server instance
- No concurrent requests from same AI agent (Cursor sends one request at a time)

**Concurrency Considerations:**

1. **File Watcher Concurrency:**
   - File watcher runs in background thread
   - Uses asyncio or threading for non-blocking file monitoring
   - Debouncing prevents overlapping updates

2. **Browser Sessions:**
   - Multiple browser sessions can exist concurrently
   - Each session isolated (no shared state)
   - Max 10-50 concurrent sessions (config)

3. **Future: Multi-Agent Support (Out of Scope for v1.0):**
   - Would require async request handling
   - Would require connection pooling (DuckDB, LanceDB)
   - Would require thread-safe index access

**Current Performance:**
- Single-threaded (simple, no race conditions)
- 50-100 queries/second sufficient for one AI agent

---

### 6.7 Monitoring & Profiling

#### 6.7.1 Performance Metrics

**Metrics Logged:**
```python
{
  "metric": "search_latency",
  "action": "search_standards",
  "method": "hybrid",
  "latency_ms": 145,
  "timestamp": "2025-11-04T10:30:00Z"
}
```

**Key Metrics:**
- `search_latency`: Query latency (ms)
- `index_build_time`: Index build duration (seconds)
- `embedding_generation_time`: Embedding generation duration (ms)
- `query_count`: Total queries processed
- `index_size_mb`: Index size on disk (MB)
- `memory_usage_mb`: RAM usage (MB)

**Aggregations:**
- p50, p95, p99 latencies
- Average latency per action
- Slow query log (queries > 1 second)

---

#### 6.7.2 Profiling

**Tools:**
1. **Python Profiler:**
   ```python
   import cProfile
   cProfile.run('index.search(query)', 'profile.stats')
   ```

2. **Memory Profiler:**
   ```python
   from memory_profiler import profile
   @profile
   def search_memory_test():
       index.search(query)
   ```

3. **LanceDB Explain:**
   ```python
   # LanceDB query plan (shows index usage)
   table.search(query).explain()
   ```

**Profiling Workflow:**
1. Identify slow query (from logs)
2. Run profiler on slow query
3. Identify bottleneck (embedding, search, reranking)
4. Optimize bottleneck
5. Re-run profiler, validate improvement

---

#### 6.7.3 Performance Testing

**Test Scenarios:**

1. **Search Load Test:**
   ```python
   def test_search_load():
       """Test 100 sequential searches."""
       start = time.time()
       for i in range(100):
           index.search(f"query {i}")
       duration = time.time() - start
       assert duration < 20  # < 200ms per query on average
   ```

2. **Large Index Test:**
   ```python
   def test_large_index():
       """Test with 10k documents."""
       index.build(generate_test_docs(10000))
       assert index.search("test")["latency_ms"] < 300
   ```

3. **Memory Leak Test:**
   ```python
   def test_memory_leak():
       """Run 1000 searches, ensure no memory growth."""
       initial_mem = psutil.Process().memory_info().rss
       for i in range(1000):
           index.search(f"query {i}")
       final_mem = psutil.Process().memory_info().rss
       assert final_mem < initial_mem * 1.1  # < 10% growth
   ```

**Test Execution:**
- Run as part of CI/CD pipeline
- Fail build if performance regresses > 20%

---

### 6.8 Scalability

**Current Scope (v1.0):**
- Single AI agent, single machine
- No horizontal scaling
- No load balancing

**Scaling Limits:**
- Index size: 100k documents (10GB)
- Query throughput: 50-100 queries/second
- Memory: 4GB RAM
- Disk: 50GB for indexes

**Future Scaling (Out of Scope):**
- **Multi-Agent Support:**
  - Run multiple MCP servers (one per AI agent session)
  - Shared index storage (LanceDB supports concurrent readers)
  
- **Index Sharding:**
  - Shard large indexes across multiple LanceDB tables
  - Query multiple shards in parallel
  
- **Distributed Search:**
  - Run index replicas on multiple machines
  - Load balance searches across replicas

**Decision:** Scaling beyond single-agent is out of scope for v1.0

---

### 6.9 Performance Checklist

**Pre-Release Performance Review:**
- [ ] Search latency p95 < 200ms (standards)
- [ ] Index rebuild < 5 minutes (10k documents)
- [ ] Incremental update < 5 seconds (single file)
- [ ] Cold start < 30 seconds
- [ ] Memory usage < 4GB peak
- [ ] Embedding model cached (avoid reload)
- [ ] FTS/scalar indexes rebuilt after incremental updates
- [ ] Performance metrics logged
- [ ] Load tests passing (100 sequential queries < 20s)
- [ ] Memory leak tests passing (< 10% growth over 1000 queries)

---

**Performance Summary:**
- **Targets:** Search < 200ms p95, index rebuild < 5min, incremental update < 5s, cold start < 30s, memory < 4GB
- **Caching:** Embedding models (1GB RAM), LanceDB indexes (2GB RAM)
- **Optimization:** Batch embedding, lazy loading, debouncing, index optimizations
- **Monitoring:** Latency metrics (p50/p95/p99), memory usage, slow query log
- **Testing:** Load tests (100 queries), large index tests (10k docs), memory leak tests
- **Scalability:** Single-agent (v1.0), future multi-agent/distributed out of scope

---

## 7. Testing Strategy

