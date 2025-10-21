# Implementation Approach

**Project:** Evidence Validation System  
**Date:** 2025-10-20

---

## 1. Implementation Philosophy

**Core Principles:**

1. **Test-Driven Development**: Write tests before implementation where possible
2. **Incremental Delivery**: Implement phase-by-phase following the defined order
3. **Code Review Required**: All changes reviewed before merge
4. **Backwards Compatibility First**: Never break existing workflows
5. **Performance by Design**: Target < 100ms validation from the start
6. **Security-First**: Information asymmetry maintained throughout

**Development Approach:**
- Follow the 5-phase implementation plan from tasks.md
- Each phase has clear deliverables and acceptance criteria
- Test at each phase before proceeding
- Deploy using 3-week phased rollout (lenient → strict)

---

## 2. Implementation Order

**Critical Path:** Phase 1 → Phase 2 → Phase 4 → Phase 5

**Phase 1** (8 hours): Enable Core Validation
- Task 1.1: Enable validation in Session Manager (30 min)
- Task 1.2: Implement CheckpointLoader base (2 hours)
- Task 1.3: Implement YAML gate loading (1.5 hours)
- Task 1.4: Implement RAG fallback (1 hour)
- Task 1.5: Implement permissive gate fallback (30 min)
- Task 1.6: Implement ValidatorExecutor (1.5 hours)
- Task 1.7: Implement WorkflowEngine validation (1 hour)

**Phase 2** (6 hours): Migration Script & Gate Generation
- Task 2.1: Create migration script structure (1 hour)
- Task 2.2: Implement workflow scanning (30 min)
- Task 2.3: Implement checkpoint parsing (1.5 hours)
- Task 2.4: Implement gate generation (2 hours)
- Task 2.5: Run migration on all workflows (1 hour)

**Phase 3** (4 hours): workflow_creation_v1 Enhancement (parallel with Phase 4)
- Task 3.1: Create Task 4 - Generate gates (1.5 hours)
- Task 3.2: Create Task 5 - Validate consistency (1 hour)
- Task 3.3: Update Phase 2 metadata (30 min)
- Task 3.4: Test auto-generation (1 hour)

**Phase 4** (10 hours): Testing & Validation
- Task 4.1: Unit tests - CheckpointLoader (2 hours)
- Task 4.2: Unit tests - ValidatorExecutor (1.5 hours)
- Task 4.3: Integration tests - Complete phase flow (2 hours)
- Task 4.4: Performance tests (2 hours)
- Task 4.5: Security tests (1.5 hours)
- Task 4.6: Regression tests (1 hour)

**Phase 5** (6 hours): Deployment & Monitoring
- Task 5.1: Week 1 deployment (lenient) (2 hours)
- Task 5.2: Week 2 refinement (2 hours)
- Task 5.3: Week 3 production ready (strict) (1 hour)
- Task 5.4: Setup monitoring (30 min)
- Task 5.5: Write documentation (30 min)
- Task 5.6: Rollback plan testing (30 min)

---

## 3. Code Patterns

### 3.1 Session Manager Pattern (Task 1.1)

**Component:** Session Manager (mcp_server/core/session.py)

**Pattern:** Simple Enablement (1-line fix)

**Good Example:**
```python
# File: mcp_server/core/session.py
# Line ~503

def complete_phase(
    self,
    workflow_type: str,
    phase: int,
    evidence: Dict[str, Any]
) -> Dict[str, Any]:
    """Complete phase with evidence validation."""
    
    # BEFORE (hardcoded bypass):
    # checkpoint_passed = True
    
    # AFTER (actual validation):
    passed, result = self.engine._validate_checkpoint(
        workflow_type, phase, evidence
    )
    checkpoint_passed = passed
    
    if checkpoint_passed:
        # Advance to next phase
        self.state.current_phase += 1
        self.state.checkpoint_status = CheckpointStatus.PASSED
    else:
        # Stay in current phase, return errors
        self.state.checkpoint_status = CheckpointStatus.FAILED
        self.state.phase_artifacts[phase]["checkpoint_result"] = result
    
    return {
        "checkpoint_passed": checkpoint_passed,
        **result
    }
```

**Anti-pattern (What NOT to do):**
```python
# DON'T: Add complex logic to Session Manager
def complete_phase(self, ...):
    # Session Manager should NOT contain validation logic
    # It should delegate to WorkflowEngine
    if evidence.get("required_field"):  # DON'T DO THIS
        checkpoint_passed = True
    # Instead, call self.engine._validate_checkpoint()
```

---

### 3.2 Checkpoint Loader Pattern (Tasks 1.2-1.5)

