"""Unit tests for CodePartition class.

Tests the partition container that wraps semantic, AST, and graph indexes
for a single repository with multiple domains.
"""

from pathlib import Path
from unittest.mock import Mock, MagicMock

import pytest

from ouroboros.config.schemas.indexes import DomainConfig, PartitionConfig
from ouroboros.subsystems.rag.code.partition import CodePartition
from ouroboros.utils.errors import ActionableError


class TestCodePartitionInit:
    """Test CodePartition initialization."""
    
    def test_init_basic(self):
        """Test basic partition initialization."""
        config = PartitionConfig(
            path="../",
            domains={
                "code": DomainConfig(include_paths=["src/"])
            }
        )
        
        partition = CodePartition(
            partition_name="test-repo",
            partition_config=config,
            base_path=Path("/tmp/test")
        )
        
        assert partition.name == "test-repo"
        assert partition.config == config
        assert len(partition.domains) == 1
        assert "code" in partition.domains
        assert partition.semantic is None  # Not injected
        assert partition.graph is None  # Not injected
    
    def test_init_with_multiple_domains(self):
        """Test partition with multiple domains."""
        config = PartitionConfig(
            path="../",
            domains={
                "code": DomainConfig(include_paths=["src/"]),
                "tests": DomainConfig(
                    include_paths=["tests/"],
                    metadata={"type": "tests"}
                ),
                "docs": DomainConfig(include_paths=["docs/"])
            }
        )
        
        partition = CodePartition(
            partition_name="multi-domain",
            partition_config=config,
            base_path=Path("/tmp/test")
        )
        
        assert len(partition.domains) == 3
        assert all(name in partition.domains for name in ["code", "tests", "docs"])
        assert partition.domains["tests"].metadata == {"type": "tests"}
    
    def test_init_with_injected_indexes(self):
        """Test partition with pre-initialized indexes."""
        config = PartitionConfig(
            path="../",
            domains={"code": DomainConfig(include_paths=["src/"])}
        )
        
        semantic_mock = Mock()
        graph_mock = Mock()
        
        partition = CodePartition(
            partition_name="test-repo",
            partition_config=config,
            base_path=Path("/tmp/test"),
            semantic_index=semantic_mock,
            graph_index=graph_mock
        )
        
        assert partition.semantic == semantic_mock
        assert partition.graph == graph_mock


class TestCodePartitionSearch:
    """Test CodePartition search routing."""
    
    def test_search_code_routes_to_semantic(self):
        """Test that search_code action routes to semantic index."""
        config = PartitionConfig(
            path="../",
            domains={"code": DomainConfig(include_paths=["src/"])}
        )
        
        semantic_mock = Mock()
        semantic_mock.search.return_value = [{"result": "test"}]
        
        partition = CodePartition(
            partition_name="test-repo",
            partition_config=config,
            base_path=Path("/tmp/test"),
            semantic_index=semantic_mock
        )
        
        results = partition.search(
            query="test query",
            action="search_code"
        )
        
        assert results == [{"result": "test"}]
        semantic_mock.search.assert_called_once()
        call_kwargs = semantic_mock.search.call_args.kwargs
        assert call_kwargs["query"] == "test query"
        assert call_kwargs["filters"]["partition"] == "test-repo"
    
    def test_search_with_domain_filter(self):
        """Test search with domain filtering."""
        config = PartitionConfig(
            path="../",
            domains={"code": DomainConfig(include_paths=["src/"])}
        )
        
        semantic_mock = Mock()
        semantic_mock.search.return_value = []
        
        partition = CodePartition(
            partition_name="test-repo",
            partition_config=config,
            base_path=Path("/tmp/test"),
            semantic_index=semantic_mock
        )
        
        partition.search(
            query="test",
            action="search_code",
            filters={"domain": "tests"}
        )
        
        call_kwargs = semantic_mock.search.call_args.kwargs
        assert call_kwargs["filters"]["partition"] == "test-repo"
        assert call_kwargs["filters"]["domain"] == "tests"
    
    def test_search_with_metadata_filters(self):
        """Test search with metadata filtering."""
        config = PartitionConfig(
            path="../",
            domains={"code": DomainConfig(include_paths=["src/"])}
        )
        
        semantic_mock = Mock()
        semantic_mock.search.return_value = []
        
        partition = CodePartition(
            partition_name="test-repo",
            partition_config=config,
            base_path=Path("/tmp/test"),
            semantic_index=semantic_mock
        )
        
        partition.search(
            query="test",
            action="search_code",
            filters={"framework": "openai", "type": "instrumentor"}
        )
        
        call_kwargs = semantic_mock.search.call_args.kwargs
        assert call_kwargs["filters"]["framework"] == "openai"
        assert call_kwargs["filters"]["type"] == "instrumentor"
    
    def test_search_ast_routes_to_graph(self):
        """Test that search_ast action routes to graph index."""
        config = PartitionConfig(
            path="../",
            domains={"code": DomainConfig(include_paths=["src/"])}
        )
        
        graph_mock = Mock()
        graph_mock.search_ast.return_value = [{"node": "test"}]
        
        partition = CodePartition(
            partition_name="test-repo",
            partition_config=config,
            base_path=Path("/tmp/test"),
            graph_index=graph_mock
        )
        
        results = partition.search(
            query="function_def",
            action="search_ast"
        )
        
        assert results == [{"node": "test"}]
        graph_mock.search_ast.assert_called_once()
        call_kwargs = graph_mock.search_ast.call_args.kwargs
        assert call_kwargs["pattern"] == "function_def"
        assert call_kwargs["filters"]["partition"] == "test-repo"
    
    def test_search_graph_actions_route_to_graph(self):
        """Test that graph traversal actions route to graph index."""
        config = PartitionConfig(
            path="../",
            domains={"code": DomainConfig(include_paths=["src/"])}
        )
        
        graph_mock = Mock()
        graph_mock.find_callers.return_value = []
        graph_mock.find_dependencies.return_value = []
        graph_mock.find_call_paths.return_value = []
        
        partition = CodePartition(
            partition_name="test-repo",
            partition_config=config,
            base_path=Path("/tmp/test"),
            graph_index=graph_mock
        )
        
        # Test find_callers
        partition.search(query="test_func", action="find_callers")
        graph_mock.find_callers.assert_called_once_with(symbol_name="test_func", max_depth=10)
        
        # Test find_dependencies
        partition.search(query="test_func", action="find_dependencies")
        graph_mock.find_dependencies.assert_called_once_with(symbol_name="test_func", max_depth=10)
        
        # Test find_call_paths
        partition.search(query="test_func", action="find_call_paths", to_symbol="target_func")
        graph_mock.find_call_paths.assert_called_once_with(from_symbol="test_func", to_symbol="target_func", max_depth=10)
    
    def test_search_without_semantic_raises_error(self):
        """Test that search_code without semantic index raises error."""
        config = PartitionConfig(
            path="../",
            domains={"code": DomainConfig(include_paths=["src/"])}
        )
        
        partition = CodePartition(
            partition_name="test-repo",
            partition_config=config,
            base_path=Path("/tmp/test")
            # No semantic_index injected
        )
        
        with pytest.raises(ActionableError) as exc_info:
            partition.search(query="test", action="search_code")
        
        assert "SemanticIndex not initialized" in str(exc_info.value)
    
    def test_search_without_graph_raises_error(self):
        """Test that graph actions without graph index raises error."""
        config = PartitionConfig(
            path="../",
            domains={"code": DomainConfig(include_paths=["src/"])}
        )
        
        partition = CodePartition(
            partition_name="test-repo",
            partition_config=config,
            base_path=Path("/tmp/test")
            # No graph_index injected
        )
        
        with pytest.raises(ActionableError) as exc_info:
            partition.search(query="test", action="find_callers")
        
        assert "GraphIndex not initialized" in str(exc_info.value)
    
    def test_search_invalid_action_raises_error(self):
        """Test that invalid action raises error."""
        config = PartitionConfig(
            path="../",
            domains={"code": DomainConfig(include_paths=["src/"])}
        )
        
        partition = CodePartition(
            partition_name="test-repo",
            partition_config=config,
            base_path=Path("/tmp/test")
        )
        
        with pytest.raises(ActionableError) as exc_info:
            partition.search(query="test", action="invalid_action")
        
        assert "Invalid action 'invalid_action'" in str(exc_info.value)


