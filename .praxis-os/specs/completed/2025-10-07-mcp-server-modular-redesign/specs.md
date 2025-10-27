# MCP Server Modular Redesign - Technical Specifications

**Architecture, design, and technical details.**

---

## 🏗️ ARCHITECTURE OVERVIEW

### System Diagram

```
mcp_server/
├── models/                     # Data structures (scalable)
│   ├── __init__.py             # Central exports
│   ├── config.py               # RAGConfig, ServerConfig
│   ├── workflow.py             # Workflow state models
│   ├── rag.py                  # RAG models
│   ├── tools.py                # Tool schemas (future)
│   └── sub_agents/             # Sub-agent models (future)
│
├── config/                     # Configuration management
│   ├── __init__.py
│   ├── loader.py               # ConfigLoader
│   └── validator.py            # ConfigValidator
│
├── monitoring/                 # File watching
│   ├── __init__.py
│   ├── watcher.py              # AgentOSFileWatcher
│   └── handlers.py             # Event handlers (future)
│
├── server/                     # Server creation & tools
│   ├── __init__.py
│   ├── factory.py              # ServerFactory (DI)
│   └── tools/                  # MCP tools (scalable)
│       ├── __init__.py         # Tool registry
│       ├── rag_tools.py        # search_standards
│       ├── workflow_tools.py   # start_workflow, get_task, etc.
│       └── sub_agent_tools/    # Future sub-agents
│           ├── design_validator.py
│           └── concurrency_analyzer.py
│
├── core/                       # Existing engines (minimal changes)
│   ├── rag_engine.py
│   ├── workflow_engine.py
│   ├── state_manager.py
│   └── framework_generator.py
│
├── chunker.py                  # Document chunking
└── __main__.py                 # Entry point (uses factory)
```

### Components

#### Component 1: models/
**Purpose:** Centralized data structures organized by domain  
**Responsibilities:**
- Define all dataclasses and models
- Provide type safety throughout application
- Enable clean imports via `__init__.py`
- Scale to support sub-agent models

#### Component 2: config/
**Purpose:** Configuration management with single source of truth  
**Responsibilities:**
- Load configuration from `config.json`
- Provide graceful fallback to defaults
- Validate paths and settings
- Resolve relative paths to absolute

#### Component 3: monitoring/
**Purpose:** File system monitoring and index rebuilds  
**Responsibilities:**
- Watch configured paths for changes
- Trigger incremental index rebuilds
- Debounce rapid changes
- Support hot reload

#### Component 4: server/
**Purpose:** Server creation and tool registration  
**Responsibilities:**
- Wire components with dependency injection (factory.py)
- Register MCP tools by category (tools/)
- Monitor tool count for performance
- Enable selective tool loading

#### Component 5: core/
**Purpose:** Core business logic (existing, minimal changes)  
**Responsibilities:**
- RAG search and indexing
- Workflow state management
- Framework generation
- (Mostly unchanged in redesign)

---

## 📡 API SPECIFICATIONS

### Module APIs

#### ConfigLoader API

**Function:** `load(base_path: Path) -> ServerConfig`  
**Purpose:** Load server configuration with validation

**Parameters:**
```python
base_path: Path  # Path to .praxis-os/ directory
```

**Returns:**
```python
ServerConfig(
    base_path=Path("/project/.praxis-os"),
    rag=RAGConfig(
        standards_path=".praxis-os/standards",
        usage_path=".praxis-os/usage",
        workflows_path=".praxis-os/workflows",
        index_path=".praxis-os/.cache/vector_index",
        embedding_provider="local"
    )
)
```

**Error Handling:**
- Missing config.json: Log info, use defaults
- Invalid JSON: Log warning, use defaults
- Invalid paths: Validation error with details

---

#### ServerFactory API

**Function:** `create_server() -> FastMCP`  
**Purpose:** Create fully configured MCP server

**Workflow:**
```
1. Ensure directories exist
2. Ensure RAG index exists
3. Create core components (RAG engine, workflow engine, etc.)
4. Start file watchers
5. Register MCP tools
6. Return configured server
```

**Dependencies Created:**
- RAGEngine (with configured paths)
- StateManager (with base path)
- WorkflowEngine (with RAG + State)
- FrameworkGenerator (with RAG)
- AgentOSFileWatcher (with config)

