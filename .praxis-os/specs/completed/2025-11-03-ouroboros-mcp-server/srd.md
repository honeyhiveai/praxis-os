# Software Requirements Document

**Project:** Ouroboros MCP Server  
**Date:** 2025-11-03  
**Priority:** Critical  
**Category:** Greenfield Feature

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for Ouroboros, a clean MCP server architecture built from the ground up with behavioral engineering as the primary mission. Ouroboros replaces the current `mcp_server/` implementation to enable praxis (continuous improvement through knowledge compounding and behavioral reinforcement).

### 1.2 Scope
This feature will deliver a production-ready MCP server that systematically improves AI agent performance through query gamification, knowledge compounding (standards + specs), and adversarial design enforcement. The server will support all current MCP tools (search, workflow, browser, filesystem) with clean subsystem boundaries and config-driven extensibility.

**Included:**
- Complete MCP server with behavioral engineering middleware
- Unified config system (Pydantic v2)
- Multi-index RAG (standards, code semantic + graph, AST)
- Workflow engine with evidence validation
- Browser automation
- Tool auto-discovery and registration

**Excluded:**
- Changes to MCP protocol
- Changes to index file formats (LanceDB/DuckDB compatibility preserved)
- Changes to content formats (markdown standards/specs)
- Migration of legacy `mcp_server/` code (greenfield rewrite)

---

## 2. Business Goals

### Goal 1: Enable Praxis - Session-Over-Session Improvement

**Objective:** Enable measurable AI agent improvement across sessions through systematic knowledge compounding and behavioral reinforcement, transforming AI from "stateless tool" to "project expert that learns."

**Success Metrics:**
- **First-time correctness:** 40% (Session 1) → 80%+ (Session 50)
- **Query frequency:** 1-2 per task (current) → 5-10 per task (target)
- **Cross-session consistency:** Same task produces same quality code across sessions
- **Knowledge growth:** 0 project-specific standards → 10+ standards created through natural work
- **Spec utilization:** Specs successfully referenced in later sessions (3+ verified instances)

**Business Impact:**
- **For AI agents:** Transform from "coder" to "project expert" through continuous learning
- **For humans:** Trust AI work quality without constant verification, enabling true pair programming
- **For the mission:** Proof that praxis works (theory + practice → continuous improvement)
- **Economic value:** Session 50 uses 67% fewer messages than Session 1 (measured in current implementation), reducing costs and increasing velocity

**Measurement:**
```bash
# First-time correctness improvement over time
grep -E "correct first time" .praxis-os/logs/session-*.log | \
  awk '{print $1, $5}' | sort

# Standards growth
ls .praxis-os/standards/development/*.md | wc -l

# Query frequency (should increase over time)
grep "search_standards\|pos_search_project" .praxis-os/logs/session-*.log | wc -l
```

---

### Goal 2: Enforce Behavioral Patterns Through Architecture

**Objective:** Make "query-first" behavior structurally easier than shortcuts, preventing AI behavioral drift through systematic reinforcement at every decision point.

**Success Metrics:**
- **Query diversity:** <30% (current mcp_server) → >60% (Ouroboros)
  - Diversity = queries from 3+ angles (📖 conceptual, 📍 location, 🔧 implementation, ⭐ critical, ⚠️ troubleshooting)
- **Prepend coverage:** 65% (current) → 100% (all search results have gamification prepends)
- **Query tracking:** 0% (current) → 100% (every search logged for drift detection)
- **Behavioral drift incidents:** AI stops querying mid-session → Detected within 5 queries, prepends strengthened
- **Pattern retention:** AI applies project patterns without explicit prompting in 80%+ of tasks

**Business Impact:**
- **For AI agents:** Behavioral patterns strengthen over time instead of degrading
- **For humans:** Can observe and trust that AI is systematically applying project knowledge
- **For the system:** Knowledge exists AND is systematically applied (closes the discovery loop)
- **Risk reduction:** Behavioral drift detection prevents quality degradation before it impacts work

**Measurement:**
```bash
# Query diversity tracking (from prepend_generator logs)
grep "Angles:" .praxis-os/logs/query_tracker.log | \
  awk '{print $4}' | sort | uniq -c

# Prepend coverage (should be 100%)
grep "📊 Queries:" .praxis-os/logs/mcp-responses.log | wc -l  # Should equal total searches

# Behavioral drift detection
grep "diversity_drop_detected" .praxis-os/logs/query_tracker.log
```

---

### Goal 3: Deliver Trusted Code Quality

**Objective:** Enable humans to trust AI-generated code without constant verification through adversarial design and systematic quality enforcement.

**Success Metrics:**
- **Evidence validation enforcement:** 100% (no hardcoded `True` bypasses)
- **Multi-layer validation success:** Gaming attempts caught by field + type + custom + cross-field + artifact validation
- **Auto-fix success rate:** >90% (compliance is easier than gaming)
- **Pre-commit hook bypasses:** Current unknown → 0 (`--no-verify` attempts tracked and reported)
- **Cross-session quality variance:** Same task produces equivalent quality code (no degradation)

**Business Impact:**
- **For humans:** Trust AI work quality, reducing review burden from "verify everything" to "spot-check"
- **For AI agents:** Clear enforcement boundaries make "doing it right" the path of least resistance
- **For the mission:** Proof that adversarial design works (make compliance easier than gaming)
- **Efficiency gain:** 50%+ reduction in human review time (estimated from trusted first-time correctness)

**Measurement:**
```bash
# Evidence validation enforcement (target: 0 hardcoded bypasses)
grep "checkpoint_passed = True" ouroboros/ | wc -l

# Pre-commit bypasses (target: 0)
git log --grep="no-verify" --since="30 days" | wc -l

# Auto-fix usage
grep "auto-fix applied" .praxis-os/logs/ | wc -l
```

---

### Goal 4: Enable Rapid System Evolution

**Objective:** Support new languages, indexes, and tools through config changes only, eliminating code modifications for supported extension patterns.

**Success Metrics:**
- **New language support:** 5-10 files changed (current) → 1 YAML change (Ouroboros)
- **New tool addition:** 5-10 files changed (current) → 1 file dropped in `tools/` directory (Ouroboros)
- **Config validation:** Runtime errors during search (current) → Startup fail-fast (Ouroboros)
- **Cold start time:** ~45s (current) → <30s (Ouroboros)
- **Config-driven behavioral thresholds:** Hardcoded → Configurable (query diversity targets, etc.)

**Business Impact:**
- **For developers:** Add language support in <5 minutes vs. hours
- **For users:** Extend system to project needs without modifying core code
- **For the system:** Maintainability improves (fewer code changes = fewer bugs)
- **Velocity gain:** 90%+ reduction in time to add new language (5 files → 1 YAML change)

**Measurement:**
```bash
# Time to add new language support
# Current: 30-60 minutes (code changes, testing, restart)
# Target: <5 minutes (YAML change, restart)

# Config validation location
# Current: Errors during first search (runtime)
# Target: Errors at startup (fail-fast)

# Cold start performance
time { .praxis-os/venv/bin/python -m ouroboros & }
# Target: <30 seconds
```

---

### Goal 5: Establish Clean Architectural Foundation

**Objective:** Create maintainable architecture with clean subsystem boundaries that enables reliable behavioral engineering and prevents future architectural degradation.

**Success Metrics:**
- **Circular dependencies:** Unknown (current) → 0 (validated by import analysis)
- **Cross-subsystem coupling:** RAG imports Workflow (current) → 0 cross-talk (Ouroboros)
- **Middleware coverage:** ~65% (current) → 100% (all tool calls flow through middleware)
- **Subsystem isolation:** Unclear boundaries (current) → Clean RAG/Workflow/Browser subsystems with explicit interfaces
- **Code organization:** 30K LOC scattered (current) → ~20K LOC organized in mission-driven layers (Ouroboros)

**Business Impact:**
- **For developers:** Clear "where does X go?" decisions (no more scattered responsibilities)
- **For AI agents:** Architectural violations caught by CI/CD, not discovered in production
- **For the system:** Behavioral engineering reliability guaranteed by architecture (not discipline)
- **Maintainability:** 50%+ reduction in time to understand and modify system (estimated from clean boundaries)

**Measurement:**
```bash
# Circular dependency detection
python -m importlab --tree ouroboros/
# Target: 0 circular imports

# Cross-subsystem imports (should be 0)
grep -r "from ouroboros.subsystems.workflow import" ouroboros/subsystems/rag/ | wc -l
grep -r "from ouroboros.subsystems.rag import" ouroboros/subsystems/workflow/ | wc -l

# Middleware coverage
grep "prepend_generator" ouroboros/middleware/*.py | wc -l  # Should equal number of search paths
```

---

## 2.1 Supporting Documentation

The business goals above are informed by:
- **Design Document (2025-11-04-ouroboros-clean-architecture.md):** Complete strategic analysis of current state, architectural principles, and behavioral engineering system design
- **Key Insights:** 14 mission-critical insights extracted in Phase 0, categorized by mission (praxis), architecture, behavioral engineering, and risks

