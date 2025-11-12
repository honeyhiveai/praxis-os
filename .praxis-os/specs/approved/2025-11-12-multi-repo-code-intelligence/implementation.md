# Implementation Guide

**Project:** Multi-Repo Code Intelligence for Instrumentor Analysis  
**Date:** 2025-11-12  
**Based on:** srd.md (requirements) + specs.md (design) + tasks.md (breakdown)

---

## 1. Code Patterns and Best Practices

This section provides concrete implementation patterns extracted from the design document. **Copy these patterns, don't reinvent.**

### 1.1 Dynamic Partition Discovery

**Pattern:** Zero hardcoded partition names. Discover partitions from config at runtime.

**Implementation:**

```python
# ouroboros/subsystems/rag/code/code_index.py

from pathlib import Path
from typing import Dict
from ouroboros.subsystems.rag.config.schemas.indexes import CodeIndexConfig
from ouroboros.subsystems.rag.code.partition import CodePartition

class CodeIndex(BaseIndex):
    """Container for partitioned code indexes."""
    
    def __init__(self, config: CodeIndexConfig, base_path: Path):
        self.config = config
        self.base_path = base_path
        self.partitions: Dict[str, CodePartition] = {}
        
        # Dynamic discovery from config (NO hardcoded partition names)
        for partition_name, partition_config in config.partitions.items():
            self.partitions[partition_name] = CodePartition(
                name=partition_name,
                config=partition_config,
                base_path=base_path / partition_name
            )
    
    def get_partition(self, name: str) -> CodePartition:
        """Get partition by name."""
        if name not in self.partitions:
            raise ValueError(f"Partition '{name}' not found. Available: {list(self.partitions.keys())}")
        return self.partitions[name]
```

**Why this works:**
- Config drives discovery (add new partition = edit YAML, not code)
- No if/else chains for partition types
- Easy to add new partitions without code changes

**Anti-pattern:**

```python
# ❌ BAD: Hardcoded partition names
def __init__(self):
    self.primary = CodePartition("primary", ...)
    self.instrumentors = CodePartition("instrumentors", ...)
    # What if we need a third partition? Code change required!
```

---

### 1.2 Fractal Health Checks (4-Level Hierarchy)

**Pattern:** Recursive health checks from CodeIndex → Partition → Index Type → Sub-components.

**Implementation:**

```python
# ouroboros/subsystems/rag/code/code_index.py

from ouroboros.subsystems.rag.health import HealthStatus

def health_check(self) -> HealthStatus:
    """
    CodeIndex health check (Level 1).
    Aggregates health from all partitions.
    """
    partition_health = {}
    
    for name, partition in self.partitions.items():
        partition_health[name] = partition.health_check()  # Recursive call to Level 2
    
    return HealthStatus(
        healthy=all(h.healthy for h in partition_health.values()),
        name="CodeIndex",
        components=partition_health,
        metrics={
            "total_partitions": len(self.partitions),
            "healthy_partitions": sum(1 for h in partition_health.values() if h.healthy)
        }
    )
```

```python
# ouroboros/subsystems/rag/code/partition.py

def health_check(self) -> HealthStatus:
    """
    CodePartition health check (Level 2).
    Aggregates health from 3 sub-indexes.
    """
    sub_index_health = {
        "semantic": self.semantic.health_check(),  # Level 3
        "ast": self.ast.health_check(),            # Level 3
        "graph": self.graph.health_check()         # Level 3
    }
    
    return HealthStatus(
        healthy=all(h.healthy for h in sub_index_health.values()),
        name=f"Partition:{self.name}",
        components=sub_index_health,
        metrics={
            "repository_count": len(self.repositories),
            "total_chunks": self.semantic.count()
        }
    )
```

**Output Example:**

```json
{
  "healthy": true,
  "name": "CodeIndex",
  "components": {
    "primary": {
      "healthy": true,
      "name": "Partition:primary",
      "components": {
        "semantic": {"healthy": true, "name": "SemanticIndex", "metrics": {"chunks": 113000}},
        "ast": {"healthy": true, "name": "ASTIndex", "metrics": {"nodes": 450000}},
        "graph": {"healthy": true, "name": "GraphIndex", "metrics": {"symbols": 25000}}
      }
    },
    "instrumentors": {...}
  }
}
```

