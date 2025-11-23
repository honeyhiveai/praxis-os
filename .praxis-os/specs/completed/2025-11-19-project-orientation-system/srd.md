# Software Requirements Document

**Project:** Project Orientation System  
**Date:** 2025-11-19  
**Priority:** High  
**Category:** Feature

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for a Project Orientation System that enables projects using prAxIs OS to define project-specific orientation queries for AI agents, leveraging the existing inline metadata pattern for error-resistant, consumer-friendly configuration.

### 1.2 Scope
This feature will extend the existing base orientation system (which aligns AI agents to prAxIs OS patterns) with project-level orientation capabilities. Projects will be able to define custom orientation queries using inline metadata in markdown files or configuration extensions in `mcp.yaml`, enabling rapid project context loading for AI instances without requiring additional tooling in consumer projects.

---

## 2. Business Goals

### Goal 1: Accelerate AI Agent Project Onboarding

**Objective:** Reduce the time required for AI agents to understand project-specific context from unknown (currently requires manual explanation) to under 1 minute of automated orientation query execution.

**Success Metrics:**
- **Orientation Time**: Unknown/manual → < 1 minute automated
- **Context Coverage**: 0% project-specific → 80%+ key project concepts loaded
- **Query Success Rate**: N/A → 100% of orientation queries parseable and executable

**Business Impact:**
- Developers spend less time explaining project context to AI agents
- AI agents provide more accurate, context-aware suggestions immediately
- Reduced friction when onboarding new AI instances or switching conversations
- Improved developer productivity through faster AI ramp-up

### Goal 2: Enable Project-Specific Knowledge Discovery

**Objective:** Allow projects to define their own orientation patterns and critical context queries, making project knowledge discoverable through the same proven query mechanisms used for base prAxIs OS orientation.

**Success Metrics:**
- **Project Adoption**: 0 projects with custom orientation → 50%+ of prAxIs OS projects define orientation
- **Discovery Success**: N/A → 95%+ of project orientation metadata successfully discovered by AI agents
- **Extensibility**: N/A → Support multiple metadata patterns (inline, mcp.yaml extensions)

**Business Impact:**
- Projects can encode institutional knowledge in discoverable format
- Consistent orientation experience across base system and project-specific context
- Reduced knowledge silos (project context explicitly documented and queryable)
- Framework extensibility demonstrated through real-world use case

### Goal 3: Maintain Consumer-Friendly Distribution

**Objective:** Implement project orientation without requiring additional tooling, pre-commit hooks, or validation infrastructure in consumer projects, maintaining prAxIs OS's zero-tooling-friction philosophy.

**Success Metrics:**
- **Tooling Requirements**: 0 (same as current state)
- **Error Resilience**: N/A → 100% graceful degradation on malformed metadata
- **Distribution Complexity**: No increase (same files-only distribution model)

**Business Impact:**
- Projects can adopt orientation features without infrastructure overhead
- Error-resistant design prevents indexing failures from blocking AI functionality
- Maintains prAxIs OS's competitive advantage in ease of adoption
- Demonstrates framework's commitment to consumer experience

## 2.1 Supporting Documentation

The business goals above are informed by:
- **Mistletoe-Based Standards Parsing Enhancement**: Provides inline metadata pattern rationale, error-resistance requirements, and consumer distribution constraints

See `supporting-docs/INDEX.md` for complete analysis.

---

## 3. User Stories

User stories describe the feature from the user's perspective.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: AI Agent Project Self-Orientation

**As an** AI agent instance (Claude, GPT, etc.)  
**I want to** discover and execute project-specific orientation queries automatically  
**So that** I can understand project-specific context, architecture, and patterns without requiring manual developer explanation

**Acceptance Criteria:**
- Given I am a new AI instance starting a conversation in a project with orientation metadata
- When I execute the mandatory base orientation (10 queries)
- Then I discover project-specific orientation metadata and execute project queries
- And I load both base prAxIs OS patterns AND project-specific context

**Priority:** Critical

---

### Story 2: Project Maintainer Defines Orientation Queries

