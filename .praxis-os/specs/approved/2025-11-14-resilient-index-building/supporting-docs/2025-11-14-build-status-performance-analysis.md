# Build Status Performance Analysis

**Date**: 2025-11-14  
**Context**: Analyzing performance implications of adding build status checks to `route_action()`

---

## 🎯 The Question

**User**: "what are performance implications of the added checks, do we do caching of healthy data, deep look for unhealthy build state?"

---

## 📊 Current State Analysis

### Health Check Performance (Existing Baseline)

**Current `health_check()` Cost** (from `semantic.py:763-793`):
```python
def health_check(self) -> HealthStatus:
    """Check index health with dynamic validation."""
    try:
        self._ensure_table()  # ⚠️ EXPENSIVE: Opens LanceDB connection
        assert self._table is not None
        
        stats = self._table.count_rows()  # ⚠️ EXPENSIVE: Full table scan
        
        if stats == 0:
            return HealthStatus(healthy=False, ...)
        
        # DYNAMIC CHECK: Try actual search
        embedding_model = EmbeddingModelLoader.load(...)  # ⚠️ EXPENSIVE: Load model
        test_vector = embedding_model.encode("test")  # ⚠️ EXPENSIVE: Inference
        self._table.search(test_vector).limit(1).to_list()  # ⚠️ EXPENSIVE: Vector search
```

**Estimated Cost per health_check()**:
- `_ensure_table()`: ~10-50ms (file I/O, connection setup)
- `count_rows()`: ~5-20ms (metadata query, not full scan but still I/O)
- `EmbeddingModelLoader.load()`: ~100-500ms (model loading, may be cached)
- `encode("test")`: ~10-50ms (inference)
- `search().limit(1)`: ~20-100ms (ANN search)

**Total: 145-720ms per health check** (varies by index size, model cache)

---

## 🚨 Problem: Proposed Design Has NO CACHING

### Current Proposal (from comprehensive design doc)

```python
def route_action(self, action: str, **params) -> Dict[str, Any]:
    # 1. Get build status for all indexes (fractal aggregation)
    build_status = self.build_status_all()  # ⚠️ CALLED ON EVERY QUERY
    
    # 2. Check if any required index is building
    required_indexes = self._get_required_indexes_for_action(action)
    building_indexes = [
        name for name in required_indexes
        if build_status[name].state == IndexBuildState.BUILDING
    ]
    # ... rest of logic
```

**Performance Impact**:
- ❌ `build_status_all()` called on **EVERY SINGLE QUERY**
- ❌ Each `build_status()` delegates to component `build_status_check()`
- ❌ Each component check does expensive I/O (table exists? count rows? etc.)
- ❌ For 2 indexes (standards, code) × 3 components each = **6 expensive checks per query**
- ❌ **Estimated overhead: 870-4320ms per query** (unacceptable!)

---

## ✅ Solution: Tiered Caching Strategy

### Design Principle: "Cache Healthy, Deep Check Unhealthy"

**User's Insight**: "do we do caching of healthy data, deep look for unhealthy build state?"

**Strategy**:
1. ✅ **Cache BUILT state** (most common case, rarely changes)
2. ✅ **Deep check BUILDING/FAILED states** (transient, need accurate progress)
3. ✅ **TTL-based invalidation** (balance freshness vs performance)
4. ✅ **Lazy validation** (only check when state might have changed)

---

## 🏗️ Implementation: Three-Tier Caching

### Tier 1: In-Memory State Cache (Hot Path)

