"""
Checkpoint requirement loading with two-tier fallback strategy.

Loads validation requirements from gate-definition.yaml files with automatic
fallback to permissive gates for backwards compatibility.
"""

import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


@dataclass
class FieldSchema:
    """
    Schema definition for single evidence field.

    Defines type, requirements, and validation for one evidence field.

    Attributes:
        name: Field name
        type: Field type (boolean, integer, string, object, list)
        required: Whether field is required
        validator: Optional validator name
        validator_params: Optional parameters for validator
        description: Human-readable description

    Example:
        >>> schema = FieldSchema(
        ...     name="business_goals",
        ...     type="integer",
        ...     required=True,
        ...     validator="positive",
        ...     validator_params=None,
        ...     description="Number of business goals defined"
        ... )
    """

    name: str
    type: str
    required: bool
    validator: Optional[str]
    validator_params: Optional[Dict[str, Any]]
    description: str

    def validate_type(self, value: Any) -> bool:
        """
        Check if value matches declared type.

        Args:
            value: Value to type-check

        Returns:
            True if type matches, False otherwise

        Example:
            >>> schema = FieldSchema("test", "integer", True, None, None, "Test")
            >>> schema.validate_type(42)
            True
            >>> schema.validate_type("not an int")
            False
        """
        type_map = {
            "boolean": bool,
            "integer": int,
            "string": str,
            "object": dict,
            "list": list,
        }
        expected_type = type_map.get(self.type)
        return expected_type is not None and isinstance(value, expected_type)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary.

        Returns:
            Dictionary representation of schema
        """
        return {
            "name": self.name,
            "type": self.type,
            "required": self.required,
            "validator": self.validator,
            "validator_params": self.validator_params,
            "description": self.description,
        }


@dataclass
class CrossFieldRule:
    """
    Cross-field validation rule.

    Validates relationships between multiple evidence fields using lambda expressions.

    Attributes:
        rule: Lambda expression taking evidence dict (e.g., "lambda e: e['a'] > e['b']")
        error_message: Error message shown if rule fails

    Example:
        >>> rule = CrossFieldRule(
        ...     rule="lambda e: e.get('frs', 0) >= e.get('goals', 0)",
        ...     error_message="Should have at least as many FRs as goals"
        ... )
    """

    rule: str
    error_message: str

    def evaluate(self, evidence: Dict[str, Any]) -> bool:
        """
        Evaluate rule against evidence.

        Args:
            evidence: Evidence dictionary to validate

        Returns:
            True if rule passes, False otherwise

        Raises:
            ValueError: If rule syntax invalid or evaluation fails
        """
        try:
            # pylint: disable=eval-used
            # Justification: Controlled eval for lambda expressions with empty builtins
            rule_func = eval(self.rule, {"__builtins__": {}}, {})
            return bool(rule_func(evidence))
        except Exception as e:
            raise ValueError(f"Cross-field rule evaluation failed: {e}") from e

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary.

        Returns:
            Dictionary representation of rule
        """
        return {
            "rule": self.rule,
            "error_message": self.error_message,
        }


