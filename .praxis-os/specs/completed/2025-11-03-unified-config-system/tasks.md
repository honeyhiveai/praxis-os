# Implementation Tasks

**Project:** Unified Configuration System with Pydantic v2  
**Date:** 2025-11-03  
**Status:** Draft - Pending Approval

---

## Time Estimates

- **Phase 1:** 8-10 hours (Create Pydantic schemas in parallel)
- **Phase 2:** 6-8 hours (Update consumers to use new config)
- **Phase 3:** 3-4 hours (Remove old system, cleanup)
- **Phase 4:** 4-6 hours (Testing and validation)
- **Total:** **21-28 hours** (3-4 days)

---

## Phase 1: Create Pydantic Schemas (Parallel)

**Objective:** Create complete Pydantic v2 schema hierarchy without breaking existing system. This phase is parallel-safe - old dict-based config continues to work.

**Estimated Duration:** 8-10 hours

**Milestone:** Pydantic models exist and validate correctly, but aren't used yet.

### Phase 1 Tasks

#### Task 1.1: Add Pydantic v2 Dependency
- **Description:** Add pydantic>=2.0 to requirements.txt
- **Estimated Time:** 15 minutes
- **Dependencies:** None
- **Acceptance Criteria:**
  - pydantic>=2.0 in ouroboros/requirements.txt
  - pip install succeeds
  - Python can import pydantic
- **Files Changed:**
  - `ouroboros/requirements.txt`

---

#### Task 1.2: Create Base Configuration Module
- **Description:** Create base.py with enums and BaseConfig
- **Estimated Time:** 1 hour
- **Dependencies:** Task 1.1
- **Acceptance Criteria:**
  - `ouroboros/models/config/base.py` exists
  - Contains TransportMode, LogLevel, Device, FusionMethod enums
  - Contains BaseConfig with ConfigDict(frozen=True, extra="forbid")
  - All enums inherit from (str, Enum)
- **Files Created:**
  - `ouroboros/models/config/__init__.py`
  - `ouroboros/models/config/base.py`

---

#### Task 1.3: Create Index Configuration Schemas
- **Description:** Create indexes.py with all index-related configs
- **Estimated Time:** 3-4 hours
- **Dependencies:** Task 1.2
- **Acceptance Criteria:**
  - `ouroboros/models/config/indexes.py` exists
  - Contains VectorConfig, FTSConfig, CacheConfig, MetadataConfig
  - Contains StandardsIndexConfig, CodeIndexConfig, ASTIndexConfig, LanguageConfig
  - Contains IndexesConfig (container)
  - All Field() constraints implemented (ge, le, pattern, etc.)
  - Cross-field validators implemented (chunk_overlap < chunk_size)
  - source_paths validation (no empty strings)
- **Files Created:**
  - `ouroboros/models/config/indexes.py`

---

#### Task 1.4: Create Root MCPConfig Model
- **Description:** Create mcp_config.py with MCPConfig root model
- **Estimated Time:** 2 hours
- **Dependencies:** Task 1.3
- **Acceptance Criteria:**
  - `ouroboros/models/config/mcp_config.py` exists
  - Contains MCPConfig with version, server, indexes, retrieval, monitoring fields
  - Implements from_yaml() classmethod
  - Implements to_yaml() method
  - Version field validates pattern (^\d+\.\d+$)
- **Files Created:**
  - `ouroboros/models/config/mcp_config.py`

---

#### Task 1.5: Create Example config/mcp.yaml
- **Description:** Create example unified config file
- **Estimated Time:** 1 hour
- **Dependencies:** Task 1.4
- **Acceptance Criteria:**
  - `config/mcp.yaml.example` exists (or config/mcp.yaml if new install)
  - Contains all sections (server, indexes, retrieval, monitoring)
  - Includes comments explaining each setting
  - Loads successfully with MCPConfig.from_yaml()
  - Validates successfully (no ValidationError)
- **Files Created:**
  - `config/mcp.yaml.example`

---

#### Task 1.6: Write Pydantic Model Unit Tests
- **Description:** Test all Pydantic models and validators
- **Estimated Time:** 2-3 hours
- **Dependencies:** Task 1.5
- **Acceptance Criteria:**
  - `tests/unit/test_config_models.py` exists
  - Tests all Field constraints (ge, le, pattern)
  - Tests cross-field validators (chunk_overlap < chunk_size)
  - Tests unknown field rejection (extra="forbid")
  - Tests validation error messages
  - Tests MCPConfig.from_yaml() success and failure cases
  - Coverage >= 90% for all config models
- **Files Created:**
  - `tests/unit/test_config_models.py`
  - `tests/fixtures/configs/` (test config files)

---

