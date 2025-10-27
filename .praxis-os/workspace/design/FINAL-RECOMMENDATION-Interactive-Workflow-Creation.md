# Final Recommendation: Interactive Workflow Creation Systems

**Date:** October 9, 2025  
**Status:** Final  
**Approach:** Interactive AI-guided creation, not automated scripts

---

## Core Concept

Workflow creation systems are **NOT generator scripts**. They are **knowledge systems** that guide the AI in creating workflows interactively with user input.

### The Pattern

```
User: "I need test generation for my Python project"

AI: *Reads workflow-types/test-generation/design/* 
    *Asks about tooling*
    
AI: "I see you're using Python. What test framework?"
User: "pytest with tox"

AI: "What quality tools?"
User: "pylint, black, mypy"

AI: *Uses create_workflow() with discovered/confirmed info*
    *References templates to build phases*
    *Creates workflow in .praxis-os/workflows/*
    
AI: "Created test_generation_python_v1 workflow.
     Ready to use with: start_workflow(...)"
```

---

## Structure

### Universal Standards Location

```
universal/standards/workflow-types/
├── README.md
│   """
│   # Workflow-Type Creation Systems
│   
│   Knowledge systems that guide AI in creating workflows
│   of specific types (test generation, code generation).
│   
│   These are NOT scripts - they're indexed documentation
│   that the AI references during interactive creation.
│   """
│
├── test-generation/
│   ├── README.md
│   │   """
│   │   # Test Generation Workflow Creation System
│   │   
│   │   **Purpose:** Guide AI in creating test generation workflows
│   │   **Method:** Interactive discovery + template application
│   │   **Output:** Language-specific test workflow
│   │   
│   │   ## AI Usage Pattern
│   │   
│   │   1. User requests test generation workflow
│   │   2. AI reads this system's design docs
│   │   3. AI discovers/confirms language and tooling
│   │   4. AI applies templates via create_workflow()
│   │   5. AI creates workflow in user's project
│   │   
│   │   ## Not a Script
│   │   
│   │   This is NOT an automated generator. It's a knowledge
│   │   base that guides the AI through interactive creation
│   │   where user can weigh in on tooling choices.
│   │   """
│   │
│   ├── design/                    ← AI reads these (indexed ✅)
│   │   ├── overview.md            "What is test generation workflow?"
│   │   ├── methodology.md         "8-phase approach"
│   │   ├── path-system.md         "Unit/integration/validation paths"
│   │   ├── tooling-discovery.md  "How to detect/ask about tools"
│   │   └── creation-process.md    "Step-by-step AI creation guide"
│   │
│   ├── language-guides/           ← AI reads these (indexed ✅)
│   │   ├── README.md              "Language-specific considerations"
│   │   ├── python.md              "Python: pytest, pylint, black, mypy"
│   │   ├── javascript.md          "JS: jest, eslint, prettier"
│   │   ├── typescript.md          "TS: jest, eslint, prettier, tsc"
│   │   └── ...
│   │
│   └── templates/                 ← AI uses these (NOT indexed ❌)
│       ├── README.md              "Available templates" (indexed ✅)
│       ├── metadata-template.json
│       ├── phase-templates/
│       │   ├── phase-0-analysis.template.md
│       │   ├── phase-1-output.template.md
│       │   └── ...
│       └── task-templates/
│           ├── ast-analysis.template.md
│           ├── dependency-mapping.template.md
│           └── ...
│
└── production-code-generation/
    └── ... (similar structure)
```

---

## Interactive Creation Flow

### Step 1: User Request

```
User: "Create a test generation workflow for my Python project"
```

### Step 2: AI Discovery Phase

**AI reads:**
- `universal/standards/workflow-types/test-generation/design/overview.md`
- `universal/standards/workflow-types/test-generation/design/creation-process.md`
- `universal/standards/workflow-types/test-generation/language-guides/python.md`

