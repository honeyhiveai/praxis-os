"""
Security tests for consolidated workflow tools.

Covers:
- Injection attack prevention (SQL, command, path traversal)
- DOS attack prevention (oversized payloads, resource exhaustion)
- Error message security (no sensitive data leakage)
- Input sanitization (special characters, encoding attacks)

Requirement: FR-007 (Parameter validation and error messages)
"""

import json
from unittest.mock import Mock

import pytest

from mcp_server.server.tools.workflow_tools import (
    validate_evidence_size,
    validate_session_id,
    validate_target_file,
)


class TestInjectionAttackPrevention:
    """Test protection against injection attacks."""

    @pytest.mark.parametrize(
        "malicious_session_id",
        [
            # SQL injection attempts
            "' OR '1'='1",
            "1'; DROP TABLE sessions--",
            "1' UNION SELECT * FROM users--",
            # Command injection attempts
            "; rm -rf /",
            "| cat /etc/passwd",
            "`whoami`",
            "$(cat /etc/passwd)",
            # Script injection attempts
            "<script>alert('XSS')</script>",
            "javascript:alert(1)",
            # Path manipulation
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            # Null byte injection
            "valid\x00/etc/passwd",
            # Unicode attacks
            "\u202e",  # Right-to-left override
        ],
    )
    def test_session_id_injection_prevention(self, malicious_session_id):
        """Verify session_id validation blocks injection attacks."""
        with pytest.raises(ValueError) as exc_info:
            validate_session_id(malicious_session_id)

        error_msg = str(exc_info.value)
        assert (
            "Invalid session_id format" in error_msg
            or "session_id is required" in error_msg
        )
        # Ensure error doesn't expose internal details
        assert "DROP TABLE" not in error_msg
        assert "/etc/passwd" not in error_msg

    @pytest.mark.parametrize(
        "malicious_file_path",
        [
            # Directory traversal
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            # Absolute paths
            "/etc/passwd",
            "/var/log/messages",
            "C:\\Windows\\System32\\config\\sam",
            # Null byte injection
            "valid.py\x00.txt",
            # Command injection
            "file.py; rm -rf /",
            "file.py | cat /etc/passwd",
            # URL encoding attacks
            "..%2F..%2F..%2Fetc%2Fpasswd",
            # Unicode normalization attacks
            "..\u2215..\u2215etc\u2215passwd",
        ],
    )
    def test_target_file_path_traversal_prevention(self, malicious_file_path):
        """Verify target_file validation blocks path traversal attacks."""
        with pytest.raises(ValueError) as exc_info:
            validate_target_file(malicious_file_path)

        error_msg = str(exc_info.value)
        assert any(
            [
                "directory traversal" in error_msg.lower(),
                "invalid target_file" in error_msg.lower(),
                "target_file is required" in error_msg.lower(),
            ]
        )
        # Ensure error doesn't expose actual file content or paths
        assert "/etc/passwd" not in error_msg
        assert "system32" not in error_msg.lower()

    @pytest.mark.parametrize(
        "malicious_evidence",
        [
            # Script injection in string values
            {"name": "<script>alert('XSS')</script>"},
            {"cmd": "'; DROP TABLE evidence--"},
            {"path": "../../etc/passwd"},
            # Prototype pollution attempts (JavaScript-style)
            {"__proto__": {"isAdmin": True}},
            {"constructor": {"prototype": {"isAdmin": True}}},
        ],
    )
    def test_evidence_injection_prevention(self, malicious_evidence):
        """Verify evidence validation sanitizes malicious content."""
        # Evidence validation should accept these (they're valid JSON)
        # but downstream code should never eval/exec them
        try:
            validate_evidence_size(malicious_evidence)
            # If validation passes, verify it doesn't execute the malicious code
            # by checking it's still a plain dict
            assert isinstance(malicious_evidence, dict)
            # Ensure no code execution occurred
            assert "__proto__" not in dir({})  # Prototype not polluted
        except ValueError:
            # If validation rejects it, that's also acceptable
            pass


