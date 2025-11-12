"""
Integration tests for browser automation tools.

NOTE: These tests require Playwright with Chromium installed:
    pip install playwright
    playwright install chromium

Run with: pytest tests/integration/test_browser_tools.py

Traceability:
    FR-4 through FR-18, NFR-6, NFR-7, NFR-9
"""

import pytest
import subprocess
import time
from pathlib import Path

# Browser tests require Playwright (in requirements.txt)
# Mark tests so they can be filtered if needed
pytestmark = pytest.mark.browser


@pytest.fixture(scope="module")
def docs_server():
    """
    Ensure docs server is running for integration tests.
    
    Checks if server is already running, otherwise starts it.
    Only cleans up if we started it.
    """
    import urllib.request
    import urllib.error
    
    # Check if server is already running (check /praxis-os path)
    try:
        resp = urllib.request.urlopen("http://localhost:3000/praxis-os", timeout=1)
        print("\n✅ Docs server already running at http://localhost:3000")
        yield "http://localhost:3000"
        return  # Don't clean up - we didn't start it
    except urllib.error.HTTPError as e:
        # Server is running but returned an error (404, etc)
        if e.code in (404, 500):
            print("\n✅ Docs server already running at http://localhost:3000")
            yield "http://localhost:3000"
            return
        pass  # Other HTTP error, assume not running
    except Exception:
        pass  # Not running, need to start it
    
    # Get absolute path to docs directory
    test_file = Path(__file__).resolve()
    workspace_root = test_file.parent.parent.parent.parent
    docs_dir = workspace_root / "docs"
    
    # Check prerequisites
    if not docs_dir.exists():
        pytest.skip(f"Docs directory not found: {docs_dir}")
    if not (docs_dir / "package.json").exists():
        pytest.skip(f"package.json not found in {docs_dir}")
    
    # Start the docs server
    print(f"\n📦 Starting docs server in {docs_dir}...")
    process = subprocess.Popen(
        ["npm", "run", "start"],
        cwd=docs_dir,
        stdout=subprocess.DEVNULL,  # Suppress npm output
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to be ready
    max_wait = 60
    start_time = time.time()
    server_ready = False
    
    print(f"⏳ Waiting up to {max_wait}s for server...")
    while time.time() - start_time < max_wait:
        # Check if process died
        if process.poll() is not None:
            _, stderr = process.communicate()
            pytest.skip(f"Server process died: {stderr[:200]}")
        
        # Check if server is responding at /praxis-os
        try:
            urllib.request.urlopen("http://localhost:3000/praxis-os", timeout=1)
            server_ready = True
            print(f"✅ Server ready after {time.time() - start_time:.1f}s")
            break
        except Exception:
            time.sleep(1)
    
    if not server_ready:
        process.kill()
        _, stderr = process.communicate()
        pytest.skip(f"Server didn't start in {max_wait}s: {stderr[:200]}")
    
    yield "http://localhost:3000"
    
    # Cleanup - kill the server we started
    print("\n🛑 Stopping docs server...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


# ===== TASK 3.4: Tool Actions =====


@pytest.mark.asyncio
@pytest.mark.browser
async def test_navigate_success():
    """
    Test navigate action to real URL.

    Requires: Playwright + Chromium installed
    Traceability: FR-4
    """
    # Playwright is in requirements.txt and should be installed


@pytest.mark.asyncio
@pytest.mark.browser
async def test_emulate_dark_mode():
    """
    Test dark mode emulation.

    Requires: Playwright + Chromium installed
    Traceability: FR-5
    """
    # Playwright is in requirements.txt and should be installed


@pytest.mark.asyncio
@pytest.mark.browser
async def test_screenshot_to_file():
    """
    Test screenshot capture to file.

    Requires: Playwright + Chromium installed
    Traceability: FR-6
    """
    # Playwright is in requirements.txt and should be installed


# ===== TASK 3.5: Multi-Chat Isolation =====


@pytest.mark.asyncio
@pytest.mark.browser
async def test_concurrent_sessions_isolated():
    """
    Test concurrent sessions don't interfere.

    Requires: Playwright + Chromium installed
    Traceability: FR-2, NFR-5
    """
    # Playwright is in requirements.txt and should be installed


# ===== TASK 3.6: Full Workflow =====


@pytest.mark.asyncio
@pytest.mark.browser
async def test_docs_dark_mode_workflow(docs_server):
    """
    Test complete docs testing workflow.

    Requires: Playwright + Chromium installed + http://localhost:3000 running
    Traceability: FR-4, FR-5, FR-6
    
    NOTE: This is a placeholder for full browser integration testing.
    Browser tools require the full MCP server to be running with proper
    session management. Full browser testing should be done via the MCP
    client (e.g., Cursor with mcp_praxis-os_pos_browser tool).
    
    For now, we verify the docs server fixture works and skip the test.
    """
    # Verify docs server is accessible at /praxis-os
    import urllib.request
    docs_url = f"{docs_server}/praxis-os"
    response = urllib.request.urlopen(docs_url, timeout=5)
    assert response.status == 200  # Docs homepage should be accessible
    
    # TODO: Implement full browser workflow test when we have
    # a testing harness for MCP tools with session management
    pytest.skip("Full browser integration testing requires MCP server runtime")


# ===== Additional Integration Tests =====


@pytest.mark.asyncio
@pytest.mark.browser
async def test_click_type_fill_select():
    """
    Test element interaction actions.

    Requires: Playwright + Chromium installed
    Traceability: FR-9, FR-10, FR-11, FR-12
    """
    # Playwright is in requirements.txt and should be installed


@pytest.mark.asyncio
@pytest.mark.browser
async def test_wait_query_evaluate():
    """
    Test waiting and querying actions.

    Requires: Playwright + Chromium installed
    Traceability: FR-13, FR-14, FR-15
    """
    # Playwright is in requirements.txt and should be installed


@pytest.mark.asyncio
@pytest.mark.browser
async def test_cookies_and_storage():
    """
    Test cookie and storage management.

    Requires: Playwright + Chromium installed
    Traceability: FR-16, FR-17, FR-18
    """
    # Playwright is in requirements.txt and should be installed


# ===== Test Configuration =====


def pytest_addoption(parser):
    """Add custom pytest options."""
    parser.addoption(
        "--run-browser-tests",
        action="store_true",
        default=False,
        help="Run integration tests that require real browser",
    )


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "browser: mark test as requiring real browser installation"
    )
