# Cursor Data Discovery - Finding Logs, Configs, and State

**Keywords for search**: Cursor logs location, MCP server logs, Cursor config files, Cursor workspace storage, debugging Cursor, where are Cursor logs, find MCP logs, Cursor Application Support, troubleshooting MCP, Cursor state files, MCP server debugging, Cursor log files macOS, VS Code data locations, IDE data discovery, agent debugging logs

---

## 🚨 TL;DR - Cursor Data Discovery Quick Reference

**Core Principle:** Cursor stores data in OS-specific standard locations. Use discovery patterns to find logs, configs, and state dynamically rather than hardcoding paths.

**Key Locations (macOS):**
1. **Application Support** - Main data directory
   - Pattern: `~/Library/Application Support/Cursor/`
   - Contains: logs, config, workspace storage, extensions

2. **MCP Server Logs** - Located in extension host logs
   - Pattern: `~/Library/Application Support/Cursor/logs/<SESSION>/window<N>/exthost/anysphere.cursor-mcp/`
   - File pattern: `MCP project-<N>-<PROJECT_NAME>-<SERVER_NAME>.log`

3. **Workspace Storage** - Project-specific data
   - Pattern: `~/Library/Application Support/Cursor/User/workspaceStorage/<HASH>/`

4. **User Config** - Global settings
   - Pattern: `~/Library/Application Support/Cursor/User/`
   - Files: `settings.json`, `keybindings.json`

