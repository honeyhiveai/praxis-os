# Workflow Tools Extensibility Analysis
**Date**: 2025-10-15  
**Goal**: Analyze workflow tools through lens of domain-appropriate complexity  
**Question**: Should workflow tools be consolidated like aos_browser, or stay granular?

---

## Current Workflow Inventory

### Discovered Workflows (7 total)

From `.praxis-os/workflows/`:
1. **agent_os_upgrade_v1** (new!) - Self-upgrade workflow
2. **spec_creation_v1** (new!) - Create project specifications
3. **spec_execution_v1** - Execute tasks from tasks.md
4. **workflow_creation_v1** - Meta-workflow for creating workflows
5. **standards_creation_v1** - Create standards documentation (in universal/)

From code references:
6. **test_generation_v3** - Generate test suites
7. **production_code_v2** - Generate production code

### Workflow Patterns Emerging

**Code Generation Workflows** (output: code files)
- test_generation_v3
- production_code_v2

**Documentation Workflows** (output: documentation)
- standards_creation_v1
- spec_creation_v1

**Meta-Workflows** (output: workflows/specs)
- workflow_creation_v1
- spec_execution_v1

**System Workflows** (output: system changes)
- agent_os_upgrade_v1

### Extensibility Needs

**Likely future workflows** (based on patterns):
- api_documentation_v1 (documentation)
- database_migration_v1 (system)
- deployment_workflow_v1 (system)
- refactoring_workflow_v1 (code generation)
- code_review_workflow_v1 (analysis)
- security_audit_workflow_v1 (analysis)
- performance_optimization_v1 (analysis + code)

**Estimate**: 10-20 workflows total in mature system

---

## Current Tool Design: Granular Workflow Tools

### Tool Inventory (8 workflow tools)

```python
1. start_workflow(workflow_type, target_file, options)
2. get_current_phase(session_id)
3. get_task(session_id, phase, task_number)
4. complete_phase(session_id, phase, evidence)
5. get_workflow_state(session_id)
6. create_workflow(name, workflow_type, phases, ...)
7. validate_workflow(workflow_path)
8. current_date()  # utility
```

**Total tool count**: 11 (including RAG, server, browser)

### Design Analysis: Are These Appropriately Granular?

Let's apply the aos_browser lens:

**Question 1: Is this a single coherent domain?**

❌ NO - These are different domains:
- **Workflow Execution** (start, get_phase, get_task, complete_phase, get_state)
- **Workflow Creation** (create_workflow)
- **Workflow Validation** (validate_workflow)
- **Utility** (current_date)

**Analysis**: Unlike aos_browser (single domain: browser automation), workflow tools span multiple domains.

**Question 2: Do all operations share context?**

⚠️ PARTIALLY:
- Execution tools share session_id
- Creation/validation don't use session_id
- Different contexts for different tool groups

**Analysis**: Not like aos_browser where session_id is always required.

**Question 3: Are operations sequential on same entity?**

✅ YES (for execution tools):
- start_workflow → get_current_phase → get_task → complete_phase → get_workflow_state
- This IS sequential like browser operations

**But**: create_workflow and validate_workflow are independent operations

**Question 4: What's the tool count impact?**

✅ NO PROBLEM:
- Current: 8 workflow tools
- Total: 11 tools (optimal range)
- Consolidating wouldn't gain us anything (not approaching 20-tool limit)

**Question 5: Does action parameter add clarity?**

❌ NO:
```python
# Would be confusing
workflow(action="start", ...)
workflow(action="get_phase", ...)
workflow(action="complete_phase", ...)
workflow(action="create", ...)
workflow(action="validate", ...)
```

