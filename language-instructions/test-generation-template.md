# {LANGUAGE} Test Generation Instructions

**For Cursor Agent: When generating tests for {LANGUAGE}, use these instructions to apply universal test generation standards with {LANGUAGE}-specific tooling.**

---

## Overview

This document maps **universal test generation standards** to **{LANGUAGE}-specific implementation**.

### Universal Standards Reference

⚠️ MUST-READ first:
- `universal/standards/testing/test-generation/methodology.md`
- `universal/standards/testing/test-generation/path-system.md`
- `universal/standards/testing/test-generation/quality-standards.md`

### {LANGUAGE} Context

This file provides:
- {LANGUAGE}-specific analysis tools
- {LANGUAGE} testing frameworks
- {LANGUAGE} mocking patterns
- {LANGUAGE} quality tools
- {LANGUAGE} code examples

---

## Phase 0: Environment Setup ({LANGUAGE})

### Universal Requirements

> From: `universal/standards/testing/test-generation/phases/phase-0-setup.md`

1. Validate development environment
2. Analyze target file complexity
3. Select test path (unit OR integration)
4. Initialize progress tracking

### {LANGUAGE} Implementation

#### Environment Validation

🛑 EXECUTE-NOW:

```bash
# Check {LANGUAGE} installation
{LANGUAGE_VERSION_COMMAND}

# Check package manager
{PACKAGE_MANAGER_COMMAND}

# Check build tool
{BUILD_TOOL_COMMAND}

# Verify workspace
pwd
ls -la
```

**Example Output:**
```
$ {EXAMPLE_VERSION_OUTPUT}
```

#### Target File Analysis

🛑 EXECUTE-NOW:

```bash
# Line count
wc -l {TARGET_FILE}

# Function/method count
{LANGUAGE_SPECIFIC_FUNCTION_COUNT_COMMAND}
```

**Example Output:**
```
$ {EXAMPLE_COUNT_OUTPUT}
```

#### Path Selection

**Decision Factors:**

```yaml
Unit_Path_Indicators:
  - Single module testing
  - Mock control needed
  - Fast feedback required
  - Coverage metrics important

Integration_Path_Indicators:
  - Multi-component testing
  - End-to-end validation needed
  - Real system behavior critical
  - API contract verification
```

🛑 UPDATE-TABLE:

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 0: Setup | ✅ | Environment validated, path: {unit/integration} | 3/3 | Manual | ✅ |

---

## Phase 1: Function/Method Analysis ({LANGUAGE})

### Universal Requirements

> From: `universal/standards/testing/test-generation/phases/phase-1-function-analysis.md`

1. Extract ALL function/method signatures
2. Document parameters and types
3. Identify return types
4. Detect attribute/property access patterns
5. Map function calls

### {LANGUAGE} Implementation

#### Tool: {PRIMARY_ANALYSIS_TOOL}

**Installation:**
```bash
{TOOL_INSTALLATION_COMMAND}
```

**Usage:**
```{language}
{TOOL_USAGE_EXAMPLE}
```

#### Step 1: Signature Extraction

🛑 EXECUTE-NOW:

```{language}
{SIGNATURE_EXTRACTION_SCRIPT}
```

**Expected Output Format:**
```
function_name(param1: Type1, param2: Type2) -> ReturnType [Line X]
```

🛑 PASTE-OUTPUT: Paste complete function list

📊 COUNT-AND-DOCUMENT: Update progress table with exact function count

#### Step 2: Attribute/Property Access Detection

🛑 EXECUTE-NOW:

```bash
{ATTRIBUTE_DETECTION_COMMAND}
```

**Pattern Matching:**
```
{LANGUAGE_ATTRIBUTE_SYNTAX_PATTERN}
```

🛑 PASTE-OUTPUT: Paste attribute/property list

📊 COUNT-AND-DOCUMENT: Update progress table with attribute count

#### Step 3: Function Call Pattern Analysis

🛑 EXECUTE-NOW:

```bash
{FUNCTION_CALL_DETECTION_COMMAND}
```

🛑 PASTE-OUTPUT: Paste function call patterns

#### Step 4: Mock Completeness Requirements (Unit Path Only)

⚠️ IF UNIT PATH SELECTED:

Based on detected attributes, create mock completeness checklist:

**{LANGUAGE} Mock Pattern:**
```{language}
{MOCK_COMPLETENESS_PATTERN}
```

**Checklist:**
- [ ] All detected attributes included in mock
- [ ] Mock types match detected types
- [ ] No AttributeError/PropertyError possible

