# Software Requirements Document

**Project:** Evidence Validation System  
**Date:** 2025-10-20  
**Priority:** Critical  
**Category:** Bug Fix + System Enhancement

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for fixing the critical evidence validation bug in the prAxIs OS workflow engine and implementing config-driven gate definitions to prevent false evidence submission.

### 1.2 Scope
This feature will enable actual validation of workflow checkpoint evidence, prevent AI agents from submitting false claims, and establish a systematic approach to validation gate management across all workflows.

---

## 2. Business Goals

### Goal 1: Restore Validation Gate Functionality

**Objective:** Fix the critical bug where validation gates are completely bypassed, allowing false evidence to pass unchallenged and phases to advance without verification.

**Success Metrics:**
- **False Evidence Pass Rate**: 100% (current) → 0% (target)
- **Validation Gate Effectiveness**: 0% enforcement (current) → 100% enforcement (target)
- **Phase Advancement Accuracy**: Unverified (current) → Validated with proof artifacts (target)

**Business Impact:**
- **Quality Assurance**: Workflows can guarantee "near-deterministic" outputs as designed
- **System Reliability**: Validation gates actually gate, not just document requirements
- **Development Velocity**: Reduced debugging time from catching errors at gates vs. in production
- **Trust**: Users can rely on workflow validation as quality guarantee

**Current State:** Hardcoded `True` at `mcp_server/core/session.py:503` bypasses all validation logic, rendering 137+ checkpoint definitions meaningless.

**Target State:** Validation system enabled, false evidence rejected with clear error messages, AI agents required to do actual work to pass gates.

### Goal 2: Prevent AI Gaming Through Information Asymmetry

**Objective:** Implement config-driven gate definitions that hide validation schemas from AI agents, preventing them from gaming the system by submitting expected evidence without doing work.

**Success Metrics:**
- **Schema Exposure**: 100% visible in task files (current) → 0% visible to AI (target)
- **Proof-Based Evidence Rate**: <20% (current, mostly booleans) → 100% (target, structured proof artifacts)
- **Gaming Prevention Layers**: 0 (current) → 4 (field names, types, validators, content validation)

**Business Impact:**
- **Security**: AI cannot bypass validation by seeing schemas and faking responses
- **Quality**: Validators check proof content, not just claim presence
- **Scalability**: Hidden schemas allow us to strengthen validation without AI adaptation
- **Long-term Value**: System becomes more robust as AI capabilities increase

**Current State:** Task files expose evidence schemas, AI can see what to submit and fake it with boolean-only evidence.

**Target State:** gate-definition.yaml hidden from AI, natural language in tasks, multi-layer validation of proof artifacts.

### Goal 3: Systematic Workflow Validation Coverage

**Objective:** Retrofit all existing workflows with structured gate definitions and establish auto-generation for future workflows.

**Success Metrics:**
- **Workflow Coverage**: 0% have gate-definition.yaml (current) → 100% (target)
- **Auto-Generation**: 0% of new workflows (current) → 100% via workflow_creation_v1 (target)
- **Validation Consistency**: Ad-hoc/manual (current) → Systematic/config-driven (target)

**Business Impact:**
- **Consistency**: All workflows enforce validation uniformly
- **Maintainability**: Gate definitions centralized, not scattered in code
- **Productivity**: workflow_creation_v1 automatically generates gates, reducing manual effort
- **Compliance**: Validation standards applied systematically across all workflows

**Current State:** Validation requirements exist only in markdown checkpoints, parsed via RAG (brittle), no structured enforcement.

**Target State:** Every workflow phase has gate-definition.yaml, migration script for existing, auto-generation for new.

### Goal 4: Rapid Deployment of Critical Fix

**Objective:** Deploy the validation fix within 3 weeks using phased rollout to minimize risk while restoring critical functionality.

