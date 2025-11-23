# Implementation Approach

**Project:** Project Orientation System  
**Date:** 2025-11-19

---

## 1. Implementation Philosophy

**Core Principles:**
1. **Error-Resistant Design** - Graceful degradation over strict validation
2. **Test-Driven Development** - Write tests before implementation for all error paths
3. **Incremental Delivery** - Implement phases sequentially with validation gates
4. **Backward Compatibility** - Never break existing projects without orientation metadata
5. **Code Review Required** - All changes require maintainer approval

**Design Rationale:**
- praxis-os ships to consumers → can't enforce pre-commit validation
- AI agents use this system → must handle malformed input gracefully
- Orientation is optional → missing metadata should not cause errors
- Performance matters → orientation must complete < 60s for good UX

---

## 2. Implementation Order

**Phase Sequence:** (from tasks.md)
1. **Phase 1:** Inline Metadata Parser (3-4 hours) - Foundation
2. **Phase 2:** mcp.yaml Configuration Extension (2-3 hours) - Parallel to Phase 1
3. **Phase 3:** Orientation Discovery & Execution (4-5 hours) - Depends on 1+2
4. **Phase 4:** Base Orientation Integration (2-3 hours) - Depends on 3
5. **Phase 5:** Testing & Documentation (4-6 hours) - Depends on all

**Critical Path:** Phase 1 → Phase 3 → Phase 4 → Phase 5 (14-18 hours)

**Parallel Opportunity:** Phase 1 and Phase 2 can run simultaneously (saves 2-3 hours)

---

## 3. Code Patterns

### Pattern 1: Error-Resistant Regex Parsing

**Purpose:** Parse inline metadata from markdown without breaking on malformed input

**Used in:** OrientationMetadataParser._extract_inline_metadata()

**Good Example (Error-Resistant):**
```python
def _extract_inline_metadata(self, content: str, file_path: Path) -> Dict[str, Any]:
    """Extract metadata from **Metadata**: line with error resistance."""
    
    # Look for **Metadata**: line (case-sensitive, fuzzy-resistant)
    match = re.search(r'\*\*Metadata\*\*:\s*(.+)', content)
    if not match:
        # Graceful fallback: missing metadata → use path-based defaults
        return self._extract_defaults_from_path(file_path)
    
    metadata_str = match.group(1)
    metadata = {}
    
    # Parse key=value pairs (comma-separated, error-resistant)
    for item in metadata_str.split(','):
        item = item.strip()
        if '=' not in item:
            # Skip malformed entries (missing =), don't fail
            continue
        
        # Use split('=', 1) to handle values containing =
        key, value = item.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # Type coercion with fallback (never raise exception)
        try:
            if value.lower() in ('true', 'false'):
                metadata[key] = value.lower() == 'true'
            elif value.isdigit():
                metadata[key] = int(value)
            else:
                metadata[key] = value  # String fallback
        except Exception as e:
            # Log warning but continue processing
            logger.warning(
                "Failed to parse metadata value '%s' in %s: %s",
                item, file_path, e
            )
            continue  # Skip bad values, don't fail entire parse
    
    return metadata
```

**Why this works:**
- ✅ Single regex pattern (compiled at class level for performance)
- ✅ Graceful fallback on missing **Metadata**: line
- ✅ Error-resistant loop (skip bad items, continue parsing)
- ✅ Type coercion with fallback (bool → int → string)
- ✅ Never raises exceptions (logs warnings instead)
- ✅ `split('=', 1)` handles values containing = character

**Anti-Pattern (Brittle):**
```python
# ❌ DON'T DO THIS - too strict, breaks on malformed input
def _extract_inline_metadata_bad(self, content: str) -> Dict[str, Any]:
    match = re.search(r'\*\*Metadata\*\*:\s*(.+)', content)
    metadata_str = match.group(1)  # ❌ Raises AttributeError if no match
    
    for item in metadata_str.split(','):
        key, value = item.split('=')  # ❌ Raises ValueError if no '=' or multiple '='
        metadata[key] = int(value)    # ❌ Raises ValueError if not an int
    
    return metadata  # ❌ Entire parse fails on first error
```

**Graceful Degradation Scenarios:**
```python
# Scenario 1: Missing line
# Input: (no **Metadata**: line)
# Output: Returns path-based defaults (e.g., {"domain": "ai-assistant"})

# Scenario 2: Malformed (missing comma)
# Input: **Metadata**: orientation=true priority=1
# Output: Parses "orientation=true", skips "priority=1", continues

# Scenario 3: Typo in marker
# Input: **Metdata**: orientation=true
# Output: No match, returns path-based defaults

# Scenario 4: Bad value (not a bool)
# Input: **Metadata**: orientation=notabool, priority=1
# Output: Skips "orientation", parses "priority=1", logs warning
```

---

### Pattern 2: Pydantic Validation with Actionable Errors

**Purpose:** Validate mcp.yaml configuration with clear error messages

**Used in:** OrientationQuery, ProjectOrientation, ProjectConfig models

