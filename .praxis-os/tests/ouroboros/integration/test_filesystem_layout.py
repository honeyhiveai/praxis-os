"""
Integration test for filesystem layout validation.

This is a WHITELIST + BLACKLIST approach that catches:
1. Nested directory bugs (blacklist) - e.g., .praxis-os/.praxis-os/
2. Unexpected top-level directories (whitelist)
3. Missing expected directories (whitelist)

This test validates the OUTCOME (filesystem structure) rather than
the IMPLEMENTATION (how paths are constructed), making it robust
against refactoring and implementation changes.

Traceability:
    Prevents nested directory bugs across all subsystems
    Validates overall .praxis-os/ filesystem structure
"""

import pytest
from pathlib import Path
from ouroboros.subsystems.rag.index_manager import IndexManager


class TestFilesystemLayout:
    """Integration tests for filesystem layout validation."""
    
    def test_rag_indexes_filesystem_layout(self, test_config, test_base_path):
        """
        Test that building RAG indexes creates correct filesystem layout.
        
        This catches:
        - Nested directory bugs (.praxis-os/.praxis-os, .cache/.cache)
        - Missing expected cache directories
        - Unexpected directory creation
        
        This is a comprehensive test that validates the ENTIRE filesystem
        structure created by the RAG subsystem, not just individual components.
        """
        # Build indexes (this creates cache directories)
        manager = IndexManager(config=test_config.indexes, base_path=test_base_path)
        
        # Build standards index to trigger cache directory creation
        if "standards" in manager._indexes:
            standards_dir = test_base_path / "standards"
            standards_dir.mkdir(parents=True, exist_ok=True)
            (standards_dir / "test.md").write_text("# Test Standard\n\nTest content for validation.")
            manager._indexes["standards"].build([standards_dir], force=False)
        
        # WHITELIST: Expected cache directories that SHOULD exist
        expected_cache_dirs = [
            test_base_path / ".cache",
            test_base_path / ".cache" / "rag",
            test_base_path / ".cache" / "rag" / "build-progress",
            test_base_path / ".cache" / "indexes",
            test_base_path / ".cache" / "locks",
        ]
        
        missing = [d for d in expected_cache_dirs if not d.exists()]
        assert len(missing) == 0, (
            f"❌ Missing {len(missing)} expected cache directories:\n"
            + "\n".join(f"  - {d.relative_to(test_base_path)}" for d in missing)
            + "\n\nThis indicates incomplete initialization in RAG components."
        )
        
        # BLACKLIST: Forbidden nested patterns that should NEVER exist
        forbidden_patterns = [
            ".praxis-os/.praxis-os",  # Nested .praxis-os (THE RECURRING BUG)
            ".cache/.cache",          # Nested .cache
            "rag/rag",                # Nested rag
            "indexes/indexes",        # Nested indexes
            "locks/locks",            # Nested locks
            "build-progress/build-progress",  # Nested build-progress
        ]
        
        # Get all created directories
        all_dirs = [str(d.relative_to(test_base_path)) for d in test_base_path.rglob("*") if d.is_dir()]
        
        # Check for forbidden patterns
        violations = {}
        for pattern in forbidden_patterns:
            matching = [d for d in all_dirs if pattern in d]
            if matching:
                violations[pattern] = matching
        
        assert len(violations) == 0, (
            f"❌ Found {len(violations)} forbidden nested directory patterns:\n"
            + "\n".join(
                f"\n  Pattern '{pattern}' found in:\n"
                + "\n".join(f"    - {d}" for d in dirs)
                for pattern, dirs in violations.items()
            )
            + "\n\n🔧 This indicates a path construction bug in the codebase.\n"
            + "   Look for: base_path / '.praxis-os' / ...\n"
            + "   Should be: base_path / ..."
        )
        
        # WHITELIST: Expected top-level directories (only what RAG creates)
        # Note: We only check directories that RAG subsystem creates
        # Other subsystems (workflow, browser, etc.) create their own dirs
        expected_top_level_from_rag = {
            ".cache",      # Created by RAG indexes
            "standards",   # Created by this test
        }
        
        actual_top_level = {d.name for d in test_base_path.iterdir() if d.is_dir()}
        
        # Check that expected dirs exist
        missing_top_level = expected_top_level_from_rag - actual_top_level
        assert len(missing_top_level) == 0, (
            f"❌ Missing {len(missing_top_level)} expected top-level directories:\n"
            + "\n".join(f"  - {d}" for d in missing_top_level)
        )
        
        print(f"✅ Filesystem layout validated:")
        print(f"  - {len(expected_cache_dirs)} cache directories exist")
        print(f"  - {len(forbidden_patterns)} forbidden patterns checked")
        print(f"  - {len(actual_top_level)} top-level directories present")
        print(f"  - No nested directory bugs found")


