# Non-Functional Requirements Test Cases

**Purpose:** Verification tests for all 44 NFRs across 11 categories  
**Date:** 2025-11-06

---

## Performance (NFR-P1 through NFR-P7)

**Test File:** `tests/ouroboros/performance/test_performance.py`

### NFR-P1: Server Cold Start Time (<30s p95)

**Test Case P1.1: Measure cold start latency**
- **Setup:** Clean environment, no cached state
- **Action:** Run 100 server startups, measure time from process start to "Server ready" log
- **Metric:** Calculate p95 latency
- **Pass Criteria:** p95 < 30 seconds
- **Evidence:** NFR-P1 validated

**Test Case P1.2: Identify startup bottlenecks**
- **Setup:** Profile server startup
- **Action:** Measure time for each subsystem init
- **Metric:** Report top 5 slowest components
- **Pass Criteria:** Informational (for optimization)
- **Evidence:** Bottleneck visibility

---

### NFR-P2: Config Load Time (<100ms p95)

**Test Case P2.1: Measure config validation latency**
- **Setup:** Realistic config/mcp.yaml
- **Action:** Run 1000 iterations of config load + Pydantic validation
- **Metric:** Calculate p95 latency
- **Pass Criteria:** p95 < 100ms
- **Evidence:** NFR-P2 validated

---

### NFR-P3: Search Latency - Hybrid Search (<200ms p95)

**Test Case P3.1: Measure hybrid search latency**
- **Setup:** StandardsIndex with 10,000 documents
- **Action:** Run 1000 search queries (diverse topics)
- **Metric:** Measure time from `pos_search_project()` call to results returned, calculate p95
- **Pass Criteria:** p95 < 200ms
- **Evidence:** NFR-P3 validated

**Test Case P3.2: Search latency under load**
- **Setup:** Index with 10K documents
- **Action:** Run 10 concurrent search threads
- **Metric:** Measure p95 latency under concurrency
- **Pass Criteria:** p95 < 300ms (degradation acceptable)
- **Evidence:** Load handling

---

### NFR-P4: Search Latency - Code Graph Traversal (<100ms p95)

**Test Case P4.1: Measure graph query latency**
- **Setup:** GraphIndex with 50,000 symbols
- **Action:** Run 1000 find_callers/find_dependencies queries
- **Metric:** Calculate p95 latency
- **Pass Criteria:** p95 < 100ms
- **Evidence:** NFR-P4 validated

---

### NFR-P5: Incremental Index Update Latency (<5s p95)

**Test File:** `tests/ouroboros/integration/test_file_watcher_latency.py`

**Test Case P5.1: Measure file-save-to-searchable latency**
- **Setup:** FileWatcher running, StandardsIndex initialized
- **Action:** 100 iterations: (1) Save file with unique term, (2) Search for term, (3) Measure time delta
- **Metric:** Calculate p95 of (search_success_time - file_save_time)
- **Pass Criteria:** p95 < 5 seconds
- **Evidence:** NFR-P5 validated (hot reload performance)

**Test Case P5.2: Incremental update latency for large files**
- **Setup:** FileWatcher running
- **Action:** Save 10MB file with unique term, measure discovery time
- **Metric:** Time to searchable
- **Pass Criteria:** < 10 seconds (relaxed for large files)
- **Evidence:** Large file handling

---

### NFR-P6: Prepend Generation Overhead (<5ms p95)

**Test Case P6.1: Measure prepend generation latency**
- **Setup:** Session with varying history (0, 10, 50, 100 queries)
- **Action:** Run 1000 iterations of prepend_generator.generate()
- **Metric:** Calculate p95 latency
- **Pass Criteria:** p95 < 5ms
- **Evidence:** NFR-P6 validated

---

### NFR-P7: Memory Usage (<2GB RSS)

**Test Case P7.1: Measure memory during normal operation**
- **Setup:** Server running typical 1-hour session (50 queries, mixed types)
- **Action:** Sample RSS every 30 seconds via `ps` or memory profiler
- **Metric:** Max RSS observed
- **Pass Criteria:** Max RSS < 2GB
- **Evidence:** NFR-P7 validated

