# Implementation Tasks

**Project:** Parser Submodule Refactor  
**Date:** 2025-11-05  
**Status:** Draft - Pending Approval

---

## Time Estimates

- **Phase 0:** 0.5 hours (Foundation & Planning)
- **Phase 1:** 0.5 hours (Create Directory Structure)
- **Phase 2:** 1 hour (Extract Base Classes)
- **Phase 3:** 0.5 hours (Extract YAML Parser)
- **Phase 4:** 1.5 hours (Extract Markdown Utilities)
- **Phase 5:** 2 hours (Refactor SpecTasksParser & Implement Defensive Scoring)
- **Phase 6:** 0.5 hours (Update Consumers)
- **Phase 7:** 1.5 hours (Testing & Validation)
- **Phase 8:** 0.5 hours (Deprecation & Documentation)

**Total:** 8.5 hours (~2 days split across multiple sessions)

**Critical Path:** Phases 4-5 (utility extraction + refactor) are medium risk and block later phases.

---

## Phase 0: Foundation & Planning

**Objective:** Set up testing infrastructure and validate current baseline before any refactoring begins.

**Estimated Duration:** 0.5 hours

**Deliverables:**
- Baseline performance measurements captured
- Regression test suite prepared
- Git pre-refactor checkpoint created

---

## Phase 1: Create Directory Structure

**Objective:** Create the parsers/ submodule directory structure with empty placeholder files. No code changes yet.

**Estimated Duration:** 0.5 hours

**Deliverables:**
- `parsers/` directory created with 3 subpackages (markdown/, yaml/, shared/)
- 11 empty module files with `__init__.py` exports
- Structure validated (no code moved yet)

**Risk:** None (no code touched)

---

## Phase 2: Extract Base Classes

**Objective:** Move `SourceParser` ABC and `ParseError` exception to `base.py` while maintaining backward compatibility.

**Estimated Duration:** 1 hour

**Deliverables:**
- `SourceParser` and `ParseError` in `base.py`
- Backward-compatible imports in `task_parser.py`
- Deprecation warnings added
- Unit tests pass without modification

**Risk:** Low (maintains imports, adds deprecation warning)

---

## Phase 3: Extract YAML Parser

**Objective:** Move `WorkflowDefinitionParser` to `yaml/workflow_definition.py` as a test case for the refactor pattern.

**Estimated Duration:** 0.5 hours

**Deliverables:**
- `WorkflowDefinitionParser` in `yaml/workflow_definition.py`
- Backward-compatible import in `task_parser.py`
- Existing YAML parsing tests pass

**Risk:** Low (isolated, simple parser with no dependencies on other utilities)

---

## Phase 4: Extract Markdown Utilities

**Objective:** Extract shared utility functions from `SpecTasksParser` to dedicated utility modules (`traversal.py`, `extraction.py`, `shared/text.py`, `shared/dependencies.py`, `shared/validation.py`).

**Estimated Duration:** 1.5 hours

**Deliverables:**
- `traversal.py`: AST traversal utilities (5 functions, ~200 lines)
- `extraction.py`: Metadata extraction (4 functions, ~150 lines)
- `shared/text.py`: Generic text processing (6 functions, ~100 lines)
- `shared/dependencies.py`: Dependency resolution (4 functions, ~100 lines)
- `shared/validation.py`: Validation logic (2 functions, ~100 lines)
- Unit tests for each utility module

**Risk:** Medium (many dependencies, careful import management required)

**Critical:** This phase blocks Phase 5 refactor.

---

## Phase 5: Refactor SpecTasksParser & Implement Defensive Scoring

**Objective:** Slim down `SpecTasksParser` to use extracted utilities and implement the defensive semantic scoring algorithm with phase shift logic.

**Estimated Duration:** 2 hours

**Deliverables:**
- `markdown/spec_tasks.py`: Orchestration-only SpecTasksParser (~400 lines)
- `markdown/scoring.py`: NEW semantic scoring with confidence signals (~300 lines)
- Phase shift detection (+1 if Phase 0 exists)
- Task ID normalization (sequential integers)
- Dependency normalization (phase.task format with shift)
- Integration tests validate defensive parsing

**Risk:** Medium (main parser refactor + new functionality)

**Critical:** Core refactor phase, highest complexity.

---

## Phase 6: Update Consumers

**Objective:** Update import statements in workflow engine consumers to use new `parsers` submodule.

**Estimated Duration:** 0.5 hours

**Deliverables:**
- `dynamic_registry.py`: Updated imports
- `engine.py`: Updated imports (if needed)
- All consumers use `from parsers import SpecTasksParser`
- Backward-compatible imports still work (via `task_parser.py` shim)

**Risk:** Low (automated with IDE refactor tools)

---

## Phase 7: Testing & Validation

**Objective:** Comprehensive testing to ensure zero regressions and validate new defensive parsing capabilities.

**Estimated Duration:** 1.5 hours

**Deliverables:**
- Unit tests for all 11 modules (~10 test files)
- Integration tests for end-to-end parsing
- Regression tests on all completed specs (validate identical parsing)
- Performance benchmarks (validate ±5% variance)
- Defensive parsing tests (Phase 0 detection, gap validation, format variations)
- Test coverage ≥85%

**Risk:** Low (validation phase, can rollback if issues found)

---

## Phase 8: Deprecation & Documentation

**Objective:** Finalize deprecation of old `task_parser.py` and update documentation.

**Estimated Duration:** 0.5 hours

