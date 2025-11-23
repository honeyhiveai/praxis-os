"""
Backward compatibility tests for Project Orientation System.

Ensures that the new project orientation features:
1. Don't break existing functionality
2. Work gracefully when not configured
3. Are fully optional
4. Maintain all existing behavior for projects without orientation

Traceable to: .praxis-os/specs/approved/2025-11-19-project-orientation-system/
"""

import pytest
from typing import Optional
from unittest.mock import Mock, MagicMock

from ouroboros.config.schemas.orientation import OrientationQuery, ProjectOrientation, ProjectConfig
from ouroboros.config.schemas.mcp import MCPConfig
from ouroboros.subsystems.rag.standards.orientation import (
    OrientationMetadataParser,
    OrientationDiscoveryHandler,
    ProjectOrientationExecutor,
)


class TestMissingProjectConfig:
    """
    Test that missing project config is handled gracefully.
    
    This ensures backward compatibility for projects that:
    - Don't have a [project] section in mcp.yaml
    - Don't know about project orientation
    - Expect the system to work exactly as before
    """
    
    def test_no_project_section_in_config(self):
        """
        Test when mcp.yaml has no [project] section at all.
        
        Expected behavior:
        - No errors or warnings
        - Discovery returns empty list
        - System continues normally
        """
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = None  # No project section
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = []
        
        # Should not raise any exceptions
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        queries = discovery_handler.discover_orientation_queries()
        
        # Should return empty list gracefully
        assert queries == []
    
    def test_no_orientation_section_in_project_config(self):
        """
        Test when [project] exists but [project.orientation] doesn't.
        
        Expected behavior:
        - No errors
        - Discovery returns empty list
        - System handles None gracefully
        """
        mock_config = Mock(spec=MCPConfig)
        # Project config exists but orientation is None
        mock_config.project = ProjectConfig(orientation=None)
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = []
        
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        queries = discovery_handler.discover_orientation_queries()
        
        # Should return empty list gracefully
        assert queries == []
    
    def test_orientation_disabled_explicitly(self):
        """
        Test when project.orientation.enabled = false.
        
        Expected behavior:
        - System respects the disabled flag
        - No queries executed
        - No errors
        """
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=False,
                queries=[]
            )
        )
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = []
        
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        queries = discovery_handler.discover_orientation_queries()
        
        # Should return empty list when disabled
        assert queries == []
    
    def test_executor_with_empty_queries(self):
        """
        Test executor handles empty query list gracefully.
        
        Expected behavior:
        - No crashes
        - Returns valid summary with zero queries
        - Search tool never called
        """
        mock_search_tool = Mock()
        executor = ProjectOrientationExecutor(mock_search_tool)
        
        summary = executor.execute_orientation([])
        
        # Verify graceful handling
        assert summary.total_queries == 0
        assert summary.successful_queries == 0
        assert summary.failed_queries == 0
        assert summary.completed is True
        assert mock_search_tool.call_count == 0


class TestExistingFunctionalityUnchanged:
    """
    Test that existing components work exactly as before.
    
    These tests verify that adding project orientation features
    didn't break any existing behavior.
    """
    
    def test_metadata_parser_instantiation_unchanged(self):
        """
        Test OrientationMetadataParser can still be instantiated.
        
        This is the core parsing component that existed before
        project orientation. Must continue to work.
        """
        parser = OrientationMetadataParser()
        
        # Should instantiate successfully
        assert parser is not None
        assert hasattr(parser, 'extract_inline_metadata')
        assert hasattr(parser, 'METADATA_PATTERN')
    
    def test_metadata_parser_behavior_unchanged(self):
        """
        Test metadata parsing still works exactly as before.
        
        Verifies that parser behavior is unchanged by project orientation.
        """
        from pathlib import Path
        
        parser = OrientationMetadataParser()
        
        # Test with valid metadata
        content = "**Metadata**: orientation=true, priority=1, query=\"test query here\""
        metadata = parser.extract_inline_metadata(content, Path("test.md"))
        
        # Should parse correctly
        assert metadata is not None
        assert metadata.get('orientation') is True
        assert metadata.get('priority') == 1
        assert metadata.get('query') == "test query here"
    
    def test_pydantic_models_have_optional_fields(self):
        """
        Test that all project orientation fields are optional.
        
        This ensures that existing config files don't need updates.
        """
        # MCPConfig should work without project field
        # (Can't instantiate MCPConfig directly without all required fields,
        #  so we test that ProjectConfig itself is optional)
        
        # ProjectConfig with no orientation is valid
        config = ProjectConfig(orientation=None)
        assert config.orientation is None
        
        # ProjectConfig with no fields at all is valid
        config2 = ProjectConfig()
        assert config2.orientation is None


