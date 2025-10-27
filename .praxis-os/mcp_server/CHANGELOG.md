# Agent OS MCP Server - Changelog

All notable changes to the Agent OS MCP server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] - 2025-10-24

### Added - Query Gamification System

**Feature**: Behavioral reinforcement system that enhances `search_standards()` with dynamic, context-aware feedback to sustain query-first behavior.

**Components**:
- **QueryClassifier**: Keyword-based classification into 5 query angles (definition, location, practical, best_practice, error_prevention)
- **QueryTracker**: Per-session statistics tracking (total/unique queries, angles covered, query history)
- **PrependGenerator**: Dynamic feedback messages with progress counters, angle coverage visualization, and contextual suggestions
- **SessionIDExtractor**: Dynamic countdown timer (20s→19s→...→5s floor) for natural task boundary detection (~95% accuracy)

**Key Benefits**:
- 📊 Real-time progress tracking (Queries: X/5 | Unique: Y)
- 📖📍🔧⭐⚠️ Visual angle coverage indicators
- 💡 Smart suggestions based on uncovered angles
- 🎉 Completion detection (5+ queries, 4+ angles)
- ⚡ Exceptional performance (0.02ms p95 latency, 68% under token budget)
- 🔒 XSS prevention (HTML tag sanitization)

**Integration**: Seamlessly integrated into `search_standards()` MCP tool with graceful degradation and full backward compatibility.

**Testing**: 117 tests across unit, integration, performance, and security (98.3% pass rate).

**Traceability**: Implements requirements FR-001 through FR-013, NFR-P1 through NFR-P4, NFR-S1.

---

## [Unreleased] - 2025-10-13

### Fixed - workflow_creation_v1 (Critical Directory Naming Bug)

**Problem**: workflow_creation_v1 created workflows with incorrect directory names using dashes (e.g., `standards-creation-v1`) instead of underscores (e.g., `standards_creation_v1`). Additionally, it hardcoded `universal/workflows/` path which only exists in the Agent OS repo, breaking workflow creation for all standard installations.

**Root Cause**: 
1. Phase 2, Task 1 used `target_workflow_name` (from `name` field with dashes) instead of `target_workflow_type` (from `workflow_type` field with underscores) for directory creation
2. All task files hardcoded `universal/workflows/` instead of `.praxis-os/workflows/`

**Impact**: 
- Generated workflows were not discoverable by workflow engine (looks for `{workflow_type}/` with underscores)
- Workflow engine fell back to auto-generated placeholder metadata instead of loading actual metadata.json
- Complete workflow failure - unusable output
- Only works in Agent OS repo, breaks everywhere else

**Fixes Applied**:

1. **Directory Naming** (`.praxis-os/workflows/workflow_creation_v1/phases/2/task-1-create-workflow-directory.md`)
   - Changed from `{target_workflow_name}` to `{target_workflow_type}` for directory path
   - Added explicit constraint: "directory name MUST exactly match the `workflow_type` field (which uses underscores, not dashes)"
   - Updated examples to show underscore usage: `payment_processing_v1`

2. **Path Correction - All Task Files**
   - `.praxis-os/workflows/workflow_creation_v1/phases/1/task-5-prepare-workspace.md`: Changed workflow_root path
   - `.praxis-os/workflows/workflow_creation_v1/phases/2/task-1-create-workflow-directory.md`: Changed directory creation path and context
   - `.praxis-os/workflows/workflow_creation_v1/phases/2/task-8-verify-scaffolding.md`: Changed verification path and evidence examples
   - `.praxis-os/workflows/workflow_creation_v1/supporting-docs/design-summary.md`: Changed output path example
   - `.praxis-os/workflows/workflow_creation_v1/supporting-docs/workflow-definition.yaml`: Changed task purpose documentation
   - ALL references to `universal/workflows/` replaced with `.praxis-os/workflows/`

3. **Workflow Philosophy Update**
   - Workflows are ALWAYS created in `.praxis-os/workflows/` locally
   - Manual copy to `universal/workflows/` only when distributing as part of Agent OS repo
   - Build local, distribute manually

**Expected Result**: 
- Workflows created with correct underscore naming matching `workflow_type` field
- Works in all installations (not just Agent OS repo)
- Workflow engine successfully loads metadata.json
- No more directory/workflow_type mismatch errors

**Testing Required**:
- Re-run workflow_creation_v1 with design-spec.md → verify directory name uses underscores
- Verify workflow engine loads metadata (not fallback)
- Test in non-Agent-OS repo environment

