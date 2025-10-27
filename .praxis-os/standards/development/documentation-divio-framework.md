# Documentation Divio Framework Standards

**Keywords for search**: Divio documentation framework, documentation quadrants, tutorial how-to reference explanation, documentation categorization, user-oriented documentation, doc type frontmatter, learning-oriented task-oriented

---

## 🎯 TL;DR - Divio Documentation Quick Reference

**Critical Divio principles:**

1. **Four documentation types** - Tutorial, How-To, Reference, Explanation
2. **Categorize by user intent** - Learning, problem-solving, lookup, understanding
3. **No mixed-type content** - Each doc serves one purpose
4. **Add `doc_type` frontmatter** - Every doc must declare its type
5. **Organize by quadrants** - Sidebar grouped by type

**Keywords for search**: Divio framework quadrants, documentation types tutorial how-to reference explanation, user intent categorization, doc type frontmatter, mixed content splitting

**When to apply**: Creating new documentation, organizing existing docs, auditing doc structure

**Four types:**
- **Tutorial** - Learning-oriented, teaches through doing (safe to fail)
- **How-To Guide** - Task-oriented, solves specific problems (assumes knowledge)
- **Reference** - Information-oriented, technical lookup (dry, comprehensive)
- **Explanation** - Understanding-oriented, explains concepts (why and how)

---

## Purpose

Ensure all Agent OS Enhanced documentation follows the Divio Documentation Framework, organizing content by user intent (learning, problem-solving, lookup, understanding) rather than by topic or feature. This makes documentation discoverable and useful based on what users want to accomplish.

---

## The Problem

**Without Divio structure:**
- Users can't find what they need (mixed purposes in one place)
- Tutorials polluted with reference details
- Reference docs trying to teach (inappropriate for lookup)
- New users overwhelmed by wrong content type
- Documentation grows into unmaintainable mess
- Duplicate content across multiple docs

**Real-world confusion:**
- User wants to learn: lands on API reference → frustrated
- User wants quick lookup: lands on lengthy tutorial → annoyed
- User wants troubleshooting: lands on architecture explanation → confused
- Documentation scales poorly (everything mixed together)

---

## The Standard

### Four Documentation Types (Divio Quadrants)

All documentation must fit into one of four types:

#### 1. Tutorial (Learning-Oriented)

**Purpose:** Teach beginners through a complete, guided learning experience.

**Characteristics:**
- Learning goals explicit
- Safe to fail (no production consequences)
- Step-by-step with success indicators
- Beginner-friendly (explains everything)
- Complete A-to-Z experience
- Builds confidence through accomplishment

**Example titles:**
- "Your First Agent OS Enhanced Project"
- "Build a Complete Feature Spec"
- "Getting Started with Workflows"

**Required sections:**
- Learning Goals
- Prerequisites
- Time Estimate
- What You'll Build
- Step-by-step instructions
- What You Learned
- Next Steps

**User intent:** "I want to learn by doing"

#### 2. How-To Guide (Task-Oriented)

**Purpose:** Solve specific problems with concrete steps.

**Characteristics:**
- Goal-oriented ("How to...")
- Assumes existing knowledge
- Problem-solving focused
- Specific, not comprehensive
- Practical, actionable steps
- Includes troubleshooting

**Example titles:**
- "How to Deploy to Production"
- "Creating Project Standards"
- "Debug Workflow Failures"

**Required sections:**
- Goal
- Prerequisites
- When to Use This
- Numbered Steps
- Validation Checklist
- Troubleshooting

**User intent:** "I have a problem to solve"

#### 3. Reference (Information-Oriented)

**Purpose:** Provide technical details for lookup.

**Characteristics:**
- Dry, factual (no teaching)
- Lookup tables, API docs
- Minimal prose
- Comprehensive coverage
- Accurate and up-to-date
- Structured for scanning