🛑 UPDATE-TABLE:

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 1: Function Analysis | ✅ | X functions, Y attributes, mock checklist | 3/3 | Manual | ✅ |

---

## Phase 2: Output Analysis ({LANGUAGE})

### Universal Requirements

> From: `universal/standards/testing/test-generation/phases/phase-2-output-analysis.md`

1. Identify all logging/output statements
2. Classify output levels
3. Determine path-specific strategy

### {LANGUAGE} Implementation

#### Logging Framework Detection

**Common {LANGUAGE} Logging:**
- {LOGGING_FRAMEWORK_1}
- {LOGGING_FRAMEWORK_2}
- {LOGGING_FRAMEWORK_3}

🛑 EXECUTE-NOW:

```bash
{LOGGING_DETECTION_COMMAND}
```

🛑 PASTE-OUTPUT: Paste logging statement locations

#### Level Classification

🛑 EXECUTE-NOW:

```bash
{LOGGING_LEVEL_DETECTION_COMMAND}
```

**Output Structure:**
```
Level | Count | Example Locations
------|-------|------------------
DEBUG | X     | lines: ...
INFO  | X     | lines: ...
ERROR | X     | lines: ...
```

#### Path-Specific Strategy

**Unit Path:**
```{language}
{UNIT_OUTPUT_MOCKING_PATTERN}
```

**Integration Path:**
```{language}
{INTEGRATION_OUTPUT_VALIDATION_PATTERN}
```

🛑 UPDATE-TABLE:

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 2: Output Analysis | ✅ | X output statements, levels classified | 2/2 | Manual | ✅ |

---

## Phase 3: Dependency Analysis ({LANGUAGE})

### Universal Requirements

> From: `universal/standards/testing/test-generation/phases/phase-3-dependency-analysis.md`

1. Map all external dependencies
2. Map all internal dependencies
3. Identify configuration dependencies
4. Document I/O dependencies

### {LANGUAGE} Implementation

#### Import/Dependency Analysis

🛑 EXECUTE-NOW:

```bash
{IMPORT_ANALYSIS_COMMAND}
```

**Classification:**
```
External Dependencies (from third-party):
- {EXTERNAL_DEPENDENCY_PATTERN}

Internal Dependencies (from project):
- {INTERNAL_DEPENDENCY_PATTERN}

Configuration:
- {CONFIGURATION_PATTERN}

I/O Operations:
- {IO_PATTERN}
```

🛑 PASTE-OUTPUT: Paste categorized dependencies

#### Mock Strategy (Unit Path Only)

⚠️ IF UNIT PATH SELECTED:

**External Dependency Mocking:**
```{language}
{EXTERNAL_DEPENDENCY_MOCK_PATTERN}
```

**Example:**
```{language}
{EXTERNAL_MOCK_EXAMPLE}
```

#### Real Dependency Strategy (Integration Path Only)

⚠️ IF INTEGRATION PATH SELECTED:

**Real Dependency Setup:**
```{language}
{REAL_DEPENDENCY_SETUP_PATTERN}
```

🛑 UPDATE-TABLE:

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 3: Dependency Analysis | ✅ | X external, Y internal, mock strategy | 1/1 | Manual | ✅ |

---

## Phase 4: Usage Pattern Analysis ({LANGUAGE})

### Universal Requirements

> From: `universal/standards/testing/test-generation/phases/phase-4-usage-patterns.md`

1. Analyze function call patterns
2. Map control flow
3. Identify error handling
4. Document state management

### {LANGUAGE} Implementation

#### Control Flow Detection

🛑 EXECUTE-NOW:

```bash
{CONTROL_FLOW_DETECTION_COMMAND}
```

**{LANGUAGE} Patterns:**
- Conditionals: {CONDITIONAL_KEYWORDS}
- Loops: {LOOP_KEYWORDS}
- Branches: {BRANCH_KEYWORDS}

🛑 PASTE-OUTPUT: Paste control flow patterns

#### Error Handling Detection

🛑 EXECUTE-NOW:

```bash
{ERROR_HANDLING_DETECTION_COMMAND}
```

**{LANGUAGE} Error Patterns:**
- {ERROR_PATTERN_1}
- {ERROR_PATTERN_2}

🛑 PASTE-OUTPUT: Paste error handling patterns

🛑 UPDATE-TABLE:

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 4: Usage Patterns | ✅ | X control flows, Y error handlers | 2/2 | Manual | ✅ |

---

## Phase 5: Coverage Planning ({LANGUAGE})

