# Software Requirements Document

**Project:** Multi-Repo Code Intelligence for Instrumentor Analysis  
**Date:** 2025-11-12  
**Priority:** High  
**Category:** Feature

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for extending prAxIs OS code intelligence to support multi-repository indexing and automated extraction of semantic conventions from OpenTelemetry instrumentor codebases.

### 1.2 Scope
This feature will enable HoneyHive developers to analyze external instrumentor repositories (OpenTelemetry, OpenLit, Traceloop, Arize) to automatically extract semantic conventions, span naming patterns, and attribute mappings for the ingestion service trace parser. The system will index multiple repositories simultaneously using a partition-based architecture, support incremental updates, and provide structured query workflows with machine-readable output.

---

## 2. Business Goals

### Goal 1: Accelerate Instrumentor Analysis

**Objective:** Reduce time required to analyze a single instrumentor codebase from 3 hours (manual) to 15 minutes (automated), achieving a 12x speed improvement.

**Success Metrics:**
- **Analysis time**: 3 hours (manual) → 15 minutes (automated)
- **Throughput**: 1 instrumentor per 3 hours → 4 instrumentors per hour
- **First month adoption**: 5 instrumentors analyzed using automated workflows

**Business Impact:**
- Enables HoneyHive to support more frameworks faster, accelerating BYOI (Bring Your Own Instrumentor) feature adoption
- Reduces developer time spent on repetitive analysis tasks by 92%
- Expected developer time savings: ~14 hours per week at scale (5 instrumentors/week)

### Goal 2: Improve Extraction Accuracy and Completeness

**Objective:** Achieve 100% coverage of `set_attribute()` calls through AST-based code search, eliminating manual transcription errors and missed edge cases.

**Success Metrics:**
- **Attribute coverage**: ~85% (manual grep) → 100% (AST search)
- **Transcription errors**: ~10% (manual) → 0% (automated)
- **Undocumented conventions discovered**: 0 (manual docs only) → 100% (code analysis)

**Business Impact:**
- Improves accuracy of ingestion service trace parser mappings
- Reduces debugging time for missing or incorrect attribute mappings
- Discovers conventions not documented in instrumentor official docs

### Goal 3: Enable Scale Across Multiple Instrumentor Providers

**Objective:** Support analysis of 270 instrumentors across 4 providers (OpenTelemetry, OpenLit, Traceloop, Arize) totaling 437K code chunks, with query performance maintained below 200ms p95.

**Success Metrics:**
- **Instrumentor coverage**: 30+ (manual) → 270 (automated)
- **Providers supported**: 1 (OpenTelemetry) → 4 (OTel, OpenLit, Traceloop, Arize)
- **Index scale**: 113K chunks (single repo) → 437K chunks (multi-repo)
- **Query latency p95**: < 200ms (instrumentors partition), < 50ms (primary partition)

**Business Impact:**
- Comprehensive framework support for HoneyHive customers
- Competitive differentiation through breadth of instrumentor coverage
- Future-proofed architecture for monorepos and cross-project analysis

### Goal 4: Maintain Accuracy Through Incremental Updates

**Objective:** Enable re-analysis of instrumentors when they release updates, detecting breaking changes in semantic conventions automatically.

**Success Metrics:**
- **Re-analysis time**: 3 hours (full manual re-analysis) → 2-5 seconds (incremental)
- **Update detection**: Manual (reactive) → Automated (proactive)
- **Breaking change identification**: 0% (not tracked) → 100% (automated diff)

**Business Impact:**
- Reduces maintenance burden as instrumentors evolve
- Proactive detection of breaking changes before customer impact
- Enables versioned semantic convention mappings

## 2.1 Supporting Documentation

The business goals above are informed by:
- **Multi-Repo Code Intelligence Design Document (2025-11-11)**: Executive Summary, Problem Statement, Success Metrics, and Real-World Impact sections

See `supporting-docs/INDEX.md` for complete analysis.

---

## 3. User Stories

User stories describe the feature from the user's perspective.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: Analyze Instrumentor Codebase

**As a** HoneyHive developer maintaining the ingestion service  
**I want to** automatically extract all semantic conventions (`span.set_attribute()` calls) from an instrumentor codebase  
**So that** I can create accurate trace parser mappings without manual code review and transcription errors

