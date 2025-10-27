# MCP Server Modular Redesign - Software Requirements Document

**Business case, goals, and requirements.**

---

## 🎯 BUSINESS GOALS

### Primary Goals
1. **Establish Production-Grade Architecture** - Transform MCP server from prototype to sustainable, maintainable system
2. **Enable Sub-Agent Ecosystem** - Create foundation for design validators, concurrency analyzers, and other specialized agents
3. **Reduce Bug Rate** - Improve testability and reduce configuration errors through better architecture
4. **Demonstrate Standards Compliance** - Dogfood Agent OS production code standards in our own codebase

### Success Criteria
- [ ] All modules follow single responsibility principle (<200 lines/file)
- [ ] Configuration has single source of truth with validation
- [ ] Dependency injection throughout enables 90%+ test coverage
- [ ] Tool count monitoring prevents performance degradation
- [ ] Zero breaking changes to existing MCP tool interfaces
- [ ] Sub-agent tools can be added in <30 minutes per agent

---

## 👥 STAKEHOLDERS

### Primary Stakeholders
- **AI Agents (Consuming Agent OS)**: Need stable, high-quality MCP tools with good performance
  - *Concerns*: Breaking changes, tool discovery, performance with >20 tools
  
- **Framework Maintainers**: Need sustainable, extensible architecture
  - *Concerns*: Code quality, testability, bug rate, maintenance burden
  
- **Sub-Agent Developers (Future)**: Need clean interfaces to add specialized tools
  - *Concerns*: Plugin architecture, tool registration, performance monitoring

### Secondary Stakeholders
- **Agent OS Contributors**: Need clear code organization to contribute
  - *Concerns*: Findability, documentation, patterns to follow

---

## 📋 FUNCTIONAL REQUIREMENTS

### FR-1: Modular Architecture
**Priority:** Must Have  
**Description:** MCP server must be organized into domain-specific modules  
**Acceptance Criteria:**
- [ ] `models/` module with config, workflow, rag, sub_agents submodules
- [ ] `config/` module with loader and validator
- [ ] `monitoring/` module with file watcher
- [ ] `server/tools/` module with rag_tools, workflow_tools, sub_agent_tools
- [ ] `server/factory.py` with dependency injection
- [ ] All files <200 lines

### FR-2: Configuration Management
**Priority:** Must Have  
**Description:** Single source of truth for all MCP server configuration  
**Acceptance Criteria:**
- [ ] `RAGConfig` dataclass with all RAG settings
- [ ] `ServerConfig` dataclass with server-wide settings
- [ ] `ConfigLoader` reads from config.json with graceful fallback
- [ ] `ConfigValidator` validates paths and settings at startup
- [ ] No hardcoded paths in any module
- [ ] Defaults clearly defined in dataclass

### FR-3: Dependency Injection
**Priority:** Must Have  
**Description:** All components receive dependencies via constructor injection  
**Acceptance Criteria:**
- [ ] `ServerFactory` creates and wires all components
- [ ] `AgentOSFileWatcher` receives `ServerConfig` (not hardcoded paths)
- [ ] `WorkflowEngine` receives `RAGEngine` and `StateManager`
- [ ] All engines testable with mocked dependencies
- [ ] No `global` or module-level singletons

### FR-4: Tool Scalability
**Priority:** Must Have  
**Description:** Support selective tool loading with performance monitoring  
**Acceptance Criteria:**
- [ ] Tools organized by category (rag, workflow, sub_agent_tools)
- [ ] `register_all_tools()` accepts `enabled_groups` parameter
- [ ] Tool count returned and logged
- [ ] Warning logged if tool count >20
- [ ] Each tool module registers independently
- [ ] Tool groups can be enabled/disabled via config

