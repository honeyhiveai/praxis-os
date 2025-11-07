# Parser Submodule Architecture - Future-Proof Extensibility

**Status:** DRAFT - Pre-Implementation Decision  
**Date:** 2025-11-05  
**Context:** Adding defensive parsing logic would push task_parser.py to ~1500 lines  
**Related Design:** `2025-11-05-defensive-task-parser-with-phase-shift.md`  
**Problem Type:** Tech Debt Prevention / Clean Architecture

---

## Problem Statement

### Current State

**File:** `.praxis-os/ouroboros/subsystems/workflow/task_parser.py`  
**Current Size:** 1,005 lines  
**Projected Size:** ~1,500 lines (after defensive parsing implementation)

**Structure:**
```python
task_parser.py (1,005 lines)
├── ParseError (exception)
├── SourceParser (abstract base)
├── SpecTasksParser (markdown parser, ~700 lines)
│   ├── 19 helper methods
│   ├── AST traversal utilities
│   └── Text extraction helpers
└── WorkflowDefinitionParser (YAML parser, ~150 lines)
    └── 3 helper methods
```

**Issues:**
1. **Monolithic growth:** Adding parsers bloats single file
2. **Code duplication:** Utilities can't be easily reused across parsers
3. **Testing complexity:** 1,500-line file is hard to test comprehensively
4. **No extension points:** Adding Jira/GitHub parsers requires editing core file
5. **Violated SRP:** Single file handles 2+ completely different parsing strategies

### Why This Matters

**Lessons from MCP Server Growth:**
- Started at 5K lines
- Grew organically to 30K lines
- Each "small decision" added tech debt
- Eventually required complete rewrite → Ouroboros

**Current Decision Point:**
- Adding 500 lines of defensive parsing logic
- Perfect moment to architect for extensibility
- Prevent future monolithic parser file (2K+ lines)

### Future Requirements (Known)

**Likely parser additions:**
1. **Jira API Parser** - Parse epics/stories into phases/tasks
2. **GitHub Issues Parser** - Parse project board into workflow
3. **Notion Parser** - Parse Notion database into spec
4. **CSV/Spreadsheet Parser** - Import task lists from spreadsheets
5. **Linear/Asana Parser** - Parse project management tools

**Current architecture can't scale to support 5+ parsers in one file.**

---

## Design Goals

### Primary Goals

1. **Extensibility:** Add new parsers without touching existing code
2. **Maintainability:** Each parser is independently testable and modifiable
3. **Reusability:** Share utilities across parsers without duplication
4. **Clarity:** Clear file-level boundaries with obvious responsibilities

### Non-Goals

1. **Perfect abstraction:** Not building a generic parsing framework
2. **Over-engineering:** Keep it simple, only extract what's needed
3. **Breaking changes:** Maintain backward compatibility with existing imports

---

## Current Architecture Analysis

### Code Distribution

**SpecTasksParser (~700 lines):**
- AST traversal: `_get_text_content`, `_extract_list_item_text` (~150 lines)
- Metadata extraction: `_extract_metadata`, `_extract_task_info` (~100 lines)
- Task parsing: `_parse_single_task`, `_extract_task_dependencies` (~150 lines)
- Phase building: `_build_phase`, `_extract_phases_from_ast` (~200 lines)
- Validation: `_extract_acceptance_criteria`, `_extract_checklist_items` (~100 lines)

**WorkflowDefinitionParser (~150 lines):**
- YAML parsing: `parse`, `_build_dynamic_phase` (~100 lines)
- Validation gate extraction: `_extract_validation_gate` (~50 lines)

### Shared Utilities (Currently Duplicated)

**Text Extraction (~150 lines):**
- `_get_text_content()` - Generic AST traversal
- `_extract_metadata()` - Semantic key-value extraction
- `_extract_checklist_items()` - Markdown checklist parsing

**Dependency Extraction (~50 lines):**
- `_extract_task_dependencies()` - Parse task references

**Validation (~100 lines):**
- `_extract_acceptance_criteria()` - Criteria parsing
- Various validation helpers

### Dependencies

**External:**
- `mistletoe` (AST parsing) - Only used by SpecTasksParser
- `yaml` (YAML parsing) - Only used by WorkflowDefinitionParser
- `re` (regex) - Used by both

**Internal:**
- `ouroboros.subsystems.workflow.models` - DynamicPhase, DynamicTask
- `ouroboros.utils.errors` - ActionableError

