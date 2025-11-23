# Technical Specifications

**Project:** Project Orientation System  
**Date:** 2025-11-19  
**Based on:** srd.md (requirements)

---

## 1. Architecture Overview

### 1.1 Architectural Pattern

**Primary Pattern:** Modular Extension Architecture

**Rationale:**
- Project orientation extends existing prAxIs OS base orientation system
- Leverages existing RAG infrastructure (standards index, mcp.yaml config)
- Modular design allows projects to adopt orientation without core framework changes
- Reuses proven inline metadata pattern from mistletoe standards parsing design

**Key Characteristics:**
- Extension of existing base orientation (10 mandatory queries)
- Discovery-based activation (AI agents query for project orientation)
- Multiple configuration sources (inline markdown metadata, mcp.yaml extensions)
- Zero-deployment-impact (pure configuration/content changes)

---

### 1.2 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI Agent Instance                            │
│                      (Claude, GPT, etc.)                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ 1. Execute Base Orientation (10 queries)
                             │    Query 10: "project orientation discovery"
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     pos_search_project Tool                          │
│                  (Unified RAG Query Interface)                       │
└────────┬────────────────────────────────┬───────────────────────────┘
         │                                │
         │ 2. Discover Orientation        │ 3. Execute Project Queries
         │    Metadata                    │    (priority order)
         │                                │
         ▼                                ▼
┌────────────────────┐          ┌─────────────────────────┐
│  Standards Index   │          │  Standards Index        │
│  (LanceDB)         │          │  (Query Execution)      │
│                    │          │                         │
│  - Inline Metadata │          │  - Semantic Search      │
│    Parsing         │          │  - Metadata Filtering   │
│  - **Metadata**:   │          │  - Result Ranking       │
│    orientation=true│          │                         │
└────────┬───────────┘          └─────────────────────────┘
         │                                │
         │ Metadata Sources:              │
         │                                │
         ▼                                │
┌─────────────────────────────────────┐  │
│   Project Standards Files           │  │
│   (.praxis-os/standards/)           │  │
│                                     │  │
│   Example: PROJECT-OVERVIEW.md     │  │
│   **Metadata**: orientation=true,  │  │
│                 priority=1,        │  │
│                 query="dogfooding  │  │
│                        model..."   │  │
└─────────────────────────────────────┘  │
         │                                │
         │ OR                             │
         │                                │
         ▼                                │
┌─────────────────────────────────────┐  │
│   mcp.yaml Configuration            │  │
│   (.praxis-os/config/)              │  │
│                                     │  │
│   project:                          │  │
│     orientation:                    │  │
│       - query: "dogfooding model"  │  │
│         priority: 1                │  │
│         description: "..."         │  │
└─────────────────────────────────────┘  │
         │                                │
         └────────────────────────────────┘
                        │
                        │ 4. Results Returned to AI
                        ▼
         ┌────────────────────────────────────┐
         │  AI Agent Context Loaded:          │
         │  - Base prAxIs OS patterns        │
         │  - Project-specific architecture  │
         │  - Domain knowledge               │
         │  - Ready for task execution       │
         └────────────────────────────────────┘
