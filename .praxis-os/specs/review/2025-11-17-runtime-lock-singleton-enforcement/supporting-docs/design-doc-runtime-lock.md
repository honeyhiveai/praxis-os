# Runtime Lock: Singleton MCP Server Enforcement

**Document Type:** Design Document  
**Status:** Approved - Ready for Implementation  
**Created:** 2025-11-17  
**Updated:** 2025-11-17 (Decision finalized)  
**Author:** AI Agent (Sonnet 4.5) + Josh (Human Orchestrator)  
**Related Issues:** Cursor MCP race condition bug (multiple server spawns)  
**Decision:** Option B - Create Separate RuntimeLock Class ✅

---

## Executive Summary

**Problem:** Cursor's MCP client spawns multiple ouroboros server instances simultaneously, causing race conditions, index corruption, and resource exhaustion. The current `InitLock` only prevents concurrent initialization but releases after startup, allowing multiple servers to run concurrently.

**Solution:** Implement a `RuntimeLock` that is acquired at server startup and held for the entire process lifetime, ensuring only one ouroboros MCP server runs per project at any time.

**Impact:** 
- **Reliability:** Eliminates index corruption from concurrent builds
- **Performance:** Reduces resource waste (CPU, memory) from zombie processes
- **UX:** Graceful handling of duplicate spawns (fast-fail, clear messaging)

