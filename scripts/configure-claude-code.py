#!/usr/bin/env python3
"""
Configure Claude Code MCP Settings for prAxIs OS

Automatically configures Claude Code's MCP server settings to use the correct
praxis-os-rag server configuration with proper paths and transport mode.

Usage:
    python configure-claude-code.py [project_root]

    If project_root not provided, uses current directory.
"""
import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


def find_claude_code_config_dir() -> Optional[Path]:
    """
    Find Claude Code configuration directory.

    Searches common locations:
    1. ~/.config/claude-code/ (Linux, some macOS)
    2. ~/Library/Application Support/Claude/ (macOS)

    Returns:
        Path to config directory if found, None otherwise
    """
    home = Path.home()

    # Common locations
    locations = [
        home / ".config" / "claude-code",
        home / "Library" / "Application Support" / "Claude",
    ]

    for location in locations:
        if location.exists():
            return location

    return None


def load_existing_config(config_file: Path) -> Dict[str, Any]:
    """
    Load existing Claude Code config, or return empty config structure.

    Args:
        config_file: Path to config file

    Returns:
        Parsed JSON config dict, or empty structure if file doesn't exist
    """
    if not config_file.exists():
        return {"mcpServers": {}}

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Ensure mcpServers key exists
            if "mcpServers" not in config:
                config["mcpServers"] = {}
            return config
    except json.JSONDecodeError as e:
        print(f"⚠️  Warning: Existing config has invalid JSON: {e}")
        print("   Creating backup and starting fresh")
        # Backup corrupted file
        backup_file = config_file.with_suffix('.json.backup')
        config_file.rename(backup_file)
        return {"mcpServers": {}}


def create_praxis_os_config(project_root: Path) -> Dict[str, Any]:
    """
    Create praxis-os-rag MCP server configuration.

    Args:
        project_root: Absolute path to project root

    Returns:
        Configuration dict for praxis-os-rag server
    """
    # Use absolute paths (Claude Code requires them)
    venv_python = str(project_root / ".praxis-os" / "venv" / "bin" / "python")
    project_root_str = str(project_root)
    pythonpath = str(project_root / ".praxis-os")

    return {
        "command": venv_python,
        "args": ["-m", "mcp_server", "--transport", "stdio"],
        "env": {
            "PROJECT_ROOT": project_root_str,
            "PYTHONPATH": pythonpath
        }
    }


def write_config(config_file: Path, config: Dict[str, Any]) -> None:
    """
    Write configuration to file with pretty formatting.

    Args:
        config_file: Path to config file
        config: Configuration dict to write
    """
    # Ensure parent directory exists
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Write with pretty formatting
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
        f.write('\n')  # Add trailing newline


def validate_config(project_root: Path) -> bool:
    """
    Validate that required paths exist.

    Args:
        project_root: Project root directory

    Returns:
        True if valid, False otherwise
    """
    venv_python = project_root / ".praxis-os" / "venv" / "bin" / "python"
    praxis_os_dir = project_root / ".praxis-os"
    mcp_server_dir = project_root / ".praxis-os" / "mcp_server"

    if not praxis_os_dir.exists():
        print(f"✗ .praxis-os directory not found: {praxis_os_dir}")
        return False

    if not mcp_server_dir.exists():
        print(f"✗ MCP server directory not found: {mcp_server_dir}")
        return False

    if not venv_python.exists():
        print(f"✗ Python venv not found: {venv_python}")
        print("  Run installation script to create virtual environment")
        return False

    return True


def main():
    """Main configuration flow"""
    print("=" * 60)
    print("Claude Code MCP Configuration")
    print("=" * 60)
    print()

    # Parse project root
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1]).resolve()
    else:
        project_root = Path.cwd().resolve()

    print(f"Project root: {project_root}")
    print()

    # Validate project structure
    print("Step 1/4: Validating project structure")
    if not validate_config(project_root):
        print()
        print("✗ Validation failed")
        print("  Please run prAxIs OS installation first")
        sys.exit(1)
    print("✓ Project structure valid")
    print()

    # Find Claude Code config directory
    print("Step 2/4: Finding Claude Code configuration")
    config_dir = find_claude_code_config_dir()

    if not config_dir:
        print("⚠️  Claude Code configuration directory not found")
        print()
        print("Searched locations:")
        print("  • ~/.config/claude-code/")
        print("  • ~/Library/Application Support/Claude/")
        print()
        print("Manual configuration required:")
        print()
        print("1. Find your Claude Code config file")
        print("2. Add this configuration:")
        print()
        print(json.dumps({
            "mcpServers": {
                "praxis-os-rag": create_praxis_os_config(project_root)
            }
        }, indent=2))
        print()
        sys.exit(1)

    print(f"✓ Found: {config_dir}")
    print()

    # Load existing config
    print("Step 3/4: Loading existing configuration")
    config_file = config_dir / "claude_desktop_config.json"
    config = load_existing_config(config_file)

    # Check if praxis-os-rag already configured
    if "praxis-os-rag" in config["mcpServers"]:
        print("⚠️  praxis-os-rag already configured")
        print("   Updating with correct settings...")
    else:
        print("✓ No existing praxis-os-rag configuration")
    print()

    # Update config
    print("Step 4/4: Writing configuration")
    config["mcpServers"]["praxis-os-rag"] = create_praxis_os_config(project_root)
    write_config(config_file, config)
    print(f"✓ Configuration written: {config_file}")
    print()

    # Print success message
    print("=" * 60)
    print("✅ CONFIGURATION COMPLETE")
    print("=" * 60)
    print()
    print("Configuration details:")
    print(f"  • Config file: {config_file}")
    print(f"  • Python: {project_root}/.praxis-os/venv/bin/python")
    print(f"  • Transport: stdio")
    print(f"  • Project: {project_root}")
    print()
    print("Next steps:")
    print("  1. Restart Claude Code to load new configuration")
    print("  2. Open this project in Claude Code")
    print("  3. MCP server will start automatically")
    print("  4. Test with: search_standards('praxis os orientation')")
    print()
    print("Troubleshooting:")
    print("  • If server doesn't start, check Claude Code logs")
    print("  • Run validation: .praxis-os/venv/bin/python .praxis-os/scripts/validate-mcp-config.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Configuration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
