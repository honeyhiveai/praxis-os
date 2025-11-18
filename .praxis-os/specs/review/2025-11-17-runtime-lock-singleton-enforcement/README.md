# Lock Security & Singleton Enforcement Specification

**Status:** ✅ Specification Complete - Ready for Implementation  
**Date:** 2025-11-17  
**Updated:** 2025-11-17 (Expanded scope to include all locks)  
**Priority:** Critical  
**Estimated Implementation Time:** 7 hours (RuntimeLock: 5h, InitLock hardening: 2h)

---

## Executive Summary

**Problem:** Cursor's MCP client spawns multiple ouroboros server instances simultaneously, causing race conditions, index corruption, and resource exhaustion. Additionally, security audit revealed that existing locks (InitLock, IndexLockManager) lack critical security mitigations discovered during RuntimeLock design.

**Solution:** 
1. **RuntimeLock (NEW):** Lifetime lock ensuring only one MCP server runs per project
2. **InitLock Hardening (EXISTING):** Apply RuntimeLock security mitigations to prevent PID reuse, disk full, and DoS attacks
3. **IndexLockManager Hardening (EXISTING):** Add directory DoS mitigation

**Scope Expansion Rationale:**
During RuntimeLock design, we discovered security patterns (process name verification, disk full handling, directory DoS mitigation) that are universally applicable to all file-based locks. Rather than implement RuntimeLock in isolation, this spec now provides a **unified lock security framework** for the entire codebase.

**Impact:**
- **Reliability:** Eliminates index corruption from concurrent builds (0 DuckDB errors vs 5-10/week)
- **Security:** Prevents PID reuse attacks, disk full corruption, directory DoS across all locks
- **Performance:** Reduces resource waste (CPU: 159.4% → 77%, Memory: 12% → 10.9%)
- **UX:** Graceful handling of duplicate spawns (<1 second fast-fail, clear messaging)

---

## Scope: Three Locks, One Security Framework

This specification covers **three locks** with a unified security approach:

| Lock | Type | Scope | Changes |
|------|------|-------|---------|
| **RuntimeLock** | NEW | Lifetime (server startup → shutdown) | Full implementation (5 hours) |
| **InitLock** | EXISTING | Initialization only (startup → init complete) | Security hardening (2 hours) |
| **IndexLockManager** | EXISTING | Per-index operations (build, search) | Minor hardening (30 min, included in InitLock) |

**Why Expand Scope?**
- Security patterns discovered during RuntimeLock design apply to all file-based locks
- InitLock has critical gaps (PID reuse, disk full, directory DoS)
- Unified approach ensures consistent security across codebase
- Marginal cost: +2 hours for significant security improvement

---

## Specification Documents

This specification package contains 7 core documents (5 original + 2 addendums):

### 1. [srd.md](srd.md) - Software Requirements Document
**Purpose:** Defines WHAT needs to be built and WHY

**Contents:**
- 3 Business Goals (with metrics)
- 4 User Stories (with acceptance criteria)
- 8 Functional Requirements (FR-001 to FR-008)
- 13 Non-Functional Requirements (NFR-R1, NFR-P1, NFR-M1, etc.)
- Out-of-Scope Items (4 categories)

**Key Requirements:**
- **FR-001:** Singleton enforcement via lifetime lock
- **FR-002:** Stale lock detection (dead PID cleanup)
- **NFR-P1:** <100ms lock acquisition time
- **NFR-M3:** 100% test coverage

---

### 2. [specs.md](specs.md) - Technical Specifications
**Purpose:** Defines HOW the system will be built

**Contents:**
- Architecture Overview (3-layer lock hierarchy)
- Component Design (RuntimeLock class, __main__.py integration)
- API Specifications (public methods, signatures, behavior)
- Data Models (lock file format, internal state)
- Security Considerations (4 threat analyses)
- Performance Considerations (benchmarks, targets)

**Key Design Decisions:**
- **Option B:** Separate RuntimeLock class (not extend InitLock)
- **Atomic File Creation:** `os.open()` with `O_CREAT | O_EXCL`
- **Lock Order:** RuntimeLock → InitLock (runtime before init)

