---
sidebar_position: 1
doc_type: tutorial
---

# Introduction

**prAxIs OS** is a portable multi-agent development framework built on **praxis** - the integration of theory and practice through continuous learning. It transforms AI from helpful assistant to velocity-enhancing development partner that gets better with every interaction.

## What is prAxIs OS?

prAxIs OS builds on the foundation of [Agent OS by Brian Casel](https://buildermethods.com/agent-os), addressing key limitations discovered through production use:

- **90% context reduction** through semantic search (MCP/RAG)
- **Architectural phase gating** that enforces workflows in code
- **Universal + generated standards** that work across any language
- **Specialized sub-agents** for design validation, concurrency analysis, and more

## Quick Start

Install prAxIs OS in your project:

```bash
# Open your project in Cursor and say:
"Install prAxIs OS from github.com/honeyhiveai/agent-os-enhanced"
```

The Cursor agent will:
1. Analyze your project (detect language, frameworks)
2. Copy universal standards (CS fundamentals)
3. Generate language-specific standards (tailored to your stack)
4. Install MCP server locally
5. Configure Cursor MCP integration
6. Build RAG index

## What Gets Installed

```
your-project/
├── .cursorrules              # AI behavioral triggers (27 lines)
├── .praxis-os/
│   ├── standards/
│   │   ├── universal/        # Timeless CS fundamentals
│   │   └── development/      # Language-specific guidance
│   ├── mcp_server/           # MCP/RAG server
│   └── .cache/vector_index/  # Semantic search index
└── .cursor/
    └── mcp.json              # MCP configuration
```

## Core Concepts

### Praxis: Theory ⇄ Practice Integration

prAxIs OS is a **praxis engine** - every interaction creates learning that improves future interactions:

**The Cycle:**
1. **Action:** AI executes task using standards
2. **Reflection:** Evidence validates what worked/failed  
3. **Learning:** Capture pattern as new standard
4. **Refined Action:** Next AI queries and applies that learning

**The Result:**

```
Session 1:  AI + 0 standards  → 70% quality
Session 50: AI + 95 standards → 95% quality
```

The AI doesn't get smarter. **The system does.**

Through accumulated praxis cycles, prAxIs OS transforms probabilistic AI behavior into deterministic quality. Each session teaches the system. Each mistake becomes impossible to repeat. Knowledge compounds across all future work.

[Read more: Praxis Philosophy](../explanation/praxis)

### MCP/RAG Architecture

Instead of reading entire 50KB files, the MCP server uses semantic search to deliver 2-5KB targeted chunks:

- **Before:** AI reads full file, 4% relevant content, 12,500 tokens
- **After:** Vector search returns relevant chunks, 95% relevant, 625 tokens
- **Result:** 24x better relevance, 95% reduction in token usage

### Universal Standards

Timeless CS fundamentals that apply to any programming language:

- Concurrency patterns (race conditions, deadlocks, locking strategies)
- Testing strategies (test pyramid, test doubles, property-based testing)
- Architecture patterns (SOLID, dependency injection, API design)
- Failure modes (graceful degradation, circuit breakers, retry strategies)

### Language-Specific Generation

For each project, prAxIs OS generates language-specific implementations of universal standards:

- **Python:** GIL, threading, asyncio, pytest patterns
- **Go:** Goroutines, channels, sync primitives, table-driven tests
- **Rust:** Ownership, Arc/Mutex, tokio, cargo test patterns
- **And more...**

### Architectural Phase Gating

Workflows enforce progression through code, not documentation:

```python
def can_access_phase(self, phase: int) -> bool:
    """AI cannot access Phase N+1 before completing Phase N."""
    if phase == self.current_phase or phase in self.completed_phases:
        return True
    return False  # Structurally impossible to skip
```

## Next Steps

- **[Praxis Philosophy](../explanation/praxis)** - **Start here** - Why prAxIs OS works
- **[How It Works](../explanation/how-it-works)** - RAG-driven behavioral reinforcement
- **[Installation](./installation)** - Set up in your project
- **[Architecture](../explanation/architecture)** - MCP/RAG system deep-dive
- **[Standards](../reference/standards)** - Universal CS fundamentals
- **[Workflows](../reference/workflows)** - Phase-gated workflows
