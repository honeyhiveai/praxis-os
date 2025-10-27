# Software Requirements Document

**Project:** Workflow Task Management Guidance  
**Date:** 2025-10-08  
**Priority:** High  
**Category:** Enhancement

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for adding explicit task management guidance to prAxIs OS MCP workflow tool responses to prevent AI from creating parallel TODO lists during workflow execution.

### 1.2 Scope
This feature will inject standardized guidance into all MCP workflow tool responses (`start_workflow`, `get_current_phase`, `get_task`, `complete_phase`) indicating that the workflow system manages tasks and external task tools should not be used.

---

## 2. Business Goals

### Goal 1: Enforce Single-Source-of-Truth for Task Management

**Objective:** Eliminate AI-created parallel task tracking systems during workflow execution by making workflow system's role as task manager explicit in every tool response.

**Success Metrics:**
- **Parallel TODO creation rate**: 100% (current) → 0% (target)
- **Workflow execution consistency**: Variable (current) → 100% workflow-managed (target)
- **AI confusion incidents**: 1+ per workflow execution (current) → 0 (target)

**Business Impact:**
- **Users benefit**: Clearer workflow execution model, predictable AI behavior
- **Developers benefit**: Single task state to monitor and debug
- **System benefit**: Reduced complexity, fewer competing state management systems
- **Expected value**: Improved workflow reliability and user trust in guided execution patterns

### Goal 2: Maximize Workflow System Adoption

**Objective:** Increase confidence that workflows provide complete guidance by demonstrating clear ownership of task management lifecycle.

**Success Metrics:**
- **Workflow execution compliance**: Variable (current) → 100% (target)
- **User trust in workflow system**: Unknown (current) → Measurable increase through dogfooding feedback (target)

**Business Impact:**
- **prAxIs OS adoption**: More reliable workflows → increased user adoption
- **Dogfooding success**: Internal teams can confidently use workflows for complex tasks
- **Meta-framework validation**: Demonstrates workflows as complete, self-contained execution systems

---

## 2.1 Supporting Documentation

The business goals above are informed by:
- **problem-analysis.md**: Identified architectural constraint (cannot modify Cursor tools), root cause (missing guidance in MCP responses), and business impact (single-source-of-truth violation)
- **problem-analysis.md**: Extracted user need for AI to understand workflow system manages tasks
- **problem-analysis.md**: Documented importance of consistency in workflow execution patterns

See `supporting-docs/INDEX.md` for complete analysis with 26 extracted insights.

---

## 3. User Stories

User stories describe the feature from the user's perspective.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: AI Assistant Receives Clear Task Management Guidance

**As an** AI assistant executing an prAxIs OS workflow  
**I want to** receive explicit guidance in every workflow tool response that the workflow system manages all tasks  
**So that** I don't create parallel TODO lists and maintain single-source-of-truth for task state

**Acceptance Criteria:**
- Given I call `start_workflow()`, `get_current_phase()`, `get_task()`, or `complete_phase()`
- When the MCP server returns the response
- Then the response includes explicit fields indicating workflow-managed task execution mode
- And the response explicitly prohibits using external task tools like `todo_write`

**Priority:** Critical

---

### Story 2: Human User Monitors Single Task State

**As a** human user monitoring workflow execution  
**I want to** have a single source of truth for task progress and state  
**So that** I can clearly understand workflow progress without reconciling multiple task tracking systems

**Acceptance Criteria:**
- Given a workflow is executing
- When I check workflow state via `get_workflow_state()`
- Then all task status information comes from workflow system only
- And no parallel TODO lists exist to cause confusion

**Priority:** Critical

---

### Story 3: Developer Debugs Workflow Behavior

**As a** developer debugging workflow execution issues  
**I want to** see consistent workflow execution patterns without external task management  
**So that** I can identify issues in workflow design rather than AI task management choices

**Acceptance Criteria:**
- Given I'm reviewing workflow execution logs
- When I examine task progression
- Then all task state transitions are tracked solely through workflow checkpoints
- And no external TODO operations interfere with workflow flow

**Priority:** High

---

### Story 4: Workflow System Signals Operating Mode

**As the** prAxIs OS workflow system  
**I want to** clearly communicate my role as the task manager for active sessions  
**So that** AI assistants understand they should delegate task management to me

