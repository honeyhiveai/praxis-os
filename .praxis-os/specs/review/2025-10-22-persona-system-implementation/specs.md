# Technical Specifications

**Project:** Persona System Implementation  
**Date:** 2025-10-22  
**Based on:** srd.md (requirements), supporting design documents

---

## 1. Architecture Overview

### 1.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent OS Enhanced                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Main Agent (Cursor IDE)                             │   │
│  │ - User interface                                     │   │
│  │ - Task routing                                       │   │
│  │ - Invokes specialists via MCP                       │   │
│  └─────────────────┬───────────────────────────────────┘   │
│                    │ MCP invoke_specialist tool             │
│                    ▼                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ MCP Server (Python Process)                         │   │
│  │ ┌─────────────────────────────────────────────────┐ │   │
│  │ │ invoke_specialist Tool Handler                  │ │   │
│  │ │ - Validates persona exists                      │ │   │
│  │ │ - Routes to PersonaLauncher                     │ │   │
│  │ └─────────────┬──────────────────────────────────  │ │   │
│  │               │                                      │ │   │
│  │               ▼                                      │ │   │
│  │ ┌─────────────────────────────────────────────────┐ │   │
│  │ │ PersonaLauncher (Single Implementation)         │ │   │
│  │ │ - Load persona from .md file                    │ │   │
│  │ │ - Initialize LLM with system prompt             │ │   │
│  │ │ - Execute agentic loop                          │ │   │
│  │ │ - Track metrics                                 │ │   │
│  │ └─────────────┬──────────────────────────────────  │ │   │
│  │               │                                      │ │   │
│  │               ├─── Uses ───► LLM Client            │ │   │
│  │               │              (Claude/OpenAI)        │ │   │
│  │               │                                      │ │   │
│  │               └─── Uses ───► MCP Client            │ │   │
│  │                              (Tool Executor)        │ │   │
│  └─────────────────────────────────────────────────────┘   │
│                    │ queries                                │
│                    ▼                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Knowledge Layer                                      │   │
│  │ - RAG Engine: search_standards()                    │   │
│  │ - Workflow Engine: start_workflow()                 │   │
│  │ - Standards: .praxis-os/standards/                   │   │
│  │ - Workflows: .praxis-os/workflows/                   │   │
│  │ - Personas: .praxis-os/personas/ (config)            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Key Components:**
- **Main Agent (Cursor):** User-facing interface, delegates to specialists
- **MCP Tool Handler:** Entry point for specialist invocation
- **PersonaLauncher:** Core execution engine (single implementation)
- **LLM Client:** Stateless API wrapper for Claude/OpenAI
- **MCP Client:** Tool executor for specialist capabilities
- **Persona Files:** Configuration-driven specialist definitions (.md files)
- **Knowledge Layer:** RAG search, workflows, standards

**Architectural Principles:**
1. **Config-Driven:** Personas as markdown files (zero-code extensibility)
2. **Single Responsibility:** PersonaLauncher handles ALL personas (no per-persona code)
3. **Discovery-Based:** RAG semantic search for workflows/patterns (no hardcoding)
4. **Local-First:** No deployment infrastructure required
5. **Stateless Execution:** Each specialist run is independent
6. **Observable:** Comprehensive metrics tracking

### 1.2 Architectural Decisions

#### Decision 1: Personas as Markdown Files vs Python Classes

**Decision:** Implement personas as `.md` configuration files loaded dynamically, not as Python code classes.

**Rationale:** 
- **FR-002**: Persona file format requirement
- **Goal 2**: Enable zero-code specialist extensibility
- Non-programmers can create specialists
- No code changes, deployment, or restarts needed
- Version control in Git tracks persona evolution
- Dynamic loading enables runtime discovery

**Alternatives Considered:**
- **Python Classes:** Traditional OOP approach with inheritance
  - **Why not:** Requires code changes, deployment, restart for new personas
  - **Why not:** 200+ lines per specialist vs 50-100 lines markdown
  - **Why not:** Developer-only (non-programmers excluded)

- **JSON/YAML Configuration:** Structured data format
  - **Why not:** Less human-readable than markdown
  - **Why not:** Doesn't support rich documentation/examples
  - **Why not:** Markdown already used throughout Agent OS

**Trade-offs:**
- **Pros:** 
  - <5 minute persona creation time (vs 4 hours with code)
  - Infinite extensibility without framework changes
  - Team-accessible (non-developers can contribute)
  - Git-based version control
  
- **Cons:** 
  - No compile-time type checking
  - Runtime validation required
  - Potential for inconsistent persona quality
  - **Mitigation:** Persona template, validation tools, testing guide

#### Decision 2: Single PersonaLauncher Implementation

**Decision:** One `PersonaLauncher` class handles all personas through file loading.

**Rationale:**
- **FR-001**: PersonaLauncher core execution engine
- **Goal 2**: Reduce maintenance burden
- All persona-specific behavior comes from file content, not code branches
- Consistent execution model for all specialists
- Easy to add telemetry/logging/debugging
- Predictable resource usage

**Alternatives Considered:**
- **Per-Persona Classes:** Each specialist has dedicated Python class
  - **Why not:** 10 specialists = 10 classes = code sprawl
  - **Why not:** Maintenance burden multiplies with specialist count
  