---

### Fixed - workflow_creation_v1 (Critical Content Generation Bug)

**Problem**: workflow_creation_v1 generated non-functional workflow stubs (44-line files with generic placeholders instead of 100-170 line actionable task files). First production test (standards-creation-v1) revealed multi-layer extraction/generation/validation failures.

**Root Cause**: Phase 0 extraction only captured basic task metadata (name, purpose) but failed to extract detailed instructions, examples, and validation criteria from design documents. Phase 4 generation used weak fallbacks that produced generic "Execute the required actions" stubs. Phase 5 validation checked structure but not content quality.

**Impact**: Every workflow generated by workflow_creation_v1 was unusable by AI agents, requiring manual rewrite. This broke the meta-workflow foundation that all future workflows depend on.

**Fixes Applied**:

1. **Phase 0 Extraction Enhancement** (`.praxis-os/workflows/workflow_creation_v1/phases/0/task-3-extract-from-design.md`)
   - Added Step 6B: Deep extraction of task detail
   - Extracts `steps_outline` (3-8 steps per task from design doc analysis)
   - Extracts `examples_needed` (2-3 example types per task)
   - Extracts `validation_criteria` (3-5 specific quality checks per task)
   - Extracts `task_context` (rich paragraph explaining rationale and constraints)
   - Provides intelligent fallback defaults when design doc lacks detail

2. **Phase 4 Generation Enhancement** (`.praxis-os/workflows/workflow_creation_v1/phases/4/task-3-generate-task-files.md`)
   - Enhanced fallback logic for steps section with intelligent inference
   - Infers logical steps from task_purpose action verbs (write → draft/review/finalize)
   - Adds tool-specific steps based on commands_needed array
   - Includes domain expertise retrieval (🔍 MUST-SEARCH markers) when domain_focus present
   - Generates minimum 3-5 steps with command language markers
   - Enhanced examples section fallback to generate 2 default examples (success + failure case)
   - Infers example content from task type (validation/writing/implementation/parsing)

3. **Phase 5 Content Quality Validation** (NEW: `.praxis-os/workflows/workflow_creation_v1/phases/5/task-9-audit-content-quality.md`)
   - Detects generic placeholder patterns ("Execute the required actions", "Task completed successfully")
   - Validates step detail (minimum 3 steps, actionable content, tool markers)
   - Validates examples present (concrete, not placeholders)
   - Validates quality checks specific (minimum 3, measurable criteria)
   - Validates RAG integration for domain-focused tasks
   - Validates file sizes (target: 100-170 lines, flags < 60 as stubs)
   - Generates comprehensive content quality report
   - FAILS validation if generic stubs detected (prevents bad workflows from passing)
   - Added to Phase 5 phase.md and validation gate

4. **Template Documentation Enhancement** (`universal/templates/workflow-definition-template.yaml`)
   - Changed `steps_outline`, `examples_needed`, `validation_criteria` from "Optional" to "🔥 STRONGLY RECOMMENDED"
   - Added detailed guidance: WITHOUT THIS → generic stubs, WITH THIS → 100-170 line actionable tasks
   - Added ✅ GOOD PRACTICE and ❌ BAD PRACTICE examples for each field
   - Explained impact on Phase 4 generation quality

**Expected Results After Fixes**:
- Task files: 100-170 lines (vs current 44 lines)
- Steps per task: 8+ detailed steps (vs current 1 generic step)
- Examples per task: 2+ concrete examples (vs current 0)
- Quality checks: 10+ specific criteria (vs current 1 generic)
- RAG queries: 3+ for domain tasks (vs current 0)
- Command language: 80%+ coverage with tool markers
- **AI agents can execute generated workflows without human intervention**

**Testing Required** (Pending):
- Test Case 1: Re-generate standards-creation-v1 with design-spec.md and validate output quality
- Test Case 2: Simple workflow test (3 phases, 5 tasks) to verify fallback logic
- Content quality validation must pass for all generated workflows

**Analysis Documents**:
- `.praxis-os/specs/workflow-creation-v1-comprehensive-analysis-2025-10-13.md` (full verification)
- `.praxis-os/specs/workflow-creation-v1-implementation-gap-analysis-2025-10-13.md` (original analysis)

**Traceability**: This fix is critical because workflow_creation_v1 is the meta-workflow that generates all other workflows. A broken workflow generator produces broken workflows at scale. These fixes restore the foundational automation layer for the entire Agent OS workflow system.

---

## [1.6.0] - 2025-10-11

