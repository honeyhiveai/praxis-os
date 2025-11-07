"""
Integration test for end-to-end browser automation flow.

Tests the complete browser pipeline:
    1. Browser session creation
    2. Session isolation
    3. Playwright actions
    4. Session cleanup

Traceability:
    Phase 8, Task 8.3: Integration tests
    End-to-end browser automation validation
"""

import pytest
from ouroboros.subsystems.browser.manager import BrowserManager


class TestBrowserIntegration:
    """Integration tests for complete browser flow."""
    
    @pytest.fixture
    def browser_manager(self, test_config, test_base_path):
        """
        Create BrowserManager with isolated test config.
        
        Uses test fixtures that create temporary directories and configs.
        No production code touched - pure dependency injection.
        """
        from ouroboros.foundation.session_mapper import SessionMapper
        
        # Create SessionMapper with test state directory
        state_dir = test_base_path / "state"
        state_dir.mkdir(exist_ok=True)
        session_mapper = SessionMapper(state_dir)
        
        return BrowserManager(config=test_config.browser, session_mapper=session_mapper)
    
    def test_config_has_browser_settings(self, test_config):
        """Test that browser configuration is present."""
        assert test_config.browser is not None
        assert test_config.browser.browser_type in ["chromium", "firefox", "webkit"]
        assert isinstance(test_config.browser.headless, bool)
        assert test_config.browser.max_sessions > 0
        assert test_config.browser.session_timeout_minutes > 0
    
    def test_browser_manager_initializes(self, browser_manager):
        """Test BrowserManager initializes with config."""
        assert browser_manager is not None
        assert hasattr(browser_manager, "config")
    
    @pytest.mark.asyncio
    async def test_browser_session_creation(self, browser_manager):
        """Test browser session can be created."""
        session_id = "test_browser_session"
        
        # Get or create session
        session = await browser_manager.get_session(
            session_id=session_id,
            browser_type="chromium",
            headless=True
        )
        
        assert session is not None
        # BrowserSession doesn't store session_id, it's the key in manager's dict
        assert session.browser is not None
        assert session.page is not None
        
        # Cleanup
        await browser_manager.close_session(session_id)
    
    @pytest.mark.asyncio
    async def test_browser_session_isolation(self, browser_manager):
        """Test browser sessions are isolated."""
        session_1 = "test_session_1"
        session_2 = "test_session_2"
        
        # Create two sessions
        s1 = await browser_manager.get_session(session_1, "chromium", True)
        s2 = await browser_manager.get_session(session_2, "chromium", True)
        
        # Verify they're different (different browser instances)
        assert s1.browser != s2.browser
        assert s1.page != s2.page
        
        # Cleanup
        await browser_manager.close_session(session_1)
        await browser_manager.close_session(session_2)
    
    @pytest.mark.asyncio
    async def test_browser_navigate_action(self, browser_manager):
        """Test browser navigate action works."""
        session_id = "test_navigate_session"
        
        # Navigate to a page
        result = await browser_manager.navigate(
            session_id=session_id,
            url="https://example.com",
            browser_type="chromium",
            headless=True
        )
        
        assert result["status"] == "success"
        assert result["url"] == "https://example.com"
        
        # Cleanup
        await browser_manager.close_session(session_id)
    
    @pytest.mark.asyncio
    async def test_browser_list_tabs(self, browser_manager):
        """Test browser list tabs action works."""
        session_id = "test_tabs_session"
        
        # Create session
        await browser_manager.get_session(session_id, "chromium", True)
        
        # List tabs
        result = await browser_manager.list_tabs(
            session_id=session_id,
            browser_type="chromium",
            headless=True
        )
        
        assert result["status"] == "success"
        assert "tabs" in result
        assert result["count"] >= 1  # At least the main tab
        
        # Cleanup
        await browser_manager.close_session(session_id)
    
    def test_browser_config_defaults(self, test_config):
        """Test browser configuration has sensible defaults."""
        # Browser type should be valid
        assert test_config.browser.browser_type in ["chromium", "firefox", "webkit"]
        
        # Headless should be configured
        assert test_config.browser.headless in [True, False]
        
        # Max sessions should be reasonable
        assert 1 <= test_config.browser.max_sessions <= 100
        
        # Session timeout should be reasonable
        assert 1 <= test_config.browser.session_timeout_minutes <= 1440  # 1 min to 1 day

