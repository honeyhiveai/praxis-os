# Parser Refactor Design: Semantic AST-Based Parsing
**Date:** 2025-10-12  
**Author:** AI Assistant  
**Status:** Design Review

---

## 1. DESIGN PHILOSOPHY

### 1.1 Core Principle: Semantic Over Structural

**Current Approach (Structural):**
```python
# Looks for specific markdown structure
if isinstance(node, MarkdownList):
    if isinstance(item, ListItem):
        if re.search(r'Task \d+\.\d+:', text):
            # Extract task
```
**Problem:** Rigid, fails when format changes

**New Approach (Semantic):**
```python
# Understands what content MEANS
if self._semantically_represents_task(node):
    task = self._extract_task_semantic(node)
```
**Benefit:** Works with any reasonable format

### 1.2 Semantic Task Definition

A node semantically represents a task if:
1. Contains text pattern "Task N.M" where N and M are digits
2. Has a colon after the task ID: "Task N.M:"
3. Has task name/description after the colon

**Key Insight:** The MEANING is consistent across formats, only STRUCTURE varies.

---

## 2. MISTLETOE AST STRUCTURE ANALYSIS

### 2.1 List-Based Task Format

**Markdown:**
```markdown
- [ ] **Task 1.1**: Create Models
  - **Estimated Time**: 2 hours
  - **Dependencies**: None
  
  Additional description...
  
  **Acceptance Criteria:**
  - [ ] Criterion 1
```

**AST Structure:**
```
MarkdownList
├── ListItem ("- [ ] **Task 1.1**: Create Models")
│   ├── Strong("Task 1.1")
│   └── RawText(": Create Models")
├── ListItem ("  - **Estimated Time**: 2 hours")
│   └── [nested metadata]
└── ...
```

### 2.2 Heading-Based Task Format

**Markdown:**
```markdown
#### Task 1.1: Create Models

**Estimated Time:** 2 hours

Additional description...

**Acceptance Criteria:**
- [ ] Criterion 1
```

**AST Structure:**
```
Heading (level=4, "Task 1.1: Create Models")
├── RawText("Task 1.1: Create Models")

Paragraph ("**Estimated Time:** 2 hours")
├── Strong("Estimated Time:")
├── RawText(" 2 hours")

Paragraph ("Additional description...")

Heading (level=5, "**Acceptance Criteria:**") OR Paragraph
├── Strong("Acceptance Criteria:")

MarkdownList
├── ListItem("Criterion 1")
```

### 2.3 Key Observations

1. **Task ID always in text content** - Whether in Heading or ListItem
2. **Metadata follows consistent patterns** - `**Label:** Value`
3. **Acceptance criteria always in a list** - Structure is consistent
4. **Content grouping differs** - Heading tasks have "following nodes", List tasks have "nested nodes"

---

## 3. SEMANTIC PARSING STRATEGY

### 3.1 Two-Phase Approach

**Phase 1: Semantic Detection**
- Traverse AST identifying task nodes by meaning
- Don't extract yet, just mark positions

**Phase 2: Context-Aware Extraction**
- For each task node, gather associated content
- Extract based on detected format
- Apply semantic metadata extraction

### 3.2 Format Detection Pattern

```python
def _detect_task_format(self, node) -> Optional[str]:
    """
    Detect if node semantically represents a task.
    
    Returns:
        "heading" - Task in heading format (#### Task 1.1:)
        "list" - Task in list format (- [ ] **Task 1.1**:)
        None - Not a task
    """
    text = self._get_text_from_node(node)
    
    # Semantic check: contains "Task" followed by N.M pattern
    if not self._contains_task_pattern(text):
        return None
    
    # Determine format by node type
    if isinstance(node, Heading):
        return "heading"
    elif isinstance(node, ListItem):
        parent = self._get_parent(node)
        if isinstance(parent, MarkdownList):
            return "list"
    
    return None
```

---

## 4. DETAILED DESIGN

### 4.1 Class Structure

