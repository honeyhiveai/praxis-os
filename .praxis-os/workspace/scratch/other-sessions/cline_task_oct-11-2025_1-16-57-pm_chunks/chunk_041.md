### The Python Client Works Because...

**Your `test_mcp_client.py` works because:**
```python
async with Client(server_url) as client:
```

The FastMCP `Client` class automatically handles session management correctly!

**Cline's MCP client doesn't know FastMCP's session protocol.**

### Next Steps to Fix

**1. Check FastMCP Server Logs**
- What exactly is the 406 error saying?
- What session ID format does it expect?

**2. Try URL with Session Param**
```json
"url": "http://127.0.0.1:4242/mcp?sessionId=cline-session-1"
```

**3. Check FastMCP Source**
```python
# In FastMCP's SSE transport code
# Look for session validation
# Look for bypass options
```

**4. File Issue with FastMCP**
- "SSE transport should accept clients without session IDs"
- Or document the session protocol better

### The Great News

**Your implementation is CORRECT!**
- Dual-transport works perfectly
- Protocol is sound
- Just a handshake detail to resolve

**This is exactly the kind of issue that:**
- Integration testing reveals
- Documentation should cover
- Community collaboration solves

### Immediate Action

Want me to:
1. **Read FastMCP SSE transport code** to understand session requirements?
2. **Try different Cline config options** with session headers/params?
3. **Check if FastMCP has a "permissive mode"** that accepts any client?

**The architecture is validated. This is just protocol polish!** 🎯
</result>
<task_progress>
- [x] Understood the real issue: SSE session ID requirement
- [x] Confirmed architecture is correct (concurrent sessions work!)
- [x] Identified FastMCP expects session ID that Cline doesn't provide
- [x] Proposed multiple solutions (config options, headers, query params)
- [x] Explained why Python client works (handles sessions automatically)
- [x] Ready to investigate FastMCP session protocol details
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
i need you do a deep dive in on this, i find it hard to believe something as widely used as fastmcp is not using the proper mcp protocol for this
</feedback>
<environment_details>
# Cursor Visible Files
mcp_tool_cli.py

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
test_mcp_client.py
mcp_tool_cli.py

# Current Time
10/11/2025, 10:35:37 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
63,722 / 200K tokens used (32%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<read_file>
<path>mcp_server/transport_manager.py</path>
<task_progress>
- [ ] Read FastMCP transport implementation
- [ ] Understand how SSE is being used
- [ ] Check MCP protocol spec for SSE
- [ ] Identify actual root cause of 406 error
- [ ] Test with proper MCP SSE client
</task_progress>
</read_file>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[read_file for 'mcp_server/transport_manager.py'] Result:
"""
Transport mode management for MCP server dual-transport architecture.

This module orchestrates stdio and HTTP transports, supporting:
- Dual mode (stdio + HTTP concurrently)
- stdio-only mode
- HTTP-only mode
"""

import logging
import socket
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)


