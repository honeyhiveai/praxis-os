# Implementation Tasks

**Project:** Divio Documentation System Restructure  
**Date:** 2025-10-10  
**Status:** Draft - Pending Approval

---

## Time Estimates

- **Phase 1: Foundation & Infrastructure:** 4-6 hours (Directory structure, type badges, validation tooling)
- **Phase 2: Tutorial Content Creation:** 8-10 hours (2 tutorials with testing)
- **Phase 3: How-To Guide Content Creation:** 10-13 hours (5 how-to guides)
- **Phase 4: Reference & Explanation Reorganization:** 6-8 hours (Refactor existing content)
- **Phase 5: Search Integration:** 2-3 hours (Algolia configuration)
- **Phase 6: Validation Automation & Finalization:** 2.5-3.5 hours (Pre-commit hooks, CI/CD, migration report)
- **Total:** 32-43.5 hours (4-5.5 days of focused work)

---

## Phase 1: Foundation & Infrastructure

**Objective:** Establish directory structure, type badge system, and automated validation infrastructure that supports Divio compliance.

**Estimated Duration:** 4-6 hours

### Phase 1 Tasks

#### Task 1.1: Reorganize Directory Structure

**Description:** Create new `docs/content/tutorials/` and `docs/content/how-to-guides/` directories. Move existing files to appropriate Divio quadrants.

**Acceptance Criteria:**
- [ ] `docs/content/tutorials/` directory created
- [ ] `docs/content/how-to-guides/` directory created
- [ ] `docs/content/reference/` directory created (if not exists)
- [ ] `docs/content/explanation/` directory created (if not exists)
- [ ] Existing files moved to correct quadrants:
  - `installation.md` → `tutorials/` (will be refactored later)
  - `mcp-tools.md` → `reference/mcp-tools.md`
  - `how-it-works.md` → Keep in root for refactoring in Phase 4
  - `architecture.md` → `explanation/architecture.md`
  - `standards.md` → `reference/standards.md`
  - `workflows.md` → `reference/workflows.md`
- [ ] `sidebars.ts` updated to reflect new structure
- [ ] `_category_.json` files created for each directory with proper metadata
- [ ] All internal links updated to reflect new paths
- [ ] Build succeeds without errors: `npm run build`

**Time Estimate:** 1.5-2 hours

**Dependencies:** None (first task)

---

#### Task 1.2: Implement Type Badge System

**Description:** Create React component for Divio type badges and integrate into Docusaurus theme. Badges appear automatically based on frontmatter `doc_type` field.

**Acceptance Criteria:**
- [ ] `docs/src/components/DocTypeBadge.tsx` component created
- [ ] Component renders 4 badge types: 🎓 Tutorial, 📘 How-To, 📚 Reference, 💡 Explanation
- [ ] Component reads `doc_type` from frontmatter
- [ ] Component integrated into Docusaurus theme via `swizzle` or `docusaurus.config.ts`
- [ ] Badges appear at top of every doc page below title
- [ ] Badges have tooltips explaining each doc type
- [ ] CSS styling matches Agent OS brand (consistent with existing theme)
- [ ] Build succeeds: `npm run build`
- [ ] Visual verification on 5+ pages across all doc types

**Time Estimate:** 1.5-2 hours

**Dependencies:** Task 1.1 (directory structure must exist)

---

#### Task 1.3: Create Divio Compliance Validation Script

**Description:** Build Python script that validates documentation against Divio compliance criteria, checking frontmatter, content patterns, and structural requirements.

**Acceptance Criteria:**
- [ ] `scripts/validate-divio-compliance.py` script created
- [ ] Script validates frontmatter:
  - `doc_type` field exists and is one of: tutorial, how-to, reference, explanation
  - `sidebar_position` field exists (optional but recommended)
- [ ] Script validates content patterns:
  - Tutorials: Have learning goals, step-by-step structure, "What You Learned" section
  - How-To: Have goal statement, numbered steps, prerequisites
  - Reference: Have structured information, minimal prose
  - Explanation: Have background, concepts, trade-offs
- [ ] Script outputs:
  - Compliance score per file (0-100%)
  - List of violations with line numbers
  - Overall compliance percentage
  - Actionable remediation suggestions
