# RAG Discovery Scaling Patterns

**Type:** Local-only (framework development)

**Audience:** prAxIs OS framework developers

**Status:** Active - Architectural guidance

**Keywords:** RAG scaling challenges, semantic overlap corpus growth, discovery degradation, routing accuracy at scale, large knowledge base problems, namespacing strategies, vocabulary differentiation, index partitioning, discoverability ceiling, standards proliferation impact

**NOT covered here:** RAG implementation details (see `mcp-rag-configuration.md`), content authoring basics (see `rag-content-authoring.md`)

---

## 🎯 TL;DR - The Discovery Ceiling

**The Problem:** As standards corpus grows (60 → 100 → 200+), semantic overlap increases and single-query routing accuracy degrades.

**Current State (60 standards):**
- Single-query hit rate: ~33% for niche topics
- Multi-query (2-3 queries) hit rate: ~90%
- Acceptable for current scale

**Projected State (200+ standards):**
- Single-query hit rate: likely <20%
- Multi-query may require 4-6 attempts
- Risk: Agents give up and guess (adversarial design failure)

**This standard documents:**
- Why scaling degrades discovery
- What mitigation strategies exist
- When to apply each strategy
- How to monitor discovery health

---

## ❌ The Problem - Discovery Degrades with Scale

### Why Semantic Overlap Increases

**Small corpus (10-30 standards):**
- Each standard covers distinct domain
- Minimal vocabulary overlap
- Clear semantic separation
- Single-query routing effective

**Medium corpus (60-100 standards):**
- Multiple standards reference same concepts
- Example: "workflow", "testing", "development" appear in 10+ docs
- Vocabulary overlap creates confusion
- Single-query accuracy drops to 30-50%

**Large corpus (200+ standards):**
- Massive vocabulary overlap
- Every standard about "development" competes
- Even specific queries return 10+ plausible matches
- Single-query routing unreliable

### The Math of Semantic Dilution

```
Routing Accuracy ≈ 1 / (Semantic Overlap Factor)

Small corpus:  1 / 2  = 50% accuracy
Medium corpus: 1 / 3  = 33% accuracy
Large corpus:  1 / 5  = 20% accuracy
```

**Key Insight:** Without mitigation, discovery accuracy naturally degrades as corpus grows.

---

## 🛠️ Mitigation Strategies

### Strategy 1: Aggressive Vocabulary Differentiation

**What:** Use domain-specific synonyms to reduce overlap.

**Example:**
```
Instead of:         Use:
"development"    → "iteration mechanics" (dogfooding) vs "authoring process" (meta-dev)
"consumer"       → "end-user" vs "downstream developer"
"framework"      → "foundation" vs "system"
"MCP server"     → "service implementation" vs "runtime process"
"copy up"        → "promote to source" vs "sync to origin"
```

**When:** Always, especially for frequently-used terms.

**Effectiveness:** Medium (30% → 40% accuracy)

**Cost:** Requires thesaurus thinking, may feel unnatural

---

### Strategy 2: Hierarchical Namespacing

**What:** Organize standards into semantic hierarchies, use folder structure in filenames.

**Example:**
```
Current:                        Namespaced:
dogfooding-model.md          → iteration/local-first-development.md
meta-development-patterns.md → authoring/documentation-philosophy.md
workflow-construction.md     → tasks/definition-authoring.md
```

**When:** Before corpus reaches 100 standards.

**Effectiveness:** High (20% → 50% accuracy) - namespace appears in chunks

**Cost:** Requires reorganization, breaks existing references

---

### Strategy 3: Explicit Routing Index

**What:** Create a meta-standard that maps common queries to target standards.

**Example:**
```markdown
## Query Routing Map

| If Query Contains | Route To |
|-------------------|----------|
| "where to edit", "file locations", "iteration" | dogfooding-model.md |
| "what to document", "API exposure", "bug or misuse" | meta-development-patterns.md |
| "workflow authoring", "task definition" | workflow-construction.md |
```

**When:** When multi-query failure rate exceeds 10%.

**Effectiveness:** Very High (direct routing)

**Cost:** Manual maintenance, can drift out of sync

---

### Strategy 4: Metadata-Based Filtering

**What:** Add YAML frontmatter for semantic filtering.

**Example:**
```yaml
---
domain: ["iteration", "file-management"]
role: ["framework-author"]
phase: ["development"]
---
```

**RAG Enhancement:**
```python
# Query with filters
pos_search_project(
    query="where to edit",
    filter_domain="iteration",
    filter_role="framework-author"
)
```

**When:** When corpus exceeds 150 standards.

**Effectiveness:** Very High (reduces search space)

**Cost:** Requires RAG engine changes, metadata maintenance

---

### Strategy 5: Federated Indexes

**What:** Split standards into separate indexes by domain.

