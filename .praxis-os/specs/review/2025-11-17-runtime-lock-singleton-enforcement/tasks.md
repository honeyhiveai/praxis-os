# Implementation Tasks

**Project:** RuntimeLock - Singleton MCP Server Enforcement  
**Date:** 2025-11-17  
**Based on:** srd.md (requirements) + specs.md (design)

---

## Overview

This document defines the implementation tasks for RuntimeLock, broken into 4 phases:
1. **Phase 1:** RuntimeLock Implementation (2.5 hours) - includes security fixes
2. **Phase 2:** Integration with __main__.py (30 minutes)
3. **Phase 3:** Testing (1.5 hours)
4. **Phase 4:** Documentation (30 minutes)

**Total Estimated Time:** 5 hours

**Security Fixes Added (+30 minutes):**
- Timestamp validation (PID reuse mitigation)
- Retry limit (infinite loop prevention)
- Disk full handling (write verification)
- Directory DoS mitigation

---

## Phase 1: RuntimeLock Implementation

**Duration:** 2.5 hours  
**Purpose:** Implement the RuntimeLock class with all core functionality including security fixes and process name verification

---

### Task 1.1: Create RuntimeLock Class Structure

**Estimated Time:** 15 minutes

**Description:** Create `runtime_lock.py` file with class skeleton, imports, and constants.

**Acceptance Criteria:**
- [ ] File created at `.praxis-os/ouroboros/foundation/runtime_lock.py`
- [ ] All imports added (`os`, `pathlib`, `atexit`, `logging`, `typing`)
- [ ] `RuntimeLock` class defined with `LOCK_FILE_NAME` constant
- [ ] `__init__()` method signature defined with type hints
- [ ] All public and private method signatures defined
- [ ] Class docstring complete (from specs.md Section 2.1)
- [ ] File passes `mypy` type checking (no errors)

**Dependencies:** None

**Requirements Satisfied:**
- NFR-M2 (Type Safety): 100% type hints

---

### Task 1.2: Implement __init__() Method

**Estimated Time:** 10 minutes

**Description:** Implement constructor to initialize lock state and register atexit handler.

**Acceptance Criteria:**
- [ ] `self.lock_file` set to `base_path / ".cache" / ".runtime.lock"`
- [ ] `self.pid` set to `os.getpid()`
- [ ] `self.acquired` initialized to `False`
- [ ] `.cache/` directory created if missing (`mkdir(parents=True, exist_ok=True)`)
- [ ] Atexit handler registered (`atexit.register(self._cleanup)`)
- [ ] No exceptions raised (graceful error handling)
- [ ] Unit test passes: `test_runtime_lock_init()`

**Dependencies:** Task 1.1

**Requirements Satisfied:**
- FR-007 (Lock File Location): Uses `.cache/.runtime.lock`

---

### Task 1.3: Implement _try_claim_lock() Method

**Estimated Time:** 20 minutes

**Description:** Implement atomic lock file creation using `os.open()` with `O_CREAT | O_EXCL`, including timestamp, write verification, and error handling.

**Acceptance Criteria:**
- [ ] Uses `os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)`
- [ ] Writes `"{self.pid} {int(time.time())}"` as UTF-8 text (PID + timestamp)
- [ ] Verifies bytes written matches expected length (detects disk full)
- [ ] If write fails, removes partial lock file before returning `False`
- [ ] Closes file descriptor after write
- [ ] Returns `True` on success
- [ ] Returns `False` on `FileExistsError`
- [ ] Catches `IsADirectoryError`, removes directory, returns `False`
- [ ] Logs warning on other exceptions, cleans up, returns `False`
- [ ] File permissions are `0o600` (owner read/write only)
- [ ] Unit test passes: `test_try_claim_lock_success()`
- [ ] Unit test passes: `test_try_claim_lock_file_exists()`
- [ ] Unit test passes: `test_try_claim_lock_disk_full()` (mock scenario)
- [ ] Unit test passes: `test_try_claim_lock_directory_at_path()`