---

## Proposed Architecture

### Directory Structure

```
subsystems/workflow/parsers/
├── __init__.py                    # Public API exports
├── base.py                        # Abstract base classes, errors
│
├── markdown/
│   ├── __init__.py               # Markdown parser exports
│   ├── spec_tasks.py             # SpecTasksParser (core logic)
│   ├── scoring.py                # NEW: Semantic scoring for defensive parsing
│   ├── traversal.py              # AST traversal utilities
│   └── extraction.py             # Metadata/text extraction
│
├── yaml/
│   ├── __init__.py               # YAML parser exports
│   └── workflow_definition.py   # WorkflowDefinitionParser
│
└── shared/
    ├── __init__.py               # Shared utilities exports
    ├── text.py                   # Text extraction helpers
    ├── dependencies.py           # Dependency resolution
    └── validation.py             # Validation utilities
```

### File Size Targets

| File | Lines | Purpose |
|------|-------|---------|
| `base.py` | ~50 | Abstract classes, errors |
| `markdown/spec_tasks.py` | ~400 | Core SpecTasksParser logic |
| `markdown/scoring.py` | ~300 | Semantic header scoring (NEW) |
| `markdown/traversal.py` | ~200 | AST traversal utilities |
| `markdown/extraction.py` | ~150 | Metadata extraction |
| `yaml/workflow_definition.py` | ~150 | YAML parser |
| `shared/text.py` | ~100 | Generic text utilities |
| `shared/dependencies.py` | ~100 | Dependency helpers |
| `shared/validation.py` | ~100 | Validation utilities |

**Total:** ~1,550 lines (same as current + new features)  
**Per-file:** 50-400 lines (easily maintainable)

### Module Responsibilities

#### `base.py` - Foundation

```python
"""
Abstract base classes and common errors for workflow parsers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from ouroboros.utils.errors import ActionableError


class ParseError(ActionableError):
    """Raised when source parsing fails."""


class SourceParser(ABC):
    """Abstract parser for dynamic workflow sources."""
    
    @abstractmethod
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """Parse source into DynamicPhase list."""
```

**Purpose:** Shared abstractions, no dependencies on specific formats  
**Dependencies:** Only `ouroboros.utils.errors`, `ouroboros.subsystems.workflow.models`

#### `markdown/spec_tasks.py` - Spec Markdown Parser

```python
"""
Parser for prAxIs OS spec tasks.md files.

Implements defensive semantic scoring to handle format variations
from probabilistic AI systems (spec_creation_v1 workflow).
"""

from pathlib import Path
from typing import List

from mistletoe import Document

from ..base import SourceParser, ParseError
from .scoring import HeaderScorer
from .traversal import ASTTraversal
from .extraction import MetadataExtractor


class SpecTasksParser(SourceParser):
    """
    Defensive parser for spec tasks.md files.
    
    Features:
    - Semantic scoring (not rigid patterns)
    - Phase shift detection (Phase 0 → workflow Phase 1)
    - Gap validation (ensure sequential phases)
    - Cross-phase dependency tracking
    """
    
    def __init__(self):
        self.scorer = HeaderScorer()
        self.traversal = ASTTraversal()
        self.extractor = MetadataExtractor()
    
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """Parse tasks.md using defensive semantic scoring."""
        # Orchestrate scoring → classification → shift → validation
```

**Purpose:** High-level orchestration of markdown parsing  
**Dependencies:** `mistletoe`, local utilities (`scoring`, `traversal`, `extraction`)  
**Lines:** ~400 (core logic, no low-level utilities)

#### `markdown/scoring.py` - Semantic Header Scoring (NEW)

```python
"""
Semantic scoring for markdown headers (phases/tasks).

Implements confidence-based classification instead of rigid patterns.
Handles format variations from probabilistic AI outputs.
"""

from typing import Dict, List, Any


class HeaderScorer:
    """Score headers as phase/task candidates using multiple signals."""
    
    PHASE_THRESHOLD = 30.0
    TASK_THRESHOLD = 30.0
    
    def score_header(self, text: str, level: int) -> Dict[str, float]:
        """
        Score header with phase_score and task_score.
        
        Returns:
            {"phase_score": float, "task_score": float, "numbers": List[int]}
        """
    
    def classify_headers(
        self, 
        scored_headers: List[Dict[str, Any]]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Classify scored headers into phase_headers and task_headers.
        
        Uses thresholds and relative scoring.
        """
    
    def detect_phase_shift(self, phase_headers: List[Dict]) -> int:
        """
        Detect if Phase 0 exists, return shift amount (0 or 1).
        
        Raises ParseError if phases don't start at 0 or 1.
        """
```

