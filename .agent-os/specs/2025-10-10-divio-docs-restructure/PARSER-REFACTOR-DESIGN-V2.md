# Parser Refactor Design V2: Semantic AST-Based Parsing
**Date:** 2025-10-12  
**Version:** 2.0 - Incorporates Review Feedback  
**Status:** Ready for Implementation

---

## CHANGELOG FROM V1

### Critical Fixes
1. ✅ **Fixed parent tracking** - Pass parent as parameter, no `_get_parent()` calls
2. ✅ **Defined node gathering rules** - Explicit stop conditions
3. ✅ **Detailed list task extraction** - How to handle nested content
4. ✅ **Implemented validation gates** - Complete method with 3 format support
5. ✅ **Specified description building** - Clear inclusion/exclusion rules

### Design Improvements
- Added `_traverse_with_parent()` helper for clean parent tracking
- Added position tracking for better error messages
- Clarified Phase 0 is skipped (dynamic phases start at 1)
- Removed premature text caching optimization
- Added comprehensive docstrings to all methods

---

## 1. DESIGN PHILOSOPHY

### 1.1 Semantic Over Structural

**Principle:** Identify content by MEANING, not FORMAT.

**Example:**
```python
# Instead of: "Is this a list item with bold text and colon?"
# Ask: "Does this semantically represent a task?"

def _semantically_represents_task(self, text: str) -> bool:
    """Does this text mean 'this is a task'?"""
    return (
        "Task" in text and 
        self._has_task_id_pattern(text) and 
        ":" in text
    )
```

### 1.2 Format Agnostic

Support ANY reasonable format that semantically represents:
- A phase: "Phase N: Name"
- A task: "Task N.M: Name"
- Metadata: "**Label**: Value"

---

## 2. MISTLETOE AST STRUCTURE

### 2.1 Verified API Constraints

**CRITICAL:** Mistletoe nodes do NOT have parent references.

**Verified Facts:**
```python
from mistletoe import Document
from mistletoe.block_token import Heading

doc = Document("# Test")
node = doc.children[0]

# These DO NOT exist:
# node.parent  ❌
# node.get_parent()  ❌

# Only available:
# node.children  ✅
# hasattr(node, 'children')  ✅
```

**Implication:** Must track parent during traversal, cannot query it.

### 2.2 Node Types We Handle

```python
from mistletoe.block_token import (
    Heading,           # ### or ####
    Paragraph,         # Plain text or **bold**
    List as MarkdownList,  # - [ ] or -
    ListItem,          # Individual list items
)
from mistletoe.span_token import (
    RawText,           # Plain text content
    Strong,            # **bold** text
)
```

---

## 3. CORE ALGORITHM DESIGN

### 3.1 Parent Tracking Strategy

**Solution:** Pass parent as parameter during traversal.

```python
def _traverse_with_parent(
    self, 
    nodes: List, 
    parent=None
) -> Iterator[Tuple[Any, Any]]:
    """
    Traverse AST yielding (node, parent) pairs.
    
    This solves mistletoe's lack of parent references by maintaining
    parent context during traversal.
    
    Args:
        nodes: List of AST nodes to traverse
        parent: Parent node (None for root level)
        
    Yields:
        (node, parent) tuples
        
    Example:
        for node, parent in self._traverse_with_parent(doc.children):
            if isinstance(parent, MarkdownList):
                # We know this node is inside a list
    """
    for node in nodes:
        yield (node, parent)
        
        # Recurse into children with current node as parent
        if hasattr(node, 'children') and node.children:
            yield from self._traverse_with_parent(node.children, parent=node)
```

### 3.2 Phase Extraction Algorithm

```python
def _extract_phases(self, doc: Document) -> List[DynamicPhase]:
    """
    Extract all phases from document.
    
    Algorithm:
    1. Traverse root-level nodes (not nested)
    2. Find phase headings semantically
    3. Gather content until next phase
    4. Extract tasks from phase content
    5. Build DynamicPhase objects
    
    Note: Only extracts phases with phase_number >= 1
          (Phase 0 is static in hybrid workflows)
    
    Returns:
        List[DynamicPhase] with phase_number >= 1
    """
    phases = []
    nodes = doc.children
    i = 0
    
    while i < len(nodes):
        node = nodes[i]
        
        # Check if this is a phase heading
        if self._is_phase_heading(node):
            phase_info = self._extract_phase_info(node)
            
            # Skip Phase 0 (static in hybrid workflows)
            if phase_info['phase_number'] < 1:
                i += 1
                continue
            
            # Gather content until next phase
            content_end_idx = self._find_next_phase_index(i + 1, nodes)
            phase_nodes = nodes[i + 1 : content_end_idx]
            
            # Extract tasks from this phase's content
            tasks = self._extract_tasks_from_phase(phase_nodes, phase_info['phase_number'])
            
            # Extract validation gates
            validation_gate = self._extract_validation_gates(phase_nodes)
            
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
            i = content_end_idx
        else:
            i += 1
    
    return phases
```

