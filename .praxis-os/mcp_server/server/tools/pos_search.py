"""
Unified search tool for prAxIs OS multi-index RAG architecture.

Phase 8, Task 8.1: Provides pos_search tool for searching across all content types
(standards, code, AST) through a single unified interface.
"""

# pylint: disable=broad-exception-caught
# Justification: Search tool must be robust - catches broad exceptions to
# provide graceful error responses to AI agents rather than failing queries

import logging
from typing import Any, Dict, List, Optional

from fastmcp import Context

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


def register_pos_search_tools(mcp: Any, index_manager: Any) -> int:
    """
    Register unified pos_search tool with MCP server.
    
    Phase 8, Task 8.1: Creates unified search interface across all content types.
    
    :param mcp: FastMCP server instance
    :param index_manager: IndexManager instance for multi-index search
    :return: Number of tools registered (1)
    
    Example:
        >>> from server.indexes import IndexManager
        >>> manager = IndexManager(base_path, config_path)
        >>> register_pos_search_tools(mcp, manager)
        1
    """

    @mcp.tool()
    async def pos_search(
        content_type: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        n_results: int = 5,
        ctx: Context = None,
    ) -> Dict[str, Any]:
        """
        Unified search across all prAxIs OS indexed content.
        
        Phase 8, Task 8.1: Single interface for searching standards, code, and AST.
        
        Searches the specified content type using appropriate indexing strategy:
        - "standards": Hybrid vector + FTS search with metadata filtering
        - "code": Semantic code search using embeddings
        - "ast": Structural code search using Tree-sitter AST
        
        Args:
            content_type: Type of content to search. Valid values:
                - "standards": prAxIs OS documentation and standards
                - "code": Source code files (semantic search)
                - "ast": Code structure (function defs, calls, classes)
            query: Natural language question or search keywords.
                For AST queries, use structural patterns like:
                - "function: calculate_total"
                - "class: StateManager"
            filters: Optional metadata filters specific to content type.
                Examples:
                - standards: {"domain": "backend", "phase": 0}
                - code: {"language": "python"}
                - ast: {"symbol_type": "function", "language": "python"}
            n_results: Number of results to return (default: 5, max: 20)
            ctx: MCP context (auto-injected)
        
        Returns:
            Dictionary with search results:
            {
                "status": "success" | "error",
                "content_type": str,
                "query": str,
                "results": [
                    {
                        "content": str,
                        "metadata": dict,
                        "relevance_score": float
                    },
                    ...
                ],
                "count": int,
                "session_id": str (hashed),
                "error": str (only if status="error")
            }
        
        Raises:
            ValueError: If content_type is unknown or n_results invalid
            RuntimeError: If search operation fails
        
        Examples:
            >>> # Search standards
            >>> result = await pos_search(
            ...     content_type="standards",
            ...     query="How do I implement authentication?",
            ...     filters={"domain": "backend"},
            ...     n_results=5
            ... )
            
            >>> # Search code
            >>> result = await pos_search(
            ...     content_type="code",
            ...     query="user authentication logic",
            ...     filters={"language": "python"},
            ...     n_results=10
            ... )
            
            >>> # Search AST
            >>> result = await pos_search(
            ...     content_type="ast",
            ...     query="function: authenticate_user",
            ...     filters={"symbol_type": "function"},
            ...     n_results=3
            ... )
        
        Note:
            This is the unified replacement for content-specific search tools.
            For backward compatibility, use search_standards() which delegates
            to this tool with content_type="standards".
        """
        try:
            # Extract session ID for tracking
            session_id = extract_session_id_from_context(ctx)
            session_id_hash = hash_session_id(session_id)
            
            # Enrich HoneyHive span with MCP context
            if HONEYHIVE_ENABLED:
                enrich_span(
                    {
                        "mcp.tool": "pos_search",
                        "mcp.content_type": content_type,
                        "mcp.query": query,
                        "mcp.n_results": n_results,
                        "mcp.filters": filters,
                        "mcp.session_id": session_id_hash,
                    }
                )
            
            logger.info(
                "pos_search: content_type='%s', query='%s', n_results=%s, filters=%s, session=%s",
                content_type,
                query,
                n_results,
                filters,
                session_id_hash[:8],
            )
            
            # Validate content_type
            valid_types = ["standards", "code", "ast"]
            if content_type not in valid_types:
                error_msg = (
                    f"Unknown content_type: '{content_type}'. "
                    f"Valid types: {', '.join(valid_types)}"
                )
                logger.error(error_msg)
                return {
                    "status": "error",
                    "content_type": content_type,
                    "query": query,
                    "error": error_msg,
                    "session_id": session_id_hash,
                }
            
            # Validate n_results
            if not isinstance(n_results, int) or n_results < 1:
                error_msg = f"n_results must be positive integer, got: {n_results}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "content_type": content_type,
                    "query": query,
                    "error": error_msg,
                    "session_id": session_id_hash,
                }
            
            # Cap n_results at 20 to prevent excessive results
            if n_results > 20:
                logger.warning(
                    "n_results=%s exceeds max (20), capping to 20",
                    n_results
                )
                n_results = 20
            
            # Delegate to IndexManager
            search_results = index_manager.search(
                query=query,
                content_type=content_type,
                filters=filters or {},
                n_results=n_results
            )
            
            # Convert SearchResult objects to dictionaries
            results_list = [
                {
                    "content": result.content,
                    "file_path": result.file_path if hasattr(result, 'file_path') else None,
                    "line_range": result.line_range if hasattr(result, 'line_range') else None,
                    "metadata": result.metadata,
                    "relevance_score": result.relevance_score,
                }
                for result in search_results
            ]
            
            logger.info(
                "pos_search: Found %s results for content_type='%s', session=%s",
                len(results_list),
                content_type,
                session_id_hash[:8],
            )
            
            return {
                "status": "success",
                "content_type": content_type,
                "query": query,
                "results": results_list,
                "count": len(results_list),
                "session_id": session_id_hash,
            }
        
        except ValueError as e:
            # Validation errors (invalid params)
            error_msg = f"Validation error: {str(e)}"
            logger.error("pos_search validation error: %s", error_msg)
            return {
                "status": "error",
                "content_type": content_type,
                "query": query,
                "error": error_msg,
                "session_id": session_id_hash if 'session_id_hash' in locals() else "unknown",
            }
        
        except RuntimeError as e:
            # Search operation failures
            error_msg = f"Search failed: {str(e)}"
            logger.error("pos_search runtime error: %s", error_msg)
            return {
                "status": "error",
                "content_type": content_type,
                "query": query,
                "error": error_msg,
                "session_id": session_id_hash if 'session_id_hash' in locals() else "unknown",
            }
        
        except Exception as e:
            # Unexpected errors
            error_msg = f"Unexpected error: {str(e)}"
            logger.exception("pos_search unexpected error")
            return {
                "status": "error",
                "content_type": content_type,
                "query": query,
                "error": error_msg,
                "session_id": session_id_hash if 'session_id_hash' in locals() else "unknown",
            }
    
    return 1  # 1 tool registered


__all__ = ['register_pos_search_tools']