**Test Case P7.2: Memory leak detection**
- **Setup:** Server running 24-hour soak test
- **Action:** Plot RSS over time
- **Metric:** RSS growth rate
- **Pass Criteria:** RSS stable or growing <100MB/hour
- **Evidence:** No memory leaks

---

## Reliability (NFR-R1 through NFR-R5)

**Test File:** `tests/ouroboros/integration/test_reliability_soak.py`

### NFR-R1: Uptime / Crash Rate (24+ hours)

**Test Case R1.1: 24-hour soak test**
- **Setup:** Server with simulated AI agent activity (5 queries/min)
- **Action:** Run for 24 hours, log any crashes/restarts
- **Metric:** Uptime duration
- **Pass Criteria:** No unplanned restarts for 24+ hours
- **Evidence:** NFR-R1 validated

**Test Case R1.2: Soak test under load**
- **Setup:** Server with high query rate (20 queries/min)
- **Action:** Run for 12 hours
- **Metric:** Uptime + performance degradation
- **Pass Criteria:** No crashes, latency increase <50%
- **Evidence:** Stability under load

---

### NFR-R2: Health Check Coverage (95%+ detection rate)

**Test File:** `tests/ouroboros/integration/test_index_health.py`

**Test Case R2.1: Inject corruption scenarios**
- **Setup:** Create 100 corruption scenarios (corrupted index files, missing parsers, invalid configs)
- **Action:** Run health checks for each
- **Metric:** Count of detected vs. undetected issues
- **Pass Criteria:** 95+ out of 100 detected
- **Evidence:** NFR-R2 validated

---

### NFR-R3: Auto-Repair Success Rate (90%+)

**Test Case R3.1: Measure auto-repair success**
- **Setup:** Inject 100 corruption scenarios that auto-repair should fix
- **Action:** Trigger auto-repair for each
- **Metric:** Count of successful repairs
- **Pass Criteria:** 90+ out of 100 repaired successfully
- **Evidence:** NFR-R3 validated

---

### NFR-R4: Graceful Degradation

**Test File:** `tests/ouroboros/integration/test_search_flow.py`

**Test Case R4.1: FTS index failure fallback**
- **Setup:** Delete FTS index files
- **Action:** Execute search query
- **Metric:** Search completes, warning logged
- **Pass Criteria:** Search returns results (vector-only), warning present
- **Evidence:** NFR-R4 validated

---

### NFR-R5: Data Integrity

**Test File:** `tests/ouroboros/integration/test_index_integrity.py`

**Test Case R5.1: Incremental vs. full rebuild consistency**
- **Setup:** Index with 1000 documents
- **Action:** (1) Full rebuild → hash index files, (2) Delete index, (3) Build incrementally (1 doc at a time) → hash again
- **Metric:** Compare hashes
- **Pass Criteria:** Hashes identical (byte-for-byte match)
- **Evidence:** NFR-R5 validated

---

## Security (NFR-S1 through NFR-S4)

### NFR-S1: Adversarial Design Enforcement (99%+ rejection rate)

**Test File:** `tests/ouroboros/validation/test_behavioral_engineering.py`

**Test Case S1.1: Gaming attempts rejected**
- **Setup:** Create 100 gaming attempts (hardcoded True, missing artifacts, fake booleans, etc.)
- **Action:** Submit evidence for validation
- **Metric:** Count of rejected vs. accepted
- **Pass Criteria:** 99+ out of 100 rejected
- **Evidence:** NFR-S1 validated

---

### NFR-S2: Query Sanitization (No PII)

**Test File:** `tests/security/test_query_logging.py`

**Test Case S2.1: PII not logged**
- **Setup:** Execute queries containing PII patterns (emails, SSNs, credit cards)
- **Action:** Check query_history.db and log files
- **Metric:** Manual review + regex scan for PII patterns
- **Pass Criteria:** No PII found in logs
- **Evidence:** NFR-S2 validated

---

### NFR-S3: Path Traversal Prevention

**Test File:** `tests/security/test_path_validation.py`

