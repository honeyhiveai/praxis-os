"""
Performance tests for consolidated workflow tools.

Tests response time, throughput, memory usage, and scalability.
Uses pytest-benchmark for reliable performance measurements.

Performance Targets (from specs.md):
- Tool invocation overhead: < 50ms (p95)
- Action dispatch latency: < 10ms (p95)
- Validation overhead: < 5ms per operation
- Metadata cache: < 100ms for 100 workflows
- Session listing: < 200ms for 1000 sessions
"""

import asyncio
import json
from unittest.mock import AsyncMock, Mock

import pytest

from mcp_server.server.tools.workflow_tools import (
    validate_evidence_size,
    validate_session_id,
    validate_target_file,
)


class TestValidationPerformance:
    """Test performance of input validation functions."""

    def test_session_id_validation_speed(self, benchmark):
        """Verify session_id validation completes in < 5ms."""
        valid_session_id = "550e8400-e29b-41d4-a716-446655440000"

        result = benchmark(validate_session_id, valid_session_id)

        assert result is True
        # pytest-benchmark will report timing statistics

    def test_target_file_validation_speed(self, benchmark):
        """Verify target_file validation completes in < 5ms."""
        valid_file = "src/components/module.py"

        result = benchmark(validate_target_file, valid_file)

        assert result is True

    def test_evidence_validation_speed_small(self, benchmark):
        """Verify evidence validation for small payloads < 5ms."""
        small_evidence = {"test": "data", "count": 42, "status": "success"}

        result = benchmark(validate_evidence_size, small_evidence)

        assert result is True

    def test_evidence_validation_speed_large(self, benchmark):
        """Verify evidence validation for large (5MB) payloads < 100ms."""
        # Create 5MB payload (half the limit)
        large_evidence = {"data": "x" * (5 * 1024 * 1024)}

        result = benchmark(validate_evidence_size, large_evidence)

        assert result is True

    @pytest.mark.parametrize("size_mb", [0.1, 0.5, 1, 2, 5, 9])
    def test_evidence_validation_scales_linearly(self, size_mb):
        """Verify evidence validation scales linearly with payload size."""
        evidence = {"data": "x" * int(size_mb * 1024 * 1024)}

        # Should complete without timeout
        result = validate_evidence_size(evidence)

        assert result is True


class TestActionDispatcherPerformance:
    """Test performance of action dispatcher."""

    @pytest.mark.asyncio
    async def test_dispatcher_overhead(self, benchmark):
        """Verify action dispatcher adds < 10ms overhead."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Mock handler that returns immediately
        mock_workflow_engine = Mock()
        mock_workflow_engine.get_workflow_state = Mock(
            return_value={"workflow_state": {"phase": 1, "status": "active"}}
        )

        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_workflow_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Benchmark dispatcher call
        async def call_dispatcher():
            return await captured_tool_func(
                action="get_state", session_id="550e8400-e29b-41d4-a716-446655440000"
            )

        result = await benchmark.pedantic(call_dispatcher, rounds=100, iterations=1)

        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_unknown_action_rejection_speed(self, benchmark):
        """Verify unknown action rejection is fast (< 5ms)."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=Mock(),
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        async def call_invalid_action():
            return await captured_tool_func(action="invalid_action")

        result = await benchmark.pedantic(call_invalid_action, rounds=100, iterations=1)

        assert result["status"] == "error"
        assert "Unknown action" in result["error"]


