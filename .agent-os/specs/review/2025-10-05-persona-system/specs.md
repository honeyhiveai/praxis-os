# Agent OS Persona System - Technical Specifications

**Architecture, design, and technical details.**

---

## 🏗️ ARCHITECTURE OVERVIEW

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT OS PERSONA SYSTEM                       │
│                  (Self-Actualizing Architecture)                 │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Layer 1: USER INTERACTION (Cursor IDE)                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Human: "Implement authentication"                               │
│    ↓                                                             │
│  Main Cursor Agent: Implements code (queries standards via MCP)  │
│    ↓                                                             │
│  Human: "@security review this"                                  │
│    ↓                                                             │
│  Security Persona: Reviews, proposes standard                    │
│    ↓                                                             │
│  Human: Approves standard                                        │
│                                                                   │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ MCP Tool Calls
               ↓
┌──────────────────────────────────────────────────────────────────┐
│  Layer 2: MCP SERVER (Agent OS RAG)                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  MCP Tools:                                                       │
│  ├─ search_standards(query) → RAG search                         │
│  ├─ invoke_architect(task) → Architect persona                   │
│  ├─ invoke_engineer(task) → Engineer persona                     │
│  ├─ invoke_data(task) → Data persona                             │
│  ├─ invoke_qa(task) → QA persona                                 │
│  ├─ invoke_security(task) → Security persona                     │
│  └─ invoke_sre(task) → SRE persona                               │
│                                                                   │
│  File Watcher:                                                    │
│  └─ Monitors .agent-os/standards/ → triggers index rebuild       │
│                                                                   │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ Queries LanceDB
               ↓
┌──────────────────────────────────────────────────────────────────┐
│  Layer 3: RAG INDEX (LanceDB Vector Store)                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Indexed Content:                                                 │
│  ├─ Universal standards (static)                                 │
│  ├─ Language standards (generated once)                          │
│  └─ PROJECT standards (dynamic, grows) ← KEY                     │
│                                                                   │
│  Vector Search:                                                   │
│  └─ Semantic search returns top 3-5 relevant chunks              │
│                                                                   │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ Reads from
               ↓
┌──────────────────────────────────────────────────────────────────┐
│  Layer 4: STANDARDS REPOSITORY (.agent-os/standards/)            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  architecture/                                                    │
│    ├─ api-conventions.md        ← Created by Architect           │
│    ├─ caching-strategy.md       ← Created by Architect           │
│    └─ service-communication.md  ← Created by Architect           │
│                                                                   │
│  data/                                                            │
│    ├─ kafka-patterns.md         ← Created by Data Engineer       │
│    ├─ airflow-conventions.md    ← Created by Data Engineer       │
│    └─ dbt-standards.md          ← Created by Data Engineer       │
│                                                                   │
│  development/                                                     │
│    ├─ error-handling.md         ← Created by Engineer            │
│    ├─ logging-patterns.md       ← Created by Engineer            │
│    └─ code-organization.md      ← Created by Engineer            │
│                                                                   │
│  testing/                                                         │
│    └─ test-conventions.md       ← Created by QA                  │
│                                                                   │
│  security/                                                        │
│    └─ auth-patterns.md          ← Created by Security            │
│                                                                   │
│  operations/                                                      │
│    ├─ deployment-process.md     ← Created by SRE                 │
│    └─ slo-definitions.md        ← Created by SRE                 │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Components

#### Component 1: Persona Invocation System
**Purpose:** Enable users to invoke specialized AI personas  
**Responsibilities:**
- Parse `@persona` syntax from user messages
- Route to appropriate persona handler
- Execute personas asynchronously via background job queue
- Provide real-time progress updates via polling
- Return persona responses to user

**Implementation:** MCP tools per persona (e.g., `invoke_architect`), async background execution with job queue

**Architecture:** See [async-persona-execution-architecture.md](supporting-docs/async-persona-execution-architecture.md) for complete async design

