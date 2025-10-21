# GitHub Issue Update: Working StreamableHTTP Configuration

**For:** https://github.com/cline/cline/issues/6767

---

## ✅ Confirmed: StreamableHTTP Works with Explicit Type

I can confirm that Cline **does** support StreamableHTTP remote servers successfully. The maintainer (@tbarron-xyz) was correct - it works!

However, I discovered **why it was failing initially**: the configuration requires an **explicit `"type": "streamableHttp"` field**.

---

## 🔍 Root Cause Discovery

### The Problem

When connecting to a remote MCP server with only a `url` field (no explicit `type`), Cline's schema validation defaults to **SSE transport** instead of StreamableHTTP.

This is because of the **schema union check order** in `src/services/mcp/schemas.ts`:

```typescript
z.union([
    // 1. Stdio config (has command field)
    BaseConfigSchema.extend({ type: z.literal("stdio"), command: z.string(), ... }),
    
    // 2. SSE config (has url field) ← MATCHES FIRST!
    BaseConfigSchema.extend({ type: z.literal("sse"), url: z.string().url(), ... }),
    
    // 3. Streamable HTTP config (has url field) ← NEVER REACHED
    BaseConfigSchema.extend({ type: z.literal("streamableHttp"), url: z.string().url(), ... }),
])
```

When Zod checks the union, it matches the **first compatible schema**. Since both SSE and StreamableHTTP need a `url` field, **SSE matches first** when no `type` is specified.

### The Result

**Without explicit type:**
```json
{
  "mcpServers": {
    "my-server": {
      "url": "http://localhost:4244/mcp"
    }
  }
}
```
→ Cline uses **SSE transport** (deprecated) → Connection fails with "SSE error: Non-200 status code"

---

## ✅ Working Configuration

### The Fix

**Explicitly specify `"type": "streamableHttp"`:**

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "type": "streamableHttp",
      "url": "http://localhost:4244/mcp",
      "alwaysAllow": [
        "search_standards",
        "get_current_phase",
        "get_workflow_state",
        "get_server_info"
      ],
      "disabled": false,
      "timeout": 60
    }
  }
}
```

### Test Results

✅ **Connection successful**  
✅ **All MCP tools available**  
✅ **Queries work perfectly**  
✅ **No SSE errors**

Connected to a FastMCP server running in `streamable-http` transport mode (Agent OS Enhanced MCP server).

---

## 💡 Recommendation for Cline

### User Experience Improvement

Consider one of these approaches to make StreamableHTTP the default for URL-only configs:

**Option 1: Reorder schema union (as proposed in this issue)**
```typescript
z.union([
    StdioSchema,           // 1st: command-based
    StreamableHttpSchema,  // 2nd: modern (check BEFORE sse)
    SSESchema,            // 3rd: deprecated (check LAST)
])
```

**Option 2: Add warning when SSE is auto-selected**
```typescript
if (!config.type && config.url) {
    console.warn("No transport type specified for URL-based server. " +
                 "Defaulting to SSE (deprecated). Consider explicitly setting " +
                 "'type': 'streamableHttp' for modern MCP servers.");
}
```

**Option 3: Explicit type requirement**
Require `type` field for all URL-based servers (breaking change).

---

## 📝 Documentation Note

The current behavior isn't documented clearly. Users connecting to modern StreamableHTTP servers may not realize they need the explicit `type` field, leading to confusing SSE errors.

**Suggestion:** Update remote server documentation to emphasize:
- Always include `"type": "streamableHttp"` for modern MCP servers
- Omitting `type` will default to SSE (deprecated)

---

## 🙏 Thanks

Thanks to @tbarron-xyz for confirming StreamableHTTP works - this confirmation led me to investigate the configuration side rather than assuming a code issue. The problem was indeed in my configuration (missing explicit type), not in Cline's implementation!

---

## 🔗 Additional Context

**Test Environment:**
- Cline version: Latest (Oct 2025)
- MCP Server: FastMCP (Python) running `streamable-http` transport
- Project: Agent OS Enhanced (https://github.com/honeyhiveai/agent-os-enhanced)

**Working Setup:**
- Remote MCP server on `http://localhost:4244/mcp`
- FastMCP with `transport="streamable-http"`
- Cline config with explicit `"type": "streamableHttp"`
- Connection successful, all tools accessible