**Deliverables:**
- `task_parser.py` marked as deprecated compatibility shim
- Deprecation warnings emit with migration guidance
- Module docstrings updated
- Migration guide in README (if needed)
- Pre-commit hooks updated (file size validation for new modules)

**Risk:** None (maintains compatibility, documentation-only)

---



### Phase 0 Tasks (Detailed)

- [ ] **Task 0.1**: Capture baseline performance measurements
  - Run current parser on 4 benchmark specs (small, typical, large, extreme)
  - Measure parse time (p50, p95), memory usage (peak), task counts
  - Record results in `tests/benchmarks/baseline_results.json`
  - Verify measurements repeatable (run 3 times, <5% variance)
  - **Duration:** 15 minutes

- [ ] **Task 0.2**: Prepare regression test suite
  - Create `tests/regression/test_parser_regression.py`
  - Add test cases for all completed specs in `.praxis-os/specs/`
  - Verify tests pass with current implementation (100% pass rate)
  - Document test execution command
  - **Duration:** 15 minutes

- [ ] **Task 0.3**: Create git checkpoint
  - Commit all changes with message "Pre-refactor checkpoint"
  - Tag as `parser-refactor-baseline`
  - Push to remote (backup)
  - Verify clean working directory
  - **Duration:** 5 minutes

---

### Phase 1 Tasks (Detailed)

- [ ] **Task 1.1**: Create parsers directory structure
  - Create `subsystems/workflow/parsers/` directory
  - Create subdirectories: `markdown/`, `yaml/`, `shared/`
  - Add `__init__.py` to parsers/ and all subdirectories
  - Verify import paths resolve correctly
  - **Duration:** 10 minutes

- [ ] **Task 1.2**: Create placeholder module files
  - Touch `base.py` (50 lines placeholder)
  - Touch `markdown/{spec_tasks,scoring,traversal,extraction}.py` (4 files)
  - Touch `yaml/workflow_definition.py`
  - Touch `shared/{text,dependencies,validation}.py` (3 files)
  - Add module docstrings with purpose statements
  - **Duration:** 15 minutes

- [ ] **Task 1.3**: Validate structure
  - Run `python -m parsers` (should import without errors)
  - Verify all `__init__.py` files have `__all__` exports (empty for now)
  - Run linter on new files (zero errors)
  - Commit: "Phase 1: Create directory structure"
  - **Duration:** 5 minutes

---

### Phase 2 Tasks (Detailed)

- [ ] **Task 2.1**: Extract SourceParser ABC to base.py
  - Copy `SourceParser` class from `task_parser.py`
  - Add import for `DynamicPhase` from models
  - Add module docstring explaining abstract base
  - Verify abstract method enforcement (try instantiating, should fail)
  - **Duration:** 15 minutes

- [ ] **Task 2.2**: Extract ParseError to base.py
  - Copy `ParseError` exception class from `task_parser.py`
  - Add docstring with error message format guidance
  - Add example usage in docstring
  - **Duration:** 10 minutes

- [ ] **Task 2.3**: Add backward-compatible imports
  - In `task_parser.py`, import from `parsers.base`
  - Add deprecation warning with DeprecationWarning
  - Include migration guidance in warning message
  - Verify old imports still work: `from task_parser import SourceParser`
  - **Duration:** 15 minutes

- [ ] **Task 2.4**: Update exports
  - Update `parsers/__init__.py` to export SourceParser, ParseError
  - Test new import path: `from parsers import SourceParser`
  - Run unit tests (should pass without modification)
  - Commit: "Phase 2: Extract base classes"
  - **Duration:** 10 minutes

- [ ] **Task 2.5**: Validate backward compatibility
  - Run regression tests (100% pass)
  - Verify deprecation warnings appear
  - Check warning message clarity
  - **Duration:** 10 minutes

---

### Phase 3 Tasks (Detailed)

- [ ] **Task 3.1**: Copy WorkflowDefinitionParser to yaml/
  - Copy entire `WorkflowDefinitionParser` class to `workflow_definition.py`
  - Update imports to use `..base` (relative imports)
  - Add module docstring
  - **Duration:** 10 minutes

- [ ] **Task 3.2**: Add backward-compatible import in task_parser.py
  - Import from `parsers.yaml.workflow_definition`
  - Maintain `from task_parser import WorkflowDefinitionParser` compatibility
  - **Duration:** 5 minutes

- [ ] **Task 3.3**: Update parsers/__init__.py exports
  - Export WorkflowDefinitionParser
  - Verify new import: `from parsers import WorkflowDefinitionParser`
  - **Duration:** 5 minutes

- [ ] **Task 3.4**: Validate YAML parser
  - Run existing YAML parsing tests
  - Test both old and new import paths
  - Verify identical behavior
  - Commit: "Phase 3: Extract YAML parser"
  - **Duration:** 10 minutes

---

### Phase 4 Tasks (Detailed)

- [ ] **Task 4.1**: Extract AST traversal functions to traversal.py
  - Move `_get_text_content()` function (~50 lines)
  - Move `_extract_list_item_text()` function (~30 lines)
  - Move `_get_checkbox_marker()` function (~20 lines)
  - Move `_flush_inline_buffer()` function (~20 lines)
  - Add `find_headers()` utility function (~40 lines)
  - Add module docstring and function docstrings
  - Create `tests/unit/test_markdown_traversal.py` with 8+ test cases
  - **Duration:** 30 minutes

