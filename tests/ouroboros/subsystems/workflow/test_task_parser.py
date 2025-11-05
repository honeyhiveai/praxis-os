"""
Unit tests for task parsers.

Tests SourceParser interface, SpecTasksParser, and WorkflowDefinitionParser implementations.
Ported from tests/unit/test_parsers.py with full functionality preserved.
"""

from pathlib import Path

import pytest
from ouroboros.subsystems.workflow.models import DynamicPhase, DynamicTask
from ouroboros.subsystems.workflow.task_parser import (
    ParseError,
    SourceParser,
    SpecTasksParser,
    WorkflowDefinitionParser,
)


class TestSpecTasksParser:
    """Test suite for SpecTasksParser."""

    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return SpecTasksParser()

    @pytest.fixture
    def sample_tasks_md(self, tmp_path):
        """Create a sample tasks.md file."""
        content = """# Implementation Tasks
## Dynamic Workflow Engine

### Phase 1: Core Infrastructure

**Goal:** Create foundational components for dynamic workflow support without integration

**Estimated Duration:** 6-8 hours

**Tasks:**

- [ ] **Task 1.1**: Create data models for dynamic workflows
  - **Estimated Time**: 2 hours
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - [ ] DynamicPhase dataclass created
    - [ ] DynamicTask dataclass created
    - [ ] All models have Sphinx docstrings

- [ ] **Task 1.2**: Create SourceParser interface and SpecTasksParser
  - **Estimated Time**: 4-5 hours
  - **Dependencies**: Task 1.1
  - **Acceptance Criteria**:
    - [ ] SourceParser abstract class in core/parsers.py
    - [ ] SpecTasksParser implementation
    - [ ] Test coverage ≥ 90%

**Validation Gate:**
- [ ] All data models created and tested
- [ ] SpecTasksParser successfully parses example tasks.md
- [ ] Unit tests pass with ≥ 90% coverage

---

### Phase 2: Dynamic Content Registry

**Goal:** Implement template loading, rendering, and caching system

**Estimated Duration:** 4-6 hours

**Tasks:**

- [ ] **Task 2.1**: Create DynamicContentRegistry class
  - **Estimated Time**: 3-4 hours
  - **Dependencies**: Task 1.1, Task 1.2
  - **Acceptance Criteria**:
    - [ ] DynamicContentRegistry class created
    - [ ] Renders on-demand
    - [ ] Caches results

**Validation Gate:**
- [ ] Registry created and tested
- [ ] Templates load correctly
"""
        tasks_file = tmp_path / "tasks.md"
        tasks_file.write_text(content)
        return tasks_file

    @pytest.fixture
    def minimal_tasks_md(self, tmp_path):
        """Create minimal valid tasks.md."""
        content = """### Phase 1: Test Phase

**Goal:** Test goal

**Tasks:**

- [ ] **Task 1.1**: Test task
  - **Estimated Time**: 1 hour
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - [ ] Criterion 1

**Validation Gate:**
- [ ] Gate criterion
"""
        tasks_file = tmp_path / "minimal_tasks.md"
        tasks_file.write_text(content)
        return tasks_file

    def test_parse_valid_file(self, parser, sample_tasks_md):
        """Test parsing valid tasks.md file."""
        phases = parser.parse(sample_tasks_md)

        assert len(phases) == 2
        assert phases[0].phase_number == 1
        assert phases[0].phase_name == "Core Infrastructure"
        assert phases[1].phase_number == 2
        assert phases[1].phase_name == "Dynamic Content Registry"

    def test_parse_phase_metadata(self, parser, sample_tasks_md):
        """Test extracting phase metadata."""
        phases = parser.parse(sample_tasks_md)
        phase1 = phases[0]

        assert (
            phase1.description
            == "Create foundational components for dynamic workflow support without integration"
        )
        assert phase1.estimated_duration == "6-8 hours"
        assert len(phase1.validation_gate) == 3

    def test_parse_tasks(self, parser, sample_tasks_md):
        """Test extracting tasks from phase."""
        phases = parser.parse(sample_tasks_md)
        phase1 = phases[0]

        assert len(phase1.tasks) == 2

        task1 = phase1.tasks[0]
        assert task1.task_id == "1.1"
        assert task1.task_name == "Create data models for dynamic workflows"
        assert task1.estimated_time == "2 hours"
        assert task1.dependencies == []
        assert len(task1.acceptance_criteria) == 3

        task2 = phase1.tasks[1]
        assert task2.task_id == "1.2"
        assert "SourceParser" in task2.task_name
        assert task2.estimated_time == "4-5 hours"
        assert task2.dependencies == ["1.1"]

    def test_parse_validation_gate(self, parser, sample_tasks_md):
        """Test extracting validation gate criteria."""
        phases = parser.parse(sample_tasks_md)
        phase1 = phases[0]

        assert len(phase1.validation_gate) == 3
        assert "All data models created and tested" in phase1.validation_gate[0]
        assert "SpecTasksParser successfully parses" in phase1.validation_gate[1]

    def test_parse_minimal_file(self, parser, minimal_tasks_md):
        """Test parsing minimal valid file."""
        phases = parser.parse(minimal_tasks_md)

        assert len(phases) == 1
        assert phases[0].phase_number == 1
        assert len(phases[0].tasks) == 1
        assert len(phases[0].validation_gate) == 1

    def test_parse_nonexistent_file(self, parser, tmp_path):
        """Test error on nonexistent file."""
        nonexistent = tmp_path / "does_not_exist.md"

        with pytest.raises(ParseError, match="Source file not found"):
            parser.parse(nonexistent)

    def test_parse_empty_file(self, parser, tmp_path):
        """Test error on empty file."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("")

        with pytest.raises(ParseError, match="Source file is empty"):
            parser.parse(empty_file)

    def test_parse_no_phases(self, parser, tmp_path):
        """Test error when no phases found."""
        no_phases = tmp_path / "no_phases.md"
        no_phases.write_text("# Some content\nBut no phases")

        with pytest.raises(ParseError, match="No phases found"):
            parser.parse(no_phases)

    def test_parse_directory_with_tasks_md(self, parser, tmp_path):
        """Test parsing directory that contains tasks.md."""
        tasks_file = tmp_path / "tasks.md"
        content = """### Phase 1: Test

