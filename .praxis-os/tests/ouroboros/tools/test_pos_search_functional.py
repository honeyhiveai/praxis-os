"""
Functional tests for pos_search_project tool.

These tests validate the critical search interface that AI agents use to discover
information across standards, code, AST, and call graphs.

Reference: Primary knowledge discovery tool (identified 2025-11-05)
"""

from unittest.mock import Mock

import pytest

from ouroboros.tools.pos_search_project import SearchTool


class TestPosSearchFunctional:
    """Functional tests for pos_search_project tool."""
    
    @pytest.fixture
    def mock_index_manager(self):
        """Create mock IndexManager for testing."""
        manager = Mock()
        
        # Mock route_action to return dict with results
        manager.route_action = Mock(return_value={
            "results": [
                {"content": "Test standard content", "score": 0.95, "file_path": "standards/test.md"}
            ],
            "count": 1
        })
        
        return manager
    
    @pytest.fixture
    def search_tool(self, mock_index_manager):
        """Create SearchTool instance."""
        mock_mcp = Mock()
        return SearchTool(mock_mcp, mock_index_manager)
    
    # ========================================================================
    # CRITICAL: Standards Search
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_search_standards_basic(self, search_tool, mock_index_manager):
        """
        Test basic standards search (most common use case).
        
        AI agents use this to discover how to do things.
        """
        # Handlers are NOT async, so don't await
        result = search_tool._handle_search_standards(
            query="how to create a workflow"
        )
        
        # Assert: Index manager called
        mock_index_manager.route_action.assert_called_once()
        call_args = mock_index_manager.route_action.call_args
        assert call_args[0][0] == "search_standards"  # First positional arg is action
        assert call_args[1]["query"] == "how to create a workflow"
        
        # Assert: Results returned
        assert "results" in result
        assert len(result["results"]) > 0
        assert "content" in result["results"][0]
    
    @pytest.mark.asyncio
    async def test_search_standards_with_filters(self, search_tool, mock_index_manager):
        """Test standards search with metadata filters."""
        result = search_tool._handle_search_standards(
            query="workflow patterns",
            filters={"domain": "development", "phase": 1}
        )
        
        # Assert: Filters passed to index
        call_args = mock_index_manager.route_action.call_args
        assert call_args[1]["filters"] == {"domain": "development", "phase": 1}
    
    @pytest.mark.asyncio
    async def test_search_standards_n_results(self, search_tool, mock_index_manager):
        """Test limiting search results."""
        result = search_tool._handle_search_standards(
            query="test query",
            n_results=3
        )
        
        # Assert: Result limit passed
        call_args = mock_index_manager.route_action.call_args
        assert call_args[1]["n_results"] == 3
    
    # ========================================================================
    # CRITICAL: Code Search
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_search_code_semantic(self, search_tool, mock_index_manager):
        """
        Test semantic code search.
        
        AI agents use this to find relevant code by meaning.
        """
        result = search_tool._handle_search_code(
            query="function that validates user input"
        )
        
        # Assert: Code search called
        mock_index_manager.route_action.assert_called_once()
        call_args = mock_index_manager.route_action.call_args
        assert call_args[0][0] == "search_code"
        assert call_args[1]["query"] == "function that validates user input"
        
        # Assert: Code results returned
        assert "results" in result
    
    # ========================================================================
    # CRITICAL: AST Search
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_search_ast_structural(self, search_tool, mock_index_manager):
        """
        Test AST structural search.
        
        AI agents use this to find code by structure (not semantics).
        """
        result = search_tool._handle_search_ast(
            query="function definitions named test_*"
        )
        
        # Assert: AST search called
        mock_index_manager.route_action.assert_called_once()
        call_args = mock_index_manager.route_action.call_args
        assert call_args[0][0] == "search_ast"
    
    # ========================================================================
    # CRITICAL: Call Graph Queries
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_find_callers(self, search_tool, mock_index_manager):
        """
        Test finding who calls a function.
        
        Critical for impact analysis during refactoring.
        """
        result = search_tool._handle_find_callers(
            query="test_function"
        )
        
        # Assert: Callers query executed
        mock_index_manager.route_action.assert_called_once()
        call_args = mock_index_manager.route_action.call_args
        assert call_args[0][0] == "find_callers"
        assert call_args[1]["symbol_name"] == "test_function"
    
    @pytest.mark.asyncio
    async def test_find_dependencies(self, search_tool, mock_index_manager):
        """
        Test finding what a function calls.
        
        Critical for understanding dependencies.
        """
        result = search_tool._handle_find_dependencies(
            query="main_function"
        )
        
        # Assert: Dependencies query executed
        mock_index_manager.route_action.assert_called_once()
        call_args = mock_index_manager.route_action.call_args
        assert call_args[0][0] == "find_dependencies"
    
    @pytest.mark.asyncio
    async def test_find_call_paths(self, search_tool, mock_index_manager):
        """
        Test finding call path between two functions.
        
        Critical for understanding execution flow.
        """
        result = search_tool._handle_find_call_paths(
            query="main",
            to_symbol="helper"
        )
        
        # Assert: Call path query executed
        mock_index_manager.route_action.assert_called_once()
        call_args = mock_index_manager.route_action.call_args
        assert call_args[0][0] == "find_call_paths"
        assert call_args[1]["from_symbol"] == "main"  # Fixed: from_symbol not symbol_name
        assert call_args[1]["to_symbol"] == "helper"
    
    # ========================================================================
    # Integration: Multi-Query Workflow
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_multi_angle_query_workflow(self, search_tool, mock_index_manager):
        """
        Test multi-angle querying pattern (reinforcing correct behavior).
        
        AI agents should query multiple times from different angles.
        """
        # Query 1: Standards for "how to"
        search_tool._handle_search_standards(query="how to implement feature X")
        
        # Query 2: Code for "what exists"
        search_tool._handle_search_code(query="existing feature X implementation")
        
        # Query 3: AST for "where is"
        search_tool._handle_search_ast(query="function feature_x")
        
        # Query 4: Graph for "who uses"
        search_tool._handle_find_callers(query="feature_x")
        
        # Assert: All query types executed (multi-angle pattern)
        assert mock_index_manager.route_action.call_count >= 4


class TestPosSearchEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def search_tool(self):
        """Create SearchTool with mock index manager."""
        mock_mcp = Mock()
        mock_index_manager = Mock()
        return SearchTool(mock_mcp, mock_index_manager)
    
    @pytest.mark.asyncio
    async def test_empty_query_handling(self, search_tool):
        """Test handling of empty query string."""
        search_tool.index_manager.route_action = Mock(return_value={"results": [], "count": 0})
        
        result = search_tool._handle_search_standards(query="")
        
        # Assert: Empty query handled gracefully
        assert "results" in result
    
    @pytest.mark.asyncio
    async def test_no_results_handling(self, search_tool):
        """Test handling when no results found."""
        search_tool.index_manager.route_action = Mock(return_value={"results": [], "count": 0})
        
        result = search_tool._handle_search_standards(
            query="nonexistent content that will never match"
        )
        
        # Assert: Empty results handled gracefully
        assert result["results"] == []
    
    @pytest.mark.asyncio
    async def test_max_depth_parameter(self, search_tool):
        """Test max_depth parameter for graph queries."""
        search_tool.index_manager.route_action = Mock(return_value={"results": [], "count": 0})
        
        search_tool._handle_find_callers(
            query="function_name",
            max_depth=5
        )
        
        # Assert: Max depth passed to query
        call_args = search_tool.index_manager.route_action.call_args
        assert call_args[1]["max_depth"] == 5


# Mark all tests as functional
pytestmark = [pytest.mark.functional, pytest.mark.tools, pytest.mark.critical]

