# Implementation Guidance

**Project:** RuntimeLock - Singleton MCP Server Enforcement  
**Date:** 2025-11-17  
**Based on:** srd.md (requirements) + specs.md (design) + tasks.md (breakdown)

---

## 1. Code Patterns

### 1.1 Atomic File Creation Pattern with Security Hardening

**Pattern:** Use `os.open()` with `O_CREAT | O_EXCL` for atomic "check and claim" operations, with write verification and error cleanup.

**Example:**
```python
import time
import shutil

def _try_claim_lock(self) -> bool:
    """Atomically create lock file with PID and timestamp."""
    try:
        fd = os.open(
            str(self.lock_file),
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600
        )
        
        # Write PID + timestamp (for PID reuse mitigation)
        content = f"{self.pid} {int(time.time())}"
        pid_bytes = content.encode('utf-8')
        bytes_written = os.write(fd, pid_bytes)
        os.close(fd)
        
        # ✅ VERIFY WRITE SUCCEEDED (detects disk full)
        if bytes_written != len(pid_bytes):
            logger.error("Failed to write PID to lock file (disk full?)")
            self.lock_file.unlink(missing_ok=True)  # Cleanup
            return False
        
        return True
        
    except FileExistsError:
        return False
        
    except IsADirectoryError:
        # ✅ HANDLE DIRECTORY DOS ATTACK
        logger.error("Directory exists at lock path: %s (removing)", self.lock_file)
        shutil.rmtree(self.lock_file)
        return False
        
    except Exception as e:
        logger.warning("Failed to claim runtime lock: %s", e)
        # ✅ CLEANUP PARTIAL FILE
        self.lock_file.unlink(missing_ok=True)
        return False
```

**Why:** 
- `O_CREAT | O_EXCL` provides atomicity
- Timestamp enables PID reuse detection
- Write verification prevents disk-full corruption
- Directory handling prevents DoS attacks
- Cleanup ensures no partial files remain

**Anti-Pattern:** ❌ Don't use `Path.exists()` + `Path.write_text()` (race condition between check and write)

---

### 1.2 Process Name Verification Pattern (PID Reuse Mitigation)

**Pattern:** Verify PID is actually ouroboros by checking process command line. Use stdlib only (`/proc` or `ps`).

**Example:**
```python
import time
import subprocess

@staticmethod
def _get_process_cmdline(pid: int) -> Optional[str]:
    """Get process command line using stdlib only."""
    # Try /proc first (Linux, WSL2) - instant
    try:
        with open(f"/proc/{pid}/cmdline", 'rb') as f:
            cmdline = f.read().decode('utf-8', errors='ignore')
            return cmdline.replace('\x00', ' ').strip()
    except (FileNotFoundError, PermissionError, OSError):
        pass
    
    # Fall back to ps command (macOS, Unix) - ~50ms
    try:
        result = subprocess.run(
            ['ps', '-p', str(pid), '-o', 'command='],
            capture_output=True,
            text=True,
            timeout=0.5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    
    return None

@staticmethod
def _is_process_running(pid: int) -> bool:
    """Check if process is running AND is ouroboros."""
    try:
        os.kill(pid, 0)  # Check if PID exists
        
        # ✅ VERIFY IT'S ACTUALLY OUROBOROS (PID reuse detection)
        cmdline = _get_process_cmdline(pid)
        
        if cmdline is None:
            # Can't verify (permission denied, etc.)
            # Conservative: assume valid (NFR-R1: Zero False Positives)
            logger.debug("Cannot verify process name for PID %d (assuming valid)", pid)
            return True
        
        # Check if it's ouroboros
        if 'ouroboros' in cmdline.lower():
            return True  # It's our server!
        
        # ✅ PID EXISTS BUT IS NOT OUROBOROS → PID REUSE DETECTED!
        logger.warning(
            "PID %d exists but is not ouroboros (cmd='%s') - PID reused",
            pid, cmdline[:100]  # Truncate for logging
        )
        return False
        
    except OSError:
        return False  # PID doesn't exist

def acquire(self, _retry_count: int = 0) -> bool:
    """Attempt to acquire runtime lock with retry limit."""
    # ✅ PREVENT INFINITE LOOP
    if _retry_count >= 3:
        logger.error("Failed to acquire lock after 3 retries")
        return False
    
    if self._try_claim_lock():
        self.acquired = True
        logger.info("🔒 Runtime lock acquired (PID %d)", self.pid)
        return True
    
    # Read PID + timestamp
    holder_info = self._read_lock_holder()
    if holder_info is None:
        self.lock_file.unlink(missing_ok=True)
        logger.debug("Retrying lock acquisition (attempt %d/3)", _retry_count + 1)
        return self.acquire(_retry_count + 1)
    
    holder_pid, holder_timestamp = holder_info
    
    # ✅ TIMESTAMP VALIDATION (belt-and-suspenders)
    age_hours = (time.time() - holder_timestamp) / 3600
    if age_hours > 24:
        logger.warning("Lock is %d hours old (PID %d), assuming stale", int(age_hours), holder_pid)
        self.lock_file.unlink(missing_ok=True)
        return self.acquire(_retry_count + 1)
    
    # ✅ PROCESS NAME VERIFICATION (primary PID reuse defense)
    if not self._is_process_running(holder_pid):
        # Either dead OR not ouroboros (PID reused)
        logger.info("Stale runtime lock (PID %d)", holder_pid)
        self.lock_file.unlink(missing_ok=True)
        return self.acquire(_retry_count + 1)
    
    # Another ouroboros server is running
    logger.info("Another MCP server is running (PID %d). Exiting.", holder_pid)
    return False
```