class TestCodePartitionHealthCheck:
    """Test CodePartition health check aggregation."""
    
    def test_health_check_all_healthy(self):
        """Test health check when all sub-indexes are healthy."""
        from ouroboros.subsystems.rag.base import HealthStatus
        
        config = PartitionConfig(
            path="../",
            domains={
                "code": DomainConfig(include_paths=["src/"]),
                "tests": DomainConfig(include_paths=["tests/"])
            }
        )
        
        semantic_mock = Mock()
        semantic_mock.health_check.return_value = HealthStatus(
            healthy=True,
            message="Semantic index healthy",
            details={"name": "semantic"}
        )
        
        graph_mock = Mock()
        graph_mock.health_check.return_value = HealthStatus(
            healthy=True,
            message="Graph index healthy",
            details={"name": "graph"}
        )
        
        partition = CodePartition(
            partition_name="test-repo",
            partition_config=config,
            base_path=Path("/tmp/test"),
            semantic_index=semantic_mock,
            graph_index=graph_mock
        )
        
        health = partition.health_check()
        
        assert isinstance(health, HealthStatus)
        assert health.healthy is True
        assert "test-repo" in health.message
        assert health.details["domain_count"] == 2
        assert health.details["domains"] == ["code", "tests"]
        assert len(health.details["sub_components"]) == 2
    
    def test_health_check_one_degraded(self):
        """Test health check when one sub-index is degraded."""
        from ouroboros.subsystems.rag.base import HealthStatus
        
        config = PartitionConfig(
            path="../",
            domains={"code": DomainConfig(include_paths=["src/"])}
        )
        
        semantic_mock = Mock()
        semantic_mock.health_check.return_value = HealthStatus(
            healthy=True,
            message="Semantic index healthy",
            details={"name": "semantic"}
        )
        
        graph_mock = Mock()
        graph_mock.health_check.return_value = HealthStatus(
            healthy=False,  # One index unhealthy
            message="Graph index degraded",
            details={"name": "graph"}
        )
        
        partition = CodePartition(
            partition_name="test-repo",
            partition_config=config,
            base_path=Path("/tmp/test"),
            semantic_index=semantic_mock,
            graph_index=graph_mock
        )
        
        health = partition.health_check()
        
        assert isinstance(health, HealthStatus)
        assert health.healthy is False  # Partition is degraded if any sub-index is
        assert "degraded" in health.message
        assert len(health.details["sub_components"]) == 2
    
    def test_health_check_no_indexes(self):
        """Test health check when no indexes are initialized."""
        from ouroboros.subsystems.rag.base import HealthStatus
        
        config = PartitionConfig(
            path="../",
            domains={"code": DomainConfig(include_paths=["src/"])}
        )
        
        partition = CodePartition(
            partition_name="test-repo",
            partition_config=config,
            base_path=Path("/tmp/test")
            # No indexes injected
        )
        
        health = partition.health_check()
        
        assert isinstance(health, HealthStatus)
        assert "test-repo" in health.message
        assert health.healthy is True  # No indexes = nothing to fail
        assert len(health.details["sub_components"]) == 0