- **Plugin Architecture:** Dynamic class loading
  - **Why not:** Overcomplicated for use case
  - **Why not:** Still requires Python code per specialist

**Trade-offs:**
- **Pros:**
  - One implementation to maintain
  - Consistent metrics/logging
  - Easy to enhance all personas at once
  
- **Cons:**
  - Less opportunity for persona-specific optimizations
  - **Mitigation:** Configurable behavior via persona files

#### Decision 3: RAG-Based Discovery vs Hardcoded Workflows

**Decision:** Specialists discover workflows dynamically via `search_standards()` queries.

**Rationale:**
- **FR-004**: Discovery pattern integration
- **Goal 3**: Self-improving knowledge system
- Zero hardcoding = workflows instantly discoverable when added
- Cross-domain knowledge sharing (any specialist can find any workflow)
- System teaches itself through accumulated standards

**Alternatives Considered:**
- **Hardcoded Workflow References:** Personas include explicit workflow names
  - **Why not:** Breaks when workflows renamed/versioned
  - **Why not:** Personas need updates when workflows change
  - **Why not:** Defeats discovery architecture principle

- **Registry Pattern:** Central workflow registry
  - **Why not:** Maintenance burden
  - **Why not:** Discoverability limited to registered workflows

**Trade-offs:**
- **Pros:**
  - Zero maintenance when adding workflows
  - New workflows instantly available to all specialists
  - Cross-pollination of knowledge
  
- **Cons:**
  - Query quality affects discovery success
  - **Mitigation:** Teach query patterns in persona prompts, optimize RAG indexing

#### Decision 4: Agentic Loop with Max Iterations

**Decision:** Implement while loop with 50-iteration safety limit.

**Rationale:**
- **FR-012**: Agentic loop implementation
- **NFR-P2**: Specialist execution time limits
- Enables autonomous multi-tool execution
- Prevents infinite loops
- Balance between capability and cost control

**Alternatives Considered:**
- **Single LLM Call:** No loop, one-shot execution
  - **Why not:** Can't handle multi-step tasks
  - **Why not:** No tool usage capability

- **Unlimited Iterations:** Loop until completion
  - **Why not:** Risk of infinite loops (costly)
  - **Why not:** No timeout protection

**Trade-offs:**
- **Pros:**
  - Autonomous execution for complex tasks
  - Safety limit prevents runaway costs
  
- **Cons:**
  - Complex tasks might hit limit
  - **Mitigation:** Return partial results, allow resume

#### Decision 5: Local-First, No Deployment Infrastructure

**Decision:** Personas run locally in MCP server process, no centralized specialist server.

**Rationale:**
- Architectural principle: local-first
- **Goal 2**: Zero deployment overhead
- Git-based sharing sufficient for teams
- No infrastructure costs
- Simpler security model

**Alternatives Considered:**
- **Centralized Specialist Server:** Cloud-hosted personas
  - **Why not:** Deployment complexity
  - **Why not:** Infrastructure costs
  - **Why not:** Network latency

- **Serverless Functions:** Persona-as-a-service
  - **Why not:** Cold start latency
  - **Why not:** Vendor lock-in

**Trade-offs:**
- **Pros:**
  - Zero infrastructure
  - Faster execution (no network)
  - Git-based sharing works
  
- **Cons:**
  - Manual setup per machine
  - **Mitigation:** Conversational installation process

### 1.3 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| FR-001 | PersonaLauncher class | Single implementation loads personas, executes agentic loop |
| FR-002 | Persona file loading | Markdown files in `.praxis-os/personas/`, dynamic loading |
| FR-003 | MCP tool registration | `invoke_specialist` tool routes to PersonaLauncher |
| FR-004 | Discovery pattern | `search_standards()` taught in persona prompts |
| FR-005 | Workflow integration | `start_workflow()`, `complete_phase()` in tool subset |
| FR-006 | Tool subset filtering | Filtered MCP tool list provided to specialists |
| FR-007 | write_standard tool | Creates markdown in `.praxis-os/standards/project/` |
| FR-008 | Metrics tracking | Return structure with tools, artifacts, duration, tokens, cost |
| FR-009 | Error handling | Graceful failures with helpful messages |
| FR-010 | Base personas | 4 baseline .md files (database, api, security, testing) |
| FR-011 | Persona template | Template file + documentation guide |
| FR-012 | Agentic loop | While loop with max 50 iterations |
| FR-013 | File organization | Standard `.praxis-os/` directory structure |
| FR-014 | LLM provider support | Unified client interface for Claude/OpenAI |
| FR-015 | Context management | Optional context parameter to `invoke_specialist` |

### 1.4 Technology Stack

**Backend (Python 3.10+):**
- Language: Python 3.10+ (async/await, type hints)
- MCP Server: FastMCP for tool registration
- LLM Client: Anthropic SDK (Claude), OpenAI SDK (GPT)
- Type Safety: mypy for static type checking

**Data Storage:**
- Persona Files: `.praxis-os/personas/*.md` (markdown)
- Standards: `.praxis-os/standards/` (markdown)
- RAG Index: LanceDB (vector store)
- Workflow State: JSON files (filesystem)

**External Services:**
- LLM API: Anthropic Claude (claude-3-5-sonnet-20241022)
- LLM API: OpenAI GPT (gpt-4o-mini-2024-07-18)

**Infrastructure:**
- Deployment: Local MCP server process
- Version Control: Git
- Configuration: Environment variables, .env files

