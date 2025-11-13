# Dev Environment vs Distribution Artifacts - Workflow Standard

**Keywords for search**: dev environment, distribution artifacts, .praxis-os workflow, where to make changes, copy up workflow, development workflow, file organization, skeleton files, when to ship, dev vs prod

---

## 🚨 TL;DR - Dev Environment Workflow (CRITICAL)

**THE GOLDEN RULE: ALL development happens in `.praxis-os/` - NEVER copy from distribution → dev!**

```
.praxis-os/              ← 🟢 DEV ENVIRONMENT
                           ✅ ALL work happens here
                           ✅ Live, running code
                           ✅ Make all changes here

dist/ouroboros/          ← 🔵 DISTRIBUTION ARTIFACTS
dist/universal/          ← 🔵 DISTRIBUTION ARTIFACTS
                           ❌ STALE until shipped
                           ❌ READ ONLY until "ship it"
                           ✅ Sync UP only when told (sync-to-dist.sh)
```

**Workflow:**
1. ✅ Edit in `.praxis-os/` (dev environment)
2. ✅ Test in `.praxis-os/` (live running code)
3. ✅ Validate in `.praxis-os/` (confirm it works)
4. 🛑 STOP - Wait for explicit "ship it" instruction
5. ✅ ONLY THEN copy from `.praxis-os/` → distribution

**If you violate this:** Lost work, hours of debugging, file corruption, confusion.

---

## ❓ Questions This Answers

1. "Where do I make code changes in praxis-os?"
2. "What is the .praxis-os directory?"
3. "What are distribution artifacts?"
4. "When do I copy files to universal/ or mcp_server/?"
5. "Why are there duplicate files in different locations?"
6. "What is the 'copy up' workflow?"
7. "Can I edit files in universal/ or mcp_server/?"
8. "What happens if I copy distribution files back to .praxis-os/?"
9. "How do I know when to ship changes?"
10. "What is the dev vs distribution pattern?"
11. "Why did I lose work by copying files the wrong direction?"
12. "What does 'ship it' mean?"
13. "Where is the live, running MCP server code?"
14. "What files are in the dev environment?"
15. "What is the skeleton directory structure?"

---

## 🎯 Purpose

Define the ONE-WAY workflow for praxis-os development: changes flow from dev environment (`.praxis-os/`) to distribution artifacts (`dist/universal/`, `dist/ouroboros/`), **NEVER the reverse**. This prevents lost work, file corruption, and hours of debugging from copying stale distribution files back into the live dev environment.

**Core Principle:** `.praxis-os/` is the source of truth during development. Distribution artifacts are read-only snapshots copied UP when ready to ship.

---

## ❌ The Problem

