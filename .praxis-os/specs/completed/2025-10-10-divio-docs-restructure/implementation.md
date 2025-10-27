# Implementation Guidance

**Project:** Divio Documentation System Restructure  
**Date:** 2025-10-10  
**Purpose:** Practical guidance for implementing documentation restructure

---

## 1. Content Creation Patterns

This section provides concrete patterns for writing each Divio doc type with examples and anti-patterns.

### 1.1 Tutorial Content Pattern

**Purpose:** Learning-oriented, guaranteed-success, step-by-step guidance for newcomers.

**Structure Template:**
```markdown
---
sidebar_position: N
doc_type: tutorial
---

# Tutorial: {Title}

**Learning Goals:**
- {What user will learn - outcome focused}
- {Second learning goal}

**Time:** {X-Y minutes}
**Prerequisites:** {What must be done first}

## What You'll Build

{Tangible outcome description - be specific}

## Part 1: {Action} ({time estimate})

{Concrete step - what to do}

**Expected Output:**
```
{Exact output user should see}
```

**Success Indicator:** {How to know it worked}

## Part 2-N: {Continue pattern}

...

## What You Learned

- {Key takeaway emphasizing concepts, not just tasks}
- {Second takeaway}
- {Third takeaway}

## Next Steps

- [Next Tutorial] - {Brief description}
- [Related How-To] - {Brief description}
```

**Tutorial Writing Checklist:**
- [ ] Every step is concrete and actionable (no vague instructions like "set up the environment")
- [ ] Every step has expected output (user knows if they succeeded)
- [ ] Steps are numbered and include time estimates
- [ ] No step can fail (if it might fail, add fallback or simplify)
- [ ] Focus is on learning, not just completing a task
- [ ] "What You Learned" emphasizes concepts and principles
- [ ] Success is guaranteed (tested with 3+ real users achieving ≥95% success rate)
- [ ] Takes target time (measured with real users)

**Good Example (Tutorial):**
```markdown
## Part 2: Create Specification (5 minutes)

Tell your AI assistant:
```
"Create a spec for user profile API"
```

The AI will automatically invoke the `spec_creation_v1` workflow. You'll see it:
1. Execute Phase 0 (gathering context)
2. Execute Phase 1 (requirements)
3. Continue through all phases

**Expected Output:**
```
Phase 0 complete ✓
Phase 1 complete ✓
Phase 2 complete ✓
...
Specification created: .praxis-os/specs/2025-10-10-user-profile/
```

**Success Indicator:** You see "Specification created" message with a path to the spec directory.

**What's happening:** The AI is systematically creating requirements, design, tasks, and implementation guidance documents. This is Agent OS's main vehicle for development.
```

**Anti-Pattern (Tutorial):**
```markdown
## Step 2: Set up your environment

Configure your development environment according to your needs.

**What not to do:** This is vague. What does "configure" mean? What are "your needs"? Users will fail.
```

---

### 1.2 How-To Guide Content Pattern

**Purpose:** Problem-solving, goal-oriented guidance for users who know what they want to accomplish.

**Structure Template:**
```markdown
---
sidebar_position: N
doc_type: how-to
---

# How to {Task}

**Goal:** {What user will accomplish}

**Prerequisites:**
- {Requirement 1}
- {Requirement 2}

**When to Use This:** {Scenarios where this guide applies}

## Step 1: {Action}

{Concrete instruction}

```bash
# Example command
command --with-flags
```

{Explanation of what this does}

## Step 2-N: {Continue pattern}

...

## Validation

How to verify it worked:

```bash
# Verification command
verify-command
```

Expected output:
```
{Expected result}
```

## Troubleshooting

### Issue: {Common problem}

**Symptoms:** {How you know you have this problem}

**Cause:** {Why this happens}

**Solution:**
```bash
# Fix command
fix-command
```

## Related

- [Related How-To] - {When to use instead}
- [Reference] - {More details}
```

