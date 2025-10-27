            n_results: Number of results to return (default: 5)
            filters: Optional metadata filters:
                - phase: int (phase number to filter by)
                - tags: List[str] (tags to filter by)
                - framework: str (framework type to filter by)
                - is_critical: bool (only critical content)

        Returns:
            SearchResult with chunks, metadata, and metrics

        Example:
            # Get Phase 1 requirements
            result = engine.search(
                "Phase 1 method verification requirements",
                n_results=5,
                filters={"phase": 1}
            )
        """
        # Wait if rebuild in progress (timeout: 30s)
        if self._rebuilding.is_set():
            logger.debug("Waiting for index rebuild to complete...")
            if not self._rebuilding.wait(timeout=30):
                logger.warning("Rebuild timeout, proceeding with current index")

        start_time = time.time()

        # Check cache
        cache_key = self._generate_cache_key(query, n_results, filters)
        cached_result = self._check_cache(cache_key)
        if cached_result:
            logger.debug("Cache hit for query: %s...", query[:50])
            return cached_result

        # Acquire read lock for safe concurrent access during index queries
        with self._lock:
            # Try vector search
            if self.vector_search_available:
                try:
                    result = self._vector_search(query, n_results, filters)
                    elapsed_ms = (time.time() - start_time) * 1000
                    result.query_time_ms = elapsed_ms

                    # Cache result
                    self._cache_result(cache_key, result)

                    logger.info(
                        "Vector search completed: %s chunks in %.1fms",
                        len(result.chunks),
                        elapsed_ms,
                    )
                    return result

                except Exception as e:
                    logger.error("Vector search failed: %s", e, exc_info=True)
                    logger.info("Falling back to grep search")

            # Grep fallback
            result = self._grep_fallback(query, n_results)
            elapsed_ms = (time.time() - start_time) * 1000
            result.query_time_ms = elapsed_ms

            logger.info(
                "Grep search completed: %s chunks in %.1fms",
                len(result.chunks),
                elapsed_ms,
            )
            return result

    def _vector_search(
        self, query: str, n_results: int, filters: Optional[Dict]
    ) -> SearchResult:
        """
        Perform vector similarity search with LanceDB.

        Args:
            query: Search query
            n_results: Number of results
            filters: Metadata filters

        Returns:
            SearchResult with vector-retrieved chunks
        """
        # Generate query embedding
        query_embedding = self._generate_embedding(query)

        # Build LanceDB query - table is guaranteed to be available here
        if self.table is None:
            raise RuntimeError("LanceDB table not available for vector search")
        search_query = self.table.search(query_embedding).limit(n_results * 2)

        # Apply filters using WHERE clauses (LanceDB's killer feature!)
        if filters:
            where_conditions = []

            if "phase" in filters:
                where_conditions.append(f"phase = {filters['phase']}")

            if "is_critical" in filters:
                where_conditions.append(f"is_critical = {filters['is_critical']}")

            if "framework" in filters:
                where_conditions.append(f"framework_type = '{filters['framework']}'")

            if "tags" in filters:
                # Tags are JSON array, need to check if any match
                for tag in filters["tags"]:
                    where_conditions.append(f"tags LIKE '%{tag}%'")

            # Combine conditions with AND
            if where_conditions:
                where_clause = " AND ".join(where_conditions)
                search_query = search_query.where(where_clause)

        # Execute search
        results = search_query.to_list()

        # Convert to chunks format
        chunks = []
        scores = []
        total_tokens = 0

        for result in results[:n_results]:
            # Parse JSON fields
            try:
                parent_headers = json.loads(result.get("parent_headers", "[]"))
                tags = json.loads(result.get("tags", "[]"))
            except (json.JSONDecodeError, TypeError, KeyError) as e:
                logger.debug("Failed to parse metadata fields: %s", e)
                parent_headers = []
                tags = []

            chunk = {
                "content": result["content"],
                "file_path": result["file_path"],
                "section_header": result["section_header"],
                "parent_headers": parent_headers,
                "token_count": result["token_count"],
                "phase": result["phase"],
                "framework_type": result["framework_type"],
                "category": result.get("category", ""),
                "is_critical": result["is_critical"],
                "tags": tags,
            }

            chunks.append(chunk)
            scores.append(result.get("_distance", 0.0))  # LanceDB returns distance
            total_tokens += result["token_count"]

        return SearchResult(
            chunks=chunks,
            total_tokens=total_tokens,
            retrieval_method="vector",
            query_time_ms=0.0,  # Set by caller
            relevance_scores=scores,
            cache_hit=False,
        )

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for query text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        if self.embedding_provider == "local":
            if self.local_model is None:
                raise RuntimeError("Local embedding model not initialized")
            embedding = self.local_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()

        if self.embedding_provider == "openai":
            import openai

            response = openai.embeddings.create(model=self.embedding_model, input=text)
            return response.data[0].embedding

        raise ValueError(f"Unknown embedding provider: {self.embedding_provider}")

    def _grep_fallback(self, query: str, n_results: int) -> SearchResult:
        """
        Fallback to grep-based search when vector search unavailable.

        Args:
            query: Search query
            n_results: Number of results

        Returns:
            SearchResult with grep-retrieved chunks
        """
        logger.info("Using grep fallback for query: %s...", query[:50])

        try:
            # Extract search terms (simple word splitting)
            search_terms = query.lower().split()

            # Run grep for each term
            chunks = []
            seen_files = set()

            for term in search_terms[:3]:  # Limit to 3 most important terms
                result = subprocess.run(
                    [
                        "grep",
                        "-r",
                        "-i",
                        "-l",  # Files with matches
                        "-m",
                        "1",  # Stop after first match per file
                        term,
                        str(self.standards_path),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )

                # Parse matched files
                for line in result.stdout.splitlines():
                    if line and line not in seen_files:
                        seen_files.add(line)

                        # Read file content (up to first 1000 chars)
                        try:
                            content = Path(line).read_text(encoding="utf-8")[:1000]
                            chunks.append(
                                {
                                    "content": content,
                                    "file_path": line,
                                    "section_header": "Grep Match",
                                    "token_count": len(content.split()),
                                }
                            )
                        except Exception as e:
                            logger.debug("Could not read %s: %s", line, e)

                    if len(chunks) >= n_results:
                        break

                if len(chunks) >= n_results:
                    break

            total_tokens = sum(c["token_count"] for c in chunks)

            return SearchResult(
                chunks=chunks[:n_results],
                total_tokens=total_tokens,
                retrieval_method="grep_fallback",
                query_time_ms=0.0,
                relevance_scores=[1.0] * len(chunks),
                cache_hit=False,
            )

        except Exception as e:
            logger.error("Grep fallback failed: %s", e)
            return SearchResult(
                chunks=[],
                total_tokens=0,
                retrieval_method="grep_fallback",
                query_time_ms=0.0,
                relevance_scores=[],
                cache_hit=False,
            )

    def _generate_cache_key(
        self, query: str, n_results: int, filters: Optional[Dict]
    ) -> str:
        """Generate cache key from query parameters.

        Creates MD5 hash of query, n_results, and filters for cache lookup.

        :param query: Search query text
        :type query: str
        :param n_results: Number of results requested
        :type n_results: int
        :param filters: Optional metadata filters
        :type filters: Optional[Dict]
        :return: MD5 hash as cache key
        :rtype: str
        """
        key_data = f"{query}:{n_results}:{json.dumps(filters, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _check_cache(self, cache_key: str) -> Optional[SearchResult]:
        """Check if cached result exists and is fresh.

        Returns cached result if found and not expired, otherwise None.

        :param cache_key: Cache key to look up
        :type cache_key: str
        :return: Cached search result if fresh, None otherwise
        :rtype: Optional[SearchResult]
        """
        if cache_key not in self._query_cache:
            return None

        result, timestamp = self._query_cache[cache_key]

        # Check if expired
        if time.time() - timestamp > self.cache_ttl_seconds:
            del self._query_cache[cache_key]
            return None

        # Return cached result with cache_hit flag
        result.cache_hit = True
        return result

    def _cache_result(self, cache_key: str, result: SearchResult) -> None:
        """Cache search result with timestamp.

        Stores result in cache and triggers cleanup if cache grows too large.

        :param cache_key: Cache key for storage
        :type cache_key: str
        :param result: Search result to cache
        :type result: SearchResult
        """
        self._query_cache[cache_key] = (result, time.time())

        # Clean old cache entries if cache is large
        if len(self._query_cache) > 100:
            self._clean_cache()

    def _clean_cache(self) -> None:
        """Remove expired cache entries.

        Iterates through cache and deletes entries that have exceeded
        the TTL threshold.
        """
        current_time = time.time()
        expired_keys = [
            key
            for key, (_, timestamp) in self._query_cache.items()
            if current_time - timestamp > self.cache_ttl_seconds
        ]
        for key in expired_keys:
            del self._query_cache[key]

    def health_check(self) -> Dict[str, Any]:
        """
        Check RAG engine health status.

        Returns:
            Health status dictionary
        """
        health = {
            "vector_search_available": self.vector_search_available,
            "index_path": str(self.index_path),
            "standards_path": str(self.standards_path),
            "cache_size": len(self._query_cache),
            "embedding_provider": self.embedding_provider,
        }

        if self.vector_search_available:
            try:
                if self.table is not None:
                    health["chunk_count"] = self.table.count_rows()
                    health["status"] = "healthy"
                else:
                    health["status"] = "degraded"
                    health["error"] = "Table not initialized"
            except Exception as e:
                health["status"] = "degraded"
                health["error"] = str(e)
        else:
            health["status"] = "grep_only"

        return health

    def reload_index(self) -> None:
        """Reload LanceDB index for hot reload after rebuild.

        Reconnects to LanceDB and reopens the table after index rebuild.
        Clears query cache to ensure fresh results. Unlike ChromaDB, LanceDB
        has no singleton conflicts making hot reload clean and simple.

        **Thread Safety:**

        Uses write lock to prevent concurrent queries during reload. Blocks
        all search operations until reload completes. Sets `_rebuilding` event
        to signal queries to wait.

        **Example:**

        .. code-block:: python

            # After editing prAxIs OS content
            rag_engine.reload_index()  # Picks up new content immediately

        **Note:**

        This is typically called automatically by the file watcher when
        prAxIs OS content changes are detected.
        """
        # Acquire write lock to block all reads during reload
        with self._lock:
            self._rebuilding.set()  # Signal rebuild in progress
            try:
                logger.info("Reloading LanceDB index...")

                # Close old connections cleanly
                if hasattr(self, "table"):
                    del self.table
                if hasattr(self, "db"):
                    del self.db

                # Reconnect to index
                self.db = lancedb.connect(str(self.index_path))
                self.table = self.db.open_table("praxis_os_standards")
                chunk_count = self.table.count_rows()
                logger.info("Index reloaded: %s chunks", chunk_count)
                self.vector_search_available = True

                # Clear cache after reload
                self._query_cache.clear()

            except Exception as e:
                logger.error("Failed to reload index: %s", e)
                self.vector_search_available = False
            finally:
                self._rebuilding.clear()  # Signal rebuild complete

<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
universal/standards/ai-assistant/rag-content-authoring.md
universal/standards/ai-assistant/MCP-TOOLS-GUIDE.md

# Current Time
10/10/2025, 9:21:59 PM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
23,485 / 200K tokens used (12%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<read_file>
<path>mcp_server/workflow_engine.py</path>
<task_progress>
- [x] Orient with prAxIs OS standards (MCP not available, proceeding with direct analysis)
- [x] Examine project structure and purpose
- [x] Analyze key components and architecture (RAG engine completed)
- [ ] Review documentation and standards
- [ ] Identify MCP tools and workflows
- [ ] Summarize findings
</task_progress>
</read_file>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[read_file for 'mcp_server/workflow_engine.py'] Result:
"""
Workflow Engine for Phase Gating and Checkpoint Validation.

