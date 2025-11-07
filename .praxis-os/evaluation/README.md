# RAG Search Quality Evaluation

Automated measurement harness for evaluating and comparing RAG search methods.

**✅ Updated for Ouroboros Architecture (2025-11-04)**

## Overview

This evaluation system measures search quality using **standard Information Retrieval metrics**:

| Metric | What It Measures | Range | Higher is Better |
|--------|------------------|-------|------------------|
| **NDCG@K** | Ranking quality (position matters) | 0.0-1.0 | ✓ |
| **MRR** | How fast first relevant result appears | 0.0-1.0 | ✓ |
| **Precision@K** | % of returned results that are relevant | 0.0-1.0 | ✓ |
| **Recall@K** | % of relevant docs found in top K | 0.0-1.0 | ✓ |
| **MAP** | Overall precision across all ranks | 0.0-1.0 | ✓ |

---

## Quick Start

### 1. Evaluate Single Method

```bash
cd /Users/josh/src/github.com/honeyhiveai/praxis-os/.praxis-os/evaluation/scripts

# Evaluate hybrid search
python evaluate_search.py --method hybrid

# Evaluate with different K value
python evaluate_search.py --method vector --k 5

# Enable verbose output
python evaluate_search.py --method hybrid_rerank --verbose
```

### 2. Compare Multiple Methods

```bash
# Compare all methods
python evaluate_search.py --compare vector fts hybrid hybrid_rerank

# Compare specific methods
python evaluate_search.py --compare vector hybrid_rerank
```

### 3. Example Output

```
🔍 Comparing methods: vector, hybrid, hybrid_rerank
================================================================================

📊 Evaluating vector...
Results for vector:
  NDCG@10: 0.847
  MRR: 0.823
  Precision@10: 0.72
  Recall@10: 0.85
  MAP: 0.791
  Top-3 Hit Rate: 76.7%
  Avg First Rank: 2.13

📊 Evaluating hybrid...
Results for hybrid:
  NDCG@10: 0.912
  MRR: 0.891
  Precision@10: 0.81
  Recall@10: 0.92
  MAP: 0.856
  Top-3 Hit Rate: 86.7%
  Avg First Rank: 1.67

📊 Evaluating hybrid_rerank...
Results for hybrid_rerank:
  NDCG@10: 0.934
  MRR: 0.908
  Precision@10: 0.84
  Recall@10: 0.94
  MAP: 0.879
  Top-3 Hit Rate: 90.0%
  Avg First Rank: 1.43

✅ Comparison saved to ../results/comparison_20251103_123456.json
📄 Comparison report saved to ../results/comparison_report_20251103_123456.md
```

---

## Available Search Methods

| Method | Description | When to Use |
|--------|-------------|-------------|
| **vector** | Vector similarity only | Baseline for semantic search |
| **fts** | Full-text search (BM25) only | Baseline for keyword search |
| **hybrid** | Vector + FTS + RRF fusion | Best of both worlds (no re-ranking) |
| **hybrid_rerank** | Hybrid + cross-encoder re-ranking | Maximum accuracy (+20ms latency) |

---

## Ground Truth Dataset

**Location:** `ground_truth/queries.yaml`

**Coverage:**
- **30 test queries** across 10 categories
- **3 difficulty levels:** Easy (27%), Medium (47%), Hard (27%)
- **Diverse query types:** How-to, conceptual, troubleshooting, multi-concept
- **Edge cases:** Negation, acronyms, synonyms

**Categories:**
1. Workflow implementation & validation (3 queries)
2. AI assistant behavior & safety (4 queries)
3. Operations & maintenance (3 queries)
4. Architecture & design (3 queries)
5. Security & safety (3 queries)
6. Testing & validation (3 queries)
7. Configuration & setup (3 queries)
8. Edge cases & synonyms (5 queries)
9. Multi-concept queries (2 queries)
10. Acronyms & terminology (2 queries)

### Adding New Test Queries

Edit `ground_truth/queries.yaml`:

```yaml
- id: q31
  query: "your test query here"
  category: "your_category"
  difficulty: "easy|medium|hard"
  expected_docs:
    - path: "standards/path/to/doc.md"
      relevance: 3  # 3=highly relevant, 2=relevant, 1=somewhat, 0=not
      min_rank: 1   # Must appear in top N
```

---

## Output Files

### JSON Results (`results/*.json`)

Detailed per-query results:

```json
{
  "method": "hybrid",
  "k": 10,
  "timestamp": "2025-11-03T12:34:56",
  "num_queries": 30,
  "per_query_results": [
    {
      "query_id": "q1",
      "query": "How do I implement workflow gates?",
      "category": "workflow_implementation",
      "difficulty": "medium",
      "metrics": {
        "ndcg@k": 0.942,
        "mrr": 1.0,
        "precision@k": 0.8,
        "recall@k": 1.0
      },
      "top_5_results": [...]
    }
  ],
  "aggregated_metrics": {
    "ndcg@k": 0.912,
    "mrr": 0.891,
    ...
  }
}
```

### Markdown Report (`results/comparison_report_*.md`)

Human-readable comparison:

```markdown
# RAG Search Methods Comparison

| Method | NDCG@10 | MRR | Precision@10 | Recall@10 |
|--------|---------|-----|--------------|-----------|
| vector | 0.847 | 0.823 | 0.72 | 0.85 |
| hybrid | 0.912 | 0.891 | 0.81 | 0.92 |
| hybrid_rerank | 0.934 | 0.908 | 0.84 | 0.94 |

## Improvements Over Vector-Only Baseline

### hybrid
- NDCG improvement: **+7.7%**
- MRR improvement: **+8.3%**
```

