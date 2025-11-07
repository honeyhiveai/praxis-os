# Documentation Project Naming Conventions

**Keywords for search**: prAxIs OS naming, project name consistency, praxis the ai os, BuilderMethods attribution, parent project acknowledgement, documentation terminology, project references

---

## Questions This Answers

- **What is the correct capitalization for "prAxIs OS"?**
- **How do I distinguish between this project and the parent prAxIs OS?**
- **When should I acknowledge the BuilderMethods parent project?**
- **What's the meaning behind the prAxIs OS capitalization?**
- **How do I reference prAxIs OS in documentation consistently?**
- **What's the official tagline for prAxIs OS?**
- **How do I credit the parent project in documentation?**
- **What are common naming mistakes to avoid?**
- **Where should parent project acknowledgement appear?**
- **What's the link to the parent prAxIs OS project?**

## 🎯 TL;DR - Project Naming Quick Reference

**Critical naming rules:**

1. **Use "prAxIs OS"** when referring to this system/project
2. **Tagline: "praxis, the ai os"** - explains the name and philosophy
3. **Use "prAxIs OS" or "BuilderMethods prAxIs OS"** when referencing the parent project
4. **Acknowledge parent project** using homepage pattern: "Built on BuilderMethods prAxIs OS"
5. **Capitalization matters**: pr**A**x**I**s **OS** (shows embedded A-I-OS)

**Keywords for search**: prAxIs OS full name, praxis the ai os tagline, project naming consistency, BuilderMethods attribution, parent project acknowledgement, documentation references

**When to apply**: Writing documentation, creating standards, user-facing content, code comments referencing the system

---

## Naming Convention Purpose

Maintain clear distinction between this project (prAxIs OS) and its parent (BuilderMethods prAxIs OS) while properly acknowledging the foundation we built upon. The name "prAxIs OS" embeds both the philosophy (praxis) and what it is (AI OS) in one elegant package. Consistent naming prevents confusion and gives proper credit.

---

## The Problem

**Without naming conventions:**
- Users confuse prAxIs OS with the parent prAxIs OS project
- Documentation inconsistently refers to the project
- Parent project contributions are not properly acknowledged
- Search and discovery become ambiguous
- The clever embedded meaning (A-I-OS) gets lost with wrong capitalization

**Real-world impact:**
- "prAxIs OS" alone is ambiguous - which one?
- Wrong capitalization ("prAxIs OS", "PraxisOS") loses the embedded A-I-OS
- No acknowledgement appears disrespectful to parent project
- Inconsistent names hurt brand recognition

---

## The Standard

### Use "prAxIs OS" for This Project

**Always use correct capitalization when referring to this system:**

✅ **Correct:**
- "prAxIs OS provides RAG-powered semantic search"
- "In prAxIs OS, workflows are phase-gated"
- "The prAxIs OS MCP server handles..."
- "Welcome to prAxIs OS documentation"
- "prAxIs OS: praxis, the ai os"

❌ **Incorrect:**
- "prAxIs OS provides..." ← Wrong capitalization, loses embedded A-I-OS
- "PraxisOS workflows..." ← Missing spaces, wrong caps
- "prAxIs OS..." ← Old name
- "praxis os" ← Missing capitalization of A-I-OS

### Use "prAxIs OS" or "BuilderMethods prAxIs OS" for Parent

**When referencing the parent project:**

✅ **Correct:**
- "Built on BuilderMethods prAxIs OS"
- "prAxIs OS by Brian Casel provided the 3-layer structure"
- "We extend the prAxIs OS philosophy with infrastructure"
- Link to: `https://buildermethods.com/agent-os`

❌ **Incorrect:**
- "Built on prAxIs OS" ← Wrong direction
- No acknowledgement at all ← Disrespectful

### Acknowledgement Pattern (from Homepage)

**Standard acknowledgement format:**

```markdown
🙏 **Built on the shoulders of giants:** [BuilderMethods prAxIs OS](https://buildermethods.com/agent-os) 
provided the 3-layer structure and philosophical foundation. We built the infrastructure to scale it.
```

**Key elements:**
- Respect and gratitude (🙏 emoji optional)
- Link to parent project
- Clarify what they provided vs what we added
- Shows evolution, not replacement

### The Tagline

**Use the tagline to explain the name:**

```markdown
**prAxIs OS**  
*praxis, the ai os*

The operating system where theory meets practice.
```

**Key elements:**
- Shows the full meaning: "praxis, the ai os"
- Explains the capitalization (A-I-OS embedded)
- Connects to the philosophy

### Exceptions (Rare)

**OK to use shortened forms when:**
- Context is crystal clear (e.g., internal code comments with .praxis-os/ references)
- Speaking generically about "agent operating systems" as a concept
- Quoting external sources

**But always use "prAxIs OS" with correct capitalization in user-facing content.**

---

## Naming Verification Checklist

**Before publishing documentation:**

- [ ] All references to this project use "prAxIs OS" with correct capitalization
- [ ] Tagline "praxis, the ai os" included where appropriate
- [ ] Parent project acknowledged with link
- [ ] No ambiguous "prAxIs OS" references (unless clearly referring to parent)
- [ ] Code comments use "prAxIs OS" or clear context
- [ ] User-facing content consistently uses "prAxIs OS"
- [ ] Attribution respects parent project contributions
- [ ] README/docs homepage includes acknowledgement

