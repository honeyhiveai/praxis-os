  
- **Workflow Engine** (`workflow_engine.py`): Phase-gated execution with:
  - Sequential phase access enforcement
  - Checkpoint validation between phases
  - Dynamic content loading from RAG
  - Session management and state persistence
  
- **Framework Generator** (`framework_generator.py`): Dynamic workflow creation
- **State Manager** (`state_manager.py`): Session persistence and recovery
- **Browser Manager** (`server/browser_manager.py`): Puppeteer integration for testing
- **Server Factory** (`server/factory.py`): Dependency injection and initialization

### 2. **Universal Standards** (`universal/standards/`)
Comprehensive, language-agnostic best practices organized by domain:

**12 Standard Categories:**
- `ai-assistant/` - RAG content authoring, MCP tools guide
- `ai-safety/` - Production code checklists, safety patterns
- `architecture/` - Dependency injection, API design, SOLID principles
- `concurrency/` - Thread safety, race conditions, locking strategies
- `database/` - Schema design, query optimization
- `documentation/` - Code comments, API docs, README templates
- `failure-modes/` - Graceful degradation, retries, circuit breakers
- `installation/` - Installation standards and procedures
- `meta-workflow/` - Framework creation guidelines
- `performance/` - Optimization patterns, profiling
- `security/` - Authentication, encryption, secure coding
- `testing/` - Test pyramid, test doubles, property-based testing
- `workflows/` - Workflow design and execution patterns

### 3. **Workflow System** (`universal/workflows/`)
Three built-in phase-gated workflows:

- **`praxis_os_upgrade_v1/`**: Framework upgrade workflow
- **`spec_creation_v1/`**: Feature specification creation
- **`spec_execution_v1/`**: Implementation of specifications

Each workflow includes:
- `metadata.json` - Workflow overview and phase definitions
- `phase-X/` directories with task breakdowns
- Phase validation gates and checkpoint requirements

