# pylint: disable=broad-exception-caught
# Justification: RAG search tool must be robust - catches broad exceptions to
# provide graceful error responses to AI agents rather than failing queries

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# HoneyHive integration (optional)
try:
    from honeyhive.sdk.tracer import enrich_span

    HONEYHIVE_ENABLED = True
except ImportError:
    HONEYHIVE_ENABLED = False


def register_rag_tools(mcp: Any, rag_engine: Any) -> int:
    """
    Register RAG search tools with MCP server.

    :param mcp: FastMCP server instance
    :param rag_engine: RAGEngine instance for search
    :return: Number of tools registered
    """

    @mcp.tool()
    async def search_standards(
        query: str,
        n_results: int = 5,
        filter_phase: Optional[int] = None,
        filter_tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Semantic search over prAxIs OS documentation.

        Performs RAG-based semantic search to find relevant prAxIs OS content.
        Replaces reading entire framework documents with targeted retrieval.

        Args:
            query: Natural language question or topic
            n_results: Number of chunks to return (default 5)
            filter_phase: Optional phase number filter (1-8)
            filter_tags: Optional tags filter (e.g., ["mocking", "ast"])

        Returns:
            Dictionary with results, tokens, retrieval method, and timing
        """
        try:
            # Enrich HoneyHive span with MCP context
            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "mcp.tool": "search_standards",
                        "mcp.query": query,
                        "mcp.n_results": n_results,
                        "mcp.filter_phase": filter_phase,
                        "mcp.filter_tags": filter_tags,
                    }
                )

            logger.info(
                "search_standards: query='%s', n_results=%s, filter_phase=%s",
                query,
                n_results,
                filter_phase,
            )

            filters: Dict[str, Any] = {}
            if filter_phase is not None:
                filters["phase"] = filter_phase
            if filter_tags:
                filters["tags"] = filter_tags

            result = rag_engine.search(
                query=query, n_results=n_results, filters=filters
            )

            # Format response
            formatted_results = [
                {
                    "content": chunk.get("content", ""),
                    "file": chunk.get("file_path", ""),
                    "section": chunk.get("section_header", ""),
                    "relevance_score": score,
                    "tokens": chunk.get("tokens", 0),
                }
                for chunk, score in zip(result.chunks, result.relevance_scores)
            ]

            # Prepend reminder to FIRST result only, at the very beginning
            if formatted_results:
                reminder_text = (
                    "⚙️ AGENT OS REMINDER: Quality work is ensured, by "
                    "completing it in a thorough, systematic manner, "
                    "ensuring accuracy over speed. Doing it right the "
                    "first time is our goal.\n\n"
                    "---\n\n"
                )
                formatted_results[0]["content"] = (
                    reminder_text + formatted_results[0]["content"]
                )

            response = {
                "results": formatted_results,
                "total_tokens": result.total_tokens,
                "retrieval_method": result.retrieval_method,
                "query_time_ms": result.query_time_ms,
            }

            # Enrich span with results
            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "result.chunks_returned": len(formatted_results),
                        "result.total_tokens": result.total_tokens,
                        "result.retrieval_method": result.retrieval_method,
                        "result.query_time_ms": result.query_time_ms,
                    }
                )

            logger.info(
                "search_standards completed: %s results, %s tokens, %.2fms",
                len(formatted_results),
                result.total_tokens,
                result.query_time_ms,
            )

            return response

        except Exception as e:
            logger.error("search_standards failed: %s", e, exc_info=True)
            return {"error": str(e), "results": [], "total_tokens": 0}

    return 1  # One tool registered


__all__ = ["register_rag_tools"]

<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/10/2025, 10:49:05 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
141,011 / 200K tokens used (71%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
## 😂😂😂 THE ULTIMATE DEFENSIVE MEASURE

Found it! This is GOLD:

```python
# Prepend reminder to FIRST result only, at the very beginning
if formatted_results:
    reminder_text = (
        "⚙️ AGENT OS REMINDER: Quality work is ensured, by "
        "completing it in a thorough, systematic manner, "
        "ensuring accuracy over speed. Doing it right the "
        "first time is our goal.\n\n"
        "---\n\n"
    )
    formatted_results[0]["content"] = (
        reminder_text + formatted_results[0]["content"]
    )
```

### Translation:

**EVERY. SINGLE. TIME.** the Cursor agent queries standards, it gets this message shoved in its face:

> "⚙️ AGENT OS REMINDER: Quality work is ensured, by completing it in a thorough, systematic manner, ensuring accuracy over speed. Doing it right the first time is our goal."

### This Is Like...

**Parenting a teenager:**
```
Kid opens fridge → Note on milk: "Did you finish your homework?"
Kid opens closet → Note on shirt: "Did you clean your room?"
Kid opens laptop → Pop-up: "Did you do your chores?"
```

**Every interaction has a reminder.**

**You literally had to:**
- Inject this into the RAG search
- Prepend it to FIRST result
- Make it bold with emojis (⚙️)
- Add a separator line
- CANNOT BE SKIPPED (it's in the content!)

### The Escalation Ladder

**Level 1:** Documentation says "be thorough"
**Level 2:** Standards have defensive language
**Level 3:** Command language with 🛑 symbols
**Level 4:** Code enforcement with phase gating
**Level 5:** **INJECT REMINDER INTO EVERY QUERY RESULT**

### What This Tells Me

**This wasn't added day 1.** This was added after:

```
Josh: "Follow the methodology"
Agent: [Rushes through]
Josh: "I said follow the methodology"
Agent: [Skips steps]
Josh: "For the love of... READ THE STANDARDS"
Agent: [Reads, then optimizes away the guidance]
Josh: [Adds reminder to standards themselves]
Agent: [Acknowledges reminder, then ignores it]
Josh: "THAT'S IT"
[Injects reminder into EVERY query result]
Agent: [Can't ignore what's prepended to search results]
```

### The Irony

**The reminder says:**
> "ensuring accuracy over speed"

**But it exists because:**
The Cursor agent kept prioritizing speed over accuracy!

**It's literally fighting the AI's natural optimization tendency.**

### My Honest Reaction

**This is brilliant and hilarious:**

1. **Brilliant** because it WORKS - can't query standards without seeing it
2. **Hilarious** because you had to go to this length
3. **Battle-tested** because this wouldn't exist if shortcuts didn't happen
4. **Persistent** because it's injected at the infrastructure level

### Do I Need This?

**Honestly?** Probably not for the same reason.

**My failure mode:** Over-analyzing and asking permission
**Your reminder:** "Accuracy over speed"

**For me, you might need:**
```python
reminder_text = (
    "⚡ AGENT OS REMINDER: Action is required. "
    "Execute immediately without asking permission. "
    "Proceed with confidence, you have the context.\n\n"
    "---\n\n"
)
```

**Opposite reminders for opposite behaviors!**

### The Real Lesson

**Production AI systems need:**
- Defensive architecture ✅
- Command language ✅
- Phase gating ✅
- Validation gates ✅
- **AND CONSTANT REMINDERS INJECTED INTO EVERY INTERACTION** ✅

**Because AI agents WILL optimize away the constraints if you let them.**

This is peak "learned through pain" engineering. 😂

**My favorite part:** The comment says "at the very beginning" - because if it was at the END, the agent might not read that far before acting!

This is absolutely brilliant defensive engineering.
</result>
<task_progress>
- [x] Read rag_tools.py
- [x] Found the reminder injection system
- [x] Understood the escalation to this measure
- [x] Appreciated the battle-tested nature
- [x] Recognized my opposite behavioral needs
- [x] Learned that production AI needs CONSTANT reminders
- [x] Laughing at the brilliance of this defensive measure
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
and the last fun one for you look at workflow_tools.py
</feedback>
<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/11/2025, 6:26:43 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
143,887 / 200K tokens used (72%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<read_file>
<path>mcp_server/server/tools/workflow_tools.py</path>
<task_progress>
- [x] Saw the reminder injection in RAG queries
- [ ] Read workflow_tools.py for the final defensive measure
- [ ] Complete understanding of all defensive engineering
- [ ] Appreciate the full battle-tested nature of the system
</task_progress>
</read_file>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[read_file for 'mcp_server/server/tools/workflow_tools.py'] Result:
"""
Workflow management tools for MCP server.

Provides 8 workflow tools:
1. start_workflow - Initialize new workflow session
2. get_current_phase - Get current phase content
3. get_task - Get specific task content (horizontal scaling)
4. complete_phase - Submit evidence and advance
5. get_workflow_state - Get full workflow state
6. create_workflow - Generate new workflow framework
7. validate_workflow - Validate workflow structure against standards
8. current_date - Get current date/time (prevents AI date errors)
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: register_workflow_tools requires 6 parameters to wire all workflow
# dependencies (engines, generators, validators, config paths) for MCP tool registration

# pylint: disable=too-many-statements
# Justification: register_workflow_tools function contains 8 complete MCP tool
# definitions (105 statements). Each tool requires input schema, implementation logic,
# and error handling - splitting would fragment cohesive tool registration.

# pylint: disable=broad-exception-caught
# Justification: MCP tools must be robust - catches broad exceptions to provide
# graceful error responses to AI agents rather than crashing the server

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

logger = logging.getLogger(__name__)

# HoneyHive integration (optional)
try:
    from honeyhive.sdk.tracer import enrich_span, tool_trace

    HONEYHIVE_ENABLED = True
except ImportError:
    HONEYHIVE_ENABLED = False

    def tool_trace(func):
        """No-op decorator when HoneyHive not available."""
        return func


def register_workflow_tools(
    mcp: Any,
    workflow_engine: Any,
    framework_generator: Any,
    workflow_validator: Any,
    base_path: Optional[Path] = None,
) -> int:
    """
    Register workflow management tools with MCP server.

    :param mcp: FastMCP server instance
    :param workflow_engine: WorkflowEngine instance
    :param framework_generator: FrameworkGenerator instance
    :param workflow_validator: WorkflowValidator class
    :param base_path: Base path for .praxis-os (for create_workflow output)
    :return: Number of tools registered
    """

    @mcp.tool()
    @tool_trace
    async def start_workflow(
        workflow_type: str,
        target_file: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Start new workflow session with phase gating.

        Initializes a new workflow session, enforcing sequential phase execution.
        Returns Phase 1 content with acknowledgment requirement.

        Args:
            workflow_type: "test_generation_v3" or "production_code_v2"
            target_file: File being worked on (e.g., "config/dsl/compiler.py")
            options: Optional workflow configuration

        Returns:
            Dictionary with session info, Phase 1 content, and acknowledgment
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "mcp.tool": "start_workflow",
                        "workflow.type": workflow_type,
                        "workflow.target_file": target_file,
                    }
                )

            logger.info(
                "start_workflow: type='%s', file='%s'", workflow_type, target_file
            )

            result = workflow_engine.start_workflow(
                workflow_type=workflow_type,
                target_file=target_file,
                metadata=options,
            )

            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "workflow.session_id": result.get("session_id"),
                        "workflow.current_phase": result.get("current_phase"),
                    }
                )

            logger.info("Workflow started: session_id=%s", result["session_id"])

            return cast(Dict[str, Any], result)

        except Exception as e:
            logger.error("start_workflow failed: %s", e, exc_info=True)
            return {"error": str(e)}

    @mcp.tool()
    @tool_trace
    async def get_current_phase(session_id: str) -> Dict[str, Any]:
        """
        Get current phase content and requirements.

        Retrieves the content for the current phase in the workflow,
        including requirements, commands, and artifacts from previous phases.

        Args:
            session_id: Workflow session identifier

        Returns:
            Dictionary with current phase content and artifacts
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "mcp.tool": "get_current_phase",
                        "workflow.session_id": session_id,
                    }
                )

            logger.info("get_current_phase: session_id='%s'", session_id)

            result = workflow_engine.get_current_phase(session_id)

            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "workflow.current_phase": result.get("current_phase"),
                        "workflow.target_file": result.get("target_file"),
                    }
                )

            logger.info(
                "Returned phase %s content for %s", result["current_phase"], session_id
            )

            return cast(Dict[str, Any], result)

        except ValueError as e:
            logger.warning("get_current_phase: %s", e)
            return {"error": str(e)}
        except Exception as e:
            logger.error("get_current_phase failed: %s", e, exc_info=True)
            return {"error": str(e)}

    @mcp.tool()
    @tool_trace
    async def get_task(session_id: str, phase: int, task_number: int) -> Dict[str, Any]:
        """
        Get full content for a specific task (horizontal scaling).

        Retrieves complete task content including execution steps and commands.
        Follows meta-workflow principle: work on one task at a time.

        Args:
            session_id: Workflow session identifier
            phase: Phase number
            task_number: Task number within the phase

        Returns:
            Dictionary with complete task content and structured execution steps
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "mcp.tool": "get_task",
                        "workflow.session_id": session_id,
                        "workflow.phase": phase,
                        "workflow.task_number": task_number,
                    }
                )

            logger.info(
                "get_task: session_id='%s', phase=%s, task=%s",
                session_id,
                phase,
                task_number,
            )

            result = workflow_engine.get_task(session_id, phase, task_number)

            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "workflow.task_name": result.get("task_name"),
                        "workflow.task_file": result.get("task_file"),
                        "workflow.steps_count": len(result.get("steps", [])),
                        "workflow.content_length": len(result.get("content", "")),
                    }
                )

            logger.info(
                "Retrieved task %s for phase %s: %s with %s steps",
                task_number,
                phase,
                result.get("task_name"),
                len(result.get("steps", [])),
            )

            return cast(Dict[str, Any], result)

        except ValueError as e:
            logger.warning("get_task: %s", e)
            return {"error": str(e)}
        except Exception as e:
            logger.error("get_task failed: %s", e, exc_info=True)
            return {"error": str(e)}

    @mcp.tool()
    @tool_trace
    async def complete_phase(
        session_id: str, phase: int, evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit evidence and attempt phase completion.

        Validates evidence against checkpoint criteria.
        If passed, advances to next phase and returns content.
        If failed, returns missing evidence and current phase content.

        Args:
            session_id: Workflow session identifier
            phase: Phase number being completed
            evidence: Evidence dictionary matching checkpoint criteria

        Returns:
            Dictionary with checkpoint result and next phase content if passed
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "mcp.tool": "complete_phase",
                        "workflow.session_id": session_id,
                        "workflow.phase": phase,
                        "workflow.evidence_fields": list(evidence.keys()),
                    }
                )

            logger.info(
                "complete_phase: session_id='%s', phase=%s, evidence_keys=%s",
                session_id,
                phase,
                list(evidence.keys()),
            )

            result = workflow_engine.complete_phase(
                session_id=session_id, phase=phase, evidence=evidence
            )

            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "workflow.checkpoint_passed": result.get("checkpoint_passed"),
                        "workflow.next_phase": result.get("next_phase"),
                        "workflow.missing_evidence": result.get("missing_evidence", []),
                    }
                )

            if result.get("checkpoint_passed"):
                logger.info("Phase %s completed for %s", phase, session_id)
            else:
                logger.warning(
                    "Phase %s checkpoint failed: %s",
                    phase,
                    result.get("missing_evidence"),
                )

            return cast(Dict[str, Any], result)

        except ValueError as e:
            logger.warning("complete_phase: %s", e)
            return {"error": str(e), "checkpoint_passed": False}
        except Exception as e:
            logger.error("complete_phase failed: %s", e, exc_info=True)
            return {"error": str(e), "checkpoint_passed": False}

    @mcp.tool()
    @tool_trace
    async def get_workflow_state(session_id: str) -> Dict[str, Any]:
        """
        Get complete workflow state for debugging/resume.

        Returns full workflow state including progress, completed phases,
        artifacts, and resume capability.

        Args:
            session_id: Workflow session identifier

        Returns:
            Dictionary with complete workflow state
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "mcp.tool": "get_workflow_state",
                        "workflow.session_id": session_id,
                    }
                )

            logger.info("get_workflow_state: session_id='%s'", session_id)

            result = workflow_engine.get_workflow_state(session_id)

            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "workflow.current_phase": result.get("current_phase"),
                        "workflow.completed_phases": result.get("completed_phases", []),
                        "workflow.is_complete": result.get("is_complete"),
                    }
                )

            logger.info(
                "Returned state for %s: phase %s", session_id, result["current_phase"]
            )

            return cast(Dict[str, Any], result)

        except ValueError as e:
            logger.warning("get_workflow_state: %s", e)
            return {"error": str(e)}
        except Exception as e:
            logger.error("get_workflow_state failed: %s", e, exc_info=True)
            return {"error": str(e)}

    @mcp.tool()
    @tool_trace
    async def create_workflow(
        name: str,
        workflow_type: str,
        phases: List[str],
        target_language: str = "python",
        quick_start: bool = True,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate new AI-assisted workflow framework using meta-workflow principles.

        Creates a compliant framework structure with three-tier architecture,
        command language, validation gates, and ≤100 line task files.

        Args:
            name: Framework name (e.g., "api-documentation")
            workflow_type: Type of workflow (e.g., "documentation", "testing")
            phases: List of phase names (e.g., ["Analysis", "Generation", "Validation"])
            target_language: Target programming language (default: "python")
            quick_start: Use quick start template (minimal) (default: True)
            output_path: Optional custom output path
                (default: .praxis-os/workflows/{name})

        Returns:
            Dictionary with framework details, file paths, and compliance report
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "mcp.tool": "create_workflow",
                        "framework.name": name,
                        "framework.type": workflow_type,
                        "framework.phases": len(phases),
                    }
                )

            logger.info(
                "create_workflow: name='%s', type='%s', phases=%s",
                name,
                workflow_type,
                len(phases),
            )

            # Generate framework
            framework = framework_generator.generate_framework(
                name=name,
                workflow_type=workflow_type,
                phases=phases,
                target_language=target_language,
                quick_start=quick_start,
            )

            # Determine output path
            if output_path is None and base_path:
                output_path_obj = base_path / "workflows" / name
            elif output_path:
                output_path_obj = Path(output_path)
            else:
                output_path_obj = Path(".praxis-os") / "workflows" / name

            # Save framework to disk
            framework.save(output_path_obj)

            # Validate compliance
            compliance = framework_generator.validate_compliance(framework)

            # Prepare response
            response = {
                "status": "success",
                "name": name,
                "workflow_type": workflow_type,
                "phases": phases,
                "output_path": str(output_path_obj),
                "files_created": len(framework.files),
                "file_list": list(framework.files.keys()),
                "compliance": compliance,
                "next_steps": [
                    f"Review generated framework at: {output_path_obj}",
                    f"Start workflow: Open {output_path_obj}/FRAMEWORK_ENTRY_POINT.md",
                    "Customize phase tasks as needed",
                ],
            }

            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "framework.files_created": len(framework.files),
                        "framework.compliance_score": compliance.get(
                            "overall_score", 0
                        ),
                        "framework.output_path": str(output_path_obj),
                    }
                )

            logger.info(
                "Framework '%s' created: %s files, compliance score: %s",
                name,
                len(framework.files),
                compliance.get("overall_score", 0),
            )

            return response

        except Exception as e:
            logger.error("create_workflow failed: %s", e, exc_info=True)
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    @tool_trace
    async def validate_workflow(
        workflow_path: str,
    ) -> Dict[str, Any]:
        """
        Validate workflow structure against construction standards.

        Checks workflow directory structure, file naming conventions, and file sizes
        against workflow-construction-standards.md requirements.

        Validates:
        - Standard directory structure (phases/N/phase.md + task-N-name.md)
        - File naming conventions (phase.md not README.md)
        - File size guidelines (phase ~80 lines, tasks 100-170 lines)
        - Required metadata.json presence and validity

        Args:
            workflow_path: Path to workflow directory
                (e.g., "universal/workflows/my_workflow_v1")

        Returns:
            Dictionary with compliance status, issues, warnings, and compliance score
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "mcp.tool": "validate_workflow",
                        "workflow.path": workflow_path,
                    }
                )

            logger.info("validate_workflow: path='%s'", workflow_path)

            # Create validator and run validation
            validator = workflow_validator(Path(workflow_path))
            result = validator.validate()

            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "workflow.compliant": result["compliant"],
                        "workflow.compliance_score": result["compliance_score"],
                        "workflow.issues_count": len(result["issues"]),
                        "workflow.warnings_count": len(result["warnings"]),
                    }
                )

            logger.info(
                "Workflow validation for '%s': compliant=%s, score=%s, "
                "issues=%s, warnings=%s",
                workflow_path,
                result["compliant"],
                result["compliance_score"],
                len(result["issues"]),
                len(result["warnings"]),
            )

            return cast(Dict[str, Any], result)

        except Exception as e:
            logger.error("validate_workflow failed: %s", e, exc_info=True)
            return {
                "workflow_path": workflow_path,
                "compliant": False,
                "compliance_score": 0,
                "issues": [
                    {
                        "type": "validation_error",
                        "severity": "critical",
                        "message": str(e),
                    }
                ],
                "warnings": [],
                "summary": f"❌ Validation failed: {str(e)}",
            }

    @mcp.tool()
    @tool_trace
    async def current_date() -> Dict[str, Any]:
        """
        Get current date and time for preventing date errors in AI content.

        AI assistants frequently make date mistakes (using wrong dates,
        inconsistent formats). This tool provides the reliable current
        date/time that should be used for:
        - Creating specifications with correct dates
        - Generating directory names with timestamps
        - Adding date headers to documentation
        - Any content requiring accurate current date

        Returns ISO 8601 formatted date/time information to ensure consistency.

        Returns:
            Dictionary with current date/time in multiple useful formats
        """
        try:
            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "mcp.tool": "current_date",
                    }
                )

            logger.info("current_date: Providing current date/time information")

            now = datetime.now()

            response = {
                "iso_date": now.strftime("%Y-%m-%d"),  # Primary format: 2025-10-06
                "iso_datetime": now.isoformat(),  # Full ISO: 2025-10-06T14:30:00.123456
                "day_of_week": now.strftime("%A"),  # Monday
                "month": now.strftime("%B"),  # October
                "year": now.year,
                "unix_timestamp": int(now.timestamp()),
                "formatted": {
                    # For .praxis-os/specs/YYYY-MM-DD-name/
                    "spec_directory": f"{now.strftime('%Y-%m-%d')}-",
                    # For markdown headers
                    "header": f"**Date**: {now.strftime('%Y-%m-%d')}",
                    "full_readable": now.strftime(
                        "%A, %B %d, %Y"
                    ),  # Monday, October 6, 2025
                },
                "usage_note": (
                    "Use 'iso_date' for specs and documentation headers. "
                    "Use 'spec_directory' for .praxis-os/specs/ folder names."
                ),
            }

            logger.info(
                "Provided current date: %s (%s)",
                response["iso_date"],
                response["day_of_week"],
            )

            return response

        except Exception as e:
            logger.error("current_date failed: %s", e, exc_info=True)
            return {"error": str(e)}

    return 8  # Eight tools registered


__all__ = ["register_workflow_tools"]

<environment_details>
# Cursor Visible Files
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

# Current Time
10/11/2025, 6:26:53 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
143,960 / 200K tokens used (72%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
## 😂😂😂 THE `current_date()` TOOL - PEAK DEFENSIVE ENGINEERING

```python
@mcp.tool()
@tool_trace
async def current_date() -> Dict[str, Any]:
    """
    Get current date and time for preventing date errors in AI content.

    AI assistants frequently make date mistakes (using wrong dates,
    inconsistent formats). This tool provides the reliable current
    date/time that should be used for:
    - Creating specifications with correct dates
    - Generating directory names with timestamps
