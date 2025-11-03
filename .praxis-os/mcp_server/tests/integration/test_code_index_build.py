"""Integration test for CodeIndex build() method.

Phase 4, Task 4.4: Tests for embedding generation and LanceDB storage.

This is a true integration test - no mocks, real file I/O, real embeddings, real LanceDB.
"""

import pytest
from pathlib import Path
import sys
import importlib.util
from unittest.mock import patch, Mock


class TestCodeIndexBuild:
    """Integration tests for CodeIndex build functionality."""

    @pytest.fixture
    def temp_code_dir(self, tmp_path):
        """Create a temporary directory with code files for testing."""
        code_dir = tmp_path / "src"
        code_dir.mkdir()
        
        # Create Python files
        (code_dir / "auth.py").write_text("""
def authenticate(username, password):
    '''Authenticate a user with username and password.'''
    if username == "admin" and password == "secret":
        return True
    return False

class User:
    '''User class for authentication.'''
    def __init__(self, username):
        self.username = username
""")
        
        (code_dir / "utils.py").write_text("""
def calculate_sum(a, b):
    '''Calculate sum of two numbers.'''
    return a + b

def format_string(text):
    '''Format a string.'''
    return text.strip().lower()
""")
        
        # Create JavaScript file
        (code_dir / "app.js").write_text("""
function handleLogin(username, password) {
    // Handle user login
    return fetch('/api/login', {
        method: 'POST',
        body: JSON.stringify({username, password})
    });
}

const formatDate = (date) => {
    return date.toISOString();
};
""")
        
        return code_dir

    def test_build_creates_index(self, tmp_path, temp_code_dir):
        """Test that build() creates a LanceDB index with embeddings."""
        # Load modules
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        code_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "code_index.py"
        code_spec = importlib.util.spec_from_file_location("server.indexes.code_index", code_index_path)
        code_module = importlib.util.module_from_spec(code_spec)
        sys.modules['server.indexes.code_index'] = code_module
        
        code_module.BaseIndex = base_module.BaseIndex
        code_module.SearchResult = base_module.SearchResult
        
        code_spec.loader.exec_module(code_module)
        
        # Create index
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"},
            "chunking": {"code_chunk_size": 500, "code_chunk_overlap": 50}
        }
        
        index = code_module.CodeIndex(cache_path=cache_path, config=config)
        
        # Build index
        index.build(source_paths=[str(temp_code_dir)], force=True)
        
        # Verify table exists and has data
        assert index.table is not None
        row_count = index.table.count_rows()
        assert row_count > 0
        
        # Should have indexed multiple files
        # auth.py, utils.py, app.js = at least 3 chunks
        assert row_count >= 3

    def test_build_stores_correct_schema(self, tmp_path, temp_code_dir):
        """Test that build() stores records with correct schema."""
        # Load modules
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        code_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "code_index.py"
        code_spec = importlib.util.spec_from_file_location("server.indexes.code_index", code_index_path)
        code_module = importlib.util.module_from_spec(code_spec)
        sys.modules['server.indexes.code_index'] = code_module
        
        code_module.BaseIndex = base_module.BaseIndex
        code_module.SearchResult = base_module.SearchResult
        
        code_spec.loader.exec_module(code_module)
        
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"}
        }
        
        index = code_module.CodeIndex(cache_path=cache_path, config=config)
        index.build(source_paths=[str(temp_code_dir)], force=True)
        
        # Get first record
        results = index.table.search([0.0] * 384).limit(1).to_list()
        assert len(results) > 0
        
        record = results[0]
        
        # Verify schema
        assert "chunk_id" in record
        assert "content" in record
        assert "vector" in record
        assert "file_path" in record
        assert "line_start" in record
        assert "line_end" in record
        assert "language" in record
        assert "tokens" in record
        assert "symbols" in record
        
        # Verify types
        assert isinstance(record["chunk_id"], str)
        assert isinstance(record["content"], str)
        assert isinstance(record["vector"], list)
        assert isinstance(record["file_path"], str)
        assert isinstance(record["line_start"], int)
        assert isinstance(record["line_end"], int)
        assert isinstance(record["language"], str)
        assert isinstance(record["tokens"], int)

    def test_build_creates_scalar_index_on_language(self, tmp_path, temp_code_dir):
        """Test that build() creates scalar index on language field."""
        # Load modules
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        code_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "code_index.py"
        code_spec = importlib.util.spec_from_file_location("server.indexes.code_index", code_index_path)
        code_module = importlib.util.module_from_spec(code_spec)
        sys.modules['server.indexes.code_index'] = code_module
        
        code_module.BaseIndex = base_module.BaseIndex
        code_module.SearchResult = base_module.SearchResult
        
        code_spec.loader.exec_module(code_module)
        
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"}
        }
        
        index = code_module.CodeIndex(cache_path=cache_path, config=config)
        index.build(source_paths=[str(temp_code_dir)], force=True)
        
        # Verify we can query using language filter
        # This indirectly verifies the scalar index exists
        query_with_filter = index.table.search([0.0] * 384).where("language = 'python'").limit(5).to_list()
        
        # Should find Python chunks
        assert len(query_with_filter) > 0
        assert all(record["language"] == "python" for record in query_with_filter)

    def test_build_extracts_symbols(self, tmp_path, temp_code_dir):
        """Test that build() extracts and stores symbol names."""
        # Load modules
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        code_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "code_index.py"
        code_spec = importlib.util.spec_from_file_location("server.indexes.code_index", code_index_path)
        code_module = importlib.util.module_from_spec(code_spec)
        sys.modules['server.indexes.code_index'] = code_module
        
        code_module.BaseIndex = base_module.BaseIndex
        code_module.SearchResult = base_module.SearchResult
        
        code_spec.loader.exec_module(code_module)
        
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"}
        }
        
        index = code_module.CodeIndex(cache_path=cache_path, config=config)
        index.build(source_paths=[str(temp_code_dir)], force=True)
        
        # Get all records
        all_records = index.table.search([0.0] * 384).limit(100).to_list()
        
        # Should have extracted some symbols
        symbols_found = [record["symbols"] for record in all_records if record["symbols"]]
        assert len(symbols_found) > 0
        
        # Check for known symbols from our test files
        all_symbols = ",".join(symbols_found)
        assert "authenticate" in all_symbols or "User" in all_symbols or "handleLogin" in all_symbols

    def test_build_handles_multiple_languages(self, tmp_path, temp_code_dir):
        """Test that build() correctly indexes multiple programming languages."""
        # Load modules
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        code_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "code_index.py"
        code_spec = importlib.util.spec_from_file_location("server.indexes.code_index", code_index_path)
        code_module = importlib.util.module_from_spec(code_spec)
        sys.modules['server.indexes.code_index'] = code_module
        
        code_module.BaseIndex = base_module.BaseIndex
        code_module.SearchResult = base_module.SearchResult
        
        code_spec.loader.exec_module(code_module)
        
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"}
        }
        
        index = code_module.CodeIndex(cache_path=cache_path, config=config)
        index.build(source_paths=[str(temp_code_dir)], force=True)
        
        # Get all records
        all_records = index.table.search([0.0] * 384).limit(100).to_list()
        
        # Extract unique languages
        languages = set(record["language"] for record in all_records)
        
        # Should have both Python and JavaScript
        assert "python" in languages
        assert "javascript" in languages

    def test_build_force_rebuild(self, tmp_path, temp_code_dir):
        """Test that build() with force=True rebuilds existing index."""
        # Load modules
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        code_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "code_index.py"
        code_spec = importlib.util.spec_from_file_location("server.indexes.code_index", code_index_path)
        code_module = importlib.util.module_from_spec(code_spec)
        sys.modules['server.indexes.code_index'] = code_module
        
        code_module.BaseIndex = base_module.BaseIndex
        code_module.SearchResult = base_module.SearchResult
        
        code_spec.loader.exec_module(code_module)
        
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"}
        }
        
        index = code_module.CodeIndex(cache_path=cache_path, config=config)
        
        # Build first time
        index.build(source_paths=[str(temp_code_dir)], force=True)
        first_count = index.table.count_rows()
        
        # Build again with force=True
        index.build(source_paths=[str(temp_code_dir)], force=True)
        second_count = index.table.count_rows()
        
        # Should have same count (rebuild)
        assert second_count == first_count


