# prAxIs OS Upgrade Workflow - Specification

**Version:** 1.0  
**Date:** 2025-10-08  
**Status:** ✅ Complete  
**Workflow ID:** `praxis_os_upgrade_v1`

---

## Executive Summary

An AI-guided workflow for safely upgrading prAxIs OS installations (content + MCP server) with automatic validation, rollback capability, and persistence across server restarts. Demonstrates meta-workflow principles for complex operational tasks.

**Key Innovation:** Workflow state persists to disk (`.praxis-os/.cache/state/`), enabling the workflow to survive MCP server restarts during the upgrade process.

---

## Quick Links

- **Requirements:** [srd.md](srd.md) - What needs to be built and why
- **Technical Design:** [specs.md](specs.md) - How it will be built
- **Implementation Tasks:** [tasks.md](tasks.md) - Step-by-step task breakdown
- **Implementation Guide:** [implementation.md](implementation.md) - Code patterns and testing
- **Supporting Documents:** [supporting-docs/](supporting-docs/) - Additional documentation

---

## What This Workflow Does

The prAxIs OS Upgrade Workflow automates the entire upgrade process:

1. **Phase 0: Pre-Flight Checks** (30s)
   - Validates source repository
   - Checks git status is clean
   - Verifies disk space
   - Prevents concurrent upgrades

2. **Phase 1: Backup & Preparation** (20s)
   - Creates timestamped backup
   - Generates checksum manifest
   - Acquires upgrade lock

3. **Phase 2: Content Upgrade** (45s)
   - Runs safe-upgrade.py with conflict detection
   - Updates standards, usage, workflows
   - Updates version tracking

4. **Phase 3: MCP Server Upgrade** (60s) ⚠️ **Critical Phase**
   - Copies MCP server code
   - Installs dependencies
   - Runs post-install steps (playwright, etc.)
   - **Restarts MCP server**
   - Workflow resumes from disk state

5. **Phase 4: Post-Upgrade Validation** (30s)
   - Checks tool registration
   - Runs smoke tests
   - Validates RAG and browser tools

6. **Phase 5: Cleanup & Documentation** (15s)
   - Releases upgrade lock
   - Archives old backups
   - Generates reports

**Total Time:** ~3 minutes 20 seconds

---

## Key Features

### ✅ Automatic Rollback

If any phase fails (2, 3, or 4), the workflow automatically rolls back to the backup created in Phase 1. Target rollback time: < 30 seconds.

### ✅ State Persistence

Workflow state is saved to disk after each phase, enabling the workflow to survive the MCP server restart in Phase 3. This is a first for prAxIs OS workflows.

### ✅ Safety First

- Pre-flight checks prevent bad upgrades
- Timestamped backups with checksum verification
- Never overwrites user config without prompting
- Concurrent upgrade prevention via lock file

### ✅ Comprehensive Validation

- Git status checks (source must be clean)
- Disk space checks (need 2x current size)
- Post-upgrade smoke tests
- Health checks after server restart

---

## For Implementers

### Implementation Phases

The implementation is broken into 5 phases over 4-5 weeks:

1. **Foundation & Core Components** (Week 1)
   - StateManager, BackupManager, ValidationModule
   - DependencyInstaller, ServerManager, ReportGenerator

2. **Workflow Phases 0-1** (Week 2)
   - Pre-flight checks and backup preparation
   - Integration testing

3. **Workflow Phases 2-3** (Week 2-3)
   - Content upgrade and server upgrade
   - Resume capability after restart

4. **Workflow Phases 4-5 & Rollback** (Week 3-4)
   - Validation and cleanup
   - Rollback procedure

5. **Testing & Refinement** (Week 4-5)
   - Dogfooding tests
   - Documentation
   - Performance validation

**Total Duration:** 34 days (5 weeks) with buffer

### Quick Start for Developers

1. Read [srd.md](srd.md) to understand requirements
2. Read [specs.md](specs.md) for architecture and design
3. Review [tasks.md](tasks.md) for task breakdown
4. Follow [implementation.md](implementation.md) for code patterns
5. Start with Task 1.1 (Foundation)

### Testing Strategy

- **Unit Tests:** > 85% coverage for all components
- **Integration Tests:** End-to-end workflow scenarios
- **Dogfooding:** Test on praxis-os itself
- **Performance:** Validate all timing targets

---

## For Reviewers

### Review Checklist

**Requirements (srd.md):**
- [ ] Business goals clearly stated with metrics
- [ ] User stories follow format with acceptance criteria
- [ ] Functional requirements (30 total) are specific and testable
- [ ] Non-functional requirements have targets
- [ ] Out-of-scope items documented with rationale

**Technical Design (specs.md):**
- [ ] Architecture diagrams clear and complete
- [ ] All 8 components defined with responsibilities
- [ ] APIs and interfaces specified
- [ ] Data models complete with serialization
- [ ] Security controls addressed
- [ ] Performance targets realistic
- [ ] Error handling comprehensive

**Task Breakdown (tasks.md):**
- [ ] 34 tasks across 5 implementation phases
- [ ] All tasks have acceptance criteria
- [ ] Dependencies mapped correctly
- [ ] Time estimates reasonable
- [ ] Validation gates defined

**Implementation Guide (implementation.md):**
- [ ] Code patterns with concrete examples
- [ ] Testing strategy detailed
- [ ] Deployment guidance step-by-step
- [ ] Troubleshooting guide comprehensive
- [ ] Security considerations addressed

---