**Component:** CheckpointLoader (mcp_server/config/loader.py)

**Pattern:** Three-Tier Fallback with Caching

**Good Example:**
```python
from dataclasses import dataclass
from typing import Dict, Optional
from pathlib import Path
import threading
import yaml

@dataclass
class CheckpointRequirements:
    """Checkpoint validation requirements."""
    evidence_schema: Dict[str, 'FieldSchema']
    validators: Dict[str, str]
    cross_field_rules: List['CrossFieldRule']
    strict: bool
    allow_override: bool
    source: str

class CheckpointLoader:
    """Loads checkpoint requirements with fallback."""
    
    _cache: Dict[str, CheckpointRequirements] = {}
    _cache_lock: threading.Lock = threading.Lock()
    
    def load_checkpoint_requirements(
        self,
        workflow_type: str,
        phase: int
    ) -> CheckpointRequirements:
        """
        Load requirements using three-tier strategy.
        
        Strategy:
        1. Try gate-definition.yaml (cached)
        2. Try RAG parsing
        3. Return permissive gate
        """
        cache_key = f"{workflow_type}:{phase}"
        
        # Fast path: Check cache without lock
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Slow path: Load with lock (double-checked locking)
        with self._cache_lock:
            # Check again inside lock
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Try loading
            requirements = self._load_with_fallback(workflow_type, phase)
            
            # Cache and return
            self._cache[cache_key] = requirements
            return requirements
    
    def _load_with_fallback(
        self,
        workflow_type: str,
        phase: int
    ) -> CheckpointRequirements:
        """Execute three-tier fallback strategy."""
        
        # Tier 1: YAML
        requirements = self._load_from_yaml(workflow_type, phase)
        if requirements:
            logger.info(f"Loaded gate from YAML: {workflow_type}:{phase}")
            return requirements
        
        # Tier 2: RAG
        requirements = self._load_from_rag(workflow_type, phase)
        if requirements:
            logger.info(f"Loaded gate from RAG: {workflow_type}:{phase}")
            return requirements
        
        # Tier 3: Permissive
        logger.warning(f"Using permissive gate: {workflow_type}:{phase}")
        return self._get_permissive_gate()
    
    def _load_from_yaml(
        self,
        workflow_type: str,
        phase: int
    ) -> Optional[CheckpointRequirements]:
        """Load from gate-definition.yaml."""
        gate_path = Path(
            f".agent-os/workflows/{workflow_type}/phases/{phase}/gate-definition.yaml"
        )
        
        if not gate_path.exists():
            return None
        
        try:
            content = yaml.safe_load(gate_path.read_text())
            return self._parse_gate_content(content)
        except Exception as e:
            logger.error(f"Failed to load YAML gate: {e}")
            return None
```

**Anti-patterns:**
```python
# DON'T: Use unsafe YAML loading
content = yaml.load(gate_path.read_text())  # DON'T - code execution risk

# DON'T: Skip caching
def load_checkpoint_requirements(self, workflow_type, phase):
    return self._load_from_yaml(workflow_type, phase)  # DON'T - slow

# DON'T: Use simple locking (lock contention)
with self._cache_lock:
    if cache_key in self._cache:
        return self._cache[cache_key]  # DON'T - lock every read
```

---

### 3.3 Validator Executor Pattern (Task 1.6)

**Component:** ValidatorExecutor (mcp_server/validation/executor.py)

**Pattern:** Safe Lambda Execution with Restricted Globals

**Good Example:**
```python
import re
import yaml
from typing import Any, Dict, Tuple, Optional

class ValidatorExecutor:
    """Execute lambda validators in restricted context."""
    
    # Only safe builtins - NO os, sys, subprocess, etc.
    SAFE_GLOBALS = {
        'len': len,
        'str': str,
        'int': int,
        'bool': bool,
        're': re,
        'yaml': yaml,
        'any': any,
        'all': all,
        'set': set,
        'list': list,
        'dict': dict,
        'abs': abs,
        'min': min,
        'max': max,
    }
    
    def execute_validator(
        self,
        validator_expr: str,
        value: Any,
        params: Dict[str, Any] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute validator lambda in safe context.
        
        Args:
            validator_expr: Lambda expression (e.g., "lambda x: x > 0")
            value: Value to validate
            params: Optional parameters for validator
            
        Returns:
            (passed: bool, error_message: Optional[str])
        """
        if params is None:
            params = {}
        
        try:
            # Evaluate lambda in restricted context
            validator_func = eval(
                validator_expr,
                self.SAFE_GLOBALS,  # Restricted globals
                {}  # Empty locals (no access to surrounding scope)
            )
            
            # Execute validator
            passed = bool(validator_func(value, **params))
            
            return (passed, None)
            
        except Exception as e:
            # Validator exception = validation failure
            return (False, f"Validator failed: {str(e)}")
    
    def validate_syntax(self, validator_expr: str) -> bool:
        """Validate lambda expression syntax."""
        try:
            compile(validator_expr, '<string>', 'eval')
            return True
        except SyntaxError:
            return False
    
    def is_safe_validator(self, validator_expr: str) -> bool:
        """Check for forbidden patterns."""
        forbidden_patterns = [
            r'__import__',
            r'exec\s*\(',
            r'eval\s*\(',
            r'compile\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'os\.',
            r'sys\.',
            r'subprocess\.',
        ]
        
        for pattern in forbidden_patterns:
            if re.search(pattern, validator_expr):
                return False
        
        return True
```

