# Testing Documentation

**Project:** RuntimeLock - Singleton MCP Server Enforcement  
**Date:** 2025-11-17

---

## Overview

This directory contains comprehensive testing documentation for RuntimeLock, ensuring 100% requirements coverage and validation of all functional and non-functional requirements.

**Contents:**
1. Requirements List (all FRs and NFRs)
2. Functional Test Cases (FR validation)
3. Non-Functional Test Cases (NFR validation)
4. Test Strategy (unit, integration, stress, benchmarks)
5. Traceability Matrix (requirements → tests)

---

## 1. Requirements List

### Functional Requirements (from srd.md)

| ID | Requirement | Priority | Test Coverage |
|----|-------------|----------|---------------|
| FR-001 | Singleton Enforcement | Critical | TC-F001, TC-F002, TC-I001, TC-S001 |
| FR-002 | Stale Lock Detection | Critical | TC-F003, TC-F004, TC-I002 |
| FR-003 | Graceful Degradation | High | TC-F005, TC-F006, TC-F007 |
| FR-004 | Cross-Platform Support | High | TC-N007, TC-N008 |
| FR-005 | Lock Lifecycle Management | Critical | TC-F008, TC-F009, TC-F010 |
| FR-006 | Observability | High | TC-F011, TC-F012 |
| FR-007 | Lock File Location | Medium | TC-F013 |
| FR-008 | Integration with Existing Locks | Critical | TC-I003 |

### Non-Functional Requirements (from srd.md)

| ID | Requirement | Target | Test Coverage |
|----|-------------|--------|---------------|
| NFR-R1 | Zero False Positives | 0 per month | TC-N001 |
| NFR-R2 | Stale Lock Detection Accuracy | 100% | TC-N002 |
| NFR-P1 | Lock Acquisition Time | <100ms | TC-B001 |
| NFR-P2 | Duplicate Spawn Detection Time | <1 second | TC-B002 |
| NFR-M1 | Code Quality | <200 LOC | TC-N003 |
| NFR-M2 | Type Safety | 100% type hints | TC-N004 |
| NFR-M3 | Test Coverage | 100% line coverage | TC-N005 |
| NFR-C1 | No Breaking Changes | All existing tests pass | TC-N006 |
| NFR-C2 | Lock Layer Independence | No shared state | TC-I003 |
| NFR-PO1 | Cross-Platform Consistency | All platforms | TC-N007 |
| NFR-PO2 | Platform-Appropriate Primitives | Native OS calls | TC-N008 |
| NFR-O1 | Comprehensive Logging | All operations logged | TC-F011 |
| NFR-O2 | Actionable Error Messages | Remediation guidance | TC-F012 |

---

## 2. Functional Test Cases

### TC-F001: Normal Lock Acquisition

**Requirement:** FR-001 (Singleton Enforcement)

**Objective:** Verify RuntimeLock can be acquired when no other server is running.

**Preconditions:**
- No lock file exists at `.praxis-os/.cache/.runtime.lock`
- No other MCP server is running

**Test Steps:**
1. Create RuntimeLock instance with valid base_path
2. Call `acquire()`
3. Verify return value is `True`
4. Verify `acquired` flag is `True`
5. Verify lock file exists with current PID

**Expected Results:**
- `acquire()` returns `True`
- Lock file created at `.praxis-os/.cache/.runtime.lock`
- Lock file contains current process PID
- Log message: "Runtime lock acquired (PID {pid})"

**Pass/Fail Criteria:** All expected results met

---

### TC-F002: Duplicate Spawn Detection

**Requirement:** FR-001 (Singleton Enforcement)

**Objective:** Verify second server detects first server and exits gracefully.

**Preconditions:**
- First MCP server is running with RuntimeLock acquired

**Test Steps:**
1. Start first server (Server A)
2. Verify Server A acquires lock
3. Start second server (Server B) while Server A is running
4. Verify Server B's `acquire()` returns `False`
5. Verify Server B exits with code 0
6. Verify only Server A remains running

**Expected Results:**
- Server A: `acquire()` returns `True`, continues running
- Server B: `acquire()` returns `False`, exits gracefully
- Server B log: "Another MCP server is running (PID {A_pid})"
- Only 1 server process remains (`ps aux | grep ouroboros | wc -l` = 1)

