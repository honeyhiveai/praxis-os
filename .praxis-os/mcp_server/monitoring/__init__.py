"""
File system monitoring module.

Provides file watching capabilities for prAxIs OS content changes
with incremental index rebuilding and hot reload support.
"""

from .watcher import AgentOSFileWatcher

__all__ = ["AgentOSFileWatcher"]