**Acceptance Criteria:**
- Given an OpenTelemetry instrumentor repository URL
- When I run the extraction workflow
- Then I receive a structured list of all attribute keys, value sources, and usage context
- And the extraction completes in < 15 minutes
- And all `set_attribute()` calls are discovered (100% coverage)

**Priority:** Critical

---

### Story 2: Track Multiple Instrumentor Providers

**As a** HoneyHive developer  
**I want to** index instrumentors from multiple providers (OpenTelemetry, OpenLit, Traceloop, Arize) simultaneously  
**So that** I can compare conventions across providers and support diverse customer needs

**Acceptance Criteria:**
- Given 270 instrumentor repositories across 4 providers
- When I configure the multi-repo index with provider partitions
- Then all repositories are indexed and queryable
- And queries can filter by provider (`provider: "openlit"`)
- And index scale reaches 437K chunks with p95 query latency < 200ms

**Priority:** Critical

---

### Story 3: Detect Instrumentor Updates

**As a** HoneyHive developer  
**I want to** re-analyze an instrumentor when it releases a new version  
**So that** I can detect breaking changes in semantic conventions and update our mappings proactively

**Acceptance Criteria:**
- Given an instrumentor that has been previously indexed
- When the instrumentor releases a new version
- Then I can trigger an incremental re-index
- And the system detects changed files only (not full re-index)
- And a diff report shows added/removed/modified attributes
- And the incremental update completes in < 5 seconds

**Priority:** High

---

### Story 4: Export Machine-Readable Conventions

**As a** HoneyHive developer  
**I want to** export extracted semantic conventions as YAML or JSON  
**So that** I can generate ingestion service mapping code automatically instead of manual transcription

**Acceptance Criteria:**
- Given extracted conventions from an instrumentor
- When I export the results
- Then I receive structured output (YAML/JSON) containing:
  - Attribute keys (e.g., `http.method`)
  - Value sources (e.g., `request.method`)
  - Type information (variable, literal, dynamic)
  - File/line context
- And the output can be used to generate `traceParse.py` mapping code

**Priority:** High

---

### Story 5: Query Across Repositories

**As a** HoneyHive developer  
**I want to** search for code patterns across all indexed instrumentors  
**So that** I can find common conventions and framework-specific patterns

**Acceptance Criteria:**
- Given 270 indexed instrumentor repositories
- When I search for a pattern (e.g., "span naming patterns")
- Then I receive results grouped by repository and provider
- And I can filter by partition (`partition: "instrumentors"`)
- And I can filter by specific provider (`provider: "opentelemetry"`)
- And I can filter by specific repository (`repo_name: "fastapi-instrumentation"`)

**Priority:** High

---

### Story 6: Analyze My Own Multi-Project Codebase

**As a** HoneyHive developer working on the primary codebase  
**I want to** index multiple related projects (praxis-os + python-sdk) in the primary partition  
**So that** I can perform cross-project code intelligence queries without mixing external instrumentors

**Acceptance Criteria:**
- Given praxis-os and python-sdk repositories
- When I configure them in the "primary" partition
- Then both are indexed together with cross-repo call graphs enabled
- And queries on the primary partition return results from both repos
- And the primary partition is operationally isolated from instrumentors partition
- And primary partition queries are fast (p95 < 50ms)

**Priority:** Medium

---

## 3.1 Story Priority Summary

**Critical (Must-Have):**
- Story 1: Analyze Instrumentor Codebase (core value proposition)
- Story 2: Track Multiple Instrumentor Providers (scale requirement)

**High Priority:**
- Story 3: Detect Instrumentor Updates (maintenance automation)
- Story 4: Export Machine-Readable Conventions (workflow automation)
- Story 5: Query Across Repositories (multi-repo search)

**Medium Priority:**
- Story 6: Analyze My Own Multi-Project Codebase (secondary use case)

## 3.2 Supporting Documentation

User needs from supporting documents:
- **Multi-Repo Code Intelligence Design Document**: Problem Statement (Section 1.1-1.2) details manual analysis pain points, requirements section (3.1) specifies multi-repo indexing and extraction workflows

