"""Unit tests for WHERE clause builder in StandardsIndex.

Phase 3, Task 3.3: Tests for _build_where_clause() method.
"""

import pytest
from unittest.mock import Mock
from pathlib import Path


class TestWhereClauseBuilder:
    """Test suite for SQL WHERE clause building."""

    @pytest.fixture
    def mock_index(self):
        """Create a minimal mock index for testing WHERE clause builder."""
        # Import modules properly - load base first, then standards_index
        import sys
        import importlib.util
        
        # Load base module first
        base_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "base.py"
        base_spec = importlib.util.spec_from_file_location("server.indexes.base", base_path)
        base_module = importlib.util.module_from_spec(base_spec)
        sys.modules['server.indexes.base'] = base_module
        base_spec.loader.exec_module(base_module)
        
        # Now load standards_index
        standards_path = Path(__file__).parent.parent.parent / "server" / "indexes" / "standards_index.py"
        standards_spec = importlib.util.spec_from_file_location("server.indexes.standards_index", standards_path)
        standards_module = importlib.util.module_from_spec(standards_spec)
        sys.modules['server.indexes.standards_index'] = standards_module
        standards_spec.loader.exec_module(standards_module)
        
        # Create a minimal instance with mocked dependencies
        index = standards_module.StandardsIndex.__new__(standards_module.StandardsIndex)
        return index

    def test_empty_filters_returns_none(self, mock_index):
        """Test that empty filters dict returns None."""
        result = mock_index._build_where_clause({})
        assert result is None
        
        result = mock_index._build_where_clause(None)
        assert result is None

    def test_single_phase_filter(self, mock_index):
        """Test single phase filter generates correct SQL."""
        result = mock_index._build_where_clause({"phase": 1})
        assert result == "phase = 1"

    def test_single_is_critical_filter(self, mock_index):
        """Test single is_critical filter generates correct SQL."""
        result = mock_index._build_where_clause({"is_critical": True})
        assert result == "is_critical = True"
        
        result = mock_index._build_where_clause({"is_critical": False})
        assert result == "is_critical = False"

    def test_single_framework_type_filter(self, mock_index):
        """Test single framework_type filter generates correct SQL."""
        result = mock_index._build_where_clause({"framework_type": "backend"})
        assert result == "framework_type = 'backend'"

    def test_multiple_filters_use_and_logic(self, mock_index):
        """Test multiple filters are combined with AND."""
        result = mock_index._build_where_clause({
            "phase": 1,
            "is_critical": True
        })
        assert "phase = 1" in result
        assert "is_critical = True" in result
        assert " AND " in result

    def test_tags_filter_uses_like(self, mock_index):
        """Test tags filter uses LIKE for substring matching."""
        result = mock_index._build_where_clause({"tags": ["python"]})
        assert "tags LIKE '%python%'" in result

    def test_multiple_tags_create_multiple_conditions(self, mock_index):
        """Test multiple tags create separate LIKE conditions."""
        result = mock_index._build_where_clause({"tags": ["python", "testing"]})
        assert "tags LIKE '%python%'" in result
        assert "tags LIKE '%testing%'" in result
        assert " AND " in result

    def test_sql_injection_prevention_for_framework_type(self, mock_index):
        """Test that single quotes in framework_type are escaped."""
        result = mock_index._build_where_clause({"framework_type": "test'OR'1'='1"})
        assert "framework_type = 'test''OR''1''=''1'" in result

    def test_sql_injection_prevention_for_tags(self, mock_index):
        """Test that single quotes in tags are escaped."""
        result = mock_index._build_where_clause({"tags": ["test'OR'1'='1"]})
        assert "tags LIKE '%test''OR''1''=''1%'" in result

    def test_invalid_filter_types_ignored(self, mock_index):
        """Test that invalid filter types are gracefully ignored."""
        # Phase should be int
        result = mock_index._build_where_clause({"phase": "invalid"})
        assert result is None
        
        # is_critical should be bool
        result = mock_index._build_where_clause({"is_critical": "yes"})
        assert result is None
        
        # framework_type should be string
        result = mock_index._build_where_clause({"framework_type": 123})
        assert result is None
        
        # tags should be list
        result = mock_index._build_where_clause({"tags": "python"})
        assert result is None

    def test_combined_valid_and_invalid_filters(self, mock_index):
        """Test that valid filters work even if some invalid filters present."""
        result = mock_index._build_where_clause({
            "phase": 1,  # valid
            "is_critical": "yes",  # invalid (should be bool)
            "framework_type": "backend"  # valid
        })
        assert result is not None
        assert "phase = 1" in result
        assert "framework_type = 'backend'" in result
        assert "is_critical" not in result

    def test_all_filters_combined(self, mock_index):
        """Test comprehensive filter with all supported types."""
        result = mock_index._build_where_clause({
            "phase": 2,
            "is_critical": True,
            "framework_type": "production_v1",
            "tags": ["deployment", "monitoring"]
        })
        
        assert "phase = 2" in result
        assert "is_critical = True" in result
        assert "framework_type = 'production_v1'" in result
        assert "tags LIKE '%deployment%'" in result
        assert "tags LIKE '%monitoring%'" in result
        
        # Should have 4 AND operators (5 conditions)
        assert result.count(" AND ") == 4

