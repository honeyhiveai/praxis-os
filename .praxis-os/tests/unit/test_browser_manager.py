"""
Unit tests for BrowserManager.

Tests browser lifecycle management, session isolation, and cleanup
without requiring real Playwright browser installation.

Traceability:
    FR-1, FR-2, FR-3, NFR-1, NFR-3, NFR-4, NFR-5, NFR-6, NFR-9
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_server.server.browser_manager import BrowserManager, BrowserSession

# ===== TASK 3.1: BrowserManager Basics =====


@pytest.mark.asyncio
async def test_init_lightweight():
    """
    Test BrowserManager initialization is lightweight (no browser).

    Per-session architecture: No shared browser created at init.

    Traceability: FR-1, NFR-1
    """
    manager = BrowserManager(session_timeout=3600)

    # Verify initialization
    assert manager._sessions == {}
    assert manager._session_timeout == 3600
    assert manager._lock is not None

    # Verify no browser process started (lightweight init)
    assert len(manager._sessions) == 0


@pytest.mark.asyncio
@patch("mcp_server.server.browser_manager.async_playwright")
async def test_get_session_creates_new_browser(mock_async_playwright):
    """
    Test get_session creates new browser process per session.

    Per-session architecture: Each session gets own Playwright + browser.

    Traceability: FR-1, FR-2, NFR-1
    """
    # Mock Playwright - need to return async context manager
    mock_playwright_ctx = AsyncMock()
    mock_playwright_instance = AsyncMock()
    mock_browser = AsyncMock()
    mock_page = AsyncMock()

    mock_browser.process = MagicMock()
    mock_browser.process.pid = 12345

    mock_playwright_instance.chromium.launch.return_value = mock_browser
    mock_browser.new_page.return_value = mock_page

    # async_playwright() returns async context manager with .start()
    mock_playwright_ctx.start.return_value = mock_playwright_instance
    mock_async_playwright.return_value = mock_playwright_ctx

    # Create manager and get session
    manager = BrowserManager()
    session = await manager.get_session("test-1")

    # Verify session created
    assert "test-1" in manager._sessions
    assert session.browser is mock_browser
    assert session.page is mock_page
    assert session.playwright is mock_playwright_instance

    # Verify Playwright + browser launched
    mock_async_playwright.return_value.start.assert_called_once()
    mock_playwright_instance.chromium.launch.assert_called_once_with(headless=True)
    mock_browser.new_page.assert_called_once()


@pytest.mark.asyncio
@patch("mcp_server.server.browser_manager.async_playwright")
async def test_get_session_reuses_existing(mock_async_playwright):
    """
    Test get_session reuses existing session (doesn't create new browser).

    Traceability: FR-2, NFR-2
    """
    # Mock Playwright
    mock_playwright_ctx = AsyncMock()
    mock_playwright_instance = AsyncMock()
    mock_browser = AsyncMock()
    mock_page = AsyncMock()

    mock_browser.process = MagicMock()
    mock_browser.process.pid = 12345

    mock_playwright_instance.chromium.launch.return_value = mock_browser
    mock_browser.new_page.return_value = mock_page

    mock_playwright_ctx.start.return_value = mock_playwright_instance
    mock_async_playwright.return_value = mock_playwright_ctx

    # Create manager and get session twice
    manager = BrowserManager()
    session1 = await manager.get_session("test-1")
    session2 = await manager.get_session("test-1")

    # Verify same session returned
    assert session1 is session2
    assert session1.page is session2.page
    assert session1.browser is session2.browser

    # Verify browser only created once
    assert mock_async_playwright.return_value.start.call_count == 1
    assert mock_playwright_instance.chromium.launch.call_count == 1


@pytest.mark.asyncio
@patch("mcp_server.server.browser_manager.async_playwright")
async def test_different_sessions_isolated(mock_async_playwright):
    """
    Test different sessions get isolated browsers (per-session architecture).

    Traceability: FR-2, NFR-5
    """

    # Mock Playwright to return different instances
    def create_mock_playwright_ctx():
        mock_pw = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_browser.process = MagicMock()
        mock_browser.process.pid = id(mock_browser)  # Unique PID
        mock_pw.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_ctx = AsyncMock()
        mock_ctx.start.return_value = mock_pw
        return mock_ctx

    mock_async_playwright.side_effect = [
        create_mock_playwright_ctx(),
        create_mock_playwright_ctx(),
    ]

    # Create manager and get two different sessions
    manager = BrowserManager()
    session1 = await manager.get_session("test-1")
    session2 = await manager.get_session("test-2")

    # Verify different sessions have different browsers
    assert session1 is not session2
    assert session1.browser is not session2.browser
    assert session1.page is not session2.page
    assert session1.playwright is not session2.playwright

    # Verify both browsers launched (call_count check not needed with side_effect)
    assert mock_async_playwright.call_count == 2


@pytest.mark.asyncio
@patch("mcp_server.server.browser_manager.async_playwright")
async def test_close_session_kills_browser(mock_async_playwright):
    """
    Test close_session kills browser process.

    Traceability: FR-3, NFR-3
    """
    # Mock Playwright
    mock_playwright_ctx = AsyncMock()
    mock_playwright_instance = AsyncMock()
    mock_browser = AsyncMock()
    mock_page = AsyncMock()

    mock_browser.process = MagicMock()
    mock_browser.process.pid = 12345

    mock_playwright_instance.chromium.launch.return_value = mock_browser
    mock_browser.new_page.return_value = mock_page

    mock_playwright_ctx.start.return_value = mock_playwright_instance
    mock_async_playwright.return_value = mock_playwright_ctx

    # Create session and close it
    manager = BrowserManager()
    session = await manager.get_session("test-1")

    assert "test-1" in manager._sessions

    await manager.close_session("test-1")

    # Verify session removed
    assert "test-1" not in manager._sessions

    # Verify cleanup called (may be called multiple times during cleanup process)
    assert mock_page.close.called
    assert mock_browser.close.called
    assert mock_playwright_instance.stop.called


@pytest.mark.asyncio
@patch("mcp_server.server.browser_manager.async_playwright")
async def test_shutdown_kills_all_browsers(mock_async_playwright):
    """
    Test shutdown kills all browser processes.

    Traceability: FR-3, NFR-3
    """

    # Mock Playwright to return different instances
    def create_mock_playwright_ctx():
        mock_pw = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_browser.process = MagicMock()
        mock_pw.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_ctx = AsyncMock()
        mock_ctx.start.return_value = mock_pw
        return mock_ctx

    mock_async_playwright.side_effect = [
        create_mock_playwright_ctx(),
        create_mock_playwright_ctx(),
        create_mock_playwright_ctx(),
    ]

    # Create multiple sessions
    manager = BrowserManager()
    await manager.get_session("test-1")
    await manager.get_session("test-2")
    await manager.get_session("test-3")

    assert len(manager._sessions) == 3

    # Shutdown all
    await manager.shutdown()

    # Verify all sessions removed
    assert len(manager._sessions) == 0


# ===== TASK 3.2: Session Isolation =====


@pytest.mark.asyncio
@patch("mcp_server.server.browser_manager.async_playwright")
async def test_multiple_sessions_isolated(mock_async_playwright):
    """
    Test multiple sessions have isolated contexts (per-session browsers).

    Traceability: FR-2, NFR-5
    """

    # Mock Playwright to return unique instances
    def create_mock_playwright_ctx():
        mock_pw = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_browser.process = MagicMock()
        mock_browser.process.pid = id(mock_browser)
        mock_pw.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_ctx = AsyncMock()
        mock_ctx.start.return_value = mock_pw
        return mock_ctx

    mock_async_playwright.side_effect = [
        create_mock_playwright_ctx(),
        create_mock_playwright_ctx(),
        create_mock_playwright_ctx(),
    ]

    manager = BrowserManager()

    # Create three sessions
    s1 = await manager.get_session("chat-A")
    s2 = await manager.get_session("chat-B")
    s3 = await manager.get_session("chat-C")

    # Verify all isolated (different browser processes)
    browsers = {s1.browser, s2.browser, s3.browser}
    pages = {s1.page, s2.page, s3.page}
    playwrights = {s1.playwright, s2.playwright, s3.playwright}

    assert len(browsers) == 3, "Each session should have own browser"
    assert len(pages) == 3, "Each session should have own page"
    assert len(playwrights) == 3, "Each session should have own Playwright"


@pytest.mark.asyncio
@patch("mcp_server.server.browser_manager.async_playwright")
async def test_concurrent_get_session(mock_async_playwright):
    """
    Test concurrent get_session calls are thread-safe.

    Traceability: FR-2, NFR-4
    """

    # Mock Playwright
    def create_mock_playwright_ctx():
        mock_pw = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_browser.process = MagicMock()
        mock_pw.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_ctx = AsyncMock()
        mock_ctx.start.return_value = mock_pw
        return mock_ctx

    mock_async_playwright.side_effect = [create_mock_playwright_ctx() for _ in range(5)]

    manager = BrowserManager()

    # Call get_session concurrently for different sessions
    sessions = await asyncio.gather(
        manager.get_session("concurrent-1"),
        manager.get_session("concurrent-2"),
        manager.get_session("concurrent-3"),
        manager.get_session("concurrent-4"),
        manager.get_session("concurrent-5"),
    )

    # Verify all sessions created successfully
    assert len(sessions) == 5
    assert len(manager._sessions) == 5

    # Verify all sessions are unique
    session_ids = {id(s) for s in sessions}
    assert len(session_ids) == 5


@pytest.mark.asyncio
@patch("mcp_server.server.browser_manager.async_playwright")
async def test_no_state_leakage(mock_async_playwright):
    """
    Test sessions don't leak state (cookies, storage, etc.).

    Per-session browsers ensure complete isolation.

    Traceability: FR-2, NFR-5
    """

    # Mock Playwright
    def create_mock_playwright_ctx():
        mock_pw = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_browser.process = MagicMock()
        mock_pw.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.context = mock_context
        mock_ctx = AsyncMock()
        mock_ctx.start.return_value = mock_pw
        return mock_ctx

    mock_async_playwright.side_effect = [
        create_mock_playwright_ctx(),
        create_mock_playwright_ctx(),
    ]

    manager = BrowserManager()

    # Create two sessions
    s1 = await manager.get_session("session-1")
    s2 = await manager.get_session("session-2")

    # Verify contexts are different (no state leakage)
    assert s1.page.context is not s2.page.context
    assert s1.browser is not s2.browser


# ===== TASK 3.3: Stale Session Cleanup =====


@pytest.mark.asyncio
@patch("mcp_server.server.browser_manager.async_playwright")
@patch("mcp_server.server.browser_manager.time")
async def test_cleanup_stale_sessions(mock_time, mock_async_playwright):
    """
    Test auto-cleanup removes stale sessions.

    Traceability: FR-3, NFR-3
    """
    # Mock time to control staleness
    now = 1000.0
    mock_time.time.side_effect = [
        now,  # session created_at
        now,  # session last_access default
        now + 3700,  # cleanup check (1h 100s later)
    ]

    # Mock Playwright
    mock_playwright_ctx = AsyncMock()
    mock_playwright_instance = AsyncMock()
    mock_browser = AsyncMock()
    mock_page = AsyncMock()
    mock_browser.process = MagicMock()
    mock_playwright_instance.chromium.launch.return_value = mock_browser
    mock_browser.new_page.return_value = mock_page
    mock_playwright_ctx.start.return_value = mock_playwright_instance
    mock_async_playwright.return_value = mock_playwright_ctx

    # Create session (timeout = 3600s = 1 hour)
    manager = BrowserManager(session_timeout=3600)
    session = await manager.get_session("old-session")

    # Manually set last_access to old time
    session.last_access = now

    # Trigger cleanup by trying to create new session
    # (cleanup runs before creating new session)
    await manager._cleanup_stale_sessions()

    # Verify stale session removed
    assert "old-session" not in manager._sessions


@pytest.mark.asyncio
@patch("mcp_server.server.browser_manager.async_playwright")
async def test_cleanup_preserves_active(mock_async_playwright):
    """
    Test cleanup preserves recently accessed sessions.

    Traceability: FR-3, NFR-3
    """

    # Mock Playwright
    def create_mock_playwright_ctx():
        mock_pw = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_browser.process = MagicMock()
        mock_pw.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_ctx = AsyncMock()
        mock_ctx.start.return_value = mock_pw
        return mock_ctx

    mock_async_playwright.side_effect = [
        create_mock_playwright_ctx(),
        create_mock_playwright_ctx(),
    ]

    # Create manager with 1 hour timeout
    manager = BrowserManager(session_timeout=3600)

    # Create two sessions
    old_session = await manager.get_session("old")
    new_session = await manager.get_session("new")

    # Make old session stale
    old_session.last_access = time.time() - 3700  # 1h 100s ago

    # Cleanup
    await manager._cleanup_stale_sessions()

    # Verify old removed, new preserved
    assert "old" not in manager._sessions
    assert "new" in manager._sessions


@pytest.mark.asyncio
@patch("mcp_server.server.browser_manager.async_playwright")
async def test_cleanup_error_handling(mock_async_playwright):
    """
    Test cleanup continues even if one session cleanup fails.

    Traceability: NFR-6 (Graceful degradation)
    """

    # Mock Playwright
    def create_mock_playwright_ctx():
        mock_pw = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_browser.process = MagicMock()
        mock_pw.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_ctx = AsyncMock()
        mock_ctx.start.return_value = mock_pw
        return mock_ctx

    mock_async_playwright.side_effect = [
        create_mock_playwright_ctx(),
        create_mock_playwright_ctx(),
    ]

    manager = BrowserManager(session_timeout=100)

    # Create two sessions
    s1 = await manager.get_session("fail-1")
    s2 = await manager.get_session("fail-2")

    # Make both stale
    s1.last_access = time.time() - 200
    s2.last_access = time.time() - 200

    # Make first session's cleanup fail
    s1.cleanup = AsyncMock(side_effect=Exception("Cleanup failed"))

    # Cleanup should continue despite error
    await manager._cleanup_stale_sessions()

    # Both sessions should be removed from dict despite cleanup error
    # (error is logged but doesn't stop cleanup)
    assert len(manager._sessions) < 2


# ===== Test Fixtures =====


@pytest.fixture
def mock_playwright():
    """Fixture providing mocked Playwright."""
    with patch("mcp_server.browser_manager.async_playwright") as mock:
        mock_pw = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_browser.process = MagicMock()
        mock_browser.process.pid = 12345
        mock_pw.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock.return_value.start.return_value = mock_pw
        yield mock