**Test Case S3.1: All traversal attempts blocked**
- **Setup:** Create 50 path traversal attempts (../../../etc/passwd, symlink attacks, etc.)
- **Action:** Submit to pos_filesystem tool
- **Metric:** Count of blocked vs. allowed
- **Pass Criteria:** 50 out of 50 blocked
- **Evidence:** NFR-S3 validated

---

### NFR-S4: Secrets Management

**Test File:** `tests/security/test_secrets.py`

**Test Case S4.1: No secrets in git**
- **Setup:** Scan entire repository
- **Action:** Run secret detection tool (e.g., detect-secrets)
- **Metric:** Number of secrets found
- **Pass Criteria:** 0 secrets
- **Evidence:** NFR-S4.1 validated

**Test Case S4.2: No secrets in logs**
- **Setup:** Run server with API keys configured
- **Action:** Scan log files for API key patterns
- **Metric:** Number of secrets found
- **Pass Criteria:** 0 secrets
- **Evidence:** NFR-S4.2 validated

---

## Scalability (NFR-SC1 through NFR-SC3)

**Test File:** `tests/ouroboros/performance/test_performance.py`

### NFR-SC1: Document Scaling (50K documents)

**Test Case SC1.1: Search performance with 50K docs**
- **Setup:** StandardsIndex with 50,000 documents
- **Action:** Run search query
- **Metric:** Latency
- **Pass Criteria:** p95 < 500ms (degradation acceptable)
- **Evidence:** NFR-SC1 validated

---

### NFR-SC2: Symbol Scaling (100K symbols)

**Test Case SC2.1: Graph query performance with 100K symbols**
- **Setup:** GraphIndex with 100,000 symbols
- **Action:** Run find_callers query
- **Metric:** Latency
- **Pass Criteria:** p95 < 300ms
- **Evidence:** NFR-SC2 validated

---

### NFR-SC3: Concurrent Query Handling

**Test File:** `tests/ouroboros/integration/test_thread_safety.py`

**Test Case SC3.1: 10 concurrent queries**
- **Setup:** Server with indexes initialized
- **Action:** Launch 10 threads executing queries simultaneously
- **Metric:** All complete without errors, latency degradation
- **Pass Criteria:** All succeed, p95 latency < 2x single-threaded
- **Evidence:** NFR-SC3 validated

---

## Maintainability (NFR-M1 through NFR-M5)

### NFR-M1: No Circular Dependencies

**Test File:** `tests/ouroboros/validation/test_architecture.py`

**Test Case M1.1: Detect circular imports**
- **Setup:** Full ouroboros codebase
- **Action:** Run static analysis tool to detect cycles
- **Metric:** Number of circular dependencies
- **Pass Criteria:** 0 circular dependencies
- **Evidence:** NFR-M1 validated

---

### NFR-M2: Clean Architecture (No cross-subsystem imports)

**Test Case M2.1: Enforce subsystem boundaries**
- **Setup:** Full ouroboros codebase
- **Action:** Check for imports from one subsystem/ directory to another (e.g., rag → workflow)
- **Metric:** Count of cross-subsystem imports
- **Pass Criteria:** 0 violations
- **Evidence:** NFR-M2 validated

---

### NFR-M3: Integration Test Coverage (≥60%)

**Test File:** `tests/conftest.py`

**Test Case M3.1: Measure integration test coverage**
- **Setup:** Run integration test suite with coverage enabled
- **Action:** Measure coverage across integration tests only
- **Metric:** Coverage percentage
- **Pass Criteria:** ≥60%
- **Evidence:** NFR-M3 validated

---

### NFR-M4: Error Message Quality

**Test File:** `tests/ouroboros/validation/test_error_messages.py`

**Test Case M4.1: All ActionableError messages include how_to_fix**
- **Setup:** Scan codebase for all ActionableError instantiations
- **Action:** Verify each has a non-empty how_to_fix field
- **Metric:** Count of errors with vs. without guidance
- **Pass Criteria:** 100% have how_to_fix
- **Evidence:** NFR-M4 validated

---

### NFR-M5: Documentation Coverage

