
[![](https://private-user-images.githubusercontent.com/7799382/400551777-140c8606-d3bf-41b9-9a1f-4dbf0d4c90cb.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzQwMDU1MTc3Ny0xNDBjODYwNi1kM2JmLTQxYjktOWExZi00ZGJmMGQ0YzkwY2IucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZTljZjI1OTEwMmYxMDU0ZGUzNzExMjFmNTE3YjE4NGYwYjY5NTE3MzA1Yzk5NmM5ZTYwMmFmMzc5Mzk3YzUzMiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.YKDVGYWLLar6Ksv915PPAlU_anUEIkrmhIfxGo0FnnU)](https://private-user-images.githubusercontent.com/7799382/400551777-140c8606-d3bf-41b9-9a1f-4dbf0d4c90cb.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzQwMDU1MTc3Ny0xNDBjODYwNi1kM2JmLTQxYjktOWExZi00ZGJmMGQ0YzkwY2IucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9ZTljZjI1OTEwMmYxMDU0ZGUzNzExMjFmNTE3YjE4NGYwYjY5NTE3MzA1Yzk5NmM5ZTYwMmFmMzc5Mzk3YzUzMiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.YKDVGYWLLar6Ksv915PPAlU_anUEIkrmhIfxGo0FnnU)

### Checkpoints: Compare and Restore

[](#checkpoints-compare-and-restore)

As Cline works through a task, the extension takes a snapshot of your workspace at each step. You can use the 'Compare' button to see a diff between the snapshot and your current workspace, and the 'Restore' button to roll back to that point.

For example, when working with a local web server, you can use 'Restore Workspace Only' to quickly test different versions of your app, then use 'Restore Task and Workspace' when you find the version you want to continue building from. This lets you safely explore different approaches without losing progress.

[![](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)](https://private-user-images.githubusercontent.com/7799382/374860276-ee14e6f7-20b8-4391-9091-8e8e25561929.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjAxNTcwNzQsIm5iZiI6MTc2MDE1Njc3NCwicGF0aCI6Ii83Nzk5MzgyLzM3NDg2MDI3Ni1lZTE0ZTZmNy0yMGI4LTQzOTEtOTA5MS04ZThlMjU1NjE5MjkucG5nP1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MTAxMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTEwMTFUMDQyNjE0WiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9MDAzZTlhMmY3MzljY2YxY2JjNTNmOTYyZTBjOTkyZjM5NzM0YmEyNzdkYjc5NWM4ZGE5ZDkzOGQxYjM1OWYxZSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.lNzHpFTKWYp_i-XW_EdXwRgVc_A56LS-P4wnJ1ij2us)  

Contributing
------------

[](#contributing)

To contribute to the project, start with our [Contributing Guide](/cline/cline/blob/main/CONTRIBUTING.md) to learn the basics. You can also join our [Discord](https://discord.gg/cline) to chat with other contributors in the `#contributors` channel. If you're looking for full-time work, check out our open positions on our [careers page](https://cline.bot/join-us)!

License
-------

[](#license)

[Apache 2.0 © 2025 Cline Bot Inc.](/cline/cline/blob/main/LICENSE)

About
-----

Autonomous coding agent right in your IDE, capable of creating/editing files, executing commands, using the browser, and more with your permission every step of the way.

[marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev "https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev")

### Resources

[Readme](#readme-ov-file)

### License

[Apache-2.0 license](#Apache-2.0-1-ov-file)

### Code of conduct

[Code of conduct](#coc-ov-file)

### Contributing

[Contributing](#contributing-ov-file)

### Uh oh!

There was an error while loading. Please reload this page.

[Activity](/cline/cline/activity)

[Custom properties](/cline/cline/custom-properties)

### Stars

[**51.2k** stars](/cline/cline/stargazers)

### Watchers

[**276** watching](/cline/cline/watchers)

### Forks

[**7.3k** forks](/cline/cline/forks)

[Report repository](/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fcline%2Fcline&report=cline+%28user%29)

[Releases 176](/cline/cline/releases)
-------------------------------------

[

Cline CLI v3.32.6-cli Latest

Oct 11, 2025



](/cline/cline/releases/tag/v3.32.6-cli)

[\+ 175 releases](/cline/cline/releases)

### Uh oh!

There was an error while loading. Please reload this page.

[Contributors 244](/cline/cline/graphs/contributors)
----------------------------------------------------

*   [![@saoudrizwan](https://avatars.githubusercontent.com/u/7799382?s=64&v=4)](https://github.com/saoudrizwan)
*   [![@celestial-vault](https://avatars.githubusercontent.com/u/58194240?s=64&v=4)](https://github.com/celestial-vault)
*   [![@sjf](https://avatars.githubusercontent.com/u/153992?s=64&v=4)](https://github.com/sjf)
*   [![@pashpashpash](https://avatars.githubusercontent.com/u/20898225?s=64&v=4)](https://github.com/pashpashpash)
*   [![@canvrno](https://avatars.githubusercontent.com/u/46584286?s=64&v=4)](https://github.com/canvrno)
*   [![@github-actions[bot]](https://avatars.githubusercontent.com/in/15368?s=64&v=4)](https://github.com/apps/github-actions)
*   [![@0xToshii](https://avatars.githubusercontent.com/u/94262432?s=64&v=4)](https://github.com/0xToshii)
*   [![@arafatkatze](https://avatars.githubusercontent.com/u/11155207?s=64&v=4)](https://github.com/arafatkatze)
*   [![@abeatrix](https://avatars.githubusercontent.com/u/68532117?s=64&v=4)](https://github.com/abeatrix)
*   [![@dcbartlett](https://avatars.githubusercontent.com/u/1077050?s=64&v=4)](https://github.com/dcbartlett)
*   [![@ellipsis-dev[bot]](https://avatars.githubusercontent.com/in/64358?s=64&v=4)](https://github.com/apps/ellipsis-dev)
*   [![@ocasta181](https://avatars.githubusercontent.com/u/2112873?s=64&v=4)](https://github.com/ocasta181)
*   [![@brownrw8](https://avatars.githubusercontent.com/u/6895070?s=64&v=4)](https://github.com/brownrw8)

[\+ 230 contributors](/cline/cline/graphs/contributors)

Languages
---------

*   [TypeScript 85.6%](/cline/cline/search?l=typescript)
*   [Go 8.2%](/cline/cline/search?l=go)
*   [JavaScript 4.3%](/cline/cline/search?l=javascript)
*   [Python 1.1%](/cline/cline/search?l=python)
*   [Shell 0.6%](/cline/cline/search?l=shell)
*   [CSS 0.2%](/cline/cline/search?l=css)

You can’t perform that action at this time.
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Current Time
10/10/2025, 9:26:16 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
47,851 / 200K tokens used (24%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
# Integrating prAxIs OS MCP Server into Cline

## 🎯 Overview

Cline (like Cursor) supports MCP (Model Context Protocol) servers and has a similar configuration approach. Here's how to integrate the local prAxIs OS MCP server with Cline:

## 📝 Part 1: MCP Server Configuration

### Cline's MCP Configuration Location

Cline uses **VS Code's settings system** for MCP configuration. You have two options:

**Option 1: User Settings (Global)**
```
~/.vscode/settings.json
```

**Option 2: Workspace Settings (Project-specific)**
```
.vscode/settings.json
```

### MCP Configuration Format for Cline

Based on Cline's architecture, add this to your VS Code settings.json:

```json
{
  "cline.mcpServers": {
    "praxis-os": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**For Windows:**
```json
{
  "cline.mcpServers": {
    "praxis-os": {
      "command": "${workspaceFolder}/.praxis-os/venv/Scripts/python.exe",
      "args": ["-m", "mcp_server"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## 🔧 Part 2: Cline Rules File (Bootstrap Configuration)

### Create `.clinerules` File

Cline uses **`.clinerules`** (equivalent to Cursor's `.cursorrules`) for behavioral instructions.

**Create this file in your project root:**

```markdown
# prAxIs OS - Cline Configuration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛑🛑🛑 STOP 🛑🛑🛑
MANDATORY:
Before you respond, you MUST answer this question:
"Have I run search_standards('Agent OS orientation guide') this conversation?"

If NO: Run it now via MCP tool, then reply "✅ Oriented. Ready."
If YES: Proceed with user's request.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## MCP Tool Usage Priority

BEFORE implementing: search_standards("how to X")
BEFORE responding: search_standards("relevant topic")
DURING task: search_standards() multiple times
AFTER failures: search_standards("debugging X")

Target: 5-10 queries per task

## File Access Rules

❌ NEVER: read_file(".praxis-os/standards/...")
❌ NEVER: read_file(".praxis-os/workflows/...")
❌ NEVER: read_file(".praxis-os/usage/...")
✅ ALWAYS: Use search_standards() MCP tool for indexed content

✅ DO: read_file(".praxis-os/specs/...") - your specs, not indexed
❌ NEVER: commit without "commit it" instruction

## Available MCP Tools

This project has prAxIs OS MCP server configured with these tools:

- **search_standards(query, n_results, filters)**: Semantic search over standards
- **start_workflow(workflow_type, target_file, metadata)**: Initialize phase-gated workflows
- **get_current_phase(session_id)**: Get current workflow phase
- **complete_phase(session_id, phase, evidence)**: Submit evidence and advance
- **get_workflow_state(session_id)**: Query workflow state
- **get_task(session_id, phase, task_number)**: Get specific task details

## Workflow Commands

When user says:
- "Create spec for [feature]" → Use search_standards first, then create spec
- "Execute tasks from [spec]" → Load spec, execute tasks sequentially
- "Start workflow" → Use start_workflow MCP tool

## Code Quality Standards

Query standards liberally = better code

Search for:
- "production code checklist" - Before implementing features
- "concurrency safety" - When dealing with shared state
- "error handling patterns" - When writing error handling
- "test coverage requirements" - Before writing tests
- "Sphinx docstring format" - When documenting code

## Remember

Query liberally = better code
Each MCP query is cheap, mistakes are expensive
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 📦 Part 3: Complete Installation Steps

### Step 1: Install prAxIs OS (if not already done)

```bash
# In your project directory
cd /path/to/your/project

# Follow prAxIs OS installation process
# (See installation/00-START.md in praxis-os repo)
```

### Step 2: Verify Python Environment

```bash
# Check venv exists
ls .praxis-os/venv/

# Test MCP server can start
.praxis-os/venv/bin/python -m mcp_server --help
```

### Step 3: Configure VS Code Settings

**Option A: Workspace Settings (Recommended)**

Create/edit `.vscode/settings.json` in your project:

```json
{
  "cline.mcpServers": {
    "praxis-os": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Option B: User Settings (Global)**

Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`):
- Type "Preferences: Open User Settings (JSON)"
- Add the same configuration

### Step 4: Create `.clinerules`

Create `.clinerules` file in project root with the content above.

### Step 5: Restart Cline

1. Reload VS Code window: `Cmd+R` / `Ctrl+R`
2. Or restart VS Code completely

### Step 6: Verify MCP Connection

In Cline chat, ask:
```
Can you run search_standards('Agent OS orientation guide')?
```

If successful, Cline will respond with orientation information.

## 🔍 Troubleshooting

### Issue: MCP Server Not Connecting

**Check logs:**
- Open VS Code Output panel
- Select "Cline" from dropdown
- Look for MCP server connection messages

**Common fixes:**
1. Verify Python path is correct:
   ```bash
   which python  # macOS/Linux
   where python  # Windows
   ```

2. Test MCP server manually:
   ```bash
   .praxis-os/venv/bin/python -m mcp_server
   ```

3. Check PYTHONPATH:
   ```bash
   echo $PYTHONPATH
   ```

### Issue: search_standards Tool Not Found

**Verify MCP server is running:**
```bash
# Check if running
ps aux | grep mcp_server

# Check available tools
.praxis-os/venv/bin/python -c "
from mcp_server.server.factory import ServerFactory
from mcp_server.config.loader import ConfigLoader
from pathlib import Path

config = ConfigLoader.load(Path('.praxis-os'))
factory = ServerFactory(config)
server = factory.create_server()
print('MCP Server tools available')
"
```

### Issue: .clinerules Not Being Recognized

**Verify file location:**
```bash
# Should be in project root
ls -la .clinerules
```

**Check file encoding:**
- Must be UTF-8
- No BOM (Byte Order Mark)

## 📊 Verification Checklist

- [ ] `.praxis-os/` directory exists with MCP server
- [ ] Python venv created at `.praxis-os/venv/`
- [ ] `.vscode/settings.json` configured with MCP server
- [ ] `.clinerules` file created in project root
- [ ] VS Code reloaded/restarted
- [ ] Cline can see MCP tools (test with search_standards)
- [ ] Cline follows behavioral rules from .clinerules

## 🎯 Key Differences: Cline vs Cursor

| Feature | Cursor | Cline |
|---------|--------|-------|
| Rules File | `.cursorrules` | `.clinerules` |
| MCP Config | `.cursor/mcp.json` | `.vscode/settings.json` |
| Config Key | `mcpServers` | `cline.mcpServers` |
| Scope | Project-specific | User or Workspace |

## 🚀 Next Steps

Once configured, you can:

1. **Query Standards:**
   ```
   search_standards('production code checklist')
   ```

2. **Start Workflows:**
   ```
   Start spec creation workflow for [feature name]
   ```

3. **Execute Tasks:**
   ```
   Execute tasks from .praxis-os/specs/YYYY-MM-DD-feature/
   ```

The MCP server will provide Cline with access to all prAxIs OS standards, workflows, and specialized tools, just like in Cursor!
</result>
<task_progress>
- [x] Analyze current project
- [x] Research Cline MCP integration
- [x] Identify Cline behavior configuration
- [x] Provide integration steps
- [x] Create equivalent bootstrap instructions
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
so this is where it gets weirder we are running cline in cursor, what are the ramifications of both cline and cursor configuring the same mcp server
</feedback>
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Current Time
10/10/2025, 9:28:19 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
103,469 / 200K tokens used (52%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
# Running Cline in Cursor with Shared MCP Server

## 🎯 The Setup: Dual MCP Configuration

You're running **Cline extension** (VS Code-based agent) **inside Cursor IDE** (which has its own AI agent). Both want to connect to the same prAxIs OS MCP server.

```
┌─────────────────────────────────────┐
│        Cursor IDE (Host)            │
│  ┌───────────────────────────────┐  │
│  │   Cursor's AI Agent           │  │
│  │   (reads .cursorrules)        │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │   Cline Extension             │  │
│  │   (reads .clinerules)         │  │
│  └───────────┬───────────────────┘  │
└──────────────┼───────────────────────┘
               │
               │ Both connect to...
               │
               ▼
    ┌──────────────────────┐
    │  prAxIs OS MCP Server │
    │  (Single Instance)   │
    └──────────────────────┘
```

## ⚠️ Key Ramifications

### 1. **Multiple Concurrent Connections**

**What Happens:**
- Each MCP client (Cursor AI + Cline) spawns its own MCP server process
- The prAxIs OS MCP server runs via stdio transport (one process per client)
- You'll have **two separate server processes** running simultaneously

**Impact:**
```bash
# You'll see two processes like:
python -m mcp_server  # Cursor's connection
python -m mcp_server  # Cline's connection
```

### 2. **Shared State Conflicts**

**Potential Issues:**

#### A. Workflow State Management
- Both agents could start/modify the same workflow
- State stored in `.praxis-os/states/` could be corrupted
- Session IDs might collide

**Risk Level:** 🔴 HIGH

#### B. RAG Index Access
- LanceDB index is **not thread-safe across processes**
- Concurrent reads are OK, but concurrent writes are dangerous
- File watcher might rebuild index while other process is reading

**Risk Level:** 🟡 MEDIUM

#### C. File System Operations
- Both agents could edit the same file simultaneously
- Race conditions in file creation/deletion
- Git conflicts if both try to commit

**Risk Level:** 🔴 HIGH

### 3. **Resource Contention**

**Memory Usage:**
```
prAxIs OS MCP Server × 2:
- 2 Python processes
- 2 LanceDB connections
- 2 sets of loaded embeddings
- 2 file watchers

Estimated: ~1-2GB RAM total
```

**CPU Usage:**
- Two RAG queries running simultaneously
- Two workflow engines checking state
- Potential slowdown during heavy use

### 4. **Configuration Confusion**

**Two Separate Configs:**

```
.cursor/mcp.json        # Cursor AI uses this
.vscode/settings.json   # Cline uses this
```

Both point to same server but:
- Different env vars might be set
- Different working directories
- Different Python paths (if misconfigured)

## ✅ Safe Configuration Strategy

### Option 1: Primary Agent (Recommended)

**Choose ONE agent as primary for prAxIs OS workflows:**

**Use Cursor AI as Primary:**
```bash
# Keep: .cursor/mcp.json with prAxIs OS config
# Keep: .cursorrules with prAxIs OS bootstrap

# Remove/disable Cline's MCP connection
# Delete: .clinerules or leave minimal
```

**Use Cline as Primary:**
```bash
# Keep: .vscode/settings.json with prAxIs OS config
# Keep: .clinerules with prAxIs OS bootstrap

# Disable Cursor AI or don't configure MCP for it
```

### Option 2: Role Separation

**Divide responsibilities between agents:**

**Cursor AI (General Development):**
- General coding assistance
- Quick edits and refactoring
- NO prAxIs OS MCP access
- Minimal .cursorrules

**Cline (Agent OS Workflows):**
- Spec creation and execution
- Standards queries
- Structured workflows
- ONLY one with prAxIs OS MCP access

**Configuration:**

`.cursorrules` (Minimal - No MCP):
```markdown
# Cursor AI Configuration
# General coding assistant - NO prAxIs OS access

## Role
You provide general coding assistance, refactoring, and quick edits.
For structured workflows and standards queries, user will switch to Cline.

## Rules
- Do not attempt to use prAxIs OS tools
- For spec creation, suggest: "Use Cline for this"
- Focus on immediate coding tasks
```

`.clinerules` (Full Agent OS):
```markdown
# Cline Configuration
# prAxIs OS - Full MCP Access

[... full prAxIs OS bootstrap as before ...]
```

`.vscode/settings.json` (Cline only):
```json
{
  "cline.mcpServers": {
    "praxis-os": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os"
      }
    }
  }
}
```

**Don't configure MCP in** `.cursor/mcp.json`

### Option 3: Session Locking (Advanced)

**Implement coordination via files:**

Create `.praxis-os/.lock/active-agent.json`:
```json
{
  "agent": "cursor",  // or "cline"
  "session_id": "abc123",
  "timestamp": "2025-10-10T21:28:00Z"
}
```

Both agents check this before starting workflows and fail if locked by other agent.

## 🔧 Practical Recommendations

### Best Practice: Single Primary Agent

**I recommend using EITHER Cursor OR Cline for Agent OS, not both:**

**Choose Cursor if:**
- ✅ You prefer Cursor's UI/UX
- ✅ You want integrated experience
- ✅ You primarily use Cursor for development

**Choose Cline if:**
- ✅ You prefer Cline's task management
- ✅ You like Cline's approval flow
- ✅ You want more control over agent actions

### Workflow State Protection

**Modify state_manager.py to add locking:**

```python
import fcntl  # Unix
import msvcrt  # Windows

class StateManager:
    def __init__(self, states_dir: Path):
        self.states_dir = states_dir
        self.lock_file = states_dir / ".workflow.lock"
    
    def acquire_lock(self, timeout: int = 5):
        """Acquire exclusive lock for workflow operations."""
        # Prevents both agents from modifying state simultaneously
        ...
```

### File Watcher Coordination

**Modify rag_engine.py to use exclusive file locks:**

```python
def reload_index(self) -> None:
    """Reload with file lock to prevent concurrent rebuilds."""
    lock_file = self.index_path / ".rebuild.lock"
    
    try:
        with open(lock_file, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            # Proceed with reload
            ...
    except BlockingIOError:
        logger.info("Another process is rebuilding index, skipping")
```

## 🎯 Recommended Setup

**For your specific case (Cline in Cursor):**

### 1. Use Cline as prAxIs OS Primary

**Why:**
- Cline has better task/workflow management UI
- Cursor can still be your IDE for editing
- Clear separation of concerns

**Configuration:**

```bash
# prAxIs OS MCP access
.vscode/settings.json  # ✅ Configure Cline MCP
.clinerules           # ✅ Full prAxIs OS bootstrap

# No prAxIs OS for Cursor AI
.cursor/mcp.json      # ❌ Leave empty or remove
.cursorrules          # ✅ Basic rules, no MCP references
```

### 2. Cursor AI for Quick Tasks

Keep `.cursorrules` minimal:

```markdown
# Cursor AI - Quick Assistance Only

You provide quick coding assistance and edits.
You do NOT have access to prAxIs OS tools.

For workflows and structured development:
- User will switch to Cline extension
- Do not attempt prAxIs OS operations

Focus on:
- Code completion and suggestions
- Quick refactoring
- Answering questions about code
```

### 3. Workflow Protocol

**User workflow:**
1. **Use Cursor AI** for quick edits, questions, refactoring
2. **Switch to Cline** when you need:
   - Spec creation
   - Standards queries  
   - Phase-gated workflows
   - Structured task execution

## 🚨 Warning Signs of Conflicts

Watch for these issues:

```bash
# Multiple workflows active
ls .praxis-os/states/*.json  # Should only see one active

# Index corruption
# RAG queries returning garbage or failing

# File editing conflicts
# Git showing unexpected changes

# High memory usage
ps aux | grep python | grep mcp_server  # Should see 1, not 2
```

## 📊 Summary

| Scenario | Risk | Recommendation |
|----------|------|----------------|
| Both agents with MCP | 🔴 HIGH | Don't do this |
| One agent with MCP | 🟢 SAFE | Recommended |
| Role separation | 🟡 MEDIUM | Acceptable with care |
| Locking implemented | 🟢 SAFE | Best if both needed |

**Bottom line:** Configure prAxIs OS MCP for **ONLY Cline**, use Cursor AI for general assistance without prAxIs OS access.
</result>
<task_progress>
- [x] Analyze current project
- [x] Research Cline MCP integration  
- [x] Identify Cline behavior configuration
- [x] Provide integration steps
- [x] Create equivalent bootstrap instructions
- [x] Analyze Cline-in-Cursor dual-agent scenario
- [x] Identify potential conflicts
- [x] Provide safe configuration strategy
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
so this gets to be even more fun, look at the installation process, we want to make sure we support installing to support a variety of agents, cursor, cline, windsurf, cluade code etc, how to we start to buiout that support and make the calling ai poperly either detect what agetnt it is and choose, or prompt and user selsects to the calling ai can install the correct stetup
</feedback>
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Current Time
10/10/2025, 9:33:19 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
106,379 / 200K tokens used (53%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<read_file>
<path>installation/00-START.md</path>
<task_progress>
- [x] Understand current installation process
- [ ] Design agent detection mechanism
- [ ] Create agent configuration matrix
- [ ] Propose installation flow architecture
- [ ] Design modular agent-specific configs
</task_progress>
</read_file>

---

**User:**

[read_file for 'installation/00-START.md'] Result:
# prAxIs OS Installation - START HERE

**Read this file first. It will direct you to the next steps.**

---

## 🎯 What You're About To Do

Install prAxIs OS into the target project. This will:
1. Create `.praxis-os/` directory structure
2. Copy standards, workflows, and MCP server code
3. Create Python virtual environment
4. Configure Cursor to use MCP server
5. Build RAG index

**Total Time**: ~5-10 minutes  
**Complexity**: Medium (vanilla LLM can follow)

---

## ⚠️ CRITICAL: Read These Mistakes FIRST

**These 4 mistakes will break the installation. Read them NOW:**

### Mistake #1: Forgetting `.praxis-os/workflows/` Directory
**What happens**: MCP server validation fails  
**Error message**: `❌ workflows_path does not exist`  
**Prevention**: Step 01 has a checklist - verify ALL 8 directories exist

### Mistake #2: Wrong Module Name in mcp.json
**What happens**: Python module not found error  
**Wrong**: `"mcp_server.praxis_os_rag"`  
**Correct**: `"mcp_server"`  
**Prevention**: Step 05 has the exact JSON to copy

### Mistake #3: Blindly Overwriting .cursorrules
**What happens**: User's existing Cursor rules are destroyed  
**Prevention**: Step 03 checks if file exists first, asks user what to do

### Mistake #4: Forgetting to Copy Workflows
**What happens**: Workflows directory exists but is empty  
**Prevention**: Step 02 has explicit copy command for workflows

---

## 📋 Installation Steps Overview

You'll follow these files in order:

```
00-START.md           ← YOU ARE HERE (clone source, setup)
01-directories.md     Create all required directories
02-copy-files.md      Copy all content from source repo
03-cursorrules.md     Handle .cursorrules safely (don't overwrite!)
04-gitignore.md       Configure .gitignore (prevent committing 2.6GB!)
05-venv-mcp.md        Create venv and mcp.json
06-validate.md        Final validation and cleanup temp files
```

Each file:
- ✅ ~200-250 lines (manageable attention span)
- ✅ Has validation checkpoints
- ✅ Tells you what file to read next
- ✅ Can be re-read if you get confused

---

## 🏗️ Architecture Context

**Source Repository** (praxis-os):
```
/tmp/agent-os-install-xyz/      ← Temp clone (will delete after!)
├── installation/               ← These guides
│   ├── 00-START.md            ← YOU ARE HERE
│   ├── 01-directories.md
│   ├── 02-copy-files.md
│   ├── 03-cursorrules.md
│   ├── 04-venv-mcp.md
│   └── 05-validate.md
├── universal/                  ← Content to copy
│   ├── standards/
│   ├── usage/
│   └── workflows/
├── mcp_server/                 ← Code to copy
└── .cursorrules                ← File to copy (or merge)
```

**⚠️ CRITICAL**: This is a temp directory that will be deleted at the end!

**Target Project** (where you're installing):
```
target-project/                 ← Where you're installing TO
├── .praxis-os/                  ← Will be created
│   ├── standards/
│   ├── usage/
│   ├── workflows/
│   ├── mcp_server/
│   └── venv/
├── .cursorrules                ← Copy or merge
└── .cursor/
    └── mcp.json                ← Create fresh
```

---

## 🔍 Pre-Installation: Get Source Repository

**IMPORTANT**: You need the prAxIs OS source code, but you CANNOT clone it directly into the target project (that would litter a git repo inside their repo).

### Option A: Clone to Temp Directory (Recommended)

```python
import tempfile
import subprocess
import os

