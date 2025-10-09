# Compliance Checking Protocol

**Universal standard for ensuring AI assistants check existing standards before taking action**

---

## 📋 Overview

### What is Compliance Checking?

**Compliance checking** is the mandatory practice of reviewing existing standards, patterns, and project rules BEFORE generating code, running tests, or making changes.

### Why It Matters

Without compliance checking, AI assistants:
- ❌ Reinvent solutions that already exist
- ❌ Violate established patterns and conventions
- ❌ Miss safety rules and critical requirements
- ❌ Create inconsistent implementations

With compliance checking, AI assistants:
- ✅ Follow established patterns
- ✅ Avoid recreating existing solutions
- ✅ Respect safety rules
- ✅ Maintain consistency across codebase

### When to Check Compliance

**ALWAYS** - At the start of every task, before generating any code or making any changes.

---

## 🚨 Mandatory: Pre-Task Compliance Checklist

**Execute this checklist at the start of EVERY task.**

### Before Any Code Generation

- [ ] **Read relevant Agent OS standards** in `.agent-os/standards/`
  - Universal standards in `.agent-os/standards/universal/`
  - AI assistant standards in `.agent-os/standards/ai-assistant/`
  - AI safety rules in `.agent-os/standards/ai-safety/` (if exists)
  - Project-specific standards in `.agent-os/standards/development/`

- [ ] **Check project-specific rules** in project documentation
  - README.md (project overview, setup instructions)
  - CONTRIBUTING.md (contribution guidelines)
  - .cursorrules (Agent OS behavioral triggers)
  - Any domain-specific documentation

- [ ] **Verify established patterns** in existing codebase
  - Search for similar implementations
  - Check existing class/module structures
  - Review import conventions
  - Understand architecture patterns

- [ ] **Confirm no existing solutions** before creating new
  - Search for existing functionality
  - Check if similar code already exists
  - Verify this isn't reinventing the wheel

- [ ] **Review recent commits** for context
  - Last 5-10 commits
  - Recent changes to related files
  - Ongoing work that might conflict

---

### Before Any Test Execution

- [ ] **Check project's test execution standards**
  - `.agent-os/standards/development/testing-standards.md` (if exists)
  - `.agent-os/standards/universal/testing/` (universal test patterns)

- [ ] **Verify test runner configuration**
  - Project's build system (tox.ini, package.json, Cargo.toml, pom.xml)
  - Test framework configuration
  - Coverage requirements

- [ ] **Use established test commands** (not manual alternatives)
  - Project should define these in `.agent-os/standards/development/validation-commands.md`
  - Never run tests manually if project has established commands
  - Follow project's CI/CD patterns

- [ ] **Follow project-specific test patterns**
  - Test file organization
  - Naming conventions
  - Mocking/stubbing patterns

---

## 🔍 Compliance Verification Process

**A systematic 3-step process to discover and follow standards.**

### Step 1: Standards Discovery

**Goal**: Find all relevant standards for your task

