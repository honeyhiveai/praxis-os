# Cascading Health Check Architecture

**Date**: 2025-11-08  
**Status**: Design  
**Author**: AI Assistant (with Josh)

---

## 🎯 Problem Statement

### Current Architecture Issues

The RAG subsystem has a complex hierarchy of indexes and sub-indexes:

```
IndexManager
├─ StandardsIndex
│  ├─ Vector index
│  ├─ FTS index
│  └─ Scalar indexes
│
└─ CodeIndex
   ├─ SemanticIndex
   │  ├─ Vector index
   │  └─ FTS index
   │
   └─ GraphIndex
      ├─ AST nodes table (structural search)
      ├─ Symbols table (graph nodes)
      └─ Relationships table (graph edges)
```

**Current health check implementation has critical flaws:**

1. **Static Logic**: Each index has hardcoded if/else chains for health checks
2. **Coarse-Grained Status**: GraphIndex reports ONE boolean (healthy/unhealthy) despite having THREE independent components
3. **False Positive Rebuilds**: If AST is broken but graph traversal works, we rebuild EVERYTHING
4. **No Partial Degradation**: `find_callers()` fails even when only AST extraction is broken
5. **Maintenance Burden**: Adding new component requires updating multiple places in code
6. **Poor Diagnostics**: "CodeIndex unhealthy" - but which part? Why?

### Real-World Example

GraphIndex currently does:

```python
def health_check(self) -> HealthStatus:
    stats = self.traversal.get_stats()
    
    # PROBLEM: OR condition couples independent features
    if stats["ast_node_count"] == 0 or stats["symbol_count"] == 0:
        return HealthStatus(healthy=False, message="unhealthy")
```

**Issues:**
- AST and graph traversal are COMPLETELY independent
- AST empty → flags entire GraphIndex as unhealthy → blocks `find_callers()` which doesn't need AST!
- No way to rebuild just AST without touching graph data
- Adding new component (e.g., imports graph) requires updating this logic

---

## 🎯 Goals

### Primary Goals

1. **Dynamic Discovery**: System discovers its own structure via component registry
2. **Granular Health**: Each component reports health independently
3. **Targeted Rebuilds**: Rebuild only what's broken, not entire indexes
4. **Partial Degradation**: Healthy components continue working when others fail
5. **Self-Similar Pattern**: Same pattern repeats at every level (fractal architecture)
6. **Zero Code Changes**: Adding new component = add registry entry, no logic changes

### Success Criteria

- [ ] Adding new component to any index requires ZERO changes to IndexManager
- [ ] Health check can report "AST broken, graph operational" with precise counts
- [ ] Rebuild system can target specific component (e.g., rebuild AST only)
- [ ] Capability discovery: Query system for "what operations are currently available?"
- [ ] Pattern works identically at all levels (GraphIndex, CodeIndex, IndexManager)

---

## 🏗️ Architecture

### Core Pattern: Component Registry

Every level of the RAG hierarchy uses the same pattern:

1. **Components register themselves** with descriptive metadata
2. **Health checks discover** registered components dynamically
3. **Rebuild decisions** based on component-specific health data
4. **Capabilities inferred** from component health status

### Component Descriptor

```python
class ComponentDescriptor:
    """Self-describing component for dynamic health checking.
    
    This is the core abstraction that enables the fractal pattern.
    Used identically at every level of the hierarchy.
    """
    
    def __init__(
        self,
        name: str,                      # Component identifier
        provides: List[str],            # What data does it provide?
        capabilities: List[str],        # What operations can it support?
        health_check: Callable,         # How to check health?
        rebuild: Callable,              # How to rebuild?
        dependencies: List[str] = None, # What does it depend on?
    ):
        self.name = name
        self.provides = provides
        self.capabilities = capabilities
        self.health_check = health_check
        self.rebuild = rebuild
        self.dependencies = dependencies or []
```

### Level 4: GraphIndex (Lowest Level)