### Universal Requirements

> From: `universal/standards/testing/test-generation/phases/phase-5-coverage-planning.md`

1. Identify all conditional branches
2. Plan edge case testing
3. Document error paths
4. Establish coverage targets

### {LANGUAGE} Implementation

#### Coverage Tool

**Tool:** {COVERAGE_TOOL_NAME}

**Installation:**
```bash
{COVERAGE_TOOL_INSTALL_COMMAND}
```

**Usage:**
```bash
{COVERAGE_TOOL_USAGE_COMMAND}
```

#### Branch Identification

🛑 EXECUTE-NOW:

```bash
{BRANCH_DETECTION_COMMAND}
```

🛑 PASTE-OUTPUT: Paste branch list

#### Edge Case Planning

**Common Edge Cases in {LANGUAGE}:**
- Null/nil/None: {NULL_HANDLING}
- Empty collections: {EMPTY_COLLECTION_HANDLING}
- Zero values: {ZERO_HANDLING}
- Boundary values: {BOUNDARY_EXAMPLES}

📊 COUNT-AND-DOCUMENT: 
- Total branches: X
- Edge cases identified: Y
- Coverage target: 90%+ (unit) or functional (integration)

🛑 UPDATE-TABLE:

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 5: Coverage Planning | ✅ | X branches, Y edge cases, 90% target | 1/1 | Manual | ✅ |

---

## Phase 6: Pre-Generation Validation ({LANGUAGE})

### Universal Requirements

> From: `universal/standards/testing/test-generation/phases/phase-6-validation.md`

1. Verify technical prerequisites
2. Validate complete analysis chain
3. Confirm path strategy
4. Prepare quality tool integration

### {LANGUAGE} Implementation

#### Import/Module Validation

🛑 EXECUTE-NOW:

```{language}
{IMPORT_VALIDATION_COMMAND}
```

**Expected:** No import errors

#### Signature Verification

🛑 EXECUTE-NOW:

```{language}
{SIGNATURE_VERIFICATION_COMMAND}
```

**Expected:** Function signatures accessible

#### Test Framework Availability

🛑 EXECUTE-NOW:

```bash
{TEST_FRAMEWORK_CHECK_COMMAND}
```

**Expected:** Test framework installed and functional

#### Quality Tools Check

🛑 EXECUTE-NOW:

```bash
# Static analyzer
{STATIC_ANALYZER_CHECK}

# Type checker (if applicable)
{TYPE_CHECKER_CHECK}

# Formatter
{FORMATTER_CHECK}

# Coverage tool
{COVERAGE_TOOL_CHECK}
```

**Expected:** All tools available

#### Analysis Completeness

🛑 VALIDATE-GATE:

- [ ] Phase 1: Functions analyzed ✅/❌
- [ ] Phase 2: Output patterns mapped ✅/❌
- [ ] Phase 3: Dependencies complete ✅/❌
- [ ] Phase 4: Usage patterns analyzed ✅/❌
- [ ] Phase 5: Coverage planned ✅/❌
- [ ] Path strategy: {unit/integration} confirmed
- [ ] Mock requirements: {complete/N/A}

⚠️ ALL must be ✅ before proceeding to Phase 7

🛑 UPDATE-TABLE:

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 6: Validation | ✅ | All prerequisites verified, analysis complete | 5/5 | Manual | ✅ |

---

## Phase 7: Test Generation ({LANGUAGE})

### Universal Requirements

> From: `universal/standards/testing/test-generation/phases/phase-7-generation.md`

1. Generate comprehensive test file
2. Execute tests immediately
3. Collect metrics
4. Perform initial validation

### {LANGUAGE} Implementation

#### Testing Framework Selection

**Recommended: {PRIMARY_TEST_FRAMEWORK}**

| Framework | Use Case | Status |
|-----------|----------|--------|
| {FRAMEWORK_1} | {USE_CASE_1} | ✅ Recommended |
| {FRAMEWORK_2} | {USE_CASE_2} | ⚠️ Alternative |
| {FRAMEWORK_3} | {USE_CASE_3} | 📝 Specialized |

#### Unit Test Template ({LANGUAGE})

⚠️ IF UNIT PATH:

```{language}
{UNIT_TEST_TEMPLATE}
```

**Key Patterns:**
- Mocking: {MOCK_PATTERN_SUMMARY}
- Assertions: {ASSERTION_PATTERN_SUMMARY}
- Fixtures: {FIXTURE_PATTERN_SUMMARY}

#### Integration Test Template ({LANGUAGE})

