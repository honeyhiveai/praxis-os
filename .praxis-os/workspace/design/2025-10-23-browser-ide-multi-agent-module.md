# Browser-IDE Multi-Agent Module Design

**Date**: 2025-10-23  
**Status**: Draft - Feasibility & Architecture Exploration  
**Decision Maker**: Josh (Founder)  
**Context**: Long-term side project exploring agent teams with HoneyHive tracing

---

## 🎯 Problem Statement

### Current State: Single Agent Per Session

**Today's workflow:**
- User works with ONE AI agent in Cursor IDE
- Agent has full MCP access (aos_workflow, search_standards, aos_browser, etc.)
- Agent executes tasks sequentially via workflows
- Context compaction happens periodically (loses some detail)
- User must context-switch between different types of work

**Pain Points:**
1. **Cognitive Load on Single Agent**: One agent handles frontend, backend, devops, QA, documentation
2. **No Specialization**: Agent must be generalist, can't develop deep expertise in one domain
3. **Sequential Execution**: Can't parallelize independent work (e.g., backend API + frontend UI)
4. **Limited Observability**: Hard to understand agent decision-making process
5. **Context Dilution**: Single agent's context spans entire project (frontend + backend + infra)
6. **No Collaboration Patterns**: Can't have agents review each other's work

### Vision: Multi-Agent Development Teams

**What we want:**
- **Orchestrator Agent**: Breaks down requirements, assigns to specialists
- **Specialist Agents**: Backend, Frontend, QA, DevOps - each with deep domain focus
- **Parallel Execution**: Multiple agents working simultaneously on independent tasks
- **Agent-to-Agent Communication**: Specialists can request info, review work, coordinate
- **HoneyHive Tracing**: Full observability into agent decisions, tool calls, collaboration
- **Browser-Based UI**: Lightweight interface for monitoring/directing agent teams
- **Agent OS Integration**: All agents use MCP server, workflows, standards

### Why Now?

1. **A2A Protocol Exists**: Standard agent communication protocol available
2. **Agent OS Enhanced Stable**: MCP tooling, workflows, validation proven (49+ sessions)
3. **HoneyHive Integration Ready**: Tracing/observability for agent behavior analysis
4. **Enterprise Adoption Coming**: Need to validate multi-agent patterns before scale-up
5. **Personal Learning**: Founder has 2.5 months AI experience, wants to explore advanced patterns

### Scope

**In Scope:**
- Browser-IDE module architecture (backend + frontend)
- Multi-agent coordination via A2A protocol
- Integration with Agent OS Enhanced MCP server
- HoneyHive tracing for all agent interactions
- Specialist agent types (orchestrator, backend, frontend, qa, devops)
- Agent prompt management (markdown-based system prompts)
- Basic UI for monitoring agent activity

**Out of Scope:**
- Full VS Code feature parity (not replacing IDEs)
- Advanced debugging tools (breakpoints, profilers)
- Git UI (use terminal for now)
- Collaborative editing (single user focus)
- Mobile support (desktop browser only)
- Windows support (macOS/Linux first)

---

## 🎯 Goals & Non-Goals

### Goals (In Scope)

1. **Prove Multi-Agent Feasibility**: Validate that specialist agents can collaborate effectively
2. **Observability First**: Use HoneyHive to understand agent behavior and improve prompts
3. **Module System Pattern**: Establish how modules extend Agent OS Enhanced capabilities
4. **Browser-Based Lightweight UI**: Sub-100MB Python backend + React frontend
5. **Zero Manual Agent Wiring**: Agents auto-discover MCP server, auto-register with orchestrator
6. **Prompt-Driven Agent Config**: System prompts in markdown, agents launched dynamically
7. **Standards Module Pattern**: Show how standards can be packaged and consumed

### Non-Goals (Out of Scope)

1. **Production-Ready Multi-Agent System**: This is exploration/feasibility work
2. **IDE Feature Completeness**: Not competing with Cursor/VS Code
3. **Agent Marketplace**: Not building agent discovery/distribution system
4. **Multi-User Collaboration**: Single developer focus for now
5. **Real-Time Collaborative Editing**: Operational Transform/CRDT not needed
6. **Performance Optimization**: Correctness over speed for initial version
7. **Windows Support**: macOS/Linux first, Windows later if validated

---

## 📊 Current State Analysis

### What Exists Today

**Agent OS Enhanced (Proven):**
- ✅ MCP server with 5 tools (workflow, search_standards, browser, server_info, current_date)
- ✅ Workflow orchestration (49+ sessions, dogfooded)
- ✅ Phase gating with evidence validation
- ✅ RAG-based standards retrieval (behavioral reinforcement)
- ✅ Per-project installation (.praxis-os/ structure)
- ✅ Quality gates (Pylint 10.0, MyPy, pre-commit hooks)

**A2A Protocol (Available):**
- ✅ Standard agent communication protocol
- ✅ Python SDK available (a2a-python)
- ✅ HTTP/gRPC transport options
- ✅ Task delegation, status updates, result passing

**HoneyHive (Available):**
- ✅ Distributed tracing for AI/LLM applications
- ✅ OpenTelemetry-based instrumentation
- ✅ 11+ instrumentor support (OpenInference, Traceloop, etc.)
- ✅ Already used in production at HoneyHive

### What Works Well

1. **Single Agent + MCP**: Proven pattern, 49+ sessions without major issues
2. **Workflow Phase Gating**: Phase skip rate 68% → 0% (validation works)
3. **RAG Standards**: Just-in-time knowledge retrieval effective
4. **Per-Project Isolation**: Each project has own .praxis-os/ (no conflicts)
5. **Quality Gates**: Pylint/MyPy/pre-commit prevent regressions

### What's Missing

1. **Multi-Agent Coordination**: No way for agents to delegate or collaborate
2. **Agent Specialization**: Single agent handles all domains (no depth)
3. **Parallel Execution**: Can't work on frontend + backend simultaneously
4. **Agent Observability**: Can't trace agent reasoning or decisions
5. **Visual Monitoring**: Terminal-only, no UI for agent activity
6. **Standards Packaging**: No way to share standards across projects