```python
class GraphIndex(BaseIndex):
    """Graph index with AST and graph traversal components."""
    
    def __init__(self, config, base_path, languages):
        # ... existing initialization ...
        
        # REGISTER COMPONENTS (declarative, discoverable)
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
                dependencies=[],  # Independent of AST
            ),
        }
    
    def _check_ast_health(self) -> Dict[str, Any]:
        """Check AST component (returns data, not boolean)."""
        conn = self.db_connection.get_connection()
        
        try:
            count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
            test = conn.execute("SELECT * FROM ast_nodes LIMIT 1").fetchone()
            
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
    
    def _check_graph_health(self) -> Dict[str, Any]:
        """Check graph component (returns data, not boolean)."""
        # Similar pattern...
    
    def health_check(self) -> HealthStatus:
        """Dynamic health check - discovers all components."""
        return dynamic_health_check(self.components)  # ← Shared helper!
```

### Level 3: CodeIndex (Aggregator)

```python
class CodeIndex(BaseIndex):
    """Container aggregating SemanticIndex + GraphIndex."""
    
    def __init__(self, config, base_path):
        # Initialize sub-indexes
        self.semantic = SemanticIndex(config.vector, base_path)
        self.graph = GraphIndex(config.graph, base_path, config.languages)
        
        # REGISTER SUB-INDEXES AS COMPONENTS (same pattern!)
        self.components = {
            "semantic": ComponentDescriptor(
                name="semantic",
                provides=["code_embeddings", "code_fts"],
                capabilities=["search_code"],
                health_check=lambda: self.semantic.health_check(),  # Delegate
                rebuild=lambda: self.semantic.build(self.config.sources, force=True),
                dependencies=[],
            ),
            "graph": ComponentDescriptor(
                name="graph",
                provides=["ast", "symbols", "relationships"],
                capabilities=["search_ast", "find_callers", "find_dependencies", "find_call_paths"],
                health_check=lambda: self.graph.health_check(),  # Delegate
                rebuild=lambda: self.graph.build(self.config.sources, force=True),
                dependencies=[],
            ),
        }
    
    def health_check(self) -> HealthStatus:
        """Same pattern, different level."""
        return dynamic_health_check(self.components)  # ← Same helper!
```

### Level 2: StandardsIndex (Sibling)

```python
class StandardsIndex(BaseIndex):
    """Standards documentation with vector + FTS + reranker."""
    
    def __init__(self, config, base_path):
        # ... initialization ...
        
        # SAME PATTERN at this level
        self.components = {
            "vector": ComponentDescriptor(
                name="vector",
                provides=["embeddings"],
                capabilities=["vector_search"],
                health_check=self._check_vector_health,
                rebuild=self._rebuild_vector,
                dependencies=[],
            ),
            "fts": ComponentDescriptor(
                name="fts",
                provides=["full_text_index"],
                capabilities=["keyword_search"],
                health_check=self._check_fts_health,
                rebuild=self._rebuild_fts,
                dependencies=["vector"],  # Built after vector
            ),
            "reranker": ComponentDescriptor(
                name="reranker",
                provides=["reranking"],
                capabilities=["hybrid_search"],
                health_check=self._check_reranker_health,
                rebuild=self._rebuild_reranker,
                dependencies=["vector", "fts"],
            ),
        }
    
    def health_check(self) -> HealthStatus:
        """Same pattern everywhere."""
        return dynamic_health_check(self.components)
```

### Level 1: IndexManager (Top Level)

