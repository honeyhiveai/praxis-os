"""
MCP tools module with selective loading and performance monitoring.

Provides tool registration with group-based selective loading to avoid
performance degradation (research shows 85% drop with >20 tools).
"""

from .browser_tools import register_browser_tools
from .rag_tools import register_rag_tools
from .registry import register_all_tools
from .server_info_tools import register_server_info_tools
from .workflow_tools import register_workflow_tools

__all__ = [
    "register_all_tools",
    "register_rag_tools",
    "register_workflow_tools",
    "register_browser_tools",
    "register_server_info_tools",
]
