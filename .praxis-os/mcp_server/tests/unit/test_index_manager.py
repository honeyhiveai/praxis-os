"""Unit tests for IndexManager orchestration layer.

Tests cover:
- IndexManager initialization with valid/invalid configs
- Configuration loading and validation
- Index initialization (placeholder behavior)
- Query routing to indexes
- Error handling for invalid queries
- Rebuild functionality
- Index access methods
"""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import importlib.util
import yaml

# Direct import of modules to avoid broken server/__init__.py
# Set up proper package structure for relative imports
base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
base_module = importlib.util.module_from_spec(spec)
sys.modules['server.indexes.base'] = base_module
spec.loader.exec_module(base_module)

manager_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "index_manager.py"
spec = importlib.util.spec_from_file_location("server.indexes.index_manager", manager_path)
manager_module = importlib.util.module_from_spec(spec)
sys.modules['server.indexes.index_manager'] = manager_module
spec.loader.exec_module(manager_module)

BaseIndex = base_module.BaseIndex
SearchResult = base_module.SearchResult
IndexManager = manager_module.IndexManager


class TestIndexManagerInitialization:
    """Test IndexManager initialization and configuration loading."""
    
    def test_init_creates_base_path_if_not_exists(self, tmp_path):
        """Test IndexManager creates base_path directory if it doesn't exist."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        # Create minimal valid config
        config = {
            "indexes": {},
            "retrieval": {"rerank": {"enabled": False}}
        }
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        assert not base_path.exists()
        
        manager = IndexManager(base_path=base_path, config_path=config_path)
        
        assert base_path.exists()
        assert base_path.is_dir()
    
    def test_init_uses_default_config_path_if_none(self, tmp_path):
        """Test IndexManager uses default config path if not provided."""
        base_path = tmp_path / "cache"
        default_config_path = tmp_path / "config" / "index_config.yaml"
        default_config_path.parent.mkdir(parents=True)
        
        config = {
            "indexes": {},
            "retrieval": {"rerank": {"enabled": False}}
        }
        with open(default_config_path, 'w') as f:
            yaml.dump(config, f)
        
        manager = IndexManager(base_path=base_path, config_path=None)
        
        assert manager.config == config
    
    def test_init_loads_config_successfully(self, tmp_path):
        """Test IndexManager loads valid config successfully."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        config = {
            "indexes": {
                "standards": {"enabled": True},
                "code": {"enabled": False}
            },
            "retrieval": {
                "rerank": {"enabled": True}
            }
        }
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        manager = IndexManager(base_path=base_path, config_path=config_path)
        
        assert manager.config == config
        assert manager.base_path == base_path
    
    def test_init_raises_error_if_config_not_found(self, tmp_path):
        """Test IndexManager raises FileNotFoundError if config doesn't exist."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "nonexistent.yaml"
        
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            IndexManager(base_path=base_path, config_path=config_path)
    
    def test_init_raises_error_if_config_invalid_yaml(self, tmp_path):
        """Test IndexManager raises ValueError if config has invalid YAML."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        # Write invalid YAML
        with open(config_path, 'w') as f:
            f.write("invalid: yaml: content: [unclosed")
        
        with pytest.raises(ValueError, match="Failed to parse YAML"):
            IndexManager(base_path=base_path, config_path=config_path)
    
    def test_init_raises_error_if_config_not_dict(self, tmp_path):
        """Test IndexManager raises ValueError if config is not a dictionary."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        # Write non-dict YAML (list)
        with open(config_path, 'w') as f:
            yaml.dump(["item1", "item2"], f)
        
        with pytest.raises(ValueError, match="Config must be a dictionary"):
            IndexManager(base_path=base_path, config_path=config_path)
    
    def test_init_raises_error_if_config_missing_required_sections(self, tmp_path):
        """Test IndexManager validates required config sections."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        # Missing 'retrieval' section
        config = {"indexes": {}}
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        with pytest.raises(ValueError, match="Config missing required sections"):
            IndexManager(base_path=base_path, config_path=config_path)
    
    def test_init_initializes_empty_indexes_dict(self, tmp_path):
        """Test IndexManager initializes indexes dict (currently empty placeholder)."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        config = {
            "indexes": {
                "standards": {"enabled": True}
            },
            "retrieval": {"rerank": {"enabled": False}}
        }
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        manager = IndexManager(base_path=base_path, config_path=config_path)
        
        # Note: Currently placeholder, returns empty dict
        assert isinstance(manager.indexes, dict)


class TestIndexManagerSearch:
    """Test IndexManager search routing and query handling."""
    
    def create_manager_with_mock_index(self, tmp_path, content_type="standards"):
        """Helper to create manager with a mock index."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        config = {
            "indexes": {content_type: {"enabled": True}},
            "retrieval": {"rerank": {"enabled": False}}
        }
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        manager = IndexManager(base_path=base_path, config_path=config_path)
        
        # Add mock index
        mock_index = Mock(spec=BaseIndex)
        manager.indexes[content_type] = mock_index
        
        return manager, mock_index
    
    def test_search_raises_error_for_empty_query(self, tmp_path):
        """Test search raises ValueError for empty query."""
        manager, _ = self.create_manager_with_mock_index(tmp_path)
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            manager.search(query="", content_type="standards")
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            manager.search(query="   ", content_type="standards")
    
    def test_search_raises_error_for_invalid_n_results(self, tmp_path):
        """Test search raises ValueError for n_results < 1."""
        manager, _ = self.create_manager_with_mock_index(tmp_path)
        
        with pytest.raises(ValueError, match="n_results must be"):
            manager.search(query="test", content_type="standards", n_results=0)
        
        with pytest.raises(ValueError, match="n_results must be"):
            manager.search(query="test", content_type="standards", n_results=-1)
    
    def test_search_raises_error_for_unknown_content_type(self, tmp_path):
        """Test search raises ValueError for unknown content_type."""
        manager, _ = self.create_manager_with_mock_index(tmp_path)
        
        with pytest.raises(ValueError, match="Unknown content_type"):
            manager.search(query="test", content_type="nonexistent")
    
    def test_search_routes_to_correct_index(self, tmp_path):
        """Test search routes query to the correct index."""
        manager, mock_index = self.create_manager_with_mock_index(tmp_path)
        
        # Configure mock to return results
        mock_results = [
            SearchResult(
                content="Result 1",
                file_path="file1.md",
                relevance_score=0.9,
                content_type="standards"
            )
        ]
        mock_index.search.return_value = mock_results
        
        results = manager.search(
            query="test query",
            content_type="standards",
            filters={"domain": "backend"},
            n_results=5
        )
        
        # Verify index.search was called with correct parameters
        mock_index.search.assert_called_once_with(
            query="test query",
            filters={"domain": "backend"},
            n=10  # 5 * 2 for re-ranking
        )
        
        assert results == mock_results[:5]
    
    def test_search_returns_top_n_results(self, tmp_path):
        """Test search returns exactly n_results (or fewer if not enough matches)."""
        manager, mock_index = self.create_manager_with_mock_index(tmp_path)
        
        # Create 20 mock results
        mock_results = [
            SearchResult(
                content=f"Result {i}",
                file_path=f"file{i}.md",
                relevance_score=1.0 - (i * 0.01),
                content_type="standards"
            )
            for i in range(20)
        ]
        mock_index.search.return_value = mock_results
        
        results = manager.search(query="test", content_type="standards", n_results=5)
        
        assert len(results) == 5
        assert results == mock_results[:5]
    
    def test_search_with_reranking_disabled(self, tmp_path):
        """Test search without re-ranking when disabled in config."""
        manager, mock_index = self.create_manager_with_mock_index(tmp_path)
        
        mock_results = [
            SearchResult(
                content="Test",
                file_path="test.md",
                relevance_score=0.8,
                content_type="standards"
            )
        ]
        mock_index.search.return_value = mock_results
        
        # Config has rerank.enabled = False
        results = manager.search(query="test", content_type="standards")
        
        # Should return results without re-ranking
        assert results == mock_results[:5]
    
    def test_search_handles_no_results(self, tmp_path):
        """Test search handles empty result set gracefully."""
        manager, mock_index = self.create_manager_with_mock_index(tmp_path)
        
        mock_index.search.return_value = []
        
        results = manager.search(query="test", content_type="standards", n_results=5)
        
        assert results == []
    
    def test_search_propagates_index_exceptions(self, tmp_path):
        """Test search raises RuntimeError if underlying index search fails."""
        manager, mock_index = self.create_manager_with_mock_index(tmp_path)
        
        mock_index.search.side_effect = Exception("Index search failed")
        
        with pytest.raises(RuntimeError, match="Search operation failed"):
            manager.search(query="test", content_type="standards")