- [ ] Script runs on all `.md` files in `docs/content/`
- [ ] Exit code 0 if compliance ≥90%, exit code 1 otherwise
- [ ] Script has `--strict` flag for 100% compliance requirement
- [ ] Script has `--report` flag to generate markdown report
- [ ] Documentation in script header explains usage
- [ ] Tested on 10+ existing docs to verify detection

**Time Estimate:** 2-3 hours

**Dependencies:** Task 1.1 (directory structure), Task 1.2 (type badge system as reference)

---

#### Task 1.4: Create Link Validation Module

**Description:** Build link validation that checks internal links, anchors, and external URLs for correctness. Integrates with build process.

**Acceptance Criteria:**
- [ ] `scripts/validate-links.py` script created
- [ ] Script validates:
  - Internal markdown links (relative paths)
  - Anchor links (section headers)
  - External URLs (HTTP 200 check with timeout)
  - Image paths
- [ ] Script outputs:
  - List of broken links with source file and line number
  - Total broken links count
  - Warnings for slow external links (>3s response)
- [ ] Script has `--skip-external` flag for faster local checks
- [ ] Script has `--report` flag for markdown report
- [ ] Exit code 0 if no broken links, exit code 1 otherwise
- [ ] Script runs in <30 seconds on full docs (with --skip-external)
- [ ] Tested on docs with intentionally broken links to verify detection
- [ ] Documentation in script header

**Time Estimate:** 1.5-2 hours

**Dependencies:** Task 1.1 (directory structure must be finalized)

---

### Phase 1 Validation Gate

🛑 **Phase 1 Completion Checkpoint:**

Before advancing to Phase 2:
- [ ] Directory structure fully reorganized and builds successfully
- [ ] Type badge system working on all doc pages
- [ ] Divio compliance validation script runs and produces report
- [ ] Link validation script runs and detects broken links
- [ ] All validation scripts documented and tested
- [ ] No broken links in current documentation
- [ ] Compliance baseline established (document current score)

**Evidence Required:**
- Screenshot of type badges on 3 different doc types
- Divio compliance report showing current baseline score
- Link validation report showing 0 broken links
- Successful build output from `npm run build`

---

## Phase 2: Tutorial Content Creation

**Objective:** Create 2 high-quality, guaranteed-success tutorials teaching Agent OS's main vehicle (spec-driven development) and workflow system.

**Estimated Duration:** 8-10 hours

### Phase 2 Tasks

#### Task 2.1: Write Tutorial 1 - "Your First Agent OS Project"

**Description:** Create comprehensive tutorial teaching complete spec creation → spec execution cycle using a simple example feature (e.g., user profile API endpoint).

**Acceptance Criteria:**
- [ ] File created: `docs/content/tutorials/your-first-agent-os-project.md`
- [ ] Frontmatter includes:
  ```yaml
  ---
  sidebar_position: 1
  doc_type: tutorial
  ---
  ```
- [ ] Tutorial structure includes:
  - **Learning Goals:** Clear list of what user will learn
  - **Time Estimate:** 15-20 minutes
  - **Prerequisites:** Agent OS installed
  - **What You'll Build:** Tangible outcome described
  - **Part 1: Design Conversation** (3 min) - Conversational design with AI
  - **Part 2: Create Specification** (5 min) - Trigger `spec_creation_v1` workflow
  - **Part 3: Review Specification** (3 min) - Understand spec artifacts
  - **Part 4: Implement Specification** (5 min) - Trigger `spec_execution_v1` workflow
  - **Part 5: Review Implementation** (2 min) - See generated code and tests
  - **What You Learned:** Key takeaways emphasizing spec-driven development as THE main vehicle
  - **Next Steps:** Link to Tutorial 2
- [ ] Every step has:
  - Concrete action (what to say/do)
  - Expected output (what user will see)
  - Success indicator (how to know it worked)
- [ ] Tutorial tested with 3 users on fresh Agent OS install
- [ ] Success rate ≥95% (all 3 users complete successfully)
- [ ] Tutorial takes 15-20 minutes for first-time users
- [ ] No vague instructions - every step is concrete
- [ ] Example feature is simple enough to complete in timeframe
- [ ] Type badge displays correctly: 🎓 Tutorial
- [ ] Links to Tutorial 2 and relevant how-to guides
- [ ] No broken links (verified with link validator)
- [ ] Divio compliance score ≥95%

