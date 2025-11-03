"""
File system monitoring for prAxIs OS content changes.

Watches standards directory for changes and triggers incremental index rebuilds
with debouncing.
"""

# pylint: disable=too-many-instance-attributes
# Justification: File watcher needs 11 attributes for paths, timing, threading,
# callbacks, state management, and config-driven patterns - essential for robust monitoring

# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: __init__ requires 8 parameters for complete watcher configuration
# (paths, debouncing, callbacks, cache control) - all necessary for flexibility

# pylint: disable=import-outside-toplevel
# Justification: IndexBuilder imported lazily to avoid circular dependencies
# and reduce startup time when file watching is not needed

# pylint: disable=broad-exception-caught
# Justification: File watcher must be robust - catches broad exceptions during
# index rebuilds to prevent file monitoring service interruption

import logging
import sys
import threading
import time
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class AgentOSFileWatcher(FileSystemEventHandler):
    """Watches prAxIs OS directories for content changes and triggers index rebuild."""

    def __init__(
        self,
        index_path: Path,
        standards_path: Path,
        usage_path: Optional[Path] = None,  # Deprecated, kept for compatibility
        workflows_path: Optional[Path] = None,  # Deprecated, kept for compatibility
        embedding_provider: str = "local",
        rag_engine: Optional[Any] = None,
        debounce_seconds: int = 5,
        config_path: Optional[Path] = None,  # NEW: Path to index_config.yaml
        index_manager: Optional[Any] = None,  # NEW: IndexManager for multi-index rebuilds
    ) -> None:
        """
        Initialize file watcher with configured paths.

        Phase 6, Task 6.1: Config-driven file watching with per-content-type patterns.

        Uses dependency injection - all paths provided by configuration.

        :param index_path: Path to vector index directory
        :param standards_path: Path to standards directory (all AI-facing content)
        :param usage_path: Deprecated, no longer used (kept for compatibility)
        :param workflows_path: Deprecated, no longer used (kept for compatibility)
        :param embedding_provider: Embedding provider ("local" or "openai")
        :param rag_engine: Optional RAG engine instance for hot reload (DEPRECATED - use index_manager)
        :param debounce_seconds: Seconds to wait after last change before rebuilding (DEPRECATED - use config)
        :param config_path: Path to index_config.yaml (defaults to .praxis-os/config/index_config.yaml)
        :param index_manager: IndexManager instance for multi-index rebuilds (standards + code)
        
        :raises ValueError: If config file not found or invalid structure
        :raises RuntimeError: If config loading fails
        """
        self.index_path = index_path
        self.standards_path = standards_path
        # Note: usage_path and workflows_path are deprecated but kept for compatibility
        self.usage_path = usage_path  # No longer used
        self.workflows_path = workflows_path  # No longer used
        self.embedding_provider = embedding_provider
        self.rag_engine = rag_engine
        self.index_manager = index_manager  # NEW: For multi-index rebuilds
        self.rebuild_pending = False
        self.last_rebuild_time = 0.0
        self.debounce_seconds = debounce_seconds  # Fallback if config not available
        
        # Load config-driven patterns (Phase 6, Task 6.1)
        self.config_path = config_path or (index_path.parent.parent / "config" / "index_config.yaml")
        self.watched_content: Dict[str, Dict[str, Any]] = self._load_watcher_config()
        
        # Per-content-type debouncing (Phase 6, Task 6.2)
        # Maps content_type -> threading.Timer instance
        self.debounce_timers: Dict[str, threading.Timer] = {}
        # Lock for thread-safe timer management
        self.timer_lock = threading.Lock()

    def on_modified(self, event: Any) -> None:
        """
        Handle file modification events.
        
        Phase 6, Task 6.1: Config-driven pattern matching replaces hardcoded extensions.

        :param event: File system event from watchdog
        """
        if event.is_directory:
            return

        # Use config-driven pattern matching (Phase 6, Task 6.1)
        content_type = self._match_content_type(event.src_path)
        if content_type is None:
            return  # No match or excluded

        logger.info(
            "📝 %s content modified: %s",
            content_type.capitalize(),
            Path(event.src_path).name
        )
        self._schedule_rebuild(content_type)

    def on_created(self, event: Any) -> None:
        """
        Handle file creation events.
        
        Phase 6, Task 6.1: Config-driven pattern matching replaces hardcoded extensions.

        :param event: File system event from watchdog
        """
        if event.is_directory:
            return

        # Use config-driven pattern matching (Phase 6, Task 6.1)
        content_type = self._match_content_type(event.src_path)
        if content_type is None:
            return  # No match or excluded

        logger.info(
            "📝 New %s content: %s",
            content_type,
            Path(event.src_path).name
        )
        self._schedule_rebuild(content_type)

    def on_deleted(self, event: Any) -> None:
        """
        Handle file deletion events.
        
        Phase 6, Task 6.1: Config-driven pattern matching replaces hardcoded extensions.
        
        File Watcher Integration: Instead of rebuilding the entire index, directly
        removes the deleted file's content from the index using IndexManager.

        :param event: File system event from watchdog
        """
        if event.is_directory:
            return

        # Use config-driven pattern matching (Phase 6, Task 6.1)
        content_type = self._match_content_type(event.src_path)
        if content_type is None:
            return  # No match or excluded

        logger.info(
            "🗑️  %s content deleted: %s",
            content_type.capitalize(),
            Path(event.src_path).name
        )
        
        # Remove file from index immediately (no debounce for deletions)
        if self.index_manager:
            try:
                content_index = self.index_manager.get_index(content_type)
                if content_index and hasattr(content_index, 'remove_file'):
                    content_index.remove_file(event.src_path)
                    logger.info(
                        "✅ Removed deleted file from %s index: %s",
                        content_type,
                        Path(event.src_path).name
                    )
                else:
                    logger.warning(
                        "⚠️  Index '%s' does not support remove_file(), skipping deletion",
                        content_type
                    )
            except Exception as e:
                logger.error(
                    "❌ Failed to remove deleted file from index: %s",
                    e,
                    exc_info=True
                )
        else:
            logger.warning("⚠️  No IndexManager available, cannot remove deleted file from index")

    def check_rebuild_flag(self) -> None:
        """
        Check for .rebuild_index flag and trigger incremental rebuild if present.
        
        This flag is created by the install script to schedule a RAG index build
        on MCP server startup. The incremental logic will detect all new files
        (including development standards created by LLM) and index them efficiently.
        
        The flag is removed after the rebuild completes.
        """
        flag_path = self.standards_path / ".rebuild_index"
        
        if not flag_path.exists():
            return  # No flag, nothing to do
        
        logger.info("🔄 .rebuild_index flag detected - building RAG index...")
        
        try:
            # Import here to avoid circular dependency
            sys.path.insert(0, str(self.index_path.parent.parent))
            from scripts.build_rag_index import IndexBuilder
            
            builder = IndexBuilder(
                index_path=self.index_path,
                standards_path=self.standards_path,
                embedding_provider=self.embedding_provider,
            )
            
            # Incremental build - will index all files if no metadata exists,
            # otherwise only new/modified files
            result = builder.build_index(force=False, incremental=True)
            
            # Reload RAG engine with thread-safe locking
            if self.rag_engine and result["status"] == "success":
                self.rag_engine.reload_index()
                logger.info("✅ Index built and RAG engine loaded with %d chunks", 
                           result.get("total_chunks", 0))
            elif result["status"] == "success":
                logger.info("✅ Index built with %d chunks", 
                           result.get("total_chunks", 0))
            else:
                logger.warning("⚠️  Index build had issues: %s",
                             result.get("message", "Unknown error"))
            
            # Remove flag after successful build
            flag_path.unlink()
            logger.info("✅ .rebuild_index flag removed - index is ready")
            
        except Exception as e:
            logger.error("❌ Failed to build index from flag: %s", e, exc_info=True)
            # Don't remove flag on error so it can be retried

    def _schedule_rebuild(self, content_type: str) -> None:
        """
        Schedule an index rebuild with per-content-type debouncing.
        
        Phase 6, Task 6.2: Per-content-type debouncing with timer cancellation.

        Prevents rapid repeated rebuilds by debouncing changes per content type.
        Each content type has its own debounce timer. If new changes arrive for
        a content type before its timer expires, the timer is canceled and restarted.

        :param content_type: Type of content that changed ("standards", "code", etc.)
        
        Example:
            >>> watcher._schedule_rebuild("code")  # Starts 10s timer for code
            >>> time.sleep(2)
            >>> watcher._schedule_rebuild("code")  # Cancels previous, starts new 10s timer
            >>> # Rebuild triggered 10s after LAST change, not first
        """
        with self.timer_lock:
            # Cancel existing timer for this content type
            if content_type in self.debounce_timers:
                old_timer = self.debounce_timers[content_type]
                if old_timer.is_alive():
                    old_timer.cancel()
                    logger.debug(
                        "⏱️  Canceled previous %s rebuild timer (new changes detected)",
                        content_type
                    )
            
            # Get debounce_seconds from config for this content type
            # Fallback to default if not in config
            content_cfg = self.watched_content.get(content_type, {})
            debounce_sec = content_cfg.get("debounce_seconds", self.debounce_seconds)
            
            logger.debug(
                "⏱️  Scheduled %s rebuild in %ds (debounce period)",
                content_type,
                debounce_sec
            )
            
            def rebuild_after_debounce() -> None:
                """
                Wait for debounce period, then incrementally update index for this content type.
                
                Uses IndexManager with incremental=True for all content types.
                """
                logger.info(
                    "🔄 Debounce period complete for %s, updating index...",
                    content_type
                )
                try:
                    if not self.index_manager:
                        logger.warning("⚠️  No IndexManager available for rebuild")
                        return
                    
                    # Get the appropriate index
                    content_index = self.index_manager.get_index(content_type)
                    if not content_index:
                        logger.warning("⚠️  %s index not available", content_type.capitalize())
                        return
                    
                    # Get source paths from config
                    if not hasattr(content_index, 'config') or 'source_paths' not in content_index.config:
                        logger.warning("⚠️  No source_paths in %s index config", content_type)
                        return
                    
                    source_paths = content_index.config['source_paths']
                    logger.info("🔨 Incrementally updating %s index (paths: %s)", content_type, source_paths)
                    
                    # Use incremental build - only processes changed files
                    content_index.build(source_paths=source_paths, force=False, incremental=True)
                    
                    # Reload RAG engine if standards were updated
                    if content_type == "standards" and self.rag_engine:
                        self.rag_engine.reload_index()
                        logger.info("✅ Standards index update complete. RAG engine reloaded.")
                    else:
                        logger.info("✅ %s index update complete", content_type.capitalize())

                    self.last_rebuild_time = time.time()
                except Exception as e:
                    logger.error(
                        "❌ Failed to rebuild %s index: %s",
                        content_type,
                        e,
                        exc_info=True
                    )
                finally:
                    # Remove timer from dict after completion
                    with self.timer_lock:
                        if content_type in self.debounce_timers:
                            del self.debounce_timers[content_type]

            # Create and start new timer
            timer = threading.Timer(debounce_sec, rebuild_after_debounce)
            timer.daemon = True
            self.debounce_timers[content_type] = timer
            timer.start()

    def _load_watcher_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Load file watcher configuration from index_config.yaml.
        
        Phase 6, Task 6.1: Config-driven pattern loading.
        
        Returns dict mapping content_type -> config:
        {
            "standards": {
                "paths": ["standards/"],
                "patterns": ["*.md", "*.json"],
                "exclude": [],
                "debounce_seconds": 5
            },
            "code": {
                "enabled": true,
                "paths": ["../src", "../lib"],
                "patterns": ["*.py", "*.js"],
                "exclude": ["**/node_modules/**"],
                "debounce_seconds": 10
            }
        }
        
        :return: Dictionary mapping content_type to its watcher configuration
        :raises ValueError: If config file not found or missing required keys
        :raises RuntimeError: If YAML parsing fails
        
        Example:
            >>> watcher = AgentOSFileWatcher(...)
            >>> config = watcher.watched_content
            >>> config["standards"]["patterns"]  # ["*.md", "*.json"]
        """
        if not self.config_path.exists():
            raise ValueError(
                f"Config file not found: {self.config_path}. "
                "File watcher requires index_config.yaml for patterns."
            )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load config from {self.config_path}: {e}") from e
        
        # Extract file_watcher.watched_content section
        if "monitoring" not in config:
            raise ValueError(
                f"Config missing 'monitoring' section: {self.config_path}. "
                "See index_config.yaml template for required structure."
            )
        
        if "file_watcher" not in config["monitoring"]:
            raise ValueError(
                f"Config missing 'monitoring.file_watcher' section: {self.config_path}. "
                "See index_config.yaml template for required structure."
            )
        
        watched_content = config["monitoring"]["file_watcher"].get("watched_content", {})
        
        if not watched_content:
            logger.warning(
                "No watched_content configured in %s. File watcher will not monitor any files.",
                self.config_path
            )
        
        # Validate each content type has required keys
        for content_type, cfg in watched_content.items():
            # Code content type can be disabled
            if content_type == "code" and not cfg.get("enabled", True):
                logger.info("Code watching disabled in config")
                continue
            
            if "patterns" not in cfg:
                raise ValueError(
                    f"Content type '{content_type}' missing 'patterns' in config. "
                    "Each watched content type must specify file patterns (e.g., ['*.md'])."
                )
        
        logger.info(
            "File watcher config loaded: %d content types, patterns=%s",
            len(watched_content),
            {k: v.get("patterns", []) for k, v in watched_content.items()}
        )
        
        return watched_content

    def _match_content_type(self, file_path: str) -> Optional[str]:
        """
        Match file path against configured patterns to determine content type.
        
        Phase 6, Task 6.1: Core pattern matching for config-driven watching.
        
        Checks each content type's patterns and exclude lists. Returns first match.
        
        :param file_path: File path to match (can be absolute or relative)
        :return: content_type string if matched (e.g., "standards", "code"), None if excluded or no match
        
        Example:
            >>> watcher._match_content_type("standards/test.md")
            "standards"
            >>> watcher._match_content_type("src/main.py")
            "code"
            >>> watcher._match_content_type("node_modules/lib.js")
            None  # Excluded
        
        Algorithm:
            1. For each content_type in config (standards, code, ...):
                a. Check exclude patterns first (skip if matched)
                b. Check include patterns (return content_type if matched)
            2. Return None if no match found
        """
        file_path_obj = Path(file_path)
        file_path_str = str(file_path_obj)
        
        # Try each content type in config
        for content_type, cfg in self.watched_content.items():
            # Skip disabled content types (e.g., code.enabled: false)
            if content_type == "code" and not cfg.get("enabled", True):
                continue
            
            # Check exclude patterns first (apply to ALL content types, not just this one)
            # This ensures exclusions work globally (e.g., node_modules excluded from all watching)
            exclude_patterns = cfg.get("exclude", [])
            excluded = False
            for pattern in exclude_patterns:
                # Handle **/ patterns (match any directory depth)
                # Convert **/ to *: "**/__pycache__/**" → "__pycache__" in path
                pattern_clean = pattern.replace("**/", "").replace("/**", "")
                
                # Check if pattern component is anywhere in path
                # This handles both "**/node_modules/**" and "*/node_modules/*"
                if pattern_clean in file_path_str:
                    excluded = True
                    break
                
                # Also try exact fnmatch for simple patterns like "*.pyc"
                if fnmatch(file_path_obj.name, pattern):
                    excluded = True
                    break
            
            if excluded:
                continue  # Skip to next content type
            
            # Check include patterns
            include_patterns = cfg.get("patterns", [])
            for pattern in include_patterns:
                # Match against filename only (not full path)
                # This allows patterns like "*.md" to work regardless of directory
                if fnmatch(file_path_obj.name, pattern):
                    return content_type
        
        # No match found
        return None


__all__ = ["AgentOSFileWatcher"]
