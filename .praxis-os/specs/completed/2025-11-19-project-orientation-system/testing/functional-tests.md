# Functional Tests Plan

**Project:** Project Orientation System  
**Date:** 2025-11-19  
**Purpose:** Detailed test cases for all functional requirements

**Test Case Format:**
- **Happy Path:** Feature works as expected under normal conditions
- **Error Path:** Handles errors gracefully without crashing
- **Edge Cases:** Boundary conditions and unusual inputs

---

## FR-001: Inline Metadata Discovery for Orientation

**Requirement:** The system shall parse inline metadata using the **Metadata**: key=value pattern to discover project-specific orientation configurations in markdown files.

**Acceptance Criteria:**
- System detects **Metadata**: orientation=true in project standards files
- System extracts orientation-specific metadata fields (priority, category, queries)
- System uses regex-based parsing consistent with standards index pattern
- System defaults to path-based metadata when inline metadata missing

### Test Cases

#### Happy Path: Valid Metadata Detection
- **Test:** `test_extract_inline_metadata_valid_all_fields()`
- **Setup:** Markdown file with `**Metadata**: orientation=true, priority=1, category=architecture, query=project architecture`
- **Action:** Call `OrientationMetadataParser.extract_inline_metadata(content, path)`
- **Expected:** Returns `{"orientation": True, "priority": 1, "category": "architecture", "query": "project architecture"}`
- **Verifies:** Criteria 1, 2, 3

#### Happy Path: Path-Based Defaults
- **Test:** `test_extract_inline_metadata_missing_returns_defaults()`
- **Setup:** Markdown file without **Metadata**: line
- **Action:** Call `extract_inline_metadata(content, Path("standards/ai-assistant/test.md"))`
- **Expected:** Returns `{"domain": "ai-assistant"}` (path-based default)
- **Verifies:** Criteria 4

#### Error Handling: Malformed Pairs
- **Test:** `test_extract_inline_metadata_malformed_pairs_partial_parse()`
- **Setup:** `**Metadata**: orientation=true, badentry, priority=1`
- **Action:** Parse metadata
- **Expected:** Returns `{"orientation": True, "priority": 1}` (skips "badentry", continues)
- **Verifies:** Error resistance, criteria 3

#### Edge Cases: Empty Metadata
- **Test:** `test_extract_inline_metadata_empty_value()`
- **Setup:** `**Metadata**: ` (empty after colon)
- **Action:** Parse metadata
- **Expected:** Returns path-based defaults, logs warning
- **Verifies:** Graceful degradation

#### Edge Cases: Multiple Equals Signs
- **Test:** `test_extract_inline_metadata_value_contains_equals()`
- **Setup:** `**Metadata**: query=how does X=Y work?, priority=1`
- **Action:** Parse metadata using `split('=', 1)`
- **Expected:** Returns `{"query": "how does X=Y work?", "priority": 1}`
- **Verifies:** Correct parsing of values containing =

---

## FR-002: mcp.yaml Project Orientation Extension

**Requirement:** The system shall support project-specific orientation configuration via top-level `project:` section in mcp.yaml with `orientation:` subsection containing query definitions.

**Acceptance Criteria:**
- mcp.yaml schema extended with optional `project.orientation` section
- Orientation section supports list of query objects with metadata (query string, priority, description)
- Configuration validated via Pydantic schemas (consistent with unified config system)
- Multiple configuration sources supported (inline markdown metadata OR mcp.yaml OR both)

### Test Cases

#### Happy Path: mcp.yaml Orientation Section
- **Test:** `test_mcp_yaml_orientation_section_valid()`
- **Setup:** mcp.yaml with `project.orientation.queries: [{query: "test", priority: 1}]`
- **Action:** Load UnifiedConfig from mcp.yaml
- **Expected:** `config.project.orientation.queries` contains OrientationQuery objects
- **Verifies:** Criteria 1, 2

#### Happy Path: Pydantic Validation
- **Test:** `test_orientation_query_pydantic_validation()`
- **Setup:** Create OrientationQuery(query="test query", priority=1, description="Test")
- **Action:** Validate model
- **Expected:** Model validates successfully
- **Verifies:** Criteria 3

#### Happy Path: Multiple Sources (Inline + mcp.yaml)
- **Test:** `test_multiple_configuration_sources_merge()`
- **Setup:** Inline metadata in standards file + mcp.yaml orientation section
- **Action:** Discover orientation queries from both sources
- **Expected:** Returns merged list with deduplication (mcp.yaml takes precedence)
- **Verifies:** Criteria 4