**Time Estimate:** 5-6 hours (includes writing, testing with users, iteration)

**Dependencies:** Phase 1 complete (directory structure, type badges, validation)

---

#### Task 2.2: Write Tutorial 2 - "Understanding Agent OS Workflows"

**Description:** Create tutorial teaching the Agent OS workflow system (phase-gated execution, checkpoints, evidence validation, workflow state).

**Acceptance Criteria:**
- [ ] File created: `docs/content/tutorials/understanding-agent-os-workflows.md`
- [ ] Frontmatter includes:
  ```yaml
  ---
  sidebar_position: 2
  doc_type: tutorial
  ---
  ```
- [ ] Tutorial structure includes:
  - **Learning Goals:** Understand workflows as phase-gated tools, not general processes
  - **Time Estimate:** 10-15 minutes
  - **Prerequisites:** Tutorial 1 complete
  - **What You'll Learn:** Explicit description
  - **Part 1: What Are Workflows?** (2 min) - Definition, mental model
  - **Part 2: Experience Checkpoint Validation** (4 min) - Try to advance without evidence, then provide evidence
  - **Part 3: Workflow State** (2 min) - Check state, understand resumption
  - **Part 4: Creating Custom Workflows** (Optional, 5 min) - When/why/how overview, point to how-to guide
  - **What You Learned:** Workflows = tools, phase gating, evidence-based progression
  - **Next Steps:** Links to how-to guides for custom workflows
- [ ] Every step has concrete action, expected output, success indicator
- [ ] Tutorial tested with 3 users (who have completed Tutorial 1)
- [ ] Success rate ≥95%
- [ ] Tutorial takes 10-15 minutes
- [ ] Type badge displays: 🎓 Tutorial
- [ ] No broken links
- [ ] Divio compliance score ≥95%

**Time Estimate:** 3-4 hours (includes writing, testing, iteration)

**Dependencies:** Task 2.1 (Tutorial 1 must exist for prerequisite reference)

---

### Phase 2 Validation Gate

🛑 **Phase 2 Completion Checkpoint:**

Before advancing to Phase 3:
- [ ] Both tutorials written and tested
- [ ] Success rate ≥95% verified with real users (6 users total, 3 per tutorial)
- [ ] Tutorials take target time (15-20 min, 10-15 min)
- [ ] Type badges display correctly
- [ ] All links verified working
- [ ] Divio compliance ≥95% for both tutorials
- [ ] Tutorials demonstrate Agent OS's main vehicle clearly

**Evidence Required:**
- User testing results (6 users, success rate, time taken, feedback)
- Divio compliance report for both tutorials
- Screenshots of tutorials with type badges
- Link validation report

---

## Phase 3: How-To Guide Content Creation

**Objective:** Create 5 problem-solving how-to guides addressing common tasks and integration scenarios.

**Estimated Duration:** 10-13 hours

### Phase 3 Tasks

#### Task 3.1: Write How-To - "Create Custom Workflows"

**Description:** Guide for creating custom Agent OS workflows for specialized needs beyond spec_creation_v1 and spec_execution_v1.

**Acceptance Criteria:**
- [ ] File created: `docs/content/how-to-guides/create-custom-workflows.md`
- [ ] Frontmatter: `doc_type: how-to`, `sidebar_position: 1`
- [ ] Structure includes:
  - **Goal:** What user will accomplish (create custom workflow)
  - **Prerequisites:** Familiarity with existing workflows (Tutorial 2)
  - **When to Use This:** Scenarios requiring custom workflows
  - **Step 1-N:** Numbered, concrete steps:
    1. Create metadata.json
    2. Create phases/ directory structure
    3. Write phase.md files (~80 lines each)
    4. Write task files (100-170 lines each)
    5. Validate against workflow-construction-standards.md
    6. Test end-to-end
  - **Validation:** How to verify workflow works
  - **Troubleshooting:** Common issues and fixes
  - **Related:** Links to workflow construction standards
- [ ] Code examples for metadata.json, phase.md, task file
- [ ] Tested by creating a simple workflow following the guide
- [ ] Type badge: 📘 How-To
- [ ] No broken links
- [ ] Divio compliance ≥90%

**Time Estimate:** 2.5-3 hours

**Dependencies:** Phase 2 complete (Tutorial 2 as prerequisite reference)

---

