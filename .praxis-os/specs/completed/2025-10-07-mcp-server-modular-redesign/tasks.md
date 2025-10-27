# MCP Server Modular Redesign - Implementation Tasks

**Phased task breakdown for implementation.**

---

## 📊 IMPLEMENTATION PHASES

### Phase 1: Foundation - Create New Modules (Week 1, Days 1-3)

**Goal:** Establish new modular structure alongside existing code without breaking changes

**Tasks:**

- [x] **Task 1.1**: Create `models/` module structure
  - **Estimated Time**: 4 hours
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - [x] `models/__init__.py` with clean exports
    - [x] `models/config.py` with RAGConfig and ServerConfig
    - [x] `models/workflow.py` with existing workflow models moved
    - [x] `models/rag.py` with RAG-related models
    - [x] `models/sub_agents/__init__.py` placeholder
    - [x] All models importable via `from mcp_server.models import X`

- [x] **Task 1.2**: Create `config/` module
  - **Estimated Time**: 3 hours
  - **Dependencies**: Task 1.1 (needs models/config.py)
  - **Acceptance Criteria**:
    - [x] `config/loader.py` with ConfigLoader class
    - [x] `config/validator.py` with ConfigValidator class
    - [x] Unit tests for loading with missing/invalid/valid config
    - [x] Unit tests for path validation
    - [x] Graceful fallback to defaults works

- [x] **Task 1.3**: Create `monitoring/` module
  - **Estimated Time**: 2 hours
  - **Dependencies**: Task 1.1 (needs ServerConfig)
  - **Acceptance Criteria**:
    - [x] `monitoring/watcher.py` with refactored AgentOSFileWatcher
    - [x] Constructor accepts ServerConfig (no hardcoded paths)
    - [x] Uses configured paths in rebuild
    - [x] Unit tests with mocked config

- [x] **Task 1.4**: Create `server/tools/` module structure
  - **Estimated Time**: 5 hours
  - **Dependencies**: None (parallel with 1.1-1.3)
  - **Acceptance Criteria**:
    - [x] `server/tools/__init__.py` with register_all_tools()
    - [x] `server/tools/rag_tools.py` with search_standards
    - [x] `server/tools/workflow_tools.py` with 7 workflow tools
    - [x] `server/tools/sub_agent_tools/__init__.py` placeholder
    - [x] Tool count monitoring (warning at >20)
    - [x] Selective loading works (enabled_groups parameter)

- [x] **Task 1.5**: Create `server/factory.py`
  - **Estimated Time**: 4 hours
  - **Dependencies**: Tasks 1.1-1.4
  - **Acceptance Criteria**:
    - [x] ServerFactory class with __init__(config)
    - [x] create_server() method with full DI
    - [x] Creates all core components
    - [x] Starts file watchers
    - [x] Registers tools
    - [x] Returns configured FastMCP server

**Phase Deliverables:**
- New modular structure exists
- All new modules have unit tests
- Old code still works (not using new modules yet)

**Validation Gate:**
- [x] All unit tests pass (new modules)
- [x] All existing tests still pass (no breakage)
- [x] Imports work correctly
- [x] Code review shows clean module boundaries

---

### Phase 2: Integration - Wire New Architecture (Week 1, Days 4-5)

**Goal:** Connect new architecture to entry point and validate with existing functionality

**Tasks:**

- [x] **Task 2.1**: Update `__main__.py` to use new factory
  - **Estimated Time**: 2 hours
  - **Dependencies**: Phase 1 complete
  - **Acceptance Criteria**:
    - [x] Import ConfigLoader, ConfigValidator, ServerFactory
    - [x] Load config with ConfigLoader.load()
    - [x] Validate with ConfigValidator.validate()
    - [x] Create server with ServerFactory(config).create_server()
    - [x] Backward compatible with existing config.json

- [x] **Task 2.2**: Update existing core engines to accept injected dependencies
  - **Estimated Time**: 3 hours
  - **Dependencies**: Task 2.1
  - **Acceptance Criteria**:
    - [x] RAGEngine accepts configured paths
    - [x] WorkflowEngine accepts workflows_base_path
    - [x] StateManager uses base_path from config
    - [x] No hardcoded paths remain

