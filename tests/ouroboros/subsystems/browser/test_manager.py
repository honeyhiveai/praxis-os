"""
Unit tests for Browser Manager.

Tests BrowserManager and BrowserSession with mocked Playwright to ensure
session lifecycle, isolation, config integration, and error handling work correctly.
"""

import asyncio
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from ouroboros.config.schemas.browser import BrowserConfig
from ouroboros.foundation.session_mapper import SessionMapper
from ouroboros.subsystems.browser.manager import BrowserManager, BrowserSession
from ouroboros.utils.errors import ActionableError


class TestBrowserSession:
    """Test suite for BrowserSession."""

    @pytest.fixture
    def mock_playwright(self):
        """Create mock Playwright instance."""
        pw = AsyncMock()
        pw.stop = AsyncMock()
        return pw

    @pytest.fixture
    def mock_browser(self):
        """Create mock Browser instance."""
        browser = AsyncMock()
        browser.close = AsyncMock()
        browser.process = MagicMock()
        browser.process.pid = 12345
        return browser

    @pytest.fixture
    def mock_page(self):
        """Create mock Page instance."""
        page = AsyncMock()
        page.close = AsyncMock()
        return page

    @pytest.fixture
    def browser_session(self, mock_playwright, mock_browser, mock_page):
        """Create BrowserSession with mocks."""
        return BrowserSession(
            playwright=mock_playwright,
            browser=mock_browser,
            page=mock_page,
            created_at=time.time(),
            browser_type="chromium",
            headless=True,
            tabs={"tab-abc123": mock_page},
        )

    @pytest.mark.asyncio
    async def test_session_cleanup_success(self, browser_session):
        """Test successful session cleanup."""
        await browser_session.cleanup()

        # Verify cleanup order
        # Note: page.close() is called twice (once in tabs loop, once as primary page)
        assert browser_session.page.close.call_count == 2
        browser_session.browser.close.assert_called_once()
        browser_session.playwright.stop.assert_called_once()
        assert len(browser_session.tabs) == 0

    @pytest.mark.asyncio
    async def test_session_cleanup_with_errors(
        self, mock_playwright, mock_browser, mock_page
    ):
        """Test session cleanup continues even if some steps fail."""
        # Make page.close fail
        mock_page.close = AsyncMock(side_effect=Exception("Page close failed"))

        session = BrowserSession(
            playwright=mock_playwright,
            browser=mock_browser,
            page=mock_page,
            created_at=time.time(),
            tabs={"tab-1": mock_page},
        )

        # Should not raise exception
        await session.cleanup()

        # Browser and Playwright should still be cleaned up
        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_cleanup_multiple_tabs(self, mock_playwright, mock_browser):
        """Test cleanup with multiple tabs."""
        tab1 = AsyncMock()
        tab2 = AsyncMock()
        tab3 = AsyncMock()

        session = BrowserSession(
            playwright=mock_playwright,
            browser=mock_browser,
            page=tab1,
            created_at=time.time(),
            tabs={"tab-1": tab1, "tab-2": tab2, "tab-3": tab3},
        )

        await session.cleanup()

        # All tabs should be closed
        # Note: tab1 is called twice (once in tabs loop, once as primary page)
        assert tab1.close.call_count == 2
        tab2.close.assert_called_once()
        tab3.close.assert_called_once()
        assert len(session.tabs) == 0


