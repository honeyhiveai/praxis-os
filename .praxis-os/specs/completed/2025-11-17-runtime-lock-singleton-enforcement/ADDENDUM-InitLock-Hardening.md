# ADDENDUM: InitLock Security Hardening

**Date:** 2025-11-17  
**Parent Spec:** Lock Security & Singleton Enforcement  
**Scope:** Apply RuntimeLock v1.2 security mitigations to existing InitLock  
**Priority:** Critical  
**Estimated Time:** 2 hours

---

## Executive Summary

**Problem:** Security audit revealed that InitLock lacks critical security mitigations discovered during RuntimeLock design: PID reuse detection, disk full handling, directory DoS mitigation, and retry limits.

**Solution:** Apply all RuntimeLock v1.2 security patterns to InitLock, bringing it to the same security standard.

**Impact:**
- **Security:** Prevents PID reuse attacks (false positives blocking valid servers)
- **Reliability:** Handles disk full gracefully (no corrupted lock files)
- **Robustness:** Prevents directory DoS attacks
- **Maintainability:** Consistent security patterns across all locks

---

## Security Audit Summary

| Mitigation | RuntimeLock v1.2 | InitLock (Current) | Gap Severity |
|------------|------------------|---------------------|--------------|
| **PID Reuse (Process Name)** | ✅ `_get_process_cmdline()` | ❌ None | **CRITICAL** |
| **PID Reuse (Timestamp)** | ✅ 24-hour timeout | ❌ None | **HIGH** |
| **Disk Full Handling** | ✅ Write verification + cleanup | ❌ None | **HIGH** |
| **Directory DoS** | ✅ `IsADirectoryError` handling | ❌ None | **MEDIUM** |
| **Retry Limit** | ✅ Max 3 retries | ❌ Infinite loop (timeout only) | **MEDIUM** |
| **Lock File Format** | ✅ "PID TIMESTAMP" | ❌ "PID" only | **HIGH** |

**Overall Grade:** InitLock: **C** → Target: **A+**

---

## Requirements

### FR-009: PID Reuse Detection (Process Name Verification)

**Priority:** Critical

**Description:** InitLock must verify that a PID belongs to an ouroboros process, not a reused PID from a different process.

**Acceptance Criteria:**
- [ ] Add `_get_process_cmdline(pid)` static method (identical to RuntimeLock)
- [ ] Update `_is_process_running(pid)` to check process name
- [ ] If PID exists but is NOT ouroboros → return `False` (stale lock)
- [ ] If cannot verify process name → return `True` (conservative, NFR-R1)
- [ ] Works on Linux (via `/proc`), macOS (via `ps`), WSL2

**Traceability:**
- Addresses PID reuse attack (false positives blocking valid servers)
- Aligns with RuntimeLock v1.2 security pattern

---

### FR-010: PID Reuse Detection (Timestamp Validation)

**Priority:** High

**Description:** InitLock must include a timestamp in the lock file to detect long-term PID reuse (belt-and-suspenders with process name verification).

**Acceptance Criteria:**
- [ ] Change lock file format from `"PID"` to `"PID TIMESTAMP"`
- [ ] Update `_try_claim_lock()` to write PID + timestamp
- [ ] Update `_read_lock_holder()` to return `(pid, timestamp)` tuple
- [ ] Add timestamp validation in `acquire()`: if lock >24 hours old, assume stale
- [ ] Backward compatible: old format `"PID"` treated as corrupted → removed → retry

**Traceability:**
- Secondary defense against PID reuse (primary: process name)
- Aligns with RuntimeLock v1.2 security pattern

---

### FR-011: Disk Full Handling

**Priority:** High

**Description:** InitLock must detect disk full conditions during lock file creation and cleanup partial files.

**Acceptance Criteria:**
- [ ] Verify bytes written after `os.write()` in `_try_claim_lock()`
- [ ] If bytes written < expected → log error, cleanup file, return `False`
- [ ] Handle partial file creation gracefully (no corrupted lock files)

**Traceability:**
- Prevents corrupted lock files from disk full
- Aligns with RuntimeLock v1.2 security pattern

---

### FR-012: Directory DoS Mitigation

**Priority:** Medium

**Description:** InitLock must detect and remove directories created at the lock file path (DoS attack prevention).

**Acceptance Criteria:**
- [ ] Handle `IsADirectoryError` in `_try_claim_lock()`
- [ ] If directory exists at lock path → log error, remove directory, return `False`
- [ ] Cleanup directory using `shutil.rmtree()`

**Traceability:**
- Prevents DoS attack via directory at lock path
- Aligns with RuntimeLock v1.2 security pattern

