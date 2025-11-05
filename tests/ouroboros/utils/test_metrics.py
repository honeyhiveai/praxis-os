"""
Unit tests for ouroboros.utils.metrics.

Tests behavioral metrics collection including:
    - Query tracking and diversity
    - Latency tracking
    - Tool usage tracking
    - Workflow gate tracking
    - Metrics summaries
"""

import time

import pytest
from ouroboros.utils.metrics import MetricsCollector


class TestMetricsCollectorInitialization:
    """Test MetricsCollector initialization."""

    def test_metrics_collector_creation(self):
        """MetricsCollector should initialize with empty data structures."""
        metrics = MetricsCollector()

        assert metrics.queries == {}
        assert metrics.latencies == {}
        assert metrics.tool_usage == {}
        assert metrics.workflow_gates == {}


class TestQueryTracking:
    """Test query tracking and diversity calculation."""

    def test_track_query_single(self):
        """track_query() should record single query."""
        metrics = MetricsCollector()
        metrics.track_query("How does X work?", session_id="s1")

        assert len(metrics.queries["s1"]) == 1
        assert metrics.queries["s1"][0] == "How does X work?"

    def test_track_query_multiple(self):
        """track_query() should record multiple queries."""
        metrics = MetricsCollector()
        metrics.track_query("Query 1", session_id="s1")
        metrics.track_query("Query 2", session_id="s1")
        metrics.track_query("Query 3", session_id="s1")

        assert len(metrics.queries["s1"]) == 3

    def test_track_query_different_sessions(self):
        """track_query() should track queries per session."""
        metrics = MetricsCollector()
        metrics.track_query("Query A", session_id="s1")
        metrics.track_query("Query B", session_id="s2")

        assert len(metrics.queries["s1"]) == 1
        assert len(metrics.queries["s2"]) == 1
        assert metrics.queries["s1"][0] == "Query A"
        assert metrics.queries["s2"][0] == "Query B"

    def test_get_query_diversity_perfect(self):
        """get_query_diversity() should return 1.0 for all unique queries."""
        metrics = MetricsCollector()
        metrics.track_query("Query A", session_id="s1")
        metrics.track_query("Query B", session_id="s1")
        metrics.track_query("Query C", session_id="s1")

        diversity = metrics.get_query_diversity("s1")
        assert diversity == 1.0

    def test_get_query_diversity_with_duplicates(self):
        """get_query_diversity() should calculate correctly with duplicates."""
        metrics = MetricsCollector()
        metrics.track_query("Query A", session_id="s1")
        metrics.track_query("Query B", session_id="s1")
        metrics.track_query("Query A", session_id="s1")  # duplicate

        diversity = metrics.get_query_diversity("s1")
        assert diversity == 2 / 3  # 2 unique, 3 total

    def test_get_query_diversity_all_duplicates(self):
        """get_query_diversity() should return low value for all duplicates."""
        metrics = MetricsCollector()
        metrics.track_query("Same query", session_id="s1")
        metrics.track_query("Same query", session_id="s1")
        metrics.track_query("Same query", session_id="s1")

        diversity = metrics.get_query_diversity("s1")
        assert diversity == 1 / 3  # 1 unique, 3 total

    def test_get_query_diversity_empty(self):
        """get_query_diversity() should return 1.0 for empty session."""
        metrics = MetricsCollector()
        diversity = metrics.get_query_diversity("nonexistent")

        assert diversity == 1.0

    def test_get_query_count(self):
        """get_query_count() should return correct counts."""
        metrics = MetricsCollector()
        metrics.track_query("A", session_id="s1")
        metrics.track_query("B", session_id="s1")
        metrics.track_query("A", session_id="s1")

        counts = metrics.get_query_count("s1")
        assert counts["unique"] == 2
        assert counts["total"] == 3
        assert counts["diversity"] == 2 / 3