```

---

### 1.3 Architectural Decisions

#### Decision 1: Inline Metadata Pattern (Not YAML Frontmatter)

**Decision:** Use **Metadata**: key=value inline pattern for orientation metadata in markdown files

**Rationale:** 
- FR-004: Error-resistant metadata parsing (AI agents mess up YAML syntax)
- FR-009: No consumer tooling requirements (YAML requires validation infrastructure)
- NFR-R1: Graceful degradation (regex-based parsing skips malformed, continues)
- Reuses proven pattern from mistletoe standards parsing design document

**Alternatives Considered:**
- **YAML Frontmatter**: Rejected due to fragility (indentation errors, bracket/quote errors, silent failures, requires pre-commit validation)
- **JSON Metadata**: Rejected due to similar fragility issues as YAML
- **Custom DSL**: Rejected as unnecessary complexity vs simple key=value

**Trade-offs:**
- **Pros:** Error-resistant, visible to humans, no tooling required, graceful degradation, regex-parseable
- **Cons:** Less structured than YAML (but acceptable for metadata use case), requires documentation for adoption

---

#### Decision 2: mcp.yaml Extension for Project Config

**Decision:** Extend mcp.yaml with optional `project.orientation` section for centralized query definitions

**Rationale:**
- FR-002: Support multiple configuration sources (inline OR mcp.yaml)
- NFR-C1: Leverage existing Pydantic v2 schema infrastructure
- Consistency with unified config system architecture
- Allows projects to choose inline (distributed metadata) or centralized (mcp.yaml) approach

**Alternatives Considered:**
- **Separate orientation.yaml**: Rejected as additional file increases complexity
- **Inline-only**: Too limiting for projects preferring centralized config
- **mcp.yaml-only**: Too limiting for projects wanting distributed metadata in standards

**Trade-offs:**
- **Pros:** Flexibility (inline OR centralized), leverages existing validation, optional not required
- **Cons:** Two config paths to maintain, slightly increased complexity

---

#### Decision 3: Discovery-Based Activation

**Decision:** Project orientation automatically discovered and executed via base orientation query 10

**Rationale:**
- FR-003: Automatic execution after base orientation
- FR-007: Integration with base orientation workflow
- Maintains AI agent autonomy (no manual activation required)
- Query-first reflex pattern (AI discovers via querying)

**Alternatives Considered:**
- **Explicit Activation Flag**: Rejected as requiring manual configuration
- **Always-On**: Rejected as some projects may not need orientation
- **Environment Variable**: Rejected as violating zero-tooling principle

**Trade-offs:**
- **Pros:** Automatic, discovery-based, consistent with prAxIs OS patterns
- **Cons:** Requires base orientation completion first (acceptable: base orientation is mandatory anyway)

---

#### Decision 4: Reuse Standards Index Infrastructure

**Decision:** Store and query orientation metadata via existing standards index (LanceDB)

**Rationale:**
- NFR-M1: Code reuse (leverage existing RAG infrastructure)
- NFR-P2: No significant indexing performance degradation
- Metadata already indexed for standards, just need to filter for orientation=true
- pos_search_project already supports metadata filtering

**Alternatives Considered:**
- **Separate Orientation Index**: Rejected as unnecessary duplication
- **File-Based Storage**: Rejected as requiring custom parsing at query time
- **Database Table**: Rejected as prAxIs OS is database-free

**Trade-offs:**
- **Pros:** Zero additional infrastructure, reuses proven components, unified query interface
- **Cons:** Orientation metadata mixes with standards metadata (acceptable: filtered via orientation=true)

---

### 1.4 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| FR-001 | Inline Metadata Parser (_extract_inline_metadata) | Regex-based parsing detects **Metadata**: orientation=true |
| FR-002 | mcp.yaml Schema Extension (ProjectConfig.orientation) | Pydantic model validates project.orientation section |
| FR-003 | Base Orientation Integration (Query 10 + Discovery) | Query 10 triggers discovery, executes project queries |
| FR-004 | Graceful Degradation (Error Handling) | Skip malformed, log warnings, continue parsing |
| FR-005 | Priority-Based Execution (Query Sorter) | Sort by priority field (1=critical, 2=high, 3=medium) |
| FR-006 | Metadata Pattern Compatibility (Shared Parser) | Reuse _extract_inline_metadata() from standards index |
| FR-007 | Base Orientation Query 10 (Discovery Trigger) | Query 10 text mentions project orientation explicitly |
| FR-008 | Metadata Schema (OrientationMetadata Model) | Pydantic model defines required/optional fields with validation |
| FR-009 | Zero Tooling (Markdown + Regex Only) | No build step, no pre-commit hooks, works with files only |
| NFR-P1 | Efficient Query Execution (LanceDB Indexes) | Reuse existing vector + scalar indexes for fast filtering |
| NFR-R1 | Graceful Degradation (Try-Except + Logging) | All parsing wrapped in error handlers, never fail indexing |
| NFR-U1 | Zero Tooling (Config-Driven) | Everything driven by markdown metadata or mcp.yaml config |
| NFR-M1 | Code Reuse (Shared Components) | Reuse standards index parser, mcp.yaml infrastructure |
| NFR-C1 | Config Compatibility (Pydantic v2) | New schemas follow existing UnifiedConfig pattern |
| NFR-S1 | No Code Execution (Regex Only) | re.search() only, no eval/exec, metadata treated as data |

---

### 1.5 Technology Stack

**Backend (Python):**
- Python 3.11+ (existing prAxIs OS requirement)
- Pydantic v2 (schema validation for mcp.yaml extensions)
- Python `re` module (regex-based metadata parsing)
- LanceDB (existing standards index storage)

**Data Storage:**
- LanceDB (vector + scalar indexes for orientation metadata)
- Filesystem (markdown files with inline metadata)
- YAML (mcp.yaml configuration file)

**No Additional Dependencies:**
- Reuses existing prAxIs OS infrastructure
- No new Python packages required
- No build tools or pre-processors

---

## 2. Component Design

---

### 2.1 Component: Inline Metadata Parser

**Purpose:** Extract orientation metadata from markdown files using regex-based **Metadata**: key=value pattern

**Responsibilities:**
- Parse **Metadata**: lines in markdown files
- Extract key=value pairs with error resistance
- Perform type coercion (bool, int, string)
- Return dictionary with graceful degradation on errors
- Filter for orientation=true marker

**Requirements Satisfied:**
- FR-001: Inline metadata discovery
- FR-004: Error-resistant parsing
- FR-006: Standards metadata pattern compatibility
- NFR-R1: Graceful degradation
- NFR-S1: No code execution (regex only)

**Public Interface:**
```python
class OrientationMetadataParser:
    """Parse orientation metadata from markdown content."""
    
    def extract_inline_metadata(
        self, 
        content: str, 
        file_path: Path
    ) -> Dict[str, Any]:
        """Extract metadata from **Metadata**: line.
        
        Args:
            content: Markdown file content
            file_path: Path for logging/debugging
            
        Returns:
            Dict with extracted metadata or defaults
            
        Examples:
            >>> parser.extract_inline_metadata(content, path)
            {'orientation': True, 'priority': 1, 'query': '...'}
        """
        pass
        
    def _coerce_type(self, value: str) -> Union[bool, int, str]:
        """Coerce string value to appropriate type."""
        pass
```

**Dependencies:**
- Requires: Python `re` module (standard library)
- Provides: Parsed metadata dicts for standards index

**Error Handling:**
- Missing **Metadata**: line → return path-based defaults
- Malformed key=value → skip pair, parse remaining, log warning
- Typo in marker → return defaults, log warning
- Bad type coercion → skip field, log warning, continue

**Implementation Notes:**
- Reuse logic from mistletoe standards parsing design
- Regex: `r'\*\*Metadata\*\*:\s*(.+)'`
- Comma-separated parsing with split(',')
- Type coercion: `value.lower() in ('true', 'false')` for bool, `value.isdigit()` for int

---

### 2.2 Component: mcp.yaml Configuration Extension

**Purpose:** Extend mcp.yaml schema with optional `project.orientation` section for centralized query definitions

**Responsibilities:**
- Define Pydantic v2 schema for project orientation config
- Validate orientation query structure
- Provide defaults for optional fields
- Integrate with existing UnifiedConfig system

**Requirements Satisfied:**
- FR-002: mcp.yaml project orientation extension
- FR-008: Orientation metadata schema
- NFR-C1: Configuration schema compatibility

**Public Interface:**
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class OrientationQuery(BaseModel):
    """Single orientation query definition."""
    
    query: str = Field(..., description="Query string for pos_search_project")
    priority: int = Field(1, ge=1, le=3, description="1=critical, 2=high, 3=medium")
    description: Optional[str] = Field(None, description="Human-readable purpose")
    category: Optional[str] = Field(None, description="Query category (architecture, patterns, etc.)")
    depends_on: Optional[List[str]] = Field(None, description="Query dependencies")

class ProjectOrientation(BaseModel):
    """Project-specific orientation configuration."""
    
    enabled: bool = Field(True, description="Enable project orientation")
    queries: List[OrientationQuery] = Field(default_factory=list)
    
class ProjectConfig(BaseModel):
    """Top-level project configuration."""
    
    orientation: Optional[ProjectOrientation] = None
    
# Extend existing UnifiedConfig
class UnifiedConfig(BaseModel):
    # ... existing fields ...
    project: Optional[ProjectConfig] = None
```

**Dependencies:**
- Requires: Pydantic v2, existing UnifiedConfig
- Provides: Validated orientation configuration

**Error Handling:**
- Missing project.orientation → project orientation disabled, graceful
- Invalid query priority → validation error with actionable message
- Circular dependencies → validation error, suggest fix

---

### 2.3 Component: Orientation Discovery Handler

**Purpose:** Discover project orientation metadata from standards index and mcp.yaml, merge sources

**Responsibilities:**
- Query standards index for orientation=true metadata
- Load project.orientation from mcp.yaml if present
- Merge inline and config-based orientation definitions
- Deduplicate queries across sources
- Sort by priority

**Requirements Satisfied:**
- FR-001: Inline metadata discovery
- FR-002: mcp.yaml extension support
- FR-005: Query execution order and dependencies