#### Error Handling: Invalid Priority
- **Test:** `test_orientation_query_invalid_priority_validation_error()`
- **Setup:** OrientationQuery(query="test", priority=5)  # Invalid: must be 1-3
- **Action:** Validate model
- **Expected:** Raises ValidationError with "Priority must be 1, 2, or 3"
- **Verifies:** Criteria 3 (actionable errors)

#### Edge Cases: Empty Queries List
- **Test:** `test_project_orientation_empty_queries_list()`
- **Setup:** `project.orientation.queries: []`
- **Action:** Load config
- **Expected:** Valid config, no queries executed (graceful)
- **Verifies:** Optional orientation

---

## FR-003: Automatic Project Orientation Execution

**Requirement:** The system shall automatically discover and execute project-specific orientation queries after successful completion of the 10 mandatory base orientation queries.

**Acceptance Criteria:**
- Orientation query in base orientation (query 10) triggers project orientation discovery
- Project orientation queries executed in priority order (critical → high → medium)
- Each project query executed via pos_search_project with results presented to AI
- Execution completes within 1 minute target for typical projects (5-10 queries)

### Test Cases

#### Happy Path: Query 10 Triggers Discovery
- **Test:** `test_query_10_triggers_project_orientation_discovery()`
- **Setup:** Base orientation complete (queries 1-9), execute query 10
- **Action:** Execute "project orientation discovery project-specific context" query
- **Expected:** Returns project orientation metadata and query list
- **Verifies:** Criteria 1

#### Happy Path: Priority Order Execution
- **Test:** `test_project_queries_executed_in_priority_order()`
- **Setup:** Project queries with priorities [3, 1, 2, 1, 3]
- **Action:** Execute project orientation
- **Expected:** Execution order: [1, 1, 2, 3, 3]
- **Verifies:** Criteria 2

#### Happy Path: pos_search_project Integration
- **Test:** `test_each_project_query_via_pos_search_project()`
- **Setup:** Project queries: ["architecture", "patterns", "dogfooding"]
- **Action:** Execute orientation
- **Expected:** Each query calls `pos_search_project(action="search_standards", query=...)`
- **Verifies:** Criteria 3

#### Happy Path: Timing Target
- **Test:** `test_orientation_completes_within_60_seconds()`
- **Setup:** 10 project queries
- **Action:** Execute with timing measurement
- **Expected:** Total execution time < 60,000ms
- **Verifies:** Criteria 4

#### Error Handling: Timeout Protection
- **Test:** `test_orientation_timeout_returns_partial_results()`
- **Setup:** Mock slow queries (total >60s)
- **Action:** Execute with 60s timeout
- **Expected:** Returns partial results for completed queries, timeout flag=true
- **Verifies:** NFR-P1, resilience

---

## FR-004: Error-Resistant Metadata Parsing

**Requirement:** The system shall gracefully degrade when project orientation metadata is missing, malformed, or contains syntax errors, ensuring indexing and orientation continue without failures.

**Acceptance Criteria:**
- Missing metadata → use path-based defaults or skip project orientation
- Malformed key=value pairs → skip bad pairs, parse valid pairs, continue
- Typo in **Metadata**: marker → return defaults, log warning, continue
- Bad type coercion → skip field, log warning, use remaining fields
- NO indexing failures or crashes due to metadata errors

### Test Cases

#### Happy Path: Graceful Degradation Matrix
- **Test:** `test_all_error_scenarios_graceful_degradation()`
- **Setup:** 10 markdown files with various error scenarios
- **Action:** Parse all files
- **Expected:** All files indexed successfully, 0 exceptions raised
- **Verifies:** Criteria 5

#### Error Path: Missing Metadata
- **Test:** `test_missing_metadata_uses_defaults()`
- **Setup:** Markdown with no **Metadata**: line
- **Action:** Parse
- **Expected:** Returns defaults, orientation skipped gracefully
- **Verifies:** Criteria 1

#### Error Path: Malformed Pairs
- **Test:** `test_malformed_pairs_skip_and_continue()`
- **Setup:** `**Metadata**: good=value, bad entry here, also_good=value`
- **Action:** Parse
- **Expected:** Returns `{"good": "value", "also_good": "value"}` (skips "bad entry here")
- **Verifies:** Criteria 2

