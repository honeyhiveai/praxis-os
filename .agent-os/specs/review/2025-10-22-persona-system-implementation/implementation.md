# Implementation Approach

**Project:** Persona System Implementation  
**Date:** 2025-10-22  
**Based on:** srd.md, specs.md, tasks.md

---

## 1. Implementation Philosophy

### Core Principles

1. **Config-Driven Architecture:** Personas are markdown files, NOT Python classes. Keep implementation focused on the execution engine, not persona-specific logic.

2. **Single Responsibility:** PersonaLauncher handles ALL personas through file loading. Resist urge to create per-persona code branches.

3. **Type Safety:** Use Python 3.10+ type hints throughout. Run mypy to catch errors early.

4. **Test-First Mindset:** Write tests alongside or before implementation. Target 80%+ coverage.

5. **Security by Design:** Implement file system sandboxing and command safety from the start, not as afterthought.

6. **Performance Awareness:** Optimize hot paths (agentic loop, file loading). Profile before optimizing.

### Implementation Values

- **Clarity > Cleverness:** Clear code beats clever code
- **Errors Explicit:** Better to crash with clear message than fail silently
- **Examples Required:** Every public API needs usage example
- **Document Decisions:** Comment "why", not "what"

---

## 2. Implementation Order

Follow the phase order from tasks.md:

**Phase 1: Core Infrastructure** (Week 1)
1. PersonaLauncher class structure
2. Persona file loading
3. LLMClient interface
4. MCPClient wrapper
5. Agentic loop

**Phase 2: Tool Integration** (Week 2)
1. invoke_specialist MCP tool
2. Tool subset filtering
3. write_standard MCP tool
4. PersonaLoader utility
5. Security hardening
6. Performance optimization

**Phase 3: Base Personas** (Week 3)
1. Persona template
2. Database/API/Security/Testing personas
3. Unit test suite

**Phase 4: Documentation** (Week 4)
1. Persona creation guide
2. API documentation
3. E2E testing
4. Requirements validation

---

## 3. Code Patterns

### 3.1 PersonaLauncher Pattern

**Core Structure:**
```python
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time
import json

PERSONA_DIR = Path(".agent-os/personas")

@dataclass
class SpecialistResult:
    """Result from specialist execution."""
    persona: str
    result: str
    tools_used: List[str]
    artifacts: List[str]
    iterations: int
    duration_ms: float
    tokens: int
    cost: float
    error: Optional[str] = None

class PersonaLauncher:
    """Core execution engine for all personas."""
    
    def __init__(
        self,
        mcp_client: MCPClient,
        llm_client: LLMClient,
        max_iterations: int = 50
    ):
        self.mcp = mcp_client
        self.llm = llm_client
        self.max_iterations = max_iterations
    
    async def run(
        self,
        persona_name: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> SpecialistResult:
        """Execute persona on task."""
        start_time = time.time()
        
        # 1. Load persona
        system_prompt = self._load_persona(persona_name)
        if isinstance(system_prompt, dict) and "error" in system_prompt:
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
        
        # 2. Initialize messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        
        if context:
            messages.append({
                "role": "user",
                "content": f"Additional context: {json.dumps(context)}"
            })
        
        # 3. Get tools
        tools = self._get_tool_schemas()
        
        # 4. Execute
        result = await self._agentic_loop(
            messages, tools, persona_name, start_time
        )
        
        return result
```

**Key Points:**
- Single `run()` method is entry point
- No persona-specific branches in code
- Error handling returns structured result, doesn't raise
- Time tracking starts at method entry

### 3.2 File Loading Pattern

