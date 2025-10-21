# Agent OS Persona System - Implementation Tasks

**Phased breakdown of implementation work.**

---

## 📋 PHASE 1: ASYNC INFRASTRUCTURE & FOUNDATION (Week 1-2)

**Goal:** Establish async job execution infrastructure and basic persona system

### Task 1.0: Implement Async Job Queue Manager
**Effort:** 8 hours  
**Owner:** AI  
**Dependencies:** None  
**Reference:** [async-persona-execution-architecture.md](supporting-docs/async-persona-execution-architecture.md)

**Subtasks:**
- [ ] Create `JobManager` class in `mcp_server/job_manager.py`
- [ ] Design SQLite schema (persona_jobs table)
- [ ] Implement create_job(), get_job(), update_progress()
- [ ] Implement complete_job(), fail_job(), cancel_job()
- [ ] Implement cleanup_old_jobs() with retention policy
- [ ] Thread-safe job access (SQLite WAL mode)
- [ ] Unit tests for concurrent access

**Deliverables:**
- `mcp_server/job_manager.py` (~300 lines)
- `mcp_server/migrations/001_persona_jobs.sql`
- `tests/unit/test_job_manager.py` (15+ tests)
- Database schema with indexes

---

### Task 1.1: Implement Background Worker Pool
**Effort:** 8 hours  
**Owner:** AI  
**Dependencies:** Task 1.0

**Subtasks:**
- [ ] Create `WorkerPool` class in `mcp_server/background_worker.py`
- [ ] Create `WorkerThread` class
- [ ] Implement job pickup loop (priority queue)
- [ ] Implement progress callback mechanism
- [ ] Implement graceful shutdown
- [ ] Handle worker crashes (stale job detection)
- [ ] Integration tests

**Deliverables:**
- `mcp_server/background_worker.py` (~400 lines)
- `tests/integration/test_background_worker.py`
- Configurable worker pool size (default: 3)

---

### Task 1.2: Create Persona Prompt System
**Effort:** 4 hours  
**Owner:** AI  
**Dependencies:** None

**Subtasks:**
- [ ] Create `mcp_server/personas/` directory
- [ ] Create `PersonaConfig` dataclass in `mcp_server/models.py`
- [ ] Create `JobState` and `ProgressUpdate` dataclasses
- [ ] Create prompt loader utility `load_persona_prompt(identifier)`
- [ ] Add persona registry `CORE_PERSONAS` dict
- [ ] Unit tests for prompt loading

**Deliverables:**
- `mcp_server/personas/__init__.py`
- `mcp_server/models.py` (updated with PersonaConfig, JobState, ProgressUpdate)
- `mcp_server/personas/loader.py`
- `tests/unit/test_persona_loader.py`

---

### Task 1.3: Enhance Persona Executor with Progress Tracking
**Effort:** 4 hours  
**Owner:** AI  
**Dependencies:** Task 1.2

**Subtasks:**
- [ ] Update `PersonaExecutor` class to accept progress callbacks
- [ ] Add progress checkpoints (initializing, searching, analyzing, generating)
- [ ] Implement ETA calculation based on progress
- [ ] Add streaming support from Anthropic SDK
- [ ] Update progress in database via callback
- [ ] Unit tests for progress tracking

**Deliverables:**
- `mcp_server/persona_executor.py` (~600 lines)
- Progress reported at 4+ checkpoints
- ETA accuracy within 50%

---

### Task 1.4: Design Architect Persona Prompt
**Effort:** 3 hours  
**Owner:** AI (with Human review)  
**Dependencies:** Task 1.2

**Subtasks:**
- [ ] Draft system prompt (target ≤1,500 tokens)
- [ ] Include: identity, expertise, review template, standards capability
- [ ] Token count optimization pass
- [ ] Human review and approval
- [ ] Finalize prompt

**Deliverables:**
- `mcp_server/personas/architect.md`
- Token count: ≤1,500
- Includes standards population workflow

---

### Task 1.5: Design Engineer Persona Prompt
**Effort:** 3 hours  
**Owner:** AI (with Human review)  
**Dependencies:** Task 1.2

**Subtasks:**
- [ ] Draft system prompt (target ≤1,500 tokens)
- [ ] Include: identity, expertise, review template, standards capability
- [ ] Token count optimization pass
- [ ] Human review and approval
- [ ] Finalize prompt

**Deliverables:**
- `mcp_server/personas/engineer.md`
- Token count: ≤1,500
- Includes standards population workflow

---

### Task 1.6: Implement Async MCP Tools (invoke_architect, invoke_engineer)
**Effort:** 6 hours  
**Owner:** AI  
**Dependencies:** Task 1.0, 1.1, 1.3, 1.4, 1.5

