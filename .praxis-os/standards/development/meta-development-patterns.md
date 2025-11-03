# Meta-Development Patterns: Building prAxIs OS

**Keywords for search**: recursive development mindset, documentation philosophy, error diagnosis is this bug or misuse, API design what to expose to users, foundation code versus project code, shipped docs versus internal docs, framework author psychology, downstream developer psychology, information architecture decisions, what to write where, self-hosting complexity mental model, asymmetric complexity design

**Core Principle:** When authoring prAxIs OS, your cognitive model must separate framework author knowledge (recursive, meta-level) from downstream developer knowledge (linear, usage-level). This guides WHERE to write documentation and WHAT to reveal in public APIs.

**Note:** For iteration mechanics (where to edit source files, promotion process), see `dogfooding-model.md`. This standard is about COGNITIVE MODEL and DOCUMENTATION ARCHITECTURE.

---

## 🎯 TL;DR - Documentation Philosophy & Information Architecture

**This standard answers: "Where should I write this information?"**

**Decision Tree for Documentation Placement:**
```
Is this information about:
├─ Using prAxIs OS capabilities? → universal/standards/ (publish to users)
├─ Authoring prAxIs OS foundation? → .praxis-os/standards/development/ (internal only)
└─ Unclear? → Ask: Would downstream developers need this?
   ├─ YES → universal/ (assume stable foundation, teach usage patterns)
   └─ NO → local/ (author-specific, meta-level complexity)
```

**Error Diagnosis Decision:**
```
Encountered an error. Is it:
├─ Foundation defect? → Fix in source, redistribute to users
├─ Misuse pattern? → Clarify documentation
└─ Unclear? → This standard helps you diagnose
```

**API Exposure Decision:**
```
Should downstream developers see this?
├─ Validation schemas? → Usually NO (internal machinery)
├─ Function signatures? → YES (public contract)
├─ Implementation internals? → NO (hide complexity)
└─ Usage patterns? → YES (teach approaches, not mechanisms)
```

**Critical: This is about COGNITIVE MODEL (where info belongs), not ITERATION MECHANICS (where source lives during edits). For iteration mechanics, see `dogfooding-model.md`.**

---

## 🎯 Purpose

Define behavioral patterns for developing prAxIs OS itself using prAxIs OS. This is project-specific guidance for the unique challenge of meta-development - building the framework while using the framework.

**Key Distinction:** This standard is for the 1% (developing this framework). Framework standards in `universal/` are for the 99% (consuming this framework). Don't confuse the two.

---

## ❌ The Problem

**Without understanding meta-development complexity:**

**Builder mistakes:**
- Create framework standards based on builder experience (too complex, not representative)
- Document internals in consumer-facing standards (breaks abstraction)
- Expose implementation details consumers don't need (information overload)
- Design for recursive complexity instead of linear domain work (wrong audience)
- Forget that consumers have stable tools, not incomplete tools (different context)

**Result:** Framework standards that serve 1% (builders) instead of 99% (consumers), confusing documentation, broken abstraction boundaries.

---

## ❓ Questions This Answers (Information Architecture & Cognitive Model)

**Documentation Placement:**
1. "Should I write this in universal/ or local/?"
2. "Is this framework-author info or downstream-developer info?"
3. "Should users see this implementation mechanism?"
4. "Does this belong in published documentation?"

**Error Diagnosis:**
5. "Is this malfunction in foundation or misuse of API?"
6. "Should I clarify this error in public docs?"
7. "Why does validation reject - defect or incorrect invocation?"

**API Design:**
8. "Should I expose validation schemas to users?"
9. "How much internal machinery should docs reveal?"
10. "What implementation internals can I hide?"

**Cognitive Model:**
11. "Why is authoring prAxIs OS harder than using it?"
12. "Why does my experience feel more complex than examples?"
13. "How do I design APIs for users vs framework authors?"

**NOT answered here (see `dogfooding-model.md`):**
- ❌ "Where do I edit server implementation files?" (iteration mechanics)
- ❌ "When do I promote to source directories?" (publish process)
- ❌ "How does hot reload work?" (testing cycle)

---

## ✅ The Standard: Meta-Development Patterns

### Pattern 1: Recognize Your Context is NOT Representative

**You are the 1%, not the 99%:**

