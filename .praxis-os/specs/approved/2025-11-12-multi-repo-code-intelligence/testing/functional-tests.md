# Functional Test Cases

**Project:** Multi-Repo Code Intelligence for Instrumentor Analysis  
**Date:** 2025-11-12  
**Purpose:** Detailed test cases for all 10 functional requirements

---

## FR-001: Multi-Repository Indexing

### FT-001: Index Single External Repository

**Requirement:** FR-001  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Add external repository to mcp.yaml instrumentors partition:
   ```yaml
   - name: "test-instrumentor"
     url: "https://github.com/open-telemetry/opentelemetry-python-contrib"
     sparse_paths: ["instrumentation/opentelemetry-instrumentation-fastapi"]
     provider: "opentelemetry"
   ```
2. Restart MCP server
3. Wait for indexing to complete (check logs)
4. Query semantic index: `pos_search_project(action="search_code", query="FastAPI instrumentation", filters={"repo_name": "test-instrumentor"})`

**Expected Results:**
- [ ] Repository clones successfully
- [ ] Files parsed without critical errors
- [ ] Chunks inserted into semantic index with `repo_name="test-instrumentor"`
- [ ] Query returns results from test-instrumentor only

**Pass Criteria:**
- Query returns >= 1 result
- All results have `repo_name == "test-instrumentor"`
- Parse error rate < 5%

---

### FT-002: Index Multiple Repositories in Same Partition

**Requirement:** FR-001  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Add 3 repositories to instrumentors partition
2. Restart MCP server
3. Query each repository individually using `repo_name` filter
4. Query entire partition without filter

**Expected Results:**
- [ ] All 3 repositories indexed successfully
- [ ] Individual queries return results only from specified repo
- [ ] Partition-wide query returns results from all 3 repos