### 3.3 Task Extraction Algorithm

```python
def _extract_tasks_from_phase(
    self, 
    phase_nodes: List, 
    phase_num: int
) -> List[DynamicTask]:
    """
    Extract all tasks from phase content.
    
    Handles both heading-based and list-based task formats.
    Uses parent tracking to detect list tasks correctly.
    
    Algorithm:
    1. Traverse phase nodes with parent tracking
    2. Detect task format semantically
    3. For heading tasks: gather following nodes
    4. For list tasks: extract from nested content
    5. Skip invalid tasks with warning
    
    Args:
        phase_nodes: All AST nodes in this phase
        phase_num: Current phase number
        
    Returns:
        List[DynamicTask] (may be empty if no tasks)
    """
    tasks = []
    processed_indices = set()
    
    # Build flat list with indices for heading tasks
    for i, node in enumerate(phase_nodes):
        if i in processed_indices:
            continue
        
        # Check heading format
        if isinstance(node, Heading):
            text = self._get_text_from_node(node)
            if self._contains_task_pattern(text):
                try:
                    # Gather following nodes for this task
                    task_content_nodes, consumed = self._gather_task_nodes(
                        i + 1, 
                        phase_nodes
                    )
                    task = self._extract_heading_task(
                        node, 
                        task_content_nodes, 
                        phase_num
                    )
                    if task:
                        tasks.append(task)
                    
                    # Mark consumed nodes
                    for j in range(i + 1, i + 1 + consumed):
                        processed_indices.add(j)
                        
                except Exception as e:
                    logger.warning(
                        f"Skipped malformed heading task in Phase {phase_num}: {e}"
                    )
    
    # Check for list-based tasks
    for node in phase_nodes:
        if isinstance(node, MarkdownList):
            list_tasks = self._extract_list_tasks_from_list(node, phase_num)
            tasks.extend(list_tasks)
    
    return tasks
```

---

## 4. DETAILED METHOD IMPLEMENTATIONS

### 4.1 Node Gathering with Stop Rules

```python
def _gather_task_nodes(
    self, 
    start_idx: int, 
    nodes: List
) -> Tuple[List, int]:
    """
    Gather nodes belonging to a heading-based task.
    
    STOP CONDITIONS (in order of priority):
    1. Another heading at level <= 4 (task or section heading)
    2. Another task pattern detected in any node
    3. End of nodes list
    
    Args:
        start_idx: Index to start gathering from
        nodes: All nodes in current phase
        
    Returns:
        (gathered_nodes, count_consumed) tuple
        
    Example:
        #### Task 1.1: Name        ← Task heading (not included)
        Paragraph                  ← INCLUDE
        **Metadata**: value        ← INCLUDE  
        List of criteria           ← INCLUDE
        #### Task 1.2: Next        ← STOP (next task)
        
        Returns: ([Paragraph, Metadata, List], 3)
    """
    gathered = []
    
    for i in range(start_idx, len(nodes)):
        node = nodes[i]
        
        # Stop at next heading (task or section)
        if isinstance(node, Heading):
            text = self._get_text_from_node(node)
            
            # Stop at any task heading
            if self._contains_task_pattern(text):
                break
            
            # Stop at same/higher level heading
            if node.level <= 4:
                break
        
        # Stop if we hit a list with task patterns
        if isinstance(node, MarkdownList):
            if self._list_contains_task_pattern(node):
                break
        
        gathered.append(node)
    
    return gathered, len(gathered)


def _list_contains_task_pattern(self, list_node: MarkdownList) -> bool:
    """
    Check if a list contains any task declarations.
    
    Used to stop gathering when we hit a list-based task.
    
    Args:
        list_node: MarkdownList to check
        
    Returns:
        True if any list item contains "Task N.M" pattern
    """
    if not hasattr(list_node, 'children'):
        return False
    
    for item in list_node.children:
        if isinstance(item, ListItem):
            text = self._get_text_from_node(item)
            if self._contains_task_pattern(text):
                return True
    
    return False
```

