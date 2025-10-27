# Dual-Transport Troubleshooting Guide

**Feature:** MCP Server Dual-Transport Architecture  
**Date:** 2025-10-11  
**Version:** 1.6.0

---

## Overview

This guide helps diagnose and fix common issues with the dual-transport MCP server. Issues are organized by symptom with specific solutions.

**Quick Diagnostics:**
```bash
# Check if server is running
ps aux | grep mcp_server

# Check state file
cat .praxis-os/.mcp_server_state.json

# Check process is alive
kill -0 $(jq '.pid' .praxis-os/.mcp_server_state.json 2>/dev/null)

# Check IDE logs
# Cursor: View → Output → MCP
# Windsurf: Similar console location
```

---

## Common Issues

### 1. Sub-Agent Can't Discover Server

**Symptom:**
```python
>>> from mcp_server.sub_agents import discover_mcp_server
>>> url = discover_mcp_server()
>>> print(url)
None
```

**Possible Causes:**

#### A. Server Not Running

**Check:**
```bash
ps aux | grep mcp_server
```

**Solution:**
- Start IDE or reload window
- Server starts automatically when IDE opens project

#### B. Transport Mode is Stdio-Only

**Check:**
```bash
jq '.transport' .praxis-os/.mcp_server_state.json
# If output is "stdio", that's the problem
```

**Solution:**
Update `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "agent-os-rag": {
      "args": [
        "-m",
        "mcp_server",
        "--transport",
        "dual"  // Add this!
      ]
    }
  }
}
```

Then reload IDE window.

#### C. State File Missing

**Check:**
```bash
ls -la .praxis-os/.mcp_server_state.json
# If "No such file or directory", that's the problem
```

**Causes:**
1. Server hasn't started yet (wait 2-3 seconds after IDE opens)
2. Server crashed during startup (check IDE logs)
3. Stdio-only mode (no state file created)

**Solution:**
```bash
# Check IDE logs for errors
# Look for:
# - Python import errors
# - Port binding errors
# - Configuration errors

# If using dual mode, state file should appear within 3 seconds
```

#### D. Stale State File (Server Crashed)

**Check:**
```bash
# Get PID from state file
PID=$(jq -r '.pid' .praxis-os/.mcp_server_state.json)

# Check if process is alive
kill -0 $PID 2>/dev/null
if [ $? -ne 0 ]; then
  echo "Process is dead (stale state file)"
fi
```

**Solution:**
```bash
# Remove stale state file
rm .praxis-os/.mcp_server_state.json

# Restart server (reload IDE window)
```

#### E. Wrong Directory

**Check:**
```bash
# Are you in the project directory?
pwd
ls .praxis-os
```

**Solution:**
```python
# Specify explicit path
from pathlib import Path
url = discover_mcp_server(Path("/absolute/path/to/project/.praxis-os"))
```

---

### 2. Connection Refused

**Symptom:**
```
ConnectionError: [Errno 61] Connection refused
```

**Possible Causes:**

#### A. Server Died After Writing State File

**Check:**
```bash
# Check if process is alive
kill -0 $(jq '.pid' .praxis-os/.mcp_server_state.json)

# Check IDE logs for crash
```

**Solution:**
```bash
# Clean restart
rm .praxis-os/.mcp_server_state.json
# Reload IDE window
# Check logs for crash cause
```

#### B. Port Mismatch

**Check:**
```bash
# What port does state file say?
jq '.port' .praxis-os/.mcp_server_state.json

# Is server actually listening on that port?
lsof -i :$(jq -r '.port' .praxis-os/.mcp_server_state.json)
```

**Solution:**
If port mismatch, delete state file and restart server.

#### C. Firewall Blocking Localhost

**Check:**
```bash
# Try curl
curl http://127.0.0.1:$(jq -r '.port' .praxis-os/.mcp_server_state.json)/mcp
```

**Solution:**
- Rare issue on localhost
- Check firewall rules: System Preferences → Security → Firewall
- Allow Python in firewall

---

### 3. Port Already in Use

**Symptom:**
```
OSError: [Errno 48] Address already in use
```

