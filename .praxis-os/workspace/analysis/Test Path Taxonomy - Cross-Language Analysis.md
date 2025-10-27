# Test Path Taxonomy - Cross-Language Analysis

**Document Version:** 1.0  
**Date:** October 9, 2025  
**Purpose:** Define flexible test path system supporting language-specific naming conventions

---

## Executive Summary

The JS/TS workflow uses a **three-path system**: Unit, Integration, and **Validation**. This pattern is universal across languages, but the third path has different names based on language ecosystem conventions.

### Key Finding

```yaml
Universal_Pattern:
  path_1: "Unit Tests" (isolation, mocked dependencies)
  path_2: "Integration Tests" (component interactions, some real dependencies)
  path_3: "Validation/Acceptance/E2E/Contract Tests" (real-world scenarios, production-like data)

Naming_Varies_By_Language: true
Concept_Is_Universal: true
```

---

## Table of Contents

1. [The Three-Path Pattern](#the-three-path-pattern)
2. [Cross-Language Naming Conventions](#cross-language-naming-conventions)
3. [Path Characteristics Matrix](#path-characteristics-matrix)
4. [Language-Specific Recommendations](#language-specific-recommendations)
5. [Design Pattern for Universal Framework](#design-pattern-for-universal-framework)
6. [Implementation Strategy](#implementation-strategy)

---

## 1. The Three-Path Pattern

### Core Concept

```
┌─────────────────────────────────────────────────────────────┐
│ Path 1: ISOLATION TESTING                                    │
│ - Mock external dependencies                                 │
│ - Test single unit in isolation                              │
│ - Fast, deterministic                                        │
│ - Universal Name: "Unit Tests"                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Path 2: INTERACTION TESTING                                  │
│ - Some real dependencies (typically internal)                │
│ - Test component interactions                                │
│ - Moderate speed, more realistic                             │
│ - Universal Name: "Integration Tests"                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Path 3: REAL-WORLD SCENARIO TESTING                          │
│ - Production-like data and scenarios                         │
│ - End-to-end behavior validation                             │
│ - Real-world edge cases                                      │
│ - NAME VARIES BY LANGUAGE ← Focus of this document           │
└─────────────────────────────────────────────────────────────┘
```

### JS/TS "Validation Tests" Definition

From `hive-kube` workflow:

```yaml
Validation_Tests:
  purpose: "Verify real-world behavior and edge cases with realistic inputs"
  characteristics:
    - Production-like data
    - End-to-end scenarios
    - Complex conditional logic paths
    - Behavioral complexity verification
  coverage_target: "≥70%"
  speed: "Slower than unit/integration"
  determinism: "Dependent on data quality"
```

---

## 2. Cross-Language Naming Conventions

### Language-by-Language Analysis

#### JavaScript/TypeScript

**Common Names:**
1. **Validation Tests** (your usage) ✅
2. **End-to-End Tests** (E2E) - Most common
3. **Acceptance Tests** - BDD contexts
4. **Scenario Tests** - Behavioral focus
5. **Feature Tests** - Rails influence

**Ecosystem Examples:**
```javascript
// Validation pattern
describe('validation', () => {
  it('should handle real-world scenario X', () => { ... });
});

// E2E pattern  
describe('e2e', () => {
  it('should complete checkout flow', () => { ... });
});

// Acceptance pattern (Cucumber)
Feature: User checkout
  Scenario: User purchases item
```

**Directory Conventions:**
- `tests/validation/` ✅ Your usage
- `tests/e2e/` (most common)
- `tests/acceptance/`
- `tests/features/`
- `__tests__/integration/` (sometimes conflated)

---

#### Python

**Common Names:**
1. **Functional Tests** - Most common in Python
2. **Acceptance Tests** - BDD contexts (behave, pytest-bdd)
3. **End-to-End Tests** (E2E)
4. **System Tests** - Enterprise contexts
5. **Smoke Tests** - Lighter validation

**Ecosystem Examples:**
```python
# Functional test (pytest)
# tests/functional/test_user_workflow.py
def test_complete_user_registration_flow():
    """Test full registration with realistic data"""
    ...

# Acceptance test (behave)
# features/user_registration.feature
Feature: User Registration
  Scenario: New user signs up successfully
    Given a new user with valid email
    When they complete registration
    Then they should receive confirmation

# System test
# tests/system/test_api_integration.py
```

**Directory Conventions:**
- `tests/functional/` (Django, Flask, FastAPI standard)
- `tests/acceptance/` (BDD projects)
- `tests/e2e/`
- `tests/system/`
- `features/` (behave/pytest-bdd)

**Python-Specific Note:**
- Django docs use "Functional tests" for Selenium-based tests
- pytest-bdd uses "Acceptance tests"
- Enterprise Python often uses "System tests"

---

#### Go

**Common Names:**
1. **End-to-End Tests** (E2E) - Most common
2. **Acceptance Tests** - Ginkgo/BDD contexts
3. **Functional Tests**
4. **Black Box Tests** - Go-specific emphasis
5. **Integration Tests** (sometimes encompasses validation)

**Ecosystem Examples:**
```go
// E2E test
// e2e_test.go or e2e/user_workflow_test.go
func TestUserRegistrationE2E(t *testing.T) {
    // Real database, real API calls
}

// Acceptance test (Ginkgo)
var _ = Describe("User Registration", func() {
    Context("When user provides valid data", func() {
        It("should complete registration", func() { ... })
    })
})

// Black box test (external package testing)
package mypackage_test  // Note: _test suffix = black box
```

**Directory Conventions:**
- `e2e/`
- `acceptance/`
- `test/e2e/`
- Package suffix: `mypackage_test` (black box approach)

**Go-Specific Note:**
- Strong distinction between white-box (`package mypackage`) and black-box (`package mypackage_test`) testing
- "Black box" tests align with validation/acceptance concept

---

#### Java

**Common Names:**
1. **Acceptance Tests** - Most common (Spring Boot)
2. **Integration Tests** (often broader than typical integration)
3. **Functional Tests**
4. **End-to-End Tests** (E2E)
5. **System Tests**
6. **Behavioral Tests** (Cucumber/JBehave)

**Ecosystem Examples:**
```java
// Acceptance test (JUnit + Spring Boot)
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
class UserAcceptanceTests {
    @Test
    void shouldCompleteRegistrationWorkflow() { ... }
}

// Behavioral test (Cucumber)
@Given("a new user with email {string}")
@When("they complete registration")
@Then("they should receive confirmation")

// Functional test
@Test
@Category(FunctionalTests.class)
void testUserWorkflow() { ... }
```

**Directory Conventions:**
- `src/test/acceptance/`
- `src/test/functional/`
- `src/test/e2e/`
- `src/test/java/.../acceptance/` (Maven structure)
- `src/acceptanceTest/` (Gradle convention)

**Java-Specific Note:**
- Spring Boot documentation emphasizes "Acceptance Tests"
- Gradle has built-in `acceptanceTest` source set support
- Enterprise Java often uses "System Tests"

---

#### Rust

**Common Names:**
1. **Integration Tests** (broader scope in Rust)
2. **End-to-End Tests** (E2E)
3. **Functional Tests**
4. **Black Box Tests** (Rust's `tests/` directory)
5. **Acceptance Tests** (less common)

**Ecosystem Examples:**
```rust
// Integration test (tests/ directory = black box)
// tests/user_workflow.rs
#[test]
fn test_complete_user_registration() {
    // Real database, real API
}

// Functional test
#[cfg(test)]
mod functional_tests {
    #[test]
    fn test_end_to_end_workflow() { ... }
}
```

**Directory Conventions:**
- `tests/` (Cargo convention for integration tests)
- `tests/functional/`
- `tests/e2e/`

**Rust-Specific Note:**
- Rust's `tests/` directory is specifically for "integration tests" but often used for what other languages call acceptance/validation tests
- Strong separation: `src/` = white box, `tests/` = black box

---

#### C#

**Common Names:**
1. **Acceptance Tests** - Most common (.NET)
2. **Integration Tests** (broader scope)
3. **Functional Tests**
4. **End-to-End Tests** (E2E)
5. **System Tests**
6. **Behavioral Tests** (SpecFlow)

**Ecosystem Examples:**
```csharp
// Acceptance test (xUnit)
public class UserAcceptanceTests : IClassFixture<WebApplicationFactory<Startup>>
{
    [Fact]
    public async Task ShouldCompleteRegistrationWorkflow()
    { ... }
}

// Behavioral test (SpecFlow)
[Given(@"a new user with email ""(.*)""")]
[When(@"they complete registration")]
[Then(@"they should receive confirmation")]

// Functional test
[Trait("Category", "Functional")]
public void TestUserWorkflow() { ... }
```

**Directory Conventions:**
- `tests/Acceptance/`
- `tests/Functional/`
- `tests/E2E/`
- `tests/Integration/` (often broad scope)
- `.AcceptanceTests/` (project suffix)

**C#-Specific Note:**
- ASP.NET Core docs emphasize "Integration Tests" (but broader scope)
- SpecFlow popularized "Behavioral Tests"
- Enterprise C# uses "Acceptance Tests"

---

#### Ruby

**Common Names:**
1. **Feature Tests** - Rails standard
2. **Acceptance Tests** - RSpec/Cucumber
3. **System Tests** - Rails 5.1+
4. **End-to-End Tests** (E2E)
5. **Scenario Tests** (Cucumber)

**Ecosystem Examples:**
```ruby
# Feature test (RSpec + Capybara)
# spec/features/user_registration_spec.rb
RSpec.feature "User registration", type: :feature do
  scenario "User completes registration" do
    visit new_user_path
    # ...
  end
end

# System test (Rails 5.1+)
# test/system/user_registration_test.rb
class UserRegistrationTest < ApplicationSystemTestCase
  test "completing registration" do
    # ...
  end
end

# Acceptance test (Cucumber)
# features/user_registration.feature
Feature: User Registration
  Scenario: User signs up
```

**Directory Conventions:**
- `spec/features/` (RSpec + Capybara)
- `test/system/` (Rails system tests)
- `features/` (Cucumber)
- `spec/acceptance/`

**Ruby-Specific Note:**
- Rails shifted from "Feature Tests" → "System Tests" in v5.1
- Both terms widely used and understood
- Capybara-based tests often called "Feature Tests"

---

### Summary Table

| Language | Most Common Name | Alternative Names | Directory Convention |
|----------|------------------|-------------------|---------------------|
| **JavaScript/TypeScript** | E2E Tests | Validation, Acceptance, Scenario, Feature | `tests/e2e/`, `tests/validation/` ✅ |
| **Python** | Functional Tests | Acceptance, E2E, System, Smoke | `tests/functional/`, `tests/acceptance/` |
| **Go** | E2E Tests | Acceptance, Functional, Black Box | `e2e/`, `acceptance/` |
| **Java** | Acceptance Tests | Integration (broad), Functional, E2E, System | `src/test/acceptance/`, `src/acceptanceTest/` |
| **Rust** | Integration Tests (broad) | E2E, Functional, Black Box | `tests/`, `tests/e2e/` |
| **C#** | Acceptance Tests | Integration (broad), Functional, E2E, System | `tests/Acceptance/`, `.AcceptanceTests/` |
| **Ruby** | Feature/System Tests | Acceptance, E2E, Scenario | `spec/features/`, `test/system/` |

---

## 3. Path Characteristics Matrix

### Universal Characteristics (Language-Agnostic)

| Characteristic | Unit Tests | Integration Tests | Path 3 (Validation/E2E/etc.) |
|---------------|------------|-------------------|------------------------------|
| **Dependencies** | All mocked | Some real (internal) | Mostly/all real |
| **Scope** | Single function/class | Multiple components | Complete scenarios |
| **Data** | Minimal test data | Realistic test data | Production-like data |
| **Speed** | <100ms | 1-10s | 10-60s |
| **Determinism** | Very high | High | Moderate |
| **Maintenance** | Low | Moderate | High |
| **Failure Diagnosis** | Pinpoint exact function | Narrows to interaction | Broad (system-level) |
| **Coverage Target** | 80-90% | 60-80% | 70-90% |
| **Test Count** | Many (70-80%) | Some (15-25%) | Few (5-15%) |

### Path 3 Naming Rationale by Language

| Language | Preferred Name | Rationale |
|----------|---------------|-----------|
| JS/TS | **Validation** or **E2E** | "Validation" emphasizes data/behavior verification; "E2E" emphasizes full-stack |
| Python | **Functional** | Django/Flask convention; "function" = feature/capability |
| Go | **E2E** | Go idiom for comprehensive testing; "acceptance" for BDD |
| Java | **Acceptance** | Spring Boot standard; BDD influence strong in Java |
| Rust | **Integration** (broad) | Cargo's `tests/` dir convention |
| C# | **Acceptance** | .NET standard; SpecFlow influence |
| Ruby | **Feature** or **System** | Rails convention; "feature" from Capybara/RSpec |

---

## 4. Language-Specific Recommendations

### JavaScript/TypeScript

**Recommended Names:**
1. **Validation Tests** (current usage) ✅ - Good choice
2. **E2E Tests** (industry standard)
3. **Acceptance Tests** (if using Cucumber/BDD)

**When to use "Validation":**
- ✅ Emphasizing data validation and edge cases
- ✅ Production-like input scenarios
- ✅ Behavioral complexity testing
- ✅ Distinguishing from full-stack E2E (browser testing)

**When to use "E2E":**
- ✅ Full-stack testing (frontend + backend)
- ✅ Browser automation (Playwright, Cypress)
- ✅ Complete user workflows

**Recommendation:**
```yaml
JS_TS_Test_Paths:
  unit: "Unit Tests" (isolation, mocked)
  integration: "Integration Tests" (component interactions)
  validation: "Validation Tests" (scenarios, data validation)
  e2e: "E2E Tests" (full-stack, browser) [optional 4th path]
```

---

### Python

**Recommended Names:**
1. **Functional Tests** (Django/Flask standard)
2. **Acceptance Tests** (BDD projects)
3. **System Tests** (enterprise)

**Framework Alignment:**
```python
# Django
# tests/functional/test_user_registration.py

# pytest-bdd
# tests/acceptance/test_user_registration.py

# Enterprise
# tests/system/test_api_integration.py
```

**Recommendation:**
```yaml
Python_Test_Paths:
  unit: "Unit Tests" (pytest, unittest)
  integration: "Integration Tests" (database, APIs)
  functional: "Functional Tests" (Django/Flask standard) ✅
  # OR
  acceptance: "Acceptance Tests" (if using BDD)
```

---

### Go

**Recommended Names:**
1. **E2E Tests** (most common)
2. **Acceptance Tests** (Ginkgo/BDD)

**Go Idioms:**
```go
// e2e/user_test.go
func TestUserRegistrationE2E(t *testing.T) { ... }

// acceptance/ (Ginkgo)
var _ = Describe("User Registration", ...)
```

**Recommendation:**
```yaml
Go_Test_Paths:
  unit: "Unit Tests" (in-package)
  integration: "Integration Tests" (cross-package)
  e2e: "E2E Tests" (complete scenarios) ✅
  # OR
  acceptance: "Acceptance Tests" (if using Ginkgo)
```

---

### Java

**Recommended Names:**
1. **Acceptance Tests** (Spring Boot standard)
2. **Functional Tests** (alternative)

**Framework Alignment:**
```java
// Spring Boot
@SpringBootTest
class UserAcceptanceTests { ... }

// Cucumber
@CucumberContextConfiguration
class AcceptanceTestConfiguration { ... }
```

**Recommendation:**
```yaml
Java_Test_Paths:
  unit: "Unit Tests" (JUnit, TestNG)
  integration: "Integration Tests" (Spring context)
  acceptance: "Acceptance Tests" (Spring Boot standard) ✅
```

---

### Rust

**Recommended Names:**
1. **Integration Tests** (Cargo standard, broad scope)
2. **E2E Tests** (if distinguishing from narrower integration)
3. **Functional Tests**

**Cargo Convention:**
```rust
// tests/ directory = integration tests (black box)
// tests/user_workflow.rs

// OR distinguish:
// tests/integration/ (component interactions)
// tests/e2e/ (complete scenarios)
```

**Recommendation:**
```yaml
Rust_Test_Paths:
  unit: "Unit Tests" (src/ with #[cfg(test)])
  integration: "Integration Tests" (tests/ directory) ✅
  # OR if distinguishing:
  integration: "Integration Tests" (component interactions)
  e2e: "E2E Tests" (complete scenarios)
```

---

### C#

**Recommended Names:**
1. **Acceptance Tests** (.NET standard)
2. **Functional Tests** (alternative)
3. **Integration Tests** (broad scope in .NET)

**Framework Alignment:**
```csharp
// xUnit + ASP.NET Core
public class UserAcceptanceTests : 
    IClassFixture<WebApplicationFactory<Startup>> { ... }

// SpecFlow
[Binding]
public class UserRegistrationSteps { ... }
```

**Recommendation:**
```yaml
CSharp_Test_Paths:
  unit: "Unit Tests" (xUnit, NUnit)
  integration: "Integration Tests" (DbContext, APIs)
  acceptance: "Acceptance Tests" (.NET standard) ✅
```

---

### Ruby

**Recommended Names:**
1. **System Tests** (Rails 5.1+ standard)
2. **Feature Tests** (RSpec + Capybara)
3. **Acceptance Tests** (Cucumber)

**Framework Alignment:**
```ruby
# Rails system tests
# test/system/user_registration_test.rb

# RSpec feature tests
# spec/features/user_registration_spec.rb

# Cucumber
# features/user_registration.feature
```

**Recommendation:**
```yaml
Ruby_Test_Paths:
  unit: "Unit Tests" (RSpec, Minitest)
  integration: "Integration Tests" (controller, model)
  system: "System Tests" (Rails 5.1+ standard) ✅
  # OR
  feature: "Feature Tests" (RSpec + Capybara)
```

---

## 5. Design Pattern for Universal Framework

### Configurable Path System

**Universal Standard:**
```yaml
# universal/standards/testing/test-generation/path-system.md

Test_Paths:
  path_1_unit:
    universal_name: "Unit Tests"
    characteristics: "Isolation, mocked dependencies"
    
  path_2_integration:
    universal_name: "Integration Tests"
    characteristics: "Component interactions, some real deps"
    
  path_3_validation:
    universal_name: "Validation Tests" (generic)
    language_specific_names:
      javascript: "validation" | "e2e" | "acceptance"
      typescript: "validation" | "e2e" | "acceptance"
      python: "functional" | "acceptance" | "system"
      go: "e2e" | "acceptance"
      java: "acceptance" | "functional"
      rust: "integration" (broad) | "e2e"
      csharp: "acceptance" | "functional"
      ruby: "system" | "feature" | "acceptance"
    characteristics: "Real-world scenarios, production-like data"
```

### Language Instructions Template

**Update Template:**
```markdown
# {LANGUAGE} Test Generation Instructions

## Test Path Naming

### Universal Paths

1. **Unit Tests** (universal)
2. **Integration Tests** (universal)
3. **{LANGUAGE_SPECIFIC_PATH_3_NAME}** (varies by language)

### {LANGUAGE} Path 3 Naming

**Recommended Name:** {PRIMARY_NAME}

**Alternative Names:** {ALTERNATIVE_NAMES}

**{LANGUAGE} Convention:**
```{language}
{EXAMPLE_TEST_STRUCTURE}
```

**Directory Structure:**
```
{DIRECTORY_CONVENTION}
```

### Path Selection Criteria

**Unit Path:**
- {UNIT_CRITERIA}

**Integration Path:**
- {INTEGRATION_CRITERIA}

**{PATH_3_NAME} Path:**
- {PATH_3_CRITERIA}
```

---

## 6. Implementation Strategy

### Step 1: Update Universal Standards

**File:** `universal/standards/testing/test-generation/path-system.md`

**Add section:**
```markdown
## Path 3: Validation/Acceptance/E2E Tests

### Universal Characteristics

Path 3 tests verify real-world scenarios with production-like data and behavior.

### Language-Specific Naming

Path 3 has **consistent characteristics** but **different names** across languages:

| Language | Primary Name | Directory Convention |
|----------|--------------|---------------------|
| JavaScript/TypeScript | Validation or E2E | tests/validation/ or tests/e2e/ |
| Python | Functional | tests/functional/ |
| Go | E2E | e2e/ |
| Java | Acceptance | src/test/acceptance/ |
| Rust | Integration (broad) | tests/ |
| C# | Acceptance | tests/Acceptance/ |
| Ruby | System or Feature | test/system/ or spec/features/ |

### Selecting the Right Name

**Factors to consider:**
1. **Language conventions** - Follow ecosystem standards
2. **Framework alignment** - Match testing framework terminology
3. **Team familiarity** - Use terms your team understands
4. **Documentation clarity** - Choose descriptive names

**All names refer to the same concept:** Testing real-world scenarios with production-like behavior.
```

### Step 2: Update Language Instructions

**For each language file:**

1. Add "Test Path Naming" section
2. Specify recommended Path 3 name
3. Provide alternative names
4. Show directory structure examples
5. Explain language-specific conventions

**Example for Python:**
```markdown
## Test Path Naming (Python)

### Universal Paths

1. **Unit Tests** - Isolation, mocked dependencies
2. **Integration Tests** - Component interactions
3. **Functional Tests** - Real-world scenarios ← Python convention

### Python Path 3: Functional Tests

**Why "Functional":**
- Django/Flask documentation standard
- "Function" = feature/capability testing
- Widely understood in Python community

**Alternative Names:**
- "Acceptance Tests" (if using pytest-bdd, behave)
- "System Tests" (enterprise contexts)
- "E2E Tests" (less common in Python)

**Directory Structure:**
```python
tests/
├── unit/          # Unit tests
├── integration/   # Integration tests
└── functional/    # Functional tests (Path 3)
```

### Path Selection in Python

Use **Functional Tests** when:
- Testing complete user workflows
- Using production-like data
- Validating complex business logic
- Testing Django views/URLs end-to-end
- Testing Flask routes with real database
```

### Step 3: Workflow Generation Updates

**Update `generate-test-workflow.py`:**

```python
def get_path_3_name(language):
    """Get language-specific Path 3 name."""
    path_3_names = {
        'javascript': 'validation',  # or 'e2e'
        'typescript': 'validation',  # or 'e2e'
        'python': 'functional',
        'go': 'e2e',
        'java': 'acceptance',
        'rust': 'integration',  # broad scope
        'csharp': 'acceptance',
        'ruby': 'system'  # or 'feature'
    }
    return path_3_names.get(language, 'validation')

def generate_metadata(language):
    """Generate workflow metadata with language-specific paths."""
    path_3_name = get_path_3_name(language)
    
    return {
        "name": f"test_generation_{language}_v1",
        "test_paths": ["unit", "integration", path_3_name],
        "path_3_info": {
            "name": path_3_name,
            "universal_concept": "Real-world scenario testing",
            "characteristics": [
                "Production-like data",
                "End-to-end behavior",
                "Complete workflows"
            ]
        }
    }
```

### Step 4: Documentation Updates

**Create:** `docs/Test-Path-Naming-Guide.md`

Quick reference for developers choosing test path names:

```markdown
# Test Path Naming Guide

## Quick Reference

| Language | Path 1 | Path 2 | Path 3 |
|----------|--------|--------|--------|
| JS/TS | unit | integration | **validation** or e2e |
| Python | unit | integration | **functional** |
| Go | unit | integration | **e2e** |
| Java | unit | integration | **acceptance** |
| Rust | unit | integration | **integration** (broad) or e2e |
| C# | unit | integration | **acceptance** |
| Ruby | unit | integration | **system** or feature |

**Bold** = Recommended primary name
```

---

## Conclusion

### Key Takeaways

1. **Pattern is Universal:** Three test paths (isolation → interaction → real-world) exist across all languages

2. **Naming Varies:** Path 3 has different names but consistent characteristics:
   - JS/TS: "Validation" or "E2E"
   - Python: "Functional"
   - Go: "E2E"
   - Java/C#: "Acceptance"
   - Ruby: "System" or "Feature"

3. **Your Choice is Valid:** JS/TS "Validation Tests" is a legitimate and descriptive name

4. **Framework Should Support Flexibility:** Universal standards + language-specific naming

### Recommendations

1. ✅ **Keep "Validation" for JS/TS** - It's descriptive and distinguishes from full E2E
2. ✅ **Document alternatives** - Help users understand equivalents
3. ✅ **Use language conventions** - Functional (Python), Acceptance (Java), etc.
4. ✅ **Maintain universal characteristics** - Same concept, different names

---

**Document End**

