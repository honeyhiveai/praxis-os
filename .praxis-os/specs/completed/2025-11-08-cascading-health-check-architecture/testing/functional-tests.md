# Functional Tests Plan

**Project:** Cascading Health Check Architecture  
**Date:** 2025-11-10  
**Purpose:** Detailed test cases for all functional requirements

---

## Test Case Format

Each test case includes:
- **Happy Path**: Feature works as expected
- **Error Handling**: Graceful error handling
- **Edge Cases**: Boundary conditions

---

## Foundation Tests (Phase 0)

### FR-001: Component Registration

**Requirement:** ComponentDescriptor class for declarative component registration  
**Acceptance Criteria:** Accepts name, provides, capabilities, health_check, rebuild, dependencies; Invalid descriptor raises ValidationError

#### Happy Path: Valid Component Registration
- **Test:** `test_component_descriptor_valid()`
- **Setup:** Create ComponentDescriptor with all required params
- **Action:** Instantiate with valid name, provides, capabilities, health_check, rebuild
- **Expected:** Component created successfully, all attributes accessible
- **Verifies:** All required parameters accepted, dependencies defaults to []

#### Error Handling: Missing Required Parameters
- **Test:** `test_component_descriptor_missing_name()`, `test_component_descriptor_missing_provides()`, etc.
- **Setup:** Attempt to create ComponentDescriptor with missing required param
- **Expected:** raises ValueError with descriptive message
- **Verifies:** Invalid descriptor rejected at registration time

#### Error Handling: Non-Callable Health Check
- **Test:** `test_component_descriptor_non_callable_health_check()`
- **Setup:** Pass string instead of callable for health_check
- **Expected:** raises ValueError "health_check must be callable"
- **Verifies:** Callable validation for health_check and rebuild

#### Edge Cases: Empty Lists
- **Test:** `test_component_descriptor_empty_provides()`, `test_component_descriptor_empty_capabilities()`
- **Setup:** Pass empty list for provides or capabilities
- **Expected:** raises ValueError "provides/capabilities cannot be empty"
- **Verifies:** Non-empty list validation

---

### FR-002: Dynamic Health Check Discovery

**Requirement:** Dynamically discover and call health_check() on all registered components  
**Acceptance Criteria:** Accepts Dict[str, ComponentDescriptor], iterates all, no if/else chains, works with 1-50+ components

#### Happy Path: Single Component
- **Test:** `test_dynamic_health_check_single_component()`
- **Setup:** Dict with 1 component (healthy)
- **Action:** Call dynamic_health_check(components)
- **Expected:** Returns HealthStatus with components dict containing 1 entry
- **Verifies:** Basic iteration and aggregation

#### Happy Path: Multiple Components (All Healthy)
- **Test:** `test_dynamic_health_check_multiple_healthy()`
- **Setup:** Dict with 3 components (all healthy)
- **Action:** Call dynamic_health_check(components)
- **Expected:** overall healthy=True, components dict with 3 entries (all healthy)
- **Verifies:** Aggregation logic (all healthy → overall healthy)

#### Happy Path: Multiple Components (One Unhealthy)
- **Test:** `test_dynamic_health_check_one_unhealthy()`
- **Setup:** Dict with 3 components (1 unhealthy, 2 healthy)
- **Action:** Call dynamic_health_check(components)
- **Expected:** overall healthy=False, components dict shows which is unhealthy
- **Verifies:** Partial degradation detection

#### Error Handling: Exception in Component Health Check
- **Test:** `test_dynamic_health_check_component_exception()`
- **Setup:** Mock component.health_check() raises Exception
- **Action:** Call dynamic_health_check(components)
- **Expected:** Exception caught, component marked unhealthy with error message, continues to other components
- **Verifies:** Resilience (NFR-R2)

#### Edge Cases: Empty Components Dict
- **Test:** `test_dynamic_health_check_empty_dict()`
- **Setup:** Pass empty dict {}
- **Action:** Call dynamic_health_check(components)
- **Expected:** Returns HealthStatus(healthy=True) (no components to fail)
- **Verifies:** Handles 0 components gracefully

#### Scalability: 50+ Components
- **Test:** `test_dynamic_health_check_scaling()`
- **Setup:** Dict with 50 components
- **Action:** Call dynamic_health_check(components), measure duration
- **Expected:** Completes in < 500ms, all components checked
- **Verifies:** O(N) iteration, no performance degradation (NFR-SC1)

---

## GraphIndex Tests (Phase 1)

### FR-003: Component-Level Health Reporting

