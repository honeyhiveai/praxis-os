"""Unit tests for AST-aware code chunking with import penalty.

Tests UniversalASTChunker functionality:
- Config-driven initialization
- Python/TypeScript/Go file chunking
- Import grouping and penalty calculation
- Symbol extraction
- Token estimation
- Chunk type assignment
- Large function detection
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from ouroboros.subsystems.rag.code.ast_chunker import (
    CodeChunk,
    UniversalASTChunker
)
from ouroboros.utils.errors import ActionableError


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def python_config():
    """Standard Python chunking config from mcp.yaml."""
    return {
        "language_configs": {
            "python": {
                "chunking": {
                    "import_nodes": ["import_statement", "import_from_statement"],
                    "definition_nodes": ["function_definition", "class_definition"],
                    "split_boundary_nodes": ["if_statement", "for_statement"],
                    "import_penalty": 0.3
                }
            }
        }
    }


@pytest.fixture
def typescript_config():
    """Standard TypeScript chunking config."""
    return {
        "language_configs": {
            "typescript": {
                "chunking": {
                    "import_nodes": ["import_statement", "export_statement"],
                    "definition_nodes": ["function_declaration", "class_declaration"],
                    "split_boundary_nodes": ["if_statement", "for_statement"],
                    "import_penalty": 0.3
                }
            }
        }
    }


@pytest.fixture
def python_sample_file(tmp_path):
    """Create a sample Python file with imports, function, and class."""
    content = '''import os
import sys
from pathlib import Path

def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    return a + b

class DataProcessor:
    """Process data from various sources."""
    
    def __init__(self, name):
        self.name = name
    
    def process(self, data):
        return data.upper()
'''
    file_path = tmp_path / "sample.py"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def python_large_function_file(tmp_path):
    """Create a Python file with a large function (>600 tokens)."""
    # Generate a large function with many lines
    lines = [
        "def large_function():",
        "    '''A very large function for testing.'''",
    ]
    # Add 150 lines of code (~3750 chars = ~937 tokens)
    for i in range(150):
        lines.append(f"    var_{i} = {i} * 2 + {i} * 3")
    lines.append("    return var_149")
    
    content = "\n".join(lines)
    file_path = tmp_path / "large_func.py"
    file_path.write_text(content)
    return file_path


# ============================================================================
# Initialization Tests
# ============================================================================

class TestUniversalASTChunkerInitialization:
    """Test UniversalASTChunker initialization and config loading."""
    
    def test_init_with_valid_config(self, python_config, tmp_path):
        """Test initialization with valid Python config."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        
        assert chunker.language == "python"
        assert chunker.base_path == tmp_path
        assert "import_statement" in chunker.import_nodes
        assert "function_definition" in chunker.definition_nodes
        assert chunker.import_penalty == 0.3
        assert chunker.target_tokens == 500
        assert chunker.parser is not None
    
    def test_init_missing_language_configs(self, tmp_path):
        """Test error when language_configs missing from config."""
        config = {}
        
        with pytest.raises(ActionableError) as exc_info:
            UniversalASTChunker("python", config, tmp_path)
        
        assert "language_configs" in str(exc_info.value)
    
    def test_init_language_not_in_config(self, python_config, tmp_path):
        """Test error when requested language not in config."""
        with pytest.raises(ActionableError) as exc_info:
            UniversalASTChunker("rust", python_config, tmp_path)
        
        assert "rust" in str(exc_info.value)
        assert "not found" in str(exc_info.value)
    
    def test_init_missing_chunking_section(self, tmp_path):
        """Test error when chunking section missing."""
        config = {
            "language_configs": {
                "python": {}
            }
        }
        
        with pytest.raises(ActionableError) as exc_info:
            UniversalASTChunker("python", config, tmp_path)
        
        assert "chunking" in str(exc_info.value)


# ============================================================================
# Import Ratio Calculation Tests
# ============================================================================

class TestImportRatioCalculation:
    """Test _calculate_import_ratio() method."""
    
    def test_pure_imports_ratio_1_0(self, python_config, tmp_path):
        """Test that pure import content returns ratio 1.0."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        content = "import os\nimport sys\nfrom pathlib import Path"
        
        ratio = chunker._calculate_import_ratio(content)
        
        assert ratio == 1.0
    
    def test_pure_code_ratio_0_0(self, python_config, tmp_path):
        """Test that pure code (no imports) returns ratio 0.0."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        content = "def foo():\n    return 42\n\nclass Bar:\n    pass"
        
        ratio = chunker._calculate_import_ratio(content)
        
        assert ratio == 0.0
    
    def test_mixed_content_ratio_0_5(self, python_config, tmp_path):
        """Test 50/50 mix of imports and code."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        content = "import os\nimport sys\ndef foo():\n    pass"
        
        ratio = chunker._calculate_import_ratio(content)
        
        assert ratio == 0.5
    
    def test_empty_content_ratio_0_0(self, python_config, tmp_path):
        """Test that empty content returns ratio 0.0."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        
        ratio = chunker._calculate_import_ratio("")
        
        assert ratio == 0.0