⚠️ IF INTEGRATION PATH:

```{language}
{INTEGRATION_TEST_TEMPLATE}
```

**Key Patterns:**
- Real dependencies: {REAL_DEPENDENCY_PATTERN}
- Setup/teardown: {SETUP_TEARDOWN_PATTERN}
- Backend verification: {VERIFICATION_PATTERN}

#### Test Generation Process

🛑 EXECUTE-NOW:

1. Create test file: `{TEST_FILE_NAMING_CONVENTION}`
2. Implement test cases for all functions (Phase 1)
3. Cover all branches (Phase 5)
4. Include edge cases (Phase 5)
5. Mock/use real dependencies per path (Phase 3)

**Generated Test Structure:**
```{language}
{TEST_FILE_STRUCTURE_EXAMPLE}
```

#### Immediate Test Execution

🛑 EXECUTE-NOW:

```bash
{TEST_EXECUTION_COMMAND}
```

🛑 PASTE-OUTPUT: Paste complete test results

#### Metrics Collection

🛑 EXECUTE-NOW:

```bash
# Coverage
{COVERAGE_MEASUREMENT_COMMAND}

# Static analysis
{STATIC_ANALYSIS_COMMAND}

# Type checking
{TYPE_CHECKING_COMMAND}

# Formatting check
{FORMATTING_CHECK_COMMAND}
```

🛑 PASTE-OUTPUT: Paste all metrics

📊 COUNT-AND-DOCUMENT: Format metrics as JSON:

```json
{
  "test_execution": {
    "passed": X,
    "failed": Y,
    "total": Z,
    "pass_rate": XX.X
  },
  "coverage": {
    "line_percent": XX.X,
    "branch_percent": XX.X
  },
  "static_analysis": {
    "score": "{SCORE_FORMAT}",
    "errors": X,
    "warnings": Y
  },
  "type_checking": {
    "errors": X
  },
  "formatting": {
    "compliant": true/false
  }
}
```

🛑 UPDATE-TABLE:

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 7: Generation + Metrics | ✅ | Tests generated, JSON metrics | 1/1 | JSON | ✅ |

---

## Phase 8: Quality Enforcement ({LANGUAGE})

### Universal Requirements

> From: `universal/standards/testing/test-generation/phases/phase-8-quality-gates.md`

1. 100% test pass rate
2. Perfect static analysis score
3. Zero type errors
4. 100% formatter compliance
5. Coverage targets met

### {LANGUAGE} Implementation

#### Quality Tools

**Static Analyzer:** {STATIC_ANALYZER_NAME}
- Command: `{STATIC_ANALYZER_COMMAND}`
- Perfect score: {PERFECT_SCORE_DEFINITION}

**Type Checker:** {TYPE_CHECKER_NAME}
- Command: `{TYPE_CHECKER_COMMAND}`
- Target: 0 errors

**Formatter:** {FORMATTER_NAME}
- Command: `{FORMATTER_COMMAND}`
- Target: 100% compliant

**Coverage:** {COVERAGE_TOOL_NAME}
- Command: `{COVERAGE_COMMAND}`
- Target: 90%+ (unit), functional (integration)

#### Automated Validation Script

**Script:** `scripts/validate-{language}-test-quality.{ext}`

**Content:**
```{language}
{VALIDATION_SCRIPT_CONTENT}
```

#### Script Execution

🛑 EXECUTE-NOW:

```bash
{VALIDATION_SCRIPT_EXECUTION_COMMAND}
```

**Required Output Format:**
```
=== Quality Validation Results ===

✅ Test Execution: X/X tests passed (100%)
✅ Coverage: XX.X% lines, XX.X% branches
✅ Static Analysis: {PERFECT_SCORE}
✅ Type Checking: 0 errors
✅ Formatting: Compliant

=== ALL QUALITY GATES PASSED ===
Exit code: 0
```

🛑 PASTE-OUTPUT: Paste complete validation output

#### Zero Tolerance Enforcement

```
🚨 ABSOLUTE REQUIREMENTS:

✅ Test Pass Rate: 100% (not 95%, not 99%)
✅ Static Analysis: {PERFECT_SCORE} (not {NEAR_PERFECT_SCORE})
✅ Type Errors: 0 (not 2, not "just warnings")
✅ Formatting: 100% (not "mostly formatted")
✅ Coverage: 90%+ for unit (not 85%)

🚨 FRAMEWORK-VIOLATION: Declaring success with ANY failure
```

#### Remediation (If Exit Code ≠ 0)

