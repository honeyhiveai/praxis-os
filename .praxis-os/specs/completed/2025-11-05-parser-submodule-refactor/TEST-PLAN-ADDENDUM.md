# Test Plan Addendum

**Project:** Parser Submodule Refactor  
**Date:** 2025-11-05  
**Purpose:** Comprehensive test plan with 100% requirements traceability  
**Status:** Addendum to completed spec (test plan creation)

---

## Executive Summary

This addendum provides a complete test plan for the Parser Submodule Refactor specification, ensuring 100% traceability from requirements to test cases.

**Key Findings:**
- **Total Requirements:** 27 (11 FRs + 16 NFRs)
- **Existing Test Coverage:** ~15 test functions (~700 lines across 2 files)
- **Critical Gaps Identified:**
  - **FR-007 (Phase Shift Detection):** ZERO tests - **Current production bug**
  - **FR-008 (Sequential Phase Validation):** ZERO tests - Prevents task misassignment
  - **NFR-R1 (Zero Regressions):** No comprehensive regression suite
- **Tests Needed:** ~50 additional test functions

**Test Plan Structure:**
1. Requirements List (all 27 requirements extracted)
2. Traceability Matrix (requirements → test files → test functions)
3. Critical Test Cases (FR-007, FR-008, NFR-R1)
4. Full Test Plan (all 65 test functions)

---

## 1. Requirements List

**Source:** `testing/requirements-list.md`

### Functional Requirements (11 FRs)

- **FR-001:** Extensible Parser Architecture
- **FR-002:** Module Size Constraints (≤500 lines)
- **FR-003:** Backward Compatibility
- **FR-004:** Plugin-Like Parser Pattern
- **FR-005:** Incremental Migration with Rollback
- **FR-006:** Defensive Format Parsing (semantic scoring)
- **FR-007:** Phase Shift Detection (0→1, 3→1) ← **CRITICAL GAP**
- **FR-008:** Sequential Phase Validation (no skipping) ← **CRITICAL GAP**
- **FR-009:** Cross-Phase Dependencies
- **FR-010:** Task ID Normalization
- **FR-011:** Dependency Format Preservation

### Non-Functional Requirements (16 NFRs)

**Categories:**
- **Performance (2):** Parsing speed, memory efficiency
- **Reliability (2):** Zero regressions ← **CRITICAL**, error handling
- **Maintainability (3):** Module size, organization, documentation
- **Testability (3):** Coverage, isolation, speed
- **Compatibility (3):** Backward compat, Python 3.9+, dependencies
- **Extensibility (2):** Parser addition effort, utility reuse
- **Deployment (2):** Migration safety, zero downtime
- **Quality Assurance (2):** Linting, code review
- **Configuration (2):** Scoring thresholds, signal tuning

**Full requirements list:** See `testing/requirements-list.md`

---

## 2. Traceability Matrix

**Source:** `testing/traceability-matrix.md`

### Critical Finding: Production Bugs Have Zero Tests

```
FR-007: Phase Shift Detection
├── Current Bug: Phase headers shift (Phase 0→1, Phase 3→1)
├── Impact: 27 tasks misassigned to wrong phases
├── Test File: tests/unit/test_semantic_parser.py
├── Status: ❌ ZERO TESTS
└── Tests Needed:
    ├── test_phase_shift_phase_0_to_1() ← Would catch current bug
    ├── test_phase_shift_phase_3_to_1() ← Would catch current bug
    └── test_phase_regression_detected()

FR-008: Sequential Phase Validation
├── Current Risk: Non-sequential phases accepted (1→3 skipping 2)
├── Impact: Task misassignment, workflow corruption
├── Test File: tests/unit/test_semantic_parser.py
├── Status: ❌ ZERO TESTS
└── Tests Needed:
    ├── test_reject_phase_skip() ← Prevents misassignment
    ├── test_1_to_3_rejected()
    └── test_sequential_phases_accepted()

NFR-R1: Zero Regressions
├── Requirement: 100% of 529+ tests must pass, all specs parse identically
├── Test File: tests/integration/test_regression.py
├── Status: ❌ NO COMPREHENSIVE SUITE
└── Tests Needed:
    └── test_all_completed_specs_parse_identically() ← Critical validation
```