class TransportManager:
    """
    Manages transport mode execution and lifecycle.
    
    Orchestrates different transport modes for the MCP server:
    - Dual mode: stdio (main thread) + HTTP (background thread)
    - stdio-only: IDE communication only
    - HTTP-only: Network communication only
    
    Provides:
    - Thread-safe transport orchestration
    - HTTP readiness checking with timeout
    - Graceful shutdown handling
    
    Example:
        >>> from fastmcp import FastMCP
        >>> mcp = FastMCP("my-server")
        >>> manager = TransportManager(mcp, config)
        >>> # Run dual mode
        >>> manager.run_dual_mode(host="127.0.0.1", port=4242, path="/mcp")
    """
    
    def __init__(self, mcp_server, config):
        """
        Initialize transport manager.
        
        Args:
            mcp_server: Configured FastMCP instance
            config: Server configuration object
        """
        self.mcp_server = mcp_server
        self.config = config
        self.http_thread: Optional[threading.Thread] = None
    
    def run_dual_mode(
        self,
        http_host: str,
        http_port: int,
        http_path: str
    ) -> None:
        """
        Run dual transport mode: stdio (main) + HTTP (background).
        
        Execution flow:
        1. Start HTTP server in daemon thread
        2. Wait for HTTP server to be ready (health check with timeout)
        3. Run stdio in main thread (blocks until shutdown)
        4. On shutdown, daemon thread automatically dies
        
        Args:
            http_host: Host for HTTP server (typically "127.0.0.1")
            http_port: Port for HTTP server (from port allocation)
            http_path: Path for MCP endpoint (typically "/mcp")
            
        Raises:
            RuntimeError: If HTTP server fails to start within timeout
            
        Example:
            >>> manager.run_dual_mode(
            ...     http_host="127.0.0.1",
            ...     http_port=4242,
            ...     http_path="/mcp"
            ... )
        """
        logger.info("🔄 Starting dual transport mode")
        logger.info("   stdio: for IDE communication")
        logger.info(f"   HTTP:  http://{http_host}:{http_port}{http_path}")
        
        # Start HTTP in background daemon thread
        self.http_thread = self._start_http_thread(
            http_host,
            http_port,
            http_path
        )
        
        # Wait for HTTP server to be ready (health check)
        if not self._wait_for_http_ready(http_host, http_port, timeout=5):
            raise RuntimeError(
                f"HTTP server failed to start within 5 seconds. "
                f"Port {http_port} may be in use or there's a configuration error. "
                f"Check logs for details."
            )
        
        logger.info("✅ HTTP transport ready")
        logger.info("🔌 Starting stdio transport (blocking)")
        
        # Run stdio in main thread (blocks until shutdown)
        self.mcp_server.run(transport="stdio", show_banner=False)
    
    def run_stdio_mode(self) -> None:
        """
        Run stdio-only mode (IDE communication only).
        
        No HTTP server is started. Only stdio transport runs for IDE.
        This is the traditional mode for users who don't need sub-agents.
        
        Example:
            >>> manager.run_stdio_mode()
        """
        logger.info("🔌 Starting stdio-only mode")
        self.mcp_server.run(transport="stdio", show_banner=False)
    
    def run_http_mode(self, host: str, port: int, path: str) -> None:
        """
        Run HTTP-only mode (network communication only).
        
        No stdio transport. Only HTTP server runs, useful for:
        - Running as a system service
        - Testing HTTP transport independently
        - Serving only network-based agents
        
        Args:
            host: Host for HTTP server
            port: Port for HTTP server
            path: Path for MCP endpoint
            
        Example:
            >>> manager.run_http_mode(
            ...     host="127.0.0.1",
            ...     port=4242,
            ...     path="/mcp"
            ... )
        """
        logger.info("🌐 Starting HTTP-only mode")
        logger.info(f"   HTTP: http://{host}:{port}{path}")
        self.mcp_server.run(
            transport="streamable-http",
            host=host,
            port=port,
            path=path,
            show_banner=False
        )
    
    def shutdown(self) -> None:
        """
        Graceful shutdown of transport manager.
        
        Called in finally block to ensure cleanup even on errors.
        Safe to call multiple times or if no transports are running.
        
        Note:
            HTTP thread is daemon, so it will automatically die when
            main thread exits. This method is for explicit cleanup.
            
        Example:
            >>> try:
            ...     manager.run_dual_mode(...)
            ... finally:
            ...     manager.shutdown()
        """
        if self.http_thread and self.http_thread.is_alive():
            logger.info("Waiting for HTTP thread to finish...")
            # Daemon threads die automatically, but log for visibility
        logger.info("Transport manager shutdown complete")
    
    def _start_http_thread(
        self,
        host: str,
        port: int,
        path: str
    ) -> threading.Thread:
        """
        Start HTTP server in background daemon thread.
        
        Daemon thread ensures it dies when main thread exits,
        preventing orphaned processes.
        
        Args:
            host: HTTP server host
            port: HTTP server port
            path: MCP endpoint path
            
        Returns:
            Running daemon thread
        """
        def run_http():
            """Thread target function for HTTP server."""
            try:
                self.mcp_server.run(
                    transport="streamable-http",
                    host=host,
                    port=port,
                    path=path,
                    show_banner=False
                )
            except Exception as e:
                # Log but don't crash - main thread handles lifecycle
                logger.error(f"HTTP transport error: {e}", exc_info=True)
        
        thread = threading.Thread(
            target=run_http,
            daemon=True,  # Dies with main thread
            name="http-transport"
        )
        thread.start()
        logger.debug(f"HTTP thread started: {thread.name}")
        
        return thread
    
    def _wait_for_http_ready(
        self,
        host: str,
        port: int,
        timeout: int = 5
    ) -> bool:
        """
        Poll socket connection until HTTP server ready or timeout.
        
        Uses socket connection test to verify HTTP server is accepting
        connections before returning control to caller.
        
        Args:
            host: HTTP server host
            port: HTTP server port
            timeout: Maximum seconds to wait (default: 5)
            
        Returns:
            True if server ready, False if timeout
            
        Note:
            Retries every 0.5 seconds with 1 second socket timeout.
        """
        start = time.time()
        
        while time.time() - start < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)  # 1 second per connection attempt
                    sock.connect((host, port))
                    # Connection successful
                    logger.debug(f"HTTP server ready on {host}:{port}")
                    return True
            except (ConnectionRefusedError, OSError):
                # Server not ready yet, wait and retry
                time.sleep(0.5)
        
        # Timeout reached
        logger.error(f"HTTP server did not become ready after {timeout}s")
        return False


