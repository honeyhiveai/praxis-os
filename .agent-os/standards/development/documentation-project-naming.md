# Documentation Project Naming Conventions

**Keywords for search**: Agent OS Enhanced naming, project name consistency, Agent OS vs Agent OS Enhanced, BuilderMethods attribution, parent project acknowledgement, documentation terminology, project references

---

## 🎯 TL;DR - Project Naming Quick Reference

**Critical naming rules:**

1. **Use "Agent OS Enhanced"** when referring to this system/project
2. **Use "Agent OS" or "BuilderMethods Agent OS"** when referencing the parent project
3. **Acknowledge parent project** using homepage pattern: "Built on BuilderMethods Agent OS"
4. **Never use "Agent OS" alone** for this project - always include "Enhanced"

**Keywords for search**: Agent OS Enhanced full name, project naming consistency, BuilderMethods attribution, parent project acknowledgement, documentation references

**When to apply**: Writing documentation, creating standards, user-facing content, code comments referencing the system

---

## Purpose

Maintain clear distinction between this project (Agent OS Enhanced) and its parent (BuilderMethods Agent OS) while properly acknowledging the foundation we built upon. Consistent naming prevents confusion and gives proper credit.

---

## The Problem

**Without naming conventions:**
- Users confuse Agent OS Enhanced with the parent Agent OS project
- Documentation inconsistently refers to the project
- Parent project contributions are not properly acknowledged
- Search and discovery become ambiguous
- Professional credibility suffers from unclear attribution

**Real-world impact:**
- "Agent OS" alone is ambiguous - which one?
- Missing "Enhanced" loses our identity and differentiators
- No acknowledgement appears disrespectful to parent project
- Inconsistent names hurt brand recognition

---

## The Standard

### Use "Agent OS Enhanced" for This Project

**Always use full name when referring to this system:**

✅ **Correct:**
- "Agent OS Enhanced provides RAG-powered semantic search"
- "In Agent OS Enhanced, workflows are phase-gated"
- "The Agent OS Enhanced MCP server handles..."
- "Welcome to Agent OS Enhanced documentation"

❌ **Incorrect:**
- "Agent OS provides RAG-powered semantic search" ← Missing "Enhanced"
- "In Agent OS, workflows are phase-gated" ← Ambiguous
- "The Agent OS MCP server..." ← Wrong project

### Use "Agent OS" or "BuilderMethods Agent OS" for Parent

**When referencing the parent project:**

✅ **Correct:**
- "Built on BuilderMethods Agent OS"
- "Agent OS by Brian Casel provided the 3-layer structure"
- "We extend the Agent OS philosophy with infrastructure"
- Link to: `https://buildermethods.com/agent-os`

❌ **Incorrect:**
- "Built on Agent OS Enhanced" ← Wrong direction
- No acknowledgement at all ← Disrespectful

### Acknowledgement Pattern (from Homepage)

**Standard acknowledgement format:**

```markdown
🙏 **Built on the shoulders of giants:** [BuilderMethods Agent OS](https://buildermethods.com/agent-os) 
provided the 3-layer structure and philosophical foundation. We built the infrastructure to scale it.
```

**Key elements:**
- Respect and gratitude (🙏 emoji optional)
- Link to parent project
- Clarify what they provided vs what we added
- Shows evolution, not replacement

### Exceptions (Rare)

**OK to use "Agent OS" alone when:**
- Context is crystal clear (e.g., internal code comments)
- Speaking generically about "agent operating systems" as a concept
- Quoting external sources that use shortened form

**But default to full name everywhere else.**

---

## Checklist

**Before publishing documentation:**

- [ ] All references to this project use "Agent OS Enhanced"
- [ ] Parent project acknowledged with link
- [ ] No ambiguous "Agent OS" references
- [ ] Code comments use full name or clear context
- [ ] User-facing content consistently uses "Agent OS Enhanced"
- [ ] Attribution respects parent project contributions
- [ ] README/docs homepage includes acknowledgement

---

## Examples

### Documentation Headers

✅ **Good:**
```markdown
# Agent OS Enhanced Architecture
# Getting Started with Agent OS Enhanced
# How Agent OS Enhanced Implements Knowledge Compounding
```

