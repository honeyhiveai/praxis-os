# Production Code Checklist - Universal AI Safety Pattern

**Timeless checklist for AI assistants to ensure all code is production-grade.**

## Core Principle

**"AI has no excuse for shortcuts."**

Unlike human developers:
- AI doesn't get tired (no fatigue-induced errors)
- AI doesn't have time pressure (microseconds vs hours)
- AI doesn't have cognitive load limits (can evaluate 100+ scenarios instantly)
- Quality checks add negligible latency (~5 seconds) vs debugging time (hours/days)

**Therefore: Every line of AI-written code must be production-grade from the start.**

---

## The 5-Second Rule

**Before writing ANY code, spend 5 seconds asking:**

1. **Shared state?** → Concurrency check
2. **Dependency?** → Version justification
3. **How does this fail?** → Failure modes
4. **Resources?** → Lifecycle management
5. **Tests?** → Coverage plan

**5 seconds of AI thinking > Hours of human debugging.**

---

## Tier 1: Universal Checks (MANDATORY FOR ALL CODE)

### Check 1: Shared State Analysis

**Question:** Does this code access any shared state?

**Shared state includes:**
- Class-level variables (shared across instances)
- Module-level/global variables
- File system (reading/writing files)
- Databases, caches, vector stores
- Network connections, connection pools
- Any data structure accessed by multiple execution contexts

**If YES → Concurrency analysis REQUIRED:**
- [ ] What happens if 2+ contexts access this simultaneously?
- [ ] Does the library handle concurrency internally? (Research - NEVER assume)
- [ ] Do I need external synchronization? (locks, atomics, channels)
- [ ] How do I test concurrent access?

**Document concurrency safety:**
```
// CONCURRENCY: Thread-safe via [mechanism]
// Tested with: [test name or reasoning]
```

**See:** `universal/standards/concurrency/shared-state-analysis.md`

---

### Check 2: Dependency Analysis

**Question:** Does this code add or modify an external dependency?

**If YES → Version justification REQUIRED:**
- [ ] Why this specific version or version range?
- [ ] What changed between versions that matters?
- [ ] What's the stability/maturity level? (alpha, beta, stable)
- [ ] Are there known issues in this version?
- [ ] Does this introduce breaking changes?

**Version specification principles:**
- **Preferred:** Compatible version range (e.g., `~1.2.0` allows 1.2.x)
- **Acceptable:** Explicit upper bound (e.g., `>=1.2.0,<2.0.0`)
- **Rare:** Exact pin (only for critical stability or known incompatibility)
- **FORBIDDEN:** Open-ended (e.g., `>=1.2.0` - non-deterministic builds)

**Document dependency choices:**
```
// Dependency: package ~1.2.0
// Justification: Latest stable, fixes concurrency bug in 1.1.x
// Breaking changes expected in 2.0.0 (major version bump)
```

**See:** `universal/standards/failure-modes/graceful-degradation.md`

---

### Check 3: Failure Mode Analysis

**Question:** How does this code fail?

**EVERY code block must answer:**
- [ ] What happens if the external service is down?
- [ ] What happens if the network times out?
- [ ] What happens if input is malformed/invalid?
- [ ] What happens if resources are exhausted (memory, disk, connections)?
- [ ] What's the graceful degradation path?

**Required pattern:**
```
try:
    result = risky_operation()
except SpecificException as e:
    log_error(f"Operation failed: {e}")
    result = fallback_strategy()  // Graceful degradation
```

**Anti-pattern (FORBIDDEN):**
```
try:
    result = risky_operation()
except:  // Bare except, no logging, no degradation
    pass
```

**See:** `universal/standards/failure-modes/` (retry, circuit-breakers, timeouts)

---

### Check 4: Resource Lifecycle Management

**Question:** Does this code manage resources (connections, files, locks)?

**If YES → Lifecycle management REQUIRED:**
- [ ] How are resources acquired? (open, connect, acquire)
- [ ] How are resources released? (close, disconnect, release)
- [ ] What happens during reload/restart?
- [ ] What happens if cleanup fails?
- [ ] Potential for resource leaks?

**Required pattern (language-specific syntax varies):**
```
// Pattern 1: Automatic cleanup (preferred)
with resource_manager() as resource:
    resource.do_work()

// Pattern 2: Explicit cleanup with guarantee
resource = None
try:
    resource = acquire_resource()
    resource.do_work()
finally:
    if resource:
        resource.cleanup()
```

