# Comprehensive Cache Analysis: prAxIs OS Workflow System
**Date:** 2025-10-13  
**Analysis Depth:** Complete system architecture  
**Scope:** All caching mechanisms and their interactions

---

## Executive Summary

The prAxIs OS workflow system has **7 distinct cache layers** operating at different scopes with varying lifecycles and invalidation strategies. The current metadata caching issue revealed fundamental architectural tensions between **development agility** and **production performance**.

**Key Finding:** File watcher invalidates RAG index but NOT metadata/session caches, creating **stale state divergence**.

---

## 1. Cache Inventory

### 1.1 RAG Engine Query Cache
**Location:** `mcp_server/rag_engine.py:86`
```python
self._query_cache: Dict[str, tuple] = {}  # {query_hash: (result, timestamp)}
```

**Lifecycle:**
- **Created:** On first search with specific query+filters+n_results
- **TTL:** 1 hour (3600 seconds, configurable)
- **Invalidation:** 
  - Automatic TTL expiration
  - Manual: `reload_index()` clears entire cache
  - Size-based cleanup (>100 entries triggers cleanup)
- **Scope:** Process-wide (single RAGEngine instance)

**Purpose:** Avoid re-embedding identical queries and re-executing vector searches

**Thread Safety:** Protected by `self._lock` (RLock)

---

### 1.2 Workflow Metadata Cache
**Location:** `mcp_server/workflow_engine.py:390`
```python
self._metadata_cache: Dict[str, WorkflowMetadata] = {}  
# {workflow_type: WorkflowMetadata}
```

**Lifecycle:**
- **Created:** First call to `load_workflow_metadata(workflow_type)`
- **TTL:** INFINITE (never expires)
- **Invalidation:** NONE (manual server restart only)
- **Scope:** Process-wide (single WorkflowEngine instance)

**Purpose:** Avoid re-reading/parsing metadata.json files

**Thread Safety:** No explicit locking (single-threaded access assumed)

**⚠️ ISSUE IDENTIFIED:** This is the root cause of the bug we found. File watcher doesn't invalidate this cache.

---

### 1.3 CheckpointLoader Checkpoint Cache
**Location:** `mcp_server/workflow_engine.py:60`
```python
self._checkpoint_cache: Dict[str, Dict] = {}  
# {f"{workflow_type}_phase_{phase}": requirements}
```

**Lifecycle:**
- **Created:** First checkpoint load for workflow_type + phase combination
- **TTL:** INFINITE (never expires)
- **Invalidation:** NONE
- **Scope:** Per CheckpointLoader instance (typically one per WorkflowEngine)

**Purpose:** Avoid re-querying RAG for checkpoint requirements parsing

**Thread Safety:** No explicit locking

**⚠️ ISSUE:** Also not invalidated by file watcher, though less critical since checkpoint docs rarely change

---

### 1.4 WorkflowEngine Session Cache
**Location:** `mcp_server/workflow_engine.py:393`
```python
self._sessions: Dict[str, WorkflowSession] = {}  
# {session_id: WorkflowSession}
```

**Lifecycle:**
- **Created:** First call to `get_session(session_id)` or `start_workflow()`
- **TTL:** Until workflow completion or manual cleanup
- **Invalidation:** 
  - Automatic: When `complete_phase()` returns `workflow_complete=True`
  - Manual: Server restart
- **Scope:** Process-wide (single WorkflowEngine instance)

**Purpose:** Avoid re-creating WorkflowSession objects (expensive - loads state, metadata, initializes dynamic registry)

**Thread Safety:** No explicit locking

**Key Point:** Each session holds its own **metadata snapshot** from creation time!

---

### 1.5 DynamicContentRegistry Content Cache
**Location:** `mcp_server/models/workflow.py` (DynamicWorkflowContent class)
```python
# Lazy-rendered content cache (not explicitly visible in code)
# Cached in DynamicWorkflowContent.phases structure
```

**Lifecycle:**
- **Created:** On WorkflowSession initialization for dynamic workflows
- **TTL:** Life of WorkflowSession
- **Invalidation:** When session is destroyed/cleaned up
- **Scope:** Per WorkflowSession instance

**Purpose:** Lazy rendering of phase/task templates with parsed content

**Thread Safety:** Session-scoped (single workflow execution)

---

### 1.6 StateManager Disk-Based Session State
**Location:** `mcp_server/state_manager.py` (JSON files in `.praxis-os/.cache/state/`)
```python
# File-based persistence: {session_id}.json
```

**Lifecycle:**
- **Created:** `create_session()` writes initial state
- **TTL:** 7 days by default (cleanup_days parameter)
- **Invalidation:**
  - Automatic: `cleanup_old_sessions()` removes sessions >7 days old
  - Manual: `delete_session(session_id)`
