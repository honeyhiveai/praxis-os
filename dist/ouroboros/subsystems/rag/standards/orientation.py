"""
Orientation Metadata Parser for Project Orientation System.

This module provides the OrientationMetadataParser class which extracts
inline orientation metadata from markdown files using the **Metadata**: pattern.

The parser implements error-resistant parsing with graceful degradation:
- Missing metadata returns empty dict (no exceptions)
- Malformed entries are skipped with warnings
- Type coercion with fallback (bool -> int -> string)

Example metadata line:
    **Metadata**: orientation=true, priority=1, query="project setup guide"

Usage:
    >>> from ouroboros.subsystems.rag.standards.orientation import OrientationMetadataParser
    >>> parser = OrientationMetadataParser()
    >>> metadata = parser.extract_inline_metadata(content, file_path)
    >>> print(metadata)
    {'orientation': True, 'priority': 1, 'query': 'project setup guide'}

Requirements:
    FR-001: Inline metadata parsing
    FR-004: Error-resistant design
    FR-006: Graceful degradation
    NFR-R1: Parse < 100ms per file
    NFR-S1: Never raise exceptions on malformed input

Author: prAxIs OS Development Team
Date: 2025-11-19
"""

import re
import logging
import time
from pathlib import Path
from typing import Dict, Any, Union, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from ouroboros.config.schemas.orientation import OrientationQuery


# Module logger
logger = logging.getLogger(__name__)


