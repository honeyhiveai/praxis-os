---
sidebar_position: 5
doc_type: explanation
---

# Specs: Historical Context Through Git

This page explains how **specs** create knowledge compounding in prAxIs OS through git-preserved design documentation that captures the "why" behind your project's evolution.

**What you'll understand:**
- How specs preserve decision history
- Why specs are NOT RAG indexed (intentionally)
- When to read specs vs query standards
- The compounding effect of documented decisions
- How specs and standards work together

---

## What Are Specs?

**Specs** (specifications) are comprehensive design documents that capture requirements, architecture decisions, trade-offs, and implementation plans for features.

**Location:** `.praxis-os/specs/YYYY-MM-DD-feature-name/`

**Access:** `read_file(".praxis-os/specs/...")` when needed

**Purpose:** Preserve the "why" and "how" of decision-making for future reference

---

## Spec Structure

Each spec directory contains:

```
.praxis-os/specs/2025-10-15-authentication-system/
├── README.md           # Executive summary
├── srd.md             # System Requirements Document
├── specs.md           # Technical specifications
├── tasks.md           # Implementation breakdown
└── implementation.md  # Detailed implementation guidance
```

**Each file serves a purpose:**
- **README.md**: Quick overview, business context
- **srd.md**: Requirements, user stories, success criteria
- **specs.md**: Architecture, technical decisions, trade-offs
- **tasks.md**: Phase-by-phase implementation plan
- **implementation.md**: Detailed guidance for execution

---

## Why Specs Are NOT RAG Indexed

### Intentional Design Decision

Specs are deliberately **NOT** indexed by RAG semantic search:

**Why NOT indexed:**

1. **Too Specific**: Specs are feature-specific implementations, not reusable patterns
2. **Would Pollute RAG**: Would add noise to pattern discovery queries
3. **Accessed Deliberately**: Read when you need specific context, not discovered accidentally
4. **Wrong Granularity**: Too detailed for pattern matching

**Example of pollution:**
```python
# If specs were indexed:
search_standards("authentication")
# Returns: 
#  - Your auth standard (pattern) ✅
#  - Auth spec from 2025-01-15 (implementation details) ❌
#  - Auth spec from 2025-03-20 (different feature) ❌
#  - OAuth spec from 2025-05-10 (unrelated) ❌
# → Can't find the pattern in the noise
```

### Better Access Pattern

**Specs are read directly when you need them:**

```python
# You know what you're looking for:
read_file(".praxis-os/specs/2025-01-15-authentication-system/specs.md")

# OR browse directory:
list_dir(".praxis-os/specs/")

# OR search with git:
git grep "authentication" .praxis-os/specs/
```

**This is intentional**—you access specs deliberately, not through discovery.

---

## The Problem Specs Solve

### Without Specs: Lost Context

**Scenario: Six Months Later**

**You (or new team member):**
- "Why did we choose JWT over sessions?"
- "What were the requirements that led to this architecture?"
- "Why is the refresh token flow so complex?"

**Without specs:**
- ❌ No record of requirements
- ❌ Lost track of trade-offs considered
- ❌ Can't remember why certain decisions were made
- ❌ Must reverse-engineer from code
- ❌ Or ask someone who might have left

**Result:** Decisions questioned, refactors based on incomplete understanding, technical debt.

---

### With Specs: Preserved Context

**Same scenario, six months later:**

**You (or new team member):**
- "Why did we choose JWT over sessions?"

**With specs:**
```bash
# Read the spec
read_file(".praxis-os/specs/2025-01-15-authentication-system/specs.md")
```

**Finds in spec:**
```markdown
## Authentication Approach: JWT vs Sessions

**Decision:** Use JWT with refresh tokens

**Rationale:**
- Mobile app needs offline capability
- Microservices architecture (stateless preferred)
- 10K+ concurrent users (session storage doesn't scale)
- Security: Short-lived access tokens + secure refresh flow

**Trade-offs Considered:**
- Sessions simpler but require Redis clustering
- JWT has size overhead but eliminates state
- Refresh tokens add complexity but improve security

**Rejected Alternatives:**
1. Pure sessions - doesn't scale for our traffic
2. Long-lived JWT - security risk
3. OAuth - overkill for our use case
```

**Result:** Complete context preserved, decisions understood, confidence in architecture.

---

## How Specs Compound Knowledge

### The Accumulation Effect

import SpecsProgression from '@site/src/components/SpecsProgression';

<SpecsProgression />

### What Compounds

**Requirements Context:**
- Business needs that drove decisions
- User stories and use cases
- Success criteria and constraints

**Technical Decisions:**
- Architecture choices and rationale
- Technology selection reasoning
- Trade-offs and alternatives considered

