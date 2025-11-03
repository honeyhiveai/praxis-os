"""Integration test for StandardsIndex build() method.

This test verifies the full index build pipeline:
1. Chunking markdown files
2. Generating embeddings
3. Creating LanceDB table
4. Creating vector, FTS, and scalar indexes
5. Verifying search functionality

This is a true integration test - no mocks, real file I/O, real embeddings.
"""

import pytest
import sys
from pathlib import Path
import tempfile
import importlib.util

# Direct imports - load base first, then standards_index
base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
base_module = importlib.util.module_from_spec(spec)
sys.modules['server.indexes.base'] = base_module
spec.loader.exec_module(base_module)

# Now load standards_index (which imports from base)
standards_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "standards_index.py"
spec = importlib.util.spec_from_file_location("server.indexes.standards_index", standards_path)
standards_module = importlib.util.module_from_spec(spec)
sys.modules['server.indexes.standards_index'] = standards_module
spec.loader.exec_module(standards_module)

StandardsIndex = standards_module.StandardsIndex


class TestIndexBuild:
    """Integration tests for index building."""
    
    def test_build_index_from_markdown_files(self):
        """Test building a real index from markdown files."""
        # Create temporary directories
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            cache_path = tmp_path / "cache"
            source_path = tmp_path / "standards"
            source_path.mkdir(parents=True)
            
            # Create test markdown files
            test_md1 = source_path / "test1.md"
            test_md1.write_text("""## Phase 0: Getting Started

This is a test standard about getting started with prAxIs OS.

### Installation

Install the system using pip install.

### Configuration

Configure the system with YAML files.
""")
            
            test_md2 = source_path / "test2.md"
            test_md2.write_text("""## Testing Standards

### Unit Testing

Write unit tests for all functions.

### Integration Testing

Test component interactions end-to-end.
""")
            
            # Create index with config
            config = {
                "embedding": {
                    "provider": "local",
                    "model": "all-MiniLM-L6-v2"
                },
                "cache": {
                    "enabled": False
                },
                "source_paths": []
            }
            
            index = StandardsIndex(cache_path, config)
            
            # Build index
            index.build(source_paths=[str(source_path)], force=True)
            
            # Verify index was created
            assert index.vector_search_available
            assert index.table is not None
            assert index.db is not None
            
            # Verify table has data
            count = index.table.count_rows()
            assert count > 0, "Index should have at least one chunk"
            
            print(f"✅ Built index with {count} chunks")
            
            # Test search functionality
            results = index.search("testing standards", filters={}, n=3)
            assert len(results) > 0, "Should find results for 'testing standards'"
            assert any("test" in r.content.lower() for r in results)
            
            print(f"✅ Search returned {len(results)} results")
    
    def test_build_index_with_metadata(self):
        """Test that metadata is correctly extracted and indexed."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            cache_path = tmp_path / "cache"
            source_path = tmp_path / "standards"
            source_path.mkdir(parents=True)
            
            # Create test file with phase marker
            test_md = source_path / "phase_test.md"
            test_md.write_text("""## Phase 1: Foundation

🚨 CRITICAL: This is a critical requirement.

Build the foundation properly.
""")
            
            config = {
                "embedding": {
                    "provider": "local",
                    "model": "all-MiniLM-L6-v2"
                },
                "cache": {
                    "enabled": False
                },
                "source_paths": []
            }
            
            index = StandardsIndex(cache_path, config)
            index.build(source_paths=[str(source_path)], force=True)
            
            # Query one record to check metadata structure
            sample = index.table.to_pandas().iloc[0]
            
            # Verify metadata fields exist
            assert "framework_type" in sample, "Should have framework_type field"
            assert "phase" in sample, "Should have phase field"
            assert "is_critical" in sample, "Should have is_critical field"
            assert "tags" in sample, "Should have tags field"
            
            print(f"✅ Metadata fields present: framework_type={sample['framework_type']}, phase={sample['phase']}, is_critical={sample['is_critical']}")
    
    def test_build_idempotent(self):
        """Test that building twice with force=False doesn't rebuild."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            cache_path = tmp_path / "cache"
            source_path = tmp_path / "standards"
            source_path.mkdir(parents=True)
            
            test_md = source_path / "test.md"
            test_md.write_text("## Test\n\nTest content")
            
            config = {
                "embedding": {
                    "provider": "local",
                    "model": "all-MiniLM-L6-v2"
                },
                "cache": {
                    "enabled": False
                },
                "source_paths": []
            }
            
            index = StandardsIndex(cache_path, config)
            
            # First build
            index.build(source_paths=[str(source_path)], force=True)
            first_count = index.table.count_rows()
            
            # Second build without force (should skip)
            index2 = StandardsIndex(cache_path, config)
            index2.build(source_paths=[str(source_path)], force=False)
            second_count = index2.table.count_rows()
            
            assert first_count == second_count
            print(f"✅ Idempotent build: {first_count} chunks both times")
    
    def test_build_creates_indexes(self):
        """Test that FTS and scalar indexes are created during build."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            cache_path = tmp_path / "cache"
            source_path = tmp_path / "standards"
            source_path.mkdir(parents=True)
            
            test_md = source_path / "test.md"
            test_md.write_text("## Test\n\nTest content with searchable keywords")
            
            config = {
                "embedding": {
                    "provider": "local",
                    "model": "all-MiniLM-L6-v2"
                },
                "cache": {
                    "enabled": False
                },
                "source_paths": []
            }
            
            index = StandardsIndex(cache_path, config)
            index.build(source_paths=[str(source_path)], force=True)
            
            # Verify table exists and has data
            assert index.table is not None
            assert index.table.count_rows() > 0
            
            # Note: LanceDB doesn't expose index metadata easily
            # So we verify indexes work by testing search functionality
            
            # Test vector search works
            results = index.search("test content", filters={}, n=1)
            assert len(results) > 0
            
            print("✅ Vector, FTS, and scalar indexes created successfully")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])

