# Persona Size Research & Recommendation

**Date:** 2025-10-21  
**Status:** Research & Analysis  
**Purpose:** Resolve competing viewpoints on optimal persona file size

---

## The Question

**What is the optimal size for Agent OS Enhanced persona files?**

Current competing claims:
- Architecture doc template: ~50 lines
- Amplifier agents: 300 specialized + 500 generic = 800 total lines
- AI suggestion (unsupported): 150-250 lines

---

## Key Constraint: Personas Are System Prompts

**Critical difference from task files:**

| File Type | Load Pattern | Context Impact | Optimal Size |
|-----------|-------------|----------------|--------------|
| **Task files** | Once per task | Temporary | ≤100 lines (per architecture doc) |
| **Persona files** | Every message | Persistent | ??? (to be determined) |

**The fundamental tradeoff:**
- Larger persona = More expertise embedded = Less discovery needed
- Larger persona = More context used = Less room for actual work
- Smaller persona = More discovery queries = More latency/round trips
- Smaller persona = Less context used = More room for actual work

---

## Architecture Doc Research

From `docs/content/explanation/architecture.md`:

```
Research finding: LLM attention quality degrades with file size:
- Under 100 lines: 95%+ attention quality
- 200-500 lines: 70-85% attention quality
- Over 500 lines: Below 70% attention quality
```

**Source:** "Lost in the Middle" research (2023) - LLMs struggle with buried information

**Applied to personas:**
- 50 lines = ~1,500 tokens = 1.5% of 100K context window
- 150 lines = ~4,500 tokens = 4.5% of context
- 300 lines = ~9,000 tokens = 9% of context
- 800 lines = ~24,000 tokens = 24% of context

**Architecture doc also states:**
> When context exceeds 15-25% of the model's window, attention quality drops below 70%

**Critical insight:** Amplifier's 800-line agents consume 24% of context JUST FOR THE PERSONA.

---

## Amplifier's Approach (800 lines)

**Breakdown:**
```
Amplifier Agent File:
├─ YAML frontmatter: ~10 lines
├─ Specialized content: ~300 lines
│   ├─ Operating modes: ~120 lines
│   ├─ Methodologies: ~100 lines
│   ├─ Decision frameworks: ~50 lines
│   └─ Examples: ~30 lines
└─ Generic Claude Code instructions: ~500 lines
    ├─ Tone and style: ~70 lines
    ├─ Task management: ~80 lines
    ├─ Code conventions: ~60 lines
    ├─ Tool usage: ~90 lines
    ├─ Examples: ~100 lines
    └─ Security/policies: ~100 lines
```

**Analysis:**
- ✅ Rich domain expertise immediately available
- ✅ Operating modes prevent mode-switching queries
- ✅ Decision frameworks embedded
- ❌ 24% context overhead per agent invocation
- ❌ Generic instructions duplicated across all agents
- ❌ Approaching attention degradation threshold

---

## Agent OS Current Approach (~50 lines)

**Breakdown:**
```
Agent OS Persona:
├─ Identity: ~10 lines
├─ Approach (discovery pattern): ~15 lines
├─ Tool list: ~15 lines
└─ Decision protocol: ~10 lines
```

**Analysis:**
- ✅ Minimal context overhead (1.5%)
- ✅ Maximum room for actual work
- ✅ Knowledge compounds via RAG
- ❌ Requires 5-10 queries per task
- ❌ Latency on every discovery
- ❌ No embedded operating modes
- ❌ Light on domain expertise

---

## The Math: Context Budget Analysis

**Scenario: Database schema design task**

### Amplifier Approach (800-line persona)
```
Context Budget: 100,000 tokens

Loaded at start:
- Persona (zen-architect): 24,000 tokens
- User request: 500 tokens
= 24,500 tokens used (24.5%)

Remaining for work: 75,500 tokens

Quality: Approaching degradation threshold (15-25%)
```

### Agent OS Current (50-line persona)
```
Context Budget: 100,000 tokens

Loaded at start:
- Persona: 1,500 tokens
- User request: 500 tokens
= 2,000 tokens used (2%)

Per RAG query (3 queries):
- Query 1: 2,000 tokens
- Query 2: 2,500 tokens
- Query 3: 1,800 tokens
= 6,300 tokens for queries

Total: 8,300 tokens (8.3%)
Remaining for work: 91,700 tokens

Quality: Optimal attention range
```

### Hybrid Approach (150-line persona)
```
Context Budget: 100,000 tokens

Loaded at start:
- Persona: 4,500 tokens
- User request: 500 tokens
= 5,000 tokens used (5%)

Per RAG query (1-2 queries, fewer needed):
- Query 1: 2,000 tokens
= 2,000 tokens for queries

Total: 7,000 tokens (7%)
Remaining for work: 93,000 tokens

Quality: Optimal attention range
```

---

## Empirical Test: What Would We Measure?

**Test scenarios:**

1. **Simple task** (e.g., "Create a User table")
   - Measure: Query count, time to completion, quality
   - Hypothesis: All approaches work, smaller is faster

2. **Complex task** (e.g., "Design multi-tenant auth with RBAC")
   - Measure: Query count, decision quality, implementation correctness
   - Hypothesis: Richer personas make better decisions faster

