---
sidebar_position: 1
doc_type: how-to
---

# Create Custom Workflows

This guide covers the AI-human collaborative process for creating custom prAxIs OS workflows that follow meta-framework principles and construction standards.

## Goal

By following this guide, AI agents will create workflows with:
- Meta-framework principle compliance (three-tier architecture, horizontal decomposition)
- Proper metadata configuration for RAG discoverability
- Phase-gated execution with validation checkpoints
- Command language for binding instructions
- File size optimization for attention quality

## Prerequisites

- Understanding of prAxIs OS workflows ([Understanding prAxIs OS Workflows](../tutorials/understanding-agent-os-workflows))
- prAxIs OS installed in your project
- **AI agents**: Heavy querying of standards throughout creation

## Critical: AI-Human Partnership Model

**Human's role:**
- Identifies need for custom workflow
- Provides strategic direction and requirements
- Reviews and approves AI-created workflow
- Guides iteration based on testing

**AI's role:**
- **Authors the workflow** (writes all files)
- Queries standards heavily (construction, metadata, meta-framework)
- Applies horizontal decomposition principles
- Ensures command language and validation gates
- Tests and iterates based on feedback

**This is NOT a human-writes-workflow guide.** AI creates workflows with human strategic guidance, following the same pattern as standards creation.

## When to Use This

Create a custom workflow when you have:

✅ **A repeatable multi-step process** - Same steps executed multiple times across projects  
✅ **Quality gates that must be enforced** - Critical validation that AI might skip  
✅ **Complex validation requirements** - More than simple "does file exist" checks  
✅ **State that needs persistence** - Work spanning multiple sessions  

**Examples:**
- Database migration with rollback validation
- API documentation generation from OpenAPI specs
- Security audit processes with compliance checks
- Performance optimization procedures with benchmarking

---

## Step 0: Query Foundation Standards (AI)

**Before starting, AI agents MUST query to understand workflow construction:**

```python
# Query 1: Workflow construction standards
search_standards("workflow construction standards meta-framework principles")

# Query 2: Meta-framework foundation
search_standards("three-tier architecture horizontal decomposition")

# Query 3: Metadata requirements
search_standards("workflow metadata standards naming conventions")

# Query 4: Command language
search_standards("command language binding instructions validation gates")

# Query 5: File size guidelines
search_standards("horizontal decomposition file size limits attention quality")
```

**Why query first:**
- Understand meta-framework principles that govern ALL workflows
- Learn file size constraints (phase.md ~80 lines, tasks 100-170 lines)
- Discover command language categories and binding symbols
- Learn validation gate patterns
- Ensure RAG-optimized metadata creation

**These queries load the construction patterns into context before creating anything.**

---

## Step 1: Understand Meta-Framework Foundation (AI)

All workflows follow **meta-framework principles**:

### 1.1 Three-Tier Architecture

**Tier 1 (Execution):** Task files ≤100 lines
- Single-responsibility, focused instructions
- Uses command language (🛑 🎯 📊)
- Consumed 1-5 files per task

**Tier 2 (Context):** Phase files ~80 lines
- Complete methodology per phase
- Read when phase starts

**Tier 3 (Methodology):** Core/ supporting docs
- Read when referenced via ⚠️ MUST-READ

**Why this matters:** File size directly impacts attention quality:
- ≤100 lines → 95%+ attention quality
- 100-170 lines → 85-95% attention
- \>500 lines → \<70% attention (failures increase)

### 1.2 Horizontal Decomposition

Break workflows **horizontally by workflow step**, not vertically by abstraction:

✅ **Correct (Horizontal):**
```
Task 1: Discover endpoints (70 lines)
Task 2: Extract contracts (85 lines)
Task 3: Validate schemas (60 lines)
```

❌ **Wrong (Vertical):**
```
Layer 1: Models (500 lines)
Layer 2: Services (600 lines)
Layer 3: Controllers (400 lines)
```

**Result:** 15-25% context use vs 90%+ → 3-4x success rate improvement

### 1.3 Command Language (Binding)

Use **command symbols** for binding instructions:

