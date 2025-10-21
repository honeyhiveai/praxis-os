# Async Persona Execution Architecture - Background Jobs with Polling

**Date:** 2025-10-06  
**Status:** Design Phase - Architecture Selection  
**Related:** persona-llm-communication.md, infrastructure-architecture.md

---

## 🎯 EXECUTIVE SUMMARY

### Problem Statement

The persona system requires long-running LLM operations that can take 30-120 seconds:
- **MCP Tool Timeout Risk**: Cursor/MCP may timeout on operations >30s
- **No Streaming in MCP**: Protocol is request-response, no incremental updates
- **Multi-Persona Bottleneck**: Sequential invocations multiply wait times
- **Poor User Experience**: No progress feedback during execution

### Solution Overview

Implement **async background job architecture** with polling-based progress updates:
- Job queue with persistent SQLite state
- Background worker pool executing persona LLM calls
- Real-time progress tracking with ETA
- MCP polling tools for status queries
- Zero timeout risk (tools return <1s)

### Key Benefits

| Benefit | Impact |
|---------|--------|
| **Zero Timeout Risk** | Tools return immediately, workers run indefinitely |
| **Progress Visibility** | Users see "Searching standards... 40%" updates |
| **Concurrent Execution** | 3+ personas can run simultaneously |
| **Scalability** | Supports 5+ minute comprehensive reviews |
| **Observability** | Job history, metrics, token tracking |
| **Reliability** | Graceful error handling, partial results |

---

## 📊 ARCHITECTURE OVERVIEW

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: User Request                                             │
│ User in Cursor: "@architect review this 500-line service"       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Main Cursor Agent Calls MCP Tool                        │
│ invoke_architect(task="review...", context="<file>")            │
└────────────────────┬────────────────────────────────────────────┘
                     │ MCP call via stdio
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: MCP Server Creates Job (< 50ms)                         │
│ - Generate job_id: "a7f3c9d2-..."                               │
│ - Insert into persona_jobs table (status: pending)              │
│ - Return immediately to Cursor                                   │
│                                                                   │
│ Returns: {status: "started", job_id: "a7f3...", eta: 45s}       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Background Worker Picks Up Job                          │
│ - Worker thread detects pending job                              │
│ - Update status: running                                         │
│ - Load architect persona prompt                                  │
│ - Initialize LLM client                                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Persona Execution with Progress Updates                 │
│                                                                   │
│ 0s:  Update progress: "Initializing architect..."               │
│ 2s:  Call search_standards("API patterns")                      │
│ 3s:  Update progress: "Searching standards... 30%"              │
│ 8s:  LLM analyzes results                                        │
│ 10s: Update progress: "Analyzing code... 60%"                   │
│ 20s: Call search_standards("concurrency patterns")              │
│ 22s: Update progress: "Analyzing patterns... 75%"               │
│ 35s: LLM generates final review                                  │
│ 40s: Update progress: "Generating review... 95%"                │
│ 45s: Complete! Store result in DB                               │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: Cursor Agent Polls for Status (every 5s)                │
│                                                                   │
│ Poll 1 (5s):  check_persona_job("a7f3...")                      │
│               → {status: "running", progress: "Searching... 30%"}│
│                                                                   │
│ Poll 2 (10s): check_persona_job("a7f3...")                      │
│               → {status: "running", progress: "Analyzing... 60%"}│
│                                                                   │
│ Poll 3 (15s): check_persona_job("a7f3...")                      │
│               → {status: "running", progress: "Analyzing... 75%"}│
│                                                                   │
│ Poll 4 (50s): check_persona_job("a7f3...")                      │
│               → {status: "complete", result: "🎯 Review:\n..."}  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: Display Results to User                                 │
│ "✅ Architect review complete! (took 45 seconds, 2 tool calls)" │
│ [Shows full review with recommendations]                        │
└─────────────────────────────────────────────────────────────────┘
```


### Component Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        MCP Server Process                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────┐         ┌──────────────────┐               │
│  │  MCP Tools      │────────>│  Job Queue       │               │
│  │  (FastMCP)      │         │  Manager         │               │
│  │                 │         │                  │               │
│  │ - invoke_*()    │         │ - create_job()   │               │
│  │ - check_job()   │<────────│ - get_job()      │               │
│  │ - list_jobs()   │         │ - update_prog()  │               │
│  │ - cancel_job()  │         │                  │               │
│  └─────────────────┘         └────────┬─────────┘               │
│           │                           │                          │
│           │                           │                          │
│           │                  ┌────────▼─────────┐               │
│           │                  │  SQLite DB       │               │
│           │                  │  (Job State)     │               │
│           │                  │                  │               │
│           │                  │ - persona_jobs   │               │
│           │                  │ - job history    │               │
│           │                  └────────┬─────────┘               │
│           │                           │                          │
│           │                           │                          │
│           │                  ┌────────▼─────────┐               │
│           │                  │  Worker Pool     │               │
│           │                  │  (3 threads)     │               │
│           │                  │                  │               │
│           │                  │ Worker 1 ────────┼──> Persona    │
│           │                  │ Worker 2 ────────┼──> Executor   │
│           │                  │ Worker 3 ────────┼──> (LLM)      │
│           │                  └──────────────────┘               │
│           │                                                      │
│           │                  ┌──────────────────┐               │
│           └─────────────────>│  Persona         │               │
│                              │  Executor        │               │
│                              │                  │               │
│                              │ - Load prompt    │               │
│                              │ - Call LLM       │──> Anthropic  │
│                              │ - Tool use loop  │<── API        │
│                              │ - Progress track │               │
│                              └──────────────────┘               │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

### Job State Machine

```
                    ┌──────────┐
                    │ PENDING  │  (Job created, waiting for worker)
                    └────┬─────┘
                         │
                         │ Worker picks up
                         ↓
                    ┌──────────┐
         ┌──────────┤ RUNNING  │  (Worker executing persona)
         │          └────┬─────┘
         │               │
         │               ├─> Progress updates (in-place)
         │               │
         │               ├─> Success
         │               │   ↓
    Cancel│          ┌────────────┐
    Request│          │ COMPLETE   │  (Result stored, ready for retrieval)
         │          └────────────┘
         │               │
         │               ├─> Timeout/Error
         │               │   ↓
         │          ┌────────────┐
         │          │  FAILED    │  (Error stored, partial result if any)
         │          └────────────┘
         │
         ↓
    ┌────────────┐
    │ CANCELLED  │  (User cancelled job)
    └────────────┘
```

---

## 🏗️ COMPONENTS DESIGN

### 1. Job Queue Manager

**File:** `mcp_server/job_manager.py`

**Responsibilities:**
- Create job entries with unique UUIDs
- Provide thread-safe job state access
- Queue pending jobs for workers
- Implement job expiration and cleanup
- Query job history

**Core API:**

```python
class JobManager:
    def create_job(
        self,
        persona: str,
        task: str,
        context: Optional[str] = None,
        priority: str = "normal"
    ) -> str:
        """
        Create new persona job.
        
        Returns:
            job_id (UUID string)
        """
    
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """
        Get job state (thread-safe).
        
        Returns:
            {
                "id": "uuid",
                "persona": "architect",
                "status": "running",
                "progress": {...},
                "result": "..." or None,
                ...
            }
        """
    
    def update_progress(
        self,
        job_id: str,
        phase: str,
        percent: int,
        message: str,
        eta_seconds: Optional[int] = None
    ) -> None:
        """Update job progress (called by worker)."""
    
    def complete_job(
        self,
        job_id: str,
        result: str,
        tokens_used: Dict[str, int]
    ) -> None:
        """Mark job complete and store result."""
    
    def fail_job(
        self,
        job_id: str,
        error: str,
        partial_result: Optional[str] = None
    ) -> None:
        """Mark job failed with error."""
    
    def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """List recent jobs for observability."""
    
    def expire_old_jobs(self, older_than_hours: int = 168) -> int:
        """Delete jobs older than N hours (default 7 days)."""
```

**Storage: SQLite Database**

Location: `.agent-os/.cache/persona_jobs.db`

Schema:
```sql
CREATE TABLE persona_jobs (
    -- Identity
    id TEXT PRIMARY KEY,           -- UUID
    persona TEXT NOT NULL,         -- "architect", "security", etc.
    
    -- Request
    task TEXT NOT NULL,            -- User's task description
    context TEXT,                  -- Optional file contents (can be large)
    priority TEXT DEFAULT 'normal',-- "low" | "normal" | "high"
    
    -- State
    status TEXT NOT NULL,          -- "pending" | "running" | "complete" | "failed" | "cancelled"
    
    -- Progress (updated during execution)
    progress_phase TEXT,           -- "searching" | "analyzing" | "generating"
    progress_percent INTEGER DEFAULT 0,
    progress_message TEXT,
    progress_eta_seconds INTEGER,
    
    -- Results
    result TEXT,                   -- Final persona output (can be large)
    error TEXT,                    -- Error message if failed
    partial_result TEXT,           -- Partial output if interrupted
    
    -- Timestamps
    created_at REAL NOT NULL,      -- Unix timestamp
    started_at REAL,               -- When worker picked up
    completed_at REAL,             -- When finished
    
    -- Observability
    tool_calls_made INTEGER DEFAULT 0,
    tokens_input INTEGER,
    tokens_output INTEGER,
    duration_seconds REAL,
    
    -- Cleanup
    expires_at REAL                -- Auto-delete after retention period
);

CREATE INDEX idx_status ON persona_jobs(status);
CREATE INDEX idx_created_at ON persona_jobs(created_at DESC);
CREATE INDEX idx_expires_at ON persona_jobs(expires_at);
CREATE INDEX idx_persona ON persona_jobs(persona);
```

**Concurrency Control:**
- SQLite with WAL (Write-Ahead Logging) mode for concurrent reads
- Row-level locking for job updates
- Atomic status transitions with SQL transactions


### 2. Background Worker Pool

**File:** `mcp_server/background_worker.py`

**Responsibilities:**
- Monitor job queue for pending jobs
- Execute persona invocations asynchronously
- Update progress during execution
- Handle errors gracefully
- Coordinate across multiple workers

**Design:**

```python
class WorkerPool:
    def __init__(
        self,
        job_manager: JobManager,
        persona_executor: PersonaExecutor,
        num_workers: int = 3
    ):
        """Initialize worker pool with configurable size."""
        self.workers: List[WorkerThread] = []
        self.shutdown_event = threading.Event()
    
    def start(self) -> None:
        """Start all worker threads."""
        for i in range(self.num_workers):
            worker = WorkerThread(
                worker_id=i,
                job_manager=self.job_manager,
                persona_executor=self.persona_executor,
                shutdown_event=self.shutdown_event
            )
            worker.start()
            self.workers.append(worker)
    
    def shutdown(self) -> None:
        """Gracefully shutdown all workers."""
        self.shutdown_event.set()
        for worker in self.workers:
            worker.join(timeout=30)


