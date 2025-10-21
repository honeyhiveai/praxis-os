# Technical Specifications

**Project:** Manifest-Based Upgrade System  
**Date:** 2025-10-07

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Agent OS Enhanced (Source)                  │
│                                                              │
│  ┌────────────────────────────────────────────────┐        │
│  │  1. Generate Manifest (Release Process)        │        │
│  │     scripts/generate-manifest.py               │        │
│  │        │                                        │        │
│  │        ▼                                        │        │
│  │  universal/.universal-manifest.json            │        │
│  └────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ rsync or git pull
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Consuming Project (e.g., python-sdk)            │
│                                                              │
│  ┌────────────────────────────────────────────────┐        │
│  │  2. Run Upgrade Tool                           │        │
│  │     scripts/safe-upgrade.py                    │        │
│  │        │                                        │        │
│  │        ├→ Read source manifest                 │        │
│  │        ├→ Calculate local checksums            │        │
│  │        ├→ Compare & classify files             │        │
│  │        ├→ Create backup                        │        │
│  │        ├→ Auto-update safe files               │        │
│  │        ├→ Prompt for conflicts                 │        │
│  │        └→ Generate report                      │        │
│  │                                                  │        │
│  │  .agent-os/                                    │        │
│  │  ├── standards/     ← Updated files            │        │
│  │  ├── usage/         ← Updated files            │        │
│  │  ├── workflows/     ← Updated files            │        │
│  │  └── UPGRADE_LOG.txt ← Logged                  │        │
│  └────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Data Models

### 2.1 Manifest Structure

```python
from typing import TypedDict, Dict
from datetime import datetime

class FileMetadata(TypedDict):
    checksum: str        # "sha256:abc123..."
    size: int            # File size in bytes
    last_updated: str    # ISO 8601 datetime

class Manifest(TypedDict):
    version: str                    # Agent OS version
    generated: str                  # ISO 8601 datetime
    generator_version: str          # Script version
    files: Dict[str, FileMetadata]  # Relative path → metadata
```

**Example:**
```json
{
  "version": "1.3.0",
  "generated": "2025-10-07T12:00:00Z",
  "generator_version": "1.0.0",
  "files": {
    "standards/ai-safety/credential-file-protection.md": {
      "checksum": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "size": 8245,
      "last_updated": "2025-10-01"
    },
    "usage/operating-model.md": {
      "checksum": "sha256:d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592",
      "size": 12567,
      "last_updated": "2025-09-15"
    }
  }
}
```

### 2.2 File Classification States

```python
from enum import Enum

class FileState(Enum):
    NEW = "new"                    # In manifest, not local
    UNCHANGED = "unchanged"        # Both exist, no changes
    AUTO_UPDATE = "auto_update"    # Local unchanged, upstream changed
    LOCAL_ONLY = "local_only"      # Local changed, upstream unchanged
    CONFLICT = "conflict"          # Both changed
    ERROR = "error"                # Processing error
```

### 2.3 Upgrade Report

```python
from dataclasses import dataclass
from typing import List

@dataclass
class UpgradeReport:
    added: List[str]          # Files added
    updated: List[str]        # Files auto-updated
    skipped: List[str]        # Files skipped (unchanged)
    local_only: List[str]     # Files with local-only changes
    conflicts: List[str]      # Files requiring manual decision
    errors: List[str]         # Files with errors
    
    start_time: datetime
    end_time: datetime
    backup_path: str
    dry_run: bool
```

---

## 3. Component Design

### 3.1 Manifest Generator

**File:** `scripts/generate-manifest.py`

**Responsibilities:**
1. Scan `universal/` directory recursively
2. Calculate SHA-256 checksum for each file
3. Collect file metadata (size, last modified)
4. Generate JSON manifest
5. Validate output

