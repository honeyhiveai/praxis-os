---
sidebar_position: 2
doc_type: how-to
---

import QualityGatesFlowDiagram from '@site/src/components/QualityGatesFlowDiagram';

# Set Up Quality Gates

Configure pre-commit hooks to enforce code quality automatically - regardless of your programming language.

## The Universal Pattern

**Quality gates implement [adversarial design](../explanation/adversarial-design.md):**

<QualityGatesFlowDiagram />

**Universal benefits:**
- ✅ **Structural enforcement** - Non-compliance blocks commits
- ✅ **Automatic verification** - Tests actually run, not just claimed  
- ✅ **Path of least resistance** - Auto-fix makes compliance easy
- ✅ **Language-agnostic** - Same pattern for Python, Go, Rust, JavaScript, etc.

---

## Prerequisites

- Git repository initialized
- Language-specific tools installed (see your language below)
- Agent OS Enhanced installed (optional, but recommended)

---

## Installation (Universal)

### 1. Install Pre-commit Framework

**All languages use the same framework:**

```bash
pip install pre-commit
```

**Why Python-based?** Pre-commit framework is written in Python, but it manages hooks for ANY language. Think of it as a universal hook manager.

### 2. Install Git Hooks

```bash
pre-commit install
```

This creates `.git/hooks/pre-commit` that runs your language-specific checks.

**Output:**
```
pre-commit installed at .git/hooks/pre-commit
```

---

## Language-Specific Configuration

Choose your language below. All follow the same pattern: **Format → Lint → Type Check → Test**.

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs groupId="programming-language">
  <TabItem value="python" label="Python" default>

### Python Setup

**Tools:** Black, isort, Pylint, MyPy, pytest

**Install tools:**
```bash
pip install black isort pylint mypy pytest
```

**Create `.pre-commit-config.yaml`:**

```yaml
# Pre-commit hooks for Python projects
fail_fast: true

repos:
  # Phase 1: Formatting (Auto-fix)
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        args: ['--line-length=88']
        
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ['--profile=black']

  # Phase 2: Linting
  - repo: local
    hooks:
      - id: pylint
        name: Pylint
        entry: pylint
        language: system
        types: [python]
        args: ['--fail-under=8.0']

  # Phase 3: Type Checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  # Phase 4: Testing
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        types: [python]
        args: ['tests/', '-v']
        pass_filenames: false
        always_run: true
```

**Optional: Create `.pylintrc`** for configuration:

```ini
[MASTER]
fail-under=8.0

[FORMAT]
max-line-length=88

[MESSAGES CONTROL]
disable=
    missing-docstring,
    too-few-public-methods
```

  </TabItem>
  
  <TabItem value="javascript" label="JavaScript/TypeScript">

### JavaScript/TypeScript Setup

**Tools:** Prettier, ESLint, TypeScript, Jest

**Install tools:**
```bash
npm install --save-dev prettier eslint typescript jest @types/jest
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

**Create `.pre-commit-config.yaml`:**

```yaml
# Pre-commit hooks for JavaScript/TypeScript projects
fail_fast: true

repos:
  # Phase 1: Formatting (Auto-fix)
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0-alpha.8
    hooks:
      - id: prettier
        types_or: [javascript, jsx, ts, tsx, json, yaml, markdown]

  # Phase 2: Linting
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: \.[jt]sx?$
        types: [file]
        additional_dependencies:
          - eslint@8.56.0
          - eslint-config-prettier@9.1.0
          - '@typescript-eslint/parser@7.0.0'
          - '@typescript-eslint/eslint-plugin@7.0.0'

  # Phase 3: Type Checking (TypeScript only)
  - repo: local
    hooks:
      - id: tsc
        name: TypeScript Compiler
        entry: npx tsc --noEmit
        language: system
        files: \.(ts|tsx)$
        pass_filenames: false

  # Phase 4: Testing
  - repo: local
    hooks:
      - id: jest
        name: Jest Tests
        entry: npm test
        language: system
        types_or: [javascript, jsx, ts, tsx]
        pass_filenames: false
        always_run: true
```

**Optional: Create `.prettierrc.json`:**

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

  </TabItem>
  
  <TabItem value="go" label="Go">

### Go Setup

**Tools:** gofmt, goimports, golangci-lint, go test

**Install tools:**
```bash
go install golang.org/x/tools/cmd/goimports@latest
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
```

**Create `.pre-commit-config.yaml`:**

```yaml
# Pre-commit hooks for Go projects
fail_fast: true

