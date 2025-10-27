](#editing-mcp-settings-files)

Editing MCP Settings Files
----------------------------------------------------------------

Settings for all installed MCP servers are located in the `cline_mcp_settings.json` file:

1.  Click the MCP Servers icon at the top navigation bar of the Cline pane.
2.  Select the “Configure” tab.
3.  Click the “Configure MCP Servers” button at the bottom of the pane.

The file uses a JSON format with a `mcpServers` object containing named server configurations:

Copy

Ask AI

    {
    	"mcpServers": {
    		"server1": {
    			"command": "python",
    			"args": ["/path/to/server.py"],
    			"env": {
    				"API_KEY": "your_api_key"
    			},
    			"alwaysAllow": ["tool1", "tool2"],
    			"disabled": false
    		}
    	}
    }
    

_Example of MCP Server config in Cline (STDIO Transport)_

* * *

[​

](#understanding-transport-types)

Understanding Transport Types
----------------------------------------------------------------------

MCP supports two transport types for server communication:

### 

[​

](#stdio-transport)

STDIO Transport

Used for local servers running on your machine:

*   Communicates via standard input/output streams
*   Lower latency (no network overhead)
*   Better security (no network exposure)
*   Simpler setup (no HTTP server needed)
*   Runs as a child process on your machine

For more in-depth information about how STDIO transport works, see [MCP Transport Mechanisms](/mcp/mcp-transport-mechanisms). STDIO configuration example:

Copy

Ask AI

    {
    	"mcpServers": {
    		"local-server": {
    			"command": "node",
    			"args": ["/path/to/server.js"],
    			"env": {
    				"API_KEY": "your_api_key"
    			},
    			"alwaysAllow": ["tool1", "tool2"],
    			"disabled": false
    		}
    	}
    }
    

### 

[​

](#sse-transport)

SSE Transport

Used for remote servers accessed over HTTP/HTTPS:

*   Communicates via Server-Sent Events protocol
*   Can be hosted on a different machine
*   Supports multiple client connections
*   Requires network access
*   Allows centralized deployment and management

For more in-depth information about how SSE transport works, see [MCP Transport Mechanisms](/mcp/mcp-transport-mechanisms). SSE configuration example:

Copy

Ask AI

    {
    	"mcpServers": {
    		"remote-server": {
    			"url": "https://your-server-url.com/mcp",
    			"headers": {
    				"Authorization": "Bearer your-token"
    			},
    			"alwaysAllow": ["tool3"],
    			"disabled": false
    		}
    	}
    }
    

* * *

[​

](#using-mcp-tools-in-your-workflow)

Using MCP Tools in Your Workflow
----------------------------------------------------------------------------

After configuring an MCP server, Cline will automatically detect available tools and resources. To use them:

1.  Type your request in Cline’s conversation window
2.  Cline will identify when an MCP tool can help with your task
3.  Approve the tool use when prompted (or use auto-approval)

Example: “Analyze the performance of my API” might use an MCP tool that tests API endpoints.

[​

](#troubleshooting-mcp-servers)

Troubleshooting MCP Servers
------------------------------------------------------------------

Common issues and solutions:

*   **Server Not Responding:** Check if the server process is running and verify network connectivity
*   **Permission Errors:** Ensure proper API keys and credentials are configured in your `mcp_settings.json` file
*   **Tool Not Available:** Confirm the server is properly implementing the tool and it’s not disabled in settings
*   **Slow Performance:** Try adjusting the network timeout value for the specific MCP server

[

Adding MCP Servers from GitHub



](/mcp/adding-mcp-servers-from-github)[

Connecting to a Remote Server



](/mcp/connecting-to-a-remote-server)

⌘I

Assistant

Responses are generated using AI and may contain mistakes.

![MCP settings edit](https://storage.googleapis.com/cline_public_images/docs/assets/MCP-settings-edit%20(1).png)

![MCP settings individual](https://storage.googleapis.com/cline_public_images/docs/assets/MCP-settings-individual.png)
<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:04:24 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
44,755 / 200K tokens used (22%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
Now I understand! According to Cline's documentation, **Cline uses a global MCP settings file, not workspace-specific configuration**.

**Why it uses the Library path:**

Cline stores MCP server configurations **globally** at:
```
~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

This is **intentional** - Cline's MCP servers are configured once globally and apply to all projects, rather than per-workspace like some other tools.

**The `.vscode/settings.json` file doesn't work for Cline** - that's specific to other VSCode/Cursor extensions, but Cline ignores it.

**How to properly configure MCP servers in Cline:**

1. Click the **"MCP Servers"** icon in Cline's top navigation bar
2. Select the **"Configure"** tab
3. Click **"Configure MCP Servers"** button at the bottom
4. This will open the global `cline_mcp_settings.json` file
5. Add your server configuration there:

```json
{
  "mcpServers": {
    "agent-os-enhanced": {
      "command": "/Users/josh/src/github.com/honeyhiveai/agent-os-enhanced/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "PROJECT_ROOT": "/Users/josh/src/github.com/honeyhiveai/agent-os-enhanced",
        "PYTHONPATH": "/Users/josh/src/github.com/honeyhiveai/agent-os-enhanced/.praxis-os",
        "PYTHONUNBUFFERED": "1"
      },
      "alwaysAllow": ["search_standards", "get_current_phase", "get_workflow_state"],
      "disabled": false
    }
  }
}
```

**Key difference from workspace config:**
- Use **absolute paths** (not `${workspaceFolder}`)
- Configuration applies globally, not per-project
- This is Cline's design - one global config for all MCP servers

Would you like me to help you add the correct configuration to the global file?
</result>
<task_progress>
- [x] Found why Cline uses global settings file
- [x] Read Cline MCP documentation
- [x] Explained global vs workspace approach
- [x] Provided correct configuration method
- [x] Explained absolute path requirement
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
this is a mess, because what is agent os is not installed in a repo?
</feedback>
<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:05:36 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
49,997 / 200K tokens used (25%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

You're absolutely right - this is a significant issue! If Agent OS is installed per-project in `.praxis-os/`, then Cline's global MCP configuration with absolute paths doesn't work well.

<web_fetch>
<url>https://docs.cline.bot/features/multiroot-workspace</url>
<task_progress>
- [x] Identified the problem with global config + per-project installation
- [ ] Check if Cline supports workspace-specific MCP configs
- [ ] Find solution for per-project MCP servers
- [ ] Recommend approach
</task_progress>
</web_fetch>

---

**User:**

[web_fetch for 'https://docs.cline.bot/features/multiroot-workspace'] Result:
Fetched Markdown for https://docs.cline.bot/features/multiroot-workspace:

Multiroot Workspace Support - Cline

[Skip to main content](#content-area)

[Cline home page![light logo](https://mintcdn.com/cline-efdc8260/_dolQeWZW8NdpVp-/assets/robot_panel_light.png?fit=max&auto=format&n=_dolQeWZW8NdpVp-&q=85&s=64692d68ce42dc99a5cb9f3771d1b450)![dark logo](https://mintcdn.com/cline-efdc8260/_dolQeWZW8NdpVp-/assets/robot_panel_dark.png?fit=max&auto=format&n=_dolQeWZW8NdpVp-&q=85&s=53b1d8433265a914528ff6afa1419412)](/)

Search...

Search...

Navigation

Features

Multiroot Workspace Support

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

*   [What is Multiroot Workspace Support?](#what-is-multiroot-workspace-support%3F)
*   [Getting Started](#getting-started)
*   [Setting Up Multi-Root Workspaces](#setting-up-multi-root-workspaces)
*   [How Cline Handles Multiple Workspaces](#how-cline-handles-multiple-workspaces)
*   [Working Across Workspaces](#working-across-workspaces)
*   [Let Cline explore, or guide it precisely](#let-cline-explore%2C-or-guide-it-precisely)
*   [Common Use Cases](#common-use-cases)
*   [Monorepo Development](#monorepo-development)
*   [Microservices Architecture](#microservices-architecture)
*   [Full-Stack Development](#full-stack-development)
*   [Auto-Approve Integration](#auto-approve-integration)
*   [Cross-Workspace Operations](#cross-workspace-operations)
*   [Best Practices](#best-practices)
*   [Organizing Your Workspaces](#organizing-your-workspaces)
*   [Effective Prompting & Tips](#effective-prompting-%26-tips)

Cline’s Multiroot feature _(experimental - Oct 1 2025)_ works seamlessly with VSCode’s multi-root workspaces, letting you manage multiple project folders in a single workspace.

[​

](#what-is-multiroot-workspace-support%3F)

What is Multiroot Workspace Support?
--------------------------------------------------------------------------------------

Instead of being limited to one project folder, Cline can read files, write code, and run commands across all folders in your VSCode workspace. This is helpful when working with monorepos, microservices, or when you’re working on related projects simultaneously.

[​

](#getting-started)

Getting Started
------------------------------------------

### 

[​

](#setting-up-multi-root-workspaces)

Setting Up Multi-Root Workspaces

1.  **Add folders to your workspace:**
    *   Use `File > Add Folder to Workspace` in VSCode
    *   Or create a `.code-workspace` file with multiple folder paths
    *   Drag and drop folders to the File Explorer
    *   Select multiple folders when opening a new workspace
2.  **Start using Cline** - Cline will automatically detect all your workspace folders and interact with them as needed.

For detailed instructions on setting up multi-root workspaces in VS Code, see [Microsoft’s official guide](https://code.visualstudio.com/docs/editing/workspaces/multi-root-workspaces).

### 

[​

](#how-cline-handles-multiple-workspaces)

How Cline Handles Multiple Workspaces

Once you have multiple folders, Cline automatically:

*   Detects all your workspace folders
*   Works with files across different projects
*   Executes commands in the right context
*   Handles path resolution intelligently

[​

](#working-across-workspaces)

Working Across Workspaces
--------------------------------------------------------------

### 

[​

](#let-cline-explore%2C-or-guide-it-precisely)

Let Cline explore, or guide it precisely

You can reference different workspaces naturally in your prompts:

Copy

Ask AI

    "Read the package.json in my frontend folder and compare it with the backend dependencies"
    

Copy

Ask AI

    "Create a shared utility function and update both the client and server to use it"
    

Copy

Ask AI

    "Search for TODO comments across all my workspace folders"
    

[​

](#common-use-cases)

Common Use Cases
--------------------------------------------

### 

[​

](#monorepo-development)

Monorepo Development

Perfect for when you have related projects in one repository:

Copy

Ask AI

    my-app.code-workspace
    ├── web/          (React frontend)
    ├── api/          (Node.js backend)
    ├── mobile/       (React Native)
    └── shared/       (Common utilities)
    

Ask Cline: _“Update the API endpoint in both web and mobile apps to match the new backend route”_

### 

[​

](#microservices-architecture)

Microservices Architecture

Manage multiple services from one workspace:

Copy

Ask AI

    services.code-workspace
    ├── user-service/
    ├── payment-service/  
    ├── notifications/
    └── infrastructure/
    

### 

[​

](#full-stack-development)

Full-Stack Development

Keep everything together while maintaining separation:

Copy

Ask AI

    fullstack.code-workspace
    ├── client/       (Frontend)
    ├── server/       (Backend API)
    ├── docs/         (Documentation)  
    └── deploy/       (Scripts & config)
    

### 

[​

](#auto-approve-integration)

Auto-Approve Integration

Multiroot workspaces work with [Auto Approve](/features/auto-approve):

*   Enable permissions for operations within workspace folders
*   Restrict auto-approve for files outside your workspace(s)
*   Configure different levels for different workspace folders

### 

[​

](#cross-workspace-operations)

Cross-Workspace Operations

Cline can complete tasks spanning multiple workspaces:

*   **Refactoring**: Update imports and references across projects
*   **Feature development**: Implement features requiring changes in multiple services
*   **Documentation**: Generate docs referencing code from multiple folders
*   **Testing**: Build & run tests across all workspaces and analyze results

When working with large multiroot workspaces, start in [Plan mode](/features/plan-and-act) to let Cline understand your project structure before making changes.

[​

](#best-practices)

Best Practices
----------------------------------------

### 

[​
