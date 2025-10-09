"""
Unit tests for DependencyInstaller.

Tests dependency installation and post-install step handling.
"""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from mcp_server.dependency_installer import DependencyInstaller


@pytest.fixture
def installer():
    """Create DependencyInstaller instance."""
    return DependencyInstaller()


@pytest.fixture
def mock_requirements_file(tmp_path):
    """Create a mock requirements.txt file."""
    req_file = tmp_path / "requirements.txt"
    req_file.write_text(
        "pytest==8.0.0\n"
        "requests==2.31.0\n"
        "playwright==1.40.0\n"
    )
    return req_file


class TestInstallDependencies:
    """Tests for install_dependencies method."""
    
    def test_install_dependencies_file_not_found(self, installer):
        """Test installation fails gracefully when requirements file not found."""
        result = installer.install_dependencies("/nonexistent/requirements.txt")
        
        assert result["success"] is False
        assert result["packages_installed"] == 0
        assert len(result["errors"]) > 0
        assert "not found" in result["errors"][0].lower()
    
    @patch('subprocess.run')
    def test_install_dependencies_success(self, mock_run, installer, mock_requirements_file):
        """Test successful dependency installation."""
        # Mock successful pip install
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Successfully installed pytest-8.0.0 requests-2.31.0 playwright-1.40.0",
            stderr=""
        )
        
        result = installer.install_dependencies(str(mock_requirements_file))
        
        assert result["success"] is True
        assert result["packages_installed"] == 1  # Count of "Successfully installed" occurrences
        assert len(result["errors"]) == 0
        assert "pytest" in result["output"] or "Successfully" in result["output"]
    
    @patch('subprocess.run')
    def test_install_dependencies_failure(self, mock_run, installer, mock_requirements_file):
        """Test dependency installation failure."""
        # Mock failed pip install
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="ERROR: Could not find a version that satisfies the requirement"
        )
        
        result = installer.install_dependencies(str(mock_requirements_file))
        
        assert result["success"] is False
        assert result["packages_installed"] == 0
        assert len(result["errors"]) > 0
    
    @patch('subprocess.run')
    def test_install_dependencies_timeout(self, mock_run, installer, mock_requirements_file):
        """Test dependency installation timeout."""
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd="pip install", timeout=300
        )
        
        result = installer.install_dependencies(str(mock_requirements_file))
        
        assert result["success"] is False
        assert "timed out" in result["errors"][0].lower()


class TestDetectPostInstallSteps:
    """Tests for detect_post_install_steps method."""
    
    def test_detect_playwright_post_install(self, installer, tmp_path):
        """Test detection of playwright post-install step."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("playwright==1.40.0\n")
        
        steps = installer.detect_post_install_steps(str(req_file))
        
        assert len(steps) == 1
        assert steps[0]["package"] == "playwright"
        assert "playwright install chromium" in steps[0]["command"]
        assert "Chromium" in steps[0]["description"]
    
    def test_detect_no_post_install_steps(self, installer, tmp_path):
        """Test when no post-install steps are needed."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("pytest==8.0.0\nrequests==2.31.0\n")
        
        steps = installer.detect_post_install_steps(str(req_file))
        
        assert len(steps) == 0
    
    def test_detect_playwright_case_insensitive(self, installer, tmp_path):
        """Test playwright detection is case-insensitive."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("Playwright==1.40.0\n")
        
        steps = installer.detect_post_install_steps(str(req_file))
        
        assert len(steps) == 1
        assert steps[0]["package"] == "playwright"
    
    def test_detect_post_install_file_not_found(self, installer):
        """Test detection handles missing requirements file."""
        steps = installer.detect_post_install_steps("/nonexistent/requirements.txt")
        
        assert len(steps) == 0


class TestRunPostInstallSteps:
    """Tests for run_post_install_steps method."""
    
    @patch('subprocess.run')
    def test_run_post_install_steps_success(self, mock_run, installer):
        """Test successful post-install step execution."""
        # Mock successful playwright install
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Chromium 119.0.6045.9 (playwright build v1091) downloaded to /path\n129.7 MB",
            stderr=""
        )
        
        steps = [
            {
                "package": "playwright",
                "command": "playwright install chromium",
                "description": "Install Chromium"
            }
        ]
        
        results = installer.run_post_install_steps(steps)
        
        assert len(results) == 1
        assert results[0]["status"] == "success"
        assert results[0]["command"] == "playwright install chromium"
        assert results[0]["size_downloaded"] is not None
    
    @patch('subprocess.run')
    def test_run_post_install_steps_failure(self, mock_run, installer):
        """Test failed post-install step execution."""
        # Mock failed command
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Error: Command failed"
        )
        
        steps = [
            {
                "package": "playwright",
                "command": "playwright install chromium",
                "description": "Install Chromium"
            }
        ]
        
        results = installer.run_post_install_steps(steps)
        
        assert len(results) == 1
        assert results[0]["status"] == "failed"
    
    @patch('subprocess.run')
    def test_run_post_install_steps_timeout(self, mock_run, installer):
        """Test post-install step timeout."""
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd="playwright install chromium", timeout=300
        )
        
        steps = [
            {
                "package": "playwright",
                "command": "playwright install chromium",
                "description": "Install Chromium"
            }
        ]
        
        results = installer.run_post_install_steps(steps)
        
        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert "timed out" in results[0]["output"].lower()
    
    def test_run_post_install_steps_empty(self, installer):
        """Test running no post-install steps."""
        results = installer.run_post_install_steps([])
        
        assert len(results) == 0
    
    @patch('subprocess.run')
    def test_run_multiple_post_install_steps(self, mock_run, installer):
        """Test running multiple post-install steps."""
        # Mock successful execution for both
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Success",
            stderr=""
        )
        
        steps = [
            {
                "package": "playwright",
                "command": "playwright install chromium",
                "description": "Install Chromium"
            },
            {
                "package": "playwright",
                "command": "playwright install firefox",
                "description": "Install Firefox"
            }
        ]
        
        results = installer.run_post_install_steps(steps)
        
        assert len(results) == 2
        assert all(r["status"] == "success" for r in results)


class TestIntegration:
    """Integration tests for DependencyInstaller."""
    
    @patch('subprocess.run')
    def test_full_installation_flow(self, mock_run, installer, mock_requirements_file):
        """Test complete installation flow with post-install steps."""
        # Mock pip install success
        def mock_run_side_effect(*args, **kwargs):
            if "pip install" in " ".join(args[0]):
                return Mock(
                    returncode=0,
                    stdout="Successfully installed playwright-1.40.0",
                    stderr=""
                )
            elif "playwright install" in " ".join(args[0]):
                return Mock(
                    returncode=0,
                    stdout="Chromium downloaded",
                    stderr=""
                )
            return Mock(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        # Install dependencies
        install_result = installer.install_dependencies(str(mock_requirements_file))
        assert install_result["success"] is True
        
        # Detect post-install steps
        post_install_steps = installer.detect_post_install_steps(str(mock_requirements_file))
        assert len(post_install_steps) == 1
        
        # Run post-install steps
        post_install_results = installer.run_post_install_steps(post_install_steps)
        assert len(post_install_results) == 1
        assert post_install_results[0]["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