Enforces architectural constraints for sequential workflow execution.
100% AI-authored via human orchestration.
"""

# pylint: disable=too-many-lines
# Justification: WorkflowEngine is the core orchestration component with
# phase gating, checkpoints, validation, content rendering, and session management
# (1270 lines). Splitting would fragment cohesive workflow logic.

# pylint: disable=broad-exception-caught
# Justification: Workflow engine must be robust - catches broad exceptions
# to provide graceful degradation and detailed error messages for AI agents

# pylint: disable=protected-access
# Justification: Engine needs to check _is_dynamic attribute from session
# registry to determine content rendering strategy (static vs dynamic)

# pylint: disable=unused-argument
# Justification: _extract_validator has context parameter reserved for future
# context-aware validation logic (currently only analyzes line content)

import json
import logging
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .core.session import WorkflowSession
from .models import (
    CommandExecution,
    PhaseMetadata,
    WorkflowMetadata,
    WorkflowState,
)
from .rag_engine import RAGEngine
from .state_manager import StateManager

logger = logging.getLogger(__name__)


class CheckpointLoader:
    """
    Load checkpoint requirements dynamically from prAxIs OS standards.

    Aligns with project principle: dynamic logic over static patterns.
    Single source of truth: prAxIs OS docs define checkpoints, not code.
    """

    def __init__(self, rag_engine: RAGEngine):
        """
        Initialize checkpoint loader.

        Args:
            rag_engine: RAG engine for querying prAxIs OS docs
        """
        self.rag_engine = rag_engine
        self._checkpoint_cache: Dict[str, Dict] = {}

    def load_checkpoint_requirements(
        self, workflow_type: str, phase: int
    ) -> Dict[str, Any]:
        """
        Load checkpoint requirements from prAxIs OS documents dynamically.

        Args:
            workflow_type: Workflow type (e.g., "test_generation_v3")
            phase: Phase number

        Returns:
            Dictionary with required evidence fields and validators
        """
        cache_key = f"{workflow_type}_phase_{phase}"

        if cache_key in self._checkpoint_cache:
            logger.debug("Cache hit for %s", cache_key)
            return self._checkpoint_cache[cache_key]

        # Query RAG for checkpoint section of this phase
        query = f"{workflow_type} Phase {phase} checkpoint requirements evidence"

        try:
            result = self.rag_engine.search(
                query=query, n_results=3, filters={"phase": phase}
            )

            # Parse checkpoint requirements from retrieved content
            requirements = self._parse_checkpoint_requirements(result.chunks)

            # Cache for performance
            self._checkpoint_cache[cache_key] = requirements

            logger.info(
                "Loaded checkpoint requirements for %s Phase %s", workflow_type, phase
            )

            return requirements

        except Exception as e:
            logger.error("Failed to load checkpoint requirements: %s", e)
            # Return minimal fallback requirements
            return {"required_evidence": {}}

    def _parse_checkpoint_requirements(
        self, chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Parse checkpoint requirements from document chunks dynamically.

        Analyzes document structure to extract:
        - Required evidence fields
        - Field types (inferred from examples)
        - Validation rules (extracted from requirements language)

        Args:
            chunks: Document chunks from RAG search

        Returns:
            Dictionary with parsed requirements
        """
        requirements = {}

        for chunk in chunks:
            content = chunk.get("content", "")
            lines = content.split("\n")

            for i, line in enumerate(lines):
                # Detect evidence requirement patterns dynamically
                if self._is_evidence_requirement(line):
                    field_name = self._extract_field_name(line)
                    if field_name and field_name != "unknown_field":
                        context_lines = (
                            lines[i : i + 3] if i + 3 < len(lines) else lines[i:]
                        )
                        field_type = self._infer_field_type(line, context_lines)
                        validator = self._extract_validator(line, context_lines)

                        requirements[field_name] = {
                            "type": field_type,
                            "validator": validator,
                            "description": self._extract_description(line),
                        }

        return {"required_evidence": requirements}

    def _is_evidence_requirement(self, line: str) -> bool:
        """Detect if line describes an evidence requirement.

        Analyzes line for requirement indicator keywords like "must provide",
        "required:", "evidence:", etc.

        :param line: Line from document to analyze
        :type line: str
        :return: True if line describes evidence requirement
        :rtype: bool
        """
        # Look for requirement indicators in line structure
        indicators = [
            "must provide",
            "required:",
            "evidence:",
            "checkpoint:",
            "verify that",
            "proof of",
        ]
        line_lower = line.lower()
        return any(ind in line_lower for ind in indicators)

    def _extract_field_name(self, line: str) -> str:
        """Extract field name from requirement line.

        Looks for field names in common formats like `field_name` or
        **field_name** or snake_case words.

        :param line: Line with potential field name
        :type line: str
        :return: Extracted field name or "unknown_field" if not found
        :rtype: str
        """
        # Look for field name patterns (typically in code formatting or bold)
        words = line.split()
        for word in words:
            # Field names often in code format: `field_name`
            if word.startswith("`") and word.endswith("`"):
                return word.strip("`")
            # Or emphasized: **field_name**
            if word.startswith("**") and word.endswith("**"):
                return word.strip("*").lower().replace(" ", "_")

        # Fallback: first snake_case word
        for word in words:
            if "_" in word and word.replace("_", "").replace("-", "").isalnum():
                return word.strip(":`\"'")

        return "unknown_field"

    def _infer_field_type(self, line: str, context: List[str]) -> type:
        """Infer field type from context and examples.

        Analyzes keywords and context to determine if field should be
        int, str, list, bool, or dict. Defaults to str if unclear.

        :param line: Line with field definition
        :type line: str
        :param context: Surrounding lines for additional context
        :type context: List[str]
        :return: Inferred type (int, str, list, bool, or dict)
        :rtype: type
        """
        line_lower = line.lower()
        context_text = " ".join(context).lower()

        # Look for type hints in context
        if any(
            word in line_lower
            for word in ["count", "number", "quantity", "total", "sum"]
        ):
            return int
        if any(
            word in line_lower or word in context_text
            for word in ["list", "array", "collection", "functions", "methods"]
        ):
            return list
        if any(word in line_lower for word in ["flag", "boolean", "true/false"]):
            return bool
        if any(word in line_lower for word in ["dict", "mapping", "object"]):
            return dict
        if any(
            word in line_lower for word in ["output", "text", "command", "path", "file"]
        ):
            return str

        # Default to string
        return str

    def _extract_validator(
        self, line: str, context: List[str]
    ) -> Callable:  # pylint: disable=unused-argument
        """Extract validation logic from requirement description.

        Analyzes requirement language to create appropriate validator function.
        Handles patterns like "greater than", "non-empty", "optional", etc.

        :param line: Line with validation requirements
        :type line: str
        :param context: Surrounding lines for context
        :type context: List[str]
        :return: Validation function that returns True if valid
        :rtype: Callable
        """
        line_lower = line.lower()

        # Analyze requirement language for validation rules
        if any(
            phrase in line_lower
            for phrase in ["greater than", "at least", "non-zero", "minimum"]
        ):
            return lambda x: (x > 0 if isinstance(x, int) else len(x) > 0)

        if any(
            phrase in line_lower
            for phrase in ["non-empty", "must contain", "cannot be empty"]
        ):
            return lambda x: len(x) > 0 if hasattr(x, "__len__") else x is not None

        if "optional" in line_lower or "may be empty" in line_lower:
            return lambda x: True

        # Default: must exist and not be None
        return lambda x: x is not None

    def _extract_description(self, line: str) -> str:
        """Extract human-readable description from line.

        Removes formatting characters (*, #, -, :, `, ") and returns
        clean description text.

        :param line: Line with description and formatting
        :type line: str
        :return: Cleaned description text
        :rtype: str
        """
        # Remove formatting and extract description text
        cleaned = line.strip('*#-:`"')
        return cleaned.strip()


