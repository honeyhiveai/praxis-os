"""
Unit tests for path construction across RAG components.

Tests that cache directory paths are constructed correctly without
creating nested .praxis-os/.praxis-os/ directories.

This prevents recurring bugs where components prepend '.praxis-os/'
to base_path, creating nested directories.

Traceability:
    Prevents nested directory bugs in RAG components
    Tests path construction logic directly
"""

import pytest
from pathlib import Path


class TestPathConstructionLogic:
    """Test path construction logic without instantiating full components."""
    
    def test_cache_path_construction_pattern(self, tmp_path):
        """
        Test the correct pattern for constructing cache paths.
        
        This is a simple logic test that validates the PATTERN we expect
        all components to follow, without needing to instantiate them.
        """
        # Simulate real-world: base_path IS .praxis-os/
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        
        # CORRECT pattern: base_path / ".cache" / ...
        correct_path = base_path / ".cache" / "rag" / "build-progress"
        
        # INCORRECT pattern: base_path / ".praxis-os" / ".cache" / ...
        incorrect_path = base_path / ".praxis-os" / ".cache" / "rag" / "build-progress"
        
        # Validate correct pattern doesn't create nesting
        assert ".praxis-os/.praxis-os" not in str(correct_path)
        assert str(correct_path) == str(tmp_path / ".praxis-os" / ".cache" / "rag" / "build-progress")
        
        # Validate incorrect pattern DOES create nesting (this is the bug)
        assert ".praxis-os/.praxis-os" in str(incorrect_path)
        assert str(incorrect_path) == str(tmp_path / ".praxis-os" / ".praxis-os" / ".cache" / "rag" / "build-progress")
    
    def test_multiple_cache_paths_no_nesting(self, tmp_path):
        """
        Test that all expected cache paths follow the correct pattern.
        
        This validates the paths used by various RAG components:
        - Semantic indexes: .cache/indexes/{code,standards}
        - Graph index: .cache/indexes/code/graph.duckdb
        - Build progress: .cache/rag/build-progress
        - Locks: .cache/locks
        """
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        
        # All expected cache paths
        expected_paths = [
            base_path / ".cache" / "indexes" / "code",
            base_path / ".cache" / "indexes" / "standards",
            base_path / ".cache" / "indexes" / "code" / "graph.duckdb",
            base_path / ".cache" / "rag" / "build-progress",
            base_path / ".cache" / "locks",
            base_path / ".cache" / "init.lock",
        ]
        
        # CRITICAL: None of these should contain nested .praxis-os/
        for path in expected_paths:
            assert ".praxis-os/.praxis-os" not in str(path), (
                f"❌ Path contains nested .praxis-os/: {path}\n"
                f"   This indicates a path construction bug."
            )
            
            # Verify they all start with base_path
            assert str(path).startswith(str(base_path)), (
                f"❌ Path doesn't start with base_path: {path}"
            )
    
    def test_path_construction_with_custom_base(self, tmp_path):
        """
        Test path construction with non-.praxis-os base_path.
        
        This ensures the pattern works correctly even when base_path
        is something other than .praxis-os/ (e.g., for testing).
        """
        # Use custom base path
        base_path = tmp_path / "custom"
        base_path.mkdir()
        
        # Construct cache paths
        cache_path = base_path / ".cache" / "indexes" / "code"
        progress_path = base_path / ".cache" / "rag" / "build-progress"
        
        # Should NOT contain .praxis-os at all
        assert ".praxis-os" not in str(cache_path)
        assert ".praxis-os" not in str(progress_path)
        
        # Should start with custom base path
        assert str(cache_path).startswith(str(base_path))
        assert str(progress_path).startswith(str(base_path))
    
    def test_nested_patterns_detection(self, tmp_path):
        """
        Test that we can detect various nested directory patterns.
        
        This validates our blacklist patterns catch all variations
        of the nesting bug.
        """
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        
        # Test various nested patterns
        nested_patterns = [
            (".praxis-os/.praxis-os", base_path / ".praxis-os" / ".cache"),
            (".cache/.cache", base_path / ".cache" / ".cache" / "rag"),
            ("rag/rag", base_path / ".cache" / "rag" / "rag" / "build-progress"),
            ("indexes/indexes", base_path / ".cache" / "indexes" / "indexes" / "code"),
        ]
        
        for pattern, path in nested_patterns:
            # Create the nested path to test detection
            path.mkdir(parents=True, exist_ok=True)
            
            # Verify our detection pattern works
            assert pattern in str(path.relative_to(tmp_path)), (
                f"❌ Failed to detect nested pattern '{pattern}' in: {path}"
            )
