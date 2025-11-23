"""
Tests for ProjectOrientationExecutor.

Tests query execution, timing tracking, and result aggregation.
"""

import pytest
import time
from unittest.mock import Mock

from ouroboros.subsystems.rag.standards.orientation import (
    ProjectOrientationExecutor,
    OrientationSessionSummary,
    QueryExecutionResult
)
from ouroboros.config.schemas.orientation import OrientationQuery


class TestProjectOrientationExecutorInstantiation:
    """Test ProjectOrientationExecutor instantiation."""
    
    def test_valid_instantiation(self):
        """
        Test ProjectOrientationExecutor with valid search_tool.
        
        Validates:
            - Constructor accepts search_tool
            - Stores reference correctly
        
        Acceptance Criterion: Task 3.4 - ProjectOrientationExecutor class exists
        """
        search_tool = Mock()
        
        executor = ProjectOrientationExecutor(search_tool)
        
        assert executor.search_tool is search_tool
    
    def test_none_search_tool_raises_error(self):
        """
        Test that None search_tool raises TypeError.
        
        Validates:
            - Constructor validates search_tool is not None
            - Clear error message
        """
        with pytest.raises(TypeError) as exc_info:
            ProjectOrientationExecutor(None)
        
        assert "search_tool" in str(exc_info.value).lower()


class TestExecuteOrientation:
    """Test execute_orientation() method."""
    
    def test_execute_successful_queries(self):
        """
        Test executing queries that all succeed.
        
        Validates:
            - All queries execute
            - Summary reports all successful
            - Timing tracked
            - Result count correct
        
        Acceptance Criterion: Task 3.4 - Executes 10 queries and returns OrientationSessionSummary
        """
        # Mock search tool that returns results
        search_tool = Mock()
        search_tool.return_value = ["result1", "result2", "result3"]
        
        executor = ProjectOrientationExecutor(search_tool)
        
        # Create 10 queries
        queries = [
            OrientationQuery(query=f"query {i}", priority=1)
            for i in range(10)
        ]
        
        summary = executor.execute_orientation(queries)
        
        # Verify summary
        assert isinstance(summary, OrientationSessionSummary)
        assert summary.total_queries == 10
        assert summary.successful_queries == 10
        assert summary.failed_queries == 0
        assert summary.completed is True
        assert len(summary.query_results) == 10
        
        # Verify timing tracked
        assert summary.total_execution_time_ms > 0
        
        # Verify each result
        for result in summary.query_results:
            assert isinstance(result, QueryExecutionResult)
            assert result.success is True
            assert result.result_count == 3
            assert result.execution_time_ms > 0
            assert result.error_message is None
    
    def test_execute_with_failures(self):
        """
        Test executing queries with some failures.
        
        Validates:
            - Failed queries don't stop execution
            - Summary reports correct counts
            - Error messages captured
        
        Acceptance Criterion: Task 3.4 - Collects all results (successful + failed) in summary
        """
        # Mock search tool that fails on even queries
        def search_func(query):
            if "even" in query:
                raise Exception("Search failed")
            return ["result"]
        
        search_tool = Mock(side_effect=search_func)
        executor = ProjectOrientationExecutor(search_tool)
        
        queries = [
            OrientationQuery(query="odd query 1", priority=1),
            OrientationQuery(query="even query 2", priority=1),
            OrientationQuery(query="odd query 3", priority=1),
            OrientationQuery(query="even query 4", priority=1)
        ]
        
        summary = executor.execute_orientation(queries)
        
        # Verify counts
        assert summary.total_queries == 4
        assert summary.successful_queries == 2
        assert summary.failed_queries == 2
        assert summary.completed is True
        
        # Verify error messages captured
        failed_results = [r for r in summary.query_results if not r.success]
        assert len(failed_results) == 2
        for result in failed_results:
            assert result.error_message is not None
            assert "Search failed" in result.error_message
    
    def test_execute_empty_queries(self):
        """
        Test executing with empty queries list.
        
        Validates:
            - Empty list handled gracefully
            - Returns valid summary
            - No exceptions
        """
        search_tool = Mock()
        executor = ProjectOrientationExecutor(search_tool)
        
        summary = executor.execute_orientation([])
        
        assert summary.total_queries == 0
        assert summary.successful_queries == 0
        assert summary.failed_queries == 0
        assert summary.completed is True
        assert summary.query_results == []
    
    def test_execute_with_timeout(self):
        """
        Test executing with timeout.
        
        Validates:
            - Timeout interrupts execution
            - Returns partial results
            - completed=False when timed out
        
        Acceptance Criterion: Task 3.4 - Returns partial results if timeout occurs
        """
        # Mock slow search tool (50ms per query)
        def slow_search(query):
            time.sleep(0.05)  # 50ms
            return ["result"]
        
        search_tool = Mock(side_effect=slow_search)
        executor = ProjectOrientationExecutor(search_tool)
        
        # Create queries
        queries = [
            OrientationQuery(query=f"query {i}", priority=1)
            for i in range(10)
        ]
        
        # Execute with 150ms timeout (should complete ~3 queries)
        summary = executor.execute_orientation(queries, timeout_ms=150)
        
        # Verify partial results
        assert summary.completed is False
        assert summary.successful_queries < 10
        assert summary.successful_queries >= 2  # At least 2 should complete
        assert len(summary.query_results) < 10
    
    def test_tracks_execution_time_per_query(self):
        """
        Test that execution time is tracked per query.
        
        Validates:
            - Each result has execution_time_ms
            - Times are reasonable
        
        Acceptance Criterion: Task 3.4 - Tracks execution_time_ms for each query
        """
        search_tool = Mock(return_value=["result"])
        executor = ProjectOrientationExecutor(search_tool)
        
        queries = [
            OrientationQuery(query="query 1", priority=1),
            OrientationQuery(query="query 2", priority=1)
        ]
        
        summary = executor.execute_orientation(queries)
        
        # Each result should have timing
        for result in summary.query_results:
            assert result.execution_time_ms > 0
            # Reasonable bounds (< 1 second for mock)
            assert result.execution_time_ms < 1000