#### Task 3.2: Write How-To - "Integrate Agent OS with CI/CD"

**Description:** Guide for integrating Agent OS workflows and validation into GitHub Actions, GitLab CI, or other CI/CD systems.

**Acceptance Criteria:**
- [ ] File created: `docs/content/how-to-guides/integrate-cicd.md`
- [ ] Frontmatter: `doc_type: how-to`, `sidebar_position: 2`
- [ ] Structure includes goal, prerequisites, when to use, numbered steps, validation, troubleshooting
- [ ] Steps cover:
  - Set up GitHub Actions workflow file
  - Run Divio compliance validation
  - Run link validation
  - Run code example tests
  - Fail build on violations
  - Generate compliance reports as artifacts
- [ ] Code examples for `.github/workflows/docs-validation.yml`
- [ ] Examples for multiple CI systems (GitHub Actions primary, GitLab CI secondary)
- [ ] Tested by implementing in a test repo
- [ ] Type badge: 📘 How-To
- [ ] No broken links
- [ ] Divio compliance ≥90%

**Time Estimate:** 2-2.5 hours

**Dependencies:** Phase 1 complete (validation scripts must exist)

---

#### Task 3.3: Write How-To - "Debug Workflow Failures"

**Description:** Guide for troubleshooting common workflow execution failures (checkpoint failures, tool errors, state corruption).

**Acceptance Criteria:**
- [ ] File created: `docs/content/how-to-guides/debug-workflow-failures.md`
- [ ] Frontmatter: `doc_type: how-to`, `sidebar_position: 3`
- [ ] Structure includes goal, prerequisites, when to use, numbered steps, validation, troubleshooting
- [ ] Steps cover:
  - Check workflow state with `get_workflow_state` tool
  - Identify which phase/task failed
  - Read checkpoint evidence requirements
  - Common failure patterns and fixes:
    - Missing evidence keys
    - Incorrect evidence values
    - Tool invocation errors
    - State file corruption
  - How to resume interrupted workflows
  - When to restart vs resume
- [ ] Code examples showing `get_workflow_state` output
- [ ] Common error messages with solutions
- [ ] Tested by intentionally creating failures and resolving them
- [ ] Type badge: 📘 How-To
- [ ] No broken links
- [ ] Divio compliance ≥90%

**Time Estimate:** 2-2.5 hours

**Dependencies:** Phase 2 complete (Tutorial 2 teaches workflows)

---

#### Task 3.4: Write How-To - "Customize Documentation Theme"

**Description:** Guide for customizing Docusaurus theme, colors, fonts, and layout for Agent OS documentation.

**Acceptance Criteria:**
- [ ] File created: `docs/content/how-to-guides/customize-theme.md`
- [ ] Frontmatter: `doc_type: how-to`, `sidebar_position: 4`
- [ ] Structure includes goal, prerequisites, when to use, numbered steps, validation, troubleshooting
- [ ] Steps cover:
  - Modify `docusaurus.config.ts` theme settings
  - Customize CSS in `src/css/custom.css`
  - Swizzle components safely
  - Add custom React components
  - Brand colors and fonts
  - Logo and favicon
  - Build and preview changes locally
- [ ] Code examples for common customizations
- [ ] Warnings about swizzling (can break on Docusaurus upgrades)
- [ ] Tested by making 3 different theme customizations
- [ ] Type badge: 📘 How-To
- [ ] No broken links
- [ ] Divio compliance ≥90%

**Time Estimate:** 1.5-2 hours

**Dependencies:** Phase 1 complete (directory structure finalized)

---

#### Task 3.5: Write How-To - "Migrate Existing Docs to Divio"

**Description:** Guide for taking existing unstructured documentation and reorganizing it into Divio quadrants.

**Acceptance Criteria:**
- [ ] File created: `docs/content/how-to-guides/migrate-to-divio.md`
- [ ] Frontmatter: `doc_type: how-to`, `sidebar_position: 5`
- [ ] Structure includes goal, prerequisites, when to use, numbered steps, validation, troubleshooting
- [ ] Steps cover:
  - Audit existing documentation
  - Categorize content by Divio type (tutorial/how-to/reference/explanation)
  - Identify content that spans multiple types (split strategy)
  - Add frontmatter `doc_type` fields
  - Refactor content to match type conventions
  - Update internal links
  - Run Divio compliance validation
  - Iterate based on validation feedback