```python
class IndexManager:
    """Orchestrator - uses same pattern at top level!"""
    
    def __init__(self, config, base_path):
        # Initialize indexes
        self._indexes = self._init_indexes()
        
        # REGISTER TOP-LEVEL INDEXES AS COMPONENTS
        self.components = {}
        
        for index_name, index in self._indexes.items():
            # Discover capabilities dynamically
            capabilities = self._discover_capabilities(index)
            
            self.components[index_name] = ComponentDescriptor(
                name=index_name,
                provides=[index_name],
                capabilities=capabilities,
                health_check=lambda idx=index: idx.health_check(),
                rebuild=lambda name=index_name: self.rebuild_index(name, force=True),
                dependencies=[],
            )
    
    def _discover_capabilities(self, index: BaseIndex) -> List[str]:
        """Dynamic capability discovery."""
        if hasattr(index, "components"):
            # Aggregate from sub-components
            caps = []
            for component in index.components.values():
                caps.extend(component.capabilities)
            return caps
        else:
            # Legacy index
            return [f"search_{index.__class__.__name__.lower()}"]
    
    def ensure_healthy_with_rebuild(self) -> Dict[str, Any]:
        """Dynamic rebuild based on component health."""
        health = self.health_check_all()
        rebuild_actions = []
        
        for index_name, status in health.items():
            if status.healthy:
                continue
            
            # DYNAMIC: Find what needs rebuilding
            actions = self._find_rebuild_actions(index_name, status)
            rebuild_actions.extend(actions)
        
        # Execute rebuilds
        for action in rebuild_actions:
            logger.info("🔨 %s", action["description"])
            action["rebuild_fn"]()
        
        return {"rebuild_actions": rebuild_actions, "final_health": self.health_check_all()}
    
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
                            "path": f"{parent_name}.{sub_name}",
                            "description": f"Rebuild {parent_name}.{sub_name}: {sub_health.get('message')}",
                            "rebuild_fn": sub_component.rebuild,
                        })
        else:
            # Leaf component
            component = self.components[parent_name]
            actions.append({
                "path": parent_name,
                "description": f"Rebuild {parent_name}: {status.message}",
                "rebuild_fn": component.rebuild,
            })
        
        return actions
```

### Shared Helper (DRY!)

```python
# In ouroboros/subsystems/rag/utils/component_helpers.py

def dynamic_health_check(components: Dict[str, ComponentDescriptor]) -> HealthStatus:
    """Generic dynamic health check - works at ANY level!
    
    Used identically by:
    - GraphIndex (checking ast + graph)
    - CodeIndex (checking semantic + graph)
    - StandardsIndex (checking vector + fts + reranker)
    - IndexManager (checking standards + code)
    """
    component_health = {}
    all_capabilities = {}
    
    for comp_name, component in components.items():
        # Call component's health check
        health_status = component.health_check()
        
        component_health[comp_name] = {
            "healthy": health_status.healthy,
            "message": health_status.message,
            "details": health_status.details,
        }
        
        # Map capabilities dynamically
        for capability in component.capabilities:
            all_capabilities[capability] = health_status.healthy
    
    overall_healthy = all(c["healthy"] for c in component_health.values())
    
    messages = [
        f"{name}: {health['message']}" 
        for name, health in component_health.items()
    ]
    
    return HealthStatus(
        healthy=overall_healthy,
        message="; ".join(messages),
        details={
            "components": component_health,
            "capabilities": all_capabilities,
        }
    )
```

---

## 🌳 The Fractal Pattern

```
IndexManager (uses component pattern)
├─ standards (ComponentDescriptor)
│  └─ StandardsIndex (uses component pattern)
│     ├─ vector (ComponentDescriptor)
│     ├─ fts (ComponentDescriptor)
│     └─ reranker (ComponentDescriptor)
│
└─ code (ComponentDescriptor)
   └─ CodeIndex (uses component pattern)
      ├─ semantic (ComponentDescriptor)
      │  └─ SemanticIndex (uses component pattern)
      │     ├─ vector (ComponentDescriptor)
      │     └─ fts (ComponentDescriptor)
      │
      └─ graph (ComponentDescriptor)
         └─ GraphIndex (uses component pattern)
            ├─ ast (ComponentDescriptor)
            └─ graph (ComponentDescriptor)
```

**Key insight**: The pattern is self-similar at every scale. Each level:
1. Registers components
2. Uses `dynamic_health_check()` helper
3. Aggregates sub-component health
4. Exposes capabilities dynamically

---

## 📊 Example: Health Check Flow

### User Query: `find_callers("my_function")`

```
Request: find_callers("my_function")
        ↓
    IndexManager
        ↓
"Is code index healthy?"
        ↓
    CodeIndex.health_check()
        ↓
┌───────────────────┬────────────────────┐
│                   │                    │
Semantic.health_check()  Graph.health_check()
│                   │
"✅ Vector: 5000"   ├─ AST: _check_ast_health()
"✅ FTS: ready"     │  "❌ 0 nodes, query fails"
│                   │
│                   └─ Graph: _check_graph_health()
│                      "✅ 500 symbols, 1200 edges"
│                   │
└───────────────────┴────────────────────┘
                    ↓
            Graph reports:
            healthy=False (AST broken)
            BUT capabilities:
              - search_ast: False ❌
              - find_callers: True ✅
              - find_dependencies: True ✅
                    ↓
            IndexManager sees:
            "Graph traversal operational,
             AST search broken"
                    ↓
            DECISION: Allow query
            (capability available)
                    ↓
            find_callers() succeeds! ✅
```

