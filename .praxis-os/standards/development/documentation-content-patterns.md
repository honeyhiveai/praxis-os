# Documentation Content Patterns Standards

**Keywords for search**: Docusaurus markdown patterns, admonishment usage, blockquote examples, code block semantic usage, clean typography documentation, content hierarchy markdown, visual containers documentation, modern docs aesthetic, HoneyHive docs style

---

## 🎯 TL;DR - Content Patterns Quick Reference

**Critical content rules:**

1. **Admonishments are containers, not emphasis** - Use sparingly for alerts/warnings, not every section
2. **Blockquotes for examples and sub-content** - Conversation examples, quoted content, visual indentation
3. **Code blocks ONLY for actual code** - Not for conversations, lists, or prose
4. **Typography does the work** - Headers, bold, italic, lists create hierarchy without boxes
5. **Clean over boxy** - Modern docs favor flowing prose over container overuse

**Keywords for search**: admonishment vs blockquote, code block semantic meaning, markdown content hierarchy, clean docs aesthetic, modern documentation patterns

**When to apply**: Writing any documentation content, refactoring existing docs, reviewing doc PRs

**Goal**: Achieve clean, modern aesthetic like HoneyHive main docs - readable prose with strategic visual elements

---

## Purpose

Ensure prAxIs OS documentation uses markdown content patterns semantically and aesthetically, creating clean, modern documentation that guides users without visual clutter. Content should flow naturally with typography providing hierarchy, reserving special containers (admonishments, blockquotes, code blocks) for their intended semantic purposes.

---

## The Problem

**Without content pattern standards:**
- Admonishments overused (every section in a colored box = visual fatigue)
- Code blocks used for non-code content (conversations, lists, diagrams)
- Typography underutilized (everything in containers instead of clean headers/lists)
- Docs feel "boxy" and cluttered instead of modern and flowing
- Users struggle to identify truly important callouts (everything highlighted = nothing highlighted)
- Semantic meaning lost (screen readers confused by misused markdown elements)

**Real-world examples of bad patterns:**
```markdown
:::info Key Point
This is important information.
:::

:::tip Another Point
This is also important.
:::

:::warning One More Thing
And this too!
:::
```
**Problem:** Everything in boxes → visual noise, no actual priority signal.

---

## The Standard

### 1. Admonishments: Use Sparingly for Alerts

**Purpose:** Critical alerts, warnings, context-sensitive information that MUST stand out.

**Docusaurus admonishment types:**
- `:::note` - Neutral supplementary information
- `:::tip` - Helpful suggestions or best practices
- `:::info` - Contextual information
- `:::warning` - Important warnings or gotchas
- `:::danger` - Critical errors or security issues

✅ **Good admonishment usage (1-2 per page max):**

```markdown
## Installation

Follow these steps to install prAxIs OS.

[Regular prose content]

:::warning Prerequisites Required
You must have Python 3.11+ installed. Earlier versions are not supported.
:::

[Continue with installation steps]
```

**Why good:** One critical warning that truly needs visual emphasis.

❌ **Bad admonishment usage (overuse):**

```markdown
:::info Overview
This section explains the concepts.
:::

## Core Concepts

:::tip First Concept
This is the first concept.
:::

:::tip Second Concept
This is the second concept.
:::

:::info Summary
Now you understand the concepts.
:::
```

**Why bad:** Every section boxed → visual fatigue, nothing stands out.

**Fix:** Use headers and clean prose:

```markdown
## Overview

This section explains the core concepts behind prAxIs OS.

## Core Concepts

### First Concept

This is the first concept. Here's how it works...

### Second Concept

This is the second concept. The key point is...

## Summary

Now you understand how these concepts work together.
```

### 2. Blockquotes: Examples, Quotes, and Sub-Content

**Purpose:** Visually indent examples, conversation transcripts, quoted content, or sub-explanations.

**When to use blockquotes:**
- Conversation/dialogue examples
- Quoted text from external sources
- Sub-content that needs visual indentation
- Multi-line examples that aren't code

