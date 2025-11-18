# Implementation Approach
## Code Search Auto-Truncation with Query-Aware Response Sizing

**Project:** Code Search Auto-Truncation  
**Date:** 2025-11-16  
**Based on:** specs.md (design) + tasks.md (implementation plan)

---

## 1. Implementation Philosophy

**Core Principles:**
1. **Post-Processing Enhancement:** Truncation happens after search, not during indexing - zero impact on existing system
2. **Backwards Compatibility:** Existing queries work unchanged, new parameter has safe default
3. **Test-Driven Development:** Write tests alongside implementation, target >90% coverage
4. **Incremental Delivery:** 4 phases with validation gates, each phase independently valuable
5. **Elegant Integration:** Reuse existing QueryClassifier, no new dependencies

**Design Philosophy:**
- Optimize for the common case (80% of queries need high-level info)
- Provide escape hatch for edge cases (`truncate=False`)
- Self-documenting via metadata (teach users how to get full chunks)
- Fail gracefully (classifier failure → safe default)

---

## 2. Implementation Order

Follow the phased approach from tasks.md:

**Phase 1: Core Truncation Logic** (2-3 hours)
- Foundational methods with parameter handling
- Smart boundary detection
- Metadata enrichment

**Phase 2: Auto-Detect Integration** (1-2 hours)
- QueryClassifier integration
- Angle-based threshold mapping
- Graceful degradation

**Phase 3: Documentation** (1 hour)
- Tool docstring updates
- Usage standard document
- Distribution sync

**Phase 4: Validation & Metrics** (1-2 hours)
- Comprehensive testing
- Performance benchmarks
- Success criteria validation

**Total: 5-8 hours (1 day)**

---

## 3. Code Patterns

### Pattern 1: Parameter Validation with Clear Error Messages

**Purpose:** Validate `truncate` parameter with actionable error messages

**Good Example:**
```python
def _determine_truncation(
    self,
    query: str,
    truncate_param: Optional[Union[bool, int, str]]
) -> Optional[int]:
    """Determine truncation based on query intent."""
    
    # Explicit values override auto-detect
    if truncate_param is False:
        return None  # No truncation
    
    if isinstance(truncate_param, int):
        if truncate_param <= 0:
            raise ValueError(
                f"Invalid truncate line count: {truncate_param}. "
                "Must be positive integer. Examples: truncate=100, truncate=200"
            )
        return truncate_param
    
    if isinstance(truncate_param, str):
        if truncate_param != "auto":
            raise ValueError(
                f"Invalid truncate string value: '{truncate_param}'. "
                "Must be 'auto'. Examples: truncate='auto', truncate=True, truncate=False"
            )
        # Fall through to auto-detect
    
    # Auto-detect based on query angle
    if truncate_param is True or truncate_param == "auto":
        # ... auto-detect logic
        pass
    
    return 100  # Fallback default
```

**Why This Works:**
- ✅ Strict type checking prevents unexpected behavior
- ✅ Clear error messages with examples
- ✅ Explicit handling of each parameter type
- ✅ Safe fallback default

**Anti-Pattern (What NOT to Do):**
```python
# BAD: Vague error, no examples
if not valid(truncate_param):
    raise ValueError("Invalid parameter")

# BAD: Silent failure
if isinstance(truncate_param, int) and truncate_param <= 0:
    truncate_param = 100  # Silently changes user input!
```

---

### Pattern 2: Angle-Based Mapping with Graceful Degradation

**Purpose:** Map query angles to truncation thresholds with fallback

**Good Example:**
```python
def _determine_truncation(
    self,
    query: str,
    truncate_param: Optional[Union[bool, int, str]]
) -> Optional[int]:
    """Determine truncation based on query intent."""
    
    # ... parameter validation (see Pattern 1)
    
    # Auto-detect based on query angle
    if truncate_param is True or truncate_param == "auto":
        try:
            # Access existing classifier
            result = self.prepend_generator.classifier.classify(query)
            angle = result.primary
        except (AttributeError, Exception) as e:
            # Graceful degradation: classifier unavailable
            logger.warning(
                f"QueryClassifier unavailable, defaulting to 100 lines: {e}"
            )
            return 100  # Safe default
        
        # Map angle to truncation strategy
        truncation_map = {
            "conceptual": 100,      # Entry point + overview
            "location": 50,         # Signature only
            "implementation": None, # Full implementation
            "critical": 150,        # Key methods + patterns
            "troubleshooting": None # Error paths + edge cases
        }
        
        return truncation_map.get(angle, 100)  # Default: 100 for unknown angles
    
    return 100  # Fallback
```

**Why This Works:**
- ✅ Reuses existing QueryClassifier (no new dependencies)
- ✅ Graceful degradation on classifier failure
- ✅ Clear mapping with comments explaining each threshold
- ✅ Safe default for unknown angles
- ✅ Logging for debugging

**Anti-Pattern (What NOT to Do):**
```python
# BAD: No error handling, will crash if classifier fails
angle = self.prepend_generator.classifier.classify(query).primary

# BAD: Hard-coded values without explanation
if angle == "conceptual":
    return 100  # Why 100? Not clear

# BAD: No default for unknown angles
return truncation_map[angle]  # KeyError if angle not in map!
```

---

### Pattern 3: Smart Boundary Detection

**Purpose:** Truncate at natural code boundaries (method/class ends)

