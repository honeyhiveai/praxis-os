# Functional Test Plan

**Project:** AST-Aware Code Chunking with Import Penalty  
**Date:** 2025-11-11  
**Purpose:** Detailed test cases for all functional requirements

---

## Test Case FT-001: AST-Aware Code Chunking

**Requirement:** FR-001  
**Priority:** Critical  
**Objective:** Verify code is chunked at AST boundaries (function/class definitions)

**Preconditions:**
- Python, TypeScript, Go language configs populated in mcp.yaml
- UniversalASTChunker implemented
- Test fixtures created with sample functions/classes

**Test Steps:**
1. Create test file with 3 functions: `func_a()`, `func_b()`, `func_c()`
2. Call `UniversalASTChunker.chunk_file(test_file)`
3. Verify chunk count = 3 (one per function)
4. For each chunk, verify `start_line` and `end_line` align with function boundaries
5. Verify no chunk contains partial function (mid-body split)
6. Repeat for TypeScript and Go test files

**Expected Results:**
- ✅ Each function is a complete chunk (no splits)
- ✅ Chunk boundaries align with AST nodes (function_definition)
- ✅ Chunks have metadata: `chunk_type="function"`, `symbols=[function_name]`
- ✅ Works consistently across Python, TypeScript, Go

**Failure Criteria:**
- ❌ Function split mid-body
- ❌ Multiple functions in single chunk (when both fit in token limit)
- ❌ Chunk boundaries don't align with AST node start/end

---

## Test Case FT-002: Import Penalty Mechanism

**Requirement:** FR-002  
**Priority:** Critical  
**Objective:** Verify import penalty reduces ranking for import-heavy chunks

**Preconditions:**
- Code index built with AST chunking
- Test fixture with import file and implementation file
- SemanticIndex integrated with penalty application

**Test Steps:**
1. Create import file: `api/__init__.py` (100% imports, `import_ratio=1.0`)
2. Create implementation file: `api/events.py` (0% imports, `import_ratio=0.0`)
3. Build index with both files
4. Query: "EventsAPI list_events filters implementation"
5. Check ranking:
   - Import chunk penalty = 0.3
   - Implementation chunk penalty = 1.0
6. Verify implementation ranks above import

**Expected Results:**
- ✅ Import chunk has `import_ratio=1.0`, `import_penalty=0.3`
- ✅ Implementation chunk has `import_ratio=0.0`, `import_penalty=1.0`
- ✅ Implementation file ranks #1-2
- ✅ Import file ranks #5 or lower

**Failure Criteria:**
- ❌ Import file ranks above implementation
- ❌ Import penalty not applied (penalty = 1.0 for imports)
- ❌ Penalty not multiplied into final score

---

## Test Case FT-003: Token-Based Chunk Sizing

**Requirement:** FR-003  
**Priority:** Critical  
**Objective:** Verify chunks target ~500 tokens (±20%)

**Preconditions:**
- Token estimation implemented (~4 chars = 1 token)
- Test fixtures with functions of varying sizes

**Test Steps:**
1. Create small function (~200 tokens)
2. Create medium function (~500 tokens)
3. Create large function (~800 tokens)
4. Chunk all functions
5. Verify token counts:
   - Small: 200 tokens (within range)
   - Medium: 500 tokens (target)
   - Large: 800 tokens (logged warning, kept intact)
6. Verify no chunk exceeds 514 tokens (CodeBERT limit)

**Expected Results:**
- ✅ Average chunk size: 400-600 tokens (500 ±20%)
- ✅ No chunk >514 tokens
- ✅ Large functions kept intact (logged as warning)
- ✅ Token count metadata stored per chunk

**Failure Criteria:**
- ❌ Chunks consistently outside 400-600 range
- ❌ Chunk exceeds 514 tokens
- ❌ Large function split arbitrarily (not at split_boundary_nodes)

---

## Test Case FT-004: Configuration-Driven Language Support

**Requirement:** FR-004  
**Priority:** High  
**Objective:** Verify languages supported via config only (no code changes)

**Preconditions:**
- Python config exists in mcp.yaml
- Test procedure for adding new language (e.g., Rust)

**Test Steps:**
1. Verify Python, TypeScript, Go configs in mcp.yaml
2. Add Rust config (copy template, adjust node types)
3. Restart server (no code changes)
4. Create Rust test file with functions
5. Chunk Rust file
6. Verify AST chunking works for Rust

**Expected Results:**
- ✅ Python, TypeScript, Go configs present at launch
- ✅ Rust added via config only (<1 hour)
- ✅ AST chunking works for Rust immediately
- ✅ Config validation catches invalid node types

**Failure Criteria:**
- ❌ Code changes required to add Rust
- ❌ Invalid config not caught on startup
- ❌ Rust chunking fails due to hardcoded language checks

---

## Test Case FT-005: Graceful Fallback to Line-Based Chunking

**Requirement:** FR-005  
**Priority:** High  
**Objective:** Verify fallback to line-based on parse failures or unsupported languages

**Preconditions:**
- Unsupported language file (e.g., Ruby)
- Corrupted file causing parse error

**Test Steps:**
1. Index Ruby file (unsupported language)
2. Verify fallback to line-based chunking
3. Verify warning logged: "No config for ruby, using line-based"
4. Index corrupted Python file (parse error)
5. Verify fallback to line-based chunking
6. Verify error logged: "AST parsing failed for [file], falling back"
7. Verify index build completes (no crash)

