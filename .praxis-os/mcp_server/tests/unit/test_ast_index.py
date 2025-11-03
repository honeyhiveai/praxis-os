"""Unit tests for ASTIndex class (Phase 5, Task 5.1-5.2).

Tests cover:
- Class initialization and BaseIndex implementation
- Language configuration loading
- Parser cache initialization
- LanceDB connection setup
- Dynamic parser loading (Task 5.2)
- Stub method validation (build, search, update, delete)
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys
import importlib.util
import logging


class TestASTIndexInit:
    """Test suite for ASTIndex initialization (Task 5.1)."""

    @pytest.fixture
    def mock_ast_index_class(self):
        """Load ASTIndex class with mocked dependencies."""
        # Load base module first
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        # Load ast_index module
        ast_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "ast_index.py"
        ast_spec = importlib.util.spec_from_file_location("server.indexes.ast_index", ast_index_path)
        ast_module = importlib.util.module_from_spec(ast_spec)
        sys.modules['server.indexes.ast_index'] = ast_module
        
        ast_module.BaseIndex = base_module.BaseIndex
        ast_module.SearchResult = base_module.SearchResult
        
        ast_spec.loader.exec_module(ast_module)
        
        return ast_module.ASTIndex

    def test_ast_index_implements_base_index(self, tmp_path, mock_ast_index_class):
        """Test that ASTIndex implements BaseIndex interface."""
        config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
        ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
        
        # Should be instance of BaseIndex
        from server.indexes.base import BaseIndex
        assert isinstance(ast_index, BaseIndex)

    def test_ast_index_initializes_attributes(self, tmp_path, mock_ast_index_class):
        """Test that ASTIndex correctly initializes all required attributes."""
        config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function"}}, "javascript": {"file_extensions": [".js"], "node_types": {"function_declaration": "function"}}}}
        ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
        
        # Core attributes
        assert ast_index.cache_path == tmp_path
        assert ast_index.config == config
        assert ast_index.table_name == "praxis_os_code_ast"
        
        # Supported languages from config
        assert ast_index.supported_languages == ["python", "javascript"]
        
        # Parser cache initialized as dict (may have parsers if installed)
        assert isinstance(ast_index.parser_cache, dict)
        # Parser cache may contain parsers if they're installed
        # Just verify it's a dict, not empty
        
        # LanceDB connection not yet established
        assert ast_index.db is None
        assert ast_index.table is None

    def test_ast_index_uses_default_languages(self, tmp_path, mock_ast_index_class):
        """Test that ASTIndex falls back to default languages if not in config."""
        config = {}  # No languages specified
        ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
        
        # Should use defaults
        assert len(ast_index.supported_languages) > 0
        assert "python" in ast_index.supported_languages
        assert "javascript" in ast_index.supported_languages

    def test_ast_index_loads_custom_languages(self, tmp_path, mock_ast_index_class):
        """Test that ASTIndex loads custom languages from config."""
        config = {"languages": {"go": {"file_extensions": [".go"], "node_types": {}}, "rust": {"file_extensions": [".rs"], "node_types": {}}, "c": {"file_extensions": [".c"], "node_types": {}}}}
        ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
        
        assert ast_index.supported_languages == ["go", "rust", "c"]

    def test_ast_index_raises_on_empty_languages(self, tmp_path, mock_ast_index_class):
        """Test that ASTIndex raises ValueError if languages list is empty."""
        config = {"languages": {}}
        
        with pytest.raises(ValueError, match="at least one language"):
            mock_ast_index_class(cache_path=tmp_path, config=config)

    def test_ast_index_parser_cache_is_dict(self, tmp_path, mock_ast_index_class):
        """Test that parser_cache is initialized as a dict (may contain parsers if installed)."""
        config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
        ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
        
        # Parser cache is a dict (may have parsers if tree-sitter packages installed)
        assert isinstance(ast_index.parser_cache, dict)


class TestASTIndexConnection:
    """Test suite for ASTIndex LanceDB connection (Task 5.1)."""

    @pytest.fixture
    def mock_ast_index_class(self):
        """Load ASTIndex class with mocked dependencies."""
        # Load base module first
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        # Load ast_index module
        ast_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "ast_index.py"
        ast_spec = importlib.util.spec_from_file_location("server.indexes.ast_index", ast_index_path)
        ast_module = importlib.util.module_from_spec(ast_spec)
        sys.modules['server.indexes.ast_index'] = ast_module
        
        ast_module.BaseIndex = base_module.BaseIndex
        ast_module.SearchResult = base_module.SearchResult
        
        ast_spec.loader.exec_module(ast_module)
        
        return ast_module.ASTIndex

    def test_connect_creates_cache_directory(self, tmp_path, mock_ast_index_class):
        """Test that _connect_to_index creates cache directory if missing."""
        cache_path = tmp_path / "nonexistent"
        config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
        ast_index = mock_ast_index_class(cache_path=cache_path, config=config)
        
        # Directory doesn't exist yet
        assert not cache_path.exists()
        
        # Mock lancedb in the ast_index module's namespace
        import sys
        ast_module = sys.modules['server.indexes.ast_index']
        
        with patch.object(ast_module.lancedb, 'connect') as mock_connect:
            mock_db = MagicMock()
            mock_table = MagicMock()
            mock_db.open_table.return_value = mock_table
            mock_connect.return_value = mock_db
            
            ast_index._connect_to_index()
        
        # Directory should now exist
        assert cache_path.exists()

    def test_connect_raises_on_table_not_found(self, tmp_path, mock_ast_index_class):
        """Test that _connect_to_index raises RuntimeError if table doesn't exist."""
        config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
        ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
        
        # Mock lancedb in the ast_index module's namespace
        import sys
        ast_module = sys.modules['server.indexes.ast_index']
        
        with patch.object(ast_module.lancedb, 'connect') as mock_connect:
            mock_db = MagicMock()
            mock_db.open_table.side_effect = Exception("Table not found")
            mock_connect.return_value = mock_db
            
            with pytest.raises(RuntimeError, match="AST index connection failed"):
                ast_index._connect_to_index()