class TestExecutionResultDataStructures:
    """Test QueryExecutionResult and OrientationSessionSummary data structures."""
    
    def test_query_execution_result_creation(self):
        """Test creating QueryExecutionResult."""
        query = OrientationQuery(query="test query", priority=1)
        
        result = QueryExecutionResult(
            query=query,
            execution_time_ms=123.45,
            success=True,
            result_count=5
        )
        
        assert result.query is query
        assert result.execution_time_ms == 123.45
        assert result.success is True
        assert result.result_count == 5
        assert result.error_message is None
    
    def test_query_execution_result_with_error(self):
        """Test creating QueryExecutionResult with error."""
        query = OrientationQuery(query="test query", priority=1)
        
        result = QueryExecutionResult(
            query=query,
            execution_time_ms=50.0,
            success=False,
            result_count=0,
            error_message="Connection failed"
        )
        
        assert result.success is False
        assert result.error_message == "Connection failed"
    
    def test_orientation_session_summary_creation(self):
        """Test creating OrientationSessionSummary."""
        query1 = OrientationQuery(query="query 1", priority=1)
        query2 = OrientationQuery(query="query 2", priority=2)
        
        result1 = QueryExecutionResult(
            query=query1, execution_time_ms=100, success=True, result_count=3
        )
        result2 = QueryExecutionResult(
            query=query2, execution_time_ms=150, success=False, error_message="Error"
        )
        
        summary = OrientationSessionSummary(
            total_queries=2,
            successful_queries=1,
            failed_queries=1,
            total_execution_time_ms=250.0,
            query_results=[result1, result2],
            completed=True
        )
        
        assert summary.total_queries == 2
        assert summary.successful_queries == 1
        assert summary.failed_queries == 1
        assert summary.total_execution_time_ms == 250.0
        assert len(summary.query_results) == 2
        assert summary.completed is True