- [ ] **Task 4.2**: Extract metadata extraction functions to extraction.py
  - Move `_extract_metadata()` function (~40 lines)
  - Move `_extract_task_info()` function (~50 lines)
  - Move `_extract_task_dependencies()` function (~30 lines)
  - Add `extract_acceptance_criteria()` function (~30 lines)
  - Add module docstring and function docstrings
  - Create `tests/unit/test_markdown_extraction.py` with 6+ test cases
  - **Duration:** 30 minutes

- [ ] **Task 4.3**: Extract text utilities to shared/text.py
  - Move `_extract_first_number()` function (~15 lines)
  - Add `clean_text()` function (~15 lines)
  - Add `normalize_separator()` function (~20 lines)
  - Add `strip_formatting()` function (~20 lines)
  - Add `extract_keywords()` function (~30 lines)
  - Add module docstring and function docstrings
  - Create `tests/unit/test_shared_text.py` with 6+ test cases
  - **Duration:** 20 minutes

- [ ] **Task 4.4**: Extract dependency resolution to shared/dependencies.py
  - Create `parse_dependency_references()` function (~30 lines)
  - Create `apply_phase_shift()` function (~20 lines)
  - Create `validate_dependencies()` function (~30 lines)
  - Create `detect_circular_dependencies()` function (~20 lines)
  - Add module docstring and function docstrings
  - Create `tests/unit/test_shared_dependencies.py` with 8+ test cases
  - **Duration:** 25 minutes

- [ ] **Task 4.5**: Extract validation logic to shared/validation.py
  - Create `validate_phase_sequence()` function (~30 lines)
  - Create `validate_required_fields()` function (~20 lines)
  - Create `validate_task_id_format()` function (~15 lines)
  - Create `generate_error_message()` function (~35 lines)
  - Add module docstring and function docstrings
  - Create `tests/unit/test_shared_validation.py` with 6+ test cases
  - **Duration:** 25 minutes

---

### Phase 5 Tasks (Detailed)

- [ ] **Task 5.1**: Implement semantic scoring in scoring.py
  - Create `ScoredHeader` dataclass (~20 lines)
  - Implement `score_phase_header()` function (~60 lines)
    - Phase keyword detection (+40 points)
    - Single number detection (+25 points)
    - H2 level bonus (+15 points)
    - Separator detection (+10 points)
    - Negation penalties (-90% for "detailed breakdown")
  - Implement `score_task_header()` function (~60 lines)
    - Task keyword detection (+40 points)
    - Dotted number detection (+30 points)
    - H3 level bonus (+20 points)
    - Starts with number (+10 points)
    - Negation penalties (-30% for "tasks" plural)
  - Implement `score_all_headers()` function (~40 lines)
  - Add comprehensive module docstring with signal documentation
  - Create `tests/unit/test_markdown_scoring.py` with 15+ test cases
  - **Duration:** 45 minutes

- [ ] **Task 5.2**: Refactor SpecTasksParser to use utilities
  - Update spec_tasks.py to import all utilities
  - Replace internal methods with utility function calls
  - Keep only orchestration logic in class
  - Update constructor to accept threshold configuration
  - Verify reduced to ~400 lines (from ~700)
  - **Duration:** 30 minutes

- [ ] **Task 5.3**: Implement 7-phase defensive parsing algorithm
  - Implement `_score_headers()` method (calls scoring.py)
  - Implement `_classify_headers()` method (threshold comparison)
  - Implement `_detect_phase_shift()` method (Phase 0 detection)
  - Implement `_validate_phase_sequence()` method (gap validation)
  - Implement `_build_phase_structures()` method (task association)
  - Implement `_normalize_dependencies()` method (shift application)
  - Implement `_normalize_task_ids()` method (sequential numbering)
  - Update main `parse()` method to orchestrate 7 phases
  - **Duration:** 45 minutes

---

### Phase 6 Tasks (Detailed)

- [ ] **Task 6.1**: Update DynamicContentRegistry imports
  - Locate import statement in `dynamic_registry.py`
  - Change from `task_parser` to `parsers`
  - Verify registry still loads parsers correctly
  - **Duration:** 10 minutes

- [ ] **Task 6.2**: Update WorkflowEngine imports (if needed)
  - Check if `engine.py` directly imports parsers
  - Update any direct imports to use `parsers` submodule
  - Verify workflow execution unaffected
  - **Duration:** 10 minutes

- [ ] **Task 6.3**: Search for other parser consumers
  - Grep codebase for `from.*task_parser import`
  - Update any additional consumers found
  - Document all import locations changed
  - **Duration:** 10 minutes

---

### Phase 7 Tasks (Detailed)

- [ ] **Task 7.1**: Create unit tests for all modules
  - `tests/unit/test_base.py` (ParseError, ABC enforcement)
  - `tests/unit/test_markdown_spec_tasks.py` (end-to-end parsing)
  - `tests/unit/test_yaml_workflow_definition.py` (YAML parsing)
  - Verify test coverage ≥85% (run coverage report)
  - **Duration:** 30 minutes

- [ ] **Task 7.2**: Create integration tests
  - `tests/integration/test_parser_integration.py`
  - Test SpecTasksParser with real spec files
  - Test phase shift detection with Phase 0 spec
  - Test gap validation with malformed spec
  - Test cross-phase dependencies
  - **Duration:** 20 minutes

- [ ] **Task 7.3**: Run regression tests on all completed specs
  - Execute regression suite on `.praxis-os/specs/completed/*/tasks.md`
  - Verify 100% pass rate (identical parsing results)
  - Document any specs that parse differently (should be improvements)
  - **Duration:** 15 minutes