```python
def _load_persona(self, persona_name: str) -> Union[str, Dict]:
    """Load persona from markdown file."""
    persona_file = PERSONA_DIR / f"{persona_name}.md"
    
    if not persona_file.exists():
        available = sorted([f.stem for f in PERSONA_DIR.glob("*.md")])
        return {
            "error": f"Persona '{persona_name}' not found",
            "available": available,
            "suggestion": f"Create: .agent-os/personas/{persona_name}.md",
            "template": "See DESIGN-Persona-System.md for template"
        }
    
    try:
        return persona_file.read_text(encoding="utf-8")
    except Exception as e:
        return {
            "error": f"Failed to read persona file: {str(e)}",
            "path": str(persona_file)
        }
```

**Anti-Pattern to Avoid:**
```python
# DON'T: Raise exceptions for missing personas
def _load_persona(self, persona_name: str) -> str:
    persona_file = PERSONA_DIR / f"{persona_name}.md"
    return persona_file.read_text()  # Raises FileNotFoundError - BAD

# DO: Return helpful error in result structure
```

### 3.3 Agentic Loop Pattern

```python
async def _agentic_loop(
    self,
    messages: List[Dict],
    tools: List[Dict],
    persona_name: str,
    start_time: float
) -> SpecialistResult:
    """Execute agentic loop until completion."""
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
        
        # Handle tool calls
        if response.tool_calls:
            for tool_call in response.tool_calls:
                # Execute tool
                result = await self.mcp.call_tool(
                    tool_call.name,
                    tool_call.arguments
                )
                
                # Track
                tools_used.append(tool_call.name)
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
            # Text response = done
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
    
    # Max iterations
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
        error="Max iterations reached"
    )
```

**Key Points:**
- Loop exits on text response (no tool calls)
- OR max iterations reached (safety limit)
- Metrics tracked every iteration
- Partial results returned if limit hit

### 3.4 LLM Client Pattern

```python
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

class LLMClient:
    """Unified LLM interface."""
    
    def __init__(self, provider: str, model: str, api_key: str):
        self.provider = provider
        self.model = model
        
        if provider == "anthropic":
            self.client = AsyncAnthropic(api_key=api_key)
        elif provider == "openai":
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
        """Call LLM with retry logic."""
        for attempt in range(max_retries):
            try:
                if self.provider == "anthropic":
                    return await self._call_anthropic(messages, tools, temperature)
                else:
                    return await self._call_openai(messages, tools, temperature)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
        
    async def _call_anthropic(self, messages, tools, temperature):
        """Anthropic-specific implementation."""
        # Convert messages to Anthropic format
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
        other_msgs = [m for m in messages if m["role"] != "system"]
        
        response = await self.client.messages.create(
            model=self.model,
            system=system_msg,
            messages=other_msgs,
            tools=tools,
            temperature=temperature,
            max_tokens=4096
        )
        
        # Convert to unified format
        return LLMResponse(
            content=response.content[0].text if response.content else "",
            model=response.model,
            tool_calls=self._extract_tool_calls_anthropic(response),
            usage=LLMUsage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens
            )
        )
    
    async def _call_openai(self, messages, tools, temperature):
        """OpenAI-specific implementation."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            temperature=temperature
        )
        
        # Convert to unified format
        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            tool_calls=self._extract_tool_calls_openai(response),
            usage=LLMUsage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
        )
```

**Key Points:**
- Provider differences abstracted
- Retry logic with exponential backoff
- Unified response format
- Tool call extraction provider-specific

### 3.5 MCP Tool Registration Pattern

```python
from fastmcp import FastMCP

mcp = FastMCP("agent-os-rag")

@mcp.tool()
async def invoke_specialist(
    persona: str,
    task: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Invoke domain specialist sub-agent.
    
    Args:
        persona: Persona name (e.g., "database", "api")
        task: Task description
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
        result = await invoke_specialist(
            persona="database",
            task="Design authentication schema"
        )
    """
    launcher = get_persona_launcher()  # Get singleton instance
    result = await launcher.run(persona, task, context)
    
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

### 3.6 Security Pattern: Path Validation

```python
def validate_path(path: str, project_root: Path) -> Path:
    """
    Validate file path is within project.
    
    Args:
        path: User-provided path
        project_root: Project root directory
    
    Returns:
        Validated absolute path
    
    Raises:
        SecurityError: If path outside project
    """
    # Resolve to absolute
    abs_path = (project_root / path).resolve()
    
    # Check within project
    try:
        abs_path.relative_to(project_root)
    except ValueError:
        raise SecurityError(f"Path outside project: {path}")
    
    return abs_path