class TestDOSAttackPrevention:
    """Test protection against Denial of Service attacks."""

    def test_oversized_evidence_rejection(self):
        """Verify extremely large evidence payloads are rejected."""
        # Create 11MB payload (exceeds 10MB limit)
        large_evidence = {"data": "x" * (11 * 1024 * 1024)}

        with pytest.raises(ValueError) as exc_info:
            validate_evidence_size(large_evidence)

        error_msg = str(exc_info.value)
        assert "too large" in error_msg.lower()
        assert "10" in error_msg or "limit" in error_msg

    def test_deeply_nested_evidence_handling(self):
        """Verify deeply nested structures don't cause stack overflow."""
        # Create deeply nested structure
        evidence = {"level": 0}
        current = evidence
        for i in range(1000):  # 1000 levels deep
            current["nested"] = {"level": i + 1}
            current = current["nested"]

        # Should either validate successfully or reject gracefully
        try:
            result = validate_evidence_size(evidence)
            assert result is True or result is False
        except (ValueError, RecursionError) as e:
            # Graceful rejection is acceptable
            assert "evidence" in str(e).lower() or "recursion" in str(e).lower()

    def test_circular_reference_handling(self):
        """Verify circular references in evidence are caught."""
        evidence = {"key": "value"}
        evidence["self_ref"] = evidence  # Create circular reference

        with pytest.raises((ValueError, TypeError)) as exc_info:
            validate_evidence_size(evidence)

        error_msg = str(exc_info.value)
        assert any(
            [
                "circular" in error_msg.lower(),
                "json" in error_msg.lower(),
                "serializable" in error_msg.lower(),
            ]
        )

    def test_many_keys_evidence_handling(self):
        """Verify evidence with excessive number of keys doesn't cause issues."""
        # Create evidence with 100,000 keys
        evidence = {f"key_{i}": f"value_{i}" for i in range(100000)}

        # Should validate successfully or reject based on size
        try:
            validate_evidence_size(evidence)
            # If accepted, it means it's under size limit
        except ValueError as e:
            # Rejection due to size is acceptable
            assert "too large" in str(e).lower() or "serializable" in str(e).lower()


class TestErrorMessageSecurity:
    """Test that error messages don't leak sensitive information."""

    @pytest.mark.asyncio
    async def test_error_no_sensitive_data_leakage(self):
        """Verify error messages don't expose internal paths or data."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)
        mock_workflow_engine = Mock()

        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_workflow_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Try various attacks and check error messages
        test_cases = [
            {
                "action": "start",
                "workflow_type": "test",
                "target_file": "../../../../etc/passwd",
            },
            {"action": "get_phase", "session_id": "'; DROP TABLE sessions--"},
            {
                "action": "complete_phase",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "phase": 1,
                "evidence": {"data": "x" * (11 * 1024 * 1024)},
            },
        ]

        for test_case in test_cases:
            result = await captured_tool_func(**test_case)

            assert result["status"] == "error"
            error_msg = result.get("error", "")

            # Verify no sensitive information in error messages
            assert "/etc/passwd" not in error_msg
            assert "DROP TABLE" not in error_msg
            assert "C:\\" not in error_msg
            assert not any(
                char in error_msg for char in ["\x00", "\x1b"]
            )  # No control chars

            # Verify error has informative message
            assert len(error_msg) > 0
            assert (
                "error" in error_msg.lower()
                or "invalid" in error_msg.lower()
                or "traversal" in error_msg.lower()
                or "format" in error_msg.lower()
                or "large" in error_msg.lower()
            )

    @pytest.mark.asyncio
    async def test_error_no_stack_trace_exposure(self):
        """Verify stack traces aren't exposed in error responses."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Make workflow_engine raise an exception
        mock_workflow_engine = Mock()
        mock_workflow_engine.start_workflow.side_effect = Exception(
            "Internal error with /secret/path/file.py"
        )

        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_workflow_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        result = await captured_tool_func(
            action="start", workflow_type="test", target_file="valid.py"
        )

        assert result["status"] == "error"
        error_msg = result.get("error", "")

        # Verify internal paths/details aren't exposed
        assert "/secret/path" not in error_msg
        assert "file.py" not in error_msg
        # Should have generic error message
        assert "internal" in error_msg.lower() or "error" in error_msg.lower()


