# Code Search Auto-Truncation with Query-Aware Response Sizing

**Specification Package v1.0**

Intelligent truncation of code search results based on query intent to optimize context window usage and improve AI agent efficiency.

---

## 📋 Document Index

This specification package contains 5 documents:

1. **[srd.md](srd.md)** - Software Requirements Document
   - Business goals and success metrics
   - User stories with acceptance criteria
   - 7 Functional Requirements (FR-1 through FR-7)
   - 5 Non-Functional Requirements (NFR-1 through NFR-5)
   - Out of scope items

2. **[specs.md](specs.md)** - Technical Specifications
   - Architecture overview and design decisions
   - Component specifications (TruncationController, TruncationProcessor, SearchCodeHandler)
   - API design with request/response formats
   - Data models and validation rules
   - Security and performance design

3. **[tasks.md](tasks.md)** - Implementation Plan
   - 4 implementation phases with time estimates (5-8 hours total)
   - Detailed tasks with action items and acceptance criteria
   - Dependencies and critical path
   - Validation gates for each phase

4. **[implementation.md](implementation.md)** - Implementation Guidance
   - 6 code patterns with good/bad examples
   - Comprehensive testing strategy (60 test cases, 90% coverage target)
   - Deployment procedures and rollback strategy
   - Troubleshooting guide with 6 common issues

5. **[README.md](README.md)** - This Document
   - Package overview and navigation
   - Quick start by role
   - Key metrics and success criteria

---

## 🚀 Quick Start by Role

### For Product Managers
**Start here:** [srd.md](srd.md)
- Read Section 1 (Business Goals) for success metrics
- Review Section 2 (User Stories) for user impact
- Check Section 7 (Acceptance Criteria) for validation

**Key Metrics:**
- 70% average token reduction for code search
- 80% reduction in temp file occurrences
- 3.4x increase in queries per context window
- <10ms P95 truncation overhead

### For Architects
**Start here:** [specs.md](specs.md)
- Read Section 1 (Architecture Overview) for design decisions
- Review Section 2 (Component Design) for system structure
- Check Section 5 (Security Design) for security considerations
- Review Section 6 (Performance Design) for scalability

**Key Design Decisions:**
- Post-processing approach (no indexing changes)
- Reuse existing QueryClassifier (no new dependencies)
- Backwards compatible (existing queries work unchanged)
- Graceful degradation (classifier failure → safe default)

### For Developers
**Start here:** [implementation.md](implementation.md)
- Read Section 1 (Implementation Philosophy) for core principles
- Review Section 3 (Code Patterns) for implementation guidance
- Check Section 4 (Testing Strategy) for test requirements
- Reference Section 6 (Troubleshooting) when debugging

**Implementation Order:**
1. Phase 1: Core Truncation Logic (2-3h)
2. Phase 2: Auto-Detect Integration (1-2h)
3. Phase 3: Documentation (1h)
4. Phase 4: Validation & Metrics (1-2h)

**Quick Reference:**
- File to modify: `.praxis-os/ouroboros/tools/pos_search_project.py`
- New methods: `_determine_truncation`, `_truncate_code_chunks`, `_find_truncation_point`
- Test coverage target: ≥90%
- Performance target: <10ms P95

### For QA Engineers
**Start here:** [implementation.md](implementation.md) Section 4 (Testing Strategy)
- Review testing/requirements-list.md for all 12 requirements
- Check testing/functional-tests.md for 38 functional test cases
- Review testing/nonfunctional-tests.md for 22 NFR test cases
- Reference testing/test-strategy.md for execution approach

**Test Execution:**
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=.praxis-os/ouroboros/tools/pos_search_project \
       --cov-report=html \
       --cov-fail-under=90

