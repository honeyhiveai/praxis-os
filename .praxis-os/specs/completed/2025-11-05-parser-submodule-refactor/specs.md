# Technical Specifications

**Project:** Parser Submodule Refactor  
**Date:** 2025-11-05  
**Based on:** srd.md (requirements), supporting design documents

---

## 1. Architecture Overview

### 1.1 Architectural Pattern

**Primary Pattern:** **Modular Plugin Architecture**

The system uses a plugin-like modular architecture where parsers are organized by format type (markdown, YAML) and shared utilities are composed as pure functions. This pattern enables adding new parsers without modifying existing code while maintaining clear module boundaries.

**Pattern Selection Rationale:**
- **Extensibility (FR-001, FR-004):** New parsers can be added as isolated submodules
- **Maintainability (FR-002, NFR-M1):** Each module stays under 500 lines
- **Reusability (FR-005, NFR-E2):** Shared utilities prevent duplication
- **Testability (NFR-T1, NFR-T2):** Independent module testing
- **Low Coupling:** Format-specific parsers don't depend on each other

**Secondary Patterns:**
- **Abstract Base Class (ABC):** `SourceParser` defines parser interface
- **Composition Over Inheritance:** Utilities as standalone functions, not class hierarchies
- **Open/Closed Principle:** Open for extension (new parsers), closed for modification (existing parsers)

---

### 1.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Public API                                  │
│  subsystems/workflow/parsers/__init__.py                        │
│  ├── SpecTasksParser (from .markdown)                           │
│  ├── WorkflowDefinitionParser (from .yaml)                      │
│  ├── SourceParser (ABC, from .base)                             │
│  └── ParseError (from .base)                                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
    ┌───────────────────────┴───────────────────────┐
    │                                               │
┌───▼──────────────────┐  ┌────────────────────┐  ┌▼──────────────┐
│  Format Parsers       │  │  Shared Utilities │  │  Base Classes │
│  (Isolated)           │  │  (Composition)    │  │  (Contracts)  │
├──────────────────────┤  ├───────────────────┤  ├───────────────┤
│ markdown/            │  │ shared/           │  │ base.py       │
│ ├── spec_tasks.py    │  │ ├── text.py      │  │ ├── Source    │
│ │   (400 lines)      │  │ │   (100 lines)  │  │ │   Parser ABC│
│ ├── scoring.py       │  │ ├── dependencies.│  │ └── ParseError│
│ │   (300 lines)      │  │ │   py (100)     │  │     (50 lines)│
│ ├── traversal.py     │  │ └── validation.py│  └───────────────┘
│ │   (200 lines)      │  │     (100 lines)  │
│ └── extraction.py    │  └───────────────────┘
│     (150 lines)      │
│                      │
│ yaml/                │
│ └── workflow_def.py  │
│     (150 lines)      │
└──────────────────────┘

        │                            │                    │
        ▼                            ▼                    ▼
    ┌─────────┐              ┌──────────┐         ┌─────────────┐
    │mistletoe│              │ re/typing│         │  pydantic   │
    │  (AST)  │              │(builtins)│         │(validation) │
    └─────────┘              └──────────┘         └─────────────┘
```

**Key Architectural Principles:**
1. **Clear Boundaries:** Each subpackage (markdown/, yaml/, shared/) has distinct responsibility
2. **One-Way Dependencies:** Parsers → shared utilities (no circular dependencies)
3. **Interface Segregation:** Each parser implements only SourceParser.parse()
4. **Dependency Injection:** Configuration via constructor parameters, not hardcoded

---

### 1.3 Architectural Decisions

#### Decision 1: Submodule Organization by Format Type

**Decision:** Organize parsers by input format (markdown/, yaml/) rather than by functionality or parser name.

**Rationale:**
- **Extensibility (FR-001):** Adding Jira parser → create `jira/` subpackage
- **Technology Isolation:** Markdown parsers use mistletoe, YAML parsers use pyyaml, no cross-contamination
- **Clear Ownership:** Each format has dedicated namespace
- **Future Plugins:** External plugins (Notion, GitHub) follow same pattern

**Alternatives Considered:**
- **By Parser Name:** `spec_tasks/`, `workflow_definition/` → Less scalable (10+ parsers)
- **Flat Structure:** All parsers in `parsers/` → Would recreate monolithic problem
- **By Use Case:** `specs/`, `workflows/` → Less clear for multi-purpose parsers

**Trade-offs:**
- **Pros:** Scales to 10+ parsers, clear technology boundaries, plugin-friendly
- **Cons:** Single-format parsers still need subpackage (extra nesting)

---

#### Decision 2: Shared Utilities as Pure Functions (Not Classes)

**Decision:** Implement shared utilities (text.py, dependencies.py, validation.py) as pure functions, not class hierarchies.

**Rationale:**
- **Simplicity (NFR-M2):** Functions easier to understand than abstract classes
- **Testability (NFR-T1):** Pure functions trivial to unit test
- **Reusability (NFR-E2):** Import and call, no instantiation ceremony
- **Composition:** Mix and match functions as needed

**Alternatives Considered:**
- **Utility Classes:** `TextExtractor`, `DependencyResolver` → More boilerplate
- **Mixins:** Parser mixins with utilities → Tight coupling, multiple inheritance issues
- **Base Parser Class:** Shared logic in base class → Violates composition over inheritance

**Trade-offs:**
- **Pros:** Simple, testable, composable, no state management
- **Cons:** No polymorphism (but not needed for utilities)

---

#### Decision 3: Semantic Scoring for Defensive Parsing

**Decision:** Replace rigid pattern matching with confidence-based semantic scoring using multiple signals.

**Rationale:**
- **Format Tolerance (FR-006):** Handles AI-generated format variations
- **GIGO Prevention (FR-008):** Still validates quality, just more flexible
- **Maintainability:** Add signals without rewriting core logic
- **Debuggability:** Confidence scores provide insight into classification decisions

**Scoring Signals:**
- **Keywords:** "phase" (+40), "task" (+40), "detailed breakdown" (-90%)
- **Structure:** H2 (+15), H3 (+20), dotted number (+30), single number (+25)
- **Context:** Separator (+10), starts with number (+10)

**Alternatives Considered:**
- **Regex Patterns:** Current approach → Fails on variations
- **Machine Learning:** Train classifier → Overkill for this problem
- **Manual Rules:** If-else chains → Hard to maintain, brittle

**Trade-offs:**
- **Pros:** Flexible, maintainable, debuggable, handles variations
- **Cons:** Thresholds need tuning (30.0 for phase/task currently)

---

#### Decision 4: Phase Shift Logic for Workflow Harness Integration

**Decision:** Auto-detect tasks.md Phase 0 and apply +1 shift to align with workflow Phase numbering.

**Rationale:**
- **Workflow Harness Requirement (FR-007):** Phase 0 is static "Spec Analysis"
- **User Convenience:** Spec authors naturally start at Phase 0
- **Automatic:** No manual renumbering required
- **Dependency Preservation:** Dependencies shifted consistently

**Algorithm:**
```python
phase_numbers = extract_all_phase_numbers()
if min(phase_numbers) == 0:
    shift = +1  # tasks.md Phase 0 → workflow Phase 1
elif min(phase_numbers) == 1:
    shift = 0   # No shift needed
else:
    raise ParseError("Phases must start at 0 or 1")
```

**Alternatives Considered:**
- **Manual Renumbering:** Require authors to start at Phase 1 → User friction
- **No Shift:** Use tasks.md numbering directly → Conflicts with static Phase 0
- **Configuration Flag:** Let user choose → Extra complexity

**Trade-offs:**
- **Pros:** Automatic, user-friendly, preserves dependencies
- **Cons:** "Magic" behavior (implicit shift) needs documentation

---

#### Decision 5: Task ID Normalization vs. Dependency Format

**Decision:** Normalize task IDs to simple integers ("1", "2", "3") while preserving dependencies as "phase.task" format ("1.2", "2.3").

**Rationale:**
- **API Compatibility (FR-010):** `get_task(phase, task_number)` expects integer
- **Cross-Phase Dependencies (FR-009, FR-011):** "phase.task" format enables tracking
- **Clarity:** Distinguishable formats for different purposes

**Example:**
```python
# DynamicTask for Phase 2, Task 3:
task_id = "3"              # Just task number (for get_task lookup)
dependencies = ["1.2", "2.1"]  # Phase.task format (cross-phase tracking)
```

**Alternatives Considered:**
- **All "phase.task":** task_id = "2.3" → Redundant with phase context
- **All integers:** dependencies = [2, 1] → Loses phase information
- **String vs. Int:** Use `int` not `str` → Breaks existing API

**Trade-offs:**
- **Pros:** Clear purpose distinction, API compatible, cross-phase tracking
- **Cons:** Two different formats to document

---

#### Decision 6: Backward Compatibility Shim During Migration

**Decision:** Keep `task_parser.py` as compatibility shim with deprecation warnings during 8-phase migration.

**Rationale:**
- **Zero Disruption (FR-003, NFR-C1):** Existing imports continue working
- **Gradual Migration (FR-005):** Deprecation warnings guide users to new imports
- **Rollback Safety (NFR-D1):** Can revert to old file if issues detected
- **Version Strategy:** Remove in next major version (v2.0)

**Shim Implementation:**
```python
# task_parser.py (compatibility shim)
import warnings
from parsers import SpecTasksParser, WorkflowDefinitionParser, ParseError

