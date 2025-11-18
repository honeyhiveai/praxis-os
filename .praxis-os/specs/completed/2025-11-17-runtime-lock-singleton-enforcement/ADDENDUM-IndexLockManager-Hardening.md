# ADDENDUM: IndexLockManager Security Hardening

**Date:** 2025-11-17  
**Parent Spec:** Lock Security & Singleton Enforcement  
**Scope:** Add directory DoS mitigation to IndexLockManager  
**Priority:** Medium  
**Estimated Time:** 30 minutes (included in InitLock 2-hour estimate)

---

## Executive Summary

**Problem:** IndexLockManager lacks directory DoS mitigation. If a directory exists at the lock file path, `open()` raises `IsADirectoryError`, preventing index operations.

**Solution:** Add `IsADirectoryError` handling in `_acquire_lock()` to detect and remove directories at the lock path.

**Impact:**
- **Robustness:** Prevents directory DoS attacks on index operations
- **Consistency:** Aligns with RuntimeLock and InitLock security patterns

**Note:** IndexLockManager uses fcntl-based locking (kernel-managed), so it does NOT need PID reuse, disk full, or retry limit mitigations. This addendum only addresses the directory DoS issue.

---

## Security Audit Summary

| Mitigation | RuntimeLock v1.2 | IndexLockManager (Current) | Gap Severity |
|------------|------------------|----------------------------|--------------|
| **PID Reuse** | ✅ Process name + timestamp | ✅ N/A (fcntl, no PID stored) | N/A |
| **Disk Full** | ✅ Write verification | ✅ N/A (fcntl, kernel-managed) | N/A |
| **Directory DoS** | ✅ `IsADirectoryError` | ❌ None | **MEDIUM** |
| **Retry Limit** | ✅ Max 3 retries | ✅ N/A (fcntl, blocking/non-blocking) | N/A |

**Overall Grade:** IndexLockManager: **B** → Target: **A**

---

## Requirement

### FR-014: Directory DoS Mitigation

**Priority:** Medium

**Description:** IndexLockManager must detect and remove directories created at the lock file path.

**Acceptance Criteria:**
- [ ] Handle `IsADirectoryError` in `_acquire_lock()` method
- [ ] If directory exists at lock path → log error, remove directory
- [ ] Raise `ActionableError` with clear remediation guidance
- [ ] Cleanup directory using `shutil.rmtree()`

**Traceability:**
- Prevents DoS attack via directory at lock path
- Aligns with RuntimeLock and InitLock security patterns

---

## Implementation Task

### Task 1: Add Directory DoS Mitigation (30 minutes)

**File:** `.praxis-os/ouroboros/subsystems/rag/lock_manager.py`

**Current Code (lines 236-243):**
```python
try:
    # Open lock file (create if doesn't exist, mode 600 for security)
    self._lock_file = open(  # noqa: SIM115
        self.lock_file_path,
        mode="a",  # Append mode (create if missing)
    )
    # ... rest of method ...
except IOError as e:
    # Handle lock unavailable, permission denied, etc.
```

**Updated Code:**
```python
try:
    # Open lock file (create if doesn't exist, mode 600 for security)
    self._lock_file = open(  # noqa: SIM115
        self.lock_file_path,
        mode="a",  # Append mode (create if missing)
    )
    # ... rest of method ...

except IsADirectoryError:
    # ✅ HANDLE DIRECTORY DOS ATTACK
    logger.error(
        "Directory exists at lock path: %s (removing)",
        self.lock_file_path
    )
    try:
        import shutil
        shutil.rmtree(self.lock_file_path)
    except Exception as cleanup_error:
        logger.error("Failed to remove directory: %s", cleanup_error)
    
    raise ActionableError(
        what_failed=f"Acquire lock for '{self.index_name}'",
        why_failed=f"Directory exists at lock path: {self.lock_file_path}",
        how_to_fix=(
            "Directory has been removed. Retry the operation.\n"
            "If issue persists:\n"
            "1. Check filesystem permissions\n"
            "2. Verify no process is creating directories at lock path\n"
            f"3. Manually inspect: ls -ld {self.lock_file_path}"
        ),
    )

except IOError as e:
    # Handle lock unavailable, permission denied, etc.
```

**Acceptance Criteria:**
- [ ] `IsADirectoryError` caught before `IOError`
- [ ] Directory removed using `shutil.rmtree()`
- [ ] `ActionableError` raised with clear guidance
- [ ] Unit test passes: `test_acquire_lock_directory_dos()`

---

## Test Case

### TC-ILM001: Directory DoS Mitigation

**Objective:** Verify IndexLockManager removes directory at lock path.

**Steps:**
1. Create directory at `.cache/rag/standards.lock`
2. Create `IndexLockManager("standards", Path(".cache/rag"))`
3. Call `acquire_exclusive()`
4. Verify `IsADirectoryError` caught
5. Verify directory removed
6. Verify `ActionableError` raised with remediation guidance

**Expected Results:**
- Directory removed
- `ActionableError` raised
- Error message includes: "Directory exists at lock path"
- How-to-fix guidance provided

**Pass/Fail Criteria:** All expected results met

---

## Code Changes Summary

**Files Modified:**
1. `.praxis-os/ouroboros/subsystems/rag/lock_manager.py` (1 method updated)

**Lines of Code:**
- Added: ~20 lines (`IsADirectoryError` handling)
- Modified: ~5 lines (exception handling order)
- Total: ~25 LOC changes

**Dependencies:**
- Added: `import shutil` (for `rmtree`)

---

## Testing Summary

**New Tests:** 1 test case (TC-ILM001)  
**Estimated Test Time:** 5 minutes  
**Coverage Target:** 100% line coverage for modified code

---

## Rollout Plan

### Phase 1: Implementation (30 minutes)
1. Add `IsADirectoryError` handling in `_acquire_lock()` (20 min)
2. Add unit test (10 min)

### Phase 2: Testing (5 minutes)
1. Run unit test
2. Verify no regressions

### Phase 3: Deployment (Immediate)
- No migration needed
- Change is backward compatible

---

## Success Criteria

- [ ] Test case TC-ILM001 passes
- [ ] 100% line coverage for modified code
- [ ] No regressions in existing IndexLockManager functionality
- [ ] IndexLockManager security grade: B → A

---

## Traceability

**Parent Spec:** Lock Security & Singleton Enforcement  
**Related Specs:**
- RuntimeLock v1.2 (security patterns source)
- InitLock Hardening (parallel effort)
- Security Audit (`.praxis-os/workspace/analysis/2025-11-17-existing-locks-security-audit.md`)

**Requirements Addressed:**
- FR-014: Directory DoS Mitigation

---

**Status:** ✅ Specification Complete - Ready for Implementation

