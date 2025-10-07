"""
Unit tests for workflow metadata loading and start_workflow enhancement.

Tests the new workflow overview feature that provides complete workflow
structure information upfront.
"""

import json
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_server.models import WorkflowMetadata, PhaseMetadata
from mcp_server.workflow_engine import WorkflowEngine
from mcp_server.state_manager import StateManager
from mcp_server.rag_engine import RAGEngine


class TestWorkflowMetadata(unittest.TestCase):
    """Test workflow metadata models and serialization."""
    
    def test_phase_metadata_creation(self):
        """Test PhaseMetadata creation and serialization."""
        phase = PhaseMetadata(
            phase_number=1,
            phase_name="Analysis",
            purpose="Analyze code structure",
            estimated_effort="15-20 minutes",
            key_deliverables=["Code analysis", "Test strategy"],
            validation_criteria=["Functions identified", "Test types determined"],
        )
        
        # Test attributes
        self.assertEqual(phase.phase_number, 1)
        self.assertEqual(phase.phase_name, "Analysis")
        self.assertEqual(len(phase.key_deliverables), 2)
        
        # Test serialization
        phase_dict = phase.to_dict()
        self.assertIn("phase_number", phase_dict)
        self.assertIn("phase_name", phase_dict)
        
        # Test deserialization
        phase2 = PhaseMetadata.from_dict(phase_dict)
        self.assertEqual(phase.phase_number, phase2.phase_number)
        self.assertEqual(phase.phase_name, phase2.phase_name)
    
    def test_workflow_metadata_creation(self):
        """Test WorkflowMetadata creation and serialization."""
        phases = [
            PhaseMetadata(
                phase_number=i,
                phase_name=f"Phase {i}",
                purpose=f"Purpose {i}",
                estimated_effort="10 minutes",
                key_deliverables=[],
                validation_criteria=[],
            )
            for i in range(3)
        ]
        
        metadata = WorkflowMetadata(
            workflow_type="test_workflow",
            version="1.0.0",
            description="Test workflow",
            total_phases=3,
            estimated_duration="30 minutes",
            primary_outputs=["output1", "output2"],
            phases=phases,
        )
        
        # Test attributes
        self.assertEqual(metadata.workflow_type, "test_workflow")
        self.assertEqual(metadata.total_phases, 3)
        self.assertEqual(len(metadata.phases), 3)
        
        # Test serialization
        metadata_dict = metadata.to_dict()
        self.assertIn("workflow_type", metadata_dict)
        self.assertIn("phases", metadata_dict)
        self.assertEqual(len(metadata_dict["phases"]), 3)
        
        # Test deserialization
        metadata2 = WorkflowMetadata.from_dict(metadata_dict)
        self.assertEqual(metadata.workflow_type, metadata2.workflow_type)
        self.assertEqual(metadata.total_phases, metadata2.total_phases)