**Subtasks:**
- [ ] Add `invoke_architect()` async function to `mcp_server/agent_os_rag.py`
- [ ] Add `invoke_engineer()` async function
- [ ] Both create jobs via JobManager
- [ ] Return job_id and estimated duration
- [ ] Add observability hooks (if HONEYHIVE_ENABLED)
- [ ] Unit tests

**Deliverables:**
- `mcp_server/agent_os_rag.py` (updated with 2 async persona tools)
- `tests/unit/test_invoke_architect.py`
- `tests/unit/test_invoke_engineer.py`

---

### Task 1.7: Implement Async Management MCP Tools
**Effort:** 4 hours  
**Owner:** AI  
**Dependencies:** Task 1.0, 1.1

**Subtasks:**
- [ ] Add `check_persona_job()` for polling
- [ ] Add `list_persona_jobs()` for observability
- [ ] Add `cancel_persona_job()` for cancellation
- [ ] Add `persona_database_stats()` for health monitoring
- [ ] Add `reset_persona_jobs()` for emergency cleanup
- [ ] Unit tests for each tool

**Deliverables:**
- `mcp_server/agent_os_rag.py` (updated with 5 management tools)
- `tests/unit/test_async_management_tools.py`

---

### Task 1.8: Integration Testing (Phase 1)
**Effort:** 4 hours  
**Owner:** AI  
**Dependencies:** Task 1.6, 1.7

**Subtasks:**
- [ ] End-to-end test: Invoke `@architect` → poll → complete
- [ ] End-to-end test: Invoke `@engineer` → poll → complete
- [ ] Test progress updates appear correctly
- [ ] Test concurrent execution (2 personas at once)
- [ ] Verify no timeout issues
- [ ] Performance metrics (job creation <50ms, polling <10ms)
- [ ] Document results

**Deliverables:**
- `tests/integration/test_async_persona_flow.py`
- Test report with latency metrics
- Bug fixes if needed

---

## 📋 PHASE 2: EXPAND PERSONAS (Week 3)

**Goal:** Deploy remaining 5 core personas with async execution

### Task 2.1: Design Data Persona Prompt
**Effort:** 3 hours  
**Owner:** AI (with Human review)  
**Dependencies:** Phase 1 complete

**Subtasks:**
- [ ] Draft system prompt (target ≤1,500 tokens)
- [ ] Include: data pipeline expertise, tech stack adaptability, standards capability
- [ ] Token count optimization pass
- [ ] Human review and approval
- [ ] Finalize prompt

**Deliverables:**
- `mcp_server/personas/data.md`

---

### Task 2.2: Design QA Persona Prompt
**Effort:** 3 hours  
**Owner:** AI (with Human review)  
**Dependencies:** Phase 1 complete

**Subtasks:**
- [ ] Draft system prompt (target ≤1,500 tokens)
- [ ] Include: testing strategy, edge case identification, standards capability
- [ ] Token count optimization pass
- [ ] Human review and approval
- [ ] Finalize prompt

**Deliverables:**
- `mcp_server/personas/qa.md`

---

### Task 2.3: Design Security Persona Prompt
**Effort:** 3 hours  
**Owner:** AI (with Human review)  
**Dependencies:** Phase 1 complete

**Subtasks:**
- [ ] Draft system prompt (target ≤1,500 tokens)
- [ ] Include: OWASP focus, threat modeling, secure coding, standards capability
- [ ] Token count optimization pass
- [ ] Human review and approval
- [ ] Finalize prompt

**Deliverables:**
- `mcp_server/personas/security.md`

---

### Task 2.4: Design SRE Persona Prompt
**Effort:** 4 hours  
**Owner:** AI (with Human review)  
**Dependencies:** Phase 1 complete

**Subtasks:**
- [ ] Draft system prompt (target ≤1,500 tokens)
- [ ] Include: SLO/SLI expertise, production readiness, observability, standards capability
- [ ] Token count optimization pass
- [ ] Human review and approval
- [ ] Finalize prompt

**Deliverables:**
- `mcp_server/personas/sre.md`

---

### Task 2.5: Implement 4 Async MCP Tools (Data, QA, Security, SRE)
**Effort:** 6 hours  
**Owner:** AI  
**Dependencies:** Task 2.1, 2.2, 2.3, 2.4

**Subtasks:**
- [ ] Add `invoke_data()` async to MCP server
- [ ] Add `invoke_qa()` async to MCP server
- [ ] Add `invoke_security()` async to MCP server
- [ ] Add `invoke_sre()` async to MCP server
- [ ] All use JobManager for async execution
- [ ] Unit tests for each
- [ ] Update persona registry

