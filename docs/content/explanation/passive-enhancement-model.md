---
sidebar_position: 1
doc_type: explanation
---

import AgentWithoutPraxis from '@site/src/components/AgentWithoutPraxis';
import MCPSubstrateStack from '@site/src/components/MCPSubstrateStack';

# The Passive Enhancement Model: prAxIs OS as Cognitive Substrate

prAxIs OS is not a coding agent. It's a cognitive substrate that enhances any MCP-capable agent through passive infrastructure—standards, workflows, and code intelligence that any AI can access.

## TL;DR

**What prAxIs OS Is:**
- MCP server providing tools (`pos_search_project`, `pos_workflow`, etc.)
- RAG indexes (multi-repo semantic search, call graphs, AST patterns)
- Evidence-based workflows (phase gates, validation)
- Searchable standards (patterns, conventions, learnings)

**What prAxIs OS Is NOT:**
- Not a replacement for your coding agent
- Not tied to specific models or providers
- Not a standalone application you run directly

**How It Works:**
1. Install prAxIs OS in your project (`.praxis-os/` directory)
2. Your coding agent connects via MCP
3. Agent gains access to enhanced capabilities
4. You keep using your agent normally—just smarter

**Result:** Your agent (Cursor, Claude, Cline, etc.) becomes systematically better at understanding your codebase, following patterns, and producing quality code.

---

## Background: The Agent Enhancement Problem

### Traditional Coding Agents

Most AI coding assistants operate in isolation:

**Without prAxIs OS:**

<AgentWithoutPraxis />

**Result:**
- Reads your code each time (slow, incomplete)
- No memory of patterns across sessions
- No systematic quality enforcement
- Knowledge lost between sessions

**Limitations:**
- **Context blindness** - Can't see across multiple repos
- **Pattern blindness** - Doesn't learn your conventions
- **Stateless** - Forgets everything between sessions
- **Quality variance** - No systematic enforcement

### The Enhancement Gap

Your coding agent is powerful, but it's working blind:
- It can write code, but doesn't know your standards
- It can search files, but not semantically across repos
- It can follow instructions, but they fade in context
- It's stateless, so patterns don't compound

**The question:** How do you give your agent persistent memory, systematic behavior, and cumulative learning?

---

## Design Decision: MCP Substrate Layer

### Decision: Passive Enhancement via MCP

**prAxIs OS sits underneath your coding agent as cognitive infrastructure.**

**Architecture:**

<MCPSubstrateStack />

**Rationale:**

1. **Universal compatibility** - Works with any MCP-capable agent
2. **Model agnostic** - Intelligence in files, not model weights  
3. **Passive enhancement** - Agent behavior improves automatically
4. **No workflow changes** - Use your agent normally

---

## How The Enhancement Works

prAxIs OS provides tools your agent can call via the MCP Protocol:

**`pos_search_project`** - Searches standards, code, call graphs via RAG indexes  
**`pos_workflow`** - Executes phase-gated workflows with evidence validation  
**`pos_browser`** - Browser automation for testing  
**`pos_filesystem`** - Safe file operations  

**From your agent's perspective:** It's having a conversation with you. When it needs project knowledge, it calls `pos_search_project("error handling")` and gets relevant chunks instantly (90% context reduction). When implementing a feature, it calls `pos_workflow` and follows phase gates with evidence requirements.

**The MCP calls are visible and inspectable** (most agents show them in tool logs), but they're seamless - the agent just naturally uses these tools when appropriate.

**For detailed technical explanation:** See [How It Works](/docs/explanation/how-it-works)

---

## Compatibility

### Supported Agents

prAxIs OS works with any MCP-capable coding agent:

| Agent | Status | Notes |
|-------|--------|-------|
| **Cursor** | ✅ Full support | Via MCP configuration |
| **Claude Desktop** | ✅ Full support | Native MCP client |
| **Cline** | ✅ Full support | MCP-enabled VSCode extension |
| **Custom Agents** | ✅ Full support | Any MCP client |

**Configuration:** One-time setup in your agent's MCP config, then it works everywhere.

