# REVISED: Workflow Creation Systems Location

**Date:** October 9, 2025  
**Status:** Updated based on actual meta-workflow usage  
**Context:** Meta-framework standards ARE local and indexed

---

## Key Understanding

### Meta-Framework Standards (Existing, Indexed)

**Location:** `universal/standards/meta-workflow/`

**Contents:**
- `framework-creation-principles.md` (~300 lines)
- `three-tier-architecture.md`
- `horizontal-decomposition.md`
- `command-language.md`
- `validation-gates.md`

**Purpose:** **Principles and guidelines** for creating ANY workflow

**Usage:** Referenced by AI WHILE creating custom workflows

**Indexed:** ✅ YES - These are runtime standards

```python
# AI creating a custom workflow
search_standards("horizontal decomposition guidelines")
# Returns: meta-workflow/horizontal-decomposition.md
# AI applies these principles to workflow being created
```

### Workflow Construction Standards (Existing, Indexed)

**Location:** `universal/standards/workflows/`

**Contents:**
- `workflow-construction-standards.md` (~400 lines)
- `workflow-metadata-standards.md`
- `workflow-system-overview.md`

**Purpose:** **Specific application** of meta-workflow to workflow structure

**Usage:** Referenced by AI WHILE creating workflows

**Indexed:** ✅ YES - These are runtime standards

---

## The New Question: Workflow-Type-Specific Creation Systems

### What We're Adding

**Test Generation Workflow Creation System:**
- Complete design documents (2000+ lines)
- Universal standard templates (per phase)
- Language instruction templates
- Generator scripts
- Path taxonomy documentation
- Implementation guides

**Production Code Generation Workflow Creation System:**
- Similar comprehensive package

### Key Difference

| Existing Meta-Framework | New Workflow Creation Systems |
|------------------------|-------------------------------|
| **Principles** | **Complete implementations** |
| "Use horizontal decomposition" | "Here's Phase 1 template with all sections" |
| "Apply command language" | "Here's exact command structure for test gen" |
| "Three-tier architecture" | "Here's test-gen-specific 8-phase breakdown" |
| ~100-300 lines per file | 2000+ lines total per system |
| **Universal principles** | **Domain-specific (testing, code gen)** |

---

## Recommendation: Install But Organize Carefully

### Proposed Structure

```
universal/standards/
├── meta-workflow/                    ← Existing (indexed ✅)
│   ├── framework-creation-principles.md
│   └── ...
│
├── workflows/                         ← Existing (indexed ✅)
│   ├── workflow-construction-standards.md
│   └── ...
│
└── workflow-types/                    ← NEW (indexed ✅ with caveats)
    ├── README.md
    │   """
    │   Workflow-type-specific creation systems.
    │   
    │   These are complete systems for creating workflows of
    │   specific types (test generation, production code, etc.).
    │   
    │   More detailed than meta-workflow principles - these are
    │   domain-specific implementations with templates and guides.
    │   """
    │
    ├── test-generation/
    │   ├── README.md
    │   │   """
    │   │   # Test Generation Workflow Creation System
    │   │   
    │   │   **When to use:** Creating test generation workflows
    │   │   **References:** meta-workflow/, workflows/ standards
    │   │   **Output:** Language-specific test workflow
    │   │   
    │   │   ## Quick Start
    │   │   1. Read design/overview.md
    │   │   2. Use generator or manual creation
    │   │   3. Follow templates/
    │   │   """
    │   │
    │   ├── design/
    │   │   ├── overview.md               (~100 lines - searchable summary)
    │   │   ├── methodology.md            (~200 lines - 8-phase approach)
    │   │   ├── path-system.md            (~150 lines - unit/integration/validation)
    │   │   └── implementation-guide.md   (~200 lines - how to create)
    │   │
    │   ├── templates/
    │   │   ├── universal-standards/
    │   │   │   ├── phase-0-template.md
    │   │   │   ├── phase-1-template.md
    │   │   │   └── ... (phase templates)
    │   │   │
    │   │   ├── language-instructions/
    │   │   │   ├── template.md           (with placeholders)
    │   │   │   ├── python-example.md
    │   │   │   └── javascript-example.md
    │   │   │
    │   │   └── workflow-structure/
    │   │       ├── metadata-template.json
    │   │       └── task-template.md
    │   │
    │   └── scripts/
    │       └── generate-workflow.py       (NOT indexed, see below)
    │
    └── production-code-generation/
        └── ... (similar structure)
```

---

## Search Behavior Strategy

### What Gets Indexed