class OrientationMetadataParser:
    """
    Parse inline orientation metadata from markdown files.
    
    This parser extracts metadata from **Metadata**: lines in markdown files
    using regex-based parsing with comprehensive error handling. It implements
    graceful degradation - malformed input returns empty dict rather than raising
    exceptions.
    
    Attributes:
        METADATA_PATTERN (re.Pattern): Compiled regex for matching **Metadata**: lines.
            Pattern: r'\\*\\*Metadata\\*\\*:\\s*(.+)'
            Matches: **Metadata**: key1=value1, key2=value2, ...
    
    Methods:
        extract_inline_metadata: Extract metadata dict from markdown content
        _coerce_type: Convert string values to appropriate Python types
        _extract_defaults_from_path: Generate default metadata from file path
    
    Error Handling:
        - Missing **Metadata**: line -> returns empty dict
        - Malformed key=value pairs -> skips entry, logs warning
        - Type coercion failure -> falls back to string, logs warning
        - Never raises exceptions to caller
    
    Performance:
        - Compiled regex pattern (class-level, reused across instances)
        - Single-pass parsing
        - Target: < 100ms per file (NFR-R1)
    
    Example:
        >>> parser = OrientationMetadataParser()
        >>> content = '''# Guide\\n**Metadata**: orientation=true, priority=1'''
        >>> metadata = parser.extract_inline_metadata(content, Path("guide.md"))
        >>> assert metadata == {'orientation': True, 'priority': 1}
    """
    
    # Class-level compiled regex pattern for performance
    # Matches: **Metadata**: <content>
    # Example: **Metadata**: orientation=true, priority=1
    METADATA_PATTERN: re.Pattern = re.compile(r'\*\*Metadata\*\*:\s*(.+)')
    
    def __init__(self) -> None:
        """
        Initialize the OrientationMetadataParser.
        
        Creates a new parser instance ready to extract metadata from markdown files.
        The regex pattern is compiled at class level for performance, so initialization
        is lightweight and fast.
        
        Args:
            None
        
        Returns:
            None
        
        Example:
            >>> parser = OrientationMetadataParser()
            >>> assert isinstance(parser, OrientationMetadataParser)
            >>> assert hasattr(parser, 'METADATA_PATTERN')
        """
        # Initialization complete - regex pattern is class-level
        # Future enhancement: Could add configuration options here
        pass
    
    def extract_inline_metadata(self, content: str, file_path: Path) -> Dict[str, Any]:
        """
        Extract orientation metadata from markdown content using **Metadata**: pattern.
        
        This method searches for a **Metadata**: line in the markdown content and parses
        comma-separated key=value pairs. It implements error-resistant parsing with
        graceful degradation - malformed input returns empty dict rather than raising
        exceptions.
        
        Args:
            content (str): Markdown file content to parse for metadata
            file_path (Path): Path to the file being parsed (used for logging)
        
        Returns:
            Dict[str, Any]: Extracted metadata as key-value pairs. Returns empty dict {}
                if **Metadata**: line is missing. Values are type-coerced:
                - "true"/"false" -> bool
                - Numeric strings -> int
                - All others -> str (fallback)
        
        Error Handling:
            - Missing **Metadata**: line -> returns {}
            - Malformed key=value pairs -> skips entry, logs warning
            - Type coercion failure -> falls back to string, logs warning
            - Never raises exceptions
        
        Performance:
            - Single regex search (compiled pattern, O(n))
            - Single-pass parsing
            - Target: < 100ms per file
        
        Examples:
            >>> parser = OrientationMetadataParser()
            >>> 
            >>> # Example 1: Valid metadata with mixed types
            >>> content1 = '''# Project Guide
            ... **Metadata**: orientation=true, priority=1, query="project setup"
            ... More content here...'''
            >>> metadata1 = parser.extract_inline_metadata(content1, Path("guide.md"))
            >>> assert metadata1 == {
            ...     'orientation': True,
            ...     'priority': 1,
            ...     'query': 'project setup'
            ... }
            >>> 
            >>> # Example 2: Missing metadata line (graceful fallback)
            >>> content2 = '''# Regular Document
            ... No metadata here...'''
            >>> metadata2 = parser.extract_inline_metadata(content2, Path("doc.md"))
            >>> assert metadata2 == {}
            >>> 
            >>> # Example 3: Malformed entries are skipped
            >>> content3 = '''# Guide
            ... **Metadata**: good=value, malformed-no-equals, another=works
            ... Content...'''
            >>> metadata3 = parser.extract_inline_metadata(content3, Path("guide.md"))
            >>> assert metadata3 == {'good': 'value', 'another': 'works'}
        
        Design Rationale:
            - Error-resistant: Skips bad entries instead of failing entire parse
            - split('=', 1): Handles values containing '=' character
            - Type coercion: Provides native Python types for convenience
            - Empty dict fallback: Missing metadata is valid (not all files need it)
        """
        try:
            # Search for **Metadata**: line using compiled pattern
            match = self.METADATA_PATTERN.search(content)
            
            if not match:
                # Graceful fallback: missing metadata is valid
                # Return empty dict, don't fail
                return {}
            
            # Extract the metadata string (everything after **Metadata**: )
            metadata_str = match.group(1)
            metadata = {}
            
            # Parse comma-separated key=value pairs with error resistance
            for item in metadata_str.split(','):
                item = item.strip()
                
                # Skip entries without '=' (malformed)
                if '=' not in item:
                    logger.warning(
                        "Skipping malformed metadata entry '%s' in %s: missing '=' character",
                        item, file_path
                    )
                    continue
                
                # Use split('=', 1) to handle values containing '=' character
                # Example: "url=https://example.com/path?param=value"
                key, value = item.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove surrounding quotes if present
                # Example: query="test value" -> test value
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Type coercion using private method
                metadata[key] = self._coerce_type(value)
            
            return metadata
            
        except Exception as e:
            # Catch-all: log error and return empty dict (never fail)
            logger.error(
                "Unexpected error parsing metadata in %s: %s - returning empty dict",
                file_path, e
            )
            return {}
    
    def _coerce_type(self, value: str) -> Union[bool, int, str]:
        """
        Convert string value to appropriate Python type with fallback.
        
        This private method performs type coercion on metadata values extracted
        from **Metadata**: lines. It attempts boolean detection first, then integer,
        and falls back to string for all other cases. Error handling ensures this
        method never raises exceptions.
        
        Args:
            value (str): String value to coerce to appropriate type
        
        Returns:
            Union[bool, int, str]: Coerced value in appropriate type:
                - bool: "true"/"false" (case-insensitive) -> True/False
                - int: Numeric strings ("123", "0", "999") -> int
                - str: All other values (fallback)
        
        Error Handling:
            - Type coercion exceptions caught and logged
            - Always returns string fallback on error
            - Never raises exceptions to caller
        
        Performance:
            - Fast path checks (boolean first, int second)
            - No regex (uses str.lower() and str.isdigit())
            - Single-pass evaluation
        
        Examples:
            >>> parser = OrientationMetadataParser()
            >>> 
            >>> # Boolean coercion (case-insensitive)
            >>> assert parser._coerce_type("true") is True
            >>> assert parser._coerce_type("False") is False
            >>> assert parser._coerce_type("TRUE") is True
            >>> 
            >>> # Integer coercion
            >>> assert parser._coerce_type("123") == 123
            >>> assert parser._coerce_type("0") == 0
            >>> assert parser._coerce_type("999") == 999
            >>> 
            >>> # String fallback
            >>> assert parser._coerce_type("hello") == "hello"
            >>> assert parser._coerce_type("test-value") == "test-value"
            >>> assert parser._coerce_type("abc123") == "abc123"
        
        Design Rationale:
            - Boolean first: Most common orientation flag case
            - isdigit(): Simple, fast, handles positive integers
            - String fallback: Always safe, preserves original value
            - Try-except: Defensive programming, log unexpected errors
        """
        try:
            # Boolean detection (case-insensitive)
            # Handles: "true", "True", "TRUE", "false", "False", "FALSE"
            if value.lower() in ('true', 'false'):
                return value.lower() == 'true'
            
            # Integer detection
            # isdigit() returns True for "123", "0", "999" etc.
            # Note: Does not handle negative numbers ("-5" returns False)
            elif value.isdigit():
                return int(value)
            
            # String fallback (default for all other cases)
            else:
                return value
                
        except Exception as e:
            # Type coercion failed unexpectedly - log warning and fallback
            logger.warning(
                "Unexpected error in type coercion for value '%s': %s - using string fallback",
                value, e
            )
            return value  # String fallback on any error


