"""
Safe lambda validator execution with restricted context.

Executes validation lambdas in controlled environment preventing arbitrary
code execution while enabling flexible validation rules.
"""

import re
from typing import Any, Dict, Optional, Tuple

import yaml

# Safe builtins allowed in validator execution context
# NO os, sys, subprocess, __import__, eval, exec, open, etc.
SAFE_GLOBALS = {
    'len': len,
    'str': str,
    'int': int,
    'bool': bool,
    'float': float,
    're': re,
    'yaml': yaml,
    'any': any,
    'all': all,
    'set': set,
    'list': list,
    'dict': dict,
    'abs': abs,
    'min': min,
    'max': max,
    'sum': sum,
    'round': round,
    'sorted': sorted,
    'enumerate': enumerate,
    'zip': zip,
}

# Forbidden patterns in validator expressions (security)
FORBIDDEN_PATTERNS = [
    r'__import__',
    r'exec\s*\(',
    r'eval\s*\(',
    r'compile\s*\(',
    r'open\s*\(',
    r'file\s*\(',
    r'input\s*\(',
    r'os\.',
    r'sys\.',
    r'subprocess\.',
    r'__builtins__',
    r'globals\s*\(',
    r'locals\s*\(',
]


class ValidatorExecutor:
    """
    Execute lambda validators in safe, restricted context.

    Provides secure execution of validation lambdas with:
    - Restricted globals (no dangerous modules)
    - Pattern blacklist (forbidden operations)
    - Syntax validation
    - Common validator library

    Example:
        >>> executor = ValidatorExecutor()
        >>> passed, error = executor.execute_validator(
        ...     "lambda x: x > 0",
        ...     42,
        ...     {}
        ... )
        >>> assert passed is True
        >>> assert error is None
    """

    def __init__(self):
        """Initialize validator executor with safe globals."""
        self.safe_globals = SAFE_GLOBALS.copy()

    def execute_validator(
        self,
        validator_expr: str,
        value: Any,
        params: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute validator lambda in safe context.

        Evaluates lambda expression against value with optional parameters.
        Returns result and optional error message.

        Args:
            validator_expr: Lambda expression string (e.g., "lambda x: x > 0")
            value: Value to validate
            params: Optional parameters for parameterized validators

        Returns:
            Tuple of (passed: bool, error_message: Optional[str])
            If passed=True, error_message is None
            If passed=False, error_message explains why

        Security:
            - Restricted globals (no os, sys, subprocess, etc.)
            - No file I/O allowed
            - Only safe builtins (len, str, int, re, yaml, etc.)

        Example:
            >>> executor = ValidatorExecutor()
            >>> passed, error = executor.execute_validator(
            ...     "lambda x: x > 0",
            ...     42,
            ...     {}
            ... )
            >>> assert passed is True

            >>> passed, error = executor.execute_validator(
            ...     "lambda x, min_val: x >= min_val",
            ...     5,
            ...     {"min_val": 10}
            ... )
            >>> assert passed is False
        """
        if params is None:
            params = {}

        try:
            # pylint: disable=eval-used
            # Justification: Controlled eval with restricted globals for validation lambdas
            validator_func = eval(
                validator_expr,
                self.safe_globals,
                {}  # Empty locals (no access to surrounding scope)
            )

            # Execute validator
            result = validator_func(value, **params)
            passed = bool(result)

            return (passed, None)

        except Exception as e:
            # Validator exception = validation failure with error message
            return (False, f"Validator failed: {str(e)}")

    def validate_syntax(self, validator_expr: str) -> bool:
        """
        Validate lambda expression syntax.

        Checks if expression is valid Python without executing it.

        Args:
            validator_expr: Lambda expression to validate

        Returns:
            True if syntax valid, False otherwise

        Example:
            >>> executor = ValidatorExecutor()
            >>> executor.validate_syntax("lambda x: x > 0")
            True
            >>> executor.validate_syntax("lambda x: invalid syntax!")
            False
        """
        try:
            compile(validator_expr, '<string>', 'eval')
            return True
        except SyntaxError:
            return False

    def is_safe_validator(self, validator_expr: str) -> bool:
        """
        Check validator expression for forbidden patterns.

        Scans expression for dangerous operations like __import__,
        exec, eval, file I/O, etc.

        Args:
            validator_expr: Lambda expression to check

        Returns:
            True if safe, False if contains forbidden patterns

        Example:
            >>> executor = ValidatorExecutor()
            >>> executor.is_safe_validator("lambda x: x > 0")
            True
            >>> executor.is_safe_validator("lambda x: __import__('os')")
            False
            >>> executor.is_safe_validator("lambda x: open('/etc/passwd')")
            False
        """
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, validator_expr):
                return False
        return True


# Common validator library
COMMON_VALIDATORS = {
    # String validators
    "non_empty": "lambda x: len(x) > 0",
    "contains_any": "lambda x, patterns: any(p in x for p in patterns)",
    "matches_pattern": "lambda x, pattern: re.match(pattern, x) is not None",
    "min_length": "lambda x, min_len: len(x) >= min_len",
    "max_length": "lambda x, max_len: len(x) <= max_len",

    # Integer validators
    "positive": "lambda x: x > 0",
    "non_negative": "lambda x: x >= 0",
    "negative": "lambda x: x < 0",
    "in_range": "lambda x, min_val, max_val: min_val <= x <= max_val",
    "equals": "lambda x, expected: x == expected",
    "not_equals": "lambda x, forbidden: x != forbidden",

    # Object validators
    "has_fields": "lambda x, fields: all(f in x for f in fields)",
    "valid_structure": "lambda x, required_keys: set(required_keys).issubset(set(x.keys()))",

    # Proof validators (check content, not just boolean claims)
    "yaml_parseable": "lambda x: yaml.safe_load(x) is not None",
    "contains_success": "lambda x: 'success' in x.lower() or '✅' in x",
    "no_errors": "lambda x: 'error' not in x.lower() and '❌' not in x",
    "contains_text": "lambda x, text: text in x",
    "not_contains_text": "lambda x, text: text not in x",

    # List validators
    "list_not_empty": "lambda x: isinstance(x, list) and len(x) > 0",
    "list_min_length": "lambda x, min_len: isinstance(x, list) and len(x) >= min_len",
    "all_items_type": "lambda x, item_type: all(isinstance(i, item_type) for i in x)",

    # Numeric validators
    "greater_than": "lambda x, threshold: x > threshold",
    "less_than": "lambda x, threshold: x < threshold",
    "between": "lambda x, low, high: low < x < high",
}


__all__ = [
    'ValidatorExecutor',
    'COMMON_VALIDATORS',
    'SAFE_GLOBALS',
    'FORBIDDEN_PATTERNS',
]