**Why:** 
- **Process name verification** detects PID reuse **immediately** (not after 24 hours)
- Works on all supported platforms (Linux, macOS, WSL2) using stdlib only
- Timestamp provides secondary defense (belt-and-suspenders)
- Conservative fallback (if can't verify, assume valid) prevents false positives
- Retry limit prevents infinite loops

**Anti-Pattern:** ❌ Don't rely solely on timestamp - PID reuse can happen in minutes on busy systems.

---

### 1.3 Graceful Error Handling Pattern

**Pattern:** Handle all exceptions gracefully, log warnings, never crash.

**Example:**
```python
def _read_lock_holder(self) -> Optional[int]:
    """Read PID from lock file."""
    try:
        content = self.lock_file.read_text(encoding='utf-8').strip()
        return int(content)
    except (FileNotFoundError, ValueError, OSError):
        return None  # Graceful degradation
```

**Why:** Lock operations should never crash the server. Return safe defaults (None, False) on errors.

**Anti-Pattern:** ❌ Don't let exceptions propagate to caller - handle internally.

---

### 1.4 Idempotent Release Pattern

**Pattern:** Make `release()` safe to call multiple times.

**Example:**
```python
def release(self) -> None:
    """Release runtime lock."""
    if not self.acquired:
        return  # Already released
    
    try:
        if self.lock_file.exists():
            self.lock_file.unlink()
            logger.info("🔓 Runtime lock released (PID %d)", self.pid)
    except Exception as e:
        logger.warning("Failed to release runtime lock: %s", e)
    finally:
        self.acquired = False  # Always clear flag
```

**Why:** `release()` may be called from multiple places (finally block, atexit handler). Idempotency prevents errors.

**Anti-Pattern:** ❌ Don't raise exceptions in `release()` - it's called during cleanup.

---

### 1.5 Atexit Handler Pattern

**Pattern:** Register cleanup handler in `__init__()` to ensure lock is released on exit.

**Example:**
```python
def __init__(self, base_path: Path):
    # ... initialization ...
    atexit.register(self._cleanup)

def _cleanup(self) -> None:
    """Cleanup on process exit (atexit handler)."""
    self.release()
```

**Why:** Ensures lock is released even if `release()` is not called explicitly (e.g., KeyboardInterrupt).

**Anti-Pattern:** ❌ Don't rely solely on finally blocks - they don't catch all exit scenarios.

---

## 2. Testing Summary

**Full testing documentation:** See `testing/` subdirectory for comprehensive test plans.

### 2.1 Test Coverage

- **Unit Tests:** 14+ tests covering all RuntimeLock methods
- **Integration Tests:** 4+ tests covering multi-process scenarios
- **Stress Tests:** 2+ tests simulating Cursor's race condition
- **Performance Benchmarks:** 3 benchmarks validating NFR-P1 and NFR-P2
- **Cross-Platform Tests:** Validation on macOS, Linux, Windows

**Target:** 100% line coverage for RuntimeLock class (NFR-M3)

### 2.2 Key Test Cases

1. **test_acquire_success()**: Normal lock acquisition
2. **test_acquire_already_held()**: Duplicate spawn detection
3. **test_acquire_stale_lock()**: Stale lock cleanup
4. **test_stress_concurrent_spawns()**: 10 simultaneous spawns → only 1 runs

### 2.3 Testing Strategy

- **Unit Tests:** Fast, isolated, mock file system when needed
- **Integration Tests:** Real file system, subprocess spawns
- **Stress Tests:** Concurrent execution, verify no race conditions
- **Benchmarks:** Measure latency, verify performance targets

**See:** `testing/test-strategy.md` for complete testing approach.

---

## 3. Deployment

### 3.1 Deployment Steps

**Step 1: Verify Prerequisites**
- [ ] Python 3.10+ installed
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Code coverage: 100% for RuntimeLock

**Step 2: Deploy Code**
```bash
# 1. Copy runtime_lock.py to foundation/
cp runtime_lock.py .praxis-os/ouroboros/foundation/

# 2. Update __main__.py with integration code
# (See specs.md Section 2.2 for exact changes)

# 3. Verify imports
python -c "from ouroboros.foundation.runtime_lock import RuntimeLock"
```

**Step 3: Test Deployment**
```bash
# 1. Start first server
python -m ouroboros --transport dual

# 2. In another terminal, try to start second server
python -m ouroboros --transport dual
# Expected: "Another MCP server is already running. Exiting."

# 3. Kill first server, verify lock file removed
ls .praxis-os/.cache/.runtime.lock  # Should not exist
```

**Step 4: Monitor**
- Check logs for "Runtime lock acquired" messages
- Verify no zombie processes (`ps aux | grep ouroboros`)
- Monitor CPU/memory usage (should be normal)

---

### 3.2 Rollback Plan

**If issues occur:**

**Step 1: Revert __main__.py Changes**
```bash
git revert <commit-hash>  # Revert integration commit
```

**Step 2: Remove RuntimeLock File**
```bash
rm .praxis-os/ouroboros/foundation/runtime_lock.py
```

**Step 3: Clean Up Lock Files**
```bash
rm .praxis-os/.cache/.runtime.lock
```

**Step 4: Restart Server**
```bash
python -m ouroboros --transport dual
```

**Verification:**
- Server starts normally
- No errors in logs
- Existing functionality works

---

### 3.3 Monitoring

**Key Metrics:**
- **Zombie Process Count:** `ps aux | grep ouroboros | wc -l` (should be 1)
- **Lock File Age:** `ls -l .praxis-os/.cache/.runtime.lock` (should match server uptime)
- **Duplicate Spawn Logs:** `grep "Another MCP server is running" logs/` (frequency indicates Cursor bug occurrence)

**Alerts:**
- Alert if zombie process count > 1 (indicates RuntimeLock failure)
- Alert if lock file age > 7 days (potential stale lock)

---

## 4. Troubleshooting

### 4.1 Common Issues

#### Issue 1: "Another MCP server is already running" but no server visible

**Symptoms:**
- New server won't start
- `ps aux | grep ouroboros` shows no processes
- Lock file exists: `.praxis-os/.cache/.runtime.lock`

**Cause:** Stale lock file from crashed server

**Solution:**
```bash
# 1. Verify no server is running
ps aux | grep ouroboros

# 2. Check lock file
cat .praxis-os/.cache/.runtime.lock  # Shows PID

# 3. Verify PID is dead
ps -p <PID>  # Should show "no such process"

# 4. Manually remove stale lock
rm .praxis-os/.cache/.runtime.lock

# 5. Restart server
python -m ouroboros --transport dual
```

**Prevention:** RuntimeLock should detect and clean up stale locks automatically. If this happens frequently, file a bug report.

---

#### Issue 2: Multiple servers running despite RuntimeLock

**Symptoms:**
- `ps aux | grep ouroboros` shows 2+ processes
- High CPU usage (>100%)
- Duplicate log entries

**Cause:** RuntimeLock not integrated or disabled

**Solution:**
```bash
# 1. Verify RuntimeLock is integrated
grep "RuntimeLock" .praxis-os/ouroboros/__main__.py

# 2. Check logs for "Runtime lock acquired"
grep "Runtime lock acquired" .cache/logs/*.log

# 3. If missing, RuntimeLock is not active
# Manually kill zombie processes
pkill -f "python -m ouroboros"

# 4. Restart with RuntimeLock enabled
python -m ouroboros --transport dual
```

**Prevention:** Ensure `__main__.py` integration is complete (see specs.md Section 2.2).

---

#### Issue 3: Server won't start on Windows

**Symptoms:**
- Server crashes on startup
- Error: "os.kill(pid, 0) not supported on Windows"

**Cause:** `os.kill(pid, 0)` behaves differently on Windows

**Solution:**
```python
# Update _is_process_running() for Windows:
@staticmethod
def _is_process_running(pid: int) -> bool:
    """Check if process is running (cross-platform)."""
    if os.name == 'nt':  # Windows
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(1, 0, pid)
        if handle == 0:
            return False
        kernel32.CloseHandle(handle)
        return True
    else:  # Unix/Linux/macOS
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
```

**Prevention:** Test on Windows before deployment (see tasks.md Task 3.5).

---

#### Issue 4: Lock file permissions error

**Symptoms:**
- Error: "Permission denied: '.praxis-os/.cache/.runtime.lock'"
- Server won't start

**Cause:** Lock file owned by different user or incorrect permissions

**Solution:**
```bash
# 1. Check lock file ownership
ls -l .praxis-os/.cache/.runtime.lock

# 2. If owned by different user, remove it
sudo rm .praxis-os/.cache/.runtime.lock

# 3. Restart server (will create new lock with correct ownership)
python -m ouroboros --transport dual
```

**Prevention:** Don't run server as different users (e.g., root vs normal user).

---

### 4.2 Debugging Tips

**Enable DEBUG Logging:**
```bash
# In .praxis-os/config/mcp.yaml
logging:
  level: "DEBUG"
```

**Check Lock File State:**
```bash
# Lock file exists?
ls -l .praxis-os/.cache/.runtime.lock

# Lock file content (PID)?
cat .praxis-os/.cache/.runtime.lock

# Is PID alive?
ps -p $(cat .praxis-os/.cache/.runtime.lock)
```

**Trace Lock Operations:**
```bash
# Grep logs for lock operations
grep -E "Runtime lock|acquire|release" .cache/logs/*.log
```

**Test Lock Manually:**
```python
from pathlib import Path
from ouroboros.foundation.runtime_lock import RuntimeLock

lock = RuntimeLock(Path(".praxis-os"))
print(f"Acquire: {lock.acquire()}")  # Should be True
print(f"Lock file exists: {lock.lock_file.exists()}")  # Should be True
print(f"PID: {lock.lock_file.read_text()}")  # Should match os.getpid()
lock.release()
print(f"Lock file exists: {lock.lock_file.exists()}")  # Should be False
```

---

### 4.3 Performance Debugging

**Measure Lock Acquisition Time:**
```python
import time
from ouroboros.foundation.runtime_lock import RuntimeLock

lock = RuntimeLock(Path(".praxis-os"))
start = time.time()
lock.acquire()
end = time.time()
print(f"Lock acquisition time: {(end - start) * 1000:.2f}ms")  # Should be <100ms
lock.release()
```

**Stress Test:**
```bash
# Spawn 10 servers simultaneously
for i in {1..10}; do
    python -m ouroboros --transport dual &
done

# Wait for all to finish
wait

# Verify only 1 is running
ps aux | grep ouroboros | grep -v grep | wc -l  # Should be 1
```

---

## 5. Code Examples

### 5.1 Complete RuntimeLock Implementation

**See:** Design doc (`supporting-docs/design-doc-runtime-lock.md`) Section "Implementation Plan" for complete code examples.

**Key Files:**
- `.praxis-os/ouroboros/foundation/runtime_lock.py` (new file, ~180 LOC)
- `.praxis-os/ouroboros/__main__.py` (modifications, ~20 LOC added)

### 5.2 Integration Example

**Before (without RuntimeLock):**
```python
def main():
    init_lock = None
    try:
        base_path = find_praxis_os_directory()
        
        init_lock = InitLock(base_path, timeout_seconds=10)
        if not init_lock.acquire():
            sys.exit(0)
        
        initialize_server()
        run_server_forever()
        
    finally:
        if init_lock:
            init_lock.release()
```

**After (with RuntimeLock):**
```python
def main():
    runtime_lock = None
    init_lock = None
    try:
        base_path = find_praxis_os_directory()
        
        # ✅ NEW: Acquire runtime lock first
        runtime_lock = RuntimeLock(base_path)
        if not runtime_lock.acquire():
            logger.info("Another MCP server is already running.")
            sys.exit(0)
        
        init_lock = InitLock(base_path, timeout_seconds=10)
        if not init_lock.acquire():
            sys.exit(0)
        
        initialize_server()
        run_server_forever()
        
    finally:
        if init_lock:
            init_lock.release()
        
        # ✅ NEW: Release runtime lock
        if runtime_lock:
            runtime_lock.release()
```

---

## 6. References

- **Requirements:** `srd.md` (all FRs and NFRs)
- **Design:** `specs.md` (architecture, components, APIs)
- **Tasks:** `tasks.md` (implementation breakdown)
- **Testing:** `testing/` directory (comprehensive test plans)
- **Design Doc:** `supporting-docs/design-doc-runtime-lock.md` (original design)

---


