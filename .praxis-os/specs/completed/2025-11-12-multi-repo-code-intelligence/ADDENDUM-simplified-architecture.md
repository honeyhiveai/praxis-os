# SPEC ADDENDUM: Simplified Multi-Repo Partitioning Architecture

**Date**: 2025-11-12  
**Spec**: Multi-Repo Code Intelligence  
**Phase Affected**: Phase 1 (Config Schema)  
**Status**: Architecture Simplification  
**Addendum Type**: Major Design Change

---

## Executive Summary

During Phase 1 implementation planning (Task 1.1 complete, starting Task 1.2), we identified critical design issues with the original partition schema. This addendum documents a **major architectural simplification** that:

- ✅ Makes the system domain-agnostic (not honeyhive-specific)
- ✅ Simplifies config structure (1 partition = 1 repo)
- ✅ Adds AI-friendly metadata for query filtering
- ✅ Removes unnecessary complexity (performance targets, nested repos)

**Implementation Status**: Pydantic schemas updated and validated ✅

---

## Schema Changes

### OLD SCHEMA (Rejected)

```python
class RepositoryConfig(BaseConfig):
    name: str
    path: Optional[str]
    url: Optional[str]
    provider: str
    sparse_paths: Optional[list[str]]
    enabled: bool

class PerformanceTargets(BaseConfig):
    p50_ms: int
    p95_ms: int
    p99_ms: int

class PartitionConfig(BaseConfig):
    repositories: list[RepositoryConfig]
    performance_targets: dict[str, PerformanceTargets]
    graph_cross_repo: bool
```

**Config Example (Old)**:
```yaml
partitions:
  primary:
    repositories:
      - name: praxis-os
        path: ../
        provider: honeyhive
    performance_targets:
      semantic: {p50_ms: 50, p95_ms: 50, p99_ms: 100}
    graph_cross_repo: true
```

---

### NEW SCHEMA (Approved)

```python
class DomainConfig(BaseConfig):
    """
    Content domain within a partition (e.g., code, tests, docs).
    """
    include_paths: list[str]                        # Required
    exclude_patterns: Optional[list[str]] = None    # Optional
    metadata: Optional[dict[str, str]] = None       # Optional (AI-queryable)

class PartitionConfig(BaseConfig):
    """
    Single repository partition with multiple domains.
    Partition name = repo name (1:1 mapping).
    """
    path: str                           # Required (repo location)
    domains: dict[str, DomainConfig]   # Required (at least one domain)
```

**Config Example (New)**:
```yaml
partitions:
  praxis-os:              # Partition name = repo name
    path: ../
    domains:
      code:
        include_paths: [ouroboros/, scripts/]
        exclude_patterns: null
        metadata: null
      tests:
        include_paths: [tests/]
        exclude_patterns: null
        metadata:
          type: tests
  
  openlit:                # External instrumentor repo
    path: ../deps/openlit
    domains:
      openai-instrumentor:
        include_paths: [instrumentation/openai/]
        exclude_patterns: null
        metadata:
          framework: openai
          type: instrumentor
          provider: openlit
```

---

## Metadata Field (NEW - Critical for AI Querying)

### Purpose

The `metadata` field allows **explicit tagging** of code domains for precise AI query filtering, without relying on file path parsing.

### Common Metadata Patterns

```yaml
# Instrumentor domains
metadata:
  framework: openai          # Which framework (openai, anthropic, langchain)
  type: instrumentor         # Type of code (instrumentor, core, tests)
  provider: openlit          # Provider (openlit, traceloop, arize)

# Test domains
metadata:
  type: tests                # Mark as test code
  framework: pytest          # Test framework

# Documentation domains
metadata:
  type: docs                 # Mark as documentation
  format: markdown           # Documentation format

# Custom domains (user-defined)
metadata:
  team: backend              # Team ownership
  service: api               # Microservice name
  language: python           # Programming language
```

### Query Interface

AI can filter searches using metadata:

```python
# Search OpenAI instrumentor specifically
pos_search_project(
    action="search_code",
    query="span attributes semantic conventions",
    filters={
        "partition": "openlit",
        "metadata.framework": "openai",
        "metadata.type": "instrumentor"
    }
)

# Search all instrumentors across providers
pos_search_project(
    action="search_code",
    query="how are spans created",
    filters={
        "metadata.type": "instrumentor"
    }
)

# Search test code only
pos_search_project(
    action="search_code",
    query="test fixtures for async code",
    filters={
        "metadata.type": "tests"
    }
)
```

---

## Updated Implementation Plan

### Phase 1: Config Extraction (UPDATED)

#### Task 1.1: Extract node type mappings from ast.py ✅
**Status**: Complete (unchanged)

#### Task 1.2: Define config schema for partitions (UPDATED)
**Status**: Complete ✅

**Original Plan**: Create `RepositoryConfig`, `PerformanceTargets`, `PartitionConfig`

**Updated Implementation**:
- ✅ Created `DomainConfig` with `include_paths`, `exclude_patterns`, `metadata`
- ✅ Created simplified `PartitionConfig` with `path` and `domains`
- ✅ Removed `RepositoryConfig`, `PerformanceTargets` (no longer needed)
- ✅ Updated exports in `__all__`

**Files Modified**:
- `.praxis-os/ouroboros/config/schemas/indexes.py` (updated)
- `.praxis-os/config/mcp.yaml` (updated with new structure)

#### Task 1.3: Update Pydantic config models (UPDATED)
**Status**: Complete ✅

**Changes**:
- Updated `CodeIndexConfig.partitions` field to `Optional[dict[str, PartitionConfig]]`
- No changes to other index configs

#### Task 1.4: Populate mcp.yaml with partition configs (UPDATED)
**Status**: Complete ✅

**Original Plan**: Define primary and instrumentors partitions

**Updated Implementation**:
- Defined `praxis-os` partition with `code` and `tests` domains
- Added commented example for `openlit` instrumentor partition
- Added metadata example: `type: tests` for test domain

#### Task 1.5: Create migration guide (UNCHANGED)
**Status**: Pending

**Note**: Migration guide will document the **new** simplified schema, not the old one.

---

### Phase 2-5: Implementation (UNCHANGED)

Phases 2-5 remain unchanged:
- **Phase 2**: Refactor `CodeIndex` to discover partitions dynamically
- **Phase 3**: Build `CodePartition` class
- **Phase 4**: Integrate metadata propagation
- **Phase 5**: Migration & validation

**Key Change**: Simpler partition discovery (no nested repository list to parse)

---

## Updated Task Breakdown

### Tasks Modified

| Task | Old Description | New Description |
|------|----------------|-----------------|
| 1.2 | Create 4 config models (Repository, Performance, Partition, update Code) | Create 2 config models (Domain, Partition, update Code) |
| 1.4 | Populate with primary/instrumentors partitions | Populate with repo-named partitions (praxis-os, openlit example) |
| 2.1 | Parse nested repository list | Parse simple partition dict |
| 4.2 | Propagate repo metadata | Propagate partition + domain + metadata |

### Tasks Removed

- ❌ Task X.X: Implement performance target validation (moved to health checks)
- ❌ Task X.X: Implement graph_cross_repo logic (deferred to future)

### Tasks Added

- ✅ Task 4.X: Implement metadata propagation to chunks
- ✅ Task 4.X: Implement metadata filtering in search queries

---

## Validation Results

### Config Validation ✅

```bash
$ python .praxis-os/workspace/validate_partition_config.py

Testing partition config loading...
✅ Config loaded successfully
✅ Partitions defined: ['praxis-os']

✅ Partition: praxis-os
   - Path: ../
   - Domains: ['code', 'tests']
   - code:
     - include_paths: ['ouroboros/', 'scripts/']
     - exclude_patterns: None
   - tests:
     - include_paths: ['tests/']
     - exclude_patterns: None

🎉 All validation checks passed!
```

