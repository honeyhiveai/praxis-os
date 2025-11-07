# Step 4: Customize MCP Configuration

**Previous**: `03-agent-configuration.md` (routed to agent-specific guide)  
**Current**: Customizing `mcp.yaml` for your project  
**Next**: `05-gitignore.md`

---

## 🎯 What This Step Does

Customize the `mcp.yaml` configuration file to match your project's source code structure. This ensures code indexing works correctly when the RAG index is built.

**Why this matters**: The config file has template paths (`ouroboros/`) that won't match your project. You MUST update code indexing paths to point to your actual source code directories.

**Time**: ~2-3 minutes (inspect project structure + edit config)

---

## ⚠️ CRITICAL: Must Customize Before Index Build

**What happens if you skip this**:
- Code indexing won't work (searches will return empty)
- RAG index will build but only index standards (not your code)
- You'll have to rebuild the index later after fixing config

**What you're customizing**:
- Code source paths (where your source code lives)
- Languages (which programming languages you use)
- AST paths (should match code paths)

**What you're NOT customizing** (usually fine as-is):
- Standards paths (usually `standards/` is correct)
- Chunk sizes, models, etc. (sane defaults)

---

## 📋 Step 4.1: Locate Config File

The config file was copied in step 02:

```python
import os

config_path = ".praxis-os/config/mcp.yaml"

if not os.path.exists(config_path):
    print(f"❌ Config file not found: {config_path}")
    print("   Did you complete step 02 (copy-files)?")
    exit(1)

print(f"✅ Found config file: {config_path}")
```

---

## 🔍 Step 4.2: Inspect Your Project Structure

Before editing, you need to know where your source code lives. Common patterns:

```python
import os

# Check common source code locations
possible_paths = [
    "src/",
    "lib/",
    "app/",
    "components/",
    "packages/",
    "cmd/",  # Go
    "pkg/",  # Go
    "internal/",  # Go
]

print("🔍 Inspecting project structure...")
print(f"   Current directory: {os.getcwd()}")

found_paths = []
for path in possible_paths:
    if os.path.exists(path):
        found_paths.append(path)
        print(f"   ✅ Found: {path}/")

if not found_paths:
    print("   ⚠️  No standard source directories found")
    print("   Your code might be at project root (check for .py, .js, .ts files)")
    print("   Or you might have a non-standard structure")
else:
    print(f"\n   📁 Source code appears to be in: {', '.join(found_paths)}")
```

**Common Project Patterns**:

| Language | Typical Paths |
|----------|--------------|
| **Python** | `src/`, `lib/`, or root-level `.py` files |
| **JavaScript/TypeScript** | `src/`, `app/`, `components/` |
| **Go** | `cmd/`, `pkg/`, `internal/` |
| **Rust** | `src/` |
| **Monorepo** | `packages/*/src/`, `apps/*/src/` |

---

## ✏️ Step 4.3: Edit Config File

Open `.praxis-os/config/mcp.yaml` and update these sections:

### Section 1: Code Index Source Paths

**Find this section** (around line 120):
```yaml
code:
  source_paths:
    # ⚠️ CHANGE THIS: Replace with your project's source code paths
    - "ouroboros/"  # ⚠️ TEMPLATE: Replace this!
```

**Update it** based on your project structure:

**Example 1: Python project with `src/` directory**
```yaml
code:
  source_paths:
    - "../src/"  # Relative to .praxis-os/ directory
```

**Example 2: JavaScript project with multiple directories**
```yaml
code:
  source_paths:
    - "../src/"
    - "../app/"
    - "../components/"
```

**Example 3: Go project**
```yaml
code:
  source_paths:
    - "../cmd/"
    - "../pkg/"
    - "../internal/"
```

**Example 4: Root-level Python files**
```yaml
code:
  source_paths:
    - "../"  # Index entire project root
```

**⚠️ Path Resolution**:
- Paths are relative to `.praxis-os/` directory (not project root)
- Use `../` to go up one level to project root
- Example: If code is at `project-root/src/`, use `../src/`

### Section 2: Code Languages

**Find this section** (around line 136):
```yaml
languages:
  # ⚠️ UPDATE THIS: Add languages your project uses
  - "python"  # ⚠️ TEMPLATE: Add your languages here
```

**Update it** with your languages:

**Example 1: Python only**
```yaml
languages:
  - "python"
```

**Example 2: TypeScript + Python**
```yaml
languages:
  - "typescript"
  - "python"
```

**Example 3: Multi-language**
```yaml
languages:
  - "python"
  - "typescript"
  - "go"
```

**Supported languages**: `python`, `javascript`, `typescript`, `go`, `rust`

### Section 3: AST Index Paths (Should Match Code Paths)

