# RAG Content Optimization - Test Query Suite

**Purpose:** Comprehensive test queries to validate RAG optimization improvements  
**Date:** 2025-10-11  
**Total Queries:** 50

---

## Query Organization

Queries are organized by content category, with expected top result(s) documented.

---

## Category 1: Architecture Standards (8 queries)

### Query 1.1: Basic SOLID
**Query:** `"how to design maintainable classes"`  
**Expected Top Result:** `solid-principles.md` → "How to Apply Single Responsibility Principle"  
**Category:** Architecture

### Query 1.2: API Design
**Query:** `"API design best practices"`  
**Expected Top Result:** `api-design-principles.md` → "What are Universal API Design Principles?"  
**Category:** Architecture

### Query 1.3: Dependency Injection
**Query:** `"how to make code testable"`  
**Expected Top Result:** `dependency-injection.md` OR `solid-principles.md` → DI sections  
**Category:** Architecture

### Query 1.4: Separation of Concerns
**Query:** `"how to organize code into layers"`  
**Expected Top Result:** `separation-of-concerns.md` → "How to Apply Layered Architecture?"  
**Category:** Architecture

### Query 1.5: Constructor Injection
**Query:** `"dependency injection constructor pattern"`  
**Expected Top Result:** `dependency-injection.md` → "How to Use Constructor Injection"  
**Category:** Architecture

### Query 1.6: REST API Design
**Query:** `"REST API HTTP methods"`  
**Expected Top Result:** `api-design-principles.md` → "How to Use HTTP Methods Correctly"  
**Category:** Architecture

### Query 1.7: Circular Dependencies
**Query:** `"how to resolve circular dependencies"`  
**Expected Top Result:** `dependency-injection.md` → "How to Resolve Circular Dependencies"  
**Category:** Architecture

### Query 1.8: MVC Pattern
**Query:** `"MVC pattern separation of concerns"`  
**Expected Top Result:** `separation-of-concerns.md` → "How to Use MVC"  
**Category:** Architecture

---

## Category 2: Testing Standards (7 queries)

### Query 2.1: Test Pyramid
**Query:** `"test pyramid ratios"`  
**Expected Top Result:** `test-pyramid.md` → "How to Calculate Test Ratios"  
**Category:** Testing

### Query 2.2: Integration Testing
**Query:** `"how to test database integration"`  
**Expected Top Result:** `integration-testing.md` → "How to Test Database Integration"  
**Category:** Testing

### Query 2.3: Test Doubles
**Query:** `"difference between mock and stub"`  
**Expected Top Result:** `test-doubles.md` → "Type 2: Stub" and "Type 4: Mock"  
**Category:** Testing

### Query 2.4: Property-Based Testing
**Query:** `"property based testing vs example based"`  
**Expected Top Result:** `property-based-testing.md` → TL;DR or main sections  
**Category:** Testing

### Query 2.5: Unit Test Speed
**Query:** `"how fast should unit tests run"`  
**Expected Top Result:** `test-pyramid.md` → "How Fast Should Tests Run?"  
**Category:** Testing

### Query 2.6: Test Isolation
**Query:** `"how to isolate tests from database"`  
**Expected Top Result:** `integration-testing.md` → "How to Choose a Test Database Strategy?"  
**Category:** Testing

### Query 2.7: When to Use Mocks
**Query:** `"when to use mocks vs fakes"`  
**Expected Top Result:** `test-doubles.md` → "How Do Test Doubles Compare?"  
**Category:** Testing

---

## Category 3: Concurrency Standards (6 queries)

### Query 3.1: Race Conditions
**Query:** `"how to detect race conditions"`  
**Expected Top Result:** `race-conditions.md` → "How to Detect Race Conditions?"  
**Category:** Concurrency

### Query 3.2: Deadlocks
**Query:** `"prevent deadlocks in concurrent code"`  
**Expected Top Result:** `deadlocks.md` → "How to Prevent Deadlocks?"  
**Category:** Concurrency

### Query 3.3: Lock Types
**Query:** `"mutex vs read-write lock"`  
**Expected Top Result:** `locking-strategies.md` → "How Do Locking Strategies Compare?"  
**Category:** Concurrency

