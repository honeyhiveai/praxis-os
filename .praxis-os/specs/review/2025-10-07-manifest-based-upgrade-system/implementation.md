# Implementation Approach

**Project:** Manifest-Based Upgrade System  
**Date:** 2025-10-07

---

## 1. Implementation Philosophy

**Core Principles:**
1. **Safety First:** Multiple safeguards to prevent data loss
2. **Progressive Implementation:** Build and test incrementally
3. **User-Centric:** Clear prompts and helpful error messages
4. **Testable:** Unit tests before integration tests
5. **Dogfooding:** Test on python-sdk before releasing

---

## 2. Implementation Order

### Phase 1: Manifest Generator
**Rationale:** Need manifest before upgrade tool can work

1. Create `scripts/generate-manifest.py`
2. Implement checksum calculation
3. Implement directory scanning
4. Add git integration for dates
5. Generate manifest for praxis-os
6. Validate manifest structure

### Phase 2: Safe Upgrade Tool (Core)
**Rationale:** Core logic without user interaction first

1. Create `scripts/safe-upgrade.py`
2. Implement manifest loading and validation
3. Implement file classification logic
4. Implement dry-run mode
5. Add logging infrastructure

### Phase 3: Interactive Features
**Rationale:** Add user interaction after core works

1. Implement backup creation
2. Implement auto-update for safe files
3. Implement conflict prompts
4. Implement diff viewer
5. Add summary report

### Phase 4: Integration and Testing
**Rationale:** Validate end-to-end

1. Unit tests for both scripts
2. Integration test on python-sdk
3. Update documentation
4. Rollback testing

---

## 3. File Creation Strategy

### 3.1 scripts/generate-manifest.py

**Structure:**
```python
#!/usr/bin/env python3
"""
Manifest Generator for Agent OS Enhanced

Scans universal/ directory and generates .universal-manifest.json
with checksums and metadata for all skeleton files.
"""

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, Any

# Constants
SUPPORTED_EXTENSIONS = {".md", ".json"}
GENERATOR_VERSION = "1.0.0"

def calculate_checksum(file_path: Path) -> str:
    """Calculate SHA-256 checksum of file."""
    ...

def get_last_modified_date(file_path: Path, repo_root: Path) -> str:
    """Get last modified date from git, fallback to filesystem."""
    ...

def scan_directory(universal_dir: Path, repo_root: Path) -> Dict[str, Dict[str, Any]]:
    """Scan directory and collect file metadata."""
    ...

def generate_manifest(universal_dir: Path, version: str, repo_root: Path) -> Dict[str, Any]:
    """Generate complete manifest."""
    ...

def validate_manifest(manifest: Dict[str, Any]) -> bool:
    """Validate manifest structure."""
    ...

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate manifest for Agent OS universal files"
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Agent OS version (e.g., 1.3.0)"
    )
    parser.add_argument(
        "--universal-dir",
        default="universal",
        help="Path to universal directory (default: universal)"
    )
    parser.add_argument(
        "--output",
        default="universal/.universal-manifest.json",
        help="Output path for manifest (default: universal/.universal-manifest.json)"
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to git repository root (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Convert to Path objects
    universal_dir = Path(args.universal_dir)
    output_path = Path(args.output)
    repo_root = Path(args.repo_root)
    
    # Validate paths
    if not universal_dir.exists():
        print(f"ERROR: Universal directory not found: {universal_dir}")
        sys.exit(1)
    
    # Generate manifest
    print(f"Generating manifest for {universal_dir}...")
    manifest = generate_manifest(universal_dir, args.version, repo_root)
    
    # Validate
    if not validate_manifest(manifest):
        print(f"ERROR: Generated manifest failed validation")
        sys.exit(1)
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Summary
    print(f"\n✅ Manifest generated successfully")
    print(f"   Files tracked: {len(manifest['files'])}")
    print(f"   Output: {output_path}")
    print(f"   Version: {manifest['version']}")

if __name__ == "__main__":
    main()
```

**Key Implementation Details:**

1. **Checksum Calculation:**
   ```python
   def calculate_checksum(file_path: Path) -> str:
       """Calculate SHA-256 checksum efficiently."""
       sha256 = hashlib.sha256()
       with open(file_path, 'rb') as f:
           # Read in 8KB chunks for memory efficiency
           for chunk in iter(lambda: f.read(8192), b''):
               sha256.update(chunk)
       return sha256.hexdigest()
   ```

