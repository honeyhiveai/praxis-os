# Technical Specifications

**Project:** RuntimeLock - Singleton MCP Server Enforcement  
**Date:** 2025-11-17  
**Based on:** srd.md (requirements)

---

## 1. Architecture Overview

### 1.1 Architectural Pattern

**Pattern:** Layered Foundation Architecture (Single Responsibility)

The RuntimeLock is designed as a foundational component in the praxis-os architecture, following a three-layer lock hierarchy:

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: InitLock (Process Initialization)             │
│ - Purpose: Prevent concurrent initialization           │
│ - Duration: 10 seconds (init phase only)               │
│ - File: .cache/.init.lock                              │
│ - Status: ✅ Existing, working                         │
├─────────────────────────────────────────────────────────┤
│ Layer 2: RuntimeLock (Singleton Enforcement) ← NEW     │
│ - Purpose: Ensure only ONE MCP server per project      │
│ - Duration: Entire process lifetime (hours/days)       │
│ - File: .cache/.runtime.lock                           │
│ - Status: ⏳ To be implemented                         │
├─────────────────────────────────────────────────────────┤
│ Layer 3: IndexLockManager (Index File Protection)      │
│ - Purpose: Prevent index file corruption               │
│ - Duration: Per-operation (seconds/minutes)            │
│ - File: .cache/locks/{index_name}.lock                 │
│ - Status: ✅ Existing, working                         │
└─────────────────────────────────────────────────────────┘
```

**Rationale:**
- **Separation of Concerns:** Each lock layer has a distinct purpose and lifecycle
- **Single Responsibility:** RuntimeLock focuses solely on singleton enforcement
- **Minimal Coupling:** No dependencies between lock layers
- **Drop-In Addition:** No changes to existing InitLock or IndexLockManager

---

### 1.2 Architectural Decisions

#### Decision 1: Separate RuntimeLock Class (Option B)

**Decision:** Create a new `RuntimeLock` class in `foundation/` that is separate from `InitLock` and held for the entire server lifetime.

**Rationale:**
- **FR-001 (Singleton Enforcement):** Requires lock held for entire process lifetime, not just initialization
- **FR-008 (Integration):** Must not modify existing InitLock or IndexLockManager
- **NFR-C1 (No Breaking Changes):** Drop-in addition to `__main__.py`
- **NFR-M1 (Code Quality):** Clear semantics, easy to understand and test

**Alternatives Considered:**
- **Option A (Extend InitLock):** Rejected - conflates init and runtime concerns, harder to test
- **Option C (Use IndexLockManager):** Rejected - semantic mismatch (not an "index"), over-engineering
- **Option D (PID File Only):** Rejected - race condition risk (no atomic "check and claim")

**Trade-offs:**
- **Pros:** 
  - Clear separation of concerns (init vs runtime vs index operations)
  - Easy to test (independent lifecycle)
  - Reusable pattern (other singletons)
  - No changes to existing code
- **Cons:** 
  - More code (new class) - acceptable tradeoff for clarity
  - Two locks to manage (init + runtime) - each has clear purpose

---

#### Decision 2: File-Based Locking with Atomic Creation

**Decision:** Use atomic file creation (O_CREAT | O_EXCL) for lock acquisition, with PID-based stale lock detection.

**Rationale:**
- **FR-001 (Singleton Enforcement):** Atomic file creation provides race-free "check and claim" operation
- **FR-002 (Stale Lock Detection):** PID stored in file enables dead process detection
- **FR-004 (Cross-Platform):** Works on Unix, Linux, macOS, Windows (standard OS primitives)
- **NFR-R1 (Zero False Positives):** Conservative PID checking (assume alive if uncertain)

**Alternatives Considered:**
- **Port-Based Locking:** Rejected - requires network stack, port conflicts, harder to debug
- **Database-Based Locking:** Rejected - DuckDB not initialized yet (chicken-egg problem)
- **fcntl-Based Locking:** Rejected - not needed (atomic file creation is sufficient)

**Trade-offs:**
- **Pros:**
  - Simple, reliable, cross-platform
  - Atomic operation (no race conditions)
  - Easy to debug (ls, cat lock file)
- **Cons:**
  - Requires file system (not a concern for development tool)
  - Stale locks possible on crash (mitigated by PID checking)

---

#### Decision 3: Lock Acquisition Order (Runtime → Init)

**Decision:** Acquire RuntimeLock BEFORE InitLock in `__main__.py`.

**Rationale:**
- **FR-005 (Lock Lifecycle):** RuntimeLock claims the "server slot" before initialization begins
- **FR-001 (Singleton Enforcement):** Prevents duplicate servers from even starting initialization
- **NFR-P2 (Duplicate Spawn Detection):** Fast-fail (<1 second) before expensive init

**Lock Acquisition Sequence:**
```
1. RuntimeLock.acquire()  ← Claim server slot
   ↓ (if fails, exit immediately)
