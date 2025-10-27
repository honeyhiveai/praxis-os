# Implementation Tasks

**Project:** Evidence Validation System  
**Date:** 2025-10-20  
**Status:** Draft - Pending Approval

---

## Time Estimates

- **Phase 1:** 8 hours (Enable core validation + checkpoint loader)
- **Phase 2:** 6 hours (Migration script + gate generation)
- **Phase 3:** 4 hours (workflow_creation_v1 enhancement)
- **Phase 4:** 10 hours (Testing + validation)
- **Phase 5:** 6 hours (Deployment + monitoring)
- **Total:** 34 hours (~1 week of focused development)

**Deployment Timeline:** 3 weeks (includes refinement and production readiness)
- Week 1: Phases 1-2 (enable + bootstrap)
- Week 2: Phase 3 (enhance + refine)
- Week 3: Phases 4-5 (test + deploy)

---

## Phase 1: Enable Core Validation

**Objective:** Enable the existing validation system and implement CheckpointLoader with gate-definition.yaml support. This is the critical path that unlocks all other functionality.

**Estimated Duration:** 8 hours

**Dependencies:** None (can start immediately)

**Deliverables:**
- Session.py fix (1-line change)
- CheckpointLoader with three-tier fallback
- Validator executor with safe globals
- Unit tests for core validation logic

### Phase 1 Tasks

#### Task 1.1: Enable Validation in Session Manager
**Estimated Time:** 30 minutes

**Description:** Replace hardcoded `checkpoint_passed = True` with actual validation call.

**Implementation:**
```python
# File: mcp_server/core/session.py
# Line 503: Change from
checkpoint_passed = True  # HARDCODED BYPASS

# To:
passed, result = self.engine._validate_checkpoint(
    workflow_type, phase, evidence
)
checkpoint_passed = passed
```

**Acceptance Criteria:**
- [ ] Line 503 updated
- [ ] Result dictionary properly returned
- [ ] Existing workflows still work (regression test)

**Testing:**
- Unit test: complete_phase with valid evidence (should pass)
- Unit test: complete_phase with invalid evidence (should fail)

---

#### Task 1.2: Implement CheckpointLoader Base
**Estimated Time:** 2 hours

**Description:** Create CheckpointLoader class with cache infrastructure.

**Implementation:**
```python
# File: mcp_server/config/loader.py

class CheckpointLoader:
    _cache: Dict[str, CheckpointRequirements] = {}
    _cache_lock: threading.Lock = threading.Lock()
    
    def load_checkpoint_requirements(
        self, workflow_type: str, phase: int
    ) -> CheckpointRequirements:
        cache_key = f"{workflow_type}:{phase}"
        
        # Double-checked locking
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        with self._cache_lock:
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            requirements = self._load_with_fallback(workflow_type, phase)
            self._cache[cache_key] = requirements
            return requirements
```

**Acceptance Criteria:**
- [ ] CheckpointLoader class created
- [ ] Cache infrastructure working
- [ ] Thread-safe access verified

**Testing:**
- Unit test: Cache hit/miss behavior
- Thread safety test: Concurrent access

---

#### Task 1.3: Implement YAML Gate Loading
**Estimated Time:** 1.5 hours

**Description:** Add YAML loading as first-tier fallback.

**Implementation:**
```python
def _load_from_yaml(
    self, workflow_type: str, phase: int
) -> Optional[CheckpointRequirements]:
    gate_path = Path(f".praxis-os/workflows/{workflow_type}/phases/{phase}/gate-definition.yaml")
    
    if not gate_path.exists():
        return None
    
    content = yaml.safe_load(gate_path.read_text())
    return self._parse_gate_content(content)
```

**Acceptance Criteria:**
- [ ] YAML files loaded and parsed
- [ ] Path traversal protection implemented
- [ ] Invalid YAML handled gracefully

**Testing:**
- Unit test: Load valid YAML
- Unit test: Load invalid YAML (should fail safely)
- Unit test: Missing YAML (should return None)
- Security test: Path traversal blocked

---

#### Task 1.4: Implement RAG Fallback
**Estimated Time:** 1 hour

**Description:** Add RAG parsing as second-tier fallback.

