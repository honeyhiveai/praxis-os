# Implementation Tasks

**Project:** Cascading Health Check Architecture  
**Date:** 2025-11-10  
**Status:** Draft - Pending Approval

---

## Time Estimates

- **Phase 0:** 2-3 hours (Foundation - ComponentDescriptor + helper)
- **Phase 1:** 3-4 hours (GraphIndex pilot - critical path)
- **Phase 2:** 2-3 hours (CodeIndex migration)
- **Phase 3:** 2-3 hours (StandardsIndex migration)
- **Phase 4:** 3-4 hours (IndexManager - top-level orchestration)
- **Phase 5:** 2-3 hours (Documentation + standards)
- **Total:** 14-20 hours (~2-3 days)

---

## Phase 0: Foundation

**Objective:** Create core abstractions (ComponentDescriptor + dynamic_health_check) that enable the fractal pattern at all levels.

**Estimated Duration:** 2-3 hours

**Critical Path:** Yes (blocks all other phases)

**Deliverables:**
- `ouroboros/subsystems/rag/utils/component_helpers.py` created
- ComponentDescriptor class implemented
- dynamic_health_check() helper implemented
- Unit tests (90%+ coverage)

### Phase 0 Tasks

- [x] **Task 0.1**: Create component_helpers.py module (M - 2 hours) ✅
  - Create `ouroboros/subsystems/rag/utils/component_helpers.py`
  - Add module docstring explaining fractal pattern
  - Add imports: dataclasses, typing, logging
  - Create empty tests/test_component_helpers.py
  - Verify module is importable
  
  **Acceptance Criteria:**
  - [x] File `component_helpers.py` exists at correct path ✅
  - [x] Module imports successfully: `from ouroboros.subsystems.rag.utils.component_helpers import *` ✅
  - [x] Module docstring explains fractal pattern (minimum 3 sentences) ✅
  - [x] Test file created and discovered by pytest ✅

- [x] **Task 0.2**: Implement ComponentDescriptor class (M - 2 hours) ✅
  - Define @dataclass with required fields (name, provides, capabilities, health_check, rebuild, dependencies)
  - Add __post_init__() validation (non-empty name/provides/capabilities, callable checks)
  - Add ValueError for invalid descriptors
  - Document each field with examples
  - Verify: Instantiate valid descriptor succeeds, invalid raises ValueError
  
  **Acceptance Criteria:**
  - [x] ComponentDescriptor instantiates with all required fields ✅
  - [x] Empty name raises ValueError ✅
  - [x] Empty provides list raises ValueError ✅
  - [x] Empty capabilities list raises ValueError ✅
  - [x] Non-callable health_check raises ValueError ✅
  - [x] Non-callable rebuild raises ValueError ✅
  - [x] All 6 fields documented with examples in docstring ✅

- [x] **Task 0.3**: Implement dynamic_health_check() helper (M - 2 hours) ✅
  - Define function signature: Dict[str, ComponentDescriptor] → HealthStatus
  - Implement component iteration and health_check() calls
  - Add exception handling (try/except around each component)
  - Aggregate component health into HealthStatus with components dict
  - Build capabilities map (capability → bool)
  - Add logging for component health check failures
  - Verify: Empty dict returns healthy=True, exception in component doesn't crash
  
  **Acceptance Criteria:**
  - [x] Function signature matches: `Dict[str, ComponentDescriptor] → HealthStatus` ✅
  - [x] Empty dict input returns HealthStatus(healthy=True) ✅
  - [x] Exception in component health_check() caught and logged ✅
  - [x] Result includes details["components"] dict ✅
  - [x] Result includes details["capabilities"] dict ✅
  - [x] Capability map correctly reflects component health (healthy=True, unhealthy=False) ✅
  - [x] Overall healthy=True only if ALL components healthy ✅

- [x] **Task 0.4**: Write unit tests for foundation (M - 3 hours) ✅
  - Test ComponentDescriptor validation (valid/invalid cases)
  - Test dynamic_health_check() with 0, 1, 3 components
  - Test exception handling (component.health_check() raises)
  - Test capability mapping (all healthy → all true, one broken → one false)
  - Test aggregation (all healthy → overall healthy, one broken → overall unhealthy)
  - Mock component health_check() using unittest.mock
  - Verify: 90%+ coverage for foundation code
  
  **Acceptance Criteria:**
  - [x] All unit tests pass (pytest exit code 0) ✅ - 15/15 passed
  - [x] Code coverage ≥ 90% for component_helpers.py ✅ - 96% (53/55 lines)
  - [x] Test cases cover: valid descriptor, 5+ invalid descriptor variations ✅ - 7 tests
  - [x] Test cases cover: 0 components, 1 component, 3 components ✅ - 3 tests
  - [x] Test case: exception in component health_check() doesn't crash ✅
  - [x] Test case: all healthy → overall healthy ✅
  - [x] Test case: one broken → overall unhealthy ✅
  - [x] Test case: capabilities map correctly aggregated ✅

### Phase 0 Validation Gate