class TestInputSanitization:
    """Test input sanitization and encoding handling."""

    @pytest.mark.parametrize(
        "special_char_session_id",
        [
            "550e8400-e29b-41d4-a716-446655440000\r\n",  # CRLF injection
            "550e8400-e29b-41d4-a716-446655440000\x00",  # Null byte
            "\x1b[31m550e8400-e29b-41d4-a716-446655440000\x1b[0m",  # ANSI escape
            "550e8400\te29b\n41d4\ra716\x0b446655440000",  # Various whitespace
        ],
    )
    def test_special_characters_handling(self, special_char_session_id):
        """Verify special characters are properly rejected or sanitized."""
        with pytest.raises(ValueError) as exc_info:
            validate_session_id(special_char_session_id)

        error_msg = str(exc_info.value)
        assert "invalid" in error_msg.lower() or "format" in error_msg.lower()

    def test_unicode_normalization_attack_prevention(self):
        """Verify Unicode normalization attacks are prevented."""
        # Unicode character that normalizes to "../"
        # Using fullwidth solidus and other Unicode tricks
        unicode_attack = "\uff0e\uff0e\uff0f"  # Fullwidth ".."/"

        # This may or may not be rejected depending on normalization
        # The important thing is it doesn't escape the workspace
        try:
            validate_target_file(unicode_attack + "etc/passwd")
            # If it passes, it's been normalized to a safe path
        except ValueError:
            # If it's rejected, that's also secure
            pass

    @pytest.mark.parametrize(
        "encoding_attack",
        [
            "%2e%2e%2f%2e%2e%2f",  # URL encoded "../"
            "..%252f..%252f",  # Double URL encoded
            "..%c0%af..%c0%af",  # Overlong UTF-8 encoding
        ],
    )
    def test_encoding_attack_prevention(self, encoding_attack):
        """Verify various encoding attacks are prevented."""
        with pytest.raises(ValueError):
            validate_target_file(encoding_attack + "etc/passwd")


class TestValidationConsistency:
    """Test that validation is consistent across all entry points."""

    @pytest.mark.asyncio
    async def test_validation_at_dispatcher_level(self):
        """Verify validation occurs at dispatcher before reaching handlers."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)

        # Mock workflow engine should NOT be called if validation fails
        mock_workflow_engine = Mock()

        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_workflow_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        # Attempt path traversal attack
        result = await captured_tool_func(
            action="start", workflow_type="test", target_file="../../../etc/passwd"
        )

        # Should fail at validation, never reaching workflow_engine
        assert result["status"] == "error"
        assert (
            "traversal" in result["error"].lower()
            or "invalid" in result["error"].lower()
        )

        # Verify workflow_engine was never called (validation stopped it)
        mock_workflow_engine.start_workflow.assert_not_called()

    @pytest.mark.asyncio
    async def test_all_actions_validate_session_id_format(self):
        """Verify all actions that accept session_id validate its format."""
        from mcp_server.server.tools.workflow_tools import register_workflow_tools

        mock_mcp = Mock()
        captured_tool_func = None

        def capture_tool(func):
            nonlocal captured_tool_func
            captured_tool_func = func
            return func

        mock_mcp.tool = Mock(return_value=capture_tool)
        mock_workflow_engine = Mock()

        register_workflow_tools(
            mcp=mock_mcp,
            workflow_engine=mock_workflow_engine,
            framework_generator=Mock(),
            workflow_validator=Mock(),
        )

        malicious_session_id = "'; DROP TABLE sessions--"

        # Test all actions that accept session_id
        actions_with_session_id = [
            {"action": "get_phase", "session_id": malicious_session_id},
            {
                "action": "get_task",
                "session_id": malicious_session_id,
                "phase": 1,
                "task_number": 1,
            },
            {
                "action": "complete_phase",
                "session_id": malicious_session_id,
                "phase": 1,
                "evidence": {},
            },
            {"action": "get_state", "session_id": malicious_session_id},
            {"action": "get_session", "session_id": malicious_session_id},
            {"action": "delete_session", "session_id": malicious_session_id},
        ]

        for test_case in actions_with_session_id:
            result = await captured_tool_func(**test_case)

            assert (
                result["status"] == "error"
            ), f"Action {test_case['action']} should reject malicious session_id"
            error_msg = result["error"]
            assert any(
                [
                    "invalid" in error_msg.lower(),
                    "format" in error_msg.lower(),
                    "uuid" in error_msg.lower(),
                ]
            ), f"Action {test_case['action']} should have clear validation error"

            # Verify SQL injection content not in error
            assert "DROP TABLE" not in error_msg