- [ ] Decision tree or flowchart for categorization
- [ ] Before/after examples of content refactored
- [ ] Tested by migrating a sample doc set
- [ ] Type badge: 📘 How-To
- [ ] No broken links
- [ ] Divio compliance ≥90%

**Time Estimate:** 2.5-3 hours

**Dependencies:** Phase 1 complete (validation scripts), Phase 2 complete (understanding of Divio types)

---

### Phase 3 Validation Gate

🛑 **Phase 3 Completion Checkpoint:**

Before advancing to Phase 4:
- [ ] All 5 how-to guides written
- [ ] Each guide tested by following steps
- [ ] Type badges display: 📘 How-To
- [ ] All links verified working
- [ ] Divio compliance ≥90% for all guides
- [ ] Guides address common user problems

**Evidence Required:**
- List of 5 how-to guides with paths
- Divio compliance report for all 5 guides
- Link validation report
- Testing notes for each guide

---

## Phase 4: Reference & Explanation Reorganization

**Objective:** Refactor existing documentation to fit Divio quadrants, enhancing reference docs and splitting `how-it-works.md` into explanation and tutorial content.

**Estimated Duration:** 6-8 hours

### Phase 4 Tasks

#### Task 4.1: Enhance `mcp-tools.md` Reference Documentation

**Description:** Expand `mcp-tools.md` to comprehensively document all MCP tools with full API signatures, parameters, return types, and examples.

**Acceptance Criteria:**
- [ ] File moved/enhanced: `docs/content/reference/mcp-tools.md`
- [ ] Frontmatter: `doc_type: reference`, `sidebar_position: 1`
- [ ] Structure includes:
  - **Overview:** Brief introduction (2-3 sentences)
  - **MCP Tool Reference:** Organized by category
    - **Workflow Tools:** `start_workflow`, `get_current_phase`, `get_task`, `complete_phase`, `get_workflow_state`
    - **RAG Tools:** `search_standards`, `current_date`
    - **Workflow Creation Tools:** `create_workflow`, `validate_workflow`
    - **Browser Tools:** `aos_browser` (with all actions)
  - Each tool documented with:
    - **Function Signature:** Full signature with types
    - **Parameters:** Table with name, type, required/optional, description
    - **Returns:** Return type and structure
    - **Examples:** 2-3 usage examples
    - **Errors:** Common errors and meanings
    - **Related Tools:** Links to related tools
- [ ] Minimal prose (reference style, not tutorial)
- [ ] Structured, scannable format
- [ ] Type badge: 📚 Reference
- [ ] No broken links
- [ ] Divio compliance ≥95%

**Time Estimate:** 2.5-3 hours

**Dependencies:** Phase 1 complete

---

#### Task 4.2: Refactor `how-it-works.md` into Explanation Content

**Description:** Split `how-it-works.md` into explanation content focusing on concepts, architecture, and rationale. Move tutorial-like sections to Tutorial 1.

**Acceptance Criteria:**
- [ ] File refactored: `docs/content/explanation/how-it-works.md`
- [ ] Frontmatter: `doc_type: explanation`, `sidebar_position: 1`
- [ ] Structure includes:
  - **The Human-AI Partnership Model:** Roles, responsibilities, mental model
  - **Spec-Driven Development Philosophy:** Why specs are the main vehicle
  - **Phase-Gated Execution:** Why checkpoints exist, benefits
  - **Tool Chain Architecture:** How MCP tools work under the hood
  - **Quality Enforcement System:** Multi-layer gates (standards, iteration, pre-commit hooks)
  - **Design Principles:** AI-oriented documentation, self-reinforcing patterns
  - **Trade-offs:** When to use workflows vs ad-hoc prompting
  - **Alternatives Considered:** Why not copilot model, why not unstructured prompting
- [ ] Sections removed and moved to Tutorial 1:
  - Step-by-step workflow pattern (this is tutorial content)
  - Concrete "You do X, AI does Y" examples (this is tutorial content)
- [ ] Focus on *why* and *how things work conceptually*, not *how to do things*
- [ ] Background context, concepts, architectural decisions
- [ ] Type badge: 💡 Explanation
- [ ] No broken links
- [ ] Divio compliance ≥90%

**Time Estimate:** 2-2.5 hours