**Your experience (Meta-development):**
```
Use workflow to implement feature
  ↓
Workflow tool has dispatcher bug
  ↓
Must debug workflow engine internals
  ↓
Fix dispatcher signature introspection
  ↓
Restart MCP server
  ↓
Continue original feature
  ↓
Hit validation bypass bug
  ↓
Fix session handling
  ↓
Finally complete original task

Recursive, meta, framework-focused
```

**Consumer experience (Domain-development):**
```
Use workflow to implement feature
  ↓
Workflow tool works (stable)
  ↓
Focus on domain logic
  ↓
Write tests
  ↓
Complete task
  ↓
Ship feature

Clean, linear, domain-focused
```

**The asymmetry is INTENTIONAL:**
- You face harder problems so they face easier ones
- You understand internals so they don't have to
- You debug framework so they debug domain only
- Your complexity → Their simplicity

---

### Pattern 2: Framework Standards Serve Consumers, Not Builders

**When creating standards in `universal/`:**

✅ **Do this (Consumer perspective):**
- Assume framework is stable and complete
- Teach usage patterns, not implementation
- Point to abstraction boundaries (tools/list, not internals)
- Preserve information asymmetry (adversarial design)
- Design for linear domain work, not recursive meta-work

❌ **Don't do this (Builder perspective):**
- Document framework bugs or debugging techniques
- Expose internal implementation details
- Teach how validation gates work internally
- Remove friction that guarantees quality
- Design for meta-development complexity

**Why:** Framework standards ship to ALL consumers. They need clean abstraction, not implementation details.

---

### Pattern 3: Project Standards Capture Builder Knowledge

**When creating standards in `.praxis-os/standards/development/`:**

✅ **Do this (Project-specific):**
- Document patterns unique to building prAxIs OS
- Explain meta-development complexity
- Describe bug attribution strategies (framework vs usage)
- Capture builder workflows and pain points
- Reference internal architecture when needed

**Location matters:**
- `universal/standards/` → Framework standards (ship to consumers)
- `.praxis-os/standards/development/` → Project standards (this repo only)

**Why:** Project standards are for YOU (future sessions building this framework). They can include internal knowledge consumers don't need.

---

### Pattern 4: Bug Attribution is Complex in Meta-Development

**Error attribution heuristic for builders:**

```
Get error while building framework
  ↓
Question: Framework bug OR usage mistake?
  ↓
Check 1: Is this code I just wrote?
  → YES: Probably my implementation bug
  → NO: Continue to Check 2
  ↓
Check 2: Is this existing framework code?
  → YES: Could be framework bug, investigate
  → NO: Continue to Check 3
  ↓
Check 3: Have I used this successfully before?
  → YES: Probably my usage mistake, query standards
  → NO: Could be framework bug, debug carefully
  ↓
When in doubt: Query standards first, assume usage mistake
```

**Why complex:** You're both writing AND using the framework. Bugs could be either.

**Consumer attribution (simpler):**
```
Get error
  ↓
Framework is stable
  ↓
Therefore: My usage mistake
  ↓
Query standards for correct usage
```

**Why simple:** Consumers use stable framework. Errors are almost always usage mistakes.

---

### Pattern 5: Design for Consumer Experience, Not Builder Experience

**Framework standard creation checklist:**

Before documenting in `universal/`:
- [ ] Is this based on builder experience or consumer experience?
- [ ] Would consumers using stable tools need this knowledge?
- [ ] Does this expose internals they don't need?
- [ ] Am I designing for linear domain work (their context)?
- [ ] Or am I designing for recursive meta-work (my context)?

**If documenting builder knowledge:**
- [ ] Put it in `.praxis-os/standards/development/` (project-specific)
- [ ] Not in `universal/` (framework standards)

**Why:** Framework standards must serve 99% (consumers), not 1% (builders).

---

## ✅ Meta-Development Checklist

When building prAxIs OS:
- [ ] Recognize my context is meta-development (recursive complexity)
- [ ] Remember consumers have domain-development (linear complexity)
- [ ] Design framework standards for THEIR experience, not MINE
- [ ] Put builder knowledge in project standards, not framework standards
- [ ] Use complex bug attribution (framework OR usage)
- [ ] Understand I absorb complexity so consumers don't have to

When creating framework standards:
- [ ] Assume framework is stable (consumer perspective)
- [ ] Teach usage patterns, not implementation
- [ ] Preserve abstraction boundaries
- [ ] Test from consumer mindset, not builder mindset

