# Skeleton vs Consumer Project Boundaries
## What Belongs in prAxIs OS Skeleton vs What Projects Define

**Date**: October 9, 2025  
**Core Question**: Where does the paradigm end and project-specific implementation begin?

---

## 🎯 Guiding Principles

### Principle 1: Paradigm vs Implementation
```
Skeleton: "HOW to think and work" (workflows, patterns, principles)
Consumer: "WHAT to use" (tools, technologies, languages)
```

### Principle 2: Universal vs Context-Specific
```
Skeleton: Works for Python, JavaScript, Rust, Go, Java, etc.
Consumer: "We use Python with pytest, black, mypy"
```

### Principle 3: Framework vs Configuration
```
Skeleton: The structure and process
Consumer: The values and specifics
```

### Principle 4: Teaching vs Prescribing
```
Skeleton: "Here's how to validate, here's why"
Consumer: "Run this exact command with these flags"
```

---

## 📦 Distribution Strategy

### Tier 1: SKELETON (Universal - Copy to Every Project)
**Location**: `universal/standards/` → copied to `.praxis-os/standards/`

**Contents**: Language-agnostic paradigm that applies to ALL projects

### Tier 2: TEMPLATES (Reference - Adapt as Needed)
**Location**: `universal/examples/` → referenced, not copied

**Contents**: Language-specific examples showing how to implement the paradigm

### Tier 3: CONSUMER (Project-Specific - Created by Project)
**Location**: Project's `.praxis-os/standards/development/`

**Contents**: Project's specific implementation of the paradigm

---

## 🗂️ Detailed Breakdown by Standard

### Gap 1: AI Assistant Entry Point & Navigation

#### IN SKELETON ✅ (90% universal)

**File**: `universal/ai-assistant/README.md` → `.praxis-os/standards/ai-assistant/README.md`

**Content**:
```markdown
# AI Assistant Standards - Start Here

## 🚨 CRITICAL: Start Here

**EVERY AI assistant interaction MUST begin with compliance checking:**

1. 📋 [Compliance Protocol](compliance-protocol.md) - MANDATORY first step
2. 🎯 [Pre-Generation Validation](pre-generation-validation.md) - Before generating code
3. 📝 [Commit Protocol](commit-protocol.md) - Before committing
4. ⚡ [Quick Reference](quick-reference.md) - Fast lookups (if project provides)

## 📊 Standards Priority Order

### 🚨 Critical (Must Follow)
1. **Compliance Protocol** - Always check existing standards first
2. **Safety Rules** - Credential protection, git safety
3. **Pre-Generation Validation** - Validate before generating
4. **Quality Framework** - Meet all quality requirements

### ⚡ Important (Should Follow)
1. **Code Generation Patterns** - Follow established patterns
2. **Error Pattern Recognition** - Systematic debugging
3. **Documentation Standards** - Proper documentation

### 📋 Helpful (Good to Follow)
1. **Quick References** - Fast pattern lookups
2. **Best Practices** - Language-specific guidance

## 🎯 Universal Workflow

```
User Request
    ↓
Pre-Task Validation (ONCE)
    ├─ Check standards first
    ├─ Verify clean starting state
    ├─ Understand full scope
    └─ Get current date
    ↓
Task Execution (PER FILE/CHANGE)
    ├─ Pre-generation validation
    ├─ Generate code/changes
    └─ Maintain state awareness
    ↓
Pre-Commit Validation (ONCE)
    ├─ Run quality gates
    ├─ Review changes
    └─ Get user approval
```

## 🔗 Project-Specific Extensions

Projects may add:
- Language-specific code generation frameworks
- Tool-specific quick references
- Project coding standards
- Technology-specific patterns

See your project's `.praxis-os/standards/development/` for project-specific standards.

---

**This is a universal standard. Language/tool-specific implementations should be in your project's `.praxis-os/standards/development/` directory.**
```

**Why in Skeleton**:
- Entry point navigation is universal
- Workflow structure (compliance → task → validation) is paradigm-level
- Priority ordering is universal concept
- Works for any language/tool

**What's Parameterized**:
- Link to project-specific standards directory
- "Projects may add..." section acknowledges project-specific extensions

#### CONSUMER DEFINES ⚙️

**File**: `.praxis-os/standards/development/README.md` (Project creates)

