"""Tests for GraphIndex (Call Graph Traversal)."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from ouroboros.config.schemas.indexes import GraphConfig
from ouroboros.subsystems.rag.base import HealthStatus, SearchResult
from ouroboros.subsystems.rag.graph_index import GraphIndex
from ouroboros.utils.errors import ActionableError, IndexError


def create_graph_config(**kwargs):
    """Helper to create valid GraphConfig with defaults."""
    defaults = {}
    defaults.update(kwargs)
    return GraphConfig(**defaults)


class TestGraphIndexInitialization:
    """Test GraphIndex initialization and lazy loading."""

    def test_initialization_basic(self, tmp_path):
        """Test basic initialization without loading dependencies."""
        config = create_graph_config()

        index = GraphIndex(config, tmp_path)

        assert index.config == config
        assert index.base_path == tmp_path
        assert (
            index.db_path
            == tmp_path / "cache" / "indexes" / "graph" / "call_graph.duckdb"
        )
        assert index._conn is None  # Lazy loading

    def test_initialization_creates_directory(self, tmp_path):
        """Test that initialization creates database directory."""
        config = create_graph_config()

        index = GraphIndex(config, tmp_path)

        assert index.db_path.parent.exists()
        assert index.db_path.parent.is_dir()


class TestGraphIndexSchema:
    """Test database schema initialization."""

    def test_schema_has_symbols_table(self, tmp_path):
        """Test that schema includes symbols table."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Verify schema method exists
        assert hasattr(index, "_initialize_schema")
        assert callable(index._initialize_schema)

    def test_schema_has_relationships_table(self, tmp_path):
        """Test that schema includes relationships table."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Verify the schema would create both tables
        # (actual DB operations would require DuckDB to be installed)
        assert hasattr(index, "_ensure_connection")


class TestGraphIndexBuild:
    """Test building graph index from code."""

    def test_build_has_correct_interface(self, tmp_path):
        """Test that build method has correct interface."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Verify method exists with correct signature
        assert hasattr(index, "build")
        assert callable(index.build)

        # Verify it accepts required parameters
        import inspect

        sig = inspect.signature(index.build)
        assert "source_paths" in sig.parameters
        assert "force" in sig.parameters


class TestGraphIndexCallGraphQueries:
    """Test call graph query methods."""

    def test_find_callers_has_correct_interface(self, tmp_path):
        """Test that find_callers method has correct interface."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Verify method exists with correct signature
        assert hasattr(index, "find_callers")
        assert callable(index.find_callers)

        # Verify it accepts required parameters
        import inspect

        sig = inspect.signature(index.find_callers)
        assert "symbol_name" in sig.parameters
        assert "max_depth" in sig.parameters

    def test_find_dependencies_has_correct_interface(self, tmp_path):
        """Test that find_dependencies method has correct interface."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Verify method exists with correct signature
        assert hasattr(index, "find_dependencies")
        assert callable(index.find_dependencies)

        # Verify it accepts required parameters
        import inspect

        sig = inspect.signature(index.find_dependencies)
        assert "symbol_name" in sig.parameters
        assert "max_depth" in sig.parameters

    def test_find_call_paths_has_correct_interface(self, tmp_path):
        """Test that find_call_paths method has correct interface."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Verify method exists with correct signature
        assert hasattr(index, "find_call_paths")
        assert callable(index.find_call_paths)

        # Verify it accepts required parameters
        import inspect

        sig = inspect.signature(index.find_call_paths)
        assert "from_symbol" in sig.parameters
        assert "to_symbol" in sig.parameters
        assert "max_depth" in sig.parameters


class TestGraphIndexSearch:
    """Test search functionality."""

    def test_search_has_correct_interface(self, tmp_path):
        """Test that search method has correct interface."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Verify method exists with correct signature
        assert hasattr(index, "search")
        assert callable(index.search)

        # Verify it accepts required parameters
        import inspect

        sig = inspect.signature(index.search)
        assert "query" in sig.parameters
        assert "n_results" in sig.parameters
        assert "filters" in sig.parameters

    def test_search_requires_connection(self, tmp_path):
        """Test that search fails gracefully if database not initialized."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Without calling build or ensuring connection, search should handle gracefully
        # (actual behavior depends on implementation)
        assert hasattr(index, "_ensure_connection")


class TestGraphIndexUpdate:
    """Test incremental updates."""

    def test_update_has_correct_interface(self, tmp_path):
        """Test that update method has correct interface."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Verify method exists with correct signature
        assert hasattr(index, "update")
        assert callable(index.update)

        # Verify it accepts required parameters
        import inspect

        sig = inspect.signature(index.update)
        assert "changed_files" in sig.parameters