**Implementation:**
```python
def _load_from_rag(
    self, workflow_type: str, phase: int
) -> Optional[CheckpointRequirements]:
    # Use existing RAG engine to parse checkpoint
    checkpoint_data = self.rag_engine.parse_checkpoint(workflow_type, phase)
    
    if not checkpoint_data:
        return None
    
    return self._parse_checkpoint_data(checkpoint_data)
```

**Acceptance Criteria:**
- [ ] RAG engine integrated
- [ ] Checkpoint parsing working
- [ ] Failures handled gracefully

**Testing:**
- Unit test: RAG parsing success
- Unit test: RAG parsing failure (should return None)

---

#### Task 1.5: Implement Permissive Gate Fallback
**Estimated Time:** 30 minutes

**Description:** Create permissive gate as final fallback.

**Implementation:**
```python
def _get_permissive_gate(self) -> CheckpointRequirements:
    return CheckpointRequirements(
        evidence_schema={},  # Accept any fields
        validators={},
        cross_field_rules=[],
        strict=False,  # Warnings only
        allow_override=True,
        source="permissive"
    )
```

**Acceptance Criteria:**
- [ ] Permissive gate created
- [ ] Always succeeds
- [ ] Logs warning when used

**Testing:**
- Unit test: Permissive gate accepts any evidence

---

#### Task 1.6: Implement ValidatorExecutor
**Estimated Time:** 1.5 hours

**Description:** Create safe lambda validator executor.

**Implementation:**
```python
# File: mcp_server/validation/executor.py

class ValidatorExecutor:
    SAFE_GLOBALS = {
        'len': len, 'str': str, 'int': int, 'bool': bool,
        're': re, 'yaml': yaml, 'any': any, 'all': all, 'set': set
    }
    
    def execute_validator(
        self, validator_expr: str, value: Any, params: Dict
    ) -> Tuple[bool, Optional[str]]:
        try:
            validator_func = eval(validator_expr, self.SAFE_GLOBALS, {})
            passed = validator_func(value, **params)
            return (passed, None)
        except Exception as e:
            return (False, f"Validator failed: {e}")
```

**Acceptance Criteria:**
- [ ] Safe globals enforced
- [ ] Lambda expressions executed
- [ ] Exceptions handled gracefully

**Testing:**
- Unit test: Each safe validator
- Security test: Attempt dangerous operations (should fail)

---

#### Task 1.7: Implement WorkflowEngine Validation
**Estimated Time:** 1 hour

**Description:** Enhance _validate_checkpoint() to use CheckpointLoader.

**Implementation:**
```python
def _validate_checkpoint(
    self, workflow_type: str, phase: int, evidence: Dict
) -> Tuple[bool, Dict]:
    # Load requirements
    requirements = self.loader.load_checkpoint_requirements(workflow_type, phase)
    
    # Validate fields
    errors = []
    for field_name, schema in requirements.evidence_schema.items():
        if schema.required and field_name not in evidence:
            errors.append(f"Field '{field_name}' is required but missing")
    
    # Return result
    passed = len(errors) == 0 or not requirements.strict
    return (passed, self._build_result(passed, errors, requirements))
```

**Acceptance Criteria:**
- [ ] CheckpointLoader integrated
- [ ] Multi-layer validation working
- [ ] Structured errors returned

**Testing:**
- Integration test: Full validation flow

---

## Phase 2: Migration Script & Gate Generation

**Objective:** Create migration script to generate gate-definition.yaml files for all existing workflows, enabling systematic validation coverage.

**Estimated Duration:** 6 hours

**Dependencies:** Phase 1 complete (CheckpointLoader working)

**Deliverables:**
- Migration script (generate-gate-definitions.py)
- Generated gates for all workflows
- Validation that generated gates work

### Phase 2 Tasks

#### Task 2.1: Create Migration Script Structure
**Estimated Time:** 1 hour

**Description:** Set up migration script with CLI interface.

**Implementation:**
```python
# File: scripts/generate-gate-definitions.py

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--workflow', type=str)
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()
    
    # Scan workflows
    workflows = scan_workflows() if not args.workflow else [args.workflow]
    
    # Generate gates
    for workflow in workflows:
        generate_workflow_gates(workflow, args.dry_run, args.strict)
```

