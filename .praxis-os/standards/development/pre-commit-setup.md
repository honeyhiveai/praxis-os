# Pre-commit Hook Setup - Agent OS Enhanced

**🎯 Automatic quality enforcement before every commit**

## Overview

Pre-commit hooks automatically enforce code quality standards before allowing commits. This prevents quality violations from entering the codebase and ensures consistency across all contributors.

**Paradigm Context**:
- **Python-SDK**: Prototype that proved the AI-assisted development platform
- **Agent OS Enhanced**: Extracted reusable paradigm/framework
- **These standards**: Battle-tested in python-sdk, adapted for Agent OS

**Key Differences from python-sdk**:
- **Documentation**: Uses Docusaurus instead of Sphinx
  - python-sdk: `tox -e docs` builds Sphinx documentation
  - agent-os: `cd docs && npm run build` builds Docusaurus site
  - Pre-commit validates markdown, not builds
- **Scope**: Framework-focused (MCP server, workflows, standards)
- **Testing**: Unit tests only in pre-commit (integration tests optional)
- **Safety**: Credential protection, git safety, workflow validation

## 🚀 Installation

### One-Time Setup

```bash
# 1. Install pre-commit (if not already installed)
pip install pre-commit

# 2. Install the hooks into your git repository
cd /path/to/agent-os-enhanced
pre-commit install

# 3. (Optional) Run on all files to verify setup
pre-commit run --all-files
```

**That's it!** The hooks will now run automatically on every `git commit`.

## 🎯 What Gets Checked

Every commit triggers these checks in sequence:

### Phase 1: Code Formatting (Auto-fix)
```bash
tox -e format  # Black + isort
```
- **Purpose**: Ensure consistent formatting
- **Action**: Auto-fixes code style issues
- **Scope**: mcp_server/, scripts/, tests/

### Phase 2: Static Analysis (Zero Tolerance)
```bash
tox -e lint    # Pylint (≥8.0/10.0, target 10.0/10.0)
tox -e type    # MyPy (ZERO errors required)
```
- **Purpose**: Catch code quality and type safety issues
- **Action**: Blocks commit if violations found
- **Scope**: mcp_server/, scripts/
- **Standards**: 
  - Pylint: Must achieve ≥8.0/10.0 (target: 10.0/10.0)
  - MyPy: ZERO errors allowed (no exceptions)

### Phase 3: Test Execution
```bash
tox -e unit    # All unit tests must pass
```
- **Purpose**: Ensure code changes don't break functionality
- **Action**: Blocks commit if any test fails
- **Scope**: Runs when mcp_server/ or tests/unit/ modified

### Phase 4: Documentation Validation
- **Purpose**: Ensure critical installation files exist
- **Action**: Verifies build_rag_index.py and installation docs present
- **Scope**: installation/, scripts/, .praxis-os/standards/
- **Note**: Agent OS uses Docusaurus for docs (not Sphinx)
  - Docusaurus builds run separately: `cd docs && npm run build`
  - Pre-commit validates markdown content only

## 🔧 Usage

### Normal Workflow (Automatic)

```bash
# 1. Make your changes
vim mcp_server/server/factory.py

# 2. Stage changes
git add mcp_server/server/factory.py

# 3. Commit (hooks run automatically)
git commit -m "fix: improve error handling"

# ✅ If all checks pass: Commit succeeds
# ❌ If any check fails: Commit blocked, fix issues
```

### Manual Hook Execution

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run tox-format --all-files
pre-commit run tox-lint --all-files
pre-commit run tox-type --all-files
pre-commit run unit-tests --all-files

# Run hooks on specific files
pre-commit run --files mcp_server/server/factory.py
```

### Bypassing Hooks (NOT RECOMMENDED)

```bash
# Emergency bypass (use with extreme caution)
git commit --no-verify -m "emergency fix"

# ⚠️  WARNING: Bypassing hooks can introduce quality violations
# Only use in genuine emergencies, then immediately run:
pre-commit run --all-files  # Fix violations before pushing
```

## 🐛 Troubleshooting

### Hook Fails: "tox: command not found"

**Problem**: tox not installed or not in PATH

**Solution**:
```bash
pip install tox
# or
pip install -r mcp_server/requirements.txt
```

### Hook Fails: Formatting Issues

**Problem**: Black or isort violations

**Solution**: The format hook auto-fixes issues, but you may need to stage changes:
```bash
# Hooks auto-fix files, but git needs them staged
git add .
git commit -m "your message"
```

### Hook Fails: Pylint Score Too Low

**Problem**: Code has too many pylint violations

**Solution**:
```bash
# Check violations
.tox/lint/bin/pylint mcp_server/your_file.py --score=no

