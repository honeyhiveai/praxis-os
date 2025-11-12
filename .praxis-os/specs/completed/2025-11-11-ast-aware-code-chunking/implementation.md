# Implementation Approach

**Project:** AST-Aware Code Chunking with Import Penalty  
**Date:** 2025-11-11

---

## 1. Implementation Philosophy

**Core Principles:**
1. **Config-Driven Design**: Language-specific logic in configuration, not code
2. **Infrastructure Reuse**: Leverage existing ASTExtractor and Tree-sitter infrastructure
3. **Graceful Degradation**: Fallback to line-based chunking on AST failures
4. **Measurable Success**: Validate with primary failure case (python-sdk query)
5. **Backward Compatibility**: Old configs and indexes continue to work

---

## 2. Implementation Order

Follow the phased approach defined in `tasks.md`:

1. **Phase 0** (8h): Config Extraction → Extract node types from ast.py to mcp.yaml
2. **Phase 1** (4h): Refactor AST Extractor → Make it config-driven
3. **Phase 2** (12h): Build Universal Chunker → Create UniversalASTChunker
4. **Phase 3** (6h): SemanticIndex Integration → Apply import penalty in search
5. **Phase 4** (6h): Migration & Validation → Validate python-sdk query fix
6. **Phase 5** (2h): Documentation → Update guides and inline docs

**Critical Path:** 38 hours (~5 days)

---

## 3. Code Patterns

### 3.1 Config-Driven AST Node Types

**Pattern:** Read language-specific node types from unified config instead of hardcoded if/elif chains.

**Good Example:**

```python
# In ast.py - Config-driven approach
def _get_significant_node_types(self, language: str) -> set:
    """Get significant AST node types for a language."""
    lang_config = self.lang_configs.get(language, {})
    if "significant_nodes" in lang_config:
        return set(lang_config["significant_nodes"])
    
    # Fallback for unconfigured languages
    logger.warning(f"No config for {language}, using defaults")
    return {"function_definition", "class_definition"}
```

**Anti-Pattern (Current Implementation):**

```python
# ❌ DON'T: Hardcoded if/elif chains (~60 lines)
def _get_significant_node_types(self, language: str) -> set:
    if language == "python":
        return {"function_definition", "async_function_definition", "class_definition", ...}
    elif language in ["javascript", "typescript", "tsx", "jsx"]:
        return {"function_declaration", "arrow_function", ...}
    elif language == "go":
        return {"function_declaration", "method_declaration", ...}
    # ... 10+ more languages
```

**Why:** Config-driven design enables adding languages without code changes, centralizes language definitions, and reduces code complexity.

---

### 3.2 AST-Aware Chunking

**Pattern:** Use Tree-sitter AST parsing to chunk at function/class boundaries.

**Good Example:**

```python
# In ast_chunker.py - UniversalASTChunker
def chunk_file(self, file_path: Path) -> List[CodeChunk]:
    """Chunk a code file at AST boundaries."""
    code = file_path.read_text(encoding="utf-8")
    
    # Parse with Tree-sitter
    tree = self.parser.parse(code.encode())
    root = tree.root_node
    
    chunks = []
    import_nodes = []
    
    # Traverse top-level nodes
    for node in root.children:
        if node.type in self.import_nodes:
            import_nodes.append(node)
        elif node.type in self.definition_nodes:
            chunk = self._chunk_definition(node, code, file_path)
            if chunk:
                chunks.append(chunk)
    
    # Group all imports into one chunk
    if import_nodes:
        import_chunk = self._chunk_imports(import_nodes, code, file_path)
        if import_chunk:
            chunks.insert(0, import_chunk)
    
    return chunks
```

**Anti-Pattern (Current Implementation):**

```python
# ❌ DON'T: Line-based chunking (arbitrary splits)
def _chunk_file(self, file_path: Path) -> List[Dict[str, Any]]:
    lines = content.split("\n")
    chunk_size = 200  # Lines, not tokens!
    overlap = 20
    
    for i in range(0, len(lines), chunk_size - overlap):
        chunk_lines = lines[i:i + chunk_size]
        # Function may be split mid-body! 🚨
```