**Public Interface:**
```python
class OrientationDiscoveryHandler:
    """Discover and aggregate orientation metadata."""
    
    def __init__(
        self,
        standards_index: StandardsIndex,
        config: UnifiedConfig
    ):
        """Initialize with index and config access."""
        pass
        
    def discover_orientation_queries(self) -> List[OrientationQuery]:
        """Discover all orientation queries from all sources.
        
        Returns:
            Sorted list of orientation queries (by priority, then definition order)
            
        Sources:
            1. Standards index (metadata with orientation=true)
            2. mcp.yaml (project.orientation.queries)
        """
        pass
        
    def _merge_sources(
        self,
        inline_queries: List[Dict],
        config_queries: List[OrientationQuery]
    ) -> List[OrientationQuery]:
        """Merge and deduplicate queries from multiple sources."""
        pass
```

**Dependencies:**
- Requires: StandardsIndex, UnifiedConfig, OrientationMetadataParser
- Provides: Aggregated orientation queries list

**Error Handling:**
- No orientation metadata found → return empty list (graceful)
- Duplicate queries → merge metadata, prefer explicit config
- Malformed queries → log warning, skip, continue

---

### 2.4 Component: Project Orientation Executor

**Purpose:** Execute discovered orientation queries in priority order via pos_search_project

**Responsibilities:**
- Execute orientation queries via pos_search_project
- Respect priority ordering (critical → high → medium)
- Handle query dependencies (if specified)
- Collect and return results to AI agent
- Track execution time for NFR-P1 compliance

**Requirements Satisfied:**
- FR-003: Automatic project orientation execution
- FR-005: Query execution order and dependencies
- NFR-P1: Orientation execution time < 1 minute

**Public Interface:**
```python
class ProjectOrientationExecutor:
    """Execute project orientation queries."""
    
    def __init__(self, search_tool):
        """Initialize with pos_search_project tool."""
        self.search_tool = search_tool
        
    def execute_orientation(
        self,
        queries: List[OrientationQuery]
    ) -> List[Dict]:
        """Execute orientation queries in priority order.
        
        Args:
            queries: Sorted list of orientation queries
            
        Returns:
            List of query results with metadata
            
        Raises:
            TimeoutError: If execution exceeds 1 minute
        """
        pass
        
    def _resolve_dependencies(
        self,
        queries: List[OrientationQuery]
    ) -> List[OrientationQuery]:
        """Resolve query dependencies, return execution order."""
        pass
```

**Dependencies:**
- Requires: pos_search_project tool, OrientationQuery models
- Provides: Query execution results

**Error Handling:**
- Query execution failure → log error, continue with remaining queries
- Timeout (>1 minute) → log warning, return partial results
- Circular dependencies → detect early, raise validation error

---

### 2.5 Component: Base Orientation Integration

**Purpose:** Integrate project orientation discovery into base orientation workflow (Query 10 modification)

**Responsibilities:**
- Modify Query 10 to trigger project orientation discovery
- Document project orientation in base orientation standard
- Ensure AI agents discover and execute project queries
- Maintain backward compatibility (no breaking changes to base orientation)

**Requirements Satisfied:**
- FR-007: Base orientation integration
- NFR-C1: Configuration schema compatibility (backward compatible)

**Public Interface:**
```markdown
### Query 10: Project-Specific Orientation Discovery

**Query String:** "project orientation discovery project-specific context queries"

**Purpose:** Discover if the current project defines project-specific orientation queries beyond base prAxIs OS patterns

**Expected Actions:**
1. Query pos_search_project for orientation metadata
2. If project orientation found, execute project queries in priority order
3. Load project-specific context (architecture, patterns, conventions)

**Success Criteria:**
- Project orientation metadata discovered (if present)
- Project queries executed successfully
- AI understands both base AND project context

**Fallback:**
- If no project orientation defined, continue with base orientation only
- Graceful degradation: missing/malformed metadata doesn't block orientation
```

**Dependencies:**
- Requires: Base orientation standard file, OrientationDiscoveryHandler
- Provides: Entry point for project orientation discovery

**Error Handling:**
- No project orientation → continue gracefully (base orientation sufficient)
- Discovery errors → log warning, continue with base orientation only

---

## 2.6 Component Interactions

**Interaction Flow:**

```
┌────────────────────────────────────────────────────────────────────┐
│ 1. AI Agent executes Base Orientation Query 10                     │
│    → Triggers project orientation discovery                         │
└─────────────────┬──────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. OrientationDiscoveryHandler.discover_orientation_queries()      │
│    ├─→ Query StandardsIndex (orientation=true)                     │
│    │   └─→ OrientationMetadataParser.extract_inline_metadata()     │
│    ├─→ Load UnifiedConfig (project.orientation)                    │
│    └─→ Merge sources, deduplicate, sort by priority                │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 3. ProjectOrientationExecutor.execute_orientation(queries)          │
│    ├─→ Resolve dependencies                                         │
│    ├─→ For each query (priority order):                             │
│    │   └─→ pos_search_project(query=query.query)                    │
│    └─→ Collect results                                              │
└─────────────────┬────────────────────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────────────┐
│ 4. Return results to AI Agent                                  │
│    → AI context loaded with project-specific knowledge         │
└────────────────────────────────────────────────────────────────┘
```

**Component Dependency Table:**

| From Component | To Component | Method/Interface | Purpose |
|----------------|--------------|------------------|---------|
| Base Orientation Query 10 | OrientationDiscoveryHandler | `discover_orientation_queries()` | Trigger discovery |
| OrientationDiscoveryHandler | StandardsIndex | `query(metadata={'orientation': True})` | Find inline metadata |
| OrientationDiscoveryHandler | OrientationMetadataParser | `extract_inline_metadata(content)` | Parse **Metadata**: lines |
| OrientationDiscoveryHandler | UnifiedConfig | `config.project.orientation` | Load mcp.yaml config |
| ProjectOrientationExecutor | pos_search_project | `search(query, n_results)` | Execute queries |
| ProjectOrientationExecutor | OrientationQuery | Data model | Query definition structure |

---

## 2.7 Module Organization

**Directory Structure:**

```
ouroboros/
├── subsystems/
│   ├── rag/
│   │   └── standards/
│   │       ├── semantic.py              # Existing standards index
│   │       └── orientation.py           # NEW: Orientation components
│   │           ├── OrientationMetadataParser
│   │           ├── OrientationDiscoveryHandler
│   │           └── ProjectOrientationExecutor
│   └── config/
│       └── models.py                    # Extend with ProjectConfig, OrientationQuery
│
├── standards/
│   └── universal/
│       └── ai-assistant/
│           └── PRAXIS-OS-ORIENTATION.md # Modify Query 10
│
.praxis-os/
├── config/
│   └── mcp.yaml                         # Optional: project.orientation section
└── standards/
    └── project/
        └── PROJECT-OVERVIEW.md          # Example: **Metadata**: orientation=true, ...
```

