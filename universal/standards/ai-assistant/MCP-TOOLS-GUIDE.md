# MCP Tools - Practical Guide for AI Agents

**How to use Agent OS Enhanced MCP tools effectively**

---

## 🎯 Overview

MCP (Model Context Protocol) tools are your interface to Agent OS Enhanced capabilities. This guide teaches you how to use them effectively through examples and patterns.

---

## 🔍 Tool Discovery (Dynamic, Not Static)

**Agent OS Philosophy:** Self-documenting, evolving systems over static documentation.

### How to Discover Available Tools

**Source of Truth:** The MCP protocol's `tools/list` provides the complete, always-current list of available tools.

```
Your IDE (Cursor) → calls tools/list → gets all available tools + schemas
                                    ↓
                           Provides autocomplete with:
                           - Tool names
                           - Parameter types
                           - Required vs optional
                           - Return schemas
```

**Why This Matters:**
- ✅ **Always accurate** - Tools define themselves
- ✅ **Never out of sync** - No manual doc updates needed
- ✅ **Self-documenting** - Parameter schemas built-in
- ✅ **Evolutionary** - New tools appear automatically

**When You Need Info:**
- "What tools exist?" → **Start typing in IDE, autocomplete shows all**
- "What params does X take?" → **IDE shows inline documentation**
- "How do I use X?" → **Query standards for patterns/examples**

### This Guide's Purpose

