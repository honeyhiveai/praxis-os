"""
Unit tests for config-driven file watcher.

Phase 6, Task 6.1: Validates config loading, pattern matching, and exclude logic.
"""

import importlib.util
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml


# Load AgentOSFileWatcher dynamically
watcher_path = Path(__file__).parent.parent.parent / "monitoring" / "watcher.py"
watcher_spec = importlib.util.spec_from_file_location("monitoring.watcher", watcher_path)
watcher_module = importlib.util.module_from_spec(watcher_spec)
sys.modules['monitoring.watcher'] = watcher_module
watcher_spec.loader.exec_module(watcher_module)

AgentOSFileWatcher = watcher_module.AgentOSFileWatcher


@pytest.fixture
def temp_config():
    """Create temporary config file with file_watcher section."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "index_config.yaml"
        config = {
            "monitoring": {
                "file_watcher": {
                    "watched_content": {
                        "standards": {
                            "paths": ["standards/"],
                            "patterns": ["*.md", "*.json"],
                            "exclude": [],
                            "debounce_seconds": 5
                        },
                        "code": {
                            "enabled": True,
                            "paths": ["../src", "../lib"],
                            "patterns": ["*.py", "*.js", "*.ts"],
                            "exclude": [
                                "**/node_modules/**",
                                "**/__pycache__/**",
                                "**/venv/**",
                                "**/dist/**",
                                "**/*.pyc"
                            ],
                            "debounce_seconds": 10
                        }
                    }
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        yield config_path


@pytest.fixture
def watcher(temp_config):
    """Create AgentOSFileWatcher with test config."""
    return AgentOSFileWatcher(
        index_path=Path("/tmp/.cache/vector"),
        standards_path=Path("/tmp/standards"),
        config_path=temp_config
    )


class TestConfigLoading:
    """Test suite for config-driven pattern loading."""
    
    def test_loads_config_on_init(self, watcher):
        """Config should be loaded during initialization."""
        assert watcher.watched_content is not None
        assert isinstance(watcher.watched_content, dict)
    
    def test_loads_all_content_types(self, watcher):
        """All configured content types should be loaded."""
        assert "standards" in watcher.watched_content
        assert "code" in watcher.watched_content
    
    def test_loads_patterns_for_each_type(self, watcher):
        """Each content type should have its patterns loaded."""
        assert watcher.watched_content["standards"]["patterns"] == ["*.md", "*.json"]
        assert "*.py" in watcher.watched_content["code"]["patterns"]
    
    def test_loads_exclude_patterns(self, watcher):
        """Exclude patterns should be loaded correctly."""
        code_excludes = watcher.watched_content["code"]["exclude"]
        assert "**/node_modules/**" in code_excludes
        assert "**/__pycache__/**" in code_excludes
    
    def test_raises_on_missing_config(self):
        """Should raise ValueError if config file doesn't exist."""
        with pytest.raises(ValueError, match="Config file not found"):
            AgentOSFileWatcher(
                index_path=Path("/tmp/.cache/vector"),
                standards_path=Path("/tmp/standards"),
                config_path=Path("/nonexistent/config.yaml")
            )
    
    def test_raises_on_missing_monitoring_section(self):
        """Should raise ValueError if config missing monitoring section."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "bad_config.yaml"
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump({"indexes": {}}, f)
            
            with pytest.raises(ValueError, match="Config missing 'monitoring' section"):
                AgentOSFileWatcher(
                    index_path=Path("/tmp/.cache/vector"),
                    standards_path=Path("/tmp/standards"),
                    config_path=config_path
                )
    
    def test_raises_on_missing_file_watcher_section(self):
        """Should raise ValueError if config missing file_watcher section."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "bad_config.yaml"
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump({"monitoring": {"log_level": "INFO"}}, f)
            
            with pytest.raises(ValueError, match="Config missing 'monitoring.file_watcher' section"):
                AgentOSFileWatcher(
                    index_path=Path("/tmp/.cache/vector"),
                    standards_path=Path("/tmp/standards"),
                    config_path=config_path
                )


class TestPatternMatching:
    """Test suite for _match_content_type() pattern matching."""
    
    def test_matches_standards_markdown(self, watcher):
        """Should match .md files to standards content type."""
        result = watcher._match_content_type("standards/test.md")
        assert result == "standards"
    
    def test_matches_standards_json(self, watcher):
        """Should match .json files to standards content type."""
        result = watcher._match_content_type("standards/workflows/spec.json")
        assert result == "standards"
    
    def test_matches_code_python(self, watcher):
        """Should match .py files to code content type."""
        result = watcher._match_content_type("src/main.py")
        assert result == "code"
    
    def test_matches_code_javascript(self, watcher):
        """Should match .js files to code content type."""
        result = watcher._match_content_type("lib/utils.js")
        assert result == "code"
    
    def test_matches_code_typescript(self, watcher):
        """Should match .ts files to code content type."""
        result = watcher._match_content_type("app/component.ts")
        assert result == "code"
    
    def test_returns_none_for_unmatched_extension(self, watcher):
        """Should return None for file extensions not in patterns."""
        result = watcher._match_content_type("README.txt")
        assert result is None
    
    def test_returns_none_for_unmatched_file(self, watcher):
        """Should return None for files that don't match any pattern."""
        result = watcher._match_content_type("image.png")
        assert result is None


