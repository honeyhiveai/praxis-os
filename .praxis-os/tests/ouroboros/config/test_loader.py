"""
Unit tests for ouroboros.config.loader.

Tests config loading utilities including:
    - find_config_file() path discovery
    - load_config() with various options
    - Error handling and messages
    - Path validation
"""

import tempfile
from pathlib import Path

import pytest
from ouroboros.config.loader import find_config_file, load_config


class TestFindConfigFile:
    """Test find_config_file() path discovery."""

    def test_find_config_file_in_current_dir(self):
        """find_config_file() should find config in current directory."""
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(
                tmpdir
            ).resolve()  # Resolve to handle /private symlink on macOS
            config_dir = tmppath / ".praxis-os" / "config"
            config_dir.mkdir(parents=True)
            config_file = config_dir / "mcp.yaml"
            config_file.write_text("version: '1.0'")

            # Find from tmpdir
            result = find_config_file(tmppath)
            assert result == config_file

    def test_find_config_file_in_parent_dir(self):
        """find_config_file() should find config in parent directory."""
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(
                tmpdir
            ).resolve()  # Resolve to handle /private symlink on macOS
            config_dir = tmppath / ".praxis-os" / "config"
            config_dir.mkdir(parents=True)
            config_file = config_dir / "mcp.yaml"
            config_file.write_text("version: '1.0'")

            # Create subdirectory
            subdir = tmppath / "subdir"
            subdir.mkdir()

            # Find from subdir
            result = find_config_file(subdir)
            assert result == config_file

    def test_find_config_file_not_found(self):
        """find_config_file() should return None if not found."""
        # Use a temporary directory without config
        with tempfile.TemporaryDirectory() as tmpdir:
            result = find_config_file(Path(tmpdir))
            assert result is None


class TestLoadConfig:
    """Test load_config() function."""

    def test_load_config_with_explicit_path(self):
        """load_config() should load config from explicit path."""
        yaml_content = """
version: "1.0"

indexes:
  standards:
    source_paths:
      - "universal/standards"
    vector:
      chunk_size: 500
    fts:
      enabled: true
  code:
    source_paths:
      - "src/"
    languages:
      - "python"
    vector:
      chunk_size: 500
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
  evidence_schemas_exposed: false

browser: {}

logging: {}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)

        try:
            config = load_config(
                config_path=temp_path,
                validate_paths=False,  # Skip path validation for test
                auto_find=False,
            )

            assert config.version == "1.0"
            assert config.indexes.standards.source_paths == ["universal/standards"]
        finally:
            temp_path.unlink()

    def test_load_config_missing_file_exits(self):
        """load_config() should exit with code 1 for missing file."""
        with pytest.raises(SystemExit) as exc_info:
            load_config(
                config_path=Path("nonexistent/config.yaml"),
                auto_find=False,
            )
        assert exc_info.value.code == 1

    def test_load_config_invalid_yaml_exits(self):
        """load_config() should exit with code 1 for invalid YAML."""
        yaml_content = """
version: "1.0"
invalid: [unclosed bracket
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)

        try:
            with pytest.raises(SystemExit) as exc_info:
                load_config(
                    config_path=temp_path,
                    validate_paths=False,
                    auto_find=False,
                )
            assert exc_info.value.code == 1
        finally:
            temp_path.unlink()

    def test_load_config_validation_error_exits(self):
        """load_config() should exit with code 1 for validation errors."""
        yaml_content = """
version: "invalid_version"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)

        try:
            with pytest.raises(SystemExit) as exc_info:
                load_config(
                    config_path=temp_path,
                    validate_paths=False,
                    auto_find=False,
                )
            assert exc_info.value.code == 1
        finally:
            temp_path.unlink()

    def test_load_config_skip_path_validation(self):
        """load_config() should skip path validation when validate_paths=False."""
        yaml_content = """
version: "1.0"
base_path: "nonexistent/path"

indexes:
  standards:
    source_paths:
      - "universal/standards"
    vector: {}
    fts: {}
  code:
    source_paths:
      - "src/"
    languages:
      - "python"
    vector: {}
    fts: {}
    graph: {}
  ast:
    source_paths:
      - "src/"
    languages:
      - "python"
  file_watcher: {}

workflow:
  evidence_schemas_exposed: false

browser: {}

logging: {}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)

        try:
            # Should succeed because validate_paths=False
            config = load_config(
                config_path=temp_path,
                validate_paths=False,
                auto_find=False,
            )
            assert config.version == "1.0"
            assert config.base_path == Path("nonexistent/path")
        finally:
            temp_path.unlink()

    def test_load_config_with_path_validation_failure(self):
        """load_config() should exit if path validation fails."""
        yaml_content = """
version: "1.0"
base_path: "nonexistent/path/that/does/not/exist"

indexes:
  standards:
    source_paths:
      - "universal/standards"
  code:
    languages:
      - "python"
  ast:
    languages:
      - "python"

workflow:
  evidence_schemas_exposed: false

browser: {}

logging: {}
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = Path(f.name)

        try:
            with pytest.raises(SystemExit) as exc_info:
                load_config(
                    config_path=temp_path,
                    validate_paths=True,  # Enable path validation
                    auto_find=False,
                )
            assert exc_info.value.code == 1
        finally:
            temp_path.unlink()

    def test_load_config_auto_find_not_found_exits(self):
        """load_config() should exit if auto_find enabled but config not found."""
        # Use a temporary directory without config
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp dir without config
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                with pytest.raises(SystemExit) as exc_info:
                    load_config(auto_find=True)
                assert exc_info.value.code == 1
            finally:
                os.chdir(original_cwd)


class TestLoadConfigIntegration:
    """Integration tests for load_config() with real config structures."""

    def test_load_config_complete_valid_config(self):
        """load_config() should successfully load a complete valid config."""
        yaml_content = """
version: "1.0"

indexes:
  standards:
    source_paths:
      - "universal/standards"
    vector:
      model: "text-embedding-3-small"
      chunk_size: 500
      chunk_overlap: 100
    fts:
      enabled: true
  code:
    source_paths:
      - "src/"
    languages:
      - "python"
      - "typescript"
    vector:
      model: "text-embedding-3-small"
    fts: {}
    graph: {}
  ast:
    source_paths:
      - "src/"
    languages:
      - "python"
    auto_install_parsers: true
  file_watcher: {}

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
            config = load_config(
                config_path=temp_path,
                validate_paths=False,
                auto_find=False,
            )

            # Verify all subsystems loaded correctly
            assert config.version == "1.0"
            assert config.indexes.standards.source_paths == ["universal/standards"]
            assert config.indexes.standards.vector.model == "text-embedding-3-small"
            assert config.indexes.code.languages == ["python", "typescript"]
            assert config.workflow.session_timeout_minutes == 1440
            assert config.workflow.evidence_schemas_exposed is False
            assert config.browser.browser_type == "chromium"
            assert config.browser.max_sessions == 10
            assert config.logging.level == "INFO"
            assert config.logging.behavioral_metrics_enabled is True
        finally:
            temp_path.unlink()
