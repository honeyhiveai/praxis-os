# Implementation Guide
## Dynamic Workflow Engine & Session-Scoped Refactor

**Date:** 2025-10-06  
**For:** Developers implementing this spec

---

## 1. Implementation Approach

### 1.1 Workflow Execution

**This spec should be implemented using the `spec_execution_v1` workflow** (dogfooding!):

```python
# Start workflow
response = start_workflow(
    workflow_type="spec_execution_v1",
    target_file=".praxis-os/specs/2025-10-06-dynamic-workflow-session-refactor",
    options={"spec_path": ".praxis-os/specs/2025-10-06-dynamic-workflow-session-refactor"}
)

# Follow workflow guidance through all phases
# Use get_task() for each task
# Submit evidence via complete_phase()
```

### 1.2 Development Environment

**Prerequisites:**
- Python 3.9+
- pytest for testing
- MCP server development environment
- Access to .praxis-os/ directory structure

**Setup:**
```bash
cd /path/to/praxis-os
python -m pytest tests/  # Ensure existing tests pass
```

---

## 2. Code Patterns

### 2.1 Data Models (Task 1.1)

**File:** `mcp_server/models/workflow.py`

**Pattern - Immutable Dataclasses:**

```python
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

@dataclass(frozen=True)
class DynamicTask:
    """
    Task structure parsed from external source.
    
    Immutable to prevent accidental modification of cached data.
    """
    task_id: str  # e.g., "1.1"
    task_name: str
    description: str
    estimated_time: str
    dependencies: List[str]
    acceptance_criteria: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "description": self.description,
            "estimated_time": self.estimated_time,
            "dependencies": self.dependencies,
            "acceptance_criteria": self.acceptance_criteria,
        }

@dataclass(frozen=True)
class DynamicPhase:
    """
    Phase structure parsed from external source.
    
    Contains list of DynamicTask objects.
    """
    phase_number: int
    phase_name: str
    description: str
    estimated_duration: str
    tasks: Tuple[DynamicTask, ...]  # Tuple for immutability
    validation_gate: Tuple[str, ...]
    
    def get_task(self, task_number: int) -> DynamicTask:
        """Get task by number (1-indexed)."""
        if task_number < 1 or task_number > len(self.tasks):
            raise IndexError(f"Task {task_number} out of range (1-{len(self.tasks)})")
        return self.tasks[task_number - 1]

@dataclass
class DynamicWorkflowContent:
    """
    Mutable cache for rendered content.
    
    Not frozen because it maintains render cache.
    """
    source_path: Path
    workflow_type: str
    phase_template: str
    task_template: str
    phases: Tuple[DynamicPhase, ...]
    
    # Render cache (mutable)
    _rendered_phases: Dict[int, str] = field(default_factory=dict)
    _rendered_tasks: Dict[Tuple[int, int], str] = field(default_factory=dict)
```

### 2.2 Parser Implementation (Task 1.2)

**File:** `mcp_server/core/parsers.py`

**Pattern - Regex-Based Parsing:**