See `supporting-docs/INDEX.md` for details.

---

## 4. Functional Requirements

Functional requirements specify capabilities the system must provide.

---

### FR-001: Multi-Repository Indexing

**Description:** The system shall index multiple external Git repositories simultaneously, tracking the source repository for each code chunk.

**Priority:** Critical

**Related User Stories:** Story 1, Story 2, Story 6

**Acceptance Criteria:**
- Support configuration of multiple repository paths (local or remote URLs)
- Track `repo_name` metadata for every indexed chunk, AST node, and graph symbol
- Support relative paths (`../vendor/instrumentor-name/`) and URLs (`https://github.com/org/repo`)
- Index repositories concurrently for performance

---

### FR-002: Partition-Based Index Organization

**Description:** The system shall organize repositories into logical partitions (e.g., "primary", "instrumentors") with independent indexes and operational isolation.

**Priority:** Critical

**Related User Stories:** Story 2, Story 6

**Acceptance Criteria:**
- Support dynamic partition discovery from `mcp.yaml` configuration
- Each partition contains independent Semantic, AST, and Graph indexes
- Queries can filter by partition name (`partition: "instrumentors"`)
- Partitions have independent performance targets and health checks
- No hardcoded partition names (config-driven)

---

### FR-003: Repository State Tracking

**Description:** The system shall track the indexing state of each repository including commit hash, last indexed timestamp, file count, and status.

**Priority:** High

**Related User Stories:** Story 3

**Acceptance Criteria:**
- Store repository state in `repository_state` DuckDB table
- Track: `repo_name`, `commit_hash`, `last_indexed_at`, `file_count`, `status` (indexed/sync_failed/pending)
- Provide query API to retrieve state for a given repository
- Update state atomically after successful index operation

---

### FR-004: Incremental Per-Repository Updates

**Description:** The system shall detect and re-index only changed files when a repository is updated, avoiding full re-indexing.

**Priority:** High

**Related User Stories:** Story 3

**Acceptance Criteria:**
- Compare current commit hash with last indexed commit hash
- Use Git diff to identify added/modified/deleted files
- Re-index only changed files across all 3 indexes (Semantic, AST, Graph)
- Complete incremental update in < 5 seconds for typical changes (< 10 files)
- Atomic update: rollback if any step fails

---

### FR-005: Cross-Repository Query Filtering

**Description:** The system shall support filtering search queries by partition, repository name, and provider metadata.

**Priority:** Critical

**Related User Stories:** Story 2, Story 5

**Acceptance Criteria:**
- Support `filters={"partition": "instrumentors"}` in `pos_search_project()`
- Support `filters={"repo_name": "fastapi-instrumentation"}`
- Support `filters={"provider": "opentelemetry"}`
- Support combining multiple filters (e.g., partition + provider)
- Return search results with repository metadata visible

---

### FR-006: Configurable Cross-Repository Call Graphs

**Description:** The system shall support configuration of cross-repository call graph edges per partition via `graph_cross_repo` flag in `mcp.yaml`.

**Priority:** High

**Related User Stories:** Story 6

**Acceptance Criteria:**
- If `graph_cross_repo: true`, allow edges between symbols in different repositories within the same partition
- If `graph_cross_repo: false`, isolate call graphs per repository (no cross-repo edges)
- Track `caller_repo` and `callee_repo` in GraphIndex `relationships` table
- Filter graph traversal queries based on `graph_cross_repo` configuration

---

### FR-007: Git Repository Synchronization

**Description:** The system shall clone and update Git repositories via standard Git operations (clone, pull, sparse checkout).

**Priority:** High

**Related User Stories:** Story 1, Story 2, Story 3

**Acceptance Criteria:**
- Clone repository on first indexing (if remote URL provided)
- Pull updates on subsequent indexing
- Support sparse checkout for large repos (only index specified subdirectories)
- Handle Git errors gracefully (log error, mark repo as `sync_failed`, continue with other repos)
- Support SSH keys and environment variables for authentication (not inline credentials)

---

### FR-008: Semantic Convention Extraction Workflows

**Description:** The system shall provide structured query workflows to extract semantic conventions (span attributes, naming patterns, events) from instrumentor codebases.

