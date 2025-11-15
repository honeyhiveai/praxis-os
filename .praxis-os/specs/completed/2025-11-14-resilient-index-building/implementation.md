# Implementation Guidance: Resilient Index Building

**Project**: prAxIs OS - RAG Subsystem Enhancement  
**Feature**: Resilient Index Building with Fractal Build Status  
**Date**: 2025-11-14  
**Status**: Implementation Guidance  
**Version**: 1.0

---

## 1. Code Patterns

### 1.1 Fractal Aggregation Pattern

**Pattern**: Use `dynamic_build_status()` helper to aggregate component statuses

**Good Example**:
```python
# ouroboros/subsystems/rag/standards/container.py
from ouroboros.shared.component_helpers import dynamic_build_status

class StandardsIndex(BaseIndex):
    def build_status(self) -> BuildStatus:
        """Aggregate build status from all components (fractal pattern)."""
        return dynamic_build_status(self.components)
```

**Anti-Pattern**: Manual aggregation logic
```python
# ❌ DON'T DO THIS
def build_status(self) -> BuildStatus:
    # Manual aggregation is error-prone and inconsistent
    worst_state = IndexBuildState.BUILT
    total_progress = 0.0
    for component in self.components.values():
        status = component.build_status_check()
        if status.state.priority > worst_state.priority:
            worst_state = status.state
        total_progress += status.progress_percent
    # ... more manual logic ...
```

---

### 1.2 Thread-Safe Cache Access Pattern

**Pattern**: Always use lock for cache operations

**Good Example**:
```python
# ouroboros/subsystems/rag/index_manager.py
def _check_build_readiness(self, index_name: str) -> Optional[BuildStatus]:
    with self._build_state_cache_lock:
        # Check cache
        if index_name in self._build_state_cache:
            cached_time = self._build_state_cache_time[index_name]
            cached_status = self._build_state_cache[index_name]
            
            # Check TTL
            age = time.time() - cached_time
            ttl = self._calculate_ttl(cached_status)
            
            if age < ttl:
                return cached_status
        
        # Cache miss - call index.build_status()
        status = self._indexes[index_name].build_status()
        
        # Update cache
        self._build_state_cache[index_name] = status
        self._build_state_cache_time[index_name] = time.time()
        
        return status
```

**Anti-Pattern**: Accessing cache without lock
```python
# ❌ DON'T DO THIS
def _check_build_readiness(self, index_name: str) -> Optional[BuildStatus]:
    # Race condition! Another thread could modify cache during read
    if index_name in self._build_state_cache:
        return self._build_state_cache[index_name]
```

---

### 1.3 Corruption Handler Callback Pattern

**Pattern**: Use callback injection to avoid circular dependencies

**Good Example**:
```python
# In IndexManager.__init__():
for index_name, index in self._indexes.items():
    # Inject handler as callback (no back-reference to IndexManager)
    index.set_corruption_handler(
        lambda error, op, name=index_name: self._handle_corruption(name, error, op)
    )
```

**Anti-Pattern**: Direct reference to IndexManager
```python
# ❌ DON'T DO THIS
class StandardsIndex(BaseIndex):
    def __init__(self, config, index_manager):
        self.index_manager = index_manager  # Circular dependency!
    
    def search(self, query):
        try:
            # ... search logic ...
        except Exception as e:
            if is_corruption_error(e):
                self.index_manager._handle_corruption(...)  # Tight coupling!
```

---

### 1.4 Atomic Cache Invalidation Pattern

**Pattern**: Invalidate and update cache atomically

**Good Example**:
```python
def _handle_corruption(self, index_name: str, error: Exception, operation: str):
    with self._build_state_cache_lock:
        # Atomic operation: invalidate + update
        self._build_state_cache.pop(index_name, None)
        self._build_state_cache_time.pop(index_name, None)
        self._build_state_cache[index_name] = BuildStatus(
            state=IndexBuildState.BUILDING,
            progress_percent=0.0,
            message="Rebuilding after corruption detection"
        )
        self._build_state_cache_time[index_name] = time.time()
    
    # Start rebuild outside lock (non-blocking)
    self._rebuild_index_background(index_name)
```

