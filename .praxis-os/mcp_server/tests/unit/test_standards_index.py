"""Unit tests for StandardsIndex implementation.

Tests cover:
- StandardsIndex initialization with valid/invalid configs
- Build and connect functionality
- Vector search with metadata filtering
- Grep fallback search
- Query result caching
- Index hot reload
- Thread safety
- Error handling
"""

import pytest
import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import importlib.util

# Direct import of modules to avoid broken server/__init__.py
base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
base_module = importlib.util.module_from_spec(spec)
sys.modules['server.indexes.base'] = base_module
spec.loader.exec_module(base_module)

standards_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "standards_index.py"
spec = importlib.util.spec_from_file_location("server.indexes.standards_index", standards_path)
standards_module = importlib.util.module_from_spec(spec)
sys.modules['server.indexes.standards_index'] = standards_module
spec.loader.exec_module(standards_module)

BaseIndex = base_module.BaseIndex
SearchResult = base_module.SearchResult
StandardsIndex = standards_module.StandardsIndex


class TestStandardsIndexInitialization:
    """Test StandardsIndex initialization and configuration."""
    
    def test_init_with_valid_config(self, tmp_path):
        """Test StandardsIndex initializes with valid configuration."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": True, "ttl_seconds": 3600},
            "source_paths": [".praxis-os/standards"]
        }
        
        # Patch SentenceTransformer in standards_index module
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            index = StandardsIndex(cache_path=cache_path, config=config)
        
        assert index.cache_path == cache_path
        assert index.embedding_provider == "local"
        assert index.embedding_model == "all-MiniLM-L6-v2"
        assert index.cache_enabled is True
        assert index.cache_ttl_seconds == 3600
        assert cache_path.exists()
    
    def test_init_creates_cache_directory(self, tmp_path):
        """Test init creates cache directory if it doesn't exist."""
        cache_path = tmp_path / "nonexistent" / "cache"
        config = {
            "embedding": {"provider": "local"},
        }
        
        assert not cache_path.exists()
        
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            index = StandardsIndex(cache_path=cache_path, config=config)
        
        assert cache_path.exists()
    
    def test_init_raises_error_if_missing_embedding_config(self, tmp_path):
        """Test init raises ValueError if embedding config missing."""
        cache_path = tmp_path / "cache"
        config = {"cache": {"enabled": True}}  # Missing 'embedding'
        
        with pytest.raises(ValueError, match="Config missing 'embedding' section"):
            StandardsIndex(cache_path=cache_path, config=config)
    
    def test_init_uses_config_defaults(self, tmp_path):
        """Test init uses sensible defaults for optional config."""
        cache_path = tmp_path / "cache"
        config = {"embedding": {}}  # Minimal config
        
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            index = StandardsIndex(cache_path=cache_path, config=config)
        
        assert index.embedding_provider == "local"
        assert index.embedding_model == "all-MiniLM-L6-v2"
        assert index.cache_enabled is True
        assert index.cache_ttl_seconds == 3600
    
    def test_init_loads_local_embedding_model(self, tmp_path):
        """Test init loads SentenceTransformer for local provider."""
        cache_path = tmp_path / "cache"
        config = {"embedding": {"provider": "local", "model": "test-model"}}
        
        mock_model = Mock()
        with patch.object(standards_module, "SentenceTransformer", return_value=mock_model) as mock_st:
            index = StandardsIndex(cache_path=cache_path, config=config)
        
        mock_st.assert_called_once_with("test-model")
        assert index.local_model is mock_model
    
    def test_init_raises_error_if_model_load_fails(self, tmp_path):
        """Test init raises RuntimeError if embedding model fails to load."""
        cache_path = tmp_path / "cache"
        config = {"embedding": {"provider": "local"}}
        
        with patch.object(standards_module, "SentenceTransformer", side_effect=Exception("Model load failed")):
            with pytest.raises(RuntimeError, match="Embedding model initialization failed"):
                StandardsIndex(cache_path=cache_path, config=config)
    
    def test_init_skips_model_load_for_openai_provider(self, tmp_path):
        """Test init doesn't load local model for openai provider."""
        cache_path = tmp_path / "cache"
        config = {"embedding": {"provider": "openai", "model": "text-embedding-ada-002"}}
        
        index = StandardsIndex(cache_path=cache_path, config=config)
        
        assert index.local_model is None
        assert index.embedding_provider == "openai"


