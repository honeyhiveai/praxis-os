# Software Requirements Document

**Project:** Manifest-Based Upgrade System  
**Date:** 2025-10-07

---

## 1. Introduction

### 1.1 Purpose

Define requirements for a safe upgrade system that enables consuming projects to update their prAxIs OS skeleton files from `universal/` without risk of losing custom content.

### 1.2 Scope

This system provides:
1. Automated manifest generation from `universal/` directory
2. Interactive upgrade tool with conflict detection
3. Safe update guarantees for consuming projects

### 1.3 Definitions

- **Skeleton Files**: Files from `universal/` that are copied to `.praxis-os/` on initial install
- **Universal Files**: Original files in praxis-os's `universal/` directory
- **Local Files**: Files in consuming project's `.praxis-os/` directory
- **Manifest**: JSON file tracking checksums of all skeleton files
- **Divergence**: When both local and universal versions of a file have changed
- **Conflict**: Situation requiring user decision (both files changed)

---

## 2. Stakeholder Requirements

### 2.1 prAxIs OS Maintainers

**SR-1:** MUST be able to generate manifest automatically  
**SR-2:** MUST track all files in `universal/` directory  
**SR-3:** SHOULD generate manifest as part of release process  
**SR-4:** MUST validate manifest completeness

### 2.2 Consuming Project Maintainers

**SR-5:** MUST be able to upgrade safely without losing custom content  
**SR-6:** MUST see preview of changes before applying  
**SR-7:** MUST be prompted before overwriting modified files  
**SR-8:** SHOULD be able to see diffs for conflicts  
**SR-9:** MUST be able to rollback failed upgrades  
**SR-10:** SHOULD have upgrade complete in <5 minutes for typical case

### 2.3 AI Assistants

**SR-11:** SHOULD NOT run upgrade tools without human approval  
**SR-12:** SHOULD query standards before advising on upgrades  
**SR-13:** MUST NOT use `rsync --delete` directly (use safe-upgrade.py)

---

## 3. Functional Requirements

### 3.1 Manifest Generation

**FR-1:** Manifest generator MUST scan all files in `universal/` directory  
**FR-2:** Manifest generator MUST calculate SHA-256 checksum for each file  
**FR-3:** Manifest generator MUST record file size for each file  
**FR-4:** Manifest generator MUST record last modified timestamp  
**FR-5:** Manifest generator MUST output `.universal-manifest.json`  
**FR-6:** Manifest generator SHOULD use git to determine last modified date  
**FR-7:** Manifest generator MUST validate output JSON structure  
**FR-8:** Manifest generator MUST handle subdirectories recursively

**Manifest Format:**
```json
{
  "version": "1.3.0",
  "generated": "2025-10-07T12:00:00Z",
  "generator_version": "1.0.0",
  "files": {
    "standards/ai-safety/credential-file-protection.md": {
      "checksum": "sha256:abc123...",
      "size": 1234,
      "last_updated": "2025-10-01"
    }
  }
}
```

### 3.2 Upgrade Tool - Core Logic

**FR-9:** Upgrade tool MUST read manifest from source  
**FR-10:** Upgrade tool MUST compare each manifest file with local copy  
**FR-11:** Upgrade tool MUST calculate checksums using same algorithm (SHA-256)  
**FR-12:** Upgrade tool MUST support dry-run mode (no changes)  
**FR-13:** Upgrade tool MUST log all actions to file and console

### 3.3 Upgrade Tool - File Classification

**FR-14:** Upgrade tool MUST classify each file into one of these states:

| State | Condition | Action |
|-------|-----------|--------|
| **New** | File in manifest but not local | Prompt to add |
| **Unchanged** | Local checksum == manifest checksum, upstream unchanged | Skip |
| **Auto-Update** | Local checksum == manifest checksum, upstream changed | Auto-update |
| **Local-Only Modified** | Local changed, upstream unchanged | Skip with note |
| **Conflict** | Both local and upstream changed | Interactive prompt |

### 3.4 Upgrade Tool - Interactive Prompts

**FR-15:** For new files, prompt:
```
➕ New file: standards/ai-safety/spec-driven-development.md
   Size: 12.3 KB
   Description: Spec-driven development process standard
   
   Add this file? [Y/n]:
```

**FR-16:** For conflicts, prompt:
```
⚠️  Conflict: standards/ai-safety/credential-file-protection.md
   Both local and universal versions have changed.
   
   Local changes:
   - Modified 2025-09-15
   - Size: 8.2 KB
   
   Universal changes:
   - Modified 2025-10-05
   - Size: 8.7 KB
   - Added: API key detection patterns
   
   Options:
   [K] Keep local version (your customizations)
   [R] Replace with universal version (lose local changes)
   [D] Show diff (side-by-side comparison)
   [S] Skip this file (decide later)
   
   Your choice:
```

**FR-17:** Diff view MUST show side-by-side comparison  
**FR-18:** After showing diff, MUST re-prompt for action

### 3.5 Upgrade Tool - Safety Guarantees

**FR-19:** Upgrade tool MUST create backup before any changes  
**FR-20:** Backup directory name MUST include timestamp  
**FR-21:** Upgrade tool MUST NOT overwrite files without explicit permission  
**FR-22:** Upgrade tool MUST NOT delete files  
**FR-23:** Upgrade tool MUST validate source manifest integrity  
**FR-24:** Upgrade tool MUST verify source directory is `universal/` (not `.praxis-os/`)