### Added
- **Dual-Transport Architecture**: Multi-agent collaboration with zero conflicts
  - **PortManager** (`mcp_server/port_manager.py`): Dynamic port allocation (4242-5242 range)
  - **ProjectInfoDiscovery** (`mcp_server/project_info.py`): Dynamic project metadata discovery
  - **TransportManager** (`mcp_server/transport_manager.py`): Orchestrates stdio + HTTP transports
  - **State file** (`.praxis-os/.mcp_server_state.json`): Server connection info for sub-agents
  - **Auto-discovery utility** (`mcp_server/sub_agents/discovery.py`): Sub-agents find server automatically

- **CLI Arguments**: 
  - `--transport {stdio,http,dual}`: Choose transport mode (default: stdio)
  - `--log-level {DEBUG,INFO,WARNING,ERROR}`: Configure logging (default: INFO)

- **Configuration Fields** (`config.yaml`):
  - `mcp.http_port`: Preferred HTTP port (default: 4242)
  - `mcp.http_host`: HTTP bind address (default: 127.0.0.1)
  - `mcp.http_path`: HTTP endpoint path (default: /mcp)

- **Sub-Agent Integration**:
  - `mcp_server/sub_agents/discovery.py`: Server discovery with PID validation
  - `mcp_server/sub_agents/mcp_client_example.py`: Working end-to-end example
  - Config helpers for Cline, Aider, and Python SDK clients

- **Server Info Tool** (`get_server_info`):
  - Returns server version, uptime, transport mode, PID
  - Returns project name, root path, Git metadata
  - Returns capabilities (tools count, RAG/workflow/browser status)

- **Comprehensive Testing**:
  - **Unit tests**: 115 tests total, 98% average coverage
    - PortManager: 19 tests, 100% coverage
    - ProjectInfoDiscovery: 26 tests, 98% coverage
    - TransportManager: 19 tests, 98% coverage
    - Config HTTP fields: 15 tests, 100% coverage
    - Server info tools: 18 tests, 100% coverage
    - Discovery utility: 28 tests, 94.67% coverage
    - Client example: 17 tests, 68.54% coverage
  - **Integration tests**: 27 tests
    - Dual-transport mode: 4 tests
    - Multi-project isolation: 4 tests
    - Error scenarios: 12 tests (port exhaustion, stale PIDs, corruption, etc.)
    - Thread safety: 7 tests (concurrent reads, performance, deadlocks)

- **Documentation**:
  - `.praxis-os/specs/2025-10-11-mcp-dual-transport/`: Complete feature specification
  - `IDE-CONFIGURATION.md`: Setup guide for Cursor, Windsurf, Claude Desktop
  - `THREAD-SAFETY.md`: Thread safety analysis and design limitations
  - Updated `README.md` with dual-transport architecture section

### Changed
- **Entry Point** (`__main__.py`):
  - Added `argparse` for CLI argument parsing
  - Added `find_agent_os_directory()` with multiple fallback paths
  - Integrated PortManager, TransportManager, and ProjectInfoDiscovery
  - Atomic state file creation and cleanup on shutdown
  - Enhanced error messages with remediation steps

- **ServerFactory** (`server/factory.py`):
  - Accepts `project_discovery` and `transport_mode` parameters
  - Passes these to tool registration for `get_server_info` tool

- **Tool Registration** (`server/tools/__init__.py`):
  - Added `register_server_info_tools()` to tool registry
  - Always registers `get_server_info` tool

- **.gitignore**: 
  - Added `.praxis-os/.mcp_server_state.json` (ephemeral state file)

### Performance
- **Port allocation**: < 50ms average (finds available port and binds)
- **State file operations**: < 5ms for reads, < 10ms for atomic writes
- **Concurrent reads**: p95 response time < 200ms with 20 concurrent threads
- **No deadlocks**: 100 operations in < 1s under high load

### Architecture
- **Transport modes**:
  - `stdio`: Single IDE, no sub-agents (default, backwards compatible)
  - `http`: HTTP only, no IDE connection
  - `dual`: **Recommended** - IDE via stdio, sub-agents via HTTP

- **Multi-project support**:
  - Zero-conflict deployment: each project gets unique port
  - Auto-port allocation: 4242-5242 range with increment on conflict
  - Independent state files: `.praxis-os/.mcp_server_state.json` per project

- **Thread safety**:
  - Single-writer, multiple-reader pattern per project
  - All read operations fully thread-safe
  - FastMCP shared instance handles concurrent stdio + HTTP requests
  - Atomic state file writes prevent corruption

