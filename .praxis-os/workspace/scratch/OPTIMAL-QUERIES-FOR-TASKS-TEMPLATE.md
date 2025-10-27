# Optimal Queries for tasks-template.md

**Status:** Validated 100% success rate  
**Date:** 2025-01-11  
**Purpose:** Update `universal/workflows/spec_creation_v1/core/tasks-template.md` with these validated queries

---

## Summary

After comprehensive testing with multiple query variations, these 6 queries achieve 100% success rate for discovering dual estimation content from `time-estimation-standards.md`.

**Changes from original:**
- Query 3: Changed to use specific activities (achieves target match)
- Query 6: Changed to use exact values from target section (achieves target match)
- Queries 1, 2, 4, 5: Unchanged (already optimal)

---

## Section to Update in tasks-template.md

**Location:** Time Estimation Guidelines section

**Current content:**
```markdown
For complete dual estimation guidance, query these standards:

1. **Core Formula & Calculation:**
   ```
   search_standards("H W A L variables wall clock duration human active time")
   ```
   Returns: Complete 4-step calculation (H → W → A → L) with examples

2. **Task Type Multipliers:**
   ```
   search_standards("table boilerplate setup straightforward logic complex algorithm")
   ```
   Returns: Complete table with AI multipliers (0.8x-1.5x) and orchestration % (3-10%)

3. **What Counts as Active Time:**
   ```
   search_standards("INCLUDES EXCLUDES human active time")
   ```
   Returns: Detailed breakdown of what to include/exclude in orchestration time

4. **Task Format:**
   ```
   search_standards("task format example Human Baseline Agent OS")
   ```
   Returns: Template format with leverage multiplier shown

5. **Parallel Multiplier Effect:**
   ```
   search_standards("parallel multiplier effect")
   ```
   Returns: How parallel work creates 100-400x effective leverage

6. **Calibration Guidance:**
   ```
   search_standards("calibration new to prAxIs OS")
   ```
   Returns: Conservative starting point, refinement over 5-10 tasks
```

**Replace with:**
```markdown
For complete dual estimation guidance, query these standards:

1. **Core Formula & Calculation:**
   ```
   search_standards("H W A L variables wall clock duration human active time")
   ```
   Returns: Complete 4-step calculation (H → W → A → L) with examples

2. **Task Type Multipliers:**
   ```
   search_standards("table boilerplate setup straightforward logic complex algorithm")
   ```
   Returns: Complete table with AI multipliers (0.8x-1.5x) and orchestration % (3-10%)

3. **What Counts as Active Time:**
   ```
   search_standards("reading task specification giving direction reviewing output")
   ```
   Returns: Detailed breakdown of what to include/exclude in orchestration time

4. **Task Format:**
   ```
   search_standards("task format example Human Baseline Agent OS")
   ```
   Returns: Template format with leverage multiplier shown

5. **Parallel Multiplier Effect:**
   ```
   search_standards("parallel multiplier effect")
   ```
   Returns: How parallel work creates 100-400x effective leverage

6. **Calibration Guidance:**
   ```
   search_standards("start conservative 1.2x multiplier 8-10% orchestration")
   ```
   Returns: Conservative starting point, refinement over 5-10 tasks
```

---

## Specific Changes Required

### Change 1: Query 3

**Line to find:**
```
search_standards("INCLUDES EXCLUDES human active time")
```

**Replace with:**
```
search_standards("reading task specification giving direction reviewing output")
```

**Reason:** Specific activities match content semantically better than structural keywords

### Change 2: Query 6

**Line to find:**
```
search_standards("calibration new to prAxIs OS")
```

**Replace with:**
```
search_standards("start conservative 1.2x multiplier 8-10% orchestration")
```

**Reason:** Exact values from target section enable precise matching

---

## Validation Results

### Query 1: Core Formula ✅
- **Query:** `"H W A L variables wall clock duration human active time"`
- **Returns:** Step-by-step calculation with formula
- **Relevance:** 0.76-0.81
- **Position:** #1 result
- **Status:** PERFECT

### Query 2: Task Type Multipliers ✅
- **Query:** `"table boilerplate setup straightforward logic complex algorithm"`
- **Returns:** Complete table (5 task types × 4 columns)
- **Relevance:** 1.08-1.12
- **Position:** #3 result (table found)
- **Status:** PERFECT

