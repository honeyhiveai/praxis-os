"""
Integration tests for Query Gamification System with search_standards().

Tests the full integration of gamification into the RAG search tool,
verifying prepend injection, progressive stats, graceful degradation,
and session isolation.
"""

from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from mcp_server.core.query_tracker import get_tracker


@pytest.fixture(autouse=True)
def reset_tracker():
    """Reset tracker and session state before each test."""
    from mcp_server.core import session_id_extractor

    tracker = get_tracker()
    tracker._session_stats = {}  # pylint: disable=protected-access

    # Also reset session_id_extractor state
    session_id_extractor._session_states = {}  # pylint: disable=protected-access

    yield

    tracker._session_stats = {}  # pylint: disable=protected-access
    session_id_extractor._session_states = {}  # pylint: disable=protected-access


@pytest.fixture
def mock_rag_engine():
    """Create mock RAG engine with test response."""
    mock_result = Mock()
    mock_result.chunks = [
        {
            "content": "Test content 1",
            "file_path": "test/file1.md",
            "section_header": "Section 1",
            "tokens": 50,
        },
        {
            "content": "Test content 2",
            "file_path": "test/file2.md",
            "section_header": "Section 2",
            "tokens": 40,
        },
    ]
    mock_result.relevance_scores = [0.9, 0.8]
    mock_result.total_tokens = 90
    mock_result.retrieval_method = "vector"
    mock_result.query_time_ms = 45.5

    mock_engine = Mock()
    mock_engine.search.return_value = mock_result
    return mock_engine


@pytest.fixture
def search_standards_func(mock_rag_engine):
    """Create search_standards function for testing."""
    from mcp_server.server.tools.rag_tools import register_rag_tools

    # Create mock MCP that captures the registered function
    registered_func = None

    class MockMCP:
        def tool(self):
            def decorator(func):
                nonlocal registered_func
                registered_func = func
                return func

            return decorator

    mcp = MockMCP()
    register_rag_tools(mcp, mock_rag_engine)

    return registered_func


@pytest.mark.asyncio
async def test_search_returns_results_with_prepend(search_standards_func):
    """Test that search_standards returns results with gamification prepend."""
    result = await search_standards_func("What is validation?")

    assert "results" in result
    assert len(result["results"]) >= 1

    first_result = result["results"][0]
    assert "content" in first_result
    assert first_result["content"].startswith("🔍🔍🔍🔍🔍")
    assert "QUERIES = KNOWLEDGE = ACCURACY = QUALITY" in first_result["content"]


@pytest.mark.asyncio
async def test_prepend_format_matches_specification(search_standards_func):
    """Test that prepend format matches specs.md requirements."""
    result = await search_standards_func("What is validation?")

    first_content = result["results"][0]["content"]
    lines = first_content.split("\n")

    # Check header line
    assert lines[0] == "🔍🔍🔍🔍🔍 QUERIES = KNOWLEDGE = ACCURACY = QUALITY ⭐⭐⭐⭐⭐"

    # Check blank line
    assert lines[1] == ""

    # Check progress line (format: "Queries: X/5 | Unique: Y | Angles: ...")
    assert "Queries:" in lines[2]
    assert "/5" in lines[2]
    assert "Unique:" in lines[2]
    assert "Angles:" in lines[2]

    # Check suggestion or completion line
    assert lines[3].startswith("💡") or lines[3].startswith("🎉")

    # Check separator
    assert "---" in first_content


@pytest.mark.asyncio
async def test_progressive_stats_across_queries(search_standards_func):
    """Test that stats progress across multiple queries in same session."""
    # Mock session ID to ensure same session
    with patch(
        "mcp_server.server.tools.rag_tools.extract_session_id_from_context"
    ) as mock_extract:
        mock_extract.return_value = "test_session_progressive"

        # First query
        result1 = await search_standards_func("What is validation?")
        content1 = result1["results"][0]["content"]
        assert "Queries: 1/5" in content1
        assert "Unique: 1" in content1

        # Second query
        result2 = await search_standards_func("Where is validation implemented?")
        content2 = result2["results"][0]["content"]
        assert "Queries: 2/5" in content2
        assert "Unique: 2" in content2

        # Third query
        result3 = await search_standards_func("How to use validation?")
        content3 = result3["results"][0]["content"]
        assert "Queries: 3/5" in content3
        assert "Unique: 3" in content3


