"""Unit tests for BaseIndex abstract class and SearchResult dataclass.

Tests cover:
- SearchResult initialization and validation
- SearchResult field constraints (relevance_score, content_type, line_range)
- BaseIndex initialization
- BaseIndex abstract method enforcement
- Error handling for invalid inputs
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock
import importlib.util

# Direct import of base.py to avoid broken server/__init__.py
base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
spec = importlib.util.spec_from_file_location("base", base_path)
base_module = importlib.util.module_from_spec(spec)
sys.modules['base'] = base_module
spec.loader.exec_module(base_module)

BaseIndex = base_module.BaseIndex
SearchResult = base_module.SearchResult


class TestSearchResult:
    """Test SearchResult dataclass initialization and validation."""
    
    def test_search_result_valid_initialization(self):
        """Test SearchResult creation with valid inputs."""
        result = SearchResult(
            content="Sample content",
            file_path="path/to/file.md",
            relevance_score=0.85,
            content_type="standards",
            metadata={"domain": "backend"},
            chunk_id="chunk_123",
            line_range=(10, 20)
        )
        
        assert result.content == "Sample content"
        assert result.file_path == "path/to/file.md"
        assert result.relevance_score == 0.85
        assert result.content_type == "standards"
        assert result.metadata == {"domain": "backend"}
        assert result.chunk_id == "chunk_123"
        assert result.line_range == (10, 20)
    
    def test_search_result_minimal_fields(self):
        """Test SearchResult with only required fields."""
        result = SearchResult(
            content="Minimal content",
            file_path="file.py",
            relevance_score=0.5,
            content_type="code"
        )
        
        assert result.content == "Minimal content"
        assert result.metadata == {}
        assert result.chunk_id is None
        assert result.line_range is None
    
    def test_search_result_invalid_relevance_score_too_low(self):
        """Test SearchResult rejects relevance_score < 0.0."""
        with pytest.raises(ValueError, match="relevance_score must be in"):
            SearchResult(
                content="Test",
                file_path="test.py",
                relevance_score=-0.1,
                content_type="code"
            )
    
    def test_search_result_invalid_relevance_score_too_high(self):
        """Test SearchResult rejects relevance_score > 1.0."""
        with pytest.raises(ValueError, match="relevance_score must be in"):
            SearchResult(
                content="Test",
                file_path="test.py",
                relevance_score=1.5,
                content_type="code"
            )
    
    def test_search_result_boundary_relevance_scores(self):
        """Test SearchResult accepts boundary values 0.0 and 1.0."""
        result_min = SearchResult(
            content="Min",
            file_path="min.py",
            relevance_score=0.0,
            content_type="code"
        )
        assert result_min.relevance_score == 0.0
        
        result_max = SearchResult(
            content="Max",
            file_path="max.py",
            relevance_score=1.0,
            content_type="ast"
        )
        assert result_max.relevance_score == 1.0
    
    def test_search_result_invalid_content_type(self):
        """Test SearchResult rejects invalid content_type."""
        with pytest.raises(ValueError, match="content_type must be one of"):
            SearchResult(
                content="Test",
                file_path="test.py",
                relevance_score=0.5,
                content_type="invalid_type"
            )
    
    def test_search_result_valid_content_types(self):
        """Test SearchResult accepts all valid content types."""
        for content_type in ["standards", "code", "ast"]:
            result = SearchResult(
                content="Test",
                file_path="test.py",
                relevance_score=0.5,
                content_type=content_type
            )
            assert result.content_type == content_type
    
    def test_search_result_invalid_line_range_not_tuple(self):
        """Test SearchResult rejects line_range that's not a tuple."""
        with pytest.raises(ValueError, match="line_range must be"):
            SearchResult(
                content="Test",
                file_path="test.py",
                relevance_score=0.5,
                content_type="code",
                line_range=[10, 20]  # List, not tuple
            )
    
    def test_search_result_invalid_line_range_wrong_length(self):
        """Test SearchResult rejects line_range with wrong number of elements."""
        with pytest.raises(ValueError, match="line_range must be"):
            SearchResult(
                content="Test",
                file_path="test.py",
                relevance_score=0.5,
                content_type="code",
                line_range=(10, 20, 30)  # 3 elements
            )
    
    def test_search_result_invalid_line_range_non_integers(self):
        """Test SearchResult rejects line_range with non-integer values."""
        with pytest.raises(ValueError, match="line_range must be"):
            SearchResult(
                content="Test",
                file_path="test.py",
                relevance_score=0.5,
                content_type="code",
                line_range=(10.5, 20)  # Float
            )
    
    def test_search_result_invalid_line_range_start_greater_than_end(self):
        """Test SearchResult rejects line_range where start > end."""
        with pytest.raises(ValueError, match="line_range must be"):
            SearchResult(
                content="Test",
                file_path="test.py",
                relevance_score=0.5,
                content_type="code",
                line_range=(20, 10)  # Start > end
            )
    
    def test_search_result_valid_line_range_equal_lines(self):
        """Test SearchResult accepts line_range where start == end (single line)."""
        result = SearchResult(
            content="Test",
            file_path="test.py",
            relevance_score=0.5,
            content_type="code",
            line_range=(15, 15)
        )
        assert result.line_range == (15, 15)
    
    def test_search_result_metadata_default_empty_dict(self):
        """Test SearchResult initializes metadata as empty dict by default."""
        result = SearchResult(
            content="Test",
            file_path="test.py",
            relevance_score=0.5,
            content_type="code"
        )
        assert result.metadata == {}
        assert isinstance(result.metadata, dict)
    
    def test_search_result_metadata_mutable_per_instance(self):
        """Test SearchResult metadata is not shared between instances."""
        result1 = SearchResult(
            content="Test1",
            file_path="test1.py",
            relevance_score=0.5,
            content_type="code"
        )
        result2 = SearchResult(
            content="Test2",
            file_path="test2.py",
            relevance_score=0.6,
            content_type="code"
        )
        
        result1.metadata["key"] = "value1"
        result2.metadata["key"] = "value2"
        
        assert result1.metadata["key"] == "value1"
        assert result2.metadata["key"] == "value2"