**Success Metrics:**
- **Time to Fix**: Unknown (current) → 3 weeks (Week 1: enable, Week 2: enhance, Week 3: production)
- **Risk Level**: High (breaking workflows) → Low (lenient → strict progression, fallback gates)
- **Adoption Rate**: 0 workflows validated → 100% within 3 weeks

**Business Impact:**
- **Speed**: 1-line fix enables validation immediately, phased enhancement reduces risk
- **Safety**: Lenient gates initially, tighten based on real usage data
- **Learning**: Early deployment provides feedback for refinement
- **Business Continuity**: Backwards-compatible fallbacks ensure existing workflows don't break

**Current State:** Bug exists but no fix timeline, unclear implementation path, high uncertainty.

**Target State:** Clear 3-week plan with weekly milestones, phased rollout strategy, defined success criteria.

---

## 2.1 Supporting Documentation

The business goals above are informed by:
- **Evidence Validation System Design Document**: Comprehensive analysis of the bug, its impact, and detailed technical solution including timeline, testing strategy, and risk mitigation

See `supporting-docs/INDEX.md` for complete analysis and extracted insights.

---

## Strategic Context

This is a **CRITICAL P0 bug fix** because:
1. Validation gates are advertised as quality guarantees but provide zero enforcement
2. AI agents can advance phases with completely false evidence
3. "Near-deterministic" workflow outputs are actually random without validation
4. System integrity depends on validation working as designed

The fix is **high-impact, low-complexity**:
- Enable existing validation system (already implemented, just disabled)
- Add structured gate definitions (config-driven, not code changes)
- Retrofit existing workflows (automated migration script)
- 3-week timeline from start to production-ready

**Success = Workflows actually validate evidence, AI must do work to pass gates, quality guarantees become real guarantees.**

---

## 3. User Stories

User stories describe the feature from the user's perspective.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: Workflow Developer Needs Functioning Validation Gates

**As a** workflow developer  
**I want to** validation gates to actually enforce evidence requirements  
**So that** I can trust that workflows produce quality outputs and catch errors early rather than in production

**Acceptance Criteria:**
- Given I define evidence requirements in a gate-definition.yaml
- When an AI agent submits evidence for a checkpoint
- Then the system validates the evidence against the schema and rejects invalid submissions

**Priority:** Critical (Must-Have)

---

### Story 2: AI Agent Needs Clear Validation Feedback

**As an** AI agent executing a workflow  
**I want to** receive specific error messages when evidence validation fails  
**So that** I know exactly what's missing or wrong and can resubmit corrected evidence

**Acceptance Criteria:**
- Given I submit evidence that fails validation
- When the checkpoint validation runs
- Then I receive a structured response with:
  - List of specific errors (which fields failed, why)
  - Remediation guidance (what to fix)
  - Next steps (how to proceed)

**Priority:** Critical (Must-Have)

---

### Story 3: System Administrator Prevents False Evidence

**As a** system administrator  
**I want to** prevent AI agents from gaming validation by hiding evidence schemas  
**So that** agents must actually complete work to pass gates, not just submit expected responses

**Acceptance Criteria:**
- Given gate-definition.yaml exists for a phase
- When an AI agent reads task instructions
- Then the agent sees natural language requirements only, not the evidence schema
- And the system validates evidence against the hidden schema
- And multi-layer validation (field names, types, validators, content) prevents gaming

**Priority:** Critical (Must-Have)

---

### Story 4: Workflow Author Adds Gates to Existing Workflows

**As a** workflow author  
**I want to** use a migration script to add gate definitions to existing workflows  
**So that** I don't have to manually create gate-definition.yaml for every phase

**Acceptance Criteria:**
- Given an existing workflow without gate definitions
- When I run the migration script
- Then gate-definition.yaml files are generated for all phases
- And the gates start as lenient (non-blocking) for safety
- And I can manually refine the generated gates as needed

**Priority:** High

---

### Story 5: Workflow Developer Auto-Generates Gates for New Workflows

