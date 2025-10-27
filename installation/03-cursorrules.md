# Step 3: Handle .cursorrules File

**Previous**: `02-copy-files.md` (copied content files)  
**Current**: Safely handling .cursorrules (don't overwrite!)  
**Next**: `04-venv-mcp.md`

---

## 🎯 What This Step Does

Copy or merge the `.cursorrules` file to configure Cursor's AI behavior.

**Why this step is special**: Unlike other files, `.cursorrules` might already exist in the target project with important user configurations. We MUST NOT blindly overwrite it.

**Time**: ~1-2 minutes (or more if manual merge needed)

---

## ⚠️ CRITICAL: Never Blindly Overwrite

**The Problem**:
- Many projects already have `.cursorrules` with custom AI configurations
- Blindly overwriting destroys the user's existing setup
- This breaks their existing Cursor workflows
- **This is a safety issue** - never destroy user's work!

**The Solution**:
1. Check if `.cursorrules` exists
2. If NO: Copy directly (safe)
3. If YES: Discuss with user and merge

---

## 🔍 Step 3.1: Check if .cursorrules Exists

```python
import os

if not os.path.exists(".cursorrules"):
    print("✅ No existing .cursorrules - safe to copy directly")
    # Go to Section A: Direct Copy
else:
    print("⚠️  Existing .cursorrules detected!")
    print("   Cannot blindly overwrite - must discuss with user")
    # Go to Section B: Merge Protocol
```

---

## 📋 Section A: Direct Copy (No Existing File)

If `.cursorrules` doesn't exist, simply copy:

```python
import shutil

# AGENT_OS_SOURCE from step 00
shutil.copy(
    f"{AGENT_OS_SOURCE}/.cursorrules",
    ".cursorrules"
)

print("✅ .cursorrules installed")
```

**Done!** Skip to validation checkpoint at the end of this file.

---

## 🔀 Section B: Merge Protocol (Existing File Found)

If `.cursorrules` exists, you MUST discuss with the user.

### Step 3.2: Read Both Files

```python
# Read existing rules
with open(".cursorrules", "r") as f:
    existing_rules = f.read()

# Read Agent OS rules
with open(f"{AGENT_OS_SOURCE}/.cursorrules", "r") as f:
    agent_os_rules = f.read()

print(f"📄 Your existing rules: {len(existing_rules.splitlines())} lines")
print(f"📄 Agent OS rules: {len(agent_os_rules.splitlines())} lines")
```

### Step 3.3: Present Options to User

```python
print("""
⚠️  Your project has existing .cursorrules

Agent OS needs to add rules to the TOP of your .cursorrules file
(they contain behavioral triggers that must run before other rules).

Options:
1. [Recommended] Auto-merge: Agent OS rules at top, your rules below
2. Manual merge: Show both files, you merge them yourself
3. Backup and replace: Use Agent OS rules only (your rules backed up)

Which option? (1/2/3): """)

user_choice = input().strip()
```

### Step 3.4: Execute User's Choice

#### Option 1: Auto-Merge (Recommended)

```python
if user_choice == "1":
    from datetime import datetime
    
    # Create merged content
    merged_content = f"""# prAxIs OS Rules
# (Added during Agent OS installation on {datetime.now().strftime('%Y-%m-%d')})

{agent_os_rules}

# ============================================================================
# Existing Project Rules (preserved from original .cursorrules)
# ============================================================================

{existing_rules}
"""
    
    # Backup original
    shutil.copy(".cursorrules", ".cursorrules.backup")
    
    # Write merged file
    with open(".cursorrules", "w") as f:
        f.write(merged_content)
    
    print("✅ Rules merged successfully!")
    print("   Structure: Agent OS rules (top) + Your rules (below)")
    print("   Backup: .cursorrules.backup")
```

#### Option 2: Manual Merge

```python
elif user_choice == "2":
    # Save Agent OS rules to temp file for user reference
    with open(".cursorrules.praxis-os", "w") as f:
        f.write(agent_os_rules)
    
    print("""
📄 Files for manual merge:

Your existing rules:  .cursorrules
Agent OS rules:       .cursorrules.praxis-os

Instructions:
1. Open both files
2. Copy Agent OS rules from .cursorrules.praxis-os
3. Paste at the TOP of .cursorrules
4. Ensure your existing rules remain below
5. Save .cursorrules
6. Delete .cursorrules.praxis-os when done

Press Enter when you've completed the manual merge...
    """)
    
    input()  # Wait for user
    print("✅ Manual merge completed (trusting user)")
```

#### Option 3: Backup and Replace

```python
else:  # Option 3 or invalid input
    from datetime import datetime
    
    # Backup with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f".cursorrules.backup.{timestamp}"
    
    shutil.copy(".cursorrules", backup_path)
    
    # Replace with Agent OS rules
    shutil.copy(f"{AGENT_OS_SOURCE}/.cursorrules", ".cursorrules")
    
    print(f"✅ Original rules backed up to: {backup_path}")
    print("   Agent OS rules are now active")
    print("\n💡 To restore your rules:")
    print("   1. Copy your rules from the backup")
    print("   2. Append them below Agent OS rules in .cursorrules")
```

---

## ✅ Validation Checkpoint #3

After handling .cursorrules, verify it's correct:

```python
import os

# Check file exists
if not os.path.exists(".cursorrules"):
    print("❌ .cursorrules missing!")
    exit(1)

# Check it has Agent OS content
with open(".cursorrules", "r") as f:
    content = f.read()

has_agent_os = "Agent OS" in content or "MANDATORY FIRST ACTION" in content

if not has_agent_os:
    print("⚠️  .cursorrules exists but doesn't contain Agent OS rules")
    print("   This might be intentional if you chose manual merge")
    print("   Verify Agent OS rules are present")
else:
    print("✅ .cursorrules configured with Agent OS rules")

# Check backup exists (if there was an existing file)
if os.path.exists(".cursorrules.backup"):
    print("✅ Original .cursorrules backed up")
```

---

## 🔍 Visual Verification

Check the merged file structure:

```bash
head -20 .cursorrules
```

**Should show**:
```
# prAxIs OS Rules
# (Added during Agent OS installation...)

## 🤖 OPERATING MODEL
...
```

If you chose auto-merge, further down you should see:

```
# ============================================================================
# Existing Project Rules (preserved from original .cursorrules)
# ============================================================================

[... your original rules ...]
```

---

## 🚨 Troubleshooting

### Issue: User chose option 1 but merge looks wrong

**Fix**: Restore from backup and try again:

```python
import shutil

# Restore original
if os.path.exists(".cursorrules.backup"):
    shutil.copy(".cursorrules.backup", ".cursorrules")
    print("✅ Restored from backup")
    # Try merge again
```

### Issue: Backup file missing

**Cause**: Either no existing file, or backup failed

**Check**:
```python
import os

if os.path.exists(".cursorrules.backup"):
    print("✅ Backup exists")
else:
    print("ℹ️  No backup (probably no existing .cursorrules)")
```

### Issue: Agent OS rules not at top

**Fix manually**:
1. Open `.cursorrules`
2. Cut the Agent OS section (starts with `# prAxIs OS Rules`)
3. Paste it at the very top of the file
4. Save

---

## 📊 Progress Check

At this point you should have:
- ✅ `.cursorrules` exists
- ✅ Contains Agent OS rules
- ✅ Original rules preserved (if they existed)
- ✅ Backup created (if there was an existing file)
- ✅ Validation checkpoint passed

**If anything above is ❌, stop and fix before continuing.**

---

## 🎯 What's Next

You've handled the `.cursorrules` file safely. Now you need to:
1. Create Python virtual environment
2. Install MCP server dependencies
3. Create `.cursor/mcp.json` configuration

**Next step**: Set up Python venv and Cursor MCP configuration.

---

## ➡️ NEXT STEP

**Read file**: `installation/04-gitignore.md`

That file will:
1. Configure `.gitignore` to prevent committing 2.6GB of ephemeral files
2. Add Agent OS entries (cache, backups, venv)
3. Verify gitignore is working correctly
4. Direct you to step 05 (venv and mcp setup)

---

**Status**: Step 3 Complete ✅  
**Handled**: .cursorrules (safely!)  
**Next File**: `04-gitignore.md`  
**Step**: 3 of 6