- [ ] **Task 7.4**: Run performance benchmarks
  - Execute benchmark suite on 4 workload sizes
  - Compare against baseline (Phase 0 measurements)
  - Verify ±5% variance (76ms-84ms for typical 40KB spec)
  - Document any performance improvements
  - **Duration:** 15 minutes

- [ ] **Task 7.5**: Test defensive parsing capabilities
  - Test Phase 0 detection and shift
  - Test format variation handling (different header styles)
  - Test gap detection (missing phases)
  - Test circular dependency detection
  - Test invalid phase starts (not 0 or 1)
  - **Duration:** 20 minutes

---

### Phase 8 Tasks (Detailed)

- [ ] **Task 8.1**: Finalize task_parser.py deprecation shim
  - Keep only imports from parsers submodule
  - Add prominent deprecation warning at module level
  - Include "will be removed in version X" timeline
  - Add migration guidance in docstring
  - **Duration:** 15 minutes

- [ ] **Task 8.2**: Update module docstrings
  - Add comprehensive docstrings to all 11 modules
  - Document module purpose, key functions, usage examples
  - Add cross-references between related modules
  - **Duration:** 15 minutes

- [ ] **Task 8.3**: Add pre-commit hooks for file size validation
  - Create `.pre-commit-config.yaml` rule for 500-line limit
  - Exclude `task_parser.py` from check (legacy file)
  - Test pre-commit hook on new modules
  - **Duration:** 10 minutes

- [ ] **Task 8.4**: Final validation and commit
  - Run full test suite (unit + integration + regression)
  - Run linter (zero errors)
  - Run type checker (mypy, zero errors)
  - Verify backward compatibility (old imports work with warnings)
  - Create final commit: "Phase 8: Complete parser refactor"
  - Tag release: `parser-refactor-v1.0`
  - **Duration:** 10 minutes

---


## Acceptance Criteria (By Task)

### Phase 0 Acceptance Criteria

**Task 0.1 Acceptance Criteria:**
- [ ] Baseline measurements captured for 4 specs (small, typical, large, extreme)
- [ ] JSON results file created with parse_time_ms, memory_mb, phase_count, task_count
- [ ] Measurements repeatable (<5% variance across 3 runs)
- [ ] Documented in `tests/benchmarks/README.md`

**Task 0.2 Acceptance Criteria:**
- [ ] Regression test file created with at least 10 test cases
- [ ] Tests cover all completed specs in `.praxis-os/specs/`
- [ ] 100% pass rate with current implementation
- [ ] Test execution command documented

**Task 0.3 Acceptance Criteria:**
- [ ] Git commit created with "Pre-refactor checkpoint" message
- [ ] Tag `parser-refactor-baseline` created
- [ ] Pushed to remote successfully
- [ ] `git status` shows clean working directory

---

### Phase 1 Acceptance Criteria

**Task 1.1 Acceptance Criteria:**
- [ ] Directory `subsystems/workflow/parsers/` exists
- [ ] Subdirectories markdown/, yaml/, shared/ created
- [ ] All directories have `__init__.py` files
- [ ] Import test passes: `python -c "import subsystems.workflow.parsers"`

**Task 1.2 Acceptance Criteria:**
- [ ] 11 module files created (base.py + 4 markdown + 1 yaml + 3 shared + 2 init)
- [ ] Each file has module-level docstring with purpose
- [ ] Placeholder imports don't cause errors
- [ ] Linter shows zero errors on new files

**Task 1.3 Acceptance Criteria:**
- [ ] `python -m parsers` executes without ImportError
- [ ] All `__init__.py` files have `__all__` defined (empty lists ok)
- [ ] Pylint/flake8 show zero errors
- [ ] Git commit created: "Phase 1: Create directory structure"

---

### Phase 2 Acceptance Criteria

**Task 2.1 Acceptance Criteria:**
- [ ] `SourceParser` class in `base.py` with `parse()` abstract method
- [ ] ABC import from `abc` module present
- [ ] Attempting to instantiate raises TypeError (abstract method)
- [ ] Type hints present on all methods

**Task 2.2 Acceptance Criteria:**
- [ ] `ParseError` exception class in `base.py`
- [ ] Inherits from Exception
- [ ] Docstring includes error message format guidance
- [ ] Example usage included in docstring

**Task 2.3 Acceptance Criteria:**
- [ ] `task_parser.py` imports from `parsers.base`
- [ ] DeprecationWarning emitted when importing from `task_parser`
- [ ] Warning message includes "use parsers submodule instead"
- [ ] Old import path still functional: `from task_parser import SourceParser`

**Task 2.4 Acceptance Criteria:**
- [ ] `parsers/__init__.py` exports SourceParser and ParseError in `__all__`
- [ ] New import works: `from parsers import SourceParser, ParseError`
- [ ] All unit tests pass without modification
- [ ] No new linter errors introduced

**Task 2.5 Acceptance Criteria:**
- [ ] Regression test suite passes 100%
- [ ] Deprecation warnings visible in test output
- [ ] Warning messages are clear and actionable
- [ ] Git commit created: "Phase 2: Extract base classes"

---

### Phase 3 Acceptance Criteria

**Task 3.1 Acceptance Criteria:**
- [ ] `WorkflowDefinitionParser` class in `yaml/workflow_definition.py`
- [ ] Uses relative import `from ..base import SourceParser`
- [ ] Module docstring explains YAML parsing purpose
- [ ] No syntax errors, imports resolve correctly

