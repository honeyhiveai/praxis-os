# Step 04: Configure .gitignore

**Estimated Time:** 2 minutes  
**Critical Risk:** Without proper .gitignore, you'll commit 1.3GB+ of ephemeral files

---

## 🎯 Objective

Add prAxIs OS entries to your project's `.gitignore` to prevent committing ~2.7GB of ephemeral files.

**📖 Canonical Source**: `.praxis-os/standards/universal/installation/gitignore-requirements.md`

---

## ⚠️ Why This Matters

**Without proper .gitignore:**
- ❌ Every commit includes 2.6GB+ of binary data
- ❌ Upgrade backups bloat your repo permanently
- ❌ Vector index conflicts across machines
- ❌ GitHub will reject pushes over file size limits

**With proper .gitignore:**
- ✅ Only track meaningful prAxIs OS content
- ✅ Ephemeral files stay local
- ✅ Clean, portable repository

---

## Read Requirements from Standards

The required .gitignore entries are defined in the standards you just copied:

```python
import re

# Read canonical requirements from standards
standards_file = ".praxis-os/standards/universal/installation/gitignore-requirements.md"

with open(standards_file, "r") as f:
    content = f.read()

# Extract the code block with required entries
match = re.search(r'```gitignore\n(.*?)\n```', content, re.DOTALL)

if not match:
    print("❌ Could not parse standards file")
    exit(1)

required_section = match.group(1)
print("✅ Loaded requirements from standards")
print(f"\nRequired entries:\n{required_section}")
```

---

## Installation Script

### Check if .gitignore Exists

```python
import os

# Check for .gitignore
if not os.path.exists(".gitignore"):
    print("⚠️  No .gitignore found")
    create_new = input("Create .gitignore? (yes/no): ").strip().lower()
    
    if create_new == "yes":
        with open(".gitignore", "w") as f:
            f.write("# Created for prAxIs OS installation\n")
        print("✅ Created .gitignore")
    else:
        print("❌ Installation cannot proceed without .gitignore")
        exit(1)
else:
    print("✅ .gitignore exists")
```

---

### Parse and Extract Patterns

```python
# Parse patterns from the standards section
lines = required_section.split("\n")
required_patterns = []
header_line = None

for line in lines:
    stripped = line.strip()
    if stripped.startswith("#"):
        if "prAxIs OS" in stripped:
            header_line = stripped
    elif stripped:  # Non-empty, non-comment
        required_patterns.append(stripped)

print(f"✅ Found {len(required_patterns)} required patterns")
```

---

### Check Existing .gitignore

```python
import os

# Read or create .gitignore
if not os.path.exists(".gitignore"):
    print("⚠️  No .gitignore found, creating...")
    with open(".gitignore", "w") as f:
        f.write("# Created for prAxIs OS installation\n")
    current_content = ""
else:
    with open(".gitignore", "r") as f:
        current_content = f.read()
    print("✅ .gitignore exists")
```

---

### Determine Missing Entries

```python
# Check what's missing
missing = [p for p in required_patterns if p not in current_content]

if not missing:
    print("✅ All prAxIs OS entries already present")
else:
    print(f"⚠️  Missing {len(missing)} entries:")
    for p in missing:
        print(f"   {p}")
```

---

### Append Missing Entries

```python
if missing:
    with open(".gitignore", "a") as f:
        # Ensure proper spacing
        if not current_content.endswith("\n\n"):
            if not current_content.endswith("\n"):
                f.write("\n")
            f.write("\n")
        
        # Add header if this is first prAxIs OS section
        if "# prAxIs OS" not in current_content and header_line:
            f.write(f"{header_line}\n")
        
        # Add missing entries
        for entry in missing:
            f.write(f"{entry}\n")
    
    print(f"✅ Added {len(missing)} entries to .gitignore")
```

---

### Verification

```python
import subprocess

# Verify gitignore is working
def verify_gitignore():
    """Check that ephemeral files are being ignored"""
    
    # Check if git is available
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Git not available, skipping verification")
        return True
    
    # Check if we're in a git repo
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("ℹ️  Not a git repository, skipping verification")
        return True
    
    # Check if .praxis-os/.cache/ would be ignored
    result = subprocess.run(
        ["git", "check-ignore", ".praxis-os/.cache/test"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ .gitignore verification: .praxis-os/.cache/ is ignored")
    else:
        print("❌ WARNING: .praxis-os/.cache/ is NOT being ignored!")
        print("   Check your .gitignore file")
        return False
    
    # Check if backup directory would be ignored
    result = subprocess.run(
        ["git", "check-ignore", ".praxis-os.backup.test"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ .gitignore verification: .praxis-os.backup.* is ignored")
    else:
        print("❌ WARNING: .praxis-os.backup.* is NOT being ignored!")
        print("   Check your .gitignore file")
        return False
    
    return True

# Run verification
if not verify_gitignore():
    print("\n⚠️  .gitignore verification failed!")
    print("Review your .gitignore file before continuing")
    exit(1)
```

---

## What Gets Tracked vs Ignored

### ✅ TRACKED (Committed to Git)
```
.praxis-os/standards/        # Universal CS fundamentals + your standards
.praxis-os/usage/            # Documentation + your custom docs
.praxis-os/workflows/        # Workflow definitions
.praxis-os/specs/            # YOUR project specifications (important!)
.praxis-os/mcp_server/       # MCP server code (if customized)
.cursor/mcp.json            # Cursor MCP configuration
.cursorrules                # AI assistant behavioral triggers
```

### ❌ IGNORED (Not Committed)
```
.praxis-os/.cache/           # 1.3GB vector index (regenerated)
.praxis-os/venv/             # Python packages (reinstalled)
.praxis-os.backup.*          # 1.3GB upgrade backups (temporary)
.praxis-os/.upgrade_lock     # Upgrade lock file
__pycache__/                # Python bytecode
```

---

## Completion Checklist

Before proceeding to step 05:

- [ ] `.gitignore` file exists ✅/❌
- [ ] prAxIs OS entries added ✅/❌
- [ ] `.praxis-os/.cache/` is ignored (verified) ✅/❌
- [ ] `.praxis-os.backup.*` is ignored (verified) ✅/❌
- [ ] No warnings from verification ✅/❌

---

## Troubleshooting

### Problem: "Git check-ignore says files are not ignored"

**Cause:** `.gitignore` entries may have incorrect format or placement

**Fix:**
```bash
# Test if pattern works
git check-ignore -v .praxis-os/.cache/test

# Should output:
# .gitignore:2:.praxis-os/.cache/  .praxis-os/.cache/test
```

---

### Problem: "Files were already committed before adding .gitignore"

**Cause:** If you've already committed ephemeral files, they'll stay in git history

**Fix:**
```bash
# Remove from git but keep locally
git rm -r --cached .praxis-os/.cache/
git rm -r --cached .praxis-os/venv/
git rm --cached .praxis-os.backup.*

# Commit the removal
git commit -m "chore: remove ephemeral prAxIs OS files from git"
```

---

### Problem: "Backup directories keep appearing in git status"

**Cause:** Pattern `.praxis-os.backup.*` might not match correctly

**Fix:**
```bash
# Test the pattern
ls -d .praxis-os.backup.* 2>/dev/null
git check-ignore .praxis-os.backup.20251008_193031

# If not ignored, check .gitignore has:
.praxis-os.backup.*
# NOT: .praxis-os.backup*/ (wrong!)
```

---

## Next Step

🎯 **NEXT-MANDATORY:** [05-venv-mcp.md](05-venv-mcp.md)

After `.gitignore` is configured, you'll create the Python virtual environment and configure the MCP server.

