"""Unit tests for FTS (Full-Text Search) index functionality.

Tests Phase 2, Task 2.1: Enable LanceDB FTS Index

Covers:
- FTS index creation on existing table
- Idempotent index creation (doesn't fail if already exists)
- Error handling for FTS creation failures
- Graceful degradation (vector-only if FTS fails)
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

StandardsIndex = standards_module.StandardsIndex


class TestFTSIndexCreation:
    """Test FTS index creation and management."""
    
    def test_fts_index_created_on_connect(self, tmp_path):
        """Test FTS index is created when connecting to existing vector index."""
        cache_path = tmp_path / "cache"
        cache_path.mkdir()
        
        # Create mock index directory
        index_path = cache_path / "praxis_os_standards.lance"
        index_path.mkdir()
        
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": True},
            "source_paths": [".praxis-os/standards"]
        }
        
        # Mock LanceDB and SentenceTransformer
        with patch("lancedb.connect") as mock_connect, \
             patch.object(standards_module, "SentenceTransformer") as mock_model, \
             patch("builtins.open", create=True) as mock_open_file, \
             patch("fcntl.flock"):
            
            # Setup mocks
            mock_table = MagicMock()
            mock_table.count_rows.return_value = 100
            mock_table.create_fts_index = MagicMock()  # No error = success
            
            mock_db = MagicMock()
            mock_db.open_table.return_value = mock_table
            mock_connect.return_value = mock_db
            
            # Initialize and connect
            index = StandardsIndex(cache_path, config)
            index.build(source_paths=[".praxis-os/standards"], force=False)
            
            # Verify FTS index creation was attempted
            mock_table.create_fts_index.assert_called_once_with("content", use_tantivy=False)
    
    def test_fts_index_idempotent(self, tmp_path):
        """Test FTS index creation is idempotent (doesn't fail if exists)."""
        cache_path = tmp_path / "cache"
        cache_path.mkdir()
        
        index_path = cache_path / "praxis_os_standards.lance"
        index_path.mkdir()
        
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": True},
            "source_paths": [".praxis-os/standards"]
        }
        
        with patch("lancedb.connect") as mock_connect, \
             patch.object(standards_module, "SentenceTransformer") as mock_model, \
             patch("builtins.open", create=True) as mock_open_file, \
             patch("fcntl.flock"):
            
            # Setup mocks - FTS index already exists
            mock_table = MagicMock()
            mock_table.count_rows.return_value = 100
            mock_table.create_fts_index.side_effect = Exception("FTS index already exists")
            
            mock_db = MagicMock()
            mock_db.open_table.return_value = mock_table
            mock_connect.return_value = mock_db
            
            # Should not raise exception
            index = StandardsIndex(cache_path, config)
            index.build(source_paths=[".praxis-os/standards"], force=False)
            
            # Connection should succeed despite "already exists" error
            assert index.vector_search_available is True
            assert index.table is not None
    
    def test_fts_index_graceful_degradation(self, tmp_path):
        """Test system continues with vector-only if FTS creation fails."""
        cache_path = tmp_path / "cache"
        cache_path.mkdir()
        
        index_path = cache_path / "praxis_os_standards.lance"
        index_path.mkdir()
        
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": True},
            "source_paths": [".praxis-os/standards"]
        }
        
        with patch("lancedb.connect") as mock_connect, \
             patch.object(standards_module, "SentenceTransformer") as mock_model, \
             patch("builtins.open", create=True) as mock_open_file, \
             patch("fcntl.flock"):
            
            # Setup mocks - FTS creation fails with unexpected error
            mock_table = MagicMock()
            mock_table.count_rows.return_value = 100
            mock_table.create_fts_index.side_effect = Exception("Unexpected FTS error")
            
            mock_db = MagicMock()
            mock_db.open_table.return_value = mock_table
            mock_connect.return_value = mock_db
            
            # Should not raise exception (graceful degradation)
            index = StandardsIndex(cache_path, config)
            index.build(source_paths=[".praxis-os/standards"], force=False)
            
            # Connection should succeed, vector search available
            assert index.vector_search_available is True
            assert index.table is not None
    
    def test_fts_index_method_exists(self, tmp_path):
        """Test _ensure_fts_index method exists and is callable."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": True},
            "source_paths": [".praxis-os/standards"]
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            # Verify method exists
            assert hasattr(index, '_ensure_fts_index')
            assert callable(index._ensure_fts_index)

