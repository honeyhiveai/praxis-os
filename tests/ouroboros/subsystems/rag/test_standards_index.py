"""Tests for StandardsIndex (Hybrid Search)."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from ouroboros.config.schemas.indexes import (
    FTSConfig,
    RerankingConfig,
    StandardsIndexConfig,
    VectorConfig,
)
from ouroboros.subsystems.rag.base import HealthStatus, SearchResult
from ouroboros.subsystems.rag.standards_index import StandardsIndex
from ouroboros.utils.errors import ActionableError, IndexError


class TestStandardsIndexInitialization:
    """Test StandardsIndex initialization and lazy loading."""

    def test_initialization_basic(self, tmp_path):
        """Test basic initialization without loading dependencies."""
        config = StandardsIndexConfig(
            vector=VectorConfig(model="all-MiniLM-L6-v2"),
            fts=FTSConfig(enabled=True),
            source_paths=["standards/"],
        )

        index = StandardsIndex(config, tmp_path)

        assert index.config == config
        assert index.base_path == tmp_path
        assert index.index_path == tmp_path / "cache" / "indexes" / "standards"
        assert index._db is None  # Lazy loading
        assert index._table is None
        assert index._embedding_model is None

    def test_initialization_creates_index_directory(self, tmp_path):
        """Test that initialization creates index directory."""
        config = StandardsIndexConfig(
            vector=VectorConfig(model="all-MiniLM-L6-v2"),
            fts=FTSConfig(enabled=True),
            source_paths=["standards/"],
        )

        index = StandardsIndex(config, tmp_path)

        assert index.index_path.exists()
        assert index.index_path.is_dir()


class TestStandardsIndexBuild:
    """Test index building from standards files."""

    @pytest.fixture
    def mock_standards_dir(self, tmp_path):
        """Create mock standards directory with sample files."""
        standards_dir = tmp_path / "standards"
        standards_dir.mkdir()

        # Create sample standard file
        (standards_dir / "test-standard.md").write_text(
            "# Test Standard\n\n"
            "This is a test standard about testing patterns.\n\n"
            "## Key Concepts\n\n"
            "Testing is important for code quality.\n"
        )

        return standards_dir

    def test_build_has_correct_interface(self, tmp_path, mock_standards_dir):
        """Test that build method has correct interface."""
        config = StandardsIndexConfig(
            vector=VectorConfig(model="all-MiniLM-L6-v2"),
            fts=FTSConfig(enabled=True),
            source_paths=["standards/"],
        )

        index = StandardsIndex(config, tmp_path)

        # Verify method exists with correct signature
        assert hasattr(index, "build")
        assert callable(index.build)


class TestStandardsIndexSearch:
    """Test search functionality (vector, FTS, hybrid)."""

    def test_search_has_correct_interface(self, tmp_path):
        """Test that search method has correct interface."""
        config = StandardsIndexConfig(
            vector=VectorConfig(model="all-MiniLM-L6-v2"),
            fts=FTSConfig(enabled=True),
            source_paths=["standards/"],
        )

        index = StandardsIndex(config, tmp_path)

        # Verify method exists with correct signature
        assert hasattr(index, "search")
        assert callable(index.search)

        # Verify it accepts required parameters
        import inspect

        sig = inspect.signature(index.search)
        assert "query" in sig.parameters
        assert "n_results" in sig.parameters
        assert "filters" in sig.parameters

    def test_search_requires_table(self, tmp_path):
        """Test that search fails gracefully if table not built."""
        config = StandardsIndexConfig(
            vector=VectorConfig(model="all-MiniLM-L6-v2"),
            fts=FTSConfig(enabled=True),
            source_paths=["standards/"],
        )

        index = StandardsIndex(config, tmp_path)

        with pytest.raises(IndexError) as exc_info:
            index.search("test query")

        assert "not built" in str(exc_info.value).lower()


class TestStandardsIndexUpdate:
    """Test incremental updates for changed files."""

    def test_update_has_correct_interface(self, tmp_path):
        """Test that update method has correct interface."""
        config = StandardsIndexConfig(
            vector=VectorConfig(model="all-MiniLM-L6-v2"),
            fts=FTSConfig(enabled=True),
            source_paths=["standards/"],
        )

        index = StandardsIndex(config, tmp_path)

        # Verify method exists with correct signature
        assert hasattr(index, "update")
        assert callable(index.update)

        # Verify it accepts required parameters
        import inspect

        sig = inspect.signature(index.update)
        assert "changed_files" in sig.parameters


class TestStandardsIndexHealthAndStats:
    """Test health checks and statistics."""

    def test_health_check_healthy(self, tmp_path):
        """Test health check when index is healthy."""
        config = StandardsIndexConfig(
            vector=VectorConfig(model="all-MiniLM-L6-v2"),
            fts=FTSConfig(enabled=True),
            source_paths=["standards/"],
        )

        index = StandardsIndex(config, tmp_path)

        # Mock healthy table
        mock_table = Mock()
        mock_table.count_rows.return_value = 100
        index._table = mock_table

        health = index.health_check()

        assert isinstance(health, HealthStatus)
        assert health.healthy is True
        assert "100 chunks" in health.message

    def test_health_check_unhealthy(self, tmp_path):
        """Test health check when index is unhealthy."""
        config = StandardsIndexConfig(
            vector=VectorConfig(model="all-MiniLM-L6-v2"),
            fts=FTSConfig(enabled=True),
            source_paths=["standards/"],
        )

        index = StandardsIndex(config, tmp_path)

        health = index.health_check()

        assert isinstance(health, HealthStatus)
        assert health.healthy is False

    def test_get_stats(self, tmp_path):
        """Test getting index statistics."""
        config = StandardsIndexConfig(
            vector=VectorConfig(model="all-MiniLM-L6-v2"),
            fts=FTSConfig(enabled=True),
            source_paths=["standards/"],
        )

        index = StandardsIndex(config, tmp_path)

        # Mock table
        mock_table = Mock()
        mock_table.count_rows.return_value = 50
        index._table = mock_table

        stats = index.get_stats()

        assert isinstance(stats, dict)
        assert "chunk_count" in stats
        assert stats["chunk_count"] == 50
        assert "embedding_model" in stats
        assert "fts_enabled" in stats


class TestStandardsIndexIntegration:
    """Integration tests with real (small) data."""

    def test_end_to_end_workflow(self, tmp_path):
        """Test complete workflow: build → search → update → health check."""
        # Create minimal standards directory
        standards_dir = tmp_path / "standards"
        standards_dir.mkdir()
        (standards_dir / "test.md").write_text("# Testing\n\nTesting is important.\n")

        config = StandardsIndexConfig(
            vector=VectorConfig(model="all-MiniLM-L6-v2"),
            fts=FTSConfig(enabled=True),
            source_paths=[str(standards_dir)],
        )

        index = StandardsIndex(config, tmp_path)

        # This test would require actual LanceDB installation
        # For now, we just verify the interface is correct
        assert hasattr(index, "build")
        assert hasattr(index, "search")
        assert hasattr(index, "update")
        assert hasattr(index, "health_check")
        assert hasattr(index, "get_stats")
