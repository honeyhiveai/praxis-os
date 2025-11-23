# Fractal Pattern Analysis: RAG Subsystem Architecture

**Date**: 2025-11-20  
**Context**: Understanding component hierarchy for hot reload design  
**Pattern**: Recursive delegation through indexed containers

---

## 🌳 The Fractal Hierarchy

### Level 1: IndexManager (Top-Level Orchestrator)

```python
class IndexManager:
    _indexes: Dict[str, BaseIndex] = {}  # Top-level index registry
    _indexes_lock: RLock  # Protects _indexes dict
    
    def route_action(action, **kwargs):
        index = self._indexes["standards"]  # Get container
        return index.search(query)  # Delegate to container
```

**Pattern**: Dictionary of containers, protected by single RLock.

---

### Level 2: Container (StandardsIndex, CodeIndex)

```python
class StandardsIndex(BaseIndex):
    _semantic_index: SemanticIndex  # Internal implementation
    components: Dict[str, ComponentDescriptor] = {
        "vector": ComponentDescriptor(...),
        "fts": ComponentDescriptor(...),
        "metadata": ComponentDescriptor(...)
    }
    
    def build(source_paths):
        with self._lock_manager.exclusive_lock():
            self._semantic_index.build(source_paths)  # Delegate
    
    def health_check():
        return dynamic_health_check(self.components)  # Fractal!
```

**Pattern**: 
- Implements BaseIndex interface
- Has `self.components` dict (component registry)
- Delegates to sub-indexes
- Uses dynamic_health_check() for fractal aggregation

---

### Level 3: Sub-Index (SemanticIndex, GraphIndex)

```python
class SemanticIndex:
    # Actual LanceDB implementation
    def build(source_paths):
        # Build vector index
        # Build FTS index
        # Build scalar indexes
```

**Pattern**: Leaf implementation, no further delegation.

---

### Level 4: Partitions (Multi-Repo Mode)

```python
class CodeIndex(BaseIndex):
    # Multi-partition mode
    _partitions: Dict[str, Partition] = {
        "praxis-os": Partition(semantic, graph),
        "honeyhive-app": Partition(semantic, graph),
        "hive-kube": Partition(semantic, graph)
    }
    
    # Partitions ARE components (fractal!)
    components: Dict[str, ComponentDescriptor] = {
        "praxis-os": ComponentDescriptor(
            health_check=lambda: partition.health_check()
        ),
        "honeyhive-app": ComponentDescriptor(...),
        "hive-kube": ComponentDescriptor(...)
    }
```

**Pattern**: Partitions registered as components, each partition has semantic + graph.

---

## 🔄 The Fractal Pattern in Action

### Example: health_check() Cascade

```
IndexManager.health_check_all()
  ↓
for name, index in self._indexes.items():
  ↓
StandardsIndex.health_check()
  ↓
dynamic_health_check(self.components)
  ↓
for name, component in self.components.items():
  ↓
component.health_check()  # Calls _check_vector_health(), etc.
  ↓
self._semantic_index.health_check()  # Leaf
```

**Fractal Property**: Each level has a dict of sub-components, uses same pattern.

---

### Example: build() Cascade

```
IndexManager.rebuild_index("code")
  ↓
index = self._indexes["code"]
index.build(source_paths, force=True)
  ↓
CodeIndex.build(source_paths, force)
  ↓
if multi_partition_mode:
    for partition in self._partitions.values():
        partition.semantic.build(source_paths)
        partition.graph.build(source_paths)
else:
    self._semantic_index.build(source_paths)
    self._graph_index.build(source_paths)
```

**Fractal Property**: Container delegates to sub-indexes, which implement actual logic.

---

## 🎯 Key Insight: Indexed Dictionaries All The Way Down

| Level | Dict Name | Key | Value | Lock |
|-------|-----------|-----|-------|------|
| **L1: IndexManager** | `_indexes` | `"standards"` | `StandardsIndex` | `_indexes_lock` (RLock) |
| **L2: Container** | `components` | `"vector"` | `ComponentDescriptor` | No lock (immutable after init) |
| **L3: CodeIndex** | `_partitions` | `"praxis-os"` | `Partition` | `_lock_manager` (per-index) |

