# MCP Tool Design Best Practices

**Research-based guidelines for designing Model Context Protocol tools.**

**Status:** Active Standard  
**Last Updated:** 2025-10-07  
**Research Sources:** AWS, Anthropic, StackOne, ModelContextProtocol.info

---

## 🎯 Core Principle: Granular Over Parameterized

**Research Finding:** MCP best practices recommend **granular tool design** - focused tools that perform specific tasks well, rather than monolithic functions with complex parameters.

### ✅ Recommended: Separate Tools

```python
# GOOD: Granular, focused tools
@mcp.tool()
async def start_workflow(workflow_type: str, target_file: str) -> Dict:
    """Initialize workflow session."""
    # Single responsibility: start workflow

@mcp.tool()
async def get_current_phase(session_id: str) -> Dict:
    """Get current phase content."""
    # Single responsibility: retrieve phase

@mcp.tool()
async def complete_phase(session_id: str, phase: int, evidence: Dict) -> Dict:
    """Submit evidence and complete phase."""
    # Single responsibility: validate and advance
```

**Benefits:**
- ✅ Clear purpose and documentation
- ✅ Easier for LLM to understand when to use each
- ✅ Reusable across different workflows
- ✅ Simpler error handling
- ✅ Better testability

### ❌ Not Recommended: Parameterized Mega-Tool

```python
# BAD: Monolithic tool with action parameters
@mcp.tool()
async def workflow(
    action: str,  # "start", "get_phase", "complete_phase", "get_task", etc.
    session_id: Optional[str] = None,
    workflow_type: Optional[str] = None,
    phase: Optional[int] = None,
    task_number: Optional[int] = None,
    evidence: Optional[Dict] = None
) -> Dict:
    """Do workflow operations based on action parameter."""
    if action == "start":
        # ...
    elif action == "get_phase":
        # ...
    elif action == "complete_phase":
        # ...
    # ... many more branches
```

**Problems:**
- ❌ Unclear when to use which action
- ❌ Complex parameter validation (which params for which action?)
- ❌ Poor error messages (ambiguous failures)
- ❌ Harder to document comprehensively
- ❌ Difficult to test all branches
- ❌ LLM confusion about correct parameters

---

## 📊 Research-Based Guidelines

### 1. Granular Tool Design

**Source:** HaaS on SaaS MCP Best Practices

**Guideline:** Create focused tools that perform specific tasks effectively.

**Example:**
```python
# Granular workflow tools
start_workflow()        # 1 responsibility
get_current_phase()     # 1 responsibility
get_task()              # 1 responsibility
complete_phase()        # 1 responsibility
get_workflow_state()    # 1 responsibility
```

**Why:** Each tool has a clear purpose that the LLM can understand and invoke correctly.

---

### 2. Tool Categorization

**Source:** HaaS on SaaS, AWS MCP Orchestration

**Guideline:** Organize tools by domain and purpose to maintain clear boundaries.

**Example:**
```python
# Tools organized by category
server/tools/
├── rag_tools.py          # search_standards
├── workflow_tools.py     # start_workflow, get_task, complete_phase
└── sub_agent_tools/
    ├── design_validator.py
    └── concurrency_analyzer.py
```

**Why:** Clear categorization helps with:
- Selective loading (stay under 20-tool limit)
- Easier maintenance
- Better discoverability

---

### 3. Token-Based Orchestration

**Source:** AWS MCP Server with Controlled Tool Orchestration

**Guideline:** Use validation tokens to enforce tool execution order and workflow sequences.

**Example:**
```python
@mcp.tool()
async def start_workflow(workflow_type: str) -> Dict:
    """Initialize workflow session."""
    session_id = generate_session_id()
    validation_token = generate_token(session_id, phase=1)
    
    return {
        "session_id": session_id,
        "current_phase": 1,
        "validation_token": validation_token,  # ← Token for next step
        "next_action": "get_current_phase"
    }

@mcp.tool()
async def get_current_phase(session_id: str, validation_token: str) -> Dict:
    """Get current phase content (requires token from start_workflow)."""
    if not validate_token(validation_token, session_id):
        raise ValueError("Invalid token. Did you call start_workflow first?")
    
    # ... return phase content with next token
```

**Why:**
- Enforces correct workflow order
- Prevents skipping required steps
- Provides clear error messages
- No need for monolithic tool with complex state

---

### 4. Consistent Naming Conventions

**Source:** HaaS on SaaS MCP Best Practices

**Guideline:** Use verb-noun pattern for tool names.

