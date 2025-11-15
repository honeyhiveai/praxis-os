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
from pathlib import Path

print("="*60)
print("prAxIs OS INSTALLATION - FINAL VALIDATION")
print("="*60)

errors = []
warnings = []

# Note: Agent detection logic is in installation/03-agent-configuration.md
# This validation script just checks what files exist and validates them

# Check 1: All directories exist
print("\n📁 Checking directories...")
required_dirs = [
    ".praxis-os/standards/universal",
    ".praxis-os/workflows",
    ".praxis-os/ouroboros",
    ".praxis-os/config",
    ".praxis-os/.cache",
    ".praxis-os/venv",
]

# Check for common agent directories (if they exist)
if Path(".cursor").exists():
    required_dirs.append(".cursor")
if Path(".vscode").exists():
    required_dirs.append(".vscode")

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
    ".praxis-os/ouroboros/__main__.py",
    ".praxis-os/ouroboros/requirements.txt",
]

# Check for agent-specific behavioral files (if they exist)
agent_behavioral_files = [
    ".cursorrules",  # Cursor
    ".clinerules",  # Cline
    ".claude/CLAUDE.md",  # Claude Code
    "CLAUDE.md",  # Claude Code CLI
    ".github/copilot-instructions.md",  # GitHub Copilot
]
for behavioral_file in agent_behavioral_files:
    if os.path.exists(behavioral_file):
        critical_files.append(behavioral_file)

# Check for MCP config files (if they exist)
mcp_config_files = [
    ".cursor/mcp.json",  # Cursor
    ".vscode/settings.json",  # VS Code agents (Cline, Claude Code, GitHub Copilot)
    ".vscode/mcp.json",  # GitHub Copilot (alternative)
    ".mcp.json",  # Claude Code CLI (project-level)
]
for mcp_file in mcp_config_files:
    if os.path.exists(mcp_file):
        critical_files.append(mcp_file)

for f in critical_files:
    if os.path.exists(f):
        print(f"  ✅ {f}")
    else:
        print(f"  ❌ {f}")
        errors.append(f"Missing file: {f}")

# Check 3: Workflows directory populated
print("\n🔄 Checking workflows...")
workflow_count = sum(len(files) for _, _, files in os.walk(".praxis-os/workflows"))
if workflow_count >= 40:  # Should have multiple workflow definitions
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

# Check 5: MCP configuration file validation
print("\n⚙️  Checking MCP configuration files...")
found_mcp_config = False

# Check all possible MCP config file locations
mcp_config_locations = [
    (".cursor/mcp.json", "mcpServers", "Cursor"),
    (".vscode/settings.json", "cline.mcpServers", "Cline"),
    (".vscode/settings.json", "claude-code.mcpServers", "Claude Code"),
    (".vscode/mcp.json", "mcpServers", "GitHub Copilot"),
    (".mcp.json", "mcpServers", "Claude Code CLI"),
]

for mcp_file, config_key, agent_name in mcp_config_locations:
    if os.path.exists(mcp_file):
        found_mcp_config = True
        print(f"  ✅ Found {mcp_file} ({agent_name})")
        try:
            with open(mcp_file, "r") as f:
                mcp_config = json.load(f)
            
            # Check for MCP server configuration
            if config_key == "mcpServers":
                # Direct mcpServers key (Cursor, GitHub Copilot, Claude Code CLI)
                if "mcpServers" in mcp_config:
                    if "praxis-os" in mcp_config["mcpServers"]:
                        module_name = mcp_config["mcpServers"]["praxis-os"]["args"][1]
                        if module_name == "ouroboros":
                            print(f"    ✅ MCP server 'praxis-os' configured correctly")
                        else:
                            print(f"    ⚠️  Module name: {module_name} (expected 'ouroboros')")
                            warnings.append(f"{mcp_file}: Module name is '{module_name}', expected 'ouroboros'")
                    else:
                        print(f"    ⚠️  MCP servers found but 'praxis-os' not configured")
                        warnings.append(f"{mcp_file}: MCP servers exist but 'praxis-os' missing")
                else:
                    print(f"    ⚠️  'mcpServers' key not found")
                    warnings.append(f"{mcp_file}: Missing 'mcpServers' key")
            else:
                # Nested key in settings.json (Cline, Claude Code VS Code)
                if config_key in mcp_config:
                    if "praxis-os" in mcp_config[config_key]:
                        print(f"    ✅ MCP server 'praxis-os' configured correctly")
                    else:
                        print(f"    ⚠️  {config_key} found but 'praxis-os' not configured")
                        warnings.append(f"{mcp_file}: {config_key} exists but 'praxis-os' missing")
                else:
                    print(f"    ⚠️  '{config_key}' key not found")
                    warnings.append(f"{mcp_file}: Missing '{config_key}' key")
                    
        except Exception as e:
            print(f"    ❌ Parse error: {e}")
            errors.append(f"{mcp_file} is invalid JSON")

if not found_mcp_config:
    print("  ⚠️  No MCP configuration files found")
    print("     Expected one of: .cursor/mcp.json, .vscode/settings.json, .vscode/mcp.json, .mcp.json")
    warnings.append("No MCP configuration file found - agent may not be configured")

# Check 6: Agent behavioral files have prAxIs OS content
print("\n📜 Checking agent behavioral files...")
behavioral_files_checked = False
behavioral_files = [
    ".cursorrules",  # Cursor
    ".clinerules",  # Cline
    ".claude/CLAUDE.md",  # Claude Code
    "CLAUDE.md",  # Claude Code CLI
    ".github/copilot-instructions.md",  # GitHub Copilot
]