# ============================================================================
# Workflow Task Management Guidance
# ============================================================================

WORKFLOW_GUIDANCE_FIELDS = {
    "⚠️_WORKFLOW_EXECUTION_MODE": "ACTIVE",
    "🛑_DO_NOT_USE_EXTERNAL_TASK_TOOLS": (
        "This workflow manages ALL tasks. DO NOT use todo_write or "
        "external task lists. The workflow IS your task tracker."
    ),
    "execution_model": "Complete task → Submit evidence → Advance phase",
}


def add_workflow_guidance(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inject task management guidance into workflow tool response.

    This decorator adds explicit guidance fields to inform AI assistants
    that the workflow system manages task state and external task tools
    (like todo_write) should not be used.

    Args:
        response: Base response dict from workflow engine

    Returns:
        Response dict with injected guidance fields (guidance fields first)

    Example:
        >>> base = {"session_id": "123", "phase": 1}
        >>> wrapped = add_workflow_guidance(base)
        >>> "⚠️_WORKFLOW_EXECUTION_MODE" in wrapped
        True
        >>> wrapped["⚠️_WORKFLOW_EXECUTION_MODE"]
        'ACTIVE'

    Note:
        - Gracefully handles non-dict inputs (returns unchanged)
        - Never raises exceptions (fail-safe design)
        - Original response fields preserved (non-invasive)
    """
    # Input validation: only process dict responses
    if not isinstance(response, dict):
        logger.debug(
            "Skipping guidance injection for non-dict response: %s",
            type(response).__name__,
        )
        return response

    try:
        # Prepend guidance fields (dict unpacking ensures guidance appears first)
        return {**WORKFLOW_GUIDANCE_FIELDS, **response}
    except Exception as e:
        # Fail-safe: return original response if injection fails
        logger.warning(
            "Failed to inject workflow guidance: %s. Returning original response.", e
        )
        return response


class WorkflowEngine:
    """
    Workflow engine with architectural phase gating.

    Features:
    - Phase gating: Can only access current phase
    - Checkpoint validation: Evidence required to advance
    - State persistence: Resume workflows
    - Error handling: Clear feedback on violations
    """

    def __init__(
        self,
        state_manager: StateManager,
        rag_engine: RAGEngine,
        checkpoint_loader: Optional[CheckpointLoader] = None,
        workflows_base_path: Optional[Path] = None,
    ):
        """
        Initialize workflow engine.

        Args:
            state_manager: State manager for persistence
            rag_engine: RAG engine for content retrieval
            checkpoint_loader: Optional custom checkpoint loader
            workflows_base_path: Base path for workflow metadata files
        """
        self.state_manager = state_manager
        self.rag_engine = rag_engine
        self.checkpoint_loader = checkpoint_loader or CheckpointLoader(rag_engine)

        # Determine workflows base path (default to universal/workflows)
        if workflows_base_path is None:
            # Try to find workflows directory relative to this file
            current_dir = Path(__file__).parent
            self.workflows_base_path = current_dir.parent / "universal" / "workflows"
        else:
            self.workflows_base_path = workflows_base_path

        # Cache for loaded workflow metadata
        self._metadata_cache: Dict[str, WorkflowMetadata] = {}

        # Session cache for session-scoped workflow execution
        self._sessions: Dict[str, WorkflowSession] = {}

        logger.info("WorkflowEngine initialized")

    def load_workflow_metadata(self, workflow_type: str) -> WorkflowMetadata:
        """
        Load workflow metadata from metadata.json file.

        Provides upfront overview information including total phases, phase names,
        purposes, and expected outputs. Falls back to generating metadata from
        phase discovery if metadata.json doesn't exist.

        Args:
            workflow_type: Workflow type (e.g., "test_generation_v3")

        Returns:
            WorkflowMetadata with complete workflow overview
        """
        # Check cache first
        if workflow_type in self._metadata_cache:
            logger.debug("Workflow metadata cache hit for %s", workflow_type)
            return self._metadata_cache[workflow_type]

        # Try to load from metadata.json
        metadata_path = self.workflows_base_path / workflow_type / "metadata.json"

        if metadata_path.exists():
            logger.info("Loading workflow metadata from %s", metadata_path)
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata_dict = json.load(f)
                metadata = WorkflowMetadata.from_dict(metadata_dict)

                # Cache the metadata
                self._metadata_cache[workflow_type] = metadata

                logger.info(
                    "Loaded metadata for %s: %s phases, %s phase definitions",
                    workflow_type,
                    metadata.total_phases,
                    len(metadata.phases),
                )
                return metadata
            except Exception as e:
                logger.warning(
                    "Failed to load metadata.json for %s: %s. "
                    "Falling back to generated metadata.",
                    workflow_type,
                    e,
                )

        # Fallback: Generate metadata from known workflow types
        logger.info("Generating fallback metadata for %s", workflow_type)
        metadata = self._generate_fallback_metadata(workflow_type)

        # Cache the generated metadata
        self._metadata_cache[workflow_type] = metadata

        return metadata

    def _generate_fallback_metadata(self, workflow_type: str) -> WorkflowMetadata:
        """
        Generate fallback metadata for workflows without metadata.json.

        Uses hardcoded knowledge of standard workflow structures for backward
        compatibility. This ensures existing workflows continue to work.

        Args:
            workflow_type: Workflow type

        Returns:
            Generated WorkflowMetadata
        """
        # Known workflow structures
        if "test" in workflow_type.lower():
            # Test generation workflow (8 phases)
            return WorkflowMetadata(
                workflow_type=workflow_type,
                version="unknown",
                description="Test generation workflow (auto-generated metadata)",
                total_phases=8,
                estimated_duration="2-3 hours",
                primary_outputs=["test files", "coverage report"],
                phases=[
                    PhaseMetadata(
                        phase_number=i,
                        phase_name=f"Phase {i}",
                        purpose=f"Phase {i} tasks",
                        estimated_effort="Variable",
                        key_deliverables=[],
                        validation_criteria=[],
                    )
                    for i in range(0, 8)
                ],
            )

        # Production code workflow (6 phases)
        return WorkflowMetadata(
            workflow_type=workflow_type,
            version="unknown",
            description="Production code workflow (auto-generated metadata)",
            total_phases=6,
            estimated_duration="1-2 hours",
            primary_outputs=["production code", "documentation"],
            phases=[
                PhaseMetadata(
                    phase_number=i,
                    phase_name=f"Phase {i}",
                    purpose=f"Phase {i} tasks",
                    estimated_effort="Variable",
                    key_deliverables=[],
                    validation_criteria=[],
                )
                for i in range(0, 6)
            ],
        )

    def get_session(self, session_id: str) -> WorkflowSession:
        """
        Get or create WorkflowSession instance.

        Implements session factory pattern - caches sessions for performance
        and initializes dynamic content registry if applicable.

        Args:
            session_id: Session identifier

        Returns:
            WorkflowSession instance

        Raises:
            ValueError: If session not found in state manager
        """
        # Check cache first
        if session_id in self._sessions:
            logger.debug("Session cache hit for %s", session_id)
            return self._sessions[session_id]

        # Load state from persistence
        state = self.state_manager.load_state(session_id)
