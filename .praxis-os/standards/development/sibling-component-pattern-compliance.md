# Sibling Component Pattern Compliance

**Standard for ensuring new components follow the same architectural patterns as their siblings at the same level.**

---

## 🎯 TL;DR - Sibling Component Pattern Compliance Quick Reference

**Keywords for search**: sibling component pattern, architectural consistency, component level consistency, new component design, subsystem extension, pattern compliance, fractal pattern adherence, ComponentDescriptor registry, health check pattern, build status pattern, same level components, architectural integration, extending subsystems, component architecture consistency

**Core Principle:** When creating a new component at the same architectural level as existing components, it MUST follow the same patterns as its siblings. Query and study siblings before designing.

**Mandatory Pre-Design Queries:**
1. **Find siblings** - Query for existing components at same level
2. **Read implementations** - Study how siblings implement key methods
3. **Document patterns** - Explicitly state pattern compliance in spec
4. **Verify in tasks** - Include pattern compliance validation tasks

**Component Pattern Compliance Checklist:**
- [ ] Queried for sibling components before design
- [ ] Read sibling implementations (`__init__`, key methods)
- [ ] Spec includes "Pattern Compliance" section
- [ ] Spec explicitly states which patterns to follow
- [ ] Tasks include pattern verification steps
- [ ] Implementation matches sibling structure

**Common Anti-Patterns:**
- ❌ Designing without studying siblings
- ❌ Spec omits pattern compliance requirements
- ❌ Manual aggregation when siblings use fractal helpers
- ❌ Different method signatures than siblings
- ❌ Missing component registry when siblings have one

**When to Query This Standard:**
- Extending subsystem → `pos_search_project(content_type="standards", query="sibling component pattern compliance")`
- Creating index container → `pos_search_project(content_type="standards", query="how to match sibling component architecture")`
- Spec review → `pos_search_project(content_type="standards", query="architectural consistency checklist")`

---

## ❓ Questions This Answers

1. "How do I ensure my new component matches existing architecture?"
2. "What patterns should I follow when extending a subsystem?"
3. "How do I find and study sibling components?"
4. "What makes components 'siblings' at the same level?"
5. "What should I query before designing a new component?"
6. "How do I document pattern compliance in specs?"
7. "What methods should match across sibling components?"
8. "When do I use ComponentDescriptor vs manual implementation?"
9. "How do I verify pattern compliance during implementation?"
10. "What are common pattern compliance failures?"
11. "How do fractal patterns apply to new components?"
12. "What if siblings don't all follow the same pattern?"
13. "Do I need a 'Pattern Compliance' section in my spec?"
14. "How do I validate architectural consistency?"
15. "What happens if I skip sibling analysis?"
16. "How do health_check and build_status relate to siblings?"
17. "When do I deviate from sibling patterns?"
18. "How do I test pattern compliance?"
19. "What level of detail on patterns belongs in the spec?"
20. "How does this relate to fractal architecture?"

---

## 🎯 Purpose

Prevent architectural drift when extending subsystems by ensuring new components follow the same patterns as existing components at the same architectural level. This standard defines what "sibling components" are, how to identify them, and how to ensure new components maintain architectural consistency.

**Key Concepts:**
- **Sibling Components**: Components at the same architectural level (e.g., StandardsIndex, CodeIndex, ASTIndex are siblings)
- **Pattern Compliance**: New components follow same structure, methods, and patterns as siblings
- **Architectural Level**: Position in system hierarchy (e.g., Index Container level, Partition level, Component level)

---

## ❌ The Problem - Adding Components Without Studying Siblings

**What happens WITHOUT this standard:**

### Symptom 1: Architectural Drift
```python
# Siblings use fractal pattern:
class StandardsIndex(BaseIndex):
    def health_check(self) -> HealthStatus:
        return dynamic_health_check(self.components)
    
    def build_status(self) -> BuildStatus:
        return dynamic_build_status(self.components)

# New component violates pattern:
class CodePartition:  # ❌ No self.components registry
    def health_check(self) -> HealthStatus:
        # ❌ Manual aggregation (siblings use helper)
        all_healthy = True
        if self.semantic:
            if not self.semantic.health_check().healthy:
                all_healthy = False
        # ... manual logic ...
```

