"""
Unit tests for ouroboros.config.schemas.browser.

Tests BrowserConfig validation including:
    - Default values
    - Custom values
    - Field constraints (min/max ranges, pattern matching)
    - Browser type validation
    - Error message quality
"""

from pathlib import Path

import pytest
from ouroboros.config.schemas.browser import BrowserConfig
from pydantic import ValidationError


class TestBrowserConfigDefaults:
    """Test BrowserConfig default values."""

    def test_browser_config_defaults(self):
        """BrowserConfig should have sensible defaults for all fields."""
        config = BrowserConfig()

        assert config.browser_type == "chromium"
        assert config.headless is True
        assert config.max_sessions == 10
        assert config.session_timeout_minutes == 30
        assert config.screenshot_dir == Path(".praxis-os/workspace/scratch")

    def test_browser_config_immutable(self):
        """BrowserConfig should be immutable (frozen)."""
        config = BrowserConfig()

        with pytest.raises(ValidationError, match="frozen"):
            config.browser_type = "firefox"


class TestBrowserConfigCustomValues:
    """Test BrowserConfig with custom values."""

    def test_browser_config_chromium(self):
        """BrowserConfig should accept 'chromium' as browser_type."""
        config = BrowserConfig(browser_type="chromium")
        assert config.browser_type == "chromium"

    def test_browser_config_firefox(self):
        """BrowserConfig should accept 'firefox' as browser_type."""
        config = BrowserConfig(browser_type="firefox")
        assert config.browser_type == "firefox"

    def test_browser_config_webkit(self):
        """BrowserConfig should accept 'webkit' as browser_type."""
        config = BrowserConfig(browser_type="webkit")
        assert config.browser_type == "webkit"

    def test_browser_config_headless_false(self):
        """BrowserConfig should accept headless=False (headed mode)."""
        config = BrowserConfig(headless=False)
        assert config.headless is False

    def test_browser_config_custom_sessions(self):
        """BrowserConfig should accept custom max_sessions within valid range."""
        config = BrowserConfig(max_sessions=25)
        assert config.max_sessions == 25

    def test_browser_config_custom_timeout(self):
        """BrowserConfig should accept custom session_timeout_minutes within valid range."""
        config = BrowserConfig(session_timeout_minutes=60)
        assert config.session_timeout_minutes == 60

    def test_browser_config_custom_screenshot_dir(self):
        """BrowserConfig should accept custom screenshot directory."""
        config = BrowserConfig(screenshot_dir=Path("custom/screenshots"))
        assert config.screenshot_dir == Path("custom/screenshots")

    def test_browser_config_minimum_values(self):
        """BrowserConfig should accept minimum valid values."""
        config = BrowserConfig(
            max_sessions=1,  # minimum
            session_timeout_minutes=5,  # minimum
        )
        assert config.max_sessions == 1
        assert config.session_timeout_minutes == 5

    def test_browser_config_maximum_values(self):
        """BrowserConfig should accept maximum valid values."""
        config = BrowserConfig(
            max_sessions=50,  # maximum
            session_timeout_minutes=120,  # maximum
        )
        assert config.max_sessions == 50
        assert config.session_timeout_minutes == 120


class TestBrowserConfigConstraints:
    """Test BrowserConfig field constraints and validation rules."""

    def test_invalid_browser_type(self):
        """BrowserConfig should reject invalid browser_type values."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            BrowserConfig(browser_type="chrome")  # should be "chromium"

    def test_invalid_browser_type_safari(self):
        """BrowserConfig should reject 'safari' (should be 'webkit')."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            BrowserConfig(browser_type="safari")

    def test_max_sessions_too_low(self):
        """BrowserConfig should reject max_sessions < 1."""
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            BrowserConfig(max_sessions=0)

    def test_max_sessions_too_high(self):
        """BrowserConfig should reject max_sessions > 50."""
        with pytest.raises(ValidationError, match="less than or equal to 50"):
            BrowserConfig(max_sessions=100)

    def test_session_timeout_too_low(self):
        """BrowserConfig should reject session_timeout_minutes < 5."""
        with pytest.raises(ValidationError, match="greater than or equal to 5"):
            BrowserConfig(session_timeout_minutes=2)

    def test_session_timeout_too_high(self):
        """BrowserConfig should reject session_timeout_minutes > 120."""
        with pytest.raises(ValidationError, match="less than or equal to 120"):
            BrowserConfig(session_timeout_minutes=180)