**Content**:
```markdown
# [Project Name] Development Standards

## Technology Stack
- Language: Python 3.11+
- Testing: pytest + tox
- Linting: pylint (≥8.0/10.0 target)
- Type checking: mypy (zero errors mandatory)
- Formatting: black + isort
- Documentation: Docusaurus

## Project-Specific Standards
1. [Code Quality Standards](code-quality.md)
2. [Testing Standards](testing-standards.md)
3. [API Design Patterns](api-design.md)
4. [Project Architecture](architecture.md)

## Tool-Specific Quick References
- [Python Quick Reference](python-quick-reference.md)
- [Pytest Patterns](pytest-patterns.md)
- [Common Error Patterns](python-error-patterns.md)
```

---

### Gap 2: Compliance Checking Protocol

#### IN SKELETON ✅ (95% universal)

**File**: `universal/ai-assistant/compliance-protocol.md` → `.praxis-os/standards/ai-assistant/compliance-protocol.md`

**Content**:
```markdown
# Compliance Checking Protocol

## Overview

**MANDATORY**: Every AI assistant task MUST begin with compliance checking.

**Why**: Prevents reinventing solutions, violating standards, missing established patterns.

---

## Pre-Task Compliance Checklist

### Before Any Code Generation
- [ ] Read relevant prAxIs OS standards in `.praxis-os/standards/`
- [ ] Check project-specific rules (README, .cursorrules, contribution docs)
- [ ] Verify established patterns in existing codebase
- [ ] Confirm no existing solutions before creating new ones
- [ ] Review recent commits for context

### Before Any Test Execution
- [ ] Check project's test execution standards
- [ ] Verify test runner configuration
- [ ] Use established test commands (not manual alternatives)
- [ ] Follow project-specific test patterns

---

## Compliance Verification Process

### Step 1: Standards Discovery

**Universal Commands** (adapt for your project):
```bash
# Find standards related to your task
find .praxis-os/standards -name "*.md" | grep -i [topic]

# Find critical/mandatory rules
grep -r "CRITICAL\|MANDATORY\|NEVER" .praxis-os/standards/

# Check project-specific rules
grep -i [topic] README.md CONTRIBUTING.md .cursorrules
```

### Step 2: Pattern Confirmation

**Universal Commands** (adapt for your project):
```bash
# Find existing patterns in codebase
[search_tool] "[pattern]" [source_directory]

# Review recent related changes
git log --oneline --grep=[topic] | head -10

