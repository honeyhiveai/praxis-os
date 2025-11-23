"""
Unit tests for orientation query list hook in StandardsIndex (RAG layer).

Tests the query interception mechanism that triggers when AI agents execute
the magic query "orientation query list" to discover orientation queries.

After refactoring 2025-11-23, the hook now lives in StandardsIndex.search()
(RAG layer) instead of SearchTool (tool layer) for cleaner architecture.

Test Coverage:
    - Exact query string triggers hook
    - Similar queries don't trigger hook (case-sensitive)
    - Hook returns formatted query list (as SearchResult objects)
    - Hook merges base + project queries
    - Hook handles missing project queries gracefully
    - Hook handles config errors gracefully

Traceability:
    Addendum 2025-11-23: Hook Implementation (Refactored to RAG layer)
    FR-019: Project Orientation System
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from ouroboros.subsystems.rag.standards.container import StandardsIndex
from ouroboros.config.schemas.indexes import StandardsIndexConfig, FTSConfig, VectorConfig
from ouroboros.config.schemas.orientation import (
    OrientationQuery,
    BaseOrientation,
    ProjectOrientationQueries,
    OrientationConfig
)


class TestOrientationQueryListHook:
    """Test orientation query list hook mechanism in StandardsIndex."""
    
    @pytest.fixture
    def standards_config(self, tmp_path):
        """Create mock StandardsIndexConfig for testing."""
        # Use Mock to avoid complex config initialization
        config = Mock()
        config.sources = ["standards"]
        return config
    
    @pytest.fixture
    def mock_config_with_base_and_project(self):
        """Mock config with both base and project queries."""
        config = Mock()
        
        # Base queries
        base_queries = [
            OrientationQuery(
                query="stateless AI architecture",
                priority=1,
                category="foundational",
                description="Core architectural truth"
            ),
            OrientationQuery(
                query="query-first decision protocol",
                priority=2,
                category="behavioral",
                description="Decision protocol"
            ),
        ]
        
        # Project queries
        project_queries = [
            OrientationQuery(
                query="dogfooding model development",
                priority=1,
                category="development",
                description="Learn how this project works"
            ),
        ]
        
        config.orientation = OrientationConfig(
            base=BaseOrientation(queries=base_queries),
            project=ProjectOrientationQueries(queries=project_queries)
        )
        
        return config
    
    @pytest.fixture
    def mock_config_base_only(self):
        """Mock config with only base queries (no project queries)."""
        config = Mock()
        
        base_queries = [
            OrientationQuery(
                query="stateless AI architecture",
                priority=1,
                category="foundational",
                description="Core architectural truth"
            ),
        ]
        
        config.orientation = OrientationConfig(
            base=BaseOrientation(queries=base_queries),
            project=None  # No project queries
        )
        
        return config
    
    def test_exact_query_triggers_hook(self, standards_config, mock_config_with_base_and_project, tmp_path):
        """Test that exact query string 'orientation query list' triggers hook."""
        # Create StandardsIndex with full_config
        with patch('ouroboros.subsystems.rag.standards.container.SemanticIndex'):
            index = StandardsIndex(
                config=standards_config,
                base_path=tmp_path,
                full_config=mock_config_with_base_and_project
            )
            
            # Execute the magic query
            results = index.search(query="orientation query list")
            
            # Should return orientation queries as SearchResult objects
            assert isinstance(results, list)
            assert len(results) == 3  # 2 base + 1 project
            
            # Check first result structure (SearchResult)
            first_result = results[0]
            assert hasattr(first_result, 'content')
            assert hasattr(first_result, 'metadata')
            assert first_result.metadata['type'] == 'orientation_query'
            assert first_result.metadata['source'] in ['base', 'project']
    
    def test_similar_queries_dont_trigger_hook(self, standards_config, mock_config_with_base_and_project, tmp_path):
        """Test that similar queries use normal search (case-sensitive)."""
        test_queries = [
            "orientation query",  # Missing "list"
            "orientation list",  # Missing "query"
            "Orientation Query List",  # Wrong case
            "orientation query list ",  # Trailing space
            " orientation query list",  # Leading space
        ]
        
        with patch('ouroboros.subsystems.rag.standards.container.SemanticIndex') as mock_semantic:
            # Mock normal search to return empty list
            mock_semantic_instance = Mock()
            mock_semantic_instance.search = Mock(return_value=[])
            mock_semantic.return_value = mock_semantic_instance
            
            index = StandardsIndex(
                config=standards_config,
                base_path=tmp_path,
                full_config=mock_config_with_base_and_project
            )
            
            for query in test_queries:
                # Reset mock
                mock_semantic_instance.search.reset_mock()
                
                # Execute query (should go to normal search, not hook)
                results = index.search(query=query)
                
                # Should call normal search
                mock_semantic_instance.search.assert_called_once()
                
                # Should not return orientation queries
                assert results == []
    
    def test_hook_returns_formatted_query_list(self, standards_config, mock_config_with_base_and_project, tmp_path):
        """Test hook returns SearchResult objects with proper structure."""
        with patch('ouroboros.subsystems.rag.standards.container.SemanticIndex'):
            index = StandardsIndex(
                config=standards_config,
                base_path=tmp_path,
                full_config=mock_config_with_base_and_project
            )
            
            results = index.search(query="orientation query list")
            
            # Check result format (SearchResult objects)
            assert len(results) > 0
            
            first_result = results[0]
            # SearchResult attributes
            assert hasattr(first_result, 'content')
            assert hasattr(first_result, 'metadata')
            assert hasattr(first_result, 'file_path')
            assert hasattr(first_result, 'relevance_score')
            
            # Check metadata structure
            metadata = first_result.metadata
            assert 'query_number' in metadata
            assert 'source' in metadata  # "base" or "project"
            assert 'priority' in metadata
            assert 'category' in metadata
            assert 'description' in metadata
            assert 'type' in metadata
            assert metadata['type'] == 'orientation_query'
    
    def test_hook_merges_base_and_project_queries(self, standards_config, mock_config_with_base_and_project, tmp_path):
        """Test hook returns base queries first, then project queries."""
        with patch('ouroboros.subsystems.rag.standards.container.SemanticIndex'):
            index = StandardsIndex(
                config=standards_config,
                base_path=tmp_path,
                full_config=mock_config_with_base_and_project
            )
            
            results = index.search(query="orientation query list")
            
            # Should have both base and project queries
            assert len(results) == 3  # 2 base + 1 project
            
            # Check order: base queries first
            sources = [r.metadata['source'] for r in results]
            
            # All "base" should come before all "project"
            base_indices = [i for i, s in enumerate(sources) if s == "base"]
            project_indices = [i for i, s in enumerate(sources) if s == "project"]
            
            if base_indices and project_indices:
                assert max(base_indices) < min(project_indices), \
                    "Base queries should come before project queries"
    
    def test_hook_handles_missing_project_queries(self, standards_config, mock_config_base_only, tmp_path):
        """Test hook gracefully handles missing project queries."""
        with patch('ouroboros.subsystems.rag.standards.container.SemanticIndex'):
            index = StandardsIndex(
                config=standards_config,
                base_path=tmp_path,
                full_config=mock_config_base_only
            )
            
            results = index.search(query="orientation query list")
            
            # Should succeed with only base queries
            assert len(results) == 1  # Only base query
            assert results[0].metadata['source'] == 'base'
    
    def test_hook_handles_no_config_gracefully(self, standards_config, tmp_path):
        """Test hook returns empty list when full_config is None."""
        with patch('ouroboros.subsystems.rag.standards.container.SemanticIndex'):
            # Create index without full_config
            index = StandardsIndex(
                config=standards_config,
                base_path=tmp_path,
                full_config=None  # No config
            )
            
            results = index.search(query="orientation query list")
            
            # Should return empty list gracefully
            assert results == []
    
    def test_hook_sorts_queries_by_priority(self, standards_config, tmp_path):
        """Test that queries are sorted by priority."""
        # Create config with mixed priorities
        config = Mock()
        base_queries = [
            OrientationQuery(query="Priority 3", priority=3, category="test", description=""),
            OrientationQuery(query="Priority 1", priority=1, category="test", description=""),
            OrientationQuery(query="Priority 2", priority=2, category="test", description=""),
        ]
        config.orientation = OrientationConfig(
            base=BaseOrientation(queries=base_queries),
            project=None
        )
        
        with patch('ouroboros.subsystems.rag.standards.container.SemanticIndex'):
            index = StandardsIndex(
                config=standards_config,
                base_path=tmp_path,
                full_config=config
            )
            
            results = index.search(query="orientation query list")
            
            # Check priorities are in order
            priorities = [r.metadata['priority'] for r in results]
            assert priorities == [1, 2, 3], "Queries should be sorted by priority"