**Example:**
```
.praxis-os/.cache/
├── vector_index_universal/      # Consumer-facing standards
├── vector_index_development/    # Framework dev standards
└── vector_index_workflows/      # Workflow/task definitions
```

**When:** When single index exceeds 500 chunks.

**Effectiveness:** Very High (eliminates cross-domain pollution)

**Cost:** Requires agent to know which index to query

---

### Strategy 6: Document Size Limits

**What:** Force splitting of large standards to maintain semantic granularity.

**Rule:** Max 400 lines or 15 chunks per standard.

**Why:** Large standards create diluted chunks that rank poorly.

**Example:**
```
Before: workflow-authoring.md (800 lines, 30 chunks)
After:  
  - workflow-metadata-authoring.md (300 lines)
  - workflow-task-authoring.md (300 lines)
  - workflow-validation.md (200 lines)
```

**When:** Always, enforce during standards creation.

**Effectiveness:** Medium (maintains keyword density)

**Cost:** More files to manage

---

## 📊 Monitoring Discovery Health

### Metrics to Track

**1. Single-Query Hit Rate**
```
Target Standard Appears in Rank 1-3
Measured across 20 common queries per standard
```

**Thresholds:**
- >70%: Excellent (small corpus)
- 40-70%: Good (medium corpus)
- 20-40%: Acceptable (requires multi-query)
- <20%: Problem (consider mitigation)

**2. Multi-Query Success Rate**
```
Target Standard Found Within N Queries
N = 3 is acceptable
N > 5 is problematic
```

**3. Semantic Collision Rate**
```
How Many Standards Share Top 10 Keywords
High collision = high overlap
```

---

## 🔍 Current State Assessment (2025-11-01)

**Corpus Size:** ~60 standards

**Single-Query Hit Rate:** ~33% (dogfooding/meta-dev test)

**Multi-Query Success:** ~90% within 3 queries

**Semantic Collision:** Medium (10-15 standards share "development", "workflow")

**Mitigation Applied:**
- ✅ Strategy 1: Vocabulary differentiation (dogfooding vs meta-dev)
- ⬜ Strategy 2: Hierarchical namespacing (not yet)
- ⬜ Strategy 3: Routing index (not yet)
- ⬜ Strategy 4: Metadata filtering (not implemented in RAG)
- ⬜ Strategy 5: Federated indexes (not yet)
- ✅ Strategy 6: Document size awareness (soft enforcement)

**Verdict:** Current state acceptable for now, but will need Strategy 2 or 4 before reaching 100 standards.

---

## 🎯 Decision Tree: Which Strategy When?

```
Corpus Size < 100 standards
├─ Single-query hit rate > 40%
│  └─ Current state acceptable, continue monitoring
│
└─ Single-query hit rate < 40%
   └─ Apply Strategy 1 (vocabulary differentiation)

Corpus Size 100-200 standards
├─ Multi-query success < 80%
│  └─ Apply Strategy 2 (hierarchical namespacing)
│     OR Strategy 4 (metadata filtering if RAG supports)
│
└─ Specific high-value standards hard to find
   └─ Apply Strategy 3 (routing index for those standards)

Corpus Size > 200 standards
├─ Even multi-query struggling
│  └─ Apply Strategy 5 (federated indexes)
│
└─ Individual standards too large (>500 lines)
   └─ Enforce Strategy 6 (document splitting)
```

---

## ❓ Questions This Answers

**Scaling Concerns:**
1. "Why is discovery getting harder as we add more standards?"
2. "What's the expected discovery accuracy at 100 standards?"
3. "When should we worry about RAG scaling?"
4. "How much semantic overlap is too much?"

**Mitigation Selection:**
5. "Which mitigation strategy should we use first?"
6. "When do we need hierarchical namespacing?"
7. "Should we create a routing index?"
8. "Do we need federated indexes?"
9. "How do we know if vocabulary differentiation is working?"

**Monitoring:**
10. "How do we measure discovery health?"
11. "What's an acceptable single-query hit rate?"
12. "When does multi-query become too expensive?"

**Design Decisions:**
13. "Should we limit standard size?"
14. "How do we organize standards at scale?"
15. "What's the discovery ceiling for prAxIs OS?"

---

## 🔗 Related Standards

**RAG Content Strategy:**
- `rag-content-authoring.md` - Basic optimization techniques
- `query-construction-patterns.md` - How agents should query

**Architecture:**
- `mcp-rag-configuration.md` - RAG implementation details
- `agent-os-architecture.md` - Overall system design

**Meta-Development:**
- `meta-development-patterns.md` - Why this problem exists in framework development
- `dogfooding-model.md` - Example of vocabulary differentiation

---

**Version:** 1.0.0  
**Created:** 2025-11-01  
**Last Updated:** 2025-11-01  
**Next Review:** When corpus reaches 100 standards or discovery issues reported

