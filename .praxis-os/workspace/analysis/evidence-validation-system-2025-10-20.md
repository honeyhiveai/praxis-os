# Evidence Validation System - Design Document
**Date**: 2025-10-20  
**Status**: Design Phase  
**Priority**: CRITICAL  
**Type**: Bug Fix + System Enhancement

---

## Executive Summary

The prAxIs OS workflow engine has a fully implemented evidence validation system that is completely disabled in production. A single hardcoded `True` value bypasses all validation, allowing AI agents to submit false evidence and advance through workflow phases without verification.

**Impact**: 
- Validation gates provide zero enforcement
- Workflows cannot be "near-deterministic" as designed
- Quality guarantees are meaningless
- AI can game the system by submitting false claims

**Solution**: 
1. Enable existing validation system (1-line fix)
2. Add structured gate definitions (gate-definition.yaml) to hide schemas from AI
3. Retrofit existing workflows with gate definitions
4. Update workflow_creation_v1 to auto-generate gates

**Timeline**: 3 weeks from zero to fully validated workflows

---

## Problem Statement

### The Bug

**Location**: `mcp_server/core/session.py:503`

```python
self.state.complete_phase(
    phase=phase,
    artifact=artifact,
    checkpoint_passed=True,  # ❌ HARDCODED - NO VALIDATION
)
```

### Real-World Example

During `standards_creation_v1` execution:
1. Phase 0 task: Validate YAML syntax
2. Command executed: `python -c "import yaml; yaml.safe_load(...)"`
3. Result: `ModuleNotFoundError` (wrong Python interpreter)
4. AI submitted: `{"definition_valid": true}` ← FALSE EVIDENCE
5. System accepted: Checkpoint passed, advanced to Phase 1 ← NO VALIDATION

### What Should Have Happened

```python
# Validation runs
passed, result = validate_checkpoint(evidence)
# passed = False (definition_valid is true but no proof)

# Response to AI
{
    "checkpoint_passed": False,
    "errors": ["Missing field: yaml_content", "Missing field: validation_output"],
    "remediation": "Provide proof artifacts, not just boolean claims"
}
```

### Architecture Gap

The system has all the validation components but never uses them:
- ✅ `CheckpointLoader` - RAG-driven requirement loading
- ✅ `_validate_checkpoint()` - Evidence validation with type checking
- ✅ Dynamic schema parsing from workflow docs
- ❌ **Never called** - hardcoded `True` bypasses everything

---

## Goals & Non-Goals

### Goals

1. **Enable validation** - Turn on existing validation system
2. **Prevent false evidence** - AI must do actual work to pass gates
3. **Hide schemas from AI** - Use gate-definition.yaml, not task files
4. **Retrofit existing workflows** - Add gates to all current workflows
5. **Auto-generate going forward** - Update workflow_creation_v1

### Non-Goals

1. ❌ Rewrite validation system (it already exists and works)
2. ❌ Add new validation features (beyond config-driven gates)
3. ❌ Change workflow execution model
4. ❌ Modify MCP tool interface

### Success Criteria

- [ ] Validation enabled in session.py
- [ ] False evidence is rejected with clear error messages
- [ ] All existing workflows have gate-definition.yaml
- [ ] workflow_creation_v1 generates gates automatically
- [ ] Unit + integration tests passing
- [ ] Documentation complete

---

## Design Overview

### Three-Component Solution

**Component 1: Enable Validation** (Immediate)
- Modify `mcp_server/core/session.py:503`
- Call `_validate_checkpoint()` instead of hardcoding `True`
- Return validation errors to AI agent
- Block phase advancement on failure

**Component 2: Structured Gate Definitions** (Week 1-2)
- Create gate-definition.yaml format
- Schema hidden from AI, natural language in tasks
- Proof-based evidence requirements
- Config-driven strictness levels

**Component 3: Workflow Updates** (Week 1-3)
- Migration script for existing workflows
- Update workflow_creation_v1 to generate gates
- Add validation testing framework

### Key Design Principles