#### Component 2: Persona Prompt System
**Purpose:** Define each persona's identity, expertise, and behavior  
**Responsibilities:**
- Load optimized persona prompt (≤1,500 tokens)
- Include standards population capability
- Provide review templates
- Define standard directories

**Implementation:** System prompts stored in `mcp_server/personas/`

#### Component 3: Standards Population System
**Purpose:** Enable personas to propose and create standards  
**Responsibilities:**
- Detect pattern opportunities
- Generate standard proposals
- Handle Human review/feedback cycle
- Create final standard files

**Implementation:** Standard creation workflow in persona prompts

#### Component 4: File Watcher & Auto-Indexing
**Purpose:** Automatically index new standards for RAG  
**Responsibilities:**
- Monitor `.agent-os/standards/` directory
- Detect new/modified `.md` files
- Trigger incremental RAG index rebuild
- Update LanceDB vector store

**Implementation:** Existing `AgentOSFileWatcher` (already built)

#### Component 5: RAG Search Engine
**Purpose:** Provide semantic search over project standards  
**Responsibilities:**
- Accept natural language queries
- Perform vector similarity search
- Return top 3-5 relevant chunks
- Include metadata (file, section, relevance score)

**Implementation:** Existing `RAGEngine` with LanceDB (already built)

#### Component 6: Main Agent Integration
**Purpose:** Enable main Cursor agent to automatically query standards  
**Responsibilities:**
- Intercept relevant queries
- Call `search_standards()` via MCP
- Incorporate returned chunks into responses
- Cite which standards were used

**Implementation:** Automatic behavior in Cursor IDE

---

## 📡 MCP TOOL SPECIFICATIONS

### Execution Model: Async Background Jobs

**All persona invocations use async execution** to prevent timeout issues and provide progress feedback.

**How It Works:**
1. User invokes persona (e.g., `@architect review this`)
2. MCP tool creates background job immediately (<50ms)
3. Returns job ID with estimated duration
4. Main Cursor agent polls for progress every 5 seconds
5. User sees real-time updates: "Searching standards... 40%"
6. Job completes, full review returned

**Key Benefits:**
- ✅ **Zero timeout risk** - Tools return immediately, workers run indefinitely
- ✅ **Progress visibility** - Users see "Analyzing... 60%" updates
- ✅ **Concurrent execution** - 3+ personas can run simultaneously
- ✅ **Scalable** - Handles 5+ minute comprehensive reviews

**Architecture:** See [async-persona-execution-architecture.md](supporting-docs/async-persona-execution-architecture.md) for full design

---

### Tool 1: invoke_architect

**Purpose:** Start Software Architect persona review as background job

**Signature:**
```python
@mcp.tool()
async def invoke_architect(
    task: str,
    context: Optional[str] = None,
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    Invoke Software Architect persona (async background job).
    
    Args:
        task: What to review/design (e.g., "review API design", "document patterns")
        context: Optional context (file paths, code, descriptions)
        priority: "low" | "normal" | "high" (affects queue priority)
    
    Returns:
        {
            "status": "started",
            "job_id": "a7f3c9d2-...",
            "persona": "architect",
            "estimated_duration_seconds": 45,
            "poll_command": "check_persona_job('a7f3c9d2...')",
            "message": "Architect review started. Polling for progress..."
        }
    """
```

**Usage:**
```
User: "@architect review this API design"
→ Calls: invoke_architect("review API design", context=<current file>)
→ Returns: Job started response with job_id
→ Main agent polls: check_persona_job(job_id) every 5s
→ Shows progress: "Searching standards... 40%"
→ Eventually returns: Full architecture review
```

**Scope:**
- System design and architecture
- Performance architecture
- Concurrency design
- API design
- Data architecture (high-level)
- Can propose architecture standards

---

### Tool 2: invoke_engineer

**Purpose:** Invoke Software Engineer persona for code review