# Usage in file operations
def access_file(name: str, mode: str, content: Optional[str] = None):
    """Access file safely."""
    validated_path = validate_path(name, PROJECT_ROOT)
    
    if mode == "read":
        return validated_path.read_text()
    elif mode == "write":
        validated_path.write_text(content)
        return {"path": str(validated_path)}
```

---

## 4. Testing Strategy

### 4.1 Unit Tests

**Test Structure:**
```python
# tests/test_persona_launcher.py

import pytest
from unittest.mock import Mock, AsyncMock, patch
from mcp_server.persona_launcher import PersonaLauncher, SpecialistResult

class TestPersonaLauncher:
    """Unit tests for PersonaLauncher."""
    
    @pytest.fixture
    def mcp_client(self):
        """Mock MCP client."""
        client = Mock()
        client.list_tools = Mock(return_value=[
            {"name": "search_standards", "description": "..."},
            {"name": "start_workflow", "description": "..."}
        ])
        client.call_tool = AsyncMock(return_value={"status": "success"})
        return client
    
    @pytest.fixture
    def llm_client(self):
        """Mock LLM client."""
        client = Mock()
        # Configure mock responses
        return client
    
    @pytest.fixture
    def launcher(self, mcp_client, llm_client):
        """PersonaLauncher instance."""
        return PersonaLauncher(mcp_client, llm_client)
    
    def test_load_persona_success(self, launcher, tmp_path):
        """Test successful persona loading."""
        # Create test persona file
        persona_file = tmp_path / "test.md"
        persona_file.write_text("# Test Specialist\n\nYou are a test.")
        
        # Patch PERSONA_DIR
        with patch("mcp_server.persona_launcher.PERSONA_DIR", tmp_path):
            result = launcher._load_persona("test")
        
        assert isinstance(result, str)
        assert "Test Specialist" in result
    
    def test_load_persona_not_found(self, launcher, tmp_path):
        """Test persona not found error."""
        with patch("mcp_server.persona_launcher.PERSONA_DIR", tmp_path):
            result = launcher._load_persona("nonexistent")
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "nonexistent" in result["error"]
        assert "available" in result
    
    @pytest.mark.asyncio
    async def test_agentic_loop_text_response(self, launcher, mcp_client, llm_client):
        """Test loop exits on text response."""
        # Mock LLM to return text (no tool calls)
        llm_client.call = AsyncMock(return_value=Mock(
            content="Task complete",
            tool_calls=None,
            usage=Mock(total_tokens=100, input_tokens=50, output_tokens=50)
        ))
        
        result = await launcher._agentic_loop(
            messages=[{"role": "system", "content": "test"}],
            tools=[],
            persona_name="test",
            start_time=time.time()
        )
        
        assert result.result == "Task complete"
        assert result.iterations == 1
        assert result.error is None
    
    @pytest.mark.asyncio
    async def test_agentic_loop_max_iterations(self, launcher, mcp_client, llm_client):
        """Test loop stops at max iterations."""
        # Mock LLM to always return tool calls
        llm_client.call = AsyncMock(return_value=Mock(
            content="",
            tool_calls=[Mock(
                id="1",
                name="search_standards",
                arguments={"query": "test"}
            )],
            usage=Mock(total_tokens=100, input_tokens=50, output_tokens=50)
        ))
        
        result = await launcher._agentic_loop(
            messages=[{"role": "system", "content": "test"}],
            tools=[],
            persona_name="test",
            start_time=time.time()
        )
        
        assert result.iterations == 50  # max_iterations
        assert result.error == "Max iterations reached"