2. InitLock.acquire()     ← Prevent concurrent init
   ↓ (if fails, release RuntimeLock, exit)
3. initialize_server()    ← Safe to initialize
4. InitLock.release()     ← Init complete
5. run_server_forever()   ← RuntimeLock still held!
6. RuntimeLock.release()  ← On shutdown (finally block + atexit)
```

**Trade-offs:**
- **Pros:**
  - Fast-fail (no wasted initialization)
  - Clear semantics (runtime → init → run)
- **Cons:**
  - Two lock acquisitions (acceptable overhead: <100ms total)

---

### 1.3 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| FR-001 | RuntimeLock class | Singleton enforcement via lifetime lock |
| FR-002 | PID checking logic | Stale lock detection via `os.kill(pid, 0)` |
| FR-003 | Graceful error handling | Try/except blocks, conservative defaults |
| FR-004 | Platform-specific primitives | `os.open()` with O_CREAT \| O_EXCL |
| FR-005 | Lock lifecycle management | Acquire in `__main__.py`, release in finally + atexit |
| FR-006 | Logging throughout | INFO-level logs for all lock operations |
| FR-007 | `.cache/.runtime.lock` | Standardized lock file location |
| FR-008 | Separate class | No changes to InitLock or IndexLockManager |
| NFR-R1 | Conservative PID checking | Assume alive if uncertain |
| NFR-P1 | Atomic file creation | <100ms lock acquisition |
| NFR-M1 | <200 LOC | Simple, focused class |
| NFR-C1 | Drop-in addition | Only modify `__main__.py` (import + acquire) |

---

### 1.4 Technology Stack

**Language:** Python 3.10+  
**Core Dependencies:** 
- `os` (atomic file operations, PID checking)
- `pathlib` (path handling)
- `atexit` (cleanup on exit)
- `logging` (observability)

**No External Dependencies:** Uses only Python standard library

**File System Requirements:**
- Atomic file creation support (O_CREAT | O_EXCL)
- PID checking support (`os.kill(pid, 0)` or equivalent)

**Platform Support:**
- ✅ macOS (primary development platform)
- ✅ Linux (production, CI/CD)
- ✅ Windows via WSL2 (Linux compatibility layer)
- ❌ Native Windows (not supported - use WSL2)

**Known Limitations:**
- **NFS:** Atomic file creation (`O_CREAT | O_EXCL`) may not be reliable on NFS-mounted directories. Use local filesystem for `.praxis-os/` directory.

---

### 1.5 Deployment Architecture

**Deployment Model:** Single-machine, multi-process

```
┌─────────────────────────────────────────────────────┐
│ User's Machine (macOS/Linux/Windows)               │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Cursor IDE (MCP Client)                     │   │
│  │                                             │   │
│  │  [Spawns]  [Spawns]  [Spawns]  [Spawns]    │   │
│  │     ↓         ↓         ↓         ↓         │   │
│  └─────┼─────────┼─────────┼─────────┼─────────┘   │
│        │         │         │         │             │
│        ↓         ↓         ↓         ↓             │
│   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │
│   │Server 1│ │Server 2│ │Server 3│ │Server 4│    │
│   │(PID A) │ │(PID B) │ │(PID C) │ │(PID D) │    │
│   └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘    │
│        │          │          │          │         │
│        ↓          ↓          ↓          ↓         │
│   ┌──────────────────────────────────────────┐    │
│   │ RuntimeLock (.cache/.runtime.lock)       │    │
│   │                                          │    │
│   │  Server 1: ✅ Acquires lock (PID A)     │    │
│   │  Server 2: ❌ Detects PID A, exits      │    │
│   │  Server 3: ❌ Detects PID A, exits      │    │
│   │  Server 4: ❌ Detects PID A, exits      │    │
│   └──────────────────────────────────────────┘    │
│                                                     │
│  Result: Only Server 1 (PID A) runs                │
└─────────────────────────────────────────────────────┘
```

**Key Characteristics:**
- **Single Project:** One `.praxis-os/` directory per project
- **Multiple Spawn Attempts:** Cursor may spawn 3-5 servers simultaneously
- **Single Winner:** First to acquire RuntimeLock wins
- **Fast-Fail Losers:** Others exit within <1 second

---

## 2. Component Design

---

### 2.1 Component: RuntimeLock

**Purpose:** Enforce singleton MCP server per project by acquiring and holding a file-based lock for the entire process lifetime.

**Responsibilities:**
- Atomically acquire runtime lock on server startup
- Detect and cleanup stale locks from crashed processes
- Hold lock for entire server lifetime (hours/days)
- Release lock on graceful shutdown (finally block + atexit)
- Provide clear logging for all lock operations
- Handle edge cases gracefully (missing directory, corrupted lock file, etc.)

**Requirements Satisfied:**
- **FR-001 (Singleton Enforcement):** Ensures only one MCP server runs per project
- **FR-002 (Stale Lock Detection):** Detects dead PIDs and cleans up stale locks
- **FR-003 (Graceful Degradation):** Handles edge cases without blocking valid servers
- **FR-005 (Lock Lifecycle):** Acquires at startup, holds for lifetime, releases on shutdown
- **FR-006 (Observability):** Logs all lock operations with PIDs
- **FR-007 (Lock File Location):** Uses `.praxis-os/.cache/.runtime.lock`
- **NFR-R1 (Zero False Positives):** Conservative PID checking
- **NFR-P1 (Performance):** <100ms lock acquisition

**Public Interface:**

```python
from pathlib import Path
from typing import Optional
import os
import atexit
import logging

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
    
    LOCK_FILE_NAME = ".runtime.lock"
    
    def __init__(self, base_path: Path):
        """
        Initialize RuntimeLock.
        
        Args:
            base_path: Path to .praxis-os directory
        """
        pass
    
    def acquire(self) -> bool:
        """
        Attempt to acquire runtime lock.
        
        Returns:
            True if lock acquired, False if another server is running
        """
        pass
    
    def release(self) -> None:
        """
        Release runtime lock.
        
        Called on graceful shutdown (finally block + atexit handler).
        """
        pass
    
    def _try_claim_lock(self) -> bool:
        """
        Atomically create lock file with PID.
        
        Returns:
            True if lock claimed, False if file already exists
        """
        pass
    
    def _read_lock_holder(self) -> Optional[int]:
        """
        Read PID from lock file.
        
        Returns:
            PID of lock holder, or None if file is corrupted/missing
        """
        pass
    
    @staticmethod
    def _is_process_running(pid: int) -> bool:
        """
        Check if process is running.
        
        Args:
            pid: Process ID to check
            
        Returns:
            True if process is running, False otherwise
        """
        pass
    
    def _cleanup(self) -> None:
        """
        Cleanup on process exit (atexit handler).
        """
        pass
