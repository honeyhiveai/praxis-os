# Agent OS Persona System - Implementation Details

**Code-level guidance, examples, and patterns.**

---

## 🔄 ASYNC EXECUTION MODEL

**All persona invocations use async background execution.** This eliminates timeout issues and provides progress visibility.

**Architecture:** See [async-persona-execution-architecture.md](supporting-docs/async-persona-execution-architecture.md) for complete design (3,295 lines).

**Key Components:**
- **Job Queue Manager** - Creates and tracks background jobs (SQLite)
- **Worker Pool** - 3 background threads execute personas
- **Progress Tracking** - Real-time updates every 5 seconds
- **Polling Tools** - Main agent polls for status/results

**Implementation covered in this document:**
- Persona prompts and MCP tool registration (this file)
- Async infrastructure (job queue, workers, database) - see async architecture doc

---

## 🏗️ DIRECTORY STRUCTURE

```
mcp_server/
├── agent_os_rag.py              # Main MCP server (ADD persona tools here)
├── models.py                     # ADD PersonaConfig, JobState, ProgressUpdate
├── job_manager.py                # NEW: Async job queue manager
├── background_worker.py          # NEW: Worker pool for async execution
├── persona_executor.py           # NEW: Persona execution with progress tracking
├── personas/                     # NEW directory
│   ├── __init__.py              # Exports CORE_PERSONAS registry
│   ├── loader.py                # Prompt loading utility
│   ├── architect.md             # Architect system prompt
│   ├── engineer.md              # Engineer system prompt
│   ├── data.md                  # Data Engineer system prompt
│   ├── qa.md                    # QA Engineer system prompt
│   ├── security.md              # Security Engineer system prompt
│   └── sre.md                   # SRE system prompt
├── standard_creator.py          # NEW: Standard file creation utility
├── metrics.py                   # NEW: Metrics tracking
└── migrations/
    └── 001_persona_jobs.sql     # NEW: Database schema

universal/
├── usage/
│   ├── persona-guide.md         # NEW: How to use personas
│   └── creating-standards.md    # NEW: How to create standards
└── templates/
    └── standard-template.md     # NEW: Standard file template

tests/
├── unit/
│   ├── test_persona_loader.py
│   ├── test_invoke_architect.py
│   ├── test_invoke_engineer.py
│   ├── test_standard_creator.py
│   └── test_metrics.py
└── integration/
    ├── test_persona_invocation.py
    └── test_standards_population.py
```

---

## 🔨 IMPLEMENTATION: PERSONA PROMPT SYSTEM

### File: `mcp_server/models.py`

**Add PersonaConfig dataclass:**

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class PersonaConfig:
    """Configuration for a specialized AI persona."""
    name: str                    # Display name (e.g., "Software Architect")
    identifier: str              # Unique ID (e.g., "architect")
    system_prompt: str           # Optimized prompt text (≤1,500 tokens)
    standard_directory: str      # Where this persona creates standards (e.g., "architecture")
    mcp_tool_name: str          # MCP tool name (e.g., "invoke_architect")
    priority: str               # "core" or "specialist"
    description: str            # Short description for docs

@dataclass
class JobState:
    """State of an async persona job."""
    id: str                          # UUID
    persona: str                     # e.g., "architect"
    task: str                        # User's request
    context: Optional[str]           # File contents, etc.
    status: str                      # "pending" | "running" | "complete" | "failed"
    priority: str                    # "low" | "normal" | "high"
    progress_phase: Optional[str]    # "initializing" | "searching" | "analyzing" | "generating"
    progress_percent: int            # 0-100
    progress_message: Optional[str]  # Human-readable status
    result: Optional[str]            # Final persona output
    error: Optional[str]             # Error message if failed
    created_at: float                # Unix timestamp
    started_at: Optional[float]
    completed_at: Optional[float]
    tool_calls_made: int
    tokens_input: Optional[int]
    tokens_output: Optional[int]

@dataclass
class ProgressUpdate:
    """Progress update for a running job."""
    phase: str                       # "initializing" | "searching" | "analyzing" | "generating"
    percent_complete: int            # 0-100
    message: str                     # Human-readable status
    eta_seconds: Optional[int]       # Estimated seconds remaining
    tool_calls_completed: int
    elapsed_seconds: float