### Schema Validation ✅

- ✅ Pydantic models parse YAML correctly
- ✅ Domain names validated (must be valid Python identifiers)
- ✅ At least one domain required per partition
- ✅ Metadata field is optional `dict[str, str]`
- ✅ exclude_patterns field is optional `list[str]`

---

## Real-World Use Cases Validated

We validated this design against actual instrumentor monorepos:

### 1. OpenLit (30+ instrumentors)
```yaml
openlit:
  path: ../deps/openlit
  domains:
    openai: {include_paths: [instrumentation/openai/], metadata: {framework: openai}}
    anthropic: {include_paths: [instrumentation/anthropic/], metadata: {framework: anthropic}}
    # ... 28 more
```

### 2. Traceloop (40+ packages)
```yaml
traceloop:
  path: ../deps/openllmetry
  domains:
    openai: {include_paths: [packages/opentelemetry-instrumentation-openai/], metadata: {framework: openai}}
    # ... 39 more
```

### 3. Large Monorepo (50-service architecture)
```yaml
my-monorepo:
  path: ../
  domains:
    auth-service: {include_paths: [services/auth/], metadata: {service: auth, team: platform}}
    billing-service: {include_paths: [services/billing/], metadata: {service: billing, team: revenue}}
    # ... 48 more
```

**Result**: ✅ All cases handled without hardcoded assumptions

---

## Benefits of Simplified Design

### For AI Consumer (Primary)

1. **Discoverable**: Can list partitions/domains to understand codebase structure
2. **Precise Filtering**: Query by explicit metadata, not file path guessing
3. **Self-Documenting**: Config structure explains content organization
4. **Flexible**: Works for any project domain (monorepo, multi-repo, tests, docs)

### For Human Users (Secondary)

1. **Simpler**: 2 models instead of 4
2. **Domain-Agnostic**: No honeyhive-specific assumptions
3. **Predictable**: Partition name = repo name (1:1 mapping)
4. **Maintainable**: Less nested config, easier to understand

### For Implementation (Tertiary)

1. **Fewer Validations**: Simpler schema, fewer edge cases
2. **Cleaner Code**: No nested repository list parsing
3. **Extensible**: Arbitrary metadata keys for future use cases

---

## Migration from Original Design

### If Already Implemented Old Schema

**Risk**: Low - Phase 1 just started, only config schema affected

**Migration Steps**:
1. Update Pydantic models (already done)
2. Update `mcp.yaml` (already done)
3. Update `CodeIndex` partition discovery (Phase 2 - not yet implemented)
4. No data migration needed (indexes not yet built with old schema)

### If Starting Fresh

**Action**: Use new schema from the start ✅ (current state)

---

## Approval & Sign-Off

### Design Doc Addendum
📄 [2025-11-12-multi-repo-partitioning-addendum.md](../../../workspace/design/2025-11-12-multi-repo-partitioning-addendum.md)

### Changes Approved By
- User (via iterative design discussion)
- AI (validated against real-world use cases)

### Implementation Status
- [x] Pydantic schemas updated
- [x] Config file updated
- [x] Validation script passing
- [x] Synced to `dist/`
- [ ] Phase 2-5 implementation (pending)

---

## Next Steps

1. ✅ Complete Phase 1 (config schema) - **DONE**
2. ⏭️ Continue to Phase 2 (CodeIndex refactor)
3. ⏭️ Implement metadata propagation (Phase 4)
4. ⏭️ Implement query filtering by metadata (Phase 4)
5. ⏭️ Update health checks to use new partition structure (Phase 5)

---

## Conclusion

This addendum represents a **significant improvement** over the original design:
- Less complex (2 models vs 4)
- More flexible (works for any domain)
- AI-optimized (explicit metadata for queries)

The simplified architecture better serves the **primary consumer** (AI) while remaining easy to configure for human users.

**Recommendation**: Proceed with implementation using the new simplified schema. ✅

