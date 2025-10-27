# Dogfooding Setup - praxis-os

**Date:** 2025-10-06  
**Status:** ✅ TRUE DOGFOODING (no symlinks, real copies)

---

## 🎯 Core Principle

**"Feel consumer pain to prevent shipping bad experiences"**

This `.praxis-os/` directory uses REAL COPIES (not symlinks) to experience the exact same installation and update workflow that consumers use.

---

## 📂 Current Structure

```
.praxis-os/
├── mcp_server/            # ✅ COPIED from ../mcp_server/
├── standards/
│   ├── universal/         # ✅ COPIED from ../../universal/standards/
│   └── development/       # Generated Python-specific standards
├── usage/                 # ✅ COPIED from ../../universal/usage/
├── workflows/             # ✅ COPIED from ../../universal/workflows/
├── venv/                  # Python virtualenv (has normal internal symlinks)
├── .cache/                # RAG index
└── scripts/               # Build scripts
```

**NO SHORTCUTS:**
- ❌ No symlinks for mcp_server (consumers get copies)
- ❌ No symlinks for standards (consumers get copies)
- ✅ Real copies of everything
- ✅ Experience real update workflow
- ✅ Feel all pain points consumers feel

---

## 🔄 Development Workflow

### For AI Agents: Your Development Process

**You are the developer. This is your workflow for making changes to prAxIs OS.**

---

### Task 1: Editing MCP Server Code

**When**: You need to add features, fix bugs, or refactor code in `mcp_server/`

**Steps**:
```bash
# 1. Edit source files in mcp_server/
# Example: vim mcp_server/server/browser_manager.py
# (Use search_replace, write, or other edit tools)

# 2. Copy updated code to .praxis-os/ (CRITICAL)
cp -r mcp_server .praxis-os/

# 3. Verify copy completed
ls -la .praxis-os/mcp_server/

# 4. Restart MCP server (REQUIRED for code changes)
pkill -f "mcp.*agent-os-rag"
# Cursor will auto-restart the server

# 5. Verify in logs
# Cursor → Settings → MCP Servers → agent-os-rag → View Logs
# Look for: "✅ MCP server started" and "✅ Tools registered: X tools"

# 6. Test your changes
# Use MCP tools to verify functionality

# 7. Commit BOTH source and copy
git add mcp_server/ .praxis-os/mcp_server/
git commit -m "feat: add browser automation tool"
```

**Why copy?**
- Dogfooding: You experience the EXACT update workflow customers use
- No symlinks: Validates copy-based installation works
- Pain = opportunities to improve customer experience

---

### Task 2: Editing Universal Standards/Usage

**When**: You need to update documentation, standards, or usage guides

**Steps**:
```bash
# 1. Edit source files in universal/
# Example: vim universal/usage/mcp-server-update-guide.md

# 2. Copy to .praxis-os/
cp -r universal/standards .praxis-os/standards/universal
# OR
cp -r universal/usage .praxis-os/usage

# 3. File watcher auto-detects and rebuilds RAG index (~30 seconds)
# NO manual rebuild needed

# 4. NO restart needed for content changes
# File watcher handles it

# 5. Verify RAG index updated
# Wait ~30 seconds, then test:
# search_standards("your new content keywords")

# 6. Commit BOTH source and copy
git add universal/ .praxis-os/standards/universal/ .praxis-os/usage/
git commit -m "docs: update mcp server update guide"
```

**Why no restart for content?**
- File watcher monitors `.praxis-os/standards/` and `.praxis-os/usage/`
- Auto-rebuilds RAG index on file changes
- Server keeps running, just reindexes content

---

### Task 3: Adding New MCP Tools

**When**: You need to add new functionality (like browser automation)

**Steps**:
```bash
# 1. Create new tool file
# Example: mcp_server/server/tools/browser_tools.py

# 2. Register in tools/__init__.py
# Add import and registration logic

# 3. Update factory.py if needed
# Add dependencies, configuration, etc.

# 4. Copy to .praxis-os/
cp -r mcp_server .praxis-os/

# 5. Restart server (REQUIRED)
pkill -f "mcp.*agent-os-rag"

# 6. Verify tool appears
# Cursor → Chat → Should see new tool available

# 7. Test the tool
# Call it with test parameters

# 8. Write tests (MANDATORY per production checklist)
# tests/unit/test_your_tool.py
# tests/integration/test_your_tool_integration.py

# 9. Run tests
pytest tests/unit/test_your_tool.py -v

# 10. Commit everything
git add mcp_server/ .praxis-os/mcp_server/ tests/
git commit -m "feat: add browser automation tool"
```

