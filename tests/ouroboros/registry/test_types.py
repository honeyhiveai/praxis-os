"""
Unit tests for ouroboros.registry.types.

Tests type definitions including:
    - ParameterInfo creation and annotation parsing
    - ToolDefinition and MCP schema generation
    - ToolMetadata tracking
"""

import inspect
from typing import Literal

import pytest
from ouroboros.registry.types import ParameterInfo, ToolDefinition, ToolMetadata


class TestParameterInfo:
    """Test ParameterInfo class."""

    def test_parameter_info_creation(self):
        """ParameterInfo should initialize with basic fields."""
        param = ParameterInfo(
            name="query",
            type_hint="str",
            required=True,
            description="Search query",
        )

        assert param.name == "query"
        assert param.type_hint == "str"
        assert param.required is True
        assert param.description == "Search query"

    def test_parameter_info_with_default(self):
        """ParameterInfo should support default values."""
        param = ParameterInfo(
            name="limit",
            type_hint="int",
            required=False,
            default=10,
        )

        assert param.required is False
        assert param.default == 10

    def test_parameter_info_with_enum(self):
        """ParameterInfo should support enum values."""
        param = ParameterInfo(
            name="action",
            type_hint="Literal",
            required=True,
            enum_values=["read", "write", "delete"],
        )

        assert param.enum_values == ["read", "write", "delete"]

    def test_from_annotation_required(self):
        """from_annotation() should detect required parameters."""
        param = ParameterInfo.from_annotation(
            name="query",
            annotation=str,
            default=inspect.Parameter.empty,
            description="Search query",
        )

        assert param.name == "query"
        assert param.type_hint == "str"
        assert param.required is True

    def test_from_annotation_with_default(self):
        """from_annotation() should detect default values."""
        param = ParameterInfo.from_annotation(
            name="limit",
            annotation=int,
            default=10,
        )

        assert param.required is False
        assert param.default == 10

    def test_from_annotation_literal(self):
        """from_annotation() should extract Literal enum values."""
        param = ParameterInfo.from_annotation(
            name="action",
            annotation=Literal["read", "write"],
            default=inspect.Parameter.empty,
        )

        assert param.enum_values == ["read", "write"]

    def test_extract_literal_values(self):
        """_extract_literal_values() should extract enum values."""
        values = ParameterInfo._extract_literal_values(Literal["a", "b", "c"])
        assert values == ["a", "b", "c"]

    def test_extract_literal_values_non_literal(self):
        """_extract_literal_values() should return empty list for non-Literal."""
        values = ParameterInfo._extract_literal_values(str)
        assert values == []