**Why:** AST chunking respects code structure, preserves complete functions/classes, and creates semantically meaningful units.

---

### 3.3 Import Penalty Application

**Pattern:** Apply ranking penalty to import-heavy chunks.

**Good Example:**

```python
# In semantic.py - Apply penalty in search ranking
def hybrid_search(self, query: str, n_results: int = 5) -> List[SearchResult]:
    """Search with RRF fusion and import penalty."""
    # ... vector + FTS search ...
    
    # Apply RRF fusion
    for result in ranked_results:
        rrf_score = 1/(60 + result.vector_rank) + 1/(60 + result.fts_rank)
        
        # Apply import penalty if chunk is import-heavy
        if hasattr(result, 'import_penalty') and result.import_penalty < 1.0:
            rrf_score *= result.import_penalty  # Reduce score by penalty
            logger.debug(f"Applied penalty {result.import_penalty} to {result.file_path}")
        
        result.final_score = rrf_score
    
    # Sort by final score (descending)
    ranked_results.sort(key=lambda r: r.final_score, reverse=True)
    return ranked_results[:n_results]
```

**Anti-Pattern:**

```python
# ❌ DON'T: Ignore import_ratio metadata
def hybrid_search(self, query: str, n_results: int = 5) -> List[SearchResult]:
    # ... RRF fusion ...
    # No penalty applied - imports rank equally with implementations! 🚨
    return ranked_results[:n_results]
```

**Why:** Import penalty demotes import-heavy chunks, ensuring implementations rank above import declarations.

---

### 3.4 Efficient Tree Traversal

**Pattern:** Use `walk()` for efficient AST traversal (O(n) vs O(n²)).

**Good Example:**

```python
# ✅ DO: Use walk() for tree traversal
def traverse_ast(root_node):
    """Efficient tree traversal using TreeCursor."""
    cursor = root_node.walk()
    
    reached_root = False
    while not reached_root:
        node = cursor.node
        process(node)
        
        # Try to go to first child
        if cursor.goto_first_child():
            continue
        
        # Try to go to next sibling
        if cursor.goto_next_sibling():
            continue
        
        # Go back up
        reached_root = not cursor.goto_parent()
```

**Anti-Pattern:**

```python
# ❌ DON'T: Recursive iteration over .children (O(n²))
def traverse_ast_bad(node):
    for child in node.children:  # Each access is O(log n)!
        process(child)
        traverse_ast_bad(child)  # Recursive calls compound cost
```

**Why:** `walk()` uses an internal cursor for O(n) traversal, while repeated `.children` access is O(n²) for deep trees.

---

### 3.5 Graceful Fallback

**Pattern:** Wrap AST chunking in try/except with fallback to line-based.

**Good Example:**

```python
# In semantic.py - Graceful fallback
def _chunk_file(self, file_path: Path) -> List[Dict[str, Any]]:
    """Chunk file with AST (fallback to line-based on error)."""
    language = self._detect_language(file_path)
    
    # Try AST chunking first
    if language and language in self.config.get("language_configs", {}):
        try:
            from ouroboros.subsystems.rag.code.ast_chunker import UniversalASTChunker
            chunker = UniversalASTChunker(language, self.config, self.base_path)
            ast_chunks = chunker.chunk_file(file_path)
            return [chunk.to_dict() for chunk in ast_chunks]
        except Exception as e:
            logger.warning(f"AST chunking failed for {file_path}: {e}, falling back to line-based")
            self.fallback_counter += 1  # Track for health metrics
    
    # Fallback: line-based chunking
    return self._chunk_file_line_based(file_path)
```

**Anti-Pattern:**

```python
# ❌ DON'T: Let AST failures crash index build
def _chunk_file(self, file_path: Path) -> List[Dict[str, Any]]:
    chunker = UniversalASTChunker(language, self.config, self.base_path)
    return chunker.chunk_file(file_path)  # Crashes if parse fails! 🚨
```

**Why:** Graceful fallback ensures index builds complete successfully even if some files fail AST parsing.

---

### 3.6 Configuration Schema

**Pattern:** Define language configs in mcp.yaml with validation.

**Good Example:**