**Priority:** Critical

**Related User Stories:** Story 1, Story 4

**Acceptance Criteria:**
- Query template: Find all `span.set_attribute()` calls via AST search
- Extract attribute key (first argument), value source (second argument), and context (file, line, function)
- Query template: Find span naming patterns via `start_span()` calls
- Query template: Find event structures via `add_event()` calls
- Detect dynamic attributes (iteration patterns like `for key, value: set_attribute()`)

---

### FR-009: Machine-Readable Output Generation

**Description:** The system shall export extraction results as structured YAML or JSON with complete attribute metadata.

**Priority:** High

**Related User Stories:** Story 4

**Acceptance Criteria:**
- Output format includes: attribute key, value source, type (variable/literal/dynamic), file, line, function
- Support YAML export for human-readable review
- Support JSON export for programmatic consumption
- Include example values where available
- Generate ingestion service mapping code templates

---

### FR-010: Partition Lifecycle Management (CRUD)

**Description:** The system shall support create, read, update, and delete operations for partitions with proper cleanup and archival.

**Priority:** High

**Related User Stories:** Story 2

**Acceptance Criteria:**
- **Create**: Detect new partition in config → create directories → initialize tables → trigger full build
- **Read**: Dynamic discovery of existing partitions from config
- **Update (Add Repo)**: Incremental index of new repository across all 3 indexes
- **Update (Remove Repo)**: Atomic deletion of all chunks/nodes/symbols for that repository
- **Delete (Soft)**: Archive partition data to `.archive/{partition}_{timestamp}/` for rollback
- **Delete (Hard)**: Permanent removal of index directories and tables (optional)
- **Orphaned Data Detection**: Warn at startup if index data exists without corresponding config entry
- **Config Validation**: Check valid paths, no duplicate repos, valid partition names on load

---

## 4.1 Requirements by Category

### Multi-Repo Indexing
- FR-001: Multi-Repository Indexing
- FR-002: Partition-Based Index Organization
- FR-003: Repository State Tracking
- FR-004: Incremental Per-Repository Updates
- FR-007: Git Repository Synchronization

### Query & Search
- FR-005: Cross-Repository Query Filtering
- FR-006: Configurable Cross-Repository Call Graphs

### Workflow & Automation
- FR-008: Semantic Convention Extraction Workflows
- FR-009: Machine-Readable Output Generation

### Operations & Lifecycle
- FR-010: Partition Lifecycle Management (CRUD)

---

## 4.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority |
|-------------|--------------|----------------|----------|
| FR-001 | Story 1, 2, 6 | Goal 3 | Critical |
| FR-002 | Story 2, 6 | Goal 3 | Critical |
| FR-003 | Story 3 | Goal 4 | High |
| FR-004 | Story 3 | Goal 4 | High |
| FR-005 | Story 2, 5 | Goal 3 | Critical |
| FR-006 | Story 6 | Goal 3 | High |
| FR-007 | Story 1, 2, 3 | Goal 3, 4 | High |
| FR-008 | Story 1, 4 | Goal 1, 2 | Critical |
| FR-009 | Story 4 | Goal 2 | High |
| FR-010 | Story 2 | Goal 3 | High |

---

## 4.3 Supporting Documentation

Requirements informed by:
- **Multi-Repo Code Intelligence Design Document**: Section 3.1 (Functional Requirements) provides detailed specifications for FR-1 through FR-10

See `supporting-docs/INDEX.md` for complete analysis.

---

## 5. Non-Functional Requirements

NFRs define quality attributes and system constraints.

---

### 5.1 Performance

**NFR-P1: Query Latency - Primary Partition**
- **Requirement:** 95th percentile query latency < 50ms for primary partition
- **Measurement:** Monitor p95 latency via `pos_search_project()` with `filters={"partition": "primary"}`
- **Rationale:** Primary partition is for user's own code, must be fast for interactive development

**NFR-P2: Query Latency - Instrumentors Partition**
- **Requirement:** 95th percentile query latency < 200ms for instrumentors partition
- **Measurement:** Monitor p95 latency via `pos_search_project()` with `filters={"partition": "instrumentors"}`
- **Rationale:** Instrumentors partition is larger (324K chunks), acceptable tradeoff for batch analysis workflows