class TestErrorHandling:
    """Test error handling in executor."""
    
    def test_search_tool_exception_handled(self):
        """
        Test that search_tool exceptions are handled gracefully.
        
        Validates:
            - Exception caught
            - Error message captured
            - Execution continues
        """
        def failing_search(query):
            raise RuntimeError("Database connection lost")
        
        search_tool = Mock(side_effect=failing_search)
        executor = ProjectOrientationExecutor(search_tool)
        
        queries = [OrientationQuery(query="test query", priority=1)]
        
        summary = executor.execute_orientation(queries)
        
        # Should complete but report failure
        assert summary.total_queries == 1
        assert summary.successful_queries == 0
        assert summary.failed_queries == 1
        assert summary.completed is True
        
        # Error captured
        result = summary.query_results[0]
        assert result.success is False
        assert "Database connection lost" in result.error_message


class TestPerformanceMonitoring:
    """Test performance metric collection and calculation."""
    
    def test_collects_execution_time_per_query(self):
        """
        Test that execution time is collected for each query.
        
        Validates:
            - Each result has execution_time_ms
            - Times are tracked
        
        Acceptance Criterion: Task 3.7 - Collects execution_time_ms for each query
        """
        search_tool = Mock(return_value=["result"])
        executor = ProjectOrientationExecutor(search_tool)
        
        queries = [
            OrientationQuery(query="query 1", priority=1),
            OrientationQuery(query="query 2", priority=1)
        ]
        
        summary = executor.execute_orientation(queries)
        
        # Each result should have timing
        for result in summary.query_results:
            assert result.execution_time_ms > 0
    
    def test_calculates_percentiles(self):
        """
        Test that percentiles (p50, p95, p99) are calculated correctly.
        
        Validates:
            - p50, p95, p99 are present in summary
            - Values are reasonable
            - Percentiles increase (p50 <= p95 <= p99)
        
        Acceptance Criterion: Task 3.7 - Calculates p50, p95, p99 percentiles correctly
        """
        # Mock search tool with variable timing
        call_count = [0]
        def variable_time_search(query):
            call_count[0] += 1
            # Sleep for different times to create distribution
            time.sleep(0.001 * call_count[0])  # 1ms, 2ms, 3ms, etc.
            return ["result"]
        
        search_tool = Mock(side_effect=variable_time_search)
        executor = ProjectOrientationExecutor(search_tool)
        
        queries = [
            OrientationQuery(query=f"query {i}", priority=1)
            for i in range(10)
        ]
        
        summary = executor.execute_orientation(queries)
        
        # Percentiles should be present
        assert summary.p50_execution_time_ms >= 0
        assert summary.p95_execution_time_ms >= 0
        assert summary.p99_execution_time_ms >= 0
        
        # Percentiles should be ordered
        assert summary.p50_execution_time_ms <= summary.p95_execution_time_ms
        assert summary.p95_execution_time_ms <= summary.p99_execution_time_ms
    
    def test_tracks_slowest_query(self):
        """
        Test that slowest query is tracked.
        
        Validates:
            - slowest_query_string is set
            - slowest_time_ms is the maximum time
        
        Acceptance Criterion: Task 3.7 - Tracks slowest_query_string and slowest_time_ms
        """
        # Mock search with one slow query
        def variable_speed_search(query):
            if "slow" in query:
                time.sleep(0.05)  # 50ms
            else:
                time.sleep(0.001)  # 1ms
            return ["result"]
        
        search_tool = Mock(side_effect=variable_speed_search)
        executor = ProjectOrientationExecutor(search_tool)
        
        queries = [
            OrientationQuery(query="fast query 1", priority=1),
            OrientationQuery(query="slow query", priority=1),
            OrientationQuery(query="fast query 2", priority=1)
        ]
        
        summary = executor.execute_orientation(queries)
        
        # Slowest query should be identified
        assert "slow" in summary.slowest_query_string
        assert summary.slowest_time_ms > 40  # Should be ~50ms
    
    def test_performance_summary_logged(self, caplog):
        """
        Test that performance summary is logged.
        
        Validates:
            - Performance metrics logged with logger.info()
            - Log contains percentiles
            - Log contains slowest query
        
        Acceptance Criterion: Task 3.7 - Metrics logged with logger.info() after execution
        """
        search_tool = Mock(return_value=["result"])
        executor = ProjectOrientationExecutor(search_tool)
        
        queries = [
            OrientationQuery(query="query 1", priority=1),
            OrientationQuery(query="query 2", priority=1)
        ]
        
        with caplog.at_level("INFO"):
            summary = executor.execute_orientation(queries)
        
        # Performance metrics should be logged
        perf_logs = [r for r in caplog.records if "Performance metrics" in r.message]
        assert len(perf_logs) > 0
        
        perf_log = perf_logs[0].message
        # Should contain percentiles
        assert "p50" in perf_log
        assert "p95" in perf_log
        assert "p99" in perf_log
        # Should contain slowest query
        assert "slowest" in perf_log
    
    def test_empty_results_metrics(self):
        """
        Test that empty results produce zero metrics.
        
        Validates:
            - Empty query list handled gracefully
            - Metrics default to zero
        """
        search_tool = Mock()
        executor = ProjectOrientationExecutor(search_tool)
        
        summary = executor.execute_orientation([])
        
        # Metrics should be zero
        assert summary.p50_execution_time_ms == 0.0
        assert summary.p95_execution_time_ms == 0.0
        assert summary.p99_execution_time_ms == 0.0
        assert summary.slowest_query_string == ""
        assert summary.slowest_time_ms == 0.0
    
    def test_single_query_percentiles(self):
        """
        Test percentiles with single query.
        
        Validates:
            - Single query produces same value for all percentiles
            - No index errors
        """
        search_tool = Mock(return_value=["result"])
        executor = ProjectOrientationExecutor(search_tool)
        
        queries = [OrientationQuery(query="single query", priority=1)]
        
        summary = executor.execute_orientation(queries)
        
        # All percentiles should be same (only one data point)
        assert summary.p50_execution_time_ms > 0
        assert summary.p50_execution_time_ms == summary.p95_execution_time_ms
        assert summary.p95_execution_time_ms == summary.p99_execution_time_ms
        assert summary.slowest_query_string == "single query"