**Goal:** Test

**Tasks:**

- [ ] **Task 1.1**: Task
  - **Estimated Time**: 1h
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - [ ] Done

**Validation Gate:**
- [ ] Pass
"""
        tasks_file.write_text(content)

        # Pass directory path, should find tasks.md
        phases = parser.parse(tmp_path)
        assert len(phases) == 1

    def test_parse_directory_without_tasks_md(self, parser, tmp_path):
        """Test error when directory doesn't contain tasks.md."""
        with pytest.raises(ParseError, match="tasks.md not found"):
            parser.parse(tmp_path)

    def test_parse_task_with_multiple_dependencies(self, parser, tmp_path):
        """Test parsing task with multiple dependencies."""
        content = """### Phase 2: Integration

**Goal:** Integrate

**Tasks:**

- [ ] **Task 2.3**: Integration test
  - **Estimated Time**: 2h
  - **Dependencies**: Task 2.1, Task 2.2
  - **Acceptance Criteria**:
    - [ ] Tests pass

**Validation Gate:**
- [ ] Complete
"""
        tasks_file = tmp_path / "multi_dep.md"
        tasks_file.write_text(content)

        phases = parser.parse(tasks_file)
        task = phases[0].tasks[0]

        assert task.dependencies == ["2.1", "2.2"]

    def test_parse_task_without_estimated_time(self, parser, tmp_path):
        """Test task without explicit estimated time."""
        content = """### Phase 1: Test

**Goal:** Test

**Tasks:**

- [ ] **Task 1.1**: Task without time
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - [ ] Done

**Validation Gate:**
- [ ] Pass
"""
        tasks_file = tmp_path / "no_time.md"
        tasks_file.write_text(content)

        phases = parser.parse(tasks_file)
        task = phases[0].tasks[0]

        assert task.estimated_time == "Variable"

    def test_parse_phase_without_goal(self, parser, tmp_path):
        """Test phase without explicit goal."""
        content = """### Phase 1: Test Phase

**Tasks:**

- [ ] **Task 1.1**: Task
  - **Estimated Time**: 1h
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - [ ] Done

**Validation Gate:**
- [ ] Pass
"""
        tasks_file = tmp_path / "no_goal.md"
        tasks_file.write_text(content)

        phases = parser.parse(tasks_file)

        assert phases[0].description == "Phase 1 objectives"

    def test_parse_task_dependencies_with_and(self, parser, tmp_path):
        """Test parsing dependencies separated by 'and'."""
        content = """### Phase 2: Integration

**Goal:** Test

**Tasks:**

- [ ] **Task 2.2**: Task with and
  - **Estimated Time**: 1h
  - **Dependencies**: Task 2.1 and Task 1.3
  - **Acceptance Criteria**:
    - [ ] Done

**Validation Gate:**
- [ ] Pass
"""
        tasks_file = tmp_path / "and_deps.md"
        tasks_file.write_text(content)

        phases = parser.parse(tasks_file)
        task = phases[0].tasks[0]

        assert "2.1" in task.dependencies
        assert "1.3" in task.dependencies

    def test_parse_multiple_phases(self, parser, sample_tasks_md):
        """Test parsing file with multiple phases."""
        phases = parser.parse(sample_tasks_md)

        assert len(phases) == 2
        assert phases[0].phase_number == 1
        assert phases[1].phase_number == 2
        assert len(phases[0].tasks) == 2
        assert len(phases[1].tasks) == 1

    def test_parse_acceptance_criteria_formatting(self, parser, tmp_path):
        """Test acceptance criteria extraction with various formatting."""
        content = """### Phase 1: Test

**Goal:** Test

**Tasks:**

- [ ] **Task 1.1**: Task with criteria
  - **Estimated Time**: 1h
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - [ ] First criterion
    - [ ] Second criterion with details
    - [ ] Third criterion

**Validation Gate:**
- [ ] Pass
"""
        tasks_file = tmp_path / "criteria.md"
        tasks_file.write_text(content)

        phases = parser.parse(tasks_file)
        task = phases[0].tasks[0]

        assert len(task.acceptance_criteria) == 3
        assert task.acceptance_criteria[0] == "First criterion"
        assert "Second criterion" in task.acceptance_criteria[1]

    def test_parse_validation_gate_multiple_criteria(self, parser, tmp_path):
        """Test validation gate with multiple criteria."""
        content = """### Phase 1: Test

**Goal:** Test

**Tasks:**

- [ ] **Task 1.1**: Task
  - **Estimated Time**: 1h
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - [ ] Done

**Validation Gate:**
- [ ] All tests pass
- [ ] No linting errors
- [ ] Documentation complete
- [ ] Code review approved
"""
        tasks_file = tmp_path / "multi_gate.md"
        tasks_file.write_text(content)

        phases = parser.parse(tasks_file)

        assert len(phases[0].validation_gate) == 4
        assert "All tests pass" in phases[0].validation_gate[0]
        assert "Code review approved" in phases[0].validation_gate[3]

    def test_abstract_source_parser(self):
        """Test that SourceParser is abstract."""
        with pytest.raises(TypeError):
            # Cannot instantiate abstract class
            SourceParser()

    def test_parse_task_id_extraction(self, parser, tmp_path):
        """Test various task ID formats are extracted correctly."""
        content = """### Phase 3: Advanced

**Goal:** Test

**Tasks:**

- [ ] **Task 3.10**: Double digit task
  - **Estimated Time**: 1h
  - **Dependencies**: Task 3.9
  - **Acceptance Criteria**:
    - [ ] Done

**Validation Gate:**
- [ ] Pass
"""
        tasks_file = tmp_path / "task_ids.md"
        tasks_file.write_text(content)

        phases = parser.parse(tasks_file)
        task = phases[0].tasks[0]

        assert task.task_id == "3.10"
        assert task.dependencies == ["3.9"]


