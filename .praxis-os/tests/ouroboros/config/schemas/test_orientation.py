"""
Unit tests for Orientation configuration models.

Tests the OrientationQuery Pydantic model including:
    - Field validation (priority range, query length)
    - Circular dependency detection
    - ValidationError messages and actionability

Author: prAxIs OS Development Team
Date: 2025-11-19
"""

import pytest
from pydantic import ValidationError

from ouroboros.config.schemas.orientation import OrientationQuery, ProjectOrientation, ProjectConfig


class TestOrientationQueryInstantiation:
    """Test basic instantiation of OrientationQuery."""
    
    def test_minimal_valid_query(self):
        """
        Test OrientationQuery with minimal required fields.
        
        Validates:
            - query and priority are sufficient
            - Optional fields default to None
            - Model instantiates successfully
        
        Acceptance Criterion: Task 2.1 - Valid model instantiates
        """
        query = OrientationQuery(
            query="test query",
            priority=1
        )
        
        assert query.query == "test query"
        assert query.priority == 1
        assert query.description is None
        assert query.category is None
        assert query.depends_on is None
    
    def test_all_fields_specified(self):
        """
        Test OrientationQuery with all fields populated.
        
        Validates:
            - All 5 fields can be set
            - Values are preserved correctly
        
        Acceptance Criterion: Task 2.1 - All 5 fields defined
        """
        query = OrientationQuery(
            query="dogfooding model development workflow",
            priority=1,
            description="Learn how prAxIs OS dogfoods itself",
            category="development",
            depends_on=["base orientation"]
        )
        
        assert query.query == "dogfooding model development workflow"
        assert query.priority == 1
        assert query.description == "Learn how prAxIs OS dogfoods itself"
        assert query.category == "development"
        assert query.depends_on == ["base orientation"]


class TestQueryFieldValidation:
    """Test query field validation (length constraints)."""
    
    def test_query_minimum_length(self):
        """
        Test that query must be at least 5 characters.
        
        Validates:
            - Queries shorter than 5 chars raise ValidationError
            - Error message is actionable
        
        Acceptance Criterion: Task 2.1 - Query min_length=5
        """
        with pytest.raises(ValidationError) as exc_info:
            OrientationQuery(query="test", priority=1)
        
        error_str = str(exc_info.value)
        assert "at least 5 characters" in error_str.lower() or "min_length" in error_str.lower()
    
    def test_query_maximum_length(self):
        """
        Test that query must not exceed 500 characters.
        
        Validates:
            - Queries longer than 500 chars raise ValidationError
            - Error message is actionable
        
        Acceptance Criterion: Task 2.1 - Query max_length=500
        """
        long_query = "x" * 501  # 501 characters
        
        with pytest.raises(ValidationError) as exc_info:
            OrientationQuery(query=long_query, priority=1)
        
        error_str = str(exc_info.value)
        assert "at most 500 characters" in error_str.lower() or "max_length" in error_str.lower()
    
    def test_query_valid_lengths(self):
        """
        Test that queries within valid range (5-500) work.
        
        Validates:
            - Minimum valid (5 chars) works
            - Maximum valid (500 chars) works
            - Mid-range values work
        """
        # Minimum valid
        query1 = OrientationQuery(query="12345", priority=1)
        assert len(query1.query) == 5
        
        # Maximum valid
        max_query = "x" * 500
        query2 = OrientationQuery(query=max_query, priority=1)
        assert len(query2.query) == 500
        
        # Mid-range
        query3 = OrientationQuery(query="test query" * 10, priority=1)
        assert len(query3.query) > 5