class TestToolDefinition:
    """Test ToolDefinition class."""

    def test_tool_definition_creation(self):
        """ToolDefinition should initialize with basic fields."""

        def dummy_tool(query: str) -> dict:
            return {"result": query}

        tool = ToolDefinition(
            name="test_tool",
            description="Test tool",
            parameters=[],
            function=dummy_tool,
        )

        assert tool.name == "test_tool"
        assert tool.description == "Test tool"
        assert callable(tool.function)

    def test_tool_definition_with_parameters(self):
        """ToolDefinition should support parameters."""
        param = ParameterInfo(
            name="query",
            type_hint="str",
            required=True,
        )

        tool = ToolDefinition(
            name="test_tool",
            description="Test",
            parameters=[param],
            function=lambda query: {"result": query},
        )

        assert len(tool.parameters) == 1
        assert tool.parameters[0].name == "query"

    def test_to_mcp_schema_basic(self):
        """to_mcp_schema() should generate basic MCP schema."""
        tool = ToolDefinition(
            name="test_tool",
            description="Test tool",
            parameters=[],
            function=lambda: {},
        )

        schema = tool.to_mcp_schema()

        assert schema["name"] == "test_tool"
        assert schema["description"] == "Test tool"
        assert "inputSchema" in schema
        assert schema["inputSchema"]["type"] == "object"

    def test_to_mcp_schema_with_required_param(self):
        """to_mcp_schema() should include required parameters."""
        param = ParameterInfo(
            name="query",
            type_hint="str",
            required=True,
            description="Search query",
        )

        tool = ToolDefinition(
            name="search_tool",
            description="Search",
            parameters=[param],
            function=lambda query: {},
        )

        schema = tool.to_mcp_schema()

        assert "query" in schema["inputSchema"]["properties"]
        assert "query" in schema["inputSchema"]["required"]
        assert schema["inputSchema"]["properties"]["query"]["type"] == "string"

    def test_to_mcp_schema_with_optional_param(self):
        """to_mcp_schema() should handle optional parameters."""
        param = ParameterInfo(
            name="limit",
            type_hint="int",
            required=False,
            default=10,
        )

        tool = ToolDefinition(
            name="test_tool",
            description="Test",
            parameters=[param],
            function=lambda limit=10: {},
        )

        schema = tool.to_mcp_schema()

        assert "limit" in schema["inputSchema"]["properties"]
        assert "limit" not in schema["inputSchema"]["required"]
        assert schema["inputSchema"]["properties"]["limit"]["default"] == 10

    def test_to_mcp_schema_with_enum(self):
        """to_mcp_schema() should include enum values for Literal types."""
        param = ParameterInfo(
            name="action",
            type_hint="Literal",
            required=True,
            enum_values=["read", "write"],
        )

        tool = ToolDefinition(
            name="file_tool",
            description="File operations",
            parameters=[param],
            function=lambda action: {},
        )

        schema = tool.to_mcp_schema()

        assert "action" in schema["inputSchema"]["properties"]
        assert schema["inputSchema"]["properties"]["action"]["enum"] == [
            "read",
            "write",
        ]

    def test_python_type_to_json_type(self):
        """_python_type_to_json_type() should map Python types to JSON types."""
        assert ToolDefinition._python_type_to_json_type("str") == "string"
        assert ToolDefinition._python_type_to_json_type("int") == "integer"
        assert ToolDefinition._python_type_to_json_type("float") == "number"
        assert ToolDefinition._python_type_to_json_type("bool") == "boolean"
        assert ToolDefinition._python_type_to_json_type("dict") == "object"
        assert ToolDefinition._python_type_to_json_type("list") == "array"
        assert ToolDefinition._python_type_to_json_type("unknown") == "string"


class TestToolMetadata:
    """Test ToolMetadata class."""

    def test_tool_metadata_creation(self):
        """ToolMetadata should initialize with basic fields."""
        meta = ToolMetadata(
            name="test_tool",
            module="test_module",
            file_path="/path/to/tool.py",
        )

        assert meta.name == "test_tool"
        assert meta.module == "test_module"
        assert meta.file_path == "/path/to/tool.py"
        assert meta.registered is False
        assert meta.error is None

    def test_tool_metadata_with_registration(self):
        """ToolMetadata should track registration status."""
        meta = ToolMetadata(
            name="test_tool",
            module="test_module",
            file_path="/path/to/tool.py",
            registered=True,
        )

        assert meta.registered is True

    def test_tool_metadata_with_error(self):
        """ToolMetadata should track registration errors."""
        meta = ToolMetadata(
            name="test_tool",
            module="test_module",
            file_path="/path/to/tool.py",
            error="Import failed",
        )

        assert meta.error == "Import failed"


class TestIntegration:
    """Test integration between types."""

    def test_complete_tool_definition_to_schema(self):
        """Complete tool definition should generate valid MCP schema."""
        params = [
            ParameterInfo(
                name="action",
                type_hint="Literal",
                required=True,
                enum_values=["search", "index"],
            ),
            ParameterInfo(
                name="query",
                type_hint="str",
                required=True,
            ),
            ParameterInfo(
                name="limit",
                type_hint="int",
                required=False,
                default=10,
            ),
        ]

        tool = ToolDefinition(
            name="pos_search_project",
            description="Search project standards and code",
            parameters=params,
            function=lambda action, query, limit=10: {},
        )

        schema = tool.to_mcp_schema()

        # Validate schema structure
        assert schema["name"] == "pos_search_project"
        assert len(schema["inputSchema"]["properties"]) == 3
        assert len(schema["inputSchema"]["required"]) == 2
        assert "action" in schema["inputSchema"]["required"]
        assert "query" in schema["inputSchema"]["required"]
        assert "limit" not in schema["inputSchema"]["required"]
        assert schema["inputSchema"]["properties"]["action"]["enum"] == [
            "search",
            "index",
        ]
