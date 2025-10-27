# Diagramming Philosophy - Universal Documentation Practice

**Timeless principles for creating effective technical diagrams in documentation.**

**Core Principle:** Visual diagrams add clarity, but must be compact and properly sized. Balance visual structure with readability.

**Inspiration:** BuilderMethods' structured, scannable approach with visual elements.

---

## The BuilderMethods Philosophy

### What They Do:
✅ Numbered sections (1️⃣ 2️⃣ 3️⃣) - Visual structure
✅ Structured layouts - Clear visual hierarchy
✅ Code blocks with syntax highlighting
✅ Clear headings and separation
✅ Compact, focused visuals

### What They Don't Do:
❌ Oversized diagrams that dominate the viewport
❌ ASCII art
❌ Complex, overwhelming visuals
❌ Static images (PNG/JPG)

### Key Insight:
BuilderMethods uses **visual structure** (numbered sections, clear layout), not just plain text. We should too, but **keep it compact**.

---

## The Compact React Component Standard

### Philosophy:
Use React components for visual diagrams, but **keep them compact** and **properly sized**.

### Requirements for React Diagrams:

**Size Constraints:**
- Max width: 800px (centered)
- Boxes: Compact padding (0.6rem 1rem)
- Icons: 1.25rem (small)
- Font sizes: 0.8rem labels, 600 weight
- Single horizontal line (~60-80px height)
- Must fit in viewport without dominating

**HoneyHive Branding:**
- Primary: `#ff8c5d` (HoneyHive orange)
- Border: `#ff6b35` (darker orange)
- Background: `rgba(255, 140, 93, 0.08)` (subtle orange tint)
- All cards use orange (not rainbow colors)

**Examples:**
- **`RAGQueryFlow.tsx`** - Single horizontal flow with 4 boxes
- **`DataFlowDiagram.tsx`** - Horizontal flow with split middle box
- **`StandardsFlowDiagram.tsx`** - Two-tier layout (older style, still compact)

**Files:** 
- `/docs/src/components/CompactDiagram.module.css` - Shared horizontal flow styles
- `/docs/src/components/StandardsFlowDiagram.module.css` - Two-tier styles

**Key Pattern (Horizontal Flow):**
```tsx
<div className={styles.compactFlow}>
  <div className={styles.flowBox}>
    <span className={styles.flowIcon}>🔍</span>
    <span className={styles.flowLabel}>Label</span>
  </div>
  <span className={styles.flowArrow}>→</span>
  {/* more boxes */}
</div>
```

---

## Standard Patterns (In Priority Order)

### Pattern 1: Compact React Component (Key Concepts)

**Use for:** Important conceptual relationships that benefit from visual structure

**When to use:**
- Process flows (A → B → C → D)
- Architecture overviews with 3-5 components
- Data flows showing relationships
- Any flow that needs visual clarity

**Horizontal Flow (Preferred):**
- Single line, boxes with arrows
- Max 5 elements per row
- See `RAGQueryFlow.tsx`, `DataFlowDiagram.tsx`

**Two-Tier Layout (When Needed):**
- Comparisons (Universal → Generated)
- See `StandardsFlowDiagram.tsx`

**Requirements:**
```css
/* Size constraints */
max-width: 900px;
padding: 1.5rem;
margin: 1.5rem auto;

/* Card sizing */
.card {
  padding: 0.75rem 1rem;  /* Compact, not huge */
  border-radius: 8px;
  font-size: 0.9rem;      /* Readable but not oversized */
}

/* Icon sizing */
.icon {
  font-size: 1.5rem;      /* Not 2rem+ */
}

/* HoneyHive orange theme */
.card {
  background: rgba(255, 140, 93, 0.08);
  border: 2px solid #ff6b35;
}
```

**Template: Use `StandardsFlowDiagram` as Reference**
- Location: `docs/src/components/StandardsFlowDiagram.tsx`
- Copy the structure and styling
- Adjust content for your use case

**Example:**
```tsx
// YourDiagram.tsx
import React from 'react';
import styles from './StandardsFlowDiagram.module.css'; // Reuse styles

export default function YourDiagram() {
  return (
    <div className={styles.container}> {/* Compact, centered */}
      <div className={styles.tier}>
        <h3 className={styles.tierTitle}>Section A</h3>
        <div className={styles.card}>
          <div className={styles.cardIcon}>🎯</div>
          <div className={styles.cardTitle}>Concept</div>
        </div>
      </div>
      <div className={styles.arrow}>
        <div className={styles.arrowLine}></div>
        <div className={styles.arrowLabel}>Transform</div>
        <div className={styles.arrowHead}>→</div>
      </div>
      <div className={styles.tier}>
        <h3 className={styles.tierTitle}>Section B</h3>
        <div className={styles.card}>
          <div className={styles.cardIcon}>✨</div>
          <div className={styles.cardTitle}>Result</div>
        </div>
      </div>
    </div>
  );
}
```

**Limit:** Max 1-2 React diagrams per doc page

---

### Pattern 2: Numbered Flow (Process Steps)

**Use for:** Installation steps, workflows, sequential processes

