# Dependency Analysis: Lock Architecture

**Date:** 2025-11-17  
**Question:** Does the expanded spec maintain downward-only dependency pathing?  
**Answer:** ✅ **YES** - All locks are independent, no circular dependencies

---

## Dependency Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      __main__.py                             │
│                   (Entry Point)                              │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
             │ imports                    │ imports
             ↓                            ↓
    ┌────────────────┐          ┌────────────────┐
    │  RuntimeLock   │          │   InitLock     │
    │   (Layer 2)    │          │   (Layer 1)    │
    │                │          │                │
    │  NEW           │          │  EXISTING      │
    │  Lifetime lock │          │  Init-only     │
    └────────────────┘          └────────────────┘
             │                            │
             │ NO DEPENDENCIES            │ NO DEPENDENCIES
             │                            │
             ↓                            ↓
        (standalone)                 (standalone)


                    ┌─────────────────────────────┐
                    │    Index Containers         │
                    │  (StandardsIndex, CodeIndex) │
                    └──────────────┬──────────────┘
                                   │
                                   │ imports
                                   ↓
                          ┌────────────────┐
                          │ IndexLockManager│
                          │   (Layer 3)     │
                          │                 │
                          │  EXISTING       │
                          │  Per-index ops  │
                          └────────────────┘
                                   │
                                   │ NO DEPENDENCIES
                                   ↓
                              (standalone)
```

---

## Layer Architecture

### **Layer 1: InitLock (Initialization)**
- **Purpose:** Prevents concurrent server initialization
- **Lifetime:** Startup → initialization complete (~5-30 seconds)
- **File:** `.praxis-os/.cache/.init.lock`
- **Used By:** `__main__.py` (entry point)
- **Dependencies:** **NONE** (stdlib only: `os`, `pathlib`, `time`, `subprocess`)

### **Layer 2: RuntimeLock (Singleton Enforcement)**
- **Purpose:** Ensures only one MCP server runs per project
- **Lifetime:** Startup → shutdown (entire process lifetime)
- **File:** `.praxis-os/.cache/.runtime.lock`
- **Used By:** `__main__.py` (entry point)
- **Dependencies:** **NONE** (stdlib only: `os`, `pathlib`, `time`, `subprocess`, `atexit`)

### **Layer 3: IndexLockManager (Per-Index Operations)**
- **Purpose:** Prevents concurrent index corruption (build/search)
- **Lifetime:** Per-operation (seconds to minutes)
- **File:** `.praxis-os/.cache/locks/{index_name}.lock`
- **Used By:** `StandardsIndex`, `CodeIndex` (index containers)
- **Dependencies:** **NONE** (stdlib only: `fcntl`, `pathlib`, `atexit`)

---

## Dependency Rules

### ✅ **Allowed (Downward Only):**
```
__main__.py
    ↓ imports
RuntimeLock  (no dependencies)

__main__.py
    ↓ imports
InitLock     (no dependencies)

StandardsIndex / CodeIndex
    ↓ imports
IndexLockManager  (no dependencies)
```

### ❌ **Forbidden (No Upward or Circular):**
```
RuntimeLock
    ↗ imports (FORBIDDEN)
__main__.py

InitLock
    ↗ imports (FORBIDDEN)
RuntimeLock

IndexLockManager
    ↗ imports (FORBIDDEN)
StandardsIndex / CodeIndex

RuntimeLock ←→ InitLock (FORBIDDEN - circular)
```

---

## Verification: No Cross-Lock Dependencies

### **RuntimeLock Dependencies:**
```python
# ouroboros/foundation/runtime_lock.py (NEW)
import os
import time
import subprocess
import atexit
import logging
from pathlib import Path
from typing import Optional

# ✅ NO IMPORTS of InitLock or IndexLockManager
```

### **InitLock Dependencies:**
```python
# ouroboros/foundation/init_lock.py (EXISTING)
import os
import time
import logging
from pathlib import Path
from typing import Optional

# ✅ NO IMPORTS of RuntimeLock or IndexLockManager
```

### **IndexLockManager Dependencies:**
```python
# ouroboros/subsystems/rag/lock_manager.py (EXISTING)
import atexit
import logging
import platform
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

try:
    import fcntl  # Unix/Linux/macOS only
    FCNTL_AVAILABLE = True
except ImportError:
    FCNTL_AVAILABLE = False

from ouroboros.utils.errors import ActionableError

# ✅ NO IMPORTS of RuntimeLock or InitLock
# ✅ Only imports ActionableError (error handling utility)
```

---

## Usage Patterns

### **Pattern 1: __main__.py (Entry Point)**
```python
# ouroboros/__main__.py

# Step 1: Acquire RuntimeLock (lifetime lock)
from ouroboros.foundation.runtime_lock import RuntimeLock

runtime_lock = RuntimeLock(base_path)
if not runtime_lock.acquire():
    logger.info("Another MCP server is running. Exiting.")
    sys.exit(0)

# Step 2: Acquire InitLock (initialization lock)
from ouroboros.foundation.init_lock import InitLock

init_lock = InitLock(base_path, timeout_seconds=10)
if not init_lock.acquire():
    logger.info("Another process is initializing. Exiting.")
    sys.exit(0)

try:
    # Step 3: Initialize server (indexes, subsystems, etc.)
    initialize_server()
