"""
Unit tests for dynamic workflow models.

Tests DynamicTask, DynamicPhase, and DynamicWorkflowContent dataclasses.
"""

import pytest

from mcp_server.models.workflow import DynamicPhase, DynamicTask, DynamicWorkflowContent


class TestDynamicTask:
    """Test suite for DynamicTask dataclass."""

    def test_create_basic_task(self):
        """Test creating a basic task with all fields."""
        task = DynamicTask(
            task_id="1.1",
            task_name="Create models",
            description="Create data models for dynamic workflows",
            estimated_time="2 hours",
            dependencies=[],
            acceptance_criteria=["Models created", "Tests passing"],
        )

        assert task.task_id == "1.1"
        assert task.task_name == "Create models"
        assert task.description == "Create data models for dynamic workflows"
        assert task.estimated_time == "2 hours"
        assert task.dependencies == []
        assert len(task.acceptance_criteria) == 2

    def test_task_with_dependencies(self):
        """Test task with dependencies."""
        task = DynamicTask(
            task_id="2.3",
            task_name="Integration test",
            description="Test integration",
            estimated_time="1 hour",
            dependencies=["2.1", "2.2"],
            acceptance_criteria=["Tests pass"],
        )

        assert task.dependencies == ["2.1", "2.2"]

    def test_task_serialization(self):
        """Test task serialization to dict."""
        task = DynamicTask(
            task_id="1.1",
            task_name="Test",
            description="Description",
            estimated_time="1 hour",
            dependencies=["1.0"],
            acceptance_criteria=["Criterion 1", "Criterion 2"],
        )

        task_dict = task.to_dict()

        assert task_dict["task_id"] == "1.1"
        assert task_dict["task_name"] == "Test"
        assert task_dict["description"] == "Description"
        assert task_dict["estimated_time"] == "1 hour"
        assert task_dict["dependencies"] == ["1.0"]
        assert len(task_dict["acceptance_criteria"]) == 2

    def test_task_deserialization(self):
        """Test task deserialization from dict."""
        task_dict = {
            "task_id": "1.1",
            "task_name": "Test",
            "description": "Description",
            "estimated_time": "1 hour",
            "dependencies": [],
            "acceptance_criteria": ["Criterion"],
        }

        task = DynamicTask.from_dict(task_dict)

        assert task.task_id == "1.1"
        assert task.task_name == "Test"
        assert task.description == "Description"
        assert task.estimated_time == "1 hour"
        assert task.dependencies == []
        assert task.acceptance_criteria == ["Criterion"]


class TestDynamicPhase:
    """Test suite for DynamicPhase dataclass."""

    def test_create_basic_phase(self):
        """Test creating a basic phase with tasks."""
        tasks = [
            DynamicTask(
                task_id="1.1",
                task_name="Task 1",
                description="First task",
                estimated_time="1 hour",
                dependencies=[],
                acceptance_criteria=["Done"],
            ),
            DynamicTask(
                task_id="1.2",
                task_name="Task 2",
                description="Second task",
                estimated_time="2 hours",
                dependencies=["1.1"],
                acceptance_criteria=["Complete"],
            ),
        ]

        phase = DynamicPhase(
            phase_number=1,
            phase_name="Core Infrastructure",
            description="Build foundation",
            estimated_duration="6-8 hours",
            tasks=tasks,
            validation_gate=["All tests pass", "No linting errors"],
        )

        assert phase.phase_number == 1
        assert phase.phase_name == "Core Infrastructure"
        assert phase.description == "Build foundation"
        assert phase.estimated_duration == "6-8 hours"
        assert len(phase.tasks) == 2
        assert len(phase.validation_gate) == 2

    def test_get_task_by_number(self):
        """Test retrieving task by number (1-indexed)."""
        tasks = [
            DynamicTask(
                task_id="1.1",
                task_name="Task 1",
                description="First",
                estimated_time="1h",
                dependencies=[],
                acceptance_criteria=[],
            ),
            DynamicTask(
                task_id="1.2",
                task_name="Task 2",
                description="Second",
                estimated_time="1h",
                dependencies=[],
                acceptance_criteria=[],
            ),
        ]

        phase = DynamicPhase(
            phase_number=1,
            phase_name="Test",
            description="Test phase",
            estimated_duration="2h",
            tasks=tasks,
            validation_gate=[],
        )

        # Test valid task numbers (1-indexed)
        task1 = phase.get_task(1)
        assert task1 is not None
        assert task1.task_id == "1.1"

        task2 = phase.get_task(2)
        assert task2 is not None
        assert task2.task_id == "1.2"

        # Test invalid task numbers
        assert phase.get_task(0) is None
        assert phase.get_task(3) is None

    def test_phase_serialization(self):
        """Test phase serialization to dict."""
        tasks = [
            DynamicTask(
                task_id="1.1",
                task_name="Task 1",
                description="First",
                estimated_time="1h",
                dependencies=[],
                acceptance_criteria=["Done"],
            )
        ]

        phase = DynamicPhase(
            phase_number=1,
            phase_name="Phase 1",
            description="Test phase",
            estimated_duration="3h",
            tasks=tasks,
            validation_gate=["Gate 1"],
        )

        phase_dict = phase.to_dict()

        assert phase_dict["phase_number"] == 1
        assert phase_dict["phase_name"] == "Phase 1"
        assert phase_dict["description"] == "Test phase"
        assert phase_dict["estimated_duration"] == "3h"
        assert len(phase_dict["tasks"]) == 1
        assert phase_dict["tasks"][0]["task_id"] == "1.1"
        assert phase_dict["validation_gate"] == ["Gate 1"]

    def test_phase_deserialization(self):
        """Test phase deserialization from dict."""
        phase_dict = {
            "phase_number": 1,
            "phase_name": "Phase 1",
            "description": "Test",
            "estimated_duration": "2h",
            "tasks": [
                {
                    "task_id": "1.1",
                    "task_name": "Task",
                    "description": "Desc",
                    "estimated_time": "1h",
                    "dependencies": [],
                    "acceptance_criteria": ["Done"],
                }
            ],
            "validation_gate": ["Pass tests"],
        }

        phase = DynamicPhase.from_dict(phase_dict)

        assert phase.phase_number == 1
        assert phase.phase_name == "Phase 1"
        assert len(phase.tasks) == 1
        assert phase.tasks[0].task_id == "1.1"
        assert phase.validation_gate == ["Pass tests"]