**Pass Criteria:**
- Each individual query returns >= 1 result from correct repo
- Partition-wide query returns results from all 3 repos
- No cross-contamination (repo A results don't appear in repo B query)

---

## FR-002: Partition Management

### FT-003: Discover Partitions from Config

**Requirement:** FR-002  
**Priority:** P0  
**Type:** Unit Test

**Test Steps:**
1. Create mcp.yaml with 2 partitions: primary, instrumentors
2. Load CodeIndex from config
3. Check `index.partitions` dictionary

**Expected Results:**
- [ ] `index.partitions` contains 2 keys: "primary", "instrumentors"
- [ ] Each partition is a CodePartition instance
- [ ] Partition names match config keys exactly

**Pass Criteria:**
```python
assert "primary" in index.partitions
assert "instrumentors" in index.partitions
assert isinstance(index.partitions["primary"], CodePartition)
```

---

### FT-004: Partition Isolation (Queries)

**Requirement:** FR-002  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Index data in both primary and instrumentors partitions
2. Query primary partition with filter: `filters={"partition": "primary"}`
3. Query instrumentors partition with filter: `filters={"partition": "instrumentors"}`
4. Verify no cross-partition contamination

**Expected Results:**
- [ ] Primary query returns only primary results
- [ ] Instrumentors query returns only instrumentors results
- [ ] Results include `partition` metadata field

**Pass Criteria:**
- All primary results have `partition == "primary"`
- All instrumentors results have `partition == "instrumentors"`
- No overlap

---

### FT-005: Partition-Level Health Checks

**Requirement:** FR-002  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Call `index.health_check()`
2. Verify 4-level fractal structure:
   - Level 1: CodeIndex
   - Level 2: CodePartition (for each partition)
   - Level 3: SemanticIndex, ASTIndex, GraphIndex (for each partition)
   - Level 4: Sub-components (e.g., LanceDB connection, DuckDB connection)

**Expected Results:**
- [ ] Health check returns HealthStatus object
- [ ] `components` field contains partition health
- [ ] Each partition health contains sub-index health

**Pass Criteria:**
```python
health = index.health_check()
assert health.healthy == True
assert "primary" in health.components
assert "semantic" in health.components["primary"].components
```

---

## FR-003: Repository State Tracking

### FT-006: Track Repository State After Sync

**Requirement:** FR-003  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Sync repository for first time
2. Query `repository_state` table:
   ```sql
   SELECT * FROM repository_state WHERE repo_name = 'test-repo';
   ```

**Expected Results:**
- [ ] Row exists with `repo_name = 'test-repo'`
- [ ] `commit_hash` matches current HEAD
- [ ] `last_indexed_at` is recent timestamp
- [ ] `file_count` > 0
- [ ] `status = 'indexed'`

**Pass Criteria:**
- All fields populated correctly
- Timestamp within last 5 minutes

---

### FT-007: Update State After Re-Sync

**Requirement:** FR-003  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Initial sync (see FT-006)
2. Make changes to repository (add file, modify file)
3. Re-sync repository
4. Query `repository_state` table again

**Expected Results:**
- [ ] `commit_hash` updated to new HEAD
- [ ] `last_indexed_at` updated to recent timestamp
- [ ] `file_count` reflects changes
- [ ] `status` remains 'indexed' (or 'sync_failed' if issues)

**Pass Criteria:**
- Commit hash changes
- Timestamp updates
- State reflects current repository state

---

## FR-004: Incremental Indexing

### FT-008: Detect Changed Files via Git Diff

**Requirement:** FR-004  
**Priority:** P0  
**Type:** Unit Test

**Test Steps:**
1. Create mock Git repository with known files
2. Record initial commit hash
3. Modify 5 files, add 2 files, delete 1 file
4. Call `tracker.get_changed_files(repo_config)`

**Expected Results:**
- [ ] Returns list of 8 changed files (5 modified + 2 added + 1 deleted)
- [ ] File paths are relative to repo root
- [ ] Deleted file included in list

**Pass Criteria:**
```python
changed = tracker.get_changed_files(repo_config)
assert len(changed) == 8
assert "modified_file_1.py" in changed
assert "new_file.py" in changed
```

---

### FT-009: Incremental Update Performance

**Requirement:** FR-004  
**Priority:** P0  
**Type:** Performance Test

**Test Steps:**
1. Create repository with 1000 files
2. Index all files (cold start)
3. Modify 10 files
4. Measure time to incremental update

**Expected Results:**
- [ ] Cold start takes 150-200 seconds (1000 files × 200ms)
- [ ] Incremental update takes < 5 seconds (10 files × 200ms)
- [ ] Only 10 files reprocessed (not all 1000)

**Pass Criteria:**
- Incremental update < 5 seconds
- Speedup >= 30x vs. cold start

---

## FR-005: Cross-Repository Query Filtering

### FT-010: Filter by Partition

**Requirement:** FR-005  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Query with `filters={"partition": "instrumentors"}`
2. Verify all results from instrumentors partition

**Expected Results:**
- [ ] All results have `partition == "instrumentors"`
- [ ] Query faster than unfiltered query (fewer chunks searched)

**Pass Criteria:**
- 100% of results from correct partition
- Query latency < 200ms p95

---

### FT-011: Filter by Repository Name

**Requirement:** FR-005  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Query with `filters={"repo_name": "fastapi-instrumentation"}`
2. Verify all results from specified repository

**Expected Results:**
- [ ] All results have `repo_name == "fastapi-instrumentation"`

**Pass Criteria:**
- 100% of results from correct repository

---

### FT-012: Filter by Provider

**Requirement:** FR-005  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Query with `filters={"provider": "opentelemetry"}`
2. Verify all results from OpenTelemetry instrumentors

**Expected Results:**
- [ ] All results have `provider == "opentelemetry"`
- [ ] Results from multiple OpenTelemetry repos (if multiple indexed)

**Pass Criteria:**
- 100% of results from correct provider

---

## FR-006: Cross-Repo Call Graph Traversal

### FT-013: Cross-Repo Graph Enabled

**Requirement:** FR-006  
**Priority:** P1  
**Type:** Integration Test

**Test Steps:**
1. Create partition with `graph_cross_repo: true`
2. Index 2 repositories with cross-repo function calls
3. Query `find_callers` for function in repo A that's called from repo B

**Expected Results:**
- [ ] Query returns caller from repo B
- [ ] Relationship table includes edge where `caller_repo != callee_repo`

**Pass Criteria:**
- Cross-repo edge detected
- Graph traversal crosses repository boundaries

---

### FT-014: Cross-Repo Graph Disabled

**Requirement:** FR-006  
**Priority:** P1  
**Type:** Integration Test

**Test Steps:**
1. Create partition with `graph_cross_repo: false`
2. Index same 2 repositories
3. Query `find_callers` for same function

**Expected Results:**
- [ ] Query does NOT return caller from repo B
- [ ] Only same-repo edges returned

**Pass Criteria:**
- No cross-repo edges in results
- All results have `caller_repo == callee_repo`

---

## FR-007: Git Repository Synchronization

### FT-015: Clone Repository

**Requirement:** FR-007  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Call `syncer.sync_repository(repo_config)` for new repository
2. Verify repository cloned to expected path

**Expected Results:**
- [ ] Repository directory exists
- [ ] `.git` directory exists
- [ ] Files checked out

**Pass Criteria:**
```python
assert (target_path / ".git").exists()
assert len(list(target_path.glob("*.py"))) > 0
```

---

### FT-016: Pull Repository Updates

**Requirement:** FR-007  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Clone repository (see FT-015)
2. Make upstream changes (simulate by modifying remote)
3. Call `syncer.sync_repository(repo_config)` again
4. Verify files updated

**Expected Results:**
- [ ] `git pull` executes successfully
- [ ] HEAD commit updated
- [ ] Changed files reflect upstream modifications

**Pass Criteria:**
- Commit hash changes
- Changed files updated locally

---

### FT-017: Sparse Checkout

**Requirement:** FR-007  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Configure repository with `sparse_paths: ["instrumentation/fastapi"]`
2. Call `syncer.sparse_clone()`
3. Verify only specified paths checked out

**Expected Results:**
- [ ] `instrumentation/fastapi/` directory exists
- [ ] Other directories (e.g., `instrumentation/django/`) do NOT exist

**Pass Criteria:**
```python
assert (target_path / "instrumentation" / "fastapi").exists()
assert not (target_path / "instrumentation" / "django").exists()
```

---

## FR-008: Semantic Convention Extraction

### FT-018: Extract Span Attributes

**Requirement:** FR-008  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Index instrumentor repository (e.g., fastapi-instrumentation)
2. Call `extract_span_attributes(repo_name="fastapi-instrumentation")`
3. Verify extracted attributes

**Expected Results:**
- [ ] Report contains list of AttributeSpec objects
- [ ] Attributes include: `http.method`, `http.url`, `http.status_code`, etc.
- [ ] Each attribute has: key, value_type, value_source, file_path, line_number

**Pass Criteria:**
- >= 10 attributes extracted
- Attributes match manual inspection of source code (spot check 3 attributes)

---

### FT-019: Extract Span Naming Patterns

**Requirement:** FR-008  
**Priority:** P0  
**Type:** Integration Test

**Test Steps:**
1. Call `extract_span_naming(repo_name="langchain-instrumentation")`
2. Verify naming pattern extracted

**Expected Results:**
- [ ] Report contains naming pattern (e.g., "langchain.{class}.{method}")
- [ ] Report contains example span names
- [ ] Report contains source locations

**Pass Criteria:**
- Pattern extracted matches manual inspection
- >= 3 example names provided

---

## FR-009: Machine-Readable Output

### FT-020: Export to YAML/JSON

**Requirement:** FR-009  
**Priority:** P0  
**Type:** Unit Test

**Test Steps:**
1. Create mock ConventionReport with attributes and naming
2. Call `export_conventions(report, format="yaml")`
3. Parse YAML output
4. Repeat for JSON format

**Expected Results:**
- [ ] YAML output is valid (parseable by PyYAML)
- [ ] JSON output is valid (parseable by json module)
- [ ] Output includes: instrumentor name, attributes, naming patterns

**Pass Criteria:**
```python
yaml_output = export_conventions(report, format="yaml")
parsed = yaml.safe_load(yaml_output)
assert "attributes" in parsed
assert len(parsed["attributes"]) > 0
```

---

## FR-010: Partition Lifecycle Management

### FT-021: Create Partition

**Requirement:** FR-010  
**Priority:** P1  
**Type:** Integration Test

**Test Steps:**
1. Add new partition to mcp.yaml
2. Call `manager.create_partition(partition_name, partition_config)`
3. Verify directories created, tables initialized

**Expected Results:**
- [ ] Partition directory exists: `.indexes/code/{partition_name}/`
- [ ] Sub-directories exist: `semantic.lance/`, `ast.duckdb`, `graph.duckdb`
- [ ] Health check shows new partition

**Pass Criteria:**
```python
assert (base_path / partition_name).exists()
assert partition_name in index.partitions
```

---

### FT-022: Update Partition (Add Repository)

**Requirement:** FR-010  
**Priority:** P1  
**Type:** Integration Test

**Test Steps:**
1. Add repository to existing partition config
2. Call `partition.add_repository(repo_config)`
3. Verify repository indexed incrementally

**Expected Results:**
- [ ] Repository cloned/synced
- [ ] Files indexed into partition
- [ ] Query returns results from new repository

**Pass Criteria:**
- Query with `repo_name` filter returns results
- Incremental indexing completes in < 5 minutes

---

### FT-023: Update Partition (Remove Repository)

**Requirement:** FR-010  
**Priority:** P1  
**Type:** Integration Test

**Test Steps:**
1. Remove repository from partition config
2. Call `partition.remove_repository(repo_name)`
3. Verify data deleted from all 3 indexes

**Expected Results:**
- [ ] Query with `repo_name` filter returns 0 results
- [ ] Semantic index: no chunks with `repo_name`
- [ ] AST index: no nodes with `repo_name`
- [ ] Graph index: no symbols with `repo_name`

**Pass Criteria:**
```sql
SELECT COUNT(*) FROM chunks WHERE repo_name = 'removed-repo';
-- Should return 0
```

---

### FT-024: Delete Partition (Soft Delete)

**Requirement:** FR-010  
**Priority:** P1  
**Type:** Integration Test

**Test Steps:**
1. Call `manager.delete_partition(partition_name, hard_delete=False)`
2. Verify data archived to `.archive/{partition_name}_{timestamp}/`
3. Call `manager.restore_partition(partition_name, timestamp)`
4. Verify partition restored and queryable

**Expected Results:**
- [ ] Archive directory exists with partition data
- [ ] Partition removed from active partitions
- [ ] After restore, partition queryable again
- [ ] Data intact after restore

**Pass Criteria:**
- Archive completes in < 2 minutes
- Restore completes in < 2 minutes
- No data loss (chunk counts match before/after)

---

## Test Summary

**Total Functional Test Cases:** 27  
**Coverage:** All 10 functional requirements covered  
**Test Types:**
- Unit Tests: 3
- Integration Tests: 23
- Performance Tests: 1

**Priority Breakdown:**
- P0 (Critical): 22 tests
- P1 (High): 5 tests

---

