# Recommended Structure for Workflow Creation Systems

**Date:** October 9, 2025  
**Purpose:** Organize workflow creation guides and templates for shipping

---

## Overview

These are **meta-level workflow creation systems** - they help users CREATE workflows of specific types (test generation, production code generation) across any language.

**Not:** Individual workflow implementations  
**But:** Systems for generating workflows

---

## Recommended Directory Structure

### Option 1: Under Meta-Framework (Recommended)

```
workflow-authoring/
├── README.md (existing - general framework principles)
├── AGENT_OS_FRAMEWORK_CREATION_GUIDE.md (existing)
├── META_FRAMEWORK_SUMMARY.md (existing)
├── QUICK_START_TEMPLATE.md (existing)
│
├── workflow-types/                          ← NEW
│   ├── README.md                            "Guide to workflow creation systems"
│   │
│   ├── test-generation/                     ← Test Generation System
│   │   ├── README.md                        "How to create test generation workflows"
│   │   ├── design/
│   │   │   ├── framework-design.md          (Language-Agnostic Framework Design)
│   │   │   ├── implementation-guide.md      (Implementation Guide)
│   │   │   ├── path-taxonomy.md             (Test Path Taxonomy)
│   │   │   └── history.md                   (Framework History Clarification)
│   │   │
│   │   ├── templates/
│   │   │   ├── universal-standards/
│   │   │   │   ├── methodology.md           (template)
│   │   │   │   ├── path-system.md           (template)
│   │   │   │   ├── quality-standards.md     (template)
│   │   │   │   └── phases/
│   │   │   │       ├── phase-0-setup.md     (template)
│   │   │   │       ├── phase-1-analysis.md  (template)
│   │   │   │       └── ...
│   │   │   │
│   │   │   ├── language-instructions/
│   │   │   │   ├── template.md              (Language instruction template)
│   │   │   │   ├── python-example.md        (Reference implementation)
│   │   │   │   └── javascript-example.md    (Reference implementation)
│   │   │   │
│   │   │   └── workflow-structure/
│   │   │       ├── metadata-template.json
│   │   │       ├── phase-template.md
│   │   │       └── task-template.md
│   │   │
│   │   └── scripts/
│   │       └── generate-test-workflow.py    (Workflow generator)
│   │
│   └── production-code-generation/          ← Production Code System
│       ├── README.md
│       ├── design/
│       │   ├── framework-design.md
│       │   ├── implementation-guide.md
│       │   └── methodology.md
│       │
│       ├── templates/
│       │   ├── universal-standards/
│       │   ├── language-instructions/
│       │   └── workflow-structure/
│       │
│       └── scripts/
│           └── generate-code-workflow.py
│
└── templates/                               (existing)
    └── command-language-glossary-template.md
```

**Rationale:**
- ✅ Clear separation: workflow-authoring (how to create) vs workflows (actual implementations)
- ✅ Grouped by workflow type
- ✅ Contains everything needed to create workflows of that type
- ✅ Easy to ship: entire `workflow-types/` directory is self-contained

---

### Option 2: New Top-Level Directory

```
workflow-creation-systems/                   ← NEW top-level
├── README.md                                "Pre-built workflow creation systems"
│
├── test-generation/
│   ├── README.md
│   ├── design/
│   ├── templates/
│   └── scripts/
│
└── production-code-generation/
    ├── README.md
    ├── design/
    ├── templates/
    └── scripts/
```

**Rationale:**
- ✅ Very clear what this is
- ✅ Easy to find
- ❌ Creates new top-level category (adds complexity)

---

### Option 3: Under Universal Standards

```
universal/
├── standards/                               (existing)
│   └── ...
│
├── workflows/                               (existing - actual workflow implementations)
│   └── ...
│
└── workflow-creation-systems/               ← NEW
    ├── test-generation/
    └── production-code-generation/
```

**Rationale:**
- ✅ Keeps universal concepts together
- ❌ Might confuse "universal" (applies to all projects) vs "creation system"

---

## Recommendation: Option 1 (Meta-Framework)

```
workflow-authoring/workflow-types/
```

