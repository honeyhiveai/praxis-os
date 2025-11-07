"""
Unit tests for ouroboros.utils.logging.

Tests structured logging including:
    - JSONFormatter
    - StructuredLogger
    - get_logger() function
    - Behavioral event logging
"""

import json
import logging
import tempfile
from pathlib import Path

import pytest
from ouroboros.utils.logging import JSONFormatter, StructuredLogger, get_logger


class TestJSONFormatter:
    """Test JSONFormatter for structured logging."""

    def test_json_formatter_basic_message(self):
        """JSONFormatter should format basic log messages as JSON."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        data = json.loads(output)

        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "Test message"
        assert "timestamp" in data

    def test_json_formatter_with_extra_fields(self):
        """JSONFormatter should include extra fields in JSON output."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        # Add extra fields
        record.session_id = "abc123"
        record.query = "How does X work?"

        output = formatter.format(record)
        data = json.loads(output)

        assert data["session_id"] == "abc123"
        assert data["query"] == "How does X work?"

    def test_json_formatter_parseable(self):
        """JSONFormatter output should be valid JSON."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)
        # Should not raise
        data = json.loads(output)
        assert isinstance(data, dict)


class TestStructuredLogger:
    """Test StructuredLogger class."""

    def test_structured_logger_creation(self):
        """StructuredLogger should initialize with name and log_dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = StructuredLogger("test", Path(tmpdir))

            assert logger.name == "test"
            assert isinstance(logger.logger, logging.Logger)

    def test_structured_logger_creates_log_dir(self):
        """StructuredLogger should create log_dir if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs" / "nested"
            logger = StructuredLogger("test", log_dir)

            assert log_dir.exists()
            assert (log_dir / "ouroboros.log").exists()

    def test_structured_logger_info(self):
        """StructuredLogger.info() should log INFO messages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = StructuredLogger("test", log_dir)

            logger.info("Test message", session_id="abc123")

            log_file = log_dir / "ouroboros.log"
            content = log_file.read_text()

            assert "Test message" in content
            assert "INFO" in content
            assert "abc123" in content

    def test_structured_logger_debug(self):
        """StructuredLogger.debug() should log DEBUG messages when level=DEBUG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = StructuredLogger("test", log_dir, level="DEBUG")

            logger.debug("Debug message", details="test")

            log_file = log_dir / "ouroboros.log"
            content = log_file.read_text()

            assert "Debug message" in content
            assert "DEBUG" in content

    def test_structured_logger_warning(self):
        """StructuredLogger.warning() should log WARNING messages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = StructuredLogger("test", log_dir)

            logger.warning("Warning message", threshold=0.5)

            log_file = log_dir / "ouroboros.log"
            content = log_file.read_text()

            assert "Warning message" in content
            assert "WARNING" in content

    def test_structured_logger_error(self):
        """StructuredLogger.error() should log ERROR messages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = StructuredLogger("test", log_dir)

            logger.error("Error message", operation="test")

            log_file = log_dir / "ouroboros.log"
            content = log_file.read_text()

            assert "Error message" in content
            assert "ERROR" in content

    def test_structured_logger_critical(self):
        """StructuredLogger.critical() should log CRITICAL messages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = StructuredLogger("test", log_dir)

            logger.critical("Critical message", subsystem="test")

            log_file = log_dir / "ouroboros.log"
            content = log_file.read_text()

            assert "Critical message" in content
            assert "CRITICAL" in content

    def test_structured_logger_behavioral(self):
        """StructuredLogger.behavioral() should log behavioral events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = StructuredLogger("test", log_dir)

            logger.behavioral(
                "query_diversity",
                {"unique_queries": 10, "total_queries": 15, "diversity": 0.67},
            )

            log_file = log_dir / "ouroboros.log"
            content = log_file.read_text()

            assert "Behavioral event" in content
            assert "query_diversity" in content
            assert "behavioral" in content

    def test_structured_logger_json_format(self):
        """StructuredLogger should write JSON Lines format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = StructuredLogger("test", log_dir)

            logger.info("Test message", field1="value1", field2="value2")

            log_file = log_dir / "ouroboros.log"
            lines = log_file.read_text().strip().split("\n")

            # Each line should be valid JSON
            for line in lines:
                data = json.loads(line)
                assert isinstance(data, dict)
                assert "timestamp" in data
                assert "level" in data
                assert "logger" in data


class TestGetLogger:
    """Test get_logger() function."""

    def test_get_logger_creates_logger(self):
        """get_logger() should create new logger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = get_logger("test_module", log_dir=log_dir)

            assert isinstance(logger, StructuredLogger)
            assert logger.name == "test_module"

    def test_get_logger_returns_cached_logger(self):
        """get_logger() should return cached logger for same name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger1 = get_logger("test_module2", log_dir=log_dir)
            logger2 = get_logger("test_module2", log_dir=log_dir)

            assert logger1 is logger2

    def test_get_logger_different_names(self):
        """get_logger() should create separate loggers for different names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger1 = get_logger("module1", log_dir=log_dir)
            logger2 = get_logger("module2", log_dir=log_dir)

            assert logger1 is not logger2
            assert logger1.name == "module1"
            assert logger2.name == "module2"

    def test_get_logger_default_log_dir(self):
        """get_logger() should use default log_dir if not provided."""
        logger = get_logger("test_module3")

        assert isinstance(logger, StructuredLogger)


class TestLogRotation:
    """Test log rotation functionality."""

    def test_log_file_created(self):
        """StructuredLogger should create log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = StructuredLogger("test", log_dir)

            logger.info("Test message")

            assert (log_dir / "ouroboros.log").exists()

    def test_multiple_log_entries(self):
        """StructuredLogger should write multiple log entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = StructuredLogger("test", log_dir)

            logger.info("Message 1")
            logger.info("Message 2")
            logger.info("Message 3")

            log_file = log_dir / "ouroboros.log"
            lines = log_file.read_text().strip().split("\n")

            assert len(lines) == 3
            assert "Message 1" in lines[0]
            assert "Message 2" in lines[1]
            assert "Message 3" in lines[2]


class TestLogContext:
    """Test structured context in logs."""

    def test_session_id_in_logs(self):
        """Logs should include session_id context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = StructuredLogger("test", log_dir)

            logger.info("Query processed", session_id="abc123", query="test")

            log_file = log_dir / "ouroboros.log"
            content = log_file.read_text()
            data = json.loads(content)

            assert data["session_id"] == "abc123"
            assert data["query"] == "test"

    def test_action_in_logs(self):
        """Logs should include action context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = StructuredLogger("test", log_dir)

            logger.info("Action executed", action="search_standards", results=5)

            log_file = log_dir / "ouroboros.log"
            content = log_file.read_text()
            data = json.loads(content)

            assert data["action"] == "search_standards"
            assert data["results"] == 5

    def test_metrics_in_logs(self):
        """Logs should include metric values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            logger = StructuredLogger("test", log_dir)

            logger.info(
                "Metrics collected",
                latency_ms=250,
                query_count=10,
                diversity=0.85,
            )

            log_file = log_dir / "ouroboros.log"
            content = log_file.read_text()
            data = json.loads(content)

            assert data["latency_ms"] == 250
            assert data["query_count"] == 10
            assert data["diversity"] == 0.85
