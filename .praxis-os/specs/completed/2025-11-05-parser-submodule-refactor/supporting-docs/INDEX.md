# Supporting Documents Index

**Spec:** Parser Submodule Refactor  
**Created:** 2025-11-05  
**Total Documents:** 2

## Document Catalog

### 1. Parser Submodule Architecture

**File:** `2025-11-05-parser-submodule-architecture.md`  
**Type:** Architectural Design Document  
**Size:** 26KB  
**Purpose:** Defines the clean architecture for refactoring the monolithic task_parser.py (1,005 lines) into a modular submodule structure with clear separation of concerns. Prevents tech debt accumulation before adding defensive parsing logic.

**Relevance:** Requirements [H], Design [H], Implementation [H]

**Key Topics:**
- Submodule directory structure (`parsers/markdown/`, `parsers/yaml/`, `parsers/shared/`)
- File size targets (50-400 lines per module vs. single 1,500-line file)
- Migration strategy (8-phase incremental approach)
- Future extensibility (Jira, GitHub, Notion parsers)
- Trade-off analysis (4 alternatives evaluated)
- Testing strategy per module

**Standout Insights:**
- Lessons learned from MCP Server 5K→30K line organic growth
- Clean architecture prevents repeating tech debt patterns
- 6-7 hour one-time investment prevents future monolithic file
- Backward compatibility maintained with deprecation shim
- Plugin-like architecture for easy parser additions

---

### 2. Defensive Task Parser with Phase Shift

**File:** `2025-11-05-defensive-task-parser-with-phase-shift.md`  
**Type:** Technical Design Document  
**Size:** 15KB  
**Purpose:** Defines the defensive parsing algorithm using semantic scoring instead of rigid pattern matching. Handles format variations from probabilistic AI systems (spec_creation_v1 workflow). Implements phase shift detection for workflow harness integration.

**Relevance:** Requirements [H], Design [H], Implementation [M]

**Key Topics:**
- Semantic header scoring (confidence-based classification)
- Phase shift detection (Phase 0 → workflow Phase 1)
- Gap validation (prevent GIGO with quality gates)
- Task/dependency normalization (task_id vs dependencies format)
- 7-phase parsing algorithm
- Error handling strategies

**Standout Insights:**
- Probabilistic AI drift is inevitable, parser must be defensive
- Current rigid parser fails: Phase 0 not recognized, 27 tasks dumped into Phase 4
- Phase shift required for spec_execution_v1 workflow harness
- Task IDs normalized to just numbers ("1", "2", "3")
- Dependencies kept as "phase.task" format ("1.1", "1.2") for cross-phase tracking
- Cross-phase dependencies explicitly supported

---

## Cross-Document Analysis

**Common Themes:**
1. **Tech Debt Prevention:** Both documents motivated by preventing monolithic growth patterns
2. **Clean Architecture:** Emphasis on separation of concerns and clear boundaries
3. **Extensibility:** Design for future parser additions without touching existing code
4. **Defensive Programming:** Handle variations gracefully instead of rigid patterns
5. **Testing Strategy:** Modular structure enables focused unit tests

**Document Relationship:**
- Architecture doc (Doc 1) defines **WHERE** code will live (structure)
- Defensive parser doc (Doc 2) defines **WHAT** code will do (algorithm)
- Both must be implemented together for complete solution
- Defensive parsing logic will be implemented IN the new submodule structure

**Implementation Dependencies:**
- Doc 1 provides the structural foundation (create submodule)
- Doc 2 provides the scoring logic (implement in `markdown/scoring.py`)
- Migration can happen incrementally: refactor first, then add features

**Potential Conflicts:**
- **None identified** - Documents are complementary, not contradictory
- Timeline estimates differ: Doc 1 estimates 6-7 hours total, Doc 2 doesn't specify
- Combined estimate: ~6-7 hours (refactor overlaps with feature implementation)

**Coverage Gaps:**
1. **Testing Specs:** Neither doc specifies exact test cases, only strategy
2. **Rollback Plan:** What if refactor causes issues in production?
3. **Performance Benchmarks:** No baseline or target performance metrics
4. **Migration Validation:** How to prove zero regressions during refactor?
5. **Documentation Updates:** What docs need updating after refactor?

---

## Document Insights Summary

### Requirements Domain (SRD Input)

**Functional Requirements:**
- FR-001: Parser must handle format variations from AI-generated tasks.md
- FR-002: Parser must detect and apply phase shift (+1 if Phase 0 exists)
- FR-003: Parser must validate sequential phases (error on gaps)
- FR-004: Parser must support cross-phase dependencies
- FR-005: Parser must be extensible (add parsers without touching existing)

