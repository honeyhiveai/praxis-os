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
    read_entire_file(".agent-os/standards/test-framework.md")  # 50KB+
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
- **Engines** read/write to project `.agent-os/` directory

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
├── .agent-os/
│   ├── mcp_server/          # Copied, not shared
│   └── .cache/vector_index/ # Project-specific index

project-2/
├── .agent-os/
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