✅ **Good blockquote usage (conversation example):**

```markdown
### Sample Correction Pattern

**Pattern:** Missing project context

> **AI:** "I'll implement the API handler..."  
> *[Implements generic solution]*  
> **User:** "This doesn't match our auth pattern"  
> **AI:** "Let me fix that to use the project's auth..."  
> *[3 more correction cycles]*

**Cost:** Each correction cycle adds 3-5 messages and 50KB+ tokens
```

**Why good:** 
- Blockquote provides visual indentation (orange left border in Docusaurus)
- Bold for speakers, italic for actions (clean typography)
- Clearly marks this as "example content" separate from main prose

✅ **Good blockquote usage (comparison structure):**

```markdown
### Cost Structure

**Traditional AI Assistance:**

> - Human writes code (slow, expensive)
> - AI suggests improvements (context overhead)
> - Human reviews suggestions (additional time)
> - Errors slip through (rework cost)
> - **Result:** Variable quality, high cost per feature

**prAxIs OS with RAG:**

> - **Upfront:** Spec creation (deliberate cost, ~2-4 hours)
> - **Execution:** AI writes 100% with RAG queries (efficient)
> - **Review:** Human approves intent (fast, ~30 min)
> - **Quality:** Enforced at commit (prevents rework)
> - **Result:** Consistent quality, lower cost per feature
```

**Why good:** Blockquotes create visual hierarchy for comparison sections while keeping clean list typography.

❌ **Bad blockquote usage (misuse for emphasis):**

```markdown
> This is an important point I want to emphasize.
```

**Why bad:** Blockquotes aren't for emphasis, use bold or admonishments for that.

**Fix:** Use bold inline or (if truly critical) an admonishment:

```markdown
**Important:** This is an important point to remember.
```

### 3. Code Blocks: ONLY for Actual Code

**Purpose:** Display code, commands, configuration files, or structured technical content.

**When to use code blocks:**
- Source code (Python, TypeScript, etc.)
- Shell commands
- Configuration files (JSON, YAML)
- API requests/responses
- Structured technical data

✅ **Good code block usage (actual code):**

```markdown
Install dependencies:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

Configure the server:

\`\`\`yaml
server:
  port: 8080
  host: 0.0.0.0
\`\`\`
```

❌ **Bad code block usage (conversation):**

```markdown
\`\`\`
AI: "I'll implement the API handler..."
[Implements generic solution]
User: "This doesn't match our auth pattern"
\`\`\`
```

**Why bad:** 
- Code blocks imply technical/executable content
- Monospace font wrong for prose
- Grey background suggests "copy this code"
- Wrong semantic meaning (not code)

**Fix:** Use blockquotes with typography (see section 2).

❌ **Bad code block usage (lists/prose):**

```markdown
\`\`\`
The benefits of this approach:
- Faster development
- Fewer errors
- Better quality
\`\`\`
```

**Why bad:** This is a list, not code. Use markdown lists.

**Fix:**

```markdown
The benefits of this approach:
- Faster development
- Fewer errors
- Better quality
```

### 4. Typography: Headers, Bold, Italic, Lists

**Purpose:** Create visual hierarchy and emphasis using native markdown typography instead of containers.

**Hierarchy tools:**
- `#` Headers - Structure and navigation
- **Bold** - Emphasis, labels, speakers
- *Italic* - Annotations, actions, secondary emphasis
- `-` Lists - Sequential items, bullet points
- `1.` Numbered lists - Ordered steps, rankings

✅ **Good typography usage (clean headers and lists):**

```markdown
## The Problem

**Without proper caching:**
- Slow page loads
- Redundant API calls
- Poor user experience

**The impact:** Each uncached request adds 200-500ms latency.

## The Solution

Use Redis for session caching:

1. Install Redis
2. Configure cache TTL
3. Update session handler

**Result:** 95% cache hit rate, 50ms average latency.
```

**Why good:**
- Headers create clear sections
- Bold creates emphasis without boxes
- Lists provide structure
- Clean, flowing prose