```markdown
## Installation Process

**1️⃣ Base Installation**

Run the base installer to install prAxIs OS to your home directory:

```bash
curl -sSL https://github.com/honeyhiveai/praxis-os | sh
```

This creates `~/.praxis-os/` with the default profile containing standards, workflows, and commands.

**What gets installed:**
- Standards from your chosen profile
- Commands adapted for your adapted modes
- Agents and workflows configured for your project

**2️⃣ Project Installation**

Navigate to your project:

```bash
cd /path/to/your/project
```

Install prAxIs OS:

```bash
~/.praxis-os/scripts/project-install.sh
```

This installer will use your defaults from `~/.praxis-os/config.yml` to prompt you for:
- Which profile to use (default: `default`)
- Whether to enable multi-agent mode (for Claude Code)
- Whether to enable single-agent mode (for all other tools)

**What gets installed:**
- `.praxis-os/` folder with standards and commands
- `.claude/` folder with agents and commands (only in multi-agent mode)

**3️⃣ Verification**

Verify installation:

```bash
cat .praxis-os/config.yml
```
```

**Key elements:**
- Numbered emoji headers (1️⃣ 2️⃣ 3️⃣)
- Code blocks with language hints
- "What gets installed" bullets
- Clear section breaks

---

### Pattern 3: Text-Based Lists (Simple Content)

**Use for:** Simple lists that don't need visual structure

**Note:** If content feels like it needs visual structure, use Pattern 1 (Compact React) instead.

**Example:**
```markdown
## Benefits

- Write once, apply everywhere
- Consistent principles across languages
- Tailored implementation guidance per project
```

**Language emoji reference (for inline use):**
- 🐍 Python
- 🔷 Go  
- 🦀 Rust
- ☕ Java
- #️⃣ C#
- 📦 TypeScript/JavaScript
- 💎 Ruby
- 🐘 PHP

---

### Pattern 4: Feature Grid (Options/Capabilities)

**Use for:** Feature lists, mode comparisons, configuration options

```markdown
## Agent Modes

**Single-Agent Mode** 🎯

Works with any AI coding tool (Cursor, Codex, Gemini, Windsurf, etc.)

→ Use when your tool doesn't support subagents
→ prAxIs OS serves as the orchestrator
→ Feeding generated prompts to your AI coding agent

**Multi-Agent Mode** 🤖

Currently only available for Claude Code

→ Specialized subagents work autonomously in parallel
→ More efficient, hands-off development
→ Design validation, concurrency analysis, test generation

**How to choose:**
- Using Cursor, Codex, Gemini? → Single-agent mode
- Using Claude Code? → Multi-agent mode (optional)
```

**Key elements:**
- Mode headers with emojis
- Brief description line
- Arrow bullets (→)
- Decision guidance at bottom

---

### Pattern 5: Metric Callouts (Stats/Results)

**Use for:** Performance metrics, improvements, benchmarks

```markdown
## Performance Results

**Context Efficiency**

📊 **90% reduction** in context size (50KB → 2-5KB)
📊 **24x improvement** in relevance (4% → 95%)
📊 **95% reduction** in token usage (12,500 → 625)

**Query Performance**

⚡ **45ms average** query latency (< 100ms requirement)
⚡ **22 queries/sec** throughput (> 10 qps requirement)
⚡ **50 seconds** index build time (< 60s requirement)
```

**Key elements:**
- Chart emoji (📊) or bolt (⚡)
- Bold metrics
- Parenthetical details
- Grouped by category

---

### Pattern 6: Comparison Table (Side-by-Side)

**Use for:** Before/after, option comparison, feature matrices

```markdown
## Context Efficiency Comparison

| Metric | Before (RAG-Lite) | After (MCP/RAG) | Improvement |
|--------|-------------------|-----------------|-------------|
| **Avg context size** | 50KB+ | 2-5KB | 90% reduction |
| **Relevant content** | 4% | 95% | 24x improvement |
| **Token usage** | 12,500 | 625 | 95% reduction |
| **Query cost** | High | Low | 95% reduction |
```

**Key elements:**
- Bold column headers
- Bold metric names in first column
- Visual alignment
- "Improvement" column for impact

---

### Pattern 7: Concept Hierarchy (Nested Structure)

**Use for:** Component breakdowns, file structures, taxonomies

```markdown
## MCP Server Structure

**Core Engines**
→ RAG Engine (Vector search with LanceDB)
→ Workflow Engine (Phase gating, state management)
→ State Manager (Workflow persistence)

**Configuration**
→ Loader (Configuration management)
→ Validator (Path validation)
→ Models (Config, workflow, RAG schemas)

**Server Layer**
→ Factory (Server initialization)
→ Tools (RAG search, workflow control)
→ Protocol (MCP communication)
```

**Key elements:**
- Bold category headers
- Arrow bullets (→)
- Parenthetical descriptions
- Flat hierarchy (not nested bullets)

---

## When to Use Mermaid (Rare)

**Only use Mermaid for:**
- Complex technical architecture (8+ interconnected components)
- Data flow diagrams with multiple conditional paths
- State machines with many transitions

**Consider Compact React Component first** - it's usually better

