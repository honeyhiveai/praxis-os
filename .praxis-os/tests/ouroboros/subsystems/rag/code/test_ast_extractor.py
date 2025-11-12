"""Tests for ASTExtractor node type configuration and fallback logic."""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ouroboros.subsystems.rag.code.graph.ast import ASTExtractor


class TestASTExtractorConfigDriven:
    """Test ASTExtractor config-driven node type extraction."""

    def test_config_driven_node_types_python(self, tmp_path):
        """Test reading Python node types from config."""
        config = {
            "language_configs": {
                "python": {
                    "chunking": {
                        "import_nodes": ["import_statement", "import_from_statement"],
                        "definition_nodes": ["function_definition", "class_definition"],
                        "split_boundary_nodes": ["if_statement", "for_statement"],
                    }
                }
            }
        }
        
        extractor = ASTExtractor(languages=["python"], base_path=tmp_path, config=config)
        node_types = extractor._get_significant_node_types("python")
        
        # Should return union of all node type categories
        assert "import_statement" in node_types
        assert "import_from_statement" in node_types
        assert "function_definition" in node_types
        assert "class_definition" in node_types
        assert "if_statement" in node_types
        assert "for_statement" in node_types
        assert len(node_types) == 6

    def test_config_driven_node_types_typescript(self, tmp_path):
        """Test reading TypeScript node types from config."""
        config = {
            "language_configs": {
                "typescript": {
                    "chunking": {
                        "import_nodes": ["import_statement", "export_statement"],
                        "definition_nodes": ["function_declaration", "arrow_function", "class_declaration"],
                        "split_boundary_nodes": ["if_statement"],
                    }
                }
            }
        }
        
        extractor = ASTExtractor(languages=["typescript"], base_path=tmp_path, config=config)
        node_types = extractor._get_significant_node_types("typescript")
        
        assert "import_statement" in node_types
        assert "export_statement" in node_types
        assert "function_declaration" in node_types
        assert "arrow_function" in node_types
        assert "class_declaration" in node_types
        assert "if_statement" in node_types
        assert len(node_types) == 6


class TestASTExtractorFallback:
    """Test ASTExtractor fallback logic for unconfigured languages."""

    def test_fallback_python_without_config(self, tmp_path, caplog):
        """Test fallback to hardcoded defaults for Python when config missing."""
        caplog.set_level(logging.WARNING)
        
        # No config provided
        extractor = ASTExtractor(languages=["python"], base_path=tmp_path, config=None)
        node_types = extractor._get_significant_node_types("python")
        
        # Should use hardcoded Python defaults
        assert "function_definition" in node_types
        assert "class_definition" in node_types
        assert "import_statement" in node_types
        
        # Should log warning about missing config
        assert "not found in config" in caplog.text
        assert "falling back to hardcoded defaults" in caplog.text

    def test_fallback_javascript_without_config(self, tmp_path, caplog):
        """Test fallback to hardcoded defaults for JavaScript when config missing."""
        caplog.set_level(logging.WARNING)
        
        extractor = ASTExtractor(languages=["javascript"], base_path=tmp_path, config=None)
        node_types = extractor._get_significant_node_types("javascript")
        
        # Should use hardcoded JavaScript defaults
        assert "function_declaration" in node_types
        assert "class_declaration" in node_types
        assert "import_statement" in node_types
        
        # Should log warning
        assert "not found in config" in caplog.text

    def test_fallback_unconfigured_language_ruby(self, tmp_path, caplog):
        """Test fallback to generic defaults for completely unconfigured language (Ruby)."""
        caplog.set_level(logging.WARNING)
        
        # Ruby not in config and not in hardcoded defaults
        extractor = ASTExtractor(languages=["ruby"], base_path=tmp_path, config=None)
        node_types = extractor._get_significant_node_types("ruby")
        
        # Should return generic fallback types
        assert "function_definition" in node_types or "function_declaration" in node_types
        assert "class_definition" in node_types or "class_declaration" in node_types
        assert len(node_types) == 4  # Generic fallback has 4 types
        
        # Should log TWO warnings: missing config + no hardcoded defaults
        warnings = [record for record in caplog.records if record.levelno == logging.WARNING]
        assert len(warnings) == 2
        assert "not found in config" in caplog.text
        assert "No hardcoded defaults" in caplog.text
        assert "generic fallback" in caplog.text

    def test_fallback_unconfigured_language_rust(self, tmp_path, caplog):
        """Test fallback for another unconfigured language (Rust)."""
        caplog.set_level(logging.WARNING)
        
        extractor = ASTExtractor(languages=["rust"], base_path=tmp_path, config=None)
        node_types = extractor._get_significant_node_types("rust")
        
        # Should return generic fallback
        assert len(node_types) == 4
        assert "function_definition" in node_types or "function_declaration" in node_types
        
        # Should log warnings guiding user to add config
        assert "Add language config to mcp.yaml" in caplog.text

    def test_no_crash_on_unconfigured_language(self, tmp_path):
        """Test that unconfigured languages don't raise exceptions (graceful degradation)."""
        extractor = ASTExtractor(languages=["elixir"], base_path=tmp_path, config=None)
        
        # Should not crash
        node_types = extractor._get_significant_node_types("elixir")
        
        # Should return some fallback types
        assert isinstance(node_types, set)
        assert len(node_types) > 0


class TestASTExtractorBackwardCompatibility:
    """Test backward compatibility (works without config parameter)."""

    def test_initialization_without_config(self, tmp_path):
        """Test ASTExtractor can be initialized without config parameter."""
        # Old-style initialization (no config)
        extractor = ASTExtractor(languages=["python"], base_path=tmp_path)
        
        assert extractor.languages == ["python"]
        assert extractor.base_path == tmp_path
        assert extractor.lang_configs == {}  # Empty dict when no config

    def test_works_without_config_parameter(self, tmp_path, caplog):
        """Test that AST extraction works when config parameter not provided."""
        caplog.set_level(logging.WARNING)
        
        extractor = ASTExtractor(languages=["python"], base_path=tmp_path)
        node_types = extractor._get_significant_node_types("python")
        
        # Should fall back to hardcoded defaults
        assert "function_definition" in node_types
        assert "class_definition" in node_types
        
        # Should log warning about missing config
        assert "not found in config" in caplog.text


class TestASTExtractorConfigDebugLogging:
    """Test debug logging when config is successfully used."""

    def test_debug_log_on_config_success(self, tmp_path, caplog):
        """Test that debug log is emitted when config-driven path succeeds."""
        caplog.set_level(logging.DEBUG)
        
        config = {
            "language_configs": {
                "python": {
                    "chunking": {
                        "import_nodes": ["import_statement"],
                        "definition_nodes": ["function_definition"],
                        "split_boundary_nodes": [],
                    }
                }
            }
        }
        
        extractor = ASTExtractor(languages=["python"], base_path=tmp_path, config=config)
        node_types = extractor._get_significant_node_types("python")
        
        # Should log debug message with node type count
        assert "Using config-driven node types for python" in caplog.text
        assert "2 types" in caplog.text  # 2 node types configured
        
        # Should NOT log any warnings (config path succeeded)
        warnings = [record for record in caplog.records if record.levelno == logging.WARNING]
        assert len(warnings) == 0

