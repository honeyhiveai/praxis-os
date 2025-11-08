# Supporting Documents Index

**Spec:** Workflow Breadcrumb Navigation System  
**Created:** 2025-11-08  
**Total Documents:** 1

## Document Catalog

### 1. Workflow Breadcrumb Navigation Design Document

**File:** `2025-11-08-workflow-breadcrumb-navigation.md`  
**Type:** Design Document  
**Purpose:** Detailed design for implementing a "breadcrumb trail" pattern in the workflow system to guide AI behavior by making the correct path the easiest path. Addresses the problem of AI agents skipping `get_phase` and `get_task` actions by only exposing the next action in the response.

**Relevance:** Requirements [H], Design [H], Implementation [H]

**Key Topics:**
- Breadcrumb Trail Pattern (revealing next action only)
- Workflow behavioral tuning
- Static vs. dynamic workflow content sourcing
- Progress gamification and guidance
- Evidence validation as the ultimate gate
- Easy path = right path philosophy

---

## Cross-Document Analysis

**Common Themes:**
- Behavioral probability engineering (making desired actions easiest)
- Preventing "optimization" by hiding future actions
- Sequential execution enforcement through just-in-time disclosure
- Workflow engine as source of truth for navigation

**Potential Conflicts:**
- None (single design document)

**Coverage Gaps:**
- Implementation details for dynamic workflows' task counting mechanism
- Edge cases for workflows with variable phase structures
- Fallback behavior if breadcrumbs fail to load

---

## Next Steps

This index will be used in Task 3 to systematically extract insights from the document. The extracted insights will be organized by:
- **Requirements Insights:** User needs (prevent task skipping), business goals (deterministic AI behavior)
- **Design Insights:** Breadcrumb pattern, guidance structure, dynamic vs. static workflow handling
- **Implementation Insights:** Code changes to `WorkflowEngine`, `add_workflow_guidance`, new `get_task_count` method

