# Non-Functional Test Plan

**Project:** AST-Aware Code Chunking with Import Penalty  
**Date:** 2025-11-11  
**Purpose:** Test cases for performance, reliability, maintainability, scalability, usability, and compatibility

---

## Performance Tests

### NFT-P1: Search Query Latency

**Requirement:** NFR-P1  
**Objective:** Verify p95 search latency <200ms

**Test Steps:**
1. Build index with AST chunking (100K LOC)
2. Execute 100 diverse queries
3. Measure latency for each query (p50, p95, p99)
4. Compare to line-based baseline

**Pass Criteria:**
- p50 <100ms
- p95 <200ms  
- p99 <300ms
- No regression vs baseline

---

### NFT-P2: Index Build Time

**Requirement:** NFR-P2  
**Objective:** Verify rebuild <10 minutes for 100K LOC

**Test Steps:**
1. Prepare test repo (100K LOC, Python/TypeScript/Go)
2. Delete index, restart server
3. Measure rebuild time
4. Verify progress logging every 10%

**Pass Criteria:**
- Rebuild <10 minutes
- AST overhead 2-3x (acceptable)
- Parallel processing used

---

### NFT-P3: Import Penalty Overhead

**Requirement:** NFR-P3  
**Objective:** Verify penalty adds <1ms overhead

**Test Steps:**
1. Profile search ranking stage
2. Measure import ratio calculation time
3. Measure penalty application time

**Pass Criteria:**
- Import ratio calc <0.5ms
- Penalty application <0.5ms
- Total <1ms

---

## Reliability Tests

### NFT-R1: Graceful Degradation

**Requirement:** NFR-R1  
**Objective:** Verify continued operation on parse failures

**Test Steps:**
1. Index corrupted files
2. Verify fallback to line-based
3. Verify health check reports degraded
4. Verify search works for all files

**Pass Criteria:**
- Parse failures logged
- Fallback activated
- Health shows degraded (not failure)
- Search operational

---

### NFT-R2: Quick Recovery

**Requirement:** NFR-R2  
**Objective:** Verify rollback <5 minutes

**Test Steps:**
1. Set `chunking_strategy: "line"`
2. Measure rollback time
3. Verify old index preserved

**Pass Criteria:**
- Rollback <5 minutes
- Backup created
- No downtime

---

### NFT-R3: Health Monitoring

**Requirement:** NFR-R3  
**Objective:** Verify health check integration

**Test Steps:**
1. Check health in operational state
2. Trigger degradation (parse failures)
3. Check health in degraded state
4. Verify metrics and recommendations

**Pass Criteria:**
- Status: operational/degraded/fallback
- Metrics: chunk count, token size, fallback rate
- Actionable recommendations

---

## Maintainability Tests

### NFT-M1: Config-Driven Languages

**Requirement:** NFR-M1  
**Objective:** Verify languages added via config only

**Test Steps:**
1. Add Rust config to mcp.yaml
2. Restart (no code changes)
3. Verify Rust chunking works
4. Time the process

**Pass Criteria:**
- No code changes
- <1 hour to add language
- Config validation works

---

### NFT-M3: Logging and Diagnostics

**Requirement:** NFR-M3  
**Objective:** Verify comprehensive logging

**Test Steps:**
1. Trigger parse failure
2. Check logs for file path, language, error
3. Trigger fallback
4. Check logs for fallback reason
5. Build index
6. Check logs for chunk statistics

**Pass Criteria:**
- Parse failures logged with details
- Fallback logged with reason
- Chunk stats logged
- Health output actionable

---

## Scalability Tests

### NFT-SC1: Multi-Repository Support

**Requirement:** NFR-SC1  
**Objective:** Verify AST chunking across partitions

**Test Steps:**
1. Configure multiple partitions (primary, instrumentors)
2. Build indexes for all partitions
3. Verify AST chunking enabled for all
4. Check partition health

**Pass Criteria:**
- AST chunking in all partitions
- Consistent quality metrics
- Partition health monitored
- No cross-partition interference

---

### NFT-SC2: Language Extensibility

**Requirement:** NFR-SC2  
**Objective:** Verify 3+ languages at launch

**Test Steps:**
1. Verify Python config exists
2. Verify TypeScript config exists
3. Verify Go config exists
4. Add new language (Rust)
5. Time addition process

**Pass Criteria:**
- Python, TypeScript, Go at launch
- Rust added in <1 hour
- Config schema documented
- Test suite validates new language

---

## Usability Tests

### NFT-U1: Search Result Relevance

**Requirement:** NFR-U1  
**Objective:** Verify implementation ranks above imports

**Test Steps:**
1. Execute python-sdk query (primary test case)
2. Verify implementation ranks #1-2
3. Verify imports rank #5+
4. Execute 100 diverse queries
5. Human evaluation of top-5 results
6. Calculate Relevance@5 and FPR

**Pass Criteria:**
- Implementation #1-2 average
- Imports #5+ average
- Relevance@5 >90%
- FPR <15%

---

### NFT-U2: Developer Experience

**Requirement:** NFR-U2  
**Objective:** Verify transparent behavior

**Test Steps:**
1. Review documentation for chunk boundaries
2. Review documentation for import penalty
3. Check health check output (human-readable)
4. Review rollback procedure docs

**Pass Criteria:**
- Chunk boundaries documented
- Import penalty documented
- Health output clear
- Rollback procedure clear

---

## Compatibility Tests

### NFT-C1: Backward Compatibility

**Requirement:** NFR-C1  
**Objective:** Verify line-based fallback maintained

**Test Steps:**
1. Index unsupported language (Ruby)
2. Verify fallback to line-based
3. Verify behavior equivalent to baseline
4. Disable AST for one language
5. Verify gradual migration works

**Pass Criteria:**
- Line-based unchanged
- Fallback equivalent to baseline
- No impact on unsupported languages
- Per-language enable/disable works

---

### NFT-C2: Integration with RAG

**Requirement:** NFR-C2  
**Objective:** Verify seamless integration

**Test Steps:**
1. Verify SemanticIndex API unchanged
2. Run existing search queries
3. Verify health check extended (not replaced)
4. Verify FTS/vector components unaffected

**Pass Criteria:**
- No breaking changes to API
- Existing queries work
- Health check extended
- No impact on other components

---

## Test Execution Summary

**Total NFT Cases:** 15  
**Performance:** 3  
**Reliability:** 3  
**Maintainability:** 2  
**Scalability:** 2  
**Usability:** 2  
**Compatibility:** 2

**Estimated Execution Time:** 6-8 hours

---


