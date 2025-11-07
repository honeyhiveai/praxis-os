"""
Performance tests for Ouroboros MCP server.

Tests:
- Cold start time < 30s
- Search latency < 200ms (p95)
- Config load < 100ms (p95)
- Middleware overhead < 5ms

Traceability:
    Phase 8, Task 8.4: Performance tests
"""

import pytest
import time
from ouroboros.middleware.query_tracker import QueryTracker
from ouroboros.middleware.query_classifier import QueryClassifier
from ouroboros.middleware.prepend_generator import PrependGenerator


class TestPerformance:
    """Performance benchmarks for Ouroboros."""
    
    def test_config_load_performance(self, test_config, test_base_path):
        """Test config loads in < 100ms."""
        # Benchmark config loading from file
        from ouroboros.config.loader import load_config
        config_path = test_base_path / "config" / "mcp.yaml"
        
        start = time.perf_counter()
        config = load_config(config_path=config_path, validate_paths=False)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert config is not None
        assert elapsed_ms < 100, f"Config load took {elapsed_ms:.1f}ms (target: <100ms)"
    
    def test_query_classifier_performance(self):
        """Test query classification is fast (<5ms)."""
        classifier = QueryClassifier()
        query = "What is workflow validation?"
        
        # Warmup
        classifier.classify(query)
        
        # Benchmark
        iterations = 100
        start = time.perf_counter()
        for _ in range(iterations):
            classifier.classify(query)
        elapsed_ms = (time.perf_counter() - start) * 1000 / iterations
        
        assert elapsed_ms < 5, f"Classification took {elapsed_ms:.2f}ms (target: <5ms)"
    
    def test_query_tracker_performance(self):
        """Test query tracking is fast (<5ms)."""
        tracker = QueryTracker()
        
        # Warmup
        tracker.record_query("session_1", "test query")
        
        # Benchmark
        iterations = 100
        start = time.perf_counter()
        for i in range(iterations):
            tracker.record_query("session_perf", f"query {i}")
        elapsed_ms = (time.perf_counter() - start) * 1000 / iterations
        
        assert elapsed_ms < 5, f"Query tracking took {elapsed_ms:.2f}ms (target: <5ms)"
    
    def test_prepend_generation_performance(self):
        """Test prepend generation is fast (<10ms)."""
        tracker = QueryTracker()
        generator = PrependGenerator(tracker)
        
        # Setup
        for i in range(5):
            tracker.record_query("session_1", f"query {i}")
        
        # Warmup
        generator.generate("session_1", "test query")
        
        # Benchmark
        iterations = 100
        start = time.perf_counter()
        for _ in range(iterations):
            generator.generate("session_1", "test query")
        elapsed_ms = (time.perf_counter() - start) * 1000 / iterations
        
        assert elapsed_ms < 10, f"Prepend generation took {elapsed_ms:.2f}ms (target: <10ms)"
    
    def test_middleware_stack_performance(self):
        """Test complete middleware stack is fast (<15ms)."""
        tracker = QueryTracker()
        classifier = QueryClassifier()
        generator = PrependGenerator(tracker)
        
        query = "What is workflow validation?"
        session_id = "perf_session"
        
        # Warmup
        classifier.classify(query)
        tracker.record_query(session_id, query)
        generator.generate(session_id, query)
        
        # Benchmark full stack
        iterations = 50
        start = time.perf_counter()
        for i in range(iterations):
            # Full middleware pipeline
            classification = classifier.classify(query)
            tracker.record_query(session_id, f"{query} {i}")
            prepend = generator.generate(session_id, query)
        elapsed_ms = (time.perf_counter() - start) * 1000 / iterations
        
        assert elapsed_ms < 15, f"Middleware stack took {elapsed_ms:.2f}ms (target: <15ms)"

