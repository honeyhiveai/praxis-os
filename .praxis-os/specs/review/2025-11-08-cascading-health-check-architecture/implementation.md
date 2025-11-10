# Implementation Approach

**Project:** Cascading Health Check Architecture  
**Date:** 2025-11-10

---

## 1. Implementation Philosophy

**Core Principles:**
1. **Incremental Migration**: Start with foundation, validate pilot, scale gradually
2. **Backward Compatibility First**: Use hasattr() checks to support mixed environments
3. **Test-Driven Development**: Write tests before implementation where possible
4. **Code Review Required**: All phases gate on peer review
5. **Pattern Uniformity**: Same pattern at all levels (fractal design)

---

## 2. Implementation Order

**Follow phased rollout from tasks.md:**

```
Phase 0: Foundation
    ↓
Phase 1: GraphIndex Pilot (validate pattern)
    ↓
Phase 2: CodeIndex ⟍
                     → Phase 4: IndexManager
Phase 3: StandardsIndex ⟋
    ↓
Phase 5: Documentation
```

**Critical Path:** Phase 0 → 1 → 2 → 4 (39-44 hours)

---

## 3. Code Patterns

### Pattern 1: ComponentDescriptor Registration

**Used in:** All indexes (GraphIndex, CodeIndex, StandardsIndex, IndexManager)

**Good Pattern:**
```python
class GraphIndex(BaseIndex):
    def __init__(self, config, base_path, languages):
        # ... existing initialization ...
        
        # Register components declaratively
        self.components = {
            "ast": ComponentDescriptor(
                name="ast",
                provides=["ast_nodes"],
                capabilities=["search_ast"],
                health_check=self._check_ast_health,
                rebuild=self._rebuild_ast,
                dependencies=[],
            ),
            "graph": ComponentDescriptor(
                name="graph",
                provides=["symbols", "relationships"],
                capabilities=["find_callers", "find_dependencies", "find_call_paths"],
                health_check=self._check_graph_health,
                rebuild=self._rebuild_graph,
                dependencies=[],
            ),
        }
```

