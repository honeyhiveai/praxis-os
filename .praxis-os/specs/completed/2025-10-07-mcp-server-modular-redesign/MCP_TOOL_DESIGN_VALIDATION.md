# MCP Tool Design Validation

**Validation of workflow tool design against MCP best practices.**

**Date:** 2025-10-07  
**Standards Reference:** `.praxis-os/standards/development/mcp-tool-design-best-practices.md`

---

## 🔍 Research Question

**Should workflow tools be:**
1. **Separate tool calls** (start_workflow, get_task, complete_phase) 
2. **Single parameterized tool** (workflow(action="start"))

---

## ✅ Research Answer: SEPARATE TOOLS

Based on comprehensive MCP best practices research from AWS, Anthropic, StackOne, and ModelContextProtocol.info:

**Recommendation:** **Use separate, granular tools** (our current design)

**Rationale:**
- ✅ **MCP Core Principle:** "Granular tool design - focused tools that perform specific tasks"
- ✅ **LLM Clarity:** Each tool has single, clear purpose
- ✅ **Better Documentation:** Each tool independently documented
- ✅ **Easier Testing:** Test each operation in isolation
- ✅ **Reusability:** Tools can be combined in different workflows
- ✅ **Token-Based Orchestration:** Enforce sequence without mega-tool

---

## 📊 Current Design Validation

### Our 7 Workflow Tools

```python
1. search_standards(query, n_results, filter_phase, filter_tags)
   Purpose: Semantic search over prAxIs OS documentation
   Category: RAG
   
2. start_workflow(workflow_type, target_file, options)
   Purpose: Initialize workflow session
   Category: Workflow
   
3. get_current_phase(session_id)
   Purpose: Get current phase with task list
   Category: Workflow
   
4. get_task(session_id, phase, task_number)
   Purpose: Get full task content (horizontal scaling)
   Category: Workflow
   
5. complete_phase(session_id, phase, evidence)
   Purpose: Submit evidence and advance phase
   Category: Workflow
   
6. get_workflow_state(session_id)
   Purpose: Get complete workflow state (debug/resume)
   Category: Workflow
   
7. create_workflow(name, workflow_type, phases, ...)
   Purpose: Generate new workflow framework
   Category: Framework
```

### Validation Against MCP Best Practices

| Best Practice | Our Design | ✅/❌ | Notes |
|--------------|------------|------|-------|
| **Granular Tool Design** | Each tool has single responsibility | ✅ | All tools focused |
| **Verb-Noun Naming** | start_workflow, get_task, complete_phase | ✅ | Consistent pattern |
| **Tool Categorization** | rag_tools.py, workflow_tools.py | ✅ | Clear organization |
| **Comprehensive Docs** | Docstrings with params, returns, raises | ✅ | All tools documented |
| **Token-Based Orchestration** | validation_token in responses | ✅ | Enforces sequences |
| **Tool Count < 20** | 7 tools currently | ✅ | Well under limit |
| **Progressive Integration** | Core tools, then sub-agents | ✅ | Phased approach |
| **Clear Error Handling** | Actionable error messages | ✅ | Guides correct usage |
| **Automated Testing** | Unit + integration tests | ✅ | Independent testing |
| **Performance Optimization** | Consolidated related data | ✅ | get_current_phase returns tasks |

**Score: 10/10 ✅ Full compliance with MCP best practices**

---

## 🚫 Why NOT Parameterized Mega-Tool

### Alternative Design (NOT recommended)

```python
@mcp.tool()
async def workflow(
    action: str,  # "start", "get_phase", "get_task", "complete", "get_state", "create"
    session_id: Optional[str] = None,
    workflow_type: Optional[str] = None,
    target_file: Optional[str] = None,
    phase: Optional[int] = None,
    task_number: Optional[int] = None,
    evidence: Optional[Dict] = None,
    # ... many more optional params
) -> Dict:
    """Perform workflow operations."""
    if action == "start":
        if not workflow_type or not target_file:
            raise ValueError("workflow_type and target_file required for start")
        return start_workflow_impl(workflow_type, target_file)
    
    elif action == "get_phase":
        if not session_id:
            raise ValueError("session_id required for get_phase")
        return get_current_phase_impl(session_id)
    
    elif action == "get_task":
        if not session_id or phase is None or task_number is None:
            raise ValueError("session_id, phase, and task_number required")
        return get_task_impl(session_id, phase, task_number)
    
    # ... 10+ more branches
```

### Problems with This Approach

**1. LLM Confusion**
- Which parameters for which action?
- Easy to hallucinate wrong parameter combinations
- Example: `workflow(action="get_task", workflow_type="foo")` ← wrong params

**2. Poor Error Messages**
```python
# Vague error
"Missing required parameters"

# vs Clear error (separate tools)
"session_id required. Did you call start_workflow first?"
```

