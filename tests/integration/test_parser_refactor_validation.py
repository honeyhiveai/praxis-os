"""
Integration test for parser refactor - validate spec_execution_v1 works.

Tests the defensive SpecTasksParser on the actual parser refactor spec
to ensure the workflow system can execute it.
"""

from pathlib import Path

import pytest
from ouroboros.subsystems.workflow.parsers import SpecTasksParser


class TestParserRefactorValidation:
    """Validate parser works on the spec that defines the refactor itself."""

    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return SpecTasksParser()

    @pytest.fixture
    def spec_path(self):
        """Path to parser refactor spec."""
        return Path(
            ".praxis-os/specs/review/2025-11-05-parser-submodule-refactor/tasks.md"
        )

    def test_parser_can_load_spec(self, parser, spec_path):
        """Test: Parser can load and parse the refactor spec."""
        assert spec_path.exists(), f"Spec not found: {spec_path}"

        phases = parser.parse(spec_path)

        assert phases is not None
        assert len(phases) > 0

    def test_phase_count_correct(self, parser, spec_path):
        """Test: Parser extracts correct number of phases (9 expected)."""
        phases = parser.parse(spec_path)

        assert len(phases) == 9, f"Expected 9 phases, got {len(phases)}"

    def test_phase_shift_applied(self, parser, spec_path):
        """Test: Phase 0 in tasks.md becomes workflow Phase 1."""
        phases = parser.parse(spec_path)

        # Phase numbers should be 1-9 (shifted from 0-8)
        phase_numbers = [p.phase_number for p in phases]
        assert phase_numbers == list(
            range(1, 10)
        ), f"Expected phases 1-9, got {phase_numbers}"

    def test_phases_have_tasks(self, parser, spec_path):
        """Test: Phases extract tasks correctly."""
        phases = parser.parse(spec_path)

        # First 8 phases should have tasks (Phase 9 may have extras)
        for phase in phases[:8]:
            assert len(phase.tasks) > 0, f"Phase {phase.phase_number} has no tasks"

    def test_task_ids_normalized(self, parser, spec_path):
        """Test: Task IDs are normalized to phase.task format."""
        phases = parser.parse(spec_path)

        for phase in phases[:3]:  # Check first 3 phases
            for i, task in enumerate(phase.tasks, start=1):
                expected_id = f"{phase.phase_number}.{i}"
                assert (
                    task.task_id == expected_id
                ), f"Task ID not normalized: expected {expected_id}, got {task.task_id}"

    def test_phase_metadata_extracted(self, parser, spec_path):
        """Test: Phase names and metadata are extracted."""
        phases = parser.parse(spec_path)

        phase_1 = phases[0]
        assert "Foundation" in phase_1.phase_name or "Planning" in phase_1.phase_name
        assert phase_1.estimated_duration is not None

    def test_no_duplicates(self, parser, spec_path):
        """Test: No duplicate phase numbers."""
        phases = parser.parse(spec_path)

        phase_numbers = [p.phase_number for p in phases]
        assert len(phase_numbers) == len(
            set(phase_numbers)
        ), "Duplicate phase numbers detected"

    def test_sequential_phases(self, parser, spec_path):
        """Test: Phases are sequential with no gaps."""
        phases = parser.parse(spec_path)

        phase_numbers = sorted([p.phase_number for p in phases])
        for i in range(len(phase_numbers) - 1):
            diff = phase_numbers[i + 1] - phase_numbers[i]
            assert (
                diff == 1
            ), f"Phase gap detected: {phase_numbers[i]} -> {phase_numbers[i + 1]}"

    def test_parser_handles_section_format(self, parser, spec_path):
        """Test: Parser handles separated 'Detailed Tasks' sections."""
        phases = parser.parse(spec_path)

        # Phase 1 should have 3 tasks (from detailed section)
        phase_1 = phases[0]
        assert (
            len(phase_1.tasks) == 3
        ), f"Phase 1 should have 3 tasks, got {len(phase_1.tasks)}"