```python
class SpecTasksParser(SourceParser):
    """
    Semantic AST-based parser for spec tasks.md files.
    
    DESIGN: Semantic understanding over pattern matching
    - Identifies tasks by meaning, not structure
    - Supports heading-based and list-based formats
    - Uses native Python string operations (no complex regex)
    - Leverages mistletoe AST for robustness
    """
    
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """Main entry point - unchanged signature"""
        
    # === PHASE-LEVEL METHODS ===
    
    def _extract_phases(self, doc: Document) -> List[DynamicPhase]:
        """Extract all phases from document"""
    
    def _is_phase_heading(self, node) -> bool:
        """Semantic: Does this heading represent a phase?"""
    
    def _extract_phase_info(self, heading: Heading) -> Dict[str, Any]:
        """Extract phase number and name from heading"""
    
    def _gather_phase_content(self, start_idx: int, nodes: List) -> List:
        """Gather all nodes until next phase"""
    
    # === TASK-LEVEL METHODS ===
    
    def _extract_tasks(self, phase_nodes: List, phase_num: int) -> List[DynamicTask]:
        """Extract all tasks from phase content"""
    
    def _detect_task_format(self, node) -> Optional[str]:
        """Semantic: Is this a task? What format?"""
    
    def _extract_heading_task(
        self, 
        heading: Heading, 
        following_nodes: List,
        phase_num: int
    ) -> DynamicTask:
        """Extract task in heading format"""
    
    def _extract_list_task(
        self, 
        list_item: ListItem,
        phase_num: int
    ) -> DynamicTask:
        """Extract task in list format"""
    
    # === METADATA EXTRACTION (SEMANTIC) ===
    
    def _extract_task_id(self, text: str) -> Optional[str]:
        """Semantic: Find "N.M" pattern in text"""
    
    def _extract_task_name(self, text: str, task_id: str) -> str:
        """Semantic: Extract name after "Task N.M:"""""
    
    def _extract_estimated_time(self, nodes: List) -> str:
        """Semantic: Find time in various formats"""
    
    def _extract_dependencies(self, nodes: List) -> List[str]:
        """Semantic: Find dependency references"""
    
    def _extract_acceptance_criteria(self, nodes: List) -> List[str]:
        """Semantic: Find criteria checklist"""
    
    def _build_description(self, nodes: List) -> str:
        """Semantic: Combine relevant content into description"""
    
    # === UTILITY METHODS ===
    
    def _get_text_from_node(self, node) -> str:
        """Extract all text content from node recursively"""
    
    def _contains_task_pattern(self, text: str) -> bool:
        """Semantic: Does text contain "Task N.M"?"""
    
    def _find_metadata_value(self, nodes: List, label: str) -> Optional[str]:
        """Semantic: Find value for metadata label"""
```

### 4.2 Core Algorithm: Phase Extraction

```python
def _extract_phases(self, doc: Document) -> List[DynamicPhase]:
    """
    1. Traverse document nodes
    2. Identify phase headings semantically
    3. Gather content between phases
    4. Extract tasks from each phase's content
    5. Build DynamicPhase objects
    """
    phases = []
    nodes = doc.children
    i = 0
    
    while i < len(nodes):
        node = nodes[i]
        
        # Semantic check: Is this a phase?
        if self._is_phase_heading(node):
            # Extract phase metadata
            phase_info = self._extract_phase_info(node)
            
            # Gather all content until next phase
            phase_content = self._gather_phase_content(i + 1, nodes)
            
            # Extract tasks from content
            tasks = self._extract_tasks(phase_content, phase_info['phase_number'])
            
            # Extract validation gates
            validation_gate = self._extract_validation_gates(phase_content)
            
            # Build phase object
            phase = DynamicPhase(
                phase_number=phase_info['phase_number'],
                phase_name=phase_info['phase_name'],
                description=phase_info.get('description', ''),
                estimated_duration=phase_info.get('estimated_duration', 'Variable'),
                tasks=tasks,
                validation_gate=validation_gate
            )
            phases.append(phase)
            
            # Skip to next phase
            i += len(phase_content) + 1
        else:
            i += 1
    
    return phases
```

