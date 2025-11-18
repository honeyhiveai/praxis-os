# Ouroboros Architecture Standard

**Last Updated:** 2025-11-17  
**Status:** ACTIVE (extracted from codebase analysis)  
**Scope:** Ouroboros MCP Server architecture, layers, and dependency rules

---

## 🚨 Ouroboros Architecture Quick Reference

**Keywords for search**: ouroboros architecture, layered architecture, dependency rules, foundation layer, subsystems layer, tools layer, middleware layer, config layer, utils layer, where to put code, downward dependencies, circular dependencies, initialization order, tool auto-discovery, subsystem independence, architectural anti-patterns, MCP server architecture, RAG subsystem, workflow subsystem, browser subsystem

**Core Principle:** Ouroboros uses strict layered architecture with downward-only dependencies. Higher layers depend on lower layers, never upward or circular.

**6 Layers (Bottom-Up):**
1. **Utils** - Cross-cutting concerns (errors, logging, metrics) - stdlib only
2. **Config** - Type-safe configuration (Pydantic v2) - fail-fast validation
3. **Foundation** - Low-level infrastructure (locks, sessions, ports) - no business logic
4. **Subsystems** - Domain logic (RAG, Workflow, Browser) - independent, no cross-subsystem deps
5. **Middleware** - Cross-cutting enhancements (query tracking, prepend generation) - behavioral engineering
6. **Tools** - MCP tool interface (thin wrappers) - auto-discovered via ToolRegistry

**Critical Dependency Rules:**
- ✅ **Downward only:** Tools → Middleware → Subsystems → Foundation → Config → Utils
- ❌ **No upward:** Foundation CANNOT depend on Subsystems
- ❌ **No circular:** No layer depends on itself through another layer
- ❌ **No cross-subsystem:** RAG subsystem CANNOT depend on Workflow subsystem

**Initialization Order (MUST follow):**
1. Config (fail-fast validation)
2. Foundation (SessionMapper, InitLock, RuntimeLock)
3. Subsystems (RAG, Workflow, Browser) - parallel, independent
4. Middleware (QueryTracker)
5. Tools (auto-discovered via ToolRegistry)

**Quick Decision Tree - Where Does My Code Go?**
- Business logic → **Subsystems**
- Cross-cutting utility → **Foundation**
- MCP tool interface → **Tools**
- Behavioral tracking → **Middleware**
- Configuration → **Config**
- Error handling → **Utils**

---

## ❓ Questions This Answers

1. "What is the ouroboros architecture and how is it organized?"
2. "What are the layers in ouroboros and what belongs in each?"
3. "What are the dependency rules between layers?"
4. "Where should I put new code in ouroboros?"
5. "How do I know if code belongs in foundation vs subsystems?"
6. "Can subsystems communicate with each other directly?"
7. "What is the initialization order for ouroboros components?"
8. "How does the tool auto-discovery system work?"
9. "What are forbidden dependencies in ouroboros?"
10. "What are architectural anti-patterns to avoid?"
11. "How do I verify my code follows architectural rules?"
12. "What is the difference between foundation and subsystems?"
13. "Why can't foundation depend on subsystems?"
14. "How do tools interact with subsystems?"
15. "What is the role of middleware in ouroboros?"
16. "How are tools registered with the MCP server?"
17. "What is subsystem independence and why does it matter?"
18. "How do I add a new subsystem to ouroboros?"
19. "What is the dependency injection pattern in ouroboros?"
20. "How do I test if my code violates architectural rules?"

---

## 🎯 Purpose and Scope

**Core Principles:** Layered architecture, downward dependencies only, dependency injection, auto-discovery

**Layers (Bottom-Up):**
1. **Utils** - Cross-cutting concerns (errors, logging, metrics)
2. **Config** - Type-safe configuration (Pydantic v2)
3. **Foundation** - Low-level infrastructure (no business logic)
4. **Subsystems** - Domain logic (RAG, Workflow, Browser)
5. **Middleware** - Cross-cutting enhancements (query tracking, session mapping)
6. **Tools** - MCP tool interface (thin wrappers, auto-discovered)