```

**Dependencies:**
- **Requires:** 
  - Python standard library (`os`, `pathlib`, `atexit`, `logging`, `subprocess`, `time`)
  - File system with atomic file creation support
  - PID checking support (`os.kill(pid, 0)`)
  - Process name verification (`/proc` filesystem or `ps` command)
- **Provides:** 
  - Singleton enforcement for MCP server
  - Used by `__main__.py` during server startup

**Error Handling:**
- **Lock file exists (holder alive):** Return `False` from `acquire()`, log INFO message, exit gracefully
- **Lock file exists (holder dead):** Remove stale lock, retry acquisition
- **Lock file corrupted (invalid PID):** Log warning, remove file, retry acquisition
- **Lock directory missing:** Create directory, proceed with acquisition
- **Lock file unreadable:** Log warning, assume holder is alive (safer default)
- **PID check fails:** Assume process is running (safer default)
- **Lock release fails:** Log warning, continue (best effort cleanup)

**Internal State:**
- `lock_file: Path` - Path to `.praxis-os/.cache/.runtime.lock`
- `pid: int` - Current process PID
- `acquired: bool` - Whether lock is currently held

---

### 2.2 Component: __main__.py Integration

**Purpose:** Integrate RuntimeLock into MCP server startup sequence.

**Responsibilities:**
- Acquire RuntimeLock before InitLock
- Release RuntimeLock on shutdown (finally block)
- Exit gracefully if RuntimeLock acquisition fails

**Requirements Satisfied:**
- **FR-005 (Lock Lifecycle):** Proper lock acquisition order and cleanup
- **FR-008 (Integration):** No breaking changes to existing code

**Code Changes:**

```python
# __main__.py (modifications)

