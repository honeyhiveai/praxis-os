# Tooling Analysis & Recommendations (Final Installation Step)

**Final step: Analyze project tooling and guide users to community best practices if gaps exist.**

---

## 🎯 GOAL

After Agent OS installs universal standards and language-specific guidance:
1. **Analyze** what tooling is configured
2. **Identify** gaps (missing test runner, linter, formatter, etc.)
3. **Recommend** community best practices
4. **Document** findings for AI consumption
5. **Never** create/modify files

---

## 🔍 TOOLING ANALYSIS FRAMEWORK

### Python Tooling Checklist

**Essential Categories:**
1. **Test Runner** - How to run tests
2. **Formatter** - Code style enforcement
3. **Linter** - Code quality checks
4. **Type Checker** - Type safety (optional but recommended)
5. **Dependency Manager** - Package management
6. **Virtual Environment** - Isolation

**Detection Logic:**

```python
def analyze_python_tooling(project_root: Path) -> ToolingAnalysis:
    """
    Analyze Python project tooling configuration.
    Returns gaps and recommendations.
    """
    findings = {
        "test_runner": detect_test_runner(project_root),
        "formatter": detect_formatter(project_root),
        "linter": detect_linter(project_root),
        "type_checker": detect_type_checker(project_root),
        "dependency_manager": detect_dependency_manager(project_root),
        "virtual_env": detect_virtual_env(project_root),
    }
    
    gaps = identify_gaps(findings)
    recommendations = generate_recommendations(gaps, findings)
    
    return ToolingAnalysis(
        findings=findings,
        gaps=gaps,
        recommendations=recommendations,
        completeness_score=calculate_score(findings)
    )
```

---

## 📋 DETECTION HEURISTICS

### Test Runner Detection

```python
def detect_test_runner(project_root: Path) -> Optional[str]:
    """Detect test runner configuration."""
    
    # Check for tox
    if (project_root / "tox.ini").exists():
        return "tox"
    
    # Check for pytest config
    if (project_root / "pytest.ini").exists():
        return "pytest"
    if (project_root / "pyproject.toml").exists():
        config = parse_toml(project_root / "pyproject.toml")
        if "tool.pytest" in config:
            return "pytest"
    
    # Check for unittest discovery
    if (project_root / "setup.py").exists():
        content = (project_root / "setup.py").read_text()
        if "test_suite" in content:
            return "unittest"
    
    # Check for Makefile
    if (project_root / "Makefile").exists():
        content = (project_root / "Makefile").read_text()
        if "test:" in content or ".PHONY: test" in content:
            return "make"
    
    # Check for package.json scripts (for Python tooling via npm)
    if (project_root / "package.json").exists():
        config = parse_json(project_root / "package.json")
        if "scripts" in config and "test" in config["scripts"]:
            return "npm scripts"
    
    return None  # No test runner detected
```

### Formatter Detection

```python
def detect_formatter(project_root: Path) -> Optional[str]:
    """Detect code formatter configuration."""
    
    # Check pyproject.toml for tool configs
    if (project_root / "pyproject.toml").exists():
        config = parse_toml(project_root / "pyproject.toml")
        if "tool.black" in config:
            return "black"
        if "tool.ruff" in config and "format" in config["tool.ruff"]:
            return "ruff"
    
    # Check for .style.yapf
    if (project_root / ".style.yapf").exists():
        return "yapf"
    
    # Check setup.cfg
    if (project_root / "setup.cfg").exists():
        config = parse_ini(project_root / "setup.cfg")
        if "tool:black" in config:
            return "black"
    
    # Check pre-commit hooks
    if (project_root / ".pre-commit-config.yaml").exists():
        config = parse_yaml(project_root / ".pre-commit-config.yaml")
        for repo in config.get("repos", []):
            if "black" in repo.get("repo", ""):
                return "black"
            if "ruff" in repo.get("repo", ""):
                return "ruff"
    
    return None
```

### Linter Detection

```python
def detect_linter(project_root: Path) -> Optional[str]:
    """Detect linter configuration."""
    
    # Check for pylintrc
    if (project_root / ".pylintrc").exists():
        return "pylint"
    if (project_root / "pylintrc").exists():
        return "pylint"
    
    # Check pyproject.toml
    if (project_root / "pyproject.toml").exists():
        config = parse_toml(project_root / "pyproject.toml")
        if "tool.pylint" in config:
            return "pylint"
        if "tool.ruff" in config and "lint" in config["tool.ruff"]:
            return "ruff"
    
    # Check for flake8
    if (project_root / ".flake8").exists():
        return "flake8"
    if (project_root / "setup.cfg").exists():
        config = parse_ini(project_root / "setup.cfg")
        if "flake8" in config:
            return "flake8"
    
    return None
```

