"""
Unit tests for component_helpers module.

Tests the ComponentDescriptor dataclass and dynamic_health_check() helper
that implement the fractal component registry pattern.

Test Coverage:
    - ComponentDescriptor: Valid and invalid instantiation
    - dynamic_health_check(): Empty dict, 0/1/3 components, exception handling
    - Capability mapping: Healthy/unhealthy component status
    - Aggregation: All healthy vs. one broken
"""

import pytest
from unittest.mock import Mock
from ouroboros.subsystems.rag.utils.component_helpers import (
    ComponentDescriptor,
    dynamic_health_check,
)
from ouroboros.subsystems.rag.base import HealthStatus


class TestComponentDescriptor:
    """Test suite for ComponentDescriptor dataclass validation."""
    
    def test_valid_descriptor(self):
        """Test that valid ComponentDescriptor instantiates successfully."""
        descriptor = ComponentDescriptor(
            name="test_component",
            provides=["data"],
            capabilities=["query"],
            health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
            rebuild=lambda: None,
            dependencies=[],
        )
        assert descriptor.name == "test_component"
        assert descriptor.provides == ["data"]
        assert descriptor.capabilities == ["query"]
        assert callable(descriptor.health_check)
        assert callable(descriptor.rebuild)
        assert descriptor.dependencies == []
    
    def test_empty_name_raises_error(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name must be non-empty"):
            ComponentDescriptor(
                name="",
                provides=["data"],
                capabilities=["query"],
                health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
                rebuild=lambda: None,
                dependencies=[],
            )
    
    def test_empty_provides_raises_error(self):
        """Test that empty provides list raises ValueError."""
        with pytest.raises(ValueError, match="provides must be non-empty"):
            ComponentDescriptor(
                name="test",
                provides=[],
                capabilities=["query"],
                health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
                rebuild=lambda: None,
                dependencies=[],
            )
    
    def test_empty_capabilities_raises_error(self):
        """Test that empty capabilities list raises ValueError."""
        with pytest.raises(ValueError, match="capabilities must be non-empty"):
            ComponentDescriptor(
                name="test",
                provides=["data"],
                capabilities=[],
                health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
                rebuild=lambda: None,
                dependencies=[],
            )
    
    def test_non_callable_health_check_raises_error(self):
        """Test that non-callable health_check raises ValueError."""
        with pytest.raises(ValueError, match="health_check must be callable"):
            ComponentDescriptor(
                name="test",
                provides=["data"],
                capabilities=["query"],
                health_check="not_callable",  # type: ignore
                rebuild=lambda: None,
                dependencies=[],
            )
    
    def test_non_callable_rebuild_raises_error(self):
        """Test that non-callable rebuild raises ValueError."""
        with pytest.raises(ValueError, match="rebuild must be callable"):
            ComponentDescriptor(
                name="test",
                provides=["data"],
                capabilities=["query"],
                health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
                rebuild=123,  # type: ignore
                dependencies=[],
            )
    
    def test_none_name_raises_error(self):
        """Test that None name raises ValueError."""
        with pytest.raises(ValueError, match="name must be non-empty"):
            ComponentDescriptor(
                name=None,  # type: ignore
                provides=["data"],
                capabilities=["query"],
                health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
                rebuild=lambda: None,
                dependencies=[],
            )


class TestDynamicHealthCheck:
    """Test suite for dynamic_health_check() function."""
    
    def test_empty_components_returns_healthy(self):
        """Test that empty components dict returns healthy=True."""
        result = dynamic_health_check({})
        
        assert result.healthy == True
        assert result.details["component_count"] == 0
        assert result.details["healthy_count"] == 0
        assert result.details["components"] == {}
        assert result.details["capabilities"] == {}
        assert "No components registered" in result.message
    
    def test_single_healthy_component(self):
        """Test with single healthy component."""
        components = {
            "comp_a": ComponentDescriptor(
                name="comp_a",
                provides=["data_a"],
                capabilities=["query_a"],
                health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
                rebuild=lambda: None,
                dependencies=[],
            ),
        }
        
        result = dynamic_health_check(components)
        
        assert result.healthy == True
        assert result.details["component_count"] == 1
        assert result.details["healthy_count"] == 1
        assert result.details["components"]["comp_a"].healthy == True
        assert result.details["capabilities"]["query_a"] == True
        assert "1 components healthy" in result.message
    
    def test_three_healthy_components(self):
        """Test with three healthy components."""
        components = {
            "comp_a": ComponentDescriptor(
                name="comp_a",
                provides=["data_a"],
                capabilities=["query_a"],
                health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
                rebuild=lambda: None,
                dependencies=[],
            ),
            "comp_b": ComponentDescriptor(
                name="comp_b",
                provides=["data_b"],
                capabilities=["query_b"],
                health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
                rebuild=lambda: None,
                dependencies=[],
            ),
            "comp_c": ComponentDescriptor(
                name="comp_c",
                provides=["data_c"],
                capabilities=["query_c"],
                health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
                rebuild=lambda: None,
                dependencies=[],
            ),
        }
        
        result = dynamic_health_check(components)
        
        assert result.healthy == True
        assert result.details["component_count"] == 3
        assert result.details["healthy_count"] == 3
        assert all(result.details["components"][name].healthy for name in components)
        assert all(result.details["capabilities"][f"query_{c}"] for c in "abc")
        assert "All 3 components healthy" in result.message
    
    def test_one_broken_component(self):
        """Test that one unhealthy component makes overall unhealthy."""
        components = {
            "comp_healthy": ComponentDescriptor(
                name="comp_healthy",
                provides=["data"],
                capabilities=["query_healthy"],
                health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
                rebuild=lambda: None,
                dependencies=[],
            ),
            "comp_broken": ComponentDescriptor(
                name="comp_broken",
                provides=["data"],
                capabilities=["query_broken"],
                health_check=lambda: HealthStatus(healthy=False, message="Broken", details={}),
                rebuild=lambda: None,
                dependencies=[],
            ),
        }
        
        result = dynamic_health_check(components)
        
        assert result.healthy == False
        assert result.details["component_count"] == 2
        assert result.details["healthy_count"] == 1
        assert result.details["components"]["comp_healthy"].healthy == True
        assert result.details["components"]["comp_broken"].healthy == False
        assert result.details["capabilities"]["query_healthy"] == True
        assert result.details["capabilities"]["query_broken"] == False
        assert "1/2 components healthy" in result.message
    
    def test_exception_in_health_check_doesnt_crash(self):
        """Test that exception in component health_check() is caught and logged."""
        components = {
            "comp_error": ComponentDescriptor(
                name="comp_error",
                provides=["data"],
                capabilities=["query_error"],
                health_check=lambda: 1 / 0,  # Raises ZeroDivisionError
                rebuild=lambda: None,
                dependencies=[],
            ),
        }
        
        # Should not raise exception
        result = dynamic_health_check(components)
        
        assert result.healthy == False
        assert result.details["component_count"] == 1
        assert result.details["healthy_count"] == 0
        assert result.details["components"]["comp_error"].healthy == False
        assert "exception" in result.details["components"]["comp_error"].message.lower()
        assert result.details["capabilities"]["query_error"] == False
    
    def test_capability_mapping_reflects_health(self):
        """Test that capability map correctly reflects component health status."""
        components = {
            "comp_a": ComponentDescriptor(
                name="comp_a",
                provides=["data"],
                capabilities=["cap_a1", "cap_a2"],
                health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
                rebuild=lambda: None,
                dependencies=[],
            ),
            "comp_b": ComponentDescriptor(
                name="comp_b",
                provides=["data"],
                capabilities=["cap_b1", "cap_b2"],
                health_check=lambda: HealthStatus(healthy=False, message="Broken", details={}),
                rebuild=lambda: None,
                dependencies=[],
            ),
        }
        
        result = dynamic_health_check(components)
        
        # Healthy component capabilities should be True
        assert result.details["capabilities"]["cap_a1"] == True
        assert result.details["capabilities"]["cap_a2"] == True
        
        # Unhealthy component capabilities should be False
        assert result.details["capabilities"]["cap_b1"] == False
        assert result.details["capabilities"]["cap_b2"] == False
    
    def test_all_healthy_gives_overall_healthy(self):
        """Test that all healthy components result in overall healthy=True."""
        components = {
            "comp_a": ComponentDescriptor(
                name="comp_a",
                provides=["data"],
                capabilities=["query_a"],
                health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
                rebuild=lambda: None,
                dependencies=[],
            ),
            "comp_b": ComponentDescriptor(
                name="comp_b",
                provides=["data"],
                capabilities=["query_b"],
                health_check=lambda: HealthStatus(healthy=True, message="OK", details={}),
                rebuild=lambda: None,
                dependencies=[],
            ),
        }
        
        result = dynamic_health_check(components)
        
        assert result.healthy == True
        assert result.details["healthy_count"] == 2
        assert result.details["component_count"] == 2
    
    def test_mock_component_health_check(self):
        """Test using mocked component health_check() for isolation."""
        mock_health = Mock(return_value=HealthStatus(
            healthy=True,
            message="Mocked OK",
            details={"mocked": True}
        ))
        
        components = {
            "mock_comp": ComponentDescriptor(
                name="mock_comp",
                provides=["mock_data"],
                capabilities=["mock_query"],
                health_check=mock_health,
                rebuild=lambda: None,
                dependencies=[],
            ),
        }
        
        result = dynamic_health_check(components)
        
        # Verify mock was called
        mock_health.assert_called_once()
        
        # Verify result reflects mocked health
        assert result.healthy == True
        assert result.details["components"]["mock_comp"].healthy == True
        assert result.details["components"]["mock_comp"].message == "Mocked OK"