---

## 2. Component Design

### 2.1 Component: PersonaLauncher

**Purpose:** Core execution engine that loads persona definitions and executes specialists through an agentic loop.

**Responsibilities:**
- Load persona markdown file from `.praxis-os/personas/`
- Initialize LLM conversation with persona as system prompt
- Execute agentic loop (call LLM → execute tools → repeat)
- Track metrics (tools, artifacts, duration, tokens, cost)
- Handle errors gracefully
- Return structured results

**Requirements Satisfied:**
- FR-001: Core execution engine
- FR-002: Persona file loading
- FR-008: Metrics tracking
- FR-009: Error handling
- FR-012: Agentic loop implementation

**Public Interface:**
```python
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time

PERSONA_DIR = Path(".praxis-os/personas")

@dataclass
class SpecialistResult:
    """Structured result from specialist execution."""
    persona: str
    result: str  # Main output text
    tools_used: List[str]  # Tool names called
    artifacts: List[str]  # Files created
    iterations: int  # Agentic loop count
    duration_ms: float  # Execution time
    tokens: int  # Total token usage
    cost: float  # API cost in USD
    error: Optional[str] = None  # Error message if failed

class PersonaLauncher:
    """
    Core execution engine for specialist personas.
    
    Single implementation handles all personas through dynamic
    file loading. Persona-specific behavior comes from markdown
    file content, not code branches.
    
    Addresses FR-001, FR-002, FR-008, FR-009, FR-012.
    """
    
    def __init__(
        self,
        mcp_client: MCPClient,
        llm_client: LLMClient,
        max_iterations: int = 50
    ):
        """
        Initialize PersonaLauncher.
        
        Args:
            mcp_client: Client for MCP tool execution
            llm_client: Client for LLM API calls
            max_iterations: Safety limit for agentic loop
        """
        self.mcp = mcp_client
        self.llm = llm_client
        self.max_iterations = max_iterations
    
    async def run(
        self,
        persona_name: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> SpecialistResult:
        """
        Execute persona on task.
        
        Loads persona from .md file, initializes conversation,
        executes agentic loop until completion or max iterations.
        
        Args:
            persona_name: Persona filename without .md
            task: Task description from user/main agent
            context: Optional context (project info, constraints)
        
        Returns:
            SpecialistResult with output, metrics, errors
        
        Example:
            result = await launcher.run(
                persona_name="database",
                task="Design auth schema with OAuth support",
                context={"db_type": "postgresql", "version": "15"}
            )
        """
        start_time = time.time()
        
        # 1. Load persona definition
        system_prompt = self._load_persona(persona_name)
        if isinstance(system_prompt, dict) and "error" in system_prompt:
            # Persona not found
            return SpecialistResult(
                persona=persona_name,
                result="",
                tools_used=[],
                artifacts=[],
                iterations=0,
                duration_ms=0,
                tokens=0,
                cost=0,
                error=system_prompt["error"]
            )
        
        # 2. Initialize conversation
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        
        if context:
            messages.append({
                "role": "user",
                "content": f"Additional context: {json.dumps(context)}"
            })
        
        # 3. Get filtered tool schemas
        tools = self._get_tool_schemas()
        
        # 4. Execute agentic loop
        result = await self._agentic_loop(
            messages=messages,
            tools=tools,
            persona_name=persona_name,
            start_time=start_time
        )
        
        return result
    
    def _load_persona(self, persona_name: str) -> Union[str, Dict]:
        """
        Load persona from markdown file.
        
        File content becomes system prompt verbatim.
        Addresses FR-002.
        
        Args:
            persona_name: Filename without .md extension
        
        Returns:
            str: Persona content as system prompt
            Dict: Error with available personas if not found
        """
        persona_file = PERSONA_DIR / f"{persona_name}.md"
        
        if not persona_file.exists():
            available = sorted([f.stem for f in PERSONA_DIR.glob("*.md")])
            return {
                "error": f"Persona '{persona_name}' not found",
                "available": available,
                "suggestion": f"Create: .praxis-os/personas/{persona_name}.md",
                "template": "See DESIGN-Persona-System.md for template"
            }
        
        return persona_file.read_text(encoding="utf-8")
    
    def _get_tool_schemas(self) -> List[Dict]:
        """
        Get filtered MCP tool schemas for specialists.
        
        Addresses FR-006: Tool subset filtering.
        
        Returns:
            List of tool schemas (JSON schema format)
        """
        # Tools available to specialists
        included_tools = [
            # Knowledge tools
            "search_standards",
            "search_codebase",
            "write_standard",
            # Workflow tools
            "start_workflow",
            "complete_phase",
            "get_current_phase",
            # File operations
            "access_file",
            "list_directory",
            "execute_command",
            # Framework tools
            "create_workflow",
            "validate_workflow",
            # Infrastructure
            "pos_browser"
        ]
        
        # Excluded: invoke_specialist (prevent recursion)
        
        # Get schemas from MCP server
        all_tools = self.mcp.list_tools()
        filtered = [
            tool for tool in all_tools
            if tool["name"] in included_tools
        ]
        
        return filtered
    
    async def _agentic_loop(
        self,
        messages: List[Dict],
        tools: List[Dict],
        persona_name: str,
        start_time: float
    ) -> SpecialistResult:
        """
        Execute agentic loop until completion or max iterations.
        
        Addresses FR-012: Agentic loop implementation.
        
        Loop pattern:
        1. Call LLM with messages and tools
        2. If tool calls: Execute tools, append results, continue
        3. If text response: Task complete, return result
        
        Args:
            messages: Conversation history
            tools: Tool schemas
            persona_name: For result structure
            start_time: For duration calculation
        
        Returns:
            SpecialistResult with metrics
        """
        tools_used = []
        artifacts = []
        total_tokens = 0
        total_cost = 0.0
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Call LLM
            response = await self.llm.call(
                messages=messages,
                tools=tools,
                temperature=0.7
            )
            
            # Track metrics
            total_tokens += response.usage.total_tokens
            total_cost += self._calculate_cost(response)
            
            # Check for tool calls
            if response.tool_calls:
                # Execute tools
                for tool_call in response.tool_calls:
                    result = await self.mcp.call_tool(
                        tool_call.name,
                        tool_call.arguments
                    )
                    
                    # Track usage
                    tools_used.append(tool_call.name)
                    
                    # Track artifacts
                    if tool_call.name in ["access_file", "write_standard"]:
                        if "path" in result:
                            artifacts.append(result["path"])
                    
                    # Append to conversation
                    messages.append({
                        "role": "assistant",
                        "content": response.content or "",
                        "tool_calls": [tool_call]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.name,
                        "content": json.dumps(result)
                    })
            else:
                # Text response = task complete
                duration_ms = (time.time() - start_time) * 1000
                
                return SpecialistResult(
                    persona=persona_name,
                    result=response.content,
                    tools_used=tools_used,
                    artifacts=artifacts,
                    iterations=iteration,
                    duration_ms=round(duration_ms, 2),
                    tokens=total_tokens,
                    cost=round(total_cost, 4)
                )
        
        # Max iterations reached
        duration_ms = (time.time() - start_time) * 1000
        
        return SpecialistResult(
            persona=persona_name,
            result=messages[-1]["content"] if messages else "",
            tools_used=tools_used,
            artifacts=artifacts,
            iterations=iteration,
            duration_ms=round(duration_ms, 2),
            tokens=total_tokens,
            cost=round(total_cost, 4),
            error="Max iterations reached (50). Partial result returned."
        )
    
    def _calculate_cost(self, response: LLMResponse) -> float:
        """
        Calculate API cost based on token usage and model.
        
        Addresses FR-008: Metrics tracking (cost).
        
        Args:
            response: LLM API response with usage info
        
        Returns:
            Cost in USD
        """
        # Claude Sonnet 3.5 pricing (example)
        if "claude" in response.model.lower():
            input_cost_per_1k = 0.003  # $3 per million
            output_cost_per_1k = 0.015  # $15 per million
        # OpenAI GPT-4o-mini pricing
        else:
            input_cost_per_1k = 0.00015  # $0.15 per million
            output_cost_per_1k = 0.0006  # $0.60 per million
        
        input_cost = (response.usage.input_tokens / 1000) * input_cost_per_1k
        output_cost = (response.usage.output_tokens / 1000) * output_cost_per_1k
        
        return input_cost + output_cost
```

