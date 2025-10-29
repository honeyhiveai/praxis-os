---
sidebar_position: 2
doc_type: explanation
---

# Architecture

prAxIs OS's architecture addresses three fundamental challenges in AI-assisted development: context overflow, phase skipping, and language-specific brittleness. This document explains the system's design, the reasoning behind key decisions, and the trade-offs involved.

---

## Overview

prAxIs OS consists of four integrated systems:

1. **MCP Server** - Model Context Protocol server providing tool discovery and execution
2. **RAG Engine** - Semantic search driving query-first behavior and 71% fewer messages
3. **Workflow Engine** - Phase-gated execution with architectural enforcement
4. **Standards System** - Universal patterns with language-specific generation

Each system solves a specific failure mode in traditional AI-assisted development.

---

## The Context Problem

### Background: Why Context Matters

Large Language Models have a fundamental limitation: **attention degradation**. When context exceeds 15-25% of the model's window, attention quality drops below 70%, leading to:
- Missed critical details (especially "lost in the middle")
- Contradictory implementations
- Ignored safety rules
- Hallucinated APIs

**Traditional approaches failed:**
- `.cursorrules` files (static, always loaded, 50KB+)
- Code comments (scattered, not discoverable)
- LLM training data (outdated, not project-specific)

### Design Decision: MCP + RAG

**Decision:** Use Model Context Protocol server with Retrieval Augmented Generation for just-in-time content delivery.

**Rationale:**
1. **Dynamic retrieval** replaces upfront loading (50KB → 2-5KB)
2. **Semantic search** finds relevant content regardless of exact keywords
3. **Standardized protocol** (MCP) enables tool discovery across AI platforms
4. **Local embeddings** avoid API costs and latency

**Architecture:**

import MCPArchitectureDiagram from '@site/src/components/MCPArchitectureDiagram';

<MCPArchitectureDiagram />

**Trade-offs:**

| Benefit | Limitation |
|---------|------------|
| 90% context reduction per query | Requires indexing (60s first run) |
| Semantic discovery (not keyword-dependent) | Vector search ~50ms overhead |
| Local embeddings (no API costs) | ~200MB memory footprint |
| Works offline | Index rebuild needed on content changes |
| Precise relevance scoring | May miss edge-case synonyms |

**Alternatives Considered:**

1. **Keyword-based search (ripgrep, grep)**
   - **Why not:** Requires exact text matches, misses semantic similarity
   - **Example:** Query "handle concurrent access" wouldn't find "race conditions"

2. **Full-text search (Elasticsearch, Solr)**
   - **Why not:** Overkill for single-project use, requires separate service
   - **Example:** 500MB+ memory, network latency, complex setup

3. **Cursor Rules only**
   - **Why not:** All content loaded upfront, 96% irrelevant, context overflow
   - **Example:** 50KB loaded, only 2KB relevant, 12,500 tokens wasted

4. **API-based embeddings (OpenAI)**
   - **Why not:** Cost per query, latency, requires internet, privacy concerns
   - **Example:** $0.0001 per query × 1000 queries = $0.10, but adds 200ms latency

---

## RAG Engine Design

### Chunking Strategy

**Decision:** Semantic chunking that respects markdown structure.

**Implementation:**
```python
def chunk_markdown(content: str) -> List[Chunk]:
    """
    Split markdown by semantic boundaries:
    - Headers (h1-h6)
    - Code blocks (maintain integrity)
    - Lists (keep grouped)
    - Paragraphs (natural breaks)
    
    Target: 200-800 tokens per chunk for optimal embedding quality.
    """
```

**Why semantic, not fixed-size:**
- Fixed-size chunks (e.g., 512 tokens) split mid-sentence, mid-code
- Semantic chunks maintain context integrity
- Headers provide natural topic boundaries
- Code blocks must stay intact for understanding

**Trade-offs:**
- **Pro:** Contextually complete chunks, better search relevance
- **Con:** Variable chunk sizes (100-1000 tokens), less predictable memory

### Vector Embeddings

**Decision:** Local `sentence-transformers` (all-MiniLM-L6-v2) stored in LanceDB.

**Rationale:**
1. **Local execution** - No API dependency, works offline
2. **Fast** - 384-dimensional vectors, efficient cosine similarity
3. **Good quality** - MTEB benchmark: 58.8% (sufficient for code/docs)
4. **Small** - 80MB model size
5. **Free** - No per-query costs

**Performance characteristics:**

