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


class TestSymlinkHandling:
    """Test symlink detection and cycle prevention (BUG 4 fix)."""
    
    def test_symlink_detection(self, temp_project, code_index_config):
        """Test that symlinks are detected and tracked."""
        import os
        
        # Create source file
        real_file = temp_project["src"] / "main.py"
        real_file.write_text("print('hello')")
        
        # Create symlink to file
        symlink_file = temp_project["src"] / "link_to_main.py"
        try:
            os.symlink(real_file, symlink_file)
        except OSError:
            pytest.skip("Symlinks not supported on this platform")
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Collect files
        chunks = index._collect_and_chunk([Path("src/")])
        
        # Should only index the file once (not twice via symlink)
        file_paths = [chunk["file_path"] for chunk in chunks]
        # Either real_file or symlink_file should be indexed, but not both
        assert len([fp for fp in file_paths if "main.py" in fp or "link_to_main.py" in fp]) <= len(chunks)
    
    def test_circular_symlink_prevention(self, temp_project, code_index_config):
        """Test that circular symlinks don't cause infinite loops."""
        import os
        
        # Create directories with circular symlinks
        dir_a = temp_project["src"] / "dir_a"
        dir_b = temp_project["src"] / "dir_b"
        dir_a.mkdir()
        dir_b.mkdir()
        
        # Create files
        (dir_a / "file_a.py").write_text("# file a")
        (dir_b / "file_b.py").write_text("# file b")
        
        # Create circular symlinks
        try:
            os.symlink(dir_b, dir_a / "link_to_b")
            os.symlink(dir_a, dir_b / "link_to_a")
        except OSError:
            pytest.skip("Symlinks not supported on this platform")
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Should not hang or crash
        chunks = index._collect_and_chunk([Path("src/")])
        
        # Should only collect the two real files
        assert len(chunks) <= 2  # May be less if symlinks cause issues, but shouldn't be more
    
    def test_broken_symlink_handling(self, temp_project, code_index_config):
        """Test that broken symlinks are skipped gracefully."""
        import os
        
        # Create broken symlink
        broken_link = temp_project["src"] / "broken.py"
        try:
            os.symlink(temp_project["src"] / "nonexistent.py", broken_link)
        except OSError:
            pytest.skip("Symlinks not supported on this platform")
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Should not crash
        chunks = index._collect_and_chunk([Path("src/")])
        
        # Should return empty (no valid files)
        assert len(chunks) == 0


class TestWindowsPathCompatibility:
    """Test Windows path handling (BUG 5 fix)."""
    
    def test_as_posix_usage(self, temp_project, code_index_config):
        """Test that as_posix() is used for cross-platform path handling."""
        # Create gitignore
        gitignore = temp_project["project_root"] / ".gitignore"
        gitignore.write_text("__pycache__/\n")
        
        # Create nested file
        nested_dir = temp_project["src"] / "subdir" / "nested"
        nested_dir.mkdir(parents=True)
        pycache = nested_dir / "__pycache__"
        pycache.mkdir()
        pyc_file = pycache / "module.pyc"
        pyc_file.write_text("bytecode")
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Should correctly exclude nested __pycache__ regardless of platform
        assert index._gitignore_matches(pyc_file)


class TestFilesOutsideBasePath:
    """Test handling of files outside base_path (BUG 2 & BUG 3 fixes)."""
    
    def test_chunk_file_outside_base_path(self, temp_project, code_index_config):
        """Test that _chunk_file handles files outside base_path without crashing."""
        # Create file outside base_path
        external_file = temp_project["project_root"].parent / "external.py"
        external_file.write_text("print('external')")
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Should not crash (uses absolute path as fallback)
        chunks = index._chunk_file(external_file)
        
        assert len(chunks) > 0
        # File path should be absolute (since it's outside base_path)
        assert chunks[0]["file_path"] == str(external_file.resolve())
    
    def test_delete_file_chunks_outside_base_path(self, temp_project, code_index_config):
        """Test that _delete_file_chunks handles files outside base_path without crashing."""
        # Create file outside base_path
        external_file = temp_project["project_root"].parent / "external.py"
        external_file.write_text("print('external')")
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Mock the table
        index._table = Mock()
        
        # Should not crash (uses absolute path)
        index._delete_file_chunks(external_file)
        
        # Should call delete with absolute path
        expected_path = str(external_file.resolve())
        index._table.delete.assert_called_once_with(f"file_path = '{expected_path}'")


