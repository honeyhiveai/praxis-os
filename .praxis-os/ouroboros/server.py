"""
Ouroboros Server: FastMCP server initialization and lifecycle management.

This module creates and configures the complete MCP server with all subsystems:
1. Load config (Pydantic v2 validation)
2. Initialize Foundation layer (StateManager)
3. Initialize Subsystems (RAG, Workflow, Browser)
4. Initialize Middleware (query_tracker, session_mapper)
5. Register Tools (via ToolRegistry auto-discovery)
6. Return FastMCP server

Architecture:
    create_server()
        ↓
    FastMCP("praxis-os")
        ↓
    Initialize Subsystems
        ↓
    Initialize Middleware
        ↓
    ToolRegistry.register_all()
        ↓
    Return configured server

Traceability:
    FR-010: Tool Auto-Discovery
    NFR-U2: Fail-fast validation at startup
    NFR-P1: Cold start <30s
"""

import logging
from pathlib import Path
from typing import Any, Optional

from fastmcp import FastMCP

from ouroboros.config.schemas.mcp import MCPConfig
from ouroboros.tools.registry import ToolRegistry
from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


def create_server(base_path: Path, transport_mode: str = "stdio") -> FastMCP:
    """
    Create and configure complete MCP server.
    
    Initializes all subsystems, middleware, and tools in the correct order:
    1. Load and validate config
    2. Create FastMCP server instance
    3. Initialize Foundation layer (StateManager)
    4. Initialize Subsystems (RAG, Workflow, Browser)
    5. Initialize Middleware (query_tracker, session_mapper)
    6. Auto-discover and register tools (via ToolRegistry)
    
    Args:
        base_path: Path to .praxis-os directory
        transport_mode: Transport mode (dual, stdio, http)
        
    Returns:
        FastMCP: Configured server ready to run
        
    Raises:
        ActionableError: If initialization fails with remediation guidance
        
    Example:
        >>> from pathlib import Path
        >>> from ouroboros.server import create_server
        >>> 
        >>> base_path = Path(".praxis-os")
        >>> mcp = create_server(base_path, transport_mode="dual")
        >>> mcp.run()  # Start server
    
    Cold Start Target: <30s
    """
    logger.info("=" * 60)
    logger.info("Initializing Ouroboros MCP Server")
    logger.info("Base path: %s", base_path)
    logger.info("=" * 60)
    
    # ========================================================================
    # 1. Load and Validate Configuration
    # ========================================================================
    logger.info("Loading configuration...")
    
    config_path = base_path / "config" / "mcp.yaml"
    
    try:
        config = MCPConfig.from_yaml(config_path)
        logger.info("✅ Configuration loaded and validated")
    except FileNotFoundError as e:
        raise ActionableError(
            what_failed="Configuration loading",
            why_failed=f"Config file not found: {config_path}",
            how_to_fix=(
                f"Create config file at {config_path}\n"
                "Reference: See documentation for config structure"
            )
        ) from e
    except Exception as e:
        raise ActionableError(
            what_failed="Configuration validation",
            why_failed=str(e),
            how_to_fix=(
                f"Fix configuration errors in {config_path}\n"
                "Check field names, types, and required values"
            )
        ) from e
    
    # Validate paths exist
    path_errors = config.validate_paths()
    if path_errors:
        error_msg = "\n".join(path_errors)
        raise ActionableError(
            what_failed="Configuration path validation",
            why_failed=f"Invalid paths in configuration:\n{error_msg}",
            how_to_fix="Create missing directories or update config paths"
        )
    
    # ========================================================================
    # 2. Create FastMCP Server Instance
    # ========================================================================
    logger.info("Creating FastMCP server instance...")
    
    mcp = FastMCP(
        "praxis-os",
        instructions=(
            "You are an AI assistant with access to the prAxIs OS MCP server. "
            "This server provides tools for searching project knowledge, "
            "managing workflows, browser automation, and file operations."
        )
    )
    
    logger.info("✅ FastMCP server created")
    
    # ========================================================================
    # 3. Initialize Foundation Layer
    # ========================================================================
    logger.info("Initializing Foundation layer...")
    
    # 3a. Initialize SessionMapper (generic state persistence)
    try:
        from ouroboros.foundation.session_mapper import SessionMapper
        
        state_dir = base_path / "state"  # New unified state directory
        state_dir.mkdir(parents=True, exist_ok=True)
        
        session_mapper = SessionMapper(state_dir=state_dir)
        logger.info("✅ SessionMapper initialized", extra={"state_dir": str(state_dir)})
    except Exception as e:
        raise ActionableError(
            what_failed="SessionMapper initialization",
            why_failed=str(e),
            how_to_fix="Check state directory permissions and disk space"
        ) from e
    
    # ========================================================================
    # 4. Initialize Subsystems
    # ========================================================================
    
    # 4a. RAG Subsystem (IndexManager)
    logger.info("Initializing RAG subsystem...")
    
    index_manager: Optional[Any] = None
    try:
        from ouroboros.subsystems.rag.index_manager import IndexManager
        
        index_manager = IndexManager(
            config=config.indexes,
            base_path=base_path
        )
        logger.info("✅ IndexManager initialized with %d indexes", 
                   len(index_manager._indexes))
        
        # Auto-build missing indexes (user requirement: "mcp should build indexes if they do not exist")
        # Delegate all health checking, rebuilding, and repair to IndexManager
        result = index_manager.ensure_all_indexes_healthy(auto_build=True)
        
        # Log summary
        if result["indexes_rebuilt"]:
            logger.info("📊 Rebuilt %d index(es): %s", 
                       len(result["indexes_rebuilt"]), 
                       ", ".join(result["indexes_rebuilt"]))
        
        if result["indexes_failed"]:
            logger.warning("⚠️  Failed to rebuild %d index(es): %s", 
                          len(result["indexes_failed"]), 
                          ", ".join(result["indexes_failed"]))
        
        if result["all_healthy"]:
            logger.info("✅ All indexes healthy and operational")
        
    except Exception as e:
        logger.warning("⚠️  IndexManager initialization failed: %s", e)
        logger.warning("    RAG tools will not be available")
        index_manager = None
    
    # 4b. File Watcher (incremental index updates)
    logger.info("Initializing FileWatcher...")
    
    file_watcher: Optional[Any] = None
    try:
        from ouroboros.subsystems.rag.watcher import FileWatcher
        
        if index_manager and config.indexes.file_watcher.enabled:
            # Define path-to-index mappings
            # Map which paths trigger which index updates
            path_mappings = {
                str(base_path / "standards"): ["standards"],  # .praxis-os/standards/ → standards index
            }
            
            # Add code paths from code config
            for source_path in config.indexes.code.source_paths:
                path_mappings[source_path] = ["code", "ast", "graph"]
            
            file_watcher = FileWatcher(
                config=config.indexes.file_watcher,
                index_manager=index_manager,
                path_mappings=path_mappings
            )
            file_watcher.start()
            logger.info("✅ FileWatcher started (hot reload enabled)")
        else:
            if not index_manager:
                logger.info("⚠️  FileWatcher skipped (IndexManager not available)")
            else:
                logger.info("⚠️  FileWatcher disabled in config")
    except Exception as e:
        logger.warning("⚠️  FileWatcher initialization failed: %s", e)
        logger.warning("    Index auto-updates will not be available")
        file_watcher = None
    
    # 4c. Workflow Subsystem (WorkflowEngine)
    logger.info("Initializing Workflow subsystem...")
    
    workflow_engine: Optional[Any] = None
    try:
        from ouroboros.subsystems.workflow.engine import WorkflowEngine
        
        workflow_engine = WorkflowEngine(
            config=config.workflow,
            base_path=base_path,
            session_mapper=session_mapper
        )
        logger.info("✅ WorkflowEngine initialized")
    except Exception as e:
        logger.warning("⚠️  WorkflowEngine initialization failed: %s", e)
        logger.warning("    Workflow tools will not be available")
        workflow_engine = None
    
    # 4d. Browser Subsystem (BrowserManager)
    logger.info("Initializing Browser subsystem...")
    
    browser_manager: Optional[Any] = None
    try:
        from ouroboros.subsystems.browser.manager import BrowserManager

        browser_manager = BrowserManager(
            config=config.browser,
            session_mapper=session_mapper
        )
        logger.info("✅ BrowserManager initialized")
    except Exception as e:
        logger.warning("⚠️  BrowserManager initialization failed: %s", e)
        logger.warning("    Browser tools will not be available")
        browser_manager = None
    
    # ========================================================================
    # 5. Initialize Middleware
    # ========================================================================
    logger.info("Initializing Middleware layer...")
    
    # 5a. QueryTracker (for behavioral metrics)
    query_tracker: Optional[Any] = None
    try:
        from ouroboros.middleware.query_tracker import QueryTracker
        query_tracker = QueryTracker()
        logger.info("✅ QueryTracker initialized (behavioral metrics enabled)")
    except Exception as e:
        logger.warning("⚠️  QueryTracker initialization failed: %s", e)
        # Non-critical, server can function without metrics
    
    # SessionMapper already initialized in Foundation layer (line 148)
    
    # ========================================================================
    # 6. Register Tools via ToolRegistry (Auto-Discovery)
    # ========================================================================
    logger.info("Registering tools via ToolRegistry...")
    
    tools_dir = Path(__file__).parent / "tools"
    
    # Initialize results with safe defaults (P0 fix: prevents crash if registration fails)
    results = {"tools_discovered": 0, "tools_registered": 0, "tools_failed": 0, "details": []}
    
    try:
        registry = ToolRegistry(
            tools_dir=tools_dir,
            mcp_server=mcp,
            dependencies={
                "index_manager": index_manager,
                "workflow_engine": workflow_engine,
                "browser_manager": browser_manager,
                "session_mapper": session_mapper,
                "query_tracker": query_tracker,
                "workspace_root": base_path.parent,  # for pos_filesystem
            }
        )
        
        results = registry.register_all()
        
        logger.info("=" * 60)
        logger.info("Tool Registration Summary:")
        logger.info("  Tools discovered: %d", results["tools_discovered"])
        logger.info("  Tools registered: %d", results["tools_registered"])
        logger.info("  Tools failed: %d", results["tools_failed"])
        logger.info("=" * 60)
        
        tools_failed = results.get("tools_failed", 0)
        if isinstance(tools_failed, (int, str)):
            failed_count = int(tools_failed) if isinstance(tools_failed, str) else tools_failed
            if failed_count > 0:
                logger.warning("⚠️  Some tools failed to register. Check logs above.")
        
        # Log details
        details: Any = results.get("details", [])
        if isinstance(details, list):
            for detail in details:
                if detail.get("status") == "success":
                    logger.info("  ✅ %s (%d tool(s))", 
                               detail.get("function"), detail.get("count"))
                else:
                    logger.warning("  ❌ %s (failed)", detail.get("function"))
        
    except Exception as e:
        raise ActionableError(
            what_failed="Tool registration",
            why_failed=str(e),
            how_to_fix=(
                "Check that tools/ directory exists and contains valid tool modules. "
                "See logs for detailed error information."
            )
        ) from e
    
    # ========================================================================
    # 7. Start Background Tasks
    # ========================================================================
    import asyncio
    
    async def cleanup_task():
        """Background task for automatic session cleanup."""
        logger.info("Starting background cleanup task...")
        
        while True:
            try:
                # Wait 1 hour between cleanups
                await asyncio.sleep(3600)
                
                # Cleanup idle browser sessions (30 min timeout)
                browser_cleaned = session_mapper.cleanup_by_timeout("browser", idle_timeout_minutes=30)
                if browser_cleaned > 0:
                    logger.info("Cleaned up %d idle browser sessions", browser_cleaned)
                
                # Cleanup old completed workflows (30 days)
                workflow_completed = session_mapper.cleanup_by_age("workflow", "completed", older_than_days=30)
                if workflow_completed > 0:
                    logger.info("Cleaned up %d old completed workflows", workflow_completed)
                
                # Cleanup old errors (7 days)
                workflow_errors = session_mapper.cleanup_by_age("workflow", "error", older_than_days=7)
                browser_errors = session_mapper.cleanup_by_age("browser", "error", older_than_days=7)
                if workflow_errors > 0 or browser_errors > 0:
                    logger.info("Cleaned up %d old error sessions", workflow_errors + browser_errors)
                    
            except Exception as e:
                logger.error("Error in cleanup task: %s", e, exc_info=True)
                # Continue running even if cleanup fails
    
    # Schedule cleanup task to run in background
    try:
        asyncio.create_task(cleanup_task())
        logger.info("✅ Background cleanup task scheduled")
    except Exception as e:
        logger.warning("Failed to start cleanup task: %s", e)
        # Non-critical, server can still function
    
    # ========================================================================
    # 8. Server Ready
    # ========================================================================
    logger.info("=" * 60)
    logger.info("✅ Ouroboros MCP Server initialized successfully!")
    logger.info("   Transport mode: %s", transport_mode)
    logger.info("   Tools available: %d", results["tools_registered"])
    logger.info("=" * 60)
    
    return mcp


__all__ = ["create_server"]