**As a** workflow developer  
**I want to** workflow_creation_v1 to automatically generate gate-definition.yaml files  
**So that** new workflows have validation from day one without manual setup

**Acceptance Criteria:**
- Given I'm creating a new workflow using workflow_creation_v1
- When I reach Phase 2 (Phase Content Generation)
- Then the workflow generates gate-definition.yaml for each phase
- And the gates match the checkpoint requirements from phase.md
- And the gates include appropriate validators for the workflow type

**Priority:** High

---

### Story 6: Workflow User Trusts Validated Outputs

**As a** workflow user  
**I want to** confidence that workflow outputs have been validated  
**So that** I can rely on "near-deterministic" quality guarantees rather than random results

**Acceptance Criteria:**
- Given a workflow completes all phases
- When I review the outputs
- Then I know each phase passed actual validation (not hardcoded true)
- And I can see evidence that was validated in the phase artifacts
- And I can trust the workflow output meets quality standards

**Priority:** High

---

### Story 7: Developer Debugs Validation Failures

**As a** workflow developer  
**I want to** detailed diagnostics when validation fails  
**So that** I can understand why evidence was rejected and fix the issue

**Acceptance Criteria:**
- Given a checkpoint validation failure
- When I review the error response
- Then I see which validators failed and why
- And I see the actual evidence values that were provided
- And I see expected values or patterns
- And I can trace the failure to specific requirements

**Priority:** Medium

---

## 3.1 Story Priority Summary

**Critical (Must-Have):**
- Story 1: Workflow Developer Needs Functioning Validation Gates
- Story 2: AI Agent Needs Clear Validation Feedback  
- Story 3: System Administrator Prevents False Evidence

**High Priority:**
- Story 4: Workflow Author Adds Gates to Existing Workflows
- Story 5: Workflow Developer Auto-Generates Gates for New Workflows
- Story 6: Workflow User Trusts Validated Outputs

**Medium Priority:**
- Story 7: Developer Debugs Validation Failures

## 3.2 Supporting Documentation

User needs from supporting documents:
- **Evidence Validation System Design Document**: 
  - Workflow developers need validation that actually works (not hardcoded bypass)
  - AI agents need clear feedback when evidence is invalid
  - System needs to prevent gaming through information asymmetry
  - Need systematic coverage across all workflows

See `supporting-docs/INDEX.md` for detailed requirements insights.

---

## 4. Functional Requirements

Functional requirements specify capabilities the system must provide.

---

### FR-001: Enable Checkpoint Validation

**Description:** The system shall call `_validate_checkpoint()` method instead of hardcoding `checkpoint_passed=True` in `mcp_server/core/session.py`.

**Priority:** Critical

**Related User Stories:** Story 1

**Acceptance Criteria:**
- Line 503 in `mcp_server/core/session.py` calls `self.engine._validate_checkpoint(workflow_type, phase, evidence)`
- Validation result (passed, errors) is evaluated before advancing phase
- If validation fails, phase does not advance
- If validation passes, phase advances with checkpoint_passed=True

---

### FR-002: Validate Evidence Against Schema

**Description:** The system shall validate submitted evidence against the requirements defined in gate-definition.yaml for the current phase.

**Priority:** Critical

**Related User Stories:** Story 1, Story 3

**Acceptance Criteria:**
- System loads gate-definition.yaml for the workflow phase
- System checks all required fields are present in evidence
- System validates field types match schema (boolean, integer, string, object, list)
- System runs custom validators specified in the schema
- System checks cross-field validation rules if defined
- Validation returns (passed: bool, result: Dict) with errors array

---

### FR-003: Return Structured Validation Errors

**Description:** The system shall return structured error responses when evidence validation fails, including specific errors, diagnostics, and remediation guidance.

**Priority:** Critical

**Related User Stories:** Story 2