class TestLatencyTracking:
    """Test latency tracking functionality."""

    def test_track_latency_context_manager(self):
        """track_latency() should work as context manager."""
        metrics = MetricsCollector()

        with metrics.track_latency("test_operation"):
            time.sleep(0.01)  # Sleep 10ms

        latencies = metrics.latencies["test_operation"]
        assert len(latencies) == 1
        assert latencies[0] >= 10  # At least 10ms

    def test_track_latency_multiple_operations(self):
        """track_latency() should track multiple operations."""
        metrics = MetricsCollector()

        with metrics.track_latency("op1"):
            time.sleep(0.01)

        with metrics.track_latency("op2"):
            time.sleep(0.02)

        assert len(metrics.latencies["op1"]) == 1
        assert len(metrics.latencies["op2"]) == 1
        assert metrics.latencies["op2"][0] > metrics.latencies["op1"][0]

    def test_track_latency_same_operation_multiple_times(self):
        """track_latency() should accumulate latencies for same operation."""
        metrics = MetricsCollector()

        with metrics.track_latency("op"):
            time.sleep(0.01)

        with metrics.track_latency("op"):
            time.sleep(0.01)

        assert len(metrics.latencies["op"]) == 2

    def test_get_latency_stats(self):
        """get_latency_stats() should return correct statistics."""
        metrics = MetricsCollector()

        with metrics.track_latency("op"):
            time.sleep(0.01)

        with metrics.track_latency("op"):
            time.sleep(0.02)

        stats = metrics.get_latency_stats("op")
        assert stats["count"] == 2
        assert stats["avg_ms"] >= 15  # Average of 10ms and 20ms
        assert stats["min_ms"] >= 10
        assert stats["max_ms"] >= 20
        assert stats["total_ms"] >= 30

    def test_get_latency_stats_empty(self):
        """get_latency_stats() should return zeros for unknown operation."""
        metrics = MetricsCollector()
        stats = metrics.get_latency_stats("nonexistent")

        assert stats["count"] == 0
        assert stats["avg_ms"] == 0.0
        assert stats["min_ms"] == 0.0
        assert stats["max_ms"] == 0.0
        assert stats["total_ms"] == 0.0


class TestToolUsageTracking:
    """Test tool usage tracking."""

    def test_track_tool_usage_single(self):
        """track_tool_usage() should increment count."""
        metrics = MetricsCollector()
        metrics.track_tool_usage("pos_search_project")

        assert metrics.tool_usage["pos_search_project"] == 1

    def test_track_tool_usage_multiple_calls(self):
        """track_tool_usage() should accumulate counts."""
        metrics = MetricsCollector()
        metrics.track_tool_usage("pos_search_project")
        metrics.track_tool_usage("pos_search_project")
        metrics.track_tool_usage("pos_search_project")

        assert metrics.tool_usage["pos_search_project"] == 3

    def test_track_tool_usage_different_tools(self):
        """track_tool_usage() should track different tools separately."""
        metrics = MetricsCollector()
        metrics.track_tool_usage("pos_search_project")
        metrics.track_tool_usage("pos_workflow")
        metrics.track_tool_usage("pos_search_project")

        assert metrics.tool_usage["pos_search_project"] == 2
        assert metrics.tool_usage["pos_workflow"] == 1


class TestWorkflowGateTracking:
    """Test workflow gate tracking."""

    def test_track_workflow_gate(self):
        """track_workflow_gate() should record gate passage."""
        metrics = MetricsCollector()
        metrics.track_workflow_gate("s1", phase=1, passed=True)

        assert metrics.workflow_gates["s1"][1] is True

    def test_track_workflow_gate_failure(self):
        """track_workflow_gate() should record gate failure."""
        metrics = MetricsCollector()
        metrics.track_workflow_gate("s1", phase=2, passed=False)

        assert metrics.workflow_gates["s1"][2] is False

    def test_track_workflow_gate_multiple_phases(self):
        """track_workflow_gate() should track multiple phases."""
        metrics = MetricsCollector()
        metrics.track_workflow_gate("s1", phase=1, passed=True)
        metrics.track_workflow_gate("s1", phase=2, passed=True)
        metrics.track_workflow_gate("s1", phase=3, passed=False)

        assert metrics.workflow_gates["s1"][1] is True
        assert metrics.workflow_gates["s1"][2] is True
        assert metrics.workflow_gates["s1"][3] is False

    def test_get_workflow_adherence_perfect(self):
        """get_workflow_adherence() should return 1.0 for all gates passed."""
        metrics = MetricsCollector()
        metrics.track_workflow_gate("s1", 1, True)
        metrics.track_workflow_gate("s1", 2, True)
        metrics.track_workflow_gate("s1", 3, True)

        adherence = metrics.get_workflow_adherence("s1")
        assert adherence["gates_attempted"] == 3
        assert adherence["gates_passed"] == 3
        assert adherence["adherence_rate"] == 1.0
        assert adherence["failed_phases"] == []

    def test_get_workflow_adherence_with_failures(self):
        """get_workflow_adherence() should calculate correctly with failures."""
        metrics = MetricsCollector()
        metrics.track_workflow_gate("s1", 1, True)
        metrics.track_workflow_gate("s1", 2, False)
        metrics.track_workflow_gate("s1", 3, True)

        adherence = metrics.get_workflow_adherence("s1")
        assert adherence["gates_attempted"] == 3
        assert adherence["gates_passed"] == 2
        assert adherence["adherence_rate"] == 2 / 3
        assert adherence["failed_phases"] == [2]

    def test_get_workflow_adherence_empty(self):
        """get_workflow_adherence() should return defaults for empty session."""
        metrics = MetricsCollector()
        adherence = metrics.get_workflow_adherence("nonexistent")

        assert adherence["gates_attempted"] == 0
        assert adherence["gates_passed"] == 0
        assert adherence["adherence_rate"] == 1.0
        assert adherence["failed_phases"] == []


