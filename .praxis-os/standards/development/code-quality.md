# Code Quality Standards - Agent OS Enhanced

**🎯 Comprehensive code quality requirements for Agent OS Enhanced**

This document defines the mandatory code quality standards, tools, and processes that ensure consistent, maintainable, and reliable code across the project.

## 🚨 MANDATORY Quality Gates

**All code MUST pass these quality gates before commit:**

### 1. Formatting (100% Compliance Required)
```bash
tox -e format        # Must pass 100%
```

**Tools and Configuration:**
- **Black**: 88-character line length, automatic formatting
- **isort**: Black profile, automatic import sorting
- **Configuration**: Defined in `pyproject.toml`

### 2. Static Analysis (≥10.0/10.0 Target)
```bash
tox -e lint          # Target: ≥10.0/10.0 pylint score
tox -e type          # Zero mypy errors (ENFORCED)
```

**Current Status:**
- **Pylint Score**: 8.33/10.0 (Target: 10.0/10.0)
- **MyPy Errors**: Zero errors required (MANDATORY)
- **Path to 10.0**: Systematic violation fixing using `.praxis-os/standards/` guides

**Tools and Requirements:**
- **pylint**: Target 10.0/10.0 score (currently enforcing ≥8.0/10.0)
- **mypy**: Zero errors allowed (STRICTLY ENFORCED)
- **Configuration**: Defined in `pyproject.toml`

### 3. Testing (100% Pass Rate Required)
```bash
tox -e unit          # All unit tests must pass
tox -e integration   # All integration tests must pass
```

**Testing Requirements:**
- **Unit Tests**: Fast, isolated, mocked dependencies
- **Integration Tests**: Real dependencies, end-to-end validation
- **Coverage**: Minimum 60% overall, 80% for new features

## 🔧 Development Workflow

### Pre-commit Validation

**Before every commit, AI assistants MUST run:**

```bash
# 1. Format code (auto-fix)
tox -e format

# 2. Lint check (must pass ≥8.0/10.0, target 10.0/10.0)
tox -e lint

# 3. Type check (ZERO errors allowed - MANDATORY)
tox -e type

# 4. Run tests (all must pass)
tox -e unit
tox -e integration  # If modifying integration points
```

### Manual Quality Verification

**Local development commands:**

```bash
# Quick quality check
tox -e format && tox -e lint && tox -e type

# Full quality validation
tox -e format && tox -e lint && tox -e type && tox -e unit

# Check current pylint score
.tox/lint/bin/pylint mcp_server/ scripts/ --score=yes

# Check mypy errors (must be zero)
tox -e type
```

## 📊 Code Quality Metrics

### Pylint Scoring Requirements

**Target scores by component:**

- **Core modules** (`mcp_server/`): Target ≥10.0/10.0 (currently 8.33/10.0)
- **Scripts** (`scripts/`): Target ≥10.0/10.0
- **Test modules** (`tests/`): Target ≥10.0/10.0

**Improvement Path:**
1. Fix all `E` (Error) violations first
2. Fix all `W` (Warning) violations systematically
3. Fix `C` (Convention) violations for style
4. Address `R` (Refactor) suggestions last

### Common Violations to Fix

**Priority 1 - Errors (E):**
- E0401: import-error (handled by dependencies)
- E1137: unsupported-assignment-operation

**Priority 2 - Warnings (W):**
- W1203: logging-fstring-interpolation (use lazy % formatting)
- W0707: raise-missing-from (add `from e` to exceptions)
- W0611: unused-import (remove unused imports)
- W0613: unused-argument (prefix with `_` or remove)
- W0718: broad-exception-caught (catch specific exceptions)
- W1514: unspecified-encoding (add `encoding='utf-8'`)
- W1510: subprocess-run-check (add `check=True`)

**Priority 3 - Conventions (C):**
- C0301: line-too-long (use Black formatting)
- C0415: import-outside-toplevel (move to top when possible)
- C0303: trailing-whitespace (use Black)

**Priority 4 - Refactor (R):**
- R0913/R0917: too-many-arguments (use keyword-only args)
- R0902: too-many-instance-attributes (refactor classes)
- R0914: too-many-locals (break into smaller functions)
- R1705: no-else-return (simplify control flow)

### Test Coverage Requirements

**Coverage targets:**

- **Unit Tests**: ≥80% line coverage for new code
- **Integration Tests**: ≥60% line coverage overall
- **Combined Coverage**: ≥60% overall
- **Critical Paths**: 100% coverage for error handling

## 🛠️ Quality Tools Configuration