**Dependencies:**
- Requires: MCPClient, LLMClient
- Provides: Specialist execution capability

**Error Handling:**
- Persona not found → Return error with available personas list
- Max iterations reached → Return partial result with error message
- LLM API error → Propagate with context
- Tool execution error → Wrapped in result message

### 2.2 Component: MCPClient

**Purpose:** Wrapper for MCP tool execution from PersonaLauncher.

**Responsibilities:**
- Execute MCP tools by name and arguments
- List available tools with schemas
- Handle tool execution errors
- Provide async interface

**Requirements Satisfied:**
- FR-001: PersonaLauncher requires tool execution
- FR-006: Tool schema listing

**Public Interface:**
```python
class MCPClient:
    """
    Client for executing MCP tools.
    
    Wraps MCP protocol communication for specialist use.
    """
    
    def __init__(self, mcp_server_connection):
        """Initialize with MCP server connection."""
        self.connection = mcp_server_connection
    
    def list_tools(self) -> List[Dict]:
        """
        List available MCP tools with schemas.
        
        Returns:
            List of tool definitions with schemas
        """
        pass
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute MCP tool.
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool parameters
        
        Returns:
            Tool result
        
        Raises:
            ToolExecutionError: If tool fails
        """
        pass
```

### 2.3 Component: LLMClient

**Purpose:** Unified interface for multiple LLM providers (Claude, OpenAI).

**Responsibilities:**
- Abstract provider-specific API differences
- Support tool calling (function calling)
- Handle rate limiting and retries
- Calculate token usage and costs

**Requirements Satisfied:**
- FR-014: LLM provider support
- NFR-R1: Error recovery with retries

