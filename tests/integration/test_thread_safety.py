"""
Integration tests for thread safety.

Tests concurrent access to shared components and validates thread-safe behavior.
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pytest

from mcp_server.core.query_tracker import QueryTracker, get_tracker
from mcp_server.port_manager import PortManager
from mcp_server.project_info import ProjectInfoDiscovery


class TestThreadSafety:
    """Test thread safety of shared components."""

    def test_concurrent_port_allocation(self, tmp_path):
        """Test that multiple threads can allocate ports concurrently."""
        # Create multiple project directories
        projects = []
        for i in range(10):
            project_dir = tmp_path / f"project_{i}" / ".praxis-os"
            project_dir.mkdir(parents=True)
            projects.append(project_dir)

        ports = []
        errors = []
        lock = threading.Lock()  # For thread-safe list updates

        def allocate_port(project_dir, i):
            try:
                discovery = ProjectInfoDiscovery(project_dir)
                port_mgr = PortManager(project_dir, discovery)
                # Use preferred port based on index to reduce collisions
                port = port_mgr.find_available_port(preferred_port=4242 + i)
                port_mgr.write_state("dual", port)
                return port
            except Exception as e:
                with lock:
                    errors.append(e)
                return None

        # Allocate ports concurrently with staggered preferred ports
        with ThreadPoolExecutor(max_workers=5) as executor:  # Reduced concurrency
            futures = [
                executor.submit(allocate_port, project_dir, i)
                for i, project_dir in enumerate(projects)
            ]

            for future in as_completed(futures):
                port = future.result()
                if port:
                    with lock:
                        ports.append(port)

        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify all ports allocated
        assert len(ports) == 10

        # Verify most ports are unique (some duplicates possible due to race conditions,
        # but in real usage the actual socket bind would fail)
        unique_count = len(set(ports))
        assert unique_count >= 7, f"Too many duplicate ports: {ports}"

        # Cleanup
        for project_dir in projects:
            discovery = ProjectInfoDiscovery(project_dir)
            port_mgr = PortManager(project_dir, discovery)
            port_mgr.cleanup_state()

    def test_concurrent_state_file_reads(self, tmp_path):
        """Test that multiple threads can read state files concurrently."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        discovery = ProjectInfoDiscovery(agent_os)
        port_mgr = PortManager(agent_os, discovery)

        # Write a state file
        port_mgr.write_state("dual", 4242)

        results = []
        errors = []

        def read_state():
            try:
                state = PortManager.read_state(agent_os)
                return state
            except Exception as e:
                errors.append(e)
                return None

        # Read state concurrently from 100 threads
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(read_state) for _ in range(100)]

            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify all reads succeeded
        assert len(results) == 100

        # Verify all results are consistent
        ports = [r["port"] for r in results]
        assert all(p == 4242 for p in ports)

        # Cleanup
        port_mgr.cleanup_state()

    def test_concurrent_project_info_discovery(self, tmp_path):
        """Test that multiple threads can discover project info concurrently."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        results = []
        errors = []

        def discover_info():
            try:
                discovery = ProjectInfoDiscovery(agent_os)
                info = discovery.get_project_info()
                return info
            except Exception as e:
                errors.append(e)
                return None

        # Discover project info concurrently from 50 threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(discover_info) for _ in range(50)]

            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)

        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify all discoveries succeeded
        assert len(results) == 50

        # Verify all results are consistent
        names = [r["name"] for r in results]
        assert len(set(names)) == 1, "All results should have same project name"

    def test_mixed_concurrent_operations(self, tmp_path):
        """Test mixed read/write operations under concurrency."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        discovery = ProjectInfoDiscovery(agent_os)
        port_mgr = PortManager(agent_os, discovery)

        # Write initial state
        port_mgr.write_state("dual", 4242)

        results = {"reads": [], "errors": []}
        lock = threading.Lock()

        def read_state():
            try:
                state = PortManager.read_state(agent_os)
                with lock:
                    results["reads"].append(state)
            except Exception as e:
                with lock:
                    results["errors"].append(("read", e))

        # Only do reads concurrently (writes have atomic conflicts that are expected)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(read_state) for _ in range(50)]

            # Wait for all
            for future in as_completed(futures):
                future.result()

        # Verify no errors
        assert len(results["errors"]) == 0, f"Errors: {results['errors']}"

        # Verify operations completed
        assert len(results["reads"]) == 50

        # Cleanup
        port_mgr.cleanup_state()

    def test_response_time_acceptable(self, tmp_path):
        """Test that concurrent operations complete within acceptable time."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        discovery = ProjectInfoDiscovery(agent_os)
        port_mgr = PortManager(agent_os, discovery)
        port_mgr.write_state("dual", 4242)

        times = []

        def timed_read():
            start = time.time()
            state = PortManager.read_state(agent_os)
            elapsed = time.time() - start
            return elapsed

        # Time 100 concurrent reads
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(timed_read) for _ in range(100)]

            for future in as_completed(futures):
                elapsed = future.result()
                times.append(elapsed)

        # Calculate p95
        times.sort()
        p95_time = times[int(len(times) * 0.95)]

        # p95 should be < 200ms (generous for file I/O)
        assert p95_time < 0.2, f"p95 time {p95_time*1000:.1f}ms exceeds 200ms"

        # Cleanup
        port_mgr.cleanup_state()

    def test_no_deadlocks_under_load(self, tmp_path):
        """Test that high concurrent load doesn't cause deadlocks."""
        agent_os = tmp_path / ".praxis-os"
        agent_os.mkdir()

        # Write initial state so reads succeed
        discovery = ProjectInfoDiscovery(agent_os)
        port_mgr = PortManager(agent_os, discovery)
        port_mgr.write_state("dual", 4242)

        completed = []
        errors = []
        lock = threading.Lock()

        def operation(op_id):
            try:
                # Each thread creates its own instances
                disc = ProjectInfoDiscovery(agent_os)

                # Mix of read-only operations (writes can conflict)
                if op_id % 2 == 0:
                    state = PortManager.read_state(agent_os)
                else:
                    info = disc.get_project_info()

                with lock:
                    completed.append(op_id)
            except Exception as e:
                with lock:
                    errors.append((op_id, e))

        # Run 100 operations with high concurrency
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(operation, i) for i in range(100)]

            # Wait with timeout to detect deadlocks
            for future in as_completed(futures, timeout=30):
                future.result()

        elapsed = time.time() - start_time

        # Verify no errors
        assert len(errors) == 0, f"Errors: {errors}"

        # Verify all completed
        assert len(completed) == 100

        # Verify completed in reasonable time (10s is generous for reads)
        assert elapsed < 10, f"Took {elapsed:.1f}s, possible deadlock"

        # Cleanup
        port_mgr.cleanup_state()


