# Project-Specific RAG System Design

**Date:** 2025-10-21  
**Status:** Design Review  
**Category:** Enhancement  
**Related Systems:** MCP Server, RAG Tools, Standards Management

---

## Executive Summary

This design proposes a **project-specific RAG system** to complement prAxIs OS's existing standards RAG. The system enables AI agents to efficiently discover specific implementation content (code, docs, upstream frameworks) through fast, targeted search, improving token efficiency and discovery speed.

**Key Innovation:** Separation of concerns between behavioral guidance (standards) and information retrieval (project RAG):
- **Standards** → "How should I work?" (patterns, conventions, decisions affecting behavior)
- **Project RAG** → "Where is X?" (fast discovery of specific code/docs/upstream content)

**Core Principles:**
1. **Config-driven** - AI agents can modify configuration without code changes
2. **Self-documenting** - Tools define themselves via MCP protocol
3. **Curated upstream** - Fetch and cache relevant framework docs, not entire libraries
4. **Time-based refresh** - Automatic upstream doc updates with manifest tracking
5. **Single MCP server** - Tool groups, not separate processes
6. **Greater efficiency** - Faster discovery, reduced token usage vs. reading full files

---

## Standards vs. Project RAG: Separation of Concerns

### Standards (Behavioral Guidance)
**Query Tool:** `search_standards()` (existing)  
**Purpose:** How should I behave when working on this project?

**Content:**
- ✅ **Project-specific conventions** - "Always use async/await", "Prefer composition over inheritance"
- ✅ **Testing patterns** - "Test pyramid: 70% unit, 20% integration, 10% e2e"
- ✅ **Code review requirements** - "All PRs need 2 approvals"
- ✅ **Architecture decisions** - "Microservices pattern with event sourcing"
- ✅ **API design patterns** - "RESTful with HATEOAS"
- ✅ **Deployment procedures** - "Blue-green deployment with canary testing"

**Format:** RAG-optimized markdown in `.praxis-os/standards/project/`

**Example Query:**
```python
search_standards("authentication patterns this project")
# → Returns: Convention document explaining JWT pattern, refresh token strategy, etc.
```

---

### Project RAG (Information Retrieval)
**Query Tool:** `search_project()` (new)  
**Purpose:** Where is specific code/docs? Show me implementation examples.

**Content:**
- ✅ **Code files** - Implementations, functions, classes
- ✅ **Documentation** - Architecture docs, feature specs, API docs
- ✅ **Upstream frameworks** - FastAPI, Django, React curated pages
- ✅ **Raw content** - Indexed as-is for fast discovery

**Format:** Indexed code/docs in project directories + `.praxis-os/cache/upstream-docs/`

**Example Query:**
```python
search_project("JWT refresh token implementation")
# → Returns: Specific code chunks from src/api/auth/endpoints.py with line numbers
```

---

### Workflow: Standards First, Then Discovery

**Typical Agent Workflow:**
1. **Understand convention:** `search_standards("auth patterns")` → Learn project uses JWT with refresh tokens
2. **Find implementation:** `search_project("JWT refresh endpoint code")` → Get specific code location
3. **Implement feature:** Apply convention from (1) using patterns from (2)

**Standards inform behavior, Project RAG provides specifics.**

---

## Problem Statement

### The Discovery Gap

**Current State:**
- ✅ `search_standards()` - Excellent for conventions, patterns, behavioral guidance
- ❌ Finding specific code/docs requires reading entire files or guessing locations

**Example Discovery Failures:**
```python
# Scenario: Agent needs to find JWT refresh token implementation
# Current approach:
grep("refresh_token")                  # Finds 50+ matches across files
read_file("src/api/auth/endpoints.py") # Reading 500+ lines, 2000 tokens
read_file("docs/auth.md")              # May or may not have implementation details

# Desired approach:
search_project("JWT refresh token endpoint implementation")
# → Returns: Specific code chunk (50-100 tokens) from endpoints.py:45-67
```

**Token Efficiency Problem:**
- Reading full files wastes context (2000 tokens → 50 tokens needed)
- `grep` results need manual filtering and context reading
- No prioritization by relevance
- Upstream framework docs not available (FastAPI, Django patterns)

**Discovery Speed Problem:**
- Multiple read attempts to find correct file
- No semantic understanding of "where is X"
- Trial-and-error file reading

---

## Solution Architecture