### 4.3 Core Algorithm: Task Extraction

```python
def _extract_tasks(self, phase_nodes: List, phase_num: int) -> List[DynamicTask]:
    """
    Semantic extraction with format detection.
    
    Strategy:
    1. Scan nodes for task signatures
    2. Detect format (heading vs list)
    3. Extract based on format
    4. Handle missing metadata gracefully
    """
    tasks = []
    i = 0
    
    while i < len(phase_nodes):
        node = phase_nodes[i]
        task_format = self._detect_task_format(node)
        
        if task_format == "heading":
            # Gather following nodes for this task
            task_nodes = self._gather_task_nodes(i + 1, phase_nodes)
            task = self._extract_heading_task(node, task_nodes, phase_num)
            tasks.append(task)
            i += len(task_nodes) + 1
            
        elif task_format == "list":
            # List tasks are self-contained
            task = self._extract_list_task(node, phase_num)
            tasks.append(task)
            i += 1
            
        else:
            i += 1
    
    return tasks
```

### 4.4 Semantic Pattern Matching Examples

**Task ID Extraction (Native String Ops):**
```python
def _extract_task_id(self, text: str) -> Optional[str]:
    """
    Semantic: Find "N.M" pattern after "Task" keyword.
    Uses native string operations for clarity and speed.
    """
    # Find "Task" keyword
    if "Task" not in text:
        return None
    
    # Extract portion after "Task"
    after_task = text.split("Task", 1)[1]
    
    # Get first word (should be ID)
    words = after_task.strip().split()
    if not words:
        return None
    
    first_word = words[0]
    
    # Clean punctuation
    task_id = first_word.rstrip(':').rstrip('*').strip()
    
    # Validate format: "N.M"
    if '.' in task_id:
        parts = task_id.split('.')
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            return task_id
    
    return None
```

**Estimated Time Extraction (Semantic Search):**
```python
def _extract_estimated_time(self, nodes: List) -> str:
    """
    Semantic: Find time estimate in various formats.
    
    Patterns:
    - "**Estimated Time**: 2 hours"
    - "**Estimated Time:** 2 hours"  
    - "Estimated Time: 2 hours"
    - Inline in task description
    """
    # Check common labels
    time_value = self._find_metadata_value(
        nodes, 
        labels=["Estimated Time", "Time Estimate", "Duration"]
    )
    
    if time_value:
        return time_value.strip()
    
    # Default if not found
    return "Not specified"
```

**Acceptance Criteria Extraction (Structural + Semantic):**
```python
def _extract_acceptance_criteria(self, nodes: List) -> List[str]:
    """
    Semantic: Find criteria section, then extract list items.
    
    Strategy:
    1. Find heading/paragraph with "Acceptance Criteria"
    2. Find next list after that marker
    3. Extract all list items
    """
    criteria = []
    found_marker = False
    
    for node in nodes:
        text = self._get_text_from_node(node)
        
        # Semantic marker detection
        if "Acceptance Criteria" in text or "Criteria" in text:
            found_marker = True
            continue
        
        # After marker, get first list
        if found_marker and isinstance(node, MarkdownList):
            criteria = self._extract_list_items(node)
            break
    
    return criteria
```

---

## 5. HANDLING EDGE CASES

### 5.1 Missing Metadata Strategy

**Problem:** Not all tasks have all metadata fields.

**Solution:** Defensive defaults
```python
def _extract_heading_task(self, heading, following_nodes, phase_num):
    task_id = self._extract_task_id(text)
    if not task_id:
        # Skip invalid tasks
        return None
    
    task_name = self._extract_task_name(text, task_id)
    
    # Defensive extraction with defaults
    estimated_time = self._extract_estimated_time(following_nodes) or "Not specified"
    dependencies = self._extract_dependencies(following_nodes) or []
    acceptance_criteria = self._extract_acceptance_criteria(following_nodes) or []
    description = self._build_description(following_nodes) or task_name
    
    return DynamicTask(
        task_id=task_id,
        task_name=task_name,
        description=description,
        estimated_time=estimated_time,
        dependencies=dependencies,
        acceptance_criteria=acceptance_criteria
    )
```