class WorkerThread(threading.Thread):
    def run(self) -> None:
        """Main worker loop."""
        while not self.shutdown_event.is_set():
            # Check for pending jobs
            job = self.job_manager.get_next_pending_job(
                worker_id=self.worker_id
            )
            
            if job is None:
                # No jobs available, sleep briefly
                time.sleep(1)
                continue
            
            # Execute job
            try:
                self.execute_job(job)
            except Exception as e:
                logger.error(f"Worker {self.worker_id} failed: {e}")
                self.job_manager.fail_job(
                    job["id"],
                    error=str(e)
                )
    
    def execute_job(self, job: Dict[str, Any]) -> None:
        """Execute a single persona job."""
        job_id = job["id"]
        
        # Mark as running
        self.job_manager.update_job_status(job_id, "running")
        
        # Execute persona with progress callbacks
        result = self.persona_executor.invoke(
            persona=job["persona"],
            task=job["task"],
            context=job.get("context"),
            progress_callback=lambda **kwargs: self.job_manager.update_progress(
                job_id, **kwargs
            )
        )
        
        # Mark complete
        self.job_manager.complete_job(
            job_id,
            result=result["output"],
            tokens_used=result["tokens"]
        )
```

**Work Distribution Strategy:**
- Priority queue: High priority jobs processed first
- FIFO within priority level
- Workers poll database for next job (simple, no coordination needed)
- Advisory locks prevent duplicate pickup

**Configuration:** `.agent-os/config.json`
```json
{
  "personas": {
    "worker_pool_size": 3,
    "job_timeout_seconds": 300,
    "max_retries": 2
  }
}
```

### 3. Persona Executor (Async-Aware)

**File:** `mcp_server/persona_executor.py`

**Responsibilities:**
- Load persona system prompts
- Invoke Anthropic LLM with tool use
- Report progress at key checkpoints
- Handle streaming from Anthropic SDK
- Provide structured output

**Enhanced with Progress Tracking:**

```python
class PersonaExecutor:
    def invoke(
        self,
        persona: str,
        task: str,
        context: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Invoke persona with progress tracking.
        
        Args:
            persona: Persona identifier ("architect", "security", etc.)
            task: User's request
            context: Optional file contents
            progress_callback: Function to call with progress updates
                             progress_callback(phase, percent, message, eta)
        
        Returns:
            {
                "output": "Final review text",
                "tokens": {"input": N, "output": M},
                "tool_calls": 3,
                "duration_seconds": 45.2
            }
        """
        start_time = time.time()
        
        # Load persona prompt
        if progress_callback:
            progress_callback(
                phase="initializing",
                percent=0,
                message=f"Initializing {persona} persona...",
                eta_seconds=None
            )
        
        system_prompt = load_persona_prompt(persona)
        
        # Build user message
        user_message = self._build_user_message(task, context)
        
        # Invoke LLM with agentic tool use loop
        messages = [{"role": "user", "content": user_message}]
        tool_calls_made = 0
        
        for turn in range(MAX_TOOL_USE_TURNS):
            if progress_callback:
                # Estimate progress based on turn
                percent = min(90, 10 + (turn * 20))
                eta = self._estimate_eta(start_time, percent)
                
                progress_callback(
                    phase="analyzing" if turn > 0 else "searching",
                    percent=percent,
                    message=f"Processing (turn {turn+1}/{MAX_TOOL_USE_TURNS})...",
                    eta_seconds=eta
                )
            
            # Call LLM (with streaming)
            response = await self.llm_client.messages.create(
                model="claude-sonnet-4-20250514",
                system=system_prompt,
                messages=messages,
                tools=self._get_available_tools(),
                max_tokens=4096
            )
            
            # Check if LLM wants to use tools
            if not self._has_tool_use(response):
                # Final response received
                break
            
            # Execute tool calls
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_calls_made += 1
                    
                    if progress_callback:
                        progress_callback(
                            phase="searching",
                            percent=min(80, 20 + (tool_calls_made * 15)),
                            message=f"Searching standards ({block.name})...",
                            eta_seconds=self._estimate_eta(start_time, 60)
                        )
                    
                    result = self._execute_tool(block.name, block.input)
                    tool_results.append(result)
            
            # Add tool results to conversation
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        
        # Final generation phase
        if progress_callback:
            progress_callback(
                phase="generating",
                percent=95,
                message="Generating final review...",
                eta_seconds=5
            )
        
        # Extract final text
        final_text = self._extract_text(response)
        
        duration = time.time() - start_time
        
        return {
            "output": final_text,
            "tokens": {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens
            },
            "tool_calls": tool_calls_made,
            "duration_seconds": duration
        }
    
    def _estimate_eta(self, start_time: float, percent_complete: int) -> int:
        """Estimate seconds remaining based on current progress."""
        if percent_complete <= 0:
            return None
        
        elapsed = time.time() - start_time
        estimated_total = elapsed / (percent_complete / 100)
        remaining = estimated_total - elapsed
        
        return max(0, int(remaining))
```

**Progress Checkpoints:**
1. **Initializing** (0%): Loading persona prompt
2. **Searching** (10-50%): Calling search_standards() tools
3. **Analyzing** (50-80%): LLM processing results
4. **Generating** (80-100%): Final review generation

### 4. Progress Reporter

**Structured Progress Format:**

```python
@dataclass
class ProgressUpdate:
    phase: str                    # "initializing" | "searching" | "analyzing" | "generating"
    percent_complete: int         # 0-100
    message: str                  # Human-readable status
    eta_seconds: Optional[int]    # Estimated seconds remaining
    tool_calls_completed: int     # Number of tool calls made so far
    elapsed_seconds: float        # Time since job started
```

**Example Progress Sequence:**

```json
// T=0s
{
  "phase": "initializing",
  "percent_complete": 0,
  "message": "Initializing architect persona...",
  "eta_seconds": null,
  "tool_calls_completed": 0,
  "elapsed_seconds": 0
}

// T=5s
{
  "phase": "searching",
  "percent_complete": 30,
  "message": "Searching standards (search_standards)...",
  "eta_seconds": 35,
  "tool_calls_completed": 1,
  "elapsed_seconds": 5
}

// T=15s
{
  "phase": "analyzing",
  "percent_complete": 60,
  "message": "Analyzing code patterns...",
  "eta_seconds": 20,
  "tool_calls_completed": 2,
  "elapsed_seconds": 15
}

// T=40s
{
  "phase": "generating",
  "percent_complete": 95,
  "message": "Generating final review...",
  "eta_seconds": 3,
  "tool_calls_completed": 3,
  "elapsed_seconds": 40
}
```


---

## 🔧 MCP TOOLS API DESIGN

### Tool 1: `invoke_architect()` (and all personas)

**Purpose:** Start persona review as background job

**Signature:**
```python
@mcp.tool()
async def invoke_architect(
    task: str,
    context: Optional[str] = None,
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    Invoke Software Architect persona for architecture review.
    
    This starts a background job that may take 30-120 seconds.
    Use check_persona_job() to poll for progress and results.
    
    Args:
        task: What to review/design (e.g., "review this API design")
        context: Optional file contents or additional context
        priority: "low" | "normal" | "high" (affects queue priority)
    
    Returns:
        {
            "status": "started",
            "job_id": "a7f3c9d2-1234-5678-90ab-cdef12345678",
            "persona": "architect",
            "estimated_duration_seconds": 45,
            "poll_command": "check_persona_job('a7f3c9d2...')",
            "message": "Architect review started. Polling for progress..."
        }
    
    Example:
        invoke_architect(
            task="Review the architecture of our payment processing system",
            context="<file contents>"
        )
    """
```

**Implementation:**
```python
async def invoke_architect(
    task: str,
    context: Optional[str] = None,
    priority: str = "normal"
) -> Dict[str, Any]:
    # Create job via job manager
    job_id = job_manager.create_job(
        persona="architect",
        task=task,
        context=context,
        priority=priority
    )
    
    # Estimate duration based on context size
    estimated_duration = _estimate_duration(len(context or ""))
    
    return {
        "status": "started",
        "job_id": job_id,
        "persona": "architect",
        "estimated_duration_seconds": estimated_duration,
        "poll_command": f"check_persona_job('{job_id}')",
        "message": "Architect review started. Polling for progress..."
    }
```

**Similar Tools:**
- `invoke_engineer(task, context, priority)` - Software Engineer
- `invoke_data(task, context, priority)` - Data Engineer
- `invoke_qa(task, context, priority)` - QA Engineer
- `invoke_security(task, context, priority)` - Security Engineer
- `invoke_sre(task, context, priority)` - SRE

### Tool 2: `check_persona_job()`

**Purpose:** Poll for job status and progress

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
            "result": "🎯 Architecture Review:\n\n## Strengths\n...",
            "duration_seconds": 42,
            "tool_calls_made": 3,
            "tokens_used": {"input": 2500, "output": 1800}
        }
        
        If failed:
        {
            "status": "failed",
            "persona": "architect",
            "error": "LLM API timeout after 120s",
            "partial_result": "🎯 Architecture Review:\n\n(incomplete)",
            "elapsed_seconds": 120
        }
    
    Example:
        check_persona_job("a7f3c9d2-1234-5678-90ab-cdef12345678")
    """
```

**Implementation:**
```python
async def check_persona_job(job_id: str) -> Dict[str, Any]:
    job = job_manager.get_job(job_id)
    
    if job is None:
        return {
            "status": "not_found",
            "error": f"Job {job_id} not found (may have expired)"
        }
    
    base_response = {
        "status": job["status"],
        "persona": job["persona"],
        "created_at": job["created_at"]
    }
    
    if job["status"] == "pending":
        return {
            **base_response,
            "message": "Job queued, waiting for worker..."
        }
    
    elif job["status"] == "running":
        elapsed = time.time() - job["started_at"]
        
        return {
            **base_response,
            "progress": {
                "phase": job["progress_phase"],
                "percent_complete": job["progress_percent"],
                "message": job["progress_message"],
                "eta_seconds": job["progress_eta_seconds"],
                "tool_calls_completed": job["tool_calls_made"]
            },
            "elapsed_seconds": elapsed
        }
    
    elif job["status"] == "complete":
        return {
            **base_response,
            "result": job["result"],
            "duration_seconds": job["duration_seconds"],
            "tool_calls_made": job["tool_calls_made"],
            "tokens_used": {
                "input": job["tokens_input"],
                "output": job["tokens_output"]
            }
        }
    
    elif job["status"] == "failed":
        return {
            **base_response,
            "error": job["error"],
            "partial_result": job.get("partial_result"),
            "elapsed_seconds": time.time() - job["started_at"]
        }
```

### Tool 3: `list_persona_jobs()`

**Purpose:** List recent jobs for observability and debugging

**Signature:**
```python
@mcp.tool()
async def list_persona_jobs(
    status: Optional[str] = None,
    persona: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    List recent persona jobs for observability.
    
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
    
    Example:
        list_persona_jobs(status="complete", limit=5)
        list_persona_jobs(persona="architect")
    """
```

### Tool 4: `cancel_persona_job()`

**Purpose:** Cancel a running job

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
    
    Example:
        cancel_persona_job("a7f3c9d2-1234-5678-90ab-cdef12345678")
    """
```

**Implementation:**
```python
async def cancel_persona_job(job_id: str) -> Dict[str, Any]:
    job = job_manager.get_job(job_id)
    
    if job is None:
        return {"status": "not_found", "error": "Job not found"}
    
    if job["status"] not in ["pending", "running"]:
        return {
            "status": "already_finished",
            "error": f"Job already in {job['status']} state"
        }
    
    # Mark as cancelled (worker will detect and stop)
    job_manager.cancel_job(job_id)
    
    # Get partial result if any
    partial = job.get("partial_result")
    
    elapsed = time.time() - job["created_at"]
    
    return {
        "status": "cancelled",
        "job_id": job_id,
        "partial_result": partial,
        "message": f"Job cancelled after {elapsed:.1f} seconds"
    }
```


---

## 🎨 DESIGN ALTERNATIVES CONSIDERED

### Alternative 1: Synchronous Only (REJECTED)

**Approach:** Simple blocking `invoke_architect()` calls that wait for LLM response

**Pros:**
- Simplest implementation (~200 lines)
- No state management or database needed
- Immediate results when successful
- Familiar request-response pattern

**Cons:**
- ❌ **Timeout Risk**: 30-120s operations likely exceed Cursor/MCP timeouts
- ❌ **No Progress Feedback**: User stares at "Loading..." with no updates
- ❌ **Poor UX for Long Operations**: 60+ second waits feel like frozen UI
- ❌ **Blocks Cursor**: User can't do anything else while waiting
- ❌ **No Observability**: Can't see what persona is doing
- ❌ **No Recovery**: If timeout occurs, all progress lost

**Example Failure Scenario:**
```
User: "@architect comprehensive review of payment service"
[Cursor shows "Loading..."]
[30 seconds pass... still "Loading..."]
[User thinks: "Is this broken? Should I cancel?"]
[45 seconds... still "Loading..."]
[60 seconds... TIMEOUT ERROR]
User: "It timed out, all that work wasted."
```

**Verdict:** ❌ Unacceptable UX for production use. Timeouts would frustrate users and undermine trust in personas.

---

### Alternative 2: Streaming via Server-Sent Events (REJECTED)

**Approach:** Implement custom streaming protocol over MCP using SSE or WebSockets

**Pros:**
- Real-time token streaming (best possible UX)
- No polling overhead
- Feels like ChatGPT streaming experience
- Can show partial results immediately

**Cons:**
- ❌ **Not Supported by MCP Protocol**: MCP spec is request-response only
- ❌ **Requires Custom Cursor Extension**: Would need to modify Cursor itself
- ❌ **Breaking MCP Compatibility**: Violates standard, may break with Cursor updates
- ❌ **Significant Engineering Effort**: ~2000+ lines, complex WebSocket handling
- ❌ **Maintenance Burden**: Custom protocol requires ongoing support

**Technical Blockers:**
- MCP stdio transport doesn't support bidirectional streaming
- FastMCP library has no streaming primitives
- Cursor IDE would need custom integration

**Verdict:** ❌ Technically infeasible without breaking MCP standards. Engineering cost too high.

---

### Alternative 3: Hybrid Fast Path + Background Fallback (CONSIDERED)

**Approach:** Try synchronous first (30s timeout), automatically fall back to async if slow

**Pros:**
- ✅ Simple cases get immediate results (no polling needed)
- ✅ Complex cases don't timeout (graceful degradation)
- ✅ Single API surface (auto-selects mode)
- ✅ Best of both worlds for short operations

**Cons:**
- ⚠️ **Inconsistent UX**: Sometimes immediate, sometimes delayed (unpredictable)
- ⚠️ **User Confusion**: "Why did it poll this time but not last time?"
- ⚠️ **Complex Implementation**: Two code paths to maintain and test
- ⚠️ **Timeout Still Interrupts**: User experiences jarring transition mid-operation
- ⚠️ **Hard to Predict**: Can't reliably estimate if operation will be fast or slow

**Example Inconsistency:**
```
User: "@architect review small function"
→ [Returns immediately in 5s] ✓

User: "@architect review same function with more context"
→ [Timeout at 30s, switches to background, now polling] ⚠️
User: "Why is it different this time?"
```

**Verdict:** ⚠️ Viable alternative but creates unpredictable UX. Users prefer consistency over occasional speed gains.

---

### Alternative 4: Async Background Jobs with Polling (SELECTED ✅)

**Approach:** All persona invocations are async from the start, with polling for progress

**Pros:**
- ✅ **Predictable UX**: Users always know what to expect
- ✅ **Zero Timeout Risk**: Jobs return immediately, workers run indefinitely
- ✅ **Real-Time Progress**: Users see "Searching... 40%" updates every 5s
- ✅ **Simple Mental Model**: "Start job → Poll for progress → Get result"
- ✅ **Scalable**: Handles 5-minute comprehensive reviews as easily as 30s simple reviews
- ✅ **Observable**: Full job history and status tracking
- ✅ **Recoverable**: Can check status after network interruption
- ✅ **Future-Proof**: Foundation for notifications, job queues, distributed workers

**Cons:**
- ⚠️ Polling overhead (~5% of execution time, 1-2 extra API calls)
- ⚠️ More complex implementation (~800 lines vs 200 for sync)
- ⚠️ Small latency (<1s job creation overhead)
- ⚠️ Requires persistent state (SQLite database)

**Why These Cons Are Acceptable:**
- Polling overhead is negligible compared to 30-120s LLM operations
- Implementation complexity is one-time cost, UX benefit is permanent
- <1s latency is imperceptible when total operation is 30-60s
- SQLite is lightweight, reliable, and already used for state management

**Example Successful UX:**
```
User: "@architect comprehensive review of payment service"
Agent: "✓ Started architect review (job: a7f3c9d2)"
[5s later]  "Progress: Searching standards... 30% (~35s remaining)"
[10s later] "Progress: Analyzing patterns... 55% (~20s remaining)"
[15s later] "Progress: Analyzing code... 75% (~12s remaining)"
[20s later] "Progress: Generating review... 95% (~3s remaining)"
[25s later] "✅ Review complete! (took 25 seconds)"
[Shows full review]
```

**Verdict:** ✅ Best balance of reliability, UX, and scalability. Async-first is the correct choice.

---

## 🔍 WHY ASYNC-FIRST IS THE RIGHT CHOICE

### 1. Predictability Over Speed

**Design Principle:** Users prefer **consistent, predictable experiences** over **occasionally faster but unpredictable** ones.

- Sync with timeout: Fast 70% of time, breaks 30% of time → Bad
- Async with polling: Consistent 100% of time → Good

### 2. Progress Visibility Builds Trust

**Psychological Impact:**
- No feedback = User assumes it's broken
- Progress updates = User knows system is working
- ETA estimates = User can plan ("I'll grab coffee")

### 3. Handles Edge Cases Gracefully

**Scenarios that break sync:**
- Large codebase reviews (5+ minutes)
- Multiple tool calls (search_standards × 5)
- Complex analysis requiring deep thinking
- Network hiccups causing retries

**Async handles all gracefully:** Job keeps running regardless of complexity.

### 4. Foundation for Future Features

**Async architecture enables:**
- Job history ("Show my last 10 reviews")
- Job templates ("Repeat this review weekly")
- Distributed workers (scale across machines)
- Priority queues (urgent reviews first)
- Notifications ("Review complete while you were away")
- Analytics (token usage, average duration)

### 5. Industry Standard Pattern

**Similar implementations:**
- GitHub Actions (start workflow → poll status)
- AWS Lambda async invocations
- Kubernetes jobs
- CI/CD pipelines

Users already understand this pattern.

---

## 🔄 EXECUTION FLOW (DETAILED SCENARIOS)

### Scenario 1: Simple Async Invocation

**Setup:**
- User wants architect review of 200-line API service
- Expected duration: ~30 seconds
- 2 tool calls needed

**Step-by-Step Execution:**

```
T=0s: USER ACTION
----------------------------------------------
User in Cursor: "@architect review this API design"
Main agent sees task and decides to call invoke_architect()


T=0.1s: MCP TOOL CALL
----------------------------------------------
Cursor → MCP Server (stdio):
{
  "method": "tools/call",
  "params": {
    "name": "invoke_architect",
    "arguments": {
      "task": "Review this API design for payment processing",
      "context": "<200 lines of code>",
      "priority": "normal"
    }
  }
}


T=0.15s: JOB CREATION
----------------------------------------------
MCP Server:
1. Generate UUID: "a7f3c9d2-1234-5678-90ab-cdef12345678"
2. Insert into persona_jobs table:
   INSERT INTO persona_jobs (
     id, persona, task, context, status, priority, created_at
   ) VALUES (
     'a7f3c9d2...', 'architect', 'Review...', '<code>', 'pending', 'normal', 1696605000
   )
3. Estimate duration: ~35 seconds (based on context size)


T=0.2s: IMMEDIATE RETURN TO CURSOR
----------------------------------------------
MCP Server → Cursor:
{
  "status": "started",
  "job_id": "a7f3c9d2-1234-5678-90ab-cdef12345678",
  "persona": "architect",
  "estimated_duration_seconds": 35,
  "poll_command": "check_persona_job('a7f3c9d2...')",
  "message": "Architect review started. Polling for progress..."
}

Cursor displays: "✓ Started architect review (job: a7f3c9d2)"


T=1s: WORKER PICKS UP JOB
----------------------------------------------
Background Worker Thread #2:
1. Query: SELECT * FROM persona_jobs WHERE status='pending' LIMIT 1
2. Found job a7f3c9d2
3. Update: UPDATE persona_jobs SET status='running', started_at=1696605001 WHERE id='a7f3c9d2'
4. Load architect persona prompt from personas/architect.md
5. Initialize LLM client


T=2s: PERSONA STARTS EXECUTION
----------------------------------------------
Worker calls PersonaExecutor.invoke():
1. Update progress: phase='initializing', percent=0, message='Initializing architect...'
2. Build user message with task + context
3. Call Anthropic API:
   
   llm_client.messages.create(
     model="claude-sonnet-4-20250514",
     system="<architect persona prompt>",
     messages=[{"role": "user", "content": "Review this API..."}],
     tools=[search_standards, list_standards, read_standard]
   )


T=5s: CURSOR POLLS FOR STATUS (First Poll)
----------------------------------------------
Main Cursor agent calls check_persona_job("a7f3c9d2...")

MCP Server returns:
{
  "status": "running",
  "persona": "architect",
  "progress": {
    "phase": "initializing",
    "percent_complete": 5,
    "message": "Initializing architect persona...",
    "eta_seconds": 30,
    "tool_calls_completed": 0
  },
  "elapsed_seconds": 5
}

Cursor displays: "🔄 Architect working... (initializing, 5% done)"


T=7s: LLM DECIDES TO SEARCH STANDARDS
----------------------------------------------
Anthropic API returns (streaming):
{
  "role": "assistant",
  "content": [
    {"type": "text", "text": "I'll check the project's API design standards first."},
    {
      "type": "tool_use",
      "id": "toolu_123",
      "name": "search_standards",
      "input": {"query": "REST API design conventions"}
    }
  ]
}

Worker executes tool:
1. tool_calls_made += 1
2. Update progress: phase='searching', percent=25, message='Searching standards...'
3. Call rag_engine.search("REST API design conventions")
4. Returns: 3 relevant chunks from .agent-os/standards/


T=10s: CURSOR POLLS (Second Poll)
----------------------------------------------
check_persona_job("a7f3c9d2...")

Returns:
{
  "status": "running",
  "progress": {
    "phase": "searching",
    "percent_complete": 30,
    "message": "Searching standards (search_standards)...",
    "eta_seconds": 25,
    "tool_calls_completed": 1
  },
  "elapsed_seconds": 10
}

Cursor displays: "🔄 Architect working... (searching, 30% done, ~25s left)"


T=12s: LLM ANALYZES RESULTS
----------------------------------------------
Worker sends tool results back to LLM:
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_123",
      "content": "<search results>"
    }
  ]
}

Update progress: phase='analyzing', percent=50, message='Analyzing code patterns...'

LLM processes results (streaming internally)


T=15s: CURSOR POLLS (Third Poll)
----------------------------------------------
check_persona_job("a7f3c9d2...")

Returns:
{
  "status": "running",
  "progress": {
    "phase": "analyzing",
    "percent_complete": 60,
    "message": "Analyzing code patterns...",
    "eta_seconds": 15,
    "tool_calls_completed": 1
  },
  "elapsed_seconds": 15
}

Cursor displays: "🔄 Architect working... (analyzing, 60% done, ~15s left)"


T=20s: LLM SEARCHES AGAIN
----------------------------------------------
LLM requests another tool:
{
  "type": "tool_use",
  "name": "search_standards",
  "input": {"query": "authentication patterns"}
}

Worker executes: tool_calls_made += 1 (now 2)
Update progress: phase='searching', percent=70, message='Searching standards...'


T=20s: CURSOR POLLS (Fourth Poll)
----------------------------------------------
Returns progress: 75%, searching, ~10s left


T=25s: LLM GENERATES FINAL REVIEW
----------------------------------------------
LLM has all info, generates final review:

Update progress: phase='generating', percent=95, message='Generating review...'

LLM returns final text:
```
🎯 Architecture Review

## Strengths
- Clean REST API structure
- Proper error handling

## Concerns
⚠️ No authentication layer
⚠️ Missing rate limiting

## Recommendations
1. Implement JWT authentication (see: standards/architecture/auth-patterns.md)
2. Add rate limiting middleware
...
```


T=28s: JOB COMPLETION
----------------------------------------------
Worker:
1. Extract final text from LLM response
2. Calculate tokens: input=2500, output=1800
3. Calculate duration: 28 seconds
4. Update database:
   UPDATE persona_jobs SET
     status='complete',
     result='<review text>',
     completed_at=1696605028,
     duration_seconds=28,
     tool_calls_made=2,
     tokens_input=2500,
     tokens_output=1800,
     progress_percent=100
   WHERE id='a7f3c9d2'

Worker logs: "✓ Job a7f3c9d2 complete (28s, 2 tools, 4300 tokens)"


T=30s: CURSOR POLLS (Fifth Poll)
----------------------------------------------
check_persona_job("a7f3c9d2...")

Returns:
{
  "status": "complete",
  "persona": "architect",
  "result": "🎯 Architecture Review\n\n## Strengths\n...",
  "duration_seconds": 28,
  "tool_calls_made": 2,
  "tokens_used": {"input": 2500, "output": 1800}
}

Cursor displays:
"✅ Architect review complete! (took 28 seconds, 2 tool calls, 4.3K tokens)"
[Shows full review text]


T=30s: USER SEES RESULT
----------------------------------------------
User: "Great review! Exactly what I needed."
```

**Key Observations:**
- Total time: 28 seconds (well within limits)
- User saw 5 progress updates (every 5s)
- No timeout risk
- Full observability (tokens, tools, duration)


### Scenario 2: Multi-Persona Concurrent Execution

**Setup:**
- User wants architect + security + SRE reviews simultaneously
- Each takes 30-45 seconds
- Worker pool has 3 workers

**Execution:**

```
T=0s: User: "@architect @security @sre review this service"

T=0.2s: Main agent calls all 3 personas:
- invoke_architect() → job_id: "aaa..."
- invoke_security() → job_id: "bbb..."
- invoke_sre() → job_id: "ccc..."

All 3 jobs created in <1s total

T=1s: Workers pick up jobs:
- Worker #1 → architect (aaa)
- Worker #2 → security (bbb)
- Worker #3 → SRE (ccc)

All execute IN PARALLEL

T=5s, 10s, 15s...: Cursor polls all 3 jobs
Shows 3 progress bars:
"🔄 Architect: Analyzing... 60%"
"🔄 Security: Searching... 40%"  
"🔄 SRE: Analyzing... 55%"

T=32s: Architect completes first
T=38s: Security completes
T=45s: SRE completes

Total wall-clock time: 45s (vs 115s if sequential!)
```

**Key Benefit:** Concurrent execution saves ~70 seconds compared to sequential.

### Scenario 3: Job Failure and Recovery

**Setup:**
- User starts comprehensive review
- LLM API times out after 90 seconds
- Partial result generated

**Execution:**

```
T=0s: invoke_architect(task="Comprehensive review of entire codebase")

T=1s: Worker picks up, starts execution

T=5-85s: Progress updates every 5s (all normal)

T=90s: Anthropic API timeout exception
Worker catches exception:
1. Capture partial result (if LLM returned any text)
2. Update DB:
   UPDATE persona_jobs SET
     status='failed',
     error='Anthropic API timeout after 90s',
     partial_result='<partial review text>',
     completed_at=1696605090
   WHERE id='xyz'

T=95s: Cursor polls, gets failure status:
{
  "status": "failed",
  "error": "Anthropic API timeout after 90s",
  "partial_result": "🎯 Architecture Review\n\n(Review incomplete due to timeout)\n\n## Strengths (partial)\n- Good structure\n...",
  "elapsed_seconds": 90
}

Cursor displays:
"⚠️ Architect review failed (timeout after 90s)"
"Partial result available:"
[Shows partial review]
"Would you like to retry with extended timeout?"

User: "Yes, retry"
Agent: invoke_architect(task="...", priority="high")  // Retry
```

**Key Benefit:** User sees partial work, not complete loss. Can retry or adjust scope.

---

## 🚨 ERROR HANDLING & RESILIENCE

### Timeout Scenarios

#### 1. LLM API Timeout (120s hard limit)

**Detection:**
```python
try:
    response = await llm_client.messages.create(
        ...,
        timeout=httpx.Timeout(120.0, connect=5.0)
    )
except httpx.TimeoutError as e:
    # Capture partial result if available
    partial_result = self._extract_partial_result(e)
    
    job_manager.fail_job(
        job_id,
        error="LLM API timeout after 120s",
        partial_result=partial_result
    )
```

**User Experience:**
- Error message explains timeout
- Partial result shown (if any)
- Option to retry with reduced scope

#### 2. Worker Thread Crash

**Detection:**
- Worker watchdog thread monitors last heartbeat
- If worker silent for >60s, assume crashed
- Mark stale jobs as failed on next worker start

**Recovery:**
```python
def cleanup_stale_jobs():
    """Called on MCP server startup."""
    stale_jobs = db.query("""
        SELECT id FROM persona_jobs
        WHERE status='running'
        AND started_at < (current_timestamp - 300)  -- 5 min ago
    """)
    
    for job in stale_jobs:
        job_manager.fail_job(
            job["id"],
            error="Worker crashed or server restarted"
        )
```

#### 3. Database Lock Contention

**Mitigation:**
- SQLite WAL mode (concurrent reads)
- Busy timeout: 30 seconds
- Retry with exponential backoff

```python
db = sqlite3.connect(
    "persona_jobs.db",
    timeout=30.0,  # Wait up to 30s for locks
    check_same_thread=False
)
db.execute("PRAGMA journal_mode=WAL")
```

### Partial Results

**Capture Strategy:**
If LLM generates 50% of review before error, save it:

```python
class PersonaExecutor:
    def __init__(self):
        self.accumulated_text = ""  # Track partial output
    
    async def invoke_with_streaming(self, ...):
        try:
            async with llm_client.messages.stream(...) as stream:
                async for text in stream.text_stream:
                    self.accumulated_text += text
                    # Continue accumulating...
        
        except Exception as e:
            # Even on error, we have partial text
            return {
                "status": "failed",
                "partial_result": self.accumulated_text,
                "error": str(e)
            }
```

**User Value:**
- Better than nothing
- May still contain useful insights
- Can inform retry strategy

### Resource Limits

#### Max Concurrent Jobs (Per Worker Pool)

```python
# config.json
{
  "personas": {
    "worker_pool_size": 3,
    "max_queue_size": 20
  }
}
```

**Behavior:**
- If 3 jobs running + 20 queued = reject new jobs
- Return: `{"error": "Job queue full (23/23), try again later"}`

#### Max Context Size

```python
MAX_CONTEXT_SIZE = 100_000  # 100KB

def create_job(..., context):
    if len(context or "") > MAX_CONTEXT_SIZE:
        return {
            "error": f"Context too large ({len(context)} bytes > {MAX_CONTEXT_SIZE}). "
                    "Please reduce the amount of code provided."
        }
```

#### Memory Monitoring

```python
import psutil

def check_memory_before_job():
    """Reject new jobs if memory critical."""
    memory = psutil.virtual_memory()
    
    if memory.percent > 90:  # >90% RAM used
        return {
            "error": "Server memory critical (90%+). Try again in a few minutes."
        }
```

### Retry Logic

#### Automatic Retries (Transient Errors)

```python
RETRY_ERRORS = [
    "rate_limit_error",
    "overloaded_error",
    "timeout_error"  # Only if <5s timeout
]

async def invoke_with_retry(self, ...):
    for attempt in range(3):
        try:
            return await self._invoke_persona(...)
        except AnthropicError as e:
            if e.type in RETRY_ERRORS and attempt < 2:
                wait = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                await asyncio.sleep(wait)
                continue
            raise
```

#### User-Triggered Retry

```python
@mcp.tool()
async def retry_persona_job(job_id: str) -> Dict[str, Any]:
    """
    Retry a failed job with same parameters.
    
    Creates a new job with same task/context but fresh execution.
    """
    old_job = job_manager.get_job(job_id)
    
    if old_job["status"] != "failed":
        return {"error": "Can only retry failed jobs"}
    
    # Create new job with same params
    new_job_id = job_manager.create_job(
        persona=old_job["persona"],
        task=old_job["task"],
        context=old_job["context"],
        priority="high"  # Bump priority for retries
    )
    
    return {
        "status": "started",
        "new_job_id": new_job_id,
        "message": f"Retry started (new job: {new_job_id})"
    }
```

---

## 👤 USER EXPERIENCE DESIGN

### Design Principle: "Progress Over Speed"

**Core Philosophy:**
Users prefer **visible progress with accurate ETAs** over **silent waiting** (even if silent is slightly faster).

**Bad UX Example (Sync):**
```
User: "@architect review"
[Shows: "Loading..."]
[30 seconds pass...]
[Still "Loading..."]
[User thinks: "Is it frozen? Should I cancel?"]
[45 seconds...]
[Finally completes]
User: "That took forever and I had no idea what was happening"
```

**Good UX Example (Async):**
```
User: "@architect review"
[Shows: "✓ Started (job: a7f3c9d2)"]
[5s: "🔄 Searching standards... 30% (~25s left)"]
[10s: "🔄 Analyzing code... 60% (~15s left)"]
[15s: "🔄 Generating review... 90% (~3s left)"]
[18s: "✅ Complete! (took 18 seconds)"]
User: "Perfect - I knew exactly what was happening the whole time"
```

### UX Pattern 1: Auto-Polling with Progress Bar (Recommended)

**Main Cursor agent implements transparent polling:**

```python
# Pseudo-code for Cursor agent behavior
async def handle_architect_review(task, context):
    # Start job
    result = await invoke_architect(task, context)
    job_id = result["job_id"]
    
    print(f"✓ Started architect review (job: {job_id[:8]}...)")
    print(f"Estimated time: {result['estimated_duration_seconds']}s")
    
    # Poll loop
    while True:
        await asyncio.sleep(5)  # Poll every 5 seconds
        
        status = await check_persona_job(job_id)
        
        if status["status"] == "running":
            prog = status["progress"]
            print(f"🔄 {prog['message']} ({prog['percent_complete']}%, ~{prog['eta_seconds']}s left)")
        
        elif status["status"] == "complete":
            print(f"✅ Review complete! (took {status['duration_seconds']}s)")
            print(status["result"])
            break
        
        elif status["status"] == "failed":
            print(f"⚠️ Review failed: {status['error']}")
            if status.get("partial_result"):
                print("Partial result:")
                print(status["partial_result"])
            break
```

**User sees:**
```
✓ Started architect review (job: a7f3c9d2...)
Estimated time: 35s

🔄 Searching standards... (30%, ~25s left)
🔄 Analyzing code patterns... (60%, ~15s left)
🔄 Generating review... (95%, ~3s left)
✅ Review complete! (took 32s)

🎯 Architecture Review

## Strengths
...
```

### UX Pattern 2: Manual Status Check (Fallback)

**If Cursor agent doesn't implement auto-polling, user can manually check:**

```
User: "@architect review this"
Agent: "✓ Started architect review
        Job ID: a7f3c9d2-1234-5678-90ab-cdef12345678
        Check status: check_persona_job('a7f3c9d2...')"

[User waits 30 seconds]

User: "check status a7f3c9d2"
Agent: "✅ Complete! Here's the review: ..."
```

**Less ideal but still functional.**

### Progress Indicator Guidelines

**Text Format:**
```
🔄 Architect working... (searching standards, 30% done, ~25s remaining)
🔄 Architect working... (analyzing code, 60% done, ~15s remaining)
🔄 Architect working... (generating review, 95% done, ~3s remaining)
✅ Architect review complete! (took 32 seconds, 2 tool calls, 4.3K tokens)
```

**Structured Format (if Cursor supports rich UI):**
```
┌─────────────────────────────────────────────┐
│ Architect Review                             │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░ 60%    │
│ Analyzing code patterns...                  │
│ Elapsed: 15s | ETA: ~15s | Tools: 2         │
└─────────────────────────────────────────────┘
```

### Error Messages (User-Friendly)

**Timeout:**
```
⚠️ Architect review timed out after 90 seconds

This usually happens with very large codebases. Try one of these:
• Reduce the scope (fewer files)
• Break into smaller reviews
• Use more specific context

Partial result (review was 70% complete):
🎯 Architecture Review (Incomplete)
...
```

**Queue Full:**
```
⚠️ Persona system is busy (3 reviews running, 20 queued)

Please try again in a few minutes, or cancel some pending jobs:
list_persona_jobs(status="pending")
```

**API Error:**
```
⚠️ LLM API error: rate_limit_exceeded

The API rate limit was hit. This will auto-retry in 30 seconds.
Current status: check_persona_job('a7f3c9d2...')
```


---

## 🧪 TESTING STRATEGY

### Unit Tests

#### test_job_manager.py

```python
def test_create_job():
    """Test job creation with unique ID."""
    job_id = job_manager.create_job("architect", "Review API", None)
    assert uuid.UUID(job_id)  # Valid UUID
    
    job = job_manager.get_job(job_id)
    assert job["status"] == "pending"
    assert job["persona"] == "architect"

def test_update_progress():
    """Test progress updates are persisted."""
    job_id = job_manager.create_job("architect", "task")
    
    job_manager.update_progress(
        job_id,
        phase="searching",
        percent=40,
        message="Searching standards..."
    )
    
    job = job_manager.get_job(job_id)
    assert job["progress_phase"] == "searching"
    assert job["progress_percent"] == 40

def test_complete_job():
    """Test job completion."""
    job_id = job_manager.create_job("architect", "task")
    
    job_manager.complete_job(
        job_id,
        result="Review complete",
        tokens_used={"input": 1000, "output": 500}
    )
    
    job = job_manager.get_job(job_id)
    assert job["status"] == "complete"
    assert job["tokens_input"] == 1000
    assert job["completed_at"] is not None

def test_concurrent_job_access():
    """Test thread-safe job access."""
    import threading
    
    job_id = job_manager.create_job("architect", "task")
    
    def update_progress(n):
        for i in range(10):
            job_manager.update_progress(
                job_id, "phase", i*10, f"Update {n}-{i}"
            )
    
    threads = [threading.Thread(target=update_progress, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Should complete without database locks or corruption
    job = job_manager.get_job(job_id)
    assert job is not None

def test_job_expiration():
    """Test old job cleanup."""
    # Create old job (simulate by backdating)
    old_job_id = job_manager.create_job("architect", "old task")
    job_manager.db.execute(
        "UPDATE persona_jobs SET created_at = created_at - 604800 WHERE id=?",
        (old_job_id,)
    )
    
    # Create recent job
    new_job_id = job_manager.create_job("architect", "new task")
    
    # Expire jobs older than 7 days
    expired_count = job_manager.expire_old_jobs(older_than_hours=168)
    
    assert expired_count == 1
    assert job_manager.get_job(old_job_id) is None
    assert job_manager.get_job(new_job_id) is not None
```

#### test_background_worker.py

```python
@pytest.mark.asyncio
async def test_worker_picks_up_job():
    """Test worker detects and executes pending job."""
    # Create pending job
    job_id = job_manager.create_job("architect", "task", "context")
    
    # Start worker pool
    worker_pool = WorkerPool(job_manager, persona_executor, num_workers=1)
    worker_pool.start()
    
    # Wait for job to complete (max 30s)
    for _ in range(30):
        job = job_manager.get_job(job_id)
        if job["status"] == "complete":
            break
        await asyncio.sleep(1)
    
    worker_pool.shutdown()
    
    assert job["status"] == "complete"
    assert job["result"] is not None

def test_worker_handles_error():
    """Test worker gracefully handles execution errors."""
    # Mock persona executor to raise error
    def failing_invoke(*args, **kwargs):
        raise RuntimeError("LLM API failed")
    
    persona_executor.invoke = failing_invoke
    
    job_id = job_manager.create_job("architect", "task")
    
    worker_pool = WorkerPool(job_manager, persona_executor, num_workers=1)
    worker_pool.start()
    
    # Wait for job to fail
    time.sleep(5)
    worker_pool.shutdown()
    
    job = job_manager.get_job(job_id)
    assert job["status"] == "failed"
    assert "LLM API failed" in job["error"]

def test_multiple_workers_concurrent():
    """Test multiple workers process jobs concurrently."""
    # Create 5 jobs
    job_ids = [job_manager.create_job("architect", f"task {i}") for i in range(5)]
    
    start_time = time.time()
    
    # 3 workers should process 5 jobs in 2 batches
    worker_pool = WorkerPool(job_manager, persona_executor, num_workers=3)
    worker_pool.start()
    
    # Wait for all to complete
    while True:
        statuses = [job_manager.get_job(jid)["status"] for jid in job_ids]
        if all(s == "complete" for s in statuses):
            break
        time.sleep(1)
    
    elapsed = time.time() - start_time
    worker_pool.shutdown()
    
    # Should take ~2x job time (2 batches), not 5x (sequential)
    assert elapsed < 40  # 5 jobs * 10s / 3 workers ≈ 20s
```

### Integration Tests

#### test_async_persona_flow.py

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_async_flow():
    """Test complete flow: invoke → worker → poll → complete."""
    # Start MCP server with real components
    mcp_server = create_server()
    
    # Invoke architect
    invoke_result = await mcp_server.invoke_architect(
        task="Review this API design",
        context="<100 lines of code>"
    )
    
    assert invoke_result["status"] == "started"
    job_id = invoke_result["job_id"]
    
    # Poll until complete
    for attempt in range(30):  # Max 30s
        status = await mcp_server.check_persona_job(job_id)
        
        if status["status"] == "complete":
            assert "Architecture Review" in status["result"]
            assert status["tokens_used"]["input"] > 0
            break
        
        elif status["status"] == "running":
            assert status["progress"]["percent_complete"] >= 0
            assert status["progress"]["message"] is not None
        
        await asyncio.sleep(1)
    
    # Should have completed
    assert status["status"] == "complete"

@pytest.mark.integration
async def test_multi_persona_concurrent():
    """Test 3 personas execute concurrently."""
    mcp_server = create_server()
    
    # Invoke 3 personas
    job1 = await mcp_server.invoke_architect(task="Review API")
    job2 = await mcp_server.invoke_security(task="Security audit")
    job3 = await mcp_server.invoke_sre(task="Production readiness")
    
    start_time = time.time()
    
    # Poll all 3
    jobs = [job1["job_id"], job2["job_id"], job3["job_id"]]
    completed = [False, False, False]
    
    while not all(completed):
        for i, job_id in enumerate(jobs):
            if completed[i]:
                continue
            
            status = await mcp_server.check_persona_job(job_id)
            if status["status"] == "complete":
                completed[i] = True
        
        await asyncio.sleep(2)
    
    elapsed = time.time() - start_time
    
    # Should complete in ~45s (concurrent), not 120s (sequential)
    assert elapsed < 60
```

### Load Tests

#### test_concurrent_jobs.py

```python
@pytest.mark.load
def test_queue_20_concurrent_jobs():
    """Test system under heavy load (20 simultaneous jobs)."""
    mcp_server = create_server()
    
    # Create 20 jobs as fast as possible
    job_ids = []
    for i in range(20):
        result = await mcp_server.invoke_architect(
            task=f"Review component {i}"
        )
        job_ids.append(result["job_id"])
    
    # All should be created successfully
    assert len(job_ids) == 20
    
    # Monitor completion over time
    completion_times = {}
    
    for job_id in job_ids:
        while True:
            status = await mcp_server.check_persona_job(job_id)
            if status["status"] == "complete":
                completion_times[job_id] = time.time()
                break
            await asyncio.sleep(1)
    
    # All should complete (may take several minutes)
    assert len(completion_times) == 20
    
    # First 3 should complete quickly (worker pool size=3)
    sorted_times = sorted(completion_times.values())
    first_batch = sorted_times[2] - sorted_times[0]
    assert first_batch < 10  # First 3 complete within 10s of each other

def test_memory_usage_under_load():
    """Test memory doesn't leak with many jobs."""
    import psutil
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Create and complete 100 jobs
    for i in range(100):
        job_id = job_manager.create_job("architect", f"task {i}")
        job_manager.complete_job(job_id, f"result {i}", {"input": 100, "output": 50})
    
    final_memory = process.memory_info().rss / 1024 / 1024
    
    # Memory increase should be reasonable (<100MB for 100 jobs)
    assert (final_memory - initial_memory) < 100
```

### User Acceptance Tests

#### test_ux_polling.py

```python
@pytest.mark.ux
async def test_progress_updates_are_meaningful():
    """Test that progress messages make sense to users."""
    mcp_server = create_server()
    
    result = await mcp_server.invoke_architect(task="Review API")
    job_id = result["job_id"]
    
    progress_messages = []
    
    # Collect all progress messages
    while True:
        status = await mcp_server.check_persona_job(job_id)
        
        if status["status"] == "running":
            msg = status["progress"]["message"]
            progress_messages.append(msg)
        
        elif status["status"] == "complete":
            break
        
        await asyncio.sleep(5)
    
    # Should have at least 3 distinct progress messages
    assert len(set(progress_messages)) >= 3
    
    # Should contain key phases
    all_msgs = " ".join(progress_messages)
    assert "searching" in all_msgs.lower() or "analyzing" in all_msgs.lower()
    
def test_eta_accuracy():
    """Test ETA estimates are within 50% of actual."""
    mcp_server = create_server()
    
    result = await mcp_server.invoke_architect(task="Review")
    job_id = result["job_id"]
    
    # Get ETA at 50% mark
    while True:
        status = await mcp_server.check_persona_job(job_id)
        
        if status["status"] == "running":
            prog = status["progress"]
            if 45 <= prog["percent_complete"] <= 55:
                eta_at_50 = prog["eta_seconds"]
                time_at_50 = time.time()
                break
        
        await asyncio.sleep(2)
    
    # Wait for completion
    while status["status"] != "complete":
        status = await mcp_server.check_persona_job(job_id)
        await asyncio.sleep(2)
    
    actual_remaining = time.time() - time_at_50
    
    # ETA should be within 50% of actual
    error_ratio = abs(actual_remaining - eta_at_50) / actual_remaining
    assert error_ratio < 0.5  # Within 50%
```

---

## ⚡ PERFORMANCE CONSIDERATIONS

### Latency Metrics

**Target Performance (95th Percentile):**

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Job Creation | < 50ms | `invoke_architect()` return time |
| Status Query | < 10ms | `check_persona_job()` return time |
| Worker Pickup | < 500ms | Time from pending → running |
| Progress Update | < 20ms | Database write time |
| Job Completion | < 100ms | Final DB update time |

**Total Overhead:**
- Async overhead vs hypothetical sync: ~1s (job creation + polling latency)
- Acceptable given we avoid 10-30% timeout risk

### Scalability Limits

**Expected Load (Per Developer):**
- 1-5 concurrent persona invocations
- 10-50 invocations per day
- ~1000 jobs per week per team (10 developers)

**System Capacity:**
- Worker pool: 3 concurrent jobs
- Queue size: 20 pending jobs
- SQLite: 1000s reads/sec, 100s writes/sec (sufficient)
- Disk: ~1MB per job result → 1GB for 1000 jobs

**Bottleneck Analysis:**

1. **Worker Pool Size (3)**
   - Limited by LLM API rate limits, not CPU/memory
   - Anthropic Tier 1: 50 req/min (can support ~16 workers theoretical)
   - Default 3 is conservative, can increase to 5-10 if needed

2. **SQLite Concurrency**
   - WAL mode supports unlimited concurrent readers
   - Single writer (serialized writes)
   - Benchmark: 1000 writes/sec (far exceeds needs)

3. **Disk I/O**
   - Result storage: ~1MB per job
   - SSD write speed: 100+ MB/s
   - Can handle 100 concurrent completions/sec

4. **Memory**
   - ~10MB per active job (LLM context in memory)
   - 3 workers × 10MB = 30MB active
   - Completed jobs on disk, not in RAM
   - Total: <100MB for entire persona system

**Scaling Beyond Single Machine:**
- Phase 6: Distributed worker pool (multiple MCP servers)
- Shared SQLite DB → PostgreSQL
- Message queue (Redis) for job coordination

### Optimization Opportunities

#### 1. Cache search_standards() Results

```python
class PersonaExecutor:
    def __init__(self):
        self.rag_cache = {}  # Per-job cache
    
    def _execute_tool(self, tool_name, tool_input):
        if tool_name == "search_standards":
            cache_key = tool_input["query"]
            
            if cache_key in self.rag_cache:
                logger.info(f"Cache hit: {cache_key}")
                return self.rag_cache[cache_key]
            
            result = rag_engine.search(cache_key)
            self.rag_cache[cache_key] = result
            return result
```

**Impact:** Reduces redundant RAG queries by ~30%

#### 2. Compress Large Results

```python
import gzip

def complete_job(self, job_id, result, ...):
    # Compress results >10KB
    if len(result) > 10_000:
        result_compressed = gzip.compress(result.encode())
        compressed = True
    else:
        result_compressed = result
        compressed = False
    
    self.db.execute(
        "UPDATE persona_jobs SET result=?, compressed=? WHERE id=?",
        (result_compressed, compressed, job_id)
    )
```

**Impact:** Saves ~70% disk space for large reviews

#### 3. Archive Old Jobs

```python
def archive_old_jobs(self, older_than_days=30):
    """Move old jobs to archive database."""
    old_jobs = self.db.query("""
        SELECT * FROM persona_jobs
        WHERE created_at < datetime('now', '-30 days')
    """)
    
    # Copy to archive DB
    archive_db.executemany("INSERT INTO persona_jobs VALUES ...", old_jobs)
    
    # Delete from main DB
    self.db.execute("""
        DELETE FROM persona_jobs
        WHERE created_at < datetime('now', '-30 days')
    """)
```

**Impact:** Keeps main DB <100MB, fast queries

---

## 📐 IMPLEMENTATION PLAN

### Phase 1: Core Infrastructure (Week 1)

**Goal:** Job queue + database schema

**Tasks:**
1. Create `mcp_server/job_manager.py`
   - JobManager class with create/get/update/complete
   - SQLite schema (persona_jobs table)
   - Database migrations
2. Create `mcp_server/models.py` additions
   - JobState dataclass
   - ProgressUpdate dataclass
3. Unit tests for JobManager
4. Manual testing (create jobs, query status)

**Deliverables:**
- `job_manager.py` (~300 lines)
- `migrations/001_persona_jobs.sql`
- 15+ unit tests

**Success Criteria:**
- Can create jobs and query status
- Concurrent access is thread-safe
- Tests pass

### Phase 2: Background Worker Pool (Week 2)

**Goal:** Workers execute jobs asynchronously

**Tasks:**
1. Create `mcp_server/background_worker.py`
   - WorkerPool class
   - WorkerThread class
   - Job pickup logic
2. Integrate with PersonaExecutor
   - Add progress callbacks
   - Wire up to job_manager
3. Worker lifecycle (start/shutdown)
4. Integration tests

**Deliverables:**
- `background_worker.py` (~400 lines)
- Modified `persona_executor.py` (+100 lines)
- 10+ integration tests

**Success Criteria:**
- Workers pick up pending jobs within 500ms
- Jobs complete successfully
- Errors are handled gracefully

### Phase 3: MCP Tools Integration (Week 3)

**Goal:** Expose async APIs via MCP

**Tasks:**
1. Modify `mcp_server/agent_os_rag.py`
   - Add invoke_* tools (architect, engineer, data, qa, security, sre)
   - Add check_persona_job tool
   - Add list_persona_jobs tool
   - Add cancel_persona_job tool
2. Wire tools to job_manager
3. End-to-end testing

**Deliverables:**
- Modified `agent_os_rag.py` (+200 lines)
- 10+ e2e tests

**Success Criteria:**
- Can invoke personas from Cursor
- Polling returns accurate status
- Results are retrieved successfully

### Phase 4: Progress Tracking (Week 4)

**Goal:** Real-time progress updates with ETA

**Tasks:**
1. Enhanced PersonaExecutor
   - Progress checkpoints (initializing, searching, analyzing, generating)
   - ETA calculation
   - Structured progress format
2. Progress reporter utility
3. UX testing

**Deliverables:**
- Enhanced `persona_executor.py` (+150 lines)
- `progress_reporter.py` (~100 lines)
- UX tests

**Success Criteria:**
- Progress updates appear every 5-10s
- ETAs are within 50% accuracy
- Progress messages are meaningful

### Phase 5: Error Handling & Polish (Week 5)

**Goal:** Production-ready reliability

**Tasks:**
1. Timeout handling (LLM API, worker crashes)
2. Partial result capture
3. Job cancellation
4. Cleanup scheduler (expire old jobs)
5. Resource limits (memory, queue size)
6. Load testing

**Deliverables:**
- Error handling code (~200 lines)
- Cleanup cron job
- Load tests
- Documentation

**Success Criteria:**
- System handles timeouts gracefully
- No resource leaks
- Can handle 20 concurrent jobs
- All tests pass

### Phase 6: Observability & Metrics (Optional, Week 6)

**Goal:** Production visibility

**Tasks:**
1. Job history queries (list_persona_jobs)
2. Token usage tracking
3. HoneyHive integration
4. Metrics dashboard
5. Performance monitoring

**Deliverables:**
- Observability code (~150 lines)
- Metrics dashboard
- Documentation

**Success Criteria:**
- Can query job history
- Token costs are tracked
- Performance metrics visible

---

## 🔗 RELATED WORK

### Existing Documents

- **persona-llm-communication.md** - How personas make LLM API calls (separate from Cursor)
- **infrastructure-architecture.md** - Overall MCP server architecture
- **persona-tool-access-architecture.md** - What tools personas can access

### Informed By

- **workflow_engine.py** - Existing state management patterns (StateManager class)
- **agent_os_rag.py** - Existing MCP tool registration (FastMCP patterns)
- **Anthropic SDK** - Streaming API examples

### Will Influence

- **implementation.md** - Will add async-specific code patterns and examples
- **specs.md** - Will reference this architecture in persona tool specifications
- **tasks.md** - Implementation tasks will follow this 5-phase plan

---

## 📊 SUCCESS METRICS

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Timeout Rate | 0% | (failed jobs with timeout) / total jobs |
| Job Creation Latency (p95) | < 50ms | Time to return from invoke_*() |
| Polling Latency (p95) | < 10ms | Time to return from check_persona_job() |
| Worker Utilization | 60-80% | (time busy) / (total time) |
| ETA Accuracy | ±50% | |actual - estimated| / actual |

### User Experience Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Progress Update Frequency | Every 5-10s | Time between progress changes |
| Perceived Responsiveness | "Instant" | 95% of users rate job start as <1s |
| Progress Clarity | 90% understand | Survey: "Progress messages were clear" |
| Error Recovery Rate | >99% | (recovered jobs) / (failed jobs) |

### Business Metrics

| Metric | Target | Impact |
|--------|--------|--------|
| Persona Adoption | +30% | More users invoke personas (no timeout fear) |
| Multi-Persona Usage | +50% | Concurrent invocations easier |
| Support Issues | -50% | Fewer "persona timed out" complaints |
| User Satisfaction | 4.5/5 | Rating of persona system reliability |

---

## 🔐 SECURITY CONSIDERATIONS

### Job Isolation

- Each job runs in separate context (no shared state between personas)
- Job results scoped to job ID (no cross-job access)
- SQLite row-level locking prevents data corruption

### Data Retention

**Sensitive Information:**
- Task descriptions may contain sensitive business logic
- Context may include API keys, secrets (user's responsibility to sanitize)
- Results stored in plaintext SQLite (consider encryption for high-security envs)

**PII Concerns:**
- Jobs contain whatever user provides in task/context
- Retention policy: 7 days for completed, 30 days for failed
- Users should avoid putting PII in persona requests

**Recommendations:**
- Document: "Sanitize sensitive data before invoking personas"
- Option: Add flag `sanitize_context=True` to scrub common secrets (API keys, tokens)

### Resource Limits

**Prevent Abuse/DoS:**
- Max context size: 100KB (prevent memory exhaustion)
- Max queue size: 20 jobs (prevent disk exhaustion)
- Max concurrent jobs per user: 5 (if multi-user future)
- Rate limiting: 10 job creations per minute per user

**Implementation:**
```python
RATE_LIMIT = 10  # jobs per minute
rate_limiter = {}  # user_id → (timestamp, count)

def check_rate_limit(user_id):
    now = time.time()
    
    if user_id in rate_limiter:
        last_time, count = rate_limiter[user_id]
        
        if now - last_time < 60:  # Within last minute
            if count >= RATE_LIMIT:
                raise RateLimitError(f"Max {RATE_LIMIT} jobs/minute")
            rate_limiter[user_id] = (last_time, count + 1)
        else:
            rate_limiter[user_id] = (now, 1)
    else:
        rate_limiter[user_id] = (now, 1)
```

---

## 📝 OPEN QUESTIONS & DECISIONS NEEDED

### Critical Decisions

1. **Polling Interval:**
   - Option A: Fixed 5s (simple, predictable)
   - Option B: Adaptive (3s when ETA <10s, 5s otherwise)
   - **Recommendation:** Option A (simpler, 5s is fine)

2. **Job Retention:**
   - Complete jobs: 7 days or 30 days?
   - Failed jobs: 30 days or 90 days (for debugging)?
   - **Recommendation:** 7 days complete, 30 days failed

3. **Tool Naming:**
   - `invoke_architect_async()` or `invoke_architect()`?
   - **Recommendation:** `invoke_architect()` (no suffix, it's the only mode)

4. **Progress Granularity:**
   - Update on every tool call or every N seconds?
   - **Recommendation:** Both (tool call completion + 5s timer)

5. **Worker Pool Size:**
   - Fixed 3, fixed 5, or auto-scale?
   - **Recommendation:** Fixed 3, configurable in config.json

6. **Priority Queue:**
   - FIFO or priority levels (low/normal/high)?
   - **Recommendation:** Priority queue (support urgent reviews)

### Nice-to-Have (Future Phases)

- WebSocket push notifications (eliminate polling)
- Distributed worker pool (multiple machines)
- Smart ETA using ML on historical jobs
- Job templates for common reviews
- Desktop notifications on completion

---

## 🚀 DECISION: ASYNC-FIRST ARCHITECTURE

### Final Design Choice

**Implement async background jobs as the primary and only persona invocation mechanism.**

### Rationale

1. **Eliminates Timeout Risk** - Jobs return immediately (<1s), workers run indefinitely
2. **Provides Transparency** - Real-time progress updates every 5s
3. **Scales to Extremes** - 5-minute reviews work same as 30s reviews
4. **Simple Mental Model** - Users always expect: start → poll → result
5. **Future-Proof** - Foundation for advanced features (history, notifications, analytics)

### Trade-offs Accepted

- ~800 lines of code (vs 200 for sync)
- Polling overhead (~5% execution time)
- Small latency (<1s startup)
- SQLite state management

### Trade-offs Worth It Because

- Sync has 10-20% timeout rate (unacceptable)
- No progress feedback frustrates users
- Can't support comprehensive reviews
- Benefits outweigh costs 10:1

---

## 🎯 CONCLUSION

### Summary

Async background job architecture is the **correct design choice** for persona invocations because it:

1. **Solves the core problem**: Eliminates 100% of timeout failures
2. **Improves UX dramatically**: Progress visibility builds user trust and confidence
3. **Scales gracefully**: Handles simple 30s reviews and complex 5min reviews identically
4. **Future-proof**: Foundation for notifications, analytics, distributed execution
5. **Industry-standard**: Users already understand "start job → poll → complete" pattern

The ~800 line implementation cost and minor polling overhead are justified by **zero timeout risk** and **superior user experience**.

### Next Steps

1. ✅ **Approve this design** (or request revisions)
2. **Update related documents:**
   - `implementation.md` - Add async-specific code patterns
   - `specs.md` - Reference this architecture
   - `tasks.md` - Use 5-phase implementation plan
3. **Begin Phase 1 implementation** (job queue manager)
4. **Weekly reviews** to track progress against plan

---

**Design Status: ✅ Complete - Ready for Implementation**

**Document Owner:** Agent OS Team  
**Last Updated:** 2025-10-06  
**Next Review:** After Phase 1 completion (Week 1)

---

## 🗄️ DATABASE MAINTENANCE STRATEGY

### Growth Analysis

**Storage Per Job:**
```
Job metadata:        ~1 KB   (id, persona, status, timestamps)
Context (code):      ~25 KB  (average, varies 1KB-100KB)
Result (review):     ~7 KB   (average, varies 1KB-20KB)
Total per job:       ~33 KB  (average)
```

**Expected Growth:**
```
Load: 10 developers × 10 jobs/day = 100 jobs/day

Daily:   100 jobs × 33KB = 3.3 MB/day
Weekly:  700 jobs × 33KB = 23 MB/week
Monthly: 3000 jobs × 33KB = 100 MB/month
6 months (no cleanup): 600 MB
```

**SQLite Performance:**
- <100MB: Excellent (ms queries)
- 100-500MB: Good (10-50ms queries)
- 500MB-1GB: Acceptable (50-100ms queries)
- >1GB: Degraded (100ms+ queries)

**Target:** Keep database <100MB via automatic cleanup

---

### Maintenance Strategy: Hybrid Approach

#### Strategy 1: Automatic Pruning (Default)

**How It Works:**
- Background cleanup task runs daily (or on startup)
- Deletes jobs older than retention period
- Different retention for different statuses

**Retention Policy (Configurable):**
```json
{
  "personas": {
    "job_retention": {
      "complete": 7,      // days (1 week)
      "failed": 30,       // days (1 month, for debugging)
      "cancelled": 7,     // days
      "pending": 1,       // days (stale jobs)
      "running": 0.1      // days (2.4 hours, crashed workers)
    }
  }
}
```

**Implementation:**

```python
class JobManager:
    def cleanup_old_jobs(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Delete jobs older than retention period.
        
        Args:
            dry_run: If True, return counts without deleting
        
        Returns:
            {
                "complete": 150,    # deleted
                "failed": 12,
                "cancelled": 5,
                "pending": 2,
                "running": 0,
                "total_deleted": 169,
                "space_freed_mb": 5.6
            }
        """
        retention = self._get_retention_policy()
        deleted_counts = {}
        total_size_before = self._get_db_size()
        
        for status, days in retention.items():
            cutoff_time = time.time() - (days * 86400)
            
            if dry_run:
                count = self.db.execute("""
                    SELECT COUNT(*) FROM persona_jobs
                    WHERE status = ? AND created_at < ?
                """, (status, cutoff_time)).fetchone()[0]
            else:
                cursor = self.db.execute("""
                    DELETE FROM persona_jobs
                    WHERE status = ? AND created_at < ?
                """, (status, cutoff_time))
                count = cursor.rowcount
                self.db.commit()
            
            deleted_counts[status] = count
        
        # Vacuum to reclaim space
        if not dry_run:
            self.db.execute("VACUUM")
        
        total_size_after = self._get_db_size()
        space_freed = (total_size_before - total_size_after) / 1024 / 1024
        
        return {
            **deleted_counts,
            "total_deleted": sum(deleted_counts.values()),
            "space_freed_mb": round(space_freed, 2)
        }
    
    def schedule_cleanup(self):
        """Run cleanup daily at 3 AM (or on startup if missed)."""
        def cleanup_loop():
            while not self.shutdown_event.is_set():
                # Check if cleanup is due
                last_cleanup = self._get_last_cleanup_time()
                now = time.time()
                
                # Run if >24 hours since last cleanup
                if now - last_cleanup > 86400:
                    logger.info("Running scheduled cleanup...")
                    result = self.cleanup_old_jobs()
                    logger.info(
                        f"Cleanup complete: {result['total_deleted']} jobs deleted, "
                        f"{result['space_freed_mb']} MB freed"
                    )
                    self._set_last_cleanup_time(now)
                
                # Sleep 1 hour, check again
                time.sleep(3600)
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
```

**Pros:**
- ✅ Set it and forget it
- ✅ Configurable retention per status
- ✅ Keeps failed jobs longer for debugging
- ✅ Automatic space reclamation (VACUUM)

**Cons:**
- ⚠️ Slightly more complex (~150 lines)
- ⚠️ VACUUM can lock DB briefly (acceptable since runs at 3 AM)

---

#### Strategy 2: Size-Based Safety Valve

**How It Works:**
- Monitor DB size before each job creation
- If DB exceeds threshold, trigger emergency cleanup

**Implementation:**

```python
def create_job(self, persona, task, context, priority="normal"):
    """Create job with size check."""
    
    # Check DB size
    db_size_mb = self._get_db_size() / 1024 / 1024
    
    if db_size_mb > 100:  # Exceeded target size
        logger.warning(f"DB size {db_size_mb:.1f}MB exceeds 100MB. Running cleanup...")
        
        # Emergency cleanup: More aggressive retention
        emergency_retention = {
            "complete": 3,   # 3 days (vs normal 7)
            "failed": 14,    # 2 weeks (vs normal 30)
            "cancelled": 1,
            "pending": 0.5,
            "running": 0.1
        }
        
        result = self.cleanup_old_jobs(retention_override=emergency_retention)
        logger.info(f"Emergency cleanup: {result['total_deleted']} jobs deleted")
        
        # If still too large, fail job creation
        db_size_mb = self._get_db_size() / 1024 / 1024
        if db_size_mb > 150:  # Hard limit
            raise DatabaseFullError(
                f"Database full ({db_size_mb:.1f}MB > 150MB). "
                "Manual cleanup required or increase retention limits."
            )
    
    # Create job normally
    job_id = str(uuid.uuid4())
    self.db.execute(...)
    return job_id
```

**Pros:**
- ✅ Prevents unbounded growth (hard limit)
- ✅ Self-healing (automatic response)

**Cons:**
- ⚠️ VACUUM during job creation (slight delay)
- ⚠️ Can reject jobs if cleanup insufficient

---

#### Strategy 3: Archive and Rotate (Optional)

**How It Works:**
- Keep main DB small (<100MB)
- Move old jobs to archive DB periodically
- Archive DB can grow large (read-only)

**Implementation:**

```python
def archive_old_jobs(self, older_than_days: int = 30):
    """Move old jobs to archive database."""
    
    archive_db = sqlite3.connect(".agent-os/.cache/persona_jobs_archive.db")
    
    # Ensure archive has same schema
    self._init_archive_schema(archive_db)
    
    # Copy old jobs to archive
    cutoff = time.time() - (older_than_days * 86400)
    
    old_jobs = self.db.execute("""
        SELECT * FROM persona_jobs
        WHERE created_at < ? AND status IN ('complete', 'failed', 'cancelled')
    """, (cutoff,)).fetchall()
    
    if old_jobs:
        archive_db.executemany("""
            INSERT OR IGNORE INTO persona_jobs VALUES (?, ?, ?, ...)
        """, old_jobs)
        archive_db.commit()
        
        # Delete from main DB
        self.db.execute("""
            DELETE FROM persona_jobs WHERE created_at < ?
        """, (cutoff,))
        self.db.commit()
        
        logger.info(f"Archived {len(old_jobs)} jobs to archive DB")
    
    archive_db.close()
```

**Pros:**
- ✅ History preserved indefinitely
- ✅ Main DB stays fast
- ✅ Can query archive for historical analysis

**Cons:**
- ❌ More complex (~200 lines)
- ❌ Two databases to manage
- ❌ Archive can grow unbounded (unless separate cleanup)

**Recommendation:** Phase 6+ (not needed for MVP)

---

#### Strategy 4: Manual Nuke and Pave (Emergency)

**How It Works:**
- Provide tool to completely reset database
- Use when automatic cleanup insufficient

**Implementation:**

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
    if not confirm:
        return {
            "status": "cancelled",
            "error": "Must pass confirm=True to reset database",
            "warning": "This will DELETE ALL job history!"
        }
    
    # Get counts before deletion
    total_jobs = job_manager.db.execute(
        "SELECT COUNT(*) FROM persona_jobs"
    ).fetchone()[0]
    
    size_before = job_manager._get_db_size() / 1024 / 1024
    
    # Delete all jobs
    job_manager.db.execute("DELETE FROM persona_jobs")
    job_manager.db.commit()
    
    # Vacuum to reclaim space
    job_manager.db.execute("VACUUM")
    
    size_after = job_manager._get_db_size() / 1024 / 1024
    space_freed = size_before - size_after
    
    logger.warning(f"Database reset: {total_jobs} jobs deleted")
    
    return {
        "status": "reset",
        "jobs_deleted": total_jobs,
        "space_freed_mb": round(space_freed, 2),
        "message": "All job history deleted. Database reset complete."
    }
```

**Usage:**
```python
# User must explicitly confirm
await reset_persona_jobs(confirm=True)
```

**Pros:**
- ✅ Dead simple
- ✅ Guaranteed to work
- ✅ Fast (<1 second)

**Cons:**
- ❌ Lose all history
- ❌ Can't debug past issues
- ❌ Must explicitly confirm (safety)

---

### Recommended Configuration

**Phase 1-3 (MVP):**
- Implement Strategy 1 (Automatic Pruning)
- Implement Strategy 2 (Size-Based Safety Valve)
- Implement Strategy 4 (Manual Nuke)

**Phase 6+ (Production):**
- Add Strategy 3 (Archive and Rotate) if history needed

**Default Config:** `.agent-os/config.json`
```json
{
  "personas": {
    "database": {
      "cleanup_schedule": "daily",
      "cleanup_time": "03:00",
      "retention_days": {
        "complete": 7,
        "failed": 30,
        "cancelled": 7,
        "pending": 1,
        "running": 0.1
      },
      "size_limit_mb": 100,
      "hard_limit_mb": 150
    }
  }
}
```

---

### Monitoring and Observability

**MCP Tool for Database Stats:**

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
            "oldest_job_days": 28,
            "estimated_cleanup_date": "2025-10-13",
            "next_cleanup": "2025-10-07 03:00:00"
        }
    """
    db_size = job_manager._get_db_size() / 1024 / 1024
    
    total_jobs = job_manager.db.execute(
        "SELECT COUNT(*) FROM persona_jobs"
    ).fetchone()[0]
    
    jobs_by_status = {}
    for status in ["complete", "failed", "running", "pending", "cancelled"]:
        count = job_manager.db.execute(
            "SELECT COUNT(*) FROM persona_jobs WHERE status = ?",
            (status,)
        ).fetchone()[0]
        jobs_by_status[status] = count
    
    oldest_job = job_manager.db.execute(
        "SELECT MIN(created_at) FROM persona_jobs"
    ).fetchone()[0]
    
    if oldest_job:
        oldest_days = (time.time() - oldest_job) / 86400
    else:
        oldest_days = 0
    
    last_cleanup = job_manager._get_last_cleanup_time()
    next_cleanup = last_cleanup + 86400
    
    return {
        "database_size_mb": round(db_size, 2),
        "total_jobs": total_jobs,
        "jobs_by_status": jobs_by_status,
        "oldest_job_days": round(oldest_days, 1),
        "next_cleanup": datetime.fromtimestamp(next_cleanup).isoformat(),
        "cleanup_recommendation": (
            "healthy" if db_size < 50
            else "schedule cleanup soon" if db_size < 100
            else "cleanup recommended" if db_size < 150
            else "cleanup urgent"
        )
    }
```

**Example Output:**
```json
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
```

---

### Maintenance Runbook

**Daily (Automatic):**
1. Cleanup task runs at 3 AM
2. Deletes jobs older than retention period
3. Runs VACUUM to reclaim space
4. Logs results

**Weekly (Manual Check):**
```python
# Check database health
await persona_database_stats()

# Expected: <50MB, <1000 jobs
```

**Monthly (Manual Cleanup if Needed):**
```python
# Dry run to see what would be deleted
result = job_manager.cleanup_old_jobs(dry_run=True)
# Shows: "Would delete 450 jobs, free 15MB"

# If acceptable, run for real
result = job_manager.cleanup_old_jobs()
```

**Emergency (Database Full):**
```python
# Option 1: Aggressive cleanup (keeps last 3 days only)
job_manager.cleanup_old_jobs(retention_override={"complete": 3, "failed": 7})

# Option 2: Nuclear option (delete everything)
await reset_persona_jobs(confirm=True)
```

---

### Disaster Recovery

**Backup Strategy:**

```bash
# Backup before major cleanup
cp .agent-os/.cache/persona_jobs.db .agent-os/.cache/persona_jobs_backup_2025-10-06.db

# Compress backups (70% reduction)
gzip .agent-os/.cache/persona_jobs_backup_*.db

# Keep last 3 monthly backups
find .agent-os/.cache -name "persona_jobs_backup_*.db.gz" -mtime +90 -delete
```

**Restore from Backup:**

```bash
# Stop MCP server
pkill -f agent_os_rag

# Restore backup
cp .agent-os/.cache/persona_jobs_backup_2025-10-06.db .agent-os/.cache/persona_jobs.db

# Restart MCP server
# (Cursor will auto-restart)
```

**Database Corruption Recovery:**

```python
# Check integrity
result = job_manager.db.execute("PRAGMA integrity_check").fetchone()

if result[0] != "ok":
    logger.error("Database corrupted!")
    
    # Attempt repair
    job_manager.db.execute("REINDEX")
    job_manager.db.execute("VACUUM")
    
    # If still broken, restore from backup or nuke
```

---

### Summary: Maintenance Strategy

**Recommended Approach:**

1. ✅ **Automatic Pruning (Default)**
   - Runs daily at 3 AM
   - Keeps complete jobs 7 days, failed jobs 30 days
   - Target: <100MB database

2. ✅ **Size-Based Safety Valve**
   - Triggers if DB exceeds 100MB
   - More aggressive cleanup (3 day retention)
   - Rejects jobs if exceeds 150MB hard limit

3. ✅ **Manual Nuke Option**
   - `reset_persona_jobs(confirm=True)` for emergencies
   - Complete reset in <1 second

4. ⚠️ **Archive (Optional, Phase 6+)**
   - If team wants indefinite history
   - Moves old jobs to separate archive DB

**Implementation Complexity:**
- Automatic pruning: ~150 lines
- Safety valve: ~50 lines
- Manual nuke: ~30 lines
- **Total: ~230 lines** (acceptable for robust maintenance)

**Expected Outcome:**
- Database stays <50MB (target)
- Max 100MB (typical)
- Never exceeds 150MB (hard limit)
- Fully automatic, no manual intervention needed

