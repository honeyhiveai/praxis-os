# MCP Tool Design Analysis - Tool Count vs. Workflow Discovery
**Date**: 2025-10-15  
**Issue**: Workflow indexing for discovery may be wrong approach  
**Alternative**: Rethink tool call design for workflow discovery  
**Research**: MCP tool count limits and design best practices

---

## Executive Summary

**Current Approach**: Index all workflow metadata in RAG for discovery

**Concern**: This may be the wrong solution to the wrong problem

**Real Issue**: How should AI agents DISCOVER and SELECT workflows?

**Research Finding**: MCP tool count limits are **strict** - performance degrades 85% beyond 20 tools

**Current Tool Count**: 11 tools (we're in good shape)

**Implications**: 
- Don't need complex discovery via RAG
- Simple, focused tools with minimal parameters is the MCP standard
- Our current workflow tools are **well-designed**
- Need to question the original problem: why do agents need to "discover" workflows via RAG?

---

## Research: Why Tool Count Limits Matter

### The Hard Science

**Source**: Microsoft Research, StackOne, AWS MCP Best Practices

**Performance Impact**:
- **<10 tools**: ✅ Optimal LLM performance
- **10-20 tools**: ✅ Good performance  
- **>20 tools**: ⚠️ Performance degrades **up to 85%**
- **>40 tools**: ❌ Platform hard limits may apply

### Why This Happens

**1. Context Window Pollution**

Every tool descriptor consumes context:
```
Tool: start_workflow
  Parameters:
    - workflow_type: string (required)
      Description: Type of workflow to start (e.g., "test_generation_v3")
    - target_file: string (required)
      Description: File path to target
    - options: object (optional)
      Description: Additional workflow options
  Returns: Dict with session_id, current_phase, phase_content
  Raises: ValueError if workflow_type invalid
  Example: start_workflow("test_generation_v3", "myfile.py")
```

**Per tool**: ~100-300 tokens for schema + description

**20 tools**: ~2,000-6,000 tokens BEFORE any user query

**Impact**: Less room for actual work, more room for tool catalog

### 2. Attention Degradation

**LLM attention is finite**. More tools = more cognitive load:

- Must evaluate which tool to use
- Must understand parameter relationships
- Must track tool execution state
- Must validate tool applicability

**With 5 tools**: Clear choices, focused attention  
**With 20 tools**: Harder to choose, split attention  
**With 40 tools**: Choice paralysis, wrong tool selection

### 3. Increased Error Rate

**Research finding** (from StackOne): Tool calling accuracy decreases with tool count

- **<10 tools**: ~95% correct tool selection
- **10-20 tools**: ~85% correct tool selection
- **>20 tools**: ~60% correct tool selection (40% error rate!)

**Common errors**:
- Wrong tool for the job
- Missing required parameters
- Incorrect parameter values
- Skipping necessary tool calls
- Calling tools out of sequence

---

## Current prAxIs OS Tool Count

### Inventory

```bash
$ grep -r "@mcp.tool()" mcp_server/server/tools/ | wc -l
11
```

**Breakdown**:

**RAG Tools (1 tool)**:
1. `search_standards` - Semantic search over standards/usage/workflows

**Workflow Tools (7 tools)**:
2. `start_workflow` - Initialize workflow session
3. `get_current_phase` - Retrieve current phase content
4. `get_task` - Retrieve specific task (horizontal scaling)
5. `complete_phase` - Submit evidence and advance phase
6. `get_workflow_state` - Get full workflow state (debug/resume)
7. `create_workflow` - Generate new workflow framework
8. `validate_workflow` - Validate workflow structure

**Server Tools (1 tool)**:
9. `get_server_info` - Server metadata and capabilities

**Browser Tools (1 tool)**:
10. `pos_browser` - Browser automation (Playwright wrapper)

**Date Tools (1 tool)**:
11. `current_date` - Get current date/time (AI date error prevention)

**Total**: 11 tools

**Status**: ✅ Well within optimal range (<10 is ideal, 11 is still good)

---

## Tool Design Quality Assessment

### ✅ GOOD: Workflow Tools (7 tools)

Our workflow tools **follow MCP best practices perfectly**:

```python
# Granular, focused tools
start_workflow()        # 1 responsibility: initialize
get_current_phase()     # 1 responsibility: retrieve phase
get_task()              # 1 responsibility: retrieve task
complete_phase()        # 1 responsibility: validate & advance
get_workflow_state()    # 1 responsibility: get state
create_workflow()       # 1 responsibility: generate framework
validate_workflow()     # 1 responsibility: validate structure
```

**Why this is good** (from standards/development/mcp-tool-design-best-practices.md):
- ✅ Each tool has single, clear responsibility
- ✅ Verb-noun naming pattern
- ✅ Simple parameters (2-3 per tool)
- ✅ Clear when to use each
- ✅ Easy to document and test
- ✅ Enables horizontal scaling (get_task)

**Research alignment**: These tools exemplify "granular over parameterized" design

### ⚠️ ANTI-PATTERN: Browser Tool (1 tool)

**Current design**:
```python
@mcp.tool()
async def pos_browser(
    action: str,  # "navigate", "screenshot", "click", "type", etc.
    session_id: Optional[str] = None,
    url: Optional[str] = None,
    selector: Optional[str] = None,
    text: Optional[str] = None,
    # ... 20+ more optional parameters
) -> Dict[str, Any]:
    """Browser automation based on action parameter."""
    if action == "navigate":
        # ...
    elif action == "screenshot":
        # ...
    elif action == "click":
        # ...
    # ... 20+ more branches
```

**This is the EXACT anti-pattern** described in mcp-tool-design-best-practices.md:

> ❌ Not Recommended: Parameterized Mega-Tool
> 
> Problems:
> - ❌ Unclear when to use which action
> - ❌ Complex parameter validation (which params for which action?)
> - ❌ Poor error messages (ambiguous failures)
> - ❌ Harder to document comprehensively
> - ❌ LLM confusion about correct parameters

**Better design** (NOT implemented yet):
```python
# Separate browser tools
@mcp.tool()
async def browser_navigate(session_id: str, url: str) -> Dict: ...

@mcp.tool()
async def browser_screenshot(session_id: str, path: str) -> Dict: ...

@mcp.tool()
async def browser_click(session_id: str, selector: str) -> Dict: ...
```

**However**: This would add ~10-15 tools, pushing us to **~25 tools** (degraded performance zone)

**Tradeoff**: 
- Option A: Keep 1 parameterized browser tool (anti-pattern but low tool count)
- Option B: Split into 15 granular tools (best practice but high tool count)
- Option C: Remove browser tools entirely (most workflows don't need them)

---

## The Original Problem: Workflow Discovery

### What Problem Were We Solving?

**Original need**: AI agents need to discover which workflow to use for a task

**Examples**:
- Agent needs to generate tests → discover `test_generation_v3`
- Agent needs to create a workflow → discover `workflow_creation_v1`
- Agent needs to execute a spec → discover `spec_execution_v1`

**Original solution**: Index workflow metadata.json in RAG so agents can search semantically

**Query example**:
```python
result = search_standards("workflow for test generation")
# Returns: test_generation_v3 metadata
```

### Is This the Right Solution?

**Questioning the approach**: 

1. **How often do agents need to discover workflows?**
   - In practice: User tells agent "use test_generation_v3"
   - User rarely says "find a workflow for testing"

2. **Do we have enough workflows to need discovery?**
   - Current: 4 workflows (test_generation_v3, workflow_creation_v1, spec_execution_v1, standards_creation_v1)
   - Future: Maybe 10-20 workflows
   - This is a small, curated set

3. **Is semantic search the right interface?**
   - Workflows are tools/processes, not documentation
   - Documentation (standards) should be searchable
   - Workflows should be **listable and selectable**

### Alternative Approaches

**Option 1: List Workflows Tool** (Add 1 tool)

```python
@mcp.tool()
async def list_workflows(
    filter_by: Optional[str] = None  # "test", "generation", "validation", etc.
) -> Dict[str, Any]:
    """
    List available workflows with descriptions.
    
    Returns all workflows with metadata for selection.
    Agents can read descriptions and choose appropriate workflow.
    
    Returns:
        {
            "workflows": [
                {
                    "workflow_type": "test_generation_v3",
                    "description": "Generate comprehensive test suites...",
                    "total_phases": 8,
                    "estimated_duration": "2-4 hours",
                    "best_for": ["Python", "pytest", "unit tests"],
                    "primary_outputs": ["test file", "coverage report"]
                },
                {
                    "workflow_type": "workflow_creation_v1",
                    "description": "Create new AI-assisted workflows...",
                    "total_phases": 6,
                    "estimated_duration": "8-12 hours",
                    "best_for": ["workflow design", "meta-workflow"],
                    "primary_outputs": ["workflow directory", "metadata.json"]
                }
            ]
        }
    """
    # Load all metadata.json files from workflows directory
    workflows = []
    for metadata_path in workflows_dir.rglob("metadata.json"):
        with open(metadata_path) as f:
            metadata = json.load(f)
        workflows.append(metadata)
    
    # Filter if requested
    if filter_by:
        workflows = [w for w in workflows if filter_by.lower() in w['description'].lower()]
    
    return {"workflows": workflows, "count": len(workflows)}
```

**Benefits**:
- ✅ +1 tool (12 total, still optimal)
- ✅ Simple, focused tool (granular design)
- ✅ No RAG index pollution
- ✅ Fast (direct file read, no vector search)
- ✅ Complete metadata returned (not just chunks)
- ✅ Filterable (optional parameter)

**Usage**:
```python
# Agent workflow
User: "Generate tests for my Python file"
Agent: Let me find the right workflow...
  → list_workflows(filter_by="test")
  → Returns test_generation_v3
  → start_workflow("test_generation_v3", "myfile.py")
```

**Option 2: Workflow Metadata in search_standards** (No new tools)

**Keep existing approach** but fix the RAG pollution:
- Index ONLY metadata.json files (not all workflow .md files)
- Build rich, searchable text from metadata
- Agents query via existing `search_standards`

**Benefits**:
- ✅ No new tools
- ✅ Uses existing RAG infrastructure
- ✅ Semantic search still available
- ✅ Fixes pollution issue (4 files vs. 137)

**Drawbacks**:
- ⚠️ Still mixing documentation (standards) with tools (workflows)
- ⚠️ RAG search for small, curated set seems overkill

**Option 3: Workflow Discovery via Standards** (No new tools, no workflow indexing)

**Radical approach**: Don't index workflows at all

**Instead**: Write standards that teach agents about workflows

**Example standard**: `standards/universal/workflows/workflow-selection-guide.md`

```markdown
# Workflow Selection Guide

## When to Use Which Workflow

### Test Generation

**Use:** test_generation_v3

**When:**
- Need to generate unit tests
- Have Python codebase
- Want pytest-based tests
- Need coverage analysis

**Start with:**
```python
start_workflow("test_generation_v3", target_file="path/to/file.py")
```

### Workflow Creation

**Use:** workflow_creation_v1

**When:**
- Need to create a new workflow
- Have design specification
- Building meta-workflow
- Generating workflow framework

**Start with:**
```python
start_workflow("workflow_creation_v1", target_file="new_workflow_name")
```

### Spec Execution

**Use:** spec_execution_v1

**When:**
- Have tasks.md specification
- Need to execute project plan
- Following structured specification
- Want phase-gated execution

**Start with:**
```python
start_workflow("spec_execution_v1", options={"spec_path": "path/to/tasks.md"})
```
```

**Benefits**:
- ✅ No new tools
- ✅ No workflow indexing
- ✅ No RAG pollution
- ✅ Standards remain RAG-optimized
- ✅ Agents learn via search_standards
- ✅ One source of truth (standard, not duplicated metadata)

**Usage**:
```python
# Agent workflow
User: "Generate tests for my Python file"
Agent: Let me find the right workflow...
  → search_standards("how to generate tests workflow")
  → Returns workflow-selection-guide.md section
  → Reads: "Use test_generation_v3"
  → start_workflow("test_generation_v3", "myfile.py")
```

---

## Tool Design: Simple Tools with Minimal Parameters

### Research Finding

**From AWS, Anthropic, HaaS on SaaS**:

> Create focused tools that perform specific tasks effectively with minimal parameters.

**Why minimal parameters?**

1. **Reduces LLM cognitive load**
   - Fewer parameters = clearer purpose
   - Less ambiguity about what to provide
   - Fewer validation errors

2. **Improves error messages**
   - Simple parameter set = specific errors
   - Easy to diagnose missing parameters
   - Clear remediation steps

3. **Enables better documentation**
   - Fewer parameters = clearer examples
   - Less complex parameter interaction
   - Easier to understand purpose

### Current prAxIs OS Tool Complexity

**Simple tools** (1-3 parameters):
```python
search_standards(query, n_results=5, filters=None)           # 3 params
start_workflow(workflow_type, target_file, options=None)     # 3 params
get_current_phase(session_id)                                # 1 param
get_task(session_id, phase, task_number)                     # 3 params
complete_phase(session_id, phase, evidence)                  # 3 params
get_workflow_state(session_id)                               # 1 param
current_date()                                               # 0 params
get_server_info()                                            # 0 params
```

**Complex tool** (20+ parameters):
```python
pos_browser(
    action,              # required
    session_id,          # optional
    url,                 # optional
    wait_until,          # optional (default: "load")
    timeout,             # optional (default: 30000)
    color_scheme,        # optional
    reduced_motion,      # optional
    screenshot_full_page,# optional (default: False)
    screenshot_path,     # optional
    screenshot_format,   # optional (default: "png")
    viewport_width,      # optional
    viewport_height,     # optional
    selector,            # optional
    text,                # optional
    value,               # optional
    button,              # optional (default: "left")
    click_count,         # optional (default: 1)
    modifiers,           # optional
    wait_for_state,      # optional (default: "visible")
    wait_for_timeout,    # optional (default: 30000)
    query_all,           # optional (default: False)
    script,              # optional
    cookies,             # optional
    cookie_name,         # optional
    storage_key,         # optional
    # ... and more
) -> Dict
```

**Analysis**: pos_browser violates MCP best practices on multiple dimensions:
1. ❌ Parameterized action dispatch (not granular)
2. ❌ 20+ parameters (not minimal)
3. ❌ Complex validation (which params for which action?)
4. ❌ Unclear error messages (parameter interactions)

---

## Recommendations

### 1. Workflow Discovery: Use Option 3 (Standards-Based)

**Recommendation**: Don't index workflows in RAG. Write standards that teach agents about workflows.

**Implementation**:
1. Create `standards/universal/workflows/workflow-selection-guide.md`
2. Document each workflow: when to use, how to start
3. Make it RAG-optimized (keywords, query hooks, examples)
4. Remove workflows from RAG indexing

**Benefits**:
- ✅ No tool count increase
- ✅ No RAG pollution
- ✅ Standards remain prominent
- ✅ One source of truth
- ✅ Easy to maintain (update one document)

**File count impact**:
- Current: 89 standards + 137 workflows = 226 indexed files
- After: 89 standards + 1 workflow guide = 90 indexed files
- **Reduction**: 60% smaller index

**Search quality**: Dramatically improved (no workflow task pollution)

### 2. Consider Adding list_workflows Tool (Optional)

**If** standards-based discovery proves insufficient, add:

```python
@mcp.tool()
async def list_workflows(filter_by: Optional[str] = None) -> Dict:
    """List available workflows with metadata."""
    # Load all metadata.json files
    # Return structured list
```

**Tool count**: 12 (still optimal)

**Use case**: When agent needs complete list, not just discovery

### 3. Browser Tools: Accept the Tradeoff

**Current design** (1 parameterized tool) is **acceptable** given:
- Alternative (15 granular tools) pushes us to >20 tools (degraded performance)
- Browser automation is secondary feature (not core workflow)
- Most workflows don't need browser tools

**Action**: Document the tradeoff, keep current design

**Future optimization**: If browser becomes core feature, consider:
- Separate MCP server for browser tools (dual-server approach)
- Selective loading (only load browser when needed)

### 4. Create Workflow Selection Guide Standard

**File**: `standards/universal/workflows/workflow-selection-guide.md`

**Content structure**:
```markdown
# Workflow Selection Guide

**Keywords**: workflow selection, which workflow, test generation, workflow creation, spec execution, when to use workflow

**Purpose**: Guide agents to select the correct workflow for their task

## Quick Selection

| Need | Workflow | Command |
|------|----------|---------|
| Generate tests | test_generation_v3 | start_workflow("test_generation_v3", "file.py") |
| Create workflow | workflow_creation_v1 | start_workflow("workflow_creation_v1", "name") |
| Execute spec | spec_execution_v1 | start_workflow("spec_execution_v1", options) |
| Create standards | standards_creation_v1 | start_workflow("standards_creation_v1", "name") |

## Detailed Workflow Information

### test_generation_v3

**When to use:**
- Generating unit tests for Python code
- Need pytest-based test suite
- Want coverage analysis
- Working with existing codebase

**What it produces:**
- Complete test file (test_*.py)
- Pytest fixtures
- Coverage report
- Test documentation

**How to start:**
```python
start_workflow(
    workflow_type="test_generation_v3",
    target_file="path/to/source.py"
)
```

### workflow_creation_v1

**When to use:**
- Creating new workflow framework
- Have design specification
- Building meta-workflow
- Need phase-gated structure

**What it produces:**
- Complete workflow directory
- metadata.json with phase definitions
- Task files (100-170 lines each)
- Supporting documentation

**How to start:**
```python
start_workflow(
    workflow_type="workflow_creation_v1",
    target_file="new_workflow_name",
    options={"design_spec_path": "path/to/design-spec.md"}
)
```

... (continue for each workflow)
```

**RAG optimization**:
- ✅ Keywords at top
- ✅ Table for quick reference
- ✅ Detailed sections for each workflow
- ✅ Code examples (copy-paste ready)
- ✅ Natural language descriptions
- ✅ Query hooks throughout

### 5. Remove Workflows from RAG Indexing

**File**: `scripts/build_rag_index.py`

**Change**:
```python
# OLD: Index all workflow files
if workflows_path and workflows_path.exists():
    self.source_paths.append(workflows_path)

# NEW: Don't index workflows (use standards instead)
# Workflows are tools, not documentation
# Discovery via standards/universal/workflows/workflow-selection-guide.md
```

**Impact**:
- 137 fewer indexed files
- Improved search quality
- Standards remain prominent
- Faster index builds

---

## Tool Count Roadmap

### Current State (11 tools) ✅

```
RAG: 1 tool
  - search_standards

Workflow: 7 tools
  - start_workflow
  - get_current_phase
  - get_task
  - complete_phase
  - get_workflow_state
  - create_workflow
  - validate_workflow

Server: 1 tool
  - get_server_info

Browser: 1 tool
  - pos_browser (parameterized anti-pattern but acceptable tradeoff)

Utility: 1 tool
  - current_date
```

### Future Additions (Planned)

**Option A: No new tools** (Recommended)
- Use standards-based workflow discovery
- Total: 11 tools (optimal range)

**Option B: Add list_workflows** (If needed)
- Add 1 tool for workflow listing
- Total: 12 tools (still optimal range)

**Option C: Add sub-agent tools** (Future)
- Design validator: +3 tools
- Concurrency analyzer: +5 tools
- Total: ~19 tools (upper end of good range)

### Tool Count Limits to Respect

```
Current: 11 tools ← WE ARE HERE ✅
Target: <15 tools (optimal)
Warning: >20 tools (performance degradation begins)
Limit: <30 tools (hard performance ceiling)
```

**Strategy**: Stay below 15 tools for core functionality, use selective loading for specialized features

---

## Conclusion

### Key Findings

1. **Tool count limits are real and strict**
   - <10 optimal, 10-20 good, >20 degrades 85%
   - We're at 11 tools (good position)

2. **Our workflow tools are well-designed**
   - Granular, not parameterized
   - Simple parameters (1-3 per tool)
   - Follow MCP best practices

3. **Workflow indexing may be wrong approach**
   - Pollutes RAG with 137 non-optimized files
   - Workflows are tools, not documentation
   - Small, curated set doesn't need semantic search

4. **Standards-based discovery is better**
   - No new tools needed
   - No RAG pollution
   - One source of truth
   - Easy to maintain

### Recommendations

**Immediate (This Week)**:
1. ✅ Create `standards/universal/workflows/workflow-selection-guide.md`
2. ✅ Remove workflows from RAG indexing
3. ✅ Test discovery via search_standards

**Short-Term (Next 2 Weeks)**:
4. Monitor agent workflow discovery success rate
5. Consider adding `list_workflows` tool if standards insufficient
6. Document browser tool tradeoff (parameterized vs. tool count)

**Long-Term (Ongoing)**:
7. Stay vigilant about tool count (hard limit: 15 tools)
8. Use selective loading for specialized features
9. Prefer standards documentation over new tools when possible

### The Right Questions

**Original question**: "Should we index workflows in RAG?"
**Better question**: "How should agents discover workflows?"
**Answer**: Via standards that teach workflow selection, not via semantic search of workflow metadata

**Original question**: "Should we add more workflow tools?"
**Better question**: "Are our tools granular enough and simple enough?"
**Answer**: Yes, our workflow tools exemplify MCP best practices

**Original question**: "Why keep tool count <20?"
**Better question**: "What is the optimal tool count for AI performance?"
**Answer**: <10 optimal, <15 ideal, <20 acceptable, >20 degraded

---

**The insight**: Tool design is about **clarity and focus**, not **feature coverage**. Simple, granular tools with minimal parameters enable AI agents to work effectively. Discovery should happen via documentation (standards), not via tool proliferation.

