# Universal Standards Creation Process (Praxis OS Developers Only)

**Standard for creating, structuring, and distributing universal standards in the Praxis OS framework.**

**Audience:** Praxis OS framework developers and contributors only. Consumers should NOT create universal standards.

---

## 🎯 TL;DR - Universal Standards Creation Quick Reference

**Keywords for search**: universal standards, creating universal standards, distribution standards, framework standards, how to create framework standards, standards for all projects, praxis os development

**Core Principle:** Universal standards ship to ALL consumer projects and define foundational "how to work" patterns that apply across ANY project using Praxis OS. Creating them requires higher quality bar and cross-project validation.

**Universal vs Project-Specific Decision Tree:**
- ✅ **Universal**: Pattern applies to ALL projects (test pyramid, RAG authoring, production code checklist)
- ❌ **Not Universal**: Pattern specific to one project's domain/tech/conventions → Project-specific standard instead

**Universal Standard Workflow:**
1. **Develop in `.praxis-os/standards/universal/[category]/`** (dogfooding)
2. **Test in praxis OS project** (validate it works)
3. **Sync to `dist/universal/standards/[category]/`** (ships to consumers)
4. **Test in consumer project** (validate it generalizes)

**Quality Bar (Higher than Project-Specific):**
- [ ] Applies to ALL projects (not domain/tech-specific)
- [ ] Tested in minimum 2 different projects
- [ ] Language-agnostic (or has language-specific variants)
- [ ] Zero assumptions about consumer's domain
- [ ] Examples work across different contexts
- [ ] RAG-optimized for discoverability
- [ ] Reviewed by another framework developer

