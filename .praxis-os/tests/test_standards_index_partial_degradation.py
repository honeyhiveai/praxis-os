"""Integration tests for StandardsIndex cascading health checks and partial degradation.

Tests validate that StandardsIndex properly registers components (vector, fts, metadata)
and that the dynamic health check provides granular diagnostics for each component.

Since StandardsIndex uses a unified LanceDB table architecture (not separate tables
like GraphIndex), we focus on testing health check reporting rather than actual
partial degradation scenarios.

Test Coverage:
    - Health check reports component-level diagnostics (vector, fts, metadata)
    - Component registration with correct dependencies
    - Graceful degradation when optional components are disabled in config
    - Dynamic component discovery via fractal health check pattern

Traceability:
    - Task 3.3: Integration tests for StandardsIndex partial degradation
    - FR-008: Partial degradation detection
    - FR-009: Targeted diagnostics
"""

import pytest
from pathlib import Path

from ouroboros.config.schemas.indexes import StandardsIndexConfig, VectorConfig, FTSConfig, MetadataFilteringConfig
from ouroboros.subsystems.rag.standards.container import StandardsIndex


@pytest.fixture(scope="function")
def test_standards_dir(tmp_path: Path) -> Path:
    """Create temporary directory with test standard markdown files.
    
    Creates simple markdown documents for testing StandardsIndex functionality.
    
    Returns:
        Path to temporary directory with test standards
    """
    standards_dir = tmp_path / "test_standards"
    standards_dir.mkdir()
    
    # Standard 1: Workflow documentation
    (standards_dir / "workflow-patterns.md").write_text("""# Workflow Patterns

## Overview
Workflows provide structured, phase-gated processes for AI agents.

## Key Concepts
- Phase gating: Sequential execution with validation
- Evidence collection: Document task completion
- Breadcrumb navigation: Guide agents through steps
""")
    
    # Standard 2: Testing documentation
    (standards_dir / "testing-strategy.md").write_text("""# Testing Strategy

## Principles
- Test coverage: 80%+ for production code
- Integration tests: Validate component interactions
- Partial degradation: Test graceful failure modes

## Patterns
- Use fixtures for test data
- Isolate tests with function scope
- Validate acceptance criteria systematically
""")
    
    return standards_dir


@pytest.fixture(scope="function")
def built_standards_index(test_standards_dir: Path, tmp_path: Path) -> StandardsIndex:
    """Create and build StandardsIndex with test standards.
    
    Returns fully built index with vector, FTS, and metadata indexes populated.
    
    Returns:
        StandardsIndex: Built index ready for testing
    """
    # Create config with required fields
    config = StandardsIndexConfig(
        source_paths=[str(test_standards_dir)],  # Convert Path to string
        vector=VectorConfig(
            model="sentence-transformers/all-MiniLM-L6-v2",
            dimension=384
        ),
        fts=FTSConfig(
            tokenizer="default",
            enabled=True
        ),
        metadata_filtering=MetadataFilteringConfig(
            enabled=True
        )
    )
    
    # Create index with temporary base path
    index = StandardsIndex(config, tmp_path)
    
    # Build index
    index.build(source_paths=[test_standards_dir], force=True)
    
    return index


def test_health_check_all_components_healthy(built_standards_index: StandardsIndex):
    """Test that health_check() reports all components healthy after build.
    
    Validates:
        - Overall health is True
        - 3 components registered (vector, fts, metadata)
        - Each component reports healthy status
        - Capabilities map includes expected operations
    """
    health = built_standards_index.health_check()
    
    # Overall health should be True
    assert health.healthy, f"Index should be healthy after build: {health.message}"
    
    # Should have 3 components
    assert "components" in health.details, "Health status should include component details"
    components = health.details["components"]
    assert len(components) == 3, f"Should have 3 components (vector, fts, metadata), got {len(components)}"
    
    # Check each component
    assert "vector" in components, "Should have vector component"
    assert "fts" in components, "Should have fts component"
    assert "metadata" in components, "Should have metadata component"
    
    # All components should be healthy
    for comp_name, comp_health in components.items():
        assert comp_health.healthy, f"Component {comp_name} should be healthy: {comp_health.message}"
    
    # Check capabilities
    assert "capabilities" in health.details, "Health status should include capabilities"
    capabilities = health.details["capabilities"]
    
    # Should have search capabilities from vector and fts components
    assert "vector_search" in capabilities, "Should have vector_search capability"
    assert "fts_search" in capabilities or "keyword_search" in capabilities, "Should have FTS search capability"
    assert "hybrid_search" in capabilities, "Should have hybrid_search capability"


