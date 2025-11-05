"""
Workflow Renderer: Load and render workflow definitions and phase content.

Architecture:
- Loads workflow metadata from metadata.json
- Renders phase content from phase directories
- Thread-safe caching for performance
"""

import json
import logging
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from ouroboros.subsystems.workflow.models import WorkflowMetadata
from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class RendererError(ActionableError):
    """Workflow rendering failed."""

    pass


class WorkflowRenderer:
    """
    Loads and renders workflow definitions.

    Responsibilities:
    - Load workflow metadata from metadata.json
    - Render phase content from phase directories
    - Cache loaded workflows for performance
    """

    def __init__(self, workflows_dir: Path):
        """
        Initialize workflow renderer.

        Args:
            workflows_dir: Base directory for workflow definitions
        """
        self.workflows_dir = workflows_dir
        self._metadata_cache: Dict[str, WorkflowMetadata] = {}
        self._cache_lock = threading.RLock()

        logger.info("WorkflowRenderer initialized", extra={"workflows_dir": str(workflows_dir)})

    def load_metadata(self, workflow_type: str) -> WorkflowMetadata:
        """
        Load workflow metadata.

        Thread-safe with caching.

        Args:
            workflow_type: Workflow type identifier

        Returns:
            WorkflowMetadata

        Raises:
            RendererError: If metadata cannot be loaded
        """
        # Fast path: Check cache
        if workflow_type in self._metadata_cache:
            return self._metadata_cache[workflow_type]

        # Slow path: Load with lock
        with self._cache_lock:
            # Re-check inside lock
            if workflow_type in self._metadata_cache:
                return self._metadata_cache[workflow_type]

            # Load metadata
            metadata = self._load_metadata_from_disk(workflow_type)

            # Cache and return
            self._metadata_cache[workflow_type] = metadata
            return metadata

    def get_phase_content(self, workflow_type: str, phase: int) -> Dict[str, Any]:
        """
        Get phase content (phase overview).

        Args:
            workflow_type: Workflow type identifier
            phase: Phase number

        Returns:
            Dictionary with phase content

        Raises:
            RendererError: If phase content cannot be loaded
        """
        phase_dir = self.workflows_dir / workflow_type / "phases" / str(phase)

        if not phase_dir.exists():
            raise RendererError(
                what_failed="Phase content loading",
                why_failed=f"Phase directory not found: {phase_dir}",
                how_to_fix=f"Create phase directory: mkdir -p {phase_dir}",
            )

        # Load phase.md (phase overview)
        phase_file = phase_dir / "phase.md"
        phase_content = None
        if phase_file.exists():
            try:
                phase_content = phase_file.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning("Failed to load phase.md", extra={"phase_file": str(phase_file), "error": str(e)})
        else:
            logger.warning("phase.md not found", extra={"phase_dir": str(phase_dir)})

        # Load phase.json if it exists (additional metadata)
        phase_metadata_file = phase_dir / "phase.json"
        phase_metadata = {}
        if phase_metadata_file.exists():
            try:
                phase_metadata = json.loads(phase_metadata_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(
                    "Failed to load phase.json", extra={"phase_metadata_file": str(phase_metadata_file), "error": str(e)}
                )

        return {
            "phase": phase,
            "workflow_type": workflow_type,
            "content": phase_content,
            "metadata": phase_metadata,
        }
    
    def get_task_content(self, workflow_type: str, phase: int, task_number: int) -> Dict[str, Any]:
        """
        Get individual task content.

        Args:
            workflow_type: Workflow type identifier
            phase: Phase number
            task_number: Task number within phase

        Returns:
            Dictionary with task content

        Raises:
            RendererError: If task content cannot be loaded
        """
        phase_dir = self.workflows_dir / workflow_type / "phases" / str(phase)

        if not phase_dir.exists():
            raise RendererError(
                what_failed="Task content loading",
                why_failed=f"Phase directory not found: {phase_dir}",
                how_to_fix=f"Create phase directory: mkdir -p {phase_dir}",
            )

        # Find task file matching pattern: task-{task_number}-*.md
        task_files = list(phase_dir.glob(f"task-{task_number}-*.md"))
        
        if not task_files:
            raise RendererError(
                what_failed="Task content loading",
                why_failed=f"Task file not found for task {task_number} in phase {phase}",
                how_to_fix=f"Create task file: {phase_dir}/task-{task_number}-name.md",
            )
        
        if len(task_files) > 1:
            logger.warning(
                "Multiple task files found for task number",
                extra={"phase": phase, "task_number": task_number, "files": [str(f) for f in task_files]},
            )
        
        # Use first matching file
        task_file = task_files[0]
        
        try:
            task_content = task_file.read_text(encoding="utf-8")
        except Exception as e:
            raise RendererError(
                what_failed="Task content loading",
                why_failed=f"Failed to read task file: {task_file}",
                how_to_fix=f"Check file permissions: chmod 644 {task_file}",
            ) from e

        return {
            "phase": phase,
            "task_number": task_number,
            "workflow_type": workflow_type,
            "content": task_content,
            "file": task_file.name,
        }

    def list_workflows(self) -> Dict[str, WorkflowMetadata]:
        """
        List all available workflows.

        Returns:
            Dictionary of workflow_type -> WorkflowMetadata
        """
        workflows = {}

        if not self.workflows_dir.exists():
            logger.warning("Workflows directory does not exist", extra={"workflows_dir": str(self.workflows_dir)})
            return workflows

        for workflow_dir in self.workflows_dir.iterdir():
            if not workflow_dir.is_dir():
                continue

            metadata_file = workflow_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            try:
                metadata = self.load_metadata(workflow_dir.name)
                workflows[workflow_dir.name] = metadata
            except Exception as e:
                logger.warning(
                    "Failed to load workflow metadata",
                    extra={"workflow_dir": str(workflow_dir), "error": str(e)},
                )
                continue

        return workflows

    def _load_metadata_from_disk(self, workflow_type: str) -> WorkflowMetadata:
        """
        Load metadata from disk.

        Args:
            workflow_type: Workflow type identifier

        Returns:
            WorkflowMetadata

        Raises:
            RendererError: If metadata cannot be loaded
        """
        metadata_file = self.workflows_dir / workflow_type / "metadata.json"

        if not metadata_file.exists():
            raise RendererError(
                what_failed="Workflow metadata loading",
                why_failed=f"Metadata file not found: {metadata_file}",
                how_to_fix=f"Create workflow directory with metadata.json: {metadata_file.parent}",
            )

        try:
            content = json.loads(metadata_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise RendererError(
                what_failed="Workflow metadata parsing",
                why_failed=f"Invalid JSON in {metadata_file}: {e}",
                how_to_fix=f"Fix JSON syntax in {metadata_file}",
            ) from e
        except Exception as e:
            raise RendererError(
                what_failed="Workflow metadata loading",
                why_failed=f"Failed to read {metadata_file}: {e}",
                how_to_fix=f"Check file permissions: chmod 644 {metadata_file}",
            ) from e

        # Parse into Pydantic model (Pydantic handles all field mapping)
        try:
            # Ensure workflow_type is set if missing
            if "workflow_type" not in content:
                content["workflow_type"] = workflow_type
            
            # Let Pydantic parse the entire JSON with the full schema
            metadata = WorkflowMetadata(**content)
            return metadata
        except Exception as e:
            raise RendererError(
                what_failed="Workflow metadata validation",
                why_failed=f"Invalid metadata format: {e}",
                how_to_fix="Check metadata.json structure matches WorkflowMetadata schema",
            ) from e