### Rebuild Decision Flow

```
IndexManager.ensure_healthy_with_rebuild()
        ↓
"Code index unhealthy, drill down..."
        ↓
Check CodeIndex.components:
  - semantic: ✅ healthy
  - graph: ❌ unhealthy
        ↓
Check GraphIndex.components:
  - ast: ❌ unhealthy (0 nodes)
  - graph: ✅ healthy (500 symbols)
        ↓
DECISION: Rebuild code.graph.ast ONLY
        ↓
Execute: code.graph.components["ast"].rebuild()
        ↓
Result:
  - AST rebuilt: 250 nodes
  - Graph untouched: 500 symbols preserved
  - Total time: 2s (vs 30s for full rebuild)
```

---

## ✨ Benefits

### 1. Zero Code Changes for New Components

**Before (Static):**
```python
# Adding new "imports" component requires changes in 5+ places:

# 1. Update GraphIndex.health_check():
if stats["ast_node_count"] == 0 or stats["symbol_count"] == 0 or stats["import_count"] == 0:
    # ...

# 2. Update IndexManager rebuild decision tree:
if not ast_health and not graph_health and not import_health:
    # ...
elif not ast_health and graph_health and import_health:
    # ...
# (12 more combinations!)

# 3. Update capability mapping:
capabilities = {
    "search_ast": ast_healthy,
    "find_callers": graph_healthy,
    "find_imports": import_healthy,  # Added
}

# 4. Update rebuild methods...
# 5. Update diagnostics...
```

**After (Dynamic):**
```python
# Just add to registry:
self.components["imports"] = ComponentDescriptor(
    name="imports",
    provides=["import_relationships"],
    capabilities=["find_import_dependencies"],
    health_check=self._check_imports_health,
    rebuild=self._rebuild_imports,
    dependencies=["symbols"],
)

# That's it! Everything else works automatically.
```

### 2. Granular Diagnostics

**Before:**
```
❌ CodeIndex: unhealthy
```

**After:**
```
❌ CodeIndex: unhealthy
   ├─ ✅ Semantic: operational (5000 embeddings, FTS ready)
   └─ ❌ Graph: partially operational
      ├─ ❌ AST: 0 nodes, query fails (DuckDB table empty)
      └─ ✅ Graph: 500 symbols, 1200 edges, queries working

Capabilities:
  - search_code: ✅ Available
  - search_ast: ❌ Unavailable
  - find_callers: ✅ Available
  - find_dependencies: ✅ Available
  - find_call_paths: ✅ Available

Recommended action: Rebuild code.graph.ast (2s rebuild vs 30s full rebuild)
```

### 3. Targeted Rebuilds

```bash
# Before: Rebuild everything (30s)
Rebuilding code index...
  - Clearing semantic data... (10s)
  - Re-embedding 5000 chunks... (15s)
  - Clearing graph data... (1s)
  - Re-parsing AST... (2s)
  - Re-extracting symbols... (2s)
Total: 30s

# After: Rebuild only what's broken (2s)
Rebuilding code.graph.ast...
  - Clearing AST nodes... (0.1s)
  - Re-parsing AST... (2s)
Total: 2.1s

# Preserved:
  - 5000 embeddings (semantic)
  - 500 symbols (graph)
  - 1200 relationships (graph)
```

### 4. Partial Degradation

```python
# AST broken, graph operational:
pos_search_project(action="search_ast", query="function")
# Returns: {"status": "error", "message": "AST index unhealthy"}

pos_search_project(action="find_callers", query="my_function")
# Returns: {"status": "success", "results": [...]}  ← Still works!
```

### 5. Self-Maintaining Code

```python
# IndexManager doesn't need to know about GraphIndex internals:

def ensure_healthy_with_rebuild(self):
    """Works with ANY index that has .components attribute."""
    for index_name, status in self.health_check_all().items():
        if not status.healthy:
            actions = self._find_rebuild_actions(index_name, status)
            # ↑ Discovers structure dynamically
            for action in actions:
                action["rebuild_fn"]()  # Component knows how to rebuild itself
```