**AI analyzes project:**
```python
# Check for Python files
glob("**/*.py")

# Detect test framework
if Path("pytest.ini").exists() or "pytest" in requirements:
    test_framework = "pytest"
elif Path("tox.ini").exists():
    test_framework = "pytest + tox"
else:
    test_framework = None  # Ask user

# Detect linter
if "pylint" in requirements:
    linter = "pylint"
elif "flake8" in requirements:
    linter = "flake8"
else:
    linter = None  # Ask user

# etc.
```

### Step 3: AI Confirms with User

```
AI: "I've detected your Python project uses:
     - Test framework: pytest + tox
     - Linter: pylint
     - Formatter: black
     - Type checker: mypy
     
     Is this correct? Any changes?"

User: "Yes, that's right"

OR

User: "Actually, we don't use mypy yet, skip that"
```

### Step 4: AI Creates Workflow

```python
# Via MCP tool
create_workflow(
    name="test_generation_python_v1",
    workflow_type="test_generation",
    phases=[
        "Phase 0: Analysis",
        "Phase 1: Output Patterns",
        "Phase 2: Dependencies",
        # ... 8 phases total
    ],
    target_language="python",
    options={
        "test_framework": "pytest",
        "tox_enabled": true,
        "linter": "pylint",
        "formatter": "black",
        "type_checker": None,  # User said skip
        "paths": ["unit", "integration", "functional"]
    }
)
```

**Behind the scenes:**
- MCP tool reads templates from `templates/`
- Applies language-specific customizations
- Populates placeholders with detected/confirmed tooling
- Creates workflow files in `.praxis-os/workflows/test_generation_python_v1/`

### Step 5: Confirmation

```
AI: "✅ Created test generation workflow for Python

     Location: .praxis-os/workflows/test_generation_python_v1/
     
     Phases: 8 (analysis through quality enforcement)
     Paths: unit, integration, functional
     Tools: pytest, tox, pylint, black
     
     Ready to use:
     start_workflow('test_generation_python_v1', 'src/module.py')
     
     Want me to explain the workflow or start generating tests?"
```

---

## Design Documentation Structure

### design/overview.md (~100 lines)

```markdown
# Test Generation Workflow System Overview

**Purpose:** Create language-specific test generation workflows

**Output:** Complete workflow in .praxis-os/workflows/

**Approach:** Interactive AI-guided creation with user confirmation

## What This Creates

An 8-phase test generation workflow:
- Phase 0: Code analysis (AST, functions, properties)
- Phase 1: Output patterns (logging, console)
- Phase 2: Dependency mapping (imports, mocking strategy)
- Phase 3: Usage patterns (call sites, contexts)
- Phase 4: Coverage analysis (existing tests, gaps)
- Phase 5: Test plan creation (human approval)
- Phase 6: Test generation (actual test code)
- Phase 7: Quality validation (linter, formatter, tests)
- Phase 8: Completion and handoff

## Multi-Path Support

- Unit tests: Mock dependencies, isolation
- Integration tests: Real dependencies, interactions
- Validation/Functional/E2E tests: Real-world scenarios
  (Name varies by language - see path-system.md)

## Language Support

See language-guides/ for language-specific tooling:
- Python (pytest, pylint, black, mypy)
- JavaScript (jest, eslint, prettier)
- TypeScript (jest, eslint, prettier, tsc)
- Go (go test, golangci-lint, gofmt)
- etc.
```

### design/creation-process.md (~150 lines)