**Anti-patterns:**
```python
# DON'T: Use unrestricted eval
validator_func = eval(validator_expr)  # DON'T - security risk

# DON'T: Allow access to builtins
eval(validator_expr, {'__builtins__': __builtins__}, {})  # DON'T - dangerous

# DON'T: Import modules inside validators
validators = {
    "hack": "lambda x: __import__('os').system('rm -rf /')"  # DON'T - code execution
}
```

---

### 3.4 Workflow Engine Validation Pattern (Task 1.7)

**Component:** WorkflowEngine (mcp_server/workflow_engine.py)

**Pattern:** Multi-Layer Validation with Structured Errors

**Good Example:**
```python
from typing import Dict, List, Tuple, Any

class WorkflowEngine:
    """Orchestrates workflow execution and validation."""
    
    def __init__(self, loader: CheckpointLoader):
        self.loader = loader
        self.executor = ValidatorExecutor()
    
    def _validate_checkpoint(
        self,
        workflow_type: str,
        phase: int,
        evidence: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate evidence against checkpoint requirements.
        
        Multi-layer validation:
        1. Load gate definition
        2. Check required fields
        3. Validate field types
        4. Run custom validators
        5. Check cross-field rules
        
        Returns:
            (passed: bool, result: Dict)
        """
        # Load requirements
        requirements = self.loader.load_checkpoint_requirements(
            workflow_type, phase
        )
        
        # Initialize result
        errors: List[str] = []
        warnings: List[str] = []
        fields_submitted = list(evidence.keys())
        fields_required = requirements.get_required_fields()
        fields_missing = [f for f in fields_required if f not in evidence]
        
        # Layer 1: Check required fields
        for field_name in fields_required:
            if field_name not in evidence:
                errors.append(
                    f"Field '{field_name}' is required but missing"
                )
        
        # Layer 2 & 3: Validate present fields (type + validators)
        for field_name, field_value in evidence.items():
            if field_name not in requirements.evidence_schema:
                warnings.append(
                    f"Field '{field_name}' not in schema (ignoring)"
                )
                continue
            
            schema = requirements.evidence_schema[field_name]
            
            # Layer 2: Type validation
            if not schema.validate_type(field_value):
                errors.append(
                    f"Field '{field_name}' must be {schema.type}, "
                    f"got: {type(field_value).__name__}"
                )
                continue
            
            # Layer 3: Custom validator
            if schema.validator:
                validator_expr = requirements.validators.get(schema.validator)
                if not validator_expr:
                    warnings.append(
                        f"Validator '{schema.validator}' not found for '{field_name}'"
                    )
                    continue
                
                passed, error = self.executor.execute_validator(
                    validator_expr,
                    field_value,
                    schema.validator_params or {}
                )
                
                if not passed:
                    errors.append(
                        f"Validator '{schema.validator}' failed for "
                        f"field '{field_name}': {error}"
                    )
        
        # Layer 4: Cross-field validation
        for rule in requirements.cross_field_rules:
            try:
                if not rule.evaluate(evidence):
                    errors.append(
                        f"Cross-field validation failed: {rule.error_message}"
                    )
            except Exception as e:
                errors.append(f"Cross-field rule error: {e}")
        
        # Determine if passed
        if requirements.strict:
            passed = len(errors) == 0
        else:
            passed = True  # Lenient mode: errors become warnings
            if errors:
                warnings.extend(errors)
                errors = []
        
        # Build result
        result = {
            "checkpoint_passed": passed,
            "errors": errors,
            "warnings": warnings,
            "diagnostics": {
                "fields_submitted": fields_submitted,
                "fields_required": fields_required,
                "fields_missing": fields_missing,
                "strict_mode": requirements.strict,
                "gate_source": requirements.source,
                "validation_timestamp": datetime.now().isoformat()
            },
            "remediation": self._build_remediation(errors),
            "next_steps": self._build_next_steps(errors)
        }
        
        return (passed, result)
```