**Result:** New component works differently, has more bugs, harder to maintain

### Symptom 2: Incomplete Implementations
```python
# Siblings have both methods:
class StandardsIndex:
    def health_check(self) -> HealthStatus: ...
    def build_status(self) -> BuildStatus: ...

# New component missing method:
class CodePartition:
    def health_check(self) -> HealthStatus: ...
    # ❌ build_status() missing entirely!
```

**Result:** Runtime crashes when system expects method to exist

### Symptom 3: Specs Don't Mention Patterns
```markdown
<!-- Spec says: -->
## CodePartition Architecture
- Wraps semantic and graph sub-indexes
- Provides unified search interface

<!-- ❌ Never mentions: -->
<!-- - Must follow ComponentDescriptor pattern like StandardsIndex -->
<!-- - Must implement health_check() and build_status() -->
<!-- - Must use dynamic helpers, not manual aggregation -->
```

**Result:** Implementer guesses, gets it wrong

---

## ✅ The Standard - Sibling Component Pattern Compliance

### Step 1: Identify Component Level

Before designing, identify where your component sits in the architecture.

**Common Architectural Levels:**
- **Orchestrator**: Top-level managers (e.g., IndexManager, WorkflowEngine)
- **Index Container**: High-level indexes (e.g., StandardsIndex, CodeIndex, ASTIndex)
- **Partition**: Multi-repo containers (e.g., CodePartition)
- **Sub-Index**: Specialized indexes (e.g., SemanticIndex, GraphIndex)
- **Component**: Lowest-level pieces (e.g., VectorComponent, FTSComponent)

**How to identify:**
```python
# Ask: "What other components have similar responsibilities?"
# - StandardsIndex indexes standards docs
# - CodeIndex indexes code
# - ASTIndex indexes syntax trees
# → All are "Index Containers" (same level)
#
# - CodePartition manages one repository
# → Siblings would be other partition-like containers
```

### Step 2: Query for Sibling Components

**Mandatory queries BEFORE designing:**

```python
# Query 1: Find components at same level
pos_search_project(
    content_type="standards",
    query="[your component type] architecture implementation pattern"
)
# Example: "index container architecture implementation pattern"

# Query 2: Search code for sibling implementations
pos_search_project(
    action="search_code",
    query="[sibling name] __init__ health_check build_status"
)
# Example: "StandardsIndex __init__ health_check build_status"

# Query 3: Find architectural patterns
pos_search_project(
    content_type="standards", 
    query="fractal pattern ComponentDescriptor dynamic helpers"
)
```

### Step 3: Read Sibling Implementations

**REQUIRED: Read actual code of sibling components**

```python
# Read at minimum:
# 1. __init__() - How siblings initialize
# 2. Key methods - What methods exist, their signatures
# 3. Component registration - How ComponentDescriptor is used
# 4. Aggregation logic - Manual vs helper functions

# Example:
read_file("ouroboros/subsystems/rag/standards/container.py")
read_file("ouroboros/subsystems/rag/code/container.py")

# Study:
# - Do they use self.components registry?
# - Do they use dynamic_health_check()?
# - Do they use dynamic_build_status()?
# - What's their method signature consistency?
```

### Step 4: Document Pattern Compliance in Spec

**REQUIRED: Spec must have "Pattern Compliance" section**

