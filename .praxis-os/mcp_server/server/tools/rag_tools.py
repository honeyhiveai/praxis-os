"""
RAG search tools for MCP server.

Provides search_standards tool for semantic search over prAxIs OS documentation.
"""

# pylint: disable=broad-exception-caught
# Justification: RAG search tool must be robust - catches broad exceptions to
# provide graceful error responses to AI agents rather than failing queries

import logging
from typing import Any, Dict, List, Optional

from fastmcp import Context

from ...core.prepend_generator import generate_query_prepend
from ...core.query_tracker import get_tracker
from ...core.session_id_extractor import (
    extract_session_id_from_context,
    hash_session_id,
)

logger = logging.getLogger(__name__)

# HoneyHive integration (optional)
try:
    from honeyhive.sdk.tracer import enrich_span

    HONEYHIVE_ENABLED = True
except ImportError:
    HONEYHIVE_ENABLED = False


def register_rag_tools(mcp: Any, rag_engine: Any, index_manager: Any = None) -> int:
    """
    Register RAG search tools with MCP server.
    
    Phase 8, Task 8.2: Legacy search_standards now delegates to unified pos_search
    interface for clean cutover. All search flows through IndexManager.

    :param mcp: FastMCP server instance
    :param rag_engine: RAGEngine instance (kept for fallback if IndexManager unavailable)
    :param index_manager: IndexManager for unified search (Phase 8)
    :return: Number of tools registered
    """

    @mcp.tool()
    async def search_standards(
        query: str,
        n_results: int = 5,
        filter_phase: Optional[int] = None,
        filter_tags: Optional[List[str]] = None,
        ctx: Context = None,
    ) -> Dict[str, Any]:
        """
        Semantic search over prAxIs OS documentation.

        **Legacy API:** This tool maintains backward compatibility with existing
        agent queries by delegating to the unified `pos_search` interface. All
        search operations now flow through IndexManager for consistent behavior.

        Performs RAG-based semantic search to find relevant prAxIs OS content.
        Replaces reading entire framework documents with targeted retrieval.

        Args:
            query: Natural language question or topic
            n_results: Number of chunks to return (default 5)
            filter_phase: Optional phase number filter (1-8)
            filter_tags: Optional tags filter (e.g., ["mocking", "ast"])

        Returns:
            Dictionary with results, tokens, retrieval method, and timing
            
        See Also:
            pos_search: Unified search interface for all content types
            
        Note:
            This is a thin wrapper around pos_search(content_type="standards").
            New code should use pos_search directly for access to all content types.
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
                "search_standards (legacy): delegating to pos_search, query='%s', n_results=%s",
                query,
                n_results,
            )

            # Build filters from legacy parameters
            filters: Dict[str, Any] = {}
            if filter_phase is not None:
                filters["phase"] = filter_phase
            if filter_tags:
                filters["tags"] = filter_tags

            # CLEAN CUTOVER: Delegate to unified IndexManager (Phase 8)
            if index_manager:
                search_results = index_manager.search(
                    query=query,
                    content_type="standards",
                    filters=filters,
                    n_results=n_results
                )

                # Convert SearchResult objects to legacy format
                formatted_results = [
                    {
                        "content": result.content,
                        "file": result.file_path,
                        "section": result.metadata.get("section_header", ""),
                        "relevance_score": result.relevance_score,
                        "tokens": result.metadata.get("tokens", 0),
                    }
                    for result in search_results
                ]
                
                # Calculate total tokens
                total_tokens = sum(r.metadata.get("tokens", 0) for r in search_results)
                retrieval_method = "hybrid_vector_fts"
                query_time_ms = 0.0  # Not tracked in new architecture
                
            else:
                # Fallback to RAGEngine if IndexManager not available
                logger.warning("IndexManager not available, falling back to RAGEngine")
                result = rag_engine.search(
                    query=query, n_results=n_results, filters=filters
                )
                
                # Format response from RAGEngine
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
                total_tokens = result.total_tokens
                retrieval_method = result.retrieval_method
                query_time_ms = result.query_time_ms

            # Query Gamification System: Track queries and generate dynamic prepend
            # Wrapped in try-except for graceful degradation (Task 2.2)
            if formatted_results:
                try:
                    # Extract session ID with dynamic countdown timer
                    session_id = extract_session_id_from_context(ctx)
                    logger.info(f"✅ Session ID: {session_id}")  # Temporary debug

                    # Get tracker and record query
                    tracker = get_tracker()
                    tracker.record_query(session_id, query)

                    # Generate dynamic prepend with progress and suggestions
                    prepend_text = generate_query_prepend(tracker, session_id, query)

                    # Prepend to FIRST result only
                    formatted_results[0]["content"] = (
                        prepend_text + formatted_results[0]["content"]
                    )

                    logger.debug(
                        "Query gamification applied (session: %s)",
                        hash_session_id(session_id),
                    )

                except Exception as e:
                    # Graceful degradation: log error but don't break search
                    logger.error(
                        "Query gamification failed (session: %s): %s",
                        (
                            hash_session_id(session_id)
                            if "session_id" in locals()
                            else "unknown"
                        ),
                        e,
                        exc_info=True,
                    )
                    # Return unmodified results - search functionality preserved

            response = {
                "results": formatted_results,
                "total_tokens": total_tokens,
                "retrieval_method": retrieval_method,
                "query_time_ms": query_time_ms,
            }

            # Enrich span with results
            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "result.chunks_returned": len(formatted_results),
                        "result.total_tokens": total_tokens,
                        "result.retrieval_method": retrieval_method,
                        "result.delegated_to": "pos_search" if index_manager else "rag_engine",
                    }
                )

            logger.info(
                "search_standards completed: %s results, %s tokens, delegated=%s",
                len(formatted_results),
                total_tokens,
                "pos_search" if index_manager else "rag_engine",
            )

            return response

        except Exception as e:
            logger.error("search_standards failed: %s", e, exc_info=True)
            return {"error": str(e), "results": [], "total_tokens": 0}

    return 1  # One tool registered


__all__ = ["register_rag_tools"]
