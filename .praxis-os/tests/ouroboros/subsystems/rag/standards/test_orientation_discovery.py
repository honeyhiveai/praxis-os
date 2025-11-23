"""
Tests for OrientationDiscoveryHandler.

Tests discovery of orientation queries from both standards index and config.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from ouroboros.subsystems.rag.standards.orientation import OrientationDiscoveryHandler
from ouroboros.config.schemas.orientation import OrientationQuery, ProjectOrientation, ProjectConfig


class TestOrientationDiscoveryHandlerInstantiation:
    """Test OrientationDiscoveryHandler instantiation."""
    
    def test_valid_instantiation(self):
        """
        Test OrientationDiscoveryHandler with valid dependencies.
        
        Validates:
            - Constructor accepts standards_index and config
            - Stores references correctly
            - Creates parser instance
        
        Acceptance Criterion: Task 3.1 - OrientationDiscoveryHandler class exists with __init__
        """
        # Create mocks
        standards_index = Mock()
        config = Mock()
        
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        assert handler.standards_index is standards_index
        assert handler.config is config
        assert handler.parser is not None
    
    def test_none_standards_index_raises_error(self):
        """
        Test that None standards_index raises TypeError.
        
        Validates:
            - Constructor validates standards_index is not None
            - Clear error message
        """
        config = Mock()
        
        with pytest.raises(TypeError) as exc_info:
            OrientationDiscoveryHandler(None, config)
        
        assert "standards_index" in str(exc_info.value).lower()
    
    def test_none_config_raises_error(self):
        """
        Test that None config raises TypeError.
        
        Validates:
            - Constructor validates config is not None
            - Clear error message
        """
        standards_index = Mock()
        
        with pytest.raises(TypeError) as exc_info:
            OrientationDiscoveryHandler(standards_index, None)
        
        assert "config" in str(exc_info.value).lower()


class TestDiscoverFromStandards:
    """Test _discover_from_standards() method."""
    
    def test_discover_from_standards_with_results(self):
        """
        Test discovering queries from standards index.
        
        Validates:
            - Queries standards index with orientation filter
            - Parses metadata from results
            - Returns List[OrientationQuery]
        
        Acceptance Criterion: Task 3.1 - Discovers queries from standards index
        """
        # Create mock standards index
        standards_index = Mock()
        
        # Mock search results
        mock_result = Mock()
        mock_result.content = '**Metadata**: query="test query", priority=1'
        mock_result.file_path = 'test.md'
        
        standards_index.search.return_value = [mock_result]
        
        # Create mock config
        config = Mock()
        config.project = None
        
        # Create handler and discover
        handler = OrientationDiscoveryHandler(standards_index, config)
        queries = handler._discover_from_standards()
        
        # Validate
        assert isinstance(queries, list)
        assert len(queries) == 1
        assert queries[0].query == "test query"
        assert queries[0].priority == 1
    
    def test_discover_from_standards_no_results(self):
        """
        Test discovering when standards index returns no results.
        
        Validates:
            - Empty list returned gracefully
            - No exceptions raised
        
        Acceptance Criterion: Task 3.1 - Empty list returned when no orientation defined
        """
        # Create mock standards index with no results
        standards_index = Mock()
        standards_index.search.return_value = []
        
        config = Mock()
        config.project = None
        
        handler = OrientationDiscoveryHandler(standards_index, config)
        queries = handler._discover_from_standards()
        
        assert queries == []
    
    def test_discover_from_standards_invalid_metadata(self):
        """
        Test discovering with invalid/missing query in metadata.
        
        Validates:
            - Skips results without 'query' field
            - Returns partial results (other valid queries)
            - Logs warnings
        """
        standards_index = Mock()
        
        # Mock results: one valid, one missing query
        valid_result = Mock()
        valid_result.content = '**Metadata**: query="valid query", priority=1'
        valid_result.file_path = 'valid.md'
        
        invalid_result = Mock()
        invalid_result.content = '**Metadata**: priority=2'  # No query!
        invalid_result.file_path = 'invalid.md'
        
        standards_index.search.return_value = [valid_result, invalid_result]
        
        config = Mock()
        config.project = None
        
        handler = OrientationDiscoveryHandler(standards_index, config)
        queries = handler._discover_from_standards()
        
        # Only valid query should be returned
        assert len(queries) == 1
        assert queries[0].query == "valid query"


class TestDiscoverFromConfig:
    """Test _discover_from_config() method."""
    
    def test_discover_from_config_with_queries(self):
        """
        Test discovering queries from mcp.yaml config.
        
        Validates:
            - Extracts queries from config.project.orientation
            - Returns List[OrientationQuery]
        
        Acceptance Criterion: Task 3.1 - Discovers queries from mcp.yaml
        """
        standards_index = Mock()
        
        # Create mock config with project orientation
        config = Mock()
        config.project = Mock()
        config.project.orientation = Mock()
        config.project.orientation.enabled = True
        config.project.orientation.queries = [
            OrientationQuery(query="config query 1", priority=1),
            OrientationQuery(query="config query 2", priority=2)
        ]
        
        handler = OrientationDiscoveryHandler(standards_index, config)
        queries = handler._discover_from_config()
        
        assert len(queries) == 2
        assert queries[0].query == "config query 1"
        assert queries[1].query == "config query 2"
    
    def test_discover_from_config_no_project_section(self):
        """
        Test discovering when config has no project section.
        
        Validates:
            - Empty list returned gracefully
            - No exceptions raised
        
        Acceptance Criterion: Task 3.1 - Empty list returned when no orientation defined
        """
        standards_index = Mock()
        
        config = Mock()
        config.project = None  # No project section
        
        handler = OrientationDiscoveryHandler(standards_index, config)
        queries = handler._discover_from_config()
        
        assert queries == []
    
    def test_discover_from_config_disabled_orientation(self):
        """
        Test discovering when orientation is disabled in config.
        
        Validates:
            - Empty list returned when enabled=False
            - Respects enabled flag
        """
        standards_index = Mock()
        
        config = Mock()
        config.project = Mock()
        config.project.orientation = Mock()
        config.project.orientation.enabled = False  # Disabled!
        config.project.orientation.queries = [
            OrientationQuery(query="disabled query", priority=1)
        ]
        
        handler = OrientationDiscoveryHandler(standards_index, config)
        queries = handler._discover_from_config()
        
        # Should return empty list when disabled
        assert queries == []
    
    def test_discover_from_config_no_orientation_section(self):
        """
        Test discovering when project section exists but no orientation.
        
        Validates:
            - Empty list returned gracefully
            - Handles partial config structure
        """
        standards_index = Mock()
        
        config = Mock()
        config.project = Mock()
        config.project.orientation = None  # No orientation section
        
        handler = OrientationDiscoveryHandler(standards_index, config)
        queries = handler._discover_from_config()
        
        assert queries == []


class TestDiscoverOrientationQueries:
    """Test discover_orientation_queries() main method."""
    
    def test_discover_from_both_sources(self):
        """
        Test discovering and merging queries from both sources.
        
        Validates:
            - Discovers from standards
            - Discovers from config
            - Merges into single list
            - Returns List[OrientationQuery]
        
        Acceptance Criterion: Task 3.1 - Returns List[OrientationQuery] from both sources merged
        """
        # Mock standards index with one result
        standards_index = Mock()
        mock_result = Mock()
        mock_result.content = '**Metadata**: query="standards query", priority=1'
        mock_result.file_path = 'standards.md'
        standards_index.search.return_value = [mock_result]
        
        # Mock config with one query
        config = Mock()
        config.project = Mock()
        config.project.orientation = Mock()
        config.project.orientation.enabled = True
        config.project.orientation.queries = [
            OrientationQuery(query="config query", priority=2)
        ]
        
        handler = OrientationDiscoveryHandler(standards_index, config)
        queries = handler.discover_orientation_queries()
        
        # Should have 2 queries (1 from each source)
        assert len(queries) == 2
        # After sorting: priority 1 first, then priority 2
        assert queries[0].query == "standards query"  # priority 1
        assert queries[0].priority == 1
        assert queries[1].query == "config query"  # priority 2
        assert queries[1].priority == 2
    
    def test_discover_empty_when_no_sources(self):
        """
        Test discovering when both sources are empty.
        
        Validates:
            - Empty list returned gracefully
            - No exceptions raised
        
        Acceptance Criterion: Task 3.1 - Empty list returned when no orientation defined
        """
        # Empty standards
        standards_index = Mock()
        standards_index.search.return_value = []
        
        # Empty config
        config = Mock()
        config.project = None
        
        handler = OrientationDiscoveryHandler(standards_index, config)
        queries = handler.discover_orientation_queries()
        
        assert queries == []
    
    def test_discover_continues_on_standards_error(self):
        """
        Test that discovery continues if standards source fails.
        
        Validates:
            - Standards error logged but doesn't crash
            - Config queries still returned
            - Graceful error handling
        """
        # Standards raises exception
        standards_index = Mock()
        standards_index.search.side_effect = Exception("Standards error")
        
        # Config has queries
        config = Mock()
        config.project = Mock()
        config.project.orientation = Mock()
        config.project.orientation.enabled = True
        config.project.orientation.queries = [
            OrientationQuery(query="config query", priority=1)
        ]
        
        handler = OrientationDiscoveryHandler(standards_index, config)
        queries = handler.discover_orientation_queries()
        
        # Should still return config queries
        assert len(queries) == 1
        assert queries[0].query == "config query"
    
    def test_discover_continues_on_config_error(self):
        """
        Test that discovery continues if config source fails.
        
        Validates:
            - Config error logged but doesn't crash
            - Standards queries still returned
            - Graceful error handling
        """
        # Standards has queries
        standards_index = Mock()
        mock_result = Mock()
        mock_result.content = '**Metadata**: query="standards query", priority=1'
        mock_result.file_path = 'test.md'
        standards_index.search.return_value = [mock_result]
        
        # Config raises exception when accessed
        config = Mock()
        # Make config.project raise an exception
        type(config).project = property(lambda self: (_ for _ in ()).throw(Exception("Config error")))
        
        handler = OrientationDiscoveryHandler(standards_index, config)
        queries = handler.discover_orientation_queries()
        
        # Should still return standards queries
        assert len(queries) == 1
        assert queries[0].query == "standards query"


class TestMergeSources:
    """Test _merge_sources() deduplication logic."""
    
    def test_merge_no_duplicates(self):
        """
        Test merging queries with no duplicates.
        
        Validates:
            - All queries from both sources preserved
            - Config queries appear first
            - Standards queries appear second
        
        Acceptance Criterion: Task 3.2 - Returns merged List[OrientationQuery] without duplicates
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        standards_queries = [
            OrientationQuery(query="standards query 1", priority=1),
            OrientationQuery(query="standards query 2", priority=2)
        ]
        
        config_queries = [
            OrientationQuery(query="config query", priority=1)
        ]
        
        merged = handler._merge_sources(standards_queries, config_queries)
        
        # Should have all 3 queries (no duplicates)
        assert len(merged) == 3
        
        # Config queries first
        assert merged[0].query == "config query"
        
        # Standards queries second
        assert merged[1].query == "standards query 1"
        assert merged[2].query == "standards query 2"
    
    def test_merge_with_duplicates_config_wins(self):
        """
        Test merging with duplicates - config takes precedence.
        
        Validates:
            - Duplicate removed (only one copy)
            - Config version preserved (not standards)
            - Config metadata used (priority, description)
        
        Acceptance Criterion: Task 3.2 - Duplicate query: mcp.yaml config takes precedence
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        standards_queries = [
            OrientationQuery(
                query="duplicate query",
                priority=2,
                description="From standards"
            ),
            OrientationQuery(query="unique standards", priority=1)
        ]
        
        config_queries = [
            OrientationQuery(
                query="duplicate query",
                priority=1,
                description="From config"
            )
        ]
        
        merged = handler._merge_sources(standards_queries, config_queries)
        
        # Should have 2 queries (duplicate removed)
        assert len(merged) == 2
        
        # First query is config version (duplicate)
        assert merged[0].query == "duplicate query"
        assert merged[0].priority == 1  # Config priority
        assert merged[0].description == "From config"  # Config description
        
        # Second query is unique standards
        assert merged[1].query == "unique standards"
    
    def test_merge_complex_scenario(self):
        """
        Test complex merge: 5 inline + 3 config (2 duplicates) → 6 unique.
        
        Validates:
            - Correct deduplication count
            - All unique queries preserved
            - Config precedence maintained
        
        Acceptance Criterion: Task 3.2 - Test: 5 inline + 3 config (2 duplicates) → 6 unique queries
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        # 5 standards queries
        standards_queries = [
            OrientationQuery(query="standards 1", priority=1),
            OrientationQuery(query="standards 2", priority=2),
            OrientationQuery(query="duplicate A", priority=2),  # Duplicate
            OrientationQuery(query="standards 3", priority=1),
            OrientationQuery(query="duplicate B", priority=3),  # Duplicate
        ]
        
        # 3 config queries (2 are duplicates of standards)
        config_queries = [
            OrientationQuery(query="duplicate A", priority=1),  # Overrides standards
            OrientationQuery(query="config unique", priority=1),
            OrientationQuery(query="duplicate B", priority=1),  # Overrides standards
        ]
        
        merged = handler._merge_sources(standards_queries, config_queries)
        
        # Should have 6 unique queries (5 + 3 - 2 duplicates)
        assert len(merged) == 6
        
        # First 3 are config queries
        assert merged[0].query == "duplicate A"
        assert merged[0].priority == 1  # Config priority
        assert merged[1].query == "config unique"
        assert merged[2].query == "duplicate B"
        assert merged[2].priority == 1  # Config priority
        
        # Last 3 are unique standards queries
        assert merged[3].query == "standards 1"
        assert merged[4].query == "standards 2"
        assert merged[5].query == "standards 3"
    
    def test_merge_empty_standards(self):
        """
        Test merging with empty standards list.
        
        Validates:
            - Config queries returned unchanged
            - No exceptions
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        standards_queries = []
        config_queries = [
            OrientationQuery(query="config query", priority=1)
        ]
        
        merged = handler._merge_sources(standards_queries, config_queries)
        
        assert len(merged) == 1
        assert merged[0].query == "config query"
    
    def test_merge_empty_config(self):
        """
        Test merging with empty config list.
        
        Validates:
            - Standards queries returned unchanged
            - No exceptions
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        standards_queries = [
            OrientationQuery(query="standards query", priority=1)
        ]
        config_queries = []
        
        merged = handler._merge_sources(standards_queries, config_queries)
        
        assert len(merged) == 1
        assert merged[0].query == "standards query"
    
    def test_merge_both_empty(self):
        """
        Test merging with both sources empty.
        
        Validates:
            - Empty list returned
            - No exceptions
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        merged = handler._merge_sources([], [])
        
        assert merged == []


class TestSortByPriority:
    """Test _sort_by_priority() sorting logic."""
    
    def test_sort_mixed_priorities(self):
        """
        Test sorting with mixed priorities.
        
        Validates:
            - Priority 1 queries first
            - Priority 2 queries second
            - Priority 3 queries last
            - Definition order preserved within same priority
        
        Acceptance Criterion: Task 3.3 - Queries sorted by priority: all priority=1, then priority=2, then priority=3
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        unsorted = [
            OrientationQuery(query="third", priority=3),
            OrientationQuery(query="first A", priority=1),
            OrientationQuery(query="second A", priority=2),
            OrientationQuery(query="first B", priority=1),
            OrientationQuery(query="second B", priority=2)
        ]
        
        sorted_queries = handler._sort_by_priority(unsorted)
        
        # Should have all queries
        assert len(sorted_queries) == 5
        
        # Priority 1 first (both in order)
        assert sorted_queries[0].query == "first A"
        assert sorted_queries[0].priority == 1
        assert sorted_queries[1].query == "first B"
        assert sorted_queries[1].priority == 1
        
        # Priority 2 second (both in order)
        assert sorted_queries[2].query == "second A"
        assert sorted_queries[2].priority == 2
        assert sorted_queries[3].query == "second B"
        assert sorted_queries[3].priority == 2
        
        # Priority 3 last
        assert sorted_queries[4].query == "third"
        assert sorted_queries[4].priority == 3
    
    def test_sort_preserves_definition_order(self):
        """
        Test that sorting preserves order within same priority.
        
        Validates:
            - Stable sort (same priority keeps original order)
            - Definition order maintained
        
        Acceptance Criterion: Task 3.3 - Within same priority, definition order preserved
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        # All same priority
        unsorted = [
            OrientationQuery(query="first", priority=2),
            OrientationQuery(query="second", priority=2),
            OrientationQuery(query="third", priority=2),
            OrientationQuery(query="fourth", priority=2)
        ]
        
        sorted_queries = handler._sort_by_priority(unsorted)
        
        # Order should be preserved (stable sort)
        assert sorted_queries[0].query == "first"
        assert sorted_queries[1].query == "second"
        assert sorted_queries[2].query == "third"
        assert sorted_queries[3].query == "fourth"
    
    def test_sort_example_from_spec(self):
        """
        Test sorting with example from spec: [p3, p1, p2, p1] → [p1, p1, p2, p3].
        
        Validates:
            - Correct sort order
            - Same priorities grouped together
        
        Acceptance Criterion: Task 3.3 - Test: [p3, p1, p2, p1] → [p1, p1, p2, p3]
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        unsorted = [
            OrientationQuery(query="p3 query", priority=3),
            OrientationQuery(query="p1 query A", priority=1),
            OrientationQuery(query="p2 query", priority=2),
            OrientationQuery(query="p1 query B", priority=1)
        ]
        
        sorted_queries = handler._sort_by_priority(unsorted)
        
        # Should be: p1, p1, p2, p3
        assert sorted_queries[0].priority == 1
        assert sorted_queries[1].priority == 1
        assert sorted_queries[2].priority == 2
        assert sorted_queries[3].priority == 3
        
        # Verify queries match
        assert sorted_queries[0].query == "p1 query A"
        assert sorted_queries[1].query == "p1 query B"
        assert sorted_queries[2].query == "p2 query"
        assert sorted_queries[3].query == "p3 query"
    
    def test_sort_empty_list(self):
        """
        Test sorting empty list.
        
        Validates:
            - Empty list returns empty list
            - No exceptions
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        sorted_queries = handler._sort_by_priority([])
        
        assert sorted_queries == []
    
    def test_sort_single_query(self):
        """
        Test sorting with single query.
        
        Validates:
            - Single query returned unchanged
            - No exceptions
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        unsorted = [OrientationQuery(query="only query", priority=2)]
        sorted_queries = handler._sort_by_priority(unsorted)
        
        assert len(sorted_queries) == 1
        assert sorted_queries[0].query == "only query"
    
    def test_discover_returns_sorted_queries(self):
        """
        Test that discover_orientation_queries() returns sorted queries.
        
        Validates:
            - End-to-end: discovery → merge → sort
            - Final result is sorted by priority
        
        Acceptance Criterion: Task 3.3 - Returns sorted List[OrientationQuery]
        """
        # Mock standards with mixed priorities
        standards_index = Mock()
        mock_result1 = Mock()
        mock_result1.content = '**Metadata**: query="standards p2", priority=2'
        mock_result1.file_path = 'test1.md'
        
        mock_result2 = Mock()
        mock_result2.content = '**Metadata**: query="standards p1", priority=1'
        mock_result2.file_path = 'test2.md'
        
        standards_index.search.return_value = [mock_result1, mock_result2]
        
        # Mock config with mixed priorities
        config = Mock()
        config.project = Mock()
        config.project.orientation = Mock()
        config.project.orientation.enabled = True
        config.project.orientation.queries = [
            OrientationQuery(query="config p3", priority=3),
            OrientationQuery(query="config p1", priority=1)
        ]
        
        handler = OrientationDiscoveryHandler(standards_index, config)
        queries = handler.discover_orientation_queries()
        
        # Should be sorted: p1, p1, p2, p3
        assert len(queries) == 4
        assert queries[0].priority == 1
        assert queries[1].priority == 1
        assert queries[2].priority == 2
        assert queries[3].priority == 3


