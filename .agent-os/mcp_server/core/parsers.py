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

import yaml

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

        Uses flexible pattern matching to handle AI format variations:
        - ## or ### headers
        - "Phase N:" or "Phase N -" or "N." or "N:"
        - Phase number before or after name

        Args:
            doc: Mistletoe Document object

        Returns:
            List of DynamicPhase objects
        """
        phases: List[DynamicPhase] = []
        current_phase_data = None

        for node in doc.children:
            # Semantic check: match content pattern on ANY heading level
            if isinstance(node, Heading):
                header_text = self._get_text_content(node)

                # Try to extract phase info (semantic pattern match)
                phase_info = self._extract_phase_info(header_text)

                if phase_info:
                    # Save previous phase if exists
                    if current_phase_data:
                        phase = self._build_phase(current_phase_data)
                        if phase:
                            phases.append(phase)

                    # Start new phase
                    current_phase_data = {
                        "phase_number": phase_info["number"],
                        "phase_name": phase_info["name"],
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

    def _extract_phase_info(self, header_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract phase number and name using semantic analysis (no regex).

        Semantic approach: Look for "phase" keyword + number, then extract name.
        Works for any format variation.

        Args:
            header_text: Header text to parse

        Returns:
            Dict with 'number' and 'name' or None if not a phase header
        """
        text_lower = header_text.lower()

        # CRITICAL: Reject if this looks like a task
        # Tasks have "task" keyword or "N.M" pattern (two numbers with dot)
        if "task" in text_lower:
            return None

        # Semantic check: Must have "phase" keyword
        if "phase" not in text_lower:
            # Maybe it's just "N. Name" or "N: Name" format
            # But NOT if it has task pattern (N.M)
            
            # Check for task pattern (e.g., "1.1")
            first_num = self._extract_first_number(header_text)
            if first_num:
                # After first number, if we see dot/dash followed by another digit,
                # this is a task pattern, not a phase
                i = 0
                while i < len(header_text) and not header_text[i].isdigit():
                    i += 1
                while i < len(header_text) and header_text[i].isdigit():
                    i += 1
                # Check what comes after first number
                if i < len(header_text) and header_text[i] in ".-":
                    next_i = i + 1
                    if next_i < len(header_text) and header_text[next_i].isdigit():
                        # This is a task pattern (N.M), not a phase
                        return None
                
                # No task pattern, treat as phase
                # Find where name starts after the number
                i = 0
                # Skip to number
                while i < len(header_text) and not header_text[i].isdigit():
                    i += 1
                # Skip number digits
                while i < len(header_text) and header_text[i].isdigit():
                    i += 1
                # Skip separator and whitespace
                while i < len(header_text) and header_text[i] in ".:-— \t":
                    i += 1
                # Rest is name
                name = header_text[i:].strip()
                if name:
                    return {"number": first_num, "name": name}
            return None

        # Extract number (any digits found after "phase")
        number = self._extract_first_number(header_text)
        if not number:
            return None

        # SEMANTIC REQUIREMENT: Must have separator after number
        # Find position after number, check for separator
        # This prevents "Phase 1 Tasks" from matching (no separator)
        i = 0
        while i < len(header_text) and not header_text[i].isdigit():
            i += 1
        # Skip number digits
        while i < len(header_text) and header_text[i].isdigit():
            i += 1
        # Check for separator
        if i >= len(header_text):
            return None
        # Skip whitespace
        while i < len(header_text) and header_text[i] in " \t":
            i += 1
        if i >= len(header_text):
            return None
        # Must have separator (: or -)
        if header_text[i] not in ":.-—−":
            return None

        # Extract name: Everything after separator
        i += 1  # Skip separator
        # Skip whitespace after separator
        while i < len(header_text) and header_text[i] in " \t":
            i += 1

        name = header_text[i:].strip()

        return {"number": number, "name": name} if name else None

    def _extract_first_number(self, text: str) -> Optional[int]:
        """Extract first number found in text (native Python, no regex)."""
        digits = []
        for char in text:
            if char.isdigit():
                digits.append(char)
            elif digits:  # Found digits, then non-digit
                break

        if digits:
            return int("".join(digits))
        return None

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
        current_task_content = []  # Collect content for current task heading
        current_task_heading = None

        for i, node in enumerate(phase_data["nodes"]):
            if isinstance(node, Paragraph):
                text = self._get_text_content(node)

                # Check if this paragraph starts with a task (e.g., "Task 1.1:")
                task_info = self._extract_task_info(text)
                if task_info and not current_task_heading:
                    # This paragraph IS a task heading (without markdown heading marker)
                    # Start collecting content for this task
                    current_task_heading = text
                    current_task_content = []
                    continue

                # If we're collecting task content, add this paragraph
                if current_task_heading:
                    current_task_content.append(text)
                else:
                    # Look for metadata patterns using flexible matching
                    desc = self._extract_metadata(text, ["objective", "goal", "purpose"])
                    if desc:
                        phase_data["description"] = desc

                    duration = self._extract_metadata(
                        text,
                        [
                            "estimated duration",
                            "estimated effort",
                            "timeframe",
                            "estimated time",
                        ],
                    )
                    if duration:
                        phase_data["estimated_duration"] = duration

                    # Check if this paragraph is the validation gate header
                    if "Validation Gate:" in text:
                        seen_validation_gate_header = True

            # Extract tasks from markdown lists
            elif isinstance(node, MarkdownList):
                # Flush any pending task content first
                if current_task_heading:
                    full_task_text = current_task_heading + "\n" + "\n".join(current_task_content)
                    phase_data["task_lines"].append({"text": full_task_text, "node": node})
                    current_task_heading = None
                    current_task_content = []

                self._extract_tasks_from_list(
                    node, phase_data, seen_validation_gate_header
                )
                # Reset the flag after processing the list
                if seen_validation_gate_header:
                    seen_validation_gate_header = False

            # Extract tasks from headings (ANY level - semantic pattern match)
            elif isinstance(node, Heading):
                header_text = self._get_text_content(node)
                task_info = self._extract_task_info(header_text)
                
                if task_info:
                    # Flush previous task if exists
                    if current_task_heading:
                        full_task_text = current_task_heading + "\n" + "\n".join(current_task_content)
                        phase_data["task_lines"].append({"text": full_task_text, "node": node})
                    
                    # Start collecting content for this new task
                    current_task_heading = header_text
                    current_task_content = []
                else:
                    # Not a task heading, if we're collecting task content, this ends it
                    if current_task_heading:
                        full_task_text = current_task_heading + "\n" + "\n".join(current_task_content)
                        phase_data["task_lines"].append({"text": full_task_text, "node": node})
                        current_task_heading = None
                        current_task_content = []

        # Flush any remaining task content
        if current_task_heading:
            full_task_text = current_task_heading + "\n" + "\n".join(current_task_content)
            phase_data["task_lines"].append({"text": full_task_text, "node": None})

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

    def _extract_metadata(self, text: str, labels: List[str]) -> Optional[str]:
        """
        Extract metadata value using semantic search (native Python, no regex).

        Args:
            text: Text to search
            labels: List of possible label variations (lowercase)

        Returns:
            Extracted value or None
        """
        text_lower = text.lower()

        for label in labels:
            # Find label in text
            label_pos = text_lower.find(label)
            if label_pos == -1:
                continue

            # Found the label, now find the separator and value
            after_label = text[label_pos + len(label) :]
            after_label_stripped = after_label.lstrip()

            # Check for common separators
            if not after_label_stripped:
                continue

            first_char = after_label_stripped[0]
            if first_char in ":−-—":
                # Skip separator and whitespace
                value_start = after_label_stripped[1:].lstrip()
                # Extract until newline or end
                value_end = value_start.find("\n")
                if value_end != -1:
                    value = value_start[:value_end].strip()
                else:
                    value = value_start.strip()

                # Clean up any HTML-like tags
                if "<" in value and ">" in value:
                    clean_parts = []
                    in_tag = False
                    for char in value:
                        if char == "<":
                            in_tag = True
                        elif char == ">":
                            in_tag = False
                        elif not in_tag:
                            clean_parts.append(char)
                    value = "".join(clean_parts).strip()

                if value:
                    return value

        return None

    def _extract_task_dependencies(self, text: str) -> List[str]:
        """Extract dependencies using semantic search (native Python)."""
        # Try multiple dependency labels
        dep_text = self._extract_metadata(
            text, ["dependencies", "depends on", "requires", "after"]
        )
        if not dep_text:
            return []

        if dep_text.lower() == "none":
            return []

        # Extract task IDs like "1.1" from dep text (native Python)
        task_ids = []
        i = 0
        while i < len(dep_text):
            if dep_text[i].isdigit():
                # Found a digit, collect the number
                num1_digits = []
                while i < len(dep_text) and dep_text[i].isdigit():
                    num1_digits.append(dep_text[i])
                    i += 1

                # Check for dot or dash separator
                if i < len(dep_text) and dep_text[i] in ".-":
                    i += 1
                    # Collect second number
                    num2_digits = []
                    while i < len(dep_text) and dep_text[i].isdigit():
                        num2_digits.append(dep_text[i])
                        i += 1

                    if num1_digits and num2_digits:
                        task_id = "".join(num1_digits) + "." + "".join(num2_digits)
                        task_ids.append(task_id)
            else:
                i += 1

        return task_ids if task_ids else [d.strip() for d in dep_text.split(",")]

    def _parse_single_task(self, task_text: str) -> Optional[DynamicTask]:
        """Parse a single task using flexible patterns."""
        # Try multiple task ID patterns
        task_info = self._extract_task_info(task_text)
        if not task_info:
            return None

        # Extract estimated time using flexible matching
        estimated_time = (
            self._extract_metadata(
                task_text, ["estimated time", "estimated duration", "time", "duration"]
            )
            or "Variable"
        )

        return DynamicTask(
            task_id=task_info["id"],
            task_name=task_info["name"],
            description=task_info["name"],
            estimated_time=estimated_time,
            dependencies=self._extract_task_dependencies(task_text),
            acceptance_criteria=self._extract_acceptance_criteria(task_text),
        )

    def _extract_task_info(self, text: str) -> Optional[Dict[str, str]]:
        """
        Extract task ID and name using semantic search (native Python, no regex).

        Looks for "task" keyword + two numbers separated by dot/dash,
        then extracts the name after separator.

        Args:
            text: Text containing task

        Returns:
            Dict with 'id' and 'name' or None
        """
        text_lower = text.lower()

        # Look for "task" keyword
        task_pos = text_lower.find("task")
        if task_pos == -1:
            # Try without "task" keyword - just look for N.M pattern at start
            task_pos = 0
        else:
            task_pos += 4  # Skip "task" word

        # Skip whitespace and formatting (* -)
        i = task_pos
        while i < len(text) and text[i] in " \t\n*-":
            i += 1

        # Extract first number
        num1_digits = []
        while i < len(text) and text[i].isdigit():
            num1_digits.append(text[i])
            i += 1

        if not num1_digits:
            return None

        # Check for separator (. or -)
        if i >= len(text) or text[i] not in ".-−":
            return None
        i += 1  # Skip separator

        # Extract second number
        num2_digits = []
        while i < len(text) and text[i].isdigit():
            num2_digits.append(text[i])
            i += 1

        if not num2_digits:
            return None

        # Found task ID!
        task_id = "".join(num1_digits) + "." + "".join(num2_digits)

        # Now extract the name - skip colon/dash and whitespace
        while i < len(text) and text[i] in " \t:*-−":
            i += 1

        # Collect rest of line as name
        name_chars = []
        while i < len(text) and text[i] != "\n":
            name_chars.append(text[i])
            i += 1

        task_name = "".join(name_chars).strip()

        if not task_name:
            return None

        return {"id": task_id, "name": task_name}

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
                # Convert to list if needed to access first element
                children_list = list(node.children)
                if children_list:
                    return self._get_text_content(children_list[0])

            parts = []
            for child in node.children:
                text = self._get_text_content(child)
                if text:
                    parts.append(text)
            # For paragraph nodes, inline elements join without newlines
            return "".join(parts)

        return str(node)