**Dependency Rules:**
- ✅ **Downward only:** Higher layers depend on lower layers
- ❌ **No upward:** Lower layers NEVER depend on higher layers
- ❌ **No circular:** No layer depends on itself through another layer
- ❌ **No skipping:** Tools → Middleware → Subsystems → Foundation (no shortcuts)

**Initialization Order:**
1. Config (fail-fast validation)
2. Foundation (StateManager, SessionMapper)
3. Subsystems (RAG, Workflow, Browser)
4. Middleware (QueryTracker)
5. Tools (auto-discovered via ToolRegistry)

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Agent                                  │
│                   (Claude, GPT-4, etc.)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │ MCP Protocol
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    TOOLS LAYER (Layer 6)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ pos_search_project  pos_workflow  pos_browser            │   │
│  │ pos_filesystem      get_server_info  current_date        │   │
│  └──────────────────────────────────────────────────────────┘   │
│  • Thin wrappers around subsystems                              │
│  • Auto-discovered via ToolRegistry                             │
│  • Action-based dispatch (single tool, multiple actions)        │
│  • Middleware integration (query tracking, prepend generation)  │
└────────────────────────────┬────────────────────────────────────┘
                             │ delegates to
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                  MIDDLEWARE LAYER (Layer 5)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ QueryTracker       PrependGenerator                      │   │
│  │ QueryClassifier    SessionIdExtractor                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│  • Cross-cutting enhancements (behavioral engineering)          │
│  • Wraps all tool calls for tracking/metrics                    │
│  • No business logic (pure middleware)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │ enhances
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                  SUBSYSTEMS LAYER (Layer 4)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ RAG Subsystem                                            │   │
│  │   ├─ IndexManager (orchestration)                        │   │
│  │   ├─ StandardsIndex (hybrid search)                      │   │
│  │   ├─ CodeIndex (semantic + graph + AST)                  │   │
│  │   └─ FileWatcher (incremental updates)                   │   │
│  │                                                           │   │
│  │ Workflow Subsystem                                       │   │
│  │   ├─ WorkflowEngine (phase gating)                       │   │
│  │   ├─ EvidenceValidator (checkpoint validation)           │   │
│  │   └─ DynamicRegistry (workflow discovery)                │   │
│  │                                                           │   │
│  │ Browser Subsystem                                        │   │
│  │   └─ BrowserManager (Playwright wrapper)                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│  • Domain-specific business logic                                │
│  • Independent subsystems (no cross-subsystem dependencies)     │
│  • Depend only on Foundation layer                              │
└────────────────────────────┬────────────────────────────────────┘
                             │ uses
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                  FOUNDATION LAYER (Layer 3)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ InitLock           RuntimeLock (NEW)                     │   │
│  │ SessionMapper      SessionStateHelper                    │   │
│  │ ProjectInfoDiscovery                                     │   │
│  │ PortManager        TransportManager                      │   │
│  │ StateManager                                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│  • Low-level infrastructure utilities                           │
│  • NO business logic                                            │
│  • Stdlib-only dependencies (no external packages)              │
│  • Horizontal concerns (cross-cutting)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │ uses
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    CONFIG LAYER (Layer 2)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ MCPConfig (root)                                         │   │
│  │   ├─ IndexesConfig (RAG subsystem)                       │   │
│  │   ├─ WorkflowConfig (workflow subsystem)                 │   │
│  │   ├─ BrowserConfig (browser subsystem)                   │   │
│  │   └─ LoggingConfig (logging subsystem)                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│  • Type-safe configuration (Pydantic v2)                        │
│  • Fail-fast validation at startup                             │
│  • Single source of truth (config/mcp.yaml)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │ uses
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                     UTILS LAYER (Layer 1)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ ActionableError    Logging    Metrics                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│  • Cross-cutting utilities (errors, logging, metrics)           │
│  • Used by ALL layers                                           │
│  • NO dependencies (stdlib only)                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📂 Directory Structure

