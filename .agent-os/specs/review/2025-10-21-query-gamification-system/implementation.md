# Implementation Approach

**Project:** Query Gamification System  
**Date:** 2025-10-21

---

## 1. Implementation Philosophy

**Core Principles:**

1. **Minimalist Enhancement:** Add gamification without changing existing behavior. The system is an interceptor, not a replacement.

2. **Graceful Degradation:** Gamification failures must never break search. Error handling is mandatory at every integration point.

3. **Performance First:** Every operation must meet strict latency targets (≤20ms total overhead). Performance is a feature, not an afterthought.

4. **Type Safety:** 100% type hints coverage with mypy --strict passing. Types document intent and catch errors at compile time.

5. **Test-Driven Validation:** Every requirement (FR and NFR) must have corresponding tests. No requirement is "done" without test evidence.

---

## 2. Implementation Order

**Recommended Sequence** (from tasks.md):

```
Phase 1: Foundation (Parallel Implementation Recommended)
├── Task 1.1: QueryClassifier (1.5-2 hours)
├── Task 1.2: QueryTracker (2-2.5 hours)
├── Task 1.3: PrependGenerator (1-1.5 hours)
└── Task 1.4: SessionExtractor (0.5-1 hour)
     ↓
Phase 2: Integration (Sequential)
├── Task 2.1: Integrate into search_standards() (1.5-2 hours)
├── Task 2.2: Add error handling (0.5-1 hour)
└── Task 2.3: Validate backward compatibility (0.5 hour)
     ↓
Phase 3: Testing (Parallel Recommended)
├── Task 3.1: Unit tests (1.5-2 hours)
├── Task 3.2: Integration tests (1-1.5 hours)
├── Task 3.3: Performance tests (1-1.5 hours)
└── Task 3.4: Security tests (0.5-1 hour)
     ↓
Phase 4: Finalization (Sequential)
├── Task 4.1: Code review & cleanup (0.5-1 hour)
├── Task 4.2: Documentation (0.5 hour)
└── Task 4.3: Final validation (0.5 hour)
```

**Critical Path:** Phase 1 → Task 2.1 → Phase 3 → Phase 4 (~10-15 hours total)

---

## 3. Code Patterns

### Pattern 1: Pure Function Design

**Use Case:** QueryClassifier, PrependGenerator, SessionExtractor

**Why:** Pure functions are testable, predictable, and have no side effects. They're ideal for stateless operations like classification and formatting.

**Good Example:**

```python
def classify_query_angle(query: str) -> QueryAngle:
    """
    Pure function: same input → same output, no side effects.
    
    ✅ Pros:
    - Deterministic (testable with simple assertions)
    - No hidden state (all dependencies are parameters)
    - Thread-safe (no shared mutable state)
    """
    query_lower = query.lower()
    
    # Definition angle
    if any(kw in query_lower for kw in ['what is', 'define', 'explain']):
        return 'definition'
    
    # Location angle
    if any(kw in query_lower for kw in ['where', 'which file', 'locate']):
        return 'location'
    
    # Practical angle
    if any(kw in query_lower for kw in ['how to', 'implement', 'build']):
        return 'practical'
    
    # Best practice angle
    if any(kw in query_lower for kw in ['best practice', 'pattern', 'recommend']):
        return 'best_practice'
    
    # Error prevention angle
    if any(kw in query_lower for kw in ['avoid', 'mistake', 'pitfall', 'error']):
        return 'error_prevention'
    
    # Default fallback
    return 'definition'
```