@pytest.mark.asyncio
async def test_graceful_degradation_on_gamification_error(search_standards_func):
    """Test that search still works when gamification fails."""
    # Mock tracker to raise exception
    with patch("mcp_server.server.tools.rag_tools.get_tracker") as mock_get_tracker:
        mock_tracker = Mock()
        mock_tracker.record_query.side_effect = RuntimeError("Tracker failure")
        mock_get_tracker.return_value = mock_tracker

        # Search should still work
        result = await search_standards_func("What is validation?")

        assert "results" in result
        assert len(result["results"]) >= 1
        # Results should be unmodified (no gamification prepend)
        assert "error" not in result


@pytest.mark.asyncio
async def test_session_isolation(search_standards_func, mock_rag_engine):
    """Test that different sessions have independent stats."""
    # Session 1: 2 queries
    with patch(
        "mcp_server.server.tools.rag_tools.extract_session_id_from_context"
    ) as mock_extract:
        mock_extract.return_value = "session_1"

        result1a = await search_standards_func("What is validation?")
        result1b = await search_standards_func("Where is validation?")

        content1b = result1b["results"][0]["content"]
        assert "Queries: 2/5" in content1b

    # Session 2: 1 query (should start fresh)
    with patch(
        "mcp_server.server.tools.rag_tools.extract_session_id_from_context"
    ) as mock_extract:
        mock_extract.return_value = "session_2"

        result2a = await search_standards_func("What is validation?")

        content2a = result2a["results"][0]["content"]
        assert "Queries: 1/5" in content2a  # Fresh session!


@pytest.mark.asyncio
async def test_backward_compatibility_function_signature(search_standards_func):
    """Test that function signature is backward compatible."""
    import inspect

    sig = inspect.signature(search_standards_func)
    params = list(sig.parameters.keys())

    # Required parameters
    assert "query" in params

    # Optional parameters
    assert "n_results" in params
    assert "filter_phase" in params
    assert "filter_tags" in params

    # No new required parameters added
    assert sig.parameters["n_results"].default == 5
    assert sig.parameters["filter_phase"].default is None
    assert sig.parameters["filter_tags"].default is None


@pytest.mark.asyncio
async def test_second_result_unchanged(search_standards_func):
    """Test that second and subsequent results don't have prepend."""
    result = await search_standards_func("What is validation?")

    assert len(result["results"]) >= 2

    # First result has prepend
    first_content = result["results"][0]["content"]
    assert first_content.startswith("🔍🔍🔍🔍🔍")

    # Second result does NOT have prepend (original content)
    second_content = result["results"][1]["content"]
    assert not second_content.startswith("🔍🔍🔍🔍🔍")
    assert second_content == "Test content 2"


@pytest.mark.asyncio
async def test_angle_coverage_visualization(search_standards_func):
    """Test that angle coverage is visualized correctly."""
    # First query: definition angle
    result1 = await search_standards_func("What is validation?")
    content1 = result1["results"][0]["content"]
    assert "📖✓" in content1  # Definition covered

    # Second query: location angle
    result2 = await search_standards_func("Where is validation?")
    content2 = result2["results"][0]["content"]
    assert "📖✓" in content2  # Still covered
    assert "📍✓" in content2  # Location covered

    # Third query: practical angle
    result3 = await search_standards_func("How to use validation?")
    content3 = result3["results"][0]["content"]
    assert "📖✓" in content3
    assert "📍✓" in content3
    assert "🔧✓" in content3  # Practical covered
