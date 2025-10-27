# Spec-Driven Development Orientation Gap
**Date**: 2025-10-15  
**Problem**: I keep missing the 2-workflow process (design → spec_creation_v1 → spec_execution_v1)  
**Solution**: Make this clearer in orientation

---

## What I Keep Missing

### My Wrong Mental Model ❌

```
Design Doc → Implement Directly
```

I think:
1. Create design analysis doc
2. Start implementing
3. Write code directly

### Correct prAxIs OS Model ✅

```
Design Doc → spec_creation_v1 → Formal Spec → spec_execution_v1 → Implementation
```

The process is:
1. **Design discussion** (conversational with user)
2. **spec_creation_v1** workflow → produces 5-file spec structure
3. User reviews/approves spec
4. **spec_execution_v1** workflow → produces implementation (code + tests + docs)

---

## The 2-Workflow Process

### Workflow 1: spec_creation_v1

**Input**: Design document or discussion notes  
**Output**: 5-file formal spec in `.praxis-os/specs/YYYY-MM-DD-feature-name/`

**Files created**:
1. `README.md` - Executive summary
2. `srd.md` - Business requirements (Software Requirements Document)
3. `specs.md` - Technical specifications
4. `tasks.md` - Implementation task breakdown
5. `implementation.md` - Detailed implementation guidance

**Duration**: 30 minutes - 2 hours

**Example**:
```python
start_workflow(
    workflow_type="spec_creation_v1",
    target_file="validation-gates",
    options={"design_doc": ".praxis-os/specs/config-driven-validation-design-2025-10-15.md"}
)
```

### Workflow 2: spec_execution_v1

**Input**: Formal spec directory (output from spec_creation_v1)  
**Output**: Complete implementation (production code + tests + docs)

**Duration**: 2-8 hours

**Example**:
```python
start_workflow(
    workflow_type="spec_execution_v1",
    target_file="validation-gates",
    options={"spec_path": ".praxis-os/specs/2025-10-15-validation-gates"}
)
```

---

## Why I Keep Getting This Wrong

### Gap 1: Not Clear in Orientation

When I run the 8 bootstrap queries, I don't think I get clear guidance on:
- "There are TWO workflows for feature development"
- "Design → spec_creation → spec_execution"
- "Never implement directly from design docs"

### Gap 2: prAxIs OS Development Process Not Emphasized

The operating model is there, but the **2-workflow process** isn't emphasized enough.

I should learn:
1. ✅ Query liberally (I get this)
2. ✅ AI writes all code (I get this)
3. ✅ Use workflows for specs (I get this abstractly)
4. ❌ **TWO workflows required** (I keep missing this)
5. ❌ **spec_creation_v1 comes BEFORE spec_execution_v1** (I skip this)

### Gap 3: Confusion About "Design Docs"

When I create analysis documents like:
- `config-driven-validation-design-2025-10-15.md`
- `consolidated-workflow-tool-design-2025-10-15.md`

I think: "These are ready for implementation!"

But actually: "These are inputs TO spec_creation_v1!"

---

## Proposed Orientation Enhancement

### Add to Bootstrap Query 3: "Agent OS Development Process"

Current result should include:

```markdown
## Phase 2: Structured Spec Creation

**Critical**: This uses spec_creation_v1 workflow

**Trigger**: User says "Create the spec" OR "This design looks good, spec it"

**Process**:
1. Query: search_standards("how to create specification")
2. Discover spec_creation_v1 workflow
3. Start workflow with design doc as input
4. Follow phases to create 5-file spec
5. Present spec for approval

**Output**: `.praxis-os/specs/YYYY-MM-DD-feature-name/` with 5 files

## Phase 3: Structured Implementation

**Critical**: This uses spec_execution_v1 workflow

**Trigger**: User says "Implement the spec" OR "Approved, build it"

**Process**:
1. Query: search_standards("how to execute specification")
2. Discover spec_execution_v1 workflow
3. Start workflow with spec path as input
4. Follow phases to implement feature
5. Present complete implementation

**Output**: Production code + tests + documentation

## The 2-Workflow Process (MEMORIZE THIS!)

❌ NEVER: Design → Implement directly
✅ ALWAYS: Design → spec_creation_v1 → User approval → spec_execution_v1

Design docs are INPUTS to spec_creation_v1, not ready for implementation!
```

---

## What Should Be in Standards

### File: `standards/universal/ai-assistant/agent-os-development-process.md`

Should explicitly state:

```markdown
## The 2-Workflow Model

prAxIs OS uses TWO separate workflows for feature development:

### Workflow 1: Specification Creation (spec_creation_v1)
- **Input**: Design discussion, notes, or rough design doc
- **Output**: Formal 5-file specification
- **Duration**: 30min - 2 hours
- **User action**: Review and approve spec

### Workflow 2: Specification Execution (spec_execution_v1)
- **Input**: Approved formal specification
- **Output**: Complete implementation (code + tests + docs)
- **Duration**: 2-8 hours
- **User action**: Review and approve implementation

### Why Two Workflows?

1. **Separation of concerns**: Design ≠ Implementation
2. **Approval gate**: User reviews spec before code is written
3. **Quality assurance**: Each workflow has its own validation gates
4. **Clarity**: No confusion about "ready to implement"

### Common Mistake

❌ **Wrong**: Create design doc → Start implementing
```python
# AI thinks: "I have a design doc, let me write code"
search_replace("file.py", old, new)  # WRONG!
```

✅ **Correct**: Create design doc → spec_creation_v1 → spec_execution_v1
```python
# Step 1: Create formal spec
start_workflow("spec_creation_v1", "feature-name", 
               options={"design_doc": "design.md"})

# Step 2: Wait for user approval of spec

# Step 3: Execute spec
start_workflow("spec_execution_v1", "feature-name",
               options={"spec_path": ".praxis-os/specs/2025-10-15-feature-name"})
```
```

---

## How to Test Understanding

After orientation, AI should be able to answer:

**Q1**: "User gives you a design doc and says 'implement this'. What do you do?"

**A1**: 
1. Use spec_creation_v1 workflow to create formal spec
2. Present spec for user approval
3. After approval, use spec_execution_v1 to implement
4. Present complete implementation

**Q2**: "You created an analysis document. Is it ready for spec_execution_v1?"

**A2**: No! Analysis docs are inputs TO spec_creation_v1, not ready for spec_execution_v1.

**Q3**: "How many workflows are needed for feature development?"

**A3**: TWO workflows:
1. spec_creation_v1 (design → formal spec)
2. spec_execution_v1 (spec → implementation)

---

## Recommendation

Update orientation query results to emphasize:
1. **2-workflow process** is mandatory
2. **Design docs are not specs** (they're inputs to spec_creation_v1)
3. **Never implement directly** from design docs
4. **Always wait for user approval** between workflows

This should be prominent in Query 3 (Development Process) and Query 5 (Practical Examples).

---

## Next Steps

1. Update `standards/universal/ai-assistant/agent-os-development-process.md` to clarify 2-workflow model
2. Rebuild RAG index
3. Test orientation with new content
4. Verify AI understands the process

**Should I create a spec for this orientation enhancement?** 😄 (Using spec_creation_v1, of course!)