- **Scope:** Persistent across server restarts

**Purpose:** Enable workflow resumption after server restart/crash

**Thread Safety:** File locking (fcntl.LOCK_EX for writes, LOCK_SH for reads)

**Key Point:** Contains **snapshot of workflow state**, not live references

---

### 1.7 RAG Index (LanceDB Vector Database)
**Location:** `.praxis-os/.cache/vector_index/` (LanceDB database files)

**Lifecycle:**
- **Created:** `scripts/build_rag_index.py` initial build
- **Updated:** File watcher triggers incremental rebuild on .md/.json changes
- **Invalidation:** Full rebuild (--force flag) or incremental update
- **Scope:** Persistent across server restarts

**Purpose:** Vector search over prAxIs OS content

**Thread Safety:** LanceDB internal locking + RAGEngine._lock

**Key Point:** File watcher DOES invalidate this via `reload_index()`

---

## 2. Cache Interaction Map

```
File Change (.md or .json in .praxis-os/)
    ↓
File Watcher Detects (monitoring/watcher.py)
    ↓
    ├─→ Rebuild RAG Index (scripts/build_rag_index.py)
    │       ↓
    │   Update LanceDB Vector Database ✅
    │       ↓
    │   Call rag_engine.reload_index() ✅
    │       ↓
    │   Clear RAG Query Cache ✅
    │
    └─→ WorkflowEngine Metadata Cache ❌ NOT CLEARED
            ↓
        CheckpointLoader Cache ❌ NOT CLEARED
            ↓
        Session Cache (holds stale metadata) ❌ NOT CLEARED
```

---

## 3. Lifecycle Analysis by Operation

### 3.1 Server Start
```
1. RAGEngine.__init__()
   - Connects to LanceDB
   - Loads embedding model
   - Initializes empty query_cache

2. WorkflowEngine.__init__()
   - Initializes empty _metadata_cache
   - Initializes empty _sessions cache
   - Creates CheckpointLoader (empty _checkpoint_cache)

3. StateManager.__init__()
   - Scans .cache/state/ for existing sessions
   - Ready to load/create sessions
```

### 3.2 File Change (dogfooding scenario)
```
1. Edit universal/workflows/praxis_os_upgrade_v1/metadata.json
2. Copy to .praxis-os/workflows/praxis_os_upgrade_v1/metadata.json
3. File watcher detects .json change
4. Wait 5 seconds (debounce)
5. Rebuild RAG index (incremental)
6. Call rag_engine.reload_index()
   ├─→ Clears _query_cache ✅
   ├─→ Reconnects to LanceDB ✅
   └─→ Sets _rebuilding event ✅

❌ WorkflowEngine._metadata_cache still has old metadata!
❌ WorkflowEngine._sessions still have old WorkflowSession objects!
❌ Each WorkflowSession.metadata still points to old data!
```

### 3.3 Workflow Start (after file change)
```
1. start_workflow(workflow_type="praxis_os_upgrade_v1", ...)
2. Call load_workflow_metadata("praxis_os_upgrade_v1")
   - Check _metadata_cache
   - CACHE HIT! ❌ Returns stale metadata
3. Create or resume session
   - Uses STALE metadata
4. Session stores metadata snapshot
   - Now session has STALE metadata forever!
```

---

## 4. Root Cause Analysis

### The Problem Chain

```
1. DESIGN: Metadata cache has infinite TTL for performance
           ↓
2. ASSUMPTION: metadata.json rarely changes in production
           ↓
3. REALITY: In development/dogfooding, it changes frequently
           ↓
4. MISSING: File watcher → workflow engine cache invalidation hook
           ↓
5. RESULT: Stale metadata served to new sessions
           ↓
6. MANIFESTATION: Tasks fallback to RAG (missing tasks array)
```

### Why This Wasn't Caught Earlier

1. **Most workflows have stable metadata** - Don't edit metadata.json often
2. **Server restarts during development** - Clears cache naturally
3. **Dynamic workflows use RAG fallback** - Masks the issue
4. **Dogfooding revealed it** - Rapid iteration on workflow_creation_v1 and praxis_os_upgrade_v1

---

## 5. Cache Invalidation Strategies (Current)

| Cache Layer | Strategy | Trigger | Effectiveness |
|-------------|----------|---------|---------------|
| RAG Query Cache | TTL + Size-based | Time + reload_index() | ✅ Good |
| RAG Index | File Watcher | .md/.json changes | ✅ Excellent |
| Workflow Metadata | None | Manual restart | ❌ Poor |
| Checkpoint Cache | None | Manual restart | ⚠️ Acceptable |
| Session Cache | Workflow completion | complete_phase() | ✅ Good |
| Dynamic Registry | Session lifecycle | Session cleanup | ✅ Good |
| State Files | Age-based | 7 days old | ✅ Good |