### 4.2 List Task Extraction with Nested Content

```python
def _extract_list_tasks_from_list(
    self, 
    list_node: MarkdownList, 
    phase_num: int
) -> List[DynamicTask]:
    """
    Extract all tasks from a list node.
    
    Handles nested list structure where metadata is indented under task.
    
    Args:
        list_node: MarkdownList node potentially containing tasks
        phase_num: Current phase number
        
    Returns:
        List of extracted DynamicTask objects
    """
    tasks = []
    
    if not hasattr(list_node, 'children'):
        return tasks
    
    for item in list_node.children:
        if isinstance(item, ListItem):
            text = self._get_text_from_node(item)
            
            # Check if this item is a task
            if self._contains_task_pattern(text):
                try:
                    task = self._extract_list_task(item, phase_num)
                    if task:
                        tasks.append(task)
                except Exception as e:
                    logger.warning(
                        f"Skipped malformed list task in Phase {phase_num}: {e}"
                    )
    
    return tasks


def _extract_list_task(
    self, 
    list_item: ListItem, 
    phase_num: int
) -> Optional[DynamicTask]:
    """
    Extract task from list item format.
    
    Structure:
        - [ ] **Task 1.1**: Name
          - **Estimated Time**: 2 hours
          - **Dependencies**: Task 1.0
          
          Additional description paragraph
          
          **Acceptance Criteria:**
          - [ ] Criterion 1
          - [ ] Criterion 2
    
    The nested structure is in list_item.children as:
    - Nested MarkdownList (contains metadata items)
    - Nested Paragraph (contains description)
    
    Args:
        list_item: ListItem node containing task
        phase_num: Current phase number
        
    Returns:
        DynamicTask object or None if invalid
    """
    # Extract from main item text
    item_text = self._get_text_from_node(list_item)
    task_id = self._extract_task_id(item_text)
    
    if not task_id:
        return None
    
    task_name = self._extract_task_name(item_text, task_id)
    
    # Gather nested content
    nested_nodes = []
    if hasattr(list_item, 'children') and list_item.children:
        for child in list_item.children:
            if isinstance(child, MarkdownList):
                # Nested list contains metadata items
                if hasattr(child, 'children'):
                    nested_nodes.extend(child.children)
            elif isinstance(child, Paragraph):
                # Paragraph contains description
                nested_nodes.append(child)
            else:
                # Include other content
                nested_nodes.append(child)
    
    # Extract metadata from nested content
    estimated_time = self._extract_estimated_time(nested_nodes)
    dependencies = self._extract_dependencies(nested_nodes)
    acceptance_criteria = self._extract_acceptance_criteria(nested_nodes)
    description = self._build_description(nested_nodes)
    
    # Use task_name as fallback description
    if not description:
        description = task_name
    
    return DynamicTask(
        task_id=task_id,
        task_name=task_name,
        description=description,
        estimated_time=estimated_time,
        dependencies=dependencies,
        acceptance_criteria=acceptance_criteria
    )
```

### 4.3 Validation Gates Extraction

```python
def _extract_validation_gates(self, phase_nodes: List) -> List[str]:
    """
    Extract validation gate criteria from phase content.
    
    Supports three formats:
    
    Format 1 - List after heading:
        **Validation Gate:**
        - [ ] Criterion 1
        - [ ] Criterion 2
    
    Format 2 - Inline text:
        **Validation Gate:** All tasks complete, tests passing
    
    Format 3 - Dedicated section:
        #### Validation Gate
        Criteria:
        - [ ] Complete
    
    Strategy:
    1. Find "Validation Gate" marker
    2. Check for inline text (same line after colon)
    3. Otherwise, find next list
    4. Extract list items as criteria
    
    Args:
        phase_nodes: All nodes in current phase
        
    Returns:
        List of validation criteria strings (may be empty)
    """
    criteria = []
    found_marker = False
    marker_node_idx = None
    
    for i, node in enumerate(phase_nodes):
        text = self._get_text_from_node(node)
        
        # Find validation gate marker
        if "Validation Gate" in text:
            found_marker = True
            marker_node_idx = i
            
            # Check for inline format: "**Validation Gate:** criteria"
            if ":" in text:
                after_colon = text.split("Validation Gate:", 1)[1].strip()
                if after_colon and not after_colon.startswith("\n"):
                    # Inline format - split on comma
                    inline_criteria = [c.strip() for c in after_colon.split(",")]
                    return [c for c in inline_criteria if c]
            
            # Not inline, continue to find list
            continue
        
        # After marker, look for list
        if found_marker:
            if isinstance(node, MarkdownList):
                criteria = self._extract_list_items(node)
                break
            
            # Stop if we hit another heading
            if isinstance(node, Heading):
                break
    
    return criteria


def _extract_list_items(self, list_node: MarkdownList) -> List[str]:
    """
    Extract text from all items in a list.
    
    Cleans checkbox markers and formatting.
    
    Args:
        list_node: MarkdownList node
        
    Returns:
        List of cleaned item texts
    """
    items = []
    
    if not hasattr(list_node, 'children') or not list_node.children:
        return items
    
    for item in list_node.children:
        if isinstance(item, ListItem):
            text = self._get_text_from_node(item)
            
            # Clean checkbox markers
            text = text.replace("- [ ]", "").replace("- [x]", "").replace("- [X]", "")
            text = text.strip()
            
            if text:
                items.append(text)
    
    return items
```