**Dependency Rules:**
- No circular imports between orientation.py and existing standards index
- OrientationMetadataParser can import from standards/semantic.py (code reuse)
- Config models extend existing UnifiedConfig (backward compatible)
- Base orientation standard modified in-place (Query 10 text change only)

---

## 3. API Design

**Note:** This feature has no HTTP/REST APIs - all interfaces are internal Python APIs consumed by prAxIs OS subsystems.

---

### 3.1 Public Python Interfaces

#### OrientationMetadataParser.extract_inline_metadata()

**Purpose:** Extract orientation metadata from markdown content

**Signature:**
```python
def extract_inline_metadata(
    self, 
    content: str, 
    file_path: Path
) -> Dict[str, Any]:
    """Extract metadata from **Metadata**: line.
    
    Args:
        content: Full markdown file content
        file_path: Path to file (for logging)
        
    Returns:
        Dict with extracted metadata:
        {
            'orientation': bool,      # Required marker
            'priority': int,          # 1-3 (optional, default 2)
            'query': str,             # Query string (optional)
            'category': str,          # Category tag (optional)
            'description': str,       # Human-readable (optional)
            'depends_on': List[str]   # Dependencies (optional)
        }
        
    Raises:
        Never raises - returns defaults on error
        
    Example:
        >>> parser.extract_inline_metadata(content, path)
        {'orientation': True, 'priority': 1, 'query': 'dogfooding model'}
    """
```

**Error Handling:**
- Missing **Metadata**: line → returns empty dict `{}`
- Malformed key=value → skips bad pair, logs warning, continues
- Type coercion failure → skips field, logs warning, continues

---

#### OrientationDiscoveryHandler.discover_orientation_queries()

**Purpose:** Discover and aggregate orientation queries from all sources

**Signature:**
```python
def discover_orientation_queries(self) -> List[OrientationQuery]:
    """Discover all orientation queries from inline metadata and mcp.yaml.
    
    Returns:
        Sorted list of OrientationQuery objects (by priority, then order)
        Empty list if no orientation defined (graceful)
        
    Raises:
        Never raises - logs warnings on errors, returns partial results
        
    Example:
        >>> handler.discover_orientation_queries()
        [
            OrientationQuery(query='dogfooding model', priority=1),
            OrientationQuery(query='ouroboros architecture', priority=1),
            OrientationQuery(query='query-first protocol', priority=2)
        ]
    """
```

**Sources Checked:**
1. StandardsIndex query with `metadata={'orientation': True}`
2. UnifiedConfig `project.orientation.queries` (if present)

**Error Handling:**
- No orientation found → returns `[]` (empty list, graceful)
- Duplicate queries → merges metadata, prefers mcp.yaml over inline
- Malformed queries → skips, logs warning, continues

---

#### ProjectOrientationExecutor.execute_orientation()

**Purpose:** Execute orientation queries via pos_search_project

**Signature:**
```python
def execute_orientation(
    self,
    queries: List[OrientationQuery]
) -> List[Dict[str, Any]]:
    """Execute orientation queries in priority order.
    
    Args:
        queries: Sorted list of orientation queries
        
    Returns:
        List of dicts with query results:
        [
            {
                'query': str,
                'results': List[Dict],  # Search results
                'execution_time_ms': int,
                'success': bool
            }
        ]
        
    Raises:
        TimeoutError: If total execution exceeds 60 seconds (NFR-P1)
        
    Example:
        >>> executor.execute_orientation(queries)
        [
            {
                'query': 'dogfooding model',
                'results': [{...}],
                'execution_time_ms': 250,
                'success': True
            }
        ]
    """
```

**Execution Order:**
1. Resolve dependencies (if `depends_on` specified)
2. Execute queries in priority order (1 → 2 → 3)
3. Within same priority, execute in definition order
4. Track time per query and total time

**Error Handling:**
- Query execution failure → logs error, continues with remaining queries
- Timeout (>60s total) → logs warning, returns partial results
- Circular dependencies → raises ValueError during resolution

---

### 3.2 Data Transfer Objects (Pydantic Models)

#### OrientationQuery

**Purpose:** Define single orientation query with metadata

**Schema:**
```python
class OrientationQuery(BaseModel):
    """Single orientation query definition."""
    
    query: str = Field(
        ..., 
        description="Query string for pos_search_project",
        min_length=5,
        max_length=500
    )
    
    priority: int = Field(
        2, 
        ge=1, 
        le=3,
        description="1=critical, 2=high, 3=medium"
    )
    
    description: Optional[str] = Field(
        None,
        description="Human-readable purpose of query",
        max_length=200
    )
    
    category: Optional[str] = Field(
        None,
        description="Query category (architecture, patterns, domain, etc.)",
        max_length=50
    )
    
    depends_on: Optional[List[str]] = Field(
        None,
        description="List of query strings this depends on"
    )
    
    # Validation
    @validator('priority')
    def validate_priority(cls, v):
        """Ensure priority in range 1-3."""
        if v < 1 or v > 3:
            raise ValueError("Priority must be 1 (critical), 2 (high), or 3 (medium)")
        return v
    
    @validator('depends_on')
    def validate_no_circular_deps(cls, v, values):
        """Prevent self-dependencies."""
        if v and values.get('query') in v:
            raise ValueError("Query cannot depend on itself")
        return v
```

**Validation Rules:**
- `query`: Required, 5-500 characters
- `priority`: 1-3 integer (1=critical, 2=high, 3=medium)
- `description`: Optional, max 200 chars
- `category`: Optional, max 50 chars
- `depends_on`: Optional list, no circular dependencies

---

#### ProjectOrientation

**Purpose:** Project-level orientation configuration for mcp.yaml

**Schema:**
```python
class ProjectOrientation(BaseModel):
    """Project-specific orientation configuration."""
    
    enabled: bool = Field(
        True,
        description="Enable project orientation discovery and execution"
    )
    
    queries: List[OrientationQuery] = Field(
        default_factory=list,
        description="List of project orientation queries"
    )
    
    # Validation
    @validator('queries')
    def validate_no_duplicate_queries(cls, v):
        """Ensure no duplicate query strings."""
        queries = [q.query for q in v]
        if len(queries) != len(set(queries)):
            raise ValueError("Duplicate queries found - each query must be unique")
        return v
```

**Validation Rules:**
- `enabled`: Boolean, defaults to True
- `queries`: List of OrientationQuery, must be unique

---

### 3.3 Configuration Extension (mcp.yaml)

#### Project Config Schema