```markdown
## Pattern Compliance

CodePartition must follow the same ComponentDescriptor/fractal pattern as 
StandardsIndex and CodeIndex.

**Required Patterns:**
1. **Component Registry**: Use self.components: Dict[str, ComponentDescriptor]
2. **Health Check**: Use dynamic_health_check(self.components)
3. **Build Status**: Use dynamic_build_status(self.components)  
4. **Component Registration**: Register sub-indexes in __init__() with callbacks
5. **Method Signatures**: Match StandardsIndex/CodeIndex signatures exactly

**Rationale:**
- Consistency across all index containers
- Reuse proven fractal aggregation logic
- Avoid manual aggregation bugs
- Enable dynamic component discovery

**Verification:**
- [ ] __init__() creates self.components registry
- [ ] Semantic and graph sub-indexes registered as ComponentDescriptors
- [ ] health_check() delegates to dynamic_health_check()
- [ ] build_status() delegates to dynamic_build_status()
```

### Step 5: Add Pattern Verification Tasks

**REQUIRED: Tasks must verify pattern compliance**

```markdown
### Task 3.2: Implement ComponentDescriptor Registry

**File**: ouroboros/subsystems/rag/code/partition.py

**Description**: Create self.components registry matching StandardsIndex pattern

**Pattern Reference**: 
See StandardsIndex.components (lines 105-128 in standards/container.py)

**Acceptance Criteria**:
- [ ] self.components: Dict[str, ComponentDescriptor] created in __init__()
- [ ] Semantic sub-index registered with health_check and build_status_check callbacks
- [ ] Graph sub-index registered with health_check and build_status_check callbacks
- [ ] Pattern matches StandardsIndex/CodeIndex exactly
- [ ] Unit test verifies component registration

### Task 3.3: Implement health_check() Using Fractal Pattern

**File**: ouroboros/subsystems/rag/code/partition.py

**Description**: Implement health_check() using dynamic_health_check()

**Pattern Reference**:
See StandardsIndex.health_check() (line 595 in standards/container.py)

**Acceptance Criteria**:
- [ ] Method signature: def health_check(self) -> HealthStatus
- [ ] Implementation: return dynamic_health_check(self.components)
- [ ] Pattern matches siblings exactly (no manual aggregation)
- [ ] Integration test verifies fractal aggregation
```

### Step 6: Verify During Implementation

**Implementation checklist:**

```python
# Before writing code:
✓ Read sibling implementations
✓ Understand their structure
✓ Know which patterns to follow

# While writing code:
✓ Match method signatures exactly
✓ Use same helpers (dynamic_health_check, etc.)
✓ Follow same initialization pattern
✓ Register components same way

# After writing code:
✓ Compare side-by-side with sibling
✓ Verify pattern compliance
✓ Test that behavior matches siblings
```

---

## ✅ Compliance Checklist

### Design Phase
- [ ] Identified component's architectural level
- [ ] Queried for sibling components
- [ ] Read sibling implementations (at least 2)
- [ ] Documented common patterns found
- [ ] Spec includes "Pattern Compliance" section
- [ ] Spec explicitly lists patterns to follow
- [ ] Spec explains rationale for each pattern

### Specification Phase
- [ ] Spec references sibling implementations by file/line
- [ ] Tasks include pattern verification steps
- [ ] Acceptance criteria mention pattern matching
- [ ] Examples show sibling pattern usage
- [ ] Anti-patterns warn against deviations

### Implementation Phase
- [ ] Followed patterns exactly as specified
- [ ] Method signatures match siblings
- [ ] Helpers used (not manual aggregation)
- [ ] Component registry structure matches
- [ ] Side-by-side comparison done

### Validation Phase
- [ ] Unit tests verify pattern compliance
- [ ] Integration tests compare behavior to siblings
- [ ] Code review checks pattern matching
- [ ] Documentation notes pattern compliance

---

## 📝 Examples

### Example 1: Adding CodePartition (Should Have Done This)

**Context:** Creating CodePartition to manage multi-repo code partitions

**Step 1: Identify Level**
```
CodePartition manages indexes for one repository
→ Similar to: StandardsIndex (manages standards), CodeIndex (manages code)
→ Level: "Index Container"
→ Siblings: StandardsIndex, CodeIndex
```