class TestBrowserManager:
    """Test suite for BrowserManager."""

    @pytest.fixture
    def config(self):
        """Create default BrowserConfig."""
        return BrowserConfig(
            browser_type="chromium",
            headless=True,
            max_sessions=10,
            session_timeout_minutes=30,
        )

    @pytest.fixture
    def session_mapper(self, tmp_path):
        """Create SessionMapper with temp directory."""
        state_dir = tmp_path / "state"
        return SessionMapper(state_dir)

    @pytest.fixture
    def manager(self, config, session_mapper):
        """Create BrowserManager with config and session_mapper."""
        return BrowserManager(config, session_mapper)

    @pytest.mark.asyncio
    @patch("ouroboros.subsystems.browser.manager.async_playwright")
    async def test_get_session_creates_new(self, mock_async_pw, manager):
        """Test getting a new session creates browser."""
        # Setup mocks
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()

        mock_async_pw.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.process.pid = 12345

        # Get session
        session = await manager.get_session("browser_test_s0")

        # Verify session created
        assert session is not None
        assert session.browser_type == "chromium"
        assert session.headless is True
        assert "browser_test_s0" in manager._sessions
        mock_async_pw.return_value.start.assert_called_once()
        mock_playwright_instance.chromium.launch.assert_called_once()

    @pytest.mark.asyncio
    @patch("ouroboros.subsystems.browser.manager.async_playwright")
    async def test_get_session_reuses_existing(self, mock_async_pw, manager):
        """Test getting existing session reuses it."""
        # Setup mocks
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()

        mock_async_pw.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.process.pid = 12345

        # Create session
        session1 = await manager.get_session("browser_test_s0")
        initial_access = session1.last_access

        # Small delay
        await asyncio.sleep(0.1)

        # Get same session
        session2 = await manager.get_session("browser_test_s0")

        # Should be same session
        assert session1 is session2
        assert session2.last_access > initial_access
        # Playwright should only be started once
        assert mock_async_pw.return_value.start.call_count == 1

    @pytest.mark.asyncio
    @patch("ouroboros.subsystems.browser.manager.async_playwright")
    async def test_get_session_max_limit(self, mock_async_pw, manager):
        """Test max sessions limit is enforced."""
        # Setup mocks
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()

        mock_async_pw.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.process.pid = 12345

        # Create max sessions (config has max_sessions=10)
        for i in range(manager.config.max_sessions):
            await manager.get_session(f"browser_test_s{i}")

        # Next session should fail
        with pytest.raises(
            ActionableError, match="Maximum concurrent sessions reached"
        ):
            await manager.get_session("browser_test_s999")

    @pytest.mark.asyncio
    @patch("ouroboros.subsystems.browser.manager.async_playwright")
    async def test_get_session_invalid_browser_type(self, mock_async_pw, manager):
        """Test invalid browser type raises error."""
        # Setup mocks
        mock_playwright_instance = AsyncMock()
        mock_async_pw.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )

        # Try invalid browser type
        with pytest.raises(ActionableError, match="Invalid browser_type"):
            await manager.get_session("browser_test_s0", browser_type="invalid")

    @pytest.mark.asyncio
    @patch("ouroboros.subsystems.browser.manager.async_playwright")
    async def test_get_session_cross_browser(self, mock_async_pw, manager):
        """Test getting sessions with different browser types."""
        # Setup mocks
        mock_playwright_instance = AsyncMock()
        mock_chromium = AsyncMock()
        mock_firefox = AsyncMock()
        mock_page = AsyncMock()

        mock_async_pw.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_chromium)
        mock_playwright_instance.firefox.launch = AsyncMock(return_value=mock_firefox)
        mock_chromium.new_page = AsyncMock(return_value=mock_page)
        mock_firefox.new_page = AsyncMock(return_value=mock_page)
        mock_chromium.process.pid = 1
        mock_firefox.process.pid = 2

        # Get chromium session
        chromium_session = await manager.get_session(
            "browser_chromium", browser_type="chromium"
        )
        assert chromium_session.browser_type == "chromium"

        # Get firefox session
        firefox_session = await manager.get_session(
            "browser_firefox", browser_type="firefox"
        )
        assert firefox_session.browser_type == "firefox"

        # Both should exist
        assert len(manager._sessions) == 2

    @pytest.mark.asyncio
    @patch("ouroboros.subsystems.browser.manager.async_playwright")
    async def test_close_session(self, mock_async_pw, manager):
        """Test closing a session."""
        # Setup mocks
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()

        mock_async_pw.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.process.pid = 12345

        # Create session
        await manager.get_session("browser_test_s0")
        assert "browser_test_s0" in manager._sessions

        # Close session
        await manager.close_session("browser_test_s0")
        assert "browser_test_s0" not in manager._sessions

        # Verify cleanup called
        # Note: page.close() is called twice (once in tabs loop, once as primary page)
        assert mock_page.close.call_count == 2
        mock_browser.close.assert_called_once()
        mock_playwright_instance.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_nonexistent_session(self, manager):
        """Test closing nonexistent session is safe."""
        # Should not raise exception
        await manager.close_session("nonexistent")

    @pytest.mark.asyncio
    @patch("ouroboros.subsystems.browser.manager.async_playwright")
    async def test_cleanup_stale_sessions(self, mock_async_pw, tmp_path):
        """Test stale session cleanup."""
        # Create config with 5-minute timeout (minimum allowed)
        config = BrowserConfig(
            browser_type="chromium",
            headless=True,
            max_sessions=10,
            session_timeout_minutes=5,
        )
        session_mapper = SessionMapper(tmp_path / "state")
        manager = BrowserManager(config, session_mapper)

        # Setup mocks
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()

        mock_async_pw.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.process.pid = 12345

        # Create session
        await manager.get_session("browser_test_s0")
        assert "browser_test_s0" in manager._sessions

        # Manually set last_access to past to simulate stale session
        # This bypasses the config's frozen state
        session = manager._sessions["browser_test_s0"]
        session.last_access = time.time() - (
            6 * 60
        )  # 6 minutes ago (exceeds 5-minute timeout)

        # Create new session (triggers cleanup)
        await manager.get_session("browser_test_s1")

        # Old session should be cleaned up
        assert "browser_test_s0" not in manager._sessions
        assert "browser_test_s1" in manager._sessions

    @pytest.mark.asyncio
    @patch("ouroboros.subsystems.browser.manager.async_playwright")
    async def test_shutdown(self, mock_async_pw, manager):
        """Test graceful shutdown."""
        # Setup mocks
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()

        mock_async_pw.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.process.pid = 12345

        # Create multiple sessions
        await manager.get_session("browser_test_s0")
        await manager.get_session("browser_test_s1")
        await manager.get_session("browser_test_s2")

        assert len(manager._sessions) == 3

        # Shutdown
        await manager.shutdown()

        # All sessions should be closed
        assert len(manager._sessions) == 0

    @pytest.mark.asyncio
    @patch("ouroboros.subsystems.browser.manager.async_playwright")
    async def test_config_integration(self, mock_async_pw, tmp_path):
        """Test BrowserManager respects config settings."""
        config = BrowserConfig(
            browser_type="firefox",
            headless=False,
            max_sessions=5,
            session_timeout_minutes=60,
        )
        session_mapper = SessionMapper(tmp_path / "state")
        manager = BrowserManager(config, session_mapper)

        # Setup mocks
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()

        mock_async_pw.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )
        mock_playwright_instance.firefox.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.process.pid = 12345

        # Create session (should use config defaults)
        session = await manager.get_session("browser_test_s0")

        # Verify config was used
        assert session.browser_type == "firefox"
        assert session.headless is False
        mock_playwright_instance.firefox.launch.assert_called_once_with(headless=False)
        assert manager.config.max_sessions == 5
        assert manager.config.session_timeout_seconds == 3600  # 60 minutes * 60