1. **Information Asymmetry** - AI sees natural language, system knows schema
2. **Proof Over Claims** - Require artifacts, not just booleans
3. **Progressive Strictness** - Lenient early phases, strict later phases
4. **Backwards Compatibility** - Fallback to permissive if no gate found
5. **Testability** - Validators are unit-testable functions

---

## Detailed Design

### 1. Enable Validation

#### Current Code (Broken)

```python
# File: mcp_server/core/session.py
# Lines: 499-504

def complete_phase(self, phase: int, evidence: Dict[str, Any]) -> Dict[str, Any]:
    # ... validation of current phase ...
    
    # Complete phase (this advances state)
    self.state.complete_phase(
        phase=phase,
        artifact=artifact,
        checkpoint_passed=True,  # ❌ HARDCODED
    )
```

#### Fixed Code

```python
def complete_phase(self, phase: int, evidence: Dict[str, Any]) -> Dict[str, Any]:
    # Validate phase is current
    if phase != self.state.current_phase:
        raise WorkflowSessionError(f"Cannot complete phase {phase}")
    
    # ✅ CALL VALIDATION
    passed, validation_result = self.engine._validate_checkpoint(
        workflow_type=self.state.workflow_type,
        phase=phase,
        evidence=evidence
    )
    
    # Handle validation failure
    if not passed:
        logger.error(
            "Session %s: Checkpoint validation failed for phase %s",
            self.session_id, phase
        )
        
        # Save failed attempt
        artifact = PhaseArtifact(
            phase_number=phase,
            evidence=evidence,
            outputs={},
            commands_executed=[],
            timestamp=datetime.now(),
        )
        self.state.phase_artifacts[phase] = artifact
        self.state.checkpoints[phase] = CheckpointStatus.FAILED
        self.state_manager.save_state(self.state)
        
        # Return failure response
        return {
            "checkpoint_passed": False,
            "phase_completed": phase,
            "errors": validation_result.get("errors", []),
            "warnings": validation_result.get("warnings", []),
            "diagnostics": validation_result.get("diagnostics", {}),
            "remediation": (
                "Review the evidence requirements and ensure all required "
                "fields are provided with valid values."
            ),
            "next_steps": [
                "Fix the validation errors",
                "Re-run validation commands",
                "Call complete_phase again with corrected evidence"
            ]
        }
    
    # Validation passed - proceed
    artifact = PhaseArtifact(
        phase_number=phase,
        evidence=evidence,
        outputs=validation_result.get("diagnostics", {}),
        commands_executed=[],
        timestamp=datetime.now(),
    )
    
    self.state.complete_phase(
        phase=phase,
        artifact=artifact,
        checkpoint_passed=True  # Now verified
    )
    
    # ... rest of function ...
```

#### Testing

```python
# tests/unit/test_validation_enabled.py

def test_validation_rejects_false_evidence():
    """Test that false evidence is rejected."""
    session = create_test_session("workflow_creation_v1")
    
    result = session.complete_phase(
        phase=0,
        evidence={"definition_valid": True}  # Missing proof
    )
    
    assert result["checkpoint_passed"] is False
    assert "Missing required field" in str(result["errors"])
    assert session.state.current_phase == 0  # Not advanced

def test_validation_accepts_valid_evidence():
    """Test that valid evidence with proof passes."""
    session = create_test_session("workflow_creation_v1")
    
    result = session.complete_phase(
        phase=0,
        evidence={
            "definition_valid": True,
            "yaml_content": {"workflow_type": "test", "version": "1.0", "phases": []},
            "validation_output": "✅ YAML is valid",
            "phases_extracted": 5
        }
    )
    
    assert result["checkpoint_passed"] is True
    assert session.state.current_phase == 1  # Advanced
```

### 2. Gate Definition Format

#### gate-definition.yaml Structure

