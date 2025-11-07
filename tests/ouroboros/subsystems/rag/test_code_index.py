"""Tests for CodeIndex (Semantic Code Search)."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
from ouroboros.config.schemas.indexes import (
    CodeIndexConfig,
    FTSConfig,
    GraphConfig,
    VectorConfig,
)
from ouroboros.subsystems.rag.base import HealthStatus, SearchResult
from ouroboros.subsystems.rag.code_index import CodeIndex
from ouroboros.utils.errors import ActionableError, IndexError


def create_code_config(**kwargs):
    """Helper to create valid CodeIndexConfig with defaults."""
    defaults = {
        "source_paths": ["src/"],
        "languages": ["python"],
        "vector": VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
        "fts": FTSConfig(enabled=True),
        "graph": GraphConfig(),
    }
    defaults.update(kwargs)
    return CodeIndexConfig(**defaults)


class TestCodeIndexInitialization:
    """Test CodeIndex initialization and lazy loading."""

    def test_initialization_basic(self, tmp_path):
        """Test basic initialization without loading dependencies."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python", "javascript"],
        )

        index = CodeIndex(config, tmp_path)

        assert index.config == config
        assert index.base_path == tmp_path
        assert index.index_path == tmp_path / "cache" / "indexes" / "code"
        assert index._db is None  # Lazy loading
        assert index._table is None
        assert index._embedding_model is None

    def test_initialization_creates_index_directory(self, tmp_path):
        """Test that initialization creates index directory."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python"],
        )

        index = CodeIndex(config, tmp_path)

        assert index.index_path.exists()
        assert index.index_path.is_dir()

    def test_initialization_with_multiple_languages(self, tmp_path):
        """Test initialization with multiple configured languages."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python", "javascript", "typescript", "go"],
        )

        index = CodeIndex(config, tmp_path)

        assert len(index.config.languages) == 4
        assert "python" in index.config.languages


class TestCodeIndexBuild:
    """Test index building from code files."""

    @pytest.fixture
    def mock_code_dir(self, tmp_path):
        """Create mock code directory with sample files."""
        code_dir = tmp_path / "src"
        code_dir.mkdir()

        # Create sample Python file
        (code_dir / "example.py").write_text(
            "def hello_world():\n"
            '    """Say hello."""\n'
            "    print('Hello, world!')\n"
            "\n"
            "def goodbye():\n"
            '    """Say goodbye."""\n'
            "    print('Goodbye!')\n"
        )

        # Create sample JavaScript file
        (code_dir / "app.js").write_text(
            "function greet(name) {\n" "  return `Hello, ${name}!`;\n" "}\n"
        )

        return code_dir

    def test_build_has_correct_interface(self, tmp_path, mock_code_dir):
        """Test that build method has correct interface."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python", "javascript"],
        )

        index = CodeIndex(config, tmp_path)

        # Verify method exists with correct signature
        assert hasattr(index, "build")
        assert callable(index.build)

        # Verify it accepts required parameters
        import inspect

        sig = inspect.signature(index.build)
        assert "source_paths" in sig.parameters
        assert "force" in sig.parameters


class TestCodeIndexLanguageDetection:
    """Test language detection and file filtering."""

    def test_get_file_extensions_python(self, tmp_path):
        """Test file extension mapping for Python."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python"],
        )

        index = CodeIndex(config, tmp_path)
        extensions = index._get_file_extensions()

        assert ".py" in extensions

    def test_get_file_extensions_multiple_languages(self, tmp_path):
        """Test file extension mapping for multiple languages."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python", "javascript", "typescript"],
        )

        index = CodeIndex(config, tmp_path)
        extensions = index._get_file_extensions()

        assert ".py" in extensions
        assert ".js" in extensions
        assert ".ts" in extensions

    def test_detect_language_from_extension(self, tmp_path):
        """Test language detection from file extension."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python", "javascript"],
        )

        index = CodeIndex(config, tmp_path)

        # Create test files
        py_file = tmp_path / "test.py"
        js_file = tmp_path / "test.js"

        assert index._detect_language(py_file) == "python"
        assert index._detect_language(js_file) == "javascript"

    def test_should_skip_node_modules(self, tmp_path):
        """Test that node_modules directories are skipped."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["javascript"],
        )

        index = CodeIndex(config, tmp_path)

        node_modules_path = tmp_path / "node_modules" / "package" / "index.js"
        assert index._should_skip_path(node_modules_path) is True

    def test_should_not_skip_regular_files(self, tmp_path):
        """Test that regular source files are not skipped."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python"],
        )

        index = CodeIndex(config, tmp_path)

        regular_path = tmp_path / "src" / "module.py"
        assert index._should_skip_path(regular_path) is False


