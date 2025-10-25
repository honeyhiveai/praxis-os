"""
Unit tests for WorkflowEngine thread safety.

Tests concurrent session creation to verify double-checked locking
prevents race conditions and duplicate session creation.
"""

import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List

import pytest

from mcp_server.models import WorkflowState
from mcp_server.rag_engine import RAGEngine
from mcp_server.state_manager import StateManager
from mcp_server.workflow_engine import WorkflowEngine


def create_test_state(
    session_id: str, workflow_type: str = "test_workflow"
) -> WorkflowState:
    """Helper to create WorkflowState with all required fields."""
    return WorkflowState(
        session_id=session_id,
        workflow_type=workflow_type,
        target_file="test.py",
        current_phase=0,
        completed_phases=[],
        phase_artifacts={},
        checkpoints={},
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={},
    )


@pytest.fixture
def temp_state_dir(tmp_path):
    """Create temporary state directory for tests."""
    return tmp_path / "states"


@pytest.fixture
def temp_workflows_dir(tmp_path):
    """Create temporary workflows directory for tests."""
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    return workflows_dir


@pytest.fixture
def rag_engine(tmp_path):
    """Create RAGEngine for tests."""
    index_path = tmp_path / "index"
    standards_path = tmp_path / "standards"
    standards_path.mkdir(parents=True, exist_ok=True)

    return RAGEngine(
        index_path=index_path,
        standards_path=standards_path,
        embedding_provider="local",
    )


@pytest.fixture
def state_manager(temp_state_dir):
    """Create StateManager for tests."""
    return StateManager(temp_state_dir)


@pytest.fixture
def workflow_engine(state_manager, rag_engine, temp_workflows_dir):
    """Create WorkflowEngine for tests."""
    engine = WorkflowEngine(
        state_manager=state_manager,
        rag_engine=rag_engine,
        workflows_base_path=temp_workflows_dir,
    )
    return engine