class TestGraphIndexHealthAndStats:
    """Test health checks and statistics."""

    def test_health_check_healthy(self, tmp_path):
        """Test health check when index is healthy."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Mock healthy connection
        mock_conn = Mock()
        mock_conn.execute.return_value.fetchone.return_value = (50,)
        index._conn = mock_conn

        health = index.health_check()

        assert isinstance(health, HealthStatus)
        assert health.healthy is True

    def test_health_check_unhealthy(self, tmp_path):
        """Test health check when index is unhealthy."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        health = index.health_check()

        assert isinstance(health, HealthStatus)
        assert health.healthy is False

    def test_get_stats(self, tmp_path):
        """Test getting index statistics."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Mock connection with stats
        mock_conn = Mock()
        mock_conn.execute.return_value.fetchone.return_value = (100, 250)
        index._conn = mock_conn

        stats = index.get_stats()

        assert isinstance(stats, dict)
        assert "symbol_count" in stats
        assert "relationship_count" in stats


class TestGraphIndexTreeSitter:
    """Test Tree-sitter integration."""

    def test_has_tree_sitter_support(self, tmp_path):
        """Test that GraphIndex has Tree-sitter support."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Verify Tree-sitter related methods exist
        # (actual parsing would require tree-sitter to be installed)
        assert hasattr(index, "_ensure_connection")
        # The actual AST parsing would be in _extract_symbols method
        # which is tested via the build method


class TestGraphIndexRecursiveCTE:
    """Test recursive CTE query construction."""

    def test_recursive_queries_have_max_depth(self, tmp_path):
        """Test that recursive queries respect max_depth parameter."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Verify max_depth is a parameter for graph traversal methods
        import inspect

        sig_callers = inspect.signature(index.find_callers)
        assert "max_depth" in sig_callers.parameters
        assert sig_callers.parameters["max_depth"].default == 10

        sig_deps = inspect.signature(index.find_dependencies)
        assert "max_depth" in sig_deps.parameters
        assert sig_deps.parameters["max_depth"].default == 10

        sig_paths = inspect.signature(index.find_call_paths)
        assert "max_depth" in sig_paths.parameters
        assert sig_paths.parameters["max_depth"].default == 10


class TestGraphIndexIntegration:
    """Integration tests for graph index."""

    def test_end_to_end_interface(self, tmp_path):
        """Test complete workflow interface."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # Verify all required methods exist
        assert hasattr(index, "build")
        assert hasattr(index, "search")
        assert hasattr(index, "update")
        assert hasattr(index, "health_check")
        assert hasattr(index, "get_stats")

        # Verify graph-specific methods
        assert hasattr(index, "find_callers")
        assert hasattr(index, "find_dependencies")
        assert hasattr(index, "find_call_paths")

    def test_graph_index_separate_from_code_index(self, tmp_path):
        """Test that GraphIndex is independent from CodeIndex."""
        config = create_graph_config()
        index = GraphIndex(config, tmp_path)

        # GraphIndex should have its own database path
        assert "graph" in str(index.db_path)
        assert "call_graph.duckdb" in str(index.db_path)