**Task 3.2 Acceptance Criteria:**
- [ ] `task_parser.py` imports WorkflowDefinitionParser from parsers.yaml
- [ ] Old import path still works with deprecation warning
- [ ] No duplicate class definitions

**Task 3.3 Acceptance Criteria:**
- [ ] WorkflowDefinitionParser in `parsers/__init__.py` `__all__`
- [ ] New import works: `from parsers import WorkflowDefinitionParser`
- [ ] Type hints maintained

**Task 3.4 Acceptance Criteria:**
- [ ] Existing YAML parsing tests pass (100%)
- [ ] Both old and new imports tested
- [ ] Identical behavior verified (same output for same input)
- [ ] Git commit created: "Phase 3: Extract YAML parser"

---

### Phase 4 Acceptance Criteria

**Task 4.1 Acceptance Criteria:**
- [ ] 5 functions extracted to `traversal.py` (~200 lines total)
- [ ] All functions have docstrings with parameters, returns, examples
- [ ] Test file `test_markdown_traversal.py` created with ≥8 test cases
- [ ] Test coverage ≥85% for traversal.py
- [ ] All tests passing

**Task 4.2 Acceptance Criteria:**
- [ ] 4 functions extracted to `extraction.py` (~150 lines total)
- [ ] All functions have type hints
- [ ] Test file `test_markdown_extraction.py` created with ≥6 test cases
- [ ] Test coverage ≥85% for extraction.py
- [ ] All tests passing

**Task 4.3 Acceptance Criteria:**
- [ ] 5 functions in `shared/text.py` (~100 lines total)
- [ ] Pure functions (no side effects, no state)
- [ ] Test file `test_shared_text.py` created with ≥6 test cases
- [ ] Test coverage ≥85% for text.py
- [ ] All tests passing

**Task 4.4 Acceptance Criteria:**
- [ ] 4 functions in `shared/dependencies.py` (~100 lines total)
- [ ] Circular dependency detection implemented with DFS algorithm
- [ ] Test file `test_shared_dependencies.py` created with ≥8 test cases
- [ ] Test coverage ≥85% for dependencies.py
- [ ] All tests passing, including circular detection

**Task 4.5 Acceptance Criteria:**
- [ ] 4 functions in `shared/validation.py` (~100 lines total)
- [ ] Error messages include remediation guidance ("Fix: ...")
- [ ] Test file `test_shared_validation.py` created with ≥6 test cases
- [ ] Test coverage ≥85% for validation.py
- [ ] All tests passing
- [ ] Git commit: "Phase 4: Extract utilities"

---

### Phase 5 Acceptance Criteria

**Task 5.1 Acceptance Criteria:**
- [ ] `ScoredHeader` dataclass defined with 5 fields
- [ ] `score_phase_header()` implements 4 positive signals, 1 negative
- [ ] `score_task_header()` implements 4 positive signals, 1 negative
- [ ] Test file with ≥15 test cases covering all signals
- [ ] Test coverage ≥90% for scoring.py (critical path)
- [ ] Signal weights documented in module docstring

**Task 5.2 Acceptance Criteria:**
- [ ] SpecTasksParser imports all 5 utility modules
- [ ] Internal methods replaced with utility function calls
- [ ] File reduced to ≤400 lines (from ~700)
- [ ] Constructor accepts phase_threshold and task_threshold parameters
- [ ] No functionality regressions

**Task 5.3 Acceptance Criteria:**
- [ ] All 7 methods implemented (_score_headers through _normalize_task_ids)
- [ ] Main parse() method orchestrates 7-phase algorithm
- [ ] Phase shift logic: +1 if min(phases) == 0, error if min > 1
- [ ] Task IDs normalized to "1", "2", "3" (not "0.1", "1.1")
- [ ] Dependencies preserved as "phase.task" format with shift applied
- [ ] Integration test validates full algorithm on real spec
- [ ] Git commit: "Phase 5: Implement defensive parsing"

---

### Phase 6 Acceptance Criteria

**Task 6.1 Acceptance Criteria:**
- [ ] DynamicContentRegistry import changed to `from parsers import`
- [ ] Registry still loads SpecTasksParser successfully
- [ ] No runtime errors during workflow initialization

**Task 6.2 Acceptance Criteria:**
- [ ] WorkflowEngine imports updated (if any direct imports exist)
- [ ] Workflow execution test passes
- [ ] get_task() calls work correctly

**Task 6.3 Acceptance Criteria:**
- [ ] Grep results documented for all `task_parser` imports
- [ ] All consumer imports updated
- [ ] List of changed files recorded
- [ ] Git commit: "Phase 6: Update consumers"

---

### Phase 7 Acceptance Criteria

**Task 7.1 Acceptance Criteria:**
- [ ] Unit test files created for all 11 modules
- [ ] Total test coverage ≥85% across parser submodule
- [ ] All tests passing (100% pass rate)
- [ ] Coverage report generated and saved

**Task 7.2 Acceptance Criteria:**
- [ ] Integration test file created with ≥5 test scenarios
- [ ] Phase shift test: spec with Phase 0 parses correctly
- [ ] Gap validation test: malformed spec raises ParseError
- [ ] Cross-phase dependency test passes
- [ ] All integration tests passing

**Task 7.3 Acceptance Criteria:**
- [ ] Regression suite run on all `.praxis-os/specs/completed/*/tasks.md`
- [ ] 100% pass rate (or documented improvements only)
- [ ] No specs parse worse than before
- [ ] Results logged to `tests/regression/results.log`