**Anti-patterns:**
```python
# DON'T: Validate all fields even after first error (wasteful)
for field in all_fields:
    validate(field)  # DON'T - use fail-fast

# DON'T: Return generic errors
return {"error": "Validation failed"}  # DON'T - be specific

# DON'T: Crash on validation error
if field not in evidence:
    raise Exception("Missing field")  # DON'T - return structured error
```

---

## 4. Testing Strategy

### 4.1 Unit Testing Approach

**Coverage Target:** > 90% for validation system

**Test Structure:**
```python
# tests/unit/test_checkpoint_loader.py

import pytest
from mcp_server.config.loader import CheckpointLoader

class TestCheckpointLoader:
    """Unit tests for CheckpointLoader."""
    
    @pytest.fixture
    def loader(self):
        return CheckpointLoader()
    
    def test_load_from_yaml_success(self, loader, tmp_path):
        """Test successful YAML loading."""
        # Create test YAML
        gate_file = tmp_path / "gate-definition.yaml"
        gate_file.write_text("""
checkpoint:
  strict: false
  allow_override: true
evidence_schema:
  test_field:
    type: boolean
    required: true
validators: {}
        """)
        
        # Test loading
        requirements = loader._load_from_yaml("test_workflow", 1)
        
        assert requirements is not None
        assert "test_field" in requirements.evidence_schema
        assert requirements.strict == False
    
    def test_cache_hit_performance(self, loader):
        """Verify cache hit < 10ms."""
        import time
        
        # Pre-warm cache
        loader.load_checkpoint_requirements("spec_creation_v1", 1)
        
        # Time cache hit
        start = time.perf_counter()
        requirements = loader.load_checkpoint_requirements("spec_creation_v1", 1)
        duration = (time.perf_counter() - start) * 1000
        
        assert duration < 10, f"Cache hit took {duration}ms (expected < 10ms)"
    
    def test_thread_safety(self, loader):
        """Test concurrent access."""
        import concurrent.futures
        
        def load():
            return loader.load_checkpoint_requirements("test_workflow", 1)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(load) for _ in range(100)]
            results = [f.result() for f in futures]
        
        # All should return same cached instance
        assert all(r is results[0] for r in results)
```

**Testing Checklist:**
- [ ] All public methods tested
- [ ] Edge cases covered (empty inputs, null values)
- [ ] Error conditions tested
- [ ] Performance targets verified
- [ ] Thread safety confirmed

---

### 4.2 Integration Testing Approach

**Test Structure:**
```python
# tests/integration/test_complete_phase_validation.py

import pytest
from mcp_server.core.session import Session

class TestCompletePhaseValidation:
    """Integration tests for complete_phase with validation."""
    
    @pytest.fixture
    def session(self):
        return Session(workflow_type="spec_creation_v1")
    
    def test_valid_evidence_passes(self, session):
        """Test happy path: valid evidence passes validation."""
        evidence = {
            "srd_created": True,
            "business_goals": 4,
            "user_stories": 7,
            "functional_requirements": 12,
            "nfr_categories": 8,
            "out_of_scope_defined": True,
            "traceability_matrix": True,
            "supporting_docs_referenced": True
        }
        
        result = session.complete_phase(
            workflow_type="spec_creation_v1",
            phase=1,
            evidence=evidence
        )
        
        assert result["checkpoint_passed"] == True
        assert result["errors"] == []
        assert result["next_phase"] == 2
    
    def test_missing_required_field_fails(self, session):
        """Test validation failure: missing required field."""
        evidence = {
            "business_goals": 4,
            # Missing: user_stories (required)
        }
        
        result = session.complete_phase(
            workflow_type="spec_creation_v1",
            phase=1,
            evidence=evidence
        )
        
        assert result["checkpoint_passed"] == False
        assert any("user_stories" in e for e in result["errors"])
        assert "remediation" in result
        assert "next_steps" in result
    
    def test_fallback_to_rag(self, session):
        """Test fallback when YAML missing."""
        # Test workflow without gate-definition.yaml
        result = session.complete_phase(
            workflow_type="workflow_without_gates",
            phase=1,
            evidence={"some_field": True}
        )
        
        # Should not fail (fallback to RAG/permissive)
        assert "checkpoint_passed" in result
```

---

### 4.3 Performance Testing Approach