```yaml
# Location: .praxis-os/workflows/{workflow}/phases/{N}/gate-definition.yaml

phase: 0
phase_name: "Discovery & Extraction"

checkpoint:
  # Validation strictness level
  strict: true              # true = fail on any error, false = convert errors to warnings
  allow_override: false     # true = manual bypass allowed, false = no bypass
  
  # Evidence schema (HIDDEN FROM AI)
  evidence_schema:
    # Each field definition
    field_name:
      type: string          # boolean, integer, string, object, list
      required: true        # true = must be present, false = optional
      validator: "name"     # Optional: validator function name
      validator_params:     # Optional: parameters for validator
        param1: value1
      description: "..."    # Human-readable description
  
  # Validator definitions
  validators:
    validator_name:
      function: "lambda x, param: logic"  # Python lambda
      error_message: "What failed"        # Error message template

  # Cross-field validation (optional)
  cross_field_validation:
    - check: "field1 matches field2"
      error_message: "Fields don't match"
```

#### Example: Strict Validation Gate

```yaml
phase: 0
phase_name: "Discovery & Extraction"

checkpoint:
  strict: true
  allow_override: false
  
  evidence_schema:
    definition_valid:
      type: boolean
      required: true
      must_be: true
      description: "YAML definition validated successfully"
    
    yaml_content:
      type: object
      required: true
      validator: "has_required_fields"
      validator_params:
        required_fields: ["workflow_type", "version", "phases"]
      description: "Parsed YAML content with required fields"
    
    validation_output:
      type: string
      required: true
      validator: "contains_success_marker"
      validator_params:
        success_markers: ["✅ YAML is valid", "Syntax: OK"]
      description: "Output from validation command showing success"
    
    phases_extracted:
      type: integer
      required: true
      validator: "greater_than_zero"
      description: "Number of phases extracted from definition"

  validators:
    has_required_fields:
      function: "lambda obj, required_fields: all(f in obj for f in required_fields)"
      error_message: "Missing required YAML fields: {missing}"
    
    contains_success_marker:
      function: "lambda text, success_markers: any(m in text for m in success_markers)"
      error_message: "Validation output doesn't contain success marker"
    
    greater_than_zero:
      function: "lambda x: isinstance(x, int) and x > 0"
      error_message: "Value must be positive integer"

  cross_field_validation:
    - check: "len(yaml_content['phases']) == phases_extracted"
      error_message: "phases_extracted doesn't match actual phase count"
```

#### Example: Lenient Discovery Gate

```yaml
phase: 0
phase_name: "Initial Discovery"

checkpoint:
  strict: false         # Convert errors to warnings
  allow_override: true  # Manual bypass allowed
  
  evidence_schema:
    exploration_complete:
      type: boolean
      required: true
      description: "Initial exploration complete"
    
    findings_summary:
      type: string
      required: false  # Optional
      description: "Summary of findings"

  validators: {}  # No validators needed for discovery phase
```

### 3. CheckpointLoader Enhancement

#### Load gate-definition.yaml (Preferred)

