# Implementation Approach

**Project:** Parser Submodule Refactor  
**Date:** 2025-11-05  
**Based on:** srd.md (requirements), specs.md (design), tasks.md (implementation plan)

---

## 1. Implementation Philosophy

**Core Principles:**

1. **Incremental Migration:** Refactor in 8 phases with validation gates between each. Maintain backward compatibility throughout.

2. **Test-Driven Validation:** Write tests during extraction, not after. Each utility module must have ≥85% coverage before integration.

3. **Zero Regressions:** Use regression test suite on all completed specs. Any parsing differences must be improvements, not breakages.

4. **Defensive Programming:** Handle format variations gracefully. Use semantic scoring instead of rigid pattern matching.

5. **Clean Architecture:** Clear module boundaries, one-way dependencies, composition over inheritance.

---

## 2. Implementation Order

**Critical Path (8.5 hours):**

```
Phase 0: Foundation (0.5h) → Baseline + Regression Suite
    ↓
Phase 1: Structure (0.5h) → Directory Creation
    ↓
Phase 2: Base Classes (1h) → SourceParser + ParseError
    ↓
Phase 4: Utilities (1.5h) → Extract 5 utility modules ← CRITICAL
    ↓
Phase 5: Refactor + Scoring (2h) → Defensive Parsing ← LARGEST PHASE
    ↓
Phase 6: Consumers (0.5h) → Update Imports
    ↓
Phase 7: Testing (1.5h) → Validation ← QUALITY GATE
    ↓
Phase 8: Deprecation (0.5h) → Finalization
```

**Phase 3 (YAML Parser) can run parallel with Phase 4 but is not on critical path.**

**Note:** Phases 4-5 are the highest complexity. Budget extra time for debugging and iteration.

---

## 3. Code Patterns

### 3.1 Abstract Base Class Pattern

**Used in:** `base.py` (SourceParser)

**Pattern:**
```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from ouroboros.subsystems.workflow.models import DynamicPhase

class SourceParser(ABC):
    """Abstract base class for workflow source parsers.
    
    All parsers must implement parse() method that converts
    source file into list of DynamicPhase objects.
    """
    
    @abstractmethod
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """Parse source file into dynamic phases.
        
        Args:
            source_path: Path to source file (must exist and be readable)
            
        Returns:
            List of DynamicPhase objects (at least 1 phase)
            
        Raises:
            ParseError: If file not found, invalid format, or validation fails
        """
        pass
```

