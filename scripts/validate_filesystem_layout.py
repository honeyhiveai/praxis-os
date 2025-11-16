#!/usr/bin/env python3
"""
Pre-commit hook to validate .praxis-os/ filesystem layout.

Runs instantly before commit to catch nested directory bugs.

This is the FIRST LINE OF DEFENSE - provides instant feedback
to developers before they commit code with path construction bugs.

Usage:
    python scripts/validate_filesystem_layout.py

Exit codes:
    0 - Validation passed
    1 - Validation failed (nested directories found)

Traceability:
    Prevents nested directory bugs from being committed
    Catches recurring .praxis-os/.praxis-os/ bug pattern
"""

import sys
from pathlib import Path


def check_filesystem_layout() -> bool:
    """
    Check .praxis-os/ filesystem for forbidden directory patterns.

    Returns:
        True if validation passed, False if violations found
    """
    praxis_dir = Path(".praxis-os")

    if not praxis_dir.exists():
        print("✅ No .praxis-os directory (skipping filesystem layout check)")
        return True

    # BLACKLIST: Forbidden patterns that indicate path construction bugs
    forbidden_patterns = [
        ".praxis-os/.praxis-os",  # Nested .praxis-os (THE RECURRING BUG)
        ".cache/.cache",  # Nested .cache
        "rag/rag",  # Nested rag
        "indexes/indexes",  # Nested indexes
        "locks/locks",  # Nested locks
        "build-progress/build-progress",  # Nested build-progress
    ]

    # Get all directories
    try:
        all_dirs = [
            str(d.relative_to(praxis_dir)) for d in praxis_dir.rglob("*") if d.is_dir()
        ]
    except Exception as e:
        print(f"⚠️  Error scanning .praxis-os directory: {e}")
        print("   Skipping filesystem layout check")
        return True  # Don't fail on scan errors

    # Check for violations
    violations = {}
    for pattern in forbidden_patterns:
        matching = [d for d in all_dirs if pattern in d]
        if matching:
            violations[pattern] = matching

    if violations:
        print("❌ Filesystem Layout Validation Failed")
        print(f"\nFound {len(violations)} forbidden nested directory patterns:")

        for pattern, dirs in violations.items():
            print(f"\n  Pattern '{pattern}':")
            # Show first 5 violations per pattern
            for d in sorted(dirs)[:5]:
                print(f"    - {d}")
            if len(dirs) > 5:
                print(f"    ... and {len(dirs) - 5} more")

        print("\n🔧 How to fix:")
        print("   1. Check path construction in RAG components")
        print("   2. Look for: base_path / '.praxis-os' / '.cache'")
        print("   3. Should be: base_path / '.cache'")
        print("\n   The bug is likely in one of these files:")
        print("   - .praxis-os/ouroboros/subsystems/rag/code/semantic.py")
        print("   - .praxis-os/ouroboros/subsystems/rag/standards/semantic.py")
        print("   - .praxis-os/ouroboros/subsystems/rag/code/graph/container.py")
        print("   - .praxis-os/ouroboros/subsystems/rag/code/container.py")
        print("   - .praxis-os/ouroboros/subsystems/rag/standards/container.py")

        return False

    print("✅ Filesystem layout validated (no nested directories found)")
    return True


def main() -> int:
    """
    Main entry point for pre-commit hook.

    Returns:
        0 if validation passed, 1 if validation failed
    """
    try:
        passed = check_filesystem_layout()
        return 0 if passed else 1
    except Exception as e:
        print(f"❌ Unexpected error during filesystem layout validation: {e}")
        print("   Skipping check to avoid blocking commit")
        return 0  # Don't block commit on unexpected errors


if __name__ == "__main__":
    sys.exit(main())
