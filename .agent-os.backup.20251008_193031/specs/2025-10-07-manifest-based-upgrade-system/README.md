# Manifest-Based Upgrade System

**Date:** 2025-10-07  
**Status:** Draft - Pending Approval  
**Priority:** High  
**Estimated Effort:** 2-3 days

---

## Executive Summary

Implement a safe, manifest-based upgrade system that allows consuming projects to update their Agent OS skeleton files without risk of losing custom content.

**Core Innovation:** Checksum-based tracking with interactive prompts for conflicts.

---

## Problem Statement

**Current State:**
- Update procedures documented in `universal/standards/installation/update-procedures.md`
- Uses `rsync --delete` which is dangerous for diverged files
- No tracking of which skeleton files have been customized
- No safe way to detect conflicts between local and upstream changes
- Manual process prone to errors

**Pain Points:**
1. Fear of overwriting custom content during updates
2. No visibility into what will change before applying
3. Cannot detect when both local and upstream versions changed
4. All-or-nothing approach (update everything or nothing)

---

## Solution Overview

Implement two complementary tools:

### 1. Manifest Generator (`scripts/generate-manifest.py`)
- Scans `universal/` directory
- Generates `.universal-manifest.json` with checksums
- Tracks file size, last modified date
- Runs automatically on release preparation

### 2. Safe Upgrade Tool (`scripts/safe-upgrade.py`)
- Reads manifest from source
- Compares checksums with local files
- Auto-updates unchanged files
- Prompts user for conflict resolution
- Dry-run mode for preview
- Detailed logging and rollback support

**Key Guarantee:** Never overwrites modified files without explicit user permission.

---

## Design Principles

1. **Safety First:** Never delete or overwrite without permission
2. **User Control:** Interactive prompts for conflicts
3. **Transparency:** Show diffs, log all actions
4. **Idempotent:** Safe to run multiple times
5. **Rollback-Ready:** Automatic backups before changes

---

## Architecture Overview

```
agent-os-enhanced/
├── universal/
│   ├── .universal-manifest.json  ← Generated manifest
│   ├── standards/
│   ├── usage/
│   └── workflows/
└── scripts/
    ├── generate-manifest.py       ← New: Manifest generator
    └── safe-upgrade.py             ← New: Interactive upgrade tool
```

**Upgrade Flow:**
```
1. Generate Manifest (on release)
   └→ Checksums all universal/ files

2. User Runs Upgrade (on consuming project)
   └→ Compare local vs manifest checksums
       ├→ Match → Auto-update if upstream changed
       ├→ Local modified, upstream unchanged → Skip
       └→ Both changed → Interactive prompt
           ├→ [K]eep local
           ├→ [R]eplace with universal
           ├→ [D]iff to review
           └→ [S]kip
```

---

## Scope

### In Scope
- Manifest generation script
- Safe upgrade script with interactive prompts
- Checksum-based divergence detection
- Dry-run mode
- Automatic backups
- Detailed logging
- Integration with existing update-procedures standard

### Out of Scope
- Automated CI/CD integration (future enhancement)
- Git-based tracking (future enhancement)
- MCP server update automation (separate concern)
- Three-way merge tool (too complex for v1)

---

## Success Criteria

- [ ] Manifest accurately tracks all universal/ files
- [ ] Upgrade tool detects conflicts correctly
- [ ] User prompted for every conflict
- [ ] Unchanged files auto-update safely
- [ ] Dry-run shows preview without changes
- [ ] Backups created before any modifications
- [ ] Rollback procedure documented and tested
- [ ] Dogfooded on python-sdk successfully

---

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Checksum collision | High | Very Low | Use SHA-256 (cryptographically secure) |
| User accidentally overwrites | High | Medium | Require explicit confirmation, show diffs |
| Manifest out of date | Medium | Low | Auto-generate on release, validate on upgrade |
| Large files slow | Low | Low | Optimize for text files only (no binaries) |

---

## Dependencies

- Python 3.11+ (already required)
- No new dependencies (uses stdlib only)
- Existing `universal/standards/installation/update-procedures.md`

---

## Deliverables

1. **Scripts**
   - `scripts/generate-manifest.py`
   - `scripts/safe-upgrade.py`

2. **Manifest**
   - `universal/.universal-manifest.json`

3. **Documentation**
   - Update `universal/usage/agent-os-update-guide.md`
   - Add examples and troubleshooting

4. **Testing**
   - Unit tests for both scripts
   - Integration test on python-sdk (dogfooding)

---

## Related Documents

- [Upgrade Strategy Analysis](../../../uograde-strategy-analysis.md) - Design discussion
- [Update Procedures Standard](../../../universal/standards/installation/update-procedures.md) - Current process

---

## Approval

**Created by:** AI Assistant (Claude)  
**Requires Approval from:** Josh

**Next Step:** Review this spec, approve approach, then implement.
