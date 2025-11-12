# Supporting Documents Index

**Spec:** AST-Aware Code Chunking with Import Penalty  
**Created:** 2025-11-11  
**Total Documents:** 1

## Document Catalog

### 1. AST-Aware Code Chunking with Import Penalty (Design Document)

**File:** `2025-11-10-ast-aware-code-chunking-import-penalty.md`  
**Type:** Technical Design Document  
**Date:** 2025-11-10  
**Size:** 54K  
**Purpose:** Comprehensive design for improving code semantic search quality by implementing AST-aware chunking at function/class boundaries instead of arbitrary line-based chunking, with ranking penalties for import-heavy chunks.

**Relevance:** Requirements [H], Design [H], Implementation [H]

**Key Topics:**
- Problem: Import files (`__init__.py`) rank higher than implementations in semantic search
- Root Cause: Simple line-based chunking (200 lines) treats imports same as implementation code
- Solution: Tree-sitter AST parsing to chunk at function/class boundaries
- Import Penalty: Ranking penalty mechanism for import-heavy chunks
- Configuration-Driven: Language-agnostic design using unified `mcp.yaml` config
- Reuse: Leverage existing `ast.py` infrastructure and node type mappings
- Alignment: Integration with Cascading Health Check Architecture
- Multi-Repo: Impact on multi-repo indexing and partitioning strategy
- Performance: Target 500-token chunks (per spec) vs current 200-line chunks

**Key Sections:**
1. Problem Statement (Real failure case from python-sdk)
2. Current State (Implementation analysis)
3. Root Cause Analysis (Line-based chunking issues)
4. Proposed Solution (AST-aware chunking + import penalty)
5. Design Details (AST traversal, chunking algorithm, penalty mechanism)
6. Implementation Plan (4 phases)
7. Performance Analysis (Overhead calculations)
8. Migration Strategy (Backward compatibility, reindex process)
9. Success Metrics (Relevance, precision, quality metrics)
10. Risks and Mitigations (7 risks identified)

---

## Cross-Document Analysis

**Common Themes:**
- **Code Intelligence Quality:** First negative feedback on semantic search quality across all praxis OS usage
- **Configuration-Driven Design:** Leverage unified `mcp.yaml` for language-agnostic implementation
- **Infrastructure Reuse:** Existing `ast.py` Tree-sitter infrastructure and node type mappings
- **Scalability:** Support multiple languages via config, not code changes
- **Health Monitoring:** Integration with Cascading Health Check Architecture for graceful degradation

**Potential Conflicts:**
- None identified (single authoritative design document)

**Coverage Gaps:**
- **Testing Strategy:** Document describes what to test (relevance, precision) but not detailed test implementation
- **User Feedback Loop:** How to collect ongoing feedback on search quality improvements
- **Metrics Dashboard:** Mechanism for monitoring search quality metrics in production
- **Edge Cases:** Handling of non-standard file structures (e.g., generated code, vendored dependencies)

---

## Design Maturity Assessment

**Strengths:**
- ✅ Comprehensive problem analysis with real failure case
- ✅ Clear root cause identification
- ✅ Leverages existing infrastructure (ast.py, Tree-sitter, mcp.yaml)
- ✅ Configuration-driven for scalability
- ✅ Integration with Cascading Health Check Architecture
- ✅ Performance analysis with concrete overhead estimates
- ✅ Migration strategy with rollback procedure
- ✅ 7 risks identified with mitigation strategies

**Areas for Spec Elaboration:**
- **Testing:** Detailed test plan for relevance/precision validation
- **Monitoring:** Production metrics collection and alerting
- **Documentation:** User-facing docs for import penalty feature
- **Examples:** More real-world query/ranking examples
- **Validation:** Acceptance criteria for "success" (quantitative thresholds)

---

## Next Steps

This index will be used in Task 3 to systematically extract insights from the design document. The extracted insights will be organized by:
- **Requirements Insights:** User needs (search quality), business goals (multi-repo support), functional requirements (AST chunking, import penalty)
- **Design Insights:** Architecture (config-driven, Tree-sitter AST), patterns (chunk algorithm, penalty calculation), component designs (SemanticIndex, mcp.yaml)
- **Implementation Insights:** Code patterns (AST traversal), testing strategies (relevance metrics), deployment guidance (reindex process, rollback)

**Key Extraction Priorities:**
1. **User Story:** Extract the real failure case as primary user story
2. **Functional Requirements:** AST-aware chunking, import penalty, config-driven languages
3. **Non-Functional Requirements:** Performance targets, backward compatibility, graceful degradation
4. **Technical Constraints:** CodeBERT token limits (514), Tree-sitter API usage patterns
5. **Success Metrics:** Relevance ranking, precision improvements, query performance
6. **Risks:** 7 identified risks and their mitigation strategies

---

## Extracted Insights

### Requirements Insights (Phase 1)