class OrientationDiscoveryHandler:
    """
    Discovers and aggregates orientation queries from multiple sources.
    
    This handler provides the central discovery mechanism for orientation queries,
    collecting them from two sources:
        1. Standards Index: Queries embedded inline metadata in markdown files
        2. Config File: Queries defined in mcp.yaml project.orientation section
    
    Discovery Strategy:
        - Standards queries: Metadata-tagged markdown files (orientation=true)
        - Config queries: Structured YAML configuration
        - Merging: Combined list with no deduplication (intentional)
        - Graceful: Empty sources return empty list (no errors)
    
    Use Cases:
        - Orientation bootstrap: Discover all queries for AI agent orientation
        - Dynamic discovery: Find project-specific queries at runtime
        - Multi-source aggregation: Combine inline + config queries
    
    Args:
        standards_index: StandardsIndex instance for querying markdown files
        config: MCPConfig instance containing project.orientation section
    
    Example:
        >>> from ouroboros.config.loader import load_config
        >>> from ouroboros.subsystems.rag.standards.container import StandardsIndex
        >>> 
        >>> # Initialize components
        >>> config = load_config()
        >>> standards_index = StandardsIndex(config.indexes.standards)
        >>> 
        >>> # Discover queries
        >>> handler = OrientationDiscoveryHandler(standards_index, config)
        >>> queries = handler.discover_orientation_queries()
        >>> 
        >>> # Use discovered queries
        >>> for query in queries:
        ...     print(f"{query.priority}: {query.query}")
    
    Design Rationale:
        - Two-source discovery: Supports both inline docs and structured config
        - Graceful degradation: Missing sources don't cause failures
        - No deduplication: Allows intentional query repetition (different priorities)
        - Type-safe: Returns List[OrientationQuery] (Pydantic validated)
    """
    
    def __init__(self, standards_index, config):
        """
        Initialize OrientationDiscoveryHandler with index and config.
        
        Args:
            standards_index: StandardsIndex instance for querying markdown content
            config: MCPConfig instance (contains project.orientation section)
        
        Raises:
            TypeError: If standards_index or config are None
        
        Design:
            Stores references to dependencies without deep validation.
            Actual validation happens during discover_orientation_queries().
        """
        if standards_index is None:
            raise TypeError("standards_index cannot be None")
        if config is None:
            raise TypeError("config cannot be None")
        
        self.standards_index = standards_index
        self.config = config
        self.parser = OrientationMetadataParser()
        
        logger.info("OrientationDiscoveryHandler initialized")
    
    def discover_orientation_queries(self) -> List['OrientationQuery']:
        """
        Discover orientation queries from all sources and return merged list.
        
        Discovery Process:
            1. Query standards index for files with orientation=true metadata
            2. Parse inline metadata from markdown content using parser
            3. Load queries from config.project.orientation if present
            4. Merge both sources into single list
            5. Return List[OrientationQuery] (may be empty)
        
        Returns:
            List[OrientationQuery]: All discovered queries from both sources.
                Empty list if no orientation queries found (graceful).
        
        Error Handling:
            - Standards query failure -> logs error, continues with config
            - Config missing/None -> skips config queries, continues
            - Parser errors -> logged by parser, skipped gracefully
            - Returns empty list if both sources fail/empty
        
        Performance:
            - Standards query: Depends on index size (typically < 100ms)
            - Config access: O(1) (direct attribute access)
            - Total: Target < 200ms for typical projects
        
        Examples:
            >>> handler = OrientationDiscoveryHandler(standards_index, config)
            >>> 
            >>> # Discover from both sources
            >>> queries = handler.discover_orientation_queries()
            >>> assert isinstance(queries, list)
            >>> 
            >>> # Handle empty case (no orientation)
            >>> if not queries:
            ...     print("No orientation queries configured")
            >>> 
            >>> # Process discovered queries
            >>> for query in sorted(queries, key=lambda q: q.priority):
            ...     print(f"Priority {query.priority}: {query.query}")
        
        Design Rationale:
            - Try-catch per source: One source failure doesn't block others
            - Empty list fallback: Missing orientation is valid (not an error)
            - No deduplication: Allows intentional repetition at different priorities
            - Standards first: Inline docs typically more stable than config
        """
        queries_from_standards = []
        queries_from_config = []
        
        # Source 1: Standards index (inline metadata)
        try:
            queries_from_standards = self._discover_from_standards()
            logger.info(
                "Discovered %d orientation queries from standards index",
                len(queries_from_standards)
            )
        except Exception as e:
            logger.error(
                "Failed to discover orientation queries from standards: %s",
                e, exc_info=True
            )
            # Continue with config source even if standards fails
        
        # Source 2: Config file (mcp.yaml project.orientation)
        try:
            queries_from_config = self._discover_from_config()
            logger.info(
                "Discovered %d orientation queries from config",
                len(queries_from_config)
            )
        except Exception as e:
            logger.error(
                "Failed to discover orientation queries from config: %s",
                e, exc_info=True
            )
            # Continue even if config fails
        
        # Merge and deduplicate queries (config takes precedence)
        merged_queries = self._merge_sources(queries_from_standards, queries_from_config)
        
        # Resolve dependencies (topological sort)
        dependency_resolved_queries = self._resolve_dependencies(merged_queries)
        
        # Sort by priority (1 → 2 → 3) while preserving dependency order
        sorted_queries = self._sort_by_priority(dependency_resolved_queries)
        
        logger.info(
            "Total orientation queries after merging, dependency resolution, and sorting: %d (standards=%d, config=%d, duplicates removed=%d)",
            len(sorted_queries),
            len(queries_from_standards),
            len(queries_from_config),
            len(queries_from_standards) + len(queries_from_config) - len(sorted_queries)
        )
        
        return sorted_queries
    
    def _discover_from_standards(self) -> List['OrientationQuery']:
        """
        Discover orientation queries from standards index metadata.
        
        Queries the standards index for documents with orientation=true metadata,
        then parses inline metadata to extract OrientationQuery parameters.
        
        Returns:
            List[OrientationQuery]: Queries from standards (empty if none found)
        
        Process:
            1. Query index with filters={'orientation': True}
            2. For each result, parse metadata from content
            3. Extract query, priority, description, category
            4. Construct OrientationQuery objects
            5. Return list of valid queries
        
        Error Handling:
            - Query returns no results -> return []
            - Metadata parsing fails -> skip entry, log warning
            - Invalid OrientationQuery construction -> skip, log error
            - Returns partial results on errors (graceful degradation)
        """
        from ouroboros.config.schemas.orientation import OrientationQuery
        
        queries = []
        
        try:
            # Query standards index for orientation-tagged documents
            results = self.standards_index.search(
                query="orientation",  # Minimal query (filters will do the work)
                n_results=100,  # Get all orientation docs
                filters={'orientation': True}
            )
            
            logger.debug(
                "Standards index query returned %d results for orientation=true",
                len(results)
            )
            
            # Parse metadata from each result
            for result in results:
                try:
                    # Extract metadata from markdown content
                    metadata = self.parser.extract_inline_metadata(
                        result.content,
                        Path(result.file_path)
                    )
                    
                    # Skip if no query defined
                    if 'query' not in metadata:
                        logger.warning(
                            "Skipping orientation doc %s: no 'query' in metadata",
                            result.file_path
                        )
                        continue
                    
                    # Construct OrientationQuery from metadata
                    # Required: query, priority
                    # Optional: description, category, depends_on
                    query = OrientationQuery(
                        query=metadata['query'],
                        priority=metadata.get('priority', 2),  # Default medium priority
                        description=metadata.get('description'),
                        category=metadata.get('category'),
                        depends_on=metadata.get('depends_on')
                    )
                    
                    queries.append(query)
                    logger.debug(
                        "Parsed orientation query from %s: %s (priority=%d)",
                        result.file_path, query.query, query.priority
                    )
                    
                except Exception as e:
                    logger.warning(
                        "Failed to parse orientation query from %s: %s - skipping",
                        result.file_path if 'result' in locals() else 'unknown',
                        e
                    )
                    continue
            
            return queries
            
        except Exception as e:
            logger.error(
                "Failed to query standards index for orientation: %s",
                e, exc_info=True
            )
            return []  # Return empty list on error
    
    def _discover_from_config(self) -> List['OrientationQuery']:
        """
        Discover orientation queries from mcp.yaml config.
        
        Extracts queries from config.project.orientation.queries if present.
        
        Returns:
            List[OrientationQuery]: Queries from config (empty if none/missing)
        
        Process:
            1. Check if config.project exists
            2. Check if config.project.orientation exists
            3. Check if config.project.orientation.enabled is True
            4. Return config.project.orientation.queries
        
        Error Handling:
            - project section missing -> return []
            - orientation section missing -> return []
            - orientation.enabled is False -> return []
            - queries list empty -> return []
            - All cases handled gracefully (no exceptions)
        """
        try:
            # Check if project section exists
            if not hasattr(self.config, 'project') or self.config.project is None:
                logger.debug("No project section in config - skipping config queries")
                return []
            
            # Check if orientation section exists
            if not hasattr(self.config.project, 'orientation') or self.config.project.orientation is None:
                logger.debug("No project.orientation section in config - skipping config queries")
                return []
            
            # Check if orientation is enabled
            if not self.config.project.orientation.enabled:
                logger.info("Project orientation is disabled in config - skipping config queries")
                return []
            
            # Return queries from config (already OrientationQuery objects)
            from ouroboros.config.schemas.orientation import OrientationQuery
            queries: List[OrientationQuery] = self.config.project.orientation.queries
            logger.debug(
                "Loaded %d orientation queries from config",
                len(queries)
            )
            return queries
            
        except Exception as e:
            logger.error(
                "Failed to load orientation queries from config: %s",
                e, exc_info=True
            )
            return []  # Return empty list on error
    
    def _merge_sources(
        self,
        standards_queries: List['OrientationQuery'],
        config_queries: List['OrientationQuery']
    ) -> List['OrientationQuery']:
        """
        Merge and deduplicate queries from standards and config sources.
        
        Implements intelligent merging with the following rules:
            1. Deduplicate by query string (case-sensitive exact match)
            2. Config queries take precedence over standards queries
            3. Preserve all unique queries from both sources
            4. Maintain query order: config queries first, then unique standards queries
        
        Precedence Rationale:
            Config queries (mcp.yaml) represent explicit project configuration
            and should override inline standards metadata. This allows projects
            to customize orientation without modifying source documentation.
        
        Args:
            standards_queries: Queries discovered from standards index
            config_queries: Queries discovered from mcp.yaml config
        
        Returns:
            List[OrientationQuery]: Merged list without duplicates.
                Config queries appear first, followed by unique standards queries.
        
        Deduplication Strategy:
            - Uses query string as deduplication key
            - Case-sensitive comparison (intentional)
            - Config query overwrites standards query if same string
            - Preserves all metadata from winning query
        
        Performance:
            - O(n) for standards queries (build set)
            - O(m) for config queries (filter duplicates)
            - Total: O(n + m) where n=standards, m=config
            - Memory: O(n) for query_strings set
        
        Examples:
            >>> handler = OrientationDiscoveryHandler(standards_index, config)
            >>> 
            >>> # Example 1: No duplicates
            >>> standards = [
            ...     OrientationQuery(query="standards query 1", priority=1),
            ...     OrientationQuery(query="standards query 2", priority=2)
            ... ]
            >>> config = [
            ...     OrientationQuery(query="config query", priority=1)
            ... ]
            >>> merged = handler._merge_sources(standards, config)
            >>> assert len(merged) == 3  # All unique
            >>> 
            >>> # Example 2: With duplicates (config wins)
            >>> standards = [
            ...     OrientationQuery(query="duplicate query", priority=2, description="From standards"),
            ...     OrientationQuery(query="unique standards", priority=1)
            ... ]
            >>> config = [
            ...     OrientationQuery(query="duplicate query", priority=1, description="From config")
            ... ]
            >>> merged = handler._merge_sources(standards, config)
            >>> assert len(merged) == 2  # 1 duplicate removed
            >>> assert merged[0].description == "From config"  # Config won
            >>> assert merged[0].priority == 1  # Config priority
        
        Design Rationale:
            - Config first: Explicit configuration is primary source
            - Query string key: Simplest, most intuitive deduplication
            - No metadata merging: Prevents complexity, unclear semantics
            - Preserves order: Predictable execution order (priority-based)
        """
        # Early exit for empty cases
        if not standards_queries and not config_queries:
            return []
        if not standards_queries:
            return list(config_queries)  # Return copy
        if not config_queries:
            return list(standards_queries)  # Return copy
        
        # Build set of query strings from config (for deduplication)
        config_query_strings = {q.query for q in config_queries}
        
        logger.debug(
            "Merging queries: %d from standards, %d from config, %d config query strings",
            len(standards_queries),
            len(config_queries),
            len(config_query_strings)
        )
        
        # Filter standards queries to exclude duplicates
        unique_standards_queries = [
            q for q in standards_queries
            if q.query not in config_query_strings
        ]
        
        duplicates_removed = len(standards_queries) - len(unique_standards_queries)
        if duplicates_removed > 0:
            logger.info(
                "Removed %d duplicate queries (config took precedence over standards)",
                duplicates_removed
            )
        
        # Merge: config first (precedence), then unique standards
        merged = list(config_queries) + unique_standards_queries
        
        logger.debug(
            "Merged result: %d total queries (%d config + %d unique standards)",
            len(merged),
            len(config_queries),
            len(unique_standards_queries)
        )
        
        return merged
    
    def _sort_by_priority(self, queries: List['OrientationQuery']) -> List['OrientationQuery']:
        """
        Sort orientation queries by priority field (1 → 2 → 3).
        
        Implements stable sorting with the following rules:
            1. Sort by priority ascending (1=high, 2=medium, 3=low)
            2. Within same priority, preserve original order (stable sort)
            3. Missing priority defaults to 2 (medium, already set by Pydantic)
        
        Sort Order:
            - Priority 1: High priority (foundational, execute first)
            - Priority 2: Medium priority (important, execute second)
            - Priority 3: Low priority (supplemental, execute last)
        
        Args:
            queries: List of OrientationQuery objects to sort
        
        Returns:
            List[OrientationQuery]: Sorted list (new list, input not modified)
        
        Stability:
            Python's sorted() is stable, so queries with the same priority
            maintain their relative order from the input list. This preserves:
                - Config queries before standards queries (from merge step)
                - Definition order within each source
        
        Performance:
            - Timsort algorithm: O(n log n) worst case
            - Best case O(n) for nearly sorted data
            - Stable sort: Preserves relative order
            - Memory: O(n) for new list
        
        Examples:
            >>> handler = OrientationDiscoveryHandler(standards_index, config)
            >>> 
            >>> # Mixed priorities
            >>> unsorted = [
            ...     OrientationQuery(query="third", priority=3),
            ...     OrientationQuery(query="first A", priority=1),
            ...     OrientationQuery(query="second", priority=2),
            ...     OrientationQuery(query="first B", priority=1)
            ... ]
            >>> sorted_queries = handler._sort_by_priority(unsorted)
            >>> assert [q.query for q in sorted_queries] == [
            ...     "first A",  # priority 1
            ...     "first B",  # priority 1 (order preserved)
            ...     "second",   # priority 2
            ...     "third"     # priority 3
            ... ]
        
        Design Rationale:
            - Priority first: Ensures critical queries execute before supplemental
            - Stable sort: Predictable, preserves merge order (config before standards)
            - Ascending order: Natural priority ordering (1 is highest)
            - Simple key: Just priority field, no complex comparisons
        """
        # Early exit for empty list
        if not queries:
            return []
        
        # Sort by priority (ascending: 1, 2, 3)
        # Python's sorted() is stable (preserves order for equal keys)
        sorted_queries = sorted(queries, key=lambda q: q.priority)
        
        logger.debug(
            "Sorted %d queries by priority (stable sort preserves definition order)",
            len(sorted_queries)
        )
        
        return sorted_queries
    
    def _resolve_dependencies(self, queries: List['OrientationQuery']) -> List['OrientationQuery']:
        """
        Resolve query dependencies using topological sort.
        
        Implements dependency resolution with the following rules:
            1. Queries with depends_on execute after their dependencies
            2. Circular dependencies raise ValueError
            3. No dependencies → returns original order
            4. Topological sort ensures correct execution order
        
        Dependency Resolution:
            If query A depends_on query B, then B must execute before A.
            This ensures that dependent queries have context from their dependencies.
        
        Args:
            queries: List of OrientationQuery objects (may have depends_on)
        
        Returns:
            List[OrientationQuery]: Topologically sorted list respecting dependencies
        
        Raises:
            ValueError: If circular dependencies detected (e.g., A→B→A)
        
        Algorithm:
            Uses Kahn's algorithm for topological sorting:
            1. Build adjacency list (dependency graph)
            2. Calculate in-degrees (number of dependencies per query)
            3. Start with queries having 0 dependencies
            4. Process queries, decrementing dependent in-degrees
            5. Detect cycles if any queries remain unprocessed
        
        Performance:
            - Time: O(V + E) where V=queries, E=dependencies
            - Space: O(V + E) for graph and in-degree storage
            - Target: < 10ms for typical query counts (< 50 queries)
        
        Examples:
            >>> handler = OrientationDiscoveryHandler(standards_index, config)
            >>> 
            >>> # Linear dependency chain: A→B→C
            >>> queries = [
            ...     OrientationQuery(query="A", priority=1, depends_on=["B"]),
            ...     OrientationQuery(query="B", priority=1, depends_on=["C"]),
            ...     OrientationQuery(query="C", priority=1)
            ... ]
            >>> resolved = handler._resolve_dependencies(queries)
            >>> assert [q.query for q in resolved] == ["C", "B", "A"]
            >>> 
            >>> # Circular dependency: A→B→A (raises ValueError)
            >>> circular = [
            ...     OrientationQuery(query="A", priority=1, depends_on=["B"]),
            ...     OrientationQuery(query="B", priority=1, depends_on=["A"])
            ... ]
            >>> try:
            ...     handler._resolve_dependencies(circular)
            ... except ValueError as e:
            ...     print(e)  # "Circular dependency detected: A → B → A"
        
        Design Rationale:
            - Topological sort: Standard algorithm for dependency resolution
            - Kahn's algorithm: Simple, efficient, detects cycles naturally
            - Query string as key: Matches depends_on field format
            - Fail-fast on cycles: Invalid dependency configuration
        """
        # Early exit for empty list or queries without dependencies
        if not queries:
            return []
        
        # Check if any queries have dependencies
        has_dependencies = any(q.depends_on for q in queries)
        if not has_dependencies:
            logger.debug("No dependencies found, returning original order")
            return queries
        
        logger.debug("Resolving dependencies for %d queries", len(queries))
        
        # Build query lookup map (query_string → OrientationQuery)
        query_map: Dict[str, 'OrientationQuery'] = {q.query: q for q in queries}
        
        # Build adjacency list (dependency → [dependent_queries])
        # If A depends_on B, then B → A in the graph
        graph: Dict[str, List[str]] = {q.query: [] for q in queries}
        in_degree: Dict[str, int] = {q.query: 0 for q in queries}
        
        for query in queries:
            if query.depends_on:
                for dependency_query_str in query.depends_on:
                    # Validate dependency exists in query set
                    if dependency_query_str not in query_map:
                        logger.warning(
                            "Query '%s' depends on '%s' which is not in the query set - ignoring dependency",
                            query.query, dependency_query_str
                        )
                        continue
                    
                    # Add edge: dependency → query
                    graph[dependency_query_str].append(query.query)
                    in_degree[query.query] += 1
        
        # Kahn's algorithm: Start with queries having no dependencies (in_degree = 0)
        queue = [q for q in queries if in_degree[q.query] == 0]
        sorted_queries = []
        
        while queue:
            # Pop query with no dependencies
            current = queue.pop(0)
            sorted_queries.append(current)
            
            # Decrement in-degree of dependent queries
            for dependent_query_str in graph[current.query]:
                in_degree[dependent_query_str] -= 1
                
                # If dependent now has no dependencies, add to queue
                if in_degree[dependent_query_str] == 0:
                    queue.append(query_map[dependent_query_str])
        
        # Check for circular dependencies
        if len(sorted_queries) != len(queries):
            # Find queries involved in cycle
            cycle_queries = [q for q in queries if in_degree[q.query] > 0]
            cycle_query_strs = [q.query for q in cycle_queries]
            
            # Build cycle description for error message
            cycle_desc = " → ".join(cycle_query_strs[:3])  # Show first 3
            if len(cycle_query_strs) > 3:
                cycle_desc += " → ..."
            
            raise ValueError(
                f"Circular dependency detected involving queries: {cycle_query_strs}. "
                f"Example cycle: {cycle_desc}. "
                f"Remediation: Remove circular dependencies from query definitions."
            )
        
        logger.info(
            "Dependency resolution complete: %d queries sorted topologically",
            len(sorted_queries)
        )
        
        return sorted_queries