# Fix violations systematically (see code-quality.md)
# Priority: E (errors) → W (warnings) → C (conventions) → R (refactor)

# Re-run to verify
pre-commit run tox-lint --files mcp_server/your_file.py
```

### Hook Fails: MyPy Type Errors

**Problem**: Type checking errors (ZERO tolerance)

**Solution**:
```bash
# Check specific errors
tox -e type -- mcp_server/your_file.py

# Common fixes:
# - Add type annotations to functions
# - Fix type mismatches
# - Use proper generic types

# Must achieve ZERO errors before commit
```

### Hook Fails: Test Failures

**Problem**: Unit tests failing

**Solution**:
```bash
# Run tests with verbose output
tox -e unit -- -vv

# Fix failing tests
# Ensure all assertions pass

# Verify fix
pre-commit run unit-tests --all-files
```

### Hook Runs Too Slowly

**Problem**: Hooks take long time on large commits

**Solution**:
```bash
# Commit smaller, focused changes
# Pre-commit only runs on changed files

# For large refactoring:
# 1. Run tox manually first to catch issues early
tox -e format && tox -e lint && tox -e type && tox -e unit

# 2. Then commit (hooks will be faster)
git commit -m "refactor: improve code quality"
```

## 📊 Quality Standards Enforced

### Formatting
- **Black**: 88-character line length
- **isort**: Black profile, sorted imports
- **Enforcement**: Auto-fix, then verify

### Static Analysis
- **Pylint**: ≥8.0/10.0 (currently 8.33/10.0)
  - Target: 10.0/10.0 for all new code
  - Path: Systematic violation fixing
- **MyPy**: Zero errors (ZERO tolerance)
  - All type errors must be fixed
  - No exceptions or bypasses allowed

### Testing
- **Unit Tests**: 100% pass rate
- **Coverage**: Minimum 60% overall, 80% for new code
- **Speed**: Fast execution (mocked dependencies)

## 🔄 Updating Hooks

### Update Pre-commit Framework
```bash
# Update to latest pre-commit version
pip install --upgrade pre-commit

# Update hook dependencies
pre-commit autoupdate
```

### Update Hook Configuration

Edit `.pre-commit-config.yaml` and run:
```bash
pre-commit install --install-hooks
```

## 🎓 Best Practices

### DO:
- ✅ Run hooks on all files periodically: `pre-commit run --all-files`
- ✅ Fix violations immediately when caught
- ✅ Commit smaller, focused changes
- ✅ Run `tox -e format` before staging to auto-fix issues
- ✅ Aim for perfect scores (Pylint: 10.0/10.0, MyPy: zero errors)

### DON'T:
- ❌ Use `--no-verify` routinely (only for genuine emergencies)
- ❌ Ignore hook failures and force push
- ❌ Disable hooks permanently
- ❌ Commit large changes without running hooks first
- ❌ Bypass MyPy errors (ZERO tolerance policy)

## 📚 Related Documentation

- **Code Quality Standards**: `.praxis-os/standards/development/code-quality.md`
- **Linter Quick Reference**: `.praxis-os/standards/ai-assistant/code-generation/linters/README.md`
- **Testing Standards**: `.praxis-os/standards/development/testing-standards.md`
- **Pre-commit Config**: `.pre-commit-config.yaml`

## 🆘 Getting Help

**Hooks blocking your commit?**

1. **Read the error output** - It tells you exactly what's wrong
2. **Check documentation** - See `.praxis-os/standards/development/code-quality.md`
3. **Run checks manually** - `tox -e format && tox -e lint && tox -e type`
4. **Fix systematically** - Address errors, then warnings, then conventions

**Still stuck?**

The hooks are enforcing quality standards that ensure code reliability. Take time to understand and fix violations rather than bypassing them.

---

**Installed**: Pre-commit hooks actively enforcing quality  
**Standards**: Aligned with HoneyHive python-sdk  
**Non-Negotiable**: Zero MyPy errors, ≥8.0/10.0 Pylint, 100% test pass rate

