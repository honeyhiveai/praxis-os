"""
Performance tests for Project Orientation System.

Tests Non-Functional Requirements (NFRs) for:
- NFR-P1: Orientation execution completes < 60s for 10 queries
- NFR-P2: Metadata parsing < 100ms per file
- Query execution p95 < 2s target
- Timeout protection triggers at 60s boundary

Traceable to: .praxis-os/specs/approved/2025-11-19-project-orientation-system/
"""

import pytest
import time
from pathlib import Path
from typing import List, Any
from unittest.mock import Mock

from ouroboros.config.schemas.orientation import OrientationQuery
from ouroboros.subsystems.rag.standards.orientation import (
    OrientationMetadataParser,
    ProjectOrientationExecutor,
)


class TestNFRP1OrientationExecutionTime:
    """
    Test NFR-P1: Full orientation execution < 60 seconds for 10 queries.
    
    This is a critical performance requirement to ensure AI agents
    can complete orientation quickly without delays.
    """
    
    def test_ten_queries_execute_under_60_seconds(self):
        """
        Test that 10 queries execute in < 60,000ms (NFR-P1).
        
        This is the primary performance target for the orientation system.
        Each query should be fast enough that 10 queries complete well
        under the 60-second timeout.
        """
        # Create 10 test queries
        queries = [
            OrientationQuery(
                query=f"test query {i} for performance testing",
                priority=1,
                description=f"Query {i}"
            )
            for i in range(10)
        ]
        
        # Mock search tool that simulates realistic search time (~500ms per query)
        def mock_search(query: str) -> List[Any]:
            time.sleep(0.5)  # Simulate 500ms search time
            return [{"result": "mock result"}]
        
        executor = ProjectOrientationExecutor(mock_search)
        
        # Execute and time
        start_time = time.monotonic()
        summary = executor.execute_orientation(queries)
        total_time_ms = (time.monotonic() - start_time) * 1000
        
        # Verify NFR-P1: < 60,000ms for 10 queries
        assert total_time_ms < 60000, (
            f"NFR-P1 FAILED: 10 queries took {total_time_ms:.0f}ms, "
            f"expected < 60,000ms"
        )
        
        # Verify all queries completed successfully
        assert summary.total_queries == 10
        assert summary.successful_queries == 10
        assert summary.completed is True
        
        # Log actual time for monitoring
        print(f"\n✅ NFR-P1 PASSED: 10 queries completed in {total_time_ms:.0f}ms (< 60,000ms)")
    
    def test_parallel_execution_potential(self):
        """
        Test that sequential execution is fast enough for NFR-P1.
        
        Even with sequential execution, 10 queries should complete quickly.
        This test validates that we don't need complex parallelization
        to meet performance targets.
        """
        queries = [
            OrientationQuery(
                query=f"query {i}",
                priority=1,
                description=f"Test {i}"
            )
            for i in range(10)
        ]
        
        # Fast mock (100ms per query = 1000ms total)
        def fast_mock_search(query: str) -> List[Any]:
            time.sleep(0.1)
            return [{"result": "fast"}]
        
        executor = ProjectOrientationExecutor(fast_mock_search)
        
        start_time = time.monotonic()
        summary = executor.execute_orientation(queries)
        total_time_ms = (time.monotonic() - start_time) * 1000
        
        # With fast queries, should complete in ~1 second
        assert total_time_ms < 2000, f"Fast queries took {total_time_ms:.0f}ms, expected < 2000ms"
        assert summary.successful_queries == 10
        
        print(f"\n✅ Sequential execution: 10 fast queries in {total_time_ms:.0f}ms")