**✅ Design Documentation:**
```
universal/standards/workflow-types/test-generation/design/
├── overview.md            ✅ Indexed
├── methodology.md         ✅ Indexed
├── path-system.md         ✅ Indexed
└── implementation-guide.md ✅ Indexed
```

**Why:** AI needs to search "how to create test workflows" and get guidance

**✅ Template READMEs:**
```
templates/universal-standards/README.md   ✅ Indexed
templates/language-instructions/README.md  ✅ Indexed
```

**Why:** Help AI understand what templates exist

**❌ Template Files:**
```
templates/universal-standards/phase-0-template.md  ❌ NOT indexed
templates/language-instructions/template.md        ❌ NOT indexed
```

**Why:** These are TEMPLATES with placeholders, not actual standards
- Should NOT appear in search results
- Used via direct reference when generating

**❌ Scripts:**
```
scripts/generate-workflow.py  ❌ NOT indexed
```

**Why:** Code files, not documentation

---

## How to Control Indexing

### Option 1: Selective .cursorignore (Recommended)

```
# .cursorignore (or .praxis-os/.ragignore if we create one)

# Don't index template files (have placeholders)
universal/standards/workflow-types/*/templates/universal-standards/*.md
universal/standards/workflow-types/*/templates/language-instructions/*.md
universal/standards/workflow-types/*/templates/workflow-structure/*.md

# Don't index scripts
universal/standards/workflow-types/*/scripts/

# DO index design docs (no exclusion needed, just document as exception)
```

### Option 2: Naming Convention

```
templates/
├── README.md               ← Indexed (explains templates)
├── phase-0.template.md     ← NOT indexed (*.template.md excluded)
├── phase-1.template.md     ← NOT indexed
└── python.example.md       ← Indexed (example, not template)
```

Add to RAG engine:
```python
def _should_index_file(self, file_path: str) -> bool:
    # Exclude template files
    if '.template.' in file_path:
        return False
    # Include example files
    if '.example.' in file_path:
        return True
```

### Option 3: Metadata Flag

Add to file frontmatter:
```markdown
---
index_in_rag: false
reason: "Template file with placeholders"
---

# Phase 0 Template
...
```

---

## Search Result Quality

### Good Search Results

```python
search_standards("test generation methodology")

# Returns:
1. universal/standards/workflow-types/test-generation/design/methodology.md
   "8-phase test generation approach..."
   
2. universal/standards/workflow-types/test-generation/design/overview.md
   "Complete test generation system overview..."
   
3. universal/standards/meta-workflow/framework-creation-principles.md
   "Universal framework principles..."

# ✅ User gets guidance, not templates with placeholders
```

### Bad Search Results (If Templates Indexed)

```python
search_standards("test generation Phase 1")

# Returns:
1. universal/standards/workflow-types/test-generation/templates/.../phase-1-template.md
   "🛑 EXECUTE-NOW: {COMMAND_PLACEHOLDER}..."
   
2. .praxis-os/workflows/test_generation_python_v1/phases/1/task-1.md
   "🛑 EXECUTE-NOW: python -c 'import ast...'"

# ❌ User confused: which one? One has placeholders!
```

---

## Mental Model for Users

### Hierarchy of Standards

```
Level 1: Meta-Framework (Universal Principles)
├── universal/standards/meta-workflow/
└── "HOW to create ANY workflow"

Level 2: Workflow Construction (Workflow-Specific)
├── universal/standards/workflows/
└── "HOW to structure workflows in Agent OS"

Level 3: Workflow-Type Systems (Domain-Specific)
├── universal/standards/workflow-types/
└── "WHAT to include in test/code workflows"

Level 4: Generated Workflows (Project-Specific)
├── .praxis-os/workflows/test_generation_python_v1/
└── "EXECUTE this for Python testing"
```

### Search Expectations

**User Query:** "How do I create a test generation workflow?"

**Expected Path:**
1. Search finds: `workflow-types/test-generation/design/overview.md`
2. User reads: "8-phase methodology, path system, etc."
3. User decides: Generate automatically OR create manually
4. If manual: User references templates directly (not via search)
5. If automatic: User runs generator script
6. Result: Workflow created in `.praxis-os/workflows/`

---

## Recommendation Summary

### ✅ Install Locally

**Location:** `universal/standards/workflow-types/`

**Rationale:**
- Consistent with meta-workflow being local
- Available offline
- Can be referenced during workflow creation
- Part of "standards" that guide workflow creation

### ✅ Index Selectively