class TestResolveDependencies:
    """Test _resolve_dependencies() topological sorting."""
    
    def test_linear_dependency_chain(self):
        """
        Test resolving linear dependency chain: A→B→C resolves to [C, B, A].
        
        Validates:
            - Linear dependencies resolve correctly
            - Dependent queries execute after dependencies
            - Order is topologically sorted
        
        Acceptance Criterion: Task 3.6 - Test: A→B→C resolves to [C, B, A] execution order
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        queries = [
            OrientationQuery(query="query A", priority=1, depends_on=["query B"]),
            OrientationQuery(query="query B", priority=1, depends_on=["query C"]),
            OrientationQuery(query="query C", priority=1)
        ]
        
        resolved = handler._resolve_dependencies(queries)
        
        # Should be [C, B, A] - dependencies first
        assert len(resolved) == 3
        assert resolved[0].query == "query C"  # No dependencies
        assert resolved[1].query == "query B"  # Depends on C
        assert resolved[2].query == "query A"  # Depends on B
    
    def test_no_dependencies_returns_original_order(self):
        """
        Test that queries without dependencies maintain original order.
        
        Validates:
            - No dependencies → original order preserved
            - No exceptions raised
        
        Acceptance Criterion: Task 3.6 - No dependencies → returns original order
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        queries = [
            OrientationQuery(query="query 1", priority=1),
            OrientationQuery(query="query 2", priority=2),
            OrientationQuery(query="query 3", priority=3)
        ]
        
        resolved = handler._resolve_dependencies(queries)
        
        # Order should be preserved
        assert resolved[0].query == "query 1"
        assert resolved[1].query == "query 2"
        assert resolved[2].query == "query 3"
    
    def test_complex_dependency_graph(self):
        """
        Test resolving complex dependency graph with multiple branches.
        
        Validates:
            - Complex dependencies resolve correctly
            - Multiple dependencies per query work
            - All dependencies execute before dependents
        
        Acceptance Criterion: Task 3.6 - Dependencies resolve correctly: A depends on B → B executes before A
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        # Graph:
        #   D depends on [B, C]
        #   B depends on [A]
        #   C depends on [A]
        #   A has no dependencies
        # Valid order: A, then B and C (either order), then D
        queries = [
            OrientationQuery(query="query D", priority=1, depends_on=["query B", "query C"]),
            OrientationQuery(query="query B", priority=1, depends_on=["query A"]),
            OrientationQuery(query="query C", priority=1, depends_on=["query A"]),
            OrientationQuery(query="query A", priority=1)
        ]
        
        resolved = handler._resolve_dependencies(queries)
        
        # A should be first
        assert resolved[0].query == "query A"
        
        # B and C should be next (either order)
        middle_queries = {resolved[1].query, resolved[2].query}
        assert middle_queries == {"query B", "query C"}
        
        # D should be last (depends on both B and C)
        assert resolved[3].query == "query D"
    
    def test_circular_dependency_raises_error(self):
        """
        Test that circular dependencies raise ValueError.
        
        Validates:
            - Circular dependency detected
            - Error message includes cycle description
            - Clear remediation guidance
        
        Acceptance Criterion: Task 3.6 - Circular dependencies raise ValueError with cycle description
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        # Circular: A → B → A
        queries = [
            OrientationQuery(query="query A", priority=1, depends_on=["query B"]),
            OrientationQuery(query="query B", priority=1, depends_on=["query A"])
        ]
        
        with pytest.raises(ValueError) as exc_info:
            handler._resolve_dependencies(queries)
        
        error_msg = str(exc_info.value).lower()
        assert "circular" in error_msg
        assert "dependency" in error_msg
        # Should mention the queries involved
        assert "query a" in error_msg or "query b" in error_msg
    
    def test_self_dependency_caught_by_pydantic(self):
        """
        Test that self-dependency (A depends on A) is caught by Pydantic validation.
        
        Validates:
            - Self-circular dependency caught at query creation
            - Pydantic validator prevents invalid query
        
        Note: This is caught by OrientationQuery validation, not dependency resolution.
        """
        from pydantic import ValidationError
        
        # Self-circular: A → A
        # This should fail at query creation (Pydantic validation)
        with pytest.raises(ValidationError) as exc_info:
            OrientationQuery(query="query A", priority=1, depends_on=["query A"])
        
        error_msg = str(exc_info.value).lower()
        assert "circular" in error_msg or "itself" in error_msg
    
    def test_missing_dependency_ignored(self, caplog):
        """
        Test that missing dependencies are ignored with warning.
        
        Validates:
            - Query depending on non-existent query doesn't crash
            - Warning logged
            - Execution continues
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        queries = [
            OrientationQuery(query="query A", priority=1, depends_on=["query MISSING"]),
            OrientationQuery(query="query B", priority=1)
        ]
        
        with caplog.at_level("WARNING"):
            resolved = handler._resolve_dependencies(queries)
        
        # Should complete successfully
        assert len(resolved) == 2
        
        # Warning logged about missing dependency
        assert any("query MISSING" in record.message for record in caplog.records)
    
    def test_empty_list_returns_empty(self):
        """
        Test that empty query list returns empty.
        
        Validates:
            - Empty list handled gracefully
            - No exceptions
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        resolved = handler._resolve_dependencies([])
        
        assert resolved == []
    
    def test_topological_sort_returns_list(self):
        """
        Test that dependency resolution returns List[OrientationQuery].
        
        Validates:
            - Return type is list
            - All queries present in result
            - Order respects dependencies
        
        Acceptance Criterion: Task 3.6 - Returns topologically sorted List[OrientationQuery]
        """
        standards_index = Mock()
        config = Mock()
        handler = OrientationDiscoveryHandler(standards_index, config)
        
        queries = [
            OrientationQuery(query="query 1", priority=1),
            OrientationQuery(query="query 2", priority=1, depends_on=["query 1"])
        ]
        
        resolved = handler._resolve_dependencies(queries)
        
        # Return type check
        assert isinstance(resolved, list)
        assert all(isinstance(q, OrientationQuery) for q in resolved)
        
        # All queries present
        assert len(resolved) == 2
        
        # Dependencies respected
        assert resolved[0].query == "query 1"
        assert resolved[1].query == "query 2"