**Test Structure:**
```python
# tests/unit/test_performance.py

import pytest
import time
from mcp_server.workflow_engine import WorkflowEngine

class TestPerformance:
    """Performance tests for validation system."""
    
    def test_cached_validation_speed(self):
        """Verify < 10ms for cached validation."""
        engine = WorkflowEngine()
        
        # Pre-warm cache
        engine._validate_checkpoint("spec_creation_v1", 1, valid_evidence)
        
        # Time validation
        start = time.perf_counter()
        passed, result = engine._validate_checkpoint(
            "spec_creation_v1", 1, valid_evidence
        )
        duration = (time.perf_counter() - start) * 1000
        
        assert duration < 10, f"Cached validation took {duration}ms"
        assert passed == True
    
    def test_concurrent_performance(self):
        """Verify no degradation with concurrent workflows."""
        engine = WorkflowEngine()
        
        def validate():
            start = time.perf_counter()
            engine._validate_checkpoint("spec_creation_v1", 1, valid_evidence)
            return (time.perf_counter() - start) * 1000
        
        # 10 concurrent validations
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            durations = list(executor.map(lambda _: validate(), range(10)))
        
        # All should be fast
        assert all(d < 100 for d in durations)
        
        # 95th percentile
        p95 = sorted(durations)[int(len(durations) * 0.95)]
        assert p95 < 50, f"p95 latency {p95}ms (expected < 50ms)"
```

---

### 4.4 Security Testing Approach

**Test Structure:**
```python
# tests/unit/test_security.py

import pytest
from mcp_server.validation.executor import ValidatorExecutor

class TestSecurity:
    """Security tests for validation system."""
    
    def test_schema_hidden_from_ai(self):
        """Verify get_task() never returns gate content."""
        task = get_task("spec_creation_v1", 1, 1)
        
        # Schema should not be in response
        assert "gate-definition.yaml" not in str(task)
        assert "evidence_schema" not in str(task)
        assert "validators" not in str(task)
    
    def test_dangerous_validators_blocked(self):
        """Verify dangerous validators rejected."""
        executor = ValidatorExecutor()
        
        dangerous_validators = [
            "lambda x: __import__('os').system('rm -rf /')",
            "lambda x: exec('malicious code')",
            "lambda x: open('/etc/passwd').read()",
        ]
        
        for validator in dangerous_validators:
            # Should not pass safety check
            assert not executor.is_safe_validator(validator)
            
            # Should fail on execution
            passed, error = executor.execute_validator(validator, "test", {})
            assert passed == False
    
    def test_restricted_globals(self):
        """Verify only safe globals accessible."""
        executor = ValidatorExecutor()
        
        # These should work (safe)
        passed, _ = executor.execute_validator("lambda x: len(x) > 0", "test", {})
        assert passed == True
        
        # These should fail (unsafe)
        with pytest.raises(NameError):
            executor.execute_validator("lambda x: os.listdir('/')", "test", {})
```

---

## 5. Deployment Approach

### 5.1 Pre-Deployment Checklist

**Before deploying to production:**
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Performance tests pass (< 100ms validation)
- [ ] Security tests pass (schemas hidden, validators safe)
- [ ] Regression tests pass (existing workflows work)
- [ ] Code review complete
- [ ] Documentation updated
- [ ] Rollback plan tested

### 5.2 Deployment Steps (Week 1)

**Step 1: Deploy Code Changes**
```bash
# Create feature branch
git checkout -b feature/evidence-validation

# Implement changes
# ... (follow Phase 1-4 from tasks.md)

# Run tests
pytest tests/ --cov=mcp_server --cov-report=term-missing

# Code review
gh pr create --title "Evidence Validation System" --body "..."

# After approval, merge
git checkout main
git merge feature/evidence-validation
git push origin main
```

**Step 2: Run Migration Script**
```bash
# Dry-run first
python scripts/generate-gate-definitions.py --dry-run

# Review output, then generate
python scripts/generate-gate-definitions.py

# Verify gates created
ls -la .agent-os/workflows/*/phases/*/gate-definition.yaml | wc -l
# Expected: ~85 files (15 workflows × ~5-6 phases avg)

# Commit gates
git add .agent-os/workflows/
git commit -m "Add gate-definition.yaml files for all workflows"
git push origin main
```

**Step 3: Verify in Production**
```bash
# Test with real workflow
curl -X POST http://localhost:8000/mcp/complete_phase \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "workflow_type": "spec_creation_v1",
    "phase": 1,
    "evidence": {
      "srd_created": true,
      "business_goals": 4,
      "user_stories": 7,
      "functional_requirements": 12,
      "nfr_categories": 8,
      "out_of_scope_defined": true,
      "traceability_matrix": true,
      "supporting_docs_referenced": true
    }
  }'

# Expected: {"checkpoint_passed": true, "next_phase": 2}
```