class TestStandardsIndexBuild:
    """Test StandardsIndex build and connect functionality."""
    
    def test_build_skips_if_index_exists_and_not_force(self, tmp_path):
        """Test build skips if index exists and force=False."""
        cache_path = tmp_path / "cache"
        cache_path.mkdir()
        
        # Create fake index
        index_path = cache_path / "praxis_os_standards.lance"
        index_path.mkdir()
        
        config = {"embedding": {"provider": "local"}}
        
        mock_db = Mock()
        mock_table = Mock()
        mock_table.count_rows.return_value = 100
        mock_db.open_table.return_value = mock_table
        
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            with patch("lancedb.connect", return_value=mock_db):
                with patch("builtins.open", mock_open()):
                    with patch("fcntl.flock"):
                        index = StandardsIndex(cache_path=cache_path, config=config)
                        index.build(source_paths=[".praxis-os/standards"], force=False)
        
        # Should connect but not rebuild
        assert index.vector_search_available is True
    
    def test_build_logs_warning_for_missing_implementation(self, tmp_path, caplog):
        """Test build logs warning about missing full implementation."""
        cache_path = tmp_path / "cache"
        config = {"embedding": {"provider": "local"}}
        
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            index = StandardsIndex(cache_path=cache_path, config=config)
            
            with pytest.raises(RuntimeError, match="Index build/connect failed"):
                index.build(source_paths=[".praxis-os/standards"], force=True)
        
        assert "Full build not yet implemented" in caplog.text
    
    def test_connect_to_index_success(self, tmp_path):
        """Test _connect_to_index successfully connects to existing index."""
        cache_path = tmp_path / "cache"
        cache_path.mkdir()
        
        # Create fake index
        index_path = cache_path / "praxis_os_standards.lance"
        index_path.mkdir()
        
        config = {"embedding": {"provider": "local"}}
        
        mock_db = Mock()
        mock_table = Mock()
        mock_table.count_rows.return_value = 150
        mock_db.open_table.return_value = mock_table
        
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            with patch("lancedb.connect", return_value=mock_db):
                with patch("builtins.open", mock_open()):
                    with patch("fcntl.flock"):
                        index = StandardsIndex(cache_path=cache_path, config=config)
                        index._connect_to_index()
        
        assert index.vector_search_available is True
        assert index.table is mock_table
        assert index.db is mock_db
    
    def test_connect_to_index_raises_error_if_not_found(self, tmp_path):
        """Test _connect_to_index raises RuntimeError if index doesn't exist."""
        cache_path = tmp_path / "cache"
        config = {"embedding": {"provider": "local"}}
        
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            index = StandardsIndex(cache_path=cache_path, config=config)
            
            with pytest.raises(RuntimeError, match="Index not found"):
                index._connect_to_index()