3. **Novel domain** (e.g., "Design event sourcing system")
   - Measure: Discovery effectiveness, learning curve
   - Hypothesis: Discovery-based shines (RAG has knowledge, persona doesn't)

**What to track:**
- Query count per task
- Time to first implementation
- Implementation correctness (linter errors, test pass rate)
- Context utilization at task completion
- User satisfaction (subjective)

---

## Recommendation: Tiered Persona System

**Don't pick one size - use tiers based on persona type:**

### Tier 1: Lightweight Discovery Personas (50-80 lines)
**Use for:** Domains with rich RAG content, exploratory work

```markdown
# Domain Specialist (~60 lines)

You are a [Domain] Specialist.

## Core Philosophy
[20 lines - your values and approach]

## Discovery Protocol
1. Query: search_standards("how to [task]")
2. Discover: workflow exists?
3. Execute: follow structure or best practices
4. Document: write_standard()

## Essential Tools
[20 lines - tool priorities and usage]

## Quick Reference
[10 lines - most common patterns]
```

**Context cost:** 1.5-2.5% (1,500-2,500 tokens)

### Tier 2: Guided Personas (100-150 lines)
**Use for:** Core domains with established patterns

```markdown
# Domain Specialist (~120 lines)

You are a [Domain] Specialist.

## Core Philosophy
[20 lines]

## Operating Modes
### ANALYZE Mode
[15 lines - when and how]

### DESIGN Mode
[15 lines - when and how]

### IMPLEMENT Mode
[15 lines - when and how]

## Decision Framework
[20 lines - key decisions, when to query deeper]

## Essential Patterns
[20 lines - most common scenarios]

## Discovery Protocol
[15 lines - when to query, what to document]
```

**Context cost:** 3-4.5% (3,000-4,500 tokens)

### Tier 3: Expert Personas (200-250 lines)
**Use for:** Critical domains needing deep expertise

```markdown
# Domain Specialist (~220 lines)

[Everything from Tier 2, plus:]

## Detailed Methodologies per Mode
[60 lines - step-by-step approaches]

## Common Pitfalls & Solutions
[30 lines - what not to do]

## Integration Patterns
[20 lines - how this domain connects to others]

## Advanced Decision Trees
[30 lines - complex scenarios]
```

**Context cost:** 6-7.5% (6,000-7,500 tokens)

---

## Specific Recommendation for Agent OS Enhanced

**Phase 1: Start with Tier 2 (100-150 lines)**

Rationale:
- Balances embedded expertise with discovery
- Reduces query overhead (5-10 → 1-3 queries)
- Stays well under attention degradation threshold
- Adds operating modes (missing from current design)
- Still leaves 92-95% context for actual work

**Structure:**
1. Core Philosophy (20 lines) - domain values
2. Operating Modes (45 lines) - 3 modes × 15 lines each
3. Decision Framework (20 lines) - when to query deeper
4. Essential Patterns (15 lines) - quick reference
5. Discovery Protocol (10 lines) - RAG integration
6. Tools & Workflows (10 lines) - MCP tool usage

= **120 lines total**

**Phase 2: Measure and iterate**
- Track query count per persona
- Measure task completion times
- Monitor context utilization
- Adjust tier assignments based on data

**Phase 3: Optimize per domain**
- Frequently-used personas → Tier 3 (reduce queries)
- Exploratory personas → Tier 1 (maximize flexibility)
- Standard personas → Tier 2 (default)

---

## Comparison Table

| Approach | Size | Context % | Queries/Task | Expertise | Flexibility |
|----------|------|-----------|--------------|-----------|-------------|
| **Amplifier** | 800 lines | 24% | 0-1 | High | Low |
| **Agent OS Current** | 50 lines | 1.5% | 5-10 | Low | High |
| **Tier 1 (Lightweight)** | 60 lines | 2% | 4-7 | Low | High |
| **Tier 2 (Guided)** | 120 lines | 4% | 1-3 | Medium | Medium |
| **Tier 3 (Expert)** | 220 lines | 7% | 0-2 | High | Medium |

---

## Conclusion

**The answer is: It depends on the persona's domain.**

**But if forced to pick ONE size for all personas:**
→ **Tier 2: 100-150 lines (target: 120 lines)**

**Why:**
- 2-3x richer than current (adds modes, frameworks)
- 6-7x smaller than Amplifier (avoids attention degradation)
- Reduces query overhead significantly (5-10 → 1-3)
- Still leaves 95%+ context for actual work
- Can be adjusted per domain over time

**Next steps:**
1. Create Tier 2 template (120 lines)
2. Implement 2-3 personas using template
3. Measure actual query counts and context usage
4. Adjust based on empirical data
5. Document "when to use which tier" guidelines

---

## Open Questions

1. **Generic instructions:** Should we extract these into a shared include rather than duplicating in every persona? (Like Amplifier's bottom 500 lines)

2. **Mode vs. discovery:** Are operating modes worth the space, or should we keep discovery-first philosophy?

3. **Context tracking:** Should we instrument persona invocations to measure actual context usage?

4. **Dynamic sizing:** Could personas grow/shrink based on task complexity?

---

**Status:** Ready for discussion and empirical testing  
**Recommendation:** Proceed with Tier 2 (120 lines) as default, with flexibility to adjust per domain  
**Next Action:** Create reference implementation of Tier 2 persona template

