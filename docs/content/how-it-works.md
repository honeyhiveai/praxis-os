---
sidebar_position: 2
---

# How It Works

Agent OS Enhanced changes how you work with AI - from prompting to orchestration. Here's the complete workflow pattern.

## The Human-AI Partnership Model

### Your Role: Orchestrator
- Design direction and decisions
- Review and approval
- Team coordination
- Quality validation

### AI's Role: Implementation Engine
- 100% code authorship
- Design documentation
- Test creation
- Artifact generation

**Key principle:** You guide through conversation, AI invokes tools automatically.

## Complete Workflow Pattern

### Phase 1: Design Discussion

**You initiate** (conversational):
```
"We need user authentication with JWT tokens"
```

**AI responds** (conversational):
```
Let me understand the requirements:
- Will this be for web, mobile, or both?
- Do you need social auth (Google, GitHub)?
- What's your session duration requirement?
- Any specific compliance needs (GDPR, HIPAA)?
```

**Back and forth discussion:**
- You clarify requirements
- AI asks questions
- You make decisions
- AI proposes approaches

**AI creates design doc:**
```
I'll document this design:
- Authentication architecture
- Token structure (access + refresh)
- Security considerations
- Database schema
- API endpoints
```

AI writes `design-doc.md` with your approved approach.

### Phase 2: Spec Creation (Tool Chain Activation)

**You trigger** (conversational):
```
"This design looks good. Create the full spec for implementation."
```

**AI invokes MCP tool automatically:**
```python
# AI makes this tool call (you don't see this)
start_workflow(
    workflow_type="spec_creation_v1",
    target_file="user_authentication"
)
```

**What happens:**
1. AI starts `spec_creation_v1` workflow
2. Executes Phase 0: Context gathering
3. Provides checkpoint evidence
4. Advances to Phase 1: Requirements
5. Executes Phase 1: SRD creation
6. Continues through all phases systematically

**Result:** Complete specification in `.agent-os/specs/2025-10-08-user-auth/`
- `README.md` - Executive summary
- `srd.md` - Business requirements
- `specs.md` - Technical design
- `tasks.md` - Implementation breakdown
- `implementation.md` - Detailed guidance

### Phase 3: Review & Refinement

**You review:**
```
"The spec looks good, but add rate limiting to the token endpoint
and use refresh token rotation for better security."
```

**AI updates:**
- Modifies `specs.md` with rate limiting design
- Adds refresh token rotation
- Updates security considerations
- Adjusts implementation tasks

**Iterate until approved.**

### Phase 4: Commit & Team Review

**You orchestrate:**
```
"Commit this spec for team review"
```

**AI executes:**
```bash
git add .agent-os/specs/2025-10-08-user-auth/
git commit -m "spec: user authentication with JWT"
git push
```

**Team reviews spec** in PR, provides feedback.

**If changes needed:**
```
"Update the spec: use Redis for session storage instead of PostgreSQL"
```

AI modifies spec, you commit updates.

**Once approved:**
```
"Spec approved, ready for implementation"
```

### Phase 5: Implementation (Tool Chain Activation)

**You trigger** (conversational):
```
"Implement the user authentication spec"
```

**AI invokes MCP tool automatically:**
```python
# AI makes this tool call (you don't see this)
start_workflow(
    workflow_type="spec_execution_v1",
    target_file="user_authentication"
)
```

**What happens:**
1. AI starts `spec_execution_v1` workflow
2. Phase 0: Reviews the spec
3. Phase 1: Creates structure, installs dependencies
4. Phase 2: Implements features (100% AI-authored code)
5. Phase 3: Writes comprehensive tests
6. Phase 4: Creates documentation
7. Phase 5: Quality validation

**Throughout implementation:**
- You review progress
- AI provides updates
- You catch issues: "This has a race condition"
- AI fixes immediately
- AI commits work systematically

### Phase 6: Review & Ship

**You validate:**
```
"Show me the authentication flow"
```

AI explains implementation, you test locally.

**If issues found:**
```
"The token refresh logic doesn't handle expired refresh tokens"
```

AI fixes, writes test, commits.

**When satisfied:**
```
"This is ready. Create PR for team review."
```

AI creates PR with:
- Implementation code
- Comprehensive tests
- Documentation
- Specification reference

## Tool Calls: The Hidden Mechanism

### You Never Call Tools Directly

❌ **Not this:**
```
"Use the mcp_agent-os-rag_start_workflow tool with spec_creation_v1"
```

✅ **This:**
```
"Create a spec for user authentication"
```

The AI automatically invokes the right tool.

### Available Tool Chains