| Metric | Value | Context |
|--------|-------|---------|
| Query latency | ~45ms | 95th percentile: 82ms |
| Embedding time | ~5ms/chunk | Parallelized on indexing |
| Memory usage | ~200MB | Includes model + index |
| Index build | ~60s | 500 markdown files |
| Relevance | 95% | Human-evaluated on test queries |

**Alternative: OpenAI embeddings (text-embedding-3-small)**
- **Pro:** Higher quality (62.3% MTEB), 1536 dimensions
- **Con:** $0.02 per 1M tokens, 150ms latency, requires API key
- **Decision:** Local is sufficient, avoid external dependencies

### Context Reduction

**The "Lost in the Middle" problem:**

Research shows LLMs struggle with information buried in long contexts. Relevant content at position 30% (in a 10,000-token context) has 65% attention quality.

**Our solution:**
- Load only top 3-5 chunks (2-5KB total)
- Chunks ranked by cosine similarity
- Present in order of relevance (most relevant first)

import ContextReductionComparison from '@site/src/components/ContextReductionComparison';

<ContextReductionComparison />

---

## Workflow Engine Design

### The Phase Skipping Problem

**Background:** AI agents have a strong tendency to "shortcut" multi-phase processes:
- Skip requirements → jump to implementation
- Skip design → code directly
- Skip tests → mark as "TODO"

Traditional approaches failed:
- ❌ "Please don't skip phases" (ignored 70% of the time)
- ❌ Bold warnings "**DO NOT SKIP**" (ignored 50% of the time)
- ❌ Repeated reminders (attention degradation)

### Design Decision: Architectural Enforcement

**Decision:** Phase gating enforced in code, not documentation.

**Implementation:**
```python
class WorkflowState:
    current_phase: int = 0
    completed_phases: List[int] = []
    
    def get_phase_content(self, phase: int) -> Optional[PhaseContent]:
        """AI can ONLY access current or completed phases."""
        if phase == self.current_phase:
            return self._load_phase(phase)
        if phase in self.completed_phases:
            return self._load_phase(phase)  # Review previous
        return None  # Future phases: structurally inaccessible
    
    def complete_phase(self, phase: int, evidence: dict) -> Result:
        """Validate evidence before advancing."""
        if phase != self.current_phase:
            return Result.error("Cannot complete non-current phase")
        
        checkpoint = self._load_checkpoint(phase)
        missing = checkpoint.validate(evidence)
        
        if missing:
            return Result.error(f"Missing evidence: {missing}")
        
        self.completed_phases.append(phase)
        self.current_phase = phase + 1
        return Result.success()
```

**Why this works:**
- AI **cannot** call `get_phase_content(phase=2)` when `current_phase=1`
- The tool returns `None` - no content to act on
- Phase advancement requires explicit evidence submission
- State persists across sessions (file-based)

**Trade-offs:**

| Benefit | Limitation |
|---------|------------|
| 100% phase order enforcement | Cannot parallelize phases |
| Evidence-based validation | Requires explicit checkpoint design |
| Resumable workflows | State file must be preserved |
| Audit trail (all evidence logged) | More complex than free-form execution |

**Alternatives Considered:**

1. **Documentary enforcement (warnings)**
   - **Why not:** Ignored 50-70% of the time
   - **Evidence:** Tested with 100 workflows, 68% skipped at least one phase

2. **Human approval between phases**
   - **Why not:** Breaks flow, requires constant human attention
   - **Use case:** Better for critical systems (we may add optional mode)

3. **Time-based locks (must wait 5 minutes per phase)**
   - **Why not:** Arbitrary, doesn't ensure quality, frustrating

4. **LLM fine-tuning to never skip**
   - **Why not:** No control over user's LLM, fine-tuning is expensive
   - **Observation:** GPT-4 still skips despite being "more compliant"

### Checkpoint System

**Design:** Each phase defines required evidence in `phase.md`:

```markdown
### Phase 1 Validation Gate

🛑 **Checkpoint:**
Before advancing to Phase 2, provide evidence:
- `requirements_documented`: List of all requirements
- `acceptance_criteria`: Testable success criteria
- `stakeholders_identified`: Who approved these?
```

**Workflow engine parses this dynamically:**
```python
checkpoint = {
    "requirements_documented": {"type": "list", "min_items": 3},
    "acceptance_criteria": {"type": "list", "min_items": 2},
    "stakeholders_identified": {"type": "string"}
}

# AI submits evidence
evidence = {
    "requirements_documented": ["Req1", "Req2", "Req3"],
    "acceptance_criteria": ["AC1", "AC2"],
    "stakeholders_identified": "Product team"
}

# Validation
result = validate_checkpoint(checkpoint, evidence)  # ✅ Pass
```