---

### 3. [tasks.md](tasks.md) - Implementation Tasks
**Purpose:** Breaks implementation into actionable tasks

**Contents:**
- 4 Implementation Phases
- 22 Tasks (with acceptance criteria)
- Time Estimates (4.5 hours total)
- Dependencies (task → task, phase → phase)
- Validation Gates (per-phase checkpoints)

**Phases:**
1. **Phase 1:** RuntimeLock Implementation (2 hours, 8 tasks)
2. **Phase 2:** Integration with __main__.py (30 minutes, 5 tasks)
3. **Phase 3:** Testing (1.5 hours, 5 tasks)
4. **Phase 4:** Documentation (30 minutes, 4 tasks)

---

### 4. [implementation.md](implementation.md) - Implementation Guidance
**Purpose:** Provides code patterns, deployment, and troubleshooting

**Contents:**
- 5 Code Patterns (atomic file creation, conservative PID checking, etc.)
- Testing Summary (31 test cases, 100% coverage)
- Deployment Steps (4-step process)
- Rollback Plan (emergency recovery)
- Troubleshooting Guide (4 common issues + solutions)
- Code Examples (complete RuntimeLock implementation)

**Key Patterns:**
- **Atomic File Creation:** `os.open()` with `O_CREAT | O_EXCL`
- **Conservative PID Checking:** Assume alive if uncertain (NFR-R1)
- **Graceful Error Handling:** Never crash, log warnings
- **Idempotent Release:** Safe to call multiple times

---

### 5. [testing/README.md](testing/README.md) - Testing Documentation
**Purpose:** Comprehensive test plans for all requirements

**Contents:**
- Requirements List (8 FRs, 13 NFRs)
- 13 Functional Test Cases (TC-F001 to TC-F013)
- 3 Integration Test Cases (TC-I001 to TC-I003)
- 2 Stress Test Cases (TC-S001 to TC-S002)
- 3 Performance Benchmarks (TC-B001 to TC-B003)
- 8 Non-Functional Test Cases (TC-N001 to TC-N008)
- Test Strategy (unit, integration, stress, benchmarks)
- Traceability Matrix (requirements → tests, 100% coverage)

**Test Coverage:**
- **Total Test Cases:** 31
- **Requirements Coverage:** 100% (all FRs and NFRs)
- **Target Coverage:** 100% line coverage for RuntimeLock

---

---

### 6. [ADDENDUM-InitLock-Hardening.md](ADDENDUM-InitLock-Hardening.md) - InitLock Security Fixes
**Purpose:** Apply RuntimeLock security mitigations to existing InitLock

**Contents:**
- Security Audit Summary (4 critical gaps identified)
- Requirements (FR-009 to FR-012: PID reuse, disk full, directory DoS, retry limit)
- Implementation Tasks (5 tasks, 2 hours)
- Test Cases (8 new tests for security mitigations)
- Backward Compatibility (lock file format migration)

**Key Changes:**
- Add `_get_process_cmdline()` for process name verification
- Change lock file format: `"PID"` → `"PID TIMESTAMP"`
- Add disk full handling (write verification + cleanup)
- Add directory DoS mitigation (`IsADirectoryError`)
- Add retry limit (max 3 retries)

---

### 7. [ADDENDUM-IndexLockManager-Hardening.md](ADDENDUM-IndexLockManager-Hardening.md) - IndexLockManager Minor Fixes
**Purpose:** Add directory DoS mitigation to IndexLockManager

**Contents:**
- Security Audit Summary (1 issue identified)
- Implementation Task (1 task, 30 minutes, included in InitLock time estimate)
- Test Case (1 new test)

**Key Changes:**
- Add `IsADirectoryError` handling in `_acquire_lock()`

---

## Supporting Documents

### [supporting-docs/design-doc-runtime-lock.md](supporting-docs/design-doc-runtime-lock.md)
**Purpose:** Original design document with detailed analysis