### Type Checker Detection

```python
def detect_type_checker(project_root: Path) -> Optional[str]:
    """Detect type checker configuration."""
    
    # Check for mypy
    if (project_root / "mypy.ini").exists():
        return "mypy"
    if (project_root / ".mypy.ini").exists():
        return "mypy"
    if (project_root / "pyproject.toml").exists():
        config = parse_toml(project_root / "pyproject.toml")
        if "tool.mypy" in config:
            return "mypy"
    
    # Check for pyright
    if (project_root / "pyrightconfig.json").exists():
        return "pyright"
    
    # Check for pyre
    if (project_root / ".pyre_configuration").exists():
        return "pyre"
    
    return None
```

---

## 🎯 GAP IDENTIFICATION

```python
def identify_gaps(findings: Dict[str, Optional[str]]) -> List[Gap]:
    """Identify missing or incomplete tooling."""
    gaps = []
    
    if findings["test_runner"] is None:
        gaps.append(Gap(
            category="test_runner",
            severity="critical",
            message="No test runner detected",
            impact="Cannot run tests automatically"
        ))
    
    if findings["formatter"] is None:
        gaps.append(Gap(
            category="formatter",
            severity="important",
            message="No code formatter detected",
            impact="Code style inconsistency likely"
        ))
    
    if findings["linter"] is None:
        gaps.append(Gap(
            category="linter",
            severity="important",
            message="No linter detected",
            impact="No automated code quality checks"
        ))
    
    if findings["type_checker"] is None:
        gaps.append(Gap(
            category="type_checker",
            severity="recommended",
            message="No type checker detected",
            impact="No type safety enforcement"
        ))
    
    return gaps
```

---

## 💡 RECOMMENDATION GENERATION

### Community Best Practices Database

```python
PYTHON_BEST_PRACTICES = {
    "test_runner": {
        "recommended": "pytest with tox wrapper",
        "alternatives": ["pytest", "unittest", "nose2"],
        "rationale": "pytest: most popular, rich ecosystem. tox: multi-env testing.",
        "template": ".agent-os/templates/python/tox.ini",
        "docs": ".agent-os/usage/python-testing-best-practices.md"
    },
    "formatter": {
        "recommended": "black + isort",
        "alternatives": ["ruff format", "yapf", "autopep8"],
        "rationale": "black: opinionated, zero config. isort: import sorting.",
        "template": ".agent-os/templates/python/pyproject.toml",
        "docs": ".agent-os/usage/python-formatting-best-practices.md"
    },
    "linter": {
        "recommended": "pylint OR ruff",
        "alternatives": ["flake8", "pyflakes"],
        "rationale": "pylint: comprehensive. ruff: fast, all-in-one.",
        "template": ".agent-os/templates/python/.pylintrc",
        "docs": ".agent-os/usage/python-linting-best-practices.md"
    },
    "type_checker": {
        "recommended": "mypy",
        "alternatives": ["pyright", "pyre"],
        "rationale": "mypy: most mature, widely adopted.",
        "template": ".agent-os/templates/python/mypy.ini",
        "docs": ".agent-os/usage/python-type-checking-best-practices.md"
    }
}

def generate_recommendations(gaps: List[Gap], findings: Dict) -> List[Recommendation]:
    """Generate recommendations based on gaps and existing tooling."""
    recommendations = []
    
    for gap in gaps:
        category = gap.category
        best_practice = PYTHON_BEST_PRACTICES[category]
        
        # Consider existing tooling when recommending
        existing_tools = [tool for tool in findings.values() if tool]
        
        # If using ruff for formatting, recommend ruff for linting too
        if "ruff" in existing_tools and category == "linter":
            recommendation = "ruff (already using for formatting)"
        else:
            recommendation = best_practice["recommended"]
        
        recommendations.append(Recommendation(
            category=category,
            severity=gap.severity,
            tool=recommendation,
            alternatives=best_practice["alternatives"],
            rationale=best_practice["rationale"],
            template_path=best_practice["template"],
            docs_path=best_practice["docs"]
        ))
    
    return recommendations
```

---

## 📄 GENERATED OUTPUT

### File: `.agent-os/standards/development/python-tooling-analysis.md`

**Example 1: Complete Setup**

