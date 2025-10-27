# Create temp directory
temp_dir = tempfile.mkdtemp(prefix="agent-os-install-")
print(f"📦 Cloning to temp location: {temp_dir}")

# Clone repo to temp
subprocess.run([
    "git", "clone", 
    "https://github.com/honeyhiveai/agent-os-enhanced.git",
    temp_dir
], check=True)

# Store this path - you'll use it throughout installation
AGENT_OS_SOURCE = temp_dir
print(f"✅ Source ready at: {AGENT_OS_SOURCE}")

# IMPORTANT: At the end of installation (step 05), you'll delete this temp directory
```

### Option B: User Provides Path

If the user already has Agent OS cloned somewhere:

```python
# Ask user where they've cloned agent-os-enhanced
AGENT_OS_SOURCE = input("Path to agent-os-enhanced clone: ")

# Validate it
assert os.path.exists(f"{AGENT_OS_SOURCE}/universal/"), "Invalid path"
assert os.path.exists(f"{AGENT_OS_SOURCE}/mcp_server/"), "Invalid path"

print(f"✅ Using source at: {AGENT_OS_SOURCE}")
```

### Pre-Installation Checks

```python
# 1. Check source repo is valid
assert os.path.exists(f"{AGENT_OS_SOURCE}/universal/"), "Source repo invalid"
assert os.path.exists(f"{AGENT_OS_SOURCE}/mcp_server/"), "MCP server not found"

# 2. Check target project is writable
assert os.access(".", os.W_OK), "Target directory not writable"

# 3. Check Python version
import sys
assert sys.version_info >= (3, 8), "Python 3.8+ required"

# 4. Check NOT inside agent-os-enhanced repo itself
current_dir = os.path.basename(os.getcwd())
assert current_dir != "agent-os-enhanced", "Don't install inside source repo!"
```

**If any checks fail, stop and fix before continuing.**

**⚠️ REMEMBER**: If you cloned to temp (Option A), you MUST delete it in step 05!

---

## 📚 Reference Materials

During installation, you can reference:

- **Common Failures**: `installation/TROUBLESHOOTING.md` (if you get stuck)
- **Detailed Guide**: `installation/DETAILED-GUIDE.md` (800+ lines, comprehensive)
- **Merge Protocol**: `installation/03-cursorrules.md` (step 3 has full details)

But for normal installation, just follow 01 → 02 → 03 → 04 → 05.

---

## 🎬 Ready to Start?

You've read the critical mistakes. You understand the architecture.

**Your first task**: Create directories.

---

## ➡️ NEXT STEP

**Read file**: `installation/01-directories.md`

That file will:
1. List all 8 required directories
2. Provide exact commands to create them
3. Provide validation commands
4. Direct you to step 02

---

**Status**: Pre-Installation Complete ✅  
**Next File**: `01-directories.md`  
**Step**: 1 of 5


<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Current Time
10/10/2025, 9:33:34 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
106,689 / 200K tokens used (53%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
# Multi-Agent Installation Architecture for Agent OS

## 🎯 Design Goals

Support installation across multiple AI coding agents:
- **Cursor** - Most common, already supported
- **Cline** (VS Code extension) - Growing rapidly
- **Windsurf** - New competitor
- **Claude Code** - Anthropic's potential offering
- **Continue** (VS Code extension) - Open source alternative
- **Generic VS Code** - Fallback for any VS Code-based setup

## 📋 Agent Configuration Matrix

### Configuration Differences

| Agent | Rules File | MCP Config | Config Format |
|-------|-----------|------------|---------------|
| **Cursor** | `.cursorrules` | `.cursor/mcp.json` | Cursor-specific JSON |
| **Cline** | `.clinerules` | `.vscode/settings.json` | VS Code settings |
| **Windsurf** | `.windsurfrules` | `.windsurf/mcp.json` | Windsurf-specific JSON |
| **Continue** | `.continuerules` | `.vscode/settings.json` | VS Code settings |
| **VS Code** | `.vscode/rules.md` | `.vscode/settings.json` | VS Code settings |

## 🔍 Agent Detection Strategy

### Phase 1: Automatic Detection

Create `installation/00-detect-agent.py`:

```python
"""
Agent OS - Multi-Agent Detection
Automatically detects which AI coding agent is being used.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Configuration profile for an AI coding agent."""
    name: str
    rules_file: str
    mcp_config_path: str
    mcp_config_key: str
    python_path_template: str  # Template with {workspaceFolder}
    detection_files: list[str]  # Files that indicate this agent
    priority: int  # Higher = check first
    
