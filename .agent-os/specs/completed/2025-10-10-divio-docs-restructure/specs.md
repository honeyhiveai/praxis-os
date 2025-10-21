# Technical Specifications

**Project:** Agent OS Enhanced Documentation Restructure  
**Date:** 2025-10-10  
**Based on:** srd.md (requirements)

---

## 1. Architecture Overview

### 1.1 Architectural Pattern

**Pattern:** Content Organization Architecture - Divio 4-Quadrant Framework

**Rationale:**
- **Current Problem:** Documentation scattered across flat structure with mixed content types (46% Divio compliance)
- **Solution:** Reorganize into clear quadrants (Tutorials, How-To Guides, Reference, Explanation) each serving distinct user needs
- **Pattern Selection:** Divio framework chosen because it's:
  - Proven documentation architecture standard
  - Addresses all user journey stages (learning, doing, looking up, understanding)
  - Measurable (compliance can be calculated)
  - Maintainable (clear boundaries prevent content type mixing)

**Related Requirements:**
- Business Goal 1: Increase documentation usability (FR-005: Directory structure reorganization)
- All user stories benefit from clear content type separation
- NFR-Q4: Divio compliance ≥90%

---

### 1.2 High-Level Architecture Diagram

```
Current State (46% Compliant):
docs/content/
├── intro.md (Explanation)
├── how-it-works.md (Mixed! Explanation + Instruction)
├── architecture.md (Explanation)
├── installation.md (Mixed! Reference + How-To)
├── mcp-tools.md (Reference)
├── standards.md (Explanation)
├── workflows.md (Explanation)
└── upgrading.md (Reference + How-To)

Target State (90%+ Compliant):
docs/
├── content/
│   ├── tutorials/ [NEW - 0% → 20%]
│   │   ├── first-5-minutes.md (Tutorial)
│   │   └── first-workflow.md (Tutorial)
│   │
│   ├── how-to-guides/ [NEW - 8% → 20%]
│   │   ├── create-custom-standards.md (How-To)
│   │   ├── debug-workflows.md (How-To)
│   │   ├── customize-language-standards.md (How-To)
│   │   ├── query-effectively.md (How-To)
│   │   ├── multi-project-setup.md (How-To)
│   │   └── cicd-integration.md (How-To)
│   │
│   ├── reference/ [REORGANIZED + ENHANCED - 60% → 25%]
│   │   ├── mcp-tools.md (Reference - ENHANCE)
│   │   ├── command-language.md (Reference - NEW)
│   │   ├── workflow-metadata.md (Reference - NEW)
│   │   └── file-structure.md (Reference - NEW)
│   │
│   └── explanation/ [REORGANIZED + REFACTORED - 70% → 25%]
│       ├── intro.md (Explanation - MOVE + AUDIT)
│       ├── architecture.md (Explanation - MOVE + AUDIT)
│       ├── standards.md (Explanation - MOVE + AUDIT)
│       ├── workflows.md (Explanation - MOVE + AUDIT)
│       ├── how-it-works.md (Explanation - MOVE + REFACTOR remove instruction)
│       └── concepts.md (Explanation - NEW glossary)
│
├── installation.md (Special case - keep at root)
├── upgrading.md (Special case - keep at root)
├── troubleshooting.md (NEW - add at root)
└── quick-reference.md (NEW - add at root)
```

---

### 1.3 Content Transformation Flow

```
Phase 1: Audit Existing Content
    ↓
[intro.md, architecture.md, etc.] → Type analysis → Classification map
    ↓
Phase 2: Directory Structure Setup
    ↓
Create: tutorials/, how-to-guides/, reference/, explanation/
    ↓
Phase 3: Content Migration
    ↓
┌─────────────┬──────────────────┬────────────────────┐
│ MOVE        │ REFACTOR         │ CREATE NEW         │
├─────────────┼──────────────────┼────────────────────┤
│ intro.md    │ how-it-works.md  │ first-5-minutes.md │
│ architecture│ (remove instr.)  │ first-workflow.md  │
│ standards.md│                  │ 6 how-to guides    │
│ workflows.md│                  │ command-language   │
│ mcp-tools.md│                  │ metadata reference │
│             │                  │ file-structure     │
│             │                  │ concepts.md        │
└─────────────┴──────────────────┴────────────────────┘
    ↓
Phase 4: Enhancement
    ↓
Add type badges, update navigation, implement search
    ↓
Phase 5: Validation
    ↓
Link check, Divio compliance check, build test
    ↓
Launch (90%+ Divio compliant)
```

**Key Principle:** Preserve existing quality content, reorganize structure, add missing pieces, refactor only where content type mixing occurs.

---

### 1.4 Infrastructure Architecture

```
User Browser
    ↓
Docusaurus Documentation Site (React-based static site)
    ├── Content Layer (Markdown files organized by Divio quadrant)
    │   ├── Type badge component (visual quadrant identification)
    │   └── Navigation (sidebars.ts configuration)
    │
    ├── Search Layer
    │   ├── Option A: Algolia DocSearch (preferred - free for OSS)
    │   └── Option B: Local search plugin (backup)
    │
    ├── Build Layer
    │   ├── Markdown → React components
    │   ├── Frontmatter parsing (doc_type, sidebar_position)
    │   └── Static HTML generation
    │
    └── Validation Layer (CI/CD)
        ├── Divio compliance script (validate doc_type distribution)
        ├── Link checker (0 broken links requirement)
        ├── Code example testing (all examples must work)
        └── Build test (site must build without errors)

MCP RAG Integration (Agent OS Enhanced feature)
    ↓
File Watcher monitors docs/ directory
    ↓
Documentation changes trigger RAG reindex (10-30 seconds)
    ↓
Updated docs queryable via MCP search_standards tool
```

**Infrastructure Components:**
1. **Docusaurus** - Static site generator (already in place, enhance configuration)
2. **Type Badge System** - React component for visual type identification (new)
3. **Search** - Algolia or local plugin for content discovery (new)
4. **CI/CD Validation** - Automated quality gates (new scripts)
5. **MCP RAG Integration** - Documentation indexed for AI query (existing, no changes needed)

**Related Requirements:**
- FR-006: Document type badge system
- FR-007: Search functionality integration
- FR-009: Divio compliance validation
- FR-010: Link and build validation
- NFR-M4: File watcher integration (already exists, leveraged not modified)

---

### 1.5 Deployment Architecture

```
GitHub Repository (main branch)
    ↓
Pull Request Created
    ↓
GitHub Actions CI/CD Pipeline Triggered
    │
    ├─→ Divio Compliance Check (scripts/validate-divio-compliance.py)
    │   └─→ Must be ≥80% to proceed
    │
    ├─→ Link Validation (check all internal links)
    │   └─→ Must have 0 broken links
    │
    ├─→ Code Example Testing (test all documentation code examples)
    │   └─→ All examples must execute successfully
    │
    └─→ Build Test (npm run build in docs/)
        └─→ Build must succeed without errors
    ↓
All Checks Pass → Merge Allowed
    ↓
Merge to main
    ↓
Deploy Pipeline Triggered
    │
    ├─→ Stage 1: Build Static Site (Docusaurus build)
    ├─→ Stage 2: Optimize Assets (image compression, minification)
    └─→ Stage 3: Deploy to Production (GitHub Pages / Netlify / Vercel)
    ↓
Production Documentation Site Live
    ↓
File Watcher Detects Changes (Agent OS Enhanced)
    ↓
RAG Index Updated (documentation searchable via MCP within 10-30 seconds)
```

