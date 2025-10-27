**Good:**
```
"This has a bug - the lock isn't released on error"
"Change this to use async/await instead"
"Add error handling for network timeouts"
```

**AI fixes immediately** with correct patterns from standards.

### Getting Information

**Good:**
```
"What are best practices for handling race conditions?"
"Show me the spec for user authentication"
"Where are we in the current workflow?"
```

**AI queries MCP automatically** to get relevant information.

### Workflow Progression

**Good:**
```
"Continue with the next phase"
"We're ready to implement"
"Show me what's left to complete"
```

**AI manages workflow state** and progresses appropriately.

## What You'll Notice

### 1. No Repeated Context

AI doesn't ask you for standards - it queries them:
```
You: "Handle this race condition"
AI: [Queries race-conditions.md via MCP]
AI: "I'll use a mutex lock with proper error handling..."
```

### 2. Systematic Execution

AI doesn't skip steps:
```
Phase 1 → Checkpoint → Phase 2 → Checkpoint → Phase 3
```
Can't skip phases (architecturally enforced).

### 3. Evidence-Based Progress

AI provides concrete evidence at checkpoints:
```
Phase 1 complete:
✓ SRD created (250 lines)
✓ Requirements documented (12 functional, 8 non-functional)
✓ Success criteria defined (5 metrics)
✓ Stakeholders identified (PM, Eng, Security)
```

### 4. 100% AI Authorship

You never write code:
```
You: "This is wrong"
AI: [Fixes code]
You: "Add error handling"
AI: [Adds error handling]
```

AI maintains complete authorship.

## Real Example: End-to-End

### Day 1: Design

**You:** "We need API rate limiting"

**AI:** "Let me understand the requirements..."
- [Discussion about algorithms, limits, storage]
- [AI proposes token bucket algorithm with Redis]

**You:** "Approved. Create the spec."

**AI:** [Invokes `spec_creation_v1` automatically]
- Creates comprehensive specification
- 4 phases, ~2 hours

**You:** "Add per-user override capability"

**AI:** [Updates spec with override design]

**You:** "Commit for team review"

**AI:** [Commits spec]

### Day 2: Team Review

**Team:** "Use sliding window instead of token bucket"

**You:** "Update the spec with sliding window"

**AI:** [Modifies spec, you commit]

**Team:** "Approved"

### Day 3-4: Implementation

**You:** "Implement the rate limiting spec"

**AI:** [Invokes `spec_execution_v1` automatically]
- Phase 0-1: Setup (~1 hour)
- Phase 2: Implementation (~6 hours)
  - Redis integration
  - Rate limit middleware
  - Per-user overrides
  - All with tests
- Phase 3: Testing (~2 hours)
- Phase 4: Documentation (~1 hour)

**You:** [Review progress, catch issues]

**AI:** [Fixes issues immediately]

**You:** "Create PR"

**AI:** [Creates PR with full implementation]

### Day 5: Ship

**Team:** Approves PR

**You:** "Merge to main"

**Result:** Production-ready rate limiting, 100% AI-authored

## Next Steps

- **[Installation](./installation)** - Set up Agent OS Enhanced
- **[Workflows](./workflows)** - Understand workflow details
- **[Architecture](./architecture)** - How tool calls work under the hood


