# Workflow Discovery: Tool-Based, Not RAG-Based
**Date**: 2025-10-15  
**Key Insight**: Workflows discovered via `workflow(action='list_workflows')`, not RAG  
**Reason**: Removing `.praxis-os/workflows/` from RAG index (pollution fix)

---

## The Complete Picture

### Three-Layer Architecture

**Layer 1: Standards (RAG)** - Behavioral patterns
- WHEN to use workflows
- WHY workflows matter
- WHAT patterns to follow
- ❌ NOT: Which specific workflows exist

**Layer 2: Workflow Tool** - Discovery & Execution
- WHICH workflows are available (`list_workflows`)
- HOW to start them (`start`)
- WHAT state they're in (`get_state`)
- ✅ YES: Current workflow catalog

**Layer 3: Workflow Content** - Execution
- Phase-by-phase instructions
- Task breakdown
- Validation gates
- ❌ NOT indexed in RAG (pollution prevention)

---

## Discovery Pattern (Correct Approach)

### OLD Pattern (RAG-based Discovery) ❌

```python
# This won't work after we remove workflows from RAG
search_standards("what workflow for creating specs?")
# Would return workflow names from indexed workflow markdown
```

**Problem**: 
- Workflows in RAG = 137+ files of non-optimized content
- Index pollution degrades search quality
- Workflow content not designed for RAG retrieval

### NEW Pattern (Tool-based Discovery) ✅

```python
# Step 1: Query standards for WHEN/WHY
search_standards("how to create specification")
# Returns: "Use workflows for spec creation, discover via workflow tool"

# Step 2: Discover available workflows via tool
result = workflow(action='list_workflows', category='specification')
# Returns: [
#   {workflow_type: "spec_creation_v1", description: "..."},
#   ...
# ]

# Step 3: Use discovered workflow
workflow(
    action='start',
    workflow_type='spec_creation_v1',  # From discovery
    target_file='feature-name'
)
```

**Benefits**:
1. ✅ No RAG pollution (workflows not indexed)
2. ✅ Programmatic discovery (tool returns structured data)
3. ✅ Always current (tool queries filesystem/metadata)
4. ✅ Standards stay behavioral (patterns, not catalogs)

---

## What Goes Where

### Standards (RAG Index)

**Include**:
- Behavioral patterns (when to query, when to use workflows)
- Meta-patterns (how Agent OS works)
- Quality standards (code quality, testing)
- Architecture principles
- Development process (2-workflow model)

**Example content**:
```markdown
When user says "create the spec":
1. Query for spec creation guidance
2. Discover available workflows via workflow tool
3. Start discovered workflow
4. Follow phases systematically
```

**Key**: Teaches the pattern "discover via tool", not "use workflow X"

### Workflow Tool (`list_workflows` action)

**Returns**:
- Available workflows (current list)
- Workflow metadata (description, phases, duration)
- Filtering by category (specification, testing, etc.)
- Structured data (JSON response)

**Example response**:
```json
{
  "workflows": [
    {
      "workflow_type": "spec_creation_v1",
      "name": "Specification Creation",
      "description": "Create formal 5-file specs from design docs",
      "category": "specification",
      "total_phases": 4,
      "estimated_duration": "30min - 2 hours"
    },
    {
      "workflow_type": "spec_execution_v1",
      "name": "Specification Execution",
      "description": "Implement features from formal specs",
      "category": "implementation",
      "total_phases": 5,
      "estimated_duration": "2-8 hours"
    }
  ]
}
```

### Workflow Content (NOT Indexed)

**Contains**:
- Phase markdown files
- Task markdown files
- Validation gate definitions
- Command glossaries
- Progress tracking

**Why not indexed**: 
- Not RAG-optimized
- Task-specific (not reusable patterns)
- Would pollute index (137+ files)
- Better accessed via workflow tool during execution

---

## The Correct Standards Content

### Phase 2: Structured Spec Creation

**WRONG (RAG-based discovery)**:
```markdown
Query for spec creation workflow:
search_standards("workflow for creating specifications")
```

**CORRECT (Tool-based discovery)**:
```markdown
When user says "create the spec":

1. Query for behavioral guidance:
   search_standards("how to create specification")

2. Discover available workflows:
   workflow(action='list_workflows', category='specification')

3. Select spec creation workflow from results

4. Start workflow with design doc as input

5. Follow workflow phases systematically

6. Present spec for user approval
```

### Phase 3: Structured Implementation

**WRONG (Hardcoded names)**:
```markdown
Use spec_execution_v1 workflow
```

**CORRECT (Dynamic discovery)**:
```markdown
After spec approval:

1. Query for implementation guidance:
   search_standards("how to execute specification")

2. Discover available workflows:
   workflow(action='list_workflows', category='implementation')

3. Select spec execution workflow from results

4. Start workflow with spec path as input

5. Follow workflow phases systematically

6. Present complete implementation
```

---

## Updated Workflow Tool Actions

From our consolidated design, the discovery actions:

### `list_workflows` Action

**Purpose**: Discover available workflows

**Parameters**:
- `category` (optional): Filter by category (specification, implementation, testing)
- `search_query` (optional): Filter by keyword search

**Returns**: List of workflows with metadata