### Query 3.4: Shared State
**Query:** `"how to identify shared mutable state"`  
**Expected Top Result:** `shared-state-analysis.md` → "How to Identify Shared State?"  
**Category:** Concurrency

### Query 3.5: Lock Ordering
**Query:** `"lock ordering to prevent deadlock"`  
**Expected Top Result:** `deadlocks.md` → "How to Use Lock Ordering"  
**Category:** Concurrency

### Query 3.6: Thread Safety
**Query:** `"how to make code thread safe"`  
**Expected Top Result:** `race-conditions.md` OR `shared-state-analysis.md` → prevention strategies  
**Category:** Concurrency

---

## Category 4: Database & Performance (4 queries)

### Query 4.1: N+1 Queries
**Query:** `"avoid N+1 query problem"`  
**Expected Top Result:** `database-patterns.md` → "How to Avoid the N+1 Query Problem"  
**Category:** Database

### Query 4.2: Database Indexes
**Query:** `"when to use database indexes"`  
**Expected Top Result:** `database-patterns.md` → "How to Use Database Indexes Effectively"  
**Category:** Database

### Query 4.3: Performance Optimization
**Query:** `"how to optimize slow code"`  
**Expected Top Result:** `optimization-patterns.md` → "What Is the Performance Optimization Process?"  
**Category:** Performance

### Query 4.4: Premature Optimization
**Query:** `"premature optimization is evil"`  
**Expected Top Result:** `optimization-patterns.md` → "What Performance Anti-Patterns Should I Avoid?"  
**Category:** Performance

---

## Category 5: Failure Modes & Resilience (5 queries)

### Query 5.1: Retry Strategies
**Query:** `"exponential backoff with jitter"`  
**Expected Top Result:** `retry-strategies.md` → "How to Implement Exponential Backoff with Jitter"  
**Category:** Failure Modes

### Query 5.2: Circuit Breakers
**Query:** `"circuit breaker pattern"`  
**Expected Top Result:** `circuit-breakers.md` → "What are the Three Circuit Breaker States?"  
**Category:** Failure Modes

### Query 5.3: Graceful Degradation
**Query:** `"graceful degradation vs fail fast"`  
**Expected Top Result:** `graceful-degradation.md` → "How Does Graceful Degradation Work?"  
**Category:** Failure Modes

### Query 5.4: Timeout Patterns
**Query:** `"how to set timeouts for operations"`  
**Expected Top Result:** `timeout-patterns.md` → "How Should I Configure Timeouts?"  
**Category:** Failure Modes

### Query 5.5: Transient Failures
**Query:** `"how to distinguish transient vs permanent failures"`  
**Expected Top Result:** `retry-strategies.md` → "How to Distinguish Transient vs Permanent Failures"  
**Category:** Failure Modes

---

## Category 6: Security (2 queries)

### Query 6.1: OWASP Top 10
**Query:** `"OWASP top 10 security threats"`  
**Expected Top Result:** `security-patterns.md` → "What Are the OWASP Top 10 Security Threats?"  
**Category:** Security

### Query 6.2: Input Validation
**Query:** `"how to validate user input"`  
**Expected Top Result:** `security-patterns.md` → "How to Validate User Input"  
**Category:** Security

---

## Category 7: Documentation (4 queries)

### Query 7.1: API Documentation
**Query:** `"what to document in API endpoints"`  
**Expected Top Result:** `api-documentation.md` → "What Should I Document for Every Endpoint?"  
**Category:** Documentation

### Query 7.2: Code Comments
**Query:** `"when to write code comments"`  
**Expected Top Result:** `code-comments.md` → "When Should I Write Comments?"  
**Category:** Documentation

### Query 7.3: README Structure
**Query:** `"README template structure"`  
**Expected Top Result:** `readme-templates.md` → "What Is the Universal README Structure?"  
**Category:** Documentation

### Query 7.4: Comment Quality
**Query:** `"explain why not what in comments"`  
**Expected Top Result:** `code-comments.md` → "What Is the Golden Rule for Comments?"  
**Category:** Documentation

---

## Category 8: Meta-Framework & Workflows (5 queries)

### Query 8.1: Command Language
**Query:** `"workflow command language symbols"`  
**Expected Top Result:** `command-language.md` → "What Is Command Language?"  
**Category:** Meta-Framework