#### From AST-Aware Code Chunking Design Document:

**User Story: Real Failure Case**
- **Context:** python-sdk project, first negative feedback on semantic search quality across all praxis OS usage
- **Query:** `pos_search_project(action="search_code", query="EventsAPI list_events multiple filters array implementation")`
- **Problem:** Import file (`api/__init__.py`) ranked #1, actual implementation (`api/events.py`) buried at #4
- **User Feedback:** "Too much noise, 40KB of results, right code buried at #4"
- **Significance:** Critical to fix before hive-kube monorepo deployment

**Functional Requirements:**
1. **AST-Aware Chunking:** Chunk code at function/class boundaries using Tree-sitter AST parsing
2. **Import Penalty:** Apply ranking penalties to import-heavy chunks (0.3 multiplier)
3. **Configuration-Driven:** Support multiple languages via `mcp.yaml` config (no code changes per language)
4. **Chunking Target:** 500 tokens per chunk (CodeBERT limit: 514 tokens) with 50-token overlap
5. **Graceful Fallback:** Line-based chunking as fallback for unsupported languages
6. **Reindex Capability:** Ability to rebuild code index with new chunking strategy

**Business Goals:**
- Improve semantic search relevance (Relevance@5: 60% → 90%)
- Rank implementations above imports (#4 avg → #1-2 avg)
- Maintain search latency (<200ms p95)
- Enable multi-repo support (hive-kube monorepo readiness)

**User Needs:**
- Find implementation code, not import declarations
- Relevant results in top 5 (not buried)
- Fast search response (<200ms)
- Accurate code discovery across multiple repositories

**Constraints:**
- CodeBERT token limit: 514 tokens (spec target: 500 tokens/chunk)
- Backward compatibility with existing indexes
- Must work offline (local embeddings)
- Performance: AST parsing 2-3x slower than line-based (acceptable for index-time overhead)

**Out of Scope:**
- Real-time re-indexing (index rebuild is manual/scheduled)
- Per-file chunking strategies (global config only)
- Custom ranking algorithms beyond import penalty
- Cross-language AST comparisons

---

### Design Insights (Phase 2)

#### From AST-Aware Code Chunking Design Document:

**Architecture:**
- **Config-Driven Design:** Unified `mcp.yaml` config for language-specific AST node types
- **Infrastructure Reuse:** Leverage existing `ast.py` Tree-sitter infrastructure and node type mappings
- **Single Source of Truth:** Same config used for both AST extraction (symbols/relationships) AND chunking
- **Graceful Degradation:** Integration with Cascading Health Check Architecture (AST failure → fallback to line-based)

**Components:**

1. **UniversalASTChunker** (NEW)
   - Language-agnostic AST chunker reading from mcp.yaml config
   - Chunks at function/class boundaries
   - Calculates import ratio and penalty
   - Target: 500 tokens per chunk

2. **Refactored ASTExtractor** (MODIFIED)
   - Remove ~60 lines of if/elif chains
   - Add ~15 lines of config reading
   - Read node types from `language_configs` in mcp.yaml
   - Shared parser infrastructure with chunker

3. **mcp.yaml Extensions** (CONFIG)
   - `language_configs` section with per-language node types
   - `chunking` subsection with import_nodes, definition_nodes, split_boundary_nodes
   - `import_penalty` parameter (default: 0.3)
   - `chunking_strategy` feature flag ("ast" or "line")

**Data Models:**

```python
@dataclass
class CodeChunk:
    content: str
    file_path: Path
    start_line: int
    end_line: int
    chunk_type: str  # "function", "class", "import", "module"
    symbols: List[str]  # Function/class names
    import_ratio: float  # 0.0-1.0
    import_penalty: float  # 0.3-1.0 (ranking multiplier)
    token_count: int
```

**AST Chunking Algorithm:**
1. Parse file with Tree-sitter
2. Traverse AST, detect definition_nodes (functions, classes)
3. Group imports into single chunk
4. Split large functions at split_boundary_nodes if needed
5. Calculate import ratio per chunk
6. Apply import penalty to score

**Import Penalty Mechanism:**
```python
import_ratio = import_lines / total_lines
if import_ratio > 0.5:
    penalty = lang_config.get("import_penalty", 0.3)  # Reduce score by 70%
    final_score = base_score * penalty
```

**Integration Points:**
- **SemanticIndex** (`semantic.py`): Replace `_chunk_file()` to use `UniversalASTChunker`
- **Search Ranking**: Apply import penalty in RRF fusion step
- **Health Checks**: AST component reports health, fallback to line-based on failure
- **Multi-Repo**: AST chunking applies across all partitions (primary, instrumentors)

**API/Interfaces:**
- `UniversalASTChunker.chunk_file(file_path) -> List[CodeChunk]`
- Config schema in mcp.yaml (language_configs, chunking section)
- Backward compatible: line-based fallback if AST fails

**Security:**
- No new security concerns (same Tree-sitter parsing as existing AST extraction)
- Config validation to prevent malformed node type lists
- Sandbox Tree-sitter parsing (prevent infinite loops)

**Performance Targets:**
- Chunking: 300-500 files/second (2-3x slower than line-based acceptable)
- Search latency: <200ms p95 (no regression)
- Import penalty application: <1ms overhead

---

### Implementation Insights (Phase 4)

#### From AST-Aware Code Chunking Design Document:

**Code Patterns:**

1. **Config-Driven Node Types** (ast.py refactor)
```python
def _get_significant_node_types(self, language: str) -> set:
    lang_config = self.lang_configs.get(language, {})
    if "significant_nodes" in lang_config:
        return set(lang_config["significant_nodes"])
    # Fallback for unconfigured languages
    return {"function_definition", "class_definition"}
```

2. **AST Traversal with Tree-sitter** (ast_chunker.py)
```python
# Use walk() for O(n) efficiency, not recursive iteration O(n²)
cursor = root_node.walk()
while cursor.goto_first_child() or cursor.goto_next_sibling():
    if cursor.node.type in self.definition_nodes:
        # Chunk function/class
```

3. **Import Penalty Application** (semantic.py)
```python
# In search ranking (RRF fusion step)
for result in search_results:
    if result.chunk_type == "import" and result.import_ratio > 0.5:
        result.score *= result.import_penalty  # Reduce by 70%
```

**Testing Strategies:**

1. **Unit Tests** (AST chunker)
   - Parse real files (Python, TypeScript, Go)
   - Verify function boundaries detected
   - Verify imports grouped
   - Verify token counts (500 ±20%)
   - Test import ratio calculation

2. **Integration Tests** (SemanticIndex)
   - Build index with AST chunking
   - Run python-sdk failure query
   - Verify implementations rank #1-2
   - Verify imports rank #5+
   - Measure search latency (<200ms)

3. **Comparison Tests** (AST vs Line-based)
   - Side-by-side index builds
   - Same query set
   - Compare ranking quality
   - Measure Relevance@5 improvement (60% → 90% target)

4. **Relevance Metrics** (Human evaluation)
   - Sample 100 queries
   - Human judges rate top-5 results (relevant/irrelevant)
   - Calculate Relevance@5, False Positive Rate
   - Target: Relevance@5 > 90%, FPR < 15%

**Deployment Guidance:**

1. **Gradual Rollout** (4-week plan)
   - Week 1: Enable AST for praxis-os (dogfood)
   - Week 2: Enable for python-sdk (validate fix)
   - Week 3: Default for new installs
   - Week 4: Remove line-based fallback

2. **Index Rebuild Process**
```bash
# Delete old index
rm -rf .praxis-os/.cache/indexes/code

# Rebuild with AST chunking (automatic on restart)
mcp-server restart
```
**Time:** 1-2 minutes for 100K LOC

3. **Rollback Procedure** (if quality degrades)
   - **Detect:** Relevance@5 < 70%, latency p95 > 300ms, user reports
   - **Action:** Set `chunking_strategy: "line"` in mcp.yaml
   - **Rebuild:** Move index to backup, restart server
   - **Recovery time:** < 5 minutes

4. **Language-Specific Rollback** (per-language enable/disable)
```yaml
language_configs:
  python:
    chunking:
      enabled: true  # Python works
  typescript:
    chunking:
      enabled: false  # TypeScript broken, use line-based
```

**Monitoring:**
- Query latency (p50, p95, p99)
- Relevance@5 metric (human eval)
- False positive rate (irrelevant in top-5)
- Import rank position (should be #5+)
- Index build time (track AST parsing overhead)

**Success Criteria:**
| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Relevance@5 | 60% | 90% | Human eval |
| Implementation Rank | #4 avg | #1-2 avg | Position tracking |
| Import Rank | #1-3 | #5+ | Position tracking |
| Search Latency (p95) | <200ms | <200ms | Prometheus |
| False Positive Rate | 40% | <15% | Top-5 irrelevant |

---

### Cross-References

**Validated by Multiple Sources:**
- Single authoritative source (design document)

**Conflicts:**
- None identified

**High-Priority Items:**
1. **Fix python-sdk failure case:** Validate query ranks implementations #1-2 (PRIMARY USER STORY)
2. **Configuration-driven languages:** Enable adding new languages via config only
3. **Graceful fallback:** Line-based chunking for unsupported languages
4. **Performance validation:** Search latency < 200ms p95 (no regression)
5. **Rollback procedure:** < 5 minute recovery time if quality degrades

---

## Insight Summary

**Total:** 87 insights  
**By Category:** Requirements [25], Design [42], Implementation [20]  
**Multi-source validated:** 0 (single document)  
**Conflicts to resolve:** 0  
**High-priority items:** 5

**Phase 0 Complete:** ✅ 2025-11-11