### 4. **Installation System** (`installation/`)
Conversational installation process with 6 phases:
1. Clone source to temp directory
2. Create required directories
3. Copy universal standards and MCP server
4. Safe .cursorrules handling (won't overwrite)
5. Python venv setup + MCP configuration
6. Validation and cleanup

### 5. **Documentation Site** (`docs/`)
Docusaurus-based documentation with:
- Architecture deep-dives
- Installation guides
- MCP tools reference
- Standards overview
- React-based interactive diagrams

## 🔑 Key Design Principles

### **1. Dogfooding**
The repository uses its own framework for development:
- `.praxis-os/` contains a real installation (copied, not symlinked)
- Tests installation process every time framework is edited
- Catches consumer bugs before shipping

### **2. Dynamic Over Static**
- RAG retrieves standards dynamically (not hardcoded)
- Workflow content loaded on-demand
- Checkpoint requirements parsed from docs
- Framework generator creates compliant workflows

### **3. Phase Gating**
- Workflows enforce sequential execution
- Cannot access future phases without completing current
- Evidence required to advance phases
- Clear architectural boundaries

### **4. Portability**
- Self-contained installation per project
- No global dependencies
- Version pinning per project
- Language-agnostic universal standards

### **5. AI-First Design**
- `.cursorrules` provide behavioral triggers
- MCP tools designed for AI agent consumption
- Standards written for LLM comprehension
- Workflow tasks have explicit AI instructions

## 📊 Project Statistics

**Codebase Structure:**
- **Python MCP Server**: ~4,000+ lines (modular architecture)
- **Universal Standards**: 12 categories, 50+ documents
- **Workflows**: 3 built-in, extensible system
- **Tests**: Comprehensive unit + integration coverage
- **Documentation**: Full Docusaurus site

**Key Technologies:**
- **MCP**: Model Context Protocol for tool/resource exposure
- **LanceDB**: Vector database for semantic search
- **FastMCP**: Python MCP server framework
- **sentence-transformers**: Local embeddings (all-MiniLM-L6-v2)
- **Puppeteer**: Browser automation via Python
- **Docusaurus**: Documentation site generator

## 🚀 Current Capabilities

**For AI Agents:**
1. **Semantic Search**: Query standards via `search_standards` MCP tool
2. **Workflow Execution**: Start and progress through phase-gated workflows
3. **Browser Testing**: Automated browser interactions for validation
4. **Dynamic Generation**: Create new compliant workflows on-demand
5. **State Management**: Resume interrupted workflows

**For Developers:**
1. **Standards Repository**: Single source of truth for best practices
2. **Workflow Templates**: Proven patterns for common tasks
3. **Installation Automation**: Cursor agent handles setup
4. **Hot Reload**: File watcher updates RAG index automatically
5. **Version Control**: Per-project prAxIs OS version management

## 🎯 Project Maturity

**Strengths:**
- ✅ Comprehensive standards library (12 categories)
- ✅ Robust RAG implementation with fallbacks
- ✅ Working phase-gated workflow system
- ✅ Full dogfooding implementation
- ✅ Conversational installation
- ✅ Strong type safety (Sphinx docstrings, type hints)
- ✅ Thread-safe hot reload
- ✅ Comprehensive test coverage

**Notable Features:**
- Production-quality error handling throughout
- Extensive logging and debugging support
- Graceful degradation (RAG → grep fallback)
- Session recovery and cleanup
- Dynamic checkpoint validation
- Metadata-driven workflows

## 📈 Next Steps Recommendations

Based on the analysis, potential areas for enhancement:

1. **MCP Tool Expansion**: Add more specialized tools (code analysis, dependency management)
2. **Language Templates**: Pre-built language-specific workflow templates
3. **Observability**: Enhanced metrics and monitoring capabilities
4. **Sub-Agent System**: Fully implement specialized sub-agents referenced in docs
5. **Workflow Marketplace**: Community-contributed workflow library
6. **IDE Integration**: Deeper integration beyond Cursor

## 🎓 Conclusion

prAxIs OS is a **mature, well-architected framework** that successfully combines AI capabilities with software engineering best practices. The codebase demonstrates:

- **High Code Quality**: Comprehensive documentation, type safety, error handling
- **Thoughtful Design**: Dependency injection, phase gating, dynamic content loading
- **Production Ready**: Thread safety, graceful degradation, session management
- **Developer Experience**: Dogfooding, conversational installation, clear documentation

The project is **actively maintained** and follows its own standards, making it a compelling foundation for AI-augmented development workflows.
</result>
<task_progress>
- [x] Orient with prAxIs OS standards (MCP not available, proceeding with direct analysis)
- [x] Examine project structure and purpose
- [x] Analyze key components and architecture
- [x] Review documentation and standards structure
- [x] Identify MCP tools and workflows
- [x] Summarize findings
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
how would we integrate the local agent-os mcp server into cline, and the equivalent of the cursorrules to bootstrap the cline agent into it
</feedback>
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
universal/standards/ai-assistant/rag-content-authoring.md
universal/standards/ai-assistant/MCP-TOOLS-GUIDE.md

# Current Time
10/10/2025, 9:25:19 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
43,312 / 200K tokens used (22%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<read_file>
<path>installation/05-venv-mcp.md</path>
<task_progress>
- [x] Analyze current project
- [ ] Research Cline MCP integration
- [ ] Identify Cline behavior configuration
- [ ] Provide integration steps
- [ ] Create equivalent bootstrap instructions
</task_progress>
</read_file>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[read_file for 'installation/05-venv-mcp.md'] Result:
# Step 4: Python venv and MCP Configuration

**Previous**: `03-cursorrules.md` (handled .cursorrules)  
**Current**: Creating Python venv and configuring Cursor MCP  
**Next**: `05-validate.md`

---

## 🎯 What This Step Does

1. Create isolated Python virtual environment
2. Install MCP server dependencies
3. Create `.cursor/mcp.json` configuration file
4. Validate Python setup

**Why isolated venv**: Prevents prAxIs OS dependencies from conflicting with your project's dependencies.

**Time**: ~2-3 minutes

---

## 📦 Step 4.1: Create Python Virtual Environment

```python
import subprocess
import sys

# Create venv in .praxis-os/venv
print("📦 Creating Python virtual environment...")

result = subprocess.run([
    sys.executable, "-m", "venv", ".praxis-os/venv"
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Failed to create venv:")
    print(result.stderr)
    exit(1)

print("✅ Virtual environment created at .praxis-os/venv/")
```

---

## 📥 Step 4.2: Install MCP Server Dependencies

```python
import subprocess
import os

# Determine pip path based on platform
if os.name == "nt":  # Windows
    pip_path = ".praxis-os/venv/Scripts/pip"
else:  # Unix-like (Linux, macOS, WSL2)
    pip_path = ".praxis-os/venv/bin/pip"

print(f"📥 Installing MCP server dependencies...")

result = subprocess.run([
    pip_path, "install", 
    "-r", ".praxis-os/mcp_server/requirements.txt"
], capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Failed to install dependencies:")
    print(result.stderr)
    exit(1)

print("✅ Dependencies installed")
print(result.stdout)
```

---

## ✅ Validation Checkpoint #4A

Verify Python venv is working:

```python
import subprocess
import os

# Determine python path
if os.name == "nt":
    python_path = ".praxis-os/venv/Scripts/python.exe"
else:
    python_path = ".praxis-os/venv/bin/python"

# Test Python
result = subprocess.run([
    python_path, "--version"
], capture_output=True, text=True)

if result.returncode == 0:
    print(f"✅ Python venv working: {result.stdout.strip()}")
else:
    print("❌ Python venv not working")
    exit(1)

# Test module can be imported
result = subprocess.run([
    python_path, "-c", "import mcp_server"
], capture_output=True, text=True, 
   env={**os.environ, "PYTHONPATH": ".praxis-os"}
)

if result.returncode == 0:
    print("✅ MCP server module importable")
else:
    print("❌ Cannot import mcp_server:")
    print(result.stderr)
    exit(1)
```

---

## 🔧 Step 4.3: Create .cursor/mcp.json

⚠️ **CRITICAL**: Use `"mcp_server"` NOT `"mcp_server.praxis_os_rag"`!

```python
import json
import os

# Determine correct Python path for mcp.json
if os.name == "nt":
    # Windows native
    python_cmd = "${workspaceFolder}/.praxis-os/venv/Scripts/python.exe"
else:
    # Linux, macOS, WSL2
    python_cmd = "${workspaceFolder}/.praxis-os/venv/bin/python"

mcp_config = {
    "mcpServers": {
        "agent-os-rag": {
            "command": python_cmd,
            "args": ["-m", "mcp_server"],  # ← CORRECT module name!
            "env": {
                "PROJECT_ROOT": "${workspaceFolder}",
                "PYTHONPATH": "${workspaceFolder}/.praxis-os",
                "PYTHONUNBUFFERED": "1"
            },
            "autoApprove": [
                "search_standards",
                "get_current_phase",
                "get_workflow_state"
            ]
        }
    }
}

# Write mcp.json
with open(".cursor/mcp.json", "w") as f:
    json.dump(mcp_config, f, indent=2)

print("✅ .cursor/mcp.json created")
print(f"   Platform: {'Windows' if os.name == 'nt' else 'Unix-like'}")
print(f"   Python: {python_cmd}")
print("   Module: mcp_server")
```

---

## 📄 Verify mcp.json Content

Check that the file was created correctly:

```python
import json

# Read and verify
with open(".cursor/mcp.json", "r") as f:
    config = json.load(f)

# Critical checks
checks = {
    "agent-os-rag server configured": "agent-os-rag" in config.get("mcpServers", {}),
    "Module name is 'mcp_server'": config["mcpServers"]["agent-os-rag"]["args"][1] == "mcp_server",
    "PYTHONPATH is set": "PYTHONPATH" in config["mcpServers"]["agent-os-rag"]["env"],
}

all_passed = all(checks.values())

for check, passed in checks.items():
    print(f"{'✅' if passed else '❌'} {check}")

if not all_passed:
    print("\n❌ mcp.json configuration has issues!")
    exit(1)

print("\n✅ mcp.json configured correctly")
```

---

## 🔍 Manual Verification

You can manually check the mcp.json file:

```bash
cat .cursor/mcp.json
```

**Should look like this** (Linux/macOS/WSL2):
```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os",
        "PYTHONUNBUFFERED": "1"
      },
      "autoApprove": [
        "search_standards",
        "get_current_phase",
        "get_workflow_state"
      ]
    }
  }
}
```

**For Windows native**, the `command` should use `Scripts/python.exe` instead of `bin/python`.

---

## ✅ Validation Checkpoint #4B

Test that MCP server can start (don't worry if it complains about missing index, that's normal):

```python
import subprocess
import os
import time

# Determine python path
if os.name == "nt":
    python_path = ".praxis-os/venv/Scripts/python.exe"
else:
    python_path = ".praxis-os/venv/bin/python"

print("🧪 Testing MCP server startup...")

# Try to import and validate config
test_script = """
import sys
from pathlib import Path
sys.path.insert(0, '.praxis-os')

from mcp_server.config import ConfigLoader, ConfigValidator

config = ConfigLoader.load(Path('.praxis-os'))
errors = ConfigValidator.validate(config)

if errors:
    print('VALIDATION_FAILED')
    for error in errors:
        print(f'  {error}')
    sys.exit(1)
else:
    print('VALIDATION_PASSED')
"""

result = subprocess.run([
    python_path, "-c", test_script
], capture_output=True, text=True)

if "VALIDATION_PASSED" in result.stdout:
    print("✅ MCP server validation passed!")
else:
    print("❌ MCP server validation failed:")
    print(result.stdout)
    print(result.stderr)
    exit(1)
```

**Expected output**: `✅ MCP server validation passed!`

---

## 🚨 Troubleshooting

### Issue: "No module named 'venv'"

**Cause**: Python installation incomplete

**Fix**:
```bash
# Install python venv support (Ubuntu/Debian)
sudo apt-get install python3-venv

# Then retry venv creation
```

### Issue: "Permission denied" on venv creation

**Cause**: No write permission

**Fix**:
```bash
# Check permissions
ls -ld .praxis-os
# Should show write permission (w)
```

### Issue: Dependencies install fails

**Cause**: Network issue or missing dependencies

**Fix**:
```bash
# Retry with verbose output
.praxis-os/venv/bin/pip install -r .praxis-os/mcp_server/requirements.txt -v
```

### Issue: Config validation fails with "workflows_path does not exist"

**Cause**: You skipped step 01 or 02

**Fix**: Go back and ensure:
1. `.praxis-os/workflows/` directory exists (step 01)
2. Workflow files were copied (step 02)

---

## 📊 Progress Check

At this point you should have:
- ✅ Python venv at `.praxis-os/venv/`
- ✅ MCP server dependencies installed
- ✅ `.cursor/mcp.json` created with correct config
- ✅ Module name is `"mcp_server"` (not `"mcp_server.praxis_os_rag"`)
- ✅ Config validation passes
- ✅ All validation checkpoints passed

**If anything above is ❌, stop and fix before continuing.**

---

## 🎯 What's Next

You've set up the Python environment and Cursor configuration. Now for the final step:
1. Run comprehensive validation
2. **Clean up temp directory** (critical!)
3. Inform user of successful installation

**Next step**: Final validation and cleanup.

---

## ➡️ NEXT STEP

**Read file**: `installation/06-validate.md`

That file will:
1. Run comprehensive validation of entire installation
2. **Delete the temp directory** (clean up after ourselves!)
3. Provide user instructions for enabling MCP server
4. Declare installation complete

---

**Status**: Step 4 Complete ✅  
**Created**: Python venv + mcp.json  
**Next File**: `05-validate.md`  
**Step**: 5 of 5 (final step!)


<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
universal/standards/ai-assistant/rag-content-authoring.md
universal/standards/ai-assistant/MCP-TOOLS-GUIDE.md

# Current Time
10/10/2025, 9:25:27 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
43,551 / 200K tokens used (22%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<read_file>
<path>mcp_server/README.md</path>
<task_progress>
- [x] Analyze current project
- [ ] Research Cline MCP integration
- [ ] Identify Cline behavior configuration
- [ ] Provide integration steps
- [ ] Create equivalent bootstrap instructions
</task_progress>
</read_file>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[read_file for 'mcp_server/README.md'] Result:
# prAxIs OS MCP Server

**Model Context Protocol server for prAxIs OS with RAG, sub-agents, and workflow engine.**

## Components

### Core Server
- **`praxis_os_rag.py`**: Main MCP server entry point
- **`rag_engine.py`**: LanceDB vector search with semantic retrieval
- **`workflow_engine.py`**: Phase-gated workflows with checkpoint validation
- **`state_manager.py`**: Workflow state persistence

### Sub-Agents (Specialized Tools)
- **`sub_agents/design_validator.py`**: Adversarial design review agent
- **`sub_agents/concurrency_analyzer.py`**: Thread safety analysis agent
- **`sub_agents/architecture_critic.py`**: System design review agent
- **`sub_agents/test_generator.py`**: Systematic test creation agent

## Installation

This MCP server is copied to `.praxis-os/mcp_server/` in target projects during prAxIs OS installation.

## Dependencies

```txt
# MCP server dependencies
lancedb~=0.25.0          # Vector database
sentence-transformers>=2.0.0  # Local embeddings
mcp>=1.0.0               # Model Context Protocol
watchdog>=3.0.0          # File watching for hot reload
```

## Configuration

Configured in target project's `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "python",
      "args": ["${workspaceFolder}/.praxis-os/mcp_server/praxis_os_rag.py"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os"
      }
    }
  }
}
```

## Available Tools

### RAG Tools
- **`search_standards(query, n_results, filters)`**: Semantic search over standards
- **`start_workflow(workflow_type, target_file)`**: Initialize phase-gated workflow with complete overview
  - **NEW**: Returns `workflow_overview` with total phases, phase names, purposes, and deliverables
  - Eliminates need for separate `get_workflow_state()` call
  - See `WORKFLOW_METADATA_GUIDE.md` for details
- **`get_current_phase(session_id)`**: Get current phase requirements
- **`complete_phase(session_id, phase, evidence)`**: Submit evidence and advance
- **`get_workflow_state(session_id)`**: Query complete workflow state
- **`create_workflow(name, workflow_type, phases)`**: Generate new AI-assisted workflow frameworks
- **`current_date()`**: Get current date/time in ISO 8601 format (prevents AI date errors)

### Sub-Agent Tools
- **`validate_design(spec, target_domain)`**: Adversarial design review
- **`analyze_concurrency(code_snippet, language)`**: Thread safety analysis
- **`critique_architecture(design_doc)`**: System design review
- **`generate_tests(target_code, framework)`**: Systematic test generation

## Observability Integration (Optional)

The MCP server has no-op observability hooks by default. To add tracing:

**See `observability-integration.md` for detailed instructions on adding:**
- HoneyHive (AI-specific observability)
- OpenTelemetry (universal observability)
- Other platforms

User can request: "Add HoneyHive tracing" and you (Cursor agent) follow the guide.

## Version History

See `CHANGELOG.md` for version history and updates.

## Development

To modify the MCP server:
1. Make changes in `praxis-os/mcp_server/`
2. Test in a sample project
3. Update `CHANGELOG.md`
4. Tag release (semver)
5. Users update via: "Update prAxIs OS to latest version"

---

**Note:** The actual MCP server implementation files should be copied from the HoneyHive Python SDK's `.praxis-os/mcp_server/` directory. This README serves as documentation for the structure.

<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
universal/standards/ai-assistant/rag-content-authoring.md
universal/standards/ai-assistant/MCP-TOOLS-GUIDE.md

# Current Time
10/10/2025, 9:25:34 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
46,574 / 200K tokens used (23%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<web_fetch>
<url>https://github.com/cline/cline</url>
<task_progress>
- [x] Analyze current project
- [ ] Research Cline MCP integration
- [ ] Identify Cline behavior configuration
- [ ] Provide integration steps
- [ ] Create equivalent bootstrap instructions
</task_progress>
</web_fetch>

---

**User:**

[web_fetch for 'https://github.com/cline/cline'] Result:
Fetched Markdown for https://github.com/cline/cline:

                  GitHub - cline/cline: Autonomous coding agent right in your IDE, capable of creating/editing files, executing commands, using the browser, and more with your permission every step of the way.                                             

[Skip to content](#start-of-content) 

You signed in with another tab or window. Reload to refresh your session. You signed out in another tab or window. Reload to refresh your session. You switched accounts on another tab or window. Reload to refresh your session. Dismiss alert

[cline](/cline) / **[cline](/cline/cline)** Public

*   [Notifications](/login?return_to=%2Fcline%2Fcline) You must be signed in to change notification settings
*   [Fork 7.3k](/login?return_to=%2Fcline%2Fcline)
*   [Star 51.2k](/login?return_to=%2Fcline%2Fcline)
    

Autonomous coding agent right in your IDE, capable of creating/editing files, executing commands, using the browser, and more with your permission every step of the way.

[marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev "https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev")

### License

[Apache-2.0 license](/cline/cline/blob/main/LICENSE)

[51.2k stars](/cline/cline/stargazers) [7.3k forks](/cline/cline/forks) [Branches](/cline/cline/branches) [Tags](/cline/cline/tags) [Activity](/cline/cline/activity)

[Star](/login?return_to=%2Fcline%2Fcline)

[Notifications](/login?return_to=%2Fcline%2Fcline) You must be signed in to change notification settings

cline/cline
===========

 main

[**939** Branches](/cline/cline/branches)[**187** Tags](/cline/cline/tags)

[](/cline/cline/branches)[](/cline/cline/tags)

Go to file

Code

Open more actions menu

Folders and files
-----------------

Name

Name

Last commit message

Last commit date

Latest commit
-------------

![arafatkatze](https://avatars.githubusercontent.com/u/11155207?v=4&size=40)![pashpashpash](https://avatars.githubusercontent.com/u/20898225?v=4&size=40)

[arafatkatze](/cline/cline/commits?author=arafatkatze)

and

[pashpashpash](/cline/cline/commits?author=pashpashpash)

[Fix CLI installation script (](/cline/cline/commit/0858ff517af6243427a45ee175f76abd596291ce)[#6760](https://github.com/cline/cline/pull/6760)[)](/cline/cline/commit/0858ff517af6243427a45ee175f76abd596291ce)

Open commit detailssuccess

Oct 10, 2025

[0858ff5](/cline/cline/commit/0858ff517af6243427a45ee175f76abd596291ce) · Oct 10, 2025

History
-------

[3,707 Commits](/cline/cline/commits/main/)

Open commit details

[](/cline/cline/commits/main/)

[.changeset](/cline/cline/tree/main/.changeset ".changeset")

[.changeset](/cline/cline/tree/main/.changeset ".changeset")

[CLI Auth Wizard 🧙 (](/cline/cline/commit/a670c1efa2a84bea70e9c74ffdedcde94f12675d "CLI Auth Wizard 🧙 (#6742)
* CLI auth wizard
Default Cline model, better menu UX, display active provider and model at main menu
Model switcher for BYO providers
Provider switching, UI changes
List configured providers now shows all providers user has configured
Added remove provider feature
Changes to model picker for BYO providers
Model fetch filtering tweaks
Only update model fields for provider when possible
Consolidated provider field mapping
Change to not set provider as active when updating model
Dont set Cline as active provider when setting Cline model
Added model fetching for OpenAI provider (req API key)
Added model fetching for Ollama provider
Added support for model listing from providers.go for models without remote fetch
Moved auth specific code out of manager
Bedrock fields, OpenAI Native BaseURL
More graceful fetch failure
Fixed auth callback issue
* Added model list feature for AWS
AWS - Profile only support in CLI for now, UX changes (WIP
Remove Save and Exit option
Auto enable filtering/search in model lists
Added cancel option for some menus")[#6742](https://github.com/cline/cline/pull/6742)[)](/cline/cline/commit/a670c1efa2a84bea70e9c74ffdedcde94f12675d "CLI Auth Wizard 🧙 (#6742)
* CLI auth wizard
Default Cline model, better menu UX, display active provider and model at main menu
Model switcher for BYO providers
Provider switching, UI changes
List configured providers now shows all providers user has configured
Added remove provider feature
Changes to model picker for BYO providers
Model fetch filtering tweaks
Only update model fields for provider when possible
Consolidated provider field mapping
Change to not set provider as active when updating model
Dont set Cline as active provider when setting Cline model
Added model fetching for OpenAI provider (req API key)
Added model fetching for Ollama provider
Added support for model listing from providers.go for models without remote fetch
Moved auth specific code out of manager
Bedrock fields, OpenAI Native BaseURL
More graceful fetch failure
Fixed auth callback issue
* Added model list feature for AWS
AWS - Profile only support in CLI for now, UX changes (WIP
Remove Save and Exit option
Auto enable filtering/search in model lists
Added cancel option for some menus")

Oct 10, 2025

[.clinerules](/cline/cline/tree/main/.clinerules ".clinerules")

[.clinerules](/cline/cline/tree/main/.clinerules ".clinerules")

[Improved git branch analysis workflow (](/cline/cline/commit/e6b00527ed0085d7081aaa82cff4b437a7bdcd8b "Improved git branch analysis workflow (#5602)
Co-authored-by: Kevin Bond <kevin@Mac.hsd1.ca.comcast.net>")[#5602](https://github.com/cline/cline/pull/5602)[)](/cline/cline/commit/e6b00527ed0085d7081aaa82cff4b437a7bdcd8b "Improved git branch analysis workflow (#5602)
Co-authored-by: Kevin Bond <kevin@Mac.hsd1.ca.comcast.net>")

Aug 15, 2025

[.github](/cline/cline/tree/main/.github ".github")

[.github](/cline/cline/tree/main/.github ".github")

[Standalone CLI Installation (](/cline/cline/commit/3472e6068c8f9f1a2b2172659608b972cffe7518 "Standalone CLI Installation  (#6689)
* Phase 1 download node binary
* Phase 2 include cli binaries
* Phase 3 add scripts
* Phase 4 bug fix
* Phase 5: adding install script
* Phase 6: pushing github actions
* Phase 7: fixing redundancy
* Phase 7: fixing redundancy
* Temporary commit for workspace stuff
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Adding JB fixes
* Adding JB fixes
* Adding CLI-JB fixes
* Refactor
* Refactor
* refactor
* Update release-standalone.yml
Remove VSCode packaging env vars from CLI workflow.
---------
Co-authored-by: Sarah Fortune <sarah.fortune@gmail.com>")[#6689](https://github.com/cline/cline/pull/6689)[)](/cline/cline/commit/3472e6068c8f9f1a2b2172659608b972cffe7518 "Standalone CLI Installation  (#6689)
* Phase 1 download node binary
* Phase 2 include cli binaries
* Phase 3 add scripts
* Phase 4 bug fix
* Phase 5: adding install script
* Phase 6: pushing github actions
* Phase 7: fixing redundancy
* Phase 7: fixing redundancy
* Temporary commit for workspace stuff
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Fix tests
* Adding JB fixes
* Adding JB fixes
* Adding CLI-JB fixes
* Refactor
* Refactor
* refactor
* Update release-standalone.yml
Remove VSCode packaging env vars from CLI workflow.
---------
Co-authored-by: Sarah Fortune <sarah.fortune@gmail.com>")

Oct 10, 2025

[.husky](/cline/cline/tree/main/.husky ".husky")

[.husky](/cline/cline/tree/main/.husky ".husky")

[Remove --no-stash flag from lint-staged in pre-commit hook (](/cline/cline/commit/60ddf80e5c8f5e0f2cf7b00778feaaa668781f2d "Remove --no-stash flag from lint-staged in pre-commit hook (#6188)
### Problem
The `--no-stash` flag was originally added to work around issues where teammates hadn't installed Biome after our migration from Prettier. When the formatter failed, lint-staged's default stashing behavior would remove staged changes, causing frustration.
However, this workaround now causes a different problem: lint-staged runs formatters on files containing both staged AND unstaged changes. When Biome formats these files, it inadvertently stages unstaged modifications, effectively merging work-in-progress changes into commits.
### Solution
Remove the `--no-stash` flag to restore lint-staged's default behavior:
- Stash unstaged changes before running formatters
- Run formatters only on staged content