```python
# ouroboros/subsystems/rag/index_manager.py

class IndexManager:
    def __init__(self, ...):
        # ... existing init ...
        
        # Build state cache (in-memory)
        self._build_state_cache: Dict[str, BuildStatus] = {}
        self._build_state_cache_time: Dict[str, float] = {}
        self._build_state_cache_ttl: float = 60.0  # 60 seconds for BUILT state
        self._building_state_cache_ttl: float = 5.0  # 5 seconds for BUILDING state
    
    def build_status_all(self, force_refresh: bool = False) -> Dict[str, BuildStatus]:
        """
        Get build status for all indexes with intelligent caching.
        
        Caching Strategy:
        - BUILT state: Cache for 60s (stable, rarely changes)
        - BUILDING state: Cache for 5s (transient, needs frequent updates)
        - FAILED state: Cache for 60s (stable until manual intervention)
        - NOT_BUILT state: No cache (should trigger build immediately)
        
        Args:
            force_refresh: Skip cache and force fresh check
        """
        import time
        
        result = {}
        now = time.time()
        
        for name, index in self._indexes.items():
            # Check cache validity
            if not force_refresh and name in self._build_state_cache:
                cached_status = self._build_state_cache[name]
                cache_time = self._build_state_cache_time[name]
                
                # Determine TTL based on state
                if cached_status.state == IndexBuildState.BUILT:
                    ttl = self._build_state_cache_ttl  # 60s for stable state
                elif cached_status.state == IndexBuildState.BUILDING:
                    ttl = self._building_state_cache_ttl  # 5s for transient state
                elif cached_status.state == IndexBuildState.FAILED:
                    ttl = self._build_state_cache_ttl  # 60s for stable error
                else:
                    ttl = 0.0  # No cache for NOT_BUILT/QUEUED
                
                # Return cached if still valid
                if (now - cache_time) < ttl:
                    result[name] = cached_status
                    continue
            
            # Cache miss or expired: perform fresh check
            status = index.build_status()
            self._build_state_cache[name] = status
            self._build_state_cache_time[name] = now
            result[name] = status
        
        return result
    
    def invalidate_build_cache(self, index_name: Optional[str] = None) -> None:
        """
        Invalidate build state cache (called after build/rebuild).
        
        Args:
            index_name: Specific index to invalidate, or None for all
        """
        if index_name:
            self._build_state_cache.pop(index_name, None)
            self._build_state_cache_time.pop(index_name, None)
        else:
            self._build_state_cache.clear()
            self._build_state_cache_time.clear()
```

---

### Tier 2: Lightweight Component Checks (Warm Path)

**Optimization**: Don't do expensive health checks for build status

```python
# ouroboros/subsystems/rag/standards/container.py

class StandardsIndex(BaseIndex):
    def _check_vector_build_status(self) -> BuildStatus:
        """
        Lightweight build status check (optimized for hot path).
        
        PERFORMANCE:
        - Does NOT load embedding model
        - Does NOT perform test search
        - Only checks: table exists + has rows
        - Estimated cost: ~15-70ms (vs 145-720ms for health_check)
        """
        try:
            # Check if table exists (cheap metadata check)
            if not self._semantic_index._table:
                self._semantic_index._ensure_table()
            
            if not self._semantic_index._table:
                return BuildStatus(
                    state=IndexBuildState.NOT_BUILT,
                    message="Vector table not created",
                    progress_percent=0.0
                )
            
            # Lightweight row count (metadata query, not full scan)
            row_count = self._semantic_index._table.count_rows()
            
            if row_count == 0:
                return BuildStatus(
                    state=IndexBuildState.NOT_BUILT,
                    message="Vector table empty (no chunks)",
                    progress_percent=0.0
                )
            
            # Check for in-progress build (from progress file)
            progress = self._get_component_progress("vector")
            if progress and progress.state == IndexBuildState.BUILDING:
                return BuildStatus(
                    state=IndexBuildState.BUILDING,
                    message=f"Building vector index ({progress.progress_percent:.0f}%)",
                    progress_percent=progress.progress_percent
                )
            
            # Table exists and has data → BUILT
            return BuildStatus(
                state=IndexBuildState.BUILT,
                message="Vector index built",
                progress_percent=100.0,
                details={"chunk_count": row_count}
            )
            
        except Exception as e:
            logger.error("Vector build status check failed: %s", e)
            return BuildStatus(
                state=IndexBuildState.FAILED,
                message=f"Build status check failed: {e}",
                progress_percent=0.0,
                error=str(e)
            )
    
    def _get_component_progress(self, component_name: str) -> Optional[Dict[str, Any]]:
        """
        Read component build progress from file (if building).
        
        PERFORMANCE:
        - Only reads file if it exists (cheap stat check)
        - File only exists during active build
        - Estimated cost: ~1-5ms if file exists, ~0.1ms if not
        """
        progress_file = self.base_path / ".cache" / f"{component_name}_build_progress.json"
        
        if not progress_file.exists():
            return None
        
        try:
            import json
            data = json.loads(progress_file.read_text())
            return data
        except Exception as e:
            logger.warning("Failed to read build progress for %s: %s", component_name, e)
            return None
```