```markdown
# Python Tooling Analysis

**Analysis Date:** 2025-10-06  
**Completeness Score:** 100% ✅

---

## Detected Tooling

| Category | Tool | Status |
|----------|------|--------|
| **Test Runner** | tox | ✅ Detected |
| **Formatter** | black + isort | ✅ Detected |
| **Linter** | pylint | ✅ Detected |
| **Type Checker** | mypy | ✅ Detected |
| **Dependency Manager** | pip + requirements.txt | ✅ Detected |
| **Virtual Environment** | venv | ✅ Detected |

---

## Configuration Details

### Test Runner: tox
- **Config file:** `tox.ini`
- **Environments:** py313, lint, format, unit, integration
- **AI command:** `tox` (run all tests), `tox -e unit` (unit only)

### Formatter: black + isort
- **Config file:** `pyproject.toml`
- **Black version:** 23.0+
- **Isort profile:** black-compatible
- **AI command:** `tox -e format` (check), `tox -e format-fix` (auto-fix)

### Linter: pylint
- **Config file:** `pyproject.toml`
- **AI command:** `tox -e lint` (includes pylint + mypy)

### Type Checker: mypy
- **Config file:** `pyproject.toml`
- **Strict mode:** No
- **AI command:** `tox -e lint` (includes mypy)

---

## Assessment

✅ **Excellent tooling setup!**

This project has comprehensive tooling configured. All essential categories
are covered with industry-standard tools.

No recommendations at this time.

---

## AI Execution Protocol

🛑 CRITICAL: Use detected tooling commands

- **Run all tests:** `tox`
- **Run unit tests:** `tox -e unit`
- **Run integration tests:** `tox -e integration`
- **Check code quality:** `tox -e lint`
- **Check formatting:** `tox -e format`
- **Auto-fix formatting:** `tox -e format-fix`

Do NOT run pytest, black, or pylint directly. Always use tox.
```

---

**Example 2: Gaps Detected**

```markdown
# Python Tooling Analysis

**Analysis Date:** 2025-10-06  
**Completeness Score:** 40% ⚠️

---

## Detected Tooling

| Category | Tool | Status |
|----------|------|--------|
| **Test Runner** | pytest | ✅ Detected |
| **Formatter** | None | ❌ Missing |
| **Linter** | None | ❌ Missing |
| **Type Checker** | None | ⚠️ Not detected |
| **Dependency Manager** | pip + requirements.txt | ✅ Detected |
| **Virtual Environment** | venv | ✅ Detected |

---

## Configuration Details

### Test Runner: pytest
- **Config file:** `pytest.ini`
- **AI command:** `pytest tests/` (direct pytest, no wrapper)

---

## Gaps & Recommendations

### 🚨 CRITICAL: No Code Formatter

**Impact:** Code style inconsistency across team. Manual formatting required.

**Recommendation: black + isort**

Black is the most popular Python formatter (opinionated, zero-config).
Isort handles import sorting.

**How to add:**
1. Install: `pip install black isort`
2. Configure: See template at `.agent-os/templates/python/pyproject.toml`
3. Usage: `black src/ tests/` and `isort src/ tests/`
4. Learn more: `.agent-os/usage/python-formatting-best-practices.md`

**Alternatives:**
- ruff format (fast, all-in-one tool)
- yapf (Google style guide)

---

### ⚠️ IMPORTANT: No Linter

**Impact:** No automated code quality checks. Bugs and code smells undetected.

**Recommendation: pylint OR ruff**

Pylint is comprehensive (finds bugs, smells, style issues).
Ruff is faster and combines multiple tools.

**How to add:**
1. Install: `pip install pylint` OR `pip install ruff`
2. Configure: See template at `.agent-os/templates/python/.pylintrc`
3. Usage: `pylint src/` OR `ruff check src/`
4. Learn more: `.agent-os/usage/python-linting-best-practices.md`

---

### 💡 RECOMMENDED: Add Type Checker

**Impact:** No type safety enforcement. Type-related bugs possible.

**Recommendation: mypy**

Mypy is the most mature Python type checker. Catches type errors at dev time.

**How to add:**
1. Install: `pip install mypy`
2. Add type hints to code: `def foo(x: int) -> str:`
3. Configure: See template at `.agent-os/templates/python/mypy.ini`
4. Usage: `mypy src/`
5. Learn more: `.agent-os/usage/python-type-checking-best-practices.md`

---

## Suggested Next Steps

1. **Add formatter** (critical): Ensures consistent code style
   - Run: `cp .agent-os/templates/python/pyproject.toml ./pyproject.toml`
   - Install: `pip install black isort`
   - Test: `black --check src/`

2. **Add linter** (important): Catches bugs and code smells
   - Install: `pip install pylint`
   - Configure: `cp .agent-os/templates/python/.pylintrc ./.pylintrc`
   - Test: `pylint src/`

3. **Consider tox wrapper** (recommended): Coordinate all tools
   - Copy: `cp .agent-os/templates/python/tox.ini ./tox.ini`
   - Install: `pip install tox`
   - Test: `tox -e lint`
   - Learn more: `.agent-os/usage/python-testing-best-practices.md`

4. **Add type hints** (optional but recommended): Improve code quality
   - Add hints to functions: `def foo(x: int) -> str:`
   - Install mypy: `pip install mypy`
   - Check types: `mypy src/`

---

## AI Execution Protocol

🛑 CRITICAL: Use detected tooling commands

- **Run tests:** `pytest tests/`

⚠️ **Formatting not configured:** AI cannot auto-format code until formatter added.

⚠️ **Linting not configured:** AI cannot check code quality automatically.

Once tooling added, update this file and `.agent-os/config.json`.
```