**As a** project owner/maintainer  
**I want to** define project-specific orientation queries using inline metadata or mcp.yaml extensions  
**So that** AI agents working on my project automatically understand key architectural concepts, dogfooding model, and project-specific patterns

**Acceptance Criteria:**
- Given I want to define project orientation
- When I add inline metadata (**Metadata**: orientation=true) to a standards file OR extend mcp.yaml with project orientation queries
- Then the orientation metadata is discoverable by AI agents during base orientation
- And the metadata includes query strings that load project-critical context

**Priority:** Critical

---

### Story 3: Developer Benefits from Pre-Oriented AI

**As a** developer using AI assistance  
**I want** AI agents to already understand my project context when I start a conversation  
**So that** I can focus on solving problems instead of spending time explaining background, architecture, and project-specific conventions

**Acceptance Criteria:**
- Given I start a new AI conversation in my project
- When the AI completes orientation (base + project)
- Then the AI understands project-specific architecture (e.g., ouroboros layered subsystems)
- And the AI understands project-specific patterns (e.g., dogfooding model, query-first decision protocol)
- And I can immediately ask context-dependent questions without preamble

**Priority:** High

---

### Story 4: Framework Author Demonstrates Extensibility

**As a** prAxIs OS framework author  
**I want to** demonstrate that the inline metadata pattern works for real-world extensions beyond standards parsing  
**So that** I validate the architectural decision to use inline metadata and prove the framework's extensibility

**Acceptance Criteria:**
- Given the inline metadata pattern was designed but not yet implemented for standards
- When project orientation is implemented using inline metadata
- Then it serves as the first production use case for the pattern
- And it validates the error-resistant, consumer-friendly design

**Priority:** Medium

---

## 3.1 Story Priority Summary

**Critical (Must-Have):**
- Story 1: AI Agent Project Self-Orientation
- Story 2: Project Maintainer Defines Orientation Queries

**High Priority:**
- Story 3: Developer Benefits from Pre-Oriented AI

**Medium Priority:**
- Story 4: Framework Author Demonstrates Extensibility

---

## 3.2 Supporting Documentation

User needs from supporting documents:
- **Mistletoe-Based Standards Parsing Enhancement**: Documents need for error-resistant metadata pattern that works without consumer validation tooling, enabling AI agents to self-configure

See `supporting-docs/INDEX.md` for complete analysis.

---

## 4. Functional Requirements

Functional requirements specify capabilities the system must provide.

---

### FR-001: Inline Metadata Discovery for Orientation

**Description:** The system shall parse inline metadata using the **Metadata**: key=value pattern to discover project-specific orientation configurations in markdown files.

**Priority:** Critical

**Related User Stories:** Story 1 (AI Agent Self-Orientation), Story 2 (Project Maintainer Defines Orientation)

**Acceptance Criteria:**
- System detects **Metadata**: orientation=true in project standards files
- System extracts orientation-specific metadata fields (priority, category, queries)
- System uses regex-based parsing consistent with standards index pattern
- System defaults to path-based metadata when inline metadata missing

---

### FR-002: mcp.yaml Project Orientation Extension

**Description:** The system shall support project-specific orientation configuration via top-level `project:` section in mcp.yaml with `orientation:` subsection containing query definitions.

**Priority:** Critical

**Related User Stories:** Story 2 (Project Maintainer Defines Orientation)

**Acceptance Criteria:**
- mcp.yaml schema extended with optional `project.orientation` section
- Orientation section supports list of query objects with metadata (query string, priority, description)
- Configuration validated via Pydantic schemas (consistent with unified config system)
- Multiple configuration sources supported (inline markdown metadata OR mcp.yaml OR both)

---

### FR-003: Automatic Project Orientation Execution

**Description:** The system shall automatically discover and execute project-specific orientation queries after successful completion of the 10 mandatory base orientation queries.

**Priority:** Critical

**Related User Stories:** Story 1 (AI Agent Self-Orientation), Story 3 (Developer Benefits)