class TestBrowserConfig:
    """Test suite for BrowserConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = BrowserConfig()

        assert config.browser_type == "chromium"
        assert config.headless is True
        assert config.max_sessions == 10
        assert config.session_timeout_minutes == 30
        assert config.session_timeout_seconds == 1800

    def test_custom_config(self):
        """Test custom configuration."""
        config = BrowserConfig(
            browser_type="firefox",
            headless=False,
            max_sessions=20,
            session_timeout_minutes=60,
        )

        assert config.browser_type == "firefox"
        assert config.headless is False
        assert config.max_sessions == 20
        assert config.session_timeout_minutes == 60
        assert config.session_timeout_seconds == 3600

    def test_invalid_browser_type_validation(self):
        """Test invalid browser type raises validation error."""
        with pytest.raises(ValueError):
            BrowserConfig(browser_type="invalid")

    def test_max_sessions_validation(self):
        """Test max_sessions bounds are enforced."""
        # Too low
        with pytest.raises(ValueError):
            BrowserConfig(max_sessions=0)

        # Too high
        with pytest.raises(ValueError):
            BrowserConfig(max_sessions=51)

        # Valid bounds
        config1 = BrowserConfig(max_sessions=1)
        assert config1.max_sessions == 1

        config2 = BrowserConfig(max_sessions=50)
        assert config2.max_sessions == 50

    def test_timeout_validation(self):
        """Test session_timeout_minutes bounds are enforced."""
        # Too low
        with pytest.raises(ValueError):
            BrowserConfig(session_timeout_minutes=4)

        # Too high
        with pytest.raises(ValueError):
            BrowserConfig(session_timeout_minutes=121)

        # Valid bounds
        config1 = BrowserConfig(session_timeout_minutes=5)
        assert config1.session_timeout_minutes == 5

        config2 = BrowserConfig(session_timeout_minutes=120)
        assert config2.session_timeout_minutes == 120