**Requirements if using Mermaid:**
- Must use HoneyHive orange theme (see below)
- Keep it simple (< 10 nodes)
- Ask: Could a compact React component do this better?

**Mermaid theme template:**
```markdown
\`\`\`mermaid
%%{init: {'theme':'base', 'themeVariables': { 
  'primaryColor':'#ff8c5d',
  'primaryTextColor':'#fff',
  'primaryBorderColor':'#ff6b35',
  'lineColor':'#ff8c5d',
  'secondaryColor':'#1a1d24',
  'tertiaryColor':'#2d3139',
  'fontFamily':'Inter'
}}}%%
graph LR
    A[Component A] -->|Action| B[Component B]
    
    style A fill:#ff8c5d,stroke:#ff6b35,stroke-width:2px,color:#0a0c10
    style B fill:#1a1d24,stroke:#ff8c5d,stroke-width:2px,color:#fff
\`\`\`
```

---

## Implementation Guide

### For AI Agents (Me):

When creating documentation, follow this decision tree:

1. **Does it need visual structure?** → Use Pattern 1 (Compact React Component)
   - Two-tier relationships
   - Multi-step flows
   - Concept comparisons
   - Architecture overviews
   
2. **Is it a simple list?** → Use Pattern 3 (Text-Based Lists)

3. **Is it a process with steps?** → Use Pattern 2 (Numbered Flow)

4. **Is it features/options?** → Use Pattern 4 (Feature Grid)

5. **Is it metrics/stats?** → Use Pattern 5 (Metric Callouts)

6. **Is it a comparison?** → Use Pattern 6 (Table)

7. **Is it a structure/hierarchy?** → Use Pattern 7 (Nested)

8. **Is it extremely complex architecture?** → Consider Mermaid (rare)

**Prefer visual structure (Pattern 1) over plain text when it adds clarity.**

### Creating New React Components:

1. Copy `StandardsFlowDiagram.tsx` and `.module.css`
2. Keep the same size constraints
3. Use HoneyHive orange branding
4. Test that it fits in viewport (1440x900)
5. Verify mobile responsive

---

## Quick Reference Card

### Emoji Library:
```
Process: 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣
Languages: 🐍 🔷 🦀 ☕ #️⃣ 📦 💎 🐘
Arrows: → ↓ ←
Modes: 🎯 🤖 ⚡
Metrics: 📊 ⚡ ✅ ❌
Actions: ✓ ✗ ⚠️
```

### Text Formatting:
```markdown
**Bold** for headers and emphasis
`code` for technical terms
→ for list items
> for callouts/notes
```

### Code Blocks:
```markdown
\`\`\`bash
# Always specify language
command here
\`\`\`

\`\`\`python
# For better syntax highlighting
code here
\`\`\`
```

---

## Examples to Follow

### ✅ Perfect (Compact React Component):
**See:** `docs/content/standards.md` - StandardsFlowDiagram

- Compact, fits in viewport
- HoneyHive orange branding
- Clear visual structure
- Interactive hover states
- Mobile responsive

### ✅ Good (Numbered Flow):
```markdown
## Installation Process

**1️⃣ Base Installation**

Run the base installer:

\`\`\`bash
curl -sSL https://example.com/install | sh
\`\`\`

**2️⃣ Project Installation**

Navigate to your project and install.
```

### ❌ Bad Examples:

**Oversized React Component:**
- Takes up entire viewport
- Cards too large (2rem+ padding)
- Icons too big (3rem+)
- Dominates the page

**Plain Text When Visual Structure Needed:**
- Just bullet points for complex relationships
- No visual hierarchy
- Hard to scan

**ASCII Diagrams:**
- Breaks in different fonts
- Not accessible
- Looks unprofessional

---

## Current Implementation Status

### ✅ Completed:

1. **standards.md** - StandardsFlowDiagram component
   - Compact React component (two-tier) ✅
   - HoneyHive orange branding ✅
   - Fits in viewport ✅

2. **architecture.md** - Converted Mermaid → React
   - RAGQueryFlow (horizontal, 4 boxes) ✅
   - DataFlowDiagram (horizontal, split middle) ✅
   - Uses CompactDiagram.module.css ✅
   - **These are the new gold standard for horizontal flows**

3. **how-it-works.md** 
   - Mostly text ✅
   - Could benefit from a workflow diagram (compact React) if needed

---

## Maintenance

### Adding New Docs:

1. Write content in plain text first
2. Identify sections that might benefit from patterns
3. Apply appropriate pattern from this guide
4. Review: Would text alone be clearer?
5. If yes, keep it text

### Quarterly Audit:

- Review all diagrams
- Ask: "Would text be clearer?"
- Remove unnecessary visuals
- Ensure emoji consistency
- Verify HoneyHive orange in any Mermaid

---

## Why This Works

**Scannable:** Eyes move faster through text than complex visuals
**Accessible:** Screen readers work perfectly
**Copy-paste friendly:** Code blocks are usable
**Mobile-optimized:** Text reflows naturally
**Maintainable:** Easy to update, no design tools needed
**Professional:** BuilderMethods proves this approach works

**Remember:** The best diagram is often no diagram.