```markdown
# AI Workflow Creation Process

**For AI:** Step-by-step guide to creating test generation workflows

## Prerequisites

Before creating workflow:

1. ✅ Confirm user wants test generation
2. ✅ Identify target language
3. ✅ Detect or ask about tooling
4. ✅ Confirm path preferences (unit/integration/validation)

## Step-by-Step Process

### Step 1: Language Detection

🛑 EXECUTE-NOW: Detect language

```python
# Check file extensions
language = detect_primary_language()
# Python: .py files
# JavaScript: .js files
# TypeScript: .ts files
# Go: .go files
```

### Step 2: Tooling Discovery

Read language guide for target language:
```
universal/standards/workflow-types/test-generation/language-guides/{language}.md
```

🛑 EXECUTE-NOW: Detect tools

**Test Framework:**
- Python: pytest.ini, tox.ini, unittest
- JavaScript: jest.config.js, package.json
- TypeScript: jest.config.ts, package.json
- Go: go test (built-in)

**Linter:**
- Python: pylint, flake8 in requirements
- JavaScript: .eslintrc
- TypeScript: .eslintrc, tsconfig.json
- Go: .golangci.yml

**Formatter:**
- Python: black, autopep8
- JavaScript: .prettierrc
- TypeScript: .prettierrc
- Go: gofmt (built-in)

**Type Checker:**
- Python: mypy.ini
- TypeScript: tsconfig.json
- Go: built-in

### Step 3: User Confirmation

📊 COUNT-AND-DOCUMENT: Present findings

```
AI: "Detected:
     Language: Python
     Test framework: pytest + tox
     Linter: pylint
     Formatter: black
     Type checker: mypy
     
     Confirm or make changes?"
```

### Step 4: Path Selection

Ask about test paths:
```
AI: "What types of tests do you want to generate?
     [ ] Unit tests (isolation, mocked dependencies)
     [ ] Integration tests (component interactions)
     [ ] Functional tests (end-to-end scenarios)
     
     Recommended: All three for comprehensive coverage"
```

Note: Path 3 name varies by language (see path-system.md):
- Python: "functional"
- JavaScript/TypeScript: "validation" or "e2e"
- Go: "e2e"
- Java: "acceptance"

### Step 5: Create Workflow

🛑 EXECUTE-NOW: Use create_workflow tool

```python
create_workflow(
    name=f"test_generation_{language}_v1",
    workflow_type="test_generation",
    phases=[...],  # 8 phases
    target_language=language,
    options={
        "test_framework": detected_test_framework,
        "linter": detected_linter,
        "formatter": detected_formatter,
        "type_checker": detected_type_checker,
        "paths": selected_paths,
        "tox_enabled": tox_detected  # Python-specific
    }
)
```

### Step 6: Template Application

The create_workflow tool will:
1. Read templates from templates/phase-templates/
2. Read templates from templates/task-templates/
3. Populate placeholders with language-specific tooling
4. Create workflow files in .praxis-os/workflows/

### Step 7: Confirmation

📊 COUNT-AND-DOCUMENT: Confirm creation

```
AI: "✅ Workflow created successfully
     
     Location: .praxis-os/workflows/test_generation_{language}_v1/
     Phases: 8
     Total tasks: ~45
     
     Ready to use with: start_workflow(...)"
```

## Error Handling

If tooling not detected:
- ⚠️ Ask user for missing information
- Don't assume defaults
- Provide recommendations based on language guide

If language not supported:
- ⚠️ Check language-guides/ directory
- If no guide exists, explain current support
- Suggest manual workflow creation using meta-workflow principles
```

### design/tooling-discovery.md (~100 lines)