repos:
  # Phase 1: Formatting (Auto-fix)
  - repo: https://github.com/dnephin/pre-commit-golang
    rev: v0.5.1
    hooks:
      - id: go-fmt
      - id: go-imports

  # Phase 2: Linting
  - repo: https://github.com/golangci/golangci-lint
    rev: v1.59.1
    hooks:
      - id: golangci-lint
        args: ['--fast']

  # Phase 3: Vet (Go's built-in static analysis)
  - repo: https://github.com/dnephin/pre-commit-golang
    rev: v0.5.1
    hooks:
      - id: go-vet

  # Phase 4: Testing
  - repo: local
    hooks:
      - id: go-test
        name: Go Tests
        entry: go test ./...
        language: system
        types: [go]
        pass_filenames: false
        always_run: true

  # Optional: Go Mod Tidy
  - repo: https://github.com/dnephin/pre-commit-golang
    rev: v0.5.1
    hooks:
      - id: go-mod-tidy
```

**Optional: Create `.golangci.yml`:**

```yaml
linters:
  enable:
    - errcheck
    - gosimple
    - govet
    - ineffassign
    - staticcheck
    - unused

run:
  timeout: 5m
```

  </TabItem>
  
  <TabItem value="rust" label="Rust">

### Rust Setup

**Tools:** rustfmt, Clippy, cargo test

**Install tools:**
```bash
rustup component add rustfmt clippy
```

**Create `.pre-commit-config.yaml`:**

```yaml
# Pre-commit hooks for Rust projects
fail_fast: true

repos:
  # Phase 1: Formatting (Auto-fix)
  - repo: https://github.com/doublify/pre-commit-rust
    rev: v1.0
    hooks:
      - id: fmt
        args: ['--manifest-path', 'Cargo.toml', '--all', '--']

  # Phase 2: Linting (Clippy)
  - repo: https://github.com/doublify/pre-commit-rust
    rev: v1.0
    hooks:
      - id: clippy
        args: ['--manifest-path', 'Cargo.toml', '--all-targets', '--all-features', '--', '-D', 'warnings']

  # Phase 3: Type Checking
  - repo: https://github.com/doublify/pre-commit-rust
    rev: v1.0
    hooks:
      - id: cargo-check
        args: ['--manifest-path', 'Cargo.toml', '--all-targets']

  # Phase 4: Testing
  - repo: local
    hooks:
      - id: cargo-test
        name: Cargo Tests
        entry: cargo test
        language: system
        types: [rust]
        pass_filenames: false
        always_run: true
```

**Optional: Create `rustfmt.toml`:**

```toml
max_width = 100
hard_tabs = false
tab_spaces = 4
edition = "2021"
```

  </TabItem>
  
  <TabItem value="ruby" label="Ruby">

### Ruby Setup

**Tools:** RuboCop, RSpec

**Install tools:**
```bash
gem install rubocop
bundle add rspec --group development,test
```

**Create `.pre-commit-config.yaml`:**

```yaml
# Pre-commit hooks for Ruby projects
fail_fast: true

repos:
  # Phase 1 & 2: Formatting + Linting (RuboCop does both)
  - repo: https://github.com/rubocop/rubocop
    rev: v1.64.1
    hooks:
      - id: rubocop
        args: ['--auto-correct', '--display-cop-names']

  # Phase 4: Testing
  - repo: local
    hooks:
      - id: rspec
        name: RSpec Tests
        entry: bundle exec rspec
        language: system
        types: [ruby]
        pass_filenames: false
        always_run: true
```

**Optional: Create `.rubocop.yml`:**

```yaml
AllCops:
  NewCops: enable
  TargetRubyVersion: 3.2

Style/StringLiterals:
  EnforcedStyle: single_quotes

Metrics/MethodLength:
  Max: 20
```

  </TabItem>
  
  <TabItem value="csharp" label="C#/.NET">

### C#/.NET Setup

**Tools:** dotnet format, dotnet test (included with .NET SDK)

**No additional installation needed** - tools come with .NET SDK.

**Create `.pre-commit-config.yaml`:**

```yaml
# Pre-commit hooks for C#/.NET projects
fail_fast: true