**Index:**
- ✅ Design documentation (overview, methodology, guides)
- ✅ README files (explain what templates exist)
- ✅ Example files (python-example.md, javascript-example.md)

**Don't Index:**
- ❌ Template files (have placeholders like {PLACEHOLDER})
- ❌ Generator scripts (Python code, not docs)

**Method:** Use `.cursorignore` or file naming convention

### ✅ Clear Documentation

Add prominent README explaining:
```markdown
# Workflow-Type-Specific Creation Systems

These are detailed systems for creating workflows of specific
types (test generation, production code generation, etc.).

## vs Meta-Framework Standards

- **Meta-framework**: Universal principles (any workflow)
- **Workflow-types**: Domain-specific systems (test/code workflows)

## vs Generated Workflows

- **Workflow-types**: Templates and guides (CREATE workflows)
- **Generated workflows**: Actual workflows (EXECUTE workflows)

## Using These Systems

1. Search for overview: `search_standards("test generation overview")`
2. Read design docs (indexed, searchable)
3. Reference templates directly (not searchable, intentionally)
4. Generate workflow with scripts OR create manually
5. Use generated workflow in .praxis-os/workflows/
```

---

## Implementation

### Step 1: Create Directory

```bash
mkdir -p universal/standards/workflow-types/test-generation/{design,templates,scripts}
mkdir -p universal/standards/workflow-types/test-generation/templates/{universal-standards,language-instructions,workflow-structure}
```

### Step 2: Move Design Docs

```bash
# Move from docs/ to universal/standards/workflow-types/test-generation/design/
mv "docs/Language-Agnostic Test Generation Framework Design.md" \
   "universal/standards/workflow-types/test-generation/design/framework-design.md"

mv "docs/Test Path Taxonomy - Cross-Language Analysis.md" \
   "universal/standards/workflow-types/test-generation/design/path-taxonomy.md"

# etc.
```

### Step 3: Split Large Design Docs

The design docs are quite large (2000+ lines). Split into focused pieces:

```
design/
├── overview.md           (~100 lines - quick summary, VERY searchable)
├── methodology.md        (~200 lines - 8-phase approach)
├── path-system.md        (~150 lines - unit/integration/validation)
├── language-agnostic.md  (~200 lines - universal vs language-specific)
├── implementation.md     (~200 lines - how to implement)
└── history.md            (~100 lines - V3 → Agent OS)
```

**Why Split:** Easier to search, easier to find relevant sections

### Step 4: Add Selective Indexing

```bash
# Add to .cursorignore or create .praxis-os/.ragignore
echo "universal/standards/workflow-types/*/templates/**/*.md" >> .cursorignore
echo "!universal/standards/workflow-types/*/templates/**/README.md" >> .cursorignore
echo "universal/standards/workflow-types/*/scripts/" >> .cursorignore
```

Or use naming convention:
```bash
# Rename templates
mv phase-0-setup.md phase-0-setup.template.md
mv phase-1-analysis.md phase-1-analysis.template.md
# Update RAG engine to skip *.template.md files
```

### Step 5: Create Clear READMEs

At each level:
- `universal/standards/workflow-types/README.md` - What these are
- `test-generation/README.md` - Test generation system overview
- `design/README.md` - Design doc organization
- `templates/README.md` - What templates exist (indexed)
- Each template directory: README explaining usage

---

## Final Structure

```
universal/standards/
├── meta-workflow/          ← Universal principles (indexed ✅)
├── workflows/               ← Workflow construction (indexed ✅)
└── workflow-types/          ← Domain-specific systems (indexed ✅ selectively)
    └── test-generation/
        ├── README.md        (indexed ✅)
        ├── design/          (indexed ✅ - searchable guides)
        │   ├── overview.md
        │   ├── methodology.md
        │   └── ...
        ├── templates/       (NOT indexed ❌ - templates have placeholders)
        │   ├── README.md    (indexed ✅ - explains templates)
        │   └── ...
        └── scripts/         (NOT indexed ❌ - code files)
```

---

## Conclusion

**Install locally:** ✅ YES - Consistent with meta-workflow standards  
**Index completely:** ❌ NO - Only index design docs, not templates  
**Location:** `universal/standards/workflow-types/`  
**Indexing:** Selective (design docs yes, templates no)

**Benefits:**
- ✅ Consistent with existing meta-workflow pattern
- ✅ Available offline
- ✅ Searchable guidance without placeholder confusion
- ✅ Clear hierarchy: principles → workflow-types → generated workflows

**Key Implementation:** Use selective indexing (via .cursorignore or naming) to exclude template files while indexing design documentation.

---

**Document End**

