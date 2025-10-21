# Supporting Documents Index

**Spec:** Workflow Task Management Guidance  
**Created:** 2025-10-08  
**Total Documents:** 1

## Document Catalog

### 1. Problem Analysis

**File:** `problem-analysis.md`  
**Type:** Problem analysis and requirements capture  
**Purpose:** Documents the issue where AI creates external TODOs while executing MCP workflows, analyzes root causes, and proposes solutions

**Relevance:** Requirements [H], Design [H], Implementation [H]

**Key Topics:**
- AI behavioral issue: Creating parallel TODOs during workflow execution
- Architectural constraint: Cannot modify Cursor's tool descriptions
- Root cause: Missing guidance in MCP workflow tool responses
- Proposed solution: Inject task management guidance into all workflow responses
- Three solution options with recommendation (Option 1)

---

## Cross-Document Analysis

**Common Themes:**
- Single-source-of-truth principle for task management
- Architectural separation between Cursor tools and Agent OS MCP tools
- Need for explicit guidance in tool responses

**Potential Conflicts:**
- None (single document)

**Coverage Gaps:**
- Current implementation details of workflow_engine.py
- Exact response structure of workflow tools
- Test strategy details
- Migration/deployment approach

---

## Next Steps

This index will be used in Task 3 to systematically extract insights from each document. The extracted insights will be organized by:
- **Requirements Insights:** User needs, business goals, functional requirements
- **Design Insights:** Architecture patterns, technical approaches, component designs
- **Implementation Insights:** Code patterns, testing strategies, deployment guidance

---

## Extracted Insights

### Requirements Insights (Phase 1)

#### From problem-analysis.md:
- **User Need:** AI must understand when workflow system is managing tasks and not create parallel TODO lists
- **Business Goal:** Enforce single-source-of-truth for task management during workflow execution
- **Functional Req (FR-1):** All workflow tool responses must indicate task management mode (MUST)
- **Functional Req (FR-2):** Guidance must explicitly prohibit external task tools like todo_write (MUST)
- **Functional Req (FR-3):** Pattern must work for all workflows - existing and future (MUST)
- **Functional Req (FR-4):** Implementation should not require updating workflow .md files (SHOULD)
- **Functional Req (FR-5):** Guidance must be visible on every workflow tool call (SHOULD)
- **Constraint:** Cannot modify Cursor's tool descriptions - all guidance must come from MCP side
- **NFR-1:** Response size increase must be < 200 bytes
- **NFR-2:** Implementation time < 1 hour
- **NFR-3:** 100% backward compatibility with existing workflows

### Design Insights (Phase 2)

#### From problem-analysis.md:
- **Architecture:** Two-provider system (Cursor tools vs Agent OS MCP tools) - can only control MCP side
- **Component:** Workflow engine must inject guidance into all tool responses
- **Solution Pattern (Recommended - Option 1):** Prepend guidance fields to all workflow tool responses
  - Add `⚠️_WORKFLOW_EXECUTION_MODE: "ACTIVE"` field
  - Add `🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS` field with explicit prohibition
  - Add `execution_model` field describing workflow progression
- **Alternative (Option 2):** Inject preamble into phase_content array
- **Alternative (Option 3):** Add only to workflow_overview (rejected - not persistent enough)
- **Design Constraint:** Solution must work without modifying individual workflow .md files
- **Design Principle:** Single injection point in workflow_engine.py for all workflows

### Implementation Insights (Phase 4)

#### From problem-analysis.md:
- **Code Location:** Primary changes in `mcp_server/workflow_engine.py`
- **Code Location:** Apply wrapper in `mcp_server/server/tools/workflow_tools.py`
- **Code Pattern:** Create response wrapper function that injects guidance fields
- **Code Pattern:** Apply wrapper to all workflow tool responses (start_workflow, get_current_phase, get_task, complete_phase)
- **Testing:** Unit tests for response injection logic
- **Testing:** Integration test validating AI doesn't create TODOs during workflow execution
- **No Changes Required:** Workflow .md files, metadata.json, phase/task files remain unchanged
- **Success Criteria:** AI never creates TODOs when executing workflows

### Cross-References

**Validated by Multiple Sources:** N/A (single document)

**Conflicts:** None identified

**High-Priority:**
- Implementing FR-1 and FR-2 (explicit task management mode indication)
- Using Option 1 (prepend to all responses) for maximum reliability
- Ensuring backward compatibility (NFR-3)
- Architectural constraint that MCP side must provide all guidance

---

## Insight Summary

**Total:** 26 insights  
**By Category:** Requirements [12], Design [9], Implementation [5]  
**Multi-source validated:** 0 (single document)  
**Conflicts to resolve:** 0  
**High-priority items:** 4

**Phase 0 Complete:** ✅ 2025-10-08

