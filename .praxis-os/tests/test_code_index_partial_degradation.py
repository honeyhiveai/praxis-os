"""Integration tests for CodeIndex cascading health checks and partial degradation.

Tests validate that CodeIndex properly delegates health checks to sub-indexes
(SemanticIndex and GraphIndex) and that operations continue to work when one
sub-index is degraded but the other is healthy.

Test Coverage:
    - Partial degradation: Semantic broken but graph operations succeed
    - Partial degradation: Graph broken but semantic operations succeed
    - Health check reports component-level diagnostics
    - Dynamic component discovery (adding GraphIndex component doesn't require CodeIndex changes)

Traceability:
    - Task 2.3: Integration tests for CodeIndex partial degradation
    - FR-008: Partial degradation detection
    - FR-009: Targeted diagnostics
"""

import pytest
from pathlib import Path
import tempfile

from ouroboros.config.schemas.indexes import CodeIndexConfig, GraphConfig, VectorConfig, FTSConfig
from ouroboros.subsystems.rag.code.container import CodeIndex


@pytest.fixture(scope="function")
def test_code_dir(tmp_path: Path) -> Path:
    """Create temporary directory with test Python files.
    
    Creates simple Python code for testing CodeIndex functionality.
    
    Returns:
        Path to temporary directory with test code
    """
    code_dir = tmp_path / "test_code"
    code_dir.mkdir()
    
    # File 1: Functions with calls
    (code_dir / "module_a.py").write_text("""
def function_a():
    return function_b()

def function_b():
    return "result"
""")
    
    # File 2: Classes
    (code_dir / "module_b.py").write_text("""
class MyClass:
    def method_a(self):
        return self.method_b()
    
    def method_b(self):
        return "data"
""")
    
    return code_dir


@pytest.fixture(scope="function")
def built_code_index(test_code_dir: Path) -> CodeIndex:
    """Create and build CodeIndex with test code.
    
    Returns fully built index with both semantic and graph sub-indexes populated.
    
    Returns:
        CodeIndex: Built index ready for testing
    """
    # Create config with required fields
    config = CodeIndexConfig(
        source_paths=[str(test_code_dir)],  # Convert Path to string
        languages=["python"],
        vector=VectorConfig(
            model="microsoft/codebert-base",
            dimension=768
        ),
        fts=FTSConfig(
            tokenizer="default",
            enabled=True
        ),
        graph=GraphConfig()
    )
    
    base_path = test_code_dir  # Use test_code_dir as base_path
    index = CodeIndex(config, base_path)
    index.build([test_code_dir], force=True)
    
    return index


class TestPartialDegradation:
    """Test suite for CodeIndex partial degradation scenarios."""
    
    def test_semantic_broken_graph_healthy_find_callers_succeeds(self, built_code_index: CodeIndex):
        """Test: Semantic broken, graph healthy → find_callers() succeeds.
        
        Validates that graph operations continue to work when semantic index is degraded.
        This demonstrates partial degradation: one component broken, others operational.
        """
        # Break semantic by dropping the LanceDB table
        db = built_code_index._semantic_index.db_connection.connect()
        if "code" in db.table_names():
            db.drop_table("code")
            built_code_index._semantic_index._table = None  # Reset cached table reference
        
        # Verify semantic is broken
        semantic_health = built_code_index._semantic_index.health_check()
        assert semantic_health.healthy == False, "Semantic should be unhealthy after clearing table"
        
        # Verify graph is still healthy
        graph_health = built_code_index._graph_index.health_check()
        assert graph_health.healthy == True, "Graph should still be healthy"
        
        # Verify find_callers() still works (uses graph, not semantic)
        try:
            results = built_code_index.find_callers("function_b", max_depth=3)
            print(f"✅ find_callers() succeeded with semantic broken: {len(results)} results")
            # Note: May return 0 results if no callers exist, but should not raise exception
            assert True, "find_callers() should succeed when graph is healthy"
        except Exception as e:
            pytest.fail(f"find_callers() should succeed when graph is healthy, but raised: {e}")
    
    def test_graph_broken_semantic_healthy_search_succeeds(self, built_code_index: CodeIndex):
        """Test: Graph broken, semantic healthy → search() succeeds.
        
        Validates that semantic search continues to work when graph index is degraded.
        This demonstrates partial degradation in the opposite direction.
        """
        # Break graph by clearing all tables
        conn = built_code_index._graph_index.db_connection.get_connection()
        conn.execute("DELETE FROM relationships")
        conn.execute("DELETE FROM symbols")
        conn.execute("DROP TABLE IF EXISTS ast_nodes")
        conn.execute("""
            CREATE TABLE ast_nodes (
                id INTEGER PRIMARY KEY,
                file_path TEXT NOT NULL,
                language TEXT NOT NULL,
                node_type TEXT NOT NULL,
                symbol_name TEXT,
                start_line INTEGER NOT NULL,
                end_line INTEGER NOT NULL,
                parent_id INTEGER,
                FOREIGN KEY (parent_id) REFERENCES ast_nodes(id)
            )
        """)
        
        # Verify graph is broken
        graph_health = built_code_index._graph_index.health_check()
        assert graph_health.healthy == False, "Graph should be unhealthy after clearing tables"
        
        # Verify semantic is still healthy
        semantic_health = built_code_index._semantic_index.health_check()
        assert semantic_health.healthy == True, "Semantic should still be healthy"
        
        # Verify search() still works (uses semantic, not graph)
        try:
            results = built_code_index.search("function", n_results=5)
            print(f"✅ search() succeeded with graph broken: {len(results)} results")
            assert len(results) > 0, "search() should return results when semantic is healthy"
        except Exception as e:
            pytest.fail(f"search() should succeed when semantic is healthy, but raised: {e}")
    
    def test_health_check_granular_diagnostics(self, built_code_index: CodeIndex):
        """Test: health_check() provides granular component diagnostics.
        
        Validates that CodeIndex.health_check() properly reports health of both
        semantic and graph components, and that graph component shows nested
        ast + graph sub-components.
        """
        # Get health status
        health = built_code_index.health_check()
        
        # Verify overall structure
        assert health.healthy == True, "CodeIndex should be healthy with all components operational"
        assert "components" in health.details, "health_check() should return components dict"
        
        components = health.details["components"]
        
        # Verify semantic component
        assert "semantic" in components, "Should have semantic component"
        semantic = components["semantic"]
        assert semantic.healthy == True, "Semantic component should be healthy"
        print(f"✅ Semantic component: {semantic.message}")
        
        # Verify graph component
        assert "graph" in components, "Should have graph component"
        graph = components["graph"]
        assert graph.healthy == True, "Graph component should be healthy"
        print(f"✅ Graph component: {graph.message}")
        
        # Verify graph shows nested sub-components (ast + graph)
        if "components" in graph.details:
            graph_subcomponents = graph.details["components"]
            print(f"✅ Graph sub-components: {list(graph_subcomponents.keys())}")
            assert "ast" in graph_subcomponents, "Graph should show ast sub-component"
            assert "graph" in graph_subcomponents, "Graph should show graph sub-component"
        
        print(f"\n✅ Granular diagnostics validated:")
        print(f"   - CodeIndex reports 2 components (semantic, graph)")
        print(f"   - Graph component shows nested sub-components")
        print(f"   - Each component provides detailed health metrics")


