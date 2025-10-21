# Cline Integration Guide for Agent OS Enhanced

**Successfully connecting Cline to Agent OS Enhanced MCP server**

Last Updated: October 20, 2025

---

## 🎉 Quick Start

**TL;DR:** Cline can connect to Agent OS Enhanced via HTTP using the streamable-http transport. The key is explicitly specifying `"type": "streamableHttp"` in the configuration.

**Setup Time:** ~2 minutes  
**Difficulty:** Easy

---

## 📋 Prerequisites

1. Agent OS Enhanced installed in your project (`.agent-os/` directory exists)
2. MCP server running (Cursor's agent should already be using it)
3. Cline extension installed in VSCode or Cursor

---

## 🚀 Setup Methods

### Method 1: Automated Setup (Recommended)

Run the configuration script:

```bash
python .agent-os/bin/update-cline-mcp.py
```

The script will:
1. Find the current MCP server port from `.agent-os/.mcp_server_state.json`
2. Locate Cline's config file automatically
3. Create the correct configuration with proper transport type
4. Preserve any other MCP servers you have configured

**After running:**
1. Reload your VSCode/Cursor window (Cmd/Ctrl+Shift+P → "Reload Window")
2. Verify connection in Cline → MCP Servers → Configure tab
3. You should see "agent-os-rag" with a green dot (connected)

---

### Method 2: Manual Setup

1. **Find Current Port:**
   ```bash
   cat .agent-os/.mcp_server_state.json
   ```
   Look for the `"port"` value (e.g., 4244)

2. **Edit Cline Config:**
   - In Cline, click MCP Servers icon
   - Go to "Configure" tab
   - Click "Configure MCP Servers" at bottom
   - Add this configuration:

   ```json
   {
     "mcpServers": {
       "agent-os-rag": {
         "type": "streamableHttp",
         "url": "http://127.0.0.1:4244/mcp",
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

3. **Save and Reload:**
   - Save the config file
   - Reload window (Cmd/Ctrl+Shift+P → "Reload Window")

---

## 🔍 The Critical Detail: Transport Type

### Why "type" Matters

**THE KEY INSIGHT:** Cline's schema validation checks transport types in this specific order:

1. **stdio** (needs `command` field)
2. **sse** (needs `url` field) ← **Matches first for URL-only configs!**
3. **streamableHttp** (needs `url` field)

When you provide only a `url` without specifying `type`, Zod's union schema matches the **first compatible schema**, which is SSE (the deprecated transport).

**This is why the connection failed initially** - Cline was trying to use SSE transport instead of streamableHttp!

### The Fix

**Always explicitly specify:**
```json
{
  "type": "streamableHttp",
  "url": "http://127.0.0.1:4244/mcp"
}
```

**Not just:**
```json
{
  "url": "http://127.0.0.1:4244/mcp"
}
```

---

## 🔧 Configuration Reference

### Complete Config Structure

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "type": "streamableHttp",           // REQUIRED: Must be explicit
      "url": "http://127.0.0.1:4244/mcp", // MCP server endpoint
      "alwaysAllow": [                    // Tools that don't need approval
        "search_standards",
        "get_current_phase", 
        "get_workflow_state",
        "get_server_info"
      ],
      "disabled": false,                  // Enable/disable server
      "timeout": 60                       // Request timeout in seconds
    }
  }
}
```

### Field Explanations

- **type**: Transport mechanism. Must be `"streamableHttp"` for Agent OS
- **url**: HTTP endpoint where MCP server is listening
- **alwaysAllow**: Tools that execute without user approval (use `alwaysAllow`, not `autoApprove`)
- **disabled**: Set to `true` to keep config but disable connection
- **timeout**: Maximum time to wait for responses (default: 60 seconds)

---

## 🧪 Testing the Connection

### 1. Visual Check

In Cline:
1. Click MCP Servers icon
2. Go to "Configure" tab
3. Look for "agent-os-rag"
4. Status should show: **Green dot** = Connected

### 2. Functional Test

Try this in Cline chat:

```
Search standards for "orientation"
```

You should see Cline use the `search_standards` tool and return Agent OS documentation.

### 3. Verify All Tools Available

In the Cline MCP UI, expand "agent-os-rag" server. You should see all available tools:
- search_standards
- get_current_phase
- get_workflow_state
- get_server_info
- start_workflow
- complete_phase
- get_task
- create_workflow
- validate_workflow
- current_date
- aos_browser

---

## 🐛 Troubleshooting

### Issue: "Not Connected" Error

**Symptoms:**
- Red dot next to "agent-os-rag"
- Error: "Not connected"

**Solutions:**
1. **Check MCP server is running:**
   ```bash
   ps aux | grep mcp_server
   ```
   Should show a Python process running

2. **Verify port in state file:**
   ```bash
   cat .agent-os/.mcp_server_state.json | jq .port
   ```

3. **Check if port matches config:**
   Compare port from state file to URL in Cline config

4. **Try restarting the MCP server:**
   - Kill the current server process
   - Cursor's agent will automatically restart it

---

### Issue: "SSE Error: Non-200 status code (400)"

**Symptom:**
- Connection shows error about SSE
- HTTP 400 or 406 errors

**Cause:** Config is missing `"type": "streamableHttp"` field

**Solution:**
1. Open Cline config (MCP Servers → Configure → Configure MCP Servers)
2. Add `"type": "streamableHttp"` to the agent-os-rag server config
3. Save and reload window

---

### Issue: Port Number Changed

**Symptom:**
- Was working, now not connected
- Port in state file different from config

**Cause:** Agent OS uses dynamic port allocation (4242-5252 range)

**Solution:**
1. Run the update script again:
   ```bash
   python .agent-os/bin/update-cline-mcp.py
   ```
2. Or manually update the port in Cline config

**Prevention:** The update script is designed for this - run it whenever the port changes.

---

### Issue: Can't Find Cline Config File

**Symptom:**
- Script can't locate `cline_mcp_settings.json`

**Solution:**
1. Find it manually:
   - **macOS/Linux:** `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/`
   - **Windows:** `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\`

2. Pass path to script (future enhancement):
   ```bash
   python update-cline-mcp.py --config-path /path/to/cline_mcp_settings.json
   ```

---

## 🏗️ Architecture

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent OS Enhanced Project                     │
│                                                                   │
│  Cursor's Agent                         Cline                    │
│       │                                   │                       │
│       │ stdio                             │ HTTP (streamableHttp) │
│       ↓                                   ↓                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         Agent OS MCP Server (dual transport)            │    │
│  │  - stdio for Cursor's agent                             │    │
│  │  - HTTP on port 4244 for Cline (and other clients)     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                       │
│                           ↓                                       │
│              ┌─────────────────────────┐                         │
│              │  .agent-os/             │                         │
│              │  ├── standards/         │                         │
│              │  ├── workflows/         │                         │
│              │  ├── usage/             │                         │
│              │  └── .cache/            │                         │
│              └─────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

**Key Points:**
1. **One MCP server, two transports:** The server runs in "dual" mode
2. **Cursor's agent:** Uses stdio (its own process)
3. **Cline:** Connects via HTTP to the same server
4. **Sequential work:** Not simultaneous - each agent works, then the other reviews
5. **File-based communication:** Agents communicate through code files, not shared state

---

## 📝 Agent OS Workflow with Cline

### Typical Usage Pattern

1. **Cursor's agent implements feature:**
   - Queries standards
   - Writes code
   - Creates tests
   - Commits when done

2. **User switches to Cline for review:**
   - Cline queries same standards
   - Reviews Cursor's work
   - Finds edge cases or issues
   - Suggests improvements

3. **Back to Cursor or continue with Cline:**
   - Address feedback
   - Iterate until complete

### Why This Works

- **Same knowledge base:** Both query the same RAG index
- **Independent:** No coordination needed (sequential work)
- **Complementary:** Each agent has different strengths
- **File-based:** Output files are the communication medium

---

## 🎓 Best Practices

### 1. Run Orientation

First thing in any Cline session:

```
search standards for "orientation bootstrap queries mandatory eight queries"
```

Then run the 8 bootstrap queries listed in the results. This loads the behavioral patterns and query mechanics.

### 2. Query Liberally

Agent OS is query-driven. Target: 5-10 queries per task.

Examples:
```
search standards for "production code checklist"
search standards for "error handling patterns"
search standards for "testing best practices"
```

### 3. Use Sequential Validation

Let one agent finish before the other starts. Review via files:

```
Read the file cursor's agent just created and analyze it for:
- Completeness
- Edge cases
- Test coverage
- Production readiness
```

### 4. Keep Tools Auto-Approved

The `alwaysAllow` configuration lets Cline query standards without approval each time. This is safe and recommended for:
- search_standards
- get_current_phase
- get_workflow_state  
- get_server_info

---

## 🔄 Updating Configuration

### When Port Changes

If the MCP server restarts on a different port:

```bash
python .agent-os/bin/update-cline-mcp.py
```

Then reload window in VSCode/Cursor.

### Adding More Tools to Auto-Approve

Edit Cline config and add tool names to `alwaysAllow` array:

```json
{
  "alwaysAllow": [
    "search_standards",
    "get_current_phase",
    "get_workflow_state",
    "get_server_info",
    "validate_workflow",    // Add new tools here
    "current_date"
  ]
}
```

---

## 📁 Cline Rules (.clinerules/)

Agent OS Enhanced includes a `.clinerules/` folder with project-specific rules for Cline:

**File:** `.clinerules/agent-os-orientation.md`

This file ensures:
- Mandatory orientation on session start (8 bootstrap queries)
- Query-driven development reminders
- File operation guidelines (query vs read)
- Git safety rules

Cline automatically loads all markdown files from `.clinerules/` folder. The orientation rules ensure every Cline session starts with the proper Agent OS behavioral patterns.

**The orientation will prompt you to:**
1. Run the orientation bootstrap query
2. Execute all 8 bootstrap queries in sequence
3. Reply "✅ Oriented. Ready." when complete

---

## 📚 Related Documentation

- **Agent OS Standards:** `.agent-os/standards/` - Query-driven documentation
- **Orientation Guide:** Query `"orientation bootstrap queries"`
- **Query Patterns:** Query `"query construction patterns"`
- **Production Checklist:** Query `"production code checklist"`
- **Cline Rules:** `.clinerules/agent-os-orientation.md` - Auto-loaded on every session

---

## 🙏 Credits

**Discovery Process:**
- Issue identified: October 20, 2025
- Root cause found by analyzing Cline source code
- Schema union order was the key insight
- Solution: Explicit `"type": "streamableHttp"` in config

**Key Files Analyzed:**
- `/tmp/cline/src/services/mcp/McpHub.ts` - Connection handling
- `/tmp/cline/src/services/mcp/schemas.ts` - Schema validation order

---

## ✅ Success Checklist

- [ ] `.agent-os/` directory exists in project
- [ ] MCP server running (check with `ps aux | grep mcp_server`)
- [ ] Ran `update-cline-mcp.py` script
- [ ] Reloaded VSCode/Cursor window
- [ ] Cline shows "agent-os-rag" with green dot
- [ ] Can successfully run `search_standards` query
- [ ] Completed orientation (8 bootstrap queries)

**You're ready to use Cline with Agent OS Enhanced!** 🎉
