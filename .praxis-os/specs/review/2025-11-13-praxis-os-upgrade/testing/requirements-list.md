# Requirements Traceability List

**Spec ID:** 2025-11-13-praxis-os-upgrade  
**Purpose:** Complete list of requirements for test coverage tracking

---

## Functional Requirements

### FR-1: Pre-Flight Validation
- FR-1.1: Verify `.praxis-os/` directory exists
- FR-1.2: Verify `.praxis-os/ouroboros/` exists
- FR-1.3: Check Python ≥ 3.9 available
- FR-1.4: Check git installed
- FR-1.5: Verify disk space ≥ 500MB
- FR-1.6: Detect breaking changes
- FR-1.7: Exit with clear error if checks fail

### FR-2: Mandatory Backup
- FR-2.1: Create timestamped backup directory
- FR-2.2: Backup essential files
- FR-2.3: Exclude ephemeral data
- FR-2.4: Generate checksum manifest
- FR-2.5: Validate backup integrity
- FR-2.6: Complete in < 10 seconds
- FR-2.7: Backup size < 100MB
- FR-2.8: Support --skip-backup flag

### FR-3: Source Acquisition
- FR-3.1: Clone from GitHub
- FR-3.2: Support --source flag
- FR-3.3: Validate source structure
- FR-3.4: Extract version
- FR-3.5: Compare versions
- FR-3.6: Display version change
- FR-3.7: Complete in < 60 seconds

### FR-4: Framework File Upgrade
- FR-4.1-4.4: Rsync framework files
- FR-4.5: Use --delete flag
- FR-4.6: Preserve specs/
- FR-4.7: Preserve standards/development/
- FR-4.8: Generate change report
- FR-4.9: Verify checksums
- FR-4.10: Complete in < 90 seconds

### FR-5: Config Reconciliation
- FR-5.1: Copy template
- FR-5.2: Compare configs
- FR-5.3: Skip if no changes
- FR-5.4: Create prompt if changes
- FR-5.5: Prompt includes instructions
- FR-5.6: Display instructions
- FR-5.7: Complete in < 15 seconds

### FR-6: Gitignore Merge
- FR-6.1-6.6: Additive merge of patterns

### FR-7: Dependency Update
- FR-7.1-7.6: Update venv dependencies

### FR-8: Index Rebuild Trigger
- FR-8.1-8.4: Create rebuild flag

### FR-9: Upgrade Validation
- FR-9.1-9.7: File-based validation

### FR-10: Cleanup & Reporting
- FR-10.1-10.5: Cleanup and report

### FR-11: Automatic Rollback
- FR-11.1-11.7: Rollback on failure

### FR-12: Dry-Run Preview
- FR-12.1-12.4: Show changes without modifying

### FR-13: Breaking Change Detection
- FR-13.1-13.4: Detect and explain breaking changes

### FR-14: Concurrent Prevention
- FR-14.1-14.6: Prevent concurrent upgrades

---

## Non-Functional Requirements

### NFR-1: Performance
- NFR-1.1: Total time < 5 minutes
- NFR-1.2: Backup < 10 seconds
- NFR-1.3: File copy < 90 seconds
- NFR-1.4: Dependencies < 60 seconds
- NFR-1.5: Validation < 30 seconds

### NFR-2: Reliability
- NFR-2.1: 99.9% success rate
- NFR-2.2: 100% rollback on failure
- NFR-2.3: 100% user content preservation
- NFR-2.4: 0% data loss

### NFR-3: Maintainability
- NFR-3.1: Single script < 1000 lines
- NFR-3.2: Reuse 80%+ install logic
- NFR-3.3: Clear documentation
- NFR-3.4: Type hints
- NFR-3.5: Test coverage > 80%

### NFR-4: Usability
- NFR-4.1: Single command
- NFR-4.2: Progress indicators
- NFR-4.3: Clear messages
- NFR-4.4: Actionable errors
- NFR-4.5: --help with examples

### NFR-5: Safety
- NFR-5.1: Mandatory backup
- NFR-5.2: Atomic operations
- NFR-5.3: Checksum validation
- NFR-5.4: Automatic rollback
- NFR-5.5: Dry-run mode

### NFR-6: Compatibility
- NFR-6.1: Python ≥ 3.9
- NFR-6.2: macOS, Linux, Windows
- NFR-6.3: No new dependencies
- NFR-6.4: Compatible with existing structure

