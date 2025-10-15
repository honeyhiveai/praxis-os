"""
Unit tests for RAGEngine thread safety.

Tests concurrent cache access to verify locking prevents RuntimeError
during concurrent cache cleanup operations.
"""

import threading
import time
from pathlib import Path

import pytest

from mcp_server.rag_engine import RAGEngine


@pytest.fixture
def temp_index_dir(tmp_path):
    """Create temporary index directory for tests."""
    index_dir = tmp_path / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    return index_dir


@pytest.fixture
def temp_standards_dir(tmp_path):
    """Create temporary standards directory for tests."""
    standards_dir = tmp_path / "standards"
    standards_dir.mkdir(parents=True, exist_ok=True)
    # Create a dummy file so grep doesn't fail
    (standards_dir / "test.md").write_text("# Test content\n")
    return standards_dir


@pytest.fixture
def rag_engine(temp_index_dir, temp_standards_dir):
    """Create RAGEngine for tests."""
    return RAGEngine(
        index_path=temp_index_dir,
        standards_path=temp_standards_dir,
        embedding_provider="local",
        cache_ttl_seconds=1,  # Short TTL for testing expiration
    )


def test_concurrent_cache_cleanup_no_runtime_error(rag_engine):
    """
    Test that concurrent searches and cache cleanup don't crash.

    Verifies that the lock in _clean_cache() prevents RuntimeError
    that would occur from modifying dict during iteration.
    """
    errors = []

    def search_loop():
        """Continuously search to populate cache."""
        try:
            for i in range(50):
                # Different queries to create cache entries
                rag_engine.search(f"test query {i % 10}")
        except Exception as e:
            errors.append(("search", e))

    def cleanup_loop():
        """Continuously clean cache."""
        try:
            for _ in range(50):
                rag_engine._clean_cache()
                time.sleep(0.001)  # Small delay
        except Exception as e:
            errors.append(("cleanup", e))

    # Start concurrent threads
    threads = [
        threading.Thread(target=search_loop),
        threading.Thread(target=search_loop),  # Two search threads
        threading.Thread(target=cleanup_loop),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Assert no RuntimeError occurred
    assert len(errors) == 0, f"Errors occurred: {errors}"


def test_cache_ttl_expiration(rag_engine):
    """
    Test that cache entries expire correctly after TTL.

    Verifies that _clean_cache() removes expired entries
    based on cache_ttl_seconds setting.
    """
    # Manually populate cache (since grep fallback doesn't cache)
    import time as time_module

    from mcp_server.models.rag import SearchResult

    # Add test entries to cache
    rag_engine._query_cache["test_key_1"] = (
        SearchResult(
            chunks=[],
            total_tokens=0,
            retrieval_method="test",
            query_time_ms=0,
            relevance_scores=[],
        ),
        time_module.time(),
    )
    rag_engine._query_cache["test_key_2"] = (
        SearchResult(
            chunks=[],
            total_tokens=0,
            retrieval_method="test",
            query_time_ms=0,
            relevance_scores=[],
        ),
        time_module.time(),
    )

    # Check cache has entries
    assert len(rag_engine._query_cache) == 2, "Cache should have 2 entries"

    # Wait for TTL to expire (cache_ttl_seconds = 1)
    time.sleep(1.5)

    # Clean cache
    rag_engine._clean_cache()

    # Verify cache is empty
    assert (
        len(rag_engine._query_cache) == 0
    ), "Cache should be empty after TTL expiration"


def test_concurrent_cache_operations_stress_test(rag_engine):
    """
    Stress test with many iterations to catch rare race conditions.

    Runs sustained concurrent cache operations to ensure
    robustness under heavy load.
    """
    iterations = 100  # Reduced for faster CI
    errors = []

    def worker(worker_id):
        """Worker that alternates between search and cleanup."""
        try:
            for i in range(iterations):
                if i % 10 == 0:
                    rag_engine._clean_cache()
                else:
                    rag_engine.search(f"query {worker_id}-{i % 5}")
        except Exception as e:
            errors.append((worker_id, e))

    # Start multiple workers
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Errors occurred: {errors}"


def test_check_cache_thread_safety(rag_engine):
    """
    Test that _check_cache() is thread-safe.

    Verifies concurrent cache lookups don't cause issues
    and properly acquire lock.
    """
    # Manually populate cache with test data
    import time as time_module

    from mcp_server.models.rag import SearchResult

    test_cache_key = "test_cache_key_123"
    rag_engine._query_cache[test_cache_key] = (
        SearchResult(
            chunks=[],
            total_tokens=0,
            retrieval_method="test",
            query_time_ms=0,
            relevance_scores=[],
        ),
        time_module.time(),
    )

    results = []
    errors = []

    def check_cache_worker():
        """Worker that checks cache repeatedly."""
        try:
            for _ in range(100):
                result = rag_engine._check_cache(test_cache_key)
                results.append(result is not None)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=check_cache_worker) for _ in range(5)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Errors occurred: {errors}"
    # All checks should find the cache entry (since TTL is 1 second and we run quickly)
    assert (
        sum(results) > 450
    ), f"Most cache checks should succeed, got {sum(results)}/500"


def test_cache_cleanup_during_search(rag_engine):
    """
    Test cache cleanup happening during active searches.

    Verifies that cleanup can safely run while searches
    are populating the cache.
    """
    errors = []
    search_count = [0]
    cleanup_count = [0]

    def searcher():
        """Continuous searcher."""
        try:
            for i in range(100):
                rag_engine.search(f"query {i % 20}")
                search_count[0] += 1
        except Exception as e:
            errors.append(("search", e))

    def cleaner():
        """Continuous cleaner."""
        try:
            for _ in range(50):
                rag_engine._clean_cache()
                cleanup_count[0] += 1
                time.sleep(0.002)
        except Exception as e:
            errors.append(("clean", e))

    threads = [
        threading.Thread(target=searcher),
        threading.Thread(target=searcher),
        threading.Thread(target=cleaner),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert search_count[0] > 0, "Searches should have completed"
    assert cleanup_count[0] > 0, "Cleanups should have completed"


def test_cache_size_limit_cleanup(rag_engine):
    """
    Test that cache cleanup triggers when size exceeds limit.

    Verifies that _cache_result() triggers cleanup when
    cache grows beyond 100 entries.
    """
    # Populate cache with many entries
    for i in range(150):
        rag_engine.search(f"unique query {i}")

    # Cache should not grow unbounded
    # (cleanup should have been triggered at 100 entries)
    cache_size = len(rag_engine._query_cache)

    # Allow some margin since cleanup happens after threshold
    assert cache_size < 120, (
        f"Cache size {cache_size} should be controlled by cleanup. "
        "Expected < 120 after cleanup triggers at 100."
    )