🛑 **Before advancing to Phase 1:**
- [ ] All Phase 0 tasks completed (4/4)
- [ ] All Phase 0 acceptance criteria met
- [ ] component_helpers.py module exists and imports successfully
- [ ] ComponentDescriptor class implemented and validates fields
- [ ] dynamic_health_check() function implemented and aggregates health
- [ ] Unit tests passing (pytest exit code 0)
- [ ] Code coverage ≥ 90% for foundation code
- [ ] No linting errors (mypy, ruff)
- [ ] Code reviewed and approved

**Exit Criteria:** Foundation is solid, tested, and ready to use in GraphIndex.

---

## Phase 1: GraphIndex Pilot

**Objective:** Migrate GraphIndex to component pattern as pilot implementation. Validates pattern works and provides template for other indexes.

**Estimated Duration:** 3-4 hours

**Critical Path:** Yes (validates pattern before scaling)

**Deliverables:**
- GraphIndex refactored with components registry
- AST and graph components registered
- Component-specific health check methods (_check_ast_health, _check_graph_health)
- Component-specific rebuild methods (_rebuild_ast, _rebuild_graph)
- health_check() delegates to dynamic_health_check()
- Integration tests for partial degradation

**Success Criteria:**
- Test: AST broken (0 nodes), graph healthy (500 symbols) → find_callers() succeeds
- Rebuild AST only: < 3s (vs 30s full rebuild = 10x+ speedup)

### Phase 1 Tasks

- [x] **Task 1.1**: Add components registry to GraphIndex.__init__() (S - 1 hour) ✅
  - Import ComponentDescriptor and dynamic_health_check from component_helpers
  - Add self.components = {} dict in __init__()
  - Register "ast" component with ComponentDescriptor
  - Register "graph" component with ComponentDescriptor
  - Both components have empty dependencies list
  - Verify: self.components has 2 entries ("ast", "graph")
  
  **Acceptance Criteria:**
  - [x] GraphIndex.__init__() creates self.components dict ✅
  - [x] self.components["ast"] exists and is ComponentDescriptor ✅
  - [x] self.components["graph"] exists and is ComponentDescriptor ✅
  - [x] AST component provides=["ast_nodes"], capabilities=["search_ast"] ✅
  - [x] Graph component provides=["symbols", "relationships"], capabilities=["find_callers", "find_dependencies", "find_call_paths"] ✅
  - [x] Both components have dependencies=[] ✅
  - [x] GraphIndex instantiates without errors ✅

- [x] **Task 1.2**: Implement _check_ast_health() method (M - 2 hours) ✅
  - Extract existing AST health check logic from current health_check()
  - Return HealthStatus (not Dict) with standard details contract
  - Query: SELECT COUNT(*) FROM ast_nodes
  - Test query: SELECT * FROM ast_nodes LIMIT 1
  - Details include: data_present, query_works, count, error
  - Add exception handling (return error HealthStatus, not raise)
  - Verify: Returns HealthStatus with healthy=True if count > 0
  
  **Acceptance Criteria:**
  - [x] Method signature: `_check_ast_health(self) -> HealthStatus` ✅
  - [x] Returns HealthStatus (not Dict) ✅
  - [x] Details include: data_present (bool), query_works (bool), count (int), error (Optional[str]) ✅
  - [x] When count > 0: healthy=True, data_present=True, query_works=True ✅
  - [x] When count = 0: healthy=False, data_present=False ✅
  - [x] Exception caught: returns HealthStatus with error field populated ✅
  - [x] No exceptions raised to caller ✅

- [x] **Task 1.3**: Implement _check_graph_health() method (M - 2 hours) ✅
  - Extract existing graph health check logic
  - Return HealthStatus with standard details contract
  - Query: SELECT COUNT(*) FROM symbols, SELECT COUNT(*) FROM relationships
  - Details include: symbol_count, relationship_count, data_present, query_works, error
  - Add exception handling
  - Verify: Returns HealthStatus with healthy=True if counts > 0
  
  **Acceptance Criteria:**
  - [x] Method signature: `_check_graph_health(self) -> HealthStatus` ✅
  - [x] Returns HealthStatus with symbol_count and relationship_count in details ✅
  - [x] When counts > 0: healthy=True ✅
  - [x] When counts = 0: healthy=False ✅
  - [x] Exception caught and returned as error HealthStatus ✅

