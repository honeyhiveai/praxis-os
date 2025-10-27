#!/bin/bash
# Validate improved estimation queries (natural language per RAG standards)

OUTPUT="/tmp/improved_estimation_queries.txt"
rm -f "$OUTPUT"

echo "Testing IMPROVED queries (natural language per RAG standards)..."
echo "Results will be saved to: $OUTPUT"
echo ""

# Query 1: Core Formula (UNCHANGED - already works)
echo "========================================" >> "$OUTPUT"
echo "QUERY 1: Core Formula & Calculation" >> "$OUTPUT"
echo "Query: H W A L variables wall clock duration human active time" >> "$OUTPUT"
echo "Status: ✅ Already works (natural language)" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "H W A L variables wall clock duration human active time", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 1 complete"

# Query 2: Task Type Multipliers (UNCHANGED - already works)
echo "========================================" >> "$OUTPUT"
echo "QUERY 2: Task Type Multipliers" >> "$OUTPUT"
echo "Query: table boilerplate setup straightforward logic complex algorithm" >> "$OUTPUT"
echo "Status: ✅ Already works (keyword-based but effective)" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "table boilerplate setup straightforward logic complex algorithm", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 2 complete"

# Query 3: What Counts as Active Time (IMPROVED - natural language)
echo "========================================" >> "$OUTPUT"
echo "QUERY 3: What Counts as Active Time" >> "$OUTPUT"
echo "OLD Query: INCLUDES EXCLUDES human active time" >> "$OUTPUT"
echo "NEW Query: what counts as orchestration time" >> "$OUTPUT"
echo "Status: 🔄 IMPROVED to natural language" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "what counts as orchestration time", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 3 complete (IMPROVED)"

# Query 4: Task Format (UNCHANGED - already works)
echo "========================================" >> "$OUTPUT"
echo "QUERY 4: Task Format" >> "$OUTPUT"
echo "Query: task format example Human Baseline Agent OS" >> "$OUTPUT"
echo "Status: ✅ Already works (natural language)" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "task format example Human Baseline Agent OS", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 4 complete"

# Query 5: Parallel Multiplier Effect (UNCHANGED - already works)
echo "========================================" >> "$OUTPUT"
echo "QUERY 5: Parallel Multiplier Effect" >> "$OUTPUT"
echo "Query: parallel multiplier effect" >> "$OUTPUT"
echo "Status: ✅ Already works (natural language)" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "parallel multiplier effect", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 5 complete"

# Query 6: Calibration Guidance (IMPROVED - natural language)
echo "========================================" >> "$OUTPUT"
echo "QUERY 6: Calibration Guidance" >> "$OUTPUT"
echo "OLD Query: calibration new to Agent OS Enhanced" >> "$OUTPUT"
echo "NEW Query: how to calibrate time estimates" >> "$OUTPUT"
echo "Status: 🔄 IMPROVED to natural language" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "how to calibrate time estimates", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 6 complete (IMPROVED)"

echo ""
echo "========================================" >> "$OUTPUT"
echo "VALIDATION COMPLETE - IMPROVED QUERIES" >> "$OUTPUT"
echo "All 6 queries executed with natural language approach" >> "$OUTPUT"
echo "Queries 3 & 6 improved per RAG optimization standards" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"

echo ""
echo "Validation complete!"
echo "Results saved to: $OUTPUT"
echo ""
echo "Summary:"
echo "  4 queries unchanged (already natural language) ✅"
echo "  2 queries improved (now natural language) 🔄"
echo ""
echo "To view: cat $OUTPUT"
echo "To compare: diff /tmp/all_estimation_queries.txt $OUTPUT"