**mcp.yaml Extension:**
```yaml
# Existing mcp.yaml structure
# ...

# NEW: Optional project configuration section
project:
  orientation:
    enabled: true
    queries:
      - query: "dogfooding model local-first development workflow"
        priority: 1
        description: "Understand project's dogfooding development pattern"
        category: "development-workflow"
        
      - query: "ouroboros architecture layered subsystems modular design"
        priority: 1
        description: "Learn system architecture and component boundaries"
        category: "architecture"
        
      - query: "query-first decision protocol grep-first anti-pattern"
        priority: 2
        description: "Learn decision-making patterns for AI agents"
        category: "ai-patterns"
        depends_on:
          - "dogfooding model local-first development workflow"
```

**Schema Validation:**
- Validated via Pydantic at config load time
- Invalid config → actionable error message with line number and fix suggestion
- Backward compatible: missing `project` section is valid (orientation disabled)

---

### 3.4 Error Response Format

**All components use consistent error logging:**

```python
# Error format
{
    'component': 'OrientationMetadataParser',
    'method': 'extract_inline_metadata',
    'error_type': 'MalformedMetadata',
    'file_path': '.praxis-os/standards/project/OVERVIEW.md',
    'line_content': '**Metadata**: orientation=true priority=missing-comma',
    'error_detail': 'Failed to parse priority=missing-comma: missing comma separator',
    'action_taken': 'Skipped malformed pair, continuing with remaining metadata',
    'severity': 'warning'
}
```

**Logging Levels:**
- `DEBUG`: Successful parsing, query execution
- `INFO`: Discovery results, execution summary
- `WARNING`: Malformed metadata, parse errors, slow queries
- `ERROR`: Unexpected failures (should be rare due to graceful degradation)

**Never Raised Exceptions:**
- Metadata parsing never raises (returns defaults)
- Discovery never raises (returns empty list)
- Execution may raise TimeoutError (after 60s, per NFR-P1)

---

## 4. Data Models

**Note:** This feature uses existing LanceDB storage (standards index) with metadata extensions. No new database tables required.

---

### 4.1 Orientation Metadata Model (Inline in Markdown)

**Storage Format:** Inline in markdown files

**Example:**
```markdown
# Project Overview

**Metadata**: orientation=true, priority=1, query="dogfooding model development workflow", category="development", description="Learn project's local-first development pattern"

## Architecture

This project uses a dogfooding model...
```

**Parsed Representation:**
```python
{
    'orientation': True,           # Required marker (bool)
    'priority': 1,                  # 1-3 (int, default 2)
    'query': 'dogfooding model...',# Query string (str, optional)
    'category': 'development',      # Category tag (str, optional)
    'description': 'Learn...',      # Human-readable (str, optional)
    # Path-based defaults if inline missing:
    'domain': 'project',            # From file path
    'file_path': '.praxis-os/standards/project/OVERVIEW.md'
}
```

**Storage:** Stored in LanceDB as part of standards index chunk metadata (no schema changes)

---

### 4.2 Standards Index Chunk with Orientation Metadata

**Existing LanceDB Schema (extended with orientation metadata):**

```python
# LanceDB Table: standards_chunks
{
    'id': str,                     # Chunk ID (UUID)
    'content': str,                # Chunk text content
    'vector': List[float],         # Embedding vector (1536 dims)
    'file_path': str,              # Source file path
    'section': str,                # Section heading
    'chunk_id': str,               # Chunk identifier
    
    # Existing metadata fields:
    'domain': str,                 # universal/development/etc.
    'phase': int,                  # 0-8 (if applicable)
    
    # NEW: Orientation metadata fields (added via inline parsing):
    'orientation': bool,           # Orientation marker (default False)
    'priority': int,               # 1-3 (if orientation=True)
    'query': str,                  # Query string (if specified)
    'category': str,               # Category tag (if specified)
    'description': str             # Human-readable (if specified)
}
```

**Indexes:**
- **Vector index:** HNSW for semantic search (existing)
- **Scalar indexes:** 
  - `domain` (btree, existing)
  - `phase` (bitmap, existing)
  - **NEW**: `orientation` (bitmap, for fast filtering)
  - **NEW**: `priority` (bitmap, for sorting)

**Query Pattern:**
```python
# Discover orientation metadata
results = standards_index.query(
    metadata={'orientation': True},
    n_results=100
)

# Filter and sort by priority
orientation_chunks = [
    r for r in results 
    if r['metadata'].get('query')  # Has query defined
]
sorted_chunks = sorted(
    orientation_chunks,
    key=lambda x: (
        x['metadata'].get('priority', 2),  # Sort by priority first
        x['file_path']                      # Then by file path
    )
)
```

---

### 4.3 OrientationQuery Domain Model

**Purpose:** In-memory representation of orientation query with validation

**Model Definition:**
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class OrientationQuery(BaseModel):
    """Single orientation query definition."""
    
    query: str = Field(..., min_length=5, max_length=500)
    priority: int = Field(2, ge=1, le=3)
    description: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    depends_on: Optional[List[str]] = None
    source: str = Field(..., description="inline|mcp.yaml")
    file_path: Optional[str] = None
    
    class Config:
        frozen = True  # Immutable after creation
```

**Business Rules:**
- Priority 1 = Critical (execute first)
- Priority 2 = High (default)
- Priority 3 = Medium (execute last)
- Query must be valid pos_search_project query string
- No circular dependencies allowed

**Lifecycle:**
1. Created by OrientationDiscoveryHandler from LanceDB chunks or mcp.yaml
2. Validated via Pydantic
3. Sorted by priority + order
4. Passed to ProjectOrientationExecutor
5. Executed via pos_search_project
6. Results returned to AI agent

---

### 4.4 ProjectOrientation Configuration Model

**Purpose:** Configuration schema for mcp.yaml project orientation section

**Model Definition:** (Already defined in API section 3.2)

**Storage Format (mcp.yaml):**
```yaml
project:
  orientation:
    enabled: true
    queries:
      - query: "dogfooding model"
        priority: 1
        description: "Learn development workflow"
        category: "development"
        
      - query: "ouroboros architecture"
        priority: 1
        description: "Learn system structure"
        category: "architecture"
        depends_on:
          - "dogfooding model"
```

**Validation:**
- Validated at config load time via Pydantic v2
- Invalid config → ConfigValidationError with actionable message
- Missing section → defaults to disabled (graceful)

---

### 4.5 Execution Result Model

**Purpose:** Track query execution results and timing

**Model:**
```python
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class OrientationExecutionResult:
    """Result of executing a single orientation query."""
    
    query: str
    priority: int
    success: bool
    results: List[Dict[str, Any]]  # pos_search_project results
    execution_time_ms: int
    error: Optional[str] = None
    
@dataclass
class OrientationSessionSummary:
    """Summary of complete orientation session."""
    
    total_queries: int
    successful_queries: int
    failed_queries: int
    total_execution_time_ms: int
    results: List[OrientationExecutionResult]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_queries == 0:
            return 0.0
        return (self.successful_queries / self.total_queries) * 100
