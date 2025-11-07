# Software Requirements Document

**Project:** Unified Configuration System with Pydantic v2  
**Date:** 2025-11-03  
**Priority:** High  
**Category:** Enhancement (Architecture)

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for replacing the dual configuration system (Python dataclasses + YAML dict) with a unified, validated configuration system using Pydantic v2.

### 1.2 Scope
This feature will consolidate all MCP server configuration into a single `config/mcp.yaml` file backed by Pydantic v2 validation schemas, providing type safety, fail-fast validation, and clear error messages while maintaining all existing functionality.

---

## 2. Business Goals

### Goal 1: Eliminate Configuration-Related Runtime Errors

**Objective:** Reduce configuration errors causing server failures or incorrect behavior from runtime (during search operations) to startup (fail-fast with clear messages).

**Success Metrics:**
- Config validation errors: Currently discovered during search → Discovered at server startup (100% shift)
- KeyError exceptions from config access: Current (unknown frequency) → Zero
- Time to identify config error: Currently 5-30 minutes (discover during operation) → <10 seconds (startup failure with clear message)
- User frustration incidents: Reduce by 90% (catch before users encounter issues)

**Business Impact:**
- **Developers benefit:** Immediate feedback on config typos, no debugging failed searches
- **System reliability:** Server won't start with invalid config (no partial failures)
- **Time savings:** ~25 minutes saved per config error (no search debugging needed)
- **User confidence:** "It just works" - if server starts, config is valid

---

### Goal 2: Enable Config-Driven Feature Development

**Objective:** Allow new features (indexes, languages, models) to be added via YAML configuration changes only, without code modifications.

**Success Metrics:**
- Code changes required for new index type: Currently 5-10 files → 0 files (YAML only)
- Code changes required for new language support: Currently 3-5 files → 0 files (YAML only)
- Time to add new index: Currently 2-4 hours (code + testing) → 15 minutes (YAML config)
- Configuration flexibility: Currently limited to hardcoded options → Unlimited via schema

