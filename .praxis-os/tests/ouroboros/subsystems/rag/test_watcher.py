"""Tests for FileWatcher (Incremental Index Updates)."""

import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from ouroboros.config.schemas.indexes import FileWatcherConfig
from ouroboros.subsystems.rag.watcher import FileWatcher
from ouroboros.utils.errors import ActionableError


def create_watcher_config(**kwargs):
    """Helper to create valid FileWatcherConfig with defaults."""
    defaults = {
        "enabled": True,
        "debounce_ms": 100,  # Short for tests
        "watch_patterns": ["*.md", "*.py"],
    }
    defaults.update(kwargs)
    return FileWatcherConfig(**defaults)


class TestFileWatcherInitialization:
    """Test FileWatcher initialization."""

    def test_initialization_basic(self):
        """Test basic initialization."""
        config = create_watcher_config()
        mock_index_manager = Mock()
        path_mappings = {
            ".praxis-os/standards/": ["standards"],
            "src/": ["code", "graph", "ast"],
        }

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        assert watcher.config == config
        assert watcher.index_manager == mock_index_manager
        assert watcher.path_mappings == path_mappings
        assert watcher._observer is None  # Not started yet

    def test_initialization_with_custom_debounce(self):
        """Test initialization with custom debounce."""
        config = create_watcher_config(debounce_ms=500)
        mock_index_manager = Mock()
        path_mappings = {".praxis-os/standards/": ["standards"]}

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        assert watcher.config.debounce_ms == 500


class TestFileWatcherPathMapping:
    """Test path-to-index mapping logic."""

    def test_get_affected_indexes_standards(self):
        """Test mapping for standards path."""
        config = create_watcher_config()
        mock_index_manager = Mock()
        path_mappings = {
            ".praxis-os/standards/": ["standards"],
            "src/": ["code", "graph", "ast"],
        }

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        affected = watcher._get_affected_indexes(Path(".praxis-os/standards/doc.md"))
        assert affected == ["standards"]

    def test_get_affected_indexes_code(self):
        """Test mapping for code paths."""
        config = create_watcher_config()
        mock_index_manager = Mock()
        path_mappings = {
            ".praxis-os/standards/": ["standards"],
            "src/": ["code", "graph", "ast"],
        }

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        affected = watcher._get_affected_indexes(Path("src/module.py"))
        assert set(affected) == {"code", "graph", "ast"}

    def test_get_affected_indexes_no_match(self):
        """Test mapping for unmatched paths."""
        config = create_watcher_config()
        mock_index_manager = Mock()
        path_mappings = {
            ".praxis-os/standards/": ["standards"],
        }

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        affected = watcher._get_affected_indexes(Path("other/file.txt"))
        assert affected == []


class TestFileWatcherDebouncing:
    """Test debouncing logic."""

    def test_debounce_timer_setup(self):
        """Test that debounce timer is set up correctly."""
        config = create_watcher_config(debounce_ms=100)
        mock_index_manager = Mock()
        path_mappings = {".praxis-os/standards/": ["standards"]}

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        # Simulate adding changes
        with watcher._lock:
            watcher._pending_changes["standards"].add(Path("test.md"))
            watcher._reset_debounce_timer()

        assert watcher._debounce_timer is not None
        assert watcher._debounce_timer.is_alive()

        # Clean up
        watcher._debounce_timer.cancel()

    def test_debounce_collects_multiple_changes(self):
        """Test that debouncing collects multiple changes."""
        config = create_watcher_config(debounce_ms=100)
        mock_index_manager = Mock()
        path_mappings = {".praxis-os/standards/": ["standards"]}

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        # Add multiple changes
        with watcher._lock:
            watcher._pending_changes["standards"].add(Path("test1.md"))
            watcher._pending_changes["standards"].add(Path("test2.md"))

        assert len(watcher._pending_changes["standards"]) == 2


class TestFileWatcherStartStop:
    """Test start/stop functionality."""

    def test_start_disabled(self):
        """Test that start does nothing when disabled."""
        config = create_watcher_config(enabled=False)
        mock_index_manager = Mock()
        path_mappings = {".praxis-os/standards/": ["standards"]}

        watcher = FileWatcher(config, mock_index_manager, path_mappings)
        watcher.start()

        assert watcher._observer is None

    def test_stop_when_not_started(self):
        """Test that stop handles not-started case."""
        config = create_watcher_config()
        mock_index_manager = Mock()
        path_mappings = {".praxis-os/standards/": ["standards"]}

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        # Should not raise
        watcher.stop()