**Good Example:**
```python
def _find_truncation_point(self, lines: List[str], max_lines: int) -> int:
    """Find natural truncation point at method boundary.
    
    Looks backwards from max_lines for method boundary to avoid cutting mid-method.
    
    Args:
        lines: List of code lines
        max_lines: Target truncation line
        
    Returns:
        Actual truncation line (natural boundary)
    """
    # Start at max_lines, look backwards up to 20 lines for method boundary
    for i in range(max_lines, max(0, max_lines - 20), -1):
        line = lines[i].strip()
        
        # Found end of method (blank line or next def/class)
        if not line or line.startswith("def ") or line.startswith("class "):
            return i
    
    # No natural boundary found within 20 lines, use max_lines as fallback
    return max_lines
```

**Why This Works:**
- ✅ Preserves semantic integrity (no mid-method cuts)
- ✅ Limited search range (20 lines) for performance
- ✅ Language-specific boundaries (Python: `def`, `class`)
- ✅ Safe fallback if no boundary found
- ✅ Clear docstring explaining algorithm

**Anti-Pattern (What NOT to Do):**
```python
# BAD: Hard truncation at exact line (breaks semantic integrity)
def _find_truncation_point(self, lines, max_lines):
    return max_lines  # Always cuts at exact line, may be mid-method!

# BAD: Unbounded search (performance issue)
for i in range(max_lines, 0, -1):  # Could search entire file!
    if is_boundary(lines[i]):
        return i

# BAD: No fallback (could return None or raise exception)
for i in range(max_lines, max_lines - 20, -1):
    if is_boundary(lines[i]):
        return i
# Missing: return max_lines  # Fallback!
```

---

### Pattern 4: Metadata Enrichment for Self-Teaching

**Purpose:** Add comprehensive metadata to teach users how to get full chunks

**Good Example:**
```python
def _truncate_code_chunks(
    self, 
    results: List[Dict[str, Any]], 
    max_lines: int
) -> List[Dict[str, Any]]:
    """Truncate code chunks at method boundaries."""
    truncated_results = []
    
    for result in results:
        content = result.get("content", "")
        lines = content.split("\n")
        
        if len(lines) <= max_lines:
            # No truncation needed
            result["truncated"] = False
            result["full_line_count"] = len(lines)
            truncated_results.append(result)
            continue
        
        # Find natural truncation point
        truncation_point = self._find_truncation_point(lines, max_lines)
        
        # Truncate at natural boundary
        truncated_content = "\n".join(lines[:truncation_point])
        truncated_content += f"\n\n... [truncated: {len(lines) - truncation_point} more lines]"
        truncated_content += f"\nUse truncate=False to get full implementation"
        
        # Add comprehensive metadata
        result["content"] = truncated_content
        result["truncated"] = True
        result["full_line_count"] = len(lines)
        result["truncation_point"] = truncation_point
        result["hint"] = "Use truncate=False to get full chunk"
        
        truncated_results.append(result)
    
    return truncated_results
```

**Why This Works:**
- ✅ Inline hint in content (visible to user)
- ✅ Comprehensive metadata (truncated, full_line_count, truncation_point, hint)
- ✅ Self-teaching (tells user how to get full chunk)
- ✅ Consistent metadata for both truncated and non-truncated results

**Anti-Pattern (What NOT to Do):**
```python
# BAD: No metadata, user doesn't know content was truncated
result["content"] = truncated_content
return result

# BAD: Incomplete metadata (missing hint)
result["truncated"] = True
# Missing: full_line_count, truncation_point, hint

# BAD: No inline hint (user may not check metadata)
result["content"] = truncated_content  # No "... [truncated]" message
result["hint"] = "Use truncate=False"  # Only in metadata
```

---

### Pattern 5: Backwards Compatible API Enhancement

**Purpose:** Add new parameter without breaking existing queries

**Good Example:**
```python
async def _handle_search_code(
    self,
    query: str,
    n_results: int = 3,
    truncate: Union[bool, int, str] = True,  # NEW: Safe default
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Handle code search with optional truncation.
    
    Args:
        query: Search query
        n_results: Number of results (default: 3)
        truncate: Truncation control (default: True for auto-detect)
            - True: Auto-detect based on query angle
            - False: No truncation (full chunks)
            - int: Explicit line count
            - "auto": Same as True (explicit)
        filters: Optional metadata filters
        
    Returns:
        Search results with optional truncation applied
    """
    # Execute search (existing logic - unchanged)
    results = await self.semantic_index.search(query, n_results, filters)
    
    # Apply truncation if enabled (NEW logic)
    if truncate is not False:  # Only skip if explicitly False
        threshold = self._determine_truncation(query, truncate)
        if threshold is not None:
            results = self._truncate_code_chunks(results, threshold)
            # Add truncation_reason metadata
            # ...
    
    return results
```

**Why This Works:**
- ✅ New parameter with safe default (`True` = auto-detect)
- ✅ Existing queries work unchanged (get auto-truncation)
- ✅ Explicit override available (`truncate=False`)
- ✅ Clear docstring with all parameter types
- ✅ Existing logic unchanged (search execution)

**Anti-Pattern (What NOT to Do):**
```python
# BAD: Breaking change (no default, existing queries break)
async def _handle_search_code(self, query, n_results, truncate):
    # Existing queries missing 'truncate' will fail!

# BAD: Unsafe default (changes behavior unexpectedly)
truncate: bool = False  # Default disables feature!

# BAD: No escape hatch (users can't get full chunks)
# Always truncate, no way to disable
```

---

### Pattern 6: Performance-Conscious String Operations

**Purpose:** Efficient string processing with minimal allocations