**Anti-pattern (FORBIDDEN):**
```
resource = acquire_resource()
resource.do_work()
// No cleanup! Resource leak!
```

---

### Check 5: Test Coverage

**Question:** How do I validate this works?

**EVERY code change must have:**
- [ ] Unit test for happy path
- [ ] Unit test for failure modes
- [ ] Integration test if touching external systems
- [ ] Concurrent access test if touching shared state

**Minimum acceptable:**
```
test_happy_path():
    result = my_function(valid_input)
    assert result == expected_output

test_failure_mode():
    expect_error(SpecificException):
        my_function(invalid_input)
```

**See:** `universal/standards/testing/` (test-pyramid, test-doubles, integration)

---

## Tier 2: Infrastructure Code Checks

**Apply Tier 1 + Tier 2 when code involves:**
- Datastores (SQL, NoSQL, vector stores, caches)
- Background threads or async operations
- File I/O with hot reload or watching
- Network connections with pooling
- External APIs with rate limits

### Check 6: Datastore Concurrency

**Questions:**
- [ ] Does the datastore library handle concurrent access internally?
- [ ] Do I need external synchronization?
- [ ] What happens during index rebuild/schema migration?
- [ ] How do I test concurrent read/write scenarios?

**Research protocol:**
1. Read library documentation section on concurrency
2. Search for "thread-safe" or "concurrent" in library docs
3. Check issue tracker for concurrency-related bugs
4. **When in doubt: Add external synchronization**

**Example pattern (pseudocode):**
```
class DataStore:
    initialize():
        lock = create_reentrant_lock()
        rebuilding_flag = create_event_flag()
    
    read_data(query):
        if rebuilding_flag.is_set():
            rebuilding_flag.wait(timeout=30)
        with lock:
            return vector_search(query)
    
    reload_index():
        with lock:
            rebuilding_flag.set()
            try:
                rebuild_logic()
            finally:
                rebuilding_flag.clear()
```

---

### Check 7: Connection Lifecycle

**Questions:**
- [ ] Are connections pooled or per-request?
- [ ] What's the connection timeout strategy?
- [ ] How are stale connections detected and cleaned?
- [ ] What happens during service restart?

**Required pattern:**
```
reload_connection():
    with lock:
        // Clean up old connections
        if connection_exists:
            close_connection()
        if pool_exists:
            close_pool()
        
        // Reconnect
        connection = create_connection()
```

---

### Check 8: Async/Threading

**Questions:**
- [ ] Are there any race conditions between contexts?
- [ ] Are there any deadlock scenarios?
- [ ] How do I gracefully shut down background workers?
- [ ] Are daemon threads appropriate or do I need proper cleanup?

**Required pattern:**
```
class BackgroundWorker:
    initialize():
        stop_event = create_event_flag()
        thread = create_thread(work_function, daemon=True)
        thread.start()
    
    work_function():
        while not stop_event.is_set():
            do_work()
            sleep(interval)
    
    shutdown():
        stop_event.set()
        thread.join(timeout=5)
```

---

## Tier 3: Complex Systems Checks

**Apply Tier 1 + Tier 2 + Tier 3 when code involves:**
- New architectural patterns (not yet in codebase)
- Distributed systems (multiple processes/machines)
- Performance-critical paths (hot loops, high throughput)
- Security-sensitive operations (auth, credentials, encryption)

### Check 9: Architecture Review

**When to use design validation:**
- Introducing new design patterns
- Adding new infrastructure components
- Modifying critical paths
- Refactoring >200 lines of code

**Validation should ensure:**
- Failure mode analysis complete
- Design alternatives considered
- Implementation with quality gates
- Performance and security reviewed

---

### Check 10: Performance Analysis

**Questions:**
- [ ] What's the algorithmic complexity (Big O)?
- [ ] Are there any N+1 query problems?
- [ ] What's the memory footprint with large inputs?
- [ ] How does this scale with concurrent requests?

**Validation:**
- [ ] Benchmark with realistic data sizes
- [ ] Profile memory usage
- [ ] Stress test with concurrent load

---

### Check 11: Security Analysis