class TestWorkflowEngineMetadata(unittest.TestCase):
    """Test workflow engine metadata loading functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mocks
        self.state_manager = Mock(spec=StateManager)
        self.rag_engine = Mock(spec=RAGEngine)
        
        # Create temporary test directory
        self.test_dir = Path("/tmp/test_workflows")
        self.test_dir.mkdir(exist_ok=True)
        
        # Create workflow engine with test directory
        self.engine = WorkflowEngine(
            state_manager=self.state_manager,
            rag_engine=self.rag_engine,
            workflows_base_path=self.test_dir,
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test directory
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_fallback_metadata_generation_test_workflow(self):
        """Test fallback metadata generation for test workflows."""
        metadata = self.engine._generate_fallback_metadata("test_generation_v3")
        
        self.assertEqual(metadata.workflow_type, "test_generation_v3")
        self.assertEqual(metadata.total_phases, 8)
        self.assertEqual(len(metadata.phases), 8)
        self.assertIn("test files", metadata.primary_outputs)
    
    def test_fallback_metadata_generation_production_workflow(self):
        """Test fallback metadata generation for production workflows."""
        metadata = self.engine._generate_fallback_metadata("production_code_v2")
        
        self.assertEqual(metadata.workflow_type, "production_code_v2")
        self.assertEqual(metadata.total_phases, 6)
        self.assertEqual(len(metadata.phases), 6)
        self.assertIn("production code", metadata.primary_outputs)
    
    def test_load_metadata_from_file(self):
        """Test loading metadata from metadata.json file."""
        # Create test workflow directory
        workflow_dir = self.test_dir / "test_workflow"
        workflow_dir.mkdir()
        
        # Create metadata.json
        test_metadata = {
            "workflow_type": "test_workflow",
            "version": "1.0.0",
            "description": "Test workflow",
            "total_phases": 2,
            "estimated_duration": "20 minutes",
            "primary_outputs": ["output1"],
            "phases": [
                {
                    "phase_number": 0,
                    "phase_name": "Setup",
                    "purpose": "Setup phase",
                    "estimated_effort": "10 minutes",
                    "key_deliverables": ["setup complete"],
                    "validation_criteria": ["ready"],
                },
                {
                    "phase_number": 1,
                    "phase_name": "Execute",
                    "purpose": "Execute phase",
                    "estimated_effort": "10 minutes",
                    "key_deliverables": ["execution complete"],
                    "validation_criteria": ["done"],
                },
            ],
        }
        
        metadata_file = workflow_dir / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(test_metadata, f)
        
        # Load metadata
        metadata = self.engine.load_workflow_metadata("test_workflow")
        
        # Verify loaded correctly
        self.assertEqual(metadata.workflow_type, "test_workflow")
        self.assertEqual(metadata.total_phases, 2)
        self.assertEqual(len(metadata.phases), 2)
        self.assertEqual(metadata.phases[0].phase_name, "Setup")
        self.assertEqual(metadata.phases[1].phase_name, "Execute")
    
    def test_metadata_caching(self):
        """Test that metadata is cached after first load."""
        # Create test workflow with metadata
        workflow_dir = self.test_dir / "test_workflow"
        workflow_dir.mkdir()
        
        test_metadata = {
            "workflow_type": "test_workflow",
            "version": "1.0.0",
            "description": "Test workflow",
            "total_phases": 1,
            "estimated_duration": "10 minutes",
            "primary_outputs": [],
            "phases": [
                {
                    "phase_number": 0,
                    "phase_name": "Test",
                    "purpose": "Test",
                    "estimated_effort": "10 minutes",
                    "key_deliverables": [],
                    "validation_criteria": [],
                }
            ],
        }
        
        metadata_file = workflow_dir / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(test_metadata, f)
        
        # Load metadata first time
        metadata1 = self.engine.load_workflow_metadata("test_workflow")
        
        # Delete metadata file
        metadata_file.unlink()
        
        # Load again - should come from cache
        metadata2 = self.engine.load_workflow_metadata("test_workflow")
        
        # Should be same object from cache
        self.assertIs(metadata1, metadata2)
        self.assertEqual(metadata2.workflow_type, "test_workflow")
    
    def test_start_workflow_includes_overview(self):
        """Test that start_workflow returns workflow_overview."""
        # Mock state manager to return a new session
        mock_state = MagicMock()
        mock_state.session_id = "test-session-123"
        mock_state.workflow_type = "test_generation_v3"
        mock_state.target_file = "test.py"
        mock_state.current_phase = 1
        mock_state.completed_phases = []
        mock_state.phase_artifacts = {}
        
        self.state_manager.get_active_session.return_value = None
        self.state_manager.create_session.return_value = mock_state
        
        # Mock RAG engine response
        mock_rag_result = MagicMock()
        mock_rag_result.chunks = []
        mock_rag_result.total_tokens = 0
        mock_rag_result.retrieval_method = "test"
        self.rag_engine.search.return_value = mock_rag_result
        
        # Start workflow
        result = self.engine.start_workflow(
            workflow_type="test_generation_v3",
            target_file="test.py"
        )
        
        # Verify workflow_overview is present
        self.assertIn("workflow_overview", result)
        self.assertIn("total_phases", result["workflow_overview"])
        self.assertIn("phases", result["workflow_overview"])
        
        # Verify overview structure
        overview = result["workflow_overview"]
        self.assertEqual(overview["workflow_type"], "test_generation_v3")
        self.assertEqual(overview["total_phases"], 8)  # Fallback generates 8 phases
        self.assertEqual(len(overview["phases"]), 8)


class TestGetTask(unittest.TestCase):
    """Test get_task functionality for horizontal scaling."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mocks
        self.state_manager = Mock(spec=StateManager)
        self.rag_engine = Mock(spec=RAGEngine)
        
        # Create temporary test directory
        self.test_dir = Path("/tmp/test_workflows")
        self.test_dir.mkdir(exist_ok=True)
        
        # Create workflow engine
        self.engine = WorkflowEngine(
            state_manager=self.state_manager,
            rag_engine=self.rag_engine,
            workflows_base_path=self.test_dir,
        )
        
        # Create mock session state
        self.mock_state = MagicMock()
        self.mock_state.session_id = "test-session-123"
        self.mock_state.workflow_type = "test_generation_v3"
        self.mock_state.target_file = "test.py"
        self.mock_state.current_phase = 1
        
        self.state_manager.load_state.return_value = self.mock_state
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_get_task_returns_full_content(self):
        """Test that get_task returns complete task content."""
        # Mock RAG engine to return task chunks
        mock_rag_result = MagicMock()
        mock_rag_result.chunks = [
            {
                "file_path": "phases/1/task-1-console-detection.md",
                "content": "# Task 1: Console Detection\n\n🛑 EXECUTE-NOW: Find console.log\n```bash\ngrep -n \"console\\.log\" test.py\n```\n\n📊 COUNT-AND-DOCUMENT: Total calls: [NUMBER]",
                "section_header": "Console Detection",
                "start_line": 1,
                "tokens": 50,
            },
            {
                "file_path": "phases/1/task-1-console-detection.md",
                "content": "More content for task 1\n\n🛑 EXECUTE-NOW: Find console.error\n```bash\ngrep -n \"console\\.error\" test.py\n```",
                "section_header": "Console Detection",
                "start_line": 10,
                "tokens": 30,
            },
        ]
        mock_rag_result.total_tokens = 80
        mock_rag_result.retrieval_method = "vector"
        
        self.rag_engine.search.return_value = mock_rag_result
        
        # Get task
        result = self.engine.get_task(
            session_id="test-session-123",
            phase=1,
            task_number=1
        )
        
        # Verify structure
        self.assertEqual(result["session_id"], "test-session-123")
        self.assertEqual(result["workflow_type"], "test_generation_v3")
        self.assertEqual(result["phase"], 1)
        self.assertEqual(result["task_number"], 1)
        self.assertEqual(result["task_name"], "Console Detection")
        
        # Verify content is complete (both chunks combined)
        self.assertIn("Task 1: Console Detection", result["content"])
        self.assertIn("Find console.log", result["content"])
        self.assertIn("Find console.error", result["content"])
        
        # Verify steps extracted
        self.assertIn("steps", result)
        self.assertGreater(len(result["steps"]), 0)
        
        # Verify first step
        step1 = result["steps"][0]
        self.assertEqual(step1["type"], "execute_command")
        self.assertIn("grep", step1["command"])
        # Command has escaped pattern "console\\.log"
        self.assertTrue("console" in step1["command"] or "console" in step1["description"])
        
    def test_get_task_filters_correct_task_file(self):
        """Test that get_task only returns chunks from the correct task file."""
        # Mock RAG with chunks from multiple tasks
        mock_rag_result = MagicMock()
        mock_rag_result.chunks = [
            {
                "file_path": "phases/1/task-1-console-detection.md",
                "content": "Task 1 content",
                "section_header": "Task 1",
                "start_line": 1,
                "tokens": 20,
            },
            {
                "file_path": "phases/1/task-2-logger-analysis.md",
                "content": "Task 2 content",
                "section_header": "Task 2",
                "start_line": 1,
                "tokens": 20,
            },
            {
                "file_path": "phases/1/task-1-console-detection.md",
                "content": "More task 1 content",
                "section_header": "Task 1",
                "start_line": 10,
                "tokens": 20,
            },
        ]
        mock_rag_result.total_tokens = 60
        mock_rag_result.retrieval_method = "vector"
        
        self.rag_engine.search.return_value = mock_rag_result
        
        # Get task 1
        result = self.engine.get_task(
            session_id="test-session-123",
            phase=1,
            task_number=1
        )
        
        # Should only contain task-1 content
        self.assertIn("Task 1 content", result["content"])
        self.assertIn("More task 1 content", result["content"])
        self.assertNotIn("Task 2 content", result["content"])
        
        # Verify 2 chunks retrieved (both task-1 chunks)
        self.assertEqual(result["chunks_retrieved"], 2)
    
    def test_get_task_handles_missing_task(self):
        """Test that get_task handles missing tasks gracefully."""
        # Mock RAG with no matching chunks
        mock_rag_result = MagicMock()
        mock_rag_result.chunks = [
            {
                "file_path": "phases/1/task-2-logger-analysis.md",
                "content": "Task 2 content",
                "section_header": "Task 2",
                "start_line": 1,
                "tokens": 20,
            },
        ]
        mock_rag_result.total_tokens = 20
        mock_rag_result.retrieval_method = "vector"
        
        self.rag_engine.search.return_value = mock_rag_result
        
        # Try to get task 5 (doesn't exist)
        result = self.engine.get_task(
            session_id="test-session-123",
            phase=1,
            task_number=5
        )
        
        # Should return error
        self.assertIn("error", result)
        self.assertIn("not found", result["error"].lower())
        self.assertEqual(result["task_number"], 5)
    
    def test_get_task_invalid_session(self):
        """Test that get_task raises error for invalid session."""
        # Mock state manager to return None
        self.state_manager.load_state.return_value = None
        
        # Should raise ValueError
        with self.assertRaises(ValueError) as context:
            self.engine.get_task(
                session_id="invalid-session",
                phase=1,
                task_number=1
            )
        
        self.assertIn("not found", str(context.exception).lower())
    
    def test_get_task_extracts_steps(self):
        """Test that get_task correctly extracts execution steps."""
        # Mock RAG with task containing multiple command types
        mock_rag_result = MagicMock()
        mock_rag_result.chunks = [
            {
                "file_path": "phases/1/task-1-test.md",
                "content": """# Test Task

🛑 EXECUTE-NOW: Run test command
```bash
npm test
```

📊 COUNT-AND-DOCUMENT: Tests passed: [NUMBER]

🔍 QUERY-AND-DECIDE: Check if tests passed

🛑 EXECUTE-NOW: Another command
```bash
npm run build
```
""",
                "section_header": "Test Task",
                "start_line": 1,
                "tokens": 100,
            },
        ]
        mock_rag_result.total_tokens = 100
        mock_rag_result.retrieval_method = "vector"
        
        self.rag_engine.search.return_value = mock_rag_result
        
        # Get task
        result = self.engine.get_task(
            session_id="test-session-123",
            phase=1,
            task_number=1
        )
        
        # Verify steps extracted
        steps = result["steps"]
        self.assertGreater(len(steps), 0)
        
        # Check for execute_command steps
        execute_steps = [s for s in steps if s["type"] == "execute_command"]
        self.assertGreaterEqual(len(execute_steps), 2)
        
        # Check for decision_point steps
        decision_steps = [s for s in steps if s["type"] == "decision_point"]
        self.assertGreaterEqual(len(decision_steps), 1)


if __name__ == "__main__":
    unittest.main()