**Server fails to start with this error in IDE logs.**

**Possible Causes:**

#### A. Previous Server Didn't Clean Up

**Check:**
```bash
# What's using the port?
lsof -i :4242
```

**Solution:**
```bash
# Kill the process
kill $(lsof -t -i :4242)

# Or use a different preferred port
```

#### B. All Ports in Range Exhausted

**This is very rare (would need 1000 servers running).**

**Check:**
```bash
# How many ports in use?
for port in {4242..4262}; do
  lsof -i :$port 2>/dev/null && echo "Port $port in use"
done
```

**Solution:**
```yaml
# .praxis-os/config.yaml
mcp:
  http_port: 5500  # Use different range
```

#### C. Port Range Conflicts

**If you run many projects simultaneously:**

**Solution:**
- Server auto-increments ports (4242 → 4243 → 4244...)
- This should "just work" for up to 1000 projects
- If it doesn't, check IDE logs for the actual error

---

### 4. IDE Doesn't Load MCP Server

**Symptom:**
- No MCP tools available in IDE
- IDE doesn't show MCP server in status

**Possible Causes:**

#### A. Config File Not Found

**Check:**
```bash
# Cursor
ls .cursor/mcp.json

# Windsurf
ls .windsurf/mcp.json

# Claude Desktop
ls ~/Library/Application\ Support/Claude/claude_desktop_config.json  # macOS
```

**Solution:**
Create or fix config file. See `IDE-CONFIGURATION.md`.

#### B. Invalid JSON

**Check:**
```bash
# Validate JSON syntax
jq '.' .cursor/mcp.json
# If error, JSON is invalid
```

**Solution:**
Fix JSON syntax errors (missing commas, quotes, braces).

#### C. Wrong Python Path

**Check:**
```bash
# Does venv exist?
ls .praxis-os/venv/bin/python

# Can we run it?
.praxis-os/venv/bin/python --version
```

**Solution:**
If venv missing or broken:
```bash
cd .praxis-os
python3 -m venv venv
venv/bin/pip install -r mcp_server/requirements.txt
```

#### D. MCP Server Code Missing

**Check:**
```bash
ls .praxis-os/mcp_server/__main__.py
```

**Solution:**
Reinstall Agent OS (see installation guide).

#### E. IDE Needs Restart

**Solution:**
- Cmd+Shift+P (macOS) or Ctrl+Shift+P (Windows/Linux)
- Type: "Reload Window"
- Or fully quit and restart IDE

---

### 5. Different Port Every Time

**Symptom:**
State file shows different port after each server restart.

**Is This a Problem?**

**No, this is expected behavior!**

Ports are ephemeral:
- Released when server stops
- Reallocated when server starts
- Sub-agents auto-discover new port via state file

**Why This Happens:**
1. Server shuts down, releases port
2. Between shutdown and restart, another process takes the port
3. Server starts, tries preferred port (4242), finds it taken
4. Server increments to next available port (4243)

**If You Need Consistent Port:**
```yaml
# .praxis-os/config.yaml
mcp:
  http_port: 4242  # Preferred port
```

**Note:** This is a *preference*, not a guarantee. If port is taken, server will still increment.

---

### 6. Multiple Projects Conflict

**Symptom:**
- Running multiple projects simultaneously
- Sub-agent connects to wrong project's server

**Possible Causes:**

#### A. Auto-Discovery From Wrong Directory

**Check:**
```bash
# Where are you running the script?
pwd

# Does this directory have .praxis-os/?
ls .praxis-os
```

**Solution:**
```python
# Use explicit paths
from pathlib import Path
url_a = discover_mcp_server(Path("~/projects/project-a/.praxis-os"))
url_b = discover_mcp_server(Path("~/projects/project-b/.praxis-os"))
```

#### B. Shared State File (Misconfiguration)

**Check:**
```bash
# Each project should have independent state files
ls ~/projects/project-a/.praxis-os/.mcp_server_state.json
ls ~/projects/project-b/.praxis-os/.mcp_server_state.json
```

**Solution:**
Ensure each project has its own `.praxis-os/` directory.