from ouroboros.foundation.runtime_lock import RuntimeLock

def main():
    # Initialize components (for cleanup in finally block)
    runtime_lock = None
    init_lock = None
    # ... other components ...
    
    try:
        # Find and validate .praxis-os directory
        base_path = find_praxis_os_directory()
        logger.info("Base path: %s", base_path)
        
        # ✅ NEW: Acquire runtime lock (singleton enforcement)
        runtime_lock = RuntimeLock(base_path)
        if not runtime_lock.acquire():
            # Another server is running, exit gracefully
            logger.info(
                "Another MCP server is already running. "
                "This is expected behavior with misbehaving MCP clients."
            )
            sys.exit(0)
        
        # Acquire initialization lock (defends against concurrent spawns)
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
        
        if transport_mgr:
            transport_mgr.shutdown()
        
        if init_lock:
            init_lock.release()
        
        # ✅ NEW: Release runtime lock
        if runtime_lock:
            runtime_lock.release()
        
        logger.info("Shutdown complete")
```

**Dependencies:**
- **Requires:** RuntimeLock class
- **Provides:** Singleton MCP server enforcement

---

### 2.3 Component Interactions

**Interaction Sequence (Server Startup):**

```
┌──────────┐
│ __main__ │
└────┬─────┘
     │
     │ 1. RuntimeLock(base_path)
     ↓
┌────────────────┐
│ RuntimeLock    │
│ __init__()     │
└────┬───────────┘
     │
     │ 2. acquire()
     ↓
┌────────────────┐
│ RuntimeLock    │
│ _try_claim_lock│  ← Atomic file creation (O_CREAT | O_EXCL)
└────┬───────────┘
     │
     ├─→ Success? → Return True → Continue startup
     │
     └─→ Failure? → _read_lock_holder() → _is_process_running()
                    ├─→ Alive? → Return False → Exit gracefully
                    └─→ Dead? → Remove stale lock → Retry
```

**Interaction Table:**

| From | To | Method | Purpose |
|------|----|--------|---------|
| `__main__.py` | `RuntimeLock` | `__init__(base_path)` | Initialize lock with project path |
| `__main__.py` | `RuntimeLock` | `acquire()` | Attempt to acquire singleton lock |
| `RuntimeLock` | `RuntimeLock` | `_try_claim_lock()` | Atomically create lock file |
| `RuntimeLock` | `RuntimeLock` | `_read_lock_holder()` | Read PID from existing lock |
| `RuntimeLock` | `RuntimeLock` | `_is_process_running(pid)` | Check if PID is alive |
| `__main__.py` | `RuntimeLock` | `release()` | Release lock on shutdown |
| `atexit` | `RuntimeLock` | `_cleanup()` | Automatic cleanup on exit |

---

### 2.4 Module Organization

**File Location:**
```
.praxis-os/
└── ouroboros/
    └── foundation/
        ├── __init__.py
        ├── init_lock.py          # Existing
        ├── runtime_lock.py       # ✅ NEW
        └── lock_manager.py       # Existing (IndexLockManager)
```

**Module Dependencies:**
```
__main__.py
  ├─→ foundation.runtime_lock.RuntimeLock  # NEW
  ├─→ foundation.init_lock.InitLock        # Existing
  └─→ (no dependency on IndexLockManager)

RuntimeLock
  └─→ Python stdlib only (os, pathlib, atexit, logging)
