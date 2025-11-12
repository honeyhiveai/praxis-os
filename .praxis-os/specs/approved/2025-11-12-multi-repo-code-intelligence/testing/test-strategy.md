# Test Strategy

**Project:** Multi-Repo Code Intelligence for Instrumentor Analysis  
**Date:** 2025-11-12  
**Purpose:** Comprehensive testing strategy and methodology

---

## 1. Testing Overview

### 1.1 Test Objectives

**Primary Goals:**
1. **Functional Correctness:** Verify all 10 functional requirements met
2. **Performance Validation:** Ensure all performance targets achieved (p95 latency, extraction time)
3. **Reliability:** Validate error handling, partial degradation, rollback capability
4. **Scalability:** Confirm system scales to 270 instrumentors with 437K chunks
5. **Security:** Verify no credential leaks, path traversal prevention
6. **Backward Compatibility:** Ensure single-repo usage still works

### 1.2 Test Scope

**In Scope:**
- All 39 requirements (10 FR + 29 NFR)
- Multi-repository indexing
- Partition management (CRUD operations)
- Cross-repo queries and graph traversal
- Incremental indexing performance
- Extraction workflows
- Configuration validation
- Error handling and graceful degradation

**Out of Scope:**
- UI testing (no UI for MVP)
- Real-time sync (batch/cron only for MVP)
- Cross-language call graphs (Python-only for MVP)
- External API testing (GitHub API, GitLab API)

---

## 2. Test Pyramid

### 2.1 Test Distribution

**70% Unit Tests (Fast, Isolated)**
- Individual components tested in isolation
- Mocked dependencies
- Fast execution (< 1 second per test)
- High coverage of edge cases

**20% Integration Tests (Multi-Component)**
- Multiple components working together
- Real database connections (test databases)
- Realistic data scenarios
- End-to-end workflows within subsystems

**10% E2E Tests (Full System)**
- Complete user workflows
- Real Git repositories
- Production-like environment
- Slow execution (minutes per test)
- Focus on critical paths

### 2.2 Rationale

- **Fast feedback:** Unit tests run in < 30 seconds total
- **Comprehensive coverage:** Unit tests catch 70% of bugs
- **Realistic validation:** Integration tests catch integration issues
- **Production confidence:** E2E tests validate real-world scenarios

---

## 3. Unit Testing Strategy

### 3.1 Components to Unit Test

| Component | Test Count | Mock Dependencies |
|-----------|------------|-------------------|
| RepositoryTracker | 8 | DuckDB (in-memory) |
| RepositorySyncer | 10 | Git operations (mocked) |
| CodePartition | 12 | Sub-indexes (mocked) |
| IncrementalIndexer | 15 | Partition, Tracker, Syncer |
| PartitionManager | 10 | Filesystem (temp dirs) |
| Config Models (Pydantic) | 8 | None (pure validation) |

**Total Unit Tests:** ~63

### 3.2 Unit Test Pattern

```python
# Example: Unit test for RepositoryTracker

import pytest
from ouroboros.subsystems.rag.code.tracker import RepositoryTracker
from pathlib import Path

@pytest.fixture
def tracker():
    """Fixture with in-memory DuckDB."""
    return RepositoryTracker(db_path=":memory:")

def test_mark_indexed_creates_state(tracker):
    """Test marking repository as indexed creates state record."""
    tracker.mark_indexed(
        repo_name="test-repo",
        commit_hash="abc123",
        file_count=100
    )
    
    state = tracker.get_state("test-repo")
    assert state is not None
    assert state.commit_hash == "abc123"
    assert state.file_count == 100
    assert state.status == "indexed"

def test_get_changed_files_first_time_returns_all(tracker, mock_repo):
    """Test first-time index returns all files (no prior state)."""
    repo_config = RepositoryConfig(name="new-repo", path="/path/to/repo")
    
    # No prior state
    assert tracker.get_state("new-repo") is None
    
    # Should return all files
    changed = tracker.get_changed_files(repo_config)
    assert len(changed) == len(mock_repo.all_files)
```

### 3.3 Mocking Strategy

**What to Mock:**
- External services (Git, network)
- Slow operations (file I/O, database)
- Non-deterministic behavior (timestamps, UUIDs)

