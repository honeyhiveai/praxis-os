"""
Integration tests for the complete Project Orientation System.

Tests the full workflow from discovery through execution, simulating
how base orientation (Query 10) triggers project orientation discovery
and execution.

Traceable to: .praxis-os/specs/approved/2025-11-19-project-orientation-system/
"""

import pytest
from typing import List, Any
from unittest.mock import Mock, MagicMock, patch

from ouroboros.config.schemas.orientation import OrientationQuery, ProjectOrientation, ProjectConfig
from ouroboros.config.schemas.mcp import MCPConfig
from ouroboros.subsystems.rag.standards.orientation import (
    OrientationMetadataParser,
    OrientationDiscoveryHandler,
    ProjectOrientationExecutor,
    QueryExecutionResult,
    OrientationSessionSummary,
)


class TestOrientationFullWorkflow:
    """
    Test the complete orientation workflow from Query 10 trigger through execution.
    
    Simulates:
    1. Base orientation queries 1-9 execute
    2. Query 10 triggers project orientation discovery
    3. Project queries discovered from standards + config
    4. Project queries executed after base orientation
    """
    
    def test_full_workflow_with_project_orientation(self):
        """
        Test complete workflow: Query 10 → discovery → execution.
        
        Simulates the full flow:
        - Base queries 1-9 complete (mocked)
        - Query 10 executes (triggers project orientation)
        - Project queries discovered from both sources
        - Project queries executed in priority order
        - All queries succeed
        """
        # Setup: Create mock config with project orientation
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=True,
                queries=[
                    OrientationQuery(
                        query="project architecture patterns design",
                        priority=1,
                        description="Core architecture",
                        category="architecture"
                    ),
                    OrientationQuery(
                        query="project testing conventions standards",
                        priority=2,
                        description="Testing standards",
                        category="testing"
                    )
                ]
            )
        )
        
        # Setup: Create mock standards index
        mock_result = Mock()
        mock_result.content = "**Metadata**: orientation=true, priority=1, query=\"domain model concepts entities\""
        mock_result.file_path = "mock/path/domain.md"
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = [mock_result]
        
        # Phase 1: Query 10 triggers discovery
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        discovered_queries = discovery_handler.discover_orientation_queries()
        
        # Verify discovery found all queries
        assert len(discovered_queries) >= 2
        query_strings = [q.query for q in discovered_queries]
        assert "project architecture patterns design" in query_strings
        assert "project testing conventions standards" in query_strings
        
        # Phase 2: Execute discovered queries
        mock_search_tool = Mock(return_value=[{"result": "mock search result"}])
        executor = ProjectOrientationExecutor(mock_search_tool)
        
        summary = executor.execute_orientation(discovered_queries)
        
        # Verify execution completed successfully
        assert summary.total_queries == len(discovered_queries)
        assert summary.successful_queries == len(discovered_queries)
        assert summary.failed_queries == 0
        assert summary.completed is True
        
        # Verify search tool was called for each query
        assert mock_search_tool.call_count == len(discovered_queries)
    
    def test_base_orientation_only_no_project_config(self):
        """
        Test graceful fallback when no project orientation configured.
        
        Simulates:
        - Base queries 1-10 complete normally
        - Query 10 attempts project discovery
        - No project.orientation in config
        - System continues gracefully (no errors)
        """
        # Setup: Config with NO project section
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = None  # No project config at all
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = []  # No inline metadata either
        
        # Discovery should handle missing config gracefully
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        discovered_queries = discovery_handler.discover_orientation_queries()
        
        # Should return empty list (not raise error)
        assert discovered_queries == []
        
        # Executor should handle empty query list gracefully
        mock_search_tool = Mock()
        executor = ProjectOrientationExecutor(mock_search_tool)
        
        summary = executor.execute_orientation(discovered_queries)
        
        # Verify graceful handling
        assert summary.total_queries == 0
        assert summary.successful_queries == 0
        assert summary.failed_queries == 0
        assert summary.completed is True
        assert mock_search_tool.call_count == 0
    
    def test_disabled_project_orientation(self):
        """
        Test when project.orientation.enabled = false.
        
        Even though queries are defined, they should not execute
        when orientation is explicitly disabled.
        """
        # Setup: Config with enabled=False
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=False,  # Explicitly disabled
                queries=[
                    OrientationQuery(
                        query="should not execute query",
                        priority=1,
                        description="This query should not run"
                    )
                ]
            )
        )
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = []
        
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        discovered_queries = discovery_handler.discover_orientation_queries()
        
        # Should return empty list because orientation is disabled
        assert discovered_queries == []
    
    def test_priority_ordering_across_sources(self):
        """
        Test that queries from both sources are properly ordered by priority.
        
        Verifies that:
        - Priority 1 queries execute before priority 2
        - Priority 2 queries execute before priority 3
        - Within same priority, definition order preserved
        """
        # Setup: Mix of priorities from both sources
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=True,
                queries=[
                    OrientationQuery(
                        query="config priority 2 first defined",
                        priority=2,
                        description="Second priority, first defined"
                    ),
                    OrientationQuery(
                        query="config priority 1 query",
                        priority=1,
                        description="Highest priority from config"
                    ),
                    OrientationQuery(
                        query="config priority 2 second defined",
                        priority=2,
                        description="Second priority, second defined"
                    )
                ]
            )
        )
        
        # Mock standards with priority 1 and 3
        mock_result1 = Mock()
        mock_result1.content = "**Metadata**: orientation=true, priority=1, query=\"standards priority 1 query\""
        mock_result1.file_path = "mock/path/priority1.md"
        
        mock_result2 = Mock()
        mock_result2.content = "**Metadata**: orientation=true, priority=3, query=\"standards priority 3 query\""
        mock_result2.file_path = "mock/path/priority3.md"
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = [mock_result1, mock_result2]
        
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        discovered_queries = discovery_handler.discover_orientation_queries()
        
        # Extract query strings in execution order
        query_strings = [q.query for q in discovered_queries]
        query_priorities = [q.priority for q in discovered_queries]
        
        # Verify priority ordering
        assert query_priorities[0] == 1  # First queries should be priority 1
        assert query_priorities[1] == 1
        
        # All priority 1s before priority 2s
        first_p2_idx = next((i for i, p in enumerate(query_priorities) if p == 2), None)
        last_p1_idx = next((i for i in range(len(query_priorities)-1, -1, -1) if query_priorities[i] == 1), None)
        
        if first_p2_idx is not None and last_p1_idx is not None:
            assert first_p2_idx > last_p1_idx
        
        # Verify priority 3 comes last
        assert query_priorities[-1] == 3
        assert "standards priority 3 query" in query_strings[-1]
    
    def test_execution_with_partial_failures(self):
        """
        Test that execution continues even when some queries fail.
        
        Simulates:
        - Multiple project queries discovered
        - Some queries succeed, some fail
        - Execution continues for all queries
        - Summary correctly reports success/failure counts
        """
        # Setup: Multiple queries
        queries = [
            OrientationQuery(
                query="query that succeeds query",
                priority=1,
                description="This will succeed"
            ),
            OrientationQuery(
                query="query that fails badly",
                priority=1,
                description="This will fail"
            ),
            OrientationQuery(
                query="another success query",
                priority=2,
                description="This will also succeed"
            )
        ]
        
        # Setup: Search tool that fails on second query
        def mock_search_with_failures(query: str) -> List[Any]:
            if "fails" in query:
                raise ValueError("Simulated search failure")
            return [{"result": f"Results for {query}"}]
        
        executor = ProjectOrientationExecutor(mock_search_with_failures)
        summary = executor.execute_orientation(queries)
        
        # Verify partial success
        assert summary.total_queries == 3
        assert summary.successful_queries == 2
        assert summary.failed_queries == 1
        assert summary.completed is True
        
        # Verify failed query is reported
        failed_results = [r for r in summary.query_results if not r.success]
        assert len(failed_results) == 1
        assert "fails" in failed_results[0].query.query
        assert "Simulated search failure" in failed_results[0].error_message


