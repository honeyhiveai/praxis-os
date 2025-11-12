"""
Unit tests for ouroboros.config.schemas.mcp.

Tests MCPConfig (root config) validation including:
    - Default values
    - Subsystem composition
    - Version validation
    - YAML loading
    - Path validation
    - Error message quality
"""

import tempfile
from pathlib import Path

import pytest
from ouroboros.config.schemas.browser import BrowserConfig
from ouroboros.config.schemas.indexes import (
    ASTIndexConfig,
    CodeIndexConfig,
    FileWatcherConfig,
    FTSConfig,
    GraphConfig,
    IndexesConfig,
    StandardsIndexConfig,
    VectorConfig,
)
from ouroboros.config.schemas.logging import LoggingConfig
from ouroboros.config.schemas.mcp import MCPConfig
from ouroboros.config.schemas.workflow import WorkflowConfig
from pydantic import ValidationError


@pytest.fixture
def minimal_indexes_config():
    """Create minimal IndexesConfig for testing."""
    return IndexesConfig(
        standards=StandardsIndexConfig(
            source_paths=["universal/standards"],
            vector=VectorConfig(),
            fts=FTSConfig(),
        ),
        code=CodeIndexConfig(
            source_paths=["src/"],
            languages=["python"],
            vector=VectorConfig(),
            fts=FTSConfig(),
            graph=GraphConfig(),
        ),
        ast=ASTIndexConfig(
            source_paths=["src/"],
            languages=["python"],
        ),
        file_watcher=FileWatcherConfig(),
    )


class TestMCPConfigCreation:
    """Test MCPConfig creation and composition."""

    def test_mcp_config_minimal(self, minimal_indexes_config):
        """MCPConfig should compose all subsystem configs."""
        config = MCPConfig(
            version="1.0",
            indexes=minimal_indexes_config,
            workflow=WorkflowConfig(),
            browser=BrowserConfig(),
            logging=LoggingConfig(),
        )

        assert config.version == "1.0"
        assert config.base_path == Path(".praxis-os")
        assert isinstance(config.indexes, IndexesConfig)
        assert isinstance(config.workflow, WorkflowConfig)
        assert isinstance(config.browser, BrowserConfig)
        assert isinstance(config.logging, LoggingConfig)

    def test_mcp_config_custom_base_path(self, minimal_indexes_config):
        """MCPConfig should accept custom base_path."""
        config = MCPConfig(
            version="2.1",
            base_path=Path("custom/base"),
            indexes=minimal_indexes_config,
            workflow=WorkflowConfig(),
            browser=BrowserConfig(),
            logging=LoggingConfig(),
        )

        assert config.version == "2.1"
        assert config.base_path == Path("custom/base")

    def test_mcp_config_immutable(self, minimal_indexes_config):
        """MCPConfig should be immutable (frozen)."""
        config = MCPConfig(
            version="1.0",
            indexes=minimal_indexes_config,
            workflow=WorkflowConfig(),
            browser=BrowserConfig(),
            logging=LoggingConfig(),
        )

        with pytest.raises(ValidationError, match="frozen"):
            config.version = "2.0"


class TestMCPConfigVersionValidation:
    """Test version field validation."""

    def test_valid_versions(self, minimal_indexes_config):
        """MCPConfig should accept valid semantic versions."""
        valid_versions = ["1.0", "2.1", "10.5", "99.99"]
        for version in valid_versions:
            config = MCPConfig(
                version=version,
                indexes=minimal_indexes_config,
                workflow=WorkflowConfig(),
                browser=BrowserConfig(),
                logging=LoggingConfig(),
            )
            assert config.version == version

    def test_invalid_version_missing_minor(self, minimal_indexes_config):
        """MCPConfig should reject version without minor component."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            MCPConfig(
                version="1",
                indexes=minimal_indexes_config,
                workflow=WorkflowConfig(),
                browser=BrowserConfig(),
                logging=LoggingConfig(),
            )

    def test_invalid_version_with_patch(self, minimal_indexes_config):
        """MCPConfig should reject version with patch component."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            MCPConfig(
                version="1.0.0",
                indexes=minimal_indexes_config,
                workflow=WorkflowConfig(),
                browser=BrowserConfig(),
                logging=LoggingConfig(),
            )

    def test_invalid_version_with_prefix(self, minimal_indexes_config):
        """MCPConfig should reject version with 'v' prefix."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            MCPConfig(
                version="v1.0",
                indexes=minimal_indexes_config,
                workflow=WorkflowConfig(),
                browser=BrowserConfig(),
                logging=LoggingConfig(),
            )


class TestMCPConfigRequiredFields:
    """Test required field validation."""

    def test_missing_version(self, minimal_indexes_config):
        """MCPConfig should require version field."""
        with pytest.raises(ValidationError, match="version"):
            MCPConfig(
                indexes=minimal_indexes_config,
                workflow=WorkflowConfig(),
                browser=BrowserConfig(),
                logging=LoggingConfig(),
            )

    def test_missing_indexes(self):
        """MCPConfig should require indexes field."""
        with pytest.raises(ValidationError, match="indexes"):
            MCPConfig(
                version="1.0",
                workflow=WorkflowConfig(),
                browser=BrowserConfig(),
                logging=LoggingConfig(),
            )

    def test_missing_workflow(self, minimal_indexes_config):
        """MCPConfig should require workflow field."""
        with pytest.raises(ValidationError, match="workflow"):
            MCPConfig(
                version="1.0",
                indexes=minimal_indexes_config,
                browser=BrowserConfig(),
                logging=LoggingConfig(),
            )

    def test_missing_browser(self, minimal_indexes_config):
        """MCPConfig should require browser field."""
        with pytest.raises(ValidationError, match="browser"):
            MCPConfig(
                version="1.0",
                indexes=minimal_indexes_config,
                workflow=WorkflowConfig(),
                logging=LoggingConfig(),
            )

    def test_missing_logging(self, minimal_indexes_config):
        """MCPConfig should require logging field."""
        with pytest.raises(ValidationError, match="logging"):
            MCPConfig(
                version="1.0",
                indexes=minimal_indexes_config,
                workflow=WorkflowConfig(),
                browser=BrowserConfig(),
            )


class TestMCPConfigYAMLLoading:
    """Test loading config from YAML files."""

    def test_from_yaml_valid_config(self, minimal_indexes_config):
        """MCPConfig.from_yaml() should load valid YAML config."""
        # Create temporary YAML config
        yaml_content = """
