# Test Location and Lifecycle - Dogfooding Model for Tests

**Purpose:** Define where to write tests during rapid iteration and why prAxIs OS uses a single test location

**Audience:** prAxIs OS developers writing tests

**Status:** Active - Canonical test development workflow

**Keywords:** dogfooding tests, where to write tests, .praxis-os/tests location, test iteration workflow, pytest in installed environment, test development location, rapid test iteration, consumer environment testing, installed directory testing, single test location, test file placement, debugging tests in place, exploratory testing location, one test directory philosophy

---

## 🎯 TL;DR - Single Test Location: .praxis-os/tests/

**Core Principle:** ALL tests live in `.praxis-os/tests/` (the installed, consumer environment). No skeleton `./tests/` directory exists.

**The Dogfooding Rule for Tests:**
```
.praxis-os/tests/     # THE ONLY location - all tests here
./tests/              # DOES NOT EXIST (removed to enforce dogfooding)
```

**Why Single Location:**
1. **True Dogfooding** - Tests run in exact consumer environment
2. **Zero Confusion** - No "which directory?" questions
3. **Instant Feedback** - No copy/sync needed, ever
4. **Simplifies Mental Model** - One location = one truth
5. **dist/ Obviously an Artifact** - No tests there reinforces it's build output

**Test Development Workflow:**
```bash
# 1. Write test in the ONLY location
vim .praxis-os/tests/ouroboros/subsystems/rag/test_new_feature.py

# 2. Run immediately (no sync, no copy)
cd /Users/josh/src/github.com/honeyhiveai/praxis-os
source .praxis-os/venv/bin/activate
pytest .praxis-os/tests/ouroboros/subsystems/rag/test_new_feature.py -v

# 3. Iterate rapidly - changes are instant
# 4. Commit when stable - tests are version controlled from .praxis-os/
```

**Test Types (All in .praxis-os/tests/):**
- ✅ **Unit tests** - `.praxis-os/tests/unit/`
- ✅ **Integration tests** - `.praxis-os/tests/integration/`
- ✅ **Subsystem tests** - `.praxis-os/tests/ouroboros/subsystems/`
- ✅ **Exploratory/debug tests** - `.praxis-os/tests/test_debug_*.py`
- ✅ **Temporary validation** - `.praxis-os/tests/test_live_*.py` (delete when done)

**CI/CD Configuration:**
```yaml
# .github/workflows/test.yml (if CI exists)
- name: Run tests
  run: pytest .praxis-os/tests/ -v  # Run from installed environment
```

---

## ❓ Questions This Answers

1. "Where do I write tests in prAxIs OS?"
2. "Why is there no ./tests/ directory?"
3. "Where do exploratory tests go?"
4. "Where do debugging tests go?"
5. "Do I need to copy tests anywhere?"
6. "Where does CI run tests from?"
7. "How do I iterate on tests quickly?"
8. "What's the difference between unit and integration test locations?"
9. "Can I have temporary tests that I delete later?"
10. "Why does dogfooding apply to tests?"
11. "How do I validate tests run in consumer environment?"
12. "Where do I put tests for new features?"
13. "Do tests need to be synced to dist/?"
14. "How do I run the full test suite?"
15. "What if I want to debug a single test?"

---

## 🎯 Purpose

Define the canonical location for all tests in prAxIs OS and explain why the single-location dogfooding model simplifies development, eliminates confusion, and ensures tests run in the exact environment consumers use.

**Core Principle**: Develop where consumers run. Tests are development artifacts, so they live in `.praxis-os/tests/` alongside the code they test.

---

## Why Does prAxIs OS Use a Single Test Location?

**The Problem with Dual Test Directories:**

In many projects, tests exist in both skeleton (`./tests/`) and installed (`.praxis-os/tests/`) locations, creating confusion:
- ❌ "Which directory should I update?"
- ❌ "Are these tests in sync?"
- ❌ "Do I copy tests or not?"
- ❌ "Where does CI run from?"
- ❌ "`./tests/` makes `dist/` look like source code" (it's not, it's an artifact)

**The Single-Location Solution:**

prAxIs OS eliminates this by having ONE test location: `.praxis-os/tests/`