**Why confusing?**:
- start vs. create (both initialize something)
- get_phase vs. get_task (need both, action parameter doesn't help)
- complete_phase (verb-noun doesn't fit action pattern)

### Verdict: Current Granular Design Is CORRECT

**Reasons**:
1. ✅ Multiple domains (execution, creation, validation)
2. ✅ Different purposes (start vs. query vs. mutate vs. create vs. validate)
3. ✅ Tool count not a problem (8 tools is fine)
4. ✅ Action parameter would confuse, not clarify
5. ✅ Operations are conceptually distinct (not variations)

**Contrast with aos_browser**:
- Browser: Single domain (browser automation) → parameterized
- Workflows: Multiple domains (execution, creation, validation) → granular

---

## The Real Question: Workflow Discovery & Extensibility

### Current Approach: No Discovery Tool

**How agents find workflows today**:
1. User tells agent: "use test_generation_v3"
2. Agent calls: `start_workflow("test_generation_v3", "file.py")`

**Problem**: Agent doesn't know which workflows exist or when to use them

### Discovery Options Analysis

#### Option 1: Index Workflows in RAG (Current - Proposed to Remove)

**Approach**: Index workflow metadata.json files in RAG

**Current state**: Indexing ALL 137 workflow .md files (pollution)

**Proposed fix**: Index only metadata.json (4 files)

**How it works**:
```python
# Agent searches for workflows
result = search_standards("workflow for test generation")
# Returns metadata.json content
# Agent extracts workflow_type: "test_generation_v3"
# Agent calls start_workflow("test_generation_v3", ...)
```

**Pros**:
- ✅ No new tools
- ✅ Semantic search (flexible queries)
- ✅ Works with existing search_standards tool

**Cons**:
- ❌ Mixes documentation (standards) with tools (workflows)
- ❌ RAG search for small curated set (7 workflows) seems overkill
- ❌ Still have indexing/caching overhead

#### Option 2: list_workflows Tool (Add 1 Tool)

**Approach**: New tool that returns all workflow metadata

```python
@mcp.tool()
async def list_workflows(
    category: Optional[str] = None  # "code_generation", "documentation", "system"
) -> Dict[str, Any]:
    """
    List available workflows with metadata.
    
    Returns complete workflow information for selection.
    Agents read descriptions and choose appropriate workflow.
    
    Args:
        category: Optional filter ("code_generation", "documentation", "system", "meta")
    
    Returns:
        {
            "workflows": [
                {
                    "workflow_type": "test_generation_v3",
                    "category": "code_generation",
                    "description": "Generate comprehensive test suites...",
                    "total_phases": 8,
                    "estimated_duration": "2-4 hours",
                    "best_for": ["Python", "pytest", "unit tests"],
                    "primary_outputs": ["test file", "coverage report"],
                    "when_to_use": "Need to generate unit tests for Python code"
                },
                {
                    "workflow_type": "workflow_creation_v1",
                    "category": "meta",
                    "description": "Create new AI-assisted workflows...",
                    ...
                }
            ],
            "total": 7,
            "categories": ["code_generation", "documentation", "system", "meta"]
        }
    """
    # Load all metadata.json files
    workflows = []
    workflows_dir = Path(".praxis-os/workflows")
    
    for metadata_path in workflows_dir.glob("*/metadata.json"):
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        # Enhance with category (inferred from metadata or explicit)
        metadata["category"] = _infer_category(metadata)
        workflows.append(metadata)
    
    # Filter by category if requested
    if category:
        workflows = [w for w in workflows if w.get("category") == category]
    
    return {
        "workflows": workflows,
        "total": len(workflows),
        "categories": list(set(w["category"] for w in workflows))
    }
```

**Tool count**: 12 (still optimal range)

**How it works**:
```python
# Agent discovers workflows
User: "Generate tests for my Python file"
Agent: Let me find the right workflow...
  → list_workflows(category="code_generation")
  → Returns test_generation_v3
  → start_workflow("test_generation_v3", "myfile.py")
```

**Pros**:
- ✅ Fast (direct file read, no RAG)
- ✅ Complete metadata (not chunked)
- ✅ Filterable by category
- ✅ No RAG pollution
- ✅ Clean separation (workflows as tools, not documentation)

**Cons**:
- ⚠️ +1 tool (12 total, but still optimal)
- ⚠️ Not semantic search (must match category exactly)
- ⚠️ Agent must read through full list

#### Option 3: Workflow Selection Standard (No New Tools)

**Approach**: Write a standard that teaches agents about workflows

**File**: `standards/universal/workflows/workflow-selection-guide.md`

**Content**:
```markdown
# Workflow Selection Guide

**Keywords**: workflow selection, which workflow to use, test generation, workflow creation, spec execution, standards creation, code generation, documentation workflow

## Quick Reference

| Need | Workflow | Category |
|------|----------|----------|
| Generate tests | test_generation_v3 | code_generation |
| Create workflow | workflow_creation_v1 | meta |
| Execute spec | spec_execution_v1 | meta |
| Create standards | standards_creation_v1 | documentation |
| Create project spec | spec_creation_v1 | documentation |
| Upgrade Agent OS | agent_os_upgrade_v1 | system |
| Generate production code | production_code_v2 | code_generation |

## By Category

### Code Generation Workflows

#### test_generation_v3

**When to use:**
- Need to generate unit tests for Python code
- Want pytest-based test suite with fixtures
- Need coverage analysis
- Working with existing codebase

**Best for:**
- Python projects
- Unit testing
- TDD workflows

**Start command:**
```python
start_workflow(
    workflow_type="test_generation_v3",
    target_file="path/to/source.py"
)
```

... (detailed descriptions for each workflow)
```

**How it works**:
```python
# Agent discovers workflows
User: "Generate tests for my Python file"
Agent: Let me find the right workflow...
  → search_standards("how to generate tests which workflow")
  → Returns workflow-selection-guide.md
  → Reads: "Use test_generation_v3 for test generation"
  → start_workflow("test_generation_v3", "myfile.py")
```

**Pros**:
- ✅ No new tools
- ✅ No RAG pollution (1 standard file, not 137 workflow files)
- ✅ RAG-optimized (keywords, examples, natural language)
- ✅ Semantic search works (flexible queries)
- ✅ One source of truth
- ✅ Easy to maintain

**Cons**:
- ⚠️ Indirect (search → read → extract workflow_type)
- ⚠️ Requires well-written standard
- ⚠️ Agent must parse text (not structured data)

---

## Extensibility Considerations

### How Will This Scale?

**Today**: 7 workflows  
**Future**: 10-20 workflows  
**Mature system**: 30-50 workflows?

### Option 1 (RAG) Scaling

**7 workflows**: 7 metadata.json chunks  
**20 workflows**: 20 metadata.json chunks  
**50 workflows**: 50 metadata.json chunks

**RAG impact**: Minimal (metadata is small, well-structured)

**Search quality**: May degrade as workflow count increases (more similar descriptions)

### Option 2 (list_workflows) Scaling

**7 workflows**: Returns 7 workflow objects  
**20 workflows**: Returns 20 workflow objects  
**50 workflows**: Returns 50 workflow objects (might need pagination)

**Performance**: Fast (direct file read)

**Agent UX**: May need to add search/filter parameters:
```python
list_workflows(
    category="code_generation",
    search_query="test generation",  # keyword search
    language="python"  # filter by target language
)
```

### Option 3 (Standards) Scaling

**7 workflows**: 1 standard document (~500 lines)  
**20 workflows**: 1 standard document (~1500 lines) or split by category  
**50 workflows**: Multiple standard documents by category

**Maintainability**: Requires updates when workflows added

**Search quality**: Good (well-written standards are RAG-optimized)

---

## Domain Analysis: Should Workflows Be One Tool?

### Comparing to aos_browser

**aos_browser domain**:
- Single entity: browser page/session
- Single context: session_id (always required)
- Sequential operations: navigate → wait → click → type → screenshot
- Operation types: 20+ browser actions
- **Consolidation makes sense**

**Workflow domain**:
- Multiple entities: workflow sessions, workflow metadata, workflow files
- Mixed contexts: session_id for execution, file paths for creation/validation
- Mixed operations: execute, create, validate
- Operation types: 8 operations across 3 domains
- **Consolidation doesn't make sense**

### What If We Did Consolidate?

```python
# HYPOTHETICAL: Consolidated workflow tool
@mcp.tool()
async def workflow(
    action: str,  # "start" | "get_phase" | "get_task" | "complete" | 
                  # "get_state" | "create" | "validate" | "list"
    
    # Execution context
    session_id: Optional[str] = None,
    workflow_type: Optional[str] = None,
    target_file: Optional[str] = None,
    phase: Optional[int] = None,
    task_number: Optional[int] = None,
    evidence: Optional[Dict] = None,
    options: Optional[Dict] = None,
    
    # Creation context
    name: Optional[str] = None,
    phases: Optional[List[str]] = None,
    target_language: Optional[str] = None,
    
    # Validation context
    workflow_path: Optional[str] = None,
    
    # Discovery context
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """Unified workflow operations."""
    
    if action == "start":
        # start_workflow
        if not workflow_type or not target_file:
            raise ValueError("start requires workflow_type and target_file")
        return workflow_engine.start_workflow(workflow_type, target_file, options)
    
    elif action == "get_phase":
        # get_current_phase
        if not session_id:
            raise ValueError("get_phase requires session_id")
        return workflow_engine.get_current_phase(session_id)
    
    elif action == "get_task":
        # get_task
        if not session_id or phase is None or task_number is None:
            raise ValueError("get_task requires session_id, phase, task_number")
        return workflow_engine.get_task(session_id, phase, task_number)
    
    elif action == "complete":
        # complete_phase
        if not session_id or phase is None or not evidence:
            raise ValueError("complete requires session_id, phase, evidence")
        return workflow_engine.complete_phase(session_id, phase, evidence)
    
    elif action == "get_state":
        # get_workflow_state
        if not session_id:
            raise ValueError("get_state requires session_id")
        return workflow_engine.get_workflow_state(session_id)
    
    elif action == "create":
        # create_workflow
        if not name or not workflow_type or not phases:
            raise ValueError("create requires name, workflow_type, phases")
        return framework_generator.create_workflow(name, workflow_type, phases, ...)
    
    elif action == "validate":
        # validate_workflow
        if not workflow_path:
            raise ValueError("validate requires workflow_path")
        return workflow_validator.validate(workflow_path)
    
    elif action == "list":
        # list_workflows
        return list_workflows_internal(category)
    
    else:
        raise ValueError(f"Unknown action: {action}")
```

### Problems with Consolidation

**1. Confusing parameter validation**
- Which parameters for which action?
- Error messages complex: "start requires workflow_type and target_file"
- LLM must remember parameter requirements per action

**2. Poor semantics**
- workflow(action="start") vs. start_workflow()
- workflow(action="complete") vs. complete_phase()
- Action names don't match natural language well

**3. Mixed domains**
- Execution (start, get_phase, complete) vs. Creation (create) vs. Validation (validate) vs. Discovery (list)
- No coherence like aos_browser (single domain: browser)

**4. No tool count benefit**
- Current: 8 workflow tools → 11 total tools (optimal)
- Consolidated: 1 workflow tool → 4 total tools (over-optimized?)
- Not approaching 20-tool limit, so no need to consolidate

**5. Harder to extend**
- Add new workflow operation = add new action type
- vs. Add new tool (clear separation)

### Verdict: Keep Granular Design

**Workflow tools should stay granular** because:
1. ✅ Multiple domains (not single like browser)
2. ✅ Different purposes (start vs. query vs. mutate vs. create)
3. ✅ Tool count not a problem (8 tools is fine)
4. ✅ Clear semantics (start_workflow is clearer than workflow(action="start"))
5. ✅ Easy to extend (add new tool vs. add new action branch)

---

## Recommendation: Hybrid Approach

### Core Execution Tools: Keep Granular (Current Design) ✅

```python
# Workflow execution (5 tools)
start_workflow(workflow_type, target_file, options)
get_current_phase(session_id)
get_task(session_id, phase, task_number)
complete_phase(session_id, phase, evidence)
get_workflow_state(session_id)

# Workflow authoring (2 tools)
create_workflow(name, workflow_type, phases, ...)
validate_workflow(workflow_path)

# Utility (1 tool)
current_date()
```

**Why**: Different domains, clear semantics, optimal tool count

### Discovery: Add list_workflows Tool (Recommended)

```python
# Workflow discovery (1 new tool)
list_workflows(category=None)
```

**Why**:
- Fast, structured data
- No RAG pollution
- Clean separation (workflows as tools)
- Filterable by category
- Total: 12 tools (still optimal)

**Alternative**: Use workflow-selection-guide.md standard (no new tool)

---

## Action Items

### Immediate (This Week)

1. **Decision**: list_workflows tool OR workflow-selection-guide.md standard?

   **Recommend**: list_workflows tool
   - Reason: Structured data is better for agent selection
   - Reason: Fast, no RAG overhead
   - Reason: 12 tools is still optimal range
   - Reason: Clean separation of concerns

2. **Remove workflows from RAG indexing**
   - Current: Indexing 137 workflow .md files
   - After: Index 0 workflow files
   - Impact: 60% smaller index, better search quality

3. **Add category field to workflow metadata.json**
   ```json
   {
     "workflow_type": "test_generation_v3",
     "category": "code_generation",  // NEW
     "version": "1.0.0",
     ...
   }
   ```

4. **Implement list_workflows tool**
   - Load all metadata.json files
   - Add category inference
   - Add filtering by category

### Short-Term (Next 2 Weeks)

5. **Test workflow discovery**
   - Agent asks: "which workflow for testing?"
   - Agent calls: list_workflows(category="code_generation")
   - Agent selects: test_generation_v3
   - Agent starts: start_workflow("test_generation_v3", ...)

6. **Create workflow-selection-guide.md** (as backup/documentation)
   - Even if we add list_workflows, the standard is useful
   - Provides natural language guidance
   - Searchable via search_standards

7. **Add workflow categories to documentation**
   - Document category taxonomy
   - Update workflow metadata standards

### Long-Term (Ongoing)

8. **Monitor tool count**
   - Current: 11 tools (optimal)
   - With list_workflows: 12 tools (still optimal)
   - Target: <15 tools
   - Warning threshold: >20 tools

9. **Consider future extensions**
   - search_workflows(query) - semantic search over workflow descriptions?
   - get_workflow_metadata(workflow_type) - get metadata without starting?
   - pause_workflow(session_id) - pause and resume?
   - fork_workflow(session_id, new_target) - branch from current state?

---

## Conclusion

### Key Insights

1. **Workflow tools should stay granular** (unlike aos_browser)
   - Multiple domains (execution, creation, validation)
   - Different purposes (not variations of same operation)
   - Tool count not a problem

2. **Discovery is the gap**
   - Agents don't know which workflows exist
   - Need structured access to workflow metadata

3. **list_workflows tool is best solution**
   - Clean, fast, structured
   - No RAG pollution
   - 12 tools still optimal
   - Extensible (add filters as needed)

4. **Don't index workflows in RAG**
   - Workflows are tools, not documentation
   - Mixing concerns (documentation vs. tool discovery)
   - Better to provide structured access

### Domain-Appropriate Complexity Applied

**aos_browser**: Complex, parameterized (CORRECT)
- Single domain (browser automation)
- Shared context (session_id)
- 20+ operations on same entity
- Tool count economics (1 tool vs. 20 tools)

**Workflow tools**: Simple, granular (CORRECT)
- Multiple domains (execution, creation, validation)
- Mixed contexts (session_id, file paths)
- 8 distinct operations across domains
- Tool count not a problem (8 tools is fine)

**The principle**: Match tool complexity to domain complexity
- Complex, coherent domain → parameterized tool
- Multiple domains → granular tools