**Dependencies:** Task 2.1 (Tutorial 1 must exist to receive moved content)

---

#### Task 4.3: Enhance `standards.md` and `workflows.md` Reference Documentation

**Description:** Ensure `standards.md` and `workflows.md` are reference-style (structured info, minimal prose) and comprehensive.

**Acceptance Criteria:**
- [ ] `docs/content/reference/standards.md` updated:
  - Frontmatter: `doc_type: reference`
  - Lists all standards categories
  - Brief description of each category
  - Links to standards in `universal/standards/`
  - Table format for easy scanning
  - Minimal prose
- [ ] `docs/content/reference/workflows.md` updated:
  - Frontmatter: `doc_type: reference`
  - Lists all available workflows (spec_creation_v1, spec_execution_v1, etc.)
  - For each workflow:
    - Name, purpose, phases, typical duration
  - Table format
  - Links to workflow directories
  - Minimal prose
- [ ] Type badges: 📚 Reference
- [ ] No broken links
- [ ] Divio compliance ≥90% for both files

**Time Estimate:** 1.5-2 hours

**Dependencies:** Phase 1 complete

---

#### Task 4.4: Create `architecture.md` Explanation Documentation

**Description:** Enhance `architecture.md` to explain Agent OS Enhanced's architecture, design decisions, and trade-offs.

**Acceptance Criteria:**
- [ ] File enhanced: `docs/content/explanation/architecture.md`
- [ ] Frontmatter: `doc_type: explanation`, `sidebar_position: 2`
- [ ] Structure includes:
  - **Overview:** High-level architecture
  - **Component Diagram:** Visual diagram of MCP server, RAG engine, workflows, standards
  - **MCP Architecture:** How Model Context Protocol enables tool discovery
  - **RAG Engine Design:** Chunking strategy, vector search, context reduction
  - **Workflow Engine:** Phase gating, state management, checkpoint validation
  - **Standards System:** Universal vs language-specific, side-loading
  - **Design Decisions:** Why these choices were made
  - **Trade-offs:** Benefits and limitations
  - **Alternatives Considered:** Other approaches and why they weren't chosen
- [ ] Focus on *understanding the system*, not *how to use it*
- [ ] Background, context, rationale
- [ ] Type badge: 💡 Explanation
- [ ] No broken links
- [ ] Divio compliance ≥90%

**Time Estimate:** 2-2.5 hours

**Dependencies:** None (independent explanation)

---

### Phase 4 Validation Gate

🛑 **Phase 4 Completion Checkpoint:**

Before advancing to Phase 5:
- [ ] `mcp-tools.md` enhanced as reference documentation
- [ ] `how-it-works.md` refactored into explanation content
- [ ] `standards.md` and `workflows.md` are reference-style
- [ ] `architecture.md` is explanation-style
- [ ] All files have correct `doc_type` frontmatter
- [ ] Type badges display correctly
- [ ] All links verified working
- [ ] Divio compliance ≥90% for all refactored files

**Evidence Required:**
- Divio compliance report for all 5 files
- Link validation report
- Screenshots showing type badges for each doc type
- Before/after comparison for `how-it-works.md` (show sections moved)

---

## Phase 5: Search Integration

**Objective:** Configure Docusaurus Algolia search for fast, accurate documentation search.

**Estimated Duration:** 2-3 hours

### Phase 5 Tasks

#### Task 5.1: Configure Algolia DocSearch

**Description:** Set up Algolia DocSearch with Docusaurus, configure index settings, and test search functionality.

**Acceptance Criteria:**
- [ ] Algolia account created or existing account configured
- [ ] Algolia application created for Agent OS Enhanced docs
- [ ] API keys obtained (search API key, admin API key)
- [ ] `docusaurus.config.ts` updated with Algolia config:
  ```typescript
  algolia: {
    appId: 'YOUR_APP_ID',
    apiKey: 'YOUR_SEARCH_API_KEY',
    indexName: 'agent-os-enhanced',
    contextualSearch: true,
  }
  ```
- [ ] Algolia crawler configured (or manual scraping script)
- [ ] Index populated with documentation content
- [ ] Search bar appears in navigation
- [ ] Search tested with 10+ queries:
  - "spec creation" → Returns Tutorial 1, spec-related docs
  - "workflow" → Returns Tutorial 2, workflow reference
  - "MCP tools" → Returns mcp-tools.md reference
  - "how it works" → Returns explanation/how-it-works.md
  - etc.
