# Step 6: Final Validation and Cleanup

**Previous**: `05-venv-mcp.md` (created venv, mcp.json, and RAG index)  
**Current**: Final validation and cleanup  
**Next**: Installation complete!

---

## 🎯 What This Step Does

1. Run comprehensive validation of entire installation
2. **Clean up temp directory** (delete cloned repo)
3. Provide user instructions
4. Declare installation complete

**Time**: ~1 minute

---

## ✅ Comprehensive Validation

Run this complete validation script:

```python
import os
import sys
import json

print("="*60)
print("AGENT OS INSTALLATION - FINAL VALIDATION")
print("="*60)

errors = []
warnings = []

# Check 1: All directories exist
print("\n📁 Checking directories...")
required_dirs = [
    ".praxis-os/standards/universal",
    ".praxis-os/usage",
    ".praxis-os/workflows",
    ".praxis-os/mcp_server",
    ".praxis-os/.cache",
    ".praxis-os/venv",
    ".cursor",
]

for d in required_dirs:
    if os.path.exists(d):
        print(f"  ✅ {d}")
    else:
        print(f"  ❌ {d}")
        errors.append(f"Missing directory: {d}")

# Check 2: Critical files exist
print("\n📄 Checking critical files...")
critical_files = [
    ".praxis-os/workflows/spec_creation_v1/metadata.json",
    ".praxis-os/workflows/spec_execution_v1/metadata.json",
    ".praxis-os/mcp_server/__main__.py",
    ".praxis-os/mcp_server/requirements.txt",
    ".cursorrules",
    ".cursor/mcp.json",
]

for f in critical_files:
    if os.path.exists(f):
        print(f"  ✅ {f}")
    else:
        print(f"  ❌ {f}")
        errors.append(f"Missing file: {f}")

# Check 3: Workflows directory populated
print("\n🔄 Checking workflows...")
workflow_count = sum(len(files) for _, _, files in os.walk(".praxis-os/workflows"))
if workflow_count >= 40:  # Should have ~47 files
    print(f"  ✅ Workflows populated ({workflow_count} files)")
else:
    print(f"  ⚠️  Workflows sparse ({workflow_count} files, expected ~47)")
    warnings.append(f"Workflows may be incomplete: {workflow_count} files")

# Check 4: Python venv working
print("\n🐍 Checking Python venv...")
if os.name == "nt":
    python_path = ".praxis-os/venv/Scripts/python.exe"
else:
    python_path = ".praxis-os/venv/bin/python"

if os.path.exists(python_path):
    print(f"  ✅ Python venv exists")
else:
    print(f"  ❌ Python venv missing")
    errors.append("Python venv not found")

# Check 5: mcp.json has correct module name
print("\n⚙️  Checking mcp.json configuration...")
try:
    with open(".cursor/mcp.json", "r") as f:
        mcp_config = json.load(f)
    
    module_name = mcp_config["mcpServers"]["praxis-os-rag"]["args"][1]
    if module_name == "mcp_server":
        print(f"  ✅ Module name correct: {module_name}")
    else:
        print(f"  ❌ Wrong module name: {module_name}")
        errors.append(f"Module should be 'mcp_server', not '{module_name}'")
        
except Exception as e:
    print(f"  ❌ mcp.json parse error: {e}")
    errors.append("mcp.json is invalid")

# Check 6: .cursorrules has prAxIs OS content
print("\n📜 Checking .cursorrules...")
try:
    with open(".cursorrules", "r") as f:
        cursorrules = f.read()
    
    if "prAxIs OS" in cursorrules or "MANDATORY FIRST ACTION" in cursorrules:
        print("  ✅ prAxIs OS rules present")
    else:
        print("  ⚠️  prAxIs OS rules not detected")
        warnings.append("cursorrules may not have prAxIs OS content")
except Exception as e:
    print(f"  ❌ Error reading .cursorrules: {e}")
    errors.append(".cursorrules unreadable")

# Check 7: RAG index exists
print("\n📚 Checking RAG index...")
rag_checks = {
    "Index directory": os.path.exists(".praxis-os/.cache/vector_index"),
    "LanceDB data": os.path.exists(".praxis-os/.cache/vector_index/praxis_os_standards.lance"),
    "Metadata file": os.path.exists(".praxis-os/.cache/vector_index/metadata.json"),
}

all_rag_passed = all(rag_checks.values())
if all_rag_passed:
    print("  ✅ RAG index built")
else:
    print("  ❌ RAG index missing or incomplete")
    for check, passed in rag_checks.items():
        if not passed:
            print(f"     Missing: {check}")
    errors.append("RAG index not built - run: .praxis-os/venv/bin/python .praxis-os/scripts/build_rag_index.py")

# Summary
print("\n" + "="*60)
if errors:
    print("❌ VALIDATION FAILED")
    print("\nErrors:")
    for error in errors:
        print(f"  - {error}")
    print("\nFix these errors before continuing!")
    sys.exit(1)
elif warnings:
    print("⚠️  VALIDATION PASSED WITH WARNINGS")
    print("\nWarnings:")
    for warning in warnings:
        print(f"  - {warning}")
    print("\nYou may proceed, but review warnings.")
else:
    print("✅ VALIDATION PASSED - ALL CHECKS SUCCESSFUL")

print("="*60)
```

---

## 🧹 CRITICAL: Clean Up Temp Directory

⚠️ **DO NOT SKIP THIS STEP!**

If you cloned to a temp directory in step 00, you MUST delete it now:

```python
import shutil
import os

# AGENT_OS_SOURCE from step 00
# This should be the temp directory path

if 'AGENT_OS_SOURCE' in globals() or 'AGENT_OS_SOURCE' in locals():
    # Check if it's a temp directory (safety check)
    if "/tmp/" in AGENT_OS_SOURCE or "temp" in AGENT_OS_SOURCE.lower():
        print(f"🗑️  Cleaning up temp directory: {AGENT_OS_SOURCE}")
        
        try:
            shutil.rmtree(AGENT_OS_SOURCE)
            print("✅ Temp directory deleted")
        except Exception as e:
            print(f"⚠️  Could not delete temp directory: {e}")
            print(f"   Please manually delete: {AGENT_OS_SOURCE}")
    else:
        print(f"ℹ️  Source directory looks permanent, not deleting: {AGENT_OS_SOURCE}")
else:
    print("ℹ️  No AGENT_OS_SOURCE variable found")
    print("   If you cloned to temp, please manually delete it")
```

**Manual cleanup** (if needed):

```bash
# If the script didn't delete it, do it manually
rm -rf /tmp/praxis-os-install-*
```

---

## 🎬 User Instructions

The installation is complete, but the MCP server won't start until Cursor is restarted or MCP is enabled.

**Inform the user:**

```
✅ prAxIs OS installed successfully!

Installation Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ .praxis-os/ directory structure created
✅ ~106 files copied from source repository
✅ .cursorrules configured (or merged with existing)
✅ Python virtual environment created
✅ MCP server dependencies installed
✅ .cursor/mcp.json configured
✅ Temp files cleaned up
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 🔄 Enable MCP Server:

   Option A: Restart Cursor (easiest)
   - Close and reopen Cursor
   - MCP server will start automatically

   Option B: Enable without restarting
   - Open Cursor Settings (Cmd/Ctrl + ,)
   - Navigate to: Features → Model Context Protocol
   - Find "praxis-os-rag" server
   - Click "Enable" or toggle it on

2. ✅ Verify MCP Server is Running:

   You should see MCP tools available in chat:
   - search_standards
   - start_workflow
   - get_current_phase
   - pos_browser
   - And more...

3. 🎯 Try It Out:

   Say to me: "Search standards for concurrency patterns"

   Or: "Start the spec creation workflow for building a rate limiter"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What's Installed:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Standards:
   - Universal CS fundamentals (architecture, testing, concurrency, etc.)
   - Searchable via MCP: search_standards()

🔄 Workflows:
   - spec_creation_v1: Phase-gated spec creation
   - spec_execution_v1: Dynamic spec execution
   - Accessible via: start_workflow()

🤖 MCP Server:
   - RAG engine (semantic search with 90% context reduction)
   - Workflow engine (phase-gated execution)
   - Browser automation (Playwright integration)
   - Sub-agents (design validator, concurrency analyzer, etc.)

📝 Documentation:
   - .praxis-os/usage/creating-specs.md
   - .praxis-os/usage/operating-model.md
   - .praxis-os/usage/mcp-usage-guide.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Troubleshooting:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If MCP server doesn't start:
1. Check Cursor's MCP logs
2. Verify .cursor/mcp.json exists and is valid
3. Run validation: .praxis-os/venv/bin/python -c "
   from pathlib import Path
   from mcp_server.config import ConfigLoader, ConfigValidator
   config = ConfigLoader.load(Path('.praxis-os'))
   errors = ConfigValidator.validate(config)
   print('✅ Valid' if not errors else f'❌ {errors}')
   "

If you need help: Check installation/README.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 Installation Complete!
```

---

## 📊 Final Status

At this point:
- ✅ All files installed
- ✅ All configuration done
- ✅ Temp files cleaned up
- ✅ User informed
- ✅ Ready to use

---

## 🚨 Post-Installation Checklist

Before you finish, double-check:

```python
final_checks = {
    "Directories created": os.path.exists(".praxis-os/workflows"),
    "Files copied": os.path.exists(".praxis-os/workflows/spec_creation_v1/metadata.json"),
    ".cursorrules handled": os.path.exists(".cursorrules"),
    "Python venv created": os.path.exists(".praxis-os/venv"),
    "mcp.json created": os.path.exists(".cursor/mcp.json"),
    "Temp directory deleted": not os.path.exists(AGENT_OS_SOURCE) if 'AGENT_OS_SOURCE' in globals() else True,
}

all_done = all(final_checks.values())

print("\nFinal Checklist:")
for check, status in final_checks.items():
    print(f"  {'✅' if status else '❌'} {check}")

if all_done:
    print("\n🎉 Installation 100% complete!")
else:
    print("\n⚠️  Some items incomplete - review above")
```

---

## 🎯 Installation Complete!

**You have successfully installed prAxIs OS!**

The installation followed these steps:
1. ✅ Cloned source to temp directory (step 00)
2. ✅ Created all required directories (step 01)
3. ✅ Copied all content files (step 02)
4. ✅ Handled .cursorrules safely (step 03)
5. ✅ Configured .gitignore (step 04)
6. ✅ Created Python venv, mcp.json, and RAG index (step 05)
7. ✅ Validated and cleaned up (step 06)

**No further steps required.**

The user should restart Cursor to activate the MCP server.

---

**Status**: Installation Complete ✅  
**Duration**: ~5-10 minutes  
**Files Installed**: ~106 files  
**Temp Files**: Cleaned up ✅