**Task 7.4 Acceptance Criteria:**
- [ ] Benchmark suite executed on 4 workload sizes
- [ ] All results within ±5% of baseline
- [ ] Typical (40KB) spec: 76-84ms (target: 80ms ±5%)
- [ ] Performance comparison table generated

**Task 7.5 Acceptance Criteria:**
- [ ] Phase 0 detection test: correctly shifts to Phase 1
- [ ] Format variation test: handles different header styles
- [ ] Gap detection test: raises ParseError for [1,3,5]
- [ ] Circular dependency test: detects A→B→C→A cycle
- [ ] Invalid start test: raises ParseError for Phase 2 start
- [ ] All defensive tests passing

---

### Phase 8 Acceptance Criteria

**Task 8.1 Acceptance Criteria:**
- [ ] `task_parser.py` contains only imports + warning (≤30 lines)
- [ ] Module-level warning includes timeline ("version 2.0")
- [ ] Docstring explains deprecation and migration path
- [ ] Warning emitted when module imported

**Task 8.2 Acceptance Criteria:**
- [ ] All 11 modules have comprehensive docstrings
- [ ] Each docstring includes purpose, usage example, cross-references
- [ ] Public functions have complete docstrings (params, returns, raises, examples)
- [ ] Docstring linter (pydocstyle) shows zero errors

**Task 8.3 Acceptance Criteria:**
- [ ] `.pre-commit-config.yaml` includes file-size-limit hook
- [ ] Hook configured for 500-line limit
- [ ] `task_parser.py` excluded from hook
- [ ] Pre-commit test passes on all new modules
- [ ] Hook triggers on 501-line file (tested with dummy file)

**Task 8.4 Acceptance Criteria:**
- [ ] Full test suite passes: unit (≥85% coverage) + integration + regression (100%)
- [ ] Linter shows zero errors (pylint, flake8)
- [ ] Type checker shows zero errors (mypy --strict)
- [ ] Backward compatibility verified (old imports work with warnings)
- [ ] Git commit: "Phase 8: Complete parser refactor"
- [ ] Git tag: `parser-refactor-v1.0`
- [ ] All 40 tasks completed and checked off

---


## Dependencies

### Phase-Level Dependencies

```
Phase 0 (Foundation)
    ↓
Phase 1 (Structure) ← No code dependencies, just directory creation
    ↓
Phase 2 (Base Classes) ← Requires directory structure from Phase 1
    ↓
Phase 3 (YAML Parser) ← Requires base classes from Phase 2
    ↓
Phase 4 (Utilities) ← Requires base classes, independent of Phase 3
    ↓
Phase 5 (Refactor + Scoring) ← **CRITICAL** Requires all utilities from Phase 4
    ↓
Phase 6 (Consumers) ← Requires refactored parsers from Phase 5
    ↓
Phase 7 (Testing) ← Requires all code complete (Phases 1-6)
    ↓
Phase 8 (Deprecation) ← Requires testing validated (Phase 7)
```

### Phase 0 → Phase 1
Phase 1 (directory creation) can proceed immediately after Phase 0 baseline is captured. No code dependencies, but baseline provides rollback point.

### Phase 1 → Phase 2
Phase 2 (base class extraction) requires directory structure from Phase 1. Cannot create `base.py` without `parsers/` directory existing.

### Phase 2 → Phase 3
Phase 3 (YAML parser) requires `SourceParser` ABC and `ParseError` from Phase 2. WorkflowDefinitionParser inherits from SourceParser.

### Phase 2 → Phase 4
Phase 4 (utilities) requires base classes but is independent of Phase 3. Can be done in parallel with Phase 3, but both need Phase 2 complete.

### Phase 4 → Phase 5
**CRITICAL PATH:** Phase 5 (refactor) cannot proceed without all utilities from Phase 4. SpecTasksParser will call functions from traversal.py, extraction.py, scoring.py, text.py, dependencies.py, validation.py.

### Phase 5 → Phase 6
Phase 6 (consumer updates) requires new import paths from refactored Phase 5. Cannot update imports before parsers exist.

### Phases 1-6 → Phase 7
Phase 7 (testing) validates all previous work. Requires complete implementation through Phase 6.

### Phase 7 → Phase 8
Phase 8 (deprecation finalization) only proceeds after Phase 7 validates zero regressions.

---

### Task-Level Dependencies

#### Phase 0 (Independent Tasks)
- Task 0.1, 0.2: Can run in parallel
- Task 0.3: Requires 0.1 and 0.2 complete (git checkpoint after baseline + tests)

#### Phase 1 (Sequential)
- Task 1.1 → 1.2 → 1.3 (must be sequential)

#### Phase 2 (Mostly Sequential)
- Task 2.1, 2.2: Can run in parallel (both extract to base.py)
- Task 2.3: Requires 2.1 and 2.2 complete (backward-compat imports)
- Task 2.4: Requires 2.3 (exports depend on imports)
- Task 2.5: Requires 2.4 (validation of complete phase)

#### Phase 3 (Sequential)
- Task 3.1 → 3.2 → 3.3 → 3.4 (must be sequential)

#### Phase 4 (Parallel Extraction + Sequential Validation)
- **Parallel Group:** Tasks 4.1, 4.2, 4.3, 4.4, 4.5 can run in parallel
  - Each extracts to independent file
  - No interdependencies between utilities
  - **Time Savings:** ~2 hours if done serially, ~45 minutes if parallel (longest task duration)