**Example titles:**
- "MCP Tools Reference"
- "Workflow API Reference"
- "Configuration Options"

**Required sections:**
- Brief overview (1-2 sentences)
- Tables/Lists of items
- Technical specifications
- Minimal explanatory prose

**User intent:** "I need to look something up"

#### 4. Explanation (Understanding-Oriented)

**Purpose:** Explain concepts, background, and why things work.

**Characteristics:**
- Conceptual (not practical)
- Answers "why" and "how" (not "how to")
- Background and context
- Trade-offs and comparisons
- Deepens understanding
- Multiple perspectives

**Example titles:**
- "Understanding Knowledge Compounding"
- "Architecture Overview"
- "How RAG Works"

**Required sections:**
- Context/Background
- Core Concepts (multiple sections)
- How It Works (conceptual)
- Trade-offs/Comparisons
- Related Topics

**User intent:** "I want to understand why"

### Decision Tree for Categorization

**Use this to categorize any doc:**

```
Is this content...

1. Teaching a beginner through a complete learning experience?
   → YES: TUTORIAL
   Example: "Build Your First API" (learning-oriented)

2. Solving a specific problem with concrete steps?
   → YES: HOW-TO GUIDE
   Example: "How to Deploy to Production" (task-oriented)

3. Describing technical details, APIs, or specifications?
   → YES: REFERENCE
   Example: "API Endpoints Reference" (information-oriented)

4. Explaining concepts, background, or WHY things work?
   → YES: EXPLANATION
   Example: "Understanding Authentication Flow" (understanding-oriented)
```

### Add `doc_type` Frontmatter

**Every documentation file must declare its type:**

```markdown
---
sidebar_position: 1
doc_type: tutorial  # or: how-to, reference, explanation
---

# Document Title
```

**Valid `doc_type` values:**
- `tutorial`
- `how-to`
- `reference`
- `explanation`

**This enables:**
- Validation scripts to check compliance
- Badges showing doc type (visual clarity)
- Filtering and organization
- Quality assurance

### No Mixed-Type Content

**Each document serves ONE purpose only.**

❌ **Bad - Mixed content:**

```markdown
# Getting Started

## Installation (Tutorial)
[Step-by-step setup]

## API Reference (Reference)
[Table of all endpoints]

## Troubleshooting (How-To)
[Common problems]
```

✅ **Good - Split into 3 docs:**

1. `tutorials/your-first-project.md` - Installation tutorial
2. `reference/api-endpoints.md` - API reference table
3. `how-to-guides/troubleshoot-setup.md` - Troubleshooting guide

### Organize Sidebar by Quadrants

**Sidebar must group docs by type:**

```typescript
const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: 'category',
      label: '🎓 Tutorials',
      items: ['tutorials/intro', 'tutorials/first-project'],
    },
    {
      type: 'category',
      label: '📋 How-To Guides',
      items: ['how-to-guides/deploy', 'how-to-guides/configure'],
    },
    {
      type: 'category',
      label: '💡 Explanation',
      items: ['explanation/architecture', 'explanation/concepts'],
    },
    {
      type: 'category',
      label: '📚 Reference',
      items: ['reference/api', 'reference/config'],
    },
  ],
};
```

**Order:** Tutorials → How-To Guides → Explanation → Reference

**Rationale:** Most common user path: Learn → Solve Problems → Understand → Look Up

---

## Checklist

**Before creating new documentation:**

- [ ] Identified user intent (learning, problem-solving, lookup, understanding)
- [ ] Chosen correct Divio type (tutorial, how-to, reference, explanation)
- [ ] Confirmed content serves only one purpose (no mixing)
- [ ] Planned required sections for chosen type
- [ ] Decided on file location (`tutorials/`, `how-to-guides/`, `reference/`, `explanation/`)

**When writing documentation:**