**Step 2: Query for Siblings**
```python
pos_search_project(
    content_type="standards",
    query="StandardsIndex CodeIndex architecture component registry"
)

pos_search_project(
    action="search_code",
    query="StandardsIndex health_check build_status components"
)
```

**Step 3: Read Siblings**
```python
read_file("ouroboros/subsystems/rag/standards/container.py")
# Lines 105-128: Component registry setup
# Line 595: health_check() uses dynamic_health_check()
# Line 613: build_status() uses dynamic_build_status()

read_file("ouroboros/subsystems/rag/code/container.py")
# Same pattern!
```

**Step 4: Document in Spec**
```markdown
## Pattern Compliance

CodePartition follows the ComponentDescriptor/fractal pattern used by
StandardsIndex and CodeIndex.

**Required:**
1. self.components registry
2. dynamic_health_check() for aggregation
3. dynamic_build_status() for build status

**Files to reference:**
- standards/container.py:105-128 (component registration)
- standards/container.py:595 (health_check pattern)
- standards/container.py:613 (build_status pattern)
```

**Step 5: Add Task**
```markdown
### Task 2.1: Implement ComponentDescriptor Registry

Pattern reference: standards/container.py:105-128

Acceptance criteria:
- [ ] self.components created in __init__()
- [ ] Semantic registered with callbacks
- [ ] Graph registered with callbacks
- [ ] Pattern matches StandardsIndex exactly
```

**Result:** CodePartition would have been implemented correctly from the start

### Example 2: Adding New Workflow Subsystem

**Context:** Creating PaymentWorkflow alongside existing workflows

**Step 1: Identify Level**
```
PaymentWorkflow executes payment processing steps
→ Similar to: SpecCreationWorkflow, SpecExecutionWorkflow
→ Level: "Workflow Engine"
→ Siblings: SpecCreationWorkflow, SpecExecutionWorkflow
```

**Step 2: Study Siblings**
```python
# Both siblings use:
# - Phase-based execution
# - State persistence
# - Evidence validation
# - Checkpoint system

# Pattern found: All workflows extend BaseWorkflow
# and implement execute_phase()
```

**Step 3: Spec Pattern Compliance**
```markdown
## Pattern Compliance

PaymentWorkflow must follow the phase-based execution pattern used by
all existing workflows.

**Required Patterns:**
1. Extend BaseWorkflow
2. Implement execute_phase(phase_number)
3. Use checkpoint system for state
4. Validate evidence at phase gates
5. Support pause/resume
```

**Result:** New workflow integrates seamlessly

---

## 🚫 Anti-Patterns

### Anti-Pattern 1: Spec Doesn't Mention Pattern Compliance

**❌ Bad:**
```markdown
# Multi-Repo Code Intelligence Spec

## CodePartition
- Manages one repository
- Has semantic and graph sub-indexes
- Provides search interface

<!-- No mention of patterns! -->
```

**✅ Good:**
```markdown
## CodePartition - Pattern Compliance

CodePartition must follow the ComponentDescriptor pattern used by
StandardsIndex and CodeIndex.

**Required:**
- self.components: Dict[str, ComponentDescriptor]
- health_check() uses dynamic_health_check(self.components)
- build_status() uses dynamic_build_status(self.components)

**Reference:**
See standards/container.py:595, 613 for pattern
```

### Anti-Pattern 2: Manual Aggregation When Siblings Use Helpers

**❌ Bad:**
```python
# Siblings use dynamic helper:
class StandardsIndex:
    def health_check(self):
        return dynamic_health_check(self.components)

# New component does manual (inconsistent):
class CodePartition:
    def health_check(self):
        all_healthy = True
        for component in [self.semantic, self.graph]:
            if component and not component.health_check().healthy:
                all_healthy = False
        # ... more manual logic
```

**✅ Good:**
```python
# Matches sibling pattern:
class CodePartition:
    def health_check(self):
        return dynamic_health_check(self.components)
```