### Two-Index RAG System

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent (Cursor, etc.)                  │
│  Workflow: Standards (how?) → Project RAG (where?)          │
└────────────────────┬────────────────────────────────────────┘
                     │ MCP Protocol
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Single MCP Server (Tool Groups)                │
├─────────────────────────────────────────────────────────────┤
│  Tool Group: RAG                                            │
│  ├─ search_standards()   → Behavioral guidance              │
│  │                         (universal + project patterns)   │
│  └─ search_project()     → Information retrieval (NEW)      │
│                            (code/docs/upstream)             │
│                                                              │
│  Tool Group: Workflow                                       │
│  ├─ start_workflow()                                        │
│  ├─ complete_phase()                                        │
│  └─ ...                                                      │
│                                                              │
│  Tool Group: Config (NEW)                                   │
│  └─ update_project_rag_config()  → AI modifies config       │
└─────────────────────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    RAG Index Layer                          │
├─────────────────────────────────────────────────────────────┤
│  Index 1: Standards (existing, enhanced)                    │
│  ├─ Universal standards (.praxis-os/standards/universal/)    │
│  ├─ Project standards (.praxis-os/standards/project/) ← NEW  │
│  ├─ Content: Conventions, patterns, behavioral guidance     │
│  ├─ Format: RAG-optimized markdown                          │
│  ├─ Strategy: Manual chunking optimization                  │
│  └─ Refresh: Manual (content changes)                       │
│                                                              │
│  Index 2: Project Content (NEW)                             │
│  ├─ Source 1: Project code (src/, lib/, etc.)               │
│  ├─ Source 2: Project docs (docs/, README.md)               │
│  ├─ Source 3: Curated upstream (.praxis-os/cache/)           │
│  ├─ Content: Raw implementations, specific data             │
│  ├─ Format: Indexed as-is (code, markdown, etc.)            │
│  ├─ Strategy: Hierarchical RAG (large codebase)             │
│  └─ Refresh: Code on-demand, upstream time-based            │
└─────────────────────────────────────────────────────────────┘

KEY DISTINCTION:
- Index 1 (Standards): "How should I work on this project?"
- Index 2 (Project): "Where is X? Show me Y implementation."
```

---

## Project-Specific Standards (Enhanced Index 1)

### Creating Project Standards

**When to Create:**
Project-specific behavioral patterns, conventions, and decisions that affect how agents should work on this project.

**Examples:**
- ✅ "This project uses async/await everywhere - never use callbacks"
- ✅ "Testing convention: 70% unit, 20% integration, 10% e2e"
- ✅ "All API endpoints must have OpenAPI documentation"
- ✅ "Authentication uses JWT with 15min access + 7day refresh tokens"
- ✅ "Database migrations use Alembic - never modify existing migrations"

**Format Requirements:**
- **RAG-optimized markdown** - Follow `search_standards("RAG content authoring")`
- **Keywords and query hooks** - Make discoverable via natural language queries
- **TL;DR sections** - Quick reference at top
- **Code examples** - Show don't tell
- **When to use / not use** - Clear guidance
- **Cross-references** - Link to related standards

**Location:** `.praxis-os/standards/project/`

**Discovery:** Via `search_standards()` (existing tool, already indexes project standards)

**Example Standard:**

```markdown
# Authentication Patterns (This Project)

**TL;DR:** JWT access tokens (15min) + refresh tokens (7day). Refresh tokens rotate on use.

**Keywords:** auth, authentication, JWT, refresh token, access token, login, logout, token rotation

---

## 🎯 Purpose

This standard defines how authentication works in this project, so agents implement auth consistently.

**Questions This Answers:**
- How do we handle user authentication?
- What token expiry times do we use?
- How do refresh tokens work?
- Where should tokens be stored (client-side)?

---

## Convention: JWT with Rotating Refresh Tokens

**Pattern:**
1. Login → Returns access token (JWT, 15min) + refresh token (UUID, 7day)
2. Access token in Authorization header for API calls
3. When access token expires → Call `/auth/refresh` with refresh token
4. Refresh endpoint returns NEW access token + NEW refresh token
5. Old refresh token invalidated (one-time use)

**Implementation Requirements:**

When implementing auth endpoints:
- ✅ Access tokens: JWT, 15 min expiry, include user_id + roles
- ✅ Refresh tokens: UUID, 7 day expiry, stored in database
- ✅ Rotate refresh tokens: Issue new one on every refresh, invalidate old
- ✅ httpOnly cookies: Store refresh tokens client-side in httpOnly cookies
- ❌ Never store refresh tokens in localStorage (XSS vulnerability)

**Code Examples:**

Find implementation:
```python
search_project("JWT token generation implementation")
search_project("refresh token endpoint code")
```

**Related Standards:**
- `search_standards("API security patterns")`
- `search_standards("database session management")`

---

## Why This Pattern?

**Security Considerations:**
- Short-lived access tokens limit damage if leaked
- Rotating refresh tokens prevent replay attacks
- httpOnly cookies prevent XSS theft
- Database-backed refresh tokens enable revocation

**Testing Considerations:**
- Mock JWT signing in tests (use fixed secret)
- Test token expiry edge cases
- Test refresh token rotation
- Test concurrent refresh attempts (race condition)

---