- [ ] Added `doc_type` frontmatter
- [ ] Followed structural conventions for chosen type
- [ ] Avoided mixing purposes (no tutorial + reference in one doc)
- [ ] Used appropriate tone (learning, task, factual, conceptual)
- [ ] Included all required sections for type

**After writing documentation:**

- [ ] Verified `doc_type` matches content
- [ ] Checked sidebar placement (correct quadrant)
- [ ] Validated against type conventions
- [ ] No mixed-type red flags (lookup tables in tutorials, teaching in reference)

---

## Examples

### Example 1: Tutorial vs How-To

**Topic:** "Setting up authentication"

**Tutorial version:** `tutorials/your-first-authenticated-app.md`

```markdown
---
doc_type: tutorial
---

# Build Your First Authenticated App

## Learning Goals
By completing this tutorial, you will learn to:
1. Understand authentication basics
2. Set up OAuth 2.0 from scratch
3. Test authentication flow
4. Deploy a secure app

## Prerequisites
- Completed "Your First App" tutorial
- 30 minutes

## What You'll Build
A simple authenticated app that logs in users and displays their profile.

## Steps

### Step 1: Understand OAuth Flow
Before we build, let's understand how OAuth works...
[Teaching content]

### Step 2: Set Up OAuth Provider
Create an account on [Provider]...
[Detailed setup]

...
```

**How-To version:** `how-to-guides/add-authentication.md`

```markdown
---
doc_type: how-to
---

# Add Authentication to Existing App

## Goal
Add OAuth 2.0 authentication to an existing application.

## Prerequisites
- Existing app with user system
- OAuth provider account
- Basic understanding of OAuth (see "Understanding OAuth" explanation)

## When to Use This
Use when you need to add authentication to an already-built application.

## Steps

1. Install auth library:
   ```bash
   npm install oauth2-client
   ```

2. Configure OAuth provider:
   ```javascript
   // config/auth.js
   export const oauthConfig = { /* ... */ }
   ```

3. Add login endpoint...

## Validation
- [ ] Login redirects to OAuth provider
- [ ] Callback handles tokens correctly
- [ ] User profile displays after login

## Troubleshooting
**Issue:** Redirect URI mismatch
**Solution:** ...
```

**Key differences:**
- Tutorial: Teaches from zero, learning-focused
- How-To: Assumes knowledge, problem-focused

### Example 2: Reference vs Explanation

**Topic:** "MCP Tools"

**Reference version:** `reference/mcp-tools.md`

```markdown
---
doc_type: reference
---

# MCP Tools Reference

Complete reference of all MCP tools available in Agent OS Enhanced.

## search_standards

**Purpose:** Semantic search over Agent OS standards

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Natural language query |
| `n_results` | int | No | Number of results (default: 5) |
| `filter_phase` | int | No | Filter by phase number |

**Returns:**
| Field | Type | Description |
|-------|------|-------------|
| `results` | array | Matching standards chunks |
| `total_tokens` | int | Total tokens in results |

**Example:**
```python
search_standards("how to write tests")
```

## pos_browser

[Similar technical reference format]
```

**Explanation version:** `explanation/how-mcp-works.md`

```markdown
---
doc_type: explanation
---

# Understanding MCP Integration

## What is MCP?

Model Context Protocol (MCP) is a standardized interface that allows AI agents
to access external tools and data sources. Think of it as a universal adapter
between AI models and the tools they need.

## Why MCP?

Before MCP, every AI integration required custom code. MCP solves this by...

[Conceptual explanation]

## How MCP Works in Agent OS Enhanced

Agent OS Enhanced uses MCP to expose three core capabilities:

1. **RAG Search** - Semantic search over standards
2. **Workflow Execution** - Phase-gated task orchestration  
3. **Browser Control** - Automated testing and interaction

[Explains concepts, not technical details]

## Trade-offs

MCP provides standardization but introduces...

[Discussion of pros/cons]
```

**Key differences:**
- Reference: Dry, factual, lookup tables
- Explanation: Conceptual, why it works, context

