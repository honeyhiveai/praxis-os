# Architectural Decision: Workflow Creation Systems Location

**Date:** October 9, 2025  
**Status:** Proposed  
**Decision:** Where workflow creation systems should live and how they're accessed

---

## Context

Workflow creation systems (test-generation, production-code-generation) are **meta-level tools** that generate workflows. They contain:
- Design documentation
- Universal standard templates
- Language instruction templates
- Generator scripts

**Question:** Should these be:
1. In source repo only (users reference from GitHub)?
2. Installed locally in `.praxis-os/standards/meta-workflow/`?
3. Installed locally but NOT indexed by MCP?

---

## Key Insight: Build-Time vs Runtime

These are **BUILD-TIME dependencies**, not **RUNTIME dependencies**.

```yaml
Analogy:
  Build_Tools: "webpack.config.js, tsconfig.json, generator scripts"
  vs
  Application_Code: "The actual app that runs"

Workflow_Creation_Systems: "Templates and generators for workflows"
  vs
Actual_Workflows: "The workflows users execute"
```

### Usage Pattern

```
Phase 1: Workflow Creation (ONE-TIME or occasional)
├── User reads design docs
├── User runs generator script
├── Generates: workflow in .praxis-os/workflows/
└── User doesn't need creation system anymore

Phase 2: Workflow Usage (ONGOING)
├── User starts workflow
├── User executes phases
├── User completes workflow
└── User repeats with different files
```

**Frequency:**
- Creation: Once per language/project (rare)
- Usage: Daily/weekly with generated workflows (common)

---

## Problem with Local Installation + Indexing

If installed in `.praxis-os/standards/meta-workflow/workflow-types/` and indexed:

### Search Pollution

```python
# User query
search_standards("How do I generate tests for this Python function?")

# Returns (BAD):
1. meta-workflow/workflow-types/test-generation/design/framework-design.md
   "Complete design for creating test generation workflows..."
   
2. meta-workflow/workflow-types/test-generation/templates/phase-1-template.md
   "Template for Phase 1 analysis..."
   
3. .praxis-os/workflows/test_generation_python_v1/phases/1/task-1.md
   "Execute AST analysis on target file..."  ← USER WANTS THIS

# User gets confused:
# - Do I use the template or the workflow?
# - Why are there two sets of instructions?
# - Which one applies to me?
```

### Cognitive Overload

- Users see BOTH creation instructions AND usage instructions
- Creation system docs are detailed (2000+ lines total)
- 90%+ of search results would be irrelevant for daily workflow usage
- "How do I analyze dependencies?" returns template instructions, not actual workflow task

### Version Confusion

```
Scenario: User generates workflow from v1.0 templates
Then: Templates update to v1.1 (in source)
But: User's local copy still has v1.0 templates
Query: "Test generation methodology" returns v1.0 (local) not v1.1 (source)
```

---

## Options Analysis

### Option 1: Source Repo Only (Recommended)

**Location:** `meta-workflow/workflow-types/` in source repo  
**Access:** Users read from GitHub when needed  
**Local:** Not installed in user projects

```yaml
Pros:
  - ✅ No search pollution
  - ✅ Always up-to-date (users reference latest)
  - ✅ Clear separation (creation vs usage)
  - ✅ Smaller local installation
  - ✅ No version confusion

Cons:
  - ❌ Requires internet for initial setup
  - ❌ Not available offline (but only needed once)
  - ❌ Can't use search_standards to explore creation system
```

**User Experience:**

```bash
# One-time: Generate workflow
cd ~/praxis-os/  # Clone source repo
cd meta-workflow/workflow-types/test-generation/
python scripts/generate-test-workflow.py --language python --project ~/my-project/

# Result: Generates workflow in ~/my-project/.praxis-os/workflows/

# Ongoing: Use generated workflow
cd ~/my-project/
# Via MCP
start_workflow("test_generation_python_v1", "src/module.py")
# Agent reads from .praxis-os/workflows/ (local, generated)
```

**Installation Flow:**

```bash
# prAxIs OS installation script
pip install agent-os  # Does NOT include workflow-types/

# User wants test generation
git clone https://github.com/honeyhiveai/praxis-os.git ~/agent-os-source
# OR visit GitHub directly

# Generate workflow
python ~/agent-os-source/meta-workflow/workflow-types/test-generation/scripts/generate-test-workflow.py \
    --language python \
    --project ~/my-project/

# Done - user now has workflow, doesn't need source repo anymore
```

---

### Option 2: Local Installation + Indexed (Not Recommended)

**Location:** `.praxis-os/standards/meta-workflow/workflow-types/`  
**Access:** Via search_standards  
**Indexed:** Yes