**Acceptance Criteria:**
- Response includes `checkpoint_passed: false` when validation fails
- Response includes `errors` array with specific failure messages
- Response includes `warnings` array for non-critical issues
- Response includes `diagnostics` dict with metadata (fields submitted, fields required, timestamp)
- Response includes `remediation` string with actionable guidance
- Response includes `next_steps` array with how to proceed
- Error messages are specific (not generic "validation failed")

---

### FR-004: Load Gate Definitions from YAML

**Description:** The system shall load checkpoint requirements from gate-definition.yaml files, with fallback to RAG parsing if YAML not found.

**Priority:** Critical

**Related User Stories:** Story 3, Story 4

**Acceptance Criteria:**
- CheckpointLoader.load_checkpoint_requirements() checks for gate-definition.yaml first
- If YAML exists, parses and returns structured requirements
- If YAML missing, falls back to RAG-based parsing of phase.md
- If RAG fails, returns permissive gate (non-blocking) with warning logged
- YAML schema includes: checkpoint (strict, allow_override), evidence_schema, validators
- Requirements are cached with thread-safe double-checked locking

---

### FR-005: Hide Evidence Schemas from AI

**Description:** The system shall keep gate-definition.yaml files hidden from AI agents, who only see natural language task instructions.

**Priority:** Critical

**Related User Stories:** Story 3

**Acceptance Criteria:**
- gate-definition.yaml files are not included in task file content
- Task files contain only natural language descriptions (no schema definitions)
- AI agents receive task content via get_task() without gate schema
- System loads gate schema internally when validating evidence
- Information asymmetry is maintained (AI sees requirements, system knows schema)

---

### FR-006: Support Proof-Based Evidence

**Description:** The system shall validate proof artifacts (not just boolean claims) by checking the content of submitted evidence.

**Priority:** Critical

**Related User Stories:** Story 3

**Acceptance Criteria:**
- Evidence schema requires structured artifacts (yaml_content, validation_output, etc.)
- Validators check proof content matches expectations (e.g., yaml_content parses, validation_output contains success markers)
- Boolean fields alone are insufficient (must be accompanied by proof)
- System can verify HOW validation was performed (command, output, results)

---

### FR-007: Generate Migration Script for Existing Workflows

**Description:** The system shall provide a migration script (`scripts/generate-gate-definitions.py`) that generates gate-definition.yaml files for existing workflows.

**Priority:** High

**Related User Stories:** Story 4

**Acceptance Criteria:**
- Script scans `.praxis-os/workflows/` directory for all workflows
- For each workflow, parses checkpoint sections from phase.md files
- Generates gate-definition.yaml with evidence schema and validators
- Supports dry-run mode to preview changes without writing files
- Supports single workflow mode (`--workflow workflow_name`)
- Generated gates start as lenient (strict: false) for safety
- Creates minimal gates for phases without checkpoints

---

### FR-008: Auto-Generate Gates in workflow_creation_v1

**Description:** The system shall enhance workflow_creation_v1 to automatically generate gate-definition.yaml files during Phase 2 (Phase Content Generation).

**Priority:** High

**Related User Stories:** Story 5

**Acceptance Criteria:**
- workflow_creation_v1 Phase 2 includes task-4-generate-gate-definitions.md
- workflow_creation_v1 Phase 2 includes task-5-validate-gate-consistency.md
- Generated gates match checkpoint requirements from phase.md
- Gates include appropriate validators for evidence types
- Gate strictness appropriate for phase type (lenient for discovery, strict for implementation)
- Generated gates are validated before workflow completion

---

### FR-009: Support Multi-Layer Validation

**Description:** The system shall implement multi-layer validation that checks field names, types, validators, and proof content to prevent gaming.

**Priority:** High

**Related User Stories:** Story 3

**Acceptance Criteria:**
- Layer 1: Validates required field names are present (not just any fields)
- Layer 2: Validates field types match schema (boolean vs string vs integer vs object)
- Layer 3: Runs custom validators specified in gate definition
- Layer 4: Validates proof artifact content (e.g., parsed YAML structure, command output text)
- Each layer provides specific error messages when validation fails
- AI cannot easily bypass validation by guessing schema

