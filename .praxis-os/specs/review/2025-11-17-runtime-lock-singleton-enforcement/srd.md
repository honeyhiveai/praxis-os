# Software Requirements Document

**Project:** RuntimeLock - Singleton MCP Server Enforcement  
**Date:** 2025-11-17  
**Priority:** Critical  
**Category:** Enhancement (Reliability)

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for implementing a `RuntimeLock` mechanism to enforce singleton MCP server instances per project, preventing race conditions, index corruption, and resource exhaustion caused by multiple concurrent server processes.

### 1.2 Scope
This feature will introduce a new `RuntimeLock` class that is acquired at server startup and held for the entire process lifetime, ensuring only one ouroboros MCP server runs per project at any time. It complements the existing `InitLock` (initialization) and `IndexLockManager` (index operations) to create a three-layer lock architecture.

---

## 2. Business Goals

### Goal 1: Eliminate Index Corruption from Concurrent Server Processes

**Objective:** Prevent data corruption in code indexes (DuckDB, LanceDB) caused by multiple MCP server instances building indexes simultaneously.

**Success Metrics:**
- **DuckDB Constraint Errors**: Current: 5-10 per week → Target: 0 per week
- **Duplicate Log Entries**: Current: 2x-4x duplication → Target: 1x (single server)
- **Index Rebuild Loops**: Current: "Bouncing" index (never healthy) → Target: Single successful build

**Business Impact:**
- **Reliability**: Users can trust that indexes are accurate and complete
- **Data Integrity**: Zero risk of corrupted index files requiring manual cleanup
- **Developer Productivity**: No time wasted debugging index issues (estimated 2-4 hours/week saved)

---

### Goal 2: Reduce Resource Waste from Zombie Processes

**Objective:** Eliminate CPU and memory waste from multiple zombie MCP server processes running concurrently.

**Success Metrics:**
- **Concurrent Processes**: Current: 3-5 zombie processes → Target: 1 active process
- **CPU Usage**: Current: 159.4% (2+ cores) → Target: 77% (single server)
- **Memory Usage**: Current: 12% RAM (7.9 GB) → Target: 10.9% RAM (single server)

**Business Impact:**
- **Performance**: User's machine remains responsive (no CPU/memory exhaustion)
- **Battery Life**: Reduced power consumption on laptops (estimated 20-30% improvement)
- **Cost Savings**: No need for manual process cleanup (estimated 10-15 minutes/day saved)

---

### Goal 3: Improve User Experience with Graceful Duplicate Spawn Handling

**Objective:** Provide a seamless experience when Cursor's MCP client spawns multiple servers due to race conditions, with fast-fail and clear messaging.

**Success Metrics:**
- **Duplicate Spawn Detection Time**: Current: N/A (no detection) → Target: <1 second
- **Manual Cleanup Required**: Current: 5-10 `kill -9` commands/week → Target: 0 per week
- **User Confusion**: Current: "Why is my index bouncing?" → Target: Clear logs explaining behavior

**Business Impact:**
- **User Satisfaction**: No frustration from unpredictable behavior or manual cleanup
- **Adoption**: Reduces barrier to entry (no need to understand process management)
- **Support Load**: Fewer support requests about zombie processes (estimated 50% reduction)

---

## 2.1 Supporting Documentation

The business goals above are informed by:
- **Runtime Lock Design Document** (`supporting-docs/design-doc-runtime-lock.md`): 
  - Evidence of 5 concurrent zombie processes observed in production
  - Root cause analysis showing `InitLock` releases too early
  - Quantified impact: 159.4% CPU, 12% RAM, 5-10 DuckDB errors/week
  - Approved solution: Option B - Create Separate RuntimeLock Class

See `supporting-docs/REFERENCES.md` for complete documentation.

---

## 3. User Stories

User stories describe the feature from the user's perspective.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: Automatic Singleton Enforcement

**As a** praxis-os user (developer using Cursor with MCP)  
**I want to** have only one MCP server running per project automatically  
**So that** I don't experience index corruption, resource waste, or unpredictable behavior from zombie processes

**Acceptance Criteria:**
- Given Cursor spawns multiple MCP servers simultaneously (race condition)
- When the second server attempts to start
- Then it detects the first server is running and exits gracefully within 1 second
- And no error messages are logged (this is expected behavior)
- And only 1 MCP server process remains running

**Priority:** Critical (Must-Have)

---

### Story 2: Automatic Stale Lock Cleanup

**As a** praxis-os user  
**I want to** have stale locks automatically cleaned up when the MCP server crashes  
**So that** I can start a new server without manual intervention (deleting lock files)

