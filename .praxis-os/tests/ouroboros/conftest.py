"""
Pytest fixtures for Ouroboros tests.

Provides isolated test environments with temporary configs and directories.
No test logic in production code - tests use dependency injection.
"""

import pytest
from pathlib import Path
from ouroboros.config.loader import load_config
from ouroboros.config.schemas.mcp import MCPConfig


@pytest.fixture
def test_base_path(tmp_path):
    """
    Create isolated test .praxis-os directory structure.
    
    Returns:
        Path to temporary .praxis-os directory
    """
    base_path = tmp_path / ".praxis-os"
    base_path.mkdir()
    
    # Create required subdirectories
    (base_path / "config").mkdir()
    (base_path / "cache" / "indexes").mkdir(parents=True)
    (base_path / "standards").mkdir()
    (base_path / "workflows").mkdir()
    
    return base_path


@pytest.fixture
def test_config(test_base_path):
    """
    Create minimal test MCP config in isolated test directory.
    
    Uses same schema as production but with test-safe defaults:
    - In-memory or temp paths for databases
    - Minimal required fields only
    - No path validation
    
    Returns:
        MCPConfig instance loaded from test config file
    """
    config_path = test_base_path / "config" / "mcp.yaml"
    
    # Create minimal test config
    test_config_yaml = """# Test Configuration (isolated from production)
version: "1.0"

indexes:
  standards:
    source_paths:
      - "standards/"
    vector:
      model: "sentence-transformers/all-MiniLM-L6-v2"
      dimension: 384
      chunk_size: 800
      chunk_overlap: 100
    fts: {}
    metadata_filtering:
      enabled: false  # Disable for faster tests
  
  code:
    source_paths:
      - "ouroboros/"
    languages:
      - "python"
    vector:
      model: "sentence-transformers/all-MiniLM-L6-v2"
      dimension: 384
      chunk_size: 200
      chunk_overlap: 20
    fts: {}
    graph: {}
  
  ast:
    source_paths:
      - "ouroboros/"
    languages:
      - "python"
    auto_install_parsers: false  # Skip parser install in tests
  
  file_watcher:
    enabled: false  # Disable watcher in tests

workflow:
  workflows_dir: "workflows/"
  state_dir: "state/"
  session_timeout_minutes: 60

browser:
  browser_type: "chromium"
  headless: true
  max_sessions: 5
  session_timeout_minutes: 15

logging:
  level: "WARNING"  # Reduce noise in tests
  format: "text"
  log_dir: "logs/"
  behavioral_metrics_enabled: false
"""
    
    config_path.write_text(test_config_yaml)
    
    # Load config using production loader (no test logic!)
    return load_config(config_path=config_path, validate_paths=False)

