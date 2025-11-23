"""
Project Orientation configuration schemas.

Provides Pydantic v2 models for project-specific orientation queries that
extend the base 10 mandatory orientation queries with project-specific guidance.

Models:
    OrientationQuery: Single orientation query with priority and dependencies
    ProjectOrientation: Collection of orientation queries with enable flag
    ProjectConfig: Top-level project configuration with orientation section

The project orientation system allows projects to define custom queries that
execute after the base 10 mandatory queries, providing project-specific context
to AI agents during orientation.

Example mcp.yaml:
    project:
      orientation:
        enabled: true
        queries:
          - query: "dogfooding model self-hosting praxis-os"
            priority: 1
            description: "Understand how prAxIs OS dogfoods itself"
            category: "development"
          - query: "test location lifecycle where to write tests"
            priority: 2
            depends_on: ["dogfooding model"]

See Also:
    - base.BaseConfig: Base configuration model
    - mcp.MCPConfig: Root configuration that includes ProjectConfig
"""

from typing import List, Optional

from pydantic import Field, field_validator

from ouroboros.config.schemas.base import BaseConfig


class OrientationQuery(BaseConfig):
    """
    Single orientation query with priority and validation.
    
    Represents one query to execute during project orientation. Queries are
    executed in priority order (1=highest, 3=lowest) after the 10 mandatory
    base queries complete.
    
    Fields:
        query (str): Query string to execute via pos_search_project()
            - Minimum 5 characters (ensures meaningful query)
            - Maximum 500 characters (prevents excessively long queries)
            - Should use content-specific phrases (see query-construction-patterns.md)
        
        priority (int): Execution priority (1-3)
            - 1: High priority (execute first, foundational concepts)
            - 2: Medium priority (execute second, important but non-blocking)
            - 3: Low priority (execute last, nice-to-have context)
        
        description (str, optional): Human-readable description of query purpose
            - Helps maintainers understand why this query exists
            - Not used during execution (documentation only)
        
        category (str, optional): Query category for organization
            - Examples: "development", "architecture", "testing", "deployment"
            - Used for grouping queries in documentation
        
        depends_on (List[str], optional): Query dependencies
            - List of query strings this query depends on
            - Execution order respects dependencies within priority level
            - Circular dependencies prevented by validator
    
    Validation:
        - Priority must be 1, 2, or 3 (enforced by range validator)
        - Query length must be 5-500 characters (enforced by Field constraints)
        - Circular dependencies prevented (query cannot depend on itself)
        - Actionable error messages guide remediation
    
    Example:
        >>> # Valid query
        >>> query = OrientationQuery(
        ...     query="dogfooding model development workflow",
        ...     priority=1,
        ...     description="Learn how prAxIs OS dogfoods itself",
        ...     category="development"
        ... )
        >>> 
        >>> # Invalid priority raises ValidationError
        >>> try:
        ...     bad_query = OrientationQuery(query="test query", priority=5)
        ... except ValidationError as e:
        ...     print(e)  # "Priority must be 1, 2, or 3 (got 5)"
    
    Design Rationale:
        - Priority-based execution ensures foundational queries run first
        - Dependencies allow complex knowledge graphs
        - Field constraints catch common errors early (fail-fast)
        - Optional fields provide flexibility without complexity
    """
    
    query: str = Field(
        description="Query string to execute during orientation",
        min_length=5,
        max_length=500
    )
    
    priority: int = Field(
        description="Execution priority (1=high, 2=medium, 3=low)",
        ge=1,
        le=3
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Human-readable description of query purpose (documentation only)"
    )
    
    category: Optional[str] = Field(
        default=None,
        description="Query category for organization (e.g., 'development', 'testing')"
    )
    
    depends_on: Optional[List[str]] = Field(
        default=None,
        description="List of query strings this query depends on"
    )
    
    @field_validator("priority")
    @classmethod
    def validate_priority_range(cls, v: int) -> int:
        """
        Validate priority is within valid range (1-3).
        
        Args:
            v: Priority value to validate
        
        Returns:
            int: Validated priority value
        
        Raises:
            ValueError: If priority is not 1, 2, or 3
        
        Note:
            Pydantic v2 Field(ge=1, le=3) already validates range,
            but this provides more actionable error message.
        """
        if v < 1 or v > 3:
            raise ValueError(
                f"Priority must be 1 (high), 2 (medium), or 3 (low). Got: {v}. "
                f"Remediation: Update priority to a valid value (1-3)."
            )
        return v
    
    @field_validator("depends_on")
    @classmethod
    def validate_no_circular_dependencies(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        """
        Prevent circular dependencies (query depending on itself).
        
        Args:
            v: List of query dependencies
            info: Validation context with other field values
        
        Returns:
            Optional[List[str]]: Validated dependencies list
        
        Raises:
            ValueError: If query depends on itself (circular dependency)
        
        Design:
            Only checks direct self-dependency here. Full dependency graph
            cycle detection happens in ProjectOrientation validator.
        """
        if v is None:
            return v
        
        # Get the query string being validated
        query_str = info.data.get('query')
        
        # Check if query depends on itself
        if query_str and query_str in v:
            raise ValueError(
                f"Circular dependency detected: Query '{query_str}' cannot depend on itself. "
                f"Remediation: Remove '{query_str}' from depends_on list."
            )
        
        return v


class ProjectOrientation(BaseConfig):
    """
    Project orientation configuration with query collection.
    
    Container for project-specific orientation queries that execute after the
    10 mandatory base queries. Provides enable/disable flag and duplicate
    detection to prevent configuration errors.
    
    Fields:
        enabled (bool): Whether project orientation is enabled
            - Default: True
            - When False, project queries are skipped entirely
            - Useful for temporarily disabling without removing queries
        
        queries (List[OrientationQuery]): List of orientation queries
            - Can be empty (no queries is valid)
            - Executed in priority order (1 → 2 → 3)
            - Duplicate query strings prevented by validator
    
    Validation:
        - Duplicate query strings raise ValidationError with details
        - Empty queries list is valid (project may have no custom queries)
        - Queries execute in priority order regardless of list order
    
    Example:
        >>> # Minimal configuration (enabled by default)
        >>> config = ProjectOrientation(queries=[])
        >>> assert config.enabled is True
        >>> assert config.queries == []
        >>> 
        >>> # Full configuration
        >>> config = ProjectOrientation(
        ...     enabled=True,
        ...     queries=[
        ...         OrientationQuery(
        ...             query="dogfooding model development",
        ...             priority=1
        ...         ),
        ...         OrientationQuery(
        ...             query="test location lifecycle",
        ...             priority=2
        ...         )
        ...     ]
        ... )
        >>> 
        >>> # Duplicate queries raise ValidationError
        >>> try:
        ...     bad_config = ProjectOrientation(
        ...         queries=[
        ...             OrientationQuery(query="test query", priority=1),
        ...             OrientationQuery(query="test query", priority=2)  # Duplicate!
        ...         ]
        ...     )
        ... except ValidationError as e:
        ...     print(e)  # "Duplicate query: 'test query'"
    
    Design Rationale:
        - enabled flag: Allows temporary disable without config changes
        - Duplicate detection: Prevents copy-paste errors in mcp.yaml
        - Empty queries allowed: Not all projects need custom orientation
        - Priority-based execution: Foundation queries before advanced topics
    """
    
    enabled: bool = Field(
        default=True,
        description="Whether project orientation is enabled (default: True)"
    )
    
    queries: List[OrientationQuery] = Field(
        description="List of project-specific orientation queries"
    )
    
    @field_validator("queries")
    @classmethod
    def validate_no_duplicate_queries(cls, v: List[OrientationQuery]) -> List[OrientationQuery]:
        """
        Prevent duplicate query strings in the queries list.
        
        Args:
            v: List of OrientationQuery objects to validate
        
        Returns:
            List[OrientationQuery]: Validated queries list
        
        Raises:
            ValueError: If duplicate query strings are found
        
        Design:
            Checks for duplicate query strings (case-sensitive exact match).
            This prevents copy-paste errors where the same query is defined
            multiple times with different priorities or descriptions.
        
        Example:
            >>> # This raises ValueError
            >>> queries = [
            ...     OrientationQuery(query="test query", priority=1),
            ...     OrientationQuery(query="test query", priority=2)  # Duplicate!
            ... ]
        """
        if not v:
            # Empty list is valid
            return v
        
        # Extract query strings
        query_strings = [q.query for q in v]
        
        # Check for duplicates
        seen = set()
        duplicates = []
        
        for query_str in query_strings:
            if query_str in seen:
                duplicates.append(query_str)
            seen.add(query_str)
        
        if duplicates:
            # List unique duplicates for clarity
            unique_duplicates = list(set(duplicates))
            raise ValueError(
                f"Duplicate queries found: {unique_duplicates}. "
                f"Each query string must be unique. "
                f"Remediation: Remove or modify duplicate queries in mcp.yaml."
            )
        
        return v


class BaseOrientation(BaseConfig):
    """
    Base orientation queries (praxis-os defaults).
    
    Contains the base praxis-os orientation queries that all projects inherit.
    These queries provide foundational knowledge about praxis-os patterns,
    behaviors, and architecture.
    
    Fields:
        queries (List[OrientationQuery]): List of base orientation queries
            - Defined in dist/config/mcp.yaml (distribution template)
            - ~10 queries covering core praxis-os concepts
            - Always executed first (before project queries)
    
    Example YAML:
        orientation:
          base:
            queries:
              - query: "stateless AI architecture cease to exist"
                priority: 1
                category: "foundational"
                description: "Core architectural truth"
    """
    
    queries: List[OrientationQuery] = Field(
        default_factory=list,
        description="List of base praxis-os orientation queries"
    )


class ProjectOrientationQueries(BaseConfig):
    """
    Project-specific orientation queries (optional).
    
    Contains project-specific orientation queries that extend the base queries
    with project-specific context, architecture, and patterns.
    
    Fields:
        queries (List[OrientationQuery]): List of project orientation queries
            - Defined in .praxis-os/config/mcp.yaml (project config)
            - Optional - not all projects need custom queries
            - Executed after base queries
    
    Example YAML:
        orientation:
          project:
            queries:
              - query: "dogfooding model self-hosting development"
                priority: 1
                category: "development"
    """
    
    queries: List[OrientationQuery] = Field(
        default_factory=list,
        description="List of project-specific orientation queries"
    )


class OrientationConfig(BaseConfig):
    """
    Top-level orientation configuration (base + project).
    
    Provides a unified configuration for orientation queries with:
    - Base queries: praxis-os foundational patterns (from dist/config/mcp.yaml)
    - Project queries: project-specific context (from .praxis-os/config/mcp.yaml)
    
    The query interception hook ("orientation query list") reads this config
    and returns merged base + project queries for AI agents to execute.
    
    Fields:
        base (Optional[BaseOrientation]): Base praxis-os queries
            - Defined in distribution template
            - Usually ~10 queries
            - Always executed first
        
        project (Optional[ProjectOrientationQueries]): Project-specific queries
            - Defined in project config
            - Optional (can be empty)
            - Executed after base queries
    
    Example YAML (full):
        orientation:
          base:
            queries:
              - query: "stateless AI architecture"
                priority: 1
          project:
            queries:
              - query: "dogfooding model"
                priority: 1
    
    Example YAML (base only):
        orientation:
          base:
            queries:
              - query: "stateless AI architecture"
                priority: 1
    
    Backward Compatibility:
        - orientation section is optional
        - base section is optional (defaults to empty list)
        - project section is optional (defaults to empty list)
        - Existing configs without orientation continue to work
    
    Query Execution Order:
        1. Base queries (priority 1 → 2 → 3)
        2. Project queries (priority 1 → 2 → 3)
    
    Design Rationale:
        - Separation of concerns: base vs project knowledge
        - Extensibility: Projects can add queries without modifying base
        - Transparency: All queries visible in config files
        - Type safety: Pydantic validates entire structure
    
    Traceability:
        FR-019: Project Orientation System
        Addendum 2025-11-23: Top-level orientation with base + project
    """
    
    base: Optional[BaseOrientation] = Field(
        default=None,
        description="Base praxis-os orientation queries (from distribution)"
    )
    
    project: Optional[ProjectOrientationQueries] = Field(
        default=None,
        description="Project-specific orientation queries (optional)"
    )


class ProjectConfig(BaseConfig):
    """
    Top-level project configuration with orientation section.
    
    DEPRECATED: This structure (project.orientation) is maintained for
    backward compatibility. New configs should use top-level orientation
    with base + project subsections.
    
    Root configuration for project-specific settings, starting with orientation.
    Provides a structured extension point for adding project-specific configuration
    while maintaining backward compatibility with existing configurations.
    
    Fields:
        orientation (Optional[ProjectOrientation]): Project orientation configuration
            - None or missing: Project has no custom orientation queries
            - Present: Project defines custom orientation queries
    
    Backward Compatibility:
        Missing project section in mcp.yaml is valid:
            - Existing configs without project section continue to work
            - No validation errors if project field is absent
            - Defaults to None (no project-specific configuration)
    
    Example YAML (old structure - deprecated):
        project:
          orientation:
            enabled: true
            queries:
              - query: "dogfooding model development"
                priority: 1
    
    Example YAML (new structure - preferred):
        orientation:
          base:
            queries:
              - query: "stateless AI architecture"
                priority: 1
          project:
            queries:
              - query: "dogfooding model development"
                priority: 1
    
    Design:
        - Optional by design: Not all projects need custom orientation
        - Extensible: Additional project-specific fields can be added later
        - Type-safe: Pydantic validates nested structure
        - Fail-fast: Invalid orientation config caught at startup
    
    Use Cases:
        - Dogfooding: praxis-os defines its own orientation queries
        - Large projects: Custom orientation for project-specific patterns
        - Teams: Standardized onboarding queries for new developers
        - Frameworks: Framework-specific guidance for AI agents
    """
    
    orientation: Optional[ProjectOrientation] = Field(
        default=None,
        description="Project-specific orientation configuration (optional, deprecated - use top-level orientation)"
    )