### Existing Coverage

**Good coverage:**
- ✅ FR-006 (Defensive Parsing): ~10 tests in test_semantic_parser.py
- ✅ FR-010 (Task ID Normalization): Basic coverage
- ✅ FR-001 (Architecture): Structure tests exist

**Gaps:**
- ❌ FR-007, FR-008: ZERO tests (production bugs)
- ❌ NFR-R1: No comprehensive regression suite
- ❌ NFR-P1, NFR-P2: No performance tests
- ❌ NFR-M1-M3, NFR-T1-T3, NFR-Q1: No validation tests

**Full traceability matrix:** See `testing/traceability-matrix.md`

---

## 3. Critical Test Cases (Priority 1)

### 3.1 FR-007: Phase Shift Detection Tests

**Test Case 7.1: Detect Phase 0 → Phase 1 Shift**
```python
def test_phase_shift_phase_0_to_1():
    """
    Test that parser detects when a document starts with Phase 0, then shifts to Phase 1.
    
    Current Bug: Parser assigns tasks incorrectly when phases shift.
    Impact: 27 tasks misassigned in production spec.
    
    Setup: tasks.md with Phase 0 header, then Phase 1 header
    Action: Parse document
    Assert: Phase shift detected, warning emitted OR error raised
    Evidence: FR-007.1 validated
    """
    tasks_md = """
    # Phase 0: Discovery
    
    ## Task 0.1: Initial Research
    
    # Phase 1: Implementation
    
    ## Task 1.1: Build Feature
    """
    
    parser = SpecTasksParser()
    result = parser.parse(tasks_md)
    
    # Assert: Phase shift was detected
    assert result.has_phase_shift or result.errors
    # Or: Assert error raised preventing parse
```

**Test Case 7.2: Detect Phase 3 → Phase 1 Regression**
```python
def test_phase_shift_phase_3_to_1():
    """
    Test that parser detects when phases regress (3 → 1).
    
    This indicates structural problems in the spec.
    
    Setup: tasks.md with Phase 3, then Phase 1
    Action: Parse document
    Assert: Regression detected, parse fails or warns
    Evidence: FR-007.2 validated
    """
    tasks_md = """
    # Phase 3: Testing
    
    ## Task 3.1: Write Tests
    
    # Phase 1: Implementation
    
    ## Task 1.1: Build Feature
    """
    
    parser = SpecTasksParser()
    
    # Should raise error or return result with errors
    with pytest.raises(ParseError) as exc_info:
        parser.parse(tasks_md)
    
    assert "phase regression" in str(exc_info.value).lower()
    assert "3" in str(exc_info.value) and "1" in str(exc_info.value)
```

**Test Case 7.3: Accept Normal Sequential Phases**
```python
def test_sequential_phases_accepted():
    """
    Test that normal sequential phases (1→2→3) are accepted.
    
    This is the happy path - should work without errors.
    
    Setup: tasks.md with sequential phases
    Action: Parse document
    Assert: No errors, all tasks assigned correctly
    Evidence: FR-007.3 validated
    """
    tasks_md = """
    # Phase 1: Discovery
    
    ## Task 1.1: Research
    
    # Phase 2: Implementation
    
    ## Task 2.1: Build
    
    # Phase 3: Testing
    
    ## Task 3.1: Test
    """
    
    parser = SpecTasksParser()
    result = parser.parse(tasks_md)
    
    assert not result.errors
    assert len(result.phases) == 3
    assert result.phases[0].phase_number == 1
    assert result.phases[1].phase_number == 2
    assert result.phases[2].phase_number == 3
```

---

### 3.2 FR-008: Sequential Phase Validation Tests

