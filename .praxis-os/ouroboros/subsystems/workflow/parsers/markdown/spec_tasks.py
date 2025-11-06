"""
SpecTasksParser - Defensive parser for tasks.md files.

Implements robust parsing with semantic scoring to handle AI format variations.
Uses phase shift detection for spec_execution_v1 workflow harness.

This is the refactored implementation using modular utilities.
Target: ~400 lines (down from ~800 in monolithic version)
"""

from pathlib import Path
from typing import Dict, List, Optional

from mistletoe import Document
from mistletoe.block_token import Heading, List as MarkdownList

from ouroboros.subsystems.workflow.models import DynamicPhase, DynamicTask

from ..base import ParseError, SourceParser
from ..shared import dependencies as dep_utils
from ..shared import text as text_utils
from ..shared import validation as val_utils
from . import extraction, scoring, traversal


class SpecTasksParser(SourceParser):
    """
    Defensive parser for prAxIs OS spec tasks.md files.

    Uses semantic scoring and flexible pattern matching to handle variations
    in AI-generated markdown. Implements phase shift detection for workflow
    harness integration.

    Key features:
    - Semantic scoring for phase/task identification
    - Phase 0 detection and +1 shift application
    - Task ID normalization to sequential integers
    - Dependency normalization with phase shift
    - Liberal acceptance of format variations
    """

    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse tasks.md with defensive scoring algorithm.

        Implements phase shift for spec_execution_v1:
        - Phase 0 exists → +1 shift (Phase 0 becomes workflow Phase 1)
        - Starts at Phase 1 → no shift

        Args:
            source_path: Path to tasks.md file or directory containing it

        Returns:
            List of DynamicPhase objects with normalized numbering

        Raises:
            ParseError: If file is invalid or cannot be parsed
        """
        # Validate and load file
        source_path = self._resolve_source_path(source_path)
        content = self._load_content(source_path)

        # Parse markdown AST
        try:
            doc = Document(content)
        except Exception as e:
            raise ParseError(f"Failed to parse markdown: {e}") from e

        # Extract phases using defensive algorithm
        phases = self._extract_phases_defensively(doc, source_path)

        if not phases:
            raise ParseError(f"No phases found in {source_path}")

        return phases

    def _resolve_source_path(self, source_path: Path) -> Path:
        """Resolve source path to tasks.md file."""
        if not source_path.exists():
            raise ParseError(f"Source not found: {source_path}")

        if source_path.is_dir():
            tasks_file = source_path / "tasks.md"
            if not tasks_file.exists():
                raise ParseError(
                    f"tasks.md not found in directory: {source_path}"
                )
            return tasks_file

        return source_path

    def _load_content(self, source_path: Path) -> str:
        """Load and validate file content."""
        try:
            content = source_path.read_text(encoding="utf-8")
        except Exception as e:
            raise ParseError(f"Failed to read {source_path}: {e}") from e

        if not content.strip():
            raise ParseError(f"Source file is empty: {source_path}")

        return content

    def _extract_phases_defensively(
        self, doc: Document, source_path: Path
    ) -> List[DynamicPhase]:
        """
        Extract phases using semantic scoring and defensive parsing.

        Strategy:
        1. Find all headers, score them for "phase-ness"
        2. Group by confidence, use high-confidence headers as phases
        3. Extract phase numbers, detect Phase 0
        4. Apply phase shift if needed
        5. Extract tasks for each phase
        6. Normalize task IDs and dependencies

        Args:
            doc: Parsed markdown document
            source_path: Source file path (for error messages)

        Returns:
            List of DynamicPhase objects with normalized numbering
        """
        # Step 1: Find and score all headers
        all_headers = traversal.find_headers(doc)
        
        if not all_headers:
            raise ParseError(f"No headers found in {source_path}")

        # Step 2: Classify headers by confidence
        phase_headers = self._identify_phase_headers(all_headers)

        if not phase_headers:
            raise ParseError(f"No phase headers identified in {source_path}")

        # Step 3: Extract phase numbers and detect shift requirement
        phase_numbers = [
            scoring.extract_phase_number_defensively(
                traversal.get_text_content(h)
            )
            for h in phase_headers
        ]

        # Validate sequence
        is_valid, error = val_utils.validate_phase_sequence(phase_numbers)
        if not is_valid:
            raise ParseError(f"Invalid phase sequence: {error}")

        # Detect phase shift (Phase 0 → +1 shift)
        phase_shift = val_utils.detect_phase_shift_requirement(phase_numbers)

        # Step 4: Build phases with shift applied
        phases = []
        for i, header in enumerate(phase_headers):
            phase = self._build_phase_from_header(
                header, doc, phase_numbers[i], phase_shift
            )
            if phase:
                phases.append(phase)

        return phases

    def _identify_phase_headers(
        self, headers: List[Heading], threshold: float = 0.7
    ) -> List[Heading]:
        """
        Identify which headers represent phases using scoring.

        Uses higher threshold (0.7) to filter out metadata sections
        that score 0.5 but aren't actually phases.

        Args:
            headers: All headers in document
            threshold: Confidence threshold for phase classification (default 0.7)

        Returns:
            List of headers classified as phases, in document order
        """
        phase_headers = []

        for header in headers:
            score = scoring.score_phase_header(header)
            if score >= threshold:
                phase_headers.append(header)

        return phase_headers

    def _build_phase_from_header(
        self,
        header: Heading,
        doc: Document,
        original_phase_num: int,
        phase_shift: int,
    ) -> Optional[DynamicPhase]:
        """
        Build DynamicPhase from header and following content.

        Args:
            header: Phase header node
            doc: Full document
            original_phase_num: Original phase number from markdown
            phase_shift: Shift to apply (+1 if Phase 0 exists, else 0)

        Returns:
            DynamicPhase object or None if invalid
        """
        # Apply shift to phase number
        workflow_phase_num = original_phase_num + phase_shift

        # Extract phase content (nodes between this header and next phase)
        phase_content = self._extract_content_after_header(header, doc)

        # Extract metadata
        header_text = traversal.get_text_content(header)
        phase_info = extraction.extract_phase_info(header_text, phase_content)

        if not phase_info:
            return None

        phase_name = phase_info.get("phase_name", f"Phase {workflow_phase_num}")
        objective = phase_info.get("objective", "")
        estimated_duration = phase_info.get("estimated_duration", "Variable")

        # Extract tasks
        tasks = self._extract_tasks_from_content(
            phase_content, workflow_phase_num, phase_shift
        )

        # Extract validation gate
        validation_gate = extraction.extract_validation_gate(phase_content)

        return DynamicPhase(
            phase_number=workflow_phase_num,
            phase_name=phase_name,
            description=objective,
            estimated_duration=estimated_duration,
            tasks=tasks,
            validation_gate=validation_gate,
        )

    def _extract_content_after_header(
        self, header: Heading, doc: Document
    ) -> str:
        """
        Extract content between header and next same-level header.

        Args:
            header: Starting header
            doc: Full document

        Returns:
            Content string
        """
        # Find header position in document
        header_index = -1
        for i, child in enumerate(doc.children):
            if child is header:
                header_index = i
                break

        if header_index == -1:
            return ""

        # Collect content until next same-level header
        content_parts = []
        for i in range(header_index + 1, len(doc.children)):
            child = doc.children[i]

            # Stop at next phase header
            if isinstance(child, Heading) and child.level <= header.level:
                if scoring.score_phase_header(child) >= 0.5:
                    break

            # Collect content
            text = traversal.get_text_content(child)
            if text:
                content_parts.append(text)

        return "\n\n".join(content_parts)

    def _extract_tasks_from_content(
        self, content: str, phase_number: int, phase_shift: int
    ) -> List[DynamicTask]:
        """
        Extract tasks from phase content using flexible patterns.

        Args:
            content: Phase content text
            phase_number: Workflow phase number (after shift)
            phase_shift: Shift applied to phases

        Returns:
            List of DynamicTask objects with normalized IDs
        """
        tasks = []
        task_counter = 1  # Normalize to 1, 2, 3...

        # Split content into potential task blocks
        # Look for task indicators (Task N.N, N.N:, checkboxes)
        task_blocks = self._split_into_task_blocks(content)

        for block in task_blocks:
            # Score block as potential task
            score = scoring.score_task_indicator(block)
            
            if score < 0.3:  # Low confidence, skip
                continue

            # Extract task info
            task_info = extraction.extract_task_info(block)
            if not task_info:
                continue

            # Build task with normalized ID
            normalized_task_id = f"{phase_number}.{task_counter}"

            # Extract dependencies and normalize them
            dep_text = text_utils.extract_metadata(
                block, ["dependencies", "depends on", "requires", "after"]
            )
            dependencies = []
            if dep_text:
                raw_deps = dep_utils.parse_dependency_references(dep_text)
                # Normalize dependencies with phase shift
                dependencies = [
                    dep_utils.normalize_dependency_format(d, phase_shift)
                    for d in raw_deps
                ]

            # Extract acceptance criteria
            acceptance_criteria = extraction.extract_acceptance_criteria(block)

            task = DynamicTask(
                task_id=normalized_task_id,
                task_name=task_info.get("task_name", f"Task {task_counter}"),
                description=task_info.get("description", ""),
                estimated_time=task_info.get("estimated_time", "Variable"),
                dependencies=dependencies,
                acceptance_criteria=acceptance_criteria,
            )

            tasks.append(task)
            task_counter += 1

        return tasks

    def _split_into_task_blocks(self, content: str) -> List[str]:
        """
        Split content into potential task blocks.

        Uses multiple strategies:
        - Split on "Task N.N" patterns
        - Split on "N.N:" patterns
        - Split on checkbox list items
        - Split on ### subheaders

        Args:
            content: Content to split

        Returns:
            List of content blocks that might be tasks
        """
        blocks = []

        # Strategy 1: Split on task patterns
        # Match "Task N.N" or "N.N:" at start of line
        pattern = r"(?:^|\n)(?:[-*]\s*\[[ x]\]\s*)?(?:\*\*)?(?:[Tt]ask\s+)?(\d+\.\d+)"
        
        split_positions = [0]
        for match in re.finditer(pattern, content):
            split_positions.append(match.start())
        split_positions.append(len(content))

        # Extract blocks between split positions
        for i in range(len(split_positions) - 1):
            start = split_positions[i]
            end = split_positions[i + 1]
            block = content[start:end].strip()
            if block and len(block) > 10:  # Minimum block size
                blocks.append(block)

        # If no blocks found, try paragraph splitting
        if not blocks:
            blocks = [p.strip() for p in content.split("\n\n") if p.strip()]

        return blocks


import re  # Import at module level for _split_into_task_blocks


__all__ = [
    "SpecTasksParser",
]