warnings.warn(
    "Importing from 'task_parser' is deprecated. "
    "Use 'from parsers import SpecTasksParser' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ["SpecTasksParser", "WorkflowDefinitionParser", "ParseError"]
```

**Alternatives Considered:**
- **Hard Break:** Delete old file immediately → Breaks existing code
- **No Deprecation:** Silent forwarding → Users never migrate
- **Dual Implementation:** Maintain both → Tech debt lingers

**Trade-offs:**
- **Pros:** Zero breaking changes, clear migration path, safety net
- **Cons:** Temporary code duplication (50 lines), eventual removal needed

---

### 1.4 Technology Stack

**Language:**
- Python 3.9+ (project minimum version, NFR-C2)

**Core Dependencies (Existing):**
- **mistletoe 1.3+:** Markdown AST parsing (markdown/ subpackage only)
- **pyyaml 6.0+:** YAML parsing (yaml/ subpackage only)
- **pydantic 2.0+:** Data validation (DynamicPhase, DynamicTask models)

**Standard Library:**
- **re:** Regular expressions (pattern matching, text extraction)
- **typing:** Type hints (enforced by mypy, NFR-Q1)
- **dataclasses:** ScoredHeader for semantic scoring
- **pathlib:** File path manipulation

**No New Dependencies (NFR-C3):** Refactor uses existing project dependencies only.

**Development Dependencies:**
- **pytest:** Unit/integration testing (NFR-T1)
- **mypy:** Static type checking (NFR-Q1)
- **black:** Code formatting (line length 100, NFR-Q1)
- **pylint/flake8:** Linting (zero errors enforced, NFR-Q1)

---

### 1.5 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| FR-001 | Submodule plugin architecture | New parsers added as isolated subpackages |
| FR-002 | Module file size limits | Each module ≤500 lines enforced by structure |
| FR-003 | Compatibility shim (task_parser.py) | Deprecation warnings, backward compatible imports |
| FR-004 | SourceParser ABC | All parsers implement parse() interface |
| FR-005 | 8-phase migration strategy | Incremental refactor with rollback checkpoints |
| FR-006 | Semantic scoring (scoring.py) | Multi-signal confidence-based classification |
| FR-007 | Phase shift detection | Auto-detect Phase 0, apply +1 shift |
| FR-008 | Gap validation logic | Sequential phase validation with errors |
| FR-009 | Dependency tracking | "phase.task" format preserves cross-phase refs |
| FR-010 | Task ID normalization | Simple integers for get_task() compatibility |
| FR-011 | Dependency format preservation | List[str] with "phase.task" format |
| NFR-M1 | File size enforcement | Pre-commit hooks validate ≤500 lines |
| NFR-T1 | Test coverage | One test file per module |
| NFR-E1 | Plugin addition effort | Clear pattern, ≤4 hours for new parser |
| NFR-C1 | Backward compatibility | Compatibility shim maintains old imports |
| NFR-SC1 | Scoring thresholds | PHASE_THRESHOLD=30.0, TASK_THRESHOLD=30.0 (configurable) |

---

### 1.6 Deployment Architecture

**Single-Process Refactor:** This is a code organization refactor within the existing Ouroboros MCP server process. No changes to deployment infrastructure required.

**Migration Deployment:**
```
Phase 1-3: Create structure, extract base/YAML
├── Deploy: Compatibility shim active
├── Test: Regression suite on all specs
└── Rollback: Revert commits if issues

Phase 4-5: Extract markdown utilities, refactor SpecTasksParser
├── Deploy: Incremental module extraction
├── Test: Unit tests per module + full regression
└── Rollback: Per-phase commits

Phase 6: Implement defensive scoring
├── Deploy: New scoring logic
├── Test: Validate on problematic specs
└── Rollback: Revert to extracted but non-defensive version

Phase 7-8: Update consumers, deprecate shim
├── Deploy: Update import statements
├── Test: Full system test
└── Complete: Remove shim in v2.0
```

**Zero Downtime (NFR-D2):** Refactor is backward compatible; no service interruption required.

---



## 2. Component Design

This section defines the 11 modules in the parsers submodule with their responsibilities, interfaces, and dependencies.

---

### 2.1 Component: base.py (Abstract Base & Errors)

**Purpose:** Define the SourceParser interface contract and ParseError exception for all parsers.

**Responsibilities:**
- Define abstract `SourceParser` base class with `parse()` method signature
- Provide `ParseError` exception for parser-specific errors
- Establish parser contract: input (Path) → output (List[DynamicPhase])

**Requirements Satisfied:**
- FR-004: Plugin-like parser pattern (ABC defines interface)
- NFR-M2: Clear separation of concerns (base abstractions isolated)

**Public Interface:**
```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from ouroboros.subsystems.workflow.models import DynamicPhase

class ParseError(Exception):
    """Parser-specific error with actionable message."""
    pass

class SourceParser(ABC):
    """Abstract base class for all workflow source parsers."""
    
    @abstractmethod
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """Parse source file into dynamic phases.
        
        Args:
            source_path: Path to source file (tasks.md, metadata.yaml, etc.)
            
        Returns:
            List of DynamicPhase objects with tasks
            
        Raises:
            ParseError: If parsing fails or validation errors occur
        """
        pass
```

**Dependencies:**
- Requires: `DynamicPhase` model from `ouroboros.subsystems.workflow.models`
- Provides: Base interface for all parsers

**File Size:** ~50 lines (exception + ABC + docstrings)

---

### 2.2 Component: markdown/spec_tasks.py (Core SpecTasksParser)

**Purpose:** Orchestrate parsing of tasks.md files using defensive semantic scoring and phase shift logic.

**Responsibilities:**
- Implement `SourceParser.parse()` for markdown tasks.md files
- Execute 7-phase defensive parsing algorithm
- Coordinate calls to scoring, traversal, extraction utilities
- Apply phase shift logic and dependency normalization
- Validate phase sequences and error on quality issues

**Requirements Satisfied:**
- FR-006: Defensive format parsing (semantic scoring)
- FR-007: Phase shift detection (+1 if Phase 0 exists)
- FR-008: Sequential phase validation (error on gaps)
- FR-009: Cross-phase dependencies
- FR-010: Task ID normalization
- FR-011: Dependency format preservation

**Public Interface:**
```python
from pathlib import Path
from typing import List, Optional
from parsers.base import SourceParser, ParseError
from ouroboros.subsystems.workflow.models import DynamicPhase, DynamicTask

class SpecTasksParser(SourceParser):
    """Parse tasks.md files with defensive semantic scoring."""
    
    def __init__(
        self, 
        phase_threshold: float = 30.0,
        task_threshold: float = 30.0
    ):
        """Initialize parser with scoring thresholds.
        
        Args:
            phase_threshold: Minimum confidence to classify as phase header
            task_threshold: Minimum confidence to classify as task header
        """
        self.phase_threshold = phase_threshold
        self.task_threshold = task_threshold
    
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """Parse tasks.md into phases with defensive algorithm.
        
        Algorithm:
        1. Score all headers (confidence-based)
        2. Classify headers as phases or tasks
        3. Detect phase shift (Phase 0 detection)
        4. Validate phase sequence (no gaps)
        5. Build phase structures (associate tasks)
        6. Normalize dependencies (apply shift)
        7. Normalize task IDs (sequential 1-indexed)
        
        Raises:
            ParseError: If file not found, phases invalid, or format unparseable
        """
        # Implementation delegates to utility modules
```

**Internal Methods:**
```python
def _score_headers(self, doc, content: str) -> List[ScoredHeader]:
    """Score all headers using semantic signals."""
    
def _classify_headers(self, scored: List[ScoredHeader]) -> Tuple[List, List]:
    """Separate phase headers from task headers."""
    
def _detect_phase_shift(self, phase_headers: List) -> int:
    """Determine shift amount (0 or 1) based on Phase 0 detection."""
    
def _validate_phase_sequence(self, phases: List, shift: int) -> None:
    """Validate sequential phases, raise ParseError on gaps."""
    
def _build_phase_structures(self, phases, tasks, content, shift) -> List[DynamicPhase]:
    """Associate tasks with phases and build DynamicPhase objects."""
    
def _normalize_dependencies(self, phases: List[DynamicPhase], shift: int) -> None:
    """Apply phase shift to dependency references."""
    
def _normalize_task_ids(self, phases: List[DynamicPhase]) -> None:
    """Convert task IDs to sequential integers (1, 2, 3...)."""
```

**Dependencies:**
- Requires: `scoring.py`, `traversal.py`, `extraction.py` (markdown utilities)
- Requires: `dependencies.py`, `validation.py` (shared utilities)
- Requires: `mistletoe` (AST parsing)
- Provides: tasks.md parsing capability

**File Size:** ~400 lines (orchestration + 7 internal methods)

**Error Handling:**
- File not found → `ParseError("tasks.md not found at {path}")`
- Invalid phase start → `ParseError("Phases must start at 0 or 1, found {min}")`
- Phase gaps → `ParseError("Phase sequence has gaps: missing {missing_phases}")`
- No phases found → `ParseError("No phases found in {path}")`

---

### 2.3 Component: markdown/scoring.py (Semantic Scoring)

**Purpose:** Calculate confidence scores for headers to classify as phase/task using multiple signals.

**Responsibilities:**
- Score headers based on keywords, structure, context
- Apply penalty signals (negation patterns)
- Return confidence scores for classification decisions

**Requirements Satisfied:**
- FR-006: Defensive format parsing (multi-signal scoring)
- NFR-SC1: Scoring thresholds (configurable weights)
- NFR-SC2: Signal weights documented

**Public Interface:**
```python
from dataclasses import dataclass
from typing import List

@dataclass
class ScoredHeader:
    """Header with confidence scores for classification."""
    text: str
    level: int  # 1=H1, 2=H2, 3=H3
    phase_score: float
    task_score: float
    line_number: int

def score_phase_header(text: str, level: int, context: str) -> float:
    """Calculate phase header confidence score.
    
    Signals:
    - "phase" keyword: +40 points
    - Single number (0-9): +25 points
    - H2 level (##): +15 points
    - Separator (:, -): +10 points
    - Negation "detailed breakdown": -90%
    
    Args:
        text: Header text
        level: Header level (1-6)
        context: Surrounding text
        
    Returns:
        Confidence score (0-100+)
    """

def score_task_header(text: str, level: int, context: str) -> float:
    """Calculate task header confidence score.
    
    Signals:
    - "task" keyword: +40 points
    - Dotted number (0.1, 1.2): +30 points
    - H3 level (###): +20 points
    - Starts with number: +10 points
    - Negation "tasks" plural: -30%
    
    Returns:
        Confidence score (0-100+)
    """

def score_all_headers(document, content: str) -> List[ScoredHeader]:
    """Score all headers in document using both phase and task scoring."""
```

**Dependencies:**
- Requires: Standard library (re for regex)
- Provides: Scoring functions for SpecTasksParser

**File Size:** ~300 lines (scoring logic + signal definitions)

---

### 2.4 Component: markdown/traversal.py (AST Traversal)

**Purpose:** Traverse mistletoe AST to extract headers, lists, and content.

**Responsibilities:**
- Navigate mistletoe AST node tree
- Extract text content from nodes
- Find headers and list items
- Preserve line number information

**Requirements Satisfied:**
- NFR-E2: Shared utility reuse (generic AST traversal)

**Public Interface:**
```python
from mistletoe import Document
from typing import List, Optional

def get_text_content(node) -> str:
    """Recursively extract text from AST node.
    
    Args:
        node: Mistletoe AST node
        
    Returns:
        Concatenated text content
    """

def find_headers(document: Document) -> List[tuple]:
    """Find all headers in document.
    
    Returns:
        List of (level, text, line_number) tuples
    """

def extract_list_items(node) -> List[str]:
    """Extract all list items from list node.
    
    Returns:
        List of item text strings
    """

def get_next_sibling(node, parent):
    """Get next sibling node in tree."""

def get_content_between_headers(doc, start_line, end_line) -> str:
    """Extract content between two header line numbers."""
```

**Dependencies:**
- Requires: `mistletoe` (AST library)
- Provides: AST utilities for SpecTasksParser

**File Size:** ~200 lines (traversal algorithms)

---

### 2.5 Component: markdown/extraction.py (Metadata Extraction)

**Purpose:** Extract structured metadata from markdown content (dependencies, acceptance criteria, checklists).

**Responsibilities:**
- Parse task metadata (duration, priority, dependencies)
- Extract acceptance criteria from text
- Parse checklist items
- Extract phase metadata

**Requirements Satisfied:**
- FR-009: Cross-phase dependencies (extraction logic)
- NFR-E2: Shared utility reuse

**Public Interface:**
```python
from typing import List, Dict, Optional

def extract_task_metadata(content: str) -> Dict[str, any]:
    """Extract task metadata from content.
    
    Returns:
        {
            'dependencies': List[str],  # ["1.2", "2.3"]
            'duration': Optional[str],   # "2 hours"
            'priority': Optional[str]    # "High"
        }
    """

def extract_acceptance_criteria(content: str) -> List[str]:
    """Extract acceptance criteria bullet points."""

def extract_checklist_items(content: str) -> List[Dict[str, any]]:
    """Extract checklist items with completion status.
    
    Returns:
        [{'text': '...', 'checked': False}, ...]
    """

def extract_phase_metadata(content: str) -> Dict[str, any]:
    """Extract phase-level metadata (estimated time, objectives)."""
```

**Dependencies:**
- Requires: `re` (regex for pattern extraction)
- Provides: Metadata extraction for SpecTasksParser

**File Size:** ~150 lines (extraction patterns)

---

### 2.6 Component: yaml/workflow_definition.py (WorkflowDefinitionParser)

**Purpose:** Parse workflow metadata.yaml files for workflow definitions.

**Responsibilities:**
- Parse YAML workflow definitions
- Extract validation gates
- Build DynamicPhase objects from YAML structure
- Validate workflow metadata schema

**Requirements Satisfied:**
- FR-001: Extensible parser architecture (YAML parser isolated)
- NFR-M2: Clear separation (YAML logic separate from markdown)

**Public Interface:**
```python
from pathlib import Path
from typing import List
from parsers.base import SourceParser, ParseError
from ouroboros.subsystems.workflow.models import DynamicPhase
import yaml

class WorkflowDefinitionParser(SourceParser):
    """Parse workflow metadata.yaml files."""
    
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """Parse YAML workflow definition.
        
        Raises:
            ParseError: If YAML invalid or required fields missing
        """

def _extract_validation_gate(gate_data: dict) -> Dict:
    """Extract validation gate from YAML structure."""

def _build_dynamic_phase(phase_data: dict, phase_num: int) -> DynamicPhase:
    """Build DynamicPhase from YAML phase definition."""
```

**Dependencies:**
- Requires: `pyyaml` (YAML parsing)
- Requires: `validation.py` (shared validation)
- Provides: YAML parsing capability

**File Size:** ~150 lines (YAML parsing logic)

---

### 2.7 Component: shared/text.py (Text Utilities)

**Purpose:** Generic text processing utilities usable by any parser.

**Responsibilities:**
- Clean and normalize text
- Extract keywords
- Handle special characters
- Text similarity calculations

**Requirements Satisfied:**
- NFR-E2: Shared utility reuse (60% code reuse target)

**Public Interface:**
```python
from typing import List, Optional

def clean_text(text: str) -> str:
    """Remove extra whitespace, normalize separators."""

def extract_keywords(text: str) -> List[str]:
    """Extract meaningful keywords from text."""

def normalize_separator(text: str) -> str:
    """Normalize various separator styles (-, —, :) to standard."""

def strip_formatting(text: str) -> str:
    """Remove markdown formatting (**, __, etc.)."""

def extract_number(text: str) -> Optional[int]:
    """Extract first number from text."""

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity score (0.0-1.0)."""
```

**Dependencies:**
- Requires: `re`, `typing` (standard library)
- Provides: Text utilities for all parsers

**File Size:** ~100 lines (pure functions)

---

### 2.8 Component: shared/dependencies.py (Dependency Resolution)

**Purpose:** Parse and resolve task dependency references.

**Responsibilities:**
- Parse dependency references from text ("Task 1.2", "1.2", etc.)
- Resolve cross-phase dependencies
- Validate dependency targets exist
- Apply phase shift to dependency references

**Requirements Satisfied:**
- FR-009: Cross-phase dependencies (resolution logic)
- FR-011: Dependency format preservation ("phase.task")

**Public Interface:**
```python
from typing import List, Set
import re

def parse_dependency_references(text: str) -> List[str]:
    """Extract dependency references from text.
    
    Patterns:
    - "Task 1.2" → "1.2"
    - "depends on 2.3" → "2.3"
    - "1.2, 1.3" → ["1.2", "1.3"]
    
    Returns:
        List of "phase.task" strings
    """

def validate_dependencies(
    dependencies: List[str],
    available_tasks: Set[str],
    current_phase: int
) -> None:
    """Validate dependencies exist and don't reference future phases.
    
    Raises:
        ValueError: If dependency invalid or creates forward reference
    """

def apply_phase_shift(dependencies: List[str], shift: int) -> List[str]:
    """Apply phase shift to dependency references.
    
    Example: shift=1, ["0.1", "1.2"] → ["1.1", "2.2"]
    """

def detect_circular_dependencies(tasks: List[DynamicTask]) -> Optional[List[str]]:
    """Detect circular dependency chains.
    
    Returns:
        Cycle path if found, None otherwise
    """
```

**Dependencies:**
- Requires: `re`, `typing` (standard library)
- Provides: Dependency utilities for parsers

**File Size:** ~100 lines (parsing + validation logic)

---

### 2.9 Component: shared/validation.py (Validation Utilities)

**Purpose:** Generic validation logic for parsers.

**Responsibilities:**
- Validate phase sequences
- Check required fields present
- Validate data types and constraints
- Generate actionable error messages

**Requirements Satisfied:**
- FR-008: Sequential phase validation
- NFR-R2: Actionable error messages

**Public Interface:**
```python
from typing import List, Optional

def validate_phase_sequence(
    phase_numbers: List[int],
    shift: int = 0
) -> None:
    """Validate phases are sequential without gaps.
    
    After shift, phases must be [1, 2, 3, ..., N].
    
    Raises:
        ValueError: If phases have gaps with missing phase numbers
    """

def validate_required_fields(data: dict, required: List[str]) -> None:
    """Check required fields present in data.
    
    Raises:
        ValueError: With list of missing fields
    """

def validate_task_id_format(task_id: str) -> bool:
    """Validate task ID format (number or phase.task)."""

def generate_error_message(
    error_type: str,
    context: dict
) -> str:
    """Generate actionable error message with remediation guidance."""
```

**Dependencies:**
- Requires: `typing` (standard library)
- Provides: Validation utilities for parsers

**File Size:** ~100 lines (validation functions)

---

### 2.10 Component Interactions

**Parsing Flow (SpecTasksParser):**
```
SpecTasksParser.parse()
    ↓
    1. Read file content
    ↓
    2. Parse AST (mistletoe)
    ↓
    3. score_all_headers() [scoring.py]
       ├─ find_headers() [traversal.py]
       ├─ score_phase_header() [scoring.py]
       └─ score_task_header() [scoring.py]
    ↓
    4. Classify headers (thresholds)
    ↓
    5. Detect phase shift
       └─ validate_phase_sequence() [validation.py]
    ↓
    6. Build phases
       ├─ get_content_between_headers() [traversal.py]
       ├─ extract_task_metadata() [extraction.py]
       └─ parse_dependency_references() [dependencies.py]
    ↓
    7. Normalize
       ├─ apply_phase_shift() [dependencies.py]
       └─ Task ID normalization (internal)
    ↓
    Return List[DynamicPhase]
```

**Component Dependency Matrix:**

| Component | Depends On | Used By |
|-----------|-----------|---------|
| base.py | models.py | All parsers |
| spec_tasks.py | scoring, traversal, extraction, dependencies, validation | DynamicContentRegistry |
| scoring.py | - | spec_tasks.py |
| traversal.py | mistletoe | spec_tasks.py |
| extraction.py | - | spec_tasks.py |
| workflow_definition.py | validation, pyyaml | DynamicContentRegistry |
| text.py | - | All parsers (optional) |
| dependencies.py | - | spec_tasks.py, workflow_definition.py |
| validation.py | - | spec_tasks.py, workflow_definition.py |

---

### 2.11 Module Organization

**Directory Structure:**
```
subsystems/workflow/parsers/
├── __init__.py                    # Public API (exports all parsers)
├── base.py                        # 50 lines
│
├── markdown/
│   ├── __init__.py               # Export SpecTasksParser
│   ├── spec_tasks.py             # 400 lines (orchestration)
│   ├── scoring.py                # 300 lines (semantic scoring)
│   ├── traversal.py              # 200 lines (AST utilities)
│   └── extraction.py             # 150 lines (metadata extraction)
│
├── yaml/
│   ├── __init__.py               # Export WorkflowDefinitionParser
│   └── workflow_definition.py   # 150 lines (YAML parsing)
│
└── shared/
    ├── __init__.py               # Export all utilities
    ├── text.py                   # 100 lines (text processing)
    ├── dependencies.py           # 100 lines (dependency resolution)
    └── validation.py             # 100 lines (validation logic)

Total: 11 files, ~1,550 lines (vs. 1,005 current, ~1,500 projected monolithic)
```

**Import Rules:**
- **No circular imports:** One-way dependency flow
- **Explicit exports:** All `__init__.py` files define `__all__`
- **Public API:** Only `parsers/__init__.py` exports to outside world
- **Internal imports:** Use relative imports within subpackages

**Example Public API (`parsers/__init__.py`):**
```python
"""Parser submodule public API."""

from .base import SourceParser, ParseError
from .markdown.spec_tasks import SpecTasksParser
from .yaml.workflow_definition import WorkflowDefinitionParser

# Utilities available for new parser implementations
from .shared import text, dependencies, validation

__all__ = [
    "SourceParser",
    "ParseError",
    "SpecTasksParser",
    "WorkflowDefinitionParser",
    "text",
    "dependencies",
    "validation",
]
```

---


## 3. API Design

This section defines the public and internal interfaces for the parser submodule. Since this is an internal code refactor, there are no HTTP/REST endpoints—only Python API interfaces.

---

### 3.1 Public API (External Consumers)

The parser submodule exposes a clean public API through `parsers/__init__.py` for external consumers (workflow engine, dynamic registry, etc.).

#### Import Interface

**Usage:**
```python
# Primary imports for consumers
from parsers import SpecTasksParser, WorkflowDefinitionParser, ParseError

# Optional: Import SourceParser ABC for custom parsers
from parsers import SourceParser

# Optional: Import utilities for custom parser implementations
from parsers import text, dependencies, validation
```

**Exported API:**
- `SourceParser` (ABC) - Base class for implementing new parsers
- `ParseError` (Exception) - Parser-specific error with actionable message
- `SpecTasksParser` (class) - Markdown tasks.md parser
- `WorkflowDefinitionParser` (class) - YAML metadata parser
- `text` (module) - Text processing utilities
- `dependencies` (module) - Dependency resolution utilities
- `validation` (module) - Validation logic utilities

**Backward Compatibility (NFR-C1):**
```python
# Old import path (deprecated but supported)
from task_parser import SpecTasksParser, WorkflowDefinitionParser, ParseError
# → Emits DeprecationWarning with migration guidance

# New import path (recommended)
from parsers import SpecTasksParser, WorkflowDefinitionParser, ParseError
```

---

### 3.2 Core Parser Interface (SourceParser ABC)

**Interface Contract:**

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from ouroboros.subsystems.workflow.models import DynamicPhase

class SourceParser(ABC):
    """Abstract base class for all workflow source parsers."""
    
    @abstractmethod
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """Parse source file into dynamic phases.
        
        Contract:
        - Input: Path to source file (must exist and be readable)
        - Output: List of DynamicPhase objects (at least 1 phase)
        - Errors: Raise ParseError with actionable message on failure
        
        Implementers must:
        1. Validate file exists and is readable
        2. Parse content according to format
        3. Return at least one DynamicPhase
        4. Raise ParseError (not generic exceptions) on failure
        5. Include actionable error messages with remediation guidance
        
        Args:
            source_path: Path to source file
            
        Returns:
            List[DynamicPhase]: Parsed phases with tasks
            
        Raises:
            ParseError: File not found, invalid format, validation failure
        """
        pass
```

**Usage Example:**
```python
parser = SpecTasksParser(phase_threshold=30.0, task_threshold=30.0)
try:
    phases = parser.parse(Path(".praxis-os/specs/review/2025-11-04-foo/tasks.md"))
    for phase in phases:
        print(f"Phase {phase.phase_number}: {len(phase.tasks)} tasks")
except ParseError as e:
    print(f"Parse failed: {e}")
    # Error message includes remediation guidance
```

---

### 3.3 SpecTasksParser API

**Constructor:**
```python
def __init__(
    self,
    phase_threshold: float = 30.0,
    task_threshold: float = 30.0
) -> None:
    """Initialize parser with scoring configuration.
    
    Parameters:
        phase_threshold: Minimum confidence score (0-100+) to classify
                        header as phase. Default: 30.0
        task_threshold: Minimum confidence score (0-100+) to classify
                       header as task. Default: 30.0
    
    Raises:
        ValueError: If thresholds < 0 or > 100
    """
```

**Parse Method:**
```python
def parse(self, source_path: Path) -> List[DynamicPhase]:
    """Parse tasks.md file with defensive semantic scoring.
    
    Algorithm:
    1. Load and validate file
    2. Parse markdown AST
    3. Score all headers (phase/task classification)
    4. Detect phase shift (Phase 0 → +1 shift)
    5. Validate phase sequence (error on gaps)
    6. Build phase structures (associate tasks)
    7. Normalize dependencies (apply shift)
    8. Normalize task IDs (sequential 1-indexed)
    
    Parameters:
        source_path: Path to tasks.md file
        
    Returns:
        List[DynamicPhase]: Phases numbered [1, 2, 3, ..., N] after shift
        
    Raises:
        ParseError: File not found
        ParseError: No phases found
        ParseError: Invalid phase start (not 0 or 1)
        ParseError: Phase sequence has gaps
        ParseError: Circular dependencies detected
    """
```

**Configuration:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| phase_threshold | float | 30.0 | Min confidence for phase header |
| task_threshold | float | 30.0 | Min confidence for task header |

---

### 3.4 WorkflowDefinitionParser API

**Constructor:**
```python
def __init__(self) -> None:
    """Initialize YAML parser (no configuration needed)."""
```

**Parse Method:**
```python
def parse(self, source_path: Path) -> List[DynamicPhase]:
    """Parse workflow metadata.yaml file.
    
    Expected YAML Structure:
    ```yaml
    phases:
      - number: 1
        name: "Phase Name"
        tasks:
          - id: "1"
            description: "Task description"
            dependencies: ["0.1"]
    ```
    
    Parameters:
        source_path: Path to metadata.yaml file
        
    Returns:
        List[DynamicPhase]: Parsed phases from YAML
        
    Raises:
        ParseError: File not found
        ParseError: Invalid YAML syntax
        ParseError: Required fields missing (phases, tasks)
        ParseError: Invalid schema
    """
```

---

### 3.5 Utility APIs (For Custom Parser Implementations)

#### scoring.py API

```python
def score_phase_header(text: str, level: int, context: str) -> float:
    """Calculate phase header confidence score.
    
    Returns: 0-100+ score (higher = more confident)
    """

def score_task_header(text: str, level: int, context: str) -> float:
    """Calculate task header confidence score.
    
    Returns: 0-100+ score (higher = more confident)
    """
```

#### dependencies.py API

```python
def parse_dependency_references(text: str) -> List[str]:
    """Extract dependency references from text.
    
    Returns: List of "phase.task" strings (e.g., ["1.2", "2.3"])
    """

def apply_phase_shift(dependencies: List[str], shift: int) -> List[str]:
    """Apply phase shift to dependency references.
    
    Example: shift=1, ["0.1", "1.2"] → ["1.1", "2.2"]
    """

def validate_dependencies(
    dependencies: List[str],
    available_tasks: Set[str],
    current_phase: int
) -> None:
    """Validate dependencies exist and don't reference future phases.
    
    Raises: ValueError with list of invalid dependencies
    """
```

#### validation.py API

```python
def validate_phase_sequence(
    phase_numbers: List[int],
    shift: int = 0
) -> None:
    """Validate phases are sequential without gaps.
    
    Raises: ValueError with list of missing phase numbers
    """

def generate_error_message(
    error_type: str,
    context: dict
) -> str:
    """Generate actionable error message with remediation guidance.
    
    Returns: Error message string with "Fix: ..." guidance
    """
```

---

### 3.6 Data Models (API Contracts)

**Input:** Path objects
```python
from pathlib import Path
source_path = Path(".praxis-os/specs/review/2025-11-04-foo/tasks.md")
```

**Output:** DynamicPhase and DynamicTask models
```python
from pydantic import BaseModel
from typing import List, Optional

class DynamicTask(BaseModel):
    """Task within a dynamic phase."""
    task_id: str              # "1", "2", "3" (normalized to just task number)
    description: str          # Task content
    dependencies: List[str]   # ["1.2", "2.3"] (phase.task format)
    duration: Optional[str]   # "2 hours" (if specified)
    priority: Optional[str]   # "High" (if specified)

class DynamicPhase(BaseModel):
    """Dynamic workflow phase with tasks."""
    phase_number: int         # 1, 2, 3, ... (after shift applied)
    tasks: List[DynamicTask]  # At least 1 task per phase
    
    def get_task(self, task_number: int) -> DynamicTask:
        """Get task by number (1-indexed).
        
        Raises: IndexError if task_number out of range
        """
```

**Error Model:**
```python
class ParseError(Exception):
    """Parser-specific error with actionable message.
    
    Message format: "{Problem}. Fix: {Remediation guidance}"
    
    Examples:
    - "Phase sequence has gaps: missing phases [2, 4]. Fix: Add missing phases or renumber sequentially."
    - "File not found: /path/to/tasks.md. Fix: Check path and ensure file exists."
    """
```

---

### 3.7 Error Handling Contract

**Error Format:**
All parser errors use `ParseError` with actionable messages following this pattern:
```
{Problem description}. Fix: {Remediation guidance}
```

**Error Categories:**

| Error Type | Example | Remediation |
|------------|---------|-------------|
| File Not Found | `tasks.md not found at {path}` | Check path and ensure file exists |
| Invalid Format | `No phases found in {path}` | Add at least one phase header (## Phase N) |
| Phase Sequence | `Phases must start at 0 or 1, found {min}` | Renumber phases to start at 0 or 1 |
| Phase Gaps | `Phase sequence has gaps: missing {nums}` | Add missing phases or renumber sequentially |
| Dependencies | `Invalid dependency {dep}: target not found` | Fix dependency reference or add missing task |
| Circular Deps | `Circular dependency: {cycle}` | Remove circular reference in dependency chain |
| Threshold | `No headers classified (check thresholds)` | Lower thresholds or fix header format |

**Error Handling Example:**
```python
try:
    parser = SpecTasksParser()
    phases = parser.parse(Path("tasks.md"))
except ParseError as e:
    # Error message includes "Fix:" guidance
    print(f"Parse failed: {e}")
    # Log error with context
    logger.error(f"tasks.md parse error: {e}", extra={"path": "tasks.md"})
    # Re-raise or handle gracefully
    raise
```

---

### 3.8 Configuration Interface

**Parser Configuration:**
```python
# SpecTasksParser configuration via constructor
parser = SpecTasksParser(
    phase_threshold=30.0,  # Adjust if headers not detected
    task_threshold=30.0    # Adjust if tasks not detected
)

# WorkflowDefinitionParser has no configuration
parser = WorkflowDefinitionParser()
```

**Global Constants (NFR-SC1):**
```python
# Default scoring thresholds (can be overridden)
DEFAULT_PHASE_THRESHOLD = 30.0
DEFAULT_TASK_THRESHOLD = 30.0

# Signal weights (documented in scoring.py)
PHASE_KEYWORD_WEIGHT = 40
TASK_KEYWORD_WEIGHT = 40
DOTTED_NUMBER_WEIGHT = 30
SINGLE_NUMBER_WEIGHT = 25
# ... (see scoring.py for full signal definitions)
```

---

### 3.9 Integration Points

**Consumer: DynamicContentRegistry**
```python
# Registry uses parsers to load dynamic content
from parsers import SpecTasksParser

class DynamicContentRegistry:
    def __init__(self):
        self.spec_parser = SpecTasksParser()
    
    def load_phases(self, spec_dir: Path) -> List[DynamicPhase]:
        tasks_path = spec_dir / "tasks.md"
        return self.spec_parser.parse(tasks_path)
```

**Consumer: WorkflowEngine**
```python
# Engine retrieves tasks via get_task() interface
phase = dynamic_phases[phase_number - 1]
task = phase.get_task(task_number)  # 1-indexed
```

---

### 3.10 API Summary

**Public Exports:** 7 (2 parsers, 1 ABC, 1 exception, 3 utility modules)

**Parser Methods:** 2 (SpecTasksParser.parse, WorkflowDefinitionParser.parse)

**Utility Functions:** 12 (scoring: 2, dependencies: 4, validation: 2, text: 6, traversal: 5, extraction: 4)

**Configuration Parameters:** 2 (phase_threshold, task_threshold)

**Error Types:** 1 (ParseError with 7 error categories)

**Data Models:** 2 (DynamicPhase, DynamicTask from external models.py)

---


## 4. Data Models

This section defines data structures used by the parser submodule, including external models (Pydantic), internal structures (dataclasses), and input file schemas.

---

### 4.1 External Data Models (Pydantic - Not Modified)

These models are defined in `ouroboros.subsystems.workflow.models` and consumed by the parser. **No changes to these models** in this refactor.

#### DynamicPhase

```python
from pydantic import BaseModel, Field
from typing import List

class DynamicPhase(BaseModel):
    """Dynamic workflow phase with tasks."""
    
    phase_number: int = Field(..., ge=1, description="Phase number (1-indexed)")
    tasks: List['DynamicTask'] = Field(..., min_length=1, description="Tasks in phase")
    
    def get_task(self, task_number: int) -> 'DynamicTask':
        """Get task by number (1-indexed).
        
        Args:
            task_number: Task number (1-indexed, not 0-indexed)
            
        Returns:
            DynamicTask at index (task_number - 1)
            
        Raises:
            IndexError: If task_number out of range
        """
        if task_number < 1 or task_number > len(self.tasks):
            raise IndexError(f"Task {task_number} not found in phase {self.phase_number}")
        return self.tasks[task_number - 1]
```

**Fields:**
- `phase_number`: Integer ≥ 1 (workflow phase number after shift applied)
- `tasks`: List of tasks (minimum 1 task per phase)

**Validation Rules:**
- `phase_number` must be ≥ 1
- `tasks` list cannot be empty
- Pydantic validates types automatically

---

#### DynamicTask

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class DynamicTask(BaseModel):
    """Task within a dynamic phase."""
    
    task_id: str = Field(..., description="Task identifier (normalized to just number)")
    description: str = Field(..., min_length=1, description="Task content")
    dependencies: List[str] = Field(
        default_factory=list,
        description="Dependencies in 'phase.task' format (e.g., ['1.2', '2.3'])"
    )
    duration: Optional[str] = Field(None, description="Estimated duration (e.g., '2 hours')")
    priority: Optional[str] = Field(None, description="Priority level (e.g., 'High')")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria")
    checklist: List[dict] = Field(default_factory=list, description="Checklist items")
```

**Fields:**
- `task_id`: String with just task number ("1", "2", "3") for get_task() compatibility
- `description`: Task content (minimum 1 character)
- `dependencies`: List of "phase.task" strings (["1.2", "2.3"]) for cross-phase tracking
- `duration`: Optional estimated duration string
- `priority`: Optional priority level string
- `acceptance_criteria`: Optional list of criteria
- `checklist`: Optional list of checklist items

**Business Rules:**
- `task_id` must be a simple integer string within a phase
- `dependencies` must use "phase.task" format for cross-phase dependencies
- Dependencies can reference earlier phases only (no forward references)
- Task numbering is sequential within phase (1, 2, 3, ...)

---

### 4.2 Internal Data Structures (New)

These structures are used internally by the parser and not exposed in the public API.

#### ScoredHeader (Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ScoredHeader:
    """Header with confidence scores for phase/task classification."""
    
    text: str              # Header text (e.g., "Phase 1: Foundation")
    level: int             # Header level (1=H1, 2=H2, 3=H3, ...)
    phase_score: float     # Confidence it's a phase header (0-100+)
    task_score: float      # Confidence it's a task header (0-100+)
    line_number: int       # Line number in source file
    
    def is_phase(self, threshold: float) -> bool:
        """Check if phase score exceeds threshold."""
        return self.phase_score >= threshold
    
    def is_task(self, threshold: float) -> bool:
        """Check if task score exceeds threshold."""
        return self.task_score >= threshold
    
    def classify(self, phase_threshold: float, task_threshold: float) -> str:
        """Classify as 'phase', 'task', or 'unknown'."""
        if self.phase_score >= phase_threshold and self.phase_score > self.task_score:
            return 'phase'
        elif self.task_score >= task_threshold:
            return 'task'
        else:
            return 'unknown'
```

**Purpose:** Store header analysis results during semantic scoring phase.

**Fields:**
- `text`: Original header text
- `level`: Markdown header level (1-6)
- `phase_score`: Confidence score for phase classification (0-100+)
- `task_score`: Confidence score for task classification (0-100+)
- `line_number`: Source file line number for error reporting

**Validation:**
- `level` must be 1-6 (valid markdown header levels)
- `phase_score` and `task_score` can exceed 100 (signal accumulation)
- `line_number` must be ≥ 1

---

#### ParserConfig (TypedDict - Optional)

```python
from typing import TypedDict

class ParserConfig(TypedDict, total=False):
    """Configuration for parser behavior."""
    
    phase_threshold: float      # Min score for phase classification (default: 30.0)
    task_threshold: float       # Min score for task classification (default: 30.0)
    strict_mode: bool           # Fail on warnings (default: False)
    debug_scoring: bool         # Log scoring details (default: False)
```

**Purpose:** Optional configuration structure for parser initialization.

**Defaults:**
- `phase_threshold`: 30.0
- `task_threshold`: 30.0
- `strict_mode`: False (warnings don't raise errors)
- `debug_scoring`: False (no verbose scoring logs)

---

### 4.3 Input File Schemas

#### tasks.md Schema (Markdown)

**Expected Structure:**
```markdown
# Spec Title (H1)

## Phase 0: Foundation (H2 - Phase Header)
High-level overview...

### Task 0.1: Setup Environment (H3 - Task Header)
**Dependencies:** None
**Duration:** 30 minutes

Task description with acceptance criteria...

### Task 0.2: Create Configuration (H3)
**Dependencies:** Task 0.1
**Duration:** 1 hour

Task description...

## Phase 1: Implementation (H2)
### Task 1.1: Build Component (H3)
...
```

**Semantic Patterns (Flexible):**

Phase Headers:
- Must contain "phase" keyword (case-insensitive) OR
- Must be H2 (##) with single number (0-9) OR
- Must match pattern: `## Phase {N}: {Title}`

Task Headers:
- Must contain "task" keyword (case-insensitive) OR
- Must be H3 (###) with dotted number (N.M) OR
- Must match pattern: `### Task {N}.{M}: {Title}`

**Metadata Patterns:**
- Dependencies: `**Dependencies:**` followed by task references
- Duration: `**Duration:**` followed by time string
- Priority: `**Priority:**` followed by level (High/Medium/Low)

**Validation Rules:**
- At least one phase must exist
- Phases must start at 0 or 1
- Phase numbers must be sequential (no gaps)
- Task numbers can have gaps (flexible)
- Dependencies must reference existing tasks
- No forward dependencies (phase N can't depend on phase M where M > N)

---

#### metadata.yaml Schema (YAML)

**Expected Structure:**
```yaml
workflow_type: spec_execution_v1
dynamic_phases: true

phases:
  - number: 1
    name: "Phase Name"
    description: "Phase description"
    estimated_time: "2 hours"
    tasks:
      - id: "1"
        description: "Task description"
        dependencies: []
        acceptance_criteria:
          - "Criterion 1"
          - "Criterion 2"
      - id: "2"
        description: "Another task"
        dependencies: ["1"]
        
  - number: 2
    name: "Second Phase"
    tasks:
      - id: "1"
        description: "Task in phase 2"
        dependencies: ["1.2"]  # Cross-phase dependency
```

**Required Fields:**
- `phases` (array): At least one phase
- `phases[].number` (int): Phase number (1-indexed)
- `phases[].tasks` (array): At least one task per phase
- `phases[].tasks[].id` (string): Task ID (unique within phase)
- `phases[].tasks[].description` (string): Task description

**Optional Fields:**
- `phases[].name` (string): Phase name
- `phases[].description` (string): Phase description
- `phases[].estimated_time` (string): Time estimate
- `phases[].tasks[].dependencies` (array): Dependency list
- `phases[].tasks[].acceptance_criteria` (array): Criteria list
- `phases[].tasks[].duration` (string): Task duration
- `phases[].tasks[].priority` (string): Task priority

**Validation Rules:**
- Valid YAML syntax
- Required fields present
- Phase numbers sequential
- Task IDs unique within phase
- Dependencies reference valid tasks

---

### 4.4 Output Data Model

**Parser Output:**
```python
# Both parsers return this structure
result: List[DynamicPhase] = parser.parse(source_path)

# Structure:
# [
#   DynamicPhase(
#     phase_number=1,
#     tasks=[
#       DynamicTask(
#         task_id="1",
#         description="...",
#         dependencies=["0.1"],  # phase.task format
#         duration="2 hours",
#         priority="High",
#         acceptance_criteria=[...],
#         checklist=[...]
#       ),
#       DynamicTask(task_id="2", ...),
#     ]
#   ),
#   DynamicPhase(phase_number=2, tasks=[...]),
# ]
```

**Guarantees:**
- `phase_number` is sequential [1, 2, 3, ..., N] (no gaps)
- `task_id` is normalized to just task number within phase
- `dependencies` preserve "phase.task" format with shift applied
- At least one phase with at least one task

---

### 4.5 Error Context Structures

**ParseError Context (Embedded in Exception Message):**
```python
{
    "error_type": str,      # "file_not_found", "phase_gap", "invalid_dependency", etc.
    "file_path": str,       # Source file path
    "line_number": int,     # Optional: line where error occurred
    "details": dict,        # Error-specific context
    "remediation": str      # Fix guidance
}
```

**Example Error Messages:**
```python
ParseError(
    "File not found: /path/to/tasks.md. "
    "Fix: Check path and ensure file exists."
)

ParseError(
    "Phase sequence has gaps: missing phases [2, 4]. "
    "Fix: Add missing phases or renumber sequentially starting from 0 or 1."
)

ParseError(
    "Invalid dependency '3.1': task not found. "
    "Fix: Ensure dependency references an existing task or remove the reference."
)
```

---

### 4.6 Data Transformation Flow

**Input → Parser → Output:**

```
tasks.md (Markdown)
    ↓ [read file]
Content (str)
    ↓ [parse AST]
Document (mistletoe)
    ↓ [score headers]
List[ScoredHeader]
    ↓ [classify]
phase_headers: List[ScoredHeader]
task_headers: List[ScoredHeader]
    ↓ [detect shift]
shift: int (0 or 1)
    ↓ [validate sequence]
[raises ParseError if gaps]
    ↓ [build phases]
phases_raw: List[dict]
    ↓ [normalize]
phases_normalized: List[dict]
    ↓ [construct models]
List[DynamicPhase]  ← OUTPUT
```

**Data Transformations:**
1. **Markdown → AST:** mistletoe parses to node tree
2. **AST → ScoredHeaders:** Scoring algorithm evaluates headers
3. **ScoredHeaders → Classification:** Threshold comparison
4. **Phase Numbers → Shifted:** Apply +1 if Phase 0 detected
5. **Task IDs → Normalized:** "0.1" → "1" (just task number)
6. **Dependencies → Shifted:** "0.1" → "1.1" (preserve phase.task format)
7. **Dict → Pydantic:** Construct DynamicPhase/DynamicTask models

---

### 4.7 Validation Rules Summary

**Phase Validation:**
- Phase numbers must start at 0 or 1 (error if min > 1)
- After shift, phases must be [1, 2, 3, ..., N] sequential
- No gaps allowed (e.g., [1, 2, 4] → error, missing 3)
- At least 1 phase required

**Task Validation:**
- Task IDs unique within phase (normalized to 1, 2, 3...)
- Dependencies use "phase.task" format (e.g., "1.2")
- No forward references (can't depend on later phase)
- No self-references (task can't depend on itself)
- Circular dependencies detected and rejected

**Content Validation:**
- File must exist and be readable
- Markdown must parse (valid AST)
- At least one header classified as phase
- At least one header classified as task (per phase)
- Confidence scores meet thresholds

---

### 4.8 Data Model Summary

**External Models:** 2 (DynamicPhase, DynamicTask from models.py - not modified)

**Internal Structures:** 2 (ScoredHeader dataclass, ParserConfig TypedDict)

**Input Schemas:** 2 (tasks.md markdown structure, metadata.yaml schema)

**Output Structure:** List[DynamicPhase] (uniform across all parsers)

**Validation Rules:** 15+ (phase sequence, task IDs, dependencies, content)

**Transformations:** 7 steps (markdown → AST → scoring → classification → normalization → models)

---


## 5. Security Design

This section addresses security considerations for the parser submodule. Since this is **internal tooling** (not exposed to untrusted external users), security focuses on defensive programming, safe file handling, and preventing resource exhaustion.

---

### 5.1 Threat Model

**Trust Boundary:**
- **Trusted:** Spec files created by authenticated developers or AI workflows
- **Untrusted:** None (internal tool, no external user input)
- **Attack Surface:** File system access, markdown/YAML parsing, regular expressions

**Threat Scenarios:**
1. **Malicious Markdown:** Crafted markdown causing parser DoS (huge files, deep nesting)
2. **Path Traversal:** Attempts to read files outside workspace
3. **Regex DoS:** Complex patterns causing excessive backtracking
4. **Resource Exhaustion:** Large files consuming excessive memory/CPU
5. **Information Disclosure:** Error messages leaking sensitive paths
6. **Dependency Vulnerabilities:** Security issues in mistletoe/pyyaml

**Risk Level:** **LOW**
- Internal tool with trusted inputs
- No network exposure
- No credential handling
- Limited blast radius (parser errors don't affect other systems)

---

### 5.2 Input Validation

#### File Path Validation

**Control:** Validate source_path before reading to prevent path traversal.

```python
def validate_source_path(source_path: Path, workspace_root: Path) -> None:
    """Validate source path is within workspace.
    
    Prevents:
    - Path traversal (../ attacks)
    - Absolute paths outside workspace
    - Symlink attacks
    
    Raises:
        ValueError: If path invalid or outside workspace
    """
    # Resolve to absolute path
    resolved = source_path.resolve()
    workspace = workspace_root.resolve()
    
    # Check within workspace
    if not str(resolved).startswith(str(workspace)):
        raise ValueError(
            f"Path {source_path} is outside workspace {workspace_root}. "
            "Fix: Ensure source file is within project directory."
        )
    
    # Check file (not directory)
    if resolved.is_dir():
        raise ValueError(f"Path {source_path} is a directory, expected file.")
```

**Implementation Location:** `shared/validation.py`

**Usage:**
```python
# In SpecTasksParser.parse()
validate_source_path(source_path, workspace_root=Path.cwd())
```

---

#### Content Size Limits

**Control:** Enforce maximum file size to prevent resource exhaustion.

```python
MAX_FILE_SIZE_MB = 10  # 10MB limit for spec files
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

def check_file_size(source_path: Path, max_size: int = MAX_FILE_SIZE_BYTES) -> None:
    """Check file size within limits.
    
    Prevents:
    - Memory exhaustion from huge files
    - DoS via oversized specs
    
    Raises:
        ValueError: If file exceeds size limit
    """
    size = source_path.stat().st_size
    if size > max_size:
        size_mb = size / (1024 * 1024)
        max_mb = max_size / (1024 * 1024)
        raise ValueError(
            f"File {source_path} too large ({size_mb:.1f}MB > {max_mb:.1f}MB). "
            "Fix: Split spec into multiple files or reduce content."
        )
```

**Rationale:**
- Typical tasks.md files: 10-100KB
- Large specs: 500KB - 2MB
- 10MB limit provides ample headroom while preventing abuse

---

#### Markdown AST Depth Limits

**Control:** mistletoe AST parsing has implicit depth limits (Python recursion limit).

**Current:** Python default recursion limit (~1000) sufficient for markdown depth.

**Additional Safety:**
```python
import sys

# In parser __init__ or module level
MAX_RECURSION_DEPTH = 500  # Lower than Python default for safety

def traverse_with_depth_limit(node, depth=0, max_depth=MAX_RECURSION_DEPTH):
    """Traverse AST with depth limit.
    
    Prevents:
    - Stack overflow from deeply nested markdown
    - DoS via recursive structures
    """
    if depth > max_depth:
        raise RecursionError(
            f"Markdown nesting exceeds {max_depth} levels. "
            "Fix: Reduce header/list nesting depth."
        )
    # ... traversal logic with depth+1 for children
```

**Implementation:** Optional safety check in `traversal.py`

---

### 5.3 Regular Expression Safety

**Control:** Use non-backtracking regex patterns to prevent ReDoS attacks.

**Vulnerable Pattern (Example):**
```python
# BAD: Catastrophic backtracking possible
r"(a+)+" 
```

**Safe Pattern (Example):**
```python
# GOOD: No nested quantifiers
r"a+"
```

**Review Checklist:**
- ✅ No nested quantifiers (`(a+)+`, `(a*)*`)
- ✅ No overlapping alternatives (`(a|ab)+`)
- ✅ Use possessive quantifiers or atomic groups when needed
- ✅ Test regex performance on worst-case inputs

**Implementation:** All regex patterns in `dependencies.py`, `extraction.py` reviewed for safety.

---

### 5.4 Dependency Security

**Control:** Use only trusted, actively maintained dependencies with no known vulnerabilities.

**Current Dependencies:**
- **mistletoe 1.3+:** Markdown parser (actively maintained, no known CVEs)
- **pyyaml 6.0+:** YAML parser (actively maintained, safe_load used)
- **pydantic 2.0+:** Data validation (actively maintained, no known CVEs)

**Security Practices:**
1. **Use safe_load() for YAML:** Never use yaml.load() (arbitrary code execution)
   ```python
   # In WorkflowDefinitionParser
   with open(source_path) as f:
       data = yaml.safe_load(f)  # ✅ Safe
       # data = yaml.load(f)     # ❌ UNSAFE - never use
   ```

2. **Pin dependency versions:** Specify minimum versions in `requirements.txt`
   ```
   mistletoe>=1.3.0,<2.0.0
   pyyaml>=6.0,<7.0
   pydantic>=2.0,<3.0
   ```

3. **Monitor for vulnerabilities:** Use tools like `pip-audit` or `safety`
   ```bash
   pip-audit  # Check for known vulnerabilities
   ```

4. **No new dependencies (NFR-C3):** This refactor introduces zero new external dependencies.

---

### 5.5 Error Message Safety

**Control:** Error messages must not leak sensitive information (credentials, internal paths, user data).

**Safe Error Messages:**
```python
# ✅ SAFE: Relative path, actionable guidance
ParseError(
    "File not found: specs/review/2025-11-04-foo/tasks.md. "
    "Fix: Check path and ensure file exists."
)

# ✅ SAFE: No sensitive info
ParseError(
    "Phase sequence has gaps: missing phases [2, 4]. "
    "Fix: Add missing phases or renumber sequentially."
)
```

**Unsafe Error Messages (Avoid):**
```python
# ❌ UNSAFE: Leaks absolute path
ParseError(
    "File not found: /Users/developer/projects/client-secret-repo/tasks.md"
)

# ❌ UNSAFE: Leaks internal implementation details
ParseError(
    "SQL query failed: SELECT * FROM users WHERE api_key = '...'"
)
```

**Implementation Guidelines:**
1. Use relative paths in error messages (relative to workspace root)
2. No stack traces in production error messages (log separately)
3. No credentials, tokens, or secrets in error messages
4. Sanitize file content snippets in error messages (truncate, no PII)

---

### 5.6 Resource Limits

**Control:** Prevent resource exhaustion from malicious or malformed inputs.

| Resource | Limit | Rationale |
|----------|-------|-----------|
| File Size | 10MB | Typical specs <100KB, 10MB provides headroom |
| Parse Time | 30 seconds | Typical parse <1 second, 30s prevents DoS |
| Memory | 100MB per parse | Typical <5MB, 100MB prevents memory exhaustion |
| Header Count | 10,000 | Typical <100 headers, 10K prevents DoS |
| Task Count | 5,000 per phase | Typical <50 tasks, 5K prevents DoS |

**Implementation:**
```python
import signal

def parse_with_timeout(parser, source_path, timeout_seconds=30):
    """Parse with timeout to prevent infinite loops.
    
    Raises:
        TimeoutError: If parsing exceeds timeout
    """
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Parsing {source_path} exceeded {timeout_seconds}s timeout")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        result = parser.parse(source_path)
    finally:
        signal.alarm(0)  # Cancel alarm
    
    return result
```

**Note:** Timeouts primarily for defense in depth; expected parse times <1 second.

---

### 5.7 Circular Dependency Detection

**Control:** Detect and reject circular task dependencies to prevent infinite loops.

**Algorithm:**
```python
def detect_circular_dependencies(tasks: List[DynamicTask]) -> Optional[List[str]]:
    """Detect circular dependency chains using DFS.
    
    Returns:
        List of task IDs in cycle if found, None otherwise
    """
    # Build dependency graph
    graph = {task.task_id: task.dependencies for task in tasks}
    
    visited = set()
    rec_stack = []
    
    def dfs(task_id: str) -> Optional[List[str]]:
        if task_id in rec_stack:
            # Cycle found: return cycle path
            cycle_start = rec_stack.index(task_id)
            return rec_stack[cycle_start:] + [task_id]
        
        if task_id in visited:
            return None
        
        visited.add(task_id)
        rec_stack.append(task_id)
        
        for dep in graph.get(task_id, []):
            cycle = dfs(dep)
            if cycle:
                return cycle
        
        rec_stack.pop()
        return None
    
    for task_id in graph:
        cycle = dfs(task_id)
        if cycle:
            return cycle
    
    return None
```

**Implementation Location:** `shared/dependencies.py`

**Error Handling:**
```python
cycle = detect_circular_dependencies(tasks)
if cycle:
    cycle_str = " → ".join(cycle)
    raise ParseError(
        f"Circular dependency detected: {cycle_str}. "
        "Fix: Remove circular reference in dependency chain."
    )
```

---

### 5.8 Audit Logging (Optional)

**Control:** Log parser operations for debugging and security auditing.

**Not Required for Initial Implementation:** Since this is internal tooling with trusted inputs, comprehensive audit logging is not a critical requirement. However, basic operational logging is recommended:

```python
import logging

logger = logging.getLogger(__name__)

def parse(self, source_path: Path) -> List[DynamicPhase]:
    """Parse with basic operational logging."""
    logger.info(f"Parsing {source_path}")
    
    try:
        phases = self._parse_internal(source_path)
        logger.info(
            f"Successfully parsed {source_path}: "
            f"{len(phases)} phases, "
            f"{sum(len(p.tasks) for p in phases)} tasks"
        )
        return phases
    
    except ParseError as e:
        logger.error(
            f"Parse failed for {source_path}: {e}",
            extra={"source_path": str(source_path)}
        )
        raise
```

**Log Levels:**
- INFO: Successful parse operations
- WARNING: Deprecated API usage
- ERROR: Parse failures with actionable errors
- DEBUG: Scoring details (if debug_scoring enabled)

**Log Sanitization:**
- Do NOT log file content (may contain sensitive info)
- Log relative paths only (not absolute)
- Log metadata (file size, phase count) is safe

---

### 5.9 Security Testing

**Testing Requirements:**

1. **Path Traversal Tests:**
   ```python
   def test_path_traversal_blocked():
       parser = SpecTasksParser()
       with pytest.raises(ValueError, match="outside workspace"):
           parser.parse(Path("../../../etc/passwd"))
   ```

2. **File Size Limit Tests:**
   ```python
   def test_oversized_file_rejected():
       # Create 11MB file
       with pytest.raises(ValueError, match="too large"):
           parser.parse(oversized_file_path)
   ```

3. **Circular Dependency Tests:**
   ```python
   def test_circular_dependency_detected():
       # tasks.md with A → B → C → A
       with pytest.raises(ParseError, match="Circular dependency"):
           parser.parse(circular_tasks_path)
   ```

4. **ReDoS Tests:**
   ```python
   def test_regex_performance():
       # Worst-case input for dependency regex
       malicious_text = "Task " + "a" * 10000
       # Should complete in <1 second
       result = parse_dependency_references(malicious_text)
   ```

---

### 5.10 Security Review Checklist

Before deployment, verify:

- [ ] ✅ File path validation prevents traversal
- [ ] ✅ File size limits enforced (10MB)
- [ ] ✅ YAML parser uses safe_load() (not load())
- [ ] ✅ No new external dependencies introduced
- [ ] ✅ Regex patterns reviewed for ReDoS vulnerabilities
- [ ] ✅ Error messages don't leak sensitive information
- [ ] ✅ Circular dependency detection implemented
- [ ] ✅ Timeout protection for long-running parses
- [ ] ✅ Security tests cover threat scenarios
- [ ] ✅ Dependency versions pinned and audited

---

### 5.11 Security Summary

**Security Posture:** **LOW RISK**
- Internal tool with trusted inputs
- No authentication/authorization required (file system access controls suffice)
- No network exposure
- No credential or PII handling
- Limited blast radius (parser failures don't affect other systems)

**Key Controls Implemented:**
1. Input validation (path, size, depth)
2. Safe dependency usage (safe_load, pinned versions)
3. Resource limits (file size, parse time, memory)
4. Error message safety (no sensitive info leaks)
5. Circular dependency detection
6. Regex DoS prevention

**Not Required:**
- Authentication/authorization (file system ACLs sufficient)
- Encryption at rest/in transit (internal tool, no PII)
- RBAC (single-user context)
- Security monitoring (basic operational logging sufficient)

**Future Considerations:**
- If parsers exposed via API: Add authentication, rate limiting
- If parsing untrusted user input: Sandbox parsing, stricter validation
- If handling PII: Add data classification, encryption

---


## 6. Performance Design

This section defines performance targets, optimization strategies, and monitoring for the parser submodule. Since this is an internal code refactor (not a web service), performance focuses on parse speed, memory efficiency, and algorithm complexity.

---

### 6.1 Performance Targets (from NFRs)

**NFR-P1: Parsing Speed**
- **Target:** ≤100ms for files up to 50KB (p95)
- **Baseline:** Current parser handles 40KB file in ~80ms
- **Acceptance:** ±5% variance from current implementation (76ms - 84ms acceptable)

**NFR-P2: Memory Efficiency**
- **Target:** ≤50MB peak memory per parse operation
- **Baseline:** Current parser uses ~3-5MB for typical specs
- **Acceptance:** No memory leaks (verified by long-running test suite)

**Typical Workload:**
- File sizes: 10KB - 100KB (typical: 20-40KB)
- Header count: 10-100 headers (typical: 30-50)
- Task count: 10-100 tasks (typical: 20-40)
- Parse frequency: On-demand (workflow start, not frequent)

---

### 6.2 Algorithm Complexity

**Target Complexity:** O(n) where n = file size or header count

**Current Algorithm Analysis:**

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| File read | O(n) | n = file size, unavoidable |
| AST parse (mistletoe) | O(n) | n = file size, library-dependent |
| Header scoring | O(h) | h = header count, linear scan |
| Classification | O(h) | h = header count, threshold comparison |
| Phase shift detection | O(p) | p = phase count, find min |
| Sequence validation | O(p) | p = phase count, gap detection |
| Task association | O(h + t) | h = headers, t = tasks, proximity matching |
| Dependency normalization | O(t * d) | t = tasks, d = avg dependencies per task |
| Circular detection | O(t + e) | t = tasks, e = edges, DFS |

**Total Complexity:** O(n + h + t) ≈ **O(n)** (linear in file size)

**Optimization Notes:**
- No nested loops over large data structures
- No backtracking or exponential search
- Single-pass algorithms where possible
- Early termination on errors

---

### 6.3 Optimization Strategies

#### 6.3.1 Parsing Optimization

**Strategy:** Minimize AST traversals

```python
# ✅ GOOD: Single traversal to collect all headers
headers = find_all_headers(document)  # One pass
for header in headers:
    score_header(header)  # O(h) total

# ❌ BAD: Multiple traversals
for potential_phase in document:
    if is_phase(potential_phase):  # Traverses entire doc per phase
        ...
```

**Implementation:**
- `traversal.py` provides single-pass header collection
- Scoring done in batch, not per-header document scan
- Content extraction between headers uses line numbers (no repeated traversal)

---

#### 6.3.2 Memory Optimization

**Strategy:** Avoid storing entire file content in multiple representations

```python
# ✅ GOOD: Read once, reference by line numbers
content = source_path.read_text()  # Load once
doc = Document(content)             # AST shares string data
# Extract metadata using content[start:end] slicing

# ❌ BAD: Duplicate storage
content = source_path.read_text()
doc = Document(content)
processed = preprocess(content)      # Duplicate
normalized = normalize(processed)    # Another duplicate
```

**Implementation:**
- Single file read
- AST shares underlying string data
- Content extraction uses slicing (no copies)
- Intermediate ScoredHeader objects are lightweight (~100 bytes each)

---

#### 6.3.3 Lazy Evaluation

**Strategy:** Compute expensive operations only when needed

**Not Applicable:** All parsing must complete before returning DynamicPhase list. No opportunity for lazy evaluation since:
- Workflow engine needs complete phase list upfront
- Phase sequence validation requires all phases
- Dependency resolution requires all tasks

**Future Consideration:** If streaming/incremental parsing needed (not current requirement).

---

### 6.4 Performance Benchmarking

**Benchmark Suite:** Measure parsing performance across representative workloads.

#### 6.4.1 Benchmark Cases

| Case | File Size | Headers | Tasks | Description |
|------|-----------|---------|-------|-------------|
| Small | 5KB | 10 | 5 | Minimal spec |
| Typical | 40KB | 50 | 25 | Average spec |
| Large | 100KB | 150 | 75 | Complex spec |
| Extreme | 500KB | 500 | 250 | Stress test |

#### 6.4.2 Baseline Measurements

**Current Implementation (task_parser.py):**
```
Small (5KB):    20ms,  2MB memory
Typical (40KB): 80ms,  4MB memory
Large (100KB):  180ms, 8MB memory
Extreme (500KB): Untested (exceeds typical use)
```

**Target (parsers/ submodule):**
```
Small (5KB):    20ms ± 5%  (19-21ms)
Typical (40KB): 80ms ± 5%  (76-84ms)
Large (100KB):  180ms ± 5% (171-189ms)
Extreme (500KB): <1000ms (1 second acceptable for rare case)
```

#### 6.4.3 Benchmark Implementation

```python
import pytest
import time
from pathlib import Path

@pytest.mark.benchmark
def test_parse_performance_typical():
    """Benchmark typical 40KB spec parsing."""
    parser = SpecTasksParser()
    spec_path = Path("test/fixtures/typical_40kb_tasks.md")
    
    # Warmup
    parser.parse(spec_path)
    
    # Measure
    start = time.perf_counter()
    for _ in range(10):
        result = parser.parse(spec_path)
    elapsed = time.perf_counter() - start
    
    avg_ms = (elapsed / 10) * 1000
    assert avg_ms < 100, f"Parse took {avg_ms:.1f}ms (target: <100ms)"
    
    # Memory check
    import tracemalloc
    tracemalloc.start()
    result = parser.parse(spec_path)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    peak_mb = peak / (1024 * 1024)
    assert peak_mb < 50, f"Peak memory {peak_mb:.1f}MB (target: <50MB)"
```

---

### 6.5 Regression Testing

**Goal:** Ensure refactor maintains performance (±5% variance acceptable).

#### 6.5.1 Regression Test Suite

```python
@pytest.mark.performance_regression
class TestPerformanceRegression:
    """Compare old vs. new implementation performance."""
    
    def test_parse_speed_regression(self):
        """Ensure new parser not slower than old."""
        # Parse with old implementation
        old_parser = OldSpecTasksParser()  # From task_parser.py
        start = time.perf_counter()
        old_result = old_parser.parse(spec_path)
        old_time = time.perf_counter() - start
        
        # Parse with new implementation
        new_parser = SpecTasksParser()  # From parsers/
        start = time.perf_counter()
        new_result = new_parser.parse(spec_path)
        new_time = time.perf_counter() - start
        
        # Allow ±5% variance
        assert new_time <= old_time * 1.05, \
            f"New parser slower: {new_time:.3f}s vs {old_time:.3f}s"
    
    def test_memory_regression(self):
        """Ensure new parser not using more memory."""
        # Similar memory comparison test
```

**Execution:** Run regression tests on all completed specs before deployment.

---

### 6.6 Profiling & Optimization

#### 6.6.1 Profiling Strategy

**When to Profile:**
- Initial implementation (baseline)
- Before performance optimization
- After optimization (verify improvement)
- On performance regression detection

**Tools:**
```python
# cProfile for function-level profiling
python -m cProfile -o profile.stats test_parser.py

# memory_profiler for memory analysis
@profile
def parse(self, source_path):
    ...

# line_profiler for line-level profiling
@profile
def _score_headers(self, document, content):
    ...
```

**Analysis:**
```python
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)  # Top 20 slowest functions
```

#### 6.6.2 Optimization Opportunities

**Identified Hotspots (Hypothetical - Profile to Confirm):**

1. **AST Traversal (traversal.py):**
   - **Optimization:** Cache node lookups if repeated
   - **Estimate:** 5-10% speedup if multiple traversals

2. **Regex Matching (dependencies.py, extraction.py):**
   - **Optimization:** Compile regex patterns once at module level
   - **Estimate:** 3-5% speedup

3. **String Operations (text.py):**
   - **Optimization:** Use str.startswith() instead of regex where possible
   - **Estimate:** 2-3% speedup

**Implementation Priority:**
1. **Measure first** (profile on real workloads)
2. **Optimize hotspots** (>5% of total time)
3. **Validate improvement** (benchmark before/after)
4. **Avoid premature optimization** (clarity > marginal gains)

---

### 6.7 Scalability Analysis

**Current Scale:**
- Single file parsing (no batch operations)
- On-demand execution (workflow start)
- Single-threaded (no concurrency)

**Scalability Limits:**

| Dimension | Current | Limit | Bottleneck |
|-----------|---------|-------|------------|
| File size | 40KB | 10MB | Memory, parse time |
| Task count | 25 | 5,000 | Algorithm O(n), not performance |
| Parse frequency | On-demand | N/A | Not a bottleneck |
| Concurrent parses | 1 | Unlimited | Stateless, no shared state |

**Not a Concern:**
- Parse frequency low (once per workflow start, not per-request)
- No caching needed (parse is already fast)
- No database involved (no query optimization)
- No horizontal scaling needed (single-process sufficient)

**Future Scaling (If Needed):**
- **Batch Parsing:** Parse multiple specs in parallel (use multiprocessing pool)
- **Caching:** Cache parsed phases if same spec parsed repeatedly (not current pattern)
- **Streaming:** Parse incrementally for huge files (>10MB, not current requirement)

---

### 6.8 Performance Monitoring

#### 6.8.1 Metrics Collection

**Operational Metrics (Logged):**
```python
import logging
import time

logger = logging.getLogger(__name__)

def parse(self, source_path: Path) -> List[DynamicPhase]:
    start = time.perf_counter()
    file_size = source_path.stat().st_size
    
    try:
        phases = self._parse_internal(source_path)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        logger.info(
            "Parse successful",
            extra={
                "source": str(source_path),
                "file_size_kb": file_size / 1024,
                "phase_count": len(phases),
                "task_count": sum(len(p.tasks) for p in phases),
                "parse_time_ms": elapsed_ms,
            }
        )
        return phases
    
    except ParseError as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.error(
            "Parse failed",
            extra={
                "source": str(source_path),
                "file_size_kb": file_size / 1024,
                "parse_time_ms": elapsed_ms,
                "error": str(e),
            }
        )
        raise
```

**Metrics to Track:**
- `parse_time_ms` (histogram): Parse duration
- `file_size_kb` (histogram): Input file size
- `phase_count` (counter): Phases parsed
- `task_count` (counter): Tasks parsed
- `parse_errors` (counter): Parse failures by error type

#### 6.8.2 Performance Alerts (Optional)

**Not Required for Initial Implementation:** Basic logging sufficient for internal tool.

**Future Consideration (If Production Issues):**
```python
# Alert if parse time exceeds threshold
if elapsed_ms > 1000:  # 1 second
    logger.warning(
        f"Slow parse: {elapsed_ms:.0f}ms for {source_path}",
        extra={"parse_time_ms": elapsed_ms, "threshold_ms": 1000}
    )
```

---

### 6.9 Performance Testing Strategy

**Test Levels:**

1. **Unit Tests:** Verify algorithm correctness (not performance-focused)
   ```python
   def test_scoring_correctness():
       score = score_phase_header("Phase 1: Foo", level=2, context="")
       assert score >= 30.0  # Meets threshold
   ```

2. **Benchmark Tests:** Measure parse speed/memory on fixed inputs
   ```python
   @pytest.mark.benchmark
   def test_parse_benchmark():
       # Timed execution, assert < threshold
   ```

3. **Regression Tests:** Compare old vs. new implementation
   ```python
   @pytest.mark.regression
   def test_no_performance_regression():
       # old_time vs new_time, assert new <= old * 1.05
   ```

4. **Stress Tests:** Extreme inputs (huge files, deep nesting)
   ```python
   @pytest.mark.stress
   def test_extreme_file_size():
       # 500KB file, assert parse < 1 second
   ```

**Execution Frequency:**
- Unit tests: Every commit (CI)
- Benchmark tests: Pre-release, performance investigation
- Regression tests: Before deployment (migration validation)
- Stress tests: Manual, during optimization work

---

### 6.10 Performance Summary

**Targets Met:**
- ✅ Parse speed: ≤100ms for 50KB files (current: ~80ms)
- ✅ Memory efficiency: ≤50MB per parse (current: ~4MB)
- ✅ Algorithm complexity: O(n) linear
- ✅ Zero regression: ±5% variance acceptable

**Key Strategies:**
- Single-pass algorithms (no nested loops)
- Minimal AST traversals (batch header collection)
- Memory efficiency (no content duplication)
- Compiled regex patterns (module-level)

**Monitoring:**
- Operational logging (parse time, file size, counts)
- Benchmark suite (4 workload sizes)
- Regression tests (old vs. new comparison)
- Profiling tools (cProfile, memory_profiler)

**Not Required:**
- Caching (parse is fast, infrequent)
- Database optimization (no database)
- Horizontal scaling (single-process sufficient)
- Real-time monitoring (internal tool)

**Future Optimization Opportunities:**
- Profile on real workloads (identify hotspots)
- Optimize hot paths (>5% of total time)
- Parallel batch parsing (if needed)
- Streaming for huge files (if >10MB files emerge)

---

