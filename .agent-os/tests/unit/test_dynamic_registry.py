"""
Unit tests for DynamicContentRegistry.

Tests template loading, source parsing, content rendering, and caching.
"""

import time
from pathlib import Path

import pytest

from mcp_server.core.dynamic_registry import (
    DynamicContentRegistry,
    DynamicRegistryError,
)
from mcp_server.core.parsers import SpecTasksParser


class TestDynamicContentRegistry:
    """Test suite for DynamicContentRegistry."""

    @pytest.fixture
    def sample_templates(self, tmp_path):
        """Create sample template files."""
        phase_template = tmp_path / "phase-template.md"
        phase_template.write_text(
            """# Phase [PHASE_NUMBER]: [PHASE_NAME]

**Goal:** [PHASE_DESCRIPTION]
**Duration:** [ESTIMATED_DURATION]
**Tasks:** [TASK_COUNT] tasks

## Validation Gate
[VALIDATION_GATE]

🎯 NEXT-MANDATORY: Phase [NEXT_PHASE_NUMBER]
"""
        )

        task_template = tmp_path / "task-template.md"
        task_template.write_text(
            """# Task [TASK_ID]: [TASK_NAME]

**Phase:** [PHASE_NUMBER] - [PHASE_NAME]
**Description:** [TASK_DESCRIPTION]
**Time:** [ESTIMATED_TIME]
**Dependencies:** [DEPENDENCIES]

🛑 EXECUTE-NOW: Complete acceptance criteria

## Acceptance Criteria
[ACCEPTANCE_CRITERIA]

🎯 NEXT-MANDATORY: Task [NEXT_TASK_NUMBER]
"""
        )

        return phase_template, task_template

    @pytest.fixture
    def sample_source(self, tmp_path):
        """Create sample source tasks.md file."""
        source = tmp_path / "tasks.md"
        content = """### Phase 1: Foundation

**Goal:** Build core infrastructure
**Estimated Duration:** 4 hours

**Tasks:**

- [ ] **Task 1.1**: Create models
  - **Estimated Time**: 2 hours
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - [ ] Models created
    - [ ] Tests pass

- [ ] **Task 1.2**: Create parsers
  - **Estimated Time**: 2 hours
  - **Dependencies**: Task 1.1
  - **Acceptance Criteria**:
    - [ ] Parser works
    - [ ] Coverage ≥ 90%

**Validation Gate:**
- [ ] All tests pass
- [ ] No linting errors

---

### Phase 2: Integration

**Goal:** Wire components together
**Estimated Duration:** 2 hours

**Tasks:**

- [ ] **Task 2.1**: Integrate registry
  - **Estimated Time**: 2 hours
  - **Dependencies**: Task 1.1, Task 1.2
  - **Acceptance Criteria**:
    - [ ] Integration complete

**Validation Gate:**
- [ ] Integration tests pass
"""
        source.write_text(content)
        return source

    @pytest.fixture
    def registry(self, sample_templates, sample_source):
        """Create a registry instance."""
        phase_template, task_template = sample_templates
        parser = SpecTasksParser()

        return DynamicContentRegistry(
            workflow_type="test_workflow",
            phase_template_path=phase_template,
            task_template_path=task_template,
            source_path=sample_source,
            parser=parser,
        )

    def test_create_registry(self, registry):
        """Test creating registry instance."""
        assert registry is not None
        assert registry.workflow_type == "test_workflow"
        assert registry.content is not None
        assert len(registry.content.phases) == 2

    def test_template_not_found(self, tmp_path, sample_source):
        """Test error when template file not found."""
        nonexistent = tmp_path / "does_not_exist.md"
        valid_template = tmp_path / "valid.md"
        valid_template.write_text("# Template")

        parser = SpecTasksParser()

        with pytest.raises(DynamicRegistryError, match="Template not found"):
            DynamicContentRegistry(
                workflow_type="test",
                phase_template_path=nonexistent,
                task_template_path=valid_template,
                source_path=sample_source,
                parser=parser,
            )

    def test_source_not_found(self, sample_templates, tmp_path):
        """Test error when source file not found."""
        phase_template, task_template = sample_templates
        nonexistent_source = tmp_path / "missing.md"

        parser = SpecTasksParser()

        with pytest.raises(DynamicRegistryError, match="Failed to parse source"):
            DynamicContentRegistry(
                workflow_type="test",
                phase_template_path=phase_template,
                task_template_path=task_template,
                source_path=nonexistent_source,
                parser=parser,
            )

    def test_empty_source(self, sample_templates, tmp_path):
        """Test error with empty source file."""
        phase_template, task_template = sample_templates
        empty_source = tmp_path / "empty.md"
        empty_source.write_text("")

        parser = SpecTasksParser()

        with pytest.raises(DynamicRegistryError, match="Failed to parse source"):
            DynamicContentRegistry(
                workflow_type="test",
                phase_template_path=phase_template,
                task_template_path=task_template,
                source_path=empty_source,
                parser=parser,
            )

    def test_get_phase_content(self, registry):
        """Test getting rendered phase content."""
        phase1_content = registry.get_phase_content(1)

        assert "Phase 1: Foundation" in phase1_content
        assert "Build core infrastructure" in phase1_content
        assert "4 hours" in phase1_content
        assert "**Tasks:** 2 tasks" in phase1_content
        assert "- [ ] All tests pass" in phase1_content
        assert "- [ ] No linting errors" in phase1_content
        assert "🎯 NEXT-MANDATORY: Phase 2" in phase1_content

    def test_get_phase_content_caching(self, registry):
        """Test that phase content is cached."""
        # First render
        content1 = registry.get_phase_content(1)
        # Second render (should be cached)
        content2 = registry.get_phase_content(1)

        assert content1 == content2
        assert 1 in registry.content._rendered_phases

    def test_get_phase_content_invalid_phase(self, registry):
        """Test error when getting nonexistent phase."""
        with pytest.raises(IndexError, match="Phase 99 not found"):
            registry.get_phase_content(99)

    def test_get_task_content(self, registry):
        """Test getting rendered task content."""
        task_content = registry.get_task_content(1, 1)

        assert "Task 1.1: Create models" in task_content
        assert "**Phase:** 1 - Foundation" in task_content
        assert "Create models" in task_content
        assert "2 hours" in task_content
        assert "**Dependencies:** None" in task_content
        assert "- [ ] Models created" in task_content
        assert "- [ ] Tests pass" in task_content
        assert "🛑 EXECUTE-NOW: Complete acceptance criteria" in task_content

    def test_get_task_content_with_dependencies(self, registry):
        """Test task content with dependencies."""
        task_content = registry.get_task_content(1, 2)

        assert "Task 1.2: Create parsers" in task_content
        assert "**Dependencies:** 1.1" in task_content

    def test_get_task_content_caching(self, registry):
        """Test that task content is cached."""
        # First render
        content1 = registry.get_task_content(1, 1)
        # Second render (should be cached)
        content2 = registry.get_task_content(1, 1)

        assert content1 == content2
        assert (1, 1) in registry.content._rendered_tasks

    def test_get_task_content_invalid_phase(self, registry):
        """Test error when getting task from nonexistent phase."""
        with pytest.raises(IndexError, match="Phase 99 not found"):
            registry.get_task_content(99, 1)

    def test_get_task_content_invalid_task(self, registry):
        """Test error when getting nonexistent task."""
        with pytest.raises(IndexError, match="Task 99 not found"):
            registry.get_task_content(1, 99)

    def test_get_phase_metadata(self, registry):
        """Test getting phase metadata."""
        metadata = registry.get_phase_metadata(1)

        assert metadata["phase_number"] == 1
        assert metadata["phase_name"] == "Foundation"
        assert metadata["description"] == "Build core infrastructure"
        assert metadata["estimated_duration"] == "4 hours"
        assert metadata["task_count"] == 2
        assert len(metadata["tasks"]) == 2
        assert len(metadata["validation_gate"]) == 2

        # Check first task metadata
        task1 = metadata["tasks"][0]
        assert task1["task_number"] == 1
        assert task1["task_id"] == "1.1"
        assert task1["task_name"] == "Create models"
        assert task1["estimated_time"] == "2 hours"
        assert task1["dependencies"] == []

    def test_get_phase_metadata_invalid_phase(self, registry):
        """Test error when getting metadata for nonexistent phase."""
        with pytest.raises(IndexError, match="Phase 99 not found"):
            registry.get_phase_metadata(99)

    def test_get_total_phases(self, registry):
        """Test getting total phase count."""
        assert registry.get_total_phases() == 2

    def test_has_phase(self, registry):
        """Test checking if phase exists."""
        assert registry.has_phase(1) is True
        assert registry.has_phase(2) is True
        assert registry.has_phase(3) is False
        assert registry.has_phase(99) is False

    def test_get_all_phases_metadata(self, registry):
        """Test getting metadata for all phases."""
        all_metadata = registry.get_all_phases_metadata()

        assert len(all_metadata) == 2
        assert all_metadata[0]["phase_number"] == 1
        assert all_metadata[0]["phase_name"] == "Foundation"
        assert all_metadata[1]["phase_number"] == 2
        assert all_metadata[1]["phase_name"] == "Integration"

    def test_rendering_performance(self, registry):
        """Test that first render is under 100ms."""
        start = time.perf_counter()
        registry.get_phase_content(1)
        duration_ms = (time.perf_counter() - start) * 1000

        assert (
            duration_ms < 100
        ), f"First render took {duration_ms:.2f}ms (target: <100ms)"

    def test_cached_rendering_performance(self, registry):
        """Test that cached render is very fast (<5ms)."""
        # Warm up cache
        registry.get_phase_content(1)

        # Measure cached access
        start = time.perf_counter()
        registry.get_phase_content(1)
        duration_ms = (time.perf_counter() - start) * 1000

        assert duration_ms < 5, f"Cached render took {duration_ms:.2f}ms (target: <5ms)"

    def test_multiple_phase_rendering(self, registry):
        """Test rendering multiple phases."""
        phase1 = registry.get_phase_content(1)
        phase2 = registry.get_phase_content(2)

        assert "Phase 1: Foundation" in phase1
        assert "Phase 2: Integration" in phase2
        assert phase1 != phase2

    def test_task_with_multiple_dependencies(self, registry):
        """Test task with multiple dependencies renders correctly."""
        task_content = registry.get_task_content(2, 1)

        assert "**Dependencies:** 1.1, 1.2" in task_content

    def test_source_path_stored(self, registry, sample_source):
        """Test that source path is stored in content."""
        assert registry.content.source_path == str(sample_source)

    def test_workflow_type_stored(self, registry):
        """Test that workflow type is stored."""
        assert registry.workflow_type == "test_workflow"
        assert registry.content.workflow_type == "test_workflow"