**Version:** 1.0  
**Last Updated:** 2025-10-21  
**Author:** Team consensus from security review
```

### Benefits of Project Standards

1. **Behavioral Consistency** - All agents follow same patterns
2. **Knowledge Compounding** - Patterns captured for reuse
3. **RAG Optimized** - Discoverable via natural language queries
4. **Self-Improving** - Standards evolve as project learns

### Standards vs. README

**README.md:** Getting started, installation, overview (for humans)  
**Standards:** Detailed conventions, patterns, rules (for agents)

Both are valuable, different purposes.

---

## Component Design

### 1. New MCP Tool: `search_project()`

**Tool Signature:**
```python
@server.call_tool()
async def search_project(
    query: str,
    n_results: int = 5,
    source_filter: str | None = None,      # 'code', 'docs', 'upstream'
    framework_filter: str | None = None,   # 'fastapi', 'django', etc.
    priority_boost: str | None = None      # 'recent', 'frequently_accessed'
) -> dict:
    """
    Semantic search over project-specific knowledge.
    
    Searches code, docs, and curated upstream documentation.
    Use for project-specific questions. For prAxIs OS patterns,
    use search_standards() instead.
    
    For usage patterns, query: search_standards("how to use search_project")
    
    Args:
        query: Natural language question about the project
        n_results: Number of relevant chunks (default 5)
        source_filter: Limit to 'code', 'docs', or 'upstream'
        framework_filter: Limit to specific framework (e.g., 'fastapi')
        priority_boost: Boost recent/frequently accessed files
        
    Returns:
        {
            "results": [
                {
                    "content": "...",
                    "file": "src/auth/middleware.py",
                    "source_type": "code",
                    "framework": None,
                    "relevance_score": 0.92,
                    "lines": "45-67"
                }
            ],
            "total_tokens": 1250,
            "retrieval_method": "hierarchical_rag",
            "query_time_ms": 125
        }
    """
```

**Self-Teaching Pattern:**
- Docstring points to `search_standards("how to use search_project")`
- Usage patterns documented in standards
- MCP schema keeps parameters current

---

### 2. Config-Driven Architecture

**Configuration File:** `.praxis-os/config/project-rag.yaml`

```yaml
# Project RAG Configuration
# AI agents can modify this to improve discovery

version: "1.0"

# ============================================================
# INDEX CONFIGURATION
# ============================================================

indexes:
  project:
    enabled: true
    
    # Project-specific sources
    sources:
      # Documentation (high priority)
      - type: docs
        paths:
          - "docs/"
          - "README.md"
          - "ARCHITECTURE.md"
        priority: 1.0
        recursive: true
        file_patterns: ["*.md", "*.rst"]
        
      # Code (medium priority)
      - type: code
        paths:
          - "src/"
          - "lib/"
        priority: 0.8
        recursive: true
        file_patterns: ["*.py", "*.js", "*.ts", "*.go"]
        ignore_patterns:
          - "*/tests/*"
          - "*/migrations/*"
          - "*/__pycache__/*"
        
      # Curated upstream docs (framework-specific)
      - type: upstream
        framework: fastapi
        priority: 0.9
        refresh_days: 7
        pages:
          - title: "Dependency Injection"
            url: "https://fastapi.tiangolo.com/tutorial/dependencies/"
          - title: "Request Validation"
            url: "https://fastapi.tiangolo.com/tutorial/body/"
          - title: "Background Tasks"
            url: "https://fastapi.tiangolo.com/tutorial/background-tasks/"
          - title: "Testing"
            url: "https://fastapi.tiangolo.com/tutorial/testing/"

# ============================================================
# RETRIEVAL STRATEGY
# ============================================================

retrieval:
  # Primary strategy
  strategy: hierarchical_rag  # Options: vector, hierarchical_rag, hybrid
  
  # Chunking
  chunk_size: 500
  chunk_overlap: 50
  
  # Hierarchical RAG (for large codebases)
  hierarchical:
    enabled: true
    summary_level: "file"  # file, directory, or module
    top_k_summaries: 10
    expand_top_k: 3
  
  # Hybrid search
  hybrid:
    vector_weight: 0.7
    bm25_weight: 0.3
  
  # Reranking
  reranking:
    enabled: true
    model: "cross-encoder/ms-marco-MiniLM-L-6-v2"

# ============================================================
# UPSTREAM DOCS MANAGEMENT
# ============================================================

upstream:
  # Cache location (gitignored)
  cache_dir: ".praxis-os/cache/upstream-docs"
  
  # Refresh policy
  refresh_policy:
    default_interval_days: 7
    check_on_startup: true
    
  # Download settings
  download:
    timeout_seconds: 30
    retry_attempts: 3
    user_agent: "Agent-OS-Enhanced/1.0"
    
  # Manifest tracking
  manifest_file: ".manifest.json"

# ============================================================
# PERFORMANCE
# ============================================================

performance:
  # Index building
  build_on_startup: false  # Only if stale
  incremental_updates: true
  
  # Query limits
  max_results: 20
  query_timeout_ms: 5000
  
  # Caching
  query_cache_enabled: true
  query_cache_ttl_seconds: 300