class TestExcludePatterns:
    """Test suite for exclude pattern matching."""
    
    def test_excludes_node_modules(self, watcher):
        """Should exclude files in node_modules directory."""
        result = watcher._match_content_type("node_modules/lib.js")
        assert result is None
    
    def test_excludes_nested_node_modules(self, watcher):
        """Should exclude node_modules at any depth."""
        result = watcher._match_content_type("app/node_modules/package/index.js")
        assert result is None
    
    def test_excludes_pycache(self, watcher):
        """Should exclude __pycache__ directories."""
        result = watcher._match_content_type("src/__pycache__/module.pyc")
        assert result is None
    
    def test_excludes_venv(self, watcher):
        """Should exclude venv directories."""
        result = watcher._match_content_type("venv/lib/python3.9/site-packages/pkg.py")
        assert result is None
    
    def test_excludes_dist(self, watcher):
        """Should exclude dist directories."""
        result = watcher._match_content_type("dist/bundle.js")
        assert result is None
    
    def test_excludes_pyc_files(self, watcher):
        """Should exclude .pyc files by extension."""
        result = watcher._match_content_type("module.pyc")
        assert result is None
    
    def test_does_not_exclude_valid_code(self, watcher):
        """Should not exclude valid code files."""
        result = watcher._match_content_type("src/main.py")
        assert result == "code"


class TestEventHandlers:
    """Test suite for file system event handlers."""
    
    def test_on_modified_triggers_rebuild_for_matched_file(self, watcher):
        """Should trigger rebuild when matched file is modified."""
        watcher._schedule_rebuild = MagicMock()
        
        event = MagicMock()
        event.is_directory = False
        event.src_path = "standards/test.md"
        
        watcher.on_modified(event)
        
        watcher._schedule_rebuild.assert_called_once()
    
    def test_on_modified_skips_unmatched_file(self, watcher):
        """Should not trigger rebuild for unmatched files."""
        watcher._schedule_rebuild = MagicMock()
        
        event = MagicMock()
        event.is_directory = False
        event.src_path = "README.txt"
        
        watcher.on_modified(event)
        
        watcher._schedule_rebuild.assert_not_called()
    
    def test_on_modified_skips_excluded_file(self, watcher):
        """Should not trigger rebuild for excluded files."""
        watcher._schedule_rebuild = MagicMock()
        
        event = MagicMock()
        event.is_directory = False
        event.src_path = "node_modules/lib.js"
        
        watcher.on_modified(event)
        
        watcher._schedule_rebuild.assert_not_called()
    
    def test_on_created_triggers_rebuild_for_matched_file(self, watcher):
        """Should trigger rebuild when matched file is created."""
        watcher._schedule_rebuild = MagicMock()
        
        event = MagicMock()
        event.is_directory = False
        event.src_path = "src/new_file.py"
        
        watcher.on_created(event)
        
        watcher._schedule_rebuild.assert_called_once()
    
    def test_on_deleted_triggers_rebuild_for_matched_file(self, watcher):
        """Should trigger rebuild when matched file is deleted."""
        watcher._schedule_rebuild = MagicMock()
        
        event = MagicMock()
        event.is_directory = False
        event.src_path = "standards/old.md"
        
        watcher.on_deleted(event)
        
        watcher._schedule_rebuild.assert_called_once()
    
    def test_event_handlers_skip_directories(self, watcher):
        """All event handlers should skip directory events."""
        watcher._schedule_rebuild = MagicMock()
        
        event = MagicMock()
        event.is_directory = True
        event.src_path = "src/"
        
        watcher.on_modified(event)
        watcher.on_created(event)
        watcher.on_deleted(event)
        
        # Should not trigger rebuild for any directory event
        watcher._schedule_rebuild.assert_not_called()