### FR-5: Backward Compatibility
**Priority:** Must Have  
**Description:** Existing MCP tool interfaces must not break  
**Acceptance Criteria:**
- [ ] All 7 existing tools work identically
- [ ] Existing `config.json` files still work
- [ ] File watcher still auto-rebuilds index
- [ ] No changes to tool signatures or responses
- [ ] Migration happens in phases without breaking

### FR-6: Standards Compliance
**Priority:** Must Have  
**Description:** Code must follow Agent OS production code standards  
**Acceptance Criteria:**
- [ ] Complete type annotations
- [ ] Proper error handling (no bare except)
- [ ] Concurrency safety documented
- [ ] Configuration validated
- [ ] Dependency injection throughout
- [ ] Resource lifecycle managed (observers stopped)

---

## 🔒 NON-FUNCTIONAL REQUIREMENTS

### NFR-1: Performance
- MCP server startup time <2 seconds
- Tool registration <100ms per tool
- Configuration loading <50ms
- No performance regression from modularization

### NFR-2: Maintainability
- All modules <200 lines
- Clear module boundaries
- Comprehensive docstrings
- Type hints on all functions

### NFR-3: Testability
- 90%+ test coverage for new modules
- All components mockable
- Integration tests for end-to-end flows
- Unit tests for each module

### NFR-4: Scalability
- Support 30+ tools without code changes
- Selective tool loading to stay under 20-tool limit
- Sub-agent tools as plugins
- No hardcoded tool lists

---

## ⚠️ CONSTRAINTS

### Technical Constraints
- Must maintain backward compatibility with existing MCP clients
- Must use existing FastMCP framework
- Must work with existing RAG index structure
- Must preserve existing file watcher behavior
- Python 3.8+ compatibility

### Business Constraints
- Cannot break existing consuming projects
- Must complete migration in <2 weeks
- Must have zero downtime for users
- Cannot require manual intervention from consumers

---

## 🎭 USER STORIES

### User Story 1: AI Agent Using MCP Tools
**As an** AI agent consuming Agent OS via MCP  
**I want** stable, performant tools that don't break  
**So that** I can reliably assist users without errors

**Acceptance Criteria:**
- [ ] All existing tools work identically
- [ ] Tool discovery unchanged
- [ ] Response formats unchanged
- [ ] Performance maintained or improved

### User Story 2: Framework Maintainer
**As a** framework maintainer  
**I want** clear, testable modules with good separation of concerns  
**So that** I can fix bugs quickly and add features confidently

**Acceptance Criteria:**
- [ ] Can find relevant code in <30 seconds
- [ ] Can add new tool group in <30 minutes
- [ ] Can test modules in isolation
- [ ] Can understand dependencies from constructor

### User Story 3: Sub-Agent Developer
**As a** developer creating a design validator sub-agent  
**I want** a clear plugin interface for registering tools  
**So that** I can add my agent's tools without touching server core

**Acceptance Criteria:**
- [ ] Can create new file in `server/tools/sub_agent_tools/`
- [ ] Can register tools by implementing `register_X_tools()` function
- [ ] Tool count automatically monitored
- [ ] Can enable/disable via config

### User Story 4: Configuration Administrator
**As an** admin configuring Agent OS for a project  
**I want** a single, validated config file with clear defaults  
**So that** I don't have to hunt for hidden settings or debug path issues

**Acceptance Criteria:**
- [ ] All config in `config.json` with schema
- [ ] Clear error messages if config invalid
- [ ] Defaults work for 80% of projects
- [ ] Validation happens at startup

---

## 🚫 OUT OF SCOPE

**Explicitly NOT included in this redesign:**

- Changes to MCP tool interfaces or behaviors
- New features (only architecture refactoring)
- Migration of existing `core/` engines (minimal changes only)
- Changes to RAG index format
- Changes to workflow state persistence format
- UI or visualization tools
- Performance optimization beyond architecture
- New sub-agent implementations (just the infrastructure)

---

**This SRD defines what success looks like from business, user, and technical perspectives.**

