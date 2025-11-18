# Document References

## Embedded Documents

### Runtime Lock Singleton Enforcement (Design Doc)
**File:** `design-doc-runtime-lock.md`  
**Original Source:** `.praxis-os/workspace/design/2025-11-17-runtime-lock-singleton-enforcement.md` (gitignored)  
**Purpose:** Comprehensive design document analyzing the zombie server problem, evaluating 4 design options, and proposing the RuntimeLock solution

**Key Content:**
- Problem statement with evidence (5 zombie processes observed)
- Root cause analysis (InitLock releases too early)
- 4 design options evaluated (A, B, C, D)
- Approved solution: Option B - Create Separate RuntimeLock Class
- Complete implementation plan with code examples
- Testing strategy (unit, integration, stress tests)
- Risk analysis and mitigations

**Decision Status:** ✅ APPROVED (2025-11-17)

---

**Note:** This design doc was copied from the workspace/ directory (gitignored) into the spec bundle so it becomes part of the committed specification and is version controlled with the spec.