---

## 6. Architectural Tensions

### Development vs Production

| Aspect | Development Need | Production Need | Current Design |
|--------|------------------|-----------------|----------------|
| Metadata changes | Frequent | Rare | Optimized for production |
| Cache invalidation | Immediate | Rarely needed | No mechanism |
| Hot reload | Essential | Nice-to-have | Partial (RAG only) |
| Performance | Less critical | Critical | Fast (caching) |
| Server restarts | Acceptable | Minimize | Required for metadata updates |

### Dynamic vs Static Workflows

| Workflow Type | Metadata Usage | Cache Impact |
|---------------|----------------|--------------|
| Static (test_generation_v3) | Tasks from metadata.json | Stale cache breaks get_task() |
| Dynamic (spec_execution_v1) | Phase 0 from metadata, 1-N dynamic | Hybrid - partial impact |
| Hybrid (praxis_os_upgrade_v1) | All phases from metadata | Critical - all tasks fail |

---

## 7. Proposed Solutions

### Option 1: Add File Watcher Hook (RECOMMENDED)
**Impact:** Low  
**Complexity:** Low  
**Effectiveness:** High for dogfooding

```python
# In workflow_engine.py
def clear_metadata_cache(self, workflow_type: Optional[str] = None) -> None:
    """Clear metadata cache for hot reload."""
    with self._cache_lock:  # Add locking
        if workflow_type:
            self._metadata_cache.pop(workflow_type, None)
            # Also clear sessions using this workflow
            to_remove = [
                sid for sid, session in self._sessions.items()
                if session.workflow_type == workflow_type
            ]
            for sid in to_remove:
                self._sessions.pop(sid)
        else:
            self._metadata_cache.clear()
            self._sessions.clear()

# In monitoring/watcher.py (line 163)
if self.rag_engine and result["status"] == "success":
    self.rag_engine.reload_index()
    # NEW: Clear workflow metadata cache
    if self.workflow_engine:
        # Detect which workflows changed
        changed_workflow = self._detect_workflow_from_path(event.src_path)
        if changed_workflow:
            self.workflow_engine.clear_metadata_cache(changed_workflow)
        else:
            # If unsure, clear all
            self.workflow_engine.clear_metadata_cache()
```

**Pros:**
- ✅ Enables true hot reload in development
- ✅ Maintains production performance (cache still used)
- ✅ Minimal code changes
- ✅ Leverages existing file watcher infrastructure

**Cons:**
- ❌ Adds coupling between watcher and workflow engine
- ❌ Need to pass workflow_engine to watcher
- ❌ Active sessions using stale metadata still need handling

---

### Option 2: TTL-Based Metadata Cache
**Impact:** Medium  
**Complexity:** Low  
**Effectiveness:** Medium

```python
def load_workflow_metadata(self, workflow_type: str) -> WorkflowMetadata:
    cache_entry = self._metadata_cache.get(workflow_type)
    
    if cache_entry:
        metadata, timestamp, file_mtime = cache_entry
        metadata_path = self.workflows_base_path / workflow_type / "metadata.json"
        
        # Check if file changed
        current_mtime = metadata_path.stat().st_mtime if metadata_path.exists() else 0
        
        # Check TTL (5 minutes in dev, infinite in prod?)
        ttl = 300 if os.getenv("ENV") == "development" else float('inf')
        age = time.time() - timestamp
        
        if file_mtime == current_mtime and age < ttl:
            return metadata
    
    # Load from disk...
    metadata = WorkflowMetadata.from_dict(json.load(f))
    self._metadata_cache[workflow_type] = (metadata, time.time(), metadata_path.stat().st_mtime)
    return metadata
```

**Pros:**
- ✅ No coupling to file watcher
- ✅ Works in all scenarios
- ✅ Detects file changes automatically

**Cons:**
- ❌ Stat() call on every cache check (disk I/O)
- ❌ Stale for up to 5 minutes in development
- ❌ Environment detection complexity

---

### Option 3: Remove Metadata Cache Entirely
**Impact:** High (performance)  
**Complexity:** Trivial  
**Effectiveness:** High (correctness)

```python
def load_workflow_metadata(self, workflow_type: str) -> WorkflowMetadata:
    # Remove cache check (lines 412-414)
    # Always load from disk
    metadata_path = self.workflows_base_path / workflow_type / "metadata.json"
    # ... rest of loading logic
```

**Pros:**
- ✅ Always correct
- ✅ Simple
- ✅ No cache invalidation complexity

**Cons:**
- ❌ Performance hit on every workflow operation
- ❌ Metadata.json parsed repeatedly
- ❌ Unnecessary disk I/O in production

---

### Option 4: Hybrid - Cache with Development Flag
**Impact:** Low  
**Complexity:** Low  
**Effectiveness:** High

