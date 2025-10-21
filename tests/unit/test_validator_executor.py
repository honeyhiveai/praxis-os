"""
Unit tests for ValidatorExecutor.

Tests safe lambda execution, security features, and common validators.
"""

import pytest

from mcp_server.validation.validator_executor import (
    COMMON_VALIDATORS,
    FORBIDDEN_PATTERNS,
    SAFE_GLOBALS,
    ValidatorExecutor,
)


class TestValidatorExecutor:
    """Tests for ValidatorExecutor class."""

    @pytest.fixture
    def executor(self):
        """Create ValidatorExecutor instance."""
        return ValidatorExecutor()

    def test_execute_simple_validator_pass(self, executor):
        """Test simple validator that passes."""
        passed, error = executor.execute_validator("lambda x: x > 0", 42, {})

        assert passed is True
        assert error is None

    def test_execute_simple_validator_fail(self, executor):
        """Test simple validator that fails."""
        passed, error = executor.execute_validator("lambda x: x > 0", -5, {})

        assert passed is False
        assert error is None  # Validation failed but no exception

    def test_execute_validator_with_params(self, executor):
        """Test validator with parameters."""
        passed, error = executor.execute_validator(
            "lambda x, min_val, max_val: min_val <= x <= max_val",
            50,
            {"min_val": 1, "max_val": 100},
        )

        assert passed is True
        assert error is None

    def test_execute_validator_params_fail(self, executor):
        """Test validator with parameters that fails."""
        passed, error = executor.execute_validator(
            "lambda x, min_val: x >= min_val", 5, {"min_val": 10}
        )

        assert passed is False
        assert error is None

    def test_execute_validator_string_operations(self, executor):
        """Test validator with string operations."""
        passed, error = executor.execute_validator(
            "lambda x: len(x) > 5", "hello world", {}
        )

        assert passed is True
        assert error is None

    def test_execute_validator_regex(self, executor):
        """Test validator using regex."""
        passed, error = executor.execute_validator(
            "lambda x: re.match(r'^[a-z]+$', x) is not None", "hello", {}
        )

        assert passed is True
        assert error is None

    def test_execute_validator_yaml_parsing(self, executor):
        """Test validator that parses YAML."""
        yaml_content = """
key: value
list:
  - item1
  - item2
"""
        passed, error = executor.execute_validator(
            "lambda x: yaml.safe_load(x) is not None", yaml_content, {}
        )

        assert passed is True
        assert error is None

    def test_execute_validator_exception_handling(self, executor):
        """Test validator that raises exception."""
        # Lambda tries to access non-existent key
        passed, error = executor.execute_validator(
            "lambda x: x['nonexistent'] > 0", {"existing": 42}, {}
        )

        assert passed is False
        assert error is not None
        assert "Validator failed" in error

    def test_execute_validator_invalid_syntax_raises(self, executor):
        """Test validator with invalid syntax raises error."""
        passed, error = executor.execute_validator("lambda x: invalid syntax!", 42, {})

        assert passed is False
        assert error is not None
        assert "Validator failed" in error

    def test_execute_validator_no_params_provided(self, executor):
        """Test validator with None params (defaults to empty dict)."""
        passed, error = executor.execute_validator(
            "lambda x: x > 0", 42, None  # Should default to {}
        )

        assert passed is True
        assert error is None

    def test_validate_syntax_valid(self, executor):
        """Test syntax validation for valid lambda."""
        assert executor.validate_syntax("lambda x: x > 0") is True
        assert executor.validate_syntax("lambda x, y: x + y") is True
        assert executor.validate_syntax("lambda x: len(x) > 5") is True

    def test_validate_syntax_invalid(self, executor):
        """Test syntax validation for invalid lambda."""
        assert executor.validate_syntax("lambda x: invalid!") is False
        assert executor.validate_syntax("not a lambda") is False
        assert executor.validate_syntax("lambda x:") is False

    def test_is_safe_validator_safe_expressions(self, executor):
        """Test safety check for safe expressions."""
        safe_validators = [
            "lambda x: x > 0",
            "lambda x: len(x) > 5",
            "lambda x: re.match(r'pattern', x)",
            "lambda x: yaml.safe_load(x)",
            "lambda x, y: x + y",
        ]

        for validator in safe_validators:
            assert executor.is_safe_validator(validator) is True

    def test_is_safe_validator_forbidden_import(self, executor):
        """Test safety check catches __import__."""
        dangerous_validators = [
            "lambda x: __import__('os').system('rm -rf /')",
            "lambda x: __import__('sys').exit()",
        ]

        for validator in dangerous_validators:
            assert executor.is_safe_validator(validator) is False

    def test_is_safe_validator_forbidden_exec(self, executor):
        """Test safety check catches exec/eval."""
        dangerous_validators = [
            "lambda x: exec('malicious code')",
            "lambda x: eval('dangerous')",
        ]

        for validator in dangerous_validators:
            assert executor.is_safe_validator(validator) is False

    def test_is_safe_validator_forbidden_open(self, executor):
        """Test safety check catches file operations."""
        dangerous_validators = [
            "lambda x: open('/etc/passwd').read()",
            "lambda x: file('/etc/passwd')",
        ]

        for validator in dangerous_validators:
            assert executor.is_safe_validator(validator) is False

    def test_is_safe_validator_forbidden_os_sys(self, executor):
        """Test safety check catches os/sys access."""
        dangerous_validators = [
            "lambda x: os.listdir('/')",
            "lambda x: sys.exit()",
            "lambda x: subprocess.run(['ls'])",
        ]

        for validator in dangerous_validators:
            assert executor.is_safe_validator(validator) is False

    def test_is_safe_validator_forbidden_builtins(self, executor):
        """Test safety check catches __builtins__ access."""
        dangerous_validators = [
            "lambda x: __builtins__['eval']('code')",
            "lambda x: globals()",
            "lambda x: locals()",
        ]

        for validator in dangerous_validators:
            assert executor.is_safe_validator(validator) is False

    def test_safe_globals_contains_expected(self):
        """Test SAFE_GLOBALS contains expected safe functions."""
        assert "len" in SAFE_GLOBALS
        assert "str" in SAFE_GLOBALS
        assert "re" in SAFE_GLOBALS
        assert "yaml" in SAFE_GLOBALS
        assert "any" in SAFE_GLOBALS
        assert "all" in SAFE_GLOBALS

    def test_safe_globals_excludes_dangerous(self):
        """Test SAFE_GLOBALS excludes dangerous modules."""
        assert "os" not in SAFE_GLOBALS
        assert "sys" not in SAFE_GLOBALS
        assert "subprocess" not in SAFE_GLOBALS
        assert "__import__" not in SAFE_GLOBALS
        assert "eval" not in SAFE_GLOBALS
        assert "exec" not in SAFE_GLOBALS

    def test_forbidden_patterns_coverage(self):
        """Test FORBIDDEN_PATTERNS covers key security threats."""
        assert any("__import__" in p for p in FORBIDDEN_PATTERNS)
        assert any("exec" in p for p in FORBIDDEN_PATTERNS)
        assert any("eval" in p for p in FORBIDDEN_PATTERNS)
        assert any("open" in p for p in FORBIDDEN_PATTERNS)
        assert any("os\\." in p for p in FORBIDDEN_PATTERNS)
        assert any("sys\\." in p for p in FORBIDDEN_PATTERNS)