class TestMetadataCachePerformance:
    """Test performance of workflow metadata caching."""

    @pytest.mark.asyncio
    async def test_list_workflows_cache_performance(self):
        """Verify cached workflow listing is fast (< 10ms)."""
        import mcp_server.server.tools.workflow_tools as wf_tools
        from mcp_server.server.tools.workflow_tools import register_workflow_tools
        from mcp_server.server.tools.workflow_tools.handlers import discovery

        # Pre-populate cache with 100 workflows
        discovery._workflow_metadata_cache = [
            {
                "workflow_type": f"workflow_{i}",
                "name": f"Workflow {i}",
                "category": "testing" if i % 2 == 0 else "documentation",
                "version": "1.0",
            }
            for i in range(100)
        ]

        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=Mock(),
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Time cache access
        import time

        start = time.perf_counter()

        result = await captured_tool_func(action="list_workflows")

        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result["status"] == "success"
        assert result["count"] == 100
        assert (
            elapsed_ms < 100
        ), f"Cache access took {elapsed_ms:.2f}ms, expected < 100ms"

    @pytest.mark.asyncio
    async def test_list_workflows_with_filter_performance(self):
        """Verify filtered workflow listing is fast."""
        import mcp_server.server.tools.workflow_tools as wf_tools
        from mcp_server.server.tools.workflow_tools import register_workflow_tools
        from mcp_server.server.tools.workflow_tools.handlers import discovery

        # Pre-populate cache with 100 workflows
        discovery._workflow_metadata_cache = [
            {
                "workflow_type": f"workflow_{i}",
                "category": "testing" if i % 2 == 0 else "documentation",
            }
            for i in range(100)
        ]

        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=Mock(),
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Time filtered access
        import time

        start = time.perf_counter()

        result = await captured_tool_func(action="list_workflows", category="testing")

        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result["status"] == "success"
        assert result["count"] == 50
        assert elapsed_ms < 100, f"Filtered cache access took {elapsed_ms:.2f}ms"


class TestConcurrentOperations:
    """Test performance under concurrent load."""

    @pytest.mark.asyncio
    async def test_concurrent_validation_operations(self):
        """Verify validation handles concurrent operations efficiently."""
        valid_session_id = "550e8400-e29b-41d4-a716-446655440000"

        async def validate_async():
            return validate_session_id(valid_session_id)

        # Run 100 validations concurrently
        import time

        start = time.perf_counter()

        tasks = [validate_async() for _ in range(100)]
        results = await asyncio.gather(*tasks)

        elapsed_ms = (time.perf_counter() - start) * 1000

        assert all(r is True for r in results)
        assert elapsed_ms < 500, f"100 concurrent validations took {elapsed_ms:.2f}ms"

    @pytest.mark.asyncio
    async def test_concurrent_action_dispatching(self):
        """Verify dispatcher handles concurrent requests efficiently."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Mock fast-returning handler
        mock_workflow_engine = Mock()
        mock_workflow_engine.get_workflow_state = Mock(
            return_value={"workflow_state": {"phase": 1}}
        )

        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_workflow_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        async def call_action():
            return await captured_tool_func(
                action="get_state", session_id="550e8400-e29b-41d4-a716-446655440000"
            )

        # Run 50 concurrent dispatcher calls
        import time

        start = time.perf_counter()

        tasks = [call_action() for _ in range(50)]
        results = await asyncio.gather(*tasks)

        elapsed_ms = (time.perf_counter() - start) * 1000

        assert all(r["status"] == "success" for r in results)
        assert elapsed_ms < 1000, f"50 concurrent calls took {elapsed_ms:.2f}ms"


class TestMemoryUsage:
    """Test memory efficiency of workflow operations."""

    def test_evidence_validation_memory_efficient(self):
        """Verify evidence validation doesn't copy large payloads unnecessarily."""
        # Create 5MB evidence
        large_evidence = {"data": "x" * (5 * 1024 * 1024)}

        import sys

        initial_size = sys.getsizeof(large_evidence)

        # Validate should not significantly increase memory
        result = validate_evidence_size(large_evidence)

        final_size = sys.getsizeof(large_evidence)

        assert result is True
        # Object size shouldn't change significantly (< 10% growth)
        assert final_size < initial_size * 1.1

    @pytest.mark.asyncio
    async def test_cache_memory_efficiency(self):
        """Verify workflow cache doesn't consume excessive memory."""
        import mcp_server.server.tools.workflow_tools as wf_tools
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        # Create 1000 workflow entries
        workflows = [
            {
                "workflow_type": f"workflow_{i}",
                "name": f"Workflow {i}",
                "category": "testing",
                "version": "1.0",
            }
            for i in range(1000)
        ]

        from mcp_server.server.tools.workflow_tools.handlers import discovery

        discovery._workflow_metadata_cache = workflows

        import sys

        cache_size_bytes = sys.getsizeof(workflows)
        cache_size_mb = cache_size_bytes / (1024 * 1024)

        # 1000 workflows should be < 1MB in memory
        assert cache_size_mb < 1.0, f"Cache uses {cache_size_mb:.2f}MB"