**Acceptance Criteria:**
- Orientation query in base orientation (query 10) triggers project orientation discovery
- Project orientation queries executed in priority order (critical → high → medium)
- Each project query executed via pos_search_project with results presented to AI
- Execution completes within 1 minute target for typical projects (5-10 queries)

---

### FR-004: Error-Resistant Metadata Parsing

**Description:** The system shall gracefully degrade when project orientation metadata is missing, malformed, or contains syntax errors, ensuring indexing and orientation continue without failures.

**Priority:** Critical

**Related User Stories:** Story 2 (Project Maintainer Defines Orientation)

**Acceptance Criteria:**
- Missing metadata → use path-based defaults or skip project orientation
- Malformed key=value pairs → skip bad pairs, parse valid pairs, continue
- Typo in **Metadata**: marker → return defaults, log warning, continue
- Bad type coercion → skip field, log warning, use remaining fields
- NO indexing failures or crashes due to metadata errors

---

### FR-005: Query Execution Order and Dependencies

**Description:** The system shall support execution order specification for project orientation queries via priority metadata and optional dependency fields.

**Priority:** High

**Related User Stories:** Story 2 (Project Maintainer Defines Orientation)

**Acceptance Criteria:**
- Queries executed in priority order (critical=1, high=2, medium=3)
- Within same priority, queries executed in definition order
- Optional `depends_on` field for explicit dependencies between queries
- Dependency validation prevents circular dependencies

---

### FR-006: Standards Metadata Pattern Compatibility

**Description:** The system shall use the same inline metadata pattern (**Metadata**: orientation=true, priority=1, domain=project) as designed for standards parsing to ensure consistency and reuse existing parsing infrastructure.

**Priority:** High

**Related User Stories:** Story 4 (Framework Author Demonstrates Extensibility)

**Acceptance Criteria:**
- Orientation metadata uses **Metadata**: key=value format (comma-separated)
- Type coercion follows standards parsing (bool: true/false, int: digits, string: default)
- Error handling follows standards parsing (skip malformed, log warnings, continue)
- Code reuse: shared _extract_inline_metadata() method or equivalent

---

### FR-007: Base Orientation Integration

**Description:** The system shall integrate project orientation discovery into the existing base orientation workflow, ensuring AI agents execute both base and project orientation systematically.

**Priority:** Critical

**Related User Stories:** Story 1 (AI Agent Self-Orientation), Story 3 (Developer Benefits)

**Acceptance Criteria:**
- Base orientation query 10 explicitly mentions project orientation discovery
- AI agents query for "project orientation" or "project-specific queries"
- Discovery returns project orientation metadata and query list
- AI agents execute project queries after base orientation complete

---

### FR-008: Orientation Metadata Schema

**Description:** The system shall define a clear schema for project orientation metadata including required and optional fields.

**Priority:** High

**Related User Stories:** Story 2 (Project Maintainer Defines Orientation)

**Acceptance Criteria:**
- Required fields: orientation=true (marker), query (string)
- Optional fields: priority (1-3), category (string), description (string), depends_on (list)
- Schema documented in standards for project maintainers
- Validation provides actionable error messages

---

### FR-009: No Consumer Tooling Requirements

**Description:** The system shall implement project orientation without requiring additional tooling, pre-commit hooks, or validation infrastructure in consumer projects.

**Priority:** Critical

**Related User Stories:** All stories (cross-cutting requirement)

**Acceptance Criteria:**
- Orientation works with markdown files only (no build step)
- mcp.yaml extension optional, not required
- No pre-commit hooks needed for validation
- Malformed metadata degrades gracefully (no user intervention)

---

## 4.1 Requirements by Category

### Metadata Discovery & Parsing
- FR-001, FR-004, FR-006, FR-008

### Configuration & Extensibility
- FR-002, FR-009

### Orientation Execution
- FR-003, FR-005, FR-007

---