version: "1.0"
base_path: ".praxis-os"

indexes:
  standards:
    source_paths:
      - "universal/standards"
    vector:
      chunk_size: 500
      chunk_overlap: 12
    fts:
      enabled: true
  code:
    source_paths:
      - "src/"
    languages:
      - "python"
    vector:
      chunk_size: 500
      chunk_overlap: 12
    fts:
      enabled: true
    graph: {}
  ast:
    source_paths:
      - "src/"
    languages:
      - "python"
  file_watcher:
    enabled: true

workflow:
  workflows_dir: ".praxis-os/workflows"
  state_dir: ".praxis-os/workflow_states"
  session_timeout_minutes: 1440
  cleanup_completed_after_days: 30
  evidence_schemas_exposed: false

browser:
  browser_type: "chromium"
  headless: true
  max_sessions: 10
  session_timeout_minutes: 30
  # Note: screenshot_dir removed from BrowserConfig schema

logging:
  log_dir: ".praxis-os/logs"
  level: "INFO"
  format: "json"
  rotation_size_mb: 100
  max_files: 10
  behavioral_metrics_enabled: true
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)

        try:
            config = MCPConfig.from_yaml(temp_path)

            assert config.version == "1.0"
            assert config.base_path == Path(".praxis-os")
            assert config.indexes.standards.source_paths == ["universal/standards"]
            assert config.workflow.session_timeout_minutes == 1440
            assert config.browser.browser_type == "chromium"
            assert config.logging.level == "INFO"
        finally:
            temp_path.unlink()

    def test_from_yaml_missing_file(self):
        """MCPConfig.from_yaml() should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            MCPConfig.from_yaml(Path("nonexistent/config.yaml"))

    def test_from_yaml_invalid_yaml(self):
        """MCPConfig.from_yaml() should raise ValueError for invalid YAML."""
        yaml_content = """
version: "1.0"
indexes:
  - this is not valid YAML syntax: [unclosed bracket
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Failed to parse YAML"):
                MCPConfig.from_yaml(temp_path)
        finally:
            temp_path.unlink()

    def test_from_yaml_validation_error(self):
        """MCPConfig.from_yaml() should raise ValidationError for invalid config."""
        yaml_content = """
version: "invalid_version"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValidationError):
                MCPConfig.from_yaml(temp_path)
        finally:
            temp_path.unlink()


class TestMCPConfigPathValidation:
    """Test path validation functionality."""

    def test_validate_paths_with_valid_base_path(self, minimal_indexes_config):
        """validate_paths() should return empty list for valid paths."""
        config = MCPConfig(
            version="1.0",
            base_path=Path.cwd(),  # Current directory exists
            indexes=minimal_indexes_config,
            workflow=WorkflowConfig(),
            browser=BrowserConfig(),
            logging=LoggingConfig(),
        )

        errors = config.validate_paths()
        assert errors == []

    def test_validate_paths_with_invalid_base_path(self, minimal_indexes_config):
        """validate_paths() should return errors for invalid base_path."""
        config = MCPConfig(
            version="1.0",
            base_path=Path("nonexistent/base/path"),
            indexes=minimal_indexes_config,
            workflow=WorkflowConfig(),
            browser=BrowserConfig(),
            logging=LoggingConfig(),
        )

        errors = config.validate_paths()
        assert len(errors) > 0
        assert any("Base path does not exist" in error for error in errors)


class TestMCPConfigSerialization:
    """Test MCPConfig serialization."""

    def test_mcp_config_to_dict(self, minimal_indexes_config):
        """MCPConfig should serialize to dict with nested structure."""
        config = MCPConfig(
            version="1.0",
            indexes=minimal_indexes_config,
            workflow=WorkflowConfig(),
            browser=BrowserConfig(),
            logging=LoggingConfig(),
        )

        data = config.model_dump()
        assert data["version"] == "1.0"
        assert "indexes" in data
        assert "workflow" in data
        assert "browser" in data
        assert "logging" in data


class TestErrorMessages:
    """Test error message quality."""

    def test_version_error_message(self):
        """Error message for invalid version should be clear."""
        with pytest.raises(ValidationError) as exc_info:
            MCPConfig(
                version="1",
                indexes=minimal_indexes_config,
                workflow=WorkflowConfig(),
                browser=BrowserConfig(),
                logging=LoggingConfig(),
            )

        error_str = str(exc_info.value)
        assert "version" in error_str.lower()
        assert "pattern" in error_str.lower()