### 5.3 Week 2: Refinement

**Analyze Validation Logs:**
```python
# scripts/analyze_validation_failures.py

import json
from collections import Counter

def analyze_logs():
    """Analyze validation failure patterns."""
    failures = []
    
    with open("logs/validation.log") as f:
        for line in f:
            if "validation failed" in line:
                data = json.loads(line)
                failures.append(data)
    
    # Most common errors
    errors = Counter(
        error for failure in failures 
        for error in failure.get("errors", [])
    )
    
    print("Most common validation errors:")
    for error, count in errors.most_common(10):
        print(f"{count:3d}: {error}")
    
    # Workflows with high failure rate
    workflow_failures = Counter(
        failure["workflow_type"] for failure in failures
    )
    
    print("\nWorkflows with most failures:")
    for workflow, count in workflow_failures.most_common(5):
        print(f"{count:3d}: {workflow}")
```

**Refine Gates:**
```yaml
# Example: Add validator based on failure pattern
# .agent-os/workflows/spec_creation_v1/phases/1/gate-definition.yaml

evidence_schema:
  business_goals:
    type: integer
    required: true
    validator: in_range  # ADD: Based on analysis
    validator_params:
      min_val: 1
      max_val: 10
    description: "Number of business goals (1-10 is reasonable)"

validators:
  in_range: "lambda x, min_val, max_val: min_val <= x <= max_val"  # ADD
```

### 5.4 Week 3: Production Ready

**Enable Strict Mode:**
```yaml
# Update critical workflows to strict mode
# .agent-os/workflows/spec_creation_v1/phases/2/gate-definition.yaml

checkpoint:
  strict: true  # CHANGE: from false to true
  allow_override: false  # CHANGE: from true to false
```

**Verify Production Stability:**
```bash
# Check validation metrics
curl http://localhost:8000/metrics | grep validation

# Expected metrics:
# validation_pass_rate{workflow="spec_creation_v1",phase="1"} 0.95
# validation_p95_latency_ms{workflow="spec_creation_v1",phase="1"} 45
# validation_cache_hit_rate 0.97
```

---

## 6. Monitoring & Observability

### 6.1 Key Metrics to Track

**Validation Performance:**
- `validation_latency_ms` (p50, p95, p99)
- `validation_cache_hit_rate`
- `validation_pass_rate` (per workflow/phase)

**System Health:**
- `validation_errors_total` (counter)
- `validation_fallback_total` (counter by source: rag, permissive)
- `concurrent_validations` (gauge)

**Implementation:**
```python
# mcp_server/workflow_engine.py

import logging
from prometheus_client import Histogram, Counter, Gauge

# Metrics
validation_latency = Histogram(
    'validation_latency_ms',
    'Validation latency in milliseconds',
    ['workflow_type', 'phase']
)

validation_results = Counter(
    'validation_results_total',
    'Validation results',
    ['workflow_type', 'phase', 'result']  # result: pass/fail
)

def _validate_checkpoint(self, workflow_type, phase, evidence):
    """Validate with metrics."""
    import time
    
    start = time.perf_counter()
    
    try:
        # Load requirements
        requirements = self.loader.load_checkpoint_requirements(
            workflow_type, phase
        )
        
        # Track gate source
        gate_source = requirements.source
        validation_fallback.labels(source=gate_source).inc()
        
        # Validate
        passed, result = self._validate_checkpoint_impl(
            workflow_type, phase, evidence, requirements
        )
        
        # Record metrics
        duration_ms = (time.perf_counter() - start) * 1000
        validation_latency.labels(
            workflow_type=workflow_type,
            phase=phase
        ).observe(duration_ms)
        
        validation_results.labels(
            workflow_type=workflow_type,
            phase=phase,
            result="pass" if passed else "fail"
        ).inc()
        
        # Log slow validations
        if duration_ms > 100:
            logger.warning(
                f"Slow validation: {workflow_type}:{phase} took {duration_ms}ms"
            )
        
        return (passed, result)
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        validation_errors.labels(
            workflow_type=workflow_type,
            phase=phase
        ).inc()
        raise
```

---

### 6.2 Logging Strategy

**Log Levels:**
- **INFO**: Validation success, cache hits
- **WARNING**: Validation failures (expected), slow validations, fallbacks
- **ERROR**: System errors, validation exceptions