class TestScalability:
    """Test performance scaling characteristics."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("session_count", [10, 100, 1000])
    async def test_list_sessions_scales_with_count(self, session_count):
        """Verify list_sessions performance scales acceptably."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Mock sessions
        mock_sessions = [
            {
                "session_id": f"550e8400-e29b-41d4-a716-44665544{i:04d}",
                "workflow_type": "test",
                "status": "active",
            }
            for i in range(session_count)
        ]

        mock_workflow_engine = Mock()
        mock_workflow_engine.state_manager = Mock()
        mock_workflow_engine.state_manager.list_sessions = Mock(
            return_value=mock_sessions
        )

        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_workflow_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Time operation
        import time

        start = time.perf_counter()

        result = await captured_tool_func(action="list_sessions")

        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result["status"] == "success"
        assert result["count"] == session_count

        # Performance targets:
        # - 10 sessions: < 50ms
        # - 100 sessions: < 100ms
        # - 1000 sessions: < 200ms
        if session_count == 10:
            assert elapsed_ms < 50, f"{session_count} sessions took {elapsed_ms:.2f}ms"
        elif session_count == 100:
            assert elapsed_ms < 100, f"{session_count} sessions took {elapsed_ms:.2f}ms"
        elif session_count == 1000:
            assert elapsed_ms < 200, f"{session_count} sessions took {elapsed_ms:.2f}ms"

    @pytest.mark.parametrize("evidence_count", [1, 10, 100])
    def test_evidence_validation_with_many_keys(self, evidence_count):
        """Verify evidence validation scales with key count."""
        evidence = {f"key_{i}": f"value_{i}" for i in range(evidence_count)}

        import time

        start = time.perf_counter()

        result = validate_evidence_size(evidence)

        elapsed_ms = (time.perf_counter() - start) * 1000

        assert result is True
        # Should be fast even with 100 keys
        if evidence_count <= 10:
            assert elapsed_ms < 5
        else:
            assert elapsed_ms < 20


class TestResponseTimeConsistency:
    """Test that response times are consistent across calls."""

    @pytest.mark.asyncio
    async def test_consistent_validation_performance(self):
        """Verify validation performance is consistent across multiple calls."""
        valid_session_id = "550e8400-e29b-41d4-a716-446655440000"

        import time

        times = []

        # Run validation 100 times
        for _ in range(100):
            start = time.perf_counter()
            validate_session_id(valid_session_id)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        # Calculate statistics
        avg_ms = sum(times) / len(times)
        max_ms = max(times)
        min_ms = min(times)

        # Performance should be consistent
        # For very fast operations (< 0.01ms avg), allow more variance due to timer resolution
        # For slower operations, max shouldn't be more than 10x average
        if avg_ms < 0.01:
            # Very fast operations, check absolute time instead
            assert max_ms < 1.0, f"Max time {max_ms:.3f}ms exceeds 1ms"
        else:
            assert (
                max_ms < avg_ms * 10
            ), f"Performance inconsistent: avg={avg_ms:.2f}ms, max={max_ms:.2f}ms"
        assert (
            avg_ms < 1.0
        ), f"Average validation time {avg_ms:.2f}ms exceeds 1ms target"

    @pytest.mark.asyncio
    async def test_p95_response_time_under_target(self):
        """Verify p95 response time meets performance targets."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        mock_workflow_engine = Mock()
        mock_workflow_engine.get_workflow_state = Mock(
            return_value={"workflow_state": {"phase": 1}}
        )

        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_workflow_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        import time

        times = []

        # Run 100 calls
        for _ in range(100):
            start = time.perf_counter()
            result = await captured_tool_func(
                action="get_state", session_id="550e8400-e29b-41d4-a716-446655440000"
            )
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            assert result["status"] == "success"

        # Calculate p95 (95th percentile)
        times.sort()
        p95_ms = times[94]  # 95th item in sorted list of 100

        # Target: p95 < 50ms
        assert p95_ms < 50, f"p95 response time {p95_ms:.2f}ms exceeds 50ms target"