class TestNoInlineMetadataScenarios:
    """
    Test scenarios where no inline metadata exists.
    
    This is the most common backward compatibility case:
    existing projects have markdown files but no orientation metadata.
    """
    
    def test_discovery_with_no_inline_metadata_anywhere(self):
        """
        Test when standards have no orientation metadata at all.
        
        Expected behavior:
        - No errors
        - Discovery completes successfully
        - Returns empty or config-only queries
        """
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = None
        
        # Standards index returns results but none have metadata
        mock_result1 = Mock()
        mock_result1.content = "# Regular Markdown\n\nNo metadata here."
        mock_result1.file_path = "standard1.md"
        
        mock_result2 = Mock()
        mock_result2.content = "# Another Document\n\nJust regular content."
        mock_result2.file_path = "standard2.md"
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = [mock_result1, mock_result2]
        
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        queries = discovery_handler.discover_orientation_queries()
        
        # Should handle absence of metadata gracefully
        assert queries == []
    
    def test_standards_index_search_unchanged(self):
        """
        Test that standards index search behavior is unchanged.
        
        The discovery handler should use the existing search interface
        without requiring any changes to StandardsIndex.
        """
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = []
        
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = None
        
        # Discovery should call search with expected pattern
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        queries = discovery_handler.discover_orientation_queries()
        
        # Verify search was called (to discover metadata)
        # But the search interface itself is unchanged
        assert mock_standards_index.search.called


class TestEdgeCases:
    """
    Test edge cases that could break backward compatibility.
    """
    
    def test_config_with_empty_queries_list(self):
        """
        Test when queries list is explicitly empty.
        
        Expected behavior:
        - No errors
        - System handles empty list gracefully
        """
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=True,
                queries=[]  # Empty list
            )
        )
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = []
        
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        queries = discovery_handler.discover_orientation_queries()
        
        # Should return empty list
        assert queries == []
    
    def test_malformed_inline_metadata_doesnt_crash(self):
        """
        Test that malformed metadata doesn't break discovery.
        
        Expected behavior:
        - Log warning
        - Skip malformed entry
        - Continue processing
        - No crash
        """
        mock_config = Mock(spec=MCPConfig)
        mock_config.project = None
        
        # Return malformed metadata
        mock_result = Mock()
        mock_result.content = "**Metadata**: completely broken garbage data"
        mock_result.file_path = "broken.md"
        
        mock_standards_index = Mock()
        mock_standards_index.search.return_value = [mock_result]
        
        # Should not raise exception
        discovery_handler = OrientationDiscoveryHandler(mock_standards_index, mock_config)
        queries = discovery_handler.discover_orientation_queries()
        
        # Should complete successfully (may return empty list)
        assert isinstance(queries, list)
    
    def test_search_tool_exception_doesnt_break_system(self):
        """
        Test that exceptions from search tool are handled gracefully.
        
        Expected behavior:
        - Exception caught
        - Error logged
        - Execution continues
        - Summary reports failure correctly
        """
        def failing_search_tool(query: str):
            raise RuntimeError("Search index unavailable")
        
        executor = ProjectOrientationExecutor(failing_search_tool)
        
        queries = [
            OrientationQuery(
                query="test query that will fail",
                priority=1,
                description="Test query"
            )
        ]
        
        # Should not raise exception
        summary = executor.execute_orientation(queries)
        
        # Should report failure gracefully
        assert summary.total_queries == 1
        assert summary.successful_queries == 0
        assert summary.failed_queries == 1


class TestNoRegressions:
    """
    Test that existing tests and functionality still work.
    
    These are smoke tests to ensure no regressions.
    """
    
    def test_orientation_query_pydantic_model_validation(self):
        """
        Test OrientationQuery model validation still works.
        
        This is the core Pydantic model. Must continue to work.
        """
        # Valid query should validate
        query = OrientationQuery(
            query="valid query string",
            priority=1,
            description="Test description"
        )
        
        assert query.query == "valid query string"
        assert query.priority == 1
        assert query.description == "Test description"
        
        # Invalid query should raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            OrientationQuery(
                query="ab",  # Too short (min_length=5)
                priority=1
            )
    
    def test_project_config_serialization(self):
        """
        Test ProjectConfig can serialize/deserialize correctly.
        
        Critical for backward compatibility with config loading.
        """
        # With orientation
        config_with = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=True,
                queries=[
                    OrientationQuery(
                        query="test query serialization",
                        priority=1,
                        description="Test"
                    )
                ]
            )
        )
        
        # Should serialize
        data = config_with.model_dump()
        assert 'orientation' in data
        
        # Should deserialize
        config_restored = ProjectConfig.model_validate(data)
        assert config_restored.orientation is not None
        assert config_restored.orientation.enabled is True
        
        # Without orientation
        config_without = ProjectConfig(orientation=None)
        data2 = config_without.model_dump()
        
        # Should handle None gracefully
        assert data2['orientation'] is None

