# Installation Variation Strategy

**How Agent OS handles tooling variations during LLM-driven installation.**

---

## 🎯 THE CORE TENSION

Agent OS is installed by an **LLM agent** following the `installation-guide.md`. But real-world projects have variations:

- Existing tox.ini with different env groupings
- Different formatters (black vs ruff vs yapf)
- Different test runners (pytest vs unittest vs nose)
- Different CI setups (GitHub Actions vs GitLab vs Jenkins)

**Question:** Should Agent OS **prescribe** tooling or **adapt** to existing conventions?

---

## 📊 THREE INSTALLATION SCENARIOS

### Scenario 1: Greenfield Project (No Existing Tooling)

**Context:**
- New project, no tox.ini, no .pre-commit-config.yaml
- No existing CI/CD
- Empty or minimal pyproject.toml

**Agent OS Approach:**
```
✅ PRESCRIBE BEST PRACTICES
- Install tox.ini with python-sdk grouping (lint = pylint+mypy, format = black+isort)
- Create .pre-commit-config.yaml
- Generate GitHub Actions workflow
- Rationale: No conflicts, establish good patterns from day 1
```

**Outcome:** Consistent, high-quality setup across all greenfield projects.

---

### Scenario 2: Existing Project with Compatible Tooling

**Context:**
- Has tox.ini with similar groupings (maybe slightly different)
- Uses black, isort, pylint, mypy (same tools, different config)
- Has working CI/CD

**Agent OS Approach:**
```
⚖️ DETECT → SUGGEST → ADAPT
1. Detect: "Project uses black, isort, pylint, mypy"
2. Compare: "Grouping differs: lint has formatting checks"
3. Document: Create standard explaining existing approach
4. Suggest: "Consider aligning with python-sdk grouping for consistency"
5. Respect: Don't modify existing tox.ini
```

**Example Standard Generated:**
```markdown
# .agent-os/standards/development/python-project-tooling.md

## Project Tooling Configuration

This project uses the following tox configuration:

- `tox -e lint`: black --check, isort --check, pylint
- `tox -e type`: mypy
- `tox -e format`: black, isort (auto-fix)

**Rationale:** [Detected from existing tox.ini]

**Note:** This differs from Agent OS python-sdk reference (which groups
pylint+mypy as "lint"). Consider aligning for consistency across projects,
but existing setup works well.

**To align with python-sdk:**
- Move black/isort checks to `[testenv:format]`
- Move mypy to `[testenv:lint]`
- See: .agent-os/usage/tox-best-practices.md
```

**Outcome:** Agent OS documents existing approach, suggests improvements, but doesn't force changes.

---

### Scenario 3: Existing Project with Different Tools

**Context:**
- Uses ruff instead of black+isort+pylint
- Uses nose2 instead of pytest
- No tox, uses Makefile

**Agent OS Approach:**
```
🔍 DETECT → DOCUMENT → INTEGRATE
1. Detect: "No tox.ini, has Makefile with 'make test', 'make lint'"
2. Detect: "Uses ruff (all-in-one) instead of black+pylint"
3. Document: Create standard explaining project's approach
4. Integrate: Reference Makefile targets in .agent-os/config.json
5. Respect: Don't create competing tox.ini
```

**Generated Config:**
```json
{
  "test_command": "make test",
  "lint_command": "make lint",
  "format_command": "make format",
  "tooling": {
    "runner": "make",
    "formatter": "ruff",
    "linter": "ruff",
    "test_framework": "nose2"
  }
}
```

**Generated Standard:**
```markdown
# .agent-os/standards/development/python-project-tooling.md

## Project Tooling Configuration

This project uses **ruff** for linting and formatting (all-in-one tool).

Commands:
- `make lint`: Run ruff check
- `make format`: Run ruff format
- `make test`: Run nose2

**Rationale:** Ruff is faster and combines multiple tools.

**AI Test Execution Protocol:**
- Run tests: `make test`
- Run linting: `make lint`
- Auto-fix: `make format`
```