**Business Impact:**
- **Development velocity:** 8-15x faster feature additions (config vs code)
- **Deployment flexibility:** Users can customize without code forks
- **Maintenance burden:** Reduced (config changes don't require code review)
- **Innovation:** Lower barrier for experimental features

---

### Goal 3: Improve Developer Experience with Type Safety

**Objective:** Provide IDE autocomplete and compile-time checking for all configuration access, eliminating guesswork about configuration structure.

**Success Metrics:**
- Dict access (`config["key"]`): Currently 100% → 0% (replaced with `config.key`)
- IDE autocomplete availability: Currently 0% → 100% of config access
- Runtime KeyError exceptions: Currently unknown baseline → Zero
- Documentation accuracy: Currently manual sync → Auto-generated from schemas (always current)

**Business Impact:**
- **Developer productivity:** ~30% faster config-related development (no docs lookups, no trial-and-error)
- **Code quality:** Fewer bugs from typos or incorrect structure assumptions
- **Onboarding:** New contributors understand config immediately via IDE hints
- **Maintainability:** Schema is self-documenting

---

### Goal 4: Establish Foundation for Future Scalability

**Objective:** Create a configuration architecture that supports future growth (multi-index, distributed deployment, language migration) without redesign.

**Success Metrics:**
- Migration readiness: Currently Python-specific → Language-agnostic schema (JSON Schema export)
- Validation portability: Currently Python code → Exportable schema (Rust serde compatible)
- Configuration versioning: Currently none → Explicit version field with migration support
- Extension points: Currently ad-hoc → Defined schema extension patterns

**Business Impact:**
- **Future-proofing:** Rust migration possible (Pydantic schema → serde schema)
- **Risk reduction:** Configuration changes validated before deployment
- **Architecture flexibility:** Support microservices, distributed indexing
- **Investment protection:** Config system won't need redesign at scale

---

## 2.1 Supporting Documentation

The business goals above are informed by:
- **unified-config-system-pydantic-v2.md**: Detailed analysis of current dual config pain points, benefits comparison showing 8-15x efficiency gains, migration path
- **language-choice-analysis.md**: Strategic context that Python is current best choice, but Pydantic provides bridge to future Rust migration via schema portability

See `supporting-docs/INDEX.md` and `supporting-docs/INSIGHTS.md` for complete analysis.

---

## 2.2 Business Goal Validation

✅ All goals validated against criteria:
- **Specific:** Each goal targets clear outcome (eliminate runtime errors, enable config-driven features, provide type safety, establish scalability foundation)
- **Measurable:** Quantifiable metrics (KeyErrors → zero, code changes → 0 files, dev time 2-4hrs → 15min, IDE autocomplete 0% → 100%)
- **Business-Focused:** Clear value statements (reliability, velocity, productivity, future-proofing)
- **Actionable:** Directly addressable through Pydantic v2 implementation

---

## 3. User Stories

User stories describe the feature from the user's perspective.

### Story Format

**As a** {user type}  
**I want to** {capability}  
**So that** {benefit}

---

### Story 1: Clear Error Messages on Config Mistakes

**As a** MCP server developer  
**I want to** receive clear, actionable error messages when my config has typos or invalid values  
**So that** I can fix configuration problems immediately without debugging through runtime failures

**Acceptance Criteria:**
- Given I have an invalid `chunk_size: 50` (below minimum 100)
- When I start the MCP server
- Then I see error: "indexes → standards → vector → chunk_size: Input should be greater than or equal to 100"
- And the server does not start
- And I know exactly which field and value to fix

**Priority:** Critical (Must-Have)

---

### Story 2: Type-Safe Configuration Access

**As a** MCP server developer  
**I want to** access configuration values with IDE autocomplete and type checking  
**So that** I don't have to guess field names or look up documentation constantly

**Acceptance Criteria:**
- Given I'm writing code that needs the embedding model name
- When I type `config.indexes.standards.vector.`
- Then my IDE shows autocomplete options: `model`, `chunk_size`, `chunk_overlap`, etc.
- And I get compile-time errors if I mistype a field name
- And I don't need to look up the YAML structure

**Priority:** Critical (Must-Have)

---

### Story 3: Add New Index Type Without Code Changes

**As a** system administrator  
**I want to** add a new index type (e.g., specs index) by editing only YAML config  
**So that** I can customize indexing behavior without modifying Python code

**Acceptance Criteria:**
- Given I want to index a new content type
- When I add a new section to `mcp.yaml` under `indexes:`
- Then the system automatically creates and manages that index
- And I don't need to edit any Python files
- And the new index inherits all standard behaviors (FTS, vector, caching)

**Priority:** High

---

### Story 4: Understand Configuration Requirements

**As a** new contributor to prAxIs OS  
**I want to** see all available configuration options with descriptions and constraints  
**So that** I can understand what's configurable without reading source code

**Acceptance Criteria:**
- Given I'm new to the project
- When I look at the Pydantic schema files
- Then I see Field descriptions for every config option
- And I see validation rules (ge=100, le=2000, pattern, etc.)
- And I understand what each field does and what values are valid
- And I can generate JSON Schema docs automatically

**Priority:** High

---

### Story 5: Validate Config Before Deployment

**As a** system administrator  
**I want to** validate my configuration file before deploying to production  
**So that** I know it will work before restarting the live server

**Acceptance Criteria:**
- Given I have a modified `mcp.yaml` file
- When I run a validation command
- Then I see all validation errors (if any)
- And I can fix them before deployment
- And I'm confident the server will start successfully

**Priority:** High

---

### Story 6: Migrate Existing Config Safely

**As an** existing prAxIs OS user  
**I want to** migrate from the old dual-config system to the new unified system  
**So that** I can benefit from improved validation without losing my settings

**Acceptance Criteria:**
- Given I have existing `index_config.yaml` and `models/config.py`
- When the migration happens
- Then all my existing settings are preserved
- And I receive clear guidance on what changed
- And the system validates my migrated config
- And I know immediately if anything needs manual adjustment

**Priority:** High

---

## 3.1 Story Priority Summary

**Critical (Must-Have):**
- Story 1: Clear Error Messages on Config Mistakes
- Story 2: Type-Safe Configuration Access

**High Priority:**
- Story 3: Add New Index Type Without Code Changes
- Story 4: Understand Configuration Requirements
- Story 5: Validate Config Before Deployment
- Story 6: Migrate Existing Config Safely

**Rationale:** Critical stories address core pain points (runtime errors, type safety) that affect daily development. High priority stories enable scalability and usability but aren't blockers.

---

## 3.2 Supporting Documentation

User needs from supporting documents:
- **unified-config-system-pydantic-v2.md**: "Clear error messages at startup (not during search when it's too late)", "Type-safe configuration access (IDE autocomplete, no runtime KeyErrors)"
- **language-choice-analysis.md**: "Type safety via Pydantic addresses main pain point", "Config-driven architecture for future scalability"

See `supporting-docs/INSIGHTS.md` section "Requirements Insights" for complete user need analysis.

---

## 4. Functional Requirements

Functional requirements specify capabilities the system must provide.

---

### FR-001: Load Configuration from Single YAML File

**Description:** The system shall load all configuration from a single `config/mcp.yaml` file using Pydantic v2 validation.

**Priority:** Critical

**Related User Stories:** Story 1, Story 2

**Acceptance Criteria:**
- System loads config from exactly one YAML file (`config/mcp.yaml`)
- All settings previously in `index_config.yaml` and `models/config.py` are consolidated
- Config file uses hierarchical structure (server, indexes, retrieval)
- YAML file is valid and parseable

---

### FR-002: Fail-Fast Validation at Server Startup

**Description:** The system shall validate all configuration values at server startup and refuse to start if any validation errors exist.

**Priority:** Critical

**Related User Stories:** Story 1

**Acceptance Criteria:**
- All validation occurs before server begins accepting requests
- Server exits with non-zero status code if validation fails
- Server logs validation errors clearly before exiting
- No partial startup state (all-or-nothing)
- Validation completes in <100ms

---

### FR-003: Display Clear Error Messages with Field Paths

**Description:** The system shall display validation errors with full field paths and helpful descriptions when configuration is invalid.

**Priority:** Critical

**Related User Stories:** Story 1

**Acceptance Criteria:**
- Error messages show field path: "indexes → standards → vector → chunk_size"
- Error messages explain constraint: "Input should be greater than or equal to 100"
- Error messages show actual invalid value
- Multiple errors are shown together (not just first error)
- Error messages suggest fix where possible

---

### FR-004: Type-Safe Configuration Property Access

**Description:** The system shall provide type-safe property access to all configuration values using Pydantic models.

**Priority:** Critical

**Related User Stories:** Story 2

**Acceptance Criteria:**
- All config access uses dot notation: `config.indexes.standards.vector.model`
- No dict-style access (`config["indexes"]`) in codebase
- IDE provides autocomplete for all config fields
- Type checker (mypy) detects invalid field access at compile time
- Runtime AttributeError impossible for valid config fields

---

### FR-005: Validate Field Constraints

**Description:** The system shall enforce all field constraints defined in Pydantic schemas (ranges, patterns, types).

**Priority:** Critical

**Related User Stories:** Story 1, Story 5

**Acceptance Criteria:**
- Numeric fields: validate min/max ranges (e.g., chunk_size 100-2000)
- String fields: validate patterns where applicable (e.g., version format)
- Boolean fields: accept only true/false
- Enum fields: accept only defined values (e.g., device: cpu|cuda|mps)
- Cross-field validation: chunk_overlap < chunk_size
- All constraints documented in Field() definitions

---

### FR-006: Dynamic Index Initialization from Config

**Description:** The system shall dynamically initialize all enabled indexes based on configuration without code changes.

**Priority:** High

**Related User Stories:** Story 3

**Acceptance Criteria:**
- System reads `indexes` section from config
- For each enabled index (enabled: true), system initializes corresponding index class
- Index receives its config subsection as Pydantic model
- Adding new index type requires only config change (no Python edits)
- Disabling index (enabled: false) skips initialization
- Unknown index types are rejected with clear error

---

### FR-007: Support All Existing Index Types

**Description:** The system shall support all currently implemented index types (standards, code, AST) through unified config schema.

**Priority:** Critical

**Related User Stories:** Story 6

**Acceptance Criteria:**
- Standards index: vector, FTS, metadata, cache settings
- Code index: vector, FTS, exclude patterns, cache settings
- AST index: languages, node_types, auto_install_parsers, cache settings
- All existing functionality preserved
- No feature regression from old config system

---

### FR-008: Provide Field Documentation in Schemas

**Description:** The system shall include descriptions and constraints for all configuration fields in Pydantic schema definitions.

**Priority:** High

**Related User Stories:** Story 4

**Acceptance Criteria:**
- Every Field() has description parameter
- Descriptions explain purpose and valid values
- Constraints visible in Field() (ge, le, pattern)
- Examples provided where helpful
- Documentation generateable from schemas (JSON Schema export)

---

### FR-009: Support Configuration Versioning

**Description:** The system shall include explicit version field in config schema to support future migrations.

**Priority:** High

**Related User Stories:** Story 6

**Acceptance Criteria:**
- Config file has top-level `version` field
- Version format validated (e.g., "1.0")
- System checks version compatibility at startup
- Unsupported versions rejected with clear upgrade message
- Version field reserved for future migration logic

---

### FR-010: Provide Standalone Validation Tool

**Description:** The system shall provide a command-line tool to validate configuration without starting the server.

**Priority:** High

**Related User Stories:** Story 5

**Acceptance Criteria:**
- Tool loads and validates mcp.yaml
- Exits with status 0 if valid, non-zero if invalid
- Displays all validation errors (same format as startup)
- Runnable in CI/CD pipelines
- Completes in <1 second

---

### FR-011: Preserve Backwards Compatibility During Migration

**Description:** The system shall support running with old config format during migration phase (optional fallback).

**Priority:** High

**Related User Stories:** Story 6

**Acceptance Criteria:**
- System detects old config format (index_config.yaml exists)
- System logs warning about deprecated config
- Old config continues working (no forced migration)
- Clear migration instructions logged
- Deprecation timeline communicated

---

### FR-012: Export JSON Schema for Documentation

**Description:** The system shall support exporting Pydantic schemas as JSON Schema for documentation generation.

**Priority:** Medium

**Related User Stories:** Story 4

**Acceptance Criteria:**
- `MCPConfig.model_json_schema()` produces valid JSON Schema
- Schema includes all fields, types, descriptions, constraints
- Schema can drive documentation generators (e.g., MkDocs)
- Schema can drive config editors (e.g., VS Code YAML validation)
- Schema version tracked

---

## 4.1 Requirements by Category

### Configuration Loading & Validation
- FR-001: Load Configuration from Single YAML File
- FR-002: Fail-Fast Validation at Server Startup
- FR-003: Display Clear Error Messages with Field Paths
- FR-005: Validate Field Constraints
- FR-009: Support Configuration Versioning
- FR-010: Provide Standalone Validation Tool

### Type Safety & Developer Experience
- FR-004: Type-Safe Configuration Property Access
- FR-008: Provide Field Documentation in Schemas
- FR-012: Export JSON Schema for Documentation

### Extensibility & Scalability
- FR-006: Dynamic Index Initialization from Config
- FR-007: Support All Existing Index Types

### Migration & Compatibility
- FR-011: Preserve Backwards Compatibility During Migration

---

## 4.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority |
|-------------|--------------|----------------|----------|
| FR-001 | Story 1, 2 | Goal 1, 2 | Critical |
| FR-002 | Story 1 | Goal 1 | Critical |
| FR-003 | Story 1 | Goal 1 | Critical |
| FR-004 | Story 2 | Goal 3 | Critical |
| FR-005 | Story 1, 5 | Goal 1 | Critical |
| FR-006 | Story 3 | Goal 2 | High |
| FR-007 | Story 6 | Goal 2 | Critical |
| FR-008 | Story 4 | Goal 3 | High |
| FR-009 | Story 6 | Goal 4 | High |
| FR-010 | Story 5 | Goal 1 | High |
| FR-011 | Story 6 | Goal 1 | High |
| FR-012 | Story 4 | Goal 3 | Medium |

---

## 4.3 Supporting Documentation

Requirements informed by:
- **unified-config-system-pydantic-v2.md**: Detailed config structure, Pydantic schema examples, validation approach, migration phases
- **INSIGHTS.md (Requirements section)**: Specific needs extracted include: "Single source of truth", "Fail-fast validation", "Type-safe access", "Config-driven behavior"

See `supporting-docs/INSIGHTS.md` for complete requirements analysis.

---

## 5. Non-Functional Requirements

NFRs define quality attributes and system constraints.

---

### 5.1 Performance

**NFR-P1: Configuration Load Time**
- Config file loading: < 50ms (99th percentile)
- Pydantic validation: < 100ms (99th percentile)
- Total startup overhead: < 150ms added to server startup
- No noticeable delay for users

**NFR-P2: Memory Overhead**
- Pydantic models memory footprint: < 5MB
- No memory leaks from config objects
- Config objects created once at startup (not per-request)

**NFR-P3: Validation Performance**
- Field validation: < 1ms per field
- Cross-field validation: < 5ms total
- Validation scales linearly with config size

---

### 5.2 Maintainability

**NFR-M1: Code Quality**
- Type hints: 100% coverage for all config-related code
- Mypy strict mode: zero errors
- Pylint score: ≥ 9.0/10
- No `type: ignore` comments without justification

**NFR-M2: Test Coverage**
- Unit test coverage: ≥ 90% for Pydantic models
- Integration test coverage: ≥ 80% for config loading
- Validation error test coverage: 100% of constraint types
- All edge cases tested (empty config, invalid types, cross-field violations)

**NFR-M3: Documentation Quality**
- Every Pydantic Field has description
- Every model has docstring with example
- JSON Schema auto-generates from models
- Documentation stays in sync with code (single source of truth)

---

### 5.3 Usability

**NFR-U1: Error Message Clarity**
- Field path shows full hierarchy: "indexes → standards → vector → chunk_size"
- Constraint explained: "Input should be greater than or equal to 100"
- Actual value shown: "Got: 50"
- Suggestion provided where possible: "Did you mean 'cpu' instead of 'cpy'?"
- Multiple errors shown together (not just first)

**NFR-U2: IDE Support**
- Autocomplete works in VS Code, PyCharm, Cursor
- Type checking works with mypy, pyright, pylance
- Hover documentation shows Field descriptions
- Go-to-definition navigates to Pydantic model

**NFR-U3: Learning Curve**
- New developers understand config in < 30 minutes
- Schema files are self-documenting
- Examples provided for all common scenarios
- Migration guide available with step-by-step instructions

---

### 5.4 Compatibility

**NFR-C1: Python Version**
- Minimum Python version: 3.10
- Maximum Python version: 3.13 (tested)
- Pydantic v2 compatibility: ≥ 2.0, < 3.0

**NFR-C2: Backwards Compatibility**
- Old config format supported during transition (optional)
- Clear deprecation warnings logged
- Migration period: minimum 1 release cycle
- No forced breaking changes without notice

**NFR-C3: Platform Compatibility**
- Works on Linux, macOS, Windows
- No platform-specific config required
- Path separators handled automatically
- File encodings: UTF-8 universal

---

### 5.5 Reliability

**NFR-R1: Fail-Fast Behavior**
- Invalid config: server refuses to start (100% of cases)
- No partial startup with invalid config
- Exit code: non-zero on validation failure
- Validation deterministic (same config = same result)

**NFR-R2: Error Handling**
- YAML parse errors: clear syntax error message with line number
- File not found: helpful message with expected path
- Permission denied: actionable error message
- No silent failures or default fallbacks for invalid config

**NFR-R3: Configuration Immutability**
- Config objects immutable after load (Pydantic frozen=True)
- No runtime config modifications allowed
- Changes require server restart
- Thread-safe config access

---

### 5.6 Security

**NFR-S1: Input Validation**
- All input validated before use (Pydantic enforces)
- No code injection via config values
- File paths validated (no directory traversal)
- Model names validated against allowlist patterns

**NFR-S2: Secrets Management**
- No secrets in config file (use environment variables)
- Config file permissions: 0644 (world-readable OK, no secrets)
- Sensitive fields clearly marked in schema
- Secrets loading documented separately

---

### 5.7 Extensibility

**NFR-E1: Schema Evolution**
- New fields: backwards compatible (optional with defaults)
- Deprecated fields: supported with warnings for 1+ releases
- Version field supports future migrations
- JSON Schema export enables tooling

**NFR-E2: Validation Extensibility**
- Custom validators: Pydantic @field_validator supported
- Cross-field validation: Pydantic @model_validator supported
- Validation rules: declarative in Field() definitions
- No validation logic scattered in business code

---

### 5.8 Supporting Documentation

NFRs informed by:
- **unified-config-system-pydantic-v2.md**: Performance considerations (config load time), error message examples, validation approach
- **language-choice-analysis.md**: Python version compatibility, future Rust migration readiness (JSON Schema export)
- **INSIGHTS.md (Implementation section)**: Code patterns, testing strategy, error handling requirements

See `supporting-docs/INSIGHTS.md` sections "Design Insights" and "Implementation Insights" for detailed technical constraints.

---

## 6. Out of Scope

Explicitly defines what is NOT included. Items may be considered for future phases.

### Explicitly Excluded

---

#### Features

**Not Included in This Release:**

1. **Runtime Config Hot-Reload**
   - **Reason:** Config changes require validation at startup. Hot-reload introduces complexity (partial updates, rollback, state consistency). Server restart is acceptable for config changes (infrequent operation).
   - **Future Consideration:** Phase 3 if user demand emerges. Would require significant refactoring (immutable config → mutable, validation hooks, rollback mechanism).

2. **Automatic Config Migration Tool**
   - **Reason:** Migration is one-time event. Manual migration with clear guide is simpler and lower risk than automated tool that might misinterpret custom settings.
   - **Future Consideration:** Not planned. Migration guide sufficient for one-time transition.

3. **GUI Config Editor**
   - **Reason:** YAML editing with IDE validation (using JSON Schema) is sufficient. GUI would require web framework, authentication, deployment complexity.
   - **Future Consideration:** Phase 4+ if enterprise users request. Lower priority than core functionality.

4. **Config Versioning & Migration Framework**
   - **Reason:** Beyond simple version field. Full migration framework (transformers, backward compat layers) is premature until config structure stabilizes.
   - **Future Consideration:** Phase 2-3 after initial deployment and feedback on config evolution needs.

5. **Distributed Config Management**
   - **Reason:** prAxIs OS is single-server architecture. Distributed config (etcd, Consul) adds deployment complexity without current use case.
   - **Future Consideration:** Phase 5+ if multi-server deployment becomes requirement.

6. **Config Encryption**
   - **Reason:** Secrets should use environment variables, not config file. Config file contains public settings only (no sensitive data to encrypt).
   - **Future Consideration:** Not planned. Environment variables are standard for secrets.

7. **Multiple Config File Support**
   - **Reason:** Single source of truth principle. Multiple files (overrides, includes) increase complexity and debugging difficulty.
   - **Future Consideration:** Not planned. Use environment-specific YAML files if needed (dev.yaml, prod.yaml), not merging.

---

#### User Types

**Not Supported:**

- **Non-Python Developers:** This config system is Python-specific (Pydantic). Users of other language implementations would need separate config systems.
  - **Mitigation:** JSON Schema export enables some tooling portability.

- **Users Requiring Runtime Config Changes:** Config is immutable after load. Runtime changes not supported.
  - **Mitigation:** Restart is fast (<2s), acceptable for infrequent config changes.

---

#### Platforms

**All Python 3.10+ Platforms Supported:**
- No platform exclusions (Linux, macOS, Windows all supported)
- Python 3.9 and below NOT supported (Pydantic v2 requires 3.10+)

---

#### Integrations

**Not Included:**

1. **REST API for Config Management**
   - **Reason:** Config is static file, not runtime-editable. REST API would enable runtime changes (explicitly out of scope).
   - **Future Consideration:** Not planned.

2. **Web UI for Config Editing**
   - **Reason:** YAML + IDE is sufficient for developers. Web UI adds deployment complexity.
   - **Future Consideration:** Phase 4+ for enterprise users (low priority).

3. **Integration with External Config Stores (Vault, Parameter Store)**
   - **Reason:** Environment variables are standard for secrets. External stores add dependency and deployment complexity.
   - **Future Consideration:** Phase 3+ if demand from enterprise users.

4. **Config Change Notifications / Webhooks**
   - **Reason:** Config changes are infrequent (deploy-time only). No need for real-time notifications.
   - **Future Consideration:** Not planned.

---

## 6.1 Future Enhancements

**Potential Phase 2:**
- Config validation CLI with detailed reporting (FR-010 baseline → enhanced reporting)
- Config diff tool (compare two config files, highlight changes)
- Config template generator (scaffold new config from defaults)

**Potential Phase 3:**
- Limited hot-reload for non-critical settings (logging levels, cache sizes)
- Config migration framework (version transforms)
- Enhanced IDE plugins (real-time validation, autocomplete from running server)

**Potential Phase 4+:**
- Web-based config editor (for non-developer users)
- Integration with external config stores (enterprise feature)
- Multi-environment config management tooling

**Explicitly Not Planned:**
- GUI for config editing (YAML + IDE sufficient)
- Automatic migration tool (one-time manual migration acceptable)
- Runtime config modification API (violates immutability principle)
- Multiple config file merging (violates single source of truth)

---

## 6.2 Supporting Documentation

Out-of-scope items informed by:
- **unified-config-system-pydantic-v2.md**: "Out-of-Scope: Auto-migration of old configs (manual migration with script)", "Out-of-Scope: Runtime config hot-reload (restart required for changes)"
- **language-choice-analysis.md**: Context that Python is requirement (rules out language-agnostic config systems), future Rust migration would need separate config system

See `supporting-docs/INSIGHTS.md` "Requirements Insights" section for explicit out-of-scope statements from source documents.

---

## Phase 1 Summary

**Requirements Gathering Complete:**
- ✅ Business Goals: 4 goals with measurable metrics
- ✅ User Stories: 6 stories (2 critical, 4 high)
- ✅ Functional Requirements: 12 requirements across 4 categories
- ✅ Non-Functional Requirements: 8 categories (Performance, Maintainability, Usability, Compatibility, Reliability, Security, Extensibility)
- ✅ Out-of-Scope: 7 features, 2 user types, 4 integrations explicitly excluded with rationale

**Traceability Established:**
- All requirements trace to user stories
- All user stories trace to business goals
- Supporting documentation referenced throughout

**Ready for Phase 2:** Technical Design