**Good Examples:**
```
search_standards      # verb-noun
start_workflow        # verb-noun
get_current_phase     # verb-noun-modifier
complete_phase        # verb-noun
create_workflow       # verb-noun
```

**Bad Examples:**
```
standards             # noun only (what action?)
workflow              # noun only (ambiguous)
phase                 # noun only (get? set? delete?)
do_workflow_thing     # vague verb
```

---

### 5. Comprehensive Documentation

**Source:** HaaS on SaaS, ModelContextProtocol.info

**Guideline:** Each tool must have detailed docstring with parameters, return values, and examples.

**Example:**
```python
@mcp.tool()
async def get_task(
    session_id: str,
    phase: int,
    task_number: int
) -> Dict[str, Any]:
    """
    Get full content for a specific task (horizontal scaling).
    
    Retrieves complete task content including execution steps and commands.
    Follows meta-workflow principle: work on one task at a time.
    
    :param session_id: Workflow session identifier (from start_workflow)
    :param phase: Phase number (0-8)
    :param task_number: Task number within the phase (1-10)
    :return: Dictionary with complete task content and structured execution steps
    :raises ValueError: If session_id invalid or task not found
    :raises KeyError: If phase/task_number out of range
    
    Example:
        # Start workflow first
        response = await start_workflow("test_generation_v3", "myfile.py")
        session_id = response["session_id"]
        
        # Get Phase 1, Task 1
        task = await get_task(session_id, phase=1, task_number=1)
        
        # Execute task steps
        for step in task["execution_steps"]:
            # ... execute step
    """
```

**Why:** 
- LLM understands when and how to use tool
- Reduces hallucinated parameters
- Provides usage examples

---

### 6. Automated Testing

**Source:** HaaS on SaaS MCP Best Practices

**Guideline:** Test tools independently before LLM integration.

**Example:**
```python
def test_workflow_tools_sequence():
    """Test workflow tools execute in correct sequence."""
    # Test start_workflow
    start_response = start_workflow("test_generation_v3", "test.py")
    assert "session_id" in start_response
    assert "validation_token" in start_response
    
    # Test get_current_phase with token
    phase_response = get_current_phase(
        session_id=start_response["session_id"],
        validation_token=start_response["validation_token"]
    )
    assert phase_response["phase"] == 1
    
    # Test invalid token fails
    with pytest.raises(ValueError):
        get_current_phase(session_id=start_response["session_id"], 
                         validation_token="invalid")
```

**Why:**
- Catch bugs before LLM interaction
- Validate orchestration logic
- Document expected behavior

---

### 7. Tool Count Management

**Source:** Microsoft Research, StackOne

**Guideline:** Monitor tool count and use selective loading to stay under performance threshold.

**Recommendations:**
- **<10 tools:** Optimal LLM performance
- **10-20 tools:** Good performance
- **>20 tools:** Performance degrades (up to 85%)
- **>40 tools:** Platform hard limits may apply

**Strategy:**
```python
# Selective tool loading
def register_all_tools(
    mcp: FastMCP,
    enabled_groups: List[str] = ["rag", "workflow"]  # Default: core only
) -> int:
    tool_count = 0
    
    if "rag" in enabled_groups:
        tool_count += register_rag_tools(mcp)
    
    if "workflow" in enabled_groups:
        tool_count += register_workflow_tools(mcp)
    
    # Sub-agents opt-in
    if "design_validator" in enabled_groups:
        tool_count += register_design_validator_tools(mcp)
    
    if tool_count > 20:
        logger.warning(f"⚠️  {tool_count} tools exceeds recommended limit (20)")
    
    return tool_count
```

---

### 8. Progressive Integration

**Source:** HaaS on SaaS MCP Best Practices

**Guideline:** Start with core tools, expand incrementally.

**Approach:**
```
Phase 1: Core tools (7 tools)
  - search_standards
  - start_workflow
  - get_current_phase
  - get_task
  - complete_phase
  - get_workflow_state
  - create_workflow

Phase 2: First sub-agent (10 tools total)
  - Add design_validator_tools (3 tools)
  
Phase 3: Second sub-agent (15 tools total)
  - Add concurrency_analyzer_tools (5 tools)

Phase 4: Monitor and optimize
  - Measure LLM accuracy
  - Adjust tool count based on performance
```

---

### 9. Clear Error Handling

**Source:** ModelContextProtocol.info

**Guideline:** Provide actionable error messages that guide LLM to correct usage.

**Good Error Messages:**
```python
# GOOD: Actionable, specific
raise ValueError(
    f"Invalid session_id: {session_id}. "
    "Did you call start_workflow first? "
    "Session may have expired (max 24 hours)."
)

# GOOD: Suggests fix
raise ValueError(
    f"Phase {phase} not started. Current phase is {current_phase}. "
    "Call get_current_phase to see available tasks."
)
```