**Algorithm:**
```python
def generate_manifest(universal_dir: Path, version: str) -> Manifest:
    """
    Generate manifest from universal/ directory.
    
    Args:
        universal_dir: Path to universal/ directory
        version: Agent OS version string
        
    Returns:
        Manifest dictionary
    """
    files = {}
    
    # Find all markdown and JSON files
    for file_path in universal_dir.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix not in [".md", ".json"]:
            continue
        if file_path.name.startswith("."):
            continue
            
        # Calculate relative path
        rel_path = str(file_path.relative_to(universal_dir))
        
        # Calculate checksum
        checksum = calculate_checksum(file_path)
        
        # Get file size
        size = file_path.stat().st_size
        
        # Get last modified (from git if available)
        last_updated = get_last_modified_date(file_path)
        
        # Add to manifest
        files[rel_path] = {
            "checksum": f"sha256:{checksum}",
            "size": size,
            "last_updated": last_updated
        }
    
    return {
        "version": version,
        "generated": datetime.now(UTC).isoformat(),
        "generator_version": "1.0.0",
        "files": files
    }

def calculate_checksum(file_path: Path) -> str:
    """Calculate SHA-256 checksum of file."""
    import hashlib
    
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    
    return sha256.hexdigest()

def get_last_modified_date(file_path: Path) -> str:
    """Get last modified date from git, fallback to filesystem."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci", str(file_path)],
            capture_output=True,
            text=True,
            check=True
        )
        # Parse git date and convert to ISO date
        git_date = result.stdout.strip().split()[0]
        return git_date
    except:
        # Fallback to filesystem mtime
        mtime = file_path.stat().st_mtime
        return datetime.fromtimestamp(mtime).date().isoformat()
```

**Usage:**
```bash
cd agent-os-enhanced/
python scripts/generate-manifest.py --version 1.3.0 --output universal/.universal-manifest.json
```

---

### 3.2 Safe Upgrade Tool

**File:** `scripts/safe-upgrade.py`

**Responsibilities:**
1. Load and validate manifest
2. Classify each file's state
3. Create backup before changes
4. Auto-update safe files
5. Prompt for conflicts
6. Generate report

**Core Algorithm:**
```python
def classify_file(rel_path: str, manifest: Manifest, local_dir: Path, source_dir: Path) -> FileState:
    """
    Classify file state based on checksums.
    
    Args:
        rel_path: Relative path of file
        manifest: Source manifest
        local_dir: Local .agent-os/ directory
        source_dir: Source universal/ directory
        
    Returns:
        FileState enum value
    """
    local_file = local_dir / rel_path
    source_file = source_dir / rel_path
    
    # Get checksums
    manifest_checksum = manifest["files"][rel_path]["checksum"]
    source_checksum = f"sha256:{calculate_checksum(source_file)}"
    
    # Case 1: File doesn't exist locally
    if not local_file.exists():
        return FileState.NEW
    
    # Calculate local checksum
    local_checksum = f"sha256:{calculate_checksum(local_file)}"
    
    # Case 2: Local matches manifest (user hasn't changed it)
    if local_checksum == manifest_checksum:
        if source_checksum == manifest_checksum:
            return FileState.UNCHANGED
        else:
            return FileState.AUTO_UPDATE
    
    # Case 3: Local changed (user customized it)
    else:
        if source_checksum == manifest_checksum:
            return FileState.LOCAL_ONLY
        else:
            return FileState.CONFLICT

def process_file(rel_path: str, state: FileState, source_file: Path, local_file: Path, dry_run: bool) -> str:
    """
    Process a single file based on its state.
    
    Returns:
        Action taken as string (for logging)
    """
    if state == FileState.NEW:
        print(f"\n➕ New file: {rel_path}")
        print(f"   Size: {source_file.stat().st_size / 1024:.1f} KB")
        
        if dry_run:
            return "would_add"
        
        choice = input("   Add this file? [Y/n]: ").strip().lower()
        if choice in ["", "y", "yes"]:
            local_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, local_file)
            print(f"   ✅ Added")
            return "added"
        else:
            print(f"   ⏭️  Skipped")
            return "skipped"
    
    elif state == FileState.AUTO_UPDATE:
        if not dry_run:
            shutil.copy2(source_file, local_file)
            print(f"🔄 Updated: {rel_path}")
            return "updated"
        else:
            print(f"🔄 Would update: {rel_path}")
            return "would_update"
    
    elif state == FileState.UNCHANGED:
        if dry_run:
            print(f"⏭️  Unchanged: {rel_path}")
        return "skipped"
    
    elif state == FileState.LOCAL_ONLY:
        print(f"📝 Local-only changes: {rel_path}")
        return "local_only"
    
    elif state == FileState.CONFLICT:
        return handle_conflict(rel_path, source_file, local_file, dry_run)

def handle_conflict(rel_path: str, source_file: Path, local_file: Path, dry_run: bool) -> str:
    """
    Handle conflict with interactive prompt.
    """
    print(f"\n⚠️  Conflict: {rel_path}")
    print(f"   Both local and universal versions have changed.")
    print(f"\n   Local file:")
    print(f"   - Size: {local_file.stat().st_size / 1024:.1f} KB")
    print(f"   - Modified: {datetime.fromtimestamp(local_file.stat().st_mtime).strftime('%Y-%m-%d')}")
    print(f"\n   Universal file:")
    print(f"   - Size: {source_file.stat().st_size / 1024:.1f} KB")
    
    if dry_run:
        print(f"   [DRY RUN] Would prompt for action")
        return "would_conflict"
    
    while True:
        print(f"\n   Options:")
        print(f"   [K] Keep local version (your customizations)")
        print(f"   [R] Replace with universal version (lose local changes)")
        print(f"   [D] Show diff (side-by-side comparison)")
        print(f"   [S] Skip this file (decide later)")
        
        choice = input(f"\n   Your choice: ").strip().upper()
        
        if choice == "K":
            print(f"   ✅ Kept local version")
            return "kept_local"
        
        elif choice == "R":
            confirm = input(f"   ⚠️  This will overwrite your local changes. Are you sure? [y/N]: ").strip().lower()
            if confirm == "y":
                shutil.copy2(source_file, local_file)
                print(f"   ✅ Replaced with universal version")
                return "replaced"
            else:
                continue
        
        elif choice == "D":
            show_diff(local_file, source_file)
            continue
        
        elif choice == "S":
            print(f"   ⏭️  Skipped")
            return "skipped"
        
        else:
            print(f"   Invalid choice. Please choose K, R, D, or S.")
            continue

def show_diff(local_file: Path, source_file: Path):
    """Show side-by-side diff of two files."""
    import difflib
    
    with open(local_file) as f1, open(source_file) as f2:
        local_lines = f1.readlines()
        source_lines = f2.readlines()
    
    differ = difflib.Differ()
    diff = list(differ.compare(local_lines, source_lines))
    
    print(f"\n   === DIFF ===")
    print(f"   - = Local version (will be lost if replaced)")
    print(f"   + = Universal version (new content)\n")
    
    for line in diff[:50]:  # Show first 50 lines
        if line.startswith('- '):
            print(f"   {line}", end='')
        elif line.startswith('+ '):
            print(f"   {line}", end='')
        elif line.startswith('? '):
            continue  # Skip hint lines
    
    if len(diff) > 50:
        print(f"\n   ... ({len(diff) - 50} more lines)")
    
    print(f"\n   === END DIFF ===\n")
```