**Pattern**: Each level is a dictionary mapping names to implementations.

---

## 🔥 Hot Reload: Fractal Propagation

### Adding New Repo (Multi-Repo Example)

```python
# User adds to config:
config.yaml:
  rag:
    code:
      partitions:
        - name: praxis-os
        - name: honeyhive-app  # NEW!

# Hot reload triggered:
POST /reload-config

# Propagation cascade:
1. IndexManager.reload_indexes(new_config)
     ↓
2. Determine changes: to_add=["honeyhive-app"]
     ↓
3. For each new index:
     index = CodeIndex(new_config, base_path)  # Creates container
     ↓
4. CodeIndex.__init__():
     reconciler.reconcile()  # Creates partition directories
     ↓
5. self._partitions["honeyhive-app"] = Partition(semantic, graph)
     ↓
6. self.components["honeyhive-app"] = ComponentDescriptor(...)
     ↓
7. IndexManager.add_index("code", index)
     ↓
8. with self._indexes_lock:
       self._indexes["code"] = index  # Replaces old CodeIndex
```

**Fractal Property**: Adding one partition at L3 automatically creates components at L2, which are accessible via L1.

---

### Thread Safety Through Levels

**L1 (IndexManager)**: RLock on `_indexes` dict
```python
def add_index(self, name, index):
    with self._indexes_lock:  # RLock
        self._indexes[name] = index
```

**L2 (Container)**: Lock on operations, immutable components
```python
def build(self, source_paths):
    with self._lock_manager.exclusive_lock():  # File lock
        self._semantic_index.build(source_paths)

# components dict is immutable after __init__
self.components = {...}  # Set once, never modified
```

**L3 (Sub-Index)**: Internal locking (LanceDB, DuckDB handle their own)

**Insight**: Each level protects its own dictionary. Hot reload only modifies L1.

---

## 📊 Fractal Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ IndexManager                                                 │
│                                                              │
│ _indexes = {                                                │
│   "standards": StandardsIndex ─────────────┐                │
│   "code": CodeIndex ───────────────────┐   │                │
│ }                                       │   │                │
│ _indexes_lock (RLock)                   │   │                │
└─────────────────────────────────────────┼───┼────────────────┘
                                          │   │
                                          │   │
          ┌───────────────────────────────┘   │
          │                                   │
          ▼                                   ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│ CodeIndex (Container)    │    │ StandardsIndex (Container)   │
│                          │    │                              │
│ components = {           │    │ components = {               │
│   "semantic": {...}      │    │   "vector": {...}            │
│   "graph": {...}         │    │   "fts": {...}               │
│ }                        │    │   "metadata": {...}          │
│                          │    │ }                            │
│ OR (multi-partition):    │    │                              │
│ _partitions = {          │    │ Delegates to:                │
│   "praxis-os": {...}     │    │   _semantic_index           │
│   "honeyhive": {...}     │    │                              │
│ }                        │    │                              │
└──────────────────────────┘    └──────────────────────────────┘
          │                                   │
          │                                   │
          ▼                                   ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│ Partition                │    │ SemanticIndex                │
│                          │    │                              │
│ semantic: SemanticIndex  │    │ LanceDB:                     │
│ graph: GraphIndex        │    │ - Vector index               │
│                          │    │ - FTS index                  │
│ components = {           │    │ - Scalar indexes             │
│   "semantic": {...}      │    │                              │
│   "graph": {...}         │    │                              │
│ }                        │    │                              │
└──────────────────────────┘    └──────────────────────────────┘
```

---

## 🎨 Design Principles

### 1. **Indexed Containers Pattern**
Every level is a dict mapping names to implementations:
- `_indexes[name]` → BaseIndex container
- `components[name]` → ComponentDescriptor
- `_partitions[name]` → Partition

### 2. **Fractal Delegation**
Operations cascade down through dictionaries:
```python
manager.health_check_all()
  → for index in _indexes.values(): index.health_check()
    → dynamic_health_check(components)
      → for component in components.values(): component.health_check()
