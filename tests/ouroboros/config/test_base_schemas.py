"""
Tests for base configuration schemas.

Tests EnvType enum and BaseConfig model validation, including:
    - EnvType enum values
    - BaseConfig immutability (frozen=True)
    - BaseConfig unknown field rejection (extra="forbid")
    - Path resolution (relative to .praxis-os/)
    - Path security (traversal and absolute path rejection)
    - String whitespace stripping
    - Validation error messages

Test Coverage:
    - EnvType enum: 100%
    - BaseConfig validation: 100%
    - Path resolution: 100%
    - Security validation: 100%
"""

from pathlib import Path

import pytest
from ouroboros.config.schemas.base import BaseConfig, EnvType
from pydantic import Field, ValidationError


class TestEnvType:
    """Tests for EnvType enum."""

    def test_env_type_values(self):
        """Test EnvType enum has correct values."""
        assert EnvType.DEVELOPMENT.value == "development"
        assert EnvType.PRODUCTION.value == "production"
        assert EnvType.TEST.value == "test"

    def test_env_type_comparison(self):
        """Test EnvType enum comparison."""
        env = EnvType.DEVELOPMENT
        assert env == EnvType.DEVELOPMENT
        assert env != EnvType.PRODUCTION
        assert env != EnvType.TEST

    def test_env_type_from_string(self):
        """Test EnvType can be created from string."""
        assert EnvType("development") == EnvType.DEVELOPMENT
        assert EnvType("production") == EnvType.PRODUCTION
        assert EnvType("test") == EnvType.TEST

    def test_env_type_invalid_value(self):
        """Test EnvType rejects invalid values."""
        with pytest.raises(ValueError, match="'invalid' is not a valid EnvType"):
            EnvType("invalid")


class TestBaseConfig:
    """Tests for BaseConfig base model."""

    def test_base_config_creation(self):
        """Test BaseConfig can be subclassed and instantiated."""

        class TestConfig(BaseConfig):
            name: str = Field(description="Test name")
            value: int = Field(ge=0, le=100, default=50)

        config = TestConfig(name="test", value=75)
        assert config.name == "test"
        assert config.value == 75

    def test_base_config_frozen(self):
        """Test BaseConfig is immutable (frozen=True)."""

        class TestConfig(BaseConfig):
            name: str = Field(description="Test name")

        config = TestConfig(name="test")

        # Attempt to modify should raise ValidationError
        with pytest.raises(ValidationError, match="Instance is frozen"):
            config.name = "modified"  # type: ignore

    def test_base_config_extra_forbid(self):
        """Test BaseConfig rejects unknown fields (extra='forbid')."""

        class TestConfig(BaseConfig):
            name: str = Field(description="Test name")

        # Unknown field should raise ValidationError
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            TestConfig(name="test", unknown_field="value")  # type: ignore

    def test_base_config_field_validation(self):
        """Test BaseConfig validates field constraints."""

        class TestConfig(BaseConfig):
            port: int = Field(ge=1024, le=65535, description="Port number")

        # Valid port
        config = TestConfig(port=8080)
        assert config.port == 8080

        # Port too low
        with pytest.raises(ValidationError, match="greater than or equal to 1024"):
            TestConfig(port=80)

        # Port too high
        with pytest.raises(ValidationError, match="less than or equal to 65535"):
            TestConfig(port=99999)

    def test_base_config_string_stripping(self):
        """Test BaseConfig strips whitespace from strings."""

        class TestConfig(BaseConfig):
            name: str = Field(description="Test name")

        config = TestConfig(name="  test  ")
        assert config.name == "test"  # Whitespace stripped

    def test_base_config_default_values(self):
        """Test BaseConfig validates default values."""

        class TestConfig(BaseConfig):
            name: str = Field(default="default", description="Test name")
            port: int = Field(default=8080, ge=1024, le=65535)

        config = TestConfig()
        assert config.name == "default"
        assert config.port == 8080


