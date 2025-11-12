# Non-Functional Test Cases

**Project:** Multi-Repo Code Intelligence for Instrumentor Analysis  
**Date:** 2025-11-12  
**Purpose:** Detailed test cases for all 29 non-functional requirements

---

## Performance Tests (NFR-P)

### NFT-001: Primary Partition Query Latency < 50ms

**Requirement:** NFR-P1  
**Priority:** P0  
**Type:** Performance Test

**Test Setup:**
- Primary partition with 113K chunks
- 100 test queries (mix of semantic, AST, graph)
- Measure latency for each query

**Test Steps:**
1. Run 100 queries with `filters={"partition": "primary"}`
2. Measure query time for each
3. Calculate p95 latency

**Pass Criteria:**
- p95 latency < 50ms
- No query > 100ms (p100 sanity check)

**Measurement Script:**
```python
import time
import statistics

latencies = []
for query in test_queries:
    start = time.time()
    results = index.search(query, filters={"partition": "primary"})
    latency_ms = (time.time() - start) * 1000
    latencies.append(latency_ms)

p95 = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
assert p95 < 50, f"p95 latency {p95}ms exceeds target 50ms"
```

---

### NFT-002: Instrumentors Partition Query Latency < 200ms

**Requirement:** NFR-P2  
**Priority:** P0  
**Type:** Performance Test

**Test Setup:**
- Instrumentors partition with 324K chunks
- 100 test queries

**Pass Criteria:**
- p95 latency < 200ms

---

### NFT-003: Extraction Workflow < 15 Minutes

**Requirement:** NFR-P3  
**Priority:** P0  
**Type:** Performance Test

**Test Setup:**
- Single instrumentor (e.g., fastapi-instrumentation)
- Run full extraction workflow: attributes + naming + export

**Test Steps:**
1. Start timer
2. Call `extract_span_attributes(repo_name)`
3. Call `extract_span_naming(repo_name)`
4. Call `export_conventions(report, format="yaml")`
5. Stop timer

**Pass Criteria:**
- Total time < 15 minutes (900 seconds)

**Actual Target:** 3 hours manual analysis → 15 minutes automated = **12x speedup**

---

### NFT-004: Incremental Index Update < 5 Seconds

**Requirement:** NFR-P4  
**Priority:** P0  
**Type:** Performance Test

**Test Setup:**
- Repository with 10 changed files
- Measure incremental update time

**Pass Criteria:**
- Total time < 5 seconds
- All 3 indexes updated (semantic, AST, graph)

**Expected:** 10 files × 200ms = 2 seconds (well under 5s target)

---

### NFT-005: Cold Start < 10 Minutes

**Requirement:** NFR-P5  
**Priority:** P1  
**Type:** Performance Test

**Test Setup:**
- Empty instrumentors partition
- Add 270 instrumentor repositories
- Measure full initial indexing time

**Pass Criteria:**
- Total time < 10 minutes (600 seconds)

**Note:** Requires concurrent indexing (4 cores) to meet target. Sequential would take ~45 minutes.

---

## Storage Tests (NFR-ST)

### NFT-006: Total Disk Usage < 3GB

**Requirement:** NFR-ST1  
**Priority:** P0  
**Type:** Integration Test

**Test Setup:**
- Full deployment: primary + instrumentors partitions
- 270 instrumentors indexed

**Test Steps:**
1. Measure disk usage: `du -sh .indexes/code/`
2. Break down by partition:
   - Primary: `du -sh .indexes/code/primary/`
   - Instrumentors: `du -sh .indexes/code/instrumentors/`

**Pass Criteria:**
- Total < 3GB
- Primary < 500MB
- Instrumentors < 2GB
- Margins < 500MB (for growth)

**Measurement Script:**
```bash
total=$(du -sb .indexes/code/ | cut -f1)
gb=$((total / 1024 / 1024 / 1024))
assert [ $gb -lt 3 ]
```

---

### NFT-007: Incremental Storage (No Duplication)

**Requirement:** NFR-ST2  
**Priority:** P1  
**Type:** Unit Test