- [ ] Search results return in <500ms (verified with Network tab)
- [ ] Search results ranked correctly (most relevant first)
- [ ] Faceting configured by doc_type (optional but recommended)
- [ ] Documentation added for search configuration (where keys are stored, how to update index)

**Time Estimate:** 2-3 hours

**Dependencies:** Phase 1-4 complete (all content must exist for indexing)

---

### Phase 5 Validation Gate

🛑 **Phase 5 Completion Checkpoint:**

Before advancing to Phase 6:
- [ ] Search bar visible in documentation
- [ ] Search returns results in <500ms
- [ ] Search tested with 10+ queries with correct results
- [ ] Search index covers all documentation
- [ ] Configuration documented

**Evidence Required:**
- Screenshot of search bar and search results
- Performance measurement (query time)
- Test query results (10 queries with screenshots)
- Documentation of Algolia configuration

---

## Phase 6: Validation Automation & Finalization

**Objective:** Implement local pre-commit validation hooks and CI/CD automation to ensure documentation quality. Generate final migration report.

**Estimated Duration:** 2.5-3.5 hours

### Phase 6 Tasks

#### Task 6.1: Create Pre-Commit Validation Hooks

**Description:** Set up local pre-commit hooks to catch documentation quality issues BEFORE they reach CI/CD. Provides immediate feedback to developers.

**Acceptance Criteria:**
- [ ] File created: `scripts/pre-commit/validate-docs.sh` (or integrate into existing pre-commit infrastructure)
- [ ] Pre-commit hook runs on any changes to `docs/**/*.md` files
- [ ] Hook executes:
  1. **Quick Divio Compliance Check:**
     - Run `python scripts/validate-divio-compliance.py` on changed files only
     - Fail commit if compliance <80% (warning threshold)
  2. **Link Validation:**
     - Run `python scripts/validate-links.py --skip-external` on changed files
     - Fail commit if broken internal links found
  3. **Build Check (Optional):**
     - Optional full build check (can be slow)
     - Enabled via environment variable: `DOCS_FULL_BUILD=1`
- [ ] Hook provides clear error messages with actionable fixes
- [ ] Hook completes in <10 seconds for typical changes
- [ ] Documentation added to pre-commit README explaining:
  - What validations run locally
  - How to skip in emergencies (`git commit --no-verify`)
  - When to run full build check
- [ ] Hook integrated into existing pre-commit infrastructure in `scripts/pre-commit/`

**Time Estimate:** 1-1.5 hours

**Dependencies:** Phase 1 complete (validation scripts exist)

**Rationale:** Catch issues locally BEFORE pushing. CI/CD is backstop, not primary validation. Faster feedback loop, less CI churn.

---

#### Task 6.2: Create GitHub Actions CI/CD Validation Pipeline

**Description:** Set up GitHub Actions as backstop validation to catch any issues that bypass pre-commit hooks. Ensures main branch quality and provides reports.

**Acceptance Criteria:**
- [ ] File created: `.github/workflows/docs-validation.yml`
- [ ] Workflow triggers on:
  - Pull requests to main
  - Pushes to main
  - Manual trigger (workflow_dispatch)
- [ ] Workflow jobs:
  1. **Divio Compliance Check:**
     - Run `scripts/validate-divio-compliance.py` (full validation, all files)
     - Fail if overall compliance <90%
     - Upload compliance report as artifact
  2. **Link Validation:**
     - Run `scripts/validate-links.py` (including external URLs)
     - Fail if broken links found
     - Upload link validation report as artifact
  3. **Build Check:**
     - Run `npm run build` in docs/
     - Fail if build errors
     - Upload build artifacts
- [ ] Workflow uses caching for node_modules
- [ ] Workflow completes in <5 minutes
- [ ] Status checks required for PR merge
- [ ] Deploy job (on push to main):
  - Deploy to GitHub Pages after all checks pass
- [ ] Documentation explains workflow and how to interpret failures

**Time Estimate:** 1.5-2 hours

**Dependencies:** Task 6.1 complete (pre-commit hooks exist), Phase 1-5 complete (all content finalized)

**Rationale:** CI/CD is BACKSTOP for pre-commit hooks. Catches issues from developers who skip hooks, validates external links (slow, not suitable for pre-commit), generates reports for auditing.

