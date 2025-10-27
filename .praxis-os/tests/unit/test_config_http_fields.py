"""
Unit tests for HTTP configuration fields.

Tests MCPConfig HTTP fields and validation.
"""

from pathlib import Path

import pytest

from mcp_server.config.validator import ConfigValidator
from mcp_server.models.config import MCPConfig, RAGConfig, ServerConfig


@pytest.fixture
def temp_config_paths(tmp_path):
    """Create temporary config directories."""
    # Create .praxis-os directory
    praxis_os_dir = tmp_path / ".praxis-os"
    praxis_os_dir.mkdir()

    # Create required directories in project root (parent of .praxis-os)
    (tmp_path / "standards").mkdir()
    (tmp_path / "usage").mkdir()
    (tmp_path / "workflows").mkdir()
    (tmp_path / ".cache").mkdir()

    return praxis_os_dir


@pytest.fixture
def base_config(temp_config_paths):
    """Create valid base ServerConfig."""
    rag = RAGConfig(
        standards_path="standards",
        workflows_path="workflows",
        index_path=".cache/vector_index",
    )
    mcp = MCPConfig()
    return ServerConfig(base_path=temp_config_paths, rag=rag, mcp=mcp)


class TestMCPConfigDefaults:
    """Test MCPConfig default values for HTTP fields."""

    def test_default_http_port(self):
        """Test http_port has correct default value."""
        config = MCPConfig()
        assert config.http_port == 4242

    def test_default_http_host(self):
        """Test http_host has correct default value."""
        config = MCPConfig()
        assert config.http_host == "127.0.0.1"

    def test_default_http_path(self):
        """Test http_path has correct default value."""
        config = MCPConfig()
        assert config.http_path == "/mcp"

    def test_can_override_defaults(self):
        """Test HTTP fields can be overridden."""
        config = MCPConfig(http_port=5000, http_host="127.0.0.1", http_path="/custom")

        assert config.http_port == 5000
        assert config.http_host == "127.0.0.1"
        assert config.http_path == "/custom"


class TestConfigValidation:
    """Test configuration validation for HTTP fields."""

    def test_valid_config_passes(self, base_config):
        """Test valid configuration passes validation."""
        errors = ConfigValidator.validate(base_config)
        assert errors == []

    def test_http_port_too_low(self, base_config):
        """Test validation fails for port < 1024."""
        base_config.mcp.http_port = 1023

        errors = ConfigValidator.validate(base_config)

        assert len(errors) > 0
        assert any("http_port" in error and "1024-65535" in error for error in errors)

    def test_http_port_too_high(self, base_config):
        """Test validation fails for port > 65535."""
        base_config.mcp.http_port = 65536

        errors = ConfigValidator.validate(base_config)

        assert len(errors) > 0
        assert any("http_port" in error and "1024-65535" in error for error in errors)

    def test_http_port_valid_range(self, base_config):
        """Test validation passes for valid port range."""
        # Test boundary values
        for port in [1024, 4242, 65535]:
            base_config.mcp.http_port = port
            errors = ConfigValidator.validate(base_config)
            # Should not have http_port errors (may have other unrelated errors)
            assert not any("http_port" in error for error in errors)

    def test_http_host_must_be_localhost(self, base_config):
        """Test http_host must be 127.0.0.1 for security."""
        base_config.mcp.http_host = "0.0.0.0"

        errors = ConfigValidator.validate(base_config)

        assert len(errors) > 0
        assert any("http_host" in error and "127.0.0.1" in error for error in errors)

    def test_http_host_localhost_passes(self, base_config):
        """Test http_host='127.0.0.1' passes validation."""
        base_config.mcp.http_host = "127.0.0.1"

        errors = ConfigValidator.validate(base_config)

        # Should not have http_host errors
        assert not any("http_host" in error for error in errors)

    def test_http_path_must_start_with_slash(self, base_config):
        """Test http_path must start with '/'."""
        base_config.mcp.http_path = "mcp"

        errors = ConfigValidator.validate(base_config)

        assert len(errors) > 0
        assert any("http_path" in error and "/" in error for error in errors)

    def test_http_path_with_slash_passes(self, base_config):
        """Test http_path starting with '/' passes validation."""
        for path in ["/", "/mcp", "/custom/path"]:
            base_config.mcp.http_path = path
            errors = ConfigValidator.validate(base_config)
            # Should not have http_path errors
            assert not any("http_path" in error for error in errors)


class TestBackwardCompatibility:
    """Test backward compatibility with existing configs."""

    def test_config_without_http_fields_uses_defaults(self, temp_config_paths):
        """Test config without HTTP fields still works (uses defaults)."""
        # Create config without specifying HTTP fields
        rag = RAGConfig(
            standards_path="standards",
            workflows_path="workflows",
            index_path=".cache/vector_index",
        )
        # MCPConfig() will use default HTTP values
        mcp = MCPConfig()
        config = ServerConfig(base_path=temp_config_paths, rag=rag, mcp=mcp)

        # Should validate successfully with defaults
        errors = ConfigValidator.validate(config)
        assert errors == []

        # Check defaults are applied
        assert config.mcp.http_port == 4242
        assert config.mcp.http_host == "127.0.0.1"
        assert config.mcp.http_path == "/mcp"


class TestDocstrings:
    """Verify code quality requirements."""

    def test_mcpconfig_has_docstring(self):
        """Test MCPConfig class has docstring."""
        assert MCPConfig.__doc__ is not None
        assert "MCP server" in MCPConfig.__doc__

    def test_validator_has_docstring(self):
        """Test ConfigValidator has docstring."""
        assert ConfigValidator.__doc__ is not None
        assert ConfigValidator.validate.__doc__ is not None