```python
import re
from pathlib import Path
from typing import List
from abc import ABC, abstractmethod

class ParseError(Exception):
    """Raised when source parsing fails."""
    pass

class SourceParser(ABC):
    """Abstract parser interface."""
    
    @abstractmethod
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """Parse source into structured phases."""
        pass

class SpecTasksParser(SourceParser):
    """
    Parser for prAxIs OS spec tasks.md files.
    
    Expected format:
    ### Phase N: Name
    **Goal:** Description
    **Tasks:**
    - [ ] **Task N.M**: Name
      - **Estimated Time**: X hours
      - **Dependencies**: Task N.K or None
      - **Acceptance Criteria**:
        - [ ] Criterion 1
    **Validation Gate:**
    - [ ] Gate criterion
    """
    
    # Regex patterns
    PHASE_HEADER = re.compile(r'^###\s+Phase\s+(\d+):\s+(.+)$', re.MULTILINE)
    GOAL = re.compile(r'^\*\*Goal:\*\*\s+(.+)$', re.MULTILINE)
    TASK_HEADER = re.compile(r'^-\s+\[\s+\]\s+\*\*Task\s+([\d\.]+)\*\*:\s+(.+)$', re.MULTILINE)
    ESTIMATED_TIME = re.compile(r'^\s+-\s+\*\*Estimated Time\*\*:\s+(.+)$', re.MULTILINE)
    DEPENDENCIES = re.compile(r'^\s+-\s+\*\*Dependencies\*\*:\s+(.+)$', re.MULTILINE)
    ACCEPTANCE = re.compile(r'^\s+-\s+\[\s+\]\s+(.+)$', re.MULTILINE)
    
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse tasks.md into structured phases.
        
        :param source_path: Path to tasks.md file
        :return: List of DynamicPhase objects
        :raises ParseError: If format is invalid or file not found
        """
        if not source_path.exists():
            raise ParseError(f"Source file not found: {source_path}")
        
        try:
            content = source_path.read_text()
        except Exception as e:
            raise ParseError(f"Failed to read {source_path}: {e}")
        
        # Split into phase sections
        phase_sections = self._split_into_phases(content)
        
        if not phase_sections:
            raise ParseError(f"No phases found in {source_path}")
        
        # Parse each section
        phases = []
        for section in phase_sections:
            try:
                phase = self._parse_phase_section(section)
                phases.append(phase)
            except Exception as e:
                raise ParseError(f"Failed to parse phase section: {e}")
        
        return phases
    
    def _split_into_phases(self, content: str) -> List[str]:
        """Split content by ### Phase headers."""
        # Find all phase headers
        matches = list(self.PHASE_HEADER.finditer(content))
        
        if not matches:
            return []
        
        sections = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            sections.append(content[start:end])
        
        return sections
    
    def _parse_phase_section(self, section: str) -> DynamicPhase:
        """Parse single phase section into DynamicPhase."""
        # Extract phase number and name
        header_match = self.PHASE_HEADER.search(section)
        if not header_match:
            raise ParseError("Phase header not found")
        
        phase_number = int(header_match.group(1))
        phase_name = header_match.group(2).strip()
        
        # Extract goal/description
        goal_match = self.GOAL.search(section)
        description = goal_match.group(1).strip() if goal_match else ""
        
        # Extract estimated duration (look for pattern)
        duration_match = re.search(r'\*\*Estimated Duration:\*\*\s+(.+?)$', section, re.MULTILINE)
        estimated_duration = duration_match.group(1).strip() if duration_match else "Unknown"
        
        # Extract tasks
        tasks = self._extract_tasks(section, phase_number)
        
        # Extract validation gate
        validation_gate = self._extract_validation_gate(section)
        
        return DynamicPhase(
            phase_number=phase_number,
            phase_name=phase_name,
            description=description,
            estimated_duration=estimated_duration,
            tasks=tuple(tasks),
            validation_gate=tuple(validation_gate)
        )
    
    def _extract_tasks(self, section: str, phase_number: int) -> List[DynamicTask]:
        """Extract all tasks from phase section."""
        tasks = []
        
        # Find task headers
        task_matches = list(self.TASK_HEADER.finditer(section))
        
        for i, task_match in enumerate(task_matches):
            task_id = task_match.group(1)  # e.g., "1.1"
            task_name = task_match.group(2).strip()
            
            # Extract task details (between this task and next)
            start = task_match.end()
            end = task_matches[i + 1].start() if i + 1 < len(task_matches) else len(section)
            task_content = section[start:end]
            
            # Parse task details
            estimated_time = self._extract_field(task_content, self.ESTIMATED_TIME, "Unknown")
            dependencies_str = self._extract_field(task_content, self.DEPENDENCIES, "None")
            dependencies = self._parse_dependencies(dependencies_str)
            
            # Extract acceptance criteria
            acceptance_criteria = self._extract_acceptance_criteria(task_content)
            
            # Extract description (text between header and first detail)
            description_match = re.search(r'^(.+?)(?=\s+-\s+\*\*)', task_content, re.DOTALL | re.MULTILINE)
            description = description_match.group(1).strip() if description_match else ""
            
            tasks.append(DynamicTask(
                task_id=task_id,
                task_name=task_name,
                description=description,
                estimated_time=estimated_time,
                dependencies=dependencies,
                acceptance_criteria=acceptance_criteria
            ))
        
        return tasks
    
    def _extract_field(self, content: str, pattern: re.Pattern, default: str) -> str:
        """Extract field using regex pattern."""
        match = pattern.search(content)
        return match.group(1).strip() if match else default
    
    def _parse_dependencies(self, deps_str: str) -> List[str]:
        """Parse dependencies string into list."""
        if deps_str.lower() in ("none", ""):
            return []
        # Split by comma or "and"
        deps = re.split(r',|\sand\s', deps_str)
        return [d.strip() for d in deps if d.strip()]
    
    def _extract_acceptance_criteria(self, content: str) -> List[str]:
        """Extract list of acceptance criteria."""
        # Find "Acceptance Criteria:" section
        criteria_section = re.search(
            r'\*\*Acceptance Criteria\*\*:(.+?)(?=\*\*|$)',
            content,
            re.DOTALL
        )
        
        if not criteria_section:
            return []
        
        criteria_text = criteria_section.group(1)
        
        # Extract checkboxes
        criteria = []
        for match in self.ACCEPTANCE.finditer(criteria_text):
            criteria.append(match.group(1).strip())
        
        return criteria
    
    def _extract_validation_gate(self, section: str) -> List[str]:
        """Extract validation gate criteria."""
        # Find "Validation Gate:" section
        gate_section = re.search(
            r'\*\*Validation Gate:\*\*(.+?)(?=###|$)',
            section,
            re.DOTALL
        )
        
        if not gate_section:
            return []
        
        gate_text = gate_section.group(1)
        
        # Extract checkboxes
        criteria = []
        for match in self.ACCEPTANCE.finditer(gate_text):
            criteria.append(match.group(1).strip())
        
        return criteria
```