**Main Function:**
```python
def main():
    parser = argparse.ArgumentParser(description="Safe Agent OS upgrade tool")
    parser.add_argument("--source", required=True, help="Path to agent-os-enhanced repo")
    parser.add_argument("--target", default=".agent-os", help="Path to local .agent-os directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--yes", action="store_true", help="Auto-confirm all prompts (dangerous)")
    
    args = parser.parse_args()
    
    # Validate source
    source_dir = Path(args.source) / "universal"
    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        sys.exit(1)
    
    # Load manifest
    manifest_path = source_dir / ".universal-manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found: {manifest_path}")
        sys.exit(1)
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    print(f"Agent OS Upgrade Tool")
    print(f"{'='*60}")
    print(f"Source: {source_dir}")
    print(f"Target: {args.target}")
    print(f"Version: {manifest['version']}")
    print(f"Dry run: {args.dry_run}")
    print(f"{'='*60}\n")
    
    # Create backup
    if not args.dry_run:
        backup_dir = create_backup(args.target)
        print(f"✅ Backup created: {backup_dir}\n")
    
    # Process each file
    report = UpgradeReport(
        added=[], updated=[], skipped=[], local_only=[], conflicts=[], errors=[],
        start_time=datetime.now(),
        end_time=None,
        backup_path=backup_dir if not args.dry_run else None,
        dry_run=args.dry_run
    )
    
    for rel_path, metadata in manifest["files"].items():
        source_file = source_dir / rel_path
        local_file = Path(args.target) / rel_path
        
        try:
            state = classify_file(rel_path, manifest, Path(args.target), source_dir)
            action = process_file(rel_path, state, source_file, local_file, args.dry_run)
            
            # Update report
            if action == "added":
                report.added.append(rel_path)
            elif action == "updated":
                report.updated.append(rel_path)
            elif action == "skipped":
                report.skipped.append(rel_path)
            elif action == "local_only":
                report.local_only.append(rel_path)
            elif action in ["kept_local", "replaced"]:
                report.conflicts.append(rel_path)
        
        except Exception as e:
            print(f"❌ Error processing {rel_path}: {e}")
            report.errors.append(rel_path)
    
    # Print summary
    report.end_time = datetime.now()
    print_summary(report)
    
    # Write log
    if not args.dry_run:
        write_upgrade_log(args.target, report, manifest)

if __name__ == "__main__":
    main()
```

---

## 4. Integration Points

### 4.1 File Watcher Integration

After upgrade, RAG index auto-rebuilds:
```
.agent-os/ files change
    ↓
File watcher detects
    ↓
Triggers RAG rebuild
    ↓
MCP server uses new content
```

