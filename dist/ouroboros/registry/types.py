"""
Type definitions for tool registry.

Provides data classes for tool metadata extracted during discovery:
    - ToolDefinition: Complete tool definition with signature
    - ToolMetadata: Tool metadata (name, description, parameters)
    - ParameterInfo: Parameter information from type hints

Example Usage:
    >>> from ouroboros.registry.types import ToolDefinition, ParameterInfo
    >>> 
    >>> param = ParameterInfo(
    ...     name="query",
    ...     type_hint="str",
    ...     required=True,
    ...     default=None,
    ...     description="Search query"
    ... )
    >>> 
    >>> tool = ToolDefinition(
    ...     name="pos_search_project",
    ...     description="Search project standards",
    ...     parameters=[param],
    ...     function=search_function
    ... )

See Also:
    - loader: ToolRegistry for tool discovery
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Optional, get_args, get_origin


@dataclass
class ParameterInfo:
    """
    Information about a function parameter extracted from type hints.

    Attributes:
        name (str): Parameter name
        type_hint (str): Type hint as string (e.g., "str", "int", "Literal['a', 'b']")
        required (bool): Whether parameter is required
        default (Any): Default value (None if required)
        description (str): Parameter description from docstring
        enum_values (list[str]): Enum values if Literal type hint
    """

    name: str
    type_hint: str
    required: bool
    default: Any = None
    description: str = ""
    enum_values: list[str] = field(default_factory=list)

    @classmethod
    def from_annotation(
        cls,
        name: str,
        annotation: Any,
        default: Any,
        description: str = "",
    ) -> "ParameterInfo":
        """
        Create ParameterInfo from function parameter annotation.

        Args:
            name: Parameter name
            annotation: Type annotation (from __annotations__)
            default: Default value (inspect.Parameter.empty if required)
            description: Parameter description from docstring

        Returns:
            ParameterInfo: Parameter information

        Example:
            >>> from typing import Literal
            >>> import inspect
            >>> 
            >>> param = ParameterInfo.from_annotation(
            ...     name="action",
            ...     annotation=Literal["read", "write"],
            ...     default=inspect.Parameter.empty,
            ...     description="Action to perform"
            ... )
            >>> assert param.enum_values == ["read", "write"]

        Supported Types:
            - str, int, float, bool: Basic types
            - Literal["a", "b"]: Enum values (extracted to enum_values)
            - Optional[str]: Optional types (required=False)
            - dict, list: Complex types
        """
        import inspect

        # Check if required (no default value)
        required = default is inspect.Parameter.empty

        # Extract type hint string
        type_hint = cls._format_type_hint(annotation)

        # Extract enum values from Literal type hints
        enum_values = cls._extract_literal_values(annotation)

        return cls(
            name=name,
            type_hint=type_hint,
            required=required,
            default=None if required else default,
            description=description,
            enum_values=enum_values,
        )

    @staticmethod
    def _format_type_hint(annotation: Any) -> str:
        """
        Format type annotation as string.

        Args:
            annotation: Type annotation

        Returns:
            str: Formatted type hint (e.g., "str", "Literal['a', 'b']")

        Example:
            >>> from typing import Literal
            >>> ParameterInfo._format_type_hint(str)
            'str'
            >>> ParameterInfo._format_type_hint(Literal["a", "b"])
            "Literal['a', 'b']"
        """
        if hasattr(annotation, "__name__"):
            name = annotation.__name__
            return name if isinstance(name, str) else str(annotation)
        return str(annotation)

    @staticmethod
    def _extract_literal_values(annotation: Any) -> list[str]:
        """
        Extract enum values from Literal type hint.

        Args:
            annotation: Type annotation

        Returns:
            list[str]: Enum values if Literal, empty list otherwise

        Example:
            >>> from typing import Literal
            >>> ParameterInfo._extract_literal_values(Literal["a", "b", "c"])
            ['a', 'b', 'c']
            >>> ParameterInfo._extract_literal_values(str)
            []
        """
        # Check if Literal type hint
        if get_origin(annotation) is Literal:
            return list(get_args(annotation))
        return []


@dataclass
class ToolDefinition:
    """
    Complete tool definition for MCP registration.

    Attributes:
        name (str): Tool name (function name)
        description (str): Tool description from docstring
        parameters (list[ParameterInfo]): Function parameters
        function (Callable): Tool function
        module_path (str): Module path (e.g., "ouroboros.tools.pos_search_project")
        return_type (str): Return type hint
    """

    name: str
    description: str
    parameters: list[ParameterInfo]
    function: Callable
    module_path: str = ""
    return_type: str = "dict[str, Any]"

    def to_mcp_schema(self) -> dict[str, Any]:
        """
        Convert tool definition to MCP tool schema.

        Returns:
            dict: MCP tool schema for FastMCP registration

        Example:
            >>> tool = ToolDefinition(
            ...     name="pos_search_project",
            ...     description="Search project",
            ...     parameters=[
            ...         ParameterInfo(
            ...             name="query",
            ...             type_hint="str",
            ...             required=True,
            ...             description="Search query"
            ...         )
            ...     ],
            ...     function=lambda query: {"result": query}
            ... )
            >>> schema = tool.to_mcp_schema()
            >>> assert schema["name"] == "pos_search_project"
            >>> assert "query" in schema["inputSchema"]["properties"]

        MCP Schema Format:
            {
                "name": "tool_name",
                "description": "Tool description",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "param_name": {
                            "type": "string",
                            "description": "Param description",
                            "enum": ["value1", "value2"]  # If Literal
                        }
                    },
                    "required": ["required_param1", "required_param2"]
                }
            }
        """
        properties = {}
        required = []

        for param in self.parameters:
            param_schema: dict[str, Any] = {
                "type": self._python_type_to_json_type(param.type_hint),
                "description": param.description or f"{param.name} parameter",
            }

            # Add enum values if Literal type hint
            if param.enum_values:
                param_schema["enum"] = param.enum_values

            # Add default value if provided
            if not param.required and param.default is not None:
                param_schema["default"] = param.default

            properties[param.name] = param_schema

            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    @staticmethod
    def _python_type_to_json_type(type_hint: str) -> str:
        """
        Convert Python type hint to JSON schema type.

        Args:
            type_hint: Python type hint string

        Returns:
            str: JSON schema type

        Mapping:
            - str → "string"
            - int → "integer"
            - float → "number"
            - bool → "boolean"
            - dict → "object"
            - list → "array"
            - Any → "string" (default)
        """
        type_mapping = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "dict": "object",
            "list": "array",
        }
        return type_mapping.get(type_hint, "string")


@dataclass
class ToolMetadata:
    """
    Tool metadata for registry tracking.

    Attributes:
        name (str): Tool name
        module (str): Module name
        file_path (str): File path
        registered (bool): Whether tool is registered with MCP
        error (Optional[str]): Registration error if any
    """

    name: str
    module: str
    file_path: str
    registered: bool = False
    error: Optional[str] = None


__all__ = ["ParameterInfo", "ToolDefinition", "ToolMetadata"]

