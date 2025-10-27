# Amplifier vs prAxIs OS: Agent/Persona System Comparison

**Date:** 2025-10-21  
**Status:** Analysis Complete  
**Purpose:** Compare Microsoft Amplifier's agent system with prAxIs OS's persona/workflow system

---

## Executive Summary

Both systems implement specialized AI agents through markdown-based configuration, but with fundamentally different architectures and philosophies:

**Amplifier** = Task-specific agents with predefined modes + Claude Code integration + "bricks and studs" philosophy  
**prAxIs OS** = Discovery-driven personas + Phase-gated workflows + RAG-based knowledge compounding

---

## Side-by-Side Comparison

| Aspect | Microsoft Amplifier | prAxIs OS |
|--------|---------------------|-------------------|
| **Agent Definition** | `.claude/agents/*.md` (Claude Code format) | `.praxis-os/personas/*.md` (Custom format) |
| **Agent Philosophy** | Task-specific experts with operating modes | Discovery-driven generalists with domain focus |
| **Invocation** | Claude Code's Task tool | MCP tool: `invoke_specialist()` |
| **Knowledge Access** | Manual references (@DISCOVERIES.md, @ai_context/) | RAG semantic search: `search_standards()` |
| **Workflow Integration** | Implicit coordination between agents | Explicit phase-gated workflows |
| **Execution Model** | Claude Code sub-agent system | Custom PersonaLauncher with agentic loop |
| **Knowledge Compounding** | Manual documentation via DISCOVERIES.md | Automatic via `write_standard()` + RAG |
| **Architecture** | "Bricks & studs" modular design | Three-tier workflow architecture |
| **Evidence Validation** | Human review, no automated gates | Automated checkpoint validation |
| **Agent Count** | 20+ specialized agents | Unlimited (add .md file = new persona) |

---

## Architecture Comparison

### Amplifier: Agent-Centric Architecture

```
User Request
    ↓
Claude Code (Main Agent)
    ↓
Task Tool (invoke agent)
    ↓
Specialized Agent (e.g., zen-architect)
    ├─ Mode Selection (ANALYZE/ARCHITECT/REVIEW)
    ├─ Reference @DISCOVERIES.md, @ai_context/
    ├─ Execute with domain expertise
    └─ Return specification or implementation
    ↓
Handoff to next agent (e.g., modular-builder)
    ├─ Build from specification
    ├─ Follow "bricks and studs" philosophy
    └─ Return implementation
```

**Key Characteristics:**
- Agents have **explicit operating modes** (analyze/architect/review, etc.)
- Agents **manually reference** documentation via @ mentions
- Agents **collaborate via handoff** (architect → builder → bug-hunter)
- **No workflow state** - coordination is informal
- **Human judgment** determines when to use which agent

### prAxIs OS: Workflow-Centric Architecture

```
User Request
    ↓
Main Agent (Cursor/Continue)
    ↓
invoke_specialist(persona, task)
    ↓
PersonaLauncher loads .praxis-os/personas/{name}.md
    ↓
Persona (e.g., database)
    ├─ Query: search_standards("how to design database schema")
    ├─ Discover: Workflow exists? ("database-schema-design")
    ├─ Execute: start_workflow(type, target_file)
    └─ Phase Loop:
        ├─ get_current_phase(session_id)
        ├─ Execute phase tasks
        ├─ complete_phase(session_id, phase, evidence)
        ├─ Automated validation gate
        └─ Advance to next phase OR return errors
    ↓
Document learnings: write_standard(category, name, content)
    ↓
RAG auto-indexes → Future discovery
```

**Key Characteristics:**
- Personas **discover** workflows via semantic search
- **State-based execution** with session persistence
- **Automated validation gates** with evidence requirements
- **Knowledge compounding** through write_standard()
- **RAG-driven** - no hardcoded knowledge

---

## Agent/Persona Design Comparison

### Amplifier: zen-architect Agent

**Format:**
```markdown
---
name: zen-architect
description: Use this agent PROACTIVELY for code planning, architecture design, and review tasks...
model: inherit
---

You are the Zen Architect, a master designer who embodies ruthless simplicity...

## 🔍 ANALYZE MODE (Default for new features/problems)
[Detailed mode instructions]

## 🏗️ ARCHITECT MODE (Triggered by system design needs)
[Detailed mode instructions]

## ✅ REVIEW MODE (Triggered by code review needs)
[Detailed mode instructions]

## Decision Framework
For EVERY decision, ask:
1. Necessity: "Do we actually need this right now?"
2. Simplicity: "What's the simplest way to solve this?"
...
```