### 4.4 Description Building

```python
def _build_description(self, nodes: List) -> str:
    """
    Build task description from content nodes.
    
    INCLUSION RULES:
    1. Include: Paragraph nodes
    2. Exclude: Nodes with metadata patterns
    3. Stop: At "Acceptance Criteria" marker
    4. Clean: Remove bold markers from description
    
    METADATA PATTERNS TO EXCLUDE:
    - "**Estimated Time"
    - "**Dependencies"
    - "**Acceptance Criteria"
    - "**Validation Gate"
    - "**Human Baseline"
    - "**Agent OS"
    
    Args:
        nodes: Task content nodes
        
    Returns:
        Combined description text (empty string if none)
        
    Example:
        Input nodes:
            Paragraph("This task creates the models")
            Paragraph("**Estimated Time**: 2h")
            Paragraph("Implementation details here")
            Paragraph("**Acceptance Criteria:**")
            List(...)
        
        Returns: "This task creates the models\n\nImplementation details here"
    """
    description_parts = []
    
    # Metadata patterns to exclude
    metadata_markers = [
        "Estimated Time",
        "Dependencies",
        "Acceptance Criteria",
        "Validation Gate",
        "Human Baseline",
        "Agent OS",
    ]
    
    for node in nodes:
        if not isinstance(node, Paragraph):
            continue
        
        text = self._get_text_from_node(node)
        
        # Stop at acceptance criteria
        if "Acceptance Criteria" in text:
            break
        
        # Skip metadata lines
        if any(marker in text for marker in metadata_markers):
            continue
        
        # Skip if it starts with bold marker (likely metadata)
        if text.strip().startswith("**") and ":" in text[:50]:
            continue
        
        # Include this paragraph
        cleaned = text.strip()
        if cleaned:
            description_parts.append(cleaned)
    
    # Combine with double newline (markdown paragraph spacing)
    description = "\n\n".join(description_parts)
    
    return description
```

### 4.5 Metadata Extraction Methods

```python
def _extract_estimated_time(self, nodes: List) -> str:
    """
    Extract estimated time from nodes.
    
    Looks for patterns:
    - "**Estimated Time**: 2 hours"
    - "**Estimated Time:** 2 hours"
    - "Estimated Time: 2 hours"
    
    Args:
        nodes: Content nodes to search
        
    Returns:
        Time string or "Not specified"
    """
    time_labels = ["Estimated Time", "Time Estimate", "Duration"]
    
    for node in nodes:
        text = self._get_text_from_node(node)
        
        for label in time_labels:
            if label in text and ":" in text:
                # Extract value after colon
                parts = text.split(label, 1)[1]
                if ":" in parts:
                    value = parts.split(":", 1)[1].strip()
                    # Clean up formatting
                    value = value.replace("**", "").split("\n")[0].strip()
                    if value:
                        return value
    
    return "Not specified"


def _extract_dependencies(self, nodes: List) -> List[str]:
    """
    Extract task dependencies from nodes.
    
    Looks for patterns:
    - "**Dependencies**: Task 1.1, Task 1.2"
    - "**Dependencies:** None"
    - References to "Task N.M" or "Phase N"
    
    Args:
        nodes: Content nodes to search
        
    Returns:
        List of dependency strings (may be empty)
    """
    dependencies = []
    
    for node in nodes:
        text = self._get_text_from_node(node)
        
        if "Dependencies" in text or "Depends on" in text:
            # Extract after colon
            if ":" in text:
                after_colon = text.split(":", 1)[1]
                
                # Check for "None"
                if "None" in after_colon or "none" in after_colon:
                    return []
                
                # Extract Task N.M patterns
                # Use simple string search, not regex
                words = after_colon.split()
                for i, word in enumerate(words):
                    if word == "Task" and i + 1 < len(words):
                        # Next word might be "N.M"
                        task_id = words[i + 1].rstrip(',').rstrip('.')
                        if '.' in task_id:
                            parts = task_id.split('.')
                            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                                dependencies.append(f"Task {task_id}")
                    elif word == "Phase" and i + 1 < len(words):
                        phase_num = words[i + 1].rstrip(',').rstrip('.')
                        if phase_num.isdigit():
                            dependencies.append(f"Phase {phase_num}")
    
    return dependencies


def _extract_acceptance_criteria(self, nodes: List) -> List[str]:
    """
    Extract acceptance criteria from nodes.
    
    Strategy:
    1. Find "Acceptance Criteria" marker
    2. Get next list after marker
    3. Extract list items
    
    Args:
        nodes: Content nodes to search
        
    Returns:
        List of criteria strings (may be empty)
    """
    criteria = []
    found_marker = False
    
    for node in nodes:
        text = self._get_text_from_node(node)
        
        # Find acceptance criteria marker
        if "Acceptance Criteria" in text:
            found_marker = True
            continue
        
        # After marker, get first list
        if found_marker and isinstance(node, MarkdownList):
            criteria = self._extract_list_items(node)
            break
    
    return criteria
```