**Non-Functional Requirements:**
- NFR-001: Each module file ≤ 500 lines (maintainability)
- NFR-002: Backward compatible imports with deprecation warnings
- NFR-003: Zero regressions on existing specs (validation required)
- NFR-004: Modular testing (unit test each component independently)

### Design Domain (specs.md Input)

**Architecture Patterns:**
- Submodule organization by parser type (markdown/, yaml/, shared/)
- Abstract base class pattern (SourceParser ABC)
- Composition over inheritance (utilities as standalone modules)
- Semantic scoring over pattern matching

**Component Structure:**
```
parsers/
├── base.py (ABC, errors)
├── markdown/ (SpecTasksParser + utilities)
├── yaml/ (WorkflowDefinitionParser)
└── shared/ (cross-parser utilities)
```

**Key Design Decisions:**
1. Semantic scoring with confidence thresholds (not rigid regex)
2. Pure functions for shared utilities (not classes)
3. Embedded mode for supporting docs (not references)
4. 8-phase incremental migration (not big-bang refactor)

### Implementation Domain (implementation.md Input)

**Implementation Phases (from Doc 1):**
1. Create directory structure
2. Extract base classes
3. Extract YAML parser (simple case)
4. Extract markdown utilities
5. Refactor SpecTasksParser
6. Implement new scoring logic (from Doc 2)
7. Update consumers
8. Deprecate old file

**Critical Implementation Details:**
- Task IDs: Just task number within phase ("1", "2", "3")
- Dependencies: Phase.task format ("1.1", "1.2") for cross-phase tracking
- Phase shift: +1 if min(phase_numbers) == 0
- Validation: Error on gaps, invalid starts, circular dependencies

**Risk Mitigation:**
- Keep task_parser.py as compatibility shim during transition
- Run regression tests on all completed specs
- Incremental migration allows rollback at each phase

---

## Next Steps

This index will be used in Task 3 to systematically extract insights from each document. The extracted insights will be organized by:
- **Requirements Insights:** Functional/non-functional requirements for SRD
- **Design Insights:** Architecture decisions, component design for specs.md
- **Implementation Insights:** Phase breakdown, code patterns for implementation.md

**Task 3 Focus:**
- Extract specific requirements statements
- Document architectural decisions with rationale
- Break down implementation into concrete tasks
- Identify acceptance criteria per phase


---

## Extracted Insights

### Requirements Insights (Phase 1 - SRD)

#### From Parser Submodule Architecture:
- **FR-001:** Parser system must support adding new parsers without modifying existing code
- **FR-002:** Each module file must be ≤ 500 lines for maintainability
- **FR-003:** System must maintain backward compatibility during migration
- **FR-004:** Parser additions must follow plugin-like pattern
- **FR-005:** Migration must be incremental with rollback capability at each phase
- **NFR-001:** Zero regressions on existing spec parsing (validation required)
- **NFR-002:** Deprecation warnings for old imports (not hard breaks)
- **NFR-003:** Module boundaries must be clear and testable in isolation

#### From Defensive Task Parser:
- **FR-006:** Parser must handle format variations from probabilistic AI systems
- **FR-007:** Parser must auto-detect Phase 0 and apply +1 shift for workflow harness
- **FR-008:** Parser must validate sequential phases and error on gaps (GIGO prevention)
- **FR-009:** Parser must support cross-phase task dependencies
- **FR-010:** Task IDs must be normalized to integers within phase
- **FR-011:** Dependencies must preserve phase.task format for cross-phase tracking
- **NFR-004:** Semantic scoring thresholds: PHASE_THRESHOLD=30.0, TASK_THRESHOLD=30.0
- **NFR-005:** Error messages must be actionable with fix guidance

### Design Insights (Phase 2 - specs.md)

#### From Parser Submodule Architecture:
- **Architecture:** Three-tier submodule structure (markdown/, yaml/, shared/)
- **Pattern:** Abstract base class (SourceParser) with format-specific implementations
- **Component:** base.py (50 lines) - ParseError, SourceParser ABC
- **Component:** markdown/spec_tasks.py (400 lines) - Core SpecTasksParser orchestration
- **Component:** markdown/scoring.py (300 lines) - NEW semantic scoring logic
- **Component:** markdown/traversal.py (200 lines) - AST traversal utilities
- **Component:** markdown/extraction.py (150 lines) - Metadata extraction
- **Component:** yaml/workflow_definition.py (150 lines) - YAML parser
- **Component:** shared/text.py (100 lines) - Generic text utilities
- **Component:** shared/dependencies.py (100 lines) - Dependency resolution
- **Component:** shared/validation.py (100 lines) - Validation logic
- **Decision:** Pure functions for shared utilities (not classes) - simpler, easier to test
- **Decision:** Constructor params for configuration (not hardcoded) - flexibility
- **Migration:** 8-phase incremental approach with backward compatibility shim