**NFR-P3: Extraction Workflow Performance**
- **Requirement:** Complete instrumentor analysis workflow in < 15 minutes per instrumentor
- **Measurement:** Time from workflow start to YAML/JSON output generation
- **Target:** 12x improvement over manual analysis (3 hours → 15 minutes)

**NFR-P4: Incremental Update Performance**
- **Requirement:** Incremental per-repository update in < 5 seconds for typical changes (< 10 files)
- **Measurement:** Time from Git pull detection to index update completion
- **Rationale:** Enables near-real-time re-analysis when instrumentors update

**NFR-P5: Cold Start Index Build**
- **Requirement:** Index 270 instrumentors (324K chunks) in < 10 minutes (cold start, parallel)
- **Measurement:** Time from empty index to all repositories indexed
- **Rationale:** Reasonable one-time setup cost for comprehensive instrumentor coverage

---

### 5.2 Storage

**NFR-ST1: Total Disk Usage**
- **Requirement:** Total disk usage < 3GB for all partitions (primary + instrumentors + health check overhead)
- **Measurement:** Sum of index directory sizes (Semantic LanceDB + AST/Graph DuckDB)
- **Breakdown:**
  - Primary partition: < 500MB (praxis-os + python-sdk)
  - Instrumentors partition: < 2GB (270 instrumentors)
  - Overhead: < 500MB (health checks, logs, archives)

**NFR-ST2: Incremental Storage**
- **Requirement:** Incremental indexing only stores changed chunks, not full repo re-index
- **Measurement:** Compare disk usage before/after incremental update (should be proportional to changed files)
- **Rationale:** Efficient storage for long-term maintenance

**NFR-ST3: Archive Storage (Soft Delete)**
- **Requirement:** Soft delete archives use < 10% of active index size
- **Measurement:** Size of `.archive/` directory relative to active indexes
- **Rationale:** Rollback capability without excessive disk usage

---

### 5.3 Maintainability

**NFR-M1: Query Template Reusability**
- **Requirement:** Extraction workflows use parameterized query templates, not hardcoded per-instrumentor logic
- **Measurement:** Count of unique query templates vs. number of instrumentors analyzed (target: < 10 templates for 270 instrumentors)
- **Rationale:** Reduces maintenance burden as instrumentors evolve

**NFR-M2: Version-Controlled Extraction Scripts**
- **Requirement:** All extraction workflows stored in version control with change history
- **Measurement:** Git commit history for workflow scripts
- **Rationale:** Reproducibility and auditability of analysis process

**NFR-M3: Output Format Documentation**
- **Requirement:** YAML/JSON output schema documented with examples
- **Measurement:** Schema documentation exists and includes example outputs
- **Rationale:** Enables ingestion service integration without guesswork

**NFR-M4: Configuration-Driven Architecture**
- **Requirement:** Zero hardcoded partition names or repository paths in code
- **Measurement:** Code review confirms all partitions/repos loaded dynamically from `mcp.yaml`
- **Rationale:** Enables adding/removing partitions without code changes

---

### 5.4 Reliability

**NFR-R1: Graceful Parse Error Handling**
- **Requirement:** Parse failures for exotic languages do not block indexing of other files
- **Measurement:** Log parse errors, skip file, continue with repository indexing
- **Success:** No index build failures due to single unparseable file

**NFR-R2: Per-Repository Health Checks**
- **Requirement:** Health check system reports status per repository with actionable error messages
- **Measurement:** `pos_workflow(action="get_health")` returns detailed status including per-repo health
- **Rationale:** Enables targeted debugging of indexing issues

**NFR-R3: Rollback Capability**
- **Requirement:** Soft delete enables rollback to previous partition state if new extraction fails validation
- **Measurement:** Successful restore from `.archive/` directory
- **Success:** Rollback completes in < 2 minutes

**NFR-R4: Atomic Updates**
- **Requirement:** Repository index updates are atomic (all-or-nothing) across all 3 indexes (Semantic, AST, Graph)
- **Measurement:** Failed update does not leave partial data in any index
- **Rationale:** Prevents inconsistent state between indexes