### Backwards Compatibility
- **No breaking changes**: 
  - Existing `.cursor/mcp.json` configs work without modification
  - Omitting `--transport` defaults to stdio-only mode
  - All existing IDE integrations continue to function
  - Upgrade is opt-in via `--transport dual` argument

### Known Limitations
- **Port allocation race conditions**: Multiple threads may select same port before binding (actual socket bind fails cleanly)
- **Concurrent writes**: Not designed for multiple servers writing to same state file (single server per project is the intended usage)
- **PID validation**: Windows requires psutil for accurate checking (conservative fallback assumes alive)

See `.praxis-os/specs/2025-10-11-mcp-dual-transport/THREAD-SAFETY.md` for detailed analysis.

---

## [1.5.0] - 2025-10-08

### Added
- **Gitignore Standards**: Canonical source for .gitignore requirements
  - `universal/standards/installation/gitignore-requirements.md` (151 lines)
  - Documents all 6 required patterns with rationale and impact
  - Explains ~2.7GB of ephemeral files prevented from being committed
  - Provides verification commands and historical context
  - Single source of truth for installation and upgrade workflows

- **Installation Step 04**: Gitignore configuration
  - `installation/04-gitignore.md` (322 lines)
  - Reads patterns dynamically from standards (no hardcoding)
  - Appends missing entries to target .gitignore
  - Prevents committing: .cache/ (1.3GB), .backup.* (1.3GB), venv/ (100MB)
  - Git check-ignore verification

- **Upgrade Workflow Phase 2 Task 3**: Gitignore update
  - `workflows/agent_os_upgrade_v1/phases/2/task-3-update-gitignore.md` (147 lines)
  - Compares target .gitignore with standards requirements
  - Appends missing entries automatically during upgrade
  - Warns if ephemeral files already committed

### Changed
- **Installation Numbering**: Steps renumbered to accommodate gitignore
  - `04-venv-mcp.md` → `05-venv-mcp.md`
  - `05-validate.md` → `06-validate.md`
  - Total installation steps: 5 → 6
  - Updated all cross-references in 00-START.md, 03-cursorrules.md, README.md

- **Upgrade Workflow Phase 2**: Task additions and renumbering
  - Added `task-3-update-gitignore.md` (new)
  - Renumbered `task-3-verify-checksums` → `task-4-verify-checksums`
  - Phase timing: 45s → 60s (+15s for gitignore)
  - Total tasks in Phase 2: 3 → 4
  - Updated phase.md metadata

- **Repository .gitignore**: Added missing critical patterns
  - `.praxis-os.backup.*` - upgrade backups (1.3GB+)
  - `.praxis-os/.upgrade_lock` - upgrade lock file
  - Prevents accidentally committing 665 backup files (discovered during testing)

### Fixed
- **CRITICAL SAFETY**: Removed dangerous `--delete` from user-writable directories
  - **Location**: `workflows/agent_os_upgrade_v1/phases/2/task-2-actual-upgrade.md`
  - **Issue**: `rsync --delete` on `.praxis-os/usage/` would delete user docs
  - **Fix**: Changed to `rsync -av` (NO --delete) for usage directory
  - **Added**: Directory classification documentation (system-managed vs user-writable)
  - **Impact**: Prevents data loss during upgrades

- **Documentation**: Updated installation/SYSTEM-SUMMARY.md
  - File structure now shows all 7 steps (00-06)
  - Sequential chain updated with gitignore step
  - Checkpoint system renumbered correctly
  - Issue table updated with new fix locations

### Architecture
- **Single Source of Truth Pattern**: Implemented for gitignore requirements
  - Installation reads from: `.praxis-os/standards/universal/installation/gitignore-requirements.md`
  - Upgrade reads from: `.praxis-os/standards/universal/installation/gitignore-requirements.md`
  - Zero hardcoded lists in workflows (DRY principle)
  - To add new pattern: Edit ONE file, both flows automatically pick it up
  - Versioned and auditable in git

### Performance
- **Installation Time**: ~5-10 minutes (unchanged, gitignore step < 2min)
- **Upgrade Time**: 3min 20s → 3min 35s (+15s for gitignore check)

### Documentation
- Updated `installation/README.md` with 7-step structure
- Updated `installation/00-START.md` with step 04 gitignore
- Updated `installation/SYSTEM-SUMMARY.md` with new architecture
- Updated `workflows/agent_os_upgrade_v1/README.md` with Phase 2 changes