#### Error Path: Typo in Marker
- **Test:** `test_typo_in_metadata_marker_logs_warning_returns_defaults()`
- **Setup:** `**Metdata**: orientation=true` (typo: "Metdata")
- **Action:** Parse
- **Expected:** No match, returns defaults, logs warning with typo location
- **Verifies:** Criteria 3

#### Error Path: Bad Type Coercion
- **Test:** `test_bad_type_coercion_skip_field_continue()`
- **Setup:** `**Metadata**: orientation=notabool, priority=1`
- **Action:** Parse with type coercion
- **Expected:** Skips "orientation" (bad bool), parses "priority=1", logs warning
- **Verifies:** Criteria 4

---

## FR-005: Query Execution Order and Dependencies

**Requirement:** The system shall support execution order specification for project orientation queries via priority metadata and optional dependency fields.

**Acceptance Criteria:**
- Queries executed in priority order (critical=1, high=2, medium=3)
- Within same priority, queries executed in definition order
- Optional `depends_on` field for explicit dependencies between queries
- Dependency validation prevents circular dependencies

### Test Cases

#### Happy Path: Priority Order
- **Test:** `test_queries_executed_in_priority_order()`
- **Setup:** Queries with priorities [3, 1, 2, 1, 3]
- **Action:** Sort and execute
- **Expected:** Execution order: [p1, p1, p2, p3, p3]
- **Verifies:** Criteria 1

#### Happy Path: Definition Order Within Priority
- **Test:** `test_same_priority_maintains_definition_order()`
- **Setup:** Queries [A(p2), B(p2), C(p2)]
- **Action:** Sort
- **Expected:** Order: [A, B, C] (definition order preserved)
- **Verifies:** Criteria 2

#### Happy Path: Dependency Resolution
- **Test:** `test_depends_on_field_resolves_dependencies()`
- **Setup:** Query A depends_on=[B], Query B depends_on=[C], Query C no deps
- **Action:** Resolve dependencies with topological sort
- **Expected:** Execution order: [C, B, A]
- **Verifies:** Criteria 3

#### Error Handling: Circular Dependency Detection
- **Test:** `test_circular_dependency_raises_value_error()`
- **Setup:** Query A depends_on=[B], Query B depends_on=[A]
- **Action:** Resolve dependencies
- **Expected:** Raises ValueError with "Circular dependency detected: A → B → A"
- **Verifies:** Criteria 4

#### Edge Cases: Self-Dependency
- **Test:** `test_query_cannot_depend_on_itself()`
- **Setup:** OrientationQuery(query="test", depends_on=["test"])
- **Action:** Validate model
- **Expected:** Raises ValidationError "Query cannot depend on itself"
- **Verifies:** Pydantic validation prevents self-dependency

---

## FR-006: Standards Metadata Pattern Compatibility

**Requirement:** The system shall use the same inline metadata pattern (**Metadata**: orientation=true, priority=1, domain=project) as designed for standards parsing to ensure consistency and reuse existing parsing infrastructure.

**Acceptance Criteria:**
- Orientation metadata uses **Metadata**: key=value format (comma-separated)
- Type coercion follows standards parsing (bool: true/false, int: digits, string: default)
- Error handling follows standards parsing (skip malformed, log warnings, continue)
- Code reuse: shared _extract_inline_metadata() method or equivalent

### Test Cases

#### Happy Path: Format Matches Standards
- **Test:** `test_orientation_metadata_format_identical_to_standards()`
- **Setup:** `**Metadata**: orientation=true, priority=1, domain=project`
- **Action:** Parse with orientation parser
- **Expected:** Same result as standards parser for same input
- **Verifies:** Criteria 1

#### Happy Path: Type Coercion Consistency
- **Test:** `test_type_coercion_matches_standards_parsing()`
- **Setup:** Test inputs: "true", "123", "text"
- **Action:** Parse with both parsers
- **Expected:** Both return `{bool: True, int: 123, str: "text"}`
- **Verifies:** Criteria 2

#### Happy Path: Error Handling Consistency
- **Test:** `test_error_handling_matches_standards_parsing()`
- **Setup:** Malformed input
- **Action:** Parse with both parsers
- **Expected:** Both skip malformed, log warning, continue
- **Verifies:** Criteria 3

