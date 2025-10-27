"""
Pytest configuration for prAxIs OS tests.

Registers custom pytest options and markers.
"""

import pytest


def pytest_addoption(parser):
    """Add custom pytest command-line options."""
    parser.addoption(
        "--run-browser-tests",
        action="store_true",
        default=False,
        help="Run integration tests that require real browser (Playwright)",
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "browser: mark test as requiring real browser installation (Playwright)",
    )