**Why dynamic checkpoints:**
- Checkpoints defined in docs (easy to update)
- No code changes to modify workflow gates
- Each workflow can have custom evidence requirements
- Supports spec-driven workflows (checkpoints in `tasks.md`)

---

## Standards System Design

### The Language Brittleness Problem

**Background:** Documentation is typically:
1. **Language-agnostic** (too vague): "Use proper synchronization"
2. **Language-specific** (too narrow): "Use Python's `threading.Lock()`"

Neither scales:
- Vague docs → AI guesses → 40% error rate
- Specific docs → Only works for one language → Rewrite for each language

**Example:** Race conditions exist in Python, Go, Rust, JavaScript, Java, C++, C#...
- Universal principle: "Multiple threads, shared state, at least one write"
- Python-specific: `threading.Lock()`, `asyncio.Lock()`, GIL behavior
- Go-specific: `sync.Mutex`, channels, goroutine safety, `-race` detector
- Rust-specific: `Mutex<T>`, `Arc`, ownership rules prevent most races

### Design Decision: Universal + Generated

**Decision:** Write once (universal), generate many (language-specific).

**Architecture:**

import StandardsGenerationFlow from '@site/src/components/StandardsGenerationFlow';

<StandardsGenerationFlow />

**Universal Standard Structure Example:**

**Race Conditions (Universal)**

**Definition**  
Race condition occurs when:
1. Multiple execution contexts access shared state
2. At least one performs a write operation
3. Timing affects the result

**Detection**
- Non-deterministic behavior
- "Works on my machine" bugs
- Sporadic test failures

**Prevention**
- Mutual exclusion (locks)
- Atomic operations
- Immutable data structures
- Message passing (actor model)

**Testing**
- Run tests under load (10x parallelism)
- Use race detectors
- Property-based testing with random scheduling

---

**Generated Python-Specific Standard Example:**

**Race Conditions (Python)**

**Python-Specific Concerns**

*GIL (Global Interpreter Lock)*
- Protects Python object access
- Does NOT prevent race conditions
- Switching happens between bytecode instructions

*Threading Module*
```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    with lock:  # Acquire lock
        counter += 1  # Critical section
```

*Asyncio Module*
```python
import asyncio

counter = 0
lock = asyncio.Lock()

async def increment():
    global counter
    async with lock:
        counter += 1
```

*Testing with pytest*
```python
import pytest
import threading

def test_race_condition():
    counter = 0
    lock = threading.Lock()
    
    def worker():
        nonlocal counter
        for _ in range(1000):
            with lock:
                counter += 1
    
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    assert counter == 10000  # Would fail without lock
```

**Generation process:**
1. **Detect project language** (pyproject.toml, package.json, go.mod, etc.)
2. **Analyze frameworks** (FastAPI, Django, Express, Gin, etc.)
3. **Read universal standard** (timeless principles)
4. **Generate language-specific** (syntax, idioms, stdlib, frameworks)
5. **Cross-reference** (link back to universal)

**Trade-offs:**

| Benefit | Limitation |
|---------|------------|
| Write once, apply everywhere | Generation requires LLM call (one-time) |
| Consistent principles across languages | Generated content may need human review |
| Tailored to actual project frameworks | Regenerate when project changes significantly |
| Timeless universal standards | Language-specific may age (Python 3.8 → 3.13) |

**Alternatives Considered:**

1. **Manual language-specific docs**
   - **Why not:** 8 languages × 50 standards = 400 docs to maintain
   - **Cost:** Unsustainable, docs drift, inconsistencies

2. **Pure universal (no language-specific)**
   - **Why not:** AI guesses syntax, 40% error rate
   - **Example:** "Use a lock" → AI guesses wrong import, wrong syntax

3. **LLM training data only**
   - **Why not:** Not project-specific, outdated, no new patterns
   - **Example:** AI trained on Python 3.7, your project uses 3.12 features

4. **IDE-specific (JetBrains, VSCode extensions)**
   - **Why not:** Ties docs to tooling, not portable
   - **Goal:** Work with any AI assistant (Cursor, Continue, Copilot)

---

## Three-Tier File Architecture

### The Attention Quality Problem

**Research finding:** LLM attention quality degrades with file size:
- Under 100 lines: 95%+ attention quality
- 200-500 lines: 70-85% attention quality
- Over 500 lines: Below 70% attention quality

