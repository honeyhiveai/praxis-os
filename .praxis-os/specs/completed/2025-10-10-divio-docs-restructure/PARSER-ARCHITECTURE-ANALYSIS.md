# Dynamic Workflow Parser Architecture Analysis
**Date:** 2025-10-12  
**Purpose:** Complete system analysis before parser refactoring

---

## 1. DATA STRUCTURES & CONTRACTS

### 1.1 DynamicTask (@dataclass)
**Location:** `mcp_server/models/workflow.py:449-480`

**Contract:**
```python
@dataclass
class DynamicTask:
    task_id: str                    # Required: "1.1", "2.3", etc.
    task_name: str                  # Required: Human-readable name
    description: str                # Required: What needs to be done
    estimated_time: str             # Required: "2 hours", "30 minutes", etc.
    dependencies: List[str]         # Required: ["1.1", "1.2"] or []
    acceptance_criteria: List[str]  # Required: Checklist items or []
    
    def to_dict() -> Dict[str, Any]
    @classmethod from_dict(data: Dict[str, Any]) -> DynamicTask
```

**Key Requirements:**
- `task_id` must be in format "N.M" (phase.task)
- All fields are REQUIRED (no optionals)
- Empty lists are valid (not None)
- Must be serializable to/from dict

---

### 1.2 DynamicPhase (@dataclass)
**Location:** `mcp_server/models/workflow.py:483-542`

**Contract:**
```python
@dataclass
class DynamicPhase:
    phase_number: int               # Required: 1, 2, 3, etc. (NOT 0)
    phase_name: str                 # Required: Human-readable name
    description: str                # Required: Phase goal or purpose
    estimated_duration: str         # Required: "4-6 hours", etc.
    tasks: List[DynamicTask]        # Required: Can be empty []
    validation_gate: List[str]      # Required: Gate criteria or []
    
    def to_dict() -> Dict[str, Any]
    @classmethod from_dict(data: Dict[str, Any]) -> DynamicPhase
    def get_task(task_number: int) -> Optional[DynamicTask]  # 1-indexed
```

**Key Requirements:**
- `phase_number` MUST be >= 1 (phase 0 is static, not dynamic)
- `tasks` list can be empty but not None
- `get_task()` uses 1-indexed task_number (not 0-indexed)
- Must be serializable to/from dict

---

### 1.3 SourceParser (Abstract Base Class)
**Location:** `mcp_server/core/parsers.py:26-48`

**Contract:**
```python
class SourceParser(ABC):
    @abstractmethod
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Args:
            source_path: Path to source file OR directory containing it
        
        Returns:
            List[DynamicPhase] - Phases with populated tasks
            
        Raises:
            ParseError: If source invalid or cannot be parsed
        """
```

**Key Requirements:**
- MUST accept both file path AND directory path
- If directory, MUST find `tasks.md` within it
- MUST return List[DynamicPhase] (not empty, or raise ParseError)
- MUST raise ParseError (not generic Exception) on failure
- Each phase MUST have valid phase_number >= 1
- Each task MUST have all required fields populated

---

## 2. DATA FLOW ARCHITECTURE

### 2.1 Initialization Flow

```
WorkflowEngine.start_workflow()
    ↓
creates WorkflowSession.__init__()
    ↓
checks _is_dynamic() → metadata.dynamic_phases == True?
    ↓
YES → _initialize_dynamic_registry()
    ↓
    creates SpecTasksParser()
    ↓
    creates DynamicContentRegistry(
        workflow_type,
        phase_template_path,  # .md template file
        task_template_path,   # .md template file
        source_path,          # spec directory or tasks.md
        parser
    )
        ↓
        DynamicContentRegistry.__init__():
            1. Loads templates from filesystem
            2. Calls parser.parse(source_path)
            3. Creates DynamicWorkflowContent with phases
            4. Raises DynamicRegistryError if anything fails
```

**Critical Paths:**
1. Parser MUST return `List[DynamicPhase]` with all fields populated
2. Registry MUST successfully create `DynamicWorkflowContent`
3. Any exception during init raises `DynamicRegistryError` → caught by Session → raises `WorkflowSessionError`

---

### 2.2 Task Retrieval Flow