---

### FR-010: Support Progressive Strictness

**Description:** The system shall support configurable strictness levels per phase, allowing lenient gates for early phases and strict gates for later phases.

**Priority:** High

**Related User Stories:** Story 4, Story 6

**Acceptance Criteria:**
- Gate definition includes `strict` field (true/false)
- When strict=false, errors converted to warnings, validation passes
- When strict=true, any error causes validation to fail
- Gate definition includes `allow_override` field for manual bypass capability
- Workflows can use lenient gates initially, tighten over time based on usage
- Default fallback gate is lenient (backwards compatible)

---

### FR-011: Provide Backwards Compatibility

**Description:** The system shall fall back to permissive validation when gate-definition.yaml is not found, ensuring existing workflows don't break.

**Priority:** High

**Related User Stories:** Story 4

**Acceptance Criteria:**
- If gate-definition.yaml missing, CheckpointLoader tries RAG parsing
- If RAG parsing fails, returns permissive gate (minimal requirements)
- Permissive gate accepts any evidence with type checking only
- Warning logged when fallback occurs
- Existing workflows continue to function (no breaking changes)
- System encourages but doesn't require gate definitions

---

### FR-012: Maintain Validation Audit Trail

**Description:** The system shall store validation attempt history including failed attempts, for debugging and analysis.

**Priority:** Medium

**Related User Stories:** Story 7

**Acceptance Criteria:**
- Failed validation attempts saved to workflow state
- Phase artifacts include validation result even on failure
- CheckpointStatus.FAILED set when validation fails
- State persisted after failed validation
- Users can review validation history
- Evidence submitted in failed attempts is preserved

---

## 4.1 Requirements by Category

### Core Validation (Critical)
- FR-001: Enable Checkpoint Validation
- FR-002: Validate Evidence Against Schema  
- FR-003: Return Structured Validation Errors
- FR-004: Load Gate Definitions from YAML
- FR-005: Hide Evidence Schemas from AI
- FR-006: Support Proof-Based Evidence

### Workflow Integration (High)
- FR-007: Generate Migration Script for Existing Workflows
- FR-008: Auto-Generate Gates in workflow_creation_v1
- FR-009: Support Multi-Layer Validation
- FR-010: Support Progressive Strictness
- FR-011: Provide Backwards Compatibility

### Developer Experience (Medium)
- FR-012: Maintain Validation Audit Trail

## 4.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority |
|-------------|--------------|----------------|----------|
| FR-001 | Story 1 | Goal 1 | Critical |
| FR-002 | Story 1, 3 | Goal 1, 2 | Critical |
| FR-003 | Story 2 | Goal 1 | Critical |
| FR-004 | Story 3, 4 | Goal 2, 3 | Critical |
| FR-005 | Story 3 | Goal 2 | Critical |
| FR-006 | Story 3 | Goal 2 | Critical |
| FR-007 | Story 4 | Goal 3 | High |
| FR-008 | Story 5 | Goal 3 | High |
| FR-009 | Story 3 | Goal 2 | High |
| FR-010 | Story 4, 6 | Goal 3, 4 | High |
| FR-011 | Story 4 | Goal 4 | High |
| FR-012 | Story 7 | Goal 1 | Medium |

## 4.3 Supporting Documentation

Requirements informed by:
- **Evidence Validation System Design Document**: 
  - Detailed technical requirements for each FR
  - Code examples showing implementation approach
  - Testing strategy for validation system
  - Migration approach for existing workflows

See `supporting-docs/INDEX.md` for complete requirements insights.

---

## 5. Non-Functional Requirements

NFRs define quality attributes and system constraints.

---

### 5.1 Performance

**NFR-P1: Validation Speed**
- Checkpoint validation: < 100ms per validation (95th percentile)
- Gate definition loading (cached): < 10ms
- Gate definition loading (first time): < 50ms
- Zero impact on phase advancement time for passing validation