**Questions:**
- [ ] Are credentials ever logged or committed?
- [ ] Is user input sanitized?
- [ ] Are secrets properly encrypted at rest?
- [ ] Are there any injection vulnerabilities?

**Required:**
- [ ] Use environment variables for secrets (NEVER hardcode)
- [ ] Use parameterized queries (NEVER string concatenation)
- [ ] Validate and sanitize all external input
- [ ] Audit logging for security events

**See:** `universal/standards/ai-safety/credential-file-protection.md`

---

## Anti-Patterns (FORBIDDEN)

### 1. "Prototype Mode" Thinking

```
// ❌ BAD: "This is just a quick prototype"
connect_database():
    return open_connection("db.sqlite")  // No error handling, no cleanup
```

**Why forbidden:** AI has no time pressure. There is no "quick prototype" - only production code.

---

### 2. Assuming Thread-Safety

```
// ❌ BAD: "The library probably handles this"
class Cache:
    initialize():
        data = create_dictionary()  // Assumes dictionary is thread-safe
```

**Why forbidden:** NEVER assume. Research or add synchronization.

---

### 3. Broad Version Ranges

```
// ❌ BAD: dependency specification
package>=1.0.0  // Allows ANY version >= 1.0.0 (non-deterministic)
```

**Why forbidden:** Non-deterministic builds. Use compatible version ranges.

---

### 4. Silent Failures

```
// ❌ BAD: Fails silently
try:
    result = api_call()
except:
    pass  // User has no idea what went wrong
```

**Why forbidden:** Debugging nightmare. Log errors, degrade gracefully.

---

### 5. Resource Leaks

```
// ❌ BAD: No cleanup
file = open("data.txt")
data = file.read()
// file never closed!
```

**Why forbidden:** Use automatic cleanup mechanisms (RAII, with statements, defer, etc.).

---

## Commit Documentation

**Every commit must document checklist completion:**

```
type(scope): brief description

Tier 1 Checks:
- Concurrency: [Thread-safe via RLock | No shared state]
- Dependencies: [Added package~X.Y.Z because reason | No changes]
- Failure Modes: [Graceful degradation via fallback | N/A]
- Resources: [Proper cleanup via context manager | N/A]
- Tests: [Added test_feature_happy + test_feature_failure]

Tier 2 Checks (if applicable):
- Datastore Concurrency: [External locking added | N/A]
- Connection Lifecycle: [Cleanup before reload | N/A]
- Async/Threading: [No race conditions, validated with test | N/A]

Tier 3 Checks (if applicable):
- Architecture: [Design validated | N/A]
- Performance: [O(n) complexity, benchmarked | N/A]
- Security: [Credentials from env vars, input sanitized | N/A]
```

---

## Quick Reference

### Pre-Code Checklist (2 minutes max)

```
Before writing code:
□ Read shared state patterns (shared-state-analysis.md)
□ Read failure mode patterns (graceful-degradation.md)
□ Read relevant architecture patterns (SOLID, DI, etc.)
□ Verify import paths exist (import-verification-rules.md)
□ Check for similar code in codebase (grep/search)

While writing code:
□ Add concurrency safety comments
□ Add failure handling (try/catch with degradation)
□ Add resource cleanup (with/finally/defer)
□ Document dependency versions
□ Plan test coverage

After writing code:
□ Write tests (happy path + failure modes)
□ Run linter/formatter
□ Check for resource leaks
□ Review concurrency safety
□ Document in commit message
```

---

## Related Standards

- **[Shared State Analysis](../concurrency/shared-state-analysis.md)** - Analyzing concurrent access
- **[Graceful Degradation](../failure-modes/graceful-degradation.md)** - Handling failures
- **[Git Safety Rules](git-safety-rules.md)** - Safe git operations
- **[Credential Protection](credential-file-protection.md)** - Never write to credential files
- **[Import Verification](import-verification-rules.md)** - Verify imports before use

---

## Summary

**This is not optional. This is the baseline for all AI-authored code.**

Every line of code written by AI should be production-grade because:
1. AI has no time pressure
2. AI doesn't get tired
3. AI can evaluate 100+ scenarios instantly
4. Quality checks take seconds, debugging takes hours

**AI has no excuse for shortcuts.**

---

**Production code is the only code. There is no "prototype" or "draft" code when AI writes it. Every line should be production-ready from the start.**