**Without this standard:**
- ✗ Agents copy stale distribution files → `.praxis-os/` (overwrites live dev work)
- ✗ Hours of work lost (yesterday's nested config incident)
- ✗ Confusion about "which file is the real one?"
- ✗ File corruption from mixing old and new code
- ✗ Debugging loops trying to figure out why changes disappeared

**Real incident (2025-11-03):**
Agent confusion about file locations led to copying `universal/config/index_config.yaml` (stale flat structure from Oct) → `.praxis-os/config/index_config.yaml` (current nested structure from Nov 2), **losing hours of work** on the correct config design.

---

## 📋 The Standard

### Rule 1: ALL Development in `.praxis-os/`

**The dev environment is:**
```
.praxis-os/
├── config/                    ← Config files (active, live)
│   └── mcp.yaml
├── ouroboros/                 ← MCP server code (active, running)
│   ├── __main__.py
│   ├── subsystems/
│   │   ├── rag/
│   │   │   ├── standards/
│   │   │   ├── code/
│   │   │   └── index_manager.py
│   │   └── workflow/
│   └── tools/
├── standards/                 ← Standards (active, indexed)
│   ├── development/
│   │   └── this-file.md      ← You are here!
│   └── universal/
└── venv/                      ← Virtual environment (isolated)
```

**What this means:**
- ✅ ALL code edits happen in `.praxis-os/`
- ✅ ALL config changes happen in `.praxis-os/`
- ✅ ALL testing happens in `.praxis-os/`
- ✅ The MCP server **RUNS** from `.praxis-os/`
- ✅ Standards are **INDEXED** from `.praxis-os/`
- ✅ This is the **LIVE, ACTIVE CODE**

### Rule 2: Distribution Artifacts are READ-ONLY (Until "Ship It")

**Distribution artifacts are:**
```
universal/                     ← 🔵 STALE until shipped
├── config/
│   └── index_config.yaml     ← May be outdated
├── standards/                ← Skeleton files
└── templates/                ← Skeleton files

mcp_server/                    ← 🔵 STALE until shipped
├── __main__.py               ← May not exist yet
├── server/
│   ├── indexes/              ← May not exist yet
│   └── tools/
└── ...
```

**What this means:**
- ❌ DO NOT edit files here during development
- ❌ DO NOT copy files from here to `.praxis-os/`
- ❌ These files are STALE (may be weeks/months old)
- ✅ These are templates/skeletons for new installs
- ✅ Only updated when explicitly told to "ship it"

### Rule 3: One-Way Flow (Dev → Distribution)

**The workflow:**
```
┌─────────────────────────────────────────────────────┐
│  Phase 1: Development (Days/Weeks)                  │
│  ─────────────────────────────────────────────────  │
│                                                      │
│  .praxis-os/                                        │
│  └── [ALL WORK HAPPENS HERE]                        │
│      ✅ Edit code                                    │
│      ✅ Test changes                                 │
│      ✅ Iterate rapidly                              │
│      ✅ Run MCP server                               │
│                                                      │
│  universal/, mcp_server/                            │
│  └── [IGNORED - May be stale]                       │
│                                                      │
└─────────────────────────────────────────────────────┘
                       ↓
         🛑 Wait for "ship it" 🛑
                       ↓
┌─────────────────────────────────────────────────────┐
│  Phase 2: Shipping (Minutes)                        │
│  ─────────────────────────────────────────────────  │
│                                                      │
│  User says: "ship it" or "copy up to distribution"  │
│                                                      │
│  .praxis-os/ ──────────────────→ universal/         │
│              ONE-WAY COPY        mcp_server/        │
│                                                      │
│  Distribution artifacts now CURRENT                  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**KEY INSIGHT:** This is a **publishing** workflow, not a **synchronization** workflow. Dev is active, distribution is published snapshots.

### Rule 4: Explicit "Ship It" Required

**DO NOT copy to distribution unless:**
- ✅ User explicitly says "ship it"
- ✅ User explicitly says "copy up to distribution"
- ✅ User explicitly says "update universal/ or mcp_server/"
- ✅ User explicitly says "ready to ship"

**Implicit signals that DO NOT mean ship:**
- ❌ "This looks good"
- ❌ "Feature is complete"
- ❌ "Tests pass"
- ❌ User moves to next task
- ❌ User asks to commit changes

**Why:** Dev environment may be in flux, user may want more testing, or may not be ready for distribution yet.

---

## ✅ Validation Checklist

**Before making ANY file change, verify:**
- [ ] Am I working in `.praxis-os/`? (If no, STOP)
- [ ] Is this the dev environment? (Check for `venv/`, active code)
- [ ] Am I about to copy distribution → dev? (If yes, STOP)
- [ ] Did user say "ship it" or equivalent? (If no, don't copy to distribution)

**Before copying to distribution:**
- [ ] User explicitly said "ship it" or "copy up"?
- [ ] All tests pass in `.praxis-os/`?
- [ ] Feature is validated and working?
- [ ] I'm copying FROM `.praxis-os/` TO distribution (correct direction)?

---

## 📚 Examples

### ✅ Example 1: Correct Workflow (Fix a Bug)

**Scenario:** Fix FTS corruption bug in `standards_index.py`

```bash
# 1. Edit in dev environment
vim .praxis-os/mcp_server/server/indexes/standards_index.py
# [Add FTS rebuild logic]

# 2. Test in dev environment
cd .praxis-os
python evaluation/scripts/evaluate_search.py
# ✅ Tests pass, bug fixed

# 3. Wait for user signal
# User: "Great! Ship it when ready."

# 4. Copy UP to distribution
cp .praxis-os/mcp_server/server/indexes/standards_index.py \
   mcp_server/server/indexes/standards_index.py
```

**Result:** ✅ Bug fixed, distribution updated, no lost work

### ✅ Example 2: Correct Workflow (Update Config)

**Scenario:** Add nested structure to `index_config.yaml`

```bash
# 1. Edit in dev environment
vim .praxis-os/config/index_config.yaml
# [Convert flat structure → nested structure]

# 2. Test in dev environment
# Restart MCP server, run queries
# ✅ Config works, indexes build correctly

# 3. Wait for user signal
# User: "This is perfect! Copy up to universal/"

# 4. Copy UP to distribution
cp .praxis-os/config/index_config.yaml \
   universal/config/index_config.yaml
```

**Result:** ✅ Config updated, distribution current, no lost work

### ❌ Example 3: WRONG - Copying Distribution to Dev

**Scenario:** Agent sees "duplicate" config files, tries to "sync" them

```bash
# ❌ WRONG - Agent sees stale distribution file
ls universal/config/index_config.yaml
# (File from Oct 15, flat structure)

# ❌ WRONG - Agent thinks it should "update" dev
cp universal/config/index_config.yaml \
   .praxis-os/config/index_config.yaml

# ❌ WRONG - Overwrites current dev work (Nov 3 nested structure)
# ✗ HOURS OF WORK LOST
```

**Result:** ✗ Dev work destroyed, hours lost debugging, file corruption

### ❌ Example 4: WRONG - Premature Shipping

**Scenario:** Feature works in dev, agent copies to distribution without being told

```bash
# ✅ Feature works in dev
.praxis-os/mcp_server/server/tools/new_tool.py

# ❌ WRONG - Agent copies to distribution WITHOUT "ship it" signal
cp .praxis-os/mcp_server/server/tools/new_tool.py \
   mcp_server/server/tools/new_tool.py

# User: "Wait, I wanted to test this more!"
# Now distribution has half-baked feature
```

**Result:** ✗ Premature shipping, user loses control, distribution polluted

---

## 🚫 Anti-Patterns

### Anti-Pattern 1: "Synchronizing" Files

**DON'T DO THIS:**
```bash
# Agent sees two versions of same file
.praxis-os/config/index_config.yaml    # Current (Nov 3)
universal/config/index_config.yaml     # Stale (Oct 15)

# Agent thinks: "These should match, let me sync them"
# Agent copies WRONG DIRECTION → destroys current work
```

**WHY IT'S WRONG:** These files are NOT meant to stay in sync during development. Distribution is a published snapshot, not a mirror.

### Anti-Pattern 2: "Cleaning Up" Duplicates

**DON'T DO THIS:**
```bash
# Agent thinks: "Two copies of same file is messy"
# Agent deletes .praxis-os/ version to "clean up"
# Agent keeps universal/ version (stale)
```

**WHY IT'S WRONG:** `.praxis-os/` is the LIVE CODE. Distribution is the backup/template.

### Anti-Pattern 3: "Updating" Dev from Distribution

**DON'T DO THIS:**
```bash
# Agent thinks: "Distribution has newer timestamp, must be current"
# Agent copies distribution → dev
```

**WHY IT'S WRONG:** Timestamps don't indicate which is current. `.praxis-os/` is ALWAYS current during development.

### Anti-Pattern 4: "Helpful" Auto-Shipping

**DON'T DO THIS:**
```bash
# Agent thinks: "Feature is done, I'll helpfully ship it"
# Agent copies to distribution without being told
```

**WHY IT'S WRONG:** Only user knows when feature is ready. Agent cannot infer shipping readiness.

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **About to edit a file** | `pos_search_project(content_type="standards", query="where should I make changes in praxis-os")` |
| **See duplicate files** | `pos_search_project(content_type="standards", query="why are there two versions of the same file")` |
| **About to copy files** | `pos_search_project(content_type="standards", query="dev vs distribution workflow copy direction")` |
| **Lost work incident** | `pos_search_project(content_type="standards", query="why did my changes disappear")` |
| **User says 'ship it'** | `pos_search_project(content_type="standards", query="how to copy dev to distribution")` |
| **Confused about locations** | `pos_search_project(content_type="standards", query="what is .praxis-os directory")` |

---

## 🔗 Related Standards

- `mcp-rag-configuration.md` - RAG indexing from `.praxis-os/standards/`
- `agent-os-architecture.md` - Overall system design
- `rag-content-authoring.md` - How to structure this standard for discoverability

---

## 🧪 Testing Discoverability

**Verify this standard is discoverable:**

```python
# Query 1: Location confusion
pos_search_project(content_type="standards", query="where do I make code changes")
# Expected: This standard in top 3

# Query 2: Copy direction
pos_search_project(content_type="standards", query="copy files to distribution or from distribution")
# Expected: This standard in top 3

# Query 3: Lost work
pos_search_project(content_type="standards", query="why did I lose my changes")
# Expected: This standard in top 3

# Query 4: Duplicate files
pos_search_project(content_type="standards", query="two versions of same file praxis os")
# Expected: This standard in top 3
```

---

## 📊 Behavioral Impact

**Before this standard:**
- ✗ Agent confusion about file locations → copies wrong direction
- ✗ 4+ hours lost work (2025-11-02 evening incident)
- ✗ File corruption, debugging loops, user frustration

**After this standard:**
- ✅ Clear mental model: `.praxis-os/` = dev, everything else = distribution
- ✅ Query before copying: "where should I make changes?"
- ✅ Zero lost work from wrong-direction copies
- ✅ User controls shipping timing explicitly

---

## 🎓 Key Takeaways

1. **`.praxis-os/` is the ONE TRUE SOURCE during development**
2. **Distribution artifacts are read-only until "ship it"**
3. **Flow is ALWAYS dev → distribution, NEVER reversed**
4. **Wait for explicit "ship it" signal before copying**
5. **Query this standard when unsure about file locations**

---

**Version:** 1.0.0  
**Created:** 2025-11-03  
**Last Updated:** 2025-11-03  
**Status:** 🔴 CRITICAL - Read before making ANY file changes  
**Next Review:** After first month of zero lost-work incidents