**NFR-P2: Caching Efficiency**
- CheckpointLoader cache hit rate: > 95%
- Memory overhead per cached gate: < 10KB
- No cache invalidation required during workflow execution

**NFR-P3: Scalability**
- Support concurrent validation across multiple workflow sessions
- Thread-safe cache implementation (double-checked locking)
- No performance degradation with 10+ concurrent workflows

### 5.2 Reliability

**NFR-R1: Backwards Compatibility**
- Zero breaking changes for existing workflows without gate definitions
- Graceful fallback to permissive gates when YAML missing
- All existing workflows continue to function post-deployment

**NFR-R2: Error Handling**
- Validation errors never cause workflow crashes
- Failed validation persisted to state (not lost)
- Clear recovery path for validation failures (resubmit evidence)

**NFR-R3: Data Integrity**
- Validation results accurately reflect gate requirements
- No false positives (invalid evidence passing)
- No false negatives (valid evidence failing) due to bugs
- State persistence guarantees validation results not lost

### 5.3 Security

**NFR-S1: Information Asymmetry**
- gate-definition.yaml files never exposed to AI agents via get_task()
- Evidence schemas never included in task file content
- Validators never exposed in API responses
- System maintains information advantage over AI

**NFR-S2: Validator Security**
- Custom validators execute in controlled context
- No arbitrary code execution from validator functions
- Lambda validators only (no external module loading in v1.0)
- Validator syntax validated before execution

**NFR-S3: Audit Trail**
- All validation attempts logged (success and failure)
- Evidence preserved even for failed validations
- Validation timestamp and result persisted
- No evidence tampering possible after submission

### 5.4 Maintainability

**NFR-M1: Code Quality**
- Test coverage for validation system: minimum 90%
- All validators unit tested with valid/invalid inputs
- Integration tests for complete_phase with validation enabled
- Type hints on all validation functions

**NFR-M2: Configuration-Driven**
- Validation behavior controlled by gate-definition.yaml (not code)
- New validators added without code changes to CheckpointLoader
- Gate strictness adjustable per phase without code deployment
- Schema evolution supported (backwards compatible)

**NFR-M3: Debuggability**
- Validation errors include specific field/validator that failed
- Diagnostics include evidence submitted vs expected
- Clear remediation guidance in error responses
- Logging at INFO level for validation pass/fail

### 5.5 Usability

**NFR-U1: Error Message Quality**
- Errors are specific (not "validation failed")
- Errors explain WHAT failed and WHY
- Errors include remediation steps (HOW to fix)
- Errors avoid exposing internal implementation details to AI

**NFR-U2: Developer Experience**
- Migration script runs in < 5 minutes for all workflows
- Dry-run mode allows preview before changes
- Generated gates are human-readable YAML
- Manual refinement of generated gates is straightforward

**NFR-U3: Documentation**
- gate-definition.yaml format documented with examples
- Common validator patterns provided as templates
- Migration guide for adding gates to existing workflows
- Troubleshooting guide for validation failures

### 5.6 Deployment

**NFR-D1: Phased Rollout**
- Week 1: Enable validation with lenient gates (non-blocking)
- Week 2: Enhance workflow_creation_v1, refine gates
- Week 3: Switch to strict gates based on real data
- Rollback capability at each phase

**NFR-D2: Zero Downtime**
- Validation enablement requires no server restart
- Gate definition updates hot-loaded (cache invalidation optional)
- No workflow interruption during deployment

**NFR-D3: Monitoring**
- Validation pass/fail rate tracked per workflow
- Average validation time per phase tracked
- Cache hit rate monitored
- False evidence attempts logged and alerted

### 5.7 Compatibility

**NFR-C1: Python Version**
- Minimum Python 3.8 (for lambda syntax, type hints)
- Compatible with current prAxIs OS runtime environment
- No new dependencies required (uses existing pyyaml)