### 4.6 Semantic Pattern Detection

```python
def _extract_task_id(self, text: str) -> Optional[str]:
    """
    Extract task ID from text using semantic pattern matching.
    
    Semantic pattern: "Task N.M" where N and M are integers.
    
    Uses native string operations for clarity and performance.
    
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
        >>> _extract_task_id("Task 1.1.1: Too many parts")
        None
    """
    # Must contain "Task"
    if "Task" not in text:
        return None
    
    # Extract portion after "Task"
    after_task = text.split("Task", 1)[1].strip()
    
    # Get first word (should be the ID)
    words = after_task.split()
    if not words:
        return None
    
    first_word = words[0]
    
    # Clean punctuation: "1.1:" -> "1.1", "**1.1**:" -> "1.1"
    task_id = first_word.rstrip(':').rstrip('*').strip()
    
    # Validate format: must be "N.M"
    if '.' not in task_id:
        return None
    
    parts = task_id.split('.')
    if len(parts) != 2:
        return None
    
    if not (parts[0].isdigit() and parts[1].isdigit()):
        return None
    
    return task_id


def _extract_task_name(self, text: str, task_id: str) -> str:
    """
    Extract task name from text.
    
    Strategy:
    1. Find "Task {task_id}:" pattern
    2. Extract text after colon
    3. Clean formatting (bold, etc.)
    4. Return first line as name
    
    Args:
        text: Text containing task declaration
        task_id: Already extracted task ID
        
    Returns:
        Task name string
        
    Examples:
        >>> _extract_task_name("Task 1.1: Create Models", "1.1")
        "Create Models"
        >>> _extract_task_name("**Task 1.1**: Create Models", "1.1")
        "Create Models"
    """
    # Find marker
    marker = f"Task {task_id}:"
    if marker not in text:
        # Try with bold
        marker = f"**Task {task_id}**:"
    
    if marker not in text:
        return f"Task {task_id}"
    
    # Extract after marker
    after_marker = text.split(marker, 1)[1]
    
    # Get first line
    first_line = after_marker.split("\n")[0].strip()
    
    # Clean formatting
    first_line = first_line.replace("**", "").replace("*", "").strip()
    
    return first_line if first_line else f"Task {task_id}"


def _contains_task_pattern(self, text: str) -> bool:
    """
    Semantic check: Does text contain a task declaration?
    
    A task declaration has:
    - The word "Task"
    - Format "N.M" where N and M are digits
    
    Args:
        text: Text to check
        
    Returns:
        True if contains task pattern
    """
    if "Task" not in text:
        return False
    
    # Try to extract task ID
    task_id = self._extract_task_id(text)
    return task_id is not None
```

### 4.7 Utility Methods