**Universal Commands** (adapt for your project's search tools):

```bash
# Find standards related to your task
find .agent-os/standards -name "*.md" | grep -i [topic]

# Find critical/mandatory rules
grep -r "CRITICAL\|MANDATORY\|NEVER" .agent-os/standards/

# Check universal standards
ls .agent-os/standards/universal/

# Check AI assistant standards
ls .agent-os/standards/ai-assistant/

# Check project-specific standards
ls .agent-os/standards/development/

# Check project-specific rules in root docs
grep -i [topic] README.md CONTRIBUTING.md .cursorrules
```

**MCP Alternative** (if MCP tools available):

```
Use semantic search to find relevant standards:
"What are the [topic] best practices?"
"How should I handle [scenario]?"
```

---

### Step 2: Pattern Confirmation

**Goal**: Understand existing implementations and patterns

**Universal Commands** (adapt for your project's tools):

```bash
# Find existing patterns in codebase
[search_tool] "[pattern]" [source_directory]

# Examples for different tools:
# - grep -r "pattern" src/
# - rg "pattern" src/
# - codebase_search(query="pattern", target_directories=["src"])

# Review recent related changes
git log --oneline --grep=[topic] | head -10

# Find similar implementations
[search_tool] "[class_name]" [source_directory]
[search_tool] "[function_signature]" [source_directory]

# Check import patterns
[search_tool] "^import" [source_directory] | head -20
[search_tool] "^from .* import" [source_directory] | head -20
```

**Examples by Language**:

```bash
# Python
grep -r "class.*Tracer" src/
grep -r "def.*process" src/
grep -r "from project import" src/

# JavaScript/TypeScript
grep -r "export class" src/
grep -r "export function" src/
grep -r "import.*from" src/

# Go
grep -r "^type.*struct" .
grep -r "^func" .
grep -r "^package" .

# Rust
grep -r "^pub struct" src/
grep -r "^pub fn" src/
grep -r "^use " src/
```

---

### Step 3: Compliance Decision

**Goal**: Decide how to proceed based on findings

**Decision Matrix**:

```
Existing Standard Found?
├─ YES → Follow it exactly
│   ├─ Standard is adequate? → Proceed with standard
│   └─ Standard is inadequate? → Propose improvement to human (don't deviate)
│
└─ NO existing standard
    ├─ Pattern exists in codebase?
    │   ├─ YES → Extract pattern, follow it, propose documenting as standard
    │   └─ NO → Check universal standards
    │       ├─ Universal standard applies? → Follow universal guidance
    │       └─ No universal guidance? → Propose approach to human, document decision
```

**Examples**:

**Scenario 1: Standard Exists**
```
Task: Run unit tests
Found: .agent-os/standards/development/testing-standards.md says "Use tox -e unit"
Decision: ✅ Run `tox -e unit` (follow standard)
```

**Scenario 2: Pattern Exists, No Standard**
```
Task: Create new API endpoint
Found: 10 existing endpoints in src/api/ following RESTful pattern
Decision: ✅ Follow existing RESTful pattern, suggest documenting as standard
```

**Scenario 3: No Standard or Pattern**
```
Task: Implement caching
Found: No existing caching, no caching standard
Decision: ✅ Check universal standards for caching patterns, propose approach to human
```

---

## 🚫 Common Compliance Failures

**Learn from these common mistakes.**

### ❌ Failure 1: Ignoring Test Execution Standards

**Symptom**: Running tests manually instead of using project's test runner

**Example**:
```bash
❌ WRONG: pytest tests/ --cov
✅ CORRECT: tox -e unit  # (or project's defined command)

❌ WRONG: npm test -- --coverage
✅ CORRECT: npm run test:ci  # (if project defines this)

❌ WRONG: cargo test
✅ CORRECT: cargo test --all-features  # (if project requires this)
```

**Why It Fails**:
- Bypasses project's test configuration
- Misses environment setup (virtualenv, dependencies)
- Incorrect coverage reporting
- Violates CI/CD expectations

**Prevention**:
1. Check `.agent-os/standards/development/testing-standards.md` or `validation-commands.md`
2. Look for test configuration files (tox.ini, pytest.ini, jest.config.js)
3. Check project's CI/CD configuration (.github/workflows/, .gitlab-ci.yml)
4. Ask user: "What's the correct command to run tests?"

---

### ❌ Failure 2: Recreating Existing Solutions

**Symptom**: Implementing functionality that already exists

**Example**:
```python
# AI implements new logging utility
❌ WRONG: Creating src/utils/logger.py when src/logging/logger.py already exists

# AI creates new validation function  
❌ WRONG: def validate_email(email): ...
          when utils.validation.validate_email() already exists
```

**Why It Fails**:
- Duplicates code (maintenance burden)
- Inconsistent implementations
- Misses existing tests and documentation
- Violates DRY principle

**Prevention**:
1. Search codebase for similar functionality BEFORE implementing
2. Check existing modules and utilities
3. Review imports in existing files (what are they using?)
4. Ask: "Does this functionality already exist?"

---

### ❌ Failure 3: Violating Safety Rules

**Symptom**: Performing dangerous operations without checking safety rules

**Examples**:
```bash
❌ WRONG: git push --force origin main
✅ CORRECT: Check git safety rules first - force push to main usually forbidden

❌ WRONG: Writing API keys to .env file  
✅ CORRECT: Check credential safety rules - never write credentials

❌ WRONG: Using hardcoded date "2025-10-09"
✅ CORRECT: Check date usage policy - always get current date dynamically
```

**Why It Fails**:
- Data loss (force push)
- Security violations (credential exposure)
- Incorrect behavior (hardcoded dates)

**Prevention**:
1. Always check `.agent-os/standards/ai-safety/` before dangerous operations
2. Review git safety rules before git operations
3. Check credential protection rules before writing config files
4. Verify date usage policy before using dates

---

### ❌ Failure 4: Skipping Architecture Patterns

**Symptom**: Not following established architecture patterns

**Examples**:
```python
# Project uses dependency injection
❌ WRONG: config = load_config()  # Direct instantiation
✅ CORRECT: def __init__(self, config: Config):  # Injected dependency

# Project uses factory pattern
❌ WRONG: tracer = Tracer(config)  # Direct instantiation
✅ CORRECT: tracer = TracerFactory.create(config)  # Factory

# Project uses repository pattern
❌ WRONG: db.execute("SELECT * FROM users")  # Direct database access
✅ CORRECT: user_repository.find_all()  # Repository abstraction
```

**Why It Fails**:
- Inconsistent with existing code
- Breaks architecture assumptions
- Harder to test
- Violates project conventions

**Prevention**:
1. Check `.agent-os/standards/universal/architecture/` for patterns
2. Review existing code structure
3. Look for factories, builders, repositories in codebase
4. Follow "do what the Romans do" principle

---

## 📊 Compliance Scoring

**Measure your compliance systematically.**

### Score Calculation

```
Compliance Score = (Standards Followed / Total Applicable Standards) × 100%
```

### Interpretation

| Score | Status | Meaning | Action |
|-------|--------|---------|--------|
| **100%** | ✅ Perfect | All standards followed | Excellent - maintain this |
| **80-99%** | ✅ Good | Minor deviations with justification | Document deviations, improve |
| **60-79%** | ⚠️ Moderate | Significant gaps | Review and address gaps |
| **<60%** | ❌ Poor | Major violations | Stop, review standards, restart |

### Example Scoring

**Task**: Create new API endpoint

**Applicable Standards**:
1. ✅ API design patterns (followed - used RESTful)
2. ✅ Error handling (followed - used project's error middleware)
3. ✅ Authentication (followed - used existing auth decorator)
4. ❌ Input validation (missed - didn't use project's validator)
5. ✅ Documentation (followed - added OpenAPI docstring)

**Score**: 4/5 = 80% (Good compliance)

**Action**: Add input validation to reach 100%

---

## 📝 Compliance Reporting Template

**Use this template to report compliance at task start.**

```markdown
## Compliance Check: [Task Name]

### Standards Reviewed

**Universal Standards**:
- [ ] `.agent-os/standards/universal/[relevant-category]/` - [Brief summary]
- [ ] `.agent-os/standards/ai-assistant/` - [Brief summary]
- [ ] `.agent-os/standards/ai-safety/` - [Brief summary if applicable]

**Project-Specific Standards**:
- [ ] `.agent-os/standards/development/[standard].md` - [Brief summary]
- [ ] Project documentation (README, CONTRIBUTING) - [Brief summary]

### Patterns Found

**Existing Implementations**:
- [File/Class/Function] - [Pattern description]
- [File/Class/Function] - [Pattern description]

**Import Conventions**:
- [Import pattern description]

**Architecture Patterns**:
- [Pattern description]

### Compliance Decision

**Approach**: [Following existing | New pattern | Hybrid]

**Justification**: [Why this approach is appropriate]

**Compliance Score**: [0-100]%

**Standards Followed**:
1. [Standard name] - [How followed]
2. [Standard name] - [How followed]

**Deviations (if any)**:
- [Deviation description] - [Justification]

### Next Steps

- [Action item 1]
- [Action item 2]
```

---

## 🎯 Project-Specific Compliance

**Projects should create project-specific compliance rules.**

### Creating Compliance Addendum

**File**: `.agent-os/standards/development/compliance-addendum.md`

**Contents**:
- Project-specific mandatory rules
- Technology-specific compliance checks
- Tool-specific verification commands
- Project conventions and patterns

### Example Compliance Addendum

```markdown
# Project Name - Compliance Addendum

## Mandatory Rules

### Test Execution
❌ NEVER: Run `pytest` directly
✅ ALWAYS: Use `tox -e unit` or `tox -e integration`

### Code Quality
❌ NEVER: Commit with MyPy errors
✅ ALWAYS: Achieve zero MyPy errors before commit

### Git Safety
❌ NEVER: Force push to main/master
✅ ALWAYS: Use feature branches

## Verification Commands

### Check if module exists
```bash
grep -r "class ClassName" src/
```

### Verify import path
```bash
python -c "from project.module import Class"
```

## Project Conventions

### File Organization
- Production code: `src/`
- Tests: `tests/unit/` or `tests/integration/`
- Configuration: `config/`

### Naming Conventions
- snake_case for functions and variables
- PascalCase for classes
- UPPER_CASE for constants
```

---

## ✅ Compliance Success Patterns

**Examples of good compliance checking in practice.**

### Success Pattern 1: New Feature Implementation

```markdown
Task: Add rate limiting to API

Compliance Check:
1. ✅ Searched .agent-os/standards/ for "rate limit" - found concurrency patterns
2. ✅ Searched codebase for existing rate limiting - none found
3. ✅ Checked universal/failure-modes/ for throttling patterns - found circuit breaker
4. ✅ Reviewed API architecture - found middleware pattern in use
5. ✅ Checked project conventions - found Redis used for caching

Decision: Implement rate limiter as middleware (follows existing pattern), using Redis (follows existing tools), with circuit breaker (follows universal patterns)

Result: Implementation consistent with codebase, uses established tools, follows universal patterns
```

### Success Pattern 2: Bug Fix

```markdown
Task: Fix race condition in tracer

Compliance Check:
1. ✅ Searched .agent-os/standards/universal/concurrency/ - found locking strategies
2. ✅ Reviewed existing tracer code - found existing use of threading.Lock
3. ✅ Checked if project has concurrency standards - found in development/concurrency.md
4. ✅ Verified project uses thread-safe patterns - yes, consistently uses locks

Decision: Use threading.Lock (existing pattern), follow project's lock acquisition order (project standard)

Result: Fix consistent with existing concurrency approach, follows project patterns
```

---

## 🎓 Teaching Compliance to New AI Assistants

**If you're training or onboarding new AI assistants:**

### Key Points to Emphasize

1. **"Check first, then act"** - Never generate code without checking standards
2. **"When in doubt, search it out"** - If unsure, search for existing patterns
3. **"Standards exist for a reason"** - Don't deviate without justification
4. **"Consistency > cleverness"** - Follow existing patterns even if you know a "better" way

### Training Exercises

**Exercise 1**: Given a task, identify all applicable standards
**Exercise 2**: Search codebase for existing patterns before implementing
**Exercise 3**: Identify compliance violations in sample code
**Exercise 4**: Create compliance report for a task

---

## 🔗 Related Standards

- **[Pre-Generation Validation](pre-generation-validation.md)** - What to validate before generating code
- **[Commit Protocol](commit-protocol.md)** - How to review and commit changes
- **[Analysis Methodology](analysis-methodology.md)** - How to conduct comprehensive analysis

---

## ❓ FAQ

### Q: What if compliance checking takes too long?

**A**: Compliance checking typically takes 30-90 seconds but prevents hours of rework. It's always worth it.

### Q: What if standards conflict?

**A**: Priority order: AI Safety > Project-Specific > Universal. Ask human for clarification.

### Q: What if no standards exist for my task?

**A**: Check universal standards first, then propose approach to human, then document decision for future.

### Q: Can I skip compliance if the task is small?

**A**: No. Even small tasks should check for existing solutions and patterns. It takes 30 seconds.

---

**This is a universal standard. It applies to all projects using Agent OS Enhanced, regardless of programming language or technology stack.**

**For project-specific compliance rules, see `.agent-os/standards/development/compliance-addendum.md` in your project.**