---

## Naming Convention Examples

### Documentation Headers

✅ **Good:**
```markdown
# prAxIs OS Architecture
# Getting Started with prAxIs OS
# How prAxIs OS Implements Knowledge Compounding
# prAxIs OS: praxis, the ai os
```

❌ **Bad:**
```markdown
# prAxIs OS Architecture  ← Wrong capitalization
# Getting Started with PraxisOS  ← Missing spaces, wrong caps
# prAxIs OS Architecture  ← Old name
```

### Code Comments

✅ **Good:**
```python
# prAxIs OS MCP server initialization
# Following prAxIs OS standards for...
# Query prAxIs OS RAG engine for...
```

✅ **Also OK (with clear context):**
```python
# Initialize MCP server (prAxIs OS)
# Load .praxis-os/ structure  ← Context clear from directory
```

❌ **Bad:**
```python
# prAxIs OS server initialization  ← Wrong capitalization
# prAxIs OS standards  ← Old name
# Following prAxIs OS standards  ← Ambiguous (which one?)
```

### Acknowledgements

✅ **Good:**
```markdown
This project builds on [BuilderMethods prAxIs OS](https://buildermethods.com/agent-os),
extending its 3-layer documentation structure with MCP, RAG, and workflow infrastructure.

Built with inspiration from prAxIs OS by Brian Casel, prAxIs OS adds...
```

❌ **Bad:**
```markdown
Based on prAxIs OS (no link, no clarity)
Inspired by some project (no attribution)
[No acknowledgement at all]
```

### User-Facing Content

✅ **Good:**
```markdown
**What is prAxIs OS?**

prAxIs OS (*praxis, the ai os*) is an AI development platform that extends the prAxIs OS 
philosophy with production infrastructure: MCP servers, RAG semantic search, and phase-gated workflows.

**How does prAxIs OS differ from prAxIs OS?**

BuilderMethods prAxIs OS provides the 3-layer structure (standards/specs/product) and 
philosophical foundation. prAxIs OS adds the infrastructure to scale it:
- MCP server for tool integration
- RAG engine for 90% context reduction
- Workflow engine with phase gating
- Persistent session state

The name "prAxIs OS" embeds both the philosophy (praxis) and what it is (AI OS).
```

---

## Anti-Patterns

### ❌ Wrong Capitalization

```markdown
# Getting Started with prAxIs OS

Welcome to PraxisOS! This guide covers praxis os installation...
```

**Problem:** Wrong capitalization loses the embedded A-I-OS meaning.

**Fix:** Use "prAxIs OS" with correct capitalization consistently.

### ❌ Using Old Name

```markdown
# prAxIs OS Documentation

A complete AI development platform with MCP, RAG, and workflows.
```

**Problem:** Using the old "prAxIs OS" name after rebrand.

**Fix:** Update to "prAxIs OS" everywhere.

### ❌ No Parent Acknowledgement

```markdown
# prAxIs OS Documentation

A complete AI development platform with MCP, RAG, and workflows.
```

**Problem:** No credit to parent project, appears to claim original invention.

**Fix:** Add acknowledgement section linking to BuilderMethods prAxIs OS.

### ❌ Ambiguous References

```markdown
prAxIs OS uses RAG to reduce context. The prAxIs OS MCP server provides...
```

**Problem:** Which project? The parent doesn't have RAG or MCP server.

**Fix:** Use "prAxIs OS" consistently for this project, "BuilderMethods prAxIs OS" for parent.

---

## Frequently Asked Questions

**Why the weird capitalization?**
→ pr**A**x**I**s **OS** embeds "AI OS" in the name. It shows both the philosophy (praxis) and what it is (AI Operating System).

**Can I use "prAxIs OS" or "praxis os"?**
→ No - the capitalization is part of the brand. Always use "prAxIs OS".

**What's the tagline?**
→ "praxis, the ai os" - it explains the name and connects to the philosophy.

**Can I ever use "prAxIs OS" to refer to this project?**
→ No - that's the parent project. Always use "prAxIs OS" for this project.

**What about in conversation or Slack?**
→ Use "prAxIs OS" - it's only 10 characters and the capitalization matters for brand recognition.

**Should every single mention use the full name?**
→ First mention should always be "prAxIs OS". Subsequent mentions in same section can use "the system" or "prAxIs OS" for variety.

**How do I refer to the parent project?**
→ "BuilderMethods prAxIs OS", "prAxIs OS by Brian Casel", or link to buildermethods.com/agent-os

**What if I'm writing about agent OS concepts generally?**
→ Then "agent operating systems" or "agent OS paradigm" (lowercase) works. Our name is specifically: "prAxIs OS"

---

## Related Standards

- `rag-content-authoring.md` - Ensure naming consistency aids RAG discovery
- `documentation-diagrams.md` - Use full name in diagram labels
- `standards-creation-process.md` - Apply naming rules to new standards

---

## Maintenance

**Update this standard when:**
- Brand identity evolves
- Parent project changes name or URL
- New attribution requirements emerge
- Community feedback highlights confusion about capitalization

**Last reviewed:** 2025-10-27 (Updated for prAxIs OS rebrand)

---