**How-To Writing Checklist:**
- [ ] Goal is stated clearly and concretely at the top
- [ ] Prerequisites are listed (user knows if they qualify)
- [ ] Steps are numbered and actionable
- [ ] Code examples are complete and tested (not pseudocode)
- [ ] Validation section shows how to verify success
- [ ] Troubleshooting covers 2-3 common issues
- [ ] Minimal explanation (focus on doing, not understanding)
- [ ] Successfully tested by following the guide yourself

**Good Example (How-To):**
```markdown
## Step 2: Configure Docusaurus

Edit `docusaurus.config.ts`:

```typescript
export default {
  // ... existing config
  algolia: {
    appId: 'YOUR_APP_ID',
    apiKey: 'YOUR_SEARCH_API_KEY',
    indexName: 'agent-os-enhanced',
    contextualSearch: true,
  },
};
```

Replace `YOUR_APP_ID` and `YOUR_SEARCH_API_KEY` with your Algolia credentials from Step 1.

Save the file.
```

**Anti-Pattern (How-To):**
```markdown
## Step 2: Configure the search feature

Set up search according to the documentation.

**What not to do:** No concrete instructions. User doesn't know what to edit or where.
```

---

### 1.3 Reference Content Pattern

**Purpose:** Structured information for lookup, minimal prose, high scanability.

**Structure Template:**
```markdown
---
sidebar_position: N
doc_type: reference
---

# {Topic} Reference

**Overview:** {1-2 sentence summary}

---

## {Category 1}

### `function_name(param1, param2)`

**Description:** {Brief description}

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `param1` | string | Yes | {Description} |
| `param2` | number | No | {Description} (default: {value}) |

**Returns:** `{ReturnType}` - {Description}

**Example:**
```language
function_name("value", 42)
// Returns: {expected output}
```

**Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `ErrorName` | {When this happens} | {How to fix} |

**Related:** [other_function](#other_function), [Concept](../explanation/concept.md)

---

## {Category 2}

{Continue pattern}
```

**Reference Writing Checklist:**
- [ ] Minimal prose (no tutorials or explanations embedded)
- [ ] Information is structured (tables, lists, code blocks)
- [ ] Easily scannable (user can find info quickly)
- [ ] Complete (covers all items in category)
- [ ] Consistent format (every item uses same template)
- [ ] Examples are minimal but functional
- [ ] Cross-references to related items

**Good Example (Reference):**
```markdown
### `start_workflow(workflow_type, target_file)`

**Description:** Initiates a phase-gated workflow session.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_type` | string | Yes | Workflow identifier (e.g., "spec_creation_v1", "spec_execution_v1") |
| `target_file` | string | Yes | File or feature name being worked on |

**Returns:** `Dict[str, Any]` - Session information with session_id and Phase 1 content.

**Example:**
```python
start_workflow(
    workflow_type="spec_creation_v1",
    target_file="user_authentication"
)
# Returns: {"session_id": "abc-123", "current_phase": 1, ...}
```

**Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `WorkflowNotFound` | Invalid workflow_type | Use valid workflow: spec_creation_v1, spec_execution_v1 |
| `StateConflict` | Active workflow exists | Complete or abandon existing workflow |