**Acceptance Criteria:**
- [ ] CLI interface working
- [ ] Dry-run mode implemented
- [ ] Single workflow mode working

**Testing:**
- Unit test: CLI argument parsing

---

#### Task 2.2: Implement Workflow Scanning
**Estimated Time:** 30 minutes

**Description:** Scan .praxis-os/workflows/ directory for all workflows.

**Implementation:**
```python
def scan_workflows(workflows_dir: str = ".praxis-os/workflows") -> List[str]:
    workflows = []
    for entry in Path(workflows_dir).iterdir():
        if entry.is_dir() and (entry / "phases").exists():
            workflows.append(entry.name)
    return sorted(workflows)
```

**Acceptance Criteria:**
- [ ] All workflows found
- [ ] Invalid directories skipped
- [ ] Results sorted alphabetically

**Testing:**
- Unit test: Scan with real workflows directory

---

#### Task 2.3: Implement Checkpoint Parsing
**Estimated Time:** 1.5 hours

**Description:** Parse checkpoint sections from phase.md files.

**Implementation:**
```python
def parse_checkpoint(phase_md_path: str) -> Dict[str, Any]:
    content = Path(phase_md_path).read_text()
    
    # Find checkpoint section
    checkpoint_match = re.search(
        r'## .*Checkpoint.*?\n(.*?)(?=\n##|\Z)',
        content, re.DOTALL | re.IGNORECASE
    )
    
    if not checkpoint_match:
        return {}
    
    # Extract evidence fields
    fields = extract_evidence_fields(checkpoint_match.group(1))
    return {"fields": fields}
```

**Acceptance Criteria:**
- [ ] Checkpoint sections parsed
- [ ] Evidence fields extracted
- [ ] Missing checkpoints handled

**Testing:**
- Unit test: Parse various checkpoint formats

---

#### Task 2.4: Implement Gate Generation
**Estimated Time:** 2 hours

**Description:** Generate gate-definition.yaml from parsed checkpoints.

**Implementation:**
```python
def generate_gate_yaml(checkpoint_data: Dict, strict: bool = False) -> str:
    fields = checkpoint_data.get("fields", {})
    
    gate = {
        "checkpoint": {
            "strict": strict,
            "allow_override": True
        },
        "evidence_schema": {},
        "validators": {
            "positive": "lambda x: x > 0"
        }
    }
    
    # Generate schema for each field
    for field_name, field_info in fields.items():
        gate["evidence_schema"][field_name] = {
            "type": infer_type(field_info),
            "required": True,
            "description": field_info.get("description", "")
        }
    
    return yaml.dump(gate, sort_keys=False)
```

**Acceptance Criteria:**
- [ ] YAML generated for all fields
- [ ] Validators inferred where possible
- [ ] Output is valid YAML

**Testing:**
- Unit test: Generate gate from checkpoint data
- Integration test: Generated YAML loads correctly

---

#### Task 2.5: Run Migration on All Workflows
**Estimated Time:** 1 hour

**Description:** Execute migration script on all workflows with dry-run, then actual generation.

**Implementation:**
```bash
# Dry-run first
python scripts/generate-gate-definitions.py --dry-run

# Review output, then generate
python scripts/generate-gate-definitions.py

# Verify
ls -la .praxis-os/workflows/*/phases/*/gate-definition.yaml | wc -l
```

**Acceptance Criteria:**
- [ ] All workflows processed
- [ ] Gates generated for all phases
- [ ] No errors during generation
- [ ] Generated files commit to git

**Testing:**
- Integration test: Load generated gates with CheckpointLoader

---

## Phase 3: workflow_creation_v1 Enhancement

**Objective:** Enhance workflow_creation_v1 to auto-generate gate-definition.yaml files for new workflows, ensuring future workflows have validation from day one.

**Estimated Duration:** 4 hours

**Dependencies:** Phase 2 complete (migration script working)

**Deliverables:**
- task-4-generate-gate-definitions.md
- task-5-validate-gate-consistency.md
- Updated workflow_creation_v1 Phase 2

### Phase 3 Tasks

#### Task 3.1: Create Task 4 - Generate Gates
**Estimated Time:** 1.5 hours