```

**Usage:**
```python
# After execution
summary = executor.execute_orientation(queries)
logger.info(f"Orientation complete: {summary.success_rate:.1f}% success rate")
logger.info(f"Total time: {summary.total_execution_time_ms}ms")
```

---

### 4.6 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│ 1. INPUT: Markdown Files + mcp.yaml                          │
│                                                               │
│    PROJECT-OVERVIEW.md                    mcp.yaml           │
│    **Metadata**: orientation=true   project:                 │
│                  priority=1            orientation:           │
│                  query="..."             queries: [...]      │
└───────────────┬──────────────────────┬───────────────────────┘
                │                      │
                ▼                      ▼
┌────────────────────────────┐  ┌──────────────────────────┐
│ 2. PARSING                 │  │ 2. CONFIG LOADING        │
│                            │  │                          │
│ OrientationMetadataParser  │  │ UnifiedConfig            │
│ → Dict[str, Any]           │  │ → ProjectOrientation     │
└─────────────┬──────────────┘  └──────────┬───────────────┘
              │                            │
              ▼                            ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. STORAGE: LanceDB Standards Index                          │
│                                                               │
│    Chunk Metadata:                  Config In-Memory:        │
│    {orientation: True,               ProjectOrientation      │
│     priority: 1,                     object                  │
│     query: "..."}                                            │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. DISCOVERY & AGGREGATION                                   │
│                                                               │
│    OrientationDiscoveryHandler                               │
│    → List[OrientationQuery]                                  │
│    (sorted by priority)                                      │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. EXECUTION                                                  │
│                                                               │
│    ProjectOrientationExecutor                                │
│    → OrientationSessionSummary                               │
│    (results + timing)                                        │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. OUTPUT: AI Agent Context                                  │
│                                                               │
│    - Base prAxIs OS patterns (from base orientation)         │
│    - Project-specific knowledge (from project orientation)   │
│    - Ready for task execution                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. Security Design

**Threat Model:** This is an internal framework extension with no network exposure. Primary security concerns are input validation and preventing code execution via metadata.

---

### 5.1 No Code Execution Risk

**Requirement:** NFR-S1 - No eval/exec or dynamic code execution

**Implementation:**
- **Regex-Based Parsing Only:** All metadata parsing uses Python `re` module
  ```python
  # Safe: Regex pattern matching
  match = re.search(r'\*\*Metadata\*\*:\s*(.+)', content)
  
  # NEVER use eval, exec, or compile
  # ❌ eval(metadata_value)    # FORBIDDEN
  # ❌ exec(query_string)       # FORBIDDEN
  # ❌ compile(code, '<string>', 'exec')  # FORBIDDEN
  ```

- **Data-Only Treatment:** All metadata values treated as data, never as code
  ```python
  # All values are strings, ints, or bools (never callables)
  metadata = {
      'orientation': bool,    # Boolean flag
      'priority': int,         # Integer 1-3
      'query': str,            # String query (never executed as code)
      'category': str          # String tag
  }
  ```

- **No Dynamic Imports:** No `__import__()`, `importlib`, or module loading based on metadata

**Validation:**
- Code review checklist: No eval/exec/compile in orientation.py
- Static analysis: mypy, bandit security linting
- Test coverage: Security test cases for malicious metadata attempts

---

### 5.2 Input Validation

**Requirement:** NFR-S2 - Validate all metadata fields against expected types

**Validation Layers:**

**Layer 1: Type Coercion with Fallback**
```python
def _coerce_type(self, value: str) -> Union[bool, int, str]:
    """Safely coerce string value to appropriate type."""
    try:
        # Boolean detection
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer detection (no negative, no floats)
        if value.isdigit():
            return int(value)
        
        # Default: string (safe fallback)
        return value
        
    except Exception as e:
        logger.warning(f"Type coercion failed for '{value}': {e}")
        return value  # Return string on failure (safe default)
```

**Layer 2: Pydantic Schema Validation**
```python
class OrientationQuery(BaseModel):
    query: str = Field(..., min_length=5, max_length=500)  # Length limits
    priority: int = Field(2, ge=1, le=3)                   # Range validation
    depends_on: Optional[List[str]] = None
    
    @validator('query')
    def validate_query_safe(cls, v):
        """Ensure query doesn't contain dangerous patterns."""
        # No shell metacharacters
        dangerous_chars = ['`', '$', ';', '|', '&', '>', '<']
        if any(char in v for char in dangerous_chars):
            raise ValueError(f"Query contains forbidden characters")
        return v
    
    @validator('depends_on')
    def validate_no_circular_deps(cls, v, values):
        """Prevent circular dependencies."""
        if v and values.get('query') in v:
            raise ValueError("Circular dependency detected")
        return v
```

**Layer 3: Dependency Graph Validation**
```python
def _validate_dependency_graph(self, queries: List[OrientationQuery]) -> None:
    """Detect circular dependencies and infinite loops."""
    
    # Build dependency graph
    graph = {q.query: q.depends_on or [] for q in queries}
    
    # Detect cycles using depth-first search
    visited = set()
    rec_stack = set()
    
    def has_cycle(node):
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True  # Cycle detected
                
        rec_stack.remove(node)
        return False
    
    for query in graph:
        if query not in visited:
            if has_cycle(query):
                raise ValueError(f"Circular dependency detected involving '{query}'")