repos:
  # Phase 1: Formatting (Auto-fix)
  - repo: local
    hooks:
      - id: dotnet-format
        name: dotnet format
        entry: dotnet format
        language: system
        types: [c#]
        pass_filenames: false

  # Phase 2: Build (includes analyzers)
  - repo: local
    hooks:
      - id: dotnet-build
        name: dotnet build
        entry: dotnet build --configuration Debug
        language: system
        types: [c#]
        pass_filenames: false

  # Phase 4: Testing
  - repo: local
    hooks:
      - id: dotnet-test
        name: dotnet test
        entry: dotnet test --no-build
        language: system
        types: [c#]
        pass_filenames: false
        always_run: true
```

**Optional: Enable code analysis in `.csproj`:**

```xml
<PropertyGroup>
  <AnalysisLevel>latest</AnalysisLevel>
  <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
</PropertyGroup>
```

  </TabItem>
</Tabs>

---

## Testing Your Setup

**Universal command (works for all languages):**

```bash
# Run all hooks on all files
pre-commit run --all-files
```

**Expected output:**
```
Black....................................................................Passed
isort....................................................................Passed
Pylint..................................................................Passed
mypy.....................................................................Passed
pytest...................................................................Passed
```

**If any checks fail:**
- ✅ Read the error message
- ✅ Fix the issue in your code
- ✅ Run `pre-commit run --all-files` again

---

## Universal Pattern Explained

**Notice the pattern across ALL languages:**

| Phase | Purpose | Examples by Language |
|-------|---------|---------------------|
| **1. Format** | Auto-fix style | Black (Python), Prettier (JS), gofmt (Go), rustfmt (Rust) |
| **2. Lint** | Catch bugs | Pylint (Python), ESLint (JS), golangci-lint (Go), Clippy (Rust) |
| **3. Type Check** | Type safety | MyPy (Python), TSC (TypeScript), go vet (Go), cargo check (Rust) |
| **4. Test** | Verify correctness | pytest (Python), Jest (JS), go test (Go), cargo test (Rust) |

**Same philosophy, different tools.** The adversarial design principle is universal.

---

## Common Issues (Language-Independent)

### Hook Fails: "Command not found"

**Problem:** Tool not installed.

**Fix:** Install language-specific tools (see your language tab above).

---

### Quality Check Fails

**Philosophy:** **This is working as designed!** The hook caught real issues before they entered your repository.

**Fix:**
1. Read the error message carefully
2. Fix the issue in your code
3. Stage the fixed files: `git add <files>`
4. Try commit again

**Example:**
```bash
# Pylint fails
Pylint..................................................................Failed
- hook id: pylint
- exit code: 1

your_file.py:10:0: C0114: Missing module docstring (missing-module-docstring)

# Fix: Add docstring to your_file.py
# Stage changes and commit again
```

---

### Tests Fail on Commit

**Problem:** Tests are actually broken.

**Fix:**
```bash
# Run tests locally to see details
pytest tests/ -v              # Python
npm test                      # JavaScript
go test ./...                 # Go
cargo test                    # Rust

# Fix failing tests
# Stage changes and commit again
```

**Philosophy:** The hook saved you from committing broken code!

---

### Bypass (Emergency Only)

```bash
# Skip hooks (NOT RECOMMENDED)
git commit --no-verify
```

**Warning:** Use only if hooks are broken. This defeats the entire purpose of quality gates.

---

## Advanced: Multi-Language Projects

**If your project uses multiple languages:**

```yaml
repos:
  # Python
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        files: '\.py$'
  
  # JavaScript
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0-alpha.8
    hooks:
      - id: prettier
        files: '\.(js|jsx|ts|tsx)$'
  
  # Go
  - repo: https://github.com/dnephin/pre-commit-golang
    rev: v0.5.1
    hooks:
      - id: go-fmt
        files: '\.go$'
```

**Pattern:** Same framework, different hooks based on file extensions.

---

## CI/CD Integration

**Language-independent CI check:**

<Tabs groupId="ci-platform">
  <TabItem value="github" label="GitHub Actions" default>

```yaml
# .github/workflows/quality.yml
name: Quality Gates

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pre-commit
      - run: pre-commit run --all-files
```

  </TabItem>
  
  <TabItem value="gitlab" label="GitLab CI">

```yaml
# .gitlab-ci.yml
quality-gates:
  stage: test
  image: python:3.11
  script:
    - pip install pre-commit
    - pre-commit run --all-files
```

  </TabItem>
  
  <TabItem value="circleci" label="CircleCI">

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  quality-gates:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run: pip install pre-commit
      - run: pre-commit run --all-files

workflows:
  test:
    jobs:
      - quality-gates
```

  </TabItem>
</Tabs>

**Works for any language** because pre-commit manages language-specific tools.

---

## Philosophy: Why This Pattern Works

Read: [Adversarial Design Philosophy](../explanation/adversarial-design.md)

**Core principle:** Make non-compliance structurally impossible, not just discouraged.

**Universal across languages:**
1. **Assume gaming:** AI will claim "tests pass" without running them
2. **Structural enforcement:** Hooks actually run tests, block if failing  
3. **Path of least resistance:** Auto-fix makes compliance automatic
4. **Language-agnostic:** Same pattern, different tools

**Result:** AI naturally does the right thing because it's the only path forward.

---

## Related Documentation

- [Adversarial Design](../explanation/adversarial-design.md) - Universal philosophy
- [Evidence Validation](../reference/workflows.md#evidence-validation-system) - Workflow-level gates
- [CONTRIBUTING.md](../../../CONTRIBUTING.md#quality-enforcement-system) - Agent OS Enhanced's Python example

---

## Next Steps

1. ✅ Choose your language tab above
2. ✅ Install language-specific tools
3. ✅ Create `.pre-commit-config.yaml`
4. ✅ Run `pre-commit install`
5. ✅ Test with `pre-commit run --all-files`
6. ✅ Configure CI to run same checks

**Result:** Code quality enforced automatically, regardless of language.

