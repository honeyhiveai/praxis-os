"""
Test IndexManager for dynamic action routing and index orchestration.

Tests:
- Index initialization and registration
- Action routing (search_standards, search_code, find_callers, etc.)
- Error handling for invalid actions
- Index retrieval
- Health checks

Traceability:
    Phase 8, Task 8.2: RAG subsystem unit tests
    FR-029: Index Manager (dynamic routing)
"""

import pytest
from ouroboros.subsystems.rag.index_manager import IndexManager
from ouroboros.utils.errors import ActionableError


class TestIndexManager:
    """Test IndexManager dynamic routing and orchestration."""
    
    @pytest.fixture
    def index_manager(self, test_config, test_base_path):
        """
        Create IndexManager with isolated test config.
        
        Uses test fixtures that create temporary directories and configs.
        No production code touched - pure dependency injection.
        """
        return IndexManager(
            config=test_config.indexes,
            base_path=test_base_path
        )
    
    def test_initialization(self, index_manager):
        """Test IndexManager initializes correctly."""
        assert index_manager is not None
        assert hasattr(index_manager, "_indexes")
        assert isinstance(index_manager._indexes, dict)
    
    def test_has_standards_index(self, index_manager):
        """Test standards index is registered."""
        assert "standards" in index_manager._indexes
        standards_index = index_manager._indexes["standards"]
        assert standards_index is not None
    
    def test_has_code_index(self, index_manager):
        """Test code index is registered."""
        assert "code" in index_manager._indexes
        code_index = index_manager._indexes["code"]
        assert code_index is not None
    
    def test_code_index_has_ast_capabilities(self, index_manager):
        """Test CodeIndex has AST search capabilities via GraphIndex."""
        assert "code" in index_manager._indexes
        code_index = index_manager._indexes["code"]
        
        # CodeIndex should have search_ast method (delegates to GraphIndex)
        assert hasattr(code_index, "search_ast"), "CodeIndex should have search_ast method"
        
        # CodeIndex should have internal _graph_index
        assert hasattr(code_index, "_graph_index"), "CodeIndex should have _graph_index attribute"
        assert code_index._graph_index is not None
    
    def test_code_index_has_graph_capabilities(self, index_manager):
        """Test CodeIndex has graph traversal capabilities via GraphIndex."""
        assert "code" in index_manager._indexes
        code_index = index_manager._indexes["code"]
        
        # CodeIndex should have graph traversal methods (delegates to GraphIndex)
        assert hasattr(code_index, "find_callers"), "CodeIndex should have find_callers method"
        assert hasattr(code_index, "find_dependencies"), "CodeIndex should have find_dependencies method"
        assert hasattr(code_index, "find_call_paths"), "CodeIndex should have find_call_paths method"
        
        # CodeIndex should have internal _graph_index
        assert hasattr(code_index, "_graph_index"), "CodeIndex should have _graph_index attribute"
        assert code_index._graph_index is not None
    
    def test_get_index_valid(self, index_manager):
        """Test get_index returns correct index."""
        standards_index = index_manager.get_index("standards")
        assert standards_index is not None
        assert hasattr(standards_index, "search")
    
    def test_get_index_invalid(self, index_manager):
        """Test get_index returns None for invalid index."""
        result = index_manager.get_index("nonexistent")
        assert result is None
    
    def test_route_action_invalid(self, index_manager):
        """Test route_action rejects invalid actions."""
        with pytest.raises(ActionableError) as exc_info:
            index_manager.route_action(
                action="invalid_action",
                query="test"
            )
        
        error = exc_info.value
        assert "invalid_action" in str(error).lower() or "unknown" in str(error).lower()
        assert hasattr(error, "how_to_fix")
    
    def test_route_action_valid_actions(self, index_manager):
        """Test all valid actions are in registry."""
        valid_actions = [
            "search_standards",
            "search_code",
            "search_ast",
            "find_callers",
            "find_dependencies",
            "find_call_paths"
        ]
        
        # Just verify the actions don't raise "unknown action" errors
        # (they may fail due to index not being built, which is fine)
        for action in valid_actions:
            try:
                index_manager.route_action(action=action, query="test")
            except ActionableError as e:
                # Should not be "unknown action" error from routing
                error_str = str(e).lower()
                # OK if index has errors, NOT OK if action itself is unknown
                if "unknown" in error_str:
                    assert "action" not in error_str  # "unknown action" is bad
                    # "unknown error" from LanceDB/Rust is fine
            except Exception:
                # Other errors are fine (index not built, etc.)
                pass
    
    def test_health_check_all(self, index_manager):
        """Test health_check_all returns status for all indexes."""
        health = index_manager.health_check_all()
        
        assert isinstance(health, dict)
        # Should have health status for each index
        assert len(health) > 0
    
    def test_get_stats(self, index_manager):
        """Test get_stats returns stats for all indexes."""
        stats = index_manager.get_stats()
        
        assert isinstance(stats, dict)
        # Should have stats for each index
        assert len(stats) > 0