❌ **Bad typography usage (containers instead):**

```markdown
:::info The Problem
Without proper caching, you'll experience slow page loads, redundant API calls, and poor user experience.
:::

:::tip The Solution
\`\`\`
Install Redis, configure cache TTL, update session handler
\`\`\`
:::
```

**Why bad:** Overuses containers, buries information in boxes, uses code block for non-code.

### 5. Clean Aesthetic: Let Content Breathe

**Principle:** Modern documentation favors flowing prose over visual containers. Compare:

**Boxy style (old):**
- Every section in an admonishment
- Overuse of colored containers
- Visual fatigue
- Hard to scan

**Clean style (modern - HoneyHive main docs):**
- Headers and prose flow naturally
- Strategic use of containers (1-2 per page)
- White space and typography
- Easy to scan

✅ **Good clean aesthetic:**

```markdown
## Getting Started

prAxIs OS uses a spec-driven workflow. Here's how it works:

### 1. Write a Specification

Create a markdown spec in `.praxis-os/specs/` describing your feature:

**Key sections:**
- Goal - What you're building
- Requirements - Functional requirements
- Implementation - Technical approach

### 2. AI Implements from Spec

The AI reads your spec and implements with RAG query guidance:

> **AI:** *[Queries standards: "authentication patterns"]*  
> **AI:** *[Retrieves: Project-specific auth docs]*  
> **AI:** "I'll use the custom OAuth handler from the standards..."

### 3. Human Reviews Intent

You review that the AI understood your intent, not line-by-line code review.

**Review checklist:**
- [ ] Matches spec requirements
- [ ] Follows project standards
- [ ] Passes quality gates

**Time savings:** 2-4 hours implementation vs 30 min review.
```

**Why good:**
- Clean headers structure the content
- Bold and italic create emphasis
- One blockquote example (strategically placed)
- Lists for structured data
- No box overload

❌ **Bad boxy aesthetic:**

```markdown
:::info Getting Started
prAxIs OS uses a spec-driven workflow.
:::

:::tip Step 1: Write a Specification
Create a markdown spec describing your feature.
:::

:::tip Step 2: AI Implements
The AI reads your spec and implements.
:::

:::note Example
\`\`\`
AI: Queries standards
AI: Retrieves docs
AI: Uses custom handler
\`\`\`
:::

:::info Step 3: Review
You review that the AI understood your intent.
:::
```

**Why bad:** Everything boxed, visual noise, hard to read.

---

## Decision Guide: Which Pattern to Use?

**Use this flowchart to decide:**

```
What type of content are you writing?

1. Is this code, commands, or technical syntax?
   → YES: Use ```code blocks```

2. Is this a critical warning or alert that MUST stand out?
   → YES: Use :::admonishment (sparingly!)

3. Is this a conversation example, quote, or sub-explanation?
   → YES: Use > blockquote

4. Is this normal content (explanations, steps, lists)?
   → YES: Use clean typography (headers, bold, lists)
```

**Example applications:**

| Content Type | Pattern | Example |
|--------------|---------|---------|
| Python code | Code block | `\`\`\`python` |
| Shell command | Code block | `\`\`\`bash` |
| Conversation | Blockquote | `> **AI:** "I'll implement..."` |
| Warning | Admonishment | `:::warning` (1-2 per page) |
| Section header | Typography | `## Getting Started` |
| Emphasis | Typography | `**Important:**` |
| List | Typography | `- Item 1` |
| Steps | Typography | `1. First step` |

---

## Checklist

**Before writing documentation content:**

- [ ] Identified content types (code vs examples vs prose)
- [ ] Planned header structure (H2, H3, H4 hierarchy)
- [ ] Decided if any admonishments truly needed (aim for 0-2 per page)
- [ ] Considered blockquotes for examples/quotes only
- [ ] Code blocks reserved for actual code

**While writing:**