**Contents:**
- Problem statement (evidence: 5 zombie processes)
- Root cause analysis (InitLock releases too early)
- 4 design options evaluated (A, B, C, D)
- Approved solution: Option B - Create Separate RuntimeLock Class
- Complete implementation plan with code examples
- Testing strategy (unit, integration, stress tests)
- Risk analysis and mitigations

**Decision:** Option B approved on 2025-11-17

---

## Quick Start

### For Implementers

**Step 1: Read Requirements**
```bash
# Start here to understand WHAT and WHY
cat srd.md
```

**Step 2: Review Design**
```bash
# Understand HOW it will be built
cat specs.md
```

**Step 3: Follow Tasks**
```bash
# Step-by-step implementation guide
cat tasks.md
```

**Step 4: Use Code Patterns**
```bash
# Code examples and best practices
cat implementation.md
```

**Step 5: Write Tests**
```bash
# Test cases for all requirements
cat testing/README.md
```

---

### For Reviewers

**Checklist:**
- [ ] Business goals clear and measurable (srd.md Section 2)
- [ ] User stories have acceptance criteria (srd.md Section 3)
- [ ] All FRs are testable (srd.md Section 4)
- [ ] Architecture is sound (specs.md Section 1)
- [ ] APIs are well-defined (specs.md Section 3)
- [ ] Tasks have acceptance criteria (tasks.md)
- [ ] Test coverage is 100% (testing/README.md)
- [ ] Deployment plan is clear (implementation.md Section 3)

---

## Key Metrics

### Business Impact
- **Index Corruption:** 5-10 DuckDB errors/week → 0
- **CPU Usage:** 159.4% (2+ cores) → 77% (single server)
- **Memory Usage:** 12% RAM (7.9 GB) → 10.9% RAM
- **Manual Cleanup:** 5-10 `kill -9` commands/week → 0

### Technical Targets
- **Lock Acquisition:** <100ms (95th percentile)
- **Duplicate Spawn Detection:** <1 second (99th percentile)
- **Code Quality:** <200 LOC, 100% type hints
- **Test Coverage:** 100% line coverage
- **Cross-Platform:** macOS, Linux, Windows

---

## Implementation Timeline

| Phase | Duration | Tasks | Key Deliverable |
|-------|----------|-------|-----------------|
| Phase 1 | 2.5 hours | 8 | RuntimeLock class complete (with security fixes) |
| Phase 2 | 30 minutes | 5 | __main__.py integration |
| Phase 3 | 1.5 hours | 5 | All tests passing |
| Phase 4 | 30 minutes | 4 | Documentation complete |
| **Total** | **5 hours** | **22** | **Production-ready** |

**Security Fixes Added (+30 minutes):**
- Timestamp validation (PID reuse mitigation)
- Retry limit (infinite loop prevention)
- Disk full handling (write verification)
- Directory DoS mitigation

---

## Success Criteria

**Before Deployment:**
- [ ] All 22 tasks complete (tasks.md)
- [ ] All 31 test cases pass (testing/README.md)
- [ ] 100% line coverage for RuntimeLock
- [ ] All performance benchmarks meet targets
- [ ] Cross-platform validation complete (macOS, Linux, Windows)
- [ ] No regressions in existing functionality

**After Deployment:**
- [ ] Zero zombie processes (`ps aux | grep ouroboros | wc -l` = 1)
- [ ] Zero index corruption (0 DuckDB errors)
- [ ] CPU usage normal (single server: ~77%)
- [ ] No manual cleanup required (0 `kill -9` commands)

---

## Dependencies

**Python Version:** 3.10+  
**External Dependencies:** None (uses Python stdlib only)

**Internal Dependencies:**
- `ouroboros.foundation.init_lock.InitLock` (existing)
- `ouroboros.foundation.lock_manager.IndexLockManager` (existing)

**No Breaking Changes:** Drop-in addition to `__main__.py`

---

## Risks and Mitigations

### Risk 1: PID Reuse Attack
**Likelihood:** Low  
**Impact:** Medium  
**Mitigation:** Conservative PID checking, timeout for old locks (>7 days)

