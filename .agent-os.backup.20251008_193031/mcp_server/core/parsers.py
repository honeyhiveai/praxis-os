"""
Source parsers for dynamic workflow content.

Provides abstract interface and concrete implementations for parsing
external sources (like spec tasks.md files) into structured workflow data.
"""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any
from mcp_server.models.workflow import DynamicPhase, DynamicTask

# Mistletoe imports for AST-based parsing
from mistletoe import Document
from mistletoe.block_token import Heading, List as MarkdownList, ListItem, Paragraph
from mistletoe.span_token import RawText, Strong


class ParseError(Exception):
    """Raised when source parsing fails."""
    
    pass


class SourceParser(ABC):
    """
    Abstract parser for dynamic workflow sources.
    
    Subclasses implement parsing for specific source formats
    (e.g., tasks.md files, Jira API, GitHub Issues, etc.).
    """
    
    @abstractmethod
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse source into structured phase/task data.
        
        Args:
            source_path: Path to source file or directory
            
        Returns:
            List of DynamicPhase objects with populated tasks
            
        Raises:
            ParseError: If source is invalid or cannot be parsed
        """
        pass


class SpecTasksParser(SourceParser):
    """
    AST-based parser for Agent OS spec tasks.md files.
    
    Uses mistletoe to parse markdown into an AST, then extracts phases,
    tasks, acceptance criteria, dependencies, and validation gates through
    tree traversal. Much more robust than regex-based parsing.
    
    Handles variations in formatting gracefully:
    - ## or ### for phase headers
    - **Objective:** or **Goal:** for descriptions
    - Different task list formats
    - Flexible acceptance criteria placement
    """
    
    def parse(self, source_path: Path) -> List[DynamicPhase]:
        """
        Parse spec's tasks.md file into structured phases using AST.
        
        Args:
            source_path: Path to tasks.md file or directory containing it
            
        Returns:
            List of DynamicPhase objects
            
        Raises:
            ParseError: If file format is invalid or cannot be parsed
        """
        if not source_path.exists():
            raise ParseError(f"Source file not found: {source_path}")
        
        if source_path.is_dir():
            # If directory provided, look for tasks.md
            source_path = source_path / "tasks.md"
            if not source_path.exists():
                raise ParseError(f"tasks.md not found in directory: {source_path.parent}")
        
        try:
            content = source_path.read_text(encoding="utf-8")
        except Exception as e:
            raise ParseError(f"Failed to read {source_path}: {e}")
        
        if not content.strip():
            raise ParseError(f"Source file is empty: {source_path}")
        
        # Parse markdown into AST
        try:
            doc = Document(content)
        except Exception as e:
            raise ParseError(f"Failed to parse markdown: {e}")
        
        # Extract phases from AST
        phases = self._extract_phases_from_ast(doc)
        
        if not phases:
            raise ParseError(f"No phases found in {source_path}")
        
        return phases
    
    def _extract_phases_from_ast(self, doc: Document) -> List[DynamicPhase]:
        """
        Extract phases by traversing the markdown AST.
        
        Args:
            doc: Mistletoe Document object
            
        Returns:
            List of DynamicPhase objects
        """
        phases = []
        current_phase_data = None
        
        for node in doc.children:
            # Check for phase headers (## Phase N: Name or ### Phase N: Name)
            if isinstance(node, Heading) and node.level in [2, 3]:
                header_text = self._get_text_content(node)
                phase_match = re.match(r'Phase (\d+):\s*(.+)', header_text)
                
                if phase_match:
                    # Save previous phase if exists
                    if current_phase_data:
                        phase = self._build_phase(current_phase_data)
                        if phase:
                            phases.append(phase)
                    
                    # Start new phase
                    phase_number = int(phase_match.group(1))
                    phase_name = phase_match.group(2).strip()
                    current_phase_data = {
                        'phase_number': phase_number,
                        'phase_name': phase_name,
                        'description': '',
                        'estimated_duration': 'Variable',
                        'task_lines': [],
                        'validation_gate': [],
                        'nodes': []  # Collect nodes for this phase
                    }
                    continue
            
            # Collect nodes that belong to current phase
            if current_phase_data is not None:
                current_phase_data['nodes'].append(node)
        
        # Don't forget the last phase
        if current_phase_data:
            phase = self._build_phase(current_phase_data)
            if phase:
                phases.append(phase)
        
        return phases
    
    def _build_phase(self, phase_data: Dict[str, Any]) -> Optional[DynamicPhase]:
        """
        Build a DynamicPhase from collected phase data.
        
        Args:
            phase_data: Dictionary with phase information and AST nodes
            
        Returns:
            DynamicPhase object or None if invalid
        """
        # Extract metadata from nodes
        for node in phase_data['nodes']:
            if isinstance(node, Paragraph):
                text = self._get_text_content(node)
                
                # Look for common metadata patterns
                if 'Objective:' in text or 'Goal:' in text:
                    desc_match = re.search(r'\*\*(?:Objective|Goal):\*\*\s*(.+)', text)
                    if desc_match:
                        phase_data['description'] = desc_match.group(1).strip()
                
                if 'Estimated Duration:' in text or 'Estimated Effort:' in text:
                    dur_match = re.search(r'\*\*Estimated (?:Duration|Effort):\*\*\s*(.+)', text)
                    if dur_match:
                        phase_data['estimated_duration'] = dur_match.group(1).strip()
            
            # Extract tasks from markdown lists
            elif isinstance(node, MarkdownList):
                self._extract_tasks_from_list(node, phase_data)
        
        # Build tasks
        tasks = self._parse_collected_tasks(phase_data['task_lines'], phase_data['phase_number'])
        
        return DynamicPhase(
            phase_number=phase_data['phase_number'],
            phase_name=phase_data['phase_name'],
            description=phase_data['description'] or f"Phase {phase_data['phase_number']} objectives",
            estimated_duration=phase_data['estimated_duration'],
            tasks=tasks,
            validation_gate=phase_data['validation_gate'],
        )
    
    def _extract_tasks_from_list(self, list_node: MarkdownList, phase_data: Dict[str, Any]):
        """
        Extract tasks from a markdown list node.
        
        Args:
            list_node: Mistletoe List node
            phase_data: Phase data dict to populate
        """
        if not list_node or not hasattr(list_node, 'children') or list_node.children is None:
            return
        
        for item in list_node.children:
            if not isinstance(item, ListItem):
                continue
            
            item_text = self._get_text_content(item)
            
            # Check if this is a task (contains "Task N.M:")
            if re.search(r'Task \d+\.\d+:', item_text):
                phase_data['task_lines'].append({
                    'text': item_text,
                    'node': item
                })
            
            # Check for validation gate items
            elif 'Validation Gate:' in item_text or phase_data['validation_gate'] or \
                 any('validation' in line.lower() for line in item_text.split('\n')[:2]):
                # This is validation gate content
                gate_items = self._extract_checklist_items(item)
                phase_data['validation_gate'].extend(gate_items)
    
    def _parse_collected_tasks(self, task_data_list: List[Dict[str, Any]], phase_number: int) -> List[DynamicTask]:
        """
        Parse collected task data into DynamicTask objects.
        
        Args:
            task_data_list: List of task data dictionaries
            phase_number: Phase number for context
            
        Returns:
            List of DynamicTask objects
        """
        tasks = []
        
        for task_data in task_data_list:
            text = task_data['text']
            
            # Extract task ID and name
            task_match = re.search(r'Task (\d+)\.(\d+):\s*(.+?)(?:\n|$)', text)
            if not task_match:
                continue
            
            task_id = f"{task_match.group(1)}.{task_match.group(2)}"
            task_name = task_match.group(3).strip()
            
            # Extract estimated time
            time_match = re.search(r'\*\*Estimated (?:Time|Duration):\*\*\s*(.+)', text)
            estimated_time = time_match.group(1).strip() if time_match else "Not specified"
            
            # Extract dependencies
            deps_match = re.search(r'\*\*Dependencies:\*\*\s*(.+)', text)
            dependencies = []
            if deps_match:
                deps_text = deps_match.group(1).strip()
                if deps_text.lower() != 'none':
                    dependencies = [d.strip() for d in deps_text.split(',')]
            
            # Extract acceptance criteria
            acceptance_criteria = self._extract_acceptance_criteria(text)
            
            tasks.append(DynamicTask(
                task_id=task_id,
                task_name=task_name,
                description=task_name,  # Could extract fuller description
                estimated_time=estimated_time,
                dependencies=dependencies,
                acceptance_criteria=acceptance_criteria,
            ))
        
        return tasks
    
    def _extract_acceptance_criteria(self, text: str) -> List[str]:
        """
        Extract acceptance criteria checklist items from text.
        
        Args:
            text: Task text containing acceptance criteria
            
        Returns:
            List of acceptance criteria strings
        """
        criteria = []
        in_criteria = False
        
        for line in text.split('\n'):
            if 'Acceptance Criteria:' in line:
                in_criteria = True
                continue
            
            if in_criteria:
                # Look for checklist items
                if line.strip().startswith('- [ ]'):
                    criterion = line.strip()[5:].strip()
                    criteria.append(criterion)
                elif line.strip() and not line.strip().startswith('-'):
                    # End of checklist
                    break
        
        return criteria
    
    def _extract_checklist_items(self, node) -> List[str]:
        """
        Extract checklist items from a node's children.
        
        Args:
            node: AST node to search
            
        Returns:
            List of checklist item strings
        """
        items = []
        text = self._get_text_content(node)
        
        for line in text.split('\n'):
            if line.strip().startswith('- [ ]'):
                item = line.strip()[5:].strip()
                items.append(item)
        
        return items
    
    def _get_text_content(self, node) -> str:
        """
        Extract all text content from a node and its children.
        
        Args:
            node: Mistletoe AST node
            
        Returns:
            Concatenated text content
        """
        if node is None:
            return ''
        
        if isinstance(node, RawText):
            return node.content
        
        if isinstance(node, Strong):
            return self._get_text_content(node.children[0]) if node.children else ''
        
        if hasattr(node, 'children') and node.children is not None:
            return ''.join(self._get_text_content(child) for child in node.children)
        
        return str(node) if node else ''


__all__ = [
    "ParseError",
    "SourceParser",
    "SpecTasksParser",
]