2. **Git Integration:**
   ```python
   def get_last_modified_date(file_path: Path, repo_root: Path) -> str:
       """Get last modified date, prefer git over filesystem."""
       try:
           result = subprocess.run(
               ["git", "log", "-1", "--format=%ci", str(file_path)],
               cwd=repo_root,
               capture_output=True,
               text=True,
               check=True,
               timeout=5
           )
           # Extract date (YYYY-MM-DD) from git output
           git_datetime = result.stdout.strip()
           if git_datetime:
               return git_datetime.split()[0]
       except (subprocess.SubprocessError, subprocess.TimeoutExpired):
           pass
       
       # Fallback to filesystem mtime
       mtime = file_path.stat().st_mtime
       return datetime.fromtimestamp(mtime).date().isoformat()
   ```

3. **Directory Scanning:**
   ```python
   def scan_directory(universal_dir: Path, repo_root: Path) -> Dict[str, Dict[str, Any]]:
       """Recursively scan directory for supported files."""
       files = {}
       
       for file_path in sorted(universal_dir.rglob("*")):
           # Skip directories
           if not file_path.is_file():
               continue
           
           # Skip unsupported extensions
           if file_path.suffix not in SUPPORTED_EXTENSIONS:
               continue
           
           # Skip hidden files
           if file_path.name.startswith(".") and file_path.name != ".universal-manifest.json":
               continue
           
           # Calculate relative path
           rel_path = str(file_path.relative_to(universal_dir))
           
           # Skip manifest itself
           if rel_path == ".universal-manifest.json":
               continue
           
           # Collect metadata
           files[rel_path] = {
               "checksum": f"sha256:{calculate_checksum(file_path)}",
               "size": file_path.stat().st_size,
               "last_updated": get_last_modified_date(file_path, repo_root)
           }
           
           print(f"  ✓ {rel_path}")
       
       return files
   ```

---

### 3.2 scripts/safe-upgrade.py

**Structure:**
```python
#!/usr/bin/env python3
"""
Safe Upgrade Tool for Agent OS

Safely upgrades local .praxis-os/ directory from praxis-os source
with conflict detection and interactive prompts.
"""

import argparse
import json
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

# File classification states
class FileState(Enum):
    NEW = "new"
    UNCHANGED = "unchanged"
    AUTO_UPDATE = "auto_update"
    LOCAL_ONLY = "local_only"
    CONFLICT = "conflict"
    ERROR = "error"

# Upgrade report
@dataclass
class UpgradeReport:
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    local_only: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    backup_path: Optional[str] = None
    dry_run: bool = False

def load_manifest(manifest_path: Path) -> Dict:
    """Load and validate manifest."""
    ...

def create_backup(target_dir: Path) -> Path:
    """Create timestamped backup of target directory."""
    ...

def classify_file(...) -> FileState:
    """Classify file state based on checksums."""
    ...

def process_file(...) -> str:
    """Process file based on its state."""
    ...

def handle_conflict(...) -> str:
    """Handle conflict with interactive prompt."""
    ...

def show_diff(local_file: Path, source_file: Path):
    """Show side-by-side diff."""
    ...

def print_summary(report: UpgradeReport):
    """Print upgrade summary."""
    ...

def write_upgrade_log(target_dir: Path, report: UpgradeReport, manifest: Dict):
    """Write upgrade to log file."""
    ...

def main():
    """Main entry point."""
    ...

if __name__ == "__main__":
    main()
```

**Key Implementation Details:**

See `specs.md` Section 3.2 for detailed algorithms.

---

## 4. Code Style Guidelines

### 4.1 Python Style

- Follow PEP 8
- Use type hints on all functions
- Use docstrings (Google style)
- Max line length: 100 characters
- Use `pathlib.Path` for all file operations

**Example:**
```python
def calculate_checksum(file_path: Path) -> str:
    """
    Calculate SHA-256 checksum of file.
    
    Args:
        file_path: Path to file
        
    Returns:
        Hexadecimal checksum string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file isn't readable
    """
    # Implementation...
```

### 4.2 Error Messages

- Clear and actionable
- Include context and suggested fix
- Use emoji for visual clarity (✅ ❌ ⚠️)