- [ ] Using headers to structure content
- [ ] Using bold/italic for inline emphasis
- [ ] Using lists for sequential items
- [ ] Admonishments only for critical alerts (not every section)
- [ ] Blockquotes for examples/quotes (not emphasis)
- [ ] Code blocks for code only (not conversations or prose)

**After writing (aesthetic check):**

- [ ] Content flows naturally (not overly boxy)
- [ ] Headers create clear sections
- [ ] Admonishments count: 0-2 per page
- [ ] No code blocks used for non-code content
- [ ] Clean, scannable, modern aesthetic

---

## Examples

### Example 1: Refactoring from Boxy to Clean

**Before (boxy, admonishment overuse):**

```markdown
:::info Key Insight
The cost per message increased despite overall savings.
:::

:::warning Pattern 1: Missing Context
\`\`\`
AI: "I'll implement the API handler..."
User: "This doesn't match our auth pattern"
AI: "Let me fix that..."
\`\`\`
:::

:::warning Pattern 2: Wrong Assumptions
\`\`\`
AI: "I'll use standard error handling..."
User: "We have a custom error handler"
\`\`\`
:::

:::tip Query Before Implementing
\`\`\`
AI: [Queries standards]
AI: [Retrieves docs]
AI: "I'll use the custom handler..."
\`\`\`
:::

:::info Summary
Query standards before implementing to reduce correction cycles.
:::
```

**After (clean typography with strategic blockquotes):**

```markdown
## The Surprising Finding: Cost Per Message Increased

Despite 54% overall cost reduction, **cost per message increased 2.3%**. Why?

**The mechanism:** More search_standards queries added upfront cost per message, but dramatically reduced correction cycles. The tradeoff: slightly higher per-message cost for massively fewer total messages.

### Sample Correction Patterns (September)

#### Pattern 1: Missing Context

> **AI:** "I'll implement the API handler..."  
> *[Implements generic solution]*  
> **User:** "This doesn't match our auth pattern"  
> **AI:** "Let me fix that to use the project's auth..."  
> *[3 more correction cycles]*

**Cost:** Each correction cycle adds 3-5 messages and 50KB+ tokens

#### Pattern 2: Wrong Assumptions

> **AI:** "I'll use standard error handling..."  
> *[Implements based on training data]*  
> **User:** "We have a custom error handler"  
> **AI:** "My mistake, let me update to use the custom handler..."

**Cost:** 2-4 correction messages per assumption

### Sample Query-First Pattern (October)

#### Query Before Implementing

> **AI:** *[Queries standards: "error handling patterns"]*  
> **AI:** *[Retrieves: Custom error handler documentation]*  
> **AI:** "I'll use the project's custom error handler..."  
> *[Implements correctly first time]*  
> **User:** "Looks good"

**Cost:** One query (~2KB) vs multiple correction cycles (~50KB+)

## Key Takeaways

**Query standards before implementing.** Upfront cost pays off through eliminated correction cycles.
```

**What changed:**
- ❌ Removed 5 admonishments
- ✅ Added clean headers (H2, H3, H4)
- ✅ Used blockquotes for conversation examples (semantic meaning + visual indent)
- ✅ Used bold for emphasis and labels
- ✅ Used italic for action annotations
- ✅ Removed code blocks from non-code content
- ✅ Clean, flowing prose with strategic visual hierarchy

### Example 2: When to Actually Use Admonishments

✅ **Good use (1 admonishment, truly critical):**

```markdown
## Installation

Follow these steps to install prAxIs OS on your system.

### Prerequisites

- Python 3.11 or later
- Git
- 4GB RAM minimum

:::warning Docker Not Supported Yet
prAxIs OS does not currently support Docker deployment. Docker support is planned for v2.0. 
For now, install directly on your system or use a virtual environment.
:::

### Step 1: Clone Repository

[Installation continues...]
```

**Why good:** One critical warning that saves users from wasting time trying Docker.

❌ **Bad use (admonishment for every section):**