```yaml
# In .praxis-os/config/mcp.yaml
indexes:
  code:
    source_paths: ["ouroboros/"]
    languages: ["python", "typescript", "go"]
    chunking_strategy: "ast"  # "ast" or "line"
    
    vector:
      model: "microsoft/codebert-base"
      chunk_size: 500  # Target tokens per chunk
      chunk_overlap: 50
    
    fts:
      enabled: true
    
    # Language-specific node type mappings
    language_configs:
      python:
        significant_nodes:
          - function_definition
          - async_function_definition
          - class_definition
          - decorated_definition
        
        symbol_nodes:
          - function_definition
          - async_function_definition
          - class_definition
        
        call_nodes:
          - call
          - attribute  # For method calls
        
        chunking:
          import_nodes:
            - import_statement
            - import_from_statement
          definition_nodes:
            - function_definition
            - async_function_definition
            - class_definition
            - decorated_definition
          split_boundary_nodes:
            - if_statement
            - for_statement
            - while_statement
            - try_statement
            - with_statement
          import_penalty: 0.3  # Reduce import chunk scores by 70%
          enabled: true
      
      typescript:
        # ... similar structure for TypeScript ...
      
      go:
        # ... similar structure for Go ...
```

**Why:** Unified config centralizes language definitions, enables validation, and allows language support without code changes.

---

### 3.7 CodeChunk Data Model

**Pattern:** Use dataclass for type-safe chunk representation.

**Good Example:**

```python
# In ast_chunker.py
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class CodeChunk:
    """Semantic code chunk (function, class, or imports)."""
    content: str
    file_path: Path
    start_line: int
    end_line: int
    chunk_type: str  # "function", "class", "import", "module"
    symbols: List[str]  # Function/class names in chunk
    import_ratio: float  # 0.0-1.0 (percentage of import lines)
    import_penalty: float  # 0.3-1.0 (ranking multiplier)
    token_count: int
    
    def to_dict(self) -> dict:
        """Convert to dict for LanceDB storage."""
        return {
            "content": self.content,
            "file_path": str(self.file_path),
            "start_line": self.start_line,
            "end_line": self.end_line,
            "chunk_type": self.chunk_type,
            "symbols": self.symbols,
            "import_ratio": self.import_ratio,
            "import_penalty": self.import_penalty,
            "token_count": self.token_count,
        }
```

**Why:** Type-safe data model prevents errors, documents structure, and provides serialization.

---

### 3.8 Import Ratio Calculation

**Pattern:** Calculate import ratio for penalty application.

**Good Example:**

```python
# In ast_chunker.py
def _calculate_import_ratio(self, content: str) -> float:
    """Calculate what percentage of lines are imports."""
    lines = content.split('\n')
    if not lines:
        return 0.0
    
    import_lines = sum(1 for line in lines if self._is_import_line(line))
    return import_lines / len(lines)

def _is_import_line(self, line: str) -> bool:
    """Detect if a line is an import statement (language-agnostic)."""
    stripped = line.strip()
    return (
        stripped.startswith('import ') or
        stripped.startswith('from ') or
        stripped.startswith('use ') or  # Rust
        stripped.startswith('#include') or  # C/C++
        stripped.startswith('require(')  # JavaScript
    )

def _calculate_penalty(self, import_ratio: float) -> float:
    """Calculate ranking penalty based on import ratio."""
    if import_ratio > 0.5:
        return self.import_penalty  # Default: 0.3
    return 1.0  # No penalty
```

**Why:** Import ratio enables targeted penalty application only to import-heavy chunks.

---

## 4. Testing Strategy

**Comprehensive testing documentation:** See `testing/` subdirectory

### 4.1 Test Coverage

**Test Levels:**
- **Unit Tests** (Phase 2, Task 2.8): 30+ tests for `UniversalASTChunker`, >85% coverage
- **Integration Tests** (Phase 3, Task 3.5): AST end-to-end, import penalty, fallback
- **E2E Tests** (Phase 4, Task 4.1-4.3): Index rebuild, comparison suite, python-sdk validation
- **Performance Tests** (Phase 4, Task 4.4): Query latency, index build time, penalty overhead
- **Relevance Tests** (Phase 4, Task 4.5): Human evaluation (100 queries, Relevance@5 >90%)

