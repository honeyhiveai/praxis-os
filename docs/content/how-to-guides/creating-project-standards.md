---
sidebar_position: 7
doc_type: how-to
---

# Creating Project Standards

This guide covers everything you need to know about creating project-specific standards that make prAxIs OS smarter about your codebase over time.

**You'll learn:**
- When to create a standard vs when not to
- The collaborative process (human + AI)
- How AI queries to ensure quality
- RAG optimization for discoverability
- Testing and maintaining standards
- Common pitfalls and how to avoid them

---

## Quick Start

**Fastest path to creating a standard:**

1. **Recognize the pattern** (you've used it 2-3+ times)
2. **Tell AI**: "Let's create a standard for [pattern]"
3. **AI queries heavily** (learns structure, RAG optimization)
4. **AI creates the standard** (properly formatted, discoverable)
5. **Verify via search** (confirm AI can find it)
6. **Use it immediately** (next task benefits automatically)

**Time:** 5-10 minutes per standard

---

## When to Create a Standard

### ✅ Good Candidates

**Patterns (Used 2-3+ Times):**
- Error handling formats
- Naming conventions
- Code organization patterns
- Testing strategies
- Integration approaches

**Example:**
```python
# Used 3 times → Should be standardized
try:
    result = api_call()
except APIError as e:
    return {"error_code": e.code, "message": str(e)}
```

**Conventions (Need Consistency):**
- API response formats
- Database naming rules
- File organization
- Import ordering
- Comment styles

**Example:**
```python
# All files follow this → Should be standardized
from typing import ...
from datetime import ...

from third_party import ...

from our_project import ...
```

**Decisions (Worth Codifying):**
- Architectural principles
- Technology choices
- Performance requirements
- Security practices

**Example:**
> "All services communicate via event bus, never direct calls" → Document why and how

**"Future AI Should Know This":**
- Project-specific quirks
- Domain conventions
- Integration patterns
- Optimization techniques

---

### ❌ Not Good Candidates

**One-Time Implementations:**
```python
❌ Don't document:
def calculate_specific_report():
    # This is run once for a specific feature
    # Not a reusable pattern
```

**Feature Designs:**
```markdown
❌ Don't create standard for:
"User Authentication System Design"
→ This belongs in a spec, not a standard
```

**Code Documentation:**
```python
❌ Don't create standard for:
"""
This function processes payments.
Args: ...
Returns: ...
"""
→ This belongs in docstrings, not standards
```

**Already in Universal Standards:**
```markdown
❌ Don't recreate:
"SOLID Principles" or "Test Pyramid"
→ Already in `.agent-os/standards/universal/`
```

**High-Level Overview:**
```markdown
❌ Don't document:
"Project Overview" or "Getting Started"
→ This belongs in README.md
```

---

## The Collaborative Process

### Step 1: Human Identifies (Strategic Decision)

**You recognize a pattern:**
- "We've handled pagination the same way three times"
- "This error format should be our standard"
- "We should document this integration pattern"

**You tell AI:**

**Option A - Direct Request:**
> "Create a standard for our API pagination pattern"

**Option B - Outline the Pattern:**
> "We use cursor-based pagination with `next_token` and `page_size`. Let's create a standard for this."

**Option C - Ask for Suggestion:**
> "I've implemented this pattern three times. Should we create a standard?"

**Key:** Human makes the strategic decision to document.

---

### Step 2: AI Queries Heavily (Learning Phase)

AI doesn't just write immediately. It queries to learn the proper approach:

#### Query 1: Standard Structure

```python
search_standards("how to create standards structure required sections")
```

**AI learns:**
- Purpose section (why it exists)
- Problem section (what without it)
- Standard section (actual rules)
- Checklist section (validation)
- Examples section (real code)
- Anti-patterns section (avoid these)

#### Query 2: RAG Optimization

```python
search_standards("RAG content optimization keywords discoverability")
```

**AI learns:**
- TL;DR section at top
- Keywords for search
- Natural language headers
- Query hooks (questions answered)
- Content-specific phrases

#### Query 3: Query Construction

```python
search_standards("query construction patterns semantic search")
```

**AI learns:**
- How future queries will be phrased
- What keywords to include
- Phrase patterns that match searches

#### Query 4: Domain-Specific (If Needed)

```python
search_standards("API design best practices")
# or
search_standards("database patterns")
# or
search_standards("testing strategies")
```

**AI learns:**
- Universal patterns in this domain
- Best practices to reference
- Common anti-patterns

**Why Heavy Querying Matters:**
- Ensures consistent structure
- Optimizes for discoverability
- Follows meta-standards (standards about standards)
- Creates standards AI can find

---

### Step 3: AI Creates the Standard (Writing Phase)

AI writes the markdown file following learned patterns:

**File location:** `.agent-os/standards/development/[topic].md`

**Structure:**

```markdown
# [Topic] Standard

**Keywords for search**: [relevant, keywords, for, discovery]

---

## 🎯 TL;DR - [Topic] Quick Reference

[3-5 sentence summary with core principle and key points]

**Key Rules:**
- [Rule 1]
- [Rule 2]
- [Rule 3]

**Example:**
[Quick code example]

---

## 🎯 Purpose

[2-3 sentences explaining why this standard exists]

**Questions This Answers:**
- [Question 1]
- [Question 2]
- [Question 3]

---

## ⚠️ The Problem Without This Standard

[Explain what happens without this standard, with examples]

---

## ✅ The Standard

[Detailed rules, patterns, conventions]

[Code examples]

[Implementation guidance]

---

## 📋 Checklist

Before merging code:
- [ ] [Check 1]
- [ ] [Check 2]
- [ ] [Check 3]

---

## ❌ Anti-Patterns

[Common mistakes with examples]

---

## 🧪 Testing (If Applicable)

[How to verify compliance]

---

**Version:** 1.0.0
**Created:** [Date]
**Last Updated:** [Date]
**Next Review:** [When to review]
```

---

## RAG Optimization Details

### Keywords Section

**Purpose:** Help AI discover via semantic search

**Include:**
- Primary terms (API, error handling, pagination)
- Synonyms (exception handling, error responses)
- Related concepts (validation, exceptions, status codes)
- Natural phrases (how to handle errors)

**Example:**
```markdown
**Keywords for search**: API errors, error handling, error responses, 
exception handling, error format, validation errors, API exceptions, 
error codes, structured errors, consistent error format
```

### TL;DR Section

**Purpose:** High-density, keyword-rich summary

**Include:**
- Core principle (1 sentence)
- Key rules (bullet points)
- Quick example (code snippet)

**Why:** RAG often returns TL;DR sections in top results—maximize information density.

### Questions This Answers

**Purpose:** Match how AI will query

**Include 5-7 natural questions:**
- "How do I [do X]?"
- "What is the pattern for [Y]?"
- "When should I [Z]?"

**Example:**
```markdown
**Questions This Answers:**
- How should I format API error responses?
- What fields are required in error objects?
- How do I handle validation vs business logic errors?
- What error codes should I use?
- How do I test error handling?
```

**Why:** AI queries with questions—make them match.

### Natural Language Headers

**Use descriptive headers:**
```markdown
✅ "How to Handle Validation Errors"
✅ "Required Fields in Error Responses"

❌ "Usage"
❌ "Examples"
❌ "Notes"
```

**Why:** RAG indexes by section—specific headers improve discovery.

---

## Verification Steps

### 1. File Created

Verify the file exists:
```bash
ls .agent-os/standards/development/[your-standard].md
```

### 2. RAG Indexed

Wait 5-10 seconds for file watcher to re-index.

### 3. Test Discovery

Ask AI to search:

**You:** "Search for our [topic] standards"

**AI queries:**
```python
search_standards("[topic] patterns")
```

**Success:** Your standard appears in top 3 results ✅

**Problem:** Not in results → Improve keywords/content

### 4. Test Application

Create a task that should use the standard:

**You:** "Create a new [feature] that uses [pattern]"

**AI should:**
1. Query standards before implementing
2. Discover your standard
3. Follow your pattern automatically

**Verify:** Check if AI followed your documented approach.

---

## Common Patterns

### API Standards

**Common topics:**
- Error responses
- Pagination
- Filtering/sorting
- Authentication
- Rate limiting
- Versioning

**Example:**
```markdown
# API Pagination Standard

Always use cursor-based pagination with:
- `next_token`: String for next page
- `page_size`: Integer (default 50, max 500)
- `has_more`: Boolean indicating more pages

Example response:
{
  "data": [...],
  "pagination": {
    "next_token": "abc123",
    "page_size": 50,
    "has_more": true
  }
}
```

### Database Standards

**Common topics:**
- Naming conventions (tables, columns, indexes)
- Migration patterns
- Query patterns
- Transaction handling

**Example:**
```markdown
# Database Naming Standard

Tables: snake_case plural (users, order_items)
Columns: snake_case (first_name, created_at)
Indexes: idx_{table}_{column}_{column}
Foreign keys: fk_{table}_{ref_table}
```

### Testing Standards

**Common topics:**
- Test organization
- Naming patterns
- Fixture usage
- Mock strategies

**Example:**
```markdown
# Test Organization Standard

Structure:
tests/
  unit/           # Pure logic, no I/O
  integration/    # External services
  e2e/            # Full system tests

Naming: test_{feature}_{scenario}_{expected}
Example: test_user_login_invalid_password_raises_error
```

### Code Organization Standards

**Common topics:**
- File structure
- Import ordering
- Module organization
- Naming conventions

---

## Maintaining Standards

### When to Update

**Update standards when:**
- Pattern evolves (better approach discovered)
- New edge cases identified
- Technology changes
- Team feedback suggests improvements

**Don't update for:**
- Minor wording tweaks (unless clarity improves)
- Personal preferences
- One-off exceptions

### Version Control

Include version info in standard:

```markdown
**Version:** 2.0.0
**Created:** 2025-10-01
**Last Updated:** 2025-10-12
**Changes:** Added async error handling patterns
**Next Review:** 2026-01-12 or when async patterns change
```

### Review Cycle

**Quarterly reviews:**
- Are standards still being followed?
- Do they need updates based on new learnings?
- Are they discoverable (test with queries)?
- Any standards that should be archived?

### Archiving Old Standards

Don't delete—archive:

```bash
mv .agent-os/standards/development/old-pattern.md \
   .agent-os/standards/development/archived/old-pattern.md
```

Add note in archived file:
```markdown
# ⚠️ ARCHIVED: Old Pattern Standard

**Archived:** 2025-10-12
**Reason:** Replaced by new-pattern.md
**See:** ../new-pattern.md
```

---

## Common Pitfalls

### 1. Too Vague

**Problem:**
```markdown
❌ "Write good error handling"
```

**Solution:**
```markdown
✅ "All API errors must return JSON with error_code (string) 
    and message (string) fields. Example: 
    {\"error_code\": \"VALIDATION_ERROR\", \"message\": \"Invalid email\"}"
```

**Fix:** Be specific and actionable.

### 2. Missing Examples

**Problem:**
```markdown
❌ Standard has rules but no code examples
```

**Solution:**
```markdown
✅ Include real code from your project showing the pattern in action
```

**Fix:** Every rule needs an example.

### 3. Poor Discoverability

**Problem:**
```markdown
❌ Generic headers: "Usage", "Examples"
❌ No keywords
❌ No TL;DR
```

**Solution:**
```markdown
✅ Keywords: "API error handling, error responses, exception handling"
✅ TL;DR: High-density summary
✅ Headers: "How to Handle Validation Errors"
```

**Fix:** Query `search_standards("RAG optimization")` to learn patterns.

### 4. Over-Documentation

**Problem:**
```markdown
❌ Creating standards for everything
❌ Documenting one-time implementations
```

**Solution:**
```markdown
✅ Only document patterns used 2-3+ times
✅ Ask: "Will future AI benefit from this?"
```

**Fix:** Be selective—quality over quantity.

### 5. Not Testing Discovery

**Problem:**
```markdown
❌ Created standard but didn't verify AI can find it
```

**Solution:**
```markdown
✅ Test: search_standards("topic")
✅ Verify: Appears in top 3 results
✅ Improve: Add keywords if not found
```

**Fix:** Always test discoverability.

---

## Troubleshooting

### "AI can't find my standard"

**Check:**
1. Has RAG re-indexed? (wait 10 seconds)
2. Does standard have keywords?
3. Does query match content?

**Fix:**
- Add more keywords at top
- Include TL;DR with core terms
- Add "Questions This Answers" section
- Use natural language in headers

### "Standard not being followed"

**Check:**
1. Did AI query before implementing?
2. Was standard in top 3 search results?
3. Does standard have clear examples?

**Fix:**
- Improve discoverability (more keywords)
- Add clearer examples
- Include checklist for validation
- Ask AI: "Did you check our [topic] standards?"

### "Too many standards, hard to maintain"

**Solution:**
- Archive outdated ones
- Consolidate related standards
- Focus on high-value patterns
- Review quarterly

### "Standard conflicts with universal standard"

**Resolution:**
- Project standards override universal for project-specific needs
- Document WHY your project differs
- Reference universal standard with explanation

**Example:**
```markdown
# Our Exception Handling (Different from Universal)

**Note:** We deviate from universal exception handling patterns
because our API serves mobile clients with limited connectivity.

**Why:** Mobile clients need structured errors for offline handling.

**Universal pattern:** Standard HTTP exceptions
**Our pattern:** Structured JSON with error codes

[Details...]
```

---

## Advanced Topics

### Multi-File Standards

For complex topics, organize as:

```
.agent-os/standards/development/
  authentication/
    _index.md          # Overview with links
    jwt-patterns.md    # JWT specifics
    session-mgmt.md    # Session specifics
    oauth-flow.md      # OAuth specifics
```

`_index.md` includes keywords for all sub-topics and links to detailed files.

### Domain-Specific Standards

Organize by domain:

```
.agent-os/standards/development/
  api/
    error-handling.md
    pagination.md
    versioning.md
  database/
    naming.md
    migrations.md
  testing/
    unit-tests.md
    integration-tests.md
```

Each with full keywords for discoverability.

### Team Standards

For team coordination:

```markdown
# Code Review Standard

**Purpose:** Consistent code review process

**Required Checks:**
- [ ] All tests passing
- [ ] Linter clean
- [ ] Documentation updated
- [ ] Breaking changes noted

**Review Timeline:** 24 hours maximum
```

---

## Best Practices

### Do

✅ Document patterns used 2-3+ times
✅ Query heavily when creating (learn structure/optimization)
✅ Include rich keywords and TL;DR
✅ Add real code examples from your project
✅ Test discoverability via search
✅ Update based on learnings
✅ Review quarterly

### Don't

❌ Document everything (over-documentation)
❌ Skip the TL;DR section
❌ Use vague language
❌ Create without querying meta-standards
❌ Forget to verify discoverability
❌ Let standards go stale
❌ Delete old standards (archive instead)

---

## Examples by Category

### API Standard Example

See [Tutorial: Your First Project Standard](../tutorials/your-first-project-standard) for complete API error handling example.

### Database Standard Example

```markdown
# Database Migration Standard

**Keywords**: database migrations, schema changes, alembic, migration scripts

## TL;DR
All migrations must be reversible with up() and down(). Test both 
directions before merging.

## The Standard
1. Always include rollback logic
2. Test locally: up → down → up
3. Name: YYYY_MM_DD_HHMM_description.py
4. Never modify data and schema in same migration
...
```

### Testing Standard Example

```markdown
# Unit Test Standard

**Keywords**: unit testing, test structure, test naming, pytest

## TL;DR
Unit tests follow AAA pattern (Arrange, Act, Assert). Name tests:
test_{feature}_{scenario}_{expected}

## The Standard
...
```

---

## Next Steps

**Start Creating:**
- Identify your most common pattern
- Tell AI: "Let's create a standard for [pattern]"
- Follow this guide
- Test discoverability
- Use it immediately

**Learn More:**
- [Tutorial: Your First Project Standard](../tutorials/your-first-project-standard) - Hands-on walkthrough
- [Knowledge Compounding](../explanation/knowledge-compounding) - Why this works
- [Standards Reference](../reference/standards) - Browse existing standards

**Remember:** Every standard makes the next 10 tasks better. Start small, compound over time.

---

## Related Documentation

- **[Your First Project Standard](../tutorials/your-first-project-standard)** - Hands-on tutorial
- **[Knowledge Compounding](../explanation/knowledge-compounding)** - The concept explained
- **[Standards Reference](../reference/standards)** - Universal and project standards
- **[Understanding Workflows](../tutorials/understanding-agent-os-workflows)** - Related to specs