---

### 5.5 Scalability

**NFR-SC1: Chunk Scale Capacity**
- **Requirement:** Support 437K chunks (primary 113K + instrumentors 324K) with single-table architecture
- **Current:** 87% of 500K chunk threshold
- **Future-Proof:** Nested partitioning strategy defined for > 500K chunks

**NFR-SC2: Provider Extensibility**
- **Requirement:** Add new instrumentor provider without code changes, only config updates
- **Measurement:** Add 5th provider (e.g., new instrumentor vendor) by only editing `mcp.yaml`
- **Rationale:** Supports evolving instrumentor ecosystem

**NFR-SC3: Concurrent Query Support**
- **Requirement:** Support multiple concurrent queries without significant latency degradation
- **Measurement:** p95 latency increase < 50% with 10 concurrent queries vs. single query
- **Rationale:** Enables batch analysis workflows

---

### 5.6 Operability

**NFR-O1: Startup Validation**
- **Requirement:** Validate config on startup, detect orphaned data, report actionable errors
- **Measurement:** Startup completes with warning/error log if config issues detected
- **Success:** Zero silent failures, all errors have remediation guidance

**NFR-O2: Partition Lifecycle Observability**
- **Requirement:** All partition CRUD operations logged with timestamps and outcomes
- **Measurement:** Audit log includes create/update/delete events with success/failure status
- **Rationale:** Enables debugging and compliance

**NFR-O3: Cascading Health Check Integration**
- **Requirement:** Multi-repo indexes integrate with Cascading Health Check Architecture
- **Measurement:** 4-level fractal health check output (CodeIndex → Partition → Index Type → Sub-components)
- **Rationale:** Consistent operability across prAxIs OS

**NFR-O4: Config Validation**
- **Requirement:** Validate `mcp.yaml` config on load, reject invalid entries with specific error messages
- **Checks:** Valid paths, no duplicate repos, valid partition names, valid URL formats
- **Rationale:** Prevents runtime errors from config typos

---

## 5.7 Supporting Documentation

NFRs informed by:
- **Multi-Repo Code Intelligence Design Document**: Section 3.2 (Non-Functional Requirements) provides detailed performance, storage, maintainability, and reliability targets

See `supporting-docs/INDEX.md` for complete analysis.

---

## 6. Out of Scope

Explicitly defines what is NOT included. Items may be considered for future phases.

### Explicitly Excluded

---

#### Features

**Not Included in This Release:**

1. **Remote API-Based Indexing (GitHub API, GitLab API)**
   - **Reason:** Requires network calls, API rate limits, authentication complexity. MVP uses local Git clones only.
   - **Future Consideration:** Phase 2 could add optional API-based indexing for organizations without local clone access.

2. **Language-Specific Analysis Beyond Tree-sitter Capabilities**
   - **Reason:** Tree-sitter provides language-agnostic AST parsing. Deep semantic analysis (type inference, data flow) requires language-specific tooling.
   - **Future Consideration:** Integrate with language servers (LSP) for advanced analysis if needed.

3. **Real-Time Repository Sync**
   - **Reason:** Real-time file watching and incremental sync adds complexity. MVP uses batch/cron-based sync.
   - **Future Consideration:** File watcher integration for near-real-time updates in active development scenarios.

4. **Cross-Language Call Graphs**
   - **Reason:** Python-only call graphs for MVP. Cross-language edges (Python ↔ TypeScript) require polyglot analysis.
   - **Future Consideration:** Add cross-language support when JavaScript/TypeScript instrumentors are indexed.

5. **GUI for Extraction Workflows**
   - **Reason:** MVP uses programmatic workflows (`pos_search_project()` + Python scripts). GUI adds development time without core value.
   - **Future Consideration:** Web UI or CLI tool for non-developers to run extractions.

6. **Automatic Ingestion Service Code Generation**
   - **Reason:** MVP exports YAML/JSON output. Code generation (Python mapping templates) is manual or scripted separately.
   - **Future Consideration:** Jinja2 templates to auto-generate `traceParse.py` code from extraction output.

---

#### User Types

**Not Supported:**