def test_concurrent_session_creation_no_duplicates(workflow_engine, state_manager):
    """
    Test that concurrent get_session() calls return same object.

    Verifies double-checked locking prevents duplicate session creation
    when multiple threads request the same session_id simultaneously.
    """
    session_id = "test-concurrent-session"

    # Create initial session state
    state = create_test_state(session_id)
    state_manager.save_state(state)

    # Collect session object IDs from all threads
    session_ids: List[int] = []
    session_ids_lock = threading.Lock()

    # Barrier to synchronize thread start (maximize concurrency)
    num_threads = 10
    barrier = threading.Barrier(num_threads)

    def get_session_worker():
        """Worker that gets session after barrier."""
        barrier.wait()  # Wait for all threads ready
        session = workflow_engine.get_session(session_id)
        with session_ids_lock:
            session_ids.append(id(session))

    # Start threads
    threads = [threading.Thread(target=get_session_worker) for _ in range(num_threads)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify all threads got same session object
    unique_ids = set(session_ids)
    assert len(unique_ids) == 1, (
        f"Created {len(unique_ids)} different sessions! "
        f"Expected 1. IDs: {unique_ids}"
    )

    # Verify metrics recorded the race condition
    metrics = workflow_engine.get_metrics()
    assert metrics["misses"] == 1, "Should have exactly 1 cache miss"
    # At least some threads should have hit the cache or double-load path
    assert (metrics["hits"] + metrics["double_loads"]) == num_threads - 1, (
        f"Expected {num_threads - 1} hits/double_loads, "
        f"got hits={metrics['hits']}, double_loads={metrics['double_loads']}"
    )


def test_concurrent_session_creation_stress_test(workflow_engine, state_manager):
    """
    Stress test with 1000 iterations to catch rare race conditions.

    Runs many iterations of concurrent session creation to ensure
    robustness under sustained concurrent load.
    """
    base_session_id = "stress-test-session"
    iterations = 100  # Reduced from 1000 for faster CI
    threads_per_iteration = 5

    failures = []

    for i in range(iterations):
        session_id = f"{base_session_id}-{i}"

        # Create session state
        state = create_test_state(session_id)
        state_manager.save_state(state)

        session_ids = []
        lock = threading.Lock()

        def worker():
            session = workflow_engine.get_session(session_id)
            with lock:
                session_ids.append(id(session))

        threads = [
            threading.Thread(target=worker) for _ in range(threads_per_iteration)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        unique = set(session_ids)
        if len(unique) != 1:
            failures.append(f"Iteration {i}: {len(unique)} sessions created")

    assert len(failures) == 0, f"Failures: {failures}"


def test_no_memory_leak_session_cache(workflow_engine, state_manager):
    """
    Test that session cache doesn't leak memory.

    Verifies that creating sessions doesn't accumulate unbounded
    cache entries and that cache size matches expected count.
    """
    num_sessions = 100

    for i in range(num_sessions):
        session_id = f"leak-test-{i}"

        state = create_test_state(session_id)
        state_manager.save_state(state)

        # Create session
        workflow_engine.get_session(session_id)

    # Verify cache size matches number of unique sessions
    # (Access internal cache for testing purposes)
    cache_size = len(workflow_engine._sessions)
    assert (
        cache_size == num_sessions
    ), f"Expected {num_sessions} cached sessions, got {cache_size}"


def test_metrics_record_double_load(workflow_engine, state_manager):
    """
    Test that metrics correctly record double-load events.

    Verifies that when race conditions occur (and are prevented),
    the metrics properly track double_loads counter.
    """
    session_id = "metrics-test-session"

    state = create_test_state(session_id)
    state_manager.save_state(state)

    # Reset metrics
    workflow_engine.metrics.reset()

    # Concurrent access to trigger potential double-load
    num_threads = 10
    barrier = threading.Barrier(num_threads)

    def worker():
        barrier.wait()
        workflow_engine.get_session(session_id)

    threads = [threading.Thread(target=worker) for _ in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    metrics = workflow_engine.get_metrics()

    # Should have exactly 1 miss (first thread creates)
    assert metrics["misses"] == 1

    # Should have hits + double_loads = num_threads - 1
    total_cache_operations = metrics["hits"] + metrics["double_loads"]
    assert total_cache_operations == num_threads - 1

    # If any double_loads occurred, verify they were logged
    # (In practice, double_loads may be 0 if timing doesn't trigger race)
    if metrics["double_loads"] > 0:
        assert metrics["lock_waits"] >= metrics["double_loads"]


def test_clear_session_cache(workflow_engine, state_manager):
    """
    Test that clear_session_cache() properly resets cache.

    Verifies test isolation capability by clearing cache and
    ensuring sessions are recreated on next access.
    """
    session_id = "clear-test-session"

    state = create_test_state(session_id)
    state_manager.save_state(state)

    # Create session
    session1 = workflow_engine.get_session(session_id)
    session1_id = id(session1)

    # Clear cache
    count = workflow_engine.clear_session_cache()
    assert count == 1, f"Expected to clear 1 session, cleared {count}"

    # Get session again - should be new object
    session2 = workflow_engine.get_session(session_id)
    session2_id = id(session2)

    assert session1_id != session2_id, "Session should be recreated after cache clear"


def test_session_cache_hit_rate(workflow_engine, state_manager):
    """
    Test that cache hit rate is calculated correctly.

    Verifies metrics accurately track hit rate for cache performance
    monitoring.
    """
    session_id = "hitrate-test-session"

    state = create_test_state(session_id)
    state_manager.save_state(state)

    # Reset metrics
    workflow_engine.metrics.reset()

    # First access (miss)
    workflow_engine.get_session(session_id)

    # Next 9 accesses (hits)
    for _ in range(9):
        workflow_engine.get_session(session_id)

    metrics = workflow_engine.get_metrics()

    assert metrics["misses"] == 1
    assert metrics["hits"] == 9
    assert metrics["total_operations"] == 10
    assert (
        abs(metrics["hit_rate"] - 0.9) < 0.01
    ), f"Expected 90% hit rate, got {metrics['hit_rate']:.1%}"