### 2.3 Dynamic Registry (Task 2.1, 2.2)

**File:** `mcp_server/core/dynamic_registry.py`

**Pattern - Lazy Loading with Cache:**

```python
class DynamicContentRegistry:
    """
    Session-scoped registry for dynamic workflow content.
    
    Lifecycle:
    1. Initialize with templates and source
    2. Parse source once
    3. Render on-demand
    4. Cache results
    """
    
    def __init__(
        self,
        workflow_type: str,
        templates: Dict[str, Path],
        source_path: Path,
        parser: SourceParser
    ):
        """
        Initialize registry.
        
        :param workflow_type: Workflow type
        :param templates: {'phase': path, 'task': path}
        :param source_path: Path to source file (e.g., tasks.md)
        :param parser: Parser instance for source type
        """
        self.workflow_type = workflow_type
        self.source_path = source_path
        
        # Load templates
        self.phase_template = self._load_template(templates['phase'])
        self.task_template = self._load_template(templates['task'])
        
        # Parse source
        phases = parser.parse(source_path)
        
        # Create content cache
        self.content = DynamicWorkflowContent(
            source_path=source_path,
            workflow_type=workflow_type,
            phase_template=self.phase_template,
            task_template=self.task_template,
            phases=tuple(phases)
        )
    
    def _load_template(self, template_path: Path) -> str:
        """Load template from file."""
        if not template_path.exists():
            raise TemplateError(f"Template not found: {template_path}")
        
        try:
            return template_path.read_text()
        except Exception as e:
            raise TemplateError(f"Failed to load template {template_path}: {e}")
    
    def get_phase_content(self, phase: int) -> str:
        """
        Get rendered phase content (cached).
        
        :param phase: Phase number (0-indexed)
        :return: Rendered phase content with command language
        :raises PhaseOutOfRangeError: If phase invalid
        """
        if phase < 0 or phase >= len(self.content.phases):
            raise PhaseOutOfRangeError(
                f"Phase {phase} out of range (0-{len(self.content.phases)-1})"
            )
        
        # Check cache
        if phase in self.content._rendered_phases:
            return self.content._rendered_phases[phase]
        
        # Render
        rendered = self.content.render_phase(phase)
        
        # Cache
        self.content._rendered_phases[phase] = rendered
        
        return rendered
    
    def get_task_content(self, phase: int, task_number: int) -> str:
        """
        Get rendered task content (cached).
        
        :param phase: Phase number (0-indexed)
        :param task_number: Task number (1-indexed)
        :return: Rendered task content with command language
        """
        cache_key = (phase, task_number)
        
        # Check cache
        if cache_key in self.content._rendered_tasks:
            return self.content._rendered_tasks[cache_key]
        
        # Render
        rendered = self.content.render_task(phase, task_number)
        
        # Cache
        self.content._rendered_tasks[cache_key] = rendered
        
        return rendered
    
    def get_phase_metadata(self, phase: int) -> Dict[str, Any]:
        """Get phase metadata for engine responses."""
        phase_obj = self.content.phases[phase]
        
        return {
            "name": phase_obj.phase_name,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "task_name": task.task_name,
                    "estimated_time": task.estimated_time
                }
                for task in phase_obj.tasks
            ]
        }
```