**Good:**
```
❌ ERROR: Manifest not found at universal/.universal-manifest.json

   The source directory may be outdated or corrupt.
   
   To fix:
   1. Ensure you're using praxis-os v1.3.0 or later
   2. Run: cd praxis-os && python scripts/generate-manifest.py --version 1.3.0
```

**Bad:**
```
Error: File not found
```

---

## 5. Testing Approach

### 5.1 Unit Test Structure

```python
# tests/unit/test_manifest_generator.py

import pytest
from pathlib import Path
from scripts.generate_manifest import calculate_checksum, scan_directory

def test_calculate_checksum_known_content():
    """Test checksum calculation with known SHA-256."""
    # Create temp file with "hello world"
    # Known SHA-256: b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
    ...

def test_scan_directory_finds_all_files():
    """Test directory scanning finds all supported files."""
    # Create temp directory with md and json files
    # Scan directory
    # Assert all files found
    ...

def test_scan_directory_ignores_unsupported():
    """Test directory scanning ignores unsupported extensions."""
    # Create temp directory with .txt, .py files
    # Scan directory
    # Assert these files not included
    ...
```

```python
# tests/unit/test_safe_upgrade.py

import pytest
from scripts.safe_upgrade import classify_file, FileState

def test_classify_new_file():
    """Test classification of new file (in manifest, not local)."""
    # Setup: file in manifest, not in local dir
    # Assert: FileState.NEW
    ...

def test_classify_auto_update():
    """Test classification of auto-update file."""
    # Setup: local matches manifest, source changed
    # Assert: FileState.AUTO_UPDATE
    ...

def test_classify_conflict():
    """Test classification of conflict (both changed)."""
    # Setup: local != manifest, source != manifest
    # Assert: FileState.CONFLICT
    ...
```

### 5.2 Integration Test Plan

**Test on praxis-os itself (dogfooding):**

1. **Setup:**
   ```bash
   cd /Users/josh/src/github.com/honeyhiveai/praxis-os
   cp -r .praxis-os .praxis-os.test-backup
   ```

2. **Generate Manifest:**
   ```bash
   python scripts/generate-manifest.py --version 1.3.0
   ```

3. **Dry Run:**
   ```bash
   python scripts/safe-upgrade.py \
       --source . \
       --target .praxis-os \
       --dry-run
   ```