**Why this works:**
- Single health check call reveals entire system state
- Partial degradation visible (one partition unhealthy doesn't hide others)
- Aligns with Cascading Health Check Architecture

---

### 1.3 Parse-Once-Index-Thrice

**Pattern:** Single Tree-sitter parse populates all 3 indexes. **2.25x faster than parsing 3 times.**

**Implementation:**

```python
# ouroboros/subsystems/rag/code/indexer.py

from ouroboros.subsystems.rag.code.ast_index.ast import ASTExtractor
from tree_sitter import Parser, Language

def update_file(self, file_path: Path, repo_config: RepositoryConfig):
    """
    Update single file across all 3 indexes.
    Parse ONCE, index THRICE.
    """
    # 1. Parse file ONCE with Tree-sitter
    with open(file_path, 'r') as f:
        source_code = f.read()
    
    parser = Parser()
    parser.set_language(Language(tree_sitter_python.language(), "python"))
    tree = parser.parse(bytes(source_code, "utf8"))
    
    # 2. Extract data structures from SAME parse tree
    #    (No re-parsing!)
    
    # Extract semantic chunks (via UniversalASTChunker)
    chunks = self.chunker.chunk_file(file_path, source_code, tree)
    
    # Extract AST nodes (from same tree)
    ast_nodes = ASTExtractor.extract_nodes(tree.root_node, file_path)
    
    # Extract graph symbols (from same tree)
    symbols = self._extract_symbols(tree.root_node, file_path)
    relationships = self._extract_relationships(tree.root_node, symbols)
    
    # 3. Delete old data from all 3 indexes (atomic)
    self.partition.semantic.delete_by_file(file_path)
    self.partition.ast.delete_by_file(file_path)
    self.partition.graph.delete_by_file(file_path)
    
    # 4. Insert new data into all 3 indexes (atomic)
    self.partition.semantic.insert_chunks(chunks, repo_config)
    self.partition.ast.insert_nodes(ast_nodes, repo_config)
    self.partition.graph.insert_symbols(symbols, repo_config)
    self.partition.graph.insert_relationships(relationships, repo_config)
```

**Why this works:**
- Tree-sitter parse is the bottleneck (150ms for 500-line file)
- Extracting data from existing tree is fast (50ms total for all 3)
- Total: 200ms vs. 450ms (3 parses)

**Anti-pattern:**

```python
# ❌ BAD: Parsing 3 times
self.partition.semantic.update_file(file_path)  # Parse 1
self.partition.ast.update_file(file_path)       # Parse 2
self.partition.graph.update_file(file_path)     # Parse 3
# Total time: 450ms (3x slower)
```

---

### 1.4 Incremental Indexing Workflow

**Pattern:** Git diff to detect changes, update only changed files.

**Implementation:**

```python
# ouroboros/subsystems/rag/code/indexer.py

from ouroboros.subsystems.rag.code.tracker import RepositoryTracker
from ouroboros.subsystems.rag.code.syncer import RepositorySyncer

def update_repository(self, repo_config: RepositoryConfig) -> RebuildStats:
    """
    Incremental update for single repository.
    Only reprocesses changed files.
    """
    stats = RebuildStats()
    start_time = time.time()
    
    try:
        # 1. Git pull (or clone if first time)
        sync_result = self.syncer.sync_repository(repo_config)
        if not sync_result.success:
            raise Exception(sync_result.error)
        
        # 2. Detect changed files via Git diff
        changed_files = sync_result.changed_files
        if not changed_files:
            logger.info(f"No changes for {repo_config.name}")
            return stats
        
        logger.info(f"Processing {len(changed_files)} changed files for {repo_config.name}")
        
        # 3. Update only changed files (parse-once-index-thrice)
        for file_path in changed_files:
            try:
                self.update_file(file_path, repo_config)
                stats.files_updated += 1
            except Exception as e:
                logger.warning(f"Parse error for {file_path}: {e}")
                stats.parse_errors += 1
                # CONTINUE with other files, don't fail entire repo
        
        # 4. Update tracker state (commit hash, timestamp)
        self.tracker.mark_indexed(
            repo_name=repo_config.name,
            commit_hash=sync_result.new_commit,
            file_count=stats.files_updated
        )
        
    except Exception as e:
        logger.error(f"Sync failed for {repo_config.name}: {e}")
        self.tracker.mark_failed(repo_config.name, str(e))
        raise
    
    finally:
        stats.total_time_ms = (time.time() - start_time) * 1000
    
    return stats
```

**Why this works:**
- Typical change: 5 files → 5 × 200ms = 1 second (fast)
- Full re-index: 1000 files → 1000 × 200ms = 200 seconds (slow, only on first run)
- **200x speedup for typical changes**

---

### 1.5 Partition Routing for Query Performance

**Pattern:** Route queries to specific partition(s) based on filters to minimize chunks searched.

**Implementation:**

```python
# ouroboros/subsystems/rag/code/code_index.py

def search(self, query: str, action: str, filters: Optional[Dict] = None, **kwargs):
    """
    Route search to appropriate partition(s) based on filters.
    """
    if filters and "partition" in filters:
        # Fast path: Route to specific partition
        partition_name = filters["partition"]
        partition = self.get_partition(partition_name)
        
        logger.info(f"Routing query to partition '{partition_name}'")
        return partition.search(query, action, filters=filters, **kwargs)
    
    else:
        # Slow path: Search all partitions, aggregate results
        logger.info(f"Searching all {len(self.partitions)} partitions")
        all_results = []
        
        for partition_name, partition in self.partitions.items():
            try:
                results = partition.search(query, action, filters=filters, **kwargs)
                # Tag results with partition metadata
                for result in results:
                    result["_partition"] = partition_name
                all_results.extend(results)
            except Exception as e:
                logger.warning(f"Search failed for partition '{partition_name}': {e}")
                # CONTINUE with other partitions (partial degradation)
        
        # Sort by relevance score
        all_results.sort(key=lambda r: r.get("relevance_score", 0), reverse=True)
        
        return all_results
```

**Performance Impact:**
- Partition-specific query: Search 113K chunks (primary) vs. 437K (all) = **3.9x faster**
- Primary partition p95: 50ms
- Instrumentors partition p95: 200ms
- All partitions p95: 250ms

---

### 1.6 Configuration Schema (Pydantic)

**Pattern:** Use Pydantic for config validation with descriptive error messages.

**Implementation:**

```python
# ouroboros/subsystems/rag/config/schemas/indexes.py

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional

class RepositoryConfig(BaseModel):
    """Configuration for a single repository."""
    name: str = Field(..., description="Unique repository name (alphanumeric + underscore)")
    path: Optional[str] = Field(None, description="Local path (if repository exists locally)")
    url: Optional[str] = Field(None, description="Remote Git URL (for cloning)")
    provider: str = Field(..., description="Provider: honeyhive, opentelemetry, openlit, traceloop, arize, local")
    sparse_paths: List[str] = Field(default_factory=list, description="Sparse checkout paths (subdirectories only)")
    enabled: bool = Field(default=True, description="Enable/disable indexing for this repository")
    
    @field_validator("name")
    def validate_name(cls, v):
        """Ensure name is alphanumeric + underscore."""
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(f"Repository name '{v}' must be alphanumeric + underscore/hyphen")
        return v
    
    @field_validator("url")
    def validate_no_credentials(cls, v):
        """Reject URLs with embedded credentials."""
        if v and "@" in v.split("://")[1] if "://" in v else False:
            raise ValueError(
                "Embedded credentials in URL detected. "
                "Use SSH keys or environment variables for authentication."
            )
        return v
    
    @field_validator("provider")
    def validate_provider(cls, v):
        """Validate provider is in allowed list."""
        allowed = ["honeyhive", "opentelemetry", "openlit", "traceloop", "arize", "local"]
        if v not in allowed:
            raise ValueError(f"Provider '{v}' not allowed. Must be one of: {allowed}")
        return v
    
    def model_post_init(self, __context):
        """Ensure either path OR url is provided (not both)."""
        if not self.path and not self.url:
            raise ValueError(f"Repository '{self.name}' must have either 'path' or 'url'")
        if self.path and self.url:
            raise ValueError(f"Repository '{self.name}' cannot have both 'path' and 'url'")

class PerformanceTargets(BaseModel):
    """Performance targets for partition indexes."""
    semantic: Dict[str, int] = Field(default={"p95_ms": 150}, description="Semantic index p95 latency (ms)")
    ast: Dict[str, int] = Field(default={"p95_ms": 50}, description="AST index p95 latency (ms)")
    graph: Dict[str, int] = Field(default={"p95_ms": 100}, description="Graph index p95 latency (ms)")

class PartitionConfig(BaseModel):
    """Configuration for a code partition."""
    name: str = Field(..., description="Human-readable partition name")
    repositories: List[RepositoryConfig] = Field(..., description="Repositories in this partition")
    performance_targets: PerformanceTargets = Field(default_factory=PerformanceTargets)
    graph_cross_repo: bool = Field(True, description="Enable cross-repo call graph edges within partition")

class CodeIndexConfig(BaseModel):
    """Configuration for entire code index."""
    partitions: Dict[str, PartitionConfig] = Field(..., description="Partition definitions (key = partition_name)")
    chunking_strategy: str = Field(default="ast", description="Chunking strategy: 'ast' or 'line'")
    # ... existing fields from AST-Aware Chunking spec
```

**Why this works:**
- Validation happens at config load time (fail fast)
- Descriptive error messages guide users to fix issues
- Type safety prevents runtime errors

---

### 1.7 Error Handling Strategy

**Pattern:** Fail gracefully, log actionable errors, don't block entire system.

**Implementation:**

```python
# Error handling examples

# 1. Git sync failures: Log error, mark repo as failed, CONTINUE with other repos
try:
    sync_result = self.syncer.sync_repository(repo_config)
    if not sync_result.success:
        raise Exception(sync_result.error)
except Exception as e:
    logger.error(f"Sync failed for {repo_config.name}: {e}")
    self.tracker.mark_failed(repo_config.name, str(e))
    # RETURN, don't crash entire process
    return RebuildStats(parse_errors=1)

# 2. Parse errors: Log warning, skip file, CONTINUE with other files
for file_path in changed_files:
    try:
        self.update_file(file_path, repo_config)
        stats.files_updated += 1
    except Exception as e:
        logger.warning(f"Parse error for {file_path}: {e}")
        stats.parse_errors += 1
        # CONTINUE, don't fail entire repo

# 3. Schema drift: Validate fields, fail fast with actionable error
def search(self, query: str, filters: Dict):
    # Validate partition field exists
    if "partition" in filters:
        partition = filters["partition"]
        if partition not in self.partitions:
            raise ValueError(
                f"Partition '{partition}' not found. "
                f"Available partitions: {list(self.partitions.keys())}. "
                f"Check mcp.yaml config."
            )

# 4. Orphaned data: Warn at startup, provide cleanup command, DON'T auto-delete
orphaned = self.manager.detect_orphaned_data()
if orphaned:
    logger.warning(
        f"Orphaned index data detected: {orphaned}. "
        f"These partitions are not in mcp.yaml config. "
        f"To clean up: python -m ouroboros.tools.cleanup_partitions {' '.join(orphaned)}"
    )
    # Don't auto-delete! User must explicitly approve.
```

**Principles:**
- **Partial degradation** over total failure
- **Actionable errors** with remediation steps
- **User control** for destructive operations (no auto-delete)

---

### 1.8 Sparse Checkout for Large Repos

**Pattern:** Clone only specific subdirectories to save disk space and time.

**Implementation:**

```python
# ouroboros/subsystems/rag/code/syncer.py

import git

def sparse_clone(self, url: str, target: Path, sparse_paths: List[str]) -> str:
    """
    Clone repository with sparse checkout (only specified subdirectories).
    
    Args:
        url: Remote Git URL
        target: Local target directory
        sparse_paths: List of paths to checkout (e.g., ["instrumentation/openai"])
    
    Returns:
        Commit hash of cloned HEAD
    """
    # Initialize empty repo
    repo = git.Repo.init(target)
    
    # Enable sparse checkout
    repo.git.config("core.sparseCheckout", "true")
    
    # Write sparse-checkout file
    sparse_file = target / ".git" / "info" / "sparse-checkout"
    sparse_file.parent.mkdir(parents=True, exist_ok=True)
    sparse_file.write_text("\n".join(sparse_paths))
    
    # Add remote and fetch
    origin = repo.create_remote("origin", url)
    origin.fetch()
    
    # Checkout main branch (only sparse paths)
    repo.git.checkout("main")
    
    # Return HEAD commit hash
    return repo.head.commit.hexsha
```

**Performance Impact:**
- Full repo: 10K files, 2GB, 5 minutes clone
- Sparse (instrumentation/ only): 500 files, 100MB, 1 minute clone
- **20x smaller disk, 5x faster clone**

---

## 2. Testing Summary

Comprehensive testing documentation is provided in the `testing/` subdirectory:

- **requirements-list.md:** All 32 requirements (10 FR, 22 NFR) with descriptions
- **functional-tests.md:** Test cases for all 10 functional requirements
- **nonfunctional-tests.md:** Verification tests for all 22 non-functional requirements
- **test-strategy.md:** Unit, integration, and E2E testing approach

**Key Testing Metrics:**
- **Total Test Cases:** 56 (27 functional + 29 non-functional)
- **Coverage Target:** 85% code coverage
- **Performance Targets:** Primary p95 < 50ms, Instrumentors p95 < 200ms, Extraction < 15 min
- **Reliability Target:** Parse error rate < 5%, sync success rate > 95%

**Test Pyramid:**
- **Unit Tests (70%):** Fast, isolated, mocked dependencies
- **Integration Tests (20%):** Multi-component workflows
- **E2E Tests (10%):** Full extraction workflows on real instrumentors

See `testing/test-strategy.md` for complete details.

---

## 3. Deployment Guidance

### 3.1 Pre-Deployment Checklist

Before deploying to production, verify:

- [ ] All Phase 0-6 tasks completed (see tasks.md)
- [ ] Config validation passes (`python -m ouroboros.tools.validate_config`)
- [ ] All unit tests pass (>= 85% coverage)
- [ ] All integration tests pass
- [ ] Performance benchmarks meet targets (p95 < 200ms)
- [ ] Backup existing code index to `.archive/pre-multi-repo-backup/`
- [ ] Git credentials configured (SSH keys or env vars)
- [ ] Disk space available (estimate: primary 500MB + instrumentors 2GB)

---

### 3.2 Phased Rollout Strategy

**Phase 0: Pre-Deployment (30 minutes)**

1. **Backup existing index:**
   ```bash
   cd /path/to/praxis-os
   mkdir -p .archive/pre-multi-repo-backup
   cp -r .indexes/code .archive/pre-multi-repo-backup/
   ```

2. **Validate config:**
   ```bash
   python -m ouroboros.tools.validate_config config/mcp.yaml
   ```

3. **Run schema migrations:**
   ```bash
   python -m ouroboros.tools.migrate_schemas --dry-run
   python -m ouroboros.tools.migrate_schemas  # Apply if dry-run looks good
   ```

---

**Phase 1: Primary Partition Only (1 hour)**

Deploy with ONLY primary partition to validate:

1. **Update mcp.yaml:**
   ```yaml
   indexes:
     code:
       partitions:
         primary:
           name: "Primary Code"
           repositories:
             - name: "praxis-os"
               path: "/Users/josh/src/github.com/honeyhiveai/praxis-os/ouroboros/"
               provider: "local"
         # instrumentors partition commented out for Phase 1
   ```

2. **Restart MCP server:**
   ```bash
   # Kill existing server
   pkill -f "python.*mcp_server"
   
   # Start with new config
   python -m ouroboros.mcp_server
   ```

3. **Verify primary partition:**
   ```python
   # In Python REPL or test script
   from ouroboros.subsystems.rag.code.code_index import CodeIndex
   
   index = CodeIndex.from_config()
   health = index.health_check()
   print(health)  # Should show primary partition healthy
   
   # Test query
   results = index.search("health check implementation", action="search_code")
   print(f"Found {len(results)} results")
   ```

4. **Monitor for 24 hours:**
   - Check MCP logs for errors
   - Monitor query latency (should be < 50ms p95)
   - Verify no regressions in existing functionality

---

**Phase 2: Add 3 Test Instrumentors (4 hours)**

Add small instrumentors to test multi-repo before scaling:

1. **Update mcp.yaml to add instrumentors partition:**
   ```yaml
   instrumentors:
     name: "OpenTelemetry Instrumentors"
     repositories:
       - name: "fastapi-instrumentation"
         url: "https://github.com/open-telemetry/opentelemetry-python-contrib"
         sparse_paths: ["instrumentation/opentelemetry-instrumentation-fastapi"]
         provider: "opentelemetry"
       - name: "langchain-instrumentation"
         url: "https://github.com/traceloop/openllmetry"
         sparse_paths: ["packages/opentelemetry-instrumentation-langchain"]
         provider: "traceloop"
       - name: "openai-instrumentation"
         url: "https://github.com/openlit/openlit"
         sparse_paths: ["sdk/python/src/openlit/instrumentation/openai"]
         provider: "openlit"
     performance_targets:
       semantic: {p95_ms: 200}
       ast: {p95_ms: 75}
       graph: {p95_ms: 150}
     graph_cross_repo: false
   ```

2. **Restart MCP server** (indexes new partition automatically)

3. **Monitor initial indexing:**
   ```bash
   tail -f ~/.praxis-os/logs/mcp_server.log
   # Watch for "Indexing repository: fastapi-instrumentation"
   # Should complete in ~5-10 minutes for 3 repos
   ```

4. **Test queries on instrumentors partition:**
   ```python
   results = index.search(
       "span.set_attribute http method",
       action="search_code",
       filters={"partition": "instrumentors"}
   )
   print(f"Found {len(results)} results across instrumentors")
   ```

5. **Run extraction workflow on 1 instrumentor:**
   ```python
   from ouroboros.subsystems.rag.code.workflows.extraction import extract_span_attributes
   
   report = extract_span_attributes("fastapi-instrumentation")
   print(f"Extracted {len(report.attributes)} attributes")
   # Should complete in < 15 minutes
   ```

6. **Monitor for 48 hours** before scaling to all 270 instrumentors

---

**Phase 3: Scale to All 270 Instrumentors (8-10 hours initial index)**

Once Phase 2 is stable:

1. **Add remaining instrumentors to mcp.yaml** (see design doc for full list)

2. **Trigger incremental build:**
   ```bash
   python -m ouroboros.tools.rebuild_partition instrumentors --incremental
   ```

3. **Monitor cold start time** (should be < 10 minutes for full 270 instrumentors if parallelized)

4. **Validate performance targets:**
   - Primary p95 < 50ms (unchanged from Phase 1)
   - Instrumentors p95 < 200ms
   - Total disk usage < 3GB

5. **Setup cron for daily sync:**
   ```bash
   # Add to crontab
   0 2 * * * /path/to/praxis-os/scripts/sync_instrumentors.sh >> /var/log/praxis-os-sync.log 2>&1
   ```

---

### 3.3 Rollback Procedure

If issues arise, rollback in reverse order:

**Rollback from Phase 3 → Phase 2:**
1. Remove extra instrumentors from mcp.yaml (keep only 3 test repos)
2. Soft delete instrumentor data: `python -m ouroboros.tools.delete_partition instrumentors --soft`
3. Restart MCP server

**Rollback from Phase 2 → Phase 1:**
1. Remove instrumentors partition from mcp.yaml
2. Soft delete instrumentor data: `python -m ouroboros.tools.delete_partition instrumentors --soft`
3. Restart MCP server

**Rollback from Phase 1 → Pre-Deployment:**
1. Stop MCP server
2. Restore backup: `rm -rf .indexes/code && cp -r .archive/pre-multi-repo-backup/code .indexes/`
3. Revert mcp.yaml to pre-deployment version
4. Restart MCP server

**Rollback SLA:** < 2 minutes (NFR-R3)

---

### 3.4 Monitoring and Alerts

**Key Metrics to Monitor:**

1. **Query Latency (p95):**
   - Primary partition: Alert if > 50ms
   - Instrumentors partition: Alert if > 200ms

2. **Index Health:**
   - Check health endpoint every 5 minutes: `/health/code_index`
   - Alert if any partition unhealthy

3. **Repository Sync Status:**
   - Check `repository_state` table for "sync_failed" status
   - Alert if > 5% repos failed

4. **Disk Usage:**
   - Monitor `.indexes/code/` directory size
   - Alert if > 3GB

5. **Parse Error Rate:**
   - Check logs for parse errors
   - Alert if > 5% of files fail to parse

**Logging:**

```python
# Standard log format for correlation
logger.info(
    "Repository sync completed",
    extra={
        "repo_name": repo_config.name,
        "partition": partition_name,
        "files_updated": stats.files_updated,
        "parse_errors": stats.parse_errors,
        "duration_ms": stats.total_time_ms
    }
)
```

---

## 4. Troubleshooting Guide

### 4.1 Common Issues and Solutions

#### Issue 1: Config Validation Fails

**Symptom:**
```
ValueError: Repository 'python-sdk' must have either 'path' or 'url'
```

**Cause:** Config missing required fields

**Solution:**
```yaml
# ❌ BAD
repositories:
  - name: "python-sdk"
    provider: "honeyhive"
    # Missing path or url!

# ✅ GOOD
repositories:
  - name: "python-sdk"
    url: "https://github.com/honeyhiveai/python-sdk"
    provider: "honeyhive"
```

---

#### Issue 2: Git Sync Fails (Authentication)

**Symptom:**
```
ERROR: Sync failed for openai-instrumentation: Authentication failed
```

**Cause:** SSH keys not configured or HTTPS credentials missing

**Solution:**

For SSH URLs:
```bash
# Test SSH access
ssh -T git@github.com
# Should return: "Hi username! You've successfully authenticated..."

# If fails, add SSH key to ssh-agent
ssh-add ~/.ssh/id_rsa
```

For HTTPS URLs:
```bash
# Set credential helper (Linux/Mac)
git config --global credential.helper store

# Or use environment variable
export GIT_ASKPASS=/path/to/credential/helper
```

**Alternative:** Use SSH URLs instead of HTTPS:
```yaml
# ✅ Recommended
url: "git@github.com:honeyhiveai/python-sdk.git"

# ❌ Avoid (requires password)
url: "https://github.com/honeyhiveai/python-sdk.git"
```

---

#### Issue 3: Query Latency Exceeds Target

**Symptom:**
```
WARNING: Query latency p95 = 350ms (target: 200ms)
```

**Cause:** Searching all partitions instead of specific partition

**Solution:**

```python
# ❌ SLOW: Searches all partitions (437K chunks)
results = index.search("span attributes", action="search_code")

# ✅ FAST: Routes to specific partition (324K chunks)
results = index.search(
    "span attributes",
    action="search_code",
    filters={"partition": "instrumentors"}
)
```

**If still slow after filtering:**
1. Check chunk count: `SELECT COUNT(*) FROM chunks WHERE partition = 'instrumentors'`
2. Verify vector index exists: `SHOW INDEXES FROM chunks`
3. Profile query: Enable debug logging to see time breakdown
4. Consider concurrent indexing optimization (see specs.md Section 6.5)

---

#### Issue 4: Parse Errors for Specific Files

**Symptom:**
```
WARNING: Parse error for instrumentor.py: Unexpected token at line 45
```

**Cause:** Syntax error in source file or Tree-sitter version mismatch

**Solution:**

1. **Verify file syntax manually:**
   ```bash
   python -m py_compile /path/to/instrumentor.py
   ```

2. **Check Tree-sitter version:**
   ```python
   import tree_sitter_python
   print(tree_sitter_python.BINDING_VERSION)
   # Should be >= 0.20.0
   ```

3. **Skip problematic files (if legitimate syntax issue):**
   - Parse errors are logged but don't block repo
   - File will be skipped, rest of repo continues

4. **Update Tree-sitter bindings if needed:**
   ```bash
   pip install --upgrade tree-sitter-python
   ```

---

#### Issue 5: Orphaned Data Warning at Startup

**Symptom:**
```
WARNING: Orphaned index data detected: ['old_instrumentors_backup']
```

**Cause:** Partition removed from config but data still on disk

**Solution:**

1. **Review orphaned partition:**
   ```bash
   ls -lh .indexes/code/old_instrumentors_backup/
   # Check if data is actually needed
   ```

2. **Clean up if not needed:**
   ```bash
   python -m ouroboros.tools.cleanup_partitions old_instrumentors_backup
   ```

3. **Or restore if accidentally removed from config:**
   - Add partition back to mcp.yaml
   - Restart MCP server

**Prevention:** Use soft delete for partitions (archives data for rollback)

---

#### Issue 6: Disk Usage Exceeds 3GB

**Symptom:**
```
ALERT: Disk usage = 3.5GB (target: < 3GB)
```

**Cause:** Too many instrumentors indexed or no sparse checkout

**Solution:**

1. **Use sparse checkout for large repos:**
   ```yaml
   - name: "opentelemetry-contrib"
     url: "https://github.com/open-telemetry/opentelemetry-python-contrib"
     sparse_paths: ["instrumentation/opentelemetry-instrumentation-*"]  # ✅
     # Instead of cloning entire 2GB repo
   ```

2. **Remove unused repositories:**
   ```python
   partition.remove_repository("unused-instrumentor")
   ```

3. **Compact indexes:**
   ```bash
   # DuckDB: VACUUM to reclaim space
   python -m ouroboros.tools.compact_indexes --partition instrumentors
   ```

4. **Archive old partition data:**
   ```bash
   python -m ouroboros.tools.delete_partition old_partition --soft
   ```

---

#### Issue 7: Cross-Repo Graph Traversal Incorrect

**Symptom:**
```
Query returns cross-repo edges despite graph_cross_repo: false
```

**Cause:** Bug in graph query filtering

**Diagnosis:**
```sql
-- Check relationships table for cross-repo edges
SELECT COUNT(*) FROM relationships
WHERE caller_repo != callee_repo
  AND caller_id IN (SELECT symbol_id FROM symbols WHERE partition = 'instrumentors');
-- Should be 0 if graph_cross_repo = false
```

**Solution:**

Verify graph query includes cross-repo filter:
```sql
WITH RECURSIVE call_chain AS (
    SELECT r.caller_id, s.symbol_name, s.repo_name, 1 AS depth
    FROM relationships r
    JOIN symbols s ON r.caller_id = s.symbol_id
    WHERE r.callee_id = :target_symbol_id
      AND s.partition = :partition
      AND (:allow_cross_repo = TRUE OR r.caller_repo = r.callee_repo)  -- ✅ Filter
)
SELECT * FROM call_chain;
```

---

### 4.2 Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Set log level to DEBUG
export PRAXIS_LOG_LEVEL=DEBUG

# Or in mcp.yaml
logging:
  level: DEBUG
  file: ~/.praxis-os/logs/mcp_debug.log
```

**Useful debug logs:**
- Partition routing decisions
- Query execution plans
- Parse timings per file
- Git sync output
- Health check details

---

### 4.3 Performance Profiling

If queries are slow, profile to identify bottlenecks:

```python
import cProfile
import pstats

# Profile a query
profiler = cProfile.Profile()
profiler.enable()

results = index.search("span attributes", action="search_code", filters={"partition": "instrumentors"})

profiler.disable()

# Print top 20 slowest functions
stats = pstats.Stats(profiler)
stats.sort_stats('cumtime')
stats.print_stats(20)
```

**Common bottlenecks:**
1. **Vector search:** Optimize by reducing `n_results` or using IVF_PQ index
2. **FTS search:** Ensure Tantivy index is built
3. **Graph traversal:** Limit `max_depth` to avoid exponential explosion
4. **Parse time:** Use concurrent indexing for large repos

---

## 5. Success Criteria

Deployment is successful when:

- [ ] All 32 requirements met (10 FR + 22 NFR)
- [ ] Primary partition queries < 50ms p95
- [ ] Instrumentors partition queries < 200ms p95
- [ ] Extraction workflow < 15 minutes per instrumentor
- [ ] All unit tests pass (>= 85% coverage)
- [ ] All integration tests pass
- [ ] No regressions in existing single-repo functionality
- [ ] Health checks show all partitions healthy
- [ ] Disk usage < 3GB
- [ ] Zero data loss during deployment
- [ ] Rollback tested and < 2 minutes

---

## 6. Next Steps

After successful deployment:

1. **Production Monitoring:** Setup alerts for key metrics (see Section 3.4)
2. **User Documentation:** Create user guide for querying multi-repo indexes
3. **Automation:** Setup cron jobs for daily instrumentor sync
4. **Scale Testing:** Validate performance with full 270 instrumentors
5. **Optimization:** Implement concurrent indexing if cold start > 10 minutes (specs.md Section 6.5)
6. **Feature Requests:** Gather feedback from HoneyHive team on extraction workflows

---

## 7. References

- **srd.md:** Requirements specification (32 requirements)
- **specs.md:** Technical design (1,659 lines)
- **tasks.md:** Implementation tasks (26 tasks, 7 phases, 25-30 hours)
- **testing/requirements-list.md:** Requirements traceability matrix
- **testing/functional-tests.md:** Functional test cases (27 tests)
- **testing/nonfunctional-tests.md:** Non-functional test cases (29 tests)
- **testing/test-strategy.md:** Testing approach and methodology
- **Design Document:** `.praxis-os/design/2025-11-12-multi-repo-code-intelligence.md` (supporting docs)

---