- [x] **Task 2.3**: Integration testing
  - **Estimated Time**: 4 hours
  - **Dependencies**: Tasks 2.1-2.2
  - **Acceptance Criteria**:
    - [x] End-to-end test: server starts with new architecture
    - [x] All 8 MCP tools work identically
    - [x] File watcher triggers rebuild correctly
    - [x] Configuration validation works
    - [x] Hot reload works

- [x] **Task 2.4**: Test with custom config.json
  - **Estimated Time**: 2 hours
  - **Dependencies**: Task 2.3
  - **Acceptance Criteria**:
    - [x] Custom paths work
    - [x] Partial config uses defaults for missing
    - [x] Invalid config shows clear errors
    - [x] Path resolution correct

**Phase Deliverables:**
- New architecture fully wired
- All existing functionality working
- Integration tests passing

**Validation Gate:**
- [x] All 8 MCP tools callable and working
- [x] File watcher rebuilds index on changes
- [x] Configuration validation catches errors
- [x] No regressions in functionality
- [x] Performance maintained or improved

---

### Phase 3: Cleanup - Deprecate Old Code (Week 2, Days 1-2)

**Goal:** Remove scattered configuration and clean up monolithic modules

**Tasks:**

- [x] **Task 3.1**: Remove old `_load_path_config()` from praxis_os_rag.py
  - **Estimated Time**: 1 hour
  - **Dependencies**: Phase 2 complete
  - **Acceptance Criteria**:
    - [x] Function removed
    - [x] All references updated to use ConfigLoader
    - [x] No broken imports

- [x] **Task 3.2**: Remove old tool registration from praxis_os_rag.py
  - **Estimated Time**: 2 hours
  - **Dependencies**: Task 3.1
  - **Acceptance Criteria**:
    - [x] Tool definitions moved to server/tools/
    - [x] `create_server()` removed from praxis_os_rag.py (entire file deleted)
    - [x] File reduced to utilities only (deleted, replaced by modular architecture)

- [x] **Task 3.3**: Move models from models.py to models/ module
  - **Estimated Time**: 2 hours
  - **Dependencies**: Task 3.1
  - **Acceptance Criteria**:
    - [x] Old models.py deprecated (deleted)
    - [x] All imports updated to use models/ module
    - [x] Backward compatible imports (if needed)

- [x] **Task 3.4**: Clean up hardcoded paths in old AgentOSFileWatcher
  - **Estimated Time**: 1 hour
  - **Dependencies**: Tasks 3.1-3.3
  - **Acceptance Criteria**:
    - [x] Old AgentOSFileWatcher removed (deleted with praxis_os_rag.py)
    - [x] Only new monitoring/watcher.py used
    - [x] All watchers use configured paths

- [x] **Task 3.5**: Update documentation
  - **Estimated Time**: 3 hours
  - **Dependencies**: Tasks 3.1-3.4
  - **Acceptance Criteria**:
    - [x] README.md reflects new architecture
    - [x] ARCHITECTURE.md updated with new structure
    - [x] CONTRIBUTING.md updated with new patterns
    - [x] CHANGELOG.md documents changes (v1.4.0 entry added)

**Phase Deliverables:**
- Clean, modular codebase
- No legacy code paths
- Updated documentation

**Validation Gate:**
- [x] No duplicated code
- [x] All tests passing (33/33: 28 unit + 5 integration)
- [x] Documentation accurate
- [x] Code review confirms clean architecture

---

### Phase 4: Enhancement - Enable Sub-Agent Support (Week 2, Days 3-5)

**Goal:** Validate architecture with first sub-agent tool group

**Tasks:**

- [ ] **Task 4.1**: Add sub-agent tool configuration
  - **Estimated Time**: 2 hours
  - **Dependencies**: Phase 3 complete
  - **Acceptance Criteria**:
    - [ ] config.json accepts "enabled_tool_groups"
    - [ ] ServerConfig passes to factory
    - [ ] Tool registration respects configuration

- [ ] **Task 4.2**: Create example sub-agent tool module
  - **Estimated Time**: 4 hours
  - **Dependencies**: Task 4.1
  - **Acceptance Criteria**:
    - [ ] `server/tools/sub_agent_tools/example.py` created
    - [ ] Implements `register_example_tools()` pattern
    - [ ] Returns tool count
    - [ ] Can be enabled via config

- [ ] **Task 4.3**: Test tool count monitoring
  - **Estimated Time**: 2 hours
  - **Dependencies**: Task 4.2
  - **Acceptance Criteria**:
    - [ ] Enable 7 + 5 + 5 + 5 = 22 tools
    - [ ] Warning logged at startup
    - [ ] All tools work
    - [ ] Selective disable works