4. **Verify Detection:**
   - All files detected (should mostly be UNCHANGED since we're testing on source)
   - Any local customizations detected as conflicts
   - Manifest itself excluded from upgrade

5. **Execute Upgrade:**
   ```bash
   python scripts/safe-upgrade.py \
       --source . \
       --target .praxis-os
   ```

6. **Verify Success:**
   - No files deleted
   - Any customized files preserved (or user chose to replace)
   - MCP queries work
   - RAG index auto-rebuilt

7. **Cleanup:**
   ```bash
   rm -rf .praxis-os.test-backup
   ```

**Note:** This is true dogfooding - upgrading praxis-os's own `.praxis-os/` from its own `universal/` directory. This tests the self-upgrade scenario.

---

## 6. Documentation Strategy

### 6.1 In-Script Documentation

Both scripts should have comprehensive `--help`:

```bash
$ python scripts/generate-manifest.py --help

usage: generate-manifest.py [-h] --version VERSION [--universal-dir DIR]
                           [--output FILE] [--repo-root DIR]

Generate manifest for Agent OS universal files

Arguments:
  --version VERSION    Agent OS version (e.g., 1.3.0)
  --universal-dir DIR  Path to universal directory (default: universal)
  --output FILE        Output path (default: universal/.universal-manifest.json)
  --repo-root DIR      Git repository root (default: current directory)

Examples:
  # Generate manifest for release 1.3.0
  python scripts/generate-manifest.py --version 1.3.0
  
  # Custom paths
  python scripts/generate-manifest.py --version 1.3.0 \
      --universal-dir /path/to/universal \
      --output /path/to/manifest.json
```

### 6.2 User Documentation

**Update:** `universal/usage/agent-os-update-guide.md`

Add new section:
```markdown
## Manifest-Based Upgrade (Recommended)

### Prerequisites

- Python 3.11 or later
- praxis-os repository (v1.3.0+)
- Backup of .praxis-os/ (recommended)

### Step 1: Pull Latest Source

```bash
cd /path/to/praxis-os
git pull origin main
git log -1  # Note commit hash
```

### Step 2: Preview Changes (Dry Run)

```bash
cd /path/to/your-project
python /path/to/praxis-os/scripts/safe-upgrade.py \
    --source /path/to/praxis-os \
    --target .praxis-os \
    --dry-run
```

Review the preview:
- ➕ New files: Will be added (you'll be prompted)
- 🔄 Updated files: Safe to auto-update (unchanged locally)
- 📝 Local-only: Your customizations preserved
- ⚠️  Conflicts: You'll choose (keep local or use new)

### Step 3: Execute Upgrade

```bash
python /path/to/praxis-os/scripts/safe-upgrade.py \
    --source /path/to/praxis-os \
    --target .praxis-os
```

The tool will:
1. Create automatic backup (.praxis-os.backup.TIMESTAMP)
2. Auto-update unchanged files
3. Prompt for conflicts with options:
   - [K] Keep your local version
   - [R] Replace with new version
   - [D] Show diff before deciding
   - [S] Skip (decide later)

### Step 4: Verify

Wait 10-30 seconds for RAG index auto-rebuild, then test:

```bash
mcp_agent-os-rag_search_standards("testing standards")
```

### Rollback (If Needed)

```bash
rm -rf .praxis-os
mv .praxis-os.backup.YYYYMMDD_HHMMSS .praxis-os
```

### Troubleshooting

**Q: Script says "manifest not found"**
A: Source repo is too old. Update to praxis-os v1.3.0+

**Q: I accidentally replaced my custom file**
A: Restore from backup: .praxis-os.backup.YYYYMMDD_HHMMSS

**Q: Upgrade interrupted mid-way**
A: Safe to re-run. Idempotent design allows multiple runs.
```

---

## 7. Rollout Strategy

### 7.1 Development Phase

1. Implement on feature branch
2. Unit tests passing
3. Generate manifest for praxis-os
4. Commit manifest to repo

### 7.2 Dogfooding Phase

1. Test on praxis-os itself (self-upgrade, dry-run first)
2. Document any issues
3. Fix and iterate
4. Test on external project (python-sdk) if needed for additional validation

### 7.3 Release Phase

1. Merge to main
2. Tag release (v1.3.0)
3. Update documentation
4. Announce in README
5. Add to installation guide

### 7.4 Adoption Phase

1. Users pull latest praxis-os
2. Users run safe-upgrade.py
3. Collect feedback
4. Iterate on prompts/UX

---

## 8. Future Enhancements (Out of Scope)

### 8.1 CI/CD Integration

Auto-generate manifest on release:
```yaml
# .github/workflows/release.yml
- name: Generate manifest
  run: |
    python scripts/generate-manifest.py --version ${{ github.ref_name }}
    git add universal/.universal-manifest.json
    git commit -m "chore: update manifest for ${{ github.ref_name }}"
```

### 8.2 Three-Way Merge

For structured files (JSON, YAML), implement intelligent merging:
```python
def three_way_merge(base, local, remote):
    """Merge changes from both sides."""
    # Parse structured data
    # Identify non-conflicting changes
    # Auto-merge where possible
    # Prompt only for true conflicts
```

### 8.3 MCP Tool

Expose upgrade via MCP:
```python
@mcp.tool()
def upgrade_agent_os(source_path: str, dry_run: bool = True) -> dict:
    """Programmatic upgrade access for AI agents."""
    # Must require human approval
    # Returns preview or execution result
```

---

## 9. Success Metrics

### 9.1 Development Metrics

- [ ] Unit tests: 100% of core functions
- [ ] Integration test: Successful python-sdk upgrade
- [ ] Documentation: Complete and clear
- [ ] Code review: Approved by maintainer

### 9.2 User Metrics

- [ ] Zero data loss reports
- [ ] <5 minutes average upgrade time
- [ ] >90% user satisfaction (no confusion)
- [ ] <5% rollback rate

---

## 10. Risk Mitigation Checklist

Before releasing:

- [ ] Unit tests pass
- [ ] Integration test on python-sdk successful
- [ ] Rollback procedure tested
- [ ] Backup creation tested
- [ ] Dry-run mode tested
- [ ] Conflict prompts tested
- [ ] Documentation reviewed
- [ ] Error messages clear

---

**Implementation guide complete. Ready for task breakdown.**