**What NOT to Mock:**
- Business logic
- Data structures
- Algorithms

**Mock Libraries:**
- `unittest.mock` for Python mocks
- `pytest-mock` for pytest integration
- `responses` for HTTP mocking (if needed)

---

## 4. Integration Testing Strategy

### 4.1 Integration Test Scenarios

**Partition Lifecycle (5 tests):**
1. Create partition → Add repo → Query → Verify
2. Update partition (add 2nd repo) → Query both → Verify
3. Remove repo → Verify deleted from all 3 indexes
4. Soft delete partition → Archive → Restore → Verify
5. Cross-partition query → Verify aggregation

**Incremental Indexing (4 tests):**
1. Cold start → Modify files → Incremental update → Verify performance
2. Parse error handling → Skip file → Continue with repo
3. Sync failure → Mark failed → Continue with other repos
4. Parse-once-index-thrice → Verify all 3 indexes updated

**Cross-Repo Queries (4 tests):**
1. Filter by partition → Verify routing
2. Filter by repo_name → Verify isolation
3. Cross-repo graph (enabled) → Verify edges
4. Cross-repo graph (disabled) → Verify no edges

**Extraction Workflows (3 tests):**
1. Extract attributes → Verify count and accuracy
2. Extract naming → Verify pattern
3. Export YAML/JSON → Verify format

**Total Integration Tests:** ~20

### 4.2 Integration Test Environment

**Test Databases:**
- LanceDB: Temp directory (`/tmp/test_semantic_*.lance`)
- DuckDB: In-memory or temp file

**Test Repositories:**
- Use small, controlled test repos (not full 270 instrumentors)
- Mock repos with known structure (3-5 files each)
- Real repos for E2E tests only

**Cleanup:**
```python
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Cleanup test indexes after each test."""
    yield
    # Cleanup
    shutil.rmtree("/tmp/test_semantic_*", ignore_errors=True)
```

---

## 5. End-to-End Testing Strategy

### 5.1 E2E Test Scenarios

**Critical Path #1: Single Instrumentor Extraction (15 min)**
1. Add instrumentor to config
2. Restart MCP server
3. Wait for indexing
4. Run extraction workflow
5. Export to YAML
6. Verify accuracy (spot check 10 attributes)

**Critical Path #2: Query Across Partitions (5 min)**
1. Index primary + 3 test instrumentors
2. Query primary partition only
3. Query instrumentors partition only
4. Query all partitions
5. Verify results and latency

**Critical Path #3: Partition Lifecycle (10 min)**
1. Create new partition
2. Add 2 repos
3. Query partition
4. Soft delete partition
5. Restore partition
6. Verify data intact

**Total E2E Tests:** 3 (covering critical paths)

### 5.2 E2E Test Environment

**Infrastructure:**
- Full prAxIs OS deployment
- Real Git repositories (small instrumentors)
- Real MCP server
- Real databases (not mocked)

**Data:**
- 3 test instrumentors: FastAPI, LangChain, OpenAI
- Primary partition: praxis-os + python-sdk

**Execution:**
- Manual execution (not automated initially)
- CI/CD integration later (GitHub Actions)

---

## 6. Performance Testing Strategy

### 6.1 Performance Test Methodology

**Baseline Establishment:**
1. Run tests on clean system (no other load)
2. Warm up caches (run 10 queries before measuring)
3. Measure 100 iterations
4. Calculate p95 latency

**Performance Metrics:**
- **Query Latency:** p50, p95, p99, max
- **Indexing Time:** Cold start, incremental update
- **Extraction Time:** Single instrumentor extraction
- **Disk Usage:** Total size, per-partition breakdown

**Tools:**
- Python `time` module for timing
- `statistics` module for percentiles
- `du` command for disk usage
- Custom profiling scripts

### 6.2 Performance Test Execution