| Symbol | Command | Type | Binding |
|--------|---------|------|---------|
| 🛑 | EXECUTE-NOW | Blocking | Cannot proceed |
| 🛑 | VALIDATE-GATE | Quality gate | Requires evidence |
| 🚨 | FRAMEWORK-VIOLATION | Error detection | Prevents shortcuts |
| 🎯 | NEXT-MANDATORY | Routing | Explicit control flow |
| 📊 | COUNT-AND-DOCUMENT | Evidence | Quantified proof |
| ⚠️ | MUST-READ | Required input | Load context |

**Why symbols:** Natural language = ~60% compliance, Symbols = ~85% compliance

### 1.4 Validation Gates (Evidence-Based)

Every phase ends with **measurable evidence**, not trust:

❌ **Trust-based:** "Did you validate the schemas?"
✅ **Evidence-based:** `[ ] schema_validation_passed - validation.json shows 0 errors ✅`

---

## Step 2: Plan Workflow Structure (Human + AI Collaboration)

**Human provides:** Strategic direction, requirements, desired outcome
**AI creates:** Structured plan following meta-framework principles

### 2.1 Identify Phases

Break process into distinct phases with clear handoff points:

**Example: API Validation Workflow**
- Phase 0: API Discovery (find all endpoints)
- Phase 1: Contract Validation (check OpenAPI compliance)
- Phase 2: Security Analysis (check auth, CORS, rate limiting)
- Phase 3: Performance Testing (benchmark response times)

**AI queries:**
```python
search_standards("workflow phase organization sequential dependencies")
```

### 2.2 Define Validation Gates

For each phase, define **measurable evidence criteria**:

**Example Phase 0 Gate:**
```markdown
🛑 VALIDATE-GATE: Phase 0 Checkpoint

Before advancing to Phase 1:
- [ ] endpoint_inventory_created - inventory.json exists ✅/❌
- [ ] contracts_extracted - All 24 endpoints have contracts ✅/❌
- [ ] no_undocumented_routes - grep verification passed ✅/❌
```

**AI queries:**
```python
search_standards("validation gates evidence collection measurable criteria")
```

### 2.3 Estimate Duration

Provide realistic time estimates:

**AI queries:**
```python
search_standards("time estimation standards workflow duration")
```

- Phase-level estimates (e.g., "10 minutes")
- Total workflow duration (e.g., "45-60 minutes")
- Based on actual execution, not ideal scenarios

---

## Step 3: Create Workflow Directory Structure (AI)

**AI queries:**
```python
search_standards("workflow directory structure phase.md task files")
```

Create the standard workflow directory structure:

```bash
mkdir -p .praxis-os/workflows/api_validation_v1/phases/{0,1,2,3}
mkdir -p .praxis-os/workflows/api_validation_v1/core
```

**Result:**
```
.praxis-os/workflows/api_validation_v1/
├── metadata.json           # Workflow definition (required)
├── phases/
│   ├── 0/
│   │   ├── phase.md       # Phase overview (~80 lines) - NOT README.md
│   │   ├── task-1-name.md # Task files (100-170 lines each)
│   │   └── task-2-name.md
│   ├── 1/
│   ├── 2/
│   └── 3/
└── core/                   # Optional supporting docs
```

**Critical naming conventions:**
- ✅ Use `phase.md` (NOT README.md) - workflow engine looks for phase.md
- ✅ Task files: `task-N-descriptive-name.md`
- ✅ Workflow naming: `{purpose}_v{version}` (e.g., `api_validation_v1`)

---

## Step 4: Create metadata.json (AI)

**AI queries:**
```python
# Query metadata standards
search_standards("workflow metadata standards schema required fields")

# Query RAG optimization
search_standards("RAG content authoring keywords natural language")

# Query naming conventions
search_standards("workflow naming conventions versioning")
```

**Critical:** Metadata must be **RAG-optimized** for discoverability. Use natural language descriptions that match how AI agents will query.

Create `.praxis-os/workflows/api_validation_v1/metadata.json`:

```json
{
  "workflow_type": "api_validation_v1",
  "version": "1.0.0",
  "name": "API Validation Workflow",
  "description": "Validate API design, security, and performance compliance",
  "author": "Your Team",
  "total_phases": 4,
  "estimated_duration": "45-60 minutes",
  "primary_outputs": [
    "API validation report",
    "Compliance checklist",
    "Security recommendations"
  ],
  "phases": [
    {
      "phase_number": 0,
      "phase_name": "API Discovery",
      "phase_file": "phases/0/phase.md",
      "checkpoint": {
        "required_evidence": [
          "endpoint_inventory_created",
          "contracts_extracted",
          "no_undocumented_routes"
        ]
      }
    },
    {
      "phase_number": 1,
      "phase_name": "Contract Validation",
      "phase_file": "phases/1/phase.md",
      "checkpoint": {
        "required_evidence": [
          "openapi_spec_valid",
          "request_schemas_validated",
          "response_schemas_validated"
        ]
      }
    },
    {
      "phase_number": 2,
      "phase_name": "Security Analysis",
      "phase_file": "phases/2/phase.md",
      "checkpoint": {
        "required_evidence": [
          "auth_mechanisms_verified",
          "cors_configured_correctly",
          "rate_limiting_implemented"
        ]
      }
    },
    {
      "phase_number": 3,
      "phase_name": "Performance Testing",
      "phase_file": "phases/3/phase.md",
      "checkpoint": {
        "required_evidence": [
          "benchmarks_run",
          "response_times_under_threshold",
          "report_generated"
        ]
      }
    }
  ]
}
```

**Key Fields:**

- `workflow_type`: Unique identifier (use semantic versioning in name)
- `version`: Semantic version number
- `description`: Natural language description (searchable by RAG)
- `total_phases`: Number of phases
- `estimated_duration`: Realistic time estimate
- `primary_outputs`: Key deliverables
- `phases`: Array of phase objects with checkpoints

---

## Step 5: Write Phase Files (AI)

**AI queries:**
```python
# Learn phase file structure
search_standards("phase.md file structure objectives commands tasks")

# Understand file size constraints
search_standards("phase files 80 lines why overview only")

# Learn command language for phases
search_standards("command language phase objectives routing")
```

Create a `phase.md` file for each phase. These should be **~80 lines** and provide **overview-level guidance only**.

**Why ~80 lines:**
- Keeps attention quality at 95%+ (optimal range)
- Forces focus on overview vs details (details go in task files)
- Maintains three-tier architecture (phase = Tier 2 context)

### 5.1 Phase File Template

Create `.praxis-os/workflows/api_validation_v1/phases/0/phase.md`:

```markdown
# Phase 0: API Discovery

🎯 **Objective:** Identify all API endpoints and extract contract definitions

**Duration:** 10 minutes

---

## What This Phase Does

This phase scans your codebase to:
1. Discover all HTTP endpoints
2. Extract route definitions
3. Identify handler functions
4. Build endpoint inventory
5. Extract request/response contracts

---

## Commands

### 🔍 ANALYZE
Scan codebase for API endpoints using framework-specific patterns.

### 📊 EXTRACT
Parse route definitions and handler signatures.

### ✅ VERIFY
Confirm all routes documented, no orphaned handlers.

---

## Tasks

This phase has 3 tasks:

1. **Scan Routes** - Find all endpoint definitions
2. **Extract Contracts** - Get request/response schemas
3. **Build Inventory** - Create structured endpoint list

Work through tasks sequentially using horizontal decomposition (one task at a time).

---

## 🛑 Validation Gate

Before advancing to Phase 1, provide evidence:

- [ ] `endpoint_inventory_created` - inventory.json file exists
- [ ] `contracts_extracted` - All endpoints have contracts
- [ ] `no_undocumented_routes` - No routes missing from inventory

---

## Next Phase

**Phase 1: Contract Validation** - Validate OpenAPI compliance
```

**Phase File Guidelines:**

- Start with 🎯 objective (binding command)
- List what the phase accomplishes (high-level)
- Use command language for key actions (🔍 ANALYZE, 📊 EXTRACT, ✅ VERIFY)
- Reference tasks but **don't duplicate** detailed task content
- End with 🛑 VALIDATE-GATE (measurable evidence)
- Keep to ~80 lines (enforce attention quality)