class TestMetricsSummary:
    """Test metrics summary functionality."""

    def test_get_summary_empty(self):
        """get_summary() should return empty summary for new collector."""
        metrics = MetricsCollector()
        summary = metrics.get_summary()

        assert "timestamp" in summary
        assert "query_metrics" in summary
        assert "latency_metrics" in summary
        assert "tool_usage" in summary
        assert "workflow_metrics" in summary

    def test_get_summary_with_data(self):
        """get_summary() should include all tracked metrics."""
        metrics = MetricsCollector()

        # Track some data
        metrics.track_query("Query A", session_id="s1")
        metrics.track_tool_usage("pos_search_project")
        with metrics.track_latency("search"):
            time.sleep(0.01)

        summary = metrics.get_summary()

        assert "s1" in summary["query_metrics"]
        assert "pos_search_project" in summary["tool_usage"]
        assert "search" in summary["latency_metrics"]


class TestSessionReset:
    """Test session reset functionality."""

    def test_reset_session_queries(self):
        """reset_session() should clear queries for session."""
        metrics = MetricsCollector()
        metrics.track_query("Query", session_id="s1")
        metrics.track_query("Query", session_id="s2")

        metrics.reset_session("s1")

        assert "s1" not in metrics.queries
        assert "s2" in metrics.queries

    def test_reset_session_workflow_gates(self):
        """reset_session() should clear workflow gates for session."""
        metrics = MetricsCollector()
        metrics.track_workflow_gate("s1", 1, True)
        metrics.track_workflow_gate("s2", 1, True)

        metrics.reset_session("s1")

        assert "s1" not in metrics.workflow_gates
        assert "s2" in metrics.workflow_gates

    def test_reset_session_preserves_global_metrics(self):
        """reset_session() should preserve latency and tool usage."""
        metrics = MetricsCollector()
        metrics.track_tool_usage("tool1")
        with metrics.track_latency("op1"):
            time.sleep(0.01)

        metrics.reset_session("s1")

        assert "tool1" in metrics.tool_usage
        assert "op1" in metrics.latencies


class TestMetricsIntegration:
    """Test integration of multiple metrics."""

    def test_complete_workflow_tracking(self):
        """Test tracking complete workflow with all metrics."""
        metrics = MetricsCollector()

        # Track queries
        metrics.track_query("How does X work?", session_id="s1")
        metrics.track_query("What is Y?", session_id="s1")

        # Track tool usage
        metrics.track_tool_usage("pos_search_project")
        metrics.track_tool_usage("pos_workflow")

        # Track latency
        with metrics.track_latency("search_standards"):
            time.sleep(0.01)

        # Track workflow gates
        metrics.track_workflow_gate("s1", 1, True)
        metrics.track_workflow_gate("s1", 2, True)

        # Get summary
        summary = metrics.get_summary()

        assert summary["query_metrics"]["s1"]["total"] == 2
        assert summary["tool_usage"]["pos_search_project"] == 1
        assert summary["latency_metrics"]["search_standards"]["count"] == 1
        assert summary["workflow_metrics"]["s1"]["gates_passed"] == 2