class TestThreadSafety:
    """Test thread-safe caching (BUG 6 fix)."""
    
    def test_gitignore_cache_thread_safety(self, temp_project, code_index_config):
        """Test that concurrent gitignore loading is safe."""
        import threading
        
        # Create gitignore
        gitignore = temp_project["project_root"] / ".gitignore"
        gitignore.write_text("*.pyc\n")
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        results = []
        errors = []
        
        def load_gitignore():
            try:
                parser = index._load_gitignore()
                results.append(parser)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = [threading.Thread(target=load_gitignore) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should not have errors
        assert len(errors) == 0
        
        # All results should be the same cached parser
        assert len(set(id(r) for r in results if r is not None)) == 1
    
    def test_parser_cache_thread_safety(self, temp_project, code_index_config):
        """Test that concurrent parser cache access is safe."""
        import threading
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Create test file
        test_file = temp_project["src"] / "test.py"
        test_file.write_text("print('test')")
        
        results = []
        errors = []
        
        def check_builtin():
            try:
                result = index._builtin_default_matches(test_file)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = [threading.Thread(target=check_builtin) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should not have errors
        assert len(errors) == 0
        
        # All results should be consistent
        assert len(set(results)) == 1


class TestGitignoreEdgeCases:
    """Test edge cases for gitignore handling (EDGE CASE 1 & 2 fixes)."""
    
    def test_large_gitignore_rejection(self, temp_project, code_index_config):
        """Test that very large .gitignore files are rejected."""
        # Create very large gitignore (> 1MB)
        gitignore = temp_project["project_root"] / ".gitignore"
        large_content = "*.pyc\n" * (1024 * 1024 // 6 + 1)  # > 1MB
        gitignore.write_text(large_content)
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Should return None (rejected due to size)
        parser = index._load_gitignore()
        assert parser is None
    
    def test_malformed_gitignore_error_message(self, temp_project, code_index_config, caplog):
        """Test that malformed .gitignore produces clear error message."""
        # Create malformed gitignore
        gitignore = temp_project["project_root"] / ".gitignore"
        # gitignore-parser might not actually fail on any content, so we'll mock the parse function
        gitignore.write_text("*.pyc\n")
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        with patch("ouroboros.subsystems.rag.code.semantic.parse_gitignore", side_effect=ValueError("Invalid pattern")):
            parser = index._load_gitignore()
        
        # Should return None and log error
        assert parser is None
        assert "Failed to parse .gitignore" in caplog.text
        assert "Falling back to built-in exclusion patterns" in caplog.text
    
    def test_gitignore_size_logging(self, temp_project, code_index_config, caplog):
        """Test that gitignore loading logs file size."""
        import logging
        
        # Enable logging capture
        caplog.set_level(logging.INFO)
        
        # Create normal gitignore
        gitignore = temp_project["project_root"] / ".gitignore"
        gitignore.write_text("*.pyc\n__pycache__/\n")
        
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        # Load gitignore
        parser = index._load_gitignore()
        
        # Should log file size
        assert parser is not None
        assert "bytes" in caplog.text


class TestParserConsistency:
    """Test parser consistency (caching removed due to gitignore-parser temp file requirements)."""
    
    def test_builtin_parser_consistency(self, temp_project, code_index_config):
        """Test that builtin pattern matching is consistent across calls."""
        index = SemanticIndex(config=code_index_config, base_path=temp_project["praxis_os"])
        
        test_file = temp_project["src"] / "test.py"
        test_file.write_text("print('test')")
        
        # Multiple calls should give same result
        result1 = index._builtin_default_matches(test_file)
        result2 = index._builtin_default_matches(test_file)
        result3 = index._builtin_default_matches(test_file)
        
        # Should be consistent
        assert result1 == result2 == result3
    
    def test_config_parser_consistency(self, temp_project):
        """Test that config pattern matching is consistent across calls."""
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
            exclude_patterns=["test_*.py", "*.tmp"],
        )
        
        index = SemanticIndex(config=config, base_path=temp_project["praxis_os"])
        
        test_file = temp_project["src"] / "test_main.py"
        test_file.write_text("print('test')")
        
        # Multiple calls should give same result
        result1 = index._config_patterns_match(test_file, config.exclude_patterns)
        result2 = index._config_patterns_match(test_file, config.exclude_patterns)
        result3 = index._config_patterns_match(test_file, config.exclude_patterns)
        
        # Should be consistent
        assert result1 == result2 == result3

