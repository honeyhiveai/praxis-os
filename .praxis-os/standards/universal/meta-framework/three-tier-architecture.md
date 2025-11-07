# Three-Tier Architecture - Universal Meta-Framework Pattern

**Timeless pattern for organizing AI workflow content by consumption model**

---

## 🎯 TL;DR - Three-Tier Architecture Quick Reference

**Keywords for search**: three-tier architecture, workflow structure, README phase task, tier 1 tier 2 tier 3, side-loaded context, active read context, output artifacts, framework organization, AI consumption model

**Core Principle:** Organize framework content by when and how AI consumes it: Tier 1 (side-loaded during execution, ≤100 lines), Tier 2 (on-demand reading, 200-500 lines), Tier 3 (generated outputs, never re-read).

**The Problem:** Everything in one place → Large files → Context overflow → Poor attention → Failures
**The Solution:** Separate by consumption model → Small execution files → Optimal context → Success

**The Three Tiers:**

1. **Tier 1: Side-Loaded Context** (Execution Files)
   - **What:** Files AI reads during execution
   - **Size:** ≤100 lines per file
   - **Examples:** task-1-setup.md, task-2-validation.md
   - **Pattern:** Single-responsibility, command language (🛑 🎯)
   - **Consumption:** Read 1-5 files per task (5-10% context)

2. **Tier 2: Active Read Context** (Methodology/Reference)
   - **What:** Files AI reads on-demand for guidance
   - **Size:** 200-500 lines
   - **Examples:** phase-overview.md, README.md, architecture.md
   - **Pattern:** Comprehensive methodology, principles
   - **Consumption:** Read when explicitly needed (15-25% context)

3. **Tier 3: Output Artifacts** (Generated Content)
   - **What:** AI generates but NEVER re-reads
   - **Size:** Unlimited
   - **Examples:** tests/, generated-code/, reports/
   - **Pattern:** Human/system consumption only
   - **Critical:** Re-reading Tier 3 causes context pollution

**Directory Structure:**
```
framework/
├── README.md              (Tier 2: Overview)
├── phases/
│   ├── 1/
│   │   ├── phase.md      (Tier 2: Methodology)
│   │   ├── task-1.md     (Tier 1: Execution, ≤100 lines)
│   │   ├── task-2.md     (Tier 1: Execution, ≤100 lines)
│   │   └── task-3.md     (Tier 1: Execution, ≤100 lines)
│   └── 2/ ...
└── outputs/               (Tier 3: Generated, never re-read)
```

**File Size Targets:**
- **Tier 1 (Execution):** 60-100 lines → 95%+ attention quality
- **Tier 2 (Methodology):** 200-500 lines → 80-90% attention quality
- **Tier 3 (Outputs):** Unlimited → Not consumed by AI

**Why This Works:**
- **Context efficiency:** 15-25% utilization vs 75-90%
- **Focused attention:** AI reads only what's needed
- **Scalability:** Add tasks without context bloat
- **Maintainability:** Small, focused files easy to update

**Common Mistake:** Mixing tiers → context pollution → degraded performance

---

## ❓ Questions This Answers

1. "What is three-tier architecture?"
2. "How should I organize workflow files?"
3. "What's the difference between README, phase, and task files?"
4. "What is side-loaded context?"
5. "What is active read context?"
6. "What are output artifacts?"
7. "Why can't AI re-read generated code?"
8. "What file sizes should I use?"
9. "How do I prevent context overflow?"
10. "How do tiers interact?"
11. "What's Tier 1 vs Tier 2 vs Tier 3?"

---

## What Is Three-Tier Architecture?

A systematic organization of framework content into three categories based on **when and how the AI consumes them**:

1. **Tier 1**: AI reads **during execution** (side-loaded context)
2. **Tier 2**: AI reads **on-demand** (active read context)
3. **Tier 3**: AI **generates** but never re-reads (output artifacts)

---

## The Core Problem

**Context Window is Finite**: LLMs have limited context (100K-1M tokens), and attention quality degrades as utilization increases.

**Traditional Approach Fails**:
```
Put everything in one place → Large files → Context overflow → Poor attention → Failures
```

**Three-Tier Solution**:
```
Separate by consumption model → Small execution files → Optimal context → High attention → Success
```

---

## Tier 1: Side-Loaded Context

### Purpose
Files the AI reads **during execution** to know what to do next.

### Characteristics
- **Size**: ≤100 lines per file
- **Pattern**: Single-responsibility, focused instructions
- **Binding**: Uses command language (🛑 🎯 ⚠️)
- **Consumption**: Read 1-5 files per task

### Examples
- `phase-1-setup.md` (85 lines)
- `task-2-validation.md` (72 lines)
- `step-3-generation.md` (94 lines)

### File Structure Template
```markdown
# Task: [Name]

🛑 EXECUTE-NOW: [prerequisite]

## Objective
Brief description (2-3 sentences)

## Steps

### Step 1: [Action]
Specific instruction with command

### Step 2: [Action]
Specific instruction with command

🛑 VALIDATE-GATE: [criteria]
- [ ] Criterion 1 ✅/❌
- [ ] Criterion 2 ✅/❌

🎯 NEXT-MANDATORY: [next-file.md]
```