```markdown
# Tooling Discovery Guide

**For AI:** How to detect and confirm project tooling

## Python

### Test Framework
Check files:
- `pytest.ini` → pytest
- `tox.ini` → pytest + tox (recommend using tox)
- `setup.py` → unittest (built-in)
- `pyproject.toml` → check [tool.pytest]

Ask user if not found:
"What test framework do you use?
 - pytest (recommended)
 - unittest (built-in)
 - pytest with tox (for multi-environment testing)"

### Linter
Check files:
- `pyproject.toml` [tool.pylint] → pylint
- `.pylintrc` → pylint
- `.flake8` → flake8
- `requirements.txt` or `pyproject.toml` dependencies

Recommend: pylint (comprehensive)

### Formatter
Check files:
- `pyproject.toml` [tool.black] → black
- `.black` → black
- Check dependencies

Recommend: black (opinionated, consistent)

### Type Checker
Check files:
- `mypy.ini` → mypy
- `pyproject.toml` [tool.mypy] → mypy
- Look for type hints in existing code

Optional: Ask if they want type checking

## JavaScript

### Test Framework
Check files:
- `jest.config.js` → Jest
- `package.json` scripts.test → check command
- `mocha` in dependencies → Mocha
- `jasmine` in dependencies → Jasmine

Recommend: Jest (most popular)

### Linter
Check files:
- `.eslintrc` → ESLint
- `.eslintrc.js` → ESLint
- `package.json` eslintConfig → ESLint

Recommend: ESLint (standard)

### Formatter
Check files:
- `.prettierrc` → Prettier
- `package.json` prettier config → Prettier

Recommend: Prettier (most popular)

## TypeScript

Same as JavaScript, plus:

### Type Checker
- `tsconfig.json` → tsc (built-in)
- Always present for TypeScript projects

## Go

### Test Framework
- `go test` is built-in, always use

### Linter
Check files:
- `.golangci.yml` → golangci-lint
- Default: `go vet` (built-in)

Recommend: golangci-lint (comprehensive)

### Formatter
- `gofmt` is built-in, always use

## General Pattern

For each language:
1. 🔍 Check for config files
2. 🔍 Check dependencies/requirements
3. ❓ Ask user if not found
4. 💡 Recommend best practices
5. ✅ Confirm with user before creating
```

---

## Language Guides Structure

### language-guides/python.md (~200 lines)

```markdown
# Python Test Generation Guide

**For AI:** Creating Python test generation workflows

## Overview

Python test generation workflow characteristics:
- Test framework: pytest or unittest
- Multi-environment: tox (recommended)
- Linting: pylint (10.0/10 target)
- Formatting: black (100% compliant)
- Type checking: mypy (optional, 0 errors if used)

## Tooling Detection

### Test Framework

**Priority 1: tox**
```python
if Path("tox.ini").exists():
    # ALWAYS use tox if available
    test_framework = "pytest + tox"
    test_command = "tox -e unit"
```

Why: tox provides isolated environments, matches CI/CD

**Priority 2: pytest**
```python
if Path("pytest.ini").exists() or "pytest" in requirements:
    test_framework = "pytest"
    test_command = "pytest tests/"
```

**Priority 3: unittest**
```python
# Built-in, always available
test_framework = "unittest"
test_command = "python -m unittest discover"
```

### Analysis Tools

**AST Parsing:**
```python
# Built-in ast module for code analysis
import ast
tree = ast.parse(source_code)
# Extract: functions, parameters, return types, attribute access
```

**Coverage:**
```python
# pytest-cov for coverage measurement
test_command_with_coverage = "pytest --cov=module --cov-report=term-missing"
```

## Test Paths

Python standard names:
- Unit: `tests/unit/`
- Integration: `tests/integration/`
- Functional: `tests/functional/` ← Python convention

(Not "validation" or "e2e" - use "functional" for Python)

## Phase-Specific Commands

### Phase 0: AST Analysis
```python
python -c "
import ast
with open('target.py') as f:
    tree = ast.parse(f.read())
# Extract functions, classes, methods
"
```

### Phase 1: Logging Detection
```bash
grep -n "logger\|logging\|print" target.py
```

### Phase 7: Quality Validation
```bash
# If tox configured
tox -e unit          # Run tests
tox -e lint          # Run pylint
tox -e type          # Run mypy

# If no tox
pytest tests/unit/ -v
pylint target.py
black --check target.py
mypy target.py
```

## Quality Targets

- Test pass rate: 100%
- Pylint score: 10.0/10 (exactly)
- Black formatting: 100% compliant
- MyPy errors: 0 (if type checking enabled)
- Coverage: 90%+ line and branch (unit tests)

## Example Workflow Creation

```python
create_workflow(
    name="test_generation_python_v1",
    workflow_type="test_generation",
    target_language="python",
    options={
        "test_framework": "pytest",
        "tox_enabled": True,
        "linter": "pylint",
        "linter_target": "10.0/10",
        "formatter": "black",
        "type_checker": "mypy",
        "coverage_target": 90,
        "paths": ["unit", "integration", "functional"]
    }
)
```
```