## Phase 2: Update Consumers to Use New Config

**Objective:** Refactor IndexManager, StandardsIndex, and ServerFactory to accept and use Pydantic config models instead of raw dicts.

**Estimated Duration:** 6-8 hours

**Milestone:** All components use type-safe config access (config.indexes.standards.vector.model), no dict["key"] access.

### Phase 2 Tasks

#### Task 2.1: Update IndexManager Constructor
- **Description:** Change IndexManager to accept IndexesConfig (Pydantic model)
- **Estimated Time:** 1.5 hours
- **Dependencies:** Phase 1 complete
- **Acceptance Criteria:**
  - `IndexManager.__init__()` accepts `config: IndexesConfig` parameter
  - `_init_indexes()` uses `self.config.standards`, `self.config.code`, `self.config.ast`
  - Type-safe access throughout (no dict["key"])
  - Existing tests updated to use Pydantic models
  - All existing functionality works identically
- **Files Changed:**
  - `ouroboros/server/indexes/index_manager.py`
  - `tests/unit/test_index_manager.py`

---

#### Task 2.2: Update StandardsIndex Constructor
- **Description:** Change StandardsIndex to accept StandardsIndexConfig
- **Estimated Time:** 1.5 hours
- **Dependencies:** Task 2.1
- **Acceptance Criteria:**
  - `StandardsIndex.__init__()` accepts `config: StandardsIndexConfig` parameter
  - All config access uses type-safe properties: `config.vector.model`, `config.fts.stem`, etc.
  - No dict.get() calls remain
  - Existing tests updated
  - Search functionality unchanged
- **Files Changed:**
  - `ouroboros/server/indexes/standards_index.py`
  - `tests/unit/test_standards_index.py`

---

#### Task 2.3: Update CodeIndex Constructor
- **Description:** Change CodeIndex to accept CodeIndexConfig
- **Estimated Time:** 1 hour
- **Dependencies:** Task 2.1
- **Acceptance Criteria:**
  - `CodeIndex.__init__()` accepts `config: CodeIndexConfig` parameter
  - Type-safe config access throughout
  - Existing tests updated
  - Search functionality unchanged
- **Files Changed:**
  - `ouroboros/server/indexes/code_index.py` (if exists)
  - `tests/unit/test_code_index.py` (if exists)

---

#### Task 2.4: Update ASTIndex Constructor
- **Description:** Change ASTIndex to accept ASTIndexConfig
- **Estimated Time:** 1 hour
- **Dependencies:** Task 2.1
- **Acceptance Criteria:**
  - `ASTIndex.__init__()` accepts `config: ASTIndexConfig` parameter
  - Type-safe access to `config.languages`, `config.node_types`, `config.auto_install_parsers`
  - Existing tests updated
  - Tree-sitter functionality unchanged
- **Files Changed:**
  - `ouroboros/server/indexes/ast_index.py`
  - `tests/unit/test_ast_index.py`

---

#### Task 2.5: Update ServerFactory to Load Unified Config
- **Description:** Refactor ServerFactory to use MCPConfig.from_yaml()
- **Estimated Time:** 2 hours
- **Dependencies:** Tasks 2.1-2.4
- **Acceptance Criteria:**
  - ServerFactory loads config using `MCPConfig.from_yaml(config_path)`
  - Catches ValidationError, displays user-friendly error messages
  - Passes Pydantic models to components (not dicts)
  - IndexManager receives `config.indexes`
  - RAGEngine receives `config.retrieval` (if applicable)
  - Existing server startup unchanged from user perspective
- **Files Changed:**
  - `ouroboros/server/factory.py`
  - `ouroboros/__main__.py` (error handling)
  - `tests/integration/test_server_startup.py`

---

#### Task 2.6: Update RAGEngine Integration
- **Description:** Update RAGEngine to work with new config system
- **Estimated Time:** 1-2 hours
- **Dependencies:** Task 2.5
- **Acceptance Criteria:**
  - RAGEngine receives IndexManager with Pydantic-backed config
  - No direct config access in RAGEngine (delegates to IndexManager)
  - Existing search functionality unchanged
  - Integration tests pass
- **Files Changed:**
  - `ouroboros/rag_engine.py`
  - `tests/integration/test_rag_engine.py`

---

## Phase 3: Remove Old Config System

**Objective:** Delete old dataclass-based config and consolidate to single config/mcp.yaml file.

**Estimated Duration:** 3-4 hours

**Milestone:** Single source of truth (config/mcp.yaml), all old config code removed.

### Phase 3 Tasks