```
ouroboros/
├── __init__.py                   # Root package
├── __main__.py                   # Entry point (server startup)
├── server.py                     # Server factory (create_server)
│
├── utils/                        # LAYER 1: Cross-cutting utilities
│   ├── errors.py                 # ActionableError (remediation guidance)
│   ├── logging.py                # Structured JSON logging
│   └── metrics.py                # Behavioral metrics tracking
│
├── config/                       # LAYER 2: Configuration
│   ├── loader.py                 # Config loading utilities
│   └── schemas/                  # Pydantic v2 models
│       ├── base.py               # BaseConfig, EnvType
│       ├── mcp.py                # MCPConfig (root)
│       ├── indexes.py            # IndexesConfig (RAG)
│       ├── workflow.py           # WorkflowConfig
│       ├── browser.py            # BrowserConfig
│       └── logging.py            # LoggingConfig
│
├── foundation/                   # LAYER 3: Low-level infrastructure
│   ├── init_lock.py              # Initialization coordination
│   ├── runtime_lock.py           # Singleton enforcement (NEW)
│   ├── session_mapper.py         # Generic state persistence
│   ├── session_state_helper.py   # Type-safe state wrapper
│   ├── project_info.py           # Project metadata discovery
│   ├── port_manager.py           # Dynamic port allocation
│   ├── transport_manager.py      # Transport orchestration
│   └── state_manager.py          # Legacy state management
│
├── subsystems/                   # LAYER 4: Domain logic
│   ├── rag/                      # RAG Subsystem
│   │   ├── index_manager.py      # Orchestrates all indexes
│   │   ├── base.py               # BaseIndex, HealthStatus, BuildStatus
│   │   ├── lock_manager.py       # Per-index locking (fcntl)
│   │   ├── watcher.py            # File watcher (incremental updates)
│   │   ├── standards/            # Standards index
│   │   │   ├── container.py      # StandardsIndex
│   │   │   └── semantic.py       # Hybrid search (vector + FTS + RRF)
│   │   ├── code/                 # Code index
│   │   │   ├── container.py      # CodeIndex
│   │   │   ├── semantic.py       # Semantic search (CodeBERT)
│   │   │   ├── partition.py      # Multi-repo partitioning
│   │   │   ├── reconciler.py     # Partition reconciliation
│   │   │   └── graph/            # Call graph
│   │   │       ├── container.py  # GraphIndex
│   │   │       ├── ast.py        # AST extraction (Tree-sitter)
│   │   │       └── traversal.py  # Graph traversal (DuckDB)
│   │   └── utils/                # RAG utilities
│   │       ├── component_helpers.py  # Fractal health/build status
│   │       ├── corruption_detector.py
│   │       ├── duckdb_helpers.py
│   │       ├── lancedb_helpers.py
│   │       └── progress_file.py
│   │
│   ├── workflow/                 # Workflow Subsystem
│   │   ├── engine.py             # WorkflowEngine (phase gating)
│   │   ├── evidence_validator.py # Checkpoint validation
│   │   ├── dynamic_registry.py   # Workflow discovery
│   │   ├── guidance.py           # Task guidance generation
│   │   ├── models.py             # Workflow data models
│   │   ├── phase_gates.py        # Phase gate logic
│   │   ├── workflow_renderer.py  # Workflow rendering
│   │   └── parsers/              # Workflow parsers
│   │       ├── markdown/         # Markdown spec parser
│   │       ├── yaml/             # YAML workflow parser
│   │       └── shared/           # Shared parsing utilities
│   │
│   └── browser/                  # Browser Subsystem
│       ├── manager.py            # BrowserManager (Playwright)
│       └── models.py             # Browser data models
│
├── middleware/                   # LAYER 5: Cross-cutting enhancements
│   ├── query_tracker.py          # Query history tracking
│   ├── query_classifier.py       # Angle detection
│   ├── prepend_generator.py      # Gamification messages
│   └── session_id_extractor.py   # Session ID extraction
│
└── tools/                        # LAYER 6: MCP tool interface
    ├── registry.py               # ToolRegistry (auto-discovery)
    ├── base.py                   # ActionDispatchMixin
    ├── pos_search_project.py     # Unified search tool
    ├── pos_workflow.py           # Workflow management tool
    ├── pos_browser.py            # Browser automation tool
    ├── pos_filesystem.py         # File operations tool
    ├── get_server_info.py        # Server status tool
    └── current_date.py           # Date/time tool
```