**Good Example:**
```python
def _truncate_code_chunks(self, results, max_lines):
    """Truncate with efficient string operations."""
    for result in results:
        content = result.get("content", "")
        lines = content.split("\n")  # O(n) - single pass
        
        if len(lines) <= max_lines:
            # No truncation needed - no allocation
            result["truncated"] = False
            result["full_line_count"] = len(lines)
            continue
        
        truncation_point = self._find_truncation_point(lines, max_lines)  # O(20) = O(1)
        truncated_content = "\n".join(lines[:truncation_point])  # O(n) - single allocation
        # ... add metadata
    
    return results
```

**Why This Works:**
- ✅ O(n) complexity where n = lines (bounded by chunk size)
- ✅ Minimal allocations (split, slice, join)
- ✅ No deep copies (list slicing creates views)
- ✅ Bounded search (20 lines max)

**Anti-Pattern (What NOT to Do):**
```python
# BAD: Inefficient string concatenation in loop
truncated = ""
for i in range(truncation_point):
    truncated += lines[i] + "\n"  # O(n²) - creates new string each iteration!

# BAD: Unnecessary deep copy
lines_copy = copy.deepcopy(lines)  # Wastes memory

# BAD: Unbounded search
for i in range(len(lines)):  # Could search entire file!
    if is_boundary(lines[i]):
        break
```

---

## 4. Testing Patterns

### Unit Test Pattern

**Good Example:**
```python
def test_determine_truncation_conceptual_query():
    """Test conceptual query returns 100 lines."""
    tool = POSSearchProject()
    
    # Mock classifier to return conceptual angle
    with patch.object(tool.prepend_generator.classifier, 'classify') as mock_classify:
        mock_classify.return_value = Mock(primary="conceptual")
        
        result = tool._determine_truncation("How does X work?", True)
        
        assert result == 100
        mock_classify.assert_called_once_with("How does X work?")

def test_truncate_code_chunks_preserves_small_chunks():
    """Test chunks smaller than threshold are not truncated."""
    tool = POSSearchProject()
    
    results = [{"content": "line1\nline2\nline3"}]  # 3 lines
    truncated = tool._truncate_code_chunks(results, max_lines=100)
    
    assert truncated[0]["truncated"] == False
    assert truncated[0]["full_line_count"] == 3
    assert "line1\nline2\nline3" == truncated[0]["content"]
```