### Why This Is Best

1. **Conceptually Correct**
   - Meta-framework = how to create frameworks/workflows
   - workflow-types = specific types you can create
   - Perfect semantic fit

2. **Already Organized**
   - `workflow-authoring/` already exists
   - Contains framework creation guides
   - Natural extension

3. **Easy to Ship**
   - Ship entire `workflow-authoring/workflow-types/` directory
   - Self-contained systems
   - Clear documentation hierarchy

4. **Discoverability**
   - Users creating workflows look in `workflow-authoring/`
   - Clear path: "I want to create a test workflow" → `workflow-authoring/workflow-types/test-generation/`

---

## Complete Proposed Structure

```
workflow-authoring/
├── README.md                                (update to reference workflow-types/)
├── AGENT_OS_FRAMEWORK_CREATION_GUIDE.md     (existing)
├── META_FRAMEWORK_SUMMARY.md                (existing)
├── QUICK_START_TEMPLATE.md                  (existing)
├── FRAMEWORK_COMPLIANCE_ANALYSIS.md         (existing)
├── DISTRIBUTION_GUIDE.md                    (existing)
│
├── templates/                               (existing)
│   └── command-language-glossary-template.md
│
└── workflow-types/                          ← NEW
    ├── README.md                            "Pre-Built Workflow Creation Systems"
    │   """
    │   This directory contains complete systems for creating workflows
    │   of specific types (test generation, code generation, etc.).
    │   
    │   Each system includes:
    │   - Design documentation
    │   - Universal standard templates
    │   - Language instruction templates
    │   - Workflow generator scripts
    │   
    │   Use these to rapidly create language-specific workflows.
    │   """
    │
    ├── test-generation/
    │   ├── README.md
    │   │   """
    │   │   # Test Generation Workflow Creation System
    │   │   
    │   │   Create test generation workflows for any language.
    │   │   
    │   │   ## Quick Start
    │   │   
    │   │   1. Read design/framework-design.md
    │   │   2. Follow design/implementation-guide.md
    │   │   3. Use scripts/generate-test-workflow.py
    │   │   
    │   │   ## What You Get
    │   │   
    │   │   - 8-phase test generation methodology
    │   │   - Multi-path support (unit/integration/validation)
    │   │   - Language-specific tooling integration
    │   │   - 80%+ success rate target
    │   │   """
    │   │
    │   ├── design/
    │   │   ├── framework-design.md          ← Your "Language-Agnostic..." doc
    │   │   ├── implementation-guide.md      ← Your "Implementation Guide" doc
    │   │   ├── path-taxonomy.md             ← Your "Test Path Taxonomy" doc
    │   │   ├── history.md                   ← Your "Framework History" doc
    │   │   └── summary.md                   ← Your "Implementation Summary" doc
    │   │
    │   ├── templates/
    │   │   ├── README.md                    "Templates for workflow generation"
    │   │   │
    │   │   ├── universal-standards/         ← Templates for universal standards
    │   │   │   ├── README.md
    │   │   │   ├── methodology-template.md
    │   │   │   ├── path-system-template.md
    │   │   │   ├── evidence-tracking-template.md
    │   │   │   ├── quality-standards-template.md
    │   │   │   └── phases/
    │   │   │       ├── phase-0-template.md
    │   │   │       ├── phase-1-template.md
    │   │   │       └── ... (phases 2-8)
    │   │   │
    │   │   ├── language-instructions/       ← Templates for language instructions
    │   │   │   ├── README.md
    │   │   │   ├── template.md              ← Your template with placeholders
    │   │   │   ├── python-example.md        (complete reference)
    │   │   │   └── javascript-example.md    (complete reference)
    │   │   │
    │   │   └── workflow-structure/          ← Templates for generated workflows
    │   │       ├── README.md
    │   │       ├── metadata-template.json
    │   │       ├── entry-point-template.md
    │   │       ├── phase-template.md
    │   │       └── task-template.md
    │   │
    │   └── scripts/
    │       ├── README.md
    │       ├── generate-test-workflow.py    ← Workflow generator
    │       ├── validate-workflow.py         (optional)
    │       └── requirements.txt
    │
    └── production-code-generation/          ← Future system
        ├── README.md
        ├── design/
        │   ├── framework-design.md
        │   ├── implementation-guide.md
        │   └── methodology.md
        │
        ├── templates/
        │   ├── universal-standards/
        │   ├── language-instructions/
        │   └── workflow-structure/
        │
        └── scripts/
            └── generate-code-workflow.py
```