## 4.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority |
|-------------|--------------|----------------|----------|
| FR-001 | Story 1, 2 | Goal 1, 2 | Critical |
| FR-002 | Story 2 | Goal 2 | Critical |
| FR-003 | Story 1, 3 | Goal 1 | Critical |
| FR-004 | Story 2 | Goal 3 | Critical |
| FR-005 | Story 2 | Goal 2 | High |
| FR-006 | Story 4 | Goal 2 | High |
| FR-007 | Story 1, 3 | Goal 1 | Critical |
| FR-008 | Story 2 | Goal 2 | High |
| FR-009 | All | Goal 3 | Critical |

---

## 4.3 Supporting Documentation

Requirements informed by:
- **Mistletoe-Based Standards Parsing Enhancement**: Inline metadata pattern (**Metadata**: key=value), error-resistant parsing, graceful degradation, regex-based extraction, no tooling requirements

See `supporting-docs/INDEX.md` for complete extracted insights.

---

## 5. Non-Functional Requirements

NFRs define quality attributes and system constraints.

---

### 5.1 Performance

**NFR-P1: Orientation Execution Time**
- Project orientation discovery and execution: < 1 minute for typical projects (5-10 queries)
- Inline metadata parsing overhead: < 100ms per markdown file
- mcp.yaml parsing overhead: < 50ms per configuration load
- Justification: Base orientation is 10 queries, project orientation should be comparable in duration

**NFR-P2: Indexing Performance**
- Metadata extraction shall not degrade standards index build time by more than 5%
- Parsing errors shall not cause retry loops or significant slowdowns

---

### 5.2 Reliability

**NFR-R1: Graceful Degradation**
- 100% graceful degradation on malformed metadata (skip, log warning, continue)
- Zero indexing failures due to metadata syntax errors
- Zero orientation execution failures due to bad metadata

**NFR-R2: Error Resilience**
- Missing metadata → use defaults or skip project orientation
- Malformed key=value pairs → parse valid pairs, skip bad pairs
- Typo in marker → log warning, return defaults
- Bad type coercion → skip field, use remaining fields

---

### 5.3 Usability

**NFR-U1: Zero Tooling Requirements**
- No additional tooling required in consumer projects (beyond base prAxIs OS)
- No pre-commit hooks required for metadata validation
- No build step required for orientation to function
- Orientation works with markdown files and mcp.yaml only

**NFR-U2: Error Messages**
- Actionable error/warning messages for malformed metadata
- Log warnings with file path, line number, and specific issue
- Error messages guide users to fix metadata without deep framework knowledge

**NFR-U3: Documentation Clarity**
- Orientation metadata schema documented with examples
- Project maintainers can implement orientation without framework expertise
- Examples cover common patterns (inline markdown, mcp.yaml extension)

---

### 5.4 Maintainability

**NFR-M1: Code Reuse**
- Reuse existing _extract_inline_metadata() parsing logic from standards index design
- Share error handling patterns between standards and orientation metadata
- Leverage existing Pydantic schema infrastructure for mcp.yaml extensions

**NFR-M2: Test Coverage**
- Minimum 90% code coverage for metadata parsing and orientation execution
- Comprehensive test scenarios: valid metadata, missing, malformed, typos, bad types
- Integration tests for base + project orientation workflow

**NFR-M3: Code Quality**
- Comprehensive Sphinx-style docstrings for all functions
- Full type hints (parameters and return types)
- Zero linting errors (flake8, mypy)

---

### 5.5 Compatibility

**NFR-C1: Configuration Schema Compatibility**
- mcp.yaml extensions follow Pydantic v2 schema patterns (consistent with unified config system)
- Backward compatible: projects without orientation metadata continue working unchanged
- Forward compatible: new metadata fields added without breaking existing configs

**NFR-C2: Standards Index Compatibility**
- Orientation metadata parsing compatible with existing standards index architecture
- No breaking changes to current standards markdown format
- Inline metadata pattern matches standards parsing design (from mistletoe design doc)

---

### 5.6 Security

**NFR-S1: No Code Execution**
- Regex-based parsing only (no eval(), exec(), or dynamic code execution)
- Metadata values treated as data, not code
- No command injection risk from malicious metadata