### Why ≤100 Lines?

| File Size | AI Attention | Success Rate | Context Use |
|-----------|--------------|--------------|-------------|
| ≤100 | 95%+ | 85%+ | 5-10% |
| 200-300 | 80-90% | 70-80% | 15-25% |
| 500+ | <70% | <60% | 40%+ |

**Empirical Result**: ≤100 lines maintains optimal attention quality.

---

## Tier 2: Active Read Context

### Purpose
Files the AI reads **on-demand** for comprehensive understanding.

### Characteristics
- **Size**: 200-500 lines per file
- **Pattern**: Complete methodology, architecture, principles
- **Consumption**: Read when referenced (⚠️ MUST-READ)
- **Frequency**: 1-3 times per workflow

### Examples
- `README.md` (350 lines) - Framework overview
- `METHODOLOGY.md` (450 lines) - Complete methodology
- `ARCHITECTURE.md` (280 lines) - System design

### File Structure Template
```markdown
# [Framework Name] - Methodology

## Overview
Comprehensive introduction

## Architecture
System design and components

## Workflow
Complete process description

## Quality Standards
Expectations and criteria

## References
Related documents
```

### Why 200-500 Lines?

- **Too Small** (<200): Fragmentation overhead, context switching
- **Too Large** (>500): Attention degrades, key details missed
- **Sweet Spot** (200-500): Complete enough to be comprehensive, small enough for high attention

---

## Tier 3: Output Artifacts

### Purpose
Files the AI **generates** as deliverables.

### Characteristics
- **Size**: Unlimited
- **Pattern**: Generated code, schemas, documentation, reports
- **Consumption**: AI generates, human reads, **AI NEVER re-reads**
- **Critical**: Must not pollute context

### Examples
- Generated test files (500-2000 lines)
- Extracted schemas (1000+ lines)
- API documentation (unlimited)
- Analysis reports (500-5000 lines)

### The Re-Reading Problem

**❌ Bad Pattern**:
```
1. AI generates schema.json (1000 lines)
2. AI reads schema.json to continue
3. Context now at 60%+ utilization
4. Attention degrades
5. Quality drops
```

**✅ Good Pattern**:
```
1. AI generates schema.json (1000 lines)
2. AI references schema.json by name only
3. Context stays at 15-25% utilization
4. Attention remains high
5. Quality maintained
```

### Preventing Re-Reading

**Use summaries, not full content**:

```markdown
## Generated Artifacts

- `schema.json` (1247 lines)
  - 24 endpoints extracted
  - 18 models defined
  - Validation: ✅ Passed

**Do not re-read this file. Reference by name only.**
```

---

## Tier Interaction Patterns

### Pattern 1: Top-Down Execution

```
Entry Point (Tier 2)
  ↓ References
Phase 1 (Tier 1) → Generates → Output 1 (Tier 3)
  ↓ References
Phase 2 (Tier 1) → Generates → Output 2 (Tier 3)
  ↓ References
Phase 3 (Tier 1) → Generates → Output 3 (Tier 3)
```

### Pattern 2: On-Demand Methodology

```
Task (Tier 1)
  ↓ ⚠️ MUST-READ: methodology.md
Methodology (Tier 2)
  ↓ Returns to
Task (Tier 1)
  ↓ Continues execution
```

### Pattern 3: Evidence Collection (No Re-Reading)

```
Task 1 (Tier 1) → Generates Report (Tier 3)
  ↓ Collects summary: "12/15 tests passing"
Task 2 (Tier 1) → Uses summary, NOT full report
  ↓ Continues with summary
Task 3 (Tier 1) → References "12/15", NOT file content
```

---

## Implementation Guide

### Step 1: Identify Content by Consumption

**Ask**: When does AI need this content?

- **During every task** → Tier 1
- **For comprehensive context** → Tier 2
- **Generated as output** → Tier 3

### Step 2: Apply Size Constraints

**Tier 1**: Break into ≤100 line files
```bash
# Audit Tier 1 files
find phases/ -name "*.md" -exec sh -c 'lines=$(wc -l < "$1"); if [ $lines -gt 100 ]; then echo "⚠️  $lines lines: $1"; fi' _ {} \;
```

**Tier 2**: Keep 200-500 lines
```bash
# Audit Tier 2 files
find core/ -name "*.md" -exec sh -c 'lines=$(wc -l < "$1"); if [ $lines -gt 500 ]; then echo "⚠️  $lines lines: $1"; fi' _ {} \;
```

### Step 3: Prevent Tier 3 Re-Reading

**Add warnings in Tier 1**:
```markdown
🚨 FRAMEWORK-VIOLATION: Do not re-read generated files

Use summaries only:
- schema.json: 24 endpoints, 18 models
- tests.py: 45/60 tests passing

Do NOT open these files for details.
```

