"""
Unit tests for WorkflowRenderer class.

Tests the get_task_count() method for static workflows, including:
- Correct count retrieval for existing phases
- Error handling for missing phase directories
- Edge cases (empty phase, nonexistent workflow)
"""

import pytest
from pathlib import Path

from ouroboros.subsystems.workflow.workflow_renderer import (
    WorkflowRenderer,
    RendererError,
)


class TestGetTaskCount:
    """Test get_task_count() method for static workflows."""

    @pytest.fixture
    def renderer(self):
        """Create WorkflowRenderer with standard workflows directory."""
        # Get absolute path to workflows directory
        # Tests run from project root, so we need absolute path
        project_root = Path(__file__).parent.parent.parent  # tests/unit -> tests -> .praxis-os
        workflows_dir = project_root / "workflows"
        return WorkflowRenderer(workflows_dir)

    def test_get_task_count_for_existing_phase(self, renderer):
        """Test that task count is correctly retrieved for existing phase."""
        # Arrange
        workflow_type = "spec_creation_v1"
        phase = 0

        # Act
        count = renderer.get_task_count(workflow_type, phase)

        # Assert - should return number of unique task numbers
        assert isinstance(count, int)
        assert count > 0  # Should have at least one task
        assert count == 4  # spec_creation_v1 Phase 0 has tasks 0-3

    def test_get_task_count_returns_integer(self, renderer):
        """Test that method returns integer type."""
        # Arrange
        workflow_type = "spec_creation_v1"
        phase = 0

        # Act
        count = renderer.get_task_count(workflow_type, phase)

        # Assert
        assert isinstance(count, int)
        assert not isinstance(count, bool)  # bool is subclass of int in Python

    def test_get_task_count_for_missing_phase_directory_raises_error(self, renderer):
        """Test that RendererError is raised when phase directory doesn't exist."""
        # Arrange
        workflow_type = "spec_creation_v1"
        nonexistent_phase = 9999  # Phase that definitely doesn't exist

        # Act & Assert
        with pytest.raises(RendererError) as exc_info:
            renderer.get_task_count(workflow_type, nonexistent_phase)

        # Assert error details
        error = exc_info.value
        assert "Phase directory not found" in str(error)
        assert "mkdir -p" in str(error)  # Should include actionable fix

    def test_error_includes_mkdir_command(self, renderer):
        """Test that error includes actionable mkdir command for missing directory."""
        # Arrange
        workflow_type = "spec_creation_v1"
        missing_phase = 99

        # Act & Assert
        with pytest.raises(RendererError) as exc_info:
            renderer.get_task_count(workflow_type, missing_phase)

        # Assert mkdir command is present
        error_dict = exc_info.value.to_dict()
        assert "how_to_fix" in error_dict
        assert "mkdir" in error_dict["how_to_fix"]
        assert "phases/99" in error_dict["how_to_fix"]

    def test_get_task_count_for_nonexistent_workflow_raises_error(self, renderer):
        """Test that RendererError is raised for nonexistent workflow type."""
        # Arrange
        nonexistent_workflow = "fake_workflow_v99"
        phase = 0

        # Act & Assert
        with pytest.raises(RendererError) as exc_info:
            renderer.get_task_count(nonexistent_workflow, phase)

        # Assert error is about missing directory
        error = exc_info.value
        assert "Phase directory not found" in str(error)

    def test_get_task_count_for_different_phases(self, renderer):
        """Test that method works for different phase numbers."""
        # Arrange
        workflow_type = "spec_creation_v1"

        # Act - test multiple phases
        try:
            count_phase_0 = renderer.get_task_count(workflow_type, 0)
            count_phase_1 = renderer.get_task_count(workflow_type, 1)

            # Assert - both should return valid counts
            assert isinstance(count_phase_0, int)
            assert isinstance(count_phase_1, int)
            assert count_phase_0 > 0
            assert count_phase_1 > 0

        except RendererError:
            # If phase 1 doesn't exist, that's okay - not all workflows have multiple phases
            pytest.skip("Phase 1 doesn't exist for this workflow")

    def test_get_task_count_only_counts_markdown_files(self, renderer, tmp_path):
        """Test that only .md files matching pattern are counted."""
        # Arrange - create custom renderer with temp directory
        workflow_dir = tmp_path / "test_workflow_v1"
        phase_dir = workflow_dir / "phases" / "0"
        phase_dir.mkdir(parents=True)

        # Create task files matching pattern task-*-*.md
        (phase_dir / "task-1-first.md").write_text("# Task 1")
        (phase_dir / "task-2-second.md").write_text("# Task 2")
        (phase_dir / "task-3-third.md").write_text("# Task 3")

        # Create non-task files that should NOT be counted
        (phase_dir / "phase.md").write_text("# Phase")
        (phase_dir / "notes.txt").write_text("notes")
        (phase_dir / "README.md").write_text("# README")

        custom_renderer = WorkflowRenderer(tmp_path)

        # Act
        count = custom_renderer.get_task_count("test_workflow_v1", 0)

        # Assert - should only count task-*-*.md files
        # Debug: print what files were found if count is wrong
        if count != 3:
            found_files = list(phase_dir.glob("task-*-*.md"))
            pytest.fail(f"Expected 3 task files, got {count}. Files found: {[f.name for f in found_files]}")

        assert count == 3

    def test_get_task_count_with_zero_tasks(self, renderer, tmp_path):
        """Test that method returns 0 for phase directory with no task files."""
        # Arrange - create empty phase directory
        workflow_dir = tmp_path / "empty_workflow_v1"
        phase_dir = workflow_dir / "phases" / "0"
        phase_dir.mkdir(parents=True)

        # Create non-task file
        (phase_dir / "phase.md").write_text("# Phase")

        custom_renderer = WorkflowRenderer(tmp_path)

        # Act
        count = custom_renderer.get_task_count("empty_workflow_v1", 0)

        # Assert - should return 0, not raise error
        assert count == 0

    def test_get_task_count_performance(self, renderer):
        """Test that method completes in < 5ms for typical directories (NFR-P1)."""
        import time

        # Arrange
        workflow_type = "spec_creation_v1"
        phase = 0

        # Act - measure execution time
        start = time.perf_counter()
        count = renderer.get_task_count(workflow_type, phase)
        duration = time.perf_counter() - start

        # Assert - should complete in < 5ms (0.005 seconds)
        assert duration < 0.005, f"Task count took {duration*1000:.2f}ms (expected < 5ms)"
        assert count > 0  # Verify it actually worked


class TestGetTaskCountThreadSafety:
    """Test thread-safety of get_task_count() method."""

    @pytest.fixture
    def renderer(self):
        """Create WorkflowRenderer with standard workflows directory."""
        # Get absolute path to workflows directory
        project_root = Path(__file__).parent.parent.parent
        workflows_dir = project_root / "workflows"
        return WorkflowRenderer(workflows_dir)

    def test_concurrent_task_count_calls(self, renderer):
        """Test that concurrent calls to get_task_count are thread-safe."""
        import threading
        import time

        # Arrange
        workflow_type = "spec_creation_v1"
        phase = 0
        results = []
        errors = []

        def get_count():
            try:
                count = renderer.get_task_count(workflow_type, phase)
                results.append(count)
            except Exception as e:
                errors.append(e)

        # Act - run multiple threads
        threads = [threading.Thread(target=get_count) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=1.0)

        # Assert - all calls should succeed with same result
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        assert all(count == results[0] for count in results), "Inconsistent results from concurrent calls"

