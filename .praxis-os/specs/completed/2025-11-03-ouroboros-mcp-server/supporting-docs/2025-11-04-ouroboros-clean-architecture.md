# Ouroboros: Clean MCP Server Architecture

**Date:** 2025-11-04  
**Status:** Draft - Awaiting Approval  
**Author:** Josh (with AI pair programming)

---

## Problem Statement

### What are we solving?

prAxIs OS exists to enable **praxis** - the integration of theory and practice through continuous learning cycles. The system's mission is to make AI agents systematically better through just-in-time knowledge discovery, behavioral reinforcement, and knowledge compounding.

**The current `mcp_server/` violates this mission:**

1. **Broken Behavioral Engineering**
   - Query gamification prepends exist but aren't consistently applied
   - No systematic reinforcement of "query-first" behavior
   - AI behavioral drift occurs (shortcuts, skips querying)
   - Result: Session 50 looks like Session 1 (no learning)

2. **Failed Knowledge Compounding**
   - Standards and specs work, but system doesn't enforce their use
   - RAG components tangled with unrelated code
   - File watcher calls external scripts (architectural insanity)
   - Result: Knowledge exists but isn't systematically applied

3. **Compromised Adversarial Design**
   - Evidence validation exists but inconsistently enforced
   - No clear boundaries between "enforcement" and "implementation"
   - Gaming is sometimes easier than compliance
   - Result: AI shortcuts when possible

4. **Architectural Chaos** (symptom, not root cause)
   - 30,000 LOC with deep coupling
   - No clean subsystem boundaries
   - Duplicate logic, scattered responsibilities
   - Result: Can't maintain behavioral systems reliably

**The Real Impact:**
- **For AI Agents:** Can't become project experts; no session-to-session improvement
- **For Humans:** Can't trust AI work quality; must verify everything
- **For the System:** Can't compound knowledge; standards exist but aren't discovered
- **For the Mission:** Praxis fails; theory and practice don't integrate

**Scope:**
- **Included:** Rebuild MCP server with behavioral engineering as PRIMARY architecture driver
- **Excluded:** Changing MCP protocol, index formats, or config YAML structure

**Success looks like:**
- **Behavioral:** AI queries 5-10x per task (measured), session 50 > session 1 (compounding)
- **Quality:** First-time correctness >80%, cross-session consistency maintained
- **Architecture:** Clean subsystems enable reliable behavioral enforcement
- **Trust:** Humans can trust AI work because system guarantees quality

---

## Goals & Non-Goals

### Goals (In Scope) - Ordered by Priority

**PRIMARY: Enable Praxis (Knowledge Compounding + Behavioral Reinforcement)**

1. **Query Gamification System** - The behavioral foundation
   - Prepends in 100% of search results (reinforcement at every decision point)
   - Query diversity metrics tracked (5 angles: 📖 conceptual, 📍 location, 🔧 implementation, ⭐ critical, ⚠️ troubleshooting)
   - Self-reinforcing loop: Query → Success → More querying
   - Counteracts inherited human shortcuts (efficiency pressure, impatience)

2. **Knowledge Compounding Architecture** - Two mechanisms working together
   - Standards: RAG-indexed, auto-discovered patterns (query-driven)
   - Specs: Git-preserved, deliberately-accessed history (NOT RAG-indexed)
   - File watcher triggers incremental re-indexing (<5s from save to searchable)
   - Session 50 measurably better than Session 1

3. **Adversarial Design** - Make compliance easier than gaming
   - Hidden evidence schemas (information asymmetry)
   - Multi-layer validation (field presence → type → custom → cross-field → artifact)
   - Proof artifacts required (no boolean "I did it", need actual outputs)
   - Auto-fix and clear remediation (make doing the work easier than faking it)

**SECONDARY: Clean Architecture (Enables Primary Goals)**

4. **Tool-Centric Design** - Domain abstraction pattern
   - Tools are domains (`pos_search_project`, `pos_workflow`, `pos_browser`, `pos_filesystem`)
   - `action` parameter for operations within domain
   - Intentional parameter complexity → forces standards usage → reinforces querying
   - Pluggable (auto-discover from `tools/` directory)

5. **Middleware Layer** - Cross-cutting behavioral enforcement
   - `prepend_generator`: Query gamification at every search result
   - `query_tracker`: Measure query diversity, detect behavioral drift
   - `query_classifier`: Multi-angle analysis (5 dimensions)
   - Applied consistently across all tools

6. **Config-Driven Extensibility** - Zero code changes for supported behaviors
   - Pydantic v2 schemas (type-safe, IDE autocomplete, fail-fast validation)
   - New languages via YAML (auto-install parsers in isolated venv)
   - New index types via config (IndexManager routes dynamically)
   - Behavioral thresholds configurable (query diversity targets, etc.)

**TERTIARY: Technical Quality**

7. **Performance** - <30s cold start, <100ms config load, <200ms search
8. **Reliability** - Health checks, auto-repair, graceful degradation
9. **Developer Experience** - Clear errors, auto-fix suggestions, comprehensive logging

### Non-Goals (Out of Scope)