**Discovery Pattern (Don't Hardcode):**
```bash
# Find latest log session
find ~/Library/Application\ Support/Cursor/logs -type d -maxdepth 1 | sort | tail -1

# Find MCP logs
find ~/Library/Application\ Support/Cursor/logs -name "MCP*.log" | sort -t/ -k10 | tail -5

# Find workspace for current project
ls -td ~/Library/Application\ Support/Cursor/User/workspaceStorage/*/ | head -1
```

**When to Use:**
- Debugging MCP server issues
- Troubleshooting Cursor behavior
- Investigating extension problems
- Monitoring file watcher activity
- Checking MCP tool calls

---

## ❓ Questions This Answers

1. Where are Cursor MCP server logs located?
2. How do I find Cursor logs on macOS?
3. Where does Cursor store configuration files?
4. How do I debug MCP server issues?
5. Where is workspace-specific data stored?
6. How do I find the latest Cursor log session?
7. What is the MCP log file naming pattern?
8. Where are extension host logs?
9. How do I monitor file watcher activity?
10. Where does Cursor store user settings?
11. How do I find logs for a specific project?
12. What is the workspaceStorage directory structure?
13. How do I troubleshoot RAG index issues?
14. Where are MCP tool call logs?
15. How do I check if file watcher is working?
16. Where does Cursor store session data?
17. How do I find logs without hardcoding paths?
18. What is the Application Support directory structure?
19. How do I discover Cursor data locations dynamically?
20. Where are renderer logs vs extension host logs?

---

## 🎯 Purpose

Define discovery patterns for Cursor's data locations (logs, configs, state) to enable effective debugging and troubleshooting without hardcoding environment-specific paths.

**Key Distinction:** Discovery patterns vs hardcoded paths
- **Discovery patterns**: Use `find`, `ls`, patterns to locate dynamically
- **Hardcoded paths**: Brittle, environment-specific, breaks across systems

---

## ❌ The Problem - Without Discovery Patterns

**For developers:**
- ❌ Can't find MCP server logs when debugging
- ❌ Hardcoded paths that don't work on other systems
- ❌ Manual hunting through directories
- ❌ Can't programmatically access latest logs

**For troubleshooting:**
- ❌ No systematic way to find relevant logs
- ❌ Miss important diagnostic information
- ❌ Can't verify file watcher is working
- ❌ Can't monitor RAG index rebuilds

**For standards:**
- ❌ Can't document universal discovery process
- ❌ Environment-specific instructions that don't generalize
- ❌ Instructions break when log sessions rotate

---

## ✅ The Standard - Discovery Patterns

### macOS Data Locations

**Application Support Root:**
```
~/Library/Application Support/Cursor/
├── logs/                           # Log sessions
│   └── <YYYYMMDDTHHMMSS>/          # Session timestamp
│       ├── main.log                # Main process logs
│       ├── sharedprocess.log       # Shared process logs
│       └── window<N>/              # Window-specific logs
│           ├── exthost/            # Extension host logs
│           │   └── anysphere.cursor-mcp/  # MCP extension logs
│           │       └── MCP project-<N>-<PROJECT>-<SERVER>.log
│           ├── fileWatcher.log     # File watcher activity
│           ├── renderer.log        # Renderer process logs
│           └── output_<TIMESTAMP>/ # Output channel logs
│               └── cursor.hooks.log
├── User/                           # User-level data
│   ├── settings.json               # Global settings
│   ├── keybindings.json            # Key bindings
│   └── workspaceStorage/           # Workspace data
│       └── <HASH>/                 # Project-specific hash
└── Service Worker/                 # Service worker data
```

### Discovery Pattern 1: Find Latest Log Session

**Problem:** Log session names rotate (timestamped)

**Solution:** Find dynamically
```bash
# Find latest session
LATEST_SESSION=$(find ~/Library/Application\ Support/Cursor/logs \
  -type d -maxdepth 1 -name "20*" | sort | tail -1)

echo "Latest session: $LATEST_SESSION"
```

**Result:** Always finds current session regardless of timestamp

---

### Discovery Pattern 2: Find MCP Server Logs

**Problem:** MCP log location varies by window and project

**Solution:** Search by pattern
```bash
# Find all MCP logs (latest first)
find ~/Library/Application\ Support/Cursor/logs \
  -name "MCP*.log" -type f \
  -printf '%T@ %p\n' 2>/dev/null | \
  sort -rn | head -5 | cut -d' ' -f2

# Or on macOS (no -printf):
find ~/Library/Application\ Support/Cursor/logs \
  -name "MCP*.log" -type f \
  -exec stat -f "%m %N" {} \; | \
  sort -rn | head -5 | cut -d' ' -f2-
```

**For specific project:**
```bash
# Find MCP log for praxis-os project
find ~/Library/Application\ Support/Cursor/logs \
  -name "MCP*praxis-os*.log" -type f | \
  sort | tail -1
```

**Result:** Finds relevant logs without hardcoding window numbers or timestamps

---

### Discovery Pattern 3: Monitor File Watcher Activity

**Problem:** Need to verify file watcher detected changes

**Solution:** Tail file watcher log
```bash
# Find and tail file watcher log
LATEST_SESSION=$(find ~/Library/Application\ Support/Cursor/logs \
  -type d -maxdepth 1 -name "20*" | sort | tail -1)

tail -f "$LATEST_SESSION"/window*/fileWatcher.log
```

**Look for:**
```
2025-11-01 12:50:46 [info] File changed: .praxis-os/standards/development/multi-agent-architecture.md
```

---

### Discovery Pattern 4: Check RAG Index Rebuilds

**Problem:** Need to verify auto-rebuild triggered

**Solution:** Search MCP logs for rebuild activity
```bash
# Find latest MCP log for praxis-os
MCP_LOG=$(find ~/Library/Application\ Support/Cursor/logs \
  -name "MCP*praxis-os*.log" -type f | sort | tail -1)

# Check for recent rebuilds
grep -E "(watcher|rebuild|index|Found.*changed files)" "$MCP_LOG" | tail -20
```

**Look for sequence:**
```
Found 1 changed files
🗑️  Removing old chunks for changed files...
Processing 1 markdown files
✅ Index incremental update complete in 0.4s
Reloading LanceDB index...
✅ Index incremental complete. RAG engine reloaded with fresh index.
```

---

### Discovery Pattern 5: Debug MCP Tool Calls

**Problem:** Need to see what tools are being called

**Solution:** Monitor MCP log
```bash
# Find and tail MCP log
MCP_LOG=$(find ~/Library/Application\ Support/Cursor/logs \
  -name "MCP*praxis-os*.log" -type f | sort | tail -1)

tail -f "$MCP_LOG" | grep -E "(pos_search|CallToolRequest)"
```

**Look for:**
```
[INFO] mcp.server.lowlevel.server: Processing request of type CallToolRequest
[INFO] mcp_server.server.tools.rag_tools: pos_search: query='...', n_results=5
[INFO] mcp_server.server.tools.rag_tools: pos_search completed: 3 results, 512 tokens, 45.2ms
```

---

### Discovery Pattern 6: Find Workspace Storage

**Problem:** Need to find workspace-specific data

**Solution:** Match by project path or name
```bash
# List all workspace storage (sorted by modification time)
ls -td ~/Library/Application\ Support/Cursor/User/workspaceStorage/*/ | head -10

# Find workspace containing specific file
grep -l "praxis-os" \
  ~/Library/Application\ Support/Cursor/User/workspaceStorage/*/workspace.json \
  2>/dev/null | head -1
```

---

## 📋 Checklist - Data Discovery

### When Debugging MCP Issues

- [ ] Find latest log session dynamically (don't hardcode timestamp)
- [ ] Locate MCP server log for specific project
- [ ] Check file watcher log for change detection
- [ ] Verify RAG index rebuild triggered
- [ ] Monitor MCP tool calls in real-time
- [ ] Check for LanceDB errors (index corruption)
- [ ] Verify graceful degradation to grep fallback

### When Writing Standards/Docs

- [ ] Use discovery patterns (find, grep)
- [ ] Never hardcode session timestamps
- [ ] Never hardcode window numbers
- [ ] Never hardcode workspace hashes
- [ ] Provide cross-platform discovery if possible
- [ ] Document expected log patterns
- [ ] Include examples with dynamic paths

### When Troubleshooting

- [ ] Tail logs in real-time (don't just read static files)
- [ ] Filter logs for relevant patterns
- [ ] Check timestamps to correlate events
- [ ] Look for error sequences (not just single errors)
- [ ] Verify file system changes vs log events
- [ ] Check multiple log sources (MCP, file watcher, renderer)

---

## 💡 Examples - Real-World Debugging

### Example 1: Verify File Watcher Detected New File

**Scenario:** Created new standard, want to confirm auto-rebuild

**Discovery sequence:**
```bash
# 1. Find latest MCP log
MCP_LOG=$(find ~/Library/Application\ Support/Cursor/logs \
  -name "MCP*praxis-os*.log" -type f | sort | tail -1)

# 2. Check for recent file changes
grep "Found.*changed files" "$MCP_LOG" | tail -5

# 3. Check rebuild completion
grep "Index incremental complete" "$MCP_LOG" | tail -1
```

**Expected output:**
```
2025-11-01 12:50:30 Found 1 changed files
2025-11-01 12:50:31 ✅ Index incremental complete. RAG engine reloaded with fresh index.
```

**Interpretation:**
- ✅ File watcher detected change
- ✅ Auto-rebuild completed in ~1 second
- ✅ No manual rebuild needed

---

### Example 2: Diagnose RAG Index Corruption

**Scenario:** `pos_search` returning no results, suspect index issue

**Discovery sequence:**
```bash
# 1. Find latest MCP log
MCP_LOG=$(find ~/Library/Application\ Support/Cursor/logs \
  -name "MCP*praxis-os*.log" -type f | sort | tail -1)

# 2. Check for LanceDB errors
grep -A5 "lance error\|RuntimeError" "$MCP_LOG" | tail -20

# 3. Check for grep fallback
grep "Falling back to grep" "$MCP_LOG" | tail -5
```

**Possible findings:**
```
RuntimeError: lance error: LanceError(IO): External error: Not found: ...
Falling back to grep search
```

**Root cause:** Index corrupted (often from manual rebuild while MCP server running)

**Resolution:**
```bash
# Wait for file watcher to trigger auto-rebuild
# OR restart Cursor (clean MCP server start)
# OR run rebuild script when MCP server NOT running
```

---

### Example 3: Monitor MCP Tool Performance

**Scenario:** Queries feel slow, want to measure performance

**Discovery sequence:**
```bash
# Find and tail MCP log
MCP_LOG=$(find ~/Library/Application\ Support/Cursor/logs \
  -name "MCP*praxis-os*.log" -type f | sort | tail -1)

# Monitor query performance
tail -f "$MCP_LOG" | grep "pos_search completed"
```

**Watch for:**
```
pos_search completed: 5 results, 512 tokens, 45.2ms    # ✅ Fast (vector search)
pos_search completed: 0 results, 0 tokens, 5096.9ms    # ❌ Slow (grep timeout)
```

**Interpretation:**
- <100ms: Vector search working (good)
- >5000ms: Grep fallback timeout (index issue)

---

## 🚫 Anti-Patterns - Common Mistakes

### Anti-Pattern 1: Hardcoding Log Paths

**Wrong:**
```bash
# Hardcoded timestamp
tail ~/Library/Application\ Support/Cursor/logs/20251030T141913/window1/exthost/anysphere.cursor-mcp/MCP*.log
```

**Problem:** Breaks when:
- New Cursor session starts (different timestamp)
- Different window has MCP server
- Different project name

**Right:**
```bash
# Dynamic discovery
find ~/Library/Application\ Support/Cursor/logs \
  -name "MCP*praxis-os*.log" -type f | sort | tail -1 | xargs tail
```

---

### Anti-Pattern 2: Reading Static Log Files

**Wrong:**
```bash
# Read once
cat ~/path/to/mcp.log | grep "error"
```

**Problem:** Misses real-time activity, can't correlate with actions

**Right:**
```bash
# Tail in real-time
MCP_LOG=$(find ~/Library/Application\ Support/Cursor/logs \
  -name "MCP*praxis-os*.log" -type f | sort | tail -1)

tail -f "$MCP_LOG" | grep --line-buffered "error\|watcher\|rebuild"
```

---

### Anti-Pattern 3: Assuming Single Window

**Wrong:**
```bash
# Assumes window1
tail ~/Library/Application\ Support/Cursor/logs/*/window1/exthost/*/MCP*.log
```

**Problem:** MCP server could be in window2, window3, etc.

**Right:**
```bash
# Search all windows
find ~/Library/Application\ Support/Cursor/logs \
  -path "*/window*/exthost/*/MCP*.log" | sort | tail -1
```

---

### Anti-Pattern 4: Manual Rebuild While MCP Running

**Wrong:**
```bash
# MCP server is running (Cursor open)
python .praxis-os/scripts/build_rag_index.py --force
```

**Problem:** Corrupts LanceDB index (open file handles)

**Right:**
```bash
# Trust file watcher to auto-rebuild
# OR close Cursor first, then rebuild
# OR check logs to verify auto-rebuild happened
```

---

## 🔗 Related Standards

**Query for related patterns:**
```python
pos_search_project(content_type="standards", query="file watcher automatic rebuild RAG index")
pos_search_project(content_type="standards", query="MCP server debugging troubleshooting logs")
pos_search_project(content_type="standards", query="LanceDB index corruption graceful degradation")
pos_search_project(content_type="standards", query="grep fallback timeout RAG search")
```

**Key related documents:**
- `.praxis-os/standards/development/dogfooding-model.md` - File watcher behavior
- `.praxis-os/standards/development/multi-agent-architecture.md` - MCP server architecture
- `.praxis-os/mcp_server/monitoring/watcher.py` - File watcher implementation

---

## 🔄 Maintenance

**Update this standard when:**
- Cursor changes log directory structure
- MCP extension changes log file naming
- New log sources become available
- Discovery patterns fail on new OS versions
- Better discovery methods emerge

**Review quarterly or when:**
- Debugging becomes difficult (paths changed?)
- Discovery patterns break
- New Cursor version released
- Cross-platform support needed (Windows, Linux)

---

## ✅ Success Criteria

A contributor understands Cursor data discovery when they can:

- [ ] Find latest MCP log without hardcoding paths
- [ ] Monitor file watcher activity in real-time
- [ ] Diagnose RAG index issues from logs
- [ ] Verify auto-rebuild triggered for file changes
- [ ] Locate workspace storage dynamically
- [ ] Use discovery patterns in standards/docs
- [ ] Debug MCP issues systematically
- [ ] Avoid hardcoding environment-specific paths

---

**Last Updated:** 2025-11-01  
**Status:** Active  
**Scope:** praxis-os development (local standard, not distributed)  
**Platform:** macOS (patterns adaptable to Linux/Windows)