**Description:** Add task to generate gate-definition.yaml files.

**Implementation:**
Create `.praxis-os/workflows/workflow_creation_v1/phases/2/task-4-generate-gate-definitions.md`:

```markdown
# Task 4: Generate Gate Definitions

**Objective:** Generate gate-definition.yaml for each phase.

**Steps:**
1. For each phase in metadata.json
2. Parse checkpoint section from phase.md
3. Generate gate-definition.yaml with:
   - Evidence schema
   - Validators
   - Strictness (false for phases 0-1, true for 2+)

**Command:**
```bash
python scripts/generate-gate-definitions.py --workflow {workflow_name}
```
```

**Acceptance Criteria:**
- [ ] Task file created
- [ ] Instructions clear
- [ ] Examples provided

---

#### Task 3.2: Create Task 5 - Validate Consistency
**Estimated Time:** 1 hour

**Description:** Add task to validate gate consistency.

**Implementation:**
Create `.praxis-os/workflows/workflow_creation_v1/phases/2/task-5-validate-gate-consistency.md`:

```markdown
# Task 5: Validate Gate Consistency

**Objective:** Ensure gates match checkpoint requirements.

**Steps:**
1. Load each gate-definition.yaml
2. Compare to phase.md checkpoint section
3. Verify all requirements have schema fields
4. Report mismatches

**Command:**
```bash
python scripts/validate-workflow-metadata.py --workflow {workflow_name}
```
```

**Acceptance Criteria:**
- [ ] Task file created
- [ ] Validation steps documented

---

#### Task 3.3: Update Phase 2 Metadata
**Estimated Time:** 30 minutes

**Description:** Update workflow_creation_v1 Phase 2 to include new tasks.

**Implementation:**
```python
# File: .praxis-os/workflows/workflow_creation_v1/phases/2/phase.md
# Add to task list:
- task-4-generate-gate-definitions.md
- task-5-validate-gate-consistency.md
```

**Acceptance Criteria:**
- [ ] Phase.md updated
- [ ] Tasks in correct order
- [ ] Estimated times added

---

#### Task 3.4: Test Auto-Generation
**Estimated Time:** 1 hour

**Description:** Test that workflow_creation_v1 generates gates correctly.

**Implementation:**
```bash
# Create a test workflow
python -m mcp_server start_workflow workflow_type=workflow_creation_v1

# Execute through Phase 2
# Verify gate-definition.yaml files created
```

**Acceptance Criteria:**
- [ ] Test workflow created
- [ ] Gates auto-generated
- [ ] Gates validate correctly

**Testing:**
- Integration test: Create workflow, verify gates generated

---

## Phase 4: Testing & Validation

**Objective:** Comprehensive testing of the validation system including unit tests, integration tests, performance tests, and security tests.

**Estimated Duration:** 10 hours

**Dependencies:** Phases 1-3 complete

**Deliverables:**
- 90%+ test coverage
- All tests passing
- Performance benchmarks met
- Security tests passing

### Phase 4 Tasks

#### Task 4.1: Unit Tests - CheckpointLoader
**Estimated Time:** 2 hours

**Description:** Test all CheckpointLoader functionality.

**Implementation:**
```python
# File: tests/unit/test_checkpoint_loader.py

def test_load_from_yaml():
    """Test YAML loading."""
    pass

def test_load_from_rag():
    """Test RAG fallback."""
    pass

def test_permissive_gate():
    """Test permissive gate fallback."""
    pass

def test_cache_behavior():
    """Test cache hit/miss."""
    pass

def test_thread_safety():
    """Test concurrent access."""
    pass
```

**Acceptance Criteria:**
- [ ] All loader paths tested
- [ ] Cache behavior verified
- [ ] Thread safety confirmed

---

#### Task 4.2: Unit Tests - ValidatorExecutor
**Estimated Time:** 1.5 hours

**Description:** Test validator execution and security.

**Implementation:**
```python
# File: tests/unit/test_validator_executor.py

def test_safe_validators():
    """Test allowed validators."""
    pass

def test_dangerous_validators():
    """Test blocked validators."""
    pass

def test_validator_exceptions():
    """Test error handling."""
    pass
```