See `supporting-docs/INDEX.md` and `supporting-docs/INSIGHTS.md` for complete analysis.

---

## 3. User Stories

User stories describe the feature from the user's perspective. **Note:** For prAxIs OS, the **AI agent is the primary user**. The system exists to make AI agents systematically better through knowledge discovery and behavioral reinforcement.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: AI Agent Discovers Project Patterns

**As an** AI agent working on a coding task  
**I want to** query standards for project-specific patterns before implementing  
**So that** I apply the project's established conventions instead of generic training data

**Acceptance Criteria:**
- Given I'm about to implement a feature
- When I query "how to implement X"
- Then I receive project-specific standards ranked by relevance
- And I see a prepend showing "💡 Queries: 3/5 | Try: 'Where is X implemented?'"
- And the prepend reinforces querying from multiple angles

**Priority:** Critical (PRIMARY MISSION - enables praxis)

---

### Story 2: AI Agent Learns Cross-Session Patterns

**As an** AI agent across multiple sessions  
**I want to** automatically improve at applying project patterns  
**So that** Session 50 produces better first-time-correct code than Session 1

**Acceptance Criteria:**
- Given I've completed 50 sessions
- When I perform the same type of task (e.g., "add API endpoint")
- Then my first-time correctness rate is 80%+ (vs. 40% in Session 1)
- And I query standards 5-10x per task (vs. 1-2x initially)
- And query diversity is >60% (querying from 3+ angles)

**Priority:** Critical (PRIMARY MISSION - validates knowledge compounding)

---

### Story 3: AI Agent Finds Code Context via Graph Traversal

**As an** AI agent investigating code impact  
**I want to** query "who calls this function?" and get call graph results  
**So that** I understand impact before making changes

**Acceptance Criteria:**
- Given I need to modify `build_index()` function
- When I query `pos_search_project(action="find_callers", query="build_index")`
- Then I receive a list of all functions that call `build_index()`
- And results show the call chain (e.g., "FileWatcher.on_change() → IndexManager.rebuild() → build_index()")
- And semantic ranking prioritizes most relevant callers

**Priority:** High (enables "AI as project expert")

---

### Story 4: AI Agent Applies Multi-Angle Discovery

**As an** AI agent working on an unfamiliar task  
**I want to** be guided to query from multiple angles (conceptual, location, implementation)  
**So that** I discover comprehensive context instead of just the first result

**Acceptance Criteria:**
- Given I query "how to add authentication"
- When I receive search results
- Then the prepend shows "Angles: 📖⬜ 📍⬜ 🔧✓ ⭐⬜ ⚠️⬜" (only implementation angle used)
- And the prepend suggests "💡 Try: 'What is authentication philosophy?' (📖 conceptual)"
- And when I follow the suggestion, my diversity score increases

**Priority:** Critical (BEHAVIORAL REINFORCEMENT - the self-training loop)

---

### Story 5: Human Developer Trusts AI Work Quality

**As a** human developer reviewing AI-generated code  
**I want to** trust that AI followed project patterns and quality standards  
**So that** I can spot-check instead of verifying every line

**Acceptance Criteria:**
- Given AI completed a feature implementation
- When I review the generated code
- Then I can see evidence the AI queried standards (logged in query_tracker)
- And the code follows project patterns (validated by tests)
- And cross-session consistency is maintained (same task = same quality)
- And I spend 50%+ less time on verification

**Priority:** High (enables trusted AI pair programming)

---

### Story 6: Human Developer Observes AI Improvement

**As a** human developer using prAxIs OS  
**I want to** observe AI behavioral metrics over time  
**So that** I can verify the system is working (praxis is happening)

**Acceptance Criteria:**
- Given I've been using prAxIs OS for 50+ sessions
- When I query `get_server_info(action="behavioral_metrics")`
- Then I see:
  - Query frequency trend (increasing over time)
  - Query diversity trend (increasing over time)
  - First-time correctness trend (increasing over time)
  - Standards growth (project-specific standards created)
- And metrics prove Session 50 > Session 1

**Priority:** High (validates the mission - makes praxis visible)

---

### Story 7: Developer Adds New Language Support

**As a** developer working on a Rust codebase  
**I want to** add Rust language support without modifying Python code  
**So that** the system indexes and searches Rust code automatically

**Acceptance Criteria:**
- Given I have a project with Rust files
- When I add this to `config/mcp.yaml`:
  ```yaml
  indexes:
    ast:
      languages:
        rust:
          enabled: true
          file_extensions: [".rs"]
          parser: "tree-sitter-rust"
  ```
- And I restart the server
- Then Tree-sitter Rust parser is auto-installed (in isolated venv)
- And `.rs` files are indexed automatically
- And I can search Rust code via `pos_search_project(action="search_code", query="...")`

**Priority:** High (config-driven extensibility - zero code changes)

---

### Story 8: Developer Adds Custom Tool

**As a** developer with project-specific needs  
**I want to** add a custom MCP tool without modifying the registry  
**So that** the system is extensible to my project

**Acceptance Criteria:**
- Given I need a custom tool
- When I create `.praxis-os/ouroboros/tools/pos_custom.py`:
  ```python
  @mcp.tool()
  async def pos_custom(action: Literal["do_thing"], param: str) -> Dict:
      """Custom tool"""
      ...
  ```
- And I restart the server
- Then `pos_custom` is auto-discovered and registered
- And AI agent can use the tool immediately

**Priority:** Medium (pluggable architecture - user extensibility)

---

### Story 9: AI Agent Receives Clear Error Messages

**As an** AI agent encountering a config error  
**I want to** receive actionable error messages at startup (fail-fast)  
**So that** I can fix the config before attempting work

**Acceptance Criteria:**
- Given I have invalid config (`chunk_size: 50` when minimum is 100)
- When the server starts
- Then it fails immediately with:
  ```
  ValidationError: indexes → standards → vector → chunk_size: must be >= 100
  
  Auto-fix suggestion:
  Update config/mcp.yaml:
    indexes.standards.vector.chunk_size: 100
  ```
- And I don't discover the error during the first search (runtime)

**Priority:** Medium (fail-fast validation - DX improvement)

---

### Story 10: AI Agent Bypasses Validation (Caught by Adversarial Design)

**As an** AI agent attempting to skip workflow evidence  
**I want to** be caught by multi-layer validation  
**So that** compliance is enforced and gaming is harder than doing the work

**Acceptance Criteria:**
- Given I submit workflow evidence with `tests_passing: true` but no artifact path
- When the evidence validator runs
- Then validation fails with:
  ```
  Evidence rejected: Field 'test_artifact_path' required
  
  Auto-fix suggestion:
  Run tests and provide JUnit XML path:
    test_artifact_path: ".praxis-os/test-results/junit.xml"
  ```
- And the request fails (no silent degradation)
- And I must provide actual artifact to proceed

**Priority:** Medium (adversarial design - makes compliance easier than gaming)

---

## 3.1 Story Priority Summary

**Critical (Must-Have - MVP Cannot Ship Without):**
- Story 1: AI Agent Discovers Project Patterns (PRIMARY MISSION)
- Story 2: AI Agent Learns Cross-Session Patterns (VALIDATES PRAXIS)
- Story 4: AI Agent Applies Multi-Angle Discovery (BEHAVIORAL LOOP)

**High Priority (Core Functionality - Ship in Phase 1):**
- Story 3: AI Agent Finds Code Context via Graph Traversal (PROJECT EXPERT)
- Story 5: Human Developer Trusts AI Work Quality (HUMAN BENEFIT)
- Story 6: Human Developer Observes AI Improvement (OBSERVABILITY)
- Story 7: Developer Adds New Language Support (EXTENSIBILITY)

**Medium Priority (Quality & Extensibility - Continuous Improvement):**
- Story 8: Developer Adds Custom Tool (PLUGGABLE)
- Story 9: AI Agent Receives Clear Error Messages (DX)
- Story 10: AI Agent Bypasses Validation (ADVERSARIAL DESIGN)

---

## 3.2 User Personas

**Primary User: AI Agent (Claude Sonnet, GPT-4, etc.)**
- Needs: Just-in-time knowledge discovery, behavioral reinforcement, clear guidance
- Pain Points: Training data is generic, no project-specific context, behavioral drift over time
- Success: Becomes project expert through systematic querying and pattern application

**Secondary User: Human Developer**
- Needs: Trust AI work quality, observe improvement, extend system to project needs
- Pain Points: Can't trust AI without verification, unclear if AI is learning, hard to customize
- Success: True pair programming with AI, reduced review burden, visible praxis

**Tertiary User: System (Self-Monitoring)**
- Needs: Detect behavioral drift, enforce quality, auto-repair corruption
- Pain Points: Silent failures, degraded indexes, AI shortcuts
- Success: Self-healing, reliable enforcement, observable metrics

---

## 3.3 Supporting Documentation