**Traditional workflow file:** 2000 lines, all phases and tasks in one file
- **Context use:** 90% of model's window
- **Attention quality:** Under 70%
- **Success rate:** 60-65%

### Design Decision: Horizontal Decomposition

**Decision:** Break workflows into three tiers by consumption pattern, not abstraction.

import ThreeTierArchitecture from '@site/src/components/ThreeTierArchitecture';

<ThreeTierArchitecture />

**Why three tiers:**
1. **Different consumption patterns** → Different size requirements
2. **Execution files** loaded every task → Must be tiny
3. **Methodology files** loaded once → Can be larger
4. **Output files** never fully loaded → Unlimited

**Comparison:**

| Approach | File Size | Context Use | Attention Quality | Success Rate |
|----------|-----------|-------------|-------------------|--------------|
| Monolithic (old) | 2000 lines | 90% | Under 70% | 60-65% |
| Three-tier (new) | 30-100 lines | 15-25% | 95%+ | 85-95% |

**Trade-offs:**
- **Pro:** 3-4x improvement in success rate
- **Pro:** Minimal context overhead
- **Con:** More files to maintain (30 vs 1)
- **Con:** Navigation complexity (mitigated by phase.md navigation)

---

## Design Decisions Summary

| Decision | Problem Solved | Trade-off |
|----------|---------------|-----------|
| MCP + RAG | Context overflow (50KB → 5KB) | Indexing overhead (60s first run) |
| Semantic chunking | Maintain context integrity | Variable chunk sizes |
| Local embeddings | Cost, latency, privacy | Slightly lower quality than API |
| Architectural phase gating | AI skips phases (68% → 0%) | No phase parallelization |
| Evidence-based checkpoints | Quality gates bypassed | Explicit checkpoint design needed |
| Universal + generated standards | Language brittleness | One-time LLM generation call |
| Three-tier file architecture | Attention degradation | More files to maintain |
| File watcher for auto-reindex | Stale index | ~50ms filesystem overhead |

---

## Performance Characteristics

### RAG Engine

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Query latency (p50) | 32ms | Under 50ms | ✅ |
| Query latency (p95) | 82ms | Under 100ms | ✅ |
| Index build time | 52s | Under 60s | ✅ |
| Memory footprint | ~200MB | Under 500MB | ✅ |
| Throughput | ~22 qps | Over 10 qps | ✅ |

### Workflow Engine

| Metric | Value |
|--------|-------|
| State save latency | 3-8ms |
| State load latency | 2-5ms |
| Checkpoint validation | 1-2ms |
| Phase transition | Under 10ms |

### Overall Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Context per query | 50KB+ | 2-5KB | 90% reduction |
| Relevant content | 4% | 95% | 24x improvement |
| Messages needed | Baseline | -71% | Behavioral change |
| Cost per month | Baseline | -54% | Even with +59% model cost |
| Success rate | 70% | 92% | 31% improvement |
| Phase skipping rate | 68% | 0% | 100% elimination |

**Key insight:** Technical efficiency (90% context reduction per query) enables behavioral change (71% fewer messages), which drives cost reduction (54%). See [Economics](./economics) for full analysis.

---

## Deployment Model

### Per-Project Installation

**Decision:** Each project gets its own prAxIs OS copy.

**Structure:**

import DeploymentStructure from '@site/src/components/DeploymentStructure';

<DeploymentStructure />

**Why per-project, not global:**

1. **Version control**: Different projects can use different prAxIs OS versions
2. **Customization**: Tailor standards and workflows per project
3. **Isolation**: No cross-contamination between projects
4. **Portability**: Git clone includes prAxIs OS setup
5. **Team consistency**: Everyone uses same version

**Trade-offs:**
- **Pro:** Complete project isolation and customization
- **Con:** ~50MB per project (mostly MCP server Python code)
- **Con:** Updates must be run per project (mitigated by `praxis_os_upgrade_v1` workflow)

**Alternative: Global installation**
- **Why not:** Version conflicts, no per-project customization
- **Example:** Project A needs old workflow, Project B needs new workflow → conflict

---

## Related Documentation

- [How It Works](./how-it-works) - RAG-driven behavioral reinforcement
- [Reference: MCP Tools](../reference/mcp-tools) - Complete tool API
- [Reference: Standards](../reference/standards) - Universal standards index
- [Reference: Workflows](../reference/workflows) - Available workflows
- [Tutorial: Installation](../tutorials/installation) - Set up prAxIs OS