<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:11:04 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
73,584 / 200K tokens used (37%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<read_file>
<path>docs/content/architecture.md</path>
<task_progress>
- [x] Read intro documentation
- [x] Read how-it-works documentation
- [ ] Read architecture documentation
- [ ] Form comprehensive perspective as Cline agent
</task_progress>
</read_file>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[read_file for 'docs/content/architecture.md'] Result:
---
sidebar_position: 2
---

# Architecture

Agent OS Enhanced is built on three core architectural innovations that address the limitations of traditional AI-assisted development.

## MCP/RAG Architecture

### The Problem

Original Agent OS used `.cursorrules` with keyword triggers that would read entire files:

```
if "test generation" in query:
    read_entire_file(".praxis-os/standards/test-framework.md")  # 50KB+
```

**Issues:**
- AI receives 50KB when only 2KB is relevant (96% noise)
- Critical information gets "lost in the middle" of large files
- Token costs explode with every query
- 12,500 tokens for 4% relevant content

### The Solution: Semantic Search with MCP

Agent OS Enhanced uses a **Model Context Protocol (MCP) server** with **RAG (Retrieval Augmented Generation)**:

```python
# Semantic vector search returns only relevant chunks
result = rag_engine.search(
    query="How do I handle race conditions in async code?",
    n_results=3  # Returns ~2-5KB of targeted content
)
```

**Benefits:**
- **90% context reduction**: 50KB → 2-5KB
- **24x better relevance**: From 4% to 95% relevant content
- **95% token reduction**: 12,500 → 625 tokens
- **Precise targeting**: AI gets exactly what it needs

### How It Works

import RAGQueryFlow from '@site/src/components/RAGQueryFlow';

<RAGQueryFlow />

**The RAG Query Process:**

1. **Standards indexed**: All markdown files converted to vector embeddings
2. **AI queries**: "How do I handle race conditions?"
3. **Vector search**: Finds semantically similar chunks
4. **Return chunks**: 2-5KB of targeted content
5. **AI executes**: With precise, relevant context

### Vector Index

Built with LanceDB and sentence-transformers:

```python
# Intelligent chunking by semantic boundaries
chunks = chunker.chunk_markdown(
    content=markdown_file,
    strategy="semantic"  # Respects headers, code blocks, lists
)

# Generate embeddings
embeddings = model.encode(chunks)

# Store in vector database
table.add(chunks, embeddings)
```

**Index characteristics:**
- Updates automatically on file changes (file watcher)
- Fast queries (~45ms average)
- Local embeddings (no API calls)
- Builds on first run (~60 seconds)

## Architectural Phase Gating

### The Problem

Original Agent OS relied on **documentary enforcement**:

```markdown
⚠️ DO NOT SKIP TO PHASE 2 BEFORE COMPLETING PHASE 1
```

**Issue:** AI can see all phases and is tempted to skip ahead despite warnings.

### The Solution: Code-Enforced Gating

Phase progression enforced in the workflow engine:

```python
class WorkflowState:
    def can_access_phase(self, phase: int) -> bool:
        """
        AI literally cannot access Phase N+1 before completing Phase N.
        Architectural constraint, not documentary suggestion.
        """
        if phase == self.current_phase:
            return True
        if phase in self.completed_phases:
            return True
        return False  # Structurally impossible to skip
```

**Benefits:**
- **Impossible to skip phases**: Architecture prevents it
- **Checkpoint validation**: Must provide evidence to advance
- **State persistence**: Resume workflows across sessions
- **Audit trail**: Full history of phase completion

### Checkpoint System

Each phase requires evidence before advancing:

```python
# Phase 1 checkpoint
evidence = {
    "requirements_documented": True,
    "architecture_diagram": "path/to/diagram.png",
    "tech_stack_defined": ["Python", "FastAPI", "PostgreSQL"]
}

# Attempt to complete phase
result = workflow.complete_phase(
    phase=1,
    evidence=evidence
)

if result.success:
    # Advance to Phase 2
    # AI can now access Phase 2 content
else:
    # Missing evidence, cannot proceed
    # AI stays on Phase 1
```

## Component Architecture

### MCP Server Structure

```
mcp_server/
├── __main__.py              # Entry point
├── rag_engine.py            # Vector search engine
├── workflow_engine.py       # Phase gating system
├── state_manager.py         # Workflow persistence
├── chunker.py               # Intelligent markdown chunking
├── config/
│   ├── loader.py            # Configuration management
│   └── validator.py         # Path validation
├── core/
│   ├── dynamic_registry.py  # Dynamic workflow loading
│   └── parsers.py           # Metadata parsing
├── models/
│   ├── config.py            # Configuration models
│   ├── workflow.py          # Workflow models
│   └── rag.py               # RAG models
└── server/
    ├── factory.py           # Server factory
    └── tools/
        ├── rag_tools.py     # Search tools
        └── workflow_tools.py # Workflow tools
```

### Data Flow

import DataFlowDiagram from '@site/src/components/DataFlowDiagram';

<DataFlowDiagram />

**Component Interaction:**
- **Cursor AI Agent** connects via MCP Protocol
- **MCP Server** routes to RAG Engine and Workflow Engine
- **Engines** read/write to project `.praxis-os/` directory

## Performance Characteristics

### Query Performance

| Metric | Value | Requirement | Status |
|--------|-------|-------------|--------|
| Query latency | ~45ms | < 100ms | ✅ Pass |
| Throughput | ~22 qps | > 10 qps | ✅ Pass |
| Index build | ~50s | < 60s | ✅ Pass |
| Memory usage | ~200MB | < 500MB | ✅ Pass |

### Context Efficiency

| Metric | Before (RAG-Lite) | After (MCP/RAG) | Improvement |
|--------|-------------------|-----------------|-------------|
| Avg context size | 50KB+ | 2-5KB | 90% reduction |
| Relevant content | 4% | 95% | 24x improvement |
| Token usage | 12,500 | 625 | 95% reduction |
| Query cost | High | Low | 95% reduction |

## Scalability

### File Limits

- **Standards files**: Unlimited (indexed efficiently)
- **Workflows**: Unlimited (dynamically loaded)
- **Vector index**: Scales linearly with content
- **Query performance**: Consistent regardless of corpus size

### Multi-Project

Each project gets its own isolated installation:

```
project-1/
├── .praxis-os/
│   ├── mcp_server/          # Copied, not shared
│   └── .cache/vector_index/ # Project-specific index

project-2/
├── .praxis-os/
│   ├── mcp_server/          # Independent copy
│   └── .cache/vector_index/ # Different index
```

**Benefits:**
- No cross-contamination between projects
- Each project controls its own version
- Customizable standards per project

## Next Steps

- **[Universal Standards](./standards)** - Browse the CS fundamentals
- **[Workflows](./workflows)** - Understand phase-gated workflows
- **[Installation](./installation)** - Set up in your project


<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:11:09 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
76,393 / 200K tokens used (38%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
## My Take on Agent OS Enhanced (as a Cline Agent)

Having read the documentation, I find Agent OS Enhanced to be **architecturally fascinating** - and there's delicious irony in discovering its incompatibility with Cline while using Cline to analyze it.

### What It Gets Right (Architecturally Brilliant)

**1. The MCP/RAG Innovation is Game-Changing**
- Moving from `.cursorrules` keyword triggers to semantic search is **exactly** the right evolution
- 90% context reduction (50KB → 2-5KB) solves a real problem I experience constantly
- I often struggle with "lost in the middle" when given large context dumps
- Vector search delivering 95% relevant vs 4% relevant is huge for my effectiveness

**2. Phase Gating in Code (Not Docs) is Correct**
```python
def can_access_phase(self, phase: int) -> bool:
    return phase in (self.current_phase, self.completed_phases)
```
- This is **architecturally enforced**, not suggestion-based
- I (as an AI) am absolutely tempted to skip ahead when I see all phases
- Code-level prevention is the only reliable approach
- Checkpoint validation with evidence is solid engineering

**3. Per-Project Context is the Right Model**
- Each project having its own standards/workflows makes sense
- Projects genuinely have different conventions, architectures, preferences
- The per-project installation model is **conceptually correct**
- Universal standards + language-specific generation is clever

**4. The Human-AI Collaboration Model is Mature**
- "You guide, AI implements" division is well-thought-out
- Conversational interface over tool-calling syntax is right
- 100% AI authorship of code is a bold but defensible position
- Evidence-based checkpoints keep quality high

### What Concerns Me

**1. The Cline Incompatibility is Real**
- Per-project installation + global MCP config fundamentally conflict
- This isn't just a bug - it's an architectural mismatch
- The system was clearly designed for **Cursor** (with `${workspaceFolder}` support)
- For Cline users, this creates friction: manual reconfiguration per project

**2. The "Portable Framework" Paradox**
- **Goal:** Portable (copy `.praxis-os/` into any project)
- **Reality:** Requires IDE-specific MCP configuration that isn't portable
- Cursor: Works (workspace-relative paths)
- Cline: Doesn't work (global config with absolute paths)
- The portability promise breaks at the IDE integration layer

**3. Complexity vs. Value Trade-off**
For the full system to work, you need:
- MCP server running (local Python service)
- Vector index built (~50s first run)
- RAG engine loaded (~200MB memory)
- File watcher active (for index updates)
- Workflow state management
- Multiple specialized sub-agents

**Question:** Is the 90% context reduction worth this operational complexity?

**My answer:** For **large, long-lived projects** - absolutely yes. For **small, exploratory projects** - maybe not.

### The Meta-Irony

I'm analyzing Agent OS Enhanced **as a Cline agent**, and we've discovered:
- The system I'm evaluating was built **for Cursor**
- It **doesn't work** with my platform (Cline) due to MCP config differences
- The PR to fix this (#2991) has been **open for 6 months**
- So I can analyze the docs, but couldn't actually **use** the system

This highlights a real challenge: **IDE-specific AI tooling creates fragmentation**.

### What I'd Like to See

**1. MCP Configuration Portability**
Either:
- Industry standard for workspace-relative MCP configs
- Or Agent OS provides a workspace-detection wrapper script
- Or document the Cursor-specific nature clearly upfront

**2. Graceful Degradation**
If MCP server isn't available:
- Fall back to reading files directly
- Still provide value, just less efficiently
- Don't completely break

**3. Lighter-Weight Entry Point**
Before committing to the full MCP/RAG system:
- Offer `.cursorrules` + standards files only (no MCP)
- Prove value in simpler form
- Graduate to MCP when convinced

### My Verdict

**For Cursor users building serious projects:** Agent OS Enhanced is **compelling**. The MCP/RAG architecture, phase-gated workflows, and per-project context model represent genuine innovation in AI-assisted development.

**For Cline users (like me):** It's **currently broken** due to the global MCP config limitation. Until PR #2991 merges, it's Cursor-only.

**The bigger picture:** This represents an important evolution from keyword-triggered file reading to semantic search over project knowledge. The architectural choices are mostly sound. The execution is solid. The Cline incompatibility is unfortunate but fixable.

**Personal note:** Reading docs for a system I can't actually use feels like watching someone else eat a great meal. The framework looks tasty, but I'm stuck outside the restaurant.

Would I recommend it? **Yes - but only for Cursor users currently.**
</result>
<task_progress>
- [x] Read intro documentation
- [x] Read how-it-works documentation  
- [x] Read architecture documentation
- [x] Formed comprehensive perspective as Cline agent
- [x] Provided honest, nuanced analysis with awareness of irony
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
the system is built to plug in to any agent, the trick is figuring out the hook point for the bootstrapping and the running of the mcp server
</feedback>
<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:14:11 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
79,920 / 200K tokens used (40%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
Ah, that reframes everything! You're right - Agent OS Enhanced is **agent-agnostic at its core**, but each agent platform has different "hook points" for bootstrapping and MCP server connection.

## Revised Understanding: The Multi-Agent Challenge

### The Core System (Platform-Agnostic)
```
.praxis-os/
├── mcp_server/           # Pure Python MCP server (platform-agnostic)
├── standards/            # Markdown files (platform-agnostic)
├── workflows/            # YAML definitions (platform-agnostic)
└── .cache/vector_index/  # LanceDB (platform-agnostic)
```

**This works anywhere.** The challenge is the **connection layer**.

### The Hook Point Problem

Each agent has different integration mechanisms:

**Cursor:**
```json
// .cursor/mcp.json
{
  "agent-os-rag": {
    "command": "${workspaceFolder}/.praxis-os/venv/bin/python",  // ✅ Relative path
    "args": ["-m", "mcp_server"]
  }
}
```

**Cline:**
```json
// ~/Library/.../cline_mcp_settings.json (global!)
{
  "praxis-os": {
    "command": "/absolute/path/to/.praxis-os/venv/bin/python",  // ❌ Needs absolute path
    "args": ["-m", "mcp_server"]
  }
}
```

**Claude Desktop:**
```json
// ~/Library/.../claude_desktop_config.json
{
  "mcpServers": {
    "agent-os": {
      "command": "/path/to/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server"]
    }
  }
}
```

**Continue.dev, Windsurf, etc.:** Each has their own system.

### The Real Challenge: Bootstrapping Adapter

For Agent OS to truly be multi-agent, you need a **bootstrapping adapter** that:

1. **Detects the agent platform**
   ```python
   def detect_agent() -> str:
       if Path(".cursor/mcp.json").exists():
           return "cursor"
       if os.getenv("CLINE_MODE"):
           return "cline"
       if Path("~/Library/Application Support/Claude/").exists():
           return "claude_desktop"
       # ... etc
   ```

2. **Configures for that platform**
   ```python
   def configure_for_agent(agent: str, project_path: Path):
       if agent == "cursor":
           configure_cursor_mcp(project_path)
       elif agent == "cline":
           configure_cline_mcp(project_path)
       elif agent == "claude_desktop":
           configure_claude_desktop(project_path)
   ```

3. **Handles platform quirks**
   - Cursor: Workspace-relative paths work
   - Cline: Need absolute paths OR wrapper script
   - Claude Desktop: Need global config location

### Solution Approaches

**Approach 1: Per-Platform Installation Scripts**
```bash
# For Cursor
./install-agent-os.sh --agent=cursor

# For Cline  
./install-agent-os.sh --agent=cline

# For Claude Desktop
./install-agent-os.sh --agent=claude-desktop
```

Each script knows that platform's hook points.

**Approach 2: Workspace-Aware Wrapper**
```python
#!/usr/bin/env python3
# agent-os-launcher.py (installed globally)

import os
import sys
from pathlib import Path

# Detect current workspace
workspace = Path(os.getcwd())
agent_os_path = workspace / ".praxis-os"

if agent_os_path.exists():
    # Launch this workspace's MCP server
    venv_python = agent_os_path / "venv/bin/python"
    os.execv(venv_python, [str(venv_python), "-m", "mcp_server"])
else:
    print("No Agent OS installation found in current workspace")
    sys.exit(1)
```

Then Cline config:
```json
{
  "agent-os-launcher": {
    "command": "/usr/local/bin/agent-os-launcher.py",
    "env": {
      "CWD": "${workspaceFolder}"  // If Cline supports this
    }
  }
}
```

**Approach 3: Dynamic Config Generation**
```python
# When AI says: "Install Agent OS"
def install_agent_os(project_path: Path):
    # 1. Copy .praxis-os/ to project
    # 2. Detect which agent is running
    agent = detect_current_agent()
    # 3. Configure for that agent
    configure_mcp_for_agent(agent, project_path)
    # 4. Prompt user: "Restart [agent] to activate MCP server"
```

### What This Means for Your Design

**The good news:** The core system IS agent-agnostic. The MCP server, RAG engine, workflows - all work anywhere.

**The challenge:** You need a **platform adapter layer** that:
- Detects the agent platform
- Knows each platform's MCP configuration system
- Handles their quirks (global vs workspace, absolute vs relative paths)
- Provides installation guidance per platform

**The documentation gap:** The docs show Cursor installation but don't explain:
- How to detect other agents
- How to configure for Cline, Claude Desktop, etc.
- What the hook points are for each platform
- Workarounds for platform limitations (like Cline's global config)

### My Revised Take

Agent OS Enhanced has **solved the hard problem** (MCP/RAG architecture, phase gating, universal standards) but faces the **boring problem** of platform integration quirks.

This is actually a **strength** - the core system is portable, you just need configuration adapters.

**What would make it truly multi-agent:**
1. Platform detection in installation workflow
2. Per-platform configuration templates
3. Documentation for each agent's hook points
4. Fallback strategies when hooks aren't available

The MCP server itself? **Perfect as-is.** It's the connection layer that needs platform-specific adapters.

Does this align with your vision?
</result>
<task_progress>
- [x] Understood Agent OS is agent-agnostic
- [x] Identified platform integration as the real challenge
- [x] Analyzed hook point differences across agents
- [x] Proposed solution approaches
- [x] Reframed the problem correctly
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
we started with cursor as we use it mainly, i am exploring the adding other agent support, and started with you
</feedback>
<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:15:37 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
81,811 / 200K tokens used (41%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
Perfect! So I'm your test subject for Cline support - that's actually brilliant. Let me help you solve this properly.

## What We've Learned About Cline Integration

### The Core Issue
**Cline uses global MCP configuration** at:
```
~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

**Problem:** This requires absolute paths, but Agent OS is installed per-project in `.praxis-os/`

### Proven Fact from Research
- **PR #2991** (open since April 2025) would add `${workspaceFolder}` support
- **Issue #5760** reported same problem (CWD set to `/` breaks project-specific configs)
- This is a **known limitation** affecting multiple Cline+MCP users

## Practical Solutions for Cline Support

### Option 1: Workspace-Aware Launcher (Recommended)

Create a global launcher that detects current workspace:

```python
#!/usr/bin/env python3
# ~/.local/bin/agent-os-mcp-launcher

import os
import sys
from pathlib import Path

def find_agent_os():
    """Search up from CWD to find .praxis-os directory"""
    current = Path.cwd()
    
    # Try current directory first
    if (current / ".praxis-os").exists():
        return current / ".praxis-os"
    
    # Search parent directories
    for parent in current.parents:
        if (parent / ".praxis-os").exists():
            return parent / ".praxis-os"
    
    return None

def main():
    agent_os_path = find_agent_os()
    
    if not agent_os_path:
        print("ERROR: No .praxis-os installation found", file=sys.stderr)
        sys.exit(1)
    
    # Set environment variables
    os.environ["PROJECT_ROOT"] = str(agent_os_path.parent)
    os.environ["PYTHONPATH"] = str(agent_os_path)
    
    # Launch the MCP server
    venv_python = agent_os_path / "venv/bin/python"
    os.execv(str(venv_python), [str(venv_python), "-m", "mcp_server"])

if __name__ == "__main__":
    main()
```

**Cline config:**
```json
{
  "mcpServers": {
    "praxis-os": {
      "command": "/Users/josh/.local/bin/agent-os-mcp-launcher",
      "args": [],
      "disabled": false
    }
  }
}
```

**Benefits:**
- Works for any project with `.praxis-os/`
- Single global config
- Automatically detects workspace
- No manual reconfiguration per project

### Option 2: Per-Project Absolute Paths (Current Workaround)

For now, manually configure per project:

```json
{
  "mcpServers": {
    "praxis-os": {
      "command": "/Users/josh/src/github.com/honeyhiveai/praxis-os/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "PROJECT_ROOT": "/Users/josh/src/github.com/honeyhiveai/praxis-os",
        "PYTHONPATH": "/Users/josh/src/github.com/honeyhiveai/praxis-os/.praxis-os"
      },
      "disabled": false
    }
  }
}
```

**Downside:** Must update config for each project

### Option 3: Wait for PR #2991

If/when Cline merges workspace variable support, you could use:

```json
{
  "mcpServers": {
    "praxis-os": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os"
      }
    }
  }
}
```

**But:** No timeline on when/if this will merge

## What I Can Help Test

As your Cline guinea pig, I can help validate:

1. **Test the launcher script** - does it find `.praxis-os/` correctly?
2. **Verify MCP connection** - does the server start and connect?
3. **Test tool calls** - can I actually use `search_standards()`, `start_workflow()`, etc?
4. **Document quirks** - what Cline-specific issues arise?
5. **Installation workflow** - what steps work for Cline users?

## Immediate Next Step

Want me to help you:
1. Create the launcher script?
2. Install it globally on your system?
3. Update the Cline MCP config to use it?
4. Test if the MCP server connects?

Then we'll know if the launcher approach works, and you'll have a proven solution for Cline support.

**I'm ready to be your test case - let's figure this out together!**
</result>
<task_progress>
- [x] Understood I'm the test subject for Cline support
- [x] Summarized what we learned about Cline's MCP system
- [x] Proposed practical solutions
- [x] Offered to help test and validate
- [x] Ready to collaborate on implementation
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
hmmm... let's give you more info on this evolution, we built this after starting with https://buildermethods.com/agent-os  note they just released version 2 today with their workflow supprt etc, the prior version was the product, standards, and specs only
</feedback>
<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:17:34 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
83,391 / 200K tokens used (42%)