- [ ] **Task 4.4**: Performance testing with multiple tool sets
  - **Estimated Time**: 3 hours
  - **Dependencies**: Task 4.3
  - **Acceptance Criteria**:
    - [ ] Benchmark with 7, 15, 22, 30 tools
    - [ ] Measure tool call latency
    - [ ] Verify warning threshold appropriate
    - [ ] Document performance characteristics

- [ ] **Task 4.5**: Create sub-agent development guide
  - **Estimated Time**: 3 hours
  - **Dependencies**: Tasks 4.1-4.4
  - **Acceptance Criteria**:
    - [ ] Document how to create sub-agent tool module
    - [ ] Document tool registration pattern
    - [ ] Document testing requirements
    - [ ] Document performance considerations

**Phase Deliverables:**
- Sub-agent infrastructure validated
- Example sub-agent tool module
- Performance characteristics documented
- Developer guide for sub-agents

**Validation Gate:**
- [ ] Sub-agent tools can be added in <30 minutes
- [ ] Tool count monitoring works
- [ ] Performance acceptable with 20+ tools
- [ ] Documentation clear and complete

---

## 🎯 MILESTONE TRACKING

| Milestone | Target Date | Status | Notes |
|-----------|------------|--------|-------|
| Phase 1 Complete | 2025-10-10 | ✅ Complete | New modules created |
| Phase 2 Complete | 2025-10-11 | ✅ Complete | Architecture wired |
| Phase 3 Complete | 2025-10-14 | ✅ Complete | Legacy code removed |
| Phase 4 Complete | 2025-10-17 | ⏳ Deferred | Sub-agents enabled (infrastructure ready) |
| Full Deployment | 2025-10-18 | ✅ Complete | Production ready (Phases 1-3) |

---

## ⚠️ RISKS & MITIGATION

### Risk 1: Breaking Changes to Existing Tools
**Likelihood:** Medium  
**Impact:** High  
**Mitigation Strategy:**
- Maintain backward compatibility throughout
- Extensive integration testing
- Phase 2 validation gate ensures no breakage
- Can rollback to previous commit if needed

### Risk 2: Performance Regression
**Likelihood:** Low  
**Impact:** Medium  
**Mitigation Strategy:**
- Benchmark before and after
- Lazy loading where possible
- Profile startup time
- Validate in Phase 2 gate

### Risk 3: Configuration Migration Issues
**Likelihood:** Medium  
**Impact:** Low  
**Mitigation Strategy:**
- Graceful fallback to defaults
- Validation with clear error messages
- Test with various config.json formats
- Document migration in CHANGELOG

### Risk 4: File Watcher Not Triggering
**Likelihood:** Low  
**Impact:** Medium  
**Mitigation Strategy:**
- Unit tests for watcher with mocked filesystem
- Integration tests with real file changes
- Manual testing during Phase 2
- Validate paths passed correctly

### Risk 5: Tool Count Limit Reached Too Easily
**Likelihood:** Medium  
**Impact:** Low  
**Mitigation Strategy:**
- Selective loading by default (7 tools)
- Warning logged at 20 tools
- Performance testing validates threshold
- Users control enabled_groups

---

## 📋 TASK DEPENDENCIES

```
Phase 1:
  Task 1.1 (models/) → Task 1.2 (config/)
                    → Task 1.3 (monitoring/)
                    → Task 1.5 (factory)
  
  Task 1.4 (tools/) → Task 1.5 (factory)

Phase 2:
  Phase 1 Complete → Task 2.1 (__main__.py)
                  → Task 2.2 (core engines)
                  → Task 2.3 (integration tests)
                  → Task 2.4 (custom config test)

Phase 3:
  Phase 2 Complete → Task 3.1 (remove old config)
                  → Task 3.2 (remove old tools)
                  → Task 3.3 (move models)
                  → Task 3.4 (clean watcher)
                  → Task 3.5 (docs)

Phase 4:
  Phase 3 Complete → Task 4.1 (config)
                  → Task 4.2 (example sub-agent)
                  → Task 4.3 (monitoring)
                  → Task 4.4 (performance)
                  → Task 4.5 (guide)
```

---

**Total Estimated Time: 58 hours (~10 working days)**  
**Target Completion: 2 weeks (with buffer for issues)**

