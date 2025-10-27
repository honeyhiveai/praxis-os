#!/bin/bash
# Test ultra-specific queries targeting deep sections

OUTPUT="/tmp/ultra_specific_queries.txt"
rm -f "$OUTPUT"

echo "Testing ULTRA-SPECIFIC queries for deep sections..."
echo "Results will be saved to: $OUTPUT"
echo ""

# Query 3 Variations: What Counts as Active Time
echo "========================================" >> "$OUTPUT"
echo "QUERY 3 - VARIATION A: Match Section Header Exactly" >> "$OUTPUT"
echo "Query: what counts as human active time" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "what counts as human active time", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 3A complete"

echo "========================================" >> "$OUTPUT"
echo "QUERY 3 - VARIATION B: Match Subsection Content" >> "$OUTPUT"
echo "Query: INCLUDES in orchestration estimate" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "INCLUDES in orchestration estimate", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 3B complete"

echo "========================================" >> "$OUTPUT"
echo "QUERY 3 - VARIATION C: Match Specific Activities" >> "$OUTPUT"
echo "Query: reading task specification giving direction reviewing output" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "reading task specification giving direction reviewing output", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 3C complete"

# Query 6 Variations: Calibration Guidance
echo "========================================" >> "$OUTPUT"
echo "QUERY 6 - VARIATION A: Match Section Header" >> "$OUTPUT"
echo "Query: calibrating your estimates if you are new" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "calibrating your estimates if you are new", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 6A complete"

echo "========================================" >> "$OUTPUT"
echo "QUERY 6 - VARIATION B: Match Specific Guidance" >> "$OUTPUT"
echo "Query: start conservative 1.2x multiplier 8-10% orchestration" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "start conservative 1.2x multiplier 8-10% orchestration", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 6B complete"

echo "========================================" >> "$OUTPUT"
echo "QUERY 6 - VARIATION C: Match Process Flow" >> "$OUTPUT"
echo "Query: track actual versus estimated for 5-10 tasks" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"
python mcp_tool_cli.py search_standards '{"query": "track actual versus estimated for 5-10 tasks", "n_results": 3}' >> "$OUTPUT" 2>&1
echo "" >> "$OUTPUT"
echo "✓ Query 6C complete"

echo ""
echo "========================================" >> "$OUTPUT"
echo "ULTRA-SPECIFIC QUERY TESTING COMPLETE" >> "$OUTPUT"
echo "6 query variations tested (3 for Q3, 3 for Q6)" >> "$OUTPUT"
echo "========================================" >> "$OUTPUT"

echo ""
echo "Testing complete!"
echo "Results saved to: $OUTPUT"
echo ""
echo "Summary:"
echo "  Query 3: 3 variations tested"
echo "    A: Exact section header"
echo "    B: Subsection keyword" 
echo "    C: Specific activities"
echo ""
echo "  Query 6: 3 variations tested"
echo "    A: Section header match"
echo "    B: Specific guidance"
echo "    C: Process flow"
echo ""
echo "To view: cat $OUTPUT | less"