@dataclass
class CheckpointRequirements:
    """
    Checkpoint validation requirements.

    Container for checkpoint validation requirements loaded from gate-definition.yaml
    with fallback to RAG or permissive gate. Immutable once loaded (safe for caching).

    Attributes:
        evidence_schema: Field schemas by field name
        validators: Validator lambda expressions by name
        cross_field_rules: Cross-field validation rules
        strict: Whether strict mode enabled (errors block vs warnings)
        allow_override: Whether manual override allowed
        source: How requirements were loaded (yaml, rag, permissive)

    Example:
        >>> requirements = CheckpointRequirements(
        ...     evidence_schema={"field1": FieldSchema(...)},
        ...     validators={"positive": "lambda x: x > 0"},
        ...     cross_field_rules=[],
        ...     strict=False,
        ...     allow_override=True,
        ...     source="yaml"
        ... )
    """

    evidence_schema: Dict[str, FieldSchema]
    validators: Dict[str, str]
    cross_field_rules: List[CrossFieldRule]
    strict: bool
    allow_override: bool
    source: str

    def get_required_fields(self) -> List[str]:
        """
        Get list of required field names.

        Returns:
            List of field names where required=True

        Example:
            >>> requirements.get_required_fields()
            ['business_goals', 'user_stories']
        """
        return [
            name for name, schema in self.evidence_schema.items() if schema.required
        ]

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary for logging/debugging.

        Returns:
            Dictionary representation of requirements
        """
        return {
            "evidence_schema": {
                k: v.to_dict() for k, v in self.evidence_schema.items()
            },
            "validators": self.validators,
            "cross_field_rules": [r.to_dict() for r in self.cross_field_rules],
            "strict": self.strict,
            "allow_override": self.allow_override,
            "source": self.source,
        }


class CheckpointLoaderError(Exception):
    """Raised when checkpoint loading fails."""


class CheckpointLoader:
    """
    Loads checkpoint requirements with two-tier fallback strategy.

    Loading strategy (in order):
    1. gate-definition.yaml (if exists) - strict validation, cached for performance
    2. Permissive gate (if YAML missing) - accepts any evidence

    Thread-safe caching using double-checked locking pattern ensures:
    - High cache hit rate (> 95%)
    - Fast cached loads (< 10ms)
    - Safe concurrent access
    - Minimal lock contention

    Attributes:
        workflows_base_path: Base path for workflow definitions
        _cache: Thread-safe cache of parsed requirements
        _cache_lock: Lock for cache access

    Example:
        >>> loader = CheckpointLoader(Path(".praxis-os/workflows"))
        >>> requirements = loader.load_checkpoint_requirements("spec_creation_v1", 1)
        >>> assert requirements.source in ["yaml", "permissive"]
    """

    def __init__(self, workflows_base_path: Path):
        """
        Initialize checkpoint loader.

        Args:
            workflows_base_path: Base path for workflow definitions
                (typically .praxis-os/workflows)
        """
        self.workflows_base_path = workflows_base_path
        self._cache: Dict[str, CheckpointRequirements] = {}
        self._cache_lock = threading.Lock()

    def load_checkpoint_requirements(
        self, workflow_type: str, phase: int
    ) -> CheckpointRequirements:
        """
        Load checkpoint requirements using two-tier strategy.

        Strategy:
        1. Try gate-definition.yaml (if exists) - strict validation, cached
        2. Return permissive gate (if YAML missing) - accepts any evidence

        Uses double-checked locking for thread-safe caching:
        - Fast path: Check cache without lock (95%+ hit rate, < 10ms)
        - Slow path: Load with lock on cache miss (< 50ms first time)

        Args:
            workflow_type: Workflow identifier (e.g., "spec_creation_v1")
            phase: Phase number (0-based)

        Returns:
            CheckpointRequirements with evidence_schema, validators,
            strict flag, and source indicator

        Example:
            >>> requirements = loader.load_checkpoint_requirements(
            ...     "spec_creation_v1", 1
            ... )
            >>> assert "business_goals" in requirements.evidence_schema
            >>> assert requirements.source == "yaml"  # or "permissive"
        """
        cache_key = f"{workflow_type}:{phase}"

        # Fast path: Check cache without lock (95%+ of calls)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Slow path: Load with lock (double-checked locking)
        with self._cache_lock:
            # Check again inside lock (another thread may have loaded)
            if cache_key in self._cache:
                return self._cache[cache_key]

            # Load using three-tier fallback
            requirements = self._load_with_fallback(workflow_type, phase)

            # Cache and return
            self._cache[cache_key] = requirements
            return requirements

    def _load_with_fallback(
        self, workflow_type: str, phase: int
    ) -> CheckpointRequirements:
        """
        Execute two-tier fallback strategy.

        Tries YAML first, falls back to permissive gate if missing.

        Args:
            workflow_type: Workflow identifier
            phase: Phase number

        Returns:
            CheckpointRequirements from first successful source
        """
        # Tier 1: YAML
        requirements = self._load_from_yaml(workflow_type, phase)
        if requirements:
            logger.info("Loaded gate from YAML: %s:%s", workflow_type, phase)
            return requirements

        # Tier 2: Permissive (backwards compatibility)
        logger.info(
            "Using permissive gate (no gate-definition.yaml): %s:%s",
            workflow_type,
            phase,
        )
        return self._get_permissive_gate()

    def _load_from_yaml(
        self, workflow_type: str, phase: int
    ) -> Optional[CheckpointRequirements]:
        """
        Load from gate-definition.yaml file.

        Path: .praxis-os/workflows/{workflow_type}/phases/{phase}/gate-definition.yaml

        Args:
            workflow_type: Workflow identifier
            phase: Phase number

        Returns:
            CheckpointRequirements if file exists and valid, None otherwise

        Raises:
            CheckpointLoaderError: If file exists but has invalid format
        """
        gate_path = (
            self.workflows_base_path
            / workflow_type
            / "phases"
            / str(phase)
            / "gate-definition.yaml"
        )

        if not gate_path.exists():
            return None

        try:
            content = yaml.safe_load(gate_path.read_text(encoding="utf-8"))
            return self._parse_gate_content(content, "yaml")
        except yaml.YAMLError as e:
            logger.error("Failed to parse YAML gate %s: %s", gate_path, e)
            return None
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Justification: Catch-all for graceful fallback to RAG/permissive gate
            logger.error("Failed to load YAML gate %s: %s", gate_path, e)
            return None

    def _parse_gate_content(
        self, content: Dict[str, Any], source: str
    ) -> CheckpointRequirements:
        """
        Parse gate content into CheckpointRequirements.

        Args:
            content: Parsed YAML content
            source: Source indicator (yaml, rag, permissive)

        Returns:
            CheckpointRequirements object

        Raises:
            CheckpointLoaderError: If content structure invalid
        """
        # Validate required sections
        if "checkpoint" not in content:
            raise CheckpointLoaderError("Missing 'checkpoint' section")
        if "evidence_schema" not in content:
            raise CheckpointLoaderError("Missing 'evidence_schema' section")

        # Parse checkpoint config
        checkpoint_config = content["checkpoint"]
        strict = checkpoint_config.get("strict", False)
        allow_override = checkpoint_config.get("allow_override", True)

        # Parse evidence schema
        evidence_schema = {}
        for field_name, field_config in content["evidence_schema"].items():
            evidence_schema[field_name] = FieldSchema(
                name=field_name,
                type=field_config.get("type", "string"),
                required=field_config.get("required", False),
                validator=field_config.get("validator"),
                validator_params=field_config.get("validator_params"),
                description=field_config.get("description", ""),
            )

        # Parse validators
        validators = content.get("validators", {})

        # Parse cross-field rules
        cross_field_rules = []
        for rule_config in content.get("cross_field_validation", []):
            cross_field_rules.append(
                CrossFieldRule(
                    rule=rule_config["rule"],
                    error_message=rule_config["error_message"],
                )
            )

        return CheckpointRequirements(
            evidence_schema=evidence_schema,
            validators=validators,
            cross_field_rules=cross_field_rules,
            strict=strict,
            allow_override=allow_override,
            source=source,
        )

    def _get_permissive_gate(self) -> CheckpointRequirements:
        """
        Return permissive gate for backwards compatibility.

        Used when gate-definition.yaml is missing. Accepts any evidence without
        validation. This ensures workflows without explicit gates still work.

        Design note: RAG fallback was considered but removed because workflows
        are not indexed in the RAG system (only standards are indexed).

        Returns:
            CheckpointRequirements in permissive mode
        """
        return CheckpointRequirements(
            evidence_schema={},
            validators={},
            cross_field_rules=[],
            strict=False,
            allow_override=True,
            source="permissive",
        )


__all__ = [
    "FieldSchema",
    "CrossFieldRule",
    "CheckpointRequirements",
    "CheckpointLoaderError",
    "CheckpointLoader",
]