**Test Steps:**
1. Initial index: Record disk usage
2. Modify 10 files
3. Incremental update
4. Record new disk usage
5. Calculate delta

**Pass Criteria:**
- Delta < 10MB (only changed files stored, not entire repo duplicated)

---

## Maintainability Tests (NFR-M)

### NFT-008: Extraction Template Reusability

**Requirement:** NFR-M1  
**Priority:** P1  
**Type:** Integration Test

**Test Steps:**
1. Create single extraction template for `span.set_attribute`
2. Run template on 3 different instrumentors (FastAPI, LangChain, OpenAI)
3. Verify template works without modification

**Pass Criteria:**
- Same template code works for all 3 instrumentors
- No instrumentor-specific conditionals required

---

### NFT-009: Version-Controlled Outputs

**Requirement:** NFR-M2  
**Priority:** P1  
**Type:** Manual Test

**Test Steps:**
1. Run extraction workflow
2. Export to YAML
3. Commit to Git: `git add extracted_conventions/*.yaml`
4. Verify files committed successfully

**Pass Criteria:**
- YAML files committed to Git
- `git log` shows extraction outputs

---

## Reliability Tests (NFR-R)

### NFT-010: Parse Error Handling

**Requirement:** NFR-R1  
**Priority:** P0  
**Type:** Unit Test

