# RAG Content Optimization Guide for Future Authors

**Purpose:** Comprehensive guide for creating and maintaining RAG-optimized content in prAxIs OS  
**Date:** 2025-10-11  
**Status:** Gold Standard Template

---

## 🎯 Quick Start

**When creating new prAxIs OS content:**
1. ✅ Use the RAG Optimization Template (Section 2)
2. ✅ Follow the 7-component structure
3. ✅ Write query-oriented headers
4. ✅ Test with 5-10 natural language queries
5. ✅ Validate search results

**Expected Time:** 30-60 minutes per document (depending on complexity)

---

## 📋 The RAG Optimization Template

### Component 1: TL;DR Section (MANDATORY)

**Purpose:** Front-loaded summary for immediate value and discoverability

**Structure:**
```markdown
## 🎯 TL;DR - [Topic] Quick Reference

**Keywords for search**: [10-15 relevant search terms, comma-separated]

**Core Principle:** [One sentence stating the fundamental principle]

**[Section Name]:**
[3-7 key points, bullets or numbered list]

**[Another Section Name]:**
[More critical information]

**When to query this standard:**
- [Situation] → `search_standards("[example query]")`
- [Another situation] → `search_standards("[example query]")`

**For complete guide with examples, continue reading below.**

---
```

**Example (from solid-principles.md):**
```markdown
## 🚨 SOLID Quick Reference (TL;DR)

**Keywords for search**: SOLID principles, class design, maintainable code, object-oriented design, single responsibility, open closed principle, liskov substitution, interface segregation, dependency inversion, dependency injection, testable code, how to design classes

**Critical information:**

1. **Single Responsibility (SRP)** - One class, one reason to change. Each class does one thing well.
2. **Open/Closed (OCP)** - Open for extension, closed for modification. Add features without changing existing code.
3. **Liskov Substitution (LSP)** - Subtypes must be substitutable for their base types. Child classes work anywhere parent does.
4. **Interface Segregation (ISP)** - Many small interfaces > one large interface. Don't force clients to depend on unused methods.
5. **Dependency Inversion (DIP)** - Depend on abstractions, not concretions. High-level modules shouldn't depend on low-level details.

**When to query this standard:**
- Designing new classes → `search_standards("how to design maintainable classes")`
- Code review feedback about coupling → `search_standards("reducing code coupling")`
- Making code testable → `search_standards("dependency injection pattern")`

**For complete guide with examples, continue reading below.**
```

**Best Practices:**
- ✅ Put TL;DR FIRST (after title/intro)
- ✅ Include 10-15 keywords (actual search terms users will use)
- ✅ Keep it scannable (bullets, short paragraphs)
- ✅ Provide immediate value (user can stop reading here if needed)
- ✅ Use "Keywords for search" field explicitly
- ❌ Don't make it too long (target: 1-2 screen scrolls)
- ❌ Don't use jargon without explanation

---

### Component 2: "Questions This Answers" Section (MANDATORY)

**Purpose:** Explicit list of natural language queries the content answers

**Structure:**
```markdown
## ❓ Questions This Answers

1. "[First natural question]"
2. "[Second natural question]"
3. "[Third natural question]"
...
10. "[Tenth natural question]"

---
```

**Example (from production-code-checklist.md):**
```markdown
## ❓ Questions This Answers

1. "What should I check before committing code?"
2. "How do I ensure my code is production-ready?"
3. "What are the quality standards for AI-written code?"
4. "How do I handle configuration in prAxIs OS?"
5. "When do I need concurrency analysis?"
6. "How should I handle failures gracefully?"
7. "What documentation is required for production code?"
8. "What testing is required before committing?"

---
```

**Best Practices:**
- ✅ Write as actual user questions (how people search)
- ✅ Cover main topics AND edge cases
- ✅ Include failure scenarios ("What happens if X fails?")
- ✅ Use natural language, not technical jargon
- ✅ 8-12 questions (enough for coverage, not overwhelming)
- ❌ Don't use yes/no questions (prefer "how", "what", "when")
- ❌ Don't duplicate TL;DR keywords verbatim