---

## 🎯 Layer Definitions

### Layer 1: Utils (Cross-Cutting Utilities)

**Purpose:** Foundational utilities used by ALL layers

**Contents:**
- `errors.py`: ActionableError with remediation guidance
- `logging.py`: Structured JSON logging
- `metrics.py`: Behavioral metrics tracking

**Rules:**
- ✅ Used by all layers
- ✅ Stdlib-only dependencies
- ❌ NO dependencies on other ouroboros layers
- ❌ NO business logic

**Example:**
```python
from ouroboros.utils.errors import ActionableError

raise ActionableError(
    what_failed="Config validation",
    why_failed="chunk_size must be >= 100",
    how_to_fix="Update config: indexes.vector.chunk_size = 500"
)
```

---

### Layer 2: Config (Type-Safe Configuration)

**Purpose:** Single source of truth for all configuration

**Contents:**
- `schemas/`: Pydantic v2 models for all config sections
- `loader.py`: Config loading and validation utilities

**Rules:**
- ✅ Depends on Utils only
- ✅ Fail-fast validation at startup
- ✅ Type-safe access (IDE autocomplete)
- ❌ NO business logic
- ❌ NO runtime config changes (immutable after load)

**Example:**
```python
from ouroboros.config.schemas.mcp import MCPConfig

config = MCPConfig.from_yaml(Path(".praxis-os/config/mcp.yaml"))
print(config.indexes.standards.vector.model)  # Type-safe access
```

---

### Layer 3: Foundation (Low-Level Infrastructure)

**Purpose:** Low-level utilities with NO business logic

**Contents:**
- `InitLock`: Initialization coordination (prevents concurrent spawns)
- `RuntimeLock`: Singleton enforcement (NEW - lifetime lock)
- `SessionMapper`: Generic state persistence
- `SessionStateHelper`: Type-safe state wrapper
- `ProjectInfoDiscovery`: Project metadata discovery
- `PortManager`: Dynamic port allocation
- `TransportManager`: Transport orchestration
- `StateManager`: Legacy state management

**Rules:**
- ✅ Depends on Config, Utils only
- ✅ Stdlib-only dependencies (no external packages)
- ✅ Horizontal concerns (cross-cutting)
- ❌ NO business logic
- ❌ NO dependencies on Subsystems, Middleware, Tools

**Characteristics:**
- **Reusable:** Can be used by any subsystem
- **Generic:** Not tied to specific domain logic
- **Stateless:** Mostly stateless utilities (except StateManager)

**Example:**
```python
from ouroboros.foundation.init_lock import InitLock

lock = InitLock(base_path, timeout_seconds=10)
if lock.acquire():
    # Initialize server
    pass
```

---

### Layer 4: Subsystems (Domain Logic)

**Purpose:** Domain-specific business logic

**Contents:**
- **RAG Subsystem:** Multi-index search (standards, code, AST, graph)
- **Workflow Subsystem:** Phase-gated execution with evidence validation
- **Browser Subsystem:** Playwright-based browser automation

**Rules:**
- ✅ Depends on Foundation, Config, Utils only
- ✅ Independent subsystems (no cross-subsystem dependencies)
- ✅ Business logic lives here
- ❌ NO dependencies on Middleware or Tools
- ❌ NO direct communication between subsystems

**Subsystem Independence:**
```
RAG Subsystem ❌ → Workflow Subsystem (FORBIDDEN)
RAG Subsystem ✅ → Foundation Layer (ALLOWED)
```

**Example:**
```python
from ouroboros.subsystems.rag.index_manager import IndexManager

index_manager = IndexManager(config.indexes, base_path)
results = index_manager.search("standards", "How does X work?")
```

---

### Layer 5: Middleware (Cross-Cutting Enhancements)

**Purpose:** Cross-cutting enhancements that wrap tool calls