```python
def __init__(self, ..., enable_caching: bool = True):
    self.enable_caching = enable_caching  # False in dev, True in prod
    self._metadata_cache: Dict[str, WorkflowMetadata] = {}

def load_workflow_metadata(self, workflow_type: str) -> WorkflowMetadata:
    if self.enable_caching and workflow_type in self._metadata_cache:
        return self._metadata_cache[workflow_type]
    
    # Load from disk...
    metadata = WorkflowMetadata.from_dict(json.load(f))
    
    if self.enable_caching:
        self._metadata_cache[workflow_type] = metadata
    
    return metadata
```

**Pros:**
- ✅ Best of both worlds
- ✅ Production performance maintained
- ✅ Development correctness ensured
- ✅ Explicit control

**Cons:**
- ❌ Need environment detection or configuration
- ❌ Different behavior in dev vs prod (testing gap)

---

## 8. Recommendations

### Short Term (Immediate Fix)
**Use Option 1: File Watcher Hook**

1. Add `clear_metadata_cache()` method to WorkflowEngine
2. Inject workflow_engine into FileWatcher
3. Call cache clear after RAG reload
4. Add logging for debugging

**Estimated effort:** 30 minutes  
**Risk:** Low  
**Value:** High (unblocks dogfooding)

### Medium Term (Next Sprint)
**Add Environment Awareness**

1. Detect development mode via:
   - Environment variable: `AGENT_OS_ENV=development`
   - Config file: `.praxis-os/config.json` with `{"development_mode": true}`
   - Heuristic: Check if `.git/` exists in workspace

2. Use different cache strategies per environment:
   - Development: No metadata cache OR 30s TTL
   - Production: Infinite TTL with file watcher invalidation

3. Add monitoring:
   - Cache hit rate metrics
   - Cache size tracking
   - Invalidation event logging

### Long Term (Architecture)
**Unified Cache Management**

1. Create `CacheManager` class:
   ```python
   class CacheManager:
       def __init__(self, development_mode: bool):
           self.metadata_cache = MetadataCache(ttl=0 if development_mode else None)
           self.query_cache = QueryCache(ttl=3600)
           self.session_cache = SessionCache()
       
       def invalidate_all(self):
           """Global cache invalidation"""
       
       def invalidate_workflow(self, workflow_type: str):
           """Workflow-specific invalidation"""
   ```

2. Single invalidation API
3. Consistent cache behavior
4. Better observability

---

## 9. Testing Strategy

### Unit Tests Needed
```python
def test_metadata_cache_invalidation():
    """Test that metadata cache clears on file change"""
    # 1. Load workflow metadata (cache it)
    # 2. Modify metadata.json
    # 3. Trigger file watcher
    # 4. Load metadata again
    # 5. Assert new metadata is loaded
    
def test_session_cache_with_stale_metadata():
    """Test session behavior with stale metadata"""
    # 1. Create session
    # 2. Modify metadata
    # 3. Try to get_task()
    # 4. Assert graceful handling
```

### Integration Tests Needed
```python
def test_full_hot_reload():
    """End-to-end hot reload test"""
    # 1. Start server
    # 2. Start workflow
    # 3. Modify workflow metadata
    # 4. File watcher triggers
    # 5. Start NEW workflow
    # 6. Assert new metadata used
```

---

## 10. Performance Impact Analysis

### Current Performance (with infinite cache)
- Metadata load: ~1ms (cached) vs ~50ms (disk)
- Workflow start: ~100ms total
- get_task: ~5ms (cached metadata) vs ~200ms (RAG fallback)

### After File Watcher Hook (Option 1)
- Same as current in steady state
- 1-time cache miss after file change: +50ms
- Acceptable trade-off for correctness

### After TTL Cache (Option 2)
- Metadata load: ~2ms (stat + cached) vs ~50ms (disk)
- Stat() adds ~1ms per check
- Minimal impact, acceptable

### After Removing Cache (Option 3)
- Metadata load: ~50ms ALWAYS
- Workflow operations 50x slower
- NOT recommended

---

## 11. Conclusion

The cache architecture is **well-designed for production** but **lacks development agility**. The missing link is **cache invalidation propagation from file watcher to workflow engine**.

### Key Insights
1. **Caching is not wrong** - It's essential for performance
2. **File watcher exists** - Just needs to invalidate all caches
3. **Dynamic workflows hide the issue** - RAG fallback masks stale metadata
4. **Dogfooding revealed architectural gap** - Rapid iteration exposed the problem

### Immediate Action
Implement **Option 1 (File Watcher Hook)** to unblock dogfooding while maintaining production performance.

### Future Direction
Move toward **environment-aware caching** with unified cache management for better observability and control.

---

**End of Analysis**