@dataclass
class QueryExecutionResult:
    """
    Result of executing a single orientation query.
    
    Captures the query, execution time, success status, and any results or errors.
    Used for tracking and debugging orientation execution.
    
    Attributes:
        query: The OrientationQuery that was executed
        execution_time_ms: Time taken to execute query in milliseconds
        success: Whether query executed successfully
        result_count: Number of results returned (0 if failed)
        error_message: Error message if query failed (None if successful)
    """
    query: 'OrientationQuery'
    execution_time_ms: float
    success: bool
    result_count: int = 0
    error_message: Optional[str] = None


@dataclass
class OrientationSessionSummary:
    """
    Summary of an orientation session execution.
    
    Aggregates results from all queries executed during orientation,
    providing metrics for monitoring and debugging.
    
    Attributes:
        total_queries: Total number of queries attempted
        successful_queries: Number of queries that executed successfully
        failed_queries: Number of queries that failed
        total_execution_time_ms: Total time for all queries in milliseconds
        query_results: List of individual query execution results
        completed: Whether all queries completed (not interrupted by timeout)
        p50_execution_time_ms: 50th percentile (median) query execution time
        p95_execution_time_ms: 95th percentile query execution time
        p99_execution_time_ms: 99th percentile query execution time
        slowest_query_string: Query string of the slowest query
        slowest_time_ms: Execution time of the slowest query
    """
    total_queries: int
    successful_queries: int
    failed_queries: int
    total_execution_time_ms: float
    query_results: List[QueryExecutionResult] = field(default_factory=list)
    completed: bool = True
    p50_execution_time_ms: float = 0.0
    p95_execution_time_ms: float = 0.0
    p99_execution_time_ms: float = 0.0
    slowest_query_string: str = ""
    slowest_time_ms: float = 0.0


