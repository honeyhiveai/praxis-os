# Implementation Tasks
## Code Search Auto-Truncation with Query-Aware Response Sizing

**Project:** Code Search Auto-Truncation  
**Date:** 2025-11-16  
**Status:** Draft - Pending Approval  
**Based on:** srd.md (requirements) + specs.md (design)

---

## Time Estimates

- **Phase 1:** 2-3 hours (Core truncation logic)
- **Phase 2:** 1-2 hours (Auto-detect integration)
- **Phase 3:** 1 hour (Documentation & standards)
- **Phase 4:** 1-2 hours (Validation & metrics)
- **Total:** 5-8 hours (~1 day)

---

## Phase 1: Core Truncation Logic

**Objective:** Implement foundational truncation methods with parameter handling, smart boundary detection, and metadata enrichment

**Estimated Duration:** 2-3 hours

**Deliverables:**
- `_determine_truncation()` method with parameter validation
- `_truncate_code_chunks()` method with smart boundary detection
- `_find_truncation_point()` helper method
- Enhanced `_handle_search_code()` with `truncate` parameter
- Metadata fields added to responses

**Success Criteria:**
- Explicit truncation works (`truncate=False`, `truncate=200`)
- Smart boundaries detected (no mid-method cuts)
- Metadata includes all required fields
- Unit tests pass for all parameter types

### Phase 1 Tasks

- [ ] **Task 1.1**: Add `truncate` parameter to `_handle_search_code` method (M: 1-2h)
  - Add `truncate: Union[bool, int, str] = True` parameter to method signature
  - Update method docstring with parameter documentation and examples
  - Add parameter validation (type checking, value validation)
  - Raise ValueError with examples for invalid parameter types
  - Verify: Parameter accepted, validated, documented

- [ ] **Task 1.2**: Implement `_determine_truncation()` method (M: 1-2h)
  - Create method signature: `_determine_truncation(query, truncate_param) -> Optional[int]`
  - Handle explicit values: `False` → None, `int` → int, `"auto"` → auto-detect
  - Implement default fallback (100 lines) for unknown cases
  - Add error handling for invalid parameter types
  - Verify: All parameter types handled correctly, returns int or None

- [ ] **Task 1.3**: Implement `_find_truncation_point()` helper method (S: 1h)
  - Create method signature: `_find_truncation_point(lines, max_lines) -> int`
  - Implement backwards search (max_lines to max_lines-20)
  - Detect Python boundaries (blank line, `def `, `class `)
  - Fallback to max_lines if no boundary found
  - Verify: Finds natural boundaries, no mid-method cuts

- [ ] **Task 1.4**: Implement `_truncate_code_chunks()` method (M: 2-3h)
  - Create method signature: `_truncate_code_chunks(results, max_lines) -> List[Dict]`
  - For each result: check if truncation needed (len > max_lines)
  - Find truncation point using `_find_truncation_point()`
  - Truncate content at boundary
  - Add inline hint: "\n\n... [truncated: X more lines]\nUse truncate=False..."
  - Add metadata fields: truncated, full_line_count, truncation_point, hint
  - Handle edge cases: empty content, chunk smaller than threshold
  
  **Acceptance Criteria:**
  - [ ] Method signature matches spec: `_truncate_code_chunks(results, max_lines) -> List[Dict]`
  - [ ] Chunks >max_lines are truncated, chunks ≤max_lines unchanged
  - [ ] Truncation occurs at natural boundaries (no mid-method cuts)
  - [ ] All metadata fields present when truncated: truncated=True, full_line_count, truncation_point, hint
  - [ ] Inline hint includes "Use truncate=False" guidance
  - [ ] Edge cases handled: empty content returns unchanged, small chunks not truncated
  - [ ] Unit tests pass for small/medium/large chunks
  - [ ] Zero linter errors on new code

- [ ] **Task 1.5**: Integrate truncation into search flow (S: 1h)
  - In `_handle_search_code`, after search execution
  - Call `_determine_truncation(query, truncate_param)` to get threshold
  - If threshold is not None and action is "search_code":
    - Call `_truncate_code_chunks(results, threshold)`
    - Add `truncation_reason` metadata to response
  - Return enhanced results
  - Verify: Truncation applied when enabled, skipped when disabled

- [ ] **Task 1.6**: Write unit tests for core methods (M: 2h)
  - Test `_determine_truncation`: all parameter types (True/False/int/"auto"/invalid)
  - Test `_find_truncation_point`: boundaries found, fallback, edge cases
  - Test `_truncate_code_chunks`: small/medium/large chunks, metadata
  - Test parameter validation: invalid types raise ValueError
  - Verify: >90% coverage for new methods, all tests pass