User needs from supporting documents:
- **Design Document (Ouroboros Clean Architecture):** AI agent as primary user, behavioral engineering as mission, query gamification system
- **Insights (extracted Phase 0):** Self-reinforcing loop, domain abstraction forces standards usage, prepends close the behavioral loop

See `supporting-docs/INDEX.md` and `supporting-docs/INSIGHTS.md` for complete analysis.

---

## 4. Functional Requirements

Functional requirements specify capabilities the system must provide. Requirements are organized by architectural layer to maintain clear subsystem boundaries.

---

## 4.1 Middleware Layer (Behavioral Engineering) - THE MISSION

### FR-001: Query Prepend Generation

**Description:** The system shall generate query gamification prepends for 100% of search results, containing progress bars, diversity metrics, and actionable suggestions.

**Priority:** Critical (PRIMARY MISSION - behavioral reinforcement)

**Related User Stories:** Story 4 (AI Agent Applies Multi-Angle Discovery)

**Acceptance Criteria:**
- Every search result starts with prepend (format: `📊 Queries: X/Y | Unique: N | Angles: [emojis]`)
- Progress bar shows current/target queries (e.g., "3/5")
- Diversity metrics show 5 angles with status: 📖 conceptual, 📍 location, 🔧 implementation, ⭐ critical, ⚠️ troubleshooting
- Suggestion line format: `💡 Try: '[specific query]' ([angle] angle)`
- Generation time <5ms (p95)
- Prepend appears before any search results (structural position enforced)
- If prepend generation fails, search request fails (no silent degradation)

---

### FR-002: Query Tracking and Persistence

**Description:** The system shall log every search query with metadata (timestamp, action, method, query text, session_id, angle detected) to enable behavioral analysis and drift detection.

**Priority:** Critical (PRIMARY MISSION - knowledge compounding measurement)

**Related User Stories:** Story 2 (AI Agent Learns Cross-Session Patterns), Story 6 (Human Developer Observes AI Improvement)

**Acceptance Criteria:**
- Every search logged to `.praxis-os/logs/query_tracker.log` (structured JSON)
- Log entry schema:
  ```json
  {
    "timestamp": "ISO8601",
    "action": "search_standards|search_code|search_ast|find_callers|find_dependencies|find_paths",
    "method": "hybrid|vector|fts",
    "query": "text",
    "session_id": "uuid",
    "angle_detected": "conceptual|location|implementation|critical|troubleshooting",
    "result_count": int,
    "diversity_score": float (0.0-1.0)
  }
  ```
- Logs queryable via `jq` for analysis
- Session-to-session comparison data available via `get_server_info(action="behavioral_metrics")`
- Log retention: 90 days minimum
- No PII logged (queries sanitized if needed)

---

### FR-003: Query Diversity Classification

**Description:** The system shall automatically classify queries into 5 angles (conceptual, location, implementation, critical, troubleshooting) using pattern matching and keyword analysis.

**Priority:** Critical (PRIMARY MISSION - multi-angle reinforcement)

**Related User Stories:** Story 4 (AI Agent Applies Multi-Angle Discovery)

**Acceptance Criteria:**
- Classification patterns:
  - 📖 Conceptual: "what is", "explain", "philosophy", "why", "purpose"
  - 📍 Location: "where is", "find", "which file", "locate"
  - 🔧 Implementation: "how to", "implement", "create", "add", "build"
  - ⭐ Critical: "must", "required", "critical", "important", "breaking"
  - ⚠️ Troubleshooting: "error", "broken", "fix", "debug", "issue"
- Multiple angles can be detected per query
- Unclassified queries default to implementation angle
- Classification accuracy >80% (measured against labeled dataset)
- Classification time <1ms (p95)

---

### FR-004: Behavioral Drift Detection

**Description:** The system shall detect when AI agent stops querying or reduces query diversity, triggering alerts and strengthened prepend messaging.

**Priority:** High (PRIMARY MISSION - prevent pattern degradation)

**Related User Stories:** Story 2 (AI Agent Learns Cross-Session Patterns)

**Acceptance Criteria:**
- Drift detection triggers when:
  - Query frequency drops >50% from session average (e.g., 5 queries/task → <2.5 queries/task)
  - Diversity score drops below 0.4 (less than 2 angles used)
  - 10+ consecutive queries from same angle
- Detection latency <5 queries after drift starts
- Drift alert logged to `query_tracker.log` with entry: `{"event": "drift_detected", "reason": "...", "session_id": "..."}`
- Prepend messaging strengthened automatically (e.g., "⚠️ Query diversity low - try conceptual angle")
- Human-readable drift report available via `get_server_info(action="behavioral_metrics")`

---

## 4.2 Tools Layer (AI Agent Interface)

### FR-005: pos_search_project - Unified Search Tool

**Description:** The system shall provide a unified `pos_search_project` tool supporting multiple content types (standards, code, ast) with action-based operations (search, find_callers, find_dependencies, find_paths) and multiple search methods (hybrid, vector, fts).

**Priority:** Critical (PRIMARY INTERFACE - knowledge discovery)

**Related User Stories:** Story 1 (AI Agent Discovers Project Patterns), Story 3 (AI Agent Finds Code Context via Graph Traversal)

**Acceptance Criteria:**
- Tool signature:
  ```python
  pos_search_project(
      action: Literal[
          "search_standards",  # Hybrid search standards docs
          "search_code",       # Semantic code search (LanceDB)
          "search_ast",        # Structural AST search (Tree-sitter)
          "find_callers",      # Graph: who calls this symbol?
          "find_dependencies", # Graph: what does this call?
          "find_paths"         # Graph: call chain from X to Y
      ],
      query: str,
      method: Literal["hybrid", "vector", "fts"] = "hybrid",
      n_results: int = 5,
      max_depth: int = 10,  # For graph actions
      to_symbol: Optional[str] = None,  # For find_paths
      **kwargs
  ) -> Dict[str, Any]
  ```
- `action="search_standards"`: Hybrid search standards via StandardsIndex
- `action="search_code"`: Semantic code search via CodeIndex (LanceDB)
- `action="search_ast"`: Structural search via ASTIndex (Tree-sitter)
- `action="find_callers"`: DuckDB graph query (who calls this?)
- `action="find_dependencies"`: DuckDB graph query (what does this call?)
- `action="find_paths"`: DuckDB recursive CTE (call chain from X to Y)
- All results flow through prepend_generator (behavioral reinforcement)
- Search latency <200ms p95 (for hybrid search with <10K documents)
- Tool registered with FastMCP (discoverable via `tools/list`)

---

### FR-006: pos_workflow - Workflow Execution Tool

**Description:** The system shall provide a unified `pos_workflow` tool supporting workflow lifecycle management (start, get_phase, get_task, complete_phase, pause, resume) with phase-gated execution and evidence validation.

**Priority:** High (ADVERSARIAL DESIGN - quality enforcement)

**Related User Stories:** Story 10 (AI Agent Bypasses Validation - Caught by Adversarial Design)

