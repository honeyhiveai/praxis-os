"""
Workflow session management.

Session-scoped workflow execution with encapsulated state and lifecycle management.
Replaces stateless service pattern with clean object-oriented design.
"""

# pylint: disable=too-many-instance-attributes
# Justification: WorkflowSession manages 10 attributes for workflow state,
# registry, RAG engine, parsers, and metadata - all essential for session

# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: __init__ needs 11 parameters to configure session with
# all required dependencies and state management (includes engine for validation)

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
from mcp_server.core.parsers import (
    SourceParser,
    SpecTasksParser,
    WorkflowDefinitionParser,
)
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
        engine: Any,  # WorkflowEngine instance for validation
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
            engine: WorkflowEngine instance for checkpoint validation
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
        self.engine = engine
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

        Raises:
            DynamicRegistryError: If initialization fails
        """
        # Get dynamic configuration from metadata (use getattr for type safety)
        dynamic_config = getattr(self.metadata, "dynamic_config", None)
        if not dynamic_config:
            raise DynamicRegistryError(
                "Dynamic workflow missing dynamic_config in metadata"
            )

        # Get source path from options
        source_path_key = dynamic_config.get("source_path_key", "spec_path")
        source_path_str = self.options.get(source_path_key)

        if not source_path_str:
            raise DynamicRegistryError(
                f"Dynamic workflow requires '{source_path_key}' in options"
            )

        source_path = Path(source_path_str)

        # Get template paths
        workflow_dir = self.workflows_base_path / self.workflow_type
        templates = dynamic_config.get("templates", {})

        phase_template_path = workflow_dir / templates.get(
            "phase", "phases/dynamic/phase-template.md"
        )
        task_template_path = workflow_dir / templates.get(
            "task", "phases/dynamic/task-template.md"
        )

        # Get parser (defaults to spec_tasks_parser for backward compatibility)
        parser_name = dynamic_config.get("parser", "spec_tasks_parser")
        parser: SourceParser
        if parser_name == "spec_tasks_parser":
            parser = SpecTasksParser()
        elif parser_name == "workflow_definition_parser":
            parser = WorkflowDefinitionParser()
        else:
            raise DynamicRegistryError(f"Unsupported parser: {parser_name}")

        # Create registry
        self.dynamic_registry = DynamicContentRegistry(
            workflow_type=self.workflow_type,
            phase_template_path=phase_template_path,
            task_template_path=task_template_path,
            source_path=source_path,
            parser=parser,
        )

    def get_current_phase(self) -> Dict[str, Any]:
        """
        Get current phase content.

        No session_id parameter needed - cleaner API!

        Returns:
            Dictionary with phase content, tasks, and metadata

        Raises:
            WorkflowSessionError: If phase retrieval fails
        """
        current_phase = self.state.current_phase

        # Check if workflow is complete
        if self.state.is_complete():
            return {
                "session_id": self.session_id,
                "workflow_type": self.workflow_type,
                "current_phase": current_phase,
                "is_complete": True,
                "message": "Workflow complete! All phases finished.",
            }

        # Get phase content based on workflow type
        try:
            if self._is_dynamic() and self.dynamic_registry:
                # Check if phase exists in dynamic registry
                # (Phase 0 is usually static, phases 1+ are dynamic)
                if self.dynamic_registry.has_phase(current_phase):
                    return self._get_dynamic_phase_content(current_phase)

                # Fallback to static content for phases not in dynamic registry
                return self._get_static_phase_content(current_phase)

            return self._get_static_phase_content(current_phase)
        except Exception as e:
            raise WorkflowSessionError(f"Failed to get phase content: {e}") from e

    def _get_dynamic_phase_content(self, phase: int) -> Dict[str, Any]:
        """
        Get dynamically-rendered phase content.

        Args:
            phase: Phase number

        Returns:
            Phase content with template-wrapped enforcement
        """
        if not self.dynamic_registry:
            raise WorkflowSessionError("Dynamic registry not initialized")

        # Get rendered phase content
        phase_content = self.dynamic_registry.get_phase_content(phase)

        # Get phase metadata for response structure
        phase_metadata = self.dynamic_registry.get_phase_metadata(phase)

        return {
            "session_id": self.session_id,
            "workflow_type": self.workflow_type,
            "current_phase": phase,
            "phase_name": phase_metadata["phase_name"],
            "phase_content": phase_content,
            "tasks": phase_metadata["tasks"],
            "task_count": phase_metadata["task_count"],
            "validation_gate": phase_metadata["validation_gate"],
            "source": "dynamic",
        }

    def _get_static_phase_content(self, phase: int) -> Dict[str, Any]:
        """
        Get static phase content from RAG.

        Args:
            phase: Phase number

        Returns:
            Phase content from RAG search
        """
        # Query RAG for phase content
        query = f"{self.workflow_type} Phase {phase}"

        result = self.rag_engine.search(
            query=query, n_results=5, filters={"phase": phase}
        )

        return {
            "session_id": self.session_id,
            "workflow_type": self.workflow_type,
            "current_phase": phase,
            "phase_content": result.chunks if result.chunks else [],
            "source": "rag",
        }

    def get_task(self, phase: int, task_number: int) -> Dict[str, Any]:
        """
        Get task content.

        Clean parameters - no session_id needed!

        Args:
            phase: Phase number
            task_number: Task number within phase (1-indexed)

        Returns:
            Dictionary with task content and metadata

        Raises:
            WorkflowSessionError: If task retrieval fails
        """
        # Validate phase access
        if not self.state.can_access_phase(phase):
            raise WorkflowSessionError(
                f"Cannot access phase {phase}. "
                f"Current phase is {self.state.current_phase}."
            )

        try:
            if self._is_dynamic() and self.dynamic_registry:
                # Check if phase exists in dynamic registry
                if self.dynamic_registry.has_phase(phase):
                    return self._get_dynamic_task_content(phase, task_number)

                # Fallback to static content for phases not in dynamic registry
                return self._get_static_task_content(phase, task_number)

            return self._get_static_task_content(phase, task_number)
        except Exception as e:
            raise WorkflowSessionError(f"Failed to get task content: {e}") from e

    def _get_dynamic_task_content(self, phase: int, task_number: int) -> Dict[str, Any]:
        """
        Get dynamically-rendered task content.

        Args:
            phase: Phase number
            task_number: Task number

        Returns:
            Task content with template-wrapped enforcement
        """
        if not self.dynamic_registry:
            raise WorkflowSessionError("Dynamic registry not initialized")

        # Get rendered task content
        task_content = self.dynamic_registry.get_task_content(phase, task_number)

        # Get phase metadata for context
        phase_metadata = self.dynamic_registry.get_phase_metadata(phase)

        # Find task metadata
        task_metadata = None
        for task in phase_metadata["tasks"]:
            if task["task_number"] == task_number:
                task_metadata = task
                break

        return {
            "session_id": self.session_id,
            "workflow_type": self.workflow_type,
            "phase": phase,
            "task_number": task_number,
            "task_content": task_content,
            "task_metadata": task_metadata,
            "source": "dynamic",
        }

    def _get_static_task_content(self, phase: int, task_number: int) -> Dict[str, Any]:
        """
        Get static task content from metadata or RAG.

        First checks if the task is defined in metadata.json (for hybrid
        dynamic workflows like spec_execution_v1 where Phase 0 is static
        but Phase 1-N are dynamic). Falls back to RAG if not found in metadata.

        Args:
            phase: Phase number
            task_number: Task number

        Returns:
            Task content from metadata or RAG search

        Raises:
            WorkflowSessionError: If task not found
        """
        # Check metadata first for static task definitions
        if hasattr(self.metadata, "phases") and self.metadata.phases:
            for phase_meta in self.metadata.phases:
                if phase_meta.phase_number == phase:
                    # Check if this phase has tasks defined in metadata
                    if phase_meta.tasks is not None and len(phase_meta.tasks) > 0:
                        for task in phase_meta.tasks:
                            if task.get("task_number") == task_number:
                                # Found task in metadata, load from file
                                task_file = task.get("file")
                                if task_file:
                                    return self._load_task_from_file(
                                        phase, task_number, task_file, task
                                    )

        # Fallback to RAG for tasks not in metadata
        query = f"{self.workflow_type} Phase {phase} Task {task_number}"

        result = self.rag_engine.search(
            query=query, n_results=3, filters={"phase": phase}
        )

        if not result.chunks:
            raise WorkflowSessionError(f"Task {task_number} not found in Phase {phase}")

        return {
            "session_id": self.session_id,
            "workflow_type": self.workflow_type,
            "phase": phase,
            "task_number": task_number,
            "task_content": result.chunks,
            "source": "rag",
        }

    def _load_task_from_file(
        self,
        phase: int,
        task_number: int,
        task_file: str,
        task_metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Load task content from a file specified in metadata.

        Args:
            phase: Phase number
            task_number: Task number
            task_file: Relative path to task file from workflow directory
            task_metadata: Task metadata from metadata.json

        Returns:
            Task content loaded from file

        Raises:
            WorkflowSessionError: If file not found or cannot be read
        """
        workflow_dir = self.workflows_base_path / self.workflow_type
        task_path = workflow_dir / "phases" / str(phase) / task_file

        try:
            if not task_path.exists():
                raise WorkflowSessionError(f"Task file not found: {task_path}")

            content = task_path.read_text()

            return {
                "session_id": self.session_id,
                "workflow_type": self.workflow_type,
                "phase": phase,
                "task_number": task_number,
                "task_name": task_metadata.get("name", f"Task {task_number}"),
                "task_file": task_file,
                "content": content,
                "purpose": task_metadata.get("purpose", ""),
                "source": "metadata_file",
                "steps": [],  # Could parse steps from content if needed
            }
        except Exception as e:
            raise WorkflowSessionError(
                f"Failed to load task file {task_path}: {e}"
            ) from e

    def complete_phase(self, phase: int, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete phase with validation.

        Args:
            phase: Phase number being completed
            evidence: Evidence dictionary for checkpoint validation

        Returns:
            Dictionary with completion status and next phase content

        Raises:
            WorkflowSessionError: If completion fails
        """
        # Validate phase is current
        if phase != self.state.current_phase:
            raise WorkflowSessionError(
                f"Cannot complete phase {phase}. "
                f"Current phase is {self.state.current_phase}."
            )

        # Create phase artifact
        artifact = PhaseArtifact(
            phase_number=phase,
            evidence=evidence,
            outputs={},
            commands_executed=[],
            timestamp=datetime.now(),
        )

        # Validate checkpoint with evidence (multi-layer validation)
        checkpoint_passed, validation_result = self.engine.validate_checkpoint(
            self.state.workflow_type, phase, evidence, session_id=self.session_id
        )

        # Complete phase (this advances state)
        self.state.complete_phase(
            phase=phase,
            artifact=artifact,
            checkpoint_passed=checkpoint_passed,
        )

        # Persist updated state
        self.state_manager.save_state(self.state)

        logger.info(
            "Session %s: Completed phase %s, advanced to phase %s",
            self.session_id,
            phase,
            self.state.current_phase,
        )

        # Get next phase content if workflow not complete
        if not self.state.is_complete():
            next_phase_content = self.get_current_phase()

            return {
                "checkpoint_passed": checkpoint_passed,
                "validation_result": validation_result,
                "phase_completed": phase,
                "next_phase": self.state.current_phase,
                "next_phase_content": next_phase_content,
                "workflow_complete": False,
            }

        return {
            "checkpoint_passed": checkpoint_passed,
            "validation_result": validation_result,
            "phase_completed": phase,
            "workflow_complete": True,
            "message": "Workflow complete! All phases finished.",
        }

    def cleanup(self) -> None:
        """
        Clean up session resources.

        Called when workflow completes or session terminates.
        Frees memory by clearing caches and registries.
        """
        # Clear dynamic registry if present
        if self.dynamic_registry:
            # Registry will be garbage collected
            self.dynamic_registry = None
            logger.info("Session %s: Cleaned up dynamic registry", self.session_id)

        logger.info("Session %s: Cleanup complete", self.session_id)

    def get_state(self) -> WorkflowState:
        """
        Get current workflow state.

        Returns:
            Current workflow state
        """
        return self.state


__all__ = [
    "WorkflowSessionError",
    "WorkflowSession",
]