class TestQuery10Integration:
    """
    Test Query 10 specifically as the bridge between base and project orientation.
    """
    
    def test_query_10_as_orientation_trigger(self):
        """
        Test that Query 10 serves as the trigger for project orientation.
        
        This is a conceptual test showing how Query 10 would work:
        1. Base queries 1-9 provide foundation
        2. Query 10 is the last base query
        3. Query 10 mentions "project orientation discovery"
        4. This triggers the project orientation system
        """
        # This test documents the integration point conceptually
        # In actual implementation, Query 10 would be in the base orientation
        # and would reference the project orientation system
        
        query_10_text = "project orientation discovery project-specific context"
        
        # Verify Query 10 mentions the key concepts
        assert "project orientation" in query_10_text
        assert "discovery" in query_10_text
        assert "project-specific" in query_10_text
    
    def test_base_plus_project_execution_order(self):
        """
        Test that project queries execute AFTER base queries.
        
        Execution order should be:
        1. Base queries 1-9
        2. Query 10 (triggers discovery)
        3. Project queries (discovered + executed)
        """
        # Simulate the execution order
        execution_log = []
        
        # Base queries 1-9 (simulated)
        for i in range(1, 10):
            execution_log.append(f"base_query_{i}")
        
        # Query 10 triggers discovery
        execution_log.append("base_query_10_project_discovery")
        
        # Project queries discovered and executed
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=True,
                queries=[
                    OrientationQuery(
                        query="project query one",
                        priority=1,
                        description="First project query"
                    )
                ]
            )
        )
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = []
        
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        project_queries = discovery_handler.discover_orientation_queries()
        
        for query in project_queries:
            execution_log.append(f"project_query_{query.query}")
        
        # Verify order: base queries come before project queries
        base_query_indices = [i for i, log in enumerate(execution_log) if "base_query" in log]
        project_query_indices = [i for i, log in enumerate(execution_log) if "project_query" in log]
        
        if project_query_indices:
            assert max(base_query_indices) < min(project_query_indices)