---

#### Tool Registration API

**Function:** `register_all_tools(mcp, rag_engine, workflow_engine, framework_generator, enabled_groups) -> int`  
**Purpose:** Register MCP tools with selective loading

**Parameters:**
```python
mcp: FastMCP                        # Server instance
rag_engine: RAGEngine               # For search tools
workflow_engine: WorkflowEngine     # For workflow tools
framework_generator: FrameworkGenerator  # For create_workflow
enabled_groups: List[str] = None    # Tool groups to enable
```

**Returns:**
```python
tool_count: int  # Total tools registered
```

**Behavior:**
```python
if enabled_groups is None:
    enabled_groups = ["rag", "workflow"]  # Default: core only

tool_count = 0
if "rag" in enabled_groups:
    tool_count += register_rag_tools(mcp, rag_engine)
if "workflow" in enabled_groups:
    tool_count += register_workflow_tools(mcp, workflow_engine, framework_generator)

if tool_count > 20:
    logger.warning(f"⚠️ {tool_count} tools exceeds recommended limit (20)")

return tool_count
```

---

## 💾 DATA MODELS

### Model 1: RAGConfig

```python
@dataclass
class RAGConfig:
    """RAG system configuration with validated defaults."""
    
    # Paths (relative to project root)
    standards_path: str = ".praxis-os/standards"
    usage_path: str = ".praxis-os/usage"
    workflows_path: str = ".praxis-os/workflows"
    index_path: str = ".praxis-os/.cache/vector_index"
    
    # Settings
    embedding_provider: str = "local"
    
    def resolve_paths(self, project_root: Path) -> Dict[str, Path]:
        """Resolve relative paths to absolute paths."""
        return {
            "standards_path": project_root / self.standards_path,
            "usage_path": project_root / self.usage_path,
            "workflows_path": project_root / self.workflows_path,
            "index_path": project_root / self.index_path,
        }
```

**Validation Rules:**
- All path strings must be relative or absolute
- `embedding_provider` must be "local" or "openai"
- Paths validated at runtime by ConfigValidator

---

### Model 2: ServerConfig

```python
@dataclass
class ServerConfig:
    """Complete MCP server configuration."""
    
    base_path: Path
    rag: RAGConfig
    
    @property
    def project_root(self) -> Path:
        """Project root is parent of base_path."""
        return self.base_path.parent
    
    @property
    def resolved_paths(self) -> Dict[str, Path]:
        """Get all resolved paths."""
        return self.rag.resolve_paths(self.project_root)
```

**Validation Rules:**
- `base_path` must exist and be a directory
- All resolved paths must exist (except index_path parent)

---

## 🔄 WORKFLOW / PROCESS FLOW

### Workflow 1: Server Startup

```
1. main() loads configuration via ConfigLoader.load(base_path)
2. ConfigValidator.validate(config) checks all paths
3. If validation fails: log errors, raise ValueError
4. ServerFactory(config) created with validated config
5. factory.create_server() called:
   a. Ensure cache directories exist
   b. Ensure RAG index exists
   c. Create RAGEngine with resolved paths
   d. Create StateManager, WorkflowEngine, FrameworkGenerator
   e. Start file watchers (one per monitored path)
   f. Create FastMCP server
   g. Register tools via register_all_tools()
   h. Log tool count
   i. Return server
6. server.run(transport='stdio')
```

---

### Workflow 2: Configuration Loading

```
1. ConfigLoader.load(base_path) called
2. Check if config.json exists at base_path / "config.json"
3. If missing:
   - Log info message
   - Return RAGConfig() with defaults
   - Wrap in ServerConfig
4. If exists:
   - Read and parse JSON
   - Extract "rag" section
   - Create RAGConfig with overrides (defaults for missing)
   - Handle parse errors gracefully
   - Return ServerConfig
5. ConfigValidator.validate() called
6. Check all resolved paths exist
7. Return list of errors (empty if valid)
```

---

### Workflow 3: Tool Registration

```
1. register_all_tools() called with enabled_groups
2. If enabled_groups None: use ["rag", "workflow"]
3. Initialize tool_count = 0
4. For each enabled group:
   - Call register_X_tools(mcp, dependencies)
   - Add returned count to tool_count
5. If tool_count > 20:
   - Log warning about performance
6. Log info with total tool count
7. Return tool_count
```