**Requirement:** Report health status for each component independently  
**Acceptance Criteria:** Status for EACH component, includes healthy/message/details, drill-down supported

#### Happy Path: AST Healthy, Graph Healthy
- **Test:** `test_graphindex_health_both_healthy()`
- **Setup:** GraphIndex with populated ast_nodes and symbols/relationships tables
- **Action:** Call GraphIndex.health_check()
- **Expected:** HealthStatus with components["ast"]["healthy"]=True, components["graph"]["healthy"]=True
- **Verifies:** Component-level reporting

#### Happy Path: AST Broken, Graph Healthy
- **Test:** `test_graphindex_health_ast_broken_graph_healthy()`
- **Setup:** Clear ast_nodes table (count=0), keep symbols/relationships
- **Action:** Call GraphIndex.health_check()
- **Expected:** overall healthy=False, components["ast"]["healthy"]=False, components["graph"]["healthy"]=True
- **Verifies:** Independent component health

#### Integration: Drill-Down from CodeIndex
- **Test:** `test_codeindex_health_drilldown()`
- **Setup:** CodeIndex → GraphIndex → AST/Graph components
- **Action:** Call CodeIndex.health_check()
- **Expected:** Response includes nested components: code.graph.ast, code.graph.graph
- **Verifies:** 3-level drill-down (FR-003 acceptance)

#### Edge Cases: Empty Table (count=0)
- **Test:** `test_graphindex_health_empty_ast()`
- **Setup:** ast_nodes table exists but empty (COUNT=0)
- **Action:** Call _check_ast_health()
- **Expected:** Returns unhealthy with details["count"]=0, details["data_present"]=False
- **Verifies:** Empty ≠ missing (NFR-010)

---

### FR-004: Targeted Component Rebuild

**Requirement:** Rebuild only broken components, preserve healthy data  
**Acceptance Criteria:** Identifies specific components, uses component path, rebuild < 3s, preserves healthy data

#### Happy Path: Rebuild AST Only
- **Test:** `test_graphindex_rebuild_ast_only()`
- **Setup:** AST broken (0 nodes), graph healthy (500 symbols)
- **Action:** Call _rebuild_ast()
- **Expected:** ast_nodes repopulated (count > 0), symbols/relationships unchanged (exact same count)
- **Verifies:** Component isolation (FR-004, NFR-R3)

#### Performance: Rebuild Time < 3s
- **Test:** `test_graphindex_rebuild_ast_performance()`
- **Setup:** AST broken
- **Action:** Call _rebuild_ast(), measure duration with time.perf_counter()
- **Expected:** Duration < 3s
- **Verifies:** Performance target (NFR-P2)

#### Integration: IndexManager Targeted Rebuild
- **Test:** `test_indexmanager_targeted_rebuild()`
- **Setup:** Only code.graph.ast broken
- **Action:** Call ensure_healthy_with_rebuild()
- **Expected:** Only AST rebuilt, actions list shows path="code.graph.ast", other components untouched
- **Verifies:** Recursive drill-down, targeted rebuild

#### Error Handling: File Parse Error During Rebuild
- **Test:** `test_rebuild_ast_file_error_continues()`
- **Setup:** Mock _parse_file() raises exception for 1 file
- **Action:** Call _rebuild_ast()
- **Expected:** Error logged, continues to next file, rebuild completes
- **Verifies:** Resilience during rebuild

---

### FR-005: Capability Discovery and Mapping

**Requirement:** Dynamically map capabilities to components, report availability  
**Acceptance Criteria:** Components declare capabilities, health response includes capabilities dict, aggregated automatically

#### Happy Path: All Capabilities Available
- **Test:** `test_graphindex_capabilities_all_available()`
- **Setup:** GraphIndex with both components healthy
- **Action:** Call GraphIndex.health_check()
- **Expected:** details["capabilities"] = {"search_ast": True, "find_callers": True, "find_dependencies": True, "find_call_paths": True}
- **Verifies:** Capability mapping from healthy components

#### Happy Path: Partial Capabilities Available
- **Test:** `test_graphindex_capabilities_partial()`
- **Setup:** AST unhealthy, graph healthy
- **Action:** Call GraphIndex.health_check()
- **Expected:** capabilities["search_ast"]=False, capabilities["find_callers"]=True
- **Verifies:** Capability reflects component health

#### Integration: Aggregated from Sub-Components
- **Test:** `test_codeindex_capabilities_aggregated()`
- **Setup:** CodeIndex → GraphIndex, GraphIndex declares 4 capabilities
- **Action:** Call CodeIndex.health_check(), inspect capabilities
- **Expected:** CodeIndex capabilities include all 4 from GraphIndex
- **Verifies:** Automatic aggregation (FR-005 acceptance)