---

### Component 3: Query-Oriented Headers (MANDATORY)

**Purpose:** Make headers searchable and discoverable

**Pattern:**
```markdown
## [Question or Clear Action Statement]

[1-2 sentence context paragraph explaining WHY this matters]

[Content...]
```

**Examples:**

**❌ BAD (Not Query-Oriented):**
```markdown
## Single Responsibility Principle

**Definition:** A class should have one, and only one, reason to change.
```

**✅ GOOD (Query-Oriented):**
```markdown
## How to Apply Single Responsibility Principle

A class should have one, and only one, reason to change. This keeps classes focused and makes them easier to test, understand, and maintain.

**Definition:** One class, one reason to change.
```

**More Examples:**
- "What Git Operations Are STRICTLY FORBIDDEN?" (not "Forbidden Operations")
- "How to Detect Race Conditions?" (not "Detection")
- "What Are Good Performance Targets?" (not "Performance Targets")
- "How to Verify .gitignore Is Working?" (not "Verification")

**Best Practices:**
- ✅ Phrase as questions ("How to...", "What is...", "When to...")
- ✅ Use action statements ("Apply X", "Implement Y")
- ✅ Add context paragraph immediately after header
- ✅ Match how users naturally query
- ❌ Don't use jargon without explanation
- ❌ Don't use abbreviations in headers

---

### Component 4: Context Paragraphs (MANDATORY)

**Purpose:** Provide immediate value and context after every major header

**Pattern:**
```markdown
## [Query-Oriented Header]

[1-2 sentence paragraph explaining WHY this section matters or WHAT it covers]

[Main content...]
```

**Example (from test-pyramid.md):**
```markdown
## Why the Pyramid Shape Matters

Understanding each layer's purpose and characteristics helps you structure your test suite correctly.

[Content about pyramid ratios...]
```

**Best Practices:**
- ✅ Keep it brief (1-2 sentences max)
- ✅ Explain WHY before diving into HOW
- ✅ Connect to user's goal or pain point
- ✅ Use clear, simple language
- ❌ Don't repeat the header verbatim
- ❌ Don't start with definitions (start with value)

---

### Component 5: "When to Query This Standard" Section (HIGHLY RECOMMENDED)

**Purpose:** Situational discovery guide

**Structure:**
```markdown
## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **[Situation 1]** | `search_standards("[example query]")` |
| **[Situation 2]** | `search_standards("[example query]")` |
| **[Situation 3]** | `search_standards("[example query]")` |
...

---
```

**Example (from git-safety-rules.md):**
```markdown
## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Git operations** | `search_standards("git safety rules")` |
| **Revert changes** | `search_standards("how to revert file changes")` |
| **Forbidden commands** | `search_standards("forbidden git commands")` |
| **git reset** | `search_standards("can AI use git reset")` |
| **git push force** | `search_standards("git push force")` |
| **Safe git operations** | `search_standards("safe git operations")` |

---
```

**Best Practices:**
- ✅ Use table format for clarity
- ✅ Bold situation names
- ✅ Include actual query examples in backticks
- ✅ Cover 5-8 common situations
- ✅ Include both obvious AND edge case situations
- ❌ Don't be generic ("When you need X" - too vague)
- ❌ Don't duplicate TL;DR queries

---

### Component 6: Cross-References Section (HIGHLY RECOMMENDED)

**Purpose:** Guide multi-document discovery

**Structure:**
```markdown
## 🔗 Related Standards

**Query workflow for [topic]:**

1. **Start with [this]** → `search_standards("[query]")` (this document)
2. **Learn [next topic]** → `search_standards("[query]")` → `path/to/file.md`
3. **Understand [related]** → `search_standards("[query]")` → `path/to/file.md`
4. **[Final step]** → `search_standards("[query]")` → `path/to/file.md`

**By Category:**

**[Category 1]:**
- `path/to/file1.md` - Brief description → `search_standards("[query]")`
- `path/to/file2.md` - Brief description → `search_standards("[query]")`

**[Category 2]:**
- `path/to/file3.md` - Brief description → `search_standards("[query]")`
- `path/to/file4.md` - Brief description → `search_standards("[query]")`

---
```