---

### FR-013: Retry Limit

**Priority:** Medium

**Description:** InitLock must limit retries to prevent infinite loops if lock operations fail repeatedly.

**Acceptance Criteria:**
- [ ] Add `_retry_count` parameter to `acquire()` method
- [ ] Max 3 retries (same as RuntimeLock)
- [ ] If max retries exceeded → log error, return `False`
- [ ] Log DEBUG message on each retry attempt

**Traceability:**
- Prevents infinite loops if `unlink()` fails repeatedly
- Aligns with RuntimeLock v1.2 security pattern

---

## Implementation Tasks

### Task 1: Add Process Name Verification (45 minutes)

**Subtasks:**
1. Copy `_get_process_cmdline()` from RuntimeLock to InitLock (10 min)
2. Update `_is_process_running()` to call `_get_process_cmdline()` (15 min)
3. Add process name check: if not "ouroboros" → return `False` (10 min)
4. Add conservative fallback: if cannot verify → return `True` (10 min)

**Acceptance Criteria:**
- [ ] `_get_process_cmdline()` tries `/proc` first, falls back to `ps`
- [ ] `_is_process_running()` checks PID exists AND is ouroboros
- [ ] Unit tests pass: `test_is_process_running_pid_reused()`

---

### Task 2: Add Timestamp to Lock File (30 minutes)

**Subtasks:**
1. Update `_try_claim_lock()` to write `"PID TIMESTAMP"` format (10 min)
2. Update `_read_lock_holder()` to return `(pid, timestamp)` tuple (10 min)
3. Add backward compatibility: old format treated as corrupted (10 min)

**Acceptance Criteria:**
- [ ] Lock file format: `"12345 1700000000"`
- [ ] `_read_lock_holder()` returns `(int, int)` or `None`
- [ ] Old format `"12345"` returns `None` (triggers cleanup)

---

### Task 3: Add Timestamp Validation (15 minutes)

**Subtasks:**
1. Add timestamp age calculation in `acquire()` (5 min)
2. If lock >24 hours old → log warning, remove, retry (10 min)

**Acceptance Criteria:**
- [ ] Locks older than 24 hours are removed
- [ ] Log warning: "Lock is X hours old, assuming stale"
- [ ] Unit test passes: `test_acquire_stale_lock_old_timestamp()`

---

### Task 4: Add Disk Full Handling (15 minutes)

**Subtasks:**
1. Add write verification in `_try_claim_lock()` (10 min)
2. Cleanup partial file on error (5 min)

**Acceptance Criteria:**
- [ ] Verify `bytes_written == len(content)`
- [ ] If mismatch → log error, `unlink()`, return `False`
- [ ] Unit test passes: `test_try_claim_lock_disk_full()`

---

### Task 5: Add Directory DoS and Retry Limit (15 minutes)

**Subtasks:**
1. Add `IsADirectoryError` handling in `_try_claim_lock()` (10 min)
2. Add `_retry_count` parameter to `acquire()` (5 min)

**Acceptance Criteria:**
- [ ] `IsADirectoryError` → log error, `rmtree()`, return `False`
- [ ] `_retry_count >= 3` → log error, return `False`
- [ ] Unit tests pass: `test_try_claim_lock_directory_dos()`, `test_acquire_max_retries()`

---

## Test Cases

### TC-IL001: Process Name Verification (PID Reused)

**Objective:** Verify InitLock detects PID reuse via process name.

**Steps:**
1. Find PID of running non-ouroboros process (e.g., `bash`)
2. Create lock file with that PID + current timestamp
3. Call `acquire()`
4. Verify `_is_process_running()` returns `False` (PID reused)
5. Verify lock file removed, new lock created

**Expected:** Lock acquired, old lock removed

---

### TC-IL002: Process Name Verification (Cannot Verify)

**Objective:** Verify InitLock assumes process is valid if cannot verify.

**Steps:**
1. Mock `_get_process_cmdline()` to return `None`
2. Call `acquire()`
3. Verify `_is_process_running()` returns `True` (conservative)
4. Verify `acquire()` returns `False` (lock held)

**Expected:** Conservative behavior (NFR-R1)

---

### TC-IL003: Timestamp Validation (Old Lock)

**Objective:** Verify InitLock removes locks older than 24 hours.

**Steps:**
1. Create lock file with PID + timestamp from 25 hours ago
2. Call `acquire()`
3. Verify lock age calculated as >24 hours
4. Verify lock file removed, new lock created

**Expected:** Old lock removed, new lock acquired

---

### TC-IL004: Disk Full Handling

