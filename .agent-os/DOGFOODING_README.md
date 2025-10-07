# Dogfooding Setup - agent-os-enhanced

**Date:** 2025-10-06  
**Status:** ✅ TRUE DOGFOODING (no symlinks, real copies)

---

## 🎯 Core Principle

**"Feel consumer pain to prevent shipping bad experiences"**

This `.agent-os/` directory uses REAL COPIES (not symlinks) to experience the exact same installation and update workflow that consumers use.

---

## 📂 Current Structure

```
.agent-os/
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

### Editing Source Code

When you edit framework source:

```bash
# 1. Edit source
vim mcp_server/agent_os_rag.py
# OR
vim universal/standards/ai-safety/production-code-checklist.md

# 2. Copy to .agent-os/ (like consumers do)
cp -r mcp_server .agent-os/
# OR
cp -r universal/standards .agent-os/standards/universal

# 3. Rebuild RAG index
python .agent-os/scripts/build_rag_index.py --force

# 4. Restart MCP server (if code changed)
# Cursor → Settings → MCP → Restart agent-os-rag

# 5. Test (experience real workflow)
# Query MCP to verify changes

# 6. Commit BOTH source and installed copy
git add mcp_server/ .agent-os/mcp_server/
git add universal/standards/ .agent-os/standards/universal/
git commit -m "fix: update something"
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
- ❌ Edit `.agent-os/` files directly (edit source, then copy)
- ❌ Skip copying after editing source
- ❌ Commit source without copying to `.agent-os/`

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
find .agent-os -type l
# Should only show:
# .agent-os/venv/bin/python (normal venv symlink)
# .agent-os/venv/bin/python3 (normal venv symlink)
# No others!
```

### Verify Copies Match Source

```bash
# Standards should match
diff -r universal/standards .agent-os/standards/universal

# MCP server should match
diff -r mcp_server .agent-os/mcp_server
```

---

## 🎯 Success Metrics

**We're truly dogfooding when:**
- [ ] No symlinks (except venv internals)
- [ ] All content is real copies
- [ ] We follow same update workflow as consumers
- [ ] We feel friction and fix it
- [ ] `.agent-os/` serves as reference example for consumers

**We're NOT dogfooding when:**
- [ ] We use symlinks for "convenience"
- [ ] We edit `.agent-os/` directly
- [ ] We skip copying steps
- [ ] We accept friction instead of fixing it

---

## 📝 Reference for Consumers

This `.agent-os/` directory is tracked in git to serve as a **reference example** for consumers.

Consumers can look at:
- File structure
- Generated standards (Python example)
- Config files
- Directory organization

This is REAL installation output, not a special case.

---

**Remember:** Every inconvenience you experience = consumers experience = opportunity to improve before shipping!