**Acceptance Criteria:**
- Given a workflow session is active
- When any workflow tool is invoked
- Then the response includes task management mode indicator
- And guidance persists across all tool calls (not just `start_workflow`)

**Priority:** Critical

---

## 3.1 Story Priority Summary

**Critical (Must-Have):**
- Story 1: AI receives clear task management guidance
- Story 2: Human monitors single task state
- Story 4: Workflow signals operating mode

**High Priority:**
- Story 3: Developer debugs workflow behavior

---

## 3.2 Supporting Documentation

User needs from supporting documents:
- **problem-analysis.md**: AI must understand when workflow system is managing tasks
- **problem-analysis.md**: Eliminate confusion from competing task management systems
- **problem-analysis.md**: Enable reliable, consistent workflow execution patterns

See `supporting-docs/INDEX.md` for details.

---

## 4. Functional Requirements

Functional requirements specify capabilities the system must provide.

---

### FR-1: Workflow Task Management Mode Indication

**Description:** The system shall include explicit task management mode indicators in all workflow tool responses (`start_workflow`, `get_current_phase`, `get_task`, `complete_phase`) to signal that the workflow manages task state.

**Priority:** Critical

**Related User Stories:** Story 1, Story 4

**Acceptance Criteria:**
- All workflow tool responses include a `⚠️_WORKFLOW_EXECUTION_MODE: "ACTIVE"` field or equivalent
- Mode indication is present in every workflow-related tool response, not just at workflow start
- Field is prominently positioned in response structure (top-level or first in dict)

---

### FR-2: Explicit External Task Tool Prohibition

**Description:** The system shall include explicit guidance in all workflow tool responses prohibiting the use of external task management tools (such as `todo_write`) during workflow execution.

**Priority:** Critical

**Related User Stories:** Story 1, Story 2

**Acceptance Criteria:**
- Response includes field like `🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS` with clear prohibition message
- Message explicitly names `todo_write` and other competing task tools
- Message explains WHY external tools should not be used (workflow is task manager)

---

### FR-3: Workflow Execution Model Communication

**Description:** The system shall communicate the workflow execution model (complete task → submit evidence → advance phase) in workflow tool responses.

**Priority:** High

**Related User Stories:** Story 1, Story 4

**Acceptance Criteria:**
- Response includes field describing workflow progression pattern
- Pattern is concise and actionable (e.g., "Complete task → Submit evidence → Advance phase")
- Model communicated consistently across all workflow tools

---

### FR-4: Universal Workflow Coverage

**Description:** The system shall apply task management guidance to all workflow types without requiring modifications to individual workflow markdown files or metadata.

**Priority:** Critical

**Related User Stories:** Story 3

**Acceptance Criteria:**
- Implementation works for all existing workflows (`spec_creation_v1`, `spec_execution_v1`, etc.)
- No changes required to workflow .md files in `universal/workflows/`
- No changes required to workflow `metadata.json` files
- Guidance injection happens at runtime in workflow engine

---

### FR-5: Backward Compatibility

**Description:** The system shall maintain 100% backward compatibility with existing workflow definitions and execution patterns.

**Priority:** Critical

**Related User Stories:** Story 3

