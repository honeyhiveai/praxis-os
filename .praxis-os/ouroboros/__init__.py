"""
Ouroboros MCP Server - Clean Architecture Rewrite.

A ground-up rebuild of the praxis-os MCP server with behavioral engineering
as the PRIMARY mission. Implements mission-driven layered architecture with
zero cross-talk, config-driven extensibility, and fail-fast validation.

Architecture Layers:
    - Tools Layer: AI agent interface (domain abstraction pattern)
    - Middleware Layer: Behavioral engineering (self-reinforcing loop)
    - Subsystems Layer: RAG, Workflow, Browser (isolated implementations)
    - Foundation Layer: Config, Utils, Errors, Logging

Key Principles:
    1. Behavioral Engineering First - Praxis is the mission
    2. Fail-Fast Validation - Invalid state crashes with actionable errors
    3. Config-Driven Extensibility - Add features via YAML, not code
    4. Test at All Layers - Unit → Integration → Performance → Validation
    5. Zero Cross-Talk - Subsystems never call each other directly

Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "praxis-os Team"

__all__ = ["__version__", "__author__"]