**Acceptance Criteria:**
- Given the MCP server crashed or was force-killed (`kill -9`)
- And a stale lock file exists with a dead PID
- When I start a new MCP server
- Then it detects the stale lock (dead PID check)
- And removes the stale lock file
- And acquires the lock successfully
- And the server starts normally

**Priority:** Critical (Must-Have)

---

### Story 3: Clear Observability for Debugging

**As a** praxis-os developer or power user  
**I want to** see clear log messages about lock acquisition and duplicate spawn detection  
**So that** I can understand what's happening when Cursor spawns multiple servers and debug issues if needed

**Acceptance Criteria:**
- Given the MCP server starts
- When it acquires the runtime lock successfully
- Then it logs "Runtime lock acquired (PID {pid})"
- And when a duplicate spawn is detected
- Then it logs "Another MCP server is running (PID {holder_pid}). Exiting gracefully."
- And when a stale lock is cleaned up
- Then it logs "Stale runtime lock (dead PID {dead_pid})"

**Priority:** High

---

### Story 4: Cross-Platform Reliability

**As a** praxis-os user on any platform (macOS, Linux, Windows)  
**I want to** have consistent singleton enforcement behavior  
**So that** I get the same reliable experience regardless of my operating system

**Acceptance Criteria:**
- Given I'm running praxis-os on macOS, Linux, or Windows
- When the RuntimeLock is used
- Then it works consistently across all platforms
- And uses appropriate OS primitives (fcntl on Unix, file creation atomicity on Windows)
- And provides the same guarantees (singleton enforcement, stale lock detection)

**Priority:** High

---

## 3.1 Story Priority Summary

**Critical (Must-Have):**
- Story 1: Automatic Singleton Enforcement
- Story 2: Automatic Stale Lock Cleanup

**High Priority:**
- Story 3: Clear Observability for Debugging
- Story 4: Cross-Platform Reliability

---

## 3.2 Supporting Documentation

User needs from supporting documents:
- **Runtime Lock Design Document**: 
  - User pain point: Manual `kill -9` commands 5-10 times/week
  - User confusion: "Why is my index bouncing?"
  - User frustration: Unpredictable behavior from multiple servers

See `supporting-docs/REFERENCES.md` for details.

---

## 4. Functional Requirements

Functional requirements specify capabilities the system must provide.

---

### FR-001: Singleton Enforcement

**Description:** The system shall ensure only one ouroboros MCP server process runs per project at any time by acquiring a runtime lock at startup and holding it for the entire process lifetime.

**Priority:** Critical

**Related User Stories:** Story 1

**Acceptance Criteria:**
- When a second MCP server attempts to start while another is running, it shall detect the existing server within 1 second
- The second server shall exit gracefully with exit code 0 (no error)
- The second server shall NOT log error messages (this is expected behavior)
- Only one MCP server process shall remain running after duplicate spawn attempts

---

### FR-002: Stale Lock Detection

**Description:** The system shall detect and cleanup stale runtime locks from crashed or killed processes by checking if the lock holder PID is still running.

**Priority:** Critical

**Related User Stories:** Story 2

**Acceptance Criteria:**
- When a lock file exists with a PID that is no longer running, the system shall detect it as stale
- The system shall remove the stale lock file
- The system shall acquire the lock successfully after cleanup
- The system shall handle zombie processes (PID exists but process is dead)
- The system shall handle corrupted lock files (invalid PID format)

---

### FR-003: Graceful Degradation

**Description:** The system shall handle edge cases in lock acquisition without blocking valid servers from starting.

**Priority:** High

**Related User Stories:** Story 2

**Acceptance Criteria:**
- When the lock file is missing, the system shall create it and proceed
- When the lock file is unreadable, the system shall log a warning and proceed
- When the lock directory is missing, the system shall create it and proceed
- When PID checking fails, the system shall assume the process is running (safer default)
- The system shall never block a valid server from starting due to lock issues

---

### FR-004: Cross-Platform Support

**Description:** The system shall provide consistent singleton enforcement behavior across Unix, Linux, macOS, and Windows platforms.

**Priority:** High

**Related User Stories:** Story 4

**Acceptance Criteria:**
- On Unix/Linux/macOS, the system shall use atomic file creation (O_CREAT | O_EXCL)
- On Windows, the system shall use equivalent atomic file creation primitives
- The system shall provide the same guarantees on all platforms (singleton enforcement, stale lock detection)
- The system shall use platform-appropriate PID checking mechanisms (os.kill(pid, 0) on Unix, equivalent on Windows)

---

### FR-005: Lock Lifecycle Management