---

## Phase 2: Auto-Detect Integration

**Objective:** Integrate QueryClassifier for automatic truncation threshold detection based on query angle

**Estimated Duration:** 1-2 hours

**Deliverables:**
- QueryClassifier integration in `_determine_truncation()`
- Angle-to-threshold mapping (conceptual→100, location→50, etc.)
- `truncation_reason` metadata in responses
- Graceful degradation for classifier failures

**Success Criteria:**
- Auto-detect works for all 5 query angles
- Classifier failure defaults to 100 lines
- `truncation_reason` metadata accurate
- Integration tests pass for each angle

### Phase 2 Tasks

- [ ] **Task 2.1**: Integrate QueryClassifier into `_determine_truncation()` (M: 1-2h)
  - Access existing classifier via `self.prepend_generator.classifier`
  - Call `classifier.classify(query)` to get query angle
  - Extract `primary` angle from classification result
  - Implement angle-to-threshold mapping (conceptual→100, location→50, implementation→None, critical→150, troubleshooting→None)
  - Add graceful degradation: classifier failure → default to 100 lines
  
  **Acceptance Criteria:**
  - [ ] Conceptual queries return 100 lines threshold
  - [ ] Location queries return 50 lines threshold
  - [ ] Implementation queries return None (no truncation)
  - [ ] Critical queries return 150 lines threshold
  - [ ] Troubleshooting queries return None (no truncation)
  - [ ] Classifier failure defaults to 100 lines (no crash)
  - [ ] Integration tests pass for all 5 query angles
  - [ ] Zero linter errors on modified code

- [ ] **Task 2.2**: Add `truncation_reason` metadata to responses (S: 1h)
  - Create `truncation_reason` dict with angle, max_lines, override fields
  - Add to response metadata only if truncation was applied
  - Include detected angle and threshold used
  - Add override guidance: "Use truncate=False to get full chunks"
  - Verify: Metadata present when truncated, absent when not truncated

- [ ] **Task 2.3**: Write integration tests for auto-detect (M: 2h)
  - Test conceptual query → 100 lines truncation
  - Test location query → 50 lines truncation
  - Test implementation query → no truncation
  - Test critical query → 150 lines truncation
  - Test troubleshooting query → no truncation
  - Test classifier failure → defaults to 100 lines
  - Verify: All angles produce correct truncation, metadata accurate

---

## Phase 3: Documentation & Standards

**Objective:** Update tool documentation, create usage standards, and provide comprehensive examples

**Estimated Duration:** 1 hour

**Deliverables:**
- Updated `pos_search_project` docstring with `truncate` parameter
- Usage examples for all parameter types
- Standard document explaining truncation behavior
- Troubleshooting guide for edge cases

**Success Criteria:**
- Docstring includes all parameter types with examples
- Standard document published
- Examples are copy-paste ready
- Troubleshooting guide covers common issues

### Phase 3 Tasks

- [ ] **Task 3.1**: Update `pos_search_project` tool docstring (S: 30min)
  - Add `truncate` parameter documentation to docstring
  - Include parameter behavior table (True/False/int/"auto")
  - Add 3-4 usage examples (auto-detect, explicit override, custom line count)
  - Document response metadata fields (truncated, full_line_count, hint)
  - Verify: Docstring complete, examples copy-paste ready

- [ ] **Task 3.2**: Create usage standard document (M: 1-2h)
  - Create `.praxis-os/standards/universal/tools/code-search-truncation.md`
  - Document truncation behavior by query angle
  - Explain when to use `truncate=False` (implementation queries)
  - Provide troubleshooting guide (classifier failure, no boundary found)
  - Include performance considerations (<10ms overhead)
  - Add examples for each query type
  - Verify: Standard published, comprehensive, actionable

- [ ] **Task 3.3**: Update distribution files (S: 15min)
  - Sync changes to `dist/ouroboros/tools/pos_search_project.py`
  - Verify distribution matches source
  - Test MCP server restart (hot reload)
  - Verify: Distribution synced, server restarts cleanly

---

## Phase 4: Validation & Metrics

**Objective:** Implement comprehensive testing, performance benchmarks, and behavioral metrics tracking

**Estimated Duration:** 1-2 hours

