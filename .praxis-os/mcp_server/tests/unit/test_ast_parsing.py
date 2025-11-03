"""Unit tests for AST parsing functionality (Phase 5, Task 5.3).

Tests cover:
- Symbol dataclass
- _parse_file() method with Tree-sitter integration
- _get_node_type_map() for language-specific mappings
- _extract_symbols_from_node() for tree traversal
- _extract_symbol_name() for name extraction
- _extract_signature() for function signatures
- Error handling and graceful degradation
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
import sys
import importlib.util


class TestSymbolDataclass:
    """Test suite for Symbol dataclass."""

    def test_symbol_initialization(self):
        """Test that Symbol dataclass initializes correctly."""
        # Load base module first
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        # Load ast_index module
        ast_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "ast_index.py"
        spec = importlib.util.spec_from_file_location("server.indexes.ast_index", ast_index_path)
        ast_module = importlib.util.module_from_spec(spec)
        sys.modules['server.indexes.ast_index'] = ast_module
        ast_module.BaseIndex = base_module.BaseIndex
        ast_module.SearchResult = base_module.SearchResult
        spec.loader.exec_module(ast_module)
        
        Symbol = ast_module.Symbol
        
        symbol = Symbol(
            symbol_name="authenticate",
            symbol_type="function",
            file_path="src/auth.py",
            line_range=(10, 20),
            language="python",
            signature="def authenticate(user, pwd)"
        )
        
        assert symbol.symbol_name == "authenticate"
        assert symbol.symbol_type == "function"
        assert symbol.file_path == "src/auth.py"
        assert symbol.line_range == (10, 20)
        assert symbol.language == "python"
        assert symbol.signature == "def authenticate(user, pwd)"

    def test_symbol_generates_id(self):
        """Test that Symbol auto-generates symbol_id."""
        # Load base module first
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        ast_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "ast_index.py"
        spec = importlib.util.spec_from_file_location("server.indexes.ast_index", ast_index_path)
        ast_module = importlib.util.module_from_spec(spec)
        sys.modules['server.indexes.ast_index'] = ast_module
        ast_module.BaseIndex = base_module.BaseIndex
        ast_module.SearchResult = base_module.SearchResult
        spec.loader.exec_module(ast_module)
        
        Symbol = ast_module.Symbol
        
        symbol = Symbol(
            symbol_name="User",
            symbol_type="class",
            file_path="src/models.py",
            line_range=(5, 15),
            language="python"
        )
        
        assert symbol.symbol_id == "src/models.py:5-15"

    def test_symbol_default_signature(self):
        """Test that Symbol has empty string as default signature."""
        # Load base module first
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        ast_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "ast_index.py"
        spec = importlib.util.spec_from_file_location("server.indexes.ast_index", ast_index_path)
        ast_module = importlib.util.module_from_spec(spec)
        sys.modules['server.indexes.ast_index'] = ast_module
        ast_module.BaseIndex = base_module.BaseIndex
        ast_module.SearchResult = base_module.SearchResult
        spec.loader.exec_module(ast_module)
        
        Symbol = ast_module.Symbol
        
        symbol = Symbol(
            symbol_name="User",
            symbol_type="class",
            file_path="src/models.py",
            line_range=(5, 15),
            language="python"
        )
        
        assert symbol.signature == ""


class TestNodeTypeMapping:
    """Test suite for language-specific node type mappings."""

    @pytest.fixture
    def mock_ast_index(self, tmp_path):
        """Create mock ASTIndex instance."""
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        ast_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "ast_index.py"
        ast_spec = importlib.util.spec_from_file_location("server.indexes.ast_index", ast_index_path)
        ast_module = importlib.util.module_from_spec(ast_spec)
        sys.modules['server.indexes.ast_index'] = ast_module
        
        ast_module.BaseIndex = base_module.BaseIndex
        ast_module.SearchResult = base_module.SearchResult
        
        ast_spec.loader.exec_module(ast_module)
        
        # Mock importlib to avoid requiring actual parsers
        with patch('importlib.import_module', return_value=MagicMock()):
            config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
            return ast_module.ASTIndex(cache_path=tmp_path, config=config)

    def test_get_node_type_map_python(self, mock_ast_index):
        """Test node type map for Python."""
        node_map = mock_ast_index._get_node_type_map("python")
        
        assert "function_definition" in node_map
        assert node_map["function_definition"] == "function"
        assert "class_definition" in node_map
        assert node_map["class_definition"] == "class"

    def test_get_node_type_map_javascript(self, mock_ast_index):
        """Test node type map for JavaScript."""
        node_map = mock_ast_index._get_node_type_map("javascript")
        
        assert "function_declaration" in node_map
        assert node_map["function_declaration"] == "function"
        assert "class_declaration" in node_map
        assert node_map["class_declaration"] == "class"
        assert "method_definition" in node_map
        assert node_map["method_definition"] == "method"

    def test_get_node_type_map_unknown_language(self, mock_ast_index):
        """Test node type map for unknown language returns empty dict."""
        node_map = mock_ast_index._get_node_type_map("unknown")
        
        assert node_map == {}


class TestSymbolExtraction:
    """Test suite for symbol extraction helper methods."""

    @pytest.fixture
    def mock_ast_index(self, tmp_path):
        """Create mock ASTIndex instance."""
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        ast_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "ast_index.py"
        ast_spec = importlib.util.spec_from_file_location("server.indexes.ast_index", ast_index_path)
        ast_module = importlib.util.module_from_spec(ast_spec)
        sys.modules['server.indexes.ast_index'] = ast_module
        
        ast_module.BaseIndex = base_module.BaseIndex
        ast_module.SearchResult = base_module.SearchResult
        
        ast_spec.loader.exec_module(ast_module)
        
        # Mock importlib to avoid requiring actual parsers
        with patch('importlib.import_module', return_value=MagicMock()):
            config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
            return ast_module.ASTIndex(cache_path=tmp_path, config=config)

    def test_extract_symbol_name(self, mock_ast_index):
        """Test extraction of symbol name from node."""
        # Create mock node with identifier child
        mock_identifier = MagicMock()
        mock_identifier.type = "identifier"
        mock_identifier.text = b"authenticate"
        
        mock_node = MagicMock()
        mock_node.children = [mock_identifier]
        
        name = mock_ast_index._extract_symbol_name(mock_node, "python")
        
        assert name == "authenticate"

    def test_extract_symbol_name_no_identifier(self, mock_ast_index):
        """Test extraction when no identifier child exists."""
        mock_node = MagicMock()
        mock_node.children = []
        
        name = mock_ast_index._extract_symbol_name(mock_node, "python")
        
        assert name == ""

    def test_extract_signature(self, mock_ast_index):
        """Test extraction of function signature."""
        content = "def authenticate(username, password):\n    return True"
        
        mock_node = MagicMock()
        mock_node.start_byte = 0
        mock_node.end_byte = len(content)
        
        signature = mock_ast_index._extract_signature(mock_node, content)
        
        assert signature == "def authenticate(username, password):"

    def test_extract_signature_handles_error(self, mock_ast_index):
        """Test signature extraction handles errors gracefully."""
        mock_node = MagicMock()
        mock_node.start_byte = 0
        mock_node.end_byte = 100
        
        content = "short"
        
        signature = mock_ast_index._extract_signature(mock_node, content)
        
        # Python string slicing doesn't raise on out-of-bounds, just returns what's available
        assert signature == "short"


class TestParseFile:
    """Test suite for _parse_file() method."""

    @pytest.fixture
    def mock_ast_index(self, tmp_path):
        """Create mock ASTIndex instance."""
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        ast_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "ast_index.py"
        ast_spec = importlib.util.spec_from_file_location("server.indexes.ast_index", ast_index_path)
        ast_module = importlib.util.module_from_spec(ast_spec)
        sys.modules['server.indexes.ast_index'] = ast_module
        
        ast_module.BaseIndex = base_module.BaseIndex
        ast_module.SearchResult = base_module.SearchResult
        
        ast_spec.loader.exec_module(ast_module)
        
        # Mock importlib to avoid requiring actual parsers
        with patch('importlib.import_module', return_value=MagicMock()):
            config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
            return ast_module.ASTIndex(cache_path=tmp_path, config=config)

    def test_parse_file_raises_on_file_not_found(self, mock_ast_index, tmp_path):
        """Test that _parse_file raises FileNotFoundError for missing file."""
        nonexistent = tmp_path / "nonexistent.py"
        mock_parser = MagicMock()
        
        # Mock tree-sitter to be available so file check happens
        with patch.dict('sys.modules', {'tree_sitter': Mock()}):
            with patch('builtins.__import__', return_value=Mock()):
                with pytest.raises(FileNotFoundError):
                    mock_ast_index._parse_file(nonexistent, "python", mock_parser)

    def test_parse_file_handles_tree_sitter_not_installed(self, mock_ast_index, tmp_path):
        """Test graceful handling when tree-sitter not installed."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")
        
        mock_parser = MagicMock()
        
        # Mock tree_sitter import to fail
        with patch.dict('sys.modules', {'tree_sitter': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module")):
                symbols = mock_ast_index._parse_file(test_file, "python", mock_parser)
        
        # Should return empty list, not raise
        assert symbols == []

    def test_parse_file_handles_parser_init_error(self, mock_ast_index, tmp_path):
        """Test graceful handling when parser initialization fails."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")
        
        mock_parser = MagicMock()
        # Parser module missing language() function
        mock_parser.language = None
        
        symbols = mock_ast_index._parse_file(test_file, "python", mock_parser)
        
        # Should return empty list, not raise
        assert symbols == []

    def test_parse_file_handles_parse_error(self, mock_ast_index, tmp_path):
        """Test graceful handling when parsing fails."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo(): pass")
        
        mock_parser_module = MagicMock()
        mock_language = MagicMock()
        mock_parser_module.language.return_value = mock_language
        
        # Get the module and patch Parser class in it
        import sys
        ast_module = sys.modules.get('server.indexes.ast_index')
        
        if ast_module:
            # Mock Parser class inside the module
            with patch.object(ast_module, 'Parser', create=True) as MockParser:
                mock_parser_instance = MagicMock()
                mock_parser_instance.parse.side_effect = Exception("Parse failed")
                MockParser.return_value = mock_parser_instance
                
                # Also need to mock tree_sitter import
                mock_tree_sitter = MagicMock()
                mock_tree_sitter.Parser = MockParser
                with patch.dict('sys.modules', {'tree_sitter': mock_tree_sitter}):
                    symbols = mock_ast_index._parse_file(test_file, "python", mock_parser_module)
                
                # Should return empty list, not raise
                assert symbols == []
        else:
            # If module not loaded, just verify method exists
            assert hasattr(mock_ast_index, '_parse_file')