#### From Defensive Task Parser:
- **Algorithm:** 7-phase defensive parsing: score → classify → shift → validate → build → normalize deps → normalize IDs
- **Scoring:** Multi-signal confidence scoring (keyword + structure + context + penalties)
- **Phase Signals:** "phase" keyword (+40), single number (+25), H2 level (+15), separator (+10)
- **Task Signals:** "task" keyword (+40), dotted number (+30), H3 level (+20), starts with number (+10)
- **Negation:** "detailed breakdown" (-90%), "tasks" plural (-30%)
- **Classification:** Compare scores, apply thresholds, classify as phase/task
- **Shift Detection:** If min(phase_numbers) == 0: shift += 1, else if min != 1: error
- **Validation:** After shift, phases must be [1,2,3...N] sequential, error on gaps
- **Association:** Tasks → phases by proximity (nearest preceding) + inference (task N.M → Phase N)
- **Normalization:** task_id = just number ("1","2","3"), dependencies = "phase.task" ("1.1","1.2")

### Implementation Insights (Phase 4 - implementation.md)

#### From Parser Submodule Architecture:
- **Phase 1:** Create directory structure (`parsers/{markdown,yaml,shared}/`)
- **Phase 2:** Extract base classes (SourceParser, ParseError) to base.py
- **Phase 3:** Extract YAML parser (simpler, isolated, good test case)
- **Phase 4:** Extract markdown utilities (traversal, extraction to separate files)
- **Phase 5:** Refactor SpecTasksParser to use extracted utilities
- **Phase 6:** Implement new scoring logic in markdown/scoring.py
- **Phase 7:** Update consumers (dynamic_registry.py, engine.py imports)
- **Phase 8:** Deprecate task_parser.py (compatibility shim with warnings)
- **Testing:** One test file per module (~10 new test files)
- **Validation:** Regression test all completed specs
- **Timeline:** 6-7 hours total (can be split across sessions)

#### From Defensive Task Parser:
- **Implementation:** Replace `_extract_phases_from_ast()` with new 7-phase algorithm
- **Method 1:** `_score_headers(doc, content)` - Extract and score all headers
- **Method 2:** `_classify_headers(scored)` - Separate phases from tasks
- **Method 3:** `_detect_phase_shift(phases)` - Determine shift amount (0 or 1)
- **Method 4:** `_validate_phase_sequence(phases, shift)` - Check for gaps
- **Method 5:** `_build_phase_structures(phases, tasks, content, shift)` - Associate and build
- **Method 6:** `_normalize_dependencies(phases, shift)` - Apply shift to deps
- **Method 7:** `_normalize_task_ids(phases)` - Sequential 1-indexed numbering
- **Testing:** Unit test scoring, shift detection, validation, normalization separately
- **Validation:** Test on problematic spec (2025-11-04-rag-index-submodule-refactor)
- **Data Structure:** ScoredHeader dataclass for confidence tracking

### Cross-References

**Validated by Multiple Sources:**
- Tech debt prevention as primary motivation (both docs emphasize)
- Clean architecture with clear boundaries (both docs require)
- Extensibility for future parsers (both docs design for)
- Testing strategy with module isolation (both docs specify)
- Incremental migration approach (both docs recommend)

**Conflicts:**
- **None identified** - Documents are complementary
- Architecture doc provides structure, defensive parser doc provides algorithm
- Both must be implemented together for complete solution

**High-Priority Items:**
1. **Critical:** Create submodule structure BEFORE implementing new scoring (avoid 1,500-line file)
2. **Critical:** Phase shift detection (required for spec_execution_v1 workflow)
3. **Critical:** Gap validation (prevent GIGO, ensure spec quality)
4. **Important:** Backward compatibility (don't break existing consumers)
5. **Important:** Regression testing (zero regressions requirement)

---

## Insight Summary

**Total:** 52 insights extracted  
**By Category:** 
- Requirements: 16 insights (8 functional, 8 non-functional)
- Design: 26 insights (11 components, 15 architectural decisions/patterns)
- Implementation: 10 insights (8 phases + 7 methods + testing/validation)

**Multi-source validated:** 5 themes (tech debt, clean architecture, extensibility, testing, incremental)  
**Conflicts to resolve:** 0 (documents are complementary)  
**High-priority items:** 5 (submodule first, phase shift, gap validation, compatibility, regression testing)

**Coverage Gaps Identified:**
1. Performance benchmarks (baseline/targets not specified)
2. Rollback procedures (what if migration fails?)
3. Exact test case specifications (only strategy, not cases)
4. Documentation update requirements (what docs need changes?)
5. Production deployment validation (how to verify in prod?)

**Phase 0 Complete:** ✅ 2025-11-05