---

## 🔄 INSTALLATION FLOW (WITH FINAL STEP)

### Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Install Universal Standards                             │
│  - Copy universal/ standards to .agent-os/standards/            │
│  - Copy universal/usage/ to .agent-os/usage/                    │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Detect Language                                         │
│  - Scan for *.py files → Python                                 │
│  - Scan for *.ts files → TypeScript                             │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Generate Language-Specific Standards                    │
│  - python-testing.md (universal principles → Python)            │
│  - python-concurrency.md                                         │
│  - python-dependencies.md                                        │
│  - python-code-quality.md                                        │
│  - python-documentation.md                                       │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Analyze Tooling (NEW FINAL STEP)                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 4a. Detect Existing Tooling                              │   │
│  │     - Test runner? (tox, pytest, make)                   │   │
│  │     - Formatter? (black, ruff, yapf)                     │   │
│  │     - Linter? (pylint, ruff, flake8)                     │   │
│  │     - Type checker? (mypy, pyright)                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 4b. Identify Gaps                                        │   │
│  │     - Critical: No test runner                           │   │
│  │     - Important: No formatter                            │   │
│  │     - Recommended: No type checker                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 4c. Generate Recommendations                             │   │
│  │     - Point to community best practices                  │   │
│  │     - Link to templates                                  │   │
│  │     - Provide rationale                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 4d. Document Findings                                    │   │
│  │     - Create: python-tooling-analysis.md                 │   │
│  │     - Completeness score                                 │   │
│  │     - Gaps & recommendations                             │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: Build RAG Index                                         │
│  - Index all standards (including tooling-analysis.md)          │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 6: Display Summary                                         │
│                                                                   │
│  ✓ Agent OS installed successfully!                             │
│                                                                   │
│  Tooling Analysis:                                               │
│  ─────────────────────────────────────────────────────          │
│  Completeness Score: 40% ⚠️                                      │
│                                                                   │
│  Detected:                                                        │
│  ✓ Test runner: pytest                                          │
│  ✓ Dependency manager: pip                                      │
│                                                                   │
│  Missing:                                                         │
│  ✗ Formatter (critical)                                          │
│  ✗ Linter (important)                                            │
│  ✗ Type checker (recommended)                                    │
│                                                                   │
│  See recommendations: .agent-os/standards/development/          │
│                        python-tooling-analysis.md               │
│                                                                   │
│  Templates available: .agent-os/templates/python/               │
│  Best practices: .agent-os/usage/python-*-best-practices.md    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 KEY BENEFITS

### 1. Non-Invasive
- Never creates files
- Never modifies existing files
- Just analyzes and documents

### 2. Educational
- Explains gaps and their impact
- Points to community best practices
- Provides rationale for recommendations

### 3. Actionable
- Links to templates (ready to copy)
- Links to detailed guides
- Clear next steps

### 4. AI-Consumable
- Documents findings in standards
- AI can query via RAG
- Clear execution commands

### 5. Team-Friendly
- Respects existing conventions
- Suggests improvements (doesn't force)
- Balances pragmatism with best practices

---

## 📝 SUMMARY

**Final Installation Step: Tooling Analysis**

```
1. Detect: What tooling exists?
2. Analyze: What's missing?
3. Recommend: Point to best practices
4. Document: Create tooling-analysis.md
5. Display: Show summary to user
6. Done: User decides next steps
```

**User then:**
- Reads recommendations
- Copies templates if desired
- Or keeps current setup
- Or implements custom solution

**Result:** Agent OS provides guidance, user maintains control.

---

**This approach balances helpfulness with non-invasiveness. Thoughts?**