```python
def _get_text_from_node(self, node) -> str:
    """
    Recursively extract all text content from an AST node.
    
    Handles:
    - RawText nodes (leaf text)
    - Strong nodes (bold **text**)
    - Nested structures (paragraphs with bold, etc.)
    
    Args:
        node: AST node (any type)
        
    Returns:
        Extracted text content
    """
    if node is None:
        return ''
    
    # Leaf text node
    if isinstance(node, RawText):
        return node.content if hasattr(node, 'content') else str(node)
    
    # String nodes
    if isinstance(node, str):
        return node
    
    # Strong (bold) - preserve markers for metadata detection
    if isinstance(node, Strong):
        if hasattr(node, 'children') and node.children:
            inner = ''.join(self._get_text_from_node(c) for c in node.children)
            return f"**{inner}**"
        return ''
    
    # Recurse into children
    if hasattr(node, 'children') and node.children:
        return ''.join(self._get_text_from_node(c) for c in node.children)
    
    return ''


def _is_phase_heading(self, node) -> bool:
    """
    Semantic check: Does this heading represent a phase?
    
    A phase heading:
    - Is a Heading node (level 2 or 3 typically)
    - Contains "Phase"
    - Contains a number
    - Has format "Phase N: Name"
    
    Args:
        node: AST node to check
        
    Returns:
        True if this is a phase heading
    """
    if not isinstance(node, Heading):
        return False
    
    text = self._get_text_from_node(node)
    
    # Must contain "Phase" and colon
    if "Phase" not in text or ":" not in text:
        return False
    
    # Must have a digit
    return any(char.isdigit() for char in text.split(":")[0])


def _extract_phase_info(self, heading: Heading) -> Dict[str, Any]:
    """
    Extract phase number and name from heading.
    
    Args:
        heading: Heading node containing phase declaration
        
    Returns:
        Dict with phase_number and phase_name
    """
    text = self._get_text_from_node(heading)
    
    # Split on colon
    parts = text.split(":", 1)
    phase_part = parts[0].strip()
    phase_name = parts[1].strip() if len(parts) > 1 else "Unknown"
    
    # Extract number from phase part
    digits = ''.join(char for char in phase_part if char.isdigit())
    phase_number = int(digits) if digits else 0
    
    return {
        'phase_number': phase_number,
        'phase_name': phase_name,
    }


def _find_next_phase_index(self, start_idx: int, nodes: List) -> int:
    """
    Find the index of the next phase heading.
    
    Args:
        start_idx: Index to start searching from
        nodes: All nodes to search
        
    Returns:
        Index of next phase or len(nodes) if no more phases
    """
    for i in range(start_idx, len(nodes)):
        if self._is_phase_heading(nodes[i]):
            return i
    
    return len(nodes)
```

---

## 5. COMPLETE CLASS STRUCTURE

```python
class SpecTasksParser(SourceParser):
    """
    Semantic AST-based parser for Agent OS spec tasks.md files.
    
    DESIGN: Semantic understanding over pattern matching
    - Identifies content by meaning, not structure
    - Supports heading-based and list-based task formats
    - Uses native Python string operations (no complex regex)
    - Handles mistletoe AST constraints (no parent references)
    
    Supports formats:
    - Heading tasks: #### Task 1.1: Name
    - List tasks: - [ ] **Task 1.1**: Name
    - Mixed formats in same file
    
    Contract:
    - Returns List[DynamicPhase] with phase_number >= 1
    - All DynamicTask fields populated (uses defaults for missing)
    - Raises ParseError only for file/parse failures
    - Logs warnings for malformed individual tasks
    """
    
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """Main entry point - see Section 3.2"""
        
    # === TRAVERSAL ===
    def _traverse_with_parent(self, nodes, parent=None):
        """Yield (node, parent) pairs - see Section 3.1"""
    
    # === PHASE EXTRACTION ===
    def _extract_phases(self, doc: Document) -> List[DynamicPhase]:
        """Extract all phases - see Section 3.2"""
    
    def _is_phase_heading(self, node) -> bool:
        """Semantic phase detection - see Section 4.7"""
    
    def _extract_phase_info(self, heading) -> Dict[str, Any]:
        """Extract phase metadata - see Section 4.7"""
    
    def _find_next_phase_index(self, start_idx, nodes) -> int:
        """Find next phase boundary - see Section 4.7"""
    
    # === TASK EXTRACTION ===
    def _extract_tasks_from_phase(self, phase_nodes, phase_num) -> List[DynamicTask]:
        """Extract all tasks from phase - see Section 3.3"""
    
    def _gather_task_nodes(self, start_idx, nodes) -> Tuple[List, int]:
        """Gather heading task content - see Section 4.1"""
    
    def _extract_heading_task(self, heading, nodes, phase_num) -> Optional[DynamicTask]:
        """Extract heading format task - see Section 4.2"""
    
    def _extract_list_tasks_from_list(self, list_node, phase_num) -> List[DynamicTask]:
        """Extract all tasks from list - see Section 4.2"""
    
    def _extract_list_task(self, list_item, phase_num) -> Optional[DynamicTask]:
        """Extract single list task - see Section 4.2"""
    
    # === METADATA EXTRACTION ===
    def _extract_task_id(self, text) -> Optional[str]:
        """Semantic task ID extraction - see Section 4.6"""
    
    def _extract_task_name(self, text, task_id) -> str:
        """Extract task name - see Section 4.6"""
    
    def _extract_estimated_time(self, nodes) -> str:
        """Extract time estimate - see Section 4.5"""
    
    def _extract_dependencies(self, nodes) -> List[str]:
        """Extract dependencies - see Section 4.5"""
    
    def _extract_acceptance_criteria(self, nodes) -> List[str]:
        """Extract criteria - see Section 4.5"""
    
    def _extract_validation_gates(self, nodes) -> List[str]:
        """Extract validation gates - see Section 4.3"""
    
    def _build_description(self, nodes) -> str:
        """Build description - see Section 4.4"""
    
    # === UTILITIES ===
    def _get_text_from_node(self, node) -> str:
        """Recursive text extraction - see Section 4.7"""
    
    def _contains_task_pattern(self, text) -> bool:
        """Semantic task detection - see Section 4.6"""
    
    def _list_contains_task_pattern(self, list_node) -> bool:
        """Check if list has tasks - see Section 4.1"""
    
    def _extract_list_items(self, list_node) -> List[str]:
        """Extract list item texts - see Section 4.3"""
```