**Template Rendering:**

```python
def render_phase(self, phase: int) -> str:
    """Render phase template with phase data."""
    phase_obj = self.phases[phase]
    
    # Build replacement dictionary
    replacements = {
        "PHASE_NUMBER": str(phase_obj.phase_number),
        "PHASE_NAME": phase_obj.phase_name,
        "PHASE_DESCRIPTION": phase_obj.description,
        "ESTIMATED_DURATION": phase_obj.estimated_duration,
        "TASK_COUNT": str(len(phase_obj.tasks)),
        "VALIDATION_GATE": self._format_list(phase_obj.validation_gate),
        "NEXT_PHASE_NUMBER": str(phase_obj.phase_number + 1)
    }
    
    # Render template
    return self._replace_placeholders(self.phase_template, replacements)

def _replace_placeholders(self, template: str, replacements: Dict[str, str]) -> str:
    """Replace [PLACEHOLDER] with values."""
    result = template
    
    for key, value in replacements.items():
        placeholder = f"[{key}]"
        result = result.replace(placeholder, value)
    
    return result

def _format_list(self, items: List[str]) -> str:
    """Format list for markdown."""
    if not items:
        return "- None"
    
    return "\n".join(f"- {item}" for item in items)
```

### 2.4 Session-Scoped Architecture (Task 3.1, 3.2)

**File:** `mcp_server/core/session.py`

**Pattern - Composition Over Inheritance:**

```python
class WorkflowSession:
    """
    Session-scoped workflow with lifecycle management.
    
    Encapsulates:
    - Session state
    - Dynamic content (if applicable)
    - Phase/task retrieval logic
    - Completion validation
    """
    
    def __init__(
        self,
        session_id: str,
        workflow_type: str,
        target_file: str,
        state: WorkflowState,
        rag_engine: RAGEngine,
        state_manager: StateManager,
        workflows_base_path: Path,
        metadata: WorkflowMetadata,
        options: Optional[Dict[str, Any]] = None
    ):
        self.session_id = session_id
        self.workflow_type = workflow_type
        self.target_file = target_file
        self.state = state
        self.rag_engine = rag_engine
        self.state_manager = state_manager
        self.workflows_base_path = workflows_base_path
        self.metadata = metadata
        self.options = options or {}
        
        # Initialize dynamic content if applicable
        self.dynamic_registry = self._init_dynamic_registry()
    
    def _init_dynamic_registry(self) -> Optional[DynamicContentRegistry]:
        """Initialize dynamic content registry if workflow is dynamic."""
        if not self.metadata.dynamic_phases:
            return None
        
        config = self.metadata.dynamic_config
        if not config:
            logger.warning(f"Workflow {self.workflow_type} has dynamic_phases but no dynamic_config")
            return None
        
        try:
            # Get source path from options
            source_key = config.get("source_path_key", "spec_path")
            source_path_str = self.options.get(source_key)
            
            if not source_path_str:
                raise ValueError(f"Dynamic workflow requires '{source_key}' in options")
            
            source_path = Path(source_path_str) / "tasks.md"
            
            # Load templates
            workflow_dir = self.workflows_base_path / self.workflow_type
            templates = {
                'phase': workflow_dir / config['templates']['phase'],
                'task': workflow_dir / config['templates']['task']
            }
            
            # Get parser
            parser_name = config.get("parser", "spec_tasks_parser")
            parser = PARSER_REGISTRY.get(parser_name)
            
            # Create registry
            return DynamicContentRegistry(
                workflow_type=self.workflow_type,
                templates=templates,
                source_path=source_path,
                parser=parser
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize dynamic registry: {e}")
            return None
    
    def _is_dynamic(self) -> bool:
        """Check if this session uses dynamic content."""
        return self.dynamic_registry is not None
    
    def get_current_phase(self) -> Dict[str, Any]:
        """Get current phase content (no session_id parameter!)."""
        phase = self.state.current_phase
        
        if self._is_dynamic():
            # Dynamic path
            phase_content = self.dynamic_registry.get_phase_content(phase)
            phase_meta = self.dynamic_registry.get_phase_metadata(phase)
            
            return {
                "session_id": self.session_id,
                "workflow_type": self.workflow_type,
                "target_file": self.target_file,
                "current_phase": phase,
                "phase_content": phase_content,
                "phase_name": phase_meta["name"],
                "tasks": phase_meta["tasks"],
                "source": "dynamic"
            }
        else:
            # Static path (RAG)
            return self._get_static_phase_content(phase)
    
    def get_task(self, phase: int, task_number: int) -> Dict[str, Any]:
        """Get task content (clean parameters - only phase and task_number)."""
        if self._is_dynamic():
            task_content = self.dynamic_registry.get_task_content(phase, task_number)
            
            return {
                "session_id": self.session_id,
                "phase": phase,
                "task_number": task_number,
                "task_content": task_content,
                "source": "dynamic"
            }
        else:
            return self._get_static_task_content(phase, task_number)
    
    def cleanup(self) -> None:
        """Clean up resources on workflow completion."""
        self.dynamic_registry = None
        logger.info(f"Session {self.session_id} cleaned up")
```

