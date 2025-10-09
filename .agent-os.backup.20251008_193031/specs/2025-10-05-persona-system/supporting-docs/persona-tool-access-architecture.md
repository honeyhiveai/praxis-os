# Persona Tool Access Architecture

**How personas (sub-agents) access MCP tools from within the MCP server.**

---

## 🎯 THE CHALLENGE

Personas are implemented as MCP tools that live inside the MCP server. But they need to query project standards and access other MCP functionality to do their work effectively.

**Question:** How can a persona (which IS an MCP tool) call OTHER MCP tools?

---

## ✅ THE SOLUTION: LLM Tool Calling

Personas are **AI agents with tool access**, not simple prompt wrappers. They use the LLM's native tool calling capability to invoke other MCP tools.

### Architecture Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│  User in Cursor IDE                                              │
└────────────────────────────┬────────────────────────────────────┘
                             │ MCP Protocol
                             │ "@architect review API design"
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│  MCP Server (agent_os_rag.py)                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  @mcp.tool()                                                      │
│  async def invoke_architect(task, context):                      │
│      # 1. Load persona system prompt                             │
│      system_prompt = load_persona_prompt("architect")            │
│                                                                   │
│      # 2. Define available tools for this persona                │
│      tools = [                                                    │
│          {                                                        │
│              "name": "search_standards",                          │
│              "description": "Search project standards",           │
│              "input_schema": {...}                                │
│          },                                                       │
│          {                                                        │
│              "name": "list_standards",                            │
│              "description": "List all standards in domain",       │
│              "input_schema": {...}                                │
│          }                                                        │
│      ]                                                            │
│                                                                   │
│      # 3. Call LLM with tools enabled                            │
│      response = await llm_client.messages.create(                │
│          model="claude-sonnet-4",                                 │
│          system=system_prompt,                                    │
│          messages=[{"role": "user", "content": task}],            │
│          tools=tools,  # ← ENABLE TOOL CALLING                   │
│          max_tokens=4096                                          │
│      )                                                            │
│                                                                   │
│      # 4. Handle tool use requests                               │
│      while response.stop_reason == "tool_use":                   │
│          tool_results = []                                        │
│          for tool_call in response.content:                      │
│              if tool_call.type == "tool_use":                    │
│                  # Execute tool call server-side                 │
│                  result = await execute_tool(                    │
│                      tool_call.name,                             │
│                      tool_call.input                             │
│                  )                                                │
│                  tool_results.append({                           │
│                      "tool_use_id": tool_call.id,                │
│                      "content": result                           │
│                  })                                               │
│                                                                   │
│          # Continue conversation with tool results               │
│          response = await llm_client.messages.create(            │
│              model="claude-sonnet-4",                             │
│              system=system_prompt,                                │
│              messages=[...previous, tool_results],                │
│              tools=tools,                                         │
│              max_tokens=4096                                      │
│          )                                                        │
│                                                                   │
│      # 5. Return final text response                             │
│      return response.content[0].text                             │
│                                                                   │
└──────────────┬──────────────────────────────────────────────────┘
               │
               │ When LLM calls "search_standards"
               ↓
┌─────────────────────────────────────────────────────────────────┐
│  async def execute_tool(tool_name, tool_input):                  │
│      """Execute MCP tool internally."""                          │
│      if tool_name == "search_standards":                         │
│          return await search_standards(**tool_input)             │
│      elif tool_name == "list_standards":                         │
│          return await list_standards(**tool_input)               │
│      else:                                                        │
│          raise ValueError(f"Unknown tool: {tool_name}")          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 IMPLEMENTATION DETAILS

### Step 1: Define Tool Schemas

Personas need tool definitions in the format expected by the LLM API:

```python
# mcp_server/personas/tools.py

PERSONA_TOOLS = [
    {
        "name": "search_standards",
        "description": "Semantic search over project standards. Use this to find relevant project patterns before making recommendations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query (e.g., 'API design patterns', 'error handling')"
                },
                "n_results": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "list_standards",
        "description": "List all standards in a specific domain to see what's already documented.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain to list (e.g., 'architecture', 'data', 'security')"
                }
            },
            "required": ["domain"]
        }
    },
    {
        "name": "read_standard",
        "description": "Read the full contents of a specific standard file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Relative path to standard (e.g., 'architecture/api-conventions.md')"
                }
            },
            "required": ["file_path"]
        }
    }
]
```

---

### Step 2: Tool Execution Router

Create a helper to execute tools internally:

```python
# mcp_server/personas/tool_executor.py

async def execute_persona_tool(
    tool_name: str,
    tool_input: Dict[str, Any],
    rag_engine: RAGEngine,
    base_path: Path
) -> str:
    """
    Execute a tool call from a persona.
    
    This routes tool calls from the LLM to the appropriate MCP tool
    implementation, executing them server-side.
    
    Args:
        tool_name: Name of tool to execute
        tool_input: Tool parameters from LLM
        rag_engine: RAG engine instance
        base_path: Base path to .agent-os/
    
    Returns:
        Tool result as string (JSON for structured data)
    """
    try:
        if tool_name == "search_standards":
            query = tool_input["query"]
            n_results = tool_input.get("n_results", 5)
            
            # Call RAG engine directly
            result = rag_engine.search(query=query, n_results=n_results)
            
            # Format results for LLM
            formatted = []
            for chunk in result.chunks[:n_results]:
                formatted.append({
                    "file": chunk.file_path,
                    "section": chunk.heading,
                    "content": chunk.content,
                    "relevance": chunk.score
                })
            
            return json.dumps({
                "results": formatted,
                "query_time_ms": result.query_time_ms
            })
        
        elif tool_name == "list_standards":
            domain = tool_input["domain"]
            standards_path = base_path / "standards" / domain
            
            if not standards_path.exists():
                return json.dumps({"error": f"Domain '{domain}' not found", "files": []})
            
            files = [
                str(f.relative_to(base_path / "standards"))
                for f in standards_path.glob("*.md")
            ]
            
            return json.dumps({"domain": domain, "files": files})
        
        elif tool_name == "read_standard":
            file_path = tool_input["file_path"]
            full_path = base_path / "standards" / file_path
            
            if not full_path.exists():
                return json.dumps({"error": f"Standard not found: {file_path}"})
            
            content = full_path.read_text(encoding="utf-8")
            return json.dumps({"file": file_path, "content": content})
        
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})
    
    except Exception as e:
        return json.dumps({"error": str(e)})
```

---

### Step 3: Persona Invocation with Tool Support

Update the persona invocation pattern:

```python
# mcp_server/agent_os_rag.py

async def _invoke_persona_with_tools(
    persona_identifier: str,
    task: str,
    context: Optional[str],
    rag_engine: RAGEngine,
    base_path: Path
) -> str:
    """
    Invoke persona with tool calling support.
    
    This enables personas to query standards, list files, and access
    project context while generating their reviews.
    """
    from mcp_server.personas import CORE_PERSONAS, PERSONA_TOOLS
    from mcp_server.personas.tool_executor import execute_persona_tool
    
    # Load persona config
    if persona_identifier not in CORE_PERSONAS:
        return f"Error: Unknown persona '{persona_identifier}'"
    
    persona = CORE_PERSONAS[persona_identifier]
    
    # Build initial message
    user_message = f"Task: {task}"
    if context:
        user_message += f"\n\nContext:\n{context}"
    
    messages = [{"role": "user", "content": user_message}]
    
    # Multi-turn conversation with tool support
    max_turns = 5  # Prevent infinite loops
    for turn in range(max_turns):
        response = llm_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=persona.system_prompt,
            messages=messages,
            tools=PERSONA_TOOLS  # Enable tool calling
        )
        
        # Check if LLM wants to use tools
        if response.stop_reason == "tool_use":
            # Execute all requested tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = await execute_persona_tool(
                        tool_name=block.name,
                        tool_input=block.input,
                        rag_engine=rag_engine,
                        base_path=base_path
                    )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            
            # Add assistant's tool use and tool results to conversation
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            
            # Continue loop to get next response
            continue
        
        elif response.stop_reason == "end_turn":
            # LLM is done, return final text
            text_blocks = [
                block.text for block in response.content
                if hasattr(block, "text")
            ]
            return "\n".join(text_blocks)
        
        else:
            # Unexpected stop reason
            return f"Unexpected stop reason: {response.stop_reason}"
    
    return "Error: Max conversation turns reached"


@mcp.tool()
async def invoke_architect(task: str, context: Optional[str] = None) -> str:
    """Invoke Software Architect persona with tool access."""
    return await _invoke_persona_with_tools(
        persona_identifier="architect",
        task=task,
        context=context,
        rag_engine=rag_engine,
        base_path=base_path
    )
```

---

## 💡 KEY BENEFITS

### 1. **Personas Are Context-Aware**
Personas can query project standards before making recommendations, ensuring advice is project-specific, not generic.