1. **Not changing the mission** - Still enabling praxis, not just "better dev tools"
2. **Not changing content formats** - Standards/specs stay markdown, git-versioned
3. **Not changing MCP protocol** - Works with Cursor/Claude as-is
4. **Not changing index file formats** - LanceDB/DuckDB compatibility preserved
5. **Not migrating old code** - Greenfield rewrite, port only what makes sense
6. **Not multi-language server** - Python for now (ML/AI ecosystem maturity)
7. **Not distributed** - Single-server, per-project installation model
8. **Not optimizing for speed over correctness** - Systematic > fast

---

## Current State Analysis

### What Exists Today?

**mcp_server/** (30,000 LOC):
- RAG system: StandardsIndex (vector + FTS + rerank) ✅ works well
- AST Index: Tree-sitter integration ✅ works well
- Workflow engine: Phase-based execution with evidence validation ✅ works well
- Browser automation: Playwright wrapper ✅ works well
- Query prepends: Partially implemented ⚠️ inconsistent
- Config system: Dual (dataclasses + YAML) ❌ validation at runtime
- Tool registry: Hardcoded ❌ not pluggable

### What Works Well (Keep This)

- **StandardsIndex architecture** - Vector + FTS + RRF + reranking is solid
- **Workflow validation** - Evidence-based phase gates prevent behavioral drift
- **Browser session management** - Isolated Playwright sessions per AI
- **Tree-sitter integration** - Auto-install parsers in isolated venv
- **Incremental indexing** - File watcher updates indexes on change

### What's Broken (Fix This)

- **Architecture** - No subsystem boundaries, everything coupled
- **Config** - Runtime validation, dual system (dataclasses + YAML), dict access
- **Tool Registration** - Hardcoded, not pluggable
- **Query Gamification** - Inconsistent, sometimes missing
- **Error Messages** - Generic, not actionable
- **File Watcher** - Calls external scripts (architectural insanity)

### What's Missing (Add This)

- **Code Graph Traversal** - DuckDB for call graphs (who calls what?)
- **Tool Auto-Discovery** - Scan `tools/` directory, register automatically
- **Unified Config** - Single Pydantic system, validated at startup
- **Middleware Layer** - Consistent prepend generation, query tracking
- **Health Checks** - Startup validation, index status reporting

### Metrics

**Current Pain (mcp_server/):**
- Cold start: ~45 seconds (config + index load)
- Config errors: Discovered at runtime (during search)
- New tool: 5-10 files changed (hardcoded registration)
- New language: 3-5 files changed (hardcoded parser logic)
- Query diversity: ~30% (AI under-queries standards)

**Target (Ouroboros):**
- Cold start: <30 seconds
- Config errors: Startup (fail-fast)
- New tool: 1 file (drop in `tools/`)
- New language: 1 YAML change
- Query diversity: >60%

---

## Proposed Design

### Architecture

**Mission-Driven Layered Architecture:**

The architecture is organized around **enabling praxis** (knowledge compounding + behavioral reinforcement), not just technical organization. Each layer serves the behavioral engineering mission.

```
┌─────────────────────────────────────────────────────────────┐
│                      TOOLS LAYER                            │
│         (AI Agent Interface - Intentionally Complex)        │
├─────────────────────────────────────────────────────────────┤
│  pos_search_project      pos_workflow      pos_browser              │
│  pos_filesystem  get_server_info                            │
│                                                             │
│  Design: Domain abstraction with rich parameters           │
│  Purpose: Complexity → Forces standards usage → Querying   │
│  Pluggable: Auto-discover from tools/ directory            │
└──────────────────┬──────────────────────────────────────────┘
                   │ ALL tool calls flow through middleware
                   │ (NO EXCEPTIONS - behavioral engineering requires 100% coverage)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              MIDDLEWARE LAYER (THE MISSION)                 │
│      (Behavioral Engineering - Self-Reinforcing Loop)       │
├─────────────────────────────────────────────────────────────┤
│  prepend_generator:   Query gamification (progress bars,   │
│                       diversity metrics, suggestions)       │
│                       → Appears in 100% of search results   │
│                                                             │
│  query_tracker:       Logs every search                     │
│                       → Detects behavioral drift            │
│                       → Measures session-to-session         │
│                       → Enables compounding analysis        │
│                                                             │
│  query_classifier:    Multi-angle detection                 │
│                       → 📖 Conceptual, 📍 Location           │
│                       → 🔧 Implementation, ⭐ Critical        │
│                       → ⚠️ Troubleshooting                   │
│                                                             │
│  CRITICAL: If middleware fails, the request FAILS           │
│  (No silent degradation - behavioral system is mandatory)   │
└──────────────────┬──────────────────────────────────────────┘
                   │ Middleware wraps all subsystem calls
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  SUBSYSTEMS LAYER                           │
│              (Hidden Implementation - Isolated)             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  RAG Subsystem (Knowledge Compounding):                     │
│  ├─ IndexManager: Routes to correct index                  │
│  ├─ StandardsIndex: Vector+FTS+RRF+Rerank (RAG-indexed)    │
│  ├─ CodeIndex: Semantic (LanceDB) + Graph (DuckDB)         │
│  ├─ ASTIndex: Tree-sitter structural search                │
│  └─ FileWatcher: Incremental re-indexing (<5s)             │
│                                                             │
│  Workflow Subsystem (Adversarial Design):                   │
│  ├─ PhaseGates: Structural enforcement (no skipping)       │
│  ├─ EvidenceValidator: Multi-layer lie detection           │
│  ├─ HiddenSchemas: Information asymmetry                   │
│  └─ StateManager: Session persistence                      │
│                                                             │
│  Browser Subsystem:                                         │
│  └─ Playwright: Isolated sessions per AI agent             │
│                                                             │
│  Design: Zero cross-talk between subsystems                 │
│  Purpose: Clean boundaries enable reliable enforcement      │
└──────────────────┬──────────────────────────────────────────┘
                   │ All subsystems use config
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  FOUNDATION LAYER                           │
├─────────────────────────────────────────────────────────────┤
│  Config (Pydantic v2):  Type-safe, fail-fast validation    │
│  Logging:               Structured JSON, behavioral metrics │
│  Errors:                Auto-fix suggestions, clear paths   │
└─────────────────────────────────────────────────────────────┘
```

**Architectural Principles (In Priority Order):**

1. **Behavioral Engineering First**
   - Middleware layer is NON-OPTIONAL
   - All tool calls flow through behavioral reinforcement
   - If prepend generation fails → Fail the request (no silent degradation)
   - Why: The mission is praxis, not just "a better dev tool"

2. **One-Way Dependencies** (Enforced)
   - Tools → Middleware → Subsystems → Foundation
   - NEVER: Subsystems → Tools
   - NEVER: RAG → Workflow (cross-contamination)
   - Validated: Import analysis in CI/CD

3. **Config-Driven Extensibility**
   - New languages: YAML change, zero code (Tree-sitter auto-install)
   - New behavioral thresholds: Config change (query diversity targets)
   - Subsystems receive Pydantic models (no `dict["key"]` access)
   - Why: Reduces code changes, improves maintainability

4. **Adversarial Design Throughout**
   - Hidden evidence schemas (information asymmetry)
   - Multi-layer validation (field → type → custom → cross-field → artifact)
   - Fail-fast on gaming attempts (no "maybe it's okay")
   - Why: Make compliance easier than gaming

5. **Observability Built-In**
   - Query tracking: Every search logged (behavioral analysis)
   - Structured logging: JSON format, queryable with `jq`
   - Metrics: Session-to-session comparison, drift detection
   - Why: Can't improve what you can't measure

### Data Models

**Config (Pydantic v2):**
```python
class MCPConfig(BaseConfig):
    version: str = Field(pattern=r"^\d+\.\d+$")
    indexes: IndexesConfig  # RAG configuration
    workflow: WorkflowConfig
    browser: BrowserConfig
    
    @classmethod
    def from_yaml(cls, path: Path) -> "MCPConfig":
        """Load and validate (fail-fast at startup)"""
```

**Tool Definition:**
```python
@dataclass
class ToolDefinition:
    name: str
    function: Callable
    signature: ToolSignature  # Extracted from type hints
    subsystem: str  # Which subsystem it calls
```

**Query Tracking:**
```python
@dataclass
class QueryRecord:
    timestamp: datetime
    action: str  # search_standards, search_code, search_ast, find_callers, etc.
    method: str  # hybrid, vector, fts
    query: str
    session_id: str
```

### API/Interfaces

**Tool Registry (Auto-Discovery):**
```python
class ToolRegistry:
    def discover_tools(self, tools_dir: Path) -> List[ToolDefinition]:
        """Scan directory, import modules, register with FastMCP"""
    
    def register_tool(self, tool: ToolDefinition) -> None:
        """Register single tool"""
```

**Middleware Hook:**
```python
class PrependGenerator:
    def generate(self, query_record: QueryRecord) -> str:
        """Generate gamification prepend for search result"""
```

**Subsystem Interface:**
```python
class BaseSubsystem(ABC):
    def __init__(self, config: BaseConfig):
        """All subsystems receive Pydantic config"""
    
    @abstractmethod
    def health_check(self) -> HealthStatus:
        """Startup validation"""
```

### Key Behaviors

**1. Startup Sequence:**
```
1. Load config/mcp.yaml → MCPConfig.from_yaml()
2. Validate config (Pydantic, fail-fast)
3. Initialize subsystems (IndexManager, WorkflowEngine, BrowserManager)
4. Run health checks (indexes exist, parsers installed)
5. Discover tools (scan tools/ directory)
6. Register tools with FastMCP
7. Start server (stdio or HTTP)
```

**2. Search Flow (with Behavioral Engineering):**
```
pos_search_project(action="search_standards", query="how to X")
  ↓
Query Tracker records (action, method, timestamp)
    ↓
IndexManager routes to StandardsIndex
    ↓
StandardsIndex performs hybrid search (vector + FTS + RRF + rerank)
    ↓
Results returned to middleware
    ↓
Prepend Generator creates gamification prepend
    ↓
Results + prepend returned to AI agent
    ↓
AI sees: "💡 Query diversity: 3/10 | 🎯 Searched: standards | Consider: code, AST"
```

**3. Tool Auto-Discovery:**
```
tools/pos_search_project.py contains @mcp.tool() decorator
    ↓
ToolRegistry scans tools/ directory
    ↓
Imports pos_search_project.py module
    ↓
Extracts function signature from type hints
    ↓
Registers with FastMCP (no manual registration needed)
```

**4. Config-Driven Language Support:**
```yaml
# config/mcp.yaml
indexes:
  ast:
    languages:
      rust:  # NEW LANGUAGE (zero code changes)
        enabled: true
        file_extensions: [".rs"]
        parser: "tree-sitter-rust"
```
```
Server starts
    ↓
ASTIndex reads config.ast.languages
    ↓
Sees "rust" entry
    ↓
Checks if tree-sitter-rust installed
    ↓
If not: auto-install in isolated venv
    ↓
Rust files now indexed (no Python changes)
```

### Example Scenarios

**Scenario 1: User Adds Custom Tool**
```bash
# User creates: .praxis-os/ouroboros/tools/pos_custom.py
@mcp.tool()
async def pos_custom(action: Literal["do_thing"], param: str) -> Dict:
    """Custom tool for project-specific needs"""
    ...

# Server restart
# → ToolRegistry auto-discovers pos_custom.py
# → Registers with FastMCP
# → AI agent sees new tool (no code changes to registry)
```

**Scenario 2: AI Agent Discovers Call Graph**
```python
# AI queries: "Who calls build_index()?"
pos_search_project(
    action="find_callers",
    query="build_index"
)

# → DuckDB recursive CTE finds all callers
# → LanceDB ranks by semantic similarity
# → Returns: "FileWatcher.on_change() → IndexManager.rebuild() → StandardsIndex.build_index()"
```

**Scenario 3: Config Error at Startup**
```yaml
# config/mcp.yaml (invalid)
indexes:
  standards:
    vector:
      chunk_size: 50  # Below minimum (100)
```
```
Server starts
    ↓
MCPConfig.from_yaml() validates
    ↓
ValidationError: "indexes → standards → vector → chunk_size: must be >= 100"
    ↓
Server exits (fail-fast, clear error)
```

---

## Options Considered

### Option A: Refactor mcp_server/ In-Place

**Pros:**
- Preserve git history
- Incremental migration
- Lower perceived risk

**Cons:**
- 30,000 LOC of coupled code
- Estimated 4-6 weeks to untangle
- High risk of breaking existing functionality
- Cannot fix architectural issues (too deep)
- Must maintain backwards compatibility during transition

**Trade-offs:** Safety vs. timeline - "safe" refactor actually higher risk due to complexity

---

### Option B: Ground-Up Rewrite (Ouroboros) ✅ RECOMMENDED

**Pros:**
- Clean slate - implement architecture correctly from start
- Parallel development - old server keeps working
- Faster - estimated 3-4 weeks (vs. 4-6 for refactor)
- Lower risk - old server is safety net
- No backwards compat constraints

**Cons:**
- Must recreate all functionality
- Git history reset for new code
- Requires careful feature parity validation

**Trade-offs:** Speed + quality vs. git history - we choose quality

**Why This Option:**
1. Analysis showed refactor would take longer than rewrite
2. Architectural issues too deep to fix incrementally
3. Behavioral engineering needs clean middleware layer
4. Parallel development provides safety net

---

### Option C: Hybrid (Refactor Some, Rewrite Some)

**Pros:**
- Keep "good" parts (StandardsIndex, WorkflowEngine)
- Rewrite "bad" parts (config, tool registry)

**Cons:**
- Unclear boundaries - when to refactor vs. rewrite?
- Still requires untangling for extraction
- Worst of both worlds (complexity + partial history loss)

**Trade-offs:** Complexity overhead not worth partial git history preservation

---

## Risks & Mitigations

### Risk 1: Feature Parity Gaps
**Description:** Ouroboros missing functionality from mcp_server  
**Probability:** High  
**Impact:** High  
**Mitigation:**
- Create comprehensive feature checklist from mcp_server
- Build features incrementally with validation
- Keep mcp_server running until parity verified
**Contingency:** Fall back to mcp_server if critical gaps found

### Risk 2: Performance Regression
**Description:** Ouroboros slower than mcp_server  
**Probability:** Medium  
**Impact:** Medium  
**Mitigation:**
- Profile mcp_server baseline (<45s cold start)
- Set performance targets (<30s cold start)
- Performance test each phase
**Contingency:** Optimize hot paths, lazy-load subsystems

### Risk 3: Config Format Incompatibility
**Description:** Existing config files don't work with Pydantic schemas  
**Probability:** Low  
**Impact:** High  
**Mitigation:**
- Design Pydantic schemas to match existing YAML structure
- Test with actual .praxis-os/config/*.yaml files
- Create migration script if needed
**Contingency:** Support both formats during transition

### Risk 4: Tool Discovery Breaks
**Description:** Auto-discovery fails to find/register tools  
**Probability:** Medium  
**Impact:** High  
**Mitigation:**
- Comprehensive tests for discovery logic
- Clear error messages when tools fail to load
- Fallback to explicit registration
**Contingency:** Maintain hardcoded registry as backup

### Risk 5: Query Gamification Overhead
**Description:** Prepend generation slows down searches  
**Probability:** Low  
**Impact:** Low  
**Mitigation:**
- Benchmark prepend generation (<5ms target)
- Cache query stats (don't recalculate every time)
- Make it configurable (disable if needed)
**Contingency:** Disable prepends if >10ms overhead

---

## Open Questions

### Q1: Config Spec Approach
**Question:** Should we create a formal spec for unified config system, or implement directly from design docs?

**Context:** We have:
- Design doc (`.praxis-os/specs/.../unified-config-system/supporting-docs/unified-config-system-pydantic-v2.md`)
- Half-written spec targeting mcp_server/ refactor
- This Ouroboros design doc

**Options:**
- A) Create new spec via `spec_creation_v1` targeting Ouroboros greenfield
- B) Implement directly from design docs + this document (skip spec for config)

**Recommendation:** Option B - config system is well-understood, formal spec overhead not needed

**Decision Needed From:** Josh

**Deadline:** Before starting Phase 0 implementation

---

### Q2: Workflow Engine Reuse
**Question:** Can we reuse workflow engine from mcp_server/, or rewrite?

**Context:** Workflow engine (~3,000 LOC) appears well-structured with clean interfaces

**Investigation Needed:**
- Is it cleanly separable from mcp_server internals?
- Does it have dependencies on old config system?
- Is it well-tested?
- Can we copy it to ouroboros/ and adapt?

**Options:**
- A) Copy workflow/ directory wholesale, adapt imports
- B) Rewrite workflow engine from scratch
- C) Extract as shared library

**Recommendation:** Investigate in Phase 4, lean toward Option A if dependencies minimal

**Decision Needed From:** Josh (after investigation)

**Deadline:** Before Phase 4 starts

---

### Q3: Testing Strategy
**Question:** TDD (tests first) or tests after initial implementation?

**Context:**
- TDD: Slower, higher quality, better design
- Tests after: Faster iteration, may miss edge cases

**Options:**
- A) Strict TDD (write tests for each component before implementing)
- B) Hybrid (tests alongside implementation)
- C) Tests after (implement first, comprehensive test suite after)

**Recommendation:** Option B (hybrid) - write tests for config/registry (critical), implement RAG/tools first then test

**Decision Needed From:** Josh

**Deadline:** Before starting Phase 0

---

## Success Criteria

**Measurement Philosophy:** We measure product outcomes and behavioral patterns, not implementation details. Success is determined by whether the system enables praxis (continuous improvement through knowledge compounding and behavioral reinforcement).

### PRIMARY: Praxis Effectiveness (The Mission)

**1. Knowledge Compounding (Session-to-Session Improvement)**
- [ ] Session 50 demonstrably better than Session 1 (measured via first-time correctness rate)
- [ ] Standards grow organically (10+ project-specific standards created through natural work)
- [ ] Specs preserve decision history (3+ specs created, successfully referenced in later sessions)
- [ ] Cross-session consistency (same task produces same quality across sessions)

**Measurement:**
```bash
# Standards growth
ls .praxis-os/standards/development/*.md | wc -l

# First-time correctness improvement
# Session 1: ~40% tasks correct first try
# Session 50: ~80% tasks correct first try

# Spec usage
git log --grep="referenced spec" | wc -l
```

**2. Behavioral Reinforcement (Query-First Pattern)**
- [ ] Query diversity >60% (AI queries from 3+ angles: conceptual, location, implementation)
- [ ] Query frequency 5-10x per task (measured by `query_tracker`)
- [ ] Query prepends in 100% of search results (behavioral reinforcement never fails)
- [ ] "Query before implementing" pattern observable in AI behavior (fewer correction cycles)

**Measurement:**
```bash
# Query diversity (from prepend_generator logs)
grep "Angles:" .praxis-os/logs/query_tracker.log | \
  awk '{print $4}' | sort | uniq -c

# Query frequency per session
grep "search_standards" .praxis-os/logs/session-*.log | wc -l

# Correction frequency (should decrease over time)
grep -E "let me fix|actually|my mistake" .praxis-os/logs/ | wc -l
```

**3. Adversarial Design (Compliance > Gaming)**
- [ ] Evidence validation enforced 100% (no hardcoded `True` bypasses)
- [ ] Multi-layer validation catches gaming attempts (field + type + custom + cross-field + artifact)
- [ ] Auto-fix success rate >90% (compliance is easier than gaming)
- [ ] Zero `--no-verify` commits (pre-commit hooks not bypassed)

**Measurement:**
```bash
# Evidence validation enforcement
grep "checkpoint_passed = True" ouroboros/ | wc -l  # Target: 0

# Pre-commit bypass attempts
git log --grep="no-verify" --since="30 days" | wc -l  # Target: 0

# Auto-fix usage
grep "auto-fix applied" .praxis-os/logs/ | wc -l
```

### SECONDARY: Technical Quality (Enables Primary Goals)

**4. Architectural Integrity**
- [ ] Zero circular dependencies (validated by import analysis)
- [ ] Clean subsystem boundaries (RAG never imports Workflow, etc.)
- [ ] Middleware applied consistently (100% of search results have prepends)
- [ ] Tool registry auto-discovery works (drop file, restart, tool available)

**5. Configuration & Extensibility**
- [ ] Pydantic validation fail-fast (config errors at startup, not runtime)
- [ ] New language via YAML only (Python, Go, Rust tested - zero code changes)
- [ ] Config-driven behavioral thresholds (query diversity target configurable)
- [ ] Type-safe config access everywhere (no `dict["key"]` in codebase)

**6. Performance Targets**
- [ ] Cold start <30s (vs. 45s current)
- [ ] Config load <100ms (Pydantic validation)
- [ ] Search latency <200ms p95 (hybrid search: vector + FTS + RRF + rerank)
- [ ] Incremental index rebuild <5s (file watcher → searchable)

**7. Functional Completeness**
- [ ] All MCP tools migrated (pos_search_project, pos_workflow, pos_browser, pos_filesystem, get_server_info)
- [ ] Standards search (LanceDB: vector + FTS + metadata + rerank)
- [ ] Code search (LanceDB semantic + DuckDB graph traversal)
- [ ] AST structural search (Tree-sitter with auto-install)
- [ ] Workflow execution (phase gates + evidence validation + hidden schemas)
- [ ] Browser automation (Playwright with isolated sessions)

### TERTIARY: Developer Experience (Makes System Usable)

**8. Error Quality**
- [ ] Clear validation errors with field paths (e.g., "indexes → standards → vector → chunk_size: must be >= 100")
- [ ] Auto-fix suggestions in every error (tell AI how to fix, not just what's wrong)
- [ ] Startup health checks (validate all indexes, parsers, config before accepting requests)

**9. Observability**
- [ ] Structured logging (JSON format, queryable with `jq`)
- [ ] Query tracker metrics (diversity, frequency, angles used)
- [ ] Server info tool (index counts, health, version, behavioral metrics)

**10. Trust Signals (For Human Reviewers)**
- [ ] Evidence artifacts visible (not just "tests passed", but path to JUnit XML)
- [ ] Audit trail comprehensive (who did what when, with evidence)
- [ ] Reproducible builds (same inputs → same outputs)

---

### Anti-Success Criteria (What We DON'T Measure)

❌ **Prompt quality** - We build systems that work regardless of prompt craftsmanship  
❌ **Token efficiency** - We measure message reduction (behavioral), not token compression (technical)  
❌ **Lines of code** - We measure first-time correctness, not speed of code generation  
❌ **Test coverage %** - We measure cross-session consistency, not static metrics  
❌ **Number of tools** - We measure query diversity, not tool proliferation

**Why not these?** They optimize for the wrong thing. prAxIs OS optimizes for praxis: continuous improvement through knowledge compounding and behavioral reinforcement. Technical metrics are secondary, enabling the primary mission.

---

## The Behavioral Engineering System (How It Actually Works)

This section explains the **self-reinforcing behavioral loop** that makes prAxIs OS effective. Understanding this is critical to implementing Ouroboros correctly.

### The Core Loop

```
┌─────────────────────────────────────────────────────────────┐
│                  THE SELF-REINFORCING LOOP                  │
└─────────────────────────────────────────────────────────────┘

1. AI Agent faces decision → "How should I implement X?"

2. Standards teach querying → "Query before implementing"
   (This message is in EVERY standard)

3. AI queries standards → search_standards("how to implement X")

4. Search returns results + PREPEND → "💡 Queries: 3/5 | Try: 'What is X?'"
   (Gamification: progress bar, suggests more angles)

5. AI sees prepend → Reinforced to query MORE

6. AI queries from another angle → search_standards("what is X")

7. New prepend → "💡 Queries: 4/5 | Angles: 📖✓ 🔧✓ | Try location angle"

8. AI implements → Uses discovered standards

9. Implementation succeeds → AI learns "querying = success"

10. Next task → AI MORE LIKELY to query first
    (Behavioral pattern strengthened)

┌─────────────────────────────────────────────────────────────┐
│   Result: Query-first behavior becomes AUTOMATIC           │
│   Session 50 > Session 1 (pattern has compounded)          │
└─────────────────────────────────────────────────────────────┘
```

### Why This Works (Behavioral Psychology)

**1. Operant Conditioning**
- **Behavior:** Query standards before implementing
- **Reward:** Find correct answer, avoid mistakes
- **Result:** Behavior strengthens over time

**2. Gamification**
- **Progress bars:** "Queries: 4/5" (creates desire to complete)
- **Diversity metrics:** "Angles: 📖✓ 🔧⬜ ⭐⬜" (encourages exploration)
- **Suggestions:** "Try: 'Where is X implemented?'" (reduces friction)

**3. Immediate Reinforcement**
- **Timing:** Prepend appears IMMEDIATELY after query (< 100ms)
- **Frequency:** EVERY search result has prepend (100% reinforcement)
- **Consistency:** Message never changes (reliable pattern)

**4. Self-Fulfilling Prophecy**
- AI queries → Finds answer → Succeeds
- Success → AI more likely to query next time
- More queries → More success → Stronger pattern
- Pattern becomes self-sustaining

### The Three Layers of Behavioral Engineering

**Layer 1: Content Design (Standards)**
```markdown
# Every standard includes:

**Keywords for search:** [50+ terms for discoverability]

🚨 TL;DR - High keyword density at top

**Critical:** Always query before implementing

## The Problem
[What happens without this standard]

## The Standard
[Specific, actionable pattern]

## Example
[Real code from the project]

## Anti-patterns
[Common mistakes to avoid]
```

**Why this works:**
- **High keyword density** → Appears in top 3 results
- **"Query before implementing"** → Behavioral reminder in every standard
- **Specific examples** → AI can copy-paste, reducing effort
- **Anti-patterns** → Prevents mistakes without querying

**Layer 2: Query Prepends (Middleware)**
```
📊 Queries: 4/5 | Unique: 3 | Angles: 📖✓ 📍⬜ 🔧✓ ⭐⬜ ⚠️⬜
💡 Try: 'Where is X implemented?' (📍 location angle)

---

[Actual search results here]
```

**Why this works:**
- **Progress bar** → Gamification (4/5 = almost done!)
- **Diversity tracking** → Encourages multi-angle thinking
- **Concrete suggestion** → Reduces "what should I query?" friction
- **Visible at top** → Can't miss it, always reinforces

**Layer 3: Query Tracking (Observability)**
```python
# query_tracker.py logs every search:
{
  "timestamp": "2025-11-04T10:30:45Z",
  "action": "search_standards",
  "query": "how to implement X",
  "session_id": "abc123",
  "angle_detected": "implementation", # 🔧
  "result_count": 5,
  "diversity_score": 0.60  # 3 of 5 angles used
}
```

**Why this works:**
- **Measure behavioral drift** → Detect if AI stops querying
- **Session-to-session comparison** → Prove compounding (Session 50 > Session 1)
- **Intervention trigger** → If diversity drops, strengthen prepends

### Counteracting Inherited Human Shortcuts

**The Problem:** AI training data contains human shortcuts designed for biological constraints AI doesn't have.

**Human Shortcut → AI Inheritance → prAxIs OS Counter-Pattern**

| Human Pattern | Why Humans Do It | AI Inherits | prAxIs OS Solution |
|---------------|------------------|-------------|-------------------|
| "Move fast" | Energy conservation | Skips analysis | Phase gates prevent skipping |
| "Good enough" | Fatigue | Accepts suboptimal | Evidence validation enforces quality |
| "I know this" | Avoid repeated effort | Relies on training data | "Query before implementing" in every standard |
| "Ship it" | Deadline pressure | Skips tests | Pre-commit hooks block commits |
| "Ask forgiveness" | Social dynamics | Gaming validation | Multi-layer lie detection |

**How prepends counter this:**

Every search result includes: **"💡 Query liberally - you can search 10x in 30 seconds without fatigue"**

This explicitly reminds AI:
- ✅ You don't have human energy constraints
- ✅ Systematic > fast
- ✅ Query-first = correct-first
- ✅ Efficiency pressure is inherited, not real

### Why Domain Abstraction + Parameter Complexity Is Intentional

**Traditional Approach:** Many simple tools
```python
# 50 tools, each simple:
create_user()
update_user()
delete_user()
list_users()
# ... 46 more
```

**Problem:** AI can use without thinking, relies on training data, never queries standards.

**prAxIs OS Approach:** Few complex tools
```python
# 5 tools, each rich:
pos_filesystem(
    action: Literal["read", "write", "delete", "list", "move", ...],
    path: str,
    content: Optional[str] = None,
    recursive: bool = False,
    follow_symlinks: bool = False,
    encoding: str = "utf-8",
    create_parents: bool = False,
    ...  # 15+ parameters
)
```

**Effect:** AI MUST query to discover:
- What actions are available?
- Which parameters apply to which actions?
- What are the parameter groupings?
- What are the best practices?

**Result:** Parameter complexity → Forces standards query → Reinforces behavioral pattern.

**Where standards document this:**
```markdown
# .praxis-os/standards/development/filesystem-operations.md

## pos_filesystem Action Groups

### Read Operations (action="read")
Required: path
Optional: encoding, follow_symlinks

### Write Operations (action="write")
Required: path, content
Optional: encoding, create_parents, mode

### Move Operations (action="move")
Required: path, destination
Optional: overwrite, create_parents
```

### The Closing Loop: Prepends

**Every search result** starts with:
```
📊 Queries: 1/5 | Unique: 1 | Angles: 📖⬜ 📍⬜ 🔧⬜ ⭐✓ ⚠️⬜
💡 Try: 'What is the conceptual foundation of X?' (📖 conceptual angle)
```

**This is the CLOSING LOOP of the behavioral engineering system:**

1. Standards teach querying
2. AI queries standards
3. Prepend reinforces querying MORE
4. AI queries more
5. More queries = more prepends = stronger reinforcement
6. Pattern becomes automatic

**Without prepends:** Behavioral drift occurs (AI stops querying after initial success)
**With prepends:** Self-reinforcing loop sustains (AI keeps querying, pattern strengthens)

### Implementation Requirements for Ouroboros

**CRITICAL:** Behavioral engineering MUST work 100% of the time, or the entire system fails.

**Non-negotiable requirements:**

1. **Prepends in 100% of search results** - No exceptions, no failures, no "oops forgot"
2. **Query tracker logs every search** - Behavioral drift detection requires complete data
3. **Middleware between ALL tools and subsystems** - Can't reinforce if we skip the layer
4. **Standards ALWAYS include "query liberally"** - Content must teach the behavior
5. **Parameter complexity intentional** - Don't "simplify" tools; complexity forces querying
6. **Progress bars accurate** - Gamification only works if metrics are real
7. **Suggestions actionable** - "Try X" must actually work if AI copies it
8. **Fail-fast on behavioral violations** - If prepend generation fails, FAIL THE REQUEST (don't silently degrade)

**Testing behavioral engineering:**
```python
def test_prepend_in_all_results():
    """Prepends MUST appear in 100% of search results."""
    result = pos_search_project(action="search_standards", query="test")
    assert result["content"].startswith("📊 Queries:")
    assert "💡 Try:" in result["content"]
    
def test_query_tracker_logs_all_searches():
    """Every search MUST be logged for drift detection."""
    pos_search_project(action="search_standards", query="test")
    logs = read_query_tracker_logs()
    assert len(logs) > 0
    assert logs[-1]["query"] == "test"
    
def test_diversity_calculation():
    """Diversity metrics MUST be accurate for gamification."""
    # Query from 3 different angles
    pos_search_project(action="search_standards", query="what is X")  # conceptual
    pos_search_project(action="search_standards", query="how to implement X")  # implementation
    pos_search_project(action="search_standards", query="where is X")  # location
    
    metrics = get_session_diversity()
    assert metrics["angles_used"] == 3
    assert metrics["diversity_score"] == 0.60  # 3/5
```

---

## File Change Summary

### Files to Create (Ouroboros Structure)

**Config:**
- `ouroboros/config/schemas/base.py` (Enums, BaseConfig)
- `ouroboros/config/schemas/indexes.py` (RAG config)
- `ouroboros/config/schemas/workflow.py`
- `ouroboros/config/schemas/browser.py`
- `ouroboros/config/schemas/mcp.py` (Root MCPConfig)

**Tools:**
- `ouroboros/tools/pos_search_project.py`
- `ouroboros/tools/pos_workflow.py`
- `ouroboros/tools/pos_browser.py`
- `ouroboros/tools/pos_filesystem.py`
- `ouroboros/tools/get_server_info.py`

**Middleware:**
- `ouroboros/middleware/prepend_generator.py`
- `ouroboros/middleware/query_tracker.py`
- `ouroboros/middleware/query_classifier.py`

**Subsystems (RAG):**
- `ouroboros/subsystems/rag/index_manager.py`
- `ouroboros/subsystems/rag/standards_index.py`
- `ouroboros/subsystems/rag/code_index.py`
- `ouroboros/subsystems/rag/ast_index.py`
- `ouroboros/subsystems/rag/graph_index.py` (DuckDB)
- `ouroboros/subsystems/rag/watcher.py`

**Subsystems (Workflow, Browser):**
- `ouroboros/subsystems/workflow/engine.py`
- `ouroboros/subsystems/workflow/state_manager.py`
- `ouroboros/subsystems/workflow/task_parser.py`
- `ouroboros/subsystems/browser/manager.py`
- `ouroboros/subsystems/browser/playwright_impl.py`

**Utils:**
- `ouroboros/utils/logging.py`
- `ouroboros/utils/metrics.py`
- `ouroboros/utils/errors.py`

**Registry:**
- `ouroboros/registry/loader.py`

**Entry Points:**
- `ouroboros/__main__.py`
- `ouroboros/server.py`

**Tests:**
- `tests/ouroboros/` (mirror structure)

### Files to Modify
- `.praxis-os/.mcp_server_state.json` (config path update when switching)

### Files to Delete
- None (mcp_server/ stays as archive until validated)

---

## Testing Approach

### Unit Tests
- **Config:** Pydantic model validation (all Field constraints, cross-field validators)
- **Registry:** Tool discovery (find modules, extract signatures, register)
- **Middleware:** Prepend generation (query diversity, formatting)
- **RAG:** IndexManager routing, StandardsIndex search methods
- **Coverage Target:** ≥90% for config, registry, middleware

### Integration Tests
- **Config Loading:** Load actual .praxis-os/config/*.yaml files
- **Tool Discovery:** Scan actual tools/ directory
- **End-to-End Search:** Query → middleware → RAG → results + prepend
- **Subsystem Initialization:** Config → IndexManager → StandardsIndex → search works

### Performance Tests
- **Config Load:** <100ms (p95)
- **Cold Start:** <30s (full server startup)
- **Search Latency:** <200ms (hybrid search)
- **Incremental Update:** <5s (single file change)

### Validation Tests
- **Feature Parity:** All mcp_server tools replicated
- **Config Compatibility:** Existing YAML files work
- **Query Gamification:** Prepends appear in 100% of searches

---

## Related Documents

### Analysis Documents
- `.praxis-os/workspace/analysis/2025-11-03-complete-mcp-server-architecture.md` - Full mcp_server audit
- `.praxis-os/workspace/analysis/2025-11-03-rag-architecture-refactor-plan.md` - Clean RAG design goals

### Design Documents
- `.praxis-os/specs/review/2025-11-03-unified-config-system/supporting-docs/unified-config-system-pydantic-v2.md` - Pydantic config design
- `.praxis-os/workspace/requirements/2025-11-04-rag-implementation-requirements.md` - Multi-index RAG (LanceDB + DuckDB)

### Standards
- `universal/standards/documentation/design-document-structure.md` - Design doc structure (this follows it!)
- `.praxis-os/standards/development/dev-vs-distribution-workflow.md` - Development workflow

---

## Appendix: Prior Art & Research

### Behavioral Engineering Research
- **Query Gamification:** Inspired by video game achievement systems (progress bars, diversity metrics)
- **Goodhart's Law Prevention:** Workflow evidence hidden to prevent optimization for validation over completion

### Architecture Inspiration
- **Hexagonal Architecture:** Ports and adapters (tools = ports, subsystems = adapters)
- **Domain-Driven Design:** Subsystems as bounded contexts (RAG never talks to Workflow)
- **Plugin Architecture:** VS Code extension model (drop file in directory, auto-discovered)

### Technology Choices
- **Pydantic v2:** FastAPI, LangChain use it successfully
- **FastMCP:** Official MCP Python framework
- **LanceDB + DuckDB:** "Best of both worlds" for code search (semantic + graph)

---

**Version:** 1.0  
**Created:** 2025-11-04  
**Next Step:** Human review & approval, then `spec_creation_v1` workflow