**Common Mistakes:**
- ❌ Creating universal standard for project-specific pattern
- ❌ Shipping untested standards to consumers
- ❌ Domain-specific examples (only work in one context)
- ❌ Skipping `dist/` sync (standard doesn't ship)

---

## ❓ Questions This Answers

1. "When should I create a universal standard vs project-specific standard?"
2. "Where do I create universal standards during development?"
3. "How do I ship universal standards to consumers?"
4. "What quality bar must universal standards meet?"
5. "How do I test universal standards across projects?"
6. "What's the difference between dogfooding and distribution?"
7. "When do I sync to dist/universal/?"
8. "How do I validate a standard is truly universal?"
9. "What categories exist for universal standards?"
10. "How do I deprecate a universal standard?"

---

## 🎯 Purpose

Define how Praxis OS framework developers create, test, and distribute universal standards that ship to ALL consumer projects. Universal standards have a higher quality bar and require cross-project validation before distribution.

**Key Distinction:** Universal vs Project-Specific
- **Universal**: Applies to ALL projects using Praxis OS (ships in `dist/`)
- **Project-Specific**: Specific to THIS project's conventions (`.praxis-os/standards/development/`)

---

## When Should I Create a Universal Standard?

Create a universal standard ONLY when the pattern applies to ALL projects using Praxis OS, regardless of domain, technology, or team.

**✅ Create universal standard when:**
- Pattern applies across ANY project (test pyramid, production code checklist)
- Methodology is domain-agnostic (RAG content authoring, Git safety)
- Behavior should be consistent everywhere (AI assistant patterns, validation gates)
- Framework-level concern (workflow construction, MCP tool design)

**❌ Do NOT create universal standard when:**
- Pattern specific to one domain (HoneyHive docs standards → project-specific)
- Technology-specific pattern (Django middleware → project-specific)
- Company-specific convention (internal API design → project-specific)
- Project's unique architecture (microservices pattern → project-specific)

**Examples of universal standards:**
- `universal/standards/testing/test-pyramid.md` - Testing strategy (applies everywhere)
- `universal/standards/ai-assistant/rag-content-authoring.md` - RAG optimization (applies everywhere)
- `universal/standards/ai-safety/production-code-checklist.md` - Code quality (applies everywhere)

**Examples of project-specific standards:**
- `.praxis-os/standards/development/ouroboros-architecture.md` - Praxis OS's MCP server (specific to this project)
- `.praxis-os/standards/development/python-testing.md` - Python test patterns (specific to Python projects)

---

## How to Create a Universal Standard (Step-by-Step)

Complete workflow from identifying a universal pattern through distribution to consumers.

### Step 1: Validate It's Truly Universal

**Before creating, ask:**
- [ ] Does this apply to ALL projects using Praxis OS?
- [ ] Is it domain-agnostic (or has domain-agnostic variants)?
- [ ] Can it be explained without project-specific context?
- [ ] Would a consumer in a completely different domain benefit?

**If any answer is "no" → Create project-specific standard instead**

Query to check if it already exists:
```python
pos_search_project(content_type="standards", query="[your pattern topic]")
```

### Step 2: Identify Correct Category

**Universal standards location** (during development):
```
.praxis-os/standards/universal/[category]/[standard-name].md
```

**Standard Categories:**
- `ai-assistant/` - How AI agents should work (framework-level behavior)
- `ai-safety/` - Safety constraints and rules (applies everywhere)
- `architecture/` - Architectural patterns (general patterns)
- `concurrency/` - Concurrency standards (general patterns)
- `database/` - Database patterns (general patterns)
- `documentation/` - Documentation standards (applies everywhere)
- `failure-modes/` - Error handling patterns (general patterns)
- `installation/` - Installation/upgrade procedures (framework-level)
- `meta-workflow/` - Framework creation/maintenance (framework-level)
- `operations/` - Operational standards (framework-level)
- `performance/` - Performance optimization (general patterns)
- `security/` - Security patterns (general patterns)
- `testing/` - Testing standards (applies everywhere)
- `workflows/` - Workflow system standards (framework-level)

**Create new category** if none fit (but query first to see if it should merge with existing).

### Step 3: Draft the Standard (Use Template)

Follow the RAG-optimized template structure from the consumer-facing `standards-creation-process.md`:

```markdown
# [Standard Name]

**[One sentence describing what this standard defines]**

---

## 🎯 TL;DR - [Standard Name] Quick Reference

**Keywords for search**: [keywords]
**Core Principle:** [principle]
[...standard sections...]
```

**Critical for universal standards:**
- [ ] Examples work across different domains
- [ ] No project-specific assumptions
- [ ] Language-agnostic (or note language-specific variants)
- [ ] Justification explains WHY (not just WHAT)

### Step 4: Test in Praxis OS Project (Dogfooding)

**Create in `.praxis-os/standards/universal/[category]/[name].md`**

Use it immediately in the Praxis OS project:
- [ ] Does it solve the problem?
- [ ] Are examples clear?
- [ ] Is it discoverable through natural queries?
- [ ] File watcher auto-indexes within 30 seconds

```python
# Verify indexed
pos_search_project(content_type="standards", query="[your topic]")
```

### Step 5: RAG Optimize for Discoverability

Follow RAG optimization guidance from `standards-creation-process.md`:

```python
# Query for optimization patterns
pos_search_project(content_type="standards", query="how to make content discoverable for agents")
pos_search_project(content_type="standards", query="RAG content authoring keywords query hooks")
```

**Test from 5+ different angles:**
```python
pos_search_project(content_type="standards", query="how to [primary task]")
pos_search_project(content_type="standards", query="what is [main concept]")
pos_search_project(content_type="standards", query="[topic] best practices")
pos_search_project(content_type="standards", query="when should I [scenario]")
pos_search_project(content_type="standards", query="[topic] anti-patterns")
```

**Must return in top 3 results for ALL angles.**

### Step 6: Sync to Distribution

**When ready to ship to consumers**, sync from dev to distribution:

```bash
# Run the sync script
./scripts/sync-to-dist.sh --sync
```

This copies:
```
.praxis-os/standards/universal/[category]/[name].md
  ↓
dist/universal/standards/[category]/[name].md  ← Ships to consumers
```

**Critical:** Wait for explicit "ship it" signal before syncing.

### Step 7: Test in Consumer Project

**Install in a consumer project and validate:**
- [ ] Standard appears in consumer's `.praxis-os/standards/universal/`
- [ ] Queries return the standard correctly
- [ ] Examples work in different context
- [ ] No project-specific assumptions leak through

```python
# In consumer project
pos_search_project(content_type="standards", query="[your topic]")
```

### Step 8: Monitor and Iterate

**After shipping:**
- Monitor dogfooding feedback from consumers
- Update based on cross-project learnings
- Sync updates to `dist/` when ready

**Deprecation process:**
- Add deprecation notice to standard
- Keep for 3+ months (transition period)
- Archive to `deprecated/` directory
- Update `dist/` so deprecation ships

---

## What Makes a Good Universal Standard?

**Higher quality bar than project-specific standards.**

A good universal standard must:

- [ ] **Truly universal** - Applies to ALL projects (any domain/tech)
- [ ] **Tested in 2+ projects** - Validated it generalizes
- [ ] **Domain-agnostic examples** - Work across different contexts
- [ ] **Zero project assumptions** - No leaking of specific project patterns
- [ ] **Language-agnostic** - Or explicitly calls out language-specific variants
- [ ] **Clear justification** - Explains WHY, not just WHAT
- [ ] **RAG-optimized** - Discoverable from 5+ angles
- [ ] **Reviewed** - Another framework developer validated it
- [ ] **Versioned** - Breaking changes tracked

---

## What Are Universal Standard Anti-Patterns?

### Anti-Pattern 1: Project-Specific Pattern as Universal

**❌ Wrong:**
```markdown
# Universal API Design Standard

All APIs must use FastAPI with Pydantic models.
Database migrations use Alembic.
Authentication uses our internal JWT service.
```

**Why wrong:** Specific to Python/FastAPI projects, assumes tech stack, assumes "internal JWT service" exists.

**✅ Right:**
```markdown
# API Design Principles (Universal)

APIs should:
- Use type-safe request/response models (language-specific: Pydantic/Zod/Joi)
- Have versioning strategy (v1, v2, etc.)
- Document authentication requirements
- Return consistent error formats
```

---

### Anti-Pattern 2: Untested Generalization

**❌ Wrong:**
```markdown
# Testing Standard (Universal)

All tests must use pytest fixtures.
```

**Why wrong:** Only works for Python projects, not tested in other languages.

**✅ Right:**
```markdown
# Testing Standard (Universal)

All tests should use test fixtures/factories for setup.
Language-specific: pytest fixtures (Python), factory_bot (Ruby), FactoryGirl (JS)
```

---

### Anti-Pattern 3: Skipping Distribution Sync

**❌ Wrong:**
```markdown
# Create standard in .praxis-os/standards/universal/
# Never sync to dist/
# Consumers never receive it
```

**Why wrong:** Standard exists in praxis OS project but never ships to consumers.

**✅ Right:**
```markdown
# Create in .praxis-os/standards/universal/
# Test and validate
# Run ./scripts/sync-to-dist.sh --sync
# Consumers receive it in their .praxis-os/standards/universal/
```

---

## How to Deprecate a Universal Standard?

**Deprecation must ship to consumers.**

### Step 1: Add Deprecation Notice

**Edit in `.praxis-os/standards/universal/[category]/[name].md`:**

```markdown
## ⚠️ DEPRECATED (2025-11-24)

This standard is superseded by [new-standard.md].

**Migration path:**
1. Query new standard: `pos_search_project(content_type="standards", query="[new topic]")`
2. [Specific migration steps]

**Timeline:** This standard will be archived on 2026-02-24 (3 months).
```

### Step 2: Sync to Distribution

```bash
./scripts/sync-to-dist.sh --sync
```

### Step 3: Keep for Transition Period

**Keep for minimum 3 months:**
- Gives consumers time to discover deprecation
- Allows gradual migration
- Prevents breakage

### Step 4: Archive

**After 3 months, move to archive:**

```bash
# In .praxis-os/
mkdir -p standards/universal/deprecated/
mv standards/universal/[category]/[name].md standards/universal/deprecated/

# Sync to distribution
./scripts/sync-to-dist.sh --sync
```

---

## Distribution Workflow Reference

**The dogfooding → distribution flow:**

```
┌─────────────────────────────────────────┐
│  Phase 1: Development (Dogfooding)      │
│  ─────────────────────────────────────  │
│                                          │
│  .praxis-os/standards/universal/        │
│  └── [Create and test here]             │
│      ✅ Edit standard                    │
│      ✅ Test in praxis OS project        │
│      ✅ Iterate rapidly                  │
│      ✅ RAG optimize                     │
│                                          │
│  dist/universal/standards/              │
│  └── [STALE - Not updated yet]          │
│                                          │
└─────────────────────────────────────────┘
                   ↓
     🛑 Wait for "ship it" 🛑
                   ↓
┌─────────────────────────────────────────┐
│  Phase 2: Distribution                  │
│  ─────────────────────────────────────  │
│                                          │
│  ./scripts/sync-to-dist.sh --sync       │
│                                          │
│  .praxis-os/standards/universal/        │
│       ↓ ONE-WAY COPY                    │
│  dist/universal/standards/              │
│       ↓ SHIPS TO CONSUMERS              │
│  [Consumer] .praxis-os/standards/       │
│                                          │
└─────────────────────────────────────────┘
```

**Key points:**
- Edit in `.praxis-os/standards/universal/` (dogfooding)
- Sync to `dist/universal/standards/` (ships to consumers)
- Never edit `dist/` directly (read-only until sync)
- Flow is ALWAYS dev → distribution

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Deciding universal vs project** | `pos_search_project(content_type="standards", query="when to create universal standard")` |
| **Creating universal standard** | `pos_search_project(content_type="standards", query="how to create universal standard praxis os")` |
| **Distribution workflow** | `pos_search_project(content_type="standards", query="how to ship universal standards to consumers")` |
| **Quality criteria** | `pos_search_project(content_type="standards", query="universal standard quality bar")` |
| **Deprecation** | `pos_search_project(content_type="standards", query="deprecate universal standard")` |
| **Testing across projects** | `pos_search_project(content_type="standards", query="validate universal standard generalizes")` |

---

## 🔗 Related Standards

**Query workflow for universal standard creation:**

1. **Start with universal standard creation** → `pos_search_project(content_type="standards", query="how to create universal standard")` (this document)
2. **Learn RAG optimization** → `pos_search_project(content_type="standards", query="RAG content authoring")` → `standards/documentation/rag-content-authoring.md`
3. **Understand dev workflow** → `pos_search_project(content_type="standards", query="dev vs distribution workflow")` → `standards/development/dev-vs-distribution-workflow.md`
4. **Learn distribution process** → `pos_search_project(content_type="standards", query="dist directory distribution")` → `standards/development/dist-directory-rationale.md`

**By Category:**

**Development:**
- `standards/development/dev-vs-distribution-workflow.md` - Dev → dist workflow → `pos_search_project(content_type="standards", query="dev vs distribution")`
- `standards/development/dist-directory-rationale.md` - Why dist/ → `pos_search_project(content_type="standards", query="dist directory")`
- `standards/development/dogfooding-model.md` - Dogfooding patterns → `pos_search_project(content_type="standards", query="dogfooding")`

**Meta-Framework:**
- `standards/meta-workflow/command-language.md` - Command symbols → `pos_search_project(content_type="standards", query="command language")`
- `standards/meta-workflow/three-tier-architecture.md` - Content organization → `pos_search_project(content_type="standards", query="three tier architecture")`

---

**Remember**: Creating universal standards is a framework developer responsibility. Most users create project-specific standards instead. Only create universal standards when the pattern truly applies to ALL projects using Praxis OS.

---

**Version:** 1.0.0  
**Created:** 2025-11-24  
**Last Updated:** 2025-11-24  
**Audience:** Praxis OS framework developers only  
**Status:** 🟢 Active  
**Next Review:** After first 10 universal standards shipped