**Outcome:** Agent OS adapts to project's existing tooling, documents it for AI consumption.

---

## 🤖 INSTALLATION DETECTION LOGIC

### Phase 1: Discovery (Read-Only)

**What the installer checks:**

```python
# Pseudo-code for installation agent

def detect_project_tooling(project_root):
    findings = {}
    
    # Check for test runners
    if (project_root / "tox.ini").exists():
        findings["test_runner"] = "tox"
        findings["tox_envs"] = parse_tox_envs()
    elif (project_root / "Makefile").exists():
        findings["test_runner"] = "make"
        findings["make_targets"] = parse_makefile_targets()
    elif (project_root / "pyproject.toml").exists():
        findings["test_runner"] = detect_from_pyproject()
    
    # Check for formatters
    if check_uses_ruff():
        findings["formatter"] = "ruff"
        findings["linter"] = "ruff"
    elif check_uses_black():
        findings["formatter"] = "black"
        findings["import_sorter"] = "isort"
        findings["linter"] = detect_linter()  # pylint, flake8, etc.
    
    # Check for existing standards
    if (project_root / ".agent-os").exists():
        findings["agent_os_installed"] = True
        findings["agent_os_version"] = detect_version()
    
    return findings
```

---

### Phase 2: Decision Logic

**Decision tree for installer:**

```
1. Is Agent OS already installed?
   YES → Update mode (respect existing standards, suggest improvements)
   NO → Continue

2. Does project have ANY existing tooling?
   NO → Greenfield mode (prescribe best practices)
   YES → Continue

3. Is existing tooling compatible with Agent OS standards?
   YES → Integration mode (document existing, light suggestions)
   NO → Adaptation mode (adapt standards to existing tools)

4. Are there conflicts (e.g., tox + Makefile both present)?
   YES → Prompt user: "Which is primary?"
   NO → Continue

5. Document decisions in .agent-os/standards/development/
```

---

### Phase 3: User Prompts (When Needed)

**When to prompt user:**

```
Scenario: Conflicting tooling detected
─────────────────────────────────────────────────────
Agent: "I detected both tox.ini and Makefile with overlapping targets.
        Which should I use as the primary test/lint command?"

Options:
1. tox (recommended for Python projects)
2. make (keep existing workflow)
3. Both (I'll document both)

User: [makes choice]

Agent: "Got it. I'll configure .agent-os/config.json to use [choice]."
```

```
Scenario: No tooling detected
─────────────────────────────────────────────────────
Agent: "No test runner detected. Would you like me to create one?"

Options:
1. Yes, create tox.ini (recommended)
2. Yes, create Makefile
3. No, I'll add it later

User: [makes choice]

Agent: "Creating tox.ini with best practices from python-sdk..."
```

---

## 📋 INSTALLATION MODES

### Mode 1: Prescriptive (Greenfield)

**When:** No existing tooling detected

**What Agent OS does:**
```
1. Create tox.ini with python-sdk grouping:
   - [testenv:lint]: pylint + mypy
   - [testenv:format]: black --check + isort --check
   - [testenv:format-fix]: black + isort (auto-fix)

2. Create .agent-os/config.json:
   {
     "test_command": "tox",
     "lint_command": "tox -e lint",
     "format_command": "tox -e format-fix"
   }

3. Generate standard: python-tooling.md
   Documents WHY these choices (best practices, consistency)

4. Update language instructions for future projects
```

**Variation:** None (deterministic)

---

### Mode 2: Suggestive (Compatible Existing)

**When:** Existing tooling similar but not identical

**What Agent OS does:**
```
1. Do NOT modify existing tox.ini

2. Create .agent-os/config.json pointing to existing:
   {
     "test_command": "tox",
     "lint_command": "tox -e lint",
     "format_command": "tox -e format"
   }

3. Generate standard: python-tooling.md
   - Documents EXISTING approach
   - Includes "Suggestion" section:
     "Consider aligning with python-sdk for consistency.
      See: .agent-os/usage/tox-best-practices.md"

4. Create .agent-os/standards/suggestions/
   - tox-alignment-suggestion.md (why and how to align)
```