**Purpose:** NEW defensive parsing logic (semantic scoring)  
**Dependencies:** None (pure logic)  
**Lines:** ~300

#### `markdown/traversal.py` - AST Utilities

```python
"""
Mistletoe AST traversal utilities.

Provides generic helpers for extracting text, navigating nodes,
and handling markdown-specific structures.
"""

from typing import Any, List
from mistletoe.span_token import LineBreak, RawText, Strong
from mistletoe.block_token import ListItem, Paragraph


class ASTTraversal:
    """Utilities for traversing Mistletoe AST."""
    
    def get_text_content(self, node: Any) -> str:
        """Extract all text from node and children recursively."""
    
    def extract_list_item_text(self, node: ListItem) -> str:
        """Extract text from ListItem with proper structure."""
    
    def get_all_headings(self, doc: Any) -> List[Dict[str, Any]]:
        """Extract all headings with metadata (text, level, line)."""
```

**Purpose:** Generic markdown AST navigation  
**Dependencies:** `mistletoe`  
**Lines:** ~200

#### `markdown/extraction.py` - Metadata Extraction

```python
"""
Metadata extraction from markdown text.

Semantic search for key-value pairs, dependencies, acceptance criteria.
"""

from typing import List, Optional


class MetadataExtractor:
    """Extract structured metadata from free-form markdown text."""
    
    def extract_metadata(self, text: str, labels: List[str]) -> Optional[str]:
        """
        Semantic key-value extraction.
        
        Example: extract_metadata(text, ["duration", "estimated time"])
        Finds: "Estimated Time: 2 hours" → "2 hours"
        """
    
    def extract_task_dependencies(self, text: str) -> List[str]:
        """Extract task IDs from dependency text (e.g., "Task 1.1, Task 1.2")."""
    
    def extract_acceptance_criteria(self, text: str) -> List[str]:
        """Extract checklist items from markdown."""
```

**Purpose:** Text parsing utilities  
**Dependencies:** `re` (regex for patterns)  
**Lines:** ~150

#### `yaml/workflow_definition.py` - YAML Parser

```python
"""
Parser for workflow definition YAML files.

Used by workflow_creation_v1 to parse workflow structure
from YAML definitions into executable phases/tasks.
"""

import yaml
from pathlib import Path
from typing import List

from ..base import SourceParser, ParseError


class WorkflowDefinitionParser(SourceParser):
    """Parse workflow definition YAML into DynamicPhase list."""
    
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """Parse YAML workflow definition."""
```

**Purpose:** YAML-specific parsing  
**Dependencies:** `yaml`  
**Lines:** ~150 (unchanged from current)

#### `shared/text.py` - Generic Text Utils

```python
"""
Generic text processing utilities.

Shared across all parsers for common text operations.
"""

from typing import List, Optional


def extract_first_number(text: str) -> Optional[int]:
    """Extract first number from text using character scanning."""


def extract_all_numbers(text: str) -> List[int]:
    """Extract all numbers from text."""


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
```

**Purpose:** Parser-agnostic text utilities  
**Dependencies:** None  
**Lines:** ~100

#### `shared/dependencies.py` - Dependency Resolution

```python
"""
Task dependency resolution and validation.

Shared logic for parsing, normalizing, and validating
task dependencies across different parser formats.
"""

from typing import List, Dict, Any


def parse_dependency_references(text: str) -> List[str]:
    """Parse task references from text (e.g., "Task 1.1, 2.3")."""


def normalize_dependency(dep: str, shift_amount: int) -> str:
    """Apply phase shift to dependency (e.g., "0.1" → "1.1" with shift=1)."""


def validate_dependencies(
    tasks: List[Dict[str, Any]], 
    allow_cross_phase: bool = True
) -> List[str]:
    """
    Validate all task dependencies exist and are valid.
    
    Returns list of errors (empty if valid).
    """
```

**Purpose:** Dependency logic shared across parsers  
**Dependencies:** None  
**Lines:** ~100

#### `shared/validation.py` - Validation Utils

