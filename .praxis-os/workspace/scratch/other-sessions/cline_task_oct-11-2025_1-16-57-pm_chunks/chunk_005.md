
](#organizing-your-workspaces)

Organizing Your Workspaces

1.  **Group related projects** that often need coordinated changes
2.  **Use consistent folder structures** across workspaces when possible
3.  **Name folders clearly** so Cline can understand your project structure

### 

[​

](#effective-prompting-%26-tips)

Effective Prompting & Tips

When working with multiroot workspaces, these approaches work best:

*   **Be specific** about which workspace when it matters: _“Update the user model in the backend workspace”_
*   **Reference relationships**: _“The frontend uses the API types from the shared workspace”_
*   **Describe cross-workspace operations**: _“This change needs to be reflected in both the web and mobile apps”_
*   **Scope your searches** when dealing with large codebases: _“Search for ‘TODO’ in just the frontend workspace”_
*   **Break down large tasks** into workspace-specific operations when possible
*   **Consider excluding large folders** like `node_modules` from your workspace search Scope

[

Focus Chain



](/features/focus-chain)[

Plan & Act



](/features/plan-and-act)

⌘I

Assistant

Responses are generated using AI and may contain mistakes.
<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:05:48 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
50,306 / 200K tokens used (25%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
You've identified a **fundamental architectural mismatch** between Agent OS and Cline's MCP system:

**The Problem:**
- **Agent OS**: Installs per-project in `.praxis-os/` (different path for each repo)
- **Cline MCP**: Uses global config with absolute paths (points to ONE location)

This means if you have Agent OS in multiple projects:
```
/path/to/project-a/.praxis-os/mcp_server  ← Can only configure ONE
/path/to/project-b/.praxis-os/mcp_server  ← of these at a time
/path/to/project-c/.praxis-os/mcp_server  ← in global Cline settings
```

**Why this is broken:**
- You'd need to **manually reconfigure** Cline's global MCP settings every time you switch projects
- Or only work on one Agent OS project at a time
- No way to have project-specific MCP servers with Cline's current design

**Possible Solutions:**

1. **Check if Cline supports workspace variables** (like `${workspaceFolder}`)
   - Unlikely, since it's global config
   - Would need to verify

2. **Create a workspace-aware wrapper script:**
   - Script detects current workspace
   - Launches correct `.praxis-os/mcp_server` for that workspace
   - Configure Cline to call the wrapper instead

3. **Install Agent OS globally** (defeats its portability)
   - Not recommended

4. **Use Cursor instead of Cline** for Agent OS
   - Cursor's `.cursor/mcp.json` supports `${workspaceFolder}` variable
   - Works per-workspace as designed

**The harsh reality:**
Agent OS's per-project design and Cline's global MCP config are incompatible architectures. Either Agent OS needs to work differently, or you need to use Cursor (which supports workspace-relative MCP configs) instead of Cline.

This is a design limitation, not a configuration problem.
</result>
<task_progress>
- [x] Identified architectural mismatch
- [x] Explained why per-project + global config don't work
- [x] Listed possible solutions
- [x] Recommended using Cursor instead of Cline for Agent OS
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
hmmm this is a pretty big issue, i am surprised this does not cause issues for cline users
</feedback>
<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:06:50 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
55,119 / 200K tokens used (28%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
You're absolutely right - this IS a significant issue, and it reveals a design assumption mismatch.

**Why most Cline users don't hit this:**

Most MCP servers are either:

1. **Global tools** - Filesystem access, web browsing, database queries
   - Same server works for any project
   - Global configuration makes sense

2. **Remote services** - Weather APIs, GitHub integration, etc.
   - Accessed via URL (SSE transport)
   - Not project-specific

**Agent OS is different:**
- **Project-specific context** (each project has its own standards/workflows)
- **Local STDIO** (not a remote service)
- **Per-project installation** (lives in `.praxis-os/`)

This combination is rare in the MCP ecosystem.

**Real-world impact:**

For developers using Agent OS across multiple projects, this means:
- Manual MCP config switching between projects
- OR only using Agent OS in one active project
- OR staying in Cursor where `${workspaceFolder}` works

**Potential solutions:**

1. **Wrapper script approach** (most practical):
   ```bash
   # ~/bin/agent-os-mcp-wrapper.sh
   # Detects current Cursor workspace and launches appropriate server
   ```
   Configure Cline to call this wrapper

2. **Document the limitation clearly** in Agent OS docs:
   - "Cline support requires manual configuration per project"
   - Recommend Cursor for Agent OS users

3. **Feature request to Cline** for workspace variable support in MCP configs

4. **Alternative Agent OS architecture** - Single global installation with workspace detection

This is a legitimate architectural gap between per-project tooling and global MCP configuration.
</result>
<task_progress>
- [x] Explained why this doesn't affect most Cline users
- [x] Identified Agent OS as edge case (project-specific local MCP)
- [x] Acknowledged this is a real limitation
- [x] Suggested practical workarounds
- [x] Recommended documenting this limitation
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
do some research on the web, is this a commonly reported issue for cline and mcp servers
</feedback>
<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:07:35 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
55,730 / 200K tokens used (28%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<web_fetch>
<url>https://github.com/cline/cline/issues?q=mcp+workspace</url>
<task_progress>
- [x] Understood the architectural issue
- [ ] Research if this is a known problem in Cline community
- [ ] Search GitHub issues for workspace MCP problems
- [ ] Check discussions about per-project MCP
- [ ] Report findings
</task_progress>
</web_fetch>

---

**User:**

[web_fetch for 'https://github.com/cline/cline/issues?q=mcp+workspace'] Result:
Fetched Markdown for https://github.com/cline/cline/issues?q=mcp+workspace:

                  Issues · cline/cline                                            

[Skip to content](#start-of-content) 

You signed in with another tab or window. Reload to refresh your session. You signed out in another tab or window. Reload to refresh your session. You switched accounts on another tab or window. Reload to refresh your session. Dismiss alert

[cline](/cline) / **[cline](/cline/cline)** Public

*   [Notifications](/login?return_to=%2Fcline%2Fcline) You must be signed in to change notification settings
*   [Fork 7.3k](/login?return_to=%2Fcline%2Fcline)
*   [Star 51.2k](/login?return_to=%2Fcline%2Fcline)
    

Issues
======

Search Issues

mcp workspace

mcp workspace

Clear filter

Search

[Labels](/cline/cline/labels)[Milestones](/cline/cline/milestones)[New issue](/login?return_to=https://github.com/cline/cline/issues?q=mcp+workspace)

Search results
--------------

*   [
    
    Open
    
    9 (9)](/cline/cline/issues?q=mcp%20workspace%20state%3Aopen)
*   [
    
    Closed
    
    40 (40)](/cline/cline/issues?q=mcp%20workspace%20state%3Aclosed)

Author

Labels

Projects

More Actions

*   ### [IntelliJ Cline plugin Agent's shell ENV vars can't execute commands when using a node version manager (Incorrect PATH for shell)](/cline/cline/issues/6388)
    
    [JetBrains](/cline/cline/issues?q=mcp%20workspace%20label%3AJetBrains)
    
    Status: Open.
    
    #6388 In cline/cline;
    
    · [ainsly](/cline/cline/issues?q=mcp%20workspace%20author%3Aainsly) opened on Sep 22, 2025
    

*   ### [MCP installed failed](/cline/cline/issues/6372)
    
    [JetBrains](/cline/cline/issues?q=mcp%20workspace%20label%3AJetBrains)
    
    Status: Open.
    
    #6372 In cline/cline;
    
    · [FineLu](/cline/cline/issues?q=mcp%20workspace%20author%3AFineLu) opened on Sep 21, 2025
    

*   ### [Changeset version bump](/cline/cline/pull/6238)
    
    Status: Merged (completed).
    
    cline/clinenumber 6238
    
    #6238 In cline/cline;
    
    · by [github-actions](/cline/cline/issues?q=mcp%20workspace%20author%3Aapp%2Fgithub-actions) was closed on Sep 17, 2025
    

*   ### [Changeset version bump](/cline/cline/pull/6224)
    
    Status: Merged (completed).
    
    cline/clinenumber 6224
    
    #6224 In cline/cline;
    
    · by [github-actions](/cline/cline/issues?q=mcp%20workspace%20author%3Aapp%2Fgithub-actions) was closed on Sep 15, 2025
    

*   ### [API requests are not being sent](/cline/cline/issues/5778)
    
    Status: Closed (completed).
    
    #5778 In cline/cline;
    
    · by [Rokurolize](/cline/cline/issues?q=mcp%20workspace%20author%3ARokurolize) was closed on Aug 25, 2025
    

*   ### [Local MCP servers unable to load project-specific .env files](/cline/cline/issues/5760)
    
    Status: Closed (completed).
    
    #5760 In cline/cline;
    
    · by [zcutlip](/cline/cline/issues?q=mcp%20workspace%20author%3Azcutlip) was closed on Aug 25, 2025
    

*   ### [template-based system prompt](/cline/cline/pull/5731)
    
    Status: Merged (completed).
    
    cline/clinenumber 5731
    
    #5731 In cline/cline;
    
    · by [abeatrix](/cline/cline/issues?q=mcp%20workspace%20author%3Aabeatrix) was closed on Aug 25, 2025
    

*   ### [Global Workflows configured correctly but fail to trigger](/cline/cline/issues/5062)
    
    [stale](/cline/cline/issues?q=mcp%20workspace%20label%3Astale)
    
    Status: Open.
    
    #5062 In cline/cline;
    
    · [yy1588133](/cline/cline/issues?q=mcp%20workspace%20author%3Ayy1588133) opened on Jul 20, 2025
    

*   ### [Feature Proposal: Support for Agent Rules Standard via AGENTS.md File](/cline/cline/issues/5033)
    
    [proposaldetailed feature proposal](/cline/cline/issues?q=mcp%20workspace%20label%3Aproposal)detailed feature proposal
    
    Status: Closed (completed).
    
    #5033 In cline/cline;
    
    · by [sgryphon](/cline/cline/issues?q=mcp%20workspace%20author%3Asgryphon) was closed on Jul 26, 2025
    

*   ### [Error generating TypeScript for proto files](/cline/cline/issues/4678)
    
    Status: Open.
    
    #4678 In cline/cline;
    
    · [Pinocchio2018](/cline/cline/issues?q=mcp%20workspace%20author%3APinocchio2018) opened on Jul 6, 2025
    

*   ### [Support Claude Code-style hooks](/cline/cline/issues/4658)
    
    [proposaldetailed feature proposal](/cline/cline/issues?q=mcp%20workspace%20label%3Aproposal)detailed feature proposal
    
    Status: Closed (completed).
    
    #4658 In cline/cline;
    
    · by [boxabirds](/cline/cline/issues?q=mcp%20workspace%20author%3Aboxabirds) was closed on Jul 26, 2025
    

*   ### [feat: configurable cline rules root path (#4561)](/cline/cline/pull/4563)
    
    Status: Open (in progress).
    
    cline/clinenumber 4563
    
    #4563 In cline/cline;
    
    · [toyamagu-2021](/cline/cline/issues?q=mcp%20workspace%20author%3Atoyamagu-2021) opened on Jun 29, 2025
    

*   ### [Fix MCP System Issues and Compatibility Problems](/cline/cline/issues/4391)
    
    Status: Open.
    
    #4391 In cline/cline;
    
    · [celestial-vault](/cline/cline/issues?q=mcp%20workspace%20author%3Acelestial-vault) opened on Jun 22, 2025
    

*   ### [Extension not working in Remote SSH environment](/cline/cline/issues/4352)
    
    Status: Open.
    
    #4352 In cline/cline;
    
    · [celestial-vault](/cline/cline/issues?q=mcp%20workspace%20author%3Acelestial-vault) opened on Jun 21, 2025
    

*   ### [Changeset version bump](/cline/cline/pull/4204)
    
    [size:MThis PR changes 30-99 lines, ignoring generated files.](/cline/cline/issues?q=mcp%20workspace%20label%3Asize%3AM)This PR changes 30-99 lines, ignoring generated files.
    
    Status: Merged (completed).
    
    cline/clinenumber 4204
    
    #4204 In cline/cline;
    
    · by [github-actions](/cline/cline/issues?q=mcp%20workspace%20author%3Aapp%2Fgithub-actions) was closed on Jun 17, 2025
    

*   ### [LS is moar](/cline/cline/pull/3883)
    
    Status: Merged (completed).
    
    cline/clinenumber 3883
    
    #3883 In cline/cline;
    
    · by [celestial-vault](/cline/cline/issues?q=mcp%20workspace%20author%3Acelestial-vault) was closed on May 28, 2025
    

*   ### [Terminal output capture failure in Cline v3.15.0/v3.15.1](/cline/cline/issues/3445)
    
    [Triaged](/cline/cline/issues?q=mcp%20workspace%20label%3ATriaged)
    
    Status: Closed (completed).
    
    #3445 In cline/cline;
    
    · by [zytbeyond](/cline/cline/issues?q=mcp%20workspace%20author%3Azytbeyond) was closed on Jun 21, 2025
    

*   ### [Background MCP servers not stopped when closing VSCode windows](/cline/cline/issues/3200)
    
    [Triaged](/cline/cline/issues?q=mcp%20workspace%20label%3ATriaged)
    
    Status: Closed (completed).
    
    #3200 In cline/cline;
    
    · by [jimcchi](/cline/cline/issues?q=mcp%20workspace%20author%3Ajimcchi) was closed on May 14, 2025
    

*   ### [MCP toggle state issue](/cline/cline/issues/3165)
    
    [Triaged](/cline/cline/issues?q=mcp%20workspace%20label%3ATriaged)
    
    Status: Closed (completed).
    
    #3165 In cline/cline;
    
    · by [pashpashpash](/cline/cline/issues?q=mcp%20workspace%20author%3Apashpashpash) was closed on Jun 22, 2025
    

*   ### [Can not connect/install mcp server context7 > spawn context7-mcp ENOENT spawn context7-mcp ENOENT](/cline/cline/issues/3135)
    
    Status: Closed (completed).
    
    #3135 In cline/cline;
    
    · by [1knueller](/cline/cline/issues?q=mcp%20workspace%20author%3A1knueller) was closed on Apr 26, 2025
    

*   ### [Changeset version bump](/cline/cline/pull/3131)
    
    Status: Merged (completed).
    
    cline/clinenumber 3131
    
    #3131 In cline/cline;
    
    · by [github-actions](/cline/cline/issues?q=mcp%20workspace%20author%3Aapp%2Fgithub-actions) was closed on May 2, 2025
    

*   ### [Cline doesn't follow symlinks in .clinerules files](/cline/cline/issues/3092)
    
    Status: Duplicate of an existing item.
    
    #3092 In cline/cline;
    
    · by [dvcrn](/cline/cline/issues?q=mcp%20workspace%20author%3Advcrn) was closed on Jul 3, 2025
    
    · Duplicate
    

*   ### [What's yer path?](/cline/cline/pull/3047)
    
    Status: Merged (completed).
    
    cline/clinenumber 3047
    
    #3047 In cline/cline;
    
    · by [celestial-vault](/cline/cline/issues?q=mcp%20workspace%20author%3Acelestial-vault) was closed on Apr 21, 2025
    

*   ### [not detecting playwright mcp server using ollama local model on windows](/cline/cline/issues/3025)
    
    Status: Closed (completed).
    
    #3025 In cline/cline;
    
    · by [OhBobb](/cline/cline/issues?q=mcp%20workspace%20author%3AOhBobb) was closed on Jun 22, 2025
    

*   ### [Fix: Expand ${workspaceFolder} for MCP stdio transport cwd/env](/cline/cline/pull/2991)
    
    Status: Open (in progress).
    
    cline/clinenumber 2991
    
    #2991 In cline/cline;
    
    · [narunbabu](/cline/cline/issues?q=mcp%20workspace%20author%3Anarunbabu) opened on Apr 19, 2025
    

You can’t perform that action at this time.

Issues · cline/cline

49 results
<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:07:45 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
55,911 / 200K tokens used (28%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

Excellent find! There's an open PR addressing this exact issue. Let me get more details:

<web_fetch>
<url>https://github.com/cline/cline/pull/2991</url>
<task_progress>
- [x] Found workspace MCP is a known issue
- [ ] Get details on the PR fixing ${workspaceFolder} support
- [ ] Understand current status and timeline
- [ ] Report comprehensive findings
</task_progress>
</web_fetch>

---

**User:**

[web_fetch for 'https://github.com/cline/cline/pull/2991'] Result:
Fetched Markdown for https://github.com/cline/cline/pull/2991:

                 Fix: Expand ${workspaceFolder} for MCP stdio transport cwd/env by narunbabu · Pull Request #2991 · cline/cline · GitHub                                            

[Skip to content](#start-of-content) 

You signed in with another tab or window. Reload to refresh your session. You signed out in another tab or window. Reload to refresh your session. You switched accounts on another tab or window. Reload to refresh your session. Dismiss alert

[cline](/cline) / **[cline](/cline/cline)** Public

*   [Notifications](/login?return_to=%2Fcline%2Fcline) You must be signed in to change notification settings
*   [Fork 7.3k](/login?return_to=%2Fcline%2Fcline)
*   [Star 51.2k](/login?return_to=%2Fcline%2Fcline)
    

Fix: Expand ${workspaceFolder} for MCP stdio transport cwd/env #2991
====================================================================

New issue

**Have a question about this project?** Sign up for a free GitHub account to open an issue and contact its maintainers and the community.

[Sign up for GitHub](/signup?return_to=%2Fcline%2Fcline%2Fissues%2Fnew%2Fchoose)

By clicking “Sign up for GitHub”, you agree to our [terms of service](https://docs.github.com/terms) and [privacy statement](https://docs.github.com/privacy). We’ll occasionally send you account related emails.

Already on GitHub? [Sign in](/login?return_to=%2Fcline%2Fcline%2Fissues%2Fnew%2Fchoose) to your account

[Jump to bottom](#issue-comment-box)

Open

[narunbabu](/narunbabu) wants to merge 2 commits into [cline:main](/cline/cline/tree/main "cline/cline:main")

_base:_ main

Branches Tags

Loading

Loading

 

from [narunbabu:fix-mcp-workspacefolder](/narunbabu/cline/tree/fix-mcp-workspacefolder "narunbabu/cline:fix-mcp-workspacefolder")

Open

[Fix: Expand ${workspaceFolder} for MCP stdio transport cwd/env](#top) #2991
============================================================================

[narunbabu](/narunbabu) wants to merge 2 commits into [cline:main](/cline/cline/tree/main "cline/cline:main") from [narunbabu:fix-mcp-workspacefolder](/narunbabu/cline/tree/fix-mcp-workspacefolder "narunbabu/cline:fix-mcp-workspacefolder")

+14 −5

Conversation
------------

[![narunbabu](https://avatars.githubusercontent.com/u/18241463?s=80&v=4)](/narunbabu)

Copy link

### 

![@narunbabu](https://avatars.githubusercontent.com/u/18241463?s=48&v=4) **[narunbabu](/narunbabu)** commented [Apr 19, 2025](#issue-3006471931) •

edited by ellipsis-dev bot

Loading

### Uh oh!

There was an error while loading. Please reload this page.

### Description

This PR addresses an issue where the `${workspaceFolder}` variable was not being expanded when used in the `cwd` (current working directory) or `env` (environment variables) fields for MCP servers configured with the `stdio` transport type.

**Problem:**

*   Servers launched via Cline would start in an incorrect directory (e.g., the VS Code installation directory) instead of the intended project workspace root specified by `${workspaceFolder}` in the `cwd` setting.
*   Environment variables defined using `${workspaceFolder}` (e.g., `PROJECT_ROOT`) would contain the literal string `${workspaceFolder}` instead of the resolved path.
*   This prevented servers from correctly resolving relative file paths based on the active workspace, leading to errors when accessing project files or writing output.

**Cause:**

The logic within `src/services/mcp/McpHub.ts` for initializing the `@modelcontextprotocol/sdk/client/stdio.js` `StdioClientTransport` did not include logic to explicitly expand the `${workspaceFolder}` variable for the `cwd` and `env` configuration options (as well as `command` and `args`) before spawning the server process.

**Solution:**

This PR modifies the `connectToServer` method in `src/services/mcp/McpHub.ts` to:

1.  Reliably determine the `workspaceRoot` path using the `vscode.workspace.workspaceFolders` API.
2.  Implement an `expand` function that replaces occurrences of the literal string `${workspaceFolder}` with the actual `workspaceRoot` path.
3.  Apply this `expand` function to the `command`, `args`, `env` values, and the `cwd` value obtained from the server configuration _before_ constructing the `StdioClientTransport`.
4.  Provide a fallback for `cwd` to default to the determined `workspaceRoot` if `cwd` is not explicitly set in the server configuration.

This ensures that the server process is launched with the correct working directory and properly resolved environment variable paths when `${workspaceFolder}` is used in the configuration.

### Test Procedure

1.  Configured an MCP server (e.g., `FileDump`) using the `stdio` transport in settings (e.g., `cline_mcp_settings.json` or workspace `.vscode/settings.json`).
2.  Set `"cwd": "${workspaceFolder}"` in the server configuration.
3.  Set `"env": { "PROJECT_ROOT": "${workspaceFolder}" }` in the server configuration.
4.  Added debug logging at the start of the target server script (e.g., in Python using `os.getcwd()` and `os.getenv('PROJECT_ROOT')`) to print the CWD and relevant environment variable on startup.
5.  Launched VS Code in a specific project workspace.
6.  Started the configured MCP server via the Cline interface.
7.  **Verified:** Checked the MCP server's output logs. Confirmed that the logged `cwd` and the value of the `PROJECT_ROOT` environment variable correctly reflected the actual workspace path, not the VS Code installation directory or the literal string `${workspaceFolder}`.
8.  **Verified:** Confirmed that tool calls involving relative paths now correctly resolved paths relative to the workspace root.

### Type of Change

*    Bug fix (non-breaking change which fixes an issue)
*    New feature (non-breaking change which adds functionality)
*    Breaking change (fix or feature that would cause existing functionality to not work as expected)
*    Documentation update
*    Other (please describe):

* * *

Important

Fixes `${workspaceFolder}` expansion issue in MCP stdio transport configurations in `McpHub.ts`.

*   **Behavior**:
    *   Fixes issue where `${workspaceFolder}` was not expanded in `cwd` and `env` for MCP servers using `stdio` transport in `McpHub.ts`.
    *   Adds fallback for `cwd` to default to `workspaceRoot` if not set.
*   **Implementation**:
    *   Adds `expand` function in `connectToServer` to replace `${workspaceFolder}` with actual path.
    *   Applies `expand` to `command`, `args`, `env`, and `cwd` before constructing `StdioClientTransport`.
*   **Misc**:
    *   Updates version to `3.13.1` in `package.json`.
    *   Updates `CHANGELOG.md` for version `3.13.1`.

This description was created by [![Ellipsis](https://camo.githubusercontent.com/34bf9170ce9970063622a6598321f3ac85ed9e532670205236a10469e231eb1d/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f456c6c69707369732d626c75653f636f6c6f723d313735313733)](https://www.ellipsis.dev?ref=cline%2Fcline&utm_source=github&utm_medium=referral) for [907a43e](https://github.com/cline/cline/commit/907a43ebfd82fdf68bd9d27b954d6120257f1a14). You can [customize](https://app.ellipsis.dev/cline/settings/summaries) this summary. It will automatically update as commits are pushed.

Sorry, something went wrong.

### Uh oh!

There was an error while loading. Please reload this page.

 

🚀 2 ellipsis-dev\[bot\] and oomathias reacted with rocket emoji

All reactions

*   🚀 2 reactions

 [![@saoudrizwan](https://avatars.githubusercontent.com/u/7799382?s=40&v=4)](/saoudrizwan)[![@narunbabu](https://avatars.githubusercontent.com/u/18241463?s=40&v=4)](/narunbabu)

`[Prepare for release](/cline/cline/pull/2991/commits/907a43ebfd82fdf68bd9d27b954d6120257f1a14 "Prepare for release")`

Loading

Loading status checks…

### Uh oh!

There was an error while loading. Please reload this page.

`[907a43e](/cline/cline/pull/2991/commits/907a43ebfd82fdf68bd9d27b954d6120257f1a14)`

[![@narunbabu](https://avatars.githubusercontent.com/u/18241463?s=40&u=5f64eae5a9182613dfc1b12763fc62b04cce2604&v=4)](/narunbabu) [narunbabu](/narunbabu) requested review from [NightTrek](/NightTrek), [dcbartlett](/dcbartlett), [ocasta181](/ocasta181), [pashpashpash](/pashpashpash), [saito-sv](/saito-sv) and [saoudrizwan](/saoudrizwan) as [code owners](/cline/cline/blob/ba6dcb5bc9f785667753a5e6c3ace75001be353e/.github/CODEOWNERS#L1) [April 19, 2025 14:44](#event-17328814633)

[![@changeset-bot](https://avatars.githubusercontent.com/in/28616?s=80&v=4)](/apps/changeset-bot) [![changeset-bot](https://avatars.githubusercontent.com/in/28616?s=40&u=dfac8d20bd8180eee325b15beb2569b9b6ae4846&v=4)](https://github.com/apps/changeset-bot)

Copy link

### 

**[changeset-bot](/apps/changeset-bot) bot** commented [Apr 19, 2025](#issuecomment-2816735235) •

edited

Loading

### Uh oh!

There was an error while loading. Please reload this page.

### ⚠️ No Changeset found

Latest commit: [73d2b8f](https://github.com/cline/cline/commit/73d2b8f5a2b67d0287909cd2d8fba10a5d1265b4)

Merging this PR will not cause a version bump for any packages. If these changes should not result in a new version, you're good to go. **If these changes should result in a version bump, you need to add a changeset.**

This PR includes no changesets

When changesets are added to this PR, you'll see the packages that this PR includes changesets for and the associated semver types

[Click here to learn what changesets are, and how to add one](https://github.com/changesets/changesets/blob/main/docs/adding-a-changeset.md).

[Click here if you're a maintainer who wants to add a changeset to this PR](https://github.com/narunbabu/cline/new/fix-mcp-workspacefolder?filename=.changeset/pink-balloons-kiss.md&value=---%0A%22claude-dev%22%3A%20patch%0A---%0A%0AFix%3A%20Expand%20%24%7BworkspaceFolder%7D%20for%20MCP%20stdio%20transport%20cwd%2Fenv%0A)

  

All reactions

Sorry, something went wrong.

### Uh oh!

There was an error while loading. Please reload this page.

[![ellipsis-dev[bot]](https://avatars.githubusercontent.com/in/64358?s=60&v=4)](/apps/ellipsis-dev)

**[ellipsis-dev](/apps/ellipsis-dev) bot** reviewed [Apr 19, 2025](#pullrequestreview-2779985063)

[View reviewed changes](/cline/cline/pull/2991/files/907a43ebfd82fdf68bd9d27b954d6120257f1a14)

Copy link

Contributor

### 

![@ellipsis-dev](https://avatars.githubusercontent.com/in/64358?s=48&v=4) **[ellipsis-dev](/apps/ellipsis-dev) bot** left a comment

[](#pullrequestreview-2779985063)

There was a problem hiding this comment.

### Choose a reason for hiding this comment

The reason will be displayed to describe this comment to others. [Learn more](https://docs.github.com/articles/managing-disruptive-comments/#hiding-a-comment).

 Choose a reason Spam Abuse Off Topic Outdated Duplicate Resolved Hide comment

👍 Looks good to me! Reviewed everything up to [907a43e](https://github.com/cline/cline/commit/907a43ebfd82fdf68bd9d27b954d6120257f1a14) in 2 minutes and 0 seconds

More details

*   Looked at `94` lines of code in `4` files
*   Skipped `0` files when reviewing.
*   Skipped posting `9` drafted comments based on config settings.

1\. `src/services/mcp/McpHub.ts:209`

*   **Draft comment:**  
    Consider handling scenarios with multiple workspace folders rather than always using the first. If a workspace has multiple folders, the intended expansion might differ.
*   **Reason this comment was not posted:**  
    Decided after close inspection that this draft comment was likely wrong and/or not actionable: usefulness confidence = 20% vs. threshold = 50%  
    While the comment raises a valid theoretical concern about multiple workspaces, it's speculative ("might differ") and doesn't provide a clear action item. The current implementation provides a reasonable default behavior by using the first workspace or cwd. Supporting multiple workspaces would add significant complexity without clear benefit.  
    The comment does identify a real edge case that could affect some users who have multiple workspace folders. Not handling this could cause confusion.  
    While true, the comment is speculative and doesn't provide clear guidance on what should be done. The current behavior is reasonable and documented through the code.  
    Delete the comment. It raises a speculative concern without providing clear actionable guidance, and the current behavior is a reasonable default.

2\. `src/services/mcp/McpHub.ts:210`

*   **Draft comment:**  
    Extract the `${workspaceFolder}` expansion logic into a separate utility function for reuse and improved readability.
*   **Reason this comment was not posted:**  
    Decided after close inspection that this draft comment was likely wrong and/or not actionable: usefulness confidence = 20% vs. threshold = 50%  
    While the expansion logic is used multiple times, it's all within a very localized block of code (5 lines). The logic is simple and clear. Moving it to a utility function would add indirection and cognitive overhead of having to look up the function definition elsewhere. The current inline approach keeps related code together and is more readable. The suggestion seems like over-engineering for this simple case.  
    I could be undervaluing the benefits of DRY (Don't Repeat Yourself) principles. If this expansion logic needs to be modified in the future, having it in one place would be beneficial.  
    The expansion logic is extremely unlikely to change - it's a simple string replacement tied to VSCode's ${workspaceFolder} variable syntax. Even if it did need to change, the changes would be trivial to make in these 4 adjacent lines. The cognitive cost of extracting this exceeds the minimal maintenance benefit.  
    The comment should be deleted. The suggested refactoring would add unnecessary complexity without meaningful benefits, given the simplicity and locality of the current code.

3\. `src/services/mcp/McpHub.ts:267`

*   **Draft comment:**  
    The regex for detecting informational logs (`/^\s*INFO\b/`) now only catches lines beginning with 'INFO'. Confirm that this behavior fits with all expected output formats.
*   **Reason this comment was not posted:**  
    Confidence changes required: `50%` <= threshold `50%`  
    None

4\. `CHANGELOG.md:3`

*   **Draft comment:**  
    The changelog entry for version 3.13.1 refers to a task cancellation bug, which doesn't match the PR title and description (workspaceFolder expansion). Please update the changelog entry to reflect the changes made.
*   **Reason this comment was not posted:**  
    Comment did not seem useful. Confidence is useful = `0%` <= threshold `50%`  
    The comment is asking the PR author to update the changelog entry to match the PR title and description. This is similar to asking the author to update the PR description, which is against the rules. The comment does not provide a specific code suggestion or ask for a test to be written, so it should be removed.

5\. `package.json:5`

*   **Draft comment:**  
    Version bumped to 3.13.1. Ensure that the version and associated changelog entries accurately reflect all changes in this release.
*   **Reason this comment was not posted:**  
    Confidence changes required: `0%` <= threshold `50%`  
    None

6\. `src/services/mcp/McpHub.ts:64`

*   **Draft comment:**  
    The optional 'cwd' field has been added in the StdioConfigSchema. This is a good addition to allow explicit current working directory configuration. Consider adding inline comments to document its expected format or behavior.
*   **Reason this comment was not posted:**  
    Confidence changes required: `0%` <= threshold `50%`  
    None

7\. `src/services/mcp/McpHub.ts:208`

*   **Draft comment:**  
    The new workspaceFolder expansion logic is implemented by defining an 'expand' function applied to command, args, env, and cwd. This solution seems robust. Consider adding unit tests for different workspace configurations to ensure correctness.
*   **Reason this comment was not posted:**  
    Confidence changes required: `0%` <= threshold `50%`  
    None

8\. `src/services/mcp/McpHub.ts:266`

*   **Draft comment:**  
    The regex for classifying logs has been updated to use `/^\s*INFO\b/` instead of checking for absence of 'error'. This change is more deterministic for identifying info logs. Verify that this new pattern covers all expected log formats.
*   **Reason this comment was not posted:**  
    Confidence changes required: `0%` <= threshold `50%`  
    None

9\. `CHANGELOG.md:5`

*   **Draft comment:**  
    The sentence '- Fix bug where task cancellation during thinking stream would result in error state' might be clearer if it said '... would result in an error state', adding the article 'an'. This is a minor typographical/grammatical adjustment.
*   **Reason this comment was not posted:**  
    Decided after close inspection that this draft comment was likely wrong and/or not actionable: usefulness confidence = 10% vs. threshold = 50%  
    This is a very minor grammatical suggestion. While technically correct English would use 'an' before 'error state', changelog entries often use a more terse style where articles are sometimes omitted. The meaning is perfectly clear without the article. This seems like an unnecessary nitpick that doesn't improve understanding or clarity significantly.  
    The comment is technically correct English grammar. Some could argue that maintaining proper grammar in documentation is important for professionalism.  
    While proper grammar is good, changelog entries commonly use a more concise style. The meaning is clear either way, and this level of grammatical nitpicking creates noise without adding value.  
    Delete this comment as it's an overly pedantic grammatical suggestion that doesn't meaningfully improve the changelog entry.

Workflow ID: `wflow_l745zzeyuOBsBkaw`

* * *

You can teach Ellipsis what to look for with 👍 / 👎 [feedback](https://docs.ellipsis.dev/features/code-review#teaching-ellipsis), review rules, user-specific overrides, `quiet` mode, and [more](https://docs.ellipsis.dev/config).

Sorry, something went wrong.

### Uh oh!

There was an error while loading. Please reload this page.

 

All reactions

[![@narunbabu](https://avatars.githubusercontent.com/u/18241463?s=40&v=4)](/narunbabu)

`[Merge branch 'cline:main' into fix-mcp-workspacefolder](/cline/cline/pull/2991/commits/73d2b8f5a2b67d0287909cd2d8fba10a5d1265b4 "Merge branch 'cline:main' into fix-mcp-workspacefolder")`

Verified

Verified
========

This commit was created on GitHub.com and signed with GitHub’s **verified signature**.

GPG key ID: B5690EEEBB952194

Verified

[Learn about vigilant mode](https://docs.github.com/github/authenticating-to-github/displaying-verification-statuses-for-all-of-your-commits)

Loading

Loading status checks…

### Uh oh!

There was an error while loading. Please reload this page.

`[73d2b8f](/cline/cline/pull/2991/commits/73d2b8f5a2b67d0287909cd2d8fba10a5d1265b4)`

[![@dcbartlett](https://avatars.githubusercontent.com/u/1077050?s=40&u=6e63d955a89098e236a30ea67aab8e2277a40a81&v=4)](/dcbartlett) [dcbartlett](/dcbartlett) requested a review from [Garoth](/Garoth) as a [code owner](/cline/cline/blob/29bdb6c9814c412fde0d6f0c9a76bc3861165be7/.github/CODEOWNERS#L1) [April 24, 2025 07:47](#event-17385132379)

[![@dcbartlett](https://avatars.githubusercontent.com/u/1077050?s=40&u=6e63d955a89098e236a30ea67aab8e2277a40a81&v=4)](/dcbartlett) [dcbartlett](/dcbartlett) [force-pushed](/cline/cline/compare/0cefc0e23662069a784ff7e43e0a5603ddc6820d..c040be9eb10c4bbf5ff6ba4f91b92aa16119d226) the main branch 12 times, most recently from [`0cefc0e`](/cline/cline/commit/0cefc0e23662069a784ff7e43e0a5603ddc6820d) to [`c040be9`](/cline/cline/commit/c040be9eb10c4bbf5ff6ba4f91b92aa16119d226) [Compare](/cline/cline/compare/0cefc0e23662069a784ff7e43e0a5603ddc6820d..c040be9eb10c4bbf5ff6ba4f91b92aa16119d226) [May 7, 2025 20:56](#event-17563395108)

[![@dcbartlett](https://avatars.githubusercontent.com/u/1077050?s=40&u=6e63d955a89098e236a30ea67aab8e2277a40a81&v=4)](/dcbartlett) [dcbartlett](/dcbartlett) [force-pushed](/cline/cline/compare/533620b451255a38678980d4e5559304aeb778b4..a22fc10a722ecd0ec95a9856c6f0774e5263dde6) the main branch from [`533620b`](/cline/cline/commit/533620b451255a38678980d4e5559304aeb778b4) to [`a22fc10`](/cline/cline/commit/a22fc10a722ecd0ec95a9856c6f0774e5263dde6) [Compare](/cline/cline/compare/533620b451255a38678980d4e5559304aeb778b4..a22fc10a722ecd0ec95a9856c6f0774e5263dde6) [May 22, 2025 18:02](#event-17777344965)

[![@andrew-martin-ck](https://avatars.githubusercontent.com/u/51206931?s=80&v=4)](/andrew-martin-ck)

Copy link

### 

**[andrew-martin-ck](/andrew-martin-ck)** commented [May 27, 2025](#issuecomment-2913473734)

Hi there, curious if this one will be merged anytime soon? I'm fairly certain this will solve an issue I'm encountering and seems really useful.

  

All reactions

Sorry, something went wrong.
