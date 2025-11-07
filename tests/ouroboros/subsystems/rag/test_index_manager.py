"""Tests for IndexManager orchestration."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from ouroboros.config.schemas.indexes import (
    CodeIndexConfig,
    FTSConfig,
    IndexesConfig,
    RerankingConfig,
    StandardsIndexConfig,
    VectorConfig,
)
from ouroboros.subsystems.rag.index_manager import IndexManager
from ouroboros.utils.errors import ActionableError, IndexError


@pytest.fixture
def minimal_indexes_config():
    """Minimal IndexesConfig for testing.

    Uses the same structure as tests/ouroboros/config/test_mcp_schemas.py
    """
    from ouroboros.config.schemas.indexes import (
        ASTIndexConfig,
        CodeIndexConfig,
        FileWatcherConfig,
        GraphConfig,
    )

    return IndexesConfig(
        standards=StandardsIndexConfig(
            source_paths=["standards/"],
            vector=VectorConfig(),  # Use defaults
            fts=FTSConfig(),  # Use defaults (enabled=True)
            reranking=None,
        ),
        code=CodeIndexConfig(
            source_paths=["src/"],
            languages=["python"],
            vector=VectorConfig(),
            fts=FTSConfig(),
            graph=GraphConfig(),
        ),
        ast=ASTIndexConfig(source_paths=["src/"], languages=["python"]),
        file_watcher=FileWatcherConfig(),  # Use defaults
    )


class TestIndexManager:
    """Tests for IndexManager initialization and routing."""

    def test_init_with_standards_index(self, minimal_indexes_config, tmp_path):
        """Test IndexManager initializes with all configured indexes."""
        manager = IndexManager(config=minimal_indexes_config, base_path=tmp_path)

        # All indexes should be initialized (including stubs)
        assert "standards" in manager._indexes
        assert "code" in manager._indexes
        assert "graph" in manager._indexes  # Graph index added for call graph traversal
        assert "ast" in manager._indexes
        assert len(manager._indexes) == 4  # standards, code, graph, ast

    def test_init_logs_warning_when_code_not_implemented(
        self, minimal_indexes_config, tmp_path
    ):
        """Test IndexManager logs warnings for stub indexes."""
        # Code and AST indexes are stubs, so they should log warnings
        manager = IndexManager(config=minimal_indexes_config, base_path=tmp_path)

        # Should have only standards index (code/ast are stubs)
        assert "standards" in manager._indexes
        # Code and AST might be present but will show as not implemented

    def test_get_index_returns_standards(self, minimal_indexes_config, tmp_path):
        """Test getting standards index by name."""
        manager = IndexManager(config=minimal_indexes_config, base_path=tmp_path)

        standards_index = manager.get_index("standards")
        assert standards_index is not None

    def test_get_index_returns_none_for_missing(self, minimal_indexes_config, tmp_path):
        """Test getting non-existent index returns None."""
        manager = IndexManager(config=minimal_indexes_config, base_path=tmp_path)

        missing_index = manager.get_index("nonexistent")
        assert missing_index is None

    def test_route_action_search_standards(self, minimal_indexes_config, tmp_path):
        """Test routing search_standards action."""
        manager = IndexManager(config=minimal_indexes_config, base_path=tmp_path)

        # Mock the standards index search method
        manager._indexes["standards"].search = MagicMock(return_value=[])

        result = manager.route_action(
            action="search_standards", query="test query", n_results=5
        )

        assert result["status"] == "success"
        assert "results" in result
        assert "count" in result

    def test_route_action_invalid_action(self, minimal_indexes_config, tmp_path):
        """Test routing invalid action raises error."""
        manager = IndexManager(config=minimal_indexes_config, base_path=tmp_path)

        with pytest.raises(ActionableError) as exc_info:
            manager.route_action(action="invalid_action")

        assert "Unknown action" in str(exc_info.value)

    def test_route_action_search_code_not_built(self, minimal_indexes_config, tmp_path):
        """Test searching code when index is not built yet."""
        manager = IndexManager(config=minimal_indexes_config, base_path=tmp_path)

        # CodeIndex is now a real implementation, so it should raise IndexError
        # when trying to search an index that hasn't been built yet
        with pytest.raises(IndexError) as exc_info:
            manager.route_action(action="search_code", query="test query")

        assert "search_code" in str(exc_info.value)
        assert (
            "Index not built yet" in str(exc_info.value).lower()
            or "not built" in str(exc_info.value).lower()
        )

    def test_health_check_all_returns_statuses(self, minimal_indexes_config, tmp_path):
        """Test health_check_all returns status for all indexes."""
        manager = IndexManager(config=minimal_indexes_config, base_path=tmp_path)

        statuses = manager.health_check_all()

        assert "standards" in statuses
        assert statuses["standards"].healthy is False  # Index not built yet

    def test_rebuild_index_unknown_index(self, minimal_indexes_config, tmp_path):
        """Test rebuilding unknown index raises error."""
        manager = IndexManager(config=minimal_indexes_config, base_path=tmp_path)

        with pytest.raises(ActionableError) as exc_info:
            manager.rebuild_index("nonexistent")

        assert "Index not found" in str(exc_info.value)

    def test_get_stats_returns_dict(self, minimal_indexes_config, tmp_path):
        """Test get_stats returns stats for all indexes."""
        manager = IndexManager(config=minimal_indexes_config, base_path=tmp_path)

        stats = manager.get_stats()

        assert isinstance(stats, dict)
        assert "standards" in stats

    def test_update_from_watcher_unknown_index(self, minimal_indexes_config, tmp_path):
        """Test updating unknown index logs warning but doesn't crash."""
        manager = IndexManager(config=minimal_indexes_config, base_path=tmp_path)

        # Should not raise, just log warning
        manager.update_from_watcher("nonexistent", [tmp_path / "test.md"])

    def test_update_from_watcher_standards(self, minimal_indexes_config, tmp_path):
        """Test updating standards index from file watcher."""
        manager = IndexManager(config=minimal_indexes_config, base_path=tmp_path)

        # Mock the standards index update method
        manager._indexes["standards"].update = MagicMock()

        changed_files = [tmp_path / "standards" / "test.md"]
        manager.update_from_watcher("standards", changed_files)

        manager._indexes["standards"].update.assert_called_once_with(changed_files)


class TestIndexManagerWithMultipleIndexes:
    """Tests for IndexManager with multiple indexes configured."""

    # Use shared fixture instead of redefining

    def test_health_check_all_multiple_indexes(self, minimal_indexes_config, tmp_path):
        """Test health check with multiple indexes."""
        manager = IndexManager(config=minimal_indexes_config, base_path=tmp_path)

        statuses = manager.health_check_all()

        assert len(statuses) >= 1  # At least standards
        for status in statuses.values():
            assert hasattr(status, "healthy")
            assert hasattr(status, "message")