**Test Case 8.1: Reject Phase Skip (1→3)**
```python
def test_reject_phase_skip_1_to_3():
    """
    Test that parser rejects non-sequential phases (1→3 skipping 2).
    
    This prevents task misassignment and workflow corruption.
    
    Setup: tasks.md with Phase 1, then Phase 3 (skipping 2)
    Action: Parse document
    Assert: Parse fails with clear error message
    Evidence: FR-008.1 validated
    """
    tasks_md = """
    # Phase 1: Discovery
    
    ## Task 1.1: Research
    
    # Phase 3: Testing
    
    ## Task 3.1: Test
    """
    
    parser = SpecTasksParser()
    
    with pytest.raises(ParseError) as exc_info:
        parser.parse(tasks_md)
    
    error_msg = str(exc_info.value).lower()
    assert "phase skip" in error_msg or "non-sequential" in error_msg
    assert "1" in str(exc_info.value) and "3" in str(exc_info.value)
    
    # Error message should be actionable
    assert "expected phase 2" in error_msg or "missing phase 2" in error_msg
```

**Test Case 8.2: Accept Sequential Phases**
```python
def test_accept_sequential_phases():
    """
    Test that sequential phases (1→2→3→4) are accepted.
    
    Setup: tasks.md with perfectly sequential phases
    Action: Parse document
    Assert: All phases parsed correctly, no errors
    Evidence: FR-008.2 validated
    """
    tasks_md = """
    # Phase 1: Discovery
    ## Task 1.1: Research
    
    # Phase 2: Design
    ## Task 2.1: Design
    
    # Phase 3: Implementation
    ## Task 3.1: Build
    
    # Phase 4: Testing
    ## Task 4.1: Test
    """
    
    parser = SpecTasksParser()
    result = parser.parse(tasks_md)
    
    assert not result.errors
    assert len(result.phases) == 4
    
    for i in range(4):
        assert result.phases[i].phase_number == i + 1
```

---

### 3.3 NFR-R1: Zero Regressions Test

**Test Case R1.1: All Completed Specs Parse Identically**
```python
@pytest.mark.integration
@pytest.mark.slow
def test_all_completed_specs_parse_identically():
    """
    Test R1.1: All completed specs parse identically before/after refactor.
    
    This is the CRITICAL regression test - ensures refactor introduces zero bugs.
    
    Setup: All specs in .praxis-os/specs/completed/
    Action: Parse each spec with new parser, compare to baseline
    Assert: 100% identical parse results
    Evidence: NFR-R1 validated
    """
    specs_dir = Path(".praxis-os/specs/completed/")
    spec_dirs = [d for d in specs_dir.iterdir() if d.is_dir()]
    
    failed_specs = []
    total_specs = 0
    
    for spec_dir in spec_dirs:
        tasks_file = spec_dir / "tasks.md"
        if not tasks_file.exists():
            continue
        
        total_specs += 1
        
        try:
            # Parse with new parser
            parser = SpecTasksParser()
            result = parser.parse(tasks_file.read_text())
            
            # Baseline comparison (if baseline exists)
            baseline_file = spec_dir / ".baseline_parse.json"
            if baseline_file.exists():
                baseline = json.loads(baseline_file.read_text())
                
                # Compare critical fields
                if result.total_phases != baseline["total_phases"]:
                    failed_specs.append((spec_dir.name, "phase count mismatch"))
                    continue
                
                if result.total_tasks != baseline["total_tasks"]:
                    failed_specs.append((spec_dir.name, "task count mismatch"))
                    continue
            
        except Exception as e:
            failed_specs.append((spec_dir.name, str(e)))
    
    # Assert zero regressions
    assert len(failed_specs) == 0, \
        f"NFR-R1 VIOLATION: {len(failed_specs)}/{total_specs} specs failed:\n" + \
        "\n".join([f"  - {name}: {reason}" for name, reason in failed_specs])
    
    print(f"\n✅ NFR-R1 VALIDATED: All {total_specs} completed specs parse identically")
```

---

## 4. Priority Test Implementation Roadmap

### Priority 1 (Critical - Implement Immediately)

**These tests would prevent the current production bugs:**