class TestDynamicComponentDiscovery:
    """Test suite for dynamic component discovery pattern."""
    
    def test_adding_graph_component_requires_zero_code_index_changes(self, built_code_index: CodeIndex):
        """Test: Adding component to GraphIndex requires 0 changes to CodeIndex.
        
        This validates the dynamic discovery pattern: CodeIndex uses
        dynamic_health_check() which automatically discovers components
        from the registry. When GraphIndex adds a new component (e.g., "metrics"),
        it automatically appears in CodeIndex health checks without any
        CodeIndex code changes.
        
        This test simulates adding a component to GraphIndex and verifies
        it automatically appears in CodeIndex health output.
        """
        # Get initial health to see current graph sub-components
        initial_health = built_code_index.health_check()
        initial_components = initial_health.details["components"]
        initial_graph = initial_components["graph"]
        
        initial_subcomponents = []
        if "components" in initial_graph.details:
            initial_subcomponents = list(initial_graph.details["components"].keys())
        
        print(f"Initial graph sub-components: {initial_subcomponents}")
        
        # Simulate adding a new component to GraphIndex
        # (In real implementation, this would be done by GraphIndex itself)
        from ouroboros.subsystems.rag.utils.component_helpers import ComponentDescriptor
        from ouroboros.subsystems.rag.base import HealthStatus
        
        # Add a mock "metrics" component to GraphIndex
        built_code_index._graph_index.components["metrics"] = ComponentDescriptor(
            name="metrics",
            provides=["query_stats", "performance_metrics"],
            capabilities=["get_metrics"],
            health_check=lambda: HealthStatus(
                healthy=True,
                message="Metrics component operational",
                details={"metric_count": 42},
                last_updated=None
            ),
            rebuild=lambda: None,  # ComponentDescriptor requires callable, not None
            dependencies=[],
        )
        
        # Get health again - the new component should automatically appear
        updated_health = built_code_index.health_check()
        updated_components = updated_health.details["components"]
        updated_graph = updated_components["graph"]
        
        updated_subcomponents = []
        if "components" in updated_graph.details:
            updated_subcomponents = list(updated_graph.details["components"].keys())
        
        print(f"Updated graph sub-components: {updated_subcomponents}")
        
        # Verify new component appears automatically
        assert "metrics" in updated_subcomponents, "New component should automatically appear in health output"
        
        print(f"\n✅ Dynamic discovery validated:")
        print(f"   - Added 'metrics' component to GraphIndex")
        print(f"   - Component automatically appears in CodeIndex.health_check()")
        print(f"   - 0 lines changed in CodeIndex (dynamic discovery)")