---

## 🎯 Implementation Strategy

### Phase 0: Foundation
- [ ] Create `ComponentDescriptor` class
- [ ] Create `dynamic_health_check()` helper
- [ ] Add tests for helper function

### Phase 1: GraphIndex (Pilot)
- [ ] Refactor GraphIndex to use component pattern
- [ ] Split `_check_ast_health()` and `_check_graph_health()`
- [ ] Implement `_rebuild_ast()` and `_rebuild_graph()`
- [ ] Update `health_check()` to use `dynamic_health_check()`
- [ ] Test: AST broken, graph works → find_callers succeeds

### Phase 2: CodeIndex
- [ ] Refactor CodeIndex to register semantic + graph as components
- [ ] Update health_check() to use pattern
- [ ] Test: Semantic broken, graph works → find_callers succeeds

### Phase 3: StandardsIndex
- [ ] Refactor to register vector + fts + reranker
- [ ] Test: FTS broken, vector works → vector_search succeeds

### Phase 4: IndexManager
- [ ] Refactor to register top-level indexes as components
- [ ] Update `ensure_healthy_with_rebuild()` to use dynamic discovery
- [ ] Update `_find_rebuild_actions()` for recursive drilling
- [ ] Test: Full cascade from server startup

### Phase 5: Documentation
- [ ] Document ComponentDescriptor pattern in standards
- [ ] Add "how to add new component" guide
- [ ] Update RAG architecture diagrams

---

## 🔄 Migration Path

### Backward Compatibility

Indexes without `.components` attribute continue to work:

```python
# Old index without component pattern
class LegacyIndex(BaseIndex):
    def health_check(self):
        # Old implementation
        return HealthStatus(...)

# IndexManager handles both:
if hasattr(index, "components"):
    # New dynamic pattern
    capabilities = self._discover_capabilities(index)
else:
    # Legacy fallback
    capabilities = [f"search_{index.__class__.__name__.lower()}"]
```

### Gradual Rollout

1. Implement foundation (Phase 0)
2. Migrate GraphIndex first (pilot, most benefit)
3. Test in production
4. Migrate CodeIndex
5. Migrate StandardsIndex
6. Update IndexManager last (when all sub-indexes migrated)

---

## 🚨 Risks & Mitigations

### Risk 1: Circular Dependencies

**Problem**: Component A depends on B, B depends on A

**Mitigation**:
- Document dependency rules
- Add validation in ComponentDescriptor.__init__()
- Detect cycles at registration time

### Risk 2: Performance Overhead

**Problem**: Health checks now call through multiple layers

**Mitigation**:
- Health checks are already infrequent (server startup, manual trigger)
- Dynamic discovery is one-time at init
- Actual queries cached in-memory

### Risk 3: Complexity

**Problem**: Pattern may be hard to understand for new contributors

**Mitigation**:
- Excellent documentation
- Clear examples
- Uniform pattern reduces cognitive load (same everywhere)
- Self-documenting: Component registry shows structure

---

## 📚 Related Standards

Query for implementation guidance:
- `pos_search_project(content_type="standards", query="RAG architecture patterns")`
- `pos_search_project(content_type="standards", query="dynamic vs static patterns")`
- `pos_search_project(content_type="standards", query="health check best practices")`

---

## ✅ Success Metrics

After implementation:

1. **Add imports component to GraphIndex**:
   - Lines of code changed in IndexManager: 0
   - Lines of code changed in CodeIndex: 0
   - Lines of code changed in GraphIndex: ~30 (just registry entry + methods)

2. **Rebuild time for AST-only failure**:
   - Before: 30s (full rebuild)
   - After: 2s (targeted rebuild)
   - Speedup: 15x

3. **Partial degradation test**:
   - AST broken, graph operational
   - `find_callers()` success rate: 100%
   - `search_ast()` failure rate: 100% (expected)

4. **Diagnostic clarity**:
   - Before: "CodeIndex unhealthy" (1 boolean)
   - After: 5+ component-level statuses + capabilities map

---

**This design enables a self-similar, fractal architecture where adding complexity doesn't increase maintenance burden.**