# ============================================================================
# Penalty Calculation Tests
# ============================================================================

class TestPenaltyCalculation:
    """Test _calculate_penalty() method."""
    
    def test_high_import_ratio_gets_penalty(self, python_config, tmp_path):
        """Test ratio > 0.5 returns configured penalty (0.3)."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        
        penalty = chunker._calculate_penalty(1.0)
        assert penalty == 0.3
        
        penalty = chunker._calculate_penalty(0.6)
        assert penalty == 0.3
        
        penalty = chunker._calculate_penalty(0.51)
        assert penalty == 0.3
    
    def test_low_import_ratio_no_penalty(self, python_config, tmp_path):
        """Test ratio <= 0.5 returns no penalty (1.0)."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        
        penalty = chunker._calculate_penalty(0.0)
        assert penalty == 1.0
        
        penalty = chunker._calculate_penalty(0.4)
        assert penalty == 1.0
        
        penalty = chunker._calculate_penalty(0.5)
        assert penalty == 1.0


# ============================================================================
# Token Estimation Tests
# ============================================================================

class TestTokenEstimation:
    """Test _estimate_tokens() method."""
    
    def test_token_estimation_heuristic(self, python_config, tmp_path):
        """Test token count estimation (~4 chars per token)."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        
        # 400 chars ≈ 100 tokens
        content = "x" * 400
        tokens = chunker._estimate_tokens(content)
        assert tokens == 100
        
        # 2000 chars ≈ 500 tokens
        content = "y" * 2000
        tokens = chunker._estimate_tokens(content)
        assert tokens == 500
    
    def test_empty_content_zero_tokens(self, python_config, tmp_path):
        """Test empty content returns 0 tokens."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        
        tokens = chunker._estimate_tokens("")
        
        assert tokens == 0


# ============================================================================
# Symbol Extraction Tests
# ============================================================================

class TestSymbolExtraction:
    """Test _extract_symbol_name() method."""
    
    def test_extract_function_name(self, python_config, tmp_path, python_sample_file):
        """Test extraction of function name from AST node."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        code = python_sample_file.read_text()
        tree = chunker.parser.parse(bytes(code, 'utf-8'))
        
        # Find function_definition node
        func_node = None
        for node in tree.root_node.children:
            if node.type == "function_definition":
                func_node = node
                break
        
        assert func_node is not None
        symbol = chunker._extract_symbol_name(func_node, code)
        assert symbol == "calculate_sum"
    
    def test_extract_class_name(self, python_config, tmp_path, python_sample_file):
        """Test extraction of class name from AST node."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        code = python_sample_file.read_text()
        tree = chunker.parser.parse(bytes(code, 'utf-8'))
        
        # Find class_definition node
        class_node = None
        for node in tree.root_node.children:
            if node.type == "class_definition":
                class_node = node
                break
        
        assert class_node is not None
        symbol = chunker._extract_symbol_name(class_node, code)
        assert symbol == "DataProcessor"


# ============================================================================
# Import Chunking Tests
# ============================================================================

class TestImportChunking:
    """Test _chunk_imports() method."""
    
    def test_chunk_imports_creates_single_chunk(self, python_config, tmp_path, python_sample_file):
        """Test that multiple imports are grouped into single chunk."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        code = python_sample_file.read_text()
        tree = chunker.parser.parse(bytes(code, 'utf-8'))
        
        # Collect import nodes
        import_nodes = [
            node for node in tree.root_node.children
            if node.type in chunker.import_nodes
        ]
        
        chunk = chunker._chunk_imports(import_nodes, code, python_sample_file)
        
        assert chunk is not None
        assert chunk.chunk_type == "import"
        assert chunk.import_ratio == 1.0
        assert chunk.import_penalty == 0.3
        assert "import os" in chunk.content
        assert "import sys" in chunk.content
        assert "from pathlib import Path" in chunk.content
    
    def test_chunk_imports_empty_list_returns_none(self, python_config, tmp_path):
        """Test that empty import node list returns None."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        
        chunk = chunker._chunk_imports([], "code", Path("/fake.py"))
        
        assert chunk is None


# ============================================================================
# Definition Chunking Tests
# ============================================================================

class TestDefinitionChunking:
    """Test _chunk_definition() method."""
    
    def test_chunk_function_definition(self, python_config, tmp_path, python_sample_file):
        """Test chunking of function definition."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        code = python_sample_file.read_text()
        tree = chunker.parser.parse(bytes(code, 'utf-8'))
        
        # Find function node
        func_node = None
        for node in tree.root_node.children:
            if node.type == "function_definition":
                func_node = node
                break
        
        chunk = chunker._chunk_definition(func_node, code, python_sample_file)
        
        assert chunk.chunk_type == "function"
        assert "calculate_sum" in chunk.symbols
        assert "def calculate_sum" in chunk.content
        assert chunk.import_ratio == 0.0  # Pure code, no imports
        assert chunk.import_penalty == 1.0  # No penalty
    
    def test_chunk_class_definition(self, python_config, tmp_path, python_sample_file):
        """Test chunking of class definition."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        code = python_sample_file.read_text()
        tree = chunker.parser.parse(bytes(code, 'utf-8'))
        
        # Find class node
        class_node = None
        for node in tree.root_node.children:
            if node.type == "class_definition":
                class_node = node
                break
        
        chunk = chunker._chunk_definition(class_node, code, python_sample_file)
        
        assert chunk.chunk_type == "class"
        assert "DataProcessor" in chunk.symbols
        assert "class DataProcessor" in chunk.content
        assert chunk.import_ratio == 0.0