**Example (from solid-principles.md):**
```markdown
## 🔗 Related Standards

**Query workflow for SOLID principles:**

1. **Start with SOLID** → `search_standards("how to design maintainable classes")` (this document)
2. **Apply to architecture** → `search_standards("API design principles")` → `standards/architecture/api-design-principles.md`
3. **Learn testing** → `search_standards("how to test SOLID code")` → `standards/testing/test-doubles.md`
4. **Ensure production quality** → `search_standards("production code checklist")` → `standards/ai-safety/production-code-checklist.md`

**By Category:**

**Architecture:**
- `standards/architecture/dependency-injection.md` - Implementing DIP in practice → `search_standards("dependency injection pattern")`
- `standards/architecture/separation-of-concerns.md` - Layered architecture principles → `search_standards("separation of concerns")`

**Testing:**
- `standards/testing/test-doubles.md` - Testing with mocks and stubs → `search_standards("test doubles")`
- `standards/testing/integration-testing.md` - Integration test patterns → `search_standards("integration testing")`

---
```

**Best Practices:**
- ✅ Provide sequential "query workflow" for learning path
- ✅ Group by category
- ✅ Include file paths AND query examples
- ✅ Brief description of each reference
- ✅ 5-10 related standards (enough for context, not overwhelming)
- ❌ Don't just list file names (provide value/context)
- ❌ Don't link to unrelated content

---

### Component 7: Keywords for Search (MANDATORY)

**Purpose:** Explicit SEO boost for critical queries

**Location:** Inside TL;DR section

**Format:**
```markdown
**Keywords for search**: keyword1, keyword2, keyword3, ...
```

**How to Choose Keywords:**
1. ✅ Think like a user: "What would I search for?"
2. ✅ Include the topic name and variations
3. ✅ Include problem statements ("how to fix X", "avoid Y")
4. ✅ Include related concepts
5. ✅ Include common misspellings or variations
6. ✅ 10-15 keywords total

**Example (from race-conditions.md):**
```markdown
**Keywords for search**: race conditions, race condition bugs, concurrent bugs, data races, threading issues, shared state problems, concurrent access, synchronization, thread safety, how to detect race conditions, prevent race conditions
```

**Best Practices:**
- ✅ Use actual search phrases, not just single words
- ✅ Include long-tail queries ("how to detect race conditions")
- ✅ Think about failure scenarios ("threading issues", "concurrent bugs")
- ✅ Include variations (plural/singular, abbreviations)
- ❌ Don't keyword stuff (keep it natural)
- ❌ Don't use obscure technical jargon

---

## ✅ Optimization Checklist

Use this checklist when creating or optimizing content:

### Structure
- [ ] TL;DR section is FIRST (after intro)
- [ ] "Questions This Answers" section is SECOND
- [ ] All major headers are query-oriented
- [ ] Each major header has 1-2 sentence context paragraph
- [ ] "When to Query This Standard" section included
- [ ] "Cross-References" section included

### TL;DR Quality
- [ ] Includes "Keywords for search" field with 10-15 terms
- [ ] States core principle clearly
- [ ] Provides immediate value (user can stop reading here)
- [ ] Includes 3-7 key points
- [ ] Scannable (bullets, short paragraphs)
- [ ] Ends with "For complete guide, continue reading below"

### Discoverability
- [ ] Headers phrased as questions or actions
- [ ] Context paragraphs explain WHY
- [ ] Keywords match natural search queries
- [ ] "Questions This Answers" covers main use cases
- [ ] Cross-references provide clear navigation