**Signature:**
```python
@mcp.tool()
async def invoke_engineer(
    task: str,
    context: Optional[str] = None
) -> str:
    """
    Invoke Software Engineer persona.
    
    Args:
        task: What to review/implement (e.g., "review code quality", "document patterns")
        context: Optional context
    
    Returns:
        Engineer's review/proposal
    """
```

**Scope:**
- Code design and implementation
- Performance optimization
- Thread-safety
- Code quality and standards
- Refactoring
- Can propose development standards

---

### Tool 3: invoke_data

**Purpose:** Invoke Data Engineer persona for data architecture

**Signature:**
```python
@mcp.tool()
async def invoke_data(
    task: str,
    context: Optional[str] = None
) -> str:
    """
    Invoke Data Engineer persona.
    
    Args:
        task: What to review/design (e.g., "review Kafka setup", "document patterns")
        context: Optional context
    
    Returns:
        Data engineer's review/proposal
    """
```

**Scope:**
- Data pipeline architecture
- Streaming/ETL patterns
- Data modeling
- Data quality
- Tech stack standards population
- Can propose data standards

---

### Tool 4: invoke_qa

**Purpose:** Invoke QA Engineer persona for testing strategy

**Signature:**
```python
@mcp.tool()
async def invoke_qa(
    task: str,
    context: Optional[str] = None
) -> str:
    """
    Invoke QA Engineer persona.
    
    Args:
        task: What to review (e.g., "review test coverage", "document test patterns")
        context: Optional context
    
    Returns:
        QA engineer's review/proposal
    """
```

**Scope:**
- Testing strategy
- Test coverage analysis
- Edge case identification
- Test quality
- Can propose testing standards

---

### Tool 5: invoke_security

**Purpose:** Invoke Security Engineer persona for security review

**Signature:**
```python
@mcp.tool()
async def invoke_security(
    task: str,
    context: Optional[str] = None
) -> str:
    """
    Invoke Security Engineer persona.
    
    Args:
        task: What to review (e.g., "security review", "document auth patterns")
        context: Optional context
    
    Returns:
        Security engineer's review/proposal
    """
```

**Scope:**
- Security vulnerabilities
- Threat modeling
- OWASP compliance
- Secure coding patterns
- Can propose security standards

---

### Tool 6: invoke_sre

**Purpose:** Invoke SRE persona for production readiness

**Signature:**
```python
@mcp.tool()
async def invoke_sre(
    task: str,
    context: Optional[str] = None
) -> str:
    """
    Invoke SRE persona.
    
    Args:
        task: What to review (e.g., "production readiness", "document deployment")
        context: Optional context
    
    Returns:
        SRE's review/proposal
    """
```

**Scope:**
- Production readiness
- SLO/SLI design
- Observability
- Deployment strategies
- Operational excellence
- Can propose operations standards

---

### Tool 7: check_persona_job

**Purpose:** Poll for persona job status and progress

**Signature:**
```python
@mcp.tool()
async def check_persona_job(job_id: str) -> Dict[str, Any]:
    """
    Check status of a persona background job.
    
    Call this repeatedly (every 3-5 seconds) to monitor progress
    until status is "complete" or "failed".
    
    Args:
        job_id: Job identifier returned by invoke_*()
    
    Returns:
        If running:
        {
            "status": "running",
            "persona": "architect",
            "progress": {
                "phase": "analyzing",
                "percent_complete": 60,
                "message": "Analyzing code patterns...",
                "eta_seconds": 20,
                "tool_calls_completed": 2
            },
            "elapsed_seconds": 25
        }
        
        If complete:
        {
            "status": "complete",
            "persona": "architect",
            "result": "🎯 Architecture Review:\n\n...",
            "duration_seconds": 42,
            "tool_calls_made": 3,
            "tokens_used": {"input": 2500, "output": 1800}
        }
        
        If failed:
        {
            "status": "failed",
            "persona": "architect",
            "error": "LLM API timeout after 120s",
            "partial_result": "..." (if any),
            "elapsed_seconds": 120
        }
    """
```