**Common mistake:** Including detailed commands/code in phase.md → Move to task files!

**AI queries during writing:**
```python
search_standards("validation gate patterns evidence requirements")
```

---

## Step 6: Write Task Files (AI)

**AI queries:**
```python
# Learn task file structure
search_standards("task file structure 100-170 lines single responsibility")

# Understand command language for tasks
search_standards("command language EXECUTE-NOW VALIDATE-GATE FRAMEWORK-VIOLATION")

# Learn evidence collection patterns
search_standards("evidence collection quantified proof COUNT-AND-DOCUMENT")

# Horizontal decomposition
search_standards("horizontal decomposition one task per file")
```

Create detailed task files (**100-170 lines**) for each task in each phase.

**Why 100-170 lines:**
- Optimal range: 85-95% attention quality
- Single-responsibility principle enforced
- Horizontal decomposition (by workflow step, not abstraction layers)
- Focused execution without context overflow

**One task = one file** (horizontal decomposition principle)

### 6.1 Task File Template

Create `.praxis-os/workflows/api_validation_v1/phases/0/task-1-scan-routes.md`:

```markdown
# Task 1: Scan Routes

🎯 **Objective:** Discover all HTTP endpoint definitions in the codebase

**Estimated Time:** 3-4 minutes

---

## Context

API endpoints can be defined in multiple ways depending on the framework:
- Express: `app.get('/path', handler)`
- FastAPI: `@app.get('/path')`
- Flask: `@app.route('/path', methods=['GET'])`

This task identifies all endpoint definitions regardless of framework.

---

## Prerequisites

- Codebase accessible
- Framework identified (Express/FastAPI/Flask/etc.)

---

## Commands

### 🔍 ANALYZE-FRAMEWORK

Identify the web framework used:

```bash
# Check package.json or requirements.txt
grep -E "(express|fastapi|flask)" package.json requirements.txt
```

### 🔍 SEARCH-ROUTES

Search for route definitions using framework-specific patterns:

**Express:**
```bash
grep -r "app\.(get|post|put|delete|patch)" src/
```

**FastAPI:**
```bash
grep -r "@app\.(get|post|put|delete|patch)" .
```

**Flask:**
```bash
grep -r "@app\.route" .
```

### 📊 EXTRACT-ENDPOINTS

For each route found, extract:
- HTTP method (GET, POST, etc.)
- Path (e.g., `/api/users/:id`)
- Handler function name
- File location

### ✅ VERIFY-COMPLETENESS

Check for missed routes:
- Search for alternative patterns
- Check for dynamic route registration
- Verify against running server logs (if available)

---

## Acceptance Criteria

- [ ] Framework identified and documented
- [ ] All route definitions found (verified via multiple search patterns)
- [ ] Route data extracted (method, path, handler, location)
- [ ] Results saved to `endpoint-scan.json`:
  ```json
  {
    "framework": "express",
    "total_endpoints": 12,
    "endpoints": [
      {
        "method": "GET",
        "path": "/api/users/:id",
        "handler": "getUserById",
        "file": "src/api/users.ts",
        "line": 45
      }
    ]
  }
  ```

---

## Troubleshooting

### Issue: Routes not found by grep

**Cause:** Dynamic route registration or non-standard patterns

**Solution:**
1. Check for route files imported dynamically
2. Search for router instances: `grep -r "Router()" src/`
3. Look for route middleware: `grep -r "\.use(" src/`

### Issue: Too many false positives

**Cause:** Comments or test files matching patterns

**Solution:**
```bash
# Exclude test files and comments
grep -r "app\.get" src/ --exclude="*.test.ts" | grep -v "^\s*//"
```

---

## Next Task

**Task 2: Extract Contracts** - Get request/response schemas for each endpoint
```

**Task File Guidelines:**

- Start with 🎯 objective and time estimate
- Provide context and background (why this task matters)
- Use **binding command language** with concrete examples:
  - 🛑 EXECUTE-NOW for critical blocking steps
  - 🛑 VALIDATE-GATE for quality gates
  - 🚨 FRAMEWORK-VIOLATION to prevent shortcuts
  - 📊 COUNT-AND-DOCUMENT for quantified evidence
  - ⚠️ MUST-READ for required context loading