```

**Coverage Target:** 80%+ for core components

**Run Tests:**
```bash
pytest tests/ -v --cov=mcp_server --cov-report=html
```

### 4.2 Integration Tests

```python
# tests/integration/test_specialist_invocation.py

@pytest.mark.integration
@pytest.mark.asyncio
async def test_invoke_specialist_end_to_end(real_mcp_server, tmp_path):
    """Test complete specialist invocation."""
    # Create test persona
    persona_dir = tmp_path / "personas"
    persona_dir.mkdir()
    (persona_dir / "test.md").write_text("""
    # Test Specialist
    
    You are a test specialist.
    
    ## Your Approach
    1. Respond with "Task completed successfully"
    """)
    
    # Patch persona directory
    with patch("mcp_server.persona_launcher.PERSONA_DIR", persona_dir):
        # Call tool
        result = await invoke_specialist(
            persona="test",
            task="Complete this task"
        )
    
    # Verify result structure
    assert result["persona"] == "test"
    assert isinstance(result["result"], str)
    assert isinstance(result["tools_used"], list)
    assert result["error"] is None
```

### 4.3 End-to-End Tests

```python
# tests/e2e/test_user_stories.py

@pytest.mark.e2e
class TestUserStories:
    """Test complete user stories from srd.md."""
    
    @pytest.mark.asyncio
    async def test_story_1_invoke_specialist(self):
        """Story 1: Invoke domain specialist for high-quality output."""
        # User action: "Use database specialist to design auth schema"
        result = await invoke_specialist(
            persona="database",
            task="Design authentication schema with OAuth support"
        )
        
        # Verify quality indicators
        assert result["error"] is None
        assert "search_standards" in result["tools_used"]
        assert len(result["result"]) > 500  # Comprehensive output
        assert result["iterations"] > 1  # Multi-step execution
    
    def test_story_2_create_custom_persona(self, tmp_path):
        """Story 2: Create custom specialist without code changes."""
        # User creates persona file
        persona_file = Path(".agent-os/personas/caching.md")
        persona_file.write_text("""
        # Caching Optimization Specialist
        
        You are a caching specialist.
        [... persona content ...]
        """)
        
        # Verify immediately available
        available = PersonaLoader.list_available()
        assert "caching" in available
        
        # Verify can be invoked (no restart needed)
        result = invoke_specialist(
            persona="caching",
            task="Optimize API caching"
        )
        assert result["persona"] == "caching"
```

---

## 5. Deployment

### 5.1 Pre-Deployment Checklist

**Code Quality:**
- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Type checking passes (`mypy mcp_server/`)
- [ ] Linter clean (`flake8 mcp_server/`)
- [ ] Coverage ≥ 80% (`pytest --cov`)
- [ ] Code reviewed and approved

**Dependencies:**
- [ ] requirements.txt or pyproject.toml updated
- [ ] Dependencies documented
- [ ] Version pinning appropriate

**Configuration:**
- [ ] Environment variables documented
- [ ] Example .env file provided
- [ ] API keys not committed
- [ ] Default values sensible

**Documentation:**
- [ ] README updated
- [ ] API documentation complete
- [ ] Persona creation guide ready
- [ ] Examples provided

### 5.2 Installation Steps

**For Development:**
```bash
# Clone repository
git clone https://github.com/honeyhiveai/agent-os-enhanced.git
cd agent-os-enhanced

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with API keys

# Create directory structure
mkdir -p .agent-os/personas
mkdir -p .agent-os/standards/project

