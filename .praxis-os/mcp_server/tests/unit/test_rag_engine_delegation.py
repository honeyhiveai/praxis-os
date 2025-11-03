"""Unit tests for RAGEngine delegation to StandardsIndex.

Tests verify backward compatibility after refactoring to delegate search
operations to the new multi-index architecture.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import importlib.util

# Direct import to avoid broken server/__init__.py
rag_path = Path(__file__).parent.parent.parent / "rag_engine.py"
spec = importlib.util.spec_from_file_location("rag_engine", rag_path)
rag_module = importlib.util.module_from_spec(spec)
sys.modules['rag_engine_test'] = rag_module

# Mock dependencies before loading
with patch("rag_engine.StandardsIndex"):
    with patch("rag_engine.IndexManager"):
        spec.loader.exec_module(rag_module)

RAGEngine = rag_module.RAGEngine


class TestRAGEngineDelegation:
    """Test RAGEngine delegates to StandardsIndex while maintaining API."""
    
    def test_init_creates_standards_index(self, tmp_path):
        """Test RAGEngine initializes StandardsIndex on init."""
        index_path = tmp_path / "index"
        standards_path = tmp_path / "standards"
        standards_path.mkdir()
        
        # Mock StandardsIndex to prevent actual initialization
        mock_standards_index = Mock()
        mock_standards_index.build.return_value = None
        
        with patch("rag_engine.StandardsIndex", return_value=mock_standards_index):
            engine = RAGEngine(
                index_path=index_path,
                standards_path=standards_path
            )
        
        assert engine.standards_index is mock_standards_index
        assert engine.vector_search_available is True
        # Verify build was called to connect to existing index
        mock_standards_index.build.assert_called_once()
    
    def test_init_handles_standards_index_failure(self, tmp_path):
        """Test RAGEngine gracefully handles StandardsIndex initialization failure."""
        index_path = tmp_path / "index"
        standards_path = tmp_path / "standards"
        
        # Mock StandardsIndex to raise error
        with patch("rag_engine.StandardsIndex", side_effect=Exception("Init failed")):
            engine = RAGEngine(
                index_path=index_path,
                standards_path=standards_path
            )
        
        assert engine.standards_index is None
        assert engine.vector_search_available is False
    
    def test_search_delegates_to_standards_index(self, tmp_path):
        """Test search() delegates to StandardsIndex.search()."""
        index_path = tmp_path / "index"
        standards_path = tmp_path / "standards"
        standards_path.mkdir()
        
        # Create mock StandardsIndex with search results
        mock_standards_index = Mock()
        mock_result = Mock()
        mock_result.content = "Test content"
        mock_result.file_path = "test.md"
        mock_result.relevance_score = 0.9
        mock_result.metadata = {
            "section_header": "Test",
            "parent_headers": [],
            "token_count": 10,
            "phase": 0,
            "framework_type": "",
            "category": "",
            "is_critical": False,
            "tags": []
        }
        mock_standards_index.search.return_value = [mock_result]
        mock_standards_index.build.return_value = None
        
        with patch("rag_engine.StandardsIndex", return_value=mock_standards_index):
            engine = RAGEngine(
                index_path=index_path,
                standards_path=standards_path
            )
            
            result = engine.search(query="test query", n_results=5)
        
        # Verify delegation
        mock_standards_index.search.assert_called_once_with(
            query="test query",
            filters=None,
            n=5
        )
        
        # Verify legacy format returned
        assert hasattr(result, 'chunks')
        assert hasattr(result, 'total_tokens')
        assert hasattr(result, 'retrieval_method')
        assert len(result.chunks) == 1
        assert result.chunks[0]["content"] == "Test content"
    
    def test_search_with_filters_delegates_correctly(self, tmp_path):
        """Test search() passes filters to StandardsIndex."""
        index_path = tmp_path / "index"
        standards_path = tmp_path / "standards"
        standards_path.mkdir()
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = []
        mock_standards_index.build.return_value = None
        
        with patch("rag_engine.StandardsIndex", return_value=mock_standards_index):
            engine = RAGEngine(
                index_path=index_path,
                standards_path=standards_path
            )
            
            filters = {"phase": 1, "is_critical": True}
            result = engine.search(query="test", n_results=10, filters=filters)
        
        # Verify filters passed through
        mock_standards_index.search.assert_called_once_with(
            query="test",
            filters=filters,
            n=10
        )
    
    def test_convert_to_legacy_format(self, tmp_path):
        """Test _convert_to_legacy_format() correctly transforms results."""
        index_path = tmp_path / "index"
        standards_path = tmp_path / "standards"
        
        # Create engine without StandardsIndex initialization
        with patch("rag_engine.StandardsIndex", side_effect=Exception("Skip")):
            engine = RAGEngine(
                index_path=index_path,
                standards_path=standards_path
            )
        
        # Create mock new-format results
        mock_result1 = Mock()
        mock_result1.content = "Content 1"
        mock_result1.file_path = "file1.md"
        mock_result1.relevance_score = 0.9
        mock_result1.metadata = {
            "section_header": "Section 1",
            "parent_headers": ["Header A"],
            "token_count": 50,
            "phase": 1,
            "framework_type": "test",
            "category": "example",
            "is_critical": True,
            "tags": ["tag1"]
        }
        
        mock_result2 = Mock()
        mock_result2.content = "Content 2"
        mock_result2.file_path = "file2.md"
        mock_result2.relevance_score = 0.7
        mock_result2.metadata = {
            "section_header": "Section 2",
            "parent_headers": [],
            "token_count": 30,
            "phase": 0,
            "framework_type": "",
            "category": "",
            "is_critical": False,
            "tags": []
        }
        
        # Convert
        result = engine._convert_to_legacy_format([mock_result1, mock_result2])
        
        # Verify legacy format
        assert len(result.chunks) == 2
        assert result.chunks[0]["content"] == "Content 1"
        assert result.chunks[0]["token_count"] == 50
        assert result.chunks[1]["content"] == "Content 2"
        assert result.total_tokens == 80
        assert result.relevance_scores == [0.9, 0.7]
        assert result.retrieval_method == "vector"
    
    def test_reload_index_delegates_to_standards_index(self, tmp_path):
        """Test reload_index() delegates to StandardsIndex."""
        index_path = tmp_path / "index"
        standards_path = tmp_path / "standards"
        standards_path.mkdir()
        
        mock_standards_index = Mock()
        mock_standards_index.build.return_value = None
        
        with patch("rag_engine.StandardsIndex", return_value=mock_standards_index):
            engine = RAGEngine(
                index_path=index_path,
                standards_path=standards_path
            )
            
            engine.reload_index()
        
        # Verify delegation
        mock_standards_index.reload_index.assert_called_once()
    
    def test_health_check_uses_standards_index(self, tmp_path):
        """Test health_check() queries StandardsIndex state."""
        index_path = tmp_path / "index"
        standards_path = tmp_path / "standards"
        standards_path.mkdir()
        
        mock_table = Mock()
        mock_table.count_rows.return_value = 150
        
        mock_standards_index = Mock()
        mock_standards_index.table = mock_table
        mock_standards_index.build.return_value = None
        
        with patch("rag_engine.StandardsIndex", return_value=mock_standards_index):
            engine = RAGEngine(
                index_path=index_path,
                standards_path=standards_path
            )
            
            health = engine.health_check()
        
        assert health["status"] == "healthy"
        assert health["chunk_count"] == 150
        assert health["vector_search_available"] is True