```

**Dependency Rules:**
- ✅ No circular imports
- ✅ RuntimeLock is standalone (no internal dependencies)
- ✅ No changes to InitLock or IndexLockManager
- ✅ Only `__main__.py` imports RuntimeLock

---

## 3. API Specifications

---

### 3.1 RuntimeLock Public API

**Class:** `RuntimeLock`

**Constructor:**
```python
def __init__(self, base_path: Path) -> None
```
- **Parameters:**
  - `base_path: Path` - Path to `.praxis-os` directory
- **Returns:** None
- **Side Effects:** 
  - Creates `.cache/` directory if missing
  - Registers atexit cleanup handler
- **Exceptions:** None (graceful handling)

---

**Method:** `acquire()`
```python
def acquire(self, _retry_count: int = 0) -> bool
```
- **Purpose:** Attempt to acquire runtime lock
- **Parameters:** 
  - `_retry_count: int` - Internal retry counter (default: 0, max: 3)
- **Returns:** 
  - `True` if lock acquired successfully
  - `False` if another server is running or max retries exceeded
- **Side Effects:**
  - Creates `.cache/.runtime.lock` file with current PID and timestamp
  - Logs INFO message on success/failure
  - May remove stale lock files
  - Logs DEBUG message on retry attempts
- **Exceptions:** None (all errors handled internally)
- **Behavior:**
  - If lock file doesn't exist → create atomically, return True
  - If lock file exists with dead PID → remove, retry (up to 3 times)
  - If lock file exists with alive PID → return False
  - If lock file corrupted → remove, retry (up to 3 times)
  - If lock file is >24 hours old → assume stale, remove, retry
  - If max retries (3) exceeded → log error, return False

---

**Method:** `release()`
```python
def release(self) -> None
```
- **Purpose:** Release runtime lock
- **Parameters:** None
- **Returns:** None
- **Side Effects:**
  - Removes `.cache/.runtime.lock` file
  - Logs INFO message
- **Exceptions:** None (best-effort cleanup, logs warnings on failure)
- **Idempotency:** Safe to call multiple times

---

**Private Method:** `_try_claim_lock()`
```python
def _try_claim_lock(self) -> bool
```
- **Purpose:** Atomically create lock file with PID and timestamp
- **Returns:** 
  - `True` if file created successfully
  - `False` if file already exists, disk full, or directory at path
- **Implementation:** 
  - Uses `os.open()` with `O_CREAT | O_EXCL | O_WRONLY`
  - Writes "PID TIMESTAMP" format (e.g., "47294 1700000000")
  - Verifies bytes written (detects disk full)
  - Handles `IsADirectoryError` (removes directory, returns False)
  - Cleans up partial files on error

---

**Private Method:** `_read_lock_holder()`
```python
def _read_lock_holder(self) -> Optional[tuple[int, int]]
```
- **Purpose:** Read PID and timestamp from lock file
- **Returns:** 
  - `tuple[int, int]` (PID, timestamp) if file readable and valid
  - `None` if file missing/corrupted
- **Implementation:** 
  - Reads file content
  - Parses format: "PID TIMESTAMP" (e.g., "47294 1700000000")
  - Returns tuple (pid, timestamp)
  - Returns None on any parse error

---

**Static Method:** `_is_process_running()`
```python
@staticmethod
def _is_process_running(pid: int) -> bool
```
- **Purpose:** Check if process is running AND is an ouroboros server
- **Parameters:** `pid: int` - Process ID to check
- **Returns:** 
  - `True` if process is running and is ouroboros (or can't verify)
  - `False` if process is dead OR is not ouroboros (PID reused)
- **Implementation:** 
  - Uses `os.kill(pid, 0)` to check if PID exists
  - Calls `_get_process_cmdline(pid)` to verify process name
  - If cmdline contains "ouroboros" → return True
  - If cmdline doesn't contain "ouroboros" → return False (PID reuse!)
  - If can't read cmdline → return True (conservative, NFR-R1)
- **Platform Notes:** 
  - Linux/WSL2: Uses `/proc/{pid}/cmdline` (fast)
  - macOS: Falls back to `ps` command
  - All platforms: Conservative if verification fails

---

**Private Static Method:** `_get_process_cmdline()`
```python
@staticmethod
def _get_process_cmdline(pid: int) -> Optional[str]
```
- **Purpose:** Get process command line using stdlib only
- **Parameters:** `pid: int` - Process ID to query
- **Returns:** 
  - `str` command line if readable
  - `None` if cannot read (permission denied, etc.)
- **Implementation:**
  - Try `/proc/{pid}/cmdline` first (Linux, WSL2)
  - Fall back to `ps -p {pid} -o command=` (macOS, Unix)
  - Return None on any error
- **Platform Support:**
  - Linux/WSL2: `/proc` filesystem (instant)
  - macOS: `ps` command via subprocess (~50ms)
  - Windows: Not applicable (WSL2 only)

---

**Private Method:** `_cleanup()`
```python
def _cleanup(self) -> None
```
- **Purpose:** Cleanup on process exit (atexit handler)
- **Returns:** None
- **Side Effects:** Calls `release()`
- **Registration:** Registered in `__init__()` via `atexit.register()`

---

### 3.2 Integration API (__main__.py)

**Usage Pattern:**
```python
# 1. Import
from ouroboros.foundation.runtime_lock import RuntimeLock