- Include code snippets and shell commands (executable)
- List acceptance criteria as **measurable checkboxes**
- Add troubleshooting section (common issues)
- Keep to 100-170 lines (attention quality optimization)
- **One task = one file** (horizontal decomposition - single responsibility)

**AI queries during writing:**
```python
search_standards("FRAMEWORK-VIOLATION patterns common shortcuts")
search_standards("acceptance criteria measurable evidence")
```

---

## Step 7: Validate Against Standards (AI)

**AI queries:**
```python
# Get validation checklist
search_standards("workflow construction standards validation checklist")

# Learn compliance patterns
search_standards("workflow quality standards file naming phase.md")
```

Use the workflow construction checklist:

### 7.1 Structural Validation

```bash
# Check directory structure
ls .praxis-os/workflows/api_validation_v1/
# Should see: metadata.json, phases/, core/

# Check phase files exist (and named correctly - phase.md not README.md)
ls .praxis-os/workflows/api_validation_v1/phases/*/phase.md
```

**AI verifies:**
- [ ] All phase directories have `phase.md` (NOT README.md) ✅/❌
- [ ] Task files named `task-N-descriptive-name.md` ✅/❌
- [ ] `metadata.json` exists and is valid JSON ✅/❌

### 7.2 File Size Validation

```bash
# Check phase.md files (~80 lines) - optimal attention quality
wc -l .praxis-os/workflows/api_validation_v1/phases/*/phase.md

# Check task files (100-170 lines) - acceptable attention quality
wc -l .praxis-os/workflows/api_validation_v1/phases/*/*task*.md
```

**AI verifies:**
- [ ] Phase files 70-90 lines (acceptable range) ✅/❌
- [ ] Task files 100-170 lines (optimal range) ✅/❌
- [ ] No execution files >200 lines (quality degradation threshold) ✅/❌

**If files too large:** Apply horizontal decomposition - split by single responsibility

### 7.3 Content Validation

**AI verifies:**
- [ ] Command language used throughout (🛑 🎯 📊 🚨 ⚠️) ✅/❌
- [ ] All tasks have 🛑 VALIDATE-GATE with measurable criteria ✅/❌
- [ ] Evidence collection points (📊 COUNT-AND-DOCUMENT) ✅/❌
- [ ] Task navigation links complete ✅/❌
- [ ] 🚨 FRAMEWORK-VIOLATION guards against common shortcuts ✅/❌

### 7.4 Metadata Validation

**AI verifies metadata.json:**
- [ ] All required fields present (workflow_type, version, name, etc.) ✅/❌
- [ ] Natural language descriptions (RAG-optimized for discovery) ✅/❌
- [ ] Realistic time estimates (based on actual execution) ✅/❌
- [ ] Validation criteria defined for each phase (evidence requirements) ✅/❌
- [ ] Searchable keywords in description ✅/❌

---

## Step 8: Test End-to-End (AI + Human)

**AI queries:**
```python
search_standards("workflow testing end-to-end validation")
```

Test the workflow with the workflow engine:

### 8.1 Start the Workflow

In Cursor chat:

```
Start the api_validation_v1 workflow on src/api/
```

### 8.2 Monitor Execution

Watch for:
- Phase transitions
- Task execution
- Checkpoint validation
- Evidence collection

### 8.3 Verify State Persistence

Test resumption:
1. Start workflow
2. Complete Phase 0
3. Close Cursor
4. Reopen Cursor
5. Check workflow state:
   ```
   What's the current workflow state for api_validation_v1?
   ```

### 8.4 Verify Checkpoints

Try to skip a phase (should be blocked):
```
Skip to Phase 2
```

Expected: Workflow engine blocks the request, requires Phase 1 evidence first.

---

## Final Validation Checklist (AI)

Before considering the workflow complete, AI verifies:

**Meta-Framework Compliance:**
- [ ] Three-tier architecture followed (phase ~80, tasks 100-170, core for reference) ✅/❌
- [ ] Horizontal decomposition applied (one task = one file, single responsibility) ✅/❌
- [ ] Command language used throughout (🛑 🎯 📊 🚨 ⚠️) ✅/❌
- [ ] Validation gates are evidence-based (not trust-based) ✅/❌