**Characteristics:**
- **Explicit modes** with emoji indicators
- **Rich context references** (@ai_context/IMPLEMENTATION_PHILOSOPHY.md)
- **Detailed methodologies** for each mode
- **Handoff instructions** to other agents
- **Philosophy embedded** in agent definition (ruthless simplicity, Occam's Razor)

### prAxIs OS: database Persona

**Format:**
```markdown
# Database Specialist

You are a Database Design Specialist in prAxIs OS.

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

**Characteristics:**
- **Discovery-driven** - agent doesn't know workflows upfront
- **Tool-centric** - explicit tool priorities
- **Learning protocol** - always document new patterns
- **Minimalist** - shorter, focused on discovery
- **Universal template** - same structure for all personas

---

## Key Philosophical Differences

### 1. Knowledge Access

**Amplifier:**
```markdown
# Inside zen-architect agent
Always read @ai_context/IMPLEMENTATION_PHILOSOPHY.md and 
@ai_context/MODULAR_DESIGN_PHILOSOPHY.md first.

**Modular Design ("Bricks & Studs"):**
- Define the contract (inputs, outputs, side effects)
- Specify module boundaries and responsibilities
...
```
- **Push model**: Content pushed into agent prompt via @ mentions
- **Static**: Documentation is manually referenced
- **Upfront**: All knowledge loaded at start

**prAxIs OS:**
```markdown
# Inside any persona
1. Query standards for guidance: search_standards("how to [task]")
2. Discover workflows: If structured process exists, use it
```
- **Pull model**: Content pulled on-demand via RAG query
- **Dynamic**: Only relevant content loaded
- **Just-in-time**: Knowledge queried when needed

### 2. Workflow Structure

**Amplifier:**
- Agents have **operating modes** (analyze/architect/review)
- **Informal handoffs** between agents
- **Human judgment** on process flow
- **No state tracking** between tasks
- Example: zen-architect → modular-builder → bug-hunter

**prAxIs OS:**
- Agents **discover workflows** via search
- **Formal phase gates** with validation
- **Automated enforcement** of process
- **State persistence** across sessions
- Example: `start_workflow("test-generation-js-ts")` → 9 phases with checkpoints

### 3. Collaboration Model

**Amplifier: Agent Handoff Pattern**
```markdown
# In zen-architect
**Handoff to Implementation:**
After creating specifications, delegate to modular-builder agent:
"I've analyzed the requirements and created specifications. 
The modular-builder agent will now implement these modules."
```
- Agents explicitly mention next agent
- Main agent interprets and routes
- **Sequential**: One agent at a time
- **Manual**: Human or main agent decides transitions

**prAxIs OS: Nested Invocation Pattern**
```python
# Main agent can invoke specialist
invoke_specialist(persona="database", task="Design auth schema")
  ↓
# Specialist can invoke another specialist
invoke_specialist(persona="security", task="Review auth security")
  ↓
# Or follow a workflow
start_workflow("database-schema-design", "auth.sql")
```
- Agents can spawn other specialists
- WorkflowEngine manages state
- **Parallel**: Multiple specialists can work independently
- **Automated**: Phase gates enforce transitions

### 4. Quality Enforcement

**Amplifier: Human Review**
```markdown
# In modular-builder
### After Completion
- [ ] Verify implementation matches specification
- [ ] All tests pass
- [ ] Module works in isolation
- [ ] Public interface is clean and minimal
- [ ] Code follows simplicity principles
```
- Checklists for human review
- Agent reports completion
- No automated validation
- Trust-based system

**prAxIs OS: Automated Gates**
```python
# In workflow phase.md
## Validation Gate
🛑 VALIDATE-GATE: Phase N Checkpoint

**Criteria (all must be ✅):**
- [ ] Criterion 1: [specific, measurable] ✅/❌
- [ ] Criterion 2: [specific, measurable] ✅/❌

# WorkflowEngine enforces
def complete_phase(session_id, phase, evidence):
    requirements = load_checkpoint(workflow_type, phase)
    for criterion, validator in requirements.items():
        if not validator(evidence[criterion]):
            return {"status": "failed", "missing": criterion}
    return {"status": "success", "next_phase": phase + 1}
```
- Automated validation gates
- Evidence-based advancement
- **Cannot skip phases** (architecturally enforced)
- System-enforced quality

---

## Strengths and Weaknesses

### Amplifier Strengths

✅ **Rich Domain Expertise**
- Agents have detailed domain knowledge embedded
- Multiple operating modes per agent
- Philosophy-driven decision frameworks

✅ **Flexible Collaboration**
- Agents can adapt collaboration patterns
- Human can override agent recommendations
- Informal handoffs allow creativity

✅ **Proven Integration**
- Built on Claude Code platform
- Task tool is standard feature
- Works with existing IDE workflows

✅ **Philosophy Consistency**
- "Ruthless simplicity" embedded in agents
- "Bricks & studs" enforced by design
- Clear architectural principles

### Amplifier Weaknesses

❌ **Manual Knowledge Discovery**
- Agents must manually @ mention docs
- No semantic search
- Knowledge not dynamically discovered

❌ **No Process Enforcement**
- Agents can skip steps
- No automated validation gates
- Quality depends on agent compliance

❌ **Limited Knowledge Compounding**
- DISCOVERIES.md is manual
- No automatic indexing
- Hard to discover past learnings

❌ **Platform Lock-in**
- Requires Claude Code
- Cannot run on other platforms
- Tight coupling to Task tool

### prAxIs OS Strengths

✅ **RAG-Driven Discovery**
- Semantic search finds relevant knowledge
- No manual @ mentions needed
- Dynamic content loading (90% context reduction)

✅ **Architectural Enforcement**
- Phase gates prevent skipping
- Automated validation
- Cannot proceed without evidence

✅ **Knowledge Compounding**
- write_standard() auto-indexed
- Future agents discover learnings
- System improves over time

✅ **Platform Agnostic**
- MCP protocol (standard)
- Works with Cursor, Continue, etc.
- Not locked to one IDE

✅ **Config-Driven**
- Add persona = add .md file
- No code changes
- Easy to extend

### prAxIs OS Weaknesses

❌ **Less Domain Richness**
- Personas are simpler than Amplifier agents
- No built-in operating modes
- Discovery pattern is uniform

❌ **Learning Curve**
- RAG query patterns must be learned
- Workflow creation more complex
- Evidence requirements need design

❌ **Workflow Rigidity**
- Phase gates can feel restrictive
- Cannot skip ahead (by design)
- Less flexibility than informal handoffs

❌ **MCP Server Overhead**
- Requires local Python server
- More complex setup
- Additional moving part

---

## Use Case Fit

### When to Use Amplifier

**Best For:**
- **Exploratory development** where process flexibility is valuable
- **Small teams** (1-5 devs) with high trust
- **Claude Code users** already on the platform
- **Philosophy-driven codebases** valuing ruthless simplicity
- **Rapid prototyping** where formal processes slow down

**Example:**
> "We're a 2-person startup building a new product. We need AI help but don't want rigid processes. We love the 'bricks & studs' philosophy and want agents that embody it."

### When to Use prAxIs OS

**Best For:**
- **Enterprise teams** (10+ devs) needing consistency
- **Regulated environments** requiring audit trails
- **Multi-platform teams** (Cursor + Continue + etc.)
- **Knowledge-intensive projects** where learning compounds
- **Complex workflows** (9+ phase processes)

**Example:**
> "We're a 50-person team building a medical device. We need strict phase gates, evidence validation, and an audit trail. Our developers use different IDEs."

---

## Hybrid Opportunities

### What prAxIs OS Could Adopt from Amplifier

1. **Operating Modes**
   ```markdown
   # Enhanced persona with modes
   You are a Database Specialist.
   
   ## 🔍 ANALYSIS MODE (default)
   - search_standards("database analysis patterns")
   - [mode-specific guidance]
   
   ## 🏗️ DESIGN MODE (for schema work)
   - search_standards("database schema design")
   - [mode-specific guidance]
   ```

2. **Richer Philosophy Embedding**
   - Personas could embed more domain philosophy
   - Decision frameworks within personas
   - Not just "query and execute"

3. **Agent Handoff Patterns**
   - Explicit handoff guidance in personas
   - "When to invoke security specialist"
   - Clear collaboration patterns

### What Amplifier Could Adopt from Agent OS

1. **RAG-Based Knowledge Discovery**
   ```markdown
   # In zen-architect
   Instead of: "Always read @ai_context/IMPLEMENTATION_PHILOSOPHY.md"
   Use: "Query standards: search('implementation philosophy ruthless simplicity')"
   ```

2. **Automated Validation Gates**
   ```markdown
   # After ANALYZE mode
   **Checkpoint Evidence Required:**
   - problem_decomposition: [structured breakdown]
   - solution_options: [2-3 approaches with trade-offs]
   - recommendation: [clear choice with justification]
   
   Cannot proceed to ARCHITECT mode without evidence.
   ```

3. **Knowledge Compounding System**
   ```markdown
   # After completing task
   write_discovery(
       category="architectural-patterns",
       pattern="new-pattern-name",
       content="..."
   )
   # Auto-indexed for future discovery
   ```

---

## Technical Implementation Comparison

### Amplifier: Claude Code Integration

```markdown
# .claude/agents/zen-architect.md
---
name: zen-architect
description: Use this agent PROACTIVELY for code planning...
model: inherit
---
[Agent prompt]
```

**Invocation:**
```
User: "Design the caching layer"
Main Agent: [Uses Task tool]
Claude Code: Spawns zen-architect sub-agent
zen-architect: [Executes with full context]
Returns: Specification
```

**Pros:**
- Simple file-based configuration
- Automatic discovery by Claude Code
- Built-in Task tool
- Session management handled by platform

**Cons:**
- Platform-specific format
- No custom validation logic
- Limited state management

### prAxIs OS: MCP + Custom Launcher

```python
# mcp_server/tools/specialist_tools.py
@mcp.tool()
async def invoke_specialist(persona: str, task: str) -> Dict:
    result = await launcher.run(
        persona_name=persona,
        task=task
    )
    return result

# mcp_server/persona_launcher.py
class PersonaLauncher:
    async def run(self, persona_name: str, task: str) -> str:
        persona_file = Path(f".praxis-os/personas/{persona_name}.md")
        system_prompt = persona_file.read_text()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        
        while True:
            response = await self.llm.call(messages, tools)
            if response.tool_calls:
                result = await self._execute_tool(...)
                messages.append({"role": "tool", "content": result})
            else:
                return response.content
```

**Pros:**
- Platform-agnostic (MCP standard)
- Custom validation logic
- State management
- Full control over execution

**Cons:**
- More complex implementation
- Local server required
- More configuration needed

---

## Recommendations for prAxIs OS

Based on Amplifier analysis:

### High-Priority Adoptions

1. **Add Operating Modes to Personas**
   - Enrich persona definitions with modes
   - Maintain discovery-driven approach
   - Example: database persona with ANALYZE/DESIGN/OPTIMIZE modes

2. **Richer Domain Philosophy**
   - Embed more decision frameworks
   - Add domain-specific checklists
   - Keep personas teachable, not just routers

3. **Explicit Handoff Patterns**
   - Document when to invoke other specialists
   - Add collaboration guidance to personas
   - Create "persona composition patterns" standard

### Consider for Future

4. **Hybrid Validation**
   - Keep automated gates for critical phases
   - Add "human approval gates" for creative phases
   - Example: Phase 2 (Design) requires human approval, Phase 3 (Implementation) automated

5. **Mode-Aware Workflows**
   - Workflows specify which mode each phase needs
   - Persona switches modes automatically per phase
   - Example: "Phase 1: database.ANALYZE, Phase 2: database.DESIGN"

---

## Conclusion

**Amplifier** = Rich agent expertise + Flexible collaboration + Philosophy-driven + Claude Code native  
**prAxIs OS** = Discovery-driven + Process enforcement + Knowledge compounding + Platform-agnostic

**Best of Both Worlds:**
- **Amplifier's** rich domain knowledge and operating modes
- **Agent OS's** RAG discovery and automated validation
- **Amplifier's** philosophy embedding
- **Agent OS's** knowledge compounding

**Next Steps:**
1. Design "Enhanced Persona Template" with modes
2. Create "Database Specialist v2" as proof of concept
3. Test discovery + modes combination
4. Document persona authoring best practices

---

**Document Status:** Complete  
**Next Review:** After implementing enhanced persona template  
**Related:** `amplifier-deep-analysis-2025-10-20.md`, `ARCHITECTURE-Agent-OS-Persona-And-Workflow-System.md`