# Run tests
pytest tests/ -v
```

**For Production (Dogfooding):**
```bash
# Same as development, but:
# - Use production API keys
# - Enable monitoring/logging
# - Configure resource limits
```

### 5.3 Monitoring

**Metrics to Track:**
```python
# Log every specialist execution
logger.info({
    "event": "specialist_execution",
    "persona": result.persona,
    "duration_ms": result.duration_ms,
    "tokens": result.tokens,
    "cost": result.cost,
    "tools_used": result.tools_used,
    "success": result.error is None
})
```

**Alerts:**
- Cost exceeds $1 per execution (unusually high)
- Max iterations hit frequently (>10% of runs)
- Error rate >5%
- Execution time >10 minutes

---

## 6. Troubleshooting

### 6.1 Common Issues

**Issue: Persona not found**
```
Error: Persona 'database' not found
Available: []
```

**Solution:**
1. Check `.agent-os/personas/` directory exists
2. Check `database.md` file exists
3. Check file permissions (readable)
4. Check filename is exactly `database.md` (case-sensitive)

**Issue: Max iterations reached**
```
Error: Max iterations reached (50). Partial result returned.
```

**Solution:**
1. Check persona prompt clarity (is task clear?)
2. Check tool descriptions (do specialists understand tools?)
3. Review tool call history (is specialist stuck in loop?)
4. Consider increasing max_iterations for complex tasks
5. Improve workflow discovery (better RAG indexing)

**Issue: LLM API errors**
```
Error: Rate limit exceeded
```

**Solution:**
1. Implement exponential backoff (already in LLMClient)
2. Add API key rotation
3. Use lower-cost model for simple tasks
4. Implement request queuing

**Issue: High costs**
```
Warning: Specialist execution cost $2.50 (unusually high)
```

**Solution:**
1. Review token usage (check message history size)
2. Implement message pruning (remove old history)
3. Optimize persona prompts (shorter is better)
4. Use cheaper model for initial tasks

**Issue: Security errors**
```
SecurityError: Path outside project: ../../../etc/passwd
```

**Solution:**
1. Check path validation is enabled
2. Review specialist's file access patterns
3. Ensure `validate_path()` called before file ops
4. Check symlink resolution

### 6.2 Debugging Tips

**Enable Debug Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Inspect Message History:**
```python
# In agentic loop, log messages
logger.debug(f"Messages: {json.dumps(messages, indent=2)}")
```

**Profile Performance:**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run specialist
result = await launcher.run("database", "Design schema")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

**Test with Mocked LLM:**
```python
# For reproducible testing
class MockLLMClient:
    def __init__(self, responses):
        self.responses = iter(responses)
    
    async def call(self, messages, tools, temperature):
        return next(self.responses)

# Use in tests
mock_llm = MockLLMClient([
    LLMResponse(content="Step 1 complete", tool_calls=[...]),
    LLMResponse(content="Step 2 complete", tool_calls=[...]),
    LLMResponse(content="Task complete", tool_calls=None)
])
```

---

## 7. Best Practices

### 7.1 Persona Creation

**DO:**
- Start with template
- Include discovery pattern explicitly
- Prioritize `search_standards()` as primary tool
- Add ALWAYS/NEVER decision protocol
- Provide domain-specific examples
- Test with real tasks before committing

**DON'T:**
- Hardcode workflow names (use discovery)
- Skip `write_standard()` documentation step
- Make prompts too long (< 2000 tokens)
- Include implementation details (keep high-level)

### 7.2 Error Handling

**DO:**
- Return structured errors, don't raise
- Include helpful messages with next steps
- List available options (e.g., personas)
- Log errors for debugging
- Provide fallback values where appropriate

**DON'T:**
- Silent failures (always return error info)
- Generic error messages ("Something went wrong")
- Crash main agent on specialist error
- Leak sensitive info in error messages

### 7.3 Performance

**DO:**
- Profile before optimizing
- Optimize hot paths only
- Use async/await throughout
- Implement timeouts
- Prune message history

**DON'T:**
- Premature optimization
- Blocking I/O in async code
- Unbounded loops or recursion
- Memory leaks (large message histories)

---

**Document Version:** 1.0  
**Created:** 2025-10-22  
**Status:** Ready for implementation

