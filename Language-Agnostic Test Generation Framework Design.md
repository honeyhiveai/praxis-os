# Language-Agnostic Test Generation Framework Design

**Document Version:** 1.0  
**Date:** October 9, 2025  
**Author:** Agent OS Framework Design  
**Status:** Design Specification

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Design Philosophy](#design-philosophy)
3. [Architecture Overview](#architecture-overview)
4. [Universal Standards (Language-Agnostic)](#universal-standards-language-agnostic)
5. [Language-Specific Instructions](#language-specific-instructions)
6. [Workflow Construction Pattern](#workflow-construction-pattern)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Example Instantiations](#example-instantiations)

---

## 1. Executive Summary

### Problem Statement

The V3 Test Generation Framework achieves 80%+ success rates for **Python** but is tightly coupled to Python-specific tooling (AST parsing, pytest, pylint, black). Organizations need test generation across multiple languages (JavaScript, Go, Java, Rust, TypeScript, C#) without duplicating the entire framework.

### Solution Design

Create a **three-layer architecture**:

```
Layer 1: Universal Test Generation Standards (Language-Agnostic)
    ↓
Layer 2: Language-Specific Instructions (Tooling & Patterns)
    ↓
Layer 3: Generated Workflow (Language-Specific, Project-Aware)
```

### Key Innovation

**Separation of Concerns:**
- **What to analyze** (universal) vs **How to analyze** (language-specific)
- **Test methodology** (universal) vs **Test frameworks** (language-specific)
- **Quality principles** (universal) vs **Quality tools** (language-specific)

### Success Metrics

- ✅ Single set of universal standards for all languages
- ✅ Language-specific instructions for 7+ languages
- ✅ 80%+ first-run success rate per language
- ✅ Automated workflow generation for detected languages
- ✅ <100 line file constraints maintained

---

## 2. Design Philosophy

### Core Principles

#### Principle 1: Universal Methodology, Language-Specific Tooling

```yaml
Universal (What):
  - "Analyze function signatures and parameters"
  - "Detect attribute access patterns"
  - "Map dependency graph"
  - "Plan branch coverage"

Language-Specific (How):
  Python:
    - "Use ast.parse() to extract function signatures"
    - "Use ast.walk() for attribute detection"
  JavaScript:
    - "Use @babel/parser to parse AST"
    - "Use espree for node traversal"
  Go:
    - "Use go/parser to parse syntax tree"
    - "Use go/ast for traversal"
```

#### Principle 2: Test Methodology is Universal

```yaml
Universal_Test_Concepts:
  unit_testing:
    - "Isolate code under test"
    - "Mock external dependencies"
    - "Verify behavior in isolation"
  
  integration_testing:
    - "Test component interactions"
    - "Use real dependencies"
    - "Verify end-to-end flows"
  
  coverage_principles:
    - "Branch coverage for all conditionals"
    - "Edge case identification"
    - "Error path testing"
  
  quality_gates:
    - "100% test pass rate"
    - "Static analysis with zero errors"
    - "Consistent formatting"
    - "Type safety validation"
```

#### Principle 3: Eight-Phase Analysis is Universal

```yaml
Phase_Methodology:
  phase_0: "Environment setup and path selection"
  phase_1: "Method/function verification"
  phase_2: "Logging/output analysis"
  phase_3: "Dependency mapping"
  phase_4: "Usage pattern analysis"
  phase_5: "Coverage planning"
  phase_6: "Pre-generation validation"
  phase_7: "Test generation and metrics"
  phase_8: "Quality enforcement"

# Each phase WHAT is universal
# Each phase HOW is language-specific
```

#### Principle 4: Quality Standards are Universal

```yaml
Universal_Quality_Targets:
  test_execution:
    requirement: "100% pass rate"
    rationale: "Generated tests must work"
  
  static_analysis:
    requirement: "Perfect score (language-specific scale)"
    rationale: "Consistent code quality"
  
  type_safety:
    requirement: "Zero type errors"
    rationale: "Type correctness validation"
  
  formatting:
    requirement: "100% compliant with formatter"
    rationale: "Consistent style"
  
  coverage:
    unit_tests: "90%+ line and branch"
    integration_tests: "Functional flow coverage"
```

---

## 3. Architecture Overview

### Three-Layer System

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Universal Standards (Language-Agnostic)           │
│  Location: universal/standards/testing/                     │
│                                                              │
│  - test-generation-methodology.md                           │
│  - analysis-phase-framework.md                              │
│  - path-system-standards.md (unit vs integration)           │
│  - quality-gate-requirements.md                             │
│  - evidence-tracking-standards.md                           │
│  - coverage-planning-principles.md                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Language-Specific Instructions                    │
│  Location: language-instructions/                           │
│                                                              │
│  - python-test-generation.md                                │
│  - javascript-test-generation.md                            │
│  - go-test-generation.md                                    │
│  - java-test-generation.md                                  │
│  - typescript-test-generation.md                            │
│  - rust-test-generation.md                                  │
│  - csharp-test-generation.md                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Generated Workflow (Language + Project Specific)  │
│  Location: .agent-os/workflows/test_generation_{lang}_v1/   │
│                                                              │
│  Generated by LLM using:                                     │
│  - Universal standards (Layer 1)                            │
│  - Language instructions (Layer 2)                          │
│  - Detected project patterns (runtime analysis)             │
└─────────────────────────────────────────────────────────────┘
```

### File Organization

```
universal/standards/testing/
├── README.md                              # Overview
├── test-generation/
│   ├── methodology.md                     # 8-phase overview
│   ├── phase-0-setup.md                   # Universal setup
│   ├── phase-1-function-analysis.md       # Function/method analysis
│   ├── phase-2-output-analysis.md         # Logging/output patterns
│   ├── phase-3-dependency-analysis.md     # Dependency mapping
│   ├── phase-4-usage-patterns.md          # Call pattern analysis
│   ├── phase-5-coverage-planning.md       # Coverage strategy
│   ├── phase-6-validation.md              # Pre-generation checks
│   ├── phase-7-generation.md              # Test generation
│   ├── phase-8-quality-gates.md           # Quality enforcement
│   ├── path-system.md                     # Unit vs integration
│   ├── evidence-tracking.md               # Progress tables
│   └── quality-standards.md               # Quality targets

language-instructions/
├── python-test-generation.md              # Python tooling
├── javascript-test-generation.md          # JS/Jest/Mocha
├── typescript-test-generation.md          # TS + type checking
├── go-test-generation.md                  # Go testing pkg
├── java-test-generation.md                # JUnit/TestNG
├── rust-test-generation.md                # Cargo test
└── csharp-test-generation.md              # xUnit/NUnit
```

---

## 4. Universal Standards (Language-Agnostic)

### 4.1 Test Generation Methodology

**File:** `universal/standards/testing/test-generation/methodology.md`

**Purpose:** Define the universal 8-phase approach to test generation

**Content Structure:**

```markdown
# Test Generation Methodology (Universal)

## Overview

This standard defines the systematic approach to generating high-quality tests for **any programming language**. The methodology consists of 8 sequential phases that build comprehensive understanding before generation.

## Core Principles

### Principle 1: Deep Analysis Before Generation

❌ Surface-level analysis → Incomplete tests → Failures
✅ Deep analysis → Comprehensive tests → Success

### Principle 2: Path-Based Strategies

- **Unit Path**: Mock external dependencies, test in isolation
- **Integration Path**: Real dependencies, end-to-end validation
- Path selected at Phase 0, enforced throughout

### Principle 3: Evidence-Based Progress

- Every phase produces quantified evidence
- Progress tracked in structured tables
- Automated validation with exit codes

## Eight-Phase Framework

### Phase 0: Environment Setup and Path Selection

**Universal Requirements:**
1. Validate development environment
2. Analyze target file complexity
3. Select test path (unit OR integration)
4. Initialize progress tracking

**Language-Specific Implementation:**
- Environment validation commands differ per language
- Complexity metrics use language-specific tools
- See: `language-instructions/{language}-test-generation.md`

### Phase 1: Function/Method Analysis

**Universal Requirements:**
1. Extract all function/method signatures
2. Document parameter lists and types
3. Identify return types
4. Detect attribute/field access patterns
5. Map function call patterns

**Analysis Output:**
- Function inventory with signatures
- Parameter count and types
- All accessed attributes
- Mock completeness requirements (unit path)

**Language-Specific Implementation:**
- Python: AST parsing with ast.parse()
- JavaScript: @babel/parser or espree
- Go: go/parser and go/ast
- See: Phase 1 section in language instructions

### Phase 2: Output Analysis

**Universal Requirements:**
1. Identify all logging/output statements
2. Classify output levels (debug, info, error, etc.)
3. Determine output strategy per path
   - Unit: Mock output to prevent side effects
   - Integration: Use real output for validation

**Language-Specific Implementation:**
- Python: grep for "logger" or AST analysis
- JavaScript: console.log/winston/pino detection
- Go: fmt.Print*/log package analysis

### Phase 3: Dependency Analysis

**Universal Requirements:**
1. Map all external dependencies
2. Map all internal module dependencies
3. Identify configuration dependencies
4. Document I/O dependencies (file, network, database)

**Dependency Strategy:**
- Unit Path: ALL external dependencies mocked
- Integration Path: Real dependencies, selective mocking

**Language-Specific Implementation:**
- Python: import analysis + module inspection
- JavaScript: require()/import analysis
- Go: import path analysis
- Java: import + package analysis

### Phase 4: Usage Pattern Analysis

**Universal Requirements:**
1. Analyze all function call sites
2. Document control flow patterns (if/switch/loops)
3. Map error handling patterns
4. Identify state management patterns

**Language-Specific Implementation:**
- Varies by language syntax and idioms
- See language instructions for parsing strategies

### Phase 5: Coverage Planning

**Universal Requirements:**
1. Identify all conditional branches
2. Plan edge case testing
3. Document error paths
4. Establish coverage targets
   - Unit: 90%+ line and branch coverage
   - Integration: Functional flow coverage

**Language-Specific Implementation:**
- Coverage tools differ per language
- See language instructions for coverage measurement

### Phase 6: Pre-Generation Validation

**Universal Requirements:**
1. Verify all technical prerequisites
2. Validate complete analysis chain (Phases 1-5)
3. Confirm path-specific strategy
4. Prepare quality tool integration

**Language-Specific Implementation:**
- Import/module validation commands
- Signature verification approaches
- See language instructions

### Phase 7: Test Generation and Metrics

**Universal Requirements:**
1. Generate comprehensive test file
2. Execute tests and collect metrics
3. Measure coverage
4. Run static analysis
5. Check formatting

**Language-Specific Implementation:**
- Test framework patterns (pytest, Jest, go test, JUnit)
- Assertion libraries
- Fixture patterns
- See language instructions and templates

### Phase 8: Quality Enforcement

**Universal Requirements:**
1. 100% test pass rate (zero failures)
2. Perfect static analysis score
3. Zero type errors (if typed language)
4. 100% formatter compliance
5. Coverage targets met

**Enforcement:**
- Automated validation script with exit code 0
- Zero tolerance for quality failures
- Language-specific quality tools
- See: quality-gate-requirements.md

## Success Criteria

- ✅ All 8 phases completed with evidence
- ✅ Progress table shows all phases complete
- ✅ Path strategy followed consistently
- ✅ Quality gates passed with automation
- ✅ 80%+ first-run success rate target

## See Also

- [Path System Standards](path-system.md)
- [Evidence Tracking](evidence-tracking.md)
- [Quality Standards](quality-standards.md)
- Language-specific instructions in `/language-instructions/`
```

### 4.2 Path System Standards

**File:** `universal/standards/testing/test-generation/path-system.md`

**Purpose:** Define unit vs integration testing strategies universally

**Content Structure:**

```markdown
# Path System Standards (Universal)

## Overview

The path system provides two distinct testing strategies applicable to **any programming language**:

1. **Unit Path**: Isolation through mocking
2. **Integration Path**: End-to-end validation

## Universal Path Principles

### Unit Testing Path

**Core Strategy:** Isolate code under test by mocking external dependencies

**Universal Characteristics:**
- Mock all external APIs (HTTP, database, file system)
- Mock all external libraries
- Execute real production code
- High determinism
- Fast execution
- 90%+ coverage target

**What Gets Mocked (Universal):**
```yaml
External_APIs:
  - HTTP clients
  - Database connections
  - Message queues
  - External services

External_Libraries:
  - Third-party packages
  - Standard library I/O
  - Time/date functions
  - Random number generators

Configuration:
  - Environment variables
  - Config files
  - Secrets/credentials

I/O_Operations:
  - File system access
  - Network sockets
  - Standard input/output
```

**What Gets Executed (Universal):**
```yaml
Code_Under_Test:
  - All functions/methods being tested
  - Internal logic and algorithms
  - Control flow
  - Error handling
```

**Critical Insight:**
```
❌ WRONG: Mock the function under test → 0% coverage
✅ CORRECT: Mock the dependencies → Execute code → Coverage!
```

### Integration Testing Path

**Core Strategy:** Validate real system interactions end-to-end

**Universal Characteristics:**
- Use real external dependencies
- Validate actual system behavior
- Verify backend integration
- Subject to system state
- Slower execution
- Functional coverage focus

**What Stays Real (Universal):**
```yaml
Real_Dependencies:
  - Actual API clients
  - Real database connections
  - Live external services (test environment)
  - Actual message queues

Real_Configuration:
  - Test environment configs
  - Test credentials
  - Real connection strings

Real_I/O:
  - Actual file operations (test directories)
  - Real network calls
```

**What Gets Mocked (Minimal):**
```yaml
Test_Specific:
  - Test data generation
  - Cleanup helpers
  - Time manipulation (sometimes)
```

## Path Selection Decision Tree

```yaml
Choose_Unit_When:
  - Testing single module/class
  - Need fast feedback
  - Require high determinism
  - Want coverage metrics
  - External dependencies costly/slow

Choose_Integration_When:
  - Testing multiple components
  - Need end-to-end validation
  - Verifying API contracts
  - System behavior critical
  - Backend verification required
```

## Path Enforcement

### Phase 0: Path Lock

- Path selected at Phase 0
- Selection documented in progress table
- **Cannot change mid-execution**
- All subsequent phases follow selected path

### Violation Detection

```yaml
Path_Mixing_Violations:
  indicator: "Unit mocks in integration test"
  response: "🚨 FRAMEWORK-VIOLATION - Path locked at Phase 0"
  
  indicator: "Integration fixtures in unit test"
  response: "🚨 FRAMEWORK-VIOLATION - Must use unit mocks"
```

## Language-Specific Mocking

### Mock Patterns by Language

**Python:**
- unittest.mock (Mock, patch, MagicMock)
- pytest-mock
- responses (HTTP mocking)

**JavaScript:**
- Jest mocking
- Sinon.js
- nock (HTTP)

**Go:**
- Interface-based mocking
- gomock
- testify/mock

**Java:**
- Mockito
- EasyMock
- PowerMock

**See:** Language-specific instructions for detailed patterns

## Success Patterns

### Unit Path Success:
```yaml
Analysis: "All dependencies identified"
Strategy: "Complete mock suite prepared"
Generation: "Mocks + real code execution"
Validation: "90%+ coverage achieved"
```

### Integration Path Success:
```yaml
Analysis: "All integration points mapped"
Strategy: "Real dependencies configured"
Generation: "Real calls + backend verification"
Validation: "Functional flows complete"
```

## See Also

- [Test Generation Methodology](methodology.md)
- [Quality Standards](quality-standards.md)
- Language-specific mock patterns in `/language-instructions/`
```

### 4.3 Evidence Tracking Standards

**File:** `universal/standards/testing/test-generation/evidence-tracking.md`

**Purpose:** Define progress tracking and evidence requirements

**Content Structure:**

```markdown
# Evidence Tracking Standards (Universal)

## Overview

Evidence tracking ensures systematic execution and prevents vague claims. Progress is tracked through structured tables updated after each phase.

## Universal Progress Table

### Template Structure

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 0: Setup | ❌ | None | 0/N | Manual | ❌ |
| 1: Function Analysis | ❌ | None | 0/N | Manual | ❌ |
| 2: Output Analysis | ❌ | None | 0/N | Manual | ❌ |
| 3: Dependency Analysis | ❌ | None | 0/N | Manual | ❌ |
| 4: Usage Patterns | ❌ | None | 0/N | Manual | ❌ |
| 5: Coverage Planning | ❌ | None | 0/N | Manual | ❌ |
| 6: Pre-Generation | ❌ | None | 0/N | Manual | ❌ |
| 7: Generation + Metrics | ❌ | None | 0/1 | JSON | ❌ |
| 8: **Quality Gates** | ❌ | None | 0/1 | **EXIT CODE 0** | ❌ |

## Evidence Requirements

### Quantified Evidence (Not Vague)

❌ **Unacceptable Evidence:**
- "Analysis complete"
- "Several functions found"
- "Dependencies identified"
- "Tests passing"

✅ **Acceptable Evidence:**
- "15 functions found: [list signatures]"
- "8 external dependencies: requests, os, sys..."
- "23 attribute accesses detected"
- "Tests: 18/18 passing (100%)"

### Evidence by Phase

**Phase 0:**
```yaml
Required:
  - Environment validation output
  - Target file metrics (lines, functions)
  - Path selection (unit OR integration)
  - Progress table initialized
```

**Phase 1:**
```yaml
Required:
  - Function count with signatures
  - Parameter lists and types
  - Attribute access patterns (count + list)
  - Mock completeness requirements
```

**Phase 2:**
```yaml
Required:
  - Output statement count
  - Output levels identified
  - Path-specific strategy
```

**Phase 3:**
```yaml
Required:
  - External dependency list
  - Internal dependency list
  - Configuration dependency list
  - Mock strategy documented
```

**Phase 4:**
```yaml
Required:
  - Function call pattern count
  - Control flow branch count
  - Error handling pattern count
```

**Phase 5:**
```yaml
Required:
  - Conditional branch count
  - Edge case list
  - Coverage target plan
```

**Phase 6:**
```yaml
Required:
  - Technical prerequisite validation
  - Analysis completeness checklist
  - Path strategy confirmation
```

**Phase 7:**
```yaml
Required:
  - Test execution results (pass/fail counts)
  - Coverage percentage
  - Static analysis score
  - Type checking results
  - Formatting status
```

**Phase 8:**
```yaml
Required:
  - Automated script execution output
  - Exit code (must be 0)
  - All quality gate results
```

## Command Execution Tracking

### Command Count Format

```
Commands: X/Y executed
Where:
  X = Commands executed
  Y = Total commands required
```

### Command Output Requirements

🛑 **PASTE-OUTPUT:** Command results must be pasted, not summarized

Example:
```
✅ Correct:
Command: wc -l src/tracer.py
Output:
  312 src/tracer.py

❌ Wrong:
Command: wc -l src/tracer.py
Output: File has several hundred lines
```

## Status Indicators

### Phase Status

- ❌ Not started
- 🔄 In progress
- ✅ Complete with evidence
- ⚠️ Blocked (with reason)

### Gate Status

- ❌ Not validated
- ⚠️ Validation in progress
- ✅ Passed
- 🚫 Failed (with details)

## Validation Requirements

### Manual Validation (Phases 0-6)

```yaml
Requirements:
  - Evidence documented in table
  - Commands executed with output
  - Findings quantified
  - Ready to proceed to next phase
```

### JSON Validation (Phase 7)

```yaml
Requirements:
  - Structured metrics in JSON format
  - All metrics populated
  - No placeholders
  - See: phase-7-generation.md
```

### Automated Validation (Phase 8)

```yaml
Requirements:
  - Script execution output pasted
  - Exit code explicitly stated
  - Must be exit code 0
  - All gates documented
```

## Violation Detection

### Evidence Gaps

```yaml
Indicator: "Phase marked complete without quantified evidence"
Response: "🚨 EVIDENCE-GAP: Provide specific counts and findings"
```

### Phase Skipping

```yaml
Indicator: "Moving to Phase X without Phase X-1 evidence"
Response: "🚨 FRAMEWORK-VIOLATION: Complete previous phase"
```

### Vague Claims

```yaml
Indicator: "Tests passing" without pass/fail counts
Response: "📊 COUNT-AND-DOCUMENT: Provide exact test counts"
```

## See Also

- [Test Generation Methodology](methodology.md)
- [Quality Standards](quality-standards.md)
- [Command Language](../../../meta-framework/command-language.md)
```

### 4.4 Quality Gate Requirements

**File:** `universal/standards/testing/test-generation/quality-standards.md`

**Purpose:** Define universal quality targets and enforcement

**Content Structure:**

```markdown
# Quality Standards (Universal)

## Overview

Quality standards apply to **all generated tests** regardless of programming language. These are non-negotiable requirements enforced through automated validation.

## Universal Quality Targets

### 1. Test Execution (100% Pass Rate)

**Requirement:**
```yaml
target: "100% test pass rate"
tolerance: "Zero failed tests"
rationale: "Generated tests must work correctly"
```

**Measurement:**
```
All test frameworks report pass/fail counts
Requirement: pass_count == total_count AND fail_count == 0
```

**Language-Specific Frameworks:**
- Python: pytest, unittest
- JavaScript: Jest, Mocha, Jasmine
- Go: go test
- Java: JUnit, TestNG
- Rust: cargo test
- C#: xUnit, NUnit

### 2. Static Analysis (Perfect Score)

**Requirement:**
```yaml
target: "Perfect static analysis score"
tolerance: "Zero warnings/errors"
rationale: "Consistent code quality"
```

**Language-Specific Scales:**
- Python: Pylint 10.0/10
- JavaScript: ESLint 0 errors/warnings
- Go: go vet 0 issues
- Java: CheckStyle 0 violations
- Rust: clippy 0 warnings
- TypeScript: TSLint/ESLint 0 issues
- C#: StyleCop 0 violations

### 3. Type Safety (Zero Type Errors)

**Requirement:**
```yaml
target: "Zero type errors"
tolerance: "None"
rationale: "Type correctness validation"
applicable: "Typed languages and optional typing"
```

**Language-Specific Type Checkers:**
- Python: mypy (if type hints used)
- JavaScript: Flow (if used)
- TypeScript: tsc
- Go: Built-in type system
- Java: javac
- Rust: rustc
- C#: Built-in type system

### 4. Code Formatting (100% Compliant)

**Requirement:**
```yaml
target: "100% formatter compliance"
tolerance: "Zero formatting issues"
rationale: "Consistent style"
```

**Language-Specific Formatters:**
- Python: Black
- JavaScript: Prettier
- Go: gofmt
- Java: google-java-format
- Rust: rustfmt
- TypeScript: Prettier
- C#: dotnet format

### 5. Code Coverage

**Requirements:**
```yaml
unit_tests:
  line_coverage: "90%+ minimum"
  branch_coverage: "90%+ minimum"
  rationale: "Comprehensive testing"

integration_tests:
  requirement: "Functional flow coverage"
  metric: "All integration points validated"
  rationale: "End-to-end validation"
```

**Language-Specific Coverage Tools:**
- Python: coverage.py, pytest-cov
- JavaScript: Istanbul, Jest coverage
- Go: go test -cover
- Java: JaCoCo
- Rust: tarpaulin
- TypeScript: Istanbul, Jest
- C#: coverlet

## Quality Enforcement System

### Phase 8: Automated Validation

**Validation Script:**
```
Language-specific script that:
1. Runs all tests → Checks 100% pass rate
2. Runs static analyzer → Checks perfect score
3. Runs type checker → Checks zero errors
4. Runs formatter → Checks compliance
5. Runs coverage tool → Checks targets

Exit code 0: All gates passed ✅
Exit code 1: One or more gates failed ❌
```

**Script Naming:**
- Python: `validate-python-test-quality.py`
- JavaScript: `validate-javascript-test-quality.js`
- Go: `validate-go-test-quality.sh`
- Etc.

### Zero Tolerance Enforcement

```yaml
🚨 ABSOLUTE REQUIREMENTS:

test_pass_rate: "100% (not 95%, not 99%)"
static_analysis: "Perfect (not 9.5/10)"
type_errors: "0 (not 2, not 'just warnings')"
formatting: "100% (not 'mostly formatted')"
coverage: "90%+ for unit (not 85%)"

🚨 FRAMEWORK-VIOLATION: Declaring success with ANY failure
```

### Quality Gate Output

**Required Format:**
```
=== Quality Validation Results ===

✅ Test Execution: X/X tests passed (100%)
✅ Coverage: X.X% lines, X.X% branches
✅ Static Analysis: {Perfect score in language scale}
✅ Type Checking: 0 errors
✅ Formatting: Compliant

=== ALL QUALITY GATES PASSED ===
Exit code: 0
```

## Failure Remediation

### Failure Categories

**1. Test Failures:**
```yaml
symptom: "Tests failing on execution"
causes:
  - Incorrect mock attributes
  - Wrong function signatures
  - Missing dependencies
  - Logic errors
remediation: "Return to Phase 1-4 analysis"
```

**2. Coverage Failures:**
```yaml
symptom: "Coverage below 90%"
causes:
  - Missing test cases
  - Uncovered branches
  - Edge cases not tested
remediation: "Return to Phase 5 coverage planning"
```

**3. Static Analysis Failures:**
```yaml
symptom: "Linter warnings/errors"
causes:
  - Style violations
  - Code smells
  - Unused imports
remediation: "Fix issues, re-validate"
```

**4. Type Errors:**
```yaml
symptom: "Type checker errors"
causes:
  - Incorrect type annotations
  - Type mismatches
  - Missing type definitions
remediation: "Fix types, re-validate"
```

## Language-Specific Quality Configuration

### Configuration Files

Each language may have quality tool configuration:

**Python:**
- `pyproject.toml`: Black, Pylint, MyPy config
- `.pylintrc`: Pylint settings
- `mypy.ini`: Type checking config

**JavaScript:**
- `.eslintrc`: ESLint rules
- `.prettierrc`: Prettier config
- `jest.config.js`: Jest settings

**Go:**
- `.golangci.yml`: Linter configuration

**See:** Language-specific instructions for configuration details

## Success Metrics

### Target Success Rate

```yaml
framework_target:
  first_run_success: "80%+ per language"
  definition: "Tests pass all quality gates on first execution"
  measurement: "Across diverse modules/projects"
```

### Quality Consistency

```yaml
consistency_target:
  perfect_scores: "100% of successful generations"
  rationale: "Automated validation ensures consistency"
```

## See Also

- [Test Generation Methodology](methodology.md)
- [Phase 8: Quality Enforcement](phase-8-quality-gates.md)
- Language-specific quality tools in `/language-instructions/`
```

---

## 5. Language-Specific Instructions

### 5.1 Instruction Template

**Purpose:** Language-specific instructions tell the LLM **HOW** to apply universal standards to a specific language.

**Template File:** `language-instructions/{language}-test-generation.md`

**Structure:**

```markdown
# {Language} Test Generation Instructions

**For Cursor Agent: When generating tests for {Language}, use these instructions to apply universal test generation standards with {Language}-specific tooling.**

---

## Overview

This document maps **universal test generation standards** to **{Language}-specific implementation**.

### Universal Standards Reference

Read these universal standards:
- `universal/standards/testing/test-generation/methodology.md`
- `universal/standards/testing/test-generation/path-system.md`
- `universal/standards/testing/test-generation/quality-standards.md`

### {Language} Context

This file provides:
- {Language}-specific analysis tools
- {Language} testing frameworks
- {Language} mocking patterns
- {Language} quality tools
- {Language} code examples

---

## Phase 0: Environment Setup ({Language})

### Environment Validation

**Universal Requirement:** Validate development environment

**{Language} Implementation:**

```bash
# Check {Language} installation
{language_version_command}

# Check package manager
{package_manager_command}

# Check build tool
{build_tool_command}

# Verify workspace
pwd
ls -la {relevant_paths}
```

**Example:**
```
$ python --version
Python 3.11.5

$ which pytest
/usr/local/bin/pytest
```

### Target File Analysis

**Universal Requirement:** Analyze target file complexity

**{Language} Implementation:**

```bash
# Line count
wc -l {target_file}

# Function/method count
{language_specific_function_count_command}

# Dependency count
{language_specific_dependency_count_command}
```

### Path Selection

**Universal Requirement:** Select unit OR integration path

**Decision Factors:**
- See universal path-system.md
- {Language}-specific framework availability
- Project testing patterns

---

## Phase 1: Function/Method Analysis ({Language})

### Universal Requirements

From `methodology.md` Phase 1:
1. Extract all function/method signatures
2. Document parameters and types
3. Identify return types
4. Detect attribute/field access
5. Map function calls

### {Language} Implementation

#### AST-Based Signature Extraction

**Tool:** {Language parsing tool}

**Command:**
```{language}
{language_specific_ast_parsing_script}
```

**Example Output:**
```
function_name(param1: Type1, param2: Type2) -> ReturnType at line X
```

#### Attribute Access Detection

**Pattern:** {Language attribute syntax}

**Command:**
```bash
{language_specific_attribute_detection_command}
```

#### Function Call Analysis

**Command:**
```bash
{language_specific_function_call_detection}
```

### Mock Completeness (Unit Path)

**Universal Principle:** All accessed attributes must be mocked

**{Language} Pattern:**
```{language}
{language_specific_mock_attribute_pattern}
```

---

## Phase 2: Output Analysis ({Language})

### Universal Requirements

1. Identify logging/output statements
2. Classify output levels
3. Determine path strategy

### {Language} Implementation

#### Logging Framework Detection

**Common {Language} Logging:**
- {logging_framework_1}
- {logging_framework_2}
- {logging_framework_3}

**Detection Command:**
```bash
{language_specific_logging_detection}
```

#### Output Mocking (Unit Path)

**Pattern:**
```{language}
{language_specific_output_mocking_pattern}
```

---

## Phase 3: Dependency Analysis ({Language})

### Universal Requirements

1. Map external dependencies
2. Map internal dependencies
3. Identify configuration
4. Document I/O dependencies

### {Language} Implementation

#### Import/Dependency Analysis

**Command:**
```bash
{language_specific_import_analysis}
```

#### External vs Internal Classification

**{Language} Conventions:**
- External: {external_dependency_indicators}
- Internal: {internal_dependency_indicators}

#### Mock Strategy (Unit Path)

**External Dependency Mocking:**
```{language}
{language_specific_external_dependency_mock_pattern}
```

**Internal Dependency Handling:**
```{language}
{language_specific_internal_dependency_pattern}
```

---

## Phase 4: Usage Pattern Analysis ({Language})

### {Language}-Specific Patterns

#### Control Flow

**{Language} Conditionals:**
```bash
{language_specific_control_flow_detection}
```

#### Error Handling

**{Language} Error Patterns:**
- {error_pattern_1}
- {error_pattern_2}

**Detection:**
```bash
{language_specific_error_handling_detection}
```

---

## Phase 5: Coverage Planning ({Language})

### Coverage Tool

**{Language} Coverage Tool:** {coverage_tool_name}

**Usage:**
```bash
{coverage_tool_command}
```

**Output Interpretation:**
```
{coverage_output_example}
```

### Branch Identification

**Command:**
```bash
{language_specific_branch_detection}
```

---

## Phase 6: Pre-Generation Validation ({Language})

### Import Validation

**Command:**
```{language}
{language_specific_import_validation}
```

### Signature Verification

**Command:**
```{language}
{language_specific_signature_verification}
```

---

## Phase 7: Test Generation ({Language})

### Testing Frameworks

**Recommended: {primary_test_framework}**

| Framework | Use Case | Status |
|-----------|----------|--------|
| {framework_1} | {use_case_1} | ✅ Recommended |
| {framework_2} | {use_case_2} | ⚠️ Alternative |

### Unit Test Template ({Language})

```{language}
{language_specific_unit_test_template}
```

### Integration Test Template ({Language})

```{language}
{language_specific_integration_test_template}
```

### Assertion Patterns

```{language}
{language_specific_assertion_patterns}
```

### Fixture Patterns

```{language}
{language_specific_fixture_patterns}
```

### Mocking Patterns

#### Mock External APIs

```{language}
{language_specific_api_mocking}
```

#### Mock Database

```{language}
{language_specific_database_mocking}
```

#### Mock File System

```{language}
{language_specific_filesystem_mocking}
```

---

## Phase 8: Quality Enforcement ({Language})

### Quality Tools

**Static Analyzer:** {static_analyzer}
- Command: `{static_analyzer_command}`
- Target: {perfect_score_definition}

**Type Checker:** {type_checker}
- Command: `{type_checker_command}`
- Target: 0 errors

**Formatter:** {formatter}
- Command: `{formatter_command}`
- Target: 100% compliant

**Coverage:** {coverage_tool}
- Command: `{coverage_command}`
- Target: 90%+ for unit

### Validation Script

**Script:** `scripts/validate-{language}-test-quality.{ext}`

```{language}
{validation_script_content}
```

**Usage:**
```bash
{validation_script_usage}
```

**Required Output:**
```
=== Quality Validation Results ===

✅ Test Execution: X/X tests passed (100%)
✅ Coverage: X.X% lines, X.X% branches  
✅ Static Analysis: {perfect_score}
✅ Type Checking: 0 errors
✅ Formatting: Compliant

=== ALL QUALITY GATES PASSED ===
Exit code: 0
```

---

## Project Context Integration

### Framework Detection

**Detect {Language} Frameworks:**
- {framework_1}: Check for {indicator_1}
- {framework_2}: Check for {indicator_2}

### Configuration Files

**Detect:**
- {config_file_1}: {purpose}
- {config_file_2}: {purpose}

**Generate if missing:**
```{language}
{config_file_template}
```

---

## Common Patterns

### {Language}-Specific Test Patterns

#### Pattern 1: {pattern_name}
```{language}
{pattern_code}
```

#### Pattern 2: {pattern_name}
```{language}
{pattern_code}
```

---

## Troubleshooting

### Common Issues

**Issue 1: {common_issue_1}**
- Symptom: {symptom}
- Cause: {cause}
- Solution: {solution}

**Issue 2: {common_issue_2}**
- Symptom: {symptom}
- Cause: {cause}
- Solution: {solution}

---

## See Also

- [Universal Test Generation Methodology](../universal/standards/testing/test-generation/methodology.md)
- [Path System Standards](../universal/standards/testing/test-generation/path-system.md)
- [Quality Standards](../universal/standards/testing/test-generation/quality-standards.md)
```

---

## 6. Workflow Construction Pattern

### 6.1 Automated Workflow Generation

**Process:**

```yaml
Step_1_Language_Detection:
  input: "Target project directory"
  detection:
    - Check for language-specific files
    - Analyze package manager files
    - Detect build tools
  output: "Detected language(s)"

Step_2_Read_Universal_Standards:
  input: "universal/standards/testing/test-generation/"
  action: "Load all universal standard files"
  output: "Universal methodology understanding"

Step_3_Read_Language_Instructions:
  input: "language-instructions/{detected_language}-test-generation.md"
  action: "Load language-specific implementation guide"
  output: "Language-specific tooling knowledge"

Step_4_Analyze_Project:
  input: "Target project"
  actions:
    - Detect testing frameworks
    - Identify quality tools
    - Find configuration files
    - Analyze existing test patterns
  output: "Project-specific context"

Step_5_Generate_Workflow:
  input:
    - Universal standards (Step 2)
    - Language instructions (Step 3)
    - Project context (Step 4)
  action: "Generate language-specific workflow"
  output: ".agent-os/workflows/test_generation_{language}_v1/"

Step_6_Create_Workflow_Metadata:
  input: "Generated workflow"
  action: "Create metadata.json"
  output: "Workflow registration data"
```

### 6.2 Generated Workflow Structure

**Directory:** `.agent-os/workflows/test_generation_{language}_v1/`

```
test_generation_{language}_v1/
├── metadata.json
├── README.md
├── phases/
│   ├── 0/
│   │   ├── phase.md
│   │   └── task-1-environment-setup.md
│   ├── 1/
│   │   ├── phase.md
│   │   ├── task-1-function-analysis.md
│   │   └── task-2-attribute-detection.md
│   ├── 2/
│   │   ├── phase.md
│   │   └── task-1-output-analysis.md
│   ├── 3/
│   │   ├── phase.md
│   │   └── task-1-dependency-analysis.md
│   ├── 4/
│   │   ├── phase.md
│   │   └── task-1-usage-patterns.md
│   ├── 5/
│   │   ├── phase.md
│   │   └── task-1-coverage-planning.md
│   ├── 6/
│   │   ├── phase.md
│   │   └── task-1-validation.md
│   ├── 7/
│   │   ├── phase.md
│   │   └── task-1-generation.md
│   └── 8/
│       ├── phase.md
│       └── task-1-quality-gates.md
└── templates/
    ├── unit-test-template.{ext}
    ├── integration-test-template.{ext}
    └── validation-script.{ext}
```

### 6.3 Workflow Generation Command

**Usage:**

```bash
# Generate test generation workflow for detected language
python scripts/generate-test-workflow.py --language {language}

# Or auto-detect
python scripts/generate-test-workflow.py --auto-detect

# Output
Generated: .agent-os/workflows/test_generation_{language}_v1/
Registered: Workflow available via MCP
```

---

## 7. Implementation Roadmap

### Phase 1: Universal Standards Creation

**Deliverables:**
1. `universal/standards/testing/test-generation/methodology.md`
2. `universal/standards/testing/test-generation/path-system.md`
3. `universal/standards/testing/test-generation/quality-standards.md`
4. `universal/standards/testing/test-generation/evidence-tracking.md`
5. Phase-specific standards (phases 0-8)

**Timeline:** 1-2 weeks

### Phase 2: Language Instruction Templates

**Deliverables:**
1. Complete instruction template
2. Example: `language-instructions/python-test-generation.md` (comprehensive)
3. Example: `language-instructions/javascript-test-generation.md` (comprehensive)

**Timeline:** 1 week

### Phase 3: Additional Language Instructions

**Deliverables:**
1. `go-test-generation.md`
2. `typescript-test-generation.md`
3. `java-test-generation.md`
4. `rust-test-generation.md`
5. `csharp-test-generation.md`

**Timeline:** 2-3 weeks (1-2 days per language)

### Phase 4: Workflow Generation Automation

**Deliverables:**
1. `scripts/generate-test-workflow.py`
2. Language detection logic
3. Workflow template generation
4. Metadata generation
5. MCP integration

**Timeline:** 1-2 weeks

### Phase 5: Validation Scripts per Language

**Deliverables:**
1. Python validation script
2. JavaScript validation script
3. Go validation script
4. Java validation script
5. Rust validation script
6. TypeScript validation script
7. C# validation script

**Timeline:** 2 weeks

### Phase 6: Testing and Refinement

**Deliverables:**
1. Test each language workflow on sample projects
2. Measure success rates
3. Refine based on results
4. Document lessons learned

**Timeline:** 2-3 weeks

### Total Timeline: 9-13 weeks

---

## 8. Example Instantiations

### 8.1 Python Test Generation

**Universal Standard Application:**

```yaml
Phase_1_Function_Analysis:
  universal_requirement: "Extract all function signatures"
  python_implementation: "Use ast.parse() and ast.walk()"
  
  universal_requirement: "Document parameters and types"
  python_implementation: "Extract from ast.FunctionDef.args"
  
  universal_requirement: "Detect attribute access"
  python_implementation: "Find ast.Attribute nodes"
```

**Generated Task File:** `phases/1/task-1-function-analysis.md`

```markdown
# Task 1: Function Analysis (Python)

## Universal Requirements

> From: `universal/standards/testing/test-generation/phase-1-function-analysis.md`

1. Extract all function signatures
2. Document parameters and types
3. Identify return types
4. Detect attribute access patterns

## Python Implementation

### Step 1: AST-Based Function Extraction

🛑 EXECUTE-NOW:

```python
python -c "
import ast
import sys

def analyze_functions(file_path):
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args = [arg.arg for arg in node.args.args]
            defaults = len(node.args.defaults)
            required = len(args) - defaults
            
            # Extract return type if annotated
            return_type = (
                ast.unparse(node.returns) 
                if node.returns else 'Unknown'
            )
            
            functions.append({
                'name': node.name,
                'args': args,
                'required_args': required,
                'total_args': len(args),
                'return_type': return_type,
                'line': node.lineno
            })
    
    for func in functions:
        print(f\"{func['name']}({', '.join(func['args'])}) -> {func['return_type']} [Line {func['line']}]\")
    
    return len(functions)

count = analyze_functions(sys.argv[1])
print(f\"\\n📊 Total functions: {count}\")
" [PRODUCTION_FILE]
```

🛑 PASTE-OUTPUT: Paste complete function list

📊 COUNT-AND-DOCUMENT: Update progress table with function count

### Step 2: Attribute Access Detection

🛑 EXECUTE-NOW:

```python
python -c "
import ast
import sys

def find_attributes(file_path):
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    attributes = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            # Get the attribute name
            attributes.add(node.attr)
    
    for attr in sorted(attributes):
        print(f\"  - {attr}\")
    
    return len(attributes)

print(\"Detected attributes:\")
count = find_attributes(sys.argv[1])
print(f\"\\n📊 Total unique attributes: {count}\")
" [PRODUCTION_FILE]
```

🛑 PASTE-OUTPUT: Paste attribute list

### Step 3: Mock Completeness Requirements (Unit Path Only)

⚠️ IF UNIT PATH SELECTED:

Based on detected attributes, create mock completeness checklist:

```python
class MockObject:
    def __init__(self):
        self.attribute_1 = Mock()  # From analysis
        self.attribute_2 = Mock()  # From analysis
        # ... ALL detected attributes
```

🛑 UPDATE-TABLE:

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 1: Function Analysis | ✅ | X functions, Y attributes | 2/2 | Manual | ✅ |

## See Also

- [Universal Phase 1](../../../../universal/standards/testing/test-generation/phase-1-function-analysis.md)
- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
```

### 8.2 JavaScript Test Generation

**Universal Standard Application:**

```yaml
Phase_1_Function_Analysis:
  universal_requirement: "Extract all function signatures"
  javascript_implementation: "Use @babel/parser or espree"
  
  universal_requirement: "Document parameters"
  javascript_implementation: "Extract from FunctionDeclaration.params"
  
  universal_requirement: "Detect attribute access"
  javascript_implementation: "Find MemberExpression nodes"
```

**Generated Task File:** `phases/1/task-1-function-analysis.md`

```markdown
# Task 1: Function Analysis (JavaScript)

## Universal Requirements

> From: `universal/standards/testing/test-generation/phase-1-function-analysis.md`

1. Extract all function signatures
2. Document parameters
3. Identify return types (if TypeScript)
4. Detect property access patterns

## JavaScript Implementation

### Step 1: Function Extraction

🛑 EXECUTE-NOW:

```bash
# Install parser if needed
npm install --save-dev @babel/parser

# Extract functions
node -e "
const fs = require('fs');
const parser = require('@babel/parser');

const code = fs.readFileSync(process.argv[1], 'utf-8');
const ast = parser.parse(code, {
  sourceType: 'module',
  plugins: ['jsx', 'typescript']
});

function extractFunctions(node, functions = []) {
  if (node.type === 'FunctionDeclaration' || 
      node.type === 'FunctionExpression' ||
      node.type === 'ArrowFunctionExpression') {
    const params = node.params.map(p => p.name || 'destructured');
    const name = node.id ? node.id.name : '<anonymous>';
    functions.push({
      name: name,
      params: params,
      line: node.loc.start.line
    });
  }
  
  for (const key in node) {
    if (node[key] && typeof node[key] === 'object') {
      if (Array.isArray(node[key])) {
        node[key].forEach(child => extractFunctions(child, functions));
      } else {
        extractFunctions(node[key], functions);
      }
    }
  }
  
  return functions;
}

const functions = extractFunctions(ast);
functions.forEach(f => {
  console.log(\`\${f.name}(\${f.params.join(', ')}) [Line \${f.line}]\`);
});

console.log(\`\\n📊 Total functions: \${functions.length}\`);
" [TARGET_FILE]
```

🛑 PASTE-OUTPUT: Paste complete function list

### Step 2: Property Access Detection

🛑 EXECUTE-NOW:

```bash
grep -o "[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*" [TARGET_FILE] | sort -u
```

🛑 PASTE-OUTPUT: Paste property access list

### Step 3: Mock Completeness (Unit Path Only)

⚠️ IF UNIT PATH SELECTED:

Using Jest mocking:

```javascript
const mockObject = {
  property1: jest.fn(),
  property2: jest.fn(),
  // ... ALL detected properties
};
```

🛑 UPDATE-TABLE:

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 1: Function Analysis | ✅ | X functions, Y properties | 2/2 | Manual | ✅ |

## See Also

- [Universal Phase 1](../../../../universal/standards/testing/test-generation/phase-1-function-analysis.md)
- [Jest Mocking Documentation](https://jestjs.io/docs/mock-functions)
```

### 8.3 Go Test Generation

**Universal Standard Application:**

```yaml
Phase_1_Function_Analysis:
  universal_requirement: "Extract all function signatures"
  go_implementation: "Use go/parser and go/ast"
  
  universal_requirement: "Document parameters and types"
  go_implementation: "Extract from FuncDecl.Type.Params"
  
  universal_requirement: "Detect method calls"
  go_implementation: "Find SelectorExpr nodes"
```

**Generated Task File:** `phases/1/task-1-function-analysis.md`

```markdown
# Task 1: Function Analysis (Go)

## Universal Requirements

> From: `universal/standards/testing/test-generation/phase-1-function-analysis.md`

1. Extract all function signatures
2. Document parameters and types
3. Identify return types
4. Detect method calls

## Go Implementation

### Step 1: AST-Based Function Extraction

🛑 EXECUTE-NOW:

Create temporary analysis script:

```go
// analyze_functions.go
package main

import (
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: go run analyze_functions.go <file.go>")
		return
	}

	fset := token.NewFileSet()
	node, err := parser.ParseFile(fset, os.Args[1], nil, parser.ParseComments)
	if err != nil {
		panic(err)
	}

	var functions []string
	ast.Inspect(node, func(n ast.Node) bool {
		if fn, ok := n.(*ast.FuncDecl); ok {
			params := []string{}
			if fn.Type.Params != nil {
				for _, param := range fn.Type.Params.List {
					for _, name := range param.Names {
						params = append(params, name.Name)
					}
				}
			}
			
			returns := "unknown"
			if fn.Type.Results != nil && len(fn.Type.Results.List) > 0 {
				returns = fmt.Sprintf("%d return values", len(fn.Type.Results.List))
			}
			
			functions = append(functions, fmt.Sprintf("%s(%s) -> %s [Line %d]",
				fn.Name.Name,
				strings.Join(params, ", "),
				returns,
				fset.Position(fn.Pos()).Line,
			))
		}
		return true
	})

	for _, fn := range functions {
		fmt.Println(fn)
	}
	fmt.Printf("\n📊 Total functions: %d\n", len(functions))
}
```

```bash
go run analyze_functions.go [TARGET_FILE]
```

🛑 PASTE-OUTPUT: Paste complete function list

### Step 2: Method Call Detection

🛑 EXECUTE-NOW:

```bash
grep -oE "[a-zA-Z_][a-zA-Z0-9_]*\.[A-Z][a-zA-Z0-9_]*\(" [TARGET_FILE] | sort -u
```

🛑 PASTE-OUTPUT: Paste method call list

### Step 3: Mock Strategy (Unit Path Only)

⚠️ IF UNIT PATH SELECTED:

Using testify/mock:

```go
type Mock{ObjectName} struct {
	mock.Mock
}

func (m *Mock{ObjectName}) Method1(args) returnType {
	args := m.Called(args)
	return args.Get(0).(returnType)
}
```

🛑 UPDATE-TABLE:

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 1: Function Analysis | ✅ | X functions, Y methods | 2/2 | Manual | ✅ |

## See Also

- [Universal Phase 1](../../../../universal/standards/testing/test-generation/phase-1-function-analysis.md)
- [Go testing package](https://pkg.go.dev/testing)
- [testify/mock](https://github.com/stretchr/testify)
```

---

## Conclusion

This design enables:

1. **Single Source of Truth:** Universal standards define methodology once
2. **Language Flexibility:** Language instructions adapt to any language
3. **Automated Generation:** LLM combines both to create workflows
4. **Proven Methodology:** 80%+ success rate pattern from V3 Python
5. **Maintainability:** Update universal standards → all languages benefit

### Next Steps

1. Create universal standards (Layer 1)
2. Write language instructions (Layer 2)
3. Build workflow generator (automation)
4. Validate across languages
5. Iterate based on results

---

**Document End**