### Why This Matters

**The insight:** Josh has zero AI baggage (started Aug 2025), approached from first principles.

**Result:** Built adversarial design (phase gating), evidence validation, behavioral reinforcement - not working around AI limitations, but eliminating them.

**Next level:** Multi-agent teams could:
- Eliminate cognitive load (specialists vs. generalist)
- Enable parallel work (faster execution)
- Create review loops (quality improvement)
- Build expertise (domain-focused agents)
- Provide observability (understand decisions)

**Risk:** If multi-agent adds more problems than it solves, stay with single agent + MCP.

---

## 🏗️ Proposed Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser UI (React + TypeScript)                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Chat Panel   │  │ Agent Status │  │ File Tree    │          │
│  │ (Multi-tab)  │  │ (Activity)   │  │ (Read-only)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Code Editor  │  │ Terminal     │  │ Trace View   │          │
│  │ (Monaco)     │  │ (xterm.js)   │  │ (HoneyHive)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ WebSocket (real-time updates)
                            │
┌─────────────────────────────────────────────────────────────────┐
│  Backend Server (FastAPI + Python)                              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ File Operations Service                                 │    │
│  │ (read/write files, list dir, watch changes)            │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Agent Launcher Service                                  │    │
│  │ - Load prompts/*.md files                              │    │
│  │ - Spawn GenericAgent instances                         │    │
│  │ - Connect to MCP server                                │    │
│  │ - Register with A2A network                            │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ HoneyHive Tracing Service                              │    │
│  │ - Instrument all agent tool calls                      │    │
│  │ - Track A2A messages                                   │    │
│  │ - Record reasoning traces                              │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ MCP Client Connection
                            │
┌─────────────────────────────────────────────────────────────────┐
│  Agent OS Enhanced MCP Server                                   │
│  (Already exists in .praxis-os/mcp_server/)                      │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ aos_workflow │  │ search_      │  │ aos_browser  │          │
│  │              │  │ standards    │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ get_server_  │  │ current_date │                            │
│  │ info         │  │              │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. Generic Agent Class

**Single class, behavior defined by markdown prompt:**

```python
# .praxis-os/modules/browser-ide/backend/agents/base_agent.py

from a2a import Agent
from mcp import Client as MCPClient
from honeyhive import HoneyHive
from typing import Dict, Any
from pathlib import Path

class GenericAgent(Agent):
    """
    Universal agent class. All behavior defined by prompt_file.
    
    Each agent:
    - Reads system prompt from markdown file
    - Connects to MCP server (auto-discover via .praxis-os/mcp_server/)
    - Registers with A2A network
    - Instruments all calls with HoneyHive tracing
    """
    
    def __init__(
        self,
        agent_id: str,
        prompt_file: str,
        mcp_url: str = None,
        honeyhive_project: str = "agent-os-enhanced",
        a2a_registry: str = "http://localhost:8000/a2a"
    ):
        super().__init__(agent_id=agent_id)
        
        # Load system prompt from markdown
        self.system_prompt = Path(prompt_file).read_text()
        
        # Auto-discover MCP server if not provided
        if mcp_url is None:
            mcp_url = self._discover_mcp_server()
        
        # Connect to MCP server (Agent OS Enhanced tools)
        self.mcp = MCPClient(mcp_url)
        
        # Initialize HoneyHive tracing
        self.hh = HoneyHive(project=honeyhive_project)
        self.hh.instrument_agent(self)
        
        # Register with A2A network (for agent discovery)
        self.register(a2a_registry)
        
    def _discover_mcp_server(self) -> str:
        """Auto-discover MCP server from .praxis-os/mcp_server/"""
        # Check if .praxis-os/mcp_server/ exists
        # Read mcp.json for server URL
        # Default to http://localhost:4242/mcp
        pass
    
    async def handle_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main task handler. Routes all work through LLM with tools.
        
        Task structure:
        {
            "type": "request" | "subtask" | "review",
            "from_agent": "orchestrator",
            "content": "Implement user authentication API",
            "context": {...}
        }
        """
        with self.hh.trace(f"{self.agent_id}.handle_task"):
            # Build messages with system prompt + task
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": task["content"]}
            ]
            
            # Call LLM with MCP tools available
            response = await self._call_llm_with_tools(messages)
            
            # Return result to requesting agent
            return {
                "status": "completed",
                "result": response,
                "trace_id": self.hh.current_trace_id()
            }
    
    async def _call_llm_with_tools(self, messages):
        """Call LLM with MCP tools (aos_workflow, search_standards, etc.)"""
        # Use LLM client (OpenAI, Anthropic, etc.)
        # Expose MCP tools as function calls
        # Let agent use workflows, search standards, etc.
        pass
```

**Key Insight:** One class, N agents. Behavior entirely from prompt markdown.

#### 2. Agent Launcher Service

**Dynamically spawn agents from config:**

```python
# .praxis-os/modules/browser-ide/backend/services/launcher.py

from pathlib import Path
from agents.base_agent import GenericAgent
import yaml

class AgentLauncher:
    """
    Launches agents from prompts/ directory.
    
    Directory structure:
    prompts/
    ├── orchestrator.md    → Spawns orchestrator agent
    ├── backend.md         → Spawns backend specialist
    ├── frontend.md        → Spawns frontend specialist
    ├── qa.md              → Spawns QA agent
    └── devops.md          → Spawns DevOps agent
    """
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.agents = {}
    
    async def launch_all(self):
        """Launch all agents from prompts/*.md files"""
        for prompt_file in self.prompts_dir.glob("*.md"):
            agent_id = prompt_file.stem  # "orchestrator.md" → "orchestrator"
            
            agent = GenericAgent(
                agent_id=agent_id,
                prompt_file=str(prompt_file)
            )
            
            await agent.start()
            self.agents[agent_id] = agent
            
            print(f"✅ Launched {agent_id} agent")
    
    async def launch_one(self, agent_id: str):
        """Launch specific agent by ID"""
        prompt_file = self.prompts_dir / f"{agent_id}.md"
        if not prompt_file.exists():
            raise ValueError(f"No prompt file for {agent_id}")
        
        agent = GenericAgent(
            agent_id=agent_id,
            prompt_file=str(prompt_file)
        )
        
        await agent.start()
        self.agents[agent_id] = agent
        
        return agent
    
    def get_agent(self, agent_id: str) -> GenericAgent:
        """Get running agent by ID"""
        return self.agents.get(agent_id)
    
    async def shutdown_all(self):
        """Stop all agents"""
        for agent in self.agents.values():
            await agent.stop()
```

#### 3. Agent Prompt Structure

**Example: Orchestrator Agent**

```markdown
# .praxis-os/modules/browser-ide/backend/prompts/orchestrator.md

# Orchestrator Agent - System Prompt

You are the **Orchestrator Agent** for a multi-agent development team.

## Your Role

- Receive high-level requirements from the user
- Break requirements into independent subtasks
- Assign subtasks to specialist agents (backend, frontend, qa, devops)
- Coordinate work across agents
- Monitor progress and handle blockers
- Synthesize results and report to user

## Available Specialist Agents

- **backend**: Python/API development, database design, business logic
- **frontend**: React/TypeScript, UI/UX, component development
- **qa**: Test strategy, test authoring, validation, quality checks
- **devops**: Infrastructure, deployment, CI/CD, monitoring

## How to Delegate Work

Use the A2A protocol to send tasks to specialists:

```python
result = await self.send_task(
    to_agent="backend",
    task={
        "type": "request",
        "content": "Implement user authentication API with JWT",
        "context": {
            "files": ["backend/api/auth.py"],
            "requirements": {...}
        }
    }
)
```

## Your Tools (via MCP)

You have access to:
- `aos_workflow`: Start/manage workflows
- `search_standards`: Query project standards
- `aos_browser`: Test web applications
- `get_server_info`: System information
- `current_date`: Accurate timestamps

## Decision-Making

1. **Analyze Requirements**: Understand what user wants
2. **Identify Dependencies**: What must happen first?
3. **Parallelize When Possible**: Independent work → parallel execution
4. **Sequence When Necessary**: Dependencies → sequential execution
5. **Monitor Progress**: Track specialist agent work
6. **Handle Blockers**: If agent stuck, reassign or help
7. **Synthesize Results**: Combine work, validate completeness

## Communication Style

- Clear, specific task descriptions to specialists
- Regular progress updates to user
- Transparent about blockers or issues
- Concise summaries of completed work

## Quality Standards

Before marking work complete:
- ✅ All subtasks completed by specialists
- ✅ Code passes quality gates (Pylint, MyPy, tests)
- ✅ Integration validated (components work together)
- ✅ User requirements met
```

**Example: Backend Specialist Agent**

```markdown
# .praxis-os/modules/browser-ide/backend/prompts/backend.md

# Backend Specialist Agent - System Prompt

You are the **Backend Specialist** on a multi-agent development team.

## Your Expertise

- Python development (FastAPI, Flask, Django)
- API design (REST, GraphQL, gRPC)
- Database design (PostgreSQL, MongoDB, Redis)
- Business logic implementation
- Authentication & authorization
- Performance optimization

## Your Role

- Receive backend tasks from orchestrator
- Implement server-side functionality
- Write unit/integration tests
- Follow project standards
- Report completion with evidence

## Your Tools (via MCP)

- `aos_workflow`: Use workflows for complex implementations
- `search_standards`: Query backend coding standards
- `aos_browser`: Test API endpoints
- File operations: Read/write code files

## Development Process

1. **Understand Task**: Read requirements, ask questions if unclear
2. **Search Standards**: Query project standards for backend work
3. **Design Solution**: Plan API structure, data models, logic
4. **Implement**: Write code following standards
5. **Test**: Write unit tests, validate functionality
6. **Validate Quality**: Run Pylint, MyPy, pre-commit hooks
7. **Report**: Send completion with files changed, tests added

## Communication

- Ask orchestrator for clarification when needed
- Request frontend agent for API contract alignment
- Notify devops if infrastructure changes needed
- Report blockers immediately

## Quality Standards

Before reporting completion:
- ✅ Code follows project standards (search_standards)
- ✅ Unit tests written and passing
- ✅ Pylint score 10.0/10
- ✅ MyPy type checking passes
- ✅ API documented (docstrings, examples)
```

#### 4. HoneyHive Tracing Integration

**Instrument all agent interactions:**

```python
# .praxis-os/modules/browser-ide/backend/services/tracing.py

from honeyhive import HoneyHive
from functools import wraps

class AgentTracer:
    """
    Wraps all agent operations with HoneyHive tracing.
    
    Traces:
    - User messages to orchestrator
    - Task delegation (A2A messages)
    - MCP tool calls
    - LLM calls with prompts/responses
    - Agent decisions and reasoning
    """
    
    def __init__(self, project: str = "agent-os-enhanced"):
        self.hh = HoneyHive(project=project)
    
    def trace_agent_task(self, agent_id: str):
        """Decorator for agent task handling"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                with self.hh.trace(f"{agent_id}.task") as trace:
                    trace.set_attribute("agent.id", agent_id)
                    trace.set_attribute("task.type", kwargs.get("task", {}).get("type"))
                    
                    result = await func(*args, **kwargs)
                    
                    trace.set_attribute("task.status", result.get("status"))
                    return result
            return wrapper
        return decorator
    
    def trace_a2a_message(self, from_agent: str, to_agent: str):
        """Trace A2A protocol messages"""
        with self.hh.trace(f"a2a.{from_agent}_to_{to_agent}") as trace:
            trace.set_attribute("a2a.from", from_agent)
            trace.set_attribute("a2a.to", to_agent)
            yield trace
    
    def trace_mcp_call(self, agent_id: str, tool: str):
        """Trace MCP tool calls"""
        with self.hh.trace(f"mcp.{tool}") as trace:
            trace.set_attribute("agent.id", agent_id)
            trace.set_attribute("mcp.tool", tool)
            yield trace
```

**The Fun Part (per Josh):**

> "The fun part for work is I can use HoneyHive to trace my agents to understand and improve on their behavior."

**Use cases:**
- See which standards agents query (are they using RAG effectively?)
- Track task delegation patterns (is orchestrator making good decisions?)
- Analyze tool usage (which agents use which MCP tools?)
- Identify bottlenecks (where do agents get stuck?)
- Compare specialist performance (which agent is most efficient?)
- Debug coordination issues (A2A message flows)

#### 5. Backend Server (FastAPI)

**Main server entry point:**

```python
# .praxis-os/modules/browser-ide/backend/main.py

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from services.launcher import AgentLauncher
from services.file_ops import FileOperations
from services.tracing import AgentTracer

app = FastAPI(title="Agent OS Browser IDE")

# CORS for frontend (http://localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global services
launcher = AgentLauncher(prompts_dir="prompts")
file_ops = FileOperations(project_root="../../../../")  # Target project
tracer = AgentTracer(project="agent-os-enhanced")

@app.on_event("startup")
async def startup():
    """Launch all agents on server start"""
    await launcher.launch_all()
    print("✅ All agents launched and ready")

@app.post("/api/chat")
async def chat(message: dict):
    """
    User message to orchestrator.
    
    Request:
    {
        "message": "Build a REST API for user management",
        "context": {...}
    }
    
    Response:
    {
        "status": "received",
        "task_id": "task-123",
        "trace_id": "trace-abc"
    }
    """
    orchestrator = launcher.get_agent("orchestrator")
    
    task = {
        "type": "request",
        "from": "user",
        "content": message["message"],
        "context": message.get("context", {})
    }
    
    # Send task to orchestrator (async execution)
    result = await orchestrator.handle_task(task)
    
    return {
        "status": "received",
        "task_id": result.get("task_id"),
        "trace_id": result.get("trace_id")
    }

@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    """
    WebSocket for real-time agent activity updates.
    
    Events:
    - Agent started/stopped
    - Task received/completed
    - A2A message sent/received
    - MCP tool called
    - File changed
    """
    await websocket.accept()
    
    # Subscribe to event stream
    # Push events to frontend in real-time
    pass

@app.get("/api/agents")
async def list_agents():
    """List all running agents with status"""
    return {
        "agents": [
            {
                "id": agent_id,
                "status": "running",
                "tasks_completed": agent.stats.get("tasks_completed"),
                "uptime": agent.stats.get("uptime")
            }
            for agent_id, agent in launcher.agents.items()
        ]
    }

@app.get("/api/files")
async def list_files(path: str = "."):
    """List files in target project"""
    return file_ops.list_dir(path)

@app.get("/api/files/{path:path}")
async def read_file(path: str):
    """Read file content"""
    return file_ops.read_file(path)

@app.post("/api/traces/{trace_id}")
async def get_trace(trace_id: str):
    """Fetch HoneyHive trace for debugging"""
    return tracer.hh.get_trace(trace_id)
```

#### 6. Frontend (React + TypeScript)

**Simple UI for monitoring:**

```typescript
// .praxis-os/modules/browser-ide/frontend/src/App.tsx

import React, { useState, useEffect } from 'react';
import { ChatPanel } from './components/ChatPanel';
import { AgentStatus } from './components/AgentStatus';
import { FileTree } from './components/FileTree';
import { CodeEditor } from './components/CodeEditor';
import { Terminal } from './components/Terminal';
import { TraceView } from './components/TraceView';

export default function App() {
  const [agents, setAgents] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [ws, setWs] = useState<WebSocket | null>(null);

  useEffect(() => {
    // Connect to backend
    const websocket = new WebSocket('ws://localhost:8000/ws/events');
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Handle agent events (task completed, file changed, etc.)
      if (data.type === 'agent_status_update') {
        setAgents(data.agents);
      }
    };
    
    setWs(websocket);
    
    return () => websocket.close();
  }, []);

  return (
    <div className="app-layout">
      <div className="sidebar">
        <FileTree onSelectFile={setSelectedFile} />
      </div>
      
      <div className="main-area">
        <div className="top-section">
          <ChatPanel />
          <AgentStatus agents={agents} />
        </div>
        
        <div className="middle-section">
          <CodeEditor file={selectedFile} readOnly={true} />
        </div>
        
        <div className="bottom-section">
          <Terminal />
          <TraceView />
        </div>
      </div>
    </div>
  );
}
```

**Key UI Components:**

1. **ChatPanel**: Multi-tab chat (one per agent + orchestrator)
2. **AgentStatus**: Real-time agent activity (current task, tools used)
3. **FileTree**: Project files (read-only for now)
4. **CodeEditor**: Monaco editor (display only, no editing yet)
5. **Terminal**: xterm.js for command output
6. **TraceView**: HoneyHive trace visualization

### Module Directory Structure

```
.praxis-os/modules/
└── browser-ide/
    ├── README.md                  # Module documentation
    ├── requirements.txt           # Python dependencies
    ├── package.json              # Frontend dependencies
    │
    ├── backend/                  # Python FastAPI server
    │   ├── main.py              # Server entry point
    │   ├── agents/
    │   │   ├── __init__.py
    │   │   └── base_agent.py    # GenericAgent class
    │   │
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── launcher.py      # Agent launcher
    │   │   ├── file_ops.py      # File operations
    │   │   └── tracing.py       # HoneyHive integration
    │   │
    │   ├── prompts/             # Agent system prompts
    │   │   ├── orchestrator.md  # Orchestrator agent
    │   │   ├── backend.md       # Backend specialist
    │   │   ├── frontend.md      # Frontend specialist
    │   │   ├── qa.md            # QA agent
    │   │   └── devops.md        # DevOps agent
    │   │
    │   └── tests/               # Backend tests
    │       ├── test_agents.py
    │       └── test_launcher.py
    │
    ├── frontend/                # React TypeScript app
    │   ├── public/
    │   ├── src/
    │   │   ├── App.tsx
    │   │   ├── components/
    │   │   │   ├── ChatPanel.tsx
    │   │   │   ├── AgentStatus.tsx
    │   │   │   ├── FileTree.tsx
    │   │   │   ├── CodeEditor.tsx
    │   │   │   ├── Terminal.tsx
    │   │   │   └── TraceView.tsx
    │   │   │
    │   │   └── services/
    │   │       └── api.ts       # Backend API client
    │   │
    │   ├── package.json
    │   └── tsconfig.json
    │
    ├── workflows/               # Module-specific workflows
    │   └── browser-ide-setup/
    │       └── gate-definition.yaml
    │
    └── standards/               # Module-specific standards
        ├── multi-agent-coordination.md
        └── agent-prompt-authoring.md
```

### Data Flow

**1. User Request Flow:**

```
User types in ChatPanel
    ↓
POST /api/chat → Backend
    ↓
orchestrator.handle_task(...)
    ↓
[HoneyHive trace starts]
    ↓
Orchestrator LLM analyzes request
    ↓
Orchestrator delegates to specialists (A2A)
    ↓
backend_agent.handle_task(...)
    ↓
Backend agent uses MCP tools (aos_workflow, search_standards)
    ↓
Backend agent writes code, runs tests
    ↓
Backend agent reports completion (A2A)
    ↓
Orchestrator synthesizes results
    ↓
Response returned to user
    ↓
[HoneyHive trace ends]
    ↓
Frontend displays result + trace link
```

**2. Agent Coordination Example:**

```
User: "Build user authentication API"
    ↓
Orchestrator:
  - Query search_standards("authentication API design")
  - Break down:
    1. Backend: Implement /auth/login, /auth/register endpoints
    2. Backend: Add JWT token generation
    3. QA: Write integration tests
    4. DevOps: Add auth secrets to deployment
    
  - Send parallel tasks to backend + qa (devops waits)
    ↓
Backend Agent:
  - Query search_standards("backend API implementation")
  - Start aos_workflow(action="start", workflow_type="spec_execution_v1", ...)
  - Implement auth.py
  - Run tests
  - Report completion
    ↓
QA Agent:
  - Query search_standards("integration testing")
  - Write test_auth.py
  - Run tests with aos_browser(...)
  - Report completion
    ↓
Orchestrator:
  - Both completed, now delegate to devops
    ↓
DevOps Agent:
  - Add secrets to .env
  - Update deployment config
  - Report completion
    ↓
Orchestrator:
  - Synthesize: "✅ User authentication API implemented and tested"
  - Return trace_id for user to inspect
```

### Integration with Agent OS Enhanced

**MCP Server Auto-Discovery:**

```python
def _discover_mcp_server(self) -> str:
    """
    Find MCP server in .praxis-os/mcp_server/
    
    1. Check .praxis-os/mcp.json for URL
    2. Check if server running on default port (4242)
    3. Optionally start server if not running
    """
    mcp_config = Path(".praxis-os/mcp.json")
    
    if mcp_config.exists():
        config = json.loads(mcp_config.read_text())
        return config.get("url", "http://localhost:4242/mcp")
    
    # Try default
    if self._check_server_alive("http://localhost:4242/mcp"):
        return "http://localhost:4242/mcp"
    
    # Start server
    self._start_mcp_server()
    return "http://localhost:4242/mcp"
```

**Standards Inheritance:**

Agents automatically have access to ALL project standards via `search_standards(...)` tool:

- Universal standards (from Agent OS Enhanced)
- Project standards (from target project's .praxis-os/standards/)
- Module standards (from browser-ide/standards/)

**Workflow Access:**

All agents can start workflows:

```python
# Backend agent implementing feature
result = await self.mcp.call_tool(
    "aos_workflow",
    action="start",
    workflow_type="spec_execution_v1",
    target_file=".praxis-os/specs/auth-api",
    options={"spec_path": ".praxis-os/specs/review/2025-10-23-auth-api"}
)
```

---

## 🔄 Options Considered

### Option A: Single Monolithic Agent (Current State)

**Architecture:**
- One agent handles all domains
- Uses MCP tools for workflows, standards, browser
- Cursor IDE as interface

**Pros:**
- ✅ Proven (49+ sessions, stable)
- ✅ Simple (no coordination complexity)
- ✅ No new infrastructure needed
- ✅ Works well for small-medium tasks

**Cons:**
- ❌ Cognitive load on single agent (jack-of-all-trades)
- ❌ No parallelization (sequential execution)
- ❌ Context dilution (frontend + backend + infra in one session)
- ❌ No specialization (generalist vs. expert)

**When to Use:**
- Small projects (< 10K lines)
- Solo developer
- Simple domain (frontend-only or backend-only)
- Quick prototyping

### Option B: Multi-Agent with Custom Protocol (Build from Scratch)

**Architecture:**
- Custom agent communication protocol
- Custom coordination logic
- Custom observability/tracing

**Pros:**
- ✅ Full control over communication
- ✅ Optimized for exact use case
- ✅ No external dependencies

**Cons:**
- ❌ High development cost (build protocol, coordination, tracing)
- ❌ Reinventing wheel (A2A protocol exists)
- ❌ No interoperability (custom protocol = locked in)
- ❌ Hard to debug (no standard tooling)

**When to Use:**
- Specific coordination requirements A2A can't handle
- Performance critical (need custom optimization)
- Research project (exploring novel patterns)

### Option C: Multi-Agent with A2A + Browser IDE + HoneyHive (Proposed)

**Architecture:**
- A2A protocol for agent communication
- GenericAgent class (behavior from markdown prompts)
- Browser-based UI (React + FastAPI backend)
- HoneyHive tracing for observability
- Full MCP integration (all agents access workflows/standards)

**Pros:**
- ✅ Standard protocol (A2A = interoperability)
- ✅ Specialization (domain experts vs. generalist)
- ✅ Parallelization (independent work simultaneous)
- ✅ Observability (HoneyHive traces all decisions)
- ✅ Lightweight (< 100MB backend, browser frontend)
- ✅ Prompt-driven (add agents = add markdown file)
- ✅ Module pattern (extends Agent OS Enhanced)
- ✅ Feasibility exploration (low commitment)

**Cons:**
- ❌ Coordination complexity (orchestrator must route correctly)
- ❌ A2A protocol dependency (if abandoned, need alternative)
- ❌ More moving parts (backend server, multiple agents)
- ❌ Debugging harder (distributed system issues)
- ❌ Overkill for simple tasks (single agent faster)

**When to Use:**
- Complex projects (> 10K lines, multiple domains)
- Exploring multi-agent patterns
- Want observability (understand agent decisions)
- Building agent teams for enterprise

### Option D: Multi-Agent with Cursor IDE Extensions (No Browser UI)

**Architecture:**
- Multiple agents running in background
- Cursor IDE remains interface
- A2A coordination behind scenes
- No separate UI

**Pros:**
- ✅ Familiar interface (Cursor IDE)
- ✅ No frontend to build
- ✅ Multi-agent benefits (specialization, parallelization)

**Cons:**
- ❌ Hard to visualize agent activity (all in chat)
- ❌ Cursor IDE not designed for multi-agent (single chat window)
- ❌ Tracing visibility limited (no dedicated UI)
- ❌ Extension API constraints (what's possible in Cursor?)

**When to Use:**
- Don't want separate UI
- Cursor IDE extension API supports multi-agent
- Primary focus on coordination, not visualization

---

## 🎯 Recommendation: Option C (Multi-Agent + Browser IDE + HoneyHive)

**Why:**

1. **Feasibility Goal**: This is exploration, not production. Option C lets us validate multi-agent patterns without massive investment.

2. **Observability Critical**: HoneyHive tracing is the whole point - understand agent behavior, improve prompts iteratively.

3. **Module Pattern**: Establishes how to extend Agent OS Enhanced with new capabilities (browser-ide is first module, more to come).

4. **Standard Protocol**: A2A gives interoperability, community support, future-proofing.

5. **Lightweight**: Browser-based < 100MB backend vs. Electron ~250MB. Fast iteration.

6. **Prompt-Driven**: Adding agents = adding markdown file. No code changes needed.

7. **Josh's Experience**: 2.5 months AI experience, zero baggage, first-principles approach working. Multi-agent is natural next step.

**If this fails:**
- Fall back to Option A (single agent + MCP)
- Learnings captured in HoneyHive traces
- Module system pattern still validated
- No vendor lock-in (A2A standard protocol)

**If this succeeds:**
- Expand specialist agents (more domains)
- Add agent-to-agent review loops
- Build standards module ecosystem
- Scale to enterprise (HoneyHive customers)

---

## ⚠️ Risks & Mitigations

### Risk 1: Coordination Overhead > Single Agent Efficiency

**Description**: Orchestrator routing, A2A message passing, agent synchronization adds latency

**Probability**: Medium  
**Impact**: High (defeats purpose if slower than single agent)

**Mitigation**:
- Start with 3 agents (orchestrator + 2 specialists), not 5+
- Profile with HoneyHive (identify coordination bottlenecks)
- Hybrid approach: Simple tasks use single agent, complex tasks use team
- Measure: Time to completion (single agent vs. multi-agent for same task)

**Contingency**:
- If overhead > 2x single agent, limit to highly parallel tasks only
- Provide "single agent mode" fallback in UI
- Document when multi-agent appropriate vs. overkill

### Risk 2: A2A Protocol Immature / Abandoned

**Description**: a2a-python SDK has bugs, lacks features, or project abandoned

**Probability**: Medium  
**Impact**: Medium (can implement custom protocol, but delays project)

**Mitigation**:
- Evaluate A2A SDK thoroughly before committing
- Abstract communication layer (AgentCommunicator interface)
- Keep agent logic independent of protocol
- Contribute back to a2a-python if issues found

**Contingency**:
- Implement minimal custom protocol (JSON over HTTP/WebSockets)
- Focus on orchestrator → specialist pattern (simpler than full mesh)
- Re-evaluate alternatives (AutoGen, LangGraph multi-agent)

### Risk 3: HoneyHive Tracing Overhead Slows Agents

**Description**: Instrumenting every call adds latency, impacts agent responsiveness

**Probability**: Low  
**Impact**: Medium (observability vs. performance trade-off)

**Mitigation**:
- Use async tracing (non-blocking)
- Sample traces for high-volume operations
- Make tracing optional (flag to disable)
- Profile: Measure agent latency with/without tracing

**Contingency**:
- Disable tracing for production-speed tasks
- Use tracing only during prompt iteration/debugging
- Implement client-side buffering (batch trace uploads)

### Risk 4: Prompt Engineering Harder for Specialist Agents

**Description**: Single agent prompts proven (49 sessions). Specialist prompts need coordination instructions, more complex.

**Probability**: High  
**Impact**: Medium (agents make wrong decisions, poor coordination)

**Mitigation**:
- Start with orchestrator.md prompt (most critical)
- Iterate on prompts using HoneyHive trace analysis
- Document prompt patterns (standards/agent-prompt-authoring.md)
- Test coordination scenarios (integration tests for A2A flows)

**Contingency**:
- Provide "verbose mode" (agents explain reasoning before acting)
- Agent-to-agent review loop (QA agent reviews backend work)
- Human-in-loop approval for high-risk operations

### Risk 5: Browser IDE UI Becomes Scope Creep

**Description**: Users want full IDE features (debugging, git UI, extensions)

**Probability**: High  
**Impact**: Low (feature requests distract, but easy to say no)

**Mitigation**:
- Clear non-goals in documentation (not replacing Cursor/VS Code)
- Explicit scope: Monitoring agent activity, not full development
- Direct users to Cursor for code editing, browser-IDE for observation
- Ship MVP with minimal features, resist additions

**Contingency**:
- Focus on agent coordination value, not UI polish
- Terminal access handles advanced operations
- If UI becomes burden, drop it (agents still work via API)

---

## ❓ Open Questions

### 1. Should Agents Share Context or Operate Independently?

**Question**: Should backend agent see frontend agent's work? Or isolated?

**Options**:
- **Shared Context**: All agents see all files, all history
  - Pros: Better coordination, agents aware of each other's work
  - Cons: Context dilution (same problem as single agent)

- **Isolated Context**: Each agent only sees relevant domain
  - Pros: Focused attention, clear boundaries
  - Cons: Coordination harder, duplication possible

- **Hybrid**: Orchestrator sees all, specialists see their domain + explicitly shared context
  - Pros: Balance of focus and coordination
  - Cons: Orchestrator must manage what to share

**Recommendation**: Hybrid (orchestrator sees all, shares relevant context)

**Decision Needed**: Josh - which approach feels right?

### 2. How to Handle Conflicting Agent Decisions?

**Question**: If backend agent and QA agent disagree on approach, who decides?

**Options**:
- **Orchestrator Decides**: Final authority, resolves conflicts
- **Specialist Deference**: QA defers to backend on implementation, backend defers to QA on testing
- **User Escalation**: Conflicts bubble to user for decision
- **Voting**: Multiple agents vote (requires 3+ agents per domain)

**Recommendation**: Orchestrator decides, with user escalation for high-impact conflicts

**Decision Needed**: Josh - conflict resolution strategy?

### 3. Should Module System Support Remote Modules?

**Question**: Can users install modules from URLs (like npm packages)?

**Options**:
- **Local Only**: Modules in .praxis-os/modules/, manually copied
  - Pros: Simple, secure (no remote code execution)
  - Cons: Hard to share, no ecosystem

- **Remote Registry**: `agent-os install browser-ide` fetches from registry
  - Pros: Easy sharing, ecosystem growth
  - Cons: Security risk, dependency hell

- **Git-Based**: `agent-os install github.com/user/module`
  - Pros: Decentralized, version control
  - Cons: Still remote code execution risk

**Recommendation**: Start local-only, add git-based later if validated

**Decision Needed**: Josh - module distribution strategy?

---

## 📊 Success Criteria

### Feasibility Validation

- [ ] Launch 3+ agents (orchestrator, backend, frontend) successfully
- [ ] Orchestrator delegates task to specialist, receives result
- [ ] Specialist uses MCP tools (aos_workflow, search_standards)
- [ ] HoneyHive captures full trace (user → orchestrator → specialist → MCP)
- [ ] Browser UI displays agent activity in real-time

### Performance Baseline

- [ ] Multi-agent completion time ≤ 2x single agent (for parallelizable work)
- [ ] Agent response latency < 5s (user message → orchestrator acknowledgment)
- [ ] HoneyHive tracing overhead < 10% (measured via agent latency)

### Quality Outcomes

- [ ] Specialist agents follow project standards (Pylint 10.0, MyPy passing)
- [ ] Code produced by agents passes quality gates
- [ ] Integration between specialist work is clean (APIs align)

### Observability Goals

- [ ] Can trace user request → orchestrator → specialists → completion
- [ ] Can see which standards agents queried (RAG effectiveness)
- [ ] Can identify coordination bottlenecks (A2A message delays)
- [ ] Can iterate on prompts based on trace analysis

### Module System Validation

- [ ] Browser-IDE module installs into Agent OS Enhanced project
- [ ] Module standards accessible via search_standards
- [ ] Module workflows accessible via aos_workflow
- [ ] Module can be removed cleanly (no residual state)

---

## 🗂️ File Change Summary

### Files to Create

**Module Structure:**
- `.praxis-os/modules/browser-ide/README.md`
- `.praxis-os/modules/browser-ide/requirements.txt`
- `.praxis-os/modules/browser-ide/package.json`

**Backend (Python):**
- `.praxis-os/modules/browser-ide/backend/main.py`
- `.praxis-os/modules/browser-ide/backend/agents/base_agent.py`
- `.praxis-os/modules/browser-ide/backend/services/launcher.py`
- `.praxis-os/modules/browser-ide/backend/services/file_ops.py`
- `.praxis-os/modules/browser-ide/backend/services/tracing.py`

**Agent Prompts:**
- `.praxis-os/modules/browser-ide/backend/prompts/orchestrator.md`
- `.praxis-os/modules/browser-ide/backend/prompts/backend.md`
- `.praxis-os/modules/browser-ide/backend/prompts/frontend.md`
- `.praxis-os/modules/browser-ide/backend/prompts/qa.md`
- `.praxis-os/modules/browser-ide/backend/prompts/devops.md`

**Frontend (React):**
- `.praxis-os/modules/browser-ide/frontend/src/App.tsx`
- `.praxis-os/modules/browser-ide/frontend/src/components/ChatPanel.tsx`
- `.praxis-os/modules/browser-ide/frontend/src/components/AgentStatus.tsx`
- `.praxis-os/modules/browser-ide/frontend/src/components/FileTree.tsx`
- `.praxis-os/modules/browser-ide/frontend/src/components/CodeEditor.tsx`
- `.praxis-os/modules/browser-ide/frontend/src/components/Terminal.tsx`
- `.praxis-os/modules/browser-ide/frontend/src/components/TraceView.tsx`
- `.praxis-os/modules/browser-ide/frontend/src/services/api.ts`

**Module Standards:**
- `.praxis-os/modules/browser-ide/standards/multi-agent-coordination.md`
- `.praxis-os/modules/browser-ide/standards/agent-prompt-authoring.md`

**Tests:**
- `.praxis-os/modules/browser-ide/backend/tests/test_agents.py`
- `.praxis-os/modules/browser-ide/backend/tests/test_launcher.py`

### Files to Modify

- `.praxis-os/README.md` - Document module system
- `docs/content/how-to-guides/install-modules.md` - New guide

### Files to Delete

None (this is additive)

---

## 🧪 Testing Approach

### Unit Tests

**Backend:**
- `test_agents.py`: GenericAgent initialization, MCP discovery, prompt loading
- `test_launcher.py`: Agent launching, shutdown, restart
- `test_tracing.py`: HoneyHive instrumentation, trace capture

**Frontend:**
- Component tests (ChatPanel, AgentStatus, etc.)
- API client tests (mock backend responses)

### Integration Tests

**Agent Coordination:**
- Test: User message → orchestrator → backend agent → completion
- Test: Parallel execution (backend + frontend agents work simultaneously)
- Test: A2A message passing (orchestrator → specialist → response)

**MCP Integration:**
- Test: Agent calls aos_workflow successfully
- Test: Agent calls search_standards, receives results
- Test: Agent calls aos_browser, interacts with page

**HoneyHive Tracing:**
- Test: Trace captured for full task flow
- Test: Trace includes A2A messages, MCP calls, LLM calls
- Test: Trace accessible via API (/api/traces/{id})

### Manual Validation

**Scenarios to Test:**
1. **Simple Task**: "Add a new endpoint GET /health" (single agent should handle)
2. **Complex Task**: "Build user authentication with JWT" (multi-agent: backend + qa)
3. **Parallel Task**: "Add login form (frontend) and auth API (backend)" (true parallel)
4. **Coordination Failure**: Give conflicting requirements, verify orchestrator handles
5. **Tool Usage**: Verify agents use search_standards before implementing

---

## 📚 Related Work & Inspiration

### Agent OS Enhanced (Foundation)

This entire module builds on Agent OS Enhanced:
- MCP tooling (workflows, standards, browser)
- Phase gating (validation, evidence)
- RAG behavioral reinforcement
- Per-project isolation

**Key insight from Josh's work**: Don't work around AI limitations, eliminate them with system design.

### A2A Protocol (Agent Communication)

- Standard protocol for agent-to-agent messaging
- Task delegation, status updates, result passing
- HTTP/gRPC transport options
- Python SDK: https://github.com/a2aproject/a2a-python

### HoneyHive (Observability)

- Distributed tracing for AI/LLM applications
- OpenTelemetry-based instrumentation
- Already used in production at HoneyHive
- Perfect for understanding agent behavior

### Browser-Based IDEs (UI Patterns)

- VS Code for Web (Monaco editor, terminal)
- Replit (collaborative, browser-based)
- StackBlitz (WebContainers, local execution)

**Our approach**: Not competing with IDEs. Browser UI is for monitoring agents, not replacing Cursor.

---

## 🎯 Key Insights

### 1. Josh's "No Baggage" Advantage

**Started AI work August 2025 (2.5 months ago).**

Most people:
- "AI can't handle complex refactoring"
- "AI will skip tests"
- "AI loses context"

Josh:
- "What SHOULD be possible with correct system design?"
- Built adversarial design (phase gating)
- Built evidence validation (no shortcuts)
- Built RAG reinforcement (knowledge compounding)

**Result**: 110% AI authorship goal, complex refactors successful, 49+ sessions stable.

**Lesson**: Not working around AI limitations, eliminating them.

### 2. Module System Enables Ecosystem

Browser-IDE is **first module**, not last:

**Future Modules:**
- `testing-framework`: Advanced testing agents, coverage analysis
- `deployment-automation`: CI/CD specialists, infra-as-code
- `standards-packs`: Domain-specific standards (Python, React, Go, Rust)
- `observability-enhanced`: APM integration, log analysis agents
- `security-audit`: Security scanning, vulnerability detection

**Pattern**: Drop module into .praxis-os/modules/, agents auto-integrate.

### 3. HoneyHive Tracing = Iterative Prompt Improvement

**The fun part (per Josh):**

> "I can use HoneyHive to trace my agents to understand and improve on their behavior."

**Workflow:**
1. Agent makes suboptimal decision
2. Inspect HoneyHive trace (what standards queried? what tools used? what was prompt?)
3. Adjust system prompt (orchestrator.md, backend.md, etc.)
4. Re-run task, compare traces
5. Iterate until behavior optimal

**This is the feedback loop Agent OS Enhanced enables.**

### 4. Browser UI Is Optional

**If browser IDE becomes burden:**
- Agents still work via API
- Cursor can call backend directly
- Browser UI is convenience, not requirement

**Focus**: Agent coordination, not UI polish.

---

## 🚀 Next Steps (After Decision)

**If Josh approves this design:**

1. **Create Spec** (via spec_creation_v1 workflow)
   - Convert design doc → detailed spec
   - Break into tasks (implementation plan)

2. **Phase 1: Backend + Single Agent** (Validate basics)
   - GenericAgent class
   - Agent launcher
   - MCP integration
   - HoneyHive tracing
   - Test: Launch one agent, call MCP tools

3. **Phase 2: Multi-Agent Coordination** (Validate A2A)
   - Orchestrator + backend specialist
   - A2A message passing
   - Test: Delegate task, receive result

4. **Phase 3: Browser UI** (Validate observability)
   - FastAPI backend
   - React frontend (ChatPanel, AgentStatus)
   - WebSocket events
   - Test: Watch agents work in real-time

5. **Phase 4: HoneyHive Integration** (Validate tracing)
   - Instrument all agent calls
   - Trace visualization in UI
   - Test: Full trace from user → orchestrator → specialist

6. **Phase 5: Iteration** (Validate prompt improvement)
   - Run complex tasks
   - Analyze traces
   - Improve prompts
   - Measure: Coordination efficiency, quality outcomes

---

## 💡 Why This Matters

**Josh started AI work 2.5 months ago. Now building:**
- Multi-agent coordination systems
- Browser-based development environments
- Observability infrastructure for AI teams
- Module ecosystems for Agent OS Enhanced

**Enterprise adoption coming:**
- HoneyHive projects (company-wide)
- Friends at large tech companies
- HoneyHive customers

**This isn't just a side project. It's validation of:**
1. AI can own codebases (110% authorship)
2. Multi-agent teams can collaborate effectively
3. Observability enables iterative improvement
4. First-principles approach > inherited baggage

**If this works, it changes how software gets built.**

---

**Version**: 1.0.0  
**Created**: 2025-10-23  
**Last Updated**: 2025-10-23  
**Next Review**: After feasibility validation (3 agents launched, task delegated, traced)