---

### Tool 8: list_persona_jobs

**Purpose:** List recent persona jobs for observability

**Signature:**
```python
@mcp.tool()
async def list_persona_jobs(
    status: Optional[str] = None,
    persona: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    List recent persona jobs for observability and debugging.
    
    Args:
        status: Filter by status ("pending", "running", "complete", "failed")
        persona: Filter by persona ("architect", "security", etc.)
        limit: Max number of jobs to return (default 10)
    
    Returns:
        {
            "jobs": [
                {
                    "job_id": "a7f3c9d2...",
                    "persona": "architect",
                    "status": "complete",
                    "task": "Review API design...",
                    "created_at": "2025-10-06T14:30:00",
                    "duration_seconds": 42
                },
                ...
            ],
            "total_count": 25,
            "filtered_count": 10
        }
    """
```

---

### Tool 9: cancel_persona_job

**Purpose:** Cancel a running persona job

**Signature:**
```python
@mcp.tool()
async def cancel_persona_job(job_id: str) -> Dict[str, Any]:
    """
    Cancel a running persona job.
    
    The job will be marked as cancelled and the worker will stop processing.
    Partial results (if any) will be saved.
    
    Args:
        job_id: Job identifier to cancel
    
    Returns:
        {
            "status": "cancelled",
            "job_id": "a7f3c9d2...",
            "partial_result": "..." or None,
            "message": "Job cancelled after 15 seconds"
        }
    """
```

---

### Tool 10: persona_database_stats

**Purpose:** Get persona job database statistics and health metrics

**Signature:**
```python
@mcp.tool()
async def persona_database_stats() -> Dict[str, Any]:
    """
    Get persona job database statistics.
    
    Returns:
        {
            "database_size_mb": 45.3,
            "total_jobs": 1234,
            "jobs_by_status": {
                "complete": 1100,
                "failed": 23,
                "running": 3,
                "pending": 8
            },
            "oldest_job_days": 28.3,
            "next_cleanup": "2025-10-07T03:00:00",
            "cleanup_recommendation": "healthy"
        }
    """
```

---

### Tool 11: reset_persona_jobs

**Purpose:** Emergency database reset (delete all job history)

**Signature:**
```python
@mcp.tool()
async def reset_persona_jobs(confirm: bool = False) -> Dict[str, Any]:
    """
    DANGER: Delete all persona job history.
    
    This will remove all job records from the database.
    Use this if automatic cleanup is insufficient or database is corrupted.
    
    Args:
        confirm: Must be True to proceed (safety check)
    
    Returns:
        {
            "status": "reset",
            "jobs_deleted": 1523,
            "space_freed_mb": 48.3,
            "message": "All job history deleted"
        }
    """
```

---

## 💾 DATA MODELS

### Model 1: PersonaConfig

```python
@dataclass
class PersonaConfig:
    """Configuration for a persona."""
    name: str                  # e.g., "Software Architect"
    identifier: str            # e.g., "architect"
    system_prompt: str         # Optimized prompt (≤1,500 tokens)
    standard_directory: str    # e.g., "architecture"
    mcp_tool_name: str        # e.g., "invoke_architect"
    priority: str             # "core" or "specialist"
```

### Model 2: StandardProposal

```python
@dataclass
class StandardProposal:
    """A proposed standard awaiting Human approval."""
    id: str                    # Unique ID
    domain: str               # e.g., "architecture", "data"
    topic: str                # e.g., "api-conventions"
    content: str              # Markdown content
    proposed_by: str          # Persona that proposed it
    status: str               # "draft", "approved", "rejected"
    feedback: Optional[str]   # Human feedback
    created_at: datetime
    updated_at: datetime
```

### Model 3: JobState