```python
"""
Validation utilities for parsed workflow data.

Common validation logic for phase sequences, task structures,
and data quality checks.
"""

from typing import List, Dict, Any


def validate_phase_sequence(
    phase_numbers: List[int], 
    shift_amount: int
) -> List[str]:
    """
    Validate phases are sequential with no gaps.
    
    Returns list of errors (empty if valid).
    """


def validate_task_structure(task: Dict[str, Any]) -> List[str]:
    """Validate task has required fields."""
```

**Purpose:** Validation logic shared across parsers  
**Dependencies:** None  
**Lines:** ~100

### Public API (`parsers/__init__.py`)

```python
"""
Workflow parsers for dynamic content sources.

Public API for all parser implementations.
"""

# Base classes
from .base import SourceParser, ParseError

# Concrete parsers
from .markdown.spec_tasks import SpecTasksParser
from .yaml.workflow_definition import WorkflowDefinitionParser

# Future parsers can be added here
# from .jira.api_parser import JiraParser
# from .github.issues_parser import GitHubIssuesParser


__all__ = [
    # Base
    "SourceParser",
    "ParseError",
    # Parsers
    "SpecTasksParser",
    "WorkflowDefinitionParser",
]
```

---

## Migration Strategy

### Phase 1: Create Structure (No Code Changes)

**Action:** Create directory structure with `__init__.py` files

```bash
mkdir -p subsystems/workflow/parsers/{markdown,yaml,shared}
touch subsystems/workflow/parsers/__init__.py
touch subsystems/workflow/parsers/base.py
touch subsystems/workflow/parsers/markdown/{__init__.py,spec_tasks.py,scoring.py,traversal.py,extraction.py}
touch subsystems/workflow/parsers/yaml/{__init__.py,workflow_definition.py}
touch subsystems/workflow/parsers/shared/{__init__.py,text.py,dependencies.py,validation.py}
```

**Risk:** None (no code touched)

### Phase 2: Extract Base Classes

**Action:** Move `SourceParser` and `ParseError` to `base.py`

**Changes:**
- Copy `SourceParser` + `ParseError` from `task_parser.py` → `base.py`
- Add backward-compatible import in `task_parser.py`:
  ```python
  from .parsers.base import SourceParser, ParseError
  ```

**Risk:** Low (maintains imports, adds deprecation warning)

### Phase 3: Extract YAML Parser (Simpler)

**Action:** Move `WorkflowDefinitionParser` to `yaml/workflow_definition.py`

**Changes:**
- Copy entire `WorkflowDefinitionParser` class
- Update imports to use `..base`
- Add backward-compatible import in `task_parser.py`

**Risk:** Low (isolated, simple parser)

### Phase 4: Extract Markdown Utilities

**Action:** Move shared utilities to respective files

**4a. Extract `traversal.py`:**
- Move `_get_text_content`, `_extract_list_item_text`, `_get_checkbox_marker`, `_flush_inline_buffer`

**4b. Extract `extraction.py`:**
- Move `_extract_metadata`, `_extract_task_info`, `_extract_task_dependencies`

**4c. Extract `shared/text.py`:**
- Move `_extract_first_number`, text processing helpers

**Risk:** Medium (many dependencies, careful import management needed)

### Phase 5: Refactor SpecTasksParser

**Action:** Slim down `spec_tasks.py` to use extracted utilities

**Changes:**
- Import utilities from extracted modules
- Replace method calls with utility calls
- Keep only orchestration logic in main class

**Risk:** Medium (main parser refactor)

### Phase 6: Implement New Scoring Logic

**Action:** Add `markdown/scoring.py` with defensive parsing

**Changes:**
- Implement `HeaderScorer` class
- Update `spec_tasks.py` to use scorer
- Add phase shift detection logic

**Risk:** Medium (new functionality, needs testing)

### Phase 7: Update Consumers

**Action:** Update imports in `dynamic_registry.py` and other consumers

**Before:**
```python
from ouroboros.subsystems.workflow.task_parser import SpecTasksParser
```

**After:**
```python
from ouroboros.subsystems.workflow.parsers import SpecTasksParser
```

**Risk:** Low (automated with IDE refactor tools)

### Phase 8: Deprecate Old File

**Action:** Keep `task_parser.py` as deprecated compatibility shim

```python
"""
DEPRECATED: Use ouroboros.subsystems.workflow.parsers instead.

This file is kept for backward compatibility.
Will be removed in future version.
"""

import warnings
from .parsers import *

warnings.warn(
    "task_parser module is deprecated, use parsers submodule",
    DeprecationWarning,
    stacklevel=2
)
```