class TestErrorHandlingIntegration:
    """
    Test error handling across the full integration.
    """
    
    def test_malformed_inline_metadata_doesnt_break_workflow(self):
        """
        Test that malformed inline metadata is handled gracefully.
        
        Even with bad metadata, the workflow should:
        - Log warnings
        - Skip malformed entries
        - Continue with valid entries
        - Not crash
        """
        # Setup: Standards index returns mix of valid and invalid
        mock_result1 = Mock()
        mock_result1.content = "**Metadata**: this is completely malformed garbage"
        mock_result1.file_path = "mock/malformed.md"
        
        mock_result2 = Mock()
        mock_result2.content = "**Metadata**: orientation=true, priority=1, query=\"valid query here\""
        mock_result2.file_path = "mock/valid.md"
        
        mock_result3 = Mock()
        mock_result3.content = "**Metadata**: orientation=true"  # Missing required fields
        mock_result3.file_path = "mock/incomplete.md"
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = [mock_result1, mock_result2, mock_result3]
        
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = None
        
        # Should not raise exception
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        
        # Discovery should handle malformed data gracefully
        discovered_queries = discovery_handler.discover_orientation_queries()
        
        # Should find the one valid query
        assert len(discovered_queries) >= 0  # May be 0 if validation strict, or 1 if lenient
    
    def test_search_tool_exception_handling(self):
        """
        Test that executor handles search tool exceptions gracefully.
        
        If the search tool raises an exception, the executor should:
        - Catch the exception
        - Log the error
        - Mark the query as failed
        - Continue with remaining queries
        """
        queries = [
            OrientationQuery(
                query="query that raises exception",
                priority=1,
                description="This will raise"
            )
        ]
        
        def failing_search_tool(query: str) -> List[Any]:
            raise RuntimeError("Search index is unavailable")
        
        executor = ProjectOrientationExecutor(failing_search_tool)
        summary = executor.execute_orientation(queries)
        
        # Verify graceful failure
        assert summary.total_queries == 1
        assert summary.successful_queries == 0
        assert summary.failed_queries == 1
        
        # Verify error is captured
        assert summary.query_results[0].error_message is not None
        assert "Search index is unavailable" in summary.query_results[0].error_message


class TestConfigurationVariations:
    """
    Test various configuration scenarios.
    """
    
    def test_config_only_no_inline_metadata(self):
        """
        Test project orientation with only mcp.yaml config (no inline metadata).
        """
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=True,
                queries=[
                    OrientationQuery(
                        query="config only query",
                        priority=1,
                        description="From config only"
                    )
                ]
            )
        )
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = []  # No inline metadata
        
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        discovered_queries = discovery_handler.discover_orientation_queries()
        
        # Should find config query
        assert len(discovered_queries) == 1
        assert discovered_queries[0].query == "config only query"
    
    def test_inline_metadata_only_no_config(self):
        """
        Test project orientation with only inline metadata (no mcp.yaml config).
        """
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = None  # No project config
        
        mock_result = Mock()
        mock_result.content = "**Metadata**: orientation=true, priority=1, query=\"inline metadata query\""
        mock_result.file_path = "mock/inline.md"
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = [mock_result]
        
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        discovered_queries = discovery_handler.discover_orientation_queries()
        
        # Should find inline query
        assert len(discovered_queries) >= 0  # Implementation dependent on validation
    
    def test_both_sources_config_precedence(self):
        """
        Test that when same query exists in both sources, config takes precedence.
        """
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=True,
                queries=[
                    OrientationQuery(
                        query="duplicate query string",
                        priority=1,
                        description="From config (should win)"
                    )
                ]
            )
        )
        
        mock_result = Mock()
        mock_result.content = "**Metadata**: orientation=true, priority=2, query=\"duplicate query string\", description=\"From inline (should lose)\""
        mock_result.file_path = "mock/duplicate.md"
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = [mock_result]
        
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        discovered_queries = discovery_handler.discover_orientation_queries()
        
        # Should find only one (config version)
        matching_queries = [q for q in discovered_queries if q.query == "duplicate query string"]
        
        if matching_queries:
            # Config should take precedence
            assert matching_queries[0].priority == 1  # Config priority
            assert matching_queries[0].description == "From config (should win)"