#### Happy Path: Code Reuse Verification
- **Test:** `test_shared_extract_inline_metadata_method()`
- **Setup:** Check module imports
- **Action:** Verify OrientationMetadataParser uses shared method
- **Expected:** Same `_extract_inline_metadata()` function used
- **Verifies:** Criteria 4

---

## FR-007: Base Orientation Integration

**Requirement:** The system shall integrate project orientation discovery into the existing base orientation workflow, ensuring AI agents execute both base and project orientation systematically.

**Acceptance Criteria:**
- Base orientation query 10 explicitly mentions project orientation discovery
- AI agents query for "project orientation" or "project-specific queries"
- Discovery returns project orientation metadata and query list
- AI agents execute project queries after base orientation complete

### Test Cases

#### Happy Path: Query 10 Text Update
- **Test:** `test_query_10_mentions_project_orientation_discovery()`
- **Setup:** Read PRAXIS-OS-ORIENTATION.md Query 10
- **Action:** Parse query text
- **Expected:** Query contains "project orientation" and "project-specific"
- **Verifies:** Criteria 1

#### Happy Path: AI Query Discovery
- **Test:** `test_ai_queries_project_orientation_and_discovers()`
- **Setup:** Mock AI agent executing Query 10
- **Action:** pos_search_project(query="project orientation discovery")
- **Expected:** Returns standards with orientation=true metadata
- **Verifies:** Criteria 2

#### Happy Path: Discovery Returns Metadata and Queries
- **Test:** `test_discovery_returns_metadata_and_query_list()`
- **Setup:** Project with orientation metadata
- **Action:** Execute discovery
- **Expected:** Returns {"queries": [...], "metadata": {...}}
- **Verifies:** Criteria 3

#### Happy Path: Execution Sequence
- **Test:** `test_project_queries_executed_after_base_complete()`
- **Setup:** Full orientation workflow
- **Action:** Execute base (1-10) then project queries
- **Expected:** Base completes → project discovery → project execution
- **Verifies:** Criteria 4

#### Integration Test: End-to-End Workflow
- **Test:** `test_full_orientation_workflow_base_plus_project()`
- **Setup:** Real project with orientation metadata
- **Action:** Execute complete orientation
- **Expected:** 10 base queries + N project queries = all results returned
- **Verifies:** All criteria, integration

---

## FR-008: Orientation Metadata Schema

**Requirement:** The system shall define a clear schema for project orientation metadata including required and optional fields.

**Acceptance Criteria:**
- Required fields: orientation=true (marker), query (string)
- Optional fields: priority (1-3), category (string), description (string), depends_on (list)
- Schema documented in standards for project maintainers
- Validation provides actionable error messages

### Test Cases

#### Happy Path: Required Fields Validation
- **Test:** `test_required_fields_orientation_true_and_query()`
- **Setup:** OrientationQuery(query="test query")
- **Action:** Validate model
- **Expected:** Valid (orientation=true inferred from context, query provided)
- **Verifies:** Criteria 1

#### Happy Path: Optional Fields Defaults
- **Test:** `test_optional_fields_have_defaults()`
- **Setup:** OrientationQuery(query="test")  # No priority, category, etc.
- **Action:** Validate model
- **Expected:** priority=2 (default), category=None, description=None, depends_on=None
- **Verifies:** Criteria 2

#### Happy Path: Schema Documentation
- **Test:** `test_schema_documented_in_standards()`
- **Setup:** Read project-orientation-guide.md
- **Action:** Check for schema documentation
- **Expected:** File exists, contains field descriptions and examples
- **Verifies:** Criteria 3

#### Error Handling: Missing Required Field
- **Test:** `test_missing_query_field_validation_error()`
- **Setup:** OrientationQuery()  # No query
- **Action:** Validate model
- **Expected:** Raises ValidationError "field required: query"
- **Verifies:** Criteria 4 (actionable error)

#### Error Handling: Invalid Optional Field Type
- **Test:** `test_invalid_priority_type_actionable_error()`
- **Setup:** OrientationQuery(query="test", priority="high")  # Should be int
- **Action:** Validate model
- **Expected:** Raises ValidationError "priority: value is not a valid integer"
- **Verifies:** Criteria 4 (actionable error)

---

## FR-009: No Consumer Tooling Requirements

**Requirement:** The system shall implement project orientation without requiring additional tooling, pre-commit hooks, or validation infrastructure in consumer projects.