**Risk:** None (maintains compatibility)

---

## Testing Strategy

### Unit Tests Per Module

**Base (`test_base.py`):**
- ParseError message formatting
- Abstract method enforcement

**Markdown Scoring (`test_markdown_scoring.py`):**
- Header scoring with various formats
- Phase shift detection logic
- Classification thresholds

**Markdown Traversal (`test_markdown_traversal.py`):**
- AST text extraction
- List item handling
- Nested structure parsing

**Markdown Extraction (`test_markdown_extraction.py`):**
- Metadata key-value extraction
- Dependency parsing
- Acceptance criteria extraction

**Markdown SpecTasks (`test_markdown_spec_tasks.py`):**
- End-to-end parsing
- Phase shift integration
- Dependency normalization

**YAML WorkflowDefinition (`test_yaml_workflow_definition.py`):**
- YAML parsing
- Validation gate extraction

**Shared Utilities (`test_shared_*.py`):**
- Text utilities
- Dependency resolution
- Validation logic

### Integration Tests

**Test Cross-Module Integration:**
- SpecTasksParser using all utilities
- End-to-end workflow parsing
- Error propagation across modules

**Test Backward Compatibility:**
- Old imports still work (with warnings)
- No breaking changes to API

### Regression Tests

**Test All Completed Specs:**
```bash
for spec in .praxis-os/specs/completed/*/tasks.md; do
    python -m pytest tests/integration/test_parsers.py::test_spec_parsing["$spec"]
done
```

**Success Criteria:**
- All existing specs parse correctly
- No regressions in phase/task extraction
- May improve parsing for edge cases

---

## Trade-offs and Alternatives

### Alternative 1: Keep Monolithic File

**Pros:**
- Zero migration cost
- All code in one place
- No import complexity

**Cons:**
- File grows to 2K+ lines
- Can't add parsers without touching core file
- Testing becomes harder
- Duplication across parsers

**Verdict:** ❌ Doesn't scale, repeats tech debt pattern

### Alternative 2: Extract Only Scoring Logic

**Pros:**
- Minimal refactor
- Keeps existing structure
- Small win (reduces file to ~1200 lines)

**Cons:**
- Doesn't solve extensibility problem
- Still monolithic core
- Duplication not addressed

**Verdict:** 🤷 Band-aid, not solution

### Alternative 3: Full Submodule (Proposed)

**Pros:**
- Future-proof architecture
- Easy to add parsers
- Clear boundaries
- Reusable utilities
- Follows ouroboros clean architecture goals

**Cons:**
- Higher upfront cost (~2-3 hours)
- More files to navigate
- Import paths change

**Verdict:** ✅ Best long-term investment

### Alternative 4: Plugin System

**Pros:**
- Maximum extensibility
- External parsers possible
- Dynamic loading

**Cons:**
- Over-engineered for current needs
- Complexity not justified
- No requirement for external plugins