### 5.2 Malformed Task IDs

**Problem:** Text contains "Task" but not in valid format.

**Solution:** Strict validation
```python
# Valid: "Task 1.1", "Task 2.3"
# Invalid: "Task A.1", "Task 1.1.1", "Task 1"

if '.' not in task_id:
    return None  # Skip
if not all(part.isdigit() for part in task_id.split('.')):
    return None  # Skip
if len(task_id.split('.')) != 2:
    return None  # Skip
```

### 5.3 Nested Lists

**Problem:** Acceptance criteria vs task details.

**Solution:** Context-aware extraction
```python
def _extract_acceptance_criteria(self, nodes):
    # Only extract list AFTER "Acceptance Criteria" marker
    # Ignore lists before marker (those are task details)
    
    found_marker = False
    for node in nodes:
        if "Acceptance Criteria" in self._get_text_from_node(node):
            found_marker = True
        elif found_marker and isinstance(node, MarkdownList):
            return self._extract_list_items(node)
    return []
```

---

## 6. PERFORMANCE CONSIDERATIONS

### 6.1 Optimization Strategy

**Single-Pass Parsing:**
- Traverse document once
- Build phase and task structures incrementally
- No backtracking or re-parsing

**Lazy Text Extraction:**
```python
def _get_text_from_node(self, node) -> str:
    """Extract text only when needed, cache if used multiple times"""
    if hasattr(node, '_cached_text'):
        return node._cached_text
    
    text = self._extract_text_recursive(node)
    node._cached_text = text
    return text
```

**String Operations Over Regex:**
- Use `str.split()`, `str.find()`, `in` operator
- Only use regex for complex patterns (if any)
- Native string ops are faster and more readable

### 6.2 Complexity Analysis

- **Time:** O(n) where n = total nodes in AST
- **Space:** O(p * t) where p = phases, t = avg tasks per phase
- **Typical file:** ~500 nodes, <5ms parse time

---

## 7. ERROR HANDLING STRATEGY

### 7.1 Error Hierarchy

```python
ParseError
├── "Source file not found"          # File system error
├── "Failed to parse markdown"       # Mistletoe error
└── "No phases found"                # Empty result
```

**Key Decision:** Don't fail on malformed individual tasks
```python
# If task extraction fails, log and skip
try:
    task = self._extract_heading_task(...)
    if task:  # Valid task
        tasks.append(task)
except Exception as e:
    logger.warning(f"Skipped malformed task: {e}")
    # Continue parsing other tasks
```

### 7.2 Validation Points

1. **File Level:** Source exists and readable
2. **Parse Level:** Mistletoe can parse markdown
3. **Phase Level:** At least one phase found
4. **Task Level:** Task has valid ID (others can be defaults)

---

## 8. TESTING STRATEGY

### 8.1 Unit Tests

**Test Input Variations:**
```python
def test_task_id_extraction():
    assert _extract_task_id("Task 1.1: Name") == "1.1"
    assert _extract_task_id("**Task 1.1**: Name") == "1.1"
    assert _extract_task_id("#### Task 1.1: Name") == "1.1"
    assert _extract_task_id("Task A.1") is None
    assert _extract_task_id("Task 1.1.1") is None

def test_heading_task_format():
    markdown = "#### Task 1.1: Create Models\n\n**Estimated Time:** 2h"
    doc = Document(markdown)
    tasks = parser._extract_tasks(doc.children, phase_num=1)
    assert len(tasks) == 1
    assert tasks[0].task_id == "1.1"
    assert tasks[0].estimated_time == "2h"

def test_list_task_format():
    markdown = "- [ ] **Task 1.1**: Create Models\n  - **Estimated Time**: 2h"
    doc = Document(markdown)
    tasks = parser._extract_tasks(doc.children, phase_num=1)
    assert len(tasks) == 1
    assert tasks[0].task_id == "1.1"
```

### 8.2 Integration Tests