No manual index rebuild needed (already implemented).

### 4.2 Update Procedures Standard

Update `universal/standards/installation/update-procedures.md`:
```markdown
## Recommended Update Process

1. Pull latest agent-os-enhanced
2. Run manifest generator (if developing)
3. Run safe-upgrade tool with dry-run
4. Review preview
5. Execute upgrade
6. Verify with test query
```

---

## 5. Testing Strategy

### 5.1 Unit Tests

**Test File:** `tests/unit/test_manifest_generator.py`

```python
def test_calculate_checksum():
    """Test checksum calculation."""
    # Create temp file with known content
    # Calculate checksum
    # Verify matches expected SHA-256

def test_generate_manifest():
    """Test manifest generation."""
    # Create temp directory structure
    # Generate manifest
    # Verify all files included
    # Verify checksums correct

def test_manifest_validation():
    """Test manifest JSON validation."""
    # Valid manifest → passes
    # Invalid JSON → fails
    # Missing fields → fails
```

**Test File:** `tests/unit/test_safe_upgrade.py`

```python
def test_classify_file_new():
    """Test classification of new file."""
    # File in manifest, not local → NEW

def test_classify_file_unchanged():
    """Test classification of unchanged file."""
    # Local == manifest, source == manifest → UNCHANGED

def test_classify_file_auto_update():
    """Test classification of auto-update file."""
    # Local == manifest, source != manifest → AUTO_UPDATE

def test_classify_file_local_only():
    """Test classification of local-only modified file."""
    # Local != manifest, source == manifest → LOCAL_ONLY

def test_classify_file_conflict():
    """Test classification of conflict."""
    # Local != manifest, source != manifest → CONFLICT
```

### 5.2 Integration Tests

**Test:** Dogfood on python-sdk

1. Generate manifest from agent-os-enhanced
2. Run safe-upgrade on python-sdk in dry-run mode
3. Verify detection of:
   - New files (if any added)
   - Unchanged files
   - Customized files
4. Execute upgrade
5. Verify no data loss
6. Verify MCP queries work

---

## 6. Performance Optimization

### 6.1 Checksum Calculation

Use chunked reading (8KB chunks) for efficient memory usage:
```python
# Good: Memory-efficient
sha256 = hashlib.sha256()
with open(file_path, 'rb') as f:
    for chunk in iter(lambda: f.read(8192), b''):
        sha256.update(chunk)

# Bad: Loads entire file into memory
sha256 = hashlib.sha256(file_path.read_bytes())
```

### 6.2 Parallel Processing

For large numbers of files, use multiprocessing:
```python
from multiprocessing import Pool

def calculate_file_metadata(file_path):
    return {
        "checksum": calculate_checksum(file_path),
        "size": file_path.stat().st_size
    }

with Pool() as pool:
    results = pool.map(calculate_file_metadata, file_paths)
```

---

## 7. Error Handling

### 7.1 Common Errors

| Error | Cause | Handling |
|-------|-------|----------|
| Manifest not found | Old source repo | Clear error, show how to fix |
| Invalid source path | Wrong directory | Validate early, fail fast |
| Permission denied | File access issue | Clear error, suggest chmod |
| Backup failed | Disk full | Abort before changes |
| Partial update | Interrupted | Log progress, support resume |

### 7.2 Rollback Procedure

If upgrade fails:
```bash
# 1. Identify backup
ls -lt .agent-os.backup.* | head -1

# 2. Restore
rm -rf .agent-os
mv .agent-os.backup.YYYYMMDD_HHMMSS .agent-os

# 3. Verify
mcp_agent-os-rag_search_standards("test query")
```

---

## 8. Security Considerations

### 8.1 Path Traversal Prevention

```python
def safe_path_join(base: Path, rel_path: str) -> Path:
    """Safely join paths, preventing directory traversal."""
    result = (base / rel_path).resolve()
    if not result.is_relative_to(base.resolve()):
        raise ValueError(f"Path traversal detected: {rel_path}")
    return result
```

### 8.2 Manifest Integrity

```python
def validate_manifest(manifest: dict) -> bool:
    """Validate manifest structure and content."""
    required_fields = ["version", "generated", "files"]
    if not all(field in manifest for field in required_fields):
        return False
    
    # Validate each file entry
    for rel_path, metadata in manifest["files"].items():
        if not all(k in metadata for k in ["checksum", "size"]):
            return False
        if not metadata["checksum"].startswith("sha256:"):
            return False
    
    return True
```

---

**Technical specifications complete. Ready for implementation.**
