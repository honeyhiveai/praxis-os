"""Unit tests for CodeIndex file discovery functionality.

Phase 4, Task 4.2: Tests for _discover_files() and related methods.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock
import sys
import importlib.util


class TestCodeFileDiscovery:
    """Test suite for code file discovery methods."""

    @pytest.fixture
    def code_index(self, tmp_path):
        """Create a CodeIndex instance for testing."""
        # Load base module
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        # Load code_index module with mocked SentenceTransformer
        with patch('sentence_transformers.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_st.return_value = mock_model
            
            code_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "code_index.py"
            code_spec = importlib.util.spec_from_file_location("server.indexes.code_index", code_index_path)
            code_module = importlib.util.module_from_spec(code_spec)
            sys.modules['server.indexes.code_index'] = code_module
            
            code_module.BaseIndex = base_module.BaseIndex
            code_module.SearchResult = base_module.SearchResult
            code_module.SentenceTransformer = mock_st
            
            code_spec.loader.exec_module(code_module)
            
            config = {"embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"}}
            index = code_module.CodeIndex(cache_path=tmp_path, config=config)
            return index

    @pytest.fixture
    def test_file_structure(self, tmp_path):
        """Create a test file structure for discovery tests."""
        # Create directories
        (tmp_path / "src").mkdir()
        (tmp_path / "lib").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "venv").mkdir()
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "src" / "__pycache__").mkdir()
        
        # Create Python files
        (tmp_path / "src" / "main.py").write_text("print('hello')")
        (tmp_path / "src" / "utils.py").write_text("def util(): pass")
        (tmp_path / "lib" / "lib.py").write_text("class Lib: pass")
        (tmp_path / "tests" / "test_main.py").write_text("def test(): pass")
        
        # Create JS/TS files
        (tmp_path / "src" / "app.js").write_text("console.log('hi')")
        (tmp_path / "src" / "types.ts").write_text("type A = string")
        
        # Create files that should be excluded
        (tmp_path / "venv" / "excluded.py").write_text("# should be excluded")
        (tmp_path / "node_modules" / "lib.js").write_text("// should be excluded")
        (tmp_path / "src" / "__pycache__" / "cached.pyc").write_text("# cached")
        
        return tmp_path

    def test_discover_files_finds_python_files(self, code_index, test_file_structure):
        """Test that _discover_files finds all Python files."""
        files = code_index._discover_files(
            source_paths=[str(test_file_structure)],
            include_patterns=["**/*.py"],
            exclude_patterns=["**/venv/**", "**/node_modules/**", "**/__pycache__/**"]
        )
        
        # Should find 4 .py files (main.py, utils.py, lib.py, test_main.py)
        assert len(files) == 4
        assert all(f.suffix == ".py" for f in files)
        assert not any("venv" in str(f) for f in files)
        assert not any("node_modules" in str(f) for f in files)
        assert not any("__pycache__" in str(f) for f in files)

    def test_discover_files_finds_multiple_extensions(self, code_index, test_file_structure):
        """Test that _discover_files finds files with multiple extensions."""
        files = code_index._discover_files(
            source_paths=[str(test_file_structure)],
            include_patterns=["**/*.py", "**/*.js", "**/*.ts"],
            exclude_patterns=["**/venv/**", "**/node_modules/**", "**/__pycache__/**"]
        )
        
        # Should find 6 files (4 .py + 1 .js + 1 .ts)
        assert len(files) == 6
        extensions = {f.suffix for f in files}
        assert extensions == {".py", ".js", ".ts"}

    def test_discover_files_excludes_venv(self, code_index, test_file_structure):
        """Test that _discover_files excludes venv directory."""
        files = code_index._discover_files(
            source_paths=[str(test_file_structure)],
            include_patterns=["**/*.py"],
            exclude_patterns=["**/venv/**"]
        )
        
        assert not any("venv" in str(f) for f in files)

    def test_discover_files_excludes_node_modules(self, code_index, test_file_structure):
        """Test that _discover_files excludes node_modules directory."""
        files = code_index._discover_files(
            source_paths=[str(test_file_structure)],
            include_patterns=["**/*.js"],
            exclude_patterns=["**/node_modules/**"]
        )
        
        assert not any("node_modules" in str(f) for f in files)

    def test_discover_files_excludes_pycache(self, code_index, test_file_structure):
        """Test that _discover_files excludes __pycache__ directory."""
        files = code_index._discover_files(
            source_paths=[str(test_file_structure)],
            include_patterns=["**/*.pyc"],
            exclude_patterns=["**/__pycache__/**"]
        )
        
        assert not any("__pycache__" in str(f) for f in files)

    def test_discover_files_handles_single_file(self, code_index, test_file_structure):
        """Test that _discover_files handles a single file path."""
        single_file = test_file_structure / "src" / "main.py"
        files = code_index._discover_files(
            source_paths=[str(single_file)],
            include_patterns=["**/*.py"],
            exclude_patterns=[]
        )
        
        assert len(files) == 1
        assert files[0].name == "main.py"

    def test_discover_files_handles_multiple_source_paths(self, code_index, test_file_structure):
        """Test that _discover_files handles multiple source paths."""
        files = code_index._discover_files(
            source_paths=[str(test_file_structure / "src"), str(test_file_structure / "lib")],
            include_patterns=["**/*.py"],
            exclude_patterns=["**/__pycache__/**"]
        )
        
        # Should find 3 files (main.py, utils.py from src; lib.py from lib)
        assert len(files) == 3
        assert any(f.name == "main.py" for f in files)
        assert any(f.name == "utils.py" for f in files)
        assert any(f.name == "lib.py" for f in files)

    def test_discover_files_raises_on_nonexistent_path(self, code_index, tmp_path):
        """Test that _discover_files raises FileNotFoundError for nonexistent paths."""
        with pytest.raises(FileNotFoundError, match="Source path does not exist"):
            code_index._discover_files(
                source_paths=[str(tmp_path / "nonexistent")],
                include_patterns=["**/*.py"],
                exclude_patterns=[]
            )

    def test_discover_files_returns_sorted_results(self, code_index, test_file_structure):
        """Test that _discover_files returns sorted file list."""
        files = code_index._discover_files(
            source_paths=[str(test_file_structure)],
            include_patterns=["**/*.py"],
            exclude_patterns=["**/venv/**", "**/node_modules/**", "**/__pycache__/**"]
        )
        
        # Verify results are sorted
        assert files == sorted(files)

    def test_discover_files_removes_duplicates(self, code_index, test_file_structure):
        """Test that _discover_files removes duplicate file entries."""
        # Pass the same source path twice
        files = code_index._discover_files(
            source_paths=[str(test_file_structure), str(test_file_structure)],
            include_patterns=["**/*.py"],
            exclude_patterns=["**/venv/**", "**/node_modules/**", "**/__pycache__/**"]
        )
        
        # Should not have duplicates
        assert len(files) == len(set(files))

    def test_matches_patterns_include_only(self, code_index, tmp_path):
        """Test _matches_patterns with include patterns only."""
        py_file = tmp_path / "test.py"
        py_file.touch()
        
        assert code_index._matches_patterns(py_file, ["**/*.py"], []) is True
        assert code_index._matches_patterns(py_file, ["**/*.js"], []) is False

    def test_matches_patterns_exclude_takes_precedence(self, code_index, tmp_path):
        """Test that exclude patterns take precedence over include patterns."""
        venv_file = tmp_path / "venv" / "test.py"
        venv_file.parent.mkdir()
        venv_file.touch()
        
        # Matches include but also matches exclude
        assert code_index._matches_patterns(
            venv_file,
            ["**/*.py"],
            ["**/venv/**"]
        ) is False

    def test_path_matches_glob_simple(self, code_index, tmp_path):
        """Test _path_matches_glob with simple patterns."""
        py_file = tmp_path / "test.py"
        
        assert code_index._path_matches_glob(py_file, "**/*.py") is True
        assert code_index._path_matches_glob(py_file, "**/*.js") is False

    def test_path_matches_glob_recursive(self, code_index, tmp_path):
        """Test _path_matches_glob with recursive patterns."""
        nested_file = tmp_path / "a" / "b" / "c" / "test.py"
        
        assert code_index._path_matches_glob(nested_file, "**/*.py") is True
        assert code_index._path_matches_glob(nested_file, "**/c/*.py") is True

    def test_build_discovers_code_files(self, code_index, test_file_structure):
        """Test that build() method uses _discover_files correctly."""
        # Spy on _discover_files to verify it's called
        original_discover = code_index._discover_files
        called_with = []
        
        def spy_discover(*args, **kwargs):
            called_with.append((args, kwargs))
            return original_discover(*args, **kwargs)
        
        code_index._discover_files = spy_discover
        
        # build() should raise NotImplementedError after discovery (Task 4.3-4.4 incomplete)
        with pytest.raises(NotImplementedError, match="Tasks 4.3-4.4"):
            code_index.build(source_paths=[str(test_file_structure)], force=True)
        
        # Verify _discover_files was called
        assert len(called_with) == 1
        args, kwargs = called_with[0]
        assert str(test_file_structure) in args[0]  # source_paths
        assert "**/*.py" in args[1]  # include_patterns
        assert "**/__pycache__/**" in args[2]  # exclude_patterns

    def test_build_handles_no_files_found(self, code_index, tmp_path):
        """Test that build() handles gracefully when no files are discovered."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        # Should return early without raising
        code_index.build(source_paths=[str(empty_dir)], force=True)
        # No exception = success