**Evolution History:**
- How features changed over time
- Why pivots happened
- What was learned

**Institutional Knowledge:**
- Domain understanding
- Integration approaches
- Performance requirements

---

## When to Read Specs

### Use Cases for Spec Reading

**1. Understanding Historical Decisions**
- **Question:** "Why did we implement it this way?"
- **Action:** Read the spec for that feature
- **Result:** Understand rationale and trade-offs

**2. Onboarding to Complex Features**
- **Situation:** Working on authentication for first time
- **Action:** Read authentication spec
- **Result:** Understand architecture before touching code

**3. Refactoring Decisions**
- **Concern:** "Should we refactor this?"
- **Action:** Read original spec to understand requirements
- **Result:** Make informed decision based on original intent

**4. Debugging Architectural Issues**
- **Problem:** System behavior unclear
- **Action:** Read specs to understand intended design
- **Result:** Identify if bug or misunderstood architecture

**5. Planning Related Features**
- **Task:** Build feature related to existing system
- **Action:** Read related specs to understand integration points
- **Result:** Consistent with existing architecture

---

## How Specs and Standards Work Together

### Complementary, Not Redundant

**Specs answer:** "Why did we build it this way?"

**Standards answer:** "How should I build things?"

### Example: Authentication

**Spec** (`.praxis-os/specs/2025-01-15-authentication-system/`):
```markdown
# Authentication System Spec

## Requirements
- Support 10K concurrent users
- Mobile + web clients
- Offline capability needed
- Session timeout: 30 minutes

## Architecture
JWT with refresh token flow because:
- Stateless (scales horizontally)
- Works offline (mobile)
- Microservices-friendly

## Implementation
[Detailed design of the specific system]
```

**Standard** (`.praxis-os/standards/development/jwt-authentication.md`):
```markdown
# JWT Authentication Standard

## The Pattern
All JWT tokens must:
- Use RS256 algorithm
- Include: user_id, role, exp, iat
- Access token: 15 min lifetime
- Refresh token: 7 day lifetime

## Example
```python
def create_access_token(user_id):
    return jwt.encode({
        "user_id": user_id,
        "role": user.role,
        "exp": now() + 15_minutes,
        "iat": now()
    }, private_key, algorithm="RS256")
```
```

**The relationship:**
- **Spec**: WHY we use JWT, WHAT the system does
- **Standard**: HOW to implement JWT tokens consistently

**When AI works on auth:**
1. Queries standard → Discovers HOW pattern
2. Reads spec (if needed) → Understands WHY context
3. Implements → Follows standard, respects original intent

---

## The Git History Dimension

### Specs + Git = Complete Evolution Story

**Git preserves:**
- When spec was created (commit date)
- Who created it (commit author)
- Why it changed (commit messages)
- How it evolved (git diff)

**Example workflow:**
```bash
# See when authentication was added
git log --all --oneline -- ".praxis-os/specs/*authentication*"

# See what changed in auth spec
git log -p .praxis-os/specs/2025-01-15-authentication-system/specs.md

# See why OAuth was added later
git show abc123:.praxis-os/specs/2025-03-20-oauth-integration/
```

**Value:**
- Decisions tracked over time
- Evolution visible
- Context never lost
- Rationale preserved

---

## Real-World Example

### Without Specs: Mystery Code

**Month 1:** Implement complex retry logic in API client

**Month 6:** New developer
- "Why is this retry logic so complicated?"
- "Why do we wait 5 seconds between retries?"
- "Why exponential backoff only after 3 failures?"

**Without spec:**
- Code has no context
- Original requirements unknown
- Must guess or ask around
- Might "simplify" and break edge cases

---

### With Specs: Documented Context

**Month 1:** Implement API client with spec

**Spec documents:**
```markdown
# API Client Spec

## Requirement: Handle External API Rate Limits

External API limitations:
- Rate limit: 100 req/min
- Returns 429 after limit
- Requires 5-second backoff
- Three strikes = 10 min lockout

## Retry Strategy

Simple retry (first 3 attempts):
- Immediate retry on network errors
- 5-second delay on 429 (per API docs)

Exponential backoff (after 3 failures):
- Prevents three-strikes lockout
- Back off: 10s, 20s, 40s
- Give API time to recover

## Why Not Simpler?
Simple retry would trigger lockout,
making service unavailable for 10 minutes.
```

**Month 6:** New developer
- Reads spec
- Understands requirements
- Sees rationale for complexity
- Doesn't "simplify" and break it

---

## Creating Specs That Compound

### What Makes a Good Spec

**1. Capture Requirements**
- What business needs drove this?
- What constraints exist?
- What success looks like?

