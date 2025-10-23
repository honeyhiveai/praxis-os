"""
Constants for consolidated workflow management tool.
"""

# Valid workflow actions
VALID_ACTIONS = {
    "list_workflows", "start", "get_phase", "get_task", "complete_phase",
    "get_state", "list_sessions", "get_session", "delete_session",
    "pause", "resume", "retry_phase", "rollback", "get_errors"
}

# Security and validation constants
MAX_EVIDENCE_SIZE = 10 * 1024 * 1024  # 10 MB
SESSION_ID_PATTERN = r"^[a-f0-9\-]{36}$"  # UUID format