```

**Validation Summary:**
- Query strings: 5-500 characters, no shell metacharacters
- Priority: Integer 1-3 only
- Dependencies: No circular references, no self-dependencies
- All parsing wrapped in try-except with graceful fallback

---

### 5.3 Data Protection

**Requirement:** Protect orientation metadata from tampering or exposure

**Markdown Files (Inline Metadata):**
- **Storage:** Plain text in `.praxis-os/standards/` directory
- **Access Control:** Filesystem permissions (same as other standards)
- **Integrity:** Git version control tracks all changes
- **No Secrets:** Orientation metadata is non-sensitive project knowledge (no API keys, passwords)

**mcp.yaml Configuration:**
- **Storage:** Plain text YAML in `.praxis-os/config/` directory
- **Access Control:** Filesystem permissions
- **Integrity:** Git version control
- **No Secrets:** Configuration is non-sensitive (queries are public knowledge)

**LanceDB Index:**
- **Storage:** Local LanceDB files in `.praxis-os/.cache/`
- **Access Control:** Filesystem permissions
- **Integrity:** Rebuilt from source files on changes (cache, not source of truth)
- **No Sensitive Data:** Contains project documentation and metadata only

**Threat Assessment:**
- ✅ No network exposure (local filesystem only)
- ✅ No authentication required (internal framework)
- ✅ No PII or sensitive data in orientation metadata
- ✅ Git tracks all changes (audit trail)
- ✅ Malicious metadata cannot execute code (regex parsing only)

---

### 5.4 Query Execution Safety

**Requirement:** Ensure orientation queries cannot cause damage or data leakage

**Query Execution Constraints:**
- **Read-Only:** All queries are read-only (pos_search_project is read-only)
- **No Side Effects:** Queries cannot modify state, write files, or execute commands
- **Timeout Protection:** 60-second timeout prevents runaway queries (NFR-P1)
- **Rate Limiting:** Implicit via total execution time limit

**Safe Query Patterns:**
```python
def execute_orientation(self, queries: List[OrientationQuery]) -> List[Dict]:
    """Execute queries with safety controls."""
    
    start_time = time.time()
    results = []
    
    for query in queries:
        # Timeout check
        elapsed = (time.time() - start_time) * 1000
        if elapsed > 60000:  # 60 seconds
            logger.warning(f"Orientation timeout after {elapsed}ms")
            break
        
        try:
            # Execute read-only query
            result = self.search_tool.search(
                query=query.query,
                n_results=5  # Limit results per query
            )
            results.append({
                'query': query.query,
                'success': True,
                'results': result
            })
            
        except Exception as e:
            # Graceful error handling (never crash)
            logger.error(f"Query execution failed: {e}")
            results.append({
                'query': query.query,
                'success': False,
                'error': str(e)
            })
            # Continue with remaining queries
    
    return results
```

---

### 5.5 Security Monitoring & Logging

**Requirement:** Log security-relevant events for auditing

**Security Audit Log Events:**

```python
# 1. Malformed Metadata Detected
logger.warning(
    "Malformed metadata detected",
    extra={
        'component': 'OrientationMetadataParser',
        'file_path': file_path,
        'line_content': metadata_line,
        'error': 'Missing comma separator',
        'action': 'Skipped malformed pair, continuing'
    }
)

# 2. Circular Dependency Detected
logger.error(
    "Circular dependency in orientation queries",
    extra={
        'component': 'ProjectOrientationExecutor',
        'queries': [q1, q2, q3],
        'cycle': 'q1 → q2 → q3 → q1',
        'action': 'Rejected configuration'
    }
)

# 3. Query Execution Timeout
logger.warning(
    "Orientation execution timeout",
    extra={
        'component': 'ProjectOrientationExecutor',
        'elapsed_ms': 60500,
        'completed_queries': 7,
        'remaining_queries': 3,
        'action': 'Returning partial results'
    }
)

# 4. Suspicious Query Pattern
logger.warning(
    "Suspicious query pattern detected",
    extra={
        'component': 'OrientationQuery',
        'query': query_string,
        'issue': 'Contains shell metacharacters',
        'action': 'Validation rejected'
    }
)
```

**Log Retention:**
- Logs stored in `.praxis-os/logs/orientation.log`
- Rotate daily, keep 30 days
- No PII in logs (queries are non-sensitive)

---

### 5.6 Security Testing Strategy

**Test Cases:**

1. **Malicious Metadata Injection**
   - Test: Metadata with `eval()`, `__import__()`, shell commands
   - Expected: Parsed as strings, never executed

2. **Query String Injection**
   - Test: Queries with shell metacharacters, SQL injection patterns
   - Expected: Validation rejects, logs warning

3. **Circular Dependency Attack**
   - Test: Dependency graph with cycles (A → B → C → A)
   - Expected: Validation detects cycle, rejects configuration

4. **Resource Exhaustion**
   - Test: 1000 queries, each returning 100 results
   - Expected: Timeout after 60s, partial results returned

5. **Path Traversal**
   - Test: file_path with `../../../etc/passwd`
   - Expected: Not applicable (paths from index, not user input)

**Security Review Checklist:**
- [ ] No eval/exec/compile in codebase
- [ ] All metadata values validated via Pydantic
- [ ] Dependency graph validated (no cycles)
- [ ] Timeout protection implemented
- [ ] Security test cases passing
- [ ] Bandit security linting clean

---

## 6. Performance Design

**Performance Targets:** NFR-P1 requires orientation execution < 1 minute for typical projects (5-10 queries)

---

### 6.1 Metadata Parsing Performance

**Requirement:** NFR-P2 - Metadata extraction shall not degrade standards index build time by more than 5%

**Optimization Strategy:**
- **Regex Compilation:** Compile regex patterns once, reuse across files
  ```python
  class OrientationMetadataParser:
      # Class-level compiled regex (amortized cost)
      METADATA_PATTERN = re.compile(r'\*\*Metadata\*\*:\s*(.+)')
      
      def extract_inline_metadata(self, content: str) -> Dict:
          # Compiled regex is fast (O(n) single pass)
          match = self.METADATA_PATTERN.search(content)
          # ...
  ```

- **Single-Pass Parsing:** Extract all metadata in one regex match + split operation
- **No LLM Calls:** Zero-cost parsing (no API calls, no model inference)
- **Lazy Loading:** Parse metadata only when orientation=true filter applied

**Performance Targets:**
- Metadata parsing: < 100ms per markdown file (typical file 10-50 KB)
- Index build overhead: < 5% increase vs. no metadata parsing
- Memory overhead: Negligible (metadata is small dict per chunk)

**Measurement:**
```python
import time

start = time.time()
metadata = parser.extract_inline_metadata(content, path)
elapsed_ms = (time.time() - start) * 1000

assert elapsed_ms < 100, f"Metadata parsing too slow: {elapsed_ms}ms"
```

---

### 6.2 Query Execution Performance

**Requirement:** NFR-P1 - Project orientation execution < 1 minute for typical projects (5-10 queries)

**Performance Budget:**
- Total time: 60,000ms (60 seconds)
- Per-query budget: 60,000ms / 10 queries = 6,000ms/query average
- Realistic: Most queries < 500ms, allows for 2-3 slow queries

**Optimization Strategies:**

**1. Efficient Index Queries:**
```python
# Leverage LanceDB scalar indexes
results = standards_index.query(
    metadata={'orientation': True},  # Bitmap index (fast)
    n_results=100                     # Limit results
)

# Post-filter in memory (cheap)
orientation_results = [
    r for r in results 
    if r['metadata'].get('query')  # Has query defined
]
```

**2. Parallel Query Execution** (Future Optimization):
```python
# Phase 1: Sequential (simple, meets NFR-P1)
for query in queries:
    result = execute_query(query)
    