```python
# Example: Performance test for query latency

import time
import statistics

def test_query_latency_p95(index):
    """Test query latency meets p95 < 200ms target."""
    latencies = []
    
    # Warm up
    for _ in range(10):
        index.search("test query", filters={"partition": "instrumentors"})
    
    # Measure
    for _ in range(100):
        start = time.time()
        results = index.search("test query", filters={"partition": "instrumentors"})
        latency_ms = (time.time() - start) * 1000
        latencies.append(latency_ms)
    
    # Calculate p95
    p95 = statistics.quantiles(latencies, n=20)[18]
    
    # Assert
    assert p95 < 200, f"p95 latency {p95}ms exceeds target 200ms"
    
    # Log results
    print(f"Latency stats: p50={statistics.median(latencies):.1f}ms, p95={p95:.1f}ms, max={max(latencies):.1f}ms")
```

### 6.3 Performance Benchmarks

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Primary partition p95 latency | < 50ms | 100 queries, p95 calculation |
| Instrumentors partition p95 latency | < 200ms | 100 queries, p95 calculation |
| Extraction workflow | < 15 min | Single instrumentor, full workflow |
| Incremental update (10 files) | < 5 sec | Git diff + parse + index |
| Cold start (270 instrumentors) | < 10 min | Full index build (concurrent) |
| Total disk usage | < 3GB | `du -sh .indexes/code/` |

---

## 7. Test Data Strategy

### 7.1 Test Data Sources

**Unit Tests:**
- Synthetic data (hand-crafted test cases)
- Small, controlled datasets (3-5 items)
- Edge cases (empty, null, malformed)

**Integration Tests:**
- Mock repositories (git repos with known structure)
- Test instrumentors (small, well-behaved repos)
- Sample queries (representative of real usage)

**E2E Tests:**
- Real instrumentors (FastAPI, LangChain, OpenAI)
- Real queries (from HoneyHive use cases)
- Production-like volume (3 instrumentors = ~50K chunks)

### 7.2 Test Data Management

**Storage:**
- Mock repos: `tests/fixtures/repos/`
- Test configs: `tests/fixtures/configs/`
- Expected outputs: `tests/fixtures/expected/`

**Version Control:**
- All test data in Git
- Mock repos as submodules (if large)
- Test configs as YAML files

**Cleanup:**
- Temp data cleaned after each test
- No persistent state between tests

---

## 8. Test Execution

### 8.1 Local Development

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_tracker.py

# Run with coverage
pytest --cov=ouroboros/subsystems/rag/code --cov-report=html

# Run performance tests
pytest tests/performance/ --benchmark
```

### 8.2 Continuous Integration (CI)

**GitHub Actions Workflow:**

```yaml
name: Test Multi-Repo Code Intelligence

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run unit tests
        run: pytest tests/unit/ --cov --cov-report=xml
      - name: Run integration tests
        run: pytest tests/integration/
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**CI Triggers:**
- Every commit to feature branches
- Every pull request
- Nightly builds (for E2E and performance tests)

---

## 9. Test Coverage

### 9.1 Coverage Targets

**Code Coverage:**
- **Overall:** >= 85%
- **Critical paths:** >= 95% (partition management, incremental indexing)
- **New code:** 100% (all new functions must have tests)

**Requirement Coverage:**
- **Functional:** 100% (all 10 FR have test cases)
- **Non-Functional:** 100% (all 29 NFR have test cases)

### 9.2 Coverage Measurement

```bash
# Generate coverage report
pytest --cov=ouroboros/subsystems/rag/code --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# Check coverage threshold
pytest --cov --cov-fail-under=85
```

### 9.3 Coverage Gaps

**Acceptable Gaps:**
- Logging statements (not critical to test)
- Error handling for impossible states (defensive programming)
- Performance optimizations (tested via benchmarks, not unit tests)

**Unacceptable Gaps:**
- Business logic untested
- Critical paths without tests
- New features without tests

---

## 10. Test Maintenance

### 10.1 Test Review Process

**Code Review Checklist:**
- [ ] All new code has corresponding tests
- [ ] Tests follow naming convention: `test_<function>_<scenario>`
- [ ] Tests are independent (no shared state)
- [ ] Tests are deterministic (no flakiness)
- [ ] Tests are fast (unit tests < 1s, integration < 10s)

**Test Quality Metrics:**
- Test pass rate >= 99% (allow 1% flakiness)
- Test execution time < 5 minutes (unit + integration)
- Code coverage >= 85%

### 10.2 Test Refactoring

