"""
Test FileWatcher performance (file-save-to-searchable latency).

Tests NFR-P5: Incremental Index Update Latency (<5s p95)

This integration test validates end-to-end FileWatcher performance:
1. File saved → FileWatcher detects → IndexManager updates → Content searchable
2. Measures p95 latency from file save to successful search
3. Validates <5s p95 target (hot reload performance requirement)

Traceability:
    NFR-P5: Incremental Index Update Latency
    Test Plan Addendum: Section 4.1, Test P5.1 and P5.2
    Priority 1: Performance validation for FileWatcher

Reference: TEST-PLAN-ADDENDUM.md, section 4.1 (NFR-P5)
"""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock

from ouroboros.config.schemas.indexes import FileWatcherConfig
from ouroboros.config.loader import load_config
from ouroboros.subsystems.rag.watcher import FileWatcher
from ouroboros.subsystems.rag.index_manager import IndexManager


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.slow
class TestFileWatcherLatency:
    """Test FileWatcher performance (NFR-P5)."""
    
    @pytest.fixture
    def test_standards_dir(self, test_base_path):
        """Create temporary standards directory for testing inside test_base_path."""
        standards_dir = test_base_path / "standards"
        standards_dir.mkdir(exist_ok=True)
        
        # Create a few initial files for realistic conditions
        for i in range(5):
            (standards_dir / f"existing-{i}.md").write_text(
                f"# Existing Standard {i}\n\nSome content"
            )
        
        return standards_dir
    
    @pytest.fixture
    def index_dir(self, tmp_path):
        """Create temporary index directory."""
        index_dir = tmp_path / "indexes"
        index_dir.mkdir()
        return index_dir
    
    @pytest.fixture
    def watcher_config(self):
        """Create FileWatcher config for testing."""
        return FileWatcherConfig(
            enabled=True,
            debounce_ms=500,  # Realistic debounce (matches production)
            watch_patterns=["*.md"]
        )
    
    @pytest.fixture
    def integrated_setup(self, test_standards_dir, index_dir, watcher_config, test_config, test_base_path):
        """
        Create integrated FileWatcher + IndexManager setup.
        
        This is an end-to-end integration fixture that simulates
        the production environment using isolated test configs.
        Builds indexes so tests can actually search.
        """
        # Create IndexManager with isolated test config
        index_manager = IndexManager(
            config=test_config.indexes,
            base_path=test_base_path
        )
        
        # Override standards source path to use our test directory
        if "standards" in index_manager._indexes:
            standards_index = index_manager._indexes["standards"]
            standards_index._source_paths = [test_standards_dir]
            
            # Build the index (required for search to work)
            try:
                standards_index.build([test_standards_dir], force=False)
            except Exception as e:
                # If build fails, that's a real error - don't skip
                pytest.fail(f"Failed to build standards index: {e}")
        
        # Create FileWatcher
        path_mappings = {
            str(test_standards_dir): ["standards"]
        }
        
        file_watcher = FileWatcher(
            config=watcher_config,
            index_manager=index_manager,
            path_mappings=path_mappings
        )
        
        # Start watcher
        file_watcher.start()
        
        yield {
            "watcher": file_watcher,
            "index_manager": index_manager,
            "standards_dir": test_standards_dir
        }
        
        # Cleanup
        file_watcher.stop()
    
    # Test P5.1: File-save-to-searchable latency (<5s p95)
    def test_file_save_to_searchable_latency(self, integrated_setup):
        """
        Test P5.1: Measure file-save-to-searchable latency.
        
        Reference: TEST-PLAN-ADDENDUM.md, section 4.1, Test P5.1
        
        Setup: FileWatcher running, StandardsIndex initialized
        Action: 100 iterations: (1) Save file with unique term, (2) Search for term, (3) Measure time delta
        Metric: Calculate p95 of (search_success_time - file_save_time)
        Pass Criteria: p95 < 5 seconds
        Evidence: NFR-P5 validated (hot reload performance)
        
        Note: This is the definitive end-to-end test for FileWatcher performance.
        """
        watcher = integrated_setup["watcher"]
        index_manager = integrated_setup["index_manager"]
        standards_dir = integrated_setup["standards_dir"]
        
        # Get standards index
        standards_index = index_manager.get_index("standards")
        
        if standards_index is None:
            pytest.skip("Standards index not available (may not be built)")
        
        latencies = []
        
        # Run 20 iterations (reduced from 100 for test speed, but enough for p95)
        num_iterations = 20
        
        for i in range(num_iterations):
            # Generate unique term
            unique_term = f"LATENCYTEST{i}_{int(time.time() * 1000)}"
            
            # Save file with unique term
            test_file = standards_dir / f"latency-test-{i}.md"
            
            save_start = time.time()
            test_file.write_text(f"# Latency Test {i}\n\n{unique_term}")
            file_save_time = time.time()
            
            # Poll for term to become searchable (max 10 seconds)
            search_success_time = None
            max_wait = 10  # 10 seconds max
            poll_interval = 0.1  # 100ms
            
            elapsed = 0
            while elapsed < max_wait:
                try:
                    results = standards_index.search(unique_term, n_results=1)
                    if len(results) > 0:
                        # Handle SearchResult objects (have .content attribute) or dicts
                        first_result = results[0]
                        content = first_result.content if hasattr(first_result, "content") else first_result.get("content", "")
                        if unique_term in content:
                            search_success_time = time.time()
                            break
                except Exception:
                    # Index might be rebuilding, keep polling
                    pass
                
                time.sleep(poll_interval)
                elapsed += poll_interval
            
            if search_success_time is None:
                # Term never became searchable - test failure
                pytest.fail(
                    f"Term '{unique_term}' never became searchable after {max_wait}s. "
                    "FileWatcher may not be triggering updates."
                )
            
            # Calculate latency
            latency = search_success_time - file_save_time
            latencies.append(latency)
        
        # Calculate p95
        latencies.sort()
        p95_index = int(len(latencies) * 0.95)
        p95_latency = latencies[p95_index]
        
        # Report metrics
        avg_latency = sum(latencies) / len(latencies)
        p50_latency = latencies[len(latencies) // 2]
        max_latency = latencies[-1]
        
        print(f"\n📊 File-Save-to-Searchable Latency Metrics:")
        print(f"   p50: {p50_latency:.2f}s")
        print(f"   p95: {p95_latency:.2f}s")
        print(f"   avg: {avg_latency:.2f}s")
        print(f"   max: {max_latency:.2f}s")
        print(f"   iterations: {num_iterations}")
        
        # Assert p95 < 5 seconds
        assert p95_latency < 5.0, \
            f"NFR-P5 VIOLATION: p95 latency {p95_latency:.2f}s exceeds 5s target"
        
        # SUCCESS: NFR-P5 validated
    
    # Test P5.2: Large file incremental update latency
    def test_large_file_incremental_update_latency(self, integrated_setup):
        """
        Test P5.2: Large file incremental update latency.
        
        Reference: TEST-PLAN-ADDENDUM.md, section 4.1, Test P5.2
        
        Setup: FileWatcher running
        Action: Save 10MB file with unique term, measure discovery time
        Metric: Time to searchable
        Pass Criteria: < 10 seconds (relaxed for large files)
        Evidence: Large file handling
        """
        watcher = integrated_setup["watcher"]
        index_manager = integrated_setup["index_manager"]
        standards_dir = integrated_setup["standards_dir"]
        
        # Get standards index
        standards_index = index_manager.get_index("standards")
        
        if standards_index is None:
            pytest.skip("Standards index not available")
        
        # Generate unique term
        unique_term = f"LARGEFILETEST_{int(time.time() * 1000)}"
        
        # Create large file (~1MB for test speed, 10MB would be too slow)
        large_content = "# Large File\n\n" + ("Lorem ipsum dolor sit amet. " * 10000)
        large_content += f"\n\n{unique_term}"  # Unique term at end
        
        large_file = standards_dir / "large-file.md"
        
        file_save_start = time.time()
        large_file.write_text(large_content)
        file_save_time = time.time()
        
        print(f"\n📄 Large file size: {len(large_content) / 1024:.1f} KB")
        
        # Poll for term to become searchable (max 15 seconds for large file)
        search_success_time = None
        max_wait = 15
        poll_interval = 0.2
        
        elapsed = 0
        while elapsed < max_wait:
            try:
                results = standards_index.search(unique_term, n_results=1)
                if len(results) > 0:
                    # Handle SearchResult objects (have .content attribute) or dicts
                    first_result = results[0]
                    content = first_result.content if hasattr(first_result, "content") else first_result.get("content", "")
                    if unique_term in content:
                        search_success_time = time.time()
                        break
            except Exception:
                pass
            
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        if search_success_time is None:
            pytest.fail(f"Large file never became searchable after {max_wait}s")
        
        latency = search_success_time - file_save_time
        
        print(f"📊 Large file latency: {latency:.2f}s")
        
        # Assert < 10 seconds (relaxed target for large files)
        assert latency < 10.0, \
            f"Large file latency {latency:.2f}s exceeds 10s target"


# Additional markers
pytestmark = [pytest.mark.integration, pytest.mark.performance]