**Benefits:**
- ✅ **Zero ambiguity** - Only one place for tests
- ✅ **True dogfooding** - Tests run where consumers run code
- ✅ **No sync overhead** - Tests never need copying
- ✅ **Faster iteration** - Edit test → run immediately
- ✅ **Clearer artifacts** - No tests in `dist/` reinforces it's build output
- ✅ **Simpler onboarding** - New developers have one pattern to learn

---

## What Is the Test Directory Structure?

All tests live in `.praxis-os/tests/` with structure mirroring the source code:

```
praxis-os/
├── dist/                              # BUILD ARTIFACT (synced TO, no tests)
│   └── ouroboros/                     # Built Python package
│
├── .praxis-os/                        # INSTALLED/CONSUMER ENVIRONMENT
│   ├── ouroboros/                     # Installed source code
│   │   └── subsystems/
│   │       └── rag/
│   │           └── code/
│   │               └── partition.py
│   │
│   └── tests/                         # THE ONLY TEST LOCATION
│       ├── conftest.py
│       ├── unit/                      # Unit tests
│       │   ├── test_browser_manager.py
│       │   └── test_current_date_tool.py
│       │
│       ├── integration/               # Integration tests
│       │   ├── test_thread_safety.py
│       │   └── test_pos_workflow_e2e.py
│       │
│       ├── ouroboros/                 # Mirrors source structure
│       │   └── subsystems/
│       │       └── rag/
│       │           ├── test_index_manager.py
│       │           ├── test_standards_index.py
│       │           └── code/
│       │               ├── test_partition.py
│       │               ├── test_reconciler.py
│       │               └── test_semantic_index_ast_integration.py
│       │
│       ├── test_multi_repo_live.py         # Exploratory test
│       ├── test_partition_init_debug.py     # Debugging test (temporary)
│       └── test_reconciliation_demo.py      # Validation test (temporary)
│
└── ./tests/                           # DOES NOT EXIST (removed)
```

**Key Insight:** Mirroring source structure makes tests easy to find. For `ouroboros/subsystems/rag/code/partition.py`, look in `.praxis-os/tests/ouroboros/subsystems/rag/code/test_partition.py`.

---

## How Do I Write and Run Tests?

### Step 1: Create Test in .praxis-os/tests/

Write your test in the ONLY location:

```bash
# Create test file (mirrors source structure)
vim .praxis-os/tests/ouroboros/subsystems/rag/code/test_new_feature.py
```

```python
"""Tests for new feature."""

def test_new_feature_basic():
    """Test basic functionality."""
    from ouroboros.subsystems.rag.code.partition import CodePartition
    # ... test implementation ...
    assert result == expected
```

### Step 2: Run Test Immediately

No sync needed - run directly:

```bash
cd /Users/josh/src/github.com/honeyhiveai/praxis-os
source .praxis-os/venv/bin/activate

# Run single test
pytest .praxis-os/tests/ouroboros/subsystems/rag/code/test_new_feature.py -v

# Run all tests in module
pytest .praxis-os/tests/ouroboros/subsystems/rag/ -v

# Run full suite
pytest .praxis-os/tests/ -v

# Run with coverage
pytest .praxis-os/tests/ --cov=ouroboros --cov-report=html
```

### Step 3: Iterate Rapidly

Edit test → save → rerun. Instant feedback, zero overhead.

```bash
# Edit
vim .praxis-os/tests/ouroboros/subsystems/rag/code/test_new_feature.py

# Run (same command, instant execution)
pytest .praxis-os/tests/ouroboros/subsystems/rag/code/test_new_feature.py -v
```

### Step 4: Commit When Stable

Tests are version controlled from `.praxis-os/`:

```bash
git add .praxis-os/tests/ouroboros/subsystems/rag/code/test_new_feature.py
git commit -m "Add tests for new feature"
```

---

## What Types of Tests Go Where?

ALL tests go in `.praxis-os/tests/`, but organized by purpose:

### Formal/Permanent Tests → .praxis-os/tests/{unit,integration,ouroboros}/