❌ **Bad:**
```markdown
# Agent OS Architecture  ← Missing "Enhanced"
# Getting Started with AOS  ← Unclear abbreviation
```

### Code Comments

✅ **Good:**
```python
# Agent OS Enhanced MCP server initialization
# Following Agent OS Enhanced standards for...
# Query Agent OS Enhanced RAG engine for...
```

✅ **Also OK (with clear context):**
```python
# Initialize MCP server (Agent OS Enhanced)
# Load .agent-os/ structure  ← Context implies "Enhanced"
```

❌ **Bad:**
```python
# Agent OS server initialization  ← Which one?
# Following Agent OS standards  ← Ambiguous
```

### Acknowledgements

✅ **Good:**
```markdown
This project builds on [BuilderMethods Agent OS](https://buildermethods.com/agent-os),
extending its 3-layer documentation structure with MCP, RAG, and workflow infrastructure.

Built with inspiration from Agent OS by Brian Casel, Agent OS Enhanced adds...
```

❌ **Bad:**
```markdown
Based on Agent OS (no link, no clarity)
Inspired by some project (no attribution)
[No acknowledgement at all]
```

### User-Facing Content

✅ **Good:**
```markdown
**What is Agent OS Enhanced?**

Agent OS Enhanced is an AI development platform that extends the Agent OS philosophy
with production infrastructure: MCP servers, RAG semantic search, and phase-gated workflows.

**How does Agent OS Enhanced differ from Agent OS?**

BuilderMethods Agent OS provides the 3-layer structure (standards/specs/product) and 
philosophical foundation. Agent OS Enhanced adds the infrastructure to scale it:
- MCP server for tool integration
- RAG engine for 90% context reduction
- Workflow engine with phase gating
- Persistent session state
```

---

## Anti-Patterns

### ❌ Inconsistent Naming

```markdown
# Getting Started

Welcome to Agent OS! This guide covers Agent OS Enhanced installation...
```

**Problem:** Switches between names, confusing readers.

**Fix:** Pick "Agent OS Enhanced" and stick with it.

### ❌ No Parent Acknowledgement

```markdown
# Agent OS Enhanced Documentation

A complete AI development platform with MCP, RAG, and workflows.
```

**Problem:** No credit to parent project, appears to claim original invention.

**Fix:** Add acknowledgement section linking to BuilderMethods Agent OS.

### ❌ Ambiguous References

```markdown
Agent OS uses RAG to reduce context. The Agent OS MCP server provides...
```

**Problem:** Which project? The parent doesn't have RAG or MCP server.

**Fix:** Use "Agent OS Enhanced" consistently.

### ❌ Over-Abbreviation

```markdown
AOS provides workflows. The AOS system handles...
```

**Problem:** "AOS" is unclear, creates another ambiguity.

**Fix:** Write out "Agent OS Enhanced" - clarity over brevity.

---

## Frequently Asked Questions

**Can I ever use "Agent OS" to refer to this project?**
→ Only when context is crystal clear (e.g., internal comments with .agent-os/ references). Default to full name.

**What about in conversation or Slack?**
→ Full name preferred, but "Agent OS Enhanced" or "AOS Enhanced" both OK if team understands context.

**Should every single mention use the full name?**
→ First mention should always be full. Subsequent mentions in same section can use "the system" or "Agent OS Enhanced" for variety.

**How do I refer to the parent project?**
→ "BuilderMethods Agent OS", "Agent OS by Brian Casel", or link to buildermethods.com/agent-os

**What if I'm writing about agent OS concepts generally?**
→ Then "agent operating systems" or "agent OS paradigm" (lowercase) works. Our name is capitalized: "Agent OS Enhanced"

---

## Related Standards

- `rag-content-authoring.md` - Ensure naming consistency aids RAG discovery
- `documentation-diagrams.md` - Use full name in diagram labels
- `standards-creation-process.md` - Apply naming rules to new standards

---

## Maintenance

**Update this standard when:**
- Brand identity evolves (unlikely but possible)
- Parent project changes name or URL
- New attribution requirements emerge
- Community feedback highlights confusion

**Last reviewed:** 2025-10-13

---