class TestASTIndexStubMethods:
    """Test suite for ASTIndex stub methods (Task 5.1)."""

    @pytest.fixture
    def mock_ast_index_class(self):
        """Load ASTIndex class with mocked dependencies."""
        # Load base module first
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        # Load ast_index module
        ast_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "ast_index.py"
        ast_spec = importlib.util.spec_from_file_location("server.indexes.ast_index", ast_index_path)
        ast_module = importlib.util.module_from_spec(ast_spec)
        sys.modules['server.indexes.ast_index'] = ast_module
        
        ast_module.BaseIndex = base_module.BaseIndex
        ast_module.SearchResult = base_module.SearchResult
        
        ast_spec.loader.exec_module(ast_module)
        
        return ast_module.ASTIndex

    def test_build_returns_without_error(self, tmp_path, mock_ast_index_class):
        """Test that build() executes without error (implemented in Tasks 5.3-5.4)."""
        config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
        ast_index = mock_ast_index_class(cache_path=tmp_path, config=config, base_path=tmp_path)
        
        # Build should not raise (may warn about no files found)
        ast_index.build(source_paths=["nonexistent/"], force=False)

    def test_build_validates_inputs(self, tmp_path, mock_ast_index_class):
        """Test that build() accepts valid inputs."""
        config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
        ast_index = mock_ast_index_class(cache_path=tmp_path, config=config, base_path=tmp_path)
        
        # Should accept these inputs without raising
        ast_index.build(source_paths=["src/", "lib/"], force=True)

    def test_search_requires_built_index(self, tmp_path, mock_ast_index_class):
        """Test that search() raises RuntimeError if index not built (Task 5.5)."""
        config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
        ast_index = mock_ast_index_class(cache_path=tmp_path, config=config, base_path=tmp_path)
        
        # Should raise RuntimeError if index not built
        with pytest.raises(RuntimeError, match="Index not built"):
            ast_index.search(query="test", filters={}, n=5)

    def test_search_validates_query(self, tmp_path, mock_ast_index_class):
        """Test that search() validates query before raising NotImplementedError."""
        config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
        ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
        
        # Empty query should raise ValueError
        with pytest.raises(ValueError, match="Query cannot be empty"):
            ast_index.search(query={}, filters={}, n=5)

    def test_search_validates_n(self, tmp_path, mock_ast_index_class):
        """Test that search() validates n parameter."""
        config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
        ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
        
        query = {"symbol_type": "function"}
        
        # n=0 should raise ValueError
        with pytest.raises(ValueError, match="n must be positive"):
            ast_index.search(query=query, filters={}, n=0)
        
        # n=-1 should raise ValueError
        with pytest.raises(ValueError, match="n must be positive"):
            ast_index.search(query=query, filters={}, n=-1)

    def test_update_raises_not_implemented(self, tmp_path, mock_ast_index_class):
        """Test that update() raises NotImplementedError (stub for Task 5.1)."""
        config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
        ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
        
        with pytest.raises(NotImplementedError, match="Phase 6"):
            ast_index.update(changed_files=["src/auth.py"])

    def test_delete_raises_not_implemented(self, tmp_path, mock_ast_index_class):
        """Test that delete() raises NotImplementedError (stub for Task 5.1)."""
        config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
        ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
        
        with pytest.raises(NotImplementedError, match="Phase 6"):
            ast_index.delete(file_paths=["old/deprecated.py"])