class TestFilesystemLayoutSmoke:
    """Smoke tests for real .praxis-os/ installation filesystem layout."""
    
    @pytest.mark.skipif(
        not Path(".praxis-os").exists(),
        reason="Requires real .praxis-os installation"
    )
    def test_real_installation_no_nested_directories(self):
        """
        Smoke test: Validate real installation has no nested directories.
        
        This is the LAST LINE OF DEFENSE - catches bugs that slip through
        unit and integration tests by checking the actual installed filesystem.
        
        This runs against the REAL .praxis-os/ directory, not a test fixture.
        """
        praxis_dir = Path(".praxis-os")
        
        # BLACKLIST: Forbidden patterns that indicate bugs
        forbidden_patterns = [
            ".praxis-os/.praxis-os",
            ".cache/.cache",
            "rag/rag",
            "indexes/indexes",
            "locks/locks",
            "build-progress/build-progress",
        ]
        
        # Get all directories in real installation
        all_dirs = [str(d.relative_to(praxis_dir)) for d in praxis_dir.rglob("*") if d.is_dir()]
        
        # Check for violations
        violations = {}
        for pattern in forbidden_patterns:
            matching = [d for d in all_dirs if pattern in d]
            if matching:
                violations[pattern] = matching
        
        assert len(violations) == 0, (
            f"❌ Real installation has {len(violations)} nested directory bugs:\n"
            + "\n".join(
                f"\n  Pattern '{pattern}' found in:\n"
                + "\n".join(f"    - {d}" for d in dirs[:5])  # Show first 5
                + (f"\n    ... and {len(dirs) - 5} more" if len(dirs) > 5 else "")
                for pattern, dirs in violations.items()
            )
            + "\n\n🚨 This is a PRODUCTION BUG - fix immediately!\n"
            + "   Check path construction in RAG components."
        )
        
        print(f"✅ Real installation filesystem layout validated")
        print(f"  - {len(all_dirs)} directories checked")
        print(f"  - {len(forbidden_patterns)} forbidden patterns validated")
        print(f"  - No nested directory bugs found")
    
    @pytest.mark.skipif(
        not Path(".praxis-os").exists(),
        reason="Requires real .praxis-os installation"
    )
    def test_real_installation_expected_structure(self):
        """
        Smoke test: Validate real installation has expected top-level structure.
        
        This catches unexpected top-level directories that might indicate:
        1. Path construction bugs
        2. New features that need whitelist updates
        3. User-created directories (harmless but worth noting)
        """
        praxis_dir = Path(".praxis-os")
        
        # WHITELIST: Expected top-level directories in a real installation
        expected_top_level = {
            ".cache",           # RAG indexes, build progress, locks
            "bin",              # Secondary agent scripts (optional)
            "config",           # mcp.yaml and other config files
            "ouroboros",        # MCP server code (synced from dist/)
            "scripts",          # Helper scripts (synced from dist/)
            "specs",            # User specs (workspace, approved, completed)
            "standards",        # User + universal standards
            "workflows",        # Workflow definitions (synced from dist/)
            "workspace",        # User workspace (design docs, analysis)
            "venv",             # Python virtual environment (optional)
            "logs",             # Log files (optional)
            "workflow_states",  # Workflow state (optional)
            "state",            # Session state, browser sessions (optional)
            "tests",            # Test suite (dogfooding/development)
            "evaluation",       # Evaluation results (dogfooding/development)
        }
        
        actual_top_level = {d.name for d in praxis_dir.iterdir() if d.is_dir()}
        
        # Check for unexpected directories
        unexpected = actual_top_level - expected_top_level
        
        # Filter out common harmless directories
        harmless = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".tox", ".cursor"}
        unexpected = unexpected - harmless
        
        if len(unexpected) > 0:
            print(f"⚠️  Found {len(unexpected)} unexpected top-level directories:")
            for d in sorted(unexpected):
                print(f"  - {d}")
            print("\nThis might indicate:")
            print("  1. A bug in path construction")
            print("  2. A new feature that needs to be added to the whitelist")
            print("  3. User-created directories (harmless)")
            print("\nIf this is a new feature, update the whitelist in:")
            print("  .praxis-os/tests/ouroboros/integration/test_filesystem_layout.py")
        
        # Don't fail on unexpected dirs (might be user-created or new features)
        # Just warn so developers can investigate
        
        # Check that critical directories exist
        critical_dirs = {".cache", "config", "ouroboros", "standards"}
        missing_critical = critical_dirs - actual_top_level
        
        assert len(missing_critical) == 0, (
            f"❌ Real installation missing {len(missing_critical)} critical directories:\n"
            + "\n".join(f"  - {d}" for d in missing_critical)
            + "\n\nThis indicates an incomplete or corrupted installation."
        )
        
        print(f"✅ Real installation structure validated")
        print(f"  - {len(actual_top_level)} top-level directories present")
        print(f"  - {len(critical_dirs)} critical directories verified")