---

### Workflow 4: File Watcher Rebuild

```
1. File change event detected by watchdog
2. AgentOSFileWatcher.on_modified() called
3. Check if rebuild already pending (debounce)
4. If not pending:
   - Set rebuild_pending = True
   - Schedule rebuild after debounce_seconds
5. After debounce:
   - Log rebuild trigger
   - Call IndexBuilder with configured paths
   - Rebuild index incrementally
   - If rag_engine exists: reload index (hot reload)
   - Set rebuild_pending = False
```

---

## 🔐 SECURITY CONSIDERATIONS

### Authentication
- MCP server runs locally, no network authentication
- File system access controlled by OS permissions

### Authorization
- RAG index read-only after build
- Configuration files protected by file permissions
- No user input directly into file system operations

### Data Protection
- Configuration validated before use (path traversal prevention)
- Paths resolved safely (no symlink attacks)
- Error messages don't expose sensitive paths

---

## ⚡ PERFORMANCE CONSIDERATIONS

### Expected Load
- MCP tool calls: 1-10 per minute per agent
- RAG searches: <1 second per query
- Index rebuilds: Triggered on file change only (debounced)

### Performance Targets
- **Server Startup**: <2 seconds
- **Tool Registration**: <100ms total
- **Configuration Loading**: <50ms
- **Tool Call Latency**: No regression from current

### Optimization Strategies
- Lazy loading of components where possible
- Selective tool loading to stay under 20-tool limit
- Debounced file watching (avoid rebuild storms)
- Hot reload of RAG index (no server restart)

### Tool Count Performance

**Research-Based Limits:**
- **<20 tools**: Optimal LLM performance
- **20-30 tools**: Degraded performance (up to 85% drop)
- **>30 tools**: Severe "lost in the middle" effect

**Our Strategy:**
- Default: 7 tools (rag + workflow)
- With 2 sub-agents: ~15 tools (safe)
- With 4 sub-agents: ~23 tools (warning logged)
- Selective loading prevents hitting limit

---

## 🧪 TESTING STRATEGY

### Unit Testing
- Each module tested in isolation
- Mock dependencies via dependency injection
- Test dataclass validation
- Test configuration loading (missing, invalid, valid)
- Test path resolution
- Test tool registration with different groups

### Integration Testing
- End-to-end server creation
- Configuration validation with real filesystem
- Tool registration and invocation
- File watcher triggering index rebuild
- Multi-tool workflows

### End-to-End Testing
- Full server startup with real config
- MCP tool calls via stdio transport
- File change triggering rebuild and hot reload
- Backward compatibility with existing tools

### Performance Testing
- Benchmark server startup time
- Benchmark tool registration time
- Test with 10, 20, 30 tools (measure latency)
- Verify no regression from current architecture

---

## 🔌 INTEGRATION POINTS

### Integration 1: FastMCP Framework
**Purpose:** MCP protocol implementation  
**Method:** Use FastMCP decorators and server instance  
**Error Handling:** FastMCP handles protocol errors, we handle tool errors

### Integration 2: Watchdog File Watcher
**Purpose:** Monitor file system for changes  
**Method:** Use Observer + FileSystemEventHandler  
**Error Handling:** Catch permission errors, log and continue

### Integration 3: LanceDB RAG Index
**Purpose:** Vector search for documentation  
**Method:** Use IndexBuilder and RAGEngine  
**Error Handling:** Validate index exists, rebuild if corrupted

---

## 🚀 DEPLOYMENT STRATEGY

### Deployment Method
- No separate deployment (code is the server)
- Users pull latest code or update via Agent OS update process
- MCP server restarts automatically on code change (Cursor restarts it)

### Rollout Plan
1. **Phase 1**: Create new modules (no breaking changes)
2. **Phase 2**: Wire new architecture, test with existing functionality
3. **Phase 3**: Deprecate old code, full migration
4. **Phase 4**: Enable sub-agent support

### Rollback Plan
- Git revert to previous commit
- User restarts MCP server (Cursor → Settings → MCP → Restart)
- All existing functionality preserved (backward compatible)

---

**This spec defines the complete technical architecture for the modular redesign.**