---

## 3. Testing Patterns

### 3.1 Unit Test Structure

```python
# tests/unit/test_dynamic_registry.py

import pytest
from pathlib import Path
from mcp_server.core.dynamic_registry import DynamicContentRegistry
from mcp_server.core.parsers import SpecTasksParser

@pytest.fixture
def sample_tasks_md(tmp_path):
    """Create sample tasks.md for testing."""
    tasks_file = tmp_path / "tasks.md"
    tasks_file.write_text("""
### Phase 1: Setup

**Goal:** Initial setup

**Tasks:**

- [ ] **Task 1.1**: Create module
  - **Estimated Time**: 2 hours
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - [ ] Module created
    - [ ] Tests pass

**Validation Gate:**
- [ ] All tests pass
""")
    return tasks_file

@pytest.fixture
def sample_templates(tmp_path):
    """Create sample templates."""
    phase_template = tmp_path / "phase-template.md"
    phase_template.write_text("""
# Phase [PHASE_NUMBER]: [PHASE_NAME]

[PHASE_DESCRIPTION]

Tasks: [TASK_COUNT]
""")
    
    task_template = tmp_path / "task-template.md"
    task_template.write_text("""
# Task [TASK_ID]: [TASK_NAME]

[TASK_DESCRIPTION]

Estimated: [ESTIMATED_TIME]
""")
    
    return {'phase': phase_template, 'task': task_template}

def test_registry_initialization(sample_tasks_md, sample_templates):
    """Test registry loads templates and parses source."""
    parser = SpecTasksParser()
    
    registry = DynamicContentRegistry(
        workflow_type="test",
        templates=sample_templates,
        source_path=sample_tasks_md,
        parser=parser
    )
    
    assert registry.content.phases is not None
    assert len(registry.content.phases) == 1
    assert registry.content.phases[0].phase_name == "Setup"

def test_phase_rendering(sample_tasks_md, sample_templates):
    """Test phase template rendering."""
    parser = SpecTasksParser()
    registry = DynamicContentRegistry(
        workflow_type="test",
        templates=sample_templates,
        source_path=sample_tasks_md,
        parser=parser
    )
    
    content = registry.get_phase_content(0)
    
    assert "# Phase 1: Setup" in content
    assert "Initial setup" in content
    assert "Tasks: 1" in content

def test_caching(sample_tasks_md, sample_templates):
    """Test rendered content is cached."""
    parser = SpecTasksParser()
    registry = DynamicContentRegistry(
        workflow_type="test",
        templates=sample_templates,
        source_path=sample_tasks_md,
        parser=parser
    )
    
    # First call
    content1 = registry.get_phase_content(0)
    
    # Second call (should be cached)
    content2 = registry.get_phase_content(0)
    
    assert content1 == content2
    assert 0 in registry.content._rendered_phases
```

