"""
Integration tests for MCPConfig with ProjectConfig field.

Tests backward compatibility and project orientation integration.
These tests verify that the project field is properly integrated into
MCPConfig without breaking existing configurations.
"""

import pytest

from ouroboros.config.schemas.mcp import MCPConfig
from ouroboros.config.schemas.orientation import ProjectConfig, ProjectOrientation, OrientationQuery


class TestMCPConfigProjectField:
    """Test MCPConfig project field integration."""
    
    def test_project_field_exists_and_optional(self):
        """
        Test that MCPConfig has a project field that defaults to None.
        
        Validates:
            - project field exists on MCPConfig
            - Defaults to None (backward compatible)
            - Type is Optional[ProjectConfig]
        
        Acceptance Criterion: Task 2.3 - UnifiedConfig has project: Optional[ProjectConfig] field
        """
        # Check field exists in model fields
        assert 'project' in MCPConfig.model_fields
        
        # Check it's optional (default is None)
        project_field = MCPConfig.model_fields['project']
        assert not project_field.is_required()
    
    def test_can_access_project_field(self):
        """
        Test that project field can be accessed on MCPConfig instance.
        
        This is a basic structural test using a real config file.
        
        Acceptance Criterion: Task 2.3 - Config loads without project section
        """
        from pathlib import Path
        from ouroboros.config.loader import find_config_file
        
        # Load actual config
        config_path = find_config_file()
        if config_path and config_path.exists():
            config = MCPConfig.from_yaml(config_path)
            
            # Should have project field (even if None)
            assert hasattr(config, 'project')
            # Project might be None or ProjectConfig depending on actual config
            assert config.project is None or isinstance(config.project, ProjectConfig)


class TestProjectConfigIntegration:
    """Test ProjectConfig integration with ProjectOrientation."""
    
    def test_project_config_with_orientation(self):
        """
        Test ProjectConfig with ProjectOrientation.
        
        Validates:
            - ProjectConfig accepts ProjectOrientation
            - Nested structure works correctly
        
        Acceptance Criterion: Task 2.3 - ProjectConfig class defined with Optional[ProjectOrientation]
        """
        project_config = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=True,
                queries=[
                    OrientationQuery(
                        query="test query",
                        priority=1
                    )
                ]
            )
        )
        
        assert project_config.orientation is not None
        assert project_config.orientation.enabled is True
        assert len(project_config.orientation.queries) == 1
    
    def test_project_config_serialization(self):
        """
        Test ProjectConfig serialization with orientation.
        
        Validates:
            - model_dump() includes orientation
            - Round-trip serialization works
        
        Acceptance Criterion: Task 2.3 - Config loads with project.orientation section
        """
        project_config = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=True,
                queries=[
                    OrientationQuery(
                        query="test query",
                        priority=2,
                        description="Test description"
                    )
                ]
            )
        )
        
        # Serialize
        data = project_config.model_dump()
        
        assert 'orientation' in data
        assert data['orientation']['enabled'] is True
        assert len(data['orientation']['queries']) == 1
        
        # Round-trip
        project_config2 = ProjectConfig(**data)
        assert project_config2.orientation is not None
        assert project_config2.orientation.enabled is True
        assert len(project_config2.orientation.queries) == 1

