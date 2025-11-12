# Extracted Insights

**Spec:** Cascading Health Check Architecture  
**Extracted:** 2025-11-10  
**Source:** 2025-11-08-cascading-health-check-architecture.md

---

## Requirements Insights (Phase 1)

### From Design Document:

**User Needs:**
- **Need:** Rebuild only broken components, not entire indexes (AST broken → rebuild AST only, not entire GraphIndex)
- **Need:** Continue using healthy components when others fail (AST broken but `find_callers()` should still work)
- **Need:** Clear diagnostics showing exactly what's broken and where (not "CodeIndex unhealthy" but "code.graph.ast: 0 nodes, query fails")
- **Need:** Add new components without updating logic in 5+ places

**Business Goals:**
- **Goal:** Reduce rebuild time from 30s to 2s for targeted component failures (15x speedup)
- **Goal:** Zero code changes in IndexManager when adding new component to any index
- **Goal:** Enable partial degradation (operational components continue working)
- **Goal:** Self-maintaining architecture (adding complexity doesn't increase maintenance burden)

**Functional Requirements:**
- **Req:** Health checks must report status for each component independently
- **Req:** System must discover its own structure via component registry (no hardcoded if/else)
- **Req:** Rebuild system must target specific broken components
- **Req:** Capability discovery must be dynamic ("what operations are currently available?")
- **Req:** Pattern must work identically at all hierarchy levels (GraphIndex, CodeIndex, IndexManager)

**Constraints:**
- **Constraint:** Must maintain backward compatibility with indexes that don't use component pattern
- **Constraint:** Health checks are infrequent (server startup, manual trigger) so performance overhead acceptable
- **Constraint:** Each component must know how to check its own health and rebuild itself

**Out-of-Scope:**
- Real-time health monitoring (checks are manual/startup only)
- Automatic remediation (system identifies problems but doesn't auto-fix)
- Cross-component dependency resolution algorithms (components declare dependencies but system doesn't resolve)

---

## Design Insights (Phase 2)

### From Design Document:

**Architecture Patterns:**
- **Pattern:** Fractal/self-similar component registry (same pattern at every level)
- **Pattern:** Dynamic discovery vs static if/else chains
- **Pattern:** Capability-based operations (check if capability available before calling)
- **Pattern:** Fail-safe partial degradation (unhealthy components don't block healthy ones)

**Core Components:**

1. **ComponentDescriptor** (Foundation)
   - **Purpose:** Self-describing component for dynamic health checking
   - **Attributes:**
     - `name`: Component identifier
     - `provides`: List of data types component provides (e.g., ["ast_nodes"])
     - `capabilities`: List of operations component supports (e.g., ["search_ast"])
     - `health_check`: Callable that returns Dict[str, Any] with health data
     - `rebuild`: Callable that rebuilds the component
     - `dependencies`: List of component names this depends on
   - **Used at:** All 4 levels (GraphIndex, CodeIndex, StandardsIndex, IndexManager)

2. **dynamic_health_check() Helper** (DRY Principle)
   - **Purpose:** Generic health check function that works at ANY level
   - **Input:** Dict[str, ComponentDescriptor]
   - **Output:** HealthStatus with aggregated component health + capability map
   - **Location:** `ouroboros/subsystems/rag/utils/component_helpers.py`
   - **Used by:** All indexes and IndexManager

**Four-Level Hierarchy:**

1. **Level 4 - GraphIndex** (Lowest):
   - **Components:** "ast", "graph"
   - **AST component:** Provides ast_nodes, supports search_ast
   - **Graph component:** Provides symbols/relationships, supports find_callers/find_dependencies/find_call_paths
   - **Key:** AST and graph are INDEPENDENT (one broken doesn't block the other)

2. **Level 3 - CodeIndex** (Aggregator):
   - **Components:** "semantic", "graph"
   - **Semantic component:** Delegates to SemanticIndex (vector + FTS)
   - **Graph component:** Delegates to GraphIndex (AST + graph)
   - **Key:** Sub-indexes registered AS components (composition)

3. **Level 2 - StandardsIndex** (Sibling):
   - **Components:** "vector", "fts", "reranker"
   - **Dependencies:** FTS depends on vector, reranker depends on both
   - **Key:** Shows dependency chain (vector → fts → reranker)

4. **Level 1 - IndexManager** (Top):
   - **Components:** "standards", "code"
   - **Discovery:** Aggregates capabilities from sub-components dynamically
   - **Rebuild:** Uses _find_rebuild_actions() to drill down recursively

**Data Models:**

**ComponentDescriptor:**
```python
class ComponentDescriptor:
    name: str
    provides: List[str]
    capabilities: List[str]
    health_check: Callable[[], HealthStatus]
    rebuild: Callable[[], None]
    dependencies: List[str]
```

**HealthStatus:**
```python
class HealthStatus:
    healthy: bool
    message: str
    details: Dict[str, Any]  # includes "components" and "capabilities"
```

**Component Health Dict:**
```python
{
    "healthy": bool,
    "message": str,
    "details": {
        "data_present": bool,
        "query_works": bool,
        "count": int,
        "error": Optional[str]
    }
}
```

**APIs:**

**Component Registration:**
```python
self.components = {
    "ast": ComponentDescriptor(
        name="ast",
        provides=["ast_nodes"],
        capabilities=["search_ast"],
        health_check=self._check_ast_health,
        rebuild=self._rebuild_ast,
        dependencies=[],
    ),
}
```

**Health Check:**
```python
def health_check(self) -> HealthStatus:
    return dynamic_health_check(self.components)
```

**Capability Discovery:**
```python
def _discover_capabilities(self, index: BaseIndex) -> List[str]:
    if hasattr(index, "components"):
        caps = []
        for component in index.components.values():
            caps.extend(component.capabilities)
        return caps
    else:
        return [f"search_{index.__class__.__name__.lower()}"]
```

**Security:**
- No explicit security requirements (internal subsystem)
- Component health checks must not expose sensitive data

---

## Implementation Insights (Phase 4)

### From Design Document:

**Code Patterns:**

1. **Component Registration Pattern:**
```python
def __init__(self, config, base_path):
    # ... existing init ...
    
    self.components = {
        "component_name": ComponentDescriptor(
            name="component_name",
            provides=["data_type"],
            capabilities=["operation"],
            health_check=self._check_component_health,
            rebuild=self._rebuild_component,
            dependencies=[],
        ),
    }
```

2. **Health Check Pattern:**
```python
def _check_component_health(self) -> Dict[str, Any]:
    """Returns data dict, NOT boolean."""
    try:
        count = # ... query component ...
        test = # ... test query ...
        return {
            "data_present": count > 0,
            "query_works": test is not None,
            "count": count,
            "error": None,
        }
    except Exception as e:
        return {
            "data_present": False,
            "query_works": False,
            "count": 0,
            "error": str(e),
        }
```

3. **Backward Compatibility Pattern:**
```python
if hasattr(index, "components"):
    # New dynamic pattern
    capabilities = self._discover_capabilities(index)
else:
    # Legacy fallback
    capabilities = [f"search_{index.__class__.__name__.lower()}"]
```

**Testing Strategy:**

**Phase 1 Tests (GraphIndex):**
- Test: AST broken, graph operational → find_callers() succeeds
- Test: Graph broken, AST operational → search_ast() succeeds
- Test: Both broken → both operations fail
- Test: Component health check returns correct data structure

**Phase 2 Tests (CodeIndex):**
- Test: Semantic broken, graph operational → find_callers() succeeds
- Test: Health check aggregates from sub-components correctly

**Phase 4 Tests (IndexManager):**
- Test: Full cascade from server startup
- Test: _find_rebuild_actions() correctly drills down to broken component
- Test: Targeted rebuild only rebuilds broken component (verify preserved data)

**Unit Test Focus:**
- ComponentDescriptor instantiation and validation
- dynamic_health_check() helper with various component combinations
- Component registration edge cases (duplicate names, missing health_check, etc.)

**Integration Test Focus:**
- End-to-end health check from IndexManager → CodeIndex → GraphIndex → components
- Rebuild flow targeting specific broken component
- Partial degradation scenarios (some components broken, others operational)

**Deployment:**

**Migration Phases:**
1. **Phase 0:** Create ComponentDescriptor + dynamic_health_check()
2. **Phase 1:** Migrate GraphIndex (pilot, most benefit)
3. **Phase 2:** Migrate CodeIndex
4. **Phase 3:** Migrate StandardsIndex
5. **Phase 4:** Migrate IndexManager (after all sub-indexes migrated)

**Rollout Strategy:**
- Gradual (phase-by-phase)
- Test in production after each phase
- Backward compatibility maintained throughout
- Can roll back individual phases if issues arise

**Monitoring:**
- Track rebuild times (target: 2s for AST-only vs 30s for full)
- Track partial degradation success rate (target: 100% for independent components)
- Monitor for false positives (healthy reported as unhealthy)

---

## Cross-References

**Validated by Multiple Sources:**
- N/A (single source document)

**Conflicts:**
- None

**High-Priority Items:**
1. **ComponentDescriptor implementation** (foundation for entire pattern)
2. **dynamic_health_check() helper** (DRY principle, used everywhere)
3. **GraphIndex migration** (pilot, highest impact, proves pattern works)
4. **Backward compatibility** (must not break existing indexes)
5. **AST/graph independence** (core problem being solved)

---

## Insight Summary

**Total:** 45 insights  
**By Category:** Requirements [15], Design [20], Implementation [10]  
**Multi-source validated:** 0 (single source)  
**Conflicts to resolve:** 0  
**High-priority items:** 5

**Key Takeaways:**
1. The fractal pattern is the core innovation (same abstraction at every level)
2. Backward compatibility is critical (legacy indexes must continue working)
3. Testing strategy focuses on partial degradation scenarios (core benefit)
4. Migration is phased and reversible (low risk)
5. Success metrics are quantifiable (15x speedup, 100% partial degradation, 0 IndexManager changes)

**Phase 0 Complete:** ✅ 2025-11-10