class TestWorkflowDefinitionParser:
    """Test suite for WorkflowDefinitionParser."""

    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return WorkflowDefinitionParser()

    @pytest.fixture
    def sample_workflow_yaml(self, tmp_path):
        """Create a sample workflow definition YAML file."""
        content = """
workflow_type: test_workflow_v1
version: 1.0.0
name: Test Workflow
description: A test workflow for validation

phases:
  - number: 1
    name: Setup Phase
    purpose: Set up test environment
    estimated_duration: 2 hours
    tasks:
      - number: 1
        name: Create test files
        purpose: Create necessary test files
        estimated_time: 1 hour
        dependencies: []
        validation_criteria:
          - Test files exist
          - Files have correct format
      - number: 2
        name: Configure environment
        purpose: Configure test environment
        estimated_time: 1 hour
        dependencies: []
        validation_criteria:
          - Environment configured
    validation_gate:
      evidence_required:
        files_created:
          type: list
          description: List of created files
          validator: non_empty
        config_complete:
          type: boolean
          description: Configuration complete
          validator: is_true

  - number: 2
    name: Execution Phase
    purpose: Execute tests
    estimated_duration: 3 hours
    tasks:
      - number: 1
        name: Run tests
        purpose: Execute test suite
        estimated_time: 3 hours
        dependencies: []
        validation_criteria:
          - All tests pass
    validation_gate:
      evidence_required:
        test_results:
          type: dict
          description: Test execution results
          validator: all_pass
"""
        yaml_file = tmp_path / "workflow.yaml"
        yaml_file.write_text(content)
        return yaml_file

    def test_parse_valid_yaml(self, parser, sample_workflow_yaml):
        """Test parsing valid workflow YAML file."""
        phases = parser.parse(sample_workflow_yaml)

        assert len(phases) == 2
        assert phases[0].phase_number == 1
        assert phases[0].phase_name == "Setup Phase"
        assert phases[1].phase_number == 2
        assert phases[1].phase_name == "Execution Phase"

    def test_parse_phase_metadata(self, parser, sample_workflow_yaml):
        """Test extracting phase metadata from YAML."""
        phases = parser.parse(sample_workflow_yaml)
        phase1 = phases[0]

        assert phase1.description == "Set up test environment"
        assert phase1.estimated_duration == "2 hours"
        assert len(phase1.tasks) == 2

    def test_parse_tasks_from_yaml(self, parser, sample_workflow_yaml):
        """Test extracting tasks from YAML."""
        phases = parser.parse(sample_workflow_yaml)
        phase1 = phases[0]

        assert len(phase1.tasks) == 2

        task1 = phase1.tasks[0]
        assert task1.task_id == "1.1"
        assert task1.task_name == "Create test files"
        assert task1.description == "Create necessary test files"
        assert task1.estimated_time == "1 hour"
        assert task1.dependencies == []
        assert len(task1.acceptance_criteria) == 2

    def test_parse_validation_gate_from_yaml(self, parser, sample_workflow_yaml):
        """Test extracting validation gate from YAML."""
        phases = parser.parse(sample_workflow_yaml)
        phase1 = phases[0]

        assert len(phase1.validation_gate) == 2
        assert "files_created" in phase1.validation_gate[0]
        assert "config_complete" in phase1.validation_gate[1]

    def test_parse_nonexistent_yaml(self, parser, tmp_path):
        """Test error on nonexistent YAML file."""
        nonexistent = tmp_path / "does_not_exist.yaml"

        with pytest.raises(ParseError, match="Definition file not found"):
            parser.parse(nonexistent)

    def test_parse_empty_yaml(self, parser, tmp_path):
        """Test error on empty YAML file."""
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("")

        with pytest.raises(ParseError, match="Definition file is empty"):
            parser.parse(empty_file)

    def test_parse_yaml_without_phases(self, parser, tmp_path):
        """Test error when YAML has no phases."""
        no_phases = tmp_path / "no_phases.yaml"
        no_phases.write_text("workflow_type: test\nversion: 1.0.0\n")

        with pytest.raises(ParseError, match="No phases found"):
            parser.parse(no_phases)

    def test_parse_task_with_dependencies(self, parser, tmp_path):
        """Test parsing task with dependencies from YAML."""
        content = """
phases:
  - number: 1
    name: Test Phase
    purpose: Test
    tasks:
      - number: 1
        name: First task
        purpose: Do first
        dependencies: []
      - number: 2
        name: Second task
        purpose: Do second
        dependencies: ["1.1"]
        validation_criteria:
          - Task complete
    validation_gate:
      evidence_required: {}
"""
        yaml_file = tmp_path / "deps.yaml"
        yaml_file.write_text(content)

        phases = parser.parse(yaml_file)
        task2 = phases[0].tasks[1]

        assert task2.task_id == "1.2"
        assert task2.dependencies == ["1.1"]