**Pass/Fail Criteria:** All expected results met

---

### TC-F003: Stale Lock Detection (Dead PID)

**Requirement:** FR-002 (Stale Lock Detection)

**Objective:** Verify RuntimeLock detects and cleans up stale locks from dead processes.

**Preconditions:**
- Lock file exists with PID 99999 and timestamp (dead process)

**Test Steps:**
1. Create lock file with PID 99999: `echo "99999 1700000000" > .cache/.runtime.lock`
2. Create RuntimeLock instance
3. Call `acquire()`
4. Verify `_is_process_running(99999)` returns `False` (PID doesn't exist)
5. Verify stale lock file is removed
6. Verify new lock file is created with current PID

**Expected Results:**
- `acquire()` returns `True`
- Old lock file (PID 99999) removed
- New lock file created with current PID and timestamp
- Log message: "Stale runtime lock (PID 99999)"

**Pass/Fail Criteria:** All expected results met

---

### TC-F003b: Stale Lock Detection (PID Reused)

**Requirement:** FR-002 (Stale Lock Detection), Security (PID Reuse Mitigation)

**Objective:** Verify RuntimeLock detects PID reuse via process name verification.

**Preconditions:**
- Lock file exists with PID of a running non-ouroboros process (e.g., `bash`)

**Test Steps:**
1. Find PID of a running non-ouroboros process: `pgrep bash | head -1`
2. Create lock file with that PID: `echo "{bash_pid} {current_timestamp}" > .cache/.runtime.lock`
3. Create RuntimeLock instance
4. Call `acquire()`
5. Verify `_get_process_cmdline(bash_pid)` returns command line containing "bash"
6. Verify `_is_process_running(bash_pid)` returns `False` (PID exists but not ouroboros)
7. Verify stale lock file is removed
8. Verify new lock file is created with current PID

**Expected Results:**
- `acquire()` returns `True`
- Old lock file (bash PID) removed
- New lock file created with current PID
- Log warning: "PID {bash_pid} is not ouroboros (cmd='...')"
- Log info: "Stale runtime lock (PID {bash_pid})"

**Pass/Fail Criteria:** All expected results met

---

### TC-F003c: Process Name Verification (Cannot Verify)

**Requirement:** FR-002 (Stale Lock Detection), NFR-R1 (Zero False Positives)

**Objective:** Verify RuntimeLock assumes process is valid if cannot verify process name.

**Preconditions:**
- Lock file exists with PID of a running process
- `/proc/{pid}/cmdline` is unreadable (permission denied)
- `ps` command fails (mock scenario)

**Test Steps:**
1. Create lock file with valid PID
2. Mock `_get_process_cmdline()` to return `None` (cannot read)
3. Call `acquire()`
4. Verify `_is_process_running()` returns `True` (conservative)
5. Verify `acquire()` returns `False` (lock held)

**Expected Results:**
- `acquire()` returns `False` (assume lock is held)
- Log debug: "Cannot verify process name for PID {pid} (assuming valid)"
- Conservative behavior (NFR-R1: Zero False Positives)

**Pass/Fail Criteria:** All expected results met

---

### TC-F004: Stale Lock Detection (Corrupted File)

**Requirement:** FR-002 (Stale Lock Detection), FR-003 (Graceful Degradation)

**Objective:** Verify RuntimeLock handles corrupted lock files gracefully.

**Preconditions:**
- Lock file exists with invalid content (e.g., "abc123")

**Test Steps:**
1. Create corrupted lock file: `echo "abc123" > .cache/.runtime.lock`
2. Create RuntimeLock instance
3. Call `acquire()`
4. Verify `_read_lock_holder()` returns `None`
5. Verify corrupted lock file is removed
6. Verify new lock file is created with current PID and timestamp

**Expected Results:**
- `acquire()` returns `True`
- Corrupted lock file removed
- New lock file created with current PID and timestamp
- Log warning about corrupted file

**Pass/Fail Criteria:** All expected results met

---

### TC-F004b: Stale Lock Detection (Old Timestamp)

**Requirement:** FR-002 (Stale Lock Detection), Security (PID Reuse Mitigation)

**Objective:** Verify RuntimeLock detects locks older than 24 hours as stale.

**Preconditions:**
- Lock file exists with valid PID but old timestamp (>24 hours ago)

**Test Steps:**
1. Calculate timestamp from 25 hours ago: `old_ts = int(time.time()) - (25 * 3600)`
2. Create lock file with current PID but old timestamp: `echo "{current_pid} {old_ts}" > .cache/.runtime.lock`
3. Create RuntimeLock instance
4. Call `acquire()`
5. Verify lock age calculated as >24 hours
6. Verify lock file is removed (assumed stale)
7. Verify new lock file is created with current PID and fresh timestamp

**Expected Results:**
- `acquire()` returns `True`
- Old lock file removed
- New lock file created with fresh timestamp
- Log warning: "Lock is 25 hours old (PID {pid}), assuming stale"

**Pass/Fail Criteria:** All expected results met

---

### TC-F005: Missing Lock Directory

**Requirement:** FR-003 (Graceful Degradation)

**Objective:** Verify RuntimeLock creates `.cache/` directory if missing.

**Preconditions:**
- `.cache/` directory does not exist

**Test Steps:**
1. Delete `.cache/` directory: `rm -rf .praxis-os/.cache`
2. Create RuntimeLock instance
3. Verify `.cache/` directory is created in `__init__()`
4. Call `acquire()`
5. Verify lock file is created

**Expected Results:**
- `.cache/` directory created automatically
- Lock file created at `.praxis-os/.cache/.runtime.lock`
- No exceptions raised

**Pass/Fail Criteria:** All expected results met

---

### TC-F006: Lock File Unreadable

**Requirement:** FR-003 (Graceful Degradation)

**Objective:** Verify RuntimeLock handles unreadable lock files gracefully.

**Preconditions:**
- Lock file exists but is unreadable (permissions 0o000)

**Test Steps:**
1. Create lock file with no permissions: `touch .cache/.runtime.lock && chmod 000 .cache/.runtime.lock`
2. Create RuntimeLock instance
3. Call `acquire()`
4. Verify `_read_lock_holder()` returns `None`
5. Verify RuntimeLock assumes lock is held (safer default)

**Expected Results:**
- `acquire()` returns `False` (assume lock is held)
- Log warning about unreadable file
- No exceptions raised

**Pass/Fail Criteria:** All expected results met

---

### TC-F007: PID Check Fails

**Requirement:** FR-003 (Graceful Degradation), NFR-R1 (Zero False Positives)

**Objective:** Verify RuntimeLock assumes process is alive if PID check fails.

**Preconditions:**
- Lock file exists with valid PID
- `os.kill()` raises unexpected exception (mock scenario)

**Test Steps:**
1. Create lock file with valid PID
2. Mock `os.kill()` to raise unexpected exception
3. Call `acquire()`
4. Verify `_is_process_running()` returns `True` (safer default)
5. Verify `acquire()` returns `False`

**Expected Results:**
- `acquire()` returns `False` (assume lock is held)
- No exceptions raised
- Conservative behavior (NFR-R1)

**Pass/Fail Criteria:** All expected results met

---

### TC-F008: Lock Lifecycle (Acquire → Hold → Release)

**Requirement:** FR-005 (Lock Lifecycle Management)

**Objective:** Verify complete lock lifecycle from acquisition to release.

**Preconditions:**
- No lock file exists

**Test Steps:**
1. Create RuntimeLock instance
2. Call `acquire()` → verify `True`, lock file created
3. Verify lock is held (file exists with current PID)
4. Call `release()` → verify lock file deleted
5. Verify `acquired` flag is `False`

**Expected Results:**
- Lock acquired successfully
- Lock held (file exists)
- Lock released successfully (file deleted)
- `acquired` flag transitions: `False` → `True` → `False`

**Pass/Fail Criteria:** All expected results met

---

### TC-F009: Atexit Handler Cleanup

**Requirement:** FR-005 (Lock Lifecycle Management)

**Objective:** Verify atexit handler releases lock on process exit.

**Preconditions:**
- RuntimeLock acquired

**Test Steps:**
1. Spawn subprocess with RuntimeLock acquisition
2. Subprocess exits normally (no explicit `release()` call)
3. Verify lock file is removed by atexit handler
4. Verify new process can acquire lock

**Expected Results:**
- Lock file removed on subprocess exit
- New process acquires lock successfully
- Atexit handler executed

**Pass/Fail Criteria:** All expected results met

---

### TC-F010: Lock Acquisition Order (Runtime → Init)

**Requirement:** FR-005 (Lock Lifecycle Management), FR-008 (Integration)

**Objective:** Verify RuntimeLock is acquired before InitLock in __main__.py.

**Preconditions:**
- Server starting up

**Test Steps:**
1. Add logging to track lock acquisition order
2. Start server
3. Verify RuntimeLock.acquire() called before InitLock.acquire()
4. Verify both locks acquired successfully
5. Verify server runs normally

**Expected Results:**
- Log order: "Runtime lock acquired" → "Init lock acquired"
- Both locks held during server runtime
- InitLock released after init, RuntimeLock held until shutdown

**Pass/Fail Criteria:** All expected results met

---

### TC-F011: Observability (Logging)

**Requirement:** FR-006 (Observability), NFR-O1 (Comprehensive Logging)

**Objective:** Verify all lock operations are logged with sufficient detail.

**Preconditions:**
- Logging enabled at INFO level

**Test Steps:**
1. Acquire lock → verify log: "Runtime lock acquired (PID {pid})"
2. Attempt duplicate spawn → verify log: "Another MCP server is running (PID {holder_pid})"
3. Detect stale lock → verify log: "Stale runtime lock (dead PID {dead_pid})"
4. Release lock → verify log: "Runtime lock released (PID {pid})"

**Expected Results:**
- All operations logged at INFO level
- All log messages include relevant PIDs
- Log messages are clear and actionable

**Pass/Fail Criteria:** All expected results met

---

### TC-F012: Actionable Error Messages

**Requirement:** FR-006 (Observability), NFR-O2 (Actionable Error Messages)

**Objective:** Verify error messages include remediation guidance.

**Preconditions:**
- Various error scenarios (stale lock, corrupted file, etc.)

**Test Steps:**
1. Trigger stale lock scenario
2. Verify log message explains what happened and what was done
3. Trigger corrupted file scenario
4. Verify log message is actionable

**Expected Results:**
- Error messages explain the problem clearly
- Error messages indicate what action was taken
- Users can understand and resolve issues without developer help

**Pass/Fail Criteria:** All expected results met

---

### TC-F013: Lock File Location and Permissions

**Requirement:** FR-007 (Lock File Location)

**Objective:** Verify lock file is created in correct location with correct permissions and format.

**Preconditions:**
- No lock file exists

**Test Steps:**
1. Acquire lock
2. Verify lock file path: `.praxis-os/.cache/.runtime.lock`
3. Verify lock file permissions: `0o600` (owner read/write only)
4. Verify lock file content: Current PID and timestamp as UTF-8 text
5. Verify format: "PID TIMESTAMP" (e.g., "47294 1700000000")

**Expected Results:**
- Lock file at `.praxis-os/.cache/.runtime.lock`
- Permissions: `0o600`
- Content: Single line with PID and timestamp (e.g., "47294 1700000000")
- Both PID and timestamp are valid integers

**Pass/Fail Criteria:** All expected results met

---

### TC-F014: Process Name Verification (_get_process_cmdline)

**Requirement:** FR-002 (Stale Lock Detection), Security (PID Reuse Mitigation)

**Objective:** Verify `_get_process_cmdline()` correctly retrieves process command line.

**Preconditions:**
- Various processes running (ouroboros, bash, etc.)

**Test Steps:**
1. Get current process PID: `os.getpid()`
2. Call `_get_process_cmdline(current_pid)`
3. Verify result contains "ouroboros" or "python"
4. Find bash PID: `pgrep bash | head -1`
5. Call `_get_process_cmdline(bash_pid)`
6. Verify result contains "bash"
7. Call `_get_process_cmdline(99999)` (dead PID)
8. Verify result is `None`

**Expected Results:**
- Current process: Returns command line containing "ouroboros" or "python"
- Bash process: Returns command line containing "bash"
- Dead PID: Returns `None`
- On Linux/WSL2: Uses `/proc/{pid}/cmdline` (fast)
- On macOS: Falls back to `ps` command (~50ms)

**Pass/Fail Criteria:** All expected results met

---

## 3. Integration Test Cases

### TC-I001: Single Server Startup

**Requirement:** FR-001 (Singleton Enforcement)

**Objective:** Verify single server starts and runs normally with RuntimeLock.

**Test Steps:**
1. Start MCP server
2. Verify RuntimeLock acquired
3. Verify server initializes successfully
4. Verify server runs normally (responds to MCP requests)
5. Stop server
6. Verify lock file removed

**Expected Results:**
- Server starts successfully
- RuntimeLock acquired
- No errors in logs
- Lock file removed on shutdown

**Pass/Fail Criteria:** All expected results met

---

### TC-I002: Sequential Server Starts

**Requirement:** FR-002 (Stale Lock Detection)

**Objective:** Verify Server B can start after Server A exits.

**Test Steps:**
1. Start Server A
2. Verify Server A acquires lock
3. Stop Server A gracefully
4. Verify lock file removed
5. Start Server B
6. Verify Server B acquires lock successfully

**Expected Results:**
- Server A: Acquires lock, runs, releases lock on exit
- Server B: Acquires lock after Server A exits
- No stale locks remain

**Pass/Fail Criteria:** All expected results met

---

### TC-I003: Lock Layer Independence

**Requirement:** FR-008 (Integration), NFR-C2 (Lock Layer Independence)

**Objective:** Verify RuntimeLock, InitLock, and IndexLockManager operate independently.

**Test Steps:**
1. Start server
2. Verify RuntimeLock acquired (Layer 2)
3. Verify InitLock acquired (Layer 1)
4. Verify InitLock released after init
5. Verify RuntimeLock still held
6. Trigger index build
7. Verify IndexLockManager acquires per-index locks (Layer 3)
8. Verify no interference between lock layers

**Expected Results:**
- All three lock layers operate independently
- No shared state between layers
- No deadlocks or race conditions

**Pass/Fail Criteria:** All expected results met

---

## 4. Stress Test Cases

### TC-S001: Concurrent Spawns (10 Servers)

**Requirement:** FR-001 (Singleton Enforcement), NFR-P2 (Duplicate Spawn Detection)

**Objective:** Simulate Cursor's race condition with 10 concurrent spawns.

**Test Steps:**
1. Spawn 10 MCP servers simultaneously using `&` (background)
2. Wait for all spawns to complete
3. Count running servers: `ps aux | grep ouroboros | grep -v grep | wc -l`
4. Verify only 1 server is running
5. Verify 9 servers exited gracefully (exit code 0)
6. Verify logs show 9 duplicate spawn detections

**Expected Results:**
- Only 1 server running
- 9 servers exited within <1 second each
- No race conditions
- No index corruption

**Pass/Fail Criteria:** All expected results met

---

### TC-S002: Rapid Sequential Starts (20 Servers)

**Requirement:** FR-002 (Stale Lock Detection), NFR-R2 (Stale Lock Detection Accuracy)

**Objective:** Verify no stale locks remain after rapid start/stop cycles.

**Test Steps:**
1. Loop 20 times:
   a. Start server
   b. Wait 1 second
   c. Stop server (graceful)
2. Verify no stale lock files remain
3. Verify 100% cleanup rate

**Expected Results:**
- All 20 servers start and stop successfully
- No stale lock files remain
- 100% cleanup rate (NFR-R2)

**Pass/Fail Criteria:** All expected results met

---

## 5. Performance Benchmarks

### TC-B001: Lock Acquisition Time (Normal Case)

**Requirement:** NFR-P1 (Lock Acquisition Time)

**Target:** <100ms (95th percentile)

**Test Steps:**
1. Run 100 iterations:
   a. Acquire lock
   b. Measure time
   c. Release lock
2. Calculate 95th percentile latency
3. Verify <100ms

**Expected Results:**
- 95th percentile < 100ms
- Typical case: <1ms

**Pass/Fail Criteria:** 95th percentile < 100ms

---

### TC-B002: Lock Acquisition Time (Stale Lock Case)

**Requirement:** NFR-P1 (Lock Acquisition Time)

**Target:** <100ms (95th percentile)

**Test Steps:**
1. Run 100 iterations:
   a. Create stale lock (dead PID)
   b. Acquire lock (triggers stale detection + cleanup)
   c. Measure time
   d. Release lock
2. Calculate 95th percentile latency
3. Verify <100ms

**Expected Results:**
- 95th percentile < 100ms
- Typical case: <20ms

**Pass/Fail Criteria:** 95th percentile < 100ms

---

### TC-B003: Duplicate Spawn Detection Time

**Requirement:** NFR-P2 (Duplicate Spawn Detection Time)

**Target:** <1 second (99th percentile)

**Test Steps:**
1. Start Server A
2. Run 100 iterations:
   a. Start Server B (duplicate)
   b. Measure time from start to exit
   c. Verify Server B exited
3. Calculate 99th percentile latency
4. Verify <1 second

**Expected Results:**
- 99th percentile < 1 second
- Typical case: <50ms

**Pass/Fail Criteria:** 99th percentile < 1 second

---

## 6. Non-Functional Test Cases

### TC-N001: Zero False Positives

**Requirement:** NFR-R1 (Zero False Positives)

**Target:** 0 false positives per month

**Test Steps:**
1. Run 1000 iterations of normal lock acquisition
2. Verify no valid servers are incorrectly detected as stale
3. Run 100 iterations with long-running servers (>1 hour)
4. Verify no valid servers are killed

**Expected Results:**
- 0 false positives in 1000 iterations
- All valid servers continue running

**Pass/Fail Criteria:** 0 false positives

---

### TC-N002: Stale Lock Detection Accuracy

**Requirement:** NFR-R2 (Stale Lock Detection Accuracy)

**Target:** 100% detection rate

**Test Steps:**
1. Create 100 stale locks (dead PIDs)
2. Attempt to acquire lock 100 times
3. Verify all 100 stale locks are detected and cleaned up

**Expected Results:**
- 100/100 stale locks detected
- 100% detection rate

**Pass/Fail Criteria:** 100% detection rate

---

### TC-N003: Code Quality (LOC)

**Requirement:** NFR-M1 (Code Quality)

**Target:** <200 LOC for RuntimeLock class

**Test Steps:**
1. Count lines in `runtime_lock.py` (excluding comments and blank lines)
2. Verify <200 LOC

**Expected Results:**
- RuntimeLock class: <200 LOC

**Pass/Fail Criteria:** <200 LOC

---

### TC-N004: Type Safety

**Requirement:** NFR-M2 (Type Safety)

**Target:** 100% type hints coverage

**Test Steps:**
1. Run `mypy runtime_lock.py`
2. Verify 0 errors
3. Verify all functions/methods have type hints

**Expected Results:**
- `mypy` passes with 0 errors
- 100% type hints coverage

**Pass/Fail Criteria:** `mypy` passes, 100% coverage

---

### TC-N005: Test Coverage

**Requirement:** NFR-M3 (Test Coverage)

**Target:** 100% line coverage for RuntimeLock class

**Test Steps:**
1. Run `pytest --cov=runtime_lock --cov-report=term-missing`
2. Verify 100% line coverage

**Expected Results:**
- 100% line coverage
- All branches covered

**Pass/Fail Criteria:** 100% line coverage

---

### TC-N006: No Breaking Changes

**Requirement:** NFR-C1 (No Breaking Changes)

**Target:** All existing tests pass

**Test Steps:**
1. Run full test suite (all existing tests)
2. Verify 0 failures
3. Verify no regressions in existing functionality

**Expected Results:**
- All existing tests pass
- No regressions

**Pass/Fail Criteria:** 0 test failures

---

### TC-N007: Cross-Platform Consistency (macOS, Linux, Windows)

**Requirement:** NFR-PO1 (Cross-Platform Consistency)

**Target:** Identical behavior on all platforms

**Test Steps:**
1. Run full test suite on macOS
2. Run full test suite on Linux (CI/CD)
3. Run full test suite on Windows (if available)
4. Verify all tests pass on all platforms

**Expected Results:**
- All tests pass on macOS
- All tests pass on Linux
- All tests pass on Windows (or documented limitations)

**Pass/Fail Criteria:** All tests pass on all platforms

---

### TC-N008: Platform-Appropriate Primitives

**Requirement:** NFR-PO2 (Platform-Appropriate Primitives)

**Target:** Use native OS primitives

**Test Steps:**
1. Verify `os.open()` with `O_CREAT | O_EXCL` used on all platforms
2. Verify `os.kill(pid, 0)` used on Unix/Linux/macOS
3. Verify Windows-specific PID checking (if implemented)
4. Verify no platform-specific workarounds or hacks

**Expected Results:**
- Native OS primitives used
- No workarounds

**Pass/Fail Criteria:** Native primitives used on all platforms

---

## 7. Test Strategy

### 7.1 Unit Testing

**Scope:** All RuntimeLock methods

**Approach:**
- Fast, isolated tests
- Mock file system when needed (use `tmp_path` fixture)
- Test all code paths (happy path + error paths)
- Verify return values, side effects, logging

**Tools:**
- `pytest` for test execution
- `pytest-cov` for coverage
- `unittest.mock` for mocking

**Target:** 100% line coverage

---

### 7.2 Integration Testing

**Scope:** Multi-process scenarios, __main__.py integration

**Approach:**
- Real file system
- Subprocess spawns (actual MCP servers)
- Verify inter-process behavior
- Test lock acquisition order

**Tools:**
- `subprocess` module
- `pytest` for test execution

**Target:** All integration scenarios covered

---

### 7.3 Stress Testing

**Scope:** Concurrent spawns, rapid sequential starts

**Approach:**
- Simulate Cursor's race condition
- Spawn 10+ servers simultaneously
- Verify only 1 runs
- Verify no stale locks remain

**Tools:**
- Shell scripts (`for` loops with `&`)
- `pytest` for assertions

**Target:** 100% success rate under stress

---

### 7.4 Performance Benchmarking

**Scope:** Lock acquisition time, duplicate spawn detection time

**Approach:**
- Measure latency (95th/99th percentile)
- Run 100+ iterations
- Verify targets met (NFR-P1, NFR-P2)

**Tools:**
- `time` module for measurements
- `pytest` for benchmarks

**Target:** All performance targets met

---

### 7.5 Cross-Platform Testing

**Scope:** macOS, Linux, Windows

**Approach:**
- Run full test suite on all platforms
- Verify consistent behavior
- Document platform-specific limitations (if any)

**Tools:**
- CI/CD (GitHub Actions) for Linux
- Manual testing on macOS, Windows

**Target:** All tests pass on all platforms

---

## 8. Traceability Matrix

**Requirements → Test Cases:**

| Requirement | Test Cases |
|-------------|------------|
| FR-001 | TC-F001, TC-F002, TC-I001, TC-S001 |
| FR-002 | TC-F003, TC-F004, TC-I002, TC-S002 |
| FR-003 | TC-F005, TC-F006, TC-F007 |
| FR-004 | TC-N007, TC-N008 |
| FR-005 | TC-F008, TC-F009, TC-F010 |
| FR-006 | TC-F011, TC-F012 |
| FR-007 | TC-F013 |
| FR-008 | TC-F010, TC-I003 |
| NFR-R1 | TC-F007, TC-N001 |
| NFR-R2 | TC-N002, TC-S002 |
| NFR-P1 | TC-B001, TC-B002 |
| NFR-P2 | TC-B003, TC-S001 |
| NFR-M1 | TC-N003 |
| NFR-M2 | TC-N004 |
| NFR-M3 | TC-N005 |
| NFR-C1 | TC-N006 |
| NFR-C2 | TC-I003 |
| NFR-PO1 | TC-N007 |
| NFR-PO2 | TC-N008 |
| NFR-O1 | TC-F011 |
| NFR-O2 | TC-F012 |

**Coverage:** 100% (all requirements have test cases)

---

## 9. Test Execution Summary

**Total Test Cases:** 35
- Functional: 17 (includes process name verification tests)
- Integration: 3
- Stress: 2
- Benchmarks: 3
- Non-Functional: 8
- Cross-Platform: 2

**Estimated Execution Time:**
- Unit Tests: 5 minutes
- Integration Tests: 10 minutes
- Stress Tests: 5 minutes
- Benchmarks: 10 minutes
- Cross-Platform: 15 minutes (per platform)
- **Total:** ~45 minutes (single platform), ~90 minutes (all platforms)

**Success Criteria:**
- All 35 test cases pass
- 100% line coverage for RuntimeLock
- All performance targets met
- No regressions in existing functionality
- Process name verification works on Linux, macOS, and WSL2

---