**Test Against Real Specs:**
```python
def test_divio_spec_parsing():
    """Heading-based format"""
    parser = SpecTasksParser()
    phases = parser.parse(Path(".agent-os/specs/2025-10-10-divio-docs-restructure"))
    
    assert len(phases) == 6
    assert sum(len(p.tasks) for p in phases) == 19
    assert phases[0].phase_number == 1
    assert phases[0].tasks[0].task_id == "1.1"

def test_template_format_parsing():
    """List-based format from template"""
    parser = SpecTasksParser()
    # Create temp file with template format
    phases = parser.parse(temp_path)
    
    assert len(phases) > 0
    assert all(len(p.tasks) > 0 for p in phases)
```

---

## 9. MIGRATION PLAN

### 9.1 Implementation Steps

1. **Implement core semantic methods** (3 hours)
   - `_extract_task_id()` with native string ops
   - `_detect_task_format()` for both formats
   - `_get_text_from_node()` recursive extractor

2. **Implement heading task extraction** (2 hours)
   - `_extract_heading_task()`
   - `_gather_task_nodes()`
   - Test against Divio spec

3. **Implement list task extraction** (2 hours)
   - `_extract_list_task()`
   - Test against template format

4. **Implement metadata extraction** (2 hours)
   - `_extract_estimated_time()`
   - `_extract_dependencies()`
   - `_extract_acceptance_criteria()`

5. **Integration and testing** (2 hours)
   - Test all existing specs
   - Verify contracts met
   - Performance validation

6. **Deploy and validate** (1 hour)
   - Clear caches
   - Restart server
   - Test live workflow

### 9.2 Rollback Plan

**If refactor fails:**
```bash
cd .agent-os
git restore mcp_server/core/parsers.py
pkill -9 -f "Python.*mcp_server"
# Restart Cursor
```

**Success Criteria:**
- ✅ Divio spec parses: 6 phases, 19 tasks
- ✅ Template format still works
- ✅ No breaking changes to contracts
- ✅ All 12 existing specs parse successfully

---

## 10. CODE QUALITY STANDARDS

### 10.1 Style Guidelines

- **No complex regex:** Use native string operations
- **Descriptive names:** `_extract_task_id` not `_get_id`
- **Type hints:** All method signatures annotated
- **Docstrings:** Explain WHAT and WHY, not HOW
- **Short methods:** Max 30 lines per method
- **Single responsibility:** Each method does one thing

### 10.2 Documentation Requirements

```python
def _extract_task_id(self, text: str) -> Optional[str]:
    """
    Extract task ID from text using semantic pattern matching.
    
    Semantically identifies "Task N.M" pattern where:
    - N and M are integers
    - Pattern appears after "Task" keyword
    - Format is exactly "N.M" (not N.M.O or N or M)
    
    Args:
        text: Text content that may contain task ID
        
    Returns:
        Task ID string (e.g., "1.1") or None if not found/invalid
        
    Examples:
        >>> _extract_task_id("Task 1.1: Create")
        "1.1"
        >>> _extract_task_id("**Task 2.3**: Build")
        "2.3"
        >>> _extract_task_id("Task A.1")
        None
    """
```

---

## 11. REVIEW CHECKLIST

Before implementation, verify:

- [ ] Design maintains all existing contracts
- [ ] Semantic approach is clear and maintainable
- [ ] Edge cases are handled gracefully
- [ ] Error handling is appropriate
- [ ] Testing strategy is comprehensive
- [ ] Performance is acceptable
- [ ] Code quality standards defined
- [ ] Migration plan is clear
- [ ] Rollback plan exists

---

## 12. OPEN QUESTIONS FOR REVIEW

1. **Metadata Defaults:** Are "Not specified" and `[]` appropriate defaults?
2. **Task Validation:** Should we skip invalid tasks silently or log warnings?
3. **Description Building:** How much content should go into `description` field?
4. **Performance:** Is caching text extraction necessary or premature optimization?
5. **Testing:** Should we add tests to CI/CD or manual verification only?

---

**Status:** Ready for review  
**Next Step:** Address review feedback, then implement

