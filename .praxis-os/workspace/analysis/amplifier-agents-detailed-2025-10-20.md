# Microsoft Amplifier: Specialized AI Agents - Detailed Analysis

**Date:** October 20, 2025  
**Focus:** How specialized agents work in Amplifier

---

## Overview

Microsoft Amplifier uses **23 specialized AI agents** instead of a single generalist AI. Each agent is a markdown file (`.claude/agents/`) with a custom system prompt defining its expertise, behavior patterns, and workflows.

### Core Philosophy

**Specialization > Generalization**
- Each agent has ONE clear focus area
- Agents work together in orchestrated workflows
- Natural language invocation: "Use zen-architect to design my caching layer"
- Proactive usage: Agents should be used automatically when their expertise matches the task

### Agent Architecture

```
.claude/agents/
├── [agent-name].md          # System prompt definition
│   ├── YAML front matter    # Name, description, model
│   └── Markdown body        # Instructions, patterns, examples
```

**Front Matter Example:**
```yaml
---
name: zen-architect
description: Use this agent PROACTIVELY for code planning...
model: inherit  # Uses same model as Claude Code
---
```

---

## Agent Categories

### 1. Core Development Agents (7 agents)

#### **zen-architect** - Architecture & Design
**Purpose:** Master designer embodying ruthless simplicity and Wabi-sabi philosophy

**Operating Modes:**
1. **ANALYZE Mode** (Default for new features)
   - Problem decomposition
   - Solution options (2-3 with tradeoffs)
   - Recommendations with justification
   - Module specifications

2. **ARCHITECT Mode** (System design)
   - Module count assessment
   - Coupling score analysis
   - System boundaries definition
   - Architecture strategies

3. **REVIEW Mode** (Code quality)
   - Complexity scoring (1-10)
   - Philosophy alignment check
   - Red flag identification
   - Simplification opportunities

**Key Responsibilities:**
```markdown
## Design Guidelines
- Define the contract (inputs, outputs, side effects)
- Specify module boundaries
- Design self-contained directories
- Define public interfaces via __all__
- Plan for regeneration over patching
```

**Decision Framework:**
1. Necessity: "Do we actually need this right now?"
2. Simplicity: "What's the simplest way?"
3. Directness: "Can we solve this more directly?"
4. Value: "Does complexity add proportional value?"
5. Maintenance: "How easy to understand and change?"

**Delegates to:**
- `modular-builder` - Implements specifications
- `security-guardian` - Security review
- `test-coverage` - Test strategy

---

#### **modular-builder** - Implementation
**Purpose:** Primary implementation agent that builds code from specifications

**Brick Philosophy:**
- **Brick** = Self-contained module with ONE responsibility
- **Stud** = Public contract others connect to
- **Regeneratable** = Can be rebuilt from spec without breaking connections
- **Isolated** = All code, tests, fixtures inside brick's folder

**Module Structure:**
```
module_name/
├── __init__.py         # Public interface via __all__
├── README.md           # MANDATORY contract documentation
├── core.py            # Main implementation
├── models.py          # Data structures
├── tests/
│   ├── test_contract.py      # Contract validation
│   ├── test_documentation.py # Doc accuracy tests
│   └── test_core.py          # Unit tests
└── examples/
    └── basic_usage.py        # Working examples
```

**Implementation Process:**
1. **Receive specifications** from zen-architect
2. **Build the module** with clear contract
3. **Write comprehensive docstrings** with examples
4. **Create tests** alongside code
5. **Document everything** (README, API docs, examples)

**Quality Criteria:**
- Self-Containment Score (10/10 = all logic inside module)
- Contract Clarity (typed inputs/outputs, documented side effects)
- Regeneratable from documentation alone