**Anti-Pattern (Don't Do This):**
```python
# ❌ Registering components as tuples - not descriptive
self.components = [
    ("ast", self._check_ast_health, self._rebuild_ast),
    ("graph", self._check_graph_health, self._rebuild_graph),
]

# ❌ Hardcoded capabilities - not discoverable
self.capabilities = ["search_ast", "find_callers"]  # static, not dynamic
```

---

### Pattern 2: Component Health Check Method

**Used in:** GraphIndex._check_ast_health(), StandardsIndex._check_vector_health()

**Good Pattern:**
```python
def _check_ast_health(self) -> HealthStatus:
    """Check AST component health (returns HealthStatus, not Dict)."""
    conn = self.db_connection.get_connection()
    
    try:
        count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
        test = conn.execute("SELECT * FROM ast_nodes LIMIT 1").fetchone()
        
        healthy = count > 0 and test is not None
        return HealthStatus(
            healthy=healthy,
            message=f"{count} AST nodes" if healthy else "No AST data",
            details={
                "data_present": count > 0,
                "query_works": test is not None,
                "count": count,
                "error": None,
            }
        )
    except Exception as e:
        # Don't raise - return error HealthStatus
        return HealthStatus(
            healthy=False,
            message=f"AST health check failed: {e}",
            details={
                "data_present": False,
                "query_works": False,
                "count": 0,
                "error": str(e),
            }
        )
```

**Anti-Pattern (Don't Do This):**
```python
# ❌ Returning boolean - not enough information
def _check_ast_health(self) -> bool:
    count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
    return count > 0

# ❌ Raising exceptions instead of returning error status
def _check_ast_health(self) -> HealthStatus:
    count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
    if count == 0:
        raise ValueError("No AST data")  # ❌ Don't raise
```

---

### Pattern 3: Lambda Wrapper with Default Argument Binding

**Used in:** CodeIndex, IndexManager

**Good Pattern:**
```python
class CodeIndex(BaseIndex):
    def __init__(self, config, base_path):
        # Initialize sub-indexes
        self.semantic = SemanticIndex(config.vector, base_path)
        self.graph = GraphIndex(config.graph, base_path, config.languages)
        
        # Register with lambda wrappers using DEFAULT ARGUMENT BINDING
        self.components = {
            "semantic": ComponentDescriptor(
                name="semantic",
                provides=["code_embeddings", "code_fts"],
                capabilities=["search_code"],
                health_check=lambda idx=self.semantic: idx.health_check(),  # ✅ idx bound
                rebuild=lambda idx=self.semantic: idx.build(force=True),
                dependencies=[],
            ),
            "graph": ComponentDescriptor(
                name="graph",
                provides=["ast", "symbols", "relationships"],
                capabilities=["search_ast", "find_callers"],
                health_check=lambda idx=self.graph: idx.health_check(),  # ✅ idx bound
                rebuild=lambda idx=self.graph: idx.build(force=True),
                dependencies=[],
            ),
        }
```

**Anti-Pattern (Don't Do This):**
```python
# ❌ Late binding - captures variable reference, not value
self.components = {
    "semantic": ComponentDescriptor(
        health_check=lambda: self.semantic.health_check(),  # ❌ self.semantic can change
        ...
    ),
}

# Even worse in loops:
for index_name, index in self._indexes.items():
    self.components[index_name] = ComponentDescriptor(
        health_check=lambda: index.health_check(),  # ❌ index changes in loop!
        ...
    )

# ✅ CORRECT in loops:
for index_name, index in self._indexes.items():
    self.components[index_name] = ComponentDescriptor(
        health_check=lambda idx=index: idx.health_check(),  # ✅ idx bound at creation
        ...
    )
```

---

### Pattern 4: Dynamic Health Check Usage

**Used in:** All indexes (GraphIndex, CodeIndex, StandardsIndex, IndexManager)

**Good Pattern:**
```python
class GraphIndex(BaseIndex):
    def health_check(self) -> HealthStatus:
        """Dynamic health check - discovers all components."""
        return dynamic_health_check(self.components)
```

**That's it!** Single line. No static if/else logic.

**Anti-Pattern (Don't Do This):**
```python
# ❌ Static if/else chains - defeats the purpose
def health_check(self) -> HealthStatus:
    if "ast" in self.components:
        ast_health = self.components["ast"].health_check()
    if "graph" in self.components:
        graph_health = self.components["graph"].health_check()
    # ... manual aggregation ...
```

---

### Pattern 5: Backward Compatibility with hasattr()

**Used in:** IndexManager._discover_capabilities()

**Good Pattern:**
```python
def _discover_capabilities(self, index: BaseIndex) -> List[str]:
    """Dynamic capability discovery with backward compatibility."""
    if hasattr(index, "components"):
        # New pattern - aggregate from components
        caps = []
        for component in index.components.values():
            caps.extend(component.capabilities)
        return caps
    else:
        # Legacy fallback - still works
        return [f"search_{index.__class__.__name__.lower()}"]
```

**Anti-Pattern (Don't Do This):**
```python
# ❌ Assuming components always exists - breaks legacy indexes
def _discover_capabilities(self, index: BaseIndex) -> List[str]:
    caps = []
    for component in index.components.values():  # ❌ AttributeError if legacy
        caps.extend(component.capabilities)
    return caps
```

---

### Pattern 6: Recursive Drill-Down for Targeted Rebuild

**Used in:** IndexManager._find_rebuild_actions()

**Good Pattern:**
```python
def _find_rebuild_actions(self, parent_name: str, status: HealthStatus) -> List[Dict]:
    """Recursively discover what needs rebuilding."""
    actions = []
    sub_components = status.details.get("components", {})
    
    if sub_components:
        # Drill down to specific unhealthy components
        index = self._indexes[parent_name]
        
        if hasattr(index, "components"):
            for sub_name, sub_health in sub_components.items():
                if not sub_health.get("healthy"):
                    sub_component = index.components[sub_name]
                    actions.append({
                        "path": f"{parent_name}.{sub_name}",  # ✅ Hierarchical path
                        "description": f"Rebuild {parent_name}.{sub_name}: {sub_health.get('message')}",
                        "rebuild_fn": sub_component.rebuild,
                    })
    else:
        # Leaf component - no sub-components
        component = self.components[parent_name]
        actions.append({
            "path": parent_name,
            "description": f"Rebuild {parent_name}: {status.message}",
            "rebuild_fn": component.rebuild,
        })
    
    return actions
```

**Anti-Pattern (Don't Do This):**
```python
# ❌ Always rebuilding entire index - defeats targeted rebuild
def _find_rebuild_actions(self, parent_name: str, status: HealthStatus) -> List[Dict]:
    return [{
        "path": parent_name,
        "description": f"Rebuild {parent_name}",
        "rebuild_fn": lambda: self.rebuild_index(parent_name)  # ❌ Full rebuild always
    }]
```

---

### Pattern 7: Component Isolation in Rebuild

**Used in:** GraphIndex._rebuild_ast(), GraphIndex._rebuild_graph()

**Good Pattern:**
```python
def _rebuild_ast(self) -> None:
    """Rebuild only AST component - preserve graph data."""
    conn = self.db_connection.get_connection()
    
    # Clear ONLY ast_nodes table
    conn.execute("DELETE FROM ast_nodes")
    logger.info("Cleared ast_nodes table")
    
    # Re-parse all source files
    for file_path in self._get_source_files():
        try:
            tree = self._parse_file(file_path)
            self._insert_ast_nodes(tree, file_path)
        except Exception as e:
            logger.error("Failed to parse %s: %s", file_path, e)
            # Continue with next file - don't abort entire rebuild
    
    logger.info("AST rebuild complete")
```

**Anti-Pattern (Don't Do This):**
```python
# ❌ Clearing all tables - destroys healthy data
def _rebuild_ast(self) -> None:
    conn.execute("DELETE FROM ast_nodes")
    conn.execute("DELETE FROM symbols")       # ❌ Don't touch graph data!
    conn.execute("DELETE FROM relationships")  # ❌ Destroys healthy component
```

---

## 4. Error Handling Patterns

### Pattern: Exception Handling in Health Checks

**Principle:** Health checks NEVER raise exceptions to caller. Always return error HealthStatus.

**Good Pattern:**
```python
def _check_ast_health(self) -> HealthStatus:
    try:
        # ... health check logic ...
        return HealthStatus(healthy=True, ...)
    except Exception as e:
        logger.error("Health check failed for AST: %s", e, exc_info=True)
        return HealthStatus(
            healthy=False,
            message=f"health check exception: {e}",
            details={"error": str(e)}
        )
```

### Pattern: Exception Handling in Rebuilds

**Principle:** Rebuilds log errors but continue processing (don't abort).

**Good Pattern:**
```python
def _rebuild_ast(self) -> None:
    for file_path in self._get_source_files():
        try:
            self._parse_and_insert(file_path)
        except Exception as e:
            logger.error("Failed to parse %s: %s", file_path, e)
            # Continue - one file failure doesn't abort entire rebuild
```

---

## 5. Testing Patterns

[Continued in next section - Task 3]

---

## 6. Implementation Checklist

Before committing code for any task:
- [ ] Code follows patterns above (no anti-patterns)
- [ ] Health checks return HealthStatus (not bool, not raise)
- [ ] Lambda wrappers use default argument binding
- [ ] hasattr() checks for backward compatibility where needed
- [ ] Component registration is declarative (not imperative)
- [ ] Rebuild methods preserve healthy component data
- [ ] Exception handling: health checks don't raise, rebuilds continue
- [ ] Tests written (see Testing Strategy section)
- [ ] No linting errors
- [ ] Code reviewed

---

## 7. Deployment

### Deployment Strategy: Phased Rollout

**Rationale:** Gradual migration minimizes risk, validates pattern at each step, allows rollback if issues found.

**Phase-by-Phase Deployment:**

```
Phase 0: Foundation (no deployment - library code only)
    ↓
Phase 1: GraphIndex Pilot → Deploy + Monitor
    ↓ (Test in production before proceeding)
Phase 2: CodeIndex → Deploy
Phase 3: StandardsIndex → Deploy (parallel with Phase 2)
    ↓
Phase 4: IndexManager → Deploy (final integration)
    ↓
Phase 5: Documentation → Publish standards
```

---

### Deployment Steps

**For Each Phase:**

1. **Run Tests:**
   ```bash
   pytest ouroboros/tests/ -v --cov=ouroboros
   # Coverage target: ≥ 90% for foundation, ≥ 80% for indexes
   ```

2. **Run Linters:**
   ```bash
   mypy ouroboros/ --strict
   ruff check ouroboros/
   # Target: 0 errors
   ```

3. **Sync to Distribution:**
   ```bash
   scripts/sync-to-dist.sh
   # Copies ouroboros/ → dist/ouroboros/
   ```

4. **Commit Changes:**
   ```bash
   git add .
   git commit -m "feat(rag): Phase N - [description]"
   # Follow conventional commits
   ```

5. **Run Pre-Commit Hooks:**
   ```bash
   # Hooks run automatically on commit
   # Includes: mypy, ruff, pytest
   ```

6. **Push and Wait for CI:**
   ```bash
   git push origin feature/cascading-health-checks
   # CI runs full test suite
   ```

7. **Deploy to Server:**
   ```bash
   # MCP server restart (development)
   # Or: uvicorn restart (production)
   ```

8. **Verify Health:**
   ```bash
   # Test health check endpoint
   curl -X POST http://localhost:8000/health_check
   ```

9. **Monitor Logs:**
   ```bash
   tail -f ~/.praxis-os/logs/mcp-server.log
   # Watch for component health check entries
   ```

10. **Smoke Test:**
    ```bash
    # Test critical operations
    # - search_ast
    # - find_callers
    # - search_standards
    ```

---

### Environment Configuration

**No New Environment Variables Required**

This is an internal refactoring. Existing configuration continues working.

**Existing Variables (unchanged):**
```bash
# Base Path
PRAXIS_OS_BASE_PATH=/path/to/workspace

# Database (DuckDB - file-based, no server)
# No env var needed - uses ~/.praxis-os/state/

# Logging
LOG_LEVEL=INFO  # DEBUG for development
```

**Configuration Files (unchanged):**
- `.praxis-os/config.yaml` - MCP server config
- No changes required for component pattern

---

### Database Migrations

**No Database Migrations Required**

**Why?**
- Component pattern is code-only (no schema changes)
- Uses existing tables: ast_nodes, symbols, relationships, documents
- Health check queries unchanged (SELECT COUNT(*))
- Backward compatible with existing data

**Verification:**
```python
# After deployment, verify existing queries work
conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]  # Should succeed
```

---

### Rollback Strategy

**Per-Phase Rollback:**

Each phase can be rolled back independently due to `hasattr()` backward compatibility checks.

**If Phase 1 (GraphIndex) Fails:**

1. **Identify Issue:**
   ```bash
   # Check logs
   tail -f ~/.praxis-os/logs/mcp-server.log | grep -i error
   ```

2. **Stop Deployment:**
   ```bash
   # Don't proceed to Phase 2-5
   ```

3. **Rollback Code:**
   ```bash
   git revert <commit-sha>
   git push origin feature/cascading-health-checks
   ```

4. **Restart Server:**
   ```bash
   # MCP server restart
   # GraphIndex falls back to existing health_check()
   ```

5. **Verify System Health:**
   ```bash
   curl -X POST http://localhost:8000/health_check
   # Should show legacy health check (no "components" field)
   ```

6. **Investigate Root Cause:**
   - Check test failures
   - Review error logs
   - Fix issues before re-attempting

**If Phase 4 (IndexManager) Fails:**

Phases 1-3 remain deployed. Only IndexManager rolls back to legacy behavior.

**Rollback Checklist:**
- [ ] Previous commit identified
- [ ] Rollback tested on development environment
- [ ] No data corruption (components preserve data)
- [ ] Legacy health checks still functional
- [ ] All tests passing after rollback

---

### Deployment Checklist

**Pre-Deployment (Per Phase):**
- [ ] All phase tasks completed (per tasks.md)
- [ ] All acceptance criteria met
- [ ] All tests passing (unit + integration)
- [ ] Code coverage targets met (90% foundation, 80% indexes)
- [ ] No linting errors (mypy + ruff)
- [ ] Code reviewed and approved
- [ ] Phase validation gate passed
- [ ] Deployment plan reviewed

**Deployment (Per Phase):**
- [ ] Tests run successfully
- [ ] Linters pass (0 errors)
- [ ] Code synced to dist/
- [ ] Commit created with conventional commit message
- [ ] Pre-commit hooks pass
- [ ] CI pipeline passes
- [ ] Server restarted
- [ ] Health check endpoint responds
- [ ] Logs clean (no errors)

**Post-Deployment (Per Phase):**
- [ ] Health checks showing component-level details
- [ ] Critical operations tested (search_ast, find_callers)
- [ ] Performance targets met (health check < 50ms, rebuild < 3s)
- [ ] No regression in existing functionality
- [ ] Backward compatibility verified (legacy indexes still work)
- [ ] Metrics normal (no spikes in error rate, latency)
- [ ] Documentation updated (if Phase 5)
- [ ] Stakeholders notified (optional - internal refactor)

**Before Proceeding to Next Phase:**
- [ ] Current phase stable in production for ≥ 24 hours
- [ ] No critical issues reported
- [ ] Performance metrics acceptable
- [ ] Rollback plan tested (development)

---

### Monitoring After Deployment

**Key Metrics to Watch:**

1. **Health Check Duration:**
   ```bash
   # Look for log entries
   grep "Health check for.*took" ~/.praxis-os/logs/mcp-server.log
   # Alert if > 50ms per component, > 500ms cascade
   ```

2. **Rebuild Duration:**
   ```bash
   grep "Rebuild.*took" ~/.praxis-os/logs/mcp-server.log
   # Alert if > 5s (target: < 3s)
   ```

3. **Component Health Status:**
   ```bash
   # Check for unhealthy components
   grep "unhealthy" ~/.praxis-os/logs/mcp-server.log
   # Alert if component unhealthy > 5 minutes
   ```

4. **Error Rates:**
   ```bash
   # Check for health check exceptions
   grep "Health check failed" ~/.praxis-os/logs/mcp-server.log
   # Alert if exception rate increases
   ```

**Success Indicators:**
- ✅ Health checks complete < 500ms
- ✅ Targeted rebuilds complete < 3s (15x speedup vs 30s)
- ✅ Partial degradation working (healthy components succeed)
- ✅ No false positive rebuilds
- ✅ Adding component requires 0 changes in parent indexes

**Failure Indicators:**
- ❌ Health checks timeout (> 500ms)
- ❌ Rebuild takes > 5s
- ❌ Healthy components affected by unhealthy siblings
- ❌ False positive rebuilds still occurring
- ❌ Adding component requires changes in multiple files

---

## 8. Testing Strategy

### 8.1 Requirements Summary

**Total Requirements to Test:** 28
- **Functional Requirements:** 10 (FR-001 through FR-010)
- **Non-Functional Requirements:** 18 (across 7 categories)

**Priority Distribution:**
- Critical: 8 requirements (4 FR + 4 NFR)
- High: 16 requirements (5 FR + 11 NFR)
- Medium: 4 requirements (1 FR + 3 NFR)

**Source:** `testing/requirements-list.md`

---

### 8.2 Test Coverage

**Functional Test Cases:** 41 test cases covering all 10 FRs
- Foundation tests (Phase 0): 10 test cases
- GraphIndex tests (Phase 1): 15 test cases
- Cross-Index tests (Phase 2-4): 16 test cases

**Non-Functional Test Specifications:** 28 test specs covering all 18 NFRs
- Performance: 8 test specs (3 NFRs)
- Reliability: 7 test specs (4 NFRs)
- Maintainability: 4 test specs (4 NFRs)
- Compatibility: 3 test specs (2 NFRs)
- Scalability: 3 test specs (2 NFRs)
- Usability: 2 test specs (2 NFRs)
- Portability: 1 test spec (1 NFR)

**Integration Scenarios:** 14 multi-component test scenarios

**Total Test Functions Estimated:** 65-90 tests
- Unit tests: 40-50 (60% of tests)
- Integration tests: 20-30 (35% of tests)
- E2E tests: 5-10 (5% of tests)

**Details:**
- `testing/functional-tests.md` - Functional test cases
- `testing/nonfunctional-tests.md` - NFR verification tests
- `testing/test-strategy.md` - Overall testing approach

---

### 8.3 Coverage Targets

**Per-Phase Targets:**

| Phase | Component | Target | Priority |
|-------|-----------|--------|----------|
| 0 | component_helpers.py | ≥ 90% | Critical |
| 1 | GraphIndex | ≥ 80% | Critical |
| 2 | CodeIndex | ≥ 80% | High |
| 3 | StandardsIndex | ≥ 80% | High |
| 4 | IndexManager | ≥ 80% | Critical |

**Enforcement:**
- Pre-commit hook: `pytest --cov-fail-under=80`
- Phase validation gate: Verify coverage before proceeding
- CI/CD: Coverage report uploaded (if applicable)

---

### 8.4 Testing Approach

**Test-Driven Development:**
- Write tests before/alongside implementation
- Red → Green → Refactor cycle

**Test Pyramid:**
```
        /\
       /E2E\          ← Few (5-10): Full cascade scenarios
      /------\
     /Integr-\       ← Some (20-30): Component interactions
    /----------\
   /Unit Tests \     ← Many (40-50): Isolated components
  /--------------\
```

**Unit Testing:**
- Scope: Individual functions/methods
- Isolation: Mock external dependencies (DB, I/O)
- Structure: AAA pattern (Arrange, Act, Assert)
- Organization: `tests/unit/{component}/`

**Integration Testing:**
- Scope: Component interactions
- Database: Real DuckDB (tmpfile or in-memory)
- Focus: Partial degradation, targeted rebuild, cascade
- Organization: `tests/integration/`

**E2E Testing:**
- Scope: Full system scenarios
- Levels: IndexManager → CodeIndex → GraphIndex → components (4 levels)
- Focus: Server startup cascade, backward compatibility
- Organization: `tests/e2e/`

**Mocking Strategy:**
- Mock: External APIs, DB (in unit tests), file I/O, time
- Don't mock: Units under test, data structures, integration components

**Source:** `testing/test-strategy.md`

---

### 8.5 Test Execution

**Commands:**

```bash
# Run all tests
pytest ouroboros/tests/ -v

# Run with coverage
pytest ouroboros/tests/ --cov=ouroboros/subsystems/rag --cov-report=term-missing

# Run unit tests only
pytest ouroboros/tests/unit/ -v

# Run integration tests only
pytest ouroboros/tests/integration/ -v

# Run specific test
pytest ouroboros/tests/unit/subsystems/rag/utils/test_component_helpers.py::test_component_descriptor_valid -v

# Run failed tests only
pytest --lf
```

**Coverage Reporting:**

```bash
# HTML coverage report
pytest ouroboros/tests/ --cov=ouroboros/subsystems/rag --cov-report=html
open htmlcov/index.html
```

**CI/CD Integration:**
- Pre-commit hooks run tests automatically
- Blocks commit if tests fail or coverage < 80%
- CI pipeline runs full test suite on every commit

---

### 8.6 Testing Checklist

**Before Implementation (Per Phase):**
- [ ] Review functional test cases for this phase
- [ ] Review NFR verification tests
- [ ] Set up test environment (test DB, fixtures)
- [ ] Understand mocking strategy

**During Implementation (Per Task):**
- [ ] Write tests first/alongside code (TDD)
- [ ] Run tests frequently (`pytest`)
- [ ] Verify tests pass
- [ ] Check coverage (`pytest --cov`)
- [ ] Refactor if needed

**Before Task Completion:**
- [ ] All task tests implemented
- [ ] All tests passing (exit code 0)
- [ ] Coverage target met (≥ 80% or ≥ 90% for foundation)
- [ ] No linting errors
- [ ] Tests reviewed with code

**Before Phase Completion:**
- [ ] All phase tests implemented (per phase validation gate)
- [ ] All acceptance criteria met (verified by tests)
- [ ] Integration scenarios passing
- [ ] NFR metrics achieved (performance, reliability targets)
- [ ] Phase validation gate checklist complete

---

### 8.7 Completeness Verification

✅ **All 28 requirements have been:**
1. ✅ Extracted into `requirements-list.md` (10 FR + 18 NFR = 28 total)
2. ✅ Given test cases in `functional-tests.md` (41 test cases for 10 FRs)
3. ✅ Given verification tests in `nonfunctional-tests.md` (28 test specs for 18 NFRs)
4. ✅ Covered by testing approach in `test-strategy.md`

**No requirements are untested.**

**Verification Summary:**
- `requirements-list.md`: 28 requirements
- `functional-tests.md`: 10 FRs covered (41 test cases)
- `nonfunctional-tests.md`: 18 NFRs covered (28 test specs)
- `test-strategy.md`: Test execution strategy defined

**All counts match:** ✅

---

### 8.8 Testing References

**For Implementation:**
- 📄 `testing/requirements-list.md` - All 28 requirements with criteria
- 📄 `testing/functional-tests.md` - 41 functional test cases with setup/assert
- 📄 `testing/nonfunctional-tests.md` - 28 NFR verification tests with metrics
- 📄 `testing/test-strategy.md` - Testing approach, patterns, execution

**Quick Reference:**
- Foundation tests (Phase 0): See functional-tests.md "Foundation Tests" section
- GraphIndex tests (Phase 1): See functional-tests.md "GraphIndex Tests" section
- Performance tests: See nonfunctional-tests.md "Performance Tests" section
- Mocking examples: See test-strategy.md "Mocking Strategy" section

---

## 9. Troubleshooting Guide

### 9.1 Common Issues and Solutions

---

#### Issue 1: ComponentDescriptor ValueError on Registration

**Symptoms:**
```
ValueError: name cannot be empty
ValueError: provides cannot be empty
ValueError: health_check must be callable
```

**Cause:** Missing required parameters or invalid types when creating ComponentDescriptor

**Solution:**
```python
# ❌ Wrong
descriptor = ComponentDescriptor(
    name="",  # Empty name
    provides=[],  # Empty list
    capabilities=["op"],
    health_check="not_callable",  # Not a callable
    rebuild=lambda: None,
)

# ✅ Correct
descriptor = ComponentDescriptor(
    name="ast",
    provides=["ast_nodes"],
    capabilities=["search_ast"],
    health_check=self._check_ast_health,  # Method reference
    rebuild=self._rebuild_ast,
    dependencies=[],  # Optional, defaults to []
)
```

---

#### Issue 2: Lambda Late Binding in Loops

**Symptoms:**
- All components in loop have same health check function
- Last component's health check called for all components

**Cause:** Lambda captures variable reference, not value (late binding)

**Solution:**
```python
# ❌ Wrong
for index_name, index in self._indexes.items():
    self.components[index_name] = ComponentDescriptor(
        health_check=lambda: index.health_check(),  # ❌ All reference same 'index'
        ...
    )

# ✅ Correct: Use default argument binding
for index_name, index in self._indexes.items():
    self.components[index_name] = ComponentDescriptor(
        health_check=lambda idx=index: idx.health_check(),  # ✅ 'idx' bound at creation
        ...
    )
```

---

#### Issue 3: Health Check Raises Exception Instead of Returning Error Status

**Symptoms:**
- Health check crashes with unhandled exception
- System-wide health check fails when one component broken

**Cause:** Component health check method raises exception instead of returning error HealthStatus

**Solution:**
```python
# ❌ Wrong
def _check_ast_health(self) -> HealthStatus:
    count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
    if count == 0:
        raise ValueError("No AST data")  # ❌ Don't raise

# ✅ Correct
def _check_ast_health(self) -> HealthStatus:
    try:
        count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
        if count == 0:
            return HealthStatus(
                healthy=False,
                message="No AST data",
                details={"count": 0, "data_present": False}
            )
        return HealthStatus(healthy=True, ...)
    except Exception as e:
        return HealthStatus(
            healthy=False,
            message=f"Health check failed: {e}",
            details={"error": str(e)}
        )
```

---

#### Issue 4: Rebuild Clears Healthy Component Data

**Symptoms:**
- After AST rebuild, graph data is missing
- Symbols/relationships count = 0 after targeted rebuild

**Cause:** Rebuild clears ALL tables instead of just broken component's tables

**Solution:**
```python
# ❌ Wrong
def _rebuild_ast(self):
    conn.execute("DELETE FROM ast_nodes")
    conn.execute("DELETE FROM symbols")       # ❌ Don't touch graph
    conn.execute("DELETE FROM relationships")  # ❌ Destroys healthy data

# ✅ Correct
def _rebuild_ast(self):
    conn.execute("DELETE FROM ast_nodes")  # ✅ Only AST table
    # Re-parse files and insert AST nodes
```

---

#### Issue 5: hasattr() Not Used for Backward Compatibility

**Symptoms:**
- AttributeError: 'LegacyIndex' has no attribute 'components'
- Mixed environment breaks after IndexManager migration

**Cause:** Code assumes all indexes have .components attribute

**Solution:**
```python
# ❌ Wrong
def _discover_capabilities(self, index):
    caps = []
    for component in index.components.values():  # ❌ Assumes .components exists
        caps.extend(component.capabilities)
    return caps

# ✅ Correct
def _discover_capabilities(self, index):
    if hasattr(index, "components"):  # ✅ Check first
        caps = []
        for component in index.components.values():
            caps.extend(component.capabilities)
        return caps
    else:
        # Legacy fallback
        return [f"search_{index.__class__.__name__.lower()}"]
```

---

#### Issue 6: Health Check Timeout (> 500ms)

**Symptoms:**
- Full cascade health check takes > 500ms
- Individual component health checks > 50ms

**Cause:** Slow database queries, missing indexes, or too many components

**Solution:**

**Diagnose:**
```python
import time

# Add timing to health checks
start = time.perf_counter()
status = index.health_check()
duration = time.perf_counter() - start
print(f"Health check took {duration:.3f}s")
```

**Optimize:**
```sql
-- Add indexes if missing
CREATE INDEX idx_ast_nodes_file ON ast_nodes(file_path);
CREATE INDEX idx_symbols_name ON symbols(name);

-- Optimize COUNT queries
SELECT COUNT(*) FROM ast_nodes;  -- Should be < 10ms
```

**If still slow:**
- Check database file size (vacuum if needed)
- Reduce component count (combine similar components)
- Cache health check results (careful: may miss actual issues)

---

#### Issue 7: Targeted Rebuild Still Takes 30s

**Symptoms:**
- _rebuild_ast() takes as long as full rebuild
- Speedup factor < 10x

**Cause:** Rebuild is doing more than necessary (e.g., rebuilding graph too)

**Diagnose:**
```python
import time

start = time.perf_counter()
index._rebuild_ast()
duration = time.perf_counter() - start
print(f"Rebuild took {duration:.1f}s")  # Should be < 3s
```

**Solution:**
- Verify only AST table cleared (not symbols/relationships)
- Check if graph rebuild accidentally called
- Profile to find bottleneck

---

### 9.2 Debugging Techniques

**Python Debugger (pdb):**
```python
import pdb

def _check_ast_health(self):
    pdb.set_trace()  # Breakpoint here
    count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
    # Step through code
```

**Logging:**
```python
import logging

logger = logging.getLogger(__name__)

def _check_ast_health(self):
    logger.debug("Checking AST health")
    count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
    logger.info(f"AST count: {count}")
    # ...
```

**Inspect Health Check Response:**
```python
health = index.health_check()
print(health)
print(health.details)
print(health.details["components"])
print(health.details["capabilities"])
```

**Database Inspection:**
```python
conn = index.db_connection.get_connection()

# Check table counts
ast_count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
symbol_count = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
print(f"AST: {ast_count}, Symbols: {symbol_count}")

# Check schema
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(f"Tables: {tables}")
```

**Verify Component Registration:**
```python
index = GraphIndex(config, base_path, languages)
print(f"Components: {list(index.components.keys())}")
for name, comp in index.components.items():
    print(f"{name}: {comp.provides}, {comp.capabilities}")
```

---

### 9.3 Performance Debugging

**Profile Health Check:**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

status = index.health_check()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slowest functions
```

**Measure Component-Level Performance:**
```python
import time

for comp_name, component in index.components.items():
    start = time.perf_counter()
    health = component.health_check()
    duration = time.perf_counter() - start
    print(f"{comp_name}: {duration*1000:.1f}ms")
```

**Memory Profiling:**
```python
import sys

descriptor = ComponentDescriptor(...)
size = sys.getsizeof(descriptor)
print(f"ComponentDescriptor size: {size} bytes")
```

**Database Query Performance:**
```sql
-- Enable query timing
.timer on

-- Run slow query
SELECT COUNT(*) FROM ast_nodes;

-- Check if indexes help
EXPLAIN QUERY PLAN SELECT COUNT(*) FROM ast_nodes;
```

---

### 9.4 Test Debugging

**Run Single Test:**
```bash
pytest ouroboros/tests/unit/subsystems/rag/utils/test_component_helpers.py::test_component_descriptor_valid -v -s
# -v: verbose
# -s: show print statements
```

**Debug Test with pdb:**
```python
def test_component_descriptor_valid():
    import pdb; pdb.set_trace()
    descriptor = ComponentDescriptor(...)
```

**Check Test Coverage:**
```bash
pytest ouroboros/tests/ --cov=ouroboros/subsystems/rag/utils/component_helpers --cov-report=term-missing
# Shows which lines not covered
```

**Run Failed Tests Only:**
```bash
pytest --lf  # Last failed
pytest --ff  # Failed first, then rest
```

---

### 9.5 Integration Test Debugging

**Check Test Database:**
```python
import pytest
import tempfile

@pytest.fixture
def test_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        print(f"Test DB: {f.name}")  # Print path for inspection
        yield f.name
    # Comment out cleanup to inspect DB after test
    # os.unlink(f.name)
```

**Inspect Database After Test:**
```bash
# Use printed path from above
duckdb /tmp/test_xyz.db

# Check tables
SHOW TABLES;

# Check counts
SELECT COUNT(*) FROM ast_nodes;
SELECT COUNT(*) FROM symbols;
```

---

### 9.6 Common Test Failures

**Test: `test_partial_degradation_ast_broken_graph_healthy` fails**

**Symptom:** `find_callers()` raises exception instead of succeeding

**Cause:** Graph component incorrectly depends on AST

**Solution:** Verify GraphIndex components have `dependencies=[]` (not dependent)

---

**Test: `test_dynamic_health_check_component_exception` fails**

**Symptom:** Exception not caught, test crashes

**Cause:** `dynamic_health_check()` missing try/except around `component.health_check()`

**Solution:** Add exception handling:
```python
for comp_name, component in components.items():
    try:
        health = component.health_check()
    except Exception as e:
        logger.error(f"Health check failed for {comp_name}: {e}")
        health = HealthStatus(
            healthy=False,
            message=f"Exception: {e}",
            details={"error": str(e)}
        )
```

---

### 9.7 Getting Help

**Before Asking:**
1. Check this troubleshooting guide
2. Review code patterns (section 3)
3. Check test examples in `testing/` directory
4. Search standards: `pos_search_project(query="your issue")`

**When Asking for Help, Include:**
1. **What you're trying to do** (e.g., "Adding imports component to GraphIndex")
2. **What you expected** (e.g., "Health check should show 3 components")
3. **What actually happened** (e.g., "AttributeError: 'ComponentDescriptor' object has no attribute 'capabilities'")
4. **Code snippet** (relevant 10-20 lines)
5. **Error message** (full traceback)
6. **What you've tried** (e.g., "Checked ComponentDescriptor definition, verified all required params")

**Resources:**
- **Specifications:** This directory (`specs/review/2025-11-08-cascading-health-check-architecture/`)
- **Design Doc:** `supporting-docs/2025-11-08-cascading-health-check-architecture.md`
- **Test Examples:** `testing/functional-tests.md`, `testing/test-strategy.md`
- **Standards:** Query with `pos_search_project(query="...")`

---

### 9.8 Debugging Checklist

**When Something Doesn't Work:**
- [ ] Read error message carefully (what line? what type?)
- [ ] Check if component registered correctly (`print(index.components)`)
- [ ] Verify lambda binding uses default arguments
- [ ] Check hasattr() for backward compatibility
- [ ] Verify health check returns HealthStatus (not raises)
- [ ] Check database (counts, schema)
- [ ] Add logging/print statements
- [ ] Run single test in isolation
- [ ] Check test database after failure
- [ ] Search standards for similar issues
- [ ] Review code patterns (section 3)

**If Still Stuck:**
- Ask for help with context (see section 9.7)
- Create minimal reproduction case
- Check if issue is in foundation or specific index

---

