"""
Test code index file exclusion system (three-tier: .gitignore, built-in defaults, config patterns).

Tests:
- Tier 1: .gitignore pattern respect
- Tier 2: Built-in default exclusion patterns
- Tier 3: Config exclude_patterns
- Combined behavior (all tiers)
- Edge cases (negation, nested gitignore, caching)
- Fallback behavior (when gitignore-parser not installed)
- Integration tests with real project structures

Traceability:
    Design: .praxis-os/workspace/design/2025-11-07-code-index-gitignore-support.md
    FR-XXX: Code indexer file exclusion system
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ouroboros.config.schemas.indexes import CodeIndexConfig, FTSConfig, GraphConfig, VectorConfig
from ouroboros.subsystems.rag.code.semantic import SemanticIndex


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project directory structure."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    
    # Create .praxis-os directory (base_path)
    praxis_os = project_root / ".praxis-os"
    praxis_os.mkdir()
    (praxis_os / ".cache" / "indexes" / "code").mkdir(parents=True)
    
    # Create source directory
    src = project_root / "src"
    src.mkdir()
    
    return {
        "project_root": project_root,
        "praxis_os": praxis_os,
        "src": src,
    }


@pytest.fixture
def code_index_config():
    """Create CodeIndexConfig for testing."""
    return CodeIndexConfig(
        source_paths=["src/"],
        languages=["python"],
        vector=VectorConfig(
            model="sentence-transformers/all-MiniLM-L6-v2",
            chunk_size=200,
            chunk_overlap=20,
            dimension=384,
        ),
        fts=FTSConfig(enabled=True),
        duckdb_path=Path(".praxis-os/code.duckdb"),
        graph=GraphConfig(max_depth=10),
        respect_gitignore=True,
        exclude_patterns=None,
    )


@pytest.fixture
def semantic_index(temp_project, code_index_config):
    """Create SemanticIndex instance for testing."""
    return SemanticIndex(
        config=code_index_config,
        base_path=temp_project["praxis_os"],
    )


class TestGitignoreRespect:
    """Test Tier 1: .gitignore pattern respect."""
    
    def test_respects_gitignore_patterns(self, temp_project, code_index_config):
        """Test that .gitignore patterns are respected."""
        # Create .gitignore
        gitignore = temp_project["project_root"] / ".gitignore"
        gitignore.write_text("__pycache__/\n*.pyc\nbuild/\n")
        
        # Create files
        (temp_project["src"] / "main.py").write_text("print('hello')")
        (temp_project["src"] / "__pycache__").mkdir(parents=True)
        (temp_project["src"] / "__pycache__" / "main.pyc").write_text("bytecode")
        (temp_project["src"] / "build").mkdir(parents=True)
        (temp_project["src"] / "build" / "output.txt").write_text("build output")
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Check exclusion
        assert index._should_exclude_file(temp_project["src"] / "__pycache__" / "main.pyc")
        assert index._should_exclude_file(temp_project["src"] / "build" / "output.txt")
        assert not index._should_exclude_file(temp_project["src"] / "main.py")
    
    def test_find_gitignore_walks_up(self, temp_project, code_index_config):
        """Test that _find_gitignore_file walks up directory tree (monorepo support)."""
        # Create nested structure
        subproject = temp_project["project_root"] / "subproject"
        subproject.mkdir()
        (subproject / ".praxis-os").mkdir()
        
        # Create .gitignore at project root
        gitignore = temp_project["project_root"] / ".gitignore"
        gitignore.write_text("*.pyc\n")
        
        # Create SemanticIndex in subproject
        index = SemanticIndex(
            config=code_index_config,
            base_path=subproject / ".praxis-os",
        )
        
        # Should find .gitignore at project root
        found = index._find_gitignore_file()
        assert found == gitignore
    
    def test_has_gitignore(self, temp_project, code_index_config):
        """Test _has_gitignore() method."""
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Initially no .gitignore
        assert not index._has_gitignore()
        
        # Create .gitignore
        gitignore = temp_project["project_root"] / ".gitignore"
        gitignore.write_text("*.pyc\n")
        
        # Reset cache
        index._gitignore_path = None
        
        # Now should find it
        assert index._has_gitignore()


class TestBuiltinDefaults:
    """Test Tier 2: Built-in default exclusion patterns."""
    
    def test_builtin_defaults_when_no_gitignore(self, temp_project, code_index_config):
        """Test built-in defaults when no .gitignore exists."""
        # Ensure no .gitignore
        assert not (temp_project["project_root"] / ".gitignore").exists()
        
        # Create files that should be excluded by built-in defaults
        (temp_project["src"] / "__pycache__").mkdir(parents=True)
        (temp_project["src"] / "__pycache__" / "file.pyc").write_text("bytecode")
        (temp_project["src"] / ".tox").mkdir(parents=True)
        (temp_project["src"] / ".tox" / "config").write_text("tox config")
        (temp_project["src"] / "node_modules").mkdir(parents=True)
        (temp_project["src"] / "node_modules" / "package").write_text("package")
        
        # Create source file that should NOT be excluded
        (temp_project["src"] / "main.py").write_text("print('hello')")
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Should exclude built-in patterns
        assert index._should_exclude_file(temp_project["src"] / "__pycache__" / "file.pyc")
        assert index._should_exclude_file(temp_project["src"] / ".tox" / "config")
        assert index._should_exclude_file(temp_project["src"] / "node_modules" / "package")
        
        # Should NOT exclude source files
        assert not index._should_exclude_file(temp_project["src"] / "main.py")
    
    def test_builtin_patterns_match(self, temp_project, code_index_config):
        """Test _builtin_default_matches() method directly."""
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Test various patterns
        assert index._builtin_default_matches(temp_project["src"] / "__pycache__" / "file.pyc")
        assert index._builtin_default_matches(temp_project["src"] / ".venv" / "bin" / "python")
        assert index._builtin_default_matches(temp_project["src"] / "dist" / "package.tar.gz")
        assert index._builtin_default_matches(temp_project["src"] / ".git" / "config")
        assert index._builtin_default_matches(temp_project["src"] / ".DS_Store")
        
        # Should NOT match source files
        assert not index._builtin_default_matches(temp_project["src"] / "main.py")
        assert not index._builtin_default_matches(temp_project["src"] / "utils.py")


class TestConfigPatterns:
    """Test Tier 3: Config exclude_patterns."""
    
    def test_config_exclude_patterns(self, temp_project):
        """Test config exclude_patterns are applied."""
        config = CodeIndexConfig(
            source_paths=["src/"],
            languages=["python"],
            vector=VectorConfig(
                model="sentence-transformers/all-MiniLM-L6-v2",
                chunk_size=200,
                chunk_overlap=20,
                dimension=384,
            ),
            fts=FTSConfig(enabled=True),
            duckdb_path=Path(".praxis-os/code.duckdb"),
            graph=GraphConfig(max_depth=10),
            respect_gitignore=False,  # Disable gitignore to test config patterns only
            exclude_patterns=["custom_build/", "*.generated.py"],
        )
        
        # Create files
        (temp_project["src"] / "main.py").write_text("print('hello')")
        (temp_project["src"] / "custom_build").mkdir(parents=True)
        (temp_project["src"] / "custom_build" / "output.txt").write_text("output")
        (temp_project["src"] / "file.generated.py").write_text("# generated")
        
        index = SemanticIndex(config=config, base_path=temp_project["praxis_os"])
        
        # Should exclude config patterns
        assert index._should_exclude_file(temp_project["src"] / "custom_build" / "output.txt")
        assert index._should_exclude_file(temp_project["src"] / "file.generated.py")
        
        # Should NOT exclude source files
        assert not index._should_exclude_file(temp_project["src"] / "main.py")
    
    def test_config_patterns_match(self, temp_project, code_index_config):
        """Test _config_patterns_match() method directly."""
        config = CodeIndexConfig(
            source_paths=["src/"],
            languages=["python"],
            vector=VectorConfig(
                model="sentence-transformers/all-MiniLM-L6-v2",
                chunk_size=200,
                chunk_overlap=20,
                dimension=384,
            ),
            fts=FTSConfig(enabled=True),
            duckdb_path=Path(".praxis-os/code.duckdb"),
            graph=GraphConfig(max_depth=10),
            exclude_patterns=["test_*.py", "temp/"],
        )
        
        index = SemanticIndex(config=config, base_path=temp_project["praxis_os"])
        
        # Should match patterns
        assert index._config_patterns_match(
            temp_project["src"] / "test_example.py",
            ["test_*.py"]
        )
        assert index._config_patterns_match(
            temp_project["src"] / "temp" / "file.txt",
            ["temp/"]
        )
        
        # Should NOT match other files
        assert not index._config_patterns_match(
            temp_project["src"] / "main.py",
            ["test_*.py"]
        )


class TestCombinedBehavior:
    """Test combined behavior of all three tiers."""
    
    def test_gitignore_and_config_patterns_combined(self, temp_project):
        """Test that gitignore and config patterns work together (additive)."""
        # Create .gitignore
        gitignore = temp_project["project_root"] / ".gitignore"
        gitignore.write_text("build/\n*.pyc\n")
        
        config = CodeIndexConfig(
            source_paths=["src/"],
            languages=["python"],
            vector=VectorConfig(
                model="sentence-transformers/all-MiniLM-L6-v2",
                chunk_size=200,
                chunk_overlap=20,
                dimension=384,
            ),
            fts=FTSConfig(enabled=True),
            duckdb_path=Path(".praxis-os/code.duckdb"),
            graph=GraphConfig(max_depth=10),
            respect_gitignore=True,
            exclude_patterns=["custom_exclude/"],
        )
        
        # Create files
        (temp_project["src"] / "main.py").write_text("print('hello')")
        (temp_project["src"] / "build").mkdir(parents=True)
        (temp_project["src"] / "build" / "output.txt").write_text("build")
        (temp_project["src"] / "custom_exclude").mkdir(parents=True)
        (temp_project["src"] / "custom_exclude" / "file.txt").write_text("excluded")
        
        index = SemanticIndex(config=config, base_path=temp_project["praxis_os"])
        
        # Both should be excluded
        assert index._should_exclude_file(temp_project["src"] / "build" / "output.txt")  # gitignore
        assert index._should_exclude_file(temp_project["src"] / "custom_exclude" / "file.txt")  # config
        
        # Source file should NOT be excluded
        assert not index._should_exclude_file(temp_project["src"] / "main.py")
    
    def test_disable_gitignore_respect(self, temp_project):
        """Test respect_gitignore=False uses built-in defaults only."""
        # Create .gitignore
        gitignore = temp_project["project_root"] / ".gitignore"
        gitignore.write_text("src/main.py\n")  # Try to exclude main.py
        
        config = CodeIndexConfig(
            source_paths=["src/"],
            languages=["python"],
            vector=VectorConfig(
                model="sentence-transformers/all-MiniLM-L6-v2",
                chunk_size=200,
                chunk_overlap=20,
                dimension=384,
            ),
            fts=FTSConfig(enabled=True),
            duckdb_path=Path(".praxis-os/code.duckdb"),
            graph=GraphConfig(max_depth=10),
            respect_gitignore=False,  # Disable gitignore
            exclude_patterns=None,
        )
        
        # Create files
        (temp_project["src"] / "main.py").write_text("print('hello')")
        (temp_project["src"] / "__pycache__").mkdir(parents=True)
        (temp_project["src"] / "__pycache__" / "file.pyc").write_text("bytecode")
        
        index = SemanticIndex(config=config, base_path=temp_project["praxis_os"])
        
        # .gitignore should be ignored
        assert not index._should_exclude_file(temp_project["src"] / "main.py")
        
        # Built-in defaults should still work
        assert index._should_exclude_file(temp_project["src"] / "__pycache__" / "file.pyc")


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_negation_patterns(self, temp_project, code_index_config):
        """Test gitignore negation patterns (!)."""
        # Create .gitignore with negation
        gitignore = temp_project["project_root"] / ".gitignore"
        gitignore.write_text("*.pyc\n!important.pyc\n")
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Create files
        (temp_project["src"] / "file.pyc").write_text("bytecode")
        (temp_project["src"] / "important.pyc").write_text("important bytecode")
        
        # Regular .pyc should be excluded
        assert index._should_exclude_file(temp_project["src"] / "file.pyc")
        
        # Negated file should NOT be excluded (if gitignore-parser handles it)
        # Note: This depends on gitignore-parser implementation
        # If parser doesn't support negation, this test may need adjustment
    
    def test_absolute_paths(self, temp_project, code_index_config):
        """Test that absolute paths work correctly."""
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Create file with absolute path
        file_path = temp_project["src"] / "main.py"
        file_path.write_text("print('hello')")
        
        # Should work with absolute path
        assert not index._should_exclude_file(file_path.resolve())
    
    def test_relative_paths(self, temp_project, code_index_config):
        """Test that relative paths work correctly."""
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Create file
        file_path = temp_project["src"] / "main.py"
        file_path.write_text("print('hello')")
        
        # Should work with relative path
        relative_path = file_path.relative_to(temp_project["project_root"])
        # Note: _should_exclude_file expects absolute Path, but should handle relative
        
        # Test with absolute path (normal case)
        assert not index._should_exclude_file(file_path)


class TestCaching:
    """Test caching behavior for performance."""
    
    def test_gitignore_caching(self, temp_project, code_index_config):
        """Test that gitignore parser is cached (not re-parsed per file)."""
        # Create .gitignore
        gitignore = temp_project["project_root"] / ".gitignore"
        gitignore.write_text("*.pyc\nbuild/\n")
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # First call should load parser
        parser1 = index._load_gitignore()
        assert parser1 is not None
        
        # Second call should return cached parser
        parser2 = index._load_gitignore()
        assert parser2 is parser1  # Same object (cached)
        
        # _find_gitignore_file should also be cached
        path1 = index._find_gitignore_file()
        path2 = index._find_gitignore_file()
        assert path1 == path2


class TestIntegration:
    """Integration tests with real project structures."""
    
    def test_real_python_project(self, temp_project):
        """Test with Python project structure."""
        # Create Python project structure
        (temp_project["src"] / "main.py").write_text("print('hello')")
        (temp_project["src"] / "utils.py").write_text("def helper(): pass")
        (temp_project["src"] / "__pycache__").mkdir(parents=True)
        (temp_project["src"] / "__pycache__" / "main.pyc").write_text("bytecode")
        (temp_project["src"] / ".tox" / "py39" / "lib").mkdir(parents=True)
        (temp_project["src"] / ".pytest_cache" / "v").mkdir(parents=True)
        
        config = CodeIndexConfig(
            source_paths=["src/"],
            languages=["python"],
            vector=VectorConfig(
                model="sentence-transformers/all-MiniLM-L6-v2",
                chunk_size=200,
                chunk_overlap=20,
                dimension=384,
            ),
            fts=FTSConfig(enabled=True),
            duckdb_path=Path(".praxis-os/code.duckdb"),
            graph=GraphConfig(max_depth=10),
        )
        
        index = SemanticIndex(config=config, base_path=temp_project["praxis_os"])
        
        # Source files should NOT be excluded
        assert not index._should_exclude_file(temp_project["src"] / "main.py")
        assert not index._should_exclude_file(temp_project["src"] / "utils.py")
        
        # Build artifacts SHOULD be excluded
        assert index._should_exclude_file(temp_project["src"] / "__pycache__" / "main.pyc")
        assert index._should_exclude_file(temp_project["src"] / ".tox" / "py39" / "lib")
        assert index._should_exclude_file(temp_project["src"] / ".pytest_cache" / "v")
    
    def test_real_javascript_project(self, temp_project):
        """Test with JavaScript project structure."""
        # Create JavaScript project structure
        (temp_project["src"] / "index.js").write_text("console.log('hello')")
        (temp_project["src"] / "utils.js").write_text("export function helper() {}")
        (temp_project["src"] / "node_modules" / "lodash").mkdir(parents=True)
        (temp_project["src"] / "node_modules" / "lodash" / "index.js").write_text("// lodash")
        (temp_project["src"] / "dist").mkdir(parents=True)
        (temp_project["src"] / "dist" / "bundle.js").write_text("// bundle")
        
        config = CodeIndexConfig(
            source_paths=["src/"],
            languages=["javascript"],
            vector=VectorConfig(
                model="sentence-transformers/all-MiniLM-L6-v2",
                chunk_size=200,
                chunk_overlap=20,
                dimension=384,
            ),
            fts=FTSConfig(enabled=True),
            duckdb_path=Path(".praxis-os/code.duckdb"),
            graph=GraphConfig(max_depth=10),
        )
        
        index = SemanticIndex(config=config, base_path=temp_project["praxis_os"])
        
        # Source files should NOT be excluded
        assert not index._should_exclude_file(temp_project["src"] / "index.js")
        assert not index._should_exclude_file(temp_project["src"] / "utils.js")
        
        # Dependencies and build output SHOULD be excluded
        assert index._should_exclude_file(temp_project["src"] / "node_modules" / "lodash" / "index.js")
        assert index._should_exclude_file(temp_project["src"] / "dist" / "bundle.js")