```

### 3. **Immutable Components, Mutable Indexes**
- **L1 `_indexes`**: Mutable (hot reload adds/removes)
- **L2 `components`**: Immutable (set once in `__init__`)
- **L3 sub-indexes**: Leaf implementations

### 4. **Lock Hierarchy**
- **L1**: RLock on `_indexes` dict (write operations rare)
- **L2**: File locks per index (exclusive during build)
- **L3**: Database-level locks (LanceDB, DuckDB internal)

---

## 🔮 Hot Reload Implications

### What Gets Modified?

**L1 (IndexManager)**:
- ✅ `_indexes` dict modified (add/remove containers)
- ✅ Requires RLock protection
- ✅ Snapshot pattern for safe iteration

**L2 (Container)**:
- ❌ `components` dict NOT modified (immutable)
- ✅ New container instance created with new components
- ✅ Old container swapped out atomically

**L3 (Sub-Index)**:
- ❌ No changes (leaf implementations)

### Key Insight: Replace, Don't Modify

Hot reload doesn't modify containers in-place. It creates new containers and swaps them:

```python
# NOT this (modifying in place):
def reload_bad(self, new_config):
    index = self._indexes["code"]
    index.add_partition("new-repo")  # Dangerous!

# THIS (create new, swap atomically):
def reload_good(self, new_config):
    new_index = CodeIndex(new_config, base_path)  # New instance
    with self._indexes_lock:
        self._indexes["code"] = new_index  # Atomic swap
```

**Why This Works**:
1. Old container still exists for in-flight requests
2. New requests get new container
3. Python GC cleans up old container when no references remain
4. No need to synchronize container internals (immutable)

---

## 📝 API Design for Hot Reload

### Recommended Methods

```python
class IndexManager:
    def add_index(self, index_name: str, index: BaseIndex) -> None:
        """Add or replace index (atomic swap)."""
        with self._indexes_lock:
            if index_name in self._indexes:
                logger.info("Replacing existing index: %s", index_name)
            self._indexes[index_name] = index
    
    def remove_index(self, index_name: str) -> Optional[BaseIndex]:
        """Remove index, returning old instance for cleanup."""
        with self._indexes_lock:
            return self._indexes.pop(index_name, None)
    
    def reload_indexes(self, new_config: IndexesConfig) -> Dict[str, Any]:
        """Reload indexes from new config (declarative)."""
        # Determine add/remove/keep
        current = set(self._indexes.keys())
        new = self._get_required_indexes(new_config)
        
        to_add = new - current
        to_remove = current - new
        to_keep = current & new
        
        # Add new indexes
        for name in to_add:
            index = self._create_index(name, new_config)
            self.add_index(name, index)
        
        # Remove old indexes
        for name in to_remove:
            old_index = self.remove_index(name)
            if old_index and hasattr(old_index, 'close'):
                old_index.close()
        
        # Recreate kept indexes (config may have changed)
        for name in to_keep:
            # For multi-repo, CodeIndex __init__ reconciles partitions
            new_index = self._create_index(name, new_config)
            self.add_index(name, new_index)  # Atomic swap
        
        return {
            "added": list(to_add),
            "removed": list(to_remove),
            "updated": list(to_keep)
        }
```

---

## ✅ Fractal Pattern Validation

**Property 1**: Each level is a dictionary
- ✅ L1: `_indexes` (IndexManager)
- ✅ L2: `components` (Container)
- ✅ L3: `_partitions` (CodeIndex multi-repo)

**Property 2**: Operations cascade recursively
- ✅ `health_check()` → `dynamic_health_check()` → `component.health_check()`
- ✅ `build()` → `partition.build()` → `semantic.build()` + `graph.build()`

**Property 3**: Each level protects its own dict
- ✅ L1: RLock on `_indexes`
- ✅ L2: File lock on operations (components immutable)
- ✅ L3: Database-level locks

**Property 4**: Hot reload creates new instances, doesn't modify
- ✅ New container created with new components
- ✅ Atomic swap at L1
- ✅ Python GC cleans up old container

---

**Status**: Fractal pattern understood  
**Implication**: Hot reload is simple at L1, complex graph is encapsulated  
**Next**: Update design doc with hot reload API