# Phase 2: Parallel (if needed for > 10 queries)
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(execute_query, queries)
```

**3. Query Result Caching:**
- Cache pos_search_project results per session (in-memory)
- Avoid re-executing identical queries within same orientation session
- Cache invalidation: Clear on index rebuild

**4. Timeout Protection:**
```python
def execute_orientation(self, queries: List[OrientationQuery]) -> List[Dict]:
    start_time = time.time()
    results = []
    
    for query in queries:
        elapsed_ms = (time.time() - start_time) * 1000
        
        if elapsed_ms > 60000:  # 60 second timeout
            logger.warning(f"Orientation timeout after {elapsed_ms}ms")
            break  # Return partial results
            
        # Execute query with per-query timeout
        result = self._execute_with_timeout(query, timeout_ms=10000)
        results.append(result)
    
    return results
```

**Performance Targets:**
- Typical query (5-10 results): 200-500ms
- Complex query (semantic search): 500-2000ms
- Total orientation time: < 60,000ms (60s) for 10 queries
- Timeout: 60s hard limit

---

### 6.3 Memory Optimization

**Requirement:** Minimize memory overhead for orientation metadata

**Memory Budget Analysis:**

**Per-File Metadata:**
```python
# Typical orientation metadata per file
metadata = {
    'orientation': True,      # 1 byte (bool)
    'priority': 1,            # 4 bytes (int)
    'query': '...',           # ~50-200 bytes (str)
    'category': 'arch',       # ~10-50 bytes (str)
    'description': '...'      # ~50-200 bytes (str)
}
# Total: ~120-460 bytes per file with orientation metadata
```

**Project-Wide:**
- Typical project: 5-10 orientation-tagged files
- Memory overhead: 5 files × 400 bytes = 2 KB (negligible)
- Large project: 50 orientation files × 400 bytes = 20 KB (still negligible)

**Optimization Strategies:**
- **Lazy Loading:** Don't load orientation metadata until Query 10 executed
- **Streaming:** Process orientation queries one at a time (no bulk load)
- **No Duplication:** Share metadata dicts between mcp.yaml and inline sources

---

### 6.4 Scalability Considerations

**Scaling Dimensions:**

**1. Number of Orientation Queries:**
- Current target: 5-10 queries (fits 60s budget)
- Maximum supported: 20 queries (with parallel execution in Phase 2)
- Hard limit: 60s timeout ensures bounded execution time

**2. Project Size:**
- Small project (10-50 standards files): < 5 orientation files typical
- Medium project (100-500 files): < 20 orientation files typical  
- Large project (1000+ files): < 50 orientation files typical
- **Observation:** Orientation count scales sub-linearly with project size

**3. Concurrent AI Agents:**
- Orientation is per-agent, per-session (no shared state)
- Multiple agents can execute orientation simultaneously
- Resource contention: Standards index is read-only (no locks)
- **Scalability:** Linear with number of agents (stateless execution)

---

### 6.5 Performance Monitoring

**Metrics to Track:**

**1. Orientation Execution Metrics:**
```python
@dataclass
class OrientationMetrics:
    total_queries: int
    successful_queries: int
    failed_queries: int
    total_execution_time_ms: int
    average_query_time_ms: float
    slowest_query_ms: int
    slowest_query_string: str
    
    # Percentiles
    p50_ms: int
    p95_ms: int
    p99_ms: int
```

**2. Metadata Parsing Metrics:**
```python
@dataclass
class ParsingMetrics:
    files_parsed: int
    files_with_orientation: int
    parsing_time_ms: int
    errors_encountered: int
    malformed_metadata_count: int
```

**3. Performance Targets (SLIs):**
- **Orientation Execution:** p95 < 30,000ms (30s for 10 queries)
- **Metadata Parsing:** p95 < 50ms per file
- **Query Execution:** p95 < 2,000ms per query
- **Discovery:** < 500ms to find all orientation metadata

**4. Alerting Thresholds:**
- ⚠️ **Warning:** Orientation execution > 45s (approaching 60s timeout)
- 🚨 **Error:** Orientation execution timeout (hit 60s limit)
- ⚠️ **Warning:** Query execution > 5s (unusually slow)
- 🚨 **Error:** Metadata parsing errors > 10% of files

**5. Performance Logging:**
```python
logger.info(
    "Orientation execution complete",
    extra={
        'total_queries': 10,
        'successful': 9,
        'failed': 1,
        'total_time_ms': 12450,
        'avg_time_ms': 1383,
        'p95_ms': 2100,
        'slowest_query': 'ouroboros architecture',
        'slowest_time_ms': 2350
    }
)
```

---

### 6.6 Load Testing Strategy

**Test Scenarios:**

**Scenario 1: Typical Project**
- 10 orientation queries
- Each query returns 5 results
- Expected: < 10s total execution time

**Scenario 2: Large Project**
- 20 orientation queries
- Mix of fast (< 500ms) and slow (< 2s) queries
- Expected: < 30s total execution time (within 60s budget)

**Scenario 3: Stress Test**
- 50 orientation queries (unrealistic but tests limits)
- Expected: Timeout after 60s, return partial results

**Scenario 4: Concurrent Agents**
- 10 AI agents execute orientation simultaneously
- Each executes 10 queries
- Expected: All complete successfully, no resource contention

**Load Test Implementation:**
```bash
# Simulate 10 concurrent orientation sessions
python -m pytest tests/performance/test_orientation_load.py \
    --concurrent=10 \
    --queries-per-session=10 \
    --timeout=60
```

---

### 6.7 Performance Regression Prevention

**Automated Performance Tests:**

```python
def test_orientation_execution_performance():
    """Ensure orientation meets NFR-P1 target."""
    
    # Setup: 10 typical queries
    queries = create_typical_orientation_queries()
    executor = ProjectOrientationExecutor(search_tool)
    
    # Execute with timing
    start = time.time()
    results = executor.execute_orientation(queries)
    elapsed_ms = (time.time() - start) * 1000
    
    # Assert: < 60s (NFR-P1 requirement)
    assert elapsed_ms < 60000, \
        f"Orientation execution too slow: {elapsed_ms}ms (target: < 60000ms)"
    
    # Warn if approaching limit
    if elapsed_ms > 45000:
        warnings.warn(f"Orientation execution approaching timeout: {elapsed_ms}ms")

def test_metadata_parsing_performance():
    """Ensure metadata parsing meets NFR-P2 target."""
    
    # Setup: Typical standards file (20 KB)
    content = create_typical_standards_file()
    parser = OrientationMetadataParser()
    
    # Execute with timing
    start = time.time()
    metadata = parser.extract_inline_metadata(content, Path('test.md'))
    elapsed_ms = (time.time() - start) * 1000
    
    # Assert: < 100ms per file
    assert elapsed_ms < 100, \
        f"Metadata parsing too slow: {elapsed_ms}ms (target: < 100ms)"
```

**CI/CD Integration:**
- Run performance tests on every commit
- Fail build if performance regresses > 20%
- Track performance metrics over time (trend analysis)

---


