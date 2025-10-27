# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/11/2025, 6:40:54 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
105,942 / 200K tokens used (53%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<read_file>
<path>mcp_server/requirements.txt</path>
<task_progress>
- [x] Recognized I should have researched first
- [ ] Find FastMCP version being used
- [ ] Research FastMCP actual transport capabilities
- [ ] Provide accurate implementation based on real capabilities
</task_progress>
</read_file>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[read_file for 'mcp_server/requirements.txt'] Result:
# prAxIs OS MCP/RAG Server Dependencies
# 100% AI-authored via human orchestration

# Vector database for RAG (switched from ChromaDB to LanceDB for better filtering)
# Locked to 0.25.x series for stability (latest stable as of Oct 2025)
lancedb~=0.25.0

# Model Context Protocol
mcp>=1.0.0
fastmcp>=0.2.0

# Local embeddings (default, free, offline)
sentence-transformers>=2.0.0

# File watching for automatic index rebuild
watchdog>=3.0.0

# Markdown AST parsing for dynamic workflow content
mistletoe>=1.4.0

# Browser automation (Phase 2 feature)
playwright>=1.40.0

# Optional: OpenAI embeddings for higher quality (~3-5% better)
# openai>=1.0.0


<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/11/2025, 6:41:01 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
106,047 / 200K tokens used (53%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<search_files>
<path>mcp_server</path>
<regex>from fastmcp import|FastMCP\(</regex>
<task_progress>
- [x] Found fastmcp>=0.2.0 dependency
- [ ] Search for FastMCP usage patterns in codebase
- [ ] Understand actual FastMCP capabilities
- [ ] Provide accurate implementation
</task_progress>
</search_files>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[search_files for 'from fastmcp import|FastMCP\('] Result:
Found 2 results.

mcp_server/server/factory.py
│----
│from fastmcp import FastMCP
│from watchdog.observers import Observer
│        # Create FastMCP instance
│----
│        mcp = FastMCP("agent-os-rag")
│
│----
<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/11/2025, 6:41:08 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
106,566 / 200K tokens used (53%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<web_fetch>
<url>https://github.com/jlowin/fastmcp</url>
<task_progress>
- [x] Found FastMCP usage in codebase
- [ ] Fetch FastMCP documentation/README
- [ ] Understand actual transport capabilities
- [ ] Provide accurate implementation
</task_progress>
</web_fetch>

---

**User:**

[web_fetch for 'https://github.com/jlowin/fastmcp'] Result:
Fetched Markdown for https://github.com/jlowin/fastmcp:

                  GitHub - jlowin/fastmcp: 🚀 The fast, Pythonic way to build MCP servers and clients                                             

[Skip to content](#start-of-content) 

You signed in with another tab or window. Reload to refresh your session. You signed out in another tab or window. Reload to refresh your session. You switched accounts on another tab or window. Reload to refresh your session. Dismiss alert

[jlowin](/jlowin) / **[fastmcp](/jlowin/fastmcp)** Public

*   [Notifications](/login?return_to=%2Fjlowin%2Ffastmcp) You must be signed in to change notification settings
*   [Fork 1.4k](/login?return_to=%2Fjlowin%2Ffastmcp)
*   [Star 18.9k](/login?return_to=%2Fjlowin%2Ffastmcp)
    

🚀 The fast, Pythonic way to build MCP servers and clients

[gofastmcp.com](https://gofastmcp.com "https://gofastmcp.com")

### License

[Apache-2.0 license](/jlowin/fastmcp/blob/main/LICENSE)

[18.9k stars](/jlowin/fastmcp/stargazers) [1.4k forks](/jlowin/fastmcp/forks) [Branches](/jlowin/fastmcp/branches) [Tags](/jlowin/fastmcp/tags) [Activity](/jlowin/fastmcp/activity)

[Star](/login?return_to=%2Fjlowin%2Ffastmcp)

[Notifications](/login?return_to=%2Fjlowin%2Ffastmcp) You must be signed in to change notification settings

jlowin/fastmcp
==============

 main

[**47** Branches](/jlowin/fastmcp/branches)[**64** Tags](/jlowin/fastmcp/tags)

[](/jlowin/fastmcp/branches)[](/jlowin/fastmcp/tags)

Go to file

Code

Open more actions menu

Folders and files
-----------------

Name

Name

Last commit message

Last commit date

Latest commit
-------------

[![Anurag-gg](https://avatars.githubusercontent.com/u/86948851?v=4&size=40)](/Anurag-gg)[Anurag-gg](/jlowin/fastmcp/commits?author=Anurag-gg)

[fixed a comment in File class (](/jlowin/fastmcp/commit/72b27a284a7b8349676dcd0fd7032d13ac399959)[#2066](https://github.com/jlowin/fastmcp/pull/2066)[)](/jlowin/fastmcp/commit/72b27a284a7b8349676dcd0fd7032d13ac399959)

success

Oct 11, 2025

[72b27a2](/jlowin/fastmcp/commit/72b27a284a7b8349676dcd0fd7032d13ac399959) · Oct 11, 2025

History
-------

[2,245 Commits](/jlowin/fastmcp/commits/main/)

Open commit details

[](/jlowin/fastmcp/commits/main/)

[.cursor/rules](/jlowin/fastmcp/tree/main/.cursor/rules "This path skips through empty directories")

[.cursor/rules](/jlowin/fastmcp/tree/main/.cursor/rules "This path skips through empty directories")

[Add tags, improve duplicate import behavior](/jlowin/fastmcp/commit/f0d07e5f04118d0699755742baaff0616cf50e89 "Add tags, improve duplicate import behavior")

Apr 12, 2025

[.github](/jlowin/fastmcp/tree/main/.github ".github")

[.github](/jlowin/fastmcp/tree/main/.github ".github")

[Fixes for Martian prompts](/jlowin/fastmcp/commit/defa67f8a9d420bbbd5d1c65a8c091002b29e22b "Fixes for Martian prompts")

Oct 3, 2025

[docs](/jlowin/fastmcp/tree/main/docs "docs")

[docs](/jlowin/fastmcp/tree/main/docs "docs")

[fix: wrong server name in explicit server entrypoint doc](/jlowin/fastmcp/commit/c8603bfd3b9c89e8161a7db022a09eca3c2a8c29 "fix: wrong server name in explicit server entrypoint doc")

Oct 9, 2025

[examples](/jlowin/fastmcp/tree/main/examples "examples")

[examples](/jlowin/fastmcp/tree/main/examples "examples")

[Internal refactor of MCP handlers (](/jlowin/fastmcp/commit/91af3cd2aec9cdbb9d41db9f469b5d5f7f08972e "Internal refactor of MCP handlers (#2005)")[#2005](https://github.com/jlowin/fastmcp/pull/2005)[)](/jlowin/fastmcp/commit/91af3cd2aec9cdbb9d41db9f469b5d5f7f08972e "Internal refactor of MCP handlers (#2005)")

Oct 5, 2025

[scripts](/jlowin/fastmcp/tree/main/scripts "scripts")

[scripts](/jlowin/fastmcp/tree/main/scripts "scripts")

[Update dedupe logic (](/jlowin/fastmcp/commit/26a2c2ed622ac8ac90387718f92b629feb8d076b "Update dedupe logic (#1460)")[#1460](https://github.com/jlowin/fastmcp/pull/1460)[)](/jlowin/fastmcp/commit/26a2c2ed622ac8ac90387718f92b629feb8d076b "Update dedupe logic (#1460)")

Aug 11, 2025

[src/fastmcp](/jlowin/fastmcp/tree/main/src/fastmcp "This path skips through empty directories")

[src/fastmcp](/jlowin/fastmcp/tree/main/src/fastmcp "This path skips through empty directories")

[fixed a comment in File class (](/jlowin/fastmcp/commit/72b27a284a7b8349676dcd0fd7032d13ac399959 "fixed a comment in File class (#2066)")[#2066](https://github.com/jlowin/fastmcp/pull/2066)[)](/jlowin/fastmcp/commit/72b27a284a7b8349676dcd0fd7032d13ac399959 "fixed a comment in File class (#2066)")

Oct 11, 2025

[tests](/jlowin/fastmcp/tree/main/tests "tests")

[tests](/jlowin/fastmcp/tree/main/tests "tests")

[Merge branch 'main' into switch-kvstore](/jlowin/fastmcp/commit/93c41e815cb5e693d0bad553ca7a167a87c12a7d "Merge branch 'main' into switch-kvstore")

Oct 9, 2025

[.ccignore](/jlowin/fastmcp/blob/main/.ccignore ".ccignore")

[.ccignore](/jlowin/fastmcp/blob/main/.ccignore ".ccignore")

[Update .ccignore](/jlowin/fastmcp/commit/e334d80c25e31538f005a625a7b07f9141c8c85a "Update .ccignore")

Jun 30, 2025

[.gitignore](/jlowin/fastmcp/blob/main/.gitignore ".gitignore")

[.gitignore](/jlowin/fastmcp/blob/main/.gitignore ".gitignore")

[Implement typed source system for FastMCP configuration (](/jlowin/fastmcp/commit/1f3f82d245f97632b9bd9ccb63746acad9c87f71 "Implement typed source system for FastMCP configuration (#1607)")[#1607](https://github.com/jlowin/fastmcp/pull/1607)[)](/jlowin/fastmcp/commit/1f3f82d245f97632b9bd9ccb63746acad9c87f71 "Implement typed source system for FastMCP configuration (#1607)")

Aug 24, 2025

[.pre-commit-config.yaml](/jlowin/fastmcp/blob/main/.pre-commit-config.yaml ".pre-commit-config.yaml")

[.pre-commit-config.yaml](/jlowin/fastmcp/blob/main/.pre-commit-config.yaml ".pre-commit-config.yaml")

[Fix typos discovered by codespell (](/jlowin/fastmcp/commit/d6aa980ff5be59579978cfeeaabc0a135eb26dd9 "Fix typos discovered by codespell (#1922)")[#1922](https://github.com/jlowin/fastmcp/pull/1922)[)](/jlowin/fastmcp/commit/d6aa980ff5be59579978cfeeaabc0a135eb26dd9 "Fix typos discovered by codespell (#1922)")

Sep 26, 2025

[.python-version](/jlowin/fastmcp/blob/main/.python-version ".python-version")

[.python-version](/jlowin/fastmcp/blob/main/.python-version ".python-version")

[Initial commit](/jlowin/fastmcp/commit/b6ade5e72cd9c56317ad96546d59074bd45aede7 "Initial commit")

Nov 29, 2024

[AGENTS.md](/jlowin/fastmcp/blob/main/AGENTS.md "AGENTS.md")

[AGENTS.md](/jlowin/fastmcp/blob/main/AGENTS.md "AGENTS.md")

[Add log level support for stdio and HTTP transports (](/jlowin/fastmcp/commit/d4cc1fbf10a1ecf532beb2530c6ba4edcaac4d6a "Add log level support for stdio and HTTP transports (#1840)")[#1840](https://github.com/jlowin/fastmcp/pull/1840)[)](/jlowin/fastmcp/commit/d4cc1fbf10a1ecf532beb2530c6ba4edcaac4d6a "Add log level support for stdio and HTTP transports (#1840)")

Sep 19, 2025

[CLAUDE.md](/jlowin/fastmcp/blob/main/CLAUDE.md "CLAUDE.md")

[CLAUDE.md](/jlowin/fastmcp/blob/main/CLAUDE.md "CLAUDE.md")

[Consolidate agent instructions into AGENTS.md (](/jlowin/fastmcp/commit/bfc8efdf31c31f9cc0524d07d0fbc28157c9cc79 "Consolidate agent instructions into AGENTS.md (#1404)")[#1404](https://github.com/jlowin/fastmcp/pull/1404)[)](/jlowin/fastmcp/commit/bfc8efdf31c31f9cc0524d07d0fbc28157c9cc79 "Consolidate agent instructions into AGENTS.md (#1404)")

Aug 8, 2025

[CODE\_OF\_CONDUCT.md](/jlowin/fastmcp/blob/main/CODE_OF_CONDUCT.md "CODE_OF_CONDUCT.md")

[CODE\_OF\_CONDUCT.md](/jlowin/fastmcp/blob/main/CODE_OF_CONDUCT.md "CODE_OF_CONDUCT.md")

[Create CODE\_OF\_CONDUCT.md (](/jlowin/fastmcp/commit/2662deb067fb037615ec795b288eb8807253d740 "Create CODE_OF_CONDUCT.md (#1523)")[#1523](https://github.com/jlowin/fastmcp/pull/1523)[)](/jlowin/fastmcp/commit/2662deb067fb037615ec795b288eb8807253d740 "Create CODE_OF_CONDUCT.md (#1523)")

Aug 16, 2025

[LICENSE](/jlowin/fastmcp/blob/main/LICENSE "LICENSE")

[LICENSE](/jlowin/fastmcp/blob/main/LICENSE "LICENSE")

[Basic cleanup](/jlowin/fastmcp/commit/1b6813ef262bc5ff36a4b75f8fdc490177f448e3 "Basic cleanup")

Apr 5, 2025

[README.md](/jlowin/fastmcp/blob/main/README.md "README.md")

[README.md](/jlowin/fastmcp/blob/main/README.md "README.md")

[Update dark mode image in README (](/jlowin/fastmcp/commit/8f1a9735f575ce7921c4ecc69e814d3ee167ff58 "Update dark mode image in README (#1885)")[#1885](https://github.com/jlowin/fastmcp/pull/1885)[)](/jlowin/fastmcp/commit/8f1a9735f575ce7921c4ecc69e814d3ee167ff58 "Update dark mode image in README (#1885)")

Sep 21, 2025

[README\_OPENAPI.md](/jlowin/fastmcp/blob/main/README_OPENAPI.md "README_OPENAPI.md")

[README\_OPENAPI.md](/jlowin/fastmcp/blob/main/README_OPENAPI.md "README_OPENAPI.md")

[Fix OpenAPI deepObject style parameter encoding (](/jlowin/fastmcp/commit/b0f45a85c4b8a4f582b52d72835f07e721eab950 "Fix OpenAPI deepObject style parameter encoding (#1122)
* Fix OpenAPI deepObject style parameter encoding
Add support for deepObject style with explode=true to properly serialize
object parameters using bracket notation (param[key]=value) instead of
JSON strings. Fixes #1114.
🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>
* Create README_OPENAPI.md
---------
Co-authored-by: Claude <noreply@anthropic.com>")[#1122](https://github.com/jlowin/fastmcp/pull/1122)[)](/jlowin/fastmcp/commit/b0f45a85c4b8a4f582b52d72835f07e721eab950 "Fix OpenAPI deepObject style parameter encoding (#1122)
* Fix OpenAPI deepObject style parameter encoding
Add support for deepObject style with explode=true to properly serialize
object parameters using bracket notation (param[key]=value) instead of
JSON strings. Fixes #1114.
🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>
* Create README_OPENAPI.md
---------
Co-authored-by: Claude <noreply@anthropic.com>")

Jul 11, 2025

[Windows\_Notes.md](/jlowin/fastmcp/blob/main/Windows_Notes.md "Windows_Notes.md")

[Windows\_Notes.md](/jlowin/fastmcp/blob/main/Windows_Notes.md "Windows_Notes.md")

[Adding some notes for windows users](/jlowin/fastmcp/commit/f0a92df15515d160b48fdfa95bb8bafe4f9a0f36 "Adding some notes for windows users")

Dec 2, 2024

[justfile](/jlowin/fastmcp/blob/main/justfile "justfile")

[justfile](/jlowin/fastmcp/blob/main/justfile "justfile")

[switch from](/jlowin/fastmcp/commit/77b425c47d296737359e223046ed8b2b05ac3e92 "switch from `pyright` to `ty` (#1545)") ``[pyright](/jlowin/fastmcp/commit/77b425c47d296737359e223046ed8b2b05ac3e92 "switch from `pyright` to `ty` (#1545)")`` [to](/jlowin/fastmcp/commit/77b425c47d296737359e223046ed8b2b05ac3e92 "switch from `pyright` to `ty` (#1545)") ``[ty](/jlowin/fastmcp/commit/77b425c47d296737359e223046ed8b2b05ac3e92 "switch from `pyright` to `ty` (#1545)")`` [(](/jlowin/fastmcp/commit/77b425c47d296737359e223046ed8b2b05ac3e92 "switch from `pyright` to `ty` (#1545)")[#1545](https://github.com/jlowin/fastmcp/pull/1545)[)](/jlowin/fastmcp/commit/77b425c47d296737359e223046ed8b2b05ac3e92 "switch from `pyright` to `ty` (#1545)")

Aug 19, 2025

[pyproject.toml](/jlowin/fastmcp/blob/main/pyproject.toml "pyproject.toml")

[pyproject.toml](/jlowin/fastmcp/blob/main/pyproject.toml "pyproject.toml")

[Add raise on validation error and set uniform collection names](/jlowin/fastmcp/commit/de0c39c1b3ef953a9521d71a97c4dcf0afb38635 "Add raise on validation error and set uniform collection names")

Oct 8, 2025

[uv.lock](/jlowin/fastmcp/blob/main/uv.lock "uv.lock")

[uv.lock](/jlowin/fastmcp/blob/main/uv.lock "uv.lock")

[Add raise on validation error and set uniform collection names](/jlowin/fastmcp/commit/de0c39c1b3ef953a9521d71a97c4dcf0afb38635 "Add raise on validation error and set uniform collection names")

Oct 8, 2025

View all files

Repository files navigation
---------------------------

  ![FastMCP Logo](/jlowin/fastmcp/raw/main/docs/assets/brand/wordmark-watercolor-waves.png)

FastMCP v2 🚀
=============

[](#fastmcp-v2-)

**The fast, Pythonic way to build MCP servers and clients.**

_Made with ☕️ by [Prefect](https://www.prefect.io/)_

[![Docs](https://camo.githubusercontent.com/4fc759e03096f1811d9e10de82f8abdcf2eaf8218aa14395b2bd848cd72829a9/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646f63732d676f666173746d63702e636f6d2d626c7565)](https://gofastmcp.com) [![PyPI - Version](https://camo.githubusercontent.com/571af8b9c9cf7b99e371fe54614d2c2fabc3579c4ca8a6106d01fbba280d69d7/68747470733a2f2f696d672e736869656c64732e696f2f707970692f762f666173746d63702e737667)](https://pypi.org/project/fastmcp) [![Tests](https://github.com/jlowin/fastmcp/actions/workflows/run-tests.yml/badge.svg)](https://github.com/jlowin/fastmcp/actions/workflows/run-tests.yml) [![License](https://camo.githubusercontent.com/9eeb024ed9173dd272ded357cd6de7ec3d7e0b229045de94971f70c4e8f5e359/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f6c6963656e73652f6a6c6f77696e2f666173746d63702e737667)](https://github.com/jlowin/fastmcp/blob/main/LICENSE)

[![jlowin%2Ffastmcp | Trendshift](https://camo.githubusercontent.com/820d21df75e7cefe69c9321a491c7cd0d0f5c1d45cc3a1e1aa1bf6387732ceeb/68747470733a2f2f7472656e6473686966742e696f2f6170692f62616467652f7265706f7369746f726965732f3133323636)](https://trendshift.io/repositories/13266)

Note

#### FastMCP 2.0: The Standard Framework

[](#fastmcp-20-the-standard-framework)

FastMCP pioneered Python MCP development, and FastMCP 1.0 was incorporated into the [official MCP SDK](https://github.com/modelcontextprotocol/python-sdk) in 2024.

**This is FastMCP 2.0** — the actively maintained, production-ready framework that extends far beyond basic protocol implementation. While the SDK provides core functionality, FastMCP 2.0 delivers everything needed for production: advanced MCP patterns (server composition, proxying, OpenAPI/FastAPI generation, tool transformation), enterprise auth (Google, GitHub, WorkOS, Azure, Auth0, and more), deployment tools, testing utilities, and comprehensive client libraries.

**For production MCP applications, install FastMCP:** `pip install fastmcp`

* * *

**FastMCP is the standard framework for building MCP applications**, providing the fastest path from idea to production.

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) is a standardized way to provide context and tools to LLMs. FastMCP makes building production-ready MCP servers simple, with enterprise auth, deployment tools, and a complete ecosystem built in.

\# server.py
from fastmcp import FastMCP

mcp \= FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) \-> int:
    """Add two numbers"""
    return a + b

if \_\_name\_\_ \== "\_\_main\_\_":
    mcp.run()

Run the server locally:

fastmcp run server.py

### 📚 Documentation

[](#-documentation)

FastMCP's complete documentation is available at **[gofastmcp.com](https://gofastmcp.com)**, including detailed guides, API references, and advanced patterns. This readme provides only a high-level overview.

Documentation is also available in [llms.txt format](https://llmstxt.org/), which is a simple markdown standard that LLMs can consume easily.

There are two ways to access the LLM-friendly documentation:

*   [`llms.txt`](https://gofastmcp.com/llms.txt) is essentially a sitemap, listing all the pages in the documentation.
*   [`llms-full.txt`](https://gofastmcp.com/llms-full.txt) contains the entire documentation. Note this may exceed the context window of your LLM.

* * *

Table of Contents
-----------------

[](#table-of-contents)

*   [FastMCP v2 🚀](#fastmcp-v2-)
    *   [📚 Documentation](#-documentation)
    *   [What is MCP?](#what-is-mcp)
    *   [Why FastMCP?](#why-fastmcp)
    *   [Installation](#installation)
    *   [Core Concepts](#core-concepts)
        *   [The `FastMCP` Server](#the-fastmcp-server)
        *   [Tools](#tools)
        *   [Resources & Templates](#resources--templates)
        *   [Prompts](#prompts)
        *   [Context](#context)
        *   [MCP Clients](#mcp-clients)
    *   [Authentication](#authentication)
        *   [Enterprise Authentication, Zero Configuration](#enterprise-authentication-zero-configuration)
    *   [Deployment](#deployment)
        *   [From Development to Production](#from-development-to-production)
    *   [Advanced Features](#advanced-features)
        *   [Proxy Servers](#proxy-servers)
        *   [Composing MCP Servers](#composing-mcp-servers)
        *   [OpenAPI & FastAPI Generation](#openapi--fastapi-generation)
    *   [Running Your Server](#running-your-server)
    *   [Contributing](#contributing)
        *   [Prerequisites](#prerequisites)
        *   [Setup](#setup)
        *   [Unit Tests](#unit-tests)
        *   [Static Checks](#static-checks)
        *   [Pull Requests](#pull-requests)

* * *

What is MCP?
------------

[](#what-is-mcp)

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) lets you build servers that expose data and functionality to LLM applications in a secure, standardized way. It is often described as "the USB-C port for AI", providing a uniform way to connect LLMs to resources they can use. It may be easier to think of it as an API, but specifically designed for LLM interactions. MCP servers can:

*   Expose data through **Resources** (think of these sort of like GET endpoints; they are used to load information into the LLM's context)
*   Provide functionality through **Tools** (sort of like POST endpoints; they are used to execute code or otherwise produce a side effect)
*   Define interaction patterns through **Prompts** (reusable templates for LLM interactions)
*   And more!

FastMCP provides a high-level, Pythonic interface for building, managing, and interacting with these servers.

Why FastMCP?
------------

[](#why-fastmcp)

FastMCP handles all the complex protocol details so you can focus on building. In most cases, decorating a Python function is all you need — FastMCP handles the rest.

🚀 **Fast:** High-level interface means less code and faster development

🍀 **Simple:** Build MCP servers with minimal boilerplate

🐍 **Pythonic:** Feels natural to Python developers

🔍 **Complete:** Everything for production — enterprise auth (Google, GitHub, Azure, Auth0, WorkOS), deployment tools, testing frameworks, client libraries, and more

FastMCP provides the shortest path from idea to production. Deploy locally, to the cloud with [FastMCP Cloud](https://fastmcp.cloud), or to your own infrastructure.

Installation
------------

[](#installation)

We recommend installing FastMCP with [uv](https://docs.astral.sh/uv/):

uv pip install fastmcp

For full installation instructions, including verification, upgrading from the official MCPSDK, and developer setup, see the [**Installation Guide**](https://gofastmcp.com/getting-started/installation).

Core Concepts
-------------

[](#core-concepts)

These are the building blocks for creating MCP servers and clients with FastMCP.

### The `FastMCP` Server

[](#the-fastmcp-server)

The central object representing your MCP application. It holds your tools, resources, and prompts, manages connections, and can be configured with settings like authentication.

from fastmcp import FastMCP

\# Create a server instance
mcp \= FastMCP(name\="MyAssistantServer")

Learn more in the [**FastMCP Server Documentation**](https://gofastmcp.com/servers/fastmcp).

### Tools

[](#tools)

Tools allow LLMs to perform actions by executing your Python functions (sync or async). Ideal for computations, API calls, or side effects (like `POST`/`PUT`). FastMCP handles schema generation from type hints and docstrings. Tools can return various types, including text, JSON-serializable objects, and even images or audio aided by the FastMCP media helper classes.

@mcp.tool
def multiply(a: float, b: float) \-> float:
    """Multiplies two numbers."""
    return a \* b

Learn more in the [**Tools Documentation**](https://gofastmcp.com/servers/tools).

### Resources & Templates

[](#resources--templates)

Resources expose read-only data sources (like `GET` requests). Use `@mcp.resource("your://uri")`. Use `{placeholders}` in the URI to create dynamic templates that accept parameters, allowing clients to request specific data subsets.

\# Static resource
@mcp.resource("config://version")
def get\_version(): 
    return "2.0.1"

\# Dynamic resource template
@mcp.resource("users://{user\_id}/profile")
def get\_profile(user\_id: int):
    \# Fetch profile for user\_id...
    return {"name": f"User {user\_id}", "status": "active"}

Learn more in the [**Resources & Templates Documentation**](https://gofastmcp.com/servers/resources).

### Prompts

[](#prompts)

Prompts define reusable message templates to guide LLM interactions. Decorate functions with `@mcp.prompt`. Return strings or `Message` objects.

@mcp.prompt
def summarize\_request(text: str) \-> str:
    """Generate a prompt asking for a summary."""
    return f"Please summarize the following text:\\n\\n{text}"

Learn more in the [**Prompts Documentation**](https://gofastmcp.com/servers/prompts).

### Context

[](#context)

Access MCP session capabilities within your tools, resources, or prompts by adding a `ctx: Context` parameter. Context provides methods for:

*   **Logging:** Log messages to MCP clients with `ctx.info()`, `ctx.error()`, etc.
*   **LLM Sampling:** Use `ctx.sample()` to request completions from the client's LLM.
*   **HTTP Request:** Use `ctx.http_request()` to make HTTP requests to other servers.
*   **Resource Access:** Use `ctx.read_resource()` to access resources on the server
*   **Progress Reporting:** Use `ctx.report_progress()` to report progress to the client.
*   and more...

To access the context, add a parameter annotated as `Context` to any mcp-decorated function. FastMCP will automatically inject the correct context object when the function is called.

from fastmcp import FastMCP, Context

mcp \= FastMCP("My MCP Server")

@mcp.tool
async def process\_data(uri: str, ctx: Context):
    \# Log a message to the client
    await ctx.info(f"Processing {uri}...")

    \# Read a resource from the server
    data \= await ctx.read\_resource(uri)

    \# Ask client LLM to summarize the data
    summary \= await ctx.sample(f"Summarize: {data.content\[:500\]}")

    \# Return the summary
    return summary.text

Learn more in the [**Context Documentation**](https://gofastmcp.com/servers/context).

### MCP Clients

[](#mcp-clients)

Interact with _any_ MCP server programmatically using the `fastmcp.Client`. It supports various transports (Stdio, SSE, In-Memory) and often auto-detects the correct one. The client can also handle advanced patterns like server-initiated **LLM sampling requests** if you provide an appropriate handler.

Critically, the client allows for efficient **in-memory testing** of your servers by connecting directly to a `FastMCP` server instance via the `FastMCPTransport`, eliminating the need for process management or network calls during tests.

from fastmcp import Client

async def main():
    \# Connect via stdio to a local script
    async with Client("my\_server.py") as client:
        tools \= await client.list\_tools()
        print(f"Available tools: {tools}")
        result \= await client.call\_tool("add", {"a": 5, "b": 3})
        print(f"Result: {result.content\[0\].text}")

    \# Connect via SSE
    async with Client("http://localhost:8000/sse") as client:
        \# ... use the client
        pass

To use clients to test servers, use the following pattern:

from fastmcp import FastMCP, Client

mcp \= FastMCP("My MCP Server")

async def main():
    \# Connect via in-memory transport
    async with Client(mcp) as client:
        \# ... use the client

FastMCP also supports connecting to multiple servers through a single unified client using the standard MCP configuration format:

from fastmcp import Client

\# Standard MCP configuration with multiple servers
config \= {
    "mcpServers": {
        "weather": {"url": "https://weather-api.example.com/mcp"},
        "assistant": {"command": "python", "args": \["./assistant\_server.py"\]}
    }
}

\# Create a client that connects to all servers
client \= Client(config)

async def main():
    async with client:
        \# Access tools and resources with server prefixes
        forecast \= await client.call\_tool("weather\_get\_forecast", {"city": "London"})
        answer \= await client.call\_tool("assistant\_answer\_question", {"query": "What is MCP?"})

Learn more in the [**Client Documentation**](https://gofastmcp.com/clients/client) and [**Transports Documentation**](https://gofastmcp.com/clients/transports).

Authentication
--------------

[](#authentication)

### Enterprise Authentication, Zero Configuration

[](#enterprise-authentication-zero-configuration)

FastMCP provides comprehensive authentication support that sets it apart from basic MCP implementations. Secure your servers and authenticate your clients with the same enterprise-grade providers used by major corporations.

**Built-in OAuth Providers:**

*   **Google**
*   **GitHub**
*   **Microsoft Azure**
*   **Auth0**
*   **WorkOS**
*   **Descope**
*   **JWT/Custom**
*   **API Keys**

Protecting a server takes just two lines:

from fastmcp.server.auth import GoogleProvider

auth \= GoogleProvider(client\_id\="...", client\_secret\="...", base\_url\="https://myserver.com")
mcp \= FastMCP("Protected Server", auth\=auth)

Connecting to protected servers is even simpler:

async with Client("https://protected-server.com/mcp", auth\="oauth") as client:
    \# Automatic browser-based OAuth flow
    result \= await client.call\_tool("protected\_tool")

**Why FastMCP Auth Matters:**

*   **Production-Ready:** Persistent storage, token refresh, comprehensive error handling
*   **Zero-Config OAuth:** Just pass `auth="oauth"` for automatic setup
*   **Enterprise Integration:** WorkOS SSO, Azure Active Directory, Auth0 tenants
*   **Developer Experience:** Automatic browser launch, local callback server, environment variable support
*   **Advanced Architecture:** Full OIDC support, Dynamic Client Registration (DCR), and unique OAuth proxy pattern that enables DCR with any provider

_Authentication this comprehensive is unique to FastMCP 2.0._

Learn more in the **Authentication Documentation** for [servers](https://gofastmcp.com/servers/auth) and [clients](https://gofastmcp.com/clients/auth).

Deployment
----------

[](#deployment)

### From Development to Production

[](#from-development-to-production)

FastMCP supports every deployment scenario from local development to global scale:

**Development:** Run locally with a single command

fastmcp run server.py

**Production:** Deploy to [**FastMCP Cloud**](https://fastmcp.cloud) — Remote MCP that just works

*   Instant HTTPS endpoints
*   Built-in authentication
*   Zero configuration
*   Free for personal servers

**Self-Hosted:** Use HTTP or SSE transports for your own infrastructure

mcp.run(transport\="http", host\="0.0.0.0", port\=8000)

Learn more in the [**Deployment Documentation**](https://gofastmcp.com/deployment).

Advanced Features
-----------------

[](#advanced-features)

FastMCP introduces powerful ways to structure and compose your MCP applications.

### Proxy Servers

[](#proxy-servers)

Create a FastMCP server that acts as an intermediary for another local or remote MCP server using `FastMCP.as_proxy()`. This is especially useful for bridging transports (e.g., remote SSE to local Stdio) or adding a layer of logic to a server you don't control.

Learn more in the [**Proxying Documentation**](https://gofastmcp.com/patterns/proxy).

### Composing MCP Servers

[](#composing-mcp-servers)

Build modular applications by mounting multiple `FastMCP` instances onto a parent server using `mcp.mount()` (live link) or `mcp.import_server()` (static copy).

Learn more in the [**Composition Documentation**](https://gofastmcp.com/patterns/composition).

### OpenAPI & FastAPI Generation

[](#openapi--fastapi-generation)

Automatically generate FastMCP servers from existing OpenAPI specifications (`FastMCP.from_openapi()`) or FastAPI applications (`FastMCP.from_fastapi()`), instantly bringing your web APIs to the MCP ecosystem.

Learn more: [**OpenAPI Integration**](https://gofastmcp.com/integrations/openapi) | [**FastAPI Integration**](https://gofastmcp.com/integrations/fastapi).

Running Your Server
-------------------

[](#running-your-server)

The main way to run a FastMCP server is by calling the `run()` method on your server instance:

\# server.py
from fastmcp import FastMCP

mcp \= FastMCP("Demo 🚀")

@mcp.tool
def hello(name: str) \-> str:
    return f"Hello, {name}!"

if \_\_name\_\_ \== "\_\_main\_\_":
    mcp.run()  \# Default: uses STDIO transport

FastMCP supports three transport protocols:

**STDIO (Default)**: Best for local tools and command-line scripts.

mcp.run(transport\="stdio")  \# Default, so transport argument is optional

**Streamable HTTP**: Recommended for web deployments.

mcp.run(transport\="http", host\="127.0.0.1", port\=8000, path\="/mcp")

**SSE**: For compatibility with existing SSE clients.

mcp.run(transport\="sse", host\="127.0.0.1", port\=8000)

See the [**Running Server Documentation**](https://gofastmcp.com/deployment/running-server) for more details.

Contributing
------------

[](#contributing)

Contributions are the core of open source! We welcome improvements and features.

### Prerequisites

[](#prerequisites)

*   Python 3.10+
*   [uv](https://docs.astral.sh/uv/) (Recommended for environment management)

### Setup

[](#setup)

1.  Clone the repository:
    
    git clone https://github.com/jlowin/fastmcp.git 
    cd fastmcp
    
2.  Create and sync the environment:
    
    uv sync
    
    This installs all dependencies, including dev tools.
    
3.  Activate the virtual environment (e.g., `source .venv/bin/activate` or via your IDE).
    

### Unit Tests

[](#unit-tests)

FastMCP has a comprehensive unit test suite. All PRs must introduce or update tests as appropriate and pass the full suite.

Run tests using pytest:

pytest

or if you want an overview of the code coverage

uv run pytest --cov=src --cov=examples --cov-report=html

### Static Checks

[](#static-checks)

FastMCP uses `pre-commit` for code formatting, linting, and type-checking. All PRs must pass these checks (they run automatically in CI).

Install the hooks locally:

uv run pre-commit install

The hooks will now run automatically on `git commit`. You can also run them manually at any time:

pre-commit run --all-files
# or via uv
uv run pre-commit run --all-files

### Pull Requests

[](#pull-requests)

1.  Fork the repository on GitHub.
2.  Create a feature branch from `main`.
3.  Make your changes, including tests and documentation updates.
4.  Ensure tests and pre-commit hooks pass.
5.  Commit your changes and push to your fork.
6.  Open a pull request against the `main` branch of `jlowin/fastmcp`.

Please open an issue or discussion for questions or suggestions before starting significant work!

About
-----

🚀 The fast, Pythonic way to build MCP servers and clients

[gofastmcp.com](https://gofastmcp.com "https://gofastmcp.com")

### Topics

[python](/topics/python "Topic: python") [mcp](/topics/mcp "Topic: mcp") [agents](/topics/agents "Topic: agents") [llms](/topics/llms "Topic: llms") [model-context-protocol](/topics/model-context-protocol "Topic: model-context-protocol") [mcp-servers](/topics/mcp-servers "Topic: mcp-servers") [mcp-tools](/topics/mcp-tools "Topic: mcp-tools") [fastmcp](/topics/fastmcp "Topic: fastmcp") [mcp-clients](/topics/mcp-clients "Topic: mcp-clients")

### Resources

[Readme](#readme-ov-file)

### License

[Apache-2.0 license](#Apache-2.0-1-ov-file)

### Code of conduct

[Code of conduct](#coc-ov-file)

### Uh oh!

There was an error while loading. Please reload this page.

[Activity](/jlowin/fastmcp/activity)

### Stars

[**18.9k** stars](/jlowin/fastmcp/stargazers)

### Watchers

[**78** watching](/jlowin/fastmcp/watchers)

### Forks

[**1.4k** forks](/jlowin/fastmcp/forks)

[Report repository](/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fjlowin%2Ffastmcp&report=jlowin+%28user%29)

[Releases 63](/jlowin/fastmcp/releases)
---------------------------------------

[

v2.12.4: OIDC What You Did There Latest

Sep 26, 2025



](/jlowin/fastmcp/releases/tag/v2.12.4)

[\+ 62 releases](/jlowin/fastmcp/releases)

[Used by 4.7k](/jlowin/fastmcp/network/dependents)
--------------------------------------------------