**Description:** The system shall acquire the runtime lock at server startup, hold it for the entire process lifetime, and release it on graceful shutdown.

**Priority:** Critical

**Related User Stories:** Story 1

**Acceptance Criteria:**
- The runtime lock shall be acquired before the init lock (lock order: runtime → init)
- The runtime lock shall be held continuously from startup until shutdown
- The runtime lock shall be released in the finally block to ensure cleanup on exceptions
- The runtime lock shall be released via atexit handler to ensure cleanup on normal exit
- If the server crashes, the lock file may remain (will be detected as stale by next spawn)

---

### FR-006: Observability

**Description:** The system shall provide clear logging for lock acquisition, duplicate spawn detection, and stale lock cleanup to enable debugging.

**Priority:** High

**Related User Stories:** Story 3

**Acceptance Criteria:**
- When the lock is acquired, the system shall log "Runtime lock acquired (PID {pid})" at INFO level
- When a duplicate spawn is detected, the system shall log "Another MCP server is running (PID {holder_pid}). Exiting gracefully." at INFO level
- When a stale lock is cleaned up, the system shall log "Stale runtime lock (dead PID {dead_pid})" at INFO level
- When lock acquisition fails, the system shall log the reason with sufficient detail for debugging
- All log messages shall include the relevant PIDs for traceability

---

### FR-007: Lock File Location

**Description:** The system shall store the runtime lock file in the `.praxis-os/.cache/` directory with a standardized name.

**Priority:** Medium

**Related User Stories:** Story 1, Story 2

**Acceptance Criteria:**
- The runtime lock file shall be named `.runtime.lock`
- The lock file shall be stored at `.praxis-os/.cache/.runtime.lock`
- The lock file shall contain only the PID of the lock holder (as UTF-8 text)
- The lock file shall have permissions 0o600 (owner read/write only)
- The `.cache/` directory shall be created if it doesn't exist

---

### FR-008: Integration with Existing Locks

**Description:** The system shall integrate with the existing InitLock and IndexLockManager without conflicts or breaking changes.

**Priority:** Critical

**Related User Stories:** Story 1

**Acceptance Criteria:**
- The RuntimeLock shall be a separate class (not modify InitLock)
- The RuntimeLock shall be acquired before the InitLock in `__main__.py`
- The InitLock shall continue to be released after initialization (no changes to InitLock behavior)
- The IndexLockManager shall continue to operate independently (per-index locking)
- No breaking changes to existing code (drop-in addition to `__main__.py`)

---

## 4.1 Requirements by Category

### Lock Management (Core)
- FR-001: Singleton Enforcement
- FR-002: Stale Lock Detection
- FR-005: Lock Lifecycle Management
- FR-007: Lock File Location

### Reliability & Edge Cases
- FR-003: Graceful Degradation
- FR-004: Cross-Platform Support

### Integration & Compatibility
- FR-008: Integration with Existing Locks

### Observability
- FR-006: Observability

---

## 4.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority |
|-------------|--------------|----------------|----------|
| FR-001 | Story 1 | Goal 1, Goal 2 | Critical |
| FR-002 | Story 2 | Goal 3 | Critical |
| FR-003 | Story 2 | Goal 3 | High |
| FR-004 | Story 4 | Goal 3 | High |
| FR-005 | Story 1 | Goal 1, Goal 2 | Critical |
| FR-006 | Story 3 | Goal 3 | High |
| FR-007 | Story 1, Story 2 | Goal 1 | Medium |
| FR-008 | Story 1 | Goal 1 | Critical |

---

## 4.3 Supporting Documentation

Requirements informed by:
- **Runtime Lock Design Document** (`supporting-docs/design-doc-runtime-lock.md`):
  - FR-001, FR-005: Approved solution (Option B - Separate RuntimeLock Class)
  - FR-002: Stale lock detection requirements from root cause analysis
  - FR-003: Graceful degradation requirements from risk analysis
  - FR-004: Cross-platform support requirements
  - FR-006: Observability requirements from implementation plan
  - FR-008: Integration requirements (three-layer lock architecture)

---

## 5. Non-Functional Requirements

NFRs define quality attributes and system constraints.

---

### 5.1 Reliability

**NFR-R1: Zero False Positives**
- **Target:** 0 false positives (never kill valid server)
- **Measurement:** Number of valid servers incorrectly detected as stale per month
- **Rationale:** False positive = user's work interrupted (critical failure)
- **Verification:** Unit tests for PID checking, integration tests with long-running servers