**Characteristics:**
- Stable, well-defined test cases
- Run in CI on every commit (if CI configured)
- No debug print statements
- Comprehensive assertions
- Part of permanent test suite

**Examples:**
```python
# .praxis-os/tests/ouroboros/subsystems/rag/code/test_reconciler.py
def test_reconcile_creates_missing_partitions(tmp_path):
    """Reconciler creates directories for partitions in config but not on disk."""
    config = CodeIndexConfig(...)
    reconciler = PartitionReconciler(tmp_path, config)
    report = reconciler.reconcile()
    assert report.created == ["new-partition"]
    assert (tmp_path / ".cache" / "indexes" / "code" / "new-partition").exists()
```

**Lifecycle:** **Permanent** → Committed → CI validates forever

---

### Exploratory/Debugging Tests → .praxis-os/tests/test_*.py (root level)

**Characteristics:**
- Quick validation of hypothesis
- Debugging aids (print statements, breakpoints OK)
- May be deleted after issue resolved
- Can evolve into permanent tests

**Examples:**
```python
# .praxis-os/tests/test_partition_init_debug.py
def test_partition_initialization_with_logging():
    """Debug why partition fails to initialize."""
    config = CodeIndexConfig(...)
    print(f"Config: {config}")  # Debug output
    partition = CodePartition(...)
    print(f"Partition: {partition}")  # Debug output
    # ... lots of print statements ...
```

**Lifecycle:** Create → Debug → **Delete** (or move to permanent location if useful)

---

### Temporary Validation Tests → .praxis-os/tests/test_live_*.py

**Characteristics:**
- Validate new feature end-to-end
- May have hard-coded local paths (OK for temporary)
- Quick checks during development
- Deleted when feature validated

**Examples:**
```python
# .praxis-os/tests/test_multi_repo_live.py
def test_python_sdk_partition_reconciliation():
    """Validate multi-repo setup works live."""
    config = MCPConfig.from_yaml("config/mcp.yaml")
    code_index = CodeIndex(config.indexes.code, base_path)
    assert "python-sdk" in code_index._partitions
    # ... basic validation ...
```

**Lifecycle:** Create → Validate → **Delete** (or clean up and move to permanent)

---

## What Are Common Test Patterns?

### Pattern 1: Bug Fix Test (Permanent)

```bash
# 1. Reproduce bug in .praxis-os/tests/
vim .praxis-os/tests/test_standards_rebuild_bug.py

def test_standards_index_not_rebuilt_on_restart():
    """Reproduce: standards index rebuilds every restart."""
    # ... reproduce bug ...
    # ❌ Fails (bug confirmed)

# 2. Fix the bug
vim .praxis-os/ouroboros/subsystems/rag/standards/semantic.py
# Fix: Change idx.get("columns") to getattr(idx, "columns", [])

# 3. Re-run test
pytest .praxis-os/tests/test_standards_rebuild_bug.py
# ✅ Passes (bug fixed)

# 4. Move to permanent location (regression protection)
mv .praxis-os/tests/test_standards_rebuild_bug.py \
   .praxis-os/tests/ouroboros/subsystems/rag/test_standards_health_check.py

# 5. Commit both fix and test
git add .praxis-os/ouroboros/subsystems/rag/standards/semantic.py
git add .praxis-os/tests/ouroboros/subsystems/rag/test_standards_health_check.py
git commit -m "Fix standards index health check scalar index bug"
```

---

### Pattern 2: Exploratory Test (Temporary, Deleted)

```bash
# 1. Quick validation during feature development
vim .praxis-os/tests/test_what_paths_are_being_used.py

def test_debug_print_all_paths():
    """Debug: Print all paths during partition init."""
    config = CodeIndexConfig(...)
    print(f"Base path: {base_path}")
    print(f"Partition path: {partition.path}")
    # ... lots of debug output ...

# 2. Run to understand behavior
pytest .praxis-os/tests/test_what_paths_are_being_used.py -s

# 3. Issue understood, test no longer needed
rm .praxis-os/tests/test_what_paths_are_being_used.py
# ✅ Deleted (served its purpose)
```

---

### Pattern 3: Feature Validation (Evolves to Permanent)