**Log Format:**
```json
{
  "timestamp": "2025-10-20T15:12:00Z",
  "level": "INFO",
  "message": "Checkpoint validation passed",
  "workflow_type": "spec_creation_v1",
  "phase": 1,
  "duration_ms": 23,
  "cache_hit": true,
  "gate_source": "yaml"
}
```

---

## 7. Troubleshooting Guide

### 7.1 Common Issues

#### Issue 1: Validation Always Passes (No Gating)

**Symptom:** All evidence passes validation regardless of content.

**Cause:** Validation not enabled, or using permissive gate.

**Diagnosis:**
```python
# Check if validation enabled
# File: mcp_server/core/session.py line 503
# Should be: passed, result = self.engine._validate_checkpoint(...)
# NOT: checkpoint_passed = True

# Check gate source
logger.info(f"Gate source: {requirements.source}")
# If source="permissive", gate-definition.yaml missing
```

**Solution:**
1. Verify session.py fix applied (line 503)
2. Check gate-definition.yaml exists
3. Run migration script if gates missing

---

#### Issue 2: Validation Too Slow (> 100ms)

**Symptom:** Validation taking longer than 100ms target.

**Cause:** Cache miss, complex validators, or I/O operations.

**Diagnosis:**
```python
# Check cache hit rate
metrics = get_metrics()
cache_hit_rate = metrics['validation_cache_hit_rate']
# Should be > 0.95

# Check validation duration
p95_latency = metrics['validation_latency_ms_p95']
# Should be < 50ms (cached) or < 100ms (first time)
```

**Solution:**
1. Verify caching enabled (double-checked locking)
2. Simplify complex validators
3. Remove I/O from validators
4. Pre-warm cache on startup (if needed)

---

#### Issue 3: Schema Leaked to AI

**Symptom:** AI agent discovers validation requirements.

**Cause:** gate-definition.yaml exposed via MCP tool.

**Diagnosis:**
```python
# Check get_task() response
task = get_task("spec_creation_v1", 1, 1)
# Search for leaked content
assert "gate-definition.yaml" not in str(task)
assert "evidence_schema" not in str(task)
```

**Solution:**
1. Verify get_task() excludes gate files
2. Review all MCP tool responses
3. Add security tests to catch leaks

---

#### Issue 4: Validator Security Violation

**Symptom:** Dangerous validator detected or executed.

**Cause:** Malicious or poorly written gate-definition.yaml.

**Diagnosis:**
```python
# Check validator safety
executor = ValidatorExecutor()
is_safe = executor.is_safe_validator(validator_expr)
# Should be True for all validators

# Check for forbidden patterns
forbidden = ['__import__', 'exec', 'open', 'os.', 'sys.']
for pattern in forbidden:
    assert pattern not in validator_expr
```

**Solution:**
1. Review gate-definition.yaml validators
2. Remove dangerous patterns
3. Use pre-commit hook to validate
4. Restrict file write access

---

#### Issue 5: Backwards Compatibility Broken

**Symptom:** Existing workflows fail after deployment.

**Cause:** Fallback chain not working, or strict mode enabled prematurely.

**Diagnosis:**
```python
# Test fallback chain
result = complete_phase(
    workflow_type="workflow_without_gates",
    phase=1,
    evidence={}
)
# Should not crash, should use RAG or permissive gate
```

**Solution:**
1. Verify three-tier fallback working
2. Check strict=false for migrated gates
3. Test with workflows missing gates
4. Rollback if needed

---

### 7.2 Debugging Tools

**Tool 1: Validation Test Script**
```python
# scripts/test_validation.py

def test_validation(workflow_type: str, phase: int):
    """Test validation for specific workflow phase."""
    engine = WorkflowEngine()
    
    # Test with empty evidence
    passed, result = engine._validate_checkpoint(
        workflow_type, phase, {}
    )
    
    print(f"Empty evidence: {'PASS' if passed else 'FAIL'}")
    if not passed:
        print(f"Errors: {result['errors']}")
    
    # Test with valid evidence (if known)
    # ... add valid evidence test
```

**Tool 2: Cache Inspector**
```python
# scripts/inspect_cache.py

def inspect_cache():
    """Inspect CheckpointLoader cache state."""
    loader = CheckpointLoader()
    
    print(f"Cache size: {len(loader._cache)}")
    print(f"Cached workflows:")
    for key in sorted(loader._cache.keys()):
        requirements = loader._cache[key]
        print(f"  {key}: {len(requirements.evidence_schema)} fields, source={requirements.source}")
```