class TestNFRP2MetadataParsingSpeed:
    """
    Test NFR-P2: Metadata parsing < 100ms per file.
    
    Fast metadata parsing is critical because it runs during discovery
    for every standards document that might contain orientation metadata.
    """
    
    def test_single_file_parsing_under_100ms(self):
        """
        Test that parsing a single file takes < 100ms (NFR-P2).
        
        This ensures discovery is fast even when scanning many files.
        """
        parser = OrientationMetadataParser()
        
        # Realistic markdown content with metadata
        content = """
# System Architecture

**Metadata**: orientation=true, priority=1, query="system architecture microservices patterns design", description="Core architecture knowledge", category="architecture"

This document describes our microservices architecture...

## Core Services

- API Gateway
- Auth Service
- Data Service

...more content...
        """
        
        # Parse and time
        start_time = time.monotonic()
        metadata = parser.extract_inline_metadata(content, Path("test.md"))
        elapsed_ms = (time.monotonic() - start_time) * 1000
        
        # Verify NFR-P2: < 100ms per file
        assert elapsed_ms < 100, (
            f"NFR-P2 FAILED: Parsing took {elapsed_ms:.2f}ms, expected < 100ms"
        )
        
        # Verify parsing was successful
        assert metadata is not None
        assert metadata.get('orientation') is True
        assert metadata.get('priority') == 1
        
        print(f"\n✅ NFR-P2 PASSED: Parsing completed in {elapsed_ms:.2f}ms (< 100ms)")
    
    def test_batch_parsing_scales_linearly(self):
        """
        Test that parsing 10 files takes < 1000ms (10 * 100ms).
        
        Validates that parsing performance scales linearly and
        doesn't degrade with multiple files.
        """
        parser = OrientationMetadataParser()
        
        # Create 10 different content samples
        contents = [
            f"**Metadata**: orientation=true, priority=1, query=\"test query {i}\""
            for i in range(10)
        ]
        
        # Parse all and time
        start_time = time.monotonic()
        for i, content in enumerate(contents):
            metadata = parser.extract_inline_metadata(content, Path(f"test{i}.md"))
            assert metadata is not None
        elapsed_ms = (time.monotonic() - start_time) * 1000
        
        # Should be < 1000ms for 10 files (< 100ms each)
        assert elapsed_ms < 1000, (
            f"Batch parsing took {elapsed_ms:.0f}ms for 10 files, "
            f"expected < 1000ms (100ms per file)"
        )
        
        avg_per_file = elapsed_ms / 10
        print(f"\n✅ Batch parsing: 10 files in {elapsed_ms:.0f}ms ({avg_per_file:.1f}ms per file)")
    
    def test_large_file_parsing_performance(self):
        """
        Test parsing performance with a large markdown file.
        
        Validates that regex-based parsing is efficient even with
        large documents (the metadata is at the top, so size shouldn't matter much).
        """
        parser = OrientationMetadataParser()
        
        # Large file with metadata at top
        large_content = "# Title\n\n**Metadata**: orientation=true, priority=1, query=\"large file test\"\n\n"
        large_content += "Lorem ipsum dolor sit amet...\n" * 1000  # Add lots of content
        
        start_time = time.monotonic()
        metadata = parser.extract_inline_metadata(large_content, Path("large.md"))
        elapsed_ms = (time.monotonic() - start_time) * 1000
        
        # Even large files should parse < 100ms (metadata at top)
        assert elapsed_ms < 100, f"Large file parsing took {elapsed_ms:.2f}ms, expected < 100ms"
        assert metadata is not None
        
        print(f"\n✅ Large file ({len(large_content)} chars) parsed in {elapsed_ms:.2f}ms")


class TestQueryExecutionP95Performance:
    """
    Test query execution p95 < 2000ms target.
    
    While not a hard requirement, we aim for p95 query execution < 2s
    to ensure consistent performance.
    """
    
    def test_p95_query_execution_under_2_seconds(self):
        """
        Test that p95 query execution time < 2000ms.
        
        This is a target, not a hard requirement, but validates
        that most queries complete quickly.
        """
        # Create 20 queries to get meaningful p95
        queries = [
            OrientationQuery(
                query=f"query {i} for p95 testing",
                priority=1,
                description=f"Query {i}"
            )
            for i in range(20)
        ]
        
        # Mock with variable timing (most fast, some slower)
        call_count = [0]
        
        def variable_timing_mock(query: str) -> List[Any]:
            call_count[0] += 1
            # 90% of queries: 500ms
            # 10% of queries: 1500ms
            if call_count[0] % 10 == 0:
                time.sleep(1.5)  # Slow query
            else:
                time.sleep(0.5)  # Fast query
            return [{"result": "mock"}]
        
        executor = ProjectOrientationExecutor(variable_timing_mock)
        summary = executor.execute_orientation(queries)
        
        # Verify p95 < 2000ms
        assert summary.p95_execution_time_ms < 2000, (
            f"P95 query time {summary.p95_execution_time_ms:.0f}ms, "
            f"target < 2000ms"
        )
        
        # Log performance metrics
        print(f"\n✅ Performance metrics:")
        print(f"   P50: {summary.p50_execution_time_ms:.0f}ms")
        print(f"   P95: {summary.p95_execution_time_ms:.0f}ms (target < 2000ms)")
        print(f"   P99: {summary.p99_execution_time_ms:.0f}ms")
        print(f"   Slowest: {summary.slowest_time_ms:.0f}ms")