#### 1. RAG Search (Automatic)

**When you ask:**
```
"How do I handle race conditions in async code?"
```

**AI invokes:**
```python
search_standards(
    query="race conditions async code",
    n_results=3
)
```

**You see:** AI's answer with context from standards.

#### 2. Spec Creation Workflow

**When you say:**
```
"Create a spec for [feature]"
```

**AI invokes:**
```python
start_workflow(
    workflow_type="spec_creation_v1",
    target_file="feature_name"
)
```

**You see:** AI systematically creates specification.

#### 3. Spec Execution Workflow

**When you say:**
```
"Implement the [feature] spec"
```

**AI invokes:**
```python
start_workflow(
    workflow_type="spec_execution_v1",
    target_file="feature_name"
)
```

**You see:** AI builds feature with tests and docs.

#### 4. Custom Workflow Creation

**When you say:**
```
"I need a workflow for API documentation generation"
```

**AI invokes:**
```python
create_workflow(
    name="api_documentation_v1",
    workflow_type="documentation",
    phases=["Analysis", "Generation", "Review"]
)
```

**You see:** Complete workflow structure created.

## Conversation Patterns

### Starting Work

**Good:**
```
"We need user authentication"
"Let's add caching to the API"
"Create a workflow for database migrations"
```

**Not:**
```
"Call start_workflow with spec_creation_v1"
"Use the RAG tool to search"
```

### Making Corrections

**Good:**
```
"This has a bug - the lock isn't released on error"
"Change this to use async/await instead"
"Add error handling for network timeouts"
```

**AI fixes immediately** with correct patterns from standards.

### Getting Information

**Good:**
```
"What are best practices for handling race conditions?"
"Show me the spec for user authentication"
"Where are we in the current workflow?"
```

**AI queries MCP automatically** to get relevant information.

### Workflow Progression

**Good:**
```
"Continue with the next phase"
"We're ready to implement"
"Show me what's left to complete"
```

**AI manages workflow state** and progresses appropriately.

## What You'll Notice

### 1. No Repeated Context

AI doesn't ask you for standards - it queries them:
```
You: "Handle this race condition"
AI: [Queries race-conditions.md via MCP]
AI: "I'll use a mutex lock with proper error handling..."
```

### 2. Systematic Execution

AI doesn't skip steps:
```
Phase 1 → Checkpoint → Phase 2 → Checkpoint → Phase 3
```
Can't skip phases (architecturally enforced).

### 3. Evidence-Based Progress

AI provides concrete evidence at checkpoints:
```
Phase 1 complete:
✓ SRD created (250 lines)
✓ Requirements documented (12 functional, 8 non-functional)
✓ Success criteria defined (5 metrics)
✓ Stakeholders identified (PM, Eng, Security)
```

### 4. 100% AI Authorship

You never write code:
```
You: "This is wrong"
AI: [Fixes code]
You: "Add error handling"
AI: [Adds error handling]
```

AI maintains complete authorship.

## Real Example: End-to-End

### Day 1: Design

**You:** "We need API rate limiting"

**AI:** "Let me understand the requirements..."
- [Discussion about algorithms, limits, storage]
- [AI proposes token bucket algorithm with Redis]

**You:** "Approved. Create the spec."

**AI:** [Invokes `spec_creation_v1` automatically]
- Creates comprehensive specification
- 4 phases, ~2 hours

**You:** "Add per-user override capability"

**AI:** [Updates spec with override design]

**You:** "Commit for team review"

**AI:** [Commits spec]

### Day 2: Team Review

**Team:** "Use sliding window instead of token bucket"

**You:** "Update the spec with sliding window"

**AI:** [Modifies spec, you commit]

**Team:** "Approved"

### Day 3-4: Implementation

**You:** "Implement the rate limiting spec"

**AI:** [Invokes `spec_execution_v1` automatically]
- Phase 0-1: Setup (~1 hour)
- Phase 2: Implementation (~6 hours)
  - Redis integration
  - Rate limit middleware
  - Per-user overrides
  - All with tests
- Phase 3: Testing (~2 hours)
- Phase 4: Documentation (~1 hour)

**You:** [Review progress, catch issues]

**AI:** [Fixes issues immediately]

**You:** "Create PR"

**AI:** [Creates PR with full implementation]

### Day 5: Ship

**Team:** Approves PR

**You:** "Merge to main"

**Result:** Production-ready rate limiting, 100% AI-authored

## Next Steps

- **[Installation](./installation)** - Set up Agent OS Enhanced
- **[Workflows](./workflows)** - Understand workflow details
- **[Architecture](./architecture)** - How tool calls work under the hood

