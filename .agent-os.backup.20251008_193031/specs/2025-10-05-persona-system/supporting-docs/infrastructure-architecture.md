# Infrastructure & Network Architecture

**Understanding the process topology, communication channels, and endpoint awareness.**

---

## 🏗️ PROCESS TOPOLOGY

### Where Everything Runs

```
┌─────────────────────────────────────────────────────────────────┐
│  LOCAL MACHINE (User's Computer)                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Process 1: Cursor IDE (Electron App)                     │  │
│  │  - User interface                                          │  │
│  │  - MCP client built-in                                     │  │
│  │  - Manages stdio connections to MCP servers               │  │
│  └────────────────┬───────────────────────────────────────────┘  │
│                   │ stdio (stdin/stdout pipes)                    │
│                   │ NOT network sockets                           │
│                   ↓                                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Process 2: MCP Server (Python)                           │  │
│  │  File: .agent-os/mcp_server/agent_os_rag.py              │  │
│  │                                                            │  │
│  │  Components:                                               │  │
│  │  ├─ FastMCP server (stdio transport)                      │  │
│  │  ├─ RAG Engine (LanceDB local)                            │  │
│  │  ├─ Workflow Engine                                       │  │
│  │  ├─ Tool handlers (search_standards, invoke_architect)    │  │
│  │  └─ HTTP client (for calling LLM APIs)                    │  │
│  │                                                            │  │
│  │  Listens on: stdin (reads MCP requests)                   │  │
│  │  Writes to: stdout (sends MCP responses)                  │  │
│  │  No network port exposed                                   │  │
│  └────────────────┬───────────────────────────────────────────┘  │
│                   │ HTTPS (outbound only)                         │
│                   ↓                                               │
└───────────────────┼───────────────────────────────────────────────┘
                    │
                    │ Internet
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│  REMOTE: Anthropic API (api.anthropic.com)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Claude Sonnet 4 Inference                                │  │
│  │  - Receives: system prompt, messages, tool definitions    │  │
│  │  - Returns: text response OR tool_use requests            │  │
│  │  - Stateless (no awareness of MCP server internals)       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔌 COMMUNICATION CHANNELS

### Channel 1: Cursor ↔ MCP Server (stdio)

**Protocol:** JSON-RPC over stdio (NOT HTTP/network)

**Why stdio?**
- No network ports to manage
- No firewall issues
- Cursor spawns and manages the Python process
- Automatic cleanup when Cursor closes

**Configuration:** `.cursor/mcp.json`
```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.agent-os/venv/bin/python",
      "args": ["-m", "mcp_server.agent_os_rag"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.agent-os"
      }
    }
  }
}
```

**Cursor does:**
1. Spawns Python process via `command + args`
2. Opens stdin/stdout pipes to the process
3. Sends JSON-RPC requests to stdin
4. Reads JSON-RPC responses from stdout

**Example MCP request (Cursor → MCP Server):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "invoke_architect",
    "arguments": {
      "task": "Review this API design",
      "context": "..."
    }
  }
}
```

**Example MCP response (MCP Server → Cursor):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Architecture Review:\n\n🎯 Assessment:\n..."
      }
    ]
  }
}
```

---

### Channel 2: MCP Server ↔ LLM API (HTTPS)

**Protocol:** HTTPS (REST API)

**Why HTTPS?**
- LLM runs remotely (Anthropic's servers)
- Standard web API
- Authenticated via API key

**Request Flow:**

```python
# Inside MCP Server (agent_os_rag.py)

@mcp.tool()
async def invoke_architect(task: str, context: str) -> str:
    # This function runs in MCP server process (LOCAL)
    
    # Load persona prompt (from local filesystem)
    system_prompt = load_persona_prompt("architect")
    
    # Call remote LLM API via HTTPS
    response = llm_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,      # Sent to remote API
        messages=[{"role": "user", "content": task}],
        tools=[                     # Tool definitions sent to API
            {
                "name": "search_standards",
                "description": "Search project standards",
                "input_schema": {...}
            }
        ]
    )
    
    # Response comes back from remote API
    # Could be text OR tool_use request
    
    return response.content[0].text
```

**Example HTTPS request (MCP Server → Anthropic API):**
```http
POST https://api.anthropic.com/v1/messages
Content-Type: application/json
x-api-key: sk-ant-...
anthropic-version: 2023-06-01