**Why This Works:**
- ✅ Clear test names (describe what's being tested)
- ✅ Mocking external dependencies (classifier)
- ✅ Specific assertions (exact values, not just "truthy")
- ✅ Edge cases covered (small chunks)

---

## 5. Error Handling Patterns

### Graceful Degradation Pattern

**Good Example:**
```python
try:
    result = self.prepend_generator.classifier.classify(query)
    angle = result.primary
except (AttributeError, Exception) as e:
    logger.warning(
        f"QueryClassifier unavailable, defaulting to 100 lines: {e}"
    )
    return 100  # Safe default
```

**Why This Works:**
- ✅ Catches specific exceptions
- ✅ Logs warning for debugging
- ✅ Returns safe default (system continues working)
- ✅ No user-facing error (graceful degradation)

---

## 6. Documentation Patterns

### Comprehensive Docstring Pattern

**Good Example:**
```python
def _determine_truncation(
    self,
    query: str,
    truncate_param: Optional[Union[bool, int, str]]
) -> Optional[int]:
    """Determine truncation line count based on query intent.
    
    Args:
        query: Search query string
        truncate_param: Truncation control
            - True: Auto-detect based on query angle (default)
            - False: No truncation (full chunks)
            - int: Explicit line count (e.g., 200)
            - "auto": Same as True (explicit auto-detect)
            
    Returns:
        Line count to truncate to, or None for no truncation
        
    Raises:
        ValueError: If truncate_param is invalid type or value
        
    Examples:
        >>> _determine_truncation("How does X work?", True)
        100  # Conceptual query
        
        >>> _determine_truncation("Where is X?", True)
        50  # Location query
        
        >>> _determine_truncation("Any query", False)
        None  # No truncation
        
        >>> _determine_truncation("Any query", 200)
        200  # Explicit line count
    """
```

**Why This Works:**
- ✅ Complete Args documentation with all parameter types
- ✅ Clear Returns description
- ✅ Raises section for error cases
- ✅ Concrete examples for each parameter type
- ✅ Comments explain the "why"

---

## 4. Testing Strategy

### 4.1 Requirements Summary

**Functional Requirements:** 7
- FR-1: Query-Aware Auto-Truncation
- FR-2: Explicit Override Mechanism
- FR-3: Smart Boundary Truncation
- FR-4: Response Metadata
- FR-5: Backwards Compatibility
- FR-6: Query Distribution Optimization
- FR-7: Preserve Docstrings and Signatures

**Non-Functional Requirements:** 5
- NFR-1: Performance (<10ms P95 overhead)
- NFR-2: Reliability (graceful degradation)
- NFR-3: Maintainability (>90% coverage)
- NFR-4: Observability (metrics tracking)
- NFR-5: Usability (self-documenting)

**Total Requirements:** 12

**Source:** `testing/requirements-list.md`

---

### 4.2 Traceability Matrix

**Coverage:**
- FRs mapped to tests: 7/7 (100%)
- NFRs mapped to tests: 5/5 (100%)
- Total test functions: 55

**Test Distribution:**
- Unit tests: 28 (47%)
- Integration tests: 21 (35%)
- Performance tests: 5 (8%)
- Coverage tests: 1 (2%)
- Observability tests: 5 (8%)

**Matrix:** `testing/traceability-matrix.md`

---

### 4.3 Test Cases

**Functional Test Cases:** 38
- FR-1 (Query-Aware): 7 tests
- FR-2 (Override): 6 tests
- FR-3 (Smart Boundaries): 5 tests
- FR-4 (Metadata): 4 tests
- FR-5 (Backwards Compat): 5 tests
- FR-6 (Distribution): 3 tests
- FR-7 (Docstrings): 4 tests
- Integration: 4 tests

**Non-Functional Test Cases:** 22
- Performance: 6 tests
- Reliability: 6 tests
- Maintainability: 3 tests
- Observability: 5 tests
- Usability: 5 tests

**Total Test Cases:** 60

**Details:**
- Functional: `testing/functional-tests.md`
- Non-Functional: `testing/nonfunctional-tests.md`

---

### 4.4 Testing Approach

**Philosophy:**
- Test-Driven Development (TDD)
- Fast, isolated unit tests
- Integration tests for component interactions
- Performance validation (<10ms P95)
- Behavioral verification (80/15/5 distribution)

**Coverage Targets:**
- Overall: ≥90% line coverage (NFR-3)
- Unit tests: ≥95% coverage of truncation logic
- Integration tests: 100% of critical paths
- Edge cases: 100% of error conditions

**Test Organization:**
```
tests/
├── unit/
│   └── test_truncation.py (28 tests)
├── integration/
│   ├── test_search_code.py (13 tests)
│   └── test_metrics.py (8 tests)
├── performance/
│   └── test_truncation_perf.py (5 tests)
└── coverage/
    └── test_coverage.py (1 test)
```

**Execution Time:** ~1 minute total
- Unit: 2-3 seconds
- Integration: 5-10 seconds
- Performance: 30-60 seconds

**Strategy:** `testing/test-strategy.md`

---

### 4.5 Testing Checklist

**Before Implementation:**
- [ ] Review traceability matrix (`testing/traceability-matrix.md`) ✅/❌
- [ ] Review functional test cases (`testing/functional-tests.md`) ✅/❌
- [ ] Review non-functional test cases (`testing/nonfunctional-tests.md`) ✅/❌
- [ ] Review testing strategy (`testing/test-strategy.md`) ✅/❌
- [ ] Set up test environment (pytest, coverage tools) ✅/❌

**During Implementation:**
- [ ] Write tests first/alongside code (TDD) ✅/❌
- [ ] Run tests frequently (after each method) ✅/❌
- [ ] Verify tests pass before moving to next task ✅/❌
- [ ] Check coverage ≥90% for new code ✅/❌
- [ ] Mock external dependencies (QueryClassifier) ✅/❌

**Before Phase Completion:**
- [ ] All 55 test functions implemented ✅/❌
- [ ] All tests passing (0 failures) ✅/❌
- [ ] Coverage target met (≥90%) ✅/❌
- [ ] Performance benchmarks pass (<10ms P95) ✅/❌
- [ ] NFR metrics achieved (token reduction, reliability) ✅/❌
- [ ] Integration tests verify end-to-end flows ✅/❌
- [ ] Edge cases covered (classifier failure, invalid params) ✅/❌

---

### 4.6 Completeness Verification

✅ **All 12 requirements have been:**
1. Extracted into `requirements-list.md` (7 FRs + 5 NFRs)
2. Mapped to 55 test functions in `traceability-matrix.md`
3. Given 60 detailed test cases in `functional-tests.md` and `nonfunctional-tests.md`
4. Covered by comprehensive testing strategy in `test-strategy.md`

**Cross-Check:**
- Requirements in `requirements-list.md`: 12 ✅
- Requirements in `traceability-matrix.md`: 12 ✅
- Requirements in `functional-tests.md`: 7 FRs ✅
- Requirements in `nonfunctional-tests.md`: 5 NFRs ✅
- Test functions in `traceability-matrix.md`: 55 ✅
- Test cases in `functional-tests.md`: 38 ✅
- Test cases in `nonfunctional-tests.md`: 22 ✅
- **Total test cases: 60 ✅**

**No requirements are untested. 100% coverage.**

---

### 4.7 Test Execution Commands

**Run All Tests:**
```bash
pytest tests/ -v
```

**Run Unit Tests Only:**
```bash
pytest tests/unit/ -v
```

**Run Integration Tests Only:**
```bash
pytest tests/integration/ -v
```

**Run Performance Tests:**
```bash
pytest tests/performance/ -v --benchmark-only
```

**Run with Coverage:**
```bash
pytest tests/ --cov=.praxis-os/ouroboros/tools/pos_search_project \
       --cov-report=html \
       --cov-fail-under=90
```

**Run Specific Test:**
```bash
pytest tests/unit/test_truncation.py::test_determine_truncation_conceptual_query -v
```

**View Coverage Report:**
```bash
open htmlcov/index.html
```

---

## 5. Deployment

### 5.1 Deployment Overview

**Deployment Type:** In-place update (no new services)

**Impact:** Low-risk enhancement
- Post-processing only (no indexing changes)
- Backwards compatible (existing queries work unchanged)
- No database migrations required
- No new dependencies

**Deployment Time:** ~5 minutes
- Code deployment: 2 minutes
- Verification: 3 minutes

---

### 5.2 Deployment Steps

**1. Pre-Deployment Validation**
```bash
# Run full test suite
pytest tests/ --cov=.praxis-os/ouroboros/tools/pos_search_project \
       --cov-fail-under=90

# Run linter
flake8 .praxis-os/ouroboros/tools/pos_search_project.py

# Run performance benchmarks
pytest tests/performance/ --benchmark-only
```

**2. Sync Distribution Files**
```bash
# Copy updated file to distribution
cp .praxis-os/ouroboros/tools/pos_search_project.py \
   dist/ouroboros/tools/pos_search_project.py

# Verify sync
diff .praxis-os/ouroboros/tools/pos_search_project.py \
     dist/ouroboros/tools/pos_search_project.py
```

**3. Restart MCP Server**
```bash
# Restart praxis-os MCP server to load new code
# (Method depends on deployment environment)
# Example: systemctl restart praxis-os-mcp
```

**4. Verify Deployment**
```bash
# Test basic search (should work unchanged)
# Use MCP client or Cursor to execute:
pos_search_project(action="search_code", query="How does X work?")

# Verify truncation is applied
# Check response for truncated=True and metadata

# Test explicit override
pos_search_project(action="search_code", query="How does X work?", truncate=False)

# Verify full chunks returned
```

**5. Smoke Test Critical Paths**
- Conceptual query → Truncated to ~100 lines ✅
- Location query → Truncated to ~50 lines ✅
- Implementation query → Full chunks ✅
- Standards search → No truncation ✅
- Error handling → Invalid param returns clear error ✅

---

### 5.3 Environment Variables

**No New Environment Variables Required**

This feature uses existing infrastructure:
- Existing `QueryClassifier` (already configured)
- Existing `SemanticIndex` (no changes)
- Existing `PrependGenerator` (no changes)

**Existing Configuration (unchanged):**
```bash
# MCP Server Configuration
PRAXIS_OS_WORKSPACE=/path/to/workspace
PRAXIS_OS_LOG_LEVEL=INFO

# RAG Configuration (existing)
EMBEDDING_MODEL=microsoft/codebert-base
TARGET_TOKENS=500
```

---

### 5.4 Database Migrations

**No Database Migrations Required**

This feature:
- Does NOT modify the code index
- Does NOT change embeddings
- Does NOT alter database schema
- Is purely post-processing logic

**Index Status:** No rebuild needed ✅

---

### 5.5 Rollback Strategy

**If Deployment Fails:**

**Step 1: Identify Issue Severity**
- Critical (system down): Immediate rollback
- High (incorrect results): Rollback within 5 minutes
- Medium (performance issue): Investigate, rollback if needed
- Low (minor bug): Fix forward

**Step 2: Execute Rollback**
```bash
# Restore previous version from git
git checkout HEAD~1 -- .praxis-os/ouroboros/tools/pos_search_project.py
git checkout HEAD~1 -- dist/ouroboros/tools/pos_search_project.py

# Restart MCP server
# systemctl restart praxis-os-mcp

# Verify rollback
pos_search_project(action="search_code", query="test")
# Should return pre-truncation behavior (full chunks)
```

**Step 3: Verify System Health**
```bash
# Check search functionality
pos_search_project(action="search_code", query="How does X work?")

# Check logs for errors
tail -f /var/log/praxis-os/mcp-server.log

# Verify no performance degradation
# Run performance tests
```

**Step 4: Investigate Root Cause**
- Review error logs
- Check test failures
- Analyze performance metrics
- Identify fix or mitigation

---

### 5.6 Rollback Checklist

**Pre-Deployment (Rollback Preparation):**
- [x] Previous version in git history ✅
- [x] No database migrations (nothing to reverse) ✅
- [x] No new dependencies (nothing to uninstall) ✅
- [x] Rollback tested on local environment ✅

**During Rollback:**
- [ ] Previous version restored from git ✅/❌
- [ ] Distribution files synced ✅/❌
- [ ] MCP server restarted ✅/❌
- [ ] Search functionality verified ✅/❌
- [ ] No errors in logs ✅/❌

**Post-Rollback:**
- [ ] System health normal ✅/❌
- [ ] Performance metrics normal ✅/❌
- [ ] Root cause identified ✅/❌
- [ ] Fix planned ✅/❌

---

### 5.7 Deployment Checklist

**Pre-Deployment:**
- [ ] All 60 tests passing ✅/❌
- [ ] Coverage ≥90% ✅/❌
- [ ] Performance benchmarks pass (<10ms P95) ✅/❌
- [ ] Code reviewed ✅/❌
- [ ] Linter clean (no errors) ✅/❌
- [ ] Documentation updated ✅/❌
- [ ] Standard document created ✅/❌

**Deployment:**
- [ ] Distribution files synced ✅/❌
- [ ] MCP server restarted ✅/❌
- [ ] Basic search works ✅/❌
- [ ] Truncation applied correctly ✅/❌
- [ ] Override mechanism works ✅/❌

**Post-Deployment:**
- [ ] Smoke tests pass (5 critical paths) ✅/❌
- [ ] Logs clean (no errors) ✅/❌
- [ ] Performance normal (<10ms overhead) ✅/❌
- [ ] Behavioral metrics tracking ✅/❌
- [ ] No user-reported issues ✅/❌

**Validation (24 hours post-deployment):**
- [ ] Token reduction metrics validate 70% reduction ✅/❌
- [ ] Temp file frequency reduced by 80% ✅/❌
- [ ] Query angle distribution matches 80/15/5 ✅/❌
- [ ] No performance degradation ✅/❌
- [ ] No reliability issues ✅/❌

---

### 5.8 Monitoring and Alerts

**Metrics to Monitor:**
1. **Performance:**
   - Truncation overhead (P95 <10ms)
   - Search latency (no degradation)
   - MCP server response time

2. **Behavioral:**
   - Token reduction per query (target: 70%)
   - Temp file frequency (target: 80% reduction)
   - Query refinement rate (truncate=False after truncated)
   - Angle distribution (validate 80/15/5)

3. **Reliability:**
   - Error rate (should be 0%)
   - Classifier availability (graceful degradation if down)
   - Search success rate (should be 100%)

**Alerts (if applicable):**
- Performance degradation (P95 >15ms)
- High error rate (>1%)
- Classifier failures (>10%)

**Logging:**
```python
# Existing logging infrastructure
logger.info(f"Truncation applied: {angle} → {max_lines} lines")
logger.warning(f"QueryClassifier unavailable, defaulting to 100 lines")
logger.error(f"Truncation failed: {error}")
```

---

### 5.9 Deployment Risk Assessment

**Risk Level:** LOW

**Why Low Risk:**
1. **Post-processing only:** No changes to indexing or search logic
2. **Backwards compatible:** Existing queries work unchanged
3. **Graceful degradation:** Classifier failure → safe default
4. **No dependencies:** Uses existing infrastructure
5. **No migrations:** No database changes
6. **Easily reversible:** Single file rollback

**Mitigation:**
- Comprehensive test coverage (60 tests, 90% coverage)
- Performance validation (<10ms overhead)
- Gradual rollout (can test on single client first)
- Monitoring and alerts (detect issues early)
- Fast rollback (5 minutes to restore)

---

### 5.10 Success Criteria

**Immediate (Day 1):**
- [ ] All smoke tests pass ✅/❌
- [ ] No errors in logs ✅/❌
- [ ] Performance <10ms P95 ✅/❌
- [ ] Search functionality unchanged ✅/❌

**Short-term (Week 1):**
- [ ] Token reduction ~70% ✅/❌
- [ ] Temp file frequency reduced ~80% ✅/❌
- [ ] No user-reported issues ✅/❌
- [ ] Query refinement rate <5% (good classification) ✅/❌

**Long-term (Month 1):**
- [ ] Angle distribution validates 80/15/5 assumption ✅/❌
- [ ] Context window capacity increased 3.4x ✅/❌
- [ ] No performance degradation ✅/❌
- [ ] Feature adoption (users understand truncate parameter) ✅/❌

---

## 6. Troubleshooting

### 6.1 Common Issues

#### Issue 1: Truncation Not Applied

**Symptoms:**
- Query returns full chunks (500+ lines) when truncation expected
- Response metadata shows `truncated=False`
- No truncation metadata in response

**Cause:**
- `truncate` parameter explicitly set to `False`
- Query classified as "implementation" or "troubleshooting" (no truncation for these angles)
- Chunk smaller than truncation threshold

**Solution:**
```python
# Check query classification
result = classifier.classify("Your query here")
print(f"Detected angle: {result.primary}")

# If angle is "implementation" or "troubleshooting", truncation is skipped (by design)
# If you want truncation, use explicit override:
response = pos_search_project(
    action="search_code",
    query="Your query",
    truncate=100  # Explicit line count
)

# Or rephrase query to change classification:
# "How to implement X?" → "How does X work?" (conceptual, will truncate)
```

---

#### Issue 2: QueryClassifier Unavailable

**Symptoms:**
- Warning in logs: "QueryClassifier unavailable, defaulting to 100 lines"
- All queries truncated to 100 lines regardless of angle
- Response metadata shows `angle="conceptual"` (fallback)

**Cause:**
- QueryClassifier not initialized
- PrependGenerator not available
- Exception during classification

**Solution:**
```python
# Check if QueryClassifier is available
try:
    result = self.prepend_generator.classifier.classify("test")
    print("QueryClassifier available ✅")
except Exception as e:
    print(f"QueryClassifier unavailable: {e}")

# Verify PrependGenerator initialization
if not hasattr(self, 'prepend_generator'):
    print("ERROR: PrependGenerator not initialized")

# Check logs for initialization errors
tail -f /var/log/praxis-os/mcp-server.log | grep "QueryClassifier"
```

**Mitigation:**
- System gracefully degrades to 100-line default
- Search continues to work
- Fix QueryClassifier initialization if needed

---

#### Issue 3: Truncation Point Mid-Method

**Symptoms:**
- Truncated content cuts off mid-method
- Incomplete function definitions in results
- Syntax errors in truncated code

**Cause:**
- No natural boundary found within 20 lines of target
- Large method (>120 lines) with no blank lines
- Fallback to exact line count

**Solution:**
```python
# Check if natural boundary was found
# Look for warning in logs:
# "No natural boundary found within 20 lines, using target"

# If this happens frequently, consider:
# 1. Increase search range (change 20 to 30 in _find_truncation_point)
# 2. Add more boundary patterns (e.g., comments, decorators)
# 3. Use explicit line count that aligns with method boundaries

# Temporary workaround: Use explicit line count
response = pos_search_project(
    action="search_code",
    query="Your query",
    truncate=150  # Adjust to align with method boundary
)
```

---

#### Issue 4: Performance Degradation (>10ms)

**Symptoms:**
- Truncation overhead >10ms (P95)
- Slow search responses
- High CPU usage during truncation

**Cause:**
- Very large chunks (2000+ lines)
- Inefficient string operations
- Too many results (n_results >10)

**Solution:**
```python
# Measure truncation time
import time

start = time.perf_counter()
result = _truncate_code_chunks(chunks, max_lines=100)
end = time.perf_counter()
print(f"Truncation time: {(end - start) * 1000:.2f}ms")

# If >10ms:
# 1. Reduce n_results (fewer chunks to process)
response = pos_search_project(
    action="search_code",
    query="Your query",
    n_results=3  # Default, reduce if needed
)

# 2. Profile string operations
# Check if split/join are bottlenecks

# 3. Consider caching truncated results (if same chunks queried repeatedly)
```

---

#### Issue 5: Invalid truncate Parameter

**Symptoms:**
- Error: "Invalid truncate parameter"
- Response status: "error"
- Search fails to execute

**Cause:**
- Invalid parameter type (e.g., dict, list)
- Invalid string value (not "auto")
- Negative integer

**Solution:**
```python
# Valid parameter types:
truncate=True          # Auto-detect (default) ✅
truncate=False         # No truncation ✅
truncate=100           # Explicit line count ✅
truncate="auto"        # Explicit auto-detect ✅

# Invalid parameter types:
truncate="invalid"     # ❌ String must be "auto"
truncate=-50           # ❌ Must be positive
truncate={"lines": 100} # ❌ Dict not supported

# Check error message for guidance
response = pos_search_project(action="search_code", query="...", truncate="invalid")
print(response["error"]["message"])
# "truncate must be True, False, int, or 'auto'"
```

---

#### Issue 6: Metadata Missing in Response

**Symptoms:**
- No `truncated` field in results
- No `truncation_reason` in metadata
- No inline hint in content

**Cause:**
- Truncation not applied (chunk smaller than threshold)
- Search action not "search_code" (standards, AST, graph)
- Old version of code (pre-truncation)

**Solution:**
```python
# Check if truncation was applied
result = response["results"][0]
if "truncated" not in result:
    print("Truncation metadata not present")
    print(f"Chunk size: {len(result['content'].split('\n'))} lines")
    print(f"Threshold: {threshold} lines")
    # If chunk < threshold, no truncation applied (by design)

# Check search action
print(f"Action: {response['action']}")
# Truncation only applies to "search_code"

# Verify code version
grep "truncated" .praxis-os/ouroboros/tools/pos_search_project.py
# Should find metadata enrichment code
```

---

### 6.2 Debugging Techniques

#### Enable Verbose Logging

```python
import logging

# Set log level to DEBUG
logging.getLogger("praxis_os").setLevel(logging.DEBUG)

# Check truncation logic
logger.debug(f"Query: {query}")
logger.debug(f"Detected angle: {angle}")
logger.debug(f"Truncation threshold: {max_lines}")
logger.debug(f"Chunk size: {len(lines)} lines")
logger.debug(f"Truncation point: {truncation_point}")
```

#### Use Python Debugger (pdb)

```python
# Add breakpoint in truncation logic
def _determine_truncation(self, query, truncate_param):
    import pdb; pdb.set_trace()  # Breakpoint here
    
    # Step through code
    # (Pdb) n  # Next line
    # (Pdb) s  # Step into function
    # (Pdb) p angle  # Print variable
    # (Pdb) c  # Continue
```

#### Inspect Response Structure

```python
import json

response = pos_search_project(action="search_code", query="How does X work?")

# Pretty-print response
print(json.dumps(response, indent=2))

# Check specific fields
print(f"Status: {response['status']}")
print(f"Count: {response['count']}")
print(f"Truncated: {response['results'][0].get('truncated', 'N/A')}")
print(f"Full line count: {response['results'][0].get('full_line_count', 'N/A')}")
print(f"Truncation reason: {response['metadata'].get('truncation_reason', 'N/A')}")
```

#### Test Individual Methods

```python
# Test _determine_truncation in isolation
tool = POSSearchProject()
result = tool._determine_truncation("How does X work?", True)
print(f"Threshold: {result}")  # Should be 100 for conceptual

# Test _find_truncation_point
lines = ["line1", "line2", ..., "line100"]
truncation_point = tool._find_truncation_point(lines, max_lines=100)
print(f"Truncation point: {truncation_point}")

# Test _truncate_code_chunks
chunks = [{"content": "...", "file": "test.py"}]
truncated = tool._truncate_code_chunks(chunks, max_lines=100)
print(f"Truncated: {truncated[0]['truncated']}")
```

#### Check QueryClassifier Behavior

```python
# Test query classification
from praxis_os.middleware.query_classifier import QueryClassifier

classifier = QueryClassifier()
result = classifier.classify("How does authentication work?")
print(f"Primary angle: {result.primary}")  # Should be "conceptual"

result = classifier.classify("Where is the login function?")
print(f"Primary angle: {result.primary}")  # Should be "location"

result = classifier.classify("How to implement OAuth2?")
print(f"Primary angle: {result.primary}")  # Should be "implementation"
```

---

### 6.3 Performance Debugging

#### Measure Truncation Overhead

```python
import time
import numpy as np

# Measure multiple runs for statistical validity
overheads = []
for _ in range(100):
    start = time.perf_counter()
    _truncate_code_chunks(chunks, max_lines=100)
    end = time.perf_counter()
    overheads.append((end - start) * 1000)  # ms

print(f"Mean: {np.mean(overheads):.2f}ms")
print(f"P95: {np.percentile(overheads, 95):.2f}ms")
print(f"P99: {np.percentile(overheads, 99):.2f}ms")

# Target: P95 <10ms
```

#### Profile String Operations

```python
import cProfile
import pstats

# Profile truncation
profiler = cProfile.Profile()
profiler.enable()

_truncate_code_chunks(chunks, max_lines=100)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions by time
```

#### Check Memory Usage

```python
import tracemalloc

# Start tracking memory
tracemalloc.start()

# Execute truncation
result = _truncate_code_chunks(chunks, max_lines=100)

# Get memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024 / 1024:.2f} MB")
print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")

tracemalloc.stop()
```

---

### 6.4 Test Debugging

#### Run Specific Test with Verbose Output

```bash
# Run single test with full output
pytest tests/unit/test_truncation.py::test_determine_truncation_conceptual_query -vv -s

# Show print statements
pytest tests/ -vv -s

# Show full traceback on failure
pytest tests/ -vv --tb=long
```

#### Debug Test Failure

```python
# Add pdb to failing test
def test_determine_truncation_conceptual_query():
    import pdb; pdb.set_trace()
    
    tool = POSSearchProject()
    result = tool._determine_truncation("How does X work?", True)
    assert result == 100  # Breakpoint before assertion
```

#### Check Test Coverage

```bash
# Run with coverage and show missing lines
pytest tests/ --cov=.praxis-os/ouroboros/tools/pos_search_project \
       --cov-report=term-missing

# Generate HTML report for detailed view
pytest tests/ --cov --cov-report=html
open htmlcov/index.html
```

---

### 6.5 Integration Debugging

#### Test End-to-End Flow

```python
# Test complete search flow with truncation
response = pos_search_project(
    action="search_code",
    query="How does the workflow system work?",
    n_results=3
)

# Verify each step
print("Step 1: Search executed ✅" if response["status"] == "success" else "❌")
print("Step 2: Results returned ✅" if response["count"] > 0 else "❌")
print("Step 3: Truncation applied ✅" if response["results"][0]["truncated"] else "❌")
print("Step 4: Metadata present ✅" if "truncation_reason" in response["metadata"] else "❌")
```

#### Check Component Interactions

```python
# Verify QueryClassifier integration
print("QueryClassifier available:", hasattr(tool.prepend_generator, 'classifier'))

# Verify SemanticIndex integration
print("SemanticIndex available:", hasattr(tool, 'semantic_index'))

# Test graceful degradation
with patch.object(tool.prepend_generator.classifier, 'classify', side_effect=Exception("Fail")):
    result = tool._determine_truncation("test", True)
    print(f"Graceful degradation: {result == 100}")  # Should default to 100
```

---

### 6.6 Getting Help

**Before Asking for Help, Gather:**
1. **Error Message:** Full error text and stack trace
2. **Query:** Exact query that triggered issue
3. **Response:** Full response JSON (if available)
4. **Logs:** Relevant log entries (grep for errors)
5. **Environment:** Python version, OS, MCP server version
6. **Steps to Reproduce:** Minimal example that reproduces issue

**Example Help Request:**
```
Issue: Truncation not applied for conceptual query

Query: "How does authentication work?"
Expected: ~100 lines truncated
Actual: 500 lines (full chunk)

Response metadata:
{
  "truncated": false,
  "full_line_count": 500
}

Logs:
[2025-11-16 10:30:15] WARNING: QueryClassifier unavailable, defaulting to 100 lines

Environment:
- Python 3.11
- praxis-os v1.0.0
- macOS 14.6

Steps to reproduce:
1. Execute: pos_search_project(action="search_code", query="How does authentication work?")
2. Check response["results"][0]["truncated"]
3. Expected True, got False
```

**Resources:**
- Documentation: `.praxis-os/standards/universal/tools/pos-search-project-usage-guide.md`
- Design Document: `.praxis-os/workspace/design/2025-11-16-code-search-auto-truncation.md`
- Test Examples: `tests/unit/test_truncation.py`, `tests/integration/test_search_code.py`
- Code Patterns: This document (Section 3)

---

### 6.7 Known Limitations

**Limitation 1: Language-Specific Boundaries**
- Current implementation uses Python-specific boundaries (`def `, `class `)
- May not work optimally for other languages (JavaScript, Go, Rust)
- **Workaround:** Use explicit line count for non-Python code

**Limitation 2: Very Large Methods**
- Methods >500 lines may not have natural boundaries within 20-line search range
- Fallback to exact line count may cut mid-method
- **Workaround:** Increase search range or use explicit line count

**Limitation 3: Query Classification Accuracy**
- QueryClassifier may misclassify edge-case queries
- Misclassification leads to suboptimal truncation
- **Workaround:** Use explicit `truncate` parameter to override

**Limitation 4: No Pagination**
- Cannot fetch "next page" of truncated content
- Must use `truncate=False` to get full chunk
- **Future Enhancement:** Add `get_full_chunk` action

---

### 6.8 Troubleshooting Checklist

**When Truncation Doesn't Work:**
- [ ] Check query classification (is angle correct?) ✅/❌
- [ ] Check chunk size (is it smaller than threshold?) ✅/❌
- [ ] Check `truncate` parameter (is it explicitly False?) ✅/❌
- [ ] Check search action (is it "search_code"?) ✅/❌
- [ ] Check logs for errors or warnings ✅/❌

**When Performance is Slow:**
- [ ] Measure truncation overhead (is it >10ms?) ✅/❌
- [ ] Check chunk sizes (are they >2000 lines?) ✅/❌
- [ ] Check n_results (is it >10?) ✅/❌
- [ ] Profile string operations (are they bottleneck?) ✅/❌
- [ ] Check concurrent load (are there many requests?) ✅/❌

**When Tests Fail:**
- [ ] Run tests with verbose output (-vv) ✅/❌
- [ ] Check coverage (is it <90%?) ✅/❌
- [ ] Check mocks (are dependencies mocked correctly?) ✅/❌
- [ ] Check assertions (are they specific enough?) ✅/❌
- [ ] Check test data (is it representative?) ✅/❌

---