**NFR-S2: Input Validation**
- All metadata fields validated against expected types
- Query strings sanitized before execution
- Dependency graph validated to prevent infinite loops

---

## 5.7 Supporting Documentation

NFRs informed by:
- **Mistletoe-Based Standards Parsing Enhancement**: Performance targets (zero-cost parsing), error resilience patterns, no code execution risk, regex-based approach

See `supporting-docs/INDEX.md` for complete extracted insights.

---

## 6. Out of Scope

Explicitly defines what is NOT included. Items may be considered for future phases.

### Explicitly Excluded

---

#### Features

**Not Included in This Release:**

1. **YAML Frontmatter Support**
   - **Reason:** Explicitly rejected in design documentation (AI agents mess up YAML syntax, consumers can't enforce validation, silent failures)
   - **Future Consideration:** Not planned - inline metadata pattern chosen as strategic direction

2. **LLM-Enhanced Metadata Generation**
   - **Reason:** Costs money (~$0.01/doc), auto-generation from headers/keywords sufficient for orientation use case
   - **Future Consideration:** Optional in Phase 2 if projects demand higher-quality metadata

3. **Multi-Level Orientation Hierarchies**
   - **Reason:** Complexity not justified by current use cases (base → project is sufficient)
   - **Future Consideration:** Phase 2+ if organizations need team-level or individual-level orientation

4. **Orientation Query Template Library**
   - **Reason:** Projects should define their own queries (project-specific by definition)
   - **Future Consideration:** Community-contributed templates possible, but not framework responsibility

5. **Orientation Analytics and Metrics**
   - **Reason:** Monitoring which queries are most effective requires additional infrastructure
   - **Future Consideration:** Phase 2 feature (track query effectiveness, AI behavior changes)

6. **Orientation Versioning**
   - **Reason:** Tracking orientation changes over time not required for MVP
   - **Future Consideration:** Phase 2 (useful for understanding evolution of project knowledge)

7. **Dynamic Orientation Query Generation**
   - **Reason:** AI agents generating their own orientation queries introduces complexity and unpredictability
   - **Future Consideration:** Research topic, not production feature

---

#### Platforms

**Not Supported:**

- **Standalone Orientation Tool**: Project orientation is integrated into prAxIs OS only, not available as separate tool or library (Reason: Tightly coupled with RAG infrastructure, mcp.yaml config, and standards index)

---

#### Integrations

**Not Included:**

- **External Orientation Services**: No integration with external knowledge bases or orientation APIs (Reason: Self-contained design maintains zero-tooling philosophy)
- **Orientation Sharing Services**: No cross-project orientation sharing or marketplace (Reason: Projects define their own context, not sharable templates)

---

#### User Types

**Not Supported:**

- **Non-AI Users**: This feature is specifically for AI agent orientation (human developers benefit indirectly but don't interact with orientation system directly)
- **AI Agents Outside prAxIs OS Ecosystem**: Orientation system assumes prAxIs OS environment, not portable to other frameworks

---

## 6.1 Future Enhancements

**Potential Phase 2:**
- Orientation analytics (query effectiveness metrics, AI behavior tracking)
- Orientation versioning (track changes over time, A/B test query formulations)
- LLM-enhanced metadata generation (optional, costs money)
- Multi-level orientation hierarchies (organization → project → team)

**Potential Phase 3:**
- Community orientation patterns library (best practices from real projects)
- Cross-project orientation insights (aggregate learning from multiple projects)
- Orientation recommendation engine (suggest queries based on project type)

**Explicitly Not Planned:**
- YAML frontmatter support (strategic rejection)
- AI-generated orientation queries (unpredictable, not production-ready)
- Standalone orientation tool (requires prAxIs OS ecosystem)

---

## 6.2 Supporting Documentation

Out-of-scope items from:
- **Mistletoe-Based Standards Parsing Enhancement**: LLM-enhanced metadata generation explicitly noted as "optional, costs money" - auto-generation sufficient

See `supporting-docs/INDEX.md` for complete analysis.

---