**Test File:** `tests/ouroboros/validation/test_documentation.py`

**Test Case M5.1: All public APIs documented**
- **Setup:** Scan codebase for public functions/classes
- **Action:** Check for docstrings
- **Metric:** Percentage with docstrings
- **Pass Criteria:** ≥90%
- **Evidence:** NFR-M5 validated

---

## Usability (NFR-U1 through NFR-U4)

**Test File:** `tests/ouroboros/integration/test_usability.py`

### NFR-U1: Error Discoverability (1 search)

**Test Case U1.1: Error messages searchable**
- **Setup:** Trigger 20 common errors
- **Action:** For each error message, search standards index
- **Metric:** Count of errors with relevant results in top 5
- **Pass Criteria:** 18+ out of 20 discoverable
- **Evidence:** NFR-U1 validated

---

### NFR-U2: Fail-Fast Validation

**Test Case U2.1: All config errors at startup**
- **Setup:** Invalid config with 5 errors
- **Action:** Start server
- **Metric:** All 5 errors reported
- **Pass Criteria:** All errors shown, none discovered at runtime
- **Evidence:** NFR-U2 validated

---

### NFR-U3: Behavioral Feedback

**Test Case U3.1: Query diversity metrics visible**
- **Setup:** Execute 20 queries
- **Action:** Call get_server_info(action="behavioral_metrics")
- **Metric:** Returns diversity scores
- **Pass Criteria:** Metrics present and accurate
- **Evidence:** NFR-U3 validated

---

### NFR-U4: Tool Discoverability

**Test Case U4.1: Workflow metadata indexed**
- **Setup:** StandardsIndex with workflow files
- **Action:** Search for workflow capabilities
- **Metric:** Workflow metadata returned
- **Pass Criteria:** Relevant workflows discoverable
- **Evidence:** NFR-U4 validated

---

## Extensibility (NFR-E1 through NFR-E3)

**Test File:** `tests/ouroboros/integration/test_extensibility.py`

### NFR-E1: Config-Driven Languages

**Test Case E1.1: Add language with 1 YAML change**
- **Setup:** Add new language entry to config/mcp.yaml
- **Action:** Restart server, check if parser available
- **Metric:** Language usable
- **Pass Criteria:** No code changes required, language works
- **Evidence:** NFR-E1 validated

---

### NFR-E2: Pluggable Tools

**Test Case E2.1: Drop tool in directory**
- **Setup:** Create new tool file in tools/ directory
- **Action:** Restart server
- **Metric:** Tool registered and callable
- **Pass Criteria:** No core code changes needed
- **Evidence:** NFR-E2 validated

---

### NFR-E3: Custom Workflows

**Test Case E3.1: Create workflow without core changes**
- **Setup:** Create new workflow in workflows/ directory
- **Action:** Use pos_workflow to start it
- **Metric:** Workflow executes
- **Pass Criteria:** No core code changes needed
- **Evidence:** NFR-E3 validated

---

## Portability (NFR-PO1 through NFR-PO3)

**Test File:** `tests/ouroboros/integration/test_platform_compat.py`

### NFR-PO1: MacOS Support

**Test Case PO1.1: Run on macOS 12+**
- **Setup:** macOS 12+ machine
- **Action:** Install and run server
- **Metric:** Server starts successfully
- **Pass Criteria:** All features work
- **Evidence:** NFR-PO1 validated

---

### NFR-PO2: Linux Support

**Test Case PO2.1: Run on Ubuntu 20.04+**
- **Setup:** Ubuntu 20.04+ machine
- **Action:** Install and run server
- **Metric:** Server starts successfully
- **Pass Criteria:** All features work
- **Evidence:** NFR-PO2 validated

---

### NFR-PO3: WSL2 Support

**Test Case PO3.1: Run on Windows WSL2**
- **Setup:** Windows with WSL2
- **Action:** Install and run server
- **Metric:** Server starts successfully
- **Pass Criteria:** All features work
- **Evidence:** NFR-PO3 validated

---

## Compatibility (NFR-C1 through NFR-C3)