**Anti-Pattern**: Non-atomic operations
```python
# ❌ DON'T DO THIS
def _handle_corruption(self, index_name: str, error: Exception, operation: str):
    # Race condition! Another thread could access cache between these operations
    self._build_state_cache.pop(index_name, None)
    # ... other code ...
    self._build_state_cache[index_name] = BuildStatus(...)
```

---

### 1.5 Progress Callback Pattern

**Pattern**: Accept optional progress callback and write progress files

**Good Example**:
```python
# ouroboros/subsystems/rag/standards/vector.py
def build(
    self, 
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> None:
    """Build vector index with progress reporting."""
    try:
        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            # ... embed and index chunk ...
            
            # Report progress every 10 chunks
            if progress_callback and i % 10 == 0:
                progress = (i + 1) / total_chunks * 100
                message = f"Embedding chunk {i+1}/{total_chunks}"
                progress_callback(progress, message)
                
                # Also write to progress file
                self._write_progress_file(progress, message)
        
        # Cleanup progress file on success
        self._delete_progress_file()
    except Exception as e:
        # Cleanup progress file on failure
        self._delete_progress_file()
        raise
```

**Anti-Pattern**: Blocking progress writes
```python
# ❌ DON'T DO THIS
def build(self, progress_callback=None):
    for i, chunk in enumerate(chunks):
        # ... embed chunk ...
        
        # Blocking write on every chunk! (too frequent)
        if progress_callback:
            progress_callback(progress, message)
            time.sleep(0.1)  # Artificial delay - bad!
```

---

### 1.6 Dynamic TTL Pattern

**Pattern**: Adjust cache TTL based on build progress

**Good Example**:
```python
def _calculate_building_ttl(self, progress_percent: float) -> float:
    """
    Dynamic TTL for BUILDING state based on progress.
    
    Early stage (0-10%): 2s TTL (fast changes)
    Mid stage (10-50%): 5s TTL (steady progress)
    Late stage (50-100%): 10s TTL (slow, near completion)
    """
    if progress_percent < 10:
        return 2.0
    elif progress_percent < 50:
        return 5.0
    else:
        return 10.0
```

**Anti-Pattern**: Static TTL for all states
```python
# ❌ DON'T DO THIS
def _calculate_ttl(self, status: BuildStatus) -> float:
    return 60.0  # Same TTL for all states - not optimal!
```

---

### 1.7 Graceful Degradation Pattern

**Pattern**: Return "building" status instead of failing

**Good Example**:
```python
def route_action(self, action: str, query: str, ...) -> Dict[str, Any]:
    # Check build readiness
    required_indexes = self._get_required_indexes_for_action(action)
    for index_name in required_indexes:
        status = self._check_build_readiness(index_name)
        
        if status and status.state == IndexBuildState.BUILDING:
            # Graceful degradation: return "building" response
            return self._format_building_response(status, action)
        
        if status and status.state == IndexBuildState.FAILED:
            # Graceful degradation: return "failed" response with remediation
            return self._format_failed_response(status, action)
    
    # All indexes BUILT - execute query normally
    try:
        results = self._execute_query(action, query, ...)
        return {"status": "success", "results": results}
    except Exception as e:
        if is_corruption_error(e):
            # Auto-repair triggered by corruption handler
            # Return graceful response
            return {
                "status": "building",
                "message": "Auto-repair in progress",
                "retry_in": 30
            }
        raise
```

**Anti-Pattern**: Failing immediately
```python
# ❌ DON'T DO THIS
def route_action(self, action: str, query: str, ...) -> Dict[str, Any]:
    status = self._check_build_readiness(index_name)
    if status.state != IndexBuildState.BUILT:
        raise ActionableError("Index not ready!")  # User-facing error!
```

---

### 1.8 Config Validation Pattern

**Pattern**: Use `model_post_init()` for validation warnings

