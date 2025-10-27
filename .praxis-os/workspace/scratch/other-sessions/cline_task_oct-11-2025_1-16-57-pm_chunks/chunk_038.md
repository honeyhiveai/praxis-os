[Composio’s MCP Marketplace](https://mcp.composio.dev/) provides access to a wide range of third-party servers that support the Model Context Protocol (MCP). These servers expose APIs for services like GitHub, Notion, Slack, and others. Each server includes configuration instructions and built-in authentication support (e.g. OAuth or API keys). To connect, locate the desired service in the marketplace and follow the integration steps provided there.

#### 

[​

](#connecting-via-smithery)

Connecting via Smithery

Smithery is a third-party MCP server marketplace that allows users to discover and connect to a variety of Model Context Protocol (MCP) servers. If you’re using an MCP-compatible client (such as Cursor, Claude Desktop, or Cline), you can browse available servers and integrate them directly into your workflow. To explore available options, visit the Smithery marketplace: [https://smithery.ai](https://smithery.ai) Please note: Smithery is maintained independently and is not affiliated with our project. Use at your own discretion.

### 

[​

](#managing-installed-mcp-servers)

Managing Installed MCP Servers

Once added, your MCP servers appear in the “Configure” tab where you can:

#### 

[​

](#view-server-status)

View Server Status

Each server displays its current status:

*   **Green dot**: Connected and ready to use
*   **Yellow dot**: In the process of connecting
*   **Red dot**: Disconnected or experiencing errors

#### 

[​

](#configure-server-settings)

Configure Server Settings

Click on a server to expand its settings panel:

1.  **Tools & Resources**:
    *   View all available tools and resources from the server
    *   Configure auto-approval settings for tools (if enabled)
2.  **Request Timeout**:
    *   Set how long Cline should wait for server responses
    *   Options range from 30 seconds to 1 hour
3.  **Server Management**:
    *   **Restart Server**: Reconnect if the server becomes unresponsive
    *   **Delete Server**: Remove the server from your configuration

#### 

[​

](#enable%2Fdisable-servers)

Enable/Disable Servers

Toggle the switch next to each server to enable or disable it:

*   **Enabled**: Cline can use the server’s tools and resources
*   **Disabled**: The server remains in your configuration but is not active

### 

[​

](#troubleshooting-connection-issues)

Troubleshooting Connection Issues

If a server fails to connect:

1.  An error message will be displayed with details about the failure
2.  Check that the server URL is correct and the server is running
3.  Use the “Restart Server” button to attempt reconnection
4.  If problems persist, you can delete the server and try adding it again

### 

[​

](#advanced-configuration)

Advanced Configuration

For advanced users, Cline stores MCP server configurations in a JSON file that can be modified:

1.  In the “Configure” tab, click “Configure MCP Servers” to access the settings file
2.  The configuration for each server follows this format:

Copy

Ask AI

    {
    	"mcpServers": {
    		"exampleServer": {
    			"url": "https://example.com/mcp-sse",
    			"disabled": false,
    			"autoApprove": ["tool1", "tool2"],
    			"timeout": 30
    		}
    	}
    }
    

Key configuration options:

*   **url**: The endpoint URL (for remote servers)
*   **disabled**: Whether the server is currently enabled (true/false)
*   **autoApprove**: List of tool names that don’t require confirmation
*   **timeout**: Maximum time in seconds to wait for server responses

For additional MCP settings, click the “Advanced MCP Settings” link to access VSCode settings.

### 

[​

](#using-mcp-server-tools)

Using MCP Server Tools

Once connected, Cline can use the tools and resources provided by the MCP server. When Cline suggests using an MCP tool:

1.  A tool approval prompt will appear (unless auto-approved)
2.  Review the tool details and parameters before approving
3.  The tool will execute and return results to Cline

[

Configuring MCP Servers



](/mcp/configuring-mcp-servers)[

MCP Made Easy



](/mcp/mcp-marketplace)

⌘I

Assistant

Responses are generated using AI and may contain mistakes.
<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/11/2025, 10:21:57 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
137,576 / 200K tokens used (69%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
## Found the Issue! Config Format is Correct

### Cline's Remote MCP Server Config Format

**From Cline documentation:**
```json
{
  "mcpServers": {
    "exampleServer": {
      "url": "https://example.com/mcp-sse",
      "disabled": false,
      "autoApprove": ["tool1", "tool2"],
      "timeout": 30
    }
  }
}
```

### Your Current Config

```json
{
  "mcpServers": {
    "agent-os-enhanced": {
      "disabled": false,
      "timeout": 60,
      "type": "sse",
      "url": "http://127.0.0.1:4242/mcp"
    }
  }
}
```

**This is CORRECT!** ✅

### The Real Problem: SSE vs HTTP Transport

**Cline expects SSE (Server-Sent Events) transport** for remote servers. Notice the example URL ends in `/mcp-sse`.

**Your Agent OS server might be running "http" transport**, not "sse" transport.

### Check Your Server Transport

From the spec, FastMCP supports both:
- `transport="streamable-http"` - HTTP with streaming
- `transport="sse"` - Server-Sent Events

**Check how your server is running:**

```bash
# Check your __main__.py or wherever transport is set
# Look for:
mcp.run(transport="streamable-http", ...)  # This might not work with Cline
# vs
mcp.run(transport="sse", ...)  # Cline expects this
```

### Solution

**Update your Agent OS server to use SSE transport:**

```python
# In transport_manager.py or __main__.py
# Change from:
mcp.run(transport="streamable-http", ...)

# To:
mcp.run(transport="sse", ...)
```

**Then restart the server.**

### Why This Matters

- **Cline documentation** shows remote servers using SSE URLs
- **Your curl test worked** because HTTP endpoints respond
- **But Cline specifically expects SSE transport** for remote connections
- **FastMCP supports both** - just need to use SSE instead

### Next Steps

1. **Check your server's transport type** (streamable-http vs sse)
2. **If using streamable-http, change to sse**
3. **Restart the MCP server**
4. **The curl test would still work** (SSE is HTTP-based)
5. **Cline should connect successfully**

**The config is correct - the issue is likely the server transport type!**
</result>
<task_progress>
- [x] Found Cline's remote MCP config documentation
- [x] Verified config format is CORRECT
- [x] Identified real issue: Server transport type (http vs sse)
- [x] FastMCP supports both transports
- [x] Cline expects SSE for remote servers
- [x] Solution: Change server to use transport="sse"
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
what is the difference in sse and streaming-http, fastmcp thinks sse it legacy http access, what is cline's view on this
</feedback>
<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/11/2025, 10:23:17 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
143,183 / 200K tokens used (72%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<web_fetch>
<url>https://docs.cline.bot/mcp/mcp-transport-mechanisms</url>
<task_progress>
- [ ] Fetch Cline's MCP transport mechanisms documentation
- [ ] Understand SSE vs streaming-http from Cline's perspective
- [ ] Clarify the difference and which to use
</task_progress>
</web_fetch>

---

**User:**

[web_fetch for 'https://docs.cline.bot/mcp/mcp-transport-mechanisms'] Result:
Fetched Markdown for https://docs.cline.bot/mcp/mcp-transport-mechanisms:

MCP Transport Mechanisms - Cline

[Skip to main content](#content-area)

[Cline home page![light logo](https://mintcdn.com/cline-efdc8260/_dolQeWZW8NdpVp-/assets/robot_panel_light.png?fit=max&auto=format&n=_dolQeWZW8NdpVp-&q=85&s=64692d68ce42dc99a5cb9f3771d1b450)![dark logo](https://mintcdn.com/cline-efdc8260/_dolQeWZW8NdpVp-/assets/robot_panel_dark.png?fit=max&auto=format&n=_dolQeWZW8NdpVp-&q=85&s=53b1d8433265a914528ff6afa1419412)](/)

Search...

Search...

Navigation

MCP Servers

MCP Transport Mechanisms

##### Getting Started

*   [
    
    What is Cline?
    
    
    
    ](/getting-started/what-is-cline)
*   [
    
    Installing Cline
    
    
    
    ](/getting-started/installing-cline)
*   [
    
    Model Selection Guide
    
    
    
    ](/getting-started/model-selection-guide)
*   [
    
    Task Management in Cline
    
    
    
    ](/getting-started/task-management)
*   [
    
    Context Management
    
    
    
    ](/getting-started/understanding-context-management)
*   For New Coders
    

##### Improving Your Prompting Skills

*   [
    
    Prompt Engineering Guide
    
    
    
    ](/prompting/prompt-engineering-guide)
*   [
    
    Cline Memory Bank
    
    
    
    ](/prompting/cline-memory-bank)

##### Features

*   @ Mentions
    
*   [
    
    Auto approve
    
    
    
    ](/features/auto-approve)
*   [
    
    Auto Compact
    
    
    
    ](/features/auto-compact)
*   [
    
    Checkpoints
    
    
    
    ](/features/checkpoints)
*   [
    
    Cline rules
    
    
    
    ](/features/cline-rules)
*   Commands & Shortcuts
    
*   Customization
    
*   [
    
    Dictation
    
    
    
    ](/features/dictation)
*   [
    
    Drag & Drop
    
    
    
    ](/features/drag-and-drop)
*   [
    
    Editing Messages
    
    
    
    ](/features/editing-messages)
*   [
    
    Focus Chain
    
    
    
    ](/features/focus-chain)
*   [
    
    Multiroot Workspace
    
    
    
    ](/features/multiroot-workspace)
*   [
    
    Plan & Act
    
    
    
    ](/features/plan-and-act)
*   Slash Commands
    
*   [
    
    Workflows
    
    
    
    ](/features/slash-commands/workflows)
*   [
    
    YOLO Mode
    
    
    
    ](/features/yolo-mode)

##### Exploring Cline's Tools

*   [
    
    Cline Tools Reference Guide
    
    
    
    ](/exploring-clines-tools/cline-tools-guide)
*   [
    
    New Task Tool
    
    
    
    ](/exploring-clines-tools/new-task-tool)
*   [
    
    Remote Browser Support
    
    
    
    ](/exploring-clines-tools/remote-browser-support)

##### Enterprise Solutions

*   [
    
    Cloud Provider Integration
    
    
    
    ](/enterprise-solutions/cloud-provider-integration)
*   [
    
    Custom Instructions
    
    
    
    ](/enterprise-solutions/custom-instructions)
*   [
    
    MCP Servers
    
    
    
    ](/enterprise-solutions/mcp-servers)
*   [
    
    Security Concerns
    
    
    
    ](/enterprise-solutions/security-concerns)

##### MCP Servers

*   [
    
    MCP Overview
    
    
    
    ](/mcp/mcp-overview)
*   [
    
    Adding MCP Servers from GitHub
    
    
    
    ](/mcp/adding-mcp-servers-from-github)
*   [
    
    Configuring MCP Servers
    
    
    
    ](/mcp/configuring-mcp-servers)
*   [
    
    Connecting to a Remote Server
    
    
    
    ](/mcp/connecting-to-a-remote-server)
*   [
    
    MCP Made Easy
    
    
    
    ](/mcp/mcp-marketplace)
*   [
    
    MCP Server Development Protocol
    
    
    
    ](/mcp/mcp-server-development-protocol)
*   [
    
    MCP Transport Mechanisms
    
    
    
    ](/mcp/mcp-transport-mechanisms)

##### Provider Configuration

*   [
    
    Anthropic
    
    
    
    ](/provider-config/anthropic)
*   [
    
    Claude Code
    
    
    
    ](/provider-config/claude-code)
*   AWS Bedrock
    
*   [
    
    GCP Vertex AI
    
    
    
    ](/provider-config/gcp-vertex-ai)
*   [
    
    LiteLLM & Cline (using Codestral)
    
    
    
    ](/provider-config/litellm-and-cline-using-codestral)
*   [
    
    VS Code Language Model API
    
    
    
    ](/provider-config/vscode-language-model-api)
*   [
    
    xAI (Grok)
    
    
    
    ](/provider-config/xai-grok)
*   [
    
    Mistral
    
    
    
    ](/provider-config/mistral-ai)
*   [
    
    DeepSeek
    
    
    
    ](/provider-config/deepseek)
*   [
    
    Groq
    
    
    
    ](/provider-config/groq)
*   [
    
    Cerebras
    
    
    
    ](/provider-config/cerebras)
*   [
    
    Doubao
    
    
    
    ](/provider-config/doubao)
*   [
    
    Fireworks AI
    
    
    
    ](/provider-config/fireworks)
*   [
    
    Z AI (Zhipu AI)
    
    
    
    ](/provider-config/zai)
*   [
    
    Ollama
    
    
    
    ](/provider-config/ollama)
*   [
    
    OpenAI
    
    
    
    ](/provider-config/openai)
*   [
    
    OpenAI Compatible
    
    
    
    ](/provider-config/openai-compatible)
*   [
    
    OpenRouter
    
    
    
    ](/provider-config/openrouter)
*   [
    
    SAP AI Core
    
    
    
    ](/provider-config/sap-aicore)
*   [
    
    Vercel AI Gateway
    
    
    
    ](/provider-config/vercel-ai-gateway)
*   [
    
    Requesty
    
    
    
    ](/provider-config/requesty)
*   [
    
    Baseten
    
    
    
    ](/provider-config/baseten)

##### Running Models Locally

*   [
    
    Read Me First
    
    
    
    ](/running-models-locally/read-me-first)
*   [
    
    LM Studio
    
    
    
    ](/running-models-locally/lm-studio)
*   [
    
    Ollama
    
    
    
    ](/running-models-locally/ollama)

##### Troubleshooting

*   [
    
    Terminal Quick Fixes
    
    
    
    ](/troubleshooting/terminal-quick-fixes)
*   [
    
    Terminal Troubleshooting
    
    
    
    ](/troubleshooting/terminal-integration-guide)

##### More Info

*   [
    
    Telemetry
    
    
    
    ](/more-info/telemetry)

On this page

*   [STDIO Transport](#stdio-transport)
*   [How STDIO Transport Works](#how-stdio-transport-works)
*   [STDIO Characteristics](#stdio-characteristics)
*   [When to Use STDIO](#when-to-use-stdio)
*   [STDIO Implementation Example](#stdio-implementation-example)
*   [SSE Transport](#sse-transport)
*   [How SSE Transport Works](#how-sse-transport-works)
*   [SSE Characteristics](#sse-characteristics)
*   [When to Use SSE](#when-to-use-sse)
*   [SSE Implementation Example](#sse-implementation-example)
*   [Local vs. Hosted: Deployment Aspects](#local-vs-hosted%3A-deployment-aspects)
*   [STDIO: Local Deployment Model](#stdio%3A-local-deployment-model)
*   [Practical Example](#practical-example)
*   [SSE: Hosted Deployment Model](#sse%3A-hosted-deployment-model)
*   [Practical Example](#practical-example-2)
*   [Hybrid Approaches](#hybrid-approaches)
*   [Choosing Between STDIO and SSE](#choosing-between-stdio-and-sse)
*   [Configuring Transports in Cline](#configuring-transports-in-cline)

Model Context Protocol (MCP) supports two primary transport mechanisms for communication between Cline and MCP servers: Standard Input/Output (STDIO) and Server-Sent Events (SSE). Each has distinct characteristics, advantages, and use cases.

[​

](#stdio-transport)

STDIO Transport
------------------------------------------

STDIO transport runs locally on your machine and communicates via standard input/output streams.

### 

[​

](#how-stdio-transport-works)

How STDIO Transport Works

1.  The client (Cline) spawns an MCP server as a child process
2.  Communication happens through process streams: client writes to server’s STDIN, server responds to STDOUT
3.  Each message is delimited by a newline character
4.  Messages are formatted as JSON-RPC 2.0

Copy

Ask AI

    Client                    Server
      |                         |
      |<---- JSON message ----->| (via STDIN)
      |                         | (processes request)
      |<---- JSON message ------| (via STDOUT)
      |                         |
    

### 

[​

](#stdio-characteristics)

STDIO Characteristics

*   **Locality**: Runs on the same machine as Cline
*   **Performance**: Very low latency and overhead (no network stack involved)
*   **Simplicity**: Direct process communication without network configuration
*   **Relationship**: One-to-one relationship between client and server
*   **Security**: Inherently more secure as no network exposure

### 

[​

](#when-to-use-stdio)

When to Use STDIO

STDIO transport is ideal for:

*   Local integrations and tools running on the same machine
*   Security-sensitive operations
*   Low-latency requirements
*   Single-client scenarios (one Cline instance per server)
*   Command-line tools or IDE extensions

### 

[​

](#stdio-implementation-example)

STDIO Implementation Example

Copy

Ask AI

    import { Server } from "@modelcontextprotocol/sdk/server/index.js"
    import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js"
    
    const server = new Server({ name: "local-server", version: "1.0.0" })
    // Register tools...
    
    // Use STDIO transport
    const transport = new StdioServerTransport(server)
    transport.listen()
    

[​

](#sse-transport)

SSE Transport
--------------------------------------

Server-Sent Events (SSE) transport runs on a remote server and communicates over HTTP/HTTPS.

### 

[​

](#how-sse-transport-works)

How SSE Transport Works

1.  The client (Cline) connects to the server’s SSE endpoint via HTTP GET request
2.  This establishes a persistent connection where the server can push events to the client
3.  For client-to-server communication, the client makes HTTP POST requests to a separate endpoint
4.  Communication happens over two channels:
    *   Event Stream (GET): Server-to-client updates
    *   Message Endpoint (POST): Client-to-server requests

Copy

Ask AI

    Client                             Server
      |                                  |
      |---- HTTP GET /events ----------->| (establish SSE connection)
      |<---- SSE event stream -----------| (persistent connection)
      |                                  |
      |---- HTTP POST /message --------->| (client request)
      |<---- SSE event with response ----| (server response)
      |                                  |
    

### 

[​

](#sse-characteristics)

SSE Characteristics

*   **Remote Access**: Can be hosted on a different machine from your Cline instance
*   **Scalability**: Can handle multiple client connections concurrently
*   **Protocol**: Works over standard HTTP (no special protocols needed)
*   **Persistence**: Maintains a persistent connection for server-to-client messages
*   **Authentication**: Can use standard HTTP authentication mechanisms

### 

[​

](#when-to-use-sse)

When to Use SSE

SSE transport is better for:

*   Remote access across networks
*   Multi-client scenarios
*   Public services
*   Centralized tools that many users need to access
*   Integration with web services

### 

[​

](#sse-implementation-example)

SSE Implementation Example

Copy

Ask AI

    import { Server } from "@modelcontextprotocol/sdk/server/index.js"
    import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js"
    import express from "express"
    
    const app = express()