**NFR-R2: Stale Lock Detection Accuracy**
- **Target:** 100% detection rate for stale locks (dead PIDs)
- **Measurement:** Percentage of stale locks successfully detected and cleaned up
- **Rationale:** Users should never need to manually delete lock files
- **Verification:** Unit tests with dead PIDs, integration tests with force-killed servers

---

### 5.2 Performance

**NFR-P1: Lock Acquisition Time**
- **Target:** <100ms for lock acquisition (normal case)
- **Measurement:** Time from RuntimeLock.acquire() call to return
- **Rationale:** Should not slow down server startup (startup already takes 5-10 seconds for index loading)
- **Verification:** Benchmark tests, profiling in production

**NFR-P2: Duplicate Spawn Detection Time**
- **Target:** <1 second for duplicate spawn detection and exit
- **Measurement:** Time from second server start to graceful exit
- **Rationale:** Fast-fail reduces resource waste and user confusion
- **Verification:** Integration tests with concurrent spawns, stress tests

---

### 5.3 Maintainability

**NFR-M1: Code Quality**
- **Target:** <200 LOC for RuntimeLock class
- **Measurement:** Lines of code in `runtime_lock.py`
- **Rationale:** Foundation layer code must be simple and bulletproof
- **Verification:** Code review, complexity analysis

**NFR-M2: Type Safety**
- **Target:** 100% type hints coverage
- **Measurement:** Percentage of functions/methods with type annotations
- **Rationale:** Foundation layer must be type-safe for reliability
- **Verification:** mypy static type checking, code review

**NFR-M3: Test Coverage**
- **Target:** 100% line coverage for RuntimeLock class
- **Measurement:** Coverage report from pytest
- **Rationale:** Critical code path must be fully tested
- **Verification:** pytest-cov, CI/CD coverage gates

---

### 5.4 Compatibility

**NFR-C1: No Breaking Changes**
- **Target:** Zero breaking changes to existing code
- **Measurement:** All existing tests pass without modification
- **Rationale:** Should be drop-in addition to `__main__.py`
- **Verification:** Full test suite execution, regression testing

**NFR-C2: Lock Layer Independence**
- **Target:** RuntimeLock, InitLock, and IndexLockManager operate independently
- **Measurement:** No shared state or dependencies between lock layers
- **Rationale:** Three distinct lock layers with clear purposes
- **Verification:** Architecture review, integration tests

---

### 5.5 Portability

**NFR-PO1: Cross-Platform Consistency**
- **Target:** Identical behavior on macOS, Linux, Windows
- **Measurement:** All tests pass on all three platforms
- **Rationale:** Users expect consistent experience regardless of OS
- **Verification:** CI/CD testing on multiple platforms, manual testing

**NFR-PO2: Platform-Appropriate Primitives**
- **Target:** Use native OS primitives for lock operations
- **Measurement:** No platform-specific workarounds or hacks
- **Rationale:** Reliability depends on using OS-provided atomicity guarantees
- **Verification:** Code review, platform-specific testing

---

### 5.6 Observability

**NFR-O1: Comprehensive Logging**
- **Target:** All lock operations logged with sufficient detail for debugging
- **Measurement:** Percentage of lock operations with corresponding log entries
- **Rationale:** Users and developers need visibility into lock behavior
- **Verification:** Log analysis, manual testing with log inspection

**NFR-O2: Actionable Error Messages**
- **Target:** All error messages include remediation guidance
- **Measurement:** Percentage of error messages with "how to fix" instructions
- **Rationale:** Users should be able to resolve issues without developer intervention
- **Verification:** Error message review, user testing

---

## 5.7 Supporting Documentation

NFRs informed by:
- **Runtime Lock Design Document** (`supporting-docs/design-doc-runtime-lock.md`):
  - NFR-R1: Zero false positives requirement from risk analysis
  - NFR-P1: <100ms lock acquisition target from performance requirements
  - NFR-M1, NFR-M2, NFR-M3: Code quality targets from maintainability requirements
  - NFR-C1, NFR-C2: Compatibility requirements from design decision (Option B)
  - NFR-PO1, NFR-PO2: Cross-platform requirements from FR-004
  - NFR-O1, NFR-O2: Observability requirements from FR-006

---

## 6. Out of Scope

Explicitly defines what is NOT included. Items may be considered for future phases.

### Explicitly Excluded

---

#### Features

**Not Included in This Release:**

1. **Distributed Lock Management (Multi-Machine)**
   - **Reason:** RuntimeLock is designed for single-machine, multi-process scenarios (Cursor spawning multiple servers on one machine). Distributed locking (across multiple machines) requires different primitives (e.g., Redis, etcd, ZooKeeper) and adds significant complexity.
   - **Future Consideration:** If praxis-os evolves to support distributed deployments (e.g., cloud-based MCP servers), distributed locking could be added as a separate layer.