**Good Example**:
```python
# ouroboros/config/schemas/indexes.py
class IndexBuildConfig(BaseModel):
    disk_space_threshold_gb: float = Field(default=2.0, ge=0.1)
    max_retries: int = Field(default=3, ge=0, le=10)
    # ... other fields ...
    
    @model_validator(mode="after")
    def validate_config(self) -> "IndexBuildConfig":
        """Validate config and log warnings for unsafe overrides."""
        if self.disk_space_threshold_gb < 1.0:
            logger.warning(
                "⚠️  Low disk_space_threshold_gb (%.1fGB). "
                "Recommended: 2GB+ to prevent mid-build failures.",
                self.disk_space_threshold_gb
            )
        
        if self.max_retries > 5:
            logger.warning(
                "⚠️  High max_retries (%d). "
                "May delay failure detection. Recommended: 3 retries.",
                self.max_retries
            )
        
        return self
```

**Anti-Pattern**: Raising errors on validation
```python
# ❌ DON'T DO THIS
@model_validator(mode="after")
def validate_config(self) -> "IndexBuildConfig":
    if self.disk_space_threshold_gb < 1.0:
        raise ValueError("disk_space_threshold_gb must be >=1GB")  # Too strict!
```

---

## 2. Testing Strategy

### 2.1 Testing Pyramid

```
         /\
        /  \  E2E Tests (5%)
       /    \  - Chaos tests (5 scenarios)
      /------\  - End-to-end workflows
     /        \
    /  Integr. \ Integration Tests (15%)
   /    Tests   \ - Fractal aggregation
  /              \ - Auto-repair flow
 /----------------\ - Query routing
/                  \
/   Unit Tests (80%) \ Unit Tests (80%)
/____________________\ - Data models
                       - Cache logic
                       - Config validation
                       - Component checks
```

**Coverage Targets**:
- Unit tests: >90% coverage
- Integration tests: >80% coverage
- E2E/Chaos tests: 5 critical scenarios

---

### 2.2 Unit Testing Approach

**Focus**: Test individual components in isolation

**Examples**:
- `BuildStatus` model validation
- `IndexBuildState` priority calculation
- `dynamic_build_status()` aggregation logic
- Cache TTL calculation
- Config validation warnings
- Component build status checks (mocked dependencies)

**Tools**:
- `pytest` for test framework
- `unittest.mock` for mocking
- `pytest-cov` for coverage reporting

---

### 2.3 Integration Testing Approach

**Focus**: Test interactions between components

**Examples**:
- Fractal aggregation (IndexManager → Index → Components)
- Query routing with build status checking
- Corruption detection → auto-repair → recovery
- Background rebuild coordination
- Progress reporting and cleanup

**Tools**:
- `pytest` with fixtures for real indexes
- Temporary directories for test data
- `threading` for concurrent scenarios

---

### 2.4 Chaos Testing Approach

**Focus**: Validate resilience under stress

**Scenarios**:
1. **Mid-Build Corruption**: Corrupt index during active build
2. **Concurrent Rebuild Requests**: Multiple corruption events simultaneously
3. **Corruption Under Query Load**: Corruption during 100 concurrent queries
4. **Disk Space Exhaustion**: Disk fills mid-build
5. **Config Validation**: Unsafe config overrides trigger warnings

**Tools**:
- `pytest` with custom fixtures for chaos scenarios
- `unittest.mock` to simulate disk full, corruption, etc.
- `threading` for concurrent load

---

### 2.5 Performance Testing Approach

**Focus**: Measure performance impact

**Benchmarks**:
- Query latency (P50, P95, P99) before/after implementation
- Cache hit rate measurement
- Build time overhead measurement
- Memory usage measurement

**Tools**:
- `pytest-benchmark` for performance benchmarks
- `memory_profiler` for memory usage
- Custom metrics collection

**Targets**:
- P99 query latency increase <5ms
- Cache hit rate >99%
- Build time overhead <5%
- Memory overhead <100KB

---

## 3. Deployment Guidance