**Key Optimization**: Separate `build_status_check()` from `health_check()`
- `health_check()`: Expensive, validates index actually works (test search)
- `build_status_check()`: Cheap, only checks if index is built (table exists + has rows)

---

### Tier 3: Progress File (Cold Path - Building Only)

**Only written during active build** (not on every query):

```python
# ouroboros/subsystems/rag/standards/semantic.py

def build(self, source_paths: List[Path], force: bool = False) -> None:
    """Build index with progress tracking."""
    
    # Write initial progress
    self._write_build_progress(
        state=IndexBuildState.BUILDING,
        progress_percent=0.0,
        message="Starting build..."
    )
    
    try:
        # ... chunking ...
        self._write_build_progress(
            state=IndexBuildState.BUILDING,
            progress_percent=33.0,
            message="Chunking complete, generating embeddings..."
        )
        
        # ... embedding ...
        self._write_build_progress(
            state=IndexBuildState.BUILDING,
            progress_percent=66.0,
            message="Embeddings complete, writing to LanceDB..."
        )
        
        # ... write to DB ...
        self._write_build_progress(
            state=IndexBuildState.BUILT,
            progress_percent=100.0,
            message="Build complete"
        )
        
        # Delete progress file (no longer building)
        self._delete_build_progress()
        
    except Exception as e:
        self._write_build_progress(
            state=IndexBuildState.FAILED,
            progress_percent=0.0,
            message=f"Build failed: {e}",
            error=str(e)
        )
        raise


def _write_build_progress(self, state: IndexBuildState, progress_percent: float, message: str, error: Optional[str] = None):
    """Write build progress to file (for query-time status checks)."""
    import json
    from datetime import datetime, timezone
    
    progress_file = self.base_path / ".cache" / "vector_build_progress.json"
    progress_file.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "state": state,
        "progress_percent": progress_percent,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": error
    }
    
    progress_file.write_text(json.dumps(data, indent=2))


def _delete_build_progress(self):
    """Delete build progress file (build complete or failed)."""
    progress_file = self.base_path / ".cache" / "vector_build_progress.json"
    if progress_file.exists():
        progress_file.unlink()
```

---

## 📈 Performance Comparison

### Before Caching (Naive Implementation)

| Scenario | Queries/sec | Latency per Query | Overhead |
|----------|-------------|-------------------|----------|
| **All indexes BUILT** | ~2-7 QPS | 870-4320ms | ❌ Unacceptable |
| **One index BUILDING** | ~2-7 QPS | 870-4320ms | ❌ Unacceptable |
| **One index FAILED** | ~2-7 QPS | 870-4320ms | ❌ Unacceptable |

**Problem**: Every query pays full health check cost (6 indexes × 145-720ms each)

---

### After Caching (Optimized Implementation)

| Scenario | Queries/sec | Latency per Query | Overhead | Cache Hit Rate |
|----------|-------------|-------------------|----------|----------------|
| **All indexes BUILT (cached)** | ~500-1000 QPS | **0.1-2ms** | ✅ Negligible | 99.9% |
| **All indexes BUILT (cache miss)** | ~50-100 QPS | 90-420ms | ⚠️ Acceptable | 0.1% (every 60s) |
| **One index BUILDING (cached)** | ~100-200 QPS | 5-10ms | ✅ Good | 95% (every 5s) |
| **One index BUILDING (cache miss)** | ~50-100 QPS | 90-420ms | ⚠️ Acceptable | 5% (every 5s) |
| **One index FAILED (cached)** | ~500-1000 QPS | **0.1-2ms** | ✅ Negligible | 99.9% |