### Example 3: Identifying Mixed Content

**Before (Mixed):** `configuration.md`

```markdown
# Configuration

## Overview
Configuration uses JSON files. JSON is a data format that... [Explanation]

## How to Configure
1. Create config.json
2. Add these fields... [How-To]

## Configuration Reference
| Field | Type | Description |
|-------|------|-------------|
| port | number | Server port | [Reference]
```

**This is THREE types mixed together!**

**After (Split):**

1. `explanation/configuration-concepts.md` - Explains JSON, config paradigm
2. `how-to-guides/configure-application.md` - Steps to configure
3. `reference/configuration-options.md` - Technical reference table

---

## Anti-Patterns

### ❌ Tutorial with API Reference

```markdown
---
doc_type: tutorial
---

# Your First API

[Tutorial content]

## API Reference
| Endpoint | Method | Description |
```

**Problem:** Reference table doesn't belong in tutorial (lookup vs learning).

**Fix:** Link to separate reference doc: "See [API Reference](../reference/api) for complete details."

### ❌ Reference Trying to Teach

```markdown
---
doc_type: reference
---

# API Reference

Let's learn about APIs! First, you need to understand REST...
[Teaching content in reference doc]
```

**Problem:** Reference should be dry lookup, not teaching.

**Fix:** Keep reference factual, link to explanation for concepts.

### ❌ How-To That's Actually a Tutorial

```markdown
---
doc_type: how-to
---

# How to Build Your First App

[Teaches from zero, learning-oriented]
```

**Problem:** "First" suggests tutorial (learning), not how-to (problem-solving).

**Fix:** Change to tutorial or make it assume knowledge: "How to Add Feature X to Existing App"

### ❌ Vague `doc_type`

```markdown
---
doc_type: guide
---
```

**Problem:** "guide" is ambiguous (tutorial or how-to?).

**Fix:** Use exact values: `tutorial`, `how-to`, `reference`, `explanation`

### ❌ No Sidebar Grouping

```
- Introduction
- Your First Project (Tutorial)
- API Reference (Reference)
- Deploy to AWS (How-To)
- Architecture (Explanation)
```

**Problem:** Types mixed together, hard to navigate by intent.

**Fix:** Group by type (Tutorials, How-To Guides, etc.)

---

## Frequently Asked Questions

**How do I know if it's a tutorial or how-to?**
→ Tutorial = learning-oriented, teaches from zero. How-To = problem-solving, assumes knowledge.

**Can a doc be both reference and how-to?**
→ No. Split into two docs: one with technical reference, one with task steps.

**What if my content doesn't fit any quadrant?**
→ It always fits. Ask: What's the user's intent? Learning, problem-solving, lookup, or understanding?

**Should I duplicate content across types?**
→ No. Link between docs. Tutorial links to reference, how-to links to explanation, etc.

**How do I handle very short docs?**
→ Still categorize by intent. A 2-paragraph reference is still reference.

**Can I put explanation in tutorials?**
→ Minimal context OK, but link to explanation doc for depth. Tutorial stays focused on doing.

**What about changelog or release notes?**
→ These are reference (information-oriented lookup).

---

## Related Standards

- `documentation-project-naming.md` - Use "Agent OS Enhanced" consistently
- `documentation-diagrams.md` - Use React components for all doc types
- `documentation-theming.md` - Theme docs consistently across quadrants
- `rag-content-authoring.md` - Optimize all doc types for RAG discoverability

---

## Maintenance

**Update this standard when:**
- Divio framework evolves (unlikely, stable framework)
- Project adds new doc patterns
- Validation scripts change requirements
- User feedback highlights categorization issues

**Periodic review:**
- Audit docs for type compliance (quarterly)
- Check for mixed-type content
- Validate sidebar organization
- Update examples with real project docs

**Last reviewed:** 2025-10-13

---