---

### 7. Slow Performance

**Symptom:**
- Tool calls take a long time
- Sub-agent connections are slow

**Possible Causes:**

#### A. RAG Index Building

**Check IDE logs for:**
```
Building RAG index...
Processing 1234 chunks...
```

**This happens on server startup (first time or after config changes).**

**Solution:**
- Wait for index build to complete (10-30 seconds)
- Future startups will be faster (index cached)

#### B. Too Many Concurrent Requests

**Check:**
```bash
# How many sub-agents are connected?
# Hard to check directly, but symptoms include:
# - Slow responses
# - Timeouts
# - CPU usage high for mcp_server process
```

**Solution:**
- Reduce concurrent requests
- Add delays between tool calls
- Use connection pooling

#### C. Large Project / Large Index

**Check:**
```bash
# How big is the RAG index?
du -sh .praxis-os/.cache/vector_index
```

**If > 500MB:**
- Index may be slow to search
- Consider excluding large files from standards/

---

### 8. State File Keeps Appearing/Disappearing

**Symptom:**
State file is created, then deleted, then created again...

**Possible Causes:**

#### A. Server Crashing Repeatedly

**Check IDE logs for crash messages.**

**Common Crash Causes:**
1. Import errors (missing dependencies)
2. Configuration errors (invalid config.yaml)
3. Port binding errors (permission issues)

**Solution:**
```bash
# Check dependencies
.praxis-os/venv/bin/pip list

# Validate config
cat .praxis-os/config.yaml

# Check permissions
ls -la .praxis-os/

# Try running manually to see errors
.praxis-os/venv/bin/python -m mcp_server --transport dual --log-level DEBUG
```

#### B. Multiple IDE Instances

**If you have same project open in multiple IDE windows:**

**Solution:**
- Close all but one IDE window
- Each project should have ONE main IDE instance
- Sub-agents can connect from anywhere (unlimited)

---

### 9. Sub-Agent Gets Stale Data

**Symptom:**
Sub-agent queries standards but gets outdated results.

**Possible Causes:**

#### A. RAG Index Not Rebuilt

**Standards updated but index wasn't rebuilt.**

**Check:**
```bash
# When was index last modified?
stat -f "%Sm" .praxis-os/.cache/vector_index/*.lance 2>/dev/null || \
stat -c "%y" .praxis-os/.cache/vector_index/*.lance 2>/dev/null
```

**Solution:**
```bash
# Force index rebuild
rm -rf .praxis-os/.cache/vector_index
# Restart server (reload IDE window)
```

#### B. Caching in Sub-Agent

**Some sub-agents cache responses.**

**Solution:**
- Restart sub-agent
- Clear sub-agent cache (if supported)
- Force re-query with updated parameters

---

### 10. Windows-Specific Issues

**Symptom:**
Issues that only occur on Windows.

#### A. Backslash in Paths

**Windows uses backslashes `\`, which need escaping in JSON.**

**Solution:**
```json
{
  "command": "C:\\path\\to\\.praxis-os\\venv\\Scripts\\python.exe",
  // or
  "command": "C:/path/to/.praxis-os/venv/Scripts/python.exe"
}
```

#### B. PID Validation Fails

**Windows requires `psutil` for accurate PID checking.**

**Check:**
```bash
.praxis-os\venv\Scripts\python -c "import psutil"
```

**Solution:**
```bash
.praxis-os\venv\Scripts\pip install psutil
```

#### C. Port Already in Use (Windows)

**Windows sometimes doesn't release ports immediately.**

**Solution:**
```bash
# List processes using port
netstat -ano | findstr :4242

# Kill process by PID
taskkill /PID <pid> /F
```

---

## Debug Commands Reference

### Check Server Status

```bash
# Is server running?
ps aux | grep mcp_server | grep -v grep

# Get server PID
pgrep -f mcp_server

# Check server process details
ps -p $(pgrep -f mcp_server) -f
```

### Check State File

```bash
# State file exists?
ls -la .praxis-os/.mcp_server_state.json

# View state file
cat .praxis-os/.mcp_server_state.json