**Expected Results:**
- ✅ Unsupported languages use line-based fallback
- ✅ Parse errors trigger fallback (don't crash)
- ✅ Fallback uses 200-line chunks, 20-line overlap
- ✅ Health check reports degraded status
- ✅ Fallback count tracked in metrics

**Failure Criteria:**
- ❌ Index build crashes on parse error
- ❌ Unsupported language causes error (should fallback gracefully)
- ❌ Fallback not logged or tracked

---

## Test Case FT-006: Index Rebuild Capability

**Requirement:** FR-006  
**Priority:** High  
**Objective:** Verify index rebuild with AST chunking completes in <10 minutes for 100K LOC

**Preconditions:**
- Test repository with 100K LOC (Python, TypeScript, Go)
- AST chunking enabled in mcp.yaml

**Test Steps:**
1. Backup existing index
2. Delete index: `rm -rf .praxis-os/.cache/indexes/code`
3. Restart server (triggers rebuild)
4. Monitor rebuild progress (logs every 10%)
5. Measure rebuild time
6. Verify chunk quality: token counts, import ratios, AST boundaries

**Expected Results:**
- ✅ Rebuild completes in <10 minutes for 100K LOC
- ✅ Progress logged every 10%
- ✅ All source files indexed
- ✅ Sample query returns chunks with `chunk_type` metadata
- ✅ Chunk statistics logged (count, avg token size)

**Failure Criteria:**
- ❌ Rebuild exceeds 10 minutes
- ❌ Rebuild fails or crashes
- ❌ Chunks missing `chunk_type` metadata

---

## Test Case FT-007: Configuration-Based Rollback

**Requirement:** FR-007  
**Priority:** High  
**Objective:** Verify rollback to line-based in <5 minutes

**Preconditions:**
- Index built with AST chunking
- mcp.yaml accessible for editing

**Test Steps:**
1. Set `chunking_strategy: "line"` in mcp.yaml
2. Restart server
3. Measure rollback time (detect config change → rebuild complete)
4. Verify old index backed up: `.cache/indexes/code.ast-backup` exists
5. Query for known implementation
6. Verify chunks use line-based (no `chunk_type` metadata)

**Expected Results:**
- ✅ Rollback completes in <5 minutes
- ✅ Old index preserved as backup
- ✅ New index uses line-based chunking
- ✅ Search functionality works with line-based chunks
- ✅ Rollback logged with timestamp

**Failure Criteria:**
- ❌ Rollback exceeds 5 minutes
- ❌ Old index not backed up (data loss risk)
- ❌ Search broken after rollback

---

## Test Case FT-008: Health Check Integration

**Requirement:** FR-008  
**Priority:** High  
**Objective:** Verify AST chunking integrated with Cascading Health Check Architecture

**Preconditions:**
- CodeIndex health check implemented
- AST chunker registered as component

**Test Steps:**
1. Build index with AST chunking (all successful)
2. Call `pos_search_project` health check
3. Verify AST component reports "operational"
4. Verify metrics: chunk count, avg token size, fallback count=0
5. Trigger parse failures (corrupted files)
6. Call health check again
7. Verify AST component reports "degraded"
8. Verify actionable recommendation provided

**Expected Results:**
- ✅ Health check reports operational/degraded/fallback status
- ✅ Metrics include: chunk count, token size, fallback rate
- ✅ Degraded status when fallback rate >25%
- ✅ Actionable recommendations (e.g., "Check TypeScript config")

**Failure Criteria:**
- ❌ AST component not registered in health check
- ❌ Health status always "operational" even with failures
- ❌ No metrics or recommendations

---

## Test Case FT-009: Import Chunk Grouping

**Requirement:** FR-009  
**Priority:** Medium  
**Objective:** Verify consecutive imports grouped into single chunk

**Preconditions:**
- Python file with 10 consecutive import statements
- Import grouping implemented

**Test Steps:**
1. Create file with 10 imports at top, then 3 functions
2. Chunk file
3. Verify chunk count = 4 (1 import chunk + 3 function chunks)
4. Verify import chunk has `chunk_type="import"`
5. Verify import chunk includes all 10 imports
6. Verify imported symbols extracted

**Expected Results:**
- ✅ All imports in single chunk
- ✅ Import chunk marked `chunk_type="import"`
- ✅ Import chunk has `import_ratio=1.0`
- ✅ Imported symbols list populated

**Failure Criteria:**
- ❌ Each import as separate chunk
- ❌ Imports mixed with function chunks
- ❌ Import chunk not penalized

---

## Test Case FT-010: Multi-Language Consistency

**Requirement:** FR-010  
**Priority:** Medium  
**Objective:** Verify consistent chunking quality across Python, TypeScript, Go

**Preconditions:**
- Test fixtures for all 3 languages
- Same functionality implemented in each language

**Test Steps:**
1. Create equivalent function in Python, TypeScript, Go
2. Chunk all 3 files
3. Compare chunk quality:
   - Token counts similar (±10%)
   - Chunk boundaries at function definitions
   - Import penalty applied consistently
4. Run same query against all 3 languages
5. Verify Relevance@5 >90% for all languages

**Expected Results:**
- ✅ Python, TypeScript, Go chunk quality equivalent
- ✅ Implementation ranks above imports for all languages
- ✅ Relevance@5 >90% for all languages
- ✅ Consistent behavior (no language-specific quirks)

**Failure Criteria:**
- ❌ One language consistently worse quality
- ❌ Language-specific bugs or edge cases
- ❌ Relevance@5 varies significantly between languages

---

## Test Execution Summary

**Total Test Cases:** 10  
**Critical:** 3 (FT-001, FT-002, FT-003)  
**High:** 5 (FT-004 through FT-008)  
**Medium:** 2 (FT-009, FT-010)

**Estimated Execution Time:** 4-6 hours (includes test fixture creation)

**Pass Criteria:** All test cases pass with no critical or high failures

---