---

## [1.4.0] - 2025-10-07

### Added
- **Modular Architecture**: Complete refactoring to modular structure
  - `models/` module: Data structures organized by domain (config, workflow, rag)
  - `config/` module: ConfigLoader and ConfigValidator for single source of truth
  - `monitoring/` module: Refactored file watcher with dependency injection
  - `server/` module: ServerFactory and modular tool registration
  - Sub-agent infrastructure ready for future expansion

### Changed
- **Configuration Management**: New ConfigLoader with graceful fallback
  - Validates all paths before server creation
  - Supports custom, partial, and invalid configs
  - Clear error messages for configuration issues
- **Dependency Injection**: All components created via ServerFactory
  - No hardcoded paths in any module
  - Easy to test with mocked dependencies
  - Clean separation of concerns
- **Tool Registration**: Modular tool organization
  - Tools grouped by domain (rag_tools, workflow_tools)
  - Tool count monitoring (warns at >20 tools)
  - Selective loading via `enabled_tool_groups` config
- **Entry Point**: __main__.py rewritten to use new architecture
  - Uses ConfigLoader, ConfigValidator, ServerFactory
  - Maintains backward compatibility with existing configs

### Removed
- `agent_os_rag.py` (984 lines): Replaced by modular architecture
- `models.py` (410 lines): Replaced by models/ module
- Old `_load_path_config()` function: Replaced by ConfigLoader
- Old `AgentOSFileWatcher`: Replaced by monitoring/watcher.py with DI

### Migration
- **No breaking changes**: All existing functionality preserved
- All 8 MCP tools work identically (1 RAG + 7 workflow)
- All 33 tests passing (28 unit + 5 integration)
- Existing config.json files work unchanged
- Import updates required for developers (see migration guide)

---

## [1.3.1] - 2025-10-06

### Fixed
- **Phase 0 Workflows Now Work Correctly**: Fixed hardcoded initial phase bug
  - **Bug**: Workflows starting at Phase 0 were incorrectly initialized to Phase 1
  - **Impact**: Phase 0 was completely skipped, breaking workflows like `test-generation-js-ts`
  - **Fix**: Dynamic phase detection in `state_manager.py` and `workflow_engine.py`
    - `StateManager.create_session()` now detects starting phase (0 or 1)
    - Checks if `phases/0/` directory exists in workflow structure
    - Defaults to Phase 1 for backwards compatibility
    - `WorkflowEngine.start_workflow()` uses `state.current_phase` instead of hardcoded 1
  - **Testing**: Added 7 new unit tests for Phase 0 detection and execution
  - **Backwards Compatible**: Workflows without Phase 0 still start at Phase 1

**Before (Broken):**
```python
start_workflow("test-generation-js-ts", "file.ts")
# Returns:
{
  "current_phase": 1,  # ❌ Should be 0
  "phase_content": {"phase_number": 1, ...}  # Skips Phase 0
}
```

**After (Fixed):**
```python
start_workflow("test-generation-js-ts", "file.ts")
# Returns:
{
  "current_phase": 0,  # ✅ Correct
  "phase_content": {"phase_number": 0, ...}  # Phase 0 content
}
```

---

## [1.3.0] - 2025-10-06

### Added
- **`get_task` MCP Tool (Horizontal Scaling)**: New tool for retrieving individual tasks
  - Signature: `get_task(session_id, phase, task_number)`
  - Returns complete task content with execution steps
  - Follows meta-workflow principle: one task at a time
  - Ensures complete content via 50-chunk RAG retrieval
  - Sorted chunks maintain proper content order

- **Update Documentation (Critical)**: Comprehensive guides to prevent update mistakes
  
  **Content Updates (No Restart Required):**
  - **`universal/usage/agent-os-update-guide.md`**: Content update instructions
    - Correct source location (`universal/` not `.praxis-os/`)
    - **File watcher auto-detects `.md`/`.json` changes** - no manual action needed
    - RAG index rebuilds automatically in ~10-30 seconds
    - **No server restart required** for content updates
    - Example update scripts with validation
    - Version tracking and rollback procedures
    - Troubleshooting common mistakes
  
  **Server Updates (Restart Required):**
  - **`universal/usage/mcp-server-update-guide.md`**: MCP server update instructions
    - **Server code updates (.py files) REQUIRE restart**
    - File watchers only monitor content files, not Python code
    - Package vs source installation updates
    - Dependency management
    - Breaking changes and migration guides
    - Production deployment strategies
  
  **Standards & Warnings:**
  - **`universal/standards/installation/update-procedures.md`**: Official update standards
    - Formal requirements distinguishing content vs server updates
    - Content updates: automatic via file watcher
    - Server updates: manual restart required
    - Validation and compliance checklists
    - Incident response procedures
  - **`CRITICAL_UPDATE_WARNING.md`**: High-visibility warning at repo root
    - Clear DO/DON'T comparison for content updates
    - Explains file watcher auto-detection
    - Emergency recovery steps
    - Quick reference for developers

