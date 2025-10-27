# ASCII Diagram Inventory - Conversion to React Components

**Date:** 2025-10-13
**Purpose:** Inventory of all ASCII diagrams in Agent OS Enhanced documentation that need to be converted to React components per `documentation-diagrams.md` standard.

---

## Summary

**Total files with ASCII diagrams:** 8

1. `explanation/architecture.md` - MCP architecture diagram
2. `explanation/how-it-works.md` - Context degradation examples  
3. `tutorials/intro.md` - Project structure tree
4. `tutorials/installation.md` - Project structure tree
5. `tutorials/your-first-agent-os-project.md` - (checking)
6. `explanation/specs-knowledge-compounding.md` - (checking)
7. `how-to-guides/create-custom-workflows.md` - Directory structure trees
8. `reference/workflows.md` - (checking)

---

## Detailed Inventory

### 1. `explanation/architecture.md`

**Line 53-84:** MCP System Architecture Diagram
```
┌─────────────────────────────────────────────────────────┐
│                   Cursor AI Agent                       │
│  (Claude, GPT-4, etc. via MCP client)                  │
└────────────────┬────────────────────────────────────────┘
                 │ MCP Protocol
                 ↓
┌─────────────────────────────────────────────────────────┐
│              MCP Server (stdio transport)               │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Tool Registry                       │   │
│  │  • search_standards                              │   │
│  │  • start_workflow                                │   │
│  │  • complete_phase                                │   │
│  │  • get_workflow_state                            │   │
│  └────────────┬──────────────────┬──────────────────┘   │
│               │                  │                       │
│               ↓                  ↓                       │
│  ┌───────────────────┐  ┌──────────────────────┐        │
│  │    RAG Engine     │  │  Workflow Engine     │        │
│  │  • Vector search  │  │  • Phase gating      │        │
│  │  • Chunking       │  │  • State mgmt        │        │
...
```

**Type:** System architecture flow
**Conversion:** Create `MCPArchitectureDiagram.tsx` component
**Complexity:** High - nested boxes, vertical layout, multiple components

---

### 2. `explanation/how-it-works.md`

**Line 64-71:** Context degradation visualization
```
├── Initial orientation: 15,000 tokens (75% of context)
└── User message: 5,000 tokens (25%)

├── Initial orientation: 15,000 tokens (still 15k)
├── 29 messages: 2,485,000 tokens (99.4%)
└── Latest message: 5,000 tokens
```

**Type:** Tree/hierarchy showing context growth
**Conversion:** Could be a simple list with icons or stay as code block (informational)
**Complexity:** Low - might not need conversion (data visualization)

---

### 3. `tutorials/intro.md`

**Line 40-48:** Basic project structure
```
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

**Type:** Directory tree structure
**Conversion:** Keep as code block (standard file tree format) OR create `ProjectStructureDiagram.tsx`
**Complexity:** Low-Medium - tree structure
**Decision needed:** File trees are commonly shown as ASCII - may not need conversion

---

### 4. `tutorials/installation.md`

**Line 31-50:** Detailed project structure
```
├── .cursorrules                  # 26 lines - AI behavioral triggers
├── .praxis-os/
│   ├── standards/
│   │   ├── universal/            # Copied from repo
│   │   │   ├── concurrency/      # Race conditions, deadlocks, etc.
│   │   │   ├── architecture/     # SOLID, DI, API design
│   │   │   ├── testing/          # Test pyramid, test doubles
│   │   │   ├── failure-modes/    # Circuit breakers, retries
│   │   │   └── security/         # Security patterns
│   │   └── development/          # Generated for your language
│   │       ├── python-concurrency.md  # (if Python project)
│   │       ├── python-testing.md
│   │       └── python-architecture.md
│   ├── usage/                    # How to use Agent OS Enhanced
│   ├── workflows/                # Phase-gated workflows
│   │   ├── spec_creation_v1/
│   │   └── spec_execution_v1/
│   ├── mcp_server/               # MCP/RAG server (copied)
│   │   ├── __main__.py
│   │   ├── rag_engine.py
```

**Type:** Directory tree structure (detailed)
**Conversion:** Keep as code block (file tree) OR create component if needed
**Complexity:** Low-Medium
**Decision needed:** Standard practice is to show file trees as ASCII in code blocks

---

### 5. `tutorials/your-first-agent-os-project.md`

**Line 142-146:** Spec directory structure
```
  ├── README.md           # Specification overview
  ├── srd.md             # Software Requirements Document
  ├── specs.md           # Technical specification
  ├── tasks.md           # Implementation tasks
  └── implementation.md  # Implementation guidance