class AgentDetector:
    """Detects which AI coding agent is being used."""
    
    AGENT_PROFILES = {
        "cursor": AgentConfig(
            name="Cursor",
            rules_file=".cursorrules",
            mcp_config_path=".cursor/mcp.json",
            mcp_config_key="mcpServers",
            python_path_template="${workspaceFolder}/.praxis-os/venv/bin/python",
            detection_files=[".cursor/mcp.json", ".cursor/settings.json"],
            priority=10
        ),
        "cline": AgentConfig(
            name="Cline",
            rules_file=".clinerules",
            mcp_config_path=".vscode/settings.json",
            mcp_config_key="cline.mcpServers",
            python_path_template="${workspaceFolder}/.praxis-os/venv/bin/python",
            detection_files=[".vscode/extensions.json"],  # Check for Cline extension
            priority=9
        ),
        "windsurf": AgentConfig(
            name="Windsurf",
            rules_file=".windsurfrules",
            mcp_config_path=".windsurf/mcp.json",
            mcp_config_key="mcpServers",
            python_path_template="${workspaceFolder}/.praxis-os/venv/bin/python",
            detection_files=[".windsurf/config.json"],
            priority=8
        ),
        "continue": AgentConfig(
            name="Continue",
            rules_file=".continuerules",
            mcp_config_path=".vscode/settings.json",
            mcp_config_key="continue.mcpServers",
            python_path_template="${workspaceFolder}/.praxis-os/venv/bin/python",
            detection_files=[".continue/config.json"],
            priority=7
        ),
        "vscode": AgentConfig(
            name="VS Code (Generic)",
            rules_file=".vscode/agent-rules.md",
            mcp_config_path=".vscode/settings.json",
            mcp_config_key="mcp.servers",
            python_path_template="${workspaceFolder}/.praxis-os/venv/bin/python",
            detection_files=[".vscode/settings.json"],
            priority=1  # Lowest priority (fallback)
        )
    }
    
    @classmethod
    def detect_agent(cls) -> Optional[str]:
        """
        Detect which agent is being used based on project files.
        
        Returns:
            Agent ID (e.g., "cursor", "cline") or None if cannot detect
        """
        # Sort by priority (highest first)
        sorted_profiles = sorted(
            cls.AGENT_PROFILES.items(),
            key=lambda x: x[1].priority,
            reverse=True
        )
        
        for agent_id, profile in sorted_profiles:
            # Check if any detection files exist
            for detection_file in profile.detection_files:
                if os.path.exists(detection_file):
                    print(f"🔍 Detected: {profile.name}")
                    print(f"   Evidence: {detection_file} exists")
                    return agent_id
        
        print("⚠️  Could not auto-detect agent")
        return None
    
    @classmethod
    def detect_or_prompt(cls) -> str:
        """
        Detect agent or prompt user to select.
        
        Returns:
            Selected agent ID
        """
        # Try auto-detection first
        detected = cls.detect_agent()
        
        if detected:
            # Confirm with user
            profile = cls.AGENT_PROFILES[detected]
            print(f"\n✅ Detected: {profile.name}")
            response = input(f"   Use {profile.name}? (y/n): ").lower()
            
            if response == 'y':
                return detected
            else:
                print("   User wants different agent, showing menu...")
        
        # Show selection menu
        return cls.prompt_agent_selection()
    
    @classmethod
    def prompt_agent_selection(cls) -> str:
        """
        Prompt user to select their agent.
        
        Returns:
            Selected agent ID
        """
        print("\n🤖 Select your AI coding agent:")
        print()
        
        # Create numbered menu
        agents = list(cls.AGENT_PROFILES.items())
        for i, (agent_id, profile) in enumerate(agents, 1):
            print(f"   {i}. {profile.name}")
        
        print()
        
        while True:
            try:
                choice = int(input("Enter number (1-{}): ".format(len(agents))))
                if 1 <= choice <= len(agents):
                    selected_id = agents[choice - 1][0]
                    selected_profile = cls.AGENT_PROFILES[selected_id]
                    print(f"\n✅ Selected: {selected_profile.name}")
                    return selected_id
                else:
                    print("❌ Invalid choice, try again")
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Installation cancelled")
                exit(1)
    
    @classmethod
    def get_config(cls, agent_id: str) -> AgentConfig:
        """Get configuration for specified agent."""
        return cls.AGENT_PROFILES[agent_id]

