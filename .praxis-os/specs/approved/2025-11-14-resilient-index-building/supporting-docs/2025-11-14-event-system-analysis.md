# Event System Analysis: Do We Need It?

**Date**: 2025-11-14  
**Context**: User question: "should we have an internal event system, so health check comes back bad, triggers event, event processor flushes healthy out of the cache, then triggers index rebuild, or am i over complicating things?"

---

## 🎯 The Question

**Proposed Flow**:
```
health_check() → BAD
  ↓
Event: "index_unhealthy"
  ↓
Event Processor:
  1. Flush cache (invalidate_build_cache)
  2. Trigger rebuild
```

**Is this needed, or over-engineering?**

---

## 📊 Current Architecture Analysis

### Current Pattern: Inline Error Handling

```python
# ouroboros/subsystems/rag/standards/container.py:180-188

def search(self, query: str, **kwargs) -> List[SearchResult]:
    try:
        with self._lock_manager.shared_lock():
            return self._semantic_index.search(query, **kwargs)
    except Exception as e:
        if is_corruption_error(e):
            logger.warning("Corruption detected during search, attempting auto-repair...")
            raise ActionableError(
                what_failed="Search standards index",
                why_failed=f"Index corrupted: {e}",
                how_to_fix="Auto-repair required. Call rebuild_secondary_indexes() or rebuild index."
            ) from e
        else:
            raise
```

**Current Flow**:
```
search() → Exception
  ↓
is_corruption_error(e)?
  ↓ YES
Raise ActionableError (tells caller to rebuild)
  ↓
Caller decides what to do
```

**Key Observation**: Current system does NOT auto-rebuild, it just **reports** the need to rebuild.

---

## 🤔 Event System: Pros & Cons

### ✅ Pros (Why You Might Want It)

#### 1. **Decoupling** (Separation of Concerns)
```python
# Without events (current):
def search():
    try:
        # ... search logic ...
    except Exception as e:
        if is_corruption_error(e):
            # Search method knows about corruption AND cache AND rebuild
            invalidate_build_cache()
            trigger_rebuild()
            raise

# With events (proposed):
def search():
    try:
        # ... search logic ...
    except Exception as e:
        if is_corruption_error(e):
            # Search method only knows about corruption
            emit_event("index_corrupted", index_name="standards")
            raise

# Elsewhere:
@on_event("index_corrupted")
def handle_corruption(event):
    invalidate_build_cache(event.index_name)
    trigger_rebuild(event.index_name)
```

**Benefit**: Search method doesn't need to know about cache or rebuild logic.

---

#### 2. **Multiple Handlers** (Extensibility)
```python
@on_event("index_corrupted")
def flush_cache(event):
    invalidate_build_cache(event.index_name)

@on_event("index_corrupted")
def trigger_rebuild(event):
    background_rebuild(event.index_name)

@on_event("index_corrupted")
def send_alert(event):
    logger.error("Index corrupted: %s", event.index_name)
    # Future: Send to monitoring system
```

**Benefit**: Easy to add new behaviors without modifying existing code.

---

#### 3. **Async/Background Processing** (Non-blocking)
```python
# Without events: Blocking
def search():
    try:
        # ... search ...
    except Exception as e:
        if is_corruption_error(e):
            rebuild_index()  # ⚠️ BLOCKS for minutes
            raise

# With events: Non-blocking
def search():
    try:
        # ... search ...
    except Exception as e:
        if is_corruption_error(e):
            emit_event("index_corrupted")  # ✅ Returns immediately
            raise

# Event handler runs in background thread
@on_event("index_corrupted", async=True)
def handle_corruption(event):
    rebuild_index()  # Runs in background
```

**Benefit**: Search fails fast, rebuild happens in background.

---

#### 4. **Observability** (Event Log)
```python
# All events logged automatically
event_log = [
    {"timestamp": "2025-11-14T10:30:00Z", "event": "index_corrupted", "index": "standards"},
    {"timestamp": "2025-11-14T10:30:01Z", "event": "cache_invalidated", "index": "standards"},
    {"timestamp": "2025-11-14T10:30:02Z", "event": "rebuild_started", "index": "standards"},
    {"timestamp": "2025-11-14T10:35:00Z", "event": "rebuild_completed", "index": "standards"},
]
```

**Benefit**: Clear audit trail of what happened and when.

---

### ❌ Cons (Why It Might Be Over-Engineering)

#### 1. **Complexity** (More Moving Parts)
```python
# Current: 3 lines
if is_corruption_error(e):
    invalidate_build_cache()
    raise ActionableError(...)

# With events: 20+ lines
class EventBus:
    def __init__(self): ...
    def emit(self, event): ...
    def on(self, event_type, handler): ...
    def _dispatch(self, event): ...

event_bus.on("index_corrupted", handle_corruption)
event_bus.emit("index_corrupted", index_name="standards")
```