**Good Example (Actionable Errors):**
```python
from pydantic import BaseModel, Field, validator, ValidationError

class OrientationQuery(BaseModel):
    """Single orientation query with metadata."""
    
    query: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Search query string for pos_search_project"
    )
    priority: int = Field(
        default=2,
        ge=1,
        le=3,
        description="Priority level: 1=critical, 2=high, 3=medium"
    )
    description: Optional[str] = Field(
        None,
        max_length=200,
        description="Human-readable description of query purpose"
    )
    category: Optional[str] = Field(
        None,
        max_length=50,
        description="Category for grouping (e.g., 'architecture', 'patterns')"
    )
    depends_on: Optional[List[str]] = Field(
        None,
        description="List of query strings this query depends on"
    )
    
    @validator('priority')
    def validate_priority_range(cls, v):
        """Ensure priority is 1, 2, or 3."""
        if v not in [1, 2, 3]:
            raise ValueError(
                f"Priority must be 1 (critical), 2 (high), or 3 (medium), got {v}"
            )
        return v
    
    @validator('depends_on')
    def validate_no_self_dependency(cls, v, values):
        """Prevent query from depending on itself."""
        if v and 'query' in values and values['query'] in v:
            raise ValueError(
                f"Query cannot depend on itself: {values['query']}"
            )
        return v

class ProjectOrientation(BaseModel):
    """Project-level orientation configuration."""
    
    enabled: bool = Field(
        default=True,
        description="Enable project-specific orientation queries"
    )
    queries: List[OrientationQuery] = Field(
        default_factory=list,
        description="List of orientation queries to execute"
    )
    
    @validator('queries')
    def validate_no_duplicate_queries(cls, v):
        """Prevent duplicate query strings."""
        query_strings = [q.query for q in v]
        duplicates = [q for q in query_strings if query_strings.count(q) > 1]
        if duplicates:
            raise ValueError(
                f"Duplicate queries found: {set(duplicates)}. "
                f"Each query string must be unique."
            )
        return v
```

**Why this works:**
- ✅ Field validators provide min/max constraints
- ✅ Custom validators check business rules (priority range, no self-deps)
- ✅ Error messages are actionable ("Priority must be 1, 2, or 3")
- ✅ Default values support optional fields
- ✅ ValidationError includes field path for debugging

**Anti-Pattern (Vague Errors):**
```python
# ❌ DON'T DO THIS - vague validation, unclear errors
class OrientationQueryBad(BaseModel):
    query: str  # ❌ No length constraints
    priority: int  # ❌ No range validation
    
    @validator('priority')
    def check_priority(cls, v):
        if v < 1 or v > 3:
            raise ValueError("Invalid priority")  # ❌ Vague message
        return v
```

---

### Pattern 3: Dependency Resolution with Cycle Detection

**Purpose:** Resolve query dependencies and detect circular dependencies

**Used in:** OrientationDiscoveryHandler._resolve_dependencies()

**Good Example (Topological Sort):**
```python
def _resolve_dependencies(
    self, queries: List[OrientationQuery]
) -> List[OrientationQuery]:
    """
    Resolve dependencies and return topologically sorted query list.
    
    Raises:
        ValueError: If circular dependencies detected
    """
    # Build dependency graph
    graph: Dict[str, List[str]] = {}
    query_map: Dict[str, OrientationQuery] = {}
    
    for query in queries:
        graph[query.query] = query.depends_on or []
        query_map[query.query] = query
    
    # Detect cycles using DFS
    visited = set()
    rec_stack = set()
    
    def has_cycle(node: str) -> bool:
        """DFS to detect cycles."""
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                # Circular dependency found
                return True
        
        rec_stack.remove(node)
        return False
    
    # Check all nodes for cycles
    for query_str in graph:
        if query_str not in visited:
            if has_cycle(query_str):
                # Build cycle path for error message
                cycle_path = " → ".join(rec_stack)
                raise ValueError(
                    f"Circular dependency detected: {cycle_path}. "
                    f"Queries cannot depend on each other in a cycle."
                )
    
    # Topological sort using Kahn's algorithm
    in_degree = {q: 0 for q in graph}
    for deps in graph.values():
        for dep in deps:
            if dep in in_degree:
                in_degree[dep] += 1
    
    queue = deque([q for q, deg in in_degree.items() if deg == 0])
    sorted_queries = []
    
    while queue:
        query_str = queue.popleft()
        sorted_queries.append(query_map[query_str])
        
        for dependent in graph[query_str]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)
    
    return sorted_queries
```

**Why this works:**
- ✅ DFS detects cycles before sorting (fail fast)
- ✅ Kahn's algorithm provides topological sort
- ✅ Error message includes cycle path for debugging
- ✅ Handles disconnected components (independent queries)

**Anti-Pattern (No Cycle Detection):**
```python
# ❌ DON'T DO THIS - infinite loop on circular dependencies
def _resolve_dependencies_bad(self, queries: List[OrientationQuery]):
    # ❌ No cycle detection - will loop infinitely on A→B→A
    while has_unresolved_dependencies(queries):
        # Try to resolve dependencies...
        pass  # ❌ Infinite loop if circular
```

---

### Pattern 4: Timeout Protection with Partial Results

**Purpose:** Prevent runaway execution, return partial results on timeout

**Used in:** ProjectOrientationExecutor.execute_orientation()

**Good Example (Timeout with Partial Results):**
```python
def execute_orientation(
    self, queries: List[OrientationQuery], timeout_ms: int = 60000
) -> OrientationSessionSummary:
    """
    Execute orientation queries with timeout protection.
    
    Args:
        queries: Sorted list of orientation queries
        timeout_ms: Total timeout in milliseconds (default: 60s)
    
    Returns:
        OrientationSessionSummary with results (partial if timeout)
    """
    start_time = time.time()
    results = []
    timeout_occurred = False
    
    for i, query in enumerate(queries):
        # Check total elapsed time
        elapsed_ms = (time.time() - start_time) * 1000
        if elapsed_ms >= timeout_ms:
            timeout_occurred = True
            logger.warning(
                "Orientation timeout after %.2fms. "
                "Executed %d/%d queries. Returning partial results.",
                elapsed_ms, i, len(queries)
            )
            break
        
        # Calculate remaining time for this query
        remaining_ms = timeout_ms - elapsed_ms
        query_timeout_ms = min(10000, remaining_ms)  # Max 10s per query
        
        # Execute query with per-query timeout
        try:
            query_start = time.time()
            result = self._search_tool.search_standards(
                query=query.query,
                timeout_ms=query_timeout_ms
            )
            query_elapsed_ms = (time.time() - query_start) * 1000
            
            results.append({
                "query": query.query,
                "success": True,
                "execution_time_ms": query_elapsed_ms,
                "results": result
            })
        except TimeoutError:
            logger.warning("Query timeout: %s", query.query)
            results.append({
                "query": query.query,
                "success": False,
                "execution_time_ms": query_timeout_ms,
                "error": "Query timeout"
            })
    
    # Return summary with partial flag
    total_elapsed_ms = (time.time() - start_time) * 1000
    return OrientationSessionSummary(
        queries_executed=len(results),
        queries_total=len(queries),
        timeout_occurred=timeout_occurred,
        total_time_ms=total_elapsed_ms,
        results=results
    )
```