```

**Type:** Directory tree structure
**Conversion:** Keep as code block (standard file tree format)
**Complexity:** Low
**Decision:** File trees are informational and commonly shown as ASCII

---

### 6. `explanation/specs-knowledge-compounding.md`

**Line 37-41:** Spec directory structure (similar to above)
```
├── README.md           # Executive summary
├── srd.md             # System Requirements Document
├── specs.md           # Technical specifications
├── tasks.md           # Implementation breakdown
└── implementation.md  # Detailed implementation guidance
```

**Type:** Directory tree structure
**Conversion:** Keep as code block (file tree)
**Complexity:** Low
**Decision:** Informational, standard format

---

### 7. `how-to-guides/create-custom-workflows.md`

**Line 229-238:** Workflow directory structure
```
├── metadata.json           # Workflow definition (required)
├── phases/
│   ├── 0/
│   │   ├── phase.md       # Phase overview (~80 lines) - NOT README.md
│   │   ├── task-1-name.md # Task files (100-170 lines each)
│   │   └── task-2-name.md
│   ├── 1/
│   ├── 2/
│   └── 3/
└── core/                   # Optional supporting docs
```

**Line 349-360:** Example workflow structure
```
├── metadata.json
├── phases/
│   ├── 0/
│   │   ├── phase.md
│   │   └── task-1-analyze.md
│   ├── 1/
│   │   ├── phase.md
│   │   └── task-1-generate.md
│   └── 2/
│       ├── phase.md
│       └── task-1-review.md
└── README.md
```

**Type:** Directory tree structures (2 instances)
**Conversion:** Keep as code blocks (file trees)
**Complexity:** Low
**Decision:** Instructional file trees, standard format

---

### 8. `reference/workflows.md`

**Line 349-360:** (Appears to be same as above in create-custom-workflows)

**Type:** Directory tree structure
**Conversion:** Keep as code block
**Complexity:** Low
**Decision:** Reference material, standard format

---

## Conversion Priority Analysis

### 🔴 HIGH PRIORITY - Must Convert

**1. `explanation/architecture.md` - MCP System Architecture (Line 53-84)**
- **Why:** This is a complex system architecture diagram showing relationships between components
- **Impact:** Central to understanding Agent OS Enhanced architecture
- **Complexity:** High (nested boxes, arrows, multiple layers)
- **Existing Similar Component:** See `StandardsFlowDiagram.tsx` for reference pattern
- **New Component:** `MCPArchitectureDiagram.tsx`

**2. `explanation/how-it-works.md` - Decision Flow Diagrams (Line 117-139)**
- **Why:** Shows probabilistic decision-making and RAG impact
- **Impact:** Core concept explanation
- **Complexity:** Medium (text boxes with annotations)
- **New Component:** `RAGDecisionFlowDiagram.tsx` (shows "Without RAG" vs "With RAG")

---

### 🟡 MEDIUM PRIORITY - Consider Converting

**3. `explanation/how-it-works.md` - Self-Reinforcing Loop (Line 93-104)**
- **Why:** Shows workflow cycle with arrows
- **Impact:** Explains key behavioral mechanism
- **Complexity:** Medium (step-by-step flow)
- **Decision:** Could be React component or styled code block
- **Potential Component:** `SelfReinforcingLoopDiagram.tsx`

---

### 🟢 LOW PRIORITY - Keep as Code Blocks

**4. Context Degradation Examples (how-it-works.md lines 63-73, 152-172)**
- **Why:** Simple data/stats display, not relationship diagrams
- **Decision:** Keep as code blocks (informational, not architectural)

**5. All Directory Tree Structures (8 instances across 5 files)**
- **Why:** Standard file tree format, universally understood as ASCII
- **Decision:** Keep as code blocks (standard practice for file trees)
- **Examples:**
  - `tutorials/intro.md` (project structure)
  - `tutorials/installation.md` (project structure)
  - `tutorials/your-first-agent-os-project.md` (spec structure)
  - `explanation/specs-knowledge-compounding.md` (spec structure)
  - `how-to-guides/create-custom-workflows.md` (workflow structures x2)

---

## Conversion Plan

### Phase 1: Critical Architecture Diagrams

1. **Create `MCPArchitectureDiagram.tsx`**
   - Location: `docs/src/components/MCPArchitectureDiagram.tsx`
   - Styling: `MCPArchitectureDiagram.module.css`
   - Replace: `explanation/architecture.md` lines 52-85

2. **Create `RAGDecisionFlowDiagram.tsx`**
   - Location: `docs/src/components/RAGDecisionFlowDiagram.tsx`
   - Styling: Reuse `CompactDiagram.module.css` or extend
   - Replace: `explanation/how-it-works.md` lines 116-139

### Phase 2: Optional Enhancement

3. **Create `SelfReinforcingLoopDiagram.tsx`** (if decided)
   - Location: `docs/src/components/SelfReinforcingLoopDiagram.tsx`
   - Replace: `explanation/how-it-works.md` lines 92-104

### Phase 3: Review & Cleanup

4. Review all replaced sections in docs
5. Test light/dark mode rendering
6. Verify responsive design
7. Update component index if needed

---

## Standards References

- `.praxis-os/standards/development/documentation-diagrams.md` - Diagram standards
- `.praxis-os/standards/development/documentation-theming.md` - Theming variables
- Existing components: `StandardsFlowDiagram.tsx`, `DataFlowDiagram.tsx`, `RAGQueryFlow.tsx`

---

## Summary

**Total ASCII Diagrams Found:** 15+ instances across 8 files

**Conversion Required:**
- ✅ 2 complex architectural/flow diagrams (HIGH PRIORITY)
- ⚠️ 1 optional loop diagram (MEDIUM PRIORITY)
- ❌ 12+ informational/data displays and file trees (KEEP AS-IS)

**Estimated Effort:**
- Phase 1: 2-3 components (HIGH priority)
- Phase 2: 1 component (OPTIONAL)
- Total: 2-4 new React components