---

## Use Cases

### 1. Prove Hybrid Search Value

**Goal:** Quantify improvement over vector-only

```bash
python evaluate_search.py --compare vector hybrid hybrid_rerank
```

**Expected Results:**
- Hybrid: +5-10% NDCG improvement
- Re-ranking: +10-15% NDCG improvement

### 2. Regression Testing

**Goal:** Detect quality degradation after changes

```bash
# Before changes
python evaluate_search.py --method hybrid_rerank > before.txt

# Make changes to index, config, or code

# After changes
python evaluate_search.py --method hybrid_rerank > after.txt

# Compare
diff before.txt after.txt
```

### 3. Configuration Tuning

**Goal:** Find optimal chunk size, model, or fusion weights

```bash
# Test with different configs
# Edit index_config.yaml, rebuild index, then:
python evaluate_search.py --method hybrid
```

### 4. A/B Testing

**Goal:** Compare two embedding models

```bash
# Model A (BAAI/bge-small-en-v1.5)
python evaluate_search.py --method vector > model_a.txt

# Change config to Model B, rebuild index
# Model B (BAAI/bge-base-en-v1.5)
python evaluate_search.py --method vector > model_b.txt
```

---

## Interpreting Results

### NDCG@10 Score Translation

| Score | Interpretation | What This Means |
|-------|----------------|-----------------|
| 0.90-1.00 | **Excellent** | Near-perfect ranking, relevant docs consistently at top |
| 0.80-0.90 | **Very Good** | Relevant results in top 3, minor misordering |
| 0.70-0.80 | **Good** | Relevant results found but some ordering issues |
| 0.60-0.70 | **Fair** | Relevant results appear but poorly ordered |
| <0.60 | **Needs Work** | Significant ranking problems |

### MRR (Mean Reciprocal Rank)

- **MRR = 1.0**: Perfect! Relevant result always at position 1
- **MRR = 0.5**: On average, first relevant result at position 2
- **MRR = 0.33**: On average, first relevant result at position 3

### Top-3 Hit Rate

**Target:** ≥80% (4 out of 5 queries should have relevant result in top 3)

---

## Metrics Formulas

### NDCG@K (Normalized Discounted Cumulative Gain)

```
DCG@K = Σ (relevance_i / log₂(position_i + 1))
IDCG@K = DCG of perfect ranking
NDCG@K = DCG@K / IDCG@K
```

**Why logarithmic discount?**
- Position 1 is worth 2-3x more than position 5
- Rewards having highly relevant docs at top
- Penalizes relevant docs buried deep

### MRR (Mean Reciprocal Rank)

```
RR = 1 / rank_of_first_relevant_result
MRR = average(RR) across all queries
```

**Why use reciprocal?**
- Position 1: RR = 1.0 (perfect)
- Position 2: RR = 0.5 (half as good)
- Position 10: RR = 0.1 (much worse)

---

## CI Integration

Add to your CI pipeline:

```yaml
# .github/workflows/rag-quality.yml
name: RAG Quality Check

on: [pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          cd .praxis-os
          pip install -r mcp_server/requirements.txt
      
      - name: Evaluate search quality
        run: |
          cd .praxis-os/evaluation/scripts
          python evaluate_search.py --method hybrid_rerank
      
      - name: Check quality threshold
        run: |
          # Fail if NDCG@10 < 0.85
          python -c "
          import json
          with open('.praxis-os/evaluation/results/hybrid_rerank_*.json') as f:
              data = json.load(f)
              ndcg = data['aggregated_metrics']['ndcg@k']
              if ndcg < 0.85:
                  raise ValueError(f'NDCG@10 {ndcg:.3f} below threshold 0.85')
          "
```

---

## Troubleshooting

### "StandardsIndex not available"

**Solution:** Build the index first

```bash
cd /Users/josh/src/github.com/honeyhiveai/praxis-os/.praxis-os/scripts
python build_rag_index.py
```

### "Ground truth file not found"

**Solution:** Ensure you're running from correct directory

```bash
cd /Users/josh/src/github.com/honeyhiveai/praxis-os/.praxis-os/evaluation/scripts
python evaluate_search.py --method hybrid
```

### "No module named 'mcp_server'"

**Solution:** Install dependencies

```bash
cd /Users/josh/src/github.com/honeyhiveai/praxis-os/.praxis-os
pip install -r mcp_server/requirements.txt
```

---

## Future Enhancements

1. **Automated Ground Truth Generation**
   - Use LLM to generate diverse test queries
   - Auto-label relevance using cross-encoder

2. **Live Evaluation Dashboard**
   - Real-time metrics tracking
   - Historical trend visualization

3. **Per-User Evaluation**
   - Track search quality for each user's query patterns
   - Personalized relevance judgments

4. **A/B Testing Framework**
   - Split traffic between methods
   - Statistical significance testing

---

## References

- [NDCG Explained](https://en.wikipedia.org/wiki/Discounted_cumulative_gain)
- [Information Retrieval Metrics](https://www.oreilly.com/library/view/information-retrieval/9781449311995/)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)

---

**Questions?** Search the standards: `pos_search(content_type="standards", query="RAG evaluation metrics")`