# 2. Initialize
runtime_lock = RuntimeLock(base_path)

# 3. Acquire (before InitLock)
if not runtime_lock.acquire():
    logger.info("Another MCP server is already running.")
    sys.exit(0)

# 4. Run server (lock held)
run_server_forever()

# 5. Release (in finally block)
if runtime_lock:
    runtime_lock.release()
```

**Requirements Satisfied:**
- **FR-005 (Lock Lifecycle):** Acquire → Hold → Release
- **FR-008 (Integration):** Minimal changes to `__main__.py`

---

## 4. Data Models

---

### 4.1 Lock File Format

**File:** `.praxis-os/.cache/.runtime.lock`

**Format:** Plain text, UTF-8 encoded

**Content:** Single line containing PID and Unix timestamp (space-separated)

**Example:**
```
47294 1700000000
```

**Schema:**
```
lock_file_content ::= PID_STRING SPACE TIMESTAMP_STRING
PID_STRING ::= [0-9]+
TIMESTAMP_STRING ::= [0-9]+
SPACE ::= " "
```

**Validation Rules:**
- Must contain exactly 2 space-separated integers
- PID must be positive (PID > 0)
- Timestamp must be valid Unix timestamp (seconds since epoch)
- No additional whitespace or content

**Backward Compatibility:**
- Old format (PID only) is treated as timestamp=0
- Locks with timestamp=0 are assumed stale if >24 hours old (based on file mtime)

**Invalid Examples:**
```
# Invalid: Non-numeric
abc123 1700000000

# Invalid: Missing timestamp
47294

# Invalid: Negative PID
-1 1700000000

# Invalid: Multiple lines
47294 1700000000
extra content
```

---

### 4.2 RuntimeLock Internal State

**Class Attributes:**
```python
LOCK_FILE_NAME: str = ".runtime.lock"  # Constant
```

**Instance Attributes:**
```python
lock_file: Path              # Path to .cache/.runtime.lock
pid: int                     # Current process PID (os.getpid())
acquired: bool               # Whether lock is currently held
_max_retries: int = 3        # Maximum retry attempts for lock acquisition
```

**State Transitions:**
```
Initial State:
  acquired = False
  
After acquire() → True:
  acquired = True
  lock_file exists with self.pid
  
After release():
  acquired = False
  lock_file deleted
```

---

### 4.3 File System Structure

**Directory Layout:**
```
.praxis-os/
└── .cache/
    ├── .init.lock          # InitLock (existing)
    ├── .runtime.lock       # RuntimeLock (NEW)
    └── locks/
        ├── standards.lock  # IndexLockManager (existing)
        ├── code.lock       # IndexLockManager (existing)
        └── ...