**Deployment Targets:**
- **Primary:** GitHub Pages (gh-pages branch) - Free, integrated with GitHub
- **Backup:** Netlify or Vercel - Superior performance, preview deployments
- **Requirements:** Static hosting only (no server-side rendering needed)

**Related Requirements:**
- NFR-M3: Automated CI/CD validation
- NFR-P1: Site load time <2 seconds
- NFR-PO1: Platform compatibility (static site works everywhere)

---

### 1.6 Architectural Decisions

**Decision 1: Preserve Docusaurus (Don't Switch Documentation Platforms)**

**Rationale:**
- Docusaurus already in use, proven, working
- Supports all required features (React components, MDX, search integration, sidebar management)
- Platform switch would be massive scope creep (out of scope per section 6.2)
- Risk mitigation: Enhance existing platform rather than replace

**Tradeoff:** Locked into Docusaurus ecosystem vs platform flexibility
- **Chosen:** Docusaurus lock-in acceptable given stability and feature completeness
- **Alternative Rejected:** Hugo, MkDocs, Sphinx (would require complete migration, high risk)

---

**Decision 2: Divio 4-Quadrant Over Alternative Documentation Frameworks**

**Rationale:**
- Divio specifically designed to address documentation usability problems
- Measurable compliance (can calculate percentage)
- Clear user journey mapping (learning → doing → reference → understanding)
- Industry-proven framework with widespread adoption

**Tradeoff:** Divio strictness vs content flexibility
- **Chosen:** Strict quadrant separation (each doc fits ONE type)
- **Alternative Considered:** Task-based organization (rejected - less clear boundaries, harder to measure)
- **Alternative Considered:** Audience-based organization (rejected - users have all needs across journey)

**Requirements Supported:** Business Goal 1 (usability), NFR-Q4 (Divio compliance)

---

**Decision 3: Reorganization + Selective Addition Over Complete Rewrite**

**Rationale:**
- Existing explanation documentation is high quality (70% coverage)
- Complete rewrite wastes good content and introduces risk
- User explicitly warned previous spec attempt was "off focus" treating this as greenfield
- Design document explicitly states this is reorganization + enhancement (see section 2.3 migration table)

**Tradeoff:** Inconsistent authorship voice vs efficiency and risk
- **Chosen:** Accept some voice inconsistency to preserve quality and reduce risk
- **Alternative Rejected:** Complete documentation rewrite (wasteful, high risk, contradicts scope)

**Requirements Supported:** FR-008 (content migration and preservation), Out-of-Scope section 6.2 (not a complete rewrite)

**Evidence from Design Document:** Content migration table (section 2.3) explicitly lists MOVE, REFACTOR, ENHANCE actions - not REWRITE.

---

**Decision 4: Tutorials as Top Priority Over How-To Guides**

**Rationale:**
- Current tutorial coverage: 0% (most critical gap)
- Tutorials address new user onboarding (highest impact on abandonment)
- Business Goal 2 specifically targets time to first value via tutorials
- How-to guides also critical (8% coverage) but tutorials enable initial adoption

**Tradeoff:** Parallel development vs sequential focus
- **Chosen:** Sequential (tutorials Phase 1, how-to guides Phase 2)
- **Alternative Considered:** Parallel development (rejected - splits focus, harder to test, resource constraints)

**Requirements Supported:** User Story 1 (new user onboarding), Business Goal 2 (time to first value <15 min)

---

**Decision 5: Algolia Search Over Local Search Plugin**

**Rationale:**
- Algolia DocSearch free for open-source projects
- Superior performance (<100ms typical vs <500ms local)
- Handles typos, fuzzy matching, result ranking better
- Less build overhead (indexing happens externally)
- Search analytics built-in

**Tradeoff:** External dependency vs self-hosted control
- **Chosen:** Algolia (preferred), with local search as fallback if Algolia application rejected
- **Alternative:** Local search plugin (@easyops-cn/docusaurus-search-local) - backup option

**Requirements Supported:** FR-007 (search functionality), NFR-P2 (search response <500ms)

---

**Decision 6: Type Badges via Frontmatter + React Component Over Manual Badges**

**Rationale:**
- Frontmatter `doc_type` field enables automated validation (Divio compliance script)
- React component ensures consistency (single source of truth for badge styling)
- Automated > manual (reduces human error, maintainable)

**Tradeoff:** Setup complexity vs long-term maintainability
- **Chosen:** Automated system (higher upfront setup, better long-term)
- **Alternative Rejected:** Manual badge insertion in each file (error-prone, unmaintainable)

**Requirements Supported:** FR-006 (type badge system), NFR-Q4 (Divio compliance measurement)

---

### 1.7 Architectural Risks and Mitigations

**Risk 1: Content Migration Breaks Internal Links**

**Impact:** High - Users encounter 404 errors, bad experience
**Probability:** Medium - Many internal links exist across documents

**Mitigation:**
- Automated link validation in CI/CD (FR-010)
- Link checker blocks merge if broken links detected
- Test migration in feature branch before merging to main
- Manual link audit for root-level special cases

**Requirements:** NFR-Q3 (zero broken links)

---

**Risk 2: Divio Compliance Measurement Disagreements**

**Impact:** Medium - Ambiguity about what counts as "compliant"
**Probability:** Low - Divio framework is well-defined

**Mitigation:**
- Automated compliance script with explicit calculation (FR-009)
- Documented edge cases (root-level special cases, mixed legitimate cases)
- 80% minimum threshold allows some flexibility for edge cases
- Continuous measurement (not just end-of-project check)

**Requirements:** NFR-Q4 (Divio compliance ≥90% target, 80% minimum)

---

**Risk 3: Tutorial Success Rate <95% Target**

**Impact:** High - Blocks launch per success criteria
**Probability:** Medium - Tutorials on varied environments (macOS, Linux, Windows)

**Mitigation:**
- Extensive testing with 5+ users per tutorial across all platforms
- Iterate on tutorial content until 95% success rate achieved
- Include fallback instructions for edge cases
- Testing begins in Phase 1 (Tutorials) - early validation

**Requirements:** NFR-Q1 (tutorial success rate ≥95%), User Story 1 (new user onboarding)

---

**Risk 4: Search Integration Delays Launch**

**Impact:** Low - Search is enhancement, not blocker
**Probability:** Medium - Algolia application approval uncertain

**Mitigation:**
- Algolia application submitted early (during Phase 3)
- Local search plugin as backup (can be implemented independently)
- Search can be added post-launch if necessary (out of critical path)
- Core documentation usability doesn't depend on search (navigation sufficient)

**Requirements:** FR-007 (search functionality), NFR-P2 (search response <500ms)

---

**Risk 5: Type Badge Component Breaks Docusaurus Build**

**Impact:** Medium - Documentation site won't build
**Probability:** Low - React components well-supported in Docusaurus

**Mitigation:**
- Prototype badge component in Phase 5 (Infrastructure) before full rollout
- Test build in CI/CD catches issues before merge
- Badge component uses standard Docusaurus patterns (low complexity)
- Fallback: Can launch without badges, add later (not critical path)

**Requirements:** FR-006 (type badge system)

---

## 1.8 Architecture Summary

**Key Characteristics:**
- **Pattern:** Content organization architecture (Divio 4-quadrant framework)
- **Approach:** Reorganization + selective enhancement (NOT greenfield rewrite)
- **Platform:** Docusaurus (existing, enhanced with new features)
- **Quality:** Automated validation (Divio compliance, link checking, build testing)
- **Integration:** MCP RAG (existing, leveraged for documentation search)

**Architecture Supports:**
- 4 business goals (usability, time to value, support reduction, retention)
- 4 user stories (new user, experienced user, integrator, decision-maker)
- 10 functional requirements (content creation, reorganization, enhancement, infrastructure)
- 19 non-functional requirements (quality, maintainability, accessibility, performance, usability, portability)

**Next:** Component design defines specific modules implementing this architecture.

---

## 2. Component Design

This section defines the logical components implementing the documentation restructure. For a documentation project, "components" includes content modules, templates, automation scripts, and infrastructure pieces.

---

### 2.1 Component: Tutorial Content Module

**Purpose:** Provide hands-on, learning-oriented tutorials teaching Agent OS's main vehicle (spec-driven development) and workflow system.

**Responsibilities:**
- Create Tutorial 1: "Your First Agent OS Project" - Complete spec creation → spec execution cycle
- Create Tutorial 2: "Understanding Agent OS Workflows" - Workflow system deep dive
- Ensure tutorials work on fresh installation every time
- Provide immediate, visible results at each step
- Maintain learning-oriented focus (build understanding, not just complete tasks)
- Achieve 95%+ success rate through testing

**Requirements Satisfied:**
- FR-001: Tutorial Content Creation
- User Story 1: New User Onboarding
- Business Goal 2: Time to first value <15 minutes
- NFR-Q1: Tutorial success rate ≥95%

**Tutorial 1 Content Structure: "Your First Agent OS Project"**
```markdown
# Tutorial: Your First Agent OS Project

**Learning Goals**: 
- Understand Agent OS's main vehicle (spec-driven development)
- Experience the complete spec creation → spec execution cycle
- See how AI acts as code author while you orchestrate

**Time**: 15-20 minutes
**Prerequisites**: Agent OS installed

## What You'll Build
A simple feature (e.g., user profile API endpoint) using the complete Agent OS methodology

## Part 1: Design Conversation (3 minutes)
[Have conversational design discussion with AI]
[AI asks clarifying questions]
[You make decisions]
[Expected: AI understands requirements]

## Part 2: Create Specification (5 minutes)
[You say: "Create a spec for user profile API"]
[AI invokes spec_creation_v1 workflow automatically - explain this is happening]
[AI executes phases with checkpoint evidence]
[Expected: Spec files created in .agent-os/specs/]

## Part 3: Review Specification (3 minutes)
[Review generated srd.md, specs.md, tasks.md, implementation.md]
[Understand what each file contains]
[Expected: Complete specification ready for implementation]

## Part 4: Implement Specification (5 minutes)
[You say: "Implement the user profile spec"]
[AI invokes spec_execution_v1 workflow automatically - explain this is happening]
[AI writes code, tests, documentation]
[Expected: Working implementation with passing tests]

## Part 5: Review Implementation (2 minutes)
[See the generated code]
[Run tests to verify]
[Expected: Complete, working feature]

## What You Learned
- Spec-driven development is THE way to work in Agent OS
- AI acts as code author (writes 100%), you orchestrate (provide direction)
- Workflows (spec_creation_v1, spec_execution_v1) are automatic tools
- Quality is built-in through phase gating and testing

## Next Steps
Try [Tutorial 2: Understanding Agent OS Workflows] to go deeper on workflow system
```

**Tutorial 2 Content Structure: "Understanding Agent OS Workflows"**
```markdown
# Tutorial: Understanding Agent OS Workflows

**Learning Goals**:
- Understand what workflows are (phase-gated execution tools)
- Experience checkpoint evidence validation
- Learn to work with workflow state
- Understand how to create custom workflows (optional)

**Time**: 10-15 minutes
**Prerequisites**: Tutorial 1 complete

## What You'll Learn
How Agent OS workflows provide structure, prevent skipping steps, and ensure quality

## Part 1: What Are Workflows? (2 minutes)
[Explanation of phase-gated execution]
[Difference between workflows and general process]
[Expected: Clear mental model]

## Part 2: Experience Checkpoint Validation (4 minutes)
[Start a workflow]
[Try to advance without complete evidence]
[See validation failure]
[Provide correct evidence and advance]
[Expected: Understand evidence-based gating]

## Part 3: Workflow State (2 minutes)
[Check workflow state]
[See completed vs current phases]
[Understand resumption capability]
[Expected: Know how to track and resume workflows]

## Part 4: Creating Custom Workflows (Optional, 5 minutes)
[When you might need custom workflows]
[Basic structure (metadata.json, phases/, phase.md, task files)]
[Point to comprehensive how-to guide]
[Expected: Awareness of extensibility]

## What You Learned
- Workflows = structured tools (not loose processes)
- Phase gating prevents mistakes, enforces quality
- Evidence-based checkpoints ensure completeness
- You can create custom workflows for specialized needs

## Next Steps
- [How-To: Create Custom Workflows] for building your own
- [How-To: Debug Workflows] for troubleshooting
```

**Dependencies:**
- Requires: Agent OS installation with spec_creation_v1 and spec_execution_v1 workflows
- Requires: Tutorial templates (defined in this component)
- Provides: Foundational understanding of Agent OS's main vehicle

**Quality Criteria:**
- Tutorial 1 teaches complete spec cycle (THE main vehicle)
- Every step has expected output showing success
- No step can fail (guaranteed success through testing)
- Tutorial 1: 15-20 minutes, Tutorial 2: 10-15 minutes
- Tested on macOS, Linux, Windows with 5+ users
- 95%+ success rate verified before launch

**Error Handling:**
- If environment issue detected → Provide fallback instructions
- If workflow fails unexpectedly → Tutorial includes troubleshooting section
- If user doesn't understand spec artifacts → Tutorial explains each file's purpose
- If step unclear → Iterate tutorial content until 95%+ success rate

**Location:** 
- `docs/content/tutorials/your-first-agent-os-project.md`
- `docs/content/tutorials/understanding-agent-os-workflows.md`

---

### 2.2 Component: How-To Guide Content Module

**Purpose:** Provide goal-oriented, problem-solving guides for specific tasks.

**Responsibilities:**
- Create minimum 6 how-to guides covering common problems
- Solve ONE specific problem per guide
- Provide actionable steps without unnecessary explanation
- Allow flexibility for variations
- Include troubleshooting section

**Requirements Satisfied:**
- FR-002: How-To Guide Content Creation
- User Story 2: Problem-Solving for Experienced Users
- Business Goal 3: Decrease support burden -40%

**Content Structure:**
```markdown
# How To: {Specific Problem}

**Problem**: {One sentence problem statement}
**Time**: {Estimated duration}
**Prerequisites**: {What user needs}

## Quick Answer
{TL;DR for experienced users}

## Step-by-Step Guide

### Step 1: {Action}
[Instructions]
[Command/code]

### Step 2-N: ...

### Validation
[How to verify success]

## Variations
{Adaptations for different scenarios}

## Troubleshooting
**Issue**: {Common problem}
**Solution**: {Fix}

## Related
- [Reference doc]
- [Explanation doc]
```

**Dependencies:**
- Requires: Agent OS installed and understood
- Requires: How-to guide template (defined in this component)
- Provides: Problem resolution for experienced users

**Quality Criteria:**
- Solves stated problem completely
- Steps are actionable (verbs, not explanations)
- Links to explanation docs (doesn't repeat them)
- Includes troubleshooting for common issues

**Error Handling:**
- If problem not solved → Guide fails acceptance criteria, must revise
- If too much explanation → Refactor to link reference/explanation docs

**Location:** `docs/content/how-to-guides/{guide-name}.md`

**Guides to Create:**
1. create-custom-standards.md
2. debug-workflows.md  
3. customize-language-standards.md
4. query-effectively.md
5. multi-project-setup.md
6. cicd-integration.md

---

### 2.3 Component: Reference Documentation Module

**Purpose:** Provide complete, information-oriented technical reference.

**Responsibilities:**
- Enhance existing mcp-tools.md with additional examples
- Create command language reference (complete symbol catalog)
- Create workflow metadata reference (metadata.json schema)
- Create file structure reference (edit safety matrix)
- Describe without instructing (information-oriented)

**Requirements Satisfied:**
- FR-003: Reference Documentation Enhancement and Creation
- User Story 3: API and Structure Reference
- Business Goal 1: Documentation usability

**Content Structure:**
```markdown
# Reference: {Topic}

Complete reference for {what}

## Overview
{Brief description}

## {Section 1}

### {Item 1}
**Description:** {What it is}
**Usage:** `{syntax}`
**Parameters:**
- `param1`: {type} - {description}

**Example:**
```language
{working example}
```

## {Section 2-N}
...
```

**Dependencies:**
- Requires: Agent OS codebase (for API reference accuracy)
- Requires: Reference template (defined in this component)
- Provides: Lookup information for integrators

**Quality Criteria:**
- Every API/tool/config documented
- Every example is tested and works
- No instructional steps (describe, don't instruct)
- Edit safety clearly indicated

**Error Handling:**
- If API changes → Reference must update (file watcher triggers reindex)
- If incomplete → Fails FR-003 acceptance criteria

**Location:** `docs/content/reference/{topic}.md`

**References to Create/Enhance:**
1. mcp-tools.md (ENHANCE existing)
2. command-language.md (NEW)
3. workflow-metadata.md (NEW)
4. file-structure.md (NEW)

---

### 2.4 Component: Explanation Documentation Module

**Purpose:** Provide understanding-oriented conceptual explanations.

**Responsibilities:**
- Reorganize existing explanation docs into explanation/ directory
- Audit for type purity (no instruction mixed in)
- Refactor how-it-works.md to remove instructional content
- Create concepts/glossary document
- Explain "why" not "how"

**Requirements Satisfied:**
- FR-004: Explanation Content Organization and Refactoring
- User Story 4: Understanding Architecture and Design Decisions
- Business Goal 4: User retention

**Content Structure:**
```markdown
# Explanation: {Concept}

Understanding {what} and why it matters

## What is {Concept}?
{Definition}

## Why {Concept} Matters
{Rationale, business value}

## How {Concept} Works
{Conceptual explanation without step-by-step instructions}

## Alternatives and Tradeoffs
{Other approaches, why this one chosen}

## Design Decisions
{Architectural choices, rationale}

## Related Concepts
- {Link to other explanation docs}
```

**Dependencies:**
- Requires: Existing explanation docs (to reorganize)
- Requires: Explanation template (defined in this component)
- Provides: Conceptual understanding for decision-makers

**Quality Criteria:**
- No instructional steps (if found → refactor out or move to how-to)
- Explains "why" not "how"
- Discusses alternatives and tradeoffs
- Design decisions justified with reasoning

**Error Handling:**
- If mixed content detected → Refactor to separate explanation from instruction
- If too procedural → Rewrite focusing on concepts

**Location:** `docs/content/explanation/{topic}.md`

**Files to Reorganize/Refactor:**
1. intro.md (MOVE + AUDIT)
2. architecture.md (MOVE + AUDIT)
3. standards.md (MOVE + AUDIT)
4. workflows.md (MOVE + AUDIT)
5. how-it-works.md (MOVE + REFACTOR - remove instruction)
6. concepts.md (NEW - glossary)

---

### 2.5 Component: Type Badge System

**Purpose:** Visual identification of document type (Divio quadrant).

**Responsibilities:**
- Create React component rendering type badges
- Parse `doc_type` frontmatter field
- Display badge with appropriate emoji and color
- Integrate with Docusaurus theme

**Requirements Satisfied:**
- FR-006: Document Type Badge System
- Business Goal 1: Documentation usability (visual clarity)

**Component Structure:**
```tsx
// docs/src/components/DocTypeBadge.tsx
import React from 'react';

const badges = {
  tutorial: { emoji: '🎓', label: 'Tutorial', color: '#10b981' },
  'how-to': { emoji: '📖', label: 'How-To', color: '#3b82f6' },
  reference: { emoji: '📚', label: 'Reference', color: '#8b5cf6' },
  explanation: { emoji: '💡', label: 'Explanation', color: '#f59e0b' },
};

export default function DocTypeBadge({ type }) {
  const badge = badges[type];
  return (
    <span style={{ 
      backgroundColor: badge.color, 
      color: 'white',
      padding: '0.2rem 0.6rem',
      borderRadius: '0.25rem',
      fontSize: '0.875rem',
      fontWeight: '600',
    }}>
      {badge.emoji} {badge.label}
    </span>
  );
}
```

**Dependencies:**
- Requires: Docusaurus React environment
- Requires: Frontmatter `doc_type` field in all docs
- Provides: Visual type identification for users

**Integration Points:**
- Import in doc pages via MDX
- Automatic rendering based on frontmatter
- Styling consistent with Docusaurus theme

**Error Handling:**
- If invalid doc_type → Fallback to "Unknown" badge or error message
- If missing doc_type → Validation script catches in CI/CD

**Location:** `docs/src/components/DocTypeBadge.tsx`

---

### 2.6 Component: Search Integration Module

**Purpose:** Enable users to find documentation quickly via search.

**Responsibilities:**
- Integrate Algolia DocSearch (preferred) or local search plugin (backup)
- Index all documentation content across all types
- Provide <500ms search response time
- Display document type in search results

**Requirements Satisfied:**
- FR-007: Search Functionality Integration
- NFR-P2: Search response time <500ms
- Business Goal 1: Documentation findability

**Configuration Structure:**
```javascript
// docusaurus.config.ts - Algolia option
module.exports = {
  themeConfig: {
    algolia: {
      apiKey: 'YOUR_API_KEY',
      indexName: 'agent-os-enhanced',
      appId: 'YOUR_APP_ID',
      contextualSearch: true,
      searchParameters: {
        facetFilters: ['type:content'],
      },
    },
  },
};

// Alternative: Local search plugin
plugins: [
  [
    require.resolve('@easyops-cn/docusaurus-search-local'),
    {
      hashed: true,
      indexDocs: true,
      indexBlog: false,
      indexPages: false,
      language: ['en'],
    },
  ],
],
```

**Dependencies:**
- Requires: Docusaurus site built and deployed
- Requires: Algolia account (for Algolia option) OR npm package (for local option)
- Provides: Search capability for users

**Integration Points:**
- Search bar in Docusaurus navbar
- Results display with document type indicator
- Analytics tracking search queries

**Error Handling:**
- If Algolia application rejected → Fall back to local search plugin
- If search slow → Check indexing configuration, optimize query
- If search unavailable → Site still usable via navigation

**Location:** Configuration in `docs/docusaurus.config.ts`

---

### 2.7 Component: Divio Compliance Validation Script

**Purpose:** Automated validation ensuring documentation maintains Divio compliance.

**Responsibilities:**
- Count documents by `doc_type` frontmatter field
- Calculate coverage percentages by type
- Calculate overall compliance score (0-100%)
- Enforce minimum thresholds (≥80% for merge)
- Exit 0 if compliant, exit 1 if non-compliant

**Requirements Satisfied:**
- FR-009: Divio Compliance Validation
- NFR-Q4: Divio compliance ≥90% target, 80% minimum
- NFR-M3: Automated CI/CD validation

**Script Structure:**
```python
# scripts/validate-divio-compliance.py
#!/usr/bin/env python3
"""Validate Divio compliance of documentation."""

import os
import yaml
from pathlib import Path

REQUIRED_COVERAGE = {
    'tutorial': 0.20,    # 20% of docs
    'how-to': 0.20,      # 20% of docs
    'reference': 0.25,   # 25% of docs
    'explanation': 0.25, # 25% of docs
}

def count_docs_by_type():
    """Count documents by doc_type frontmatter."""
    counts = {'tutorial': 0, 'how-to': 0, 'reference': 0, 'explanation': 0}
    
    for md_file in Path('docs/content').rglob('*.md'):
        with open(md_file) as f:
            content = f.read()
            if content.startswith('---'):
                end = content.index('---', 3)
                frontmatter = yaml.safe_load(content[3:end])
                doc_type = frontmatter.get('doc_type')
                if doc_type in counts:
                    counts[doc_type] += 1
    
    return counts

def validate_compliance():
    """Calculate and validate Divio compliance score."""
    counts = count_docs_by_type()
    total = sum(counts.values())
    
    compliance_score = 0
    for doc_type, count in counts.items():
        coverage = count / total if total > 0 else 0
        required = REQUIRED_COVERAGE[doc_type]
        compliance_score += min(coverage / required, 1.0)
    
    compliance_score = (compliance_score / 4) * 100
    
    if compliance_score < 80:
        print(f"❌ FAILED: Compliance score {compliance_score:.0f}% < 80%")
        return False
    
    print(f"✅ PASSED: Compliance score {compliance_score:.0f}%")
    return True

if __name__ == '__main__':
    import sys
    sys.exit(0 if validate_compliance() else 1)
```

**Dependencies:**
- Requires: Python 3.10+, PyYAML
- Requires: All docs have `doc_type` frontmatter
- Provides: Pass/fail signal for CI/CD

**Integration Points:**
- Called by GitHub Actions CI/CD pipeline
- Blocks merge if compliance <80%
- Provides clear error messages showing what's missing

**Error Handling:**
- If doc_type missing → Counted as "no type", fails validation
- If invalid doc_type → Ignored in counting, shows warning
- If total docs = 0 → Error, cannot calculate compliance

**Location:** `scripts/validate-divio-compliance.py`

---

### 2.8 Component: Link Validation Module

**Purpose:** Ensure zero broken links across documentation.

**Responsibilities:**
- Validate all internal links within documentation
- Warn on broken external links
- Block deployment if broken internal links detected
- Integrate with CI/CD pipeline

**Requirements Satisfied:**
- FR-010: Link and Build Validation
- NFR-Q3: Zero broken internal links
- NFR-M3: Automated CI/CD validation

**Implementation Approach:**
```bash
# Using docusaurus-plugin-content-docs built-in link checking
# + custom script for additional validation

# docs/package.json
{
  "scripts": {
    "check-links": "node scripts/check-links.js",
    "build": "docusaurus build" // includes link checking
  }
}

# scripts/check-links.js
// Custom link checker for internal links
const fs = require('fs');
const path = require('path');

function checkLinks() {
  // 1. Parse all markdown files
  // 2. Extract internal links [text](path)
  // 3. Verify target files exist
  // 4. Report broken links
  // 5. Exit 1 if any broken, 0 if all valid
}
```

**Dependencies:**
- Requires: Docusaurus build system
- Requires: Node.js for custom script
- Provides: Link integrity guarantee

**Integration Points:**
- Runs during Docusaurus build (automatic)
- Custom script runs in CI/CD pipeline
- Blocks deployment if failures detected

**Error Handling:**
- If broken internal link → CI/CD fails, deployment blocked
- If broken external link → Warning only, doesn't block
- If malformed link syntax → Build error, clear message

**Location:** `scripts/check-links.js` + Docusaurus built-in

---

### 2.9 Component: Content Migration Module

**Purpose:** Systematically migrate existing documentation into new structure.

**Responsibilities:**
- Execute content migration table (existing file → target location → action)
- Preserve git history where possible
- Update internal links to reflect new paths
- Document migration process for reference

**Requirements Satisfied:**
- FR-005: Directory Structure Reorganization
- FR-008: Content Migration and Preservation
- Out-of-Scope: NOT complete rewrite

**Migration Table (Execution Plan):**

| Current File | Target Location | Action | Link Updates |
|--------------|-----------------|--------|--------------|
| `intro.md` | `explanation/intro.md` | MOVE + AUDIT type purity | Update refs |
| `architecture.md` | `explanation/architecture.md` | MOVE + AUDIT | Update refs |
| `standards.md` | `explanation/standards.md` | MOVE + AUDIT | Update refs |
| `workflows.md` | `explanation/workflows.md` | MOVE + AUDIT | Update refs |
| `how-it-works.md` | `explanation/how-it-works.md` | MOVE + REFACTOR (remove instruction) | Update refs |
| `mcp-tools.md` | `reference/mcp-tools.md` | MOVE + ENHANCE (add examples) | Update refs |
| `installation.md` | `installation.md` (root) | KEEP (special case) | No change |
| `upgrading.md` | `upgrading.md` (root) | KEEP (special case) | No change |

**Dependencies:**
- Requires: Git repository access
- Requires: Link validation module (to verify no breaks)
- Provides: Reorganized documentation structure

**Migration Commands:**
```bash
# Use git mv to preserve history
git mv docs/content/intro.md docs/content/explanation/intro.md
git mv docs/content/architecture.md docs/content/explanation/architecture.md
# ... etc

# Update links (manual or script-assisted)
# Run link validation to verify no breaks
```

**Error Handling:**
- If git history lost → Acceptable for non-critical files, prioritize functioning site
- If link breaks detected → Fix before proceeding
- If merge conflict → Resolve manually, preserve both changes

**Location:** Migration executed as part of Phase 3 implementation

---

### 2.10 Component: CI/CD Validation Pipeline

**Purpose:** Automated quality gates ensuring documentation meets all requirements.

**Responsibilities:**
- Run Divio compliance validation
- Run link validation
- Test code examples in documentation
- Build documentation site
- Block merge if any validation fails

**Requirements Satisfied:**
- NFR-M3: Automated CI/CD validation <5 minutes
- FR-009: Divio compliance validation
- FR-010: Link and build validation

**Pipeline Structure:**
```yaml
# .github/workflows/docs-validation.yml
name: Documentation Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install pyyaml
          cd docs && npm install
      
      - name: Validate Divio Compliance
        run: python scripts/validate-divio-compliance.py
      
      - name: Check Links
        run: cd docs && npm run check-links
      
      - name: Build Documentation
        run: cd docs && npm run build
      
      - name: Test Code Examples (if applicable)
        run: python scripts/test-doc-examples.py
```

**Dependencies:**
- Requires: GitHub Actions (or equivalent CI/CD platform)
- Requires: All validation scripts implemented
- Provides: Deployment gate

**Integration Points:**
- Triggers on every push and pull request
- Results displayed in GitHub PR checks
- Merge blocked if any step fails

**Error Handling:**
- If validation fails → Clear error message, link to failing check
- If timeout → Increase timeout threshold, optimize scripts
- If flaky tests → Fix test reliability before enforcing

**Location:** `.github/workflows/docs-validation.yml`

---

### 2.11 Component Interaction Summary

**Content Flow:**
```
1. Content Creation
   Tutorial Module → Tutorial files (tutorials/)
   How-To Module → How-to files (how-to-guides/)
   Reference Module → Reference files (reference/)
   Explanation Module → Explanation files (explanation/)

2. Content Organization
   Migration Module → Moves existing files
   Link updates → Maintains integrity

3. Visual Enhancement
   Type Badge System → Adds visual indicators
   Docusaurus → Renders final site

4. Quality Assurance
   Divio Compliance Script → Validates type distribution
   Link Validation → Ensures no broken links
   CI/CD Pipeline → Orchestrates all checks

5. User Discovery
   Search Integration → Enables content finding
   Navigation (Docusaurus) → Structured browsing
```

**Component Dependencies:**
- Content modules are independent (can be created in parallel)
- Migration module depends on target directory structure existing
- Type badge system depends on doc_type frontmatter in all files
- Validation scripts depend on content being in place
- CI/CD pipeline depends on all validation scripts being implemented
- Search integration can be added independently (not blocking)

**Next:** API/Interface specifications define how components interact with Docusaurus and external tools.

---

## 3. API & Interface Specifications

For this documentation project, "APIs" refer to configuration interfaces, frontmatter schemas, and integration points with Docusaurus and external tools.

---

### 3.1 Document Frontmatter Schema

**Purpose:** Standardized metadata for all documentation files.

**Schema:**
```yaml
---
sidebar_position: number     # Controls ordering in sidebar (1, 2, 3...)
doc_type: string            # REQUIRED: "tutorial" | "how-to" | "reference" | "explanation"
title: string              # Optional: Override default title from # heading
description: string        # Optional: Meta description for SEO
keywords: array           # Optional: SEO keywords
---
```

**Validation Rules:**
- `doc_type` is REQUIRED (enforced by Divio compliance script)
- `doc_type` must be one of: tutorial, how-to, reference, explanation
- `sidebar_position` recommended for controlling order
- All other fields optional

**Example:**
```markdown
---
sidebar_position: 1
doc_type: tutorial
title: Your First 5 Minutes with Agent OS
description: A guaranteed-success tutorial to get started with Agent OS in 5 minutes
keywords: [tutorial, getting started, onboarding, first steps]
---

# Tutorial: Your First 5 Minutes with Agent OS
...
```

**Related Requirements:** FR-006 (type badges), FR-009 (Divio compliance)

---

### 3.2 Docusaurus Configuration Interface

**Purpose:** Configure documentation site behavior, navigation, and integrations.

**Primary Configuration File:** `docs/docusaurus.config.ts`

**Key Configuration Sections:**

```typescript
// docs/docusaurus.config.ts
import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';

const config: Config = {
  title: 'Agent OS Enhanced',
  tagline: 'Multi-Agent Development Framework',
  url: 'https://honeyhiveai.github.io',
  baseUrl: '/agent-os-enhanced/',
  
  // Theme configuration
  themeConfig: {
    navbar: {
      title: 'Agent OS Enhanced',
      items: [
        {type: 'doc', docId: 'intro', position: 'left', label: 'Docs'},
        {href: 'https://github.com/honeyhiveai/agent-os-enhanced', label: 'GitHub', position: 'right'},
      ],
    },
    
    // Search integration (Algolia preferred)
    algolia: {
      apiKey: 'YOUR_API_KEY',
      indexName: 'agent-os-enhanced',
      appId: 'YOUR_APP_ID',
      contextualSearch: true,
    },
    
    // Alternative: Local search
    // (configured in plugins section if Algolia unavailable)
  },
  
  // Plugins
  plugins: [
    // Conditional: Local search if Algolia unavailable
    // [
    //   require.resolve('@easyops-cn/docusaurus-search-local'),
    //   {
    //     hashed: true,
    //     indexDocs: true,
    //     language: ['en'],
    //   },
    // ],
  ],
};

export default config;
```

**Configuration Points:**
- **Navigation:** Navbar and footer links
- **Search:** Algolia or local search plugin
- **Theme:** Colors, fonts, styling
- **Plugins:** Additional functionality
- **SEO:** Meta tags, sitemap generation

**Related Requirements:** FR-007 (search), NFR-P1 (site performance)

---

### 3.3 Sidebar Configuration Interface

**Purpose:** Control documentation navigation hierarchy and ordering.

**Configuration File:** `docs/sidebars.ts`

**Structure:**
```typescript
// docs/sidebars.ts
import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro', // Root intro page
    
    {
      type: 'category',
      label: '🎓 Tutorials',
      collapsible: true,
      collapsed: false, // Open by default
      items: [
        'tutorials/first-5-minutes',
        'tutorials/first-workflow',
      ],
    },
    
    {
      type: 'category',
      label: '📖 How-To Guides',
      collapsible: true,
      items: [
        'how-to-guides/create-custom-standards',
        'how-to-guides/debug-workflows',
        'how-to-guides/customize-language-standards',
        'how-to-guides/query-effectively',
        'how-to-guides/multi-project-setup',
        'how-to-guides/cicd-integration',
      ],
    },
    
    {
      type: 'category',
      label: '📚 Reference',
      collapsible: true,
      items: [
        'reference/mcp-tools',
        'reference/command-language',
        'reference/workflow-metadata',
        'reference/file-structure',
      ],
    },
    
    {
      type: 'category',
      label: '💡 Explanation',
      collapsible: true,
      items: [
        'explanation/concepts',
        'explanation/architecture',
        'explanation/standards',
        'explanation/workflows',
        'explanation/how-it-works',
      ],
    },
    
    'installation',
    'upgrading',
    'troubleshooting',
    'quick-reference',
  ],
};

export default sidebars;
```

**Ordering Rules:**
- Items listed in display order (top to bottom)
- Categories can be collapsed/expanded
- `sidebar_position` in frontmatter overrides file order within category
- Emojis in labels provide visual Divio quadrant identification

**Related Requirements:** FR-005 (directory reorganization), NFR-A3 (clear navigation)

---

### 3.4 Divio Compliance Validation API

**Purpose:** Programmatic interface for validating documentation compliance.

**Script:** `scripts/validate-divio-compliance.py`

**Interface:**
```python
# Command-line interface
$ python scripts/validate-divio-compliance.py
# Exit code 0: Compliant (≥80%)
# Exit code 1: Non-compliant (<80%)

# Output format:
Total documents: {N}

Current coverage:
  ✅ tutorial: {N} docs ({X}%) - required: 20%
  ✅ how-to: {N} docs ({X}%) - required: 20%
  ✅ reference: {N} docs ({X}%) - required: 25%
  ❌ explanation: {N} docs ({X}%) - required: 25%

Divio compliance score: {X}%

❌ FAILED: Compliance score must be ≥80%
```

**Programmatic Interface:**
```python
from validate_divio_compliance import count_docs_by_type, validate_compliance

# Get document counts
counts = count_docs_by_type()
# Returns: {'tutorial': N, 'how-to': N, 'reference': N, 'explanation': N}

# Validate compliance
is_compliant = validate_compliance()
# Returns: bool (True if ≥80%, False otherwise)
```

**Integration:** Called by CI/CD pipeline, blocks merge if non-compliant

**Related Requirements:** FR-009 (Divio validation), NFR-Q4 (compliance ≥90%)

---

### 3.5 MCP RAG Integration Interface

**Purpose:** Documentation searchable via Agent OS Enhanced MCP tools.

**Note:** This integration already exists in Agent OS Enhanced. Documentation restructure leverages existing capability without modification.

**How It Works:**
1. File watcher monitors `docs/` directory for changes
2. Changes trigger incremental RAG index update
3. Documentation becomes queryable via `search_standards` MCP tool within 10-30 seconds
4. AI agents can query documentation semantically

**No API Changes Required:** Existing MCP tools work with reorganized documentation structure automatically.

**Query Example:**
```python
# AI agent queries documentation
mcp_agent-os-rag_search_standards(
    query="How do I create custom standards?",
    target_directories=["docs/"],
    n_results=5
)

# Returns relevant chunks from how-to guide, reference docs, explanation docs
```

**Benefits:**
- Documentation discoverable via semantic search (not just keyword matching)
- Context-efficient (returns 2-5KB chunks vs 50KB full files)
- Self-updating (file watcher handles reindexing automatically)

**Related Requirements:** NFR-M4 (file watcher integration), Business Goal 1 (usability)

---

### 3.6 GitHub Actions CI/CD Pipeline Interface

**Purpose:** Automated quality validation on every pull request.

**Trigger:** Push to any branch, pull request to main

**Pipeline Steps:**
```yaml
name: Documentation Validation
on: [push, pull_request]

jobs:
  validate:
    steps:
      - name: Validate Divio Compliance
        run: python scripts/validate-divio-compliance.py
        # Exit code 1 → Pipeline fails, blocks merge
        
      - name: Check Links
        run: cd docs && npm run check-links
        # Broken links → Pipeline fails, blocks merge
        
      - name: Build Documentation
        run: cd docs && npm run build
        # Build failure → Pipeline fails, blocks merge
        
      - name: Test Code Examples
        run: python scripts/test-doc-examples.py
        # Example failure → Pipeline fails, blocks merge
```

**Status Reporting:** Results displayed in GitHub PR checks interface

**Merge Blocking:** If any step fails, merge is blocked until fixed

**Related Requirements:** NFR-M3 (CI/CD validation <5 minutes), FR-009, FR-010

---

### 3.7 External Tool Integration Points

**Algolia DocSearch API:**
```javascript
// Algolia configuration
{
  apiKey: 'search-only-api-key',  // Public search key
  indexName: 'agent-os-enhanced',
  appId: 'application-id',
  
  // Algolia crawler configuration (algolia-config.json)
  {
    "index_name": "agent-os-enhanced",
    "start_urls": ["https://honeyhiveai.github.io/agent-os-enhanced/"],
    "selectors": {
      "lvl0": "header h1",
      "lvl1": "article h2",
      "lvl2": "article h3",
      "text": "article p, article li"
    }
  }
}
```

**GitHub Pages Deployment:**
- Source: `gh-pages` branch
- Build: `npm run build` → `build/` directory
- Deploy: Push `build/` contents to `gh-pages` branch
- URL: `https://honeyhiveai.github.io/agent-os-enhanced/`

**Alternative: Netlify Deployment:**
- Build command: `cd docs && npm run build`
- Publish directory: `docs/build`
- Deploy previews: Automatic for pull requests

**Related Requirements:** FR-007 (search), NFR-P1 (performance), NFR-PO1 (platform compatibility)

---

### 3.8 API Summary

**Configuration Interfaces:**
1. Document frontmatter (YAML schema)
2. Docusaurus config (TypeScript)
3. Sidebar config (TypeScript)

**Validation Interfaces:**
4. Divio compliance script (Python CLI)
5. Link checker (Node.js script)
6. CI/CD pipeline (GitHub Actions YAML)

**Integration Interfaces:**
7. MCP RAG (existing, no changes)
8. Algolia DocSearch (external API)
9. Deployment platforms (GitHub Pages, Netlify)

**All interfaces designed for:**
- Automation (minimal manual intervention)
- Validation (catch errors before deployment)
- Integration (work together seamlessly)

**Next:** Data models define document structures and configuration schemas.

---

## 4. Data Models

For documentation projects, "data models" refer to content structures, configuration schemas, and metadata formats.

---

### 4.1 Document Content Model

**Tutorial Document Model:**
```markdown
---
doc_type: tutorial
sidebar_position: {N}
---

# Tutorial: {Title}

**Learning Goals**: {List of learning objectives}
**Time**: {Duration estimate}
**Prerequisites**: {What's required}

## What You'll Build
{Tangible outcome description}

## Step 1: {Action} ({time})
{Command or action}
{Expected output}
{Brief explanation}

## Step N: ...

## What You Learned
- {Takeaway 1}
- {Takeaway 2}

## Next Steps
{Link to next content}
```

**How-To Guide Document Model:**
```markdown
---
doc_type: how-to
sidebar_position: {N}
---

# How To: {Specific Problem}

**Problem**: {One sentence}
**Time**: {Duration}
**Prerequisites**: {Requirements}

## Quick Answer
{TL;DR}

## Step-by-Step Guide

### Step 1-N: {Actions}
{Instructions}

## Variations
{Adaptations}

## Troubleshooting
{Common issues + solutions}

## Related
{Links}
```

**Reference Document Model:**
```markdown
---
doc_type: reference
sidebar_position: {N}
---

# Reference: {Topic}

Complete reference for {what}

## {Category 1}

### {Item 1}
**Description:** {What it is}
**Usage:** `{syntax}`
**Parameters**: {List}
**Example:** {Working code}

## {Category N}: ...
```

**Explanation Document Model:**
```markdown
---
doc_type: explanation
sidebar_position: {N}
---

# Explanation: {Concept}

Understanding {what} and why it matters

## What is {Concept}?
{Definition}

## Why {Concept} Matters
{Rationale}

## How {Concept} Works
{Conceptual explanation}

## Alternatives and Tradeoffs
{Comparison}

## Design Decisions
{Architectural choices}
```

---

### 4.2 Configuration Data Models

**Docusaurus Config Model:**
```typescript
interface DocusaurusConfig {
  title: string;
  tagline: string;
  url: string;
  baseUrl: string;
  organizationName: string;
  projectName: string;
  
  themeConfig: {
    navbar: NavbarConfig;
    footer?: FooterConfig;
    algolia?: AlgoliaConfig;
  };
  
  plugins?: PluginConfig[];
  presets: PresetConfig[];
}
```

**Sidebar Config Model:**
```typescript
interface SidebarConfig {
  [sidebarId: string]: SidebarItem[];
}

type SidebarItem = 
  | string  // Doc ID
  | {
      type: 'category';
      label: string;
      collapsible?: boolean;
      collapsed?: boolean;
      items: SidebarItem[];
    };
```

---

### 4.3 Validation Data Model

**Divio Compliance Report:**
```typescript
interface DivioComplianceReport {
  total_documents: number;
  counts: {
    tutorial: number;
    'how-to': number;
    reference: number;
    explanation: number;
  };
  coverage: {
    tutorial: number;    // Percentage
    'how-to': number;
    reference: number;
    explanation: number;
  };
  compliance_score: number;  // 0-100
  is_compliant: boolean;     // true if ≥80%
  missing_coverage: string[]; // Areas below threshold
}
```

**Link Validation Report:**
```typescript
interface LinkValidationReport {
  total_links: number;
  broken_internal: string[];   // List of broken internal links
  broken_external: string[];   // List of broken external links
  is_valid: boolean;          // true if no broken internal links
}
```

---

### 4.4 Migration Data Model

**Content Migration Map:**
```typescript
interface MigrationEntry {
  source_path: string;           // Current file location
  target_path: string;           // New file location
  action: 'MOVE' | 'REFACTOR' | 'ENHANCE' | 'KEEP';
  requires_link_updates: boolean;
  notes?: string;
}

const migrationPlan: MigrationEntry[] = [
  {
    source_path: 'docs/content/intro.md',
    target_path: 'docs/content/explanation/intro.md',
    action: 'MOVE',
    requires_link_updates: true,
    notes: 'Audit for type purity after move'
  },
  // ... etc
];
```

---

### 4.5 Search Index Data Model (Algolia)

**Search Document Structure:**
```typescript
interface SearchDocument {
  objectID: string;         // Unique identifier
  title: string;            // Page title
  content: string;          // Page content (chunked)
  doc_type: 'tutorial' | 'how-to' | 'reference' | 'explanation';
  url: string;              // Full URL
  hierarchy: {
    lvl0: string;           // H1
    lvl1?: string;          // H2
    lvl2?: string;          // H3
  };
  keywords?: string[];
}
```

---

## 5. Security Considerations

For static documentation, security concerns are minimal but still important.

---

### 5.1 Content Security

**Sensitive Information:**
- ❌ NO API keys, credentials, or secrets in documentation
- ❌ NO internal-only information in public docs
- ✅ All examples use placeholder credentials
- ✅ Configuration examples marked as templates

**Example Sanitization:**
```yaml
# Good example (placeholder)
algolia:
  apiKey: 'YOUR_API_KEY'
  appId: 'YOUR_APP_ID'

# Bad example (real credentials - never do this!)
algolia:
  apiKey: 'a1b2c3d4e5f6...'  # ❌ NEVER commit real keys
```

**Related Requirements:** Standard security practices

---

### 5.2 Deployment Security

**GitHub Pages:**
- Deploy from `gh-pages` branch only (not main)
- Restrict write access to repository (maintainers only)
- Use branch protection rules on main
- Require pull request reviews before merge

**CI/CD Security:**
- GitHub Actions secrets for any API keys
- No secrets in repository files
- Audit CI/CD pipeline access regularly

---

### 5.3 User Privacy

**Analytics:**
- If analytics implemented (Google Analytics, Algolia insights)
- Privacy policy required
- Cookie consent if in EU jurisdictions
- GDPR compliance if applicable

**Note:** Privacy considerations out of scope for initial documentation restructure per section 6.2 (out of scope).

---

### 5.4 XSS Protection

**Markdown Sanitization:**
- Docusaurus sanitizes markdown by default
- No custom HTML injection allowed
- Code examples are rendered safely (escaped)

**React Component Safety:**
- Type badge component uses React (auto-escaped)
- No dangerouslySetInnerHTML usage
- Props validated via TypeScript

**Related Requirements:** NFR-A2 (accessibility), standard web security

---

## 6. Performance Optimization

Performance considerations for documentation site speed and responsiveness.

---

### 6.1 Build Performance

**Optimization Strategies:**
- Static site generation (pre-rendered HTML)
- Code splitting by route (automatic in Docusaurus)
- Tree shaking (remove unused code)
- Minification (CSS, JS, HTML)

**Build Targets:**
- Build time <5 minutes (NFR-M3)
- Production bundle optimized for size
- Image optimization (compress, WebP format)

**Measurement:**
```bash
# Measure build time
time npm run build

# Analyze bundle size
npx webpack-bundle-analyzer docs/build
```

**Related Requirements:** NFR-P3 (build performance <5 minutes)

---

### 6.2 Page Load Performance

**Optimization Strategies:**
- Static HTML (no server-side rendering needed)
- CDN delivery (GitHub Pages, Netlify)
- Asset compression (gzip, brotli)
- Lazy loading images
- Preload critical resources

**Performance Targets:**
- Initial load <2 seconds (NFR-P1)
- Time to Interactive <3 seconds
- Subsequent navigation <1 second (client-side routing)

**Measurement:**
```bash
# Lighthouse audit
npx lighthouse https://honeyhiveai.github.io/agent-os-enhanced/

# Target scores:
# Performance: >90
# Accessibility: >90
# Best Practices: >90
# SEO: >90
```

**Related Requirements:** NFR-P1 (page load <2s)

---

### 6.3 Search Performance

**Algolia Performance:**
- Algolia provides <100ms search responses (typical)
- Meets NFR-P2 requirement (<500ms) comfortably
- No optimization needed (handled by Algolia)

**Local Search Performance:**
- Local search plugin indexes at build time
- Search executes client-side (fast)
- Typical response time 50-200ms
- Meets NFR-P2 requirement (<500ms)

**Search Optimization:**
- Limit result count (10-20 results per query)
- Debounce search input (300ms delay)
- Cache recent searches client-side

**Related Requirements:** NFR-P2 (search <500ms)

---

### 6.4 Asset Optimization

**Image Optimization:**
- Compress images before committing
- Use WebP format where supported (PNG fallback)
- Lazy load images below fold
- Responsive images (srcset for different sizes)

**Code Optimization:**
- TypeScript compiled to optimized JavaScript
- React components tree-shaken
- CSS modules scoped and optimized
- Unused code eliminated in production build

**Font Optimization:**
- System fonts preferred (no web font loading)
- If custom fonts needed: subset, woff2 format, preload

**Related Requirements:** NFR-P3 (build performance)

---

### 6.5 Caching Strategy

**Static Asset Caching:**
- Immutable assets (JS, CSS bundles with hashes)
- Cache-Control: public, max-age=31536000, immutable
- HTML pages: Cache-Control: no-cache (always validate)

**CDN Caching:**
- GitHub Pages / Netlify handle caching automatically
- Assets served from edge locations (low latency)
- Automatic cache invalidation on deployment

**Service Worker:** (Optional future enhancement)
- Offline documentation browsing
- Faster subsequent page loads
- Not required for initial launch

**Related Requirements:** NFR-P1 (page load performance)

---

### 6.6 Performance Monitoring

**Continuous Monitoring:**
- Lighthouse CI in GitHub Actions
- Performance budgets enforced
- Regression detection on pull requests

**Performance Budget:**
```javascript
// lighthouse-budget.json
{
  "budget": [
    {
      "resourceSizes": [
        {"resourceType": "script", "budget": 300},      // 300KB
        {"resourceType": "stylesheet", "budget": 75},    // 75KB
        {"resourceType": "document", "budget": 50},      // 50KB
        {"resourceType": "image", "budget": 500},        // 500KB total
      ],
      "timings": [
        {"metric": "interactive", "budget": 3000},       // 3s TTI
        {"metric": "first-contentful-paint", "budget": 1500} // 1.5s FCP
      ]
    }
  ]
}
```

**Alerting:**
- CI/CD fails if performance budgets exceeded
- Forces optimization before merge

**Related Requirements:** NFR-P1, NFR-P3 (performance targets)

---

## Phase 2 Summary

**Completed Sections:**
1. ✅ Architecture Overview (Divio 4-quadrant, content organization, migration flow)
2. ✅ Component Design (11 components defined with responsibilities, interfaces, dependencies)
3. ✅ API & Interface Specifications (9 interfaces including frontmatter, configs, validation)
4. ✅ Data Models (document structures, configuration schemas, validation reports)
5. ✅ Security Considerations (content security, deployment, privacy, XSS protection)
6. ✅ Performance Optimization (build, page load, search, assets, caching, monitoring)

**Key Design Decisions:**
- Preserve Docusaurus (enhance, don't replace)
- Divio 4-quadrant framework (measurable compliance)
- Reorganization + selective addition (NOT greenfield rewrite)
- Tutorials as top priority (0% → 20% coverage)
- Algolia search preferred (local search backup)
- Automated validation (Divio compliance, link checking)

**Architectural Risks Mitigated:**
- Content migration breaking links → Automated link validation
- Divio compliance ambiguity → Automated measurement script
- Tutorial success rate → Extensive testing before launch
- Search delays → Backup option, not critical path
- Type badge issues → Prototype early, build testing

**Requirements Traceability:**
- Architecture supports 4 business goals, 4 user stories
- Components implement 10 functional requirements
- Interfaces enable 19 non-functional requirements
- All design decisions trace back to srd.md requirements

**Next:** Phase 3 (Implementation Plan) creates detailed task breakdown with phases, dependencies, and time estimates.

---