**Cost**: More code to maintain, more potential bugs.

---

#### 2. **Indirection** (Harder to Debug)
```python
# Current: Direct call stack
search() → is_corruption_error() → invalidate_cache() → raise

# With events: Indirect call stack
search() → emit_event() → event_bus → handler_1() → handler_2() → handler_3()
```

**Cost**: Harder to trace execution flow, harder to debug.

---

#### 3. **Ordering Issues** (Race Conditions)
```python
# What if handlers run in wrong order?
@on_event("index_corrupted")
def rebuild(event):
    # Reads from cache (expects it to be invalidated)
    if cache.get(event.index_name):
        return  # Already built

@on_event("index_corrupted")
def flush_cache(event):
    cache.invalidate(event.index_name)

# If rebuild runs BEFORE flush_cache, rebuild is skipped!
```

**Cost**: Need to manage handler ordering, priority, dependencies.

---

#### 4. **Overkill for Simple Cases** (YAGNI)
```python
# Current use cases:
# 1. Corruption detected → invalidate cache + report error
# 2. Build complete → invalidate cache

# Do we need an event system for 2 use cases?
```

**Cost**: "You Aren't Gonna Need It" - premature abstraction.

---

## 🎯 Decision Framework

### When Event System Makes Sense

✅ **Use events if**:
1. **Multiple listeners**: 3+ handlers for same event
2. **Async processing**: Need background/non-blocking execution
3. **Cross-subsystem**: Events span multiple modules/subsystems
4. **Audit trail**: Need comprehensive event logging
5. **Plugin architecture**: External code needs to hook into events

### When Direct Calls Make Sense

✅ **Use direct calls if**:
1. **Simple flow**: 1-2 actions per trigger
2. **Synchronous**: Need immediate execution
3. **Single subsystem**: All code in same module
4. **Clear ownership**: One component owns the flow
5. **Easy to test**: Direct calls are easier to mock/test

---

## 📊 Current Praxis-OS Context

### Current Needs

| Trigger | Actions | Count | Async? | Cross-subsystem? |
|---------|---------|-------|--------|------------------|
| **Corruption detected** | 1. Invalidate cache<br>2. Report error | 2 | No | No (all in RAG) |
| **Build complete** | 1. Invalidate cache | 1 | No | No (all in RAG) |
| **Health check fails** | 1. Report status | 1 | No | No (all in RAG) |

**Analysis**:
- ❌ Not many actions per trigger (1-2)
- ❌ Not async (all synchronous)
- ❌ Not cross-subsystem (all in RAG)
- ✅ Simple, linear flows

**Verdict**: **Direct calls are sufficient** for current needs.

---

## 🚀 Recommendation: Hybrid Approach

### Phase 1: Keep It Simple (Now)

**Use direct calls with clear helper methods**:

```python
class IndexManager:
    def _handle_corruption(self, index_name: str, error: Exception) -> None:
        """
        Handle index corruption detection.
        
        Centralized corruption handling:
        1. Invalidate build cache
        2. Log error
        3. Raise actionable error
        """
        logger.error("Index corruption detected: %s - %s", index_name, error)
        
        # Invalidate cache (index is no longer BUILT)
        self.invalidate_build_cache(index_name)
        
        # Raise actionable error (caller decides next steps)
        raise ActionableError(
            what_failed=f"{index_name} index search",
            why_failed=f"Index corrupted: {error}",
            how_to_fix="Rebuild index or restart server (auto-rebuild on startup)"
        ) from error


# Usage in search methods:
def search(self, query: str, **kwargs) -> List[SearchResult]:
    try:
        return self._semantic_index.search(query, **kwargs)
    except Exception as e:
        if is_corruption_error(e):
            self._index_manager._handle_corruption("standards", e)
        else:
            raise
```

**Benefits**:
- ✅ Centralized corruption handling
- ✅ Cache invalidation in one place
- ✅ Easy to test (mock `_handle_corruption`)
- ✅ No event system complexity

---

### Phase 2: Add Events When Needed (Future)

**If you later need**:
- Multiple listeners (e.g., send alerts, update metrics, trigger backups)
- Async processing (e.g., background rebuild)
- Cross-subsystem coordination (e.g., notify workflow system)

**Then add a lightweight event system**:

```python
# Simple event bus (50 lines, not 500)
class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
    
    def on(self, event_type: str, handler: Callable) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def emit(self, event_type: str, **data) -> None:
        for handler in self._handlers.get(event_type, []):
            try:
                handler(**data)
            except Exception as e:
                logger.error("Event handler failed: %s", e)


# Global event bus (singleton)
event_bus = EventBus()

# Register handlers
event_bus.on("index_corrupted", lambda index_name, error: 
    index_manager.invalidate_build_cache(index_name))

# Emit events
event_bus.emit("index_corrupted", index_name="standards", error=e)
```