```

**File Permissions:**
- `.runtime.lock`: `0o600` (owner read/write only)
- `.cache/`: `0o755` (owner rwx, group/other rx)

**Requirements Satisfied:**
- **FR-007 (Lock File Location):** Standardized location in `.cache/`

---

## 5. Security Considerations

---

### 5.1 PID Reuse Attack

**Threat:** Process A crashes, leaves lock file with PID X. OS reuses PID X for unrelated process B. RuntimeLock incorrectly thinks lock is held by valid server.

**Likelihood:** Medium (PID reuse can happen in minutes on busy systems with low pid_max)

**Impact:** Medium (false positive, blocks valid server from starting)

**Mitigation:**
- **Process Name Verification (PRIMARY):** Check if PID's command line contains "ouroboros". If not, it's a different process (PID reused). Uses stdlib only (`/proc` or `ps` command).
- **Timestamp Validation (SECONDARY):** Lock file includes Unix timestamp. If lock is >24 hours old AND PID exists, assume stale (belt-and-suspenders).
- **NFR-R1 (Zero False Positives):** Conservative checking (if can't verify process name, assume valid)

**Implementation:**
```python
@staticmethod
def _get_process_cmdline(pid: int) -> Optional[str]:
    """Get process command line using stdlib only."""
    # Try /proc first (Linux, WSL2)
    try:
        with open(f"/proc/{pid}/cmdline", 'rb') as f:
            cmdline = f.read().decode('utf-8', errors='ignore')
            return cmdline.replace('\x00', ' ').strip()
    except (FileNotFoundError, PermissionError, OSError):
        pass
    
    # Fall back to ps command (macOS, Unix)
    try:
        import subprocess
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
        
        # Verify it's actually ouroboros
        cmdline = _get_process_cmdline(pid)
        
        if cmdline is None:
            # Can't verify (permission denied, etc.)
            # Conservative: assume valid (NFR-R1)
            logger.debug("Cannot verify process name for PID %d", pid)
            return True
        
        # Check if it's ouroboros
        if 'ouroboros' in cmdline.lower():
            return True  # It's our server!
        
        # PID exists but is NOT ouroboros → PID reuse!
        logger.warning("PID %d is not ouroboros (cmd='%s')", pid, cmdline[:100])
        return False
        
    except OSError:
        return False  # PID doesn't exist
```

**Current Status:** Fully Mitigated
- Process name checking detects PID reuse **immediately** (no 24-hour wait)
- Timestamp provides secondary defense (belt-and-suspenders)
- Conservative fallback ensures zero false positives

---

### 5.2 Lock File Tampering

**Threat:** Malicious user modifies `.runtime.lock` file to contain invalid PID, causing denial of service.

**Likelihood:** Low (requires local file system access)

**Impact:** Low (user can manually delete lock file to recover)

**Mitigation:**
- **File Permissions:** `0o600` (owner only)
- **Validation:** Corrupted lock files are detected and removed
- **Logging:** Tampering attempts are logged

**Current Status:** Accepted risk (requires local access, easy recovery)

---

### 5.3 Symlink Attack

**Threat:** Attacker creates symlink at `.cache/.runtime.lock` pointing to sensitive file. RuntimeLock writes PID to sensitive file.

**Likelihood:** Low (requires local file system access before server starts)

**Impact:** Low (PID is harmless data, not executable code)

**Mitigation:**
- **Atomic Creation:** `O_CREAT | O_EXCL` fails if file exists (including symlinks)
- **No Follow:** Lock file is created directly, not followed

**Current Status:** Mitigated by atomic file creation

---

### 5.4 Race Condition in Stale Lock Detection

**Threat:** Process A checks lock, finds PID X is dead, prepares to remove lock. Process B starts with PID X (reuse), acquires lock. Process A removes lock, thinking it's stale.

**Likelihood:** Very Low (requires precise timing + PID reuse)

**Impact:** High (both servers run, index corruption)

**Mitigation:**
- **Atomic Operations:** Lock removal and creation are atomic
- **Conservative Checking:** If uncertain, assume lock is valid
- **Retry Logic:** After removing stale lock, retry acquisition (not automatic success)
- **Retry Limit:** Maximum 3 retries prevents infinite loops in race conditions

**Current Status:** Mitigated by atomic operations, conservative checking, and retry limits

---

### 5.5 Disk Full During Lock Acquisition

**Threat:** Disk full causes `os.write()` to fail, leaving empty lock file. Next server sees empty file, assumes stale, removes it. Both servers acquire lock.

**Likelihood:** Low (requires disk to fill during lock acquisition)

**Impact:** High (both servers run, index corruption)

**Mitigation:**
- **Verify Bytes Written:** Check `os.write()` return value matches expected bytes
- **Cleanup on Error:** If write fails, remove partial lock file before returning False
- **Graceful Degradation:** Log error, return False (server won't start, but no corruption)

**Implementation:**
```python
pid_bytes = f"{self.pid} {int(time.time())}".encode('utf-8')
bytes_written = os.write(fd, pid_bytes)