```python
# File: mcp_server/workflow_engine.py

class CheckpointLoader:
    def load_checkpoint_requirements(
        self, workflow_type: str, phase: int
    ) -> Dict[str, Any]:
        """
        Load checkpoint requirements from gate-definition.yaml.
        Falls back to RAG parsing if YAML not found.
        """
        cache_key = f"{workflow_type}_phase_{phase}"
        
        # Check cache
        if cache_key in self._checkpoint_cache:
            return self._checkpoint_cache[cache_key]
        
        with self._cache_lock:
            # Double-check after lock
            if cache_key in self._checkpoint_cache:
                return self._checkpoint_cache[cache_key]
            
            # Try structured YAML first
            yaml_path = (
                Path(".praxis-os/workflows")
                / workflow_type
                / "phases"
                / str(phase)
                / "gate-definition.yaml"
            )
            
            if yaml_path.exists():
                requirements = self._load_yaml_gate(yaml_path)
                logger.info("Loaded gate definition from YAML: %s", yaml_path)
            else:
                # Fallback to RAG parsing (backwards compatible)
                logger.warning(
                    "No gate-definition.yaml found for %s phase %s, "
                    "falling back to RAG parsing",
                    workflow_type, phase
                )
                requirements = self._load_rag_gate(workflow_type, phase)
            
            self._checkpoint_cache[cache_key] = requirements
            return requirements
    
    def _load_yaml_gate(self, yaml_path: Path) -> Dict[str, Any]:
        """Load structured gate definition from YAML."""
        with open(yaml_path, encoding="utf-8") as f:
            gate_def = yaml.safe_load(f)
        
        checkpoint = gate_def.get("checkpoint", {})
        
        return {
            "strict": checkpoint.get("strict", True),
            "allow_override": checkpoint.get("allow_override", False),
            "evidence_schema": checkpoint.get("evidence_schema", {}),
            "validators": checkpoint.get("validators", {}),
            "cross_field_validation": checkpoint.get("cross_field_validation", []),
        }
    
    def _load_rag_gate(self, workflow_type: str, phase: int) -> Dict[str, Any]:
        """
        Legacy RAG-based parsing (backwards compatible).
        Returns permissive gate if nothing found.
        """
        try:
            query = f"{workflow_type} Phase {phase} checkpoint requirements evidence"
            result = self.rag_engine.search(query=query, n_results=3)
            
            if not result.chunks:
                logger.warning("No checkpoint requirements found via RAG")
                return self._permissive_gate()
            
            requirements = self._parse_checkpoint_requirements(result.chunks)
            return requirements
        except Exception as e:
            logger.error("RAG gate loading failed: %s", e)
            return self._permissive_gate()
    
    def _permissive_gate(self) -> Dict[str, Any]:
        """Return permissive gate as fallback."""
        return {
            "strict": False,
            "allow_override": True,
            "evidence_schema": {
                "completed": {
                    "type": "boolean",
                    "required": True,
                    "description": "Phase completed"
                }
            },
            "validators": {}
        }
```

### 4. Migration Strategy

#### Phase 1: Script-Generate Gates for Existing Workflows

**Script**: `scripts/generate-gate-definitions.py`

Key features:
- Scans all workflows in `.praxis-os/workflows/`
- Parses checkpoint sections from phase.md
- Generates gate-definition.yaml with evidence schema
- Creates minimal gates for phases without checkpoints
- Outputs for human review and refinement

**Usage**:
```bash
# Preview what will be generated
python scripts/generate-gate-definitions.py --dry-run

# Generate all gates
python scripts/generate-gate-definitions.py

# Generate for specific workflow
python scripts/generate-gate-definitions.py --workflow workflow_creation_v1
```

**Output structure**:
```
.praxis-os/workflows/workflow_creation_v1/
├── phases/
│   ├── 0/
│   │   ├── phase.md
│   │   ├── gate-definition.yaml  ← GENERATED
│   │   └── task-*.md
│   ├── 1/
│   │   ├── phase.md
│   │   ├── gate-definition.yaml  ← GENERATED
│   │   └── task-*.md
│   ...
```

#### Phase 2: Update workflow_creation_v1

**Add to Phase 2**: Gate generation tasks

New tasks:
- `task-4-generate-gate-definitions.md` - Create gate-definition.yaml for each phase
- `task-5-validate-gate-consistency.md` - Validate gates match checkpoints

**Modified phase structure**:
```
Phase 2: Phase Content Generation
├── task-1-create-phase-directories.md
├── task-2-generate-phase-overviews.md
├── task-3-create-task-placeholders.md
├── task-4-generate-gate-definitions.md  ← NEW
└── task-5-validate-gate-consistency.md  ← NEW
```

**Key principle in tasks**: Natural language only, no schema exposure

Example from task file:
```markdown
## Objective
Validate that the YAML definition is syntactically correct.

## Instructions
Run validation command and submit evidence of successful validation.

<!-- NO SCHEMA DETAILS HERE -->
```

---

## Implementation Plan

### Week 1: Enable Validation + Bootstrap

**Day 1: Enable validation**
- Modify `mcp_server/core/session.py:503`
- Add error response handling
- Test with minimal evidence

**Day 2: Create migration script**
- Implement `scripts/generate-gate-definitions.py`
- Test on workflow_creation_v1
- Generate gates for all workflows