**When to Refactor:**
- Tests become slow (> 10s for unit tests)
- Tests become flaky (intermittent failures)
- Tests duplicate logic (extract to fixtures)
- Tests are hard to understand (add comments, simplify)

**Refactoring Techniques:**
- Extract common setup to fixtures
- Use parameterized tests for similar scenarios
- Mock expensive operations
- Use test helpers for complex assertions

---

## 11. Acceptance Criteria

### 11.1 Definition of Done

A feature is "done" when:
- [ ] All functional requirements met (see functional-tests.md)
- [ ] All non-functional requirements met (see nonfunctional-tests.md)
- [ ] All unit tests pass (>= 85% coverage)
- [ ] All integration tests pass
- [ ] E2E test passes for critical path
- [ ] Performance benchmarks met
- [ ] Code reviewed and approved
- [ ] Documentation updated (implementation.md, README.md)

### 11.2 Release Criteria

The system is "ready for release" when:
- [ ] All 56 test cases pass (27 functional + 29 non-functional)
- [ ] Code coverage >= 85%
- [ ] No P0 bugs open
- [ ] Performance targets met (p95 latency, extraction time)
- [ ] Security validated (no credential leaks, path traversal prevention)
- [ ] Backward compatibility verified (single-repo usage still works)
- [ ] Deployment tested (rollout + rollback)
- [ ] User documentation complete

---

## 12. Risk Mitigation

### 12.1 Testing Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Flaky tests | High (false negatives) | Use mocks for non-deterministic behavior, seed random generators |
| Slow tests | Medium (developer experience) | Optimize unit tests, run E2E tests in CI only |
| Incomplete coverage | High (bugs in production) | Enforce 85% coverage threshold, review coverage reports |
| Test data drift | Medium (false positives) | Version control test data, validate against real data periodically |
| Performance regression | High (user impact) | Run performance tests in CI, alert on regressions |

### 12.2 Mitigation Actions

**Flaky Tests:**
- Use `pytest-timeout` to catch hanging tests
- Use `pytest-retry` for transient failures (network, race conditions)
- Investigate and fix flaky tests immediately (don't ignore)

**Slow Tests:**
- Profile tests with `pytest-benchmark`
- Optimize or move slow tests to nightly builds
- Use parallel test execution (`pytest-xdist`)

**Coverage Gaps:**
- Review coverage reports weekly
- Add tests for uncovered code before merging
- Use mutation testing to validate test quality

---

## 13. Test Metrics and Reporting

### 13.1 Key Metrics

**Test Health:**
- Pass rate: >= 99%
- Execution time: < 5 minutes (unit + integration)
- Flakiness rate: < 1%

**Code Quality:**
- Code coverage: >= 85%
- Requirement coverage: 100%
- Critical path coverage: >= 95%

**Performance:**
- Primary p95 latency: < 50ms
- Instrumentors p95 latency: < 200ms
- Extraction time: < 15 minutes

### 13.2 Reporting

**Weekly Test Report:**
- Total tests: Pass/Fail/Skip
- Coverage: Overall, per-module
- Performance: Latency trends, regressions
- Bugs: Open P0/P1/P2 counts

**Dashboard:**
- CodeCov integration (coverage visualization)
- GitHub Actions status badges
- Performance trend charts (Grafana)

---

## 14. Summary

**Test Strategy Overview:**
- **56 test cases** covering **39 requirements**
- **Test pyramid:** 70% unit, 20% integration, 10% E2E
- **Coverage target:** >= 85% code, 100% requirements
- **Performance validation:** All targets measured and enforced
- **CI/CD integration:** Automated tests on every commit

**Key Success Factors:**
1. **Fast feedback:** Unit tests run in < 30 seconds
2. **Comprehensive coverage:** All requirements have test cases
3. **Performance validation:** Latency and extraction time measured
4. **Continuous monitoring:** CI/CD catches regressions early
5. **Maintainable tests:** Clear structure, mocked dependencies, fixtures

**Next Steps:**
1. Implement unit tests (Phase 0-6 tasks)
2. Implement integration tests (Phase 0-6 validation gates)
3. Run E2E tests (post-deployment)
4. Setup CI/CD (GitHub Actions)
5. Monitor test metrics (weekly review)

---

