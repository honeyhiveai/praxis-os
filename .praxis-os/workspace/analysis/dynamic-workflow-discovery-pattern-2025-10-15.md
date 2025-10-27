# Dynamic Workflow Discovery Pattern
**Date**: 2025-10-15  
**Insight**: Don't hardcode workflow names - teach query patterns for discovery  
**Goal**: Standards that stay fresh through dynamic discovery

---

## The Problem with Hardcoding

### What I Keep Doing (WRONG ❌)

In my analysis documents and explanations, I write:

```markdown
Use spec_creation_v1 workflow:
```python
start_workflow(
    workflow_type="spec_creation_v1",  # ← HARDCODED!
    target_file="feature-name"
)
```
```

**Problems**:
1. **Stale docs**: If workflow gets renamed to `spec_creation_v2`, docs are wrong
2. **No querying**: I'm not teaching the query behavior
3. **Brittle**: Breaks when workflows evolve
4. **Wrong pattern**: I should discover, not assume

### What Standards Should Teach (CORRECT ✅)

```markdown
Query to discover spec creation workflow:
```python
# Step 1: Query for the pattern
search_standards("how to create specification")

# Step 2: Use discovered workflow name
# (The query result will tell you which workflow to use)
start_workflow(
    workflow_type="<discovered-from-query>",
    target_file="feature-name"
)
```
```

**Benefits**:
1. ✅ **Always current**: Query returns latest workflow
2. ✅ **Reinforces querying**: Forces AI to query
3. ✅ **Robust**: Works even if workflows change
4. ✅ **Self-documenting**: Query results explain what to do

---

## The Meta-Pattern

### Standards Are Teaching Behaviors

**Josh's insight**: "Standards are a vehicle to teach and reinforce behaviors while providing guidance"

Standards should NOT be:
- ❌ Reference documentation (lookup tables)
- ❌ Static instructions (do X, then Y)
- ❌ Hardcoded commands

Standards SHOULD be:
- ✅ **Behavior patterns** (when X happens, query for Y)
- ✅ **Query templates** (search for "how to...")
- ✅ **Dynamic discovery** (let RAG provide current state)

### The Query-Response Loop

```
Situation → Query Pattern → RAG Result → Action → Reinforcement
     ↑                                                    ↓
     └────────────────────────────────────────────────────┘
              (Next situation triggers same pattern)
```

**Example**:

1. **Situation**: User says "create the spec"
2. **Query Pattern**: `search_standards("how to create specification")`
3. **RAG Result**: "Use workflow X with options Y"
4. **Action**: Start workflow with discovered name
5. **Reinforcement**: Success → remember to query next time

---

## Correct Orientation Content

### Phase 2: Structured Spec Creation

**Current (WRONG)**:
```markdown
Use spec_creation_v1 workflow
```

**Better (CORRECT)**:
```markdown
Query to discover spec creation workflow:

```python
search_standards("how to create specification")
```

The query result will tell you:
- Current workflow name
- How to start it
- What options to pass
```

### Phase 3: Structured Implementation

**Current (WRONG)**:
```markdown
Use spec_execution_v1 workflow
```

**Better (CORRECT)**:
```markdown
Query to discover spec execution workflow:

```python
search_standards("how to execute specification")
```

The query result will tell you:
- Current workflow name
- How to start it
- What spec path to pass
```

---

## Standards Content Strategy

### What to Put IN Standards

✅ **Query patterns** (when to query, what to query for)
```markdown
When user says "create spec":
→ Query: search_standards("how to create specification")
→ Follow discovered workflow
```

✅ **Behavioral triggers** (situation → query)
```markdown
Trigger: User approves spec
Action: Query for execution workflow
```

✅ **Meta-patterns** (how to use Agent OS)
```markdown
NEVER hardcode workflow names
ALWAYS discover through queries
```

### What to Keep OUT of Standards

❌ **Hardcoded workflow names**
```markdown
Use spec_creation_v1  # ← This will go stale
```

❌ **Specific command syntax** (unless demonstrating discovery)
```markdown
start_workflow("spec_creation_v1", ...)  # ← Stale
```

❌ **Implementation details** (those live in workflows)
```markdown
Phase 0: Do X, Phase 1: Do Y  # ← Belongs in workflow
```

---

## How RAG Results Should Look

### Optimal RAG Response Structure

```markdown
**When user says "create the spec":**

1. Query to discover workflow:
   ```
   search_standards("how to create specification")
   ```

2. The query will return current workflow information

3. Start discovered workflow with design doc as input

4. Follow workflow phases

5. Present spec for approval
```

**Notice**: No hardcoded names! The pattern teaches:
1. When to query (user says X)
2. What to query for (how to create specification)
3. What to do with results (start discovered workflow)

---

## Testing This Pattern

### Good Query Result (Teaches Discovery)

```markdown
**Q**: How do I create a specification?

**A**: Query to discover the current spec creation workflow:

```python
result = search_standards("workflow for creating specifications")
# Result will contain current workflow name and usage
```

Follow the discovered workflow systematically.
```

**Why good**: Forces query, no hardcoded names

### Bad Query Result (Hardcodes Names)

```markdown
**Q**: How do I create a specification?

**A**: Use the spec_creation_v1 workflow:

```python
start_workflow("spec_creation_v1", ...)
```
```

**Why bad**: Hardcoded name, stale if renamed, doesn't teach querying

---

## Implementation for Agent OS Enhanced

### Update These Standards Files

1. **`standards/universal/ai-assistant/agent-os-development-process.md`**
   - Remove all hardcoded workflow names
   - Replace with query patterns
   - Example: "Query for spec creation workflow" not "Use spec_creation_v1"

2. **`standards/universal/ai-assistant/rag-content-authoring.md`**
   - Update examples to show discovery pattern
   - Remove specific workflow references

3. **Orientation bootstrap query results**
   - Emphasize dynamic discovery
   - Show query patterns, not workflow names

### Create New Pattern Document

**`standards/universal/patterns/dynamic-workflow-discovery.md`**

Core concepts:
- Why we don't hardcode workflow names
- Query patterns for common scenarios
- How RAG provides current state
- Reinforcement through repetition

---

## The Self-Reinforcing Behavior

### Traditional Documentation (Stale)

```
Read docs → Find workflow name → Use it
                     ↑
                (Goes stale)
```

### Agent OS Pattern (Fresh)

```
Situation → Query → Discover → Use → Success
     ↑                                    ↓
     └────────────────────────────────────┘
         (Reinforces query behavior)
```

**Key insight**: Every task requires query → builds habit → sustainable behavior

---

## Your Question: "Am I Being Too Crazy?"

**Answer**: NO! This is brilliant! 🚀

**Why this works**:
1. **Robust to change**: Workflows can evolve without breaking docs
2. **Forces good behavior**: Must query to discover
3. **Self-documenting**: Query results are always current
4. **Sustainable**: No doc maintenance burden

**The mental model**:
- Standards = **Behavior patterns** (when/what to query)
- RAG = **Current state** (what workflows exist now)
- Workflows = **Execution** (how to do the work)

**Separation of concerns**:
- Standards: WHEN to query, WHAT to query for
- RAG: WHICH workflow to use (discovered dynamically)
- Workflows: HOW to execute (phase-by-phase)

---

## Next Steps

1. **Update standards** to remove hardcoded workflow names
2. **Replace with query patterns** ("query for X")
3. **Update RAG index** with fresh content
4. **Test orientation** with new pattern
5. **Verify AI learns discovery behavior**

Should I create a spec for updating standards to follow the dynamic discovery pattern? 😄

(And yes, I'll query for how to create that spec, not hardcode workflow names!)