#### Phase 5 (Sequential)
- Task 5.1 → 5.2 → 5.3
- Task 5.2 requires 5.1 (refactor needs scoring.py)
- Task 5.3 requires 5.2 (algorithm needs refactored structure)

#### Phase 6 (Parallel Updates)
- Tasks 6.1, 6.2, 6.3 can run in parallel (independent file updates)

#### Phase 7 (Test Types Can Parallelize)
- Tasks 7.1, 7.2: Can run in parallel (unit vs integration)
- Task 7.3: Requires 7.1 and 7.2 (regression needs unit + integration passing)
- Tasks 7.4, 7.5: Can run in parallel after 7.3 (benchmarks + defensive tests)

#### Phase 8 (Sequential)
- Task 8.1 → 8.2 → 8.3 → 8.4 (must be sequential)

---

### Critical Path Analysis

**Critical Path (Longest Dependency Chain):**
```
Phase 0 (0.5h)
→ Phase 1 (0.5h)
→ Phase 2 (1h)
→ Phase 4 (1.5h) ← Can't parallelize if working solo
→ Phase 5 (2h) ← Largest single phase
→ Phase 6 (0.5h)
→ Phase 7 (1.5h)
→ Phase 8 (0.5h)

Total Critical Path: 8 hours
```

**Bottlenecks:**
1. **Phase 4:** Utility extraction blocks Phase 5
2. **Phase 5:** Largest phase (2 hours), blocks everything downstream
3. **Phase 7:** Testing validation gates deployment

**Optimization Opportunities:**
- Phase 4 tasks (4.1-4.5) can be done in parallel → saves ~1 hour if pair programming
- Phase 3 (YAML parser) can be done in parallel with Phase 4 → no time savings on critical path
- Phase 6 tasks (6.1-6.3) in parallel → saves ~10 minutes
- Phase 7 tasks partially parallel → saves ~20 minutes

**Realistic Timeline:**
- **Solo developer:** 8-8.5 hours (critical path + overhead)
- **Pair programming:** 7 hours (parallelizing Phase 4 tasks)
- **Split across sessions:** 2-3 days (context switching overhead)

---

### Dependency Validation

**Checked:**
- ✅ No circular dependencies identified
- ✅ All dependencies are necessary (code requires prerequisite)
- ✅ Parallel tasks are truly independent (no shared state)
- ✅ Blocking tasks identified (Phase 4 → 5, Phase 7 validation)

**Parallel Task Groups:**
1. Phase 0: Tasks 0.1, 0.2
2. Phase 2: Tasks 2.1, 2.2
3. Phase 4: Tasks 4.1, 4.2, 4.3, 4.4, 4.5 ← Biggest parallelization opportunity
4. Phase 6: Tasks 6.1, 6.2, 6.3
5. Phase 7: Tasks 7.1, 7.2 (then 7.4, 7.5)

**Sequential Constraint Tasks:**
- Phase 5 (all tasks sequential - refactor is monolithic)
- Phase 8 (all tasks sequential - finalization order matters)

---


## Phase Validation Gates

### Phase 0 Validation Gate

**Before advancing to Phase 1:**
- [ ] Baseline measurements captured and documented
- [ ] Regression test suite prepared (≥10 test cases)
- [ ] Git checkpoint created and pushed
- [ ] Clean working directory confirmed
- [ ] Baseline results saved to `tests/benchmarks/baseline_results.json`

**Quality Check:**
- Measurements repeatable (<5% variance across 3 runs)
- All completed specs have regression tests
- Rollback point established

---

### Phase 1 Validation Gate

**Before advancing to Phase 2:**
- [ ] All 11 module files created
- [ ] Directory structure validated (parsers/{markdown,yaml,shared})
- [ ] All `__init__.py` files present with `__all__` defined
- [ ] Import test passes: `python -m parsers`
- [ ] Linter shows zero errors on new files
- [ ] Git commit: "Phase 1: Create directory structure"

**Quality Check:**
- No code functionality changed (just structure created)
- Import paths resolve correctly
- No syntax errors

---

### Phase 2 Validation Gate

**Before advancing to Phase 3:**
- [ ] SourceParser ABC and ParseError extracted to base.py
- [ ] Backward-compatible imports in task_parser.py work
- [ ] Deprecation warnings emit correctly
- [ ] Old import path still functional
- [ ] New import path works: `from parsers import SourceParser`
- [ ] All unit tests pass (100%)
- [ ] Regression test suite passes (100%)
- [ ] Git commit: "Phase 2: Extract base classes"

**Quality Check:**
- Zero breaking changes
- Deprecation warnings clear and actionable
- Abstract method enforcement works (TypeError on instantiation)

---

### Phase 3 Validation Gate

**Before advancing to Phase 4:**
- [ ] WorkflowDefinitionParser extracted to yaml/workflow_definition.py
- [ ] Both old and new imports work correctly
- [ ] Existing YAML parsing tests pass (100%)
- [ ] Identical behavior verified (same input → same output)
- [ ] Backward compatibility maintained
- [ ] Git commit: "Phase 3: Extract YAML parser"

**Quality Check:**
- No YAML parsing regressions
- Parser isolation validated (independent of SpecTasksParser)

---

### Phase 4 Validation Gate