```yaml
Pros:
  - ✅ Available offline
  - ✅ Can explore via search_standards

Cons:
  - ❌ Search pollution (major issue)
  - ❌ Cognitive overload for users
  - ❌ Version confusion (local vs source)
  - ❌ Larger installation size
  - ❌ Users see creation system when they want usage
  - ❌ Duplicate/confusing results
```

**Search Pollution Example:**

```python
search_standards("test generation Phase 1")

# Returns 10+ results:
# - Template for Phase 1 (creation system)
# - Python Phase 1 task (generated workflow)
# - JavaScript Phase 1 task (generated workflow)
# - Universal Phase 1 standard template
# - Phase 1 design doc
# - Phase 1 implementation guide section
# ...

# User: "Which one do I use?!?" 😵
```

---

### Option 3: Local But Not Indexed (Middle Ground)

**Location:** `.praxis-os/workflow-creation-systems/` (NOT under standards/)  
**Access:** Direct file access only  
**Indexed:** No (excluded from MCP search)

```yaml
Pros:
  - ✅ Available offline
  - ✅ No search pollution
  - ✅ Clear separation

Cons:
  - ❌ Extra complexity (another directory)
  - ❌ Larger installation
  - ❌ Can't explore via search_standards
  - ❌ Version management still needed
```

**Implementation:**

```python
# mcp_server/rag_engine.py
def _should_index_file(self, file_path: str) -> bool:
    """Determine if file should be indexed."""
    exclude_dirs = [
        '.praxis-os/workflow-creation-systems',  # Not indexed
        '.praxis-os/venv',
        'node_modules',
        '__pycache__'
    ]
    # ...
```

---

## Recommended Approach: Option 1 (Source Only)

### Architecture

```
Source Repository (github.com/honeyhiveai/praxis-os):
├── meta-workflow/workflow-types/      ← Workflow creation systems
│   ├── test-generation/
│   └── production-code-generation/
└── [other prAxIs OS source]

User Project (~/my-project/):
├── .praxis-os/
│   ├── workflows/                      ← Generated workflows (indexed)
│   │   └── test_generation_python_v1/
│   └── standards/                      ← Project standards (indexed)
└── src/

MCP search_standards scope:
  - ~/my-project/.praxis-os/workflows/   ✅ Indexed
  - ~/my-project/.praxis-os/standards/   ✅ Indexed
  - Workflow creation systems           ❌ Not indexed (in source only)
```

### User Journey

#### First-Time Setup

```bash
# 1. Install Agent OS
pip install agent-os

# 2. Initialize project
cd ~/my-project/
agent-os init

# 3. Generate test workflow (one-time)
# Option A: Use published generator
pip install agent-os-workflow-generators
agent-os generate-workflow test-generation --language python

# Option B: Clone source and run directly
git clone https://github.com/honeyhiveai/praxis-os.git ~/agent-os-source
python ~/agent-os-source/meta-workflow/workflow-types/test-generation/scripts/generate-test-workflow.py \
    --language python \
    --project ~/my-project/

# 4. Result: Workflow created in .praxis-os/workflows/
# User now has test_generation_python_v1/ workflow locally
```

#### Ongoing Usage

```python
# User works with GENERATED workflow (in project)
# Never needs to reference creation system again

# Via MCP
start_workflow("test_generation_python_v1", "src/module.py")

# Via CLI
agent-os workflow start test_generation_python_v1 src/module.py

# Agent reads from:
# .praxis-os/workflows/test_generation_python_v1/phases/...
# (Local, generated, indexed)
```

#### Updates

```bash
# Workflow creation system updated (v1.1)
# User wants to regenerate with latest

# Pull latest source
cd ~/agent-os-source/
git pull

# Regenerate workflow
python meta-workflow/workflow-types/test-generation/scripts/generate-test-workflow.py \
    --language python \
    --project ~/my-project/ \
    --force  # Overwrites existing

# Or use published tool
pip install --upgrade agent-os-workflow-generators
agent-os generate-workflow test-generation --language python --force
```

---

## Implementation Details

### Distribution Options

#### Option A: Separate Package (Recommended)

```bash
# Core Agent OS
pip install agent-os

# Workflow generators (separate package)
pip install agent-os-workflow-generators

# Usage
agent-os generate-workflow test-generation --language python
```

**Pros:**
- ✅ Clean separation
- ✅ Users only install if needed
- ✅ Easy to version independently
- ✅ Clear dependency model

#### Option B: In Core, CLI Command

```bash
pip install agent-os

# Workflow generators included
agent-os generate-workflow test-generation --language python
```

**Pros:**
- ✅ Simpler for users (one install)
- ✅ Integrated experience

**Cons:**
- ❌ Larger core package
- ❌ Everyone gets generators (even if not needed)

#### Option C: Source Reference Only