**Production Checklist** (search: "production code checklist"):
- ✅ Type hints on all functions
- ✅ Sphinx docstrings with traceability
- ✅ Error handling with remediation
- ✅ Resource cleanup (no leaks)
- ✅ Unit tests (>80% coverage)
- ✅ Integration tests
- ✅ No linter errors

---

### Task 4: Reorganizing Code

**When**: You need to move files or refactor structure (like we did with browser_manager.py)

**Steps**:
```bash
# Example: Moving browser_manager.py to proper location

# 1. Move file in source
mv mcp_server/browser_manager.py mcp_server/server/browser_manager.py

# 2. Update all imports
# search_replace in factory.py: from ..browser_manager → from .browser_manager
# search_replace in tools/browser_tools.py: add import from ..browser_manager
# search_replace in tests: mcp_server.browser_manager → mcp_server.server.browser_manager

# 3. Run tests to verify
pytest tests/unit/test_browser_manager.py -v

# 4. Copy to .praxis-os/ (picks up new structure)
cp -r mcp_server .praxis-os/

# 5. Restart server (REQUIRED)
pkill -f "mcp.*agent-os-rag"

# 6. Verify no import errors in logs
# Cursor → Settings → MCP Servers → View Logs
# Should show clean startup

# 7. Test tools still work
# Call affected MCP tools

# 8. Commit
git add mcp_server/ .praxis-os/mcp_server/ tests/
git commit -m "refactor: move browser_manager to server module"
```

**Key**: Always copy + restart after structural changes

---

## ✅ Verification Checklist (For AI Agents)

**After ANY code change, verify:**

```bash
# 1. Files copied correctly
diff -qr mcp_server .praxis-os/mcp_server
# Should show no differences (or only expected changes)

# 2. Server restarted successfully
# Cursor → Settings → MCP Servers → agent-os-rag → View Logs
# Look for:
# ✅ "MCP server started successfully"
# ✅ "RAG engine initialized"
# ✅ "Workflow engine loaded"
# ✅ "Tools registered: X tools"

# 3. No import errors
# Logs should NOT show:
# ❌ ModuleNotFoundError
# ❌ ImportError
# ❌ AttributeError

# 4. Tools working
# Test affected MCP tools in Cursor chat
# Example: search_standards("test query")

# 5. Tests passing (if you modified code with tests)
pytest tests/unit/test_your_file.py -v
# Should show all green

# 6. No linter errors (if you added/modified code)
# Check Cursor's Problems panel
# Should show 0 errors in files you changed
```

**Checklist Before Committing:**
- [ ] Source files edited
- [ ] Files copied to `.praxis-os/`
- [ ] Server restarted (if code changed)
- [ ] Logs show clean startup
- [ ] MCP tools tested and working
- [ ] Unit tests passing
- [ ] No linter errors
- [ ] Both source and `.praxis-os/` added to git

---

## 🚨 Common Issues & Fixes (For AI Agents)

### Issue: "Changes aren't taking effect"

**Symptoms**: You edited code but server behaves the same

**Root causes**:
1. Forgot to copy to `.praxis-os/`
2. Forgot to restart server
3. Cursor cached old code

**Fix**:
```bash
# 1. Force re-copy
cp -r mcp_server .praxis-os/

# 2. Hard restart server
pkill -f "mcp.*agent-os-rag"

# 3. Verify in logs
# Cursor → Settings → MCP Servers → agent-os-rag → View Logs
# Should show fresh startup with timestamp

# 4. Hard restart Cursor if still not working
# Quit Cursor completely, then reopen
```

---

### Issue: "Import errors after moving files"

**Symptoms**: `ModuleNotFoundError: No module named 'X'`

**Root causes**:
1. Moved file but didn't update imports
2. Moved file but didn't update test patches
3. Updated imports but forgot to copy

**Fix**:
```bash
# 1. Search for all references to old module path
grep -r "old.module.path" mcp_server/ tests/

# 2. Update imports using search_replace
# search_replace in each file

# 3. Update @patch decorators in tests
grep -r "@patch.*old.module.path" tests/
# search_replace each @patch

# 4. Run tests to verify
pytest tests/ -v

# 5. Copy to .praxis-os/
cp -r mcp_server .praxis-os/

# 6. Restart server
pkill -f "mcp.*agent-os-rag"
```

---

### Issue: "Tests failing with mock errors"

**Symptoms**: `TypeError: object AsyncMock can't be used in 'await' expression`