**Public Interface:**
```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class LLMUsage:
    """Token usage information."""
    input_tokens: int
    output_tokens: int
    total_tokens: int

@dataclass
class ToolCall:
    """Tool call from LLM."""
    id: str
    name: str
    arguments: Dict[str, Any]

@dataclass
class LLMResponse:
    """Response from LLM API."""
    content: str
    model: str
    tool_calls: Optional[List[ToolCall]]
    usage: LLMUsage

class LLMClient:
    """
    Unified LLM client supporting multiple providers.
    
    Addresses FR-014: LLM provider support.
    """
    
    def __init__(
        self,
        provider: str,  # "anthropic" or "openai"
        model: str,
        api_key: str
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: "anthropic" or "openai"
            model: Model name (claude-3-5-sonnet-20241022, etc.)
            api_key: API key for provider
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        
        # Initialize provider-specific client
        if provider == "anthropic":
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=api_key)
        elif provider == "openai":
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def call(
        self,
        messages: List[Dict],
        tools: List[Dict],
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> LLMResponse:
        """
        Call LLM with messages and tools.
        
        Handles provider-specific differences and retries.
        Addresses NFR-R1: Auto retry with exponential backoff.
        
        Args:
            messages: Conversation history
            tools: Tool schemas (OpenAI function calling format)
            temperature: Sampling temperature
            max_retries: Retry attempts for failures
        
        Returns:
            LLMResponse with content, tool calls, usage
        
        Raises:
            LLMAPIError: After max retries exhausted
        """
        # Implementation handles provider-specific API calls
        # with exponential backoff retry logic
        pass
```

### 2.4 Component: Persona File Loader

**Purpose:** Validate and load persona markdown files.

**Responsibilities:**
- Validate file exists and is readable
- Parse markdown structure
- Extract sections (optional validation)
- Provide helpful errors

**Requirements Satisfied:**
- FR-002: Persona file format and loading
- FR-009: Error handling

**Public Interface:**
```python
from pathlib import Path
from typing import Optional, List

class PersonaLoader:
    """
    Loader and validator for persona markdown files.
    
    Addresses FR-002: Persona file format.
    """
    
    @staticmethod
    def load(persona_name: str) -> str:
        """
        Load persona file content.
        
        Args:
            persona_name: Filename without .md
        
        Returns:
            File content as string
        
        Raises:
            PersonaNotFoundError: If file doesn't exist
        """
        pass
    
    @staticmethod
    def list_available() -> List[str]:
        """
        List all available persona names.
        
        Returns:
            List of persona names (filenames without .md)
        """
        persona_dir = Path(".praxis-os/personas")
        return sorted([f.stem for f in persona_dir.glob("*.md")])
    
    @staticmethod
    def validate(persona_content: str) -> Optional[List[str]]:
        """
        Validate persona file structure.
        
        Checks for required sections (optional, for tooling).
        
        Args:
            persona_content: Markdown content
        
        Returns:
            None if valid, list of issues if invalid
        """
        required_sections = [
            "## Your Approach",
            "## Your Tools",
            "## Decision Protocol"
        ]
        
        issues = []
        for section in required_sections:
            if section not in persona_content:
                issues.append(f"Missing required section: {section}")
        
        return issues if issues else None
```

---

## 3. API Design

### 3.1 MCP Tool: invoke_specialist

**Purpose:** Main entry point for specialist invocation from main agent.

**Authentication:** Not required (local MCP server)

**Tool Schema:**
```json
{
  "name": "invoke_specialist",
  "description": "Invoke a domain specialist sub-agent with specific persona. Specialists are config-driven agents defined in markdown files located in .praxis-os/personas/ directory. Filename (without .md) = persona name.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "persona": {
        "type": "string",
        "description": "Persona name (e.g., 'database', 'api', 'security')"
      },
      "task": {
        "type": "string",
        "description": "Task description for specialist"
      },
      "context": {
        "type": "object",
        "description": "Optional context dict (project info, constraints, etc.)",
        "additionalProperties": true
      }
    },
    "required": ["persona", "task"]
  }
}
```

**Implementation:**
```python
from fastmcp import FastMCP
from typing import Dict, Any, Optional

mcp = FastMCP("agent-os-rag")

@mcp.tool()
async def invoke_specialist(
    persona: str,
    task: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Invoke a domain specialist sub-agent.
    
    Addresses FR-003: MCP tool registration.
    
    Args:
        persona: Persona name (e.g., "database", "api", "security")
        task: Task description for specialist
        context: Optional context dict
    
    Returns:
        {
            "persona": str,
            "result": str,
            "tools_used": List[str],
            "artifacts": List[str],
            "iterations": int,
            "duration_ms": float,
            "tokens": int,
            "cost": float,
            "error": Optional[str]
        }
    
    Examples:
        # Database schema design
        result = await invoke_specialist(
            persona="database",
            task="Design authentication schema with OAuth support"
        )
        
        # Security review with context
        result = await invoke_specialist(
            persona="security",
            task="Review authentication code for vulnerabilities",
            context={"compliance": ["GDPR", "SOC2"]}
        )
    """
    # Get PersonaLauncher instance
    launcher = get_persona_launcher()
    
    # Execute specialist
    result = await launcher.run(
        persona_name=persona,
        task=task,
        context=context
    )
    
    # Convert to dict
    return {
        "persona": result.persona,
        "result": result.result,
        "tools_used": result.tools_used,
        "artifacts": result.artifacts,
        "iterations": result.iterations,
        "duration_ms": result.duration_ms,
        "tokens": result.tokens,
        "cost": result.cost,
        "error": result.error
    }
```

**Response Structure:**
```json
{
  "persona": "database",
  "result": "Complete authentication schema design with migrations...",
  "tools_used": ["search_standards", "start_workflow", "complete_phase", "write_standard"],
  "artifacts": ["auth-schema.sql", "migrations/001_auth.sql", ".praxis-os/standards/project/database/auth-pattern.md"],
  "iterations": 27,
  "duration_ms": 45230.5,
  "tokens": 15234,
  "cost": 0.0834,
  "error": null
}
```