# ============================================================================
# File Chunking Integration Tests
# ============================================================================

class TestFileChunking:
    """Test chunk_file() method (end-to-end integration)."""
    
    def test_chunk_python_file_complete(self, python_config, tmp_path, python_sample_file):
        """Test complete Python file chunking (imports + function + class)."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        
        chunks = chunker.chunk_file(python_sample_file)
        
        # Expect: 1 import chunk + 1 function + 1 class = 3 chunks
        assert len(chunks) == 3
        
        # First chunk should be imports
        assert chunks[0].chunk_type == "import"
        assert chunks[0].import_ratio == 1.0
        
        # Second chunk should be function
        assert chunks[1].chunk_type == "function"
        assert "calculate_sum" in chunks[1].symbols
        
        # Third chunk should be class
        assert chunks[2].chunk_type == "class"
        assert "DataProcessor" in chunks[2].symbols
    
    def test_chunk_file_imports_first_order(self, python_config, tmp_path, python_sample_file):
        """Test that imports always appear first in chunk list."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        
        chunks = chunker.chunk_file(python_sample_file)
        
        assert chunks[0].chunk_type == "import"
        assert chunks[0].start_line < chunks[1].start_line
        assert chunks[0].start_line < chunks[2].start_line
    
    def test_chunk_file_nonexistent_returns_empty(self, python_config, tmp_path):
        """Test that non-existent file returns empty list."""
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        
        chunks = chunker.chunk_file(tmp_path / "nonexistent.py")
        
        assert chunks == []
    
    def test_chunk_large_function_logged(self, python_config, tmp_path, python_large_function_file, caplog):
        """Test that large functions are detected and logged."""
        import logging
        caplog.set_level(logging.DEBUG)
        
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        
        chunks = chunker.chunk_file(python_large_function_file)
        
        # Should still create chunk (no splitting in MVP)
        assert len(chunks) == 1
        assert chunks[0].chunk_type == "function"
        assert chunks[0].token_count > 600  # Should be ~937 tokens
        
        # Check debug log
        assert "Large function detected" in caplog.text


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_python_file(self, python_config, tmp_path):
        """Test chunking an empty Python file."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")
        
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        chunks = chunker.chunk_file(empty_file)
        
        # Empty file should return empty list
        assert chunks == []
    
    def test_python_file_only_imports(self, python_config, tmp_path):
        """Test file with only imports (no definitions)."""
        imports_only = tmp_path / "imports_only.py"
        imports_only.write_text("import os\nimport sys\n")
        
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        chunks = chunker.chunk_file(imports_only)
        
        assert len(chunks) == 1
        assert chunks[0].chunk_type == "import"
        assert chunks[0].import_ratio == 1.0
    
    def test_python_file_only_code_no_imports(self, python_config, tmp_path):
        """Test file with only code (no imports)."""
        code_only = tmp_path / "code_only.py"
        code_only.write_text("def foo():\n    return 42\n")
        
        chunker = UniversalASTChunker("python", python_config, tmp_path)
        chunks = chunker.chunk_file(code_only)
        
        assert len(chunks) == 1
        assert chunks[0].chunk_type == "function"
        assert chunks[0].import_ratio == 0.0


# ============================================================================
# CodeChunk Dataclass Tests
# ============================================================================

class TestCodeChunkDataclass:
    """Test CodeChunk dataclass properties."""
    
    def test_code_chunk_frozen(self):
        """Test that CodeChunk is immutable (frozen)."""
        chunk = CodeChunk(
            content="test",
            file_path=Path("/test.py"),
            start_line=1,
            end_line=5,
            chunk_type="function",
            symbols=["test"],
            import_ratio=0.0,
            import_penalty=1.0,
            token_count=10
        )
        
        with pytest.raises(AttributeError):
            chunk.content = "modified"  # Should fail (frozen)
    
    def test_code_chunk_all_fields(self):
        """Test that all CodeChunk fields are accessible."""
        chunk = CodeChunk(
            content="def foo(): pass",
            file_path=Path("/test.py"),
            start_line=10,
            end_line=11,
            chunk_type="function",
            symbols=["foo"],
            import_ratio=0.0,
            import_penalty=1.0,
            token_count=5
        )
        
        assert chunk.content == "def foo(): pass"
        assert chunk.file_path == Path("/test.py")
        assert chunk.start_line == 10
        assert chunk.end_line == 11
        assert chunk.chunk_type == "function"
        assert chunk.symbols == ["foo"]
        assert chunk.import_ratio == 0.0
        assert chunk.import_penalty == 1.0
        assert chunk.token_count == 5

