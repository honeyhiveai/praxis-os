# Persona LLM Communication Architecture

**How sub-agents (personas) make their own LLM API calls, separate from the main Cursor agent.**

---

## 🎯 THE KEY DISTINCTION

### Two Separate LLM Connections

```
┌─────────────────────────────────────────────────────────────────┐
│  CONNECTION 1: Main Cursor Agent                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Cursor IDE → Cursor's built-in LLM client → Anthropic API      │
│                                                                   │
│  - Managed by Cursor                                             │
│  - Uses Cursor's API key or user's configured key                │
│  - User chats directly with this agent                           │
│  - This agent can call MCP tools                                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  CONNECTION 2: Persona Sub-Agents                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  MCP Server → Its own LLM client → Anthropic API                │
│                                                                   │
│  - Managed by MCP server (NOT Cursor)                            │
│  - Uses API key configured in MCP server                         │
│  - Invoked when main agent calls tools like invoke_architect    │
│  - Makes independent API calls with persona prompts              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 COMPLETE FLOW: USER → PERSONA → LLM

### Scenario: User asks "@architect review this"

```
┌──────────────────────────────────────────────────────────────────┐
│  Step 1: User types in Cursor                                     │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│  Step 2: Cursor's LLM interprets "@architect" as tool call       │
│                                                                    │
│  Cursor Agent (LLM #1):                                           │
│  "User wants architect review. I should call invoke_architect()  │
│   MCP tool."                                                      │
└────────────────────────┬─────────────────────────────────────────┘
                         │ MCP tool call via stdio
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│  Step 3: MCP Server receives tool call                           │
│                                                                    │
│  MCP Server:                                                      │
│  "Received: invoke_architect(task='review this API', context=...)"│
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│  Step 4: MCP Server makes its OWN LLM API call                   │
│                                                                    │
│  MCP Server code:                                                 │
│  ```python                                                        │
│  # Load architect persona prompt                                 │
│  system_prompt = load_persona_prompt("architect")                │
│                                                                    │
│  # Make NEW API call (separate from Cursor's)                    │
│  llm_client = anthropic.Anthropic(                               │
│      api_key=os.getenv("ANTHROPIC_API_KEY")  # MCP server's key │
│  )                                                                │
│                                                                    │
│  response = llm_client.messages.create(                          │
│      model="claude-sonnet-4-20250514",                           │
│      system=system_prompt,  # Architect identity                 │
│      messages=[{"role": "user", "content": task}],               │
│      tools=[...],  # search_standards, etc.                      │
│      max_tokens=4096                                              │
│  )                                                                │
│  ```                                                              │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTPS to Anthropic
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│  Step 5: Anthropic API processes persona request (LLM #2)        │
│                                                                    │
│  Anthropic receives:                                              │
│  - System: "You are a Senior Software Architect..."              │
│  - User: "Review this API design..."                             │
│  - Tools: [search_standards, list_standards, read_standard]      │
│                                                                    │
│  LLM #2 (Architect persona):                                     │
│  "I should check existing API standards first"                   │
│  → Returns: tool_use(search_standards, query="API conventions")  │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTPS response
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│  Step 6: MCP Server executes tool (server-side)                  │
│                                                                    │
│  MCP Server:                                                      │
│  "LLM wants search_standards. Execute locally."                  │
│  → result = rag_engine.search("API conventions")                 │
│  → result = [{file: "architecture/api-conventions.md", ...}]     │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│  Step 7: MCP Server sends tool results back to LLM              │
│                                                                    │
│  MCP Server:                                                      │
│  ```python                                                        │
│  response = llm_client.messages.create(                          │
│      model="claude-sonnet-4",                                    │
│      system=system_prompt,                                        │
│      messages=[                                                   │
│          {"role": "user", "content": task},                      │
│          {"role": "assistant", "content": [tool_use]},           │
│          {"role": "user", "content": [tool_result]}              │
│      ],                                                           │
│      tools=[...],                                                 │
│      max_tokens=4096                                              │
│  )                                                                │
│  ```                                                              │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTPS to Anthropic
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│  Step 8: Anthropic API generates final review (LLM #2)           │
│                                                                    │
│  LLM #2 (Architect persona):                                     │
│  "Based on the project's API conventions standard, here's my     │
│   review: [detailed architecture review]"                        │
│  → Returns: text response (no more tool calls)                   │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTPS response
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│  Step 9: MCP Server returns result to Cursor                     │
│                                                                    │
│  MCP Server → Cursor (via stdio):                                │
│  {                                                                │
│    "result": {                                                    │
│      "content": [{                                                │
│        "type": "text",                                            │
│        "text": "🎯 Architecture Review:\n\n[review content]"     │
│      }]                                                           │
│    }                                                              │
│  }                                                                │
└────────────────────────┬─────────────────────────────────────────┘
                         │ stdio
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│  Step 10: Cursor displays result to user                         │
│                                                                    │
│  Cursor IDE:                                                      │
│  [Shows architect's review in chat]                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔑 API KEY CONFIGURATION

### Where API Keys Come From

**Main Cursor Agent:**
- Configured in Cursor IDE settings
- User provides their Anthropic API key
- OR user uses Cursor's built-in proxy/credits

**Persona Sub-Agents (MCP Server):**
- Configured in `.agent-os/config.json` or environment variables
- MCP server needs its own API key
- Separate from Cursor's key

### Configuration File: `.agent-os/config.json`

```json
{
  "llm": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-20250514",
    "api_key_env": "ANTHROPIC_API_KEY",
    "max_tokens": 4096,
    "temperature": 0.7
  },
  "project": {
    "python_executable": "/Users/josh/project/venv/bin/python",
    "test_command": "tox"
  }
}
```

### Environment Variables: `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.agent-os/venv/bin/python",
      "args": ["-m", "mcp_server.agent_os_rag"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.agent-os",
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"  // ← API key for personas
      }
    }
  }
}
```

### Alternative: Shared Key

If user wants to use the same API key for both:

```bash
# In user's shell environment
export ANTHROPIC_API_KEY="sk-ant-..."

# Cursor inherits this
# MCP server inherits this via env in mcp.json
```

---

## 💻 MCP SERVER IMPLEMENTATION

### File: `mcp_server/llm_client.py`

```python
"""LLM client initialization for persona sub-agents."""

import os
import json
from pathlib import Path
from typing import Optional
import anthropic

def get_llm_config(base_path: Path) -> dict:
    """
    Load LLM configuration for personas.
    
    Priority:
    1. Environment variables (ANTHROPIC_API_KEY)
    2. .agent-os/config.json (llm section)
    3. Defaults
    """
    config_file = base_path / "config.json"
    
    # Default config
    config = {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4096,
        "temperature": 0.7
    }
    
    # Load from config file if exists
    if config_file.exists():
        with open(config_file) as f:
            file_config = json.load(f)
            config.update(file_config.get("llm", {}))
    
    # Get API key from environment
    api_key_env = config.get("api_key_env", "ANTHROPIC_API_KEY")
    config["api_key"] = os.getenv(api_key_env)
    
    if not config["api_key"]:
        raise ValueError(
            f"No API key found. Set {api_key_env} environment variable "
            "or configure in .agent-os/config.json"
        )
    
    return config


def create_llm_client(base_path: Path) -> anthropic.Anthropic:
    """
    Create LLM client for persona sub-agents.
    
    This client is separate from Cursor's built-in client.
    """
    config = get_llm_config(base_path)
    
    if config["provider"] == "anthropic":
        return anthropic.Anthropic(api_key=config["api_key"])
    else:
        raise ValueError(f"Unsupported provider: {config['provider']}")
```

### File: `mcp_server/agent_os_rag.py`

```python
from mcp_server.llm_client import create_llm_client

def create_server(base_path: Optional[Path] = None) -> FastMCP:
    """Create MCP server with persona support."""
    
    if base_path is None:
        base_path = Path(__file__).parent.parent
    
    # Initialize LLM client for personas
    llm_client = create_llm_client(base_path)
    
    # Initialize other components
    rag_engine = RAGEngine(...)
    workflow_engine = WorkflowEngine(...)
    
    # Create FastMCP server
    mcp = FastMCP("Agent OS RAG")
    
    # Register persona tools with access to llm_client
    @mcp.tool()
    async def invoke_architect(task: str, context: Optional[str] = None) -> str:
        """Invoke Software Architect persona."""
        return await _invoke_persona_with_tools(
            persona_identifier="architect",
            task=task,
            context=context,
            llm_client=llm_client,  # ← Persona's LLM client
            rag_engine=rag_engine,
            base_path=base_path
        )
    
    return mcp
```

---

## 📊 TOKEN ACCOUNTING

### Whose Quota Is Used?

**Main Cursor Agent:**
- Uses Cursor's quota OR user's Anthropic account
- User sees these tokens in Cursor's usage dashboard

**Persona Sub-Agents:**
- Uses the API key configured for MCP server
- If same key as Cursor: All tokens go to same account
- If different key: Separate accounting

### Example: Single API Key Setup

```
User's Anthropic Account (sk-ant-123...)
├─ Cursor Agent usage:     10,000 tokens/day
└─ Persona usage:           5,000 tokens/day
   ├─ @architect:           2,000 tokens
   ├─ @security:            1,500 tokens
   └─ @sre:                 1,500 tokens

Total daily usage: 15,000 tokens
Monthly cost: ~$45 (at $3/M input, $15/M output)
```

### Observability: Tracking Persona Usage

**Option 1: MCP Server Logs**
```python
# Log every persona invocation
logger.info(
    f"Persona invoked: {persona_identifier}, "
    f"input_tokens: {response.usage.input_tokens}, "
    f"output_tokens: {response.usage.output_tokens}"
)
```

**Option 2: Metrics Dashboard**
```python
# Track in metrics
metrics.record_persona_usage(
    persona=persona_identifier,
    input_tokens=response.usage.input_tokens,
    output_tokens=response.usage.output_tokens,
    latency_ms=latency
)
```

**Option 3: HoneyHive/OpenTelemetry**
```python
# Send to observability platform
tracer.log_event(
    event_type="persona_invocation",
    persona=persona_identifier,
    tokens=response.usage,
    cost=calculate_cost(response.usage)
)
```

---

## 🔐 SECURITY CONSIDERATIONS

### API Key Isolation

**Best Practice: Separate Keys**
```
Main Cursor Agent: Uses user's personal Anthropic key
Persona Sub-Agents: Uses team/project Anthropic key
```

**Why?**
- **Cost control:** Separate billing for persona usage
- **Rate limiting:** Personas don't exhaust user's personal quota
- **Auditability:** Track project vs personal usage
- **Team sharing:** Multiple devs share persona key, but use personal keys for main agent

### Key Rotation

```python
# Easy rotation via environment variable
# No code changes needed

# Old key
export ANTHROPIC_API_KEY="sk-ant-old..."

# Rotate to new key
export ANTHROPIC_API_KEY="sk-ant-new..."

# Restart MCP server
# (Cursor automatically restarts when mcp.json changes)
```

---

## 🎭 COMPARISON: MAIN AGENT vs PERSONAS

| Aspect | Main Cursor Agent | Persona Sub-Agents |
|--------|-------------------|-------------------|
| **Process** | Runs in Cursor IDE | Runs in MCP Server (Python) |
| **LLM Client** | Cursor's built-in | MCP server's own (anthropic SDK) |
| **API Key** | Configured in Cursor | Configured in mcp.json env vars |
| **System Prompt** | Cursor's default + .cursorrules | Persona-specific (architect.md, etc.) |
| **Tools Available** | All MCP tools + Cursor's built-in | Limited subset (search, list, read) |
| **Invocation** | User chats directly | Via MCP tool call (invoke_architect) |
| **Token Accounting** | User's Cursor usage | MCP server's API key usage |
| **Conversation State** | Maintained by Cursor | Ephemeral (per invocation) |

---

## 🚀 SCALING CONSIDERATIONS

### Concurrent Persona Invocations

**Scenario:** User invokes 3 personas simultaneously
```
User: "@architect @security @sre review this"
```

**What happens:**
```
Main Cursor Agent:
├─ Calls invoke_architect() → MCP Server → Anthropic API call #1
├─ Calls invoke_security() → MCP Server → Anthropic API call #2
└─ Calls invoke_sre()      → MCP Server → Anthropic API call #3

All 3 API calls happen in parallel (async)
Total time: ~max(call1, call2, call3) ≈ 500-1500ms
```

**Implications:**
- 3× token cost (3 separate LLM inferences)
- Same latency as single call (parallel execution)
- 3× API rate limit usage

### Rate Limiting

Anthropic API limits (as of 2025):
- Tier 1: 50 requests/min, 40,000 tokens/min
- Tier 2: 1,000 requests/min, 400,000 tokens/min

**MCP Server should implement:**
```python
# Rate limiter for persona calls
from asyncio import Semaphore

persona_rate_limiter = Semaphore(10)  # Max 10 concurrent

async def _invoke_persona_with_tools(...):
    async with persona_rate_limiter:
        # Make API call
        response = await llm_client.messages.create(...)
```

---

## 📝 SUMMARY

### Key Architectural Points

1. **Two Separate LLM Connections:**
   - Main Cursor agent: Cursor manages
   - Personas: MCP server manages (separate Python SDK client)

2. **Personas Make Real API Calls:**
   - Not proxied through Cursor
   - Direct HTTPS to Anthropic API
   - Use MCP server's configured API key

3. **Configuration:**
   - API key: Environment variable or .agent-os/config.json
   - Can be same key as Cursor or separate team key
   - Easy rotation via env vars

4. **Token Accounting:**
   - If same key: All usage under one account
   - If different key: Separate accounting
   - Track via MCP server logs or observability

5. **Security:**
   - API key never exposed to LLM
   - MCP server validates all tool calls
   - Personas have read-only access to standards

6. **Scalability:**
   - Concurrent persona calls possible (async)
   - Rate limiting at MCP server level
   - Observability for usage tracking

---

**The key insight:** Personas are **independent LLM agents** running in the MCP server, making their own API calls with their own system prompts. They're NOT just routing through the main Cursor agent.
