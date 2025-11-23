# Supporting Documents Index

**Spec:** Project Orientation System  
**Created:** 2025-11-19  
**Total Documents:** 1

## Document Catalog

### 1. Mistletoe-Based Standards Parsing Enhancement

**File:** `2025-11-06-mistletoe-standards-parsing.md`  
**Type:** Design Document  
**Purpose:** Proposes using mistletoe for AST-based markdown parsing with inline metadata extraction. Documents the decision NOT to use YAML frontmatter (too fragile for AI agents) and instead use error-resistant inline metadata pattern (**Metadata**: key=value format).

**Relevance:** Requirements [H], Design [H], Implementation [H]

**Key Topics:**
- YAML frontmatter rejection rationale (AI agents mess up syntax, no consumer validation)
- Inline metadata pattern design (**Metadata**: key=value, error-resistant)
- Mistletoe AST-based parsing for structure-aware chunking
- Graceful degradation for malformed metadata
- Path-based metadata defaults
- Regex-based parsing with fuzzy matching

---

## Cross-Document Analysis

**Common Themes:**
- Error-resistant design for AI-generated content
- Consumer-friendly (no tooling required)
- Visible metadata (not hidden like frontmatter)
- Graceful degradation patterns

**Potential Conflicts:**
- None (single document)

**Coverage Gaps:**
- How to define project-specific orientation queries
- Integration with mcp.yaml configuration system
- Discovery mechanism for orientation metadata
- Query execution order and dependencies

---

## Next Steps

This index will be used in Task 3 to systematically extract insights from each document. The extracted insights will be organized by:
- **Requirements Insights:** User needs, business goals, functional requirements
- **Design Insights:** Architecture patterns, technical approaches, component designs
- **Implementation Insights:** Code patterns, testing strategies, deployment guidance

---

## Extracted Insights

### Requirements Insights (Phase 1)

#### From Mistletoe-Based Standards Parsing Enhancement:
- **User Need:** AI agents need error-resistant metadata pattern that works without consumer validation tooling
- **User Need:** Project-specific orientation queries to rapidly load project context for AI instances
- **Business Goal:** Enable semantic discovery and filtering of standards without brittle YAML syntax
- **Functional Req:** Inline metadata pattern using **Metadata**: key=value format visible to humans
- **Functional Req:** Graceful degradation when metadata is missing, malformed, or contains typos
- **Constraint:** NO YAML frontmatter (AI agents mess up syntax constantly, consumers can't enforce validation)
- **Constraint:** No tooling required in consumer projects (must work with just markdown files)
- **Constraint:** Error-resistant design (praxis-os ships to consumers, can't enforce pre-commit validation)
- **Out of Scope:** LLM-enhanced metadata generation (costs money, auto-generation sufficient)

### Design Insights (Phase 2)

#### From Mistletoe-Based Standards Parsing Enhancement:
- **Architecture:** Regex-based parsing for inline metadata with fuzzy matching and error resistance
- **Architecture:** Path-based metadata defaults when inline metadata missing or unparseable
- **Pattern:** Type coercion with fallback (bool: true/false, int: digits, string: everything else)
- **Pattern:** Comma-separated key=value pairs with error handling (skip malformed, continue parsing)
- **Component:** _extract_inline_metadata() method using re.search() for metadata line detection
- **Component:** Graceful degradation scenarios (missing line, malformed, typo in marker, bad values)
- **Data Model:** Metadata as free-form dictionary (orientation=true, priority=1, difficulty=beginner, domain=ai-assistant)
- **Security:** No code execution risk (regex-based, not eval-based)
- **Performance:** Zero-cost parsing (no LLM calls), single regex match per file

### Implementation Insights (Phase 4)

#### From Mistletoe-Based Standards Parsing Enhancement:
- **Code Pattern:** `re.search(r'\*\*Metadata\*\*:\s*(.+)', content)` for metadata line detection
- **Code Pattern:** `item.split(',')` for key=value pair splitting with error-resistant loop
- **Code Pattern:** `item.split('=', 1)` to handle values containing = character
- **Code Pattern:** `value.lower() in ('true', 'false')` for boolean detection
- **Code Pattern:** `value.isdigit()` for integer detection
- **Code Pattern:** `logger.warning()` + `continue` for graceful error handling (skip, don't fail)
- **Testing Strategy:** Test scenarios: valid metadata, missing metadata, malformed, typos, bad types
- **Testing Strategy:** Verify graceful degradation (missing line → defaults, typo → defaults, bad value → skip)
- **Deployment:** No additional dependencies (uses Python re module, standard library)
- **Monitoring:** Log warnings for unparseable metadata (helps debug without breaking indexing)

### Cross-References

**Validated by Multiple Sources:** N/A (single document)

**Conflicts:** None

**High-Priority Items:**
- Error-resistant inline metadata pattern (core architectural decision)
- NO YAML frontmatter (explicit rejection documented with rationale)
- Graceful degradation design (critical for consumer distribution)

---

## Insight Summary

**Total:** 27 insights  
**By Category:** Requirements [9], Design [9], Implementation [9]  
**Multi-source validated:** 0 (single document)  
**Conflicts to resolve:** 0  
**High-priority items:** 3

**Phase 0 Complete:** ✅ 2025-11-19