### Testing
- [ ] Tested with 5-10 natural language queries
- [ ] File ranks in top 3 for key queries
- [ ] TL;DR ranks highly for overview queries
- [ ] Specific sections rank for detailed queries

---

## 🧪 Testing Your Content

**After creating/optimizing content, run these tests:**

### Test 1: Overview Query
```python
search_standards("[topic] guide")
# Expected: Your file's TL;DR should rank #1-3
```

### Test 2: Specific Question Queries
```python
search_standards("how to [specific action from your content]")
# Expected: Relevant section from your file ranks #1-3
```

### Test 3: Problem/Failure Query
```python
search_standards("why [common problem your content addresses]")
# Expected: Your file ranks #1-3 with relevant section
```

### Test 4: Natural Language Query
```python
search_standards("[one of your 'Questions This Answers' verbatim]")
# Expected: Your "Questions This Answers" section ranks #1
```

### Test 5: Edge Case Query
```python
search_standards("[uncommon but important use case you cover]")
# Expected: Your file ranks in top 5
```

**Validation Criteria:**
- ✅ **80%+ queries successful** (4/5 or 5/5 rank in top 3)
- ✅ **At least one TL;DR hit** (proves front-loading works)
- ✅ **Specific sections discoverable** (proves header optimization works)

**If tests fail:**
1. Improve keywords in TL;DR
2. Rephrase headers to match queries
3. Add more questions to "Questions This Answers"
4. Strengthen context paragraphs

---

## 🎨 Patterns Catalog

### Pattern 1: The "Wrong vs Right" Pattern
**Use When:** Teaching correct behavior through contrast

**Structure:**
```markdown
❌ **Wrong:**
```[language]
// Anti-pattern code
```

✅ **Right:**
```[language]
// Correct code
```

**Why:** [Explanation of why right approach is better]
```

**Example:** Used extensively in `solid-principles.md`, `ai-agent-quickstart.md`

---

### Pattern 2: The "3 Laws" or "N Principles" Pattern
**Use When:** Summarizing fundamental rules

**Structure:**
```markdown
**The [N] Laws of [Topic]:**

1. **[First Law]** - [Brief explanation]
2. **[Second Law]** - [Brief explanation]
3. **[Third Law]** - [Brief explanation]
```

**Example:** Used in `optimization-patterns.md` (The 3 Laws of Performance Optimization)

---

### Pattern 3: The "Real-World Incident" Pattern
**Use When:** Demonstrating consequences of violation

**Structure:**
```markdown
## What Happens When [Rule] Is Violated? (Real Incident)

**What Happened:**
[Describe the incident]

**Impact:**
- [Consequence 1]
- [Consequence 2]
- [Consequence 3]

**Prevention Time:**
[How long proper approach would have taken vs debugging time]
```

**Example:** Used in `import-verification-rules.md`, `git-safety-rules.md`

---

### Pattern 4: The "Decision Matrix" or "Comparison Table" Pattern
**Use When:** Helping users choose between options

**Structure:**
```markdown
| Option | Use When | Pros | Cons | Performance |
|--------|----------|------|------|-------------|
| Option A | [Situation] | [Pros] | [Cons] | [Metric] |
| Option B | [Situation] | [Pros] | [Cons] | [Metric] |
```

**Example:** Used in `locking-strategies.md`, `retry-strategies.md`

---

### Pattern 5: The "Checklist" Pattern
**Use When:** Providing actionable validation steps

**Structure:**
```markdown
**Before [action], check:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]
```

**Example:** Used in `production-code-checklist.md`, `gitignore-requirements.md`

---

## 🚫 Common Anti-Patterns to Avoid

### Anti-Pattern 1: Keyword Stuffing
**Wrong:**
```markdown
## Testing Guide Testing Guide Test Guide Testing

Testing guide for testing tests to test testing framework testing...
```

**Right:**
Use keywords naturally in context, not repetitively.

---

### Anti-Pattern 2: Jargon-Heavy Headers
**Wrong:**
```markdown
## SRP Implementation via DI
```

