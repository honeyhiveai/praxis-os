"""
Task parsers for dynamic workflow content.

DEPRECATED: This module is kept for backward compatibility.
Use ouroboros.subsystems.workflow.parsers instead.

New import:
    from ouroboros.subsystems.workflow.parsers import SourceParser, ParseError, SpecTasksParser, WorkflowDefinitionParser

This module will be removed in version 2.0.
"""

import warnings

# Import all classes from new location
from ouroboros.subsystems.workflow.parsers.base import ParseError, SourceParser
from ouroboros.subsystems.workflow.parsers.markdown import SpecTasksParser
from ouroboros.subsystems.workflow.parsers.yaml import WorkflowDefinitionParser

# Emit deprecation warning
warnings.warn(
    "task_parser module is deprecated. "
    "Use 'from ouroboros.subsystems.workflow.parsers import ParseError, SourceParser, SpecTasksParser, WorkflowDefinitionParser' instead. "
    "This module will be removed in version 2.0.",
    DeprecationWarning,
    stacklevel=2
)


__all__ = [
    "ParseError",
    "SourceParser",
    "SpecTasksParser",
    "WorkflowDefinitionParser",
]