# Example usage in installation script
if __name__ == "__main__":
    detector = AgentDetector()
    agent_id = detector.detect_or_prompt()
    config = detector.get_config(agent_id)
    
    print(f"\n📋 Configuration for {config.name}:")
    print(f"   Rules file: {config.rules_file}")
    print(f"   MCP config: {config.mcp_config_path}")
    print(f"   Config key: {config.mcp_config_key}")
```

### Phase 2: Enhanced Detection Heuristics

Add `installation/detect_agent_advanced.py`:

```python
"""
Advanced agent detection using multiple signals.
"""

import subprocess
import json
from pathlib import Path

class AdvancedAgentDetector:
    """More sophisticated detection methods."""
    
    @staticmethod
    def detect_from_process() -> Optional[str]:
        """Detect from running processes."""
        try:
            # Check for Cursor process
            result = subprocess.run(
                ["pgrep", "-f", "Cursor"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return "cursor"
            
            # Check for VS Code with Cline
            result = subprocess.run(
                ["pgrep", "-f", "Code.*cline"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return "cline"
                
        except FileNotFoundError:
            pass  # pgrep not available on Windows
        
        return None
    
    @staticmethod
    def detect_from_extensions() -> Optional[str]:
        """Detect from installed VS Code extensions."""
        extensions_file = Path(".vscode/extensions.json")
        
        if extensions_file.exists():
            try:
                with open(extensions_file) as f:
                    data = json.load(f)
                    recommendations = data.get("recommendations", [])
                    
                    if "saoudrizwan.claude-dev" in recommendations:
                        return "cline"
                    if "continue.continue" in recommendations:
                        return "continue"
                        
            except (json.JSONDecodeError, KeyError):
                pass
        
        return None
    
    @staticmethod
    def detect_from_environment() -> Optional[str]:
        """Detect from environment variables."""
        import os
        
        # Check for Cursor-specific env vars
        if os.getenv("CURSOR_SESSION_ID"):
            return "cursor"
        
        # Check for VS Code env vars
        if os.getenv("VSCODE_CWD"):
            # Could be any VS Code-based agent
            # Fall back to other detection methods
            pass
        
        return None
```

## 🏗️ Modified Installation Flow

### New Step 00: Agent Detection

Create `installation/00-START.md` (updated):

```markdown
# Agent OS Installation - START HERE

## 🤖 Step 0: Detect Your AI Agent

Before installation, we need to know which AI coding agent you're using.

### Automatic Detection

Run this command to auto-detect:

```python
import sys
sys.path.insert(0, "{AGENT_OS_SOURCE}/installation")

from agent_detector import AgentDetector

detector = AgentDetector()
agent_id = detector.detect_or_prompt()
config = detector.get_config(agent_id)

# Store for later steps
AGENT_ID = agent_id
AGENT_CONFIG = config

print(f"\n✅ Configured for: {config.name}")
print(f"   Installing rules to: {config.rules_file}")
print(f"   Installing MCP to: {config.mcp_config_path}")
```

### Manual Selection

If auto-detection fails, you'll see a menu:

```
🤖 Select your AI coding agent:

   1. Cursor
   2. Cline (VS Code extension)
   3. Windsurf
   4. Continue (VS Code extension)
   5. VS Code (Generic)

Enter number (1-5):
```

### What Gets Configured

Based on your selection, installation will:

| Agent | Rules File | MCP Config Location |
|-------|-----------|---------------------|
| Cursor | `.cursorrules` | `.cursor/mcp.json` |
| Cline | `.clinerules` | `.vscode/settings.json` |
| Windsurf | `.windsurfrules` | `.windsurf/mcp.json` |
| Continue | `.continuerules` | `.vscode/settings.json` |
| VS Code | `.vscode/agent-rules.md` | `.vscode/settings.json` |

---

## ➡️ NEXT STEP

Once agent is detected, proceed to:

**Read file**: `installation/01-directories.md`

(Directory creation is same for all agents)
```

### Updated Step 3: Agent-Specific Rules File

Create `installation/03-rules-file-{agent}.md`:

```markdown
# Step 3: Configure {AGENT_NAME} Rules File

**Previous**: Directory structure created, files copied  
**Current**: Creating {rules_file}  
**Next**: MCP configuration

---

## 📄 {AGENT_NAME} Rules File: {rules_file}

### Check Existing File

```python
import os

rules_file = "{rules_file}"

if os.path.exists(rules_file):
    print(f"⚠️  {rules_file} already exists")
    print("   Options:")
    print("   1. Backup and replace")
    print("   2. Merge (append Agent OS section)")
    print("   3. Skip (keep existing)")
    
    choice = input("Enter choice (1/2/3): ")
    # Handle choice...
else:
    print(f"✅ {rules_file} does not exist, will create fresh")
```

### Agent OS Rules Content

```python
AGENT_OS_RULES = """
# Agent OS Enhanced - {AGENT_NAME} Configuration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛑🛑🛑 STOP 🛑🛑🛑
MANDATORY:
Before you respond, you MUST answer this question:
"Have I run search_standards('Agent OS orientation guide') this conversation?"

If NO: Run it now via MCP tool, then reply "✅ Oriented. Ready."
If YES: Proceed with user's request.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[... rest of standard Agent OS rules ...]
"""

# Write rules file
with open(rules_file, 'w') as f:
    f.write(AGENT_OS_RULES)

print(f"✅ Created {rules_file}")
```
```

### Updated Step 5: Agent-Specific MCP Config

Create `installation/05-mcp-config-{agent}.py`:

```python
"""
Agent-specific MCP configuration generator.
"""

import json
import os
from pathlib import Path

class MCPConfigGenerator:
    """Generate MCP config for different agents."""
    
    @staticmethod
    def generate_cursor_config(python_path: str) -> dict:
        """Generate .cursor/mcp.json"""
        return {
            "mcpServers": {
                "agent-os-enhanced": {
                    "command": python_path,
                    "args": ["-m", "mcp_server"],
                    "env": {
                        "PROJECT_ROOT": "${workspaceFolder}",
                        "PYTHONPATH": "${workspaceFolder}/.praxis-os",
                        "PYTHONUNBUFFERED": "1"
                    }
                }
            }
        }
    
    @staticmethod
    def generate_cline_config(python_path: str) -> dict:
        """Generate settings for .vscode/settings.json"""
        return {
            "cline.mcpServers": {
                "agent-os-enhanced": {
                    "command": python_path,
                    "args": ["-m", "mcp_server"],
                    "env": {
                        "PROJECT_ROOT": "${workspaceFolder}",
                        "PYTHONPATH": "${workspaceFolder}/.praxis-os",
                        "PYTHONUNBUFFERED": "1"
                    }
                }
            }
        }
    
    @staticmethod
    def generate_windsurf_config(python_path: str) -> dict:
        """Generate .windsurf/mcp.json"""
        return {
            "mcpServers": {
                "agent-os-enhanced": {
                    "command": python_path,
                    "args": ["-m", "mcp_server"],
                    "env": {
                        "PROJECT_ROOT": "${workspaceFolder}",
                        "PYTHONPATH": "${workspaceFolder}/.praxis-os"
                    }
                }
            }
        }
    
    @classmethod
    def install_config(cls, agent_id: str, config: AgentConfig):
        """Install MCP config for specified agent."""
        
        # Determine Python path (platform-specific)
        if os.name == "nt":  # Windows
            python_path = "${workspaceFolder}/.praxis-os/venv/Scripts/python.exe"
        else:  # Unix-like
            python_path = config.python_path_template
        
        # Generate config
        if agent_id == "cursor":
            mcp_config = cls.generate_cursor_config(python_path)
            config_file = Path(config.mcp_config_path)
            
            # Create directory
            config_file.parent.mkdir(exist_ok=True)
            
            # Write config
            with open(config_file, 'w') as f:
                json.dump(mcp_config, f, indent=2)
                
        elif agent_id == "cline":
            settings_config = cls.generate_cline_config(python_path)
            config_file = Path(config.mcp_config_path)
            
            # Merge with existing settings
            existing = {}
            if config_file.exists():
                with open(config_file) as f:
                    existing = json.load(f)
            
            # Merge
            existing.update(settings_config)
            
            # Write back
            config_file.parent.mkdir(exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(existing, f, indent=2)
                
        elif agent_id == "windsurf":
            mcp_config = cls.generate_windsurf_config(python_path)
            config_file = Path(config.mcp_config_path)
            
            config_file.parent.mkdir(exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(mcp_config, f, indent=2)
        
        print(f"✅ MCP config installed: {config_file}")
```

## 🎯 Installation Summary Template

Create `installation/INSTALL-COMPLETE.md`:

```markdown
# ✅ Agent OS Installation Complete!

## 📊 Installation Summary

**Agent**: {AGENT_NAME}
**Date**: {TIMESTAMP}
**Duration**: {INSTALL_TIME}

## 📁 Files Installed

- ✅ `.praxis-os/` directory structure
- ✅ Standards copied from source
- ✅ Workflows configured
- ✅ MCP server installed
- ✅ Python venv created
- ✅ {rules_file} configured
- ✅ {mcp_config_path} configured

## 🚀 Next Steps

### 1. Restart {AGENT_NAME}

{agent_specific_restart_instructions}

### 2. Verify MCP Connection

In {AGENT_NAME}, run:
```
Can you run search_standards('Agent OS orientation guide')?
```

Expected response: Orientation information from Agent OS

### 3. Try Your First Workflow

```
Create spec for [your feature name]
```

## 📚 Documentation

- Full docs: https://honeyhiveai.github.io/agent-os-enhanced/
- Usage guide: `.praxis-os/usage/operating-model.md`
- Standards: `.praxis-os/standards/`

## 🆘 Troubleshooting

If MCP not connecting:
1. Check {mcp_config_path} exists and has correct Python path
2. Verify venv exists: `ls .praxis-os/venv/`
3. Test MCP server manually: `.praxis-os/venv/bin/python -m mcp_server`

Need help? Check `.praxis-os/usage/mcp-usage-guide.md`
```

## 🔄 Implementation Plan

### Phase 1: Core Detection (Week 1)
- [x] Create agent detection module
- [ ] Test with Cursor, Cline, VS Code
- [ ] Add process-based detection
- [ ] Add extension-based detection

### Phase 2: Config Generators (Week 2)
- [ ] Implement Cursor config generator
- [ ] Implement Cline config generator  
- [ ] Implement Windsurf config generator
- [ ] Implement generic VS Code generator
- [ ] Test each configuration

### Phase 3: Installation Flow (Week 3)
- [ ] Update 00-START.md with detection
- [ ] Create agent-specific rules templates
- [ ] Update MCP config step
- [ ] Add agent-specific validation
- [ ] Test full installation for each agent

### Phase 4: Documentation (Week 4)
- [ ] Document each agent's quirks
- [ ] Create troubleshooting per agent
- [ ] Add screenshots per agent
- [ ] Create video walkthroughs

## 🎁 Bonus: Installation CLI

Create `install.py` in root:

```python
"""
Agent OS Enhanced - Universal Installer
Supports: Cursor, Cline, Windsurf, Continue, VS Code
"""

import sys
from pathlib import Path

# Add installation dir to path
sys.path.insert(0, str(Path(__file__).parent / "installation"))

from agent_detector import AgentDetector
from installation_orchestrator import InstallationOrchestrator

def main():
    print("🚀 Agent OS Enhanced - Universal Installer\n")
    
    # Detect agent
    detector = AgentDetector()
    agent_id = detector.detect_or_prompt()
    config = detector.get_config(agent_id)
    
    # Run installation
    orchestrator = InstallationOrchestrator(agent_id, config)
    success = orchestrator.run_installation()
    
    if success:
        print("\n✅ Installation complete!")
        print(f"   Configured for: {config.name}")
        print(f"\n   Restart {config.name} and try:")
        print('   "Can you run search_standards(\'Agent OS orientation guide\')?"')
    else:
        print("\n❌ Installation failed")
        print("   Check installation/INSTALL-LOG.txt for details")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Usage:
```bash
python install.py
```

This creates a **universal installer** that works with any supported agent!
</result>
<task_progress>
- [x] Understand current installation process
- [x] Design agent detection mechanism
- [x] Create agent configuration matrix
- [x] Propose installation flow architecture
- [x] Design modular agent-specific configs
- [x] Create implementation plan
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
hmmm is scripting it all out necessary? is it the best path, the goal of the project is to use the ai as the installer, starting the path of building the trust in the
</feedback>
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Recently Modified Files
These files have been modified since you last accessed them (file was just edited so you may need to re-read it before editing):
mcp_server/rag_engine.py

# Current Time
10/10/2025, 9:36:37 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
114,387 / 200K tokens used (57%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
# AI-Driven Multi-Agent Installation Architecture

## 🎯 Core Philosophy

**Trust through transparency**: The AI agent reads markdown guides, explains what it's doing, asks for confirmation, and builds trust through the installation process itself.

**No hidden scripts** - Everything is conversational and visible.

## 📋 Redesigned Approach: AI-Guided Installation

### Current State (Good Foundation)
```
installation/
├── 00-START.md          ← AI reads this first
├── 01-directories.md    ← Step-by-step, AI follows
├── 02-copy-files.md     
├── 03-cursorrules.md    
├── 04-gitignore.md      
├── 05-venv-mcp.md       
└── 06-validate.md       
```

### Enhancement: Agent Detection in Markdown

**Update `00-START.md`** to include agent detection logic that the AI can follow:

```markdown
# Agent OS Installation - START HERE

## 🤖 Step 0: Detect Your Environment

**AI: Follow these detection steps in order:**

### 1. Check for Cursor
```
if exists(".cursor/mcp.json") OR exists(".cursor/settings.json"):
    DETECTED_AGENT = "Cursor"
    RULES_FILE = ".cursorrules"
    MCP_CONFIG = ".cursor/mcp.json"
    MCP_KEY = "mcpServers"
```

### 2. Check for Cline (VS Code Extension)
```
if exists(".vscode/extensions.json"):
    read and check for "saoudrizwan.claude-dev":
        DETECTED_AGENT = "Cline"
        RULES_FILE = ".clinerules"
        MCP_CONFIG = ".vscode/settings.json"
        MCP_KEY = "cline.mcpServers"
```

### 3. Check for Windsurf
```
if exists(".windsurf/"):
    DETECTED_AGENT = "Windsurf"
    RULES_FILE = ".windsurfrules"
    MCP_CONFIG = ".windsurf/mcp.json"
    MCP_KEY = "mcpServers"
```

### 4. Check for Continue
```
if exists(".continue/config.json"):
    DETECTED_AGENT = "Continue"
    RULES_FILE = ".continuerules"
    MCP_CONFIG = ".vscode/settings.json"
    MCP_KEY = "continue.mcpServers"
```

### 5. Fallback to VS Code Generic
```
if exists(".vscode/"):
    DETECTED_AGENT = "VS Code"
    RULES_FILE = ".vscode/agent-rules.md"
    MCP_CONFIG = ".vscode/settings.json"
    MCP_KEY = "mcp.servers"
```

---

## 🗣️ Conversation Template for AI

**AI should say:**

> I've detected your environment by checking for configuration files:
> 
> - ✅ Found: {files_found}
> - 🤖 Detected Agent: **{DETECTED_AGENT}**
> 
> This means I'll configure:
> - Rules file: `{RULES_FILE}`
> - MCP configuration: `{MCP_CONFIG}`
> - Config key: `{MCP_KEY}`
> 
> Is this correct? (If not, please tell me which agent you're using)

**If user confirms:**
> Great! I'll proceed with {DETECTED_AGENT} configuration.
> 
> Here's what I'm about to do:
> 1. Create `.praxis-os/` directory structure
> 2. Copy standards, workflows, and MCP server from source
> 3. Create `{RULES_FILE}` with Agent OS behaviors
> 4. Configure MCP in `{MCP_CONFIG}`
> 5. Set up Python virtual environment
> 
> Ready to start? This will take ~5 minutes.

---

## 📂 Source Repository Location

**AI: Ask the user where to get Agent OS source:**

> I need the Agent OS Enhanced source code. Where should I get it from?
> 
> **Option 1** (Recommended): I'll clone it to a temporary directory
> ```bash
> git clone https://github.com/honeyhiveai/agent-os-enhanced.git /tmp/agent-os-install-{random}
> ```
> 
> **Option 2**: You tell me where you've already cloned it
> 
> Which option would you prefer?

**Store the answer as `AGENT_OS_SOURCE`**

---

## ➡️ NEXT STEP

Now proceed to: `installation/01-directories.md`
```

### Enhancement: Agent-Specific Configuration Sections

**Create `installation/config-templates/` directory:**

```
installation/
├── config-templates/
│   ├── cursor-mcp.json          # Template for Cursor
│   ├── cline-settings.json      # Template for Cline
│   ├── windsurf-mcp.json        # Template for Windsurf
│   ├── continue-settings.json   # Template for Continue
│   ├── vscode-settings.json     # Generic VS Code
│   │
│   ├── cursorrules.md           # Agent OS rules for Cursor
│   ├── clinerules.md            # Agent OS rules for Cline
│   ├── windsurfrules.md         # Agent OS rules for Windsurf
│   ├── continuerules.md         # Agent OS rules for Continue