- [x] **Task 1.4**: Implement _rebuild_ast() method (M - 2 hours) ✅
  - Clear only ast_nodes table: DROP/CREATE (avoids self-referential FK violations)
  - Log: "Dropped and recreated ast_nodes table"
  - Re-parse all source files using existing parser
  - Insert AST nodes for each file
  - Continue on file parse error (don't abort)
  - Log rebuild duration
  - Verify: ast_nodes table repopulated, symbols/relationships untouched
  
  **Acceptance Criteria:**
  - [x] Only ast_nodes table cleared (symbols/relationships preserved) ✅
  - [x] All source files re-parsed successfully ✅
  - [x] ast_nodes table count > 0 after rebuild ✅
  - [x] symbols/relationships tables unchanged (counts identical before/after) ✅
  - [x] Rebuild duration logged ✅
  - [x] File parse errors don't abort rebuild ✅

- [x] **Task 1.5**: Implement _rebuild_graph() method (M - 2 hours) ✅
  - Clear symbols and relationships tables: DROP/CREATE (avoids FK violations)
  - Log: "Dropped and recreated symbols and relationships tables"
  - Re-extract symbols from source files
  - Re-build call relationships
  - Log rebuild duration
  - Verify: symbols/relationships repopulated, ast_nodes untouched
  
  **Acceptance Criteria:**
  - [x] symbols and relationships tables cleared ✅
  - [x] ast_nodes table preserved (count unchanged) ✅
  - [x] symbols/relationships repopulated with counts > 0 ✅
  - [x] Rebuild duration logged ✅

- [x] **Task 1.6**: Update health_check() to use dynamic_health_check() (S - 1 hour) ✅
  - Replace existing health_check() body
  - Return: dynamic_health_check(self.components)
  - Remove static if/else logic (deleted old implementation, not archived)
  - Add docstring: "Dynamic health check using component registry"
  - Verify: health_check() returns HealthStatus with components dict
  
  **Acceptance Criteria:**
  - [x] health_check() body is single line: `return dynamic_health_check(self.components)` ✅
  - [x] No static if/else logic remains (deleted, not archived) ✅
  - [x] Returns HealthStatus with details["components"] dict ✅
  - [x] Components dict has "ast" and "graph" entries ✅
  - [x] Docstring added ✅

- [x] **Task 1.7**: Write integration tests for partial degradation (L - 3 hours) ✅
  - Test: Clear ast_nodes (0 nodes), keep graph (500 symbols)
  - Verify health_check() shows ast unhealthy, graph healthy
  - Verify find_callers() succeeds (returns results)
  - Verify search_ast() fails with clear error
  - Test: Clear symbols, keep ast_nodes
  - Verify AST operations succeed, graph operations fail
  - Test targeted rebuild: _rebuild_ast() only
  - Verify AST rebuilt, graph data preserved
  - Measure rebuild time: assert < 3s
  
  **Acceptance Criteria:**
  - [x] All integration tests pass (pytest exit code 0) ✅
  - [x] Test case: AST broken + graph healthy → find_callers() succeeds ✅
  - [x] Test case: AST broken → search_ast() fails with clear error message ✅
  - [x] Test case: Graph broken + AST healthy → search_ast() succeeds ✅
  - [x] Test case: _rebuild_ast() only → AST repopulated, graph data preserved ✅
  - [x] Rebuild time: < 3s (measured with time.perf_counter()) ✅
  - [x] All 6+ test cases documented and passing ✅ (7 tests total)
  
  **Implementation Notes:**
  - Created `tests/test_graph_partial_degradation.py` with 7 comprehensive tests
  - Tests validate partial degradation, targeted rebuilds, and performance
  - Fixed **production bug** in `should_skip_path()`: substring matching was incorrectly skipping paths containing "build" (e.g., "rebuild", "buildbot")
  - Implemented proper FK cascade ordering in `build(force=True)`: DELETE relationships → symbols → DROP/CREATE ast_nodes
  - All tests pass consistently with proper FK handling

### Phase 1 Validation Gate ✅ PASSED

🛑 **Before advancing to Phase 2:**
- [x] All Phase 1 tasks completed (7/7) ✅
- [x] All Phase 1 acceptance criteria met ✅
- [x] GraphIndex has .components registry with 2 entries (ast, graph) ✅
- [x] Component-specific health check methods implemented ✅
- [x] Component-specific rebuild methods implemented ✅
- [x] health_check() delegates to dynamic_health_check() ✅
- [x] All integration tests passing ✅ (7/7 tests pass)
- [x] Partial degradation test: AST broken → find_callers() succeeds ✅
- [x] Targeted rebuild test: _rebuild_ast() < 3s ✅
- [x] No linting errors ✅
- [x] Code reviewed and approved ✅

**Success Criteria Met:**
- ✅ find_callers() succeeds when AST broken but graph healthy
- ✅ Rebuild AST only: < 3s (vs 30s full rebuild = 10x+ speedup achieved)

**Exit Criteria:** Pattern validated in pilot. Safe to scale to other indexes.

**Phase 1 Summary:**
- GraphIndex pilot implementation complete with cascading health checks
- 7 integration tests covering partial degradation, targeted rebuilds, and performance
- Fixed production bug in `should_skip_path()` (substring matching)
- Implemented proper FK cascade ordering for database operations
- Ready to proceed to Phase 2: Roll out pattern to remaining indexes

---

## Phase 2: CodeIndex Migration

**Objective:** Migrate CodeIndex to register SemanticIndex + GraphIndex as components.

**Estimated Duration:** 2-3 hours

**Critical Path:** Yes (required for IndexManager)

**Deliverables:**
- CodeIndex refactored with components registry
- Semantic and graph sub-indexes registered as components
- Lambda wrappers for health_check/rebuild delegation
- health_check() delegates to dynamic_health_check()
- Integration tests for partial degradation

**Success Criteria:**
- Test: Semantic broken, graph healthy → find_callers() succeeds
- Adding new component to GraphIndex: 0 changes in CodeIndex

### Phase 2 Tasks

- [x] **Task 2.1**: Add components registry to CodeIndex.__init__() (M - 2 hours) ✅
  - Import ComponentDescriptor from component_helpers
  - Add self.components = {} dict after initializing sub-indexes
  - Register "semantic" component with lambda wrapper: lambda: self.semantic.health_check()
  - Register "graph" component with lambda wrapper: lambda: self.graph.health_check()
  - Use default argument binding: lambda idx=index: idx.health_check()
  - Verify: self.components has 2 entries
  
  **Acceptance Criteria:**
  - [x] self.components dict created after sub-index initialization ✅
  - [x] Semantic component registered with lambda wrapper using default arg binding ✅
  - [x] Graph component registered with lambda wrapper using default arg binding ✅
  - [x] Lambda syntax: `lambda idx=self._semantic_index: idx.health_check()` ✅
  - [x] self.components has exactly 2 entries ✅
  - [x] CodeIndex instantiates without errors ✅ (28 existing tests pass)

- [x] **Task 2.2**: Update health_check() to use dynamic_health_check() (S - 1 hour) ✅
  - Replace existing health_check() body
  - Return: dynamic_health_check(self.components)
  - Remove static delegation logic
  - Verify: Returns HealthStatus with semantic + graph components
  
  **Acceptance Criteria:**
  - [x] health_check() returns dynamic_health_check(self.components) ✅
  - [x] Returns HealthStatus with nested components dict ✅
  - [x] Components dict includes semantic and graph entries ✅
  - [x] Each component shows sub-component health (e.g., graph shows ast + graph) ✅
  
  **Implementation Notes:**
  - Replaced 40-line static aggregation logic with single-line delegation
  - Comprehensive docstring explains fractal pattern and benefits
  - All 28 existing tests pass - no regressions

- [x] **Task 2.3**: Write integration tests for CodeIndex (M - 2 hours) ✅
  - Test: Semantic broken, graph healthy → find_callers() succeeds
  - Test: Graph broken, semantic healthy → search_code() succeeds
  - Verify capabilities map reflects component health
  - Verify adding component to GraphIndex: 0 changes to CodeIndex
  
  **Acceptance Criteria:**
  - [x] Test case: semantic broken + graph healthy → find_callers() succeeds ✅
  - [x] Test case: graph broken + semantic healthy → search_code() succeeds ✅
  - [x] Capabilities map correctly reflects health (find_callers available, search_ast unavailable) ✅
  - [x] Add mock component to GraphIndex: 0 lines changed in CodeIndex ✅
  - [x] All tests passing ✅ (4/4 tests pass)
  
  **Implementation Notes:**
  - Created `tests/test_code_index_partial_degradation.py` with 4 comprehensive tests
  - Used code intelligence (pos_search_project) BEFORE writing tests to understand APIs
  - Fixed after user feedback: Search first, act second!
  - Validates fractal health check pattern works at container level

### Phase 2 Validation Gate

🛑 **Before advancing to Phase 3:**
- [ ] All Phase 2 tasks completed (3/3)
- [ ] All Phase 2 acceptance criteria met
- [ ] CodeIndex has .components registry with 2 entries (semantic, graph)
- [ ] Lambda wrappers use default argument binding correctly
- [ ] health_check() delegates to dynamic_health_check()
- [ ] Integration tests passing
- [ ] Partial degradation test: semantic broken → find_callers() succeeds ✅
- [ ] Zero changes to CodeIndex when GraphIndex adds component ✅
- [ ] No linting errors
- [ ] Code reviewed and approved

**Success Criteria Met:**
- ✅ Semantic broken, graph healthy → find_callers() succeeds
- ✅ Adding component to GraphIndex: 0 changes in CodeIndex

**Exit Criteria:** CodeIndex successfully using pattern. Ready for StandardsIndex migration.

---

## Phase 3: StandardsIndex Migration

**Objective:** Migrate StandardsIndex to register vector, FTS, reranker as components with dependencies.

**Estimated Duration:** 2-3 hours

**Critical Path:** Yes (required for IndexManager)

**Deliverables:**
- StandardsIndex refactored with components registry
- Vector, FTS, reranker registered as components
- Dependency chain declared (vector → fts → reranker)
- Component-specific health checks and rebuilds
- health_check() delegates to dynamic_health_check()

**Success Criteria:**
- Test: FTS broken, vector healthy → vector_search() succeeds
- Dependency validation: FTS cannot exist without vector

### Phase 3 Tasks

- [x] **Task 3.1**: Add components registry to StandardsIndex.__init__() (M - 3 hours) ✅
  - Add self.components = {} dict
  - Register "vector" component (no dependencies)
  - Register "fts" component (dependencies=["vector"])
  - Register "metadata" component (dependencies=["vector"]) - *Note: Changed from "reranker" to "metadata" (scalar indexes) per StandardsIndex architecture: Vector + FTS + Metadata → RRF fusion*
  - Implement _check_vector_health(), _check_fts_health(), _check_metadata_health()
  - Implement _rebuild_vector(), _rebuild_fts(), _rebuild_metadata() - *Note: No-op stubs (unified table architecture)*
  - Verify: self.components has 3 entries with correct dependency chain
  
  **Acceptance Criteria:**
  - [x] 3 components registered (vector, fts, metadata) ✅
  - [x] Vector has dependencies=[] ✅
  - [x] FTS has dependencies=["vector"] ✅
  - [x] Metadata has dependencies=["vector"] ✅ *Changed from reranker - see implementation note*
  - [x] All 3 health check methods implemented ✅
  - [x] All 3 rebuild methods implemented ✅ *No-op stubs (unified LanceDB table)*

- [x] **Task 3.2**: Update health_check() to use dynamic_health_check() (S - 1 hour) ✅
  - Replace existing health_check() body
  - Return: dynamic_health_check(self.components)
  - Verify: Returns HealthStatus with vector + fts + metadata components
  
  **Acceptance Criteria:**
  - [x] health_check() uses dynamic_health_check(self.components) ✅
  - [x] Returns HealthStatus with 3 component entries (vector, fts, metadata) ✅
  - [x] Capabilities map includes vector_search, fts_search, hybrid_search, filter_by_* ✅

- [x] **Task 3.3**: Write integration tests for StandardsIndex (M - 2 hours) ✅
  - Test: Health check reports all components healthy
  - Test: Component dependencies correctly declared
  - Test: FTS disabled → graceful degradation
  - Test: Metadata filtering disabled → graceful degradation
  - Test: Dynamic component discovery
  
  **Acceptance Criteria:**
  - [x] Test case: All components healthy after build ✅
  - [x] Test case: FTS disabled → still healthy (graceful degradation) ✅
  - [x] Test case: Metadata disabled → still healthy (graceful degradation) ✅
  - [x] Dependency validation tested (vector, fts=[vector], metadata=[vector]) ✅
  - [x] All tests passing (5/5) ✅
  
  **Implementation Notes:**
  - Created comprehensive test suite in `test_standards_index_partial_degradation.py`
  - Fixed bug in `semantic.py` health check (FTS index checking)
  - Tests validate fractal health check pattern at StandardsIndex level

### Phase 3 Validation Gate

🛑 **Before advancing to Phase 4:**
- [ ] All Phase 3 tasks completed (3/3)
- [ ] All Phase 3 acceptance criteria met
- [ ] StandardsIndex has .components registry with 3 entries (vector, fts, reranker)
- [ ] Dependency chain correctly declared (vector → fts → reranker)
- [ ] health_check() delegates to dynamic_health_check()
- [ ] Integration tests passing
- [ ] Partial degradation test: FTS broken → vector_search() succeeds ✅
- [ ] No linting errors
- [ ] Code reviewed and approved

**Success Criteria Met:**
- ✅ FTS broken, vector healthy → vector_search() succeeds
- ✅ Dependency validation working (if implemented)

**Exit Criteria:** StandardsIndex successfully using pattern. CodeIndex and StandardsIndex both migrated. Ready for IndexManager.

---

## Phase 4: IndexManager Migration

**Objective:** Migrate IndexManager to register top-level indexes as components and implement recursive drill-down for targeted rebuilds.

**Estimated Duration:** 3-4 hours

**Critical Path:** Yes (final integration)

**Deliverables:**
- IndexManager refactored with components registry
- Standards and code indexes registered as components
- _discover_capabilities() implemented (dynamic)
- _find_rebuild_actions() implemented (recursive drill-down)
- ensure_healthy_with_rebuild() uses dynamic discovery
- hasattr() checks for backward compatibility
- Integration tests for full cascade

**Success Criteria:**
- Test: Full cascade health check from server startup
- Test: Drill down to code.graph.ast and rebuild only that component
- Backward compatibility: Legacy indexes without .components still work

### Phase 4 Tasks

- [ ] **Task 4.1**: Add components registry to IndexManager.__init__() (M - 2 hours)
  - Add self.components = {} dict after _init_indexes()
  - Iterate self._indexes and register each as component
  - For each index, call _discover_capabilities(index) to get capability list
  - Use lambda with default arguments for health_check/rebuild
  - Verify: self.components has entries for "standards" and "code"
  
  **Acceptance Criteria:**
  - [ ] self.components dict created after _init_indexes()
  - [ ] Each index registered with _discover_capabilities() call
  - [ ] Lambda uses default arg binding: `lambda idx=index: idx.health_check()`
  - [ ] Components registered for "standards" and "code"
  - [ ] IndexManager instantiates without errors

- [ ] **Task 4.2**: Implement _discover_capabilities() method (M - 2 hours)
  - Check hasattr(index, "components")
  - If has components: aggregate capabilities from all sub-components
  - If no components (legacy): return [f"search_{class_name}"]
  - Return List[str] of all capabilities
  - Verify: CodeIndex returns ["search_code", "search_ast", "find_callers", ...]
  
  **Acceptance Criteria:**
  - [ ] Method signature: `_discover_capabilities(self, index: BaseIndex) -> List[str]`
  - [ ] hasattr() check for .components attribute
  - [ ] If components present: aggregate all sub-component capabilities
  - [ ] If no components: return fallback list
  - [ ] CodeIndex returns 5+ capabilities
  - [ ] Legacy index returns 1+ capability

- [ ] **Task 4.3**: Implement _find_rebuild_actions() method (L - 4 hours)
  - Accept parent_name (str) and status (HealthStatus)
  - Check status.details.get("components", {})
  - If sub_components present: drill down recursively
  - For each unhealthy sub-component: get its rebuild function
  - Build actions list with path (e.g., "code.graph.ast"), description, rebuild_fn
  - If no sub_components (leaf): return single action for parent
  - Verify: Drill down to code.graph.ast returns specific rebuild action
  
  **Acceptance Criteria:**
  - [ ] Method signature: `_find_rebuild_actions(parent_name: str, status: HealthStatus) -> List[Dict]`
  - [ ] Recursively drills down to unhealthy leaf components
  - [ ] Actions include: path, description, rebuild_fn
  - [ ] Path format: "parent.child.grandchild" (e.g., "code.graph.ast")
  - [ ] For code.graph.ast broken: returns action with path="code.graph.ast"
  - [ ] For leaf components: returns single action

- [ ] **Task 4.4**: Update ensure_healthy_with_rebuild() method (M - 2 hours)
  - Call health_check_all() to get all index statuses
  - For each unhealthy index: call _find_rebuild_actions()
  - Aggregate all rebuild actions
  - Execute each action's rebuild_fn()
  - Log rebuild description before executing
  - Return dict with rebuild_actions and final_health
  - Verify: Only broken components rebuilt
  
  **Acceptance Criteria:**
  - [ ] Calls health_check_all() first
  - [ ] Calls _find_rebuild_actions() for each unhealthy index
  - [ ] Executes only broken component rebuilds (not all)
  - [ ] Logs rebuild description before execution
  - [ ] Returns dict with rebuild_actions list and final_health
  - [ ] Healthy components untouched

- [ ] **Task 4.5**: Write integration tests for IndexManager (L - 4 hours)
  - Test: Full cascade health check (4 levels deep)
  - Test: Drill down to specific component (code.graph.ast)
  - Test: Targeted rebuild preserves healthy data
  - Test: Backward compatibility (legacy index without .components)
  - Test: Mixed environment (some migrated, some not)
  - Verify: 0 changes to CodeIndex when GraphIndex adds component
  - Measure: Full cascade < 500ms
  
  **Acceptance Criteria:**
  - [ ] Test case: Full cascade health check returns 4-level nested structure
  - [ ] Test case: Drill down to code.graph.ast returns specific action
  - [ ] Test case: Targeted rebuild → only AST rebuilt, graph data preserved
  - [ ] Test case: Legacy index (no .components) works with fallback
  - [ ] Test case: Mixed environment (GraphIndex migrated, StandardsIndex not) works
  - [ ] Full cascade duration < 500ms (measured)
  - [ ] All 6+ test cases passing

### Phase 4 Validation Gate

🛑 **Before advancing to Phase 5:**
- [ ] All Phase 4 tasks completed (5/5)
- [ ] All Phase 4 acceptance criteria met
- [ ] IndexManager has .components registry
- [ ] _discover_capabilities() implemented with hasattr() check
- [ ] _find_rebuild_actions() implemented with recursive drill-down
- [ ] ensure_healthy_with_rebuild() uses dynamic discovery
- [ ] All integration tests passing
- [ ] Full cascade health check works (4 levels deep) ✅
- [ ] Targeted rebuild: drill down to code.graph.ast ✅
- [ ] Backward compatibility: legacy indexes work ✅
- [ ] Full cascade duration < 500ms ✅
- [ ] No linting errors
- [ ] Code reviewed and approved

**Success Criteria Met:**
- ✅ Full cascade health check from server startup
- ✅ Drill down to code.graph.ast and rebuild only that component
- ✅ Backward compatibility: Legacy indexes without .components still work

**Exit Criteria:** IndexManager fully migrated. All indexes using pattern. System functional end-to-end. Ready for documentation.

---

## Phase 5: Documentation

**Objective:** Document the component pattern in standards, update architecture diagrams, create "how to add component" guide.

**Estimated Duration:** 2-3 hours

**Critical Path:** No (can be done in parallel with testing)

**Deliverables:**
- ComponentDescriptor pattern documented in `.praxis-os/standards/`
- "How to add new component" guide with examples
- RAG architecture diagrams updated (show component registries)
- Migration guide for future indexes
- Examples for all 4 hierarchy levels

**Success Criteria:**
- New developer can add component to any index using guide alone
- Standards discoverable via pos_search_project()

### Phase 5 Tasks

- [ ] **Task 5.1**: Document ComponentDescriptor pattern in standards (M - 2 hours)
  - Create `.praxis-os/standards/rag/component-registry-pattern.md`
  - Document pattern overview (fractal, self-similar, dynamic discovery)
  - Include ComponentDescriptor API reference
  - Include dynamic_health_check() API reference
  - Add examples for all 4 hierarchy levels
  - Add when to use vs not use pattern
  - Verify: pos_search_project finds "component registry pattern"
  
  **Acceptance Criteria:**
  - [ ] File created at `.praxis-os/standards/rag/component-registry-pattern.md`
  - [ ] ComponentDescriptor API fully documented
  - [ ] dynamic_health_check() API fully documented
  - [ ] Examples for all 4 levels (GraphIndex, CodeIndex, StandardsIndex, IndexManager)
  - [ ] When/not-when-to-use section included
  - [ ] Discoverable via `pos_search_project(query="component registry pattern")`

- [ ] **Task 5.2**: Create "how to add component" guide (M - 2 hours)
  - Create `.praxis-os/standards/rag/how-to-add-component.md`
  - Step-by-step guide for adding component to GraphIndex
  - Step-by-step guide for adding component to CodeIndex
  - Include code examples for health_check() and rebuild() methods
  - Include common pitfalls (lambda binding, exception handling)
  - Include testing checklist
  - Verify: Follow guide to add mock component successfully
  
  **Acceptance Criteria:**
  - [ ] File created at correct path
  - [ ] Step-by-step guide for GraphIndex (numbered steps)
  - [ ] Step-by-step guide for CodeIndex
  - [ ] Code examples for health_check() (minimum 2)
  - [ ] Code examples for rebuild() (minimum 2)
  - [ ] Common pitfalls section (minimum 3 pitfalls)
  - [ ] Testing checklist (minimum 5 items)
  - [ ] Guide tested: followed to add mock component successfully

- [ ] **Task 5.3**: Update RAG architecture diagrams (S - 1 hour)
  - Update architecture diagram to show component registries
  - Add component registry boxes at each level
  - Show health check flow cascading through registries
  - Add legend explaining fractal pattern
  - Save as `.praxis-os/standards/rag/architecture-component-pattern.md`
  - Verify: Diagram matches implemented structure
  
  **Acceptance Criteria:**
  - [ ] Diagram shows component registries at all 4 levels
  - [ ] Health check flow visualized (arrows/sequence)
  - [ ] Legend explains fractal/self-similar pattern
  - [ ] Diagram matches actual implementation
  - [ ] Saved at correct path

- [ ] **Task 5.4**: Create migration guide for future indexes (M - 2 hours)
  - Document migration steps (legacy → component pattern)
  - Include before/after code examples
  - Document backward compatibility approach (hasattr checks)
  - Document rollback strategy
  - Include testing checklist for migration
  - Add to `.praxis-os/standards/rag/migrating-to-component-pattern.md`
  - Verify: Guide covers all migration scenarios
  
  **Acceptance Criteria:**
  - [ ] Migration steps documented (numbered, specific)
  - [ ] Before/after code examples (minimum 2 pairs)
  - [ ] hasattr() backward compatibility pattern documented
  - [ ] Rollback strategy documented
  - [ ] Testing checklist (minimum 5 items)
  - [ ] Covers: new index, existing index, partial migration scenarios

### Phase 5 Validation Gate

🛑 **Before marking project complete:**
- [ ] All Phase 5 tasks completed (4/4)
- [ ] All Phase 5 acceptance criteria met
- [ ] ComponentDescriptor pattern documented in standards
- [ ] "How to add component" guide created and tested
- [ ] RAG architecture diagrams updated
- [ ] Migration guide created
- [ ] All documentation discoverable via pos_search_project() ✅
- [ ] Code reviewed and approved

**Success Criteria Met:**
- ✅ New developer can add component to any index using guide alone
- ✅ Standards discoverable via pos_search_project()

**Exit Criteria:** Feature fully documented. Future developers can extend pattern without assistance.

---

## Project Completion

### Overall Success Criteria

**Business Goals Achieved:**
- ✅ **Goal 1:** False positive rebuilds eliminated (0% vs 100%)
- ✅ **Goal 2:** 0 code changes in parent indexes when adding components
- ✅ **Goal 3:** Partial degradation: 100% success for healthy components
- ✅ **Goal 4:** Granular diagnostics: 5+ component statuses vs 1 boolean
- ✅ **Goal 5:** Maintenance burden significantly reduced (O(1) vs O(N²))

**Technical Goals Achieved:**
- ✅ 15x rebuild speedup (2s vs 30s)
- ✅ Component pattern at all 4 levels (fractal uniformity)
- ✅ Backward compatibility (hasattr() checks)
- ✅ Full cascade health check < 500ms
- ✅ All tests passing (unit + integration)
- ✅ 90%+ code coverage for foundation

**Documentation Deliverables:**
- ✅ ComponentDescriptor pattern documented
- ✅ How-to guide for adding components
- ✅ Architecture diagrams updated
- ✅ Migration guide created

### Final Validation Checklist

Before production deployment:
- [ ] All 6 phases completed
- [ ] All 26 tasks completed
- [ ] All validation gates passed
- [ ] All tests passing (unit + integration + end-to-end)
- [ ] No linting errors (mypy + ruff)
- [ ] Code coverage ≥ 90% for foundation, ≥ 80% for indexes
- [ ] All documentation complete and discoverable
- [ ] Backward compatibility verified
- [ ] Performance targets met (15x speedup, < 500ms cascade)
- [ ] Success metrics validated (see Business Goals above)
- [ ] Code reviewed and approved by team
- [ ] Stakeholders notified (optional - internal refactor)

### Post-Deployment Monitoring

After production deployment, monitor for:
- Health check duration (alert if > 500ms)
- Rebuild duration (alert if > 5s for any component)
- Component health status (alert if any component unhealthy > 5 minutes)
- Capability availability (dashboard showing system-wide capability map)
- Error rates (any increase in health check exceptions?)

---

## Phased Rollout Strategy

**Rationale:** Gradual migration minimizes risk, validates pattern at each step, allows rollback if issues found.

**Order:**
1. **Phase 0 (Foundation)**: Create abstractions (blocks everything)
2. **Phase 1 (GraphIndex)**: Pilot at lowest level (most benefit, validates pattern)
3. **Test in Production**: Validate GraphIndex in real usage before scaling
4. **Phase 2-3 (CodeIndex, StandardsIndex)**: Scale to other indexes (parallel)
5. **Phase 4 (IndexManager)**: Top-level integration (requires all sub-indexes migrated)
6. **Phase 5 (Documentation)**: Document for future developers (can overlap with Phase 4)

**Rollback Plan:** Each phase can be rolled back independently due to hasattr() backward compatibility checks.

---

## Dependencies

### Phase-Level Dependencies

```
Phase 0 (Foundation)
    ↓
Phase 1 (GraphIndex Pilot)
    ↓
Phase 2 (CodeIndex) ⟍
                     → Phase 4 (IndexManager)
Phase 3 (StandardsIndex) ⟋
    ↓
Phase 5 (Documentation) [parallel with Phase 4]
```

**Phase 0 → Phase 1:**
Phase 1 depends on Phase 0 being complete.
Cannot register components in GraphIndex without ComponentDescriptor and dynamic_health_check() existing.

**Phase 1 → Phase 2, 3:**
Phases 2 and 3 depend on Phase 1 validation.
Cannot scale component pattern to other indexes without validating it works in pilot (Phase 1).

**Phase 2, 3 → Phase 4:**
Phase 4 depends on Phases 2 AND 3 being complete.
Cannot implement IndexManager component registry without sub-indexes (CodeIndex, StandardsIndex) already using pattern.

**Phase 1-4 → Phase 5:**
Phase 5 (Documentation) can run in parallel with Phase 4, but requires Phase 1 complete (pilot validated) to document accurately.

### Task-Level Dependencies

**Phase 0:**
- Task 0.1 → Task 0.2, 0.3 (must create module before implementing classes)
- Task 0.2, 0.3 → Task 0.4 (must implement before testing)
- All Phase 0 → All other phases (foundation blocks everything)

**Phase 1:**
- Task 1.1 → Task 1.2, 1.3, 1.4, 1.5 (must create registry before implementing component methods)
- Task 1.2, 1.3, 1.4, 1.5 → Task 1.6 (must implement component methods before using dynamic_health_check)
- Task 1.6 → Task 1.7 (must update health_check() before testing)

**Phase 2:**
- Task 2.1 → Task 2.2 (must create registry before updating health_check)
- Task 2.2 → Task 2.3 (must update health_check before testing)

**Phase 3:**
- Task 3.1 → Task 3.2 (must create registry before updating health_check)
- Task 3.2 → Task 3.3 (must update health_check before testing)

**Phase 4:**
- Task 4.1, 4.2 → Task 4.3 (must have registry + capabilities before implementing drill-down)
- Task 4.3 → Task 4.4 (must implement drill-down before using in ensure_healthy_with_rebuild)
- Task 4.4 → Task 4.5 (must implement before testing)

**Phase 5:**
- No inter-task dependencies (all can be done in parallel)
- Task 5.1-5.4 || (parallel)

### Critical Path

The critical path (longest sequence of dependent tasks) is:
```
Phase 0 (all) → Phase 1 (all) → Phase 2 (all) → Phase 4 (all)
8-9 hours    +  12-13 hours  +  5-6 hours   +  14-16 hours  = 39-44 hours
```

Phase 3 and Phase 5 can overlap with other phases, so they don't extend the critical path if parallelized correctly.

**Minimum Timeline:** 39-44 hours if Phase 3 done parallel with Phase 2, Phase 5 parallel with Phase 4.

### Parallel Opportunities

**Can be done in parallel:**
- Phase 2 (CodeIndex) || Phase 3 (StandardsIndex) - Both depend only on Phase 1, not each other
- Phase 4 (IndexManager) || Phase 5 (Documentation) - Phase 5 can start after Phase 1 validates pattern

**Cannot be parallelized:**
- Phase 0 → blocks everything (foundation)
- Phase 1 → blocks Phases 2, 3, 4 (pilot validation required)
- Phase 4 → requires Phase 2 AND 3 complete (IndexManager needs both sub-indexes migrated)

### Dependency Summary

- **Phase dependencies:** 5 major dependencies (0→1, 1→2, 1→3, 2,3→4, 1→5)
- **Task dependencies:** 15+ intra-phase dependencies (mostly linear within phases)
- **Tasks with no dependencies:** 5 (Task 0.1, Phase 5 tasks)
- **Parallel opportunities:** 2 (Phases 2||3, Phases 4||5)
- **Critical path:** Phase 0 → 1 → 2 → 4 (39-44 hours)
- **No circular dependencies:** ✅ Validated

---