class TestIndexManagerRebuild:
    """Test IndexManager rebuild functionality."""
    
    def test_rebuild_all_calls_build_on_all_indexes(self, tmp_path):
        """Test rebuild_all triggers build on all enabled indexes."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        config = {
            "indexes": {
                "standards": {
                    "enabled": True,
                    "source_paths": [".praxis-os/standards"]
                },
                "code": {
                    "enabled": True,
                    "source_paths": ["src/"]
                }
            },
            "retrieval": {"rerank": {"enabled": False}}
        }
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        manager = IndexManager(base_path=base_path, config_path=config_path)
        
        # Add mock indexes
        mock_standards = Mock(spec=BaseIndex)
        mock_code = Mock(spec=BaseIndex)
        manager.indexes["standards"] = mock_standards
        manager.indexes["code"] = mock_code
        
        manager.rebuild_all(force=True)
        
        # Verify both indexes were rebuilt
        mock_standards.build.assert_called_once_with(
            source_paths=[".praxis-os/standards"],
            force=True
        )
        mock_code.build.assert_called_once_with(
            source_paths=["src/"],
            force=True
        )
    
    def test_rebuild_all_skips_indexes_without_source_paths(self, tmp_path):
        """Test rebuild_all skips indexes that have no source_paths configured."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        config = {
            "indexes": {
                "standards": {
                    "enabled": True
                    # Missing source_paths
                }
            },
            "retrieval": {"rerank": {"enabled": False}}
        }
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        manager = IndexManager(base_path=base_path, config_path=config_path)
        mock_index = Mock(spec=BaseIndex)
        manager.indexes["standards"] = mock_index
        
        # Should not raise error, just skip
        manager.rebuild_all(force=False)
        
        # Verify build was NOT called
        mock_index.build.assert_not_called()
    
    def test_rebuild_all_raises_error_if_index_build_fails(self, tmp_path):
        """Test rebuild_all raises RuntimeError if any index build fails."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        config = {
            "indexes": {
                "standards": {
                    "enabled": True,
                    "source_paths": [".praxis-os/standards"]
                }
            },
            "retrieval": {"rerank": {"enabled": False}}
        }
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        manager = IndexManager(base_path=base_path, config_path=config_path)
        mock_index = Mock(spec=BaseIndex)
        mock_index.build.side_effect = Exception("Build failed")
        manager.indexes["standards"] = mock_index
        
        with pytest.raises(RuntimeError, match="Index rebuild failed"):
            manager.rebuild_all(force=True)


class TestIndexManagerAccessMethods:
    """Test IndexManager index access and listing methods."""
    
    def test_get_index_returns_correct_index(self, tmp_path):
        """Test get_index returns the requested index instance."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        config = {
            "indexes": {},
            "retrieval": {"rerank": {"enabled": False}}
        }
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        manager = IndexManager(base_path=base_path, config_path=config_path)
        mock_index = Mock(spec=BaseIndex)
        manager.indexes["standards"] = mock_index
        
        result = manager.get_index("standards")
        
        assert result is mock_index
    
    def test_get_index_returns_none_for_unknown_type(self, tmp_path):
        """Test get_index returns None for unknown content_type."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        config = {
            "indexes": {},
            "retrieval": {"rerank": {"enabled": False}}
        }
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        manager = IndexManager(base_path=base_path, config_path=config_path)
        
        result = manager.get_index("nonexistent")
        
        assert result is None
    
    def test_list_indexes_returns_all_content_types(self, tmp_path):
        """Test list_indexes returns list of all enabled index types."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        config = {
            "indexes": {},
            "retrieval": {"rerank": {"enabled": False}}
        }
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        manager = IndexManager(base_path=base_path, config_path=config_path)
        manager.indexes["standards"] = Mock(spec=BaseIndex)
        manager.indexes["code"] = Mock(spec=BaseIndex)
        manager.indexes["ast"] = Mock(spec=BaseIndex)
        
        result = manager.list_indexes()
        
        assert set(result) == {"standards", "code", "ast"}
    
    def test_list_indexes_returns_empty_list_if_no_indexes(self, tmp_path):
        """Test list_indexes returns empty list when no indexes initialized."""
        base_path = tmp_path / "cache"
        config_path = tmp_path / "index_config.yaml"
        
        config = {
            "indexes": {},
            "retrieval": {"rerank": {"enabled": False}}
        }
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        manager = IndexManager(base_path=base_path, config_path=config_path)
        
        result = manager.list_indexes()
        
        assert result == []