# Validate JSON
jq '.' .praxis-os/.mcp_server_state.json

# Get specific fields
jq '.transport' .praxis-os/.mcp_server_state.json  # Transport mode
jq '.url' .praxis-os/.mcp_server_state.json        # HTTP URL
jq '.port' .praxis-os/.mcp_server_state.json       # HTTP port
jq '.pid' .praxis-os/.mcp_server_state.json        # Server PID
```

### Check Process Liveness

```bash
# Check if PID is alive
PID=$(jq -r '.pid' .praxis-os/.mcp_server_state.json)
kill -0 $PID 2>/dev/null && echo "Alive" || echo "Dead"

# Alternative (macOS/Linux)
ps -p $PID >/dev/null 2>&1 && echo "Alive" || echo "Dead"
```

### Check Port Usage

```bash
# What's using port 4242?
lsof -i :4242

# Get PID of process using port
lsof -t -i :4242

# Kill process using port
kill $(lsof -t -i :4242)

# Check port range
for port in {4242..4252}; do
  lsof -i :$port 2>/dev/null && echo "Port $port in use"
done
```

### Test HTTP Endpoint

```bash
# Try connecting to HTTP endpoint
PORT=$(jq -r '.port' .praxis-os/.mcp_server_state.json)
curl -v http://127.0.0.1:$PORT/mcp

# Should return JSON-RPC response or 404 (not connection refused)
```

### Check Configuration

```bash
# Validate config.yaml
cat .praxis-os/config.yaml

# Check HTTP port setting
grep -A 5 "^mcp:" .praxis-os/config.yaml

# Check if config is valid YAML
python -c "import yaml; yaml.safe_load(open('.praxis-os/config.yaml'))"
```

### Check Dependencies

```bash
# List installed packages
.praxis-os/venv/bin/pip list

# Check specific package
.praxis-os/venv/bin/pip show fastmcp

# Verify imports work
.praxis-os/venv/bin/python -c "import fastmcp; print(fastmcp.__version__)"
```

### Manual Server Start (Debug Mode)

```bash
# Run server manually with debug logging
.praxis-os/venv/bin/python -m mcp_server \
  --transport dual \
  --log-level DEBUG

# Check output for errors
# Server will run in foreground, showing all logs
```

---

## Error Messages Decoded

### "No available ports in range 4242-5242"

**Meaning:** All 1000 ports are in use (very rare).

**Solution:**
```yaml
# Use different port range
mcp:
  http_port: 6000
```

### "State file validation failed"

**Meaning:** State file is corrupted or has invalid format.

**Solution:**
```bash
rm .praxis-os/.mcp_server_state.json
# Restart server
```

### "PID X is not running"

**Meaning:** Server process died, state file is stale.

**Solution:**
```bash
rm .praxis-os/.mcp_server_state.json
# Restart server
```

### "HTTP server failed to start"

**Meaning:** Port binding failed.

**Solution:**
```bash
# Check what's using the port
lsof -i :$(jq -r '.port' .praxis-os/.mcp_server_state.json)

# Kill it or use different port
```

### "FastMCP instance not initialized"

**Meaning:** Server internal error.

**Solution:**
- Check IDE logs for full error
- Usually an import or configuration error
- Try `--log-level DEBUG`

---

## Getting Help

### 1. Enable Debug Logging

**File:** `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "args": [
        "-m",
        "mcp_server",
        "--transport",
        "dual",
        "--log-level",
        "DEBUG"
      ]
    }
  }
}
```

**View logs:** IDE console/output panel

### 2. Run Manual Test

```bash
# Test discovery
python -c "from mcp_server.sub_agents import discover_mcp_server; print(discover_mcp_server())"

# Test full integration
python -m mcp_server.sub_agents.mcp_client_example
```

### 3. Check File Permissions

```bash
# State file should be readable
ls -la .praxis-os/.mcp_server_state.json

# Config should be readable
ls -la .praxis-os/config.yaml