### Risk 2: Stale Locks
**Likelihood:** Medium (crashes, force kills)  
**Impact:** Medium (manual cleanup required)  
**Mitigation:** Automatic stale lock detection (PID checking)

### Risk 3: Cross-Platform Issues
**Likelihood:** Low  
**Impact:** Medium  
**Mitigation:** Test on Windows, fallback to simpler locking

**See:** specs.md Section 5 for complete risk analysis

---

## Next Steps

**For Implementation Team:**
1. Read this README (5 minutes)
2. Review srd.md for requirements (15 minutes)
3. Review specs.md for design (20 minutes)
4. Start Phase 1 tasks (tasks.md)
5. Follow implementation.md for code patterns
6. Write tests per testing/README.md

**For Stakeholders:**
1. Review business goals (srd.md Section 2)
2. Review success metrics (this README)
3. Approve for implementation

**For QA Team:**
1. Review testing/README.md (31 test cases)
2. Prepare test environment
3. Execute tests after implementation

---

## Questions?

**Technical Questions:** See specs.md Section 3 (API Specifications)  
**Implementation Questions:** See implementation.md Section 1 (Code Patterns)  
**Testing Questions:** See testing/README.md  
**Troubleshooting:** See implementation.md Section 4

---

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-17 | 1.0 | Initial specification complete |

---

**Status:** ✅ Ready for Implementation  
**Next Action:** Begin Phase 1 (RuntimeLock Implementation)  
**Estimated Completion:** 5 hours from start

---

## Revision History

### 2025-11-17 (v2.0) - Scope Expansion: Unified Lock Security Framework
**Changes:**
- **Expanded scope** to cover all three locks (RuntimeLock, InitLock, IndexLockManager)
- Added **ADDENDUM-InitLock-Hardening.md** (5 new requirements, 8 test cases, 2 hours)
- Added **ADDENDUM-IndexLockManager-Hardening.md** (1 new requirement, 1 test case, 30 min)
- Updated time estimate: 5 hours → 7 hours (RuntimeLock: 5h, InitLock: 2h)
- Created unified security framework applicable to all file-based locks

**Rationale:** Security audit revealed that InitLock has critical gaps (PID reuse, disk full, directory DoS). Rather than implement RuntimeLock in isolation, we're applying discovered security patterns to ALL locks for consistency and maximum security benefit.

**Impact:**
- InitLock security grade: C → A+
- IndexLockManager security grade: B → A
- Consistent security patterns across entire codebase
- Marginal cost (+2 hours) for significant security improvement

### 2025-11-17 (v1.2) - Process Name Verification Added
**Changes:**
- Added process name verification using stdlib only (`/proc` or `ps` command)
- `_is_process_running()` now checks if PID is actually ouroboros (not just alive)
- Detects PID reuse **immediately** (no 24-hour wait needed)
- Timestamp validation kept as secondary defense (belt-and-suspenders)

**Rationale:** Process name checking is superior to timestamp-only validation:
- Detects PID reuse in milliseconds (not hours)
- Works on all supported platforms (Linux, macOS, WSL2)
- No external dependencies (uses `/proc` filesystem or `ps` command)
- Conservative fallback (if can't verify, assume valid)

### 2025-11-17 (v1.1) - Security Fixes Added
**Changes:**
- Added timestamp validation to lock file format (PID reuse mitigation)
- Added retry limit to `acquire()` method (infinite loop prevention)
- Added disk full handling with write verification
- Added directory DoS mitigation (`IsADirectoryError` handling)
- Clarified Windows support (WSL2 only, not native Windows)
- Documented NFS limitation (not supported)
- Updated time estimate: 4.5 hours → 5 hours

**Rationale:** Pessimistic engineer review identified edge cases that could cause production incidents. These fixes harden the implementation against:
- PID reuse on busy systems (process name verification + 24-hour timestamp timeout)
- Infinite retry loops (3-retry limit)
- Disk full corruption (write verification + cleanup)
- Directory DoS attacks (detect and remove)

### 2025-11-17 (v1.0) - Initial Specification
**Changes:** Complete specification created via `spec_creation_v1` workflow