**Variation:** Medium (documents existing, but consistently suggests same improvements)

---

### Mode 3: Adaptive (Different Tools)

**When:** Existing tooling incompatible (e.g., ruff instead of black+pylint)

**What Agent OS does:**
```
1. Do NOT create competing tox.ini

2. Create .agent-os/config.json adapted to existing:
   {
     "test_command": "make test",
     "lint_command": "ruff check src/",
     "format_command": "ruff format src/",
     "tooling": {
       "runner": "make",
       "formatter": "ruff",
       "linter": "ruff"
     }
   }

3. Generate standard: python-tooling.md
   - Documents project's ACTUAL tooling
   - No suggestions (different paradigm, equally valid)

4. Update AI execution rules to use ruff syntax
```

**Variation:** High (adapts to existing, but documents consistently)

---

## 🎯 REDUCING LLM INSTALLATION VARIATION

### Problem: LLM Non-Determinism

**Risk:** Same installation-guide.md → different decisions each time

**Example variation:**
```
Install 1: Creates tox.ini with python-sdk grouping
Install 2: Creates tox.ini with agent-os-enhanced grouping
Install 3: Detects non-existent Makefile, creates Makefile instead
```

**Result:** Inconsistent projects, confused developers

---

### Solution 1: Explicit Decision Trees

**In `installation-guide.md`:**

```markdown
## Step 4: Configure Testing Tools

### Detection Phase (ALWAYS DO THIS FIRST)

1. Check if `tox.ini` exists: `ls tox.ini`
   - EXISTS → Go to "Integration Mode"
   - NOT FOUND → Continue to step 2

2. Check if `Makefile` exists: `ls Makefile`
   - EXISTS AND has "test" target → Go to "Makefile Mode"
   - NOT FOUND → Continue to step 3

3. Check if `pyproject.toml` has test runner:
   - HAS pytest config → Go to "pyproject.toml Mode"
   - NO test config → Go to "Greenfield Mode"

### Greenfield Mode (No Existing Tooling)

🛑 CRITICAL: Use EXACT template below (no variations)

Create `tox.ini` with this EXACT content:
[paste full python-sdk tox.ini template]

Rationale: Consistency across all Agent OS projects.
```

---

### Solution 2: Template Files (Not Instructions)

**Instead of:** "Create tox.ini with lint env for pylint and mypy"

**Use:** "Copy `universal/templates/python/tox.ini` to project root"

**Benefit:** Eliminates interpretation variation

---

### Solution 3: Validation Gates

**After installation step:**

```markdown
## Step 4.5: Validate Tooling Configuration

Run validation:
```bash
python .agent-os/scripts/validate_installation.py
```

This checks:
- ✅ tox.ini has required envs: lint, format, unit, integration
- ✅ .agent-os/config.json points to correct commands
- ✅ Standards reference correct tooling

If validation fails, do NOT proceed.
```

---

### Solution 4: Idempotency Checks

```markdown
## Before Creating Files

🛑 ALWAYS check if file exists BEFORE creating:

```python
if Path("tox.ini").exists():
    # Existing tooling detected
    # Go to Integration Mode (Step X)
else:
    # Create new tox.ini
```

⚠️ NEVER overwrite existing tooling without explicit user approval.
```

---

## 📝 RECOMMENDATION: HYBRID APPROACH

### For Agent OS Enhanced

**1. Prescriptive for "Blessed Stack"**

Define a **blessed stack** in language instructions:
```markdown
## Agent OS Python Blessed Stack

For greenfield projects, Agent OS installs:
- **Test runner:** tox
- **Formatter:** black + isort
- **Linter:** pylint
- **Type checker:** mypy
- **Grouping:** python-sdk approach (lint=pylint+mypy, format=black+isort)

Rationale: Industry best practices, mature tools, wide adoption.
```

**2. Adaptive for Existing Projects**