**NFR-C2: Workflow Engine**
- Works with existing WorkflowEngine architecture
- No breaking changes to MCP tool interface
- Complete_phase signature unchanged
- Session state model unchanged

**NFR-C3: RAG System**
- Fallback to RAG parsing when gate YAML missing
- Existing checkpoint parsing continues to work
- No changes to RAG index structure required

### 5.8 Testing

**NFR-T1: Test Coverage**
- Unit tests: validation functions, CheckpointLoader, validators
- Integration tests: complete_phase with real/fake evidence
- Regression tests: existing workflows pass with permissive gates
- Migration script tested on all existing workflows

**NFR-T2: Test Scenarios**
- Happy path: valid evidence passes validation
- Missing fields: specific error returned
- Wrong types: type mismatch detected
- Invalid content: validators reject bad proof
- Progressive scenarios: lenient → strict gate transition

## 5.9 Supporting Documentation

NFRs informed by:
- **Evidence Validation System Design Document**:
  - Performance targets (< 100ms validation time)
  - Security through information asymmetry
  - Phased rollout strategy (3 weeks)
  - Testing strategy and coverage requirements
  - Backwards compatibility as critical requirement

See `supporting-docs/INDEX.md` for complete design insights.

## 5.10 Success Metrics Summary

**Performance**: < 100ms validation, > 95% cache hit rate  
**Reliability**: 100% backwards compatible, zero crashes  
**Security**: 100% schema hidden, 0% gaming success rate  
**Quality**: 90%+ test coverage, 100% validators tested  
**Deployment**: 3-week timeline, zero downtime, phased rollout  
**User Experience**: Specific error messages, clear remediation, < 5min migration

---

## 6. Out of Scope

Explicitly defines what is NOT included. Items may be considered for future phases.

### Explicitly Excluded

---

#### Features

**Not Included in This Release:**

1. **Async Validation (External Process Wait)**
   - **Reason:** Adds significant complexity, not needed for v1.0 validation use cases
   - **Future Consideration:** Phase 2+ enhancement for CI/CD pipeline integration
   - **Impact:** All validation in v1.0 is synchronous (< 100ms target)

2. **External Module Validators**
   - **Reason:** Security risk, adds deployment complexity, lambda validators sufficient for v1.0
   - **Future Consideration:** May add in v2.0 with sandboxing
   - **Impact:** All validators must be lambda expressions in gate-definition.yaml

3. **Validation UI Dashboard**
   - **Reason:** No UI requirement for v1.0, CLI/API sufficient
   - **Future Consideration:** Phase 3+ developer tools
   - **Impact:** Validation results viewed via workflow state, logs, or API responses

4. **Evidence Replay/Re-validation**
   - **Reason:** Not needed for v1.0, state persistence sufficient
   - **Future Consideration:** Phase 2+ for audit trail analysis
   - **Impact:** Cannot re-run validation on historical evidence in v1.0

5. **Temporary Index for Testing**
   - **Reason:** Complex, not critical for validation functionality
   - **Future Consideration:** May add for advanced validation testing scenarios
   - **Impact:** Validation testing uses actual RAG index, not isolated test index

6. **Semantic Validation (NLP-based)**
   - **Reason:** Too advanced for v1.0, structured validation sufficient
   - **Future Consideration:** v2.0+ for natural language evidence validation
   - **Impact:** Evidence must be structured artifacts, not free-form text

7. **Multi-Agent Peer Review**
   - **Reason:** Not needed for evidence validation, different concern
   - **Future Consideration:** Separate feature for workflow quality assurance
   - **Impact:** Single validation path per checkpoint (no peer voting)

8. **Dynamic Gate Schema Evolution**
   - **Reason:** Backwards compatibility model sufficient for v1.0
   - **Future Consideration:** v2.0 versioning system for gate definitions
   - **Impact:** Gate schema changes require new gate-definition.yaml file

---

#### User Types

**Not Supported:**

