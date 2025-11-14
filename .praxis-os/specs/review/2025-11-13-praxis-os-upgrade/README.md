# praxis-os Upgrade System Specification

**Status:** 🚧 In Review  
**Version:** 1.0.0  
**Created:** 2025-11-13  
**Author:** AI Agent (Claude)  
**Workflow:** Created via `spec_creation_v1`

---

## 📋 Overview

This specification defines a Python-based upgrade script (`upgrade-praxis-os.py`) that safely updates praxis-os consumer installations in 3-5 minutes with mandatory backup, automatic rollback, and zero data loss.

**Key Features:**
- ✅ 8-phase upgrade flow (pre-flight → backup → clone → upgrade → config → deps → validate → cleanup)
- ✅ Mandatory backup (5s, 50MB, excludes indexes)
- ✅ Automatic rollback on any failure
- ✅ Preserves user content (specs, customizations)
- ✅ Breaking change detection (mcp_server → ouroboros)
- ✅ Version-aware config loading (old configs work, no deadlock)
- ✅ CLI with --dry-run, --source, --skip-deps flags

---

## 📂 Specification Documents

### Core Documents

- **[srd.md](srd.md)** - Software Requirements Document  
  Complete requirements: 3 business goals, 4 user stories, 14 functional requirements, 6 non-functional requirements, success metrics

- **[specs.md](specs.md)** - Technical Specifications  
  Detailed design: 8-phase architecture, 8 components, CLI API, 3 data models, 5 security controls, 4 performance strategies

- **[tasks.md](tasks.md)** - Implementation Tasks  
  23 tasks across 4 phases (12-16 hours): core infrastructure, component implementation, integration & CLI, testing & docs

- **[implementation.md](implementation.md)** - Implementation Guide  
  Code patterns, testing strategy (unit/integration/property-based), deployment guidance, troubleshooting guide

### Testing Documentation

- **[testing/requirements-list.md](testing/requirements-list.md)** - All FRs and NFRs for traceability
- **Testing plans:** Comprehensive test cases (see implementation.md for full strategy)

### Supporting Documents

- **[supporting-docs/design-doc.md](supporting-docs/design-doc.md)** - Original conversational design with all 6 design questions resolved

---

## 🎯 Quick Start

### For Implementers

1. Read `srd.md` - Understand requirements
2. Read `specs.md` - Understand technical design
3. Read `tasks.md` - Follow 23-task implementation plan
4. Read `implementation.md` - Apply code patterns and best practices
5. Execute via `spec_execution_v1` workflow

### For Reviewers

1. Check `srd.md` - Requirements complete and measurable?
2. Check `specs.md` - Design addresses all requirements?
3. Check `tasks.md` - Tasks cover all design components?
4. Check `testing/` - Test coverage comprehensive?
5. Approve or request changes

---

## 📊 Specification Metrics

- **Requirements:** 14 functional + 6 non-functional = 20 total
- **Components:** 8 classes (PreFlightValidator, BackupManager, SourceCloner, FileUpgrader, ConfigReconciler, DependencyUpdater, UpgradeValidator, UpgradeOrchestrator)
- **Implementation Tasks:** 23 tasks across 4 phases
- **Estimated Effort:** 12-16 hours
- **Target Performance:** 3-5 minutes upgrade time, 99.9% success rate

---

## 🔗 Requirements Traceability

| Requirement | Component | Test |
|-------------|-----------|------|
| FR-1 (Pre-flight) | PreFlightValidator | test_preflight_validates_all |
| FR-2 (Backup) | BackupManager | test_backup_excludes_cache |
| FR-4 (Upgrade files) | FileUpgrader | test_preserves_user_files |
| FR-11 (Rollback) | UpgradeOrchestrator | test_rollback_on_error |
| NFR-1 (Performance) | All | test_upgrade_time_under_5min |

*Full traceability matrix in testing documentation*

---

## 🚀 Implementation Workflow

This spec was created using `spec_creation_v1` workflow.

**Next Step:** Execute via `spec_execution_v1` workflow:

```python
pos_workflow(
    action="start",
    workflow_type="spec_execution_v1",
    target_file=".praxis-os/specs/review/2025-11-13-praxis-os-upgrade/tasks.md"
)
```

---

## 🔄 Approval Process

**Current Status:** 🚧 In Review

**Review Checklist:**
- [ ] Requirements complete and measurable?
- [ ] Design addresses all requirements?
- [ ] Security considerations addressed?
- [ ] Performance targets realistic?
- [ ] Testing strategy comprehensive?
- [ ] Documentation clear?

**To Approve:**
1. Review all documents
2. Move spec to `specs/approved/2025-11-13-praxis-os-upgrade/`
3. Begin implementation via `spec_execution_v1`

---

## 📚 Related Documentation

- **Install Script:** `scripts/install-praxis-os.py` (80% code reuse)
- **Upgrade Docs:** `docs/content/how-to-guides/upgrading.md` (will be rewritten)
- **Breaking Changes:** See specs.md § Breaking Change Detection

---

## 🔧 Development Environment

**Requirements:**
- Python 3.9+
- Git
- pytest (for testing)
- mypy (for type checking)

**Setup:**
```bash
# Install dev dependencies
pip install pytest mypy pylint black

# Run tests
pytest tests/

# Type check
mypy scripts/upgrade-praxis-os.py

# Format code
black scripts/upgrade-praxis-os.py
```

---

## 📝 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-13 | AI Agent (Claude) | Initial specification via spec_creation_v1 workflow |

---

**Questions or Issues?** Review supporting documentation or ask the spec author.