**Error Response (Persona Not Found):**
```json
{
  "persona": "nonexistent",
  "result": "",
  "tools_used": [],
  "artifacts": [],
  "iterations": 0,
  "duration_ms": 0,
  "tokens": 0,
  "cost": 0,
  "error": "Persona 'nonexistent' not found. Available: ['api', 'database', 'security', 'testing']. Suggestion: Create .praxis-os/personas/nonexistent.md"
}
```

### 3.2 MCP Tool: write_standard

**Purpose:** Enable specialists to document learnings as standards.

**Tool Schema:**
```json
{
  "name": "write_standard",
  "description": "Write a standard document to the Agent OS knowledge base. Creates markdown file in .praxis-os/standards/ directory for future discovery via search_standards().",
  "inputSchema": {
    "type": "object",
    "properties": {
      "category": {
        "type": "string",
        "description": "Category path (e.g., 'project/database', 'project/api')"
      },
      "name": {
        "type": "string",
        "description": "Standard name (becomes filename without .md)"
      },
      "content": {
        "type": "string",
        "description": "Markdown content of the standard"
      }
    },
    "required": ["category", "name", "content"]
  }
}
```

**Implementation:**
```python
@mcp.tool()
async def write_standard(
    category: str,
    name: str,
    content: str
) -> Dict[str, Any]:
    """
    Write standard document to knowledge base.
    
    Addresses FR-007: Knowledge documentation.
    
    Args:
        category: Category path (e.g., "project/database")
        name: Standard name (filename without .md)
        content: Markdown content
    
    Returns:
        {
            "status": "success",
            "path": str,
            "indexed": bool
        }
    
    Example:
        result = await write_standard(
            category="project/database",
            name="auth-pattern",
            content=\"\"\"
            # Authentication Schema Pattern
            
            ## Context
            High-security API with OAuth 2.0
            
            ## Pattern
            Use separate auth database with...
            \"\"\"
        )
    """
    standards_dir = Path(".praxis-os/standards")
    category_dir = standards_dir / category
    category_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = category_dir / f"{name}.md"
    file_path.write_text(content, encoding="utf-8")
    
    # Trigger RAG re-index (file watcher handles this)
    # Completes within 10 seconds (NFR-P3)
    
    return {
        "status": "success",
        "path": str(file_path),
        "indexed": False  # Will be True after re-index
    }
```

### 3.3 Internal Interfaces

**PersonaLauncher ← LLMClient:**
```python
response: LLMResponse = await llm_client.call(
    messages=messages,
    tools=tools,
    temperature=0.7
)
```

**PersonaLauncher ← MCPClient:**
```python
result: Dict = await mcp_client.call_tool(
    tool_name="search_standards",
    arguments={"query": "how to design database schema"}
)
```

---

## 4. Data Models

### 4.1 Domain Models

```python
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class SpecialistResult:
    """
    Result from specialist execution.
    
    Addresses FR-008: Metrics tracking.
    """
    persona: str
    result: str
    tools_used: List[str]
    artifacts: List[str]
    iterations: int
    duration_ms: float
    tokens: int
    cost: float
    error: Optional[str] = None

@dataclass
class LLMUsage:
    """Token usage from LLM API call."""
    input_tokens: int
    output_tokens: int
    total_tokens: int

@dataclass
class ToolCall:
    """Tool call request from LLM."""
    id: str
    name: str
    arguments: Dict[str, Any]

@dataclass
class LLMResponse:
    """Response from LLM API."""
    content: str
    model: str
    tool_calls: Optional[List[ToolCall]]
    usage: LLMUsage

@dataclass
class PersonaMetadata:
    """
    Metadata about a persona (optional, for tooling).
    """
    name: str
    file_path: str
    created_at: datetime
    modified_at: datetime
    line_count: int
    has_required_sections: bool
```

### 4.2 File System Schema

**Persona Files:**
```
.praxis-os/personas/
├── database.md          # Persona definition
├── api.md
├── security.md
└── testing.md

Format: Markdown
Size: Typically 50-200 lines
Required Sections: Identity, Approach, Tools, Decision Protocol
```

**Standards Files:**
```
.praxis-os/standards/
├── universal/           # Shipped with Agent OS
│   ├── concurrency/
│   ├── testing/
│   └── architecture/
│
└── project/            # Generated by specialists
    ├── database/
    │   ├── auth-pattern.md
    │   └── connection-pooling.md
    ├── api/
    │   └── rate-limiting.md
    └── security/
        └── token-validation.md

Format: Markdown
Created by: write_standard() tool
Indexed by: RAG system
```

**Workflow State Files:**
```
.praxis-os/cache/workflow-sessions/
└── {session_id}.json   # Workflow state

Format: JSON
Example: {
  "session_id": "db-schema-20251022-143022",
  "workflow_type": "database-schema-design",
  "current_phase": 2,
  "completed_phases": [0, 1],
  "evidence": {...}
}
```

### 4.3 Persona File Structure

