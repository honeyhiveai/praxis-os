"""
Unit tests for __main__.py entry point.

Tests CLI argument parsing, directory finding, and main orchestration.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mcp_server.__main__ import find_praxis_os_directory, main


class TestFindAgentOsDirectory:
    """Test find_praxis_os_directory function."""

    def test_finds_in_current_directory(self, tmp_path, monkeypatch):
        """Test finding .praxis-os in current directory."""
        # Create .praxis-os in temp directory
        praxis_os_dir = tmp_path / ".praxis-os"
        praxis_os_dir.mkdir()

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        result = find_praxis_os_directory()

        assert result == praxis_os_dir

    def test_finds_in_home_directory(self, tmp_path, monkeypatch):
        """Test finding .praxis-os in home directory."""
        # Mock Path.cwd() to return non-existent dir
        mock_cwd = tmp_path / "nonexistent"

        # Create .praxis-os in home
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        praxis_os_dir = home_dir / ".praxis-os"
        praxis_os_dir.mkdir()

        with patch("mcp_server.__main__.Path.cwd", return_value=mock_cwd):
            with patch("mcp_server.__main__.Path.home", return_value=home_dir):
                result = find_praxis_os_directory()

                assert result == praxis_os_dir

    def test_exits_if_not_found(self, tmp_path, monkeypatch):
        """Test exits with error if .praxis-os not found."""
        # Change to temp directory without .praxis-os
        monkeypatch.chdir(tmp_path)

        # Mock all alternative paths to not exist
        nonexistent_home = tmp_path / "nonexistent_home"
        nonexistent_file = tmp_path / "nonexistent_file"

        with patch("mcp_server.__main__.Path.home", return_value=nonexistent_home):
            with patch(
                "mcp_server.__main__.__file__",
                str(nonexistent_file / "mcp_server" / "__main__.py"),
            ):
                with pytest.raises(SystemExit) as exc_info:
                    find_praxis_os_directory()

                assert exc_info.value.code == 1


class TestMainFunction:
    """Test main function with various scenarios."""

    @patch("mcp_server.__main__.argparse.ArgumentParser.parse_args")
    @patch("mcp_server.__main__.find_praxis_os_directory")
    @patch("mcp_server.__main__.ConfigLoader.load")
    @patch("mcp_server.__main__.ConfigValidator.validate")
    @patch("mcp_server.__main__.ProjectInfoDiscovery")
    @patch("mcp_server.__main__.PortManager")
    @patch("mcp_server.__main__.ServerFactory")
    @patch("mcp_server.__main__.TransportManager")
    def test_main_dual_mode(
        self,
        mock_transport_mgr_class,
        mock_factory_class,
        mock_port_mgr_class,
        mock_proj_info_class,
        mock_validator,
        mock_loader,
        mock_find_dir,
        mock_parse_args,
        tmp_path,
    ):
        """Test main function in dual mode."""
        # Setup mocks
        args = MagicMock()
        args.transport = "dual"
        args.log_level = "INFO"
        mock_parse_args.return_value = args

        mock_find_dir.return_value = tmp_path
        mock_config = MagicMock()
        mock_config.mcp.http_host = "127.0.0.1"
        mock_config.mcp.http_path = "/mcp"
        mock_loader.return_value = mock_config
        mock_validator.return_value = []  # No errors

        mock_port_mgr = MagicMock()
        mock_port_mgr.find_available_port.return_value = 4242
        mock_port_mgr_class.return_value = mock_port_mgr

        mock_factory = MagicMock()
        mock_mcp = MagicMock()
        mock_factory.create_server.return_value = mock_mcp
        mock_factory_class.return_value = mock_factory

        mock_transport_mgr = MagicMock()
        mock_transport_mgr_class.return_value = mock_transport_mgr

        # Run main
        main()

        # Verify dual mode execution
        mock_port_mgr.find_available_port.assert_called_once()
        mock_port_mgr.write_state.assert_called_once_with(
            transport="dual", port=4242, host="127.0.0.1", path="/mcp"
        )
        mock_transport_mgr.run_dual_mode.assert_called_once_with(
            "127.0.0.1", 4242, "/mcp"
        )
        mock_port_mgr.cleanup_state.assert_called_once()

    @patch("mcp_server.__main__.argparse.ArgumentParser.parse_args")
    @patch("mcp_server.__main__.find_praxis_os_directory")
    @patch("mcp_server.__main__.ConfigLoader.load")
    @patch("mcp_server.__main__.ConfigValidator.validate")
    @patch("mcp_server.__main__.ProjectInfoDiscovery")
    @patch("mcp_server.__main__.PortManager")
    @patch("mcp_server.__main__.ServerFactory")
    @patch("mcp_server.__main__.TransportManager")
    def test_main_stdio_mode(
        self,
        mock_transport_mgr_class,
        mock_factory_class,
        mock_port_mgr_class,
        mock_proj_info_class,
        mock_validator,
        mock_loader,
        mock_find_dir,
        mock_parse_args,
        tmp_path,
    ):
        """Test main function in stdio mode."""
        # Setup mocks
        args = MagicMock()
        args.transport = "stdio"
        args.log_level = "INFO"
        mock_parse_args.return_value = args

        mock_find_dir.return_value = tmp_path
        mock_config = MagicMock()
        mock_loader.return_value = mock_config
        mock_validator.return_value = []

        mock_port_mgr = MagicMock()
        mock_port_mgr_class.return_value = mock_port_mgr

        mock_factory = MagicMock()
        mock_mcp = MagicMock()
        mock_factory.create_server.return_value = mock_mcp
        mock_factory_class.return_value = mock_factory

        mock_transport_mgr = MagicMock()
        mock_transport_mgr_class.return_value = mock_transport_mgr

        # Run main
        main()

        # Verify stdio mode execution
        mock_port_mgr.write_state.assert_called_once_with(transport="stdio", port=None)
        mock_transport_mgr.run_stdio_mode.assert_called_once()
        mock_port_mgr.cleanup_state.assert_called_once()

    @patch("mcp_server.__main__.argparse.ArgumentParser.parse_args")
    @patch("mcp_server.__main__.find_praxis_os_directory")
    @patch("mcp_server.__main__.ConfigLoader.load")
    @patch("mcp_server.__main__.ConfigValidator.validate")
    @patch("mcp_server.__main__.ProjectInfoDiscovery")
    @patch("mcp_server.__main__.PortManager")
    @patch("mcp_server.__main__.ServerFactory")
    @patch("mcp_server.__main__.TransportManager")
    def test_main_http_mode(
        self,
        mock_transport_mgr_class,
        mock_factory_class,
        mock_port_mgr_class,
        mock_proj_info_class,
        mock_validator,
        mock_loader,
        mock_find_dir,
        mock_parse_args,
        tmp_path,
    ):
        """Test main function in HTTP mode."""
        # Setup mocks
        args = MagicMock()
        args.transport = "http"
        args.log_level = "INFO"
        mock_parse_args.return_value = args

        mock_find_dir.return_value = tmp_path
        mock_config = MagicMock()
        mock_config.mcp.http_host = "127.0.0.1"
        mock_config.mcp.http_path = "/mcp"
        mock_loader.return_value = mock_config
        mock_validator.return_value = []

        mock_port_mgr = MagicMock()
        mock_port_mgr.find_available_port.return_value = 4243
        mock_port_mgr_class.return_value = mock_port_mgr

        mock_factory = MagicMock()
        mock_mcp = MagicMock()
        mock_factory.create_server.return_value = mock_mcp
        mock_factory_class.return_value = mock_factory

        mock_transport_mgr = MagicMock()
        mock_transport_mgr_class.return_value = mock_transport_mgr

        # Run main
        main()

        # Verify HTTP mode execution
        mock_port_mgr.find_available_port.assert_called_once()
        mock_port_mgr.write_state.assert_called_once_with(
            transport="http", port=4243, host="127.0.0.1", path="/mcp"
        )
        mock_transport_mgr.run_http_mode.assert_called_once_with(
            "127.0.0.1", 4243, "/mcp"
        )
        mock_port_mgr.cleanup_state.assert_called_once()

    @patch("mcp_server.__main__.argparse.ArgumentParser.parse_args")
    @patch("mcp_server.__main__.find_praxis_os_directory")
    @patch("mcp_server.__main__.ConfigLoader.load")
    @patch("mcp_server.__main__.ConfigValidator.validate")
    def test_main_exits_on_config_errors(
        self, mock_validator, mock_loader, mock_find_dir, mock_parse_args, tmp_path
    ):
        """Test main exits if config validation fails."""
        # Setup mocks
        args = MagicMock()
        args.transport = "dual"
        args.log_level = "INFO"
        mock_parse_args.return_value = args

        mock_find_dir.return_value = tmp_path
        mock_config = MagicMock()
        mock_loader.return_value = mock_config
        mock_validator.return_value = ["Error 1", "Error 2"]  # Config errors

        # Run main - should exit
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

    @patch("mcp_server.__main__.argparse.ArgumentParser.parse_args")
    @patch("mcp_server.__main__.find_praxis_os_directory")
    @patch("mcp_server.__main__.ConfigLoader.load")
    @patch("mcp_server.__main__.ConfigValidator.validate")
    @patch("mcp_server.__main__.ProjectInfoDiscovery")
    @patch("mcp_server.__main__.PortManager")
    @patch("mcp_server.__main__.ServerFactory")
    @patch("mcp_server.__main__.TransportManager")
    def test_main_cleanup_on_keyboard_interrupt(
        self,
        mock_transport_mgr_class,
        mock_factory_class,
        mock_port_mgr_class,
        mock_proj_info_class,
        mock_validator,
        mock_loader,
        mock_find_dir,
        mock_parse_args,
        tmp_path,
    ):
        """Test main cleans up on KeyboardInterrupt."""
        # Setup mocks
        args = MagicMock()
        args.transport = "stdio"
        args.log_level = "INFO"
        mock_parse_args.return_value = args

        mock_find_dir.return_value = tmp_path
        mock_config = MagicMock()
        mock_loader.return_value = mock_config
        mock_validator.return_value = []

        mock_port_mgr = MagicMock()
        mock_port_mgr_class.return_value = mock_port_mgr

        mock_factory = MagicMock()
        mock_mcp = MagicMock()
        mock_factory.create_server.return_value = mock_mcp
        mock_factory_class.return_value = mock_factory

        mock_transport_mgr = MagicMock()
        mock_transport_mgr.run_stdio_mode.side_effect = KeyboardInterrupt
        mock_transport_mgr_class.return_value = mock_transport_mgr

        # Run main - should handle KeyboardInterrupt
        main()

        # Verify cleanup happened
        mock_port_mgr.cleanup_state.assert_called_once()
        mock_transport_mgr.shutdown.assert_called_once()


class TestDocstrings:
    """Verify code quality requirements."""

    def test_functions_have_docstrings(self):
        """Test all functions have docstrings."""
        functions = [find_praxis_os_directory, main]

        for func in functions:
            assert func.__doc__ is not None
            assert len(func.__doc__) > 20  # Substantive docstring

    def test_module_has_docstring(self):
        """Test module has docstring."""
        import mcp_server.__main__ as main_module

        assert main_module.__doc__ is not None
        assert "Entry point" in main_module.__doc__