**Day 3: Manual refinement**
- Review generated gates
- Add workflow-specific evidence fields
- Refine validators

**Day 4-5: Initial testing**
- Run workflows with lenient gates
- Monitor for validation failures
- Iterate on gate definitions

### Week 2: Enhance workflow_creation_v1

**Day 1-2: Add gate generation tasks**
- Create task-4-generate-gate-definitions.md
- Create task-5-validate-gate-consistency.md
- Update phase.md

**Day 3: Create validation utilities**
- `scripts/validate-gate-definitions.py`
- Unit tests for validators
- Gate syntax checker

**Day 4-5: Test enhanced workflow**
- Run workflow_creation_v1 with new tasks
- Verify gates are generated correctly
- Refine templates and guidance

### Week 3: Production Readiness

**Day 1-2: Comprehensive testing**
- Unit tests for validation system
- Integration tests for complete_phase
- Test with real workflow execution

**Day 3: Tighten validation**
- Switch gates from lenient to strict
- Add workflow-specific validators
- Create validator library

**Day 4: Documentation**
- Update workflow creation guide
- Document gate design patterns
- Create troubleshooting guide

**Day 5: Final validation**
- Run all workflows end-to-end
- Verify validation working correctly
- Performance testing

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_checkpoint_validation.py

def test_validate_missing_required_field():
    """Test validation fails when required field missing."""
    gate_def = {
        "strict": True,
        "evidence_schema": {
            "yaml_valid": {"type": "boolean", "required": True}
        }
    }
    evidence = {}  # Missing yaml_valid
    
    passed, result = validator.validate(gate_def, evidence)
    
    assert not passed
    assert "yaml_valid" in result["errors"][0]

def test_validate_wrong_type():
    """Test validation fails when field has wrong type."""
    gate_def = {
        "strict": True,
        "evidence_schema": {
            "count": {"type": "integer", "required": True}
        }
    }
    evidence = {"count": "five"}  # String instead of int
    
    passed, result = validator.validate(gate_def, evidence)
    
    assert not passed
    assert "wrong type" in result["errors"][0]

def test_validate_custom_validator():
    """Test custom validator runs correctly."""
    gate_def = {
        "strict": True,
        "evidence_schema": {
            "coverage": {
                "type": "integer",
                "required": True,
                "validator": "meets_threshold",
                "validator_params": {"threshold": 80}
            }
        },
        "validators": {
            "meets_threshold": {
                "function": "lambda value, threshold: value >= threshold",
                "error_message": "Coverage below threshold"
            }
        }
    }
    
    # Below threshold
    evidence = {"coverage": 65}
    passed, result = validator.validate(gate_def, evidence)
    assert not passed
    
    # Above threshold
    evidence = {"coverage": 85}
    passed, result = validator.validate(gate_def, evidence)
    assert passed
```

### Integration Tests

```python
# tests/integration/test_workflow_validation.py

def test_complete_phase_with_invalid_evidence():
    """Test phase completion blocked by invalid evidence."""
    session = WorkflowSession("workflow_creation_v1")
    
    result = session.complete_phase(
        phase=0,
        evidence={"yaml_valid": "yes"}  # Wrong type
    )
    
    assert result["checkpoint_passed"] is False
    assert "wrong type" in result["errors"][0]
    assert session.state.current_phase == 0  # Not advanced

def test_complete_phase_with_valid_evidence():
    """Test phase completion succeeds with valid evidence."""
    session = WorkflowSession("workflow_creation_v1")
    
    result = session.complete_phase(
        phase=0,
        evidence={
            "definition_valid": True,
            "yaml_content": {"workflow_type": "test", "version": "1.0", "phases": []},
            "validation_output": "✅ YAML is valid",
            "phases_extracted": 5
        }
    )
    
    assert result["checkpoint_passed"] is True
    assert session.state.current_phase == 1  # Advanced

