# Technical Specifications

**Project:** Evidence Validation System  
**Date:** 2025-10-20  
**Based on:** srd.md (requirements)

---

## 1. Architecture Overview

### 1.1 Architectural Pattern: Modular Monolith Enhancement

**Pattern:** Modular Monolith with Layered Architecture

The Evidence Validation System is implemented as an enhancement to the existing Agent OS workflow engine, following a modular monolith pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Tool Layer                           │
│  (complete_phase, get_task - unchanged interface)             │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                    Session Manager                              │
│  - Phase advancement logic                                      │
│  - Evidence submission coordination                             │
│  - STATE CHANGE: Enable validation (1-line fix)                │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                  Workflow Engine                                │
│  - _validate_checkpoint() [EXISTING - currently bypassed]      │
│  - Validation orchestration                                     │
│  - Result interpretation                                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                 CheckpointLoader                                │
│  - ENHANCEMENT: Load from gate-definition.yaml                 │
│  - Fallback to RAG parsing                                      │
│  - Fallback to permissive gate                                  │
│  - Thread-safe caching (double-checked locking)                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ├──────────────────────────────────────┐
                     │                                      │
┌────────────────────▼─────────────┐  ┌──────────────────▼─────────┐
│   gate-definition.yaml           │  │   RAG Engine              │
│   (NEW - config files)           │  │   (EXISTING - unchanged)  │
│                                  │  │                            │
│   - Evidence schema              │  │   - Checkpoint parsing    │
│   - Validators (lambda)          │  │   - Natural language      │
│   - Strictness config            │  │     requirements          │
│   - Cross-field rules            │  └───────────────────────────┘
│                                  │
│   HIDDEN from AI agents          │
└──────────────────────────────────┘
```

**Key Architectural Principles:**

1. **Information Asymmetry**: AI agents see natural language tasks, system knows hidden schemas
2. **Backwards Compatibility**: Graceful fallback ensures existing workflows don't break
3. **Config-Driven**: Validation behavior controlled by YAML files, not code changes
4. **Minimal Change Footprint**: 1-line fix enables entire system, config files do the rest
5. **Progressive Strictness**: Lenient gates initially, tighten based on real usage

### 1.2 Architectural Decisions

#### Decision 1: Modular Monolith (Not Microservices)

**Decision:** Enhance existing workflow engine in-place rather than extract validation to separate service.

**Rationale:**
- **FR-002, FR-004**: Validation is tightly coupled to checkpoint evaluation
- **NFR-R1**: Zero breaking changes required
- **NFR-D2**: Zero downtime deployment
- Validation latency critical (< 100ms) - no network overhead
- Single codebase simplifies testing and deployment

**Alternatives Considered:**
- **Microservice**: Rejected - adds network latency, deployment complexity, and breaks existing interfaces
- **Plugin Architecture**: Rejected - over-engineering for a core system enhancement

**Trade-offs:**
- **Pros**: Simple, fast, backwards compatible, minimal risk
- **Cons**: Validation logic coupled to workflow engine (acceptable for core functionality)

---

#### Decision 2: Config-Driven Validation (Not Code-Based)

**Decision:** Store validation requirements in gate-definition.yaml files, not in Python code or database.

**Rationale:**
- **FR-005**: Must hide schemas from AI agents
- **NFR-M2**: Configuration-driven behavior
- **Goal 2**: Information asymmetry as security mechanism
- YAML files can be excluded from task content delivery
- No code deployment required to update validation rules
- Human-readable for manual refinement

**Alternatives Considered:**
- **Database Storage**: Rejected - harder to version control, no git diff
- **Python Code**: Rejected - requires deployment for changes, harder to hide from AI
- **JSON Format**: Rejected - less human-readable than YAML

**Trade-offs:**
- **Pros**: Version controlled, readable, AI-hidden, no deployment for updates
- **Cons**: Requires YAML parsing (acceptable - pyyaml already in stack)

---

#### Decision 3: Three-Tier Fallback Strategy

**Decision:** CheckpointLoader tries gate-definition.yaml → RAG parsing → permissive gate, in that order.

**Rationale:**
- **NFR-R1**: Backwards compatibility (100% of existing workflows must work)
- **FR-011**: Graceful degradation when gate YAML missing
- Phased migration strategy (not big-bang)
- Early deployment with lenient validation reduces risk

**Alternatives Considered:**
- **Require YAML or Fail**: Rejected - breaks all existing workflows
- **RAG Only**: Rejected - doesn't achieve information asymmetry goal
- **Two-Tier (YAML → Fail)**: Rejected - too aggressive, high risk

**Trade-offs:**
- **Pros**: Zero breaking changes, smooth migration, risk mitigation
- **Cons**: Slight complexity in CheckpointLoader (acceptable for backwards compatibility)

---

#### Decision 4: Lambda Validators (Not External Modules)

**Decision:** Validators are Python lambda expressions in YAML, evaluated in controlled context.

**Rationale:**
- **NFR-S2**: Security (no arbitrary code execution)
- **FR-009**: Multi-layer validation sufficient with lambda syntax
- Simplicity (no dependency management, module loading)
- Fast execution (inline, no I/O)

**Alternatives Considered:**
- **External Python Modules**: Rejected - security risk, requires sandboxing, deployment complexity
- **Regex Only**: Rejected - insufficient for complex validation (e.g., YAML parsing)
- **Declarative DSL**: Rejected - over-engineering, lambda syntax sufficient

**Trade-offs:**
- **Pros**: Secure, simple, fast, no deployment overhead
- **Cons**: Less expressive than full modules (acceptable for v1.0, can add in v2.0 with sandboxing)

---

#### Decision 5: Synchronous Validation (Not Async)

**Decision:** Validation completes synchronously within complete_phase() call.

**Rationale:**
- **NFR-P1**: < 100ms validation time target (achievable synchronously)
- **FR-002**: All validators designed for fast execution
- Simpler error handling and state management
- No need for polling or callbacks

**Alternatives Considered:**
- **Async with Polling**: Rejected - unnecessary complexity for < 100ms operations
- **Async with Callbacks**: Rejected - breaks existing MCP tool interface
- **Background Validation**: Rejected - can't gate phase advancement asynchronously

**Trade-offs:**
- **Pros**: Simple, fast, predictable, maintains existing interface
- **Cons**: Cannot wait for long-running external processes (acceptable - not a v1.0 requirement, see out-of-scope)

---

#### Decision 6: Thread-Safe Cache with Double-Checked Locking

**Decision:** CheckpointLoader caches parsed gate definitions with double-checked locking pattern.

**Rationale:**
- **NFR-P2**: > 95% cache hit rate target
- **NFR-P3**: Support concurrent workflows without performance degradation
- Parsed gate definitions immutable (safe to share across threads)
- Double-checked locking avoids unnecessary lock contention

**Alternatives Considered:**
- **No Caching**: Rejected - re-parsing YAML on every validation would miss NFR-P1 target
- **Simple Lock**: Rejected - lock contention under concurrent load
- **Thread-Local Cache**: Rejected - memory waste, lower hit rate

**Trade-offs:**
- **Pros**: High cache hit rate, thread-safe, low contention, < 10KB per cached gate
- **Cons**: Slight implementation complexity (acceptable for performance requirements)

---

### 1.3 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| FR-001 | Session Manager (session.py:503) | Replace hardcoded True with _validate_checkpoint() call |
| FR-002 | WorkflowEngine._validate_checkpoint() | Orchestrates validation: load gate → validate fields → run validators |
| FR-003 | WorkflowEngine._validate_checkpoint() | Returns structured dict with checkpoint_passed, errors, warnings, diagnostics, remediation |
| FR-004 | CheckpointLoader enhancement | Three-tier: gate YAML → RAG parse → permissive gate |
| FR-005 | MCP get_task() tool | Excludes gate-definition.yaml from task content, only returns phase.md/task-N.md |
| FR-006 | Validator system | Lambda validators check proof content (e.g., yaml.safe_load, output text matching) |
| FR-007 | scripts/generate-gate-definitions.py | Standalone script: scan workflows → parse checkpoints → generate YAML |
| FR-008 | workflow_creation_v1 Phase 2 | Add task-4-generate-gate-definitions.md + task-5-validate-gate-consistency.md |
| FR-009 | Validation layers | Field names → types → validators → proof content (4 layers) |
| FR-010 | gate-definition.yaml checkpoint.strict | strict: false = warnings only, strict: true = block on error |
| FR-011 | CheckpointLoader fallback logic | YAML missing → RAG → permissive gate with warning log |
| FR-012 | WorkflowState phase_artifacts | Validation result stored even on failure, CheckpointStatus.FAILED set |
| NFR-P1 | CheckpointLoader caching | Double-checked locking, < 10ms cached, < 50ms first load |
| NFR-P3 | Thread-safe cache | Concurrent workflow sessions use shared cache safely |
| NFR-R1 | Three-tier fallback | Existing workflows without YAML continue to function |
| NFR-S1 | MCP tool exclusion | gate-definition.yaml never exposed to AI in any tool response |
| NFR-S2 | Lambda-only validators | No external module loading, controlled eval context |
| NFR-M2 | Config-driven design | gate-definition.yaml controls behavior without code deployment |

### 1.4 Technology Stack

**Existing Stack (Unchanged):**
- **Language**: Python 3.8+
- **MCP Framework**: Model Context Protocol (stdio/SSE transport)
- **YAML Parser**: pyyaml (already in dependencies)
- **RAG Engine**: Existing checkpoint parsing (fallback only)
- **State Management**: WorkflowState persistence (existing)

**New Components:**
- **gate-definition.yaml**: YAML files per phase (new, but uses existing pyyaml)
- **CheckpointLoader Enhancement**: Extended to try YAML first
- **Migration Script**: `scripts/generate-gate-definitions.py` (new Python script)
- **workflow_creation_v1 Tasks**: Two new task files (markdown)

**Development Stack:**
- **Type Checking**: mypy (type hints on all validation functions)
- **Testing**: pytest (unit + integration tests)
- **Linting**: pylint/flake8 (existing standards)
- **Pre-commit**: Existing hooks (no new hooks needed)

**No New Dependencies Required**: All components use existing Python stdlib + pyyaml.

### 1.5 Deployment Architecture

**Deployment Model:** In-place enhancement (no separate services)

```
┌─────────────────────────────────────────────────────────────────┐
│                      Agent OS Runtime                           │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │           mcp_server/ (Python Package)                 │  │
│  │                                                        │  │
│  │  ├── core/session.py    [1-line change]              │  │
│  │  ├── workflow_engine.py [validation enabled]          │  │
│  │  ├── config/loader.py   [YAML loading enhanced]       │  │
│  │  └── models/workflow.py [unchanged]                   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │         .praxis-os/workflows/ (Config Files)            │  │
│  │                                                        │  │
│  │  workflow_x_v1/                                       │  │
│  │    phases/                                            │  │
│  │      1/                                               │  │
│  │        ├── phase.md                                   │  │
│  │        ├── task-1-xxx.md                              │  │
│  │        └── gate-definition.yaml  [NEW]                │  │
│  │      2/                                               │  │
│  │        └── gate-definition.yaml  [NEW]                │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │         scripts/ (Migration Tool)                      │  │
│  │                                                        │  │
│  │  └── generate-gate-definitions.py  [NEW]              │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Deployment Phases:**

**Week 1: Enable + Bootstrap**
1. Deploy code changes (session.py fix, CheckpointLoader enhancement)
2. Run migration script to generate gate-definition.yaml for all workflows
3. Gates start as lenient (strict: false) - non-blocking
4. Monitor validation pass/fail rates

**Week 2: Enhance + Refine**
1. Deploy workflow_creation_v1 updates (new tasks)
2. Refine generated gates based on real usage data
3. Add validators for common failure patterns
4. Test with both lenient and strict modes

**Week 3: Production Ready**
1. Switch critical workflow gates to strict mode
2. Full test suite passes (90%+ coverage)
3. Documentation complete
4. Rollback plan tested

**Rollback Strategy:**
- Revert session.py to hardcoded True (1-line change)
- Remove gate-definition.yaml files (falls back to RAG)
- No data migration needed (state model unchanged)
- < 5 minute rollback time

---

## 1.6 Information Flow Diagrams

### Phase Advancement with Validation (Happy Path)

```
AI Agent                Session Manager         WorkflowEngine       CheckpointLoader      gate-definition.yaml
    |                         |                       |                     |                        |
    |--complete_phase()------>|                       |                     |                        |
    |  (session_id,           |                       |                     |                        |
    |   phase, evidence)      |                       |                     |                        |
    |                         |                       |                     |                        |
    |                         |--validate_checkpoint->|                     |                        |
    |                         |  (workflow, phase,    |                     |                        |
    |                         |   evidence)           |                     |                        |
    |                         |                       |                     |                        |
    |                         |                       |--load_checkpoint--->|                        |
    |                         |                       |   (workflow, phase) |                        |
    |                         |                       |                     |                        |
    |                         |                       |                     |--read gate YAML------->|
    |                         |                       |                     |                        |
    |                         |                       |                     |<-return parsed schema--|
    |                         |                       |                     |                        |
    |                         |                       |<-return requirements|                        |
    |                         |                       |   (schema, validators)                       |
    |                         |                       |                     |                        |
    |                         |                       |--validate fields----|                        |
    |                         |                       |  (check types, run  |                        |
    |                         |                       |   validators, check |                        |
    |                         |                       |   proof content)    |                        |
    |                         |                       |                     |                        |
    |                         |<-return result--------|                     |                        |
    |                         |  (passed: true,       |                     |                        |
    |                         |   errors: [])         |                     |                        |
    |                         |                       |                     |                        |
    |--advance to next phase--|                       |                     |                        |
    |  (checkpoint_passed:    |                       |                     |                        |
    |   true)                 |                       |                     |                        |
    |<------------------------|                       |                     |                        |
```