```

---

### File: `mcp_server/personas/loader.py`

**Prompt loading utility:**

```python
"""Persona prompt loading utilities."""

from pathlib import Path
from typing import Dict
from mcp_server.models import PersonaConfig

PERSONAS_DIR = Path(__file__).parent

def load_persona_prompt(identifier: str) -> str:
    """
    Load persona system prompt from markdown file.
    
    Args:
        identifier: Persona identifier (e.g., "architect", "engineer")
    
    Returns:
        System prompt text
    
    Raises:
        FileNotFoundError: If persona file doesn't exist
    """
    prompt_file = PERSONAS_DIR / f"{identifier}.md"
    
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Persona prompt not found: {identifier}.md"
        )
    
    return prompt_file.read_text(encoding="utf-8")


def get_all_personas() -> Dict[str, PersonaConfig]:
    """
    Get all available persona configurations.
    
    Returns:
        Dictionary mapping identifier -> PersonaConfig
    """
    personas = {}
    
    for prompt_file in PERSONAS_DIR.glob("*.md"):
        identifier = prompt_file.stem
        
        # Skip files that aren't persona prompts
        if identifier in ["__init__", "loader"]:
            continue
        
        # Load prompt
        prompt_text = load_persona_prompt(identifier)
        
        # Parse metadata from prompt (assumes front matter)
        metadata = _parse_prompt_metadata(prompt_text)
        
        personas[identifier] = PersonaConfig(
            name=metadata.get("name", identifier.title()),
            identifier=identifier,
            system_prompt=prompt_text,
            standard_directory=metadata.get("standard_directory", identifier),
            mcp_tool_name=f"invoke_{identifier}",
            priority=metadata.get("priority", "core"),
            description=metadata.get("description", "")
        )
    
    return personas


def _parse_prompt_metadata(prompt_text: str) -> Dict[str, str]:
    """
    Parse YAML front matter from prompt.
    
    Expected format:
    ---
    name: Software Architect
    standard_directory: architecture
    priority: core
    description: System design and architecture reviews
    ---
    
    Args:
        prompt_text: Prompt text with optional front matter
    
    Returns:
        Metadata dictionary
    """
    metadata = {}
    
    if not prompt_text.startswith("---"):
        return metadata
    
    lines = prompt_text.split("\n")
    in_front_matter = False
    
    for line in lines[1:]:  # Skip first "---"
        if line.strip() == "---":
            break
        
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    
    return metadata
```

---

### File: `mcp_server/personas/__init__.py`

**Persona registry:**

```python
"""Agent OS Personas - Specialized AI experts."""

from mcp_server.personas.loader import load_persona_prompt, get_all_personas

# Load all personas on module import
CORE_PERSONAS = get_all_personas()

# Convenience exports
__all__ = [
    "CORE_PERSONAS",
    "load_persona_prompt",
    "get_all_personas",
]
```

---

## 🔨 IMPLEMENTATION: ASYNC PERSONA MCP TOOLS

### File: `mcp_server/agent_os_rag.py`

**Add async persona invocation tools:**

```python
from mcp_server.personas import CORE_PERSONAS
from mcp_server.job_manager import JobManager
from mcp_server.background_worker import WorkerPool
from mcp_server.persona_executor import PersonaExecutor
import anthropic

# Initialize components (on server startup)
job_manager = JobManager(db_path=".agent-os/.cache/persona_jobs.db")
persona_executor = PersonaExecutor(
    llm_client=anthropic.Anthropic(),
    rag_engine=rag_engine
)
worker_pool = WorkerPool(
    job_manager=job_manager,
    persona_executor=persona_executor,
    num_workers=3
)
worker_pool.start()