### Anti-Pattern 3: Different Method Signatures

**❌ Bad:**
```python
# Siblings:
def health_check(self) -> HealthStatus: ...
def build_status(self) -> BuildStatus: ...

# New component (incompatible signatures):
def health_check(self, include_details=False) -> Dict: ...  # ❌ Wrong!
def get_build_status(self) -> str: ...  # ❌ Wrong name & return type!
```

**✅ Good:**
```python
# Exact match:
def health_check(self) -> HealthStatus: ...
def build_status(self) -> BuildStatus: ...
```

### Anti-Pattern 4: Guessing Instead of Reading Code

**❌ Bad Process:**
```
1. Read README about StandardsIndex
2. Guess how it works
3. Implement CodePartition from guess
```

**✅ Good Process:**
```
1. Read actual StandardsIndex implementation
2. Read actual CodeIndex implementation  
3. Document patterns found
4. Implement CodePartition matching patterns
```

---

## 🔍 When to Query This Standard

| Situation | Query |
|-----------|-------|
| **Creating component in existing subsystem** | `pos_search_project(content_type="standards", query="sibling component pattern compliance")` |
| **Extending index system** | `pos_search_project(content_type="standards", query="index container architectural patterns")` |
| **Adding new partition type** | `pos_search_project(content_type="standards", query="partition pattern compliance requirements")` |
| **Spec review** | `pos_search_project(content_type="standards", query="pattern compliance section checklist")` |
| **Implementation review** | `pos_search_project(content_type="standards", query="verify sibling pattern matching")` |

---

## 🔗 Related Standards

**Architecture:**
- `cascading-health-check-architecture` - Fractal pattern details
- `resilient-index-building` - Build status fractal pattern
- `component-helpers` - dynamic_health_check, dynamic_build_status

**Process:**
- `standards-creation-process` - How to write standards
- `rag-content-authoring` - Making content discoverable
- `praxis-os-development-process` - Overall development workflow

**Anti-Patterns:**
- `production-code-checklist` - Quality standards
- `code-review-checklist` - What to look for in reviews

---

## 📊 Metrics

**How to measure compliance:**

```python
# Metric 1: Pattern match percentage
pattern_elements = [
    "has_components_registry",
    "uses_dynamic_health_check", 
    "uses_dynamic_build_status",
    "matches_method_signatures",
    "has_component_registration"
]
compliance = (elements_present / total_elements) * 100

# Target: 100% for all sibling components

# Metric 2: Architectural drift
drift_indicators = [
    "manual_aggregation_instead_of_helper",
    "different_method_signature",
    "missing_expected_method",
    "different_init_pattern"
]
drift_score = sum(drift_indicators)

# Target: 0 drift indicators
```

---

## 🎓 Lessons Learned

### Case Study: CodePartition Implementation Gap

**Date:** 2025-11-12  
**Context:** Multi-repo code intelligence spec

**What Happened:**
1. Nov 8: Cascading health check fractal pattern established
2. Nov 12: Multi-repo spec created CodePartition
3. Spec said "4-level fractal health checks" in README
4. But spec never detailed CodePartition pattern compliance
5. Implementation guessed, used manual aggregation
6. Missing build_status() entirely
7. Nov 14: Resilient index building added build_status
8. Assumed all components followed pattern
9. CodePartition still broken
10. Nov 15: MCP server crashes on startup

**Root Cause:**
- Spec didn't require studying StandardsIndex/CodeIndex
- No "Pattern Compliance" section in spec
- No tasks verifying pattern matching
- Implementer had no guidance

**Prevention:**
This standard. Mandatory sibling analysis before design.

**Cost:**
- 4 days of broken multi-repo functionality
- Wasted time debugging crashes
- Technical debt accumulated

---

**Version:** 1.0.0  
**Created:** 2025-11-15  
**Last Updated:** 2025-11-15  
**Next Review:** After 3 more subsystem extensions OR when pattern violations detected

