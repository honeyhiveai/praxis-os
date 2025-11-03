"""Unit tests for hybrid search (vector + FTS) functionality.

Tests Phase 2, Task 2.2: Implement Hybrid Search

Covers:
- Both vector and FTS searches executed in search()
- Metadata filters applied to both search methods
- Results from both methods returned separately (for fusion)
- Graceful degradation if FTS fails
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import importlib.util

# Direct import of modules
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

SearchResult = base_module.SearchResult
StandardsIndex = standards_module.StandardsIndex


class TestHybridSearch:
    """Test hybrid search (vector + FTS) functionality."""
    
    def test_hybrid_search_calls_both_methods(self, tmp_path):
        """Test search() executes both vector and FTS searches."""
        cache_path = tmp_path / "cache"
        cache_path.mkdir()
        
        index_path = cache_path / "praxis_os_standards.lance"
        index_path.mkdir()
        
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},  # Disable cache for testing
            "source_paths": [".praxis-os/standards"]
        }
        
        with patch("lancedb.connect") as mock_connect, \
             patch.object(standards_module, "SentenceTransformer") as mock_model, \
             patch("builtins.open", create=True) as mock_open_file, \
             patch("fcntl.flock"):
            
            # Setup mocks
            mock_table = MagicMock()
            mock_table.count_rows.return_value = 100
            mock_table.create_fts_index = MagicMock()
            
            mock_db = MagicMock()
            mock_db.open_table.return_value = mock_table
            mock_connect.return_value = mock_db
            
            # Initialize index
            index = StandardsIndex(cache_path, config)
            index.build(source_paths=[".praxis-os/standards"], force=False)
            
            # Mock the search methods to track calls
            index._vector_search_raw = MagicMock(return_value=[
                SearchResult(
                    content="test content",
                    file_path="/test/file.md",
                    relevance_score=0.9,
                    content_type="standards",
                    metadata={"search_method": "vector"}
                )
            ])
            
            index._fts_search_raw = MagicMock(return_value=[
                SearchResult(
                    content="test content 2",
                    file_path="/test/file2.md",
                    relevance_score=0.8,
                    content_type="standards",
                    metadata={"search_method": "fts"}
                )
            ])
            
            # Execute search
            results = index.search(query="test query", filters={}, n=5)
            
            # Verify both methods were called
            index._vector_search_raw.assert_called_once_with("test query", {}, limit=20)
            index._fts_search_raw.assert_called_once_with("test query", {}, limit=20)
            
            # Verify results returned
            assert len(results) > 0
    
    def test_hybrid_search_applies_filters_to_both(self, tmp_path):
        """Test filters are passed to both vector and FTS searches."""
        cache_path = tmp_path / "cache"
        cache_path.mkdir()
        
        index_path = cache_path / "praxis_os_standards.lance"
        index_path.mkdir()
        
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": [".praxis-os/standards"]
        }
        
        with patch("lancedb.connect") as mock_connect, \
             patch.object(standards_module, "SentenceTransformer") as mock_model, \
             patch("builtins.open", create=True) as mock_open_file, \
             patch("fcntl.flock"):
            
            mock_table = MagicMock()
            mock_table.count_rows.return_value = 100
            mock_table.create_fts_index = MagicMock()
            
            mock_db = MagicMock()
            mock_db.open_table.return_value = mock_table
            mock_connect.return_value = mock_db
            
            index = StandardsIndex(cache_path, config)
            index.build(source_paths=[".praxis-os/standards"], force=False)
            
            # Mock search methods
            index._vector_search_raw = MagicMock(return_value=[])
            index._fts_search_raw = MagicMock(return_value=[])
            
            # Execute search with filters
            filters = {"phase": 1, "is_critical": True}
            index.search(query="test query", filters=filters, n=5)
            
            # Verify filters passed to both methods
            index._vector_search_raw.assert_called_once_with("test query", filters, limit=20)
            index._fts_search_raw.assert_called_once_with("test query", filters, limit=20)
    
    def test_hybrid_search_limit_20_for_fusion(self, tmp_path):
        """Test both searches request 20 results (for fusion in Task 2.3)."""
        cache_path = tmp_path / "cache"
        cache_path.mkdir()
        
        index_path = cache_path / "praxis_os_standards.lance"
        index_path.mkdir()
        
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": [".praxis-os/standards"]
        }
        
        with patch("lancedb.connect") as mock_connect, \
             patch.object(standards_module, "SentenceTransformer") as mock_model, \
             patch("builtins.open", create=True) as mock_open_file, \
             patch("fcntl.flock"):
            
            mock_table = MagicMock()
            mock_table.count_rows.return_value = 100
            mock_table.create_fts_index = MagicMock()
            
            mock_db = MagicMock()
            mock_db.open_table.return_value = mock_table
            mock_connect.return_value = mock_db
            
            index = StandardsIndex(cache_path, config)
            index.build(source_paths=[".praxis-os/standards"], force=False)
            
            # Mock search methods
            index._vector_search_raw = MagicMock(return_value=[])
            index._fts_search_raw = MagicMock(return_value=[])
            
            # Execute search requesting n=5 results
            index.search(query="test", filters={}, n=5)
            
            # Verify limit=20 passed to both (for fusion)
            _, call_kwargs_vector = index._vector_search_raw.call_args
            _, call_kwargs_fts = index._fts_search_raw.call_args
            
            assert call_kwargs_vector['limit'] == 20
            assert call_kwargs_fts['limit'] == 20
    
    def test_fts_search_graceful_degradation(self, tmp_path):
        """Test hybrid search continues with vector-only if FTS fails."""
        cache_path = tmp_path / "cache"
        cache_path.mkdir()
        
        index_path = cache_path / "praxis_os_standards.lance"
        index_path.mkdir()
        
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": [".praxis-os/standards"]
        }
        
        with patch("lancedb.connect") as mock_connect, \
             patch.object(standards_module, "SentenceTransformer") as mock_model, \
             patch("builtins.open", create=True) as mock_open_file, \
             patch("fcntl.flock"):
            
            mock_table = MagicMock()
            mock_table.count_rows.return_value = 100
            mock_table.create_fts_index = MagicMock()
            
            mock_db = MagicMock()
            mock_db.open_table.return_value = mock_table
            mock_connect.return_value = mock_db
            
            index = StandardsIndex(cache_path, config)
            index.build(source_paths=[".praxis-os/standards"], force=False)
            
            # Mock vector search to succeed
            index._vector_search_raw = MagicMock(return_value=[
                SearchResult(
                    content="vector result",
                    file_path="/test/file.md",
                    relevance_score=0.9,
                    content_type="standards",
                    metadata={}
                )
            ])
            
            # Mock FTS search to fail (returns empty list per _fts_search_raw implementation)
            index._fts_search_raw = MagicMock(return_value=[])
            
            # Should not raise exception
            results = index.search(query="test", filters={}, n=5)
            
            # Should return vector results
            assert len(results) > 0
            assert results[0].content == "vector result"