**Standard Format:**
```markdown
# {Domain} Specialist

You are a {Domain} Specialist in Agent OS Enhanced.

{Brief role description}

## Your Approach

1. BEFORE implementing:
   - search_standards("how to {task type}")
   - Discover if workflows exist
   
2. Execute:
   - If workflow: start_workflow()
   - If no workflow: Follow best practices
   
3. Validate:
   - {Domain-specific checks}
   
4. Document:
   - write_standard("project/{domain}", "{pattern}", content)

## Your Tools

HIGH PRIORITY:
- search_standards(query) - Primary knowledge source
- search_codebase(query, dirs) - Project context
- write_standard(category, name, content) - Document learnings

WORKFLOW:
- start_workflow(type, file)
- complete_phase(session, phase, evidence)

FILE OPERATIONS:
- access_file(name, mode, content)
- execute_command(cmd)

## Decision Protocol

ALWAYS {critical requirement}
NEVER {anti-pattern}
QUERY before implementing
DOCUMENT new patterns
VALIDATE output quality
```

**Validation Rules:**
- File must exist in `.praxis-os/personas/`
- Filename = persona name + `.md`
- Must be valid UTF-8 markdown
- Recommended: Include all standard sections
- Size: Typically < 50KB

---

## 5. Security Design

### 5.1 File System Access Control

**Addresses NFR-S1: File system access control**

**Sandboxing:**
- Specialists can only read/write within project directory
- Path traversal prevented: `../` sequences blocked
- Symlinks dereferenced and validated
- Absolute paths restricted to project root

**Implementation:**
```python
def validate_path(path: str, project_root: Path) -> Path:
    """
    Validate and normalize file path.
    
    Addresses NFR-S1: File system access control.
    
    Args:
        path: User-provided path
        project_root: Project root directory
    
    Returns:
        Validated absolute path
    
    Raises:
        SecurityError: If path outside project
    """
    # Resolve to absolute path
    abs_path = (project_root / path).resolve()
    
    # Ensure within project root
    if not abs_path.is_relative_to(project_root):
        raise SecurityError(f"Path outside project: {path}")
    
    return abs_path
```

### 5.2 Command Execution Safety

**Addresses NFR-S2: Command execution safety**

**Restrictions:**
- Commands run in project directory only
- Shell injection prevented via parameterized execution
- Dangerous commands blocked: `rm -rf /`, `chmod 777`, etc.
- Command audit trail logged

**Implementation:**
```python
BLOCKED_COMMANDS = [
    "rm -rf /",
    "chmod 777",
    "sudo",
    "su",
    # ... more dangerous commands
]

async def execute_command(
    cmd: str,
    cwd: Path
) -> Dict[str, Any]:
    """
    Execute command safely.
    
    Addresses NFR-S2: Command execution safety.
    
    Args:
        cmd: Command to execute
        cwd: Working directory (validated)
    
    Returns:
        {
            "stdout": str,
            "stderr": str,
            "exit_code": int
        }
    
    Raises:
        SecurityError: If command blocked
    """
    # Check blocked commands
    if any(blocked in cmd for blocked in BLOCKED_COMMANDS):
        raise SecurityError(f"Blocked command: {cmd}")
    
    # Log for audit trail
    logger.info(f"Executing command: {cmd} in {cwd}")
    
    # Execute with subprocess (not shell)
    result = await asyncio.create_subprocess_exec(
        *cmd.split(),
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await result.communicate()
    
    return {
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
        "exit_code": result.returncode
    }
```

### 5.3 API Key Security

**Addresses NFR-S3: API key security**

**Storage:**
- API keys stored in environment variables
- Never logged or returned in results
- Never included in persona prompts or messages
- Encrypted at rest (OS keychain on supported platforms)

**Configuration:**
```bash
# .env file (gitignored)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
```

**Loading:**
```python
from dotenv import load_dotenv
import os

load_dotenv()

anthropic_key = os.getenv("ANTHROPIC_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

# Never log keys
logger.info("API keys loaded")  # Not: logger.info(f"Key: {key}")
```

### 5.4 Tool Permission Model

**Addresses NFR-S4: Tool permission model**

**Permissions:**
- All specialists get same tool subset by default
- Sensitive tools can require explicit user permission (future)
- Tool usage logged for audit
- Recursive invocation prevented (`invoke_specialist` excluded from specialist toolkit)

**Audit Logging:**
```python
# Every tool call logged
logger.info(
    f"Tool call: {tool_name} by persona={persona_name} "
    f"with args={sanitize(arguments)}"
)
```

---

## 6. Performance Design

### 6.1 Execution Performance

**Addresses NFR-P1, NFR-P2:**

**Persona Loading:**
- Target: < 100ms for typical files (<50KB)
- Strategy: Direct file read, no parsing overhead
- Caching: Not needed (loading fast enough)

**Specialist Execution:**
- Simple tasks (3-5 tool calls): < 30 seconds
- Complex tasks (20-30 tool calls): < 5 minutes
- Overall timeout: 10 minutes maximum
- Strategy: Parallel tool execution where possible (future)

### 6.2 RAG Integration Performance

**Addresses NFR-P3:**

**search_standards Query:**
- Simple queries: < 100ms
- Complex queries: < 200ms
- Strategy: Vector index optimization, relevance scoring

**write_standard File Creation:**
- File write: < 100ms
- RAG re-index: < 10 seconds
- Strategy: Incremental indexing, file watcher

### 6.3 Memory Efficiency