---

#### Task 6.3: Generate Migration Report

**Description:** Document the documentation restructure results, metrics, and migration summary.

**Acceptance Criteria:**
- [ ] File created: `docs/MIGRATION-REPORT.md` (or in spec directory)
- [ ] Report includes:
  - **Summary:** What was changed, why, and outcome
  - **Metrics:**
    - Before: Divio compliance score (from baseline)
    - After: Divio compliance score (target ≥90%)
    - Before: Broken links count
    - After: Broken links count (0)
    - Before: Tutorial coverage (0%)
    - After: Tutorial coverage (2 tutorials)
    - Before: How-to coverage (X guides)
    - After: How-to coverage (6 guides)
    - Search response time
  - **Changes:**
    - Directory structure reorganization
    - Files moved/created/refactored
    - New components (type badges, validation scripts)
    - CI/CD automation added
  - **Testing Results:**
    - Tutorial user testing (success rate, time taken)
    - Compliance validation results
    - Link validation results
  - **Next Steps:**
    - Ongoing maintenance
    - Future enhancements (if any out-of-scope items become in-scope)
- [ ] Report formatted in markdown
- [ ] Report includes before/after screenshots
- [ ] Report references spec documents for full context

**Time Estimate:** 1-1.5 hours

**Dependencies:** Phase 1-5 complete (all work done, metrics available)

---

### Phase 6 Validation Gate

🛑 **Phase 6 Completion Checkpoint:**

Before marking project complete:
- [ ] Pre-commit validation hooks installed and working
- [ ] GitHub Actions CI/CD pipeline deployed and passing
- [ ] Migration report generated
- [ ] All validation passing:
  - Divio compliance ≥90%
  - 0 broken links
  - Build succeeds
- [ ] Documentation complete and deployed

**Evidence Required:**
- Pre-commit hook execution log showing validation runs
- GitHub Actions workflow run showing all checks passing
- Migration report with before/after metrics
- Live documentation URL with working search and type badges

---

## Project Completion Checklist

🎯 **Final Validation:**

- [ ] All 6 phases complete
- [ ] 2 tutorials created and tested (≥95% success rate)
- [ ] 6 how-to guides created and tested
- [ ] Reference docs enhanced (mcp-tools.md, standards.md, workflows.md)
- [ ] Explanation docs refactored (how-it-works.md, architecture.md)
- [ ] Directory structure reorganized
- [ ] Type badge system implemented
- [ ] Divio compliance validation automated
- [ ] Link validation automated
- [ ] Search integration working (<500ms response)
- [ ] CI/CD pipeline configured
- [ ] MCP RAG index updated
- [ ] Migration report complete
- [ ] All acceptance criteria met
- [ ] No broken links (0)
- [ ] Divio compliance ≥90% overall
- [ ] Documentation builds successfully
- [ ] Ready for production deployment

---

## Risk Mitigation

### Risk 1: Tutorial Success Rate <95%

**Mitigation:**
- Iterate based on user testing feedback
- Simplify steps if users struggle
- Add screenshots for visual guidance
- Test with diverse user backgrounds

### Risk 2: Divio Compliance <90%

**Mitigation:**
- Run validation early and often
- Use validation script feedback to guide refactoring
- Refer to Divio documentation for compliance patterns
- Accept that some docs may be 85-90% (not all docs need 100%)

### Risk 3: Migration Takes Longer Than Estimated

**Mitigation:**
- Prioritize critical content first (tutorials, how-to guides)
- Reference docs can be enhanced incrementally
- Automate repetitive tasks (link updates, frontmatter addition)
- Accept MVP and iterate

### Risk 4: Search Performance <500ms

**Mitigation:**
- Optimize Algolia index settings
- Reduce index size if needed
- Use contextual search and faceting
- Fallback to client-side search if Algolia fails

---

## Notes

- **This is a reorganization and enhancement, not a greenfield creation.** Many docs already exist and need refactoring, not rewriting from scratch.
- **Quality over speed:** Tutorial success rate and Divio compliance are non-negotiable. Take time to test and iterate.
- **User-centric:** Test with real users early and often. Don't assume instructions are clear until users validate them.
- **Automate validation:** CI/CD automation ensures compliance doesn't degrade over time.