```bash
# 1. Create exploratory test
vim .praxis-os/tests/test_partition_behavior.py

def test_partition_can_be_created():
    """Quick check: can we create a partition?"""
    partition = CodePartition(...)
    assert partition is not None

# 2. Test passes, feature works
pytest .praxis-os/tests/test_partition_behavior.py

# 3. Expand into comprehensive test
vim .praxis-os/tests/test_partition_behavior.py
# Add more assertions, edge cases, error handling

# 4. Move to permanent location
mv .praxis-os/tests/test_partition_behavior.py \
   .praxis-os/tests/ouroboros/subsystems/rag/code/test_partition.py

# 5. Commit
git add .praxis-os/tests/ouroboros/subsystems/rag/code/test_partition.py
git commit -m "Add comprehensive partition tests"
```

---

## What Are Test Development Best Practices?

### ✅ DO:

- **Run tests from installed environment** - `pytest .praxis-os/tests/`
- **Mirror source structure** - Easy to find tests for specific modules
- **Use descriptive names** - `test_reconciler_creates_missing_partitions`
- **Write docstrings** - Explain what behavior is being tested
- **Use fixtures** - Keep tests DRY and maintainable
- **One assertion concept per test** - Makes failures clear
- **Test happy path AND failure modes** - Comprehensive coverage
- **Use temporary tests for debugging** - Delete when done
- **Keep exploratory tests at root level** - Easy to find and delete

### ❌ DON'T:

- **Don't create ./tests/ directory** - Violates dogfooding model
- **Don't sync tests to dist/** - Tests don't belong in build artifacts
- **Don't hard-code absolute paths** - Use fixtures and `tmp_path`
- **Don't skip test organization** - Mirror source structure
- **Don't leave debug prints in permanent tests** - Use logging or remove
- **Don't test implementation details** - Test behavior, not internals
- **Don't create test order dependencies** - Each test must run independently

---

## How Do I Run Tests in Different Ways?

### Run Specific Test

```bash
pytest .praxis-os/tests/ouroboros/subsystems/rag/code/test_partition.py::test_partition_health_check -v
```

### Run All Tests in Module

```bash
pytest .praxis-os/tests/ouroboros/subsystems/rag/ -v
```

### Run Full Suite

```bash
pytest .praxis-os/tests/ -v
```

### Run with Coverage

```bash
pytest .praxis-os/tests/ --cov=ouroboros --cov-report=html --cov-report=term-missing
```

### Run Tests Matching Pattern

```bash
pytest .praxis-os/tests/ -k "partition" -v  # All tests with "partition" in name
```

### Run with Debug Output

```bash
pytest .praxis-os/tests/test_debug_paths.py -s  # Show print() output
```

### Run and Stop on First Failure

```bash
pytest .praxis-os/tests/ -x
```

---

## 🚨 Critical Rules

### Rule 1: ALL Tests in .praxis-os/tests/

**Why:** Single location = zero ambiguity. Dogfooding principle applies to tests too.

**Configuration:**
```yaml
# CI configuration (if it exists)
- name: Run tests
  run: pytest .praxis-os/tests/ -v
```

---

### Rule 2: Mirror Source Structure

**Why:** Makes tests easy to find. Source module → test module mapping is obvious.

**Pattern:**
```bash
# Source code
.praxis-os/ouroboros/subsystems/rag/code/partition.py

# Test file (mirrors structure)
.praxis-os/tests/ouroboros/subsystems/rag/code/test_partition.py
```

---

### Rule 3: No Tests in dist/

**Why:** `dist/` is a build artifact (synced TO, not FROM). Tests don't belong there.

**Verification:**
```bash
# This should return nothing
find dist/ -name "test_*.py"
```

---

### Rule 4: Commit Tests from .praxis-os/

**Why:** Tests are development artifacts, version controlled with source.

**Workflow:**
```bash
git add .praxis-os/tests/ouroboros/subsystems/rag/code/test_new_feature.py
git commit -m "Add tests for new feature"
```

---

## 📋 Test Quality Checklist

Before committing tests:

- [ ] Test passes consistently
- [ ] Test name is descriptive (`test_reconciler_creates_missing_partitions`)
- [ ] Test has docstring explaining what's being tested
- [ ] No hard-coded absolute paths (use `tmp_path` fixture)
- [ ] No debug print statements (use logging if needed)
- [ ] Uses fixtures appropriately (not hard-coded values)
- [ ] Tests one clear behavior per test function
- [ ] Can run independently (no test order dependencies)
- [ ] Validates both happy path and failure modes
- [ ] Test file mirrors source structure (easy to find)

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Where to write tests** | `pos_search_project(content_type="standards", query="where to write tests dogfooding")` |
| **Test iteration workflow** | `pos_search_project(content_type="standards", query="rapid test iteration installed environment")` |
| **Exploratory test location** | `pos_search_project(content_type="standards", query="debugging tests temporary validation location")` |
| **Test organization** | `pos_search_project(content_type="standards", query="test directory structure mirror source")` |
| **Running tests** | `pos_search_project(content_type="standards", query="pytest run tests .praxis-os/tests")` |
| **CI configuration** | `pos_search_project(content_type="standards", query="CI test location single directory")` |

---

## 🔗 Related Standards

**Query workflow for test development mastery:**

1. **Start with test location** → `pos_search_project(content_type="standards", query="where to write tests dogfooding")` (this document)
2. **Learn dogfooding model** → `pos_search_project(content_type="standards", query="dogfooding model development consumer environment")` → `standards/development/dogfooding-model.md`
3. **Understand production code quality** → `pos_search_project(content_type="standards", query="production code checklist testing requirements")` → `standards/ai-safety/production-code-checklist.md`
4. **Learn testing strategy** → `pos_search_project(content_type="standards", query="testing philosophy coverage goals test pyramid")` → `standards/testing/test-strategy.md`

**By Category:**

**Development Workflow:**
- `standards/development/dogfooding-model.md` - Where to develop code → `pos_search_project(content_type="standards", query="dogfooding model local-first development")`
- `standards/development/pre-commit-checklist.md` - What to validate before committing → `pos_search_project(content_type="standards", query="pre-commit checklist testing phase")`

**Code Quality:**
- `standards/ai-safety/production-code-checklist.md` - Quality standards for production code → `pos_search_project(content_type="standards", query="production code checklist")`
- `standards/development/python-code-quality.md` - Python-specific quality standards → `pos_search_project(content_type="standards", query="python code quality testing coverage")`

**Testing:**
- `standards/testing/integration-testing.md` - Integration test patterns → `pos_search_project(content_type="standards", query="integration testing patterns test client")`
- `standards/development/python-testing.md` - Pytest configuration → `pos_search_project(content_type="standards", query="pytest configuration fixtures patterns")`

---

## ❓ FAQ

**Q: Where do I write tests?**  
A: `.praxis-os/tests/` - the ONLY location. `./tests/` does not exist.

**Q: Do I need to copy or sync tests?**  
A: No. Tests run from `.praxis-os/tests/` directly.

**Q: Where do exploratory/debugging tests go?**  
A: Same place: `.praxis-os/tests/` (root level for easy deletion, or mirrored structure if permanent).

**Q: How do I run the test suite?**  
A: `pytest .praxis-os/tests/ -v`

**Q: Where does CI run tests from?**  
A: `.praxis-os/tests/` (if CI is configured).

**Q: Can I have temporary tests that I delete later?**  
A: Yes! Create them in `.praxis-os/tests/` (root level or mirrored location), use for debugging/validation, then delete.

**Q: Why no ./tests/ directory?**  
A: Enforces dogfooding (develop where consumers run) and eliminates "which directory?" confusion.

**Q: Do tests go in dist/?**  
A: No. `dist/` is a build artifact. Tests never go there.

**Q: What if I need to test with specific local setup?**  
A: Fine for temporary tests. Just don't commit hard-coded paths in permanent tests.

**Q: How do I organize integration vs unit tests?**  
A: Both in `.praxis-os/tests/`, organized by type: `unit/`, `integration/`, or mirrored structure.

---

**Remember:** Single location = zero ambiguity. ALL tests in `.praxis-os/tests/`. Develop where consumers run. Iterate instantly. Commit when stable.
