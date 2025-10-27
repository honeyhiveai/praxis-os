---

**Assistant:**

[Unexpected content type]

<read_file>
<path>mcp_server/core/dynamic_registry.py</path>
<task_progress>
- [x] Understood three-tier architecture in workflows
- [ ] Read dynamic registry implementation
- [ ] Read parsers for task extraction
- [ ] Read session management
- [ ] Understand how dynamic workflows execute
- [ ] Provide implementation analysis
</task_progress>
</read_file>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[read_file for 'mcp_server/core/dynamic_registry.py'] Result:
"""
Dynamic content registry for workflow sessions.

Manages template loading, source parsing, and content rendering for dynamic workflows.
Each registry instance is tied to a single workflow session.
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: __init__ requires 6 parameters for complete registry setup
# (workflow_type, parser, source paths, template paths) - all necessary for
# flexible dynamic content management

from pathlib import Path
from typing import Any, Dict

from mcp_server.core.parsers import SourceParser
from mcp_server.models.workflow import DynamicWorkflowContent


class DynamicRegistryError(Exception):
    """Raised when dynamic registry operations fail."""


class DynamicContentRegistry:
    """
    Session-scoped registry for dynamically-generated workflow content.

    Manages the lifecycle of dynamic workflow content:
    1. Load templates from filesystem on initialization
    2. Parse source using provided parser
    3. Cache parsed phases and rendered content
    4. Serve content via get_phase_content() and get_task_content()
    5. Provide metadata for workflow engine responses

    This class is instantiated once per dynamic workflow session and
    lives for the duration of the session.

    Attributes:
        workflow_type: Type of workflow (e.g., "spec_execution_v1")
        content: Parsed and cached DynamicWorkflowContent
    """

    def __init__(
        self,
        workflow_type: str,
        phase_template_path: Path,
        task_template_path: Path,
        source_path: Path,
        parser: SourceParser,
    ):
        """
        Initialize dynamic content registry for a workflow session.

        Loads templates, parses source, and creates cached content structure.

        Args:
            workflow_type: Workflow type identifier
            phase_template_path: Path to phase template file
            task_template_path: Path to task template file
            source_path: Path to source file (e.g., spec's tasks.md)
            parser: SourceParser instance for parsing source

        Raises:
            DynamicRegistryError: If template loading or parsing fails
        """
        self.workflow_type = workflow_type

        # Load templates
        try:
            phase_template = self._load_template(phase_template_path)
            task_template = self._load_template(task_template_path)
        except Exception as e:
            raise DynamicRegistryError(f"Failed to load templates: {e}") from e

        # Parse source into structured phases
        try:
            phases = parser.parse(source_path)
        except Exception as e:
            raise DynamicRegistryError(
                f"Failed to parse source {source_path}: {e}"
            ) from e

        if not phases:
            raise DynamicRegistryError(f"No phases parsed from {source_path}")

        # Create cached content structure
        self.content = DynamicWorkflowContent(
            source_path=str(source_path),
            workflow_type=workflow_type,
            phase_template=phase_template,
            task_template=task_template,
            phases=phases,
        )

    def _load_template(self, template_path: Path) -> str:
        """
        Load template file from filesystem.

        Args:
            template_path: Path to template file

        Returns:
            Template content as string

        Raises:
            DynamicRegistryError: If template file not found or unreadable
        """
        if not template_path.exists():
            raise DynamicRegistryError(f"Template not found: {template_path}")

        try:
            return template_path.read_text(encoding="utf-8")
        except Exception as e:
            raise DynamicRegistryError(
                f"Failed to read template {template_path}: {e}"
            ) from e

    def get_phase_content(self, phase: int) -> str:
        """
        Get rendered phase content with command language.

        Uses lazy rendering and caching for performance.

        Args:
            phase: Phase number to render (matches phase_number field)

        Returns:
            Rendered phase content with enforcement commands

        Raises:
            IndexError: If phase not found
        """
        return self.content.render_phase(phase)

    def get_task_content(self, phase: int, task_number: int) -> str:
        """
        Get rendered task content with command language.

        Uses lazy rendering and caching for performance.

        Args:
            phase: Phase number (matches phase_number field)
            task_number: Task number within phase (1-indexed)

        Returns:
            Rendered task content with enforcement commands

        Raises:
            IndexError: If phase or task not found
        """
        return self.content.render_task(phase, task_number)

    def get_phase_metadata(self, phase: int) -> Dict[str, Any]:
        """
        Get phase metadata for workflow engine responses.

        Returns summary information about phase without full content,
        useful for building workflow engine API responses.

        Args:
            phase: Phase number

        Returns:
            Dictionary with phase metadata:
                - phase_number: int
                - phase_name: str
                - description: str
                - estimated_duration: str
                - task_count: int
                - tasks: List[Dict] with task metadata
                - validation_gate: List[str]

        Raises:
            IndexError: If phase not found
        """
        # Find phase by phase_number
        phase_data = next(
            (p for p in self.content.phases if p.phase_number == phase), None
        )

        if not phase_data:
            raise IndexError(f"Phase {phase} not found")

        # Build task metadata list
        tasks_metadata = [
            {
                "task_number": i + 1,
                "task_id": task.task_id,
                "task_name": task.task_name,
                "estimated_time": task.estimated_time,
                "dependencies": task.dependencies,
            }
            for i, task in enumerate(phase_data.tasks)
        ]

        return {
            "phase_number": phase_data.phase_number,
            "phase_name": phase_data.phase_name,
            "description": phase_data.description,
            "estimated_duration": phase_data.estimated_duration,
            "task_count": len(phase_data.tasks),
            "tasks": tasks_metadata,
            "validation_gate": phase_data.validation_gate,
        }

    def get_total_phases(self) -> int:
        """
        Get total number of phases in this workflow.

        Returns:
            Number of phases
        """
        return len(self.content.phases)

    def has_phase(self, phase: int) -> bool:
        """
        Check if phase exists in this workflow.

        Args:
            phase: Phase number to check

        Returns:
            True if phase exists, False otherwise
        """
        return any(p.phase_number == phase for p in self.content.phases)

    def get_all_phases_metadata(self) -> list[Dict[str, Any]]:
        """
        Get metadata for all phases.

        Useful for workflow overview and planning.

        Returns:
            List of phase metadata dictionaries
        """
        return [
            self.get_phase_metadata(phase.phase_number) for phase in self.content.phases
        ]


__all__ = [
    "DynamicRegistryError",
    "DynamicContentRegistry",
]

<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:39:33 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
116,632 / 200K tokens used (58%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<read_file>
<path>mcp_server/core/parsers.py</path>
<task_progress>
- [x] Read dynamic registry implementation
- [ ] Read parsers implementation
- [ ] Read session management
- [ ] Understand complete dynamic workflow execution
- [ ] Provide comprehensive analysis
</task_progress>
</read_file>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[read_file for 'mcp_server/core/parsers.py'] Result:
"""
Source parsers for dynamic workflow content.

Provides abstract interface and concrete implementations for parsing
external sources (like spec tasks.md files) into structured workflow data.
"""

# pylint: disable=unused-argument
# Justification: _parse_collected_tasks has phase_number parameter reserved for
# future phase-specific task processing logic

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

# Mistletoe imports for AST-based parsing
from mistletoe import Document
from mistletoe.block_token import Heading
from mistletoe.block_token import List as MarkdownList
from mistletoe.block_token import ListItem, Paragraph
from mistletoe.span_token import LineBreak, RawText, Strong

from mcp_server.models.workflow import DynamicPhase, DynamicTask


class ParseError(Exception):
    """Raised when source parsing fails."""


class SourceParser(ABC):
    """
    Abstract parser for dynamic workflow sources.

    Subclasses implement parsing for specific source formats
    (e.g., tasks.md files, Jira API, GitHub Issues, etc.).
    """

    @abstractmethod
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse source into structured phase/task data.

        Args:
            source_path: Path to source file or directory

        Returns:
            List of DynamicPhase objects with populated tasks

        Raises:
            ParseError: If source is invalid or cannot be parsed
        """


class SpecTasksParser(SourceParser):
    """
    AST-based parser for Agent OS spec tasks.md files.

    Uses mistletoe to parse markdown into an AST, then extracts phases,
    tasks, acceptance criteria, dependencies, and validation gates through
    tree traversal. Much more robust than regex-based parsing.

    Handles variations in formatting gracefully:
    - ## or ### for phase headers
    - **Objective:** or **Goal:** for descriptions
    - Different task list formats
    - Flexible acceptance criteria placement
    """

    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse spec's tasks.md file into structured phases using AST.

        Args:
            source_path: Path to tasks.md file or directory containing it

        Returns:
            List of DynamicPhase objects

        Raises:
            ParseError: If file format is invalid or cannot be parsed
        """
        if not source_path.exists():
            raise ParseError(f"Source file not found: {source_path}")

        if source_path.is_dir():
            # If directory provided, look for tasks.md
            source_path = source_path / "tasks.md"
            if not source_path.exists():
                raise ParseError(
                    f"tasks.md not found in directory: {source_path.parent}"
                )

        try:
            content = source_path.read_text(encoding="utf-8")
        except Exception as e:
            raise ParseError(f"Failed to read {source_path}: {e}") from e

        if not content.strip():
            raise ParseError(f"Source file is empty: {source_path}")

        # Parse markdown into AST
        try:
            doc = Document(content)
        except Exception as e:
            raise ParseError(f"Failed to parse markdown: {e}") from e

        # Extract phases from AST
        phases = self._extract_phases_from_ast(doc)

        if not phases:
            raise ParseError(f"No phases found in {source_path}")

        return phases

    def _extract_phases_from_ast(self, doc: Document) -> List[DynamicPhase]:
        """
        Extract phases by traversing the markdown AST.

        Args:
            doc: Mistletoe Document object

        Returns:
            List of DynamicPhase objects
        """
        phases: List[DynamicPhase] = []
        current_phase_data = None

        for node in doc.children:
            # Check for phase headers (## Phase N: Name or ### Phase N: Name)
            if isinstance(node, Heading) and node.level in [2, 3]:
                header_text = self._get_text_content(node)
                phase_match = re.match(r"Phase (\d+):\s*(.+)", header_text)

                if phase_match:
                    # Save previous phase if exists
                    if current_phase_data:
                        phase = self._build_phase(current_phase_data)
                        if phase:
                            phases.append(phase)

                    # Start new phase
                    phase_number = int(phase_match.group(1))
                    phase_name = phase_match.group(2).strip()
                    current_phase_data = {
                        "phase_number": phase_number,
                        "phase_name": phase_name,
                        "description": "",
                        "estimated_duration": "Variable",
                        "task_lines": [],
                        "validation_gate": [],
                        "nodes": [],  # Collect nodes for this phase
                    }
                    continue

            # Collect nodes that belong to current phase
            if current_phase_data is not None:
                current_phase_data["nodes"].append(node)

        # Don't forget the last phase
        if current_phase_data:
            phase = self._build_phase(current_phase_data)
            if phase:
                phases.append(phase)

        return phases

    def _build_phase(self, phase_data: Dict[str, Any]) -> Optional[DynamicPhase]:
        """
        Build a DynamicPhase from collected phase data.

        Args:
            phase_data: Dictionary with phase information and AST nodes

        Returns:
            DynamicPhase object or None if invalid
        """
        # Extract metadata from nodes
        seen_validation_gate_header = False
        for node in phase_data["nodes"]:
            if isinstance(node, Paragraph):
                text = self._get_text_content(node)

                # Look for metadata patterns (plain text or markdown)
                if "Objective:" in text or "Goal:" in text:
                    desc_match = re.search(
                        r"(?:Objective|Goal):\s*(.+?)(?:\n|$)", text, re.IGNORECASE
                    )
                    if desc_match:
                        # Clean up any remaining non-text tokens
                        desc = desc_match.group(1).strip()
                        # Remove any remaining object representations
                        desc = re.sub(r"<.*?>", "", desc)
                        phase_data["description"] = desc

                if "Estimated Duration:" in text or "Estimated Effort:" in text:
                    dur_match = re.search(
                        r"Estimated (?:Duration|Effort):\s*(.+)", text, re.IGNORECASE
                    )
                    if dur_match:
                        phase_data["estimated_duration"] = dur_match.group(1).strip()

                # Check if this paragraph is the validation gate header
                if "Validation Gate:" in text:
                    seen_validation_gate_header = True

            # Extract tasks from markdown lists
            elif isinstance(node, MarkdownList):
                self._extract_tasks_from_list(
                    node, phase_data, seen_validation_gate_header
                )
                # Reset the flag after processing the list
                if seen_validation_gate_header:
                    seen_validation_gate_header = False

        # Build tasks
        tasks = self._parse_collected_tasks(
            phase_data["task_lines"], phase_data["phase_number"]
        )

        return DynamicPhase(
            phase_number=phase_data["phase_number"],
            phase_name=phase_data["phase_name"],
            description=phase_data["description"]
            or f"Phase {phase_data['phase_number']} objectives",
            estimated_duration=phase_data["estimated_duration"],
            tasks=tasks,
            validation_gate=phase_data["validation_gate"],
        )

    def _extract_tasks_from_list(
        self,
        list_node: MarkdownList,
        phase_data: Dict[str, Any],
        is_validation_gate: bool = False,
    ):
        """
        Extract tasks from a markdown list node.

        Args:
            list_node: Mistletoe List node
            phase_data: Phase data dict to populate
            is_validation_gate: True if this list follows a "Validation Gate:" header
        """
        if (
            not list_node
            or not hasattr(list_node, "children")
            or list_node.children is None
        ):
            return

        # If this entire list is a validation gate, extract all items as gate items
        if is_validation_gate:
            for item in list_node.children:
                if isinstance(item, ListItem):
                    gate_items = self._extract_checklist_items(item)
                    phase_data["validation_gate"].extend(gate_items)
            return

        for item in list_node.children:
            if not isinstance(item, ListItem):
                continue

            item_text = self._get_text_content(item)

            # Check if this is a task (contains "Task N.M:")
            if re.search(r"Task \d+\.\d+:", item_text):
                phase_data["task_lines"].append({"text": item_text, "node": item})

            # Check for validation gate items (legacy inline format)
            elif (
                "Validation Gate:" in item_text
                or phase_data["validation_gate"]
                or any(
                    "validation" in line.lower() for line in item_text.split("\n")[:2]
                )
            ):
                # This is validation gate content
                gate_items = self._extract_checklist_items(item)
                phase_data["validation_gate"].extend(gate_items)

    def _extract_task_dependencies(self, text: str) -> List[str]:
        """Extract dependencies from task text."""
        deps_match = re.search(r"Dependencies:\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
        if not deps_match:
            return []

        deps_text = deps_match.group(1).strip()
        if deps_text.lower() == "none":
            return []

        # Extract task IDs like "1.1" from dep text
        task_ids = re.findall(r"\b(\d+\.\d+)\b", deps_text)
        return task_ids if task_ids else [d.strip() for d in deps_text.split(",")]

    def _parse_single_task(self, task_text: str) -> Optional[DynamicTask]:
        """Parse a single task from text."""
        task_match = re.search(r"Task (\d+)\.(\d+):\s*(.+?)(?:\n|$)", task_text)
        if not task_match:
            return None

        task_id = f"{task_match.group(1)}.{task_match.group(2)}"
        task_name = task_match.group(3).strip()

        # Extract estimated time
        time_match = re.search(
            r"Estimated (?:Time|Duration):\s*(.+?)(?:\n|$)", task_text, re.IGNORECASE
        )
        estimated_time = time_match.group(1).strip() if time_match else "Variable"

        return DynamicTask(
            task_id=task_id,
            task_name=task_name,
            description=task_name,
            estimated_time=estimated_time,
            dependencies=self._extract_task_dependencies(task_text),
            acceptance_criteria=self._extract_acceptance_criteria(task_text),
        )

    def _parse_collected_tasks(
        self, task_data_list: List[Dict[str, Any]], phase_number: int
    ) -> List[DynamicTask]:
        """
        Parse collected task data into DynamicTask objects.

        Args:
            task_data_list: List of task data dictionaries
            phase_number: Phase number for context

        Returns:
            List of DynamicTask objects
        """
        tasks = []
        for task_data in task_data_list:
            task = self._parse_single_task(task_data["text"])
            if task:
                tasks.append(task)
        return tasks

    def _extract_acceptance_criteria(self, text: str) -> List[str]:
        """
        Extract acceptance criteria checklist items from text.

        Args:
            text: Task text containing acceptance criteria

        Returns:
            List of acceptance criteria strings
        """
        criteria = []
        in_criteria = False

        for line in text.split("\n"):
            if "Acceptance Criteria:" in line:
                in_criteria = True
                continue

            if in_criteria:
                # Look for checklist items (with or without leading dash)
                stripped = line.strip()
                if stripped.startswith("- [ ]"):
                    criterion = stripped[5:].strip()
                    criteria.append(criterion)
                elif stripped.startswith("[ ]"):
                    # Handle cases where dash is missing (nested items)
                    criterion = stripped[3:].strip()
                    if criterion:
                        criteria.append(criterion)
                elif stripped and not stripped.startswith(("-", "[")):
                    # End of checklist (non-checklist, non-bullet content)
                    break

        return criteria

    def _extract_checklist_items(self, node) -> List[str]:
        """
        Extract checklist items from a node's children.

        Args:
            node: AST node to search

        Returns:
            List of checklist item strings
        """
        items = []
        text = self._get_text_content(node)

        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("- [ ]"):
                item = stripped[5:].strip()
                if item:
                    items.append(item)
            elif stripped.startswith("[ ]"):
                # Handle cases where dash is missing (nested items)
                item = stripped[3:].strip()
                if item:
                    items.append(item)

        return items

    def _get_checkbox_marker(self, node: ListItem) -> str:
        """Get checkbox marker for a list item."""
        if not hasattr(node, "checked"):
            return ""
        checked_val = getattr(node, "checked", None)
        if checked_val is None:
            return ""
        return "- [x] " if checked_val else "- [ ] "

    def _flush_inline_buffer(
        self, inline_buffer: list, checkbox_marker: str, parts: list
    ) -> str:
        """Flush inline buffer to parts list and return updated checkbox marker."""
        if not inline_buffer:
            return checkbox_marker

        content = "".join(inline_buffer)
        if checkbox_marker and not parts:
            parts.append(checkbox_marker + content)
            return ""  # Marker used
        parts.append(content)
        return checkbox_marker

    def _extract_list_item_text(self, node: ListItem) -> str:
        """Extract text from a ListItem node with proper structure."""
        parts: list[str] = []
        inline_buffer: list[str] = []
        checkbox_marker = self._get_checkbox_marker(node)

        for child in node.children if node.children else []:
            if isinstance(child, MarkdownList):
                # Flush inline buffer before nested list
                checkbox_marker = self._flush_inline_buffer(
                    inline_buffer, checkbox_marker, parts
                )
                inline_buffer = []
                # Extract nested list items
                for nested_item in child.children if child.children else []:
                    nested_text = self._get_text_content(nested_item)
                    if nested_text:
                        parts.append(nested_text)
            elif isinstance(child, Paragraph):
                # Flush inline buffer before paragraph
                checkbox_marker = self._flush_inline_buffer(
                    inline_buffer, checkbox_marker, parts
                )
                inline_buffer = []
                text = self._get_text_content(child)
                if text:
                    parts.append(text)
            else:
                # Accumulate inline content
                text = self._get_text_content(child)
                if text:
                    inline_buffer.append(text)

        # Flush remaining inline content
        self._flush_inline_buffer(inline_buffer, checkbox_marker, parts)
        return "\n".join(parts)

    # pylint: disable=too-many-return-statements
    def _get_text_content(self, node) -> str:
        """
        Extract all text content from a node and its children.

        Args:
            node: Mistletoe AST node

        Returns:
            Concatenated text content with preserved structure
        """
        if not node:
            return ""

        if isinstance(node, RawText):
            return str(node.content)

        if isinstance(node, LineBreak):
            return "\n"

        if isinstance(node, ListItem):
            return self._extract_list_item_text(node)

        if hasattr(node, "children") and node.children is not None:
            # Strong nodes: just return first child's content
            if isinstance(node, Strong) and node.children:
                return self._get_text_content(node.children[0])

            parts = []
            for child in node.children:
                text = self._get_text_content(child)
                if text:
                    parts.append(text)
            # For paragraph nodes, inline elements join without newlines
            return "".join(parts)

        return str(node)


__all__ = [
    "ParseError",
    "SourceParser",
    "SpecTasksParser",
]

<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:39:39 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
118,765 / 200K tokens used (59%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<read_file>
<path>mcp_server/core/session.py</path>
<task_progress>
- [x] Read dynamic registry (caching and template rendering)
- [x] Read parsers (AST-based tasks.md parsing)
- [ ] Read session management (workflow execution orchestration)
- [ ] Provide comprehensive implementation analysis
</task_progress>
</read_file>

---

**User:**

[read_file for 'mcp_server/core/session.py'] Result:
"""
Workflow session management.

Session-scoped workflow execution with encapsulated state and lifecycle management.
Replaces stateless service pattern with clean object-oriented design.
"""

# pylint: disable=too-many-instance-attributes
# Justification: WorkflowSession manages 10 attributes for workflow state,
# registry, RAG engine, parsers, and metadata - all essential for session

# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: __init__ needs 10 parameters to configure session with
# all required dependencies and state management

# pylint: disable=too-many-nested-blocks
# Justification: Complex validation logic with multiple conditional paths
# for dynamic vs static content, phase checking, and error handling

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from mcp_server.core.dynamic_registry import (
    DynamicContentRegistry,
    DynamicRegistryError,
)
from mcp_server.core.parsers import SpecTasksParser
from mcp_server.models.workflow import (
    PhaseArtifact,
    WorkflowMetadata,
    WorkflowState,
)
from mcp_server.rag_engine import RAGEngine
from mcp_server.state_manager import StateManager

logger = logging.getLogger(__name__)


class WorkflowSessionError(Exception):
    """Raised when workflow session operations fail."""


class WorkflowSession:
    """
    Session-scoped workflow with lifecycle management.

    Encapsulates all session-specific logic and state for a workflow execution.
    Each session represents one workflow instance from start to completion.

    Key improvements over stateless pattern:
    - No session_id parameter pollution
    - Natural place for dynamic content registry
    - Better encapsulation of session state
    - Easier to test and extend
    - Cleaner API for workflow operations

    Attributes:
        session_id: Unique session identifier
        workflow_type: Type of workflow being executed
        target_file: File being worked on
        state: Current workflow state
        metadata: Workflow metadata (phases, structure, etc.)
        dynamic_registry: Optional registry for dynamic workflows
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
        options: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize workflow session.

        Detects dynamic workflows and initializes registry if needed.

        Args:
            session_id: Unique session identifier
            workflow_type: Workflow type (e.g., "spec_execution_v1")
            target_file: File being worked on
            state: Current workflow state
            rag_engine: RAG engine for content retrieval
            state_manager: State manager for persistence
            workflows_base_path: Base path for workflow definitions
            metadata: Workflow metadata
            options: Optional workflow options (e.g., spec_path for dynamic workflows)

        Raises:
            WorkflowSessionError: If initialization fails
        """
        self.session_id = session_id
        self.workflow_type = workflow_type
        self.target_file = target_file
        self.state = state
        self.rag_engine = rag_engine
        self.state_manager = state_manager
        self.workflows_base_path = workflows_base_path
        self.metadata = metadata
        self.options = options or {}

        # Initialize dynamic content registry if this is a dynamic workflow
        self.dynamic_registry: Optional[DynamicContentRegistry] = None

        if self._is_dynamic():
            try:
                self._initialize_dynamic_registry()
                logger.info(
                    "Session %s: Initialized dynamic content registry", session_id
                )
            except Exception as e:
                raise WorkflowSessionError(
                    f"Failed to initialize dynamic registry: {e}"
                ) from e

        logger.info(
            "Session %s: Created for workflow %s (dynamic=%s)",
            session_id,
            workflow_type,
            self._is_dynamic(),
        )

    def _is_dynamic(self) -> bool:
        """
        Check if this is a dynamic workflow.

        Returns:
            True if workflow has dynamic_phases enabled
        """
        # Check metadata for dynamic_phases flag (use getattr for type safety)
        return bool(getattr(self.metadata, "dynamic_phases", False))

    def _initialize_dynamic_registry(self) -> None:
        """
        Initialize dynamic content registry for this session.

        Loads templates, parses source, and creates cached content structure.