**Benefits**:
- ✅ Simple implementation (no framework needed)
- ✅ Easy to add when needed
- ✅ Doesn't complicate current code

---

## 🎯 USER FEEDBACK: "raising an error is a woopty doo, have the bad state detected, index rebuilt to healthy is the target, not just flag it"

**Translation**: We need **AUTO-REPAIR**, not just error reporting!

### **Current State (Code Intelligence Analysis)**

**What exists**:
- ✅ Background rebuild on **startup** (`_build_indexes_background()` in `server.py:199`)
- ✅ File watcher triggers rebuild on **file changes**
- ❌ **NO auto-repair on runtime corruption detection**

**Current corruption flow**:
```
search() → corruption detected → raise ActionableError → query fails → user sad 😞
```

**Desired corruption flow**:
```
search() → corruption detected → trigger background rebuild → return "building" status → eventual success 🎉
```

---

## 🎉 REVISED Recommendation: Background Auto-Repair (No Events Needed)

### **Solution: Reuse Existing Background Build Pattern**

**The pattern already exists!** Just extend it to handle runtime corruption.

```python
# ouroboros/subsystems/rag/index_manager.py

class IndexManager:
    def __init__(self, ...):
        # ... existing init ...
        
        # Track indexes currently rebuilding (prevent duplicate rebuilds)
        self._rebuilding_indexes: Set[str] = set()
        self._rebuild_lock = threading.Lock()
    
    def _handle_corruption(
        self, 
        index_name: str, 
        error: Exception,
        operation: str = "search"
    ) -> Dict[str, Any]:
        """
        Handle corruption detection with automatic background rebuild.
        
        Flow:
        1. Log corruption
        2. Invalidate build cache
        3. Start background rebuild (if not already rebuilding)
        4. Return "building" response (don't fail query)
        
        Returns:
            Dict with status="building" and rebuild progress
        """
        logger.error("Corruption detected: %s.%s - %s", index_name, operation, error)
        
        # Invalidate cache (index no longer BUILT)
        self.invalidate_build_cache(index_name)
        
        # Start background rebuild (non-blocking)
        with self._rebuild_lock:
            if index_name not in self._rebuilding_indexes:
                self._rebuilding_indexes.add(index_name)
                
                # Start daemon thread for rebuild
                rebuild_thread = threading.Thread(
                    target=self._rebuild_index_background,
                    args=(index_name,),
                    name=f"rebuild-{index_name}",
                    daemon=True
                )
                rebuild_thread.start()
                
                logger.info("🔄 Started background rebuild for %s", index_name)
        
        # Return "building" response (query doesn't fail)
        return {
            "status": "building",
            "message": f"Index {index_name} corrupted, rebuilding in background",
            "suggestion": "Retry query in 30-60 seconds",
            "results": [],
            "error_type": "corruption_auto_repair",
            "index_name": index_name
        }
    
    def _rebuild_index_background(self, index_name: str) -> None:
        """
        Rebuild single index in background thread.
        
        Reuses existing ensure_all_indexes_healthy() logic but for single index.
        """
        try:
            logger.info("🔄 Rebuilding %s index (auto-repair)...", index_name)
            
            # Get index instance
            index = self._indexes.get(index_name)
            if not index:
                logger.error("❌ Index %s not found for rebuild", index_name)
                return
            
            # Rebuild index (force=True to overwrite corrupted data)
            index.build(force=True)
            
            # Invalidate cache again (now it's BUILT)
            self.invalidate_build_cache(index_name)
            
            logger.info("✅ Auto-repair complete for %s", index_name)
            
        except Exception as e:
            logger.error("❌ Auto-repair failed for %s: %s", index_name, e)
            logger.error("   Index will remain unhealthy until manual rebuild")
        finally:
            # Remove from rebuilding set
            with self._rebuild_lock:
                self._rebuilding_indexes.discard(index_name)


# Usage in StandardsIndex.search():
def search(self, query: str, **kwargs) -> List[SearchResult]:
    try:
        with self._lock_manager.shared_lock():
            return self._semantic_index.search(query, **kwargs)
    except Exception as e:
        if is_corruption_error(e):
            # Return "building" response, don't raise
            return self._index_manager._handle_corruption("standards", e, "search")
        else:
            raise
```

### **Benefits of This Approach**

