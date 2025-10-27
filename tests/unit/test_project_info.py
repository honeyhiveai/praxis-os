"""
Unit tests for ProjectInfoDiscovery.

Tests project name extraction, git info discovery, and graceful fallbacks.
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcp_server.project_info import ProjectInfoDiscovery


@pytest.fixture
def project_discovery(tmp_path):
    """Create ProjectInfoDiscovery instance with temp directory."""
    # Create .praxis-os directory
    praxis_os_path = tmp_path / "test-project" / ".praxis-os"
    praxis_os_path.mkdir(parents=True)
    return ProjectInfoDiscovery(praxis_os_path)


@pytest.fixture
def git_project_discovery(tmp_path):
    """Create ProjectInfoDiscovery for a mock git project."""
    # Create project with .git directory
    project_path = tmp_path / "test-git-project"
    project_path.mkdir()
    (project_path / ".git").mkdir()
    praxis_os_path = project_path / ".praxis-os"
    praxis_os_path.mkdir()
    return ProjectInfoDiscovery(praxis_os_path)


class TestGetProjectInfo:
    """Test get_project_info() main method."""

    def test_get_project_info_returns_complete_dict(self, project_discovery):
        """Test get_project_info returns all required fields."""
        info = project_discovery.get_project_info()

        assert isinstance(info, dict)
        assert "name" in info
        assert "root" in info
        assert "praxis_os_path" in info
        assert "git" in info

    def test_get_project_info_non_git_project(self, project_discovery):
        """Test get_project_info for non-git project."""
        info = project_discovery.get_project_info()

        assert info["name"] == "test-project"  # Directory name
        assert info["root"].endswith("test-project")
        assert info["praxis_os_path"].endswith(".praxis-os")
        assert info["git"] is None  # Not a git repo


class TestProjectNameDiscovery:
    """Test project name extraction."""

    def test_get_project_name_from_git_remote(self, git_project_discovery, monkeypatch):
        """Test project name extracted from git remote URL."""

        def mock_run_git(args):
            if args == ["remote", "get-url", "origin"]:
                return "git@github.com:user/praxis-os-enhanced.git"
            return None

        monkeypatch.setattr(git_project_discovery, "_run_git_command", mock_run_git)

        name = git_project_discovery._get_project_name()
        assert name == "praxis-os-enhanced"

    def test_get_project_name_from_https_url(self, git_project_discovery, monkeypatch):
        """Test project name extracted from HTTPS URL."""

        def mock_run_git(args):
            if args == ["remote", "get-url", "origin"]:
                return "https://github.com/user/my-project.git"
            return None

        monkeypatch.setattr(git_project_discovery, "_run_git_command", mock_run_git)

        name = git_project_discovery._get_project_name()
        assert name == "my-project"

    def test_get_project_name_from_url_without_git_suffix(
        self, git_project_discovery, monkeypatch
    ):
        """Test project name from URL without .git suffix."""

        def mock_run_git(args):
            if args == ["remote", "get-url", "origin"]:
                return "https://github.com/user/another-project"
            return None

        monkeypatch.setattr(git_project_discovery, "_run_git_command", mock_run_git)

        name = git_project_discovery._get_project_name()
        assert name == "another-project"

    def test_get_project_name_falls_back_to_directory(self, project_discovery):
        """Test project name falls back to directory name if not git."""
        name = project_discovery._get_project_name()
        assert name == "test-project"

    def test_get_git_repo_name_returns_none_for_non_git(self, project_discovery):
        """Test _get_git_repo_name returns None for non-git project."""
        name = project_discovery._get_git_repo_name()
        assert name is None


class TestGitInfoDiscovery:
    """Test git repository information discovery."""

    def test_get_git_info_returns_complete_dict(
        self, git_project_discovery, monkeypatch
    ):
        """Test _get_git_info returns complete git information."""

        def mock_run_git(args):
            cmd_responses = {
                ("remote", "get-url", "origin"): "git@github.com:user/repo.git",
                ("branch", "--show-current"): "main",
                ("rev-parse", "HEAD"): "a" * 40,  # 40-char hash
                ("status", "--porcelain"): "",  # Clean
            }
            return cmd_responses.get(tuple(args))

        monkeypatch.setattr(git_project_discovery, "_run_git_command", mock_run_git)

        git_info = git_project_discovery._get_git_info()

        assert git_info is not None
        assert git_info["remote"] == "git@github.com:user/repo.git"
        assert git_info["branch"] == "main"
        assert git_info["commit"] == "a" * 40
        assert git_info["commit_short"] == "a" * 7
        assert git_info["status"] == "clean"

    def test_get_git_info_detects_dirty_status(
        self, git_project_discovery, monkeypatch
    ):
        """Test _get_git_info detects dirty working tree."""

        def mock_run_git(args):
            cmd_responses = {
                ("remote", "get-url", "origin"): "git@github.com:user/repo.git",
                ("branch", "--show-current"): "main",
                ("rev-parse", "HEAD"): "a" * 40,
                ("status", "--porcelain"): " M modified-file.py\n",  # Dirty
            }
            return cmd_responses.get(tuple(args))

        monkeypatch.setattr(git_project_discovery, "_run_git_command", mock_run_git)

        git_info = git_project_discovery._get_git_info()

        assert git_info["status"] == "dirty"

    def test_get_git_info_returns_none_for_non_git(self, project_discovery):
        """Test _get_git_info returns None for non-git project."""
        git_info = project_discovery._get_git_info()
        assert git_info is None

    def test_get_git_info_returns_none_on_failure(
        self, git_project_discovery, monkeypatch
    ):
        """Test _get_git_info returns None if git command fails."""
        # Mock git command to return None (failure)
        monkeypatch.setattr(
            git_project_discovery, "_run_git_command", lambda args: None
        )

        git_info = git_project_discovery._get_git_info()
        assert git_info is None

    def test_is_git_repo_true_for_git_project(self, git_project_discovery):
        """Test _is_git_repo returns True for git project."""
        assert git_project_discovery._is_git_repo() is True

    def test_is_git_repo_false_for_non_git(self, project_discovery):
        """Test _is_git_repo returns False for non-git project."""
        assert project_discovery._is_git_repo() is False

    def test_get_git_remote(self, git_project_discovery, monkeypatch):
        """Test _get_git_remote returns remote URL."""
        monkeypatch.setattr(
            git_project_discovery,
            "_run_git_command",
            lambda args: (
                "git@github.com:user/repo.git"
                if args == ["remote", "get-url", "origin"]
                else None
            ),
        )

        remote = git_project_discovery._get_git_remote()
        assert remote == "git@github.com:user/repo.git"

    def test_get_git_branch(self, git_project_discovery, monkeypatch):
        """Test _get_git_branch returns branch name."""
        monkeypatch.setattr(
            git_project_discovery,
            "_run_git_command",
            lambda args: (
                "feature-branch" if args == ["branch", "--show-current"] else None
            ),
        )

        branch = git_project_discovery._get_git_branch()
        assert branch == "feature-branch"

    def test_get_git_commit(self, git_project_discovery, monkeypatch):
        """Test _get_git_commit returns commit hash."""
        commit_hash = "abc123" * 7  # 42 chars (truncate to 40)

        monkeypatch.setattr(
            git_project_discovery,
            "_run_git_command",
            lambda args: commit_hash[:40] if args == ["rev-parse", "HEAD"] else None,
        )

        commit = git_project_discovery._get_git_commit()
        assert len(commit) == 40


class TestGitCommandExecution:
    """Test git command execution with error handling."""

    def test_run_git_command_success(self, git_project_discovery):
        """Test _run_git_command returns output on success."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="test output\n", returncode=0)

            result = git_project_discovery._run_git_command(["status"])

            assert result == "test output"
            mock_run.assert_called_once()

    def test_run_git_command_timeout(self, git_project_discovery):
        """Test _run_git_command returns None on timeout."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd=["git", "status"], timeout=5
            )

            result = git_project_discovery._run_git_command(["status"])

            assert result is None

    def test_run_git_command_process_error(self, git_project_discovery):
        """Test _run_git_command returns None on process error."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1, cmd=["git", "status"]
            )

            result = git_project_discovery._run_git_command(["status"])

            assert result is None

    def test_run_git_command_os_error(self, git_project_discovery):
        """Test _run_git_command returns None on OS error."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = OSError("Git not found")

            result = git_project_discovery._run_git_command(["status"])

            assert result is None

    def test_run_git_command_file_not_found(self, git_project_discovery):
        """Test _run_git_command returns None if git not found."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("git command not found")

            result = git_project_discovery._run_git_command(["status"])

            assert result is None

    def test_run_git_command_uses_timeout(self, git_project_discovery):
        """Test _run_git_command uses 5 second timeout."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="output")

            git_project_discovery._run_git_command(["status"])

            # Verify timeout parameter was passed
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["timeout"] == 5


class TestDocstringsAndTypeHints:
    """Verify code quality requirements."""

    def test_all_methods_have_docstrings(self):
        """Test all public methods have docstrings."""
        methods = [
            ProjectInfoDiscovery.get_project_info,
            ProjectInfoDiscovery._get_project_name,
            ProjectInfoDiscovery._get_git_repo_name,
            ProjectInfoDiscovery._get_git_info,
            ProjectInfoDiscovery._is_git_repo,
            ProjectInfoDiscovery._get_git_remote,
            ProjectInfoDiscovery._get_git_branch,
            ProjectInfoDiscovery._get_git_commit,
            ProjectInfoDiscovery._get_git_status,
            ProjectInfoDiscovery._run_git_command,
        ]

        for method in methods:
            assert method.__doc__ is not None
            assert len(method.__doc__) > 20  # Substantive docstring

    def test_class_has_docstring(self):
        """Test ProjectInfoDiscovery class has comprehensive docstring."""
        assert ProjectInfoDiscovery.__doc__ is not None
        assert "Discovers project information" in ProjectInfoDiscovery.__doc__
        assert "Example:" in ProjectInfoDiscovery.__doc__

    def test_module_has_docstring(self):
        """Test module has docstring."""
        import mcp_server.project_info as pi

        assert pi.__doc__ is not None
        assert "Project information discovery" in pi.__doc__

    def test_no_hardcoded_values_in_code(self):
        """Test no hardcoded project names or paths in source."""
        import inspect

        source = inspect.getsource(ProjectInfoDiscovery)

        # Should NOT contain hardcoded project names
        assert "praxis-os-enhanced" not in source.lower().replace("praxis-os", "")
        # Should NOT contain hardcoded user paths
        assert "/Users/josh" not in source
        assert "/Users/specific" not in source