### Query 8.2: Horizontal Decomposition
**Query:** `"break down complex tasks into modules"`  
**Expected Top Result:** `horizontal-decomposition.md` → "What Is Horizontal Decomposition?"  
**Category:** Meta-Framework

### Query 8.3: Validation Gates
**Query:** `"checkpoint validation gates workflows"`  
**Expected Top Result:** `validation-gates.md` → "What Is a Validation Gate?"  
**Category:** Meta-Framework

### Query 8.4: Workflow Creation
**Query:** `"how to create prAxIs OS workflow"`  
**Expected Top Result:** `workflow-construction-standards.md` → "How to Create a New Workflow?"  
**Category:** Workflows

### Query 8.5: Workflow Metadata
**Query:** `"workflow metadata.json schema"`  
**Expected Top Result:** `workflow-metadata-standards.md` → "What Is the Workflow Metadata Schema?"  
**Category:** Workflows

---

## Category 9: AI Safety Standards (5 queries)

### Query 9.1: Production Checklist
**Query:** `"production code checklist AI"`  
**Expected Top Result:** `production-code-checklist.md` → TL;DR "The 5-Second Rule"  
**Category:** AI Safety

### Query 9.2: Credential Protection
**Query:** `"AI modifying credential files"`  
**Expected Top Result:** `credential-file-protection.md` → "What Operations Are ABSOLUTELY FORBIDDEN?"  
**Category:** AI Safety

### Query 9.3: Git Safety
**Query:** `"can AI use git reset"`  
**Expected Top Result:** `git-safety-rules.md` → "What Git Operations Are STRICTLY FORBIDDEN?"  
**Category:** AI Safety

### Query 9.4: Import Verification
**Query:** `"verify imports before using them"`  
**Expected Top Result:** `import-verification-rules.md` → "How to Verify Imports?"  
**Category:** AI Safety

### Query 9.5: Date Usage
**Query:** `"how to get current date in AI code"`  
**Expected Top Result:** `date-usage-policy.md` → "How to Get the Current Date?"  
**Category:** AI Safety

---

## Category 10: Installation & Setup (2 queries)

### Query 10.1: Gitignore Requirements
**Query:** `"what to add to gitignore for prAxIs OS"`  
**Expected Top Result:** `gitignore-requirements.md` → "Required Entries"  
**Category:** Installation

### Query 10.2: prAxIs OS Update
**Query:** `"how to update prAxIs OS"`  
**Expected Top Result:** `update-procedures.md` → "How to Execute an prAxIs OS Update"  
**Category:** Installation

---

## Category 11: Usage & Behavioral Guides (2 queries)

### Query 11.1: AI Agent Behavior
**Query:** `"how to behave as AI agent in prAxIs OS"`  
**Expected Top Result:** `ai-agent-quickstart.md` → TL;DR or behavioral scenarios  
**Category:** Usage

### Query 11.2: Creating Specs
**Query:** `"how to write design specifications"`  
**Expected Top Result:** `creating-specs.md` → "What Is the Standard Spec Directory Structure?"  
**Category:** Usage

---

## Success Metrics

**Query Success Rate Calculation:**
```
Success = Query returns expected file/section in top 3 results
Success Rate = (Successful Queries / Total Queries) × 100%
```

**Target Success Rates:**
- **Baseline (Pre-Optimization):** <50%
- **Post-Optimization Goal:** ≥90%

**Query Efficiency:**
- **Metric:** Average number of queries needed to get a complete answer
- **Baseline:** 3-5 queries (multiple reformulations needed)
- **Target:** 1-2 queries (first query successful, maybe one refinement)

---

## Test Execution Protocol

1. **Clear RAG cache** (if applicable) before testing
2. **Execute query** via `search_standards(query)`
3. **Record top 3 results** (file + section + relevance score)
4. **Mark success/failure:**
   - ✅ Success: Expected result in top 3
   - ❌ Failure: Expected result not in top 3 OR wrong content
5. **Note any issues:**
   - Wrong file ranking higher
   - Expected file not found
   - Ambiguous query needing refinement

---

**Total Queries:** 50  
**Coverage:** All 13 content categories  
**Expected Baseline Success Rate:** <50%  
**Target Post-Optimization Success Rate:** ≥90%

