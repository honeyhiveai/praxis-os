# Design Document: Persona System

**Version:** 1.0.0  
**Date:** 2025-10-12  
**Status:** Design Specification  
**Target:** Implementers, Persona Creators, AI Agents

---

## Overview

The Persona System enables domain-specific AI specialists through a config-driven architecture. Specialists are defined in markdown files and executed by a single launcher implementation, allowing infinite extensibility without code changes.

**Core Principle:** AI agents can invoke specialist sub-agents with focused expertise, improving output quality through domain knowledge and structured workflows.

**Part of:** Agent OS Enhanced spec-driven development framework for AI quality enhancement.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Design Goals](#design-goals)
3. [Architecture](#architecture)
4. [Persona Definition](#persona-definition)
5. [PersonaLauncher Implementation](#personalauncher-implementation)
6. [Discovery Pattern](#discovery-pattern)
7. [Workflow Integration](#workflow-integration)
8. [File Structure](#file-structure)
9. [Complete Flows](#complete-flows)
10. [Creating Custom Personas](#creating-custom-personas)
11. [Testing Personas](#testing-personas)

---

## 1. Problem Statement

### The Challenge

General-purpose AI agents lack domain expertise, leading to mediocre output quality:

```
Without Specialists:
Human: "Design database schema for authentication"
Generic Agent: 
  - Guesses at normalization
  - Misses indexing strategies
  - Ignores migration concerns
  - Forgets cascading deletes
Result: 60-70% quality, requires human fixes

With Specialists:
Human: "Use database specialist to design auth schema"
Database Specialist:
  - Queries database design patterns
  - Discovers schema-design workflow exists
  - Executes 5-phase structured process
  - Validates normalization, indexes, constraints
  - Documents approach for future use
Result: 85-95% quality, production-ready
```

### Why Domain Specialists Matter

**Quality improvement through:**
1. **Focused expertise:** Deep knowledge in specific domain
2. **Systematic approach:** Discovers and follows structured workflows
3. **Pattern application:** Applies proven patterns from standards
4. **Knowledge compounding:** Documents learnings for future agents

**Spec-driven development benefit:** Specialists create high-quality specs that drive implementation, reducing rework cycles.

### Why Not Code Each Specialist?

**Traditional Approach:**
```python
# 10 specialists = 10 Python classes = Code sprawl
class DatabaseSpecialist(BaseSpecialist):
    def __init__(self):
        self.domain = "database"
        self.tools = [...]
    
    def execute(self, task):
        # Custom logic per specialist
        ...

class APISpecialist(BaseSpecialist):
    # More custom code
    ...

# Adding new specialist requires:
# 1. Write Python class
# 2. Register with launcher
# 3. Deploy code changes
# 4. Restart server
```

**Agent OS Approach:**
```markdown
# .agent-os/personas/database.md
You are a Database Architecture Specialist...

# Adding new specialist requires:
# 1. Create markdown file
# Done! Immediately available.
```

**10 specialists = 10 markdown files = No code changes, no deployments**

---

## 2. Design Goals

| Goal | Implementation | Validation |
|------|----------------|------------|
| **Zero Code for New Personas** | Add .md file only | Can users add specialists without touching code? |
| **Single Implementation** | One PersonaLauncher class | Does one class handle all personas? |
| **Dynamic Discovery** | Filename = persona name | Can personas be discovered at runtime? |
| **Workflow Integration** | Query-based discovery | Do specialists find workflows via RAG? |
| **Knowledge Compounding** | write_standard() tool | Do specialists document learnings? |
| **Cross-Agent Compatible** | MCP tools only | Works in Cursor, Cline, Windsurf? |
| **Quality Enhancement** | Domain expertise + workflows | 85-95% output quality? |

---

## 3. Architecture

### Three-Layer System

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: Persona Configuration (Markdown Files)         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  .agent-os/personas/                                    │
│  ├── database.md        ← Specialist definition        │
│  ├── api.md             ← Filename = Persona name      │
│  ├── security.md        ← System prompt in markdown    │
│  └── testing.md                                         │
│                                                         │
│  NO CODE - Just configuration files                     │
│  Add file = Add specialist (instant)                    │
│                                                         │
└─────────────────┬───────────────────────────────────────┘
                  │ PersonaLauncher loads
                  ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 2: Execution Engine (Single Implementation)      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  PersonaLauncher (mcp_server/persona_launcher.py):     │
│  ├─ load(persona_name) → Read markdown file            │
│  ├─ initialize(system_prompt, task) → Setup LLM        │
│  ├─ agentic_loop() → Execute until complete            │
│  └─ Same code for ALL personas                         │
│                                                         │
│  LLM Client (stateless API):                            │
│  ├─ Anthropic/OpenAI REST calls                        │
│  └─ System prompt = Persona file content               │
│                                                         │
│  MCP Client (tool executor):                            │
│  └─ Provides tools to specialist (14 tools)            │
│                                                         │
└─────────────────┬───────────────────────────────────────┘
                  │ queries
                  ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 3: Knowledge Layer (Discovery & Learning)        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Standards (RAG-indexed):                               │
│  ├─ Universal (timeless CS patterns)                    │
│  └─ Project (accumulated learnings)                     │
│                                                         │
│  Workflows (phase-gated processes):                     │
│  ├─ Spec creation                                       │
│  ├─ Test generation                                     │
│  └─ Custom workflows                                    │
│                                                         │
│  Specialists discover everything via search_standards() │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Execution Flow

```
1. Main agent receives task:
   "Design authentication database schema"
   
2. Main agent invokes specialist:
   invoke_specialist(persona="database", task="Design auth schema")
   ↓
3. MCP tool handler validates persona exists:
   Check: .agent-os/personas/database.md exists? ✓
   ↓
4. PersonaLauncher loads specialist:
   system_prompt = read_file("database.md")
   ↓
5. Initialize LLM conversation:
   messages = [
     {"role": "system", "content": system_prompt},
     {"role": "user", "content": "Design auth schema"}
   ]
   ↓
6. Agentic loop executes:
   while not done:
     response = llm.call(messages, tools=mcp_tools)
     if tool_calls:
       for tool in tool_calls:
         result = execute_mcp_tool(tool)
         messages.append(tool_result)
     else:
       done = True  # Text response = task complete
   ↓
7. Return result to main agent:
   {
     "result": "Complete schema design with migrations",
     "tools_used": ["search_standards", "start_workflow", ...],
     "duration_ms": 45000,
     "artifacts": [...]
   }
   ↓
8. Main agent continues or reports to human
```

---

## 4. Persona Definition

### File Format

**Location:** `.agent-os/personas/[name].md`

**Naming:** Filename (without .md) becomes persona name
- `database.md` → `persona="database"`
- `api-design.md` → `persona="api-design"`

**Structure:**

```markdown
# [Domain] Specialist Title

You are a [Domain] Specialist in Agent OS Enhanced.

[Your role and expertise description]

## Your Approach

1. BEFORE implementing:
   - search_standards("how to [task type] in [domain]")
   - Discover if workflows exist
   - Query for domain-specific patterns
   
2. Execute:
   - If workflow exists: start_workflow()
   - If no workflow: Follow best practices from standards
   - Apply domain expertise
   
3. Validate:
   - [Domain-specific quality checks]
   
4. Document:
   - write_standard("project/[domain]/", "[pattern-name]", content)
   - Capture learnings for future use

## Your Tools

HIGH PRIORITY (use these first):
- search_standards(query) - Your primary knowledge source
- search_codebase(query, dirs) - Project context
- write_standard(category, name, content) - Document learnings

WORKFLOW (if structured process exists):
- start_workflow(type, file) - Execute phase-gated process
- complete_phase(session, phase, evidence) - Advance workflow

FILE OPERATIONS:
- access_file(name, mode, content) - Read/write files
- list_directory(path, pattern) - Navigate project
- execute_command(cmd, cwd) - Run commands

## Decision Protocol

[Critical rules for your domain]

ALWAYS [required behavior]
NEVER [anti-pattern to avoid]
QUERY before implementing (don't guess)
DOCUMENT new patterns discovered
VALIDATE output quality
```

### Required Sections

1. **Identity:** "You are a [Domain] Specialist"
   - Clear domain expertise
   - Role definition

2. **Approach:** Systematic workflow
   - Query first (discovery pattern)
   - Execute (workflow or best practices)
   - Validate (domain-specific)
   - Document (knowledge compounding)

3. **Tools:** Available capabilities
   - Prioritized (high-priority tools first)
   - Categorized (knowledge, workflow, file ops)
   - Self-teaching (query for usage guidance)

4. **Decision Protocol:** Critical rules
   - Domain-specific requirements
   - Anti-patterns to avoid
   - Quality standards

### Optional Sections

- **Domain Expertise:** Deep dive into specialist knowledge
- **Common Patterns:** Frequently used approaches
- **Error Handling:** Domain-specific failure modes
- **Quality Metrics:** How to measure success
- **Examples:** Reference implementations

---

## 5. PersonaLauncher Implementation

### Core Class Structure

```python
# mcp_server/persona_launcher.py

from pathlib import Path
from typing import Dict, Any, Optional, List
import time
import json

PERSONA_DIR = Path(".agent-os/personas")

class PersonaLauncher:
    """
    Single implementation for all personas.
    
    Loads persona definitions from markdown files and executes
    them through an agentic loop with MCP tools.
    
    Part of Agent OS Enhanced spec-driven development framework.
    """
    
    def __init__(self, mcp_client, llm_client):
        """
        Initialize launcher.
        
        Args:
            mcp_client: Client for MCP tool calls
            llm_client: Client for LLM API calls (Claude, GPT, etc.)
        """
        self.mcp = mcp_client
        self.llm = llm_client
    
    async def run(
        self,
        persona_name: str,
        task: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute persona on task.
        
        This is the single execution path for all specialists.
        Persona-specific behavior comes from the markdown file content,
        not from code branches.
        
        Args:
            persona_name: Name of persona (filename without .md)
            task: Task description from main agent or human
            context: Optional context information
        
        Returns:
            {
                "result": specialist_output,
                "tools_used": [tool_names],
                "artifacts": [created_files],
                "duration_ms": execution_time,
                "tokens": total_tokens,
                "cost": total_cost
            }
        """
        # 1. Load persona definition (system prompt)
        system_prompt = self._load_persona(persona_name)
        if "error" in system_prompt:
            return system_prompt  # Persona not found
        
        # 2. Initialize conversation
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        
        if context:
            messages.append({
                "role": "user",
                "content": f"Additional context: {json.dumps(context)}"
            })
        
        # 3. Get tool schemas (filtered for specialists)
        tools = self._get_tool_schemas()
        
        # 4. Execute agentic loop
        result = await self._agentic_loop(messages, tools, persona_name)
        
        return result
    
    def _load_persona(self, persona_name: str) -> Union[str, Dict]:
        """
        Load persona from markdown file.
        
        The entire file content becomes the system prompt.
        This allows infinite flexibility in persona design.
        """
        persona_file = PERSONA_DIR / f"{persona_name}.md"
        
        if not persona_file.exists():
            # Provide helpful error with available options
            available = [f.stem for f in PERSONA_DIR.glob("*.md")]
            return {
                "error": f"Persona '{persona_name}' not found",
                "available": available,
                "suggestion": f"Create: .agent-os/personas/{persona_name}.md",
                "template": "See DESIGN-Persona-System.md for template"
            }
        
        return persona_file.read_text()
    
    def _get_tool_schemas(self) -> List[Dict]:
        """
        Get MCP tool schemas for specialists.
        
        Returns subset of all MCP tools relevant to specialists:
        - Knowledge: search_standards, search_codebase, write_standard
        - Workflow: start_workflow, complete_phase, get_current_phase
        - File ops: access_file, list_directory, execute_command
        - Framework: create_workflow, validate_workflow
        - Infrastructure: aos_browser
        
        Omits: invoke_specialist (avoid infinite recursion)
        """
        return [
            # Tool schemas from MCP server
            # Filtered to specialist-relevant subset
            ...
        ]
    
    async def _agentic_loop(
        self,
        messages: List[Dict],
        tools: List[Dict],
        persona_name: str
    ) -> Dict[str, Any]:
        """
        Execute agentic loop until task complete.
        
        This is the "while loop" that makes specialists agentic.
        
        Loop structure:
        1. Call LLM with messages and tools
        2. If tool_call: Execute tool via MCP, add result to messages, continue
        3. If text response: Task complete, return result
        
        The LLM is stateless (REST API). The agent is this loop.
        """
        tools_used = []
        artifacts = []
        total_tokens = 0
        total_cost = 0.0
        start_time = time.time()
        
        iteration = 0
        max_iterations = 50  # Safety limit
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call LLM (stateless API)
            response = await self.llm.call(
                messages=messages,
                tools=tools,
                temperature=0.7
            )
            
            # Track metrics
            total_tokens += response.usage.total_tokens
            total_cost += self._calculate_cost(response)
            
            # Check for tool calls
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    # Execute tool via MCP
                    result = await self.mcp.call_tool(
                        tool_call.name,
                        tool_call.arguments
                    )
                    
                    # Track usage
                    tools_used.append(tool_call.name)
                    
                    # Track artifacts (files created)
                    if tool_call.name in ["access_file", "write_standard"]:
                        if "path" in result:
                            artifacts.append(result["path"])
                    
                    # Add to conversation
                    messages.append({
                        "role": "assistant",
                        "content": response.content,
                        "tool_calls": [tool_call]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.name,
                        "content": json.dumps(result)
                    })
            else:
                # Text response = task complete
                duration_ms = (time.time() - start_time) * 1000
                
                return {
                    "persona": persona_name,
                    "result": response.content,
                    "tools_used": tools_used,
                    "artifacts": artifacts,
                    "iterations": iteration,
                    "duration_ms": round(duration_ms, 2),
                    "tokens": total_tokens,
                    "cost": round(total_cost, 4)
                }
        
        # Safety limit reached
        return {
            "error": "Max iterations reached",
            "partial_result": messages[-1]["content"],
            "tools_used": tools_used,
            "iterations": iteration
        }
    
    def _calculate_cost(self, response) -> float:
        """Calculate API cost based on token usage and model."""
        # Implementation details...
        pass
```

### MCP Tool Registration

```python
# mcp_server/server/tools/specialist_tools.py

from fastmcp import FastMCP

mcp = FastMCP("agent-os-rag")

@mcp.tool()
async def invoke_specialist(
    persona: str,
    task: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Invoke a domain specialist sub-agent.
    
    Specialists are config-driven agents defined in markdown files.
    Located in .agent-os/personas/ directory.
    Filename (without .md) = persona name.
    
    📖 USAGE GUIDANCE:
    Before using, query: search_standards("available specialists")
    
    Specialists enhance output quality through:
    - Domain expertise
    - Structured workflows (discovered via RAG)
    - Pattern application from standards
    - Knowledge documentation for future use
    
    Args:
        persona: Persona name (e.g., "database", "api", "security")
        task: Task description for specialist
        context: Optional context dict (project info, constraints, etc.)
    
    Returns:
        {
            "persona": specialist_name,
            "result": specialist_output,
            "tools_used": [tool_names],
            "artifacts": [created_files],
            "duration_ms": execution_time,
            "cost": api_cost
        }
    
    Examples:
        # Database schema design
        invoke_specialist(
            persona="database",
            task="Design authentication schema with OAuth support"
        )
        
        # Security review
        invoke_specialist(
            persona="security",
            task="Review authentication code for vulnerabilities",
            context={"compliance": ["GDPR", "SOC2"]}
        )
        
        # API design
        invoke_specialist(
            persona="api",
            task="Design RESTful API for user management"
        )
    """
    # Single launcher handles all personas
    result = await persona_launcher.run(
        persona_name=persona,
        task=task,
        context=context
    )
    
    return result
```

---

## 6. Discovery Pattern

### Core Principle: Query First

**Specialists don't know about workflows upfront - they discover them through search.**

This enables:
- **Zero hardcoding:** Personas don't reference specific workflows
- **Evolution:** New workflows automatically discoverable
- **Cross-domain:** Security specialist can discover database workflows
- **Self-teaching:** System teaches itself through accumulated standards

### Discovery Flow

```markdown
# Inside any persona prompt (teaches the pattern)

## Your Approach

**Step 1: Query for Guidance**
search_standards("how to [your specific task in domain]")

Examples:
- "how to design database schema"
- "how to review code for security vulnerabilities"
- "how to generate comprehensive tests"

**Step 2: Interpret Results**
Look for:
- Workflow mentions: "Use [workflow-name] workflow"
- Best practices: Patterns and approaches
- Examples: Reference implementations

**Step 3: Execute**
If workflow mentioned:
  → start_workflow([workflow-name], target_file)
  → Follow phases systematically
  → Provide evidence at each gate

If no workflow:
  → Follow best practices from standards
  → Apply domain expertise
  → Consider: Should this become a workflow?

**Step 4: Document**
write_standard("project/[domain]/", "[pattern-name]", content)
→ Capture learnings for future agents
→ System improves over time
```

### Example: Database Specialist Discovery

```
Human: "Design authentication schema"
  ↓
Main agent: invoke_specialist("database", "Design auth schema")
  ↓
Database Specialist launches:
  System prompt from database.md teaches discovery pattern
  ↓
Specialist thinks: "I should query for guidance"
  ↓
Specialist: search_standards("how to design database schema")
  ↓
RAG returns:
  "Use database-schema-design workflow
   5 phases: Requirements, Design, Migration, Approval, Documentation
   Ensures: Normalization, indexes, constraints, cascading deletes"
  ↓
Specialist thinks: "Structured workflow exists! This will ensure quality."
  ↓
Specialist: start_workflow("database-schema-design", "auth.sql")
  ↓
Workflow returns: Phase 0 content (7 tasks)
  ↓
Specialist executes Phase 0 systematically:
  Task 1: Gather requirements
  Task 2: Identify entities
  Task 3: Define relationships
  Task 4: Plan normalization
  ...
  ↓
Specialist: complete_phase(session, 0, evidence={...})
  ↓
Workflow returns: Phase 1 content
  ↓
Specialist continues through all 5 phases
  ↓
Specialist: write_standard("project/database/", "auth-schema-pattern", "...")
  ↓
Returns to main agent: Complete validated schema design
```

### Why Discovery Works

1. **No Maintenance Burden:** Add workflow → Instantly discoverable
2. **Cross-Pollination:** Any specialist can find any workflow
3. **Self-Documenting:** Workflows teach their own existence via RAG
4. **Quality Improvement:** Structured workflows → Better output
5. **Knowledge Compounding:** Specialists document → Future discovery

---

## 7. Workflow Integration

### How Specialists Use Workflows

**Workflows provide structure, personas provide expertise.**

```markdown
# Inside persona prompt

When you encounter a task:

1. Query: search_standards("how to [task] in [domain]")
   
2. Look for workflow mentions in results:
   - "Use [workflow-name] workflow"
   - "Structured process: [workflow-name]"
   - "Phase-gated execution via [workflow-name]"
   
3. If workflow mentioned:
   start_workflow([workflow-name], target_file)
   → Ensures systematic execution
   → Quality gates enforce completeness
   → Evidence-based progression
   
4. If no workflow:
   Follow best practices from standards
   Apply domain expertise
   Consider proposing workflow creation
```

### Execution Pattern

```
Specialist discovers workflow exists:
  ↓
Specialist: start_workflow("database-schema-design", "auth.sql")
  Returns: {
    "session_id": "db-schema-20251012-143022",
    "current_phase": 0,
    "phase_content": "Phase 0: Requirements Analysis (7 tasks)"
  }
  ↓
Specialist executes Phase 0 tasks systematically
  ↓
Specialist: complete_phase(session, 0, evidence={
    "requirements_documented": True,
    "entities_identified": 5,
    "relationships_mapped": 8,
    "file": "auth-requirements.md"
  })
  ↓
Workflow validates evidence:
  ✓ All required fields present
  ✓ Advances to Phase 1
  Returns: Phase 1 content
  ↓
Specialist executes Phase 1 tasks
  ↓
Specialist: complete_phase(session, 1, evidence={...})
  ↓
...continues through all phases...
  ↓
Phase 5 (final):
  Specialist: complete_phase(session, 5, evidence={...})
  ↓
Workflow validates:
  ✓ All phases complete
  ✓ All evidence validated
  Returns: {
    "status": "complete",
    "artifacts": [...],
    "summary": "..."
  }
  ↓
Specialist documents learnings:
  write_standard("project/database/", "auth-schema-pattern", content)
  ↓
Returns comprehensive result to main agent
```

### Quality Through Structure

**Phase gating ensures:**
- Cannot skip phases (architecturally enforced)
- Must provide evidence at each gate
- Human approval gates for critical decisions
- Quality validation before completion

**Result:** 85-95% quality output vs. 60-70% without structure.

---

## 8. File Structure

```
.agent-os/
├── personas/                    # Specialist definitions
│   ├── database.md             # Database architecture
│   ├── api.md                  # API design
│   ├── security.md             # Security review
│   ├── testing.md              # Test generation
│   ├── performance.md          # Performance optimization
│   ├── documentation.md        # Documentation creation
│   ├── frontend.md             # Frontend architecture
│   ├── devops.md               # DevOps and deployment
│   └── [custom].md             # User-created specialists
│
├── workflows/                   # Discovered by personas via RAG
│   ├── spec_creation_v1/
│   ├── spec_execution_v1/
│   ├── test_generation_js_ts/
│   ├── database_schema_design/
│   └── [custom]/
│
└── standards/                   # Discovered by personas via RAG
    ├── universal/               # Shipped with framework
    │   ├── concurrency/
    │   ├── testing/
    │   ├── architecture/
    │   └── ...
    └── project/                 # Written by personas
        ├── database/
        ├── api/
        ├── security/
        └── [domain]/
```

---

## 9. Complete Flows

### Flow 1: Specialist with Workflow (High Quality)

```
Human: "Use database specialist to design authentication schema"
  ↓
Main Agent: invoke_specialist("database", "Design auth schema")
  ↓
PersonaLauncher:
├─ Loads: .agent-os/personas/database.md
├─ System prompt: "You are Database Specialist..."
└─ User message: "Design auth schema"
  ↓
Database Specialist (Agentic Loop):
├─ Iteration 1:
│  └─ Tool: search_standards("how to design database schema")
│     Result: "Use database-schema-design workflow, 5 phases..."
│  
├─ Iteration 2:
│  └─ Tool: start_workflow("database-schema-design", "auth.sql")
│     Result: Phase 0 content (7 tasks)
│  
├─ Iterations 3-9:
│  └─ Executes Phase 0 tasks (requirements, entities, relationships)
│  
├─ Iteration 10:
│  └─ Tool: complete_phase(session, 0, evidence={...})
│     Result: Phase 1 content
│  
├─ Iterations 11-25:
│  └─ Executes remaining phases systematically
│  
├─ Iteration 26:
│  └─ Tool: write_standard("project/database", "auth-pattern", "...")
│     Result: Standard created
│  
└─ Iteration 27:
   └─ Text response: "Complete validated schema design..."
      Result: {
        "persona": "database",
        "result": "Complete schema with migrations, indexes, constraints",
        "tools_used": ["search_standards", "start_workflow", "complete_phase", ...],
        "artifacts": ["auth.sql", "migrations/001_auth.sql", "docs/auth-schema.md"],
        "duration_ms": 45000,
        "tokens": 15000,
        "cost": 0.08
      }
  ↓
Main Agent: Receives complete result
  ↓
Human: Reviews schema, approves, commits
```

### Flow 2: Specialist without Workflow (Best Practices)

```
Human: "Use performance specialist to optimize API response time"
  ↓
Performance Specialist:
├─ search_standards("how to optimize API performance")
│  Result: Best practices (no specific workflow)
│  
├─ search_codebase("API performance bottlenecks")
│  Result: Slow database queries, N+1 problems
│  
├─ access_file("src/api/handler.ts", "read")
│  Result: Current implementation
│  
├─ Analyzes: Identifies 3 optimization opportunities:
│  1. Add database query caching
│  2. Implement response compression
│  3. Use connection pooling
│  
├─ access_file("src/api/handler.ts", "write", content="... optimized ...")
│  Result: Updated implementation
│  
├─ execute_command("npm test")
│  Result: Tests pass
│  
├─ execute_command("npm run benchmark")
│  Result: 300ms → 45ms response time (85% improvement)
│  
├─ write_standard("project/performance", "api-caching-pattern", "...")
│  Result: Pattern documented
│  
└─ Returns: "Optimized API with 85% performance improvement"
```

### Flow 3: Multi-Specialist Collaboration (Future)

```
Human: "Design and implement secure payment processing"
  ↓
Main Agent: "This requires multiple specialists"
  ↓
invoke_specialist("api", "Design payment API endpoints")
  → Returns API specification
  ↓
invoke_specialist("security", "Review payment API for vulnerabilities")
  → Returns security assessment with fixes
  ↓
invoke_specialist("database", "Design payment data schema")
  → Returns schema with PCI compliance
  ↓
Main Agent synthesizes all specialist outputs
  ↓
invoke_specialist("testing", "Generate payment processing tests")
  → Returns comprehensive test suite
  ↓
Main Agent: "Complete payment system designed with security review"
```

---

## 10. Creating Custom Personas

### Step-by-Step Guide

#### Step 1: Create Persona File

```bash
# Create new specialist
cat > .agent-os/personas/caching.md << 'EOF'
# Caching Optimization Specialist

You are a Caching Optimization Specialist in Agent OS Enhanced.

Your role is to analyze systems and implement optimal caching strategies
to improve performance, reduce costs, and enhance user experience.

## Your Domain Expertise

Expert in:
- Cache strategies (Redis, Memcached, CDN, in-memory)
- Cache invalidation patterns (TTL, LRU, event-driven)
- Performance measurement and optimization
- Cost analysis and trade-offs
- Distributed caching challenges

## Your Approach

1. BEFORE implementing:
   - search_standards("how to optimize caching for [specific context]")
   - search_standards("cache invalidation patterns")
   - Discover if caching workflows exist
   
2. Analyze current system:
   - search_codebase("cache", ["src/"])
   - Identify caching opportunities
   - Measure current performance
   
3. Execute:
   - If workflow: start_workflow()
   - If no workflow: Apply best practices
   - Implement caching layer
   - Configure cache policies
   
4. Measure:
   - execute_command("performance benchmark")
   - Compare before/after metrics
   - Validate improvement
   
5. Document:
   - write_standard("project/caching", "[pattern-name]", content)
   - Include: Strategy, metrics, trade-offs

## Your Tools

HIGH PRIORITY:
- search_standards(query) - Learn caching patterns
- search_codebase(query, dirs) - Find cache opportunities
- write_standard(category, name, content) - Document approach

WORKFLOW:
- start_workflow(type, file) - If structured process exists
- complete_phase(session, phase, evidence) - Advance workflow

FILE OPERATIONS:
- access_file(name, mode, content) - Implement caching
- execute_command(cmd) - Run benchmarks

## Decision Protocol

ALWAYS measure before optimizing (baseline metrics)
NEVER guess at cache sizes - calculate based on data
ALWAYS consider cache invalidation strategy upfront
QUERY for patterns before implementing
DOCUMENT discovered patterns
VALIDATE performance improvements with metrics

## Cache Strategy Selection

Query: search_standards("cache strategy for [use case]")

Common patterns to consider:
- High-traffic reads → Redis with TTL
- Static assets → CDN with long expiry
- Session data → Redis with persistence
- Database queries → Query result cache
- API responses → HTTP cache headers
- Computed values → In-memory LRU cache

## Quality Metrics

- Response time improvement (target: 50%+ reduction)
- Cache hit rate (target: 80%+)
- Cost reduction (if applicable)
- Zero correctness issues (stale data)
EOF
```

#### Step 2: Test Persona

```bash
# In Cursor or Cline
"Use caching specialist to optimize API response time"

# Expected specialist behavior:
# 1. Queries caching patterns
# 2. Analyzes current code
# 3. Measures baseline performance
# 4. Implements caching strategy
# 5. Measures improvement
# 6. Documents pattern
# 7. Returns metrics-backed result
```

#### Step 3: Iterate Based on Usage

```markdown
# After first use, improve persona based on:

1. What did it struggle with?
   → Add more specific guidance
   
2. What tools did it need but weren't mentioned?
   → Update tools section
   
3. What patterns should be built-in?
   → Add to decision protocol
   
4. What questions did it ask that could be preempted?
   → Enhance domain expertise section

# Update .agent-os/personas/caching.md
# Changes are immediately effective (no restart needed)
```

### Persona Creation Template

```markdown
# [Domain] Specialist

You are a [Domain] Specialist in Agent OS Enhanced.

[Brief role description - what this specialist does]

## Your Domain Expertise

Expert in:
- [Skill/Knowledge Area 1]
- [Skill/Knowledge Area 2]
- [Skill/Knowledge Area 3]
- [Tool/Technology expertise]

## Your Approach

1. BEFORE implementing:
   - search_standards("how to [task] in [domain]")
   - Discover if workflows exist
   - Query for domain-specific patterns
   
2. Analyze:
   - search_codebase("[relevant keywords]", ["src/"])
   - [Domain-specific analysis steps]
   
3. Execute:
   - If workflow: start_workflow()
   - If no workflow: Follow best practices
   - [Domain-specific implementation]
   
4. Validate:
   - [Domain-specific quality checks]
   - [Testing approach]
   
5. Document:
   - write_standard("project/[domain]", "[pattern]", content)
   - [What to capture]

## Your Tools

HIGH PRIORITY:
- search_standards(query)
- search_codebase(query, dirs)
- write_standard(category, name, content)

WORKFLOW (if applicable):
- start_workflow(type, file)
- complete_phase(session, phase, evidence)

FILE OPERATIONS:
- access_file(name, mode, content)
- list_directory(path, pattern)
- execute_command(cmd)

[Domain-specific tools if needed]

## Decision Protocol

ALWAYS [critical requirement 1]
NEVER [anti-pattern 1]
QUERY before implementing (don't guess)
DOCUMENT new patterns discovered
VALIDATE [domain-specific quality]

[Domain-specific rules]

## [Domain-Specific Section if Needed]

[Additional guidance, patterns, examples]
```

---

## 11. Testing Personas

### Manual Testing Checklist

```bash
# Test 1: Persona loads correctly
"Use [persona-name] specialist to [simple task]"
Expected: Specialist launches, no errors

# Test 2: Discovery pattern works
"Use [persona-name] specialist to [task with workflow]"
Expected: search_standards() call appears
Expected: start_workflow() if workflow exists

# Test 3: Documentation happens
"Use [persona-name] specialist to [complete task]"
Expected: write_standard() call at end
Expected: Pattern documented in project/[domain]/

# Test 4: Quality output
"Use [persona-name] specialist to [realistic task]"
Expected: 85-95% quality result
Expected: Systematic approach
Expected: Evidence of domain expertise

# Test 5: Error handling
"Use nonexistent-specialist to do something"
Expected: Helpful error with available personas
Expected: Suggestion to create persona
```

### Automated Testing Pattern

```python
# tests/test_personas.py

async def test_persona_loads():
    """Test persona file loads correctly."""
    launcher = PersonaLauncher(mcp_client, llm_client)
    result = await launcher.run("database", "Test task")
    assert "error" not in result
    assert result["persona"] == "database"

async def test_persona_discovers_workflow():
    """Test persona discovers and uses workflow."""
    # Mock search_standards to return workflow mention
    # Mock start_workflow
    launcher = PersonaLauncher(mcp_client, llm_client)
    result = await launcher.run("database", "Design schema")
    assert "start_workflow" in result["tools_used"]

async def test_persona_documents_learnings():
    """Test persona writes standards."""
    # Mock write_standard
    launcher = PersonaLauncher(mcp_client, llm_client)
    result = await launcher.run("performance", "Optimize API")
    assert "write_standard" in result["tools_used"]

async def test_persona_not_found():
    """Test helpful error for missing persona."""
    launcher = PersonaLauncher(mcp_client, llm_client)
    result = await launcher.run("nonexistent", "Task")
    assert "error" in result
    assert "available" in result  # Lists available personas
    assert "suggestion" in result  # How to create
```

---

## Summary

**Persona System Design:**

✅ **Config-Driven:** Add .md file, no code changes, instant availability  
✅ **Single Implementation:** One PersonaLauncher for all specialists  
✅ **Discovery-Based:** Specialists find workflows via RAG queries  
✅ **Knowledge Compounding:** Specialists write standards for future use  
✅ **Cross-Agent Compatible:** Works with any MCP agent  
✅ **Quality Enhancement:** 85-95% output quality through domain expertise  
✅ **Infinitely Extensible:** Users create unlimited custom personas

**Key Implementation Files:**
- `mcp_server/persona_launcher.py` - Core execution engine
- `mcp_server/server/tools/specialist_tools.py` - MCP tool registration
- `.agent-os/personas/*.md` - Persona definitions (config)

**Part of:** Agent OS Enhanced spec-driven development framework

**Related Documents:**
- [ARCHITECTURE-Agent-OS-Enhanced.md](ARCHITECTURE-Agent-OS-Enhanced.md) - System overview
- [DESIGN-MCP-Tools-Universal-Toolkit.md](DESIGN-MCP-Tools-Universal-Toolkit.md) - Tool strategy

---

**Version:** 1.0.0  
**Last Updated:** 2025-10-12  
**Status:** Ready for Implementation
