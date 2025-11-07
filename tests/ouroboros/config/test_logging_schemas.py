"""
Unit tests for ouroboros.config.schemas.logging.

Tests LoggingConfig validation including:
    - Default values
    - Custom values
    - Field constraints (min/max ranges, pattern matching)
    - Log level and format validation
    - Error message quality
"""

from pathlib import Path

import pytest
from ouroboros.config.schemas.logging import LoggingConfig
from pydantic import ValidationError


class TestLoggingConfigDefaults:
    """Test LoggingConfig default values."""

    def test_logging_config_defaults(self):
        """LoggingConfig should have sensible defaults for all fields."""
        config = LoggingConfig()

        assert config.log_dir == Path(".praxis-os/logs")
        assert config.level == "INFO"
        assert config.format == "json"
        assert config.rotation_size_mb == 100
        assert config.max_files == 10
        assert config.behavioral_metrics_enabled is True

    def test_logging_config_immutable(self):
        """LoggingConfig should be immutable (frozen)."""
        config = LoggingConfig()

        with pytest.raises(ValidationError, match="frozen"):
            config.level = "DEBUG"


class TestLoggingConfigCustomValues:
    """Test LoggingConfig with custom values."""

    def test_logging_config_debug_level(self):
        """LoggingConfig should accept DEBUG log level."""
        config = LoggingConfig(level="DEBUG")
        assert config.level == "DEBUG"

    def test_logging_config_warning_level(self):
        """LoggingConfig should accept WARNING log level."""
        config = LoggingConfig(level="WARNING")
        assert config.level == "WARNING"

    def test_logging_config_error_level(self):
        """LoggingConfig should accept ERROR log level."""
        config = LoggingConfig(level="ERROR")
        assert config.level == "ERROR"

    def test_logging_config_critical_level(self):
        """LoggingConfig should accept CRITICAL log level."""
        config = LoggingConfig(level="CRITICAL")
        assert config.level == "CRITICAL"

    def test_logging_config_text_format(self):
        """LoggingConfig should accept text format."""
        config = LoggingConfig(format="text")
        assert config.format == "text"

    def test_logging_config_custom_rotation(self):
        """LoggingConfig should accept custom rotation_size_mb within valid range."""
        config = LoggingConfig(rotation_size_mb=500)
        assert config.rotation_size_mb == 500

    def test_logging_config_custom_max_files(self):
        """LoggingConfig should accept custom max_files within valid range."""
        config = LoggingConfig(max_files=20)
        assert config.max_files == 20

    def test_logging_config_metrics_disabled(self):
        """LoggingConfig should accept behavioral_metrics_enabled=False."""
        config = LoggingConfig(behavioral_metrics_enabled=False)
        assert config.behavioral_metrics_enabled is False

    def test_logging_config_custom_log_dir(self):
        """LoggingConfig should accept custom log directory."""
        config = LoggingConfig(log_dir=Path("custom/logs"))
        assert config.log_dir == Path("custom/logs")

    def test_logging_config_minimum_values(self):
        """LoggingConfig should accept minimum valid values."""
        config = LoggingConfig(
            rotation_size_mb=10,  # minimum
            max_files=1,  # minimum
        )
        assert config.rotation_size_mb == 10
        assert config.max_files == 1

    def test_logging_config_maximum_values(self):
        """LoggingConfig should accept maximum valid values."""
        config = LoggingConfig(
            rotation_size_mb=1000,  # maximum
            max_files=100,  # maximum
        )
        assert config.rotation_size_mb == 1000
        assert config.max_files == 100