**Acceptance Criteria:**
- [ ] All validators tested
- [ ] Security verified
- [ ] Exceptions handled

---

#### Task 4.3: Integration Tests - Complete Phase Flow
**Estimated Time:** 2 hours

**Description:** Test complete validation flow end-to-end.

**Implementation:**
```python
# File: tests/integration/test_complete_phase_validation.py

def test_valid_evidence_passes():
    """Test happy path."""
    pass

def test_invalid_evidence_fails():
    """Test validation failure."""
    pass

def test_missing_gate_fallback():
    """Test fallback chain."""
    pass
```

**Acceptance Criteria:**
- [ ] Happy path works
- [ ] Validation failures work
- [ ] Fallbacks work

---

#### Task 4.4: Performance Tests
**Estimated Time:** 2 hours

**Description:** Verify performance targets met.

**Implementation:**
```python
# File: tests/unit/test_performance.py

def test_cached_validation_speed():
    """Verify < 10ms for cached."""
    pass

def test_uncached_validation_speed():
    """Verify < 50ms for uncached."""
    pass

def test_concurrent_performance():
    """Verify no degradation with 10 concurrent."""
    pass
```

**Acceptance Criteria:**
- [ ] < 10ms cached
- [ ] < 50ms uncached
- [ ] Concurrent works

---

#### Task 4.5: Security Tests
**Estimated Time:** 1.5 hours

**Description:** Verify security controls working.

**Implementation:**
```python
# File: tests/unit/test_security.py

def test_schema_hidden_from_ai():
    """Verify AI can't access schemas."""
    pass

def test_path_traversal_blocked():
    """Verify path traversal blocked."""
    pass

def test_validator_security():
    """Verify dangerous validators blocked."""
    pass
```

**Acceptance Criteria:**
- [ ] Schemas hidden
- [ ] Path traversal blocked
- [ ] Validators safe

---

#### Task 4.6: Regression Tests
**Estimated Time:** 1 hour

**Description:** Verify existing workflows still work.

**Implementation:**
```python
# File: tests/integration/test_backwards_compatibility.py

def test_workflows_without_gates():
    """Verify fallback works."""
    pass

def test_existing_workflow_state():
    """Verify state model unchanged."""
    pass
```

**Acceptance Criteria:**
- [ ] All existing workflows pass
- [ ] No breaking changes

---

## Phase 5: Deployment & Monitoring

**Objective:** Deploy validation system following 3-week phased rollout plan, establish monitoring, and document the system.

**Estimated Duration:** 6 hours

**Dependencies:** Phase 4 complete (all tests passing)

**Deliverables:**
- Deployed code changes
- Monitoring dashboard
- Documentation
- Rollback plan

### Phase 5 Tasks

#### Task 5.1: Week 1 Deployment (Lenient)
**Estimated Time:** 2 hours

**Description:** Deploy with lenient gates, monitor for issues.

**Implementation:**
```bash
# Deploy code changes
git checkout main
git merge feature/evidence-validation
git push origin main

# Run migration with lenient gates
python scripts/generate-gate-definitions.py

# Verify in production
curl -X POST /mcp/complete_phase -d '{"session_id": "test", "phase": 1, "evidence": {}}'
```

**Acceptance Criteria:**
- [ ] Code deployed
- [ ] Gates generated (strict=false)
- [ ] No breaking changes
- [ ] Validation running

**Monitoring:**
- Validation pass/fail rates
- Performance metrics
- Error logs

---

#### Task 5.2: Week 2 Refinement
**Estimated Time:** 2 hours

**Description:** Refine gates based on real usage data.

**Implementation:**
```bash
# Analyze validation logs
python scripts/analyze_validation_failures.py

# Update gates based on patterns
# Example: Add validators for common failures

# Deploy updated gates
git add .praxis-os/workflows/*/phases/*/gate-definition.yaml
git commit -m "Refine validation gates based on usage"
git push
```

**Acceptance Criteria:**
- [ ] Usage data analyzed
- [ ] Gates refined
- [ ] workflow_creation_v1 updated
- [ ] Improvements deployed

---

#### Task 5.3: Week 3 Production Ready (Strict)
**Estimated Time:** 1 hour