class TestDynamicWorkflowContent:
    """Test suite for DynamicWorkflowContent dataclass."""

    @pytest.fixture
    def sample_phases(self):
        """Create sample phases for testing."""
        return [
            DynamicPhase(
                phase_number=1,
                phase_name="Phase 1",
                description="First phase",
                estimated_duration="4h",
                tasks=[
                    DynamicTask(
                        task_id="1.1",
                        task_name="Task 1",
                        description="Do something",
                        estimated_time="2h",
                        dependencies=[],
                        acceptance_criteria=["Criterion 1", "Criterion 2"],
                    )
                ],
                validation_gate=["Gate 1", "Gate 2"],
            )
        ]

    @pytest.fixture
    def phase_template(self):
        """Sample phase template."""
        return """# Phase [PHASE_NUMBER]: [PHASE_NAME]

**Description:** [PHASE_DESCRIPTION]
**Duration:** [ESTIMATED_DURATION]
**Tasks:** [TASK_COUNT]

## Validation Gate
[VALIDATION_GATE]

Next: Phase [NEXT_PHASE_NUMBER]
"""

    @pytest.fixture
    def task_template(self):
        """Sample task template."""
        return """# Task [TASK_ID]: [TASK_NAME]

**Phase:** [PHASE_NUMBER] - [PHASE_NAME]
**Description:** [TASK_DESCRIPTION]
**Time:** [ESTIMATED_TIME]
**Dependencies:** [DEPENDENCIES]

## Acceptance Criteria
[ACCEPTANCE_CRITERIA]
"""

    def test_create_workflow_content(
        self, sample_phases, phase_template, task_template
    ):
        """Test creating DynamicWorkflowContent."""
        content = DynamicWorkflowContent(
            source_path="/path/to/tasks.md",
            workflow_type="spec_execution_v1",
            phase_template=phase_template,
            task_template=task_template,
            phases=sample_phases,
        )

        assert content.source_path == "/path/to/tasks.md"
        assert content.workflow_type == "spec_execution_v1"
        assert len(content.phases) == 1
        assert content.phase_template == phase_template
        assert content.task_template == task_template

    def test_render_phase(self, sample_phases, phase_template, task_template):
        """Test rendering a phase with template."""
        content = DynamicWorkflowContent(
            source_path="/path/to/tasks.md",
            workflow_type="spec_execution_v1",
            phase_template=phase_template,
            task_template=task_template,
            phases=sample_phases,
        )

        rendered = content.render_phase(1)

        assert "Phase 1: Phase 1" in rendered
        assert "First phase" in rendered
        assert "4h" in rendered
        assert "**Tasks:** 1" in rendered  # Markdown bold format
        assert "- [ ] Gate 1" in rendered
        assert "- [ ] Gate 2" in rendered
        assert "Next: Phase 2" in rendered

    def test_render_phase_caching(self, sample_phases, phase_template, task_template):
        """Test that rendered phases are cached."""
        content = DynamicWorkflowContent(
            source_path="/path/to/tasks.md",
            workflow_type="spec_execution_v1",
            phase_template=phase_template,
            task_template=task_template,
            phases=sample_phases,
        )

        # First render
        rendered1 = content.render_phase(1)
        # Second render (should be cached)
        rendered2 = content.render_phase(1)

        assert rendered1 == rendered2
        assert 1 in content._rendered_phases

    def test_render_task(self, sample_phases, phase_template, task_template):
        """Test rendering a task with template."""
        content = DynamicWorkflowContent(
            source_path="/path/to/tasks.md",
            workflow_type="spec_execution_v1",
            phase_template=phase_template,
            task_template=task_template,
            phases=sample_phases,
        )

        rendered = content.render_task(1, 1)

        assert "Task 1.1: Task 1" in rendered
        assert "**Phase:** 1 - Phase 1" in rendered  # Markdown bold format
        assert "Do something" in rendered
        assert "2h" in rendered
        assert "**Dependencies:** None" in rendered  # Markdown bold format
        assert "- [ ] Criterion 1" in rendered
        assert "- [ ] Criterion 2" in rendered

    def test_render_task_caching(self, sample_phases, phase_template, task_template):
        """Test that rendered tasks are cached."""
        content = DynamicWorkflowContent(
            source_path="/path/to/tasks.md",
            workflow_type="spec_execution_v1",
            phase_template=phase_template,
            task_template=task_template,
            phases=sample_phases,
        )

        # First render
        rendered1 = content.render_task(1, 1)
        # Second render (should be cached)
        rendered2 = content.render_task(1, 1)

        assert rendered1 == rendered2
        assert (1, 1) in content._rendered_tasks

    def test_render_task_with_dependencies(self, phase_template, task_template):
        """Test rendering task with dependencies."""
        phases = [
            DynamicPhase(
                phase_number=2,
                phase_name="Integration",
                description="Integrate components",
                estimated_duration="4h",
                tasks=[
                    DynamicTask(
                        task_id="2.3",
                        task_name="Integration Test",
                        description="Test integration",
                        estimated_time="1h",
                        dependencies=["2.1", "2.2"],
                        acceptance_criteria=["Tests pass"],
                    )
                ],
                validation_gate=[],
            )
        ]

        content = DynamicWorkflowContent(
            source_path="/path/to/tasks.md",
            workflow_type="spec_execution_v1",
            phase_template=phase_template,
            task_template=task_template,
            phases=phases,
        )

        rendered = content.render_task(2, 1)

        assert "**Dependencies:** 2.1, 2.2" in rendered  # Markdown bold format

    def test_render_invalid_phase(self, sample_phases, phase_template, task_template):
        """Test rendering invalid phase raises IndexError."""
        content = DynamicWorkflowContent(
            source_path="/path/to/tasks.md",
            workflow_type="spec_execution_v1",
            phase_template=phase_template,
            task_template=task_template,
            phases=sample_phases,
        )

        with pytest.raises(IndexError):
            content.render_phase(99)

    def test_render_invalid_task(self, sample_phases, phase_template, task_template):
        """Test rendering invalid task raises IndexError."""
        content = DynamicWorkflowContent(
            source_path="/path/to/tasks.md",
            workflow_type="spec_execution_v1",
            phase_template=phase_template,
            task_template=task_template,
            phases=sample_phases,
        )

        with pytest.raises(IndexError):
            content.render_task(1, 99)

    def test_serialization(self, sample_phases, phase_template, task_template):
        """Test serialization to dict."""
        content = DynamicWorkflowContent(
            source_path="/path/to/tasks.md",
            workflow_type="spec_execution_v1",
            phase_template=phase_template,
            task_template=task_template,
            phases=sample_phases,
        )

        content_dict = content.to_dict()

        assert content_dict["source_path"] == "/path/to/tasks.md"
        assert content_dict["workflow_type"] == "spec_execution_v1"
        assert content_dict["phase_template"] == phase_template
        assert content_dict["task_template"] == task_template
        assert len(content_dict["phases"]) == 1

    def test_deserialization(self, phase_template, task_template):
        """Test deserialization from dict."""
        content_dict = {
            "source_path": "/path/to/tasks.md",
            "workflow_type": "spec_execution_v1",
            "phase_template": phase_template,
            "task_template": task_template,
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Phase 1",
                    "description": "First",
                    "estimated_duration": "2h",
                    "tasks": [
                        {
                            "task_id": "1.1",
                            "task_name": "Task",
                            "description": "Desc",
                            "estimated_time": "1h",
                            "dependencies": [],
                            "acceptance_criteria": ["Done"],
                        }
                    ],
                    "validation_gate": ["Pass"],
                }
            ],
        }

        content = DynamicWorkflowContent.from_dict(content_dict)

        assert content.source_path == "/path/to/tasks.md"
        assert content.workflow_type == "spec_execution_v1"
        assert len(content.phases) == 1
        assert content.phases[0].phase_number == 1