class TestBrowserConfigSerialization:
    """Test BrowserConfig serialization and deserialization."""

    def test_browser_config_to_dict(self):
        """BrowserConfig should serialize to dict with correct structure."""
        config = BrowserConfig(
            browser_type="firefox",
            headless=False,
            max_sessions=15,
            session_timeout_minutes=45,
            screenshot_dir=Path("custom/screenshots"),
        )

        data = config.model_dump()
        assert data["browser_type"] == "firefox"
        assert data["headless"] is False
        assert data["max_sessions"] == 15
        assert data["session_timeout_minutes"] == 45
        assert data["screenshot_dir"] == Path("custom/screenshots")

    def test_browser_config_from_dict(self):
        """BrowserConfig should deserialize from dict correctly."""
        data = {
            "browser_type": "webkit",
            "headless": False,
            "max_sessions": 5,
            "session_timeout_minutes": 90,
            "screenshot_dir": "test/screenshots",
        }

        config = BrowserConfig(**data)
        assert config.browser_type == "webkit"
        assert config.headless is False
        assert config.max_sessions == 5
        assert config.session_timeout_minutes == 90
        assert config.screenshot_dir == Path("test/screenshots")


class TestBrowserTypeValidation:
    """Test browser_type pattern validation."""

    def test_browser_type_case_sensitive(self):
        """BrowserConfig browser_type should be case-sensitive."""
        # Valid lowercase
        config = BrowserConfig(browser_type="chromium")
        assert config.browser_type == "chromium"

        # Invalid uppercase
        with pytest.raises(ValidationError, match="String should match pattern"):
            BrowserConfig(browser_type="CHROMIUM")

    def test_browser_type_rejects_empty_string(self):
        """BrowserConfig should reject empty browser_type."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            BrowserConfig(browser_type="")

    def test_browser_type_strips_whitespace(self):
        """BrowserConfig should strip whitespace from browser_type (BaseConfig behavior)."""
        # BaseConfig automatically strips strings, so trailing/leading whitespace is removed
        config = BrowserConfig(browser_type=" chromium ")
        assert config.browser_type == "chromium"


class TestErrorMessages:
    """Test error message quality and actionability."""

    def test_browser_type_error_message(self):
        """Error message for invalid browser_type should be clear."""
        with pytest.raises(ValidationError) as exc_info:
            BrowserConfig(browser_type="invalid")

        error_str = str(exc_info.value)
        assert "browser_type" in error_str.lower()
        assert "pattern" in error_str.lower()

    def test_max_sessions_error_message(self):
        """Error message for invalid max_sessions should be clear."""
        with pytest.raises(ValidationError) as exc_info:
            BrowserConfig(max_sessions=0)

        error_str = str(exc_info.value)
        assert "max_sessions" in error_str.lower()
        assert "1" in error_str

    def test_session_timeout_error_message(self):
        """Error message for invalid session_timeout_minutes should be clear."""
        with pytest.raises(ValidationError) as exc_info:
            BrowserConfig(session_timeout_minutes=2)

        error_str = str(exc_info.value)
        assert "session_timeout_minutes" in error_str.lower()
        assert "5" in error_str


class TestBrowserConfigEdgeCases:
    """Test BrowserConfig edge cases and boundary conditions."""

    def test_all_fields_custom(self):
        """BrowserConfig should accept all custom fields simultaneously."""
        config = BrowserConfig(
            browser_type="firefox",
            headless=False,
            max_sessions=25,
            session_timeout_minutes=60,
            screenshot_dir=Path("custom/dir"),
        )

        assert config.browser_type == "firefox"
        assert config.headless is False
        assert config.max_sessions == 25
        assert config.session_timeout_minutes == 60
        assert config.screenshot_dir == Path("custom/dir")

    def test_partial_custom_fields(self):
        """BrowserConfig should accept partial custom fields with defaults for rest."""
        config = BrowserConfig(
            browser_type="webkit",
            max_sessions=5,
        )

        assert config.browser_type == "webkit"
        assert config.headless is True  # default
        assert config.max_sessions == 5
        assert config.session_timeout_minutes == 30  # default
        assert config.screenshot_dir == Path(".praxis-os/workspace/scratch")  # default