### 3.1 Pre-Deployment Checklist

**Code Quality**:
- [ ] All unit tests pass (>90% coverage)
- [ ] All integration tests pass (>80% coverage)
- [ ] All chaos tests pass (5/5 scenarios)
- [ ] MyPy type checking passes (no errors)
- [ ] Ruff linting passes (no errors)
- [ ] Performance benchmarks meet targets

**Documentation**:
- [ ] Code comments complete (Google style docstrings)
- [ ] API documentation updated
- [ ] Config options documented
- [ ] Migration guide created (if breaking changes)

**Configuration**:
- [ ] `IndexBuildConfig` defaults reviewed
- [ ] Disk space threshold appropriate for deployment
- [ ] Retry and TTL settings appropriate
- [ ] Telemetry enabled/disabled as needed

---

### 3.2 Deployment Steps

**Step 1: Backup**
```bash
# Backup existing indexes (optional, but recommended)
cp -r .praxis-os/.cache/rag .praxis-os/.cache/rag.backup
```

**Step 2: Deploy Code**
```bash
# Pull latest code
git pull origin main

# Install dependencies (if any new ones)
pip install -r requirements.txt
```

**Step 3: Update Configuration**
```bash
# Review and update .mcp.yaml if needed
# Add IndexBuildConfig overrides if defaults not suitable
```

**Step 4: Restart Server**
```bash
# Restart MCP server
# (Method depends on deployment - systemd, docker, etc.)
```

**Step 5: Verify Health**
```bash
# Check server health
curl http://localhost:8000/health

# Or use get_server_info tool
# Expected: All indexes healthy, build status available
```

**Step 6: Monitor**
```bash
# Monitor logs for warnings or errors
tail -f .praxis-os/logs/server.log

# Watch for config validation warnings
# Watch for build progress updates
# Watch for corruption detection (should be rare)
```

---

### 3.3 Rollback Plan

**If Issues Occur**:

**Step 1: Identify Issue**
- Check logs for errors
- Check `get_server_info(action="health")` for index status
- Check query responses for "building" or "failed" status

**Step 2: Attempt Auto-Recovery**
- If indexes are BUILDING: Wait 1-2 minutes for rebuild to complete
- If indexes are FAILED: Check error message and remediation steps
- If disk space issue: Free up space and restart server

**Step 3: Rollback Code (if needed)**
```bash
# Revert to previous version
git checkout <previous-commit>

# Restart server
# (Method depends on deployment)
```

**Step 4: Restore Indexes (if needed)**
```bash
# Restore from backup
rm -rf .praxis-os/.cache/rag
cp -r .praxis-os/.cache/rag.backup .praxis-os/.cache/rag

# Restart server
```

---

### 3.4 Migration Notes

**Backward Compatibility**:
- Existing indexes continue to work (no schema changes)
- Existing health checks continue to work
- Existing search APIs unchanged
- No breaking changes to public APIs

**New Features**:
- Build status checking (automatic, no config needed)
- Auto-repair on corruption (automatic, no config needed)
- Progress reporting (automatic, configurable via `report_progress_per_component`)
- Telemetry (opt-in via `telemetry_enabled`)

**Configuration Changes**:
- New `build` section in `IndexesConfig` (optional, defaults provided)
- All existing configs continue to work

---

## 4. Troubleshooting

### 4.1 Common Issues

#### Issue 1: Query Returns "building" Status

**Symptom**: Query returns `{"status": "building", "progress": 45.0, ...}`

**Cause**: Index is currently building or rebuilding

**Resolution**:
1. Wait 30-60s and retry query
2. Check progress percentage (0-100)
3. If progress stuck for >5 minutes, check logs for errors
4. If disk space issue, free up space and restart server

**Prevention**: Ensure indexes are built on server startup (background thread)

---

#### Issue 2: Query Returns "failed" Status

**Symptom**: Query returns `{"status": "failed", "error": "...", "remediation": "..."}`

**Cause**: Index build failed (config error, resource error, etc.)

