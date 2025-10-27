        if state is None:
            raise ValueError(f"Session {session_id} not found")

        # Load metadata for this workflow type
        metadata = self.load_workflow_metadata(state.workflow_type)

        # Create session with all dependencies
        session = WorkflowSession(
            session_id=session_id,
            workflow_type=state.workflow_type,
            target_file=state.target_file,
            state=state,
            rag_engine=self.rag_engine,
            state_manager=self.state_manager,
            workflows_base_path=self.workflows_base_path,
            metadata=metadata,
            options=state.metadata,  # Pass session metadata as options
        )

        # Cache session
        self._sessions[session_id] = session

        logger.info(
            "Created session %s for workflow %s (dynamic=%s)",
            session_id,
            state.workflow_type,
            session._is_dynamic(),
        )

        return session

    def start_workflow(
        self, workflow_type: str, target_file: str, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Start new workflow session with phase gating.

        Now creates WorkflowSession immediately for session-scoped execution.
        Initializes dynamic content registry if workflow is dynamic.

        Args:
            workflow_type: Workflow type (e.g., "test_generation_v3")
            target_file: File being worked on
            metadata: Optional additional metadata (may include spec_path
                for dynamic workflows)

        Returns:
            Dictionary with session info, workflow overview, and Phase 0 content
        """
        # Load workflow metadata for overview
        workflow_metadata = self.load_workflow_metadata(workflow_type)

        # Check for existing active session
        existing = self.state_manager.get_active_session(workflow_type, target_file)
        if existing:
            logger.info(
                "Resuming existing session %s for %s", existing.session_id, target_file
            )
            # Get or create session instance
            session = self.get_session(existing.session_id)
            # Delegate to session
            response = session.get_current_phase()
            # Add workflow overview to resumed session
            response["workflow_overview"] = workflow_metadata.to_dict()
            return add_workflow_guidance(response)

        # Create new session state (state_manager detects starting phase dynamically)
        state = self.state_manager.create_session(workflow_type, target_file, metadata)

        logger.info(
            "Started workflow %s session %s for %s at Phase %s",
            workflow_type,
            state.session_id,
            target_file,
            state.current_phase,
        )

        # Create session instance immediately (handles dynamic registry initialization)
        session = WorkflowSession(
            session_id=state.session_id,
            workflow_type=workflow_type,
            target_file=target_file,
            state=state,
            rag_engine=self.rag_engine,
            state_manager=self.state_manager,
            workflows_base_path=self.workflows_base_path,
            metadata=workflow_metadata,
            options=metadata,
        )

        # Cache session
        self._sessions[state.session_id] = session

        logger.info(
            "Created session instance %s (dynamic=%s)",
            state.session_id,
            session._is_dynamic(),
        )

        # Return initial phase content (delegates to session)
        response = session.get_current_phase()
        response["workflow_overview"] = workflow_metadata.to_dict()

        return add_workflow_guidance(response)

    def get_current_phase(self, session_id: str) -> Dict[str, Any]:
        """
        Get current phase content for session.

        Now delegates to WorkflowSession for dynamic content support.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with current phase content

        Raises:
            ValueError: If session not found
        """
        # Get or create session instance
        session = self.get_session(session_id)

        # Delegate to session (handles dynamic registry if applicable)
        return add_workflow_guidance(session.get_current_phase())

    def get_phase_content(
        self, session_id: str, requested_phase: int
    ) -> Dict[str, Any]:
        """
        Get content for requested phase with gating enforcement.

        Args:
            session_id: Session identifier
            requested_phase: Phase number requested

        Returns:
            Phase content if allowed, error with current phase if denied
        """
        state = self.state_manager.load_state(session_id)
        if state is None:
            raise ValueError(f"Session {session_id} not found")

        # Check access permission
        if not state.can_access_phase(requested_phase):
            # Phase gating violation
            logger.warning(
                "Phase sequence violation: Session %s tried to access phase %s, "
                "current phase is %s",
                session_id,
                requested_phase,
                state.current_phase,
            )

            return {
                "error": "Phase sequence violation",
                "message": f"You must complete Phase {state.current_phase} before "
                f"accessing Phase {requested_phase}",
                "violation_type": "attempted_skip",
                "requested_phase": requested_phase,
                "current_phase": state.current_phase,
                "current_phase_content": self._get_phase_content_from_rag(
                    state.workflow_type, state.current_phase
                ),
                "phase_gating_enforced": True,
            }

        # Access allowed
        return self._format_phase_response(state, requested_phase)

    def complete_phase(
        self, session_id: str, phase: int, evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Attempt to complete phase with evidence.

        Now delegates to WorkflowSession and handles cleanup on completion.

        Args:
            session_id: Session identifier
            phase: Phase to complete
            evidence: Evidence dictionary for checkpoint validation

        Returns:
            Result with pass/fail and next phase content if passed

        Raises:
            ValueError: If session not found or phase mismatch
        """
        # Get or create session instance
        session = self.get_session(session_id)

        # Delegate to session (handles dynamic registry if applicable)
        result = session.complete_phase(phase, evidence)

        # Check if workflow is complete and cleanup session
        if result.get("workflow_complete", False):
            logger.info("Workflow complete for session %s, cleaning up", session_id)
            session.cleanup()
            # Remove from cache
            if session_id in self._sessions:
                del self._sessions[session_id]

        return add_workflow_guidance(result)

    def get_workflow_state(self, session_id: str) -> Dict[str, Any]:
        """
        Get complete workflow state.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with complete state information
        """
        state = self.state_manager.load_state(session_id)
        if state is None:
            raise ValueError(f"Session {session_id} not found")

        return add_workflow_guidance(
            {
                "session_id": state.session_id,
                "workflow_type": state.workflow_type,
                "target_file": state.target_file,
                "current_phase": state.current_phase,
                "completed_phases": state.completed_phases,
                "total_phases": 8 if "test" in state.workflow_type else 6,
                "is_complete": state.is_complete(),
                "checkpoints": {
                    phase: status.value for phase, status in state.checkpoints.items()
                },
                "created_at": state.created_at.isoformat(),
                "updated_at": state.updated_at.isoformat(),
            }
        )

    def get_task(self, session_id: str, phase: int, task_number: int) -> Dict[str, Any]:
        """
        Get full content for a specific task (horizontal scaling - one task at a time).

        Now delegates to WorkflowSession for dynamic content support.

        Args:
            session_id: Session identifier
            phase: Phase number
            task_number: Task number within the phase

        Returns:
            Dictionary with complete task content and execution steps
        """
        # Get or create session instance
        session = self.get_session(session_id)

        # Delegate to session (handles dynamic registry if applicable)
        return add_workflow_guidance(session.get_task(phase, task_number))

    def _validate_checkpoint(
        self, workflow_type: str, phase: int, evidence: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate evidence against dynamically loaded checkpoint requirements.

        Args:
            workflow_type: Workflow type
            phase: Phase number
            evidence: Evidence dictionary

        Returns:
            Tuple of (passed: bool, missing_fields: List[str])
        """
        # Load requirements dynamically from Agent OS documents
        checkpoint_def = self.checkpoint_loader.load_checkpoint_requirements(
            workflow_type, phase
        )

        requirements = checkpoint_def.get("required_evidence", {})

        # If no requirements found, pass (permissive fallback)
        if not requirements:
            logger.warning(
                "No checkpoint requirements found for %s phase %s, passing by default",
                workflow_type,
                phase,
            )
            return (True, [])

        missing = []

        for field, spec in requirements.items():
            # Check field exists
            if field not in evidence:
                missing.append(
                    f"{field} (required: {spec.get('description', 'no description')})"
                )
                continue

            # Check type
            expected_type = spec.get("type", str)
            if not isinstance(evidence[field], expected_type):
                missing.append(
                    f"{field} (wrong type: expected {expected_type.__name__}, "
                    f"got {type(evidence[field]).__name__})"
                )
                continue

            # Check validator
            try:
                validator = spec.get("validator", lambda x: x is not None)
                if not validator(evidence[field]):
                    missing.append(
                        f"{field} (validation failed: {spec.get('description', '')})"
                    )
                    continue
            except Exception as e:
                missing.append(f"{field} (validation error: {str(e)})")
                continue

        passed = len(missing) == 0
        return (passed, missing)

    def _get_phase_content_from_rag(
        self, workflow_type: str, phase: int
    ) -> Dict[str, Any]:
        """Retrieve phase overview with task metadata (no full task content).

        Args:
            workflow_type: Workflow type
            phase: Phase number

        Returns:
            Dictionary with phase overview and task metadata list
        """
        try:
            # Query 1: General phase requirements and methodology
            general_query = (
                f"{workflow_type} Phase {phase} requirements instructions methodology"
            )
            general_result = self.rag_engine.search(
                query=general_query, n_results=3, filters={"phase": phase}
            )

            # Query 2: Discover available tasks in this phase
            task_query = f"{workflow_type} Phase {phase} task list files"
            task_result = self.rag_engine.search(
                query=task_query, n_results=20, filters={"phase": phase}
            )

            # Extract task metadata (no full content)
            tasks_metadata = self._extract_task_metadata_from_chunks(
                task_result.chunks, workflow_type, phase
            )

            return {
                "phase_number": phase,
                "phase_name": f"Phase {phase}",
                "content_chunks": general_result.chunks,  # General guidance only
                "tasks": tasks_metadata,  # Metadata only: task numbers, names, files
                "total_tokens": general_result.total_tokens,
                "retrieval_method": general_result.retrieval_method,
                "message": (
                    "Use get_task(session_id, phase, task_number) "
                    "to retrieve full task content"
                ),
            }

        except Exception as e:
            logger.error("Failed to retrieve phase content: %s", e)
            return {
                "phase_number": phase,
                "phase_name": f"Phase {phase}",
                "error": str(e),
                "content_chunks": [],
                "tasks": [],
            }

    def _get_task_content_from_rag(
        self, workflow_type: str, phase: int, task_number: int
    ) -> Dict[str, Any]:
        """
        Retrieve complete content for a specific task from RAG.

        Uses targeted query to get ALL chunks for the task file to ensure completeness.

        Args:
            workflow_type: Workflow type
            phase: Phase number
            task_number: Task number

        Returns:
            Dictionary with complete task content and execution steps
        """
        try:
            # Targeted query for this specific task
            # Use task number in query to find the right task file
            task_query = (
                f"{workflow_type} Phase {phase} task {task_number} "
                f"task-{task_number}- EXECUTE-NOW commands steps"
            )

            # Request many chunks to ensure we get the COMPLETE task
            # A typical task file might be split into 3-8 chunks
            result = self.rag_engine.search(
                query=task_query,
                n_results=50,  # High number to ensure completeness
                filters={"phase": phase},
            )

            # Filter to only chunks from the specific task file
            task_file_pattern = f"task-{task_number}-"
            task_chunks = [
                chunk
                for chunk in result.chunks
                if task_file_pattern in chunk.get("file_path", "")
            ]

            if not task_chunks:
                return {
                    "phase": phase,
                    "task_number": task_number,
                    "error": f"Task {task_number} not found in Phase {phase}",
                    "content": "",
                    "steps": [],
                }

            # Get task file path from first chunk
            task_file = task_chunks[0].get("file_path", "")

            # Sort chunks by position in file (if available) to maintain order
            task_chunks.sort(key=lambda c: c.get("start_line", 0))

            # Combine ALL chunks to get complete content
            full_content = "\n\n".join(
                chunk.get("content", "") for chunk in task_chunks
            )

            # Extract task name from first chunk or filename
            task_name = task_chunks[0].get("section_header", "")
            if not task_name:
                first_line = full_content.split("\n", maxsplit=1)[0].strip("#").strip()
                task_name = first_line if first_line else f"Task {task_number}"

            # Extract execution steps from complete content
            steps = self._extract_steps_from_content(full_content)

            logger.info(
                "Retrieved complete task %s for %s Phase %s: "
                "%s chunks, %s chars, %s steps",
                task_number,
                workflow_type,
                phase,
                len(task_chunks),
                len(full_content),
                len(steps),
            )

            return {
                "phase": phase,
                "task_number": task_number,
                "task_name": task_name,
                "task_file": task_file,
                "content": full_content,  # COMPLETE task content
                "steps": steps,  # Extracted commands and decision points
                "chunks_retrieved": len(task_chunks),  # For debugging
                "total_tokens": sum(chunk.get("tokens", 0) for chunk in task_chunks),
                "retrieval_method": result.retrieval_method,
            }

        except Exception as e:
            logger.error("Failed to retrieve task %s: %s", task_number, e)
            return {
                "phase": phase,
                "task_number": task_number,
                "error": str(e),
                "content": "",
                "steps": [],
            }

    def _extract_task_metadata_from_chunks(
        self, chunks: List[Dict[str, Any]], workflow_type: str, phase: int
    ) -> List[Dict[str, Any]]:
        """
        Extract task metadata (no full content) from RAG chunks.

        Groups chunks by task file and extracts only metadata.

        Args:
            chunks: RAG search result chunks
            workflow_type: Workflow type
            phase: Phase number

        Returns:
            List of task metadata dictionaries (no full content)
        """
        # Group chunks by file to identify unique tasks
        tasks_by_file = {}

        for chunk in chunks:
            file_path = chunk.get("file_path", "")

            # Only process task files (task-1-*.md, task-2-*.md, etc.)
            if "task-" in file_path and file_path.endswith(".md"):
                if file_path not in tasks_by_file:
                    # Extract task number from filename
                    task_match = re.search(r"task-(\d+)-", file_path)
                    task_number = int(task_match.group(1)) if task_match else 0

                    # Extract task name from first chunk's header
                    task_name = chunk.get("section_header", "")
                    if not task_name:
                        content = chunk.get("content", "")
                        first_line = (
                            content.split("\n")[0].strip("#").strip() if content else ""
                        )
                        task_name = first_line if first_line else f"Task {task_number}"

                    tasks_by_file[file_path] = {
                        "task_number": task_number,
                        "task_name": task_name,
                        "task_file": file_path,
                    }

        # Sort by task number
        tasks_metadata = sorted(tasks_by_file.values(), key=lambda t: t["task_number"])

        logger.info(
            "Found %s tasks in %s Phase %s", len(tasks_metadata), workflow_type, phase
        )

        return tasks_metadata

    def _structure_tasks_from_chunks(
        self, chunks: List[Dict[str, Any]], workflow_type: str, phase: int
    ) -> List[Dict[str, Any]]:
        """
        Structure task information from RAG chunks.

        Groups chunks by task file and extracts task information.

        Args:
            chunks: RAG search result chunks
            workflow_type: Workflow type
            phase: Phase number

        Returns:
            List of structured task dictionaries
        """
        # Group chunks by file (each task file becomes a task)
        tasks_by_file = {}

        for chunk in chunks:
            file_path = chunk.get("file_path", "")

            # Only process task files (task-1-*.md, task-2-*.md, etc.)
            if "task-" in file_path and file_path.endswith(".md"):
                if file_path not in tasks_by_file:
                    tasks_by_file[file_path] = {
                        "task_file": file_path,
                        "chunks": [],
                    }
                tasks_by_file[file_path]["chunks"].append(chunk)

        # Convert to structured tasks
        tasks = []
        for task_file, task_data in sorted(tasks_by_file.items()):
            task = self._extract_task_structure(task_file, task_data["chunks"])
            if task:
                tasks.append(task)

        logger.info(
            "Structured %s tasks from %s RAG chunks for %s Phase %s",
            len(tasks),
            len(chunks),
            workflow_type,
            phase,
        )

        return tasks

    def _extract_task_structure(
        self, task_file: str, chunks: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract structured task information from RAG chunks.

        Args:
            task_file: Path to task file
            chunks: RAG chunks from this task file

        Returns:
            Structured task dictionary or None
        """
        if not chunks:
            return None

        # Extract task number from filename (task-1-name.md -> 1)
        task_match = re.search(r"task-(\d+)-", task_file)
        task_number = int(task_match.group(1)) if task_match else 0

        # Combine all chunk content
        full_content = "\n\n".join(chunk.get("content", "") for chunk in chunks)

        # Extract task name from first chunk's section header or content
        task_name = chunks[0].get("section_header", "")
        if not task_name:
            # Try to extract from first line of content
            first_line = full_content.split("\n", maxsplit=1)[0].strip("#").strip()
            task_name = first_line if first_line else f"Task {task_number}"

        # Extract commands (look for code blocks and EXECUTE-NOW markers)
        steps = self._extract_steps_from_content(full_content)

        return {
            "task_number": task_number,
            "task_name": task_name,
            "task_file": task_file,
            "content": full_content,  # Full task content for reference
            "steps": steps,  # Extracted execution steps
            "chunks": [
                {
                    "content": chunk.get("content", ""),
                    "section": chunk.get("section_header", ""),
                    "tokens": chunk.get("tokens", 0),
                }
                for chunk in chunks
            ],
        }

    def _extract_steps_from_content(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract execution steps from task content.

        Looks for command patterns like:
        - 🛑 EXECUTE-NOW
        - ```bash code blocks
        - 📊 COUNT-AND-DOCUMENT

        Args:
            content: Task content markdown

        Returns:
            List of step dictionaries
        """
        steps = []

        # Find all bash code blocks with context
        # Pattern: Finds EXECUTE-NOW markers followed by bash blocks
        execute_pattern = (
            r"🛑\s*EXECUTE-NOW[:\s]*([^\n]*)\n```(?:bash|shell)?\n(.*?)\n```"
        )

        for match in re.finditer(execute_pattern, content, re.DOTALL):
            description = match.group(1).strip() or "Execute command"
            command = match.group(2).strip()

            # Look for evidence markers after this command
            evidence = None
            after_match = content[match.end() : match.end() + 500]
            evidence_match = re.search(
                r"📊\s*COUNT-AND-DOCUMENT[:\s]*([^\n]*)", after_match
            )
            if evidence_match:
                evidence = evidence_match.group(1).strip()

            steps.append(
                {
                    "description": description,
                    "type": "execute_command",
                    "command": command,
                    "evidence_required": evidence,
                }
            )

        # Also find QUERY-AND-DECIDE sections (branching logic)
        query_pattern = r"🔍\s*QUERY-AND-DECIDE[:\s]*([^\n]*)"
        for match in re.finditer(query_pattern, content):
            steps.append(
                {
                    "description": match.group(1).strip(),
                    "type": "decision_point",
                    "requires_analysis": True,
                }
            )

        return steps

    def _format_phase_response(
        self, state: WorkflowState, phase: int
    ) -> Dict[str, Any]:
        """
        Format standard phase response.

        Args:
            state: Workflow state
            phase: Phase number

        Returns:
            Formatted response dictionary
        """
        phase_content = self._get_phase_content_from_rag(state.workflow_type, phase)

        return {
            "session_id": state.session_id,
            "workflow_type": state.workflow_type,
            "target_file": state.target_file,
            "current_phase": state.current_phase,
            "requested_phase": phase,
            "phase_content": phase_content,
            "artifacts_available": self._get_artifacts_summary(state),
            "completed_phases": state.completed_phases,
            "is_complete": state.is_complete(),
        }

    def _get_artifacts_summary(self, state: WorkflowState) -> Dict[int, Dict]:
        """
        Get summary of available artifacts from completed phases.

        Args:
            state: Workflow state

        Returns:
            Dictionary mapping phase to artifact summary
        """
        summary = {}
        for phase, artifact in state.phase_artifacts.items():
            summary[phase] = {
                "phase": artifact.phase_number,
                "evidence_fields": list(artifact.evidence.keys()),
                "outputs": artifact.outputs,
                "timestamp": artifact.timestamp.isoformat(),
            }
        return summary

    def _extract_commands_from_evidence(
        self, evidence: Dict[str, Any]
    ) -> List[CommandExecution]:
        """
        Extract command executions from evidence if present.

        Args:
            evidence: Evidence dictionary

        Returns:
            List of CommandExecution objects
        """
        commands = []

        # Look for command-related fields
        if "commands_executed" in evidence:
            cmd_data = evidence["commands_executed"]
            if isinstance(cmd_data, list):
                for cmd in cmd_data:
                    if isinstance(cmd, dict):
                        commands.append(CommandExecution.from_dict(cmd))

        return commands

<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
universal/standards/ai-assistant/rag-content-authoring.md
universal/standards/ai-assistant/MCP-TOOLS-GUIDE.md

# Current Time
10/10/2025, 9:22:08 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
28,721 / 200K tokens used (14%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<list_code_definition_names>
<path>mcp_server/server</path>
<task_progress>
- [x] Orient with Agent OS standards (MCP not available, proceeding with direct analysis)
- [x] Examine project structure and purpose
- [x] Analyze key components and architecture
- [ ] Review documentation and standards structure
- [ ] Identify MCP tools and workflows
- [ ] Summarize findings
</task_progress>
</list_code_definition_names>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[list_code_definition_names for 'mcp_server/server'] Result:
browser_manager.py
|----
│class BrowserSession:
|----
│    async def cleanup(self) -> None:
|----
│class BrowserManager:
|----
│    def __init__(self, session_timeout: int = 3600):
|----
│    async def get_session(
|----
│    async def _cleanup_stale_sessions(self) -> None:
|----
│    async def close_session(self, session_id: str) -> None:
|----
│    async def shutdown(self) -> None:
|----

factory.py
|----
│class ServerFactory:
|----
│    def __init__(self, config: ServerConfig):
|----
│    def create_server(self) -> FastMCP:
|----
│    def _ensure_directories(self) -> None:
|----
│    def _ensure_index(self) -> None:
|----
│    def _create_rag_engine(self) -> RAGEngine:
|----
│    def _create_state_manager(self) -> StateManager:
|----
│    def _create_workflow_engine(
|----
│    def _create_framework_generator(self, rag_engine: RAGEngine) -> FrameworkGenerator:
|----
│    def _create_browser_manager(self) -> BrowserManager:
|----
│    def _start_file_watchers(self, rag_engine: RAGEngine) -> None:
|----
│    def _create_mcp_server(
|----
│    async def shutdown(self, browser_manager: Optional[BrowserManager] = None) -> None:
|----


<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
universal/standards/ai-assistant/rag-content-authoring.md
universal/standards/ai-assistant/MCP-TOOLS-GUIDE.md

# Current Time
10/10/2025, 9:22:46 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
40,006 / 200K tokens used (20%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<list_files>
<path>universal/standards</path>
<recursive>false</recursive>
<task_progress>
- [x] Orient with Agent OS standards (MCP not available, proceeding with direct analysis)
- [x] Examine project structure and purpose
- [x] Analyze key components and architecture
- [ ] Review documentation and standards structure
- [ ] Identify MCP tools and workflows
- [ ] Summarize findings
</task_progress>
</list_files>

---

**User:**

[list_files for 'universal/standards'] Result:
ai-assistant/
ai-safety/
architecture/
concurrency/
database/
documentation/
failure-modes/
installation/
meta-workflow/
performance/
security/
testing/
workflows/
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
universal/standards/ai-assistant/rag-content-authoring.md
universal/standards/ai-assistant/MCP-TOOLS-GUIDE.md

# Current Time
10/10/2025, 9:23:00 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
40,635 / 200K tokens used (20%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<list_files>
<path>universal/workflows</path>
<recursive>false</recursive>
<task_progress>
- [x] Orient with Agent OS standards (MCP not available, proceeding with direct analysis)
- [x] Examine project structure and purpose
- [x] Analyze key components and architecture
- [x] Review documentation and standards structure
- [ ] Identify MCP tools and workflows
- [ ] Summarize findings
</task_progress>
</list_files>

---

**User:**

[list_files for 'universal/workflows'] Result:
agent_os_upgrade_v1/
spec_creation_v1/
spec_execution_v1/
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
universal/standards/ai-assistant/rag-content-authoring.md
universal/standards/ai-assistant/MCP-TOOLS-GUIDE.md

# Current Time
10/10/2025, 9:23:04 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
40,931 / 200K tokens used (20%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
# Agent OS Enhanced - Project Analysis

## 📋 Executive Summary

**Agent OS Enhanced** is a portable, AI-first development framework that combines universal computer science fundamentals with AI-powered semantic search (RAG) and phase-gated workflows. It's designed to be installed in any project to enhance AI agent capabilities through structured guidance, standards enforcement, and intelligent context retrieval.

## 🎯 Core Purpose

The project serves as a **portable development framework** that:
- Provides universal CS fundamentals applicable across languages
- Enables semantic search over standards via MCP RAG server
- Enforces phase-gated workflows for structured task completion
- Facilitates AI-human collaboration through standardized patterns
- Maintains a single source of truth for development best practices

## 🏗️ Architecture Overview

### 1. **MCP Server** (`mcp_server/`)
The heart of the system, providing tools and resources via Model Context Protocol:

**Key Components:**
- **RAG Engine** (`rag_engine.py`): LanceDB-based semantic search with:
  - Vector similarity search with metadata filtering
  - Query caching (1-hour TTL)
  - Grep fallback for robustness
  - Thread-safe hot reload support