class TestFileWatcherEventHandling:
    """Test file event handling."""

    def test_on_file_event_ignores_directories(self):
        """Test that directory events are ignored."""
        config = create_watcher_config()
        mock_index_manager = Mock()
        path_mappings = {".praxis-os/standards/": ["standards"]}

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        # Create mock directory event
        mock_event = Mock()
        mock_event.is_directory = True
        mock_event.src_path = ".praxis-os/standards/subdir"

        watcher._on_file_event(mock_event)

        # Should not add to pending changes
        assert len(watcher._pending_changes) == 0

    def test_on_file_event_adds_to_pending(self):
        """Test that file events are added to pending changes."""
        config = create_watcher_config()
        mock_index_manager = Mock()
        path_mappings = {".praxis-os/standards/": ["standards"]}

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        # Create mock file event
        mock_event = Mock()
        mock_event.is_directory = False
        mock_event.src_path = ".praxis-os/standards/test.md"
        mock_event.event_type = "modified"

        watcher._on_file_event(mock_event)

        # Should add to pending changes
        assert (
            Path(".praxis-os/standards/test.md")
            in watcher._pending_changes["standards"]
        )


class TestFileWatcherProcessing:
    """Test change processing."""

    def test_process_pending_changes_calls_index_manager(self):
        """Test that processing calls IndexManager."""
        config = create_watcher_config()
        mock_index_manager = Mock()
        path_mappings = {".praxis-os/standards/": ["standards"]}

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        # Add pending changes
        test_file = Path(".praxis-os/standards/test.md")
        watcher._pending_changes["standards"].add(test_file)

        # Process
        watcher._process_pending_changes()

        # Should call IndexManager
        mock_index_manager.update_from_watcher.assert_called_once()
        call_args = mock_index_manager.update_from_watcher.call_args
        assert call_args[1]["index_name"] == "standards"
        assert test_file in call_args[1]["changed_files"]

    def test_process_pending_changes_handles_errors(self):
        """Test that processing handles IndexManager errors gracefully."""
        config = create_watcher_config()
        mock_index_manager = Mock()
        mock_index_manager.update_from_watcher.side_effect = Exception("Test error")
        path_mappings = {".praxis-os/standards/": ["standards"]}

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        # Add pending changes
        watcher._pending_changes["standards"].add(Path("test.md"))

        # Should not raise (logs error instead)
        watcher._process_pending_changes()


class TestFileChangeHandler:
    """Test internal file change handler."""

    def test_handler_filters_by_pattern(self):
        """Test that handler filters files by pattern."""
        config = create_watcher_config(watch_patterns=["*.md"])
        mock_index_manager = Mock()
        path_mappings = {".praxis-os/standards/": ["standards"]}

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        from ouroboros.subsystems.rag.watcher import _FileChangeHandler

        handler = _FileChangeHandler(watcher, config.watch_patterns)

        # Should match .md
        assert handler._should_process(Path("test.md")) is True

        # Should not match .txt
        assert handler._should_process(Path("test.txt")) is False


class TestFileWatcherIntegration:
    """Integration tests for FileWatcher."""

    def test_end_to_end_interface(self):
        """Test complete workflow interface."""
        config = create_watcher_config()
        mock_index_manager = Mock()
        path_mappings = {
            ".praxis-os/standards/": ["standards"],
            "src/": ["code", "graph", "ast"],
        }

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        # Verify all required methods exist
        assert hasattr(watcher, "start")
        assert hasattr(watcher, "stop")
        assert hasattr(watcher, "_on_file_event")
        assert hasattr(watcher, "_process_pending_changes")

    def test_multiple_indexes_per_path(self):
        """Test that one path can trigger multiple indexes."""
        config = create_watcher_config()
        mock_index_manager = Mock()
        path_mappings = {
            "src/": ["code", "graph", "ast"],  # 3 indexes for one path
        }

        watcher = FileWatcher(config, mock_index_manager, path_mappings)

        affected = watcher._get_affected_indexes(Path("src/module.py"))

        # Should trigger all 3 indexes
        assert set(affected) == {"code", "graph", "ast"}
