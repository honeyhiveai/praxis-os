# Task Parser Brittleness Analysis

**Date:** 2025-10-20  
**Critical Issue:** Parser keeps breaking on spec tasks.md files  
**Root Cause Impact:** Forces manual mode → Quality gaps (like three-tier fallback)

---

## Current Implementation Analysis

### Architecture: AST-Based (Good Foundation)

**Using:** `mistletoe` library for markdown AST parsing  
**File:** `mcp_server/core/parsers.py`  
**Class:** `SpecTasksParser`

**Strengths:**
- ✅ AST-based (not regex-only)
- ✅ Handles markdown structure properly
- ✅ Can traverse nested elements

**BUT: Still has brittle hardcoded patterns**

---

## Brittleness Points (Why It Keeps Breaking)

### 1. **Hardcoded Phase Header Pattern** 🚨

```python
# Line 95: _extract_phases_from_ast()
if isinstance(node, Heading) and node.level in [2, 3]:
    header_text = self._get_text_content(node)
    phase_match = re.match(r"Phase (\d+):\s*(.+)", header_text)
```

**Problem:** Requires EXACT format: `## Phase N: Name`

**Breaks on:**
- `## Phase 1 - Foundation` (dash instead of colon)
- `### Phase 1: Foundation` (level 3 header when expecting level 2)
- `## 1. Foundation` (number-dot format)
- `## Foundation (Phase 1)` (phase number after name)

**Why AI varies:** Different AI models format headers differently, workflow_creation_v1 might generate slightly different markdown

---

### 2. **Hardcoded Metadata Patterns** 🚨

```python
# Lines 135-145: _build_phase()
if "Objective:" in text or "Goal:" in text:
    desc_match = re.search(
        r"(?:Objective|Goal):\s*(.+?)(?:\n|$)", text, re.IGNORECASE
    )
```

**Problem:** Only recognizes "Objective:" or "Goal:" exactly

**Breaks on:**
- `**Purpose:** Create foundation` (Purpose vs Goal)
- `Goal - Create foundation` (dash vs colon)
- `Goal (Create foundation)` (parentheses)
- Goal on next line (multiline format)

---

### 3. **Task ID Pattern Too Strict** 🚨

```python
# Line 202: _parse_single_task()
task_match = re.search(r"Task (\d+)\.(\d+):\s*(.+?)(?:\n|$)", task_text)
```

**Problem:** Requires exact `Task N.M:` format

**Breaks on:**
- `Task 1-1:` (dash separator)
- `Task 1.1 -` (dash after task ID)
- `Task 1.1.` (period at end)
- `- Task 1.1:` (leading dash)
- `**Task 1.1:**` (bold formatting)

---

### 4. **Validation Gate Detection Too Narrow** 🚨

```python
# Lines 169-174: _extract_tasks_from_list()
elif (
    "Validation Gate:" in item_text
    or phase_data["validation_gate"]
    or any("validation" in line.lower() for line in item_text.split("\n")[:2])
):
```

**Problem:** Looks for exact "Validation Gate:" string

**Breaks on:**
- `**Checkpoint Validation:**`
- `**Phase Gate:**`
- `**Quality Gate:**`
- `**Acceptance Gate:**`

---

### 5. **Dependencies Parsing Fragile** 🚨

```python
# Lines 192-200: _extract_task_dependencies()
deps_match = re.search(r"Dependencies:\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
```

**Problem:** Requires "Dependencies:" label

**Breaks on:**
- `Depends on: Task 1.1`
- `Requires: Task 1.1`
- `After: Task 1.1`
- Inline format: `(depends on 1.1)`

---

## Failure Modes Observed

**When parser fails, it:**
1. Returns empty phases list
2. Raises ParseError
3. Forces user to manual mode
4. **Loses systematic validation**

**Cascade effect:**
```
Parser fails → Manual mode → Skip steps → Quality gaps → Incomplete implementation
```

---

## Why This Happens Repeatedly

### 1. **AI Formatting Variability**

Different AI models/prompts produce different markdown:
- Claude might use `## Phase 1: Name`
- GPT-4 might use `## 1. Name`
- Workflow generator might use `### Phase 1 - Name`

**Each variation breaks the parser!**

### 2. **Workflow Evolution**

As workflows improve, they use better formatting:
- More semantic headings
- Better organization
- Richer metadata