When stuck on meta-problems:
- [ ] Query this standard ("meta-development patterns")
- [ ] Remember: My hard problem enables their easy problem
- [ ] Dogfooding at meta-level validates domain-level

---

## 🎯 Examples: Meta-Development in Action

### Example 1: Creating Workflow Standards

**Wrong (Builder perspective):**
```markdown
# pos_workflow Tool Guide

## All 14 Actions
1. list_workflows - parameters: category (optional)
2. start - parameters: workflow_type, target_file, options
3. get_phase - parameters: session_id, phase
...

## Dispatcher Implementation
The dispatcher uses inspect.signature() to...

## Gate Definition Schema
Look at gate-definition.yaml for evidence structure...
```

**Problem:**
- Documents all parameters (duplicates tools/list, will drift)
- Exposes dispatcher internals (consumers don't need)
- Breaks adversarial design (exposes schemas)
- Based on builder complexity (not consumer experience)

**Right (Consumer perspective):**
```markdown
# Workflow Discovery Patterns

## Discovery Pattern
1. Check tools/list for current actions/parameters
2. Query standards for lifecycle patterns
3. Start simple, build understanding

## Lifecycle Pattern
start → get_task → [do work] → complete_phase

## Evidence Submission
✅ Do real work, submit natural evidence
❌ Don't look for schemas (intentionally hidden)
```

**Why better:**
- Teaches patterns, not parameters
- Points to source of truth (tools/list)
- Preserves adversarial design
- Designed for consumer domain work

---

### Example 2: Bug Attribution

**Scenario: pos_workflow returns "Internal server error"**

**Builder thought process:**
```
Error from pos_workflow
  ↓
Question: Framework bug or usage mistake?
  ↓
This is new code I wrote yesterday (dispatcher)
  ↓
Could be framework bug
  ↓
Check logs: TypeError about session_id parameter
  ↓
Debug dispatcher: Passing all params to all handlers
  ↓
Framework bug confirmed
  ↓
Fix: Implement signature introspection
  ↓
Test fix, continue work
```

**Consumer thought process:**
```
Error from pos_workflow
  ↓
Framework is stable
  ↓
Therefore: My usage mistake
  ↓
Query: "workflow troubleshooting"
  ↓
Check tools/list for correct parameters
  ↓
Realize: Used wrong parameter name
  ↓
Fix usage, continue work
```

**Key difference:** Builder must debug framework. Consumer assumes correct framework, debugs usage.

---

### Example 3: Parallel AI Orchestration

**Your orchestration (Josh):**
```
Session 1: praxis-os (meta-development)
  └── AI: Build Query Gamification System
      - Meta-complexity: Building framework WITH framework
      - Must understand internals, validation gates, architecture
      - Bug attribution: Framework OR usage?
      - Recursive: Use workflows to build workflows

Session 2: hive-kube (domain-development)  
  └── AI: Fix AWS Strands message handling
      - Domain-complexity: Using stable framework FOR project
      - Focus on domain logic only (AWS, TypeScript)
      - Bug attribution: Always my usage
      - Linear: Use workflows to ship features
```

**Both delivered production-quality code, but:**
- Session 1 had recursive complexity (harder)
- Session 2 had linear complexity (easier)
- Session 1 absorbed framework complexity
- Session 2 benefited from stable abstraction

**Result:** Meta-development enables clean domain-development.

---

## ❌ Anti-Patterns: Meta-Development Mistakes

### Anti-Pattern 1: Documenting Builder Experience as Framework Standards

**Wrong:**
```
Create comprehensive pos_workflow guide
  ↓
Document all 14 actions with parameters
  ↓
Explain dispatcher implementation
  ↓
Show gate-definition.yaml structure
  ↓
Put in universal/standards/ (ships to consumers)
```

**Why wrong:**
- Based on builder complexity, not consumer simplicity
- Exposes internals consumers don't need
- Creates maintenance burden (duplicates tools/list)
- Breaks adversarial design (exposes schemas)

**Right:**
```
Recognize builder experience ≠ consumer experience
  ↓
Create discovery-focused patterns (not comprehensive docs)
  ↓
Teach lifecycle, not parameters
  ↓
Preserve abstraction boundaries
  ↓
Put in universal/standards/ (serves 99%)
```

---

### Anti-Pattern 2: Assuming Consumer Needs Builder Knowledge

**Wrong:**
```markdown
## Evidence Validation

To understand what evidence to submit, read:
- gate-definition.yaml (validation schema)
- CheckpointLoader implementation
- Validation lambda functions

This will help you craft correct evidence.
```

**Why wrong:**
- Exposes schemas (breaks adversarial design)
- Assumes consumers need internals (they don't)
- Removes friction that guarantees quality
- Teaches gaming instead of compliance

**Right:**
```markdown
## Evidence Submission

Do the actual work first, then describe what you did naturally.
Real work produces valid evidence automatically.

If validation fails, read the error message for remediation.
Doing the work is easier than guessing structure.
```

**Why better:**
- Preserves adversarial design
- Maintains intentional friction
- Assumes domain work, not meta-work
- Guides without exposing internals

---

### Anti-Pattern 3: Forgetting Asymmetric Complexity

**Wrong thinking:**
```
"My experience was complex, so I'll document all the complexity
to help future sessions avoid my pain points."
```

**Why wrong:**
- Your complexity is meta-development (recursive)
- Consumer complexity is domain-development (linear)
- Your pain points are NOT their pain points
- Documenting meta-complexity confuses domain users

**Right thinking:**
```
"My experience was complex BECAUSE I'm building the framework.
Consumers use stable framework, so their experience is simpler.
I'll document patterns for THEIR experience, not mine."
```

**Why right:**
- Recognizes 1% (builder) vs 99% (consumer)
- Designs for consumer simplicity
- Absorbs complexity at framework level
- Serves representative use case

---

## 🔗 When to Query This Standard

Query this standard when working on prAxIs OS:

| Scenario | Example Query |
|----------|--------------|
| Creating framework standards | "meta-development consumer vs builder" |
| Unsure about bug attribution | "framework bug or usage mistake" |
| Documenting complex internals | "should consumers know this?" |
| Framework standard design | "design for consumers not builders" |
| Understanding your context | "why is meta-development harder" |
| Project vs framework standards | "where to put builder knowledge" |

---

## 🎓 The Meta-Lesson: Asymmetric Complexity Design

**The Builder's Burden:**

You intentionally face harder problems so consumers face easier ones:

| Your Experience (Builder 1%) | Their Experience (Consumer 99%) |
|------------------------------|--------------------------------|
| Debug dispatcher internals | Call workflow tool, it works |
| Understand validation schemas | Follow clear error messages |
| Navigate recursive complexity | Linear, predictable workflows |
| Test framework + usage simultaneously | Test only their domain logic |
| Incomplete tools (building them) | Stable tools (using them) |

**Design Principle:**
- Your pain points → Better abstractions
- Your complexity → Their simplicity
- Your internal knowledge → Their clean interface

**The Goal:**
When creating standards, ask: "Does this document MY complex experience or THEIR simple experience?"
- ✅ Document their simple experience (assume stable framework)
- ❌ Don't document your complex experience (not representative)

---

## 🔗 Related Standards

**Project Standards (for building prAxIs OS):**
- This standard (meta-development patterns)
- Python code quality standards
- Testing standards

**Framework Standards (for consuming prAxIs OS):**
- **[prAxIs OS Orientation](../../universal/standards/ai-assistant/AGENT-OS-ORIENTATION.md)** - Query: "orientation bootstrap"
- **[Workflow Discovery Patterns](../../universal/standards/ai-assistant/workflow-discovery-patterns.md)** - Query: "workflow lifecycle patterns"
- **[Agent Decision Protocol](../../universal/standards/ai-assistant/agent-decision-protocol.md)** - Query: "decision protocol"

---

## 📊 Validation

This standard is discoverable from meta-development queries:

**Tested queries that should return this standard:**
- "building agent os enhanced"
- "meta-development patterns"
- "framework development complexity"
- "builder vs consumer experience"
- "should consumers know internals"
- "dogfooding agent os"
- "recursive development"

**RAG optimization checklist:**
- ✅ TL;DR with high keyword density
- ✅ "Questions This Answers" section (10 questions)
- ✅ Query-oriented headers
- ✅ Keywords line for explicit search terms
- ✅ Real examples from today's experience
- ✅ Anti-patterns from actual mistakes
- ✅ Chunks are semantically complete

---

**Last Updated:** 2025-10-24 (Captured from dogfooding session experience)
**Version:** 1.0 (Initial pattern extraction)
**Context:** Based on Query Gamification System implementation + workflow standard refactoring