**Test Failures:**
```yaml
symptom: "Tests failing"
action: "Return to Phase 1-4 analysis"
check: "Mock completeness, function signatures, dependencies"
```

**Coverage Failures:**
```yaml
symptom: "Coverage below 90%"
action: "Return to Phase 5 coverage planning"
check: "Missing branches, edge cases not covered"
```

**Static Analysis Failures:**
```yaml
symptom: "Linter warnings/errors"
action: "Fix issues, re-run validation"
fix_examples: "{COMMON_LINTER_FIXES}"
```

**Type Errors:**
```yaml
symptom: "Type checker errors"
action: "Fix type annotations, re-run validation"
fix_examples: "{COMMON_TYPE_FIXES}"
```

🛑 UPDATE-TABLE:

| Phase | Status | Evidence | Commands | Validation | Gate |
|-------|--------|----------|----------|------------|------|
| 8: Quality Gates | ✅ | Exit code 0, all gates passed | 1/1 | **EXIT 0** | ✅ |

---

## Common Patterns

### Mocking Patterns

#### Mock External API

```{language}
{API_MOCKING_PATTERN}
```

#### Mock Database

```{language}
{DATABASE_MOCKING_PATTERN}
```

#### Mock File System

```{language}
{FILESYSTEM_MOCKING_PATTERN}
```

### Assertion Patterns

#### Value Assertions

```{language}
{VALUE_ASSERTION_PATTERNS}
```

#### Exception Assertions

```{language}
{EXCEPTION_ASSERTION_PATTERNS}
```

#### Collection Assertions

```{language}
{COLLECTION_ASSERTION_PATTERNS}
```

### Fixture Patterns

#### Setup/Teardown

```{language}
{SETUP_TEARDOWN_PATTERN}
```

#### Parametrized Tests

```{language}
{PARAMETRIZED_TEST_PATTERN}
```

---

## Project Context Integration

### Framework Detection

**Detect {LANGUAGE} Frameworks:**

```bash
{FRAMEWORK_DETECTION_COMMANDS}
```

**If Detected:**
- {FRAMEWORK_1}: {SPECIAL_HANDLING_1}
- {FRAMEWORK_2}: {SPECIAL_HANDLING_2}

### Configuration Files

**Generate if missing:**

```{language}
# {CONFIG_FILE_1}
{CONFIG_FILE_1_TEMPLATE}

# {CONFIG_FILE_2}
{CONFIG_FILE_2_TEMPLATE}
```

---

## Troubleshooting

### Common Issues

#### Issue 1: {COMMON_ISSUE_1}

**Symptom:** {SYMPTOM_1}

**Cause:** {CAUSE_1}

**Solution:**
```bash
{SOLUTION_1}
```

#### Issue 2: {COMMON_ISSUE_2}

**Symptom:** {SYMPTOM_2}

**Cause:** {CAUSE_2}

**Solution:**
```bash
{SOLUTION_2}
```

#### Issue 3: {COMMON_ISSUE_3}

**Symptom:** {SYMPTOM_3}

**Cause:** {CAUSE_3}

**Solution:**
```bash
{SOLUTION_3}
```

---

## See Also

- [Universal Test Generation Methodology](../universal/standards/testing/test-generation/methodology.md)
- [Path System Standards](../universal/standards/testing/test-generation/path-system.md)
- [Quality Standards](../universal/standards/testing/test-generation/quality-standards.md)
- [Evidence Tracking](../universal/standards/testing/test-generation/evidence-tracking.md)

---

## Quick Reference Card

```yaml
Phase_0: "{LANGUAGE_VERSION_COMMAND}, path selection"
Phase_1: "{PRIMARY_ANALYSIS_TOOL}, X functions, Y attributes"
Phase_2: "{LOGGING_DETECTION_COMMAND}, output strategy"
Phase_3: "{IMPORT_ANALYSIS_COMMAND}, mock/real strategy"
Phase_4: "{CONTROL_FLOW_DETECTION_COMMAND}, patterns"
Phase_5: "{COVERAGE_TOOL_NAME}, 90%+ target"
Phase_6: "Prerequisites validated, analysis complete"
Phase_7: "{PRIMARY_TEST_FRAMEWORK}, tests generated"
Phase_8: "{VALIDATION_SCRIPT_COMMAND}, exit code 0"

Success: "80%+ first-run pass rate"
```

---

**Template Version:** 1.0  
**Last Updated:** October 9, 2025  
**Instructions:** Replace ALL {PLACEHOLDER} values with language-specific content