**Resolution**:
1. Read `error` and `remediation` fields
2. Follow remediation steps (e.g., fix config, free disk space)
3. Restart server to retry build
4. If config error, TTL=None (persists until restart)
5. If transient error, TTL=24h (auto-clears after 24h)
6. If resource error, TTL=1h (auto-clears after 1h)

**Prevention**: Validate config before deployment, ensure sufficient disk space

---

#### Issue 3: Corruption Detected

**Symptom**: Logs show "Index corruption detected: ..." and "Auto-repair in progress"

**Cause**: Index files corrupted (disk error, crash, etc.)

**Resolution**:
1. Auto-repair triggered automatically (background rebuild)
2. Subsequent queries return "building" status
3. Wait 1-2 minutes for rebuild to complete
4. If rebuild fails repeatedly, check disk health
5. If persistent, delete corrupted index and restart server

**Prevention**: Ensure disk health, use reliable storage, regular backups

---

#### Issue 4: Cache Hit Rate Low

**Symptom**: Performance degradation, logs show frequent `index.build_status()` calls

**Cause**: Cache TTL too short, or indexes frequently changing state

**Resolution**:
1. Check cache hit rate via performance metrics
2. If <99%, investigate why indexes are changing state frequently
3. If indexes are stable (BUILT), increase `_build_state_cache_ttl` (default: 60s)
4. If indexes are building, this is expected (dynamic TTL: 2-10s)

**Prevention**: Ensure indexes are built before heavy query load

---

#### Issue 5: Config Validation Warnings

**Symptom**: Logs show "⚠️ Low disk_space_threshold_gb..." or similar warnings

**Cause**: Unsafe config overrides detected

**Resolution**:
1. Review warning message and recommended value
2. Update config if warning is valid
3. If override is intentional, warnings can be ignored (system still works)

**Prevention**: Use default config values unless specific need for override

---

#### Issue 6: Background Rebuild Not Completing

**Symptom**: Index stuck in BUILDING state for >10 minutes

**Cause**: Rebuild thread crashed, insufficient resources, or very large index

**Resolution**:
1. Check logs for rebuild errors
2. Check disk space and memory
3. If resources sufficient, restart server (rebuild will retry)
4. If index is very large (>100K chunks), allow more time (up to 30 minutes)

**Prevention**: Ensure sufficient resources, monitor rebuild progress

---

### 4.2 Debugging Tips

**Enable Debug Logging**:
```python
# In .mcp.yaml or environment
logging:
  level: DEBUG
```

**Check Build Status Manually**:
```python
# Use get_server_info tool
result = get_server_info(action="health")
print(result["indexes"]["standards"]["build_status"])
```

**Inspect Progress Files**:
```bash
# Check for active builds
ls -lh .praxis-os/.cache/rag/build-progress/

# Read progress file
cat .praxis-os/.cache/rag/build-progress/standards.vector.progress.json
```

**Monitor Cache Hit Rate**:
```python
# Add custom metrics (if telemetry enabled)
# Track cache hits vs misses
# Target: >99% hit rate for BUILT indexes
```

**Simulate Corruption (for testing)**:
```bash
# Corrupt DuckDB database
echo "corrupted" > .praxis-os/.cache/rag/standards/metadata.db

# Trigger query to detect corruption
# Expected: Auto-repair triggered, "building" status returned
```

---

## 5. Performance Optimization

### 5.1 Cache Tuning

**Default TTLs**:
- BUILT state: 60s (stable, rarely changes)
- BUILDING state: 2-10s (dynamic, based on progress)
- FAILED state: 60s (stable until intervention)

**Tuning Recommendations**:
- If indexes are very stable (no updates), increase BUILT TTL to 300s (5 minutes)
- If indexes are frequently updated, decrease BUILT TTL to 30s
- BUILDING TTL should remain dynamic (2-10s) for responsive progress updates

**Configuration** (future enhancement):
```yaml
# .mcp.yaml (not yet implemented, but planned)
indexes:
  build:
    cache_ttl_built: 60  # seconds
    cache_ttl_building_min: 2  # seconds
    cache_ttl_building_max: 10  # seconds
```