**Why This Pattern:**
- Enforces consistent interface across all parsers
- Enables polymorphism (DynamicContentRegistry doesn't care which parser)
- Documents contract in one place
- Python ABC prevents instantiation of base class

**Anti-Pattern:**
```python
# ❌ BAD: No ABC, just regular class
class SourceParser:
    def parse(self, source_path):
        raise NotImplementedError()  # Can be instantiated!
```

---

### 3.2 Pure Function Utilities Pattern

**Used in:** `shared/text.py`, `shared/dependencies.py`, `shared/validation.py`

**Pattern:**
```python
"""Pure utility functions with no side effects."""

def clean_text(text: str) -> str:
    """Remove extra whitespace and normalize separators.
    
    Pure function: Same input always produces same output.
    No side effects: Doesn't modify global state or input.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text with normalized whitespace
        
    Examples:
        >>> clean_text("  hello   world  ")
        "hello world"
    """
    # No self, no state, no mutations
    return " ".join(text.split())


def extract_number(text: str) -> Optional[int]:
    """Extract first number from text.
    
    Args:
        text: Text containing number
        
    Returns:
        First number found, or None if no numbers
        
    Examples:
        >>> extract_number("Phase 2: Implementation")
        2
        >>> extract_number("No numbers here")
        None
    """
    import re
    match = re.search(r'\d+', text)
    return int(match.group()) if match else None
```

**Why This Pattern:**
- Easier to test (no setup, no mocking)
- Easier to reuse (import and call, no instantiation)
- Easier to understand (no hidden state)
- Composable (output of one → input of another)

**Anti-Pattern:**
```python
# ❌ BAD: Utility as class with state
class TextUtility:
    def __init__(self):
        self.cache = {}  # Unnecessary state
    
    def clean_text(self, text):
        if text in self.cache:  # Premature optimization
            return self.cache[text]
        result = self._clean(text)
        self.cache[text] = result
        return result
```

---

### 3.3 Semantic Scoring Pattern

**Used in:** `markdown/scoring.py`

**Pattern:**
```python
from dataclasses import dataclass

@dataclass
class ScoredHeader:
    """Header with confidence scores for classification."""
    text: str
    level: int
    phase_score: float
    task_score: float
    line_number: int


def score_phase_header(text: str, level: int, context: str) -> float:
    """Calculate confidence score for phase header classification.
    
    Multi-signal scoring instead of rigid pattern matching.
    
    Signals:
    - "phase" keyword: +40 points
    - Single number (0-9): +25 points
    - H2 level (##): +15 points
    - Separator (:, -): +10 points
    - Negation "detailed breakdown": -90%
    
    Args:
        text: Header text
        level: Header level (1-6)
        context: Surrounding text (next 100 chars)
        
    Returns:
        Confidence score (0-100+, higher = more confident)
    """
    score = 0.0
    text_lower = text.lower()
    
    # Positive signals
    if "phase" in text_lower:
        score += 40.0
    
    # Extract number: "Phase 2" → 2
    import re
    numbers = re.findall(r'\b(\d+)\b', text)
    if len(numbers) == 1 and int(numbers[0]) < 10:
        score += 25.0  # Single-digit phase number
    
    if level == 2:  # H2 (##)
        score += 15.0
    
    if any(sep in text for sep in [':', '-', '—']):
        score += 10.0
    
    # Negative signals (format drift indicators)
    if "detailed" in text_lower and "breakdown" in text_lower:
        score *= 0.1  # -90% penalty
    
    if "tasks" in text_lower:  # Plural
        score *= 0.7  # -30% penalty
    
    return score
```

**Why This Pattern:**
- Handles format variations (flexible, not brittle)
- Confidence-based (gray area between phase/task)
- Extensible (add new signals without rewriting logic)
- Debuggable (can log score breakdown)

**Anti-Pattern:**
```python
# ❌ BAD: Rigid pattern matching
def is_phase_header(text: str) -> bool:
    return bool(re.match(r'^## Phase \d+:', text))  # Fails on "Phase 0 -" or "## Phase 0"
```

---

### 3.4 Configuration via Constructor Pattern

**Used in:** `markdown/spec_tasks.py`

**Pattern:**
```python
class SpecTasksParser(SourceParser):
    """Parse tasks.md with configurable scoring thresholds."""
    
    def __init__(
        self,
        phase_threshold: float = 30.0,
        task_threshold: float = 30.0
    ):
        """Initialize parser with scoring configuration.
        
        Args:
            phase_threshold: Min confidence to classify as phase (default: 30.0)
            task_threshold: Min confidence to classify as task (default: 30.0)
        """
        self.phase_threshold = phase_threshold
        self.task_threshold = task_threshold
    
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """Parse using configured thresholds."""
        # ... use self.phase_threshold in classification
```

**Usage:**
```python
# Default configuration
parser = SpecTasksParser()

# Custom configuration for edge cases
parser = SpecTasksParser(phase_threshold=25.0, task_threshold=35.0)
```

**Why This Pattern:**
- Flexibility without hardcoding
- Testable with different configurations
- Explicit dependencies (not hidden globals)
- Self-documenting (parameters in signature)

**Anti-Pattern:**
```python
# ❌ BAD: Hardcoded constants
PHASE_THRESHOLD = 30.0  # Global, not configurable

class SpecTasksParser:
    def parse(self, source_path):
        if score >= PHASE_THRESHOLD:  # Can't override per-instance
            ...
```

---

### 3.5 Relative Import Pattern (Submodules)

**Used in:** All parser submodules

**Pattern:**
```python
# In markdown/spec_tasks.py
from ..base import SourceParser, ParseError  # Up one level to base
from .scoring import score_phase_header      # Same level (markdown/)
from .traversal import find_headers           # Same level
from ..shared.dependencies import parse_dependency_references  # Up and over

# In yaml/workflow_definition.py
from ..base import SourceParser, ParseError  # Up one level
from ..shared.validation import validate_phase_sequence  # Up and over
```

**Why This Pattern:**
- Explicit module relationships
- Refactoring-friendly (move files, paths update)
- Prevents circular imports (enforces hierarchy)
- Clear dependency direction

**Anti-Pattern:**
```python
# ❌ BAD: Absolute imports in submodules
from ouroboros.subsystems.workflow.parsers.base import SourceParser
# Breaks if parsers/ moves to different location
```

---

### 3.6 Backward Compatibility Shim Pattern

**Used in:** `task_parser.py` (deprecated file)

**Pattern:**
```python
"""
DEPRECATED: Use ouroboros.subsystems.workflow.parsers instead.

This module is kept for backward compatibility during migration.
Will be removed in version 2.0.

Migration:
    # Old (deprecated)
    from ouroboros.subsystems.workflow.task_parser import SpecTasksParser
    
    # New (recommended)
    from ouroboros.subsystems.workflow.parsers import SpecTasksParser
"""

import warnings

# Re-export from new location
from .parsers import (
    SourceParser,
    ParseError,
    SpecTasksParser,
    WorkflowDefinitionParser,
)

# Emit deprecation warning
warnings.warn(
    "task_parser module is deprecated. "
    "Use 'from parsers import' instead. "
    "This module will be removed in version 2.0.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    "SourceParser",
    "ParseError",
    "SpecTasksParser",
    "WorkflowDefinitionParser",
]
```

**Why This Pattern:**
- Zero breaking changes (old code still works)
- Clear migration path (warning includes guidance)
- Timeline communicated (version 2.0 removal)
- Clean eventual removal (just delete file)

**Anti-Pattern:**
```python
# ❌ BAD: Silent forwarding (users never migrate)
from .parsers import *

# ❌ BAD: Hard break (breaks existing code)
raise ImportError("task_parser is deprecated, use parsers")
```

---

### 3.7 Defensive Parsing Algorithm Pattern

**Used in:** `markdown/spec_tasks.py` main parse() method

**Pattern (7-Phase Algorithm):**
```python
def parse(self, source_path: Path) -> List[DynamicPhase]:
    """Parse tasks.md with defensive 7-phase algorithm.
    
    Algorithm phases:
    1. Score headers (semantic confidence)
    2. Classify headers (phase vs task)
    3. Detect phase shift (Phase 0 → +1)
    4. Validate sequence (error on gaps)
    5. Build structures (associate tasks)
    6. Normalize dependencies (apply shift)
    7. Normalize task IDs (sequential 1-indexed)
    """
    # Validate and load
    if not source_path.exists():
        raise ParseError(f"File not found: {source_path}")
    
    content = source_path.read_text()
    doc = Document(content)  # mistletoe AST
    
    # Phase 1: Score all headers
    scored_headers = self._score_headers(doc, content)
    
    # Phase 2: Classify
    phase_headers, task_headers = self._classify_headers(scored_headers)
    
    # Phase 3: Detect shift
    shift_amount = self._detect_phase_shift(phase_headers)
    
    # Phase 4: Validate sequence
    self._validate_phase_sequence(phase_headers, shift_amount)
    
    # Phase 5: Build structures
    phases = self._build_phase_structures(
        phase_headers, task_headers, content, shift_amount
    )
    
    # Phase 6: Normalize dependencies
    self._normalize_dependencies(phases, shift_amount)
    
    # Phase 7: Normalize task IDs
    self._normalize_task_ids(phases)
    
    if not phases:
        raise ParseError(f"No phases found in {source_path}")
    
    return phases


def _detect_phase_shift(self, phase_headers: List[ScoredHeader]) -> int:
    """Detect if Phase 0 exists and shift needed.
    
    Returns:
        1 if Phase 0 detected (shift needed)
        0 if starts at Phase 1 (no shift)
        
    Raises:
        ParseError if phases don't start at 0 or 1
    """
    phase_numbers = [self._extract_phase_number(ph.text) for ph in phase_headers]
    phase_numbers.sort()
    min_phase = min(phase_numbers)
    
    if min_phase == 0:
        return 1  # Shift +1
    elif min_phase == 1:
        return 0  # No shift
    else:
        raise ParseError(
            f"Phases must start at 0 or 1, found {min_phase}. "
            f"Fix: Renumber phases to start at 0 or 1."
        )
```

**Why This Pattern:**
- Modular (each phase is independent method)
- Sequential (clear execution order)
- Testable (test each phase separately)
- Fail-fast (validation before building)
- Explicit shift handling (no magic)

---

### 3.8 Actionable Error Messages Pattern

**Used in:** All ParseError raises

**Pattern:**
```python
# Format: "{Problem}. Fix: {Remediation guidance}"

# File not found
raise ParseError(
    f"File not found: {source_path}. "
    f"Fix: Check path and ensure file exists."
)

# Phase gaps
missing = [2, 4]
raise ParseError(
    f"Phase sequence has gaps: missing phases {missing}. "
    f"Fix: Add missing phases or renumber sequentially starting from 0 or 1."
)

# Circular dependency
cycle = ["1.2", "2.3", "2.1", "1.2"]
raise ParseError(
    f"Circular dependency detected: {' → '.join(cycle)}. "
    f"Fix: Remove circular reference in dependency chain."
)

# Invalid phase start
raise ParseError(
    f"Phases must start at 0 or 1, found {min_phase}. "
    f"Fix: Renumber phases to start at 0 or 1."
)
```

**Why This Pattern:**
- User knows what went wrong (problem)
- User knows how to fix it (remediation)
- Reduces support requests
- Improves developer experience
- GIGO prevention (don't accept garbage)

**Anti-Pattern:**
```python
# ❌ BAD: Generic error
raise ParseError("Invalid format")  # What's invalid? How to fix?

# ❌ BAD: Technical jargon
raise ParseError("Phase sequence validation failed at index 2")  # Huh?
```

---

## 4. Testing Strategy

### 4.1 Test Organization

**Structure:**
```
tests/
├── unit/                    # Test individual modules
│   ├── test_base.py
│   ├── test_markdown_scoring.py
│   ├── test_markdown_traversal.py
│   ├── test_markdown_extraction.py
│   ├── test_markdown_spec_tasks.py
│   ├── test_yaml_workflow_definition.py
│   ├── test_shared_text.py
│   ├── test_shared_dependencies.py
│   └── test_shared_validation.py
├── integration/             # Test module interactions
│   └── test_parser_integration.py
└── regression/              # Test backward compatibility
    └── test_parser_regression.py
```

### 4.2 Unit Test Pattern (Pure Functions)

**For shared/text.py utilities:**
```python
import pytest
from parsers.shared.text import clean_text, extract_number

class TestCleanText:
    """Test text cleaning utility."""
    
    def test_removes_extra_whitespace(self):
        """Should collapse multiple spaces to single space."""
        assert clean_text("hello    world") == "hello world"
    
    def test_strips_leading_trailing(self):
        """Should remove leading/trailing whitespace."""
        assert clean_text("  hello  ") == "hello"
    
    def test_normalizes_newlines(self):
        """Should replace newlines with spaces."""
        assert clean_text("hello\nworld") == "hello world"
    
    @pytest.mark.parametrize("input,expected", [
        ("", ""),
        ("hello", "hello"),
        ("  multiple   spaces  ", "multiple spaces"),
    ])
    def test_various_inputs(self, input, expected):
        """Should handle edge cases."""
        assert clean_text(input) == expected


class TestExtractNumber:
    """Test number extraction utility."""
    
    def test_extracts_first_number(self):
        """Should extract first number from text."""
        assert extract_number("Phase 2: Implementation") == 2
    
    def test_returns_none_if_no_number(self):
        """Should return None if no numbers found."""
        assert extract_number("No numbers here") is None
    
    def test_multi_digit_numbers(self):
        """Should handle multi-digit numbers."""
        assert extract_number("Phase 123") == 123
```

**Coverage Target:** ≥85% for each module

---

### 4.3 Integration Test Pattern

**For end-to-end parsing:**
```python
from pathlib import Path
import pytest
from parsers import SpecTasksParser

class TestSpecTasksParserIntegration:
    """Integration tests for full parsing flow."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return SpecTasksParser()
    
    @pytest.fixture
    def spec_with_phase_zero(self, tmp_path):
        """Create test spec with Phase 0."""
        spec_file = tmp_path / "tasks.md"
        spec_file.write_text("""
# Test Spec

## Phase 0: Foundation
### Task 0.1: Setup
Dependencies: None

## Phase 1: Implementation
### Task 1.1: Build
Dependencies: Task 0.1
""")
        return spec_file
    
    def test_phase_shift_detection(self, parser, spec_with_phase_zero):
        """Should detect Phase 0 and apply +1 shift."""
        phases = parser.parse(spec_with_phase_zero)
        
        # Phase 0 becomes workflow Phase 1
        assert phases[0].phase_number == 1
        assert len(phases[0].tasks) == 1
        
        # Phase 1 becomes workflow Phase 2
        assert phases[1].phase_number == 2
        assert len(phases[1].tasks) == 1
    
    def test_dependency_normalization(self, parser, spec_with_phase_zero):
        """Should normalize dependencies with shift applied."""
        phases = parser.parse(spec_with_phase_zero)
        
        # Task 1.1 depends on Task 0.1 (in tasks.md)
        # After shift: depends on "1.1" (workflow Phase 1, Task 1)
        task_1_1 = phases[1].tasks[0]  # Workflow Phase 2, Task 1
        assert "1.1" in task_1_1.dependencies  # Shifted from "0.1"
    
    def test_task_id_normalization(self, parser, spec_with_phase_zero):
        """Should normalize task IDs to sequential integers."""
        phases = parser.parse(spec_with_phase_zero)
        
        # Task IDs are just numbers, not "0.1" or "1.1"
        assert phases[0].tasks[0].task_id == "1"
        assert phases[1].tasks[0].task_id == "1"
```

---

### 4.4 Regression Test Pattern

**For backward compatibility:**
```python
from pathlib import Path
import pytest
from parsers import SpecTasksParser

class TestParserRegression:
    """Regression tests on real completed specs."""
    
    @pytest.fixture
    def parser(self):
        return SpecTasksParser()
    
    @pytest.fixture
    def completed_specs(self):
        """Find all completed specs."""
        specs_dir = Path(".praxis-os/specs/completed")
        return list(specs_dir.glob("*/tasks.md"))
    
    def test_all_completed_specs_parse(self, parser, completed_specs):
        """All completed specs should parse without errors."""
        for spec_path in completed_specs:
            try:
                phases = parser.parse(spec_path)
                assert len(phases) > 0, f"No phases found in {spec_path}"
            except Exception as e:
                pytest.fail(f"Failed to parse {spec_path}: {e}")
    
    def test_parsing_is_deterministic(self, parser):
        """Same spec should parse identically multiple times."""
        spec_path = Path(".praxis-os/specs/completed/2025-10-01-example/tasks.md")
        
        result1 = parser.parse(spec_path)
        result2 = parser.parse(spec_path)
        
        # Compare phase counts
        assert len(result1) == len(result2)
        
        # Compare task counts per phase
        for p1, p2 in zip(result1, result2):
            assert len(p1.tasks) == len(p2.tasks)
```

---

### 4.5 Performance Benchmark Pattern

**For performance validation:**
```python
import time
import pytest
from pathlib import Path
from parsers import SpecTasksParser

class TestParserPerformance:
    """Performance benchmarks."""
    
    @pytest.fixture
    def parser(self):
        return SpecTasksParser()
    
    @pytest.mark.benchmark
    def test_typical_spec_parse_speed(self, parser):
        """Typical 40KB spec should parse in <100ms."""
        spec_path = Path("tests/fixtures/typical_40kb_tasks.md")
        
        # Warmup
        parser.parse(spec_path)
        
        # Measure (average of 10 runs)
        start = time.perf_counter()
        for _ in range(10):
            parser.parse(spec_path)
        elapsed = time.perf_counter() - start
        
        avg_ms = (elapsed / 10) * 1000
        assert avg_ms < 100, f"Parse took {avg_ms:.1f}ms (target: <100ms)"
    
    @pytest.mark.benchmark
    def test_memory_usage(self, parser):
        """Should not exceed 50MB peak memory."""
        import tracemalloc
        
        spec_path = Path("tests/fixtures/typical_40kb_tasks.md")
        
        tracemalloc.start()
        parser.parse(spec_path)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        peak_mb = peak / (1024 * 1024)
        assert peak_mb < 50, f"Peak memory {peak_mb:.1f}MB (target: <50MB)"
```

---

## 5. Deployment Guidance

### 5.1 Pre-Deployment Checklist

**Before deploying:**
- [ ] All 8 phases completed
- [ ] All 40 tasks checked off
- [ ] All validation gates passed
- [ ] Test suite passes 100% (unit + integration + regression)
- [ ] Test coverage ≥85%
- [ ] Linter shows zero errors (pylint, flake8)
- [ ] Type checker shows zero errors (mypy --strict)
- [ ] Performance benchmarks within ±5%
- [ ] Git tagged: `parser-refactor-v1.0`

### 5.2 Deployment Steps

**Step 1: Final Validation**
```bash
# Run full test suite
pytest tests/ -v --cov=parsers --cov-report=html

# Check coverage
open htmlcov/index.html  # Should show ≥85%

# Run linter
pylint parsers/
flake8 parsers/

# Run type checker
mypy --strict parsers/
```

**Step 2: Merge to Main**
```bash
git checkout main
git merge parser-refactor-branch
git push origin main
```

**Step 3: Tag Release**
```bash
git tag -a parser-refactor-v1.0 -m "Parser submodule refactor complete"
git push origin parser-refactor-v1.0
```

**Step 4: Monitor**
- Watch for ParseError exceptions in logs
- Monitor parse times (should stay <100ms p95)
- Check deprecation warnings are appearing

### 5.3 Rollback Procedure

**If issues detected:**

```bash
# Revert to baseline
git revert <commit-range>

# Or hard reset (if not pushed)
git reset --hard parser-refactor-baseline
```

**Rollback Triggers:**
- Any regression test failures
- Performance degradation >5%
- Production ParseError spike
- Critical bug in new code

---

## 6. Troubleshooting Guide

### 6.1 Common Issues

**Issue: Import Error**
```
ImportError: cannot import name 'SpecTasksParser' from 'parsers'
```

**Diagnosis:**
- Check `parsers/__init__.py` has `__all__` with SpecTasksParser
- Check `parsers/markdown/__init__.py` exports SpecTasksParser
- Verify file exists: `parsers/markdown/spec_tasks.py`

**Fix:**
```python
# In parsers/__init__.py
from .markdown.spec_tasks import SpecTasksParser

__all__ = ["SpecTasksParser", ...]
```

---

**Issue: Phase Shift Not Applied**
```
ParseError: Phase sequence has gaps: missing phases [1]
```

**Diagnosis:**
- tasks.md starts at Phase 0
- Shift detection failed or not applied
- Check min_phase calculation in `_detect_phase_shift()`

**Fix:**
- Verify phase detection logic extracts correct phase numbers
- Ensure shift_amount is passed to all normalization methods

---

**Issue: Circular Import**
```
ImportError: cannot import name 'X' from partially initialized module
```

**Diagnosis:**
- Two modules importing from each other
- Check import order in `__init__.py` files

**Fix:**
- Use relative imports (..base, not absolute)
- Move shared code to separate module
- Check dependency direction (should be one-way)

---

**Issue: Tests Pass Locally, Fail in CI**
```
FileNotFoundError: tests/fixtures/spec.md
```

**Diagnosis:**
- Fixture files not committed
- Relative path assumptions

**Fix:**
- Use `Path(__file__).parent / "fixtures"` for test files
- Ensure fixtures are tracked in git

---

### 6.2 Debugging Tips

**Enable Debug Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

parser = SpecTasksParser()
parser.parse(spec_path)  # Will log scoring details
```

**Inspect Scored Headers:**
```python
# Add temporary print in _score_headers
for header in scored_headers:
    print(f"{header.text}: phase={header.phase_score:.1f}, task={header.task_score:.1f}")
```

**Test Single Phase:**
```python
# Isolate specific phase extraction logic
def test_debug_phase_detection():
    parser = SpecTasksParser()
    # Set breakpoint here
    import pdb; pdb.set_trace()
    result = parser._detect_phase_shift(phase_headers)
```

---

## 7. Success Metrics

**At Completion:**
- ✅ 11 modules created (from 1 monolithic file)
- ✅ Each module ≤500 lines (maintainability)
- ✅ Zero regressions (100% backward compatible)
- ✅ Performance maintained (±5%)
- ✅ Test coverage ≥85%
- ✅ Extensible architecture (future parsers easy to add)

**Post-Deployment (30 days):**
- ✅ Zero production incidents
- ✅ Developer feedback positive
- ✅ New parser added in ≤4 hours (validation)
- ✅ Deprecation warnings visible but not blocking

---


