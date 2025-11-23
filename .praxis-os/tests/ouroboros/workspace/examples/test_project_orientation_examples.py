"""
Tests to verify Project Orientation examples are valid and work correctly.

These tests ensure that the example files we provide to users actually work
and demonstrate the correct patterns.

Traceable to: .praxis-os/specs/approved/2025-11-19-project-orientation-system/
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock

from ouroboros.config.schemas.orientation import OrientationQuery, ProjectOrientation, ProjectConfig
from ouroboros.subsystems.rag.standards.orientation import OrientationMetadataParser


class TestInlineMetadataExample:
    """
    Test that PROJECT-ORIENTATION-EXAMPLE.md has valid inline metadata.
    """
    
    def test_example_file_exists(self):
        """Verify the example markdown file exists."""
        example_file = Path("dist/universal/templates/orientation/PROJECT-ORIENTATION-EXAMPLE.md")
        assert example_file.exists(), "Example file must exist"
    
    def test_example_metadata_parses_successfully(self):
        """Verify the inline metadata in example file parses correctly."""
        example_file = Path("dist/universal/templates/orientation/PROJECT-ORIENTATION-EXAMPLE.md")
        content = example_file.read_text()
        
        parser = OrientationMetadataParser()
        metadata = parser.extract_inline_metadata(content, example_file)
        
        # Verify metadata was extracted
        assert metadata is not None
        assert len(metadata) > 0
        
        # Verify required fields
        assert metadata.get('orientation') is True
        assert metadata.get('priority') == 1
        assert metadata.get('query') is not None
        
        # Verify query is reasonable
        query_str = metadata.get('query')
        assert len(query_str) >= 5  # Min length
        assert len(query_str) <= 500  # Max length
        
        print(f"\n✅ Example inline metadata is valid:")
        print(f"   Query: {query_str}")
        print(f"   Priority: {metadata.get('priority')}")
        print(f"   Description: {metadata.get('description')}")


class TestMCPYamlExample:
    """
    Test that mcp.yaml.example has valid project orientation configuration.
    """
    
    def test_example_yaml_exists(self):
        """Verify the example YAML file exists."""
        example_file = Path("dist/universal/templates/orientation/mcp.yaml.example")
        assert example_file.exists(), "Example YAML file must exist"
    
    def test_example_yaml_is_valid(self):
        """Verify the YAML file has valid syntax."""
        example_file = Path("dist/universal/templates/orientation/mcp.yaml.example")
        content = example_file.read_text()
        
        # Should parse as valid YAML
        data = yaml.safe_load(content)
        assert data is not None
        
        print("\n✅ Example YAML has valid syntax")
    
    def test_example_has_project_orientation_section(self):
        """Verify the example has a project.orientation section."""
        example_file = Path("dist/universal/templates/orientation/mcp.yaml.example")
        content = example_file.read_text()
        data = yaml.safe_load(content)
        
        # Verify structure
        assert 'project' in data
        assert 'orientation' in data['project']
        assert 'enabled' in data['project']['orientation']
        assert 'queries' in data['project']['orientation']
        
        print("\n✅ Example has project.orientation section")
    
    def test_example_queries_are_valid(self):
        """Verify all queries in example can be validated by Pydantic."""
        example_file = Path("dist/universal/templates/orientation/mcp.yaml.example")
        content = example_file.read_text()
        data = yaml.safe_load(content)
        
        # Extract queries
        queries_data = data['project']['orientation']['queries']
        
        # Each should be a valid OrientationQuery
        queries = []
        for q_data in queries_data:
            query = OrientationQuery(**q_data)
            queries.append(query)
        
        # Verify we have queries
        assert len(queries) >= 7, f"Expected 7+ example queries, got {len(queries)}"
        
        # Verify each query is valid
        for query in queries:
            assert query.query is not None
            assert len(query.query) >= 5
            assert len(query.query) <= 500
            assert query.priority in [1, 2, 3]
        
        print(f"\n✅ All {len(queries)} example queries are valid")
        print("   Queries:")
        for query in queries:
            print(f"   - [{query.priority}] {query.query[:60]}...")
    
    def test_example_has_all_priority_levels(self):
        """Verify example demonstrates all priority levels (1, 2, 3)."""
        example_file = Path("dist/universal/templates/orientation/mcp.yaml.example")
        content = example_file.read_text()
        data = yaml.safe_load(content)
        
        queries_data = data['project']['orientation']['queries']
        queries = [OrientationQuery(**q) for q in queries_data]
        
        priorities = {q.priority for q in queries}
        
        # Should have examples of all three priorities
        assert 1 in priorities, "Example should have priority 1 queries"
        assert 2 in priorities, "Example should have priority 2 queries"
        assert 3 in priorities, "Example should have priority 3 queries"
        
        print("\n✅ Example demonstrates all priority levels:")
        print(f"   Priority 1: {sum(1 for q in queries if q.priority == 1)} queries")
        print(f"   Priority 2: {sum(1 for q in queries if q.priority == 2)} queries")
        print(f"   Priority 3: {sum(1 for q in queries if q.priority == 3)} queries")
    
    def test_example_can_create_project_config(self):
        """Verify example data can instantiate ProjectConfig."""
        example_file = Path("dist/universal/templates/orientation/mcp.yaml.example")
        content = example_file.read_text()
        data = yaml.safe_load(content)
        
        # Extract project section
        project_data = data['project']
        
        # Should be able to create ProjectConfig
        project_config = ProjectConfig(**project_data)
        
        assert project_config is not None
        assert project_config.orientation is not None
        assert project_config.orientation.enabled is True
        assert len(project_config.orientation.queries) >= 7
        
        print("\n✅ Example data successfully creates ProjectConfig")


class TestExamplesEndToEnd:
    """
    Test that examples work end-to-end (discovery + parsing).
    """
    
    def test_inline_example_discovered_and_parsed(self):
        """
        Test that inline example can be discovered and parsed end-to-end.
        
        Simulates the full flow: file → content → parser → metadata → query object
        """
        example_file = Path("dist/universal/templates/orientation/PROJECT-ORIENTATION-EXAMPLE.md")
        content = example_file.read_text()
        
        # Parse metadata
        parser = OrientationMetadataParser()
        metadata = parser.extract_inline_metadata(content, example_file)
        
        # Create OrientationQuery from metadata (excluding 'orientation' marker field)
        query = OrientationQuery(
            query=metadata['query'],
            priority=metadata['priority'],
            description=metadata.get('description'),
            category=metadata.get('category')
        )
        
        # Verify query is valid
        assert query.query == "inline metadata pattern project orientation markdown co-located"
        assert query.priority == 1
        assert query.description == "Learn the inline metadata pattern for project orientation"
        assert query.category == "documentation"
        
        print("\n✅ Inline example: End-to-end discovery and parsing successful")
    
    def test_config_example_discovered_and_validated(self):
        """
        Test that config example can be loaded and validated end-to-end.
        
        Simulates: YAML file → parsed data → ProjectConfig → queries validated
        """
        example_file = Path("dist/universal/templates/orientation/mcp.yaml.example")
        content = example_file.read_text()
        data = yaml.safe_load(content)
        
        # Create ProjectConfig
        project_config = ProjectConfig(**data['project'])
        
        # Verify orientation is enabled
        assert project_config.orientation.enabled is True
        
        # Verify all queries are valid
        queries = project_config.orientation.queries
        assert len(queries) >= 7
        
        # Verify priority distribution
        priority_1 = [q for q in queries if q.priority == 1]
        priority_2 = [q for q in queries if q.priority == 2]
        priority_3 = [q for q in queries if q.priority == 3]
        
        assert len(priority_1) >= 2, "Should have 2+ priority 1 queries"
        assert len(priority_2) >= 2, "Should have 2+ priority 2 queries"
        assert len(priority_3) >= 2, "Should have 2+ priority 3 queries"
        
        print("\n✅ Config example: End-to-end validation successful")
        print(f"   Total queries: {len(queries)}")
        print(f"   Priority 1: {len(priority_1)}")
        print(f"   Priority 2: {len(priority_2)}")
        print(f"   Priority 3: {len(priority_3)}")
    
    def test_both_examples_can_be_merged(self):
        """
        Test that inline and config examples can be merged (simulating discovery).
        
        This verifies both examples could work together in a real project.
        """
        # Load inline example
        inline_file = Path("dist/universal/templates/orientation/PROJECT-ORIENTATION-EXAMPLE.md")
        inline_content = inline_file.read_text()
        parser = OrientationMetadataParser()
        inline_metadata = parser.extract_inline_metadata(inline_content, inline_file)
        
        # Remove 'orientation' field (discovery marker, not part of model)
        query_data = {k: v for k, v in inline_metadata.items() if k != 'orientation'}
        inline_query = OrientationQuery(**query_data)
        
        # Load config example
        config_file = Path("dist/universal/templates/orientation/mcp.yaml.example")
        config_content = config_file.read_text()
        config_data = yaml.safe_load(config_content)
        project_config = ProjectConfig(**config_data['project'])
        config_queries = project_config.orientation.queries
        
        # Merge (simulated)
        all_queries = [inline_query] + config_queries
        
        # Verify no duplicates (query strings are different)
        query_strings = [q.query for q in all_queries]
        assert len(query_strings) == len(set(query_strings)), "Examples should have unique queries"
        
        # Verify total count
        assert len(all_queries) >= 8, f"Expected 8+ total queries, got {len(all_queries)}"
        
        print(f"\n✅ Both examples can be merged: {len(all_queries)} unique queries")