**Why this works:**
- ✅ Total timeout check before each query
- ✅ Per-query timeout prevents single query blocking
- ✅ Returns partial results on timeout (doesn't lose progress)
- ✅ Logs warning with timing information for debugging
- ✅ Summary includes timeout flag for caller awareness

**Anti-Pattern (Timeout Loses Results):**
```python
# ❌ DON'T DO THIS - timeout loses all results
def execute_orientation_bad(self, queries):
    with timeout(60):  # ❌ Raises exception on timeout
        for query in queries:
            result = execute_query(query)  # ❌ All results lost if timeout
            results.append(result)
    return results  # ❌ Never reached if timeout
```

---

### Pattern 5: Mistletoe AST-Based Parsing

**Purpose:** Structure-aware markdown parsing that respects code blocks and headers

**Used in:** Future enhancement for better chunking quality (Phase 1+ of mistletoe doc)

**Good Example (AST-Aware):**
```python
from mistletoe import Document
from mistletoe.block_token import Heading, CodeFence, List as MDList

def _chunk_file_with_mistletoe(self, file_path: Path) -> List[Dict]:
    """Chunk markdown file using AST-based parsing."""
    content = file_path.read_text(encoding="utf-8")
    
    # Parse markdown into AST
    doc = Document(content)
    
    chunks = []
    current_chunk = []
    current_section = "Introduction"
    
    for token in doc.children:
        # Detect H2 headers using AST (not string matching)
        if isinstance(token, Heading) and token.level == 2:
            # Save previous chunk
            if current_chunk:
                chunks.append(self._create_chunk(
                    tokens=current_chunk,
                    section=current_section,
                    metadata=metadata
                ))
            
            # Start new chunk
            current_section = self._extract_heading_text(token)
            current_chunk = [token]
        
        elif isinstance(token, CodeFence):
            # Keep code blocks atomic (don't split)
            current_chunk.append(token)
        
        elif isinstance(token, MDList):
            # Keep lists together (don't break mid-list)
            current_chunk.append(token)
        
        else:
            current_chunk.append(token)
    
    return chunks
```

**Why this works:**
- ✅ AST-based header detection (no false positives from `##` in code)
- ✅ Code fence awareness (keeps blocks intact)
- ✅ Respects markdown structure (lists, tables)
- ✅ Extensible (easy to add more token types)

**Anti-Pattern (String Matching):**
```python
# ❌ DON'T DO THIS - naive string matching breaks on code blocks
def _chunk_file_bad(self, file_path: Path):
    for line in lines:
        if line.startswith("##"):  # ❌ Matches ## in code blocks!
            # New chunk
            pass
```

---

## 4. Testing Strategy

### 4.1 Requirements Summary

**Functional Requirements:** 9
- FR-001 through FR-009
- All requirements have acceptance criteria
- 100% mapped to tests

**Non-Functional Requirements:** 14
- Performance (NFR-P1, NFR-P2)
- Reliability (NFR-R1, NFR-R2)
- Security (NFR-S1, NFR-S2)
- Maintainability (NFR-M1, NFR-M2, NFR-M3)
- Usability (NFR-U1, NFR-U2, NFR-U3)
- Compatibility (NFR-C1, NFR-C2)
- All requirements have measurement criteria
- 100% mapped to tests

**Total Requirements:** 23

**Source:** `testing/requirements-list.md`

---

### 4.2 Traceability Matrix

**Functional Requirements:**
- FRs mapped to tests: 9/9 (100%)
- Test functions for FRs: 36+
- Average tests per FR: 4

**Non-Functional Requirements:**
- NFRs mapped to tests: 14/14 (100%)
- Test functions for NFRs: 40+
- Average tests per NFR: 2.86

**Total Test Functions:** ~93
- Unit tests: ~60 (65%)
- Integration tests: ~20 (22%)
- Performance tests: ~5 (5%)
- Security tests: ~8 (8%)

**Complete Matrix:** `testing/traceability-matrix.md`

---

### 4.3 Test Cases

**Functional Test Cases:** 40+
- FR-001 (Inline Metadata Discovery): 5 test cases
- FR-002 (mcp.yaml Extension): 5 test cases
- FR-003 (Automatic Execution): 5 test cases
- FR-004 (Error-Resistant Parsing): 6 test cases
- FR-005 (Query Order and Dependencies): 5 test cases
- FR-006 (Standards Pattern Compatibility): 4 test cases
- FR-007 (Base Orientation Integration): 5 test cases
- FR-008 (Metadata Schema): 5 test cases
- FR-009 (No Tooling Requirements): 5 test cases

**NFR Verification Tests:** 25
- Performance: 5 tests (timing, overhead, benchmarks)
- Reliability: 4 tests (graceful degradation, error resilience)
- Security: 5 tests (no code execution, input validation)
- Maintainability: 5 tests (code reuse, coverage, quality)
- Usability: 3 tests (tooling, error messages, documentation)
- Compatibility: 3 tests (backward/forward compatibility)

**Integration Scenarios:** 3
- Full orientation workflow (base + project)
- Multiple configuration sources (inline + mcp.yaml)
- Error resilience end-to-end

**Details:** 
- `testing/functional-tests.md` - Comprehensive functional test cases
- `testing/nonfunctional-tests.md` - NFR verification tests

---

### 4.4 Testing Approach

**Philosophy:**
- Test-Driven Development where applicable
- Fast, isolated unit tests (< 100ms each)
- Integration tests for component interactions
- Performance benchmarking for NFR verification
- Comprehensive error path testing

**Coverage Target:** ≥ 90% line coverage

**Test Pyramid:**
- Unit Tests: 65% (~60 tests)
- Integration Tests: 22% (~20 tests)
- Performance Tests: 5% (~5 tests)
- Security Tests: 8% (~8 tests)

**Test Organization:**
```
tests/
├── ouroboros/
│   ├── subsystems/
│   │   ├── rag/standards/test_orientation.py        # 25 unit tests
│   │   └── config/test_orientation_models.py        # 15 unit tests
├── integration/test_orientation_workflow.py         # 20 integration tests
├── performance/test_orientation_performance.py      # 5 performance tests
└── security/test_orientation_security.py            # 8 security tests
```

**Mocking Strategy:**
- Mock external dependencies (pos_search_project, standards index)
- Don't mock units under test
- Use pytest fixtures for reusable test data

**Execution Commands:**
```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/ouroboros/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=ouroboros.subsystems.rag.standards.orientation \
       --cov=ouroboros.subsystems.config.models \
       --cov-report=term-missing \
       --cov-fail-under=90

# Performance tests
pytest tests/performance/ --benchmark-only

# Linting
flake8 ouroboros/subsystems/rag/standards/orientation.py
mypy ouroboros/subsystems/rag/standards/orientation.py
bandit -r ouroboros/subsystems/rag/standards/orientation.py
```

**Complete Strategy:** `testing/test-strategy.md`

---

### 4.5 Testing Checklist

**Before Implementation:**
- [ ] Review traceability matrix (`testing/traceability-matrix.md`) ✅/❌
- [ ] Review all test cases (`testing/functional-tests.md`, `testing/nonfunctional-tests.md`) ✅/❌
- [ ] Review testing strategy (`testing/test-strategy.md`) ✅/❌
- [ ] Set up test environment (pytest, coverage, mocking libraries) ✅/❌

**During Implementation (Per Phase):**
- [ ] Write tests first or alongside code (TDD approach) ✅/❌
- [ ] Run tests frequently during development ✅/❌
- [ ] Verify tests pass before moving to next task ✅/❌
- [ ] Check coverage incrementally (≥ 90% per component) ✅/❌
- [ ] Fix linting errors immediately (flake8, mypy) ✅/❌

**Before Phase Completion:**
- [ ] All unit tests implemented and passing ✅/❌
- [ ] All integration tests implemented and passing ✅/❌
- [ ] All performance tests implemented and passing ✅/❌
- [ ] All security tests implemented and passing ✅/❌
- [ ] Coverage target met (≥ 90%) ✅/❌
- [ ] NFR metrics achieved (timing, reliability, security) ✅/❌
- [ ] All linting passes (flake8, mypy, bandit, black) ✅/❌
- [ ] Code quality verified (docstrings, type hints) ✅/❌

**Before Merge:**
- [ ] Full test suite passes (unit + integration + performance + security) ✅/❌
- [ ] Coverage report generated and reviewed ✅/❌
- [ ] CI/CD pipeline passes ✅/❌
- [ ] Code review approved ✅/❌

---

### 4.6 Completeness Verification

✅ **All 23 requirements (9 FRs + 14 NFRs) have been:**
1. **Extracted** into `testing/requirements-list.md` with acceptance/measurement criteria
2. **Mapped** to specific tests in `testing/traceability-matrix.md` (100% coverage)
3. **Given test cases** in `testing/functional-tests.md` and `testing/nonfunctional-tests.md` (40+ functional, 25 NFR verification)
4. **Covered by strategy** in `testing/test-strategy.md` (unit, integration, performance, security approaches)

**Verification:**
- Requirements in srd.md: 23 (9 FRs + 14 NFRs)
- Requirements in requirements-list.md: 23 ✅
- Requirements in traceability-matrix.md: 23 ✅
- Test cases in functional-tests.md: 40+ (covering 9 FRs) ✅
- Test cases in nonfunctional-tests.md: 25 (covering 14 NFRs) ✅
- Test functions planned: ~93 ✅

**No requirements are untested.**

**Testing documentation is complete and consistent across all artifacts.**

---

## 5. Deployment Guidance

### 5.1 Deployment Overview

This feature adds project orientation capabilities to the existing prAxIs OS system. Deployment involves adding new modules, extending configuration schemas, and updating base orientation documentation.

**Deployment Type:** Feature addition to existing system  
**Impact:** Additive (no breaking changes to existing functionality)  
**Rollback Strategy:** Remove new modules, revert configuration extensions

---

### 5.2 Pre-Deployment Checklist

**Code Quality:**
- [ ] All tests passing: `pytest tests/` (100% pass rate required)
- [ ] Code coverage ≥ 90%: `pytest --cov --cov-fail-under=90`
- [ ] Linting passes: `flake8`, `mypy`, `bandit` (zero errors)
- [ ] Code formatted: `black --check ouroboros/`
- [ ] Code review approved by maintainer

**Testing:**
- [ ] Unit tests passing (~60 tests)
- [ ] Integration tests passing (~20 tests)
- [ ] Performance tests passing (orientation < 60s)
- [ ] Security tests passing (no code execution vulnerabilities)
- [ ] Backward compatibility verified (projects without orientation work unchanged)

**Documentation:**
- [ ] All docstrings complete (public methods)
- [ ] Type hints complete (all parameters and returns)
- [ ] Usage documentation created (`project-orientation-guide.md`)
- [ ] Example configurations valid

---

### 5.3 Deployment Steps

#### Step 1: Install Dependencies
```bash
# Verify mistletoe already installed (from requirements.txt)
pip list | grep mistletoe

# If not installed (shouldn't be needed, but for reference)
pip install mistletoe
```

#### Step 2: Deploy New Modules
```bash
# New files to add:
ouroboros/subsystems/rag/standards/orientation.py          # Core orientation logic
ouroboros/subsystems/config/models.py                      # Pydantic models (extend existing)

# Modified files:
standards/universal/ai-assistant/PRAXIS-OS-ORIENTATION.md  # Query 10 update
config/mcp.yaml                                            # Optional: project.orientation section
```

#### Step 3: Verify Module Imports
```bash
# Test imports work
python3 -c "from ouroboros.subsystems.rag.standards.orientation import OrientationMetadataParser; print('✅ Import successful')"
python3 -c "from ouroboros.subsystems.config.models import OrientationQuery, ProjectOrientation, ProjectConfig; print('✅ Models imported')"
```

#### Step 4: Run Unit Tests
```bash
# Run orientation-specific tests
pytest tests/ouroboros/subsystems/rag/standards/test_orientation.py -v
pytest tests/ouroboros/subsystems/config/test_orientation_models.py -v

# Expected: All tests pass
```

#### Step 5: Run Integration Tests
```bash
# Test full workflow
pytest tests/integration/test_orientation_workflow.py -v

# Expected: Base + project orientation workflow succeeds
```

#### Step 6: Verify Backward Compatibility
```bash
# Test project without orientation metadata
pytest tests/integration/test_orientation_workflow.py::test_backward_compatible_no_orientation_metadata -v

# Expected: System works without orientation (graceful fallback)
```

#### Step 7: Run Performance Benchmarks
```bash
# Verify NFR-P1 (orientation < 60s)
pytest tests/performance/test_orientation_performance.py::test_orientation_execution_under_60_seconds -v

# Expected: Execution time < 60,000ms
```

#### Step 8: Update Base Orientation Documentation
```bash
# Verify Query 10 updated in PRAXIS-OS-ORIENTATION.md
grep -A 5 "project orientation" standards/universal/ai-assistant/PRAXIS-OS-ORIENTATION.md

# Expected: Query 10 mentions project orientation discovery
```

#### Step 9: Rebuild Standards Index
```bash
# Rebuild index with new metadata parsing
python -m ouroboros.subsystems.rag.index_manager rebuild --index=standards

# Expected: Index rebuilds successfully with metadata support
```

#### Step 10: Health Check
```bash
# Verify system health
python -m ouroboros.tools.pos_search_project health_check

# Expected: All subsystems healthy, indexes built
```

---

### 5.4 Configuration

#### Optional: Add Project Orientation to mcp.yaml

**For projects that want centralized orientation configuration:**

```yaml
# Add to mcp.yaml (optional)
project:
  orientation:
    enabled: true
    queries:
      - query: "project architecture overview"
        priority: 1
        description: "High-level architectural context"
        category: "architecture"
      
      - query: "dogfooding model implementation"
        priority: 2
        description: "How praxis-os dogfoods its own patterns"
        category: "patterns"
      
      - query: "query-first decision protocol usage"
        priority: 2
        description: "Examples of query-first pattern in practice"
        category: "patterns"
```

**Validation:**
```bash
# Verify mcp.yaml parses correctly
python -c "from ouroboros.subsystems.config import UnifiedConfig; config = UnifiedConfig.from_yaml('.praxis-os/config/mcp.yaml'); print('✅ Config valid')"
```

#### Alternative: Add Inline Metadata to Standards

**For distributed orientation metadata:**

```markdown
# Example: Add to standards/development/praxis-os-architecture.md

**Metadata**: orientation=true, priority=1, category=architecture, domain=praxis-os

## Architecture Overview
...
```

**No configuration changes needed** - metadata discovered automatically during indexing.

---

### 5.5 Verification & Smoke Testing

#### Verification Tests
```bash
# 1. Verify orientation discovery
python -c "
from ouroboros.subsystems.rag.standards.orientation import OrientationDiscoveryHandler
# Test discovery logic
print('✅ Discovery works')
"

# 2. Verify query execution
python -c "
from ouroboros.subsystems.rag.standards.orientation import ProjectOrientationExecutor
# Test execution logic
print('✅ Execution works')
"

# 3. Full integration test
pytest tests/integration/test_orientation_workflow.py::test_full_orientation_workflow_base_plus_project -v

# Expected: Complete workflow succeeds
```

#### Smoke Tests (Manual)
1. Start new AI conversation in project with orientation metadata
2. Execute base orientation (queries 1-10)
3. Verify Query 10 triggers project orientation discovery
4. Verify project queries execute successfully
5. Confirm AI has both base and project context

---

### 5.6 Rollback Strategy

#### If Deployment Fails

**Immediate Rollback (< 5 minutes):**
1. **Identify failure:** Check logs for errors
2. **Stop if critical:** If orientation breaks base system, rollback immediately
3. **Remove new modules:**
   ```bash
   rm ouroboros/subsystems/rag/standards/orientation.py
   git checkout ouroboros/subsystems/config/models.py  # Revert extensions
   git checkout standards/universal/ai-assistant/PRAXIS-OS-ORIENTATION.md  # Revert Query 10
   ```
4. **Rebuild index:**
   ```bash
   python -m ouroboros.subsystems.rag.index_manager rebuild --index=standards
   ```
5. **Verify health:**
   ```bash
   pytest tests/  # Run full test suite
   ```

**Rollback Checklist:**
- [ ] Previous version code available in git
- [ ] No database migrations (N/A for this feature)
- [ ] Standards index can rebuild
- [ ] Base orientation still works after rollback
- [ ] All tests pass after rollback

**Post-Rollback:**
- [ ] Investigate root cause (logs, error messages)
- [ ] Fix issues in development environment
- [ ] Re-test thoroughly
- [ ] Schedule new deployment attempt

---

### 5.7 Monitoring & Validation

#### Post-Deployment Monitoring

**Metrics to Watch:**
- **Orientation execution time:** Monitor p50, p95, p99 (target: p95 < 60s)
- **Parsing errors:** Count warnings for malformed metadata (should be low)
- **Discovery success rate:** % of projects with orientation discovered
- **Index build time:** Monitor for degradation (target: < 5% slower)

**Logs to Check:**
```bash
# Check for orientation-related warnings/errors
grep "orientation" logs/praxis-os.log | grep -i "warn\|error"

# Check parsing warnings
grep "Failed to parse metadata" logs/praxis-os.log

# Verify discovery working
grep "project orientation discovery" logs/praxis-os.log
```

**Health Indicators:**
- ✅ All tests passing
- ✅ No exceptions in orientation code
- ✅ Orientation execution time < 60s (p95)
- ✅ Index build time degradation < 5%
- ✅ Warning rate < 5% of files

---

### 5.8 Deployment Checklist

**Pre-Deployment:**
- [ ] All tests passing (unit, integration, performance, security) ✅/❌
- [ ] Code coverage ≥ 90% ✅/❌
- [ ] Linting passes (flake8, mypy, bandit, black) ✅/❌
- [ ] Code review approved ✅/❌
- [ ] Documentation complete ✅/❌
- [ ] Example configurations valid ✅/❌
- [ ] Backward compatibility verified ✅/❌

**Deployment:**
- [ ] Dependencies verified (mistletoe) ✅/❌
- [ ] New modules deployed ✅/❌
- [ ] Module imports verified ✅/❌
- [ ] Tests run post-deployment ✅/❌
- [ ] Standards index rebuilt ✅/❌
- [ ] Health checks passing ✅/❌

**Post-Deployment:**
- [ ] Smoke tests completed ✅/❌
- [ ] Metrics normal (execution time, parsing errors) ✅/❌
- [ ] Logs clean (no unexpected errors) ✅/❌
- [ ] Base orientation still works ✅/❌
- [ ] Project orientation working (if configured) ✅/❌
- [ ] Performance targets met (< 60s, < 5% degradation) ✅/❌

**Rollback Preparation:**
- [ ] Previous version code tagged in git ✅/❌
- [ ] Rollback procedure documented ✅/❌
- [ ] Rollback tested on staging ✅/❌

---

## 6. Troubleshooting Guide

### 6.1 Common Issues and Solutions

#### Issue 1: Orientation Metadata Not Discovered

**Symptoms:**
- Project orientation queries not executing
- Query 10 finds no orientation metadata
- Discovery returns empty list

**Possible Causes:**
1. Metadata format incorrect (`**Metadata**:` typo)
2. Metadata line not in indexed files
3. Standards index not rebuilt after adding metadata
4. `orientation=true` field missing

**Solutions:**
```bash
# 1. Verify metadata format
grep -r "Metadata" standards/ | head -5
# Correct format: **Metadata**: orientation=true, priority=1

# 2. Check if file is indexed
python -c "
from ouroboros.subsystems.rag.index_manager import IndexManager
mgr = IndexManager()
results = mgr.search_standards(query='your-file-name')
print(f'File indexed: {len(results.results) > 0}')
"

# 3. Rebuild standards index
python -m ouroboros.subsystems.rag.index_manager rebuild --index=standards

# 4. Verify orientation=true present
grep "orientation=true" standards/**/*.md
```

**Verification:**
```python
from ouroboros.subsystems.rag.standards.orientation import OrientationDiscoveryHandler
handler = OrientationDiscoveryHandler(standards_index, config)
queries = handler.discover_orientation_queries()
print(f"Found {len(queries)} orientation queries")  # Should be > 0
```

---

#### Issue 2: Metadata Parsing Returns Empty Dict

**Symptoms:**
- `extract_inline_metadata()` returns `{}`
- Expected fields missing from metadata

**Possible Causes:**
1. Typo in `**Metadata**:` marker (e.g., `**Metdata**:`, `**metadata**:`)
2. Missing colon after `**Metadata**`
3. Malformed key=value pairs

**Solutions:**
```bash
# 1. Check for typos in marker
grep -r "\*\*Met.*data\*\*" standards/ | grep -v "Metadata:"
# Should return empty (no typos)

# 2. Verify exact format
cat standards/your-file.md | grep "Metadata"
# Must be: **Metadata**: key=value, key2=value2

# 3. Test parsing directly
python -c "
from ouroboros.subsystems.rag.standards.orientation import OrientationMetadataParser
from pathlib import Path

parser = OrientationMetadataParser()
content = Path('standards/your-file.md').read_text()
metadata = parser.extract_inline_metadata(content, Path('test.md'))
print(f'Parsed metadata: {metadata}')
"
```

**Fix Example:**
```markdown
# Wrong (typo in marker)
**Metdata**: orientation=true

# Wrong (missing colon)
**Metadata** orientation=true

# Wrong (case sensitive)
**metadata**: orientation=true

# Correct
**Metadata**: orientation=true, priority=1
```

---

#### Issue 3: Circular Dependency Error

**Symptoms:**
- ValueError: "Circular dependency detected"
- Orientation execution fails
- Error mentions query names in cycle

**Cause:**
Query A depends on Query B, which depends on Query A (or longer cycle)

**Solution:**
```bash
# 1. Identify the cycle from error message
# Error: "Circular dependency detected: A → B → C → A"

# 2. Fix dependency chain
# Either:
#   a) Remove depends_on field
#   b) Change depends_on to break cycle

# Example fix in mcp.yaml:
# Before (circular):
# - query: "A"
#   depends_on: ["B"]
# - query: "B"
#   depends_on: ["A"]

# After (fixed):
# - query: "A"
#   depends_on: ["B"]
# - query: "B"
#   depends_on: []  # Removed dependency
```

**Verification:**
```python
from ouroboros.subsystems.rag.standards.orientation import OrientationDiscoveryHandler
handler = OrientationDiscoveryHandler(standards_index, config)
queries = handler.discover_orientation_queries()
# Should not raise ValueError if cycle fixed
```

---

#### Issue 4: Orientation Timeout (> 60s)

**Symptoms:**
- Orientation execution takes > 60 seconds
- `timeout_occurred=True` in results
- Partial results returned

**Possible Causes:**
1. Too many queries (> 15-20)
2. Individual queries too slow (complex searches)
3. Standards index not optimized

**Solutions:**
```bash
# 1. Check query count
python -c "
from ouroboros.subsystems.config import UnifiedConfig
config = UnifiedConfig.from_yaml('.praxis-os/config/mcp.yaml')
if config.project and config.project.orientation:
    query_count = len(config.project.orientation.queries)
    print(f'Query count: {query_count}')
    if query_count > 15:
        print('⚠️  Too many queries (>15). Consider reducing.')
"

# 2. Profile slow queries
python -c "
import time
from ouroboros.tools.pos_search_project import pos_search_project

queries = ['architecture', 'patterns', 'dogfooding']
for q in queries:
    start = time.time()
    pos_search_project(action='search_standards', query=q)
    elapsed = time.time() - start
    print(f'{q}: {elapsed:.2f}s')
"

# 3. Optimize standards index
python -m ouroboros.subsystems.rag.index_manager rebuild --index=standards --optimize
```

**Mitigation:**
- Reduce number of queries to 5-10 most critical
- Use more specific queries (faster search)
- Increase priority for critical queries (execute first before timeout)

---

#### Issue 5: Pydantic ValidationError

**Symptoms:**
- ValidationError when loading mcp.yaml
- Error message about invalid field

**Possible Causes:**
1. Invalid priority value (must be 1, 2, or 3)
2. Missing required field (query)
3. Invalid type for field

**Solutions:**
```bash
# 1. Validate mcp.yaml manually
python -c "
from ouroboros.subsystems.config import UnifiedConfig
try:
    config = UnifiedConfig.from_yaml('.praxis-os/config/mcp.yaml')
    print('✅ Config valid')
except Exception as e:
    print(f'❌ Validation error: {e}')
"

# 2. Check common validation issues
# Priority must be 1, 2, or 3:
#   priority: high  # ❌ Wrong (must be int)
#   priority: 1     # ✅ Correct

# Query must be string:
#   query: ["test"]  # ❌ Wrong (list)
#   query: "test"    # ✅ Correct

# 3. Check for typos in field names
#   priorit: 1       # ❌ Typo
#   priority: 1      # ✅ Correct
```

---

#### Issue 6: ModuleNotFoundError: No module named 'mistletoe'

**Symptoms:**
- Import error when running orientation code
- `ModuleNotFoundError: No module named 'mistletoe'`

**Cause:**
Mistletoe dependency not installed

**Solution:**
```bash
# Install mistletoe
pip install mistletoe

# Verify installation
python -c "import mistletoe; print(f'Mistletoe version: {mistletoe.__version__}')"

# Update requirements.txt if missing
echo "mistletoe>=1.0.0" >> requirements.txt
```

---

#### Issue 7: Base Orientation Still Works, But No Project Queries

**Symptoms:**
- Base orientation (queries 1-10) executes successfully
- No project-specific queries discovered
- System functions normally otherwise

**Possible Causes:**
1. No orientation metadata defined in project (expected behavior)
2. Metadata not indexed yet
3. Query 10 not updated

**Solutions:**
```bash
# 1. Check if this is expected
# If project doesn't have orientation metadata, this is NORMAL behavior

# 2. Verify metadata exists
grep -r "orientation=true" standards/
# Should find at least one file if orientation defined

# 3. Verify Query 10 updated
grep "project orientation" standards/universal/ai-assistant/PRAXIS-OS-ORIENTATION.md
# Should find Query 10 with "project orientation discovery"

# 4. If metadata exists but not discovered, rebuild index
python -m ouroboros.subsystems.rag.index_manager rebuild --index=standards
```

---

### 6.2 Debugging Techniques

#### Enable Debug Logging
```python
import logging

# Set orientation logger to DEBUG
logging.getLogger('ouroboros.subsystems.rag.standards.orientation').setLevel(logging.DEBUG)

# Run orientation with verbose logging
from ouroboros.subsystems.rag.standards.orientation import OrientationDiscoveryHandler
handler = OrientationDiscoveryHandler(standards_index, config)
queries = handler.discover_orientation_queries()
# Check logs for detailed discovery process
```

#### Test Metadata Parsing in Isolation
```python
from ouroboros.subsystems.rag.standards.orientation import OrientationMetadataParser
from pathlib import Path

parser = OrientationMetadataParser()

# Test specific file
test_file = Path("standards/your-file.md")
content = test_file.read_text()
metadata = parser.extract_inline_metadata(content, test_file)

print(f"Parsed metadata: {metadata}")
print(f"Orientation field: {metadata.get('orientation')}")
print(f"Priority field: {metadata.get('priority')}")
```

#### Test Query Execution Manually
```python
from ouroboros.subsystems.rag.standards.orientation import ProjectOrientationExecutor
from ouroboros.subsystems.config.models import OrientationQuery

executor = ProjectOrientationExecutor(search_tool)

# Test single query
test_query = OrientationQuery(
    query="project architecture",
    priority=1
)

result = executor.execute_orientation([test_query])
print(f"Execution time: {result.total_time_ms}ms")
print(f"Timeout occurred: {result.timeout_occurred}")
print(f"Results: {len(result.results)}")
```

#### Inspect Standards Index
```python
from ouroboros.subsystems.rag.index_manager import IndexManager

mgr = IndexManager()

# Check index health
health = mgr.get_index_health("standards")
print(f"Index health: {health}")

# Search for orientation metadata
results = mgr.search_standards(
    query="orientation",
    filters={"orientation": True}
)
print(f"Files with orientation=true: {len(results.results)}")
```

#### Use Python Debugger (pdb)
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Then run orientation
from ouroboros.subsystems.rag.standards.orientation import OrientationDiscoveryHandler
handler = OrientationDiscoveryHandler(standards_index, config)
queries = handler.discover_orientation_queries()

# Debugger commands:
# n - next line
# s - step into
# c - continue
# p variable - print variable
# l - list code
```

---

### 6.3 Performance Debugging

#### Profile Orientation Execution Time
```python
import time
from ouroboros.subsystems.rag.standards.orientation import ProjectOrientationExecutor

# Profile with timing
start = time.time()
result = executor.execute_orientation(queries)
total_time = time.time() - start

print(f"Total execution time: {total_time:.2f}s")
print(f"Number of queries: {len(queries)}")
print(f"Average per query: {(total_time / len(queries)):.2f}s")

# Check individual query times
for query_result in result.results:
    print(f"{query_result['query']}: {query_result['execution_time_ms']}ms")
```

#### Profile Metadata Parsing Performance
```python
import time
from pathlib import Path
from ouroboros.subsystems.rag.standards.orientation import OrientationMetadataParser

parser = OrientationMetadataParser()
files = list(Path("standards").rglob("*.md"))

times = []
for file in files[:100]:  # Test first 100 files
    content = file.read_text()
    start = time.time()
    metadata = parser.extract_inline_metadata(content, file)
    elapsed_ms = (time.time() - start) * 1000
    times.append(elapsed_ms)

import statistics
print(f"Median: {statistics.median(times):.2f}ms")
print(f"p95: {statistics.quantiles(times, n=20)[18]:.2f}ms")
print(f"Max: {max(times):.2f}ms")
# Target: p95 < 100ms
```

#### Identify Slow Queries
```bash
# Run with benchmarking
pytest tests/performance/test_orientation_performance.py --benchmark-only -v

# Look for slow queries in output
# Optimize or remove queries that take > 5s
```

---

### 6.4 Getting Help

#### Information to Provide When Reporting Issues

**Required Information:**
1. **Error message** (full traceback)
2. **Steps to reproduce** (minimal example)
3. **Environment:**
   - Python version: `python --version`
   - praxis-os version: `git rev-parse HEAD`
   - Dependencies: `pip list | grep -E "mistletoe|pydantic"`
4. **Configuration:** Relevant mcp.yaml sections
5. **Sample data:** Example markdown file with metadata (if applicable)

**Example Issue Report:**
```markdown
## Issue: Orientation metadata not parsed

**Error:**
```
AttributeError: 'NoneType' object has no attribute 'group'
```

**Steps to Reproduce:**
1. Add metadata to standards/test.md:
   ```markdown
   **Metadata**: orientation=true
   ```
2. Run discovery:
   ```python
   from ouroboros.subsystems.rag.standards.orientation import OrientationDiscoveryHandler
   handler.discover_orientation_queries()
   ```
3. Error occurs

**Environment:**
- Python: 3.11.5
- praxis-os: commit abc123
- mistletoe: 1.2.1

**Configuration:**
```yaml
# No project.orientation section in mcp.yaml
```

**Sample file:** (attached)
```

#### Debugging Checklist Before Asking for Help

- [ ] Read this troubleshooting guide ✅/❌
- [ ] Check logs for errors/warnings ✅/❌
- [ ] Verify metadata format correct ✅/❌
- [ ] Test metadata parsing in isolation ✅/❌
- [ ] Verify standards index rebuilt ✅/❌
- [ ] Check mcp.yaml validation ✅/❌
- [ ] Run linting (flake8, mypy) ✅/❌
- [ ] Run tests to isolate issue ✅/❌
- [ ] Try minimal reproduction ✅/❌

#### Resources

**Documentation:**
- Project Orientation Guide: `standards/universal/workflows/project-orientation-guide.md`
- API Documentation: Docstrings in `orientation.py`
- Test Examples: `tests/ouroboros/subsystems/rag/standards/test_orientation.py`

**Code References:**
- Metadata Parser: `ouroboros/subsystems/rag/standards/orientation.py::OrientationMetadataParser`
- Pydantic Models: `ouroboros/subsystems/config/models.py::OrientationQuery`
- Discovery Handler: `ouroboros/subsystems/rag/standards/orientation.py::OrientationDiscoveryHandler`

---

**End of Implementation Guidance**

---


