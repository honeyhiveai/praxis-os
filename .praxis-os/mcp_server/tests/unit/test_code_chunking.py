"""Unit tests for CodeIndex code chunking functionality.

Phase 4, Task 4.3: Tests for _chunk_code(), _detect_language(), _extract_symbols().
"""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock
import sys
import importlib.util


class TestCodeChunking:
    """Test suite for code chunking methods."""

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

    def test_detect_language_python(self, code_index):
        """Test language detection for Python files."""
        assert code_index._detect_language(Path("test.py")) == "python"

    def test_detect_language_javascript(self, code_index):
        """Test language detection for JavaScript files."""
        assert code_index._detect_language(Path("test.js")) == "javascript"

    def test_detect_language_typescript(self, code_index):
        """Test language detection for TypeScript files."""
        assert code_index._detect_language(Path("test.ts")) == "typescript"

    def test_detect_language_go(self, code_index):
        """Test language detection for Go files."""
        assert code_index._detect_language(Path("test.go")) == "go"

    def test_detect_language_rust(self, code_index):
        """Test language detection for Rust files."""
        assert code_index._detect_language(Path("test.rs")) == "rust"

    def test_detect_language_unknown(self, code_index):
        """Test language detection for unknown extensions."""
        assert code_index._detect_language(Path("test.xyz")) == "unknown"

    def test_extract_symbols_python_functions(self, code_index):
        """Test symbol extraction for Python functions."""
        code = "def foo():\n    pass\ndef bar(x, y):\n    return x + y"
        symbols = code_index._extract_symbols(code, "python")
        assert "foo" in symbols
        assert "bar" in symbols

    def test_extract_symbols_python_classes(self, code_index):
        """Test symbol extraction for Python classes."""
        code = "class MyClass:\n    pass\nclass AnotherClass(Base):\n    pass"
        symbols = code_index._extract_symbols(code, "python")
        assert "MyClass" in symbols
        assert "AnotherClass" in symbols

    def test_extract_symbols_javascript_functions(self, code_index):
        """Test symbol extraction for JavaScript functions."""
        code = "function foo() {}\nconst bar = () => {}\nlet baz = async () => {}"
        symbols = code_index._extract_symbols(code, "javascript")
        assert "foo" in symbols
        assert "bar" in symbols
        assert "baz" in symbols

    def test_extract_symbols_typescript_functions(self, code_index):
        """Test symbol extraction for TypeScript functions with type annotations."""
        code = "function foo(): void {}\nconst bar: (x: number) => string = (x) => x.toString()"
        symbols = code_index._extract_symbols(code, "typescript")
        assert "foo" in symbols
        assert "bar" in symbols

    def test_extract_symbols_go(self, code_index):
        """Test symbol extraction for Go functions."""
        code = "func main() {}\nfunc calculateSum(a, b int) int {}"
        symbols = code_index._extract_symbols(code, "go")
        assert "main" in symbols
        assert "calculateSum" in symbols

    def test_extract_symbols_rust(self, code_index):
        """Test symbol extraction for Rust functions and structs."""
        code = "fn main() {}\nstruct Point { x: i32 }\nimpl Point {}"
        symbols = code_index._extract_symbols(code, "rust")
        assert "main" in symbols
        assert "Point" in symbols  # Both struct and impl

    def test_extract_symbols_removes_duplicates(self, code_index):
        """Test that duplicate symbols are removed."""
        code = "def foo():\n    pass\ndef foo():\n    pass"
        symbols = code_index._extract_symbols(code, "python")
        assert symbols.count("foo") == 1

    def test_extract_symbols_unknown_language(self, code_index):
        """Test that unknown languages return empty list."""
        code = "some code"
        symbols = code_index._extract_symbols(code, "unknown")
        assert symbols == []

    def test_chunk_code_simple_file(self, code_index, tmp_path):
        """Test chunking a simple Python file."""
        py_file = tmp_path / "simple.py"
        py_file.write_text("def foo():\n    pass\n\ndef bar():\n    return 42\n")
        
        chunks = code_index._chunk_code(py_file)
        
        assert len(chunks) >= 1
        assert all(chunk.tokens <= 500 for chunk in chunks)
        assert all(chunk.line_range[1] >= chunk.line_range[0] for chunk in chunks)
        assert all(chunk.language == "python" for chunk in chunks)

    def test_chunk_code_tracks_line_ranges(self, code_index, tmp_path):
        """Test that line ranges are correctly tracked."""
        py_file = tmp_path / "lines.py"
        py_file.write_text("line1\nline2\nline3\nline4\nline5\n")
        
        chunks = code_index._chunk_code(py_file)
        
        # First chunk should start at line 1
        assert chunks[0].line_range[0] == 1
        # Line ranges should be contiguous or overlapping
        for i in range(len(chunks) - 1):
            assert chunks[i+1].line_range[0] <= chunks[i].line_range[1] + 1

    def test_chunk_code_extracts_symbols(self, code_index, tmp_path):
        """Test that symbols are extracted from chunks."""
        py_file = tmp_path / "symbols.py"
        py_file.write_text("def authenticate(user):\n    pass\n\nclass User:\n    pass\n")
        
        chunks = code_index._chunk_code(py_file)
        
        # Should have extracted symbols
        all_symbols = []
        for chunk in chunks:
            all_symbols.extend(chunk.symbols)
        
        assert "authenticate" in all_symbols or "User" in all_symbols

    def test_chunk_code_empty_file(self, code_index, tmp_path):
        """Test that empty files return empty chunk list."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")
        
        chunks = code_index._chunk_code(empty_file)
        assert chunks == []

    def test_chunk_code_whitespace_only_file(self, code_index, tmp_path):
        """Test that whitespace-only files return empty chunk list."""
        whitespace_file = tmp_path / "whitespace.py"
        whitespace_file.write_text("   \n\n   \n")
        
        chunks = code_index._chunk_code(whitespace_file)
        assert chunks == []

    def test_chunk_code_generates_chunk_ids(self, code_index, tmp_path):
        """Test that chunk IDs are generated correctly."""
        py_file = tmp_path / "test.py"
        py_file.write_text("def foo():\n    pass\n")
        
        chunks = code_index._chunk_code(py_file)
        
        assert all(chunk.chunk_id is not None for chunk in chunks)
        assert all(":" in chunk.chunk_id for chunk in chunks)
        assert all("-" in chunk.chunk_id for chunk in chunks)

    def test_chunk_code_respects_chunk_size(self, code_index, tmp_path):
        """Test that chunks respect the 500-token limit."""
        # Create a file with many lines
        py_file = tmp_path / "large.py"
        lines = [f"def function_{i}():\n    pass\n" for i in range(100)]
        py_file.write_text("".join(lines))
        
        chunks = code_index._chunk_code(py_file)
        
        # All chunks should be <= chunk_size (500 tokens)
        assert all(chunk.tokens <= code_index.chunk_size for chunk in chunks)

    def test_chunk_code_applies_overlap(self, code_index, tmp_path):
        """Test that overlap is applied between chunks."""
        # Create a file large enough for multiple chunks
        py_file = tmp_path / "overlap.py"
        lines = [f"line_{i} = {i}\n" for i in range(200)]
        py_file.write_text("".join(lines))
        
        chunks = code_index._chunk_code(py_file)
        
        if len(chunks) > 1:
            # Check that chunks overlap (second chunk starts before first ends)
            assert chunks[1].line_range[0] <= chunks[0].line_range[1]

    def test_chunk_code_handles_unicode_decode_error(self, code_index, tmp_path):
        """Test that non-UTF-8 files raise UnicodeDecodeError."""
        binary_file = tmp_path / "binary.py"
        binary_file.write_bytes(b'\x80\x81\x82')  # Invalid UTF-8
        
        with pytest.raises(UnicodeDecodeError):
            code_index._chunk_code(binary_file)

    def test_chunk_code_handles_nonexistent_file(self, code_index, tmp_path):
        """Test that nonexistent files raise FileNotFoundError."""
        nonexistent = tmp_path / "nonexistent.py"
        
        with pytest.raises(FileNotFoundError):
            code_index._chunk_code(nonexistent)

    def test_build_uses_chunking(self, code_index, tmp_path):
        """Test that build() method uses chunking correctly."""
        # Create test files
        py_file1 = tmp_path / "file1.py"
        py_file1.write_text("def foo():\n    pass\n")
        py_file2 = tmp_path / "file2.py"
        py_file2.write_text("def bar():\n    pass\n")
        
        # build() should raise NotImplementedError after chunking (Task 4.4 incomplete)
        with pytest.raises(NotImplementedError, match="Task 4.4"):
            code_index.build(source_paths=[str(tmp_path)], force=True)
        
        # If we got here, chunking was successful (no exceptions before NotImplementedError)

    def test_chunk_code_large_file_performance(self, code_index, tmp_path):
        """Test that chunking handles larger files efficiently."""
        # Create a moderately large file (1000 lines)
        py_file = tmp_path / "large.py"
        lines = [f"def function_{i}(x, y, z):\n    return x + y + z\n\n" for i in range(1000)]
        py_file.write_text("".join(lines))
        
        chunks = code_index._chunk_code(py_file)
        
        # Should produce multiple chunks
        assert len(chunks) > 1
        # All chunks should be valid
        assert all(chunk.tokens > 0 for chunk in chunks)
        assert all(chunk.line_range[1] >= chunk.line_range[0] for chunk in chunks)