**Description:** Switch to strict mode for critical workflows.

**Implementation:**
```yaml
# Update gates for critical workflows
checkpoint:
  strict: true  # Enable strict mode
  allow_override: false
```

**Acceptance Criteria:**
- [ ] Critical workflows strict
- [ ] Non-critical remain lenient
- [ ] All tests still passing
- [ ] Production stable

---

#### Task 5.4: Setup Monitoring
**Estimated Time:** 30 minutes

**Description:** Configure monitoring and alerting.

**Implementation:**
```python
# Add performance metrics
logger.info("Checkpoint validation complete", extra={
    "duration_ms": duration_ms,
    "cache_hit": cache_hit,
    "workflow_type": workflow_type,
    "phase": phase,
    "passed": passed
})

# Configure alerts
# - p95 > 100ms: Warning
# - p95 > 200ms: Critical
# - Cache hit < 90%: Warning
```

**Acceptance Criteria:**
- [ ] Metrics logged
- [ ] Dashboard created
- [ ] Alerts configured

---

#### Task 5.5: Write Documentation
**Estimated Time:** 30 minutes

**Description:** Document the validation system for developers.

**Implementation:**
Create documentation:
- How to create gate-definition.yaml
- Common validator patterns
- Troubleshooting guide
- Migration guide

**Acceptance Criteria:**
- [ ] Developer guide written
- [ ] Examples provided
- [ ] Troubleshooting documented

---

#### Task 5.6: Rollback Plan Testing
**Estimated Time:** 30 minutes

**Description:** Test rollback procedure.

**Implementation:**
```bash
# Test rollback
# 1. Revert session.py change
# 2. Remove gate files
# 3. Verify existing behavior
```

**Acceptance Criteria:**
- [ ] Rollback tested
- [ ] < 5 minute rollback time
- [ ] No data loss

---

## Dependencies & Critical Path

**Critical Path:** Phase 1 → Phase 2 → Phase 4 → Phase 5
- Phase 1 must complete first (enables everything)
- Phase 2 required for full coverage
- Phase 3 can run in parallel with Phase 4
- Phase 5 requires Phase 4 complete

**Dependencies:**
```
Phase 1 (Enable)
    ↓
    ├→ Phase 2 (Migration)
    │       ↓
    └→ Phase 3 (workflow_creation_v1)
            ↓
        Phase 4 (Testing)
            ↓
        Phase 5 (Deployment)
```

---

## Risk Mitigation

**Risk 1: Breaking Existing Workflows**
- **Mitigation**: Three-tier fallback ensures backwards compatibility
- **Test**: Regression tests verify existing workflows work

**Risk 2: Performance Degradation**
- **Mitigation**: Caching strategy targets < 10ms cached validation
- **Test**: Performance tests verify < 100ms validation

**Risk 3: AI Discovery of Schemas**
- **Mitigation**: Information asymmetry + proof-based evidence
- **Test**: Security tests verify schemas hidden

**Risk 4: Deployment Issues**
- **Mitigation**: Phased 3-week rollout with lenient → strict progression
- **Test**: Rollback plan tested, < 5 minute rollback time

---

## Success Criteria

**Phase 1 Success:**
- [ ] Validation enabled (session.py fixed)
- [ ] CheckpointLoader working with all three tiers
- [ ] Unit tests passing (> 80% coverage)

**Phase 2 Success:**
- [ ] Migration script working
- [ ] All workflows have gate-definition.yaml
- [ ] Generated gates load correctly

**Phase 3 Success:**
- [ ] workflow_creation_v1 enhanced
- [ ] New workflows auto-generate gates
- [ ] Gates validated for consistency

**Phase 4 Success:**
- [ ] > 90% test coverage
- [ ] All tests passing
- [ ] Performance targets met (< 100ms)
- [ ] Security controls verified

**Phase 5 Success:**
- [ ] Code deployed to production
- [ ] Monitoring active
- [ ] Documentation complete
- [ ] Zero breaking changes

**Overall Success:**
- [ ] Validation gates actually enforce requirements
- [ ] AI agents cannot game validation
- [ ] 100% workflow coverage with gates
- [ ] < 100ms validation time
- [ ] Backwards compatible (existing workflows work)
