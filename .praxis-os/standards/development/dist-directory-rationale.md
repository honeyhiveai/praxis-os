# The `dist/` Directory - Distribution Artifacts Build Pattern

**Purpose:** Explain why praxis-os uses `dist/` for distribution artifacts and how `sync-to-dist.sh` works as the "build" process

**Audience:** praxis-os framework developers, contributors

**Status:** Active - Canonical distribution structure

**Keywords:** dist directory, distribution artifacts, build process, sync-to-dist, why dist, packaging model, build output, consumer installs, skeleton files versus live code

---

## 🎯 TL;DR - Why `dist/`?

**`dist/` is the standard software convention for "distribution artifacts" - what gets shipped to users.**

```
praxis-os/
├── dist/                    # 📦 BUILD OUTPUT (what users install)
│   ├── ouroboros/          # Built server code
│   ├── universal/          # Built standards + workflows
│   ├── config/             # Built config templates
│   └── scripts/            # Built helper scripts
│
├── scripts/                # 🛠️ REPOSITORY TOOLING
│   ├── install-praxis-os.py     # Installs from dist/
│   └── sync-to-dist.sh          # "BUILD" = sync to dist/
│
└── .praxis-os/             # 🔨 LIVE DEVELOPMENT
    ├── ouroboros/          # ← EDIT HERE
    ├── standards/          # ← EDIT HERE
    └── workflows/          # ← EDIT HERE
```