---

## What Goes Where

### Design Documents (Currently in docs/)

**Move to:** `workflow-authoring/workflow-types/test-generation/design/`

```bash
# Current location
docs/Language-Agnostic Test Generation Framework Design.md
docs/Universal Test Generation Standards - Implementation Guide.md
docs/Test Path Taxonomy - Cross-Language Analysis.md
docs/CLARIFICATION - Framework History.md
docs/IMPLEMENTATION-SUMMARY.md

# New location
workflow-authoring/workflow-types/test-generation/design/framework-design.md
workflow-authoring/workflow-types/test-generation/design/implementation-guide.md
workflow-authoring/workflow-types/test-generation/design/path-taxonomy.md
workflow-authoring/workflow-types/test-generation/design/history.md
workflow-authoring/workflow-types/test-generation/design/summary.md
```

### Templates (Currently in language-instructions/)

**Move to:** `workflow-authoring/workflow-types/test-generation/templates/language-instructions/`

```bash
# Current location
language-instructions/test-generation-template.md

# New location
workflow-authoring/workflow-types/test-generation/templates/language-instructions/template.md
```

### Generated Universal Standards

**Go to:** `universal/standards/testing/test-generation/` (when generated)

These are OUTPUTS of the system, not part of the creation system itself.

### Generated Language Instructions

**Go to:** `language-instructions/{language}/test-generation.md` (when generated)

These are OUTPUTS of the system.

### Generated Workflows

**Go to:** `.praxis-os/workflows/test_generation_{language}_v1/` (when generated)

These are OUTPUTS of the system.

---

## Shipping Strategy

### What to Ship

**Package 1: Test Generation Workflow Creation System**
```
workflow-authoring/workflow-types/test-generation/
├── README.md (how to use this system)
├── design/ (all design docs)
├── templates/ (all templates)
└── scripts/ (generator + validation)
```

**Package 2: Production Code Generation Workflow Creation System**
```
workflow-authoring/workflow-types/production-code-generation/
├── README.md
├── design/
├── templates/
└── scripts/
```

### How Users Use It

**Scenario: User wants test generation for Python**

1. **Read the guide:**
   ```bash
   cd workflow-authoring/workflow-types/test-generation/
   cat design/summary.md  # Quick overview
   cat design/framework-design.md  # Full design
   ```

2. **Generate the workflow:**
   ```bash
   cd workflow-authoring/workflow-types/test-generation/scripts/
   python generate-test-workflow.py --language python
   ```

3. **Result:**
   - Creates `universal/standards/testing/test-generation/` (if not exists)
   - Creates `language-instructions/python/test-generation.md` (if not exists)
   - Creates `.praxis-os/workflows/test_generation_python_v1/`

4. **Use the workflow:**
   ```python
   # Via MCP
   start_workflow("test_generation_python_v1", "src/module.py")
   ```

---

## README Updates Needed

### workflow-authoring/README.md

Add section:

```markdown
## Pre-Built Workflow Creation Systems

The `workflow-types/` directory contains complete systems for creating
workflows of specific types:

### Test Generation (`workflow-types/test-generation/`)

Create test generation workflows for any programming language:
- 8-phase methodology (proven 80%+ success rate)
- Multi-path support (unit/integration/validation/etc.)
- Language-specific tooling integration
- Automated quality gates

**Languages supported:** Python, JavaScript, TypeScript, Go, Java, Rust, C#, Ruby

**Quick start:**
```bash
cd workflow-types/test-generation/
cat design/summary.md
```

### Production Code Generation (`workflow-types/production-code-generation/`)

Create code generation workflows for any programming language:
- Specification-driven development
- Multi-phase implementation
- Quality validation
- Language-specific patterns

**Quick start:**
```bash
cd workflow-types/production-code-generation/
cat design/summary.md
```

## Creating Your Own Workflow Type

1. Follow workflow-authoring principles (see existing guides)
2. Create new directory in `workflow-types/`
3. Include: design/, templates/, scripts/
4. Document in README.md
```