**Before advancing to Phase 5:**
- [ ] All 5 utility modules created (traversal, extraction, text, dependencies, validation)
- [ ] Total ≥650 lines extracted to utilities (from ~700 in monolithic file)
- [ ] Each module has ≥85% test coverage
- [ ] All utility tests passing (≥38 test cases total)
- [ ] Module boundaries clean (no circular imports)
- [ ] Pure functions validated (no side effects in shared/)
- [ ] Git commit: "Phase 4: Extract utilities"

**Quality Check:**
- Utilities independently testable
- Functions are composable
- No duplicate logic between modules
- Import dependencies flow one-way

**🚨 CRITICAL GATE:** This phase blocks Phase 5 refactor. Do not proceed if any utility tests failing.

---

### Phase 5 Validation Gate

**Before advancing to Phase 6:**
- [ ] scoring.py created with semantic scoring (~300 lines)
- [ ] SpecTasksParser refactored to ≤400 lines (from ~700)
- [ ] 7-phase defensive parsing algorithm implemented
- [ ] Phase shift detection working (+1 if Phase 0 exists)
- [ ] Task ID normalization working (sequential integers)
- [ ] Dependency normalization working (phase.task format with shift)
- [ ] Integration test validates full algorithm on real spec
- [ ] Test coverage ≥85% for scoring.py and spec_tasks.py
- [ ] Git commit: "Phase 5: Implement defensive parsing"

**Quality Check:**
- SpecTasksParser uses utilities (not duplicated code)
- Semantic scoring handles format variations
- Phase 0 correctly shifts to workflow Phase 1
- Gap validation raises ParseError
- Circular dependency detection works

**🚨 CRITICAL GATE:** Core refactor complete. Do not proceed if parsing logic broken.

---

### Phase 6 Validation Gate

**Before advancing to Phase 7:**
- [ ] All consumer imports updated (DynamicContentRegistry, WorkflowEngine, etc.)
- [ ] Parsers load successfully in workflow engine
- [ ] No runtime import errors
- [ ] Grep verified all task_parser imports updated
- [ ] List of changed files documented
- [ ] Git commit: "Phase 6: Update consumers"

**Quality Check:**
- Workflow engine starts without errors
- Parsers accessible via new import paths
- No broken imports in codebase

---

### Phase 7 Validation Gate

**Before advancing to Phase 8:**
- [ ] Unit tests created for all 11 modules (≥10 test files)
- [ ] Integration tests created (≥5 test scenarios)
- [ ] Regression suite passes 100% (all completed specs)
- [ ] Performance benchmarks within ±5% of baseline
- [ ] Defensive parsing tests pass (5 scenarios)
- [ ] Test coverage ≥85% across parser submodule
- [ ] All tests passing (unit + integration + regression)
- [ ] Coverage report generated and reviewed

**Quality Check:**
- No regressions detected
- Performance maintained (typical spec: 76-84ms)
- Phase shift detection validated
- Format variation handling verified
- Gap validation working
- Circular dependency detection working

**🚨 CRITICAL GATE:** Validation phase. Do not proceed if any regressions or performance degradation detected.

---

### Phase 8 Validation Gate

**Before marking project complete:**
- [ ] task_parser.py finalized as deprecation shim (≤30 lines)
- [ ] All module docstrings comprehensive
- [ ] Pre-commit hook configured (500-line limit)
- [ ] Full test suite passes (100%)
- [ ] Linter shows zero errors (pylint, flake8)
- [ ] Type checker shows zero errors (mypy --strict)
- [ ] Backward compatibility confirmed (old imports work with warnings)
- [ ] Git commit: "Phase 8: Complete parser refactor"
- [ ] Git tag: `parser-refactor-v1.0`

**Quality Check:**
- Documentation complete
- Pre-commit hooks prevent future file size violations
- Deprecation timeline communicated
- Migration path documented

---

## Project Completion Criteria

**All phases must pass validation gates AND:**
- [ ] 100% of acceptance criteria met (≥170 criteria across 40 tasks)
- [ ] Zero regressions on existing specs
- [ ] Performance maintained or improved (±5% acceptable)
- [ ] Backward compatibility maintained
- [ ] Test coverage ≥85%
- [ ] All 11 modules ≤500 lines each
- [ ] No circular imports
- [ ] Linter + type checker clean
- [ ] Documentation complete
- [ ] Git tagged: `parser-refactor-v1.0`

**Rollback Criteria (If Any Gate Fails):**
- Revert to `parser-refactor-baseline` tag (Phase 0 checkpoint)
- Document issues encountered
- Revise design docs based on lessons learned
- Re-plan phases before attempting again

---

## Success Metrics

**Technical Metrics:**
- ✅ File count: 1 file (1,005 lines) → 11 files (≤500 lines each)
- ✅ Extensibility: Add new parser = create new subpackage (no core file edits)
- ✅ Test coverage: Current ~70% → Target ≥85%
- ✅ Performance: Maintained within ±5% (no degradation)
- ✅ Backward compatibility: 100% (deprecation warnings, not breaks)

**Process Metrics:**
- ✅ All 9 phases completed sequentially
- ✅ All 40 tasks completed with acceptance criteria met
- ✅ All 8 validation gates passed
- ✅ Zero regressions introduced
- ✅ Timeline: 8-8.5 hours actual vs. 8.5 hours estimated

**Quality Metrics:**
- ✅ Zero blocking issues in production
- ✅ Zero hotfixes required post-deployment
- ✅ Developer feedback positive (easier to navigate, understand)
- ✅ Future parser additions take ≤4 hours (measured in Phase 2 follow-up)

---