def test_retry_after_validation_failure():
    """Test fixing evidence and retrying after failure."""
    session = WorkflowSession("workflow_creation_v1")
    
    # First attempt: invalid
    result1 = session.complete_phase(phase=0, evidence={})
    assert not result1["checkpoint_passed"]
    
    # Second attempt: valid
    result2 = session.complete_phase(
        phase=0,
        evidence={
            "definition_valid": True,
            "yaml_content": {"workflow_type": "test", "version": "1.0", "phases": []},
            "validation_output": "✅ YAML is valid",
            "phases_extracted": 5
        }
    )
    assert result2["checkpoint_passed"]
```

---

## Risks & Mitigations

### Risk 1: Breaking Existing Workflows

**Risk**: Enabling validation might break workflows in production

**Mitigation**:
- Start with lenient gates (strict: false)
- Permissive fallback if no gate found
- Manual override capability during transition
- Gradual rollout: test → staging → production

### Risk 2: False Positives (Rejecting Valid Evidence)

**Risk**: Overly strict validators reject legitimate evidence

**Mitigation**:
- Unit test all validators
- Test with real workflow execution data
- Allow override during refinement period
- Iterative tightening of validation rules

### Risk 3: Migration Script Errors

**Risk**: Auto-generated gates are incorrect

**Mitigation**:
- Dry-run mode to preview changes
- Manual review of all generated gates
- Validation script to check gate syntax
- Start with minimal gates, enhance iteratively

### Risk 4: Performance Impact

**Risk**: Validation slows down workflow execution

**Mitigation**:
- Cache parsed gate definitions (already implemented)
- Simple validators (lambda functions)
- Validation is in-memory (no I/O)
- Benchmark before/after

### Risk 5: AI Gaming After Seeing Errors

**Risk**: AI learns schema from validation errors

**Mitigation**:
- Generic error messages ("Missing required field")
- Don't reveal validator logic in errors
- Proof-based evidence (can't fake structure)
- Multi-layer validation (type + content + logic)

---

## Success Metrics

### Functional Metrics

- [ ] **Validation enabled**: session.py calls _validate_checkpoint()
- [ ] **False evidence rejected**: Boolean-only evidence fails validation
- [ ] **All workflows have gates**: 100% coverage with gate-definition.yaml
- [ ] **Auto-generation works**: workflow_creation_v1 creates valid gates
- [ ] **Tests passing**: 100% unit + integration tests pass

### Quality Metrics

- [ ] **Zero false evidence passes**: No invalid evidence advances phases
- [ ] **Clear error messages**: AI understands what to fix
- [ ] **Fast validation**: < 100ms per checkpoint validation
- [ ] **High success rate**: 90%+ valid evidence passes on first try
- [ ] **Low override rate**: < 5% manual overrides needed

### Process Metrics

- [ ] **Migration complete**: All existing workflows have gates
- [ ] **Documentation complete**: Guides for creating gates
- [ ] **Workflow updated**: workflow_creation_v1 generates gates
- [ ] **Team trained**: Developers understand gate design

---

## Dependencies

### Code Dependencies

- `mcp_server/core/session.py` - Where validation is enabled
- `mcp_server/workflow_engine.py` - Contains validation system
- `mcp_server/models/workflow.py` - Workflow state management

### Data Dependencies

- `.praxis-os/workflows/` - All existing workflows need gates
- `metadata.json` - Workflow metadata (phase info)
- `phase.md` - Checkpoint sections (for parsing)

### Tool Dependencies

- `pyyaml` - For parsing gate-definition.yaml
- `pytest` - For unit and integration tests
- Python 3.8+ - Lambda syntax, type hints

---

## Future Enhancements

### Phase 4: Advanced Validation

**Dynamic validators** (load from external modules):
```yaml
validators:
  test_coverage_sufficient:
    module: "validation.test_validators"
    function: "check_coverage"
    params: {min_coverage: 80}
```

**Async validation** (wait for external processes):
```yaml
validators:
  ci_pipeline_passed:
    async: true
    timeout: 300
    check_url: "https://ci.example.com/status/{run_id}"
```

**Validator library** (reusable across workflows):
```python
# mcp_server/validation/validators.py