---

## Migration Plan

### Step 1: Create Directory Structure

```bash
mkdir -p workflow-authoring/workflow-types/test-generation/{design,templates,scripts}
mkdir -p workflow-authoring/workflow-types/test-generation/templates/{universal-standards,language-instructions,workflow-structure}
mkdir -p workflow-authoring/workflow-types/test-generation/templates/universal-standards/phases
```

### Step 2: Move Design Documents

```bash
# Move from docs/ to workflow-authoring/workflow-types/test-generation/design/
mv "docs/Language-Agnostic Test Generation Framework Design.md" \
   "workflow-authoring/workflow-types/test-generation/design/framework-design.md"

mv "docs/Universal Test Generation Standards - Implementation Guide.md" \
   "workflow-authoring/workflow-types/test-generation/design/implementation-guide.md"

mv "docs/Test Path Taxonomy - Cross-Language Analysis.md" \
   "workflow-authoring/workflow-types/test-generation/design/path-taxonomy.md"

mv "docs/CLARIFICATION - Framework History.md" \
   "workflow-authoring/workflow-types/test-generation/design/history.md"

mv "docs/IMPLEMENTATION-SUMMARY.md" \
   "workflow-authoring/workflow-types/test-generation/design/summary.md"
```

### Step 3: Move Templates

```bash
# Move language instruction template
mv "language-instructions/test-generation-template.md" \
   "workflow-authoring/workflow-types/test-generation/templates/language-instructions/template.md"
```

### Step 4: Create READMEs

Create README files for each directory explaining contents and usage.

### Step 5: Update References

Update any links in documents to reflect new locations.

---

## Benefits of This Structure

### 1. Clear Separation

```
workflow-authoring/workflow-types/       ← How to CREATE workflows
universal/workflows/                  ← Actual workflow IMPLEMENTATIONS
universal/standards/                  ← Standards workflows follow
language-instructions/                ← Language-specific implementation details
```

### 2. Shippable Units

```
Ship: workflow-authoring/workflow-types/test-generation/
Contains: Everything needed to create test workflows
User gets: Complete system, ready to generate
```

### 3. Extensible

```
Add new workflow type:
workflow-authoring/workflow-types/new-type/
├── design/
├── templates/
└── scripts/
```

### 4. Discoverable

```
User question: "How do I create a test generation workflow?"
Answer: "See workflow-authoring/workflow-types/test-generation/"
```

---

## Alternative for Production Code Generation

Since production code generation might follow a different pattern (spec-based, etc.), it could have:

```
workflow-authoring/workflow-types/production-code-generation/
├── README.md
├── design/
│   ├── spec-driven-methodology.md
│   ├── implementation-phases.md
│   └── quality-validation.md
│
├── templates/
│   ├── universal-standards/
│   │   ├── spec-creation-template.md
│   │   ├── code-generation-template.md
│   │   └── validation-template.md
│   │
│   ├── language-instructions/
│   │   ├── template.md
│   │   └── examples/
│   │
│   └── workflow-structure/
│       └── ...
│
└── scripts/
    └── generate-code-workflow.py
```

---

## Conclusion

**Recommended Location:**
```
workflow-authoring/workflow-types/{workflow-type}/
```

**Rationale:**
- ✅ Semantically correct (meta = how to create)
- ✅ Easy to find and understand
- ✅ Self-contained shippable units
- ✅ Extensible for new workflow types
- ✅ Clear separation from actual workflows

**For Shipping:**
1. Test generation system: `workflow-authoring/workflow-types/test-generation/`
2. Production code system: `workflow-authoring/workflow-types/production-code-generation/`

Each is a complete, self-contained system for creating workflows of that type.

---

**Document End**