**Find this section** (around line 175):
```yaml
ast:
  source_paths:
    # ⚠️ CHANGE THIS: Should match code.source_paths above
    - "ouroboros/"  # ⚠️ TEMPLATE: Replace this!
```

**Update it** to match your code paths:

**Example**:
```yaml
ast:
  source_paths:
    - "../src/"  # Should match code.source_paths
```

**Also update languages** (around line 181):
```yaml
languages:
  # ⚠️ UPDATE THIS: Should match code.languages above
  - "python"  # ⚠️ TEMPLATE: Add your languages here
```

---

## ✅ Validation Checkpoint #4

Verify your config changes:

```python
import yaml
import os

config_path = ".praxis-os/config/mcp.yaml"

# Read config
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Check code paths
code_paths = config["indexes"]["code"]["source_paths"]
print(f"✅ Code source paths: {code_paths}")

# Verify paths don't contain template values
if "ouroboros/" in code_paths:
    print("⚠️  WARNING: Config still contains template path 'ouroboros/'")
    print("   Did you update code.source_paths?")
else:
    print("✅ Code paths customized (no template values)")

# Check languages
languages = config["indexes"]["code"]["languages"]
print(f"✅ Languages: {languages}")

# Check AST paths match code paths
ast_paths = config["indexes"]["ast"]["source_paths"]
if ast_paths == code_paths:
    print("✅ AST paths match code paths")
else:
    print("⚠️  WARNING: AST paths don't match code paths")
    print(f"   Code: {code_paths}")
    print(f"   AST: {ast_paths}")
    print("   Consider updating AST paths to match")
```

---

## 🚨 Troubleshooting

### Issue: "I don't know where my source code is"

**Solution**: Check for common file patterns:

```python
import os
import glob

# Check for Python files
py_files = glob.glob("**/*.py", recursive=True)
if py_files:
    print(f"Found {len(py_files)} Python files")
    # Show first few directories
    dirs = set(os.path.dirname(f) for f in py_files[:10])
    print(f"Directories: {dirs}")

# Check for TypeScript/JavaScript files
ts_files = glob.glob("**/*.ts", recursive=True)
js_files = glob.glob("**/*.js", recursive=True)
if ts_files or js_files:
    print(f"Found {len(ts_files)} TS files, {len(js_files)} JS files")
```

### Issue: "Paths are relative to .praxis-os/ - I'm confused"

**Explanation**:
- `.praxis-os/config/mcp.yaml` is inside `.praxis-os/` directory
- Paths in config are relative to `.praxis-os/` (where config file lives)
- To reach project root, use `../` (go up one level)

**Example**:
```
project-root/
├── src/              ← Your code is here
└── .praxis-os/
    └── config/
        └── mcp.yaml  ← Config file is here
```

To index `src/` from config, use `../src/` (up from `.praxis-os/` to project root, then into `src/`)

### Issue: "I have a monorepo with multiple packages"

**Solution**: Use glob patterns or list multiple paths:

```yaml
code:
  source_paths:
    - "../packages/package-a/src/"
    - "../packages/package-b/src/"
    - "../apps/app-a/src/"
```

Or if all packages follow same structure:
```yaml
code:
  source_paths:
    - "../packages/*/src/"  # Index all packages
```

**Note**: Check if your config loader supports glob patterns. If not, list paths explicitly.

### Issue: "Config file has syntax errors after editing"

**Solution**: Validate YAML syntax:

```python
import yaml

try:
    with open(".praxis-os/config/mcp.yaml", "r") as f:
        yaml.safe_load(f)
    print("✅ YAML syntax is valid")
except yaml.YAMLError as e:
    print(f"❌ YAML syntax error: {e}")
    print("   Check indentation and quotes")
```

---

## 📊 Progress Check

At this point you should have:
- ✅ Config file located (`.praxis-os/config/mcp.yaml`)
- ✅ Code source paths updated (no `ouroboros/` template)
- ✅ Languages updated (matches your project)
- ✅ AST paths updated (matches code paths)
- ✅ YAML syntax validated

**If anything above is ❌, stop and fix before continuing.**

---

## 🎯 What's Next

You've customized the config for your project. Now you need to:
1. Configure `.gitignore` (prevent committing 2.6GB of ephemeral files)
2. Create Python venv and install dependencies
3. Build RAG index (will use your customized config)

**Next step**: Configure `.gitignore` to prevent committing cache files.

---

## ➡️ NEXT STEP

**Read file**: `installation/05-gitignore.md`

That file will:
1. Read gitignore requirements from standards
2. Append prAxIs OS entries to your `.gitignore`
3. Verify gitignore is working correctly
4. Direct you to step 06 (venv and mcp setup)

---

**Status**: Step 4 Complete ✅  
**Customized**: `mcp.yaml` config file  
**Next File**: `05-gitignore.md`  
**Step**: 4 of 7

