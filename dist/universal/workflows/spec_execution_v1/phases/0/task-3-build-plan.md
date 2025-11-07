# Task 3: Build Execution Plan

**Phase:** 0 (Spec Analysis & Planning)  
**Purpose:** Create execution plan, query relevant standards, prepare for implementation  
**Estimated Time:** 5 minutes

---

## 🎯 Objective

Use parsed phase and task data to build a comprehensive execution plan. Query relevant standards from the MCP system to ensure quality implementation.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1 & 2 must be completed (spec validated, tasks parsed)

⚠️ MUST-READ: Review parsed task summary from Task 2

---

## Steps

### Step 1: Query Core Standards

Use MCP to query essential standards for implementation:

```python
# Query production code checklist
MCP: search_standards("production code checklist")

# Query language-specific standards (from specs.md)
MCP: search_standards("python best practices")

# Query testing standards
MCP: search_standards("testing standards integration testing")
```

📊 COUNT-AND-DOCUMENT: Standards Retrieved
- Total standards documents: [number]
- Key standards: [list]

### Step 2: Review Spec Technical Design

Read the specs.md file to understand technical approach:

```bash
cat .praxis-os/specs/YYYY-MM-DD-name/specs.md
```

Extract key technical details:
- Architecture approach: [brief summary]
- Key technologies: [list]
- Data models: [count]
- APIs/interfaces: [count]

### Step 3: Review Implementation Guidance

Read the implementation.md file for patterns and guidance:

```bash
cat .praxis-os/specs/YYYY-MM-DD-name/implementation.md
```

Note key patterns to use:
- Code patterns: [list]
- Testing approach: [summary]
- Deployment guidance: [yes/no]

### Step 4: Build Execution Summary

Create a comprehensive execution plan summary:

📊 COUNT-AND-DOCUMENT: Execution Plan

**Spec:** `[spec name]`

**Implementation Scope:**
- Total phases: [number]
- Total tasks: [number]
- Estimated duration: [from tasks.md]

**Technical Approach:**
- Language: [e.g., Python]
- Architecture: [e.g., Modular with dependency injection]
- Key components: [list]

**Quality Standards:**
- Production code checklist: ✅ Queried
- Language standards: ✅ Queried
- Testing standards: ✅ Queried

**Execution Approach:**
- Horizontal scaling: Use `get_task()` one task at a time
- Phase gates: Validate before advancing
- Evidence collection: Document at each checkpoint

### Step 5: Prepare for Phase 1

Identify the first task to execute in Phase 1:

- Phase 1 first task: Task [N.M] - [description]
- Ready to begin: [✅/❌]

---

## Completion Criteria

🛑 VALIDATE-GATE: Execution Plan Complete

- [ ] Core standards queried via MCP ✅/❌
- [ ] Technical design reviewed (specs.md) ✅/❌
- [ ] Implementation guidance reviewed (implementation.md) ✅/❌
- [ ] Execution plan summary documented ✅/❌
- [ ] First task identified ✅/❌

🚨 FRAMEWORK-VIOLATION: Skipping standards queries

The production code checklist and language-specific standards are MANDATORY. Proceeding without them will result in low-quality code that fails validation gates.

---

## Evidence Collection

📊 COUNT-AND-DOCUMENT: Phase 0 Complete

**Validation Results:**
- Spec located: ✅
- Tasks parsed: [number] tasks across [number] phases
- Standards queried: [number] documents
- Execution plan: ✅ Complete

**Ready for Implementation:**
- First phase: Phase [number]
- First task: Task [N.M]
- Estimated time: [duration]

---

## Phase 0 Completion

🛑 VALIDATE-GATE: Phase 0 Checkpoint

This phase is complete when you have:
- ✅ Located and validated the specification package
- ✅ Parsed all phases and tasks from tasks.md
- ✅ Mapped dependencies between tasks
- ✅ Queried relevant standards via MCP
- ✅ Created comprehensive execution plan summary
- ✅ Identified the first task to execute

Submit checkpoint evidence to complete Phase 0.

---

## Next Step

🎯 NEXT-MANDATORY: Begin Phase 1 execution

Upon Phase 0 completion, use `get_current_phase()` to receive Phase 1 overview, then use `get_task(session_id, phase=1, task_number=1)` to begin first task.