**Bad Error Messages:**
```python
# BAD: Vague
raise ValueError("Invalid input")

# BAD: No context
raise KeyError(phase)

# BAD: Technical jargon
raise DatabaseException("FK constraint violation on workflow_sessions")
```

---

### 10. Performance Optimization

**Source:** ModelContextProtocol.info, StackOne

**Guidelines:**
- **Consolidate related functionality** - Don't split unnecessarily
- **Set reasonable defaults** - Reduce required parameters
- **Optimize context management** - Return only needed data
- **Cache frequently accessed data** - Reduce redundant calls

**Example:**
```python
# GOOD: Related functionality together
@mcp.tool()
async def get_current_phase(session_id: str) -> Dict:
    """Get current phase with task list (consolidated)."""
    return {
        "phase": 1,
        "phase_name": "Setup",
        "tasks": [
            {"number": 1, "name": "Task 1", "status": "pending"},
            {"number": 2, "name": "Task 2", "status": "pending"}
        ],
        "validation_token": "..."
    }

# BAD: Unnecessary split
@mcp.tool()
async def get_current_phase_number(session_id: str) -> int:
    return 1

@mcp.tool()
async def get_current_phase_name(session_id: str) -> str:
    return "Setup"

@mcp.tool()
async def get_current_phase_tasks(session_id: str) -> List:
    return [...]
```

---

## 🎯 Decision Framework

### When to use SEPARATE tools:

- ✅ Actions are conceptually distinct
- ✅ Different parameters required
- ✅ Different error conditions
- ✅ Used independently in different contexts
- ✅ Different authorization requirements

**Example:** `start_workflow`, `get_task`, `complete_phase` are distinct operations

### When to use PARAMETERIZED tool:

- ✅ Actions are variations of same operation
- ✅ Shared parameters and error handling
- ✅ Always used together in sequence
- ✅ Implementation is trivial dispatch

**Example:** `search(query, filter="all")` vs `search_standards()`, `search_usage()` (acceptable either way)

---

## 📋 Checklist for New Tools

Before adding a new MCP tool, verify:

- [ ] Tool has single, clear responsibility
- [ ] Tool name follows verb-noun pattern
- [ ] Complete docstring with params, returns, raises, example
- [ ] Parameters have type hints
- [ ] Error messages are actionable
- [ ] Tool can be tested independently
- [ ] Tool count impact assessed (<20 total?)
- [ ] Tool categorized correctly (rag/workflow/sub_agent)
- [ ] Orchestration tokens used if part of sequence
- [ ] Documentation updated

---

## 🚀 Application to Agent OS

### Current Workflow Tools (7 tools) - ✅ GOOD DESIGN

Our current workflow tools follow MCP best practices:

```python
# Granular, focused tools
1. start_workflow()        # Initialize session
2. get_current_phase()     # Retrieve phase
3. get_task()              # Retrieve task (horizontal scaling)
4. complete_phase()        # Validate and advance
5. get_workflow_state()    # Debug/resume
6. create_workflow()       # Generate framework
7. search_standards()      # RAG search
```

**Why this is good:**
- Each tool has single responsibility
- Clear when to use each
- Easy to document
- Testable independently
- Enables horizontal scaling (get_task)

**Alternative (NOT recommended):**
```python
# Parameterized mega-tool
workflow(action="start" | "get_phase" | "get_task" | "complete" | "get_state" | "create")
```

This would save tool count but:
- ❌ Harder for LLM to understand
- ❌ Complex parameter validation
- ❌ Poor error messages
- ❌ Violates MCP best practices

---

## 📚 References

- [AWS: MCP Servers with Controlled Tool Orchestration](https://aws.amazon.com/blogs/devops/flexibility-to-framework-building-mcp-servers-with-controlled-tool-orchestration/)
- [HaaS on SaaS: What is MCP?](https://haasonsaas.com/blog/what-is-mcp)
- [StackOne: Rethinking MCP - From App to Workflow Servers](https://www.stackone.com/blog/rethinking-mcp-from-app-to-workflow-servers)
- [ModelContextProtocol.info: Writing Effective Tools](https://modelcontextprotocol.info/docs/tutorials/writing-effective-tools/)
- [MCP.pm: MCP Integration Best Practices](https://mcp.pm/posts/mcp-integration-best-practices)

---

**Follow these MCP best practices to create high-quality, LLM-friendly tools that maintain performance even as the tool count grows.**
