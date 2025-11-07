# Task 3: Extract Key Insights

**Phase:** 0 (Supporting Documents Integration)  
**Purpose:** Extract and categorize insights for later phases  
**Estimated Time:** 10 minutes

---

## 🎯 Objective

Systematically extract specific insights from each supporting document, categorizing them by type (requirements, design, implementation). These insights will be referenced in later phases to inform specification content.

---

## Prerequisites

🛑 EXECUTE-NOW: Tasks 1 & 2 must be completed

- All documents must be accessible
- INDEX.md must exist with document catalog

⚠️ MUST-READ: Review INDEX.md to understand document landscape

---

## Steps

### Step 1: Read Each Document for Insights

For each document in INDEX.md, extract:

**Requirements:** User needs, business goals, functionality, constraints, out-of-scope  
**Design:** Architecture, components, technology, data models, APIs, security  
**Implementation:** Code patterns, testing, deployment, monitoring

📊 COUNT-AND-DOCUMENT: Documents reviewed [number], insights extracted [count]

### Step 2: Create Insights Document

Add insights section to INDEX.md:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/supporting-docs/INDEX.md << 'EOF'

---

## Extracted Insights

### Requirements Insights (Phase 1)

#### From {DOCUMENT_1_NAME}:
- **User Need:** {specific user need}
- **Business Goal:** {business objective}
- **Functional Req:** {desired functionality}
- **Constraint:** {limitation}

[Continue for all documents]

### Design Insights (Phase 2)

#### From {DOCUMENT_1_NAME}:
- **Architecture:** {approach/pattern}
- **Component:** {design/structure}
- **Data Model:** {schema design}
- **API:** {interface/contract}

[Continue for all documents]

### Implementation Insights (Phase 4)

#### From {DOCUMENT_1_NAME}:
- **Code Pattern:** {pattern}
- **Testing:** {strategy}
- **Deployment:** {guidance}

[Continue for all documents]

### Cross-References

**Validated by Multiple Sources:** {insights appearing in multiple docs}
**Conflicts:** {conflicting information - note sources and resolution needed}
**High-Priority:** {items emphasized across documents}

EOF
```

### Step 3: Review and Refine Insights

Review extracted insights for:

- **Completeness:** All relevant information captured
- **Clarity:** Insights specific and actionable
- **Organization:** Properly categorized
- **Traceability:** Attributed to source

### Step 4: Add Insight Summary

Add a quantitative summary to INDEX.md:

```bash
cat >> .praxis-os/specs/{SPEC_DIR}/supporting-docs/INDEX.md << 'EOF'

## Insight Summary

**Total:** {COUNT} insights  
**By Category:** Requirements [{count}], Design [{count}], Implementation [{count}]  
**Multi-source validated:** {count}  
**Conflicts to resolve:** {count}  
**High-priority items:** {count}

**Phase 0 Complete:** ✅ {DATE}

EOF
```

📊 COUNT-AND-DOCUMENT: Total insights [number], by category [Req/Design/Impl counts]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

- [ ] All documents analyzed, insights extracted (Req/Design/Impl) ✅/❌
- [ ] Insights specific, actionable, traceable to source ✅/❌
- [ ] Cross-references, conflicts, priorities identified ✅/❌
- [ ] Summary complete ✅/❌

🚨 FRAMEWORK-VIOLATION: Vague insights

Insights must be specific ("response time < 200ms" not "improve performance"), actionable, traceable, categorized.

📊 COUNT-AND-DOCUMENT: Docs [number], Insights [total: Req/Design/Impl], Quality [validated/conflicts/priority]

---

## Phase 0 Completion

🎯 PHASE-COMPLETE: Supporting documents processed

This phase is complete when you have:
- ✅ Created spec directory in correct location (`.praxis-os/specs/review/YYYY-MM-DD-name`)
- ✅ Copied all supporting documents to `supporting-docs/` subdirectory
- ✅ Created INDEX.md cataloging all documents with metadata
- ✅ Extracted categorized insights (requirements, design, implementation)
- ✅ Identified cross-references, conflicts, and high-priority items
- ✅ Added quantitative summary to INDEX.md

Submit checkpoint evidence to advance to Phase 1 (Requirements Gathering) where these insights will inform the creation of srd.md.