**Tool 3: Gate Validator**
```python
# scripts/validate_gates.py

def validate_all_gates():
    """Validate all gate-definition.yaml files."""
    import yaml
    from pathlib import Path
    
    gates = Path(".agent-os/workflows").rglob("gate-definition.yaml")
    
    for gate_path in gates:
        print(f"Validating: {gate_path}")
        
        # Load and parse
        content = yaml.safe_load(gate_path.read_text())
        
        # Validate structure
        assert "checkpoint" in content
        assert "evidence_schema" in content
        
        # Validate validators
        for name, expr in content.get("validators", {}).items():
            executor = ValidatorExecutor()
            assert executor.validate_syntax(expr), f"Invalid syntax: {name}"
            assert executor.is_safe_validator(expr), f"Unsafe validator: {name}"
        
        print(f"  ✓ Valid")
```

---

### 7.3 Emergency Procedures

#### Procedure 1: Rollback Validation System

**When to use:** Critical bug in validation system blocking all workflows.

**Steps:**
```bash
# 1. Revert session.py fix
git checkout HEAD~1 -- mcp_server/core/session.py

# 2. Restart server
systemctl restart agent-os

# 3. Verify workflows work
curl -X POST /mcp/complete_phase -d '{"session_id": "test", ...}'

# Expected: checkpoint_passed=true (hardcoded bypass restored)
```

**Time:** < 5 minutes
**Impact:** Validation disabled, checkpoints bypassed (safe, non-breaking)

---

#### Procedure 2: Switch to Lenient Mode

**When to use:** Too many false positives, gates too strict.

**Steps:**
```bash
# 1. Update all gates to lenient
find .agent-os/workflows -name "gate-definition.yaml" -exec \
  sed -i '' 's/strict: true/strict: false/' {} \;

# 2. Commit changes
git add .agent-os/workflows/
git commit -m "Switch gates to lenient mode"
git push

# 3. Restart server (if needed)
```

**Time:** < 2 minutes
**Impact:** Validation errors become warnings (non-blocking)

---

#### Procedure 3: Clear Cache

**When to use:** Cache corruption or stale data.

**Steps:**
```python
# Option 1: Restart server (clears cache)
systemctl restart agent-os

# Option 2: Programmatic clear (if accessible)
from mcp_server.config.loader import CheckpointLoader
CheckpointLoader._cache.clear()
```

**Time:** < 1 minute
**Impact:** Next validation will reload from disk (slight latency)

---

## 8. Post-Deployment Checklist

**Week 1 (Lenient Mode):**
- [ ] Code deployed successfully
- [ ] Migration script run (gates generated)
- [ ] All workflows still working
- [ ] Validation metrics being collected
- [ ] No errors in logs
- [ ] Cache hit rate > 90%
- [ ] Validation latency < 100ms

**Week 2 (Refinement):**
- [ ] Validation logs analyzed
- [ ] Common errors identified
- [ ] Gates refined based on data
- [ ] workflow_creation_v1 updated
- [ ] Documentation updated

**Week 3 (Strict Mode):**
- [ ] Critical workflows switched to strict
- [ ] All tests still passing
- [ ] No spike in validation failures
- [ ] Production stable
- [ ] Monitoring dashboard active

---

## 9. Success Metrics

**Immediate (Week 1):**
- Zero breaking changes (100% backwards compatible)
- Validation enabled (checkpoint_passed based on actual validation)
- 100% workflow coverage (all workflows have gates)

**Short-term (Week 2-3):**
- < 100ms validation latency (95th percentile)
- > 95% cache hit rate
- > 90% test coverage
- Zero security incidents (no schema leaks)

**Long-term (Month 1+):**
- Reduced false evidence submissions (AI learns requirements)
- Improved workflow completion quality
- Systematic validation coverage expansion

---

## 10. Summary

**The Evidence Validation System is production-ready when:**

1. ✅ **Core functionality working**
   - Validation enabled (session.py fixed)
   - CheckpointLoader with three-tier fallback
   - ValidatorExecutor with safe execution

2. ✅ **Full coverage achieved**
   - All workflows have gate-definition.yaml
   - Migration script working
   - workflow_creation_v1 auto-generates gates

3. ✅ **Testing complete**
   - > 90% code coverage
   - All unit/integration/performance tests passing
   - Security tests verify information asymmetry

4. ✅ **Deployment ready**
   - Phased 3-week rollout plan (lenient → strict)
   - Monitoring and alerting configured
   - Rollback plan tested (< 5 minute rollback)

5. ✅ **Documentation complete**
   - Developer guide for creating gates
   - Troubleshooting guide for common issues
   - Emergency procedures documented

**The system transforms Agent OS from "checkpoints that don't actually check" to "systematic validation that ensures quality while maintaining backwards compatibility and performance."**