---

### 5.2 Progress Reporting Frequency

**Default Behavior**:
- Progress callback called every 10-20 chunks
- Progress file written on each callback
- File write: <5ms (non-blocking)

**Tuning Recommendations**:
- If build time overhead >5%, reduce progress callback frequency (e.g., every 50 chunks)
- If progress updates too infrequent, increase callback frequency (e.g., every 5 chunks)
- Trade-off: Frequent updates = better visibility, but higher overhead

**Configuration**:
```yaml
# .mcp.yaml
indexes:
  build:
    report_progress_per_component: true  # Enable per-component progress
```

---

### 5.3 Component Check Optimization

**Current Approach**:
- Component checks are lightweight (<100ms each)
- Only verify: table exists + has rows
- No model loading, no test searches

**Future Optimizations** (if needed):
- Cache component status separately (per-component cache)
- Use file modification time to detect changes (avoid DB queries)
- Batch component checks (check all components in one DB query)

---

## 6. Future Enhancements

### 6.1 Async I/O for Progress Files

**Status**: Deferred (OS-001)

**Rationale**: Progress files are small (<1KB), writes are fast (<5ms). Async I/O adds complexity without significant benefit.

**Future Consideration**: If profiling shows progress file writes are a bottleneck (>5% of build time), implement async I/O using `aiofiles`.

---

### 6.2 Full Event System

**Status**: Deferred (OS-002)

**Rationale**: Current callback pattern is sufficient for 1 trigger → 1 action (corruption → rebuild). Full event system is overkill.

**Future Consideration**: If 3+ handlers needed per event, implement event bus using `asyncio` or `pydantic` events.

---

### 6.3 Distributed Index Building

**Status**: Deferred (OS-003)

**Rationale**: Single-server architecture. No need for distributed coordination.

**Future Consideration**: If multi-server deployment needed, implement distributed locking using Redis or etcd.

---

### 6.4 Real-Time Progress Streaming

**Status**: Deferred (OS-005)

**Rationale**: Polling-based progress (2-10s updates) is sufficient for current use cases.

**Future Consideration**: If sub-second updates needed, implement WebSocket streaming or Server-Sent Events (SSE).

---

## 7. References

### 7.1 Related Standards

- `cascading-health-check-architecture/` - Fractal pattern reference
- `stateless-instance-architecture.md` - AI statelessness principles
- `ai-capabilities-trust.md` - AI operational guidelines
- `retry-strategies.md` - Exponential backoff patterns
- `graceful-degradation.md` - Handling partial failures

### 7.2 Related Specs

- `srd.md` - Software Requirements Document (31 FRs, 16 NFRs)
- `specs.md` - Technical Specifications (architecture, components, APIs)
- `tasks.md` - Implementation Tasks (8 phases, 38 tasks)

### 7.3 Supporting Documents

- `supporting-docs/2025-11-14-resilient-index-building-COMPREHENSIVE-V2.md` - Primary design document
- `supporting-docs/2025-11-14-REVIEW-SUMMARY.md` - Pessimistic principal engineer review
- `supporting-docs/2025-11-14-resilient-index-building-feedback.md` - ChatGPT-5/Cline review
- `supporting-docs/2025-11-14-build-status-performance-analysis.md` - Performance analysis
- `supporting-docs/2025-11-14-event-system-analysis.md` - Event system analysis

---

## 8. Approval

**Implementation Guidance Author**: Claude (AI Assistant)  
**Date**: 2025-11-14  
**Status**: Pending Review

**Reviewers**:
- [ ] Technical Lead
- [ ] Implementation Team
- [ ] QA Team

**Approval Criteria**:
- [ ] Code patterns are clear and actionable
- [ ] Testing strategy is comprehensive
- [ ] Deployment guidance is complete
- [ ] Troubleshooting tips are helpful
- [ ] Performance optimization guidance is practical

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-14  
**Next Review**: After Phase 5 (Finalization)