# Venv should be executable
ls -la .praxis-os/venv/bin/python
```

### 4. Verify Installation

```bash
# All required files present?
ls .praxis-os/mcp_server/__main__.py
ls .praxis-os/mcp_server/port_manager.py
ls .praxis-os/mcp_server/project_info.py
ls .praxis-os/mcp_server/transport_manager.py
ls .praxis-os/mcp_server/sub_agents/discovery.py
```

### 5. Collect Diagnostic Info

```bash
#!/bin/bash
# Save as: diagnose.sh

echo "=== System Info ==="
uname -a
python3 --version

echo -e "\n=== Server Process ==="
ps aux | grep mcp_server | grep -v grep

echo -e "\n=== State File ==="
cat .praxis-os/.mcp_server_state.json 2>/dev/null || echo "State file not found"

echo -e "\n=== Config ==="
cat .praxis-os/config.yaml 2>/dev/null || echo "Config not found"

echo -e "\n=== Port Usage ==="
PORT=$(jq -r '.port' .praxis-os/.mcp_server_state.json 2>/dev/null)
if [ ! -z "$PORT" ]; then
  lsof -i :$PORT
fi

echo -e "\n=== Venv ==="
.praxis-os/venv/bin/python --version 2>/dev/null || echo "Venv not found"
.praxis-os/venv/bin/pip list 2>/dev/null | grep -E "(fastmcp|mcp|lancedb)"
```

**Run and share output when asking for help.**

---

## Prevention Tips

### ✅ Do's

1. **Use dual transport by default**
   ```json
   "args": ["-m", "mcp_server", "--transport", "dual"]
   ```

2. **Let server manage ports**
   - Don't hardcode ports
   - Use discovery utility

3. **Clean shutdown**
   - Close IDE normally (don't force kill)
   - State file will be cleaned up automatically

4. **Keep dependencies updated**
   ```bash
   .praxis-os/venv/bin/pip install --upgrade -r mcp_server/requirements.txt
   ```

5. **Monitor logs**
   - Check IDE console for warnings
   - Address errors before they compound

### ❌ Don'ts

1. **Don't manually edit state file**
   - It's managed by server
   - Edits will be overwritten

2. **Don't run multiple servers per project**
   - One main IDE instance
   - Unlimited sub-agents

3. **Don't commit state file**
   - It's in `.gitignore`
   - Ephemeral per-project

4. **Don't assume port 4242**
   - Use discovery
   - Port may vary

5. **Don't skip error messages**
   - Read IDE console logs
   - Errors usually have clear solutions

---

## Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Sub-agent can't find server | `rm .praxis-os/.mcp_server_state.json` + restart IDE |
| Port conflict | Server auto-increments (should resolve itself) |
| Stale state file | `rm .praxis-os/.mcp_server_state.json` |
| IDE not loading tools | Reload window (Cmd+Shift+P → Reload Window) |
| Connection refused | Check PID is alive, restart if dead |
| Different port each time | Expected behavior, use discovery |
| Slow startup | RAG index building (wait 10-30s) |
| Import errors | Reinstall deps: `pip install -r requirements.txt` |

---

## Summary

Most issues stem from:
1. **Server not running** → Start IDE
2. **Wrong transport mode** → Add `--transport dual`
3. **Stale state file** → Delete and restart
4. **Missing dependencies** → Reinstall venv

**Diagnostic Flow:**
```
1. Check process: ps aux | grep mcp_server
   └─ Not running? Restart IDE

2. Check state file: cat .praxis-os/.mcp_server_state.json
   └─ Missing? Check transport mode
   └─ Present? Check PID is alive

3. Check PID: kill -0 <pid>
   └─ Dead? Delete state file, restart

4. Check port: lsof -i :<port>
   └─ Nothing? Server didn't start HTTP
   └─ Something? Verify it's mcp_server

5. Check logs: IDE console
   └─ Look for errors, follow remediation
```

**Still stuck?**
- Run `diagnose.sh` script above
- Check `.praxis-os/specs/2025-10-11-mcp-dual-transport/` for detailed specs
- See `THREAD-SAFETY.md` for performance considerations
- Review `SUB-AGENT-INTEGRATION.md` for integration patterns

**Status:** ✅ Production Ready (2025-10-11)