**Dependencies:** Task 1.2

**Requirements Satisfied:**
- FR-001 (Singleton Enforcement): Atomic file creation
- FR-007 (Lock File Location): Correct permissions
- Security: Disk full handling, directory DoS mitigation

---

### Task 1.4: Implement _read_lock_holder() Method

**Estimated Time:** 15 minutes

**Description:** Implement PID and timestamp reading from lock file with error handling and backward compatibility.

**Acceptance Criteria:**
- [ ] Reads lock file content as UTF-8 text
- [ ] Strips whitespace from content
- [ ] Parses format: "PID TIMESTAMP" (space-separated)
- [ ] Returns `tuple[int, int]` (PID, timestamp) on success
- [ ] Handles old format (PID only): Returns `(pid, 0)` for backward compatibility
- [ ] Returns `None` on `FileNotFoundError`
- [ ] Returns `None` on `ValueError` (invalid format)
- [ ] Returns `None` on other `OSError`
- [ ] Unit test passes: `test_read_lock_holder_valid_with_timestamp()`
- [ ] Unit test passes: `test_read_lock_holder_valid_old_format()` (PID only)
- [ ] Unit test passes: `test_read_lock_holder_missing()`
- [ ] Unit test passes: `test_read_lock_holder_corrupted()`

**Dependencies:** Task 1.3

**Requirements Satisfied:**
- FR-002 (Stale Lock Detection): Read PID and timestamp for checking
- FR-003 (Graceful Degradation): Handle corrupted files
- Security: PID reuse mitigation (timestamp validation)

---

### Task 1.5: Implement _get_process_cmdline() and _is_process_running() Methods

**Estimated Time:** 25 minutes

**Description:** Implement PID checking with process name verification using stdlib only (`/proc` or `ps` command).

**Acceptance Criteria:**

**_get_process_cmdline():**
- [ ] Tries `/proc/{pid}/cmdline` first (Linux, WSL2)
- [ ] Reads file as binary, decodes UTF-8, replaces null bytes with spaces
- [ ] Falls back to `ps -p {pid} -o command=` on macOS/Unix
- [ ] Uses `subprocess.run()` with `timeout=0.5` seconds
- [ ] Returns command line string on success
- [ ] Returns `None` on any error (FileNotFoundError, PermissionError, timeout, etc.)
- [ ] Unit test passes: `test_get_process_cmdline_proc()` (Linux)
- [ ] Unit test passes: `test_get_process_cmdline_ps()` (macOS, mock)
- [ ] Unit test passes: `test_get_process_cmdline_not_found()` (dead PID)