---

### FR-006: Partial Degradation Support

**Requirement:** Operational components work even when others unhealthy  
**Acceptance Criteria:** Independent components don't block, operations check capability, healthy succeed, unhealthy fail with clear errors

#### Happy Path: AST Broken, find_callers() Succeeds
- **Test:** `test_partial_degradation_ast_broken_find_callers_succeeds()`
- **Setup:** Clear ast_nodes (AST broken), keep symbols/relationships (graph healthy)
- **Action:** Call find_callers("my_function")
- **Expected:** Returns results successfully (not affected by AST)
- **Verifies:** Independent components (FR-006, NFR-R1)

#### Happy Path: Graph Broken, search_ast() Succeeds
- **Test:** `test_partial_degradation_graph_broken_search_ast_succeeds()`
- **Setup:** Clear symbols/relationships (graph broken), keep ast_nodes (AST healthy)
- **Action:** Call search_ast("pattern")
- **Expected:** Returns AST results successfully
- **Verifies:** Reverse independence

#### Error Handling: Unhealthy Component Fails with Clear Error
- **Test:** `test_partial_degradation_ast_broken_search_ast_fails()`
- **Setup:** AST broken
- **Action:** Call search_ast("pattern")
- **Expected:** Raises clear error: "search_ast unavailable: AST component unhealthy"
- **Verifies:** Clear error messages (NFR-U1)

#### Integration: System Reports Partial Status
- **Test:** `test_partial_degradation_status_reporting()`
- **Setup:** 3/5 components unhealthy
- **Action:** Call health_check()
- **Expected:** Message includes "3/5 capabilities available" or similar
- **Verifies:** Partial degradation reporting (FR-006 acceptance)

---

## Cross-Index Tests (Phase 2-4)

### FR-007: Backward Compatibility

**Requirement:** Support indexes without component pattern  
**Acceptance Criteria:** hasattr() check, legacy fallback, mixed environment, no breaking changes

#### Happy Path: Legacy Index Without .components
- **Test:** `test_backward_compat_legacy_index()`
- **Setup:** Mock index without .components attribute
- **Action:** Call IndexManager._discover_capabilities(legacy_index)
- **Expected:** Returns fallback list [f"search_{class_name}"]
- **Verifies:** hasattr() check, fallback logic

#### Integration: Mixed Environment
- **Test:** `test_backward_compat_mixed_environment()`
- **Setup:** GraphIndex migrated (has .components), StandardsIndex not migrated
- **Action:** Call IndexManager.health_check_all()
- **Expected:** Both indexes report health, no errors
- **Verifies:** Mixed environment support (FR-007, NFR-C1)

#### Regression: BaseIndex Interface Unchanged
- **Test:** `test_backward_compat_baseindex_unchanged()`
- **Setup:** Legacy code calling BaseIndex.health_check()
- **Action:** Call health_check()
- **Expected:** Returns HealthStatus with .healthy attribute (existing code works)
- **Verifies:** No breaking changes (NFR-C2)

---

### FR-008: Component Dependency Tracking

**Requirement:** Track component dependencies  
**Acceptance Criteria:** Accepts dependencies list, validates at registration, health considers dependencies, rebuild respects order

#### Happy Path: Component with Dependencies
- **Test:** `test_component_dependency_declaration()`
- **Setup:** Create ComponentDescriptor with dependencies=["vector"]
- **Action:** Register FTS component depending on vector
- **Expected:** Component registered with dependencies tracked
- **Verifies:** Dependencies list accepted

#### Error Handling: Invalid Dependency (Not Registered)
- **Test:** `test_component_dependency_validation()`
- **Setup:** Register component with dependencies=["nonexistent"]
- **Action:** Validation at registration time
- **Expected:** raises ValueError "Dependency 'nonexistent' not found"
- **Verifies:** Dependency validation (FR-008 acceptance)

#### Error Handling: Circular Dependency Detection
- **Test:** `test_component_dependency_circular()`
- **Setup:** Component A depends on B, B depends on A
- **Action:** Register second component
- **Expected:** raises ValueError "Circular dependency detected"
- **Verifies:** Circular detection (FR-008 acceptance)

#### Integration: Rebuild Respects Dependencies
- **Test:** `test_rebuild_respects_dependencies()`
- **Setup:** FTS broken (depends on vector), vector healthy
- **Action:** Trigger rebuild
- **Expected:** Rebuilds in order: vector first (if needed), then FTS
- **Verifies:** Rebuild ordering