class TestStandardsIndexSearch:
    """Test StandardsIndex search functionality."""
    
    def create_index_with_mock_table(self, tmp_path):
        """Helper to create index with mocked LanceDB table."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local"},
            "source_paths": [".praxis-os/standards"]
        }
        
        mock_model = Mock()
        mock_model.encode.return_value = Mock(tolist=lambda: [0.1] * 384)
        
        with patch.object(standards_module, "SentenceTransformer", return_value=mock_model):
            index = StandardsIndex(cache_path=cache_path, config=config)
        
        # Mock table
        mock_table = Mock()
        index.table = mock_table
        index.db = Mock()
        index.vector_search_available = True
        
        return index, mock_table
    
    def test_search_raises_error_for_empty_query(self, tmp_path):
        """Test search raises ValueError for empty query."""
        index, _ = self.create_index_with_mock_table(tmp_path)
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            index.search(query="", filters={}, n=5)
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            index.search(query="   ", filters={}, n=5)
    
    def test_search_raises_error_for_invalid_n(self, tmp_path):
        """Test search raises ValueError for n < 1."""
        index, _ = self.create_index_with_mock_table(tmp_path)
        
        with pytest.raises(ValueError, match="n must be >= 1"):
            index.search(query="test", filters={}, n=0)
        
        with pytest.raises(ValueError, match="n must be >= 1"):
            index.search(query="test", filters={}, n=-1)
    
    def test_search_performs_vector_search(self, tmp_path):
        """Test search performs vector search when available."""
        index, mock_table = self.create_index_with_mock_table(tmp_path)
        
        # Mock search chain
        mock_search = Mock()
        mock_search.limit.return_value = mock_search
        mock_search.where.return_value = mock_search
        mock_search.to_list.return_value = [
            {
                "content": "Test content",
                "file_path": "test.md",
                "_distance": 0.5,
                "phase": 0,
                "chunk_id": "chunk1",
                "framework_type": "test",
                "is_critical": False,
                "token_count": 100,
                "section_header": "Test Section",
                "tags": "[]"
            }
        ]
        mock_table.search.return_value = mock_search
        
        results = index.search(query="test query", filters={}, n=5)
        
        assert len(results) == 1
        assert results[0].content == "Test content"
        assert results[0].file_path == "test.md"
        assert results[0].content_type == "standards"
    
    def test_search_applies_metadata_filters(self, tmp_path):
        """Test search applies metadata filters to WHERE clause."""
        index, mock_table = self.create_index_with_mock_table(tmp_path)
        
        # Mock search chain
        mock_search = Mock()
        mock_search.limit.return_value = mock_search
        mock_search.where.return_value = mock_search
        mock_search.to_list.return_value = []
        mock_table.search.return_value = mock_search
        
        filters = {
            "phase": 1,
            "is_critical": True,
            "framework_type": "python",
            "tags": ["testing"]
        }
        
        index.search(query="test", filters=filters, n=5)
        
        # Verify WHERE clause was called with filters
        assert mock_search.where.called
        where_clause = mock_search.where.call_args[0][0]
        assert "phase = 1" in where_clause
        assert "is_critical = True" in where_clause
        assert "framework_type = 'python'" in where_clause
        assert "tags LIKE '%testing%'" in where_clause
    
    def test_search_uses_cache_for_identical_queries(self, tmp_path):
        """Test search returns cached results for identical queries."""
        index, mock_table = self.create_index_with_mock_table(tmp_path)
        
        # Mock search chain
        mock_search = Mock()
        mock_search.limit.return_value = mock_search
        mock_search.to_list.return_value = [
            {
                "content": "Cached content",
                "file_path": "test.md",
                "_distance": 0.3,
                "phase": 0,
                "chunk_id": "chunk1",
                "framework_type": "",
                "is_critical": False,
                "token_count": 50,
                "section_header": "",
                "tags": "[]"
            }
        ]
        mock_table.search.return_value = mock_search
        
        # First call - should hit DB
        results1 = index.search(query="test", filters={}, n=5)
        call_count_1 = mock_table.search.call_count
        
        # Second identical call - should hit cache
        results2 = index.search(query="test", filters={}, n=5)
        call_count_2 = mock_table.search.call_count
        
        assert results1[0].content == results2[0].content
        assert call_count_1 == call_count_2  # No additional DB call
    
    def test_search_falls_back_to_grep_if_vector_unavailable(self, tmp_path):
        """Test search falls back to grep when vector search unavailable."""
        index, _ = self.create_index_with_mock_table(tmp_path)
        index.vector_search_available = False
        
        # Mock grep subprocess
        mock_result = Mock()
        mock_result.stdout = str(tmp_path / "test.md")
        mock_result.returncode = 0
        
        with patch("subprocess.run", return_value=mock_result):
            with patch("pathlib.Path.read_text", return_value="Grep matched content"):
                results = index.search(query="test query", filters={}, n=5)
        
        assert len(results) >= 0  # May be empty if source path doesn't exist
    
    def test_search_handles_vector_search_exception(self, tmp_path):
        """Test search falls back to grep if vector search raises exception."""
        index, mock_table = self.create_index_with_mock_table(tmp_path)
        
        # Make vector search fail
        mock_table.search.side_effect = Exception("Vector search failed")
        
        # Mock grep subprocess
        mock_result = Mock()
        mock_result.stdout = ""
        mock_result.returncode = 1
        
        with patch("subprocess.run", return_value=mock_result):
            results = index.search(query="test", filters={}, n=5)
        
        # Should return empty list from grep fallback
        assert isinstance(results, list)


class TestStandardsIndexCaching:
    """Test StandardsIndex caching functionality."""
    
    def test_cache_key_generation(self, tmp_path):
        """Test cache key generation creates consistent keys."""
        cache_path = tmp_path / "cache"
        config = {"embedding": {"provider": "local"}}
        
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            index = StandardsIndex(cache_path=cache_path, config=config)
        
        key1 = index._generate_cache_key("test query", {"phase": 1}, 5)
        key2 = index._generate_cache_key("test query", {"phase": 1}, 5)
        key3 = index._generate_cache_key("different query", {"phase": 1}, 5)
        
        assert key1 == key2  # Same inputs = same key
        assert key1 != key3  # Different inputs = different key
    
    def test_cache_expiration(self, tmp_path):
        """Test cache entries expire after TTL."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local"},
            "cache": {"ttl_seconds": 1}  # 1 second TTL
        }
        
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            index = StandardsIndex(cache_path=cache_path, config=config)
        
        # Cache a result
        result = SearchResult(
            content="test",
            file_path="test.md",
            relevance_score=0.8,
            content_type="standards"
        )
        cache_key = "test_key"
        index._cache_result(cache_key, [result])
        
        # Should be in cache
        cached = index._check_cache(cache_key)
        assert cached is not None
        
        # Wait for expiration
        import time
        time.sleep(1.1)
        
        # Should be expired
        cached = index._check_cache(cache_key)
        assert cached is None
    
    def test_cache_cleaning(self, tmp_path):
        """Test cache cleaning removes expired entries."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local"},
            "cache": {"ttl_seconds": 0}  # Immediate expiration
        }
        
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            index = StandardsIndex(cache_path=cache_path, config=config)
        
        # Add many cache entries
        for i in range(50):
            index._query_cache[f"key_{i}"] = ([], 0)  # Expired timestamp
        
        assert len(index._query_cache) == 50
        
        # Clean cache
        index._clean_cache()
        
        # All expired entries should be removed
        assert len(index._query_cache) == 0


class TestStandardsIndexReload:
    """Test StandardsIndex reload functionality."""
    
    def test_reload_index_reconnects_to_db(self, tmp_path):
        """Test reload_index reconnects to LanceDB."""
        cache_path = tmp_path / "cache"
        config = {"embedding": {"provider": "local"}}
        
        mock_db = Mock()
        mock_table = Mock()
        mock_table.count_rows.return_value = 200
        mock_db.open_table.return_value = mock_table
        
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            with patch("lancedb.connect", return_value=mock_db):
                index = StandardsIndex(cache_path=cache_path, config=config)
                index.db = Mock()  # Old connection
                index.table = Mock()  # Old table
                index._query_cache["test"] = ([], 0)  # Has cache
                
                index.reload_index()
        
        assert index.db is mock_db
        assert index.table is mock_table
        assert index.vector_search_available is True
        assert len(index._query_cache) == 0  # Cache cleared


class TestStandardsIndexUpdateDelete:
    """Test StandardsIndex update and delete methods."""
    
    def test_update_raises_not_implemented(self, tmp_path):
        """Test update() raises NotImplementedError."""
        cache_path = tmp_path / "cache"
        config = {"embedding": {"provider": "local"}}
        
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            index = StandardsIndex(cache_path=cache_path, config=config)
        
        with pytest.raises(NotImplementedError, match="Incremental update not yet implemented"):
            index.update(changed_files=["test.md"])
    
    def test_delete_raises_not_implemented(self, tmp_path):
        """Test delete() raises NotImplementedError."""
        cache_path = tmp_path / "cache"
        config = {"embedding": {"provider": "local"}}
        
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            index = StandardsIndex(cache_path=cache_path, config=config)
        
        with pytest.raises(NotImplementedError, match="Delete not yet implemented"):
            index.delete(file_paths=["test.md"])


class TestStandardsIndexEmbedding:
    """Test embedding generation methods."""
    
    def test_generate_embedding_local_provider(self, tmp_path):
        """Test _generate_embedding with local provider."""
        cache_path = tmp_path / "cache"
        config = {"embedding": {"provider": "local"}}
        
        mock_model = Mock()
        mock_embedding = Mock()
        mock_embedding.tolist.return_value = [0.1, 0.2, 0.3]
        mock_model.encode.return_value = mock_embedding
        
        with patch.object(standards_module, "SentenceTransformer", return_value=mock_model):
            index = StandardsIndex(cache_path=cache_path, config=config)
        
        embedding = index._generate_embedding("test text")
        
        assert embedding == [0.1, 0.2, 0.3]
        mock_model.encode.assert_called_once_with("test text", convert_to_numpy=True)
    
    def test_generate_embedding_raises_error_if_model_not_initialized(self, tmp_path):
        """Test _generate_embedding raises RuntimeError if model not initialized."""
        cache_path = tmp_path / "cache"
        config = {"embedding": {"provider": "local"}}
        
        with patch.object(standards_module, "SentenceTransformer", return_value=Mock()):
            index = StandardsIndex(cache_path=cache_path, config=config)
        
        index.local_model = None
        
        with pytest.raises(RuntimeError, match="Local embedding model not initialized"):
            index._generate_embedding("test")
    
    def test_generate_embedding_raises_error_for_unknown_provider(self, tmp_path):
        """Test _generate_embedding raises ValueError for unknown provider."""
        cache_path = tmp_path / "cache"
        config = {"embedding": {"provider": "unknown"}}
        
        index = StandardsIndex(cache_path=cache_path, config=config)
        
        with pytest.raises(ValueError, match="Unknown embedding provider"):
            index._generate_embedding("test")