```
User calls: get_task(session_id, phase=1, task_number=1)
    ↓
WorkflowEngine.get_task()
    ↓
session = get_session(session_id)
    ↓
session.get_task(phase, task_number)
    ↓
IF dynamic AND has_phase(phase):
    content = dynamic_registry.get_task_content(phase, task_number)
    ↓
    DynamicContentRegistry.get_task_content():
        content.render_task(phase, task_number)
        ↓
        DynamicWorkflowContent.render_task():
            1. Find phase by phase_number (NOT index)
            2. phase_data.get_task(task_number)  # 1-indexed
            3. Render template with task data
            4. Return rendered string
```

**Critical Paths:**
1. Phase lookup by `phase_number` field (not list index)
2. Task lookup is 1-indexed within phase
3. Returns rendered template string, not raw task object

---

### 2.3 Phase Metadata Flow

```
session.get_current_phase()
    ↓
_get_dynamic_phase_content(phase)
    ↓
dynamic_registry.get_phase_metadata(phase)
    ↓
    # Find phase by phase_number
    phase_data = next(p for p in content.phases if p.phase_number == phase)
    
    # Build task metadata
    tasks_metadata = [
        {
            "task_number": i + 1,           # 1-indexed
            "task_id": task.task_id,
            "task_name": task.task_name,
            "estimated_time": task.estimated_time,
            "dependencies": task.dependencies,
        }
        for i, task in enumerate(phase_data.tasks)
    ]
    
    return {
        "phase_number": phase_data.phase_number,
        "phase_name": phase_data.phase_name,
        "description": phase_data.description,
        "estimated_duration": phase_data.estimated_duration,
        "task_count": len(phase_data.tasks),
        "tasks": tasks_metadata,
        "validation_gate": phase_data.validation_gate,
    }
```

**Critical Path:**
- `task_count` is derived from `len(phase_data.tasks)`
- If parser returns empty tasks list, `task_count = 0`

---

## 3. CURRENT PARSER IMPLEMENTATION ANALYSIS

### 3.1 What It Does Well

**File Handling:**
```python
if source_path.is_dir():
    source_path = source_path / "tasks.md"  # ✅ Handles directories
```

**AST-Based Parsing:**
```python
doc = Document(content)  # ✅ Uses mistletoe AST
```

**Phase Detection:**
```python
# Looks for: "## Phase N: Name" or "### Phase N: Name"
if isinstance(node, Heading) and node.level in [2, 3]:
    header_text = self._get_text_content(node)
    phase_match = re.match(r'Phase (\d+):\s*(.+)', header_text)
```

### 3.2 What It Misses

**Task Detection - THE PROBLEM:**
```python
# ONLY looks for tasks in MarkdownList nodes
def _extract_tasks_from_list(self, list_node: MarkdownList, ...):
    for item in list_node.children:
        item_text = self._get_text_content(item)
        if re.search(r'Task \d+\.\d+:', item_text):
            # Extract task...
```

**This means:**
- ✅ Works: `- [ ] **Task 1.1**: Description`
- ❌ Fails: `#### Task 1.1: Description`

**The parser never checks `Heading` nodes for tasks, only `MarkdownList` nodes!**

---

## 4. WHY DIVIO SPEC RETURNS 0 TASKS

### 4.1 Divio Spec Format
```markdown
### Phase 1: Foundation & Infrastructure

**Objective:** Establish directory structure...

**Estimated Duration:** 4-6 hours

#### Task 1.1: Reorganize Directory Structure

- [ ] `docs/content/tutorials/` directory created
- [ ] `docs/content/how-to-guides/` directory created
...
```

### 4.2 Parser Behavior

1. **Phase detection:** ✅ WORKS
   - Finds `### Phase 1: Foundation & Infrastructure`
   - Creates DynamicPhase with phase_number=1

2. **Task detection:** ❌ FAILS
   - Parser only looks in `MarkdownList` nodes
   - `#### Task 1.1:` is a `Heading` node, not in a list
   - Parser skips it entirely

3. **Result:**
   - Returns `DynamicPhase(phase_number=1, tasks=[])`
   - Registry sees `task_count = 0`
   - User gets "Task 1 not found in phase 1"

---

## 5. PARSER CONTRACT REQUIREMENTS

### 5.1 Must Support Multiple Task Formats