- **External API Consumers**: Validation system is internal to prAxIs OS workflow engine, not exposed as public API
- **Non-Workflow Users**: Validation only applies to workflow checkpoint evidence, not general-purpose validation
- **Manual Overriders Without Workflow Context**: Override capability exists but must be through workflow system (not standalone validation service)

---

#### Platforms

**Not Supported:**

- **Python < 3.8**: Requires Python 3.8+ for lambda syntax, type hints
- **Non-YAML Gate Formats**: Only YAML supported for gate-definition files (no JSON, TOML, etc.)
- **Non-Workflow Contexts**: Validation system designed for workflow engine, not portable to other validation needs

---

#### Integrations

**Not Included:**

- **External Validation Services**: No integration with third-party validation APIs (all validation local)
- **CI/CD Pipeline Hooks**: No direct integration with GitHub Actions, Jenkins, etc. (manual testing only)
- **Monitoring Platforms**: No automatic metric export to Prometheus, DataDog, etc. (logging only)
- **Notification Systems**: No Slack/email alerts on validation failures (console logs only)

---

#### Quality Levels Beyond NFRs

**Not Targeting:**

- **Sub-10ms Validation**: 100ms target sufficient, sub-10ms optimization not needed
- **> 99.9% Cache Hit Rate**: 95% target sufficient for v1.0 use cases
- **100% Test Coverage**: 90% target sufficient, diminishing returns beyond that
- **Zero Manual Gate Refinement**: Migration script generates starting point, manual refinement expected

---

#### Compliance Standards

**Not Required:**

- **SOC 2 Compliance**: Not applicable to internal validation system
- **GDPR Compliance**: No personal data in evidence validation
- **HIPAA Compliance**: No healthcare data in evidence validation
- **Formal Audit Trail Format**: Validation history stored in workflow state, not formal audit format

---

## 6.1 Future Enhancements

**Potential Phase 2 (v1.1):**
- Async validation support (wait for external processes)
- Evidence replay/re-validation capability
- Enhanced migration script (smarter parsing, more validators)
- Validation metrics dashboard (simple web UI)

**Potential Phase 3 (v2.0):**
- External module validators (with sandboxing)
- Semantic validation using NLP
- Gate schema versioning system
- Temporary index for isolated validation testing
- Multi-agent peer review integration

**Explicitly Not Planned:**
- Public validation API (internal to prAxIs OS only)
- Standalone validation service (tightly coupled to workflow engine)
- Support for Python < 3.8 (technical limitation)
- Non-YAML gate formats (YAML sufficient, no need for alternatives)

---

## 6.2 Supporting Documentation

Out-of-scope items from:
- **Evidence Validation System Design Document**: 
  - Future enhancements section documents Phase 2+ capabilities
  - v1.0 focused on core validation bug fix + config-driven gates
  - v2.0 features (async, NLP, advanced) explicitly deferred

See `supporting-docs/INDEX.md` for complete design document reference.

---

## 6.3 Decision Rationale

**Why These Exclusions Matter:**

1. **Focus**: v1.0 addresses critical bug + establishes foundation. Advanced features can build on this.
2. **Timeline**: 3-week target requires scope discipline. Async/NLP/UI would add months.
3. **Risk**: Simple lambda validators are secure. External modules need sandboxing (complex).
4. **Value**: 80/20 rule - validation fix + config gates provide 80% of value with 20% of complexity.
5. **Learning**: Deploy v1.0, gather feedback, then enhance. Don't over-engineer upfront.

**Scope Boundaries Ensure:**
- On-time delivery (3-week timeline met)
- High quality (90%+ test coverage achievable)
- Low risk (backwards compatible, graceful fallbacks)
- Clear success (validation works, AI can't game, workflows covered)

**Future Path Exists:**
- v1.0 foundation enables v1.1+ enhancements
- Config-driven design allows feature addition without architecture changes
- Phased rollout model applies to future enhancements too