---

### FR-009: Fractal Pattern Uniformity

**Requirement:** Identical pattern at all hierarchy levels  
**Acceptance Criteria:** ComponentDescriptor at all 4 levels, dynamic_health_check() at all 4, consistent structure

#### Integration: Pattern at GraphIndex (Level 4)
- **Test:** `test_fractal_pattern_graphindex()`
- **Setup:** GraphIndex with self.components = {}
- **Action:** Check registration syntax, health_check() implementation
- **Expected:** Uses ComponentDescriptor, calls dynamic_health_check(self.components)
- **Verifies:** Pattern at level 4

#### Integration: Pattern at CodeIndex (Level 3)
- **Test:** `test_fractal_pattern_codeindex()`
- **Setup:** CodeIndex with self.components = {}
- **Action:** Check registration syntax, health_check() implementation
- **Expected:** Identical to GraphIndex (dict syntax, dynamic_health_check call)
- **Verifies:** Pattern uniformity

#### Integration: Pattern at StandardsIndex (Level 2)
- **Test:** `test_fractal_pattern_standardsindex()`
- **Setup:** StandardsIndex with self.components = {}
- **Action:** Check registration syntax
- **Expected:** Identical pattern
- **Verifies:** Pattern at level 2

#### Integration: Pattern at IndexManager (Level 1)
- **Test:** `test_fractal_pattern_indexmanager()`
- **Setup:** IndexManager with self.components = {}
- **Action:** Check registration syntax
- **Expected:** Identical pattern (ComponentDescriptor, dynamic_health_check)
- **Verifies:** Top-level pattern uniformity

#### Maintainability: Adding Component = Local Changes Only
- **Test:** `test_fractal_add_component_zero_changes()`
- **Setup:** Add mock "imports" component to GraphIndex
- **Action:** Check files modified
- **Expected:** Only GraphIndex modified (0 changes in CodeIndex, IndexManager)
- **Verifies:** Code change isolation (NFR-M1)

---

### FR-010: Component Health Check Data Contract

**Requirement:** Standard data contract for health responses  
**Acceptance Criteria:** Returns Dict[str, Any], required keys (data_present, query_works, count, error), exception returns error dict

#### Happy Path: Healthy Component Response Contract
- **Test:** `test_health_check_contract_healthy()`
- **Setup:** GraphIndex._check_ast_health() with populated table
- **Action:** Call _check_ast_health()
- **Expected:** Returns dict with keys: data_present=True, query_works=True, count>0, error=None
- **Verifies:** Required keys present

#### Error Handling: Unhealthy Component Response Contract
- **Test:** `test_health_check_contract_unhealthy()`
- **Setup:** Empty ast_nodes table (count=0)
- **Action:** Call _check_ast_health()
- **Expected:** Returns dict with data_present=False, count=0
- **Verifies:** Contract for unhealthy state

#### Error Handling: Exception Returns Error Dict
- **Test:** `test_health_check_contract_exception()`
- **Setup:** Mock DB connection raises exception
- **Action:** Call _check_ast_health()
- **Expected:** Returns dict with error="..." (not raised), data_present=False, query_works=False
- **Verifies:** Exception handling contract (FR-010, NFR-R2)

#### Edge Cases: Additional Component-Specific Keys
- **Test:** `test_health_check_contract_additional_keys()`
- **Setup:** Component adds custom key (e.g., "symbol_count")
- **Action:** Call health check
- **Expected:** Required keys present + additional keys allowed
- **Verifies:** Extensibility

---

## Summary

### Test Coverage

| FR ID | Test Cases | Happy Path | Error Handling | Edge Cases | Integration |
|-------|------------|------------|----------------|------------|-------------|
| FR-001 | 4 | ✅ | ✅✅ | ✅ | - |
| FR-002 | 6 | ✅✅✅ | ✅ | ✅ | ✅ |
| FR-003 | 4 | ✅✅ | - | ✅ | ✅ |
| FR-004 | 4 | ✅ | ✅ | - | ✅✅ |
| FR-005 | 3 | ✅✅ | - | - | ✅ |
| FR-006 | 4 | ✅✅ | ✅ | - | ✅ |
| FR-007 | 3 | ✅ | - | - | ✅✅ |
| FR-008 | 4 | ✅ | ✅✅ | - | ✅ |
| FR-009 | 5 | - | - | - | ✅✅✅✅✅ |
| FR-010 | 4 | ✅ | ✅✅ | ✅ | - |

**Total Test Cases:** 41  
**All FRs Covered:** 10/10 ✅  
**Integration Scenarios:** 14

---