for behavioral_file in behavioral_files:
    if os.path.exists(behavioral_file):
        behavioral_files_checked = True
        print(f"  ✅ Found {behavioral_file}")
        try:
            with open(behavioral_file, "r") as f:
                content = f.read()
            if "prAxIs OS" in content or "MANDATORY FIRST ACTION" in content:
                print(f"    ✅ Contains prAxIs OS content")
            else:
                print(f"    ⚠️  May not contain prAxIs OS content")
                warnings.append(f"{behavioral_file} may not have prAxIs OS content")
        except Exception as e:
            print(f"    ❌ Error reading: {e}")
            errors.append(f"{behavioral_file} unreadable")

if not behavioral_files_checked:
    print("  ⚠️  No agent behavioral files found")
    warnings.append("No agent behavioral file found - agent may not be configured")

# Check 7: RAG index exists
print("\n📚 Checking RAG index...")
rag_checks = {
    "Index directory": os.path.exists(".praxis-os/.cache/indexes"),
    "Standards index": os.path.exists(".praxis-os/.cache/indexes/standards"),
    "Code index": os.path.exists(".praxis-os/.cache/indexes/code"),
}

all_rag_passed = all(rag_checks.values())
if all_rag_passed:
    print("  ✅ RAG index built")
else:
    print("  ❌ RAG index missing or incomplete")
    for check, passed in rag_checks.items():
        if not passed:
            print(f"     Missing: {check}")
    errors.append("RAG index not built - start the MCP server and it will auto-build indexes")

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

# PRAXIS_OS_SOURCE from step 00
# This should be the temp directory path

if 'PRAXIS_OS_SOURCE' in globals() or 'PRAXIS_OS_SOURCE' in locals():
    # Check if it's a temp directory (safety check)
    if "/tmp/" in PRAXIS_OS_SOURCE or "temp" in PRAXIS_OS_SOURCE.lower():
        print(f"🗑️  Cleaning up temp directory: {PRAXIS_OS_SOURCE}")
        
        try:
            shutil.rmtree(PRAXIS_OS_SOURCE)
            print("✅ Temp directory deleted")
        except Exception as e:
            print(f"⚠️  Could not delete temp directory: {e}")
            print(f"   Please manually delete: {PRAXIS_OS_SOURCE}")
    else:
        print(f"ℹ️  Source directory looks permanent, not deleting: {PRAXIS_OS_SOURCE}")
else:
    print("ℹ️  No PRAXIS_OS_SOURCE variable found")
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
✅ All required files copied (standards, workflows, server code)
✅ Agent configuration files configured (or merged with existing)
✅ Python virtual environment created
✅ MCP server dependencies installed
✅ MCP configuration file configured
✅ Temp files cleaned up
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 🔄 Enable MCP Server:

   The steps depend on your agent/IDE:
   
   **Cursor:**
   - Option A: Restart Cursor (easiest)
   - Option B: Open Cursor Settings → Features → Model Context Protocol → Enable "praxis-os"
   
   **VS Code (Cline/Claude Code/GitHub Copilot):**
   - Restart VS Code or reload window
   - MCP server should start automatically if configured correctly
   
   **Claude Code CLI:**
   - MCP server starts automatically when you run Claude Code commands

2. ✅ Verify MCP Server is Running:

   You should see MCP tools available in chat:
   - pos_search_project (search standards and code)
   - pos_workflow (workflow management)
   - pos_browser (browser automation)
   - pos_filesystem (file operations)
   - current_date, get_server_info
   - And more...

3. 🎯 Try It Out:

   Say to your agent: "Search standards for concurrency patterns"

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

📝 Configuration:
   - .praxis-os/config/mcp.yaml (customized for your project)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Troubleshooting:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If MCP server doesn't start:
1. Check your agent's MCP logs (Cursor: Settings → MCP logs, VS Code: Output panel)
2. Verify MCP configuration file exists and is valid:
   - Cursor: `.cursor/mcp.json`
   - VS Code: `.vscode/settings.json` or `.vscode/mcp.json`
   - Claude Code CLI: `.mcp.json`
3. Run validation: .praxis-os/venv/bin/python -c "
   from pathlib import Path
   from ouroboros.config.loader import load_config
   config = load_config(Path('.praxis-os/config/mcp.yaml'))
   print('✅ Config loaded successfully')
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
    "Python venv created": os.path.exists(".praxis-os/venv"),
    "Temp directory deleted": not os.path.exists(PRAXIS_OS_SOURCE) if 'PRAXIS_OS_SOURCE' in globals() else True,
}

# Add agent-specific checks (if files exist)
behavioral_files = [".cursorrules", ".clinerules", ".claude/CLAUDE.md", "CLAUDE.md", ".github/copilot-instructions.md"]
for behavioral_file in behavioral_files:
    if os.path.exists(behavioral_file):
        final_checks[f"Agent behavioral file ({behavioral_file})"] = True

mcp_config_files = [".cursor/mcp.json", ".vscode/settings.json", ".vscode/mcp.json", ".mcp.json"]
for mcp_file in mcp_config_files:
    if os.path.exists(mcp_file):
        final_checks[f"MCP config ({mcp_file})"] = True

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
4. ✅ Configured agent-specific files safely (step 03)
5. ✅ Configured .gitignore (step 04)
6. ✅ Created Python venv, MCP config, and RAG index (step 05)
7. ✅ Validated and cleaned up (step 06)

**No further steps required.**

The user should restart their agent/IDE to activate the MCP server.

---

**Status**: Installation Complete ✅  
**Duration**: ~5-10 minutes  
**Files Installed**: Complete installation (see script output for counts)  
**Temp Files**: Cleaned up ✅