# Run performance tests
pytest tests/performance/ -v --benchmark-only
```

**Test Coverage:**
- 55 test functions (28 unit + 21 integration + 5 performance + 1 coverage)
- 60 detailed test cases
- 100% requirement coverage (all 12 requirements mapped to tests)

### For DevOps Engineers
**Start here:** [implementation.md](implementation.md) Section 5 (Deployment)
- Review deployment steps (5-step process)
- Check rollback strategy (5-minute rollback)
- Review monitoring and alerts
- Check success criteria for validation

**Deployment Summary:**
- **Type:** In-place update (no new services)
- **Risk:** LOW (post-processing only, backwards compatible)
- **Time:** ~5 minutes (2 min deployment + 3 min verification)
- **Rollback:** Single file restore from git (5 minutes)
- **No migrations:** No database or index changes required

---

## 📊 Key Metrics

### Business Impact
- **Token Reduction:** 70% average (from 6,000 to 1,800 tokens per query)
- **Temp File Reduction:** 80% (fewer large responses)
- **Context Window Capacity:** 3.4x increase (more queries per session)
- **Query Distribution:** 80% conceptual/location, 15% implementation, 5% critical/troubleshooting

### Technical Metrics
- **Performance:** <10ms P95 truncation overhead
- **Reliability:** Graceful degradation (classifier failure → 100-line default)
- **Coverage:** 90%+ test coverage
- **Backwards Compatibility:** 100% (existing queries work unchanged)

### Requirements Summary
- **Functional Requirements:** 7 (FR-1 through FR-7)
- **Non-Functional Requirements:** 5 (NFR-1 through NFR-5)
- **Total Requirements:** 12
- **Test Cases:** 60 (38 functional + 22 non-functional)
- **Test Functions:** 55

---

## 🎯 Feature Overview

### What is Auto-Truncation?

Intelligent truncation of code search results based on query intent:
- **Conceptual queries** ("How does X work?") → 100 lines (entry point + overview)
- **Location queries** ("Where is X?") → 50 lines (signature only)
- **Implementation queries** ("How to implement X?") → Full chunks (no truncation)
- **Critical queries** ("Key patterns in X") → 150 lines (key methods + patterns)
- **Troubleshooting queries** ("Common X errors") → Full chunks (error paths + edge cases)

### How It Works

1. **Query Classification:** Existing `QueryClassifier` detects query angle (conceptual, location, implementation, critical, troubleshooting)
2. **Threshold Mapping:** Angle maps to truncation threshold (100, 50, None, 150, None)
3. **Smart Truncation:** Truncate at natural code boundaries (method/class ends) to preserve semantic integrity
4. **Metadata Enrichment:** Add comprehensive metadata (`truncated`, `full_line_count`, `truncation_point`, `hint`)
5. **Explicit Override:** Users can override with `truncate=False` or `truncate=200` (explicit line count)

### Key Benefits

1. **Optimized Context Window:** 70% token reduction means 3.4x more queries per session
2. **Reduced Client Issues:** 80% fewer temp file writes (no more Cline crashes)
3. **Query-Aware:** Different query types get appropriate content (not one-size-fits-all)
4. **Self-Teaching:** Metadata guides users to optimal query patterns
5. **Backwards Compatible:** Existing queries work unchanged (auto-detect applied by default)
6. **Graceful Degradation:** System continues working even if QueryClassifier fails

---

## 🛠️ Implementation Phases

### Phase 1: Core Truncation Logic (2-3 hours)
- Add `truncate` parameter to `_handle_search_code`
- Implement `_determine_truncation()` method
- Implement `_find_truncation_point()` helper
- Implement `_truncate_code_chunks()` method
- Write unit tests for core methods

### Phase 2: Auto-Detect Integration (1-2 hours)
- Integrate QueryClassifier into `_determine_truncation()`
- Add `truncation_reason` metadata to responses
- Write integration tests for auto-detect

### Phase 3: Documentation (1 hour)
- Update `pos_search_project` tool docstring
- Create usage standard document
- Update distribution files

### Phase 4: Validation & Metrics (1-2 hours)
- Implement performance benchmarks
- Implement behavioral metrics tracking
- Validate success criteria
- Write edge case tests

**Total Time:** 5-8 hours (1 day)

---

## ✅ Success Criteria

### Immediate (Day 1)
- All smoke tests pass ✅
- No errors in logs ✅
- Performance <10ms P95 ✅
- Search functionality unchanged ✅

### Short-term (Week 1)
- Token reduction ~70% ✅
- Temp file frequency reduced ~80% ✅
- No user-reported issues ✅
- Query refinement rate <5% (good classification) ✅

### Long-term (Month 1)
- Angle distribution validates 80/15/5 assumption ✅
- Context window capacity increased 3.4x ✅
- No performance degradation ✅
- Feature adoption (users understand `truncate` parameter) ✅

---

## 📚 Additional Resources

### Supporting Documents
- **Design Document:** `.praxis-os/workspace/design/2025-11-16-code-search-auto-truncation.md`
- **Testing Documentation:** `testing/` directory
  - `requirements-list.md` - All 12 requirements
  - `traceability-matrix.md` - Requirements → tests mapping
  - `functional-tests.md` - 38 functional test cases
  - `nonfunctional-tests.md` - 22 NFR test cases
  - `test-strategy.md` - Testing approach and execution

### Standards References
- **Tool Usage:** `.praxis-os/standards/universal/tools/pos-search-project-usage-guide.md`
- **Behavioral Engineering:** `.praxis-os/standards/development/behavioral-engineering-patterns.md`
- **Testing Patterns:** `.praxis-os/standards/development/testing-patterns.md`

### Code References
- **File to Modify:** `.praxis-os/ouroboros/tools/pos_search_project.py`
- **Distribution File:** `dist/ouroboros/tools/pos_search_project.py`
- **QueryClassifier:** `.praxis-os/ouroboros/middleware/query_classifier.py`
- **AST Chunker:** `.praxis-os/ouroboros/subsystems/rag/code/ast_chunker.py`

---

## 🔄 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-16 | AI Agent (Cursor) | Initial specification package created via `spec_creation_v1` workflow |

---

## 📞 Questions?

**For specification questions:**
- Review relevant document from index above
- Check troubleshooting guide in implementation.md Section 6
- Reference design document for detailed rationale

**For implementation questions:**
- Start with implementation.md Section 3 (Code Patterns)
- Check implementation.md Section 6 (Troubleshooting)
- Review test examples in testing/ directory

**For testing questions:**
- Review testing/test-strategy.md for approach
- Check testing/functional-tests.md for test cases
- Reference implementation.md Section 4 for execution commands

---

**Ready to implement?** Start with [implementation.md](implementation.md) and follow the 4-phase plan!

---