---

## 6. ERROR HANDLING

### 6.1 Error Hierarchy

```python
ParseError
├── "Source file not found: {path}"
├── "tasks.md not found in directory: {path}"
├── "Failed to read {path}: {error}"
├── "Source file is empty: {path}"
├── "Failed to parse markdown: {error}"
└── "No phases found in {path}"
```

### 6.2 Graceful Degradation

```python
# Phase level: Fail fast
if not phases:
    raise ParseError(f"No phases found in {source_path}")

# Task level: Log and continue
try:
    task = self._extract_heading_task(...)
    if task:
        tasks.append(task)
except Exception as e:
    logger.warning(
        f"Skipped malformed task in Phase {phase_num}: {e}"
    )
    # Continue processing other tasks
```

---

## 7. TESTING STRATEGY

### 7.1 Unit Tests

```python
# Test task ID extraction
def test_extract_task_id_formats():
    parser = SpecTasksParser()
    assert parser._extract_task_id("Task 1.1: Name") == "1.1"
    assert parser._extract_task_id("**Task 2.3**: Name") == "2.3"
    assert parser._extract_task_id("#### Task 1.1: Name") == "1.1"
    assert parser._extract_task_id("Task A.1") is None
    assert parser._extract_task_id("Task 1.1.1") is None
    assert parser._extract_task_id("Task 1") is None

# Test format detection
def test_heading_task_extraction():
    markdown = """
    ### Phase 1: Test
    
    #### Task 1.1: Create Models
    
    **Estimated Time:** 2 hours
    
    **Acceptance Criteria:**
    - [ ] Models created
    """
    parser = SpecTasksParser()
    phases = parser.parse_from_string(markdown)
    
    assert len(phases) == 1
    assert len(phases[0].tasks) == 1
    assert phases[0].tasks[0].task_id == "1.1"
    assert phases[0].tasks[0].estimated_time == "2 hours"

# Test list format
def test_list_task_extraction():
    markdown = """
    ### Phase 1: Test
    
    - [ ] **Task 1.1**: Create Models
      - **Estimated Time**: 2 hours
      
      **Acceptance Criteria:**
      - [ ] Models created
    """
    parser = SpecTasksParser()
    phases = parser.parse_from_string(markdown)
    
    assert len(phases) == 1
    assert len(phases[0].tasks) == 1
    assert phases[0].tasks[0].task_id == "1.1"

# Test mixed formats
def test_mixed_format_in_phase():
    markdown = """
    ### Phase 1: Mixed
    
    #### Task 1.1: Heading Task
    Content
    
    - [ ] **Task 1.2**: List Task
    """
    parser = SpecTasksParser()
    phases = parser.parse_from_string(markdown)
    
    assert len(phases[0].tasks) == 2
```

### 7.2 Integration Tests

