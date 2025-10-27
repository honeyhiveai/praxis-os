# Thread Safety Metrics Monitoring Guide

**Purpose:** How to access and interpret cache performance metrics for monitoring thread safety effectiveness.

---

## Accessing Metrics

The `CacheMetrics` class tracks cache performance and race condition detection. Metrics are accessible through the WorkflowEngine:

### Python REPL Example

```python
# In Python REPL or code
from mcp_server.workflow_engine import WorkflowEngine
from mcp_server.state_manager import StateManager
from mcp_server.rag_engine import RAGEngine

# Initialize engine (adjust paths as needed)
engine = WorkflowEngine(
    state_manager=StateManager(state_dir),
    rag_engine=RAGEngine(index_path, standards_path)
)

# Get metrics snapshot
metrics = engine.get_metrics()
print(metrics)
```

### Expected Output

```python
{
    'hits': 950,              # Cache hits (found existing session)
    'misses': 50,             # Cache misses (created new session)
    'double_loads': 3,        # Race conditions prevented by locking
    'lock_waits': 50,         # Times thread acquired lock
    'hit_rate': 0.95,         # Cache hit rate (95%)
    'total_operations': 1000  # Total cache operations
}
```

---

## Metrics Interpretation

### Normal Operation

**Healthy metrics:**
- `hit_rate`: 90-99% (high cache efficiency)
- `double_loads`: 0-5 per hour (rare races)
- `lock_waits / total`: <5% (low contention)

**Example:**
```python
metrics = engine.get_metrics()
if metrics['hit_rate'] > 0.90:
    print("✅ Cache working efficiently")
if metrics['double_loads'] < 10:
    print("✅ Minimal race conditions")
```

### Alert Thresholds

#### 🟡 Warning: Elevated Race Conditions

**Trigger:** `double_loads > 10 per hour`

**Meaning:** Multiple threads frequently requesting same uncached sessions simultaneously

**Action:**
- Check logs for WARNING messages about race conditions
- Review if dual-transport mode is causing contention
- Consider increasing cache TTL if appropriate

**Example Check:**
```python
import time

metrics_start = engine.get_metrics()
time.sleep(3600)  # Wait 1 hour
metrics_end = engine.get_metrics()

double_loads_per_hour = metrics_end['double_loads'] - metrics_start['double_loads']

if double_loads_per_hour > 10:
    print("🟡 WARNING: High race condition rate")
    print(f"   Double loads in last hour: {double_loads_per_hour}")
```

#### 🔴 Critical: High Lock Contention

**Trigger:** `lock_waits / total_operations > 0.05` (5%)

**Meaning:** Threads spending significant time waiting for locks

**Action:**
- Review concurrent access patterns
- Check if cache is too small (frequent misses forcing lock acquisition)
- Investigate if specific workflows cause contention spikes

**Example Check:**
```python
metrics = engine.get_metrics()
contention_rate = metrics['lock_waits'] / metrics['total_operations'] if metrics['total_operations'] > 0 else 0

if contention_rate > 0.05:
    print(f"🔴 CRITICAL: High lock contention ({contention_rate:.1%})")
    print(f"   Lock waits: {metrics['lock_waits']}")
    print(f"   Total ops: {metrics['total_operations']}")
```

#### 🟡 Warning: Low Cache Hit Rate

**Trigger:** `hit_rate < 0.90` (90%)

**Meaning:** Cache not effective, frequent session recreations

**Action:**
- Review if sessions are being cleared too frequently
- Check if workflow patterns cause poor cache locality
- Verify cache is not being unnecessarily cleared in tests/dev

**Example Check:**
```python
metrics = engine.get_metrics()

if metrics['hit_rate'] < 0.90:
    print(f"🟡 WARNING: Low cache hit rate ({metrics['hit_rate']:.1%})")
    print(f"   Hits: {metrics['hits']}, Misses: {metrics['misses']}")
```

---

## Log Monitoring

Race conditions that are prevented by locking generate WARNING logs:

### Log Format

```
WARNING: Race condition detected (double load) - prevented by lock. session_id=abc123, thread=Thread-5
```

### Monitoring Logs

```bash
# Check for race condition warnings in logs
grep "Race condition detected" /path/to/mcp_server.log | wc -l

# View recent race conditions with context
grep -C 3 "Race condition detected" /path/to/mcp_server.log | tail -20
```

**Normal:** 0-5 occurrences per hour  
**Investigate:** >10 occurrences per hour  
**Action Required:** >50 occurrences per hour (indicates systemic concurrency issue)

---

## Monitoring in Production

### Periodic Health Check

Add this to your monitoring scripts:

```python
def check_cache_health(engine):
    """Periodic health check for cache metrics."""
    metrics = engine.get_metrics()
    
    issues = []
    
    # Check hit rate
    if metrics['hit_rate'] < 0.90:
        issues.append(f"Low hit rate: {metrics['hit_rate']:.1%}")
    
    # Check lock contention
    if metrics['total_operations'] > 0:
        contention = metrics['lock_waits'] / metrics['total_operations']
        if contention > 0.05:
            issues.append(f"High contention: {contention:.1%}")
    
    # Check race conditions
    # (Compare with previous snapshot to get rate)
    if metrics['double_loads'] > 100:  # Absolute threshold
        issues.append(f"Many double loads: {metrics['double_loads']}")
    
    if issues:
        print("🟡 Cache Health Issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Cache Health OK")
        print(f"  Hit rate: {metrics['hit_rate']:.1%}")
        print(f"  Total ops: {metrics['total_operations']}")
        return True
```

### Reset Metrics

For testing or periodic resets:

```python
# Reset metrics to zero
engine.metrics.reset()

# Verify reset
metrics = engine.get_metrics()
assert metrics['hits'] == 0
assert metrics['misses'] == 0
```

---

## Future Enhancements (Not in Scope)

- **Prometheus Export**: Export metrics to Prometheus for dashboard visualization
- **Automatic Alerting**: Trigger alerts when thresholds exceeded
- **Time-series Storage**: Track metrics over time for trend analysis
- **Per-workflow Metrics**: Track metrics separately per workflow type

These are marked as P2 (priority 2) and not included in current implementation.

---

## Troubleshooting

### High Double Load Count

**Symptom:** `double_loads` metric continuously increasing

**Cause:** Multiple threads/transports requesting same sessions simultaneously

**Resolution:**
1. Check if dual-transport mode (stdio + HTTP) is active
2. Review if sub-agents are causing concurrent requests
3. Verify session IDs are unique across requests
4. Consider if this is expected behavior (races are being prevented correctly)

### Zero Metrics After Restart

**Symptom:** All metrics show zero after MCP server restart

**Expected:** Metrics are in-memory only, reset on restart

**Resolution:** This is normal behavior. Metrics track current session only.

### Metrics Not Updating

**Symptom:** Metrics remain static during active use

**Cause:** Possible issue with metrics integration

**Debug:**
```python
# Check if metrics object exists
assert hasattr(engine, 'metrics')

# Check if recording methods are being called
# Add debug logging or breakpoints in:
# - engine.get_session() where record_hit/miss/double_load are called
```

---

## Summary

- ✅ **Access metrics**: `engine.get_metrics()`
- ✅ **Monitor hit rate**: Should be >90%
- ✅ **Watch double loads**: <10/hour is healthy
- ✅ **Check contention**: lock_waits/total <5%
- ✅ **Review logs**: Race condition WARNINGs should be rare
- ✅ **Use for validation**: Metrics prove thread safety is working