**2. Document Decisions**
- What was decided?
- Why this approach over alternatives?
- What trade-offs were made?

**3. Explain Trade-offs**
- What alternatives were considered?
- Why were they rejected?
- What are the limitations?

**4. Provide Context**
- What problem does this solve?
- How does it fit the bigger picture?
- What future considerations exist?

**5. Be Specific**
- Concrete requirements, not vague goals
- Actual numbers and constraints
- Real examples and use cases

---

### Example: Good vs Poor Spec

**Poor Spec:**
```markdown
# User Management

Build user management system.
Should be secure and scalable.
Use database to store users.
```

**Good Spec:**
```markdown
# User Management System

## Requirements
- Support 50K active users (current), 500K growth target
- GDPR compliance required (EU customers)
- Password-based + OAuth (Google, GitHub)
- Self-service password reset (reduce support tickets)

## Architecture Decisions

**Choice:** PostgreSQL with row-level security

**Why:**
- ACID guarantees for user data
- Row-level security for GDPR compliance
- JSON columns for flexible user metadata
- Scales to 500K users (validated with load tests)

**Alternatives Considered:**
1. MongoDB - easier, but no ACID guarantees for user data
2. MySQL - works, but RLS requires application-level logic
3. Firebase Auth - simple, but vendor lock-in concern

**Trade-offs:**
- PostgreSQL setup more complex than Firebase
- Benefit: Full control, no vendor lock-in
- Cost: Must manage ourselves

## Security Approach
- bcrypt password hashing (cost factor: 12)
- 15-minute password reset tokens
- 5 failed login attempts = 30 min lockout
...
```

**Why good spec compounds knowledge:**
- Future developers understand requirements
- Rationale for PostgreSQL is clear
- Trade-offs are documented
- Specific numbers provide context
- Can evaluate if assumptions still hold

---

## Maintenance and Evolution

### Updating Specs

**When to update:**
- Requirements change materially
- Architecture evolves significantly
- Major decisions need documentation

**How to update:**
- Create new commit with changes
- Document WHY the change in commit message
- Consider creating new spec if major pivot

**Git preserves history:**
- Can see original decisions
- Can see why they changed
- Evolution is visible

### Archiving Old Specs

**Don't delete—they're history:**
- Old specs show evolution
- Decisions made sense at the time
- Context for "why we changed"

**If feature removed:**
- Add note at top of spec:
  ```markdown
  # ⚠️ DEPRECATED: This feature was removed in Month X
  
  See: [reason for removal]
  ```

---

## Long-Term Value

### For Individual Developers

- **Understand context**: Never wonder "why did they do this?"
- **Make informed decisions**: Refactor with full context
- **Learn from history**: See what worked, what didn't
- **Preserve knowledge**: Your decisions documented forever

### For Teams

- **Onboard faster**: Read specs to understand system
- **Consistent understanding**: Everyone has same context
- **Avoid repeated mistakes**: Learn from documented decisions
- **Institutional memory**: Knowledge survives turnover

### For Organizations

- **Architectural consistency**: Decisions build on each other
- **Reduced technical debt**: Changes respect original intent
- **Knowledge asset**: Project history is accessible
- **Sustainable growth**: Scale without losing context

---

## Best Practices

### Do

✅ Document major features with specs
✅ Capture requirements and rationale
✅ Explain alternatives and trade-offs
✅ Be specific with numbers and constraints
✅ Commit specs to git (preserve history)
✅ Read specs before refactoring
✅ Update specs when decisions change

### Don't

❌ Create specs for trivial features
❌ Write vague, generic specs
❌ Skip rationale and trade-offs
❌ Let specs diverge from reality
❌ Delete old specs (archive instead)
❌ Expect specs to be discovered automatically (that's what standards are for)

---

## Next Steps

**Learn to Create Specs:**
- **[Your First Project](../tutorials/your-first-praxis-os-project)** - Includes spec creation
- **[Understanding Workflows](../tutorials/understanding-praxis-os-workflows)** - Spec execution

**Understand the Full Picture:**
- **[Knowledge Compounding](./knowledge-compounding)** - Overview of both mechanisms
- **[Standards Compounding](./standards-knowledge-compounding)** - How standards work

**See Related Concepts:**
- **[Workflows Reference](../reference/workflows)** - Spec creation and execution workflows

---

## Related Documentation

- **[Knowledge Compounding](./knowledge-compounding)** - Overview of both mechanisms
- **[Standards Compounding](./standards-knowledge-compounding)** - Pattern discovery
- **[Your First Project](../tutorials/your-first-praxis-os-project)** - Includes spec creation
- **[Understanding Workflows](../tutorials/understanding-praxis-os-workflows)** - How specs are used