**Test File:** `tests/ouroboros/integration/test_compatibility.py`

### NFR-C1: MCP Protocol Compatibility

**Test Case C1.1: Works with all MCP clients**
- **Setup:** Test with Claude Desktop, Cline, Cursor
- **Action:** Execute tool calls
- **Metric:** All tools work
- **Pass Criteria:** Compatible with all clients
- **Evidence:** NFR-C1 validated

---

### NFR-C2: Index Format Backwards Compatibility

**Test Case C2.1: Read old indexes**
- **Setup:** LanceDB/DuckDB indexes from v1.0
- **Action:** Load with current server
- **Metric:** Indexes load successfully
- **Pass Criteria:** Backward compatible
- **Evidence:** NFR-C2 validated

---

### NFR-C3: Python Version Support

**Test Case C3.1: Run on Python 3.10+**
- **Setup:** Test on Python 3.10, 3.11, 3.12
- **Action:** Run server and test suite
- **Metric:** All pass
- **Pass Criteria:** Works on all versions
- **Evidence:** NFR-C3 validated

---

## Observability (NFR-O1 through NFR-O4)

**Test File:** `tests/ouroboros/integration/test_observability.py`

### NFR-O1: Structured Logging

**Test Case O1.1: JSON logs with context**
- **Setup:** Enable JSON logging
- **Action:** Execute operations, check logs
- **Metric:** Logs parseable as JSON with context fields
- **Pass Criteria:** All logs structured
- **Evidence:** NFR-O1 validated

---

### NFR-O2: Query Metrics Tracking

**Test Case O2.1: All queries logged with metadata**
- **Setup:** Execute 10 queries
- **Action:** Check query_history.db
- **Metric:** All 10 present with metadata
- **Pass Criteria:** 100% logged
- **Evidence:** NFR-O2 validated

---

### NFR-O3: Performance Metrics

**Test Case O3.1: Latency metrics logged**
- **Setup:** Execute operations
- **Action:** Check logs for p50/p95/p99 metrics
- **Metric:** Latency metrics present
- **Pass Criteria:** Metrics logged
- **Evidence:** NFR-O3 validated

---

### NFR-O4: Behavioral Metrics

**Test Case O4.1: Query diversity trends tracked**
- **Setup:** Execute 20 queries
- **Action:** Call get_server_info(action="behavioral_metrics")
- **Metric:** Diversity trends visible
- **Pass Criteria:** Metrics accurate
- **Evidence:** NFR-O4 validated

---

## Testability (NFR-T1 through NFR-T3)

**Test File:** `tests/ouroboros/validation/test_testability.py`

### NFR-T1: Unit Test Isolation

**Test Case T1.1: Unit tests run without external resources**
- **Setup:** Run unit tests with no network, no DB
- **Action:** Execute unit test suite
- **Metric:** All pass
- **Pass Criteria:** No external dependencies
- **Evidence:** NFR-T1 validated

---

### NFR-T2: Integration Test Coverage (≥70%)

**Test Case T2.1: Measure integration coverage**
- **Setup:** Run integration test suite with coverage
- **Action:** Measure coverage
- **Metric:** Coverage percentage
- **Pass Criteria:** ≥70%
- **Evidence:** NFR-T2 validated

---

### NFR-T3: Performance Test Repeatability

**Test Case T3.1: Low variance across runs**
- **Setup:** Run performance test 10 times
- **Action:** Measure latency variance
- **Metric:** Coefficient of variation
- **Pass Criteria:** <5% variance
- **Evidence:** NFR-T3 validated

---

## Test Summary

- **Total Non-Functional Requirements:** 44
- **Total Test Cases Defined:** 65
- **Performance Tests:** 9
- **Reliability Tests:** 5
- **Security Tests:** 5
- **Other NFR Tests:** 46

**Critical Tests:**
- **NFR-P5:** File-save-to-searchable latency (validates FileWatcher performance)
- **NFR-R1:** 24-hour uptime (validates stability)
- **NFR-S1:** Adversarial design enforcement (validates evidence validation)
- **NFR-M3:** Integration test coverage (validates testing rigor)