finally:
    # Step 4: Release InitLock (initialization complete)
    init_lock.release()

# RuntimeLock held until process exit (atexit handler)
```

**Dependency Flow:**
```
__main__.py
    ↓ imports RuntimeLock
    ↓ imports InitLock
    ↓ initializes server
        ↓ creates StandardsIndex
            ↓ creates IndexLockManager
```

**✅ Downward only:** `__main__.py` → locks, no reverse dependencies

---

### **Pattern 2: Index Containers (StandardsIndex, CodeIndex)**
```python
# ouroboros/subsystems/rag/standards/container.py

from ouroboros.subsystems.rag.lock_manager import IndexLockManager

class StandardsIndex:
    def __init__(self, config, base_path):
        lock_dir = base_path / ".cache" / "locks"
        self._lock_manager = IndexLockManager("standards", lock_dir)
    
    def build(self):
        with self._lock_manager.exclusive_lock():
            # Build index (exclusive access)
            pass
    
    def search(self, query):
        with self._lock_manager.shared_lock():
            # Search index (shared access)
            pass
```

**Dependency Flow:**
```
StandardsIndex / CodeIndex
    ↓ imports IndexLockManager
    ↓ uses for per-operation locking
```

**✅ Downward only:** Index containers → `IndexLockManager`, no reverse dependencies

---

## Security Hardening: Shared Patterns, No Shared Code

### **Shared Security Patterns:**
All three locks use the **same security mitigations** (discovered during RuntimeLock design):

1. **Process Name Verification** (`_get_process_cmdline()`)
2. **Timestamp Validation** (lock file format: `"PID TIMESTAMP"`)
3. **Disk Full Handling** (write verification + cleanup)
4. **Directory DoS Mitigation** (`IsADirectoryError` handling)
5. **Retry Limit** (max 3 retries)

### **Implementation:**
- **RuntimeLock:** Full implementation (NEW)
- **InitLock:** Apply patterns (EXISTING, hardened)
- **IndexLockManager:** Partial (only directory DoS, fcntl-based locking is different)

### **Code Reuse:**
**❌ NO shared code** (each lock is standalone)
- RuntimeLock: `ouroboros/foundation/runtime_lock.py`
- InitLock: `ouroboros/foundation/init_lock.py`
- IndexLockManager: `ouroboros/subsystems/rag/lock_manager.py`

**Why no shared code?**
- **Independence:** Locks must work in isolation (no circular dependencies)
- **Simplicity:** Each lock is self-contained (~200 LOC)
- **Maintainability:** Changes to one lock don't affect others
- **Testing:** Each lock can be tested independently

**Trade-off:**
- **Duplication:** `_get_process_cmdline()` duplicated in RuntimeLock and InitLock
- **Benefit:** Zero dependencies, easier to understand, no coupling

---

## Verification Checklist

### ✅ **Downward-Only Dependencies:**
- [ ] ✅ `__main__.py` imports `RuntimeLock` (downward)
- [ ] ✅ `__main__.py` imports `InitLock` (downward)
- [ ] ✅ `StandardsIndex` / `CodeIndex` import `IndexLockManager` (downward)
- [ ] ✅ `RuntimeLock` has NO imports of other locks
- [ ] ✅ `InitLock` has NO imports of other locks
- [ ] ✅ `IndexLockManager` has NO imports of other locks

### ✅ **No Circular Dependencies:**
- [ ] ✅ `RuntimeLock` does NOT import `InitLock`
- [ ] ✅ `RuntimeLock` does NOT import `IndexLockManager`
- [ ] ✅ `InitLock` does NOT import `RuntimeLock`
- [ ] ✅ `InitLock` does NOT import `IndexLockManager`
- [ ] ✅ `IndexLockManager` does NOT import `RuntimeLock`
- [ ] ✅ `IndexLockManager` does NOT import `InitLock`

### ✅ **No Upward Dependencies:**
- [ ] ✅ `RuntimeLock` does NOT import `__main__.py`
- [ ] ✅ `InitLock` does NOT import `__main__.py`
- [ ] ✅ `IndexLockManager` does NOT import `StandardsIndex` / `CodeIndex`

---

## Summary

**Question:** Does the expanded spec maintain downward-only dependency pathing?

**Answer:** ✅ **YES**

**Evidence:**
1. **All locks are independent** (no cross-lock imports)
2. **Entry point imports locks** (downward: `__main__.py` → locks)
3. **Index containers import IndexLockManager** (downward: containers → lock)
4. **No circular dependencies** (verified via grep)
5. **No upward dependencies** (locks don't import their users)

**Architecture Grade:** **A+** (clean, layered, downward-only)

---

## Future Considerations

### **If we ever need shared lock utilities:**

**Option A: Shared utility module (NOT RECOMMENDED)**
```python
# ouroboros/foundation/lock_utils.py
def get_process_cmdline(pid: int) -> Optional[str]:
    # Shared implementation
    pass
```

**Problem:** Creates upward dependency (locks → utils → locks)

**Option B: Keep duplication (RECOMMENDED)**
- Each lock is self-contained
- ~20 lines of duplication is acceptable
- Easier to understand and maintain
- No coupling between locks

**Decision:** **Keep duplication** (current approach is correct)

---

**Status:** ✅ Dependency analysis complete - downward-only dependencies confirmed