- **Non-Technical Users**: Extraction workflows require understanding of semantic conventions, span attributes, and Python code. Not designed for end-users without development background.
- **External Contributors**: MVP is for internal HoneyHive development only. No public API or external access to code intelligence.

---

#### Platforms

**Not Supported:**

- **Windows Native Git Paths**: MVP assumes POSIX-style paths (`/Users/josh/...`). Windows support requires path normalization.
  - **Workaround:** Use WSL or Git Bash on Windows
  - **Future:** Add `pathlib` for cross-platform compatibility

- **Non-Unix Shells**: Sync scripts assume Bash-compatible shell. PowerShell not supported.

---

#### Integrations

**Not Included:**

- **CI/CD Pipeline Integration**: No automated extraction on pull request or merge. MVP requires manual trigger.
  - **Future Consideration:** GitHub Actions workflow to re-extract conventions on instrumentor updates

- **Slack/Email Notifications**: No alerting when extraction completes or fails. Logs only.

- **Dashboard/Metrics Visualization**: No visual dashboard for extraction results, query performance, or index health. CLI/programmatic access only.

---

#### Quality Levels Beyond Defined NFRs

**Not Included:**

- **p99 Latency < 50ms**: NFR targets p95 latency. p99 may exceed 200ms for complex queries on large partitions.

- **99.99% Uptime**: No high-availability or failover. Single-instance architecture acceptable for development tool.

- **GDPR/SOC2 Compliance**: Code intelligence is for internal use on public GitHub repos. No PII, no compliance requirements.

---

#### Compliance Standards

**Not Required:**

- **Accessibility (WCAG)**: No GUI, so accessibility standards do not apply.
- **GDPR**: No personal data indexed.
- **SOC2**: Internal development tool, not customer-facing service.

---

## 6.1 Future Enhancements

**Potential Phase 2 (After MVP Validation):**
- Real-time file watching for active repositories
- GUI or web interface for extraction workflows
- Cross-language call graphs (Python + JavaScript/TypeScript)
- GitHub Actions integration for automated re-extraction

**Potential Phase 3 (After Scale Validation):**
- Remote API-based indexing (GitHub API, GitLab API)
- Language server protocol (LSP) integration for type inference
- Dashboard for query performance and index health metrics
- Public API for external tools to query code intelligence

**Explicitly Not Planned:**
- Support for non-Git version control (SVN, Mercurial)
- Binary file analysis (compiled code, executables)
- Machine learning for convention prediction (pattern recognition beyond AST)

---

## 6.2 Supporting Documentation

Out-of-scope items from:
- **Multi-Repo Code Intelligence Design Document**: Section 3 (Requirements) explicitly lists "Out of Scope" items including remote API indexing, language-specific analysis, real-time sync, and cross-language call graphs.

See `supporting-docs/INDEX.md` for complete analysis.

---

## 7. Summary

### Requirements Overview

**Business Goals:** 4 goals focused on speed (12x improvement), accuracy (100% coverage), scale (270 instrumentors), and maintainability (incremental updates)

**User Stories:** 6 stories covering instrumentor analysis, multi-provider tracking, update detection, export workflows, cross-repo queries, and multi-project indexing

**Functional Requirements:** 10 requirements (FR-001 through FR-010) covering multi-repo indexing, partitioning, state tracking, incremental updates, query filtering, call graphs, Git sync, extraction workflows, output generation, and lifecycle management

**Non-Functional Requirements:** 22 requirements across 6 categories:
- Performance: 5 requirements (p95 latency, extraction time, incremental updates)
- Storage: 3 requirements (3GB total, incremental efficiency, archive management)
- Maintainability: 4 requirements (query templates, version control, docs, config-driven)
- Reliability: 4 requirements (error handling, health checks, rollback, atomicity)
- Scalability: 3 requirements (437K chunks, provider extensibility, concurrency)
- Operability: 4 requirements (startup validation, audit logs, health checks, config validation)

**Out of Scope:** 17 items across 5 categories (features, user types, platforms, integrations, quality levels)

### Traceability

All functional requirements trace back to user stories and business goals. All NFRs support reliability, performance, and maintainability objectives.

### Next Phase

Phase 2 (Technical Design) will translate these requirements into architecture, components, APIs, and data models.

---