class TestTimeoutProtection:
    """
    Test timeout protection at 60-second boundary.
    
    Validates that the 60-second timeout protection works correctly
    and prevents runaway executions.
    """
    
    def test_timeout_triggers_at_60_second_boundary(self):
        """
        Test that 65-second execution triggers timeout at 60s.
        
        This is critical for preventing orientation from blocking
        indefinitely if a query hangs.
        """
        # Create queries that would take > 60s if all executed
        queries = [
            OrientationQuery(
                query=f"slow query {i}",
                priority=1,
                description=f"Query {i}"
            )
            for i in range(20)  # 20 * 4s = 80s total
        ]
        
        # Mock that takes 4 seconds per query
        def slow_mock(query: str) -> List[Any]:
            time.sleep(4.0)
            return [{"result": "slow"}]
        
        executor = ProjectOrientationExecutor(slow_mock)
        
        # Execute with short timeout for testing (5 seconds = 5000ms)
        start_time = time.monotonic()
        summary = executor.execute_orientation(queries, timeout_ms=5000.0)
        elapsed_seconds = time.monotonic() - start_time
        
        # Should timeout around 5-8 seconds (2 queries * 4s each)
        # Timeout check happens between queries, so it completes query 2 before stopping
        assert elapsed_seconds < 10, (  # Give buffer for 2 queries + overhead
            f"Timeout didn't trigger: execution took {elapsed_seconds:.1f}s, "
            f"expected ~8s (2 queries before timeout)"
        )
        
        # Should have completed fewer than all queries
        assert summary.successful_queries < len(queries), (
            "Timeout didn't stop execution: all queries completed"
        )
        
        # completed flag should be False (interrupted by timeout)
        assert summary.completed is False, "Summary should indicate incomplete execution"
        
        # Should have completed ~2 queries (2 * 4s = 8s, just over 5s timeout)
        assert summary.successful_queries <= 3, (
            f"Expected ~2 queries completed, got {summary.successful_queries}"
        )
        
        print(f"\n✅ Timeout protection: stopped at {elapsed_seconds:.1f}s (limit: 5s, stopped after query completion)")
        print(f"   Completed {summary.successful_queries}/{len(queries)} queries before timeout")
    
    def test_no_timeout_when_queries_complete_quickly(self):
        """
        Test that fast queries don't trigger timeout.
        
        Validates that timeout doesn't interfere with normal operation.
        """
        queries = [
            OrientationQuery(
                query=f"fast query {i}",
                priority=1,
                description=f"Query {i}"
            )
            for i in range(10)
        ]
        
        # Fast mock (100ms per query = 1s total)
        def fast_mock(query: str) -> List[Any]:
            time.sleep(0.1)
            return [{"result": "fast"}]
        
        executor = ProjectOrientationExecutor(fast_mock)
        summary = executor.execute_orientation(queries, timeout_ms=60000.0)
        
        # Should complete all queries
        assert summary.total_queries == len(queries)
        assert summary.completed is True
        assert summary.total_execution_time_ms < 2000  # Should be ~1000ms
        
        print(f"\n✅ Fast queries: {len(queries)} queries in {summary.total_execution_time_ms:.0f}ms (no timeout)")


class TestPerformanceSummaryMetrics:
    """
    Test that performance summary metrics are calculated correctly.
    
    These metrics help monitor and debug performance issues.
    """
    
    def test_summary_includes_all_performance_metrics(self):
        """
        Test that summary includes p50, p95, p99, slowest query.
        
        These metrics are essential for performance monitoring.
        """
        queries = [
            OrientationQuery(
                query=f"query {i}",
                priority=1,
                description=f"Query {i}"
            )
            for i in range(10)
        ]
        
        def mock_search(query: str) -> List[Any]:
            time.sleep(0.1)
            return [{"result": "mock"}]
        
        executor = ProjectOrientationExecutor(mock_search)
        summary = executor.execute_orientation(queries)
        
        # Verify all performance metrics are present
        assert hasattr(summary, 'p50_execution_time_ms')
        assert hasattr(summary, 'p95_execution_time_ms')
        assert hasattr(summary, 'p99_execution_time_ms')
        assert hasattr(summary, 'slowest_query_string')
        assert hasattr(summary, 'slowest_time_ms')
        
        # Verify metrics are reasonable
        assert summary.p50_execution_time_ms > 0
        assert summary.p95_execution_time_ms >= summary.p50_execution_time_ms
        assert summary.p99_execution_time_ms >= summary.p95_execution_time_ms
        assert summary.slowest_time_ms >= summary.p99_execution_time_ms
        assert summary.slowest_query_string != ""
        
        print(f"\n✅ Performance metrics collected:")
        print(f"   P50: {summary.p50_execution_time_ms:.0f}ms")
        print(f"   P95: {summary.p95_execution_time_ms:.0f}ms")
        print(f"   P99: {summary.p99_execution_time_ms:.0f}ms")
        print(f"   Slowest: {summary.slowest_time_ms:.0f}ms ({summary.slowest_query_string})")