# ============================================================
# AI SELF-IMPROVEMENT
# ============================================================

self_improvement:
  # Allow AI to modify config
  ai_modifiable: true
  
  # Backup before AI changes
  backup_on_modify: true
  backup_dir: ".praxis-os/config/backups"
  
  # Validation
  validate_on_modify: true
  
  # Audit trail
  log_changes: true
  change_log_file: ".praxis-os/logs/project-rag-changes.log"
```

**Hot Reload:**
- Watch `.praxis-os/config/project-rag.yaml` for changes
- Reload configuration without restarting MCP server
- Validate before applying
- Log all config changes

---

### 3. Curated Upstream Documentation System

#### Architecture: Download → Cache → Index → Refresh

**Directory Structure:**
```
.praxis-os/
├── cache/
│   ├── upstream-docs/          # NOT committed (in .gitignore)
│   │   ├── fastapi/
│   │   │   ├── .manifest.json
│   │   │   ├── dependency-injection.md
│   │   │   ├── request-validation.md
│   │   │   └── background-tasks.md
│   │   ├── django/
│   │   │   └── ...
│   │   └── react/
│   │       └── ...
│   └── ...
├── config/
│   └── project-rag.yaml        # Defines what to fetch (committed)
```

**Manifest File:** `.praxis-os/cache/upstream-docs/fastapi/.manifest.json`
```json
{
  "framework": "fastapi",
  "version": "0.104.0",
  "last_synced": "2025-10-21T14:30:00Z",
  "sync_duration_seconds": 12.4,
  "next_refresh_after": "2025-10-28T14:30:00Z",
  "pages_synced": 4,
  "pages": [
    {
      "title": "Dependency Injection",
      "url": "https://fastapi.tiangolo.com/tutorial/dependencies/",
      "local_path": "dependency-injection.md",
      "downloaded_at": "2025-10-21T14:30:05Z",
      "size_bytes": 45234,
      "checksum": "sha256:abc123...",
      "http_etag": "W/\"abc123\""
    }
  ]
}
```

#### Time-Based Refresh Strategy

**Background Thread:**
```python
class UpstreamDocRefresher:
    """Background thread that checks upstream doc staleness."""
    
    def __init__(self, config: ProjectRagConfig):
        self.config = config
        self.check_interval = 3600  # Check every hour
        
    async def run(self):
        """Main refresh loop."""
        while True:
            await asyncio.sleep(self.check_interval)
            await self.check_and_refresh()
    
    async def check_and_refresh(self):
        """Check all frameworks for stale docs."""
        for framework in self.config.upstream_frameworks:
            manifest = self.load_manifest(framework)
            
            if self.is_stale(manifest):
                logger.info(f"Refreshing {framework} docs (stale)")
                await self.refresh_framework(framework)
    
    def is_stale(self, manifest: dict) -> bool:
        """Check if docs need refresh based on time or ETag."""
        if not manifest:
            return True
        
        # Time-based check
        last_synced = datetime.fromisoformat(manifest["last_synced"])
        refresh_after = datetime.fromisoformat(manifest["next_refresh_after"])
        
        if datetime.now(timezone.utc) > refresh_after:
            return True
        
        # ETag-based check (if available)
        for page in manifest.get("pages", []):
            if self.has_remote_changed(page):
                return True
        
        return False
    
    async def has_remote_changed(self, page: dict) -> bool:
        """HEAD request to check ETag without downloading."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(page["url"], timeout=5) as resp:
                    remote_etag = resp.headers.get("ETag")
                    local_etag = page.get("http_etag")
                    return remote_etag != local_etag
        except Exception as e:
            logger.warning(f"ETag check failed for {page['url']}: {e}")
            return False  # Assume unchanged on error
```

**Startup Check:**
```python
async def on_mcp_server_start():
    """Check upstream docs on server startup."""
    config = load_project_rag_config()
    
    if config.upstream.refresh_policy.check_on_startup:
        refresher = UpstreamDocRefresher(config)
        await refresher.check_and_refresh()
    
    # Start background refresh thread
    asyncio.create_task(refresher.run())
```

---

### 4. Hierarchical RAG Strategy

**Problem:** Large codebases (10K+ files) make flat vector search slow and noisy.

**Solution:** Two-stage retrieval:

1. **Stage 1: Summary Search** - Find relevant files/modules via summaries
2. **Stage 2: Detail Search** - Expand relevant files for detailed chunks

**Implementation:**
```python
class HierarchicalRAG:
    """Two-stage RAG for large codebases."""
    
    async def search(self, query: str, top_k: int = 5) -> list[Chunk]:
        """Hierarchical search."""
        
        # Stage 1: Search file summaries
        summary_results = await self.summary_index.search(
            query=query,
            top_k=10  # Get more summaries
        )
        
        # Stage 2: Expand top files and search details
        relevant_files = [r.file for r in summary_results[:3]]
        
        detail_results = await self.detail_index.search(
            query=query,
            file_filter=relevant_files,
            top_k=top_k
        )
        
        return detail_results
```

**File Summaries:**
- Generated automatically from code (AST + docstrings + comments)
- Stored in separate summary index
- Small token footprint (100-200 tokens per file)

**When to Use:**
- Codebase > 1000 files: Strongly recommended
- Codebase > 5000 files: Required for performance
- Codebase < 500 files: Flat vector search sufficient

---

### 5. AI Self-Improvement Tool

**New Tool:** `update_project_rag_config()`

```python
@server.call_tool()
async def update_project_rag_config(
    updates: dict,
    reason: str,
    create_backup: bool = True
) -> dict:
    """
    Update project RAG configuration to improve discovery.
    
    AI agents can call this to:
    - Add new upstream documentation pages
    - Adjust source priorities
    - Include/exclude code directories
    - Modify refresh intervals
    
    Changes are validated, backed up, and logged.
    
    Args:
        updates: Dict of config updates (deep merge)
        reason: Why this change improves discovery
        create_backup: Backup current config before updating
        
    Returns:
        {
            "success": true,
            "backup_path": ".praxis-os/config/backups/project-rag-2025-10-21-140530.yaml",
            "changes_applied": [...],
            "validation_warnings": [...]
        }
    
    Example:
        update_project_rag_config(
            updates={
                "indexes": {
                    "project": {
                        "sources": {
                            "upstream": {
                                "fastapi": {
                                    "pages": [
                                        {
                                            "title": "WebSockets",
                                            "url": "https://fastapi.tiangolo.com/advanced/websockets/"
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            reason="Project uses WebSockets extensively, need FastAPI WebSocket patterns"
        )
    """
```

**Self-Improvement Workflow:**
1. AI encounters discovery gap: "How do WebSockets work in FastAPI?"
2. AI realizes upstream docs don't have WebSocket page
3. AI calls `update_project_rag_config()` to add it
4. Config updated, upstream docs refreshed
5. AI retries query with new knowledge available

---

## Tool Documentation Philosophy

### Two-Tier Documentation System

**Tier 1: Self-Documenting Code (MCP Schema)**
- Tool signature with type hints
- Docstring with parameters, returns, examples
- Auto-generated MCP schema via `tools/list`
- IDE autocomplete integration
- **Always current** - code changes → schema updates

**Tier 2: Usage Patterns (Standards)**
- How to use effectively
- When to use vs. alternatives
- Multi-query strategies
- Anti-patterns and common mistakes
- Queryable via `search_standards("how to use search_project")`

### Applied to `search_project()`

**In Code (`mcp_server/tools/rag_tools.py`):**
```python
# Complete docstring with examples and pointer to standards
async def search_project(query: str, ...) -> dict:
    """
    Semantic search over project-specific knowledge.
    ...
    For usage patterns, query: search_standards("how to use search_project")
    """
```

**In Standards (`.praxis-os/standards/project/search-project-usage.md`):**
```markdown
# search_project() Usage Patterns

## When to Use
✅ Project architecture questions
✅ Framework integration patterns
❌ prAxIs OS workflows (use search_standards)

## Query Patterns
### Architecture Discovery
search_project("how does authentication work")

### Framework-Specific
search_project("FastAPI dependency injection", framework_filter="fastapi")
...
```

**Benefits:**
- ✅ No static catalogs (no drift)
- ✅ Schema always accurate (generated from code)
- ✅ Usage patterns evolve independently
- ✅ Self-teaching loop (tool → query standards → learn pattern)

---

## Implementation Plan

### Phase 1: Foundation (Week 1)

**1.1: Configuration System**
- [ ] Create `.praxis-os/config/project-rag.yaml` schema
- [ ] Implement YAML loader with validation
- [ ] Add hot reload with file watching
- [ ] Add `.praxis-os/config/backups/` to `.gitignore`

**1.2: Index Infrastructure**
- [ ] Create project index builder (separate from standards index)
- [ ] Implement code source indexing (with ignore patterns)
- [ ] Implement docs source indexing
- [ ] Add source type tagging (code/docs/upstream)

**1.3: MCP Tool**
- [ ] Implement `search_project()` tool
- [ ] Add to RAG tool group
- [ ] Write comprehensive docstring
- [ ] Test with sample project

**Validation Gate:**
- [ ] Config loads and validates correctly
- [ ] Project index builds successfully
- [ ] `search_project()` returns relevant results
- [ ] MCP schema exposes tool correctly

---

### Phase 2: Upstream Docs (Week 2)

**2.1: Curated Upstream System**
- [ ] Implement upstream doc downloader
- [ ] Create manifest file format
- [ ] Add `.praxis-os/cache/` to `.gitignore`
- [ ] Implement HTTP download with retries

**2.2: Time-Based Refresh**
- [ ] Create `UpstreamDocRefresher` background thread
- [ ] Implement staleness detection (time-based + ETag)
- [ ] Add startup check
- [ ] Add manual refresh command

**2.3: Upstream Index Integration**
- [ ] Index upstream docs with framework tagging
- [ ] Add framework_filter to `search_project()`
- [ ] Test with FastAPI, Django, React samples

**Validation Gate:**
- [ ] Upstream docs download and cache correctly
- [ ] Manifest tracks state accurately
- [ ] Background refresh works without blocking
- [ ] Framework filtering returns correct results

---

### Phase 3: Advanced Features (Week 3)

**3.1: Hierarchical RAG**
- [ ] Implement file summary generation (AST-based)
- [ ] Create two-stage search (summary → detail)
- [ ] Add configuration toggle
- [ ] Benchmark performance vs. flat search

**3.2: AI Self-Improvement**
- [ ] Implement `update_project_rag_config()` tool
- [ ] Add validation and backup logic
- [ ] Add change logging and audit trail
- [ ] Test self-improvement workflow

**3.3: Usage Standards**
- [ ] Write `.praxis-os/standards/project/search-project-usage.md`
- [ ] Document query patterns and examples
- [ ] Add to orientation bootstrap queries (optional)
- [ ] Cross-reference with tool docstring

**Validation Gate:**
- [ ] Hierarchical RAG improves performance on large codebase
- [ ] AI can modify config successfully
- [ ] Config changes are logged and reversible
- [ ] Usage standards are queryable and helpful

---

### Phase 4: Testing & Documentation (Week 4)

**4.1: Testing**
- [ ] Unit tests for config loading/validation
- [ ] Integration tests for search_project()
- [ ] End-to-end tests for upstream refresh
- [ ] Performance benchmarks (flat vs. hierarchical)

**4.2: Documentation**
- [ ] Update `docs/content/reference/mcp-tools.md`
- [ ] Create tutorial: "Adding Project-Specific Knowledge"
- [ ] Update installation guide with config setup
- [ ] Add troubleshooting guide

**4.3: Migration Guide**
- [ ] Document how to add to existing projects
- [ ] Provide example configs for common stacks
- [ ] Create upstream page curations for popular frameworks

**Validation Gate:**
- [ ] All tests passing (≥95% coverage)
- [ ] Documentation complete and reviewed
- [ ] Example configs validated
- [ ] Ready for production use

---

## Open Questions & Future Considerations

### 1. **Hybrid Search Strategy**
**Question:** Should we use vector + BM25 hybrid search by default?

**Tradeoffs:**
- **Vector only:** Semantic but misses exact matches
- **BM25 + Vector:** Better exact match recall but slower
- **Adaptive:** Choose based on query characteristics

**Recommendation:** Start with vector-only, add hybrid as optional config

---

### 2. **Index Update Frequency**
**Question:** When should the project code index rebuild?

**Options:**
- **On file save:** Real-time but expensive
- **On-demand:** Manual trigger only
- **Periodic:** Every N minutes
- **Git hook:** On commit/checkout

**Recommendation:** On-demand with periodic fallback (5 min)

---

### 3. **Upstream Doc Sources**
**Question:** Should we support multiple upstream doc sources?

**Examples:**
- Official docs (FastAPI, Django)
- GitHub README/Wiki
- Stack Overflow curated Q&A
- Blog posts (specific URLs)

**Recommendation:** Start with official docs only, expand based on demand

---

### 4. **Cross-Project Learning**
**Question:** Should projects share upstream doc caches?

**Scenario:**
- Project A uses FastAPI, downloads docs
- Project B uses FastAPI, could reuse docs

**Options:**
- **Per-project cache:** Isolated, simple
- **Global cache:** Shared across projects, complex
- **Hybrid:** Fallback to global if exists

**Recommendation:** Per-project for simplicity, revisit if cache size becomes issue

---

### 5. **Hierarchical RAG Threshold**
**Question:** When should hierarchical RAG be automatically enabled?

**Options:**
- **Never automatic:** User configures explicitly
- **File count threshold:** Auto-enable at 1000+ files
- **Query performance:** Enable if queries > 1s
- **Smart detection:** Measure and adapt

**Recommendation:** File count threshold with config override

---

### 6. **Query Routing Intelligence**
**Question:** Should we build a tool router to suggest which tool to use?

**Example:**
- Query: "how do workflows work" → Suggest `search_standards()`
- Query: "how does auth work" → Suggest `search_project()`

**Tradeoffs:**
- **Pros:** Helps agents choose correct tool
- **Cons:** Adds complexity, may be unnecessary (tool discovery already works)

**Recommendation:** Document in usage standards, no automatic routing (agents learn patterns)

---

### 7. **Unified Search Tool**
**Question:** Should we add `search_unified()` that searches both indexes?

**Use Case:**
- "How to implement dependency injection?" 
- Could match: FastAPI patterns (upstream) + project examples (code) + DI principles (standards)

**Tradeoffs:**
- **Pros:** Single query for comprehensive results
- **Cons:** Harder to prioritize, may return noisy results

**Recommendation:** Add as optional, encourage agents to query multiple tools explicitly

---

## Success Metrics

### Primary Goal: Efficiency in Discoverability

**What We're Measuring:** How quickly and efficiently agents can find specific implementations, not behavioral guidance (that's standards).

### Token Efficiency (Information Retrieval)
- **Baseline:** Current average for finding code: `grep` + 2-3 `read_file()` = ~6000 tokens
- **Target:** Average `search_project()` result: ~500 tokens
- **Goal:** 90% reduction in tokens used for discovery
- **Rationale:** Semantic search returns relevant chunks, not entire files

### Discovery Accuracy
- **Baseline:** Agent finds correct code location in 60% of first attempts (file guessing + grep)
- **Target:** Agent finds correct code/docs in 90% of first attempts (semantic search)
- **Goal:** 50% improvement in first-attempt accuracy
- **Rationale:** Semantic understanding of "where is X" vs. keyword matching

### Time to Discovery
- **Baseline:** Average time to find implementation: 3-5 queries (`grep`, multiple `read_file()`)
- **Target:** Average time to find implementation: 1-2 queries (`search_project()` + `read_file()` for context)
- **Goal:** 60% reduction in discovery steps
- **Rationale:** Direct semantic search vs. trial-and-error file reading

### Upstream Doc Utility
- **Metric:** % of queries using `framework_filter` parameter
- **Target:** 30% of project queries leverage upstream docs
- **Goal:** Demonstrates value of curated framework knowledge
- **Rationale:** Agents use FastAPI/Django patterns from cache, not generic searches

### Behavioral Consistency (Standards)
- **Metric:** % of implementations following project conventions (measured via code review)
- **Baseline:** 70% consistency (patterns not documented)
- **Target:** 95% consistency (patterns in project standards)
- **Goal:** Standards enable consistent behavior
- **Rationale:** RAG-optimized project standards guide agent behavior

---

## Risk Assessment

### Risk 1: Index Staleness (Medium)
**Problem:** Code changes but index not updated, stale results

**Mitigation:**
- On-demand rebuild with clear "Rebuild Index" command
- Periodic background updates
- Git hook integration for automatic rebuild

### Risk 2: Upstream Doc Drift (Low)
**Problem:** Upstream docs change, cached version outdated

**Mitigation:**
- Time-based refresh (7 days default)
- ETag checking for efficiency
- Manual refresh command

### Risk 3: Config Complexity (Medium)
**Problem:** YAML config intimidating for users

**Mitigation:**
- Sensible defaults (works out-of-box)
- AI can modify config (self-improving)
- Example configs for common stacks
- Validation with helpful error messages

### Risk 4: Query Confusion (Low)
**Problem:** Agents don't know when to use `search_project()` vs. `search_standards()`

**Mitigation:**
- Clear docstrings with guidance
- Usage standards with examples
- Self-teaching pattern (tool points to standards)
- Orientation includes tool discovery

### Risk 5: Performance on Large Codebases (Medium)
**Problem:** 10K+ files → slow index building, slow queries

**Mitigation:**
- Hierarchical RAG for large codebases
- Incremental index updates
- Query caching
- Benchmark and optimize early

---

## Comparison to Alternatives

### Alternative 1: Static Project Documentation
**Approach:** Manually write project docs, agents read files

**Pros:**
- No infrastructure needed
- Complete control over content

**Cons:**
- Documentation drifts from code
- Requires manual updates
- Full file reads waste tokens
- No semantic search

**Verdict:** Project RAG superior for dynamic discovery

---

### Alternative 2: Code Search Tools (grep, ripgrep)
**Approach:** Use existing search tools

**Pros:**
- Fast exact match
- Already available
- No setup

**Cons:**
- No semantic understanding
- Returns too many results (needs filtering)
- No upstream framework knowledge
- No prioritization

**Verdict:** Complement (not replace) with semantic RAG

---

### Alternative 3: LLM Code Understanding
**Approach:** Load entire codebase into context

**Pros:**
- No infrastructure
- LLM understands full context

**Cons:**
- Context limits (even 1M tokens insufficient for large codebases)
- Expensive (token costs)
- Slow (processing time)
- No upstream knowledge

**Verdict:** RAG enables targeted context loading

---

### Alternative 4: Separate MCP Server
**Approach:** New MCP server just for project RAG

**Pros:**
- Clean separation
- Independent versioning

**Cons:**
- More complexity (two processes)
- Duplicate infrastructure (embeddings, caching)
- More ports/connections to manage

**Verdict:** Single server with tool groups simpler and sufficient

---

## Conclusion

The project-specific RAG system addresses a critical discovery gap in prAxIs OS. By complementing universal standards with project-specific knowledge, AI agents can efficiently discover:

1. **Project architecture and patterns**
2. **Codebase structure and examples**
3. **Framework integration patterns**
4. **Curated upstream documentation**

**Key Innovations:**
- Config-driven (AI can improve)
- Self-documenting (MCP protocol)
- Curated upstream (not full dumps)
- Time-based refresh (automatic updates)
- Single MCP server (simplicity)

**Next Steps:**
1. Review and refine design
2. Create formal specification (use `spec_creation_v1` workflow)
3. Implement Phase 1 (foundation)
4. Test with real projects
5. Iterate based on feedback

---

## Appendices

### Appendix A: Example Configurations

#### Small Project (< 500 files)
```yaml
indexes:
  project:
    sources:
      - type: docs
        paths: ["docs/", "README.md"]
      - type: code
        paths: ["src/"]

retrieval:
  strategy: vector  # Flat search sufficient
  hierarchical:
    enabled: false
```

#### Medium Project (500-2000 files)
```yaml
indexes:
  project:
    sources:
      - type: docs
        paths: ["docs/", "README.md"]
      - type: code
        paths: ["src/", "lib/"]
      - type: upstream
        framework: fastapi
        pages: [...]  # 5-10 key pages

retrieval:
  strategy: vector
  hierarchical:
    enabled: true  # Optional at this size
```

#### Large Project (2000+ files)
```yaml
indexes:
  project:
    sources:
      - type: docs
        paths: ["docs/"]
      - type: code
        paths: ["src/", "lib/", "services/"]
        ignore_patterns:
          - "*/tests/*"
          - "*/migrations/*"
      - type: upstream
        framework: django
        pages: [...]  # 10-15 key pages

retrieval:
  strategy: hierarchical_rag  # Required for performance
  hierarchical:
    enabled: true
    summary_level: "module"
    top_k_summaries: 15
```

---

### Appendix B: Upstream Doc Curations

#### FastAPI (Recommended Pages)
```yaml
- title: "First Steps"
  url: "https://fastapi.tiangolo.com/tutorial/first-steps/"
- title: "Path Parameters"
  url: "https://fastapi.tiangolo.com/tutorial/path-params/"
- title: "Request Body"
  url: "https://fastapi.tiangolo.com/tutorial/body/"
- title: "Dependency Injection"
  url: "https://fastapi.tiangolo.com/tutorial/dependencies/"
- title: "Security - OAuth2"
  url: "https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/"
- title: "Background Tasks"
  url: "https://fastapi.tiangolo.com/tutorial/background-tasks/"
- title: "Testing"
  url: "https://fastapi.tiangolo.com/tutorial/testing/"
- title: "Database - SQLAlchemy"
  url: "https://fastapi.tiangolo.com/tutorial/sql-databases/"
```

#### Django (Recommended Pages)
```yaml
- title: "URL Dispatcher"
  url: "https://docs.djangoproject.com/en/stable/topics/http/urls/"
- title: "Views"
  url: "https://docs.djangoproject.com/en/stable/topics/http/views/"
- title: "Models"
  url: "https://docs.djangoproject.com/en/stable/topics/db/models/"
- title: "QuerySets"
  url: "https://docs.djangoproject.com/en/stable/topics/db/queries/"
- title: "Forms"
  url: "https://docs.djangoproject.com/en/stable/topics/forms/"
- title: "Authentication"
  url: "https://docs.djangoproject.com/en/stable/topics/auth/"
- title: "Testing"
  url: "https://docs.djangoproject.com/en/stable/topics/testing/"
```

#### React (Recommended Pages)
```yaml
- title: "Components and Props"
  url: "https://react.dev/learn/components"
- title: "State Management"
  url: "https://react.dev/learn/state-management"
- title: "Hooks - useState"
  url: "https://react.dev/reference/react/useState"
- title: "Hooks - useEffect"
  url: "https://react.dev/reference/react/useEffect"
- title: "Context"
  url: "https://react.dev/learn/passing-data-deeply-with-context"
- title: "React Router"
  url: "https://reactrouter.com/en/main/start/tutorial"
```

---

### Appendix C: Gitignore Requirements

**Add to `.gitignore`:**
```gitignore
# Project RAG caches (rebuildable)
.praxis-os/cache/upstream-docs/
.praxis-os/cache/indexes/

# Config backups (local)
.praxis-os/config/backups/

# Change logs (local)
.praxis-os/logs/project-rag-changes.log
```

**Commit to Git:**
```
# Config (defines what to fetch)
.praxis-os/config/project-rag.yaml

# Usage standards (how to use)
.praxis-os/standards/project/search-project-usage.md
```

---

**End of Design Document**

**Status:** Ready for review and refinement  
**Next Action:** Review with team, create formal spec, or begin Phase 1 implementation