#### Task 3.1: Create config/mcp.yaml Migration Script
- **Description:** Script to convert old index_config.yaml to new mcp.yaml
- **Estimated Time:** 1.5 hours
- **Dependencies:** Phase 2 complete
- **Acceptance Criteria:**
  - `scripts/migrate_config.py` exists
  - Reads old `config/index_config.yaml`
  - Generates new `config/mcp.yaml` with correct structure
  - Validates output using MCPConfig.from_yaml()
  - Includes dry-run mode
  - Clear migration instructions in script docstring
- **Files Created:**
  - `scripts/migrate_config.py`
  - `docs/config-migration-guide.md`

---

#### Task 3.2: Delete Old Config Dataclasses
- **Description:** Remove old models/config.py file
- **Estimated Time:** 30 minutes
- **Dependencies:** Task 3.1, all consumers updated
- **Acceptance Criteria:**
  - `ouroboros/models/config.py` deleted (old dataclasses)
  - All imports removed from other files
  - No references to old RAGConfig, MCPConfig (old), ServerConfig (old)
  - Tests pass without old config classes
- **Files Deleted:**
  - `ouroboros/models/config.py` (old file)
- **Files Changed:**
  - Any files importing from old config.py (should be none)

---

#### Task 3.3: Deprecate Old index_config.yaml
- **Description:** Add deprecation warning for old config format
- **Estimated Time:** 1 hour
- **Dependencies:** Task 3.2
- **Acceptance Criteria:**
  - ServerFactory detects old `config/index_config.yaml`
  - Logs clear deprecation warning with migration instructions
  - Suggests running `scripts/migrate_config.py`
  - Server still works with old config (graceful degradation)
  - Warning visible in logs and stderr
- **Files Changed:**
  - `ouroboros/server/factory.py` (add fallback logic)

---

#### Task 3.4: Update Documentation
- **Description:** Update all docs to reference new config system
- **Estimated Time:** 1-1.5 hours
- **Dependencies:** Task 3.3
- **Acceptance Criteria:**
  - README.md updated with config/mcp.yaml instructions
  - Configuration examples use new format
  - Migration guide added
  - All references to old config files removed
  - JSON Schema generation documented
- **Files Changed:**
  - `README.md`
  - `docs/configuration.md` (if exists)
  - `docs/config-migration-guide.md`

---

## Phase 4: Testing and Validation

**Objective:** Comprehensive testing of new config system and validation of all requirements.

**Estimated Duration:** 4-6 hours

**Milestone:** All tests pass, requirements validated, system ready for production.

### Phase 4 Tasks

#### Task 4.1: Write Integration Tests
- **Description:** End-to-end tests for config loading and server startup
- **Estimated Time:** 2 hours
- **Dependencies:** Phase 3 complete
- **Acceptance Criteria:**
  - `tests/integration/test_config_integration.py` exists
  - Tests loading valid config
  - Tests loading invalid config (various validation errors)
  - Tests server startup with new config
  - Tests all index types initialize correctly
  - Tests config immutability (frozen=True)
- **Files Created:**
  - `tests/integration/test_config_integration.py`

---

#### Task 4.2: Write Performance Tests
- **Description:** Validate config load performance (<100ms)
- **Estimated Time:** 1.5 hours
- **Dependencies:** Task 4.1
- **Acceptance Criteria:**
  - `tests/performance/test_config_performance.py` exists
  - Tests YAML load time (<20ms)
  - Tests Pydantic validation time (<80ms)
  - Tests total config load time (<100ms)
  - Tests property access time (<1μs)
  - Tests memory footprint (<50KB)
  - Uses pytest.mark.performance
- **Files Created:**
  - `tests/performance/test_config_performance.py`

---

#### Task 4.3: Write Security Tests
- **Description:** Validate security controls (input validation, path traversal)
- **Estimated Time:** 1.5 hours
- **Dependencies:** Task 4.1
- **Acceptance Criteria:**
  - `tests/security/test_config_security.py` exists
  - Tests type confusion prevention
  - Tests path traversal prevention
  - Tests resource exhaustion prevention (chunk_size limits)
  - Tests unknown field rejection
  - Uses pytest.mark.security
- **Files Created:**
  - `tests/security/test_config_security.py`

---

#### Task 4.4: Validate All Requirements
- **Description:** Manual validation checklist for all functional requirements
- **Estimated Time:** 1-2 hours
- **Dependencies:** Tasks 4.1-4.3
- **Acceptance Criteria:**
  - All 12 functional requirements (FR-001 through FR-012) validated
  - All 8 non-functional requirement categories validated
  - Evidence documented for each requirement
  - Traceability matrix updated (requirements → tests → code)
  - No failing tests
- **Deliverable:**
  - `VALIDATION_RESULTS.md` documenting all requirement validations

---