**Mental model:** `dist/` = "ready to ship to users" (like Python's `dist/`, Node's `dist/`, Rust's `target/`)

---

## 📦 What Is `dist/`?

**`dist/` = "distribution"** - The standard directory name for build artifacts in software projects.

### Industry Standard Examples:

**Python:**
```bash
python setup.py sdist    # Creates dist/my-package-1.0.tar.gz
python setup.py bdist    # Creates dist/my-package-1.0.whl
```

**Node.js:**
```bash
npm run build            # Creates dist/bundle.js
npm pack                 # Creates dist/package-1.0.0.tgz
```

**Rust:**
```bash
cargo build              # Creates target/debug/ (Rust's "dist")
cargo build --release    # Creates target/release/ (production builds)
```

**Go:**
```bash
go build -o dist/        # Explicit dist/ output
```

---

## 🎯 Why praxis-os Chose `dist/`

### **Reason 1: Clear Visual Separation**

```
dist/                    # ❌ DON'T EDIT (build artifacts)
.praxis-os/              # ✅ EDIT HERE (live development)
```

**Benefits:**
- ✅ Impossible to confuse "what to edit" with "what ships"
- ✅ `dist/` screams "I'm a build artifact!"
- ✅ Prevents accidental editing of stale distribution files

---

### **Reason 2: Standard Software Convention**

Developers immediately understand: **`dist/` = distribution artifacts**

**No explanation needed:**
- Python dev sees `dist/` → knows it's build output
- Node dev sees `dist/` → knows it's packaged code
- Rust dev sees `target/` → same concept, different name

**Consistency with industry = lower cognitive load**

---

### **Reason 3: Enforces Dogfooding**

By using `dist/` (not `src/` or `lib/`), we make it clear:

```
❌ WRONG: Edit in dist/ (stale, for shipping only)
✅ RIGHT: Edit in .praxis-os/ (live, consumer environment)
```

**Forces the correct development workflow:**
1. Edit in `.praxis-os/` (where users run code)
2. Test in `.praxis-os/` (actual runtime environment)
3. Sync to `dist/` when ready to ship (`./scripts/sync-to-dist.sh`)

---

### **Reason 4: Makes "Build" Process Obvious**

**The "build" = `./scripts/sync-to-dist.sh`**

```bash
# Development cycle:
vim .praxis-os/ouroboros/server.py    # 1. Edit live code
# Test immediately (MCP restart)       # 2. Validate locally

# When ready to ship:
./scripts/sync-to-dist.sh --sync      # 3. "BUILD" = sync to dist/

# QA validation:
python scripts/install-praxis-os.py   # 4. Test distribution
```

**Clear separation:**
- `.praxis-os/` = source of truth (development)
- `dist/` = build output (distribution)
- `scripts/sync-to-dist.sh` = build process

---

## 🔧 How `sync-to-dist.sh` Works

**The "Build" Process:**

```bash
#!/bin/bash
# sync-to-dist.sh: Copy local development → dist/ build artifacts

# What gets synced:
✅ .praxis-os/ouroboros/ → dist/ouroboros/
✅ .praxis-os/standards/universal/ → dist/universal/standards/
✅ .praxis-os/workflows/ → dist/universal/workflows/

# What gets excluded:
❌ __pycache__, *.pyc (Python bytecode)
❌ state/, .cache/ (runtime files)
❌ .praxis-os/standards/development/ (praxis-os internal docs)
```

**Usage:**

```bash
# Preview what will change (dry-run):
./scripts/sync-to-dist.sh

# Actually sync files:
./scripts/sync-to-dist.sh --sync
```

**Features:**
- ✅ Dry-run by default (preview changes)
- ✅ Uses `rsync --delete` (clean, accurate sync)
- ✅ Excludes ephemeral files automatically
- ✅ Color-coded output for clarity

---

## 📋 Directory Ownership Model

| Directory | Owner | Purpose | Edit? |
|-----------|-------|---------|-------|
| `.praxis-os/ouroboros/` | **Development** | Live server code | ✅ EDIT HERE |
| `.praxis-os/standards/universal/` | **Development** | Live standards | ✅ EDIT HERE |
| `.praxis-os/workflows/` | **Development** | Live workflows | ✅ EDIT HERE |
| `.praxis-os/standards/development/` | **praxis-os Only** | Internal docs | ✅ EDIT HERE (never synced) |
| `dist/ouroboros/` | **Distribution** | Build artifact | ❌ READ ONLY |
| `dist/universal/` | **Distribution** | Build artifact | ❌ READ ONLY |
| `scripts/` | **Repository** | Tooling | Manual copy if needed |

---

## 🔄 Development Workflow

### **Standard Development Cycle:**

```bash
# 1. Edit in live environment
vim .praxis-os/ouroboros/subsystems/rag/index_manager.py

# 2. Test immediately (no rebuild needed)
# Cursor → Cmd+Shift+P → "MCP: Restart Server"
# Test with queries/tools

# 3. Iterate rapidly
# Edit → restart → test → edit (seconds, not minutes)

# 4. When ready to ship, sync to dist/
./scripts/sync-to-dist.sh --sync

# 5. QA validation (reinstall tests distribution)
python scripts/install-praxis-os.py
# Verify installation works correctly
```

**Benefits:**
- ✅ Fast iteration (edit → test, no build step)
- ✅ Test in consumer environment (actual runtime paths)
- ✅ Explicit "ship it" step (sync-to-dist)
- ✅ QA validation (reinstall from dist/)

---

## 🚨 Common Mistakes (Prevented by `dist/`)

### **Mistake 1: Editing Distribution Files**

```bash
# ❌ WRONG: Edit build artifacts
vim dist/ouroboros/server.py
# → File watcher won't detect change
# → Not tested in runtime environment
# → Lost on next sync-to-dist
```

```bash
# ✅ RIGHT: Edit live code
vim .praxis-os/ouroboros/server.py
# → File watcher rebuilds indexes
# → Tested in runtime environment
# → Synced to dist/ when ready
```

---

### **Mistake 2: Copying Stale Dist Files → Live**

```bash
# ❌ WRONG: Copy old dist/ → live .praxis-os/
cp dist/ouroboros/server.py .praxis-os/ouroboros/
# → Overwrites your live work with stale build artifact
# → Hours of work lost!
```

```bash
# ✅ RIGHT: One-way sync (live → dist)
./scripts/sync-to-dist.sh --sync
# → Copies latest live code → dist/
# → Preserves your work
```

---

### **Mistake 3: Forgetting to Sync Before Release**

```bash
# ❌ WRONG: Commit without syncing
git add dist/
git commit -m "Update server"
# → dist/ has stale code
# → Users install old version
```

```bash
# ✅ RIGHT: Sync first, then commit
./scripts/sync-to-dist.sh --sync  # Update dist/
git add .praxis-os/ dist/
git commit -m "Update server (synced to dist)"
# → dist/ has latest code
# → Users install current version
```

---

## 📚 Comparison: Before vs After `dist/`

### **Before (Flat Structure):**

```
praxis-os/
├── universal/          # Confusing: source or dist?
├── mcp_server/         # Confusing: edit here or .praxis-os/?
└── .praxis-os/         # Live code
```

**Problems:**
- ❌ Unclear what to edit vs what ships
- ❌ Easy to edit wrong location
- ❌ No clear "build" concept

---

### **After (`dist/` Structure):**

```
praxis-os/
├── dist/               # Clear: distribution artifacts
│   ├── ouroboros/      # Clear: build output
│   └── universal/      # Clear: packaged files
├── scripts/            # Clear: tooling
│   └── sync-to-dist.sh # Clear: "build" process
└── .praxis-os/         # Clear: live development
```

**Benefits:**
- ✅ Crystal clear: edit `.praxis-os/`, ship `dist/`
- ✅ Industry standard pattern
- ✅ Explicit build process (`sync-to-dist.sh`)

---

## 🔍 Questions This Answers

**"Why is there a `dist/` directory?"**
→ Standard software convention for distribution artifacts (what ships to users)

**"Should I edit files in `dist/`?"**
→ NO! `dist/` is build output, read-only. Edit in `.praxis-os/` instead.

**"How do I update `dist/`?"**
→ Run `./scripts/sync-to-dist.sh --sync` (the "build" process)

**"Why not just edit `dist/` directly?"**
→ Doesn't test consumer environment, loses changes on next sync, breaks dogfooding

**"What's the difference between `dist/` and `.praxis-os/`?"**
→ `.praxis-os/` = live development (edit here), `dist/` = packaged files (ships to users)

**"Is this standard in other projects?"**
→ YES! Python, Node, Rust, Go all use similar patterns (dist/, build/, target/)

**"When do I sync to dist/?"**
→ When ready to ship changes to users (validated locally first)

**"Can I skip the sync step?"**
→ For local development, yes. But must sync before committing/releasing.

---

## Related Standards

**Development workflow (file locations):**
- `dogfooding-model.md` - Where to edit files during development
- `dev-vs-distribution-workflow.md` - One-way copy-up workflow

**Repository structure (organization):**
- `praxis-os-architecture.md` - Overall project layout
- `local-dev-scripts.md` - Helper scripts organization

---

**Remember:** `dist/` = "distribution artifacts" (industry standard). Edit in `.praxis-os/`, sync to `dist/` when shipping (`./scripts/sync-to-dist.sh --sync`).

