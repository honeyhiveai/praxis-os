# RuntimeLock Specification Changelog

## 2025-11-17 (v1.2) - Process Name Verification Added

### Summary
Enhanced PID reuse mitigation by adding **process name verification** using stdlib only (`/proc` or `ps` command). This provides immediate detection of PID reuse without waiting for the 24-hour timestamp timeout.

---

### Changes Made

#### 1. **specs.md** - Technical Specifications
- Added `_get_process_cmdline()` static method to API specifications
  - Tries `/proc/{pid}/cmdline` first (Linux, WSL2) - instant
  - Falls back to `ps -p {pid} -o command=` (macOS) - ~50ms
  - Returns `None` on any error (conservative)
- Updated `_is_process_running()` to verify process name
  - Checks if PID exists AND is ouroboros
  - Returns `False` if PID exists but is NOT ouroboros (PID reuse detected!)
  - Returns `True` if can't verify (conservative, NFR-R1)
- Updated dependencies to include `subprocess` and `time`
- Updated Security Considerations (Section 5.1):
  - Process name verification is now PRIMARY defense
  - Timestamp validation is SECONDARY (belt-and-suspenders)
  - Detects PID reuse immediately (not after 24 hours)

#### 2. **tasks.md** - Implementation Tasks
- Updated Task 1.5 (formerly `_is_process_running()` only):
  - Now includes both `_get_process_cmdline()` and `_is_process_running()`
  - Increased time estimate: 15 minutes → 25 minutes
  - Added acceptance criteria for process name verification
  - Added unit tests: `test_get_process_cmdline_proc()`, `test_get_process_cmdline_ps()`, `test_is_process_running_pid_reused()`
- Updated Task 1.6 (`acquire()` method):
  - Added test case: `test_acquire_stale_lock_pid_reused()`
  - Updated acceptance criteria to reflect process name checking

#### 3. **implementation.md** - Implementation Guidance
- Replaced "Conservative PID Checking Pattern" (Section 1.2) with "Process Name Verification Pattern"
- Added complete code examples for:
  - `_get_process_cmdline()` with `/proc` and `ps` fallback
  - `_is_process_running()` with process name verification
  - `acquire()` with process name checking integrated
- Updated rationale:
  - Process name verification detects PID reuse immediately
  - Works on all supported platforms using stdlib only
  - Timestamp provides secondary defense
  - Conservative fallback prevents false positives

#### 4. **README.md** - Main Specification Document
- Updated "Updated" date to reflect process name verification
- Added revision history entry (v1.2):
  - Process name verification using stdlib only
  - Immediate PID reuse detection
  - Timestamp kept as secondary defense
- Updated rationale:
  - Detects PID reuse in milliseconds (not hours)
  - No external dependencies
  - Works on Linux, macOS, WSL2

#### 5. **testing/README.md** - Testing Documentation
- Added new test cases:
  - **TC-F003b**: Stale Lock Detection (PID Reused)
    - Verifies process name verification detects PID reuse
    - Uses running non-ouroboros process (e.g., bash)
  - **TC-F003c**: Process Name Verification (Cannot Verify)
    - Verifies conservative behavior when can't read process name
  - **TC-F004b**: Stale Lock Detection (Old Timestamp)
    - Verifies 24-hour timestamp timeout (belt-and-suspenders)
  - **TC-F014**: Process Name Verification (_get_process_cmdline)
    - Unit test for `_get_process_cmdline()` method
- Updated existing test cases to reflect new lock file format (PID + timestamp)
- Updated test execution summary:
  - Total test cases: 31 → 35
  - Functional tests: 13 → 17
  - Success criteria includes process name verification on all platforms

---

### Technical Benefits

1. **Immediate PID Reuse Detection**
   - Old approach: Wait 24 hours for timestamp timeout
   - New approach: Detect in <50ms via process name check

2. **No External Dependencies**
   - Uses stdlib only (`/proc` filesystem or `ps` command)
   - No need for `psutil` or other packages

3. **Platform Support**
   - Linux: `/proc/{pid}/cmdline` (instant)
   - macOS: `ps -p {pid} -o command=` (~50ms)
   - WSL2: `/proc/{pid}/cmdline` (instant)
   - Native Windows: Not supported (WSL2 only)

4. **Conservative Fallback**
   - If can't verify process name → assume valid (NFR-R1: Zero False Positives)
   - Prevents false positives from permission errors

5. **Defense in Depth**
   - Process name verification (primary)
   - Timestamp validation (secondary, 24-hour timeout)
   - Both work together for maximum reliability

---

### Security Impact

**Before (v1.1):**
- PID reuse mitigation: Timestamp only (24-hour timeout)
- Risk: PID reuse within 24 hours would not be detected
- Likelihood: Medium (on busy systems with low pid_max)

**After (v1.2):**
- PID reuse mitigation: Process name verification (immediate) + timestamp (belt-and-suspenders)
- Risk: Virtually eliminated (detects PID reuse in milliseconds)
- Likelihood: Very Low (only if both checks fail)

---

### Implementation Estimate

**No change to total time estimate:** 5 hours
- Task 1.5 increased by 10 minutes (15 → 25 minutes)
- Offset by improved reliability (fewer edge cases to handle)

---

### Backward Compatibility

**Lock File Format Change:**
- Old format: `"PID"` (e.g., `"47294"`)
- New format: `"PID TIMESTAMP"` (e.g., `"47294 1700000000"`)

**Compatibility:**
- `_read_lock_holder()` handles both formats gracefully
- Old locks (PID only) parsed as corrupted → removed → retry
- No migration needed (stale locks cleaned up automatically)

---

### Next Steps

1. **Implementation Phase** (2.5 hours)
   - Implement `_get_process_cmdline()` method
   - Update `_is_process_running()` to use process name verification
   - Update `acquire()` to integrate both checks

2. **Testing Phase** (1.5 hours)
   - Add unit tests for process name verification
   - Add integration tests for PID reuse scenarios
   - Verify on Linux, macOS, WSL2

3. **Documentation Phase** (30 minutes)
   - Update inline comments
   - Add docstrings for new methods

---

**Status:** ✅ Specification Complete - Ready for Implementation
