"""
Configuration data models for MCP Server.

Defines RAGConfig and ServerConfig with validated defaults.
Single source of truth for configuration throughout the application.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class RAGConfig:
    """RAG system configuration with validated defaults."""

    # Paths (relative to project root)
    standards_path: str = (
        ".praxis-os/standards"  # All AI-facing content (indexed in RAG)
    )
    # NOT indexed (passed to WorkflowEngine for structured access)
    workflows_path: str = ".praxis-os/workflows"
    index_path: str = ".praxis-os/.cache/vector_index"

    # Settings
    embedding_provider: str = "local"

    def resolve_paths(self, project_root: Path) -> Dict[str, Path]:
        """
        Resolve relative paths to absolute paths.

        :param project_root: Project root directory
        :return: Dictionary of resolved Path objects
        :raises ValueError: If paths are invalid
        """
        return {
            "standards_path": project_root / self.standards_path,
            "workflows_path": project_root / self.workflows_path,
            "index_path": project_root / self.index_path,
        }


@dataclass
class MCPConfig:
    """
    MCP server-specific configuration.

    Includes transport configuration for dual-transport mode support.
    """

    enabled_tool_groups: List[str] = field(
        default_factory=lambda: ["rag", "workflow", "browser"]
    )
    max_tools_warning: int = 20

    # HTTP transport configuration (for dual and HTTP modes)
    http_port: int = 4242
    http_host: str = "127.0.0.1"
    http_path: str = "/mcp"


@dataclass
class ServerConfig:
    """Complete MCP server configuration."""

    base_path: Path
    rag: RAGConfig
    mcp: MCPConfig = field(default_factory=MCPConfig)

    @property
    def project_root(self) -> Path:
        """Project root is parent of .praxis-os/."""
        return self.base_path.parent

    @property
    def resolved_paths(self) -> Dict[str, Path]:
        """Get all resolved paths for easy access."""
        return self.rag.resolve_paths(self.project_root)


__all__ = [
    "RAGConfig",
    "MCPConfig",
    "ServerConfig",
]
