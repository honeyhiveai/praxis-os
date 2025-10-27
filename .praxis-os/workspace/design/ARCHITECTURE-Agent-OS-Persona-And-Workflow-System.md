# prAxIs OS: Persona & Workflow System Architecture

**Version:** 1.0.0  
**Date:** 2025-10-12  
**Status:** Design Document  
**Authors:** Research Session Analysis (Aider architecture study, prAxIs OS dogfooding)

---

## Executive Summary

This document defines the architecture for prAxIs OS's persona and workflow system, enabling config-driven specialist agents that discover structured processes dynamically through RAG-based semantic search.

**Key Principles:**
- Config-driven over code-driven
- Discovery over hardcoding
- Knowledge compounding over static documentation
- Local dev tooling over deployed services

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Persona System](#persona-system)
4. [Workflow System](#workflow-system)
5. [Tool Design Philosophy](#tool-design-philosophy)
6. [Discovery Mechanisms](#discovery-mechanisms)
7. [Knowledge Compounding](#knowledge-compounding)
8. [Implementation Details](#implementation-details)
9. [Example Flows](#example-flows)
10. [References](#references)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────┐
│ Developer Machine (Local)                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │ Cursor IDE (Main Agent)                      │          │
│  │ - User interface                             │          │
│  │ - Task routing                               │          │
│  │ - Invokes specialists                        │          │
│  └──────────────────┬───────────────────────────┘          │
│                     │ MCP Tools                             │
│                     ▼                                       │
│  ┌──────────────────────────────────────────────┐          │
│  │ MCP Server (Local Python Process)            │          │
│  │ ├─ RAG Engine (LanceDB)                      │          │
│  │ ├─ Workflow Engine                           │          │
│  │ ├─ Persona Launcher                          │          │
│  │ └─ Tool Registry                             │          │
│  └──────────────────┬───────────────────────────┘          │
│                     │ Spawns                                │
│                     ▼                                       │
│  ┌──────────────────────────────────────────────┐          │
│  │ Specialist Sub-Agents (Short-lived)          │          │
│  │ - Execute domain-specific tasks              │          │
│  │ - Follow workflows                           │          │
│  │ - Write learnings                            │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │ Knowledge Base (.praxis-os/)                  │          │
│  │ ├─ personas/      (config files)             │          │
│  │ ├─ workflows/     (structured processes)     │          │
│  │ ├─ standards/     (domain knowledge)         │          │
│  │ └─ cache/         (RAG index, gitignored)    │          │
│  └──────────────────────────────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Design Principles

| Principle | Implementation | Rationale |
|-----------|----------------|-----------|
| **Config-Driven** | Personas as .md files | Add persona = add file, no code changes |
| **Discovery-Based** | RAG semantic search | No hardcoding, dynamic evolution |
| **Knowledge Compounding** | Specialists write standards | System improves over time |
| **Local-First** | No deployment needed | Git-based sharing, zero infrastructure |
| **Evidence-Based** | Phase gates with validation | Quality enforcement, not trust-based |
| **Self-Teaching** | Query patterns in tool descriptions | Agents learn tool usage on-demand |

---

## 2. Core Components

### 2.1 Component Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                    prAxIs OS Architecture                      │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Persona Layer (Config)                              │    │
│  │ - Markdown files define specialist identities       │    │
│  │ - One file per persona                              │    │
│  │ - Dynamic loading by filename                       │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ▲                                    │
│                          │ loads                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Execution Layer (Code)                              │    │
│  │ - PersonaLauncher: Single class for all personas   │    │
│  │ - WorkflowEngine: Phase-gated execution            │    │
│  │ - RAGEngine: Semantic search over knowledge        │    │
│  │ - Toolkit: File ops, command exec, MCP tools       │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ▲                                    │
│                          │ queries                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Knowledge Layer (Data)                              │    │
│  │ - Standards: Universal + Project-specific          │    │
│  │ - Workflows: Process definitions                   │    │
│  │ - RAG Index: Vector embeddings                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

#### PersonaLauncher
```python
class PersonaLauncher:
    """Single implementation for all personas."""
    
    async def run(self, persona_name: str, task: str) -> str:
        # 1. Load persona from file
        prompt = Path(f".praxis-os/personas/{persona_name}.md").read_text()
        
        # 2. Run agentic loop
        while not done:
            response = llm.call(messages, tools=mcp_tools)
            if tool_call:
                result = toolkit.execute(tool_call)
            else:
                done = True
        
        return response
```

#### WorkflowEngine
```python
class WorkflowEngine:
    """Phase-gated workflow execution with evidence validation."""
    
    def start_workflow(self, type: str, target: str) -> session_id
    def get_current_phase(self, session_id: str) -> phase_content
    def complete_phase(self, session_id: str, phase: int, evidence: dict) -> result
    def get_workflow_state(self, session_id: str) -> state
```

#### RAGEngine
```python
class RAGEngine:
    """Semantic search over prAxIs OS knowledge base."""
    
    def search(self, query: str, n_results: int = 5) -> SearchResult
    def index(self, documents: List[str]) -> None
```

---

## 3. Persona System

### 3.1 Persona Definition

**Personas are markdown files that define specialist identities.**

```
.praxis-os/personas/
├── database.md          ← invoke_specialist(persona="database")
├── api.md               ← invoke_specialist(persona="api")
├── security.md          ← invoke_specialist(persona="security")
└── testing.md           ← invoke_specialist(persona="testing")
```

**File structure:**
```markdown
# Persona Name

You are a [Domain] Specialist in prAxIs OS.

## Your Approach

1. Query standards for guidance: search_standards("how to [task]")
2. Discover workflows: If structured process exists, use it
3. Execute systematically: Follow phases, submit evidence
4. Document learnings: write_standard() for future discovery

## Your Tools

HIGH PRIORITY (use first):
- search_standards(query) - Your primary knowledge source
- search_codebase(query, dirs) - Project context
- write_standard(category, name, content) - Document learnings

WORKFLOW TOOLS:
- start_workflow(type, file) - If structured process exists
- complete_phase(session, phase, evidence) - Advance workflow

## Decision Protocol

BEFORE implementing:
- Query: "how to [specific task]"
- Discover: Does workflow exist?
- Execute: Follow structured process or best practices
- Document: Write project-specific patterns

NEVER skip research phase.
ALWAYS document new patterns.
```

### 3.2 Persona Invocation Flow

```
User: "Use database specialist to design auth schema"
  ↓
Main Agent: invoke_specialist(persona="database", task="Design auth schema")
  ↓
MCP Tool Handler:
  ├─ Validates persona exists (.praxis-os/personas/database.md)
  ├─ Spawns sub-agent process
  └─ Returns: Sub-agent connection info
  ↓
PersonaLauncher:
  ├─ Loads: .praxis-os/personas/database.md
  ├─ Initializes: LLM client with toolkit
  ├─ System Prompt: Content of database.md
  └─ User Message: "Design auth schema"
  ↓
Agentic Loop (in sub-agent):
  │
  ├─ LLM: "I'll search for guidance"
  ├─ Tool Call: search_standards("how to design database schema")
  ├─ Result: "Use database-schema-design workflow"
  │
  ├─ LLM: "Structured workflow exists!"
  ├─ Tool Call: start_workflow("database-schema-design", "auth.sql")
  ├─ Result: Phase 0 content (7 tasks)
  │
  ├─ LLM: Executes Phase 0 tasks
  ├─ Tool Call: complete_phase(session_id, 0, evidence={...})
  ├─ Result: Phase 1 content
  │
  ├─ ... continues through all phases ...
  │
  └─ LLM: Returns structured schema design
  ↓
Returns to Main Agent: Complete schema with documentation
```

### 3.3 Persona Discovery Pattern

**Personas don't know about workflows upfront - they discover them:**

```markdown
# Inside any persona prompt

## Your Approach (Discovery Pattern)

**Step 1: Query for Guidance**
search_standards("how to [your specific task]")

**Step 2: Interpret Results**
- Does a workflow exist? → Use start_workflow()
- Only best practices? → Follow patterns
- Nothing found? → Use domain expertise

**Step 3: Execute**
If workflow: Follow phases systematically
If no workflow: Implement with best practices

**Step 4: Document**
write_standard("project/[domain]/", "[pattern-name]", content)
```

### 3.4 Adding New Personas

```bash
# Create new persona (user or team)
cat > .praxis-os/personas/performance.md << 'EOF'
You are a Performance Optimization Specialist.

## Your Approach
1. search_standards("how to optimize [component]")
2. Discover workflows or best practices
3. Execute systematically
4. Document optimizations

## Your Tools
- search_standards(query)
- search_codebase(query, dirs)
- write_standard(category, name, content)
EOF

# Immediately available!
invoke_specialist(persona="performance", task="Optimize API response time")
```

**No code changes. No deployment. Just add file.**

---

## 4. Workflow System

### 4.1 Workflow Structure

```
.praxis-os/workflows/
├── test-generation-js-ts/
│   ├── FRAMEWORK_ENTRY_POINT.md    ← Overview
│   ├── metadata.json                ← Config
│   ├── core/
│   │   ├── command-language-glossary.md
│   │   └── progress-tracking.md
│   └── phases/
│       ├── 0/
│       │   ├── phase.md            ← Phase overview
│       │   ├── task-1-*.md
│       │   └── task-2-*.md
│       ├── 1/
│       │   └── ...
│       └── 8/
│           └── ...
```

### 4.2 Workflow Lifecycle

```
Discovery:
search_standards("how to generate tests JavaScript")
→ "Use test-generation-js-ts workflow"

Initialization:
start_workflow("test-generation-js-ts", "file.ts")
→ Returns: session_id, Phase 0 content

Execution:
get_current_phase(session_id)
→ Returns: Current phase tasks

Advancement:
complete_phase(session_id, phase, evidence)
→ Validates evidence
→ Returns: Next phase content OR validation errors

Completion:
Phase 8 completed
→ Workflow finalized
→ Returns: Summary
```

### 4.3 Phase Gate Architecture

```markdown
# phase.md structure

## Validation Gate

🛑 VALIDATE-GATE: Phase N Checkpoint

**Criteria (all must be ✅):**
- [ ] Criterion 1: [specific, measurable] ✅/❌
- [ ] Criterion 2: [specific, measurable] ✅/❌
- [ ] Criterion 3: [specific, measurable] ✅/❌

🚨 FRAMEWORK-VIOLATION: Proceeding with ❌ criteria
```

**Engine enforces:**
```python
def complete_phase(session_id, phase, evidence):
    # Load checkpoint requirements
    requirements = load_checkpoint(workflow_type, phase)
    
    # Validate evidence
    for criterion, validator in requirements.items():
        if not validator(evidence[criterion]):
            return {
                "status": "failed",
                "missing": criterion,
                "current_phase": phase
            }
    
    # All criteria met - advance
    return {
        "status": "success",
        "next_phase": phase + 1,
        "content": load_phase_content(phase + 1)
    }
```

### 4.4 Human Approval Gates

```json
{
  "phase": 5,
  "name": "Test Plan (Human Approval)",
  "requires_approval": true
}
```

**Flow:**
```
Phase 5: Test Plan Generation
  ↓
Agent: complete_phase(5, evidence={test_plan: "..."})
  ↓
Engine: "Human approval required. Blocking."
  ↓
🛑 BLOCKED until human confirms
  ↓
Human: Approves plan
  ↓
Engine: Advances to Phase 6
```

### 4.5 Creating Custom Workflows

```python
# Via MCP tool
create_workflow(
    name="api-documentation",
    workflow_type="documentation",
    phases=["Analysis", "Generation", "Validation"],
    target_language="python"
)

# Generates:
.praxis-os/workflows/api-documentation/
├── FRAMEWORK_ENTRY_POINT.md
├── metadata.json
├── core/
│   ├── command-language-glossary.md
│   └── progress-tracking.md
└── phases/
    ├── 0/phase.md + tasks
    ├── 1/phase.md + tasks
    └── 2/phase.md + tasks
```

**Uses meta-workflow principles:**
- Three-tier architecture
- Command language
- Validation gates
- ≤100 line task files

---

## 5. Tool Design Philosophy

### 5.1 Tool Categories

```
┌─────────────────────────────────────────────┐
│ MCP Tools (LLM-callable, < 20 total)       │
├─────────────────────────────────────────────┤
│ HIGH PRIORITY (core capabilities):         │
│ - search_standards(query)                  │
│ - search_codebase(query, dirs)             │
│ - write_standard(category, name, content)  │
│                                            │
│ WORKFLOW:                                  │
│ - start_workflow(type, file)               │
│ - complete_phase(session, phase, evidence) │
│ - get_current_phase(session)               │
│                                            │
│ SPECIALIST:                                │
│ - invoke_specialist(persona, task)         │
│                                            │
│ FRAMEWORK:                                 │
│ - create_workflow(name, type, phases)      │
│ - validate_workflow(path)                  │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Framework Tools (Python methods, unlimited)│
├─────────────────────────────────────────────┤
│ NOT exposed to LLM:                        │
│ - toolkit.read_file(path)                  │
│ - toolkit.write_file(path, content)        │
│ - toolkit.list_files(pattern)              │
│ - toolkit.run_command(cmd)                 │
│ - toolkit.git_status()                     │
│                                            │
│ Framework orchestrates these automatically │
└─────────────────────────────────────────────┘
```

### 5.2 Complex Tools with RAG Guidance

**Problem:** Research says complex tools cause param errors.

**Agent OS Solution:** Self-teaching tools.

```python
@mcp.tool()
async def comprehensive_tool(
    param1: str,
    param2: List[str] = [],
    param3: Dict = {},
    ...  # 7 parameters total
):
    """
    Complex tool with many parameters.
    
    📖 USAGE GUIDANCE:
    Before calling, query: search_standards("how to use comprehensive_tool")
    Returns: Complete param guide, examples, patterns
    """
    ...
```

**Flow:**
```
Agent: Needs to use comprehensive_tool
  ↓
Agent: search_standards("how to use comprehensive_tool")
  ↓
RAG Returns:
  - Complete parameter definitions
  - When to use which parameters
  - Common patterns
  - Examples
  - Decision trees
  ↓
Agent: Generates tool call with guidance in context
  ↓
Success rate: 95%+ (vs 60% without guidance)
```

**Key Insight:**
- MCP protocol provides schemas (via tools/list)
- RAG provides usage wisdom (via search_standards)
- No duplication, single source of truth

### 5.3 Tool Schema vs Usage

```
┌─────────────────────────────────────────────┐
│ MCP Protocol (Automatic)                    │
├─────────────────────────────────────────────┤
│ tools/list returns:                         │
│ {                                           │
│   "name": "search_standards",               │
│   "description": "...",                     │
│   "inputSchema": {                          │
│     "properties": {                         │
│       "query": {"type": "string"},          │
│       "n_results": {"type": "integer"}      │
│     }                                       │
│   }                                         │
│ }                                           │
│                                             │
│ Agent/Cursor ALREADY has this!              │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ RAG Content (Query on demand)               │
├─────────────────────────────────────────────┤
│ search_standards("tool usage X") returns:   │
│ - When to use which parameters              │
│ - Common patterns                           │
│ - Examples for specific use cases           │
│ - Decision guidance                         │
│ - Error cases to avoid                      │
│                                             │
│ Agent queries this when needed              │
└─────────────────────────────────────────────┘
```

---

## 6. Discovery Mechanisms

### 6.1 Everything Is Discoverable

```
┌──────────────────────────────────────────────────────────┐
│ Discovery Mechanism                                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ What tools exist?                                        │
│ → MCP protocol: tools/list                               │
│ → Cursor shows in autocomplete                           │
│                                                          │
│ What standards exist?                                    │
│ → search_standards(query)                                │
│ → RAG semantic search                                    │
│                                                          │
│ What workflows exist?                                    │
│ → search_standards("how to [task]")                      │
│ → Returns workflow if exists                             │
│                                                          │
│ What personas exist?                                     │
│ → List .praxis-os/personas/*.md                           │
│ → Or query: search_standards("available specialists")   │
│                                                          │
│ How to use tool X?                                       │
│ → search_standards("how to use [tool_name]")            │
│ → Returns usage guide                                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 6.2 Discovery Pattern (Universal)

**All agents (main, specialists) follow same pattern:**

```
Step 1: Query for guidance
search_standards("how to [specific task]")

Step 2: Interpret results
- Workflow exists? → Use it
- Best practices only? → Follow them
- Nothing found? → Use expertise + document

Step 3: Execute
With structure or with best practices

Step 4: Document learnings
write_standard() for future discovery
```

### 6.3 Query Examples

```python
# Discovering workflows
search_standards("how to generate tests JavaScript")
→ "Use test-generation-js-ts workflow"

search_standards("how to design database schema")
→ "Use database-schema-design workflow"

search_standards("how to review code security")
→ "Use security-audit workflow"

# Discovering patterns
search_standards("authentication patterns")
→ Best practices, no specific workflow

# Discovering tool usage
search_standards("how to use search_codebase parameters")
→ Complete param guide with examples
```

---

## 7. Knowledge Compounding

### 7.1 The Self-Improving System

```
Day 1: Bootstrap
├─ Universal standards (shipped)
├─ Base workflows (shipped)
└─ Core personas (shipped)

Day 30: Team Adoption
├─ Specialists write project patterns
├─ write_standard("project/database/", "auth-pattern", ...)
├─ RAG indexes new content
└─ Future specialists discover these patterns

Day 90: Rich Knowledge Base
├─ 100+ project-specific standards
├─ 10+ custom workflows
├─ 20+ specialized personas
└─ Quality improves across all work

Day 180: Self-Actualizing
├─ Specialists create new workflows (via create_workflow)
├─ Workflows indexed automatically
├─ Knowledge dense and discoverable
└─ New team members inherit accumulated wisdom
```

### 7.2 Write Standard Flow

```
Specialist completes task
  ↓
Identifies new pattern worth documenting
  ↓
write_standard(
    category="project/database",
    name="connection-pooling-pattern",
    content="""
    # Connection Pooling Pattern
    
    ## Context
    High-traffic API endpoints
    
    ## Pattern
    Use pgBouncer with max_connections=50
    
    ## Evidence
    Reduced connection time by 80%
    
    ## Usage
    [examples]
    """
)
  ↓
File written: .praxis-os/standards/project/database/connection-pooling-pattern.md
  ↓
File watcher detects change
  ↓
RAG incrementally rebuilds index (~10 seconds)
  ↓
Immediately discoverable:
search_standards("database connection optimization")
→ Returns new pattern!
```

### 7.3 Knowledge Categories

```
.praxis-os/standards/
├── universal/              (Shipped with Agent OS)
│   ├── concurrency/
│   ├── testing/
│   ├── architecture/
│   └── ...
│
└── project/               (Written by specialists)
    ├── database/
    │   ├── auth-patterns.md
    │   ├── migration-strategies.md
    │   └── query-optimization.md
    ├── api/
    │   ├── versioning-approach.md
    │   └── rate-limiting-strategy.md
    └── security/
        ├── token-validation.md
        └── audit-logging.md
```

---

## 8. Implementation Details

### 8.1 File Structure

```
.praxis-os/
├── personas/                    # Specialist definitions
│   ├── database.md
│   ├── api.md
│   ├── security.md
│   └── testing.md
│
├── workflows/                   # Structured processes
│   ├── test-generation-js-ts/
│   ├── database-schema-design/
│   └── security-audit/
│
├── standards/                   # Knowledge base
│   ├── universal/              # Shipped
│   └── project/                # Team-written
│
├── mcp_server/                 # Framework code
│   ├── persona_launcher.py
│   ├── workflow_engine.py
│   ├── rag_engine.py
│   └── ...
│
├── venv/                       # Python virtualenv
│
└── cache/                      # Gitignored
    └── vector_index.db         # RAG index
```

### 8.2 PersonaLauncher Implementation

```python
# mcp_server/persona_launcher.py

from pathlib import Path
from typing import Dict, Any

PERSONA_DIR = Path(".praxis-os/personas")

class PersonaLauncher:
    """Single implementation for all personas."""
    
    def __init__(self, toolkit, llm_client):
        self.toolkit = toolkit
        self.llm = llm_client
    
    async def run(self, persona_name: str, task: str) -> str:
        """Run ANY persona - just load the file!"""
        
        # 1. Load system prompt from file
        persona_file = PERSONA_DIR / f"{persona_name}.md"
        
        if not persona_file.exists():
            available = [f.stem for f in PERSONA_DIR.glob("*.md")]
            return {
                "error": f"Persona '{persona_name}' not found",
                "available": available
            }
        
        system_prompt = persona_file.read_text()
        
        # 2. Initialize messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        
        # 3. Get MCP tool schemas
        tools = self._get_tool_schemas()
        
        # 4. Agentic loop
        while True:
            response = await self.llm.call(messages, tools)
            
            if response.tool_calls:
                # Execute tool via toolkit
                tool_call = response.tool_calls[0]
                result = await self._execute_tool(
                    tool_call.name,
                    tool_call.arguments
                )
                
                # Add to messages
                messages.append({
                    "role": "tool",
                    "name": tool_call.name,
                    "content": result
                })
            else:
                # LLM returned text, done
                return response.content
    
    def _get_tool_schemas(self):
        """Get MCP tool schemas for this specialist."""
        # Return subset of MCP tools
        # Core: search_standards, search_codebase, write_standard
        # Workflow: start_workflow, complete_phase
        return [...]
    
    async def _execute_tool(self, name: str, args: dict):
        """Execute tool via toolkit or MCP."""
        if name in ["search_standards", "start_workflow", ...]:
            # MCP tool - call via toolkit.mcp_client
            return await self.toolkit.mcp_call(name, args)
        elif name in ["read_file", "write_file"]:
            # Framework tool - execute directly
            return getattr(self.toolkit, name)(**args)
```

### 8.3 MCP Tool Registration

```python
# mcp_server/server/tools/specialist_tools.py

@mcp.tool()
async def invoke_specialist(
    persona: str,
    task: str,
    context: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Invoke a specialist sub-agent with specific persona.
    
    Personas are dynamically loaded from .praxis-os/personas/ directory.
    Filename (without .md) = persona name.
    
    Args:
        persona: Persona name (e.g., "database", "api", "security")
        task: Task description for specialist
        context: Optional context dict
    
    Returns:
        Specialist's analysis/implementation with learnings
    
    Example:
        invoke_specialist(
            persona="database",
            task="Design authentication schema with OAuth support"
        )
    """
    # Single launcher handles all personas
    result = await launcher.run(
        persona_name=persona,
        task=task,
        context=context
    )
    
    return result
```

### 8.4 Toolkit Implementation

```python
# mcp_server/toolkit.py

class AgentToolkit:
    """Common tooling layer for all specialists."""
    
    def __init__(self, project_root, mcp_client):
        self.project_root = project_root
        self.mcp = mcp_client
    
    # File Operations (Framework-level, not LLM tools)
    def read_file(self, path):
        """Read file from project."""
        full_path = self.project_root / path
        return full_path.read_text()
    
    def write_file(self, path, content):
        """Write file to project."""
        full_path = self.project_root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
    
    # MCP-Backed Operations (LLM-callable via MCP)
    async def mcp_call(self, tool_name, args):
        """Call MCP tool."""
        return await self.mcp.call_tool(tool_name, args)
```

---

## 9. Example Flows

### 9.1 Complete Flow: Test Generation

```
User in Cursor:
"Generate tests for src/api/auth.ts using the testing specialist"

┌──────────────────────────────────────────────────────┐
│ Main Agent (Cursor)                                  │
├──────────────────────────────────────────────────────┤
│ 1. Interprets request                                │
│ 2. Identifies: Need testing specialist              │
│ 3. Tool Call: invoke_specialist(                    │
│       persona="testing",                            │
│       task="Generate tests for src/api/auth.ts"    │
│    )                                                │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ MCP Server                                           │
├──────────────────────────────────────────────────────┤
│ 4. Receives invoke_specialist call                  │
│ 5. Spawns sub-agent process                         │
│ 6. PersonaLauncher.run("testing", task)             │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ Testing Specialist (Sub-Agent)                      │
├──────────────────────────────────────────────────────┤
│ 7. Loads: .praxis-os/personas/testing.md             │
│    System Prompt: "You are testing specialist..."   │
│                                                      │
│ 8. User Message: "Generate tests for src/api/auth"  │
│                                                      │
│ 9. LLM: "I'll search for test generation process"   │
│ 10. Tool Call: search_standards(                    │
│        "how to generate tests TypeScript"           │
│     )                                               │
│                                                      │
│ 11. RAG Returns:                                     │
│     "Use test-generation-js-ts workflow              │
│      - 9 phases                                      │
│      - AST analysis, dependency mapping             │
│      - Quality gates: 0 errors required"            │
│                                                      │
│ 12. LLM: "Structured workflow exists!"              │
│ 13. Tool Call: start_workflow(                      │
│        "test-generation-js-ts",                     │
│        "src/api/auth.ts"                            │
│     )                                               │
│                                                      │
│ 14. Workflow Engine Returns:                        │
│     session_id: "abc123"                            │
│     Phase 0 content: "7 tasks..."                   │
│                                                      │
│ 15-50. LLM executes Phase 0-8:                      │
│     - AST analysis                                   │
│     - Dependency mapping                             │
│     - Test plan (human approval)                     │
│     - Test generation                                │
│     - Quality validation (0 errors)                  │
│                                                      │
│ 51. LLM: "Tests complete, documenting pattern"      │
│ 52. Tool Call: write_standard(                      │
│        "project/testing",                           │
│        "auth-api-test-pattern",                     │
│        content="..."                                │
│     )                                               │
│                                                      │
│ 53. Returns: Complete test file + documentation     │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ Main Agent (Cursor)                                  │
├──────────────────────────────────────────────────────┤
│ 54. Receives result from specialist                 │
│ 55. Presents to user:                               │
│     "Generated comprehensive test suite:             │
│      - 25 test cases                                 │
│      - 95% coverage                                  │
│      - 0 TypeScript errors                           │
│      - 0 ESLint warnings                             │
│      Files: tests/api/auth.test.ts"                 │
└──────────────────────────────────────────────────────┘
```

### 9.2 Discovery Flow: New Pattern

```
Specialist: Complete task with no existing workflow

1. Specialist queries:
   search_standards("how to optimize API performance")
   
2. RAG returns:
   - Best practices for caching
   - Database query optimization
   - No specific workflow

3. Specialist implements using best practices:
   - Adds Redis caching
   - Optimizes database queries
   - Measures improvement

4. Specialist documents pattern:
   write_standard(
       "project/performance",
       "api-caching-strategy",
       content="""
       # API Caching Strategy
       
       ## Problem
       High-traffic endpoints causing slow response
       
       ## Solution
       Redis caching with 5-minute TTL
       
       ## Implementation
       [code examples]
       
       ## Results
       - Response time: 500ms → 50ms
       - Database load: 1000 qps → 100 qps
       """
   )

5. File written and indexed

6. Future specialists discover it:
   search_standards("API performance optimization")
   → Returns this pattern!
```

### 9.3 Workflow Creation Flow

```
User: "Create workflow for code review process"

1. Main agent: create_workflow(
       name="code-review",
       workflow_type="quality",
       phases=["Context", "Security", "Performance", "Tests", "Approval"]
   )

2. FrameworkGenerator:
   - Queries meta-workflow standards
   - Generates compliant structure:
     ├── FRAMEWORK_ENTRY_POINT.md
     ├── metadata.json
     ├── core/
     │   ├── command-language-glossary.md
     │   └── progress-tracking.md
     └── phases/
         ├── 0/ (Context)
         ├── 1/ (Security)
         ├── 2/ (Performance)
         ├── 3/ (Tests)
         └── 4/ (Approval)

3. Files written to: .praxis-os/workflows/code-review/

4. Immediately discoverable:
   search_standards("how to review code")
   → "Use code-review workflow"

5. Immediately usable:
   start_workflow("code-review", "PR-123")
```

---

## 10. Deployment Models

### 10.1 Three Deployment Patterns

#### Pattern 1: Dev Tooling (Most Common)
```
External Project (e.g., any codebase):

my-project/
├── .praxis-os/              ← Local only, gitignored
│   ├── personas/
│   ├── workflows/
│   ├── standards/
│   └── cache/
├── .gitignore              ← Contains ".praxis-os/"
└── src/

Usage:
- Developer bootstraps prAxIs OS locally
- Uses personas/workflows for productivity
- Commits outputs (code, specs), not tooling
- Other devs don't need Agent OS
```

#### Pattern 2: Team Adoption (Power Users)
```
Team Project:

team-project/
├── .praxis-os/              ← Committed to git!
│   ├── personas/           ← Team-specific specialists
│   ├── workflows/          ← Team-specific processes
│   └── standards/
│       ├── universal/      ← From Agent OS
│       └── project/        ← Team knowledge
├── .cursorrules            ← Committed
└── src/

Usage:
- Whole team uses Agent OS
- Shared personas/workflows/standards
- Knowledge compounds across team
- New members inherit accumulated wisdom
```

#### Pattern 3: Framework Development (Agent OS Itself)
```
praxis-os/

├── universal/              ← Source (edit this)
│   ├── standards/
│   ├── workflows/
│   └── personas/
│
├── .praxis-os/              ← Installation (like consumers)
│   ├── standards/universal/  ← Copied from ../universal/
│   ├── mcp_server/
│   └── cache/

Usage:
- Dogfooding - use prAxIs OS to build Agent OS
- True testing of installation process
- No shortcuts, feel all pain points
```

### 10.2 Installation Process

**Not npm/pip - conversational setup:**

```
User in ANY project:
"Install prAxIs OS from github.com/honeyhiveai/praxis-os"

Cursor agent:
1. Reads: installation/00-START.md
2. Clones repo to: /tmp/agent-os-install-xyz/
3. Follows steps 01-06 sequentially:
   - Creates .praxis-os/ directories
   - Copies files from temp clone
   - Creates venv, configures MCP
   - Builds RAG index
   - Deletes temp clone
4. Done!

Result:
- .praxis-os/ created locally
- MCP server running
- Personas/workflows available
- No nested git repo
- Clean installation
```

---

## 11. References

### 11.1 Key Documents

**Standards:**
- `.praxis-os/standards/universal/workflows/workflow-system-overview.md`
- `.praxis-os/standards/universal/meta-workflow/validation-gates.md`
- `.praxis-os/standards/universal/workflows/workflow-construction-standards.md`

**Workflows:**
- `.praxis-os/workflows/test-generation-js-ts/` (9-phase example)
- `.praxis-os/workflows/spec_creation_v1/` (Spec creation)
- `.praxis-os/workflows/praxis_os_upgrade_v1/` (Self-upgrade)

**Implementation:**
- `mcp_server/workflow_engine.py` (1270 lines)
- `mcp_server/framework_generator.py` (Generator)
- `mcp_server/rag_engine.py` (RAG search)

### 11.2 Research Insights

**From Aider Analysis:**
- Single framework, multiple prompts (17 prompt files)
- ~100 lines of LLM client code (REST wrapper)
- Prompts are configuration, not code

**From prAxIs OS Dogfooding:**
- Config-driven beats code-driven
- Discovery beats hardcoding
- RAG enables self-teaching tools
- Knowledge compounds over time

**From hive-kube test-generation-js-ts:**
- Real-world 9-phase workflow
- Human approval gates work
- Quality enforcement prevents shortcuts
- Project-specific processes are viable

---

## 12. Design Decisions

### 12.1 Key Choices

| Decision | Rationale |
|----------|-----------|
| **Personas as .md files** | Add persona = add file, no code changes |
| **Single launcher** | One implementation for all personas |
| **Dynamic file loading** | Filename = persona name, pure discovery |
| **Workflows as markdown** | Version-controlled processes |
| **RAG for discovery** | Semantic search beats hardcoding |
| **Phase gates with evidence** | Quality enforcement, not trust-based |
| **Local-first architecture** | Git-based sharing, zero infrastructure |
| **Self-teaching tools** | Query for usage patterns on-demand |
| **Knowledge compounding** | Specialists write standards → indexed → discovered |

### 12.2 Trade-offs

| Choice | Pros | Cons | Mitigation |
|--------|------|------|------------|
| Markdown files | Simple, version-controlled | No type safety | Runtime validation |
| RAG discovery | Flexible, extensible | Requires good query patterns | Teach query patterns in orientation |
| Complex tools | Atomic operations | Higher token cost per tool | RAG guidance reduces errors |
| Local-first | Zero infrastructure | Manual setup per machine | Conversational installation |
| Phase gates | Quality enforcement | More steps to complete | But higher quality output |

---

## 13. Success Metrics

**System-level:**
- Workflow completion rate: Target 85-95%
- Quality gate pass rate: Target 100% (enforced)
- Knowledge growth: Project standards count over time
- Discovery success: Query → result relevance

**User-level:**
- Time to add persona: < 5 minutes
- Time to create workflow: < 30 minutes
- Specialist accuracy: 85-95% vs 60-70% baseline
- Team adoption: Multiple devs using shared knowledge

---

## 14. Future Enhancements

### 14.1 Potential Improvements

**Persona Intelligence:**
- Persona recommender: "For this task, consider X specialist"
- Multi-persona collaboration: Two specialists work together
- Persona version control: Track persona evolution

**Workflow Evolution:**
- Workflow analytics: Success rates, bottlenecks
- Workflow optimization: AI suggests improvements
- Workflow composition: Combine workflows

**Knowledge Compounding:**
- Pattern detection: Auto-identify reusable patterns
- Standard quality scoring: Which standards most useful?
- Cross-project learning: Share anonymized patterns

**Tool Enhancement:**
- Tool usage analytics: Which tools most effective?
- Tool recommendation: "For X task, use Y tool"
- Tool composition: Multi-tool patterns

---

## Appendix A: Glossary

**Persona:** Markdown file defining specialist identity and approach

**Workflow:** Phase-gated structured process for complex tasks

**Phase Gate:** Evidence-based checkpoint that must pass to advance

**Checkpoint:** Validation criteria for phase completion

**Evidence:** Structured data proving phase requirements met

**Toolkit:** Common capabilities available to all specialists

**RAG:** Retrieval Augmented Generation - semantic search over knowledge

**Knowledge Compounding:** System improvement through specialist documentation

**Discovery Pattern:** Query-based learning instead of hardcoded knowledge

**Agentic Loop:** While loop enabling multiple LLM calls with tools

---

## Appendix B: Quick Start

### For Developers

```bash
# Install prAxIs OS in your project
"Install prAxIs OS from github.com/honeyhiveai/praxis-os"

# Use a specialist
"Use database specialist to design auth schema"

# Start a workflow
"Start test generation workflow for src/api/auth.ts"

# Create custom persona
cat > .praxis-os/personas/my-specialist.md << 'EOF'
You are a [Domain] Specialist.
[your prompt]
EOF

# Create custom workflow
create_workflow(
    name="my-process",
    phases=["Phase1", "Phase2", "Phase3"]
)
```

### For Teams

```bash
# Commit prAxIs OS to project
git add .praxis-os/
git commit -m "Add prAxIs OS with team personas"

# Team members pull and use immediately
git pull
# prAxIs OS ready!

# Build team knowledge
# Specialists automatically write to .praxis-os/standards/project/
# Commit periodically to share learnings
git add .praxis-os/standards/project/
git commit -m "Add authentication patterns from specialist"
```

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-10-12  
**Status:** Architecture Complete  
**Next Steps:** Implementation of PersonaLauncher and specialized persona prompts