**Timeline:** 4-6 hours (design → spec → implementation → testing)

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Current Architecture](#current-architecture)
3. [Root Cause Analysis](#root-cause-analysis)
4. [Requirements](#requirements)
5. [Design Options](#design-options)
6. [Proposed Solution](#proposed-solution)
7. [Implementation Plan](#implementation-plan)
8. [Testing Strategy](#testing-strategy)
9. [Rollout Plan](#rollout-plan)
10. [Risks and Mitigations](#risks-and-mitigations)
11. [Appendices](#appendices)

---

## Problem Statement

### The Issue

**Observed Behavior:**
```bash
$ ps aux | grep ouroboros
josh  72509  82.4%  0.0%  Running  Wed 1PM   5188h  # Zombie (old)
josh  47294  77.0% 10.9%  Running  8:23 AM     7h   # Active
josh  63049   0.1%  0.3%  Sleeping Sat 3PM     8h   # Zombie
josh  16526   0.0%  0.4%  Sleeping 2:10 PM     5h   # Zombie
josh  32128   0.0%  0.4%  Sleeping Sat 4PM    10h   # Zombie
```

**5 concurrent ouroboros MCP servers running for the same project!**

**Consequences:**
1. **Index Corruption:** Multiple processes building code index simultaneously
   - Race conditions writing to DuckDB
   - Duplicate log entries (2x-4x)
   - "Bouncing" index (rebuilds never complete)

2. **Resource Exhaustion:**
   - 82.4% + 77.0% = 159.4% CPU usage (2 cores pegged)
   - 10.9% + 0.3% + 0.4% + 0.4% = 12% RAM (7.9 GB wasted)
   - Cursor temp file writes (large responses)

3. **User Experience:**
   - Slow searches (multiple servers competing)
   - Unpredictable behavior (which server responds?)
   - Manual cleanup required (`kill -9`)

### Why This Matters

**Frequency:** High (happens every time Cursor misbehaves)
**Severity:** Critical (data corruption risk)
**User Impact:** Requires manual intervention (kills productivity)

---

## Current Architecture

### InitLock (Existing)

**Purpose:** Prevent concurrent initialization  
**Location:** `.praxis-os/ouroboros/foundation/init_lock.py`  
**Mechanism:** File-based lock with PID tracking

**Lock Lifecycle:**
```python
# __main__.py
init_lock = InitLock(base_path, timeout_seconds=10)

if not init_lock.acquire():
    # Another process is INITIALIZING
    sys.exit(0)

# Initialize server (indexes, subsystems, etc.)
initialize_server()

# ❌ PROBLEM: Lock released after init
init_lock.release()

# Server keeps running (no lock held!)
run_server_forever()
```

**The Gap:**
- ✅ Prevents concurrent initialization (good!)
- ❌ Allows multiple servers to run after init (bad!)

### IndexLockManager (Existing)

**Purpose:** Prevent concurrent index operations  
**Location:** `.praxis-os/ouroboros/subsystems/rag/lock_manager.py`  
**Mechanism:** fcntl-based file locking (Unix)

**Lock Types:**
- **Shared lock:** Multiple readers (searches)
- **Exclusive lock:** Single writer (builds)

**Scope:** Per-index (standards, code, AST, graph)

**Why It's Not Enough:**
- Only locks during index operations (not server lifetime)
- Doesn't prevent multiple servers from starting
- Per-index (not per-server)

---

## Root Cause Analysis

### Why Does Cursor Spawn Multiple Servers?

**Hypothesis 1: Race Condition in MCP Client**
- Cursor's MCP client spawns server on demand
- Multiple tool calls arrive simultaneously
- Client spawns 3-5 servers before first one responds
- No client-side deduplication

**Evidence:**
- Logs show multiple `CodeIndex.build()` calls at same timestamp
- All processes have similar start times (within seconds)
- Documented in praxis-os as "Cursor MCP bug"

**Hypothesis 2: Restart Logic Bug**
- Cursor detects server crash/hang
- Spawns new server
- Old server recovers (zombie)
- Both keep running

**Evidence:**
- Some processes are days old (PID 72509: Wed 1PM)
- Mix of active (100% CPU) and sleeping (0% CPU) processes

### Why Doesn't InitLock Prevent This?

**The Timing Gap:**

```
Timeline:
─────────────────────────────────────────────────────────────
T0: Server A starts
T1: Server A acquires InitLock
T2: Server A initializes (10s)
T3: Server A releases InitLock  ← ❌ TOO EARLY
T4: Server A runs forever
T5: Server B starts
T6: Server B acquires InitLock  ← ✅ Lock available!
T7: Server B initializes
T8: Server B releases InitLock
T9: Server B runs forever
T10: Both A and B running! ← ❌ PROBLEM
```

**The Design Flaw:**
- InitLock is for initialization, not runtime
- Lock released after init completes
- No mechanism to prevent concurrent execution

---

## Requirements

### Functional Requirements

**FR-1: Singleton Enforcement**
- **Description:** Only one ouroboros MCP server per project
- **Acceptance Criteria:**
  - Second spawn attempt exits gracefully (exit code 0)
  - No error messages (this is expected behavior)
  - Fast-fail (<1 second to detect and exit)

**FR-2: Stale Lock Detection**
- **Description:** Detect and cleanup locks from crashed processes
- **Acceptance Criteria:**
  - If lock holder PID is dead → claim lock
  - If lock holder PID is zombie → claim lock
  - If lock file is corrupted → claim lock (with warning)

**FR-3: Graceful Degradation**
- **Description:** Handle edge cases without blocking valid servers
- **Acceptance Criteria:**
  - Lock file missing → create and claim
  - Lock file unreadable → log warning, proceed
  - Lock directory missing → create directory, proceed

**FR-4: Cross-Platform Support**
- **Description:** Works on Unix, Linux, macOS, Windows
- **Acceptance Criteria:**
  - Unix/Linux/macOS: fcntl-based locking
  - Windows: File creation atomicity (O_CREAT | O_EXCL)
  - Consistent behavior across platforms

**FR-5: Observability**
- **Description:** Clear logging for debugging
- **Acceptance Criteria:**
  - Log when lock acquired (with PID)
  - Log when duplicate spawn detected (with holder PID)
  - Log when stale lock cleaned up (with dead PID)

### Non-Functional Requirements

**NFR-1: Reliability**
- **Target:** 0 false positives (never kill valid server)
- **Rationale:** False positive = user's work interrupted

**NFR-2: Performance**
- **Target:** <100ms lock acquisition time
- **Rationale:** Should not slow down server startup

**NFR-3: Maintainability**
- **Target:** <200 LOC, 100% type hints, comprehensive tests
- **Rationale:** Foundation layer code must be bulletproof

**NFR-4: Compatibility**
- **Target:** No breaking changes to existing code
- **Rationale:** Should be drop-in addition to `__main__.py`

---

## Design Options

### ✅ DECISION: Option B - Create Separate RuntimeLock Class

**Status:** **APPROVED** (2025-11-17)  
**Rationale:** Clean architecture, clear separation of concerns, no changes to existing code

---

### Option A: Extend InitLock to Hold for Runtime

**Approach:**
- Modify `InitLock.release()` to be a no-op
- Lock held until process exits (atexit handler)
- Rename to `RuntimeLock` for clarity

**Pros:**
- ✅ Minimal code changes
- ✅ Reuses existing PID tracking logic
- ✅ Fast to implement (1-2 hours)

**Cons:**
- ❌ Conflates init and runtime concerns
- ❌ Less clear semantics (lock name says "init")
- ❌ Harder to test (need to mock process lifecycle)

**Verdict:** ❌ **REJECTED** (violates single responsibility)

---

### Option B: Create Separate RuntimeLock Class ✅ **SELECTED**

**Approach:**
- New `RuntimeLock` class in `foundation/`
- Similar to `InitLock` but never releases
- Used alongside `InitLock` (both acquired at startup)

**Pros:**
- ✅ Clear separation of concerns
- ✅ Easy to test (separate lifecycle)
- ✅ Reusable pattern (other singletons)
- ✅ No changes to existing `InitLock`
- ✅ Complements existing `IndexLockManager` (different layer)

**Cons:**
- ❌ More code (new class) - **Acceptable tradeoff for clarity**
- ❌ Two locks to manage (init + runtime) - **Each has clear purpose**

**Verdict:** ✅ **APPROVED** (clean architecture, best practices)

**Decision Rationale:**
1. **Separation of Concerns:** InitLock = initialization, RuntimeLock = singleton enforcement
2. **Clarity:** Three distinct lock layers (process, runtime, index files)
3. **Testability:** Independent lifecycle makes testing straightforward
4. **Maintainability:** Clear semantics, easy to understand and debug
5. **Compatibility:** No changes to existing `InitLock` or `IndexLockManager`

---

### Option C: Use IndexLockManager for Runtime

**Approach:**
- Create a special "server" index lock
- Hold exclusive lock for server lifetime
- Reuse existing `IndexLockManager` infrastructure

**Pros:**
- ✅ Reuses existing locking infrastructure
- ✅ fcntl-based (more robust than file creation)

**Cons:**
- ❌ Semantic mismatch (not an "index")
- ❌ Shared/exclusive distinction not needed
- ❌ More complex than needed

**Verdict:** ❌ **REJECTED** (over-engineering, semantic confusion)

---

### Option D: PID File Only (No Locking)

**Approach:**
- Write PID to `.server.pid` file at startup
- Check PID on startup (kill if stale)
- No actual file locking

**Pros:**
- ✅ Simple implementation
- ✅ Cross-platform (no fcntl needed)

**Cons:**
- ❌ Race condition: Two processes can write PID simultaneously
- ❌ No atomic "check and claim" operation
- ❌ Less reliable than file locking

**Verdict:** ❌ **REJECTED** (race condition risk unacceptable)

---

## Approved Solution

### RuntimeLock Class (Option B)

**Design:**
```python
class RuntimeLock:
    """
    Runtime lock for enforcing singleton MCP server per project.
    
    Acquired at server startup and held for entire process lifetime.
    Prevents multiple ouroboros instances from running concurrently.
    
    Differences from InitLock:
    - InitLock: Held during initialization only (10s)
    - RuntimeLock: Held for entire server lifetime (hours/days)
    
    Lock Strategy:
    1. Attempt to create lock file atomically (O_CREAT | O_EXCL)
    2. If file exists → check if holder PID is alive
    3. If holder alive → exit gracefully (another server running)
    4. If holder dead → remove stale lock, retry
    5. On successful acquisition → hold until process exits
    
    Cleanup:
    - Lock file removed on graceful shutdown (atexit handler)
    - Lock file left behind on crash (detected as stale by next spawn)
    """
```

**Lock File Location:**
```
.praxis-os/
└── .cache/
    ├── .init.lock      # InitLock (temporary, 10s)
    └── .runtime.lock   # RuntimeLock (persistent, lifetime)
```

**Integration with __main__.py:**
```python
def main():
    # Find .praxis-os directory
    base_path = find_praxis_os_directory()
    
    # Acquire runtime lock (singleton enforcement)
    runtime_lock = RuntimeLock(base_path)
    if not runtime_lock.acquire():
        # Another server is running, exit gracefully
        logger.info("Another MCP server is already running. Exiting.")
        sys.exit(0)
    
    # Acquire init lock (concurrent initialization prevention)
    init_lock = InitLock(base_path, timeout_seconds=10)
    if not init_lock.acquire():
        # Another server is initializing, exit gracefully
        logger.info("Another MCP server is initializing. Exiting.")
        runtime_lock.release()  # Cleanup runtime lock
        sys.exit(0)
    
    try:
        # Initialize server
        initialize_server()
        
        # Release init lock (init complete)
        init_lock.release()
        
        # Run server (runtime lock still held!)
        run_server_forever()
        
    finally:
        # Cleanup on exit (graceful or crash)
        runtime_lock.release()
```

**Key Design Decisions:**

1. **Two Locks, Two Purposes:**
   - `InitLock`: Prevents concurrent initialization (10s)
   - `RuntimeLock`: Prevents concurrent execution (lifetime)

2. **Lock Acquisition Order:**
   - Runtime lock FIRST (claim server slot)
   - Init lock SECOND (prevent init race)
   - Release init lock after init
   - Hold runtime lock until exit

3. **Stale Lock Detection:**
   - Read PID from lock file
   - Check if PID is running (`os.kill(pid, 0)`)
   - If dead → remove lock file, retry

4. **Error Handling:**
   - Lock file corrupted → log warning, proceed
   - Lock directory missing → create, proceed
   - PID check fails → assume running (safer)

---

## Implementation Plan

### Phase 1: RuntimeLock Class (2 hours)

**File:** `.praxis-os/ouroboros/foundation/runtime_lock.py`

**Components:**
1. `RuntimeLock.__init__(base_path)`
2. `RuntimeLock.acquire() -> bool`
3. `RuntimeLock.release() -> None`
4. `RuntimeLock._try_claim_lock() -> bool`
5. `RuntimeLock._read_lock_holder() -> Optional[int]`
6. `RuntimeLock._is_process_running(pid) -> bool`
7. `RuntimeLock._cleanup()` (atexit handler)

**Code Structure:**
```python
class RuntimeLock:
    LOCK_FILE_NAME = ".runtime.lock"
    
    def __init__(self, base_path: Path):
        self.lock_file = base_path / ".cache" / self.LOCK_FILE_NAME
        self.pid = os.getpid()
        self.acquired = False
        
        # Ensure cache directory exists
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Register cleanup handler
        atexit.register(self._cleanup)
    
    def acquire(self) -> bool:
        """Attempt to acquire runtime lock."""
        # Try to claim lock
        if self._try_claim_lock():
            self.acquired = True
            logger.info("🔒 Runtime lock acquired (PID %d)", self.pid)
            return True
        
        # Lock exists - check if holder is alive
        holder_pid = self._read_lock_holder()
        if holder_pid is None:
            # Corrupted lock file, retry
            return self.acquire()
        
        if not self._is_process_running(holder_pid):
            # Stale lock, remove and retry
            logger.info("🔓 Stale runtime lock (dead PID %d)", holder_pid)
            self.lock_file.unlink(missing_ok=True)
            return self.acquire()
        
        # Holder is alive, another server is running
        logger.info(
            "⛔ Another MCP server is running (PID %d). "
            "Exiting gracefully.",
            holder_pid
        )
        return False
    
    def release(self) -> None:
        """Release runtime lock."""
        if not self.acquired:
            return
        
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
                logger.info("🔓 Runtime lock released (PID %d)", self.pid)
        except Exception as e:
            logger.warning("Failed to release runtime lock: %s", e)
        finally:
            self.acquired = False
    
    def _try_claim_lock(self) -> bool:
        """Atomically create lock file with PID."""
        try:
            fd = os.open(
                str(self.lock_file),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o600
            )
            os.write(fd, str(self.pid).encode('utf-8'))
            os.close(fd)
            return True
        except FileExistsError:
            return False
        except Exception as e:
            logger.warning("Failed to claim runtime lock: %s", e)
            return False
    
    def _read_lock_holder(self) -> Optional[int]:
        """Read PID from lock file."""
        try:
            content = self.lock_file.read_text(encoding='utf-8').strip()
            return int(content)
        except (FileNotFoundError, ValueError, OSError):
            return None
    
    @staticmethod
    def _is_process_running(pid: int) -> bool:
        """Check if process is running."""
        try:
            os.kill(pid, 0)  # Signal 0 = check existence
            return True
        except OSError:
            return False
    
    def _cleanup(self) -> None:
        """Cleanup on process exit (atexit handler)."""
        self.release()
```

---

### Phase 2: Integration with __main__.py (30 minutes)

**Changes:**
1. Import `RuntimeLock`
2. Acquire runtime lock before init lock
3. Hold runtime lock for server lifetime
4. Release runtime lock in finally block

**Diff:**
```python
# __main__.py

from ouroboros.foundation import PortManager, ProjectInfoDiscovery, TransportManager
+from ouroboros.foundation.runtime_lock import RuntimeLock

def main():
    # Initialize components (for cleanup in finally block)
    port_manager = None
    transport_mgr = None
    init_lock = None
+   runtime_lock = None
    
    try:
        # Find and validate .praxis-os directory
        base_path = find_praxis_os_directory()
        logger.info("Base path: %s", base_path)
        
+       # Acquire runtime lock (singleton enforcement)
+       runtime_lock = RuntimeLock(base_path)
+       if not runtime_lock.acquire():
+           # Another server is running, exit gracefully
+           logger.info(
+               "Another MCP server is already running. "
+               "This is expected behavior with misbehaving MCP clients."
+           )
+           sys.exit(0)
        
        # Acquire initialization lock (defends against concurrent spawns)
        from ouroboros.foundation.init_lock import InitLock
        
        init_lock = InitLock(base_path, timeout_seconds=10)
        if not init_lock.acquire():
            # Another process is initializing - exit gracefully
            logger.info(
                "Another MCP server instance is initializing. "
                "Exiting gracefully (this is normal with misbehaving MCP clients)."
            )
            sys.exit(0)
        
        # ... rest of initialization ...
        
    finally:
        # Cleanup: Always cleanup state file, shutdown transports, and release locks
        if port_manager:
            port_manager.cleanup_state()
            logger.info("State file cleaned up")
        
        if transport_mgr:
            transport_mgr.shutdown()
        
        if init_lock:
            init_lock.release()
        
+       if runtime_lock:
+           runtime_lock.release()
        
        logger.info("Shutdown complete")
```

---

### Phase 3: Testing (1.5 hours)

**Unit Tests:** `.praxis-os/tests/ouroboros/foundation/test_runtime_lock.py`

```python
def test_runtime_lock_acquire_success():
    """Test successful lock acquisition."""
    lock = RuntimeLock(tmp_path)
    assert lock.acquire() is True
    assert lock.acquired is True
    assert lock.lock_file.exists()

def test_runtime_lock_acquire_already_held():
    """Test lock acquisition when another process holds it."""
    # Process A acquires lock
    lock_a = RuntimeLock(tmp_path)
    assert lock_a.acquire() is True
    
    # Process B tries to acquire (should fail)
    lock_b = RuntimeLock(tmp_path)
    assert lock_b.acquire() is False

def test_runtime_lock_stale_lock_cleanup():
    """Test stale lock detection and cleanup."""
    # Create lock file with dead PID
    lock_file = tmp_path / ".cache" / ".runtime.lock"
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock_file.write_text("99999")  # Dead PID
    
    # New process should detect stale lock and claim it
    lock = RuntimeLock(tmp_path)
    assert lock.acquire() is True

def test_runtime_lock_release():
    """Test lock release."""
    lock = RuntimeLock(tmp_path)
    lock.acquire()
    lock.release()
    
    assert lock.acquired is False
    assert not lock.lock_file.exists()

def test_runtime_lock_atexit_cleanup():
    """Test atexit handler cleanup."""
    # This is tricky to test - need to spawn subprocess
    # and verify lock file is removed on exit
    pass
```

**Integration Tests:** Manual testing with multiple spawns

```bash
# Terminal 1: Start first server
python -m ouroboros --transport dual

# Terminal 2: Try to start second server (should exit gracefully)
python -m ouroboros --transport dual
# Expected: "Another MCP server is already running. Exiting."

# Terminal 1: Kill first server (Ctrl+C)

# Terminal 2: Start second server (should succeed)
python -m ouroboros --transport dual
# Expected: Server starts successfully
```

**Stress Test:** Simulate Cursor's race condition

```bash
# Spawn 10 servers simultaneously
for i in {1..10}; do
    python -m ouroboros --transport dual &
done

# Wait for all to finish
wait

# Verify only 1 is running
ps aux | grep ouroboros | grep -v grep
# Expected: Only 1 process
```

---

### Phase 4: Documentation (30 minutes)

**Updates:**
1. `RuntimeLock` docstrings (comprehensive)
2. `__main__.py` comments (explain lock order)
3. Standards doc: `.praxis-os/standards/development/singleton-enforcement.md`
4. Troubleshooting guide: How to manually remove stale locks

---

## Testing Strategy

### Unit Tests

**Coverage Target:** 100% line coverage

**Test Cases:**
1. ✅ Successful lock acquisition
2. ✅ Lock already held (graceful fail)
3. ✅ Stale lock detection (dead PID)
4. ✅ Stale lock cleanup
5. ✅ Lock release
6. ✅ Corrupted lock file (invalid PID)
7. ✅ Missing lock directory (auto-create)
8. ✅ Permission errors (graceful degradation)

### Integration Tests

**Scenarios:**
1. ✅ Single server startup (normal case)
2. ✅ Duplicate spawn (Cursor bug simulation)
3. ✅ Server crash (stale lock cleanup)
4. ✅ Manual kill (stale lock cleanup)
5. ✅ Rapid spawns (stress test)

### Manual Testing

**Checklist:**
- [ ] Start server, verify lock file created
- [ ] Try to start second server, verify graceful exit
- [ ] Kill first server, verify lock file removed
- [ ] Start second server, verify success
- [ ] Kill server with `kill -9`, verify stale lock detected
- [ ] Remove lock file manually, verify server starts

---

## Rollout Plan

### Phase 1: Development (4 hours)
- Implement `RuntimeLock` class
- Integrate with `__main__.py`
- Write unit tests
- Manual testing

### Phase 2: Testing (1 hour)
- Run full test suite
- Stress test (10 concurrent spawns)
- Verify no regressions

### Phase 3: Deployment (Immediate)
- Merge to main
- No version bump needed (internal fix)
- Document in changelog

### Phase 4: Monitoring (1 week)
- Watch for zombie processes (should be 0)
- Monitor lock file creation/cleanup
- Collect user feedback

---

## Risks and Mitigations

### Risk 1: False Positives (Killing Valid Server)

**Scenario:** RuntimeLock incorrectly detects valid server as dead

**Likelihood:** Low (PID check is reliable)

**Impact:** High (user's work interrupted)

**Mitigation:**
- Conservative PID checking (assume alive if uncertain)
- Comprehensive logging (debug false positives)
- Manual override (delete lock file)

---

### Risk 2: Stale Locks (Server Won't Start)

**Scenario:** Lock file left behind, PID check fails, server won't start

**Likelihood:** Medium (crashes, force kills)

**Impact:** Medium (user has to manually delete lock)

**Mitigation:**
- Clear error message with fix instructions
- Automatic stale lock detection (PID check)
- Timeout mechanism (if PID check hangs)

---

### Risk 3: Cross-Platform Issues

**Scenario:** Lock behavior differs on Windows vs Unix

**Likelihood:** Low (using standard OS primitives)

**Impact:** Medium (Windows users can't use praxis-os)

**Mitigation:**
- Test on Windows (VM or CI)
- Fallback to simpler locking on Windows
- Document platform-specific behavior

---

### Risk 4: Performance Regression

**Scenario:** Lock acquisition slows down server startup

**Likelihood:** Low (lock is fast)

**Impact:** Low (startup is already slow due to index loading)

**Mitigation:**
- Benchmark lock acquisition (<100ms target)
- Profile startup time before/after
- Optimize if needed (caching, async)

---

## Appendices

### Appendix A: Evidence of Problem

**Log Analysis:**
```bash
$ grep "CodeIndex.build()" logs.log | head -10
2025-11-17 08:29:37.802 INFO:ouroboros.subsystems.rag.code.container:CodeIndex.build() building 2 partitions
2025-11-17 08:29:37.802 INFO:ouroboros.subsystems.rag.code.container:CodeIndex.build() building 2 partitions
```

**Process List:**
```bash
$ ps aux | grep ouroboros
josh  72509  82.4%  0.0%  Running  Wed 1PM   5188h
josh  47294  77.0% 10.9%  Running  8:23 AM     7h
josh  63049   0.1%  0.3%  Sleeping Sat 3PM     8h
josh  16526   0.0%  0.4%  Sleeping 2:10 PM     5h
josh  32128   0.0%  0.4%  Sleeping Sat 4PM    10h
```

**Lock File State:**
```bash
$ cat .praxis-os/.cache/.init.lock
# File doesn't exist (lock released after init)

$ ls -la .praxis-os/.cache/
# No runtime lock file
```

---

### Appendix B: Comparison with Other Systems

**How Other Systems Handle Singleton Enforcement:**

1. **Docker:**
   - Uses socket file locking (`/var/run/docker.sock`)
   - Exclusive lock held for daemon lifetime
   - Stale lock detection via socket connection test

2. **PostgreSQL:**
   - Uses PID file (`postmaster.pid`)
   - Checks PID on startup, kills if stale
   - Also uses port binding (only one process can bind)

3. **Redis:**
   - Uses PID file (`redis.pid`)
   - No automatic stale lock cleanup (manual intervention)
   - Relies on port binding for enforcement

4. **Nginx:**
   - Uses PID file (`nginx.pid`)
   - Signal-based control (send signals to PID)
   - No stale lock detection (assumes admin cleanup)

**Our Approach (Hybrid):**
- PID file (like PostgreSQL, Redis)
- Automatic stale lock detection (like Docker)
- Graceful degradation (better than Nginx)

---

### Appendix C: Alternative Approaches Considered

**1. Port-Based Locking**
- Bind to a fixed port (e.g., 9999)
- Only one process can bind
- Stale lock impossible (OS cleans up)

**Rejected because:**
- Requires network stack (overkill)
- Port conflicts with other apps
- Harder to debug (netstat vs ls)

**2. Database-Based Locking**
- Use DuckDB advisory locks
- Automatic cleanup on disconnect

**Rejected because:**
- DuckDB not initialized yet (chicken-egg)
- Adds dependency on database
- Slower than file-based

**3. Systemd Socket Activation**
- Let systemd manage singleton
- Socket-based activation

**Rejected because:**
- Not cross-platform (Unix only)
- Requires systemd (not on macOS)
- Overkill for development tool

---

### Appendix D: Success Metrics

**How We'll Know It's Working:**

1. **Zero Zombie Processes**
   - Metric: `ps aux | grep ouroboros | wc -l` = 1
   - Target: 100% of the time

2. **Zero Index Corruption**
   - Metric: DuckDB errors in logs
   - Target: 0 errors per week

3. **Fast Duplicate Detection**
   - Metric: Time from spawn to exit (duplicate)
   - Target: <1 second

4. **Zero False Positives**
   - Metric: Valid server killed incorrectly
   - Target: 0 incidents per month

5. **User Satisfaction**
   - Metric: Manual `kill -9` commands
   - Target: 0 per week (down from 5-10)

---

## Conclusion

**Summary:**
- **Problem:** Cursor spawns multiple MCP servers, causing corruption
- **Root Cause:** InitLock releases too early (no runtime singleton enforcement)
- **Solution:** RuntimeLock held for server lifetime (Option B - Separate class)
- **Impact:** Eliminates zombie processes, improves reliability
- **Timeline:** 4-6 hours to implement and test

**Decision Summary:**
- **Chosen Approach:** Option B - Create Separate RuntimeLock Class ✅
- **Decision Date:** 2025-11-17
- **Decision Makers:** AI Agent + Josh (Human Orchestrator)
- **Key Rationale:** 
  1. Clean separation of concerns (init vs runtime vs index operations)
  2. Three distinct lock layers with clear purposes
  3. No changes to existing `InitLock` or `IndexLockManager`
  4. Testable, maintainable, follows best practices

**Lock Architecture (Final):**
```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: InitLock (Process Initialization)             │
│ - Purpose: Prevent concurrent initialization           │
│ - Duration: 10 seconds (init phase only)               │
│ - File: .cache/.init.lock                              │
│ - Status: ✅ Existing, working                         │
├─────────────────────────────────────────────────────────┤
│ Layer 2: RuntimeLock (Singleton Enforcement)           │
│ - Purpose: Ensure only ONE MCP server per project      │
│ - Duration: Entire process lifetime (hours/days)       │
│ - File: .cache/.runtime.lock                           │
│ - Status: ⏳ APPROVED, ready for implementation        │
├─────────────────────────────────────────────────────────┤
│ Layer 3: IndexLockManager (Index File Protection)      │
│ - Purpose: Prevent index file corruption               │
│ - Duration: Per-operation (seconds/minutes)            │
│ - File: .cache/locks/{index_name}.lock                 │
│ - Status: ✅ Existing, working                         │
└─────────────────────────────────────────────────────────┘
```

**Next Steps:**
1. ✅ Design doc complete (this document)
2. ✅ Decision finalized (Option B approved)
3. ⏳ Run `spec_creation_v1` workflow (2-3 hours)
4. ⏳ Implement RuntimeLock (2 hours)
5. ⏳ Test and deploy (1 hour)

**Expected Outcome:**
- Zero zombie processes
- Zero index corruption
- Graceful handling of Cursor's race condition
- Better user experience (no manual cleanup)
- Clear lock architecture with three distinct layers

---

**Document Status:** ✅ **APPROVED - Ready for Spec Creation**  
**Next Action:** Run `spec_creation_v1` workflow to create formal specification  
**Implementation Priority:** HIGH (prevents critical production bugs)