### 3.2 Integration Test

```python
# tests/integration/test_dynamic_workflow_e2e.py

def test_spec_execution_v1_enforcement(workflow_engine, tmp_path):
    """Test full dynamic workflow with enforcement."""
    
    # Create sample spec
    spec_dir = tmp_path / "test-spec"
    spec_dir.mkdir()
    
    tasks_file = spec_dir / "tasks.md"
    tasks_file.write_text("""
### Phase 1: Implementation

**Goal:** Implement feature

**Tasks:**

- [ ] **Task 1.1**: Create module
  - **Estimated Time**: 2 hours
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - [ ] Module created
    
**Validation Gate:**
- [ ] Tests pass
""")
    
    # Start workflow
    result = workflow_engine.start_workflow(
        workflow_type="spec_execution_v1",
        target_file=str(spec_dir),
        metadata={"spec_path": str(spec_dir)}
    )
    
    session_id = result["session_id"]
    
    # Complete Phase 0
    workflow_engine.complete_phase(
        session_id=session_id,
        phase=0,
        evidence={"spec_validated": True}
    )
    
    # Get Phase 1 content
    phase1 = workflow_engine.get_current_phase(session_id)
    
    # Verify command language present
    assert "🛑 EXECUTE-NOW" in phase1["phase_content"]
    assert "get_task()" in phase1["phase_content"]
    
    # Get task
    task = workflow_engine.get_task(session_id, phase=1, task_number=1)
    
    # Verify enforcement
    assert "🛑 EXECUTE-NOW" in task["task_content"]
    assert "production code checklist" in task["task_content"]
    
    # Complete workflow
    workflow_engine.complete_phase(
        session_id=session_id,
        phase=1,
        evidence={"tests_passing": True}
    )
    
    # Verify cleanup
    state = workflow_engine.get_workflow_state(session_id)
    assert state["is_complete"]
```

---

## 4. Quality Checklist

Before marking a task complete, verify:

### Code Quality
- [ ] Comprehensive Sphinx-style docstrings
- [ ] Full type hints (parameters + return types)
- [ ] Explicit error handling with specific exceptions
- [ ] Resource cleanup (no memory leaks)
- [ ] No linting errors

### Testing
- [ ] Unit tests for all new functions/classes
- [ ] Test coverage ≥ 80% (≥ 90% for core components)
- [ ] Integration test for end-to-end flow
- [ ] Performance benchmarks meet targets
- [ ] All tests pass

### Documentation
- [ ] Inline comments for complex logic
- [ ] API documentation complete
- [ ] Usage examples provided
- [ ] Error messages actionable

---

## 5. Troubleshooting

### Common Issues

**Issue:** Template not found  
**Solution:** Verify template paths in metadata.json are relative to workflow directory

**Issue:** Parse error on valid tasks.md  
**Solution:** Check regex patterns match exact format (spaces, capitalization)

**Issue:** Memory leak  
**Solution:** Ensure session.cleanup() called on workflow completion

**Issue:** Performance degradation  
**Solution:** Verify caching is working (_rendered_phases, _rendered_tasks)

---

## 6. Code Review Checklist

- [ ] Follows session-scoped pattern consistently
- [ ] No session_id parameters in session methods
- [ ] Dynamic content initialized only for dynamic workflows
- [ ] Templates load from correct paths
- [ ] Parser handles malformed input gracefully
- [ ] Rendering performance within targets
- [ ] Memory usage reasonable
- [ ] Backward compatibility maintained
- [ ] All tests pass
- [ ] Documentation complete

---

**Ready to implement!** Use `spec_execution_v1` workflow for systematic, phase-gated implementation with quality enforcement.