---

## Templates (Not Indexed)

### Why Not Indexed

Templates contain placeholders like `{LANGUAGE}`, `{TEST_FRAMEWORK}`, `{LINTER_COMMAND}`.

If indexed, search results would show placeholder values, confusing users.

Instead:
- ✅ Design docs ARE indexed (guide AI)
- ✅ Language guides ARE indexed (tool-specific guidance)
- ❌ Templates are NOT indexed (applied during creation)

### Template Example

`templates/phase-templates/phase-0-analysis.template.md`:

```markdown
# Phase 0: Code Analysis

**Language:** {LANGUAGE}  
**Target:** {TARGET_FILE}

## 🎯 Objective

Analyze {TARGET_FILE} to understand structure, functions, and patterns.

## Tasks

### Task 1: AST Analysis

🛑 EXECUTE-NOW:

```{LANGUAGE_SHELL}
{AST_ANALYSIS_COMMAND}
```

📊 COUNT-AND-DOCUMENT:
- Total functions: [number]
- Total classes: [number]
- Total methods: [number]

### Task 2: Dependency Detection

🛑 EXECUTE-NOW:

```bash
{DEPENDENCY_DETECTION_COMMAND}
```

📊 COUNT-AND-DOCUMENT:
- External dependencies: [list]
- Internal modules: [list]

## Deliverables

- ✅ Complete function inventory
- ✅ Dependency map
- ✅ Mock strategy (if unit path)
```

**Placeholders replaced during creation:**
- `{LANGUAGE}` → "Python" | "JavaScript" | etc.
- `{TARGET_FILE}` → User's actual file
- `{LANGUAGE_SHELL}` → "python" | "node" | etc.
- `{AST_ANALYSIS_COMMAND}` → Language-specific AST command
- `{DEPENDENCY_DETECTION_COMMAND}` → Language-specific import detection

---

## Benefits of This Approach

### 1. Interactive, Not Automated

✅ User weighs in on tooling decisions  
✅ AI confirms choices before creating  
✅ Flexible to project specifics

### 2. Indexed Guidance

✅ AI can search for creation guidance  
✅ Users can search "how to create test workflow"  
✅ Documentation is discoverable

### 3. Clean Search Results

✅ No placeholder confusion  
✅ No template pollution  
❌ Templates not in search results

### 4. Consistent with Meta-Framework

✅ Standards ARE local and indexed  
✅ Used DURING workflow creation  
✅ Follows existing pattern

---

## Final Structure Summary

```
universal/standards/workflow-types/
└── test-generation/
    ├── README.md                    (indexed ✅)
    ├── design/                      (indexed ✅)
    │   ├── overview.md              "What and why"
    │   ├── methodology.md           "8-phase approach"
    │   ├── path-system.md           "Multi-path testing"
    │   ├── creation-process.md      "AI step-by-step"
    │   └── tooling-discovery.md     "How to detect tools"
    ├── language-guides/             (indexed ✅)
    │   ├── README.md
    │   ├── python.md                "Python-specific guidance"
    │   ├── javascript.md
    │   └── typescript.md
    └── templates/                   (NOT indexed ❌)
        ├── README.md                (indexed ✅ - explains templates)
        ├── metadata-template.json
        ├── phase-templates/
        └── task-templates/
```

**AI Usage:**
1. Search and read `design/` and `language-guides/`
2. Discover/confirm tooling interactively with user
3. Use `create_workflow()` with confirmed options
4. MCP tool applies `templates/` behind the scenes
5. Workflow created in user's `.praxis-os/workflows/`

---

**Document End**

**No generator scripts - just indexed knowledge systems that guide interactive AI-driven workflow creation with user confirmation.**

