#!/bin/bash
# Quick comparison script for RAG search methods
# Usage: ./quick_compare.sh

set -e

echo "=========================================="
echo "RAG Search Methods Quick Comparison"
echo "=========================================="
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# Run comparison
python evaluate_search.py --compare vector hybrid hybrid_rerank

echo ""
echo "=========================================="
echo "✅ Comparison complete!"
echo ""
echo "Results saved to:"
echo "  - JSON: ../results/comparison_*.json"
echo "  - Report: ../results/comparison_report_*.md"
echo ""
echo "View the markdown report for human-readable results."
echo "=========================================="