### Black Configuration
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311', 'py312', 'py313']
```

### isort Configuration  
```toml
# pyproject.toml
[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
```

### Pylint Configuration
```toml
# pyproject.toml
[tool.pylint.format]
max-line-length = 88

[tool.pylint.design]
max-args = 5
max-locals = 15
max-branches = 12
max-statements = 50
max-attributes = 7
```

## 🚫 Quality Violations

### Automatic Failures

**These violations cause CI/CD failure:**

- **Formatting**: Any Black or isort violations
- **Linting**: Pylint score below 8.0/10.0 (target: 10.0/10.0)
- **Type Checking**: ANY mypy errors (ZERO tolerance)
- **Test Failures**: Any failing unit or integration tests

### Code Review Blockers

**These issues block code review approval:**

- **Any mypy errors** (ZERO tolerance - must be fixed)
- **Missing type annotations** on public functions/classes
- **Missing error handling** in critical paths
- **Untested code paths** in new features
- **Hardcoded values** without configuration
- **Security violations** (credentials, unsafe operations)

## 📈 Quality Improvement Process

### Continuous Improvement

**Path to 10.0/10.0 Pylint Score:**

1. **Phase 1**: Fix all Error (E) violations
2. **Phase 2**: Fix all Warning (W) violations  
3. **Phase 3**: Fix Convention (C) violations
4. **Phase 4**: Address Refactor (R) suggestions

**Current Focus**: Systematic violation fixing in mcp_server/ and scripts/

### Technical Debt Management

**Systematic debt reduction:**

- **Track**: Monitor pylint score trend (currently 8.33/10.0)
- **Prioritize**: Fix high-impact violations first (errors, then warnings)
- **Prevent**: All new code must achieve ≥10.0/10.0
- **Measure**: Weekly pylint score reviews

## 🔍 Quality Validation Commands

### Local Development
```bash
# Quick quality check
tox -e format && tox -e lint && tox -e type

# Full quality validation  
tox -e format && tox -e lint && tox -e type && tox -e unit && tox -e integration

# Check specific file (pylint)
.tox/lint/bin/pylint mcp_server/server/factory.py --score=no

# Check specific file (mypy - must be zero errors)
tox -e type -- mcp_server/server/factory.py

# Get detailed violations
.tox/lint/bin/pylint mcp_server/ --score=yes --output-format=text
```

### CI/CD Pipeline
```bash
# Parallel execution for speed
tox -p auto -e format,lint,type,unit,integration

# Python version compatibility
tox -e py311,py312,py313

# CRITICAL: Type checking MUST pass (zero errors)
tox -e type || exit 1
```

## 🆘 Quality Troubleshooting

### Common Issues and Solutions

**Pylint score too low:**
```bash
# Get detailed report by category
.tox/lint/bin/pylint mcp_server/ --score=yes | grep "^[EWCR][0-9]"

# Focus on errors first
.tox/lint/bin/pylint mcp_server/ --disable=all --enable=error,fatal
```

**Black/isort conflicts:**
```bash
# Use tox environment versions (not system versions)
.tox/format/bin/black mcp_server/ scripts/
.tox/format/bin/isort mcp_server/ scripts/
```

**Test failures:**
```bash
# Run with verbose output
tox -e unit -- -vv

# Run specific test
tox -e unit -- tests/unit/test_specific.py::test_function
```

## 🎯 AI Assistant Requirements

**When generating or modifying code, AI assistants MUST:**

1. **Read standards first**: Review `.praxis-os/standards/` before coding
2. **Run quality checks**: Execute `tox -e format && tox -e lint && tox -e type` immediately after changes
3. **Fix ALL violations**: 
   - Address all pylint violations before committing
   - Fix ALL mypy errors (ZERO tolerance - no exceptions)
4. **Aim for perfection**: 
   - Pylint: 10.0/10.0 for all new code
   - MyPy: Zero errors (MANDATORY)
5. **Test thoroughly**: Ensure all tests pass with good coverage

## 📚 Related Standards

- **Linter-Specific Rules**: `.praxis-os/standards/ai-assistant/code-generation/linters/README.md`
- **Testing Standards**: `.praxis-os/standards/development/testing-standards.md`
- **Python Standards**: `.praxis-os/standards/coding/python-standards.md`

---

**Current Status**: 
- **Pylint**: 8.33/10.0 → Target: 10.0/10.0  
- **MyPy**: Zero errors required (ENFORCED)
- **Tests**: All passing

**Next Review**: Weekly score checks and systematic violation fixing  
**Maintained By**: AI assistants following Agent OS standards  
**Non-Negotiable**: Zero mypy errors at all times