✅ **No event system complexity** - Reuses existing background thread pattern
✅ **Auto-repair** - Corruption triggers rebuild automatically
✅ **Non-blocking** - Query returns immediately with "building" status
✅ **Eventual consistency** - Index converges to healthy state
✅ **Idempotent** - Multiple corruption detections don't start duplicate rebuilds
✅ **Consistent with startup** - Same pattern as `_build_indexes_background()`
✅ **Observable** - Logs show rebuild progress
✅ **Testable** - Can mock threading for tests

### **Integration with Build Status Caching**

This works perfectly with the caching strategy from the comprehensive design:

1. **Corruption detected** → `_handle_corruption()` called
2. **Cache invalidated** → `invalidate_build_cache(index_name)`
3. **Background rebuild starts** → Index state = `BUILDING`
4. **Query returns** → `{"status": "building", "progress": "0%"}`
5. **Subsequent queries** → Cache returns `BUILDING` state (5s TTL)
6. **Rebuild completes** → Cache invalidated again, now `BUILT`
7. **Next query** → Success! 🎉

### **Add to Comprehensive Design Doc**

**Part 4.7: Auto-Repair on Corruption Detection**

```python
# See code above
```

---

## 🎯 Summary

**User was right**: Just raising an error is "woopty doo" - we need auto-repair!

**Solution**: 
- ✅ Reuse existing background build pattern from startup
- ✅ Add `_handle_corruption()` that starts background rebuild
- ✅ Return "building" status instead of failing query
- ✅ No event system needed (direct calls + background threads)

**When to add events**:
- Still not now! This is 1 trigger → 1 action (rebuild)
- Add events when you need 3+ actions per corruption (alert, metrics, backup)

**Result**: Corruption → Auto-repair → Eventual success 🚀

---

## 📝 Implementation: Centralized Corruption Handling

### ✅ IMPLEMENTED IN V2 DESIGN

**See**: `.praxis-os/workspace/design/2025-11-14-resilient-index-building-COMPREHENSIVE-V2.md`
- Part 3: Corruption Handling (Complete Coverage)
- FIX #7: Corruption Handler Callback Pattern
- FIX #6: Add Corruption Handling to `build()` and `update()`
- FIX #3: Add Corruption Handling to `route_action()`

**Original Proposal (For Reference)**:

**Part 4.6: Corruption Handling (Centralized)**

```python
# ouroboros/subsystems/rag/index_manager.py

class IndexManager:
    def _handle_corruption(
        self, 
        index_name: str, 
        error: Exception,
        operation: str = "search"
    ) -> None:
        """
        Centralized corruption handling.
        
        Called when corruption is detected in any index operation.
        Handles cache invalidation and error reporting.
        
        Args:
            index_name: Name of corrupted index
            error: Original corruption error
            operation: Operation that detected corruption
        
        Raises:
            ActionableError: With remediation instructions
        """
        logger.error(
            "Index corruption detected: %s during %s - %s",
            index_name, operation, error
        )
        
        # Invalidate build cache (index is no longer BUILT)
        self.invalidate_build_cache(index_name)
        
        # Raise actionable error with clear remediation
        raise ActionableError(
            what_failed=f"{index_name} index {operation}",
            why_failed=f"Index corrupted: {error}",
            how_to_fix=(
                "Options:\n"
                "1. Restart server (auto-rebuild on startup)\n"
                "2. Manually rebuild: pos_search_project(action='rebuild_index', index='{index_name}')\n"
                "3. Check disk space and file permissions"
            )
        ) from error


# Usage in StandardsIndex:
def search(self, query: str, **kwargs) -> List[SearchResult]:
    try:
        with self._lock_manager.shared_lock():
            return self._semantic_index.search(query, **kwargs)
    except Exception as e:
        if is_corruption_error(e):
            self._index_manager._handle_corruption("standards", e, "search")
        else:
            raise


# Usage in CodeIndex:
def search(self, query: str, **kwargs) -> List[SearchResult]:
    try:
        # ... search logic ...
    except Exception as e:
        if is_corruption_error(e):
            self._index_manager._handle_corruption("code", e, "search")
        else:
            raise
```

**Benefits**:
- ✅ Single place to update corruption handling
- ✅ Consistent error messages across indexes
- ✅ Automatic cache invalidation
- ✅ Easy to test (mock `_handle_corruption`)
- ✅ No event system complexity

---

## 🎯 Summary

**Your instinct was good** (thinking about decoupling), but **event system is overkill** for current needs.

**Better approach**:
1. ✅ Centralize corruption handling in `IndexManager._handle_corruption()`
2. ✅ Keep direct calls (simpler, easier to debug)
3. ✅ Add events later if complexity grows (YAGNI principle)

**When to revisit**:
- Need 3+ handlers per event
- Need async/background processing
- Need cross-subsystem coordination

**For now**: Keep it simple, centralize the logic, avoid premature abstraction. 🚀