### Changed
- **`get_current_phase` Now Returns Task Metadata Only**: Breaking change in response structure
  - `phase_content.tasks` now contains only: `task_number`, `task_name`, `task_file`
  - No longer includes full task `content` or `steps` (too much context)
  - Added message: "Use get_task(session_id, phase, task_number) to retrieve full task content"
  - General phase guidance still included in `content_chunks`

### Why This Change?

**Meta-Framework Alignment: Horizontal Scaling**

**Before (v1.2.3):** Returned all tasks at once
```typescript
get_current_phase() → {
  tasks: [
    { task_1: "...", content: "...", steps: [...] },  // 2KB
    { task_2: "...", content: "...", steps: [...] },  // 2KB
    { task_3: "...", content: "...", steps: [...] },  // 2KB
    ...
  ]  // 10KB total - attention overwhelm ❌
}
```

**After (v1.3.0):** Get task list, then retrieve one task at a time
```typescript
// Step 1: Get overview
get_current_phase() → {
  tasks: [
    { task_number: 1, task_name: "Console Detection", task_file: "..." },
    { task_number: 2, task_name: "Logger Analysis", task_file: "..." }
  ]  // Just metadata ~200 bytes ✅
}

// Step 2: Get first task
get_task(session_id, phase=1, task_number=1) → {
  content: "...",  // Complete task markdown
  steps: [...]      // Execution steps
}  // ~1-2KB focused context ✅

// Step 3: Execute, then get next task
get_task(session_id, phase=1, task_number=2) → { ... }
```