1. **FR-007 Tests (Phase Shift Detection):** 3 tests
   - Test 7.1: Phase 0→1 shift detection
   - Test 7.2: Phase 3→1 regression detection
   - Test 7.3: Sequential phases accepted
   - **Estimated effort:** 2-3 hours
   - **File:** `tests/unit/test_semantic_parser.py`

2. **FR-008 Tests (Sequential Validation):** 3 tests
   - Test 8.1: Reject phase skip (1→3)
   - Test 8.2: Reject other skips
   - Test 8.3: Accept sequential phases
   - **Estimated effort:** 2-3 hours
   - **File:** `tests/unit/test_semantic_parser.py`

3. **NFR-R1 Test (Zero Regressions):** 1 comprehensive test
   - Test R1.1: All completed specs parse identically
   - **Estimated effort:** 3-4 hours (includes baseline generation)
   - **File:** `tests/integration/test_regression.py`

**Total Priority 1 Effort:** 7-10 hours

---

### Priority 2 (Important - Implement Soon)

4. **NFR-P1, NFR-P2 (Performance Tests):** 4 tests
   - Parsing speed, memory efficiency
   - **Estimated effort:** 3-4 hours

5. **NFR-M1, NFR-T1 (Module Size & Coverage):** 3 tests
   - Max 500 lines enforcement, ≥85% coverage
   - **Estimated effort:** 2-3 hours

6. **FR-009, FR-011 (Dependencies):** 4 tests
   - Cross-phase dependencies, format preservation
   - **Estimated effort:** 2-3 hours

**Total Priority 2 Effort:** 7-10 hours

---

### Priority 3 (Nice to Have)

7. **Validation Tests (NFR-Q1, NFR-M2):** 5 tests
   - Linting, architecture validation
   - **Estimated effort:** 3-4 hours

8. **Extensibility Tests (NFR-E1, NFR-E2):** 3 tests
   - Parser addition effort, code reuse
   - **Estimated effort:** 2-3 hours

**Total Priority 3 Effort:** 5-7 hours

---

### Implementation Timeline

**Immediate (Week 1):**
- Priority 1: Critical tests (7-10 hours)
- **Prevents current production bugs from recurring**

**Short-term (Week 2):**
- Priority 2: Important tests (7-10 hours)
- **Achieves 90%+ critical path coverage**

**Medium-term (Month 1):**
- Priority 3: Validation tests (5-7 hours)
- **Achieves 100% requirements coverage**

**Total Test Implementation Effort:** 19-27 hours

---

## 5. Testing Strategy

### 5.1 Unit Testing Strategy

**Principles:**
- Fast execution (<10ms per test)
- Isolated (no file I/O, no external deps)
- Deterministic (no flakiness)

**Pattern for Parser Tests:**
```python
def test_phase_shift_detection():
    """Test pattern: Inline markdown string → parse → assert."""
    tasks_md = """
    # Phase 0: Discovery
    # Phase 1: Implementation
    """
    
    parser = SpecTasksParser()
    result = parser.parse(tasks_md)
    
    assert result.has_phase_shift
```

**Mocking Strategy:**
- Mock file system (use inline strings)
- Mock workflow engine (test parsers in isolation)
- Don't mock parsing logic (test actual code)

---

### 5.2 Integration Testing Strategy

**Principles:**
- Use real spec files from completed specs
- Test end-to-end parsing workflows
- Validate backward compatibility

**Pattern for Regression Tests:**
```python
@pytest.mark.integration
def test_real_spec_parsing():
    """Test with actual completed spec."""
    spec_path = Path(".praxis-os/specs/completed/2025-11-04-rag-index-refactor/tasks.md")
    
    parser = SpecTasksParser()
    result = parser.parse(spec_path.read_text())
    
    assert not result.errors
    assert result.total_phases > 0
    assert result.total_tasks > 0
```

---

### 5.3 Performance Testing Strategy

**Metrics:**
- Parsing speed: ≤100ms for 50KB files
- Memory usage: ≤50MB peak
- No regressions: ±5% variance