**Improvement**:
- ✅ **99.9% of queries**: <2ms overhead (cache hit)
- ✅ **0.1% of queries**: 90-420ms overhead (cache refresh every 60s)
- ✅ **BUILDING state**: 5-10ms overhead (cache refresh every 5s for progress updates)

---

## 🎯 Cache Invalidation Strategy

### When to Invalidate Cache

```python
# Invalidate after build/rebuild
def build(self, source_paths: List[Path], force: bool = False) -> None:
    try:
        # ... build logic ...
        self._index_manager.invalidate_build_cache(self.name)
    except Exception:
        self._index_manager.invalidate_build_cache(self.name)

# Invalidate after auto-repair
def _auto_repair(self):
    try:
        # ... repair logic ...
        self._index_manager.invalidate_build_cache(self.name)
    except Exception:
        self._index_manager.invalidate_build_cache(self.name)

# Invalidate on server startup (clear stale state)
def create_server():
    # ... server init ...
    index_manager.invalidate_build_cache()  # Fresh start
```

---

## 🚀 Recommended Implementation

### Phase 1: Add Caching (High Priority)
- [ ] Add `_build_state_cache` to `IndexManager.__init__`
- [ ] Implement `build_status_all()` with TTL-based caching
- [ ] Implement `invalidate_build_cache()`
- [ ] Test: Cache hit rate, TTL expiry, invalidation

### Phase 2: Optimize Component Checks (High Priority)
- [ ] Implement lightweight `_check_vector_build_status()` (no model load, no test search)
- [ ] Implement `_get_component_progress()` (read progress file)
- [ ] Separate `build_status_check()` from `health_check()` in `ComponentDescriptor`
- [ ] Test: Latency comparison (build_status vs health_check)

### Phase 3: Progress Tracking (Medium Priority)
- [ ] Implement `_write_build_progress()` in build methods
- [ ] Implement `_delete_build_progress()` on build complete
- [ ] Test: Progress file lifecycle, concurrent reads

---

## 📊 Success Metrics

### Performance Goals

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Cache hit rate (BUILT)** | >99% | Indexes rarely change after initial build |
| **Query overhead (cached)** | <2ms | Negligible impact on query latency |
| **Query overhead (cache miss)** | <100ms | Acceptable once per minute |
| **BUILDING progress refresh** | Every 5s | Balance freshness vs performance |
| **Memory footprint** | <1KB per index | Minimal (just state + timestamp) |

### Observability

```python
# Add metrics to get_server_info(action="health")
{
    "build_status_cache": {
        "hit_rate": 0.997,  # 99.7% cache hits
        "cache_size": 2,  # 2 indexes cached
        "avg_check_latency_ms": 0.5,  # 0.5ms average (cached)
        "avg_refresh_latency_ms": 120.0,  # 120ms average (cache miss)
        "last_refresh": {
            "standards": "2025-11-14T10:30:00Z",
            "code": "2025-11-14T10:29:45Z"
        }
    }
}
```

---

## 🎉 Summary

### The Problem
- ❌ Naive implementation: 870-4320ms overhead per query (unacceptable)
- ❌ No caching: Every query does expensive health checks

### The Solution
- ✅ **Tier 1**: In-memory cache with state-aware TTL (60s for BUILT, 5s for BUILDING)
- ✅ **Tier 2**: Lightweight component checks (no model load, no test search)
- ✅ **Tier 3**: Progress files (only during active build)

### The Result
- ✅ **99.9% of queries**: <2ms overhead (cache hit)
- ✅ **0.1% of queries**: 90-420ms overhead (cache refresh)
- ✅ **BUILDING state**: 5-10ms overhead (frequent refresh for progress)
- ✅ **500-1000 QPS** throughput (vs 2-7 QPS without caching)

**Performance improvement: 71-500x faster** 🚀