**Verdict:** ❌ YAGNI (You Aren't Gonna Need It)

---

## Impact Analysis

### Files Modified

**New:**
- `parsers/__init__.py`
- `parsers/base.py`
- `parsers/markdown/*.py` (5 files)
- `parsers/yaml/*.py` (1 file)
- `parsers/shared/*.py` (3 files)

**Modified:**
- `task_parser.py` (deprecation shim)
- `dynamic_registry.py` (import update)
- `engine.py` (import update, if direct usage)
- Tests (new test files, update imports)

**Total:** ~12 new files, ~4 modified files

### Import Changes

**Before:**
```python
from ouroboros.subsystems.workflow.task_parser import (
    SourceParser,
    SpecTasksParser,
    WorkflowDefinitionParser,
    ParseError,
)
```

**After:**
```python
from ouroboros.subsystems.workflow.parsers import (
    SourceParser,
    SpecTasksParser,
    WorkflowDefinitionParser,
    ParseError,
)
```

**Backward Compatibility:** Old imports work with deprecation warning

### Testing Impact

**New Test Files:**
- `tests/unit/workflow/parsers/test_base.py`
- `tests/unit/workflow/parsers/test_markdown_*.py` (4 files)
- `tests/unit/workflow/parsers/test_yaml_*.py` (1 file)
- `tests/unit/workflow/parsers/test_shared_*.py` (3 files)

**Modified Tests:**
- Update imports in existing workflow tests
- Add regression tests for refactor

**Total:** ~10 new test files

### Performance Impact

**No measurable impact expected:**
- Same code, different files
- Import overhead negligible
- Lazy loading keeps startup fast

---

## Success Criteria

### Functional Requirements

- [ ] All existing specs parse correctly (zero regressions)
- [ ] New defensive parsing works on problematic spec
- [ ] Phase shift detection works correctly
- [ ] Dependency normalization preserves relationships

### Architectural Requirements

- [ ] Each module < 500 lines
- [ ] Clear single responsibility per file
- [ ] No circular dependencies between modules
- [ ] Public API clean and intuitive

### Extensibility Requirements

- [ ] Can add new parser without touching existing code
- [ ] Utilities can be imported independently
- [ ] Test isolation (test one parser without others)

### Documentation Requirements

- [ ] Each module has clear docstring
- [ ] Public API documented
- [ ] Migration guide for consumers
- [ ] Examples of adding new parser

---

## Future Extensions

### Adding a New Parser (Example: Jira)

**Step 1:** Create new submodule

```bash
mkdir subsystems/workflow/parsers/jira
touch subsystems/workflow/parsers/jira/__init__.py
touch subsystems/workflow/parsers/jira/api_parser.py
```

**Step 2:** Implement parser

```python
# parsers/jira/api_parser.py
from ..base import SourceParser
from ..shared.text import extract_first_number
from ..shared.dependencies import parse_dependency_references


class JiraParser(SourceParser):
    """Parse Jira API responses into workflow phases."""
    
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        # Use shared utilities
        # No need to touch existing parsers
```

**Step 3:** Export in `__init__.py`

```python
# parsers/__init__.py
from .jira.api_parser import JiraParser

__all__ = [
    # ... existing ...
    "JiraParser",  # Just add to list
]
```

**Done!** No modification to existing parser code required.

---

## Open Questions

### 1. Should shared utilities be pure functions or classes?

**Option A: Pure functions** (proposed)
```python
# shared/text.py
def extract_first_number(text: str) -> Optional[int]:
    """Pure function."""
```

**Option B: Utility classes**
```python
# shared/text.py
class TextUtils:
    @staticmethod
    def extract_first_number(text: str) -> Optional[int]:
        """Static method."""
```

**Recommendation:** Pure functions (simpler, easier to test)

### 2. Should we extract validation to its own module now?

**Pros:** Clear separation of concerns  
**Cons:** May not have enough code to justify yet

**Recommendation:** Start with `shared/validation.py` even if small, easy to expand

### 3. How to handle parser-specific configuration?

**Example:** Header scoring thresholds, regex patterns

**Option A:** Hardcode in parser classes  
**Option B:** Accept in constructor  
**Option C:** Separate config files

**Recommendation:** Option B (constructor params with sensible defaults)

---

## Timeline Estimate

**Phase 1-2 (Structure + Base):** 30 minutes  
**Phase 3 (YAML Parser):** 30 minutes  
**Phase 4 (Extract Utilities):** 2 hours  
**Phase 5 (Refactor SpecTasksParser):** 1 hour  
**Phase 6 (New Scoring Logic):** 2 hours  
**Phase 7-8 (Update Consumers + Deprecation):** 30 minutes  

**Total:** ~6-7 hours

**Can be done incrementally:**
- Phases 1-5: Refactor existing (4 hours)
- Phase 6: Add new features (2 hours)
- Can split across sessions if needed

---

## Decision

**Awaiting approval to proceed with proposed submodule architecture.**

**Benefits:**
- Prevents 2K+ line monolithic file
- Enables easy parser additions
- Follows ouroboros clean architecture principles
- One-time investment prevents future tech debt

**Risks:**
- 6-7 hour migration effort
- More files to navigate
- Import path changes (mitigated with backward compatibility)

**Alternative:** Keep monolithic file, accept tech debt accumulation

---

## References

- Current file: `.praxis-os/ouroboros/subsystems/workflow/task_parser.py`
- Related design: `2025-11-05-defensive-task-parser-with-phase-shift.md`
- Ouroboros principles: `.praxis-os/workspace/design/2025-11-04-ouroboros-clean-architecture.md`
- Standards: `standards/universal/architecture/`

---

**Next Step:** Decision on whether to proceed with submodule refactor before or after implementing defensive parsing logic.