### Supported Models

Because intelligence lives in **standards + indexes** (not model weights), **any model works**.

prAxIs OS works with whatever model your MCP-capable agent connects to:
- Claude (Anthropic)
- GPT-4, o1 (OpenAI)
- Gemini (Google)
- Grok (xAI)
- Local models (Ollama, LM Studio, etc.)

**The key:** If your agent can connect to a model via API or locally, prAxIs OS enhances it.

---

## The Substrate Pattern

### Agent vs Substrate

**Traditional view:**
- Agent = Does all the work
- Codebase = Passive files

**prAxIs OS view:**
- Agent = Analyst (observes, reasons)
- prAxIs OS = Substrate (remembers, evolves)
- Together = Meta-cognitive system

**Comparison:**

| Aspect | Agent Alone | Agent + prAxIs OS |
|--------|-------------|-------------------|
| **Memory** | Stateless (forgets after session) | Persistent (project standards in searchable cache) |
| **Context** | 50KB loaded upfront (96% irrelevant) | 2-5KB retrieved on-demand (95% relevant via indexes) |
| **Patterns** | Rediscover each time | Documented once, discovered efficiently forever |
| **Quality** | Hope-based (trust AI claims) | Evidence-based (require proof) |
| **Multi-repo** | Single repo at a time | Semantic search across all repos |
| **Evolution** | Static (training data frozen) | Dynamic (standards compound) |

---

## Trade-offs

### Benefits

- ✅ **Universal compatibility** - Any MCP agent, any model
- ✅ **Persistent memory** - Standards compound within project across sessions
- ✅ **Context efficiency** - 90% reduction per query
- ✅ **Quality enforcement** - Evidence-based validation
- ✅ **Multi-repo intelligence** - Semantic search everywhere
- ✅ **Zero workflow changes** - Use your agent normally

### Limitations

- ⚠️ **Initial setup** - 5-10 minutes to install + configure MCP
- ⚠️ **Index build time** - ~60 seconds first run (auto-maintained after)
- ⚠️ **Disk space** - ~500MB for indexes (large codebases)
- ⚠️ **Behavioral drift** - After 30-40 messages of non-querying activity, AI agents may need re-orientation (active querying naturally reinforces correct behavior)

### When NOT to Use

**Skip prAxIs OS if:**
- ❌ Quick prototypes (throwaway code)
- ❌ Solo experiments (learning new tech)
- ❌ Time-critical emergencies (firefighting)
- ❌ Truly temporary scripts (one-time use)

**Use prAxIs OS for:**
- ✅ Production systems (long-lived)
- ✅ Team projects (shared understanding)
- ✅ Quality-critical code (user data, money)
- ✅ Knowledge preservation (patterns compound)

---

## Comparison: prAxIs OS vs Other Approaches

### vs Pure Coding Agents (Cursor, Claude Code)

**What they do well:**
- Fast iteration
- Natural conversation
- Direct code generation

**What prAxIs adds:**
- Persistent memory (standards)
- Systematic behavior (workflows)
- Multi-repo intelligence (semantic search)

**Relationship:** Complementary, not competitive. prAxIs makes your agent better.

---

### vs Spec-Driven Tools (GitHub Spec-Kit, AWS Kiro)