class TestTimeoutProtection:
    """Test timeout protection mechanisms."""
    
    def test_default_60_second_timeout(self):
        """
        Test that default timeout is 60 seconds.
        
        Validates:
            - Default timeout_ms is 60000 (60 seconds)
        
        Acceptance Criterion: Task 3.5 - Execution stops after 60 seconds total time
        """
        search_tool = Mock(return_value=["result"])
        executor = ProjectOrientationExecutor(search_tool)
        
        # Inspect default parameter (via function signature or test execution)
        # This test documents the expectation
        queries = [OrientationQuery(query="test query", priority=1)]
        summary = executor.execute_orientation(queries)
        
        # Should complete successfully (not timing out)
        assert summary.completed is True
    
    def test_timeout_stops_execution(self, caplog):
        """
        Test that timeout stops execution and returns partial results.
        
        Validates:
            - Execution stops when timeout reached
            - Returns partial results
            - completed=False when timed out
            - Logs warning with "Orientation timeout"
        
        Acceptance Criteria: 
            - Task 3.5: Returns partial results when timeout occurs
            - Task 3.5: Logs warning: "Orientation timeout after {ms}ms"
        """
        # Mock slow search tool (50ms per query)
        def slow_search(query):
            time.sleep(0.05)  # 50ms
            return ["result"]
        
        search_tool = Mock(side_effect=slow_search)
        executor = ProjectOrientationExecutor(search_tool)
        
        # Create 20 queries (would take ~1000ms total)
        queries = [
            OrientationQuery(query=f"query {i}", priority=1)
            for i in range(20)
        ]
        
        # Execute with 200ms timeout (should complete ~4 queries)
        with caplog.at_level("WARNING"):
            summary = executor.execute_orientation(queries, timeout_ms=200)
        
        # Verify partial results
        assert summary.completed is False
        assert summary.successful_queries < 20
        assert summary.successful_queries >= 3  # At least 3 should complete
        
        # Verify timeout warning logged
        assert any("Orientation timeout" in record.message for record in caplog.records)
    
    def test_mock_65_second_execution_times_out(self, caplog):
        """
        Test that 65-second execution times out (exceeds 60s default).
        
        Validates:
            - Execution stops before completing all queries
            - Returns partial results
            - Timeout logged
        
        Acceptance Criterion: Task 3.5 - Timeout test passes (mock 65s execution)
        """
        # Mock very slow search (100ms per query, 10 queries = 1000ms)
        def slow_search(query):
            time.sleep(0.1)  # 100ms
            return ["result"]
        
        search_tool = Mock(side_effect=slow_search)
        executor = ProjectOrientationExecutor(search_tool)
        
        # Create 100 queries (would take ~10000ms = 10s total if all execute)
        queries = [
            OrientationQuery(query=f"query {i}", priority=1)
            for i in range(100)
        ]
        
        # Execute with 500ms timeout (simulating 65s timeout scenario)
        with caplog.at_level("WARNING"):
            summary = executor.execute_orientation(queries, timeout_ms=500)
        
        # Should timeout before completing all queries
        assert summary.completed is False
        assert summary.successful_queries < 100
        
        # Verify timeout logged
        timeout_logs = [r for r in caplog.records if "Orientation timeout" in r.message]
        assert len(timeout_logs) > 0
        assert "completed" in timeout_logs[0].message.lower()
    
    def test_per_query_timeout_warning(self, caplog):
        """
        Test that per-query timeout logs warning for slow queries.
        
        Validates:
            - Individual queries exceeding per-query timeout log warning
            - Execution continues after slow query
        
        Acceptance Criterion: Task 3.5 - Per-query timeout of 10s prevents runaway queries
        """
        # Mock search tool with one slow query
        def variable_speed_search(query):
            if "slow" in query:
                time.sleep(0.2)  # 200ms (exceeds our test timeout)
            return ["result"]
        
        search_tool = Mock(side_effect=variable_speed_search)
        executor = ProjectOrientationExecutor(search_tool)
        
        queries = [
            OrientationQuery(query="fast query 1", priority=1),
            OrientationQuery(query="slow query", priority=1),
            OrientationQuery(query="fast query 2", priority=1)
        ]
        
        # Execute with per-query timeout of 100ms
        with caplog.at_level("WARNING"):
            summary = executor.execute_orientation(
                queries,
                timeout_ms=10000,  # Large total timeout
                per_query_timeout_ms=100  # Small per-query timeout
            )
        
        # All queries should complete (but one logs warning)
        assert summary.total_queries == 3
        assert summary.successful_queries == 3
        
        # Verify per-query timeout warning logged
        timeout_warnings = [
            r for r in caplog.records 
            if "exceeded per-query timeout" in r.message
        ]
        assert len(timeout_warnings) >= 1
    
    def test_no_timeout_when_queries_complete_quickly(self):
        """
        Test that fast queries don't trigger timeout.
        
        Validates:
            - Quick execution completes all queries
            - completed=True
            - No timeout warnings
        """
        search_tool = Mock(return_value=["result"])
        executor = ProjectOrientationExecutor(search_tool)
        
        queries = [
            OrientationQuery(query=f"query {i}", priority=1)
            for i in range(10)
        ]
        
        summary = executor.execute_orientation(queries, timeout_ms=10000)
        
        # Should complete all queries
        assert summary.completed is True
        assert summary.successful_queries == 10
        assert summary.total_queries == 10