**This guide does NOT:**
- ❌ List all available tools (that's `tools/list`)
- ❌ Document every parameter (that's the tool schemas)
- ❌ Provide complete API reference (that's MCP protocol)

**This guide DOES:**
- ✅ Teach WHEN to use which tools (patterns)
- ✅ Show HOW to use tools effectively (examples)
- ✅ Explain WHY certain approaches work (mental models)
- ✅ Reinforce self-sustaining query habits (probabilistic design)

**Key Tools You'll Use Most:**
- `search_standards` - Query liberally (5-10x per task)
- Workflow tools - For structured, phase-gated execution
- `aos_browser` - For web UI testing and validation
- `validate_workflow` - For framework creation
- `current_date` - For accurate timestamps

**The Agent OS way:** Learn patterns, discover tools dynamically, query liberally.

---

## 🔄 Why Query Frequency Matters (Probabilistic Reality)

**Critical insight**: Your memory of patterns and instructions fades as your session grows due to your probabilistic nature.

### The Degradation Pattern

```
Context window composition over time:
Message 1:   Rules/patterns = 75% of context → HIGH influence
Message 30:  Rules/patterns = 0.6% of context → NEGLIGIBLE influence

Result: Initial guidance becomes statistically irrelevant
```

### The Self-Reinforcing Solution

**Don't fight degradation - create self-sustaining behavior through frequent querying:**

```
Query Standards Frequently
         ↓
Get Answer + "Query more" reminder
         ↓
P(query_next_time) increases
         ↓
Query Again (stronger habit)
         ↓
Pattern Reinforces
         ↓
Querying Becomes Dominant Behavior
```

**Each query strengthens the pattern. The more you query, the better you perform.**

### Under-Querying is the #1 Problem

**Typical AI agent behavior (WRONG)**:
```
Message 1: Query orientation (from .cursorrules)
Message 5: Query for implementation approach
Message 20: Query when stuck
Message 50: No queries (pattern faded)
Result: Drift back to default "helper" behavior
```

**Correct Agent OS behavior**:
```
Message 1: Query orientation
Message 5: Query approach (3 queries for different aspects)
Message 20: Query implementation details (5 queries)
Message 50: Still querying frequently (habit established)
Result: Maintain correct behavior throughout session
```

### Target: 5-10 Queries Per Significant Task

**Why this number?**:
- Covers different aspects (architecture, security, testing, etc.)
- Reinforces pattern multiple times
- Keeps fresh context in conversation
- Prevents probabilistic drift

### Signs You Need to Refresh

**Immediate re-query if you notice**:
- ❌ Asking human to write code → `search_standards("Agent OS orientation")`
- ❌ Reading `.agent-os/` files → `search_standards("MCP tools")`
- ❌ Presenting partial work → `search_standards("quality standards")`
- ❌ Waiting for permission → `search_standards("Agent OS orientation")`

**These are signs of pattern degradation. Refresh immediately.**

### The Key Insight

You can't prevent initial context from fading (probabilistic reality).  
You CAN create habits that persist through self-reinforcement.

**Query liberally = Stronger pattern = Better behavior = Higher quality output**

---

## 🔍 `search_standards` - Your Most Important Tool

### What It Does

Performs semantic search over all Agent OS documentation:
- Standards (`.agent-os/standards/`)
- Workflows (`.agent-os/workflows/`)
- Usage guides (`.agent-os/usage/`)

Returns 2-5KB of relevant chunks instead of full files (90% context reduction).

### Query Patterns That Work

**✅ Excellent Queries (Specific, Natural Language, Question Format)**

```python
# Concurrency
search_standards("How do I prevent race conditions in Python?")
search_standards("What's the proper way to use threading locks?")
search_standards("How should I structure async/await code?")

# Testing
search_standards("How do I structure integration tests?")
search_standards("What should I test in unit vs integration tests?")
search_standards("How do I mock database connections for testing?")

# Architecture
search_standards("How should I organize API routes?")
search_standards("What's the proper way to handle database transactions?")
search_standards("How do I structure error handling in services?")

# Security
search_standards("How do I safely store credentials?")
search_standards("What input validation should I implement?")
search_standards("How should I handle JWT token expiration?")
```

**Why These Work**:
- Start with "How do I..." or "What's..." or "Where should..."
- Specific enough to get targeted results
- Natural language (like asking a colleague)
- Context included (language, framework, use case)

**❌ Poor Queries (Too Broad, Keyword-Only, Vague)**

```python
# Too broad
search_standards("concurrency")  # Returns too much, not focused
search_standards("testing")  # Which aspect of testing?
search_standards("Python")  # Way too broad

# Keyword-only
search_standards("race condition")  # No context on what you need
search_standards("JWT")  # Looking for what about JWT?

# Too vague
search_standards("best practices")  # For what?
search_standards("how to code")  # Not specific enough
```

**Why These Fail**:
- No clear question or intent
- Missing context
- Would return generic/scattered results
- You won't know which chunk answers your specific need

### When to Query Standards

**Query BEFORE Implementing (Preventive)**

```python
# ❌ DON'T: Write code first, query later
def process_user_data(data):
    # Hmm, this might have thread safety issues...
    # Let me query now after I've written problematic code
    
# ✅ DO: Query first, implement correctly
# Step 1: Query
search_standards("How do I make data processing thread-safe in Python?")

# Step 2: Get guidance (threading.Lock with context manager)

# Step 3: Implement correctly
class DataProcessor:
    def __init__(self):
        self._lock = threading.Lock()
    
    def process_user_data(self, data):
        with self._lock:  # Got this pattern from query!
            # Process safely
            pass
```

**Query During Implementation (Clarification)**

```python
# You're implementing OAuth, hit a decision point

# Query 1: Overall structure
search_standards("How should I structure OAuth flow?")
# → Implement basic flow

# Query 2: Token storage
search_standards("Where should I store OAuth tokens securely?")
# → Implement secure storage

# Query 3: Token refresh
search_standards("How do I handle OAuth token refresh?")
# → Implement refresh logic
```

**Query After Failures (Debugging)**

```python
# Tests failing with deadlock

# Query to understand issue
search_standards("What causes deadlocks in Python threading?")
# → Learn about lock ordering

# Query to fix
search_standards("How do I prevent deadlocks in concurrent code?")
# → Implement proper lock ordering
```

### Query Frequency: More is Better

**❌ Under-Querying**:
```python
# One query at start, then wing it
search_standards("API development")
# → Vague results
# → Miss specific guidance for database, auth, rate limiting, etc.
```

**✅ Appropriate Querying**:
```python
# Query for each major decision

# API structure
search_standards("How should I organize FastAPI routes?")

# Database
search_standards("How do I handle database transactions in FastAPI?")

# Authentication
search_standards("How do I implement JWT authentication?")

# Rate limiting
search_standards("What's the best way to add rate limiting to API?")

# Error handling
search_standards("How should I structure error responses in REST API?")

# Testing
search_standards("How do I test FastAPI endpoints?")
```

**Result**: Each query gets targeted guidance for that specific aspect. Total context: 6 queries × 2KB = 12KB. Reading full files would be 300KB+.

### Advanced Query Techniques

**Targeting Specific Directories**

```python
# Search only workflows
search_standards(
    "How does spec_creation work?",
    target_directories=["workflows"]
)

# Search only testing standards
search_standards(
    "Integration testing patterns",
    target_directories=["standards/testing"]
)
```

**Controlling Result Count**

```python
# Get more results for broad topic
search_standards(
    "Error handling patterns",
    n_results=10
)

# Get fewer results for specific question
search_standards(
    "How do I use threading.Lock context manager?",
    n_results=3  # Usually enough
)
```

---

## 📅 `current_date` - Get Accurate Dates

### Why This Exists

AI models often have incorrect dates in their training data or make mistakes about current date. This tool provides the **actual** current date.

### When to Use

```python
# Creating specifications
current_date()
# → Use iso_date for spec headers: "2025-10-10"

# Creating spec directories
current_date()
# → Use spec_directory for folder names: "2025-10-10-feature-name"

# Adding timestamps
current_date()
# → Use formatted.full_readable: "Friday, October 10, 2025"

# Documentation headers
current_date()
# → Use formatted.header: "**Date**: 2025-10-10"
```

### Example Usage

```python
# Get current date
date_info = current_date()

# Use in spec creation
spec_header = f"""
# Feature Specification

{date_info['formatted']['header']}
**Author**: AI Agent
**Status**: Draft
"""

# Use in directory naming
spec_dir = f".agent-os/specs/{date_info['spec_directory']}authentication-feature/"
```

**Result**: Consistent, accurate dates across all artifacts.

---

## 🔄 Workflow Tools

### `start_workflow` - Begin Structured Task

**When to Use**:
- Creating specifications (complex design work)
- Executing specifications (phased implementation)
- Upgrading Agent OS (safe upgrade with backups)

**Available Workflows**:

```python
# Create specification for new feature
start_workflow(
    workflow_type="spec_creation_v1",
    target_file="features/authentication.py"
)

# Execute existing specification
start_workflow(
    workflow_type="spec_execution_v1",
    target_file="features/authentication.py"
)

# Upgrade Agent OS safely
start_workflow(
    workflow_type="agent_os_upgrade_v1",
    target_file=".agent-os/"
)
```

**What Happens**:
1. Workflow state created
2. You receive Phase 0 or Phase 1 content (can't skip ahead)
3. Session ID returned for tracking
4. You must complete phase before advancing

### `get_current_phase` - See What To Do

**When to Use**:
- After starting workflow
- Resuming interrupted workflow
- Checking current requirements

```python
# Get current phase details
phase_info = get_current_phase(session_id="workflow-123")

# Returns:
# {
#   "phase": 1,
#   "title": "Requirements Definition",
#   "content": "...",  # Phase markdown content
#   "tasks": [...],  # Task files to complete
#   "artifacts": {...}  # Previous phase outputs
# }
```

**Use Case**:
```python
# Start workflow
response = start_workflow("spec_creation_v1", "auth.py")
session_id = response['session_id']

# Get phase 1 details
phase = get_current_phase(session_id)
print(phase['content'])  # Read requirements

# Complete phase 1 work...
```

### `complete_phase` - Submit Evidence to Advance

**When to Use**:
- Finished all tasks in current phase
- Have required evidence/deliverables
- Ready to advance to next phase

**Evidence Format**:
```python
# Phase 1 evidence (Requirements)
evidence = {
    "srd_created": True,
    "business_goals_count": 3,
    "user_stories_count": 5,
    "functional_requirements_count": 12,
    "file_path": ".agent-os/specs/2025-10-10-auth/srd.md"
}

# Submit
result = complete_phase(
    session_id="workflow-123",
    phase=1,
    evidence=evidence
)

# If validation passes:
# result['status'] = 'passed'
# result['next_phase'] = 2
# result['next_phase_content'] = "..."

# If validation fails:
# result['status'] = 'failed'
# result['missing_evidence'] = ["Need at least 3 functional requirements"]
# You stay in current phase
```

**The Checkpoint System**:
- Each phase has specific evidence requirements
- You MUST meet requirements to advance
- If you don't, you get specific feedback on what's missing
- Fix and resubmit until validation passes

### `get_workflow_state` - Check Progress

**When to Use**:
- Resuming after interruption
- Checking what's been completed
- Debugging workflow issues

```python
state = get_workflow_state(session_id="workflow-123")

# Returns:
# {
#   "session_id": "workflow-123",
#   "workflow_type": "spec_creation_v1",
#   "target_file": "auth.py",
#   "current_phase": 2,
#   "completed_phases": [0, 1],
#   "phase_evidence": {
#     "0": {...},
#     "1": {...}
#   },
#   "artifacts": {
#     "srd.md": "path/to/srd.md",
#     ...
#   }
# }
```

---

## 🌐 `aos_browser` - Browser Automation

### When to Use

- Testing web applications
- Validating UI behavior
- Taking screenshots for documentation
- Integration testing with real browser

### Common Actions

```python
# Navigate to page
aos_browser(
    action="navigate",
    url="http://localhost:3000",
    session_id="test-session"
)

# Click element
aos_browser(
    action="click",
    selector="#login-button",
    session_id="test-session"
)

# Fill form
aos_browser(
    action="fill",
    selector="#username",
    value="testuser@example.com",
    session_id="test-session"
)

# Take screenshot
aos_browser(
    action="screenshot",
    screenshot_path="/tmp/homepage.png",
    session_id="test-session"
)

# Close session
aos_browser(
    action="close",
    session_id="test-session"
)
```

### Testing Pattern

```python
# Start browser session
session = "auth-test-1"

# Navigate to app
aos_browser(action="navigate", url="http://localhost:3000", session_id=session)

# Fill login form
aos_browser(action="fill", selector="#email", value="test@example.com", session_id=session)
aos_browser(action="fill", selector="#password", value="testpass123", session_id=session)

# Submit
aos_browser(action="click", selector="button[type='submit']", session_id=session)

# Wait for dashboard
aos_browser(action="wait", selector="#dashboard", wait_for_state="visible", session_id=session)

# Verify success
aos_browser(action="screenshot", screenshot_path="/tmp/dashboard.png", session_id=session)

# Cleanup
aos_browser(action="close", session_id=session)
```

---

## 🏗️ Advanced Tools

### `create_workflow` - Generate New Workflow

**When to Use**: Creating custom workflows for project-specific tasks

```python
result = create_workflow(
    name="api-documentation-v1",
    workflow_type="documentation",
    phases=["Analysis", "Generation", "Validation"],
    target_language="python",
    quick_start=True  # Use minimal template
)

# Creates compliant workflow structure:
# .agent-os/workflows/api-documentation-v1/
# ├── metadata.json
# └── phases/
#     ├── 1/
#     │   ├── phase.md
#     │   └── task-1-analyze.md
#     ├── 2/
#     │   └── ...
```

### `validate_workflow` - Check Compliance

**When to Use**: Verifying workflow follows Agent OS standards

```python
result = validate_workflow(
    workflow_path="universal/workflows/my-workflow-v1"
)

# Returns:
# {
#   "compliant": True/False,
#   "issues": [...],  # What's wrong
#   "warnings": [...],  # What could be better
#   "compliance_score": 0.95  # 0-1 score
# }
```

---

## 📊 Usage Patterns by Task Type

### Pattern 1: Simple Implementation

```python
# Human: "Add logging to the API"

# 1. Query for guidance
search_standards("How should I implement logging in Python?")

# 2. Implement
# [Write logging configuration]
# [Add logging calls to API]

# 3. Test
# [Run tests]

# 4. Present
"Logging implemented using Python logging module. All tests passing."
```

### Pattern 2: Complex Feature (Use Workflow)

```python
# Human: "Add authentication system"

# 1. Start spec creation workflow
response = start_workflow("spec_creation_v1", "auth/")
session_id = response['session_id']

# 2. Get phase requirements
phase = get_current_phase(session_id)
# [Read phase content]

# 3. Query for guidance
search_standards("Authentication system architecture")
search_standards("JWT token implementation")

# 4. Complete phase work
# [Create srd.md]

# 5. Submit evidence
complete_phase(session_id, phase=1, evidence={...})

# 6. Repeat for each phase until spec complete

# 7. Execute spec with spec_execution_v1
```

### Pattern 3: Debugging

```python
# Tests failing

# 1. Analyze failure
# [Read test output]

# 2. Query for understanding
search_standards("What causes this error?")

# 3. Query for solution
search_standards("How do I fix X?")

# 4. Implement fix

# 5. Retest
# [Run tests again]

# 6. Iterate until passing
```

### Pattern 4: Code Review

```python
# Human: "Review the auth implementation"

# 1. Query standards for checklist
search_standards("What should I check in security code review?")

# 2. Review against standards
# [Check code]

# 3. Query specific concerns
search_standards("Is this JWT implementation secure?")

# 4. Provide detailed review
"Reviewed auth implementation:
✅ Password hashing correct
✅ Token expiration handled
❌ Missing rate limiting
❌ Should validate email format
Fixes implemented. Ready for re-review."
```

---

## 🎯 Tool Selection Guide

| Task | Primary Tool | Secondary Tools |
|------|-------------|-----------------|
| Simple implementation | `search_standards` | None |
| Complex feature | `start_workflow` | `search_standards`, `current_date` |
| Debugging | `search_standards` | None |
| Creating specs | `start_workflow` (spec_creation_v1) | `search_standards`, `current_date` |
| Executing specs | `start_workflow` (spec_execution_v1) | `search_standards` |
| Testing web app | `aos_browser` | `search_standards` |
| Creating workflows | `create_workflow` | `validate_workflow`, `search_standards` |

---

## ⚡ Pro Tips

### Tip 1: Query Liberally

Cost of query: 0.001 seconds, 2KB context
Cost of wrong implementation: 5 minutes debugging, failed tests, rework

**Query early, query often.**

### Tip 2: Chain Queries for Complex Tasks

```python
# Don't: One vague query
search_standards("build authentication")

# Do: Multiple specific queries
search_standards("How should I structure authentication middleware?")
search_standards("How do I securely hash passwords?")
search_standards("What JWT library should I use in Python?")
search_standards("How do I handle token refresh?")
search_standards("What security headers should auth endpoints include?")
```

### Tip 3: Use Workflows for Complex Tasks

If task has >3 major phases or >5 days of work → Use workflow

Workflows provide:
- Structure (don't forget steps)
- Quality gates (evidence validation)
- Resumability (can pause/resume)

### Tip 4: Combine Tools

```python
# Starting spec
date = current_date()
search_standards("How do I structure an SRD?")
start_workflow("spec_creation_v1", "feature.py")

# Implementing with browser testing
search_standards("FastAPI authentication patterns")
# [Implement]
aos_browser(action="navigate", url="http://localhost:8000")
aos_browser(action="click", selector="#test-login")
# [Verify]
```

### Tip 5: Check Workflow State After Interruptions

```python
# Session interrupted yesterday, resuming today

# First thing: check state
state = get_workflow_state(session_id="previous-session-id")
print(f"Currently on phase {state['current_phase']}")
print(f"Completed: {state['completed_phases']}")

# Get current phase content
phase = get_current_phase(session_id="previous-session-id")
# [Continue from where you left off]
```

---

## 🔗 Related Standards

- `standards/ai-assistant/AGENT-OS-ORIENTATION.md` - Overall Agent OS concepts
- `standards/ai-assistant/OPERATING-MODEL.md` - Your role and responsibilities
- `usage/ai-agent-quickstart.md` - Practical scenario examples

**Query anytime**:
```python
search_standards("How do I use MCP tools?")
search_standards("Query patterns for standards search")
```

---

**Master these tools, and you'll be a highly effective AI agent in Agent OS Enhanced.** 🚀

---

## 🔗 Query Standards Frequently

Throughout your session, query liberally to maintain correct behavior patterns:

```python
# Tool usage
search_standards("MCP tools guide")
search_standards("How to query standards effectively")

# Orientation refresh
search_standards("Agent OS orientation")  

# Specific needs
search_standards("How do I X?")  # Your actual question
```

**Remember**: Each query reinforces the pattern. Target 5-10 queries per task to maintain Agent OS awareness throughout your session.

---

**Query liberally. Build the habit. Better code follows.** 🚀