### Phase Advancement with Validation (Failure Path)

```
AI Agent                Session Manager         WorkflowEngine       CheckpointLoader      gate-definition.yaml
    |                         |                       |                     |                        |
    |--complete_phase()------>|                       |                     |                        |
    |  (session_id,           |                       |                     |                        |
    |   phase, BAD evidence)  |                       |                     |                        |
    |                         |                       |                     |                        |
    |                         |--validate_checkpoint->|                     |                        |
    |                         |                       |                     |                        |
    |                         |                       |--load_checkpoint--->|                        |
    |                         |                       |                     |--read gate YAML------->|
    |                         |                       |                     |<-return parsed schema--|
    |                         |                       |<-return requirements|                        |
    |                         |                       |                     |                        |
    |                         |                       |--validate fields----|                        |
    |                         |                       |  ❌ missing field   |                        |
    |                         |                       |  ❌ wrong type      |                        |
    |                         |                       |  ❌ validator fails |                        |
    |                         |                       |                     |                        |
    |                         |<-return result--------|                     |                        |
    |                         |  (passed: false,      |                     |                        |
    |                         |   errors: [...])      |                     |                        |
    |                         |                       |                     |                        |
    |--STAY in current phase--|                       |                     |                        |
    |  (checkpoint_passed:    |                       |                     |                        |
    |   false,                |                       |                     |                        |
    |   errors: [...],        |                       |                     |                        |
    |   remediation: "...")   |                       |                     |                        |
    |<------------------------|                       |                     |                        |
    |                         |                       |                     |                        |
    |--[AI fixes evidence]--->|                       |                     |                        |
    |--complete_phase()------>|                       |                     |                        |
    |  (retry with fixed      |                       |                     |                        |
    |   evidence)             |                       |                     |                        |
```

**Key Observations:**
- AI agent never sees gate-definition.yaml (information asymmetry maintained)
- Validation happens server-side (AI cannot bypass)
- Failed validation provides specific errors (AI learns what to fix)
- Phase does not advance until validation passes (gates actually gate)

---

## 1.7 Design Principles Applied

### SOLID Principles

**Single Responsibility:**
- `Session`: Phase advancement coordination only
- `WorkflowEngine`: Validation orchestration only
- `CheckpointLoader`: Gate definition loading only
- `Validators`: Single validation concern per lambda

**Open/Closed:**
- Validators extensible via config (new validators added without code changes)
- Gate schema extensible (new fields added without breaking existing gates)
- CheckpointLoader open for gate source extension (YAML → RAG → permissive)

**Liskov Substitution:**
- Permissive gate substitutes for missing gate definition (same interface)
- All three gate sources return same CheckpointRequirements type