**Acceptance Criteria:**
- Orientation works with markdown files only (no build step)
- mcp.yaml extension optional, not required
- No pre-commit hooks needed for validation
- Malformed metadata degrades gracefully (no user intervention)

### Test Cases

#### Happy Path: Markdown Files Only
- **Test:** `test_orientation_works_with_markdown_only()`
- **Setup:** Project with only markdown files (no mcp.yaml)
- **Action:** Discover and execute orientation
- **Expected:** Orientation works using inline metadata only
- **Verifies:** Criteria 1

#### Happy Path: mcp.yaml Optional
- **Test:** `test_mcp_yaml_extension_optional_not_required()`
- **Setup:** Project without project.orientation section in mcp.yaml
- **Action:** Load config and execute orientation
- **Expected:** Config loads successfully, orientation uses inline metadata only
- **Verifies:** Criteria 2

#### Happy Path: No Pre-Commit Hooks
- **Test:** `test_no_precommit_hooks_required_for_validation()`
- **Setup:** Consumer project without .pre-commit-config.yaml
- **Action:** Add orientation metadata, commit
- **Expected:** Orientation works without pre-commit validation
- **Verifies:** Criteria 3

#### Happy Path: Graceful Degradation
- **Test:** `test_malformed_metadata_graceful_no_user_intervention()`
- **Setup:** Markdown with malformed metadata (bad syntax)
- **Action:** Index and execute orientation
- **Expected:** Indexing succeeds, malformed file skipped, logs warning, continues
- **Verifies:** Criteria 4

#### Integration Test: Consumer Project Simulation
- **Test:** `test_consumer_project_orientation_no_external_tooling()`
- **Setup:** Fresh consumer project (no praxis-os dev tooling)
- **Action:** Add orientation metadata, execute
- **Expected:** Orientation works without any additional setup
- **Verifies:** All criteria, real-world scenario

---

## Integration Test Scenarios

### Scenario 1: Full Orientation Workflow
**Requirements:** FR-003, FR-007  
**Test:** `test_full_orientation_workflow_base_plus_project()`  
**Flow:**
1. AI agent starts conversation in project
2. Executes base orientation queries 1-9
3. Executes Query 10 (triggers project orientation discovery)
4. Discovery finds 5 project-specific queries (inline + mcp.yaml)
5. Executes 5 project queries in priority order
6. Returns combined results (10 base + 5 project = 15 total)
**Expected:** All queries execute successfully, AI has full context

### Scenario 2: Multiple Configuration Sources
**Requirements:** FR-001, FR-002  
**Test:** `test_multiple_sources_merge_and_deduplicate()`  
**Flow:**
1. Project has 3 queries in inline metadata
2. Project has 2 queries in mcp.yaml (1 duplicate)
3. Discovery merges sources
4. Deduplicates (mcp.yaml takes precedence)
5. Returns 4 unique queries
**Expected:** Correct merging and deduplication

### Scenario 3: Error Resilience End-to-End
**Requirements:** FR-004, FR-009  
**Test:** `test_error_resilience_end_to_end_workflow()`  
**Flow:**
1. Project has 5 orientation files: 2 valid, 2 malformed, 1 missing metadata
2. Index all files
3. Execute orientation
4. Returns results from 2 valid files
5. Logs warnings for malformed/missing
6. No indexing failures, no execution failures
**Expected:** Partial success, graceful degradation

---

## Test Summary

**Total Functional Test Cases:** 40+

### By Requirement:
- FR-001: 5 test cases (happy path, defaults, malformed, empty, edge cases)
- FR-002: 5 test cases (mcp.yaml, validation, multiple sources, errors, edge cases)
- FR-003: 5 test cases (discovery trigger, priority order, integration, timing, timeout)
- FR-004: 6 test cases (graceful degradation, missing, malformed, typo, bad coercion, matrix)
- FR-005: 5 test cases (priority, definition order, dependencies, circular detection, edge cases)
- FR-006: 4 test cases (format match, type coercion, error handling, code reuse)
- FR-007: 5 test cases (query 10 text, AI discovery, metadata return, sequence, integration)
- FR-008: 5 test cases (required fields, optional defaults, documentation, missing field, invalid type)
- FR-009: 5 test cases (markdown only, mcp.yaml optional, no hooks, graceful, consumer simulation)

### Integration Scenarios: 3

**Coverage:** All 9 functional requirements have comprehensive test cases covering happy path, error handling, and edge cases.

---