class TestCodeIndexSearch:
    """Integration tests for CodeIndex search functionality."""

    @pytest.fixture
    def temp_code_dir(self, tmp_path):
        """Create a temporary directory with code files for testing."""
        code_dir = tmp_path / "src"
        code_dir.mkdir()
        
        # Create Python files with authentication logic
        (code_dir / "auth.py").write_text("""
def authenticate(username, password):
    '''Authenticate a user with username and password.
    Validates credentials and returns authentication token.'''
    if username == "admin" and password == "secret":
        return generate_token(username)
    return None

def generate_token(username):
    '''Generate authentication token for user.'''
    import hashlib
    return hashlib.sha256(username.encode()).hexdigest()

class User:
    '''User class for authentication system.'''
    def __init__(self, username):
        self.username = username
        self.token = None
    
    def login(self, password):
        '''Login user with password.'''
        self.token = authenticate(self.username, password)
        return self.token is not None
""")
        
        (code_dir / "utils.py").write_text("""
def calculate_sum(a, b):
    '''Calculate sum of two numbers.'''
    return a + b

def format_string(text):
    '''Format a string to lowercase.'''
    return text.strip().lower()

def validate_email(email):
    '''Validate email address format.'''
    return '@' in email and '.' in email
""")
        
        # Create JavaScript file
        (code_dir / "app.js").write_text("""
function handleLogin(username, password) {
    // Handle user login with authentication
    return fetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({username, password})
    }).then(response => response.json());
}

const formatDate = (date) => {
    return date.toISOString();
};
""")
        
        return code_dir

    @pytest.fixture
    def built_index(self, tmp_path, temp_code_dir):
        """Create and build a CodeIndex for testing."""
        # Load modules
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        code_index_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "code_index.py"
        code_spec = importlib.util.spec_from_file_location("server.indexes.code_index", code_index_path)
        code_module = importlib.util.module_from_spec(code_spec)
        sys.modules['server.indexes.code_index'] = code_module
        
        code_module.BaseIndex = base_module.BaseIndex
        code_module.SearchResult = base_module.SearchResult
        
        code_spec.loader.exec_module(code_module)
        
        cache_path = tmp_path / "cache"
        config = {
            "embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"}
        }
        
        index = code_module.CodeIndex(cache_path=cache_path, config=config)
        index.build(source_paths=[str(temp_code_dir)], force=True)
        
        return index

    def test_search_returns_results(self, built_index):
        """Test that search() returns relevant code results."""
        results = built_index.search("authentication token handling", filters={}, n=5)
        
        assert len(results) > 0
        # Verify SearchResult structure
        assert all(hasattr(r, 'content') for r in results)
        assert all(hasattr(r, 'file_path') for r in results)
        assert all(hasattr(r, 'relevance_score') for r in results)
        assert all(hasattr(r, 'line_range') for r in results)
        assert all(hasattr(r, 'metadata') for r in results)
        assert all(hasattr(r, 'content_type') for r in results)

    def test_search_filters_by_language(self, built_index):
        """Test that search() correctly filters by language."""
        # Search only Python files
        python_results = built_index.search(
            "authentication",
            filters={"language": "python"},
            n=10
        )
        
        assert len(python_results) > 0
        assert all(r.metadata["language"] == "python" for r in python_results)
        
        # Search only JavaScript files
        js_results = built_index.search(
            "authentication",
            filters={"language": "javascript"},
            n=10
        )
        
        # Should find JS results (or none if no JS files match)
        if js_results:
            assert all(r.metadata["language"] == "javascript" for r in js_results)

    def test_search_returns_relevant_content(self, built_index):
        """Test that search() returns semantically relevant content."""
        results = built_index.search("user login authentication", filters={}, n=3)
        
        assert len(results) > 0
        
        # Results should mention authentication-related terms
        all_content = " ".join(r.content.lower() for r in results)
        assert any(term in all_content for term in ["authenticate", "login", "user", "password", "token"])

    def test_search_respects_n_limit(self, built_index):
        """Test that search() respects the n parameter."""
        results = built_index.search("code", filters={}, n=2)
        
        assert len(results) <= 2

    def test_search_returns_sorted_by_relevance(self, built_index):
        """Test that search() returns results sorted by relevance."""
        results = built_index.search("authentication", filters={}, n=5)
        
        if len(results) > 1:
            # Relevance scores should be in descending order
            scores = [r.relevance_score for r in results]
            assert scores == sorted(scores, reverse=True)

    def test_search_includes_line_ranges(self, built_index):
        """Test that search() includes line range information."""
        results = built_index.search("authentication", filters={}, n=3)
        
        assert len(results) > 0
        for result in results:
            assert result.line_range is not None
            assert isinstance(result.line_range, tuple)
            assert len(result.line_range) == 2
            assert result.line_range[1] >= result.line_range[0]

    def test_search_includes_metadata(self, built_index):
        """Test that search() includes metadata (language, symbols, tokens)."""
        results = built_index.search("authentication", filters={}, n=3)
        
        assert len(results) > 0
        for result in results:
            assert "language" in result.metadata
            assert "symbols" in result.metadata
            assert "tokens" in result.metadata
            assert isinstance(result.metadata["language"], str)
            assert isinstance(result.metadata["symbols"], list)
            assert isinstance(result.metadata["tokens"], int)

    def test_search_raises_on_empty_query(self, built_index):
        """Test that search() raises ValueError for empty query."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            built_index.search("", filters={}, n=5)

    def test_search_raises_on_invalid_n(self, built_index):
        """Test that search() raises ValueError for invalid n."""
        with pytest.raises(ValueError, match="n must be positive"):
            built_index.search("test", filters={}, n=0)
        
        with pytest.raises(ValueError, match="n must be positive"):
            built_index.search("test", filters={}, n=-1)

    def test_search_content_type_is_code(self, built_index):
        """Test that search() returns results with content_type='code'."""
        results = built_index.search("authentication", filters={}, n=3)
        
        assert len(results) > 0
        assert all(r.content_type == "code" for r in results)

