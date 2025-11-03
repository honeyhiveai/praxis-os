"""Unit tests for Reciprocal Rank Fusion (RRF) algorithm.

Tests Phase 2, Task 2.3: Implement Reciprocal Rank Fusion

Covers:
- RRF formula: score = sum(1 / (k + rank_i))
- Items in both lists get higher scores (additive)
- Results sorted by RRF score descending
- Handling overlapping items (same chunk_id in both lists)
- Edge cases (empty lists, single list)
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


class TestReciprocalRankFusion:
    """Test RRF algorithm for merging vector and FTS results."""
    
    def test_rrf_items_in_both_lists_rank_highest(self, tmp_path):
        """Test items appearing in both lists get highest RRF scores."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            # Create test results
            chunk1 = SearchResult(
                content="chunk 1",
                file_path="/test/file1.md",
                relevance_score=0.9,
                content_type="standards",
                metadata={},
                chunk_id="chunk1"
            )
            
            chunk2 = SearchResult(
                content="chunk 2",
                file_path="/test/file2.md",
                relevance_score=0.8,
                content_type="standards",
                metadata={},
                chunk_id="chunk2"
            )
            
            chunk3 = SearchResult(
                content="chunk 3",
                file_path="/test/file3.md",
                relevance_score=0.7,
                content_type="standards",
                metadata={},
                chunk_id="chunk3"
            )
            
            # List 1: [chunk1, chunk2]
            # List 2: [chunk2, chunk3]
            # chunk2 appears in both → should rank highest
            list1 = [chunk1, chunk2]
            list2 = [chunk2, chunk3]
            
            fused = index._reciprocal_rank_fusion(list1, list2, k=60)
            
            # chunk2 should be first (appears in both lists)
            assert len(fused) == 3
            assert fused[0].chunk_id == "chunk2"
    
    def test_rrf_formula_calculation(self, tmp_path):
        """Test RRF score calculation using formula: 1/(k + rank)."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            chunk1 = SearchResult(
                content="chunk 1",
                file_path="/test/file1.md",
                relevance_score=1.0,
                content_type="standards",
                metadata={},
                chunk_id="chunk1"
            )
            
            # chunk1 at rank 1 in list1: score = 1/(60+1) = 0.0164
            # chunk1 at rank 1 in list2: score = 1/(60+1) = 0.0164
            # Total RRF score = 0.0164 + 0.0164 = 0.0328
            list1 = [chunk1]
            list2 = [chunk1]
            
            fused = index._reciprocal_rank_fusion(list1, list2, k=60)
            
            expected_score = (1.0 / 61) + (1.0 / 61)  # 2 * (1/61)
            assert len(fused) == 1
            assert abs(fused[0].relevance_score - expected_score) < 0.0001
    
    def test_rrf_results_sorted_descending(self, tmp_path):
        """Test results are sorted by RRF score in descending order."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            chunks = [
                SearchResult(
                    content=f"chunk {i}",
                    file_path=f"/test/file{i}.md",
                    relevance_score=1.0,
                    content_type="standards",
                    metadata={},
                    chunk_id=f"chunk{i}"
                )
                for i in range(5)
            ]
            
            # Create lists with different rankings
            list1 = chunks[:3]  # chunk0, chunk1, chunk2
            list2 = chunks[2:]  # chunk2, chunk3, chunk4
            
            fused = index._reciprocal_rank_fusion(list1, list2, k=60)
            
            # Verify descending order
            scores = [r.relevance_score for r in fused]
            assert scores == sorted(scores, reverse=True)
    
    def test_rrf_handles_empty_lists(self, tmp_path):
        """Test RRF gracefully handles empty lists."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            chunk1 = SearchResult(
                content="chunk 1",
                file_path="/test/file1.md",
                relevance_score=0.9,
                content_type="standards",
                metadata={},
                chunk_id="chunk1"
            )
            
            # Empty list1
            fused = index._reciprocal_rank_fusion([], [chunk1], k=60)
            assert len(fused) == 1
            
            # Empty list2
            fused = index._reciprocal_rank_fusion([chunk1], [], k=60)
            assert len(fused) == 1
            
            # Both empty
            fused = index._reciprocal_rank_fusion([], [], k=60)
            assert len(fused) == 0
    
    def test_rrf_preserves_metadata(self, tmp_path):
        """Test RRF preserves original metadata and adds fusion metadata."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            chunk1 = SearchResult(
                content="chunk 1",
                file_path="/test/file1.md",
                relevance_score=0.9,
                content_type="standards",
                metadata={"phase": 1, "is_critical": True},
                chunk_id="chunk1"
            )
            
            fused = index._reciprocal_rank_fusion([chunk1], [chunk1], k=60)
            
            # Check original metadata preserved
            assert fused[0].metadata["phase"] == 1
            assert fused[0].metadata["is_critical"] is True
            
            # Check fusion metadata added
            assert fused[0].metadata["fusion_method"] == "reciprocal_rank_fusion"
            assert "original_score" in fused[0].metadata
    
    def test_rrf_k_parameter_effect(self, tmp_path):
        """Test k parameter affects RRF scores (higher k = more uniform)."""
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "cache": {"enabled": False},
            "source_paths": []
        }
        
        with patch.object(standards_module, "SentenceTransformer"):
            index = StandardsIndex(cache_path, config)
            
            chunk1 = SearchResult(
                content="chunk 1",
                file_path="/test/file1.md",
                relevance_score=1.0,
                content_type="standards",
                metadata={},
                chunk_id="chunk1"
            )
            
            # Low k gives more weight to rank
            fused_k10 = index._reciprocal_rank_fusion([chunk1], [], k=10)
            
            # High k gives less weight to rank
            fused_k100 = index._reciprocal_rank_fusion([chunk1], [], k=100)
            
            # Score with k=10: 1/11 = 0.0909
            # Score with k=100: 1/101 = 0.0099
            # k=10 should give higher score
            assert fused_k10[0].relevance_score > fused_k100[0].relevance_score