**Benefits:**
- ✅ Focused attention (one task at a time)
- ✅ Token efficient (only load what's needed now)
- ✅ Sequential execution enforced by API
- ✅ Honors horizontal scaling (small chunks ≤100 lines)
- ✅ Complete task content guaranteed

### Migration Guide

**Old pattern (v1.2.3):**
```python
phase = get_current_phase(session_id)
for task in phase['phase_content']['tasks']:
    # task already has full content and steps
    execute_steps(task['steps'])
```

**New pattern (v1.3.0):**
```python
phase = get_current_phase(session_id)
for task_meta in phase['phase_content']['tasks']:
    # Get full task content
    task = get_task(session_id, phase['current_phase'], task_meta['task_number'])
    # Now execute steps
    execute_steps(task['steps'])
```

---

## [1.2.3] - 2025-10-06

### Added
- **Structured Task Data in Phase Content**: MCP tools now return executable task data
  - `phase_content.tasks` array with structured task information
  - Each task includes task_name, task_number, task_file, content, and steps
  - Steps include command, description, type, and evidence_required
  - Extracts 🛑 EXECUTE-NOW commands from workflow files
  - Extracts 📊 COUNT-AND-DOCUMENT evidence markers
  - Supports 🔍 QUERY-AND-DECIDE decision points

### Changed
- **RAG-Based Task Retrieval**: Leverages existing workflow index (v1.2.1)
  - Dual RAG queries: general methodology + task-specific commands
  - Groups RAG chunks by task file
  - Extracts commands via regex patterns
  - No direct file reading required
  - Pure MCP interface for workflow execution

### Why This Enhancement?
**Before:** Agent had to read workflow task files directly from filesystem
```typescript
// Required file access
const task = await read_file('.praxis-os/workflows/.../task-1-console.md');
// Manual parsing needed
const commands = parseMarkdown(task);
```

**After:** Agent gets structured tasks from MCP
```typescript
// Pure MCP, no file access
const session = await start_workflow(...);
const tasks = session.phase_content.tasks;
// Structured data ready to execute
for (const step of tasks[0].steps) {
  if (step.type === "execute_command") {
    await run_terminal_cmd(step.command);
  }
}
```

---

## [1.2.2] - 2025-10-06

### Fixed
- **Hardcoded Workflow Paths Bug**: MCP server now reads paths from `config.json`
  - Fixes workflow metadata not loading in consuming projects with custom structures
  - Eliminates need for symlink workaround
  - Backward compatible - falls back to defaults if no config

### Added
- **config.json Path Configuration**: Customize directory paths for standards, usage, workflows
  - `rag.standards_path` - Path to technical standards
  - `rag.usage_path` - Path to usage guides  
  - `rag.workflows_path` - Path to workflow metadata
  - Paths resolved relative to project root
  - Partial configuration supported (specify only what you need)

- **Integration Tests**: Comprehensive test suite for custom path configuration
  - Tests default paths (no config)
  - Tests custom paths from config.json
  - Tests partial configuration
  - Tests invalid config fallback
  - Tests workflow metadata loading from custom paths

### Changed
- **Path Resolution**: All paths now resolved through `_load_path_config()`
- **File Watcher**: Uses config paths for index rebuild

### Documentation
- **CONFIG_JSON_GUIDE.md**: Complete guide for configuring custom paths
  - Common directory structures
  - Path resolution examples
  - Verification steps
  - Migration guide from symlinks

### Why This Fix?
**Before:** Consuming projects had to use symlinks or match exact directory structure
```bash
# Required workaround
ln -s ../.praxis-os-source/workflows .praxis-os/universal/workflows
```

**After:** Configure paths in config.json
```json
{
  "rag": {
    "workflows_path": ".praxis-os-source/workflows"
  }
}
```

---

## [1.2.1] - 2025-10-06

### Added
- **Workflows Directory RAG Indexing**: Workflow metadata now indexed for semantic discovery
  - Added `workflows_path` parameter to `IndexBuilder`
  - File watcher monitors `universal/workflows/` directory for changes
  - JSON files (metadata.json) now trigger index rebuilds
  - AI agents can discover workflows through semantic search

- **Comprehensive Workflow Standards Documentation**: Three indexed standards documents
  - `workflow-system-overview.md` - Complete workflow system guide (400+ lines)
  - `mcp-rag-configuration.md` - MCP RAG setup with workflows (400+ lines)
  - `workflow-metadata-standards.md` - Metadata creation standards (500+ lines)

### Changed
- **File Watcher Enhancement**: Now handles both `.md` and `.json` files
- **Directory Structure**: Updated paths to use `universal/` directory
  - `universal/standards/` - Technical standards (indexed)
  - `universal/workflows/` - Workflow metadata (indexed)
  - `universal/usage/` - Usage guides (indexed)

### Updated
- **MCP Usage Guide**: Added workflow discovery examples
- **IndexBuilder**: All calls now include workflows_path parameter
- **Server Initialization**: Passes workflows_path throughout system

### Why This Feature?
Before: AI agents couldn't discover workflows or understand MCP configuration
After: Complete workflow system discoverable through semantic search

**Discovery Flow:**
```python
# Discover workflows
result = await search_standards("What workflows are available for testing?")
# Returns: Workflow metadata and standards docs

# Learn configuration
result = await search_standards("How do I configure MCP RAG for workflows?")
# Returns: Complete configuration guide
```

---

## [1.2.0] - 2025-10-06

### Added
- **Workflow Overview in `start_workflow`**: Enhanced workflow initialization with comprehensive metadata
  - Returns complete workflow structure upfront (total phases, phase names, purposes)
  - Eliminates need for separate `get_workflow_state()` call to understand workflow
  - Includes estimated effort, key deliverables, and validation criteria for each phase
  - Backward compatible: works with or without metadata.json files
  - Auto-generates fallback metadata for existing workflows

### Why This Feature?
AI agents previously needed two API calls to understand workflow structure:
1. `start_workflow()` - Get session and Phase 1 content
2. `get_workflow_state()` - Learn total phases and structure

Now agents get complete overview immediately, enabling better planning and progress tracking.

### New Response Structure
```json
{
  "session_id": "uuid",
  "workflow_type": "test_generation_v3",
  "workflow_overview": {
    "total_phases": 8,
    "estimated_duration": "2-3 hours",
    "primary_outputs": ["test files", "coverage report"],
    "phases": [
      {
        "phase_number": 0,
        "phase_name": "Setup",
        "purpose": "Initialize test environment",
        "estimated_effort": "10 minutes",
        "key_deliverables": ["Test framework configured"],
        "validation_criteria": ["Test runner executes"]
      }
      // ... all phases
    ]
  },
  "current_phase": 1,
  "phase_content": {...}
}
```

### Metadata Files
- Created `universal/workflows/test_generation_v3/metadata.json`
- Created `universal/workflows/production_code_v2/metadata.json`
- See `WORKFLOW_METADATA_GUIDE.md` for creating metadata for new workflows

---

## [1.1.0] - 2025-10-06

### Added
- **`current_date` Tool**: New MCP tool to prevent AI date errors
  - Returns current date/time in ISO 8601 format (YYYY-MM-DD)
  - Provides multiple formatted outputs (spec directories, headers, readable)
  - Includes day of week, month, year, and unix timestamp
  - Solves systematic AI date error problem per Agent OS date policy
  - Example use: Create specifications with correct dates, proper directory naming

### Why This Feature?
AI assistants consistently make date errors:
- Using wrong dates (e.g., 2025-01-30 when current is 2025-10-06)
- Inconsistent date formats across documentation
- Hardcoded dates instead of getting current date

The `current_date` tool provides a single source of truth for the current date, ensuring all AI-generated content uses correct, consistently-formatted dates.

### Tool Documentation
```python
# Usage
result = await current_date()
# Returns:
{
  "iso_date": "2025-10-06",  # Primary format for all uses
  "iso_datetime": "2025-10-06T14:30:00.123456",
  "day_of_week": "Monday",
  "month": "October",
  "year": 2025,
  "unix_timestamp": 1728226200,
  "formatted": {
    "spec_directory": "2025-10-06-",  # For directory naming
    "header": "**Date**: 2025-10-06",  # For markdown headers
    "readable": "October 06, 2025"
  },
  "usage_note": "Use 'iso_date' (YYYY-MM-DD) for all specifications, directories, and headers per Agent OS date policy"
}
```

---

## [1.0.0] - 2025-10-05

### Added
- **Core MCP Server**: Main entry point with FastMCP integration
- **RAG Engine**: LanceDB vector search with 90%+ retrieval accuracy
- **Workflow Engine**: Phase-gated workflows with checkpoint validation
- **State Manager**: Workflow state persistence and resume capability
- **File Watcher**: Automatic index rebuild on content changes (hot reload)
- **5 MCP Tools**:
  - `search_standards` - Semantic search over standards
  - `start_workflow` - Initialize phase-gated workflow
  - `get_current_phase` - Retrieve current phase requirements
  - `complete_phase` - Submit evidence and advance
  - `get_workflow_state` - Query complete workflow state
- **Observability Hooks**: No-op by default, extensible for any platform
- **Local Embeddings**: Free, offline semantic search with sentence-transformers
- **Thread-Safe Hot Reload**: Concurrent query protection during index rebuilds
- **Documentation**: Complete README, observability integration guide

### Features
- 90% context reduction (50KB → 5KB via RAG)
- <100ms query latency
- Incremental index updates (fast hot reload)
- Project-agnostic (works with any codebase)
- No external dependencies for core functionality

### Architecture
- LanceDB for vector storage (deterministic, thread-safe)
- Sentence-transformers for embeddings (no API keys required)
- Watchdog for file system monitoring
- FastMCP for Cursor IDE integration

---

## Future Releases

### Planned for [1.1.0]
- [ ] Sub-agent: Design Validator (adversarial design review)
- [ ] Sub-agent: Concurrency Analyzer (thread safety analysis)
- [ ] Sub-agent: Architecture Critic (system design review)
- [ ] Sub-agent: Test Generator (systematic test creation)
- [ ] Enhanced RAG: Hybrid search (vector + keyword)
- [ ] Multi-language project support (Python + Go in same repo)

### Planned for [1.2.0]
- [ ] Workflow templates: API design validation
- [ ] Workflow templates: Security review
- [ ] Performance: Async RAG queries for batch operations
- [ ] Performance: Cached embeddings for frequently queried standards

---

## Updating

When a new version is released, users can update via:

```
"Update Agent OS to latest version"
```

Cursor agent will:
1. Pull latest from agent-os-enhanced repo
2. Update MCP server code
3. Preserve user customizations
4. Rebuild RAG index if needed

---

## Version Compatibility

| Agent OS Version | Python | LanceDB | Sentence-Transformers | MCP |
|------------------|--------|---------|----------------------|-----|
| 1.0.0            | ≥3.8   | ~=0.25.0 | ≥2.0.0               | ≥1.0.0 |

---

## Breaking Changes

None yet (initial release).

---

## Contributors

- 100% AI-authored via human orchestration (HoneyHive team)
- Built on Brian Casel's Builder Methods Agent OS foundation
- Inspired by HoneyHive's LLM Workflow Engineering methodology

---

**For detailed feature documentation, see README.md**