**Deliverables:**
- Unit tests (>90% coverage)
- Integration tests (all angles)
- Performance benchmarks (<10ms target)
- Behavioral metrics (token reduction, temp file frequency)
- Success criteria validation

**Success Criteria:**
- Test coverage >90%
- All tests pass
- Performance <10ms p95
- 70% token reduction achieved
- 80% temp file reduction achieved

### Phase 4 Tasks

- [ ] **Task 4.1**: Implement performance benchmarks (M: 1-2h)
  - Create benchmark script for truncation overhead measurement
  - Test scenarios: small chunks (<100 lines), medium (500 lines), large (2000 lines)
  - Measure p50, p95, p99 latency for truncation
  - Validate <10ms p95 target met
  - Test concurrent requests (100 queries)
  - Verify: Benchmarks pass, <10ms p95 achieved

- [ ] **Task 4.2**: Implement behavioral metrics tracking (M: 1-2h)
  - Add token counting to measure reduction (before/after truncation)
  - Track temp file frequency (response size >30 KB)
  - Track query refinement rate (`truncate=False` after truncated response)
  - Track angle distribution (validate 80/15/5 assumption)
  - Add metrics to response metadata (truncation_time_ms, token_reduction)
  - Verify: Metrics tracked, 70% token reduction achieved

- [ ] **Task 4.3**: Validate success criteria (S: 1h)
  - Run full test suite (unit + integration + performance)
  - Verify test coverage >90%
  - Validate 70% token reduction (6,000 → 1,800 tokens avg)
  - Validate 80% temp file reduction (40% → 8% frequency)
  - Validate <10ms truncation overhead (p95)
  - Verify backwards compatibility (existing queries work)
  - Document results in validation report
  - Verify: All success criteria met, report complete

- [ ] **Task 4.4**: Write edge case tests (S: 1h)
  - Test empty query → ValueError
  - Test empty content → No truncation
  - Test chunk smaller than threshold → No truncation
  - Test no boundary found → Fallback to max_lines
  - Test very large `truncate` value → Bounded by chunk size
  - Test invalid parameter types → ValueError with examples
  - Verify: All edge cases handled gracefully

---

## Dependencies

### Phase Dependencies

**Phase 1 → Phase 2:**
Phase 2 (Auto-Detect Integration) depends on Phase 1 (Core Truncation Logic) being complete.
Cannot integrate QueryClassifier without foundational truncation methods (`_determine_truncation`, `_truncate_code_chunks`, `_find_truncation_point`).

**Phase 2 → Phase 3:**
Phase 3 (Documentation) depends on Phase 2 (Auto-Detect) being complete.
Cannot document auto-detect behavior without implementation complete and tested.

**Phase 3 → Phase 4:**
Phase 4 (Validation) depends on Phases 1-3 being complete.
Cannot validate success criteria without full implementation and documentation.

### Task Dependencies

**Phase 1:**
- Task 1.1 → Task 1.2: `_determine_truncation()` needs `truncate` parameter defined
- Task 1.3 (parallel with 1.2): `_find_truncation_point()` independent
- Task 1.4 → Task 1.3: `_truncate_code_chunks()` calls `_find_truncation_point()`
- Task 1.5 → Tasks 1.2, 1.4: Integration needs both methods complete
- Task 1.6 (parallel with 1.5): Unit tests can be written alongside integration

**Phase 2:**
- Task 2.1 → Phase 1 complete: QueryClassifier integration needs `_determine_truncation()` method
- Task 2.2 → Task 2.1: Metadata needs angle detection working
- Task 2.3 (parallel with 2.2): Integration tests can be written alongside metadata

**Phase 3:**
- Task 3.1 → Phase 2 complete: Docstring needs auto-detect behavior finalized
- Task 3.2 (parallel with 3.1): Standard doc can be written alongside docstring
- Task 3.3 → Tasks 3.1, 3.2: Distribution sync after all changes complete

**Phase 4:**
- Task 4.1 (parallel): Benchmarks independent
- Task 4.2 (parallel): Metrics tracking independent
- Task 4.3 → All previous tasks: Validation needs everything complete
- Task 4.4 (parallel with 4.1-4.3): Edge case tests can run alongside

### Execution Order

**Linear Path (Critical):**
```
1.1 → 1.2 → 1.4 → 1.5 → 2.1 → 2.2 → 3.1 → 3.3 → 4.3
```