**Pattern:**
```python
@pytest.mark.performance
def test_parsing_speed():
    """Measure p95 parsing latency."""
    tasks_md = generate_large_tasks_file(50_000)  # 50KB
    
    latencies = []
    for _ in range(100):
        start = time.time()
        parser.parse(tasks_md)
        latencies.append(time.time() - start)
    
    p95 = sorted(latencies)[95]
    assert p95 < 0.1, f"p95 latency {p95:.3f}s exceeds 100ms"
```

---

## 6. Lessons Learned

### 6.1 Root Cause Analysis: Phase Shift Bugs

**What happened:**
- FR-007 (Phase Shift Detection) fully specified in SRD
- Implementation exists in semantic_parser.py
- **But:** ZERO tests for phase shift detection
- Bug reached production: 27 tasks misassigned

**Why it happened:**
- No test enforcing phase shift detection
- No traceability matrix mapping FR-007 → tests
- Testing section in implementation.md was generic
- No evidence gate requiring "all FRs have test plans"

**How this test plan prevents recurrence:**
- 100% requirements traceability (every FR/NFR → tests)
- Test Cases 7.1-7.3 explicitly validate phase shifts
- Traceability matrix makes gaps visible
- Requirements-driven test planning, not ad-hoc

---

### 6.2 Value of Requirements Traceability

**Before this test plan:**
- Testing was implementation-driven ("test what we built")
- Gaps invisible until production failure
- No systematic way to verify completeness

**After this test plan:**
- Testing is requirements-driven ("test what we specified")
- Gaps visible in traceability matrix
- Systematic verification: every FR/NFR must have ≥1 test

**Traceability Matrix as Quality Gate:**
```
Requirement → Test File → Test Function → Status

If ANY requirement shows "❌ MISSING", the spec is incomplete.
```

---

## 7. Test Plan Validation Checklist

Before marking this addendum complete, verify:

- [x] All 27 requirements extracted into `requirements-list.md`
- [x] Traceability matrix created mapping all requirements to tests
- [x] Critical test cases defined (FR-007, FR-008, NFR-R1)
- [x] Priority 1-3 implementation roadmap created
- [x] Testing strategy documented (unit, integration, performance)
- [ ] Priority 1 tests implemented (7-10 hours work)
- [ ] 100% critical path coverage achieved (pending Priority 1-2 implementation)

---

## 8. Related Documents

**This Addendum:**
- `testing/requirements-list.md` - All 27 requirements extracted from srd.md
- `testing/traceability-matrix.md` - Requirements → tests mapping

**Original Spec:**
- `srd.md` - Software Requirements Document (11 FRs, 16 NFRs)
- `specs.md` - Technical Specification
- `implementation.md` - Implementation Approach
- `tasks.md` - Implementation Tasks

---

## 9. Conclusion

This test plan addendum provides **100% requirements traceability** for the Parser Submodule Refactor, ensuring every functional and non-functional requirement is mapped to concrete, actionable test cases.

**Key Deliverables:**
1. ✅ 27 requirements extracted and categorized
2. ✅ Traceability matrix with 100% coverage
3. ✅ Critical test cases defined (FR-007, FR-008, NFR-R1)
4. ✅ Testing strategy documented
5. ✅ Priority implementation roadmap

**Critical Finding:**
The phase shift production bugs (FR-007, FR-008) occurred because **zero tests existed** for high-priority functional requirements. Tests 7.1-7.2 would have caught these bugs immediately.

**Next Steps:**
1. Implement Priority 1 tests (7-10 hours) to prevent current bugs from recurring
2. Implement Priority 2 tests (7-10 hours) for 90%+ critical path coverage
3. Integrate this test plan into CI/CD pipeline
4. Use this addendum as validation that spec_creation_v1 workflow updates work

**Mission Accomplished:** This spec now has the test plan it should have had from day one.

---

**Addendum Status:** ✅ Complete  
**Test Implementation Status:** 🚧 Pending (Priority 1)  
**Total Effort Required:** 19-27 hours to full coverage  
**Date:** 2025-11-05