**Deliverables:**
- `mcp_server/agent_os_rag.py` (4 new async tools)
- Unit tests for each persona
- All 7 core personas registered

---

### Task 2.6: Integration Testing (Phase 2)
**Effort:** 4 hours  
**Owner:** AI  
**Dependencies:** Task 2.5

**Subtasks:**
- [ ] End-to-end test: Invoke all 7 personas
- [ ] Test concurrent multi-persona invocation (3+ at once)
- [ ] Verify persona-specific responses
- [ ] Verify token efficiency (≤1,500 per persona)
- [ ] Performance testing (no timeout issues)
- [ ] Load test: 10 concurrent jobs
- [ ] Document results

**Deliverables:**
- Test report with concurrency results
- Performance metrics
- Bug fixes if needed

---

## 📋 PHASE 3: STANDARDS POPULATION (Week 4)

**Goal:** Enable personas to propose and create standards

### Task 3.1: Create Standard Template
**Effort:** 2 hours  
**Owner:** AI (with Human review)  
**Dependencies:** Phase 2 complete

**Subtasks:**
- [ ] Design standard markdown template
- [ ] Include sections: Context, Pattern, Examples, Anti-Patterns, When to Revisit
- [ ] Add front matter for metadata (domain, tags, created_by)
- [ ] Human review and approval

**Deliverables:**
- `universal/templates/standard-template.md`
- Template documented in `universal/usage/creating-standards.md`

---

### Task 3.2: Implement Standard Creation Helper
**Effort:** 4 hours  
**Owner:** AI  
**Dependencies:** Task 3.1

**Subtasks:**
- [ ] Create `create_standard()` utility function
- [ ] Input: domain, topic, content, metadata
- [ ] Validates file path doesn't exist
- [ ] Creates directory if needed
- [ ] Writes standard file with proper format
- [ ] Logs creation event
- [ ] Unit tests

**Deliverables:**
- `mcp_server/standard_creator.py`
- `tests/unit/test_standard_creator.py`

---

### Task 3.3: Update Persona Prompts with Standards Workflow
**Effort:** 4 hours  
**Owner:** AI  
**Dependencies:** Task 3.1, 3.2

**Subtasks:**
- [ ] Add standards proposal workflow to all 7 persona prompts
- [ ] Include: pattern detection, proposal language, Human approval wait
- [ ] Add examples of good standard proposals
- [ ] Add template usage instructions
- [ ] Verify token counts still ≤1,500

**Deliverables:**
- All 7 persona prompts updated
- Token counts verified

---

### Task 3.4: Create MCP Tool: create_standard
**Effort:** 3 hours  
**Owner:** AI  
**Dependencies:** Task 3.2

**Subtasks:**
- [ ] Add `create_standard()` MCP tool
- [ ] Parameters: domain, topic, content, approved_by
- [ ] Validates Human approval (checks metadata)
- [ ] Calls standard creator utility
- [ ] Returns success/failure message
- [ ] Unit tests

**Deliverables:**
- `mcp_server/agent_os_rag.py` (new tool)
- `tests/unit/test_create_standard.py`

---

### Task 3.5: Integration Testing (Phase 3)
**Effort:** 4 hours  
**Owner:** Human + AI  
**Dependencies:** Task 3.3, 3.4

**Subtasks:**
- [ ] Human: Request persona review that triggers standard proposal
- [ ] Persona: Proposes standard
- [ ] Human: Approves
- [ ] Persona: Creates standard via MCP tool
- [ ] Verify: File created in correct location
- [ ] Verify: File watcher detects and indexes
- [ ] Verify: Main agent queries and uses new standard
- [ ] Document full cycle time

**Deliverables:**
- End-to-end test report
- First project-specific standard created
- Cycle time metrics (proposal → indexed)

---

## 📋 PHASE 4: DOCUMENTATION & POLISH (Week 5)

**Goal:** Document system, improve UX, and finalize async infrastructure

### Task 4.1: Create Persona Usage Guide
**Effort:** 3 hours  
**Owner:** AI (with Human review)  
**Dependencies:** Phase 3 complete

**Subtasks:**
- [ ] Document how to invoke each persona
- [ ] Document what each persona does
- [ ] Document standards population workflow
- [ ] Add examples for each persona
- [ ] Add troubleshooting section
- [ ] Human review and approval

**Deliverables:**
- `universal/usage/persona-guide.md`
- Auto-installed in all projects

---

### Task 4.2: Update Installation Guide
**Effort:** 2 hours  
**Owner:** AI  
**Dependencies:** Task 4.1