{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 4096,
  "system": "You are a Senior Software Architect...",
  "messages": [
    {"role": "user", "content": "Review this API design: ..."}
  ],
  "tools": [
    {
      "name": "search_standards",
      "description": "Search project standards",
      "input_schema": {
        "type": "object",
        "properties": {
          "query": {"type": "string"}
        }
      }
    }
  ]
}
```

**Example HTTPS response (Anthropic API → MCP Server):**

**Option A: Text response (no tool use)**
```json
{
  "id": "msg_123",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Architecture Review:\n\n🎯 Assessment:\nYour API design looks solid..."
    }
  ],
  "stop_reason": "end_turn"
}
```

**Option B: Tool use request**
```json
{
  "id": "msg_123",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Let me check existing API conventions first."
    },
    {
      "type": "tool_use",
      "id": "toolu_456",
      "name": "search_standards",
      "input": {
        "query": "API design patterns REST conventions"
      }
    }
  ],
  "stop_reason": "tool_use"
}
```

---

## 🔄 COMPLETE REQUEST FLOW WITH TOOL USE

### Sequence Diagram

```
User        Cursor       MCP Server         LLM API          RAG Engine
 │            │               │                 │                 │
 │   Types    │               │                 │                 │
 │ "@architect│               │                 │                 │
 │  review"   │               │                 │                 │
 ├───────────>│               │                 │                 │
 │            │               │                 │                 │
 │            │ JSON-RPC      │                 │                 │
 │            │ invoke_       │                 │                 │
 │            │ architect()   │                 │                 │
 │            ├──────────────>│                 │                 │
 │            │  (via stdio)  │                 │                 │
 │            │               │                 │                 │
 │            │               │ HTTPS POST      │                 │
 │            │               │ /v1/messages    │                 │
 │            │               │ (system prompt  │                 │
 │            │               │  + tools def)   │                 │
 │            │               ├────────────────>│                 │
 │            │               │                 │                 │
 │            │               │                 │ (Inference)     │
 │            │               │                 │ "I need to      │
 │            │               │                 │  search first"  │
 │            │               │                 │                 │
 │            │               │ HTTPS 200       │                 │
 │            │               │ {tool_use:      │                 │
 │            │               │  search_        │                 │
 │            │               │  standards}     │                 │
 │            │               │<────────────────┤                 │
 │            │               │                 │                 │
 │            │               │ (MCP Server     │                 │
 │            │               │  executes tool  │                 │
 │            │               │  locally)       │                 │
 │            │               │                 │                 │
 │            │               │ search_standards("API patterns")  │
 │            │               ├───────────────────────────────────>│
 │            │               │                 │                 │
 │            │               │                 │    (Vector      │
 │            │               │                 │     search in   │
 │            │               │                 │     LanceDB)    │
 │            │               │                 │                 │
 │            │               │ {results: [...]}                  │
 │            │               │<───────────────────────────────────┤
 │            │               │                 │                 │
 │            │               │ HTTPS POST      │                 │
 │            │               │ /v1/messages    │                 │
 │            │               │ (continue convo │                 │
 │            │               │  with tool      │                 │
 │            │               │  results)       │                 │
 │            │               ├────────────────>│                 │
 │            │               │                 │                 │
 │            │               │                 │ (Inference      │
 │            │               │                 │  with search    │
 │            │               │                 │  results)       │
 │            │               │                 │                 │
 │            │               │ HTTPS 200       │                 │
 │            │               │ {text: "Based   │                 │
 │            │               │  on project     │                 │
 │            │               │  standards..."}│                 │
 │            │               │<────────────────┤                 │
 │            │               │                 │                 │
 │            │ JSON-RPC      │                 │                 │
 │            │ response      │                 │                 │
 │            │<──────────────┤                 │                 │
 │            │               │                 │                 │
 │  Display   │               │                 │                 │
 │  review    │               │                 │                 │
 │<───────────┤               │                 │                 │
 │            │               │                 │                 │
```

---

## 🧠 ENDPOINT AWARENESS

### Question: How does the LLM know what tools are available?

**Answer:** The MCP server sends tool definitions in EVERY API request.

**Code Example:**

```python
# MCP Server sends this to LLM API
tools = [
    {
        "name": "search_standards",
        "description": "Semantic search over project-specific standards",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "n_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    }
]

response = llm_client.messages.create(
    model="claude-sonnet-4",
    tools=tools,  # ← Sent with EVERY request
    messages=[...]
)
```

**Key Points:**
1. **LLM has NO built-in knowledge of tools** - it's stateless
2. **Every API call includes tool definitions** - like passing function signatures
3. **LLM decides whether to use tools** based on the task and available tools
4. **Tool execution happens server-side** (in MCP server), not in LLM

---

## 🔐 SECURITY MODEL

### What the LLM Can Access

**Direct access:** NOTHING
- LLM runs remotely on Anthropic's servers
- No access to user's filesystem
- No access to user's network
- No ability to execute code

**Indirect access via tool calls:**
- Can REQUEST that MCP server search standards
- Can REQUEST that MCP server list files
- Cannot directly read files
- Cannot execute arbitrary code

**MCP Server acts as security boundary:**
```python
async def execute_persona_tool(tool_name, tool_input, ...):
    # MCP server validates tool calls before executing
    
    if tool_name == "search_standards":
        # Safe: read-only semantic search
        return rag_engine.search(tool_input["query"])
    
    elif tool_name == "read_standard":
        # Safe: read-only, restricted to .agent-os/standards/
        file_path = tool_input["file_path"]
        if ".." in file_path or file_path.startswith("/"):
            return json.dumps({"error": "Invalid path"})
        return read_file(base_path / "standards" / file_path)
    
    elif tool_name == "create_project_standard":
        # BLOCKED for personas (requires Human approval)
        return json.dumps({"error": "Unauthorized: requires Human approval"})
    
    else:
        return json.dumps({"error": "Unknown tool"})
```

---

## 🚀 PERFORMANCE IMPLICATIONS

### Latency Breakdown

**Simple query (no tool use):**
```
User types "@architect review" → Cursor (local, instant)
    ↓ 0-1ms (stdio pipe)
Cursor → MCP Server (local, instant)
    ↓ 100-500ms (HTTPS round-trip)
MCP Server → Anthropic API → inference → response
    ↓ 0-1ms (stdio pipe)
MCP Server → Cursor (local, instant)
    ↓ instant (UI render)
Cursor displays result

Total: ~100-500ms (dominated by LLM API call)
```

**With 1 tool call:**
```
User types "@architect review" → Cursor (local)
    ↓ MCP Server invokes LLM API
LLM API returns tool_use request (~200ms)
    ↓ MCP Server executes search_standards (local, ~50ms)
MCP Server calls LLM API again with tool results
    ↓ LLM API returns final text (~300ms)
MCP Server → Cursor → User

Total: ~550ms (2 LLM API calls + 1 local search)
```

### Token Cost Breakdown

**Per API call:**
- System prompt: ~1,500 tokens (persona identity)
- Tool definitions: ~150 tokens per tool × 3 tools = ~450 tokens
- User message: ~100-500 tokens
- **Total input:** ~2,000-2,500 tokens per turn

**With 1 tool call:**
- Turn 1: ~2,000 tokens input, ~100 tokens output (tool use)
- Turn 2: ~2,500 tokens input (includes tool results), ~500 tokens output (final text)
- **Total:** ~4,500 input tokens, ~600 output tokens

**Cost estimate (Claude Sonnet 4):**
- Input: $3/M tokens → ~$0.014 per tool-using query
- Output: $15/M tokens → ~$0.009 per tool-using query
- **Total:** ~$0.023 per persona invocation with 1 tool call

---

## 📊 RESOURCE USAGE

### Local Resources (MCP Server)

**Memory:**
- Python process: ~100-200 MB base
- LanceDB index in memory: ~50-500 MB (depends on standards count)
- Total: ~150-700 MB

**Disk:**
- Vector index: ~10-100 MB (.agent-os/.cache/vector_index/)
- Python environment: ~500 MB (.agent-os/venv/)
- Total: ~510-600 MB

**CPU:**
- Idle: ~0%
- During RAG search: ~20-50% for 50-100ms
- During index rebuild: ~50-80% for 5-30 seconds

**Network:**
- MCP communication: 0 bytes (stdio)
- LLM API calls: ~10-50 KB per request
- Minimal bandwidth usage

### Remote Resources (Anthropic API)

**Handled by Anthropic:**
- GPU inference
- Model weights (~200 GB)
- Request queuing
- Load balancing

**User only pays per token** - no infrastructure management

---

## 🔧 DEBUGGING & OBSERVABILITY

### Logging Points

**1. MCP Server logs:** `.agent-os/.cache/mcp_server.log`
```
2025-10-06 10:15:23 - INFO - Tool invoked: invoke_architect
2025-10-06 10:15:23 - INFO - Calling LLM API with system prompt (1,523 tokens)
2025-10-06 10:15:24 - INFO - LLM requested tool: search_standards(query="API patterns")
2025-10-06 10:15:24 - INFO - Executing tool search_standards locally
2025-10-06 10:15:24 - INFO - search_standards returned 5 results (1,234 tokens)
2025-10-06 10:15:24 - INFO - Calling LLM API with tool results
2025-10-06 10:15:25 - INFO - LLM returned final response (487 tokens)
2025-10-06 10:15:25 - INFO - invoke_architect completed in 1.8s
```

**2. Cursor logs:** Available via Cursor's Developer Tools

**3. Network traffic:** Can monitor with tools like `mitmproxy` to see API calls

---

## 📝 SUMMARY

### Infrastructure Model

**Local Machine:**
- Cursor IDE (Electron app, no network port)
- MCP Server (Python process, stdio only, no network port)
- LanceDB (embedded database, no network port)
- Communication: stdio pipes (not network sockets)

**Remote:**
- Anthropic API (HTTPS, api.anthropic.com)
- Communication: HTTPS (standard web API)

### Tool Awareness

**How it works:**
1. MCP Server sends tool definitions to LLM with every API call
2. LLM sees available tools and decides whether to use them
3. If LLM wants to use a tool, it returns `tool_use` in response
4. MCP Server executes tool locally (never sent to LLM)
5. MCP Server sends tool results back to LLM
6. LLM generates final response incorporating tool results

**Key insight:** Tools are like "function signatures" sent to the LLM. The LLM says "call this function with these arguments," and the MCP server actually executes it.

### Security Boundaries

- **LLM:** Stateless, no direct access to anything, can only REQUEST tool execution
- **MCP Server:** Validates and executes tools, acts as security boundary
- **Cursor:** Manages MCP server lifecycle, no direct access to tools

---

**Does this answer your infrastructure questions?** Let me know if you want to drill deeper into any specific part!