**Contents:**
- `QueryTracker`: Query history and behavioral metrics
- `QueryClassifier`: Angle detection (conceptual, location, etc.)
- `PrependGenerator`: Gamification messages
- `SessionIdExtractor`: Session ID extraction

**Rules:**
- ✅ Depends on Foundation, Config, Utils only
- ✅ Wraps tool calls (100% coverage)
- ✅ NO business logic (pure middleware)
- ❌ NO dependencies on Subsystems or Tools
- ❌ NO direct subsystem access

**Characteristics:**
- **Transparent:** Tools don't know they're being tracked
- **Optional:** Server works without middleware (degraded)
- **Behavioral:** Focused on behavioral engineering

**Example:**
```python
from ouroboros.middleware.query_tracker import QueryTracker

tracker = QueryTracker()
tracker.log_query("How does X work?", session_id="abc123")
```

---

### Layer 6: Tools (MCP Tool Interface)

**Purpose:** MCP tools exposing subsystems to AI agents

**Contents:**
- `pos_search_project`: Unified search (6 actions)
- `pos_workflow`: Workflow management (14 actions)
- `pos_browser`: Browser automation (24 actions)
- `pos_filesystem`: File operations (12 actions)
- `get_server_info`: Server status/health/metrics
- `current_date`: Date/time tool

**Rules:**
- ✅ Depends on Middleware, Subsystems, Foundation, Config, Utils
- ✅ Thin wrappers (delegate to subsystems)
- ✅ Action-based dispatch (single tool, multiple actions)
- ✅ Auto-discovered via ToolRegistry
- ❌ NO business logic (pure delegation)

**Tool Pattern:**
```python
# Tools delegate to subsystems
class SearchTool:
    def __init__(self, mcp, index_manager, query_tracker):
        self.index_manager = index_manager  # Subsystem
        self.query_tracker = query_tracker  # Middleware
    
    def _handle_search_standards(self, query, ...):
        # Delegate to subsystem
        return self.index_manager.search("standards", query, ...)
```

---

## 🔄 Initialization Order

**Critical:** Subsystems must be initialized in dependency order.

```python
# server.py: create_server()

# 1. Load Config (fail-fast validation)
config = MCPConfig.from_yaml(config_path)

# 2. Initialize Foundation Layer
session_mapper = SessionMapper(state_dir)

# 3. Initialize Subsystems (independent, any order)
index_manager = IndexManager(config.indexes, base_path)
workflow_engine = WorkflowEngine(config.workflow, base_path, session_mapper)
browser_manager = BrowserManager(config.browser, session_mapper)

# 4. Initialize Middleware
query_tracker = QueryTracker()

# 5. Register Tools (auto-discovery)
registry = ToolRegistry(
    tools_dir=tools_dir,
    mcp_server=mcp,
    dependencies={
        "index_manager": index_manager,
        "workflow_engine": workflow_engine,
        "browser_manager": browser_manager,
        "session_mapper": session_mapper,
        "query_tracker": query_tracker,
    }
)
results = registry.register_all()
```

---

## 🚫 Dependency Rules (CRITICAL)

### ✅ **Allowed Dependencies (Downward Only)**

```
Tools → Middleware → Subsystems → Foundation → Config → Utils
  ↓        ↓            ↓             ↓          ↓        ↓
 ALL     ALL          ALL           ALL        ALL     NONE
```

**Matrix:**

|  | Utils | Config | Foundation | Subsystems | Middleware | Tools |
|--|-------|--------|------------|------------|------------|-------|
| **Utils** | - | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Config** | ✅ | - | ❌ | ❌ | ❌ | ❌ |
| **Foundation** | ✅ | ✅ | - | ❌ | ❌ | ❌ |
| **Subsystems** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Middleware** | ✅ | ✅ | ✅ | ❌ | - | ❌ |
| **Tools** | ✅ | ✅ | ✅ | ✅ | ✅ | - |

**Legend:**
- ✅ = Can import/depend on
- ❌ = FORBIDDEN (circular or upward dependency)
- `-` = Self (N/A)

---

### ❌ **Forbidden Dependencies**