**Objective:** Verify InitLock handles disk full gracefully.

**Steps:**
1. Mock `os.write()` to return 0 (disk full)
2. Call `_try_claim_lock()`
3. Verify partial file is removed
4. Verify returns `False`

**Expected:** Partial file cleaned up, no corruption

---

### TC-IL005: Directory DoS

**Objective:** Verify InitLock removes directory at lock path.

**Steps:**
1. Create directory at `.cache/.init.lock`
2. Call `_try_claim_lock()`
3. Verify `IsADirectoryError` caught
4. Verify directory removed
5. Verify returns `False` (retry)

**Expected:** Directory removed, no DoS

---

### TC-IL006: Retry Limit

**Objective:** Verify InitLock limits retries to 3.

**Steps:**
1. Mock `_try_claim_lock()` to always return `False`
2. Mock `_read_lock_holder()` to return `None` (corrupted)
3. Call `acquire()`
4. Verify max 3 retries attempted
5. Verify returns `False` after 3 retries

**Expected:** Max 3 retries, then fail

---

### TC-IL007: Backward Compatibility (Old Format)

**Objective:** Verify InitLock handles old lock file format.

**Steps:**
1. Create lock file with old format: `"12345"`
2. Call `acquire()`
3. Verify `_read_lock_holder()` returns `None` (cannot parse)
4. Verify lock file removed, new lock created with new format

**Expected:** Old lock removed, new lock uses `"PID TIMESTAMP"` format

---

### TC-IL008: Integration Test (All Mitigations)

**Objective:** Verify all mitigations work together.

**Steps:**
1. Test PID reuse detection
2. Test timestamp validation
3. Test disk full handling
4. Test directory DoS
5. Test retry limit

**Expected:** All mitigations work correctly

---

## Backward Compatibility

### Lock File Format Migration

**Old Format:** `"PID"` (e.g., `"47294"`)  
**New Format:** `"PID TIMESTAMP"` (e.g., `"47294 1700000000"`)

**Migration Strategy:**
1. `_read_lock_holder()` tries to parse new format first
2. If parse fails (old format or corrupted) → return `None`
3. `acquire()` treats `None` as corrupted lock → removes → retries
4. Next iteration creates lock with new format

**Impact:**
- **Zero downtime:** Old locks automatically migrated on next acquisition
- **No manual intervention:** Migration is automatic
- **No data loss:** Old locks are treated as stale (correct behavior)

---

## Code Changes Summary

**Files Modified:**
1. `.praxis-os/ouroboros/foundation/init_lock.py` (5 methods updated, 2 methods added)

**Lines of Code:**
- Added: ~80 lines (process name verification, timestamp handling, disk full, directory DoS)
- Modified: ~40 lines (acquire, _try_claim_lock, _read_lock_holder, _is_process_running)
- Total: ~120 LOC changes

**Dependencies:**
- Added: `import subprocess` (for `ps` command fallback)
- Added: `import time` (for timestamp)
- Added: `import shutil` (for `rmtree`)

---

## Testing Summary

**New Tests:** 8 test cases (TC-IL001 to TC-IL008)  
**Estimated Test Time:** 15 minutes  
**Coverage Target:** 100% line coverage for modified code

---

## Rollout Plan

### Phase 1: Implementation (2 hours)
1. Add process name verification (45 min)
2. Add timestamp to lock file (30 min)
3. Add timestamp validation (15 min)
4. Add disk full handling (15 min)
5. Add directory DoS and retry limit (15 min)

### Phase 2: Testing (30 minutes)
1. Unit tests (8 new tests)
2. Integration test (all mitigations)

### Phase 3: Deployment (Immediate)
- No migration needed (automatic on next server start)
- Old locks automatically cleaned up

---

## Success Criteria

- [ ] All 8 test cases pass
- [ ] 100% line coverage for modified code
- [ ] No regressions in existing InitLock functionality
- [ ] InitLock security grade: C → A+
- [ ] Consistent security patterns with RuntimeLock

---

## Traceability

**Parent Spec:** Lock Security & Singleton Enforcement  
**Related Specs:**
- RuntimeLock v1.2 (security patterns source)
- Security Audit (`.praxis-os/workspace/analysis/2025-11-17-existing-locks-security-audit.md`)

**Requirements Addressed:**
- FR-009: PID Reuse Detection (Process Name)
- FR-010: PID Reuse Detection (Timestamp)
- FR-011: Disk Full Handling
- FR-012: Directory DoS Mitigation
- FR-013: Retry Limit

---

**Status:** ✅ Specification Complete - Ready for Implementation

