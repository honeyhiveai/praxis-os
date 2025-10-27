# Standards Creation Workflow (v1) - Design Specification

**Date:** 2025-10-13
**Status:** Design Phase
**Type:** Workflow Specification

---

## Executive Summary

A workflow that codifies and validates the standards creation process, ensuring AI-authored content is RAG-optimized, semantically complete, and immediately discoverable. This workflow enforces meta-standards programmatically, closes the self-reinforcing loop, and provides measurable quality metrics for system evolution.

**Business Value:**
- Consistent quality across all standards (no manual oversight needed)
- Automated validation of RAG optimization (discoverability guaranteed)
- Measurable process quality (system-level metrics, not point-in-time scores)
- Self-sustaining system (standards teach creation, creation validates standards)

**Success Criteria:**
- 95%+ standards pass validation on first attempt (after AI learns patterns)
- 85%+ discoverability rate (queries find standard in top 3)
- 0 standards committed without validation passing
- Validation completes in < 60 seconds

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Requirements](#requirements)
3. [Architecture](#architecture)
4. [Phase Breakdown](#phase-breakdown)
5. [Validation Framework](#validation-framework)
6. [Implementation Details](#implementation-details)
7. [Success Metrics](#success-metrics)
8. [Risks and Mitigation](#risks-and-mitigation)

---

## Problem Statement

### Current State

**Manual Standards Creation:**
- AI creates standards following documented guidelines
- Human reviews for RAG optimization
- Manual testing of discoverability
- Inconsistent quality (depends on AI "memory" of guidelines)
- No programmatic validation

**Problems:**
1. **Context degradation:** RAG optimization guidelines fade as conversation length grows
2. **Inconsistent quality:** No enforcement mechanism
3. **No measurable validation:** "Looks good" is subjective
4. **Manual testing:** Time-consuming, incomplete coverage
5. **Discovery failures:** Standards may not be findable via natural queries

### Desired State

**Automated Standards Creation:**
- AI creates standards using workflow
- Workflow validates RAG optimization programmatically
- Automated multi-angle discoverability testing
- Consistent quality through code-enforced validation
- Measurable quality metrics

**Benefits:**
1. **Enforced quality:** Validation gates prevent poor standards
2. **Self-reinforcing:** Standards teach workflow, workflow validates standards
3. **Measurable:** Concrete metrics (structure compliance, discoverability scores)
4. **Scalable:** No manual review bottleneck
5. **Discoverable:** Guaranteed findable via natural queries

---

## Requirements

### Functional Requirements

**FR1: Phase-Gated Workflow**
- 5 phases with validation gates
- Cannot advance without passing checkpoint
- Evidence-based validation (programmatic checks)

**FR2: Structure Validation**
- Required sections present (TL;DR, Questions, Purpose, Examples, Related)
- Headers descriptive and keyword-rich
- Proper markdown structure

**FR3: RAG Optimization Validation**
- Keyword density analysis (TL;DR: high, body: natural)
- Query hooks present (>= 5 natural language questions)
- Headers optimized for semantic search
- Links to source of truth (no duplication)

**FR4: Discoverability Testing**
- Multi-angle query generation (5 angles: how-to, when-to, problem-solving, decision-making, tool-discovery)
- Automated RAG queries against new content
- Relevance scoring and ranking analysis
- >= 80% queries found in top 3 results

**FR5: Semantic Validation**
- Chunk size analysis (100-500 tokens target)
- Semantic completeness (each chunk standalone)
- Link validation (all references resolve)
- No content duplication (links instead)

**FR6: Integration**
- Commit to repository
- Trigger RAG index rebuild
- Validate immediate discoverability
- Update related standards if needed

### Non-Functional Requirements

**NFR1: Performance**
- Validation completes in < 60 seconds total
- Per-phase timeouts (see timeout allocation below)
- RAG queries < 100ms p95
- Index rebuild < 10 seconds (incremental)

**Timeout Allocation:**
```python
PHASE_TIMEOUTS = {
    0: 5,   # Discovery (RAG queries for existing standards)
    1: 10,  # Content creation (parsing and structure validation)
    2: 5,   # RAG optimization (keyword/header analysis)
    3: 15,  # Discoverability (5 queries × 3s each max)
    4: 10,  # Semantic validation (chunk analysis, link checks)
    5: 15   # Integration (commit + index rebuild + retest)
}
TOTAL_BUDGET = 60  # seconds
```

**NFR2: Reliability**
- Validation passes/fails deterministically
- No false positives (strict but accurate)
- Fallback if RAG unavailable (structural validation only)

**NFR3: Usability**
- Clear validation feedback (what failed, why, how to fix)
- Iterative improvement (AI can retry based on feedback)
- Human-readable reports

**NFR4: Maintainability**
- Validation rules configurable
- Easy to add new checks
- Standards-driven (validation rules from meta-standards)

---

## Architecture

### System Context

```
┌─────────────────────────────────────────────────────┐
│  Agent OS Enhanced                                   │
│                                                      │
│  ┌──────────────┐      ┌─────────────────┐         │
│  │   AI Agent   │──┬──→│  Standards      │         │
│  │              │  │   │  Creation       │         │
│  └──────────────┘  │   │  Workflow (NEW) │         │
│                    │   └─────────────────┘         │
│                    │            │                   │
│                    │            ↓                   │
│                    │   ┌─────────────────┐         │
│                    └──→│  RAG Engine     │         │
│                        │  (Validation)   │         │
│                        └─────────────────┘         │
│                                 │                   │
│                                 ↓                   │
│                        ┌─────────────────┐         │
│                        │  Universal      │         │
│                        │  Standards      │         │
│                        │  (Meta-docs)    │         │
│                        └─────────────────┘         │
└─────────────────────────────────────────────────────┘
```

### Workflow Architecture

```
Phase 0: Discovery & Context
    ↓ [Checkpoint: Context Gathered]
Phase 1: Content Creation
    ↓ [Checkpoint: Structure Valid]
Phase 2: RAG Optimization
    ↓ [Checkpoint: RAG Optimized]
Phase 3: Discoverability Testing
    ↓ [Checkpoint: Discoverable]
Phase 4: Semantic Validation
    ↓ [Checkpoint: Semantically Complete]
Phase 5: Integration & Commit
    ↓ [Checkpoint: Committed & Indexed]
✓ Complete
```

### Component Responsibilities

**Workflow Engine:**
- Phase sequencing
- Checkpoint validation
- State persistence
- Evidence collection

**Validation Module:**
- Structure checks (sections, headers, format)
- RAG optimization analysis (keywords, hooks, density)
- Discoverability testing (multi-angle queries)
- Semantic analysis (chunks, completeness, links)

**RAG Engine:**
- Query execution for testing
- Relevance scoring
- Ranking analysis
- Index rebuild triggering

**Report Generator:**
- Validation report creation
- Feedback formatting
- Metrics collection
- Evidence presentation

---

## Phase Breakdown

### Phase 0: Discovery & Context

**Goal:** Gather context and understand domain before creating standard.

**Tasks:**
1. Query existing standards for similar topics
2. Identify domain keywords and concepts
3. Review related standards for patterns
4. Extract key concepts and terminology
5. Understand target audience (AI agents querying naturally)

**Checkpoint Validation:**
```python
{
    "domain_keywords_identified": List[str],  # >= 10 keywords
    "related_standards_found": List[str],     # >= 2 standards
    "key_concepts_extracted": List[str],      # >= 5 concepts
    "audience_understood": bool               # True
}
```

**Expected Duration:** 2-3 minutes

---

### Phase 1: Content Creation

**Goal:** Author standard with all required sections.

**Required Sections:**
1. **🚨 Quick Reference / TL;DR** (200-400 tokens, high keyword density)
2. **❓ Questions This Answers** (>= 5 natural language questions)
3. **Purpose** (Why this standard exists)
4. **Main Content** (Detailed guidance, examples, patterns)
5. **Examples** (>= 2 concrete examples)
6. **Related Standards** (Links to source of truth)

**Tasks:**
1. Write Quick Reference section (front-load critical info)
2. Write Questions This Answers (>= 5 queries agents will use)
3. Write Purpose section (problem + solution)
4. Write detailed content sections
5. Add concrete examples (working code/scenarios)
6. Link to related standards (no duplication)

**Checkpoint Validation:**
```python
structure_validation = {
    "has_quick_ref": bool,           # Required
    "has_questions": bool,           # Required, >= 5 questions
    "has_purpose": bool,             # Required
    "has_examples": bool,            # Required, >= 2 examples
    "has_related_standards": bool,   # Required, >= 1 link
    "sections_complete": bool,       # All sections have content
    "markdown_valid": bool           # Valid markdown syntax
}
```

**Expected Duration:** 5-7 minutes

---

### Phase 2: RAG Optimization

**Goal:** Optimize content for RAG semantic search discovery.

**Tasks:**
1. Optimize keyword density
   - TL;DR: High density (topic appears 3-5 times)
   - Body: Natural density (not stuffing, not sparse)
2. Add query hooks throughout content
   - Use natural language phrasing
   - Match how agents think ("how to", "when should", "what is")
3. Optimize headers for keywords
   - Descriptive, not generic ("How to Execute Specs" not "Usage")
   - Include domain keywords
   - Specific to content
4. Ensure semantic chunking
   - Respect markdown boundaries
   - Target 100-500 tokens per chunk
   - Each chunk semantically complete
5. Add explicit keywords section in TL;DR

**Checkpoint Validation:**
```python
rag_optimization = {
    "keyword_density": {
        "tldr": "high",          # Topic appears 3-5 times
        "body": "natural"        # Natural distribution
    },
    "query_hooks": {
        "count": int,            # >= 5 hooks
        "natural_language": bool # Not generic questions
    },
    "headers": {
        "descriptive": bool,     # Specific, not generic
        "keyword_rich": bool,    # Include domain terms
        "count": int             # >= 3 major headers
    },
    "keywords_explicit": bool,   # "Keywords:" section in TL;DR
    "semantic_chunks_valid": bool  # Chunks 100-500 tokens
}
```

**Expected Duration:** 3-5 minutes

---

### Phase 3: Discoverability Testing

**Goal:** Validate standard is discoverable via natural queries from multiple angles.

**Test Strategy:**
Generate queries from 5 angles:
1. **How-to:** "How do I [task]?"
2. **When-to:** "When should I use [concept]?"
3. **Problem-solving:** "[Problem] not working"
4. **Decision-making:** "Should I use [X] or [Y]?"
5. **Tool-discovery:** "What tool for [task]?"

**Tasks:**
1. Generate 5 test queries (one per angle)
2. Execute queries against RAG engine (with new standard)
3. Measure relevance scores and ranking
4. Analyze results (found in top 3?)
5. Iterate if discoverability < 80%

**Checkpoint Validation:**
```python
discoverability = {
    "queries_tested": int,               # Should be 5
    "queries_found_top3": int,           # >= 4 (80%)
    "average_relevance": float,          # >= 0.85
    "average_rank": float,               # <= 2.0 (for found queries)
    "per_angle_results": {
        "how_to": {"found": bool, "rank": int, "relevance": float},
        "when_to": {"found": bool, "rank": int, "relevance": float},
        "problem_solving": {"found": bool, "rank": int, "relevance": float},
        "decision_making": {"found": bool, "rank": int, "relevance": float},
        "tool_discovery": {"found": bool, "rank": int, "relevance": float}
    }
}
```

**Success Criteria:**
- >= 80% queries found in top 3 (4/5 queries)
- Average relevance >= 0.85
- No angle completely missing (at least 1 query per angle works)

**Expected Duration:** 2-3 minutes

---

### Phase 4: Semantic Validation

**Goal:** Ensure semantic quality and completeness.

**Tasks:**
1. Analyze chunk sizes (after semantic chunking)
2. Verify semantic completeness (chunks standalone)
3. Validate all links (references resolve)
4. Check no duplication (links to source of truth)
5. Verify code examples (if any) are complete

**Checkpoint Validation:**
```python
semantic_validation = {
    "chunk_sizes": {
        "min": int,              # >= 100 tokens
        "max": int,              # <= 500 tokens
        "avg": int,              # 200-400 tokens
        "count": int             # Total chunks
    },
    "semantic_completeness": {
        "chunks_standalone": bool,      # Each chunk complete
        "no_orphaned_refs": bool,       # No dangling references
        "context_preserved": bool       # Parent headers tracked
    },
    "links": {
        "total": int,
        "valid": int,                   # All must resolve
        "broken": List[str]             # Empty if valid
    },
    "no_duplication": bool,             # Links instead of duplicating
    "code_examples_complete": bool      # If present, complete
}
```

**Expected Duration:** 1-2 minutes

---

### Phase 5: Integration & Commit

**Goal:** Commit standard and validate immediate discoverability.

**Tasks:**
1. Generate final validation report
2. Commit standard to repository
3. Trigger RAG index rebuild (incremental)
4. Validate standard immediately discoverable
5. Update related standards if needed (backlinks)
6. Record metrics

**Checkpoint Validation:**
```python
integration = {
    "file_committed": bool,              # Git commit successful
    "index_rebuilt": bool,               # RAG index updated
    "immediately_discoverable": bool,    # Re-test primary query
    "related_standards_updated": bool,   # Backlinks added if needed
    "metrics_recorded": bool             # Validation metrics saved
}
```

**Expected Duration:** 1-2 minutes

---

## Validation Framework

### Validation Architecture

```python
class ValidationResult:
    """Result of validation check."""
    passed: bool
    score: float  # 0.0 - 1.0
    details: Dict[str, Any]
    feedback: str  # Human-readable feedback
    evidence: Dict[str, Any]  # Evidence for this check

class PhaseValidation:
    """Validation for a workflow phase."""
    phase_id: int
    checks: List[ValidationCheck]
    
    def validate(self, evidence: Dict) -> ValidationResult:
        """Run all checks, return aggregated result."""
        results = [check.run(evidence) for check in self.checks]
        return self.aggregate(results)

class WorkflowValidator:
    """Validates entire workflow execution."""
    phases: List[PhaseValidation]
    
    def validate_phase(self, phase_id: int, evidence: Dict) -> ValidationResult:
        """Validate specific phase."""
        return self.phases[phase_id].validate(evidence)
    
    def generate_report(self) -> ValidationReport:
        """Generate comprehensive validation report."""
        return ValidationReport(
            phases=self.phase_results,
            overall=self.compute_overall(),
            metrics=self.collect_metrics()
        )
```

### Validation Checks

#### Structure Validation
```python
def validate_structure(content: str) -> ValidationResult:
    """Validate required sections present."""
    required = [
        "🚨.*Quick Reference|TL;DR",  # Regex patterns
        "❓.*Questions This Answers",
        "Purpose",
        "Examples?",
        "Related Standards"
    ]
    
    found = {}
    for section in required:
        found[section] = bool(re.search(section, content))
    
    passed = all(found.values())
    score = sum(found.values()) / len(found)
    
    return ValidationResult(
        passed=passed,
        score=score,
        details=found,
        feedback=generate_structure_feedback(found)
    )
```

#### RAG Optimization Validation
```python
def analyze_keyword_density(text: str, topics: List[str]) -> str:
    """
    Calculate keyword density using tf-idf normalization.
    
    :param text: Text to analyze
    :param topics: Primary keywords from Phase 0 domain analysis
    :return: "high" (2-5%), "natural" (0.5-2%), "sparse" (<0.5%), "stuffing" (>5%)
    
    Algorithm:
    1. Tokenize text (lowercase, remove punctuation)
    2. Count occurrences of each topic keyword (including variants)
       - Singular/plural forms
       - Hyphenated variants ("thread-safety" vs "thread safety")
    3. Calculate density = (keyword_count / total_tokens) * 100
    4. Return classification based on thresholds
    """
    tokens = tokenize(text.lower())
    topic_variants = expand_topic_variants(topics)  # thread-safety → [thread, safety, thread-safety]
    
    keyword_count = sum(1 for token in tokens if token in topic_variants)
    density = (keyword_count / len(tokens)) * 100
    
    if density < 0.5:
        return "sparse"
    elif density < 2.0:
        return "natural"
    elif density <= 5.0:
        return "high"
    else:
        return "stuffing"

def validate_rag_optimization(content: str, domain_topics: List[str]) -> ValidationResult:
    """Validate RAG optimization."""
    
    # Keyword density analysis
    tldr = extract_section(content, "Quick Reference|TL;DR")
    body = extract_body(content)
    
    tldr_density = analyze_keyword_density(tldr, domain_topics)  # High expected
    body_density = analyze_keyword_density(body, domain_topics)  # Natural expected
    
    # Query hooks
    questions = extract_section(content, "Questions This Answers")
    hooks_count = count_questions(questions)
    hooks_natural = analyze_question_naturalness(questions)
    
    # Headers
    headers = extract_headers(content)
    headers_descriptive = all(is_descriptive(h) for h in headers)
    headers_keyword_rich = all(has_keywords(h) for h in headers)
    
    checks = {
        "tldr_density": tldr_density == "high",
        "body_density": body_density == "natural",
        "hooks_count": hooks_count >= 5,
        "hooks_natural": hooks_natural,
        "headers_descriptive": headers_descriptive,
        "headers_keyword_rich": headers_keyword_rich
    }
    
    passed = all(checks.values())
    score = sum(checks.values()) / len(checks)
    
    return ValidationResult(
        passed=passed,
        score=score,
        details=checks,
        feedback=generate_rag_feedback(checks)
    )
```

#### Discoverability Testing
```python
async def test_discoverability(
    content: str,
    domain: str,
    rag_engine: RAGEngine
) -> ValidationResult:
    """Test if standard discoverable from multiple angles."""
    
    # Generate test queries
    angles = ["how_to", "when_to", "problem_solving", 
              "decision_making", "tool_discovery"]
    queries = generate_queries(domain, angles)
    
    # Test each query
    results = []
    for angle, query in zip(angles, queries):
        search_result = await rag_engine.search(query, n_results=5)
        
        # Check if new standard in results
        rank = find_content_rank(search_result, content)
        relevance = get_content_relevance(search_result, content)
        found = rank <= 3
        
        results.append({
            "angle": angle,
            "query": query,
            "found": found,
            "rank": rank if found else None,
            "relevance": relevance
        })
    
    # Calculate metrics
    found_count = sum(r["found"] for r in results)
    found_rate = found_count / len(results)
    avg_relevance = mean(r["relevance"] for r in results if r["found"])
    avg_rank = mean(r["rank"] for r in results if r["found"])
    
    passed = found_rate >= 0.8 and avg_relevance >= 0.85
    
    return ValidationResult(
        passed=passed,
        score=found_rate,
        details={
            "queries_tested": len(results),
            "queries_found": found_count,
            "found_rate": found_rate,
            "average_relevance": avg_relevance,
            "average_rank": avg_rank,
            "per_angle": results
        },
        feedback=generate_discoverability_feedback(results)
    )
```

#### Semantic Validation
```python
def validate_links(content: str, base_path: str) -> Dict[str, Any]:
    """
    Validate links resolve correctly.
    
    v1.0 Scope (fast, local checks only):
    - Internal file links: Check file exists (standards/..., workflows/...)
    - Relative links: Resolve against base_path and check existence
    - External URLs: DNS check only (no HTTP requests)
    - Anchor links: Skip validation (complex, defer to v2.0)
    
    :param content: Standard content with markdown links
    :param base_path: Base directory for relative path resolution
    :return: Validation result with broken link details
    """
    links = extract_markdown_links(content)
    
    results = {
        "total": len(links),
        "valid": 0,
        "broken": []
    }
    
    for link in links:
        if link.startswith("http://") or link.startswith("https://"):
            # External URL: DNS check only
            if dns_resolve(urlparse(link).netloc):
                results["valid"] += 1
            else:
                results["broken"].append(f"{link} (DNS failed)")
        
        elif link.startswith("#"):
            # Anchor link: Skip in v1.0
            results["valid"] += 1
        
        else:
            # Internal/relative file link
            resolved_path = resolve_path(base_path, link)
            if os.path.exists(resolved_path):
                results["valid"] += 1
            else:
                results["broken"].append(f"{link} (file not found)")
    
    return results

def validate_semantic_quality(content: str, base_path: str) -> ValidationResult:
    """Validate semantic completeness."""
    
    # Chunk analysis
    chunks = semantic_chunk(content)
    chunk_sizes = [len(c.split()) for c in chunks]
    
    # Link validation
    link_results = validate_links(content, base_path)
    
    checks = {
        "chunk_sizes_valid": all(100 <= s <= 500 for s in chunk_sizes),
        "avg_size_optimal": 200 <= mean(chunk_sizes) <= 400,
        "chunks_standalone": all(is_complete(c) for c in chunks),
        "no_orphaned_refs": not has_dangling_references(content),
        "links_valid": len(link_results["broken"]) == 0,
        "no_duplication": not has_duplicate_content(content)
    }
    
    passed = all(checks.values())
    score = sum(checks.values()) / len(checks)
    
    return ValidationResult(
        passed=passed,
        score=score,
        details={
            "chunk_count": len(chunks),
            "chunk_sizes": {"min": min(chunk_sizes), 
                           "max": max(chunk_sizes),
                           "avg": mean(chunk_sizes)},
            **checks
        },
        feedback=generate_semantic_feedback(checks)
    )
```

### Validation Report Format

```yaml
Standard: api-error-handling.md
Date: 2025-10-13 11:30:00
Status: ✅ VALIDATED

Phase 0: Discovery & Context ✅
  Domain Keywords: 12 found
  Related Standards: 3 found
  Key Concepts: 7 extracted
  Duration: 2m 15s

Phase 1: Content Creation ✅
  Quick Reference: ✅ Present (350 tokens)
  Questions This Answers: ✅ 8 questions
  Purpose: ✅ Present
  Examples: ✅ 4 examples
  Related Standards: ✅ 3 links
  Structure Score: 1.0
  Duration: 6m 30s

Phase 2: RAG Optimization ✅
  Keyword Density:
    TL;DR: ✅ High (5 occurrences)
    Body: ✅ Natural (distributed)
  Query Hooks: ✅ 8 hooks (natural language)
  Headers: ✅ Descriptive & keyword-rich (5 headers)
  Keywords Section: ✅ Present
  Optimization Score: 1.0
  Duration: 4m 15s

Phase 3: Discoverability Testing ✅
  Queries Tested: 5
  Queries Found (top 3): 4 (80%)
  Average Relevance: 0.87
  Average Rank: 2.0
  
  Results by Angle:
    how_to: ✅ Rank #2, Relevance 0.89
    when_to: ✅ Rank #1, Relevance 0.92
    problem_solving: ✅ Rank #3, Relevance 0.85
    decision_making: ✅ Rank #2, Relevance 0.87
    tool_discovery: ❌ Not in top 3 (Rank #7, Relevance 0.72)
  
  Discoverability Score: 0.80
  Duration: 2m 45s

Phase 4: Semantic Validation ✅
  Chunks: 6 total
  Chunk Sizes: 185-425 tokens (avg: 280)
  Semantic Completeness: ✅ All chunks standalone
  Links: ✅ 3/3 valid
  No Duplication: ✅
  Semantic Score: 1.0
  Duration: 1m 30s

Phase 5: Integration ✅
  Committed: ✅ Git commit abc123
  Index Rebuilt: ✅ Incremental update (8s)
  Immediately Discoverable: ✅ Re-tested primary query
  Related Standards Updated: ✅ Added backlinks
  Duration: 1m 45s

Overall: ✅ VALIDATED
Total Duration: 18m 40s
Quality Score: 0.96 (excellent)

Recommendations:
- Consider adding query hook for "tool discovery" angle
- Standard ready to use immediately
- AI can reference this standard starting now
```

---

## Implementation Details

### File Structure

```
universal/workflows/standards_creation_v1/
├── metadata.json                      # Workflow metadata
├── README.md                          # Overview & usage
├── phases/
│   ├── 0-discovery/
│   │   ├── phase.md                  # Phase overview
│   │   ├── task-1-query-existing.md
│   │   ├── task-2-extract-concepts.md
│   │   └── task-3-understand-audience.md
│   ├── 1-content-creation/
│   │   ├── phase.md
│   │   ├── task-1-quick-reference.md
│   │   ├── task-2-questions.md
│   │   ├── task-3-purpose.md
│   │   ├── task-4-detailed-content.md
│   │   ├── task-5-examples.md
│   │   └── task-6-related-standards.md
│   ├── 2-rag-optimization/
│   │   ├── phase.md
│   │   ├── task-1-keyword-density.md
│   │   ├── task-2-query-hooks.md
│   │   ├── task-3-headers.md
│   │   └── task-4-semantic-chunks.md
│   ├── 3-discoverability-testing/
│   │   ├── phase.md
│   │   ├── task-1-generate-queries.md
│   │   ├── task-2-execute-tests.md
│   │   └── task-3-analyze-results.md
│   ├── 4-semantic-validation/
│   │   ├── phase.md
│   │   ├── task-1-chunk-analysis.md
│   │   ├── task-2-completeness.md
│   │   └── task-3-links-duplication.md
│   └── 5-integration/
│       ├── phase.md
│       ├── task-1-commit.md
│       ├── task-2-index-rebuild.md
│       └── task-3-validate-discovery.md
└── validation/
    ├── structure_validator.py
    ├── rag_optimizer_validator.py
    ├── discoverability_tester.py
    ├── semantic_validator.py
    └── report_generator.py
```

### Validation Module Implementation

```python
# mcp_server/validation/standards_validator.py

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ValidationCheck:
    """Single validation check."""
    name: str
    category: str  # "structure", "rag", "discoverability", "semantic"
    passed: bool
    score: float
    details: Dict
    feedback: str

class StandardsValidator:
    """Validates standards against meta-standards."""
    
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
    
    def validate_structure(self, content: str) -> ValidationCheck:
        """Validate required sections present."""
        # Implementation from earlier
        pass
    
    def validate_rag_optimization(self, content: str) -> ValidationCheck:
        """Validate RAG optimization."""
        # Implementation from earlier
        pass
    
    async def validate_discoverability(
        self, 
        content: str, 
        domain: str
    ) -> ValidationCheck:
        """Test discoverability from multiple angles."""
        # Implementation from earlier
        pass
    
    def validate_semantic_quality(self, content: str) -> ValidationCheck:
        """Validate semantic completeness."""
        # Implementation from earlier
        pass
    
    async def validate_all(
        self, 
        content: str, 
        domain: str
    ) -> List[ValidationCheck]:
        """Run all validations."""
        return [
            self.validate_structure(content),
            self.validate_rag_optimization(content),
            await self.validate_discoverability(content, domain),
            self.validate_semantic_quality(content)
        ]
```

### Workflow Integration

```python
# mcp_server/workflow_engine.py

class WorkflowEngine:
    """Existing workflow engine with standards validation."""
    
    def __init__(self, standards_validator: StandardsValidator):
        self.validator = standards_validator
        # ... existing init
    
    async def execute_standards_creation_phase(
        self, 
        phase_id: int,
        state: WorkflowState
    ) -> PhaseResult:
        """Execute standards creation phase with validation."""
        
        # Execute phase tasks (existing logic)
        result = await self.execute_phase(phase_id, state)
        
        # Run validation for checkpoint
        if phase_id == 1:  # Content Creation
            validation = self.validator.validate_structure(
                state.evidence["content"]
            )
        elif phase_id == 2:  # RAG Optimization
            validation = self.validator.validate_rag_optimization(
                state.evidence["content"]
            )
        elif phase_id == 3:  # Discoverability
            validation = await self.validator.validate_discoverability(
                state.evidence["content"],
                state.evidence["domain"]
            )
        elif phase_id == 4:  # Semantic
            validation = self.validator.validate_semantic_quality(
                state.evidence["content"]
            )
        
        # Check if validation passed
        if not validation.passed:
            return PhaseResult(
                success=False,
                message=f"Validation failed: {validation.feedback}",
                evidence={"validation": validation}
            )
        
        return PhaseResult(
            success=True,
            evidence={"validation": validation}
        )
```

---

## Success Metrics

### Process Quality Metrics

**Metric 1: Validation Pass Rate**
- Target: >= 95% standards pass validation on first attempt (after AI learns)
- Measured: Pass/fail per phase, overall
- Indicates: AI has internalized meta-standards

**Metric 2: Discoverability Rate**
- Target: >= 85% queries find standard in top 3
- Measured: Found rate per standard, averaged across all standards
- Indicates: Standards are RAG-optimized effectively

**Metric 3: Structure Compliance**
- Target: 100% standards have all required sections
- Measured: Section presence per standard
- Indicates: Consistency across all standards

**Metric 4: Semantic Quality**
- Target: >= 95% chunks within optimal size range (100-500 tokens)
- Measured: Chunk size distribution per standard
- Indicates: Proper semantic chunking

**Metric 5: Validation Time**
- Target: < 60 seconds total validation time
- Measured: Duration per phase, total
- Indicates: Workflow efficiency

### System Evolution Metrics

**Metric 6: Learning Curve**
- Measure: Pass rate over time (should increase as AI learns)
- Target: Reach 95% by 20th standard created
- Indicates: Self-reinforcing loop working

**Metric 7: Coverage Expansion**
- Measure: Total standards created per month
- Target: Steady growth (not tracked currently)
- Indicates: System scaling

**Metric 8: Quality Consistency**
- Measure: Standard deviation of quality scores
- Target: Low variance (<0.1)
- Indicates: Consistent quality across all standards

### Usage Metrics

**Metric 9: Standards Discoverability**
- Measure: Query success rate (queries returning standards)
- Target: >= 90% natural queries find relevant standard
- Indicates: System working for end-users

**Metric 10: Standards Utilization**
- Measure: How often standards are queried in actual usage
- Target: All standards queried at least once per month
- Indicates: Standards are actively used, not just created

---

## Risks and Mitigation

### Risk 1: Phase 3 Discoverability Testing Implementation Gap

**Risk:** Cannot test discoverability against content not yet in RAG index

**Likelihood:** High (fundamental architectural issue)

**Impact:** Critical (Phase 3 cannot work as specified)

**Mitigation Strategy:**

**MVP Approach (v1.0):**
```python
def validate_discoverability_mvp(
    content: str, 
    questions: List[str],
    embed_fn: Callable
) -> ValidationResult:
    """
    Test discoverability using embedding similarity.
    Skips full RAG until temporary indexing implemented.
    
    :param content: Standard content to test
    :param questions: Generated test questions
    :param embed_fn: Embedding function (local or OpenAI)
    :return: Validation result with similarity scores
    """
    content_embedding = embed_fn(content)
    
    results = []
    for question in questions:
        question_embedding = embed_fn(question)
        similarity = cosine_similarity(content_embedding, question_embedding)
        
        results.append({
            "question": question,
            "similarity": similarity,
            "found": similarity >= 0.75  # Threshold for "discoverable"
        })
    
    found_rate = sum(r["found"] for r in results) / len(results)
    
    return ValidationResult(
        passed=found_rate >= 0.80,
        score=found_rate,
        details={"results": results, "method": "embedding_similarity_mvp"},
        feedback=f"Discoverability: {found_rate:.0%} (embedding-based)"
    )
```

**Calibration Process (v1.0 Prerequisite):**
```python
def calibrate_embedding_threshold(
    calibration_standards: List[str],
    test_queries: Dict[str, List[str]]  # {standard_id: [queries]}
) -> float:
    """
    Calibrate embedding similarity threshold against actual RAG results.
    
    Run once during v1.0 setup to ground MVP threshold in real data.
    
    :param calibration_standards: 10-15 existing standards
    :param test_queries: 5 test queries per standard
    :return: Optimal similarity threshold
    
    Process:
    1. For each calibration standard:
       a. Embed standard content
       b. Embed test queries
       c. Calculate cosine similarities
       d. Run actual RAG queries for comparison
       e. Measure correlation between similarity and RAG rank
    2. Find threshold that maximizes agreement
       - True positive: High similarity + top 3 RAG rank
       - False negative: Low similarity but top 3 RAG rank
       - False positive: High similarity but not in top 3
    3. Optimize for minimal false negatives (don't reject good standards)
    """
    results = []
    for standard_id, queries in test_queries.items():
        standard_content = load_standard(standard_id)
        standard_embedding = embed_fn(standard_content)
        
        for query in queries:
            query_embedding = embed_fn(query)
            similarity = cosine_similarity(standard_embedding, query_embedding)
            
            # Compare with actual RAG
            rag_results = rag_engine.search(query, n_results=5)
            rag_rank = find_content_rank(rag_results, standard_content)
            
            results.append({
                "similarity": similarity,
                "in_top3": rag_rank <= 3
            })
    
    # Find threshold with best F1 score (balance precision/recall)
    optimal_threshold = optimize_threshold(results)
    return optimal_threshold  # Expected: 0.70-0.80 range
```

**Full Implementation (v2.0):**
- Add temporary test index capability
- Index new standard content temporarily
- Run actual RAG queries
- Clean up test index after validation

---

### Risk 2: Subjective Validations Lack Concrete Rules

**Risk:** "Natural language" and "semantic completeness" are subjective

**Likelihood:** High

**Impact:** Medium (inconsistent validation results)

**Mitigation Strategy:**

**Concrete Thresholds:**
```python
# Keyword Density Thresholds
KEYWORD_DENSITY_HIGH = 0.03      # 3% in TL;DR section
KEYWORD_DENSITY_NATURAL = 0.01   # 1% in body
KEYWORD_DENSITY_MAX = 0.05       # 5% = keyword stuffing

# Question Quality Rules
MIN_QUESTION_LENGTH = 5   # words
MAX_QUESTION_LENGTH = 15  # words
REQUIRED_WH_WORDS = ["how", "what", "when", "where", "why", "which", "who"]

def is_natural_question(q: str) -> bool:
    """Check if question meets naturalness criteria."""
    words = q.split()
    word_count = len(words)
    starts_with_wh = any(q.lower().startswith(wh) for wh in REQUIRED_WH_WORDS)
    
    return (MIN_QUESTION_LENGTH <= word_count <= MAX_QUESTION_LENGTH 
            and starts_with_wh)

# Chunk Size Ranges
MIN_CHUNK_SIZE = 100   # tokens
MAX_CHUNK_SIZE = 500   # tokens
OPTIMAL_CHUNK_RANGE = (200, 400)  # optimal range

# Semantic Completeness (MVP Heuristics)
def is_chunk_complete_mvp(chunk: str, parent_header: Optional[str] = None) -> bool:
    """
    Simple heuristics for semantic completeness.
    
    :param chunk: Chunk text to validate
    :param parent_header: Parent header providing context (tracked during chunking)
    :return: True if chunk appears semantically complete
    """
    checks = {
        "has_complete_sentences": all(
            s.strip().endswith(('.', '!', '?', ':')) 
            for s in chunk.split('\n') if s.strip()
        ),
        "has_context_or_header": (
            parent_header is not None  # Parent header provides context
            or bool(re.search(r'^#+\s', chunk, re.MULTILINE))  # Or chunk has own header
        ),
        "min_length": len(chunk.split()) >= 50,
        "not_empty": len(chunk.strip()) > 0
    }
    
    # If starts with pronoun, require parent header for context
    if chunk.lstrip().lower().startswith(("this", "that", "these", "it", "they")):
        checks["has_parent_context"] = parent_header is not None
        return sum(checks.values()) >= 4  # 4/5 checks must pass
    
    return sum(checks.values()) >= 3  # 3/4 checks must pass
```

---

### Risk 3: Performance Degradation

**Risk:** Validation exceeds 60-second target

**Likelihood:** Medium (depends on RAG performance)

**Impact:** Medium (slower workflow, user frustration)

**Mitigation Strategy:**

**Performance Optimizations:**
1. **Parallel RAG Queries:**
   ```python
   async def test_discoverability_parallel(queries: List[str]):
       tasks = [rag_engine.search(q) for q in queries]
       results = await asyncio.gather(*tasks)
   ```

2. **Link Validation Caching:**
   ```python
   @lru_cache(maxsize=1000)
   def validate_link(url: str) -> bool:
       # Cache results to avoid redundant HTTP requests
       pass
   ```

3. **Timeout Limits:**
   ```python
   VALIDATION_TIMEOUT = 60  # seconds
   PHASE_TIMEOUT = 15  # seconds per phase
   RAG_QUERY_TIMEOUT = 5  # seconds per query
   ```

4. **Graceful Degradation:**
   - If RAG unavailable: Skip Phase 3, validate structure only
   - If timeout: Return partial results with warning
   - If network issues: Skip link validation, warn user

---

### Risk 4: RAG Engine Unavailable

**Risk:** MCP connection fails, RAG engine offline

**Likelihood:** Medium (network/config issues)

**Impact:** High (Phase 3 cannot execute)

**Mitigation Strategy:**

**Fallback Modes:**
```python
def validate_with_fallback(content: str) -> ValidationResult:
    """
    Attempt full validation with fallbacks.
    
    :param content: Standard content to validate
    :return: Validation result (possibly degraded)
    """
    try:
        # Attempt full validation with RAG
        return validate_full(content)
    except RAGConnectionError:
        logger.warning("RAG unavailable, using embedding-only validation")
        return validate_embedding_only(content)
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return validate_structure_only(content)
```

**Validation Levels:**
1. **Full (Optimal):** All phases with RAG queries
2. **Degraded (Embedding):** Structure + embedding similarity
3. **Minimal (Structure):** Structure validation only

**User Notification:**
```
⚠️ Warning: RAG engine unavailable
Validation running in degraded mode (structure + embeddings only)
Full discoverability testing skipped - manual review recommended
```

---

### Risk 5: Index Rebuild Fails After Commit

**Risk:** Standard committed but index rebuild fails

**Likelihood:** Low (robust incremental rebuild)

**Impact:** High (standard not discoverable)

**Mitigation Strategy:**

**Synchronous Rebuild with Rollback:**
```python
async def commit_with_validation(standard: Standard) -> CommitResult:
    """
    Commit standard and validate discoverability.
    Rollback if validation fails.
    
    :param standard: Standard to commit
    :return: Commit result with validation status
    """
    # 1. Commit to git
    commit_hash = git_commit(standard)
    
    try:
        # 2. Rebuild index (synchronous, timeout 30s)
        await rebuild_index(timeout=30)
        
        # 3. Validate immediate discoverability
        result = await test_primary_query(standard.primary_topic)
        
        if not result.found:
            # 4. Rollback if not discoverable
            git_revert(commit_hash)
            return CommitResult(
                success=False,
                message="Standard not discoverable after commit",
                action="rolled_back"
            )
        
        return CommitResult(success=True, commit=commit_hash)
        
    except TimeoutError:
        # Index rebuild took too long
        logger.warning("Index rebuild timeout - manual verification needed")
        return CommitResult(
            success=True,  # Commit succeeded
            commit=commit_hash,
            warning="Index rebuild timeout - verify discoverability manually"
        )
```

---

### Risk 6: Context Window Exhaustion

**Risk:** Large standards exceed available context

**Likelihood:** Low (most standards < 100K tokens)

**Impact:** Medium (cannot validate in single pass)

**Mitigation Strategy:**

**Chunked Validation:**
- Validate sections independently
- Aggregate results
- Only load full content for final check

**Validation Order:**
1. Quick checks first (structure, chunk sizes)
2. Expensive checks last (discoverability, semantic)
3. Stop early if quick checks fail

---

### Risk 7: False Positives/Negatives

**Risk:** Validation incorrectly passes/fails good standards

**Likelihood:** Medium (imperfect heuristics)

**Impact:** High (trust in system)

**Mitigation Strategy:**

**Conservative Validation:**
- Prefer false positives (flag for review)
- Clear feedback on why validation failed
- Manual override capability for edge cases

**Validation Report Details:**
```yaml
Validation: ❌ FAILED
Reason: Discoverability below threshold (60% vs 80% target)

Details:
  Queries Tested: 5
  Queries Found: 3
  Missing Angles:
    - "problem_solving": Query did not rank in top 3
    - "tool_discovery": Low relevance score (0.68)

Recommendations:
  1. Add more problem-solving keywords to TL;DR
  2. Include tool names in headers
  3. Retry validation after edits

Override: If this is intentional, use --force flag
```

---

### Risk 8: Workflow Learning Curve

**Risk:** AI agents struggle with new workflow initially

**Likelihood:** High (new process)

**Impact:** Low (improves over time)

**Mitigation Strategy:**

**Progressive Onboarding:**
1. **v1.0:** Structure validation only (easy win)
2. **v1.1:** Add RAG optimization checks
3. **v1.2:** Add discoverability testing (MVP)
4. **v1.3:** Add semantic validation
5. **v2.0:** Full implementation with temporary indexing

**Training Materials:**
- Example standards that pass all validations
- Common failure patterns and fixes
- Query construction templates
- Validation troubleshooting guide

**Iterative Improvement:**
- Track validation pass rates over time
- Metric 6: Learning Curve (should reach 95% by 20th standard)
- Adjust thresholds based on real-world usage

---

## Implementation Phases

### Phase Alpha: MVP (Weeks 1-2)

**Goal:** Basic workflow with structure validation

**Deliverables:**
- Phase 0-1 implemented
- Structure validation only
- Basic validation reporting

**Success Criteria:**
- Can create standards with validated structure
- Workflow engine integration works
- Reports are readable

---

### Phase Beta: Core Validation (Weeks 3-4)

**Goal:** Add RAG optimization and embedding-based discoverability

**Deliverables:**
- Phase 2 implemented (keyword density, query hooks)
- Phase 3 MVP (embedding similarity)
- Phase 4 basic (chunk sizes)

**Success Criteria:**
- Standards pass RAG optimization checks
- Embedding-based discoverability works
- Performance under 60 seconds

---

### Phase 1.0: Production Ready (Weeks 5-6)

**Goal:** Complete implementation with all phases

**Deliverables:**
- Phase 5 implemented (commit + index rebuild)
- All validation types working
- Metrics collection
- Error handling

**Success Criteria:**
- End-to-end workflow functional
- 80% validation pass rate achieved
- Documentation complete

---

### Phase 2.0: Advanced Features (Future)

**Goal:** Enhance with full RAG testing and improvements

**Deliverables:**
- Temporary index for Phase 3
- Advanced semantic validation (NLP)
- Multi-agent peer review
- Automated threshold tuning

**Success Criteria:**
- 95% validation pass rate
- Full RAG testing operational
- System learns optimal thresholds

---

## Appendix: Implementation Checklist

### Prerequisites
- [ ] Workflow engine supports phase-gated execution
- [ ] RAG engine with search capability available
- [ ] Embedding function (local or OpenAI) configured
- [ ] Git integration for commits
- [ ] Index rebuild capability
- [ ] **Calibration dataset created** (10-15 existing standards with 5 test queries each)
- [ ] **Embedding threshold calibrated** (run calibrate_embedding_threshold())

### Phase 0-1: Foundation
- [ ] Structure validator implemented
- [ ] Required section detection (regex-based)
- [ ] Markdown validation
- [ ] Validation report generator

### Phase 2: RAG Optimization
- [ ] Keyword density analyzer
- [ ] Query hook counter
- [ ] Header quality checker
- [ ] Concrete thresholds configured

### Phase 3: Discoverability (MVP)
- [ ] **Calibration dataset created** (10-15 standards, 5 queries each)
- [ ] **Embedding threshold calibrated** (optimal threshold determined)
- [ ] Question generator (5 angles: how-to, when-to, problem, decision, tool)
- [ ] Embedding-based similarity test
- [ ] Multi-angle validation (all 5 angles tested)
- [ ] 80% threshold enforcement (4/5 queries found)

### Phase 4: Semantic Validation
- [ ] Chunk size analyzer (100-500 tokens)
- [ ] Parent header tracking during chunking (for context)
- [ ] Completeness heuristics with parent context (MVP)
- [ ] Link validator (internal files + DNS, no HTTP in v1.0)
- [ ] Link validation caching (@lru_cache)
- [ ] Duplication checker

### Phase 5: Integration
- [ ] Git commit integration
- [ ] Index rebuild trigger (synchronous)
- [ ] Immediate discoverability test
- [ ] Metrics collection
- [ ] Rollback capability

### Testing
- [ ] Unit tests for each validator
- [ ] Integration tests for workflow
- [ ] End-to-end test with sample standard
- [ ] Performance test (< 60s target)
- [ ] Error scenario tests

### Documentation
- [ ] Workflow usage guide
- [ ] Validation rules reference
- [ ] Troubleshooting guide
- [ ] Example standards (pass/fail)

---

## Summary

This specification provides a complete design for an automated standards creation workflow that:

1. **Validates systematically** through 6 phases with clear checkpoints
2. **Enforces quality** via programmatic validation (not subjective review)
3. **Provides concrete feedback** on what passed/failed and why
4. **Self-improves** as AI learns patterns over time
5. **Degrades gracefully** when dependencies (RAG) unavailable
6. **Measures progress** with 10 quantitative metrics

**Key Design Decisions:**

- **MVP approach for Phase 3:** Use embedding similarity first (with calibration), full RAG later
- **Concrete thresholds:** Replace subjective terms with measurable values
  - Keyword density: 0.5-2% (natural), 2-5% (high), >5% (stuffing)
  - Embedding similarity: Calibrated threshold (0.70-0.80 expected)
  - Chunk sizes: 100-500 tokens, 200-400 optimal
- **Link validation scope (v1.0):** Internal files + DNS checks (no HTTP requests)
- **Performance budget allocation:** 60s total with per-phase timeouts (5-15s each)
- **Semantic completeness:** Parent header tracking for context-aware validation
- **Graceful degradation:** Multiple fallback modes for robustness
- **Iterative implementation:** Start simple (structure), add complexity incrementally
- **Clear error handling:** Rollback capability, timeout limits, user warnings

**Implementation Priority:**

1. **Critical (Before Alpha):** Create calibration dataset and run threshold calibration
2. **Critical (Alpha):** Phase 0-1 with structure validation
3. **High (Beta):** Phase 2-3 MVP with embedding-based discoverability
4. **High (Beta):** Phase 4 semantic validation with link checking
5. **Medium (v1.0):** Phase 5 integration, performance optimizations, error handling
6. **Low (v2.0):** Advanced features (temporary indexing, NLP-based validation)

**Pre-Implementation Requirement:**
Before beginning Alpha implementation, **run calibration process** to establish optimal embedding similarity threshold. This grounds the MVP approach in real data and reduces risk of false negatives.

**This design is ready for implementation via `workflow_creation_v1` process.**

---

**Version:** 1.2 (Implementation-ready with concrete specifications)  
**Last Updated:** 2025-10-13  
**Status:** Ready for implementation via workflow_creation_v1  
**Next Step:** 
1. Create calibration dataset (10-15 existing standards, 5 queries each)
2. Run calibration process to establish embedding threshold
3. Execute workflow_creation_v1 to scaffold workflow structure

**Changelog v1.1 → v1.2:**
- Added explicit keyword density algorithm with concrete thresholds (0.5-5%)
- Added embedding similarity calibration process for Phase 3 MVP
- Defined link validation scope for v1.0 (internal files + DNS, no HTTP)
- Added per-phase timeout allocation (5-15s each, 60s total)
- Enhanced semantic completeness validation with parent header tracking
- Added calibration as prerequisite before Alpha implementation