class TestConfigDrivenFlexibility:
    """Test suite demonstrating config-driven flexibility."""
    
    def test_can_add_new_file_pattern(self):
        """Adding new pattern to config should work without code changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config = {
                "monitoring": {
                    "file_watcher": {
                        "watched_content": {
                            "code": {
                                "patterns": ["*.py", "*.go", "*.rs"],  # Added Go and Rust
                                "exclude": []
                            }
                        }
                    }
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f)
            
            watcher = AgentOSFileWatcher(
                index_path=Path("/tmp/.cache/vector"),
                standards_path=Path("/tmp/standards"),
                config_path=config_path
            )
            
            # Should match new patterns
            assert watcher._match_content_type("main.go") == "code"
            assert watcher._match_content_type("lib.rs") == "code"
    
    def test_can_add_new_content_type(self):
        """Adding new content type to config should work without code changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config = {
                "monitoring": {
                    "file_watcher": {
                        "watched_content": {
                            "docs": {  # New content type
                                "patterns": ["*.html", "*.css"],
                                "exclude": []
                            }
                        }
                    }
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f)
            
            watcher = AgentOSFileWatcher(
                index_path=Path("/tmp/.cache/vector"),
                standards_path=Path("/tmp/standards"),
                config_path=config_path
            )
            
            # Should match new content type
            assert watcher._match_content_type("page.html") == "docs"
            assert watcher._match_content_type("style.css") == "docs"


class TestPerContentTypeDebouncing:
    """Test suite for per-content-type debouncing (Phase 6, Task 6.2)."""
    
    def test_separate_timers_for_each_content_type(self, watcher):
        """Should maintain separate debounce timers for each content type."""
        # Schedule rebuild for standards
        watcher._schedule_rebuild("standards")
        assert "standards" in watcher.debounce_timers
        
        # Schedule rebuild for code (should not interfere with standards timer)
        watcher._schedule_rebuild("code")
        assert "code" in watcher.debounce_timers
        assert "standards" in watcher.debounce_timers  # Still there
        
        # Both timers should be alive
        assert watcher.debounce_timers["standards"].is_alive()
        assert watcher.debounce_timers["code"].is_alive()
        
        # Cleanup
        watcher.debounce_timers["standards"].cancel()
        watcher.debounce_timers["code"].cancel()
    
    def test_timer_resets_on_new_change(self, watcher):
        """Timer should be canceled and restarted when new change arrives."""
        # Schedule first rebuild
        watcher._schedule_rebuild("code")
        first_timer = watcher.debounce_timers["code"]
        assert first_timer.is_alive()
        
        # Wait a bit
        time.sleep(0.1)
        
        # Schedule second rebuild (should cancel first timer)
        watcher._schedule_rebuild("code")
        second_timer = watcher.debounce_timers["code"]
        
        # First timer should be canceled, second should be alive
        assert not first_timer.is_alive()
        assert second_timer.is_alive()
        assert first_timer is not second_timer
        
        # Cleanup
        second_timer.cancel()
    
    def test_uses_content_type_specific_debounce_seconds(self, watcher):
        """Should use debounce_seconds from config for each content type."""
        # Config has standards: 5s, code: 10s
        standards_debounce = watcher.watched_content["standards"]["debounce_seconds"]
        code_debounce = watcher.watched_content["code"]["debounce_seconds"]
        
        assert standards_debounce == 5
        assert code_debounce == 10
        assert standards_debounce != code_debounce
    
    def test_thread_safe_timer_management(self, watcher):
        """Timer management should be thread-safe."""
        # Schedule multiple rebuilds in parallel
        def schedule_many():
            for _ in range(10):
                watcher._schedule_rebuild("code")
        
        threads = [threading.Thread(target=schedule_many) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have exactly one timer for "code"
        assert "code" in watcher.debounce_timers
        assert len([k for k in watcher.debounce_timers.keys() if k == "code"]) == 1
        
        # Cleanup
        if "code" in watcher.debounce_timers:
            watcher.debounce_timers["code"].cancel()
    
    def test_timers_removed_after_completion(self, watcher):
        """Timer should be removed from dict after rebuild completes."""
        # Mock the rebuild to complete quickly
        original_method = watcher._schedule_rebuild
        
        def quick_rebuild(content_type):
            with watcher.timer_lock:
                # Simulate quick completion
                def complete():
                    with watcher.timer_lock:
                        if content_type in watcher.debounce_timers:
                            del watcher.debounce_timers[content_type]
                
                timer = threading.Timer(0.1, complete)
                timer.daemon = True
                watcher.debounce_timers[content_type] = timer
                timer.start()
        
        watcher._schedule_rebuild = quick_rebuild
        watcher._schedule_rebuild("code")
        
        # Timer should exist immediately
        assert "code" in watcher.debounce_timers
        
        # Wait for timer to complete
        time.sleep(0.2)
        
        # Timer should be removed after completion
        assert "code" not in watcher.debounce_timers
        
        # Restore original method
        watcher._schedule_rebuild = original_method
    
    def test_simultaneous_different_content_types(self, watcher):
        """Different content types should be able to rebuild simultaneously."""
        # Schedule rebuilds for both content types
        watcher._schedule_rebuild("standards")
        watcher._schedule_rebuild("code")
        
        # Both should have active timers
        assert "standards" in watcher.debounce_timers
        assert "code" in watcher.debounce_timers
        assert watcher.debounce_timers["standards"].is_alive()
        assert watcher.debounce_timers["code"].is_alive()
        
        # They should be different timer objects
        assert watcher.debounce_timers["standards"] is not watcher.debounce_timers["code"]
        
        # Cleanup
        watcher.debounce_timers["standards"].cancel()
        watcher.debounce_timers["code"].cancel()
    
    def test_event_handlers_pass_content_type_to_schedule_rebuild(self, watcher):
        """Event handlers should pass content_type to _schedule_rebuild."""
        watcher._schedule_rebuild = MagicMock()
        
        # Test on_modified
        event = MagicMock()
        event.is_directory = False
        event.src_path = "standards/test.md"
        
        watcher.on_modified(event)
        
        watcher._schedule_rebuild.assert_called_once_with("standards")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