**Root causes**:
1. Incorrectly mocked async context managers
2. Wrong mock return values
3. Missing async/await in test

**Fix**:
```python
# For async context managers like Playwright:
@patch("mcp_server.server.browser_manager.async_playwright")
async def test_something(mock_async_playwright):
    # Create mock context manager
    mock_ctx = AsyncMock()
    mock_instance = AsyncMock()
    
    # Set up async context manager behavior
    mock_async_playwright.return_value = mock_ctx
    mock_ctx.__aenter__.return_value = mock_instance
    mock_ctx.__aexit__.return_value = None
    
    # OR use start() pattern:
    mock_ctx.start.return_value = mock_instance
    
    # Now test your code
```

**Search**: "pytest async mocking patterns" in standards

---

### Issue: "RAG index not updating"

**Symptoms**: Search doesn't return new content you added

**Root causes**:
1. Didn't copy to `.praxis-os/standards/` or `.praxis-os/usage/`
2. File watcher not running
3. Need to wait ~30 seconds for rebuild

**Fix**:
```bash
# 1. Verify file copied
ls -la .praxis-os/standards/universal/your-new-file.md

# 2. Check file watcher is running
# Cursor → Settings → MCP Servers → agent-os-rag → View Logs
# Look for: "File watcher started"

# 3. Wait 30 seconds, then test
sleep 30
# In Cursor: search_standards("keywords from new content")

# 4. If still not working, restart server
pkill -f "mcp.*agent-os-rag"
```

---

## 😩 Pain Points = Opportunities to Improve

When you experience friction during development:

| Pain Point | Consumer Impact | Action |
|------------|----------------|--------|
| "Ugh, copying is annoying" | Consumers feel this too | Create better update command |
| "Ugh, restart is slow" | Consumers wait too | Optimize MCP startup |
| "Ugh, forgot to copy" | Consumers get stale content | Add validation/reminders |
| "Ugh, index rebuild takes time" | Consumers wait too | Optimize indexing |

**Every pain point you feel = consumers feel = MUST FIX before shipping**

---

## ✅ Why This Approach Works

### What We Validate

1. ✅ **Installation process** - copying files works correctly
2. ✅ **Path resolution** - files found in correct locations
3. ✅ **Update workflow** - consumers can update successfully
4. ✅ **File permissions** - no permission issues
5. ✅ **Portability** - no external dependencies (like symlinks)

### What We Catch Early

- File copy errors
- Path bugs
- Missing files
- Permission issues
- Update friction
- Slow processes

### What Symlinks Would Hide

If we used symlinks for "convenience":
- ❌ Instant updates (consumers must re-install)
- ❌ No copy testing (consumers hit copy bugs)
- ❌ No friction (consumers hit friction)
- ❌ False sense of quality

---

## 🚨 Rules

### NEVER:
- ❌ Create symlinks for "convenience"
- ❌ Edit `.praxis-os/` files directly (edit source, then copy)
- ❌ Skip copying after editing source
- ❌ Commit source without copying to `.praxis-os/`

### ALWAYS:
- ✅ Copy after editing source
- ✅ Rebuild index after copying
- ✅ Test in Cursor after changes
- ✅ Feel the pain (it means consumers feel it too)
- ✅ Fix pain before shipping

---

## 📊 Verification

### Check for Symlinks (should only be venv internals)

```bash
find .praxis-os -type l
# Should only show:
# .praxis-os/venv/bin/python (normal venv symlink)
# .praxis-os/venv/bin/python3 (normal venv symlink)
# No others!
```

### Verify Copies Match Source

```bash
# Standards should match
diff -r universal/standards .praxis-os/standards/universal

# MCP server should match
diff -r mcp_server .praxis-os/mcp_server
```

---

## 🎯 Success Metrics

**We're truly dogfooding when:**
- [ ] No symlinks (except venv internals)
- [ ] All content is real copies
- [ ] We follow same update workflow as consumers
- [ ] We feel friction and fix it
- [ ] `.praxis-os/` serves as reference example for consumers

**We're NOT dogfooding when:**
- [ ] We use symlinks for "convenience"
- [ ] We edit `.praxis-os/` directly
- [ ] We skip copying steps
- [ ] We accept friction instead of fixing it

---

## 📝 Reference for Consumers

This `.praxis-os/` directory is tracked in git to serve as a **reference example** for consumers.

Consumers can look at:
- File structure
- Generated standards (Python example)
- Config files
- Directory organization

This is REAL installation output, not a special case.

---

**Remember:** Every inconvenience you experience = consumers experience = opportunity to improve before shipping!