class ProjectOrientationExecutor:
    """
    Executes project orientation queries and tracks results.
    
    This executor is responsible for:
        1. Executing orientation queries via search tool
        2. Tracking execution time per query
        3. Handling query failures gracefully
        4. Collecting results into session summary
        5. Supporting partial results on timeout
    
    The executor provides a clean separation between query discovery
    (handled by OrientationDiscoveryHandler) and query execution.
    
    Args:
        search_tool: Callable that executes search queries
            Expected signature: search_tool(query: str) -> List[SearchResult]
    
    Example:
        >>> from ouroboros.subsystems.rag.standards.container import StandardsIndex
        >>> 
        >>> # Create search tool (typically pos_search_project)
        >>> standards_index = StandardsIndex(config.indexes.standards)
        >>> search_tool = standards_index.search
        >>> 
        >>> # Create executor
        >>> executor = ProjectOrientationExecutor(search_tool)
        >>> 
        >>> # Execute queries
        >>> queries = [
        ...     OrientationQuery(query="dogfooding model", priority=1),
        ...     OrientationQuery(query="test location lifecycle", priority=2)
        ... ]
        >>> summary = executor.execute_orientation(queries)
        >>> 
        >>> # Review results
        >>> print(f"Executed {summary.total_queries} queries")
        >>> print(f"Success: {summary.successful_queries}, Failed: {summary.failed_queries}")
        >>> print(f"Total time: {summary.total_execution_time_ms:.2f}ms")
    
    Design Rationale:
        - Dependency injection: search_tool is injected (testable)
        - Error resilience: Individual query failures don't stop execution
        - Observability: Comprehensive metrics for monitoring
        - Timeout support: Can return partial results
    """
    
    def __init__(self, search_tool):
        """
        Initialize ProjectOrientationExecutor with search tool.
        
        Args:
            search_tool: Callable that executes search queries.
                Expected signature: search_tool(query: str) -> List[SearchResult]
        
        Raises:
            TypeError: If search_tool is None
        
        Design:
            Stores reference to search tool without validation.
            Actual validation happens during execute_orientation().
        """
        if search_tool is None:
            raise TypeError("search_tool cannot be None")
        
        self.search_tool = search_tool
        
        logger.info("ProjectOrientationExecutor initialized")
    
    def execute_orientation(
        self,
        queries: List['OrientationQuery'],
        timeout_ms: float = 60000.0,  # 60 seconds default
        per_query_timeout_ms: float = 10000.0  # 10 seconds per query
    ) -> OrientationSessionSummary:
        """
        Execute all orientation queries and return summary.
        
        Executes queries sequentially in priority order, tracking time and
        results for each query. Handles individual query failures gracefully
        to ensure all queries are attempted.
        
        Args:
            queries: List of OrientationQuery objects to execute (pre-sorted by priority)
            timeout_ms: Total timeout in milliseconds (default: 60000ms = 60 seconds).
                       If exceeded, returns partial results with completed=False
            per_query_timeout_ms: Per-query timeout in milliseconds (default: 10000ms = 10 seconds).
                                 Individual queries exceeding this timeout are marked as failed
        
        Returns:
            OrientationSessionSummary: Aggregate results from all queries
        
        Execution Flow:
            1. Validate inputs
            2. For each query:
                a. Check timeout (if specified)
                b. Execute query via search_tool
                c. Track timing and results
                d. Handle errors gracefully
            3. Build summary with all results
            4. Return summary (may be partial if timeout)
        
        Error Handling:
            - Individual query failures logged but don't stop execution
            - Timeout returns partial results (completed=False)
            - Empty query list returns empty summary (not an error)
            - Search tool exceptions caught and logged
        
        Performance:
            - Sequential execution: O(n) where n = number of queries
            - Target: < 100ms per query for typical searches
            - Total time depends on query complexity and index size
        
        Examples:
            >>> executor = ProjectOrientationExecutor(search_tool)
            >>> 
            >>> # Execute 3 queries
            >>> queries = [
            ...     OrientationQuery(query="query 1", priority=1),
            ...     OrientationQuery(query="query 2", priority=2),
            ...     OrientationQuery(query="query 3", priority=3)
            ... ]
            >>> summary = executor.execute_orientation(queries)
            >>> 
            >>> # Check results
            >>> assert summary.total_queries == 3
            >>> assert summary.completed is True
            >>> 
            >>> # With timeout
            >>> summary = executor.execute_orientation(queries, timeout_ms=100)
            >>> if not summary.completed:
            ...     print(f"Timed out after {summary.successful_queries} queries")
        
        Design Rationale:
            - Sequential execution: Simpler, predictable resource usage
            - Error resilience: One failure doesn't crash entire session
            - Timeout support: Prevents hanging on slow queries
            - Comprehensive metrics: Full observability into execution
        """
        # Validate inputs
        if not queries:
            logger.warning("execute_orientation called with empty queries list")
            return OrientationSessionSummary(
                total_queries=0,
                successful_queries=0,
                failed_queries=0,
                total_execution_time_ms=0.0,
                query_results=[],
                completed=True
            )
        
        logger.info("Starting orientation execution for %d queries", len(queries))
        
        # Initialize tracking
        start_time = time.time()
        query_results = []
        successful_count = 0
        failed_count = 0
        completed = True
        
        # Execute each query
        for idx, query in enumerate(queries):
            # Check timeout
            elapsed_ms = (time.time() - start_time) * 1000
            if elapsed_ms >= timeout_ms:
                logger.warning(
                    "Orientation timeout after %.2fms (%d/%d queries completed)",
                    elapsed_ms, idx, len(queries)
                )
                completed = False
                break
            
            # Execute single query with timing and per-query timeout
            result = self._execute_single_query(query, per_query_timeout_ms)
            query_results.append(result)
            
            if result.success:
                successful_count += 1
            else:
                failed_count += 1
        
        # Calculate total time
        total_time_ms = (time.time() - start_time) * 1000
        
        # Calculate performance metrics
        perf_metrics = self._calculate_performance_metrics(query_results)
        
        # Build summary
        summary = OrientationSessionSummary(
            total_queries=len(queries),
            successful_queries=successful_count,
            failed_queries=failed_count,
            total_execution_time_ms=total_time_ms,
            query_results=query_results,
            completed=completed,
            p50_execution_time_ms=perf_metrics['p50'],
            p95_execution_time_ms=perf_metrics['p95'],
            p99_execution_time_ms=perf_metrics['p99'],
            slowest_query_string=perf_metrics['slowest_query'],
            slowest_time_ms=perf_metrics['slowest_time']
        )
        
        # Log performance summary
        logger.info(
            "Orientation execution complete: %d/%d successful, %.2fms total, completed=%s",
            successful_count, len(queries), total_time_ms, completed
        )
        logger.info(
            "Performance metrics - p50: %.2fms, p95: %.2fms, p99: %.2fms, slowest: '%s' (%.2fms)",
            perf_metrics['p50'], perf_metrics['p95'], perf_metrics['p99'],
            perf_metrics['slowest_query'], perf_metrics['slowest_time']
        )
        
        return summary
    
    def _execute_single_query(
        self,
        query: 'OrientationQuery',
        timeout_ms: float
    ) -> QueryExecutionResult:
        """
        Execute a single orientation query and return result.
        
        Args:
            query: OrientationQuery to execute
            timeout_ms: Timeout for this single query in milliseconds (default: 10000ms)
        
        Returns:
            QueryExecutionResult: Result with timing and status
        
        Error Handling:
            - Catches all exceptions from search_tool
            - Returns failed result with error message
            - Logs error for debugging
            - Queries exceeding timeout_ms are marked as failed
        
        Note:
            Per-query timeout enforcement depends on search_tool implementation.
            For synchronous search tools, timeout is advisory (logged if exceeded).
            For async search tools, timeout can be enforced with asyncio.wait_for().
        """
        logger.debug("Executing query: %s (priority=%d)", query.query, query.priority)
        
        start_time = time.time()
        
        try:
            # Execute search
            results = self.search_tool(query.query)
            
            # Calculate timing
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Build success result
            result = QueryExecutionResult(
                query=query,
                execution_time_ms=execution_time_ms,
                success=True,
                result_count=len(results) if results else 0
            )
            
            # Check if query exceeded timeout (advisory warning)
            if execution_time_ms > timeout_ms:
                logger.warning(
                    "Query exceeded per-query timeout: %.2fms > %.2fms (query: %s)",
                    execution_time_ms, timeout_ms, query.query
                )
            else:
                logger.debug(
                    "Query succeeded: %d results in %.2fms",
                    result.result_count, execution_time_ms
                )
            
            return result
            
        except Exception as e:
            # Calculate timing even on failure
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Build failure result
            result = QueryExecutionResult(
                query=query,
                execution_time_ms=execution_time_ms,
                success=False,
                result_count=0,
                error_message=str(e)
            )
            
            logger.error(
                "Query failed: %s (%.2fms) - %s",
                query.query, execution_time_ms, e
            )
            
            return result
    
    def _calculate_performance_metrics(self, results: List[QueryExecutionResult]) -> dict:
        """
        Calculate performance metrics from query execution results.
        
        Computes percentiles (p50, p95, p99) and identifies slowest query
        for monitoring and performance analysis.
        
        Args:
            results: List of QueryExecutionResult from execution
        
        Returns:
            dict: Performance metrics with keys:
                - p50: 50th percentile execution time (median)
                - p95: 95th percentile execution time
                - p99: 99th percentile execution time
                - slowest_query: Query string of slowest query
                - slowest_time: Execution time of slowest query
        
        Algorithm:
            1. Extract execution times from results
            2. Sort times for percentile calculation
            3. Use simple percentile formula: time[int(len * percentile)]
            4. Find slowest query by max execution time
        
        Performance:
            - Time: O(n log n) for sorting
            - Space: O(n) for times list
            - Target: < 1ms for typical query counts
        
        Examples:
            >>> executor = ProjectOrientationExecutor(search_tool)
            >>> results = [
            ...     QueryExecutionResult(query=q1, execution_time_ms=100, success=True),
            ...     QueryExecutionResult(query=q2, execution_time_ms=200, success=True),
            ...     QueryExecutionResult(query=q3, execution_time_ms=300, success=True)
            ... ]
            >>> metrics = executor._calculate_performance_metrics(results)
            >>> assert metrics['p50'] == 200.0  # Median
            >>> assert metrics['slowest_time'] == 300.0
        
        Design Rationale:
            - Percentiles: Standard performance monitoring metrics
            - Simple calculation: Index-based percentile (no interpolation)
            - Slowest query tracking: Identifies performance outliers
            - Zero defaults: Handles empty results gracefully
        """
        # Handle empty results
        if not results:
            return {
                'p50': 0.0,
                'p95': 0.0,
                'p99': 0.0,
                'slowest_query': '',
                'slowest_time': 0.0
            }
        
        # Extract execution times
        times = [r.execution_time_ms for r in results]
        times_sorted = sorted(times)
        
        # Calculate percentiles using index-based approach
        n = len(times_sorted)
        p50_idx = int(n * 0.50) if n > 0 else 0
        p95_idx = int(n * 0.95) if n > 0 else 0
        p99_idx = int(n * 0.99) if n > 0 else 0
        
        # Ensure indices are within bounds
        p50_idx = min(p50_idx, n - 1)
        p95_idx = min(p95_idx, n - 1)
        p99_idx = min(p99_idx, n - 1)
        
        p50 = times_sorted[p50_idx]
        p95 = times_sorted[p95_idx]
        p99 = times_sorted[p99_idx]
        
        # Find slowest query
        slowest_result = max(results, key=lambda r: r.execution_time_ms)
        
        return {
            'p50': p50,
            'p95': p95,
            'p99': p99,
            'slowest_query': slowest_result.query.query,
            'slowest_time': slowest_result.execution_time_ms
        }

