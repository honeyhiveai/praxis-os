"""
Integration test for parser against REAL specs from the repository.

Tests defensive parser on actual tasks.md files to ensure it handles
format variations that exist in practice, not just assumed variations.
"""

from pathlib import Path

import pytest
from ouroboros.subsystems.workflow.parsers import SpecTasksParser


class TestParserRealSpecs:
    """Test parser against real specs from completed/ and review/ directories."""

    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return SpecTasksParser()

    @pytest.fixture
    def spec_paths(self):
        """Real spec paths to test against."""
        base = Path(".praxis-os/specs")
        return [
            # Format: Checkbox list with bold Task markers
            base / "completed/2025-10-07-spec-creation-workflow-v1/tasks.md",
            # Format: Subheaders (####) for tasks, no checkboxes
            base / "completed/2025-10-13-thread-safety-fixes/tasks.md",
            # Format: Subheaders with emoji completion markers
            base / "completed/2025-11-03-ouroboros-mcp-server/tasks.md",
            # Format: Mixed - the parser refactor spec we're implementing
            base / "review/2025-11-05-parser-submodule-refactor/tasks.md",
        ]

    def test_all_specs_parse_successfully(self, parser, spec_paths):
        """Test: Parser can load all real specs without errors."""
        for spec_path in spec_paths:
            assert spec_path.exists(), f"Spec not found: {spec_path}"

            # Should not raise
            phases = parser.parse(spec_path)
            assert phases is not None
            assert len(phases) > 0, f"No phases extracted from {spec_path}"

    def test_all_specs_extract_tasks(self, parser, spec_paths):
        """Test: Parser extracts tasks from all real specs."""
        for spec_path in spec_paths:
            phases = parser.parse(spec_path)
            total_tasks = sum(len(p.tasks) for p in phases)

            # All specs should have tasks
            assert total_tasks > 0, f"No tasks extracted from {spec_path}"

    def test_spec_creation_workflow_format(self, parser):
        """Test: Checkbox list format (- [x] **Task N.N**:)."""
        spec_path = Path(
            ".praxis-os/specs/completed/2025-10-07-spec-creation-workflow-v1/tasks.md"
        )
        phases = parser.parse(spec_path)

        # Known: This spec has 4 phases
        assert len(phases) == 4

        # Phase 1 should have 3 tasks
        phase_1 = phases[0]
        assert len(phase_1.tasks) == 3

        # Task IDs should be normalized
        assert phase_1.tasks[0].task_id == "1.1"
        assert phase_1.tasks[1].task_id == "1.2"
        assert phase_1.tasks[2].task_id == "1.3"

    def test_thread_safety_format(self, parser):
        """Test: Subheader format (#### Task N.N: Title)."""
        spec_path = Path(
            ".praxis-os/specs/completed/2025-10-13-thread-safety-fixes/tasks.md"
        )
        phases = parser.parse(spec_path)

        # Phase 1 should extract tasks from #### subheaders
        phase_1 = phases[0]
        assert len(phase_1.tasks) > 0

        # Check task names are extracted
        task_names = [t.task_name for t in phase_1.tasks]
        assert any("Metadata Cache" in name for name in task_names)

    def test_ouroboros_format(self, parser):
        """Test: Subheader with emoji format (#### Task N.N: Title ✅)."""
        spec_path = Path(
            ".praxis-os/specs/completed/2025-11-03-ouroboros-mcp-server/tasks.md"
        )
        phases = parser.parse(spec_path)

        # Known: Ouroboros spec has 8 phases
        assert len(phases) == 8

        # Should extract tasks despite emoji markers
        total_tasks = sum(len(p.tasks) for p in phases)
        assert total_tasks > 20  # Has many tasks

    def test_phase_numbers_sequential(self, parser, spec_paths):
        """Test: All specs have sequential phase numbers."""
        for spec_path in spec_paths:
            phases = parser.parse(spec_path)
            phase_numbers = sorted([p.phase_number for p in phases])

            # Check sequential
            for i in range(len(phase_numbers) - 1):
                diff = phase_numbers[i + 1] - phase_numbers[i]
                assert diff == 1, (
                    f"Phase gap in {spec_path}: "
                    f"{phase_numbers[i]} -> {phase_numbers[i + 1]}"
                )

    def test_task_ids_format(self, parser, spec_paths):
        """Test: Task IDs follow phase.task format."""
        for spec_path in spec_paths:
            phases = parser.parse(spec_path)

            for phase in phases:
                for task in phase.tasks:
                    # Should be "N.N" format
                    parts = task.task_id.split(".")
                    assert len(parts) == 2, (
                        f"Invalid task ID format: {task.task_id} " f"in {spec_path}"
                    )
                    assert parts[0].isdigit()
                    assert parts[1].isdigit()

    def test_different_formats_produce_consistent_structure(self, parser):
        """Test: Different markdown formats produce same data structure."""
        specs = [
            Path(
                ".praxis-os/specs/completed/2025-10-07-spec-creation-workflow-v1/tasks.md"
            ),
            Path(".praxis-os/specs/completed/2025-10-13-thread-safety-fixes/tasks.md"),
        ]

        results = []
        for spec_path in specs:
            phases = parser.parse(spec_path)
            # Verify structure consistency
            for phase in phases:
                assert hasattr(phase, "phase_number")
                assert hasattr(phase, "phase_name")
                assert hasattr(phase, "tasks")
                for task in phase.tasks:
                    assert hasattr(task, "task_id")
                    assert hasattr(task, "task_name")
            results.append(phases)

        # Both should have valid structures
        assert all(len(r) > 0 for r in results)