**Example**:
```python
# List all workflows
workflow(action='list_workflows')

# List spec-related workflows
workflow(action='list_workflows', category='specification')

# Search for workflows
workflow(action='list_workflows', search_query='test generation')
```

### `get_metadata` Action

**Purpose**: Get detailed metadata for specific workflow

**Parameters**:
- `workflow_type`: Workflow to query

**Returns**: Full metadata (phases, tasks, validation gates, etc.)

**Example**:
```python
# Get details before starting
workflow(
    action='get_metadata',
    workflow_type='spec_creation_v1'
)
```

---

## The Complete Flow (Correct)

### User Says: "Create a spec"

**Step 1: Query for behavioral pattern**
```python
search_standards("how to create specification")
```

**Returns** (from RAG):
```markdown
Spec creation uses workflows for systematic execution.
Discover available workflows via the workflow tool.
```

**Step 2: Discover workflows**
```python
workflow(action='list_workflows', category='specification')
```

**Returns** (from tool):
```json
{
  "workflows": [
    {"workflow_type": "spec_creation_v1", ...}
  ]
}
```

**Step 3: Start workflow**
```python
workflow(
    action='start',
    workflow_type='spec_creation_v1',
    target_file='feature-name',
    options={'design_doc': 'design.md'}
)
```

**Step 4: Execute workflow**
- Follow phases returned by workflow tool
- Complete tasks
- Submit evidence
- Advance through gates

---

## Benefits of This Architecture

### 1. Clean Separation of Concerns

- **Standards**: Patterns and behaviors (when/why)
- **Tool**: Discovery and execution (what/how)
- **Workflows**: Detailed instructions (step-by-step)

### 2. No RAG Pollution

- Remove `.praxis-os/workflows/` from index
- 137+ files no longer polluting search
- RAG focused on behavioral patterns only

### 3. Always Current

- Tool queries filesystem dynamically
- No stale workflow names in docs
- Metadata.json is source of truth

### 4. Programmatic Discovery

- Structured JSON responses
- Filterable by category
- Searchable by keywords
- Machine-readable, not text parsing

### 5. Scalable

- Add new workflows without touching standards
- Workflows self-register via metadata.json
- No doc maintenance burden

---

## Implementation Impact

### Changes to RAG Index Build

**Remove from index**:
```python
# OLD: Index all markdown
source_paths = [
    ".praxis-os/standards/",
    ".praxis-os/workflows/",  # ← REMOVE THIS
    ".praxis-os/usage/"
]

# NEW: Index only standards and usage
source_paths = [
    ".praxis-os/standards/",
    ".praxis-os/usage/"
]
```

**Result**: 
- RAG index drops from ~400 files to ~250 files
- Search quality improves (no task file noise)
- Faster indexing and queries

### Changes to Standards Content

**Update these files**:
1. `agent-os-development-process.md` - Add tool-based discovery pattern
2. `rag-content-authoring.md` - Update workflow discovery section
3. `workflow-system-overview.md` - Document tool-based discovery

**Remove**:
- Any hardcoded workflow names
- Any instructions to "query RAG for workflows"

**Add**:
- Tool-based discovery examples
- `list_workflows` action usage
- Pattern: "Standards tell you WHEN, tool tells you WHICH"

### Changes to Workflow Tool

**Ensure these actions exist** (from consolidated design):
- `list_workflows` - Discovery
- `get_metadata` - Detailed info
- `search` - Keyword search
- `start` - Execute workflow
- All other execution/management actions

---

## Testing the Pattern

### Scenario 1: AI Needs to Create Spec

**AI thinks**: "User wants a spec, what do I do?"

**Step 1: Query standards**
```python
search_standards("how to create specification")
```

**AI learns**: "Use workflows, discover via tool"

**Step 2: Use tool**
```python
workflow(action='list_workflows', category='specification')
```

**AI discovers**: "spec_creation_v1 is available"

**Step 3: Execute**
```python
workflow(action='start', workflow_type='spec_creation_v1', ...)
```

✅ **Success**: AI discovered workflow without RAG pollution

### Scenario 2: Workflow Gets Renamed

**Change**: `spec_creation_v1` → `spec_creation_v2`

**Impact**:
- ✅ Standards unchanged (no workflow names)
- ✅ Tool returns new name automatically
- ✅ AI discovers v2 via list_workflows
- ✅ No doc updates needed

**Result**: Robust to change!

---

## Next Steps

1. **Update consolidated workflow tool design** to emphasize discovery actions
2. **Update standards** to teach tool-based discovery
3. **Remove workflows from RAG index** (update build script)
4. **Test discovery pattern** with real workflows
5. **Update orientation** to include tool-based discovery

---

## Summary

**The correct pattern**:
- Standards (RAG): Teach WHEN/WHY to use workflows
- Workflow Tool: Discover WHICH workflows exist
- Workflows: HOW to execute (not in RAG)

**Not**:
- ❌ Hardcode workflow names anywhere
- ❌ Index workflows in RAG
- ❌ Query RAG for workflow discovery

**Yes**:
- ✅ Query standards for patterns
- ✅ Use tool for discovery
- ✅ Dynamic, always current

**This completes the architecture!** 🎉