```markdown
:::info Prerequisites
You need Python, Git, and RAM.
:::

:::tip Step 1
Clone the repository.
:::

:::tip Step 2
Install dependencies.
:::

:::note Summary
You've now installed prAxIs OS.
:::
```

**Why bad:** Admonishments provide no value, just visual clutter.

### Example 3: Code Blocks vs Blockquotes

**Scenario:** Showing a conversation example

❌ **Wrong (code block):**

```markdown
\`\`\`
AI: "What's the authentication pattern?"
User: "We use OAuth 2.0 with custom claims"
AI: "I'll implement that."
\`\`\`
```

**Why wrong:** Grey monospace box suggests this is code to copy/execute. Wrong semantic meaning.

✅ **Right (blockquote with typography):**

```markdown
> **AI:** "What's the authentication pattern?"  
> **User:** "We use OAuth 2.0 with custom claims"  
> **AI:** "I'll implement that."
```

**Why right:** 
- Orange left border visually separates as example
- Bold for speakers (clear roles)
- Proper prose rendering (not monospace)
- Correct semantic meaning (quoted dialogue)

**Scenario:** Showing actual code

✅ **Right (code block):**

```markdown
Implement the authentication handler:

\`\`\`typescript
export function authenticate(token: string): User {
  const claims = verifyOAuth(token);
  return createUser(claims);
}
\`\`\`
```

**Why right:** This IS code. Code blocks are correct.

---

## Anti-Patterns

### ❌ Admonishment for Every Section

```markdown
:::info Section 1
Content here.
:::

:::tip Section 2
More content.
:::

:::note Section 3
Even more content.
:::
```

**Problem:** Visual fatigue, nothing stands out, boxy aesthetic.

**Fix:** Use headers and clean prose.

### ❌ Code Block for Conversations

```markdown
\`\`\`
AI: "I'll implement..."
User: "That's wrong"
\`\`\`
```

**Problem:** Wrong semantic element (not code), grey box misleading.

**Fix:** Use blockquote with typography.

### ❌ Blockquote for General Emphasis

```markdown
> This is really important!
```

**Problem:** Blockquotes are for quotes/examples, not emphasis.

**Fix:** Use bold or (if critical) admonishment.

### ❌ Lists in Code Blocks

```markdown
\`\`\`
The benefits:
- Faster
- Better
- Cheaper
\`\`\`
```

**Problem:** This is a list, not code.

**Fix:** Use markdown lists.

---

## Frequently Asked Questions

**How many admonishments per page is too many?**
→ Aim for 0-2. If you need more than 2, your content likely needs better structure with headers.

**When should I use blockquotes vs admonishments?**
→ Blockquotes for examples/quotes (visual indent). Admonishments for critical alerts (colored box with icon).

**Can I use code blocks for pseudo-code?**
→ Yes, pseudo-code is code-like enough. But conversations, lists, and prose should never be in code blocks.

**What if I want to emphasize something but not use an admonishment?**
→ Use bold inline: `**Important:**` or a header if it's a major point.

**How do I create visual hierarchy without boxes?**
→ Headers (H2, H3, H4), bold labels, lists, whitespace. Typography is powerful.

**The old docs use lots of admonishments. Should I refactor?**
→ Yes, when editing a doc, reduce admonishments to 0-2 and use clean typography patterns.

---

## Related Standards

- `documentation-divio-framework.md` - Organize content by doc type (applies to all content patterns)
- `documentation-diagrams.md` - Use React components for complex visual content
- `documentation-theming.md` - Theme visual elements (CSS for blockquotes, etc.)
- `rag-content-authoring.md` - Structure content for RAG discoverability

---

## Maintenance

**Update this standard when:**
- New content patterns emerge from HoneyHive main docs
- Docusaurus adds new markdown features
- User feedback highlights confusing pattern usage
- Aesthetic trends shift (e.g., new modern doc styles)

**Periodic review:**
- Audit docs for admonishment overuse
- Check for code blocks used for non-code content
- Validate clean aesthetic across documentation
- Compare to HoneyHive main docs for alignment

**Last reviewed:** 2025-10-29

---