#### Task 4.5: Run Full Test Suite
- **Description:** Execute complete test suite and validate coverage
- **Estimated Time:** 30 minutes
- **Dependencies:** Task 4.4
- **Acceptance Criteria:**
  - `pytest` runs all tests successfully
  - Test coverage >= 90% for config modules
  - Test coverage >= 80% overall
  - No linter errors (pylint, ruff)
  - No type errors (mypy --strict)
  - Performance tests pass (timing requirements met)
  - Security tests pass (validation controls work)
- **Commands:**
  ```bash
  pytest tests/ -v --cov=ouroboros --cov-report=html
  pylint ouroboros/
  mypy ouroboros/ --strict
  ```

---

## Dependencies Graph

```
Phase 1: Create Schemas (Parallel)
├── Task 1.1: Add Pydantic Dependency
├── Task 1.2: Create Base Config     [depends on 1.1]
├── Task 1.3: Create Index Configs   [depends on 1.2]
├── Task 1.4: Create Root Config     [depends on 1.3]
├── Task 1.5: Create Example YAML    [depends on 1.4]
└── Task 1.6: Write Model Tests      [depends on 1.5]

Phase 2: Update Consumers
├── Task 2.1: Update IndexManager    [depends on Phase 1]
├── Task 2.2: Update StandardsIndex  [depends on 2.1]
├── Task 2.3: Update CodeIndex       [depends on 2.1]
├── Task 2.4: Update ASTIndex        [depends on 2.1]
├── Task 2.5: Update ServerFactory   [depends on 2.1-2.4]
└── Task 2.6: Update RAGEngine       [depends on 2.5]

Phase 3: Remove Old System
├── Task 3.1: Migration Script       [depends on Phase 2]
├── Task 3.2: Delete Old Dataclasses [depends on 3.1]
├── Task 3.3: Deprecate Old YAML     [depends on 3.2]
└── Task 3.4: Update Documentation   [depends on 3.3]

Phase 4: Testing
├── Task 4.1: Integration Tests      [depends on Phase 3]
├── Task 4.2: Performance Tests      [depends on 4.1]
├── Task 4.3: Security Tests         [depends on 4.1]
├── Task 4.4: Validate Requirements  [depends on 4.1-4.3]
└── Task 4.5: Run Full Suite         [depends on 4.4]
```

---

## Critical Path

The critical path (longest sequence of dependent tasks):

1. Task 1.1 → 1.2 → 1.3 → 1.4 → 1.5 (Phase 1: 8 hours)
2. Task 2.1 → 2.5 (Phase 2: 3.5 hours)
3. Task 3.1 → 3.2 → 3.3 → 3.4 (Phase 3: 4.5 hours)
4. Task 4.1 → 4.4 → 4.5 (Phase 4: 3.5 hours)

**Total Critical Path:** ~19.5 hours (~2.5 days)

**Parallelizable Tasks:**
- Phase 1: Task 1.6 (tests) can start after 1.5
- Phase 2: Tasks 2.2, 2.3, 2.4 can run in parallel after 2.1
- Phase 4: Tasks 4.2, 4.3 can run in parallel after 4.1

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pydantic validation too slow | Low | Medium | Profiling + optimization (lazy defaults) |
| Breaking changes to existing code | Medium | High | Phase 1 is parallel-safe, thorough testing |
| Complex migration for users | Medium | Medium | Migration script + clear docs + deprecation warnings |
| Incomplete test coverage | Low | Medium | Automated coverage checks (>=90% target) |
| Validation error messages unclear | Low | High | Extensive testing of error cases + user feedback |

---

## Success Criteria

**Phase 1:**
- ✅ All Pydantic models exist and validate
- ✅ Example config loads successfully
- ✅ Unit tests pass with >=90% coverage

**Phase 2:**
- ✅ All components use type-safe config access
- ✅ No dict["key"] access remains
- ✅ Server starts and functions identically

**Phase 3:**
- ✅ Old config system removed
- ✅ Single config/mcp.yaml file
- ✅ Migration script works
- ✅ Documentation updated

**Phase 4:**
- ✅ All tests pass (unit, integration, performance, security)
- ✅ Coverage >= 90% for config code, >= 80% overall
- ✅ All requirements validated
- ✅ No linter or type errors

---

## Notes

- **Backwards Compatibility:** Phase 1 is fully parallel-safe. Old dict-based config continues working until Phase 3.
- **Testing Strategy:** Write tests alongside implementation (each task includes test updates).
- **Performance:** Config load happens once at startup, so 100ms target is easily achievable.
- **Documentation:** Update docs continuously, final pass in Phase 3.

---

**Status:** Draft - Awaiting Approval  
**Last Updated:** 2025-11-03  
**Next:** Review and approve for implementation