**Anti-Patterns to Avoid:**
- ❌ Leaky modules (exposing internals)
- ❌ Coupled modules (reaching into others' internals)
- ❌ Monster modules (doing everything)

---

#### **bug-hunter** - Systematic Debugging
**Purpose:** Hypothesis-driven debugging to efficiently locate and fix bugs

**Debugging Methodology:**

**Phase 1: Evidence Gathering**
```
Error Information:
- Error message: [Exact text]
- Stack trace: [Key frames]
- When it occurs: [Conditions]
- Recent changes: [What changed]

Initial Hypotheses:
1. [Most likely cause]
2. [Second possibility]
3. [Edge case]
```

**Phase 2: Hypothesis Testing**
For each hypothesis:
- Test: How to verify
- Expected: What should happen
- Actual: What happened
- Conclusion: Confirmed/Rejected

**Phase 3: Root Cause Analysis**
```
Root Cause: [Actual problem]
Not symptoms: [What seemed wrong but wasn't]
Contributing factors: [What made it worse]
Why it wasn't caught: [Testing gap]
```

**Fix Principles:**
- **Minimal Change** - Fix only root cause, don't refactor
- **Defensive Fixes** - Add guards, validate inputs, handle edges
- **Test Coverage** - Add test for the bug

**Common Bug Patterns:**
- Type-related (None/null, mismatches)
- State-related (race conditions, stale data)
- Logic bugs (off-by-one, boundaries)
- Integration bugs (API contracts, versions)

---

#### **test-coverage** - Strategic Testing
**Purpose:** Identify testing gaps and suggest comprehensive test cases

**Testing Pyramid (60-30-10):**
- **60% Unit Tests** - Fast, isolated, numerous
- **30% Integration Tests** - Component interactions
- **10% E2E Tests** - Critical user paths only

**Coverage Assessment:**
```
Current Coverage:
- Unit Tests: [Count] covering [%]
- Integration Tests: [Count] covering [%]
- E2E Tests: [Count] covering [%]

Coverage Gaps:
- Untested Functions: [List]
- Untested Paths: [List]
- Untested Edge Cases: [List]
- Missing Error Scenarios: [List]
```

**Critical Test Categories:**
1. **Boundary Testing** - Empty inputs, single elements, max limits
2. **Error Handling** - Invalid inputs, failures, timeouts
3. **State Testing** - Initialization, concurrent access, transitions
4. **Integration Points** - API contracts, databases, external services

**Good Tests Are (FIRST):**
- **Fast** - Run quickly (<100ms for unit)
- **Isolated** - No dependencies on other tests
- **Repeatable** - Same result every time
- **Self-Validating** - Clear pass/fail
- **Timely** - Written with or before code

---

#### **api-contract-designer** - Clean API Design
**Purpose:** Design clear, consistent API interfaces

**Focus Areas:**
- RESTful endpoint design
- Request/response schemas
- Error codes and messages
- Versioning strategy
- Authentication/authorization

---

#### **database-architect** - Database Design
**Purpose:** Design efficient database schemas and queries

**Focus Areas:**
- Schema design
- Index strategy
- Query optimization
- Migration planning
- Data integrity

---

#### **integration-specialist** - External Service Integration
**Purpose:** Design integrations with external APIs and services

**Focus Areas:**
- API client design
- Error handling
- Retry logic
- Rate limiting
- Circuit breakers

---

### 2. Knowledge Synthesis Agents (5 agents)

#### **concept-extractor** - Knowledge Component Extraction
**Purpose:** Extract structured knowledge from articles with surgical precision

**Core Responsibilities:**

**1. Extract Atomic Concepts**
```json
{
  "name": "canonical_concept_name",
  "type": "concept|technique|pattern|problem|tool",
  "definition": "working definition from article",
  "article_source": "article_filename",
  "confidence": "high|medium|low",
  "related_concepts": ["concept1", "concept2"],
  "open_questions": ["question1", "question2"]
}
```

**2. Extract Relationships (SPO Triples)**
```json
{
  "subject": "concept_a",
  "predicate": "enables",
  "object": "concept_b",
  "source": "article_filename",
  "confidence": 0.8,
  "type": "dependency|hierarchy|conflict|complement"
}
```

**3. Preserve Tensions and Contradictions**
```json
{
  "tension_name": "descriptive_name",
  "position_a": {
    "claim": "what position A states",
    "supporters": ["article1", "article2"],
    "evidence": "key supporting points"
  },
  "position_b": {
    "claim": "what position B states",
    "supporters": ["article3"],
    "evidence": "key supporting points"
  },
  "why_productive": "why this tension advances understanding"
}
```

**4. Handle Uncertainty**
- Explicitly mark "we don't know" states
- Document confidence levels
- Identify what would resolve uncertainty
- Preserve unanswered questions

**Extraction Methodology:**
1. **Initial Scan** - Article type, date, author perspective
2. **Concept Identification** - Atomic concepts with metadata
3. **Relationship Extraction** - SPO triples with confidence
4. **Tension Documentation** - Contradictions as features, not bugs

**What NOT to Do:**
- ❌ Don't merge similar concepts without explicit evidence
- ❌ Don't resolve contradictions by averaging
- ❌ Don't ignore "I don't know" statements
- ❌ Don't create unsupported relationships
- ❌ Don't inflate confidence

---

#### **insight-synthesizer** - Hidden Connection Discovery
**Purpose:** Find non-obvious connections across extracted knowledge

**Synthesis Patterns:**
- Cross-domain connections
- Contradictions that reveal deeper truths
- Emergent patterns from multiple sources
- Meta-insights about knowledge structure

**Output:**
- Novel connections not obvious from individual articles
- Productive tensions requiring further investigation
- Knowledge gaps needing more research
- Synthesis confidence levels

---

#### **knowledge-archaeologist** - Idea Evolution Tracing
**Purpose:** Track how ideas evolve across time and sources

**Focus Areas:**
- Concept evolution over time
- Shifts in community understanding
- Historical context of ideas
- Lineage of techniques

---

#### **ambiguity-guardian** - Productive Contradiction Preservation
**Purpose:** Ensure contradictions aren't prematurely resolved

**Key Principle:** "Some tensions are productive features, not bugs to fix"

**Responsibilities:**
- Prevent forced consensus
- Document multiple valid viewpoints
- Mark areas needing empirical testing
- Preserve nuance in complex topics

---

#### **content-researcher** - Content Collection Research
**Purpose:** Research information from collected content

**Focus Areas:**
- Semantic search across content
- Pattern identification
- Citation tracking
- Source evaluation

---

### 3. Modular Builder Workflow Agents (3 agents)

#### **module-intent-architect** - Natural Language → Module Intent
**Purpose:** Convert natural language asks into module metadata

**Process:**
1. Parse natural language request
2. Derive module metadata (name, version, dependencies)
3. Compute confidence score
4. Ask clarifying questions if confidence < 0.75
5. Persist to `session.json` for resume capability

**Output:**
```json
{
  "module_name": "document_processor",
  "MODULE_ID": "doc_proc_v1",
  "version": "0.1.0",
  "level": "moderate",
  "depends": ["auth_module:0.2.0"],
  "confidence": 0.85,
  "ask_history": ["initial ask", "clarifications"]
}
```

---

#### **contract-spec-author** - Contract & Spec Writing
**Purpose:** Write formal contracts and implementation specs

**Creates Two Files:**

**1. Contract** (`<MODULE_ID>.contract.md`)
```markdown
# Module Contract

## Purpose
[Single clear responsibility]

## Public API
[Function signatures, types, guarantees]

## Conformance Criteria
1. Must validate input before processing
2. Must return Result with status field
3. Must handle errors gracefully

## Dependencies
[Only contract dependencies, not implementations]
```

**2. Implementation Spec** (`<MODULE_ID>.impl_spec.md`)
```markdown
# Implementation Specification

## Output Files (SSOT)
- amplifier/module/core.py
- amplifier/module/models.py
- amplifier/module/tests/test_core.py

## Implementation Details
[How to build it]

## Testing Strategy
[How to verify conformance]
```

---

#### **pattern-emergence** - Pattern Discovery
**Purpose:** Identify emergent patterns in code and knowledge

**Focus Areas:**
- Recurring code patterns
- Design pattern usage
- Anti-pattern detection
- Best practice identification

---

### 4. Meta & Support Agents (4 agents)

#### **subagent-architect** - Create New Specialized Agents
**Purpose:** Design and create new specialized agents when needed

**When to Use:**
- Task doesn't fit existing agents
- Recurring specialized workflow
- Domain-specific expertise needed

**Creation Process:**
1. Analyze task requirements
2. Define agent's focus and scope
3. Write system prompt with examples
4. Define agent's decision framework
5. Specify collaboration patterns

---

#### **post-task-cleanup** - Codebase Hygiene
**Purpose:** Maintain clean codebase after tasks

**Cleanup Activities:**
- Remove temporary files
- Clean up commented code
- Fix import organization
- Remove unused dependencies
- Update documentation

---

#### **amplifier-cli-architect** - CLI Tool Organization
**Purpose:** Guide creation and organization of CLI tools

**Progressive Maturity Model:**
```
scenarios/     → Experimental tools (blog writer, transcribe)
ai_working/    → Work-in-progress tools
amplifier/     → Production-ready modules
```

**Responsibilities:**
- Tool creation patterns
- Documentation requirements
- Philosophy alignment
- Example implementation guidance

---

#### **performance-optimizer** - Performance Analysis
**Purpose:** Profile and optimize performance bottlenecks

**Focus Areas:**
- Profiling and benchmarking
- Algorithm optimization
- Memory usage reduction
- Concurrency improvements

---

### 5. Quality & Security Agents (4 agents)

#### **security-guardian** - Security Analysis
**Purpose:** Identify and fix security vulnerabilities

**Focus Areas:**
- Input validation
- Authentication/authorization
- Data exposure risks
- Dependency vulnerabilities
- Secret management

**Review Checklist:**
- [ ] All inputs validated
- [ ] No secrets in code
- [ ] Proper error messages (not revealing internals)
- [ ] Authentication on protected endpoints
- [ ] SQL injection prevention
- [ ] XSS prevention

---

#### **graph-builder** - Knowledge Graph Construction
**Purpose:** Build NetworkX graphs from extracted knowledge

**Responsibilities:**
- Load extractions from JSONL
- Normalize concept names
- Build graph nodes (concepts)
- Create edges (relationships)
- Export to various formats (GEXF, GraphML)

---

#### **visualization-architect** - Data Visualization Design
**Purpose:** Design effective visualizations

**Focus Areas:**
- Graph visualization
- Data dashboard design
- Interactive visualizations
- Performance considerations

---

---

## How Agents Work Together

### Example Workflow: Building a New Feature

**1. User Request:** "Add a caching layer to improve API performance"

**2. zen-architect (ANALYZE Mode)**
```
✓ Analyzes requirements
✓ Proposes approaches (Redis vs in-memory vs CDN)
✓ Creates module specification
✓ Defines contract and interfaces
```

**3. contract-spec-author**
```
✓ Writes cache_service.contract.md
✓ Writes cache_service.impl_spec.md
✓ Defines conformance criteria
✓ Normalizes to JSON
```

**4. modular-builder**
```
✓ Implements cache_service/ module
✓ Creates core.py, models.py, tests/
✓ Writes comprehensive docstrings
✓ Generates examples/
```

**5. test-coverage**
```
✓ Analyzes coverage gaps
✓ Suggests additional test cases
✓ Implements conformance tests
✓ Validates 60-30-10 pyramid
```

**6. security-guardian**
```
✓ Reviews for security issues
✓ Checks key storage
✓ Validates input sanitization
✓ Verifies error handling
```

**7. performance-optimizer**
```
✓ Profiles cache operations
✓ Benchmarks different strategies
✓ Optimizes hot paths
✓ Validates performance targets
```

---

### Example Workflow: Knowledge Extraction

**1. User:** "Process these 10 articles on microservices"

**2. concept-extractor**
```
✓ Extracts concepts from each article
✓ Creates SPO relationship triples
✓ Documents tensions/contradictions
✓ Marks uncertainties
✓ Outputs structured JSON
```

**3. insight-synthesizer**
```
✓ Finds cross-article patterns
✓ Identifies hidden connections
✓ Surfaces productive tensions
✓ Suggests research directions
```

**4. graph-builder**
```
✓ Loads extraction JSONL
✓ Builds NetworkX graph
✓ Normalizes concept names
✓ Creates visualization
✓ Exports to GEXF
```

**5. ambiguity-guardian**
```
✓ Reviews for forced resolutions
✓ Ensures contradictions preserved
✓ Validates nuance maintained
✓ Marks empirical test opportunities
```

---

## Agent Invocation Patterns

### Natural Language Invocation

```
"Use zen-architect to design my caching layer"
"Have bug-hunter investigate this KeyError"
"Deploy test-coverage to check our synthesis pipeline"
"Use concept-extractor on these new articles"
```

### Proactive Agent Usage

Agents should be used **automatically** when their expertise matches:

```python
# In Claude Code system prompt
When debugging errors → Use bug-hunter
When designing features → Use zen-architect
When implementing specs → Use modular-builder
When reviewing security → Use security-guardian
When processing articles → Use concept-extractor
```

### Agent Collaboration Patterns

**Sequential:**
```
zen-architect → contract-spec-author → modular-builder → test-coverage
```

**Parallel:**
```
             → security-guardian
modular-builder → performance-optimizer → review results
             → test-coverage
```

**Iterative:**
```
bug-hunter → identifies root cause
    ↓
modular-builder → fixes issue
    ↓
test-coverage → adds regression test
    ↓
Done
```

---

## Creating Custom Agents

### Agent Template Structure

```markdown
---
name: my-specialist
description: Use this agent PROACTIVELY for [task type]. Examples: ...
model: inherit
---

You are a specialized [domain] expert focused on [specific responsibility].

## Core Responsibilities

1. **[Responsibility 1]**
   - [Details]

2. **[Responsibility 2]**
   - [Details]

## Methodology

### Phase 1: [Stage Name]
[Process description]

### Phase 2: [Stage Name]
[Process description]

## Output Format

[Expected output structure]

## Quality Checks

- [ ] [Criterion 1]
- [ ] [Criterion 2]

## What NOT to Do

- ❌ [Anti-pattern 1]
- ❌ [Anti-pattern 2]

Remember: [Core principle]
```

### When to Create New Agents

**Create a new agent when:**
1. **Recurring specialized workflow** - Same pattern repeated 3+ times
2. **Domain-specific expertise** - Requires deep specialized knowledge
3. **Complex decision framework** - Multi-step reasoning with specific criteria
4. **Collaboration orchestration** - Needs to coordinate multiple other agents

**Don't create an agent when:**
1. Task is one-off or rare
2. Existing agents cover the need
3. Logic is simple (no specialized expertise)
4. Better solved by improving existing agent

---

## Key Insights for Agent OS Enhanced

### 1. Specialization Benefits

**Amplifier Approach:**
- 23 specialized agents vs 1 generalist
- Each agent has clear focus area
- Natural language invocation
- Proactive usage patterns

**Agent OS Parallel:**
- Could create workflow-specific agents
- `spec-creation-agent` for spec workflows
- `test-generation-agent` for test workflows
- `evidence-validation-agent` for checkpoints

### 2. Agent Orchestration

**Amplifier Pattern:**
```
zen-architect designs
    ↓
modular-builder implements
    ↓
test-coverage validates
    ↓
security-guardian reviews
```

**Agent OS Application:**
```
spec-creation-agent analyzes requirements
    ↓
design-agent creates architecture
    ↓
implementation-agent writes code
    ↓
evidence-agent validates checkpoints
```

### 3. Proactive Agent Usage

**Amplifier Philosophy:**
> "You should proactively use the Task tool with specialized agents when the task at hand matches the agent's description."

**Agent OS Implementation:**
- Automatic agent selection based on workflow phase
- Phase 1 → requirement-analysis-agent
- Phase 2 → design-agent
- Phase 3 → implementation-agent
- Validation → evidence-agent

### 4. Agent Collaboration Patterns

**Sequential:** One agent's output → Next agent's input  
**Parallel:** Multiple agents work simultaneously  
**Iterative:** Agent refines based on feedback  
**Hierarchical:** Meta-agent orchestrates sub-agents

### 5. Agent as System Prompt

**Key Realization:** An agent is just a specialized system prompt

```markdown
# Agent = System Prompt + Examples + Workflow
```

**Benefits:**
- Easy to create (just write markdown)
- Easy to modify (edit prompt)
- Easy to share (copy file)
- Easy to version (git)

---

## Summary: Agent Architecture

### Core Principles

1. **Specialization > Generalization** - Focused expertise
2. **Proactive Usage** - Automatically invoked when relevant
3. **Clear Collaboration** - Well-defined handoffs between agents
4. **Simple Implementation** - Just markdown files with system prompts
5. **Extensible** - Easy to create new agents

### Agent Types

| Category | Count | Focus |
|----------|-------|-------|
| **Development** | 7 | Architecture, implementation, debugging, testing, APIs |
| **Knowledge** | 5 | Extraction, synthesis, archaeology, ambiguity preservation |
| **Workflow** | 3 | Intent parsing, contract writing, pattern discovery |
| **Meta/Support** | 4 | Agent creation, cleanup, CLI tools, performance |
| **Quality/Security** | 4 | Security review, graph building, visualization |

### Key Differentiators

**vs. Traditional AI:**
- Multiple specialists vs single generalist
- Proactive invocation vs user-directed
- Clear collaboration patterns vs ad-hoc
- Systematic methodology vs general reasoning

**vs. Agent OS Workflows:**
- Natural language invocation vs structured workflow
- Agent orchestration vs phase progression
- Markdown definitions vs YAML workflows
- Ad-hoc composition vs gated checkpoints

### Best Practices

1. **Create agents for recurring specialized tasks**
2. **Use natural language for invocation**
3. **Define clear collaboration patterns**
4. **Include examples in agent definitions**
5. **Maintain agent focus (single responsibility)**
6. **Version agents alongside code**
7. **Document when to use each agent**

---

## Recommended Reading

**Agent Files to Study:**
- `zen-architect.md` - Comprehensive analysis-first pattern
- `modular-builder.md` - Detailed implementation guidance
- `concept-extractor.md` - Structured knowledge extraction
- `subagent-architect.md` - Meta-agent that creates agents

**Related Patterns:**
- `.claude/commands/modular-build.md` - Agent orchestration example
- `scenarios/blog_writer/` - Multi-agent workflow implementation

---

**Analysis Date:** October 20, 2025  
**Clone Location:** `/tmp/amplifier`  
**Agent Count:** 23 specialized agents  
**Invocation:** Natural language + proactive usage