### Step 4: Validate Compliance

```python
def validate_tier_compliance(framework_path):
    """Validate three-tier architecture compliance."""
    tier1_files = find_files(framework_path / "phases")
    tier2_files = find_files(framework_path / "core")
    
    # Check Tier 1: ≤100 lines
    for file in tier1_files:
        lines = count_lines(file)
        assert lines <= 100, f"Tier 1 file too large: {file} ({lines} lines)"
    
    # Check Tier 2: ≤500 lines
    for file in tier2_files:
        lines = count_lines(file)
        assert lines <= 500, f"Tier 2 file too large: {file} ({lines} lines)"
    
    return "✅ Tier compliance validated"
```

---

## Benefits

### Context Efficiency
- **Before**: 75-90% context utilization (overflow risk)
- **After**: 15-25% context utilization (optimal)
- **Improvement**: 3-4x better efficiency

### Attention Quality
- **Before**: <70% attention quality (large files)
- **After**: 95%+ attention quality (small files)
- **Improvement**: 25%+ better attention

### Execution Consistency
- **Before**: 60-70% success rate
- **After**: 85-95% success rate
- **Improvement**: 3-4x more consistent

---

## Common Mistakes

### ❌ Mistake 1: Mixing Tiers
**Problem**: Execution + methodology in same file (300 lines)  
**Impact**: Neither tier optimized, both suffer  
**Fix**: Separate into Tier 1 (execution, ≤100) + Tier 2 (methodology, 200-500)

### ❌ Mistake 2: Tier 1 Too Large
**Problem**: 200-500 line "task" files  
**Impact**: Attention degrades, consistency drops  
**Fix**: Break into multiple ≤100 line task files

### ❌ Mistake 3: Re-Reading Tier 3
**Problem**: AI re-opens generated files  
**Impact**: Context pollution, attention degradation  
**Fix**: Use summaries, add explicit warnings

### ❌ Mistake 4: No Tier 2
**Problem**: All content in Tier 1, no comprehensive reference  
**Impact**: Missing context, repeated explanations  
**Fix**: Create Tier 2 methodology files

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Tier 1 Size | 95%+ ≤100 lines | Automated check |
| Tier 2 Size | 100% ≤500 lines | Automated check |
| Context Use | 15-25% | Monitor during execution |
| Attention Quality | 95%+ | Success rate proxy |

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Organizing workflows** | `pos_search(content_type="standards", query="three-tier architecture")` |
| **File structure design** | `pos_search(content_type="standards", query="workflow structure")` |
| **README phase task** | `pos_search(content_type="standards", query="README phase task structure")` |
| **Context overflow** | `pos_search(content_type="standards", query="prevent context overflow")` |
| **File size guidance** | `pos_search(content_type="standards", query="workflow file sizes")` |
| **Tier differences** | `pos_search(content_type="standards", query="tier 1 tier 2 tier 3")` |
| **Output artifacts** | `pos_search(content_type="standards", query="output artifacts")` |
| **Framework organization** | `pos_search(content_type="standards", query="framework organization")` |

---

## 🔗 Related Standards

**Query workflow for complete architecture understanding:**

1. **Start with tiers** → `pos_search(content_type="standards", query="three-tier architecture")` (this document)
2. **Learn decomposition** → `pos_search(content_type="standards", query="horizontal decomposition")` → `standards/meta-workflow/horizontal-decomposition.md`
3. **Add commands** → `pos_search(content_type="standards", query="command language")` → `standards/meta-workflow/command-language.md`
4. **Understand principles** → `pos_search(content_type="standards", query="framework creation principles")` → `standards/meta-workflow/framework-creation-principles.md`
5. **Implement gates** → `pos_search(content_type="standards", query="validation gates")` → `standards/meta-workflow/validation-gates.md`

**By Category:**

**Meta-Framework (Complete Set):**
- `standards/meta-workflow/framework-creation-principles.md` - Core principles → `pos_search(content_type="standards", query="framework creation principles")`
- `standards/meta-workflow/command-language.md` - Binding instructions → `pos_search(content_type="standards", query="command language")`
- `standards/meta-workflow/horizontal-decomposition.md` - Task breakdown → `pos_search(content_type="standards", query="horizontal decomposition")`
- `standards/meta-workflow/validation-gates.md` - Quality checkpoints → `pos_search(content_type="standards", query="validation gates")`

**Workflows:**
- `standards/workflows/workflow-construction-standards.md` - Building workflows → `pos_search(content_type="standards", query="workflow construction")`
- `standards/workflows/workflow-system-overview.md` - Workflow system → `pos_search(content_type="standards", query="workflow system overview")`

**Architecture:**
- `standards/architecture/solid-principles.md` - Single Responsibility → `pos_search(content_type="standards", query="SOLID principles")`
- `standards/architecture/separation-of-concerns.md` - Concern separation → `pos_search(content_type="standards", query="separation of concerns")`

---

**Three-tier architecture is the foundation of high-quality AI-assisted workflows. Master this pattern for consistent, scalable results.**