**Test Steps:**
1. Create repository with 10 valid files + 1 invalid file (syntax error)
2. Run incremental indexing
3. Verify:
   - 10 valid files indexed successfully
   - 1 invalid file logged as warning
   - Indexing continues (doesn't crash)

**Pass Criteria:**
```python
stats = indexer.update_repository(repo_config)
assert stats.files_updated == 10
assert stats.parse_errors == 1
# Index should still be queryable
results = index.search("test query")
assert len(results) > 0
```

---

### NFT-011: Per-Repo Health Checks

**Requirement:** NFR-R2  
**Priority:** P1  
**Type:** Integration Test

**Test Steps:**
1. Index 3 repositories, intentionally break 1 (corrupt file)
2. Call health check
3. Verify health status shows:
   - Repository 1: Healthy
   - Repository 2: Unhealthy (with error details)
   - Repository 3: Healthy

**Pass Criteria:**
- Health check reports per-repository status
- Unhealthy repo doesn't block other repos

---

### NFT-012: Rollback Capability < 2 Minutes

**Requirement:** NFR-R3  
**Priority:** P0  
**Type:** Performance Test

**Test Steps:**
1. Start timer
2. Soft delete partition: `manager.delete_partition("instrumentors", hard_delete=False)`
3. Restore partition: `manager.restore_partition("instrumentors", timestamp)`
4. Stop timer

**Pass Criteria:**
- Total time (delete + restore) < 2 minutes (120 seconds)
- Data intact after restore (chunk counts match)

---

### NFT-013: Sync Failure Isolation

**Requirement:** NFR-R4  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Add 3 repositories to partition
2. Intentionally break repo 2 (invalid URL)
3. Run sync for all 3 repos
4. Verify repos 1 and 3 sync successfully despite repo 2 failure

**Pass Criteria:**
```python
# Repo 2 fails
state_2 = tracker.get_state("repo-2")
assert state_2.status == "sync_failed"

# Repos 1 and 3 succeed
state_1 = tracker.get_state("repo-1")
state_3 = tracker.get_state("repo-3")
assert state_1.status == "indexed"
assert state_3.status == "indexed"
```

---

## Scalability Tests (NFR-S)

### NFT-014: Scale to 270 Instrumentors

**Requirement:** NFR-S1  
**Priority:** P0  
**Type:** Integration Test

**Test Setup:**
- Add 270 instrumentor repositories to config (across 4 providers)
- Run full index build

**Pass Criteria:**
- All 270 repositories indexed successfully
- Sync success rate > 95% (264+ repos)
- Query latency targets still met

---

### NFT-015: Single-Table Architecture

**Requirement:** NFR-S2  
**Priority:** P1  
**Type:** Unit Test

**Test Steps:**
1. Index 2 partitions
2. Query database schema
3. Verify single tables with partition columns

**Pass Criteria:**
```sql
-- Semantic index: Single LanceDB table
SELECT DISTINCT partition FROM chunks;
-- Should return: primary, instrumentors

-- AST index: Single DuckDB table
SELECT DISTINCT partition FROM ast_nodes;

-- Graph index: Single DuckDB tables
SELECT DISTINCT partition FROM symbols;
```

---

### NFT-016: Total Chunk Scale (437K)

**Requirement:** NFR-S3  
**Priority:** P0  
**Type:** Scale Test

**Test Setup:**
- Primary partition: 113K chunks
- Instrumentors partition: 324K chunks
- Total: 437K chunks

**Test Steps:**
1. Index full dataset
2. Count chunks: `SELECT COUNT(*) FROM chunks`
3. Run queries to verify performance maintained

**Pass Criteria:**
- Total chunk count ~437K (±10%)
- Query latency targets still met (p95 < 200ms for instrumentors)

---

### NFT-017: Parse Error Rate < 5%

**Requirement:** NFR-S4  
**Priority:** P1  
**Type:** Integration Test

**Test Setup:**
- Index 270 instrumentors
- Track parse errors across all repos

**Test Steps:**
1. Sum `parse_errors` from all rebuild stats
2. Calculate error rate: `parse_errors / total_files`

**Pass Criteria:**
- Error rate < 5%

**Expected:** Most instrumentors are well-maintained, error rate should be 1-2%

---

## Operability Tests (NFR-O)

### NFT-018: Soft Delete with Archival

**Requirement:** NFR-O1  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Delete partition: `manager.delete_partition("test-partition", hard_delete=False)`
2. Verify archive created: `ls .archive/test-partition_*/`
3. Verify archive contains:
   - `semantic.lance/`
   - `ast.duckdb`
   - `graph.duckdb`

**Pass Criteria:**
```python
archive_path = Path(".archive").glob("test-partition_*")
assert len(list(archive_path)) == 1
assert (archive_path / "semantic.lance").exists()
```

---

### NFT-019: Orphaned Data Detection

**Requirement:** NFR-O2  
**Priority:** P1  
**Type:** Unit Test

**Test Steps:**
1. Create orphaned partition directory (not in config):
   ```bash
   mkdir .indexes/code/orphaned_test/
   ```
2. Start CodeIndex
3. Check logs for orphaned data warning

**Pass Criteria:**
```python
orphaned = manager.detect_orphaned_data()
assert "orphaned_test" in orphaned
# Should log warning, not auto-delete
assert Path(".indexes/code/orphaned_test").exists()
```

---

### NFT-020: Partition Migration

**Requirement:** NFR-O3  
**Priority:** P2  
**Type:** Integration Test

**Test Steps:**
1. Move repository from `primary` to `instrumentors` partition
2. Measure time for metadata update
3. Verify repository queryable in new partition

**Pass Criteria:**
- Fast path (metadata update): < 5 seconds
- Slow path (re-index): < 5 minutes

---

### NFT-021: Config Validation

**Requirement:** NFR-O4  
**Priority:** P0  
**Type:** Unit Test

**Test Steps:**
Test all validation rules:

1. **Valid paths:**
   ```yaml
   path: "/nonexistent/path"  # Should fail
   ```

2. **No duplicate repos:**
   ```yaml
   repositories:
     - name: "duplicate"
     - name: "duplicate"  # Should fail
   ```

3. **Valid partition names:**
   ```yaml
   partitions:
     "invalid-name!":  # Should fail (special chars)
   ```

4. **No embedded credentials:**
   ```yaml
   url: "https://user:pass@github.com/repo"  # Should fail
   ```

**Pass Criteria:**
- Each invalid config raises `ValueError` with actionable message

---

## Security Tests (NFR-SEC)

### NFT-022: No Embedded Credentials

**Requirement:** NFR-SEC1  
**Priority:** P0  
**Type:** Unit Test

**Test Steps:**
1. Create config with embedded credential URL
2. Load config with Pydantic

**Expected:**
```python
try:
    config = RepositoryConfig(url="https://user:pass@github.com/repo")
    assert False, "Should have raised ValueError"
except ValueError as e:
    assert "embedded credentials" in str(e).lower()
```

**Pass Criteria:**
- Validation rejects URL with credentials
- Error message mentions SSH keys or environment variables

---

### NFT-023: Path Traversal Prevention

**Requirement:** NFR-SEC2  
**Priority:** P0  
**Type:** Unit Test

**Test Steps:**
1. Attempt to use path with `..` to escape workspace:
   ```python
   config = RepositoryConfig(path="../../etc/passwd")
   ```

**Expected:**
```python
try:
    validated_path = validate_repository_path(config.path, workspace_root)
    assert False, "Should have raised ValueError"
except ValueError as e:
    assert "outside allowed directories" in str(e).lower()
```

**Pass Criteria:**
- Path validation rejects traversal attempts

---

### NFT-024: Error Message Safety

**Requirement:** NFR-SEC3  
**Priority:** P1  
**Type:** Unit Test

**Test Steps:**
1. Trigger error with sensitive path: `/Users/josh/secrets/api_key.txt`
2. Capture error message
3. Verify sensitive paths sanitized

**Expected:**
```python
error_msg = safe_error_message(exception, repo_name)
assert "/Users/josh" not in error_msg
assert "<workspace>" in error_msg
```

**Pass Criteria:**
- Absolute paths replaced with `<workspace>/`
- URLs with credentials replaced with `<credentials>`

---

## Integration Tests (NFR-I)

### NFT-025: Cascading Health Check Integration

**Requirement:** NFR-I1  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Call global health check endpoint
2. Verify 4-level fractal structure:
   - CodeIndex → Partitions → Indexes → Sub-components

**Pass Criteria:**
```python
health = global_health_check()
assert health.components["code_index"].healthy
assert "primary" in health.components["code_index"].components
```

---

### NFT-026: AST-Aware Chunking Integration

**Requirement:** NFR-I2  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Index file with AST-aware chunking
2. Verify chunk metadata includes:
   - `chunk_type` (function/class/method)
   - `partition`
   - `repo_name`
   - `provider`

**Pass Criteria:**
```python
chunks = index.partitions["primary"].semantic.get_chunks_by_file(file_path)
assert chunks[0]["chunk_type"] in ["function", "class", "method"]
assert chunks[0]["partition"] == "primary"
```

---

### NFT-027: Backward Compatibility

**Requirement:** NFR-I3  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Create config with ONLY primary partition (single-repo setup)
2. Verify all existing functionality works:
   - Queries
   - Incremental updates
   - Health checks

**Pass Criteria:**
- All legacy tests pass
- No breaking changes to single-repo usage

---

## Performance Benchmark Tests (NFR-PB)

### NFT-028: Sync Success Rate > 95%

**Requirement:** NFR-PB1  
**Priority:** P1  
**Type:** Integration Test

**Test Setup:**
- Index 270 instrumentors
- Track sync results

**Test Steps:**
1. Count total repos: 270
2. Count failed repos: `SELECT COUNT(*) FROM repository_state WHERE status = 'sync_failed'`
3. Calculate success rate: `(270 - failed) / 270`

**Pass Criteria:**
- Success rate > 95% (<=13 failures allowed)

---

### NFT-029: Parse-Once-Index-Thrice >= 2x Faster

**Requirement:** NFR-PB2  
**Priority:** P1  
**Type:** Performance Test

**Test Steps:**
1. Measure parse-once-index-thrice: Single parse → 3 data extractions
2. Measure naive approach: 3 separate parses
3. Calculate speedup

**Expected:**
- Parse-once: 200ms (150ms parse + 50ms extract)
- Naive: 450ms (150ms parse × 3)
- Speedup: 2.25x

**Pass Criteria:**
- Speedup >= 2x

---

## Test Summary

**Total Non-Functional Test Cases:** 29  
**Coverage:** All 29 NFR covered  
**Test Types:**
- Performance: 9 tests
- Integration: 13 tests
- Unit: 7 tests

**Priority Breakdown:**
- P0 (Critical): 15 tests
- P1 (High): 13 tests
- P2 (Medium): 1 test

---