2. **Lock Monitoring Dashboard**
   - **Reason:** Observability is provided through logging (FR-006), which is sufficient for debugging. A dedicated dashboard would require additional infrastructure (web server, UI) and is not critical for the core functionality.
   - **Future Consideration:** If users request enhanced observability, a simple CLI tool (`praxis-os lock status`) could be added to show current lock holder.

3. **Lock Priority/Preemption**
   - **Reason:** All MCP servers are equal priority. There's no use case for one server to "preempt" another. The first server to acquire the lock wins.
   - **Future Consideration:** Not planned. Preemption would introduce complexity and potential for abuse.

4. **Lock Timeout/Expiration**
   - **Reason:** RuntimeLock is held for the entire server lifetime (hours/days). Automatic expiration would cause valid servers to lose their lock, leading to corruption. Stale lock detection (FR-002) handles crashed processes.
   - **Future Consideration:** Not planned. Timeout-based locking is incompatible with the singleton enforcement model.

---

#### Platforms

**Not Supported in This Release:**

- **Native Windows**: 
  - **Reason:** RuntimeLock requires Unix-like PID semantics. `os.kill(pid, 0)` behaves differently on native Windows, requiring complex workarounds (ctypes, WMI, or psutil dependency).
  - **Workaround:** Use WSL2 (Windows Subsystem for Linux) - fully supported
  - **Future Consideration:** If native Windows demand increases significantly, could add psutil dependency or implement Windows-specific PID checking

- **Exotic Unix Variants (AIX, Solaris, HP-UX)**: 
  - **Reason:** praxis-os targets modern development platforms (macOS, Linux, WSL2). Exotic Unix variants have minimal user base and would require platform-specific testing.
  - **Future Consideration:** If users request support, could be added with community contributions.

- **NFS-Mounted Project Directories**:
  - **Reason:** `O_CREAT | O_EXCL` atomicity is not guaranteed on NFS v2/v3. While NFS v4 is better, behavior varies by implementation.
  - **Workaround:** Use local filesystem for `.praxis-os/` directory
  - **Future Consideration:** Could add fcntl-based fallback for NFS detection

---

#### Integrations

**Not Included:**

- **MCP Client-Side Deduplication**: 
  - **Reason:** RuntimeLock is a server-side solution. Fixing Cursor's MCP client race condition would require changes to Cursor itself, which is outside our control.
  - **Future Consideration:** If Cursor adds client-side deduplication, RuntimeLock would still provide defense-in-depth.

- **Process Monitoring/Restart (systemd, launchd)**: 
  - **Reason:** praxis-os is a development tool, not a production service. Users run it manually or via Cursor. Automatic restart on crash is not required.
  - **Future Consideration:** If praxis-os evolves to support production deployments, systemd/launchd integration could be added.

---

#### Quality Levels

**Not Included:**

- **Sub-Millisecond Lock Acquisition**: 
  - **Reason:** NFR-P1 targets <100ms, which is sufficient for server startup. Sub-millisecond performance would require low-level optimizations (e.g., shared memory, futexes) that add complexity without meaningful benefit.
  - **Future Consideration:** Not planned. 100ms is fast enough for this use case.

- **Formal Verification of Lock Correctness**: 
  - **Reason:** RuntimeLock uses well-established OS primitives (atomic file creation, PID checking). Formal verification (e.g., TLA+, Coq) would be overkill for a development tool.
  - **Future Consideration:** Not planned. Comprehensive testing (NFR-M3) is sufficient.

---

## 6.1 Future Enhancements

**Potential Phase 2 (If User Demand):**
- CLI tool for lock status (`praxis-os lock status` to show current holder PID)
- Lock metrics collection (lock acquisition time, stale lock frequency)
- Enhanced error recovery (automatic server restart on lock acquisition failure)

**Potential Phase 3 (If Distributed Deployment):**
- Distributed lock management (Redis/etcd backend)
- Multi-machine coordination
- Cloud-native deployment support

**Explicitly Not Planned:**
- Lock timeout/expiration (incompatible with singleton model)
- Lock priority/preemption (no use case)
- MCP client-side fixes (outside our control)

---

## 6.2 Supporting Documentation

Out-of-scope items from:
- **Runtime Lock Design Document** (`supporting-docs/design-doc-runtime-lock.md`):
  - Alternative approaches considered and rejected (Option A, C, D)
  - Port-based locking rejected (overkill, port conflicts)
  - Database-based locking rejected (chicken-egg problem)
  - Systemd socket activation rejected (not cross-platform)

---