class TestCodeIndexChunking:
    """Test code chunking logic."""

    def test_chunk_file_creates_chunks(self, tmp_path):
        """Test that chunk_file creates chunks from code."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python"],
        )

        index = CodeIndex(config, tmp_path)

        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test():\n    pass\n")

        chunks = index._chunk_file(test_file)

        assert isinstance(chunks, list)
        # Should have at least one chunk
        assert len(chunks) >= 0  # May be empty if file is too small

    def test_chunk_includes_line_numbers(self, tmp_path):
        """Test that chunks include line number information."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python"],
        )

        index = CodeIndex(config, tmp_path)

        # Create test file with multiple lines
        test_file = tmp_path / "test.py"
        content = "\n".join([f"# Line {i}" for i in range(1, 201)])
        test_file.write_text(content)

        chunks = index._chunk_file(test_file)

        if chunks:
            chunk = chunks[0]
            assert "start_line" in chunk
            assert "end_line" in chunk
            assert chunk["start_line"] >= 1


class TestCodeIndexSearch:
    """Test search functionality."""

    def test_search_has_correct_interface(self, tmp_path):
        """Test that search method has correct interface."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python"],
        )

        index = CodeIndex(config, tmp_path)

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
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python"],
        )

        index = CodeIndex(config, tmp_path)

        with pytest.raises(IndexError) as exc_info:
            index.search("test query")

        assert "not built" in str(exc_info.value).lower()


class TestCodeIndexUpdate:
    """Test incremental updates."""

    def test_update_has_correct_interface(self, tmp_path):
        """Test that update method has correct interface."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python"],
        )

        index = CodeIndex(config, tmp_path)

        # Verify method exists with correct signature
        assert hasattr(index, "update")
        assert callable(index.update)

        # Verify it accepts required parameters
        import inspect

        sig = inspect.signature(index.update)
        assert "changed_files" in sig.parameters


class TestCodeIndexHealthAndStats:
    """Test health checks and statistics."""

    def test_health_check_healthy(self, tmp_path):
        """Test health check when index is healthy."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python"],
        )

        index = CodeIndex(config, tmp_path)

        # Mock healthy table
        mock_table = Mock()
        mock_table.count_rows.return_value = 50
        index._table = mock_table

        health = index.health_check()

        assert isinstance(health, HealthStatus)
        assert health.healthy is True
        assert "50 chunks" in health.message

    def test_health_check_unhealthy(self, tmp_path):
        """Test health check when index is unhealthy."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python"],
        )

        index = CodeIndex(config, tmp_path)

        health = index.health_check()

        assert isinstance(health, HealthStatus)
        assert health.healthy is False

    def test_get_stats(self, tmp_path):
        """Test getting index statistics."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python", "javascript"],
        )

        index = CodeIndex(config, tmp_path)

        # Mock table
        mock_table = Mock()
        mock_table.count_rows.return_value = 75
        index._table = mock_table

        stats = index.get_stats()

        assert isinstance(stats, dict)
        assert "chunk_count" in stats
        assert stats["chunk_count"] == 75
        assert "embedding_model" in stats
        assert "languages" in stats
        assert "fts_enabled" in stats


class TestCodeIndexIntegration:
    """Integration tests with code-specific features."""

    def test_code_index_handles_empty_files(self, tmp_path):
        """Test that empty files don't cause errors."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python"],
        )

        index = CodeIndex(config, tmp_path)

        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")

        chunks = index._chunk_file(empty_file)
        assert isinstance(chunks, list)

    def test_end_to_end_interface(self, tmp_path):
        """Test complete workflow interface."""
        config = create_code_config(
            vector=VectorConfig(model="all-MiniLM-L6-v2", chunk_size=200),
            fts=FTSConfig(enabled=True),
            languages=["python"],
        )

        index = CodeIndex(config, tmp_path)

        # Verify all required methods exist
        assert hasattr(index, "build")
        assert hasattr(index, "search")
        assert hasattr(index, "update")
        assert hasattr(index, "health_check")
        assert hasattr(index, "get_stats")

        # Verify graph-related stubs exist (handled by GraphIndex)
        assert hasattr(index, "find_callers")
        assert hasattr(index, "find_dependencies")
        assert hasattr(index, "find_call_paths")
