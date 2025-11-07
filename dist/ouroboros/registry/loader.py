"""
Tool registry with automatic discovery and registration.

Scans tools/ directory for Python files and automatically:
    - Extracts function signatures with type hints
    - Parses docstrings for descriptions
    - Detects Literal type hints for enums
    - Generates MCP schemas
    - Registers tools with FastMCP

Example Usage:
    >>> from pathlib import Path
    >>> from ouroboros.registry.loader import ToolRegistry
    >>> 
    >>> registry = ToolRegistry(tools_dir=Path("ouroboros/tools"))
    >>> tools = registry.discover_tools()
    >>> print(f"Discovered {len(tools)} tools")
    >>> 
    >>> # Register with FastMCP
    >>> for tool in tools:
    ...     registry.register_tool(mcp, tool)

See Also:
    - types: ToolDefinition, ParameterInfo for tool metadata
"""

import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Any, Optional

from ouroboros.utils.errors import ActionableError
from ouroboros.utils.logging import get_logger

from .types import ParameterInfo, ToolDefinition, ToolMetadata

logger = get_logger("ouroboros.registry")


class ToolRegistryError(ActionableError):
    """Tool registry error with remediation."""

    pass


class ToolRegistry:
    """
    Tool registry with automatic discovery and registration.

    Scans tools/ directory for Python modules containing tool functions
    and automatically generates MCP schemas for registration with FastMCP.

    Key Features:
        - Auto-discovery: Scans tools/ directory for .py files
        - Type hint extraction: Parses function signatures
        - Literal enum detection: Extracts enum values from Literal[] types
        - Docstring parsing: Extracts descriptions
        - MCP schema generation: Converts to FastMCP format

    Example:
        >>> from pathlib import Path
        >>> registry = ToolRegistry(tools_dir=Path("ouroboros/tools"))
        >>> 
        >>> # Discover all tools
        >>> tools = registry.discover_tools()
        >>> print(f"Found {len(tools)} tools")
        >>> 
        >>> # Register with FastMCP
        >>> for tool in tools:
        ...     registry.register_tool(mcp_server, tool)

    Discovery Rules:
        - Scans all .py files in tools_dir (non-recursive)
        - Skips __init__.py and files starting with _
        - Looks for functions with type hints
        - Requires function docstrings for descriptions
        - Validates Literal type hints for action parameters

    Attributes:
        tools_dir (Path): Directory to scan for tools
        discovered_tools (list[ToolDefinition]): Discovered tools
        metadata (list[ToolMetadata]): Tool metadata
    """

    def __init__(self, tools_dir: Path) -> None:
        """
        Initialize tool registry.

        Args:
            tools_dir: Directory containing tool modules

        Example:
            >>> registry = ToolRegistry(tools_dir=Path("ouroboros/tools"))
        """
        self.tools_dir = tools_dir
        self.discovered_tools: list[ToolDefinition] = []
        self.metadata: list[ToolMetadata] = []

    def discover_tools(self) -> list[ToolDefinition]:
        """
        Discover all tools in tools_dir.

        Scans directory for Python files, imports modules, extracts
        function signatures, and creates ToolDefinition objects.

        Returns:
            list[ToolDefinition]: Discovered tool definitions

        Raises:
            ToolRegistryError: If tools_dir does not exist

        Example:
            >>> registry = ToolRegistry(tools_dir=Path("ouroboros/tools"))
            >>> tools = registry.discover_tools()
            >>> for tool in tools:
            ...     print(f"Found: {tool.name}")

        Discovery Process:
            1. Scan tools_dir for .py files
            2. Import each module
            3. Find callable functions with type hints
            4. Extract function signature and docstring
            5. Parse parameters with Literal enum detection
            6. Create ToolDefinition
            7. Add to discovered_tools

        Skipped Files:
            - __init__.py
            - Files starting with _ (private modules)
            - Files without .py extension
        """
        if not self.tools_dir.exists():
            raise ToolRegistryError(
                what_failed="Tool discovery failed",
                why_failed=f"Tools directory does not exist: {self.tools_dir}",
                how_to_fix=f"Create directory: mkdir -p {self.tools_dir}",
            )

        logger.info(f"Discovering tools in {self.tools_dir}")

        # Scan for Python files
        tool_files = [
            f
            for f in self.tools_dir.glob("*.py")
            if f.name != "__init__.py" and not f.name.startswith("_")
        ]

        for tool_file in tool_files:
            try:
                tool = self._load_tool_from_file(tool_file)
                if tool:
                    self.discovered_tools.append(tool)
                    self.metadata.append(
                        ToolMetadata(
                            name=tool.name,
                            module=tool.module_path,
                            file_path=str(tool_file),
                            registered=False,
                        )
                    )
                    logger.info(f"✅ Discovered tool: {tool.name}")
            except Exception as e:
                logger.error(
                    f"❌ Failed to load tool from {tool_file}: {e}",
                    exc_info=True,
                )
                self.metadata.append(
                    ToolMetadata(
                        name=tool_file.stem,
                        module=tool_file.stem,
                        file_path=str(tool_file),
                        registered=False,
                        error=str(e),
                    )
                )

        logger.info(f"Discovered {len(self.discovered_tools)} tools")
        return self.discovered_tools

    def _load_tool_from_file(self, file_path: Path) -> Optional[ToolDefinition]:
        """
        Load tool definition from Python file.

        Args:
            file_path: Path to Python file

        Returns:
            ToolDefinition: Tool definition if valid tool found, None otherwise

        Process:
            1. Import module from file
            2. Find main tool function (looks for function with same name as file)
            3. Extract signature and docstring
            4. Parse parameters with type hints
            5. Create ToolDefinition

        Example:
            >>> registry = ToolRegistry(tools_dir=Path("ouroboros/tools"))
            >>> tool = registry._load_tool_from_file(Path("ouroboros/tools/pos_search_project.py"))
            >>> assert tool.name == "pos_search_project"
        """
        # Import module
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if not spec or not spec.loader:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Look for function with same name as file (e.g., pos_search_project.py → pos_search_project())
        if not hasattr(module, module_name):
            logger.warning(
                f"No function '{module_name}' found in {file_path.name}"
            )
            return None

        function = getattr(module, module_name)
        if not callable(function):
            logger.warning(f"'{module_name}' in {file_path.name} is not callable")
            return None

        # Extract function signature
        signature = inspect.signature(function)
        parameters = self._extract_parameters(signature)

        # Extract docstring
        description = inspect.getdoc(function) or f"{module_name} tool"

        return ToolDefinition(
            name=module_name,
            description=description.split("\n")[0],  # First line of docstring
            parameters=parameters,
            function=function,
            module_path=f"ouroboros.tools.{module_name}",
        )

    def _extract_parameters(
        self, signature: inspect.Signature
    ) -> list[ParameterInfo]:
        """
        Extract parameters from function signature.

        Args:
            signature: Function signature from inspect.signature()

        Returns:
            list[ParameterInfo]: Parameter information

        Process:
            1. Iterate through signature parameters
            2. Extract type annotation
            3. Detect Literal type hints for enums
            4. Extract default values
            5. Create ParameterInfo

        Example:
            >>> from typing import Literal
            >>> import inspect
            >>> 
            >>> def tool(action: Literal["read", "write"], path: str = "default"):
            ...     pass
            >>> 
            >>> sig = inspect.signature(tool)
            >>> params = registry._extract_parameters(sig)
            >>> assert params[0].enum_values == ["read", "write"]
            >>> assert params[1].default == "default"
        """
        parameters = []

        for param_name, param in signature.parameters.items():
            # Skip self, cls, *args, **kwargs
            if param_name in ("self", "cls") or param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue

            # Get type annotation
            annotation = param.annotation
            if annotation is inspect.Parameter.empty:
                annotation = Any  # No type hint, default to Any

            # Extract parameter info
            param_info = ParameterInfo.from_annotation(
                name=param_name,
                annotation=annotation,
                default=param.default,
                description=f"{param_name} parameter",
            )

            parameters.append(param_info)

        return parameters

    def register_tool(self, mcp: Any, tool: ToolDefinition) -> None:
        """
        Register tool with FastMCP server.

        Args:
            mcp: FastMCP server instance
            tool: Tool definition to register

        Example:
            >>> from fastmcp import FastMCP
            >>> mcp = FastMCP("test")
            >>> registry = ToolRegistry(tools_dir=Path("ouroboros/tools"))
            >>> tools = registry.discover_tools()
            >>> for tool in tools:
            ...     registry.register_tool(mcp, tool)

        Registration Process:
            1. Generate MCP schema from tool definition
            2. Register with FastMCP using @mcp.tool() decorator
            3. Mark tool as registered in metadata
            4. Log success/failure

        MCP Registration:
            Uses FastMCP's tool registration API:
                @mcp.tool()
                def tool_name(**kwargs):
                    return tool.function(**kwargs)
        """
        try:
            # Get MCP schema
            schema = tool.to_mcp_schema()

            # Register with FastMCP
            mcp.tool(
                name=schema["name"],
                description=schema["description"],
            )(tool.function)

            # Update metadata
            for meta in self.metadata:
                if meta.name == tool.name:
                    meta.registered = True
                    break

            logger.info(f"✅ Registered tool: {tool.name}")

        except Exception as e:
            logger.error(f"❌ Failed to register tool {tool.name}: {e}", exc_info=True)

            # Update metadata with error
            for meta in self.metadata:
                if meta.name == tool.name:
                    meta.error = str(e)
                    break

            raise ToolRegistryError(
                what_failed=f"Tool registration failed: {tool.name}",
                why_failed=str(e),
                how_to_fix=f"Check tool definition in {tool.module_path}",
            ) from e

    def get_tool_count(self) -> int:
        """
        Get count of discovered tools.

        Returns:
            int: Number of discovered tools

        Example:
            >>> registry = ToolRegistry(tools_dir=Path("ouroboros/tools"))
            >>> registry.discover_tools()
            >>> print(f"Found {registry.get_tool_count()} tools")
        """
        return len(self.discovered_tools)

    def get_registered_count(self) -> int:
        """
        Get count of registered tools.

        Returns:
            int: Number of successfully registered tools

        Example:
            >>> registry = ToolRegistry(tools_dir=Path("ouroboros/tools"))
            >>> registry.discover_tools()
            >>> for tool in registry.discovered_tools:
            ...     registry.register_tool(mcp, tool)
            >>> print(f"Registered {registry.get_registered_count()} tools")
        """
        return sum(1 for meta in self.metadata if meta.registered)

    def get_registration_report(self) -> dict[str, Any]:
        """
        Get registration report with success/failure details.

        Returns:
            dict: Registration report

        Example:
            >>> registry = ToolRegistry(tools_dir=Path("ouroboros/tools"))
            >>> registry.discover_tools()
            >>> report = registry.get_registration_report()
            >>> print(f"Success: {report['success_count']}/{report['total_count']}")

        Report Structure:
            {
                "total_count": 5,
                "success_count": 4,
                "failure_count": 1,
                "tools": [
                    {
                        "name": "tool_name",
                        "registered": true,
                        "error": null
                    }
                ]
            }
        """
        return {
            "total_count": len(self.metadata),
            "success_count": self.get_registered_count(),
            "failure_count": len([m for m in self.metadata if m.error]),
            "tools": [
                {
                    "name": meta.name,
                    "module": meta.module,
                    "registered": meta.registered,
                    "error": meta.error,
                }
                for meta in self.metadata
            ],
        }


__all__ = ["ToolRegistry", "ToolRegistryError"]