## Success Metrics

### Key Performance Indicators (KPIs)

| Metric | Baseline | Target | Timeline |
|--------|----------|--------|----------|
| Manual upgrade time | ~10 min | < 2 min | Immediate |
| Upgrade-related support tickets | ~5/week | < 1/week | 30 days |
| Users on latest version | ~40% | > 80% | 60 days |
| Failed upgrade rate | Unknown | < 5% | 30 days |
| User satisfaction (NPS) | Unknown | > 50 | 60 days |

### Validation Criteria

An upgrade is successful if:

1. ✅ All 6 phases complete without errors
2. ✅ MCP server responds to requests
3. ✅ All expected tools registered
4. ✅ Smoke tests pass
5. ✅ No errors in server log
6. ✅ Version updated correctly
7. ✅ User customizations preserved

---

## Document Structure

```
.praxis-os/specs/2025-10-08-agent-os-upgrade-workflow/
├── README.md                   (This file - Overview)
├── srd.md                      (System Requirements Document)
├── specs.md                    (Technical Specifications)
├── tasks.md                    (Implementation Task Breakdown)
├── implementation.md           (Implementation Guide)
└── supporting-docs/
    ├── INDEX.md                (Document catalog)
    ├── INSIGHTS.md             (Extracted insights)
    └── agent-os-upgrade-workflow-design.md  (Original design)
```

---

## Requirements Traceability

All requirements are traceable from srd.md → specs.md → tasks.md:

- **FR-1 through FR-30:** Functional requirements
- **SR-1 through SR-6:** Safety requirements
- **NFR-P1 through NFR-P5:** Performance targets
- **NFR-R1 through NFR-R5:** Reliability targets
- **NFR-U1 through NFR-U5:** Usability targets
- **NFR-M1 through NFR-M5:** Maintainability targets
- **NFR-S1 through NFR-S5:** Security controls

Each requirement has:
- Implementation in specs.md (which component)
- Tasks in tasks.md (who does what)
- Code patterns in implementation.md (how to code it)

---

## Architecture Highlights

### Three-Tier Architecture

1. **Workflow Definition** (`.md` files)
   - Human and AI readable guidance
   - Phase objectives and commands
   - Validation gates

2. **Workflow Engine** (`workflow_engine.py`)
   - Orchestrates phase execution
   - Validates checkpoints
   - Manages state transitions

3. **State Manager** (`state_manager.py`)
   - Persists state to disk
   - Enables resume after restart
   - Atomic writes prevent corruption

### Component Interactions

```
User → AI Assistant → Workflow Engine → State Manager → Disk
                           ↓
                      Components:
                      - BackupManager
                      - ValidationModule
                      - DependencyInstaller
                      - ServerManager
                      - ReportGenerator
```

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| State corruption during restart | Low | High | Atomic writes, testing |
| Dependency install failures | Medium | High | Retry, rollback |
| Rollback failures | Low | Critical | Extensive testing |
| Performance targets not met | Low | Medium | Early profiling |

---

## Future Enhancements

### Version 1.1

- Delta upgrades (only changed files)
- Custom modification detection
- Parallel downloads during backup
- Optional git commit

### Version 2.0

- Auto-update schedule (cron)
- Canary deployments
- Multi-project batch upgrades
- Cloud backup integration

---

## Usage Example

```python
# Start upgrade workflow
result = start_workflow(
    workflow_type="praxis_os_upgrade_v1",
    target_file="mcp_server",
    options={
        "source_path": "/path/to/praxis-os",
        "dry_run": false,
        "auto_restart": true
    }
)

session_id = result["session_id"]

# AI executes phases 0-2...

# Phase 3: Server restarts

# Resume after restart
state = get_workflow_state(session_id)
# AI continues with phases 4-5...

# Result: Upgrade complete!
```

---

## FAQs

### Q: What happens if the upgrade fails?

A: The workflow automatically rolls back to the backup created in Phase 1. All files are restored and the server is restarted with the previous version.

### Q: Can I preview changes before upgrading?

A: Yes! Set `"dry_run": true` in the workflow options to see what will change without actually making modifications.

### Q: What if I have custom modifications?

A: The workflow uses `safe-upgrade.py` which detects conflicts. You'll be prompted to resolve any conflicts before proceeding.

### Q: How long does an upgrade take?

A: Typical upgrade: < 2 minutes. With conflicts: < 5 minutes.

### Q: Can I roll back manually?

A: Yes, see the troubleshooting guide in implementation.md for manual rollback procedures.

---

## Approval & Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| Specification Author | AI Assistant | 2025-10-08 | ✅ Complete |
| Technical Reviewer | TBD | TBD | ⏳ Pending |
| Approver | Josh (Human) | TBD | ⏳ Pending |

---

## Changelog

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-08 | Initial specification complete | AI Assistant |

---

## References

- **Meta-Framework Guide:** `meta-workflow/META_FRAMEWORK_SUMMARY.md`
- **Workflow Construction Standards:** `universal/standards/workflows/`
- **MCP Usage Guide:** `universal/usage/mcp-usage-guide.md`
- **Safe Upgrade Spec:** `.praxis-os/specs/2025-10-07-manifest-based-upgrade-system/`

---

**Status:** ✅ Specification Complete - Ready for Implementation

**Next Steps:**
1. Review and approve specification
2. Begin implementation (start with Task 1.1)
3. Follow test-driven development approach
4. Dogfood early and often

---

_For questions or clarifications, refer to the detailed documents linked above._