### 4.2 Test Execution

```bash
# Unit tests
pytest tests/test_ast_chunker.py -v --cov

# Integration tests
pytest tests/test_semantic_index_ast_integration.py -v

# E2E validation (PRIMARY TEST)
python scripts/validate_ast_chunking.py --run-all

# Performance profiling
python scripts/profile_ast_chunking.py --queries=100

# Relevance evaluation
python scripts/evaluate_relevance.py --queries=relevance_test_set.json
```

### 4.3 Acceptance Criteria

**Phase 4 Gate (CRITICAL):**
- ✅ python-sdk query validation PASSED (implementation #1-2, imports #5+)
- ✅ p95 query latency <200ms
- ✅ Relevance@5 >90%
- ✅ False Positive Rate <15%

**Release Criteria:**
- All functional tests pass (10/10)
- All non-functional tests pass (15/15)
- Performance targets met
- Zero critical bugs

**Detailed test plans:** See `testing/functional-tests.md`, `testing/nonfunctional-tests.md`, `testing/test-strategy.md`

---

## 5. Deployment Guidance

### 5.1 Pre-Deployment Checklist

- [ ] All Phase 4 acceptance criteria met
- [ ] python-sdk query validation PASSED
- [ ] Performance targets met (p95 <200ms)
- [ ] Relevance metrics validated (Relevance@5 >90%)
- [ ] Documentation complete
- [ ] Rollback procedure tested

### 5.2 Gradual Rollout

**Week 1: Dogfooding (praxis-os)**
```yaml
# In .praxis-os/config/mcp.yaml
indexes:
  code:
    chunking_strategy: "ast"  # Enable for praxis-os
```

```bash
# Rebuild index
rm -rf .praxis-os/.cache/indexes/code
mcp-server restart
```

**Validation:**
- Run 20 test queries
- Monitor query latency (Prometheus)
- Check health status daily
- Collect user feedback

**Week 2: python-sdk Validation**
```yaml
# In python-sdk config
indexes:
  code:
    chunking_strategy: "ast"
```

**Validation (CRITICAL):**
- Run primary test query: "EventsAPI list_events multiple filters array implementation"
- Verify implementation ranks #1-2
- Verify imports rank #5+
- Monitor for 1 week

**Week 3: Default for New Installs**
- Set `chunking_strategy: "ast"` as default in template config
- Existing installs remain on line-based (opt-in upgrade)

**Week 4: Remove Line-Based Fallback** (Optional)
- If AST quality validated across all use cases
- Keep line-based as fallback for unsupported languages

### 5.3 Index Rebuild Process

**Step 1: Backup Existing Index**
```bash
cp -r .praxis-os/.cache/indexes/code .praxis-os/.cache/indexes/code.backup
```

**Step 2: Delete Current Index**
```bash
rm -rf .praxis-os/.cache/indexes/code
```

**Step 3: Restart MCP Server**
```bash
mcp-server restart
```
- Automatic rebuild triggered
- Monitor logs for progress
- **Time:** 1-2 minutes for 100K LOC

**Step 4: Validate Rebuild**
```bash
# Query for sample chunk
pos_search_project(action="search_code", query="sample function")

# Verify chunk_type metadata present
# Expected: chunk_type="function" or "class" or "import"
```

### 5.4 Rollback Procedure

**If AST Chunking Degrades Quality:**

**1. Detect Degradation:**
- Relevance@5 < 70% (critical)
- Latency p95 > 300ms (high)
- User reports "wrong results" (high)
- Fallback rate > 25% (medium)

**2. Immediate Action: Set Config**
```yaml
# In mcp.yaml
indexes:
  code:
    chunking_strategy: "line"  # Revert to line-based
```

**3. Rebuild Index:**
```bash
# Preserve AST index for debugging
mv .praxis-os/.cache/indexes/code .praxis-os/.cache/indexes/code.ast-backup

# Rebuild with line-based
mcp-server restart
```

**Recovery Time:** < 5 minutes

**4. Preserve Diagnostics:**
- Save AST index backup
- Export search logs
- Document regression queries
- Capture user feedback

**5. Per-Language Rollback (Optional):**
```yaml
# Disable AST for one language only
language_configs:
  python:
    chunking:
      enabled: true  # Python works
  
  typescript:
    chunking:
      enabled: false  # TypeScript broken, use line-based
```

---

## 6. Troubleshooting

### 6.1 Common Issues

#### Issue 1: Import Files Still Ranking High

**Symptoms:**
- Import files (`__init__.py`) rank in top-3
- Implementations rank below #5

**Diagnosis:**
```bash
# Check if import penalty applied
pos_search_project(action="search_code", query="sample")
# Look for import_penalty field in results
```

**Solutions:**
1. Verify import penalty in config: `import_penalty: 0.3`
2. Check import ratio calculation: Should be >0.5 for pure imports
3. Adjust penalty: Try `import_penalty: 0.2` (more aggressive)

---

#### Issue 2: Functions Split Mid-Body

**Symptoms:**
- Chunk contains partial function (no start or no end)
- `chunk_type` inconsistent

**Diagnosis:**
```bash
# Check chunk boundaries
# Review chunk start_line and end_line against source file
```

**Solutions:**
1. Verify language config has correct `definition_nodes`
2. Check Tree-sitter parser version
3. Verify file parses without errors

---

#### Issue 3: High Fallback Rate

**Symptoms:**
- Health check shows >25% fallback rate
- Many "AST parsing failed" warnings

**Diagnosis:**
```bash
# Check logs for parse errors
grep "AST parsing failed" .praxis-os/logs/mcp-server.log

# Check language configs
cat .praxis-os/config/mcp.yaml | grep -A 20 "language_configs"
```

**Solutions:**
1. Verify node types match Tree-sitter grammar
2. Check for corrupted source files
3. Update Tree-sitter parser version
4. Add missing language config

---

#### Issue 4: Slow Index Rebuild

**Symptoms:**
- Rebuild exceeds 10 minutes for 100K LOC
- Server appears unresponsive

**Diagnosis:**
```bash
# Check rebuild progress in logs
tail -f .praxis-os/logs/mcp-server.log

# Monitor system resources (CPU, memory)
top -pid $(pgrep -f mcp-server)
```

**Solutions:**
1. Verify parallel processing enabled
2. Check for large files (>1MB) causing slowdowns
3. Increase system resources
4. Temporarily disable AST for problematic files

---

#### Issue 5: Performance Regression (Latency >200ms)

**Symptoms:**
- p95 query latency exceeds 200ms
- User reports "search is slow"

**Diagnosis:**
```bash
# Profile search ranking
python scripts/profile_ast_chunking.py --queries=100

# Check import penalty overhead
# Expected: <1ms
```

**Solutions:**
1. Verify import penalty overhead <1ms
2. Check chunk count (too many small chunks?)
3. Optimize RRF fusion stage
4. Rollback to line-based if persistent

---

### 6.2 Debugging Tools

**1. Health Check:**
```python
pos_search_project(action="health_check")
# Shows: operational/degraded/fallback status
# Metrics: chunk count, token size, fallback rate
```

**2. Query Logging:**
```python
# Enable debug logging
import logging
logging.getLogger("ouroboros.subsystems.rag").setLevel(logging.DEBUG)
```

**3. Chunk Inspection:**
```bash
# Query for specific file
pos_search_project(action="search_code", query="filename:events.py")

# Inspect chunk metadata
# Check: chunk_type, import_ratio, import_penalty
```

---

### 6.3 Getting Help

**Internal Resources:**
- Design Document: `.praxis-os/workspace/design/2025-11-10-ast-aware-code-chunking-import-penalty.md`
- Specs: `.praxis-os/specs/review/2025-11-11-ast-aware-code-chunking/`
- Test Plans: `.praxis-os/specs/review/2025-11-11-ast-aware-code-chunking/testing/`

**External Resources:**
- Tree-sitter Documentation: https://tree-sitter.github.io/
- CodeBERT Model: https://huggingface.co/microsoft/codebert-base
- py-tree-sitter API: https://github.com/tree-sitter/py-tree-sitter

**Support Channels:**
- GitHub Issues: Report bugs with reproduction steps
- Slack: #code-intelligence channel
- Documentation: Request clarifications or examples

---