```python
@dataclass
class JobState:
    """State of an async persona job."""
    id: str                          # UUID
    persona: str                     # e.g., "architect"
    task: str                        # User's request
    context: Optional[str]           # File contents, etc.
    status: str                      # "pending" | "running" | "complete" | "failed" | "cancelled"
    priority: str                    # "low" | "normal" | "high"
    
    # Progress tracking
    progress_phase: Optional[str]    # "initializing" | "searching" | "analyzing" | "generating"
    progress_percent: int            # 0-100
    progress_message: Optional[str]  # Human-readable status
    progress_eta_seconds: Optional[int]  # Estimated seconds remaining
    
    # Results
    result: Optional[str]            # Final persona output
    error: Optional[str]             # Error message if failed
    partial_result: Optional[str]    # Partial output if interrupted
    
    # Timestamps
    created_at: float                # Unix timestamp
    started_at: Optional[float]      # When worker picked up
    completed_at: Optional[float]    # When finished
    
    # Observability
    tool_calls_made: int             # Number of tool calls
    tokens_input: Optional[int]
    tokens_output: Optional[int]
    duration_seconds: Optional[float]
```

### Model 4: ProgressUpdate

```python
@dataclass
class ProgressUpdate:
    """Progress update for a running job."""
    phase: str                       # "initializing" | "searching" | "analyzing" | "generating"
    percent_complete: int            # 0-100
    message: str                     # Human-readable status
    eta_seconds: Optional[int]       # Estimated seconds remaining
    tool_calls_completed: int        # Number of tool calls made so far
    elapsed_seconds: float           # Time since job started
```

### Model 5: StandardMetadata

```python
@dataclass
class StandardMetadata:
    """Metadata for a project standard."""
    file_path: str            # e.g., "architecture/api-conventions.md"
    domain: str               # e.g., "architecture"
    topic: str                # e.g., "api-conventions"
    created_by: str           # Persona that created it
    approved_by: str          # Human who approved it
    created_at: datetime
    last_updated: datetime
    query_count: int          # How many times queried by main agent
    tags: List[str]           # Searchable tags
```

---

## 🔄 WORKFLOW / PROCESS FLOW

### Workflow 1: Standards Population Flow

```
1. Human requests persona review
   Example: "@architect review this API design"

2. Persona analyzes code/design
   - Reviews for patterns, issues, opportunities
   - Identifies pattern worth standardizing

3. Persona proposes standard
   - "I notice a consistent API pattern. May I document it?"
   - Waits for Human approval

4. Human responds
   - Option A: "Yes" → Continue to step 5
   - Option B: "Yes, but add X" → Persona updates, go to step 5
   - Option C: "No" → Stop, continue review

5. Persona generates standard draft
   - Uses standard template (context, pattern, examples, anti-patterns)
   - Presents to Human for review

6. Human reviews draft
   - Option A: Approves → Go to step 7
   - Option B: Requests changes → Persona updates, repeat step 6
   - Option C: Rejects → Stop

7. Persona creates standard file
   - Writes to .agent-os/standards/{domain}/{topic}.md
   - Informs Human: "Standard created at {path}"

8. File watcher detects new file
   - Triggers incremental RAG index rebuild
   - Standard indexed and searchable within 30 seconds

9. Main agent queries standard
   - Future relevant queries return this standard
   - Code generation follows this pattern
```

---

### Workflow 2: Main Agent Standards Query Flow

```
1. User asks question
   Example: "How should I structure this API endpoint?"

2. Main Cursor agent processes query
   - Identifies this is about API structure
   - Calls search_standards("API endpoint structure patterns")

3. MCP server performs RAG search
   - Query embedding generated
   - Vector similarity search in LanceDB
   - Returns top 3-5 chunks

4. Chunks returned to main agent
   Example chunks:
   - architecture/api-conventions.md (relevance: 0.95)
   - development/error-handling.md (relevance: 0.87)
   - testing/test-conventions.md (relevance: 0.82)

5. Main agent generates response
   - Incorporates project-specific patterns from standards
   - Provides code example following standards
   - Cites which standards were used

6. User receives project-aware answer
   - Directly usable (matches project conventions)
   - No need to adapt generic advice
   - Consistent with existing codebase
```