class TestBaseIndex:
    """Test BaseIndex abstract class behavior."""
    
    def test_base_index_cannot_be_instantiated(self):
        """Test BaseIndex cannot be instantiated directly (abstract class)."""
        cache_path = Path("/tmp/test_cache")
        config = {"test": "config"}
        
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseIndex(cache_path, config)
    
    def test_base_index_requires_all_abstract_methods(self):
        """Test subclass must implement all abstract methods."""
        
        class IncompleteIndex(BaseIndex):
            """Incomplete implementation missing some methods."""
            def build(self, source_paths, force=False):
                pass
            # Missing: search, update, delete
        
        cache_path = Path("/tmp/test_cache")
        cache_path.mkdir(parents=True, exist_ok=True)
        config = {"test": "config"}
        
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteIndex(cache_path, config)
    
    def test_base_index_concrete_subclass_initialization(self, tmp_path):
        """Test concrete subclass can be instantiated when all methods implemented."""
        
        class ConcreteIndex(BaseIndex):
            """Complete implementation of all abstract methods."""
            def build(self, source_paths, force=False):
                pass
            
            def search(self, query, filters=None, n=5):
                return []
            
            def update(self, changed_files):
                pass
            
            def delete(self, file_paths):
                pass
        
        cache_path = tmp_path / "cache"
        config = {"chunking": {"size": 1000}}
        
        index = ConcreteIndex(cache_path, config)
        
        assert index.cache_path == cache_path
        assert index.config == config
    
    def test_base_index_initialization_validates_cache_path_parent(self):
        """Test BaseIndex validates cache_path parent directory exists."""
        
        class ConcreteIndex(BaseIndex):
            def build(self, source_paths, force=False):
                pass
            def search(self, query, filters=None, n=5):
                return []
            def update(self, changed_files):
                pass
            def delete(self, file_paths):
                pass
        
        cache_path = Path("/nonexistent/parent/cache")
        config = {"test": "config"}
        
        with pytest.raises(FileNotFoundError, match="Cache directory parent does not exist"):
            ConcreteIndex(cache_path, config)
    
    def test_base_index_initialization_validates_config_type(self, tmp_path):
        """Test BaseIndex validates config is a dictionary."""
        
        class ConcreteIndex(BaseIndex):
            def build(self, source_paths, force=False):
                pass
            def search(self, query, filters=None, n=5):
                return []
            def update(self, changed_files):
                pass
            def delete(self, file_paths):
                pass
        
        cache_path = tmp_path / "cache"
        
        with pytest.raises(ValueError, match="config must be a dictionary"):
            ConcreteIndex(cache_path, "not_a_dict")
    
    def test_base_index_stores_cache_path_and_config(self, tmp_path):
        """Test BaseIndex stores cache_path and config as instance attributes."""
        
        class ConcreteIndex(BaseIndex):
            def build(self, source_paths, force=False):
                pass
            def search(self, query, filters=None, n=5):
                return []
            def update(self, changed_files):
                pass
            def delete(self, file_paths):
                pass
        
        cache_path = tmp_path / "cache"
        config = {"key1": "value1", "key2": 42}
        
        index = ConcreteIndex(cache_path, config)
        
        assert index.cache_path == cache_path
        assert index.config == config
        assert index.config["key1"] == "value1"
        assert index.config["key2"] == 42
    
    def test_base_index_abstract_methods_have_correct_signatures(self, tmp_path):
        """Test concrete implementation can call abstract methods with correct signatures."""
        
        class ConcreteIndex(BaseIndex):
            def build(self, source_paths, force=False):
                self.build_called = True
                self.build_args = (source_paths, force)
            
            def search(self, query, filters=None, n=5):
                self.search_called = True
                self.search_args = (query, filters, n)
                return [SearchResult(
                    content="Test",
                    file_path="test.py",
                    relevance_score=0.8,
                    content_type="code"
                )]
            
            def update(self, changed_files):
                self.update_called = True
                self.update_args = (changed_files,)
            
            def delete(self, file_paths):
                self.delete_called = True
                self.delete_args = (file_paths,)
        
        cache_path = tmp_path / "cache"
        config = {}
        index = ConcreteIndex(cache_path, config)
        
        # Test build
        index.build(["path1", "path2"], force=True)
        assert index.build_called
        assert index.build_args == (["path1", "path2"], True)
        
        # Test search
        results = index.search("test query", filters={"domain": "backend"}, n=10)
        assert index.search_called
        assert index.search_args == ("test query", {"domain": "backend"}, 10)
        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        
        # Test update
        index.update(["file1.py", "file2.py"])
        assert index.update_called
        assert index.update_args == (["file1.py", "file2.py"],)
        
        # Test delete
        index.delete(["old_file.py"])
        assert index.delete_called
        assert index.delete_args == (["old_file.py"],)

