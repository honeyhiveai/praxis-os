# Standards Hybrid Optimization Roadmap

**Status:** Analysis Complete  
**Date:** 2025-11-04  
**Total Standards:** 104

---

## 📊 Current State

```
┌────────────────────────────────────────────────┐
│  COMPLIANCE DISTRIBUTION (104 files)           │
├────────────────────────────────────────────────┤
│                                                 │
│  ✅ GOOD (80-100)     ████████████████████ 76  │
│                                         73.1%   │
│                                                 │
│  ⚠️  MEDIUM (60-79)   ██ 9                     │
│                       8.7%                      │
│                                                 │
│  ❌ NEEDS_WORK (<60)  ████ 19                  │
│                       18.3%                     │
└────────────────────────────────────────────────┘
```

**Good News:** 73% already compliant with hybrid search best practices!

---

## 🎯 The Fix: 28 Files Need Updates

### Issue Priority Matrix

```
┌─────────────────────────────────────────────────────────┐
│ Issue                              │ Files │ Priority   │
├─────────────────────────────────────────────────────────┤
│ Missing "Questions This Answers"   │  28   │ 🔴 CRITICAL │
│ Missing TL;DR/Quick Reference      │  17   │ 🟡 HIGH     │
│ Broad single-keyword headers       │  59   │ 🟠 MEDIUM   │
│ Keyword stuffing                   │   2   │ 🟢 LOW      │
└─────────────────────────────────────────────────────────┘
```

---

## ⏱️ Time Investment

```
┌──────────────────────────────────────────────────┐
│  EFFORT ESTIMATE (28 files)                     │
├──────────────────────────────────────────────────┤
│                                                   │
│  Add "Questions" sections:  5-10 min per file    │
│  Add TL;DR sections:        5-10 min per file    │
│  Fix broad headers:         2-5 min per file     │
│                                                   │
│  ────────────────────────────────────────────    │
│  Total per file:            15-25 minutes        │
│                                                   │
│  ════════════════════════════════════════════    │
│                                                   │
│  Best case:   7.0 hours  (28 × 15 min)          │
│  Average:     9.3 hours  (28 × 20 min)          │
│  Worst case: 11.7 hours  (28 × 25 min)          │
│                                                   │
│  Recommended: ~1.5 days of focused work         │
│                                                   │
└──────────────────────────────────────────────────┘
```

---

## 📈 Expected Impact

Based on evaluation data (50 queries on standards/universal):

### Before Optimization
```
Top-3 Hit Rate:      78% (single-angle tested)
Multi-concept NDCG:  0.527 (vector-only)
Missing docs:        ~22 out of 100 queries
```

### After Optimization
```
Top-3 Hit Rate:      96% (multi-angle tested)    +23%
Multi-concept NDCG:  0.810 (hybrid)              +53.7%
Missing docs:        ~4 out of 100 queries       -82%
```

**Translation:** 20-50% improvement in discoverability for affected queries.

---

## 🚀 3-Phase Roadmap

### Phase 1: CRITICAL (5 hours)
**Target:** 28 files missing "Questions This Answers"

**Template:**
```markdown
## ❓ Questions This Answers

1. "How to [main use case]?"
2. "[User wants] [action] - what do I do?"
3. "When should I use [feature]?"
4. "What's the difference between [A] and [B]?"
5. "[Troubleshooting scenario]?"
```

**Files:** Focus on `standards/development/` (14 files)

---

### Phase 2: HIGH (2-3 hours)
**Target:** 17 files missing TL;DR sections

**Template:**
```markdown
## 🚨 [Topic] Quick Reference

**Keywords for search**: [natural diversity of terms]

**Core Principle:** [One sentence]

**When to use:**
- [Scenario 1]
- [Scenario 2]
- [Scenario 3]

**Critical information:**
1. **[Key Point]** - [One sentence]
2. **[Key Point]** - [One sentence]
3. **[Key Point]** - [One sentence]
```

---

### Phase 3: MEDIUM (2-4 hours)
**Target:** 59 files with broad headers

**Changes:**
- "Usage" → "How to [Specific Action] (Usage)"
- "Testing" → "Integration Testing for API Endpoints"
- "Examples" → "[Feature] Usage Examples and Patterns"

---

## 🎯 Top 10 Priority Files

**Lowest scores, highest impact:**