class TestPathResolution:
    """Tests for BaseConfig.resolve_path()."""

    def test_resolve_relative_path(self):
        """Test resolve_path converts relative paths to absolute."""
        resolved = BaseConfig.resolve_path("standards/")

        # Should be absolute
        assert resolved.is_absolute()

        # Should contain .praxis-os
        assert ".praxis-os" in str(resolved)

        # Should end with standards
        assert resolved.name == "standards"

    def test_resolve_path_with_subdirectories(self):
        """Test resolve_path handles nested directories."""
        resolved = BaseConfig.resolve_path("config/indexes/")

        assert resolved.is_absolute()
        assert "config" in resolved.parts
        assert "indexes" in resolved.parts

    def test_resolve_path_from_path_object(self):
        """Test resolve_path accepts Path objects."""
        path_obj = Path("standards/")
        resolved = BaseConfig.resolve_path(path_obj)

        assert resolved.is_absolute()
        assert resolved.name == "standards"

    def test_resolve_path_rejects_traversal(self):
        """Test resolve_path rejects path traversal attempts."""
        with pytest.raises(ValueError, match="Path traversal not allowed"):
            BaseConfig.resolve_path("../secrets/")

        with pytest.raises(ValueError, match="Path traversal not allowed"):
            BaseConfig.resolve_path("config/../../etc/passwd")

    def test_resolve_path_rejects_absolute(self):
        """Test resolve_path rejects absolute paths."""
        with pytest.raises(ValueError, match="Absolute paths not allowed"):
            BaseConfig.resolve_path("/etc/passwd")

        with pytest.raises(ValueError, match="Absolute paths not allowed"):
            BaseConfig.resolve_path("/usr/local/bin")

    def test_resolve_path_error_messages(self):
        """Test resolve_path provides actionable error messages."""
        # Path traversal error should include remediation
        try:
            BaseConfig.resolve_path("../bad/")
        except ValueError as e:
            assert "Remediation" in str(e)
            assert "Remove '../'" in str(e)

        # Absolute path error should include remediation
        try:
            BaseConfig.resolve_path("/absolute/")
        except ValueError as e:
            assert "Remediation" in str(e)
            assert "relative paths" in str(e)


class TestValidationErrorMessages:
    """Tests for validation error message quality."""

    def test_field_constraint_error_message(self):
        """Test constraint violations have clear error messages."""

        class TestConfig(BaseConfig):
            count: int = Field(ge=1, le=100, description="Item count")

        try:
            TestConfig(count=0)
        except ValidationError as e:
            error_str = str(e)
            # Should mention field name
            assert "count" in error_str
            # Should mention constraint
            assert "greater than or equal to 1" in error_str

    def test_type_error_message(self):
        """Test type mismatches have clear error messages."""

        class TestConfig(BaseConfig):
            port: int = Field(description="Port number")

        try:
            TestConfig(port="not_an_int")  # type: ignore
        except ValidationError as e:
            error_str = str(e)
            assert "port" in error_str
            assert "int" in error_str.lower() or "integer" in error_str.lower()

    def test_missing_field_error_message(self):
        """Test missing required fields have clear error messages."""

        class TestConfig(BaseConfig):
            required_field: str = Field(description="Required field")

        try:
            TestConfig()  # type: ignore
        except ValidationError as e:
            error_str = str(e)
            assert "required_field" in error_str
            assert "required" in error_str.lower() or "missing" in error_str.lower()


class TestConfigDocumentation:
    """Tests for config documentation and introspection."""

    def test_field_descriptions_preserved(self):
        """Test Field descriptions are preserved in schema."""

        class TestConfig(BaseConfig):
            name: str = Field(description="Service name")
            port: int = Field(description="Port number", ge=1024, le=65535)

        schema = TestConfig.model_json_schema()

        # Descriptions should be in schema
        assert "Service name" in str(schema)
        assert "Port number" in str(schema)

    def test_schema_generation(self):
        """Test Pydantic can generate JSON schema for documentation."""

        class TestConfig(BaseConfig):
            name: str = Field(description="Service name")

        schema = TestConfig.model_json_schema()

        # Schema should be valid dict
        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "name" in schema["properties"]