**1. No Upward Dependencies:**
```python
# ❌ FORBIDDEN
from ouroboros.subsystems.rag import IndexManager  # in foundation/

# ✅ ALLOWED
from ouroboros.foundation import SessionMapper  # in subsystems/
```

**2. No Circular Dependencies:**
```python
# ❌ FORBIDDEN
# subsystems/rag/index_manager.py
from ouroboros.subsystems.workflow import WorkflowEngine

# subsystems/workflow/engine.py
from ouroboros.subsystems.rag import IndexManager
```

**3. No Cross-Subsystem Dependencies:**
```python
# ❌ FORBIDDEN
# subsystems/rag/index_manager.py
from ouroboros.subsystems.workflow import WorkflowEngine

# ✅ ALLOWED (via Foundation)
from ouroboros.foundation import SessionMapper
```

**4. No Skipping Layers:**
```python
# ❌ FORBIDDEN (Tools → Subsystems directly, skipping Middleware)
# tools/pos_search_project.py
from ouroboros.subsystems.rag import IndexManager

# ✅ ALLOWED (Tools → Middleware → Subsystems)
# tools/pos_search_project.py
from ouroboros.middleware import QueryTracker
# IndexManager passed via dependency injection
```

---

## 🔧 Tool Auto-Discovery System

**Pattern:** Drop a file in `tools/`, no code changes needed!

**How It Works:**
1. Each tool module exports a `register_*_tool()` function
2. `ToolRegistry` scans `tools/` directory at startup
3. Imports each module and calls registration function
4. Passes dependencies via dependency injection

**Example Tool:**
```python
# tools/my_new_tool.py

def register_my_new_tool(mcp, dependencies):
    """Register my_new_tool with FastMCP."""
    
    # Extract dependencies
    my_subsystem = dependencies.get("my_subsystem")
    query_tracker = dependencies.get("query_tracker")
    
    # Define tool
    @mcp.tool()
    async def my_new_tool(action: str, param: str) -> dict:
        """My new tool description."""
        # Delegate to subsystem
        return my_subsystem.do_something(param)
    
    return my_new_tool
```

**ToolRegistry discovers and registers automatically!**

---

## 🎯 Architectural Patterns

### Pattern 1: Dependency Injection

**All subsystems receive dependencies via constructor:**

```python
class IndexManager:
    def __init__(self, config: IndexesConfig, base_path: Path):
        self.config = config
        self.base_path = base_path
```

**Benefits:**
- ✅ Testable (inject mocks)
- ✅ Explicit dependencies
- ✅ No hidden coupling

---

### Pattern 2: Action-Based Dispatch

**Single tool, multiple actions:**

```python
@mcp.tool()
async def pos_search_project(
    action: Literal["search_standards", "search_code", "search_ast", ...],
    query: str,
    ...
) -> dict:
    # Dispatch to handler based on action
    handler = self.handlers[action]
    return await handler(query, ...)
```

**Benefits:**
- ✅ Fewer tools (better UX)
- ✅ Related actions grouped
- ✅ Consistent interface

---

### Pattern 3: Fractal Health Checks

**Health status aggregates recursively:**

```python
# IndexManager aggregates index health
def health_check(self) -> HealthStatus:
    return dynamic_health_check(
        components={
            "standards": self._indexes["standards"],
            "code": self._indexes["code"],
        }
    )

# CodeIndex aggregates component health
def health_check(self) -> HealthStatus:
    return dynamic_health_check(
        components={
            "semantic": self._semantic_index,
            "graph": self._graph_index,
        }
    )
```

**Benefits:**
- ✅ Consistent pattern
- ✅ Composable
- ✅ Detailed diagnostics

---

## 🚨 Anti-Patterns to Avoid

### ❌ **Anti-Pattern 1: Circular Dependencies**

**Problem:**
```python
# subsystems/rag/index_manager.py
from ouroboros.subsystems.workflow import WorkflowEngine

# subsystems/workflow/engine.py
from ouroboros.subsystems.rag import IndexManager
```