def test_component_dependencies(built_standards_index: StandardsIndex):
    """Test that components have correct dependency declarations.
    
    Validates:
        - Vector has no dependencies (base table)
        - FTS depends on vector
        - Metadata depends on vector
    """
    components = built_standards_index.components
    
    # Vector should have no dependencies
    assert components["vector"].dependencies == [], \
        f"Vector should have no dependencies, got {components['vector'].dependencies}"
    
    # FTS should depend on vector
    assert components["fts"].dependencies == ["vector"], \
        f"FTS should depend on vector, got {components['fts'].dependencies}"
    
    # Metadata should depend on vector
    assert components["metadata"].dependencies == ["vector"], \
        f"Metadata should depend on vector, got {components['metadata'].dependencies}"


def test_fts_disabled_graceful_degradation(test_standards_dir: Path, tmp_path: Path):
    """Test that index works with FTS disabled in config.
    
    Validates:
        - Index can be built with FTS disabled
        - FTS component reports as disabled but healthy
        - Vector and metadata components remain healthy
        - Overall health is True (FTS is optional)
    """
    # Create config with FTS disabled
    config = StandardsIndexConfig(
        source_paths=[str(test_standards_dir)],
        vector=VectorConfig(
            model="sentence-transformers/all-MiniLM-L6-v2",
            dimension=384
        ),
        fts=FTSConfig(
            tokenizer="default",
            enabled=False  # Disable FTS
        ),
        metadata_filtering=MetadataFilteringConfig(
            enabled=True
        )
    )
    
    index = StandardsIndex(config, tmp_path)
    index.build(source_paths=[test_standards_dir], force=True)
    
    # Check health
    health = index.health_check()
    
    # Overall should still be healthy (FTS is optional)
    assert health.healthy, f"Index should be healthy with FTS disabled: {health.message}"
    
    # Check FTS component status
    components = health.details["components"]
    fts_health = components["fts"]
    
    # FTS should report as disabled but healthy
    assert fts_health.healthy, "FTS should be healthy even when disabled"
    assert "disabled" in fts_health.message.lower() or "not required" in fts_health.message.lower(), \
        f"FTS message should indicate it's disabled: {fts_health.message}"


def test_metadata_filtering_disabled_graceful_degradation(test_standards_dir: Path, tmp_path: Path):
    """Test that index works with metadata filtering disabled in config.
    
    Validates:
        - Index can be built with metadata filtering disabled
        - Metadata component reports as disabled but healthy
        - Vector and FTS components remain healthy
        - Overall health is True (metadata filtering is optional)
    """
    # Create config with metadata filtering disabled
    config = StandardsIndexConfig(
        source_paths=[str(test_standards_dir)],
        vector=VectorConfig(
            model="sentence-transformers/all-MiniLM-L6-v2",
            dimension=384
        ),
        fts=FTSConfig(
            tokenizer="default",
            enabled=True
        ),
        metadata_filtering=MetadataFilteringConfig(
            enabled=False  # Disable scalar indexing
        )
    )
    
    index = StandardsIndex(config, tmp_path)
    index.build(source_paths=[test_standards_dir], force=True)
    
    # Check health
    health = index.health_check()
    
    # Overall should still be healthy (metadata is optional)
    assert health.healthy, f"Index should be healthy with scalar indexing disabled: {health.message}"
    
    # Check metadata component status
    components = health.details["components"]
    metadata_health = components["metadata"]
    
    # Metadata should report as disabled but healthy
    assert metadata_health.healthy, "Metadata should be healthy even when disabled"
    assert "disabled" in metadata_health.message.lower() or "not optimized" in metadata_health.message.lower(), \
        f"Metadata message should indicate it's disabled: {metadata_health.message}"


def test_dynamic_component_discovery(built_standards_index: StandardsIndex):
    """Test that dynamic_health_check discovers all registered components.
    
    Validates:
        - Health check aggregates all components without hardcoded names
        - Adding components to registry doesn't require health_check() changes
        - Fractal pattern: components discovered dynamically from registry
    """
    # Get component count from registry
    registry_component_count = len(built_standards_index.components)
    
    # Get component count from health check
    health = built_standards_index.health_check()
    health_component_count = len(health.details["components"])
    
    # Should match (dynamic discovery)
    assert health_component_count == registry_component_count, \
        f"Health check should discover all {registry_component_count} components, found {health_component_count}"
    
    # Component names should match
    registry_names = set(built_standards_index.components.keys())
    health_names = set(health.details["components"].keys())
    
    assert registry_names == health_names, \
        f"Component names should match: registry={registry_names}, health={health_names}"