| File | Score | Fix Time | Impact |
|------|-------|----------|--------|
| `development/python-code-quality.md` | 25 | 20 min | High |
| `development/code-quality.md` | 40 | 15 min | High |
| `development/mcp-vs-cursor-rules.md` | 40 | 15 min | High |
| `development/production-code-checklist.md` | 40 | 15 min | High |
| `development/python-testing.md` | 40 | 15 min | High |
| `universal/documentation/change-impact-analysis.md` | 40 | 15 min | High |
| `development/compact-diagram-checklist.md` | 40 | 15 min | Medium |
| `development/config-json-reference.md` | 40 | 15 min | Medium |
| `development/pre-commit-setup.md` | 40 | 15 min | Medium |
| `development/python-documentation.md` | 40 | 15 min | Medium |

**Quick Win:** Fix these 10 in ~2.5 hours for maximum impact!

---

## 🔄 Testing & Validation

### Before Making Changes

Run baseline:
```bash
cd .praxis-os/evaluation/scripts
python analyze_standards_hybrid.py
```

**Current:** 73% compliant (76/104 files)

---

### After Phase 1 (Questions sections)

Re-run analysis:
```bash
python analyze_standards_hybrid.py
```

**Target:** 100% have "Questions This Answers" (104/104 files)

---

### After Phase 2 (TL;DR sections)

**Target:** 100% have TL;DR sections (104/104 files)

---

### After Phase 3 (Header refinement)

**Target:** 100% GOOD rating (score ≥80)

---

### Real-World Testing

Run evaluation on sample queries:
```bash
cd .praxis-os/evaluation/scripts
python evaluate_search.py --method hybrid --k 10
```

**Target:** NDCG@10 ≥ 0.90, Top-3 Hit Rate ≥ 95%

---

## 📋 Quality Checklist

For each updated file:

**Structure:**
- [ ] Has "Questions This Answers" section (3-5 queries)
- [ ] Has TL;DR/Quick Reference at top
- [ ] Headers use specific keyword combinations
- [ ] Chunks are 100-500 tokens

**Keywords:**
- [ ] Natural diversity (synonyms > repetition)
- [ ] No keyword stuffing
- [ ] Multi-word combinations in headers
- [ ] Both exact phrases (FTS) and semantic context (vector)

**Testing:**
- [ ] Test with semantic query (natural language)
- [ ] Test with keyword query (specific terms)
- [ ] Test with multi-concept query
- [ ] Returns in top 3 for ALL angles

---

## 🎓 Success Metrics

### Baseline (Current)
```
✅ Compliant files:        76 (73%)
📊 Average score:          82/100
❌ Missing Questions:      28 files
❌ Missing TL;DR:          17 files
⚠️  Broad headers:         59 files
```

### Target (Post-Optimization)
```
✅ Compliant files:        104 (100%)
📊 Average score:          90+/100
✅ Missing Questions:      0 files
✅ Missing TL;DR:          0 files
✅ Optimized headers:      All files
```

### Key Performance Indicators

| Metric | Before | Target | Improvement |
|--------|--------|--------|-------------|
| Compliant % | 73% | 100% | +37% |
| Avg Score | 82 | 90+ | +10% |
| Top-3 Hit Rate | 78% | 96%+ | +23% |

---

## 💡 Quick Reference

### Most Common Issues

1. **No "Questions" section** (28 files)
   - Fix: Add 3-5 natural query examples
   - Time: 5-10 minutes
   - Impact: High (critical for FTS)

2. **No TL;DR section** (17 files)
   - Fix: Add front-loaded summary with keyword diversity
   - Time: 5-10 minutes
   - Impact: High (helps both vector and FTS)

3. **Broad headers** (59 files)
   - Fix: Make headers more specific
   - Time: 2-5 minutes per header
   - Impact: Medium (improves FTS specificity)

---

## 📞 Support

**Analysis Script:**
```bash
cd .praxis-os/evaluation/scripts
python analyze_standards_hybrid.py
```

**Updated Standard:**
```
.praxis-os/standards/universal/ai-assistant/rag-content-authoring.md
```

**This Summary:**
```
.praxis-os/evaluation/STANDARDS_HYBRID_ANALYSIS_SUMMARY.md
```

**Detailed Results:**
```
.praxis-os/evaluation/results/standards_hybrid_analysis.txt
```

---

## ✅ Action Items

**Today:**
- [ ] Review this roadmap
- [ ] Prioritize: Do we optimize all 28 files or just critical ones?
- [ ] Decide: Spread over 3 days or focus session?

**This Week:**
- [ ] Phase 1: Add "Questions" sections (5 hours)
- [ ] Phase 2: Add TL;DR sections (2-3 hours)
- [ ] Run validation analysis
- [ ] Spot-check with real queries

**Next Week:**
- [ ] Phase 3: Refine broad headers (2-4 hours)
- [ ] Final validation
- [ ] Document improvements

---

**Bottom Line:** 9.3 hours of focused work to bring all 104 standards to full hybrid search compliance. Most (73%) are already compliant!