**Example:**
```
User: "@architect review this caching layer"
Architect: (thinks) "Let me check existing caching patterns"
Architect: (calls) search_standards("caching strategy")
Architect: (receives) "This project uses Redis with TTL=300s"
Architect: (responds) "Your design looks good, but use TTL=300s to match project standard"
```

### 2. **Personas Can Discover Existing Standards**
Before proposing a new standard, personas can check if one already exists.

**Example:**
```
Architect: "I should check if API conventions exist"
Architect: (calls) list_standards(domain="architecture")
Architect: (receives) ["api-conventions.md", "caching-strategy.md"]
Architect: (calls) read_standard(file_path="architecture/api-conventions.md")
Architect: (receives) Full file contents
Architect: "Great, API conventions exist. Let me reference them in my review."
```

### 3. **No Redundant Context Passing**
User doesn't need to manually paste project context. Personas fetch it themselves when needed.

### 4. **Intelligent Tool Use**
LLM decides WHEN to use tools (not every time), keeping responses fast and token-efficient.

---

## 🔒 SECURITY & CONSTRAINTS

### Tool Access Control

Personas have access to a **limited subset** of MCP tools:

**Allowed:**
- `search_standards` - Read-only semantic search
- `list_standards` - Read-only file listing
- `read_standard` - Read-only file access

**NOT Allowed:**
- `create_project_standard` - Blocked (requires explicit Human approval via main agent)
- `start_workflow` - Not relevant to persona work
- `complete_phase` - Not relevant to persona work
- File system writes - No direct file access

### Why Standards Creation Is Blocked

Personas can PROPOSE standards but cannot create them autonomously. The workflow is:

1. Persona proposes standard in their response text
2. Human reviews and approves
3. Human (via main agent) calls `create_project_standard()` explicitly

This preserves the **Human-in-the-loop** requirement for all standards.

---

## 📊 PERFORMANCE CONSIDERATIONS

### Token Costs

Each tool call adds tokens:
- Tool definition: ~100-200 tokens per tool (sent every turn)
- Tool use: ~50-100 tokens per call
- Tool result: Variable (100-1000 tokens depending on result)

**Mitigation:**
- Limit to 3-5 essential tools (not all MCP tools)
- Personas use tools intelligently (only when needed)
- Tool results are concise (top 3-5 chunks, not full files)

### Latency

Tool calls add round-trips:
- No tools: 1 LLM API call (~2-5 seconds)
- With 1 tool call: 2 LLM API calls (~4-10 seconds)
- With 2 tool calls: 3 LLM API calls (~6-15 seconds)

**Mitigation:**
- Max 5 conversation turns (prevents runaway tool use)
- Tools are fast (<500ms for RAG search)
- Most reviews won't need tools (generic advice)

---

## 🧪 TESTING STRATEGY

### Unit Tests

Test tool execution in isolation:

```python
async def test_execute_search_standards():
    result = await execute_persona_tool(
        tool_name="search_standards",
        tool_input={"query": "API patterns", "n_results": 3},
        rag_engine=mock_rag_engine,
        base_path=test_base_path
    )
    data = json.loads(result)
    assert "results" in data
    assert len(data["results"]) <= 3
```

### Integration Tests

Test full persona invocation with tool use:

```python
async def test_architect_uses_search_tool():
    # Set up test standard
    create_test_standard("architecture/api-conventions.md", content="REST best practices")
    
    # Invoke architect
    response = await invoke_architect(
        task="Review this REST API design",
        context="GET /users, POST /users"
    )
    
    # Verify persona queried standards (check logs or mock LLM)
    assert "search_standards" in captured_tool_calls
    assert "api-conventions.md" in response  # Referenced in review
```

---

## 📝 SUMMARY

**Personas access MCP tools via LLM tool calling:**

1. User invokes persona (e.g., `@architect review`)
2. MCP server calls LLM with persona system prompt + tool definitions
3. LLM decides to call tools (e.g., `search_standards`)
4. MCP server executes tools server-side
5. Results passed back to LLM
6. LLM generates final response with project context
7. User receives context-aware review

**This architecture enables:**
- ✅ Personas are project-aware (not generic)
- ✅ No manual context pasting required
- ✅ Human approval still required for standards
- ✅ Efficient token use (tools used only when needed)
- ✅ Fast performance (tools execute server-side)

---

**Implementation Priority:** Phase 1, Task 1.4-1.5 (First 2 personas with tool support)