**Solution:** Use Foundation layer for shared state:
```python
# Both subsystems depend on Foundation
from ouroboros.foundation import SessionMapper
```

---

### ❌ **Anti-Pattern 2: Business Logic in Foundation**

**Problem:**
```python
# foundation/session_mapper.py
def validate_workflow_evidence(self, evidence):
    # ❌ Business logic in foundation layer!
    if evidence["tests_passed"] < 10:
        return False
```

**Solution:** Move to Subsystems:
```python
# subsystems/workflow/evidence_validator.py
def validate_evidence(self, evidence):
    # ✅ Business logic in subsystems layer
    if evidence["tests_passed"] < 10:
        return False
```

---

### ❌ **Anti-Pattern 3: Tools with Business Logic**

**Problem:**
```python
# tools/pos_search_project.py
def _handle_search_standards(self, query):
    # ❌ Business logic in tools layer!
    chunks = self._chunk_documents(query)
    embeddings = self._generate_embeddings(chunks)
    results = self._vector_search(embeddings)
    return results
```

**Solution:** Delegate to Subsystems:
```python
# tools/pos_search_project.py
def _handle_search_standards(self, query):
    # ✅ Thin wrapper, delegates to subsystem
    return self.index_manager.search("standards", query)
```

---

### ❌ **Anti-Pattern 4: Skipping Layers**

**Problem:**
```python
# tools/pos_search_project.py
from ouroboros.subsystems.rag.standards.semantic import SemanticIndex

# ❌ Skipping IndexManager, directly accessing internal index
semantic_index = SemanticIndex(...)
results = semantic_index.search(query)
```

**Solution:** Use proper abstraction:
```python
# tools/pos_search_project.py
# ✅ Use IndexManager (proper abstraction)
results = self.index_manager.search("standards", query)
```

---

## 📊 Architectural Metrics

**Layer Complexity (Target):**
- Utils: <500 LOC total
- Config: <1000 LOC total
- Foundation: <2000 LOC total
- Subsystems: <10,000 LOC total (largest layer)
- Middleware: <1000 LOC total
- Tools: <3000 LOC total

**Module Size (Target):**
- Foundation modules: <300 LOC each
- Subsystem modules: <500 LOC each
- Tool modules: <300 LOC each

**Dependency Fan-Out (Target):**
- Foundation modules: <5 imports from ouroboros
- Subsystem modules: <10 imports from ouroboros
- Tool modules: <15 imports from ouroboros

---

## 🔍 Verification Checklist

**Before adding new code, verify:**

- [ ] ✅ Which layer does this belong in?
- [ ] ✅ Does it follow dependency rules (downward only)?
- [ ] ✅ Is it in the right directory?
- [ ] ✅ Does it have business logic? (Subsystems only)
- [ ] ✅ Is it a cross-cutting concern? (Foundation or Middleware)
- [ ] ✅ Does it depend on higher layers? (FORBIDDEN)
- [ ] ✅ Is it testable? (Dependency injection)
- [ ] ✅ Does it follow existing patterns?

---

## 📚 Related Standards

- `praxis-os-architecture.md` - High-level praxis-os architecture
- `separation-of-concerns.md` - Universal layering principles
- `solid-principles.md` - SOLID design principles
- `dependency-injection.md` - Dependency injection patterns
- `production-code-checklist.md` - Code quality standards

---

## 🎓 Summary

**Ouroboros is a layered architecture with strict dependency rules:**

1. **6 Layers:** Utils → Config → Foundation → Subsystems → Middleware → Tools
2. **Downward Dependencies Only:** Higher layers depend on lower layers
3. **Independent Subsystems:** No cross-subsystem dependencies
4. **Thin Tools:** Delegate to subsystems, no business logic
5. **Auto-Discovery:** Tools auto-discovered via ToolRegistry
6. **Dependency Injection:** All dependencies explicit and testable

**When in doubt:**
- Business logic → Subsystems
- Cross-cutting utilities → Foundation
- Tool interface → Tools
- Behavioral tracking → Middleware
- Configuration → Config
- Error handling → Utils

**Architecture Grade:** A+ (clean, layered, maintainable)