**Anti-Pattern (❌ Don't do this):**

```python
# BAD: Side effects, global state, non-deterministic
classification_cache = {}  # Global mutable state

def classify_query_angle_bad(query: str) -> QueryAngle:
    """❌ Anti-pattern: Side effects and mutable global state"""
    # Side effect: modifying global cache
    if query in classification_cache:
        return classification_cache[query]
    
    # Side effect: printing (makes testing harder)
    print(f"Classifying: {query}")
    
    result = _classify_internal(query)
    classification_cache[query] = result  # Side effect
    return result
```

**Why Anti-Pattern is Bad:**
- Mutable global state breaks testability (tests interfere with each other)
- Print statements pollute test output
- Non-deterministic behavior (cache grows indefinitely)
- Not thread-safe

---

### Pattern 2: Singleton for Shared State

**Use Case:** QueryTracker (session statistics storage)

**Why:** QueryTracker must maintain state across multiple calls but have only one instance per process. Singleton ensures single source of truth.

**Good Example:**

```python
class QueryTracker:
    """Singleton pattern for session state management."""
    
    _instance: Optional['QueryTracker'] = None
    
    def __init__(self):
        """Private constructor (use get_tracker() instead)."""
        if QueryTracker._instance is not None:
            raise RuntimeError("Use get_tracker() to get singleton instance")
        
        self._sessions: Dict[str, QueryStats] = {}
    
    def record_query(self, session_id: str, query: str) -> QueryAngle:
        """
        ✅ Pros:
        - Centralized state (single source of truth)
        - Session isolation (separate stats per session_id)
        - Bounded memory (query history limited to 10 per session)
        """
        # Get or create session stats
        if session_id not in self._sessions:
            self._sessions[session_id] = QueryStats()
        
        stats = self._sessions[session_id]
        
        # Update statistics
        stats.total_queries += 1
        
        # Classify query
        angle = classify_query_angle(query)
        stats.angles_covered.add(angle)
        
        # Check uniqueness (normalized comparison)
        normalized = query.lower().strip()
        if normalized not in [q.lower().strip() for q in stats.query_history]:
            stats.unique_queries += 1
        
        # Update history (FIFO, max 10)
        if len(stats.query_history) >= 10:
            stats.query_history.pop(0)
        stats.query_history.append(query)
        
        # Update timestamp
        stats.last_query_time = datetime.now(timezone.utc)
        
        return angle

# Module-level singleton accessor
_tracker_instance: Optional[QueryTracker] = None

def get_tracker() -> QueryTracker:
    """Get the singleton QueryTracker instance."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = QueryTracker()
    return _tracker_instance
```

**Anti-Pattern (❌ Don't do this):**

```python
# BAD: Creating new instance every time
def get_tracker_bad() -> QueryTracker:
    """❌ Anti-pattern: Returns new instance (loses state)"""
    return QueryTracker()  # New instance = lost state!

# BAD: Global mutable dict (no encapsulation)
SESSIONS = {}  # ❌ Global mutable state exposed

def record_query_bad(session_id: str, query: str):
    """❌ Anti-pattern: Direct global state manipulation"""
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {'total': 0, 'queries': []}
    
    SESSIONS[session_id]['total'] += 1
    SESSIONS[session_id]['queries'].append(query)
```

**Why Anti-Pattern is Bad:**
- `get_tracker_bad()` creates new instance every time (state is lost)
- Global `SESSIONS` dict has no encapsulation (any code can modify it)
- No type safety on dict contents (keys/values are Any)
- Hard to test (global state persists between tests)

---

### Pattern 3: Interceptor Pattern with Error Handling

**Use Case:** Integration into search_standards()

**Why:** Gamification is an optional enhancement that must never break core functionality. The interceptor pattern with try-except ensures graceful degradation.

**Good Example:**

```python
async def search_standards(
    query: str,
    n_results: int = 5,
    filter_phase: int | None = None,
    filter_tags: list[str] | None = None,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Enhanced with gamification interceptor.
    
    ✅ Pros:
    - Gamification is additive only (doesn't replace functionality)
    - Error handling prevents failures from propagating
    - Backward compatible (signature unchanged)
    - Session ID hashed in logs (privacy per NFR-S1)
    """
    # STEP 1: Perform search (core functionality, always runs)
    formatted_results = _perform_search(query, n_results, filter_phase, filter_tags)
    
    # STEP 2: Add gamification (optional enhancement, wrapped in try-except)
    try:
        # Extract session ID
        session_id = extract_session_id_from_context()
        
        # Record query
        tracker = get_tracker()
        tracker.record_query(session_id, query)
        
        # Generate prepend
        prepend = generate_query_prepend(tracker, session_id, query)
        
        # Add prepend to first result only
        if formatted_results and len(formatted_results) > 0:
            formatted_results[0]["content"] = prepend + formatted_results[0]["content"]
    
    except Exception as e:
        # Log error with hashed session ID (privacy)
        hashed_id = hash_session_id(session_id) if session_id else "unknown"
        logger.error(
            f"Gamification error (session={hashed_id}): {type(e).__name__}",
            exc_info=True  # Full traceback for debugging
        )
        # Graceful degradation: return unmodified results
        # No error propagated to caller
    
    # STEP 3: Return results (with or without gamification)
    return formatted_results
```

**Anti-Pattern (❌ Don't do this):**

```python
# BAD: No error handling, breaks search on gamification error
async def search_standards_bad(query: str, ...) -> list:
    """❌ Anti-pattern: Gamification errors break search"""
    formatted_results = _perform_search(query, ...)
    
    # ❌ NO TRY-EXCEPT: If gamification fails, entire function fails
    session_id = extract_session_id_from_context()  # Can raise exception
    tracker = get_tracker()
    tracker.record_query(session_id, query)  # Can raise exception
    prepend = generate_query_prepend(tracker, session_id, query)  # Can raise exception
    formatted_results[0]["content"] = prepend + formatted_results[0]["content"]
    
    return formatted_results

# BAD: Logging plain session ID (privacy violation)
async def search_standards_privacy_bad(query: str, ...) -> list:
    """❌ Anti-pattern: Logs plain session ID (violates NFR-S1)"""
    formatted_results = _perform_search(query, ...)
    
    try:
        session_id = extract_session_id_from_context()
        tracker = get_tracker()
        tracker.record_query(session_id, query)
        prepend = generate_query_prepend(tracker, session_id, query)
        formatted_results[0]["content"] = prepend + formatted_results[0]["content"]
    except Exception as e:
        # ❌ PRIVACY VIOLATION: Plain session ID in logs
        logger.error(f"Gamification error (session={session_id}): {e}")
    
    return formatted_results
```

**Why Anti-Pattern is Bad:**
- First example: No error handling means gamification failures break search
- Second example: Plain session ID in logs violates NFR-S1 (session privacy)
- Both examples fail graceful degradation requirement (NFR-R1)

---

### Pattern 4: Bounded Collections

**Use Case:** QueryStats query_history (limited to 10 entries)

**Why:** Unbounded collections cause memory leaks. Bounded collections with FIFO eviction ensure predictable memory usage.

**Good Example:**

```python
@dataclass
class QueryStats:
    """
    ✅ Pros:
    - Query history bounded to 10 (prevents memory leak)
    - Angles bounded to 5 (only 5 possible values)
    - Memory per session predictable (~1KB)
    """
    total_queries: int = 0
    unique_queries: int = 0
    angles_covered: Set[QueryAngle] = field(default_factory=set)  # Max 5 elements
    query_history: List[str] = field(default_factory=list)  # Max 10 elements
    last_query_time: datetime | None = None

def record_query(self, session_id: str, query: str) -> QueryAngle:
    """Record query with bounded history."""
    stats = self._sessions.get(session_id, QueryStats())
    
    # ... classification and statistics updates ...
    
    # ✅ BOUNDED: FIFO eviction when history exceeds 10
    if len(stats.query_history) >= 10:
        stats.query_history.pop(0)  # Remove oldest
    stats.query_history.append(query)  # Add newest
    
    return angle
```

**Anti-Pattern (❌ Don't do this):**

```python
# BAD: Unbounded collections (memory leak)
@dataclass
class QueryStatsBad:
    """❌ Anti-pattern: Unbounded collections"""
    total_queries: int = 0
    unique_queries: int = 0
    angles_covered: Set[QueryAngle] = field(default_factory=set)
    query_history: List[str] = field(default_factory=list)  # ❌ UNBOUNDED!
    last_query_time: datetime | None = None

def record_query_bad(self, session_id: str, query: str) -> QueryAngle:
    """❌ Anti-pattern: No bounds on history growth"""
    stats = self._sessions.get(session_id, QueryStatsBad())
    
    # ❌ NO LIMIT: History grows forever (memory leak)
    stats.query_history.append(query)  # 10,000 queries = huge memory!
    
    return angle
```

**Why Anti-Pattern is Bad:**
- Memory leak: 10,000 queries per session = 500KB per session (violates NFR-P3)
- No eviction policy: Old queries never removed
- Unpredictable memory: Can't estimate memory usage

---

### Pattern 5: Type-Safe Enumerations with Literal Types

**Use Case:** QueryAngle (5 valid angle types)

**Why:** Python Literal types provide compile-time type safety without runtime overhead. Better than string enums for simple cases.

**Good Example:**

```python
from typing import Literal

# ✅ Type-safe enumeration
QueryAngle = Literal[
    'definition',
    'location',
    'practical',
    'best_practice',
    'error_prevention'
]

def classify_query_angle(query: str) -> QueryAngle:
    """
    ✅ Pros:
    - Return type is checked by mypy (only 5 valid values)
    - No runtime overhead (strings at runtime)
    - Self-documenting (values show meaning)
    """
    # ... classification logic ...
    return 'definition'  # ✅ Valid (type checker accepts)

# Type checker catches invalid values at compile time
def process_angle(angle: QueryAngle) -> str:
    """Type checker enforces valid angles."""
    if angle == 'definition':
        return "📖"
    elif angle == 'location':
        return "📍"
    # ... handle other cases ...
    else:
        # Type checker knows this is unreachable (all cases covered)
        raise AssertionError(f"Unexpected angle: {angle}")
```

**Anti-Pattern (❌ Don't do this):**

```python
# BAD: Using plain strings (no type safety)
def classify_query_angle_bad(query: str) -> str:  # ❌ No constraint on return value
    """❌ Anti-pattern: Plain string (any value allowed)"""
    # ... classification logic ...
    return 'defination'  # ❌ Typo! Type checker doesn't catch it

# BAD: Using class constants (verbose, no type checking benefit)
class QueryAngleBad:
    """❌ Anti-pattern: Class constants (verbose, no type checking)"""
    DEFINITION = 'definition'
    LOCATION = 'location'
    PRACTICAL = 'practical'
    BEST_PRACTICE = 'best_practice'
    ERROR_PREVENTION = 'error_prevention'

def classify_query_angle_verbose(query: str) -> str:  # ❌ Still just 'str'
    """❌ Anti-pattern: Constants don't provide type safety"""
    return QueryAngleBad.DEFINITION  # Verbose, no type checking benefit

# BAD: Using Enum (unnecessary runtime overhead for simple strings)
from enum import Enum

class QueryAngleEnum(Enum):
    """❌ Anti-pattern: Enum adds runtime overhead"""
    DEFINITION = 'definition'
    LOCATION = 'location'
    # ... etc

def classify_query_angle_enum(query: str) -> QueryAngleEnum:  # Requires .value access
    """❌ Anti-pattern: Enum is overkill for simple string literals"""
    return QueryAngleEnum.DEFINITION  # Returns enum object, need .value to get string
```

**Why Anti-Pattern is Bad:**
- Plain strings: No type safety, typos not caught
- Class constants: Verbose, no type checking benefit over plain strings
- Enum: Runtime overhead (object creation), need `.value` to get string, overkill for simple cases

---

## Pattern Summary

**Pattern Count:** 5 core patterns documented  
**Anti-Patterns Identified:** 5 (one per pattern)  
**Components Mapped:** All 5 components (QueryClassifier, QueryTracker, PrependGenerator, SessionExtractor, Integration Layer)

**Pattern Application:**

| Component | Primary Pattern | Secondary Pattern |
|-----------|----------------|-------------------|
| QueryClassifier | Pure Function Design | Type-Safe Enumerations |
| QueryTracker | Singleton for Shared State | Bounded Collections |
| PrependGenerator | Pure Function Design | - |
| SessionExtractor | Pure Function Design | - |
| Integration Layer | Interceptor with Error Handling | - |

**Next:** Continue to Task 2 (Testing Strategy)

---

## 4. Testing Strategy

### 4.1 Testing Philosophy

**Test Pyramid:**
```
           /\
          /  \
         / E2E \ (Few: 6 integration tests)
        /______\
       /        \
      / Integr.  \ (Some: 10 integration tests)
     /____________\
    /              \
   /   Unit Tests   \ (Many: 30+ unit tests)
  /__________________\
```

**Coverage Targets:**
- **Unit Tests:** ≥95% coverage on core modules
- **Integration Tests:** 100% coverage of critical paths (search_standards flow)
- **Performance Tests:** All SLAs validated (latency, memory, token cost)
- **Security Tests:** All NFR-S1 controls validated (session ID hashing, log privacy)

**Testing Principles:**
1. **Test behavior, not implementation:** Tests should verify what code does, not how it does it
2. **One assertion concept per test:** Each test validates one specific behavior
3. **Arrange-Act-Assert pattern:** Structure all tests with clear setup, execution, verification
4. **Fast feedback:** Unit tests run in <1s, full suite in <10s
5. **Deterministic:** Tests never flake (no random data, no timing dependencies)

---

### 4.2 Unit Testing Strategy

**Coverage Target:** ≥95% on all 4 core modules

**Test Organization:**
```
tests/
├── core/
│   ├── __init__.py
│   ├── test_query_classifier.py      (≥8 tests)
│   ├── test_query_tracker.py         (≥10 tests)
│   ├── test_prepend_generator.py     (≥6 tests)
│   └── test_session_id_extractor.py  (≥4 tests)
├── integration/
│   └── test_search_standards_gamification.py  (≥6 tests)
├── performance/
│   └── test_gamification_performance.py       (≥8 tests)
└── security/
    └── test_gamification_security.py          (≥6 tests)
```

**Unit Test Pattern (Arrange-Act-Assert):**

```python
import pytest
from mcp_server.core.query_classifier import classify_query_angle, QueryAngle

def test_classify_definition_angle():
    """Test classification of definition-type queries."""
    # Arrange
    queries = [
        "What is validation?",
        "Define checkpoint criteria",
        "Explain phase gating"
    ]
    
    # Act & Assert
    for query in queries:
        angle = classify_query_angle(query)
        assert angle == 'definition', f"Query '{query}' should classify as 'definition'"

def test_classify_location_angle():
    """Test classification of location-type queries."""
    # Arrange
    query = "Where is validation handled?"
    
    # Act
    angle = classify_query_angle(query)
    
    # Assert
    assert angle == 'location'
    assert isinstance(angle, str)  # Type check

def test_classify_practical_angle():
    """Test classification of practical-type queries."""
    # Arrange
    queries = ["How to validate?", "How do I implement X?"]
    
    # Act & Assert
    for query in queries:
        angle = classify_query_angle(query)
        assert angle == 'practical'

def test_classify_best_practice_angle():
    """Test classification of best practice queries."""
    # Arrange
    query = "What are validation best practices?"
    
    # Act
    angle = classify_query_angle(query)
    
    # Assert
    assert angle == 'best_practice'

def test_classify_error_prevention_angle():
    """Test classification of error prevention queries."""
    # Arrange
    query = "Common validation mistakes to avoid"
    
    # Act
    angle = classify_query_angle(query)
    
    # Assert
    assert angle == 'error_prevention'

def test_classify_fallback_to_definition():
    """Test that unknown queries default to 'definition'."""
    # Arrange
    query = "xyz abc 123"  # No keywords match
    
    # Act
    angle = classify_query_angle(query)
    
    # Assert
    assert angle == 'definition', "Unknown queries should default to 'definition'"

def test_classify_case_insensitive():
    """Test that classification is case-insensitive."""
    # Arrange
    queries_same_meaning = [
        "What is validation?",
        "WHAT IS VALIDATION?",
        "what is validation?"
    ]
    
    # Act
    angles = [classify_query_angle(q) for q in queries_same_meaning]
    
    # Assert
    assert all(angle == 'definition' for angle in angles), \
        "Case variations should produce same classification"

def test_classify_latency_performance():
    """Test that classification meets latency target (≤5ms)."""
    import time
    
    # Arrange
    query = "What is validation?"
    
    # Act
    start = time.perf_counter()
    angle = classify_query_angle(query)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    # Assert
    assert angle == 'definition'
    assert elapsed_ms <= 5.0, f"Classification took {elapsed_ms:.2f}ms (target: ≤5ms)"
```

**Testing QueryTracker (Stateful Singleton):**

```python
import pytest
from mcp_server.core.query_tracker import get_tracker, QueryStats

@pytest.fixture
def tracker():
    """Fixture providing a fresh QueryTracker for each test."""
    tracker = get_tracker()
    # Reset state before each test
    tracker._sessions.clear()
    return tracker

def test_record_query_increments_total(tracker):
    """Test that record_query increments total_queries."""
    # Arrange
    session_id = "test_session"
    query = "What is X?"
    
    # Act
    tracker.record_query(session_id, query)
    stats = tracker.get_stats(session_id)
    
    # Assert
    assert stats.total_queries == 1

def test_record_query_detects_unique(tracker):
    """Test that duplicate queries (case-insensitive) don't increment unique count."""
    # Arrange
    session_id = "test_session"
    
    # Act
    tracker.record_query(session_id, "What is X?")
    tracker.record_query(session_id, "what is x?")  # Duplicate (case-insensitive)
    tracker.record_query(session_id, "What is Y?")  # Unique
    
    stats = tracker.get_stats(session_id)
    
    # Assert
    assert stats.total_queries == 3, "Total should count all queries"
    assert stats.unique_queries == 2, "Unique should count normalized-unique queries"

def test_record_query_limits_history_to_10(tracker):
    """Test that query history is limited to 10 entries (FIFO)."""
    # Arrange
    session_id = "test_session"
    
    # Act: Record 15 queries
    for i in range(15):
        tracker.record_query(session_id, f"Query {i}")
    
    stats = tracker.get_stats(session_id)
    
    # Assert
    assert len(stats.query_history) == 10, "History should be limited to 10"
    assert stats.query_history[0] == "Query 5", "Oldest should be query 5 (0-4 evicted)"
    assert stats.query_history[-1] == "Query 14", "Newest should be query 14"

def test_session_isolation(tracker):
    """Test that sessions have independent statistics."""
    # Arrange & Act
    tracker.record_query("session_A", "Query A1")
    tracker.record_query("session_A", "Query A2")
    tracker.record_query("session_B", "Query B1")
    
    stats_a = tracker.get_stats("session_A")
    stats_b = tracker.get_stats("session_B")
    
    # Assert
    assert stats_a.total_queries == 2
    assert stats_b.total_queries == 1
    assert len(stats_a.angles_covered) >= 1
    assert len(stats_b.angles_covered) >= 1
```

---

### 4.3 Integration Testing Strategy

**Scope:** Test full gamification flow integrated with search_standards()

**Coverage Target:** 100% of critical paths (search with gamification, error handling, backward compatibility)

**Integration Test Pattern:**

```python
import pytest
from mcp_server.server.tools.rag_tools import search_standards
from mcp_server.core.query_tracker import get_tracker

@pytest.fixture
def reset_tracker():
    """Reset tracker state between integration tests."""
    tracker = get_tracker()
    tracker._sessions.clear()
    yield
    tracker._sessions.clear()

def test_search_standards_adds_prepend(reset_tracker):
    """Test that search_standards adds prepend to first result."""
    # Arrange
    query = "What is validation?"
    
    # Act
    results = await search_standards(query)
    
    # Assert
    assert len(results) > 0, "Should return results"
    first_result = results[0]
    assert "content" in first_result
    assert "🔍🔍🔍🔍🔍" in first_result["content"], "Should contain prepend header"
    assert "Queries: 1/5" in first_result["content"], "Should show query count"

def test_search_standards_progressive_stats(reset_tracker):
    """Test that stats update across multiple queries."""
    # Arrange & Act
    results1 = await search_standards("What is X?")
    results2 = await search_standards("Where is X?")
    results3 = await search_standards("How to X?")
    
    # Assert
    assert "Queries: 1/5" in results1[0]["content"]
    assert "Queries: 2/5" in results2[0]["content"]
    assert "Queries: 3/5" in results3[0]["content"]

def test_search_standards_prepend_only_on_first_result(reset_tracker):
    """Test that prepend appears only on first result."""
    # Arrange
    query = "What is validation?"
    
    # Act
    results = await search_standards(query, n_results=3)
    
    # Assert
    assert len(results) >= 2, "Need multiple results for test"
    assert "🔍🔍🔍🔍🔍" in results[0]["content"], "First result should have prepend"
    assert "🔍🔍🔍🔍🔍" not in results[1]["content"], "Second result should NOT have prepend"

def test_search_standards_graceful_degradation_on_error(reset_tracker, monkeypatch):
    """Test that gamification errors don't break search."""
    # Arrange: Mock get_tracker to raise exception
    def mock_get_tracker():
        raise RuntimeError("Simulated gamification error")
    
    monkeypatch.setattr("mcp_server.server.tools.rag_tools.get_tracker", mock_get_tracker)
    
    # Act (should not raise exception)
    results = await search_standards("What is validation?")
    
    # Assert
    assert len(results) > 0, "Search should still work despite gamification error"
    # Prepend should NOT be present (graceful degradation)
    assert "🔍🔍🔍🔍🔍" not in results[0]["content"]

def test_search_standards_backward_compatibility(reset_tracker):
    """Test that function signature and return type are unchanged."""
    # Arrange
    import inspect
    from mcp_server.server.tools.rag_tools import search_standards
    
    # Act
    sig = inspect.signature(search_standards)
    
    # Assert: Check parameter names
    param_names = list(sig.parameters.keys())
    assert "query" in param_names
    assert "n_results" in param_names
    assert "filter_phase" in param_names
    assert "filter_tags" in param_names
    
    # Assert: Check return type annotation
    return_annotation = sig.return_annotation
    assert return_annotation is not inspect.Signature.empty, "Should have return type annotation"
```

---

### 4.4 Mocking Strategy

**When to Mock:**

1. **External Dependencies** (always mock in unit tests)
   - File I/O
   - Network requests
   - Environment variables

2. **Expensive Operations** (mock in unit tests, test real in integration tests)
   - Database queries
   - Search operations

3. **Non-Deterministic Sources** (always mock)
   - Current time (`datetime.now`)
   - Random number generation
   - Process ID (`os.getpid`)

**When NOT to Mock:**

1. **Pure Functions** (test directly, no mocking needed)
   - `classify_query_angle()` - no dependencies
   - `hash_session_id()` - stdlib hashlib is deterministic

2. **Fast In-Memory Operations** (test directly)
   - `QueryTracker` operations - in-memory dict operations
   - `generate_query_prepend()` - string formatting

**Mocking Examples:**

```python
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

def test_record_query_with_mocked_time():
    """Test timestamp recording with mocked current time."""
    # Arrange
    fixed_time = datetime(2025, 10, 21, 12, 0, 0, tzinfo=timezone.utc)
    tracker = get_tracker()
    tracker._sessions.clear()
    
    # Act
    with patch('mcp_server.core.query_tracker.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        tracker.record_query("session_1", "What is X?")
    
    stats = tracker.get_stats("session_1")
    
    # Assert
    assert stats.last_query_time == fixed_time

def test_extract_session_id_with_mocked_pid():
    """Test session ID extraction with mocked process ID."""
    # Arrange
    from mcp_server.core.session_id_extractor import extract_session_id_from_context
    
    # Act
    with patch('os.getpid', return_value=12345):
        session_id = extract_session_id_from_context()
    
    # Assert
    assert session_id == "session_12345"

def test_search_standards_with_mocked_search():
    """Test gamification with mocked underlying search."""
    # Arrange
    mock_results = [
        {"type": "text", "content": "Original search result"}
    ]
    
    # Act
    with patch('mcp_server.server.tools.rag_tools._perform_search', return_value=mock_results):
        results = await search_standards("What is X?")
    
    # Assert
    assert len(results) == 1
    assert "🔍🔍🔍🔍🔍" in results[0]["content"], "Should add prepend"
    assert "Original search result" in results[0]["content"], "Should preserve original content"
```

---

### 4.5 Performance Testing Strategy

**Scope:** Validate all latency and memory SLAs (NFR-P1 through NFR-P4)

**Coverage Target:** 100% of performance requirements validated

**Performance Test Pattern:**

```python
import pytest
import time
import tracemalloc
from mcp_server.core.query_classifier import classify_query_angle
from mcp_server.core.query_tracker import get_tracker

def test_classifier_latency_sla():
    """Test that classification meets ≤5ms p95 latency target."""
    # Arrange
    query = "What is validation?"
    latencies = []
    
    # Act: Measure 100 runs
    for _ in range(100):
        start = time.perf_counter()
        angle = classify_query_angle(query)
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)
    
    # Assert: Check p95 latency
    latencies_sorted = sorted(latencies)
    p95_latency = latencies_sorted[94]  # 95th percentile
    assert p95_latency <= 5.0, f"p95 latency {p95_latency:.2f}ms exceeds 5ms target"

def test_memory_usage_for_100_sessions():
    """Test that 100 sessions use ≤100KB memory."""
    # Arrange
    tracker = get_tracker()
    tracker._sessions.clear()
    tracemalloc.start()
    
    # Act: Create 100 sessions with 10 queries each
    for session_idx in range(100):
        session_id = f"session_{session_idx}"
        for query_idx in range(10):
            tracker.record_query(session_id, f"Query {query_idx}")
    
    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Assert
    memory_kb = peak_memory / 1024
    assert memory_kb <= 100, f"Memory usage {memory_kb:.2f}KB exceeds 100KB target"

def test_token_budget_compliance():
    """Test that prepend messages stay within token budget."""
    from mcp_server.core.prepend_generator import generate_query_prepend
    
    # Arrange
    tracker = get_tracker()
    tracker._sessions.clear()
    
    # Act: Test various scenarios
    scenarios = [
        (1, "early"),   # 1 query
        (3, "mid"),     # 3 queries
        (5, "complete") # 5 queries
    ]
    
    for query_count, label in scenarios:
        tracker._sessions.clear()
        for i in range(query_count):
            tracker.record_query("test_session", f"Query {i}")
        
        prepend = generate_query_prepend(tracker, "test_session", f"Query {query_count-1}")
        
        # Rough token count (split by whitespace)
        token_count = len(prepend.split())
        
        # Assert: ≤120 tokens max
        assert token_count <= 120, \
            f"Token count {token_count} exceeds 120 for scenario '{label}'"
```

---

### 4.6 Security Testing Strategy

**Scope:** Validate session ID privacy (NFR-S1) and input validation

**Coverage Target:** 100% of security controls validated

**Security Test Pattern:**

```python
import pytest
import logging
from mcp_server.core.session_id_extractor import hash_session_id

def test_session_id_hashing_produces_16_char_hex():
    """Test that hash_session_id produces 16-character hex strings."""
    # Arrange
    session_ids = ["session_123", "session_456", "default"]
    
    # Act & Assert
    for session_id in session_ids:
        hashed = hash_session_id(session_id)
        assert len(hashed) == 16, f"Hash length {len(hashed)} != 16"
        assert all(c in '0123456789abcdef' for c in hashed), "Hash should be hex"

def test_session_id_hashing_is_deterministic():
    """Test that same input produces same hash."""
    # Arrange
    session_id = "session_12345"
    
    # Act
    hash1 = hash_session_id(session_id)
    hash2 = hash_session_id(session_id)
    hash3 = hash_session_id(session_id)
    
    # Assert
    assert hash1 == hash2 == hash3, "Hashing should be deterministic"

def test_no_plain_session_ids_in_logs(caplog):
    """Test that logs contain hashed session IDs only."""
    # Arrange
    tracker = get_tracker()
    tracker._sessions.clear()
    
    # Act: Trigger logging (simulate error scenario)
    with caplog.at_level(logging.ERROR):
        # Force an error in gamification
        with patch('mcp_server.server.tools.rag_tools.get_tracker', side_effect=Exception("Test error")):
            try:
                await search_standards("What is X?")
            except:
                pass
    
    # Assert: Check logs don't contain plain session ID
    log_text = caplog.text
    assert "session_" not in log_text or \
           all(len(word) == 16 for word in log_text.split() if "session" in word.lower()), \
           "Logs should only contain hashed (16-char) session IDs"

def test_empty_query_raises_valueerror():
    """Test that empty queries are rejected."""
    # Arrange
    tracker = get_tracker()
    
    # Act & Assert
    with pytest.raises(ValueError, match="Query must be non-empty"):
        tracker.record_query("session_1", "")

def test_none_query_raises_valueerror():
    """Test that None queries are rejected."""
    # Arrange
    tracker = get_tracker()
    
    # Act & Assert
    with pytest.raises((ValueError, TypeError)):
        tracker.record_query("session_1", None)
```

---

### 4.7 Testing Checklist

**Before considering implementation complete:**

- [ ] All unit tests passing (`pytest tests/core/ -v`)
- [ ] All integration tests passing (`pytest tests/integration/ -v`)
- [ ] All performance tests passing (`pytest tests/performance/ -v`)
- [ ] All security tests passing (`pytest tests/security/ -v`)
- [ ] Code coverage ≥95% on core modules (`pytest --cov=mcp_server/core --cov-report=term`)
- [ ] No flaky tests (run suite 10 times, all passes)
- [ ] Fast feedback (<10s for full test suite)
- [ ] Test documentation complete (all tests have docstrings)
- [ ] Edge cases covered (empty inputs, None, large inputs)
- [ ] Error paths tested (exceptions, invalid inputs)
- [ ] Performance SLAs validated (latency, memory, token cost)
- [ ] Security controls validated (session ID hashing, log privacy)

---

### 4.8 Test Execution Commands

**Run all tests:**
```bash
pytest tests/ -v
```

**Run tests by category:**
```bash
pytest tests/core/ -v                 # Unit tests
pytest tests/integration/ -v          # Integration tests
pytest tests/performance/ -v          # Performance tests
pytest tests/security/ -v             # Security tests
```

**Run with coverage:**
```bash
pytest tests/ --cov=mcp_server --cov-report=html
```

**Run performance tests with detailed timing:**
```bash
pytest tests/performance/ -v -s       # -s shows print output
```

**Run tests in parallel (faster):**
```bash
pytest tests/ -n auto                 # Requires pytest-xdist
```

---

## Testing Strategy Summary

**Test Categories:** 4 (Unit, Integration, Performance, Security)  
**Total Tests:** 50+ across all categories  
**Coverage Target:** ≥95% on core modules, 100% on critical paths  
**Test Examples Provided:** 20+ concrete test functions  
**Mocking Strategy:** Documented with 3 examples  

**Next:** Continue to Task 3 (Deployment Guidance)

---

## 5. Deployment

### 5.1 Deployment Prerequisites

**Before deploying:**
- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Code coverage ≥90% (`pytest --cov`)
- [ ] No linting errors (`ruff check mcp_server/`)
- [ ] No type errors (`mypy --strict mcp_server/core/`)
- [ ] Performance SLAs validated
- [ ] Security tests passing

### 5.2 Deployment Steps

**Zero-downtime deployment (in-process enhancement):**

```bash
# 1. Pre-deployment checks
pytest tests/ -v
mypy --strict mcp_server/core/
ruff check mcp_server/

# 2. Merge to main
git checkout main
git merge feature/query-gamification
git push origin main

# 3. Restart MCP server (gamification auto-enabled)
# Method depends on deployment:
# - Development: Restart process
# - Production: Rolling restart of MCP server instances

# 4. Post-deployment verification
# - Check logs for "Gamification enabled" message
# - Manual test: Run search_standards() and verify prepend appears
# - Monitor error rates (should be 0% for gamification errors)
```

**Deployment is simple:**
- No database migrations (in-memory only)
- No configuration changes required (auto-enabled)
- No external dependencies (stdlib only)
- Backward compatible (existing code works unchanged)

### 5.3 Rollback Plan

**If issues detected:**

```bash
# Option 1: Fast rollback (revert commit)
git revert <commit-hash>
git push origin main
# Restart MCP server

# Option 2: Feature flag disable (if implemented)
export ENABLE_QUERY_GAMIFICATION=false
# Restart MCP server

# Option 3: Emergency rollback (previous version)
git checkout <previous-commit>
# Deploy previous version
```

**Rollback is safe:**
- No persistent state (in-memory only)
- No data loss (no database)
- Instant rollback (restart process)

**Rollback triggers:**
- Error rate >0.1%
- Search latency increase >5%
- User reports of issues

### 5.4 Monitoring & Alerts

**Key Metrics:**
- Gamification error rate (target: 0%)
- Search latency impact (target: <5% increase)
- Memory usage per session (target: ~1KB)
- Token cost per prepend (target: ~85 tokens avg)

**Alerts:**
- ⚠️ Warning: Gamification error rate >0.01%
- 🚨 Critical: Search latency increase >10%
- 🚨 Critical: Memory usage >200KB per 100 sessions

---

## 6. Troubleshooting

### 6.1 Common Issues

#### Issue 1: Prepend Not Appearing

**Symptoms:** search_standards() returns results but no prepend visible

**Diagnosis:**
```python
# Check if gamification is running
from mcp_server.core.query_tracker import get_tracker
tracker = get_tracker()
print(f"Active sessions: {len(tracker._sessions)}")
```

**Possible Causes:**
1. Gamification disabled (feature flag)
2. Exception in gamification code (check logs)
3. Session ID extraction failing

**Resolution:**
```bash
# Check logs for errors
grep "Gamification error" logs/*.log

# Enable debug logging
export LOG_LEVEL=DEBUG

# Test session ID extraction
python -c "from mcp_server.core.session_id_extractor import extract_session_id_from_context; print(extract_session_id_from_context())"
```

#### Issue 2: High Memory Usage

**Symptoms:** Memory usage growing over time

**Diagnosis:**
```python
# Check session count
tracker = get_tracker()
print(f"Total sessions: {len(tracker._sessions)}")

# Check query history per session
for session_id, stats in tracker._sessions.items():
    print(f"{session_id}: {len(stats.query_history)} queries in history")
```

**Possible Causes:**
1. Too many concurrent sessions
2. Query history not evicting (bug in FIFO logic)

**Resolution:**
- Verify query history limited to 10 per session
- Check for memory leaks in QueryTracker
- Monitor session count over time

#### Issue 3: Performance Degradation

**Symptoms:** Search latency increased

**Diagnosis:**
```python
import time
start = time.perf_counter()
# Run gamification code
elapsed_ms = (time.perf_counter() - start) * 1000
print(f"Gamification latency: {elapsed_ms:.2f}ms")
```

**Possible Causes:**
1. Gamification overhead >20ms
2. Query classification slow
3. Too many queries in history

**Resolution:**
- Profile with cProfile
- Check query history length (should be ≤10)
- Verify no blocking I/O in critical path

### 6.2 Debugging Commands

```bash
# Check gamification status
python -c "from mcp_server.core.query_tracker import get_tracker; t=get_tracker(); print(f'Sessions: {len(t._sessions)}')"

# Test classification
python -c "from mcp_server.core.query_classifier import classify_query_angle; print(classify_query_angle('What is validation?'))"

# Test prepend generation
python -c "from mcp_server.core.prepend_generator import generate_query_prepend; from mcp_server.core.query_tracker import get_tracker; t=get_tracker(); t.record_query('test', 'Query 1'); print(generate_query_prepend(t, 'test', 'Query 1'))"

# Check logs
tail -f logs/mcp_server.log | grep -i gamification
```

### 6.3 Performance Profiling

```python
import cProfile
import pstats

# Profile gamification flow
profiler = cProfile.Profile()
profiler.enable()

# Run gamification code
tracker = get_tracker()
tracker.record_query("session_1", "What is validation?")
prepend = generate_query_prepend(tracker, "session_1", "What is validation?")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slowest functions
```

---

## Implementation Guidance Complete

**Phase 4 Deliverables:**
- ✅ 5 code patterns documented with examples
- ✅ 5 anti-patterns identified
- ✅ Testing strategy defined (4 test categories, 50+ tests)
- ✅ 20+ test examples provided
- ✅ Deployment procedures documented
- ✅ Rollback plan defined
- ✅ Troubleshooting guide provided (3 common issues)

**Total Documentation:** ~1,150 lines of implementation guidance

**Next:** Proceed to Phase 5 (Finalization)


