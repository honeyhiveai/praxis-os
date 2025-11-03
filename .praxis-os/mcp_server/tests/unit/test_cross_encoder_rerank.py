"""Unit tests for Cross-Encoder Re-Ranking.

Tests Phase 2, Task 2.4: Add Cross-Encoder Re-Ranking

Covers:
- Optional re-ranking (config-driven)
- Re-ranking top N results only (not all)
- Cross-encoder score updates
- Graceful degradation if model unavailable
- Metadata preservation
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import importlib.util
import numpy as np

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


class TestCrossEncoderReranking:
    """Test cross-encoder re-ranking for accuracy boost."""
    
    def test_reranking_disabled_by_default(self, tmp_path):
        """Test re-ranking is disabled when not in config."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            assert not index._is_reranking_enabled()
    
    def test_reranking_enabled_when_in_config(self, tmp_path):
        """Test re-ranking is enabled when configured."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": [],
            "retrieval": {
                "rerank": {
                    "enabled": True,
                    "model": "cross-encoder/ms-marco-MiniLM-L-6-v2"
                }
            }
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            assert index._is_reranking_enabled()
    
    def test_rerank_only_top_n_results(self, tmp_path):
        """Test re-ranking only processes top N results, not all."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            # Create 15 results
            results = [
                SearchResult(
                    content=f"chunk {i}",
                    file_path=f"/test/file{i}.md",
                    relevance_score=1.0 - (i * 0.05),  # Descending scores
                    content_type="standards",
                    metadata={},
                    chunk_id=f"chunk{i}"
                )
                for i in range(15)
            ]
            
            # Mock CrossEncoder to return reversed scores (worst becomes best)
            mock_cross_encoder = MagicMock()
            # Return scores that reverse the order of top 10
            mock_scores = np.array([10 - i for i in range(10)])  # [10, 9, 8, ..., 1]
            mock_cross_encoder.predict.return_value = mock_scores
            
            with patch('sentence_transformers.CrossEncoder', return_value=mock_cross_encoder):
                reranked = index._rerank("test query", results, top_n=10)
                
                # Verify CrossEncoder.predict was called with exactly 10 pairs
                assert mock_cross_encoder.predict.call_count == 1
                pairs = mock_cross_encoder.predict.call_args[0][0]
                assert len(pairs) == 10
                
                # Verify results beyond top 10 are unchanged
                assert len(reranked) == 15
                assert reranked[10:] == results[10:]
    
    def test_rerank_updates_relevance_scores(self, tmp_path):
        """Test re-ranking updates relevance scores with cross-encoder scores."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            results = [
                SearchResult(
                    content="chunk 1",
                    file_path="/test/file1.md",
                    relevance_score=0.5,
                    content_type="standards",
                    metadata={},
                    chunk_id="chunk1"
                ),
                SearchResult(
                    content="chunk 2",
                    file_path="/test/file2.md",
                    relevance_score=0.4,
                    content_type="standards",
                    metadata={},
                    chunk_id="chunk2"
                )
            ]
            
            # Mock CrossEncoder to return specific scores
            mock_cross_encoder = MagicMock()
            mock_cross_encoder.predict.return_value = np.array([0.9, 0.8])
            
            with patch('sentence_transformers.CrossEncoder', return_value=mock_cross_encoder):
                reranked = index._rerank("test query", results, top_n=10)
                
                # Check relevance scores updated to cross-encoder scores
                assert abs(reranked[0].relevance_score - 0.9) < 0.001
                assert abs(reranked[1].relevance_score - 0.8) < 0.001
    
    def test_rerank_preserves_original_metadata(self, tmp_path):
        """Test re-ranking preserves original metadata and adds rerank metadata."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            # Need at least 2 results to trigger re-ranking (single result returns early)
            results = [
                SearchResult(
                    content="chunk 1",
                    file_path="/test/file1.md",
                    relevance_score=0.5,
                    content_type="standards",
                    metadata={"phase": 1, "is_critical": True},
                    chunk_id="chunk1"
                ),
                SearchResult(
                    content="chunk 2",
                    file_path="/test/file2.md",
                    relevance_score=0.4,
                    content_type="standards",
                    metadata={"phase": 2, "is_critical": False},
                    chunk_id="chunk2"
                )
            ]
            
            mock_cross_encoder = MagicMock()
            mock_cross_encoder.predict.return_value = np.array([0.9, 0.8])
            
            with patch('sentence_transformers.CrossEncoder', return_value=mock_cross_encoder):
                reranked = index._rerank("test query", results, top_n=10)
                
                # Check original metadata preserved
                assert reranked[0].metadata["phase"] == 1
                assert reranked[0].metadata["is_critical"] is True
                
                # Check rerank metadata added
                assert reranked[0].metadata["rerank_method"] == "cross_encoder"
                assert "pre_rerank_score" in reranked[0].metadata
                assert abs(reranked[0].metadata["pre_rerank_score"] - 0.5) < 0.001
    
    def test_rerank_graceful_degradation_import_error(self, tmp_path):
        """Test re-ranking gracefully degrades if CrossEncoder unavailable."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            result = SearchResult(
                content="chunk 1",
                file_path="/test/file1.md",
                relevance_score=0.5,
                content_type="standards",
                metadata={},
                chunk_id="chunk1"
            )
            
            # Mock ImportError for CrossEncoder
            with patch('sentence_transformers.CrossEncoder', side_effect=ImportError("No module")):
                reranked = index._rerank("test query", [result], top_n=10)
                
                # Should return original results unchanged
                assert len(reranked) == 1
                assert reranked[0] == result
    
    def test_rerank_handles_runtime_error(self, tmp_path):
        """Test re-ranking handles runtime errors during re-ranking."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            result = SearchResult(
                content="chunk 1",
                file_path="/test/file1.md",
                relevance_score=0.5,
                content_type="standards",
                metadata={},
                chunk_id="chunk1"
            )
            
            # Mock CrossEncoder to raise runtime error
            mock_cross_encoder = MagicMock()
            mock_cross_encoder.predict.side_effect = RuntimeError("Model failed")
            
            with patch('sentence_transformers.CrossEncoder', return_value=mock_cross_encoder):
                reranked = index._rerank("test query", [result], top_n=10)
                
                # Should return original results unchanged
                assert len(reranked) == 1
                assert reranked[0] == result
    
    def test_rerank_skips_single_result(self, tmp_path):
        """Test re-ranking is skipped for single result (nothing to re-order)."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            result = SearchResult(
                content="chunk 1",
                file_path="/test/file1.md",
                relevance_score=0.5,
                content_type="standards",
                metadata={},
                chunk_id="chunk1"
            )
            
            # Should skip re-ranking without calling CrossEncoder
            with patch('sentence_transformers.CrossEncoder') as mock_ce:
                reranked = index._rerank("test query", [result], top_n=10)
                
                # CrossEncoder should not be instantiated
                assert not mock_ce.called
                assert reranked == [result]
    
    def test_rerank_reorders_by_cross_encoder_score(self, tmp_path):
        """Test re-ranking reorders results by cross-encoder scores."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            # Create 3 results in order: chunk0, chunk1, chunk2
            results = [
                SearchResult(
                    content=f"chunk {i}",
                    file_path=f"/test/file{i}.md",
                    relevance_score=1.0 - (i * 0.1),
                    content_type="standards",
                    metadata={},
                    chunk_id=f"chunk{i}"
                )
                for i in range(3)
            ]
            
            # Mock CrossEncoder to reverse the order
            # chunk2 gets highest score, chunk0 gets lowest
            mock_cross_encoder = MagicMock()
            mock_cross_encoder.predict.return_value = np.array([0.3, 0.6, 0.9])
            
            with patch('sentence_transformers.CrossEncoder', return_value=mock_cross_encoder):
                reranked = index._rerank("test query", results, top_n=10)
                
                # Verify order is reversed: chunk2, chunk1, chunk0
                assert reranked[0].chunk_id == "chunk2"
                assert reranked[1].chunk_id == "chunk1"
                assert reranked[2].chunk_id == "chunk0"