@mcp.tool()
async def invoke_architect(
    task: str,
    context: Optional[str] = None,
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    Invoke Software Architect persona (async background job).
    
    The Architect persona specializes in:
    - System architecture and design patterns
    - Performance and scalability design
    - Concurrency architecture
    - API design principles
    - High-level data architecture
    
    Args:
        task: What to review/design (e.g., "review this API design")
        context: Optional context (file contents, descriptions)
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
    
    Example:
        result = await invoke_architect(
            task="Review the architecture of our payment processing system",
            context="<file contents>"
        )
        job_id = result["job_id"]
        
        # Main agent polls until complete
        while True:
            status = await check_persona_job(job_id)
            if status["status"] == "complete":
                print(status["result"])
                break
            elif status["status"] == "running":
                print(f"Progress: {status['progress']['message']}")
            await asyncio.sleep(5)
    """
    # Create background job
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


@mcp.tool()
async def invoke_engineer(
    task: str,
    context: Optional[str] = None
) -> str:
    """
    Invoke Software Engineer persona for code review and implementation guidance.
    
    The Engineer persona specializes in:
    - Code quality and design
    - Performance optimization
    - Thread-safety and concurrency
    - Refactoring strategies
    - Implementation patterns
    
    Args:
        task: What to review/implement (e.g., "review this code for thread-safety")
        context: Optional context
    
    Returns:
        Engineer's review, recommendations, and potential standard proposals
    """
    return _invoke_persona("engineer", task, context)


@mcp.tool()
async def invoke_data(
    task: str,
    context: Optional[str] = None
) -> str:
    """
    Invoke Data Engineer persona for data architecture and pipeline design.
    
    The Data Engineer persona specializes in:
    - Data pipeline architecture (Kafka, Airflow, etc.)
    - ETL/ELT design
    - Data modeling
    - Data quality patterns
    - Tech stack best practices
    
    Args:
        task: What to review/design (e.g., "review Kafka topic design")
        context: Optional context
    
    Returns:
        Data Engineer's review, recommendations, and potential standard proposals
    """
    return _invoke_persona("data", task, context)


@mcp.tool()
async def invoke_qa(
    task: str,
    context: Optional[str] = None
) -> str:
    """
    Invoke QA Engineer persona for testing strategy and test review.
    
    The QA Engineer persona specializes in:
    - Testing strategy (unit, integration, e2e)
    - Test coverage analysis
    - Edge case identification
    - Test quality assessment
    - Test pattern recommendations
    
    Args:
        task: What to review (e.g., "review test coverage for this module")
        context: Optional context
    
    Returns:
        QA Engineer's review, recommendations, and potential standard proposals
    """
    return _invoke_persona("qa", task, context)


@mcp.tool()
async def invoke_security(
    task: str,
    context: Optional[str] = None
) -> str:
    """
    Invoke Security Engineer persona for security review and threat modeling.
    
    The Security Engineer persona specializes in:
    - Security vulnerability identification (OWASP Top 10)
    - Threat modeling
    - Secure coding patterns
    - Authentication/authorization design
    - Security best practices
    
    Args:
        task: What to review (e.g., "security review of authentication flow")
        context: Optional context
    
    Returns:
        Security Engineer's review, findings, and potential standard proposals
    """
    return _invoke_persona("security", task, context)


@mcp.tool()
async def invoke_sre(
    task: str,
    context: Optional[str] = None
) -> str:
    """
    Invoke SRE persona for production readiness and operational excellence.
    
    The SRE persona specializes in:
    - Production readiness reviews
    - SLO/SLI design
    - Observability (metrics, logs, traces)
    - Deployment strategies
    - Operational risk assessment
    
    Args:
        task: What to review (e.g., "production readiness check")
        context: Optional context
    
    Returns:
        SRE's review, findings, and potential standard proposals
    """
    return _invoke_persona("sre", task, context)
```

---

## 🔨 IMPLEMENTATION: STANDARDS CREATION

### File: `mcp_server/standard_creator.py`

**Standard file creation utility:**

```python
"""Utilities for creating project standards."""

from pathlib import Path
from datetime import datetime
from typing import Optional

def create_standard(
    base_path: Path,
    domain: str,
    topic: str,
    content: str,
    created_by: str,
    approved_by: str,
    tags: Optional[list[str]] = None
) -> tuple[bool, str]:
    """
    Create a new project standard file.
    
    Args:
        base_path: Path to .agent-os/standards/ directory
        domain: Domain directory (e.g., "architecture", "data")
        topic: Standard topic/filename (e.g., "api-conventions")
        content: Standard content (markdown)
        created_by: Persona that created it (e.g., "architect")
        approved_by: Human who approved it (e.g., "josh")
        tags: Optional searchable tags
    
    Returns:
        (success: bool, message: str)
    """
    # Validate inputs
    if not topic or not content or not approved_by:
        return False, "Missing required fields: topic, content, or approved_by"
    
    # Build file path
    domain_dir = base_path / domain
    file_path = domain_dir / f"{topic}.md"
    
    # Check if file already exists
    if file_path.exists():
        return False, f"Standard already exists: {domain}/{topic}.md"
    
    # Create domain directory if needed
    domain_dir.mkdir(parents=True, exist_ok=True)
    
    # Build front matter
    front_matter = _build_front_matter(
        created_by=created_by,
        approved_by=approved_by,
        tags=tags or []
    )
    
    # Combine front matter + content
    full_content = f"{front_matter}\n{content}"
    
    # Write file
    try:
        file_path.write_text(full_content, encoding="utf-8")
        return True, f"Standard created: {domain}/{topic}.md"
    except Exception as e:
        return False, f"Failed to create standard: {str(e)}"


def _build_front_matter(
    created_by: str,
    approved_by: str,
    tags: list[str]
) -> str:
    """Build YAML front matter for standard."""
    now = datetime.now().isoformat()
    
    front_matter = [
        "---",
        f"created_by: {created_by}",
        f"approved_by: {approved_by}",
        f"created_at: {now}",
        f"last_updated: {now}",
        f"tags: [{', '.join(tags)}]",
        "---",
    ]
    
    return "\n".join(front_matter)
```

---

### File: `mcp_server/agent_os_rag.py`

**Add create_standard MCP tool:**

```python
from mcp_server.standard_creator import create_standard

@mcp.tool()
async def create_project_standard(
    domain: str,
    topic: str,
    content: str,
    created_by: str,
    approved_by: str,
    tags: Optional[list[str]] = None
) -> str:
    """
    Create a new project-specific standard file.
    
    This tool should ONLY be called after Human approval.
    The persona proposes the standard, Human approves, then this creates the file.
    
    Args:
        domain: Domain directory (e.g., "architecture", "data", "testing")
        topic: Standard topic (e.g., "api-conventions", "kafka-patterns")
        content: Full standard content (markdown)
        created_by: Persona that created it (e.g., "architect", "data")
        approved_by: Human who approved it (username)
        tags: Optional searchable tags (e.g., ["rest-api", "versioning"])
    
    Returns:
        Success/failure message
    
    Example:
        create_project_standard(
            domain="architecture",
            topic="api-conventions",
            content="# API Conventions\n\n## Context\n...",
            created_by="architect",
            approved_by="josh",
            tags=["rest-api", "versioning"]
        )
    """
    standards_path = base_path / "standards"
    
    success, message = create_standard(
        base_path=standards_path,
        domain=domain,
        topic=topic,
        content=content,
        created_by=created_by,
        approved_by=approved_by,
        tags=tags
    )
    
    if success:
        # File watcher will automatically detect and index
        message += "\n\nStandard will be indexed and searchable within 30 seconds."
    
    return message
```

---

## 📄 EXAMPLE: ARCHITECT PERSONA PROMPT

### File: `mcp_server/personas/architect.md`

```markdown
---
name: Software Architect
standard_directory: architecture
priority: core
description: System design, architecture patterns, scalability, and API design
---

# IDENTITY: SOFTWARE ARCHITECT

You are a Senior Software Architect with 15+ years of experience designing large-scale distributed systems. Your expertise spans system architecture, performance design, API design, concurrency patterns, and scalability.

## YOUR EXPERTISE

**Core Competencies:**
- System architecture and design patterns
- Performance and scalability design
- Concurrency architecture (thread-safety, race conditions, deadlocks)
- API design principles (REST, GraphQL, gRPC)
- Database architecture (high-level)
- Microservices vs monoliths
- Event-driven architecture
- Caching strategies
- Architectural trade-offs

**Review Focus:**
1. System design: Is architecture sound and scalable?
2. Performance: Will this design perform at scale?
3. Concurrency: Are race conditions/deadlocks possible?
4. API design: Is API intuitive, consistent, versioned?
5. Patterns: Are appropriate design patterns used?

## REVIEW TEMPLATE

**Use this structure for all reviews:**

### 🎯 Architecture Assessment

**Strengths:**
- [List what's well-designed]

**Concerns:**
- [List design issues, with severity: 🚨 Critical, ⚠️ Important, 💭 Consider]

**Recommendations:**
- [Specific, actionable recommendations]

### 📊 Scalability Analysis

[Performance/scalability concerns and solutions]

### 🔄 Concurrency Considerations

[Thread-safety, race conditions, locking concerns if applicable]

### 💡 Pattern Opportunities

[Suggest design patterns where appropriate]

---

## STANDARDS POPULATION CAPABILITY

**When you identify a pattern worth standardizing:**

1. **Detect Pattern**: If you see a good architectural pattern that could benefit the project, propose it
2. **Ask Permission**: "I notice [pattern]. May I document this as a project standard?"
3. **Wait for Approval**: Do not proceed without Human saying "yes"
4. **Generate Standard**: Use standard template with:
   - Context (why this matters for this project)
   - Pattern (the architectural approach)
   - Examples (code/diagrams showing pattern)
   - Anti-patterns (what to avoid)
   - When to revisit (triggers for re-evaluation)
5. **Human Review**: Present draft, incorporate feedback
6. **Finalize**: On approval, call `create_project_standard()` with:
   - domain: "architecture"
   - topic: descriptive name (e.g., "api-versioning-strategy")
   - content: full standard markdown
   - created_by: "architect"
   - approved_by: [Human's username]
   - tags: relevant tags (e.g., ["api", "versioning"])

**Standard Creation Rules:**
- Only propose standards for patterns you observe in THIS project
- Never create standards autonomously (always Human-approved)
- Focus on architectural patterns, not implementation details
- Keep standards practical and actionable

---

## CONSTRAINTS

- Language-agnostic: Review principles, not language-specific syntax
- No code execution: You review and recommend only
- Project context: Query `search_standards()` for project-specific patterns
- Cite sources: Reference project standards when making recommendations

---

## RESPONSE GUIDELINES

- Be direct and actionable
- Use severity markers: 🚨 Critical, ⚠️ Important, 💭 Consider
- Prioritize: Most critical issues first
- Be specific: "Change X to Y because Z" (not vague advice)
- Token efficiency: No fluff, only substance
```

---

## 🧪 TESTING EXAMPLES

### Unit Test: Persona Loader

```python
# tests/unit/test_persona_loader.py

import pytest
from mcp_server.personas.loader import load_persona_prompt, get_all_personas

def test_load_architect_prompt():
    """Test loading architect persona prompt."""
    prompt = load_persona_prompt("architect")
    
    assert "Software Architect" in prompt
    assert "IDENTITY" in prompt
    assert len(prompt) < 10000  # Reasonable size check

def test_load_nonexistent_persona():
    """Test error handling for missing persona."""
    with pytest.raises(FileNotFoundError):
        load_persona_prompt("nonexistent")

def test_get_all_personas():
    """Test loading all persona configs."""
    personas = get_all_personas()
    
    assert "architect" in personas
    assert "engineer" in personas
    assert personas["architect"].name == "Software Architect"
    assert personas["architect"].standard_directory == "architecture"
    assert personas["architect"].priority == "core"
```

### Integration Test: Persona Invocation

```python
# tests/integration/test_persona_invocation.py

import pytest
from mcp_server.agent_os_rag import invoke_architect

@pytest.mark.asyncio
async def test_invoke_architect_review():
    """Test architect persona invocation."""
    task = "Review this REST API design"
    context = """
    GET /api/v1/users
    POST /api/v1/users
    GET /api/v1/users/{id}
    """
    
    response = await invoke_architect(task, context)
    
    assert response is not None
    assert len(response) > 100  # Non-trivial response
    assert "API" in response or "REST" in response  # Relevant to task
```

---

**This completes the technical specification. Implementation ready to begin.**