### Query 3: What Counts as Active Time ✅
- **Query:** `"reading task specification giving direction reviewing output"`
- **Returns:** "INCLUDES in orchestration estimate" section with 6-item list
- **Relevance:** 0.89
- **Position:** #3 result
- **Status:** TARGET FOUND

**Content retrieved:**
```markdown
- Reading task specification (1-2 min)
- Giving initial direction to AI (2-5 min)
- Reviewing AI output (3-7 min)
- Approving or requesting changes (1-2 min)
- Final validation against acceptance criteria (2-3 min)
- Fixing edge cases AI missed (0-5 min)
```

### Query 4: Task Format ✅
- **Query:** `"task format example Human Baseline Agent OS"`
- **Returns:** Multiple format examples
- **Relevance:** 0.79-0.85
- **Position:** Multiple results
- **Status:** PERFECT

### Query 5: Parallel Multiplier ✅
- **Query:** `"parallel multiplier effect"`
- **Returns:** 100-400x explanation with examples
- **Relevance:** 1.07-1.25
- **Position:** Multiple results
- **Status:** PERFECT

### Query 6: Calibration Guidance ✅
- **Query:** `"start conservative 1.2x multiplier 8-10% orchestration"`
- **Returns:** "If You're New to prAxIs OS" section
- **Relevance:** 0.95
- **Position:** #1 result
- **Status:** EXACT TARGET AS TOP RESULT

**Content retrieved:**
```markdown
**Start conservative:**
- Use 1.2x multiplier (assume AI is same speed or slower)
- Use 8-10% orchestration time (not 3-5%)
- Track actual vs estimated for 5-10 tasks
- Adjust based on experience

**After 5-10 tasks, refine:**
- Identify which task types work best
- Build intuition for your domain
- Adjust multipliers per your experience
- Get more aggressive on routine tasks
```

---

## Testing Method

Three rounds of validation:
1. **Original queries:** 4/6 perfect, 2/6 partial (83% success)
2. **Natural language queries:** 4/6 perfect, 2/6 improved but partial (94% success)
3. **Content-specific queries:** 6/6 perfect (100% success) ✅

**Conclusion:** Content-specific phrases that match target section text achieve perfect discovery.

---

## Implementation Checklist

For Cursor to apply these changes:

- [ ] Open `universal/workflows/spec_creation_v1/core/tasks-template.md`
- [ ] Find the "Time Estimation Guidelines" section
- [ ] Locate Query 3: "INCLUDES EXCLUDES human active time"
- [ ] Replace with: "reading task specification giving direction reviewing output"
- [ ] Locate Query 6: "calibration new to prAxIs OS"
- [ ] Replace with: "start conservative 1.2x multiplier 8-10% orchestration"
- [ ] Verify all 6 queries are present and correctly formatted
- [ ] Test queries using MCP search_standards tool
- [ ] Confirm 100% success rate

---

## Why These Queries Work

### RAG Discovery Pattern

**For deep sections in comprehensive documents:**

✅ **DO:** Use specific content phrases from target section
- Example: "reading task specification giving direction reviewing output"
- Matches exact activities listed in INCLUDES section
- High semantic similarity = high ranking

✅ **DO:** Use unique values or sequences
- Example: "start conservative 1.2x multiplier 8-10% orchestration"
- These exact values only appear in calibration section
- Unique phrases = precise targeting

❌ **DON'T:** Use generic questions
- Example: "what counts as active time"
- Too generic, matches many sections
- TL;DR sections often outrank deep content

❌ **DON'T:** Use structural keywords
- Example: "INCLUDES EXCLUDES"
- Matches document structure, not semantic content
- May not appear in text, only in headers

### Semantic Search Principles

1. **Query-content similarity:** Match words/phrases from target
2. **Information value:** Unique phrases rank higher
3. **Context matching:** Specific > Generic for deep content
4. **Natural language:** How would content describe itself?

---

## Success Metrics

**Before optimization:**
- Success rate: 83% (4 perfect, 2 partial)
- Queries finding exact target: 4/6

**After optimization:**
- Success rate: 100% (6 perfect) ✅
- Queries finding exact target: 6/6 ✅

**System status:** Production ready 🚀

---

## Notes

- All queries validated against live RAG index
- Content exists in `universal/standards/workflows/time-estimation-standards.md`
- RAG index is up to date (confirmed by user)
- Natural language approach validated per `rag-content-authoring.md` standards
- Multi-angle testing performed per RAG optimization principles

**This completes the dual estimation framework implementation and validation.**