**Parser can't adapt!**

### 3. **No Graceful Degradation**

When a pattern doesn't match:
- Parser returns None
- No partial parsing
- All-or-nothing failure

**Should be progressive enhancement!**

---

## Dynamic Pattern Discovery Approach

### Core Principle: **Discover, Don't Dictate**

Instead of hardcoding patterns, discover them from document structure:

```python
def discover_phase_pattern(doc):
    """Analyze document to discover phase header pattern."""
    # Look for repeating header patterns
    # Analyze content to determine semantic meaning
    # Build pattern dynamically
```

### Implementation Strategy

#### 1. **Pattern Discovery Phase**

**Before parsing, analyze document to discover:**
- How are phases marked? (## or ###, numbering style)
- How are tasks marked? (bullets, numbering, formatting)
- Where are metadata fields? (bold, italic, plain text)
- What labels are used? (Goal vs Objective, Dependencies vs Requires)

#### 2. **Semantic Analysis**

**Use heuristics, not exact matches:**
```python
def is_phase_header(node):
    """Heuristic: Is this a phase header?"""
    if not isinstance(node, Heading):
        return False
    
    text = get_text(node).lower()
    
    # Heuristic clues:
    # - Contains "phase" word
    # - Has a number
    # - Level 2 or 3 heading
    # - Near start of document
    
    has_phase_keyword = "phase" in text
    has_number = re.search(r'\d+', text)
    proper_level = node.level in [2, 3]
    
    return has_phase_keyword and has_number and proper_level
```

#### 3. **Progressive Enhancement**

**Extract what's available, gracefully handle missing:**
```python
def extract_task_id(text):
    """Try multiple task ID patterns, return best match."""
    patterns = [
        r"Task (\d+)\.(\d+)",      # Task 1.1
        r"Task (\d+)-(\d+)",        # Task 1-1
        r"(\d+)\.(\d+):",           # 1.1:
        r"Task #?(\d+)\.?(\d+)",    # Task #1.1
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return f"{match.group(1)}.{match.group(2)}"
    
    # Fallback: extract any numbers found
    numbers = re.findall(r'\d+', text)
    if len(numbers) >= 2:
        return f"{numbers[0]}.{numbers[1]}"
    
    return None  # Couldn't find task ID
```

#### 4. **Fuzzy Metadata Matching**

**Instead of exact label matching:**
```python
METADATA_SYNONYMS = {
    'goal': ['goal', 'objective', 'purpose', 'aim'],
    'duration': ['duration', 'time', 'effort', 'timeframe'],
    'dependencies': ['dependencies', 'depends on', 'requires', 'after'],
    'validation': ['validation gate', 'checkpoint', 'acceptance gate', 'phase gate']
}

def find_metadata_field(text, field_type):
    """Find metadata field using synonyms."""
    text_lower = text.lower()
    for synonym in METADATA_SYNONYMS.get(field_type, []):
        if synonym in text_lower:
            # Extract value after synonym
            return extract_value_after(text, synonym)
    return None
```

#### 5. **Structure-Based Parsing**

**Use document structure, not just text patterns:**
```python
def parse_phase(phase_header, nodes_until_next_header):
    """Parse phase from header + nodes."""
    phase = {
        'number': extract_number_from_header(phase_header),
        'name': extract_name_from_header(phase_header),
        'tasks': [],
        'metadata': {}
    }
    
    # Analyze nodes in order
    for node in nodes_until_next_header:
        if is_metadata_paragraph(node):
            # Extract metadata
            update_metadata(phase, node)
        elif is_task_list(node):
            # Extract tasks
            tasks = extract_tasks(node)
            phase['tasks'].extend(tasks)
        elif is_validation_gate_list(node):
            # Extract validation gate
            phase['validation_gate'] = extract_checklist(node)
    
    return phase
```

---

## Proposed Solution

### Phase 1: Add Pattern Discovery

**Before parsing content, discover patterns:**

```python
class PatternDiscovery:
    """Discover document patterns dynamically."""
    
    def analyze_document(self, doc):
        """Analyze entire document to discover patterns."""
        return {
            'phase_header_level': self._discover_phase_header_level(doc),
            'phase_numbering_style': self._discover_numbering_style(doc),
            'metadata_labels': self._discover_metadata_labels(doc),
            'task_id_pattern': self._discover_task_pattern(doc),
        }
    
    def _discover_phase_header_level(self, doc):
        """What heading level marks phases?"""
        # Count ## vs ### headers containing "phase"
        # Return most common
    
    def _discover_numbering_style(self, doc):
        """How are phases numbered? (1: vs 1. vs 1 -)"""
        # Analyze headers with numbers
        # Return detected pattern
```

### Phase 2: Semantic Extraction

**Use discovered patterns + semantic heuristics:**

```python
class SemanticParser:
    """Parse using semantic understanding, not exact matches."""
    
    def __init__(self, patterns):
        self.patterns = patterns
    
    def extract_phase(self, header_node, body_nodes):
        """Extract phase using semantic analysis."""
        # Use discovered patterns as hints
        # Fall back to heuristics
        # Gracefully handle missing data
```

### Phase 3: Progressive Enhancement

**Build phases incrementally:**

```python
def parse_with_degradation(source):
    """Parse with graceful degradation."""
    phases = []
    
    # Try full parsing
    try:
        phases = full_parse(source)
        if phases:
            return phases
    except ParseError:
        pass
    
    # Try partial parsing
    try:
        phases = partial_parse(source)  # Get what we can
        if phases:
            logger.warning("Partial parse succeeded")
            return phases
    except ParseError:
        pass
    
    # Try minimal parsing
    phases = minimal_parse(source)  # Just phases and names
    logger.warning("Minimal parse succeeded")
    return phases
```

---

## Testing Strategy

### 1. **Variation Test Suite**

Create test cases for format variations:

```python
TEST_CASES = [
    # Standard format
    "## Phase 1: Foundation",
    
    # Variations
    "### Phase 1: Foundation",      # Different level
    "## Phase 1 - Foundation",      # Dash separator
    "## 1. Foundation",             # Number-dot
    "## Foundation (Phase 1)",      # Number after name
    
    # Edge cases
    "##Phase 1: Foundation",        # No space
    "## Phase 01: Foundation",      # Zero-padded
]

def test_phase_header_parsing():
    for test_case in TEST_CASES:
        result = parse_phase_header(test_case)
        assert result is not None, f"Failed to parse: {test_case}"
```

### 2. **Real Spec Tests**

Test with actual generated specs:

```python
def test_parse_real_specs():
    """Test parsing real spec files."""
    spec_files = [
        "specs/evidence-validation-system-2025-10-20/tasks.md",
        "specs/n8n-comparison-analysis-2025-10-16/tasks.md",
        # Add more real specs
    ]
    
    for spec_file in spec_files:
        phases = parser.parse(Path(spec_file))
        assert len(phases) > 0, f"Failed to parse {spec_file}"
```

### 3. **Fuzz Testing**

Generate variations programmatically:

```python
def generate_variations(base_format):
    """Generate format variations."""
    variations = [
        base_format,
        base_format.replace(":", " -"),
        base_format.replace("## ", "### "),
        # ... more variations
    ]
    return variations
```

---

## Migration Plan

### Step 1: Analyze Current Failures

Collect actual failing specs and document patterns

### Step 2: Implement Pattern Discovery

Add dynamic pattern discovery module

### Step 3: Refactor Parser

Make parser use discovered patterns + heuristics

### Step 4: Add Degradation

Implement progressive parsing (full → partial → minimal)

### Step 5: Test Thoroughly

Run against real specs, variations, edge cases

### Step 6: Deploy with Monitoring

Monitor parsing success rate, log failures

---

## Success Criteria

**Parser should:**
- ✅ Parse 95%+ of AI-generated specs
- ✅ Handle format variations gracefully
- ✅ Provide partial results when full parse fails
- ✅ Log clear warnings for unrecognized patterns
- ✅ Never force manual mode unnecessarily

**Quality impact:**
- ✅ Systematic validation enforced
- ✅ No quality gaps from manual mode
- ✅ Workflows work as designed

---

## Conclusion

**Current parser is brittle because:**
1. Hardcoded exact patterns
2. No format variation tolerance
3. All-or-nothing parsing
4. No pattern discovery

**Solution:**
1. Discover patterns dynamically
2. Use semantic heuristics
3. Progressive degradation
4. Extensive testing

**Impact:**
- Parser works reliably
- Workflows enforce quality
- No manual mode needed
- No quality gaps (like three-tier fallback)

**This is the root fix** that prevents cascading quality issues.