**Right:**
```markdown
## How to Apply Single Responsibility Principle with Dependency Injection
```

---

### Anti-Pattern 3: No Context Paragraphs
**Wrong:**
```markdown
## How to Use Mutex

[Immediately dives into code example]
```

**Right:**
```markdown
## How to Use Mutex

A mutex (mutual exclusion lock) ensures only one thread accesses shared state at a time, preventing race conditions.

[Code example]
```

---

### Anti-Pattern 4: Generic "When to Query"
**Wrong:**
```markdown
| **When you need it** | `search_standards("this standard")` |
```

**Right:**
```markdown
| **Git operations** | `search_standards("git safety rules")` |
| **Revert changes** | `search_standards("how to revert file changes")` |
```

---

### Anti-Pattern 5: Missing TL;DR
**Wrong:**
```markdown
# My Standard

[Immediately dives into detailed content]
```

**Right:**
```markdown
# My Standard

## 🎯 TL;DR - My Standard Quick Reference

[Quick summary with keywords, core principle, key points]

---

[Detailed content follows]
```

---

## 📏 Scoring Rubric

**Use this rubric to evaluate content quality:**

| Criteria | Points | How to Measure |
|----------|--------|----------------|
| **TL;DR Section** | 2 points | Has TL;DR with keywords, core principle, key points |
| **Questions This Answers** | 1 point | Has 8-12 natural language questions |
| **Query-Oriented Headers** | 2 points | 80%+ headers phrased as questions/actions |
| **Context Paragraphs** | 1 point | Major headers have 1-2 sentence context |
| **When to Query Section** | 1 point | Has situational guide with example queries |
| **Cross-References** | 1 point | Has query workflow and categorized references |
| **Query Test Success** | 2 points | 80%+ test queries rank file in top 3 |

**Scoring:**
- **9-10 points:** Excellent (gold standard)
- **7-8 points:** Good (meets requirements)
- **5-6 points:** Acceptable (needs improvement)
- **<5 points:** Poor (requires optimization)

**Target:** All content should score ≥7/10

---

## 🔄 Maintenance Guidelines

### When to Update Content
1. **New related standard added** → Update cross-references
2. **Common query failing** → Add to "Questions This Answers", improve keywords
3. **User feedback** → Adjust TL;DR or headers
4. **Quarterly review** → Re-test queries, update stale examples

### How to Update
1. Read current content
2. Run 5-10 test queries
3. Identify gaps or failures
4. Apply optimization template to gaps
5. Re-test queries
6. Update cross-references in related files

---

## 📚 Examples of Excellent Optimization

Study these files as gold standards:

1. **`solid-principles.md`** - Comprehensive TL;DR, excellent query-oriented headers, clear wrong/right examples
2. **`test-pyramid.md`** - Great use of tables, clear ratios, strong keywords
3. **`production-code-checklist.md`** - "The 5-Second Rule" TL;DR, excellent checklist pattern
4. **`import-verification-rules.md`** - Real-world incident pattern, "2-Minute Rule" framing
5. **`git-safety-rules.md`** - Strong forbidden/safe contrast, excellent situational guide

---

## 🎓 Final Checklist for New Content

Before publishing new prAxIs OS content:

- [ ] TL;DR section is FIRST and complete
- [ ] Keywords field has 10-15 relevant search terms
- [ ] "Questions This Answers" has 8-12 natural questions
- [ ] All major headers are query-oriented
- [ ] Context paragraphs present after major headers
- [ ] "When to Query This Standard" section included
- [ ] Cross-references provided with queries
- [ ] Tested with 5-10 natural language queries
- [ ] 80%+ test queries successful (top 3 ranking)
- [ ] File scores ≥7/10 on rubric
- [ ] Related files' cross-references updated

---

**This guide ensures all prAxIs OS content maintains the high discoverability standards established by the RAG Content Optimization project.**

**Questions? Search:** `search_standards("RAG content optimization")`