class TestLoggingConfigConstraints:
    """Test LoggingConfig field constraints and validation rules."""

    def test_invalid_log_level(self):
        """LoggingConfig should reject invalid log levels."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            LoggingConfig(level="TRACE")

    def test_invalid_log_level_lowercase(self):
        """LoggingConfig should reject lowercase log levels."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            LoggingConfig(level="info")

    def test_invalid_format(self):
        """LoggingConfig should reject invalid formats."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            LoggingConfig(format="xml")

    def test_rotation_size_too_low(self):
        """LoggingConfig should reject rotation_size_mb < 10."""
        with pytest.raises(ValidationError, match="greater than or equal to 10"):
            LoggingConfig(rotation_size_mb=5)

    def test_rotation_size_too_high(self):
        """LoggingConfig should reject rotation_size_mb > 1000."""
        with pytest.raises(ValidationError, match="less than or equal to 1000"):
            LoggingConfig(rotation_size_mb=2000)

    def test_max_files_too_low(self):
        """LoggingConfig should reject max_files < 1."""
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            LoggingConfig(max_files=0)

    def test_max_files_too_high(self):
        """LoggingConfig should reject max_files > 100."""
        with pytest.raises(ValidationError, match="less than or equal to 100"):
            LoggingConfig(max_files=200)


class TestLoggingConfigSerialization:
    """Test LoggingConfig serialization and deserialization."""

    def test_logging_config_to_dict(self):
        """LoggingConfig should serialize to dict with correct structure."""
        config = LoggingConfig(
            log_dir=Path("custom/logs"),
            level="DEBUG",
            format="text",
            rotation_size_mb=50,
            max_files=5,
            behavioral_metrics_enabled=False,
        )

        data = config.model_dump()
        assert data["log_dir"] == Path("custom/logs")
        assert data["level"] == "DEBUG"
        assert data["format"] == "text"
        assert data["rotation_size_mb"] == 50
        assert data["max_files"] == 5
        assert data["behavioral_metrics_enabled"] is False

    def test_logging_config_from_dict(self):
        """LoggingConfig should deserialize from dict correctly."""
        data = {
            "log_dir": "test/logs",
            "level": "WARNING",
            "format": "json",
            "rotation_size_mb": 200,
            "max_files": 15,
            "behavioral_metrics_enabled": True,
        }

        config = LoggingConfig(**data)
        assert config.log_dir == Path("test/logs")
        assert config.level == "WARNING"
        assert config.format == "json"
        assert config.rotation_size_mb == 200
        assert config.max_files == 15
        assert config.behavioral_metrics_enabled is True


class TestLogLevelValidation:
    """Test log level pattern validation."""

    def test_all_valid_log_levels(self):
        """LoggingConfig should accept all valid log levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            config = LoggingConfig(level=level)
            assert config.level == level

    def test_log_level_case_sensitive(self):
        """LoggingConfig log level should be case-sensitive (uppercase only)."""
        # Valid uppercase
        config = LoggingConfig(level="INFO")
        assert config.level == "INFO"

        # Invalid lowercase
        with pytest.raises(ValidationError, match="String should match pattern"):
            LoggingConfig(level="info")

        # Invalid mixed case
        with pytest.raises(ValidationError, match="String should match pattern"):
            LoggingConfig(level="Info")


class TestLogFormatValidation:
    """Test log format pattern validation."""

    def test_both_valid_formats(self):
        """LoggingConfig should accept both json and text formats."""
        json_config = LoggingConfig(format="json")
        assert json_config.format == "json"

        text_config = LoggingConfig(format="text")
        assert text_config.format == "text"

    def test_format_case_sensitive(self):
        """LoggingConfig format should be case-sensitive (lowercase only)."""
        # Valid lowercase
        config = LoggingConfig(format="json")
        assert config.format == "json"

        # Invalid uppercase
        with pytest.raises(ValidationError, match="String should match pattern"):
            LoggingConfig(format="JSON")


class TestErrorMessages:
    """Test error message quality and actionability."""

    def test_invalid_level_error_message(self):
        """Error message for invalid level should be clear."""
        with pytest.raises(ValidationError) as exc_info:
            LoggingConfig(level="TRACE")

        error_str = str(exc_info.value)
        assert "level" in error_str.lower()
        assert "pattern" in error_str.lower()

    def test_invalid_format_error_message(self):
        """Error message for invalid format should be clear."""
        with pytest.raises(ValidationError) as exc_info:
            LoggingConfig(format="xml")

        error_str = str(exc_info.value)
        assert "format" in error_str.lower()
        assert "pattern" in error_str.lower()

    def test_rotation_size_error_message(self):
        """Error message for invalid rotation_size_mb should be clear."""
        with pytest.raises(ValidationError) as exc_info:
            LoggingConfig(rotation_size_mb=5)

        error_str = str(exc_info.value)
        assert "rotation_size_mb" in error_str.lower()
        assert "10" in error_str

    def test_max_files_error_message(self):
        """Error message for invalid max_files should be clear."""
        with pytest.raises(ValidationError) as exc_info:
            LoggingConfig(max_files=0)

        error_str = str(exc_info.value)
        assert "max_files" in error_str.lower()
        assert "1" in error_str


class TestLoggingConfigEdgeCases:
    """Test LoggingConfig edge cases and boundary conditions."""

    def test_all_fields_custom(self):
        """LoggingConfig should accept all custom fields simultaneously."""
        config = LoggingConfig(
            log_dir=Path("custom/logs"),
            level="ERROR",
            format="text",
            rotation_size_mb=250,
            max_files=25,
            behavioral_metrics_enabled=False,
        )

        assert config.log_dir == Path("custom/logs")
        assert config.level == "ERROR"
        assert config.format == "text"
        assert config.rotation_size_mb == 250
        assert config.max_files == 25
        assert config.behavioral_metrics_enabled is False

    def test_partial_custom_fields(self):
        """LoggingConfig should accept partial custom fields with defaults for rest."""
        config = LoggingConfig(
            level="DEBUG",
            rotation_size_mb=50,
        )

        assert config.level == "DEBUG"
        assert config.rotation_size_mb == 50
        assert config.format == "json"  # default
        assert config.max_files == 10  # default
        assert config.behavioral_metrics_enabled is True  # default