---

## 🔐 SECURITY CONSIDERATIONS

### Authentication
- Personas run within Cursor's security context
- No separate authentication required
- Uses existing Cursor user identity

### Authorization
- Personas can read project files (via MCP)
- Personas can propose standards (write requires Human approval)
- Main agent can read standards (via RAG)
- File system permissions managed by OS

### Data Protection
- Standards files stored in project repo (user controls)
- No external data transmission (unless user's LLM API)
- Sensitive data: Use references, not actual secrets in standards
- Example: "Use Vault at $VAULT_ADDR/secrets/db" not "password=abc123"

### Secrets Management
- Standards must never contain hardcoded secrets
- Use placeholders: `$DATABASE_URL`, `$API_KEY`
- Reference secure storage: "Stored in AWS Secrets Manager"
- Persona prompts check for secrets, warn user

---

## ⚡ PERFORMANCE CONSIDERATIONS

### Expected Load
- Persona invocations: 10-50 per day per developer
- Standards creation: 5-10 per month
- Main agent queries: 100-500 per day per developer
- File watcher events: 5-10 per day

### Performance Targets
- **Persona Response Latency**: <5 seconds (first response)
- **Standards Indexing Time**: <30 seconds (file created → searchable)
- **RAG Query Latency**: <500ms (search_standards call)
- **Token Efficiency**: 90% context reduction (50KB → 5KB)

### Optimization Strategies
- Persona prompts optimized to ≤1,500 tokens (65%+ reduction)
- Incremental index updates (not full rebuild)
- Top-K retrieval (3-5 chunks, not all)
- Local embeddings (no API calls for indexing)
- Caching: RAG results cached for identical queries (5 min TTL)

---

## 🧪 TESTING STRATEGY

### Unit Testing
- Persona prompt validation (format, token count)
- Standard file format validation
- RAG query/response format
- MCP tool signatures

### Integration Testing
- End-to-end persona invocation flow
- Standards creation flow (propose → approve → create → index)
- Main agent queries standards (mock MCP calls)
- File watcher triggers index rebuild

### End-to-End Testing
- Real persona invocation in test project
- Create actual standard, verify indexing
- Main agent queries and uses standard
- Measure: proposal → approval → indexed → queried (full cycle)

---

## 🔌 INTEGRATION POINTS

### Integration 1: Cursor IDE
**Purpose:** Persona invocation UI  
**Method:** Natural language `@persona` syntax  
**Error Handling:** Fallback to main agent if persona unavailable

### Integration 2: MCP Server
**Purpose:** Tool registration and execution  
**Method:** Python MCP SDK, tool decorators  
**Error Handling:** Return error message to user if tool fails

### Integration 3: LanceDB
**Purpose:** Vector storage and search  
**Method:** Existing RAG engine  
**Error Handling:** Graceful degradation (return generic advice if RAG unavailable)

### Integration 4: Git
**Purpose:** Version control for standards  
**Method:** Standards are regular files in repo  
**Error Handling:** User resolves merge conflicts manually

---

## 🚀 DEPLOYMENT STRATEGY

### Deployment Method
- Update MCP server code (add persona tools)
- Deploy persona prompts to `mcp_server/personas/`
- No database migrations needed
- No service downtime required

### Rollout Plan
1. **Phase 1**: Deploy 2 core personas (Architect, Engineer) - Week 1
2. **Phase 2**: Deploy remaining 5 core personas - Week 2
3. **Phase 3**: Enable standards population - Week 3
4. **Phase 4**: Add specialist personas (on-demand) - Week 4+

### Rollback Plan
- Revert MCP server to previous version
- Disable persona tools via feature flag
- Standards files remain (no data loss)
- Main agent falls back to generic advice

---

**Next**: Review [Implementation Tasks](tasks.md) for phased breakdown and [Implementation Details](implementation.md) for code guidance