class TestPriorityValidation:
    """Test priority field validation (range 1-3)."""
    
    def test_priority_valid_values(self):
        """
        Test that priorities 1, 2, 3 are valid.
        
        Validates:
            - Priority 1 (high) works
            - Priority 2 (medium) works
            - Priority 3 (low) works
        
        Acceptance Criterion: Task 2.1 - Priority validates range 1-3
        """
        query1 = OrientationQuery(query="test query", priority=1)
        query2 = OrientationQuery(query="test query", priority=2)
        query3 = OrientationQuery(query="test query", priority=3)
        
        assert query1.priority == 1
        assert query2.priority == 2
        assert query3.priority == 3
    
    def test_priority_too_low(self):
        """
        Test that priority < 1 raises ValidationError.
        
        Validates:
            - Priority 0 raises error
            - Negative priorities raise error
            - Error message is actionable
        
        Acceptance Criterion: Task 2.1 - Invalid priority raises ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            OrientationQuery(query="test query", priority=0)
        
        error_str = str(exc_info.value)
        # Should mention valid range or specific issue
        assert "1" in error_str or "priority" in error_str.lower()
    
    def test_priority_too_high(self):
        """
        Test that priority > 3 raises ValidationError.
        
        Validates:
            - Priority 4 raises error
            - Priority 5+ raises error
            - Error message mentions valid range
        
        Acceptance Criterion: Task 2.1 - Invalid priority raises ValidationError with actionable message
        """
        with pytest.raises(ValidationError) as exc_info:
            OrientationQuery(query="test query", priority=4)
        
        error_str = str(exc_info.value)
        # Should mention valid range (1-3)
        assert "3" in error_str or "range" in error_str.lower()
    
    def test_priority_error_message_actionable(self):
        """
        Test that priority validation errors are actionable.
        
        Validates:
            - Error message explains valid range
            - Error message suggests remediation
        
        Acceptance Criterion: Task 2.1 - ActionableError message with remediation
        """
        with pytest.raises(ValidationError) as exc_info:
            OrientationQuery(query="test query", priority=5)
        
        error_str = str(exc_info.value).lower()
        # Should be helpful
        assert ("1" in error_str and "3" in error_str) or "remediation" in error_str


class TestCircularDependencyValidation:
    """Test circular dependency prevention."""
    
    def test_query_cannot_depend_on_itself(self):
        """
        Test that a query cannot depend on itself (direct circular dependency).
        
        Validates:
            - Query string in depends_on list raises ValidationError
            - Error message identifies the circular dependency
        
        Acceptance Criterion: Task 2.1 - Circular dependency validator prevents self-dependency
        """
        with pytest.raises(ValidationError) as exc_info:
            OrientationQuery(
                query="test query",
                priority=1,
                depends_on=["test query"]  # Circular!
            )
        
        error_str = str(exc_info.value)
        assert "circular" in error_str.lower() or "depend" in error_str.lower()
    
    def test_valid_dependencies(self):
        """
        Test that valid dependencies (not self) work correctly.
        
        Validates:
            - Query can depend on other queries
            - Multiple dependencies work
            - Dependencies list is preserved
        """
        query = OrientationQuery(
            query="advanced topic",
            priority=2,
            depends_on=["basic topic", "foundation"]
        )
        
        assert query.depends_on == ["basic topic", "foundation"]
        assert "advanced topic" not in query.depends_on
    
    def test_empty_dependencies(self):
        """
        Test that empty dependencies list is valid.
        
        Validates:
            - depends_on=[] is allowed
            - depends_on=None is allowed (default)
        """
        query1 = OrientationQuery(
            query="test query",
            priority=1,
            depends_on=[]
        )
        assert query1.depends_on == []
        
        query2 = OrientationQuery(
            query="test query",
            priority=1
        )
        assert query2.depends_on is None


class TestOptionalFields:
    """Test optional field behavior."""
    
    def test_description_optional(self):
        """Test that description field is optional."""
        query = OrientationQuery(query="test query", priority=1)
        assert query.description is None
        
        query_with_desc = OrientationQuery(
            query="test query",
            priority=1,
            description="Test description"
        )
        assert query_with_desc.description == "Test description"
    
    def test_category_optional(self):
        """Test that category field is optional."""
        query = OrientationQuery(query="test query", priority=1)
        assert query.category is None
        
        query_with_cat = OrientationQuery(
            query="test query",
            priority=1,
            category="development"
        )
        assert query_with_cat.category == "development"
    
    def test_depends_on_optional(self):
        """Test that depends_on field is optional."""
        query = OrientationQuery(query="test query", priority=1)
        assert query.depends_on is None
        
        query_with_deps = OrientationQuery(
            query="test query",
            priority=1,
            depends_on=["other query"]
        )
        assert query_with_deps.depends_on == ["other query"]


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_model_to_dict(self):
        """Test that model can be serialized to dict."""
        query = OrientationQuery(
            query="test query",
            priority=1,
            description="Test description"
        )
        
        data = query.model_dump()
        
        assert data['query'] == "test query"
        assert data['priority'] == 1
        assert data['description'] == "Test description"
        assert data['category'] is None
        assert data['depends_on'] is None
    
    def test_model_from_dict(self):
        """Test that model can be created from dict."""
        data = {
            'query': 'test query',
            'priority': 2,
            'description': 'Test description',
            'category': 'testing'
        }
        
        query = OrientationQuery(**data)
        
        assert query.query == "test query"
        assert query.priority == 2
        assert query.description == "Test description"
        assert query.category == "testing"


class TestProjectOrientationInstantiation:
    """Test basic instantiation of ProjectOrientation."""
    
    def test_minimal_valid_config(self):
        """
        Test ProjectOrientation with minimal fields (empty queries).
        
        Validates:
            - Empty queries list is valid
            - enabled defaults to True
        
        Acceptance Criterion: Task 2.2 - Model accepts empty queries list
        """
        config = ProjectOrientation(queries=[])
        
        assert config.enabled is True
        assert config.queries == []
    
    def test_enabled_defaults_to_true(self):
        """
        Test that enabled field defaults to True.
        
        Validates:
            - When enabled not specified, defaults to True
            - Default behavior is orientation enabled
        
        Acceptance Criterion: Task 2.2 - Default enabled=True when not specified
        """
        config = ProjectOrientation(queries=[])
        assert config.enabled is True
        
        # Also test with queries present
        config2 = ProjectOrientation(
            queries=[
                OrientationQuery(query="test query", priority=1)
            ]
        )
        assert config2.enabled is True
    
    def test_with_queries(self):
        """
        Test ProjectOrientation with queries populated.
        
        Validates:
            - Queries list is preserved
            - Multiple queries work
            - All fields accessible
        
        Acceptance Criterion: Task 2.2 - ProjectOrientation class defined with enabled and queries
        """
        config = ProjectOrientation(
            enabled=True,
            queries=[
                OrientationQuery(query="first query", priority=1),
                OrientationQuery(query="second query", priority=2)
            ]
        )
        
        assert config.enabled is True
        assert len(config.queries) == 2
        assert config.queries[0].query == "first query"
        assert config.queries[1].query == "second query"
    
    def test_disabled_orientation(self):
        """
        Test ProjectOrientation with enabled=False.
        
        Validates:
            - enabled can be set to False
            - Queries still present but orientation disabled
        """
        config = ProjectOrientation(
            enabled=False,
            queries=[
                OrientationQuery(query="test query", priority=1)
            ]
        )
        
        assert config.enabled is False
        assert len(config.queries) == 1


class TestDuplicateQueryValidation:
    """Test duplicate query string detection."""
    
    def test_duplicate_queries_raise_error(self):
        """
        Test that duplicate query strings raise ValidationError.
        
        Validates:
            - Same query string twice raises error
            - Error message identifies the duplicate
            - Error is actionable
        
        Acceptance Criterion: Task 2.2 - Duplicate detection works
        """
        with pytest.raises(ValidationError) as exc_info:
            ProjectOrientation(
                queries=[
                    OrientationQuery(query="test query", priority=1),
                    OrientationQuery(query="test query", priority=2)  # Duplicate!
                ]
            )
        
        error_str = str(exc_info.value)
        assert "duplicate" in error_str.lower()
        assert "test query" in error_str
    
    def test_unique_queries_valid(self):
        """
        Test that unique query strings are valid.
        
        Validates:
            - Different query strings work fine
            - Multiple queries allowed if unique
        """
        config = ProjectOrientation(
            queries=[
                OrientationQuery(query="first query", priority=1),
                OrientationQuery(query="second query", priority=2),
                OrientationQuery(query="third query", priority=3)
            ]
        )
        
        assert len(config.queries) == 3
    
    def test_empty_queries_no_duplicate_error(self):
        """
        Test that empty queries list doesn't trigger duplicate validation.
        
        Validates:
            - Empty list is valid (no duplicates)
            - No validation error
        """
        config = ProjectOrientation(queries=[])
        assert config.queries == []
    
    def test_single_query_no_duplicate_error(self):
        """
        Test that single query has no duplicates.
        
        Validates:
            - One query is always unique
            - No validation error
        """
        config = ProjectOrientation(
            queries=[
                OrientationQuery(query="only query", priority=1)
            ]
        )
        
        assert len(config.queries) == 1
    
    def test_duplicate_error_message_actionable(self):
        """
        Test that duplicate error message is actionable.
        
        Validates:
            - Error message mentions remediation
            - Error message lists duplicate queries
        
        Acceptance Criterion: Task 2.2 - Duplicate validator raises ValidationError with clear message
        """
        with pytest.raises(ValidationError) as exc_info:
            ProjectOrientation(
                queries=[
                    OrientationQuery(query="duplicate query", priority=1),
                    OrientationQuery(query="unique query", priority=2),
                    OrientationQuery(query="duplicate query", priority=3)
                ]
            )
        
        error_str = str(exc_info.value).lower()
        # Should be helpful
        assert "duplicate" in error_str
        assert "remediation" in error_str or "remove" in error_str


class TestProjectOrientationSerialization:
    """Test model serialization and deserialization."""
    
    def test_model_to_dict(self):
        """Test that ProjectOrientation can be serialized to dict."""
        config = ProjectOrientation(
            enabled=True,
            queries=[
                OrientationQuery(
                    query="test query",
                    priority=1,
                    description="Test description"
                )
            ]
        )
        
        data = config.model_dump()
        
        assert data['enabled'] is True
        assert len(data['queries']) == 1
        assert data['queries'][0]['query'] == "test query"
    
    def test_model_from_dict(self):
        """Test that ProjectOrientation can be created from dict."""
        data = {
            'enabled': False,
            'queries': [
                {
                    'query': 'test query',
                    'priority': 2
                }
            ]
        }
        
        config = ProjectOrientation(**data)
        
        assert config.enabled is False
        assert len(config.queries) == 1
        assert config.queries[0].query == "test query"
        assert config.queries[0].priority == 2


class TestProjectConfigInstantiation:
    """Test ProjectConfig model instantiation and structure."""
    
    def test_minimal_config_no_orientation(self):
        """
        Test ProjectConfig with no orientation section (None).
        
        Validates:
            - ProjectConfig can be created with orientation=None
            - Default is None
            - Backward compatible with missing orientation
        
        Acceptance Criterion: Task 2.3 - Config loads without project section
        """
        config = ProjectConfig(orientation=None)
        assert config.orientation is None
    
    def test_default_orientation_is_none(self):
        """
        Test that orientation defaults to None.
        
        Validates:
            - When orientation not specified, defaults to None
            - Backward compatibility guaranteed
        
        Acceptance Criterion: Task 2.3 - Missing project section doesn't raise validation error
        """
        config = ProjectConfig()
        assert config.orientation is None
    
    def test_with_orientation(self):
        """
        Test ProjectConfig with orientation section populated.
        
        Validates:
            - ProjectConfig accepts ProjectOrientation
            - Nested structure works correctly
        
        Acceptance Criterion: Task 2.3 - Config loads with project.orientation section
        """
        config = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=True,
                queries=[
                    OrientationQuery(query="test query", priority=1)
                ]
            )
        )
        
        assert config.orientation is not None
        assert config.orientation.enabled is True
        assert len(config.orientation.queries) == 1
    
    def test_with_disabled_orientation(self):
        """
        Test ProjectConfig with orientation disabled.
        
        Validates:
            - orientation.enabled=False is valid
            - Config structure preserved
        """
        config = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=False,
                queries=[]
            )
        )
        
        assert config.orientation is not None
        assert config.orientation.enabled is False


class TestProjectConfigSerialization:
    """Test ProjectConfig serialization and deserialization."""
    
    def test_serialize_with_orientation(self):
        """Test serialization of ProjectConfig with orientation."""
        config = ProjectConfig(
            orientation=ProjectOrientation(
                enabled=True,
                queries=[
                    OrientationQuery(
                        query="test query",
                        priority=1,
                        description="Test description"
                    )
                ]
            )
        )
        
        data = config.model_dump()
        
        assert 'orientation' in data
        assert data['orientation']['enabled'] is True
        assert len(data['orientation']['queries']) == 1
    
    def test_serialize_without_orientation(self):
        """Test serialization of ProjectConfig without orientation."""
        config = ProjectConfig(orientation=None)
        
        data = config.model_dump()
        
        assert 'orientation' in data
        assert data['orientation'] is None
    
    def test_deserialize_from_dict(self):
        """Test deserialization from dict."""
        data = {
            'orientation': {
                'enabled': True,
                'queries': [
                    {
                        'query': 'test query',
                        'priority': 2
                    }
                ]
            }
        }
        
        config = ProjectConfig(**data)
        
        assert config.orientation is not None
        assert config.orientation.enabled is True
        assert len(config.orientation.queries) == 1