**3. Complex Documentation**
```python
"""
Perform workflow operations.

:param action: One of: "start", "get_phase", "get_task", "complete", "get_state", "create"
:param session_id: Required for: get_phase, get_task, complete, get_state. Optional for: start, create
:param workflow_type: Required for: start, create. Ignored for: get_phase, get_task, complete, get_state
:param phase: Required for: get_task, complete. Ignored for: start, get_phase, get_state, create
# ... 50+ lines of parameter conditions ...
```

**4. Testing Nightmare**
```python
def test_workflow_tool():
    # Test start action
    workflow(action="start", workflow_type="...", target_file="...")
    
    # Test get_phase action
    workflow(action="get_phase", session_id="...")
    
    # Test all action/parameter combinations (15+ tests)
    # Test all error conditions (20+ tests)
    # Test parameter validation (10+ tests)
```

**5. Violates MCP Best Practices**
- ❌ Not granular (mega-function)
- ❌ Unclear purpose (does everything)
- ❌ Hard to document
- ❌ Complex parameter validation
- ❌ Poor reusability

---

## 💡 Our Design Advantages

### Advantage 1: Clear LLM Usage

```python
# LLM knows exactly what to call
await start_workflow(workflow_type="test_generation_v3", target_file="test.py")

# vs ambiguous
await workflow(action="start", workflow_type=..., target_file=...)
```

### Advantage 2: Self-Documenting

```python
# Function signature tells you everything
async def get_task(session_id: str, phase: int, task_number: int) -> Dict:
    """Get full task content (horizontal scaling)."""

# vs unclear
async def workflow(action: str, **kwargs) -> Dict:
    """Perform workflow operation based on action."""
```

### Advantage 3: Token-Based Orchestration

```python
# start_workflow returns token for next step
response = await start_workflow(...)
token = response["validation_token"]

# get_current_phase requires that token
await get_current_phase(session_id, validation_token=token)

# This enforces correct sequence WITHOUT mega-tool
```

### Advantage 4: Easy Testing

```python
# Test each tool independently
def test_start_workflow():
    result = start_workflow("test_gen", "test.py")
    assert "session_id" in result

def test_get_task():
    result = get_task("session-123", phase=1, task_number=1)
    assert "execution_steps" in result
```

### Advantage 5: Horizontal Scaling

```python
# Separate get_task tool enables one-task-at-a-time pattern
phase_data = await get_current_phase(session_id)
for task in phase_data["tasks"]:
    task_content = await get_task(session_id, phase, task["number"])
    # Work on this task
    # Request next task when ready

# This is the meta-workflow horizontal scaling principle
```

---

## 📈 Tool Count Strategy

### Current State: 7 Tools (Optimal)

- 1 RAG tool (search_standards)
- 6 Workflow tools
- **Total: 7 tools** ✅ Well under 20-tool limit

### Future State: Up to 20 Tools (Safe)

```
Current: 7 tools
+ Design validator: 3 tools → 10 total
+ Concurrency analyzer: 5 tools → 15 total
+ Test generator: 5 tools → 20 total
```

**Strategy:**
- Default: Only core tools (7)
- Opt-in: Sub-agents via `enabled_tool_groups` config
- Warning: Log if >20 tools enabled

### Why NOT Consolidate

**Consolidating workflow tools:**
- Saves: 5 tools (start, get_phase, get_task, complete, get_state → 1 tool)
- Costs: 
  - ❌ Violates MCP best practices
  - ❌ Harder for LLM to use correctly
  - ❌ More complex to maintain
  - ❌ Worse error messages
  - ❌ Breaks horizontal scaling pattern

**Not worth it:** We're at 7/20 tools, plenty of headroom

---

## ✅ Final Validation

### Design Decision: SEPARATE TOOLS ✅

**Our workflow tools design is CORRECT per MCP best practices.**

**Evidence:**
1. ✅ Research from AWS, Anthropic, StackOne confirms granular tools
2. ✅ All 10 MCP best practices satisfied
3. ✅ Tool count well under limit (7/20)
4. ✅ Clear LLM usage patterns
5. ✅ Enables horizontal scaling
6. ✅ Token-based orchestration enforces sequences

**Recommendation:** **No changes needed. Proceed with current design.**

---

## 📚 References

**New Standard Created:**
- `.praxis-os/standards/development/mcp-tool-design-best-practices.md`

**Research Sources:**
- AWS: MCP Servers with Controlled Tool Orchestration
- HaaS on SaaS: MCP Best Practices
- StackOne: Workflow Server Architecture
- ModelContextProtocol.info: Writing Effective Tools
- MCP.pm: Integration Best Practices

**Research Findings:**
- Granular tool design recommended
- Tool count monitoring critical (>20 degrades performance)
- Token-based orchestration enforces sequences
- Separate tools better for LLM clarity and testing

---

**Conclusion: Our architecture is research-validated and MCP-compliant. No design changes required.**