**Parallel Opportunities:**
```
Phase 1:
├── 1.1 → 1.2 ────┐
├── 1.3 ──────────┤
└─────────────────→ 1.4 → 1.5
                             ├── 1.6 (parallel)

Phase 2:
├── 2.1 → 2.2
└── 2.3 (parallel with 2.2)

Phase 3:
├── 3.1
├── 3.2 (parallel)
└── 3.3 (after 3.1+3.2)

Phase 4:
├── 4.1 (parallel)
├── 4.2 (parallel)
├── 4.4 (parallel)
└── 4.3 (after all)
```

**Critical Path:** 1.1 → 1.2 → 1.4 → 1.5 → 2.1 → 2.2 → 3.1 → 3.3 → 4.3 (~5-6 hours)

**Parallel Savings:** ~2-3 hours (tasks 1.3, 1.6, 2.3, 3.2, 4.1, 4.2, 4.4 can run concurrently)

---

## Validation Gates

### Phase 1 Validation Gate

Before advancing to Phase 2:
- [ ] All Phase 1 tasks (1.1-1.6) completed
- [ ] `truncate` parameter added and validated
- [ ] All three methods implemented: `_determine_truncation`, `_truncate_code_chunks`, `_find_truncation_point`
- [ ] Truncation integrated into search flow
- [ ] Unit tests passing (>90% coverage for new methods)
- [ ] Explicit truncation works: `truncate=False`, `truncate=200`
- [ ] Smart boundaries detected (no mid-method cuts)
- [ ] Metadata complete: truncated, full_line_count, truncation_point, hint
- [ ] Zero linter errors on modified code
- [ ] Code reviewed and approved

**Exit Criteria:** Core truncation logic functional, tested, and ready for QueryClassifier integration

---

### Phase 2 Validation Gate

Before advancing to Phase 3:
- [ ] All Phase 2 tasks (2.1-2.3) completed
- [ ] QueryClassifier integrated into `_determine_truncation()`
- [ ] All 5 query angles mapped correctly (conceptual→100, location→50, implementation→None, critical→150, troubleshooting→None)
- [ ] `truncation_reason` metadata added to responses
- [ ] Graceful degradation working (classifier failure → 100 lines default)
- [ ] Integration tests passing for all 5 angles
- [ ] Auto-detect working end-to-end
- [ ] Zero linter errors on modified code
- [ ] Code reviewed and approved

**Exit Criteria:** Auto-detect truncation fully functional, tested, and ready for documentation

---

### Phase 3 Validation Gate

Before advancing to Phase 4:
- [ ] All Phase 3 tasks (3.1-3.3) completed
- [ ] Tool docstring updated with `truncate` parameter
- [ ] Usage examples complete and copy-paste ready
- [ ] Standard document published (`.praxis-os/standards/universal/tools/code-search-truncation.md`)
- [ ] Troubleshooting guide complete
- [ ] Distribution files synced (`dist/ouroboros/tools/pos_search_project.py`)
- [ ] MCP server restart successful (hot reload verified)
- [ ] Documentation reviewed and approved

**Exit Criteria:** Feature fully documented, standard published, ready for validation

---

### Phase 4 Validation Gate

Before marking project complete:
- [ ] All Phase 4 tasks (4.1-4.4) completed
- [ ] Performance benchmarks passing (<10ms p95 truncation overhead)
- [ ] Behavioral metrics tracked (token reduction, temp file frequency)
- [ ] All tests passing (unit + integration + performance + edge cases)
- [ ] Test coverage >90%
- [ ] Success criteria validated:
  - [ ] 70% token reduction achieved (6,000 → 1,800 tokens avg)
  - [ ] 80% temp file reduction achieved (40% → 8% frequency)
  - [ ] <10ms truncation overhead (p95)
  - [ ] Backwards compatibility maintained
- [ ] Zero linter errors across all modified files
- [ ] Code reviewed and approved
- [ ] Validation report complete

**Exit Criteria:** All success criteria met, feature production-ready

---

## Project Completion Criteria

- [ ] All 4 phases completed with validation gates passed
- [ ] All 16 tasks completed with acceptance criteria met
- [ ] srd.md (requirements) finalized
- [ ] specs.md (technical design) finalized
- [ ] tasks.md (implementation plan) finalized
- [ ] Code implementation complete and tested
- [ ] Documentation complete (docstrings + standard)
- [ ] Success metrics validated:
  - [ ] 70% token reduction
  - [ ] 80% temp file reduction
  - [ ] <10ms performance overhead
  - [ ] >90% test coverage
- [ ] Feature deployed and monitored
- [ ] Stakeholders notified

**Total Estimated Time:** 5-8 hours (1 day)

---