**GitHub Spec-Kit** (GitHub's open-source toolkit):
- Multi-phase workflow: Constitution → Specify → Plan → Tasks → Implement
- Works with GitHub Copilot, Claude Code, Gemini CLI
- Intent-driven: Define "what" before "how"
- Structured spec templates

**AWS Kiro** (AWS's AI-focused IDE):
- Embedded spec-driven development
- Structured spec creation interface
- Multi-phased process with separate spec documents
- Integration with AI coding agents

**What prAxIs does differently:**

*Both use AI to generate detailed specs - the difference is in input source and validation:*

**Spec Creation:**
- **Spec-Kit/Kiro**: Human fills structured templates → AI generates code
- **prAxIs**: Human-AI conversation → Design doc capture → `spec_creation_v1` workflow → AI generates technical spec bundle

**Implementation:**
- **Spec-Kit/Kiro**: AI implements from spec (hope-based validation)
- **prAxIs**: `spec_execution_v1` workflow → Phase gates → Evidence artifacts required → Proof-based validation

**Knowledge:**
- **Spec-Kit/Kiro**: Per-project specs (static documentation)
- **prAxIs**: Standards compound within project over time (searchable expertise cache) + Indexes optimize AI discovery

**Integration:**
- **Spec-Kit/Kiro**: Works with specific agents/IDEs
- **prAxIs**: Works with ANY MCP-capable agent (substrate layer)

**Key difference:** Spec-Kit/Kiro are **workflow systems** (you follow their process). prAxIs is **cognitive substrate** (enhances your agent's reasoning via persistent knowledge + evidence validation).

---

### vs Traditional Development

**What it does well:**
- Established processes
- Team coordination
- Quality gates

**What prAxIs bridges:**
- Traditional quality + AI speed
- 8 weeks compressed to 8 hours
- Knowledge captured permanently

**Key insight:** prAxIs brings systematic quality to AI speed.

---

## Getting Started

### Installation: Your First Trust Exercise

prAxIs OS installation is **LLM-guided and executed** - your AI agent handles everything. This is intentional: successfully completing a complex installation builds your confidence in the AI's capabilities.

**Open your project in Cursor, Claude Code, Cline, or GitHub Copilot and say:**

```
"Install prAxIs OS from github.com/honeyhiveai/praxis-os for <AGENT> [in <IDE>]"
```

**Examples:**
- `"Install prAxIs OS from github.com/honeyhiveai/praxis-os for Cursor"`
- `"Install prAxIs OS from github.com/honeyhiveai/praxis-os for Cline in VS Code"`
- `"Install prAxIs OS from github.com/honeyhiveai/praxis-os for Claude Code"`

**What happens:**
1. **Phase 1: Mechanical** - Agent runs installation script (creates `.praxis-os/`, copies files, sets up venv)
2. **Phase 2: Configuration** - Agent parses your command, routes to correct setup guide, configures MCP

**Time:** ~5-10 minutes  
**Result:** A working installation AND increased trust in your AI agent

**Why conversational?**
- The AI successfully handles a complex, multi-step task
- You see it parse your request, make decisions, and execute correctly
- First evidence that the AI can be trusted with real work
- Sets the foundation for the human-AI collaboration model

**The Learning Parallel:**

AI agents, like people, improve through guidance and accessible knowledge. When a junior developer joins your team, you don't expect perfection—you provide:
- **Standards and conventions** - How we do things here
- **Accessible documentation** - Knowledge when they need it  
- **Mentorship and feedback** - Evidence of understanding

prAxIs OS provides the same infrastructure for AI agents. The installation is your first "pair programming" session—the AI successfully completes a complex task using the tools it will rely on going forward. Mistakes will happen (as with any developer), but each one becomes impossible to repeat once captured as a standard. The system gets smarter with every session.

**Next steps:**
- [How It Works](./how-it-works.md) - RAG mechanism
- [Architecture](./architecture.md) - System design
- [Agent Integrations](../how-to-guides/agent-integrations/README.md) - Detailed setup guides

---

## Further Reading

**Core Concepts:**
- [How It Works](./how-it-works.md) - RAG-driven behavioral reinforcement
- [Architecture](./architecture.md) - System design decisions
- [Knowledge Compounding](./knowledge-compounding.md) - How it gets smarter

**Comparisons:**
- [Code Intelligence](./code-intelligence.md) - Multi-repo semantic search
- [Adversarial Design](./adversarial-design.md) - Quality enforcement
- [Economics](./economics.md) - Cost and productivity metrics

**Getting Started:**
- [Agent Integrations](../how-to-guides/agent-integrations/README.md) - Setup for your agent
- [Creating Standards](../how-to-guides/creating-project-standards.md) - Project-specific patterns
- [Custom Workflows](../how-to-guides/create-custom-workflows.md) - Phase-gated processes