### 3.6 Upgrade Tool - Reporting

**FR-25:** Upgrade tool MUST generate summary report:
```
UPGRADE SUMMARY
================
✅ Added: 3 files
🔄 Updated: 12 files
⏭️  Skipped: 25 files (unchanged)
📝 Local-only: 4 files (customized, upstream unchanged)
⚠️  Conflicts: 2 files (manual review needed)
❌ Errors: 0 files

Time: 2m 34s
Backup: .praxis-os.backup.20251007_143022
```

**FR-26:** Upgrade tool MUST maintain upgrade log:
```
.praxis-os/UPGRADE_LOG.txt

2025-10-07 14:30:22 | v1.3.0 | abc123 | Added: 3, Updated: 12, Conflicts: 2
2025-09-15 10:15:00 | v1.2.2 | def456 | Added: 0, Updated: 5, Conflicts: 0
```

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-1:** Manifest generation MUST complete in <10 seconds for 100 files  
**NFR-2:** Checksum calculation MUST use efficient algorithm (not line-by-line)  
**NFR-3:** Upgrade dry-run MUST complete in <30 seconds for 100 files  
**NFR-4:** Interactive prompts MUST respond immediately (<100ms)

### 4.2 Usability

**NFR-5:** Command-line interface MUST be clear and self-explanatory  
**NFR-6:** Prompts MUST use clear language (avoid technical jargon)  
**NFR-7:** Default options MUST be safe (prefer keeping local)  
**NFR-8:** Help text MUST be available (`--help`)

### 4.3 Reliability

**NFR-9:** Upgrade tool MUST be idempotent (safe to run multiple times)  
**NFR-10:** Backup creation MUST succeed before any changes  
**NFR-11:** Partial failures MUST NOT leave system in broken state  
**NFR-12:** Rollback MUST be straightforward (documented in error messages)

### 4.4 Maintainability

**NFR-13:** Code MUST use Python standard library only (no dependencies)  
**NFR-14:** Code MUST be type-hinted  
**NFR-15:** Code MUST have docstrings  
**NFR-16:** Code MUST follow existing project style

### 4.5 Security

**NFR-17:** Checksum algorithm MUST be cryptographically secure (SHA-256)  
**NFR-18:** File operations MUST validate paths (prevent directory traversal)  
**NFR-19:** Manifest MUST be validated before use (JSON schema)

---

## 5. Constraints

### 5.1 Technical Constraints

- Must work with Python 3.11+
- Must work on macOS, Linux, and Windows
- Cannot require new dependencies
- Must integrate with existing file structure

### 5.2 Process Constraints

- Must not break existing update procedures
- Must support both automated and manual workflows
- Must be testable without affecting production

---

## 6. Acceptance Criteria

### 6.1 Manifest Generation

- [ ] Generates manifest with all universal/ files
- [ ] Checksums match actual file content
- [ ] Output is valid JSON
- [ ] Includes version and timestamp metadata
- [ ] Runs in <10 seconds for 100 files

### 6.2 Upgrade Tool - Basic Functionality

- [ ] Reads and validates manifest
- [ ] Detects all file states correctly (new, unchanged, conflict, etc.)
- [ ] Auto-updates safe files without prompting
- [ ] Prompts for conflicts with clear options
- [ ] Creates backup before changes

### 6.3 Upgrade Tool - Safety

- [ ] Never overwrites without permission
- [ ] Never deletes files
- [ ] Validates source directory is universal/
- [ ] Dry-run shows preview without changes
- [ ] Rollback procedure works

### 6.4 Upgrade Tool - Usability

- [ ] Clear progress indicators
- [ ] Helpful error messages
- [ ] Summary report at end
- [ ] Upgrade log maintained
- [ ] Help text available

### 6.5 Integration

- [ ] Works with existing update-procedures standard
- [ ] Documented in agent-os-update-guide.md
- [ ] Successfully upgrades python-sdk (dogfooding)
- [ ] No breaking changes to existing workflows

---

## 7. Dependencies

### 7.1 Existing Systems

- `universal/standards/installation/update-procedures.md` - Current process
- `universal/` directory structure
- `.praxis-os/` directory structure

### 7.2 Future Enhancements

- CI/CD integration for automated manifest generation
- Three-way merge tool for complex conflicts
- Git integration for tracking changes
- MCP tool for programmatic upgrades

---

## 8. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Manifest becomes stale | Medium | Auto-generate on release, validate on upgrade |
| User ignores conflicts | High | Make prompts very clear, default to safe option |
| Checksum collision | High | Use SHA-256 (collision probability negligible) |
| Large files slow | Low | Current files are text, optimize if needed |
| User loses custom work | Critical | Multiple prompts, show diffs, create backups |

---

## 9. Future Enhancements (Out of Scope)

- **Automated Scheduling**: Cron job for periodic updates
- **Three-Way Merge**: Intelligent merging for structured formats
- **Version Constraints**: Specify minimum/maximum compatible versions
- **Selective Upgrade**: Update only specific directories/files
- **MCP Tool Integration**: Programmatic access for AI assistants
- **Web UI**: Browser-based diff viewer and conflict resolution

---

## 10. References

- [Upgrade Strategy Analysis](../../../uograde-strategy-analysis.md)
- [Update Procedures Standard](../../../universal/standards/installation/update-procedures.md)
- [prAxIs OS Operating Model](../../../universal/usage/operating-model.md)

---

**Approval Status:** Draft - Pending Review