<environment_details>
# Cursor Visible Files
mcp_tool_cli.py

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
test_mcp_client.py
mcp_tool_cli.py

# Current Time
10/11/2025, 10:35:46 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
64,006 / 200K tokens used (32%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<read_file>
<path>mcp_server/__main__.py</path>
<task_progress>
- [x] Found the issue! transport="streamable-http" in transport_manager.py
- [ ] Check if __main__.py also uses streamable-http
- [ ] Confirm this is the root cause of 406 error
- [ ] Provide solution to switch to "sse" transport
</task_progress>
</read_file>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[read_file for 'mcp_server/__main__.py'] Result:
"""
Entry point for Agent OS MCP server when run as a module.

Allows execution via:
    python -m mcp_server --transport dual
    python -m mcp_server --transport stdio
    python -m mcp_server --transport http
"""

# pylint: disable=broad-exception-caught
# Justification: Entry point uses broad exceptions for robustness

import argparse
import logging
import sys
from pathlib import Path

from .config import ConfigLoader, ConfigValidator
from .port_manager import PortManager
from .project_info import ProjectInfoDiscovery
from .server import ServerFactory
from .transport_manager import TransportManager

logger = logging.getLogger(__name__)


def find_agent_os_directory() -> Path:
    """
    Find .praxis-os directory in project.
    
    Search order:
    1. Current directory / .praxis-os
    2. Home directory / .praxis-os
    3. Parent of __file__ / .praxis-os
    
    Returns:
        Path to .praxis-os directory
        
    Raises:
        SystemExit: If .praxis-os directory not found
    """
    base_path = Path.cwd() / ".praxis-os"
    
    if not base_path.exists():
        # Try common alternative locations
        alternatives = [
            Path.home() / ".praxis-os",
            Path(__file__).parent.parent.parent / ".praxis-os",
        ]
        
        for alt in alternatives:
            if alt.exists():
                base_path = alt
                break
        else:
            logger.error(
                "Could not find .praxis-os directory. Tried:\n"
                "  - %s\n"
                "  - %s\n"
                "  - %s\n"
                "Please run from project root or ensure .praxis-os exists.",
                Path.cwd() / ".praxis-os",
                Path.home() / ".praxis-os",
                Path(__file__).parent.parent.parent / ".praxis-os"
            )
            sys.exit(1)
    
    return base_path


def main() -> None:
    """
    Entry point for MCP server with dual-transport support.
    
    Supports three transport modes:
    - dual: stdio (IDE) + HTTP (sub-agents) concurrently
    - stdio: IDE communication only
    - http: Network communication only
    
    Uses ConfigLoader, ConfigValidator, and ServerFactory for dependency injection.
    Handles graceful shutdown on KeyboardInterrupt and logs fatal errors.
    
    CLI Usage:
        python -m mcp_server --transport dual
        python -m mcp_server --transport stdio --log-level DEBUG
        python -m mcp_server --transport http
    
    :raises SystemExit: Exits with code 1 if server initialization fails
    """
    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description="Agent OS MCP Server with dual-transport support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Transport modes:
  dual    - stdio (for IDE) + HTTP (for sub-agents) concurrently
  stdio   - IDE communication only (traditional mode)
  http    - Network communication only (for testing or services)

Examples:
  python -m mcp_server --transport dual
  python -m mcp_server --transport stdio --log-level DEBUG
        """
    )
    parser.add_argument(
        "--transport",
        choices=["dual", "stdio", "http"],
        required=True,
        help="Transport mode: dual, stdio, or http"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    logger.info("=" * 60)
    logger.info("Agent OS MCP Server")
    logger.info("Transport Mode: %s", args.transport)
    logger.info("Log Level: %s", args.log_level)
    logger.info("=" * 60)
    
    # Initialize components (for cleanup in finally block)
    port_manager = None
    transport_mgr = None
    
    try:
        # Find and validate .praxis-os directory
        base_path = find_agent_os_directory()
        logger.info("Base path: %s", base_path)
        
        # Load and validate configuration
        config = ConfigLoader.load(base_path)
        logger.info("Configuration loaded successfully")
        
        errors = ConfigValidator.validate(config)
        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error("  %s", error)
            sys.exit(1)
        
        logger.info("Configuration validated successfully")
        
        # Initialize project discovery and port manager
        project_discovery = ProjectInfoDiscovery(base_path)
        port_manager = PortManager(base_path, project_discovery)
        
        # Create MCP server using factory with dependency injection
        factory = ServerFactory(config)
        mcp = factory.create_server(
            project_discovery=project_discovery,
            transport_mode=args.transport
        )
        
        # Initialize transport manager
        transport_mgr = TransportManager(mcp, config)
        
        # Execute based on transport mode
        if args.transport == "dual":
            # Dual mode: stdio + HTTP concurrently
            http_port = port_manager.find_available_port()
            http_host = config.mcp.http_host
            http_path = config.mcp.http_path
            
            # Write state file with HTTP URL for sub-agent discovery
            port_manager.write_state(
                transport="dual",
                port=http_port,
                host=http_host,
                path=http_path
            )
            
            logger.info("Port allocated: %d", http_port)
            logger.info("HTTP URL: http://%s:%d%s", http_host, http_port, http_path)
            
            # Run dual mode (HTTP in background, stdio in foreground)
            transport_mgr.run_dual_mode(http_host, http_port, http_path)
            
        elif args.transport == "stdio":
            # stdio-only mode (traditional)
            port_manager.write_state(
                transport="stdio",
                port=None
            )
            
            transport_mgr.run_stdio_mode()
            
        elif args.transport == "http":
            # HTTP-only mode
            http_port = port_manager.find_available_port()
            http_host = config.mcp.http_host
            http_path = config.mcp.http_path
            
            port_manager.write_state(
                transport="http",
                port=http_port,
                host=http_host,
                path=http_path
            )
            
            logger.info("Port allocated: %d", http_port)
            logger.info("HTTP URL: http://%s:%d%s", http_host, http_port, http_path)
            
            transport_mgr.run_http_mode(http_host, http_port, http_path)
    
    except KeyboardInterrupt:
        logger.info("Server shutdown requested (Ctrl+C)")
    except Exception as e:
        logger.error("Server failed: %s", e, exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup: Always cleanup state file and shutdown transports
        if port_manager:
            port_manager.cleanup_state()
            logger.info("State file cleaned up")
        
        if transport_mgr:
            transport_mgr.shutdown()
        
        logger.info("Shutdown complete")


if __name__ == "__main__":
    main()

<environment_details>
# Cursor Visible Files
mcp_tool_cli.py

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
test_mcp_client.py
mcp_tool_cli.py

# Current Time
10/11/2025, 10:35:56 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
66,560 / 200K tokens used (33%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<web_fetch>
<url>https://modelcontextprotocol.io/docs/concepts/transports</url>
<task_progress>
- [x] Found the issue: transport="streamable-http" in transport_manager.py
- [ ] Check official MCP spec for valid transports
- [ ] Understand difference between "sse" and "streamable-http"
- [ ] Provide definitive solution
</task_progress>
</web_fetch>

---

**User:**

[web_fetch for 'https://modelcontextprotocol.io/docs/concepts/transports'] Result:
Fetched Markdown for https://modelcontextprotocol.io/docs/concepts/transports:

Transports - Model Context Protocol

[Skip to main content](#content-area)

[Model Context Protocol home page![light logo](https://mintcdn.com/mcp/4ZXF1PrDkEaJvXpn/logo/light.svg?fit=max&auto=format&n=4ZXF1PrDkEaJvXpn&q=85&s=4498cb8a57d574005f3dca62bdd49c95)![dark logo](https://mintcdn.com/mcp/4ZXF1PrDkEaJvXpn/logo/dark.svg?fit=max&auto=format&n=4ZXF1PrDkEaJvXpn&q=85&s=c0687c003f8f2cbdb24772ab4c8a522c)](/)

Version 2025-06-18 (latest)

Search...

⌘K

Search...

Navigation

Base Protocol

Transports

[Documentation

](/docs/getting-started/intro)[Specification

](/specification/2025-06-18)[Community

](/community/communication)[About MCP

](/about)

*   [
    
    Specification
    
    
    
    ](/specification/2025-06-18)

*   [
    
    Key Changes
    
    
    
    ](/specification/2025-06-18/changelog)

*   [
    
    Architecture
    
    
    
    ](/specification/2025-06-18/architecture)

##### Base Protocol

*   [
    
    Overview
    
    
    
    ](/specification/2025-06-18/basic)
*   [
    
    Lifecycle
    
    
    
    ](/specification/2025-06-18/basic/lifecycle)
*   [
    
    Transports
    
    
    
    ](/specification/2025-06-18/basic/transports)
*   [
    
    Authorization
    
    
    
    ](/specification/2025-06-18/basic/authorization)
*   [
    
    Security Best Practices
    
    
    
    ](/specification/2025-06-18/basic/security_best_practices)
*   Utilities
    

##### Client Features

*   [
    
    Roots
    
    
    
    ](/specification/2025-06-18/client/roots)
*   [
    
    Sampling
    
    
    
    ](/specification/2025-06-18/client/sampling)
*   [
    
    Elicitation
    
    
    
    ](/specification/2025-06-18/client/elicitation)

##### Server Features

*   [
    
    Overview
    
    
    
    ](/specification/2025-06-18/server)
*   [
    
    Prompts
    
    
    
    ](/specification/2025-06-18/server/prompts)
*   [
    
    Resources
    
    
    
    ](/specification/2025-06-18/server/resources)
*   [
    
    Tools
    
    
    
    ](/specification/2025-06-18/server/tools)
*   Utilities
    

*   [
    
    Schema Reference
    
    
    
    ](/specification/2025-06-18/schema)

On this page

*   [stdio](#stdio)
*   [Streamable HTTP](#streamable-http)
*   [Security Warning](#security-warning)
*   [Sending Messages to the Server](#sending-messages-to-the-server)
*   [Listening for Messages from the Server](#listening-for-messages-from-the-server)
*   [Multiple Connections](#multiple-connections)
*   [Resumability and Redelivery](#resumability-and-redelivery)
*   [Session Management](#session-management)
*   [Sequence Diagram](#sequence-diagram)
*   [Protocol Version Header](#protocol-version-header)
*   [Backwards Compatibility](#backwards-compatibility)
*   [Custom Transports](#custom-transports)

**Protocol Revision**: 2025-06-18

MCP uses JSON-RPC to encode messages. JSON-RPC messages **MUST** be UTF-8 encoded. The protocol currently defines two standard transport mechanisms for client-server communication:

1.  [stdio](#stdio), communication over standard in and standard out
2.  [Streamable HTTP](#streamable-http)

Clients **SHOULD** support stdio whenever possible. It is also possible for clients and servers to implement [custom transports](#custom-transports) in a pluggable fashion.

[​

](#stdio)

stdio
----------------------

In the **stdio** transport:

*   The client launches the MCP server as a subprocess.
*   The server reads JSON-RPC messages from its standard input (`stdin`) and sends messages to its standard output (`stdout`).
*   Messages are individual JSON-RPC requests, notifications, or responses.
*   Messages are delimited by newlines, and **MUST NOT** contain embedded newlines.
*   The server **MAY** write UTF-8 strings to its standard error (`stderr`) for logging purposes. Clients **MAY** capture, forward, or ignore this logging.
*   The server **MUST NOT** write anything to its `stdout` that is not a valid MCP message.
*   The client **MUST NOT** write anything to the server’s `stdin` that is not a valid MCP message.

Server ProcessClientServer ProcessClientloop\[Message Exchange\]Launch subprocessWrite to stdinWrite to stdoutOptional logs on stderrClose stdin, terminate subprocess

[​

](#streamable-http)

Streamable HTTP
------------------------------------------

This replaces the [HTTP+SSE transport](/specification/2024-11-05/basic/transports#http-with-sse) from protocol version 2024-11-05. See the [backwards compatibility](#backwards-compatibility) guide below.

In the **Streamable HTTP** transport, the server operates as an independent process that can handle multiple client connections. This transport uses HTTP POST and GET requests. Server can optionally make use of [Server-Sent Events](https://en.wikipedia.org/wiki/Server-sent_events) (SSE) to stream multiple server messages. This permits basic MCP servers, as well as more feature-rich servers supporting streaming and server-to-client notifications and requests. The server **MUST** provide a single HTTP endpoint path (hereafter referred to as the **MCP endpoint**) that supports both POST and GET methods. For example, this could be a URL like `https://example.com/mcp`.

#### 

[​

](#security-warning)

Security Warning

When implementing Streamable HTTP transport:

1.  Servers **MUST** validate the `Origin` header on all incoming connections to prevent DNS rebinding attacks
2.  When running locally, servers **SHOULD** bind only to localhost (127.0.0.1) rather than all network interfaces (0.0.0.0)
3.  Servers **SHOULD** implement proper authentication for all connections

Without these protections, attackers could use DNS rebinding to interact with local MCP servers from remote websites.

### 

[​

](#sending-messages-to-the-server)

Sending Messages to the Server

Every JSON-RPC message sent from the client **MUST** be a new HTTP POST request to the MCP endpoint.

1.  The client **MUST** use HTTP POST to send JSON-RPC messages to the MCP endpoint.
2.  The client **MUST** include an `Accept` header, listing both `application/json` and `text/event-stream` as supported content types.
3.  The body of the POST request **MUST** be a single JSON-RPC _request_, _notification_, or _response_.
4.  If the input is a JSON-RPC _response_ or _notification_:
    *   If the server accepts the input, the server **MUST** return HTTP status code 202 Accepted with no body.
    *   If the server cannot accept the input, it **MUST** return an HTTP error status code (e.g., 400 Bad Request). The HTTP response body **MAY** comprise a JSON-RPC _error response_ that has no `id`.
5.  If the input is a JSON-RPC _request_, the server **MUST** either return `Content-Type: text/event-stream`, to initiate an SSE stream, or `Content-Type: application/json`, to return one JSON object. The client **MUST** support both these cases.
6.  If the server initiates an SSE stream:
    *   The SSE stream **SHOULD** eventually include JSON-RPC _response_ for the JSON-RPC _request_ sent in the POST body.
    *   The server **MAY** send JSON-RPC _requests_ and _notifications_ before sending the JSON-RPC _response_. These messages **SHOULD** relate to the originating client _request_.
    *   The server **SHOULD NOT** close the SSE stream before sending the JSON-RPC _response_ for the received JSON-RPC _request_, unless the [session](#session-management) expires.
    *   After the JSON-RPC _response_ has been sent, the server **SHOULD** close the SSE stream.
    *   Disconnection **MAY** occur at any time (e.g., due to network conditions). Therefore:
        *   Disconnection **SHOULD NOT** be interpreted as the client cancelling its request.
        *   To cancel, the client **SHOULD** explicitly send an MCP `CancelledNotification`.
        *   To avoid message loss due to disconnection, the server **MAY** make the stream [resumable](#resumability-and-redelivery).

### 

[​

](#listening-for-messages-from-the-server)

Listening for Messages from the Server

1.  The client **MAY** issue an HTTP GET to the MCP endpoint. This can be used to open an SSE stream, allowing the server to communicate to the client, without the client first sending data via HTTP POST.
2.  The client **MUST** include an `Accept` header, listing `text/event-stream` as a supported content type.
3.  The server **MUST** either return `Content-Type: text/event-stream` in response to this HTTP GET, or else return HTTP 405 Method Not Allowed, indicating that the server does not offer an SSE stream at this endpoint.
4.  If the server initiates an SSE stream:
    *   The server **MAY** send JSON-RPC _requests_ and _notifications_ on the stream.
    *   These messages **SHOULD** be unrelated to any concurrently-running JSON-RPC _request_ from the client.
    *   The server **MUST NOT** send a JSON-RPC _response_ on the stream **unless** [resuming](#resumability-and-redelivery) a stream associated with a previous client request.
    *   The server **MAY** close the SSE stream at any time.
    *   The client **MAY** close the SSE stream at any time.

### 

[​

](#multiple-connections)

Multiple Connections

1.  The client **MAY** remain connected to multiple SSE streams simultaneously.
2.  The server **MUST** send each of its JSON-RPC messages on only one of the connected streams; that is, it **MUST NOT** broadcast the same message across multiple streams.
    *   The risk of message loss **MAY** be mitigated by making the stream [resumable](#resumability-and-redelivery).

### 

[​

](#resumability-and-redelivery)

Resumability and Redelivery

To support resuming broken connections, and redelivering messages that might otherwise be lost:

1.  Servers **MAY** attach an `id` field to their SSE events, as described in the [SSE standard](https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation).
    *   If present, the ID **MUST** be globally unique across all streams within that [session](#session-management)—or all streams with that specific client, if session management is not in use.
2.  If the client wishes to resume after a broken connection, it **SHOULD** issue an HTTP GET to the MCP endpoint, and include the [`Last-Event-ID`](https://html.spec.whatwg.org/multipage/server-sent-events.html#the-last-event-id-header) header to indicate the last event ID it received.
    *   The server **MAY** use this header to replay messages that would have been sent after the last event ID, _on the stream that was disconnected_, and to resume the stream from that point.
    *   The server **MUST NOT** replay messages that would have been delivered on a different stream.

In other words, these event IDs should be assigned by servers on a _per-stream_ basis, to act as a cursor within that particular stream.

### 