```bash
# No pip install for generators
# Users clone source repo when needed

git clone https://github.com/honeyhiveai/praxis-os.git
cd meta-workflow/workflow-types/test-generation/
python scripts/generate-test-workflow.py --language python --project ~/my-project/
```

**Pros:**
- ✅ Always latest version
- ✅ Simple distribution model
- ✅ No packaging complexity

**Cons:**
- ❌ More steps for users
- ❌ Requires git clone

---

## Recommendation: Hybrid Approach

### Phase 1: Source Reference (Initial Release)

```
meta-workflow/workflow-types/ lives in source repo only
Users clone or reference from GitHub
No local installation or indexing
```

**Why:**
- ✅ Simple to start
- ✅ No search pollution
- ✅ Clear separation
- ✅ Easy to iterate on design

### Phase 2: CLI Tool (After Validation)

```
Create agent-os-workflow-generators package
Provides: agent-os generate-workflow command
Generators read from package, not local project
```

**Why:**
- ✅ Better user experience
- ✅ Still no local installation/indexing
- ✅ Easy distribution
- ✅ Version management

---

## Search Scope Configuration

### Current Behavior

```python
# mcp_server/rag_engine.py
def load_standards(self):
    """Load standards from .praxis-os/standards/ and universal/standards/"""
    # Indexes everything under these directories
```

### Recommended Exclusions

```python
def _should_index_file(self, file_path: str) -> bool:
    """Determine if file should be indexed."""
    
    # Exclude build-time / meta-level content
    exclude_patterns = [
        '.praxis-os/workflow-creation-systems',  # If we add this
        'meta-workflow/workflow-types',         # If accidentally copied
        'templates/',                            # Template directories
        'scripts/',                              # Generator scripts
    ]
    
    # Only index runtime content
    include_patterns = [
        '.praxis-os/workflows',                   # Generated workflows
        '.praxis-os/standards',                   # Project standards
        'universal/standards',                   # Universal standards
        'universal/workflows',                   # Workflow implementations
    ]
```

---

## Decision Matrix

| Aspect | Source Only | Local + Indexed | Local Not Indexed |
|--------|-------------|-----------------|-------------------|
| Search pollution | ✅ None | ❌ High | ✅ None |
| Offline access | ❌ No | ✅ Yes | ✅ Yes |
| Up-to-date | ✅ Always | ❌ Stale | ❌ Stale |
| Installation size | ✅ Small | ❌ Large | ❌ Medium |
| Cognitive load | ✅ Low | ❌ High | ✅ Low |
| Version management | ✅ Simple | ❌ Complex | ⚠️ Moderate |
| User experience | ⚠️ Extra step | ✅ Integrated | ⚠️ Manual access |

**Winner:** Source Only (with CLI tool in Phase 2)

---

## Documentation Updates

### README.md

```markdown
## Workflow Creation

prAxIs OS includes workflow creation systems for common patterns:

### Test Generation

Create test generation workflows for any language:

```bash
# Option 1: Use CLI tool (recommended)
pip install agent-os-workflow-generators
agent-os generate-workflow test-generation --language python

# Option 2: Use source directly
git clone https://github.com/honeyhiveai/praxis-os.git
cd meta-workflow/workflow-types/test-generation/
python scripts/generate-test-workflow.py --language python --project ~/my-project/
```

**This creates a workflow in your project** that you then use via MCP tools.

The creation system itself is NOT installed in your project to avoid search pollution.
```

---

## Final Recommendation

### ✅ Keep in Source Repo Only

**Location:** `meta-workflow/workflow-types/` in source repository  
**Access:** Via git clone or published CLI tool  
**Installation:** NOT copied to user projects  
**Indexing:** NOT indexed by MCP search_standards

### Rationale

1. **No Search Pollution**: Users searching standards get workflow content, not creation system content
2. **Clear Separation**: Build-time (creation) vs runtime (usage)
3. **Always Up-to-Date**: Users reference latest, no stale local copies
4. **Smaller Installation**: User projects only contain what they need
5. **Simple Mental Model**: "I generate once, then use the generated workflow"

### Implementation Path

**Phase 1** (Now):
- Keep in source repo
- Document how to access and use
- Manual generation process

**Phase 2** (After validation):
- Create `agent-os-workflow-generators` package
- Provide `agent-os generate-workflow` CLI
- Seamless experience, still no local indexing

---

## Conclusion

**Answer:** These should exist in **source repo only**, NOT installed locally.

**Why:**
- Prevents search pollution
- Clear separation of concerns
- Better user experience (focused results)
- Simpler version management

**User Flow:**
1. Clone source or use CLI tool (one-time)
2. Generate workflow into project (one-time)
3. Use generated workflow (ongoing)
4. Never need to reference creation system again

The generated workflows ARE indexed and searchable. The creation system is NOT.

---

**Document End**