```python
def test_divio_spec():
    """Test heading-based format from Divio spec"""
    parser = SpecTasksParser()
    phases = parser.parse(Path(".agent-os/specs/2025-10-10-divio-docs-restructure"))
    
    assert len(phases) == 6
    assert sum(len(p.tasks) for p in phases) == 19
    assert phases[0].phase_number == 1
    assert phases[0].tasks[0].task_id == "1.1"
    assert phases[0].tasks[0].task_name == "Reorganize Directory Structure"

def test_all_existing_specs():
    """Test parser against all specs in repo"""
    parser = SpecTasksParser()
    spec_dir = Path(".agent-os/specs")
    
    for spec_path in spec_dir.iterdir():
        if spec_path.is_dir():
            tasks_file = spec_path / "tasks.md"
            if tasks_file.exists():
                try:
                    phases = parser.parse(spec_path)
                    assert len(phases) > 0, f"No phases in {spec_path.name}"
                    print(f"✅ {spec_path.name}: {len(phases)} phases")
                except Exception as e:
                    pytest.fail(f"Failed to parse {spec_path.name}: {e}")
```

---

## 8. IMPLEMENTATION CHECKLIST

### Phase 1: Foundation (3-4 hours)
- [ ] Implement `_get_text_from_node()` recursive extractor
- [ ] Implement `_extract_task_id()` with unit tests
- [ ] Implement `_extract_task_name()` with unit tests
- [ ] Implement `_contains_task_pattern()`
- [ ] Implement `_traverse_with_parent()` helper

### Phase 2: Phase Extraction (2 hours)
- [ ] Implement `_is_phase_heading()`
- [ ] Implement `_extract_phase_info()`
- [ ] Implement `_find_next_phase_index()`
- [ ] Implement `_extract_phases()` main algorithm
- [ ] Test against Divio spec phases only

### Phase 3: Heading Tasks (3 hours)
- [ ] Implement `_gather_task_nodes()` with stop rules
- [ ] Implement `_list_contains_task_pattern()`
- [ ] Implement `_extract_heading_task()`
- [ ] Test against Divio spec
- [ ] Verify 19 tasks extracted

### Phase 4: List Tasks (2-3 hours)
- [ ] Implement `_extract_list_task()`
- [ ] Implement `_extract_list_tasks_from_list()`
- [ ] Test against template format
- [ ] Verify backward compatibility

### Phase 5: Metadata (3 hours)
- [ ] Implement `_extract_estimated_time()`
- [ ] Implement `_extract_dependencies()`
- [ ] Implement `_extract_acceptance_criteria()`
- [ ] Implement `_extract_list_items()`
- [ ] Implement `_extract_validation_gates()`
- [ ] Implement `_build_description()`

### Phase 6: Integration (2 hours)
- [ ] Run all unit tests
- [ ] Test all existing specs
- [ ] Verify contracts maintained
- [ ] Update docstrings
- [ ] Code review

**Total: 15-17 hours**

---

## 9. SUCCESS CRITERIA

Parser refactor is successful when:

1. ✅ **Divio spec parses correctly**
   - 6 phases found
   - 19 tasks found
   - All metadata extracted

2. ✅ **Template format still works**
   - List-based tasks extracted
   - Backward compatibility maintained

3. ✅ **All existing specs parse**
   - No regressions
   - 12 specs in repo all parse

4. ✅ **Contracts maintained**
   - Returns `List[DynamicPhase]`
   - All fields populated
   - No breaking changes

5. ✅ **Error handling correct**
   - File errors raise ParseError
   - Malformed tasks logged, not failed
   - Clear error messages

---

## 10. MIGRATION PLAN

### Step 1: Implementation (15-17 hours)
Follow Phase 1-6 checklist above

### Step 2: Testing (2 hours)
- Run unit tests
- Test all existing specs
- Verify Divio spec works

### Step 3: Deploy (1 hour)
```bash
# Clear all caches
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} +

# Kill server
pkill -9 -f "Python.*mcp_server"

# Restart Cursor (full restart)
```

### Step 4: Validation (30 min)
```python
# Test workflow
start_workflow("spec_execution_v1", "test", 
    options={"spec_path": ".agent-os/specs/2025-10-10-divio-docs-restructure"})

# Should show 19 tasks available
```

### Rollback Plan
If anything fails:
```bash
cd .agent-os
git restore mcp_server/core/parsers.py
pkill -9 -f "Python.*mcp_server"
# Restart Cursor
```

---

**Status:** ✅ Ready for Implementation  
**Next Step:** Begin Phase 1 - Foundation  
**Estimated Completion:** 15-17 hours

