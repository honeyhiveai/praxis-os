"""
Input validation functions for workflow tools.

Provides security and data integrity validation for workflow operations.
"""

import json
import os
import re
from typing import Any, Dict

from .constants import MAX_EVIDENCE_SIZE, SESSION_ID_PATTERN


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.

    Ensures session ID is properly formatted to prevent injection attacks
    and invalid session lookups.

    Args:
        session_id: Session identifier to validate

    Returns:
        True if valid

    Raises:
        ValueError: If session ID is invalid or malformed

    Examples:
        >>> validate_session_id("550e8400-e29b-41d4-a716-446655440000")
        True
        >>> validate_session_id("invalid")
        ValueError: Invalid session_id format
    """
    if not session_id:
        raise ValueError("session_id is required")

    if not isinstance(session_id, str):
        raise ValueError("session_id must be a string")

    if not re.match(SESSION_ID_PATTERN, session_id):
        raise ValueError(
            f"Invalid session_id format: must be UUID format (36 chars, "
            f"lowercase hex with hyphens)"
        )

    return True


def validate_target_file(target_file: str) -> bool:
    """
    Validate target file path to prevent directory traversal attacks.

    Ensures file path does not escape workspace using .. or absolute paths.
    Critical for security to prevent access to system files.

    Args:
        target_file: File path to validate

    Returns:
        True if valid

    Raises:
        ValueError: If path is invalid or attempts directory traversal

    Examples:
        >>> validate_target_file("src/module.py")
        True
        >>> validate_target_file("../../../etc/passwd")
        ValueError: Invalid target_file: directory traversal detected
    """
    if not target_file:
        raise ValueError("target_file is required")

    if not isinstance(target_file, str):
        raise ValueError("target_file must be a string")

    # Check for null bytes (potential injection)
    if "\x00" in target_file:
        raise ValueError("Invalid target_file: null byte detected")

    # Check for command injection attempts (semicolon, pipe, backtick)
    dangerous_chars = [";", "|", "`", "$", "&", ">", "<"]
    if any(char in target_file for char in dangerous_chars):
        raise ValueError("Invalid target_file: potentially dangerous characters detected")

    # Check for URL encoding attacks
    if "%" in target_file:
        import urllib.parse
        decoded = urllib.parse.unquote(target_file)
        # If decoded version has dangerous patterns, reject
        if ".." in decoded or any(char in decoded for char in ["/", "\\"]):
            raise ValueError("Invalid target_file: URL encoding attack detected")

    # Normalize path to resolve any . or .. components
    norm_path = os.path.normpath(target_file)

    # Check for directory traversal attempts
    if ".." in norm_path or norm_path.startswith("/"):
        raise ValueError(
            "Invalid target_file: directory traversal detected (.. or absolute path)"
        )

    # Check for Windows-style absolute paths (even on Unix)
    if len(norm_path) > 1 and norm_path[1] == ":" and norm_path[0].isalpha():
        raise ValueError("Invalid target_file: absolute path detected (Windows-style)")

    # Ensure resolved path stays within workspace
    workspace = os.getcwd()
    full_path = os.path.abspath(os.path.join(workspace, norm_path))

    if not full_path.startswith(workspace):
        raise ValueError("Invalid target_file: resolves outside workspace")

    return True


def validate_evidence_size(evidence: Dict[str, Any]) -> bool:
    """
    Validate evidence dictionary size to prevent memory exhaustion.

    Enforces 10MB limit on evidence JSON to prevent DoS attacks and
    excessive memory usage.

    Args:
        evidence: Evidence dictionary to validate

    Returns:
        True if valid

    Raises:
        ValueError: If evidence exceeds size limit

    Examples:
        >>> validate_evidence_size({"test": "data"})
        True
        >>> validate_evidence_size({"data": "x" * (11 * 1024 * 1024)})
        ValueError: Evidence too large
    """
    if not evidence:
        return True

    if not isinstance(evidence, dict):
        raise ValueError("evidence must be a dictionary")

    # Serialize to JSON and check size
    try:
        evidence_json = json.dumps(evidence)
        size_bytes = len(evidence_json.encode("utf-8"))

        if size_bytes > MAX_EVIDENCE_SIZE:
            size_mb = size_bytes / (1024 * 1024)
            limit_mb = MAX_EVIDENCE_SIZE / (1024 * 1024)
            raise ValueError(
                f"Evidence too large: {size_mb:.2f}MB exceeds limit of {limit_mb}MB"
            )

        return True

    except (TypeError, ValueError) as e:
        if "too large" in str(e).lower():
            raise
        raise ValueError(f"Evidence is not JSON-serializable: {e}") from e