class TestCommonValidators:
    """Tests for COMMON_VALIDATORS library."""

    @pytest.fixture
    def executor(self):
        """Create ValidatorExecutor instance."""
        return ValidatorExecutor()

    def test_common_validators_exist(self):
        """Test common validators are defined."""
        expected_validators = [
            "non_empty",
            "contains_any",
            "positive",
            "in_range",
            "yaml_parseable",
            "contains_success",
            "no_errors",
        ]

        for validator_name in expected_validators:
            assert validator_name in COMMON_VALIDATORS

    def test_positive_validator(self, executor):
        """Test 'positive' common validator."""
        validator_expr = COMMON_VALIDATORS["positive"]

        # Positive number
        passed, _ = executor.execute_validator(validator_expr, 42, {})
        assert passed is True

        # Zero
        passed, _ = executor.execute_validator(validator_expr, 0, {})
        assert passed is False

        # Negative
        passed, _ = executor.execute_validator(validator_expr, -5, {})
        assert passed is False

    def test_non_empty_validator(self, executor):
        """Test 'non_empty' common validator."""
        validator_expr = COMMON_VALIDATORS["non_empty"]

        # Non-empty string
        passed, _ = executor.execute_validator(validator_expr, "hello", {})
        assert passed is True

        # Empty string
        passed, _ = executor.execute_validator(validator_expr, "", {})
        assert passed is False

    def test_in_range_validator(self, executor):
        """Test 'in_range' common validator."""
        validator_expr = COMMON_VALIDATORS["in_range"]

        # In range
        passed, _ = executor.execute_validator(
            validator_expr, 50, {"min_val": 1, "max_val": 100}
        )
        assert passed is True

        # Below range
        passed, _ = executor.execute_validator(
            validator_expr, 0, {"min_val": 1, "max_val": 100}
        )
        assert passed is False

        # Above range
        passed, _ = executor.execute_validator(
            validator_expr, 101, {"min_val": 1, "max_val": 100}
        )
        assert passed is False

    def test_yaml_parseable_validator(self, executor):
        """Test 'yaml_parseable' common validator."""
        validator_expr = COMMON_VALIDATORS["yaml_parseable"]

        # Valid YAML
        passed, _ = executor.execute_validator(
            validator_expr, "key: value\nlist:\n  - item1", {}
        )
        assert passed is True

        # Invalid YAML
        passed, _ = executor.execute_validator(
            validator_expr, "invalid: yaml: syntax:", {}
        )
        assert passed is False

    def test_contains_success_validator(self, executor):
        """Test 'contains_success' common validator."""
        validator_expr = COMMON_VALIDATORS["contains_success"]

        # Contains "success"
        passed, _ = executor.execute_validator(
            validator_expr, "The operation was a success", {}
        )
        assert passed is True

        # Contains ✅
        passed, _ = executor.execute_validator(validator_expr, "Test passed ✅", {})
        assert passed is True

        # No success indicator
        passed, _ = executor.execute_validator(validator_expr, "Operation failed", {})
        assert passed is False

    def test_no_errors_validator(self, executor):
        """Test 'no_errors' common validator."""
        validator_expr = COMMON_VALIDATORS["no_errors"]

        # No errors
        passed, _ = executor.execute_validator(
            validator_expr, "All tests passed successfully", {}
        )
        assert passed is True

        # Contains "error"
        passed, _ = executor.execute_validator(
            validator_expr, "Test failed with error", {}
        )
        assert passed is False

        # Contains ❌
        passed, _ = executor.execute_validator(validator_expr, "Test failed ❌", {})
        assert passed is False

    def test_has_fields_validator(self, executor):
        """Test 'has_fields' common validator."""
        validator_expr = COMMON_VALIDATORS["has_fields"]

        # Has all fields
        passed, _ = executor.execute_validator(
            validator_expr,
            {"name": "test", "value": 42, "status": "ok"},
            {"fields": ["name", "value"]},
        )
        assert passed is True

        # Missing field
        passed, _ = executor.execute_validator(
            validator_expr, {"name": "test"}, {"fields": ["name", "value"]}
        )
        assert passed is False

    def test_list_not_empty_validator(self, executor):
        """Test 'list_not_empty' common validator."""
        validator_expr = COMMON_VALIDATORS["list_not_empty"]

        # Non-empty list
        passed, _ = executor.execute_validator(validator_expr, [1, 2, 3], {})
        assert passed is True

        # Empty list
        passed, _ = executor.execute_validator(validator_expr, [], {})
        assert passed is False

        # Not a list
        passed, _ = executor.execute_validator(validator_expr, "not a list", {})
        assert passed is False

    def test_all_common_validators_safe(self, executor):
        """Test all common validators pass safety check."""
        for name, validator_expr in COMMON_VALIDATORS.items():
            assert (
                executor.is_safe_validator(validator_expr) is True
            ), f"Common validator '{name}' failed safety check"

    def test_all_common_validators_valid_syntax(self, executor):
        """Test all common validators have valid syntax."""
        for name, validator_expr in COMMON_VALIDATORS.items():
            assert (
                executor.validate_syntax(validator_expr) is True
            ), f"Common validator '{name}' has invalid syntax"