**Acceptance Criteria:**
- All existing workflows continue to function without modification
- Response structure remains parseable by AI (additional fields don't break parsing)
- No breaking changes to workflow tool APIs or response schemas
- Existing workflow state files remain compatible

---

### FR-6: Response Size Efficiency

**Description:** The system shall keep response size increase minimal (< 200 bytes) when adding task management guidance.

**Priority:** Medium

**Related User Stories:** Story 4

**Acceptance Criteria:**
- Guidance fields add less than 200 bytes to each response
- No duplicate guidance across multiple response fields
- Concise, actionable messaging

---

### FR-7: Persistent Guidance Across Session

**Description:** The system shall provide task management guidance on every workflow tool invocation throughout the session lifecycle, not just at session start.

**Priority:** High

**Related User Stories:** Story 1, Story 4

**Acceptance Criteria:**
- Guidance present in `start_workflow()` response
- Guidance present in `get_current_phase()` responses
- Guidance present in `get_task()` responses
- Guidance present in `complete_phase()` responses
- Guidance persists even after workflow restarts/resumptions

---

## 4.1 Functional Requirements Summary

**Total Requirements:** 7  
**By Priority:**
- Critical: 5 (FR-1, FR-2, FR-4, FR-5, FR-7)
- High: 1 (FR-3)
- Medium: 1 (FR-6)

**Requirements Traceability:**
- Story 1 → FR-1, FR-2, FR-3, FR-7
- Story 2 → FR-2
- Story 3 → FR-4, FR-5
- Story 4 → FR-1, FR-3, FR-6, FR-7

---

## 5. Non-Functional Requirements

NFRs define quality attributes and system constraints.

---

### 5.1 Performance

**NFR-P1: Response Overhead**
- Task management guidance fields add < 200 bytes to each workflow tool response
- No measurable latency impact on workflow tool response times (< 1ms overhead)
- Guidance injection happens in memory without disk I/O

**NFR-P2: Scalability**
- Guidance injection scales to all workflow types without performance degradation
- No additional memory footprint per workflow session
- Implementation supports concurrent workflow executions without contention

---

### 5.2 Maintainability

**NFR-M1: Implementation Simplicity**
- Single injection point in `workflow_engine.py` (< 50 lines of code)
- No modifications to individual workflow files
- Clear separation of concerns (guidance logic separate from workflow logic)

**NFR-M2: Code Quality**
- 100% unit test coverage for response wrapper function
- Integration test validates end-to-end behavior (no TODO creation during workflow)
- Code follows existing prAxIs OS Python conventions and style

**NFR-M3: Documentation**
- Implementation documented in code comments
- Rationale documented in this spec
- User-facing impact: none (invisible to workflow content authors)

---

### 5.3 Compatibility

**NFR-C1: Backward Compatibility**
- 100% compatibility with existing workflow definitions
- No breaking changes to workflow tool APIs
- Existing workflow state files remain valid
- Workflows created before this feature continue functioning unchanged

**NFR-C2: Forward Compatibility**
- Design accommodates future workflow types without modification
- Guidance fields are optional/advisory (don't break if ignored)
- Can be extended with additional guidance patterns in future

---

### 5.4 Reliability

**NFR-R1: Fault Tolerance**
- If guidance injection fails, workflow tools still return valid responses
- Graceful degradation: missing guidance fields don't break workflow execution
- No introduction of new failure modes

**NFR-R2: Consistency**
- Guidance messaging is identical across all workflow tools
- No variance in guidance based on workflow type
- Deterministic behavior (same input → same guidance)

---

### 5.5 Usability (AI Experience)

**NFR-U1: Clarity**
- Guidance uses clear, directive language (🛑, ⚠️ emoji markers)
- Message explicitly states what NOT to do (`DO NOT use todo_write`)
- Rationale provided ("workflow IS your task manager")

**NFR-U2: Visibility**
- Guidance fields appear early in response structure (top-level)
- Field names use attention-grabbing prefixes (⚠️, 🛑)
- Persistent across all tool calls (not just first one)

---

### 5.6 Implementation Constraints

**NFR-I1: No External Dependencies**
- Implementation uses only Python standard library and existing prAxIs OS dependencies
- No new package requirements
- No new infrastructure requirements

**NFR-I2: Development Time**
- Total implementation time < 1 hour (as per problem analysis)
- Testing time < 30 minutes
- Total delivery time < 2 hours

---

## 5.7 Non-Functional Requirements Summary

**Total NFRs:** 13  
**By Category:**
- Performance: 2
- Maintainability: 3
- Compatibility: 2
- Reliability: 2
- Usability: 2
- Implementation: 2

**Critical NFRs:**
- NFR-C1: Backward compatibility (must not break existing workflows)
- NFR-R1: Fault tolerance (must degrade gracefully)
- NFR-U1: Clarity (guidance must be effective)

---

## 6. Out of Scope

Explicitly defines what is NOT included. Items may be considered for future phases.

### Explicitly Excluded

#### Features

**Not Included in This Release:**

1. **Modifying Cursor's todo_write Tool Description**
   - **Reason:** Architectural constraint - we cannot modify Cursor's built-in tools
   - **Future Consideration:** Could request Cursor add workflow awareness to their tools (not within our control)

2. **Visual UI for Workflow Task Management**
   - **Reason:** Focus is on AI-facing guidance, not human UI
   - **Future Consideration:** Could add dashboard showing workflow task state in future release

3. **Retroactive Application to Active Workflows**
   - **Reason:** Only applies to new workflow tool calls after deployment
   - **Future Consideration:** Not applicable - workflows in progress will complete with old behavior

4. **Custom Guidance Per Workflow Type**
   - **Reason:** Universal guidance simpler and more maintainable
   - **Future Consideration:** Could add workflow-specific messaging if needed, but not currently required

5. **Analytics on TODO Creation Prevention**
   - **Reason:** Out of scope for initial implementation - validation is manual/test-based
   - **Future Consideration:** Could add telemetry to track effectiveness

6. **Guidance Localization/Translation**
   - **Reason:** English-only for initial release
   - **Future Consideration:** If prAxIs OS adds i18n support, guidance could be localized

---

#### Platforms

**Not Supported:**
- Only applies to MCP-based workflow execution
- Does not affect non-workflow tool usage
- Does not affect workflows executed outside MCP context (if any exist)

---

#### Integration

**Not Integrated:**
- No changes to Cursor IDE behavior
- No changes to other MCP servers
- No changes to workflow markdown content

---

#### Quality Levels

**Not Required:**
- Sub-millisecond injection performance (< 1ms is sufficient per NFR-P1)
- Telemetry/observability of guidance effectiveness (manual validation only)
- A/B testing different guidance messages
- Machine learning to optimize guidance text

---

#### Compliance/Standards

**Not Applicable:**
- No security/privacy implications (guidance is advisory text)
- No accessibility requirements (AI-facing, not human UI)
- No regulatory compliance requirements

---

## 6.1 Future Phase Candidates

**Version 2.0 Enhancements:**
- Workflow-specific guidance customization
- Telemetry tracking guidance effectiveness
- Visual workflow task dashboard for humans
- Integration with other AI assistant platforms

**Conditional Features (if needed):**
- Guidance intensity levels (verbose/concise modes)
- Configurable guidance (allow disabling per deployment)
- Guidance for other competing tools beyond todo_write

---

## 7. Success Criteria

### 7.1 Definition of Done

This feature is complete when:

1. ✅ All workflow tool responses include task management guidance
2. ✅ Guidance explicitly prohibits external task tools
3. ✅ Implementation requires no workflow .md file changes
4. ✅ 100% backward compatibility maintained
5. ✅ Unit tests pass (response injection logic)
6. ✅ Integration test passes (AI doesn't create TODOs during workflow)
7. ✅ Code reviewed and merged
8. ✅ Dogfood validation: Run spec_creation_v1 and verify no TODO creation

### 7.2 Acceptance Testing

**Test Scenario 1: Workflow Execution Without TODOs**
- **Given:** AI starts spec_creation_v1 workflow
- **When:** AI executes all phases
- **Then:** No todo_write calls are made during workflow execution

**Test Scenario 2: Response Structure Validation**
- **Given:** Workflow tool is called
- **When:** Response is returned
- **Then:** Response includes `⚠️_WORKFLOW_EXECUTION_MODE`, `🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS`, and `execution_model` fields

**Test Scenario 3: Backward Compatibility**
- **Given:** Existing spec_execution_v1 workflow
- **When:** Workflow is executed with new code
- **Then:** Workflow completes successfully with same behavior as before (plus no TODOs)

**Test Scenario 4: Guidance Persistence**
- **Given:** Workflow session is active
- **When:** Multiple tool calls made (`get_current_phase`, `get_task`, `complete_phase`)
- **Then:** Guidance fields present in all responses

---

## 8. Appendix

### 8.1 Related Documents

- `supporting-docs/problem-analysis.md` - Detailed problem analysis and solution options
- `supporting-docs/INDEX.md` - Extracted insights from supporting documents
- `mcp_server/workflow_engine.py` - Implementation location
- `mcp_server/server/tools/workflow_tools.py` - Tool wrappers location

### 8.2 Glossary

- **MCP**: Model Context Protocol - the interface between AI and tools
- **Workflow**: Structured, phase-gated execution framework in prAxIs OS
- **TODO**: Task management item created via Cursor's todo_write tool
- **Guidance**: Advisory fields injected into workflow tool responses
- **Checkpoint**: Phase boundary validation gate in workflow execution

### 8.3 Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-08 | Initial SRD | AI Assistant via spec_creation_v1 |

---

**End of Software Requirements Document**