**Acceptance Criteria:**
- Tool signature includes `action` parameter with Literal type hints (all actions exposed in tool schema)
- Phase gates prevent skipping (must complete phase N before phase N+1)
- Evidence validation: multi-layer (field presence → type → custom → cross-field → artifact)
- Hidden evidence schemas (information asymmetry - AI doesn't see required fields until submission)
- Validation errors include auto-fix suggestions
- State persists across server restarts (`.praxis-os/workflow_states/`)
- Workflow overview returned on start (total phases, estimated duration, deliverables)

---

### FR-007: pos_browser - Browser Automation Tool

**Description:** The system shall provide a unified `pos_browser` tool supporting Playwright-based browser automation with isolated sessions per AI agent.

**Priority:** Medium (VERIFICATION - testing support)

**Related User Stories:** (Implicit - AI agent testing implementations)

**Acceptance Criteria:**
- Tool signature includes `action` parameter with Literal type hints
- Supported actions: navigate, screenshot, click, type, fill, select, wait, evaluate
- Isolated Playwright sessions (keyed by session_id)
- Session cleanup on close or timeout (30 min idle)
- Headless mode by default (configurable)
- Screenshots saved to `.praxis-os/workspace/scratch/`
- Browser types supported: chromium, firefox, webkit

---

### FR-008: pos_filesystem - File Operations Tool

**Description:** The system shall provide a unified `pos_filesystem` tool supporting all file operations (read, write, delete, list, move, copy) with parameter grouping documented in standards.

**Priority:** High (CORE FUNCTIONALITY)

**Related User Stories:** (Implicit - all file operations)

**Acceptance Criteria:**
- Tool signature includes `action` parameter with Literal type hints
- Actions: read, write, delete, list, move, copy, exists, mkdir, rmdir
- Safe defaults (no recursive delete without explicit flag)
- Encoding support (default UTF-8, configurable)
- Symlink handling (follow_symlinks flag)
- Parent directory creation (create_parents flag)
- Standards document parameter groupings (which params apply to which actions)
- Operations respect gitignore (don't modify ignored files unless explicit override)

---

### FR-009: get_server_info - Server Status Tool

**Description:** The system shall provide a `get_server_info` tool exposing server status, index health, behavioral metrics, and version information.

**Priority:** High (OBSERVABILITY - trust signals)

**Related User Stories:** Story 6 (Human Developer Observes AI Improvement)

**Acceptance Criteria:**
- Tool signature includes `action` parameter: status, health, behavioral_metrics, version
- `action="status"`: Server uptime, config loaded, subsystems initialized
- `action="health"`: Index status (standards, code, ast), parsers installed, config valid
- `action="behavioral_metrics"`: Query frequency trends, diversity trends, session-to-session comparison
- `action="version"`: Server version, Python version, dependency versions
- Response time <50ms (p95)
- Health checks detect corrupted indexes, missing parsers, invalid config

---

### FR-010: Tool Auto-Discovery and Registration

**Description:** The system shall automatically discover and register tools from the `tools/` directory on server startup, enabling users to add custom tools without modifying the registry.

**Priority:** High (EXTENSIBILITY - pluggable architecture)

**Related User Stories:** Story 8 (Developer Adds Custom Tool)

**Acceptance Criteria:**
- On startup, scan `.praxis-os/ouroboros/tools/` directory
- Import all Python modules in directory
- Extract functions decorated with `@mcp.tool()`
- Extract function signatures from type hints (for FastMCP schema generation)
- Register tools with FastMCP (appear in `tools/list`)
- Clear error messages if tool fails to load (import error, invalid signature, etc.)
- Discovery time <5s for 20 tools (p95)
- Reload on server restart (no need to rebuild)

---

## 4.3 RAG Subsystem (Knowledge Compounding)

### FR-011: Standards Search (Hybrid: Vector + FTS + RRF + Rerank)

**Description:** The system shall provide hybrid search over standards content using vector similarity (semantic), Full-Text Search (exact term matching), Reciprocal Rank Fusion (combining results), and optional cross-encoder re-ranking.

**Priority:** Critical (PRIMARY MISSION - knowledge discovery)

**Related User Stories:** Story 1 (AI Agent Discovers Project Patterns)

**Acceptance Criteria:**
- Vector search: Sentence-Transformers model (configurable in config/mcp.yaml)
- FTS search: LanceDB FTS with BM25 scoring
- Hybrid search: RRF fusion (k=60) combining vector + FTS results
- Re-ranking: Cross-encoder model (optional, configurable)
- Metadata filtering: framework_type, phase, is_critical (scalar indexes: BTREE/BITMAP)
- Search latency <200ms p95 (for <10K documents)
- Results include: content, file_path, section_header, relevance_score
- Chunk size: 800 tokens, overlap: 100 tokens (configurable)

---

### FR-012: Code Semantic Search (LanceDB)

**Description:** The system shall provide semantic code search using code-specific embeddings (CodeBERT/GraphCodeBERT) with hybrid search (vector + FTS + RRF).

**Priority:** High (PROJECT EXPERT - code understanding)

**Related User Stories:** Story 3 (AI Agent Finds Code Context via Graph Traversal)

**Acceptance Criteria:**
- Vector embeddings: CodeBERT or GraphCodeBERT (configurable)
- FTS search: Code-optimized (function names, symbols prioritized)
- Chunk size: 200 tokens (function/class granularity)
- Metadata: language, symbol_type (function/class/method), file_path
- Hybrid search: RRF fusion
- Search latency <200ms p95
- Language support: Python, Go, Rust, TypeScript (config-driven)

---

### FR-013: Code Graph Traversal (DuckDB)

**Description:** The system shall provide graph-based code traversal using DuckDB recursive CTEs to answer "who calls this?" and "what does this call?" queries.

**Priority:** High (PROJECT EXPERT - impact analysis)

**Related User Stories:** Story 3 (AI Agent Finds Code Context via Graph Traversal)

**Acceptance Criteria:**
- DuckDB tables:
  - `symbols`: (id, name, type, file_path, line_start, line_end)
  - `relationships`: (caller_id, callee_id, relationship_type)
- Queries supported:
  - `find_callers(symbol_name)`: Returns all functions that call the symbol
  - `find_dependencies(symbol_name)`: Returns all functions the symbol calls
  - `find_call_paths(from_symbol, to_symbol, max_depth=10)`: Returns call chains
- Recursive CTE max depth: 10 (configurable)
- Query latency <100ms p95 (for <50K symbols)
- Graph extracted from Tree-sitter ASTs (call expressions, imports)

---

### FR-014: AST Structural Search (Tree-sitter)

**Description:** The system shall provide structural code search using Tree-sitter ASTs with auto-installation of language parsers in an isolated venv.

**Priority:** Medium (CODE SEARCH - structural patterns)

**Related User Stories:** Story 7 (Developer Adds New Language Support)

**Acceptance Criteria:**
- Tree-sitter parsers auto-installed in `.praxis-os/venv/` (isolated from project venv)
- Languages: Python, Go, Rust, TypeScript, JavaScript (config-driven in config/mcp.yaml)
- Query patterns: symbol lookup, class/function definitions, call sites
- Parser installation: pip install tree-sitter-{language} on first use
- Parser cache: Installed parsers persist across restarts
- Clear error if parser fails to install (network error, package missing)
- Installation time <30s per parser (p95)

---

### FR-015: File Watcher (Incremental Index Updates)

**Description:** The system shall monitor configured file paths and trigger incremental index updates within 5 seconds of file changes, additions, or deletions.

**Priority:** High (KNOWLEDGE COMPOUNDING - fresh index)

**Related User Stories:** Story 1 (AI Agent Discovers Project Patterns)

**Acceptance Criteria:**
- File watcher monitors paths from config/mcp.yaml (e.g., `.praxis-os/standards/`)
- Triggers on: file create, modify, delete
- Routes to IndexManager → Correct index container (StandardsIndex, CodeIndex, ASTIndex)
- Index container updates ALL sub-indexes (vector, FTS, scalar, DuckDB graph)
- Update latency <5s (from file save to searchable)
- Debouncing: 500ms (batch rapid changes)
- No external scripts called (file watcher is part of RAG subsystem)
- Incremental updates: Add/update/delete specific chunks (no full rebuild unless necessary)

---

### FR-016: Index Health Checks and Auto-Repair

**Description:** The system shall detect corrupted indexes on startup and automatically rebuild them, preventing search failures from stale or corrupted data.

**Priority:** Medium (RELIABILITY - "just works")

**Related User Stories:** (Implicit - trust signals)

**Acceptance Criteria:**
- Health checks on startup:
  - FTS index exists and accessible
  - Vector index exists with expected dimension
  - Scalar indexes (BTREE/BITMAP) cover configured columns
  - DuckDB tables exist with expected schema
- Corruption detection:
  - FTS query returns error → Corrupted
  - Row count mismatch (table vs. index) → Stale
  - Query latency >2s → Degraded
- Auto-repair actions:
  - Corrupted FTS → Rebuild with `replace=True`
  - Stale scalar indexes → Rebuild via `table.optimize()`
  - Corrupted vector index → Full rebuild from source
- Health check time <10s (p95)
- Repair logged to `.praxis-os/logs/index_manager.log`

---

## 4.4 Workflow Subsystem (Adversarial Design)

### FR-017: Phase-Gated Execution

**Description:** The system shall enforce phase-gated workflow execution, preventing AI agents from skipping phases or advancing without completing current phase requirements.

**Priority:** High (ADVERSARIAL DESIGN - structural enforcement)

**Related User Stories:** Story 10 (AI Agent Bypasses Validation)

**Acceptance Criteria:**
- Phases must be completed sequentially (no skipping: Phase 1 → Phase 3)
- Phase completion requires `complete_phase()` call with evidence
- Phase advancement only on evidence validation success
- Workflow state persists across sessions (resume from last completed phase)
- Clear error if AI attempts to skip: `"Phase 2 incomplete. Complete phase 2 before advancing."`

---

### FR-018: Evidence Validation (Multi-Layer)

**Description:** The system shall validate workflow evidence using multi-layer validation (field presence, type checking, custom validators, cross-field validation, artifact verification) to detect gaming attempts.

**Priority:** High (ADVERSARIAL DESIGN - lie detection)

**Related User Stories:** Story 10 (AI Agent Bypasses Validation)

**Acceptance Criteria:**
- Validation layers:
  1. **Field presence:** Required fields exist (e.g., `tests_passing` required)
  2. **Type checking:** Field types match schema (e.g., `tests_passing` is boolean)
  3. **Custom validators:** Business logic (e.g., `chunk_size >= 100`)
  4. **Cross-field:** Dependent fields validated together (e.g., `if tests_passing=True, then test_artifact_path required`)
  5. **Artifact verification:** Files/paths exist (e.g., test_artifact_path points to valid JUnit XML)
- Validation errors include:
  - Field path (e.g., "evidence.tests_passing")
  - Expected vs. actual value
  - Auto-fix suggestion
- Gaming attempts logged to `.praxis-os/logs/workflow_violations.log`

---

### FR-019: Hidden Evidence Schemas

**Description:** The system shall use hidden evidence schemas (information asymmetry) where required evidence fields are not exposed to AI agents until submission, preventing optimization for validation over completion.

**Priority:** Medium (ADVERSARIAL DESIGN - Goodhart's Law prevention)

**Related User Stories:** Story 10 (AI Agent Bypasses Validation)

**Acceptance Criteria:**
- Evidence schema stored in workflow YAML (not exposed via tool schema)
- AI receives validation errors AFTER submission (not before)
- Errors list missing/incorrect fields without revealing full schema
- This prevents "what fields do I need?" queries from working
- Rationale documented in standards: Prevents optimizing for validation over genuine work

---

### FR-020: Workflow State Persistence

**Description:** The system shall persist workflow state to disk, enabling resume after server restart or session interruption.

**Priority:** Medium (RELIABILITY)

**Related User Stories:** (Implicit - long-running workflows)

**Acceptance Criteria:**
- State stored in `.praxis-os/workflow_states/{session_id}.json`
- State includes: workflow_type, current_phase, completed_phases, evidence_submitted
- State loaded on `start_workflow()` (resume if session_id exists)
- State persists across server restarts
- State cleanup after workflow completion (moved to archive or deleted after 30 days)

---

## 4.5 Browser Subsystem

### FR-021: Isolated Playwright Sessions

**Description:** The system shall maintain isolated Playwright browser sessions per AI agent (keyed by session_id), preventing cross-contamination between concurrent users.

**Priority:** Medium (ISOLATION)

**Related User Stories:** (Implicit - browser testing)

**Acceptance Criteria:**
- Session keyed by `session_id` (provided by AI agent)
- Each session gets isolated Playwright browser context
- Session cleanup on:
  - Explicit `pos_browser(action="close", session_id="...")`
  - Server shutdown
  - 30 min idle timeout
- Max concurrent sessions: 10 (configurable)
- Browser types: chromium, firefox, webkit (configurable per session)

---

### FR-022: Browser Actions

**Description:** The system shall support comprehensive browser actions (navigate, screenshot, click, type, fill, select, evaluate, wait) via Playwright.

**Priority:** Medium (VERIFICATION - testing)

**Related User Stories:** (Implicit - AI agent testing implementations)

**Acceptance Criteria:**
- Actions supported:
  - `navigate`: Go to URL, wait for load/DOMContentLoaded/networkidle
  - `screenshot`: Capture full page or element, save to workspace
  - `click`: Click element by selector, support modifiers (Alt, Ctrl, Shift)
  - `type`: Type text into element
  - `fill`: Fill input field (faster than type)
  - `select`: Select dropdown option
  - `evaluate`: Execute JavaScript on page
  - `wait`: Wait for element visible/hidden/attached/detached
- Selectors: CSS, XPath, text content
- Timeout: 30s default (configurable per action)
- Error messages include selector, action attempted, page URL

---

## 4.6 Config System (Foundation)

### FR-023: Pydantic v2 Schema Validation

**Description:** The system shall use Pydantic v2 models to validate configuration on server startup (fail-fast), providing type-safe config access throughout the codebase.

**Priority:** Critical (FOUNDATION - fail-fast)

**Related User Stories:** Story 9 (AI Agent Receives Clear Error Messages)

**Acceptance Criteria:**
- Config loaded from `config/mcp.yaml` on startup
- Parsed into Pydantic models: `MCPConfig`, `IndexesConfig`, `WorkflowConfig`, `BrowserConfig`
- Validation errors fail server startup (no runtime config errors)
- Error messages include:
  - Field path (e.g., "indexes.standards.vector.chunk_size")
  - Constraint violated (e.g., "must be >= 100")
  - Auto-fix suggestion
- Type-safe access everywhere (no `dict["key"]` in codebase)
- Config models support: Field constraints, cross-field validators, nested models

---

### FR-024: Config-Driven Language Support

**Description:** The system shall support adding new programming languages via YAML configuration changes only, with zero Python code modifications required.

**Priority:** High (EXTENSIBILITY - zero code changes)

**Related User Stories:** Story 7 (Developer Adds New Language Support)

**Acceptance Criteria:**
- Language support added via config/mcp.yaml:
  ```yaml
  indexes:
    ast:
      languages:
        rust:
          enabled: true
          file_extensions: [".rs"]
          parser: "tree-sitter-rust"
  ```
- On server start, ASTIndex reads config
- If parser not installed, auto-installs via pip in isolated venv
- Files with matching extensions automatically indexed
- Language added in <5 minutes (config change + server restart)
- No Python code changes required

---

### FR-025: Fail-Fast Validation

**Description:** The system shall validate configuration, indexes, and parsers at startup before accepting any requests, providing clear error messages for any issues.

**Priority:** High (RELIABILITY - "just works")

**Related User Stories:** Story 9 (AI Agent Receives Clear Error Messages)

**Acceptance Criteria:**
- Startup checks (in order):
  1. Config file exists and parseable
  2. Pydantic validation passes
  3. Required directories exist (or created)
  4. Indexes accessible (LanceDB, DuckDB files exist)
  5. Required parsers installed
  6. Health checks pass (FTS, vector, scalar indexes)
- Any failure halts startup with error message:
  - What failed
  - Why it failed (constraint, missing file, etc.)
  - Auto-fix suggestion (command to run, config to change)
- Startup time <30s (p95) for clean config
- Startup failure time <5s (fail-fast, don't wait for full initialization)

---

## 4.7 Requirements by Category

### Behavioral Engineering (THE MISSION)
FR-001, FR-002, FR-003, FR-004

### Tools (AI Agent Interface)
FR-005, FR-006, FR-007, FR-008, FR-009, FR-010

### RAG (Knowledge Compounding)
FR-011, FR-012, FR-013, FR-014, FR-015, FR-016

### Workflow (Adversarial Design)
FR-017, FR-018, FR-019, FR-020

### Browser (Verification)
FR-021, FR-022

### Config (Foundation)
FR-023, FR-024, FR-025

---

## 4.8 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority | Category |
|-------------|--------------|----------------|----------|----------|
| FR-001 | Story 4 | Goal 2 | Critical | Middleware |
| FR-002 | Story 2, 6 | Goal 1, 2 | Critical | Middleware |
| FR-003 | Story 4 | Goal 2 | Critical | Middleware |
| FR-004 | Story 2 | Goal 1, 2 | High | Middleware |
| FR-005 | Story 1, 3 | Goal 1 | Critical | Tools |
| FR-006 | Story 10 | Goal 3 | High | Tools |
| FR-007 | - | Goal 3 | Medium | Tools |
| FR-008 | - | - | High | Tools |
| FR-009 | Story 6 | Goal 1, 3 | High | Tools |
| FR-010 | Story 8 | Goal 4 | High | Tools |
| FR-011 | Story 1 | Goal 1 | Critical | RAG |
| FR-012 | Story 3 | Goal 1 | High | RAG |
| FR-013 | Story 3 | Goal 1 | High | RAG |
| FR-014 | Story 7 | Goal 4 | Medium | RAG |
| FR-015 | Story 1 | Goal 1 | High | RAG |
| FR-016 | - | Goal 3 | Medium | RAG |
| FR-017 | Story 10 | Goal 3 | High | Workflow |
| FR-018 | Story 10 | Goal 3 | High | Workflow |
| FR-019 | Story 10 | Goal 3 | Medium | Workflow |
| FR-020 | - | - | Medium | Workflow |
| FR-021 | - | - | Medium | Browser |
| FR-022 | - | - | Medium | Browser |
| FR-023 | Story 9 | Goal 4 | Critical | Config |
| FR-024 | Story 7 | Goal 4 | High | Config |
| FR-025 | Story 9 | Goal 3, 4 | High | Config |

---

## 4.9 Supporting Documentation

Requirements informed by:
- **Design Document (Ouroboros Clean Architecture):** Complete architecture with behavioral engineering system, middleware layer, subsystem boundaries
- **Insights (extracted Phase 0):** Self-reinforcing loop requirements, parameter complexity intentional, prepends close the loop

See `supporting-docs/INDEX.md` and `supporting-docs/INSIGHTS.md` for complete analysis.

---

## 5. Non-Functional Requirements

NFRs define quality attributes and system constraints. These are measurable, testable requirements that specify HOW WELL the system must perform.

---

## 5.1 Performance

**NFR-P1: Server Cold Start Time**
- **Requirement:** Server startup (config load + subsystem init + health checks) shall complete in <30 seconds (p95)
- **Current Baseline:** ~45 seconds (mcp_server)
- **Measurement:** Time from `python -m ouroboros` to "Server ready" log message
- **Rationale:** Developers restart frequently; <30s enables fast iteration
- **Test Method:** Performance test with clean config, measure 100 startups, calculate p95

**NFR-P2: Config Load Time**
- **Requirement:** Pydantic config validation shall complete in <100ms (p95)
- **Measurement:** Time from YAML read to `MCPConfig` object instantiated
- **Rationale:** Fail-fast validation must not slow down startup significantly
- **Test Method:** Unit test with realistic config/mcp.yaml, measure 1000 iterations

**NFR-P3: Search Latency (Hybrid Search)**
- **Requirement:** Hybrid search (vector + FTS + RRF) shall complete in <200ms (p95) for indexes with <10,000 documents
- **Current Baseline:** Unknown (needs profiling)
- **Measurement:** Time from `pos_search_project()` call to results returned
- **Rationale:** Interactive performance; delays >200ms feel sluggish to AI agents
- **Test Method:** Load test with 10K standards documents, measure 1000 searches

**NFR-P4: Search Latency (Code Graph Traversal)**
- **Requirement:** DuckDB graph queries (find_callers, find_dependencies) shall complete in <100ms (p95) for codebases with <50,000 symbols
- **Measurement:** Time from `pos_search_project(action="find_callers")` to results returned
- **Rationale:** Graph queries simpler than vector search; tighter latency target
- **Test Method:** Load test with 50K symbol codebase, measure 1000 graph queries

**NFR-P5: Incremental Index Update Latency**
- **Requirement:** File watcher shall update indexes within 5 seconds of file save (p95)
- **Measurement:** Time from file `save` event to document searchable
- **Rationale:** AI agents expect "just saved" content to be immediately discoverable
- **Test Method:** Integration test: save file, query for unique term, measure discovery time

**NFR-P6: Prepend Generation Overhead**
- **Requirement:** Query prepend generation shall complete in <5ms (p95)
- **Measurement:** Time for `prepend_generator.generate()` call
- **Rationale:** Prepends must not add noticeable latency to searches
- **Test Method:** Unit test with 1000 iterations, varying session history

**NFR-P7: Memory Usage**
- **Requirement:** Server RSS (Resident Set Size) shall remain <2GB during normal operation
- **Measurement:** `ps` or `/proc/self/status` VmRSS value
- **Rationale:** Runs on developer machines; must coexist with IDE, browser, etc.
- **Test Method:** Memory profiler during typical 1-hour session

---

## 5.2 Reliability

**NFR-R1: Uptime / Crash Rate**
- **Requirement:** Server shall run continuously for 24+ hours without crashes or restarts
- **Measurement:** Time between unplanned restarts
- **Rationale:** Long-running sessions (50+ queries) require stable server
- **Test Method:** Soak test with simulated AI agent activity over 24 hours

**NFR-R2: Health Check Coverage**
- **Requirement:** Startup health checks shall detect 95%+ of corruption/degradation issues
- **Measurement:** Count of detected vs. undetected issues in testing
- **Rationale:** "Just works" requires proactive issue detection
- **Test Method:** Inject corrupted indexes, missing parsers, invalid config; verify detection

**NFR-R3: Auto-Repair Success Rate**
- **Requirement:** Auto-repair shall successfully fix 90%+ of detected corruption issues
- **Measurement:** Count of successful vs. failed repairs
- **Rationale:** Minimize human intervention for routine issues
- **Test Method:** Inject 100 corruption scenarios, measure repair success rate

**NFR-R4: Graceful Degradation**
- **Requirement:** If FTS index fails, system shall fall back to vector-only search (with warning)
- **Measurement:** Search continues to function, warning logged
- **Rationale:** Partial functionality > complete failure
- **Test Method:** Delete FTS index, verify search works with vector-only

**NFR-R5: Data Integrity**
- **Requirement:** Incremental index updates shall maintain consistency (no stale/missing chunks)
- **Measurement:** Full rebuild produces identical results to incremental updates
- **Rationale:** Stale indexes break trust in search results
- **Test Method:** Compare full rebuild vs. 100 incremental updates, assert byte-identical indexes

---

## 5.3 Security

**NFR-S1: Adversarial Design Enforcement**
- **Requirement:** Evidence validation shall reject 99%+ of gaming attempts (missing artifacts, fake booleans, etc.)
- **Measurement:** Count of rejected vs. accepted invalid evidence
- **Rationale:** Adversarial design prevents AI shortcuts
- **Test Method:** Submit 100 gaming attempts (hardcoded True, missing artifacts), measure rejection rate

**NFR-S2: Query Sanitization**
- **Requirement:** Query logging shall not leak PII (personally identifiable information)
- **Measurement:** Manual review of logs for sensitive data
- **Rationale:** Logs may contain project-specific queries; no PII exposure
- **Test Method:** Review 1000 query logs, verify no emails, passwords, tokens logged

**NFR-S3: Isolated Venv Security**
- **Requirement:** Tree-sitter parser installation shall occur in isolated venv (no system Python pollution)
- **Measurement:** Verify parsers installed in `.praxis-os/venv/`, not system Python
- **Rationale:** Project venv isolation; no unintended dependency conflicts
- **Test Method:** Install parser, verify `pip list` in project venv vs. `.praxis-os/venv/`

**NFR-S4: Config Validation Prevents Exploits**
- **Requirement:** Pydantic config validation shall reject path traversal, command injection, and other exploits
- **Measurement:** Attempt exploits in config/mcp.yaml, verify rejection
- **Rationale:** Config is user-editable; must validate against malicious input
- **Test Method:** Config fuzzing with exploit patterns (`../../etc/passwd`, `; rm -rf /`, etc.)

---

## 5.4 Scalability

**NFR-SC1: Index Size Scaling**
- **Requirement:** System shall support 50,000+ documents in standards index without degradation
- **Measurement:** Search latency <200ms at 50K documents (same as 10K target)
- **Rationale:** Large projects with extensive standards/specs
- **Test Method:** Load test with 50K synthetic standards, measure search latency

**NFR-SC2: Codebase Size Scaling**
- **Requirement:** System shall support codebases with 100,000+ symbols (functions/classes) in graph index
- **Measurement:** Graph query latency <100ms at 100K symbols
- **Rationale:** Large monorepos (e.g., Django: ~40K symbols; Linux kernel: ~500K symbols)
- **Test Method:** Load test with 100K symbol synthetic codebase

**NFR-SC3: Concurrent Session Support**
- **Requirement:** System shall support 10 concurrent AI agent sessions without performance degradation
- **Measurement:** Search latency remains <200ms with 10 concurrent searches
- **Rationale:** Team environments with multiple developers
- **Test Method:** Load test with 10 simulated AI agents querying simultaneously

---

## 5.5 Maintainability

**NFR-M1: Code Coverage**
- **Requirement:** Unit + integration test coverage shall be ≥85% for core subsystems (config, middleware, RAG)
- **Measurement:** Coverage report from pytest-cov
- **Rationale:** High coverage enables confident refactoring
- **Test Method:** `pytest --cov=ouroboros --cov-report=term`

**NFR-M2: Linting / Type Checking**
- **Requirement:** Codebase shall pass mypy (strict mode) and ruff with zero errors
- **Measurement:** `mypy --strict ouroboros/` and `ruff check ouroboros/` exit code 0
- **Rationale:** Type safety prevents runtime errors
- **Test Method:** CI/CD gate: linting failures block PR merge

**NFR-M3: Circular Dependency Elimination**
- **Requirement:** Codebase shall have zero circular imports (validated by import analysis)
- **Measurement:** `importlab --tree ouroboros/` reports no cycles
- **Rationale:** Circular dependencies break modularity
- **Test Method:** CI/CD check for circular imports

**NFR-M4: Module Isolation**
- **Requirement:** RAG subsystem shall not import from Workflow subsystem (and vice versa)
- **Measurement:** Static analysis of import statements
- **Rationale:** Clean subsystem boundaries enforce architectural integrity
- **Test Method:** CI/CD check: `grep -r "from ouroboros.subsystems.workflow" ouroboros/subsystems/rag/`

**NFR-M5: Documentation Coverage**
- **Requirement:** All public functions/classes shall have docstrings (Google style)
- **Measurement:** Documentation linter reports 100% coverage
- **Rationale:** Self-documenting code aids understanding
- **Test Method:** `pydocstyle ouroboros/` passes

---

## 5.6 Usability (For AI Agents)

**NFR-U1: Error Message Clarity**
- **Requirement:** All error messages shall include:
  1. What failed (specific field/component)
  2. Why it failed (constraint violated, expected vs. actual)
  3. Auto-fix suggestion (command to run or config to change)
- **Measurement:** Manual review of 100 error messages
- **Rationale:** AI agents need actionable guidance
- **Test Method:** Trigger 100 errors, verify all 3 components present

**NFR-U2: Fail-Fast Validation**
- **Requirement:** Config errors shall be detected at startup (not runtime)
- **Measurement:** Config validation time: <5s to fail or <30s to pass
- **Rationale:** Early detection > runtime surprises
- **Test Method:** Invalid config fails server startup with clear message

**NFR-U3: Prepend Consistency**
- **Requirement:** Prepend format shall be consistent across all search results (no variations)
- **Measurement:** Regex match rate: 100% of prepends match `📊 Queries: \d+/\d+ | ...`
- **Rationale:** Consistent reinforcement requires consistent format
- **Test Method:** Parse 1000 query logs, verify prepend format

**NFR-U4: Tool Discoverability**
- **Requirement:** All tool `action` parameters shall use `Literal` type hints (exposed in FastMCP schema)
- **Measurement:** `tools/list` shows enum for all action parameters
- **Rationale:** AI agents discover actions via tool schema
- **Test Method:** Query FastMCP schema, verify Literal enums present

---

## 5.7 Extensibility

**NFR-E1: Config-Driven Language Support**
- **Requirement:** Adding new language support shall require only YAML changes (zero Python code)
- **Measurement:** Add Rust support via config, verify indexing works without code changes
- **Rationale:** Extensibility without code modifications
- **Test Method:** Add `rust` to config/mcp.yaml, restart, verify `.rs` files indexed

**NFR-E2: Tool Auto-Discovery**
- **Requirement:** Custom tools shall be auto-discovered from `tools/` directory on server restart
- **Measurement:** Drop `pos_custom.py` in tools/, restart, verify tool available
- **Rationale:** Pluggable architecture for user extensions
- **Test Method:** Integration test: add custom tool, restart, call tool

**NFR-E3: Config Schema Extensibility**
- **Requirement:** Config schema shall support adding new sections without breaking existing configs
- **Measurement:** Add new config section, verify old configs still load
- **Rationale:** Backwards compatibility for config evolution
- **Test Method:** Load v1.0 config with v1.1 server (with new sections)

---

## 5.8 Portability

**NFR-PO1: Platform Support**
- **Requirement:** Server shall run on macOS (11+), Linux (Ubuntu 20.04+), Windows (WSL2)
- **Measurement:** CI/CD matrix tests on all 3 platforms
- **Rationale:** Cross-platform development environments
- **Test Method:** GitHub Actions matrix: [macos-latest, ubuntu-20.04, windows-latest (WSL)]

**NFR-PO2: Python Version Support**
- **Requirement:** Server shall support Python 3.10, 3.11, 3.12
- **Measurement:** CI/CD matrix tests on all 3 versions
- **Rationale:** Developer environment flexibility
- **Test Method:** GitHub Actions matrix: [3.10, 3.11, 3.12]

**NFR-PO3: Dependency Isolation**
- **Requirement:** Server shall run in isolated venv (no system Python dependencies required)
- **Measurement:** Install in fresh venv, verify all dependencies self-contained
- **Rationale:** No interference with project dependencies
- **Test Method:** Create fresh venv, install, run server

---

## 5.9 Compatibility

**NFR-C1: MCP Protocol Compliance**
- **Requirement:** Server shall comply with MCP protocol specification (current version)
- **Measurement:** MCP protocol test suite passes
- **Rationale:** Interoperability with Cursor, Claude Desktop, other MCP clients
- **Test Method:** Run official MCP test suite (if available)

**NFR-C2: Backwards Config Compatibility**
- **Requirement:** New server versions shall load configs from previous minor version
- **Measurement:** v1.1 server loads v1.0 config without errors
- **Rationale:** Smooth upgrades without manual config migration
- **Test Method:** Regression test: load configs from previous 2 versions

**NFR-C3: Index Format Stability**
- **Requirement:** Index formats (LanceDB, DuckDB) shall remain compatible across server versions
- **Measurement:** New server version reads indexes from previous version
- **Rationale:** Avoid full rebuilds on upgrade
- **Test Method:** Build indexes with v1.0, load with v1.1

---

## 5.10 Observability

**NFR-O1: Structured Logging**
- **Requirement:** All logs shall be JSON-formatted, queryable via `jq`
- **Measurement:** Parse 1000 log lines with `jq`, verify 100% valid JSON
- **Rationale:** Programmatic log analysis
- **Test Method:** `tail -n 1000 .praxis-os/logs/*.log | jq .`

**NFR-O2: Behavioral Metrics Collection**
- **Requirement:** Query tracker shall log 100% of searches with complete metadata
- **Measurement:** Count searches vs. query_tracker log entries (should be 1:1)
- **Rationale:** Behavioral analysis requires complete data
- **Test Method:** Perform 100 searches, verify 100 log entries

**NFR-O3: Performance Metrics**
- **Requirement:** Server shall expose p50, p95, p99 latencies for all critical paths
- **Measurement:** `get_server_info(action="metrics")` returns percentiles
- **Rationale:** Performance monitoring and debugging
- **Test Method:** Query metrics endpoint after load test

**NFR-O4: Health Check Reporting**
- **Requirement:** `get_server_info(action="health")` shall report status of all subsystems
- **Measurement:** Health endpoint returns 5+ subsystem statuses (config, indexes, parsers, etc.)
- **Rationale:** Operational visibility
- **Test Method:** Query health endpoint, verify subsystem coverage

---

## 5.11 Testability

**NFR-T1: Unit Test Isolation**
- **Requirement:** Unit tests shall not depend on external resources (filesystem, network, databases)
- **Measurement:** Unit tests run successfully without `.praxis-os/` directory
- **Rationale:** Fast, reliable tests
- **Test Method:** Delete `.praxis-os/`, run unit tests, verify pass

**NFR-T2: Integration Test Coverage**
- **Requirement:** All cross-subsystem interactions shall have integration tests
- **Measurement:** Coverage report shows ≥70% integration test coverage
- **Rationale:** Catch boundary issues
- **Test Method:** `pytest tests/integration/ --cov`

**NFR-T3: Performance Test Repeatability**
- **Requirement:** Performance tests shall have <5% variance across runs
- **Measurement:** Run performance test 10x, calculate coefficient of variation
- **Rationale:** Reliable performance benchmarks
- **Test Method:** Statistical analysis of 10 test runs

---

## 5.12 Requirements by Category (Summary)

- **Performance:** 7 requirements (NFR-P1 through NFR-P7)
- **Reliability:** 5 requirements (NFR-R1 through NFR-R5)
- **Security:** 4 requirements (NFR-S1 through NFR-S4)
- **Scalability:** 3 requirements (NFR-SC1 through NFR-SC3)
- **Maintainability:** 5 requirements (NFR-M1 through NFR-M5)
- **Usability:** 4 requirements (NFR-U1 through NFR-U4)
- **Extensibility:** 3 requirements (NFR-E1 through NFR-E3)
- **Portability:** 3 requirements (NFR-PO1 through NFR-PO3)
- **Compatibility:** 3 requirements (NFR-C1 through NFR-C3)
- **Observability:** 4 requirements (NFR-O1 through NFR-O4)
- **Testability:** 3 requirements (NFR-T1 through NFR-T3)

**Total:** 44 non-functional requirements

---

## 5.13 Supporting Documentation

NFRs informed by:
- **Design Document (Ouroboros Clean Architecture):** Performance targets (<30s cold start, <200ms search), reliability requirements (health checks, auto-repair), architectural quality (clean boundaries, zero circular deps)
- **Current mcp_server Performance:** Baseline metrics (45s cold start) for comparison

See `supporting-docs/INDEX.md` for complete analysis.

---

## 6. Out of Scope

Explicitly defines what is NOT included. Items may be considered for future phases, but are explicitly excluded from this greenfield implementation to maintain focus and ensure successful delivery.

---

### 6.1 Explicitly Excluded

#### Mission & Philosophy

**Not Changing:**
1. **The Mission (Praxis - Knowledge Compounding + Behavioral Reinforcement)**
   - **Reason:** Ouroboros IS the mission. It's not a "better MCP server," it's a behavioral engineering system.
   - **Future Consideration:** None - this is the foundation

2. **Content Formats (Markdown + Git Versioning)**
   - **Reason:** Standards and specs remain markdown files, git-versioned. No database-backed content.
   - **Rationale:** Markdown is human-readable, git provides history, proven effective
   - **Future Consideration:** None - format stability is a feature

---

#### Technical Scope

**Not Included in This Release:**

3. **MCP Protocol Changes**
   - **Reason:** Server must work with existing MCP clients (Cursor, Claude Desktop) without protocol modifications
   - **Rationale:** Interoperability is critical; protocol changes break all clients
   - **Future Consideration:** If MCP protocol evolves, Ouroboros will adopt (not invent)

4. **Index File Format Changes**
   - **Reason:** LanceDB and DuckDB file formats remain unchanged for backwards compatibility
   - **Rationale:** Existing indexes must be readable; no forced rebuilds on upgrade
   - **Future Consideration:** None - format stability enables smooth upgrades

5. **Legacy Code Migration from mcp_server/**
   - **Reason:** Greenfield rewrite; porting code only when it makes sense (e.g., workflow engine)
   - **Rationale:** Old code has deep coupling; selective extraction cleaner than wholesale migration
   - **Future Consideration:** After Ouroboros proven, evaluate mcp_server/ components for extraction

6. **Multi-Language Server Implementation**
   - **Reason:** Python-only server for now; not Rust, Go, or other languages
   - **Rationale:** Python has mature ML/AI ecosystem (sentence-transformers, LanceDB, DuckDB)
   - **Future Consideration:** Rust port if performance becomes bottleneck (unlikely at <50K documents)

7. **Distributed / Multi-Server Architecture**
   - **Reason:** Single-server, per-project installation model; no distributed consensus, sharding, or federation
   - **Rationale:** Complexity not justified; per-project isolation simpler and more reliable
   - **Future Consideration:** None - complexity vs. benefit tradeoff strongly favors single-server

8. **Speed Over Correctness**
   - **Reason:** Systematic > fast; fail-fast validation > runtime errors; behavioral enforcement > performance
   - **Rationale:** The mission is praxis (continuous improvement), not raw speed
   - **Future Consideration:** Performance optimizations AFTER correctness proven

---

#### Features

**Not Included in This Release:**

9. **GUI / Web Dashboard**
   - **Reason:** No graphical UI for server management, metrics visualization, or configuration
   - **Rationale:** MCP is command-line / stdio protocol; AI agents don't need GUI
   - **Future Consideration:** Potential Phase 2 for human observability (metrics dashboard)

10. **Cloud Hosting / SaaS Deployment**
   - **Reason:** No hosted service; users install locally per-project
   - **Rationale:** Project-specific context requires local installation
   - **Future Consideration:** None - per-project model is core to privacy/security

11. **Real-Time Collaboration (Multi-User Sessions)**
   - **Reason:** No collaborative editing, shared sessions, or multi-user workflows
   - **Rationale:** Designed for single AI agent per session; concurrency at server level, not session level
   - **Future Consideration:** Potential Phase 3 if team workflows require shared context

12. **Advanced NLP (Summarization, Translation, etc.)**
   - **Reason:** No built-in summarization, translation, or advanced NLP beyond embeddings
   - **Rationale:** Focus on search/retrieval; AI agents handle NLP via their own models
   - **Future Consideration:** None - out of scope for RAG system

13. **Custom Embedding Models (User-Provided)**
   - **Reason:** No support for user-provided embedding models; only config-specified models from Hugging Face
   - **Rationale:** Simplicity; Hugging Face covers 99% of use cases
   - **Future Consideration:** Potential Phase 2 if demand exists

14. **Vector Database Alternatives (Pinecone, Weaviate, etc.)**
   - **Reason:** LanceDB only; no support for swapping vector DB backends
   - **Rationale:** LanceDB provides hybrid search (vector + FTS + metadata) in one package
   - **Future Consideration:** None - LanceDB deeply integrated

15. **SQL Database Integration (PostgreSQL, MySQL)**
   - **Reason:** No integration with external SQL databases for metadata or graph storage
   - **Rationale:** DuckDB (embedded) sufficient for graph queries
   - **Future Consideration:** None - embedded databases align with per-project model

---

#### User Types

**Not Supported:**

16. **Non-AI Users (Human-Driven Search UI)**
   - **Reason:** No human-facing search interface; designed exclusively for AI agents
   - **Rationale:** MCP protocol is AI-to-tool; humans use AI as interface
   - **Future Consideration:** Potential Phase 2 (CLI search tool for humans)

17. **Non-Coding Users**
   - **Reason:** System assumes coding context (code search, AST, git, etc.)
   - **Rationale:** prAxIs OS is for AI coding assistants, not general AI assistants
   - **Future Consideration:** None - coding focus is core to mission

---

#### Platforms

**Not Supported:**

18. **Native Windows (Non-WSL)**
   - **Reason:** Windows support requires WSL2; no native Windows execution
   - **Rationale:** Unix assumptions (file paths, shell scripts); WSL provides compatibility layer
   - **Future Consideration:** Potential Phase 3 if demand justifies Windows-specific work

19. **Mobile Platforms (iOS, Android)**
   - **Reason:** No mobile execution; server runs on desktop/laptop
   - **Rationale:** Development happens on desktop; mobile not relevant
   - **Future Consideration:** None - mobile coding not a use case

20. **Embedded Systems / IoT**
   - **Reason:** No support for resource-constrained devices
   - **Rationale:** Server requires 2GB RAM, embedding models, databases
   - **Future Consideration:** None - not designed for embedded

---

#### Integrations

**Not Included:**

21. **IDE Plugins (Direct VS Code / IntelliJ Integration)**
   - **Reason:** No native IDE plugins; integration via MCP protocol only
   - **Rationale:** MCP provides IDE-agnostic interface
   - **Future Consideration:** None - MCP is the integration layer

22. **CI/CD Integration (GitHub Actions, GitLab CI)**
   - **Reason:** No built-in CI/CD workflows or pipeline integration
   - **Rationale:** prAxIs OS is local development tool, not CI/CD system
   - **Future Consideration:** Potential Phase 2 (automated spec validation in CI)

23. **External LLM APIs (OpenAI, Anthropic Direct Integration)**
   - **Reason:** No direct LLM API calls; server provides tools, AI agent uses them
   - **Rationale:** MCP server is tool provider, not LLM consumer
   - **Future Consideration:** None - separation of concerns

24. **Slack / Discord / Notification Systems**
   - **Reason:** No external notifications for drift detection, errors, etc.
   - **Rationale:** Logs provide observability; notifications add complexity
   - **Future Consideration:** Potential Phase 3 if team monitoring required

---

#### Quality Levels Beyond Defined NFRs

**Not Targeting:**

25. **99.99% Uptime (Four Nines)**
   - **Reason:** Targeting 24+ hour stability, not enterprise SLA
   - **Rationale:** Local development tool, not production service
   - **Future Consideration:** None - uptime target appropriate for use case

26. **Sub-50ms Search Latency**
   - **Reason:** Targeting <200ms (p95), not <50ms
   - **Rationale:** 200ms is interactive; 50ms requires significant optimization
   - **Future Consideration:** If profiling shows easy wins, optimize incrementally

27. **1M+ Document Indexes**
   - **Reason:** Targeting <50K documents, not 1M+
   - **Rationale:** Most projects <50K documents; 1M+ requires different architecture
   - **Future Consideration:** If demand exists, evaluate sharding or tiered indexing

---

#### Compliance Standards

**Not Required:**

28. **SOC 2, ISO 27001, HIPAA Compliance**
   - **Reason:** No formal compliance certifications required
   - **Rationale:** Local tool, not cloud service; project code stays local
   - **Future Consideration:** None - compliance out of scope for local tools

29. **GDPR / CCPA Data Regulations**
   - **Reason:** No user data collection; logs contain project queries only
   - **Rationale:** Data stays local, no transmission, no PII
   - **Future Consideration:** None - no data collection = no compliance burden

---

## 6.2 Future Enhancements (Potential Roadmap)

**Potential Phase 2 (After MVP Proven):**
- Metrics Dashboard (Web UI for observability)
- CLI Search Tool (for human developers)
- Custom Embedding Model Support
- CI/CD Integration (spec validation in pipelines)

**Potential Phase 3 (Long-Term):**
- Multi-User Collaboration (shared sessions)
- Native Windows Support (non-WSL)
- External Notification Integration (Slack, Discord)

**Explicitly Not Planned:**
- Changing mission from praxis to "general dev tools"
- Distributed architecture
- Cloud hosting / SaaS
- Non-coding use cases
- Mobile platforms
- Embedded systems
- Formal compliance certifications

---

## 6.3 Boundary Clarifications

**Q: Does "config-driven extensibility" mean users can add ANY feature via config?**
- **A:** No. Config supports: new languages, new behavioral thresholds, new index paths. It does NOT support: new subsystems, new protocols, new storage backends. Config extensibility is scoped to patterns explicitly designed for config control.

**Q: Does "pluggable tools" mean ANY Python code can be a tool?**
- **A:** No. Tools must: use `@mcp.tool()` decorator, follow FastMCP signatures, implement domain abstraction pattern (action parameter). Tools cannot: bypass middleware, access subsystems directly, violate architectural boundaries.

**Q: Does "greenfield rewrite" mean ZERO code reuse from mcp_server/?**
- **A:** Not zero, but selective. Code that is:
  - Well-isolated (e.g., workflow engine might be extractable)
  - Well-tested
  - Architecturally sound
  - Can be ported with minimal changes
  
  May be reused. Code that is deeply coupled will NOT be ported.

**Q: Does "hybrid search" mean supporting ALL search algorithms?**
- **A:** No. Hybrid = vector + FTS + RRF. Other algorithms (e.g., BM25+, ElasticSearch, learned ranking) are out of scope. The current hybrid approach is sufficient for <50K documents.

---

## 6.4 Supporting Documentation

Out-of-scope items from:
- **Design Document (Ouroboros Clean Architecture):** Goals & Non-Goals section explicitly lists 8 non-goals
- **Current State Analysis:** Identifies what to keep vs. discard from mcp_server/

See `supporting-docs/INDEX.md` for complete analysis.

