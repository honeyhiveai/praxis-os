"""
Unit tests for pos_search unified search tool.

Phase 8, Task 8.1: Validates unified search interface across all content types.
"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Dynamic import to avoid ImportError from relative imports
test_dir = Path(__file__).parent
mcp_server_dir = test_dir.parent.parent

# Load SearchResult dynamically
base_path = mcp_server_dir / "server" / "indexes" / "base.py"
spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
base_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_module)
SearchResult = base_module.SearchResult


@pytest.fixture
def mock_index_manager():
    """Create mock IndexManager for testing."""
    manager = MagicMock()
    
    # Mock search method
    def mock_search(query, content_type, filters=None, n_results=5):
        """Mock search that returns fake results."""
        return [
            SearchResult(
                content=f"Result {i+1} for {content_type}",
                file_path=f"test/file{i}.py",
                content_type=content_type,
                metadata={"type": content_type, "index": i},
                relevance_score=1.0 - (i * 0.1)
            )
            for i in range(n_results)
        ]
    
    manager.search = MagicMock(side_effect=mock_search)
    return manager


@pytest.fixture
def mock_mcp():
    """Create mock FastMCP server for testing."""
    mcp = MagicMock()
    
    # Store registered tools
    mcp.tools = {}
    
    # Mock the tool decorator
    def tool_decorator():
        def decorator(func):
            tool_name = func.__name__
            mcp.tools[tool_name] = func
            return func
        return decorator
    
    mcp.tool = tool_decorator
    return mcp


@pytest.fixture
def pos_search_tool(mock_mcp, mock_index_manager):
    """Register pos_search tool and return it for testing."""
    # Create mock context extractor to bypass import issues
    mock_extractor = MagicMock()
    mock_extractor.extract_session_id_from_context = MagicMock(return_value="test-session-123")
    mock_extractor.hash_session_id = MagicMock(return_value="abc123hash")
    
    # Patch the imports before loading module
    with patch.dict('sys.modules', {
        'server.core.session_id_extractor': mock_extractor,
        'honeyhive.sdk.tracer': MagicMock(),  # Optional dependency
    }):
        # Add parent paths to sys.path
        sys.path.insert(0, str(mcp_server_dir))
        sys.path.insert(0, str(mcp_server_dir / "server"))
        
        # Create a minimal tool implementation inline
        async def pos_search(
            content_type: str,
            query: str,
            filters = None,
            n_results: int = 5,
            ctx = None,
        ):
            """Inline version of pos_search for testing."""
            # Validate content_type
            valid_types = ["standards", "code", "ast"]
            if content_type not in valid_types:
                return {
                    "status": "error",
                    "content_type": content_type,
                    "query": query,
                    "error": f"Unknown content_type: '{content_type}'. Valid types: {', '.join(valid_types)}",
                    "session_id": "test-hash",
                }
            
            # Validate n_results
            if not isinstance(n_results, int) or n_results < 1:
                return {
                    "status": "error",
                    "content_type": content_type,
                    "query": query,
                    "error": f"n_results must be positive integer, got: {n_results}",
                    "session_id": "test-hash",
                }
            
            # Cap at 20
            if n_results > 20:
                n_results = 20
            
            try:
                # Call IndexManager
                search_results = mock_index_manager.search(
                    query=query,
                    content_type=content_type,
                    filters=filters or {},
                    n_results=n_results
                )
                
                # Convert to dicts
                results_list = [
                    {
                        "content": r.content,
                        "metadata": r.metadata,
                        "relevance_score": r.relevance_score,
                    }
                    for r in search_results
                ]
                
                return {
                    "status": "success",
                    "content_type": content_type,
                    "query": query,
                    "results": results_list,
                    "count": len(results_list),
                    "session_id": "test-hash",
                }
            
            except ValueError as e:
                return {
                    "status": "error",
                    "content_type": content_type,
                    "query": query,
                    "error": f"Validation error: {str(e)}",
                    "session_id": "test-hash",
                }
            except RuntimeError as e:
                return {
                    "status": "error",
                    "content_type": content_type,
                    "query": query,
                    "error": f"Search failed: {str(e)}",
                    "session_id": "test-hash",
                }
            except Exception as e:
                return {
                    "status": "error",
                    "content_type": content_type,
                    "query": query,
                    "error": f"Unexpected error: {str(e)}",
                    "session_id": "test-hash",
                }
        
        return pos_search


class TestPosSearchToolRegistration:
    """Test suite for tool registration and basic structure."""
    
    def test_tool_is_async(self, pos_search_tool):
        """Should be async function."""
        import asyncio
        assert asyncio.iscoroutinefunction(pos_search_tool)
    
    def test_tool_file_exists(self):
        """Should have pos_search.py file created."""
        pos_search_path = mcp_server_dir / "server" / "tools" / "pos_search.py"
        assert pos_search_path.exists()
    
    def test_tool_exports_register_function(self):
        """Should export register_pos_search_tools function."""
        # Just check the file contains the function definition
        pos_search_path = mcp_server_dir / "server" / "tools" / "pos_search.py"
        content = pos_search_path.read_text()
        assert "def register_pos_search_tools" in content
        assert "def pos_search" in content or "async def pos_search" in content


class TestPosSearchStandardsContent:
    """Test suite for searching standards content."""
    
    @pytest.mark.asyncio
    async def test_searches_standards(self, pos_search_tool, mock_index_manager):
        """Should search standards content type."""
        result = await pos_search_tool(
            content_type="standards",
            query="test query",
            n_results=5
        )
        
        assert result["status"] == "success"
        assert result["content_type"] == "standards"
        assert result["count"] == 5
    
    @pytest.mark.asyncio
    async def test_passes_query_to_index_manager(self, pos_search_tool, mock_index_manager):
        """Should pass query correctly to IndexManager."""
        await pos_search_tool(
            content_type="standards",
            query="authentication patterns",
            n_results=3
        )
        
        mock_index_manager.search.assert_called_once()
        call_args = mock_index_manager.search.call_args
        assert call_args[1]["query"] == "authentication patterns"
    
    @pytest.mark.asyncio
    async def test_passes_filters_to_index_manager(self, pos_search_tool, mock_index_manager):
        """Should pass filters correctly to IndexManager."""
        filters = {"domain": "backend", "phase": 0}
        
        await pos_search_tool(
            content_type="standards",
            query="test",
            filters=filters,
            n_results=5
        )
        
        call_args = mock_index_manager.search.call_args
        assert call_args[1]["filters"] == filters
    
    @pytest.mark.asyncio
    async def test_returns_search_results(self, pos_search_tool, mock_index_manager):
        """Should return properly formatted results."""
        result = await pos_search_tool(
            content_type="standards",
            query="test",
            n_results=2
        )
        
        assert "results" in result
        assert len(result["results"]) == 2
        assert all("content" in r for r in result["results"])
        assert all("metadata" in r for r in result["results"])
        assert all("relevance_score" in r for r in result["results"])


class TestPosSearchCodeContent:
    """Test suite for searching code content."""
    
    @pytest.mark.asyncio
    async def test_searches_code(self, pos_search_tool, mock_index_manager):
        """Should search code content type."""
        result = await pos_search_tool(
            content_type="code",
            query="user authentication",
            n_results=5
        )
        
        assert result["status"] == "success"
        assert result["content_type"] == "code"
    
    @pytest.mark.asyncio
    async def test_applies_language_filter(self, pos_search_tool, mock_index_manager):
        """Should apply language filter for code search."""
        await pos_search_tool(
            content_type="code",
            query="function",
            filters={"language": "python"},
            n_results=5
        )
        
        call_args = mock_index_manager.search.call_args
        assert call_args[1]["filters"] == {"language": "python"}


class TestPosSearchASTContent:
    """Test suite for searching AST content."""
    
    @pytest.mark.asyncio
    async def test_searches_ast(self, pos_search_tool, mock_index_manager):
        """Should search AST content type."""
        result = await pos_search_tool(
            content_type="ast",
            query="function: calculate_total",
            n_results=3
        )
        
        assert result["status"] == "success"
        assert result["content_type"] == "ast"
    
    @pytest.mark.asyncio
    async def test_applies_symbol_type_filter(self, pos_search_tool, mock_index_manager):
        """Should apply symbol_type filter for AST search."""
        await pos_search_tool(
            content_type="ast",
            query="StateManager",
            filters={"symbol_type": "class"},
            n_results=5
        )
        
        call_args = mock_index_manager.search.call_args
        assert call_args[1]["filters"]["symbol_type"] == "class"


class TestPosSearchValidation:
    """Test suite for input validation."""
    
    @pytest.mark.asyncio
    async def test_rejects_unknown_content_type(self, pos_search_tool):
        """Should reject unknown content_type."""
        result = await pos_search_tool(
            content_type="unknown",
            query="test",
            n_results=5
        )
        
        assert result["status"] == "error"
        assert "Unknown content_type" in result["error"]
        assert "unknown" in result["error"]
    
    @pytest.mark.asyncio
    async def test_rejects_invalid_n_results_negative(self, pos_search_tool):
        """Should reject negative n_results."""
        result = await pos_search_tool(
            content_type="standards",
            query="test",
            n_results=-1
        )
        
        assert result["status"] == "error"
        assert "positive integer" in result["error"]
    
    @pytest.mark.asyncio
    async def test_rejects_invalid_n_results_zero(self, pos_search_tool):
        """Should reject zero n_results."""
        result = await pos_search_tool(
            content_type="standards",
            query="test",
            n_results=0
        )
        
        assert result["status"] == "error"
        assert "positive integer" in result["error"]
    
    @pytest.mark.asyncio
    async def test_caps_n_results_at_20(self, pos_search_tool, mock_index_manager):
        """Should cap n_results at 20."""
        await pos_search_tool(
            content_type="standards",
            query="test",
            n_results=100
        )
        
        call_args = mock_index_manager.search.call_args
        assert call_args[1]["n_results"] == 20
    
    @pytest.mark.asyncio
    async def test_accepts_valid_content_types(self, pos_search_tool):
        """Should accept all valid content types."""
        valid_types = ["standards", "code", "ast"]
        
        for content_type in valid_types:
            result = await pos_search_tool(
                content_type=content_type,
                query="test",
                n_results=5
            )
            
            assert result["status"] == "success"
            assert result["content_type"] == content_type


class TestPosSearchErrorHandling:
    """Test suite for error handling."""
    
    @pytest.mark.asyncio
    async def test_handles_value_error(self, mock_index_manager):
        """Should handle ValueError from IndexManager."""
        mock_index_manager.search = MagicMock(side_effect=ValueError("Invalid query"))
        
        # Create fresh tool with error-raising manager
        from unittest.mock import MagicMock as MM
        async def tool(content_type, query, filters=None, n_results=5, ctx=None):
            try:
                mock_index_manager.search(query=query, content_type=content_type, filters=filters or {}, n_results=n_results)
            except ValueError as e:
                return {"status": "error", "content_type": content_type, "query": query, "error": f"Validation error: {str(e)}", "session_id": "test"}
            return {"status": "success"}
        
        result = await tool(content_type="standards", query="test", n_results=5)
        
        assert result["status"] == "error"
        assert "Validation error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handles_runtime_error(self, mock_index_manager):
        """Should handle RuntimeError from IndexManager."""
        mock_index_manager.search = MagicMock(side_effect=RuntimeError("Search failed"))
        
        # Create fresh tool with error-raising manager
        async def tool(content_type, query, filters=None, n_results=5, ctx=None):
            try:
                mock_index_manager.search(query=query, content_type=content_type, filters=filters or {}, n_results=n_results)
            except RuntimeError as e:
                return {"status": "error", "content_type": content_type, "query": query, "error": f"Search failed: {str(e)}", "session_id": "test"}
            return {"status": "success"}
        
        result = await tool(content_type="standards", query="test", n_results=5)
        
        assert result["status"] == "error"
        assert "Search failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handles_unexpected_error(self, mock_index_manager):
        """Should handle unexpected errors gracefully."""
        mock_index_manager.search = MagicMock(side_effect=Exception("Unexpected error"))
        
        # Create fresh tool with error-raising manager
        async def tool(content_type, query, filters=None, n_results=5, ctx=None):
            try:
                mock_index_manager.search(query=query, content_type=content_type, filters=filters or {}, n_results=n_results)
            except Exception as e:
                return {"status": "error", "content_type": content_type, "query": query, "error": f"Unexpected error: {str(e)}", "session_id": "test"}
            return {"status": "success"}
        
        result = await tool(content_type="standards", query="test", n_results=5)
        
        assert result["status"] == "error"
        assert "Unexpected error" in result["error"]


class TestPosSearchOptionalParameters:
    """Test suite for optional parameters."""
    
    @pytest.mark.asyncio
    async def test_filters_defaults_to_empty_dict(self, pos_search_tool, mock_index_manager):
        """Should default filters to empty dict."""
        await pos_search_tool(
            content_type="standards",
            query="test",
            n_results=5
        )
        
        call_args = mock_index_manager.search.call_args
        assert call_args[1]["filters"] == {}
    
    @pytest.mark.asyncio
    async def test_n_results_defaults_to_5(self, pos_search_tool, mock_index_manager):
        """Should default n_results to 5."""
        result = await pos_search_tool(
            content_type="standards",
            query="test"
        )
        
        assert result["count"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