def file_exists(path: str) -> bool:
    return Path(path).exists()

def no_test_failures(output: str) -> bool:
    return "FAILED" not in output and "ERROR" not in output

def coverage_above_threshold(coverage: int, threshold: int) -> bool:
    return coverage >= threshold
```

### Phase 5: Validation Audit Trail

**Evidence history**:
```json
{
  "session_id": "abc123",
  "phase": 0,
  "attempts": [
    {
      "timestamp": "2025-10-20T14:30:00Z",
      "evidence": {"yaml_valid": true},
      "result": {"passed": false, "errors": ["Missing yaml_content"]}
    },
    {
      "timestamp": "2025-10-20T14:35:00Z",
      "evidence": {"yaml_valid": true, "yaml_content": {...}},
      "result": {"passed": true}
    }
  ]
}
```

**Validation analytics**:
- Most common validation failures
- Average attempts per phase
- Workflows with highest failure rates
- AI learning curves (attempts over time)

---

## Appendices

### Appendix A: gate-definition.yaml Template

```yaml
phase: 0
phase_name: "Phase Name"

checkpoint:
  strict: true
  allow_override: false
  
  evidence_schema:
    field_name:
      type: string
      required: true
      validator: "validator_name"
      validator_params:
        param1: value1
      description: "What this field proves"
  
  validators:
    validator_name:
      function: "lambda x, param1: validation_logic"
      error_message: "Clear error message with {param1}"
  
  cross_field_validation:
    - check: "field1 consistency with field2"
      error_message: "What's inconsistent"
```

### Appendix B: Validator Patterns

**String validators**:
```yaml
non_empty:
  function: "lambda s: isinstance(s, str) and len(s.strip()) > 0"
  error_message: "String cannot be empty"

contains_any:
  function: "lambda s, markers: any(m in s for m in markers)"
  error_message: "String must contain one of: {markers}"

matches_pattern:
  function: "lambda s, pattern: re.match(pattern, s) is not None"
  error_message: "String doesn't match pattern: {pattern}"
```

**Integer validators**:
```yaml
positive:
  function: "lambda n: isinstance(n, int) and n > 0"
  error_message: "Must be positive integer"

in_range:
  function: "lambda n, min, max: min <= n <= max"
  error_message: "Must be between {min} and {max}"

equals:
  function: "lambda n, expected: n == expected"
  error_message: "Expected {expected}, got {n}"
```

**Object validators**:
```yaml
has_fields:
  function: "lambda obj, fields: all(f in obj for f in fields)"
  error_message: "Missing required fields: {missing}"

valid_structure:
  function: "lambda obj, schema: validate_schema(obj, schema)"
  error_message: "Object doesn't match schema"
```

### Appendix C: Migration Script Outline

```python
#!/usr/bin/env python3
"""Generate gate-definition.yaml for existing workflows."""

def main():
    workflows = find_all_workflows()
    
    for workflow in workflows:
        print(f"Processing: {workflow.name}")
        
        for phase in workflow.phases:
            # Parse checkpoint from phase.md
            checkpoint = parse_checkpoint(phase.md_file)
            
            # Generate gate definition
            gate = generate_gate(checkpoint, strict=False)  # Start lenient
            
            # Write to file
            write_gate(phase.directory / "gate-definition.yaml", gate)
        
        print(f"✅ {workflow.name} complete\n")
```

### Appendix D: Validation Flow Diagram

```
┌─────────────────────────────┐
│ AI: complete_phase(evidence)│
└──────────────┬──────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ CheckpointLoader.load_requirements() │
│  1. Try gate-definition.yaml         │
│  2. Fallback to RAG parsing          │
│  3. Fallback to permissive gate      │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ _validate_checkpoint(evidence)       │
│  1. Check required fields present    │
│  2. Check field types correct        │
│  3. Run custom validators            │
│  4. Check cross-field constraints    │
└──────────────┬───────────────────────┘
               │
         ┌─────┴─────┐
         │           │
         ▼           ▼
    ┌────────
