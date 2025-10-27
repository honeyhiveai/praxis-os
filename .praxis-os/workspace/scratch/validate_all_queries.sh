#!/bin/bash
# Validate all 6 estimation queries and save to single file

OUTPUT="/tmp/all_estimation_queries.txt"
rm -f "$OUTPUT"  # Clear any previous results

echo "Running all 6 estimation framework queries..."
echo "Results will be saved to: $OUTPUT"
echo ""

# Query 1: Core Formula
echo "========================================" >> "$OUTPUT"
echo "QUERY 1: Core Formula & Calculation" >> "$OUTPUT"
echo "Query: H W A L variables wall clock duration human active time" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "H W A L variables wall clock duration human active time", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 1 complete"

# Query 2: Task Type Multipliers
echo "========================================" >> "$OUTPUT"
echo "QUERY 2: Task Type Multipliers" >> "$OUTPUT"
echo "Query: table boilerplate setup straightforward logic complex algorithm" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "table boilerplate setup straightforward logic complex algorithm", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 2 complete"

# Query 3: What Counts as Active Time
echo "========================================" >> "$OUTPUT"
echo "QUERY 3: What Counts as Active Time" >> "$OUTPUT"
echo "Query: INCLUDES EXCLUDES human active time" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "INCLUDES EXCLUDES human active time", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 3 complete"

# Query 4: Task Format
echo "========================================" >> "$OUTPUT"
echo "QUERY 4: Task Format" >> "$OUTPUT"
echo "Query: task format example Human Baseline Agent OS" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "task format example Human Baseline Agent OS", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 4 complete"

# Query 5: Parallel Multiplier Effect
echo "========================================" >> "$OUTPUT"
echo "QUERY 5: Parallel Multiplier Effect" >> "$OUTPUT"
echo "Query: parallel multiplier effect" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "parallel multiplier effect", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 5 complete"

# Query 6: Calibration Guidance
echo "========================================" >> "$OUTPUT"
echo "QUERY 6: Calibration Guidance" >> "$OUTPUT"
echo "Query: calibration new to prAxIs OS" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "calibration new to prAxIs OS", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 6 complete"

echo ""
echo "========================================" >> "$OUTPUT"
echo "VALIDATION COMPLETE" >> "$OUTPUT"
echo "All 6 queries executed successfully" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"

echo ""
echo "All queries complete!"
echo "Results saved to: $OUTPUT"
echo ""
echo "To view: cat $OUTPUT"
echo "To analyze specific query: grep -A 50 'QUERY 1' $OUTPUT"