**Addresses NFR-P4:**

**Memory Limits:**
- PersonaLauncher base: < 100MB
- Per specialist execution: < 500MB
- Message history pruning: After 50 iterations or 100K tokens
- Concurrent specialists: 5 simultaneous (configurable)

**Implementation:**
```python
class PersonaLauncher:
    def _prune_messages(
        self,
        messages: List[Dict]
    ) -> List[Dict]:
        """
        Prune message history to control memory.
        
        Addresses NFR-P4: Memory efficiency.
        
        Keeps: System prompt, recent messages, context
        Drops: Middle conversation history
        
        Args:
            messages: Full message history
        
        Returns:
            Pruned message history
        """
        if len(messages) < 20:
            return messages
        
        # Keep first 2 (system + initial user)
        # Keep last 10 (recent context)
        pruned = messages[:2] + messages[-10:]
        
        logger.info(f"Pruned messages: {len(messages)} → {len(pruned)}")
        
        return pruned
```

### 6.4 Caching Strategy

**Persona File Caching:**
- Not needed: File loading fast enough (<100ms)
- Personas can change frequently (iteration)

**LLM Response Caching:**
- Provider-level caching: Use Anthropic prompt caching where available
- Application-level: Not implemented initially (complexity vs benefit)

### 6.5 Monitoring

**Addresses NFR-U2: Observability**

**Metrics Tracked:**
- Specialist execution time (per persona, per task type)
- Tool usage frequency
- Success/failure rates
- Token usage and cost
- Iteration counts

**Implementation:**
```python
# Metrics collected in SpecialistResult
# Can be aggregated for analysis

metrics_logger.info({
    "event": "specialist_execution",
    "persona": result.persona,
    "duration_ms": result.duration_ms,
    "tokens": result.tokens,
    "cost": result.cost,
    "tools_used": result.tools_used,
    "success": result.error is None
})
```

---

## 7. Requirements Satisfaction Summary

| Requirement | Design Element | Validation |
|-------------|----------------|------------|
| FR-001: PersonaLauncher | Section 2.1 | Core class with agentic loop |
| FR-002: Persona files | Section 4.2 | Markdown in `.praxis-os/personas/` |
| FR-003: MCP tool | Section 3.1 | `invoke_specialist` tool |
| FR-004: Discovery pattern | Section 2.1 | Taught in persona prompts |
| FR-005: Workflow integration | Section 2.1 | Tool subset includes workflow tools |
| FR-006: Tool filtering | Section 2.1 | `_get_tool_schemas()` method |
| FR-007: write_standard | Section 3.2 | MCP tool implementation |
| FR-008: Metrics | Section 4.1 | `SpecialistResult` dataclass |
| FR-009: Error handling | Section 2.1 | Graceful failures with helpful errors |
| FR-010: Base personas | Implementation phase | 4 .md files to create |
| FR-011: Persona template | Implementation phase | Template + guide to create |
| FR-012: Agentic loop | Section 2.1 | `_agentic_loop()` method |
| FR-013: File organization | Section 4.2 | Standard directory structure |
| FR-014: LLM providers | Section 2.3 | Unified LLMClient interface |
| FR-015: Context management | Section 2.1 | Optional context parameter |

**All functional requirements addressed in technical design.**

---

## 8. Implementation Notes

### 8.1 Technology Choices

**Python 3.10+:**
- Async/await for concurrent operations
- Type hints for clarity and safety
- Dataclasses for structured data
- Pathlib for file operations

**Dependencies:**
```python
# pyproject.toml or requirements.txt
anthropic>=0.18.0      # Claude API
openai>=1.12.0         # OpenAI API
fastmcp>=1.0.0         # MCP server framework
python-dotenv>=1.0.0   # Environment variables
```

### 8.2 Development Priorities

**Phase 1: Core Infrastructure (Week 1-2)**
1. PersonaLauncher class with agentic loop
2. LLMClient unified interface
3. MCPClient wrapper
4. invoke_specialist MCP tool

**Phase 2: File System & Discovery (Week 2-3)**
5. Persona file loading
6. write_standard tool
7. Tool subset filtering
8. Error handling

**Phase 3: Base Personas (Week 3-4)**
9. Database specialist persona
10. API specialist persona
11. Security specialist persona
12. Testing specialist persona

**Phase 4: Documentation & Testing (Week 4)**
13. Persona creation template
14. Documentation guide
15. Unit tests (80%+ coverage)
16. End-to-end scenarios

### 8.3 Testing Strategy

**Unit Tests:**
- PersonaLauncher._load_persona()
- PersonaLauncher._get_tool_schemas()
- PersonaLauncher._agentic_loop() (mocked LLM/MCP)
- LLMClient provider abstraction
- Error handling paths

**Integration Tests:**
- invoke_specialist tool end-to-end
- Persona file loading with real files
- write_standard tool creates files
- RAG re-indexing triggered

**End-to-End Tests:**
- Complete specialist execution (mocked LLM)
- Discovery pattern workflow
- Metrics tracking accuracy
- Error scenarios (persona not found, max iterations)

**Manual Testing:**
- Real specialist execution with actual LLM API
- Base persona quality validation
- Documentation clarity

---

**Document Version:** 1.0  
**Created:** 2025-10-22  
**Last Updated:** 2025-10-22  
**Status:** Ready for Phase 3 (Task Breakdown)