**Related:** [complete_phase](#complete_phase), [get_workflow_state](#get_workflow_state)
```

**Anti-Pattern (Reference):**
```markdown
### start_workflow

This function starts a workflow. It's really useful when you want to begin working on a feature. You should call it at the start of your project after you've discussed the design...

**What not to do:** Too much prose. Reference docs should be minimal and structured, not tutorial-like.
```

---

### 1.4 Explanation Content Pattern

**Purpose:** Understanding-oriented, background, concepts, trade-offs, "why" and "how it works".

**Structure Template:**
```markdown
---
sidebar_position: N
doc_type: explanation
---

# {Topic} Explained

**Overview:** {What this explains}

---

## Background

{Historical context, problem being solved, motivation}

## Concepts

### {Concept 1}

{Explanation of concept with examples}

{Why it matters}

### {Concept 2}

{Continue pattern}

## How It Works

{Step-by-step explanation of internal mechanics}

{Diagrams if helpful}

## Design Decisions

### Decision: {Decision made}

**Rationale:** {Why this choice}

**Benefits:**
- {Benefit 1}
- {Benefit 2}

**Trade-offs:**
- {Limitation 1}
- {Limitation 2}

### {More decisions...}

## Alternatives Considered

### Alternative: {Other approach}

**Why not chosen:**
- {Reason 1}
- {Reason 2}

## When to Use

{Guidance on applicability}

{When this approach is appropriate vs inappropriate}

## Related

- [Tutorial] - {Learn by doing}
- [How-To] - {Solve specific problem}
- [Reference] - {Look up details}
```

**Explanation Writing Checklist:**
- [ ] Focus on understanding, not doing
- [ ] Explains "why" and "how it works conceptually"
- [ ] Provides background and context
- [ ] Discusses trade-offs and alternatives
- [ ] Uses examples to illustrate concepts (not tasks to complete)
- [ ] Links to tutorials/how-tos for practical application
- [ ] Longer and more prose-heavy than other types (this is OK)

**Good Example (Explanation):**
```markdown
## Why Spec-Driven Development?

Agent OS uses specifications as the primary vehicle for development because of how LLMs process information. When you ask an AI to "build user authentication," the request is ambiguous. Does it include social auth? What's the session duration? Which database?

Without a spec, the AI must make assumptions. Different assumptions lead to different implementations. The result is non-deterministic - sometimes you get what you want, sometimes you don't.

Specs solve this by forcing requirement clarification *before* implementation. The `spec_creation_v1` workflow systematically asks questions, documents decisions, and creates a complete design. When implementation begins via `spec_execution_v1`, there's no ambiguity. The AI has a detailed blueprint.

**Benefits:**
- Deterministic outcomes (same spec → same implementation)
- Team alignment (spec reviewed before coding)
- AI operates with full context (no guessing)

**Trade-offs:**
- Upfront time investment (30-60 min to create spec)
- Not suitable for 5-minute tasks (overhead too high)

This is why spec creation → spec execution is THE MAIN VEHICLE for Agent OS.
```

**Anti-Pattern (Explanation):**
```markdown
## Spec-Driven Development

To use specs, run `start_workflow("spec_creation_v1", "feature")`. Then answer the questions. Finally, run `start_workflow("spec_execution_v1", "feature")`.

**What not to do:** This is how-to content, not explanation. Explanation should focus on concepts, not procedures.
```

---

## 2. Testing Strategy

Documentation testing is different from code testing. This section outlines how to validate documentation quality.

### 2.1 Tutorial User Testing

**Purpose:** Ensure tutorials have ≥95% success rate and take target time.

**Process:**

**Step 1: Recruit Test Users**
- Target: 3-5 users per tutorial
- Profile: Users matching tutorial's target audience (e.g., new Agent OS users for Tutorial 1)
- Diversity: Mix of OS (macOS, Linux, Windows), experience levels

**Step 2: Conduct Tests**
- Provide: Fresh Agent OS installation, tutorial document
- Observe: User follows tutorial without intervention
- Measure:
  - Success: Did user complete successfully? (Yes/No)
  - Time: How long did it take? (minutes)
  - Blockers: Where did user get stuck? (notes)

**Step 3: Calculate Metrics**
```python
success_rate = (successful_completions / total_users) * 100
avg_time = sum(completion_times) / len(completion_times)
```

**Step 4: Iterate**
- If success_rate < 95%: Identify common failure points, simplify steps, add clarification
- If avg_time > target_time: Simplify example, remove non-essential steps, add time guidance
- Retest with new users

**Documentation Template:**
```markdown
# Tutorial Testing Results: {Tutorial Name}

**Date:** {YYYY-MM-DD}
**Version:** {Tutorial version/commit}

## Test Users

| User | OS | Experience | Success | Time | Notes |
|------|-----|------------|---------|------|-------|
| User 1 | macOS | Beginner | ✅ Yes | 18 min | None |
| User 2 | Linux | Intermediate | ✅ Yes | 16 min | Stuck on Part 3 (2 min) |
| User 3 | Windows | Beginner | ❌ No | 25 min | Part 4 failed (spec_execution didn't run) |

## Results

- **Success Rate:** 66.7% (2/3) ❌ Below target (95%)
- **Avg Time:** 19.7 min ⚠️ Slightly over target (15-20 min)

## Issues Identified

1. **Part 4 failure (User 3):** Windows path issue with `.praxis-os` directory
2. **Part 3 confusion (User 2):** "Review spec" too vague

## Actions

1. Add Windows-specific note for Part 4 (path formatting)
2. Expand Part 3 with specific files to review and what to look for
3. Retest with 2 new Windows users

## Iteration 2 (After fixes)

{Results from second round}
```

---

### 2.2 Divio Compliance Validation

**Purpose:** Ensure documentation meets Divio standards (≥90% compliance).

**Process:**

**Step 1: Run Validation Script**
```bash
python scripts/validate-divio-compliance.py --report
```

**Step 2: Review Report**
```
Divio Compliance Report
=======================
Overall Compliance: 87% ⚠️ (Target: 90%)

By Doc Type:
- Tutorials: 95% ✅ (2 files)
- How-To: 88% ⚠️ (6 files)
- Reference: 92% ✅ (3 files)
- Explanation: 85% ⚠️ (2 files)

Issues:
- docs/content/how-to-guides/create-custom-workflows.md (line 45): Missing "Validation" section
- docs/content/explanation/how-it-works.md (line 120): Tutorial-like content detected (should be concept-focused)

Recommendations:
- Add "Validation" section to all how-to guides
- Refactor explanation docs to remove step-by-step instructions
```

**Step 3: Fix Issues**
Address each issue reported. Re-run validation to verify fixes.

**Step 4: Accept Trade-offs**
Not all docs need 100% compliance. Some docs may be hybrids or fall outside strict categories. Target 90% overall, accept some docs at 85%.

**Validation Frequency:**
- Before committing: Run on changed files
- Pre-merge: Run on all files in PR
- Post-deploy: Run on full docs site (CI/CD)

---

### 2.3 Link Validation

**Purpose:** Ensure 0 broken links (internal, anchors, external).

**Process:**

**Step 1: Run Link Validator**
```bash
python scripts/validate-links.py --report
```

**Step 2: Review Report**
```
Link Validation Report
======================
Total Links: 487
Broken Links: 3 ❌

Broken Links:
1. docs/content/tutorials/your-first-project.md (line 67)
   Link: [Tutorial 2](../tutorials/understanding-workflows.md)
   Error: File not found
   Fix: Correct path to 'understanding-agent-os-workflows.md'

2. docs/content/reference/mcp-tools.md (line 134)
   Link: [Workflow Standards](#workflow-standards)
   Error: Anchor not found
   Fix: Section is "#workflow-system-overview"

3. docs/content/how-to-guides/integrate-cicd.md (line 89)
   Link: https://example.com/old-docs
   Error: HTTP 404
   Fix: Update to current URL or remove
```

**Step 3: Fix Broken Links**
Address each broken link. Re-run validation to verify fixes.

**Step 4: Automate**
Add link validation to CI/CD (see Section 3.2).

**Validation Frequency:**
- Before committing: Run with --skip-external (fast)
- Pre-merge: Run full validation including external URLs
- Weekly: Run on live site to catch external link rot

---

### 2.4 Build Validation

**Purpose:** Ensure documentation builds successfully with no errors or warnings.

**Process:**

**Step 1: Build Locally**
```bash
cd docs/
npm run build
```

**Step 2: Check Output**
```
[SUCCESS] Generated static files in "build".
[INFO] Use `npm run serve` to test your build locally.
```

**Step 3: Serve and Test**
```bash
npm run serve
```

Open `http://localhost:3000` and spot-check:
- All pages load
- Type badges display
- Search works
- Navigation functions
- Internal links work
- Images display

**Common Build Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `Duplicate routes` | Two files with same slug | Rename one file or set explicit `slug` in frontmatter |
| `Broken link` | Link to non-existent page | Fix or remove link |
| `Invalid frontmatter` | YAML syntax error | Validate YAML, check indentation |
| `MDX parsing error` | Invalid JSX in markdown | Escape braces `\{` or use code blocks |

---

## 3. Deployment Guidance

### 3.1 Local Development Workflow

**Step 1: Make Changes**
Edit documentation files in `docs/content/`.

**Step 2: Preview Locally**
```bash
cd docs/
npm start
```

Opens `http://localhost:3000` with hot reload.

**Step 3: Test Changes**
- Verify content displays correctly
- Check links work
- Verify type badges show
- Test search (if already configured)

**Step 4: Validate Before Commit**
```bash
# Quick validation (skip external links)
python scripts/validate-links.py --skip-external
python scripts/validate-divio-compliance.py

# Build check
cd docs/
npm run build
```

**Step 5: Commit**
```bash
git add docs/
git commit -m "docs: add tutorial for custom workflows"
```

---

### 3.2 CI/CD Pipeline (GitHub Actions)

**File:** `.github/workflows/docs-validation.yml`

**Triggers:**
- Pull requests to main
- Pushes to main
- Manual dispatch

**Jobs:**

**1. Divio Compliance Check**
```yaml
divio-compliance:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install pyyaml markdown
    - name: Run Divio compliance validation
      run: python scripts/validate-divio-compliance.py --strict
    - name: Upload report
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: divio-compliance-report
        path: divio-compliance-report.md
```

**2. Link Validation**
```yaml
link-validation:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install requests
    - name: Run link validation
      run: python scripts/validate-links.py --report
    - name: Upload report
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: link-validation-report
        path: link-validation-report.md
```

**3. Build Check**
```yaml
build:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: docs/package-lock.json
    - name: Install dependencies
      run: cd docs && npm ci
    - name: Build documentation
      run: cd docs && npm run build
    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: docs-build
        path: docs/build
```

**4. Deploy (on push to main)**
```yaml
deploy:
  runs-on: ubuntu-latest
  needs: [divio-compliance, link-validation, build]
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  steps:
    - uses: actions/checkout@v3
    - name: Download build artifacts
      uses: actions/download-artifact@v3
      with:
        name: docs-build
        path: docs/build
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs/build
```

**Required Settings:**
- GitHub Pages enabled (Settings → Pages → Source: gh-pages branch)
- Status checks required for PR merge:
  - `divio-compliance`
  - `link-validation`
  - `build`

---

### 3.3 Algolia Search Index Update

**Purpose:** Keep Algolia search index in sync with documentation changes.

**Process:**

**Step 1: Configure Algolia Crawler**

Algolia can crawl your deployed site automatically. Configure the crawler:

```json
{
  "index_name": "agent-os-enhanced",
  "start_urls": [
    "https://yourdomain.github.io/agent-os-enhanced/"
  ],
  "sitemap_urls": [
    "https://yourdomain.github.io/agent-os-enhanced/sitemap.xml"
  ],
  "selectors": {
    "lvl0": ".docusaurus-content h1",
    "lvl1": ".docusaurus-content h2",
    "lvl2": ".docusaurus-content h3",
    "text": ".docusaurus-content p, .docusaurus-content li"
  },
  "schedule": "every 1 day at 3:00 am UTC"
}
```

**Step 2: Manual Reindex (if needed)**

If you need to trigger reindex immediately:

```bash
# Using Algolia CLI (requires installation and API key)
algolia reindex --index agent-os-enhanced
```

**Step 3: Verify Search Works**

After deployment and reindex:
1. Navigate to deployed docs site
2. Use search bar
3. Test 5+ queries
4. Verify results are current (reflect recent changes)

---

## 4. Troubleshooting

### 4.1 Tutorial Success Rate <95%

**Symptoms:**
- Users fail to complete tutorial
- Users get stuck at specific steps
- Users report confusion or frustration

**Common Causes:**

**Cause 1: Vague Instructions**
- Step says "set up environment" without specifics
- User doesn't know exactly what to do

**Solution:**
Make every step concrete:
- ❌ "Set up environment"
- ✅ "Open terminal and run: `export AGENT_OS_PATH=~/.praxis-os`"

**Cause 2: Step Can Fail**
- Command might fail depending on environment
- User doesn't have prerequisite installed

**Solution:**
Add fallback or simplify:
- Check prerequisites explicitly before tutorial starts
- Provide fallback commands for common failures
- Test on multiple OSes

**Cause 3: Missing Expected Output**
- User doesn't know if step succeeded
- Continues with broken state

**Solution:**
Add expected output to every step:
```markdown
Run:
```bash
agent-os --version
```

Expected output:
```
Agent OS Enhanced v2.1.0
```

If you see this, continue to next step.
```

**Cause 4: Tutorial Too Complex**
- Feature being built is too ambitious
- Takes longer than expected

**Solution:**
Simplify the example:
- Use simpler feature (e.g., "hello world API" instead of "user authentication")
- Remove optional steps
- Split into multiple tutorials

---

### 4.2 Divio Compliance <90%

**Symptoms:**
- `validate-divio-compliance.py` reports <90% compliance
- Docs feel disorganized or unclear

**Common Causes:**

**Cause 1: Wrong Doc Type**
- Content doesn't match assigned `doc_type`
- Tutorial has too much explanation
- How-to is too learning-oriented

**Solution:**
Refactor to match type:
- If tutorial has heavy background → Move to explanation doc, link from tutorial
- If how-to is teaching concepts → Split into explanation + how-to
- If reference has prose → Condense to structured info

**Cause 2: Missing Required Sections**
- Tutorials missing "What You Learned"
- How-tos missing "Validation" or "Troubleshooting"

**Solution:**
Add missing sections using templates in Section 1.

**Cause 3: Content Spans Multiple Types**
- Document tries to be tutorial + reference + explanation

**Solution:**
Split into multiple docs:
```markdown
# Before (one doc trying to do everything)
## What is X? (explanation)
## How to use X (tutorial)
## X API Reference (reference)

# After (split into 3 docs)
## explanation/what-is-x.md (background, concepts)
## tutorials/using-x.md (hands-on learning)
## reference/x-api.md (structured API info)
```

---

### 4.3 Broken Links

**Symptoms:**
- `validate-links.py` reports broken links
- Users report 404 errors

**Common Causes:**

**Cause 1: Incorrect Relative Path**
- Link uses wrong relative path after file moved

**Solution:**
Fix path:
```markdown
# From: docs/content/tutorials/first-project.md
# To: docs/content/reference/mcp-tools.md

# Wrong:
[MCP Tools](mcp-tools.md)  # Wrong directory

# Correct:
[MCP Tools](../reference/mcp-tools.md)
```

**Cause 2: Anchor Doesn't Exist**
- Link to section header that was renamed or removed

**Solution:**
Update anchor or remove link:
```markdown
# Link:
[Phase Gating](../explanation/how-it-works.md#phase-gating)

# But section header is actually "Phase-Gated Execution"

# Fix:
[Phase Gating](../explanation/how-it-works.md#phase-gated-execution)
```

**Cause 3: External URL Dead**
- External site changed URL or removed content

**Solution:**
- Update to current URL if site moved
- Use Internet Archive link if content removed but archived
- Remove link if no longer relevant

---

### 4.4 Docusaurus Build Errors

**Symptoms:**
- `npm run build` fails
- Build works locally but fails in CI

**Common Causes:**

**Cause 1: Duplicate Routes**
```
Error: Duplicate routes found:
- /docs/tutorial
  - docs/content/tutorial.md
  - docs/content/tutorial/index.md
```

**Solution:**
Rename one file or set explicit slug:
```yaml
---
slug: /tutorial-overview
---
```

**Cause 2: Invalid Frontmatter**
```
Error: Error parsing frontmatter in docs/content/tutorial.md
```

**Solution:**
Validate YAML syntax:
```yaml
# Wrong (missing quotes around colon)
sidebar_label: How To: Create Workflows

# Correct:
sidebar_label: "How To: Create Workflows"
```

**Cause 3: MDX Parsing Error**
```
Error: Unexpected token `{` in MDX
```

**Solution:**
Escape braces or use code blocks:
```markdown
# Wrong (braces in prose):
Use {variable} to access the value.

# Correct:
Use `{variable}` to access the value.
```

**Cause 4: Node Version Mismatch**
- CI uses different Node version than local

**Solution:**
Pin Node version:
```yaml
# .nvmrc
18.17.0
```

```yaml
# .github/workflows/docs-validation.yml
- uses: actions/setup-node@v3
  with:
    node-version-file: '.nvmrc'
```

---

### 4.5 Type Badges Not Showing

**Symptoms:**
- Type badges don't appear on doc pages
- Badges show for some docs but not others

**Common Causes:**

**Cause 1: Missing `doc_type` Frontmatter**
- Document doesn't have `doc_type: tutorial` etc.

**Solution:**
Add frontmatter:
```yaml
---
sidebar_position: 1
doc_type: tutorial
---
```

**Cause 2: Component Not Integrated**
- `DocTypeBadge` component not imported in Docusaurus theme

**Solution:**
Check integration in `docusaurus.config.ts` or theme swizzle.

**Cause 3: CSS Not Loaded**
- Badge component CSS not imported

**Solution:**
Import CSS in component or add to `custom.css`.

---

### 4.6 Search Not Working

**Symptoms:**
- Search bar doesn't appear
- Search returns no results
- Search is slow (>5 seconds)

**Common Causes:**

**Cause 1: Algolia Not Configured**
- Missing config in `docusaurus.config.ts`

**Solution:**
Add Algolia config (see Section 3.4).

**Cause 2: Index Not Populated**
- Algolia account created but no content indexed

**Solution:**
Run Algolia crawler or manual indexing (see Section 3.4).

**Cause 3: Wrong Index Name**
- Config references non-existent index

**Solution:**
Verify index name matches Algolia dashboard:
```typescript
algolia: {
  indexName: 'agent-os-enhanced',  // Must match Algolia index
}
```

---

## 5. Best Practices Summary

### 5.1 Content Creation
- **Use templates** from Section 1 for consistency
- **Test with real users** before considering tutorials complete
- **Validate early and often** using compliance and link validators
- **Keep it simple** - tutorials should guarantee success
- **Be concrete** - avoid vague instructions

### 5.2 Maintenance
- **Run validation before every commit**
- **Build locally before pushing**
- **Update links when moving files**
- **Reindex RAG and Algolia after content changes**
- **Monitor CI/CD for failures**

### 5.3 Quality Gates
- **Tutorial success rate ≥95%** (verified with users)
- **Divio compliance ≥90%** (measured with validator)
- **Zero broken links** (verified with validator)
- **Build succeeds** (verified with npm run build)
- **Search works** (verified with test queries)

### 5.4 Iteration Cycle
1. Write content using templates
2. Validate locally (compliance, links, build)
3. Test with users (if tutorial)
4. Iterate based on feedback
5. Commit when all gates pass
6. Deploy via CI/CD
7. Update indices (RAG, Algolia)

---

## 6. Reference

### 6.1 Key Files

| File | Purpose |
|------|---------|
| `docs/content/` | All documentation content |
| `docs/docusaurus.config.ts` | Docusaurus configuration |
| `docs/sidebars.ts` | Sidebar structure |
| `docs/src/components/DocTypeBadge.tsx` | Type badge component |
| `scripts/validate-divio-compliance.py` | Compliance validator |
| `scripts/validate-links.py` | Link validator |
| `scripts/build_rag_index.py` | RAG index builder |
| `.github/workflows/docs-validation.yml` | CI/CD pipeline |

### 6.2 Commands

| Command | Purpose |
|---------|---------|
| `cd docs && npm start` | Start local dev server |
| `cd docs && npm run build` | Build production site |
| `cd docs && npm run serve` | Serve production build locally |
| `python scripts/validate-divio-compliance.py` | Check Divio compliance |
| `python scripts/validate-links.py` | Check for broken links |
| `python scripts/build_rag_index.py` | Rebuild MCP RAG index |

### 6.3 Useful Resources

- **Divio Documentation System:** https://documentation.divio.com/
- **Docusaurus Docs:** https://docusaurus.io/docs
- **Algolia DocSearch:** https://docsearch.algolia.com/
- **Agent OS Workflow Standards:** `universal/workflows/workflow-construction-standards.md`
- **Agent OS Operating Model:** `universal/usage/operating-model.md`

---

**Document Status:** Complete - Ready for Phase 5 (Finalization)