**Format 1: List-Based (Current Template)**
```markdown
### Phase 1 Tasks

- [ ] **Task 1.1**: Task Name
  - **Estimated Time**: 2 hours
  - **Dependencies**: None
  
  Action items here
  
  **Acceptance Criteria:**
  - [ ] Criterion 1
  - [ ] Criterion 2
```

**Format 2: Heading-Based (Divio Spec)**
```markdown
### Phase 1: Phase Name

#### Task 1.1: Task Name

**Estimated Time:** 2 hours
**Dependencies:** None

Action items here

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
```

**Format 3: Hybrid (Real World)**
```markdown
### Phase 1: Phase Name

**Tasks:**

- [ ] **Task 1.1**: Quick task (inline)

#### Task 1.2: Complex Task

Detailed description...

**Acceptance Criteria:**
- [ ] Criterion 1
```

### 5.2 Parser Output Contract

**For EVERY task found, parser MUST populate:**
```python
DynamicTask(
    task_id="1.1",                    # REQUIRED: Extract "N.M"
    task_name="Task Name",            # REQUIRED: Extract name
    description="Full description",    # REQUIRED: Or use task_name if none
    estimated_time="2 hours",          # REQUIRED: Or "Not specified"
    dependencies=["1.1", "1.2"],       # REQUIRED: Extract or []
    acceptance_criteria=["Crit 1"],    # REQUIRED: Extract or []
)
```

---

## 6. REFACTORING STRATEGY

### 6.1 Principles
1. **Semantic Over Structural:** Identify tasks by MEANING, not FORMAT
2. **Format Agnostic:** Support headings, lists, and hybrid
3. **Defensive:** Handle missing metadata gracefully
4. **Maintainable:** Clear method separation, minimal regex

### 6.2 Key Changes Needed

**Current:**
```python
def _extract_tasks_from_list(self, list_node: MarkdownList, ...):
    # Only looks in lists
```

**Needed:**
```python
def _is_task_node(self, node) -> bool:
    """
    Semantic check: Is this node a task?
    - Heading containing "Task N.M:"
    - List item containing "**Task N.M**:"
    """

def _extract_task_from_heading(self, heading: Heading, following_nodes) -> DynamicTask:
    """Extract task when format is: #### Task 1.1: Name"""

def _extract_task_from_list_item(self, item: ListItem) -> DynamicTask:
    """Extract task when format is: - [ ] **Task 1.1**: Name"""
```

---

## 7. TEST CASES FOR VALIDATION

### 7.1 Must Parse Successfully

1. **Original Format** (list-based)
   - Source: `universal/workflows/spec_creation_v1/core/tasks-template.md`
   - Expected: All tasks extracted

2. **Divio Format** (heading-based)
   - Source: `.praxis-os/specs/2025-10-10-divio-docs-restructure/tasks.md`
   - Expected: 6 phases, 19 tasks

3. **Mixed Format**
   - Combination of list and heading tasks
   - Expected: All tasks extracted regardless of format

### 7.2 Must Handle Edge Cases

1. **Missing Metadata:**
   - Task with no estimated time → Use "Not specified"
   - Task with no dependencies → Use []
   - Task with no acceptance criteria → Use []

2. **Invalid Task IDs:**
   - "Task A.1" → Skip (not N.M format)
   - "Task 1.1.1" → Skip (not N.M format)
   - "Task 1:" → Skip (incomplete)

3. **Empty Phases:**
   - Phase with no tasks → Return empty tasks list
   - Raise error only if NO phases found

---

## 8. IMPLEMENTATION CHECKLIST

- [ ] Create semantic task detection (`_is_task_node`)
- [ ] Implement heading-based task extraction
- [ ] Implement list-based task extraction  
- [ ] Unified metadata extraction (time, deps, criteria)
- [ ] Handle missing/malformed metadata gracefully
- [ ] Test against list-based format (original)
- [ ] Test against heading-based format (Divio)
- [ ] Test against hybrid format
- [ ] Verify all DynamicTask fields populated
- [ ] Verify phase numbers are >= 1
- [ ] Run existing tests (if any)
- [ ] Document format support in docstring

---

## 9. SUCCESS CRITERIA

**Parser refactor is successful when:**

1. ✅ Divio spec returns 19 tasks (not 0)
2. ✅ Original template format still works
3. ✅ All existing specs can be parsed
4. ✅ No breaking changes to contracts
5. ✅ Error messages are clear
6. ✅ Code is maintainable (no complex regex)