Detection logic:
```
IF tox.ini exists:
  - Document existing grouping
  - Do NOT modify
  - Create standard explaining it
  - Suggest alignment (optional)

IF ruff detected:
  - Adapt standards to ruff
  - No tox.ini creation
  - Document ruff usage

IF Makefile detected:
  - Integrate with Makefile
  - Reference make targets
  - No competing tox.ini
```

**3. Template-Based Installation**

Store reference configs:
```
universal/templates/python/
├── tox.ini.template          # python-sdk grouping
├── pyproject.toml.template   # Basic config
└── .pre-commit-config.yaml   # Standard hooks
```

Installation uses exact templates (no LLM generation).

**4. Document ALL Decisions**

Every installation creates:
```
.agent-os/standards/development/python-tooling.md

# Python Tooling Configuration

## Installation Mode: [Greenfield/Suggestive/Adaptive]

## Detected Tooling:
- Test runner: tox (created during installation)
- Formatter: black + isort
- Linter: pylint
- Type checker: mypy

## Rationale:
No existing tooling detected. Installed Agent OS blessed stack
for consistency with python-sdk and best practices.

## Commands:
- Run tests: `tox`
- Run linting: `tox -e lint`
- Check formatting: `tox -e format`
- Auto-fix formatting: `tox -e format-fix`
```

---

## 🎭 EXAMPLE: agent-os-enhanced Installation

**What SHOULD have happened:**

```
Step 1: Detection
- No existing tox.ini
- No Makefile with test targets
- Empty .agent-os/

Step 2: Mode Selection
→ Greenfield Mode (prescriptive)

Step 3: Installation
- Copy universal/templates/python/tox.ini → ./tox.ini
- Content: python-sdk grouping (lint=pylint+mypy, format=black+isort)
- Rationale: Agent OS blessed stack

Step 4: Documentation
- Create .agent-os/standards/development/python-tooling.md
- Explain blessed stack choices
- Reference python-sdk as exemplar

Step 5: Validation
- Run: python .agent-os/scripts/validate_installation.py
- Confirms: tox.ini matches blessed stack template
```

**What ACTUALLY happened:**

```
Step 1-2: Same (detection → greenfield)

Step 3: Installation (LLM generated tox.ini from scratch)
- LLM created tox.ini based on general knowledge
- Mixed formatting checks into [testenv:lint]
- Separated mypy into [testenv:type]
- Rationale: (not explicitly documented)

Result: Inconsistent with python-sdk
```

**Root cause:** No template file, LLM interpreted instructions differently.

---

## ✅ ACTION ITEMS

### For Skeleton (universal/ directory)

1. **Create template files:**
   ```
   universal/templates/python/
   ├── tox.ini                    # python-sdk grouping
   ├── pyproject.toml
   └── .pre-commit-config.yaml
   ```

2. **Update installation-guide.md:**
   - Add explicit detection logic (if/else branches)
   - Reference template files (copy, don't generate)
   - Add validation step

3. **Create validation script:**
   ```
   universal/scripts/validate_python_installation.py
   ```

### For Language Instructions (language-instructions/python.md)

1. **Add "Blessed Stack" section**
2. **Add "Detection Logic" section**
3. **Add "Installation Modes" section**
4. **Reference template files explicitly**

### For Documentation

1. **Create:** `universal/usage/installation-philosophy.md`
   - Explains prescriptive vs adaptive
   - When to use each mode
   - How to handle edge cases

---

## 📊 SUMMARY

| Aspect | Prescriptive (Greenfield) | Adaptive (Existing) |
|--------|---------------------------|---------------------|
| **When** | No existing tooling | Existing tooling detected |
| **Approach** | Install blessed stack | Document & integrate |
| **Variation** | None (template-based) | Medium (adapts to existing) |
| **tox.ini** | Create from template | Do not modify |
| **Standards** | Explain blessed stack | Explain existing + suggest |
| **Consistency** | High (same across projects) | Medium (varies by project) |

**Key Principle:** **Prescribe for greenfield, adapt for existing, always document decisions.**

---

**Want me to create the template files and update the installation guide?**