**File Structure:**
- [ ] `metadata.json` includes all required fields + RAG-optimized descriptions ✅/❌
- [ ] Each phase has `phase.md` file (NOT README.md) ~80 lines ✅/❌
- [ ] Each task has task file named `task-N-descriptive-name.md` (100-170 lines) ✅/❌
- [ ] No execution files >200 lines (attention quality threshold) ✅/❌

**Content Quality:**
- [ ] All phases have 🛑 VALIDATE-GATE with measurable evidence ✅/❌
- [ ] All tasks have 🚨 FRAMEWORK-VIOLATION guards for common shortcuts ✅/❌
- [ ] Evidence collection points (📊 COUNT-AND-DOCUMENT) included ✅/❌
- [ ] Task navigation links complete ✅/❌

**Testing:**
- [ ] Workflow tested end-to-end successfully ✅/❌
- [ ] State persistence verified (resume works) ✅/❌
- [ ] Checkpoint gates block invalid progression (tried skipping → blocked) ✅/❌
- [ ] All 🛑 EXECUTE-NOW commands are binding (AI cannot skip) ✅/❌

**Human Review:**
- [ ] Human approves workflow structure and gates
- [ ] Human validates that workflow solves the intended problem
- [ ] Iteration based on testing feedback complete

---

## Troubleshooting

### Issue: Workflow not discovered by workflow engine

**Solution:**

1. Check file location:
   ```bash
   ls .praxis-os/workflows/your_workflow_v1/metadata.json
   ```
   Must be in `.praxis-os/workflows/` or configured in `.praxis-os/config.json`

2. Restart MCP server (restart Cursor or kill process)

3. Check logs:
   ```bash
   grep "Loaded workflow" ~/.cursor/logs/mcp-server.log
   ```

### Issue: Checkpoint validation not working

**Solution:**

1. Verify `checkpoint` object in metadata.json phase definition
2. Ensure `required_evidence` array is present
3. Check that evidence keys match exactly what's being provided

### Issue: Phase files too long (>100 lines)

**Solution:**

Phase files should be overview only (~80 lines). Move detailed content to task files:
- Commands → Task files
- Code examples → Task files
- Troubleshooting → Task files

---

## Related Documentation

- **[Understanding prAxIs OS Workflows](../tutorials/understanding-agent-os-workflows)** - Learn workflow concepts
- **[Reference: Workflows](../reference/workflows)** - Complete workflow system reference
- **Standards: workflow-construction-standards.md** - Detailed construction rules
- **Standards: workflow-metadata-standards.md** - Metadata.json specification
- **Standards: three-tier-architecture.md** - Meta-framework principles

---

## Summary

**AI-Human Collaborative Workflow Creation:**

**AI's responsibilities:**
1. ✅ Queries foundation standards (construction, meta-framework, metadata)
2. ✅ Understands meta-framework principles (three-tier, horizontal decomposition, command language)
3. ✅ Creates directory structure following naming conventions
4. ✅ Writes RAG-optimized metadata.json with evidence-based checkpoints
5. ✅ Creates phase.md files (~80 lines, overview only)
6. ✅ Creates task files (100-170 lines, single responsibility, binding commands)
7. ✅ Validates against construction standards (file sizes, command language, evidence gates)
8. ✅ Tests end-to-end and iterates based on feedback

**Human's responsibilities:**
1. ✅ Provides strategic direction and requirements
2. ✅ Reviews AI-created workflow structure
3. ✅ Approves or requests iteration
4. ✅ Validates workflow solves intended problem

**Key Success Factors:**
- **Query-heavy AI:** 5-10+ queries to standards throughout creation
- **Meta-framework grounded:** Every decision traceable to principles
- **Evidence-based:** Validation gates require proof, not trust
- **Horizontal decomposition:** Small files (≤170 lines) maintain attention quality
- **Binding commands:** Symbols (🛑 🎯 📊 🚨) create ~85% compliance vs ~60% with natural language

Custom workflows enforce quality through phase gating and command language, ensuring systematic AI execution following your defined process.

