# Task 3: Discover Requirements for Testing

**Phase:** 4 (Implementation Guidance)  
**Purpose:** Extract all FRs and NFRs from srd.md for test planning  
**Estimated Time:** 8 minutes

---

## 🎯 Objective

Extract all functional and non-functional requirements from srd.md to create a complete requirements list. This ensures every requirement gets mapped to tests.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1-2 must be completed

⚠️ MUST-READ: Query testing standards

```
MCP: pos_search_project(query="requirements traceability test coverage")
```

---

## Steps

### Step 1: Create testing directory

```bash
mkdir -p .praxis-os/specs/{SPEC_DIR}/testing
```

### Step 2: Extract all requirements from srd.md

Scan for FR and NFR sections, extract:
- Requirement ID
- Description
- Acceptance/measurement criteria
- Priority

### Step 3: Create requirements-list.md

Use table format:

```markdown
# Requirements List for Testing

## Functional Requirements
| FR ID | Description | Acceptance Criteria | Priority |
|-------|-------------|---------------------|----------|

## Non-Functional Requirements  
| NFR ID | Description | Measurement Criteria | Priority |
|--------|-------------|----------------------|----------|

## Summary
- Total Functional Requirements: {count}
- Total Non-Functional Requirements: {count}
- Total Requirements to Test: {total}
```

📊 COUNT-AND-DOCUMENT: 
- Total FRs: [number]
- Total NFRs: [number]
- FRs with acceptance criteria: [number]
- NFRs with measurement criteria: [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] testing/requirements-list.md created ✅/❌
- [ ] All FRs from srd.md extracted ✅/❌
- [ ] All NFRs from srd.md extracted ✅/❌
- [ ] Each requirement has criteria ✅/❌
- [ ] Counts documented in summary ✅/❌

🚨 FRAMEWORK-VIOLATION: Missing requirements

Every FR and NFR in srd.md MUST appear in requirements-list.md.

---

## Next Task

🎯 NEXT-MANDATORY: [task-4-requirements-traceability-matrix.md](task-4-requirements-traceability-matrix.md)