class WorkflowDefinitionParser(SourceParser):
    """
    Parser for workflow definition YAML files.

    Parses workflow definition YAML and extracts phase/task structure
    for iterative workflow generation in workflow_creation_v1.

    Unlike SpecTasksParser (which parses markdown for display),
    this parser extracts structured data for file generation.
    """

    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse workflow definition YAML into DynamicPhase objects.

        Args:
            source_path: Path to workflow definition YAML file

        Returns:
            List of DynamicPhase objects (one per target workflow phase)

        Raises:
            ParseError: If file is invalid or cannot be parsed
        """
        if not source_path.exists():
            raise ParseError(f"Definition file not found: {source_path}")

        try:
            with open(source_path, "r", encoding="utf-8") as f:
                definition = yaml.safe_load(f)
        except Exception as e:
            raise ParseError(f"Failed to read YAML: {e}") from e

        if not definition:
            raise ParseError(f"Definition file is empty: {source_path}")

        # Extract phases array
        phases_data = definition.get("phases", [])
        if not phases_data:
            raise ParseError("No phases found in definition")

        # Convert each target phase into DynamicPhase
        dynamic_phases = []
        for phase_data in phases_data:
            dynamic_phase = self._build_dynamic_phase(phase_data)
            if dynamic_phase:
                dynamic_phases.append(dynamic_phase)

        return dynamic_phases

    def _build_dynamic_phase(self, phase_data: dict) -> Optional[DynamicPhase]:
        """
        Build a DynamicPhase from workflow definition phase data.

        Args:
            phase_data: Phase dictionary from workflow definition

        Returns:
            DynamicPhase object or None if invalid
        """
        phase_number = phase_data.get("number", 0)
        phase_name = phase_data.get("name", f"Phase {phase_number}")
        description = phase_data.get("purpose", "")
        estimated_duration = phase_data.get("estimated_duration", "Variable")

        # Extract tasks
        tasks_data = phase_data.get("tasks", [])
        tasks = []
        for task_data in tasks_data:
            task = self._build_dynamic_task(task_data, phase_number)
            if task:
                tasks.append(task)

        # Extract validation gate
        validation_gate_data = phase_data.get("validation_gate", {})
        validation_gate = self._extract_validation_gate(validation_gate_data)

        return DynamicPhase(
            phase_number=phase_number,
            phase_name=phase_name,
            description=description,
            estimated_duration=estimated_duration,
            tasks=tasks,
            validation_gate=validation_gate,
        )

    def _build_dynamic_task(
        self, task_data: dict, phase_number: int
    ) -> Optional[DynamicTask]:
        """
        Build a DynamicTask from workflow definition task data.

        Args:
            task_data: Task dictionary from workflow definition
            phase_number: Parent phase number

        Returns:
            DynamicTask object or None if invalid
        """
        task_number = task_data.get("number", 1)
        task_name = task_data.get("name", f"task-{task_number}")
        task_purpose = task_data.get("purpose", "")

        # Build task ID (matches phase.task format)
        task_id = f"{phase_number}.{task_number}"

        # Extract optional fields
        estimated_time = task_data.get("estimated_time", "Variable")
        dependencies = task_data.get("dependencies", [])
        acceptance_criteria = task_data.get("validation_criteria", [])

        return DynamicTask(
            task_id=task_id,
            task_name=task_name,
            description=task_purpose,
            estimated_time=estimated_time,
            dependencies=dependencies,
            acceptance_criteria=acceptance_criteria,
        )

    def _extract_validation_gate(self, validation_gate_data: dict) -> List[str]:
        """
        Extract validation gate criteria from definition.

        Args:
            validation_gate_data: Validation gate dictionary

        Returns:
            List of validation criteria strings
        """
        criteria = []

        # Extract evidence_required fields
        evidence_required = validation_gate_data.get("evidence_required", {})
        for field_name, field_data in evidence_required.items():
            if isinstance(field_data, dict):
                description = field_data.get("description", field_name)
                field_type = field_data.get("type", "unknown")
                validator = field_data.get("validator", "")
                criteria.append(
                    f"{field_name} ({field_type}, {validator}): {description}"
                )
            else:
                criteria.append(str(field_data))

        return criteria


__all__ = [
    "ParseError",
    "SourceParser",
    "SpecTasksParser",
    "WorkflowDefinitionParser",
]