**Subtasks:**
- [ ] Add persona system to installation steps
- [ ] Document async execution model
- [ ] Document all MCP tools (18 total: 6 existing + 7 persona + 5 async management)
- [ ] Add testing steps for async personas
- [ ] Document database maintenance

**Deliverables:**
- `installation-guide.md` (updated with async details)

---

### Task 4.3: Create Metrics Dashboard (Simple)
**Effort:** 4 hours  
**Owner:** AI  
**Dependencies:** Phase 3 complete

**Subtasks:**
- [ ] Add metrics tracking to MCP server
- [ ] Track: persona invocations, standards created, query rates
- [ ] Create simple CLI command: `agent-os metrics`
- [ ] Output: JSON with key metrics
- [ ] Unit tests

**Deliverables:**
- `mcp_server/metrics.py`
- `tests/unit/test_metrics.py`
- CLI command functional

---

### Task 4.4: Error Handling & Database Maintenance
**Effort:** 4 hours  
**Owner:** AI  
**Dependencies:** Phase 3 complete

**Subtasks:**
- [ ] Add clear error messages for all failure modes
- [ ] Implement automatic cleanup scheduler (daily at 3 AM)
- [ ] Implement size-based safety valve (100MB trigger)
- [ ] Add validation for standard file paths (no duplicates)
- [ ] Add helpful hints if persona invocation fails
- [ ] Integration tests for error cases and cleanup

**Deliverables:**
- Improved error handling in all MCP tools
- Automatic database maintenance (~230 lines)
- Test coverage for error cases and cleanup

---

### Task 4.5: Final Integration Testing
**Effort:** 4 hours  
**Owner:** Human + AI  
**Dependencies:** All Phase 4 tasks

**Subtasks:**
- [ ] Test full workflow with all 7 personas
- [ ] Test concurrent persona invocations
- [ ] Test standards creation at scale (10+ standards)
- [ ] Test main agent queries with many standards (50+)
- [ ] Performance testing (measure latencies)
- [ ] Token efficiency validation
- [ ] Bug bash and fixes

**Deliverables:**
- Final test report
- Performance metrics
- All known bugs fixed
- System ready for production use

---

## 📋 PHASE 5: SPECIALIST PERSONAS (Future)

**Goal:** Add specialist personas for deep expertise

### Task 5.1: Design Specialist Personas
**Effort:** TBD  
**Owner:** AI (with Human review)  
**Dependencies:** Phase 4 complete + User demand

**Potential Specialists:**
- [ ] Performance Engineer (deep performance optimization)
- [ ] Concurrency Expert (thread-safety, race conditions)
- [ ] Database Expert (query optimization, schema design)
- [ ] Code Reviewer (pure code review focus)
- [ ] Accessibility Expert (WCAG compliance, a11y)
- [ ] API Documentation Specialist (OpenAPI, API docs)
- [ ] Observability Engineer (metrics, traces, logs)

**Approach:**
- Add only when core personas can't handle depth needed
- Core personas recommend specialists
- Implemented on-demand based on user requests

---

## 📊 TASK SUMMARY

### Effort Breakdown
| Phase | Task Count | Total Effort | Timeline |
|-------|-----------|--------------|----------|
| Phase 1: Async Infrastructure & Foundation | 9 tasks | 45 hours | Week 1-2 |
| Phase 2: Expand Personas | 6 tasks | 23 hours | Week 3 |
| Phase 3: Standards Population | 5 tasks | 17 hours | Week 4 |
| Phase 4: Documentation & Polish | 5 tasks | 18 hours | Week 5 |
| **TOTAL (MVP)** | **25 tasks** | **103 hours** | **5 weeks** |

**Note:** Phase 1 expanded to include async infrastructure (job queue, worker pool, progress tracking) to eliminate timeout issues from the start. This adds ~30 hours but delivers a production-ready system with zero timeout risk.

### Dependencies
```
Phase 1 (Foundation)
  ├─> Phase 2 (Expand Personas)
       ├─> Phase 3 (Standards Population)
            ├─> Phase 4 (Documentation & Polish)
                 └─> Phase 5 (Specialist Personas - Future)
```

### Critical Path
1. Task 1.1: Persona Prompt System (foundation for all)
2. Task 1.2-1.3: First 2 persona prompts (validates approach)
3. Task 1.4-1.5: First 2 MCP tools (proves infrastructure works)
4. Task 2.1-2.5: Remaining 5 personas (completes core)
5. Task 3.3-3.4: Standards population (critical feature)
6. Task 3.5: E2E test (validates entire system)

---

**Next**: Review [Implementation Details](implementation.md) for code-level guidance and examples