# Find similar implementations
[search_tool] "[class_name]" [source_directory]
```

### Step 3: Compliance Decision

**Decision Matrix**:
```
Existing Standard Found?
├─ YES → Follow it (don't reinvent)
│   └─ If inadequate → Propose improvement to human
└─ NO → Check if pattern exists
    ├─ YES → Extract pattern, propose standard
    └─ NO → Proceed with best practices
```

---

## Common Compliance Failures

### ❌ Failure 1: Ignoring Test Execution Standards

**Symptom**: Running tests manually instead of using project's test runner

**Example**:
```bash
❌ WRONG: pytest tests/ --cov
✅ CORRECT: [use project's test command from standards]
```

**Prevention**: Check `.praxis-os/standards/testing/` before running tests

---

### ❌ Failure 2: Recreating Existing Solutions

**Symptom**: Implementing functionality that already exists

**Prevention**: 
1. Search codebase for existing implementations
2. Check standards for established patterns
3. Review recent commits for related work

---

### ❌ Failure 3: Violating Safety Rules

**Symptom**: Performing dangerous operations (force push, credential writes)

**Prevention**:
1. Check `.praxis-os/standards/ai-safety/` for safety rules
2. Never skip without explicit human approval
3. Follow git safety protocols

---

## Compliance Scoring

### Score Calculation

```
Compliance Score = (Followed Standards / Total Applicable Standards) × 100%
```

### Interpretation

- **100%**: Perfect compliance - all standards followed
- **80-99%**: Good compliance - minor deviations with justification
- **60-79%**: Moderate compliance - significant gaps
- **<60%**: Poor compliance - major standards violations

---

## Compliance Reporting Template

```markdown
## Compliance Check: [Task Name]

### Standards Reviewed
- [ ] `.praxis-os/standards/ai-assistant/` - AI workflows
- [ ] `.praxis-os/standards/ai-safety/` - Safety rules
- [ ] `.praxis-os/standards/development/` - Project standards
- [ ] Project documentation (README, CONTRIBUTING)

### Patterns Found
- [List existing patterns found in codebase]

### Compliance Decision
- **Approach**: [Following existing | New pattern | Hybrid]
- **Justification**: [Why this approach]
- **Score**: [0-100]%

### Deviations (if any)
- [List with justifications]
```

---

## Project-Specific Compliance

Projects should create `.praxis-os/standards/development/compliance-addendum.md` with:
- Project-specific mandatory rules
- Technology-specific compliance checks
- Tool-specific verification commands
- Project conventions and patterns

---

**This is a universal standard. Project-specific compliance rules should be in `.praxis-os/standards/development/`.**
```

**Why in Skeleton**:
- "Check standards first" is core paradigm
- Verification process is universal
- Decision matrix applies to any project
- Compliance scoring is universal concept

**What's Parameterized**:
- [search_tool] placeholder for grep/rg/codebase_search
- [source_directory] placeholder for project paths
- "Project-specific compliance" section points to project standards

#### CONSUMER DEFINES ⚙️

**File**: `.praxis-os/standards/development/compliance-addendum.md` (Project creates)

**Content**:
```markdown
# prAxIs OS - Compliance Addendum

## Project-Specific Mandatory Rules

### Test Execution
❌ NEVER: Run `pytest` directly
✅ ALWAYS: Use `tox -e unit` or `tox -e integration`

### Code Quality
❌ NEVER: Commit with MyPy errors
✅ ALWAYS: Achieve zero MyPy errors before commit

### Git Safety
❌ NEVER: Force push to main/master
✅ ALWAYS: Use feature branches

## Technology-Specific Checks

### Python Import Verification
```bash
# Check if module exists
grep -r "class ClassName" mcp_server/

# Verify import path
python -c "from mcp_server.module import Class"
```

### Tox Environment Verification
```bash
# List available tox environments
tox -l

# Verify tox.ini configuration
cat tox.ini | grep -A10 "\[testenv"
```

## Project Conventions

### File Organization
- Production code: `mcp_server/`
- Tests: `tests/unit/` or `tests/integration/`
- Scripts: `scripts/`
- Documentation: `docs/`

### Naming Conventions
- Snake_case for functions and variables
- PascalCase for classes
- UPPER_CASE for constants
```

---

### Gap 3: Pre-Generation Validation Protocols

#### IN SKELETON ✅ (75% universal - WITH FIX!)

**File**: `universal/ai-assistant/pre-generation-validation.md` → `.praxis-os/standards/ai-assistant/pre-generation-validation.md`

**Content**:
```markdown
# Pre-Generation Validation Protocols

## Overview

**Purpose**: Ensure AI has current, accurate understanding before generating code.

**Timing**: Three distinct validation checkpoints with different requirements.

---

## Three Validation Checkpoints

```
User Request → AI Work → Commit
     ↓           ↓         ↓
  Pre-Task   Pre-Gen   Pre-Commit
   (Once)    (Per File)  (Once)
```

---

## Checkpoint 1: Pre-Task Validation

**When**: Once at the start of each user request

**Purpose**: Establish safe, known starting point

### Validation Steps

```bash
# 1. Get current date (prevents hardcoded dates)
CURRENT_DATE=$(date +"%Y-%m-%d")
echo "Today is: $CURRENT_DATE"

# 2. Verify correct branch
git branch --show-current

# 3. Check starting state (should be clean at task start)
git status --porcelain
# If not clean: Warn user, ask if they want to proceed

# 4. Verify development environment
[verify_dev_environment_active]
[verify_language_version]

# 5. Review recent history (for awareness)
git log --oneline -5
```

### Checklist
- [ ] Current date: Retrieved and stored
- [ ] Correct branch: Verified
- [ ] Starting state: Checked (clean preferred)
- [ ] Environment: Active and correct
- [ ] Recent history: Reviewed

**Clean State Requirement**: ✅ PREFERRED (warn if not, proceed if user approves)

---

## Checkpoint 2: Pre-Generation Validation

**When**: Before generating EACH file or code change

**Purpose**: Ensure current understanding before each generation

**CRITICAL**: This provides AWARENESS, not BLOCKING. Multi-file tasks require uncommitted changes after the first file.

### Validation Steps

```bash
# 1. Use current date from pre-task variable
# $CURRENT_DATE already set

# 2. Verify current codebase understanding
read_file [entry_point_file]              # Check current API structure
[search] "[class_pattern]" [source_dir]   # Verify current class names
[search] "[import_pattern]" [examples_dir] # Check import conventions
[search] "[type_pattern]" [source_dir]    # Verify type usage patterns

# 3. State awareness (NOT blocking!)
git status --porcelain
# Purpose: Know what's uncommitted, understand task progress
# NOT REQUIRED: Clean state (would block multi-file generation)

# 4. Verify still on correct branch
git branch --show-current
# Purpose: Prevent accidental branch switch during task
```

### Checklist
- [ ] API structure: Current understanding verified
- [ ] Class/module names: Confirmed current names
- [ ] Import patterns: Verified correct conventions
- [ ] Type patterns: Confirmed current usage
- [ ] State awareness: Know what's uncommitted (NOT blocking)
- [ ] Correct branch: Still on intended branch

**Clean State Requirement**: ❌ NOT REQUIRED (would block multi-file generation)

**Key Principle**: Be AWARE of state, don't BLOCK on state

---

## Checkpoint 3: Pre-Commit Validation

**When**: Once before committing all changes

**Purpose**: Ensure quality and completeness

### Validation Steps

```bash
# 1. Verify committing from correct branch
git branch --show-current

# 2. Review what's being committed
git status --porcelang

# 3. Run quality gates (ALL must pass)
[format_command]              # Code formatting
[lint_command]                # Static analysis
[type_check_command]          # Type checking
[unit_test_command]           # Unit tests
[integration_test_command]    # Integration tests (if applicable)

# 4. Verify documentation (if applicable)
[doc_build_command]           # Documentation builds without warnings
```

### Checklist
- [ ] Correct branch: Verified
- [ ] Changes reviewed: Appropriate scope
- [ ] Formatting: 100% compliant
- [ ] Static analysis: Meets threshold
- [ ] Type checking: Zero errors
- [ ] Unit tests: 100% pass
- [ ] Integration tests: 100% pass (if applicable)
- [ ] Documentation: Builds successfully

**Clean State Requirement**: N/A (state will be dirty, about to commit)

---

## Example: Multi-File Task Flow

### Scenario: "Create tracer module with 3 files"

```bash
# ============================================================
# PRE-TASK VALIDATION (Once at start)
# ============================================================
CURRENT_DATE=$(date +"%Y-%m-%d")
git branch --show-current  # feature/new-tracer
git status --porcelain     # (clean)
✅ Safe starting point established

# ============================================================
# Generate File 1: src/tracer.py
# ============================================================

# PRE-GENERATION VALIDATION (Before file 1)
git status --porcelain           # (clean - first file)
✅ Aware of state

read_file [entry_point]          # Check current API
✅ Current understanding verified

# Generate file 1
[write file 1]

# ============================================================
# Generate File 2: src/tracer_config.py
# ============================================================

# PRE-GENERATION VALIDATION (Before file 2)
git status --porcelain           # ?? src/tracer.py
✅ AWARE: File 1 uncommitted (expected in multi-file task)
✅ NOT BLOCKING: Proceed with file 2

git branch --show-current        # feature/new-tracer
✅ Still on correct branch

# Generate file 2
[write file 2]

# ============================================================
# Generate File 3: tests/test_tracer.py
# ============================================================

# PRE-GENERATION VALIDATION (Before file 3)
git status --porcelain           # ?? src/tracer.py, src/tracer_config.py
✅ AWARE: Files 1-2 uncommitted (expected)
✅ NOT BLOCKING: Proceed with file 3

read_file src/tracer.py          # Understand implementation for testing
✅ Current understanding verified

# Generate file 3
[write file 3]

# ============================================================
# PRE-COMMIT VALIDATION (Before committing all 3 files)
# ============================================================

# Run quality gates
[format_command]    # ✅ All 3 files formatted
[lint_command]      # ✅ All 3 files pass
[type_check_command] # ✅ All 3 files type-safe
[unit_test_command] # ✅ All tests pass

# Review and commit
git add [files]
git commit -m "feat: add tracer module with configuration"
```

**Result**: ✅ Multi-file task completed with proper validation

---

## Context-Specific Validation

### For Test Fixing Tasks

**Additional validation**:
```bash
# Understand production code before fixing tests
read_file [production_module]
[search] "def method_name" [source_dir]
[search] "class ClassName" [source_dir]
```

### For API Changes

**Additional validation**:
```bash
# Check current API consumers
[search] "from module import" [examples_dir]
[search] "import module" [test_dir]
# Understand impact before changing
```

### For Configuration Changes

**Additional validation**:
```bash
# Check configuration usage patterns
[search] "config\." [source_dir]
[search] "Config\(" [source_dir]
# Ensure consistency
```

---

## Project-Specific Validation

Projects should define in `.praxis-os/standards/development/validation-commands.md`:
- Exact commands to run for each validation step
- Language-specific validation procedures
- Tool-specific verification commands
- Project-specific checklist items

---

**This is a universal standard. Project-specific validation commands should be in `.praxis-os/standards/development/validation-commands.md`.**
```

**Why in Skeleton**:
- Three-checkpoint validation is paradigm-level
- Clean state logic (task: yes, generation: no, commit: n/a) is universal
- Multi-file awareness principle is universal
- Validation categories apply to any language

**What's Parameterized**:
- [verify_dev_environment_active] - project defines (venv/nvm/rbenv)
- [search], [read_file] - project tools
- [format_command], [lint_command], etc. - project tools
- Points to project-specific validation-commands.md

#### CONSUMER DEFINES ⚙️

**File**: `.praxis-os/standards/development/validation-commands.md` (Project creates)

**Content**:
```markdown
# prAxIs OS - Validation Commands

## Environment Validation

### Python Virtual Environment
```bash
# Verify venv active
which python
# Expected: /Users/josh/src/github.com/honeyhiveai/praxis-os/.venv/bin/python

# Verify Python version
python --version
# Expected: Python 3.11+
```

### Current Date
```bash
CURRENT_DATE=$(date +"%Y-%m-%d")
echo "Today is: $CURRENT_DATE"
```

## Codebase Understanding

### API Structure
```bash
# Check MCP server entry point
read_file mcp_server/__init__.py

# Check available tools
grep -r "def.*_tool" mcp_server/server/tools/
```

### Import Patterns
```bash
# Check how modules are imported
grep -r "from mcp_server" mcp_server/ | head -20

# Verify import style
grep -r "^import" mcp_server/ | head -20
```

## Quality Gates

### Format Check
```bash
tox -e format
# Must pass - zero tolerance for formatting issues
```

### Lint Check
```bash
tox -e lint
# Target: Pylint ≥8.0/10.0
# Current: See output for score
```

### Type Check
```bash
tox -e type
# MANDATORY: Zero MyPy errors
# Must pass - no exceptions
```

### Unit Tests
```bash
tox -e unit
# Must pass 100%
```

### Integration Tests
```bash
tox -e integration
# Must pass 100%
```

## Documentation Build

### Docusaurus Build
```bash
cd docs
npm run build
cd ..
# Must build without errors
# Warnings acceptable (review if relevant)
```
```

---

### Gaps 4-7: Quick Reference, Error Patterns, Quality Procedures, Commit Protocols

#### DECISION: Templates/Examples (Not in Skeleton)

**Reasoning**: These are 60-70% universal but heavily tool-specific

**Strategy**: Provide templates, projects adapt

#### IN TEMPLATES 📝

**Location**: `universal/examples/python/` (reference only, not copied)

**Files**:
- `python-quick-reference-template.md`
- `python-error-patterns-template.md`
- `python-quality-procedures-template.md`
- `python-commit-protocols-template.md`

**Content**: Full Python examples showing how to implement the paradigm

**Other Languages**: `universal/examples/javascript/`, `universal/examples/rust/`, etc.

#### CONSUMER CREATES ⚙️

**Location**: `.praxis-os/standards/development/` (project-specific)

**Files**:
- `quick-reference.md` - Project's quick reference cards
- `error-patterns.md` - Project's common error patterns
- `quality-procedures.md` - Project's quality gate procedures
- `commit-protocols.md` - Project's commit workflow

**Process**:
1. Start with template from `universal/examples/[language]/`
2. Adapt for project's tools and conventions
3. Refine based on project experience

---

## 📊 Summary: Distribution Strategy

### Universal Standards (In Skeleton - Copy to All Projects)

**Location**: `universal/ai-assistant/` → `.praxis-os/standards/ai-assistant/`

**Percentage Universal**: 85-95%

**Files to Include**:
1. ✅ `README.md` - Entry point and navigation (90% universal)
2. ✅ `compliance-protocol.md` - Check standards first (95% universal)
3. ✅ `pre-generation-validation.md` - Three-checkpoint validation (75% universal, WITH FIX)
4. ✅ `analysis-methodology.md` - Already created (100% universal)
5. ✅ `commit-protocol.md` - Review and CHANGELOG workflow (90% universal)

**Total**: 5 core universal standards

---

### Templates/Examples (Reference - Not Copied)

**Location**: `universal/examples/[language]/`

**Percentage Universal**: 60-70% structure, 30-40% content

**Files to Provide**:
1. 📝 `python-quick-reference-template.md`
2. 📝 `python-error-patterns-template.md`
3. 📝 `python-quality-procedures-template.md`
4. 📝 `javascript-quick-reference-template.md` (future)
5. 📝 `rust-quick-reference-template.md` (future)

**Purpose**: Show how to implement paradigm for specific language/tools

---

### Consumer Project Standards (Project Creates)

**Location**: `.praxis-os/standards/development/`

**Files Projects Create**:
1. ⚙️ `README.md` - Project overview and tech stack
2. ⚙️ `compliance-addendum.md` - Project-specific rules
3. ⚙️ `validation-commands.md` - Exact commands for validation
4. ⚙️ `code-quality.md` - Project quality standards
5. ⚙️ `quick-reference.md` - Project quick reference (adapted from template)
6. ⚙️ `error-patterns.md` - Project error patterns (adapted from template)
7. ⚙️ `quality-procedures.md` - Project quality procedures (adapted from template)

**Purpose**: Project-specific implementation of the paradigm

---

## 🎯 The Balance

### What Makes Something "Skeleton-Worthy"

**Include in Skeleton if**:
- ✅ 80%+ language-agnostic
- ✅ Core to the paradigm (compliance, validation, workflow)
- ✅ Teaches "how to think" not "what to use"
- ✅ Applies to any technology stack
- ✅ Provides structure with placeholders for specifics

**Keep as Template if**:
- 📝 60-79% language-agnostic
- 📝 Heavily tool-specific content
- 📝 Shows "what to use" for specific language
- 📝 Needs significant adaptation per project
- 📝 Language/framework-specific patterns

**Consumer Defines if**:
- ⚙️ <60% universal (mostly project-specific)
- ⚙️ Exact commands and tool names
- ⚙️ Project conventions and patterns
- ⚙️ Technology choices and configurations
- ⚙️ Team-specific workflows

---

## 📝 Implementation for prAxIs OS

### As the Skeleton Project

**prAxIs OS should have**:

1. **Universal standards** (85-95% universal)
   - Location: `universal/ai-assistant/`
   - These get COPIED to consumer projects' `.praxis-os/standards/ai-assistant/`

2. **Templates/Examples** (60-70% universal)
   - Location: `universal/examples/python/`
   - These are REFERENCED, not copied
   - Show how prAxIs OS implements the paradigm

3. **Local project standards** (project-specific)
   - Location: `.praxis-os/standards/development/`
   - prAxIs OS's own implementation
   - Serves as example for other projects

### As a Consumer Project

**When someone installs prAxIs OS, they get**:

1. **Universal standards copied** to their `.praxis-os/standards/ai-assistant/`
   - Paradigm-level guidance
   - Works for their language/tools

2. **Templates available** in `universal/examples/[language]/`
   - Can reference to see implementations
   - Adapt for their project

3. **Create their own** `.praxis-os/standards/development/`
   - Their project's specifics
   - Their tool choices
   - Their conventions

---

## 🔄 The Authorship vs Consumption Distinction

### When Working ON prAxIs OS (Authorship Mode)

**You CAN**:
- Read universal standards directly from `universal/`
- Edit universal standards
- Create new universal standards
- Update templates

### When Using prAxIs OS (Consumption Mode)

**You SHOULD**:
- Read standards from `.praxis-os/standards/` (copied from universal)
- Create project-specific standards in `.praxis-os/standards/development/`
- Reference templates from `universal/examples/` for guidance
- NOT edit universal standards directly (they'll be overwritten on upgrade)

---

## Next Steps

Based on this analysis, we should create:

### Phase 1: Core Universal Standards (High Priority)
1. `universal/ai-assistant/README.md` - Entry point
2. `universal/ai-assistant/compliance-protocol.md` - Check standards first
3. `universal/ai-assistant/pre-generation-validation.md` - Three-checkpoint validation WITH FIX
4. `universal/ai-assistant/commit-protocol.md` - Review and CHANGELOG workflow

### Phase 2: Templates (Medium Priority)
5. `universal/examples/python/python-quick-reference-template.md`
6. `universal/examples/python/python-error-patterns-template.md`

### Phase 3: prAxIs OS's Own Standards (Ongoing)
7. Refine `.praxis-os/standards/development/` with prAxIs OS specifics

**Ready to proceed with Phase 1?**