if bytes_written != len(pid_bytes):
    logger.error("Failed to write PID to lock file (disk full?)")
    self.lock_file.unlink(missing_ok=True)  # Cleanup
    return False
```

**Current Status:** Mitigated (write verification + cleanup)

---

### 5.6 Directory at Lock Path (DoS Attack)

**Threat:** Attacker (or buggy script) creates directory at `.cache/.runtime.lock`. `os.open()` fails with `IsADirectoryError`. Server cannot start.

**Likelihood:** Very Low (requires malicious intent or severe bug)

**Impact:** Medium (denial of service, but easy to fix manually)

**Mitigation:**
- **Detect Directory:** Catch `IsADirectoryError` specifically
- **Remove Directory:** Use `shutil.rmtree()` to remove directory
- **Retry Acquisition:** After cleanup, retry lock acquisition
- **Log Warning:** Alert user to potential attack or bug

**Implementation:**
```python
except IsADirectoryError:
    logger.error("Directory exists at lock path: %s (removing)", self.lock_file)
    import shutil
    shutil.rmtree(self.lock_file)
    return False  # Caller will retry
```

**Current Status:** Mitigated (directory detection + removal)

---

## 6. Performance Considerations

---

### 6.1 Lock Acquisition Performance

**Target:** <100ms (NFR-P1)

**Breakdown:**
- File creation: <1ms (atomic syscall)
- PID checking (if needed): <10ms (os.kill syscall)
- Stale lock removal: <5ms (unlink syscall)
- Retry (if stale): <20ms (total)

**Total (normal case):** <1ms  
**Total (stale lock case):** <20ms  
**Total (worst case):** <50ms (multiple retries)

**Optimization Strategies:**
- Use atomic operations (no locking overhead)
- Minimize file I/O (single read/write)
- No network calls
- No database queries

**Requirements Satisfied:**
- **NFR-P1 (Lock Acquisition Time):** <100ms target easily met

---

### 6.2 Duplicate Spawn Detection Performance

**Target:** <1 second (NFR-P2)

**Breakdown:**
- RuntimeLock.acquire(): <20ms
- Log message: <1ms
- sys.exit(0): <10ms

**Total:** <50ms (well under 1 second target)

**Requirements Satisfied:**
- **NFR-P2 (Duplicate Spawn Detection):** <1 second target easily met

---

### 6.3 Memory Footprint

**RuntimeLock Instance:**
- `lock_file: Path` - 64 bytes (pointer + small string)
- `pid: int` - 8 bytes
- `acquired: bool` - 1 byte
- **Total:** <100 bytes per instance

**Lock File:**
- Size: <10 bytes (PID as text, e.g., "47294")
- Disk space: Negligible

**Requirements Satisfied:**
- **NFR-M1 (Code Quality):** <200 LOC, minimal memory footprint

---

### 6.4 Scalability

**Single-Machine Limit:**
- One RuntimeLock per project
- No limit on number of projects
- No shared state between projects

**Multi-Machine:**
- Out of scope (see srd.md Section 6)
- Would require distributed lock (Redis, etcd, etc.)

**Requirements Satisfied:**
- **FR-004 (Cross-Platform):** Works on all platforms
- **Out of Scope:** Multi-machine deployment not supported

---

### 6.5 Performance Testing Strategy

**Benchmarks:**
1. **Lock Acquisition Time:** Measure `acquire()` latency (normal case)
2. **Stale Lock Detection Time:** Measure `acquire()` latency with dead PID
3. **Concurrent Spawn Stress Test:** Spawn 10 servers simultaneously, verify only 1 runs

**Acceptance Criteria:**
- Lock acquisition: <100ms (95th percentile)
- Duplicate spawn detection: <1 second (99th percentile)
- Stress test: 100% success rate (only 1 server runs)

**Requirements Satisfied:**
- **NFR-P1, NFR-P2:** Performance targets validated by benchmarks

---