**_is_process_running():**
- [ ] Uses `os.kill(pid, 0)` to check if PID exists
- [ ] Calls `_get_process_cmdline(pid)` to get command line
- [ ] If cmdline is `None`, returns `True` (conservative, can't verify)
- [ ] If cmdline contains "ouroboros" (case-insensitive), returns `True`
- [ ] If cmdline does NOT contain "ouroboros", logs WARNING, returns `False` (PID reuse!)
- [ ] Returns `False` on `OSError` (PID doesn't exist)
- [ ] Handles negative PIDs gracefully (return `False`)
- [ ] Unit test passes: `test_is_process_running_alive_ouroboros()` (current process)
- [ ] Unit test passes: `test_is_process_running_dead()` (PID 99999)
- [ ] Unit test passes: `test_is_process_running_pid_reused()` (mock: PID exists but not ouroboros)
- [ ] Unit test passes: `test_is_process_running_cannot_verify()` (mock: cmdline returns None)

**Dependencies:** Task 1.4

**Requirements Satisfied:**
- FR-002 (Stale Lock Detection): Check if PID is alive AND is ouroboros
- FR-004 (Cross-Platform): Works on Linux, macOS, WSL2
- NFR-R1 (Zero False Positives): Conservative checking (assume valid if can't verify)
- Security: PID reuse mitigation (immediate detection via process name)

---

### Task 1.6: Implement acquire() Method

**Estimated Time:** 40 minutes

**Description:** Implement main lock acquisition logic with stale lock detection, process name verification, timestamp validation, retry limit, and comprehensive logging.

**Acceptance Criteria:**
- [ ] Method signature: `def acquire(self, _retry_count: int = 0) -> bool`
- [ ] If `_retry_count >= 3`, logs ERROR "Failed to acquire lock after 3 retries", returns `False`
- [ ] Calls `_try_claim_lock()` first
- [ ] If successful, sets `self.acquired = True`, logs INFO, returns `True`
- [ ] If file exists, calls `_read_lock_holder()` to get `(holder_pid, holder_timestamp)`
- [ ] If holder info is `None` (corrupted), removes lock file, retries with `_retry_count + 1`
- [ ] If holder info is valid, calculates lock age: `(time.time() - holder_timestamp) / 3600` hours
- [ ] If lock age > 24 hours, logs WARNING "Lock is X hours old, assuming stale", removes file, retries
- [ ] If holder PID is valid and recent, calls `_is_process_running(holder_pid)`
  - [ ] If returns `False` (dead OR not ouroboros), logs INFO about stale lock, removes file, retries
  - [ ] If returns `True` (alive and is ouroboros), logs INFO about existing server, returns `False`
- [ ] Logs DEBUG message on each retry: "Retrying lock acquisition (attempt X/3)"
- [ ] All log messages include relevant PIDs and timestamps
- [ ] Unit test passes: `test_acquire_success()`
- [ ] Unit test passes: `test_acquire_already_held()`
- [ ] Unit test passes: `test_acquire_stale_lock_dead_pid()`
- [ ] Unit test passes: `test_acquire_stale_lock_pid_reused()` (PID exists but not ouroboros)
- [ ] Unit test passes: `test_acquire_stale_lock_old_timestamp()`
- [ ] Unit test passes: `test_acquire_corrupted_lock()`
- [ ] Unit test passes: `test_acquire_max_retries_exceeded()`

**Dependencies:** Tasks 1.3, 1.4, 1.5

**Requirements Satisfied:**
- FR-001 (Singleton Enforcement): Main acquisition logic
- FR-002 (Stale Lock Detection): Detect and cleanup stale locks
- FR-003 (Graceful Degradation): Handle edge cases
- FR-006 (Observability): Log all operations with retry details
- NFR-P1 (Performance): <100ms acquisition time
- Security: PID reuse mitigation (process name + timestamp), infinite loop prevention (retry limit)

---

### Task 1.7: Implement release() Method

**Estimated Time:** 10 minutes

**Description:** Implement lock release with graceful error handling.

**Acceptance Criteria:**
- [ ] Checks `self.acquired` flag (no-op if `False`)
- [ ] Attempts to delete lock file (`self.lock_file.unlink()`)
- [ ] Logs INFO message on successful release (include PID)
- [ ] Catches exceptions, logs warning on failure
- [ ] Sets `self.acquired = False` in finally block
- [ ] Idempotent: Safe to call multiple times
- [ ] Unit test passes: `test_release_success()`
- [ ] Unit test passes: `test_release_not_acquired()`
- [ ] Unit test passes: `test_release_file_missing()`

**Dependencies:** Task 1.6

**Requirements Satisfied:**
- FR-005 (Lock Lifecycle): Release on shutdown
- FR-006 (Observability): Log release

---

### Task 1.8: Implement _cleanup() Method

**Estimated Time:** 5 minutes

**Description:** Implement atexit handler to call release().

**Acceptance Criteria:**
- [ ] Calls `self.release()`
- [ ] No exceptions raised (release() handles errors)
- [ ] Unit test passes: `test_cleanup_calls_release()` (mock test)

**Dependencies:** Task 1.7

**Requirements Satisfied:**
- FR-005 (Lock Lifecycle): Automatic cleanup on exit

---

## Phase 1 Validation Gate

**Before proceeding to Phase 2:**
- [ ] All Task 1.1-1.8 acceptance criteria met ✅
- [ ] All unit tests pass (8 tests minimum) ✅
- [ ] `mypy` type checking passes (0 errors) ✅
- [ ] Code coverage: 100% for RuntimeLock class ✅
- [ ] Code review: <200 LOC (NFR-M1) ✅

---

## Phase 2: Integration with __main__.py

**Duration:** 30 minutes  
**Purpose:** Integrate RuntimeLock into MCP server startup sequence

---

### Task 2.1: Add RuntimeLock Import

**Estimated Time:** 2 minutes

**Description:** Add import statement for RuntimeLock in `__main__.py`.

**Acceptance Criteria:**
- [ ] Import added: `from ouroboros.foundation.runtime_lock import RuntimeLock`
- [ ] Import placed after existing foundation imports
- [ ] No import errors when running `__main__.py`

**Dependencies:** Phase 1 complete

**Requirements Satisfied:**
- FR-008 (Integration): Minimal changes to __main__.py

---

### Task 2.2: Initialize RuntimeLock Variable

**Estimated Time:** 3 minutes

**Description:** Add `runtime_lock` variable initialization in `main()` function.

**Acceptance Criteria:**
- [ ] `runtime_lock = None` added at top of `main()` function
- [ ] Placed alongside other component initializations (port_manager, init_lock, etc.)

**Dependencies:** Task 2.1

**Requirements Satisfied:**
- FR-005 (Lock Lifecycle): Proper initialization

---

### Task 2.3: Acquire RuntimeLock Before InitLock

**Estimated Time:** 10 minutes

**Description:** Add RuntimeLock acquisition logic before InitLock acquisition.

**Acceptance Criteria:**
- [ ] `runtime_lock = RuntimeLock(base_path)` called after `find_praxis_os_directory()`
- [ ] `if not runtime_lock.acquire():` check added
- [ ] On failure, log INFO message: "Another MCP server is already running..."
- [ ] On failure, call `sys.exit(0)` (graceful exit)
- [ ] RuntimeLock acquired BEFORE InitLock (correct order)
- [ ] No changes to existing InitLock logic

**Dependencies:** Task 2.2

**Requirements Satisfied:**
- FR-001 (Singleton Enforcement): Acquire runtime lock
- FR-005 (Lock Lifecycle): Correct acquisition order
- FR-006 (Observability): Log duplicate spawn detection

---

### Task 2.4: Release RuntimeLock in Finally Block

**Estimated Time:** 5 minutes

**Description:** Add RuntimeLock release in finally block for cleanup.

**Acceptance Criteria:**
- [ ] `if runtime_lock: runtime_lock.release()` added to finally block
- [ ] Placed after `init_lock.release()` (correct order)
- [ ] Finally block executes on both normal exit and exceptions

**Dependencies:** Task 2.3

**Requirements Satisfied:**
- FR-005 (Lock Lifecycle): Release on shutdown
- NFR-C1 (No Breaking Changes): Existing cleanup logic unchanged

---

### Task 2.5: Manual Integration Testing

**Estimated Time:** 10 minutes

**Description:** Manually test integration with multiple server spawns.

**Acceptance Criteria:**
- [ ] Start first server: Verify it acquires lock and runs
- [ ] Start second server: Verify it exits gracefully within 1 second
- [ ] Check logs: Verify "Runtime lock acquired" and "Another MCP server is running" messages
- [ ] Kill first server: Verify lock file is removed
- [ ] Start third server: Verify it acquires lock successfully
- [ ] Force-kill server (`kill -9`): Verify lock file remains
- [ ] Start fourth server: Verify it detects stale lock and acquires

**Dependencies:** Task 2.4

**Requirements Satisfied:**
- FR-001 (Singleton Enforcement): Only one server runs
- FR-002 (Stale Lock Detection): Stale locks are cleaned up
- NFR-P2 (Duplicate Spawn Detection): <1 second exit time

---

## Phase 2 Validation Gate

**Before proceeding to Phase 3:**
- [ ] All Task 2.1-2.5 acceptance criteria met ✅
- [ ] Manual integration tests pass ✅
- [ ] No regressions in existing functionality ✅
- [ ] Server starts and runs normally ✅

---

## Phase 3: Testing

**Duration:** 1.5 hours  
**Purpose:** Comprehensive unit, integration, and stress testing

---

### Task 3.1: Unit Tests for RuntimeLock

**Estimated Time:** 30 minutes

**Description:** Write comprehensive unit tests for all RuntimeLock methods.

**Acceptance Criteria:**
- [ ] Test file created: `tests/ouroboros/foundation/test_runtime_lock.py`
- [ ] Test: `test_runtime_lock_init()` - Verify initialization
- [ ] Test: `test_try_claim_lock_success()` - Atomic file creation
- [ ] Test: `test_try_claim_lock_file_exists()` - File already exists
- [ ] Test: `test_read_lock_holder_valid()` - Read valid PID
- [ ] Test: `test_read_lock_holder_missing()` - File missing
- [ ] Test: `test_read_lock_holder_corrupted()` - Invalid PID
- [ ] Test: `test_is_process_running_alive()` - Current process
- [ ] Test: `test_is_process_running_dead()` - Dead PID (99999)
- [ ] Test: `test_acquire_success()` - Normal acquisition
- [ ] Test: `test_acquire_already_held()` - Another server running
- [ ] Test: `test_acquire_stale_lock()` - Dead PID cleanup
- [ ] Test: `test_release_success()` - Normal release
- [ ] Test: `test_release_idempotent()` - Multiple releases
- [ ] All tests pass
- [ ] Code coverage: 100% for RuntimeLock class

**Dependencies:** Phase 1 complete

**Requirements Satisfied:**
- NFR-M3 (Test Coverage): 100% line coverage

---

### Task 3.2: Integration Tests

**Estimated Time:** 20 minutes

**Description:** Write integration tests for multi-process scenarios.

**Acceptance Criteria:**
- [ ] Test: `test_integration_single_server()` - One server starts successfully
- [ ] Test: `test_integration_duplicate_spawn()` - Second server exits gracefully
- [ ] Test: `test_integration_stale_lock_cleanup()` - Stale lock detected and removed
- [ ] Test: `test_integration_sequential_starts()` - Server A exits, Server B starts
- [ ] All tests pass
- [ ] Tests use `subprocess` to spawn actual MCP servers

**Dependencies:** Phase 2 complete

**Requirements Satisfied:**
- FR-001 (Singleton Enforcement): Integration validation
- FR-002 (Stale Lock Detection): Integration validation

---

### Task 3.3: Stress Tests

**Estimated Time:** 20 minutes

**Description:** Write stress tests to simulate Cursor's race condition.

**Acceptance Criteria:**
- [ ] Test: `test_stress_concurrent_spawns()` - Spawn 10 servers simultaneously
- [ ] Verify only 1 server remains running
- [ ] Verify 9 servers exit gracefully
- [ ] Test: `test_stress_rapid_sequential()` - Start/stop 20 servers rapidly
- [ ] Verify no stale locks remain
- [ ] All tests pass
- [ ] Tests complete within 30 seconds

**Dependencies:** Task 3.2

**Requirements Satisfied:**
- NFR-P2 (Duplicate Spawn Detection): Stress validation
- NFR-R2 (Stale Lock Detection Accuracy): 100% detection rate

---

### Task 3.4: Performance Benchmarks

**Estimated Time:** 15 minutes

**Description:** Benchmark lock acquisition and duplicate spawn detection times.

**Acceptance Criteria:**
- [ ] Benchmark: Lock acquisition time (normal case)
- [ ] Verify 95th percentile < 100ms (NFR-P1)
- [ ] Benchmark: Lock acquisition time (stale lock case)
- [ ] Verify 95th percentile < 100ms
- [ ] Benchmark: Duplicate spawn detection time
- [ ] Verify 99th percentile < 1 second (NFR-P2)
- [ ] Results logged to `benchmarks/runtime_lock_results.txt`

**Dependencies:** Task 3.3

**Requirements Satisfied:**
- NFR-P1 (Lock Acquisition Time): <100ms validated
- NFR-P2 (Duplicate Spawn Detection): <1 second validated

---

### Task 3.5: Cross-Platform Testing

**Estimated Time:** 15 minutes

**Description:** Verify RuntimeLock works on macOS, Linux, and Windows (if available).

**Acceptance Criteria:**
- [ ] Run full test suite on macOS: All tests pass
- [ ] Run full test suite on Linux (CI/CD): All tests pass
- [ ] Run full test suite on Windows (if available): All tests pass or documented limitations
- [ ] Document any platform-specific behavior in README

**Dependencies:** Task 3.4

**Requirements Satisfied:**
- FR-004 (Cross-Platform): Validated on all platforms
- NFR-PO1 (Cross-Platform Consistency): Identical behavior

---

## Phase 3 Validation Gate

**Before proceeding to Phase 4:**
- [ ] All Task 3.1-3.5 acceptance criteria met ✅
- [ ] All unit tests pass (14+ tests) ✅
- [ ] All integration tests pass (4+ tests) ✅
- [ ] All stress tests pass (2+ tests) ✅
- [ ] All benchmarks meet targets ✅
- [ ] Code coverage: 100% for RuntimeLock ✅
- [ ] Cross-platform validation complete ✅

---

## Phase 4: Documentation

**Duration:** 30 minutes  
**Purpose:** Document RuntimeLock for users and developers

---

### Task 4.1: Update RuntimeLock Docstrings

**Estimated Time:** 10 minutes

**Description:** Ensure all docstrings are complete and accurate.

**Acceptance Criteria:**
- [ ] Class docstring complete (purpose, strategy, cleanup)
- [ ] All public methods have docstrings (purpose, params, returns, exceptions)
- [ ] All private methods have docstrings (purpose, implementation notes)
- [ ] Docstrings follow Google style guide
- [ ] Examples included in class docstring

**Dependencies:** Phase 3 complete

**Requirements Satisfied:**
- NFR-M1 (Code Quality): Comprehensive documentation

---

### Task 4.2: Update __main__.py Comments

**Estimated Time:** 5 minutes

**Description:** Add comments explaining RuntimeLock integration.

**Acceptance Criteria:**
- [ ] Comment above `RuntimeLock(base_path)`: Explain singleton enforcement
- [ ] Comment above lock acquisition: Explain lock order (runtime → init)
- [ ] Comment in finally block: Explain cleanup order

**Dependencies:** Task 4.1

**Requirements Satisfied:**
- NFR-M1 (Code Quality): Clear code comments

---

### Task 4.3: Create Standards Document

**Estimated Time:** 10 minutes

**Description:** Create standards doc for singleton enforcement pattern.

**Acceptance Criteria:**
- [ ] File created: `.praxis-os/standards/development/singleton-enforcement.md`
- [ ] Document explains three-layer lock architecture
- [ ] Document includes usage examples
- [ ] Document includes troubleshooting guide (how to remove stale locks manually)
- [ ] Document references RuntimeLock, InitLock, IndexLockManager

**Dependencies:** Task 4.2

**Requirements Satisfied:**
- NFR-O2 (Actionable Error Messages): Troubleshooting guide

---

### Task 4.4: Update CHANGELOG

**Estimated Time:** 5 minutes

**Description:** Add RuntimeLock to changelog.

**Acceptance Criteria:**
- [ ] Entry added to `CHANGELOG.md` under "Unreleased" section
- [ ] Entry format: `### Added - RuntimeLock: Singleton MCP server enforcement`
- [ ] Entry includes brief description and benefits
- [ ] Entry references issue/PR number (if applicable)

**Dependencies:** Task 4.3

**Requirements Satisfied:**
- Documentation completeness

---

## Phase 4 Validation Gate

**Before marking complete:**
- [ ] All Task 4.1-4.4 acceptance criteria met ✅
- [ ] All documentation reviewed for accuracy ✅
- [ ] Standards document published ✅
- [ ] CHANGELOG updated ✅

---

## Final Validation

**Before deployment:**
- [ ] All 4 phases complete ✅
- [ ] All 20 tasks complete ✅
- [ ] All acceptance criteria met ✅
- [ ] All tests pass (20+ tests) ✅
- [ ] Code coverage: 100% for RuntimeLock ✅
- [ ] Performance benchmarks meet targets ✅
- [ ] Cross-platform validation complete ✅
- [ ] Documentation complete ✅
- [ ] No regressions in existing functionality ✅
- [ ] Ready for deployment ✅

---

## Task Dependencies (Summary)

```
Phase 1: RuntimeLock Implementation
  1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6 → 1.7 → 1.8

Phase 2: Integration
  Phase 1 → 2.1 → 2.2 → 2.3 → 2.4 → 2.5

Phase 3: Testing
  Phase 2 → 3.1 → 3.2 → 3.3 → 3.4 → 3.5

Phase 4: Documentation
  Phase 3 → 4.1 → 4.2 → 4.3 → 4.4
```

**Critical Path:** 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6 → 2.3 → 3.1 → 3.2 → 4.1

---

## Time Estimates (Summary)

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1 | 8 | 2.5 hours |
| Phase 2 | 5 | 30 minutes |
| Phase 3 | 5 | 1.5 hours |
| Phase 4 | 4 | 30 minutes |
| **Total** | **22** | **5 hours** |

**Note:** Phase 1 increased from 2 hours to 2.5 hours to include security fixes:
- Timestamp validation (PID reuse mitigation)
- Retry limit (infinite loop prevention)
- Disk full handling
- Directory DoS mitigation

---

## Requirements Traceability

All tasks trace back to requirements from `srd.md`:

| Requirement | Tasks |
|-------------|-------|
| FR-001 (Singleton Enforcement) | 1.3, 1.6, 2.3, 3.1, 3.2 |
| FR-002 (Stale Lock Detection) | 1.4, 1.5, 1.6, 2.5, 3.2 |
| FR-003 (Graceful Degradation) | 1.4, 1.6 |
| FR-004 (Cross-Platform) | 1.5, 3.5 |
| FR-005 (Lock Lifecycle) | 1.2, 1.6, 1.7, 1.8, 2.2, 2.3, 2.4 |
| FR-006 (Observability) | 1.6, 1.7, 2.3 |
| FR-007 (Lock File Location) | 1.2, 1.3 |
| FR-008 (Integration) | 2.1, 2.2, 2.3, 2.4 |
| NFR-R1 (Zero False Positives) | 1.5, 1.6 |
| NFR-R2 (Stale Lock Detection Accuracy) | 3.3 |
| NFR-P1 (Lock Acquisition Time) | 1.6, 3.4 |
| NFR-P2 (Duplicate Spawn Detection) | 2.5, 3.3, 3.4 |
| NFR-M1 (Code Quality) | 1.1, 4.1, 4.2 |
| NFR-M2 (Type Safety) | 1.1 |
| NFR-M3 (Test Coverage) | 3.1 |
| NFR-C1 (No Breaking Changes) | 2.4 |
| NFR-PO1 (Cross-Platform Consistency) | 3.5 |
| NFR-O2 (Actionable Error Messages) | 4.3 |

---