class TestASTIndexDynamicParserLoading:
    """Test suite for dynamic parser loading (Task 5.2)."""

    @pytest.fixture
    def mock_ast_index_class(self):
        """Load ASTIndex class with mocked dependencies."""
        # Load base module first
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        # Load ast_index module
        ast_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "ast_index.py"
        ast_spec = importlib.util.spec_from_file_location("server.indexes.ast_index", ast_index_path)
        ast_module = importlib.util.module_from_spec(ast_spec)
        sys.modules['server.indexes.ast_index'] = ast_module
        
        ast_module.BaseIndex = base_module.BaseIndex
        ast_module.SearchResult = base_module.SearchResult
        
        ast_spec.loader.exec_module(ast_module)
        
        return ast_module.ASTIndex

    def test_load_parsers_returns_dict(self, tmp_path, mock_ast_index_class):
        """Test that _load_parsers() returns a dictionary."""
        # Use a mock to avoid requiring actual parsers
        with patch('importlib.import_module') as mock_import:
            mock_parser = MagicMock()
            mock_import.return_value = mock_parser
            
            config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
            ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
            
            assert isinstance(ast_index.parser_cache, dict)

    def test_load_parsers_follows_naming_convention(self, tmp_path, mock_ast_index_class):
        """Test that _load_parsers() uses tree_sitter_{language} convention."""
        with patch('importlib.import_module') as mock_import:
            mock_parser = MagicMock()
            mock_import.return_value = mock_parser
            
            config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function"}}, "javascript": {"file_extensions": [".js"], "node_types": {"function_declaration": "function"}}}}
            ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
            
            # Should have called import_module for each language
            assert mock_import.call_count == 2
            mock_import.assert_any_call("tree_sitter_python")
            mock_import.assert_any_call("tree_sitter_javascript")

    def test_load_parsers_handles_import_error_gracefully(self, tmp_path, mock_ast_index_class):
        """Test that _load_parsers() continues when parser not installed."""
        def mock_import(module_name):
            if module_name == "tree_sitter_python":
                mock_parser = MagicMock()
                return mock_parser
            elif module_name == "tree_sitter_go":
                raise ImportError(f"No module named '{module_name}'")
            else:
                raise ImportError(f"No module named '{module_name}'")
        
        with patch('importlib.import_module', side_effect=mock_import):
            config = {"languages": ["python", "go"]}
            ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
            
            # Should have loaded python, skipped go
            assert "python" in ast_index.parser_cache
            assert "go" not in ast_index.parser_cache
            assert len(ast_index.parser_cache) == 1

    def test_load_parsers_handles_all_missing_parsers(self, tmp_path, mock_ast_index_class):
        """Test that _load_parsers() handles all parsers missing gracefully."""
        with patch('importlib.import_module', side_effect=ImportError("No parsers")):
            config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function"}}, "javascript": {"file_extensions": [".js"], "node_types": {"function_declaration": "function"}}}}
            ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
            
            # Should have empty parser cache
            assert ast_index.parser_cache == {}

    def test_load_parsers_handles_unexpected_exceptions(self, tmp_path, mock_ast_index_class):
        """Test that _load_parsers() handles non-ImportError exceptions."""
        def mock_import(module_name):
            if module_name == "tree_sitter_python":
                mock_parser = MagicMock()
                return mock_parser
            elif module_name == "tree_sitter_javascript":
                raise RuntimeError("Unexpected error")
            else:
                raise ImportError("Not found")
        
        with patch('importlib.import_module', side_effect=mock_import):
            config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function"}}, "javascript": {"file_extensions": [".js"], "node_types": {"function_declaration": "function"}}}}
            ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
            
            # Should have loaded python, skipped javascript due to runtime error
            assert "python" in ast_index.parser_cache
            assert "javascript" not in ast_index.parser_cache

    def test_load_parsers_stores_in_parser_cache(self, tmp_path, mock_ast_index_class):
        """Test that _load_parsers() stores loaded parsers in parser_cache."""
        mock_python_parser = MagicMock()
        mock_js_parser = MagicMock()
        
        def mock_import(module_name):
            if module_name == "tree_sitter_python":
                return mock_python_parser
            elif module_name == "tree_sitter_javascript":
                return mock_js_parser
            raise ImportError("Not found")
        
        with patch('importlib.import_module', side_effect=mock_import):
            config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function"}}, "javascript": {"file_extensions": [".js"], "node_types": {"function_declaration": "function"}}}}
            ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
            
            # Should have both parsers in cache
            assert ast_index.parser_cache["python"] == mock_python_parser
            assert ast_index.parser_cache["javascript"] == mock_js_parser

    def test_parser_cache_populated_on_init(self, tmp_path, mock_ast_index_class):
        """Test that parser_cache is populated during __init__."""
        with patch('importlib.import_module') as mock_import:
            mock_parser = MagicMock()
            mock_import.return_value = mock_parser
            
            config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
            ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
            
            # Parser cache should be populated (not empty)
            assert len(ast_index.parser_cache) > 0

    def test_load_parsers_logs_success(self, tmp_path, mock_ast_index_class, caplog):
        """Test that _load_parsers() logs successful parser loading."""
        with patch('importlib.import_module') as mock_import:
            mock_parser = MagicMock()
            mock_import.return_value = mock_parser
            
            config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
            with caplog.at_level(logging.INFO):
                ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
            
            # Should log successful loading
            assert any("Loaded Tree-sitter parser for python" in record.message for record in caplog.records)

    def test_load_parsers_logs_warning_on_missing(self, tmp_path, mock_ast_index_class, caplog):
        """Test that _load_parsers() logs warning when parser not installed."""
        with patch('importlib.import_module', side_effect=ImportError("Not found")):
            config = {"languages": {"python": {"file_extensions": [".py"], "node_types": {"function_definition": "function", "class_definition": "class"}}}}
            with caplog.at_level(logging.WARNING):
                ast_index = mock_ast_index_class(cache_path=tmp_path, config=config)
            
            # Should log warning with install instructions
            assert any("Parser for 'python' not installed" in record.message for record in caplog.records)
            assert any("pip install tree-sitter-python" in record.message for record in caplog.records)

