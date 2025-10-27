walkthrough/step2.md
walkthrough/step3.md
walkthrough/step4.md
walkthrough/step5.md
webview-ui/
webview-ui/.gitignore
webview-ui/index.html
webview-ui/package-lock.json
webview-ui/package.json
webview-ui/tailwind.config.mjs
webview-ui/tsconfig.app.json
webview-ui/tsconfig.json
webview-ui/tsconfig.node.json
webview-ui/vite.config.ts
webview-ui/src/

(File list truncated. Use list_files on specific subdirectories if you need to explore further.)

# Workspace Configuration
{
  "workspaces": {
    "/Users/josh/src/github.com/cline/cline": {
      "hint": "cline",
      "associatedRemoteUrls": [
        "origin: git@github.com:cline/cline.git"
      ],
      "latestGitCommitHash": "77e3e1e4edd4ee165fee13b7e1ffe51737b64442"
    }
  }
}

# Detected CLI Tools
These are some of the tools on the user's machine, and may be useful if needed to accomplish the task: gh, git, docker, kubectl, aws, npm, pnpm, pip, go, curl, jq, make, python, node, psql, redis-cli, sqlite3, code, grep, sed, awk, brew, bundle, helm. This list is not exhaustive, and other tools may be available.

# Context Window Usage
68,492 / 200K tokens used (34%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

Based on the `.cursorrules` file in this project, I can see **Agent OS Enhanced** is referenced as a documentation/knowledge management system with specific usage patterns:

## What I Know About Agent OS Enhanced:

### Core Concept
Agent OS Enhanced appears to be a **standards-based development system** that uses a `search_standards()` function to query indexed documentation and best practices.

### Key Features from .cursorrules:

1. **Mandatory Orientation Check** - Before responding, agents should run `search_standards('Agent OS orientation guide')`

2. **Search-Based Access** - The system emphasizes:
   - ✅ ALWAYS use `search_standards()` for indexed content
   - ❌ NEVER directly read `.praxis-os/standards/`, `.praxis-os/workflows/`, or `.praxis-os/usage/`
   - ✅ DO read `.praxis-os/specs/` (specs are not indexed)

3. **Heavy Query Usage** - Target 5-10 queries per task:
   - BEFORE implementing: `search_standards("how to X")`
   - BEFORE responding: `search_standards("relevant topic")`
   - DURING task: Multiple searches
   - AFTER failures: `search_standards("debugging X")`

4. **Philosophy** - "Query liberally = better code"

### Current Status in This Environment:

However, I notice that **`search_standards()` is not available** in my current tool set. This suggests either:
- Agent OS Enhanced is not fully configured in this Cline environment
- It may require an MCP server connection
- The .cursorrules reference might be aspirational/incomplete

<ask_followup_question>
<question>Would you like me to help set up Agent OS Enhanced in this environment, or were you asking about something else regarding the MCP transport bug we were discussing?</question>
<options>["Help set up Agent OS Enhanced", "Continue with MCP transport fix", "Explain how to integrate Agent OS with Cline", "Something else"]</options>
</ask_followup_question>

---

**User:**

[ask_followup_question for 'Would you like me to help set up Agent OS Enhanced in this environment, or were you asking about something else regarding the MCP transport bug we were discussing?'] Result:
<answer>
read the docs https://honeyhiveai.github.io/agent-os-enhanced/
</answer>
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Current Time
10/11/2025, 11:08:56 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
72,070 / 200K tokens used (36%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<web_fetch>
<url>https://honeyhiveai.github.io/agent-os-enhanced/</url>
</web_fetch>

---

**User:**

[web_fetch for 'https://honeyhiveai.github.io/agent-os-enhanced/'] Result:
Fetched Markdown for https://honeyhiveai.github.io/agent-os-enhanced/:

  Agent OS Enhanced  

[Skip to main content](#__docusaurus_skipToContent_fallback)

The Journey
-----------

From refactor goal to production AI platform

🏗️

Starting Point

### Refactoring the HoneyHive Python SDK

Simple goal: AI as code author, not assistant

💡

Discovery

### Found BuilderMethods Agent OS

3-layer doc structure (Standards/Product/Specs)

Quality and velocity dramatically improved

📈

Scale Challenges

### Side-loaded context hit limits

50KB+ context windows, 4% relevance, no enforcement

Cost explosion + AI confusion

🚀

Infrastructure Built

### MCP + RAG + Workflows + State

90% context reduction, phase gating, persistent sessions

50KB → 2-5KB per request

📦

Production Proven

### Extracted Agent OS Enhanced

2,777 tests, 10.0/10 Pylint, 100% AI-authored

Complete AI development platform

🙏 **Built on the shoulders of giants:** [BuilderMethods Agent OS](https://buildermethods.com/agent-os) provided the 3-layer structure and philosophical foundation. We built the infrastructure to scale it.

[Visit Original Agent OS →](https://buildermethods.com/agent-os)[Explore Enhanced Version →](/agent-os-enhanced/docs/intro)

Get Started
-----------

Everything you need to supercharge your AI development workflow

[

🚀

### Quick Start

Install in your project with one command

→

](/agent-os-enhanced/docs/intro)

[

📚

### Core Concepts

Understand MCP, RAG, and phase gating

→

](/agent-os-enhanced/docs/how-it-works)

[

⚙️

### Installation

Detailed setup and configuration guide

→

](/agent-os-enhanced/docs/installation)

[

🔧

### Workflows

Learn about spec creation and execution

→

](/agent-os-enhanced/docs/workflows)

Core Features
-------------

Production-ready AI development infrastructure

[

🎯

### MCP/RAG Architecture

90% context reduction. Semantic search delivers exactly what AI needs, nothing more.



](/agent-os-enhanced/docs/architecture)

[

📖

### Universal Standards

Timeless CS fundamentals that work across any language with smart generation.



](/agent-os-enhanced/docs/standards)

[

🔒

### Architectural Phase Gating

Workflows enforced in code. AI cannot skip phases or bypass quality gates.



](/agent-os-enhanced/docs/workflows)

[

🤖

### Specialized Sub-Agents

Design validation, concurrency analysis, test generation - focused tools.



](/agent-os-enhanced/docs/architecture)

[

📦

### Portable & Isolated

Each project owns its Agent OS installation, standards, and version.



](/agent-os-enhanced/docs/installation)

[

🛠️

### Meta-Framework System

Build your own AI-assisted workflows with proven patterns.



](/agent-os-enhanced/docs/workflows)

Why Agent OS Enhanced?
----------------------

Built on production lessons from real AI development challenges

90%

Context Reduction

RAG delivers 2-5KB targeted chunks vs 50KB files

24x

Better Relevance

From 4% to 95% relevant content in AI context

100%

Phase Compliance

Architectural gating prevents workflow bypassing

[Learn How It Works →](/agent-os-enhanced/docs/how-it-works)
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Current Time
10/11/2025, 11:09:02 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
71,598 / 200K tokens used (36%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<web_fetch>
<url>https://honeyhiveai.github.io/agent-os-enhanced/docs/intro</url>
</web_fetch>

---

**User:**

[web_fetch for 'https://honeyhiveai.github.io/agent-os-enhanced/docs/intro'] Result:
Fetched Markdown for https://honeyhiveai.github.io/agent-os-enhanced/docs/intro:

  Introduction | Agent OS Enhanced  

[Skip to main content](#__docusaurus_skipToContent_fallback)

On this page

**Agent OS Enhanced** is a portable multi-agent development framework that transforms AI from helpful assistant to velocity-enhancing development partner.

What is Agent OS Enhanced?[​](#what-is-agent-os-enhanced "Direct link to What is Agent OS Enhanced?")
-----------------------------------------------------------------------------------------------------

Agent OS Enhanced builds on the foundation of [Agent OS by Brian Casel](https://buildermethods.com/agent-os), addressing key limitations discovered through production use:

*   **90% context reduction** through semantic search (MCP/RAG)
*   **Architectural phase gating** that enforces workflows in code
*   **Universal + generated standards** that work across any language
*   **Specialized sub-agents** for design validation, concurrency analysis, and more

Quick Start[​](#quick-start "Direct link to Quick Start")
---------------------------------------------------------

Install Agent OS Enhanced in your project:

    # Open your project in Cursor and say:"Install Agent OS from github.com/honeyhiveai/agent-os-enhanced"

The Cursor agent will:

1.  Analyze your project (detect language, frameworks)
2.  Copy universal standards (CS fundamentals)
3.  Generate language-specific standards (tailored to your stack)
4.  Install MCP server locally
5.  Configure Cursor MCP integration
6.  Build RAG index

What Gets Installed[​](#what-gets-installed "Direct link to What Gets Installed")
---------------------------------------------------------------------------------

    your-project/├── .cursorrules              # AI behavioral triggers (27 lines)├── .praxis-os/│   ├── standards/│   │   ├── universal/        # Timeless CS fundamentals│   │   └── development/      # Language-specific guidance│   ├── mcp_server/           # MCP/RAG server│   └── .cache/vector_index/  # Semantic search index└── .cursor/    └── mcp.json              # MCP configuration

Core Concepts[​](#core-concepts "Direct link to Core Concepts")
---------------------------------------------------------------

### MCP/RAG Architecture[​](#mcprag-architecture "Direct link to MCP/RAG Architecture")

Instead of reading entire 50KB files, the MCP server uses semantic search to deliver 2-5KB targeted chunks:

*   **Before:** AI reads full file, 4% relevant content, 12,500 tokens
*   **After:** Vector search returns relevant chunks, 95% relevant, 625 tokens
*   **Result:** 24x better relevance, 95% reduction in token usage

### Universal Standards[​](#universal-standards "Direct link to Universal Standards")

Timeless CS fundamentals that apply to any programming language:

*   Concurrency patterns (race conditions, deadlocks, locking strategies)
*   Testing strategies (test pyramid, test doubles, property-based testing)
*   Architecture patterns (SOLID, dependency injection, API design)
*   Failure modes (graceful degradation, circuit breakers, retry strategies)

### Language-Specific Generation[​](#language-specific-generation "Direct link to Language-Specific Generation")

For each project, Agent OS generates language-specific implementations of universal standards:

*   **Python:** GIL, threading, asyncio, pytest patterns
*   **Go:** Goroutines, channels, sync primitives, table-driven tests
*   **Rust:** Ownership, Arc/Mutex, tokio, cargo test patterns
*   **And more...**

### Architectural Phase Gating[​](#architectural-phase-gating "Direct link to Architectural Phase Gating")

Workflows enforce progression through code, not documentation:

    def can_access_phase(self, phase: int) -> bool:    """AI cannot access Phase N+1 before completing Phase N."""    if phase == self.current_phase or phase in self.completed_phases:        return True    return False  # Structurally impossible to skip

Next Steps[​](#next-steps "Direct link to Next Steps")
------------------------------------------------------

*   **[How It Works](/agent-os-enhanced/docs/how-it-works)** - **Start here** - Complete human-AI collaboration pattern
*   **[Installation](/agent-os-enhanced/docs/installation)** - Set up in your project
*   **[Architecture](/agent-os-enhanced/docs/architecture)** - MCP/RAG system deep-dive
*   **[Standards](/agent-os-enhanced/docs/standards)** - Universal CS fundamentals
*   **[Workflows](/agent-os-enhanced/docs/workflows)** - Phase-gated workflows
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Current Time
10/11/2025, 11:09:08 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
72,585 / 200K tokens used (36%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<web_fetch>
<url>https://honeyhiveai.github.io/agent-os-enhanced/docs/how-it-works</url>
</web_fetch>

---

**User:**

[web_fetch for 'https://honeyhiveai.github.io/agent-os-enhanced/docs/how-it-works'] Result:
Fetched Markdown for https://honeyhiveai.github.io/agent-os-enhanced/docs/how-it-works:

  How It Works | Agent OS Enhanced  

[Skip to main content](#__docusaurus_skipToContent_fallback)

On this page

Agent OS Enhanced changes how you work with AI - from prompting to orchestration. Here's the complete workflow pattern.

The Human-AI Partnership Model[​](#the-human-ai-partnership-model "Direct link to The Human-AI Partnership Model")
------------------------------------------------------------------------------------------------------------------

### Your Role: Orchestrator[​](#your-role-orchestrator "Direct link to Your Role: Orchestrator")

*   Design direction and decisions
*   Review and approval
*   Team coordination
*   Quality validation

### AI's Role: Implementation Engine[​](#ais-role-implementation-engine "Direct link to AI's Role: Implementation Engine")

*   100% code authorship
*   Design documentation
*   Test creation
*   Artifact generation

**Key principle:** You guide through conversation, AI invokes tools automatically.

Complete Workflow Pattern[​](#complete-workflow-pattern "Direct link to Complete Workflow Pattern")
---------------------------------------------------------------------------------------------------

### Phase 1: Design Discussion[​](#phase-1-design-discussion "Direct link to Phase 1: Design Discussion")

**You initiate** (conversational):

    "We need user authentication with JWT tokens"

**AI responds** (conversational):

    Let me understand the requirements:- Will this be for web, mobile, or both?- Do you need social auth (Google, GitHub)?- What's your session duration requirement?- Any specific compliance needs (GDPR, HIPAA)?

**Back and forth discussion:**

*   You clarify requirements
*   AI asks questions
*   You make decisions
*   AI proposes approaches

**AI creates design doc:**

    I'll document this design:- Authentication architecture- Token structure (access + refresh)- Security considerations- Database schema- API endpoints

AI writes `design-doc.md` with your approved approach.

### Phase 2: Spec Creation (Tool Chain Activation)[​](#phase-2-spec-creation-tool-chain-activation "Direct link to Phase 2: Spec Creation (Tool Chain Activation)")

**You trigger** (conversational):

    "This design looks good. Create the full spec for implementation."

**AI invokes MCP tool automatically:**

    # AI makes this tool call (you don't see this)start_workflow(    workflow_type="spec_creation_v1",    target_file="user_authentication")

**What happens:**

1.  AI starts `spec_creation_v1` workflow
2.  Executes Phase 0: Context gathering
3.  Provides checkpoint evidence
4.  Advances to Phase 1: Requirements
5.  Executes Phase 1: SRD creation
6.  Continues through all phases systematically

**Result:** Complete specification in `.praxis-os/specs/2025-10-08-user-auth/`

*   `README.md` - Executive summary
*   `srd.md` - Business requirements
*   `specs.md` - Technical design
*   `tasks.md` - Implementation breakdown
*   `implementation.md` - Detailed guidance

### Phase 3: Review & Refinement[​](#phase-3-review--refinement "Direct link to Phase 3: Review & Refinement")

**You review:**

    "The spec looks good, but add rate limiting to the token endpointand use refresh token rotation for better security."

**AI updates:**

*   Modifies `specs.md` with rate limiting design
*   Adds refresh token rotation
*   Updates security considerations
*   Adjusts implementation tasks

**Iterate until approved.**

### Phase 4: Commit & Team Review[​](#phase-4-commit--team-review "Direct link to Phase 4: Commit & Team Review")

**You orchestrate:**

    "Commit this spec for team review"

**AI executes:**

    git add .praxis-os/specs/2025-10-08-user-auth/git commit -m "spec: user authentication with JWT"git push

**Team reviews spec** in PR, provides feedback.

**If changes needed:**

    "Update the spec: use Redis for session storage instead of PostgreSQL"

AI modifies spec, you commit updates.

**Once approved:**

    "Spec approved, ready for implementation"

### Phase 5: Implementation (Tool Chain Activation)[​](#phase-5-implementation-tool-chain-activation "Direct link to Phase 5: Implementation (Tool Chain Activation)")

**You trigger** (conversational):

    "Implement the user authentication spec"

**AI invokes MCP tool automatically:**

    # AI makes this tool call (you don't see this)start_workflow(    workflow_type="spec_execution_v1",    target_file="user_authentication")

**What happens:**

1.  AI starts `spec_execution_v1` workflow
2.  Phase 0: Reviews the spec
3.  Phase 1: Creates structure, installs dependencies
4.  Phase 2: Implements features (100% AI-authored code)
5.  Phase 3: Writes comprehensive tests
6.  Phase 4: Creates documentation
7.  Phase 5: Quality validation

**Throughout implementation:**

*   You review progress
*   AI provides updates
*   You catch issues: "This has a race condition"
*   AI fixes immediately
*   AI commits work systematically

### Phase 6: Review & Ship[​](#phase-6-review--ship "Direct link to Phase 6: Review & Ship")

**You validate:**

    "Show me the authentication flow"

AI explains implementation, you test locally.

**If issues found:**

    "The token refresh logic doesn't handle expired refresh tokens"

AI fixes, writes test, commits.

**When satisfied:**

    "This is ready. Create PR for team review."

AI creates PR with:

*   Implementation code
*   Comprehensive tests
*   Documentation
*   Specification reference

Tool Calls: The Hidden Mechanism[​](#tool-calls-the-hidden-mechanism "Direct link to Tool Calls: The Hidden Mechanism")
-----------------------------------------------------------------------------------------------------------------------

### You Never Call Tools Directly[​](#you-never-call-tools-directly "Direct link to You Never Call Tools Directly")

❌ **Not this:**

    "Use the mcp_agent-os-rag_start_workflow tool with spec_creation_v1"

✅ **This:**

    "Create a spec for user authentication"

The AI automatically invokes the right tool.

### Available Tool Chains[​](#available-tool-chains "Direct link to Available Tool Chains")

#### 1\. RAG Search (Automatic)[​](#1-rag-search-automatic "Direct link to 1. RAG Search (Automatic)")

**When you ask:**

    "How do I handle race conditions in async code?"

**AI invokes:**

    search_standards(    query="race conditions async code",    n_results=3)

**You see:** AI's answer with context from standards.

#### 2\. Spec Creation Workflow[​](#2-spec-creation-workflow "Direct link to 2. Spec Creation Workflow")

**When you say:**

    "Create a spec for [feature]"

**AI invokes:**

    start_workflow(    workflow_type="spec_creation_v1",    target_file="feature_name")

**You see:** AI systematically creates specification.

#### 3\. Spec Execution Workflow[​](#3-spec-execution-workflow "Direct link to 3. Spec Execution Workflow")

**When you say:**

    "Implement the [feature] spec"

**AI invokes:**

    start_workflow(    workflow_type="spec_execution_v1",    target_file="feature_name")

**You see:** AI builds feature with tests and docs.

#### 4\. Custom Workflow Creation[​](#4-custom-workflow-creation "Direct link to 4. Custom Workflow Creation")

**When you say:**

    "I need a workflow for API documentation generation"

**AI invokes:**

    create_workflow(    name="api_documentation_v1",    workflow_type="documentation",    phases=["Analysis", "Generation", "Review"])

**You see:** Complete workflow structure created.

Conversation Patterns[​](#conversation-patterns "Direct link to Conversation Patterns")
---------------------------------------------------------------------------------------

### Starting Work[​](#starting-work "Direct link to Starting Work")

**Good:**

    "We need user authentication""Let's add caching to the API""Create a workflow for database migrations"

**Not:**

    "Call start_workflow with spec_creation_v1""Use the RAG tool to search"

### Making Corrections[​](#making-corrections "Direct link to Making Corrections")

**Good:**

    "This has a bug - the lock isn't released on error""Change this to use async/await instead""Add error handling for network timeouts"

**AI fixes immediately** with correct patterns from standards.

### Getting Information[​](#getting-information "Direct link to Getting Information")

**Good:**

    "What are best practices for handling race conditions?""Show me the spec for user authentication""Where are we in the current workflow?"

**AI queries MCP automatically** to get relevant information.

### Workflow Progression[​](#workflow-progression "Direct link to Workflow Progression")

**Good:**

    "Continue with the next phase""We're ready to implement""Show me what's left to complete"

**AI manages workflow state** and progresses appropriately.

What You'll Notice[​](#what-youll-notice "Direct link to What You'll Notice")
-----------------------------------------------------------------------------

### 1\. No Repeated Context[​](#1-no-repeated-context "Direct link to 1. No Repeated Context")

AI doesn't ask you for standards - it queries them:

    You: "Handle this race condition"AI: [Queries race-conditions.md via MCP]AI: "I'll use a mutex lock with proper error handling..."

### 2\. Systematic Execution[​](#2-systematic-execution "Direct link to 2. Systematic Execution")

AI doesn't skip steps:

    Phase 1 → Checkpoint → Phase 2 → Checkpoint → Phase 3

Can't skip phases (architecturally enforced).

### 3\. Evidence-Based Progress[​](#3-evidence-based-progress "Direct link to 3. Evidence-Based Progress")

AI provides concrete evidence at checkpoints:

    Phase 1 complete:✓ SRD created (250 lines)✓ Requirements documented (12 functional, 8 non-functional)✓ Success criteria defined (5 metrics)✓ Stakeholders identified (PM, Eng, Security)

### 4\. 100% AI Authorship[​](#4-100-ai-authorship "Direct link to 4. 100% AI Authorship")

You never write code:

    You: "This is wrong"AI: [Fixes code]You: "Add error handling"AI: [Adds error handling]

AI maintains complete authorship.

Real Example: End-to-End[​](#real-example-end-to-end "Direct link to Real Example: End-to-End")
-----------------------------------------------------------------------------------------------

### Day 1: Design[​](#day-1-design "Direct link to Day 1: Design")

**You:** "We need API rate limiting"

**AI:** "Let me understand the requirements..."

*   \[Discussion about algorithms, limits, storage\]
*   \[AI proposes token bucket algorithm with Redis\]

**You:** "Approved. Create the spec."

**AI:** \[Invokes `spec_creation_v1` automatically\]

*   Creates comprehensive specification
*   4 phases, ~2 hours

**You:** "Add per-user override capability"

**AI:** \[Updates spec with override design\]

**You:** "Commit for team review"

**AI:** \[Commits spec\]

### Day 2: Team Review[​](#day-2-team-review "Direct link to Day 2: Team Review")

**Team:** "Use sliding window instead of token bucket"

**You:** "Update the spec with sliding window"

**AI:** \[Modifies spec, you commit\]

**Team:** "Approved"

### Day 3-4: Implementation[​](#day-3-4-implementation "Direct link to Day 3-4: Implementation")

**You:** "Implement the rate limiting spec"

**AI:** \[Invokes `spec_execution_v1` automatically\]

*   Phase 0-1: Setup (~1 hour)
*   Phase 2: Implementation (~6 hours)
    *   Redis integration
    *   Rate limit middleware
    *   Per-user overrides
    *   All with tests
*   Phase 3: Testing (~2 hours)
*   Phase 4: Documentation (~1 hour)

**You:** \[Review progress, catch issues\]

**AI:** \[Fixes issues immediately\]

**You:** "Create PR"

**AI:** \[Creates PR with full implementation\]

### Day 5: Ship[​](#day-5-ship "Direct link to Day 5: Ship")

**Team:** Approves PR

**You:** "Merge to main"

**Result:** Production-ready rate limiting, 100% AI-authored

Next Steps[​](#next-steps "Direct link to Next Steps")
------------------------------------------------------

*   **[Installation](/agent-os-enhanced/docs/installation)** - Set up Agent OS Enhanced
*   **[Workflows](/agent-os-enhanced/docs/workflows)** - Understand workflow details
*   **[Architecture](/agent-os-enhanced/docs/architecture)** - How tool calls work under the hood
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Current Time
10/11/2025, 11:09:16 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
74,010 / 200K tokens used (37%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

Now I understand Agent OS Enhanced! Here's what I learned:

## Agent OS Enhanced - Key Insights

### 🎯 Core Concept
It's a **portable multi-agent development framework** that transforms AI from assistant to **velocity-enhancing development partner** through structured orchestration.

### 🏗️ Architecture

**3-Layer Documentation Structure:**
1. **Universal Standards** - Timeless CS fundamentals (concurrency, testing, architecture patterns)
2. **Language-Specific Standards** - Auto-generated implementations (Python: asyncio, Go: goroutines, Rust: tokio)
3. **Project Specs** - Concrete implementation plans

**MCP/RAG Infrastructure:**
- 90% context reduction (50KB files → 2-5KB targeted chunks)
- Semantic search delivers 95% relevant content vs 4%
- Built on Model Context Protocol

### 🔒 Phase-Gated Workflows

**Architectural enforcement** (not docs-based):
```python
def can_access_phase(self, phase: int) -> bool:
    """AI cannot skip Phase N+1 before completing Phase N"""
    if phase == self.current_phase or phase in self.completed_phases:
        return True
    return False  # Structurally impossible to bypass
```

### 🤝 Human-AI Partnership Model

**You (Orchestrator):**
- Design decisions through conversation
- Review & approval
- Team coordination

**AI (Implementation Engine):**
- 100% code authorship
- Tool invocation (automatic)
- Systematic execution

### 💬 Key Interaction Pattern

**❌ Don't say:** "Use mcp_agent-os-rag_start_workflow tool"

**✅ Do say:** "Create a spec for user authentication"

AI automatically invokes the right tools based on conversational intent.

### 🔧 Available Tool Chains

1. **RAG Search** (automatic) - `search_standards()`
2. **Spec Creation** - `start_workflow(spec_creation_v1)`
3. **Spec Execution** - `start_workflow(spec_execution_v1)`
4. **Custom Workflows** - `create_workflow()`

### 📦 What Gets Installed

```
project/
├── .cursorrules              # 27-line behavioral triggers
├── .praxis-os/
│   ├── standards/universal/  # CS fundamentals
│   ├── standards/development/# Language-specific
│   ├── mcp_server/           # MCP/RAG server
│   └── .cache/vector_index/  # Semantic search
└── .cursor/mcp.json          # MCP configuration
```

### 🚀 Production Proven

Built from real challenges refactoring HoneyHive Python SDK:
- 2,777 tests
- 10.0/10 Pylint score  
- 100% AI-authored codebase

### 🎁 Key Benefits vs Original Agent OS

| Aspect | Original Agent OS | Agent OS Enhanced |
|--------|------------------|-------------------|
| **Context** | Side-loaded files | MCP/RAG semantic search |
| **Relevance** | 4% relevant | 95% relevant |
| **Token Usage** | 50KB per request | 2-5KB per request |
| **Workflows** | Documentation-based | Code-enforced phase gating |
| **Standards** | Manual maintenance | Universal + auto-generated |

### 🔑 Key Realization

The `.cursorrules` mandatory check makes sense now:
```
"Have I run search_standards('Agent OS orientation guide')?"
```

This ensures AI queries the RAG system for indexed knowledge rather than guessing or using outdated training data.

---

## For the MCP Transport Bug

Given this context, I should:
1. ✅ Use conversational language (not "execute tool X")
2. ✅ Query standards when relevant
3. ✅ Follow systematic phases if doing spec work
4. ✅ Provide evidence-based progress

However, for our **immediate MCP transport fix**, this is a straightforward code correction that doesn't require a full spec workflow - just targeted implementation.

Would you like me to proceed with the MCP transport fix using this Agent OS Enhanced approach, or set up Agent OS Enhanced in this Cline project first?