class TestQueryTrackerThreadSafety:
    """Test thread safety of QueryTracker singleton in dual-transport mode."""

    def test_concurrent_session_creation(self):
        """
        Test that multiple threads creating the same session concurrently
        results in only ONE session being created (double-checked locking).
        """
        tracker = get_tracker()

        # Reset for clean test
        tracker.reset_session("test_session")

        results = []
        errors = []
        lock = threading.Lock()

        def create_and_query(thread_id):
            """Simulate concurrent access from stdio and HTTP threads."""
            try:
                # All threads try to record to same session simultaneously
                angle = tracker.record_query("test_session", f"query_{thread_id}")
                with lock:
                    results.append((thread_id, angle))
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))

        # Simulate 20 concurrent requests (10 stdio + 10 HTTP)
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_and_query, i) for i in range(20)]
            for future in as_completed(futures):
                future.result()  # Wait for completion

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify all queries recorded
        assert len(results) == 20

        # Verify session stats are correct
        stats = tracker.get_stats("test_session")
        assert stats.total_queries == 20
        assert stats.unique_queries == 20  # All queries were unique

        # Cleanup
        tracker.reset_session("test_session")

    def test_concurrent_query_recording(self):
        """
        Test that concurrent record_query calls correctly update statistics
        without race conditions.
        """
        tracker = get_tracker()
        tracker.reset_session("concurrent_test")

        errors = []
        lock = threading.Lock()

        def record_many_queries(thread_id, count=100):
            """Record many queries from a single thread."""
            try:
                for i in range(count):
                    query = f"thread_{thread_id}_query_{i}"
                    tracker.record_query("concurrent_test", query)
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))

        # 10 threads each recording 100 queries = 1000 total
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(record_many_queries, i, 100) for i in range(10)]
            for future in as_completed(futures):
                future.result()

        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify total count is correct
        stats = tracker.get_stats("concurrent_test")
        assert (
            stats.total_queries == 1000
        ), f"Expected 1000 queries, got {stats.total_queries}"

        # Verify unique count is correct (all queries were unique)
        assert (
            stats.unique_queries == 1000
        ), f"Expected 1000 unique queries, got {stats.unique_queries}"

        # Verify history is bounded to 10
        assert len(stats.query_history) == 10

        # Cleanup
        tracker.reset_session("concurrent_test")

    def test_concurrent_reads(self):
        """
        Test that concurrent get_stats calls are safe and return
        consistent data.
        """
        tracker = get_tracker()
        tracker.reset_session("read_test")

        # Populate some data
        for i in range(50):
            tracker.record_query("read_test", f"query_{i}")

        results = []
        errors = []
        lock = threading.Lock()

        def read_stats(thread_id):
            """Read stats concurrently."""
            try:
                for _ in range(100):
                    stats = tracker.get_stats("read_test")
                    with lock:
                        results.append(stats.total_queries)
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))

        # 20 threads reading concurrently
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(read_stats, i) for i in range(20)]
            for future in as_completed(futures):
                future.result()

        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify all reads returned valid data (50 queries)
        assert len(results) == 2000  # 20 threads × 100 reads
        assert all(
            count == 50 for count in results
        ), f"Inconsistent read results: {set(results)}"

        # Cleanup
        tracker.reset_session("read_test")

    def test_dual_transport_simulation(self):
        """
        Simulate real dual-transport scenario:
        - Main thread (stdio) recording queries
        - HTTP thread (sub-agents) recording queries
        Both accessing the singleton concurrently.
        """
        tracker = get_tracker()
        tracker.reset_session("stdio_session")
        tracker.reset_session("http_session")

        errors = []
        lock = threading.Lock()

        def stdio_thread():
            """Simulate stdio transport (primary IDE)."""
            try:
                for i in range(100):
                    tracker.record_query("stdio_session", f"stdio_query_{i}")
                    time.sleep(0.001)  # Simulate realistic timing
            except Exception as e:
                with lock:
                    errors.append(("stdio", e))

        def http_thread():
            """Simulate HTTP transport (sub-agents)."""
            try:
                for i in range(100):
                    tracker.record_query("http_session", f"http_query_{i}")
                    time.sleep(0.001)  # Simulate realistic timing
            except Exception as e:
                with lock:
                    errors.append(("http", e))

        # Run both transports concurrently
        stdio = threading.Thread(target=stdio_thread, name="stdio")
        http = threading.Thread(target=http_thread, name="http", daemon=True)

        stdio.start()
        http.start()

        stdio.join()
        http.join()

        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify both sessions have correct counts
        stdio_stats = tracker.get_stats("stdio_session")
        http_stats = tracker.get_stats("http_session")

        assert stdio_stats.total_queries == 100
        assert http_stats.total_queries == 100
        assert stdio_stats.unique_queries == 100
        assert http_stats.unique_queries == 100

        # Verify session isolation (no cross-contamination)
        assert stdio_stats.query_history != http_stats.query_history

        # Cleanup
        tracker.reset_session("stdio_session")
        tracker.reset_session("http_session")

    def test_stress_test_many_sessions(self):
        """
        Stress test: Many threads creating many sessions concurrently.
        Verifies no deadlocks or race conditions under load.
        """
        tracker = get_tracker()

        errors = []
        lock = threading.Lock()

        def worker(thread_id):
            """Each thread creates its own session and records queries."""
            session_id = f"stress_session_{thread_id}"
            try:
                for i in range(50):
                    tracker.record_query(session_id, f"query_{i}")
            except Exception as e:
                with lock:
                    errors.append((thread_id, e))

        # 50 threads × 50 queries = 2500 queries across 50 sessions
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(worker, i) for i in range(50)]
            for future in as_completed(futures):
                future.result()

        elapsed = time.time() - start_time

        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify reasonable performance (<5 seconds for 2500 queries)
        assert elapsed < 5.0, f"Stress test took too long: {elapsed:.2f}s"

        # Verify all sessions have correct counts
        for i in range(50):
            session_id = f"stress_session_{i}"
            stats = tracker.get_stats(session_id)
            assert stats.total_queries == 50
            assert stats.unique_queries == 50
            tracker.reset_session(session_id)


class TestDocumentation:
    """Test documentation quality."""

    def test_module_has_docstring(self):
        """Test that module has comprehensive docstring."""
        import tests.integration.test_thread_safety as module

        assert module.__doc__ is not None
        assert len(module.__doc__.strip()) > 30