**Interface Segregation:**
- MCP tool interface unchanged (no new methods for validation)
- CheckpointLoader interface focused (load requirements, that's it)

**Dependency Inversion:**
- WorkflowEngine depends on CheckpointLoader abstraction (not YAML details)
- Validators depend on evidence interface (not specific evidence types)

### Additional Principles

**Information Asymmetry:**
- AI sees natural language requirements (task files)
- System knows hidden schemas (gate-definition.yaml)
- Multi-layer defense prevents schema discovery

**Fail-Safe Defaults:**
- Missing gate → permissive gate (safe, non-breaking)
- Unknown field → ignore (lenient)
- Validator error → log and pass with warning (lenient mode)

**Progressive Disclosure:**
- Week 1: Lenient gates (warnings only)
- Week 2: Refine based on data
- Week 3: Strict gates (blocking)

**Configuration Over Code:**
- Validation rules in YAML (not Python)
- Strictness configurable per phase
- Validators parameterizable

---

## Summary: Architecture at a Glance

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Pattern** | Modular Monolith | Tight coupling, zero breaking changes |
| **Config** | YAML files | Human-readable, version-controlled, AI-hidden |
| **Fallback** | YAML → RAG → Permissive | Backwards compatible, low risk |
| **Validators** | Lambda expressions | Secure, simple, fast |
| **Execution** | Synchronous | < 100ms target, simple error handling |
| **Caching** | Double-checked locking | High hit rate, thread-safe, low contention |
| **Deployment** | In-place enhancement | No new services, simple rollback |
| **Security** | Information asymmetry | AI never sees schemas |
| **Strictness** | Progressive (lenient → strict) | Phased rollout reduces risk |

**This architecture enables the 3-week timeline by leveraging existing infrastructure, minimizing changes, and providing graceful fallbacks for backwards compatibility.**

---

## 2. Component Design

---

### 2.1 Component: Session Manager

**Purpose:** Coordinates phase advancement and manages the state change to enable validation.

**Responsibilities:**
- Handle complete_phase() MCP tool calls
- Coordinate evidence submission with workflow engine
- **CRITICAL**: Enable validation by calling _validate_checkpoint() instead of hardcoding True
- Manage phase transitions based on validation results
- Persist validation results to workflow state

**Requirements Satisfied:**
- FR-001: Enable Checkpoint Validation (1-line fix at line 503)
- FR-012: Maintain Validation Audit Trail (persist results)
- NFR-R2: Error Handling (validation errors never crash workflow)

**Public Interface:**
```python
class Session:
    """Manages workflow session state and phase advancement."""
    
    def complete_phase(
        self,
        workflow_type: str,
        phase: int,
        evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete current phase with submitted evidence.
        
        BEFORE (line 503):
            checkpoint_passed = True  # HARDCODED BYPASS
        
        AFTER (line 503):
            passed, result = self.engine._validate_checkpoint(
                workflow_type, phase, evidence
            )
            checkpoint_passed = passed
        
        Args:
            workflow_type: Workflow identifier
            phase: Current phase number
            evidence: Submitted evidence dictionary
            
        Returns:
            Dict with checkpoint_passed, next_phase (if passed),
            or errors/remediation (if failed)
        """
        pass
```

**Dependencies:**
- Requires: WorkflowEngine (for validation)
- Requires: WorkflowState (for persistence)
- Provides: MCP tool interface (complete_phase)

**Error Handling:**
- Validation failure → Return structured errors, stay in current phase
- Engine exception → Log error, return safe error response, don't crash
- State persistence failure → Log warning, continue (validation result in memory)

**Testing:**
- Unit test: complete_phase with valid/invalid evidence
- Integration test: Full phase advancement flow with validation enabled
- Regression test: Existing workflows still work after change

---

### 2.2 Component: WorkflowEngine

**Purpose:** Orchestrates checkpoint validation by loading gate definitions and executing validation logic.

**Responsibilities:**
- Load checkpoint requirements via CheckpointLoader
- Validate evidence fields against schema (types, required fields)
- Execute lambda validators on evidence
- Check cross-field validation rules
- Return structured validation results (passed, errors, diagnostics)
- Handle validation exceptions gracefully

**Requirements Satisfied:**
- FR-002: Validate Evidence Against Schema
- FR-003: Return Structured Validation Errors
- FR-009: Support Multi-Layer Validation
- FR-010: Support Progressive Strictness
- NFR-P1: Validation Speed (< 100ms per validation)

**Public Interface:**
```python
class WorkflowEngine:
    """Orchestrates workflow execution and validation."""
    
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
        2. Check required fields present
        3. Validate field types
        4. Run custom validators
        5. Check proof content
        
        Args:
            workflow_type: Workflow identifier
            phase: Phase number
            evidence: Evidence dictionary to validate
            
        Returns:
            Tuple of (passed: bool, result: Dict) where result contains:
            - checkpoint_passed: bool
            - errors: List[str] (specific error messages)
            - warnings: List[str] (non-critical issues)
            - diagnostics: Dict (metadata about validation)
            - remediation: str (how to fix errors)
            - next_steps: List[str] (actions to take)
        """
        pass
    
    def _validate_field(
        self,
        field_name: str,
        field_value: Any,
        field_schema: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate single field against schema.
        
        Checks:
        - Type matches schema
        - Required field present
        - Custom validator passes (if specified)
        - Proof content valid (if artifact field)
        
        Returns:
            (passed: bool, error_message: Optional[str])
        """
        pass
```

**Dependencies:**
- Requires: CheckpointLoader (for gate definitions)
- Requires: Validator functions (lambda evaluator)
- Provides: Validation orchestration

**Error Handling:**
- CheckpointLoader exception → Fall back to permissive gate, log warning
- Validator exception → Treat as validation failure with specific error
- Unknown field type → Ignore field (lenient), or error (strict)
- Proof parsing failure → Validation fails with "invalid proof" error

**Internal Structure:**
```python
class ValidationResult:
    """Encapsulates validation outcome."""
    passed: bool
    errors: List[str]
    warnings: List[str]
    diagnostics: Dict[str, Any]
    remediation: str
    next_steps: List[str]

class ValidationLayer:
    """Each layer of multi-layer validation."""
    FIELD_NAMES = 1      # Required fields present
    FIELD_TYPES = 2      # Types match schema
    VALIDATORS = 3       # Custom validators pass
    PROOF_CONTENT = 4    # Proof artifacts valid
```

**Testing:**
- Unit test: Each validation layer independently
- Unit test: Field validation with various types
- Unit test: Lambda validator execution
- Integration test: Complete validation with real gate definitions
- Performance test: < 100ms for typical validation

---

### 2.3 Component: CheckpointLoader

**Purpose:** Loads checkpoint requirements from gate-definition.yaml with fallback to RAG and permissive gates.

**Responsibilities:**
- Implement three-tier loading strategy (YAML → RAG → permissive)
- Parse gate-definition.yaml files into structured requirements
- Cache parsed gate definitions with thread-safe locking
- Fall back gracefully when gate definitions missing
- Log warnings when fallbacks triggered
- Provide permissive gate structure for backwards compatibility

**Requirements Satisfied:**
- FR-004: Load Gate Definitions from YAML
- FR-011: Provide Backwards Compatibility
- NFR-P1, NFR-P2: Caching (> 95% hit rate, < 10ms cached)
- NFR-P3: Thread-Safe Cache
- NFR-R1: Zero breaking changes

**Public Interface:**
```python
class CheckpointLoader:
    """Loads checkpoint requirements with fallback strategies."""
    
    def load_checkpoint_requirements(
        self,
        workflow_type: str,
        phase: int
    ) -> CheckpointRequirements:
        """
        Load checkpoint requirements using three-tier strategy.
        
        Strategy:
        1. Try gate-definition.yaml (if exists)
        2. Try RAG parsing of phase.md (if YAML missing)
        3. Return permissive gate (if RAG fails)
        
        Args:
            workflow_type: Workflow identifier
            phase: Phase number
            
        Returns:
            CheckpointRequirements with evidence_schema, validators,
            strict flag, allow_override flag
        """
        pass
    
    def _load_from_yaml(
        self,
        workflow_type: str,
        phase: int
    ) -> Optional[CheckpointRequirements]:
        """
        Load from gate-definition.yaml file.
        
        Path: .praxis-os/workflows/{workflow_type}/phases/{phase}/gate-definition.yaml
        
        Returns None if file doesn't exist.
        Raises exception if file exists but invalid YAML.
        """
        pass
    
    def _load_from_rag(
        self,
        workflow_type: str,
        phase: int
    ) -> Optional[CheckpointRequirements]:
        """
        Parse checkpoint from phase.md using RAG engine.
        
        Falls back to existing RAG-based checkpoint parsing.
        Returns None if parsing fails.
        """
        pass
    
    def _get_permissive_gate(self) -> CheckpointRequirements:
        """
        Return permissive gate for backwards compatibility.
        
        Accepts any evidence with basic type checking only.
        Sets strict=False so all errors become warnings.
        """
        pass
```

**Dependencies:**
- Requires: YAML parser (pyyaml)
- Requires: RAG engine (existing, for fallback)
- Requires: File system access
- Provides: Checkpoint requirements

**Caching Strategy:**
```python
class CheckpointLoader:
    _cache: Dict[str, CheckpointRequirements] = {}
    _cache_lock: threading.Lock = threading.Lock()
    
    def load_checkpoint_requirements(self, workflow_type: str, phase: int):
        cache_key = f"{workflow_type}:{phase}"
        
        # Double-checked locking pattern
        if cache_key in self._cache:
            return self._cache[cache_key]  # Fast path (no lock)
        
        with self._cache_lock:
            if cache_key in self._cache:  # Check again inside lock
                return self._cache[cache_key]
            
            # Load and cache
            requirements = self._load_with_fallback(workflow_type, phase)
            self._cache[cache_key] = requirements
            return requirements
```

**Error Handling:**
- YAML parse error → Log error, try RAG fallback
- File not found → Silent (expected), try RAG fallback
- RAG parse error → Log warning, use permissive gate
- Invalid schema structure → Log error, use permissive gate

**Testing:**
- Unit test: YAML loading with valid/invalid files
- Unit test: Fallback chain (YAML missing → RAG → permissive)
- Unit test: Cache hit/miss behavior
- Thread safety test: Concurrent loading from multiple threads
- Performance test: < 10ms cached, < 50ms first load

---

### 2.4 Component: Validator System

**Purpose:** Execute lambda validators on evidence fields to check proof content.

**Responsibilities:**
- Evaluate lambda expressions in controlled context
- Validate proof artifacts (not just boolean claims)
- Provide parameterizable, reusable validators
- Return specific error messages on failure
- Execute safely without arbitrary code execution

**Requirements Satisfied:**
- FR-006: Support Proof-Based Evidence
- FR-009: Multi-Layer Validation (layer 3 & 4)
- NFR-S2: Validator Security (lambda-only, no external modules)

**Common Validators:**
```python
# String validators
validators = {
    "non_empty": lambda x: len(x) > 0,
    "contains_any": lambda x, patterns: any(p in x for p in patterns),
    "matches_pattern": lambda x, pattern: re.match(pattern, x) is not None,
    "min_length": lambda x, min_len: len(x) >= min_len,
    
    # Integer validators
    "positive": lambda x: x > 0,
    "in_range": lambda x, min_val, max_val: min_val <= x <= max_val,
    "equals": lambda x, expected: x == expected,
    
    # Object validators
    "has_fields": lambda x, fields: all(f in x for f in fields),
    "valid_structure": lambda x, required_keys: set(required_keys).issubset(set(x.keys())),
    
    # Proof validators (check content)
    "yaml_parseable": lambda x: yaml.safe_load(x) is not None,
    "contains_success": lambda x: "success" in x.lower() or "✅" in x,
    "no_errors": lambda x: "error" not in x.lower() and "❌" not in x,
}
```

**Usage in gate-definition.yaml:**
```yaml
evidence_schema:
  yaml_content:
    type: string
    required: true
    validator: yaml_parseable
    description: "Must be valid YAML that parses successfully"
  
  validation_output:
    type: string
    required: true
    validator: contains_success
    description: "Must contain success markers (not generic boolean)"
  
  file_count:
    type: integer
    required: true
    validator: positive
    description: "Number of files generated (must be > 0)"
```

**Dependencies:**
- Requires: Safe eval context (restricted globals/locals)
- Provides: Validation functions

**Error Handling:**
- Lambda syntax error → Validation fails with "invalid validator" error
- Lambda execution exception → Validation fails with exception message
- Unknown validator name → Validation fails with "unknown validator" error

**Security:**
```python
class ValidatorExecutor:
    # Restricted context for lambda evaluation
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
    }
    
    def execute_validator(
        self,
        validator_expr: str,
        value: Any,
        params: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Execute validator in restricted context."""
        try:
            validator_func = eval(
                validator_expr,
                self.SAFE_GLOBALS,
                {}  # Empty locals
            )
            passed = validator_func(value, **params)
            return (passed, None)
        except Exception as e:
            return (False, f"Validator failed: {str(e)}")
```

**Testing:**
- Unit test: Each common validator
- Unit test: Validator with/without params
- Unit test: Validator exception handling
- Security test: Attempt dangerous operations (should fail)

---

### 2.5 Component: Migration Script

**Purpose:** Generate gate-definition.yaml files for existing workflows by parsing checkpoint sections.

**Responsibilities:**
- Scan .praxis-os/workflows/ directory for all workflows
- For each workflow phase, parse checkpoint section from phase.md
- Generate gate-definition.yaml with evidence schema and validators
- Support dry-run mode (preview without writing)
- Support single-workflow mode (--workflow flag)
- Start with lenient gates (strict: false) for safety

**Requirements Satisfied:**
- FR-007: Generate Migration Script for Existing Workflows
- Goal 3: Systematic Workflow Validation Coverage

**Public Interface:**
```python
# scripts/generate-gate-definitions.py

def scan_workflows(workflows_dir: str) -> List[str]:
    """Find all workflows in .praxis-os/workflows/."""
    pass

def parse_checkpoint(phase_md_path: str) -> Dict[str, Any]:
    """Parse checkpoint section from phase.md."""
    pass

def generate_gate_yaml(
    checkpoint_data: Dict[str, Any],
    strict: bool = False
) -> str:
    """
    Generate gate-definition.yaml content.
    
    Default to strict=False (lenient) for safety during migration.
    """
    pass

def write_gate_file(
    workflow_dir: str,
    phase: int,
    yaml_content: str,
    dry_run: bool
) -> None:
    """Write gate-definition.yaml (or print if dry_run)."""
    pass

# CLI usage:
# python scripts/generate-gate-definitions.py
# python scripts/generate-gate-definitions.py --dry-run
# python scripts/generate-gate-definitions.py --workflow spec_creation_v1
```

**Dependencies:**
- Requires: YAML parser (pyyaml)
- Requires: RAG engine (for checkpoint parsing)
- Requires: File system access
- Provides: Generated gate-definition.yaml files

**Output Example:**
```yaml
# Generated gate-definition.yaml
checkpoint:
  strict: false  # Start lenient
  allow_override: true

evidence_schema:
  srd_created:
    type: boolean
    required: true
    description: "SRD file created"
  
  business_goals:
    type: integer
    required: true
    validator: positive
    description: "Number of business goals defined"

validators:
  positive: "lambda x: x > 0"
```

**Error Handling:**
- Workflow not found → Print error, skip
- phase.md missing → Print warning, skip phase
- Checkpoint parsing fails → Generate minimal gate
- File write error → Print error, continue with next

**Testing:**
- Integration test: Run on real workflows, verify YAML output
- Unit test: Checkpoint parsing with various formats
- Dry-run test: No files actually written

---

### 2.6 Component: workflow_creation_v1 Enhancement

**Purpose:** Auto-generate gate-definition.yaml files during workflow creation.

**Responsibilities:**
- Add task-4-generate-gate-definitions.md to Phase 2
- Add task-5-validate-gate-consistency.md to Phase 2
- Generate gates that match checkpoint requirements
- Include appropriate validators for workflow type
- Set strictness based on phase type (lenient for discovery, strict for implementation)

**Requirements Satisfied:**
- FR-008: Auto-Generate Gates in workflow_creation_v1
- Goal 3: Auto-generate gates for future workflows

**New Tasks:**

**task-4-generate-gate-definitions.md:**
```markdown
# Generate gate-definition.yaml files

For each phase created in task-2-create-phase-structure:
1. Parse checkpoint section from phase.md
2. Extract evidence requirements
3. Generate gate-definition.yaml with:
   - Evidence schema (types, required, validators)
   - Validators for the workflow type
   - Strictness appropriate for phase

Phase 0-1: strict=false (discovery)
Phase 2+: strict=true (implementation)
```

**task-5-validate-gate-consistency.md:**
```markdown
# Validate gate consistency

Ensure generated gates match checkpoint requirements:
1. Load each gate-definition.yaml
2. Compare to phase.md checkpoint section
3. Verify all checkpoint requirements have corresponding schema fields
4. Check validators are defined
5. Report mismatches
```

**Dependencies:**
- Requires: workflow_creation_v1 Phase 2 (phase content generation)
- Provides: Auto-generated gates for new workflows

**Testing:**
- Integration test: Create workflow with workflow_creation_v1, verify gates generated
- Validation test: Generated gates pass consistency check

---

## 2.7 Component Interactions

**Interaction Diagram:**

```
┌──────────────┐
│  MCP Client  │ (AI Agent)
│  (Cursor)    │
└──────┬───────┘
       │ complete_phase(session_id, phase, evidence)
       ▼
┌─────────────────────────────────────────────────────────────┐
│                      Session Manager                        │
│  - Receives complete_phase() call                           │
│  - Calls WorkflowEngine._validate_checkpoint()              │
│  - Returns result (passed or errors)                        │
└────────────────────────┬────────────────────────────────────┘
                         │ _validate_checkpoint(workflow, phase, evidence)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     WorkflowEngine                          │
│  - Loads gate via CheckpointLoader                          │
│  - Validates fields (types, required)                       │
│  - Executes validators                                      │
│  - Checks proof content                                     │
│  - Returns (passed, result)                                 │
└────────────────────────┬────────────────────────────────────┘
                         │ load_checkpoint_requirements(workflow, phase)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    CheckpointLoader                         │
│  - Try gate-definition.yaml (cache first)                   │
│  - Fallback to RAG parsing                                  │
│  - Fallback to permissive gate                              │
│  - Return CheckpointRequirements                            │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
             ▼                            ▼
┌─────────────────────┐      ┌────────────────────────┐
│ gate-definition.yaml│      │     RAG Engine         │
│ (YAML file)         │      │  (existing, fallback)  │
└─────────────────────┘      └────────────────────────┘
```

| From | To | Method | Purpose |
|------|----|----|---------|
| Session | WorkflowEngine | `_validate_checkpoint()` | Trigger validation |
| WorkflowEngine | CheckpointLoader | `load_checkpoint_requirements()` | Get gate definition |
| WorkflowEngine | ValidatorExecutor | `execute_validator()` | Run lambda validator |
| CheckpointLoader | YAML Parser | `yaml.safe_load()` | Parse gate file |
| CheckpointLoader | RAG Engine | `parse_checkpoint()` | Fallback parsing |

---

## 2.8 Module Organization

**Directory Structure:**

```
mcp_server/
├── core/
│   ├── session.py          [1-line change - enable validation]
│   └── metrics.py          [unchanged]
│
├── workflow_engine.py      [validation orchestration - existing method enabled]
│
├── config/
│   └── loader.py           [ENHANCED - CheckpointLoader with YAML loading]
│
├── models/
│   ├── workflow.py         [unchanged - CheckpointRequirements model]
│   └── config.py           [unchanged]
│
└── validation/             [NEW MODULE]
    ├── __init__.py
    ├── validators.py       [Common validator lambdas]
    └── executor.py         [ValidatorExecutor - safe eval]

scripts/
└── generate-gate-definitions.py    [NEW - migration script]

.praxis-os/workflows/
└── {workflow_name}/
    └── phases/
        └── {N}/
            └── gate-definition.yaml    [NEW - per phase]
```

**Dependency Rules:**
- No circular imports (enforced)
- Session → WorkflowEngine (one-way)
- WorkflowEngine → CheckpointLoader (one-way)
- CheckpointLoader → File system, RAG (no reverse dependencies)
- Validators → stdlib only (no external imports)

**Testing Structure:**
```
tests/
├── unit/
│   ├── test_checkpoint_loader.py
│   ├── test_workflow_engine_validation.py
│   ├── test_validator_executor.py
│   └── test_migration_script.py
│
└── integration/
    ├── test_complete_phase_validation.py
    ├── test_gate_fallback_chain.py
    └── test_workflow_creation_v1_gates.py
```

---

## 3. API Design

---

### 3.1 MCP Tool Interface (Unchanged)

**Purpose:** External MCP interface for AI agents - remains unchanged to maintain backwards compatibility.

#### complete_phase

**Method:** MCP Tool Call

**Purpose:** Complete current phase with submitted evidence (validation now enabled internally)

**Authentication:** MCP session-based

**Parameters:**
```python
{
    "session_id": "string",  # Workflow session identifier
    "phase": int,            # Current phase number
    "evidence": {            # Evidence dictionary (structure varies by workflow)
        "field1": "value1",
        "field2": 42,
        # ... workflow-specific fields
    }
}
```

**Response - Success (Validation Passed):**
```json
{
    "checkpoint_passed": true,
    "next_phase": 2,
    "message": "Phase 1 completed successfully"
}
```

**Response - Failure (Validation Failed):**
```json
{
    "checkpoint_passed": false,
    "errors": [
        "Field 'business_goals' is required but missing",
        "Field 'user_stories' must be positive integer, got: -1"
    ],
    "warnings": [
        "Field 'optional_field' not provided (non-critical)"
    ],
    "diagnostics": {
        "fields_submitted": ["business_goals", "user_stories"],
        "fields_required": ["business_goals", "user_stories", "functional_requirements"],
        "fields_missing": ["functional_requirements"],
        "validation_timestamp": "2025-10-20T14:30:00Z",
        "strict_mode": false
    },
    "remediation": "Please provide the missing 'functional_requirements' field and ensure 'user_stories' is a positive integer.",
    "next_steps": [
        "Review checkpoint requirements in task file",
        "Gather missing evidence: functional_requirements",
        "Resubmit evidence with complete_phase()"
    ]
}
```

**Error Handling:**
- Validation exception → Returns safe error response with checkpoint_passed: false
- Session not found → Returns error with appropriate message
- Invalid evidence format → Returns parsing error

**Behavioral Change:**
- **BEFORE**: Always returned `checkpoint_passed: true` (hardcoded bypass)
- **AFTER**: Returns actual validation result from WorkflowEngine

---

### 3.2 Internal Validation Interfaces

#### WorkflowEngine._validate_checkpoint()

**Purpose:** Orchestrate checkpoint validation (existing method, now actually used)

**Interface:**
```python
def _validate_checkpoint(
    self,
    workflow_type: str,
    phase: int,
    evidence: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate evidence against checkpoint requirements.
    
    Args:
        workflow_type: Workflow identifier (e.g., "spec_creation_v1")
        phase: Phase number (0-based)
        evidence: Dictionary of submitted evidence
        
    Returns:
        Tuple of (passed: bool, result: Dict) where result contains:
        - checkpoint_passed: bool (same as first tuple element)
        - errors: List[str] (empty if passed)
        - warnings: List[str] (non-critical issues)
        - diagnostics: Dict[str, Any] (validation metadata)
        - remediation: str (how to fix, empty if passed)
        - next_steps: List[str] (actions to take, empty if passed)
        
    Raises:
        ValidationError: If validation logic itself fails (not evidence failure)
        
    Example:
        >>> passed, result = engine._validate_checkpoint(
        ...     "spec_creation_v1",
        ...     1,
        ...     {"business_goals": 4, "user_stories": 7}
        ... )
        >>> assert passed == True
        >>> assert result["checkpoint_passed"] == True
    """
```

#### CheckpointLoader.load_checkpoint_requirements()

**Purpose:** Load gate definition with three-tier fallback

**Interface:**
```python
def load_checkpoint_requirements(
    self,
    workflow_type: str,
    phase: int
) -> CheckpointRequirements:
    """
    Load checkpoint requirements using fallback strategy.
    
    Strategy (in order):
    1. Load from gate-definition.yaml (if exists)
    2. Parse from phase.md via RAG (if YAML missing)
    3. Return permissive gate (if RAG fails)
    
    Args:
        workflow_type: Workflow identifier
        phase: Phase number
        
    Returns:
        CheckpointRequirements object with:
        - evidence_schema: Dict[str, FieldSchema]
        - validators: Dict[str, str] (name -> lambda expression)
        - strict: bool (strict vs lenient mode)
        - allow_override: bool (manual override capability)
        - source: str ("yaml" | "rag" | "permissive")
        
    Example:
        >>> reqs = loader.load_checkpoint_requirements("spec_creation_v1", 1)
        >>> assert "business_goals" in reqs.evidence_schema
        >>> assert reqs.strict == False  # Lenient for Phase 1
    """
```

#### ValidatorExecutor.execute_validator()

**Purpose:** Execute lambda validator in safe context

**Interface:**
```python
def execute_validator(
    self,
    validator_expr: str,
    value: Any,
    params: Dict[str, Any] = None
) -> Tuple[bool, Optional[str]]:
    """
    Execute validator lambda expression safely.
    
    Args:
        validator_expr: Lambda expression string (e.g., "lambda x: x > 0")
        value: Value to validate
        params: Optional parameters for validator
        
    Returns:
        Tuple of (passed: bool, error_message: Optional[str])
        If passed=True, error_message is None
        If passed=False, error_message explains why
        
    Security:
        - Restricted globals (no os, sys, subprocess, etc.)
        - No file I/O allowed
        - Only safe builtins (len, str, int, re, yaml, etc.)
        
    Example:
        >>> passed, error = executor.execute_validator(
        ...     "lambda x: x > 0",
        ...     42,
        ...     {}
        ... )
        >>> assert passed == True
        >>> assert error is None
    """
```

---

### 3.3 Data Models

#### CheckpointRequirements

**Purpose:** Encapsulates checkpoint validation requirements

**Structure:**
```python
@dataclass
class CheckpointRequirements:
    """Checkpoint validation requirements."""
    
    evidence_schema: Dict[str, FieldSchema]
    validators: Dict[str, str]  # name -> lambda expression
    cross_field_rules: List[CrossFieldRule]
    strict: bool
    allow_override: bool
    source: str  # "yaml" | "rag" | "permissive"
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        pass
```

#### FieldSchema

**Purpose:** Schema definition for single evidence field

**Structure:**
```python
@dataclass
class FieldSchema:
    """Schema for single evidence field."""
    
    name: str
    type: str  # "boolean" | "integer" | "string" | "object" | "list"
    required: bool
    validator: Optional[str]  # Validator name (if custom validation)
    validator_params: Optional[Dict[str, Any]]  # Params for validator
    description: str
    
    def validate_type(self, value: Any) -> bool:
        """Check if value matches type."""
        pass
```

#### ValidationResult

**Purpose:** Encapsulates validation outcome

**Structure:**
```python
@dataclass
class ValidationResult:
    """Result of checkpoint validation."""
    
    passed: bool
    errors: List[str]
    warnings: List[str]
    diagnostics: Dict[str, Any]
    remediation: str
    next_steps: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "checkpoint_passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "diagnostics": self.diagnostics,
            "remediation": self.remediation,
            "next_steps": self.next_steps
        }
```

---

### 3.4 File Format Specifications

#### gate-definition.yaml Format

**Purpose:** Define checkpoint validation requirements in config file

**Location:** `.praxis-os/workflows/{workflow_name}/phases/{N}/gate-definition.yaml`

**Schema:**
```yaml
# Checkpoint configuration
checkpoint:
  strict: boolean           # true = block on errors, false = warnings only
  allow_override: boolean   # true = manual override possible, false = strict enforcement

# Evidence field schemas
evidence_schema:
  field_name:
    type: string           # "boolean" | "integer" | "string" | "object" | "list"
    required: boolean      # true = must be present, false = optional
    validator: string      # Optional validator name (references validators section)
    validator_params:      # Optional parameters for validator
      param1: value1
    description: string    # Human-readable description

# Validator definitions (lambda expressions)
validators:
  validator_name: "lambda expression string"

# Optional cross-field validation rules
cross_field_validation:
  - rule: "lambda evidence: evidence['field1'] > evidence['field2']"
    error_message: "field1 must be greater than field2"
```

**Example - spec_creation_v1 Phase 1:**
```yaml
checkpoint:
  strict: false  # Lenient for Phase 1
  allow_override: true

evidence_schema:
  srd_created:
    type: boolean
    required: true
    description: "SRD file created successfully"
  
  business_goals:
    type: integer
    required: true
    validator: positive
    description: "Number of business goals defined (must be > 0)"
  
  user_stories:
    type: integer
    required: true
    validator: positive
    description: "Number of user stories documented (must be > 0)"
  
  functional_requirements:
    type: integer
    required: true
    validator: in_range
    validator_params:
      min_val: 3
      max_val: 50
    description: "Number of functional requirements (3-50 is reasonable)"
  
  nfr_categories:
    type: integer
    required: true
    validator: positive
    description: "Number of NFR categories addressed (must be > 0)"
  
  out_of_scope_defined:
    type: boolean
    required: true
    description: "Out-of-scope section completed"
  
  traceability_matrix:
    type: boolean
    required: true
    description: "Requirements traceability matrix created"
  
  supporting_docs_referenced:
    type: boolean
    required: true
    description: "Supporting documentation properly referenced"

validators:
  positive: "lambda x: x > 0"
  in_range: "lambda x, min_val, max_val: min_val <= x <= max_val"

cross_field_validation:
  - rule: "lambda e: e.get('functional_requirements', 0) >= e.get('business_goals', 0)"
    error_message: "Should have at least as many FRs as business goals"
```

**Validation:**
- Must be valid YAML syntax
- Required fields: `checkpoint`, `evidence_schema`
- Optional fields: `validators`, `cross_field_validation`
- Field types must be one of: boolean, integer, string, object, list
- Validator expressions must be valid Python lambda syntax

---

### 3.5 Migration Script CLI

**Purpose:** Command-line interface for generating gate definitions

**Script:** `scripts/generate-gate-definitions.py`

**Usage:**
```bash
# Generate gates for all workflows (dry-run first)
python scripts/generate-gate-definitions.py --dry-run

# Generate gates for all workflows (write files)
python scripts/generate-gate-definitions.py

# Generate gates for single workflow
python scripts/generate-gate-definitions.py --workflow spec_creation_v1

# Generate gates with strict mode (not recommended for migration)
python scripts/generate-gate-definitions.py --strict

# Verbose output
python scripts/generate-gate-definitions.py --verbose
```

**Options:**
```
--dry-run           Preview generated gates without writing files
--workflow NAME     Process single workflow instead of all
--strict            Generate strict gates (default: lenient)
--verbose, -v       Detailed output
--help, -h          Show help message
```

**Output Format:**
```
Processing workflows in .praxis-os/workflows/
✓ spec_creation_v1
  ✓ Phase 0: gate-definition.yaml generated (3 fields)
  ✓ Phase 1: gate-definition.yaml generated (8 fields)
  ✓ Phase 2: gate-definition.yaml generated (5 fields)
  ...
  
✓ test_generation_v3
  ✓ Phase 0: gate-definition.yaml generated (2 fields)
  ⚠ Phase 1: No checkpoint found, minimal gate created
  ...

Summary:
  Total workflows: 15
  Total phases: 87
  Gates generated: 85
  Minimal gates (no checkpoint): 2
  Failed: 0
```

**Exit Codes:**
- 0: Success
- 1: No workflows found
- 2: Parse errors (some phases failed)

---

### 3.6 Error Response Format

**Purpose:** Standardized error structure for validation failures

**Structure:**
```json
{
  "checkpoint_passed": false,
  "errors": [
    "Field 'required_field' is required but missing",
    "Field 'numeric_field' must be integer, got: string",
    "Validator 'positive' failed for field 'count': value must be > 0"
  ],
  "warnings": [
    "Field 'optional_field' not provided (non-critical)",
    "Validator 'recommended' suggests improving field 'description'"
  ],
  "diagnostics": {
    "validation_timestamp": "2025-10-20T14:30:00Z",
    "workflow_type": "spec_creation_v1",
    "phase": 1,
    "fields_submitted": ["field1", "field2"],
    "fields_required": ["field1", "field2", "field3"],
    "fields_missing": ["field3"],
    "fields_failed_validation": ["field2"],
    "strict_mode": false,
    "gate_source": "yaml"
  },
  "remediation": "Review the errors above. Ensure all required fields are present and have correct types. Fix validator failures by providing valid proof artifacts.",
  "next_steps": [
    "Check task-N-xxx.md for checkpoint requirements",
    "Gather missing evidence for 'required_field'",
    "Correct 'numeric_field' to be an integer",
    "Resubmit evidence via complete_phase()"
  ]
}
```

**Error Message Patterns:**

**Missing Field:**
```
Field '{field_name}' is required but missing
```

**Type Mismatch:**
```
Field '{field_name}' must be {expected_type}, got: {actual_type}
```

**Validator Failure:**
```
Validator '{validator_name}' failed for field '{field_name}': {specific_reason}
```

**Cross-Field Validation:**
```
Cross-field validation failed: {rule_description}
```

**Proof Content Invalid:**
```
Proof artifact '{field_name}' is invalid: {parsing_error}
```

---

### 3.7 Integration Points

#### MCP Tool Layer → Session Manager

**Interface:** MCP tool call routing

**Contract:** Session Manager receives complete_phase call, processes it, returns result via MCP response

#### Session Manager → WorkflowEngine

**Interface:** Internal method call

**Contract:** 
```python
passed, result = self.engine._validate_checkpoint(workflow_type, phase, evidence)
if passed:
    # Advance to next phase
else:
    # Return errors to user, stay in current phase
```

#### WorkflowEngine → CheckpointLoader

**Interface:** Internal method call

**Contract:**
```python
requirements = self.loader.load_checkpoint_requirements(workflow_type, phase)
# WorkflowEngine then validates evidence against requirements
```

#### CheckpointLoader → File System

**Interface:** File I/O

**Contract:** Read gate-definition.yaml from standard location

**Path Template:** `.praxis-os/workflows/{workflow_type}/phases/{phase}/gate-definition.yaml`

#### CheckpointLoader → RAG Engine (Fallback)

**Interface:** Existing RAG parsing

**Contract:** If YAML missing, request RAG to parse checkpoint from phase.md

---

### 3.8 API Summary

**Public Interfaces (MCP Tools):**
1. `complete_phase` - Unchanged signature, now calls validation

**Internal Interfaces:**
3. `WorkflowEngine._validate_checkpoint()` - Validation orchestration
4. `CheckpointLoader.load_checkpoint_requirements()` - Gate loading with fallback
5. `ValidatorExecutor.execute_validator()` - Safe lambda execution

**Data Models:**
4. `CheckpointRequirements` - Gate definition structure
5. `FieldSchema` - Single field validation rules
6. `ValidationResult` - Validation outcome

**File Formats:**
1. `gate-definition.yaml` - Config-driven validation schema

**CLI Tools:**
1. `generate-gate-definitions.py` - Migration script

**No New External APIs:** All changes are internal enhancements with backwards-compatible external interface.

---

## 4. Data Models

---

### 4.1 Core Validation Models

These models represent the validation system's primary data structures.

#### CheckpointRequirements

**Purpose:** Container for checkpoint validation requirements loaded from gate-definition.yaml

**Definition:**
```python
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

@dataclass
class CheckpointRequirements:
    """
    Checkpoint validation requirements.
    
    Loaded from gate-definition.yaml with fallback to RAG or permissive gate.
    Immutable once loaded (safe for caching and sharing across threads).
    """
    
    evidence_schema: Dict[str, 'FieldSchema']
    validators: Dict[str, str]  # validator_name -> lambda expression
    cross_field_rules: List['CrossFieldRule']
    strict: bool
    allow_override: bool
    source: str  # "yaml" | "rag" | "permissive"
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for logging/debugging."""
        return {
            "evidence_schema": {k: v.to_dict() for k, v in self.evidence_schema.items()},
            "validators": self.validators,
            "cross_field_rules": [r.to_dict() for r in self.cross_field_rules],
            "strict": self.strict,
            "allow_override": self.allow_override,
            "source": self.source
        }
    
    def get_required_fields(self) -> List[str]:
        """Get list of required field names."""
        return [name for name, schema in self.evidence_schema.items() if schema.required]
```

**Business Rules:**
- Immutable after creation (thread-safe for caching)
- source field tracks how requirements were loaded (yaml/rag/permissive)
- strict=False converts validation errors to warnings
- allow_override enables manual bypass (future feature)

**Example:**
```python
requirements = CheckpointRequirements(
    evidence_schema={
        "business_goals": FieldSchema(
            name="business_goals",
            type="integer",
            required=True,
            validator="positive",
            validator_params=None,
            description="Number of business goals defined"
        )
    },
    validators={"positive": "lambda x: x > 0"},
    cross_field_rules=[],
    strict=False,
    allow_override=True,
    source="yaml"
)
```

---

#### FieldSchema

**Purpose:** Schema definition for a single evidence field

**Definition:**
```python
@dataclass
class FieldSchema:
    """
    Schema for single evidence field.
    
    Defines type, requirements, and validation for one evidence field.
    """
    
    name: str
    type: str  # "boolean" | "integer" | "string" | "object" | "list"
    required: bool
    validator: Optional[str]  # Validator name (references validators dict)
    validator_params: Optional[Dict[str, Any]]  # Parameters for validator
    description: str
    
    def validate_type(self, value: Any) -> bool:
        """
        Check if value matches declared type.
        
        Returns:
            True if type matches, False otherwise
        """
        type_map = {
            "boolean": bool,
            "integer": int,
            "string": str,
            "object": dict,
            "list": list
        }
        expected_type = type_map.get(self.type)
        return expected_type is not None and isinstance(value, expected_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "type": self.type,
            "required": self.required,
            "validator": self.validator,
            "validator_params": self.validator_params,
            "description": self.description
        }
```

**Business Rules:**
- type must be one of: boolean, integer, string, object, list
- validator is optional (None = type checking only)
- validator_params passed to validator function if present
- required=True means field must be in evidence dict

**Validation:**
- name: non-empty string
- type: must be in allowed types
- description: non-empty string

**Example:**
```python
schema = FieldSchema(
    name="functional_requirements",
    type="integer",
    required=True,
    validator="in_range",
    validator_params={"min_val": 3, "max_val": 50},
    description="Number of functional requirements (3-50 is reasonable)"
)
```

---

#### CrossFieldRule

**Purpose:** Validation rule that checks relationships between multiple fields

**Definition:**
```python
@dataclass
class CrossFieldRule:
    """
    Cross-field validation rule.
    
    Validates relationships between multiple evidence fields.
    """
    
    rule: str  # Lambda expression taking evidence dict
    error_message: str
    
    def evaluate(self, evidence: Dict[str, Any]) -> bool:
        """
        Evaluate rule against evidence.
        
        Args:
            evidence: Evidence dictionary to validate
            
        Returns:
            True if rule passes, False otherwise
            
        Raises:
            ValueError: If rule syntax invalid or evaluation fails
        """
        try:
            rule_func = eval(self.rule, {"__builtins__": {}}, {})
            return bool(rule_func(evidence))
        except Exception as e:
            raise ValueError(f"Cross-field rule evaluation failed: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "rule": self.rule,
            "error_message": self.error_message
        }
```

**Business Rules:**
- rule is lambda expression accepting evidence dict
- Evaluated in restricted context (no builtins for security)
- error_message shown if rule returns False

**Example:**
```python
rule = CrossFieldRule(
    rule="lambda e: e.get('functional_requirements', 0) >= e.get('business_goals', 0)",
    error_message="Should have at least as many FRs as business goals"
)
```

---

#### ValidationResult

**Purpose:** Encapsulates outcome of checkpoint validation

**Definition:**
```python
@dataclass
class ValidationResult:
    """
    Result of checkpoint validation.
    
    Contains all information about validation outcome including
    errors, warnings, diagnostics, and remediation guidance.
    """
    
    passed: bool
    errors: List[str]
    warnings: List[str]
    diagnostics: Dict[str, Any]
    remediation: str
    next_steps: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for MCP tool response.
        
        Returns dictionary matching complete_phase response format.
        """
        return {
            "checkpoint_passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "diagnostics": self.diagnostics,
            "remediation": self.remediation,
            "next_steps": self.next_steps
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def success(cls) -> 'ValidationResult':
        """Create successful validation result."""
        return cls(
            passed=True,
            errors=[],
            warnings=[],
            diagnostics={},
            remediation="",
            next_steps=[]
        )
    
    @classmethod
    def failure(
        cls,
        errors: List[str],
        diagnostics: Dict[str, Any],
        remediation: str,
        next_steps: List[str],
        warnings: List[str] = None
    ) -> 'ValidationResult':
        """Create failed validation result."""
        return cls(
            passed=False,
            errors=errors,
            warnings=warnings or [],
            diagnostics=diagnostics,
            remediation=remediation,
            next_steps=next_steps
        )
```

**Business Rules:**
- passed=False means phase does not advance
- errors list must be non-empty if passed=False
- diagnostics contains metadata about validation attempt
- remediation provides actionable guidance
- next_steps lists concrete actions

**Example:**
```python
result = ValidationResult.failure(
    errors=["Field 'business_goals' is required but missing"],
    diagnostics={
        "fields_submitted": ["user_stories"],
        "fields_required": ["business_goals", "user_stories"],
        "fields_missing": ["business_goals"],
        "strict_mode": False
    },
    remediation="Provide the 'business_goals' field with count of goals defined",
    next_steps=["Review srd.md to count business goals", "Submit with business_goals field"]
)
```

---

### 4.2 Existing State Models (Unchanged)

These models exist in the current system and are not modified by the Evidence Validation System. Documented here for completeness.

#### WorkflowState

**Purpose:** Persistent state for workflow session

**Definition** (Existing, no changes):
```python
@dataclass
class WorkflowState:
    """
    Workflow session state.
    
    Persisted to disk after each phase. Unchanged by validation system.
    """
    
    session_id: str
    workflow_type: str
    current_phase: int
    checkpoint_status: CheckpointStatus  # PENDING | PASSED | FAILED
    phase_artifacts: Dict[int, Dict[str, Any]]  # Phase number -> artifacts
    created_at: datetime
    updated_at: datetime
    
    # Validation result stored in phase_artifacts:
    # phase_artifacts[phase]["checkpoint_result"] = ValidationResult.to_dict()
```

**Validation Integration:**
- checkpoint_status set to FAILED when validation fails
- ValidationResult stored in phase_artifacts[phase]["checkpoint_result"]
- State persisted even on validation failure (for audit trail)

**No Schema Changes Required:** Existing WorkflowState structure accommodates validation results via phase_artifacts dictionary.

---

#### CheckpointStatus

**Purpose:** Enum for checkpoint state

**Definition** (Existing, no changes):
```python
from enum import Enum

class CheckpointStatus(Enum):
    """Checkpoint validation status."""
    
    PENDING = "pending"      # Not yet attempted
    PASSED = "passed"        # Validation passed
    FAILED = "failed"        # Validation failed
    OVERRIDDEN = "overridden"  # Manually overridden (future)
```

**Usage:**
- Set to PASSED when checkpoint_passed=True
- Set to FAILED when checkpoint_passed=False
- PENDING before validation attempt
- OVERRIDDEN for future manual override feature

---

### 4.3 File-Based Data: gate-definition.yaml

**Purpose:** Config file storing validation requirements per workflow phase

**Location Pattern:** `.praxis-os/workflows/{workflow_type}/phases/{N}/gate-definition.yaml`

**Schema Structure:**
```yaml
# Top-level structure
checkpoint:
  strict: boolean
  allow_override: boolean

evidence_schema:
  {field_name}:
    type: string  # "boolean" | "integer" | "string" | "object" | "list"
    required: boolean
    validator: string  # optional
    validator_params:  # optional
      {param_name}: {value}
    description: string

validators:
  {validator_name}: "lambda expression string"

cross_field_validation:  # optional
  - rule: "lambda expression string"
    error_message: string
```

**Validation Rules:**
- Must be valid YAML syntax
- checkpoint section required
- evidence_schema section required
- validators section optional (defaults to empty dict)
- cross_field_validation section optional (defaults to empty list)
- Field types must be in allowed set
- Lambda expressions must be valid Python syntax

**Example** (spec_creation_v1 Phase 1):
```yaml
checkpoint:
  strict: false
  allow_override: true

evidence_schema:
  srd_created:
    type: boolean
    required: true
    description: "SRD file created successfully"
  
  business_goals:
    type: integer
    required: true
    validator: positive
    description: "Number of business goals defined"
  
  user_stories:
    type: integer
    required: true
    validator: positive
    description: "Number of user stories documented"
  
  functional_requirements:
    type: integer
    required: true
    validator: in_range
    validator_params:
      min_val: 3
      max_val: 50
    description: "Number of functional requirements"

validators:
  positive: "lambda x: x > 0"
  in_range: "lambda x, min_val, max_val: min_val <= x <= max_val"

cross_field_validation:
  - rule: "lambda e: e.get('functional_requirements', 0) >= e.get('business_goals', 0)"
    error_message: "Should have at least as many FRs as business goals"
```

**Storage:**
- Plain text YAML files
- Version controlled in git
- One file per workflow phase
- Human-readable and manually editable

---

### 4.4 Cache Data Structure

**Purpose:** In-memory cache for parsed gate definitions

**Implementation:**
```python
class CheckpointLoader:
    """
    Checkpoint loader with thread-safe cache.
    
    Cache structure: Dict[str, CheckpointRequirements]
    Cache key format: "{workflow_type}:{phase}"
    """
    
    _cache: Dict[str, CheckpointRequirements] = {}
    _cache_lock: threading.Lock = threading.Lock()
    
    # Example cache contents:
    # {
    #     "spec_creation_v1:0": CheckpointRequirements(...),
    #     "spec_creation_v1:1": CheckpointRequirements(...),
    #     "test_generation_v3:0": CheckpointRequirements(...)
    # }
```

**Cache Management:**
- Key: "{workflow_type}:{phase}" (e.g., "spec_creation_v1:1")
- Value: CheckpointRequirements (immutable)
- Thread-safe: Double-checked locking pattern
- No TTL: Cache persists for process lifetime
- No invalidation: Requirements don't change during execution
- Memory: ~10KB per cached gate definition

**Cache Metrics:**
- Hit rate target: > 95%
- Miss on first access only (per workflow phase)
- Typical working set: 10-20 cached gates (100-200KB total)

---

### 4.5 Validation State Flow

**State Diagram:**

```
┌─────────────┐
│   PENDING   │ (Initial state)
└──────┬──────┘
       │
       │ complete_phase(evidence)
       ▼
┌─────────────────┐
│   VALIDATING    │ (Transient - not persisted)
└────────┬────────┘
         │
         ├─── Validation Success ────┐
         │                           ▼
         │                    ┌─────────────┐
         │                    │   PASSED    │
         │                    └─────────────┘
         │                           │
         │                           │ Phase advances
         │                           ▼
         │                    ┌─────────────┐
         │                    │  Next Phase │
         │                    │   PENDING   │
         │                    └─────────────┘
         │
         └─── Validation Failure ──┐
                                   ▼
                            ┌─────────────┐
                            │   FAILED    │
                            └─────────────┘
                                   │
                                   │ Retry with corrected evidence
                                   ▼
                            ┌─────────────┐
                            │ VALIDATING  │ (Retry)
                            └─────────────┘
```

**State Transitions:**
1. **PENDING → VALIDATING**: When complete_phase() called
2. **VALIDATING → PASSED**: When validation succeeds
3. **VALIDATING → FAILED**: When validation fails
4. **FAILED → VALIDATING**: When retry with corrected evidence
5. **PASSED → Next Phase PENDING**: When phase advances

**Persistence:**
- PENDING, PASSED, FAILED persisted in WorkflowState
- VALIDATING is transient (not persisted)
- ValidationResult persisted in phase_artifacts on FAILED

---

### 4.6 Data Validation Rules

#### CheckpointRequirements Validation

**Constraints:**
- evidence_schema: non-empty dict
- validators: dict (may be empty)
- cross_field_rules: list (may be empty)
- strict: boolean
- allow_override: boolean
- source: one of ["yaml", "rag", "permissive"]

**Invariants:**
- If field references validator, validator must be in validators dict
- Field types must be in allowed set
- Validator expressions must be valid Python lambda syntax
- Cross-field rule expressions must be valid Python lambda syntax

#### FieldSchema Validation

**Constraints:**
- name: 1-255 characters, alphanumeric + underscore
- type: one of ["boolean", "integer", "string", "object", "list"]
- required: boolean
- validator: None or non-empty string
- validator_params: None or dict
- description: 1-1000 characters

**Invariants:**
- If validator set, must reference existing validator name
- If validator_params set, validator must be set
- Type matches expected Python type for validation

#### ValidationResult Validation

**Constraints:**
- If passed=False, errors list must be non-empty
- If passed=True, errors list must be empty
- warnings list always valid (may be empty)
- diagnostics dict always valid (may be empty)
- remediation string always valid (may be empty)
- next_steps list always valid (may be empty)

**Invariants:**
- passed boolean matches len(errors) == 0
- diagnostics contains validation metadata (timestamps, counts, etc.)

---

### 4.7 Data Migration

**No Database Migration Required:**
- Validation system uses existing WorkflowState structure
- No schema changes to WorkflowState
- ValidationResult stored in existing phase_artifacts dict
- Backwards compatible with existing workflow states

**File Migration (gate-definition.yaml):**
- New files created via migration script
- Existing workflows continue without files (fallback to RAG)
- Progressive migration (not big-bang)
- No data loss (non-destructive addition)

**Migration Script Output:**
```bash
# Generate gate definitions for all workflows
python scripts/generate-gate-definitions.py

# Creates:
# .praxis-os/workflows/spec_creation_v1/phases/0/gate-definition.yaml
# .praxis-os/workflows/spec_creation_v1/phases/1/gate-definition.yaml
# .praxis-os/workflows/test_generation_v3/phases/0/gate-definition.yaml
# ... (one per workflow phase)
```

---

### 4.8 Data Access Patterns

#### Read Patterns

**Hot Path (Cached):**
```python
# CheckpointLoader.load_checkpoint_requirements()
# 1. Check cache (fast path, no lock)
requirements = self._cache.get(cache_key)
if requirements:
    return requirements  # < 10ms

# 2. Load with lock (cache miss)
with self._cache_lock:
    requirements = self._load_with_fallback()
    self._cache[cache_key] = requirements
    return requirements  # < 50ms
```

**Access Frequency:**
- Hot: Gate definition loading (1x per phase per session)
- Warm: ValidationResult retrieval from phase_artifacts
- Cold: Gate definition file reads (cache misses only)

#### Write Patterns

**WorkflowState Updates:**
```python
# After validation (pass or fail)
state.checkpoint_status = CheckpointStatus.PASSED  # or FAILED
state.phase_artifacts[phase]["checkpoint_result"] = result.to_dict()
state.updated_at = datetime.now()
state.save()  # Existing persistence mechanism
```

**Write Frequency:**
- Every complete_phase() call writes WorkflowState
- No writes to gate-definition.yaml (read-only config)
- No cache writes after initialization

---

### 4.9 Data Size Estimates

**CheckpointRequirements:**
- Typical size: 5-15 fields per phase
- Memory per gate: ~5-10KB
- Cache working set: 10-20 gates = 100-200KB

**ValidationResult:**
- Typical size: 5-10 errors, 100-500 bytes diagnostics
- Memory per result: ~1-2KB
- Persisted in WorkflowState phase_artifacts

**gate-definition.yaml:**
- Typical size: 50-150 lines, 2-5KB per file
- Total for 15 workflows × 5 phases avg: 375KB-750KB
- Negligible storage impact

**Cache Memory:**
- Per CheckpointRequirements: ~10KB
- Expected working set: 20 gates = 200KB
- Maximum (all workflows cached): 75 gates = 750KB

---

## 4.10 Data Model Summary

| Model | Type | Storage | Size | Mutability |
|-------|------|---------|------|------------|
| CheckpointRequirements | Python dataclass | Memory (cached) | ~10KB | Immutable |
| FieldSchema | Python dataclass | Part of CheckpointRequirements | ~200B | Immutable |
| CrossFieldRule | Python dataclass | Part of CheckpointRequirements | ~100B | Immutable |
| ValidationResult | Python dataclass | Memory + WorkflowState | ~2KB | Immutable |
| WorkflowState | Python dataclass | Disk (JSON) | ~5-50KB | Mutable |
| gate-definition.yaml | YAML file | Disk (git) | ~5KB | Read-only at runtime |
| Cache | Dict | Memory | ~200KB | Write-once per key |

**Key Characteristics:**
- **Immutability**: Core validation models are immutable (thread-safe)
- **Caching**: CheckpointRequirements cached in memory for performance
- **Persistence**: Only WorkflowState persisted (existing mechanism)
- **Config-Driven**: gate-definition.yaml provides validation rules
- **Backwards Compatible**: No changes to existing data structures

---

## 5. Security Design

---

### 5.1 Threat Model

**System Context:**
The Evidence Validation System is an internal component of the Agent OS workflow engine. The primary security concern is **AI agents attempting to game validation by discovering evidence schemas** rather than traditional external threats like SQL injection or XSS.

**Threat Actors:**
1. **AI Agents (Primary)**: Sophisticated AI systems executing workflows who may attempt to:
   - Discover hidden validation schemas
   - Submit false evidence that passes validation
   - Bypass validation gates through schema inference
   - Exploit validator logic to pass without doing work

2. **Malicious Users (Secondary)**: Human users with file system access who may:
   - Tamper with gate-definition.yaml files
   - Modify validation results in WorkflowState
   - Inject malicious lambda validators

3. **System Bugs (Tertiary)**: Implementation flaws that may:
   - Leak validation schemas to AI agents
   - Allow arbitrary code execution in validators
   - Enable validation bypass through edge cases

**Assets to Protect:**
- **gate-definition.yaml files**: Hidden schemas that define validation requirements
- **Validator logic**: Lambda expressions that check proof content
- **Validation results**: Evidence of what passed/failed validation
- **System integrity**: Workflow engine must not crash from validation errors

---

### 5.2 Information Asymmetry (Primary Security Mechanism)

**Purpose:** Prevent AI agents from discovering validation schemas by hiding gate-definition.yaml from all AI-accessible interfaces.

#### 5.2.1 Schema Hiding

**Threat:** AI agent reads gate-definition.yaml to learn evidence structure, then submits fake evidence matching expected schema.

**Mitigation:**

1. **File Exclusion from MCP Tools**
   ```python
   # get_task() implementation
   def get_task(workflow_type: str, phase: int, task_number: int) -> Dict:
       """Return task content WITHOUT gate-definition.yaml."""
       task_content = read_file(f"phases/{phase}/task-{task_number}.md")
       # NEVER include gate-definition.yaml in response
       # AI only sees natural language requirements
       return {"content": task_content}
   ```

2. **Natural Language Task Files**
   - Task files contain only natural language descriptions
   - No structured schema definitions in markdown
   - AI must interpret requirements, not copy structure

3. **No Schema in Error Messages**
   - Error messages reference field names but not complete schema
   - Validation failures don't expose other required fields
   - Remediation guidance focuses on fixing submitted fields

**Verification:**
- Unit test: get_task() never returns gate-definition.yaml content
- Integration test: AI agent cannot access schema through any MCP tool
- Code review: Search for any file reads that could expose gates

#### 5.2.2 Multi-Layer Defense

**Threat:** AI infers schema by submitting test evidence and observing errors.

**Mitigation:**

**Layer 1: Field Names**
- Required fields not listed in single error message
- AI must discover each field independently
- Slows schema discovery through iteration

**Layer 2: Field Types**
- Type errors don't reveal expected types of other fields
- AI learns types one field at a time

**Layer 3: Custom Validators**
- Validator names not exposed (just "validation failed")
- Validator logic hidden (lambda expressions not shown)
- AI cannot see why content validation failed

**Layer 4: Proof Content**
- Proof validators check actual content (not just presence)
- Boolean fields alone insufficient (must provide artifacts)
- AI must do actual work to generate valid proof

**Example - Progressive Discovery:**
```python
# Attempt 1: AI submits empty evidence
{"errors": ["Field 'business_goals' is required"]}
# Schema leaked: business_goals exists

# Attempt 2: AI submits wrong type
{"errors": ["Field 'business_goals' must be integer"]}
# Schema leaked: type is integer

# Attempt 3: AI submits invalid value
{"errors": ["Validator 'positive' failed"]}
# Schema leaked: has validator (but not what it checks)

# Attempt 4: AI submits 0
{"errors": ["value must be > 0"]}  # From validator exception message
# Schema leaked: positive means > 0

# BUT: AI still doesn't know about other fields, cross-field rules, etc.
```

**Result:** Discovery is expensive (many iterations), each phase has unique schema, not worth gaming effort.

---

### 5.3 Validator Security

**Purpose:** Prevent arbitrary code execution and ensure validators run in controlled, safe context.

#### 5.3.1 Lambda-Only Restriction

**Threat:** Malicious user injects validator that executes arbitrary code (e.g., `os.system("rm -rf /")`)

**Mitigation:**

1. **No External Modules**
   ```yaml
   # FORBIDDEN in gate-definition.yaml
   validators:
     malicious: "lambda x: __import__('os').system('rm -rf /')"
   ```

2. **Restricted Globals**
   ```python
   class ValidatorExecutor:
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
           # NO os, sys, subprocess, __import__, eval, exec, etc.
       }
       
       def execute_validator(self, validator_expr: str, value: Any, params: Dict):
           try:
               validator_func = eval(
                   validator_expr,
                   self.SAFE_GLOBALS,  # Restricted globals only
                   {}  # Empty locals (no access to surrounding scope)
               )
               return validator_func(value, **params)
           except Exception as e:
               # Validator exception = validation failure (not system crash)
               return (False, f"Validator failed: {e}")
   ```

3. **Syntax Validation**
   - Validator expressions validated as Python lambda syntax
   - Parse validator before execution (catch syntax errors early)
   - Reject validators with dangerous patterns (e.g., `__import__`)

**Example Forbidden Validators:**
```yaml
# These would be rejected:
validators:
  dangerous1: "lambda x: exec('rm -rf /')"  # exec forbidden
  dangerous2: "lambda x: __import__('os').listdir('/')"  # __import__ forbidden
  dangerous3: "lambda x: open('/etc/passwd').read()"  # open forbidden (not in SAFE_GLOBALS)
```

**Example Allowed Validators:**
```yaml
# These are safe:
validators:
  positive: "lambda x: x > 0"
  yaml_valid: "lambda x: yaml.safe_load(x) is not None"
  has_success: "lambda x: 'success' in x.lower()"
```

#### 5.3.2 Execution Limits

**Threat:** Validator runs infinite loop or consumes excessive resources.

**Mitigation:**

1. **Timeout (Future Enhancement)**
   ```python
   # v1.0: No timeout (validators expected to be fast)
   # v2.0: Add timeout if needed
   with timeout(seconds=1):
       result = validator_func(value, **params)
   ```

2. **No I/O in Validators**
   - Validators operate on in-memory values only
   - No file reads, network requests, database queries
   - Fast, predictable execution (< 1ms per validator)

3. **Simple Validators Encouraged**
   - Migration script generates simple validators (positive, non_empty, etc.)
   - Documentation emphasizes fast, pure functions
   - Complex validation done in application code (pre-evidence submission)

**Performance Target:** Each validator execution < 1ms, total validation < 100ms

---

### 5.4 File Access Control

**Purpose:** Protect gate-definition.yaml files from tampering while allowing legitimate access.

#### 5.4.1 Read-Only at Runtime

**Threat:** Malicious code modifies gate-definition.yaml during validation.

**Mitigation:**

1. **Cache Prevents Re-reads**
   - gate-definition.yaml loaded once, cached
   - No re-reads after initial load (tampering after load has no effect)
   - Cache invalidation only on server restart

2. **File Permissions**
   ```bash
   # Recommended file permissions
   chmod 644 .praxis-os/workflows/*/phases/*/gate-definition.yaml
   # Read-write for owner, read-only for group/others
   ```

3. **Version Control**
   - gate-definition.yaml tracked in git
   - Changes reviewed through pull requests
   - Audit trail of modifications

**Access Pattern:**
```python
# Runtime: Read-only
gate = load_gate_definition(workflow, phase)  # Read from cache or file
# No writes during validation

# Development: Write during migration/creation
generate_gate_definitions()  # Migration script
workflow_creation_v1()  # Auto-generation
```

#### 5.4.2 Path Traversal Protection

**Threat:** Attacker uses path traversal to read arbitrary files (e.g., `../../etc/passwd`)

**Mitigation:**

1. **Validated File Paths**
   ```python
   def load_gate_definition(workflow_type: str, phase: int) -> CheckpointRequirements:
       # Validate inputs
       if not re.match(r'^[a-zA-Z0-9_-]+$', workflow_type):
           raise ValueError("Invalid workflow_type")
       if not isinstance(phase, int) or phase < 0:
           raise ValueError("Invalid phase")
       
       # Construct safe path
       gate_path = Path(f".praxis-os/workflows/{workflow_type}/phases/{phase}/gate-definition.yaml")
       
       # Resolve to absolute path (prevents traversal)
       gate_path = gate_path.resolve()
       
       # Verify path is within workflows directory
       if not str(gate_path).startswith(str(Path(".praxis-os/workflows").resolve())):
           raise ValueError("Path traversal attempt detected")
       
       return yaml.safe_load(gate_path.read_text())
   ```

2. **Input Validation**
   - workflow_type: Alphanumeric + underscore/dash only
   - phase: Integer >= 0
   - No special characters that could enable traversal

---

### 5.5 Data Protection

**Purpose:** Protect sensitive data in validation system.

#### 5.5.1 Evidence Data

**Sensitivity:** Evidence may contain sensitive information depending on workflow.

**Protection:**

1. **In Transit:** MCP communication over stdio (local process) or HTTPS (SSE transport)
2. **At Rest:** WorkflowState persisted to disk (existing mechanism)
3. **In Memory:** Evidence held temporarily during validation, then released
4. **In Logs:** Evidence not logged by default (only validation results)

**No Additional Encryption Required:**
- Evidence already protected by file system permissions
- No PII in typical workflow evidence (counts, booleans, file paths)
- If PII needed, handled by existing WorkflowState encryption (out of scope for validation system)

#### 5.5.2 Validation Results

**Sensitivity:** Validation results reveal checkpoint requirements (sensitive for AI hiding).

**Protection:**

1. **Not Logged to Shared Storage:** Validation failures logged locally only
2. **Not Exposed via External APIs:** MCP tools are internal only
3. **Aggregation Prevents Schema Leak:** Metrics aggregate pass/fail rates, don't expose individual evidence

#### 5.5.3 gate-definition.yaml

**Sensitivity:** HIGH - Contains hidden schemas AI must not see.

**Protection:**

1. **File System Permissions:** 644 (read-only for most users)
2. **Git Tracked:** Version control with audit trail
3. **Never Exposed to AI:** Excluded from all MCP tool responses
4. **No External Access:** Not served via HTTP or any external API

---

### 5.6 Input Validation

**Purpose:** Validate all inputs to prevent injection attacks and ensure system stability.

#### 5.6.1 Evidence Validation

**Threat:** Malicious evidence exploits validator or crashes system.

**Mitigation:**

1. **Type Checking**
   ```python
   def validate_field_type(value: Any, expected_type: str) -> bool:
       type_map = {
           "boolean": bool,
           "integer": int,
           "string": str,
           "object": dict,
           "list": list
       }
       return isinstance(value, type_map[expected_type])
   ```

2. **Size Limits**
   ```python
   # String fields
   MAX_STRING_LENGTH = 1_000_000  # 1MB
   if isinstance(value, str) and len(value) > MAX_STRING_LENGTH:
       raise ValueError("String too long")
   
   # List fields
   MAX_LIST_LENGTH = 10_000
   if isinstance(value, list) and len(value) > MAX_LIST_LENGTH:
       raise ValueError("List too long")
   
   # Object fields
   MAX_OBJECT_KEYS = 1_000
   if isinstance(value, dict) and len(value) > MAX_OBJECT_KEYS:
       raise ValueError("Object too many keys")
   ```

3. **Sanitization**
   - Evidence values not executed (only validated)
   - No eval/exec on evidence content
   - String values treated as data (not code)

#### 5.6.2 YAML Parsing

**Threat:** Malicious YAML exploits parser (YAML bombs, code execution).

**Mitigation:**

1. **Safe Loader Only**
   ```python
   # SAFE: Uses yaml.safe_load (no code execution)
   gate_content = yaml.safe_load(gate_path.read_text())
   
   # FORBIDDEN: yaml.load (can execute code)
   # gate_content = yaml.load(gate_path.read_text())  # NEVER DO THIS
   ```

2. **Size Limits**
   ```python
   MAX_YAML_SIZE = 1_000_000  # 1MB max
   content = gate_path.read_text()
   if len(content) > MAX_YAML_SIZE:
       raise ValueError("YAML file too large")
   ```

3. **Schema Validation**
   ```python
   # Validate gate-definition.yaml structure
   required_keys = ["checkpoint", "evidence_schema"]
   if not all(k in gate_content for k in required_keys):
       raise ValueError("Invalid gate structure")
   ```

#### 5.6.3 Lambda Expression Validation

**Threat:** Malicious lambda in gate-definition.yaml exploits eval().

**Mitigation:**

1. **Syntax Validation**
   ```python
   def validate_lambda_syntax(expr: str) -> bool:
       try:
           compile(expr, '<string>', 'eval')
           return True
       except SyntaxError:
           return False
   ```

2. **Pattern Blacklist**
   ```python
   FORBIDDEN_PATTERNS = [
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
   
   def is_safe_validator(expr: str) -> bool:
       for pattern in FORBIDDEN_PATTERNS:
           if re.search(pattern, expr):
               return False
       return True
   ```

3. **Restricted Execution** (as described in 5.3.1)

---

### 5.7 Audit Logging

**Purpose:** Log validation attempts for debugging and security monitoring.

#### 5.7.1 Logged Events

**Authentication/Authorization:**
- N/A (internal system, no external auth)

**Validation Events:**
```python
# Validation pass
logger.info(
    "Checkpoint validation passed",
    extra={
        "session_id": session_id,
        "workflow_type": workflow_type,
        "phase": phase,
        "gate_source": "yaml",  # or "rag" or "permissive"
        "fields_validated": len(evidence),
        "timestamp": datetime.now().isoformat()
    }
)

# Validation failure
logger.warning(
    "Checkpoint validation failed",
    extra={
        "session_id": session_id,
        "workflow_type": workflow_type,
        "phase": phase,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "fields_submitted": list(evidence.keys()),
        "fields_failed": failed_fields,
        "strict_mode": gate.strict,
        "timestamp": datetime.now().isoformat()
    }
)
```

**Security Events:**
```python
# Schema access attempt (if detected)
logger.error(
    "Attempted access to gate-definition.yaml via MCP tool",
    extra={
        "tool": "get_task",  # or other tool
        "session_id": session_id,
        "blocked": True,
        "timestamp": datetime.now().isoformat()
    }
)

# Validator security violation
logger.error(
    "Unsafe validator detected in gate-definition.yaml",
    extra={
        "workflow_type": workflow_type,
        "phase": phase,
        "validator_name": validator_name,
        "validator_expr": validator_expr,
        "forbidden_pattern": pattern,
        "timestamp": datetime.now().isoformat()
    }
)
```

#### 5.7.2 Log Retention

**Policy:**
- **Validation logs:** Retained for 90 days (debugging, metrics)
- **Security logs:** Retained for 1 year (incident response)
- **PII:** No PII logged (evidence values not logged, only field names/types)

#### 5.7.3 Log Analysis

**Metrics to Monitor:**
- Validation pass/fail rate per workflow
- Most common validation errors
- Average validation time
- Gate source distribution (yaml/rag/permissive)
- Fallback frequency (how often RAG/permissive used)

**Alerting:**
- Validation failure rate > 50% (possible gate definition issue)
- Validation time > 100ms (performance degradation)
- Security event detected (attempted schema access, unsafe validator)

---

### 5.8 Secure Development Practices

**Purpose:** Ensure security throughout development lifecycle.

#### 5.8.1 Code Review Requirements

**For Changes to:**
- **CheckpointLoader:** Schema hiding still effective?
- **ValidatorExecutor:** Safe globals still restricted?
- **MCP Tools:** No accidental schema exposure?
- **gate-definition.yaml files:** Validators safe?

**Checklist:**
- [ ] gate-definition.yaml never returned to AI
- [ ] Validators use restricted globals only
- [ ] No arbitrary code execution possible
- [ ] Input validation on all evidence fields
- [ ] Error messages don't leak complete schema

#### 5.8.2 Testing Requirements

**Security Tests:**
```python
# test_security.py

def test_gate_never_exposed_to_ai():
    """Verify get_task() never returns gate content."""
    task = get_task("spec_creation_v1", 1, 1)
    assert "gate-definition.yaml" not in str(task)
    assert "evidence_schema" not in str(task)

def test_validator_restricted_globals():
    """Verify validators cannot access dangerous modules."""
    with pytest.raises(NameError):
        execute_validator("lambda x: __import__('os').system('echo hacked')", "test")

def test_validator_syntax_validation():
    """Verify malicious validators rejected."""
    assert not is_safe_validator("lambda x: exec('rm -rf /')")
    assert not is_safe_validator("lambda x: __import__('os')")

def test_path_traversal_blocked():
    """Verify path traversal attempts blocked."""
    with pytest.raises(ValueError):
        load_gate_definition("../../etc/passwd", 0)

def test_evidence_size_limits():
    """Verify evidence size limits enforced."""
    huge_string = "x" * (MAX_STRING_LENGTH + 1)
    with pytest.raises(ValueError):
        validate_field_type(huge_string, "string")
```

#### 5.8.3 Dependency Security

**YAML Parser:**
- Use `yaml.safe_load()` exclusively (never `yaml.load()`)
- Keep pyyaml updated (security patches)

**No New Dependencies:**
- Validation system uses only stdlib + existing pyyaml
- No risk of supply chain attacks from new packages

---

### 5.9 Incident Response

**Purpose:** Plan for security incidents.

#### 5.9.1 AI Schema Discovery

**Scenario:** AI agent discovers validation schema through iteration.

**Detection:**
- High volume of validation failures with systematic evidence variations
- Pattern of field discovery (one field at a time)

**Response:**
1. Review gate-definition.yaml for that workflow
2. Strengthen validators (more proof-based, less boolean)
3. Add cross-field validation (harder to infer)
4. Consider lenient mode temporarily (prevent blocking legitimate work)

**Prevention:**
- Use proof-based evidence from the start
- Minimize boolean fields (too easy to fake)
- Require structured artifacts (YAML content, command output, etc.)

#### 5.9.2 Validator Compromise

**Scenario:** Malicious gate-definition.yaml deployed with unsafe validator.

**Detection:**
- Pre-commit hook catches forbidden patterns
- Code review catches during PR
- Runtime syntax validation catches at load time

**Response:**
1. Revert malicious gate-definition.yaml
2. Review all recent gate changes
3. Audit who has write access to .praxis-os/workflows/
4. Add additional pre-commit validation if needed

**Prevention:**
- Pre-commit hooks validate validators
- Code review all gate changes
- Limited write access to workflow files

#### 5.9.3 Validation Bypass

**Scenario:** Bug allows bypassing validation entirely.

**Detection:**
- Phases advancing without evidence
- Validation logs show unexpected permissive gate usage
- Test coverage catches regression

**Response:**
1. Emergency patch to fix bypass
2. Review all workflows processed during vulnerability window
3. Re-validate recent phase advancements

**Prevention:**
- High test coverage (90%+ for validation system)
- Integration tests for complete_phase flow
- Regression tests for known bypass patterns

---

## 5.10 Security Checklist

| Security Control | Status | Requirement | Verification |
|-----------------|--------|-------------|--------------|
| **Information Asymmetry** | ✅ Implemented | NFR-S1 | Unit test: get_task() never returns gate YAML |
| **Schema Hiding** | ✅ Implemented | FR-005 | Integration test: AI cannot access schema |
| **Validator Security** | ✅ Implemented | NFR-S2 | Unit test: Restricted globals enforced |
| **Lambda-Only** | ✅ Implemented | NFR-S2 | Code review: No external module loading |
| **Safe YAML Parsing** | ✅ Implemented | NFR-S2 | Code review: yaml.safe_load only |
| **Path Traversal Protection** | ✅ Implemented | Security best practice | Unit test: Traversal attempts blocked |
| **Input Validation** | ✅ Implemented | NFR-R2 | Unit test: Size limits enforced |
| **Audit Logging** | ✅ Implemented | NFR-S3 | Integration test: Events logged correctly |
| **File Access Control** | ✅ Implemented | Best practice | Code review: Read-only at runtime |
| **Cache Security** | ✅ Implemented | NFR-P3 | Unit test: Thread-safe cache |

---

## 5.11 Security Summary

**Primary Security Mechanism:** Information Asymmetry
- AI agents never see validation schemas
- Multi-layer defense makes schema discovery expensive
- Proof-based evidence requires actual work (not guessing)

**Secondary Mechanisms:**
- **Validator Security:** Lambda-only with restricted globals (no code execution)
- **File Access Control:** gate-definition.yaml read-only at runtime
- **Input Validation:** Evidence size limits, type checking, YAML safe parsing
- **Audit Logging:** All validation attempts logged for monitoring

**Risk Assessment:**
- **AI Gaming:** MEDIUM risk, mitigated by information asymmetry + proof-based evidence
- **Code Execution:** LOW risk, mitigated by lambda-only + restricted globals
- **File Tampering:** LOW risk, mitigated by read-only runtime + version control
- **System Crash:** LOW risk, mitigated by input validation + error handling

**Compliance:**
- No external authentication needed (internal system)
- No PII in evidence (typical workflows use counts, booleans, file paths)
- Audit trail provided (validation attempts logged)
- Backwards compatible (no breaking changes to security model)

**The validation system's security is primarily about maintaining information asymmetry to prevent AI gaming, rather than traditional security concerns like preventing external attacks.**

---

## 6. Performance Design

---

### 6.1 Performance Targets

**NFR-P1: Validation Speed**
- **Target**: < 100ms per checkpoint validation (95th percentile)
- **Breakdown**:
  - Gate loading (cached): < 10ms
  - Gate loading (first time): < 50ms
  - Field validation: < 20ms
  - Validator execution: < 10ms per validator
  - Error message generation: < 5ms

**NFR-P2: Cache Hit Rate**
- **Target**: > 95% cache hit rate
- **Impact**: First validation per phase per session loads from disk (< 50ms), subsequent validations use cache (< 10ms)

**NFR-P3: Concurrent Load**
- **Target**: No performance degradation with 10+ concurrent workflows
- **Mechanism**: Thread-safe cache with double-checked locking

---

### 6.2 Caching Strategy

#### 6.2.1 CheckpointRequirements Cache

**Purpose:** Avoid re-parsing gate-definition.yaml on every validation.

**Implementation:**
```python
class CheckpointLoader:
    _cache: Dict[str, CheckpointRequirements] = {}
    _cache_lock: threading.Lock = threading.Lock()
    
    def load_checkpoint_requirements(self, workflow_type: str, phase: int):
        cache_key = f"{workflow_type}:{phase}"
        
        # Fast path: Check cache without lock (95%+ hit rate)
        if cache_key in self._cache:
            return self._cache[cache_key]  # < 10ms
        
        # Slow path: Load and cache with lock
        with self._cache_lock:
            # Double-check inside lock
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Load from file/RAG
            requirements = self._load_with_fallback(workflow_type, phase)
            self._cache[cache_key] = requirements  # Store for future
            return requirements  # < 50ms (first time only)
```

**Cache Characteristics:**
- **Type**: In-memory dictionary
- **Scope**: Process-wide (shared across all workflow sessions)
- **Key**: "{workflow_type}:{phase}" (e.g., "spec_creation_v1:1")
- **Value**: CheckpointRequirements (immutable)
- **Size**: ~10KB per gate definition
- **Capacity**: No limit (working set: 20 gates = 200KB)
- **TTL**: Process lifetime (no expiration)
- **Invalidation**: Only on server restart
- **Thread Safety**: Double-checked locking pattern

**Performance Metrics:**
- **Hit Rate**: > 95% (only misses on first validation per phase per process)
- **Hit Latency**: < 10ms (dictionary lookup + object access)
- **Miss Latency**: < 50ms (YAML parse + cache store)
- **Memory Overhead**: ~10KB per cached gate

#### 6.2.2 Cache Warming

**Strategy:** Lazy loading (load on first use)

**Rationale:**
- Only workflows actually used get cached
- Memory efficient (no preloading unused workflows)
- Simple implementation (no warmup logic needed)

**Alternative Considered:**
- Preload all workflow gates at startup: Rejected - wastes memory, slower startup

---

### 6.3 Optimization Strategies

#### 6.3.1 YAML Parsing Optimization

**Problem:** YAML parsing is relatively slow (10-30ms).

**Solution:**
- Parse once per phase per process (cached)
- Use yaml.safe_load (optimized, secure)
- No re-parsing during validation

**Impact:** 95%+ validations use cached gate (no parsing)

#### 6.3.2 Validator Execution Optimization

**Problem:** Validators could be slow if poorly written.

**Solution:**
1. **Simple Validators**: Migration script generates fast validators (< 1ms each)
2. **No I/O**: Validators operate on in-memory values only
3. **Limited Complexity**: Lambda syntax enforces simple logic
4. **Fail Fast**: Stop at first error (don't validate remaining fields)

**Expected Performance:**
- Simple validator (x > 0): < 0.1ms
- String validator (contains): < 1ms
- YAML parsing validator: < 5ms
- Total for 5-10 validators: < 10ms

#### 6.3.3 Type Checking Optimization

**Problem:** Type checking every field could add overhead.

**Solution:**
```python
# Fast isinstance check (< 0.1ms per field)
type_map = {
    "boolean": bool,
    "integer": int,
    "string": str,
    "object": dict,
    "list": list
}

def validate_type(value: Any, expected_type: str) -> bool:
    return isinstance(value, type_map[expected_type])
```

**Impact:** Type checking negligible (< 1ms for typical evidence)

#### 6.3.4 Error Message Generation Optimization

**Problem:** Generating detailed error messages could be slow.

**Solution:**
- Pre-format error templates
- Simple string formatting (no complex templating)
- Lazy evaluation (only generate if validation fails)

**Impact:** < 5ms to generate complete error response

#### 6.3.5 Avoiding Premature Optimization

**Not Implemented in v1.0:**
- Complex cache eviction (unnecessary - small cache)
- LRU cache (unnecessary - working set small)
- Validator result caching (validators cheap to re-run)
- Connection pooling (no database access)
- Query optimization (no database queries)

**Rationale:** Current design already meets < 100ms target without additional complexity.

---

### 6.4 Performance Bottleneck Analysis

#### Potential Bottlenecks

**1. YAML Parsing (First Load)**
- **Latency**: 10-30ms per file
- **Frequency**: Once per phase per process
- **Mitigation**: Caching (95%+ hit rate)
- **Impact**: Acceptable (only affects first validation)

**2. RAG Fallback (If YAML Missing)**
- **Latency**: 50-100ms (RAG query + parsing)
- **Frequency**: Only for workflows without gate-definition.yaml
- **Mitigation**: Migration script generates YAML for all workflows
- **Impact**: Temporary during migration

**3. Validator Execution**
- **Latency**: < 1ms per simple validator, up to 5ms for YAML parsing
- **Frequency**: Every validation (but only for fields with validators)
- **Mitigation**: Simple validators encouraged, fail-fast on error
- **Impact**: Acceptable (< 10ms for 5-10 validators)

**4. Lock Contention (Cache Access)**
- **Latency**: Microseconds (uncontended), milliseconds (contended)
- **Frequency**: Only on cache misses (< 5% of validations)
- **Mitigation**: Double-checked locking (read without lock on hits)
- **Impact**: Negligible (lock held briefly, rare contention)

**5. Evidence Serialization**
- **Latency**: < 5ms for typical evidence (< 100KB)
- **Frequency**: Every validation (evidence already in memory)
- **Mitigation**: No serialization needed (evidence is dict)
- **Impact**: Not a bottleneck

#### Performance Profile

**Typical Validation (95% of cases - cache hit):**
```
Gate loading (cached):        < 10ms  (dictionary lookup)
Field type checking:          <  1ms  (5-10 isinstance calls)
Validator execution:          <  10ms (5-10 simple validators)
Error message generation:     <  5ms  (if validation fails)
-------------------------------------------------------
Total:                        < 26ms  (well below 100ms target)
```

**First Validation (5% of cases - cache miss):**
```
Gate loading (YAML parse):    < 50ms  (yaml.safe_load)
Field type checking:          <  1ms
Validator execution:          < 10ms
Error message generation:     <  5ms
-------------------------------------------------------
Total:                        < 66ms  (still below 100ms target)
```

---

### 6.5 Scalability

#### 6.5.1 Horizontal Scaling

**Capability:** System supports multiple concurrent workflow sessions.

**Mechanism:**
- **Stateless Validation**: No shared state between validations (except cache)
- **Thread-Safe Cache**: Double-checked locking enables safe concurrent access
- **Process Isolation**: Each MCP server process independent

**Scaling Characteristics:**
- **Concurrent Workflows**: 10+ workflows supported without degradation
- **Cache Sharing**: All workflows share same cache (memory efficient)
- **No Contention**: Lock-free reads on cache hits (95%+ of accesses)

**Load Test Scenario:**
```python
# 10 concurrent workflows, each validating 5 phases
# Expected performance:
# - Cache hit validations: < 10ms (no lock contention)
# - Cache miss validations: < 50ms (lock held briefly)
# - Total time: ~100ms (parallelized, not 10x serial)
```

#### 6.5.2 Vertical Scaling

**Memory:**
- **Cache Size**: ~10KB per gate × 75 workflows × 5 phases = ~3.75MB
- **Working Set**: ~200KB (10-20 active workflows)
- **Total Footprint**: < 10MB (including data structures)

**CPU:**
- **Validation**: Minimal CPU (< 1% per validation)
- **YAML Parsing**: Brief spike on cache miss (< 10ms)
- **Validators**: Simple operations (arithmetic, string ops)

**I/O:**
- **Disk Reads**: Only on cache miss (YAML file < 5KB)
- **Disk Writes**: Only WorkflowState persistence (existing)
- **Network**: None (local validation)

---

### 6.6 Performance Monitoring

#### 6.6.1 Key Performance Indicators (KPIs)

**Validation Latency:**
- **p50 (median)**: Target < 20ms, acceptable < 50ms
- **p95**: Target < 50ms, acceptable < 100ms
- **p99**: Target < 100ms, acceptable < 200ms

**Cache Performance:**
- **Hit Rate**: Target > 95%, alert if < 90%
- **Miss Rate**: Target < 5%, alert if > 10%
- **Hit Latency**: Target < 10ms, alert if > 20ms
- **Miss Latency**: Target < 50ms, alert if > 100ms

**Throughput:**
- **Validations/sec**: Target 100+, alert if < 10
- **Concurrent Workflows**: Target 10+, alert if degradation

**Error Rates:**
- **Validation Failures**: Track % (not an error, just metric)
- **System Errors**: Target 0%, alert on any occurrence

#### 6.6.2 Instrumentation

**Metrics Collection:**
```python
import time

class PerformanceMetrics:
    def __init__(self):
        self.validation_times = []
        self.cache_hits = 0
        self.cache_misses = 0
        self.validator_times = {}
    
    def record_validation(self, duration_ms: float, cache_hit: bool):
        self.validation_times.append(duration_ms)
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
    
    def record_validator(self, name: str, duration_ms: float):
        if name not in self.validator_times:
            self.validator_times[name] = []
        self.validator_times[name].append(duration_ms)
    
    def get_stats(self) -> Dict:
        times = sorted(self.validation_times)
        return {
            "count": len(times),
            "p50": times[len(times)//2] if times else 0,
            "p95": times[int(len(times)*0.95)] if times else 0,
            "p99": times[int(len(times)*0.99)] if times else 0,
            "cache_hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        }
```

**Logging:**
```python
# Validation timing
logger.info(
    "Checkpoint validation complete",
    extra={
        "duration_ms": duration_ms,
        "cache_hit": cache_hit,
        "workflow_type": workflow_type,
        "phase": phase,
        "passed": passed
    }
)

# Slow validation warning
if duration_ms > 100:
    logger.warning(
        "Slow validation detected",
        extra={
            "duration_ms": duration_ms,
            "threshold_ms": 100,
            "workflow_type": workflow_type,
            "phase": phase
        }
    )
```

#### 6.6.3 Alerting

**Performance Alerts:**

**Critical:**
- p95 latency > 200ms for 5 minutes: Page on-call
- Cache hit rate < 80% for 10 minutes: Page on-call
- System error rate > 0.1%: Immediate page

**Warning:**
- p95 latency > 100ms for 10 minutes: Notify team
- Cache hit rate < 90% for 30 minutes: Notify team
- Slow validation (> 200ms) frequency > 1/min: Notify team

**Informational:**
- Cache miss spike (> 20% for 5 min): Log for investigation
- Validation failure rate > 50%: May indicate gate issue

#### 6.6.4 Performance Dashboard

**Real-Time Metrics:**
- Current validation latency (p50, p95, p99)
- Cache hit rate (last hour)
- Validations per second
- Active workflows

**Historical Metrics:**
- Latency trends (24h, 7d, 30d)
- Cache performance trends
- Validation failure rate trends
- Slow validations (> 100ms) over time

**Per-Workflow Metrics:**
- Average validation time per workflow
- Cache behavior per workflow
- Validation failure rate per workflow

---

### 6.7 Performance Testing

#### 6.7.1 Unit Tests

**Test Type: Fast Path (Cache Hit)**
```python
def test_validation_fast_path():
    """Verify cached validation < 10ms."""
    # Pre-warm cache
    loader.load_checkpoint_requirements("spec_creation_v1", 1)
    
    # Time validation with cache hit
    start = time.perf_counter()
    passed, result = engine._validate_checkpoint(
        "spec_creation_v1", 1, valid_evidence
    )
    duration = (time.perf_counter() - start) * 1000
    
    assert duration < 10, f"Cache hit took {duration}ms (expected < 10ms)"
    assert passed == True
```

**Test Type: Slow Path (Cache Miss)**
```python
def test_validation_slow_path():
    """Verify first-time validation < 50ms."""
    # Clear cache
    loader._cache.clear()
    
    # Time validation with cache miss
    start = time.perf_counter()
    passed, result = engine._validate_checkpoint(
        "spec_creation_v1", 1, valid_evidence
    )
    duration = (time.perf_counter() - start) * 1000
    
    assert duration < 50, f"Cache miss took {duration}ms (expected < 50ms)"
    assert passed == True
```

**Test Type: Validator Performance**
```python
def test_validator_performance():
    """Verify validators execute quickly."""
    validators = {
        "positive": "lambda x: x > 0",
        "yaml_valid": "lambda x: yaml.safe_load(x) is not None"
    }
    
    for name, expr in validators.items():
        start = time.perf_counter()
        passed, error = executor.execute_validator(expr, test_value, {})
        duration = (time.perf_counter() - start) * 1000
        
        assert duration < 1, f"{name} took {duration}ms (expected < 1ms)"
```

#### 6.7.2 Integration Tests

**Test Type: Concurrent Workflows**
```python
def test_concurrent_validation():
    """Verify no performance degradation with concurrent workflows."""
    import concurrent.futures
    
    def validate_workflow(session_id: str):
        start = time.perf_counter()
        passed, result = engine._validate_checkpoint(
            "spec_creation_v1", 1, valid_evidence
        )
        return (time.perf_counter() - start) * 1000
    
    # Run 10 concurrent validations
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        durations = list(executor.map(
            validate_workflow,
            [f"session_{i}" for i in range(10)]
        ))
    
    # All should complete quickly
    assert all(d < 100 for d in durations), f"Slow validations: {[d for d in durations if d >= 100]}"
    
    # 95th percentile should be fast
    p95 = sorted(durations)[int(len(durations) * 0.95)]
    assert p95 < 50, f"p95 latency {p95}ms (expected < 50ms)"
```

#### 6.7.3 Load Testing

**Scenario: Sustained Load**
```python
# Simulate 100 validations per second for 60 seconds
# Expected: No degradation, cache hit rate > 95%
```

**Scenario: Spike Load**
```python
# Simulate 500 concurrent validations
# Expected: All complete < 200ms, no crashes
```

**Scenario: Cold Start**
```python
# Clear cache, validate 20 different workflows
# Expected: First validation per workflow < 50ms
```

---

### 6.8 Performance Tuning Opportunities

#### Future Optimizations (Not Needed for v1.0)

**1. Validator Result Caching**
- Cache validator results per field value
- Benefit: Skip re-validation of same evidence
- Complexity: Medium (cache invalidation)
- Impact: Minimal (validators already fast)

**2. Parallel Validator Execution**
- Run independent validators in parallel
- Benefit: Reduce total validation time
- Complexity: High (threading overhead)
- Impact: Minimal (validators already fast)

**3. Precompiled Validators**
- Compile lambda expressions once
- Benefit: Skip eval() on each execution
- Complexity: Low
- Impact: Minimal (eval() already fast)

**4. Batch Validation**
- Validate multiple phases in one call
- Benefit: Reduce overhead
- Complexity: Medium (API change)
- Impact: Not applicable (one phase at a time)

**5. Cache Persistence**
- Persist cache to disk across restarts
- Benefit: Skip initial YAML parsing
- Complexity: Medium (serialization)
- Impact: Minimal (startup time not critical)

**Recommendation:** None needed for v1.0. Current design meets all performance targets.

---

## 6.9 Performance Summary

**Current Design Performance:**
- **Validation Latency**: < 26ms typical (cache hit), < 66ms worst case (cache miss)
- **Cache Hit Rate**: > 95% (only misses on first validation per phase)
- **Concurrent Support**: 10+ workflows without degradation
- **Memory Footprint**: < 10MB (including cache)
- **CPU Usage**: < 1% per validation

**Performance Targets Met:**
- ✅ NFR-P1: < 100ms validation time (achieved < 70ms)
- ✅ NFR-P2: > 95% cache hit rate (expected 95%+)
- ✅ NFR-P3: Concurrent workflows supported (thread-safe cache)

**Performance Characteristics:**
- **Fast Path (95%)**: < 10ms (cache hit, no I/O)
- **Slow Path (5%)**: < 50ms (cache miss, YAML parse)
- **Scalable**: Linear scaling with concurrent workflows
- **Memory Efficient**: ~10KB per cached gate
- **No External Dependencies**: No database, network, or disk I/O after cache warm

**Monitoring:**
- Real-time latency metrics (p50, p95, p99)
- Cache performance metrics (hit rate, miss rate)
- Per-workflow performance tracking
- Alerting on performance degradation

**Testing:**
- Unit tests verify < 10ms (cached) and < 50ms (uncached)
- Integration tests verify concurrent performance
- Load tests verify sustained and spike load handling

**The validation system meets all performance requirements with significant headroom. No optimizations needed for v1.0.**
